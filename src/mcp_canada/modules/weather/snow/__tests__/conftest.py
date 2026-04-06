"""Test fixtures for snow weather client tests."""

import pytest


# ---------------------------------------------------------------------------
# Sample SWOB observation with snow depth (swob-realtime)
# Includes multi-sensor fields for Pitfall 4 testing
# ---------------------------------------------------------------------------

SAMPLE_SWOB_SNOW_FEATURE = {
    "type": "Feature",
    "id": "swob-realtime.7890",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.7, 45.4],
    },
    "properties": {
        "stn_nam-value": "OTTAWA INTL A",
        "msc_id-value": "6106000",
        "date_tm-value": "2024-03-01T12:00:00Z",
        "lat-value": 45.4,
        "lon-value": -75.7,
        # Primary snow depth sensor
        "snw_dpth-value": 15.0,
        # Backup sensors for multi-sensor fallback (Pitfall 4)
        "snw_dpth_1-value": 14.5,
        "snw_dpth_2-value": 15.5,
        # Additional weather observations
        "air_temp-value": -5.0,
        "rel_hum-value": 80.0,
    },
}

# ---------------------------------------------------------------------------
# Sample SWOB observation WITHOUT snow depth (no snow sensor at station)
# ---------------------------------------------------------------------------

SAMPLE_SWOB_NO_SNOW_FEATURE = {
    "type": "Feature",
    "id": "swob-realtime.7891",
    "geometry": {
        "type": "Point",
        "coordinates": [-79.4, 43.7],
    },
    "properties": {
        "stn_nam-value": "TORONTO PEARSON INTL A",
        "msc_id-value": "6158350",
        "date_tm-value": "2024-03-01T12:00:00Z",
        "lat-value": 43.7,
        "lon-value": -79.4,
        # No snow depth fields — this station has no snow sensor
        "air_temp-value": 8.0,
        "rel_hum-value": 65.0,
    },
}

# ---------------------------------------------------------------------------
# Sample SWOB with only backup sensors (no primary snw_dpth)
# Tests Pitfall 4: multi-sensor fallback averaging
# ---------------------------------------------------------------------------

SAMPLE_SWOB_BACKUP_ONLY_FEATURE = {
    "type": "Feature",
    "id": "swob-realtime.7892",
    "geometry": {
        "type": "Point",
        "coordinates": [-80.0, 46.0],
    },
    "properties": {
        "stn_nam-value": "SUDBURY AIRPORT",
        "msc_id-value": "6068150",
        "date_tm-value": "2024-03-01T12:00:00Z",
        "lat-value": 46.0,
        "lon-value": -80.0,
        # Primary sensor missing — use backup sensors
        # snw_dpth-value is absent
        "snw_dpth_1-value": 20.0,
        "snw_dpth_2-value": 22.0,
        "air_temp-value": -10.0,
    },
}


@pytest.fixture
def sample_swob_snow_feature():
    """SWOB observation with primary and backup snow depth sensors."""
    return SAMPLE_SWOB_SNOW_FEATURE


@pytest.fixture
def sample_swob_no_snow_feature():
    """SWOB observation with no snow depth sensors."""
    return SAMPLE_SWOB_NO_SNOW_FEATURE


@pytest.fixture
def sample_swob_backup_only_feature():
    """SWOB observation with only backup snow sensors (no primary)."""
    return SAMPLE_SWOB_BACKUP_ONLY_FEATURE
