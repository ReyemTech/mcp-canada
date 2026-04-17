"""Shared fixtures for alberta module unit tests.

Covers CKAN (package_search, package_show, org list, format facet), ArcGIS
(GeoJSON + ESRI JSON), 511 Alberta (events, winter roads, cameras), and AER
static report samples (ST1 TXT, ST3 XLSX rows, ST39 rows).

All fixtures mirror real production response shapes (live-verified 2026-04-17).

Downstream plans (02-08) consume these fixtures by name — DO NOT redefine them
in per-file test_*.py files.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# CKAN fixtures — open.alberta.ca
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_ckan_package_search_response():
    """package_search — mirrors open.alberta.ca response shape (verified 2026-04-17).

    Includes Alberta-specific extras quirks (Pitfall 11: 50+ extras to flatten)
    and realistic resources (one ESRI REST + one CSV) to exercise the
    alberta_query_dataset router in Plan 02.
    """
    return {
        "success": True,
        "result": {
            "count": 33269,
            "results": [
                {
                    "id": "ab-dataset-1",
                    "name": "wildfire-data",
                    "title": "Alberta Wildfire Data",
                    "notes": "Active wildfire incidents and historical perimeters...",
                    "organization": {
                        "name": "forestry-and-parks",
                        "title": "Forestry and Parks",
                    },
                    "license_id": "open-gov-licence-alberta",
                    "extras": [
                        {"key": "identifier-AGDEX-number", "value": "636"},
                        {"key": "identifier-ISBN-pdf", "value": "978-0-7785-9999-9"},
                        {"key": "audience", "value": "general public"},
                        {"key": "frequencyofupdate", "value": "continuous"},
                        {"key": "spatial-coverage", "value": "Alberta"},
                    ],
                    "resources": [
                        {
                            "id": "res-fs-001",
                            "name": "Active Wildfires FeatureServer",
                            "format": "ESRI REST",
                            "url": "https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/Active_Wildfires_Dashboard_view/FeatureServer/0",
                        },
                        {
                            "id": "res-csv-001",
                            "name": "Historical perimeters CSV",
                            "format": "CSV",
                            "url": "https://example.alberta.ca/perimeters.csv",
                        },
                    ],
                    "num_resources": 2,
                    "num_tags": 5,
                },
                {
                    "id": "ab-dataset-2",
                    "name": "oil-gas-wells",
                    "title": "Oil and Gas Well Licences",
                    "notes": "AER well licence registry...",
                    "organization": {
                        "name": "energy-and-minerals",
                        "title": "Energy and Minerals",
                    },
                    "license_id": "open-gov-licence-alberta",
                    "extras": [],
                    "resources": [
                        {
                            "id": "res-pdf-001",
                            "name": "Annual report",
                            "format": "PDF",
                            "url": "https://example.alberta.ca/report.pdf",
                        },
                    ],
                    "num_resources": 1,
                    "num_tags": 3,
                },
            ],
        },
    }


@pytest.fixture
def sample_ckan_package_show_response():
    """package_show for a wildfire dataset with 50+ extras (Pitfall 11)."""
    return {
        "success": True,
        "result": {
            "id": "wildfire-data",
            "name": "wildfire-data",
            "title": "Alberta Wildfire Data",
            "notes": "Active wildfire incidents and historical perimeters.",
            "organization": {
                "name": "forestry-and-parks",
                "title": "Forestry and Parks",
            },
            "license_id": "open-gov-licence-alberta",
            "extras": [
                {"key": f"extra-field-{i}", "value": f"value-{i}"}
                for i in range(55)
            ],
            "resources": [
                {
                    "id": "res-fs-001",
                    "name": "Active Wildfires FeatureServer",
                    "format": "ESRI REST",
                    "url": "https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/Active_Wildfires_Dashboard_view/FeatureServer/0",
                },
                {
                    "id": "res-csv-001",
                    "name": "Historical perimeters CSV",
                    "format": "CSV",
                    "url": "https://example.alberta.ca/perimeters.csv",
                },
            ],
        },
    }


@pytest.fixture
def sample_ckan_organization_list():
    """organization_list — 5 orgs from the 370-org Alberta catalogue."""
    return {
        "success": True,
        "result": [
            {
                "name": "forestry-and-parks",
                "title": "Forestry and Parks",
                "package_count": 240,
            },
            {
                "name": "energy-and-minerals",
                "title": "Energy and Minerals",
                "package_count": 185,
            },
            {
                "name": "health",
                "title": "Health",
                "package_count": 120,
            },
            {
                "name": "transportation-and-economic-corridors",
                "title": "Transportation and Economic Corridors",
                "package_count": 95,
            },
            {
                "name": "environment-and-protected-areas",
                "title": "Environment and Protected Areas",
                "package_count": 150,
            },
        ],
    }


@pytest.fixture
def sample_ckan_format_facet():
    """package_search?facet.field=res_format — Alberta's categories substitute.

    Pitfall 1: group_list returns empty on open.alberta.ca, so Plan 02's
    alberta_list_categories must pivot to the res_format facet instead.
    """
    return {
        "success": True,
        "result": {
            "count": 33269,
            "results": [],
            "facets": {
                "res_format": {
                    "PDF": 28763,
                    "XLSX": 774,
                    "CSV": 224,
                    "ESRI REST": 93,
                    "HTML": 85,
                    "JSON": 42,
                },
            },
        },
    }


# ---------------------------------------------------------------------------
# ArcGIS fixtures — WMBappServices + AHSGIS + GeoDiscover Alberta
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_arcgis_query_geojson():
    """FeatureServer /query?f=geojson — active wildfires (2 sample features)."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-114.0719, 54.7267]},
                "properties": {
                    "FIRE_NUMBER": "SWF054-2026",
                    "FIRE_STATUS": "Under Control",
                    "AREA_ESTIMATE": 12.4,
                    "FOREST_AREA": "Slave Lake",
                    "FIRE_START_DATE": 1713398400000,
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-119.4201, 58.7389]},
                "properties": {
                    "FIRE_NUMBER": "HWF021-2026",
                    "FIRE_STATUS": "Being Held",
                    "AREA_ESTIMATE": 89.2,
                    "FOREST_AREA": "High Level",
                    "FIRE_START_DATE": 1713312000000,
                },
            },
        ],
        "exceededTransferLimit": False,
    }


