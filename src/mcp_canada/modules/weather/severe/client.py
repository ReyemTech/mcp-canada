"""Severe weather client for MSC GeoMet OGC API.

Provides async functions for radar precipitation data, lightning information,
and UV index extraction from citypageweather. All functions return (data, was_cached) tuples.

Collections used:
- weather:rdpa:10km:24f — Regional Deterministic Precipitation Analysis (24h accumulation)
- citypageweather-realtime — city page weather with forecastGroup containing UV index

Lightning note: No lightning strike collection exists in the MSC GeoMet OGC API.
The MSC DataMart LDFA XML feed (https://dd.weather.gc.ca/) provides lightning data.
"""

from typing import Any

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_FORECAST,
    CACHE_TTL_REALTIME,
    COLL_CITYPAGE,
    COLL_RADAR,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, ogc_fetch


async def fetch_radar_data(
    lat: float,
    lon: float,
    limit: int = 10,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch radar precipitation accumulation data from RDPA collection.

    Uses a 50km bounding box centred on the given coordinates.

    Args:
        lat: Latitude of the query location.
        lon: Longitude of the query location.
        limit: Maximum number of features to return.

    Returns:
        (list[dict], was_cached) — flattened precipitation accumulation items.
    """
    bbox = build_bbox(lat, lon, radius_km=50)
    features, _, was_cached = await ogc_fetch(
        COLL_RADAR,
        bbox=bbox,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    items = []
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry")
        feat_lat, feat_lon = extract_centroid(geom)

        # RDPA field: APCP_Sfc = accumulated precipitation in mm
        precipitation_mm = props.get("APCP_Sfc")
        if precipitation_mm is not None:
            try:
                precipitation_mm = float(precipitation_mm)
            except (TypeError, ValueError):
                precipitation_mm = None

        items.append({
            "precipitation_mm": precipitation_mm,
            "datetime": props.get("datetime"),
            "lat": feat_lat if feat_lat is not None else props.get("lat"),
            "lon": feat_lon if feat_lon is not None else props.get("lon"),
        })

    return items, was_cached


async def fetch_lightning() -> tuple[None, bool]:
    """Return (None, False) — no lightning collection exists in MSC GeoMet OGC API.

    Lightning strike data is available via the MSC DataMart LDFA XML feed
    at https://dd.weather.gc.ca/ but not through the OGC API Features endpoint.
    The tool layer returns a structured NOT_FOUND error with the DataMart URL.

    Returns:
        (None, False) always.
    """
    return None, False


async def fetch_uv_index(
    lat: float | None = None,
    lon: float | None = None,
    location: str | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    """Fetch UV index from citypageweather-realtime forecastGroup.

    The UV index is embedded within the forecastGroup.forecast list for daytime
    forecast periods. This function queries the nearest city page weather and
    extracts the UV index from the first period that contains it.

    Args:
        lat: Latitude for location-based search.
        lon: Longitude for location-based search.
        location: Optional location name (informational only).

    Returns:
        (dict, was_cached) with uv_index, uv_category, period, and location info,
        or (None, False) if no UV data found.
    """
    bbox = None
    if lat is not None and lon is not None:
        bbox = build_bbox(lat, lon, radius_km=50)

    features, _, was_cached = await ogc_fetch(
        COLL_CITYPAGE,
        bbox=bbox,
        limit=5,
        ttl=CACHE_TTL_FORECAST,
    )

    if not features:
        return None, False

    # Use the first feature (nearest to requested location)
    feature = features[0]
    props = feature.get("properties", {})
    geom = feature.get("geometry")
    feat_lat, feat_lon = extract_centroid(geom)

    # Extract UV index from forecastGroup
    uv_index = None
    uv_category = None
    uv_period = None

    forecast_group = props.get("forecastGroup", {})
    forecasts = forecast_group.get("forecast", [])
    if not isinstance(forecasts, list):
        forecasts = []

    for forecast in forecasts:
        if not isinstance(forecast, dict):
            continue
        uv_data = forecast.get("uvIndex")
        if uv_data is not None and isinstance(uv_data, dict):
            raw_index = uv_data.get("Index")
            if raw_index is not None:
                try:
                    uv_index = int(raw_index)
                except (TypeError, ValueError):
                    try:
                        uv_index = float(raw_index)
                    except (TypeError, ValueError):
                        uv_index = None
            uv_category = uv_data.get("category")
            period_data = forecast.get("period", {})
            uv_period = period_data.get("textForecastName") if isinstance(period_data, dict) else None
            break  # Use first forecast period with UV data

    return {
        "location_en": props.get("location_en"),
        "location_fr": props.get("location_fr"),
        "province_en": props.get("province_en"),
        "province_fr": props.get("province_fr"),
        "uv_index": uv_index,
        "uv_category": uv_category,
        "period": uv_period,
        "lat": feat_lat if feat_lat is not None else props.get("lat"),
        "lon": feat_lon if feat_lon is not None else props.get("lon"),
    }, was_cached
