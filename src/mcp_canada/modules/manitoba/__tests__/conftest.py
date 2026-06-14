"""Shared fixtures for Manitoba module unit tests.

Provides ArcGIS Hub JSON fixtures for all response shapes Plans 02-06 reference,
plus autouse cache+limiter patch (copy of York Region pattern).
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
    "numberMatched": 82,
    "numberReturned": 2,
    "features": [
        {
            "id": "abc123mb",
            "type": "Feature",
            "geometry": None,
            "properties": {
                "title": "Manitoba_Parks",
                "type": "Feature Service",
                "snippet": "Manitoba provincial parks and protected areas (93 parks).",
                "url": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer",
                "owner": "Manitoba_Government",
                "tags": ["parks", "Manitoba", "environment"],
                "categories": ["/Categories/Environment"],
                "modified": 1700000000000,
                "numViews": 5000,
                "access": "public",
                "source": "Government of Manitoba",
            },
        },
        {
            "id": "def456mb",
            "type": "Feature",
            "geometry": None,
            "properties": {
                "title": "Overland Flood Alerts",
                "type": "Feature Service",
                "snippet": "Current overland flood watch/warning polygons for Manitoba.",
                "url": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Overland_Flood_Alerts/FeatureServer",
                "owner": "Manitoba_Government",
                "tags": ["flood", "Manitoba", "hydrology"],
                "categories": ["/Categories/Disaster Response"],
                "modified": 1750000000000,
                "numViews": 12000,
                "access": "public",
                "source": "Government of Manitoba",
            },
        },
    ],
    "links": [],
    "timestamp": "2026-06-14T04:00:00.000Z",
}

HUB_SEARCH_EMPTY: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 0,
    "numberReturned": 0,
    "features": [],
    "links": [],
    "timestamp": "2026-06-14T04:00:00.000Z",
}

HUB_ITEM_DETAIL: dict[str, Any] = {
    "id": "b71a8d37a75e4215ba13b8695261a403",
    "type": "Feature",
    "geometry": None,
    "properties": {
        "title": "MB_Cattle_Prices_Current_year",
        "type": "Feature Service",
        "snippet": "Current year weekly cattle market prices from Manitoba Agriculture.",
        "description": "Weekly Manitoba cattle market prices by auction and grade.",
        "url": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MB_Cattle_Prices_Current_year/FeatureServer",
        "owner": "Manitoba_Government",
        "tags": ["livestock", "cattle", "agriculture", "Manitoba"],
        "categories": ["/Categories/Agriculture"],
        "modified": 1749000000000,
        "numViews": 8000,
        "access": "public",
        "licenseInfo": "<a href='https://www.gov.mb.ca/legal/copyright.html'>Manitoba Open Data Licence</a>",
        "source": "Government of Manitoba",
    },
}


# ---------------------------------------------------------------------------
# ArcGIS FeatureServer query result fixtures
# (format: tuple[list[dict], bool] where bool = truncated)
# ---------------------------------------------------------------------------

SAMPLE_PARKS_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "NAME_E": "Hecla/Grindstone Provincial Park",
            "NOM_F": "Parc provincial de Hecla/Grindstone",
            "BIOME": "Boreal",
            "O_AREA": 108500.0,
            "TYPE_E": "Provincial",
            "TYPE_F": "Provincial",
            "STATUS_E": "Established",
            "PROTDATE": 1009843200000,
            "PRK_CLSS": "Provincial Park",
            "URL": "https://www.gov.mb.ca/sd/parks/",
        },
        {
            "OBJECTID": 2,
            "NAME_E": "Riding Mountain National Park",
            "NOM_F": "Parc national du Mont-Riding",
            "BIOME": "Boreal/Prairie",
            "O_AREA": 297000.0,
            "TYPE_E": "Wilderness",
            "TYPE_F": "Sauvage",
            "STATUS_E": "Established",
            "PROTDATE": 978307200000,
            "PRK_CLSS": "National Park",
            "URL": "https://www.pc.gc.ca/en/pn-np/mb/riding",
        },
    ],
    False,
)

# CRITICAL: empty flood alerts is CORRECT when no flooding active — NOT an error
SAMPLE_FLOOD_ALERTS_EMPTY: tuple[list[dict], bool] = ([], False)

SAMPLE_FLOOD_ALERTS_ACTIVE: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Type_EN": "Warning",
            "Type_FR": "Avertissement",
            "Start_Date": 1749000000000,
            "End_Date": 1749600000000,
            "Shape__Area": 12345.67,
        },
        {
            "OBJECTID": 2,
            "Type_EN": "Watch",
            "Type_FR": "Veille",
            "Start_Date": 1749000000000,
            "End_Date": None,
            "Shape__Area": 5678.90,
        },
    ],
    False,
)

SAMPLE_WATERWAYS_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "F_TYPE": "Floodway",
            "Name": "Red River Floodway",
            "Watershed": "Red River",
            "WCW": "WCW-001",
            "LengthKM": 47.0,
        },
        {
            "OBJECTID": 2,
            "F_TYPE": "Dike",
            "Name": "Winnipeg Ring Dike",
            "Watershed": "Red River",
            "WCW": "WCW-002",
            "LengthKM": 32.5,
        },
    ],
    False,
)

SAMPLE_DROUGHT_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "DM": "D2",
            "OBS_DATE": 1748995200000,
            "SOURCE": "NOAA/NDMC/USDA",
        },
        {
            "OBJECTID": 2,
            "DM": "D1",
            "OBS_DATE": 1748995200000,
            "SOURCE": "NOAA/NDMC/USDA",
        },
    ],
    False,
)

SAMPLE_AG_WEATHER_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "StnName": "Brandon",
            "LatDD": 49.87,
            "LongDD": -99.95,
            "Elevation": 409.0,
            "AgRegion": "Southwest",
            "URL": "https://agrimaps.gov.mb.ca/stations/brandon",
        },
        {
            "OBJECTID": 2,
            "StnName": "Winnipeg Airport",
            "LatDD": 49.91,
            "LongDD": -97.24,
            "Elevation": 239.0,
            "AgRegion": "Central",
            "URL": "https://agrimaps.gov.mb.ca/stations/winnipeg",
        },
    ],
    False,
)

SAMPLE_LIVESTOCK_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "week": "2026-06-07",
            "Auction": "Winnipeg",
            "Parameter": "D1 Steers (850-1000 lbs)",
            "Measure": "$/cwt",
            "Value": 185.5,
        },
        {
            "OBJECTID": 2,
            "week": "2026-06-07",
            "Auction": "Brandon",
            "Parameter": "D1 Steers (850-1000 lbs)",
            "Measure": "$/cwt",
            "Value": 183.0,
        },
    ],
    False,
)

SAMPLE_CROP_REGIONS_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "REGION": "Central",
            "RÉGION": "Centre",
        },
        {
            "OBJECTID": 2,
            "REGION": "Southwest",
            "RÉGION": "Sud-ouest",
        },
    ],
    False,
)

SAMPLE_WAIT_TIMES_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Year": 2021,
            "IndicatorDataArea": "Cardiac surgery",
            "Average_Wait": 144,
        },
        {
            "OBJECTID": 2,
            "Year": 2020,
            "IndicatorDataArea": "Cardiac surgery",
            "Average_Wait": 130,
        },
        {
            "OBJECTID": 3,
            "Year": 2019,
            "IndicatorDataArea": "Cardiac surgery",
            "Average_Wait": 60,
        },
    ],
    False,
)

SAMPLE_FISHERIES_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "ID": "WB-001",
            "Name": "Lake Winnipeg",
            "SurfaceArea": 24514.0,
            "AvgDepth": 12.0,
            "SecchiDepth": 1.5,
            "FishingDivision": "Division 1",
            "Species": "Walleye, Goldeye, Sauger",
            "Regulations": "Walleye: 6/day possession limit",
            "BoatLaunch": "Available at multiple locations",
        },
        {
            "OBJECTID": 2,
            "ID": "WB-002",
            "Name": "Lake Manitoba",
            "SurfaceArea": 4706.0,
            "AvgDepth": 3.7,
            "SecchiDepth": 0.8,
            "FishingDivision": "Division 2",
            "Species": "Walleye, Yellow Perch",
            "Regulations": "Walleye: 4/day possession limit",
            "BoatLaunch": "Available at Elm Point",
        },
    ],
    False,
)

SAMPLE_FORESTS_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Name": "Porcupine Hills Forest",
            "area_ha": 245000.0,
        },
        {
            "OBJECTID": 2,
            "Name": "Duck Mountain Forest",
            "area_ha": 189000.0,
        },
    ],
    False,
)

SAMPLE_RIVER_STATIONS_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "id": "101",
            "stationId": "05OB004",
            "stationName": "Red River at Emerson",
            "latitude": 49.0,
            "longitude": -97.21,
            "alert": "No Flooding",
            "measuredFlow": 1234.5,
            "measuredLevel": 7.21,
            "floodStage": 10.5,
            "warningTriggerLevel": 8.5,
            "province": "MB",
            "measurementDate": "2026-06-13 12:00:00",
            "waterLevel": 7.21,
            "discharge": 1234.5,
            "wscRealTimeData": "https://wateroffice.ec.gc.ca/report/real_time_e.html?stn=05OB004",
        },
        {
            "id": "102",
            "stationId": "05PF005",
            "stationName": "Assiniboine River at Brandon",
            "latitude": 49.85,
            "longitude": -99.95,
            "alert": "High Water Advisory",
            "measuredFlow": 876.0,
            "measuredLevel": 9.5,
            "floodStage": 12.0,
            "warningTriggerLevel": 10.0,
            "province": "MB",
            "measurementDate": "2026-06-13 12:00:00",
            "waterLevel": 9.5,
            "discharge": 876.0,
            "wscRealTimeData": "https://wateroffice.ec.gc.ca/report/real_time_e.html?stn=05PF005",
        },
    ],
    False,
)

SAMPLE_HEALTH_FACILITIES_FEATURES: tuple[list[dict], bool] = (
    [
        {
            "OBJECTID": 1,
            "Community_Name": "Selkirk",
            "Facility_Name": "Selkirk & District General Hospital",
            "Lat": 50.14,
            "Long": -96.87,
            "Emergency_Department_Availabili": "Yes",
            "Percentage_of_Time_Open__2015_": "100%",
            "Nearest_Alternate_Emergency_Dep": "Health Sciences Centre, Winnipeg",
            "Acute_Care_Availability": "Yes",
            "Acute_Care_Number_of_Beds": 32,
        },
        {
            "OBJECTID": 2,
            "Community_Name": "Portage la Prairie",
            "Facility_Name": "Portage District General Hospital",
            "Lat": 49.97,
            "Long": -98.29,
            "Emergency_Department_Availabili": "Yes",
            "Percentage_of_Time_Open__2015_": "100%",
            "Nearest_Alternate_Emergency_Dep": "Brandon Regional Health Centre",
            "Acute_Care_Availability": "Yes",
            "Acute_Care_Number_of_Beds": 45,
        },
    ],
    False,
)

# ---------------------------------------------------------------------------
# Manitoba 511 fixtures (raw JSON lists)
# ---------------------------------------------------------------------------

SAMPLE_511_EVENTS: list[dict] = [
    {
        "Id": "EVT-001",
        "RoadwayName": "Trans-Canada Highway 1",
        "EventType": "Construction",
        "IsFullClosure": False,
        "Latitude": 49.8951,
        "Longitude": -97.1384,
        "Description": "Single lane closures, 08:00-16:00 weekdays",
        "LastUpdated": "2026-06-13T10:00:00Z",
    },
    {
        "Id": "EVT-002",
        "RoadwayName": "PTH 75",
        "EventType": "Road Closure",
        "IsFullClosure": True,
        "Latitude": 49.35,
        "Longitude": -97.06,
        "Description": "Emergency closure due to flooding",
        "LastUpdated": "2026-06-13T06:00:00Z",
    },
]

SAMPLE_511_WINTER_ROADS: list[dict] = [
    {
        "Id": "WR-001",
        "AreaName": "Northern",
        "RoadwayName": "Winter Road to Island Lake",
        "Primary Condition": "Good",
        "Secondary Conditions": "",
        "Visibility": "Good",
        "EncodedPolyline": "_p~iF~ps|U_ulLnnqC_mqNvxq`@",
        "LastUpdated": "2026-01-15T08:00:00Z",
    },
    {
        "Id": "WR-002",
        "AreaName": "Northern",
        "RoadwayName": "Winter Road to Berens River",
        "Primary Condition": "Fair",
        "Secondary Conditions": "Drifting snow",
        "Visibility": "Fair",
        "EncodedPolyline": "gceoFmxscU_ulLnnqC",
        "LastUpdated": "2026-01-15T08:00:00Z",
    },
]

SAMPLE_511_CAMERAS: list[dict] = [
    {
        "Id": "CAM-001",
        "Location": "Perimeter Highway & Main Street",
        "Latitude": 49.92,
        "Longitude": -97.24,
        "Views": [
            {"Name": "North", "Url": "https://www.manitoba511.ca/cameras/001_N.jpg"},
            {"Name": "South", "Url": "https://www.manitoba511.ca/cameras/001_S.jpg"},
        ],
    },
    {
        "Id": "CAM-002",
        "Location": "Trans-Canada Highway 1 & PTH 16",
        "Latitude": 49.87,
        "Longitude": -97.22,
        "Views": [
            {"Name": "East", "Url": "https://www.manitoba511.ca/cameras/002_E.jpg"},
        ],
    },
]


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
        "mcp_canada.modules.manitoba.client.cached_fetch",
        fake_cached_fetch,
    )

    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock()

    def _fake_get_limiter(source, rate):
        return mock_limiter

    monkeypatch.setattr(
        "mcp_canada.modules.manitoba.client.get_limiter",
        _fake_get_limiter,
    )
    # Also patch module-level limiters created at import time
    monkeypatch.setattr(
        "mcp_canada.modules.manitoba.client._hub_limiter",
        mock_limiter,
    )
    monkeypatch.setattr(
        "mcp_canada.modules.manitoba.client._511_limiter",
        mock_limiter,
    )
