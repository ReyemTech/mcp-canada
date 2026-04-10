"""Shared fixtures for york_region module unit tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Raw Hub Search API response fixtures
# ---------------------------------------------------------------------------

HUB_SEARCH_RAW: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 50,
    "numberReturned": 2,
    "features": [
        {
            "id": "abc123",
            "properties": {
                "title": "York Region Bus Stops",
                "type": "Feature Service",
                "description": "All YRT/Viva bus stop locations in York Region.",
                "url": "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer/2",
                "owner": "YorkRegion_GIS",
                "tags": ["transit", "bus", "stops"],
                "categories": ["Transportation"],
                "created": "2021-01-15T00:00:00.000Z",
                "modified": "2024-06-01T00:00:00.000Z",
            },
        },
        {
            "id": "def456",
            "properties": {
                "title": "Beach Water Testing",
                "type": "Feature Service",
                "description": "Annual beach water testing results.",
                "url": "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Health_And_Safety/FeatureServer/0",
                "owner": "YorkRegion_Health",
                "tags": ["health", "beaches", "water"],
                "categories": ["Health", "Environment"],
                "created": "2020-05-01T00:00:00.000Z",
                "modified": "2023-08-15T00:00:00.000Z",
            },
        },
    ],
    "links": [],
}

HUB_SEARCH_EMPTY: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 0,
    "numberReturned": 0,
    "features": [],
    "links": [],
}

# Feature result fixtures (as returned by query_feature_service)
FEATURE_RESULT_SINGLE_PAGE: tuple[list[dict], bool] = (
    [
        {"OBJECTID": 1, "STOP_NAME": "Stop A", "STOP_ID": "1001"},
        {"OBJECTID": 2, "STOP_NAME": "Stop B", "STOP_ID": "1002"},
    ],
    False,
)

# Simulate 5000 features truncated
FEATURE_RESULT_TRUNCATED: tuple[list[dict], bool] = (
    [{"OBJECTID": i} for i in range(5000)],
    True,
)


# ---------------------------------------------------------------------------
# Fake cached_fetch for tests (bypasses cache, always returns fresh)
# ---------------------------------------------------------------------------

async def fake_cached_fetch(key: str, ttl: int, fetcher):
    return (await fetcher(), False)


# ---------------------------------------------------------------------------
# Autouse fixture: patch cached_fetch and get_limiter
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_cache_and_limiter(monkeypatch):
    """Patch cached_fetch to bypass cache and get_limiter to return a no-op mock."""
    monkeypatch.setattr(
        "mcp_canada.modules.york_region.client.cached_fetch",
        fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.york_region.client.get_limiter",
        _fake_get_limiter,
    )
