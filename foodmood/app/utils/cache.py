"""
Simple in-process TTL cache for meal parse results.

Design decision:
- cachetools.TTLCache (LRU + time-to-live) is lightweight and requires no
  external service (Redis, Memcached), keeping the project self-contained.
- Key = hash of normalised meal description so identical meals hit the cache
  regardless of minor whitespace / capitalisation differences.
- TTL configured via CACHE_TTL_SECONDS in .env (default 1 hour).

Trade-off: Cache is per-process and resets on restart.
  With more time: swap for Redis to support horizontal scaling.
"""

import hashlib
from cachetools import TTLCache
from app.core.config import get_settings

settings = get_settings()

# max 256 distinct meal descriptions cached at a time
_cache: TTLCache = TTLCache(maxsize=256, ttl=settings.cache_ttl_seconds)


def _make_key(meal_description: str) -> str:
    normalised = meal_description.lower().strip()
    return hashlib.md5(normalised.encode()).hexdigest()


def get_cached(meal_description: str) -> dict | None:
    """Return cached parse result or None."""
    return _cache.get(_make_key(meal_description))


def set_cached(meal_description: str, result: dict) -> None:
    """Store parse result in cache."""
    _cache[_make_key(meal_description)] = result


def cache_stats() -> dict:
    return {"size": len(_cache), "maxsize": _cache.maxsize, "ttl_seconds": _cache.ttl}