@pytest.fixture
def sample_arcgis_query_json():
    """FeatureServer /query?f=json — AHS hospitals (ESRI JSON attributes shape)."""
    return {
        "features": [
            {
                "attributes": {
                    "NAME": "Foothills Medical Centre",
                    "CITY": "Calgary",
                    "ZONE": "Calgary",
                    "INPATIENT_BEDS": 952,
                    "HAS_ED": 1,
                },
                "geometry": {"x": -114.1311, "y": 51.0654},
            },
            {
                "attributes": {
                    "NAME": "Royal Alexandra Hospital",
                    "CITY": "Edmonton",
                    "ZONE": "Edmonton",
                    "INPATIENT_BEDS": 705,
                    "HAS_ED": 1,
                },
                "geometry": {"x": -113.4909, "y": 53.5625},
            },
        ],
        "exceededTransferLimit": False,
    }


# ---------------------------------------------------------------------------
# 511 Alberta fixtures — JSON list (NOT CKAN envelope — Pitfall 6)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_511_event_list():
    """/api/v2/get/event — road events (closures + construction + incidents)."""
    return [
        {
            "ID": "ab-event-001",
            "RoadwayName": "Highway 2",
            "EventType": "closure",
            "IsFullClosure": True,
            "Latitude": 53.5444,
            "Longitude": -113.4909,
            "Reported": "2026-04-17T08:15:00Z",
            "LastUpdated": "2026-04-17T09:30:00Z",
            "Description": "Full closure northbound due to collision",
        },
        {
            "ID": "ab-event-002",
            "RoadwayName": "Highway 1",
            "EventType": "construction",
            "IsFullClosure": False,
            "Latitude": 51.0447,
            "Longitude": -114.0719,
            "Reported": "2026-04-14T00:00:00Z",
            "LastUpdated": "2026-04-17T00:00:00Z",
            "Description": "Lane reduction westbound for repaving",
        },
        {
            "ID": "ab-event-003",
            "RoadwayName": "Highway 63",
            "EventType": "incident",
            "IsFullClosure": False,
            "Latitude": 56.7267,
            "Longitude": -111.3881,
            "Reported": "2026-04-17T07:00:00Z",
            "LastUpdated": "2026-04-17T09:00:00Z",
            "Description": "Vehicle fire on shoulder",
        },
    ]


