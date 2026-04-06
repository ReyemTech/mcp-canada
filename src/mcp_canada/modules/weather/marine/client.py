"""Marine weather client for MSC GeoMet OGC API.

Provides async functions for marine forecasts, hurricane track data,
and thunderstorm outlook. All functions return (data, was_cached) tuples.

Collections used:
- marineweather-realtime — coastal/offshore marine weather forecasts
- hurricanes-track-realtime — active hurricane/tropical storm tracks
- thunderstorm_outlook — thunderstorm outlook regions and risk levels
"""

from typing import Any

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_FORECAST,
    CACHE_TTL_REALTIME,
    COLL_HURRICANE_TRACK,
    COLL_MARINE,
    COLL_THUNDERSTORM,
    PROVINCE_BBOX,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, ogc_fetch


def _flatten_marine_feature(feature: dict[str, Any]) -> dict[str, Any]:
    """Flatten a marineweather-realtime feature's deeply nested structure.

    The marineweather API nests forecast text inside regularForecast.en/fr lists,
    wave forecast in waveForecast.en/fr, and warnings in a warnings array.
    This function extracts all relevant fields into a flat dict.

    Args:
        feature: A single GeoJSON feature from marineweather-realtime.

    Returns:
        Flat dict with area, forecast text, warnings_count, and coordinates.
    """
    props = feature.get("properties", {})
    geom = feature.get("geometry")
    lat, lon = extract_centroid(geom)

    # Extract forecast text from nested regularForecast list
    regular_en = props.get("regularForecast", {}).get("en", [])
    regular_fr = props.get("regularForecast", {}).get("fr", [])

    forecast_text_en = ""
    forecast_text_fr = ""
    if regular_en and isinstance(regular_en, list):
        forecast_text_en = " ".join(
            f.get("forecast", "") for f in regular_en if isinstance(f, dict)
        ).strip()
    if regular_fr and isinstance(regular_fr, list):
        forecast_text_fr = " ".join(
            f.get("forecast", "") for f in regular_fr if isinstance(f, dict)
        ).strip()

    # Wave forecast may be a string or nested dict
    wave_en = props.get("waveForecast", {})
    if isinstance(wave_en, dict):
        wave_text_en = wave_en.get("en", "")
        wave_text_fr = wave_en.get("fr", "")
    else:
        wave_text_en = str(wave_en) if wave_en else ""
        wave_text_fr = ""

    # Combine regular + wave forecasts if both present
    if wave_text_en and forecast_text_en:
        forecast_text_en = f"{forecast_text_en} {wave_text_en}"
    elif wave_text_en:
        forecast_text_en = wave_text_en

    if wave_text_fr and forecast_text_fr:
        forecast_text_fr = f"{forecast_text_fr} {wave_text_fr}"
    elif wave_text_fr:
        forecast_text_fr = wave_text_fr

    # Count and extract warnings
    warnings = props.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    warnings_count = len(warnings)

    return {
        "area_en": props.get("area_en"),
        "area_fr": props.get("area_fr"),
        "forecast_text_en": forecast_text_en or None,
        "forecast_text_fr": forecast_text_fr or None,
        "warnings_count": warnings_count,
        "warnings": [
            {
                "event": w.get("event"),
                "en": w.get("en"),
                "fr": w.get("fr"),
            }
            for w in warnings
            if isinstance(w, dict)
        ],
        "issued_utc": props.get("issued_utc"),
        "lat": lat,
        "lon": lon,
    }


async def fetch_marine_forecast(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch marine weather forecasts from marineweather-realtime collection.

    Applies spatial filtering by province bounding box or lat/lon bounding box.
    Flattens the nested bilingual structure (Pitfall 6) into flat dicts.

    Args:
        province: Two-letter province/territory code (e.g. "NS", "BC").
        lat: Latitude for bbox search (used if province is None).
        lon: Longitude for bbox search (used if province is None).
        limit: Maximum number of features to return.

    Returns:
        (list[dict], was_cached) — flattened marine forecast items.
    """
    bbox = None
    if province and province.upper() in PROVINCE_BBOX:
        bbox = PROVINCE_BBOX[province.upper()]
    elif lat is not None and lon is not None:
        bbox = build_bbox(lat, lon, radius_km=200)

    features, _, was_cached = await ogc_fetch(
        COLL_MARINE,
        bbox=bbox,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    return [_flatten_marine_feature(f) for f in features], was_cached


async def fetch_hurricane_tracks(
    limit: int = 50,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch active hurricane and tropical storm track data.

    Returns an empty list with was_cached=False when the collection is empty
    (expected behavior off-season — tool layer adds descriptive message).

    Args:
        limit: Maximum number of features to return.

    Returns:
        (list[dict], was_cached) — hurricane track feature dicts.
    """
    features, _, was_cached = await ogc_fetch(
        COLL_HURRICANE_TRACK,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    if not features:
        return [], False

    items = []
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry")
        lat, lon = extract_centroid(geom)
        items.append({
            "name": props.get("name"),
            "advisory": props.get("advisory"),
            "storm_category": props.get("storm_category"),
            "max_wind_kt": props.get("max_wind_kt"),
            "min_pressure_mb": props.get("min_pressure_mb"),
            "forecast_track": props.get("forecast_track"),
            "lat": lat,
            "lon": lon,
        })

    return items, was_cached


async def fetch_thunderstorm_outlook(
    province: str | None = None,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch thunderstorm outlook regions and risk levels.

    Returns an empty list when the collection is empty (expected off-season).

    Args:
        province: Two-letter province/territory code to filter by bbox.
        limit: Maximum number of features to return.

    Returns:
        (list[dict], was_cached) — thunderstorm outlook region dicts.
    """
    bbox = None
    if province and province.upper() in PROVINCE_BBOX:
        bbox = PROVINCE_BBOX[province.upper()]

    features, _, was_cached = await ogc_fetch(
        COLL_THUNDERSTORM,
        bbox=bbox,
        limit=limit,
        ttl=CACHE_TTL_FORECAST,
    )

    if not features:
        return [], False

    items = []
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry")
        lat, lon = extract_centroid(geom)
        items.append({
            "region_en": props.get("region_en"),
            "region_fr": props.get("region_fr"),
            "risk_en": props.get("risk_en"),
            "risk_fr": props.get("risk_fr"),
            "outlook_en": props.get("outlook_en"),
            "outlook_fr": props.get("outlook_fr"),
            "valid_from": props.get("valid_from"),
            "valid_to": props.get("valid_to"),
            "lat": lat,
            "lon": lon,
        })

    return items, was_cached
