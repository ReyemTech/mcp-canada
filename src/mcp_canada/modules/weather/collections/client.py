"""Client functions for weather/collections sub-module.

Provides access to all MSC GeoMet OGC collections — both listing available
collections and querying items from any collection by ID.

All functions return (data, ..., was_cached) tuples.
"""

from typing import Any

from mcp_canada.modules.weather.constants import BASE_URL, CACHE_TTL_COLLECTIONS
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.geo import extract_centroid, ogc_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.rate_limiter import get_limiter


async def fetch_collections() -> tuple[list[dict], bool]:
    """Fetch all available MSC GeoMet OGC collections.

    Calls BASE_URL/collections?f=json to retrieve the catalog of all
    available data collections.

    Returns:
        (list of {id, title, description} dicts, was_cached) tuple.
    """
    url = f"{BASE_URL}/collections?f=json"

    async def _fetch() -> dict:
        limiter = get_limiter("weather", rate=20.0)
        await limiter.acquire()
        return await api_get(url, params={"f": "json"})

    raw, was_cached = await cached_fetch("wx:collections", CACHE_TTL_COLLECTIONS, _fetch)

    if not raw:
        return [], was_cached

    collections: list[dict] = []
    for coll in raw.get("collections", []):
        collections.append({
            "id": coll.get("id"),
            "title": coll.get("title"),
            "description": coll.get("description"),
        })

    return collections, was_cached


async def fetch_collection_items(
    collection_id: str,
    bbox: tuple[float, float, float, float] | None = None,
    datetime_filter: str | None = None,
    properties: dict[str, Any] | None = None,
    limit: int = 50,
) -> tuple[list[dict], int, bool]:
    """Fetch items from any MSC GeoMet OGC collection by ID.

    Delegates directly to ogc_fetch(), adding lat/lon centroid extraction
    for each feature.

    Args:
        collection_id: OGC collection ID (e.g. "climate-stations").
        bbox: Optional (lon_min, lat_min, lon_max, lat_max) spatial filter.
        datetime_filter: Optional ISO 8601 datetime or interval string.
        properties: Optional dict of property filters.
        limit: Maximum number of features to return (default 50).

    Returns:
        (list of feature dicts with lat/lon, total_matched, was_cached) tuple.
    """
    features, total, was_cached = await ogc_fetch(
        collection_id,
        bbox=bbox,
        datetime_filter=datetime_filter,
        properties=properties,
        limit=limit,
    )

    items: list[dict] = []
    for feature in features:
        lat, lon = extract_centroid(feature.get("geometry"))
        item = dict(feature)
        item["lat"] = lat
        item["lon"] = lon
        items.append(item)

    return items, total, was_cached
