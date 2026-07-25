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
    """Sample ahccd-trends OGC feature — REAL property names, captured 2026-07-25.

    This fixture previously used SCREAMING_CASE keys (CLIMATE_IDENTIFIER,
    MEASUREMENT_TYPE, TREND) that ahccd-trends does not publish. Because the
    client read the same wrong keys, the tests agreed with the code and the
    defect shipped: every filtered call matched zero records. ahccd-trends uses
    bilingual double-underscore names, unlike the SCREAMING_CASE of
    climate-daily and climate-normals.

    Note the collection carries precipitation measures only — "rain", "snow",
    "total_precip". There is no temperature series despite the AHCCD name.
    """
    return {
        "type": "Feature",
        "id": "ahccd-trends.1",
        "geometry": {"type": "Point", "coordinates": [-121.76, 49.24]},
        "properties": {
            "identifier__identifiant": "1100120.Jan.total_precip",
            "station_id__id_station": "1100120",
            "station_name__nom_station": "AGASSIZ_CDA",
            "joined__rejoint": 0,
            "elevation__elevation": 15,
            "period__periode": "Jan",
            "province__province": "BC",
            "year_range__annees": "1890-2017",
            "measurement_type__type_mesure": "total_precip",
            "trend_value__valeur_tendance": 74.81,
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
