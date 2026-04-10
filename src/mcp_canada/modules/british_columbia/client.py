"""British Columbia open data client.

Provides async functions for fetching, shaping, caching, and rate-limiting
all BC CKAN and WFS endpoints. All public functions return (data, was_cached)
tuples and delegate to shared/cache.py + shared/rate_limiter.py + shared/ogc.py.

CKAN response envelope: {"success": true, "result": ...}
For package_search: result = {"count": N, "results": [...]}
For package_show:   result = {<dataset dict>}
"""

from __future__ import annotations

from typing import Any

import httpx  # noqa: F401 — used in _api_get and tests

from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.ogc import WfsError, wfs_page_all  # noqa: F401 — used by Plan 03
from mcp_canada.shared.parsers import fetch_and_parse  # noqa: F401 — used by Plan 02 via tools
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    BASE_URL,
    CACHE_TTL_ACTIVE,  # noqa: F401 — used by Plan 03
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    CACHE_TTL_STATIC,
    MAX_RECORDS,
    RATE_GROUP_CKAN,
    RATE_GROUP_WFS,  # noqa: F401 — used by Plan 03
    RATE_LIMIT_CKAN,
    RATE_LIMIT_WFS,  # noqa: F401 — used by Plan 03
    WFS_BASE_URL,  # noqa: F401 — used by Plan 03
    WFS_PAGE_SIZE,  # noqa: F401 — used by Plan 03
)

__all__ = [
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_organizations",
    "fetch_tags",
    "_compute_queryable_via_wfs",
    "_wfs_fetch",
]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch from BC Data Catalogue CKAN API and unwrap the CKAN success envelope.

    CKAN always returns {"success": true, "result": ...}. Raises
    httpx.HTTPStatusError on non-200 responses or on CKAN success=False.

    Args:
        path: Action API path (e.g. "package_search") relative to BASE_URL.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN result field.
    """
    url = BASE_URL + path
    response = await api_get(url, params or {})
    response.raise_for_status()
    envelope = response.json()
    if not envelope.get("success", False):
        raise httpx.HTTPStatusError(
            f"CKAN returned success=False for {path}",
            request=response.request,
            response=response,
        )
    return envelope.get("result", {})


def _compute_queryable_via_wfs(resources: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Determine whether a dataset is WFS-queryable from its resource metadata.

    A resource is WFS-queryable (BC Geographic Warehouse layer) when all three
    conditions hold:
      - bcdc_type == "geographic"
      - resource_storage_location == "bc geographic warehouse"
      - object_name is truthy (non-empty string)

    Returns the (True, object_name) for the first matching resource, or
    (False, None) if no resource qualifies.

    Args:
        resources: List of CKAN resource dicts from a package_show result.

    Returns:
        (queryable, object_name) tuple.
    """
    for resource in resources:
        if (
            resource.get("bcdc_type") == "geographic"
            and resource.get("resource_storage_location") == "bc geographic warehouse"
            and bool(resource.get("object_name"))
        ):
            return True, resource["object_name"]
    return False, None


