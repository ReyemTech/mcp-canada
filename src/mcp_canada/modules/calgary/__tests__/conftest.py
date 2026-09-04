"""Shared fixtures for Calgary module unit tests.

Provides Socrata SODA API response fixtures for the discovery client functions,
plus an autouse cache+limiter patch (same pattern as nova_scotia).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Catalog / discovery fixtures
# ---------------------------------------------------------------------------

SAMPLE_CATALOG_RESPONSE: dict[str, Any] = {
    "results": [
        {
            "resource": {
                "id": "35ra-9556",
                "name": "Traffic Incidents",
                "description": "An unofficial archive of traffic incidents within Calgary.",
                "type": "dataset",
                "updatedAt": "2026-08-01T00:00:00.000Z",
                "columns_name": ["start_dt", "description", "quadrant"],
                "columns_field_name": ["start_dt", "description", "quadrant"],
                "download_count": 5210,
            },
            "classification": {
                "domain_category": "Transportation/Transit",
                "domain_tags": ["traffic", "incidents", "roads"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Calgary Roads"},
                ],
            },
            "metadata": {"domain": "data.calgary.ca"},
            "permalink": "https://data.calgary.ca/d/35ra-9556",
            "link": "https://data.calgary.ca/Transportation-Transit/Traffic-Incidents/35ra-9556",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "Open Calgary"},
        },
        {
            "resource": {
                "id": "6933-unw5",
                "name": "Building Permits",
                "description": "Development and building permits issued by the City of Calgary.",
                "type": "dataset",
                "updatedAt": "2026-08-01T00:00:00.000Z",
                "columns_name": ["permitnum", "permittype", "statuscurrent"],
                "columns_field_name": ["permitnum", "permittype", "statuscurrent"],
                "download_count": 9100,
            },
            "classification": {
                "domain_category": "Business and Economic Activity",
                "domain_tags": ["permits", "building", "development"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Calgary Building Services"},
                ],
            },
            "metadata": {"domain": "data.calgary.ca"},
            "permalink": "https://data.calgary.ca/d/6933-unw5",
            "link": "https://data.calgary.ca/Business-and-Economic-Activity/Building-Permits/6933-unw5",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "Open Calgary"},
        },
    ],
    "resultSetSize": 418,
    "timings": {},
    "warnings": [],
}


@pytest.fixture(autouse=True)
def _clear_cache_and_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch cached_fetch to pass-through (no actual cache) and get_limiter to no-op.

    This prevents test isolation issues from shared cache state and
    prevents actual rate limit delays during unit tests.
    """
    import mcp_canada.modules.calgary.client as _client_mod

    async def _passthrough_cached_fetch(key: str, ttl: int, fetcher):  # type: ignore[type-arg]
        return (await fetcher(), False)

    monkeypatch.setattr(
        "mcp_canada.modules.calgary.client.cached_fetch",
        _passthrough_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock(return_value=None)
    monkeypatch.setattr(_client_mod, "_limiter", mock_limiter)
