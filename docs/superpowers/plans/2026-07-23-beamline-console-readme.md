# Beamline-Console Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A self-updating GitHub profile README (`ronpandolfi/ronpandolfi`) rendered by a scheduled Action from hand-curated YAML + live GitHub/ORCID/Crossref data, with custom-designed theme-aware SVG panels.

**Architecture:** One PEP 723 `uv`-run script (`scripts/build.py`) fetches GitHub GraphQL activity, ORCID works, and Crossref citation counts (falling back to `data/cache.json` on any fetch failure), draws activity SVGs by string-building, and renders `templates/README.md.j2` into `README.md`. A weekly GitHub Actions workflow runs it and commits changes.

**Tech Stack:** Python 3.12 via `uv run` (inline deps: `requests`, `jinja2`, `pyyaml`), pytest for tests, GitHub Actions.

## Global Constraints

- No third-party stat widgets, badges, typing SVGs, snakes, or animations (spec "Out of scope").
- SVG fonts: labels/data `"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace`; name `"Segoe UI", "Helvetica Neue", sans-serif`. No webfonts.
- Dark palette: bg `#0d1117`, text `#e6edf3`, accent `#4dd0e1`, border `#30363d`, secondary `#8b949e`.
- Light palette: bg `#ffffff`, text `#1f2328`, accent `#0e7490`, border `#d0d7de`, secondary `#57606a`.
- ORCID iD: `0000-0003-0824-8548`. GitHub login: `ronpandolfi`.
- `README.md` is generated only — the template is the source of truth.
- Publications and projects are markdown text, never SVG.
- Run tests with: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/ -v` (from repo root).
- All work happens in `C:\Users\rp\workspace\github-profile` (already a git repo, branch `main`).

---

### Task 1: Curated data file + Jinja template + render function

**Files:**
- Create: `data/profile.yaml`
- Create: `templates/README.md.j2`
- Create: `scripts/build.py` (render portion only)
- Test: `tests/test_render.py`

**Interfaces:**
- Produces: `render_readme(profile: dict, activity: dict, publications: list, updated: str) -> str` in `scripts/build.py`. `activity` keys: `commits, prs, repos_contributed, weeks (list[int], 52 weekly totals), languages (list[{name, pct}])`. `publications` items: `{title, venue, year, citations, doi}`.

- [ ] **Step 1: Write `data/profile.yaml`**

```yaml
name: Ronald Pandolfi
role: "Scientific software · beamline controls — Advanced Light Source, LBNL"
intro: >
  I build control systems and scientific software for synchrotron beamlines
  at the Advanced Light Source. My work spans beamline control UIs, autonomous
  experiment orchestration, and the infrastructure that keeps instruments and
  their software reproducible.
now:
  - name: Lightfall
    desc: Unified beamline control dashboard for the ALS — plugin-based, built for operators and scientists alike.
    note: internal (ALS GitLab)
  - name: CSM
    desc: Configuration management API for beamline control systems — declarative IOC provisioning across the facility.
    note: internal (ALS GitLab)
projects:
  - name: Xi-CAM
    url: https://github.com/Xi-CAM/Xi-cam
    desc: Extensible platform for synchrotron data reduction, visualization, and management.
  - name: Tsuchinoko
    url: https://github.com/lbl-camera/tsuchinoko
    desc: Adaptive-experiment Qt application driving gpCAM autonomous measurement.
  - name: bluesky ecosystem
    url: https://github.com/bluesky
    desc: Contributions across the Bluesky experiment-orchestration ecosystem.
  - name: bcsophyd-zmq
    url: https://github.com/ronpandolfi/bcsophyd-zmq
    desc: LabVIEW ↔ Bluesky bridge over ZMQ for legacy beamline control integration.
links:
  - name: ORCID
    url: https://orcid.org/0000-0003-0824-8548
  - name: Google Scholar
    url: https://scholar.google.com/citations?user=SCHOLAR_ID_HERE
  - name: LinkedIn
    url: https://www.linkedin.com/in/LINKEDIN_SLUG_HERE
