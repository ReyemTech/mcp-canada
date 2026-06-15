"""Nova Scotia module constants.

Nova Scotia uses Socrata SODA (data.novascotia.ca), NOT CKAN/ArcGIS Hub.
  - Discovery = /api/catalog/v1 (NOT api/views.json — no pagination metadata).
  - categories= catalog param is BROKEN (returns resultSetSize=0 always) —
    use q= keyword search + client-side filter on classification.domain_category.
  - Transport/511 HTML-only (deferred); NS ArcGIS Hub novagis deferred.
  - Geometry stripping: use $select to exclude the_geom from curated tool responses.

All dataset IDs are live-verified 2026-06-15 against data.novascotia.ca.

Spike verdicts (20-SPIKE.md, 2026-06-15):
  - Rockweed exhe-htib: 3 tabular fields (ownership/lease_le/hectares); no curated tool.
  - ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL" (confirmed: 82 active advisories;
    empty-string comparison causes type-mismatch error on the date field).
  - Chronic disease zone field: AMI uses "health_zone" (rename to "zone"); others use "zone".
  - AMI: no sex field; plain string year ("2000"); others: ISO timestamp year.
  - Hypertension: "hypertension_count" (not "prevalence") + "prevalence_rate" (not "crude_prevalence_rate").
"""

from typing import Final

# ---------------------------------------------------------------------------
# Portal identifiers
# ---------------------------------------------------------------------------
BASE_DOMAIN: Final[str] = "data.novascotia.ca"
BASE_URL: Final[str] = f"https://{BASE_DOMAIN}"
CATALOG_URL: Final[str] = f"{BASE_URL}/api/catalog/v1"

# ---------------------------------------------------------------------------
# Rate limiting (Socrata keyless throttles ~1 req/sec per IP without token)
# ---------------------------------------------------------------------------
RATE_GROUP: Final[str] = "nova_scotia_soda"
RATE_LIMIT: Final[float] = 2.0   # conservative; keyless Socrata ~1/s per IP

# ---------------------------------------------------------------------------
# App token (read at module import; future enhancement for higher throttle)
# ---------------------------------------------------------------------------
NS_APP_TOKEN_ENV: Final[str] = "NS_APP_TOKEN"

# ---------------------------------------------------------------------------
# Fishing / Aquaculture dataset IDs (live-verified 2026-06-15)
# ---------------------------------------------------------------------------
DS_MARINE_AQUACULTURE_LEASES: Final[str] = "h57h-p9mm"     # Marine Aquaculture Leases
DS_LANDBASED_AQUACULTURE_LICENSES: Final[str] = "yqwg-f62a" # Landbased Aquaculture Licenses
DS_FISH_HATCHERY_STOCKING: Final[str] = "8e4a-m6fw"         # Fish Hatchery Stocking Records
DS_AQUACULTURE_PRODUCTION: Final[str] = "v2ex-ev63"          # Aquaculture Production/Value/Employment
DS_ROCKWEED_LEASES: Final[str] = "exhe-htib"                 # Rockweed Leases (3 attribute fields; discovery-only)

# ---------------------------------------------------------------------------
# Environment / Water dataset IDs (live-verified 2026-06-15)
# ---------------------------------------------------------------------------
DS_SURFACE_WATER_QUALITY_CONTINUOUS: Final[str] = "bkfi-mjgw"  # Continuous sensor readings
DS_SURFACE_WATER_QUALITY_STATIONS: Final[str] = "i9ee-9hct"    # Station locations
DS_BOIL_WATER_ADVISORIES: Final[str] = "7t68-9xmm"             # Boil water advisories

# ---------------------------------------------------------------------------
# Lands dataset IDs
# ---------------------------------------------------------------------------
DS_PROTECTED_AREAS: Final[str] = "ticv-5du5"  # Nova Scotia Protected Areas System
DS_CROWN_LAND: Final[str] = "3nka-59nz"        # Crown land (discoverable; not curated)

