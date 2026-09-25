import json
import logging

import redis

from app.core.config import settings

logger = logging.getLogger("taskhub.cache")

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)


def get_json(key: str) -> object | None:
    # Caching is a performance optimization, not something the API should hard-depend
    # on — if Redis is unreachable, fall back to "no cache" instead of failing the
    # request, so callers just always hit the DB in that case.
    try:
        raw = redis_client.get(key)
    except redis.RedisError:
        logger.warning("Redis unavailable, skipping cache read for %s", key)
        return None
    if raw is None:
        return None
    return json.loads(raw)


def set_json(key: str, value: object, *, ttl_seconds: int) -> None:
    try:
        redis_client.set(key, json.dumps(value), ex=ttl_seconds)
    except redis.RedisError:
        logger.warning("Redis unavailable, skipping cache write for %s", key)


def delete(key: str) -> None:
    try:
        redis_client.delete(key)
    except redis.RedisError:
        logger.warning("Redis unavailable, skipping cache invalidation for %s", key)
