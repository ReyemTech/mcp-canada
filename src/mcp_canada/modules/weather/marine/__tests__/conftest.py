"""Test fixtures for marine weather client tests."""

import pytest


# ---------------------------------------------------------------------------
# Sample marine weather feature (marineweather-realtime)
# Models nested structure from Pitfall 6 — must be flattened by client
# ---------------------------------------------------------------------------

SAMPLE_MARINE_FEATURE = {
    "type": "Feature",
    "id": "marineweather-realtime.1234",
    "geometry": {
        "type": "Point",
        "coordinates": [-63.5, 44.8],
    },
    "properties": {
        "area_en": "Northumberland Strait",
        "area_fr": "Détroit de Northumberland",
        "regularForecast": {
            "en": [
                {
                    "period": "Tonight",
                    "forecast": "Northwest 15 to 20 knots. Waves 0.5 to 1 metre.",
                }
            ],
            "fr": [
                {
                    "period": "Ce soir",
                    "forecast": "Nord-ouest 15 à 20 noeuds. Vagues 0,5 à 1 mètre.",
                }
            ],
        },
        "waveForecast": {
            "en": "Waves 0.5 to 1 metre.",
            "fr": "Vagues 0,5 à 1 mètre.",
        },
        "warnings": [
            {
                "event": "SMALL CRAFT WARNING",
                "en": "Small Craft Warning in effect.",
                "fr": "Avertissement pour petits bâtiments en vigueur.",
            }
        ],
        "issued_utc": "2024-03-01T12:00:00Z",
    },
}

# ---------------------------------------------------------------------------
# Sample hurricane feature (hurricanes-track-realtime)
# ---------------------------------------------------------------------------

SAMPLE_HURRICANE_FEATURE = {
    "type": "Feature",
    "id": "hurricanes-track-realtime.5678",
    "geometry": {
        "type": "Point",
        "coordinates": [-75.0, 25.0],
    },
    "properties": {
        "name": "HURRICANE ALPHA",
        "advisory": "2024-09-15T00:00:00Z",
        "storm_category": "Category 3",
        "max_wind_kt": 110,
        "min_pressure_mb": 955,
        "forecast_track": "NNW",
    },
}

# ---------------------------------------------------------------------------
# Sample empty response — used for off-season testing (Pitfall 7)
# ---------------------------------------------------------------------------

SAMPLE_EMPTY_RESPONSE: list[dict] = []

# ---------------------------------------------------------------------------
# Sample thunderstorm outlook feature (thunderstorm_outlook)
# ---------------------------------------------------------------------------

SAMPLE_THUNDERSTORM_FEATURE = {
    "type": "Feature",
    "id": "thunderstorm_outlook.9012",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-80.0, 43.0],
                [-75.0, 43.0],
                [-75.0, 46.0],
                [-80.0, 46.0],
                [-80.0, 43.0],
            ]
        ],
    },
    "properties": {
        "region_en": "Southern Ontario",
        "region_fr": "Sud de l'Ontario",
        "risk_en": "High",
        "risk_fr": "Élevé",
        "valid_from": "2024-07-01T18:00:00Z",
        "valid_to": "2024-07-02T06:00:00Z",
        "outlook_en": "Severe thunderstorms possible.",
        "outlook_fr": "Orages violents possibles.",
    },
}


@pytest.fixture
def sample_marine_feature():
    """Single marineweather-realtime feature with nested bilingual structure."""
    return SAMPLE_MARINE_FEATURE


@pytest.fixture
def sample_hurricane_feature():
    """Single hurricanes-track-realtime feature."""
    return SAMPLE_HURRICANE_FEATURE


@pytest.fixture
def sample_empty_response():
    """Empty feature list for off-season testing."""
    return SAMPLE_EMPTY_RESPONSE


@pytest.fixture
def sample_thunderstorm_feature():
    """Single thunderstorm_outlook feature."""
    return SAMPLE_THUNDERSTORM_FEATURE
