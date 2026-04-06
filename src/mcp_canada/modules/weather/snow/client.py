"""Snow conditions client for MSC GeoMet OGC API.

Provides async functions for snow depth from SWOB real-time observations
and estimated snow water equivalent. All functions return (data, was_cached) tuples.

Collections used:
- swob-realtime — Surface Weather Observation Bulletin real-time observations
  containing snw_dpth-value, snw_dpth_1-value, snw_dpth_2-value, air_temp-value

Snow depth notes:
- snw_dpth-value is the primary sensor reading (cm)
- snw_dpth_1-value and snw_dpth_2-value are backup sensors (Pitfall 4)
- Some stations lack snow sensors entirely — always check if field is present
"""

from typing import Any

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_REALTIME,
    COLL_SWOB,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, ogc_fetch


def _extract_snow_depth(props: dict[str, Any]) -> float | None:
    """Extract snow depth in cm from SWOB properties with multi-sensor fallback.

    Uses primary sensor (snw_dpth-value) first. Falls back to average of
    snw_dpth_1-value and snw_dpth_2-value (and _3 if present) when primary
    is absent or None (Pitfall 4).

    Always uses: `if field in props and props[field] is not None`
    to safely handle sparse SWOB observations.

    Args:
        props: Feature properties dict from SWOB real-time observation.

    Returns:
        Snow depth in cm as float, or None if no snow sensor data available.
    """
    # Primary sensor
    if "snw_dpth-value" in props and props["snw_dpth-value"] is not None:
        try:
            return float(props["snw_dpth-value"])
        except (TypeError, ValueError):
            pass

    # Multi-sensor fallback: average available backup sensors
    backup_values = []
    for backup_key in ("snw_dpth_1-value", "snw_dpth_2-value", "snw_dpth_3-value"):
        if backup_key in props and props[backup_key] is not None:
            try:
                backup_values.append(float(props[backup_key]))
            except (TypeError, ValueError):
                pass

    if backup_values:
        return sum(backup_values) / len(backup_values)

    return None


async def fetch_snow_depth(
    station_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    """Fetch snow depth from the nearest SWOB real-time observation station.

    Queries swob-realtime collection sorted by newest observation first.
    Extracts snw_dpth-value with multi-sensor fallback (Pitfall 4).

    Args:
        station_id: MSC station ID (msc_id) to query directly.
        lat: Latitude for location-based search (0.5 degree bbox).
        lon: Longitude for location-based search.

    Returns:
        (dict, was_cached) with station_name, snow_depth_cm, observed_at,
        air_temp_c, lat, lon — or (None, False) if no features found.
    """
    bbox = None
    properties = None

    if station_id is not None:
        properties = {"msc_id": station_id}
    elif lat is not None and lon is not None:
        # Use 0.5 degree bbox (~55km) for station search
        bbox = build_bbox(lat, lon, radius_km=55)

    features, _, was_cached = await ogc_fetch(
        COLL_SWOB,
        bbox=bbox,
        properties=properties,
        sortby="-date_tm-value",
        limit=1,
        ttl=CACHE_TTL_REALTIME,
    )

    if not features:
        return None, False

    feature = features[0]
    props = feature.get("properties", {})
    geom = feature.get("geometry")
    feat_lat, feat_lon = extract_centroid(geom)

    snow_depth_cm = _extract_snow_depth(props)

    # Extract air temperature if available
    air_temp_c = None
    if "air_temp-value" in props and props["air_temp-value"] is not None:
        try:
            air_temp_c = float(props["air_temp-value"])
        except (TypeError, ValueError):
            pass

    return {
        "station_name": props.get("stn_nam-value"),
        "station_id": props.get("msc_id-value"),
        "snow_depth_cm": snow_depth_cm,
        "observed_at": props.get("date_tm-value"),
        "air_temp_c": air_temp_c,
        "lat": feat_lat if feat_lat is not None else props.get("lat-value"),
        "lon": feat_lon if feat_lon is not None else props.get("lon-value"),
    }, was_cached


async def fetch_snow_water_equivalent(
    station_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    density_factor: float = 0.3,
) -> tuple[dict[str, Any] | None, bool]:
    """Estimate snow water equivalent from snow depth using a density factor.

    No direct SWE collection exists in the MSC GeoMet OGC API. This is a
    best-effort estimate using: SWE (mm) = snow_depth_cm * density_factor.

    Args:
        station_id: MSC station ID for direct station query.
        lat: Latitude for location-based search.
        lon: Longitude for location-based search.
        density_factor: Snow density as fraction (default 0.3 for settled snow).
                        0.05-0.1 for fresh powder, 0.3 for settled, 0.5 for old/compacted.

    Returns:
        (dict, was_cached) with station_name, snow_depth_cm, swe_mm, density_factor,
        observed_at, and note explaining the estimation — or (None, False) if no data.
    """
    depth_data, was_cached = await fetch_snow_depth(
        station_id=station_id, lat=lat, lon=lon
    )

    if depth_data is None:
        return None, False

    snow_depth_cm = depth_data.get("snow_depth_cm")

    # Calculate SWE estimate if snow depth is available
    swe_mm = None
    if snow_depth_cm is not None:
        swe_mm = round(snow_depth_cm * density_factor, 2)

    return {
        "station_name": depth_data.get("station_name"),
        "station_id": depth_data.get("station_id"),
        "snow_depth_cm": snow_depth_cm,
        "swe_mm": swe_mm,
        "density_factor": density_factor,
        "observed_at": depth_data.get("observed_at"),
        "air_temp_c": depth_data.get("air_temp_c"),
        "lat": depth_data.get("lat"),
        "lon": depth_data.get("lon"),
        "note": (
            "Estimated from snow depth using density factor. Not a direct measurement. "
            "Adjust density_factor for different snow types: "
            "0.05-0.1 for fresh powder, 0.3 for settled snow, 0.5 for old compacted snow."
        ),
    }, was_cached
