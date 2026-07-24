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