scholar_url: https://scholar.google.com/citations?user=SCHOLAR_ID_HERE
```

(The two `_HERE` values are real user-supplied placeholders to fill before first publish; Task 7 verifies them.)

- [ ] **Step 2: Write `templates/README.md.j2`**

```jinja
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img alt="{{ profile.name }} — {{ profile.role }}" src="assets/header-light.svg" width="100%">
</picture>

{{ profile.intro }}

## Now

{% for item in profile.now -%}
- **{{ item.name }}** — {{ item.desc }}{% if item.note %} *({{ item.note }})*{% endif %}
{% endfor %}
<sub>updated {{ updated }}</sub>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <img alt="Past-year activity: {{ activity.commits }} commits, {{ activity.prs }} pull requests, {{ activity.repos_contributed }} repositories" src="assets/activity-light.svg" width="100%">
</picture>

## Selected projects

{% for p in profile.projects -%}
- [**{{ p.name }}**]({{ p.url }}) — {{ p.desc }}
{% endfor %}

## Selected publications

{% for pub in publications -%}
- {{ pub.title }} — *{{ pub.venue }}*, {{ pub.year }}{% if pub.citations %} · cited {{ pub.citations }}×{% endif %}
{% endfor %}
<sub>[see all on Google Scholar]({{ profile.scholar_url }})</sub>

---

<sub>
{% for l in profile.links %}[{{ l.name }}]({{ l.url }}){% if not loop.last %} · {% endif %}{% endfor %}
 · this page regenerates itself weekly via [GitHub Actions](scripts/build.py)
</sub>
```

- [ ] **Step 3: Write the failing test `tests/test_render.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402

FIXTURE_ACTIVITY = {
    "commits": 412, "prs": 37, "repos_contributed": 14,
    "weeks": [3] * 52,
    "languages": [{"name": "Python", "pct": 72.0}, {"name": "C++", "pct": 28.0}],
}
FIXTURE_PUBS = [
    {"title": "Xi-cam: a versatile interface", "venue": "Synchrotron Rad.",
     "year": 2018, "citations": 42, "doi": "10.1107/x"},
]
FIXTURE_PROFILE = {
    "name": "Ronald Pandolfi", "role": "role", "intro": "Intro text.",
    "now": [{"name": "Lightfall", "desc": "dashboard", "note": "internal"}],
    "projects": [{"name": "Xi-CAM", "url": "https://x", "desc": "platform"}],
    "links": [{"name": "ORCID", "url": "https://orcid.org/0000-0003-0824-8548"}],
    "scholar_url": "https://scholar.example",
}


def test_render_readme_contains_all_sections():
    out = build.render_readme(FIXTURE_PROFILE, FIXTURE_ACTIVITY, FIXTURE_PUBS, "2026-07-23")
    assert "Ronald Pandolfi" in out
    assert "## Now" in out and "Lightfall" in out
    assert "## Selected projects" in out and "Xi-CAM" in out
    assert "cited 42×" in out
    assert "updated 2026-07-23" in out
    assert "activity-dark.svg" in out and "header-dark.svg" in out
```

- [ ] **Step 4: Run test to verify it fails**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_render.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build'` (or AttributeError).

- [ ] **Step 5: Write `scripts/build.py` (render portion)**

```python
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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_render.py -v`
Expected: PASS (1 passed).

- [ ] **Step 7: Commit**

```bash
git add data/profile.yaml templates/README.md.j2 scripts/build.py tests/test_render.py
git commit -m "feat: profile data, README template, and render function"
```

---

### Task 2: GitHub activity fetcher

**Files:**
- Modify: `scripts/build.py` (append)
- Test: `tests/test_github.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `fetch_github(token: str) -> dict` returning the `activity` dict shape from Task 1, and helper `summarize_contributions(gql: dict) -> dict` (pure, testable without network).

- [ ] **Step 1: Write the failing test `tests/test_github.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402


def _gql_fixture():
    days = [{"date": f"2026-01-{d:02d}", "contributionCount": 2} for d in range(1, 8)]
    return {
        "data": {"user": {
            "contributionsCollection": {
                "totalCommitContributions": 400,
                "totalPullRequestContributions": 30,
                "totalRepositoriesWithContributedCommits": 12,
                "contributionCalendar": {"weeks": [{"contributionDays": days}] * 52},
            },
            "repositories": {"nodes": [
                {"languages": {"edges": [
                    {"size": 7000, "node": {"name": "Python"}},
                    {"size": 3000, "node": {"name": "C++"}},
                ]}},
            ]},
        }}
    }


