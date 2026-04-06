"""Canadian Nutrient File API client.

Provides async functions for fetching, filtering, caching, and rate-limiting
all Canadian Nutrient File API endpoints. All public functions return
(data, was_cached) tuples.

Key design:
- fetch_all_foods fetches the full food list, cached for 7 days (CACHE_TTL)
- search_foods and search_by_food_group both call fetch_all_foods for client-side filtering
- Both search functions share the same cached full-list fetch
- All cache keys include lang param for bilingual cache isolation
- compare_foods uses asyncio.gather for parallel nutrient fetches
"""

import asyncio
from typing import Any

import httpx

from mcp_canada.modules.nutrient_file.constants import (
    BASE_URL,
    CACHE_TTL,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter


def _build_cache_key(path: str, params: dict[str, Any]) -> str:
    """Build a deterministic cache key from path and sorted params.

    Uses 'nut:' prefix to namespace Canadian Nutrient File cache keys.
    """
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"nut:{path}?{sorted_params}"


async def _api_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Nutrient File API with caching and rate limiting.

    Args:
        path: API path (e.g. "food", "nutrientamount").
        params: Query parameters dict.
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
            return response.json()

    return await cached_fetch(cache_key, cache_ttl, fetcher)


async def fetch_all_foods(lang: str = "en") -> tuple[list[dict], bool]:
    """Fetch the complete food list from the Canadian Nutrient File.

    This is the expensive full-list fetch, cached for 7 days (CACHE_TTL).
    The cache key is deterministic: nut:food?lang={lang}&type=json
    Both search_foods and search_by_food_group call this function to benefit
    from the shared 7-day cache.

    Args:
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — full food list.
    """
    params = {"lang": lang, "type": "json"}
    result, was_cached = await _api_get("food", params, CACHE_TTL)
    # API returns a list directly
    if isinstance(result, list):
        return result, was_cached
    return [], was_cached


async def search_foods(query: str, lang: str = "en") -> tuple[list[dict], bool]:
    """Search foods by name using client-side filtering over the cached full list.

    Calls fetch_all_foods (7-day cached) then filters by case-insensitive
    substring match on food_description field.

    Args:
        query: Search term (matched case-insensitively against food_description).
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — filtered food list.
    """
    all_foods, was_cached = await fetch_all_foods(lang)
    query_lower = query.lower()
    filtered = [
        food for food in all_foods
        if query_lower in (food.get("food_description") or "").lower()
    ]
    return filtered, was_cached


async def search_by_food_group(food_group_id: int, lang: str = "en") -> tuple[list[dict], bool]:
    """Search foods by food group using client-side filtering over the cached full list.

    Calls fetch_all_foods (7-day cached) then filters by food_group_id match.

    Args:
        food_group_id: The food group ID to filter by.
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — filtered food list.
    """
    all_foods, was_cached = await fetch_all_foods(lang)
    filtered = [
        food for food in all_foods
        if food.get("food_group_id") == food_group_id
    ]
    return filtered, was_cached


async def fetch_food_details(food_id: int, lang: str = "en") -> tuple[dict, bool]:
    """Fetch details for a single food item by ID.

    Args:
        food_id: The food item ID.
        lang: Language code ('en' or 'fr').

    Returns:
        (dict, was_cached) — food item details.
    """
    params = {"lang": lang, "id": food_id}
    result, was_cached = await _api_get("food", params, CACHE_TTL)
    # API may return a list with one item or a dict
    if isinstance(result, list):
        return result[0] if result else {}, was_cached
    return result or {}, was_cached


async def fetch_nutrient_amounts(food_id: int, lang: str = "en") -> tuple[list[dict], bool]:
    """Fetch all nutrient amounts for a food item (per 100g).

    Args:
        food_id: The food item ID.
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — nutrient amount records.
    """
    params = {"lang": lang, "id": food_id}
    result, was_cached = await _api_get("nutrientamount", params, CACHE_TTL)
    if isinstance(result, list):
        return result, was_cached
    return [], was_cached


async def fetch_serving_sizes(food_id: int, lang: str = "en") -> tuple[list[dict], bool]:
    """Fetch serving size measures for a food item.

    Args:
        food_id: The food item ID.
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — serving size records.
    """
    params = {"lang": lang, "id": food_id}
    result, was_cached = await _api_get("servingsize", params, CACHE_TTL)
    if isinstance(result, list):
        return result, was_cached
    return [], was_cached


async def fetch_nutrients(lang: str = "en") -> tuple[list[dict], bool]:
    """Fetch all nutrient names from the Canadian Nutrient File.

    Args:
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — nutrient name records.
    """
    params = {"lang": lang}
    result, was_cached = await _api_get("nutrientname", params, CACHE_TTL)
    if isinstance(result, list):
        return result, was_cached
    return [], was_cached


async def fetch_food_groups(lang: str = "en") -> tuple[list[dict], bool]:
    """Fetch all food group categories from the Canadian Nutrient File.

    Args:
        lang: Language code ('en' or 'fr').

    Returns:
        (list[dict], was_cached) — food group records.
    """
    params = {"lang": lang}
    result, was_cached = await _api_get("foodgroup", params, CACHE_TTL)
    if isinstance(result, list):
        return result, was_cached
    return [], was_cached


async def compare_foods(
    food_ids: list[int], lang: str = "en"
) -> list[tuple[list[dict], bool]]:
    """Fetch nutrient amounts for multiple foods in parallel using asyncio.gather.

    Args:
        food_ids: List of food IDs to compare (2-5 items).
        lang: Language code ('en' or 'fr').

    Returns:
        list of (list[dict], was_cached) tuples — one per food_id, in order.
    """
    results = await asyncio.gather(
        *[fetch_nutrient_amounts(fid, lang) for fid in food_ids]
    )
    return list(results)
