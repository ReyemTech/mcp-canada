"""Shared fixtures for british_columbia module unit tests.

Covers both CKAN (package_search, package_show, org/tag lists) and
WFS (active fires, fire perimeters, protected areas, mining, water wells,
exception reports, two-page pagination) sample responses.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# CKAN fixtures
# ---------------------------------------------------------------------------

def _make_ckan_dataset(
    pkg_id: str,
    name: str,
    title: str,
    bcdc_type: str = "Geographic",
    object_name: str | None = None,
    storage_location: str | None = None,
    resource_format: str = "wfs",
) -> dict[str, Any]:
    """Build a minimal CKAN package dict."""
    resources = []
    if object_name:
        resources.append({
            "id": f"{pkg_id}-res-1",
            "name": f"{title} WFS",
            "format": "wfs",
            "url": f"https://openmaps.gov.bc.ca/geo/ows?typeName={object_name}",
            "bcdc_type": "geographic",
            "resource_storage_location": storage_location or "bc geographic warehouse",
            "resource_type": "data",
            "object_name": object_name,
        })
    else:
        resources.append({
            "id": f"{pkg_id}-res-1",
            "name": f"{title} CSV",
            "format": resource_format,
            "url": f"https://example.com/{name}.csv",
            "bcdc_type": "document",
            "resource_storage_location": "external",
            "resource_type": "data",
            "object_name": None,
        })
    return {
        "id": pkg_id,
        "name": name,
        "title": title,
        "notes": f"Sample notes for {title}.",
        "organization": {"title": "BC Wildfire Service", "name": "bc-wildfire-service"},
        "bcdc_type": bcdc_type,
        "metadata_modified": "2026-01-15T10:00:00",
        "tags": [{"name": "wildfire"}, {"name": "fire"}],
        "resources": resources,
    }


CKAN_SEARCH_RESULT: dict[str, Any] = {
    "success": True,
    "result": {
        "count": 2,
        "results": [
            _make_ckan_dataset(
                "pkg-fire-001",
                "bc-historical-fire-perimeters",
                "BC Historical Fire Perimeters",
                bcdc_type="Geographic",
                object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
                storage_location="bc geographic warehouse",
            ),
            _make_ckan_dataset(
                "pkg-fire-002",
                "bc-fire-report",
                "BC Fire Report Dataset",
                bcdc_type="Document",
                object_name=None,
                resource_format="csv",
            ),
        ],
    },
}

CKAN_PACKAGE_SHOW_WFS: dict[str, Any] = {
    "success": True,
    "result": _make_ckan_dataset(
        "pkg-fire-001",
        "bc-historical-fire-perimeters",
        "BC Historical Fire Perimeters",
        bcdc_type="Geographic",
        object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
        storage_location="bc geographic warehouse",
    ),
}

CKAN_PACKAGE_SHOW_FILE: dict[str, Any] = {
    "success": True,
    "result": _make_ckan_dataset(
        "pkg-fire-002",
        "bc-fire-report",
        "BC Fire Report Dataset",
        bcdc_type="Document",
        object_name=None,
        resource_format="csv",
    ),
}

CKAN_ORGANIZATION_LIST: dict[str, Any] = {
    "success": True,
    "result": ["env-air-quality", "bc-wildfire-service", "min-forests", "min-env", "min-health"],
}

CKAN_TAG_LIST: dict[str, Any] = {
    "success": True,
    "result": ["wildfire", "forestry", "water", "mining", "parks", "climate"],
}


# ---------------------------------------------------------------------------
# WFS GeoJSON fixtures
# ---------------------------------------------------------------------------

def _make_fire_feature(i: int) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": f"PROT_CURRENT_FIRE_PNTS_SP.{i}",
        "geometry": {"type": "Point", "coordinates": [-123.0 + i * 0.5, 51.0 + i * 0.2]},
        "properties": {
            "FIRE_NUMBER": f"C{i:05d}",
            "FIRE_YEAR": 2026,
            "FIRE_STATUS": "Active",
            "FIRE_CAUSE": "Lightning",
            "FIRE_CENTRE": "Kamloops Fire Centre",
            "CURRENT_SIZE": 12.5 + i * 5,
            "LATITUDE": 51.0 + i * 0.2,
            "LONGITUDE": -123.0 + i * 0.5,
            "INCIDENT_NAME": f"Test Fire {i}",
        },
    }


def _make_perimeter_feature(i: int) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": f"PROT_HISTORICAL_FIRE_POLYS_SP.{i}",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-123.0, 51.0], [-122.9, 51.0], [-122.9, 51.1], [-123.0, 51.0]]],
        },
        "properties": {
            "FIRE_YEAR": 2023,
            "FIRE_SIZE_HECTARES": 450.0 + i * 100,
            "FIRE_LABEL": f"FIRE-2023-{i:03d}",
            "SOURCE": "BC Wildfire Service",
        },
    }


def _make_protected_area_feature(i: int) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": f"TA_PARK_ECORES_PA_SVW.{i}",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-120.0, 50.0], [-119.9, 50.0], [-119.9, 50.1], [-120.0, 50.0]]],
        },
        "properties": {
            "PROTECTED_LANDS_NAME": f"Test Provincial Park {i}",
            "PROTECTED_LANDS_DESIGNATION": "PROVINCIAL PARK",
            "OFFICIAL_AREA_HA": 5000.0 + i * 1000,
        },
    }


def _make_mining_feature(i: int) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": f"MTA_ACQUIRED_TENURE_SVW.{i}",
        "geometry": {"type": "Point", "coordinates": [-120.5, 50.5]},
        "properties": {
            "TENURE_NUMBER_ID": f"MTA-{i:06d}",
            "CLAIM_NAME": f"Test Claim {i}",
            "TENURE_TYPE_CODE": "M",
            "OWNER_NAME": f"Test Mining Corp {i}",
            "AREA_IN_HECTARES": 25.0 + i * 5,
        },
    }


def _make_water_well_feature(i: int) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": f"GW_WATER_WELLS_WRBC_SVW.{i}",
        "geometry": {"type": "Point", "coordinates": [-120.3, 50.7]},
        "properties": {
            "WELL_CLASS": "DOMESTIC",
            "CITY": "Kamloops",
            "INTENDED_WATER_USE": "Domestic",
            "AQUIFER_ID": 100 + i,
        },
    }


def _make_geojson(features: list[dict[str, Any]], number_returned: int | None = None) -> dict[str, Any]:
    if number_returned is None:
        number_returned = len(features)
    return {
        "type": "FeatureCollection",
        "totalFeatures": 1500,
        "numberMatched": 1500,
        "numberReturned": number_returned,
        "features": features,
    }


WFS_EXCEPTION_REPORT_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport version="2.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
  <ows:Exception exceptionCode="InvalidParameterValue" locator="typeNames">
    <ows:ExceptionText>Feature type NO_SUCH_LAYER unknown</ows:ExceptionText>
  </ows:Exception>
</ows:ExceptionReport>"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_ckan_package_search_response() -> dict[str, Any]:
    """CKAN package_search response with 2 datasets (one WFS-queryable, one file)."""
    return CKAN_SEARCH_RESULT


@pytest.fixture
def sample_ckan_package_show_wfs_response() -> dict[str, Any]:
    """CKAN package_show for a WFS-queryable dataset (queryable_via_wfs=True)."""
    return CKAN_PACKAGE_SHOW_WFS


@pytest.fixture
def sample_ckan_package_show_file_response() -> dict[str, Any]:
    """CKAN package_show for a file-only dataset (queryable_via_wfs=False)."""
    return CKAN_PACKAGE_SHOW_FILE


@pytest.fixture
def sample_ckan_organization_list_response() -> dict[str, Any]:
    """CKAN organization_list response with BC ministry slugs."""
    return CKAN_ORGANIZATION_LIST


@pytest.fixture
def sample_ckan_tag_list_response() -> dict[str, Any]:
    """CKAN tag_list response with common BC Data Catalogue tags."""
    return CKAN_TAG_LIST


@pytest.fixture
def sample_wfs_active_fires_geojson() -> dict[str, Any]:
    """WFS FeatureCollection with 2 active fire point features."""
    return _make_geojson([_make_fire_feature(1), _make_fire_feature(2)])


@pytest.fixture
def sample_wfs_fire_perimeters_geojson() -> dict[str, Any]:
    """WFS FeatureCollection with 2 historical fire perimeter polygon features."""
    return _make_geojson([_make_perimeter_feature(1), _make_perimeter_feature(2)])


@pytest.fixture
def sample_wfs_protected_areas_geojson() -> dict[str, Any]:
    """WFS FeatureCollection with 2 provincial park polygon features."""
    return _make_geojson([_make_protected_area_feature(1), _make_protected_area_feature(2)])


@pytest.fixture
def sample_wfs_mining_tenure_geojson() -> dict[str, Any]:
    """WFS FeatureCollection with 2 mining tenure features."""
    return _make_geojson([_make_mining_feature(1), _make_mining_feature(2)])


@pytest.fixture
def sample_wfs_water_wells_geojson() -> dict[str, Any]:
    """WFS FeatureCollection with 2 water well features in Kamloops."""
    return _make_geojson([_make_water_well_feature(1), _make_water_well_feature(2)])


@pytest.fixture
def sample_wfs_exception_report_xml() -> str:
    """ows:ExceptionReport XML string for WFS error parsing tests."""
    return WFS_EXCEPTION_REPORT_XML


@pytest.fixture
def sample_wfs_two_page_geojson() -> tuple[dict[str, Any], dict[str, Any]]:
    """Two-page pagination scenario: page1=1000 features (has_more=True), page2=500 (last)."""
    page1_features = [_make_fire_feature(i) for i in range(1000)]
    page2_features = [_make_fire_feature(i) for i in range(1000, 1500)]
    page1 = _make_geojson(page1_features, number_returned=1000)
    page2 = _make_geojson(page2_features, number_returned=500)
    return page1, page2


# ---------------------------------------------------------------------------
# Autouse fixture: patch cached_fetch and get_limiter
# ---------------------------------------------------------------------------


async def fake_cached_fetch(key: str, ttl: int, fetcher):
    """Bypass cache; always call fetcher directly."""
    return (await fetcher(), False)


@pytest.fixture(autouse=True)
def patch_cache_and_limiter(monkeypatch):
    """Patch cached_fetch to bypass cache and get_limiter to return a no-op mock."""
    monkeypatch.setattr(
        "mcp_canada.modules.british_columbia.client.cached_fetch",
        fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.british_columbia.client.get_limiter",
        _fake_get_limiter,
    )
