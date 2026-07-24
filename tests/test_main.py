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
