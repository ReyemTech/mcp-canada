"""York Region municipal open data client.

Wraps shared.arcgis_hub.* with portal-specific constants, caching, and rate limiting.
All public functions return (data, was_cached) tuples.

Coverage:
- Discovery (5 per-portal): search_datasets, dataset_details, query_features,
  list_organizations, list_categories
- Curated York Region (10): transit stops/routes, regional roads, beach water testing,
  hospitals, drinking water, solid waste sites, census age/sex, census income,
  waste diversion
- Curated Markham (2): addresses, roads
"""

from __future__ import annotations

from typing import Any

from mcp_canada.shared.arcgis_hub import (
    get_count,  # noqa: F401 — re-exported for optional direct use by tools
    get_layer_metadata,  # noqa: F401 — re-exported for optional direct use by tools
    query_feature_service,
    search_hub_datasets,
    shape_hub_dataset,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter
from mcp_canada.modules.york_region.constants import (
    PORTAL_URLS,
    RATE_GROUP,
    RATE_LIMIT,
    CACHE_TTL_SEARCH,
    CACHE_TTL_DATA,
    CACHE_TTL_ORGS,
    YR_TRANSIT_FS,
    YR_BUS_STOPS_LAYER,
    YR_BUS_ROUTES_LAYER,
    YR_REGIONAL_ROADS_LAYER,
    YR_HEALTH_FS,
    YR_BEACH_TESTING_LAYER,
    YR_HOSPITAL_LAYER,
    YR_ENVIRONMENTAL_FS,
    YR_SOLID_WASTE_SITES_LAYER,
    YR_DRINKING_WATER_FS,
    YR_DRINKING_WATER_ADVERSE_LAYER,
    YR_AGE_SEX_FS,
    YR_INCOME_FS,
    YR_WASTE_DIVERSION_FS,
    YR_CENSUS_LAYER,
    YR_CENSUS_AGE_FIELDS,
    YR_CENSUS_INCOME_FIELDS,
    MARKHAM_ADDRESSES_FS,
    MARKHAM_ROADS_FS,
    MARKHAM_ADDRESSES_LAYER,
    MARKHAM_ROADS_LAYER,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class NoPortalError(Exception):
    """Raised when a municipality has no public ArcGIS Hub portal."""


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _require_portal(portal_key: str) -> str:
    """Return the portal URL for the given key, or raise NoPortalError if None or unknown.

    Args:
        portal_key: Key from PORTAL_URLS (e.g., "york_region", "markham").

    Returns:
        The portal base URL string.

    Raises:
        NoPortalError: If the key maps to None or is not in PORTAL_URLS.
    """
    url = PORTAL_URLS.get(portal_key)
    if url is None:
        raise NoPortalError(
            f"{portal_key} has no public ArcGIS Hub open data portal as of 2026-04"
        )
    return url


def _escape_where_value(v: str) -> str:
    """Escape single quotes in a SQL WHERE clause string value.

    Prevents SQL injection in ArcGIS WHERE clauses by doubling single quotes.

    Args:
        v: User-supplied string value to embed in a WHERE clause.

    Returns:
        Escaped string safe for inclusion in a SQL-92 WHERE clause.
    """
    return v.replace("'", "''")


async def _rate_limited_call(coro_factory):
    """Acquire the arcgis_hub rate limiter then invoke the zero-arg coroutine factory."""
    limiter = get_limiter(RATE_GROUP, RATE_LIMIT)
    await limiter.acquire()
    return await coro_factory()


async def _fetch_features(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 5000,
) -> tuple[dict[str, Any], bool]:
    """Internal helper: calls query_feature_service with rate limiting + caching.

    Returns ({"features": [...], "count": int, "truncated": bool}, was_cached).
    """
    cache_key = f"york_region:fs:{service_url}:{layer_id}:{where}:{out_fields}:{include_geometry}:{max_records}"

    async def _fetcher() -> dict[str, Any]:
        features, truncated = await _rate_limited_call(
            lambda: query_feature_service(
                service_url,
                layer_id,
                where=where,
                out_fields=out_fields,
                include_geometry=include_geometry,
                max_records=max_records,
            )
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_DATA, _fetcher)


# ---------------------------------------------------------------------------
# Discovery functions (5 per-portal)
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    portal_key: str,
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """Search an ArcGIS Hub portal for datasets.

    Args:
        portal_key: One of the 10 keys in PORTAL_URLS.
        query: Free-text search query.
        limit: Max results per page.
        offset: Pagination offset.
        lang: Response language ("en" or "fr").

    Returns:
        (list of shaped dataset dicts, was_cached)

    Raises:
        NoPortalError: If the portal_key maps to None (no public portal).
    """
    portal_url = _require_portal(portal_key)
    cache_key = f"york_region:search:{portal_key}:{query}:{limit}:{offset}"

    async def _fetcher() -> list[dict[str, Any]]:
        raw = await _rate_limited_call(
            lambda: search_hub_datasets(portal_url, query=query, limit=limit, offset=offset)
        )
        return [shape_hub_dataset(f) for f in raw.get("features", [])]

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetcher)


async def fetch_get_dataset_details(
    portal_key: str,
    dataset_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch details for a specific dataset by its Hub Search ID.

    Args:
        portal_key: One of the 10 keys in PORTAL_URLS.
        dataset_id: Dataset identifier to search for.
        lang: Response language.

    Returns:
        (shaped dataset dict, was_cached)

    Raises:
        NoPortalError: If the portal_key maps to None.
        ValueError: If no dataset is found with the given ID.
    """
    portal_url = _require_portal(portal_key)
    cache_key = f"york_region:dataset:{portal_key}:{dataset_id}"

    async def _fetcher() -> dict[str, Any]:
        raw = await _rate_limited_call(
            lambda: search_hub_datasets(portal_url, query=dataset_id, limit=1)
        )
        features = raw.get("features", [])
        if not features:
            raise ValueError(f"dataset not found: {dataset_id}")
        return shape_hub_dataset(features[0])

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetcher)


async def fetch_query_features(
    portal_key: str,
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 5000,
) -> tuple[dict[str, Any], bool]:
    """Query a FeatureServer layer and return results with pagination info.

    Args:
        portal_key: Portal context (used in cache key, not for URL validation).
        service_url: Full FeatureServer base URL (without layer id).
        layer_id: Layer/table index (0-based).
        where: SQL-92 WHERE clause.
        out_fields: Comma-separated fields or "*" for all.
        include_geometry: Include GeoJSON geometry in results.
        max_records: Max total records to return (cap: 5000).

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(
        service_url,
        layer_id,
        where=where,
        out_fields=out_fields,
        include_geometry=include_geometry,
        max_records=max_records,
    )


async def fetch_list_organizations(
    portal_key: str,
    lang: str = "en",
) -> tuple[list[str], bool]:
    """List all unique dataset owners in a portal.

    Args:
        portal_key: One of the 10 keys in PORTAL_URLS.
        lang: Response language.

    Returns:
        (sorted list of unique owner strings, was_cached)

    Raises:
        NoPortalError: If the portal_key maps to None.
    """
    portal_url = _require_portal(portal_key)
    cache_key = f"york_region:orgs:{portal_key}"

    async def _fetcher() -> list[str]:
        raw = await _rate_limited_call(
            lambda: search_hub_datasets(portal_url, query="", limit=100)
        )
        owners = {
            f.get("properties", {}).get("owner")
            for f in raw.get("features", [])
        }
        return sorted(o for o in owners if o)

    return await cached_fetch(cache_key, CACHE_TTL_ORGS, _fetcher)


async def fetch_list_categories(
    portal_key: str,
    lang: str = "en",
) -> tuple[list[str], bool]:
    """List all unique dataset categories in a portal.

    Args:
        portal_key: One of the 10 keys in PORTAL_URLS.
        lang: Response language.

    Returns:
        (sorted list of unique category strings, was_cached)

    Raises:
        NoPortalError: If the portal_key maps to None.
    """
    portal_url = _require_portal(portal_key)
    cache_key = f"york_region:categories:{portal_key}"

    async def _fetcher() -> list[str]:
        raw = await _rate_limited_call(
            lambda: search_hub_datasets(portal_url, query="", limit=100)
        )
        all_cats: set[str] = set()
        for feature in raw.get("features", []):
            cats = feature.get("properties", {}).get("categories") or []
            all_cats.update(cats)
        return sorted(all_cats)

    return await cached_fetch(cache_key, CACHE_TTL_ORGS, _fetcher)


# ---------------------------------------------------------------------------
# Curated York Region helpers
# ---------------------------------------------------------------------------


async def fetch_transit_stops(
    query: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch YRT/Viva bus stops from the York Region Transportation FeatureServer.

    Args:
        query: Optional stop name filter (LIKE match, case-insensitive pattern).
        include_geometry: Include point geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    # UPPER() on both sides: the ArcGIS attribute data is stored uppercase, so a
    # raw LIKE silently drops rows for any mixed-case query (Phase 20.1).
    where = (
        f"UPPER(STOP_NAME) LIKE '%{_escape_where_value(query).upper()}%'"
        if query else "1=1"
    )
    return await _fetch_features(YR_TRANSIT_FS, YR_BUS_STOPS_LAYER, where=where, include_geometry=include_geometry)


async def fetch_transit_routes(
    route_short_name: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch YRT/Viva bus routes from the York Region Transportation FeatureServer.

    Args:
        route_short_name: Optional route short name filter (exact match).
        include_geometry: Include linestring geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = f"ROUTE_SHORT_NAME = '{_escape_where_value(route_short_name)}'" if route_short_name else "1=1"
    return await _fetch_features(YR_TRANSIT_FS, YR_BUS_ROUTES_LAYER, where=where, include_geometry=include_geometry)


async def fetch_regional_roads(include_geometry: bool = False) -> tuple[dict[str, Any], bool]:
    """Fetch the York Region regional road network (layer 0).

    Args:
        include_geometry: Include linestring geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(YR_TRANSIT_FS, YR_REGIONAL_ROADS_LAYER, include_geometry=include_geometry)


async def fetch_beach_water_testing(include_geometry: bool = False) -> tuple[dict[str, Any], bool]:
    """Fetch York Region beach water testing results.

    Args:
        include_geometry: Include point geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(YR_HEALTH_FS, YR_BEACH_TESTING_LAYER, include_geometry=include_geometry)


async def fetch_hospitals(include_geometry: bool = False) -> tuple[dict[str, Any], bool]:
    """Fetch York Region hospital locations.

    Args:
        include_geometry: Include point geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(YR_HEALTH_FS, YR_HOSPITAL_LAYER, include_geometry=include_geometry)


async def fetch_drinking_water_incidents(include_geometry: bool = False) -> tuple[dict[str, Any], bool]:
    """Fetch York Region drinking water adverse incidents.

    Args:
        include_geometry: Include geometry in results if available.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(YR_DRINKING_WATER_FS, YR_DRINKING_WATER_ADVERSE_LAYER, include_geometry=include_geometry)


async def fetch_solid_waste_sites(include_geometry: bool = False) -> tuple[dict[str, Any], bool]:
    """Fetch York Region solid waste site locations.

    Args:
        include_geometry: Include point geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    return await _fetch_features(YR_ENVIRONMENTAL_FS, YR_SOLID_WASTE_SITES_LAYER, include_geometry=include_geometry)


async def fetch_census_age_sex(
    csdname: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch York Region 2021 Census age and sex data by Dissemination Area.

    Uses a focused field set (10 fields) to avoid returning all 364 census fields.

    Args:
        csdname: Optional Census Subdivision name filter (e.g., "Markham", "Newmarket").
        include_geometry: Include polygon geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = f"CSDNAME = '{_escape_where_value(csdname)}'" if csdname else "1=1"
    return await _fetch_features(
        YR_AGE_SEX_FS, YR_CENSUS_LAYER, where=where, out_fields=YR_CENSUS_AGE_FIELDS, include_geometry=include_geometry
    )


async def fetch_census_income(
    csdname: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch York Region 2021 Census total income data by Dissemination Area.

    Args:
        csdname: Optional Census Subdivision name filter.
        include_geometry: Include polygon geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = f"CSDNAME = '{_escape_where_value(csdname)}'" if csdname else "1=1"
    return await _fetch_features(
        YR_INCOME_FS, YR_CENSUS_LAYER, where=where, out_fields=YR_CENSUS_INCOME_FIELDS, include_geometry=include_geometry
    )


async def fetch_waste_diversion(
    year: int | None = None,
) -> tuple[dict[str, Any], bool]:
    """Fetch York Region annual waste diversion statistics (2010-2021 tonnage data).

    Args:
        year: Optional year filter (e.g., 2021). Returns all years if None.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = f"YEAR = {year}" if year is not None else "1=1"
    return await _fetch_features(YR_WASTE_DIVERSION_FS, YR_CENSUS_LAYER, where=where)


# ---------------------------------------------------------------------------
# Curated Markham helpers
# ---------------------------------------------------------------------------


async def fetch_markham_addresses(
    street: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch Markham civic addresses.

    Args:
        street: Optional street name filter (LIKE match).
        include_geometry: Include point geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = (
        f"UPPER(STREET) LIKE '%{_escape_where_value(street).upper()}%'"
        if street else "1=1"
    )
    return await _fetch_features(MARKHAM_ADDRESSES_FS, MARKHAM_ADDRESSES_LAYER, where=where, include_geometry=include_geometry)


async def fetch_markham_roads(
    name: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fetch Markham road network (SLRN).

    Args:
        name: Optional road name filter (LIKE match).
        include_geometry: Include linestring geometry in results.

    Returns:
        ({"features": [...], "count": int, "truncated": bool}, was_cached)
    """
    where = (
        f"UPPER(NAME) LIKE '%{_escape_where_value(name).upper()}%'"
        if name else "1=1"
    )
    return await _fetch_features(MARKHAM_ROADS_FS, MARKHAM_ROADS_LAYER, where=where, include_geometry=include_geometry)
