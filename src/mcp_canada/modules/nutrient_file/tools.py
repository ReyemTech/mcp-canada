"""Canadian Nutrient File @tool functions.

Provides 8 intent-based MCP tools for querying Health Canada's Canadian
Nutrient File database: food search, nutrient amounts per 100g, serving sizes,
food group browsing, nutrient listing, food group listing, and food comparison.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.nutrient_file.client import (
    compare_foods,
    fetch_food_details,
    fetch_food_groups,
    fetch_nutrient_amounts,
    fetch_nutrients,
    fetch_serving_sizes,
    search_by_food_group,
    search_foods,
)
from mcp_canada.modules.nutrient_file.constants import BASE_URL
from mcp_canada.shared.envelope import make_error, make_response

# API name and base URL for _meta envelope
_API_NAME = "Canadian Nutrient File"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Search foods by name
# ---------------------------------------------------------------------------

@tool
async def nutrient_search_foods(
    query: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Canadian Nutrient File foods by name using client-side filtering.

    Use for: finding food items by name from the Health Canada Canadian Nutrient
    File database. Searches the full food list cached for 7 days.
    Keywords: food, search, name, nutrition, nutrient, health, canada, Canadian,
    diet, calorie, protein, fat, carbohydrate, ingredient, recipe, meal.
    """
    results, cached = await search_foods(query, lang)
    return make_response(
        results,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Get food details
# ---------------------------------------------------------------------------

@tool
async def nutrient_get_food_details(
    food_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get detailed information about a specific food item from the Canadian Nutrient File.

    Use for: retrieving complete details for a known food item ID including
    food description and food group classification.
    Keywords: food, details, information, id, lookup, nutrient file, Health Canada,
    food description, food group, specific food item.
    """
    data, cached = await fetch_food_details(food_id, lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Get nutrient amounts per 100g
# ---------------------------------------------------------------------------

@tool
async def nutrient_get_nutrient_amounts(
    food_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get all nutrient amounts per 100g for a specific food from the Canadian Nutrient File.

    Use for: getting the full nutritional profile of a food item including
    calories, macronutrients, vitamins, minerals per 100 grams.
    Keywords: nutrition, nutrient, amount, per 100g, calories, protein, fat,
    carbohydrate, vitamin, mineral, macronutrient, micronutrient, composition.
    """
    data, cached = await fetch_nutrient_amounts(food_id, lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Get serving sizes
# ---------------------------------------------------------------------------

@tool
async def nutrient_get_serving_sizes(
    food_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get serving size measures and conversion factors for a food item.

    Use for: looking up common serving sizes for a food such as '1 medium apple'
    or '1 cup sliced' with their gram conversion factors.
    Keywords: serving, size, measure, portion, cup, medium, gram, conversion,
    household, measure, tablespoon, ounce, weight.
    """
    data, cached = await fetch_serving_sizes(food_id, lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Search foods by food group
# ---------------------------------------------------------------------------

@tool
async def nutrient_search_by_food_group(
    food_group_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all foods within a specific food group from the Canadian Nutrient File.

    Use for: browsing all food items in a specific category such as dairy, fruits,
    vegetables, grains, or meat using the food group ID.
    Keywords: food group, category, browse, list, dairy, fruit, vegetable, grain,
    meat, poultry, legume, nut, fish, beverage, group id.
    """
    data, cached = await search_by_food_group(food_group_id, lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: List all nutrients
# ---------------------------------------------------------------------------

@tool
async def nutrient_list_nutrients(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all nutrients available in the Canadian Nutrient File database.

    Use for: discovering all nutrient names, units, and groups tracked in the
    Health Canada Canadian Nutrient File database (e.g., Energy, Protein, Vitamin C).
    Keywords: nutrients, list, all, catalog, names, units, vitamins, minerals,
    macronutrients, micronutrients, nutrient groups, dietary reference.
    """
    data, cached = await fetch_nutrients(lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: List all food groups
# ---------------------------------------------------------------------------

@tool
async def nutrient_list_food_groups(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all food group categories in the Canadian Nutrient File database.

    Use for: discovering all food categories available in the Health Canada
    Canadian Nutrient File (e.g., Dairy, Fruits, Vegetables, Grains).
    Keywords: food groups, categories, list, all, dairy, fruit, vegetable, grain,
    meat, poultry, legume, browse, discover, catalog.
    """
    data, cached = await fetch_food_groups(lang)
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Compare foods
# ---------------------------------------------------------------------------

@tool
async def nutrient_compare_foods(
    food_ids: list[int],
    format: Literal["by_food", "by_nutrient"] = "by_food",
    nutrients: list[int] | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Compare nutritional content of 2-5 foods from the Canadian Nutrient File.

    Use for: comparing the nutritional profiles of multiple foods side by side.
    Supports two output formats: grouped by food or pivoted by nutrient.
    Use nutrients filter to compare only specific nutrient IDs.
    Keywords: compare, comparison, nutrition, foods, side by side, versus, vs,
    calories, protein, fat, diet, healthier, best, macros, nutrient breakdown.

    Args:
        food_ids: List of 2-5 food IDs to compare.
        format: Output format — 'by_food' (food-keyed list) or 'by_nutrient' (nutrient pivot).
        nutrients: Optional list of nutrient_name_ids to filter comparison to specific nutrients.
        lang: Language code ('en' or 'fr').
    """
    # Validate food_ids count
    if len(food_ids) < 2:
        return make_error(
            "INVALID_INPUT",
            f"At least 2 food IDs required for comparison, got {len(food_ids)}.",
            lang=lang,
        )
    if len(food_ids) > 5:
        return make_error(
            "INVALID_INPUT",
            f"Maximum 5 food IDs allowed for comparison, got {len(food_ids)}.",
            lang=lang,
        )

    # Fetch food details and nutrient amounts in parallel
    # compare_foods handles parallel nutrient fetches via asyncio.gather
    nutrient_results = await compare_foods(food_ids, lang)

    # Fetch food details for each food_id to get descriptions
    food_details = []
    for fid in food_ids:
        detail, _ = await fetch_food_details(fid, lang)
        food_details.append(detail)

    # Apply nutrients filter if provided
    def filter_nutrients(amounts: list[dict]) -> list[dict]:
        if nutrients is None:
            return amounts
        return [n for n in amounts if n.get("nutrient_name_id") in nutrients]

    if format == "by_food":
        data = []
        for i, fid in enumerate(food_ids):
            amounts, _ = nutrient_results[i]
            food_desc = food_details[i].get("food_description", f"Food {fid}")
            data.append({
                "food_id": fid,
                "food_description": food_desc,
                "nutrients": filter_nutrients(amounts),
            })
    else:
        # format == "by_nutrient": pivot so each nutrient has values keyed by food description
        # Build a map of nutrient_name_id -> {nutrient_name, unit, food_desc -> value}
        nutrient_map: dict[int, dict] = {}
        for i, fid in enumerate(food_ids):
            amounts, _ = nutrient_results[i]
            food_desc = food_details[i].get("food_description", f"Food {fid}")
            filtered = filter_nutrients(amounts)
            for nut in filtered:
                nid = nut.get("nutrient_name_id")
                if nid is None:
                    continue
                if nid not in nutrient_map:
                    nutrient_map[nid] = {
                        "nutrient_name": nut.get("nutrient_name"),
                        "unit": nut.get("nutrient_unit"),
                        "values": {},
                    }
                nutrient_map[nid]["values"][food_desc] = nut.get("nutrient_value")

        data = list(nutrient_map.values())

    # Use cached=False for compare since it aggregates multiple fetches
    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=False,
        lang=lang,
    )
