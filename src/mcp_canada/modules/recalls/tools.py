"""Health Canada Recalls @tool functions.

Provides 6 intent-based MCP tools for querying Canadian product recalls
across all Health Canada categories: food, vehicles, health products, and
consumer products.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.recalls.client import (
    fetch_recall_details,
    fetch_recall_search,
    fetch_recent_recalls,
)
from mcp_canada.modules.recalls.constants import (
    BASE_URL,
    CATEGORIES,
)
from mcp_canada.shared.envelope import make_error, make_response, upstream_guard

# API name and base URL for _meta envelope
_API_NAME = "Health Canada Recalls"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Get recent recalls (RCLL-01)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_get_recent(
    limit: int = 25,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the most recent product recalls across all Health Canada categories.

    Use for: getting the latest recall alerts across all categories including
    food, vehicles, health products, and consumer products from Health Canada.
    Keywords: recall, recent, latest, alert, warning, safety, health canada,
    food, vehicle, health products, consumer, new, current.
    """
    try:
        items, cached = await fetch_recent_recalls(lang=lang, limit=limit, offset=offset)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        items,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Search recalls by keyword (RCLL-02)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_search(
    keyword: str,
    category: str | None = None,
    limit: int = 25,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Health Canada recalls by keyword with optional category filter.

    Use for: finding recalls matching a specific keyword such as a product
    name, brand, contaminant, or issue. Optionally filter by category.
    Keywords: search, recall, find, keyword, product, brand, contaminant,
    listeria, salmonella, airbag, defect, food, vehicle, health, consumer.
    """
    # Validate category if provided
    if category is not None and category not in CATEGORIES:
        valid = list(CATEGORIES.keys())
        return make_error(
            "INVALID_INPUT",
            f"Invalid category '{category}'. Valid values: {valid}",
            lang=lang,
        )

    categories = [category] if category is not None else []

    try:
        items, cached = await fetch_recall_search(
            search=keyword,
            categories=categories,
            lang=lang,
            limit=limit,
            offset=offset,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        items,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Get recall details (RCLL-03)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_get_details(
    recall_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full details of a specific Health Canada recall by recall ID.

    Use for: retrieving complete recall information including affected products,
    corrective actions, audience, and description for a known recall ID.
    Keywords: recall, details, full, affected products, corrective action,
    recall id, product recall, health canada, specific, information.
    """
    try:
        detail, cached = await fetch_recall_details(recall_id=recall_id, lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        detail,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Food recalls (RCLL-04)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_get_food(
    keyword: str | None = None,
    limit: int = 25,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get food product recalls from Health Canada.

    Use for: finding food safety recalls including contamination alerts,
    allergen warnings, and foodborne illness risks for food products in Canada.
    Keywords: food, recall, contamination, listeria, salmonella, allergen,
    undeclared, foodborne, illness, safety, grocery, produce, meat, dairy.
    """
    try:
        items, cached = await fetch_recall_search(
            search=keyword or "",
            categories=["FOOD"],
            lang=lang,
            limit=limit,
            offset=offset,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        items,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Vehicle recalls (RCLL-05)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_get_vehicles(
    keyword: str | None = None,
    limit: int = 25,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get vehicle recalls from Transport Canada and Health Canada.

    Use for: finding vehicle safety recalls including defects in cars, trucks,
    motorcycles, child car seats, and other motor vehicles sold in Canada.
    Keywords: vehicle, car, truck, recall, airbag, defect, safety, transport
    canada, motor vehicle, automobile, motorcycle, tire, brake, steering.
    """
    try:
        items, cached = await fetch_recall_search(
            search=keyword or "",
            categories=["VEHICLE"],
            lang=lang,
            limit=limit,
            offset=offset,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        items,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Health product recalls (RCLL-06)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def recalls_get_health_products(
    keyword: str | None = None,
    limit: int = 25,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get health product recalls from Health Canada.

    Use for: finding recalls of drugs, natural health products, medical devices,
    supplements, and other regulated health products sold in Canada.
    Keywords: health product, drug, medication, supplement, medical device,
    natural health, recall, contamination, mislabelled, health canada, recall alert.
    """
    try:
        items, cached = await fetch_recall_search(
            search=keyword or "",
            categories=["HEALTH"],
            lang=lang,
            limit=limit,
            offset=offset,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Health Canada Recalls API returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        items,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
