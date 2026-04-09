"""Test fixtures for Toronto Open Data client tests."""

from __future__ import annotations

import csv
import io
import zipfile
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_csv_bytes(headers: list[str], rows: list[list[Any]]) -> bytes:
    """Create CSV bytes for test fixtures."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def _make_zip_with_csv(filename: str, headers: list[str], rows: list[list[Any]]) -> bytes:
    """Create in-memory ZIP containing a single CSV file."""
    csv_content = _make_csv_bytes(headers, rows)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, csv_content)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# GTFS fixtures
# ---------------------------------------------------------------------------

GTFS_STOPS_ROWS = [
    ["1001", "Union Station", "43.6452", "-79.3806", "0"],
    ["1002", "Bloor-Yonge", "43.6709", "-79.3861", "0"],
    ["1003", "Spadina", "43.6672", "-79.4042", "0"],
]

GTFS_ROUTES_ROWS = [
    ["1", "1", "Yonge-University", "1"],
    ["2", "2", "Bloor-Danforth", "1"],
    ["301", "301", "Airport Express", "2"],
]

GTFS_STOPS_ZIP_BYTES = _make_zip_with_csv(
    "stops.txt",
    ["stop_id", "stop_name", "stop_lat", "stop_lon", "location_type"],
    GTFS_STOPS_ROWS,
)

GTFS_ROUTES_ZIP_BYTES = _make_zip_with_csv(
    "routes.txt",
    ["route_id", "route_short_name", "route_long_name", "route_type"],
    GTFS_ROUTES_ROWS,
)


# ---------------------------------------------------------------------------
# Datastore fixtures
# ---------------------------------------------------------------------------

SAMPLE_NEIGHBOURHOOD_RECORDS = [
    {
        "_id": 1,
        "Characteristic": "Total population",
        "Neighbourhood Name": "Bay Street Corridor",
        "City of Toronto": "2731571",
    },
    {
        "_id": 2,
        "Characteristic": "Land area in square kilometres",
        "Neighbourhood Name": "Bay Street Corridor",
        "City of Toronto": "630.2",
    },
]

SAMPLE_RENTSAFE_RECORDS = [
    {
        "_id": 1,
        "WARDNAME": "University-Rosedale",
        "WARDNO": "11",
        "ADDRESS": "123 Bloor St",
        "SCORE": "85",
        "EVALYEAR": "2023",
    },
    {
        "_id": 2,
        "WARDNAME": "Etobicoke Centre",
        "WARDNO": "2",
        "ADDRESS": "456 Kipling Ave",
        "SCORE": "72",
        "EVALYEAR": "2023",
    },
]

SAMPLE_STR_RECORDS = [
    {
        "_id": 1,
        "ward": "University-Rosedale",
        "address": "789 Bay St",
        "status": "Active",
        "operator_registration_number": "STR-2023-001",
    },
    {
        "_id": 2,
        "ward": "Etobicoke Centre",
        "address": "321 Dixon Rd",
        "status": "Cancelled",
        "operator_registration_number": "STR-2023-002",
    },
]


# ---------------------------------------------------------------------------
# CKAN fixtures
# ---------------------------------------------------------------------------

SAMPLE_TOR_DATASET = {
    "id": "ttc-bus-delay-data",
    "name": "ttc-bus-delay-data",
    "title": "TTC Bus Delay Data",
    "notes": "This dataset contains TTC bus delay information.",
    "organization": {"name": "transit-commission", "title": "Toronto Transit Commission"},
    "num_resources": 3,
    "tags": [{"name": "transit"}, {"name": "bus"}, {"name": "delay"}],
    "resources": [
        {
            "id": f"res-{i:03d}",
            "name": f"Resource {i}",
            "format": "CSV",
            "size": 1024 * i,
            "url": f"https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/res-{i}",
            "datastore_active": True,
        }
        for i in range(1, 4)
    ],
    "metadata_created": "2020-01-01T00:00:00.000000",
    "metadata_modified": "2025-08-01T00:00:00.000000",
}

SAMPLE_PACKAGE_SEARCH_RESPONSE = {
    "success": True,
    "result": {
        "count": 500,
        "results": [SAMPLE_TOR_DATASET],
    },
}

SAMPLE_PACKAGE_SHOW_RESPONSE = {
    "success": True,
    "result": SAMPLE_TOR_DATASET,
}

SAMPLE_ORGANIZATION_LIST_RESPONSE = {
    "success": True,
    "result": [
        {
            "id": "org-001",
            "name": "transit-commission",
            "title": "Toronto Transit Commission",
            "description": "TTC manages public transit in Toronto.",
            "package_count": 42,
        },
    ],
}

SAMPLE_RESOURCE_SHOW_RESPONSE = {
    "success": True,
    "result": {
        "id": "res-001",
        "name": "TTC Routes 2024",
        "format": "CSV",
        "size": 2048,
        "url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/res-001",
        "datastore_active": True,
    },
}

SAMPLE_DATASET_COUNT_RESPONSE = {
    "success": True,
    "result": {
        "count": 500,
        "results": [],
    },
}

SAMPLE_DATASTORE_RESPONSE = {
    "success": True,
    "result": {
        "records": SAMPLE_NEIGHBOURHOOD_RECORDS,
        "total": 2,
    },
}

SAMPLE_RENTSAFE_DATASTORE_RESPONSE = {
    "success": True,
    "result": {
        "records": SAMPLE_RENTSAFE_RECORDS,
        "total": 2,
    },
}

SAMPLE_STR_DATASTORE_RESPONSE = {
    "success": True,
    "result": {
        "records": SAMPLE_STR_RECORDS,
        "total": 2,
    },
}

# 311 service requests CSV fixture
SERVICE_311_CSV_ROWS = [
    ["2023-01-15", "Missed Garbage Pickup", "Closed", "Ward 1"],
    ["2023-01-20", "Pothole", "Open", "Ward 2"],
    ["2023-02-01", "Missed Garbage Pickup", "Open", "Ward 1"],
]

SERVICE_311_ZIP_BYTES = _make_zip_with_csv(
    "2023.csv",
    ["Creation Date", "Service Request Type", "Status", "Ward"],
    SERVICE_311_CSV_ROWS,
)

# Dataset details with 311 ZIP resource
SAMPLE_311_DATASET = {
    "id": "311-service-requests-customer-initiated",
    "name": "311-service-requests-customer-initiated",
    "title": "311 Service Requests",
    "notes": "Annual 311 service request data.",
    "organization": {"name": "311", "title": "311 Toronto"},
    "num_resources": 1,
    "tags": [],
    "resources": [
        {
            "id": "res-311-2023",
            "name": "2023.zip",
            "format": "ZIP",
            "size": 5000000,
            "url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/311-2023.zip",
            "datastore_active": False,
        }
    ],
    "metadata_created": "2020-01-01T00:00:00.000000",
    "metadata_modified": "2024-01-01T00:00:00.000000",
}

SAMPLE_311_PACKAGE_SHOW = {
    "success": True,
    "result": SAMPLE_311_DATASET,
}


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


def make_mock_bytes_response(content: bytes) -> MagicMock:
    """Create a mock httpx response returning raw bytes content."""
    mock = MagicMock()
    mock.content = content
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_dataset():
    """Sample Toronto CKAN dataset."""
    return SAMPLE_TOR_DATASET


@pytest.fixture
def sample_package_search():
    """Sample package_search API response."""
    return SAMPLE_PACKAGE_SEARCH_RESPONSE


@pytest.fixture
def sample_package_show():
    """Sample package_show API response."""
    return SAMPLE_PACKAGE_SHOW_RESPONSE


@pytest.fixture
def sample_organization_list():
    """Sample organization_list API response."""
    return SAMPLE_ORGANIZATION_LIST_RESPONSE


@pytest.fixture
def sample_resource_show():
    """Sample resource_show API response."""
    return SAMPLE_RESOURCE_SHOW_RESPONSE


@pytest.fixture
def sample_dataset_count():
    """Sample package_search?rows=0 count response."""
    return SAMPLE_DATASET_COUNT_RESPONSE


@pytest.fixture
def sample_neighbourhood_records():
    """Sample neighbourhood profile datastore records."""
    return SAMPLE_NEIGHBOURHOOD_RECORDS


@pytest.fixture
def gtfs_stops_zip():
    """In-memory ZIP bytes containing stops.txt."""
    return GTFS_STOPS_ZIP_BYTES


@pytest.fixture
def gtfs_routes_zip():
    """In-memory ZIP bytes containing routes.txt."""
    return GTFS_ROUTES_ZIP_BYTES


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
