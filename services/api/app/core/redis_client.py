from __future__ import annotations

from functools import lru_cache
from typing import Optional

import redis

from .config import get_settings


@lru_cache(maxsize=1)
def _get_cached_redis() -> Optional["redis.Redis"]:
    settings = get_settings()
    url = getattr(settings, "REDIS_URL", None) or ""
    try:
        if not url:
            return None
        client = redis.from_url(url, decode_responses=True)
        # Try a lightweight ping; if it fails we still return client so callers can mock/override
        try:
            client.ping()
        except Exception:
            pass
        return client
    except Exception:
        # On any error, return None so tests can inject a mock
        return None


def get_redis() -> Optional["redis.Redis"]:
    """FastAPI dependency to obtain a Redis client or None.

    In tests, this is overridden in fixtures. In runtime, it returns a client
    based on `REDIS_URL` if available.
    """
    return _get_cached_redis()
