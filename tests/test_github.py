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


def test_summarize_contributions_excludes_languages():
    fixture = _gql_fixture()
    fixture["data"]["user"]["repositories"]["nodes"][0]["languages"]["edges"].append(
        {"size": 90000, "node": {"name": "Jupyter Notebook"}})
    act = build.summarize_contributions(fixture, exclude_languages={"Jupyter Notebook"})
    assert [l["name"] for l in act["languages"]] == ["Python", "C++"]
    assert act["languages"][0]["pct"] == 70.0
