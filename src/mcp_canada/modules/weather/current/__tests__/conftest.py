"""Test fixtures for weather/current module tests."""

import pytest


@pytest.fixture
def sample_citypage_feature():
    """A citypageweather-realtime feature with nested bilingual structure.

    Structure mirrors the live API: every value is wrapped in
    {"value": {"en": ..., "fr": ...}, "units": {...}}.
    The forecastGroup contains a list of forecast periods.
    """
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-75.7, 45.4]},
        "properties": {
            "name": {"en": "Ottawa (Kanata - Orléans)", "fr": "Ottawa (Kanata - Orléans)"},
            "currentConditions": {
                "station": {
                    "value": {"en": "Ottawa Macdonald-Cartier Intl", "fr": "Ottawa Macdonald-Cartier Intl"},
                },
                "temperature": {
                    "value": {"en": 5.3, "fr": 5.3},
                    "units": {"en": "C", "fr": "C"},
                },
                "relativeHumidity": {
                    "value": {"en": 82, "fr": 82},
                    "units": {"en": "%", "fr": "%"},
                },
                "wind": {
                    "speed": {"value": {"en": 15, "fr": 15}, "units": {"en": "km/h", "fr": "km/h"}},
                    "direction": {"value": {"en": "W", "fr": "O"}},
                },
                "pressure": {
                    "value": {"en": 101.2, "fr": 101.2},
                    "units": {"en": "kPa", "fr": "kPa"},
                },
                "windChill": {
                    "value": {"en": 2.0, "fr": 2.0},
                },
                "condition": {"en": "Partly Cloudy", "fr": "Partiellement nuageux"},
                "timestamp": {"en": "2026-04-05T12:00:00Z", "fr": "2026-04-05T12:00:00Z"},
            },
            "forecastGroup": {
                "forecasts": [
                    {
                        "period": {
                            "textForecastName": {"en": "Tonight", "fr": "Ce soir"},
                        },
                        "temperatures": {
                            "temperature": [
                                {"value": {"en": -2, "fr": -2}, "class": {"en": "low", "fr": "low"}},
                            ],
                        },
                        "textSummary": {"en": "Clear. Low minus 2.", "fr": "Dégagé. Minimum moins 2."},
                        "winds": {
                            "periods": [
                                {
                                    "speed": {"value": {"en": 10, "fr": 10}},
                                    "bearing": {"value": {"en": 225, "fr": 225}},
                                },
                            ],
                        },
                        "abbreviatedForecast": {
                            "textSummary": {"en": "Clear", "fr": "Dégagé"},
                        },
                    },
                    {
                        "period": {
                            "textForecastName": {"en": "Monday", "fr": "Lundi"},
                        },
                        "temperatures": {
                            "temperature": [
                                {"value": {"en": 8, "fr": 8}, "class": {"en": "high", "fr": "high"}},
                            ],
                        },
                        "textSummary": {"en": "Sunny. High 8.", "fr": "Ensoleillé. Maximum 8."},
                        "winds": {
                            "periods": [
                                {
                                    "speed": {"value": {"en": 20, "fr": 20}},
                                    "bearing": {"value": {"en": 270, "fr": 270}},
                                },
                            ],
                        },
                        "abbreviatedForecast": {
                            "textSummary": {"en": "Sunny", "fr": "Ensoleillé"},
                        },
                    },
                ]
            },
        },
    }


@pytest.fixture
def sample_alert_feature():
    """A weather-alerts feature with all key fields populated."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-66.5, 45.9]},
        "properties": {
            "alert_code": "WWCN35_CWNT",
            "alert_type": "warning",
            "alert_name_en": "Special Weather Statement",
            "alert_name_fr": "Bulletin météorologique spécial",
            "province": "NB",
            "feature_name_en": "Saint John Region",
            "feature_name_fr": "Région de Saint-Jean",
            "alert_text_en": "Heavy rain expected. Total amounts 40 to 60 mm.",
            "alert_text_fr": "Fortes pluies attendues. Totaux de 40 à 60 mm.",
            "publication_datetime": "2026-04-05T10:00:00Z",
            "expiration_datetime": "2026-04-05T22:00:00Z",
        },
    }


@pytest.fixture
def sample_station_feature():
    """A climate-stations feature with Point geometry.

    IMPORTANT: Use geometry.coordinates for lat/lon (decimal degrees),
    NOT the LATITUDE/LONGITUDE properties (which are in DMS format).
    """
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-75.72, 45.42]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6105976",
            "STATION_NAME": "OTTAWA CDA",
            "PROVINCE_CODE": "ON",
            "LATITUDE": 454200000,   # DMS format — do NOT use this
            "LONGITUDE": -757200000,  # DMS format — do NOT use this
            "ELEVATION": 79.0,
            "FIRST_DATE": "1889-01-01",
            "LAST_DATE": "2026-04-01",
            "HLY_FIRST_DATE": "1953-01-01",
            "HLY_LAST_DATE": "2026-04-01",
            "DLY_FIRST_DATE": "1889-01-01",
            "DLY_LAST_DATE": "2026-04-01",
            "MLY_FIRST_DATE": "1889-01-01",
            "MLY_LAST_DATE": "2020-12-01",
        },
    }


@pytest.fixture
def sample_hourly_feature():
    """A climate-hourly feature with standard observation fields."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-75.72, 45.42]},
        "properties": {
            "CLIMATE_IDENTIFIER": "6105976",
            "LOCAL_DATE": "2024-01-15T14:00:00",
            "TEMP": 3.2,
            "DEW_POINT_TEMP": -1.1,
            "WIND_DIRECTION": 270,
            "WIND_SPEED": 15.0,
            "WEATHER_ENG_DESC": "Mainly clear",
            "STATION_PRESSURE": 101.8,
        },
    }
