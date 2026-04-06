"""Test fixtures for hydrometric client and tool tests."""

import pytest


# Sample hydrometric-realtime feature
SAMPLE_HYDRO_REALTIME_FEATURE = {
    "type": "Feature",
    "id": "hydro-realtime-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-76.4, 45.3],
    },
    "properties": {
        "STATION_NUMBER": "02LA004",
        "STATION_NAME": "RIDEAU RIVER AT OTTAWA",
        "LEVEL": 72.45,
        "DISCHARGE": 115.0,
        "DATETIME": "2026-04-05T10:00:00Z",
        "PROVINCE_TERR": "ON",
        "STATUS_EN": "Active",
        "STATUS_FR": "Actif",
    },
}

# Sample hydrometric-stations feature
SAMPLE_HYDRO_STATION_FEATURE = {
    "type": "Feature",
    "id": "hydro-station-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-76.4, 45.3],
    },
    "properties": {
        "STATION_NUMBER": "02LA004",
        "STATION_NAME": "RIDEAU RIVER AT OTTAWA",
        "PROVINCE_TERR": "ON",
        "STATUS_EN": "Active",
        "STATUS_FR": "Actif",
        "REAL_TIME": "Y",
        "DRAINAGE_AREA_GROSS": 3828.0,
        "CONTRIBUTOR_EN": "Water Survey of Canada",
    },
}

# Sample hydrometric-annual-peaks feature
SAMPLE_HYDRO_PEAK_FEATURE = {
    "type": "Feature",
    "id": "hydro-peak-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-76.4, 45.3],
    },
    "properties": {
        "STATION_NUMBER": "02LA004",
        "STATION_NAME": "RIDEAU RIVER AT OTTAWA",
        "PEAK": 5.12,
        "LEVEL": 78.34,
        "DISCHARGE": 488.0,
        "PEAK_DATETIME": "2019-04-26T00:00:00Z",
        "PEAK_CODE": "MAX",
        "SYMBOL": "E",
    },
}

# Sample hydrometric-daily-mean feature
SAMPLE_HYDRO_DAILY_FEATURE = {
    "type": "Feature",
    "id": "hydro-daily-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-76.4, 45.3],
    },
    "properties": {
        "STATION_NUMBER": "02LA004",
        "STATION_NAME": "RIDEAU RIVER AT OTTAWA",
        "LEVEL": 72.10,
        "DISCHARGE": 112.0,
        "DATE": "2026-04-04",
    },
}


@pytest.fixture
def sample_hydro_realtime_feature():
    """Single hydrometric-realtime feature."""
    return SAMPLE_HYDRO_REALTIME_FEATURE


@pytest.fixture
def sample_hydro_station_feature():
    """Single hydrometric-stations feature."""
    return SAMPLE_HYDRO_STATION_FEATURE


@pytest.fixture
def sample_hydro_peak_feature():
    """Single hydrometric-annual-peaks feature with historical max values."""
    return SAMPLE_HYDRO_PEAK_FEATURE


@pytest.fixture
def sample_hydro_daily_feature():
    """Single hydrometric-daily-mean feature."""
    return SAMPLE_HYDRO_DAILY_FEATURE
