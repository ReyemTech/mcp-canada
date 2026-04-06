"""Test fixtures for severe weather client tests."""

import pytest


# ---------------------------------------------------------------------------
# Sample radar precipitation feature (weather:rdpa:10km:24f)
# ---------------------------------------------------------------------------

SAMPLE_RADAR_FEATURE = {
    "type": "Feature",
    "id": "weather-rdpa-10km-24f.1111",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "lat": 45.4,
        "lon": -75.7,
        "APCP_Sfc": 12.5,       # 24h precipitation accumulation (mm)
        "datetime": "2024-03-01T12:00:00Z",
        "grid_row": 100,
        "grid_col": 200,
    },
}

# ---------------------------------------------------------------------------
# Sample citypageweather feature with UV index in forecastGroup
# ---------------------------------------------------------------------------

SAMPLE_CITYPAGE_UV_FEATURE = {
    "type": "Feature",
    "id": "citypageweather-realtime.2222",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "location_en": "Ottawa",
        "location_fr": "Ottawa",
        "province_en": "Ontario",
        "province_fr": "Ontario",
        "lat": 45.4,
        "lon": -75.7,
        "forecastGroup": {
            "forecast": [
                {
                    "period": {"textForecastName": "Today"},
                    "abbreviatedForecast": {
                        "iconCode": {"Code": "01"},
                        "pop": {"value": "0"},
                        "textSummary": "Sunny",
                    },
                    "temperatures": {
                        "temperature": [{"value": "22", "class": "high"}]
                    },
                    "uvIndex": {"Index": "8", "category": "Very High"},
                },
                {
                    "period": {"textForecastName": "Tonight"},
                    "abbreviatedForecast": {
                        "iconCode": {"Code": "30"},
                        "pop": {"value": "0"},
                        "textSummary": "Clear",
                    },
                    "temperatures": {
                        "temperature": [{"value": "12", "class": "low"}]
                    },
                },
            ]
        },
        "currentConditions": {
            "temperature": {"value": "20"},
            "humidity": {"value": "45"},
        },
    },
}

# ---------------------------------------------------------------------------
# Sample citypageweather feature WITHOUT UV index (some forecasts lack it)
# ---------------------------------------------------------------------------

SAMPLE_CITYPAGE_NO_UV_FEATURE = {
    "type": "Feature",
    "id": "citypageweather-realtime.3333",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "location_en": "Ottawa",
        "location_fr": "Ottawa",
        "forecastGroup": {
            "forecast": [
                {
                    "period": {"textForecastName": "Tonight"},
                    "abbreviatedForecast": {
                        "iconCode": {"Code": "30"},
                        "textSummary": "Clear",
                    },
                    "temperatures": {
                        "temperature": [{"value": "12", "class": "low"}]
                    },
                    # No uvIndex field here
                },
            ]
        },
    },
}


@pytest.fixture
def sample_radar_feature():
    """Single weather:rdpa:10km:24f feature with precipitation accumulation."""
    return SAMPLE_RADAR_FEATURE


@pytest.fixture
def sample_citypage_uv_feature():
    """Citypageweather feature with UV index in first forecast period."""
    return SAMPLE_CITYPAGE_UV_FEATURE


@pytest.fixture
def sample_citypage_no_uv_feature():
    """Citypageweather feature without UV index."""
    return SAMPLE_CITYPAGE_NO_UV_FEATURE
