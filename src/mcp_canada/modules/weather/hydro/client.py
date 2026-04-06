"""Hydrometric client functions for MSC GeoMet water monitoring collections.

All public functions return (data, was_cached) tuples.
Flattens GeoJSON features into plain dicts for agent consumption.
fetch_flood_risk is a composite that compares realtime levels to historical peaks.
"""

import asyncio

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_REALTIME,
    CACHE_TTL_STATIONS,
    COLL_HYDRO_DAILY,
    COLL_HYDRO_PEAKS,
    COLL_HYDRO_REALTIME,
    COLL_HYDRO_STATIONS,
    PROVINCE_BBOX,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, nearest_station, ogc_fetch


def _flatten_hydro_realtime(feature: dict) -> dict:
    """Flatten a hydrometric-realtime GeoJSON feature into a plain dict."""
    props = feature.get("properties") or {}
    lat, lon = extract_centroid(feature.get("geometry"))
    return {
        "station_number": props.get("STATION_NUMBER"),
        "station_name": props.get("STATION_NAME"),
        "level_m": props.get("LEVEL"),
        "discharge_m3s": props.get("DISCHARGE"),
        "datetime": props.get("DATETIME"),
        "lat": lat,
        "lon": lon,
    }


def _flatten_hydro_station(feature: dict) -> dict:
    """Flatten a hydrometric-stations GeoJSON feature into a plain dict."""
    props = feature.get("properties") or {}
    lat, lon = extract_centroid(feature.get("geometry"))
    return {
        "station_number": props.get("STATION_NUMBER"),
        "station_name": props.get("STATION_NAME"),
        "province": props.get("PROVINCE_TERR"),
        "lat": lat,
        "lon": lon,
        "status": props.get("STATUS_EN"),
        "real_time": props.get("REAL_TIME") == "Y",
        "drainage_area_km2": props.get("DRAINAGE_AREA_GROSS"),
    }


def _flatten_hydro_daily(feature: dict) -> dict:
    """Flatten a hydrometric-daily-mean GeoJSON feature into a plain dict."""
    props = feature.get("properties") or {}
    lat, lon = extract_centroid(feature.get("geometry"))
    return {
        "station_number": props.get("STATION_NUMBER"),
        "station_name": props.get("STATION_NAME"),
        "level_m": props.get("LEVEL"),
        "discharge_m3s": props.get("DISCHARGE"),
        "date": props.get("DATE") or props.get("DATETIME"),
        "lat": lat,
        "lon": lon,
    }