def test_summarize_contributions():
    act = build.summarize_contributions(_gql_fixture())
    assert act["commits"] == 400
    assert act["prs"] == 30
    assert act["repos_contributed"] == 12
    assert len(act["weeks"]) == 52 and act["weeks"][0] == 14
    assert act["languages"][0] == {"name": "Python", "pct": 70.0}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_github.py -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'summarize_contributions'`.

- [ ] **Step 3: Append to `scripts/build.py`**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_github.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_github.py
git commit -m "feat: GitHub GraphQL activity fetcher"
```

---

### Task 3: Publications fetcher (ORCID + Crossref)

**Files:**
- Modify: `scripts/build.py` (append)
- Test: `tests/test_publications.py`

**Interfaces:**
- Produces: `fetch_publications(top_n: int = 5) -> list` returning Task 1's publication dicts sorted by citations desc; pure helper `parse_orcid_works(works: dict) -> list` (title, venue, year, doi; citations=None).

- [ ] **Step 1: Write the failing test `tests/test_publications.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402


def _orcid_fixture():
    def summary(title, year, journal, doi):
        return {"work-summary": [{
            "title": {"title": {"value": title}},
            "publication-date": {"year": {"value": str(year)}},
            "journal-title": {"value": journal} if journal else None,
            "external-ids": {"external-id": [
                {"external-id-type": "doi", "external-id-value": doi}]},
        }]}
    return {"group": [
        summary("Paper A", 2018, "J. Synchrotron Rad.", "10.1/a"),
        summary("Paper B", 2021, None, "10.1/b"),
    ]}


def test_parse_orcid_works():
    pubs = build.parse_orcid_works(_orcid_fixture())
    assert pubs[0] == {"title": "Paper A", "venue": "J. Synchrotron Rad.",
                       "year": 2018, "citations": None, "doi": "10.1/a"}
    assert pubs[1]["venue"] == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_publications.py -v`
Expected: FAIL — no attribute `parse_orcid_works`.

- [ ] **Step 3: Append to `scripts/build.py`**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_publications.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_publications.py
git commit -m "feat: ORCID + Crossref publications fetcher"
```

---

### Task 4: Activity SVG renderer

**Files:**
- Modify: `scripts/build.py` (append)
- Test: `tests/test_svg.py`

**Interfaces:**
- Consumes: `activity` dict shape from Task 1.
- Produces: `activity_svg(activity: dict, theme: str) -> str` (`theme` in `{"dark","light"}`), plus module-level `PALETTES` dict.

- [ ] **Step 1: Write the failing test `tests/test_svg.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402

ACT = {"commits": 412, "prs": 37, "repos_contributed": 14,
       "weeks": list(range(52)),
       "languages": [{"name": "Python", "pct": 60.0}, {"name": "C++", "pct": 40.0}]}


def test_activity_svg_dark_and_light():
    dark = build.activity_svg(ACT, "dark")
    light = build.activity_svg(ACT, "light")
    assert dark.startswith("<svg") and dark.endswith("</svg>")
    assert "#0d1117" in dark and "#4dd0e1" in dark
    assert "#ffffff" in light and "#0e7490" in light
    assert "412" in dark and "Python" in dark
    # sparkline polyline exists with 52 points
    assert dark.count(",") >= 52


def test_activity_svg_flat_weeks_no_division_error():
    flat = dict(ACT, weeks=[0] * 52)
    assert "<svg" in build.activity_svg(flat, "dark")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_svg.py -v`
Expected: FAIL — no attribute `activity_svg`.

- [ ] **Step 3: Append to `scripts/build.py`**

```python
PALETTES = {
    "dark": {"bg": "#0d1117", "text": "#e6edf3", "accent": "#4dd0e1",
             "border": "#30363d", "muted": "#8b949e"},
    "light": {"bg": "#ffffff", "text": "#1f2328", "accent": "#0e7490",
              "border": "#d0d7de", "muted": "#57606a"},
}
MONO = '"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace'
LANG_ALPHAS = ["ff", "b0", "78", "4c", "2e"]  # accent opacity steps for language bar


