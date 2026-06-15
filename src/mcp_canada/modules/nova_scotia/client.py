"""Nova Scotia module client — async functions returning (data, was_cached) tuples.

Plans 02-05 fill function bodies (this Wave 0 file defines _soql helper + all signatures).
Signatures are LOCKED — downstream plans fill the bodies only.

Plan assignments:
  - Plan 02: fetch_search_datasets, fetch_dataset_details, fetch_query_dataset,
             fetch_organizations, fetch_categories
  - Plan 03: fetch_marine_aquaculture_leases, fetch_landbased_aquaculture_licenses,
             fetch_fish_hatchery_stocking, fetch_aquaculture_production
  - Plan 04: fetch_water_quality_monitoring, fetch_boil_water_advisories,
             fetch_protected_areas, fetch_air_quality_stations
  - Plan 05: fetch_health_facilities, fetch_vital_statistics, fetch_chronic_disease

Design notes:
  - shared/socrata.py provides search_catalog, get_dataset_metadata, query_dataset.
  - cached_fetch + get_limiter live here (NOT inside shared/socrata.py).
  - _soql helper centralises await _limiter.acquire() + socrata.query_dataset() call.
  - All curated fetchers return tuple[dict, bool] where dict = {"<key>": [...], "count": N, "truncated": bool}.
  - Geometry stripping: curated tools must pass explicit $select to exclude the_geom.
    fetch_query_dataset(include_geometry=False) strips the_geom from $select in Plan 02.

Chronic disease normalization (spike-confirmed 2026-06-15 — see 20-SPIKE.md):
  - AMI uses "health_zone" field → normalize to "zone" in output
  - Diabetes/COPD use "agegroup" (no underscore) → normalize to "age_group"
  - Hypertension uses "hypertension_count" and "prevalence_rate" (not standard names)
  - AMI has no "sex" field → sex filter must be skipped
  - _normalize_zone_field is implemented here (used by Plan 05)
"""

from __future__ import annotations

import os
from typing import Any

from mcp_canada.shared import socrata
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    ACTIVE_ADVISORY_FILTER,  # noqa: F401 — re-exported for Plan 04 use
    BASE_DOMAIN,
    CACHE_KEY_PREFIX,  # noqa: F401
    CACHE_TTL_ANNUAL,
    CACHE_TTL_LIVE,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    CHRONIC_DISEASE_DATASETS,
    CHRONIC_DISEASE_AGE_FIELD,
    CHRONIC_DISEASE_HAS_SEX,
    CHRONIC_DISEASE_ZONE_FIELD,
    DEFAULT_PAGE_SIZE,  # noqa: F401
    DS_AIR_QUALITY_STATIONS,  # noqa: F401
    DS_AQUACULTURE_PRODUCTION,  # noqa: F401
    DS_BIRTHS_DEATHS,  # noqa: F401
    DS_BOIL_WATER_ADVISORIES,  # noqa: F401
    DS_FISH_HATCHERY_STOCKING,  # noqa: F401
    DS_HOSPITALS,  # noqa: F401
    DS_LANDBASED_AQUACULTURE_LICENSES,  # noqa: F401
    DS_LTC_RCF_FACILITIES,  # noqa: F401
    DS_LTC_WAITLIST,  # noqa: F401
    DS_MARINE_AQUACULTURE_LEASES,  # noqa: F401
    DS_PROTECTED_AREAS,  # noqa: F401
    DS_ROCKWEED_LEASES,  # noqa: F401
    DS_SURFACE_WATER_QUALITY_CONTINUOUS,  # noqa: F401
    DS_SURFACE_WATER_QUALITY_STATIONS,  # noqa: F401
    MAX_RECORDS,
    NS_APP_TOKEN_ENV,
    RATE_GROUP,
    RATE_LIMIT,
)

# ---------------------------------------------------------------------------
# Module-level setup
# ---------------------------------------------------------------------------

# App token: read from environment at module import; passed to all socrata.* calls.
# Default is None (keyless). Set NS_APP_TOKEN env var for higher throttle limits.
APP_TOKEN: str | None = os.environ.get(NS_APP_TOKEN_ENV)

# Single shared rate limiter for all Nova Scotia SODA calls.
_limiter = get_limiter(RATE_GROUP, RATE_LIMIT)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _soql(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = MAX_RECORDS,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
) -> list[dict[str, Any]]:
    """Acquire rate-limit token then query a Nova Scotia dataset via SoQL.

    Centralises the limiter.acquire() + socrata.query_dataset() pattern
    so curated fetchers are one-liners. Does NOT cache — callers wrap with cached_fetch.

    Args:
        dataset_id: 4x4 Socrata dataset identifier.
        where: SoQL WHERE clause (optional).
        select: Comma-separated fields (optional; omit for all fields).
        order: SoQL ORDER BY clause (optional).
        limit: Max rows to return (default: MAX_RECORDS).
        offset: Pagination offset (default: 0).
        q: Full-text search within dataset (optional).
        group: SoQL GROUP BY clause for aggregations (optional).

    Returns:
        List of flat row dicts from the SODA /resource/{id}.json endpoint.
    """
    await _limiter.acquire()
    return await socrata.query_dataset(
        BASE_DOMAIN,
        dataset_id,
        where=where,
        select=select,
        order=order,
        limit=limit,
        offset=offset,
        q=q,
        group=group,
        app_token=APP_TOKEN,
    )


