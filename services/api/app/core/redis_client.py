"""Redis client helper for dependency injection."""
from __future__ import annotations

from typing import Optional

from redis.asyncio import Redis

from .config import get_settings

_redis_client: Optional[Redis] = None


def get_redis() -> Redis:
    """Return a cached Redis client configured from settings."""

    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    return _redis_client
