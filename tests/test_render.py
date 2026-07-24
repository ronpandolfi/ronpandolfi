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
