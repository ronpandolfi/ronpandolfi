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
