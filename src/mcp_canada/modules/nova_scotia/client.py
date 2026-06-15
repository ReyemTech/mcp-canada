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
# Discovery client functions (Plan 02)
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search the Nova Scotia Socrata catalog by keyword with pagination.

    Returns shaped results: {"results": [...], "total": int}.
    Limit is clamped to [1, 1000] before forwarding to the SODA API.
    """
    clamped_limit = max(1, min(limit, 1000))
    cache_key = f"{CACHE_KEY_PREFIX}catalog:search:{query}:{clamped_limit}:{offset}"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q=query,
            limit=clamped_limit,
            offset=offset,
            only="datasets",
            app_token=APP_TOKEN,
        )
        results = [socrata.shape_catalog_result(r) for r in raw.get("results", [])]
        return {"results": results, "total": raw.get("resultSetSize", 0)}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_dataset_details(
    dataset_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch /api/views/{id}.json metadata for a dataset.

    Returns {"details": flat_metadata_dict}.
    """
    cache_key = f"{CACHE_KEY_PREFIX}metadata:{dataset_id}"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        flat = await socrata.get_dataset_metadata(
            BASE_DOMAIN,
            dataset_id,
            app_token=APP_TOKEN,
        )
        return {"details": flat}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


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
    """Pass-through SoQL query for any NS dataset.

    When include_geometry=False (default) AND select is None, select is left as None —
    Socrata returns all fields including the_geom. Agents should pass explicit $select
    to exclude geometry. When include_geometry=False AND select is provided, select
    passes through unchanged.
    """
    cache_key = (
        f"{CACHE_KEY_PREFIX}query:{dataset_id}:{where}:{select}:"
        f"{order}:{limit}:{offset}:{q}:{group}:{include_geometry}"
    )

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        rows = await socrata.query_dataset(
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
        return {"rows": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_organizations() -> tuple[dict[str, Any], bool]:
    """List unique organization attributions from the NS Socrata catalog.

    Fetches a wide catalog page and aggregates unique owner.display_name /
    attribution values with dataset counts. Never uses a dedicated organizations
    endpoint — derives from catalog results (same approach as Saskatchewan Hub).
    """
    cache_key = f"{CACHE_KEY_PREFIX}organizations"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        # Fetch a wide page to capture many organizations
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q="",
            limit=1000,
            offset=0,
            only="datasets",
            app_token=APP_TOKEN,
        )
        # Aggregate unique owner.display_name values with counts
        org_counts: dict[str, int] = {}
        for result in raw.get("results", []):
            owner = result.get("owner") or {}
            name = owner.get("display_name")
            # Also try attribution from classification.domain_metadata
            if not name:
                for meta in (result.get("classification") or {}).get("domain_metadata") or []:
                    if isinstance(meta, dict) and str(meta.get("key", "")).endswith("Department"):
                        name = meta.get("value")
                        break
            if name:
                org_counts[name] = org_counts.get(name, 0) + 1

        organizations = sorted(
            [{"name": k, "dataset_count": v} for k, v in org_counts.items()],
            key=lambda x: (-int(x["dataset_count"]), str(x["name"])),
        )
        return {"organizations": organizations}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_categories() -> tuple[dict[str, Any], bool]:
    """List domain categories from the NS Socrata catalog.

    IMPORTANT: The catalog categories= param is BROKEN (returns resultSetSize=0 always).
    This function uses q= (or empty q) + client-side aggregation of
    classification.domain_category to enumerate all categories.
    The categories= param is NEVER sent.
    """
    cache_key = f"{CACHE_KEY_PREFIX}categories"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        # Fetch a wide page to capture many categories (no categories= param — it's broken)
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q="",
            limit=1000,
            offset=0,
            only="datasets",
            app_token=APP_TOKEN,
        )
        # Aggregate classification.domain_category values client-side
        cat_counts: dict[str, int] = {}
        for result in raw.get("results", []):
            classification = result.get("classification") or {}
            cat = classification.get("domain_category")
            if cat:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        categories = sorted(
            [{"name": k, "count": v} for k, v in cat_counts.items()],
            key=lambda x: (-int(x["count"]), str(x["name"])),
        )
        return {"categories": categories}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


