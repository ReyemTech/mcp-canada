"""Drug Product Database API client.

Provides async functions for fetching, caching, and rate-limiting all Drug
Product Database API endpoints. All public functions return (data, was_cached)
tuples.

IMPORTANT: All detail endpoints (ingredients, routes, schedule, therapeutic_class,
status) use `drug_code` as the `id` parameter. This is the internal numeric ID
from the Drug Product Database — NOT the DIN (Drug Identification Number).
A drug's DIN and drug_code are completely different values.
"""

import asyncio
from typing import Any

import httpx

from mcp_canada.modules.drug_database.constants import (
    BASE_URL,
    CACHE_TTL,
    HTTP_TIMEOUT,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter


def _build_cache_key(path: str, params: dict[str, Any]) -> str:
    """Build a deterministic cache key from path and sorted params."""
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"drug:{path}?{sorted_params}"


async def _api_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int = CACHE_TTL,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Drug Product Database API with caching and rate limiting.

    Args:
        path: API path relative to BASE_URL (e.g. "drugproduct/").
        params: Query parameters dict.
        cache_ttl: Cache TTL in seconds (default: 12 hours).

    Returns:
        (response_json, was_cached)
    """
    url = BASE_URL + path
    cache_key = _build_cache_key(path, params)
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            return response.json()

    return await cached_fetch(cache_key, cache_ttl, fetcher)


async def fetch_drug_search(
    brandname: str | None = None,
    din: str | None = None,
    company: str | None = None,
) -> tuple[list[dict], bool]:
    """Search for drug products by brand name, DIN, or company.

    Note: Returns drug_code in results. Use drug_code (not DIN) for all
    detail lookups (fetch_ingredients, fetch_routes, etc.).

    Args:
        brandname: Brand name to search for (partial match).
        din: DIN (Drug Identification Number) to search for.
        company: Company name to search for (partial match).

    Returns:
        (list[dict], was_cached)
    """
    params: dict[str, Any] = {}
    if brandname is not None:
        params["brandname"] = brandname
    if din is not None:
        params["din"] = din
    if company is not None:
        params["company"] = company

    return await _api_get("drugproduct/", params)


async def fetch_ingredients(
    drug_code: int,
) -> tuple[list[dict], bool]:
    """Fetch active ingredients for a drug product.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("activeingredient/", {"id": drug_code})


async def fetch_routes(
    drug_code: int,
) -> tuple[list[dict], bool]:
    """Fetch routes of administration for a drug product.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("route/", {"id": drug_code})


async def fetch_schedule(
    drug_code: int,
) -> tuple[list[dict], bool]:
    """Fetch schedule classification for a drug product.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("schedule/", {"id": drug_code})


async def fetch_therapeutic_class(
    drug_code: int,
) -> tuple[list[dict], bool]:
    """Fetch ATC (Anatomical Therapeutic Chemical) classification for a drug product.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("therapeuticclass/", {"id": drug_code})


async def fetch_status(
    drug_code: int,
) -> tuple[list[dict], bool]:
    """Fetch market status for a drug product.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("status/", {"id": drug_code})


async def fetch_companies(
    companyname: str,
) -> tuple[list[dict], bool]:
    """Search for companies in the Drug Product Database.

    Args:
        companyname: Company name to search for (partial match).

    Returns:
        (list[dict], was_cached)
    """
    return await _api_get("company/", {"companyname": companyname})


async def fetch_drug_details(
    drug_code: int,
) -> tuple[dict, bool]:
    """Fetch all detail sections for a drug product in parallel.

    Uses asyncio.gather to fetch ingredients, routes, schedule, therapeutic
    class, and status concurrently. Returns a flat sections dict (not a
    single flattened object).

    IMPORTANT: drug_code is the internal numeric ID — NOT the DIN.
    Use the drug_code from fetch_drug_search results.

    Args:
        drug_code: The internal drug_code (NOT the DIN) from Drug Product Database.

    Returns:
        (sections_dict, was_cached) where sections_dict has keys:
            - ingredients: list of active ingredients
            - routes: list of administration routes
            - schedule: list of schedule entries
            - therapeutic_class: list of ATC classifications
            - status: list of market status entries
        was_cached is True only if ALL 5 sub-responses were cached.
    """
    results = await asyncio.gather(
        fetch_ingredients(drug_code),
        fetch_routes(drug_code),
        fetch_schedule(drug_code),
        fetch_therapeutic_class(drug_code),
        fetch_status(drug_code),
    )

    (ingredients, cached_ing), (routes, cached_rts), (schedule, cached_sch), \
        (therapeutic_class, cached_tc), (status, cached_st) = results

    # Only report as cached if ALL sub-responses were cached
    all_cached = all([cached_ing, cached_rts, cached_sch, cached_tc, cached_st])

    sections = {
        "ingredients": ingredients,
        "routes": routes,
        "schedule": schedule,
        "therapeutic_class": therapeutic_class,
        "status": status,
    }

    return sections, all_cached
