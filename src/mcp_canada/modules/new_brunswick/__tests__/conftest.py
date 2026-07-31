"""Shared fixtures for New Brunswick module unit tests.

Autouse cache/limiter patch plus fixtures for every upstream surface this
module touches: federal CKAN (bilingual title_translated/notes_translated,
including a gnb.socrata.com resource url and a separately-published FR/EN
bilingual pair), the GeoNB service-directory + MapServer-layer enumeration
responses, per-curated-layer GeoJSON features (exact field names from
21-SPIKE.md §4), an empty FeatureCollection (a valid success, not an error),
and a 511 response fixture used only when a key is set.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Federal CKAN fixtures (organization:nb) — D-01, D-12
# ---------------------------------------------------------------------------

CKAN_PACKAGE_SEARCH_SAMPLE: dict[str, Any] = {
    "success": True,
    "result": {
        "count": 221,
        "results": [
            {
                "id": "aa11bb22-nb-submerged-lands",
                "name": "submerged-lands-management-areas",
                "title": "Submerged Lands Management Areas",
                "title_translated": {
                    "en": "Submerged Lands Management Areas",
                    "fr": "Zones de gestion des terres submergées",
                },
                "notes": "Areas of Crown-owned submerged land under NB jurisdiction.",
                "notes_translated": {
                    "en": "Areas of Crown-owned submerged land under NB jurisdiction.",
                    "fr": "Zones de terres submergées appartenant à la Couronne relevant du N.-B.",
                },
                "organization": {"name": "nb", "title": "New Brunswick"},
                "tags": [{"name": "environment"}, {"name": "coastal"}],
                "metadata_modified": "2026-05-01T00:00:00.000Z",
                "resources": [
                    {
                        "id": "res-1",
                        "name": "Submerged Lands CSV",
                        "format": "CSV",
                        "url": "https://open.canada.ca/data/dataset/aa11bb22/resource/res-1/download/submerged-lands.csv",
                    },
                ],
            },
            {
                "id": "cc33dd44-nb-childcare-en",
                "name": "licensed-early-learning-childcare-facilities-en",
                "title": "Licensed Early Learning and Childcare Facilities",
                "title_translated": {
                    "en": "Licensed Early Learning and Childcare Facilities",
                    "fr": "Licensed Early Learning and Childcare Facilities",
                },
                "notes": "Locations of licensed childcare facilities in New Brunswick.",
                "notes_translated": {
                    "en": "Locations of licensed childcare facilities in New Brunswick.",
                    "fr": "Locations of licensed childcare facilities in New Brunswick.",
                },
                "organization": {"name": "nb", "title": "New Brunswick"},
                "tags": [{"name": "childcare"}, {"name": "education"}],
                "metadata_modified": "2026-04-15T00:00:00.000Z",
                "resources": [
                    {
                        "id": "res-2",
                        "name": "Childcare facilities (Socrata mirror)",
                        "format": "CSV",
                        "url": "https://gnb.socrata.com/api/views/4zbh-z2ij/rows.csv",
                    },
                ],
            },
        ],
    },
}

# The separately-published French counterpart of the childcare dataset above —
# same title_translated/notes_translated shape, all-French content, a distinct
# CKAN id/name. RESEARCH Pitfall 5: this is NOT a duplicate to be deduplicated.
CKAN_CHILDCARE_FR_PACKAGE: dict[str, Any] = {
    "id": "ee55ff66-nb-childcare-fr",
    "name": "etablissements-de-garderies-educatives-agreees",
    "title": "Établissements de garderies éducatives agréées",
    "title_translated": {
        "en": "Établissements de garderies éducatives agréées",
        "fr": "Établissements de garderies éducatives agréées",
    },
    "notes": "Emplacements des établissements de garderie agréés au Nouveau-Brunswick.",
    "notes_translated": {
        "en": "Emplacements des établissements de garderie agréés au Nouveau-Brunswick.",
        "fr": "Emplacements des établissements de garderie agréés au Nouveau-Brunswick.",
    },
    "organization": {"name": "nb", "title": "New Brunswick"},
    "tags": [{"name": "garderie"}],
    "metadata_modified": "2026-04-15T00:00:00.000Z",
    "resources": [],
}


# ---------------------------------------------------------------------------
# gnb.socrata.com fixtures (checkpoint option-a)
# ---------------------------------------------------------------------------

GNB_SOCRATA_CATALOG_SAMPLE: dict[str, Any] = {
    "results": [
        {
            "resource": {
                "id": "4zbh-z2ij",
                "name": "Licensed Early Learning and Childcare Facilities",
                "description": "Locations of licensed childcare facilities.",
                "type": "dataset",
                "columns_field_name": ["facility_name", "address", "licence_number"],
                "updatedAt": "2026-05-01T00:00:00.000Z",
                "download_count": 412,
            },
            "classification": {
                "domain_category": "Health and Wellness",
                "domain_tags": ["childcare", "health"],
                "domain_metadata": [
                    {"key": "Common_Core.Department", "value": "Department of Education"},
                ],
            },
            "permalink": "https://gnb.socrata.com/d/4zbh-z2ij",
        },
    ],
    "resultSetSize": 312,
}

GNB_SOCRATA_ROWS_SAMPLE: list[dict[str, Any]] = [
    {"facility_name": "Sunshine Daycare", "address": "123 Main St", "licence_number": "NB-001"},
    {"facility_name": "Little Learners", "address": "456 King St", "licence_number": "NB-002"},
]


# ---------------------------------------------------------------------------
# GeoNB service-directory + MapServer-layer fixtures (D-06)
# ---------------------------------------------------------------------------

GEONB_SERVICE_DIRECTORY_SAMPLE: dict[str, Any] = {
    "currentVersion": 10.91,
    "folders": ["Utilities"],
    "services": [
        {"name": "GeoNB_DNR_Crown_Land", "type": "MapServer"},
        {"name": "GeoNB_ENV_Wetlands", "type": "MapServer"},
        {"name": "GeoNB_Basemap_Grey", "type": "MapServer"},
        {"name": "GeoNB_DNR_WildlifeRefuges", "type": "MapServer"},
    ],
}

GEONB_MAPSERVER_LAYERS_SAMPLE: dict[str, Any] = {
    "currentVersion": 10.91,
    "layers": [
        {"id": 3, "name": "Crown Land / Terres de la Couronne"},
    ],
    "tables": [],
}


# ---------------------------------------------------------------------------
# Per-curated-layer GeoJSON fixtures — exact field names from 21-SPIKE.md §4
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

FLOOD_HAZARD_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 1,
                "Sheet_Numb": "21G01",
                "Technical_": "Detailed",
                "Flood_Haza": "High",
            },
            "geometry": None,
        },
    ],
}

WETLANDS_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 1,
                "ID": "W-1",
                "Hectares": 4.2,
                "WC": "1",
                "WETLAND_CLASS": "Bog",
                "STATUS": "Provincially Significant",
            },
            "geometry": None,
        },
    ],
}

CIVIC_ADDRESS_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 1,
                "CIVIC_NUM": "440",
                "STREET": "King",
                "ST_TYPE_E": "St",
                "ST_TYPE_F": "Rue",
                "COMMUNITY": "Fredericton",
                "COUNTY": "York",
            },
            "geometry": None,
        },
    ],
}

# A valid success response — no features matched, NOT an error.
EMPTY_FEATURE_COLLECTION_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [],
}

# Health facility fixture — layer 0 (Hospital/Horizon) compact schema,
# live-verified field names (21-SPIKE.md §4 plus this plan's own probe).
HEALTH_FACILITY_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 1,
                "Hospital_N": "Dr. Everett Chalmers Regional Hospital",
                "Hospital_O": "Regional Hospital Corporation",
                "Name_E": "Dr. Everett Chalmers Regional Hospital",
                "Name_F": "Hôpital régional Dr-Everett-Chalmers",
                "Telephone_": "(506) 452-5400",
            },
            "geometry": None,
        },
    ],
}

# Public school fixture — layers 0/1 share one field schema (21-SPIKE.md §4).
PUBLIC_SCHOOL_GEOJSON: dict[str, Any] = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "OBJECTID": 2,
                "strID": "4010",
                "strDST": "ASD-N",
                "strNM": "Harcourt School",
                "strAD1": "155 West Side Harcourt Rd",
                "strGR": "Kindergarten, 1-5",
                "strURL": "http://harcourtschool.nbed.nb.ca",
            },
            "geometry": None,
        },
    ],
}


# ---------------------------------------------------------------------------
# NB 511 fixtures (key-gated — only exercised when NEW_BRUNSWICK_511_KEY is set)
# ---------------------------------------------------------------------------

FIVE11_EVENT_SAMPLE: list[dict[str, Any]] = [
    {
        "Id": "evt-1",
        "EventType": "roadwork",
        "Description": "Lane closure on Route 1",
        "Latitude": 45.96,
        "Longitude": -66.64,
    },
]


# ---------------------------------------------------------------------------
# Fake cached_fetch (bypasses cache, always returns fresh)
# ---------------------------------------------------------------------------


async def fake_cached_fetch(key: str, ttl: int, fetcher):
    return (await fetcher(), False)


# ---------------------------------------------------------------------------
# Autouse fixture: patch cached_fetch and all four rate limiters
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_cache_and_limiter(monkeypatch):
    """Patch cached_fetch to bypass cache and every module-level limiter to a no-op."""
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
    for limiter_name in (
        "_ckan_limiter",
        "_geonb_limiter",
        "_socrata_limiter",
        "_511_limiter",
    ):
        monkeypatch.setattr(
            f"mcp_canada.modules.new_brunswick.client.{limiter_name}",
            mock_limiter,
        )


@pytest.fixture
def crown_land_geojson() -> dict[str, Any]:
    return CROWN_LAND_GEOJSON


@pytest.fixture
def flood_hazard_geojson() -> dict[str, Any]:
    return FLOOD_HAZARD_GEOJSON


@pytest.fixture
def wetlands_geojson() -> dict[str, Any]:
    return WETLANDS_GEOJSON


@pytest.fixture
def civic_address_geojson() -> dict[str, Any]:
    return CIVIC_ADDRESS_GEOJSON


@pytest.fixture
def empty_feature_collection() -> dict[str, Any]:
    return EMPTY_FEATURE_COLLECTION_GEOJSON


@pytest.fixture
def ckan_package_search_sample() -> dict[str, Any]:
    return CKAN_PACKAGE_SEARCH_SAMPLE


@pytest.fixture
def ckan_childcare_fr_package() -> dict[str, Any]:
    return CKAN_CHILDCARE_FR_PACKAGE


@pytest.fixture
def gnb_socrata_catalog_sample() -> dict[str, Any]:
    return GNB_SOCRATA_CATALOG_SAMPLE


@pytest.fixture
def gnb_socrata_rows_sample() -> list[dict[str, Any]]:
    return GNB_SOCRATA_ROWS_SAMPLE


@pytest.fixture
def geonb_service_directory_sample() -> dict[str, Any]:
    return GEONB_SERVICE_DIRECTORY_SAMPLE


@pytest.fixture
def geonb_mapserver_layers_sample() -> dict[str, Any]:
    return GEONB_MAPSERVER_LAYERS_SAMPLE


@pytest.fixture
def five11_event_sample() -> list[dict[str, Any]]:
    return FIVE11_EVENT_SAMPLE


@pytest.fixture
def health_facility_geojson() -> dict[str, Any]:
    return HEALTH_FACILITY_GEOJSON


@pytest.fixture
def public_school_geojson() -> dict[str, Any]:
    return PUBLIC_SCHOOL_GEOJSON