# ---------------------------------------------------------------------------
# Fishing / Aquaculture client functions (Plan 03 fills bodies)
# ---------------------------------------------------------------------------


async def fetch_marine_aquaculture_leases(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Marine aquaculture leases (h57h-p9mm).

    Uses explicit $select to EXCLUDE the_geom (Pitfall 5 — geometry bloats responses).
    Optional county and speciestyp SoQL filters; $order=county ASC.
    """
    where_parts: list[str] = []
    if county:
        where_parts.append(f"county='{county}'")
    if species_type:
        where_parts.append(f"speciestyp='{species_type}'")
    where = " AND ".join(where_parts) or None

    cache_key = f"{CACHE_KEY_PREFIX}marine_leases:{county or 'all'}:{species_type or 'all'}:{limit}"

    async def fetcher() -> dict[str, Any]:
        rows = await _soql(
            DS_MARINE_AQUACULTURE_LEASES,
            where=where,
            select="license_le,ownership,species,waterbody,county,sitestatus,speciestyp,hectares,lat_dms,long_dms",
            order="county ASC",
            limit=limit,
        )
        # Defensive strip: the_geom excluded by $select; belt-and-suspenders to ensure
        # geometry never reaches the agent context (Pitfall 5 — MultiPolygon can be huge).
        rows = [{k: v for k, v in row.items() if k != "the_geom"} for row in rows]
        return {"leases": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_landbased_aquaculture_licenses(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Landbased aquaculture licenses (yqwg-f62a).

    Optional county and speciestyp SoQL filters; explicit $select.
    """
    where_parts: list[str] = []
    if county:
        where_parts.append(f"county='{county}'")
    if species_type:
        where_parts.append(f"speciestyp='{species_type}'")
    where = " AND ".join(where_parts) or None

    cache_key = f"{CACHE_KEY_PREFIX}landbased_licenses:{county or 'all'}:{species_type or 'all'}:{limit}"

    async def fetcher() -> dict[str, Any]:
        rows = await _soql(
            DS_LANDBASED_AQUACULTURE_LICENSES,
            where=where,
            select="license_le,species,speciestyp,county,ownership,sitestatus,lat_dms,long_dms",
            order="county ASC",
            limit=limit,
        )
        return {"licenses": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_fish_hatchery_stocking(
    stock: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fish hatchery stocking records (8e4a-m6fw).

    Optional stock species and county SoQL filters; $order=stocking_date DESC (newest first).
    Data current to 2025-11-19.
    """
    where_parts: list[str] = []
    if stock:
        where_parts.append(f"stock='{stock}'")
    if county:
        where_parts.append(f"county='{county}'")
    where = " AND ".join(where_parts) or None

    cache_key = f"{CACHE_KEY_PREFIX}hatchery_stocking:{stock or 'all'}:{county or 'all'}:{limit}"

    async def fetcher() -> dict[str, Any]:
        rows = await _soql(
            DS_FISH_HATCHERY_STOCKING,
            where=where,
            select="county,name,type,stock,stock_strain,hatchery,fish_length_cm,fish_weight_g,number_released,stocking_date,mark,growth_stage",
            order="stocking_date DESC",
            limit=limit,
        )
        return {"stocking_records": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_aquaculture_production(
    year: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Aquaculture production, value, employment by county (v2ex-ev63).

    Optional year and county SoQL filters.
    IMPORTANT: year is a TEXT column — use string comparison: year='2020' NOT year=2020.
    Annual data; 7-day cache TTL.
    """
    where_parts: list[str] = []
    if year:
        # Pitfall 3: year is stored as text, must use quoted string comparison
        where_parts.append(f"year='{year}'")
    if county:
        where_parts.append(f"county='{county}'")
    where = " AND ".join(where_parts) or None

    cache_key = f"{CACHE_KEY_PREFIX}aquaculture_production:{year or 'all'}:{county or 'all'}:{limit}"

    async def fetcher() -> dict[str, Any]:
        rows = await _soql(
            DS_AQUACULTURE_PRODUCTION,
            where=where,
            select="year,county,kgs,total_value,full_time,pt_employ_6_mth,pt_employ_6_mth_1,total_employ",
            order="year DESC",
            limit=limit,
        )
        return {"production": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_ANNUAL, fetcher)


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
