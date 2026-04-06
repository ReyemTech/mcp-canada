"""Test fixtures for weather/summary client and tool tests."""

import pytest


# Sample ltce-temperature feature (Long-Term Climate Extremes)
SAMPLE_LTCE_TEMP_FEATURE = {
    "type": "Feature",
    "id": "ltce-temp-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "CLIMATE_IDENTIFIER": "6105976",
        "STATION_NAME": "OTTAWA CDA",
        "LOCAL_MONTH": 7,
        "LOCAL_DAY": 15,
        "RECORD_HIGH_MAX_TEMP": 38.9,
        "RECORD_HIGH_MAX_TEMP_YEAR": 1953,
        "RECORD_LOW_MIN_TEMP": -37.8,
        "RECORD_LOW_MIN_TEMP_YEAR": 1994,
        "PROVINCE_CODE": "ON",
    },
}

# Sample ltce-precipitation feature
SAMPLE_LTCE_PRECIP_FEATURE = {
    "type": "Feature",
    "id": "ltce-precip-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "CLIMATE_IDENTIFIER": "6105976",
        "STATION_NAME": "OTTAWA CDA",
        "LOCAL_MONTH": 9,
        "LOCAL_DAY": 21,
        "RECORD_MAX_PRECIP": 63.0,
        "RECORD_MAX_PRECIP_YEAR": 1975,
        "PROVINCE_CODE": "ON",
    },
}

# Sample ltce-snowfall feature
SAMPLE_LTCE_SNOW_FEATURE = {
    "type": "Feature",
    "id": "ltce-snow-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "CLIMATE_IDENTIFIER": "6105976",
        "STATION_NAME": "OTTAWA CDA",
        "LOCAL_MONTH": 11,
        "LOCAL_DAY": 12,
        "RECORD_MAX_SNOWFALL": 42.0,
        "RECORD_MAX_SNOWFALL_YEAR": 1971,
        "PROVINCE_CODE": "ON",
    },
}

# Sample climate-normals feature with frost/growing season info
SAMPLE_CLIMATE_NORMAL_GROWING = {
    "type": "Feature",
    "id": "normal-growing-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "CLIMATE_IDENTIFIER": "6105976",
        "STATION_NAME": "OTTAWA CDA",
        "PROVINCE_CODE": "ON",
        "FROST_FREE_PERIOD": 148,
        "LAST_SPRING_FROST_DATE_30YR": "1981-05-05",
        "FIRST_FALL_FROST_DATE_30YR": "1981-10-01",
    },
}

# Sample climate-daily feature for degree days
SAMPLE_CLIMATE_DAILY_FEATURE = {
    "type": "Feature",
    "id": "daily-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "CLIMATE_IDENTIFIER": "6105976",
        "STATION_NAME": "OTTAWA CDA",
        "LOCAL_DATE": "2025-01-15",
        "MEAN_TEMPERATURE": -5.2,
        "MAX_TEMPERATURE": -1.5,
        "MIN_TEMPERATURE": -10.0,
        "HEATING_DEGREE_DAYS": 23.2,
        "COOLING_DEGREE_DAYS": 0.0,
    },
}


@pytest.fixture
def sample_ltce_temp_feature():
    """Single ltce-temperature GeoJSON feature."""
    return SAMPLE_LTCE_TEMP_FEATURE


@pytest.fixture
def sample_ltce_precip_feature():
    """Single ltce-precipitation GeoJSON feature."""
    return SAMPLE_LTCE_PRECIP_FEATURE


@pytest.fixture
def sample_ltce_snow_feature():
    """Single ltce-snowfall GeoJSON feature."""
    return SAMPLE_LTCE_SNOW_FEATURE


@pytest.fixture
def sample_climate_normal_growing():
    """Climate-normals feature with frost/growing season data."""
    return SAMPLE_CLIMATE_NORMAL_GROWING


@pytest.fixture
def sample_climate_daily_feature():
    """Single climate-daily feature with degree day data."""
    return SAMPLE_CLIMATE_DAILY_FEATURE