@pytest.fixture
def sample_511_winter_roads():
    """/api/v2/get/winterroads — road-surface condition segments."""
    return [
        {
            "ID": "wr-001",
            "RoadwayName": "Highway 2",
            "Condition": "bare and dry",
            "Visibility": "good",
            "LastUpdated": "2026-04-17T09:00:00Z",
        },
        {
            "ID": "wr-002",
            "RoadwayName": "Highway 93",
            "Condition": "snow covered",
            "Visibility": "poor",
            "LastUpdated": "2026-04-17T09:00:00Z",
        },
    ]


@pytest.fixture
def sample_511_cameras():
    """/api/v2/get/cameras — traffic-camera locations with Views array."""
    return [
        {
            "ID": "cam-001",
            "Name": "Hwy 2 @ Leduc",
            "Latitude": 53.2619,
            "Longitude": -113.5525,
            "Views": [
                {"Url": "https://511.alberta.ca/map/cam-001/n.jpg", "Direction": "N"},
                {"Url": "https://511.alberta.ca/map/cam-001/s.jpg", "Direction": "S"},
            ],
        },
        {
            "ID": "cam-002",
            "Name": "Hwy 1 @ Banff",
            "Latitude": 51.1784,
            "Longitude": -115.5708,
            "Views": [
                {"Url": "https://511.alberta.ca/map/cam-002/e.jpg", "Direction": "E"},
            ],
        },
    ]


# ---------------------------------------------------------------------------
# AER fixtures — static XLSX/TXT reports
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_aer_st1_text():
    """ST1 daily well licence TXT (fixed-width). 2 header rows + 3 data rows."""
    return (
        "Alberta Energy Regulator - Well Licences Issued Daily\n"
        "Run Date: 2026-04-17\n"
        "LIC_NUM  OPERATOR_NAME              WELL_NAME                    FIELD_CODE\n"
        "0467890  TOURMALINE OIL CORP        TOURMALINE GRN-SNKSNG HZ     0123\n"
        "0467891  CANADIAN NATURAL RESOURCES CNRL KIRBY NORTH HZ          0456\n"
        "0467892  CENOVUS ENERGY             CENOVUS FOSTER CREEK HZ      0789\n"
    )


@pytest.fixture
def sample_aer_st3_xlsx_rows():
    """ST3 monthly production XLSX — parsed rows (Gas_current.xlsx format)."""
    return [
        {"period": "2026-01", "product": "Gas", "volume_e3m3": 18523400, "units": "e3m3"},
        {"period": "2026-02", "product": "Gas", "volume_e3m3": 17842100, "units": "e3m3"},
        {"period": "2026-03", "product": "Gas", "volume_e3m3": 19012500, "units": "e3m3"},
        {"period": "2026-04", "product": "Gas", "volume_e3m3": 18450200, "units": "e3m3"},
    ]


@pytest.fixture
def sample_aer_st39_rows():
    """ST39 annual pipeline statistics — 3 sample rows for 2024."""
    return [
        {"substance": "Crude Oil", "length_km": 164_520, "year": 2024},
        {"substance": "Natural Gas", "length_km": 293_810, "year": 2024},
        {"substance": "Salt Water", "length_km": 47_215, "year": 2024},
    ]


# ---------------------------------------------------------------------------
# AQHI fixture — GeoDiscover Alberta air-quality layer
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_aqhi_query():
    """AQHI FeatureServer /query — 2 monitoring stations."""
    return {
        "features": [
            {
                "attributes": {
                    "Station_Name": "Calgary Central",
                    "NO2": 12.3,
                    "O3": 28.7,
                    "PM2_5": 5.1,
                    "AQHI": 3,
                },
                "geometry": {"x": -114.0719, "y": 51.0447},
            },
            {
                "attributes": {
                    "Station_Name": "Edmonton South",
                    "NO2": 18.9,
                    "O3": 22.1,
                    "PM2_5": 8.4,
                    "AQHI": 4,
                },
                "geometry": {"x": -113.4909, "y": 53.5444},
            },
        ],
        "exceededTransferLimit": False,
    }


# ---------------------------------------------------------------------------
# Autouse: bypass cache + rate limiter in every alberta unit test
# ---------------------------------------------------------------------------


async def _fake_cached_fetch(key: str, ttl: int, fetcher):
    """Bypass cache; always call fetcher directly and report was_cached=False."""
    return (await fetcher(), False)


@pytest.fixture(autouse=True)
def patch_cache_and_limiter(monkeypatch):
    """Patch cached_fetch + get_limiter for every alberta unit test."""
    monkeypatch.setattr(
        "mcp_canada.modules.alberta.client.cached_fetch",
        _fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.alberta.client.get_limiter",
        _fake_get_limiter,
    )
