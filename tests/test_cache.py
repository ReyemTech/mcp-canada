"""Tests for shared/cache.py — TTL-based async cache."""

import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_cache_miss_calls_fetcher():
    """cached_fetch should call fetcher on cache miss and return (data, False)."""
    from mcp_canada.shared.cache import cached_fetch

    fetcher = AsyncMock(return_value={"value": 42})
    data, was_cached = await cached_fetch("test_miss_key", ttl=60, fetcher=fetcher)

    assert data == {"value": 42}
    assert was_cached is False
    fetcher.assert_called_once()


@pytest.mark.asyncio
async def test_cache_hit_skips_fetcher():
    """cached_fetch should return cached data and True on hit, without calling fetcher."""
    from mcp_canada.shared.cache import cached_fetch

    fetcher = AsyncMock(return_value={"value": 99})
    key = "test_hit_key_unique"

    # First call — miss
    data1, cached1 = await cached_fetch(key, ttl=60, fetcher=fetcher)
    assert cached1 is False
    assert fetcher.call_count == 1

    # Second call — hit
    data2, cached2 = await cached_fetch(key, ttl=60, fetcher=fetcher)
    assert cached2 is True
    assert data2 == {"value": 99}
    assert fetcher.call_count == 1  # Not called again


@pytest.mark.asyncio
async def test_different_keys_independent():
    """Different cache keys should be stored independently."""
    from mcp_canada.shared.cache import cached_fetch

    fetcher_a = AsyncMock(return_value={"source": "a"})
    fetcher_b = AsyncMock(return_value={"source": "b"})

    data_a, _ = await cached_fetch("key_a_unique", ttl=60, fetcher=fetcher_a)
    data_b, _ = await cached_fetch("key_b_unique", ttl=60, fetcher=fetcher_b)

    assert data_a == {"source": "a"}
    assert data_b == {"source": "b"}
