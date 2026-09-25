"""Unit tests for app/core/cache.py itself (not the fake from conftest.py).

This file overrides conftest's autouse `fake_cache` fixture with a no-op version, so
these tests exercise the real get_json/set_json/delete implementation — specifically,
that a broken Redis connection degrades gracefully instead of breaking the request.
"""

import pytest
import redis

from app.core import cache


@pytest.fixture(autouse=True)
def fake_cache():
    yield None


class _BrokenRedis:
    def get(self, key):
        raise redis.RedisError("simulated connection failure")

    def set(self, *args, **kwargs):
        raise redis.RedisError("simulated connection failure")

    def delete(self, *args, **kwargs):
        raise redis.RedisError("simulated connection failure")


def test_get_json_returns_none_when_redis_is_unavailable(monkeypatch):
    monkeypatch.setattr(cache, "redis_client", _BrokenRedis())
    assert cache.get_json("some-key") is None


def test_set_json_does_not_raise_when_redis_is_unavailable(monkeypatch):
    monkeypatch.setattr(cache, "redis_client", _BrokenRedis())
    cache.set_json("some-key", {"a": 1}, ttl_seconds=10)  # must not raise


def test_delete_does_not_raise_when_redis_is_unavailable(monkeypatch):
    monkeypatch.setattr(cache, "redis_client", _BrokenRedis())
    cache.delete("some-key")  # must not raise
