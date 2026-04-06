"""AQHI client functions for MSC GeoMet Air Quality Health Index collections.

All public functions return (data, was_cached) tuples.
Flattens GeoJSON features into plain dicts for agent consumption.
"""

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_FORECAST,
    CACHE_TTL_REALTIME,
    COLL_AQHI_FORECAST,
    COLL_AQHI_OBS,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, ogc_fetch


def _flatten_aqhi_feature(feature: dict) -> dict:
    """Flatten a GeoJSON AQHI feature into a plain dict."""
    props = feature.get("properties") or {}
    lat, lon = extract_centroid(feature.get("geometry"))
    return {
        "location_id": props.get("location_id"),
        "location_name": props.get("location_name_en") or props.get("community_en"),
        "aqhi_value": props.get("aqhi"),
        "datetime": props.get("observation_datetime") or props.get("forecast_datetime"),
        "lat": lat,
        "lon": lon,
    }


async def fetch_aqhi(
    lat: float | None = None,
    lon: float | None = None,
    location_id: str | None = None,
    limit: int = 5,
) -> tuple[list[dict], bool]:
    """Fetch current AQHI observations.

    Args:
        lat: Latitude for spatial search.
        lon: Longitude for spatial search.
        location_id: AQHI location ID (e.g. "ON106") for direct lookup.
        limit: Maximum number of readings to return.

    Returns:
        (readings, was_cached) tuple of flattened AQHI dicts.
    """
    if location_id is not None:
        features, _, was_cached = await ogc_fetch(
            COLL_AQHI_OBS,
            properties={"location_id": location_id},
            limit=limit,
            ttl=CACHE_TTL_REALTIME,
        )
    else:
        bbox = build_bbox(lat, lon)  # type: ignore[arg-type]
        features, _, was_cached = await ogc_fetch(
            COLL_AQHI_OBS,
            bbox=bbox,
            limit=limit,
            ttl=CACHE_TTL_REALTIME,
        )

    return [_flatten_aqhi_feature(f) for f in features], was_cached


async def fetch_aqhi_forecast(
    lat: float | None = None,
    lon: float | None = None,
    location_id: str | None = None,
    limit: int = 10,
) -> tuple[list[dict], bool]:
    """Fetch AQHI forecasts.

    Args:
        lat: Latitude for spatial search.
        lon: Longitude for spatial search.
        location_id: AQHI location ID for direct lookup.
        limit: Maximum number of forecast periods to return.

    Returns:
        (readings, was_cached) tuple of flattened AQHI forecast dicts.
    """
    if location_id is not None:
        features, _, was_cached = await ogc_fetch(
            COLL_AQHI_FORECAST,
            properties={"location_id": location_id},
            limit=limit,
            ttl=CACHE_TTL_FORECAST,
        )
    else:
        bbox = build_bbox(lat, lon)  # type: ignore[arg-type]
        features, _, was_cached = await ogc_fetch(
            COLL_AQHI_FORECAST,
            bbox=bbox,
            limit=limit,
            ttl=CACHE_TTL_FORECAST,
        )

    return [_flatten_aqhi_feature(f) for f in features], was_cached


async def fetch_aqhi_history(
    location_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
) -> tuple[list[dict], bool]:
    """Fetch historical AQHI observations for a location.

    Args:
        location_id: AQHI location ID (e.g. "ON106").
        start_date: ISO 8601 date string for range start (e.g. "2026-03-01").
        end_date: ISO 8601 date string for range end (e.g. "2026-03-31").
        limit: Maximum number of readings to return.

    Returns:
        (readings, was_cached) tuple of flattened AQHI observation dicts.
    """
    datetime_filter: str | None = None
    if start_date and end_date:
        datetime_filter = f"{start_date}/{end_date}"
    elif start_date:
        datetime_filter = f"{start_date}/.."
    elif end_date:
        datetime_filter = f"../{end_date}"

    features, _, was_cached = await ogc_fetch(
        COLL_AQHI_OBS,
        properties={"location_id": location_id},
        datetime_filter=datetime_filter,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    return [_flatten_aqhi_feature(f) for f in features], was_cached
