"""Test fixtures for AQHI client and tool tests."""

import pytest


# Sample aqhi-observations-realtime feature
SAMPLE_AQHI_OBS_FEATURE = {
    "type": "Feature",
    "id": "aqhi-obs-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "location_id": "ON106",
        "location_name_en": "Ottawa",
        "location_name_fr": "Ottawa",
        "aqhi": 3.0,
        "observation_datetime": "2026-04-05T10:00:00Z",
        "community_en": "Ottawa",
        "community_fr": "Ottawa",
    },
}

# Sample aqhi-forecasts-realtime feature
SAMPLE_AQHI_FORECAST_FEATURE = {
    "type": "Feature",
    "id": "aqhi-forecast-1",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "location_id": "ON106",
        "location_name_en": "Ottawa",
        "location_name_fr": "Ottawa",
        "aqhi": 2.0,
        "forecast_datetime": "2026-04-05T12:00:00Z",
        "period": "afternoon",
        "community_en": "Ottawa",
        "community_fr": "Ottawa",
    },
}


@pytest.fixture
def sample_aqhi_obs_feature():
    """Single aqhi-observations-realtime feature."""
    return SAMPLE_AQHI_OBS_FEATURE


@pytest.fixture
def sample_aqhi_forecast_feature():
    """Single aqhi-forecasts-realtime feature."""
    return SAMPLE_AQHI_FORECAST_FEATURE
