"""Shared pytest fixtures for mcp-canada tests."""

import pytest
import httpx

from mcp_canada.shared.rate_limiter import TokenBucket


class MockTransport(httpx.AsyncBaseTransport):
    """Mock transport that returns 200 JSON {"ok": true}."""

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"ok": True},
            request=request,
        )


@pytest.fixture
def mock_http_client() -> httpx.AsyncClient:
    """Return an httpx.AsyncClient backed by a mock transport."""
    return httpx.AsyncClient(transport=MockTransport())


@pytest.fixture
def rate_limiter() -> TokenBucket:
    """Return a TokenBucket configured at 10 tokens/sec with capacity 10."""
    return TokenBucket(rate=10.0, capacity=10)
