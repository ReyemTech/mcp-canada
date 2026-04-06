"""TTL-based async cache wrapper using aiocache."""

from collections.abc import Callable
from typing import Any

from aiocache import SimpleMemoryCache

_cache: SimpleMemoryCache = SimpleMemoryCache()


async def cached_fetch(key: str, ttl: int, fetcher: Callable) -> tuple[Any, bool]:
    """Fetch data from cache or call fetcher on miss.

    Args:
        key: Cache key string.
        ttl: Time-to-live in seconds.
        fetcher: Async callable that returns the data on cache miss.

    Returns:
        (data, was_cached) — was_cached is True if the value was already in cache.
    """
    cached_value = await _cache.get(key)
    if cached_value is not None:
        return cached_value, True

    data = await fetcher()
    await _cache.set(key, data, ttl=ttl)
    return data, False
