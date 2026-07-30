"""Shared fixtures for New Brunswick module unit tests.

TRACER SUBSET (Task 1) — autouse cache/limiter patch plus a Crown Land GeoJSON
fixture. Task 4 extends this with federal CKAN, bilingual-pair, GeoNB
service-directory, MapServer-layer and per-curated-layer fixtures.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# GeoJSON fixtures
# ---------------------------------------------------------------------------

CROWN_LAND_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 1,
                "HOLDER": 2,
                "Shape_Length": 1234.5,
                "Shape_Area": 98765.4,
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 2,
                "HOLDER": 7,
                "Shape_Length": 987.6,
                "Shape_Area": 54321.0,
            },
            "geometry": None,
        },
    ],
}


# ---------------------------------------------------------------------------
# Fake cached_fetch (bypasses cache, always returns fresh)
# ---------------------------------------------------------------------------


async def fake_cached_fetch(key: str, ttl: int, fetcher):
    return (await fetcher(), False)


# ---------------------------------------------------------------------------
# Autouse fixture: patch cached_fetch and get_limiter
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_cache_and_limiter(monkeypatch):
    """Patch cached_fetch to bypass cache and the module-level limiter to a no-op."""
    monkeypatch.setattr(
        "mcp_canada.modules.new_brunswick.client.cached_fetch",
        fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.new_brunswick.client.get_limiter",
        _fake_get_limiter,
    )
    monkeypatch.setattr(
        "mcp_canada.modules.new_brunswick.client._geonb_limiter",
        mock_limiter,
    )


@pytest.fixture
def crown_land_geojson() -> dict[str, Any]:
    return CROWN_LAND_GEOJSON
