"""Shared fixtures for climate sub-module tests."""

import pytest


@pytest.fixture
def sample_daily_feature():
    """Sample climate-daily OGC feature."""
    return {
        "type": "Feature",
        "id": "climate-daily.1",
        "geometry": {"type": "Point", "coordinates": [-75.717, 45.367]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6158731",
            "LOCAL_DATE": "2024-01-15",
            "MAX_TEMPERATURE": "2.5",
            "MIN_TEMPERATURE": "-8.3",
            "MEAN_TEMPERATURE": "-2.9",
            "TOTAL_PRECIPITATION": "3.2",
            "TOTAL_SNOW": "3.4",
            "SNOW_ON_GROUND": "12.0",
            "HEATING_DEGREE_DAYS": "20.9",
            "COOLING_DEGREE_DAYS": "0.0",
        },
    }


@pytest.fixture
def sample_monthly_feature():
    """Sample climate-monthly OGC feature."""
    return {
        "type": "Feature",
        "id": "climate-monthly.1",
        "geometry": {"type": "Point", "coordinates": [-75.717, 45.367]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6158731",
            "LOCAL_YEAR": "2024",
            "LOCAL_MONTH": "1",
            "MEAN_TEMPERATURE": "-6.4",
            "MAX_TEMPERATURE": "-1.5",
            "MIN_TEMPERATURE": "-11.3",
            "TOTAL_PRECIPITATION": "52.3",
            "TOTAL_SNOW": "45.1",
        },
    }


@pytest.fixture
def sample_normal_feature():
    """Sample climate-normals OGC feature (1981-2010 period)."""
    return {
        "type": "Feature",
        "id": "climate-normals.1",
        "geometry": {"type": "Point", "coordinates": [-75.717, 45.367]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6158731",
            "PERIOD_BEGIN": "1981",
            "PERIOD_END": "2010",
            "MONTH": "1",
            "NORMAL_CODE": "MEAN_TEMPERATURE",
            "NORMAL_VALUE": "-10.5",
        },
    }


@pytest.fixture
def sample_trend_feature():
    """Sample ahccd-trends OGC feature."""
    return {
        "type": "Feature",
        "id": "ahccd-trends.1",
        "geometry": {"type": "Point", "coordinates": [-75.717, 45.367]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6158731",
            "MEASUREMENT_TYPE": "temperature",
            "TREND": "0.018",
            "YEAR_BEGIN": "1940",
            "YEAR_END": "2020",
        },
    }


@pytest.fixture
def sample_collection_metadata():
    """Sample OGC collection metadata for projection/drought endpoints."""
    return {
        "id": "climate:cmip5:projected:annual:anomaly",
        "title": "CMIP5 Climate Projections — Annual Anomaly",
        "description": "Projected annual anomalies from CMIP5 climate models.",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [["2006-01-01", "2100-12-31"]]},
        },
        "links": [
            {"rel": "self", "href": "https://api.weather.gc.ca/collections/climate:cmip5:projected:annual:anomaly"}
        ],
    }