# ---------------------------------------------------------------------------
# Air Quality dataset IDs
# ---------------------------------------------------------------------------
DS_AIR_QUALITY_STATIONS: Final[str] = "3bbm-drnh"  # Provincial Ambient Air Quality Monitoring Stations

# ---------------------------------------------------------------------------
# Health + Demographics dataset IDs (live-verified 2026-06-15)
# ---------------------------------------------------------------------------
DS_HOSPITALS: Final[str] = "tmfr-3h8a"         # Hospitals
DS_LTC_RCF_FACILITIES: Final[str] = "x76a-axw2" # Long-term Care / Residential Care Facilities
DS_LTC_WAITLIST: Final[str] = "c39g-gsdd"       # Long-term Care Waitlist
DS_BIRTHS_DEATHS: Final[str] = "r794-fttm"      # Births and Deaths with Rates

# ---------------------------------------------------------------------------
# Chronic disease datasets — dispatch dict (all live-verified 2026-06-15)
#
# IMPORTANT schema differences (from 20-SPIKE.md):
#   ami:          zone="health_zone" (rename→zone); no sex field; year=plain string; age="age_group"
#   diabetes:     zone="zone"; sex present; year=ISO timestamp; age="agegroup" (no underscore)
#   copd:         zone="zone"; sex present; year=ISO timestamp; age="agegroup" (no underscore)
#   hypertension: zone="zone"; sex present; year=ISO timestamp; age="age_group";
#                 count="hypertension_count" (not "prevalence"); rate="prevalence_rate"
#   asthma:       zone="zone"; sex present; year=ISO timestamp; age="age_group"
# ---------------------------------------------------------------------------
CHRONIC_DISEASE_DATASETS: Final[dict[str, str]] = {
    "ami": "24qf-ntke",
    "diabetes": "cumi-sw99",
    "copd": "ua9e-4pss",
    "hypertension": "sztc-sewr",
    "asthma": "2bih-5dgk",
}

# Per-disease zone field name (from spike — AMI uses "health_zone", others "zone")
CHRONIC_DISEASE_ZONE_FIELD: Final[dict[str, str]] = {
    "ami": "health_zone",
    "diabetes": "zone",
    "copd": "zone",
    "hypertension": "zone",
    "asthma": "zone",
}

# Per-disease age group field name (AMI + hypertension + asthma = "age_group"; others = "agegroup")
CHRONIC_DISEASE_AGE_FIELD: Final[dict[str, str]] = {
    "ami": "age_group",
    "diabetes": "agegroup",
    "copd": "agegroup",
    "hypertension": "age_group",
    "asthma": "age_group",
}

# Diseases that have a sex field (AMI does NOT)
CHRONIC_DISEASE_HAS_SEX: Final[dict[str, bool]] = {
    "ami": False,
    "diabetes": True,
    "copd": True,
    "hypertension": True,
    "asthma": True,
}

# ---------------------------------------------------------------------------
# Boil-water active advisory filter (spike-confirmed 2026-06-15)
#
# TODO: Plan 04 implements fetch_boil_water_advisories using this constant.
# ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL" because:
#   - IS NULL returns 82 (active advisories as of 2026-06-15) — CORRECT
#   - = '' causes type-mismatch error on the date column — WRONG
# ---------------------------------------------------------------------------
ACTIVE_ADVISORY_FILTER: Final[str] = "date_advisory_removed IS NULL"

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 900       # 15min — boil water advisories (critical safety data)
CACHE_TTL_SEARCH: Final[int] = 3600    # 1h — catalog search results
CACHE_TTL_META: Final[int] = 86400     # 24h — facilities, leases, hatchery, stations
CACHE_TTL_ANNUAL: Final[int] = 604800  # 7d — vital stats, production, chronic disease (annual data)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: Final[int] = 1000
MAX_RECORDS: Final[int] = 5000

# ---------------------------------------------------------------------------
# Cache key prefix
# ---------------------------------------------------------------------------
CACHE_KEY_PREFIX: Final[str] = "nova_scotia:"
