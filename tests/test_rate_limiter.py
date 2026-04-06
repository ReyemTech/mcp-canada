"""Tests for shared/rate_limiter.py — token bucket rate limiter."""

import pytest
import time


@pytest.mark.asyncio
async def test_token_bucket_allows_burst():
    """TokenBucket should allow capacity-many immediate acquires."""
    from mcp_canada.shared.rate_limiter import TokenBucket

    bucket = TokenBucket(rate=10.0, capacity=10)

    # Acquire all 10 tokens — should complete immediately (under 0.1s)
    start = time.monotonic()
    for _ in range(10):
        await bucket.acquire()
    elapsed = time.monotonic() - start

    assert elapsed < 0.5, f"Burst should be immediate, took {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_token_bucket_throttles():
    """TokenBucket should throttle when capacity is exceeded."""
    from mcp_canada.shared.rate_limiter import TokenBucket

    # Very slow rate so 11th token must wait
    bucket = TokenBucket(rate=100.0, capacity=5)

    # Drain the bucket
    for _ in range(5):
        await bucket.acquire()

    # 6th acquire should take measurable time (at least 1/100 = 0.01s)
    start = time.monotonic()
    await bucket.acquire()
    elapsed = time.monotonic() - start

    assert elapsed >= 0.005, f"Should have waited for token, elapsed: {elapsed:.3f}s"


def test_get_limiter_singleton():
    """get_limiter should return the same instance for the same source."""
    from mcp_canada.shared.rate_limiter import get_limiter, _limiters

    # Clear existing limiters to ensure a clean test
    _limiters.clear()

    limiter1 = get_limiter("test_source")
    limiter2 = get_limiter("test_source")

    assert limiter1 is limiter2


def test_different_sources_get_independent_buckets():
    """Different source names should get independent TokenBucket instances."""
    from mcp_canada.shared.rate_limiter import get_limiter, _limiters

    _limiters.clear()

    limiter_a = get_limiter("source_alpha")
    limiter_b = get_limiter("source_beta")

    assert limiter_a is not limiter_b