def activity_svg(activity: dict, theme: str) -> str:
    p = PALETTES[theme]
    w, h = 1000, 170
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'font-family=\'{MONO}\'>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" '
        f'fill="{p["bg"]}" stroke="{p["border"]}"/>',
    ]
    # --- sparkline (left third) ---
    sx, sy, sw, sh = 40, 40, 260, 90
    weeks = activity["weeks"]
    peak = max(weeks) or 1
    pts = [(sx + i * sw / (len(weeks) - 1), sy + sh - (v / peak) * sh)
           for i, v in enumerate(weeks)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{sx},{sy + sh} {line} {sx + sw},{sy + sh}"
    parts += [
        f'<polygon points="{area}" fill="{p["accent"]}" opacity="0.12"/>',
        f'<polyline points="{line}" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>',
        f'<text x="{sx}" y="{sy + sh + 24}" font-size="11" fill="{p["muted"]}">'
        f'CONTRIBUTIONS · PAST 12 MONTHS</text>',
    ]
    # --- counters (middle) ---
    stats = [(activity["commits"], "COMMITS"), (activity["prs"], "PULL REQUESTS"),
             (activity["repos_contributed"], "REPOSITORIES")]
    for i, (val, label) in enumerate(stats):
        cx = 390 + i * 130
        parts += [
            f'<text x="{cx}" y="82" font-size="30" fill="{p["text"]}">{val}</text>',
            f'<text x="{cx}" y="104" font-size="10" fill="{p["muted"]}">{label}</text>',
        ]
    # --- language bar (right) ---
    lx, ly, lw = 790, 62, 170
    x = float(lx)
    for i, lang in enumerate(activity["languages"]):
        seg = lw * lang["pct"] / 100
        alpha = LANG_ALPHAS[min(i, len(LANG_ALPHAS) - 1)]
        parts.append(f'<rect x="{x:.1f}" y="{ly}" width="{max(seg - 2, 1):.1f}" '
                     f'height="10" rx="2" fill="{p["accent"]}{alpha}"/>')
        x += seg
    legend = "  ".join(f'{l["name"]} {l["pct"]:.0f}%' for l in activity["languages"][:3])
    parts += [
        f'<text x="{lx}" y="96" font-size="10" fill="{p["muted"]}">{legend}</text>',
        f'<text x="{lx}" y="40" font-size="11" fill="{p["muted"]}">LANGUAGES</text>',
        "</svg>",
    ]
    return "".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_svg.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_svg.py
git commit -m "feat: theme-aware activity panel SVG renderer"
```

---

### Task 5: Static header SVGs

**Files:**
- Create: `assets/header-dark.svg`
- Create: `assets/header-light.svg`

No unit tests (static art); verified visually in Task 7. The two files are identical except palette values.

- [ ] **Step 1: Write `assets/header-dark.svg`**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 220">
  <defs>
    <linearGradient id="beamfade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#4dd0e1" stop-opacity="0.9"/>
      <stop offset="1" stop-color="#4dd0e1" stop-opacity="0.15"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="220" fill="#0d1117"/>
  <!-- storage ring: large circle cropped at left edge -->
  <circle cx="-40" cy="110" r="190" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <circle cx="-40" cy="110" r="150" fill="none" stroke="#21262d" stroke-width="1"/>
  <!-- tangent beam line extracting rightward -->
  <line x1="148" y1="98" x2="640" y2="62" stroke="url(#beamfade)" stroke-width="1.5"/>
  <!-- beamline optics tick marks along the beam -->
  <g stroke="#4dd0e1" stroke-width="1.5">
    <line x1="250" y1="84" x2="250" y2="98"/>
    <line x1="330" y1="78" x2="330" y2="92"/>
    <line x1="440" y1="70" x2="440" y2="84"/>
  </g>
  <circle cx="148" cy="98" r="3" fill="#4dd0e1"/>
  <!-- name + role -->
  <text x="640" y="112" font-family='"Segoe UI", "Helvetica Neue", sans-serif'
        font-size="34" font-weight="600" fill="#e6edf3">Ronald Pandolfi</text>
  <text x="640" y="140" font-family='"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace'
        font-size="13" fill="#8b949e">Scientific software · beamline controls</text>
  <text x="640" y="160" font-family='"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace'
        font-size="13" fill="#8b949e">Advanced Light Source · Lawrence Berkeley National Lab</text>
</svg>
```

- [ ] **Step 2: Write `assets/header-light.svg`**

Same markup with substitutions: bg `#ffffff`, ring strokes `#d0d7de` / `#eaeef2`, accent `#0e7490` (gradient stops and ticks and dot), name fill `#1f2328`, role fill `#57606a`.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 220">
  <defs>
    <linearGradient id="beamfade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0e7490" stop-opacity="0.9"/>
      <stop offset="1" stop-color="#0e7490" stop-opacity="0.15"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="220" fill="#ffffff"/>
  <circle cx="-40" cy="110" r="190" fill="none" stroke="#d0d7de" stroke-width="1.5"/>
  <circle cx="-40" cy="110" r="150" fill="none" stroke="#eaeef2" stroke-width="1"/>
  <line x1="148" y1="98" x2="640" y2="62" stroke="url(#beamfade)" stroke-width="1.5"/>
  <g stroke="#0e7490" stroke-width="1.5">
    <line x1="250" y1="84" x2="250" y2="98"/>
    <line x1="330" y1="78" x2="330" y2="92"/>
    <line x1="440" y1="70" x2="440" y2="84"/>
  </g>
  <circle cx="148" cy="98" r="3" fill="#0e7490"/>
  <text x="640" y="112" font-family='"Segoe UI", "Helvetica Neue", sans-serif'
        font-size="34" font-weight="600" fill="#1f2328">Ronald Pandolfi</text>
  <text x="640" y="140" font-family='"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace'
        font-size="13" fill="#57606a">Scientific software · beamline controls</text>
  <text x="640" y="160" font-family='"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace'
        font-size="13" fill="#57606a">Advanced Light Source · Lawrence Berkeley National Lab</text>
</svg>
```

- [ ] **Step 3: Visual sanity check**

Open both files in a browser (`start assets/header-dark.svg`) and confirm: ring arc visible at left, beam terminates before the name block, text legible. Adjust geometry only if text overlaps art.

- [ ] **Step 4: Commit**

```bash
git add assets/header-dark.svg assets/header-light.svg
git commit -m "feat: static beamline-motif header SVGs (dark/light)"
```

---

### Task 6: Main orchestration with cache fallback

**Files:**
- Modify: `scripts/build.py` (append `main()`)
- Create: `data/cache.json` (seeded empty: `{}`)
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `fetch_github`, `fetch_publications`, `activity_svg`, `render_readme`.
- Produces: `load_with_fallback(name: str, fetcher, cache: dict) -> tuple[object, dict]` and `main() -> None`. Cache file schema: `{"activity": {...}, "publications": [...]}`.

- [ ] **Step 1: Write the failing test `tests/test_main.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402


def test_fallback_uses_cache_on_error():
    cache = {"activity": {"commits": 1}}
    val, cache2 = build.load_with_fallback("activity", lambda: 1 / 0, cache)
    assert val == {"commits": 1} and cache2 == cache


def test_fallback_updates_cache_on_success():
    val, cache2 = build.load_with_fallback("activity", lambda: {"commits": 9}, {})
    assert val == {"commits": 9}
    assert cache2["activity"] == {"commits": 9}


def test_fallback_raises_when_no_cache():
    import pytest
    with pytest.raises(RuntimeError):
        build.load_with_fallback("activity", lambda: 1 / 0, {})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/test_main.py -v`
Expected: FAIL — no attribute `load_with_fallback`.

- [ ] **Step 3: Append to `scripts/build.py`**

```python
def load_with_fallback(name: str, fetcher, cache: dict):
    try:
        value = fetcher()
        cache = {**cache, name: value}
        return value, cache
    except Exception as exc:
        if name in cache:
            print(f"[warn] {name} fetch failed ({exc}); using cached values")
            return cache[name], cache
        raise RuntimeError(f"{name} fetch failed and no cache available") from exc


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    profile = yaml.safe_load((ROOT / "data" / "profile.yaml").read_text(encoding="utf-8"))
    cache_path = ROOT / "data" / "cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    activity, cache = load_with_fallback("activity", lambda: fetch_github(token), cache)
    publications, cache = load_with_fallback("publications", fetch_publications, cache)

    for theme in ("dark", "light"):
        (ROOT / "assets" / f"activity-{theme}.svg").write_text(
            activity_svg(activity, theme), encoding="utf-8")

    updated = dt.date.today().isoformat()
    (ROOT / "README.md").write_text(
        render_readme(profile, activity, publications, updated), encoding="utf-8")
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print("README.md and activity SVGs regenerated.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests**

Run: `uv run --with pytest,jinja2,pyyaml,requests pytest tests/ -v`
Expected: all PASS.

- [ ] **Step 5: Full local end-to-end run**

Read the GitHub PAT location from `C:\Users\rp\workspace\TOOLS.md` (do not echo the token), then:

Run: `GITHUB_TOKEN=<pat> uv run scripts/build.py` (bash) — expected output `README.md and activity SVGs regenerated.`; `README.md`, `assets/activity-*.svg`, and `data/cache.json` now populated. Inspect `README.md` rendering.

- [ ] **Step 6: Commit**

```bash
git add scripts/build.py tests/test_main.py data/cache.json README.md assets/activity-dark.svg assets/activity-light.svg
git commit -m "feat: build orchestration with cache fallback + first generated README"
```

---

### Task 7: GitHub Actions workflow + publish

**Files:**
- Create: `.github/workflows/build.yml`

**Interfaces:**
- Consumes: `scripts/build.py` `main()` via `uv run`.

- [ ] **Step 1: Write `.github/workflows/build.yml`**

```yaml
name: build-profile
on:
  schedule:
    - cron: "17 15 * * 1"   # Mondays 15:17 UTC ≈ 8:17 AM Pacific
  workflow_dispatch:
  push:
    branches: [main]
    paths: ["data/**", "templates/**", "scripts/**", "assets/header-*.svg"]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Regenerate README
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: uv run scripts/build.py
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add README.md assets/ data/cache.json
          git diff --cached --quiet || git commit -m "chore: regenerate profile"
          git push
```

- [ ] **Step 2: Fill real placeholder values in `data/profile.yaml`**

Ask Ron for his Google Scholar user ID and LinkedIn slug; replace `SCHOLAR_ID_HERE` and `LINKEDIN_SLUG_HERE`. If unavailable, remove those link entries entirely (never publish placeholder URLs).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/build.yml data/profile.yaml
git commit -m "feat: weekly regeneration workflow"
```

- [ ] **Step 4: Publish (requires user confirmation)**

Confirm with Ron before pushing (leaves the machine). Then create the repo and push:

```bash
gh repo create ronpandolfi/ronpandolfi --public --source . --push
```

Expected: repo visible at github.com/ronpandolfi, profile README renders on github.com/ronpandolfi.

- [ ] **Step 5: Verify live**

Run the workflow once manually: `gh workflow run build-profile`. Check both themes (GitHub appearance settings or browser devtools `prefers-color-scheme` emulation). Confirm SVGs render, publications populated, no placeholder text anywhere: `grep -n "_HERE" README.md data/profile.yaml` returns nothing.
```

---

## Self-review notes

- Spec coverage: layout §1–7 → Tasks 1/5 (header, prose, now, projects, pubs, footer), 4 (activity panel), 2/3 (data), 6 (cache fallback, error handling), 7 (workflow triggers, 60-day keepalive via weekly commit). Testing section → per-task pytest + Task 6 step 5 local run + Task 7 step 5 visual check. ✔
- Type consistency: `activity` / `publications` shapes identical across Tasks 1–4, 6. ✔
- Placeholders: the two `_HERE` YAML values are deliberate user-input markers, resolved in Task 7 step 2 with an explicit remove-if-unknown rule. ✔
