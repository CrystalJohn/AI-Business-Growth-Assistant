"""Response cache tests."""
import pytest
from app.services.response_cache import response_cache


def test_cache_set_get():
    response_cache.clear()
    response_cache["test_key"] = {"answer": "test", "rows": 1}
    result = response_cache.get("test_key")
    assert result is not None
    assert result["answer"] == "test"


def test_cache_miss():
    response_cache.clear()
    result = response_cache.get("nonexistent")
    assert result is None


def test_cache_overwrite():
    response_cache.clear()
    response_cache["key1"] = {"v": 1}
    response_cache["key1"] = {"v": 2}
    result = response_cache.get("key1")
    assert result["v"] == 2
