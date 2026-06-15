"""Shared fixtures for Nova Scotia module unit tests.

Provides Socrata SODA API response fixtures for all response shapes
Plans 02-05 reference, plus autouse cache+limiter patch.

Includes:
  - Catalog search response (2 entries, resultSetSize=706)
  - Views metadata response (get_dataset_metadata shape)
  - Per-dataset row fixtures for all curated datasets
  - Geometry-bearing rows for marine leases and protected areas
  - Empty boil-water advisory list (valid off-season edge case — NOT an error)
  - Both health_zone (AMI) and zone (other diseases) row fixtures for normalization tests

Spike note (20-SPIKE.md): Dataset IDs verified 2026-06-15.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Catalog / discovery fixtures
# ---------------------------------------------------------------------------

SAMPLE_CATALOG_RESPONSE: dict[str, Any] = {
    "results": [
        {
            "resource": {
                "id": "h57h-p9mm",
                "name": "Nova Scotia Marine Aquaculture Leases",
                "description": "Marine aquaculture lease locations with species, ownership, and waterbody data.",
                "type": "dataset",
                "updatedAt": "2026-01-15T00:00:00.000Z",
                "columns_name": ["license_le", "ownership", "species", "waterbody", "county"],
                "columns_field_name": ["license_le", "ownership", "species", "waterbody", "county"],
                "download_count": 8495,
            },
            "classification": {
                "domain_category": "Fishing and Aquaculture",
                "domain_tags": ["marine", "aquaculture", "leases"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Fisheries and Aquaculture"},
                    {"key": "Detailed-Metadata_Frequency", "value": "Monthly"},
                ],
            },
            "metadata": {"domain": "data.novascotia.ca"},
            "permalink": "https://data.novascotia.ca/d/h57h-p9mm",
            "link": "https://data.novascotia.ca/Fishing-and-Aquaculture/Marine-Aquaculture-Leases/h57h-p9mm",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "Open Data Nova Scotia"},
        },
        {
            "resource": {
                "id": "7t68-9xmm",
                "name": "Boil Water Advisories",
                "description": "Active and historical boil water advisories across Nova Scotia.",
                "type": "dataset",
                "updatedAt": "2026-06-14T00:00:00.000Z",
                "columns_name": ["site_name", "county", "date_advisory_issued", "date_advisory_removed"],
                "columns_field_name": ["site_name", "county", "date_advisory_issued", "date_advisory_removed"],
                "download_count": 12400,
            },
            "classification": {
                "domain_category": "Environment and Energy",
                "domain_tags": ["water", "boil", "advisory", "drinking water"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Municipal Affairs and Housing"},
                ],
            },
            "metadata": {"domain": "data.novascotia.ca"},
            "permalink": "https://data.novascotia.ca/d/7t68-9xmm",
            "link": "https://data.novascotia.ca/Environment/Boil-Water-Advisories/7t68-9xmm",
            "owner": {"id": "abc123", "user_type": "organization", "display_name": "Open Data Nova Scotia"},
        },
    ],
    "resultSetSize": 706,
    "timings": {"serviceMillis": 45},
    "warnings": [],
}

SAMPLE_CATALOG_EMPTY: dict[str, Any] = {
    "results": [],
    "resultSetSize": 0,
    "timings": {"serviceMillis": 10},
    "warnings": [],
}

SAMPLE_VIEWS_METADATA: dict[str, Any] = {
    "id": "8e4a-m6fw",
    "name": "Nova Scotia Fish Hatchery Stocking Records",
    "category": "Fishing and Aquaculture",
    "description": "Fish hatchery stocking records including species, hatchery, county, and release date.",
    "columns": [
        {"name": "County", "fieldName": "county", "dataTypeName": "text", "description": "NS county name"},
        {"name": "Stock Species", "fieldName": "stock", "dataTypeName": "text", "description": "Fish species"},
        {"name": "Number Released", "fieldName": "number_released", "dataTypeName": "number", "description": "Count released"},
        {"name": "Stocking Date", "fieldName": "stocking_date", "dataTypeName": "calendar_date", "description": "Release date"},
    ],
    "attribution": "NS Fisheries and Aquaculture",
    "license": {"name": "Open Government Licence – Nova Scotia"},
    "publicationDate": "2024-01-01T00:00:00.000Z",
    "viewLastModified": 1750000000,
    "tags": ["hatchery", "stocking", "fisheries", "brook trout"],
}


# ---------------------------------------------------------------------------
# Fishing / Aquaculture row fixtures
# ---------------------------------------------------------------------------

SAMPLE_MARINE_LEASES_ROWS: list[dict[str, Any]] = [
    {
        "license_le": "MRL-001",
        "ownership": "Atlantic Shellfish Inc.",
        "species": "Eastern Oyster",
        "waterbody": "Bras d'Or Lake",
        "county": "Inverness",
        "sitestatus": "Active",
        "speciestyp": "Shellfish",
        "hectares": "3.2",
        "lat_dms": "46°01'N",
        "long_dms": "60°45'W",
    },
    {
        "license_le": "MRL-002",
        "ownership": "NS Salmon Farms Ltd.",
        "species": "Atlantic Salmon",
        "waterbody": "Shelburne Harbour",
        "county": "Shelburne",
        "sitestatus": "Active",
        "speciestyp": "Finfish",
        "hectares": "12.8",
        "lat_dms": "43°45'N",
        "long_dms": "65°19'W",
    },
]

# Same rows but with the_geom included (to test that tools strip it)
SAMPLE_MARINE_LEASES_ROWS_WITH_GEOM: list[dict[str, Any]] = [
    {
        **SAMPLE_MARINE_LEASES_ROWS[0],
        "the_geom": {
            "type": "MultiPolygon",
            "coordinates": [[[[-60.75, 46.02], [-60.74, 46.02], [-60.74, 46.01], [-60.75, 46.01], [-60.75, 46.02]]]],
        },
    }
]

SAMPLE_LANDBASED_ROWS: list[dict[str, Any]] = [
    {
        "license_le": "LBL-001",
        "species": "Atlantic Salmon",
        "speciestyp": "Finfish",
        "county": "Hants",
        "ownership": "Hatchery Farm Ltd.",
        "sitestatus": "Active",
        "lat_dms": "45°05'N",
        "long_dms": "63°44'W",
    },
]

SAMPLE_HATCHERY_ROWS: list[dict[str, Any]] = [
    {
        "county": "Antigonish",
        "name": "Antigonish River",
        "type": "Stream",
        "stock": "Brook Trout",
        "stock_strain": "NS Wild",
        "hatchery": "Barra Glen Hatchery",
        "fish_length_cm": "12.5",
        "fish_weight_g": "25.0",
        "number_released": "5000",
        "stocking_date": "2025-11-19T00:00:00.000",
        "mark": "None",
        "growth_stage": "Fingerling",
    },
    {
        "county": "Pictou",
        "name": "East River",
        "type": "River",
        "stock": "Atlantic Salmon",
        "stock_strain": "NS Salmon",
        "hatchery": "Mersey Biodiversity Facility",
        "fish_length_cm": "18.2",
        "fish_weight_g": "68.0",
        "number_released": "2000",
        "stocking_date": "2025-10-05T00:00:00.000",
        "mark": "Fin Clip",
        "growth_stage": "Smolt",
    },
]

SAMPLE_PRODUCTION_ROWS: list[dict[str, Any]] = [
    {
        "year": "2022",
        "county": "Guysborough",
        "kgs": "1250000.0",
        "total_value": "8500000.0",
        "full_time": "45.0",
        "total_employ": "60.0",
    },
    {
        "year": "2022",
        "county": "Shelburne",
        "kgs": "980000.0",
        "total_value": "6200000.0",
        "full_time": "32.0",
        "total_employ": "48.0",
    },
]


# ---------------------------------------------------------------------------
# Environment / Water row fixtures
# ---------------------------------------------------------------------------

SAMPLE_WATER_QUALITY_ROWS: list[dict[str, Any]] = [
    {
        "station_number": "NS01EF0002",
        "date": "2024-12-06T00:00:00.000",
        "time": "12:00",
        "temperature_c": "8.3",
        "ph": "7.1",
        "specific_conductance_s_cm": "142.5",
        "dissolved_oxygen_mg_l": "11.2",
    },
    {
        "station_number": "NS01EF0002",
        "date": "2024-12-05T00:00:00.000",
        "time": "12:00",
        "temperature_c": "8.1",
        "ph": "7.0",
        "specific_conductance_s_cm": "141.8",
        "dissolved_oxygen_mg_l": "11.4",
    },
]

# Active boil-water advisories: date_advisory_removed IS NULL
SAMPLE_BOIL_WATER_ROWS_ACTIVE: list[dict[str, Any]] = [
    {
        "site_name": "Murphy Road Water Distribution System",
        "county": "ANNAPOLIS COUNTY",
        "date_advisory_issued": "2025-03-15T00:00:00.000",
        "date_advisory_removed": None,
        "facility_type": "Community Water Supply",
        "length_of_advisory": "92",
    },
    {
        "site_name": "Whycocomagh Water Utility",
        "county": "INVERNESS COUNTY",
        "date_advisory_issued": "2024-11-22T00:00:00.000",
        "date_advisory_removed": None,
        "facility_type": "Municipal Water Supply",
        "length_of_advisory": "205",
    },
]

# Empty advisory list — valid off-season / no-active-advisory edge case (NOT an error)
SAMPLE_BOIL_WATER_ROWS_EMPTY: list[dict[str, Any]] = []

SAMPLE_PROTECTED_AREAS_ROWS: list[dict[str, Any]] = [
    {
        "objectid": "1",
        "pro_name": "Kejimkujik National Park",
        "protect1": "National Park",
        "symbol": "NP",
        "owner": "Federal",
        "authority": "Parks Canada",
        "status": "Designated",
        "web_url": "https://parks.canada.ca/kejimkujik",
        "ha_gis": "381.28",
    },
    {
        "objectid": "2",
        "pro_name": "Tobeatic Wilderness Area",
        "protect1": "Wilderness Area",
        "symbol": "WA",
        "owner": "Provincial",
        "authority": "NS Lands and Forestry",
        "status": "Designated",
        "web_url": "https://nslandscapes.ca/tobeatic",
        "ha_gis": "103000.5",
    },
]

# Same rows but with the_geom (to test geometry exclusion)
SAMPLE_PROTECTED_AREAS_ROWS_WITH_GEOM: list[dict[str, Any]] = [
    {
        **SAMPLE_PROTECTED_AREAS_ROWS[0],
        "the_geom": {
            "type": "MultiPolygon",
            "coordinates": [[[[-65.2, 44.5], [-65.1, 44.5], [-65.1, 44.4], [-65.2, 44.4], [-65.2, 44.5]]]],
        },
    }
]

SAMPLE_AIR_QUALITY_ROWS: list[dict[str, Any]] = [
    {
        "national_air_pollution_surveillance_network_id": "NS001",
        "station_name": "Halifax Central",
        "city": "Halifax",
        "latitude": "44.6501",
        "longitude": "-63.5751",
        "measurements": "PM2.5, O3, NO2, SO2",
        "monitoring_period": "2000-present",
    },
    {
        "national_air_pollution_surveillance_network_id": "NS002",
        "station_name": "Dartmouth East",
        "city": "Dartmouth",
        "latitude": "44.6667",
        "longitude": "-63.5667",
        "measurements": "PM2.5, O3",
        "monitoring_period": "2005-present",
    },
]


# ---------------------------------------------------------------------------
# Health + Demographics row fixtures
# ---------------------------------------------------------------------------

SAMPLE_HOSPITALS_ROWS: list[dict[str, Any]] = [
    {
        "facility_name": "QEII Health Sciences Centre",
        "address": "1796 Summer Street",
        "town": "Halifax",
        "county": "Halifax",
        "type": "Regional",
        "x_coordinate": "-63.5901",
        "y_coordinate": "44.6476",
    },
    {
        "facility_name": "Hants Community Hospital",
        "address": "89 Payzant Drive",
        "town": "Windsor",
        "county": "Hants",
        "type": "Community",
        "x_coordinate": "-64.1333",
        "y_coordinate": "45.0000",
    },
]

SAMPLE_LTC_ROWS: list[dict[str, Any]] = [
    {
        "facility_name": "Melville Gardens",
        "address": "240 Willett St",
        "town": "Truro",
        "county": "Colchester",
        "zone": "Zone 2 - Northern",
        "beds": "68",
        "x_coordinate": "-63.2702",
        "y_coordinate": "45.3604",
        "facility_category": "Long-term Care",
    },
    {
        "facility_name": "Harbourstone Enhanced Care",
        "address": "277 Lacewood Drive",
        "town": "Halifax",
        "county": "Halifax",
        "zone": "Zone 4 - Central",
        "beds": "120",
        "x_coordinate": "-63.6478",
        "y_coordinate": "44.6805",
        "facility_category": "Long-term Care",
    },
]

SAMPLE_VITAL_STATS_ROWS: list[dict[str, Any]] = [
    {
        "counties": "ANNAPOLIS",
        "year": "2020",
        "population": "19875.0",
        "live_births": "142.0",
        "birth_rate": "7.1",
        "deaths": "281.0",
        "death_rate": "14.1",
        "natural_increase_rate": "-7.0",
    },
    {
        "counties": "HALIFAX",
        "year": "2020",
        "population": "446768.0",
        "live_births": "4812.0",
        "birth_rate": "10.8",
        "deaths": "3109.0",
        "death_rate": "7.0",
        "natural_increase_rate": "3.8",
    },
]

# AMI chronic disease rows — uses "health_zone" field (not "zone") and no "sex" field
SAMPLE_CHRONIC_DISEASE_ROWS_AMI: list[dict[str, Any]] = [
    {
        "year": "2018",
        "health_zone": "Zone 1 - Western",
        "age_group": "50 to 69",
        "population": "42185",
        "prevalence": "1847",
        "crude_prevalence_rate": "4.38",
    },
    {
        "year": "2018",
        "health_zone": "Zone 2 - Northern",
        "age_group": "50 to 69",
        "population": "38920",
        "prevalence": "1702",
        "crude_prevalence_rate": "4.37",
    },
]

# Diabetes rows — uses "zone" (not "health_zone") and "agegroup" (no underscore), has sex
SAMPLE_CHRONIC_DISEASE_ROWS_DIABETES: list[dict[str, Any]] = [
    {
        "year": "2000-01-01T00:00:00.000",
        "zone": "Zone 4 - Central",
        "sex": "F",
        "agegroup": "20 to 29",
        "population": "30198",
        "prevalence": "223",
        "crude_prevalence_rate": "0.74",
    },
    {
        "year": "2000-01-01T00:00:00.000",
        "zone": "Zone 4 - Central",
        "sex": "M",
        "agegroup": "20 to 29",
        "population": "28500",
        "prevalence": "195",
        "crude_prevalence_rate": "0.68",
    },
]

# Hypertension rows — uses "zone", "age_group", "hypertension_count", "prevalence_rate"
SAMPLE_CHRONIC_DISEASE_ROWS_HYPERTENSION: list[dict[str, Any]] = [
    {
        "year": "2000-01-01T00:00:00.000",
        "zone": "Zone 4 - Central",
        "sex": "F",
        "age_group": "20 to 29",
        "population": "30198",
        "hypertension_count": "367",
        "prevalence_rate": "1.22",
    },
]


# ---------------------------------------------------------------------------
# Autouse fixture: clear cache + patch limiter for unit tests
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_cache_and_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch cached_fetch to pass-through (no actual cache) and get_limiter to no-op.

    This prevents test isolation issues from shared cache state and
    prevents actual rate limit delays during unit tests.
    """
    import mcp_canada.modules.nova_scotia.client as _client_mod

    # Patch cached_fetch so it always calls the fetcher directly (no cache layer)
    async def _passthrough_cached_fetch(key: str, ttl: int, fetcher):  # type: ignore[type-arg]
        return (await fetcher(), False)

    monkeypatch.setattr(
        "mcp_canada.modules.nova_scotia.client.cached_fetch",
        _passthrough_cached_fetch,
    )

    # Patch the _limiter to a no-op acquire
    mock_limiter = MagicMock()
    mock_limiter.acquire = AsyncMock(return_value=None)
    monkeypatch.setattr(_client_mod, "_limiter", mock_limiter)
