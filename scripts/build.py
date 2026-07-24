# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "jinja2", "pyyaml"]
# ///
"""Build the profile README: fetch data, draw SVG panels, render the template."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]
LOGIN = "ronpandolfi"
ORCID = "0000-0003-0824-8548"


def render_readme(profile: dict, activity: dict, publications: list, updated: str) -> str:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      keep_trailing_newline=True, trim_blocks=False)
    tpl = env.get_template("README.md.j2")
    return tpl.render(profile=profile, activity=activity,
                      publications=publications, updated=updated)


GQL_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, isFork: false, ownerAffiliations: [OWNER]) {
      nodes { languages(first: 6) { edges { size node { name } } } }
    }
  }
}
"""

MAX_LANGUAGES = 5


def summarize_contributions(gql: dict) -> dict:
    user = gql["data"]["user"]
    coll = user["contributionsCollection"]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"])
             for w in coll["contributionCalendar"]["weeks"]][-52:]
    sizes: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    total = sum(sizes.values()) or 1
    languages = [{"name": n, "pct": round(100 * s / total, 1)}
                 for n, s in sorted(sizes.items(), key=lambda kv: -kv[1])[:MAX_LANGUAGES]]
    return {
        "commits": coll["totalCommitContributions"],
        "prs": coll["totalPullRequestContributions"],
        "repos_contributed": coll["totalRepositoriesWithContributedCommits"],
        "weeks": weeks,
        "languages": languages,
    }


def fetch_github(token: str) -> dict:
    now = dt.datetime.now(dt.UTC)
    variables = {"login": LOGIN,
                 "from": (now - dt.timedelta(days=365)).isoformat(),
                 "to": now.isoformat()}
    resp = requests.post("https://api.github.com/graphql",
                         json={"query": GQL_QUERY, "variables": variables},
                         headers={"Authorization": f"bearer {token}"}, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return summarize_contributions(payload)


def parse_orcid_works(works: dict) -> list:
    pubs = []
    for group in works.get("group", []):
        s = group["work-summary"][0]
        doi = None
        for eid in (s.get("external-ids") or {}).get("external-id", []):
            if eid["external-id-type"] == "doi":
                doi = eid["external-id-value"]
        year = None
        if s.get("publication-date") and s["publication-date"].get("year"):
            year = int(s["publication-date"]["year"]["value"])
        journal = s.get("journal-title")
        pubs.append({
            "title": s["title"]["title"]["value"],
            "venue": journal["value"] if journal else "",
            "year": year,
            "citations": None,
            "doi": doi,
        })
    return pubs


def _crossref_citations(doi: str) -> int | None:
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}",
                         headers={"User-Agent": f"profile-readme (mailto:ronpandolfi@lbl.gov)"},
                         timeout=15)
        r.raise_for_status()
        return r.json()["message"].get("is-referenced-by-count")
    except Exception:
        return None


def fetch_publications(top_n: int = 5) -> list:
    r = requests.get(f"https://pub.orcid.org/v3.0/{ORCID}/works",
                     headers={"Accept": "application/json"}, timeout=30)
    r.raise_for_status()
    pubs = parse_orcid_works(r.json())
    for pub in pubs:
        if pub["doi"]:
            pub["citations"] = _crossref_citations(pub["doi"])
    pubs.sort(key=lambda p: (p["citations"] or 0), reverse=True)
    return pubs[:top_n]
