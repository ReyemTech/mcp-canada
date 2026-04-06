"""Recalls API client for the Health Canada Recalls module.

Provides async functions for fetching, caching, and rate-limiting all
Recalls API endpoints. All public functions return (data, was_cached) tuples.

API base: https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/
- GET /recent/{lang}?lim=&off=          — recent recalls across all categories
- GET /search?search=&cat[]=&lim=&off=  — keyword search with optional category filter
- GET /{recall_id}/{lang}               — full detail for a specific recall
"""

from typing import Any

import httpx

from mcp_canada.modules.recalls.constants import (
    BASE_URL,
    CACHE_TTL_DETAILS,
    CACHE_TTL_SEARCH,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter


def _build_cache_key(path: str, params: Any) -> str:
    """Build a deterministic cache key from path and sorted params.

    Args:
        path: API path relative to BASE_URL.
        params: Either a dict of params or a list of (key, value) tuples.

    Returns:
        Cache key string with 'rcll:' prefix.
    """
    if isinstance(params, list):
        # Tuple-style params (for cat[] array support)
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params, key=lambda x: (x[0], str(x[1]))))
    else:
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"rcll:{path}?{sorted_params}"


async def _api_get(
    path: str,
    params: Any,
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Recalls API with caching and rate limiting.

    Args:
        path: API path relative to BASE_URL (e.g. "recent/en").
        params: Query parameters — dict or list of (key, value) tuples for cat[] support.
        cache_ttl: Cache TTL in seconds.

    Returns:
        (response_json, was_cached)
    """
    url = BASE_URL + path
    cache_key = _build_cache_key(path, params)
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            # Recalls API sometimes returns empty body on valid requests
            if not response.content:
                return {"results": []}
            return response.json()

    return await cached_fetch(cache_key, cache_ttl, fetcher)


async def fetch_recent_recalls(
    lang: str = "en",
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch the most recent recalls across all categories.

    Args:
        lang: Language code ('en' or 'fr').
        limit: Number of results to return (maps to lim param).
        offset: Pagination offset (maps to off param).

    Returns:
        (list[dict], was_cached) — list of recall summary dicts.
    """
    path = f"recent/{lang}"
    params = {"lim": limit, "off": offset}
    raw, was_cached = await _api_get(path, params, CACHE_TTL_SEARCH)

    # Extract the list from the response — API returns {"warnings": [...], "total": N}
    items: list[dict[str, Any]] = raw.get("warnings", [])
    return items, was_cached


async def fetch_recall_search(
    search: str,
    categories: list[str],
    lang: str = "en",
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """Search recalls by keyword with optional category filter.

    Uses httpx tuple-style params to support cat[] array parameter syntax
    required by the Health Canada API.

    Args:
        search: Keyword to search for.
        categories: List of category codes to filter by (e.g. ["FOOD", "VEHICLE"]).
                    Empty list means no category filter (all categories).
        lang: Language code ('en' or 'fr').
        limit: Number of results to return.
        offset: Pagination offset.

    Returns:
        (list[dict], was_cached) — list of recall summary dicts.
    """
    # Build tuple-style params list for cat[] array param support
    params: list[tuple[str, Any]] = []

    # Add category filters as cat[] array params
    for cat in categories:
        params.append(("cat[]", cat))

    # Add remaining params
    if search:
        params.append(("search", search))
    params.append(("lim", limit))
    params.append(("off", offset))

    raw, was_cached = await _api_get("search", params, CACHE_TTL_SEARCH)

    # Extract the list — API returns {"results": [...], "total": N}
    items: list[dict[str, Any]] = raw.get("results", [])
    return items, was_cached


async def fetch_recall_details(
    recall_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full detail for a specific recall by ID.

    Args:
        recall_id: The recall identifier (e.g. "2024-123").
        lang: Language code ('en' or 'fr').

    Returns:
        (dict, was_cached) — recall detail dict with full fields.
    """
    path = f"{recall_id}/{lang}"
    raw, was_cached = await _api_get(path, {}, CACHE_TTL_DETAILS)
    return raw, was_cached