def _shape_resource(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract key fields from a raw CKAN resource dict for BC datasets.

    Args:
        raw: Raw resource dict from BC CKAN API.

    Returns:
        Flat dict with routing-relevant fields.
    """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "format": raw.get("format"),
        "url": raw.get("url"),
        "bcdc_type": raw.get("bcdc_type"),
        "object_name": raw.get("object_name"),
        "resource_storage_location": raw.get("resource_storage_location"),
        "resource_type": raw.get("resource_type"),
    }


def _shape_summary(raw: dict[str, Any]) -> dict[str, Any]:
    """Shape a raw BC CKAN dataset into a flat summary dict for search results.

    Extracts the organization name from the nested organization object.

    Args:
        raw: Raw package dict from CKAN package_search results list.

    Returns:
        Flat summary with: id, name, title, notes, organization,
        bcdc_type, metadata_modified, resources_count.
    """
    org = raw.get("organization") or {}
    org_name = org.get("name") if isinstance(org, dict) else str(org)
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "title": raw.get("title"),
        "notes": raw.get("notes"),
        "organization": org_name,
        "bcdc_type": raw.get("bcdc_type"),
        "metadata_modified": raw.get("metadata_modified"),
        "resources_count": len(raw.get("resources") or []),
    }


# ---------------------------------------------------------------------------
# CKAN Discovery functions
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    q: str = "",
    rows: int = 20,
    start: int = 0,
    fq: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Search BC Data Catalogue via CKAN package_search.

    Args:
        q: Full-text search query string.
        rows: Number of results (default 20, max 1000).
        start: Pagination offset (default 0).
        fq: Optional filter query (e.g. "organization:bc-wildfire-service").

    Returns:
        (list of summary dicts, was_cached)
    """
    params: dict[str, Any] = {"q": q, "rows": rows, "start": start}
    if fq is not None:
        params["fq"] = fq

    cache_key = f"bc:search:{q}:{rows}:{start}:{fq or 'none'}"
    limiter = get_limiter(RATE_GROUP_CKAN, rate=RATE_LIMIT_CKAN)

    async def fetcher() -> list[dict[str, Any]]:
        await limiter.acquire()
        result = await _api_get("package_search", params)
        datasets = result.get("results", [])
        return [_shape_summary(d) for d in datasets]

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_dataset_details(
    package_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch full dataset metadata via CKAN package_show, including resources.

    Derives queryable_via_wfs flag and surfaces object_name at the top level
    based on the bcdc_type + resource_storage_location + object_name conditions
    from RESEARCH.md.

    Args:
        package_id: CKAN dataset ID or name slug.

    Returns:
        (details dict with queryable_via_wfs and object_name, was_cached)

    Raises:
        httpx.HTTPStatusError: On 404 or other HTTP errors.
    """
    cache_key = f"bc:details:{package_id}"
    limiter = get_limiter(RATE_GROUP_CKAN, rate=RATE_LIMIT_CKAN)

    async def fetcher() -> dict[str, Any]:
        await limiter.acquire()
        result = await _api_get("package_show", {"id": package_id})

        raw_resources = result.get("resources") or []
        queryable_via_wfs, object_name = _compute_queryable_via_wfs(raw_resources)

        # Find projection_name from the first geographic resource, if any
        projection = None
        for r in raw_resources:
            if r.get("bcdc_type") == "geographic" and r.get("projection_name"):
                projection = r.get("projection_name")
                break

        # Flatten tags to list of name strings
        tags = [t.get("name") for t in (result.get("tags") or []) if t.get("name")]

        # Flatten organization
        org = result.get("organization") or {}
        org_name = org.get("name") if isinstance(org, dict) else str(org)

        return {
            "id": result.get("id"),
            "name": result.get("name"),
            "title": result.get("title"),
            "notes": result.get("notes"),
            "organization": org_name,
            "resources": [_shape_resource(r) for r in raw_resources],
            "object_name": object_name,
            "queryable_via_wfs": queryable_via_wfs,
            "projection": projection,
            "tags": tags,
            "metadata_modified": result.get("metadata_modified"),
        }

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_organizations() -> tuple[list[dict[str, Any]], bool]:
    """List all BC Data Catalogue organizations (ministries, agencies).

    Returns:
        (list of organization dicts or name strings, was_cached)
    """
    cache_key = "bc:orgs"
    limiter = get_limiter(RATE_GROUP_CKAN, rate=RATE_LIMIT_CKAN)

    async def fetcher() -> list[Any]:
        await limiter.acquire()
        return await _api_get("organization_list", {"all_fields": "true"})

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_tags() -> tuple[list[str], bool]:
    """List all BC Data Catalogue tags for subject-area discovery.

    Returns:
        (list of tag name strings, was_cached)
    """
    cache_key = "bc:tags"
    limiter = get_limiter(RATE_GROUP_CKAN, rate=RATE_LIMIT_CKAN)

    async def fetcher() -> list[str]:
        await limiter.acquire()
        result = await _api_get("tag_list")
        # tag_list returns a list of name strings directly
        if isinstance(result, list):
            return result
        return []

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


# ---------------------------------------------------------------------------
# WFS Feature Fetch — implemented in Plan 03
# ---------------------------------------------------------------------------


async def _wfs_fetch(
    layer: str,
    cql: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    ttl: int = CACHE_TTL_STATIC,
) -> tuple[dict[str, Any], bool]:
    """Fetch features from a BCGW WFS layer with caching and rate limiting.

    Plan 03 implements this function body. Returns
    {"features": [...], "count": N, "truncated": bool} tuple.
    """
    raise NotImplementedError("Plan 03 will implement _wfs_fetch")
