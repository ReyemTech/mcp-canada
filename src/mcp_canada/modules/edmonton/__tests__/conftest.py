"""Shared fixtures for Edmonton module unit tests.

Provides Socrata SODA API response fixtures for the discovery client functions,
plus an autouse cache+limiter patch (same pattern as nova_scotia / calgary).
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
                "id": "24uj-dj8v",
                "name": "General Building Permits",
                "description": "List of issued building permits from the City of Edmonton.",
                "type": "dataset",
                "updatedAt": "2026-08-01T00:00:00.000Z",
                "columns_name": ["permit_date", "job_description", "status"],
                "columns_field_name": ["permit_date", "job_description", "status"],
                "download_count": 62493,
            },
            "classification": {
                "domain_category": "Urban Planning & Economy",
                "domain_tags": ["permits", "building", "construction"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Urban Planning & Economy"},
                ],
            },
            "metadata": {"domain": "data.edmonton.ca"},
            "permalink": "https://data.edmonton.ca/d/24uj-dj8v",
            "link": "https://data.edmonton.ca/Urban-Planning-Economy/General-Building-Permits/24uj-dj8v",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "City of Edmonton"},
        },
        {
            "resource": {
                "id": "msh8-if28",
                "name": "Property Assessment Data",
                "description": "Current year property assessment data for the City of Edmonton.",
                "type": "dataset",
                "updatedAt": "2026-08-01T00:00:00.000Z",
                "columns_name": ["account_number", "assessed_value", "neighbourhood"],
                "columns_field_name": ["account_number", "assessed_value", "neighbourhood"],
                "download_count": 40210,
            },
            "classification": {
                "domain_category": "City Administration",
                "domain_tags": ["assessment", "property", "tax"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Assessment and Taxation"},
                ],
            },
            "metadata": {"domain": "data.edmonton.ca"},
            "permalink": "https://data.edmonton.ca/d/msh8-if28",
            "link": "https://data.edmonton.ca/City-Administration/Property-Assessment-Data/msh8-if28",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "City of Edmonton"},
        },
    ],
    "resultSetSize": 1421,
    "timings": {},
    "warnings": [],
}


@pytest.fixture(autouse=True)
def _clear_cache_and_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch cached_fetch to pass-through (no actual cache) and get_limiter to no-op.

    This prevents test isolation issues from shared cache state and
    prevents actual rate limit delays during unit tests.
    """
    import mcp_canada.modules.edmonton.client as _client_mod

    async def _passthrough_cached_fetch(key: str, ttl: int, fetcher):  # type: ignore[type-arg]
        return (await fetcher(), False)

    monkeypatch.setattr(
        "mcp_canada.modules.edmonton.client.cached_fetch",
        _passthrough_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock(return_value=None)
    monkeypatch.setattr(_client_mod, "_limiter", mock_limiter)
