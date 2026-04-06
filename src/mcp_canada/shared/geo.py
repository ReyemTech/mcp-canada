"""OGC API Features utility layer for MSC GeoMet collections.

Provides haversine distance, geometry centroid extraction, bounding box
construction, and a cached OGC collection items fetcher.
"""

import hashlib
import json
import math
from typing import Any

from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.rate_limiter import get_limiter

_OGC_BASE_URL = "https://api.weather.gc.ca"
_EARTH_RADIUS_KM = 6371.0
_DEFAULT_TTL = 300


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in km between two lat/lon points.

    Args:
        lat1: Latitude of first point in decimal degrees.
        lon1: Longitude of first point in decimal degrees.
        lat2: Latitude of second point in decimal degrees.
        lon2: Longitude of second point in decimal degrees.

    Returns:
        Distance in kilometres.
    """
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return _EARTH_RADIUS_KM * c


def extract_centroid(geometry: dict | None) -> tuple[float | None, float | None]:
    """Return (lat, lon) centroid from a GeoJSON geometry dict.

    Handles Point, Polygon, and MultiPolygon. GeoJSON uses [lon, lat] order;
    this function swaps to (lat, lon) for consistency.

    Args:
        geometry: GeoJSON geometry dict or None.

    Returns:
        (lat, lon) tuple, or (None, None) for null/unsupported geometry.
    """
    if not geometry:
        return None, None

    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")

    if geom_type == "Point" and coords:
        # GeoJSON Point: [lon, lat]
        return float(coords[1]), float(coords[0])

    if geom_type == "Polygon" and coords:
        # Average of first ring vertices
        ring = coords[0]
        if not ring:
            return None, None
        avg_lat = sum(v[1] for v in ring) / len(ring)
        avg_lon = sum(v[0] for v in ring) / len(ring)
        return float(avg_lat), float(avg_lon)

    if geom_type == "MultiPolygon" and coords:
        # Average of first ring of first polygon
        first_ring = coords[0][0]
        if not first_ring:
            return None, None
        avg_lat = sum(v[1] for v in first_ring) / len(first_ring)
        avg_lon = sum(v[0] for v in first_ring) / len(first_ring)
        return float(avg_lat), float(avg_lon)

    return None, None


def build_bbox(
    lat: float, lon: float, radius_km: float = 50
) -> tuple[float, float, float, float]:
    """Build a bounding box (lon_min, lat_min, lon_max, lat_max) around a point.

    Uses the 1 degree lat ~ 111 km approximation for simplicity.

    Args:
        lat: Centre latitude in decimal degrees.
        lon: Centre longitude in decimal degrees.
        radius_km: Radius in kilometres (default 50 km).

    Returns:
        (lon_min, lat_min, lon_max, lat_max) tuple.
    """
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
    return (
        lon - lon_delta,
        lat - lat_delta,
        lon + lon_delta,
        lat + lat_delta,
    )


async def ogc_fetch(
    collection_id: str,
    *,
    bbox: tuple[float, float, float, float] | None = None,
    datetime_filter: str | None = None,
    properties: dict[str, Any] | None = None,
    sortby: str | None = None,
    limit: int = 50,
    offset: int = 0,
    ttl: int = _DEFAULT_TTL,
) -> tuple[list[dict], int, bool]:
    """Fetch items from an OGC API Features collection on MSC GeoMet.

    IMPORTANT: collection_id may contain colons (e.g. "climate:cmip5:...").
    The URL is built with an f-string to avoid percent-encoding colons in the
    path segment.

    Args:
        collection_id: OGC collection ID (colons are kept literal in the URL path).
        bbox: Optional (lon_min, lat_min, lon_max, lat_max) spatial filter.
        datetime_filter: Optional ISO 8601 datetime or interval string.
        properties: Optional dict of property filters added as query params.
        sortby: Optional sort field string (e.g. "+DATETIME").
        limit: Maximum number of features to return (default 50).
        offset: Pagination offset (default 0).
        ttl: Cache TTL in seconds (default 300).

    Returns:
        (features, number_matched, was_cached) tuple.
    """
    # Build params dict for cache key hashing
    params: dict[str, Any] = {"f": "json", "limit": limit, "offset": offset}
    if bbox is not None:
        params["bbox"] = ",".join(str(v) for v in bbox)
    if datetime_filter is not None:
        params["datetime"] = datetime_filter
    if properties:
        params.update(properties)
    if sortby is not None:
        params["sortby"] = sortby

    # Build stable cache key from sorted params
    params_hash = hashlib.md5(
        json.dumps(sorted(params.items()), sort_keys=True).encode()
    ).hexdigest()[:12]
    cache_key = f"wx:ogc:{collection_id}:{params_hash}"

    # URL: build with f-string to avoid encoding colons in collection_id path
    url = f"{_OGC_BASE_URL}/collections/{collection_id}/items"

    async def _fetch() -> dict:
        limiter = get_limiter("weather", rate=20.0)
        await limiter.acquire()
        return await api_get(url, params=params)

    raw, was_cached = await cached_fetch(cache_key, ttl, _fetch)

    features: list[dict] = raw.get("features", []) if raw else []
    number_matched: int = raw.get("numberMatched", len(features)) if raw else 0

    return features, number_matched, was_cached


async def nearest_station(
    lat: float,
    lon: float,
    collection_id: str = "climate-stations",
    radius_km: float = 100,
) -> dict | None:
    """Find the closest OGC feature to the given coordinates.

    Queries the collection with a bounding box, then picks the feature
    whose geometry centroid has the minimum haversine distance.

    Args:
        lat: Query latitude in decimal degrees.
        lon: Query longitude in decimal degrees.
        collection_id: OGC collection to search (default "climate-stations").
        radius_km: Search radius for the bounding box (default 100 km).

    Returns:
        The closest feature dict, or None if no features are found.
    """
    bbox = build_bbox(lat, lon, radius_km)
    features, _, _ = await ogc_fetch(collection_id, bbox=bbox, limit=50)

    if not features:
        return None

    best: dict | None = None
    best_dist = float("inf")

    for feature in features:
        geometry = feature.get("geometry")
        feat_lat, feat_lon = extract_centroid(geometry)
        if feat_lat is None or feat_lon is None:
            continue
        dist = haversine_km(lat, lon, feat_lat, feat_lon)
        if dist < best_dist:
            best_dist = dist
            best = feature

    return best