def _normalize_zone_field(row: dict[str, Any], disease: str) -> dict[str, Any]:
    """Normalize zone and age_group field names across chronic disease datasets.

    Spike findings (20-SPIKE.md):
      - AMI uses "health_zone" → renamed to "zone" in output
      - Diabetes/COPD use "agegroup" (no underscore) → renamed to "age_group"
      - AMI has no "sex" field → sex remains absent (not added)

    Args:
        row: Raw row dict from the SODA endpoint.
        disease: Disease key ("ami", "diabetes", "copd", "hypertension", "asthma").

    Returns:
        New dict with normalized field names + disease key injected.
    """
    result = dict(row)
    result["disease"] = disease

    # Normalize zone field
    zone_field = CHRONIC_DISEASE_ZONE_FIELD.get(disease, "zone")
    if zone_field != "zone" and zone_field in result:
        result["zone"] = result.pop(zone_field)

    # Normalize age_group field
    age_field = CHRONIC_DISEASE_AGE_FIELD.get(disease, "age_group")
    if age_field != "age_group" and age_field in result:
        result["age_group"] = result.pop(age_field)

    return result


# ---------------------------------------------------------------------------
# Discovery client functions (Plan 02 fills bodies)
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search the NS Socrata catalog. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_dataset_details(
    dataset_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch /api/views/{id}.json metadata for a dataset. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_query_dataset(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Pass-through SoQL query for any NS dataset. Filled by Plan 02.

    When include_geometry=False (default), the_geom is stripped from $select.
    """
    raise NotImplementedError("Plan 02 implements")


async def fetch_organizations() -> tuple[dict[str, Any], bool]:
    """List unique organization attributions from NS catalog. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_categories() -> tuple[dict[str, Any], bool]:
    """List domain categories from NS catalog. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


# ---------------------------------------------------------------------------
# Fishing / Aquaculture client functions (Plan 03 fills bodies)
# ---------------------------------------------------------------------------


async def fetch_marine_aquaculture_leases(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Marine aquaculture leases (h57h-p9mm); $select excludes the_geom. Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_landbased_aquaculture_licenses(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Landbased aquaculture licenses (yqwg-f62a). Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_fish_hatchery_stocking(
    stock: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fish hatchery stocking records (8e4a-m6fw). Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_aquaculture_production(
    year: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Aquaculture production, value, employment (v2ex-ev63). Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


# ---------------------------------------------------------------------------
# Environment / Air Quality client functions (Plan 04 fills bodies)
# ---------------------------------------------------------------------------


async def fetch_water_quality_monitoring(
    station_number: str | None = None,
    since: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Surface water quality continuous readings (bkfi-mjgw). Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_boil_water_advisories(
    county: str | None = None,
    active_only: bool = False,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Boil water advisories (7t68-9xmm). Active filter = IS NULL. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_protected_areas(
    status: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Protected areas system (ticv-5du5); $select excludes the_geom. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_air_quality_stations(
    city: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Air quality monitoring stations catalog (3bbm-drnh). Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


# ---------------------------------------------------------------------------
# Health + Demographics client functions (Plan 05 fills bodies)
# ---------------------------------------------------------------------------


async def fetch_health_facilities(
    facility_type: str,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Hospital or LTC facilities dispatched by facility_type. Filled by Plan 05.

    facility_type: "hospital" → DS_HOSPITALS (tmfr-3h8a)
                   "long_term_care" → DS_LTC_RCF_FACILITIES (x76a-axw2)
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_vital_statistics(
    county: str | None = None,
    year: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Annual vital statistics by county (r794-fttm). Filled by Plan 05."""
    raise NotImplementedError("Plan 05 implements")


async def fetch_chronic_disease(
    disease: str,
    health_zone: str | None = None,
    sex: str | None = None,
    year: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Chronic disease prevalence dispatched by disease type. Filled by Plan 05.

    dispatch dict: CHRONIC_DISEASE_DATASETS[disease] → dataset ID.
    Normalizes health_zone→zone (AMI) and agegroup→age_group (diabetes/COPD).
    Skips sex filter for AMI (no sex field in that dataset).
    """
    raise NotImplementedError("Plan 05 implements")
