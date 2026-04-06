"""Test fixtures for weather/collections client and tool tests."""

import pytest


# Sample response from BASE_URL/collections?f=json
SAMPLE_COLLECTIONS_RESPONSE = {
    "links": [
        {"href": "https://api.weather.gc.ca/collections?f=json", "rel": "self", "type": "application/json"}
    ],
    "collections": [
        {
            "id": "climate-stations",
            "title": "Climate Stations",
            "description": "Historical climate observation stations across Canada.",
            "extent": {
                "spatial": {"bbox": [[-141.0, 41.7, -52.6, 83.1]], "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
            },
            "links": [
                {"href": "https://api.weather.gc.ca/collections/climate-stations/items", "rel": "items"}
            ],
        },
        {
            "id": "citypageweather-realtime",
            "title": "City Page Weather Realtime",
            "description": "Real-time weather conditions for major Canadian cities.",
            "extent": {
                "spatial": {"bbox": [[-141.0, 41.7, -52.6, 83.1]], "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
            },
            "links": [
                {"href": "https://api.weather.gc.ca/collections/citypageweather-realtime/items", "rel": "items"}
            ],
        },
        {
            "id": "weather-alerts",
            "title": "Weather Alerts",
            "description": "Active weather warnings, watches, and advisories.",
            "extent": {
                "spatial": {"bbox": [[-141.0, 41.7, -52.6, 83.1]], "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
            },
            "links": [
                {"href": "https://api.weather.gc.ca/collections/weather-alerts/items", "rel": "items"}
            ],
        },
    ],
}


# Sample ogc_fetch-compatible feature list for collection items
SAMPLE_COLLECTION_ITEMS = [
    {
        "type": "Feature",
        "id": "station-1",
        "geometry": {
            "type": "Point",
            "coordinates": [-75.7, 45.4],
        },
        "properties": {
            "CLIMATE_IDENTIFIER": "6105976",
            "STATION_NAME": "OTTAWA CDA",
            "PROVINCE_CODE": "ON",
        },
    },
    {
        "type": "Feature",
        "id": "station-2",
        "geometry": {
            "type": "Point",
            "coordinates": [-79.4, 43.7],
        },
        "properties": {
            "CLIMATE_IDENTIFIER": "6158355",
            "STATION_NAME": "TORONTO CITY CENTRE",
            "PROVINCE_CODE": "ON",
        },
    },
]


@pytest.fixture
def sample_collections_response():
    """Simulated /collections?f=json API response."""
    return SAMPLE_COLLECTIONS_RESPONSE


@pytest.fixture
def sample_collection_items():
    """ogc_fetch-compatible feature list for collection items."""
    return SAMPLE_COLLECTION_ITEMS
