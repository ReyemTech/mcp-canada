"""Shared fixtures for Saskatchewan module unit tests.

Provides ArcGIS Hub JSON fixtures and FeatureServer response fixtures for all
response shapes Plans 02-05 reference, plus autouse cache+limiter patch.

Pattern: mirrors Manitoba Phase 18 conftest.py with Saskatchewan-specific fixtures.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# ArcGIS Hub Search response fixtures
# ---------------------------------------------------------------------------

HUB_SEARCH_RAW: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 181,
    "numberReturned": 2,
    "features": [
        {
            "id": "abc123sk",
            "type": "Feature",
            "geometry": None,
            "properties": {
                "title": "Provincial Estimated Crop Yields",
                "type": "Feature Service",
                "snippet": "Saskatchewan estimated crop yields by region (16 crop types).",
                "url": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer",
                "owner": "Saskatchewan_Government",
                "tags": ["agriculture", "crops", "Saskatchewan"],
                "categories": ["/Categories/Agriculture"],
                "modified": 1700000000000,
                "numViews": 3000,
                "access": "public",
                "source": "Government of Saskatchewan",
            },
        },
        {
            "id": "def456sk",
            "type": "Feature",
            "geometry": None,
            "properties": {
                "title": "Hourly Ambient Air Quality",
                "type": "Feature Service",
                "snippet": "Live hourly ambient air quality readings across Saskatchewan communities.",
                "url": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Hourly_Ambient_Air_Quality/FeatureServer",
                "owner": "Saskatchewan_Government",
                "tags": ["air quality", "environment", "Saskatchewan"],
                "categories": ["/Categories/Environment"],
                "modified": 1750000000000,
                "numViews": 8500,
                "access": "public",
                "source": "Government of Saskatchewan",
            },
        },
    ],
    "links": [],
    "timestamp": "2026-06-15T12:00:00.000Z",
}

HUB_SEARCH_EMPTY: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 0,
    "numberReturned": 0,
    "features": [],
    "links": [],
    "timestamp": "2026-06-15T12:00:00.000Z",
}

HUB_ITEM_DETAIL: dict[str, Any] = {
    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "type": "Feature",
    "geometry": None,
    "properties": {
        "title": "Provincial Estimated Crop Yields Province Summary",
        "type": "Feature Service",
        "snippet": "Saskatchewan estimated crop yields by region for 16 crop types.",
        "description": "Annual crop yield estimates for Saskatchewan by crop reporting region.",
        "url": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer",
        "owner": "Saskatchewan_Government",
        "tags": ["agriculture", "crops", "yields", "Saskatchewan"],
        "categories": ["/Categories/Agriculture"],
        "modified": 1700000000000,
        "numViews": 3000,
        "access": "public",
        "licenseInfo": "<a href='https://www.saskatchewan.ca/government/about-the-government-of-saskatchewan/open-government'>Saskatchewan Open Government Licence</a>",
        "source": "Government of Saskatchewan",
    },
}


# ---------------------------------------------------------------------------
# ArcGIS FeatureServer query result fixtures
# (format: tuple[list[dict], bool] where bool = truncated)
# ---------------------------------------------------------------------------

# Agriculture fixtures
SAMPLE_ARCGIS_CROP_YIELDS: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Region": "Provincial",
            "HRSW": 43.0,
            "Durum": 35.0,
            "Oat": 92.0,
            "Barley": 70.0,
            "Canola": 34.0,
            "Mustard": 22.0,
            "Soybean": 29.0,
            "Pea": 42.0,
            "Lentil": 1369.0,
            "Chickpea": 1200.0,
            "Canary_seed": 820.0,
            "Flax": 19.0,
            "Winter_wheat": 51.0,
            "Fall_rye": 39.0,
            "Other_wheat_": 41.0,
        },
        {
            "OBJECTID": 2,
            "Region": "Southeast",
            "HRSW": 40.0,
            "Durum": 33.0,
            "Oat": 88.0,
            "Barley": 67.0,
            "Canola": 31.0,
            "Mustard": 19.0,
            "Soybean": 27.0,
            "Pea": 39.0,
            "Lentil": 1300.0,
            "Chickpea": 1100.0,
            "Canary_seed": 790.0,
            "Flax": 17.0,
            "Winter_wheat": 49.0,
            "Fall_rye": 36.0,
            "Other_wheat_": 38.0,
        },
    ],
    False,
)

SAMPLE_ARCGIS_GRAIN_ELEVATORS: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Station": "Regina",
            "PR": "SK",
            "Railway": "CN",
            "Licensee": "Richardson International",
            "Elevator_type": "Primary",
            "Capacity_tonne": 42000.0,
        },
        {
            "OBJECTID": 2,
            "Station": "Saskatoon",
            "PR": "SK",
            "Railway": "CN",
            "Licensee": "Parrish & Heimbecker",
            "Elevator_type": "Process",
            "Capacity_tonne": 35000.0,
        },
    ],
    False,
)

# Energy/Mining fixtures
SAMPLE_ARCGIS_MINERAL_MINES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Commodity": "Potash",
            "Name": "K+S Bethune",
            "Status": "Operating",
            "Mine_Type": "Solution",
            "Company": "K+S Potash Canada GP",
            "Mine_Site": "Bethune, SK",
            "Regulation": "Provincial",
            "DateOpened": "2017",
            "Website": "https://www.kpluss.com/en-us/",
        },
        {
            "OBJECTID": 2,
            "Commodity": "Potash",
            "Name": "Mosaic Esterhazy K1/K2",
            "Status": "Operating",
            "Mine_Type": "Underground",
            "Company": "The Mosaic Company",
            "Mine_Site": "Esterhazy, SK",
            "Regulation": "Provincial",
            "DateOpened": "1962",
            "Website": "https://www.mosaicco.com/",
        },
    ],
    False,
)

# Environment/Wildfire fixtures
SAMPLE_ARCGIS_AIR_QUALITY: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "COMMUNITY": "Regina",
            "STATIONID": "SK_REGINA_01",
            "PM2_5": 7.2,
            "NO2": 12.5,
            "O3": 31.0,
            "PM10": 14.0,
            "SO2": 2.1,
            "CO": 0.4,
            "H2S": 0.8,
            "AQHI": "https://weather.gc.ca/airquality/pages/sk-1_metric_e.html",
            "DATETIME": "2026-06-15T14:00:00",
        },
        {
            "OBJECTID": 2,
            "COMMUNITY": "Saskatoon",
            "STATIONID": "SK_SASKATOON_01",
            "PM2_5": 5.8,
            "NO2": 9.3,
            "O3": 28.5,
            "PM10": 11.0,
            "SO2": 1.5,
            "CO": 0.3,
            "H2S": 0.5,
            "AQHI": "https://weather.gc.ca/airquality/pages/sk-2_metric_e.html",
            "DATETIME": "2026-06-15T14:00:00",
        },
    ],
    False,
)

# CRITICAL: empty fire bans is CORRECT when no bans are active (off-season) — NOT an error
SAMPLE_ARCGIS_FIRE_BANS_ACTIVE: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "UMTYPE": "Urban Municipality",
            "Municipali": "Arborfield",
            "Fire_Depar": "Arborfield Fire Department",
            "Start_Date": "20260611",
            "Contact_Nu": "306-555-0100",
            "Type": "Ban",
            "Comment": "Level 1 Fire Ban — All open burning prohibited",
        },
        {
            "OBJECTID": 2,
            "UMTYPE": "Urban Municipality",
            "Municipali": "Canora",
            "Fire_Depar": "Canora Fire Department",
            "Start_Date": "20260610",
            "Contact_Nu": "306-555-0200",
            "Type": "Restriction",
            "Comment": "Level 2 Restriction — Campfires allowed with permit only",
        },
    ],
    False,
)

SAMPLE_ARCGIS_FIRE_BANS_EMPTY: tuple[list[dict], bool] = ([], False)
# ^^^ This is the normal off-season state — NO ACTIVE BANS is VALID, NOT an error.

SAMPLE_ARCGIS_WILDFIRES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "YEAR": 2017,
            "FIRENAME": "PORCUPINE LAKE FIRE",
            "CAUSE1": "Lightning",
            "HECTARES": 12450.5,
            "STATUS": "Out",
            "STARTDATE": "2017-07-15",
            "OUTDATE": "2017-08-03",
            "TYPE": "Crown",
        },
        {
            "OBJECTID": 2,
            "YEAR": 2015,
            "FIRENAME": "WEYAKWIN LAKE FIRE",
            "CAUSE1": "Human",
            "HECTARES": 3200.0,
            "STATUS": "Out",
            "STARTDATE": "2015-06-20",
            "OUTDATE": "2015-07-01",
            "TYPE": "Ground",
        },
    ],
    False,
)

# Water/WSA fixtures
SAMPLE_ARCGIS_WSA_STATIONS: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Station_Number": "05MB006",
            "Station_Name": "ASSINIBOINE RIVER AT ESTERHAZY",
            "Province": "SK",
            "Latitude": 50.64,
            "Longitude": -102.09,
            "Major_Basin": "Assiniboine River",
            "Station_Type": "Water Level and Discharge",
            "Station_Class": "Primary",
            "Operated_By": "Water Survey of Canada - SK",
            "HyperLink_Graph": "https://www.wsask.ca/hydrographs/05MB006-hrly.html",
        },
        {
            "OBJECTID": 2,
            "Station_Number": "05JG006",
            "Station_Name": "NORTH SASKATCHEWAN RIVER AT PRINCE ALBERT",
            "Province": "SK",
            "Latitude": 53.20,
            "Longitude": -105.76,
            "Major_Basin": "North Saskatchewan River",
            "Station_Type": "Water Level and Discharge",
            "Station_Class": "Primary",
            "Operated_By": "Water Survey of Canada - SK",
            "HyperLink_Graph": "https://www.wsask.ca/hydrographs/05JG006-hrly.html",
        },
    ],
    False,
)

SAMPLE_ARCGIS_WSA_RESERVOIRS: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Reservoir_Name": "ADMIRAL RESERVOIR",
            "Dam_Name": "ADMIRAL DAM",
            "Imagery_Date": "2024-05-15",
            "Water_Level_MASL": 671.3,
        },
        {
            "OBJECTID": 2,
            "Reservoir_Name": "ANGLIN LAKE RESERVOIR",
            "Dam_Name": "ANGLIN LAKE DAM",
            "Imagery_Date": "2024-05-15",
            "Water_Level_MASL": 516.8,
        },
    ],
    False,
)


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
    """Patch cached_fetch to bypass cache and get_limiter to return a no-op mock."""
    monkeypatch.setattr(
        "mcp_canada.modules.saskatchewan.client.cached_fetch",
        fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.saskatchewan.client.get_limiter",
        _fake_get_limiter,
    )
    # Also patch module-level limiters created at import time
    monkeypatch.setattr(
        "mcp_canada.modules.saskatchewan.client._hub_limiter",
        mock_limiter,
    )
    monkeypatch.setattr(
        "mcp_canada.modules.saskatchewan.client._wsa_limiter",
        mock_limiter,
    )
    monkeypatch.setattr(
        "mcp_canada.modules.saskatchewan.client._spsa_limiter",
        mock_limiter,
    )
