"""Ontario Open Data API client for the ontario module.

Provides async functions for fetching, shaping, caching, and rate-limiting
all Ontario CKAN API endpoints. All public functions return (data, was_cached) tuples.

CKAN response envelope: {"success": true, "result": ...}
For package_search: result = {"count": N, "results": [...]}
For other actions: result = <data>
"""

from typing import Any

import httpx

from mcp_canada.modules.ontario.constants import (
    BASE_URL,
    CACHE_TTL_DATA,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    MAX_DESCRIPTION_CHARS,
    MAX_RESOURCES,
    POPULATION_PROJECTIONS_RESOURCE_URL,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.parsers import fetch_and_parse
from mcp_canada.shared.rate_limiter import get_limiter


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _truncate(text: str | None, max_chars: int = MAX_DESCRIPTION_CHARS) -> str | None:
    """Truncate a string to max_chars, appending '...' if truncated.

    Args:
        text: Input string, or None.
        max_chars: Maximum number of characters before truncation.

    Returns:
        Original string if within limit, truncated string with '...' suffix if
        over limit, or None if input is None.
    """
    if text is None:
        return None
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _limit_resources(
    resources: list[dict[str, Any]],
    max_count: int = MAX_RESOURCES,
) -> list[dict[str, Any]]:
    """Cap a resources list to the first max_count entries.

    Args:
        resources: List of resource dicts from CKAN.
        max_count: Maximum number of resources to return.

    Returns:
        First max_count items (or all if fewer exist).
    """
    return resources[:max_count]


def _shape_resource(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract key fields from a raw CKAN resource dict.

    Args:
        raw: Raw resource dict from Ontario CKAN API.

    Returns:
        Dict with id, name, format, size, url fields.
    """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "format": raw.get("format"),
        "size": raw.get("size"),
        "url": raw.get("url"),
    }


def _shape_dataset(raw: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    """Shape a raw Ontario CKAN dataset dict for token-efficient agent consumption.

    Extracts bilingual title/description from title_translated/notes_translated
    with fallback to 'en' then to the raw title field. Truncates descriptions
    and limits resources.

    Args:
        raw: Raw dataset dict from Ontario CKAN package_show or package_search result.
        lang: Language code ('en' or 'fr').

    Returns:
        Shaped dict with id, name, title, description, organization,
        num_resources (total), tags, resources (capped), metadata timestamps.
    """
    # Extract bilingual title
    title_translated: dict[str, str] | None = raw.get("title_translated")
    if title_translated:
        title = title_translated.get(lang) or title_translated.get("en") or raw.get("title")
    else:
        title = raw.get("title")

    # Extract bilingual description
    notes_translated: dict[str, str] | None = raw.get("notes_translated")
    if notes_translated:
        description = notes_translated.get(lang) or notes_translated.get("en") or raw.get("notes")
    else:
        description = raw.get("notes")

    description = _truncate(description)

    # Resources: record total count, then cap
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
    """Build a deterministic cache key from path and sorted params.

    Args:
        path: CKAN action API path (e.g. 'action/package_search').
        params: Query parameters dict.

    Returns:
        Cache key string with 'ontario:' prefix.
    """
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"ontario:{path}?{sorted_params}"


async def _api_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Ontario CKAN API with caching, rate limiting, and envelope unwrapping.

    CKAN always returns {"success": true, "result": ...}. This function
    returns result directly.

    Args:
        path: Action API path relative to BASE_URL (e.g. 'action/package_search').
        params: Query parameters dict.
        cache_ttl: Cache TTL in seconds.

    Returns:
        (result, was_cached) — result is the unwrapped CKAN result field.
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
# Public fetch functions
# ---------------------------------------------------------------------------

async def fetch_search_datasets(
    query: str,
    fq: str | None = None,
    rows: int = 10,
    start: int = 0,
    sort: str = "relevance asc",
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """Search Ontario CKAN datasets by keyword with optional filter query.

    Args:
        query: Solr search query string (q param).
        fq: Optional filter query (e.g. 'tags:population' or 'organization:finance').
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
    """Fetch full details for a single Ontario dataset, shaped and truncated.

    Args:
        dataset_id: CKAN dataset ID or name slug.
        lang: Language for bilingual field extraction ('en' or 'fr').

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
    """Fetch list of Ontario CKAN organizations (ministries and agencies).

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
    """Fetch details for a specific Ontario resource by ID.

    Args:
        resource_id: CKAN resource UUID.

    Returns:
        (resource dict, was_cached)
    """
    params: dict[str, Any] = {"id": resource_id}
    result, was_cached = await _api_get("action/resource_show", params, CACHE_TTL_SEARCH)
    return _shape_resource(result), was_cached


async def fetch_dataset_count() -> tuple[int, bool]:
    """Fetch total number of datasets in the Ontario Open Data Catalogue.

    Uses package_search with rows=0 to get only the count.

    Returns:
        (total dataset count, was_cached)
    """
    params: dict[str, Any] = {"q": "*:*", "rows": 0}
    result, was_cached = await _api_get("action/package_search", params, CACHE_TTL_META)
    return result.get("count", 0), was_cached


async def fetch_population_projections(
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch Ontario population projections from the Ministry of Finance XLSX.

    Parses the official Ontario MoF population projections dataset (2024–2051)
    from the direct XLSX download URL. Results are cached for 24 hours.

    Args:
        lang: Language code ('en' or 'fr'). Currently only an English XLSX is
              available; this parameter is accepted for API consistency.

    Returns:
        (list of projection row dicts, was_cached)
    """
    return await fetch_and_parse(
        POPULATION_PROJECTIONS_RESOURCE_URL,
        sheet=0,
        ttl=CACHE_TTL_DATA,
    )
