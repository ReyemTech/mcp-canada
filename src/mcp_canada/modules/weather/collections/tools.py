"""Weather collections @tool functions for MSC GeoMet.

Provides 2 MCP tools for browsing all available MSC weather data collections
and querying items from any collection directly by ID.
"""

from typing import Any, Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.collections.client import (
    fetch_collection_items,
    fetch_collections,
)
from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.shared.envelope import NOT_FOUND, UPSTREAM_ERROR, make_error, make_response

_API_URL = BASE_URL


@tool
async def wx_list_collections(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Browse all available MSC GeoMet weather data collections.

    Use for: discovering what weather data is available beyond curated tools,
    finding a collection ID to query, listing all MSC GeoMet datasets, browsing
    available weather collections, exploring OGC API capabilities.
    Keywords: collections, browse, list, available, datasets, collections catalog,
    msc geomet, ogc, api, weather data, climate data, explore, discovery,
    collection id, what data, available data, all collections, metadata.
    """
    try:
        collections, cached = await fetch_collections()
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Collections API error: {exc}", lang=lang)

    if not collections:
        return make_error(
            NOT_FOUND,
            "No collections found from MSC GeoMet API.",
            lang=lang,
        )

    return make_response(
        collections,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_collection_items(
    collection_id: str,
    bbox: str | None = None,
    datetime_filter: str | None = None,
    properties: dict[str, Any] | None = None,
    limit: int = 50,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query any MSC GeoMet weather collection by ID and return its items.

    Use for: accessing niche collections not covered by specific tools,
    querying climate data by collection ID, fetching raw OGC collection items,
    getting data from any MSC GeoMet collection directly.
    Keywords: collection, query, items, collection_id, ogc, raw data, niche,
    specific collection, climate, weather, msc geomet, features, geojson,
    spatial filter, bbox, datetime filter, properties filter, direct access.

    Note: Use wx_list_collections first to find available collection IDs.
    The bbox parameter should be formatted as 'lon_min,lat_min,lon_max,lat_max'.
    """
    # Parse bbox string if provided
    parsed_bbox: tuple[float, float, float, float] | None = None
    if bbox is not None:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
            if len(parts) == 4:
                parsed_bbox = (parts[0], parts[1], parts[2], parts[3])
        except (ValueError, TypeError):
            parsed_bbox = None

    try:
        items, total, cached = await fetch_collection_items(
            collection_id,
            bbox=parsed_bbox,
            datetime_filter=datetime_filter,
            properties=properties,
            limit=limit,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Collection items API error: {exc}", lang=lang)

    if not items:
        return make_error(
            NOT_FOUND,
            f"No items found in collection '{collection_id}'. "
            "Check the collection ID using wx_list_collections.",
            lang=lang,
        )

    return make_response(
        {"items": items, "total_matched": total, "collection_id": collection_id},
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