async def fetch_water_levels(
    station_number: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 10,
) -> tuple[list[dict], bool]:
    """Fetch real-time water levels for a hydrometric station.

    Args:
        station_number: WSC station number (e.g. "02LA004").
        lat: Latitude for nearest station lookup.
        lon: Longitude for nearest station lookup.
        limit: Maximum number of readings to return.

    Returns:
        (readings, was_cached) of flattened water level dicts.
    """
    if station_number is None and lat is not None and lon is not None:
        station_feat = await nearest_station(lat, lon, collection_id="hydrometric-stations")
        if station_feat:
            props = station_feat.get("properties") or {}
            station_number = props.get("STATION_NUMBER")

    if station_number is None:
        return [], False

    features, _, was_cached = await ogc_fetch(
        COLL_HYDRO_REALTIME,
        properties={"STATION_NUMBER": station_number},
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    return [_flatten_hydro_realtime(f) for f in features], was_cached


async def fetch_water_flow(
    station_number: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 10,
) -> tuple[list[dict], bool]:
    """Fetch real-time discharge (water flow) for a hydrometric station.

    Args:
        station_number: WSC station number (e.g. "02LA004").
        lat: Latitude for nearest station lookup.
        lon: Longitude for nearest station lookup.
        limit: Maximum number of readings to return.

    Returns:
        (readings, was_cached) of flattened readings with discharge_m3s data.
    """
    # Same underlying data as water levels — discharge is in the same realtime collection
    return await fetch_water_levels(station_number=station_number, lat=lat, lon=lon, limit=limit)


async def fetch_daily_mean_water(
    station_number: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> tuple[list[dict], bool]:
    """Fetch daily mean water level and discharge for a hydrometric station.

    Args:
        station_number: WSC station number (e.g. "02LA004").
        start_date: ISO 8601 date string for range start (e.g. "2026-04-01").
        end_date: ISO 8601 date string for range end (e.g. "2026-04-30").
        limit: Maximum number of days to return.

    Returns:
        (readings, was_cached) of flattened daily mean dicts.
    """
    datetime_filter: str | None = None
    if start_date and end_date:
        datetime_filter = f"{start_date}/{end_date}"
    elif start_date:
        datetime_filter = f"{start_date}/.."
    elif end_date:
        datetime_filter = f"../{end_date}"

    features, _, was_cached = await ogc_fetch(
        COLL_HYDRO_DAILY,
        properties={"STATION_NUMBER": station_number},
        datetime_filter=datetime_filter,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    return [_flatten_hydro_daily(f) for f in features], was_cached


async def fetch_hydro_stations(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    name: str | None = None,
    limit: int = 50,
) -> tuple[list[dict], bool]:
    """Search for hydrometric monitoring stations.

    Args:
        province: Two-letter province/territory code (e.g. "ON", "BC").
        lat: Latitude for spatial search around a point.
        lon: Longitude for spatial search around a point.
        name: Station name filter (not used as direct property filter — broad search via bbox).
        limit: Maximum number of stations to return.

    Returns:
        (stations, was_cached) of flattened station info dicts.
    """
    bbox = None
    if province is not None:
        prov_upper = province.upper()
        bbox = PROVINCE_BBOX.get(prov_upper)
    elif lat is not None and lon is not None:
        bbox = build_bbox(lat, lon, radius_km=100)

    features, _, was_cached = await ogc_fetch(
        COLL_HYDRO_STATIONS,
        bbox=bbox,
        limit=limit,
        ttl=CACHE_TTL_STATIONS,
    )

    stations = [_flatten_hydro_station(f) for f in features]

    # Optional name filter (client-side fuzzy match on station_name)
    if name is not None:
        name_lower = name.lower()
        stations = [s for s in stations if name_lower in (s.get("station_name") or "").lower()]

    return stations, was_cached


def _classify_flood_risk(percent_of_max: float) -> str:
    """Classify flood risk based on current level as a percentage of historical max.

    Args:
        percent_of_max: Current discharge as a percentage of historical max discharge.

    Returns:
        Risk level string: "low", "moderate", "high", or "critical".
    """
    if percent_of_max >= 100:
        return "critical"
    if percent_of_max >= 80:
        return "high"
    if percent_of_max >= 60:
        return "moderate"
    return "low"


async def fetch_flood_risk(
    station_number: str,
) -> tuple[dict | None, bool]:
    """Fetch flood risk assessment for a hydrometric station.

    Composites real-time water levels with historical annual peak data.
    Compares current discharge to the historical maximum to classify risk.

    Args:
        station_number: WSC station number (e.g. "02LA004").

    Returns:
        (risk_assessment_dict, was_cached) or (None, False) if data unavailable.
        Risk assessment contains: station_number, station_name, current_level,
        current_discharge, historical_max, historical_max_discharge,
        percent_of_max, risk_level.
    """
    # Fetch current levels and historical peaks concurrently
    (current_readings, current_cached), (peak_features, _, peaks_cached) = (
        await asyncio.gather(
            fetch_water_levels(station_number, limit=1),
            ogc_fetch(
                COLL_HYDRO_PEAKS,
                properties={"STATION_NUMBER": station_number},
                limit=100,
                ttl=CACHE_TTL_STATIONS,
            ),
        )
    )

    if not current_readings:
        return None, False

    current = current_readings[0]
    was_cached = current_cached and peaks_cached

    # Find historical max discharge from annual peaks
    max_discharge: float | None = None
    max_level: float | None = None
    for peak_feat in peak_features:
        props = peak_feat.get("properties") or {}
        d = props.get("DISCHARGE")
        lv = props.get("LEVEL")
        if d is not None:
            if max_discharge is None or d > max_discharge:
                max_discharge = float(d)
                max_level = float(lv) if lv is not None else None

    current_discharge = current.get("discharge_m3s")
    current_level = current.get("level_m")

    percent_of_max: float | None = None
    risk_level = "low"

    if max_discharge is not None and current_discharge is not None and max_discharge > 0:
        percent_of_max = round((current_discharge / max_discharge) * 100, 1)
        risk_level = _classify_flood_risk(percent_of_max)
    elif current_discharge is not None and current_discharge > 0 and max_discharge is None:
        # No historical peaks — can't assess risk properly
        percent_of_max = None
        risk_level = "low"

    return {
        "station_number": current.get("station_number"),
        "station_name": current.get("station_name"),
        "current_level": current_level,
        "current_discharge": current_discharge,
        "historical_max": max_level,
        "historical_max_discharge": max_discharge,
        "percent_of_max": percent_of_max,
        "risk_level": risk_level,
        "datetime": current.get("datetime"),
        "lat": current.get("lat"),
        "lon": current.get("lon"),
    }, was_cached
