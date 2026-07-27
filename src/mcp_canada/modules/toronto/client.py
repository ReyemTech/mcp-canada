"""Toronto Open Data API client for the toronto module.

Provides async functions for fetching, shaping, caching, and rate-limiting
all Toronto CKAN and datastore API endpoints. All public functions return
(data, was_cached) tuples.

CKAN response envelope: {"success": true, "result": ...}
For package_search: result = {"count": N, "results": [...]}
For datastore_search: result = {"records": [...], "total": N}
"""

from __future__ import annotations

import zipfile
from io import BytesIO
from typing import Any

import httpx

from mcp_canada.modules.toronto.constants import (
    BASE_URL,
    CACHE_TTL_DATA,
    CACHE_TTL_GTFS,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    GTFS_DATASET_ID,
    MAX_DESCRIPTION_CHARS,
    MAX_RESOURCES,
    NEIGHBOURHOOD_PROFILES_RESOURCE_ID,
    RATE_GROUP,
    RATE_LIMIT,
    RENTSAFE_EVAL_RESOURCE_ID,
    SERVICE_REQUESTS_DATASET_ID,
    SHORT_TERM_RENTALS_RESOURCE_ID,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.parsers import _parse_csv
from mcp_canada.shared.rate_limiter import get_limiter
from mcp_canada.shared.errors import UpstreamData


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _truncate(text: str | None, max_chars: int = MAX_DESCRIPTION_CHARS) -> str | None:
    """Truncate a string to max_chars, appending '...' if truncated."""
    if text is None:
        return None
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _limit_resources(
    resources: list[dict[str, Any]],
    max_count: int = MAX_RESOURCES,
) -> list[dict[str, Any]]:
    """Cap a resources list to the first max_count entries."""
    return resources[:max_count]


def _shape_resource(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract key fields from a raw CKAN resource dict.

    Includes datastore_active flag to indicate whether the resource is queryable
    via the datastore API.
    """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "format": raw.get("format"),
        "size": raw.get("size"),
        "url": raw.get("url"),
        "datastore_active": raw.get("datastore_active", False),
    }


def _shape_dataset(raw: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    """Shape a raw Toronto CKAN dataset dict for token-efficient agent consumption.

    Toronto datasets use plain title/notes fields (no title_translated), with
    bilingual variants sometimes in extras. Falls back gracefully.
    """
    title = raw.get("title")
    description = _truncate(raw.get("notes"))

    raw_resources: list[dict[str, Any]] = raw.get("resources") or []
    num_resources_total = len(raw_resources)
    limited_resources = [_shape_resource(r) for r in _limit_resources(raw_resources)]

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "title": title,
        "description": description,
        "organization": raw.get("organization"),
        "num_resources": num_resources_total,
        "tags": raw.get("tags"),
        "resources": limited_resources,
        "metadata_created": raw.get("metadata_created"),
        "metadata_modified": raw.get("metadata_modified"),
    }


def _build_cache_key(path: str, params: dict[str, Any]) -> str:
    """Build a deterministic cache key from path and sorted params."""
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"toronto:{path}?{sorted_params}"


async def _api_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Toronto CKAN API with caching, rate limiting, envelope unwrapping.

    CKAN always returns {"success": true, "result": ...}. Returns result directly.
    """
    url = BASE_URL + path
    cache_key = _build_cache_key(path, params)
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            envelope = response.json()
            return envelope["result"]

    return await cached_fetch(cache_key, cache_ttl, fetcher)


# ---------------------------------------------------------------------------
# CKAN discovery functions
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str,
    fq: str | None = None,
    rows: int = 10,
    start: int = 0,
    sort: str = "relevance asc",
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """Search Toronto CKAN datasets by keyword with optional filter query.

    Args:
        query: Solr search query string (q param).
        fq: Optional filter query (e.g. 'tags:transit' or 'organization:ttc').
        rows: Number of results to return.
        start: Offset for pagination.
        sort: Sort order string.
        lang: Language for shaping results ('en' or 'fr').

    Returns:
        (list of shaped dataset dicts, was_cached)
    """
    params: dict[str, Any] = {
        "q": query,
        "rows": rows,
        "start": start,
        "sort": sort,
    }
    if fq is not None:
        params["fq"] = fq

    result, was_cached = await _api_get("action/package_search", params, CACHE_TTL_SEARCH)
    datasets = result.get("results", [])
    return [_shape_dataset(d, lang=lang) for d in datasets], was_cached


async def fetch_dataset_details(
    dataset_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full details for a single Toronto dataset, shaped and truncated.

    Args:
        dataset_id: CKAN dataset ID or name slug.
        lang: Language for shaping results ('en' or 'fr').

    Returns:
        (shaped dataset dict, was_cached)
    """
    params: dict[str, Any] = {"id": dataset_id}
    result, was_cached = await _api_get("action/package_show", params, CACHE_TTL_SEARCH)
    return _shape_dataset(result, lang=lang), was_cached


async def fetch_organizations(
    all_fields: bool = True,
    sort: str = "name asc",
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch list of Toronto CKAN organizations (city divisions and agencies).

    Args:
        all_fields: If True, include full org details.
        sort: Sort order string.

    Returns:
        (list of organization dicts, was_cached)
    """
    params: dict[str, Any] = {
        "all_fields": all_fields,
        "sort": sort,
    }
    result, was_cached = await _api_get("action/organization_list", params, CACHE_TTL_META)
    return result, was_cached


async def fetch_resource(
    resource_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch details for a specific Toronto resource by ID.

    Args:
        resource_id: CKAN resource UUID.

    Returns:
        (shaped resource dict, was_cached)
    """
    params: dict[str, Any] = {"id": resource_id}
    result, was_cached = await _api_get("action/resource_show", params, CACHE_TTL_SEARCH)
    return _shape_resource(result), was_cached


async def fetch_dataset_count() -> tuple[int, bool]:
    """Fetch total number of datasets in the Toronto Open Data Catalogue.

    Uses package_search with rows=0 to get only the count.

    Returns:
        (total dataset count, was_cached)
    """
    params: dict[str, Any] = {"q": "*:*", "rows": 0}
    result, was_cached = await _api_get("action/package_search", params, CACHE_TTL_META)
    return result.get("count", 0), was_cached


# ---------------------------------------------------------------------------
# GTFS functions
# ---------------------------------------------------------------------------


async def _resolve_gtfs_zip_url(package: dict[str, Any]) -> str:
    """Pick the GTFS ZIP resource URL out of a CKAN package_show result.

    The URL is resolved rather than pinned: the previous hardcoded constant
    embedded a resource id and filename that Toronto later changed, leaving both
    TTC tools returning 404 behind an UPSTREAM_ERROR (Phase 20.1).
    """
    for resource in package.get("resources") or []:
        if str(resource.get("format", "")).upper() == "ZIP" and resource.get("url"):
            return str(resource["url"])
    raise UpstreamData(
        "TTC GTFS package exposes no ZIP resource — Toronto Open Data may have "
        f"restructured the dataset. Resources: "
        f"{[r.get('format') for r in package.get('resources') or []]}"
    )


async def fetch_gtfs_file(
    filename: str,
    ttl: int = CACHE_TTL_GTFS,
) -> tuple[list[dict[str, Any]], bool]:
    """Download the TTC GTFS ZIP and extract a named .txt file.

    The GTFS ZIP is ~35.9 MB. Uses a 120-second timeout to accommodate
    download time on slow connections. The extracted file is parsed as CSV.

    Args:
        filename: Name of the GTFS file to extract (e.g. 'stops.txt', 'routes.txt').
        ttl: Cache TTL in seconds (default: CACHE_TTL_GTFS = 6 hours).

    Returns:
        (list of row dicts from the extracted CSV file, was_cached)
    """
    cache_key = f"toronto:gtfs:{filename}"
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> list[dict[str, Any]]:
        package, _ = await _api_get(
            "action/package_show", {"id": GTFS_DATASET_ID}, CACHE_TTL_GTFS
        )
        zip_url = await _resolve_gtfs_zip_url(package)

        await limiter.acquire()
        async with httpx.AsyncClient(timeout=120.0) as http:
            response = await http.get(zip_url, follow_redirects=True)
            response.raise_for_status()
            zip_bytes = response.content

        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            with zf.open(filename) as f:
                csv_bytes = f.read()

        return _parse_csv(csv_bytes)

    return await cached_fetch(cache_key, ttl, fetcher)


async def fetch_gtfs_stops(
    query: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch TTC GTFS stops, optionally filtered by stop_name substring.

    Args:
        query: Optional substring to filter stops by stop_name (case-insensitive).

    Returns:
        (list of stop dicts, was_cached)
    """
    stops, was_cached = await fetch_gtfs_file("stops.txt")
    if query:
        q_lower = query.lower()
        stops = [s for s in stops if q_lower in (s.get("stop_name") or "").lower()]
    return stops, was_cached


async def fetch_gtfs_routes(
    route_type: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch TTC GTFS routes, optionally filtered by route_type.

    Route types: 0=Tram/Streetcar, 1=Subway/Metro, 2=Rail, 3=Bus.

    Args:
        route_type: Optional GTFS route_type string to filter (e.g. '0', '1', '3').

    Returns:
        (list of route dicts, was_cached)
    """
    routes, was_cached = await fetch_gtfs_file("routes.txt")
    if route_type is not None:
        routes = [r for r in routes if str(r.get("route_type", "")) == str(route_type)]
    return routes, was_cached


# ---------------------------------------------------------------------------
# Datastore helper
# ---------------------------------------------------------------------------


async def fetch_datastore_records(
    resource_id: str,
    filters: dict[str, Any] | None = None,
    limit: int = 100,
    offset: int = 0,
    fields: list[str] | None = None,
    sort: str | None = None,
    q: str | None = None,
    cache_ttl: int = CACHE_TTL_DATA,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch records from the Toronto CKAN datastore_search action.

    Args:
        resource_id: CKAN resource UUID with datastore_active=True.
        filters: Optional dict of exact-match filters (e.g. {"status": "Active"}).
        limit: Maximum number of records to return (default: 100).
        offset: Pagination offset (default: 0).
        fields: Optional list of field names to include in response.
        sort: Optional sort field (e.g. "SCORE desc").
        q: Optional full-text search query string.
        cache_ttl: Cache TTL in seconds.

    Returns:
        (list of record dicts, was_cached)
    """
    params: dict[str, Any] = {
        "resource_id": resource_id,
        "limit": limit,
        "offset": offset,
    }
    if filters:
        import json
        params["filters"] = json.dumps(filters)
    if fields:
        params["fields"] = ",".join(fields)
    if sort:
        params["sort"] = sort
    if q:
        params["q"] = q

    result, was_cached = await _api_get("action/datastore_search", params, cache_ttl)
    return result.get("records", []), was_cached


# ---------------------------------------------------------------------------
# Neighbourhood profile functions
# ---------------------------------------------------------------------------


async def fetch_neighbourhood_profile(
    neighbourhood: str | None = None,
    characteristic: str | None = None,
    limit: int = 100,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch neighbourhood profile records from the 2016 Census datastore resource.

    The neighbourhood profile resource uses an indicator-per-row model: each row
    is one Characteristic, with neighbourhood names as column headers. Use the
    'Characteristic' column to filter indicators, or neighbourhood name columns
    to look up specific area data.

    Args:
        neighbourhood: Optional neighbourhood name (column header) to include in response.
            NOTE: All neighbourhood columns are always returned; this param is informational.
        characteristic: Optional substring to filter rows by 'Characteristic' column.
        limit: Maximum number of records (default: 100).

    Returns:
        (list of profile row dicts, was_cached)
    """
    return await fetch_datastore_records(
        resource_id=NEIGHBOURHOOD_PROFILES_RESOURCE_ID,
        q=characteristic,
        limit=limit,
        cache_ttl=CACHE_TTL_DATA,
    )


async def fetch_neighbourhood_comparison(
    characteristic: str,
    limit: int = 10,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch neighbourhood profile rows for a specific Characteristic.

    Returns the row(s) matching the given Characteristic value, which contains
    all neighbourhood values as columns — enabling cross-neighbourhood comparison.

    Args:
        characteristic: Exact or partial Characteristic string to search for.
        limit: Maximum number of matching rows to return (default: 10).

    Returns:
        (list of profile row dicts, was_cached)
    """
    return await fetch_datastore_records(
        resource_id=NEIGHBOURHOOD_PROFILES_RESOURCE_ID,
        q=characteristic,
        limit=limit,
        cache_ttl=CACHE_TTL_DATA,
    )


# ---------------------------------------------------------------------------
# 311 Service Requests
# ---------------------------------------------------------------------------


async def fetch_311_requests(
    year: int,
    ward: str | None = None,
    service_type: str | None = None,
    status: str | None = None,
    limit: int = 500,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch 311 service requests for a given year from the annual ZIP+CSV resource.

    Discovers the year-specific ZIP URL from package_show, downloads and parses
    the ZIP+CSV, then applies client-side filters. Results for each year are
    cached by year key.

    Args:
        year: Year of 311 data to fetch (e.g. 2023).
        ward: Optional ward name substring filter (case-insensitive).
        service_type: Optional service type substring filter (case-insensitive).
        status: Optional status exact filter (e.g. 'Open', 'Closed').
        limit: Maximum number of records to return after filtering (default: 500).

    Returns:
        (list of service request dicts, was_cached)
    """
    cache_key = f"toronto:311:{year}"
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> list[dict[str, Any]]:
        # Step 1: Discover ZIP URL from package_show
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            pkg_response = await http.get(
                BASE_URL + "action/package_show",
                params={"id": SERVICE_REQUESTS_DATASET_ID},
            )
            pkg_response.raise_for_status()
            pkg_data = pkg_response.json()["result"]

        # Find the resource whose name matches the year (e.g. "2023.zip" or contains str(year))
        resources = pkg_data.get("resources", [])
        zip_url: str | None = None
        for resource in resources:
            name = (resource.get("name") or "").lower()
            url = resource.get("url") or ""
            if str(year) in name or str(year) in url:
                zip_url = url
                break

        if not zip_url:
            # Fallback: use the first ZIP resource
            for resource in resources:
                fmt = (resource.get("format") or "").upper()
                if fmt == "ZIP":
                    zip_url = resource.get("url")
                    break

        if not zip_url:
            return []

        # Step 2: Download and parse ZIP+CSV
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=120.0) as http:
            zip_response = await http.get(zip_url)
            zip_response.raise_for_status()
            zip_bytes = zip_response.content

        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            # Find the CSV file inside the ZIP
            csv_filename = next(
                (name for name in zf.namelist() if name.endswith(".csv")),
                None,
            )
            if not csv_filename:
                return []
            with zf.open(csv_filename) as f:
                csv_bytes = f.read()

        return _parse_csv(csv_bytes)

    all_rows, was_cached = await cached_fetch(cache_key, CACHE_TTL_DATA, fetcher)

    # Apply client-side filters
    rows = all_rows
    if ward:
        ward_lower = ward.lower()
        rows = [r for r in rows if ward_lower in str(r.get("ward", "")).lower()]
    if service_type:
        svc_lower = service_type.lower()
        rows = [
            r for r in rows
            if svc_lower in str(r.get("service_request_type", r.get("type", ""))).lower()
        ]
    if status:
        rows = [r for r in rows if r.get("status", "").lower() == status.lower()]

    return rows[:limit], was_cached


# ---------------------------------------------------------------------------
# Housing functions
# ---------------------------------------------------------------------------


async def fetch_rentsafe_evaluations(
    ward: str | None = None,
    min_score: int | None = None,
    limit: int = 100,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch RentSafeTO apartment building evaluation records.

    Calls datastore_search for the RentSafeTO resource, optionally filtering by
    ward and applying a min_score filter client-side.

    Args:
        ward: Optional ward name filter (exact match on WARDNAME field).
        min_score: Optional minimum evaluation score filter (applied client-side).
        limit: Maximum number of records to return (default: 100).

    Returns:
        (list of evaluation dicts, was_cached)
    """
    filters: dict[str, Any] = {}
    if ward:
        filters["WARDNAME"] = ward

    records, was_cached = await fetch_datastore_records(
        resource_id=RENTSAFE_EVAL_RESOURCE_ID,
        filters=filters if filters else None,
        limit=limit,
        cache_ttl=CACHE_TTL_DATA,
    )

    # Apply client-side min_score filter
    if min_score is not None:
        records = [
            r for r in records
            if _safe_int(r.get("SCORE")) >= min_score
        ]

    return records, was_cached


async def fetch_short_term_rentals(
    ward: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch short-term rental (Airbnb-style) operator registration records.

    Calls datastore_search for the STR resource with optional ward and status filters.

    Args:
        ward: Optional ward filter (applied via CKAN filter).
        status: Optional registration status filter (e.g. 'Active', 'Cancelled').
        limit: Maximum number of records to return (default: 100).

    Returns:
        (list of STR registration dicts, was_cached)
    """
    filters: dict[str, Any] = {}
    if ward:
        filters["ward"] = ward

    records, was_cached = await fetch_datastore_records(
        resource_id=SHORT_TERM_RENTALS_RESOURCE_ID,
        filters=filters if filters else None,
        limit=limit,
        cache_ttl=CACHE_TTL_DATA,
    )

    # Apply client-side status filter (field name may vary)
    if status:
        records = [
            r for r in records
            if r.get("status", "") == status
        ]

    return records, was_cached


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------


def _safe_int(value: Any) -> int:
    """Convert a value to int safely, returning 0 on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
