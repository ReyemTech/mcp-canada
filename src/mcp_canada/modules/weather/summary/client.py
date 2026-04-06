"""Client functions for weather/summary sub-module.

Provides composite fetch functions that combine multiple data sources
using asyncio.gather for parallel fetching.

All functions return (data, was_cached) tuples.
"""

import asyncio

from mcp_canada.modules.weather.aqhi.client import fetch_aqhi
from mcp_canada.modules.weather.constants import (
    CACHE_TTL_CLIMATE,
    COLL_CLIMATE_DAILY,
    COLL_CLIMATE_NORMALS,
    COLL_LTCE_PRECIP,
    COLL_LTCE_SNOW,
    COLL_LTCE_TEMP,
)
from mcp_canada.modules.weather.current.client import (
    fetch_alerts,
    fetch_current_conditions,
    fetch_forecast,
)
from mcp_canada.shared.geo import ogc_fetch


async def fetch_weather_summary(
    lat: float | None = None,
    lon: float | None = None,
    location: str | None = None,
    province: str | None = None,
    lang: str = "en",
) -> tuple[dict, bool]:
    """Fetch a comprehensive weather summary combining 4 data sources in parallel.

    Uses asyncio.gather with return_exceptions=True to fetch current conditions,
    forecast, weather alerts, and AQHI simultaneously. Failures in any source
    are handled gracefully — the other sections are still returned.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        location: City name for text-match filtering.
        province: Province code (e.g. "ON") for province-wide queries.
        lang: Language for bilingual fields ("en" or "fr").

    Returns:
        (summary dict with conditions/forecast/alerts/aqhi sections, was_cached).
    """
    raw_results = await asyncio.gather(
        fetch_current_conditions(lat=lat, lon=lon, location=location, province=province, lang=lang),
        fetch_forecast(lat=lat, lon=lon, location=location, province=province, lang=lang),
        fetch_alerts(province=province),
        fetch_aqhi(lat=lat, lon=lon),
        return_exceptions=True,
    )

    conditions_result = raw_results[0]
    forecast_result = raw_results[1]
    alerts_result = raw_results[2]
    aqhi_result = raw_results[3]

    # Extract data and cached flags, handling exceptions
    conditions: dict | None
    conditions_cached: bool
    if isinstance(conditions_result, BaseException):
        conditions = None
        conditions_cached = False
    else:
        conditions, conditions_cached = conditions_result  # type: ignore[misc]

    forecast: list[dict]
    forecast_cached: bool
    if isinstance(forecast_result, BaseException):
        forecast = []
        forecast_cached = False
    else:
        forecast, forecast_cached = forecast_result  # type: ignore[misc]

    alerts: list[dict]
    alerts_cached: bool
    if isinstance(alerts_result, BaseException):
        alerts = []
        alerts_cached = False
    else:
        alerts, alerts_cached = alerts_result  # type: ignore[misc]

    aqhi: list[dict]
    aqhi_cached: bool
    if isinstance(aqhi_result, BaseException):
        aqhi = []
        aqhi_cached = False
    else:
        aqhi, aqhi_cached = aqhi_result  # type: ignore[misc]

    # was_cached is True only if ALL successful fetches were cached
    was_cached = all([conditions_cached, forecast_cached, alerts_cached, aqhi_cached])

    summary = {
        "conditions": conditions,
        "forecast": forecast,
        "alerts": alerts,
        "aqhi": aqhi,
    }

    return summary, was_cached


async def fetch_historical_extremes(
    station_id: str,
    limit: int = 50,
) -> tuple[dict, bool]:
    """Fetch all-time weather records for a climate station.

    Fetches ltce-temperature, ltce-precipitation, and ltce-snowfall collections
    in parallel using asyncio.gather, filtered by CLIMATE_IDENTIFIER.

    Args:
        station_id: CLIMATE_IDENTIFIER for the station (e.g. "6105976").
        limit: Maximum number of records per collection (default 50).

    Returns:
        (dict with temperature_records, precipitation_records, snowfall_records, was_cached).
    """
    props = {"CLIMATE_IDENTIFIER": station_id}

    temp_result, precip_result, snow_result = await asyncio.gather(
        ogc_fetch(COLL_LTCE_TEMP, properties=props, limit=limit, ttl=CACHE_TTL_CLIMATE),
        ogc_fetch(COLL_LTCE_PRECIP, properties=props, limit=limit, ttl=CACHE_TTL_CLIMATE),
        ogc_fetch(COLL_LTCE_SNOW, properties=props, limit=limit, ttl=CACHE_TTL_CLIMATE),
        return_exceptions=False,
    )

    temp_features, _, temp_cached = temp_result
    precip_features, _, precip_cached = precip_result
    snow_features, _, snow_cached = snow_result

    def _flatten_temp(f: dict) -> dict:
        p = f.get("properties", {})
        return {
            "station_id": p.get("CLIMATE_IDENTIFIER"),
            "station_name": p.get("STATION_NAME"),
            "month": p.get("LOCAL_MONTH"),
            "day": p.get("LOCAL_DAY"),
            "record_high_c": p.get("RECORD_HIGH_MAX_TEMP"),
            "record_high_year": p.get("RECORD_HIGH_MAX_TEMP_YEAR"),
            "record_low_c": p.get("RECORD_LOW_MIN_TEMP"),
            "record_low_year": p.get("RECORD_LOW_MIN_TEMP_YEAR"),
        }

    def _flatten_precip(f: dict) -> dict:
        p = f.get("properties", {})
        return {
            "station_id": p.get("CLIMATE_IDENTIFIER"),
            "station_name": p.get("STATION_NAME"),
            "month": p.get("LOCAL_MONTH"),
            "day": p.get("LOCAL_DAY"),
            "record_max_precip_mm": p.get("RECORD_MAX_PRECIP"),
            "record_year": p.get("RECORD_MAX_PRECIP_YEAR"),
        }

    def _flatten_snow(f: dict) -> dict:
        p = f.get("properties", {})
        return {
            "station_id": p.get("CLIMATE_IDENTIFIER"),
            "station_name": p.get("STATION_NAME"),
            "month": p.get("LOCAL_MONTH"),
            "day": p.get("LOCAL_DAY"),
            "record_max_snowfall_cm": p.get("RECORD_MAX_SNOWFALL"),
            "record_year": p.get("RECORD_MAX_SNOWFALL_YEAR"),
        }

    was_cached = all([temp_cached, precip_cached, snow_cached])

    return {
        "station_id": station_id,
        "temperature_records": [_flatten_temp(f) for f in temp_features],
        "precipitation_records": [_flatten_precip(f) for f in precip_features],
        "snowfall_records": [_flatten_snow(f) for f in snow_features],
    }, was_cached


async def fetch_growing_season(
    station_id: str,
) -> tuple[dict | None, bool]:
    """Fetch growing season and frost-free period from climate normals.

    Args:
        station_id: CLIMATE_IDENTIFIER for the station (e.g. "6105976").

    Returns:
        (growing season dict with frost dates and days, was_cached), or (None, was_cached).
    """
    features, _, was_cached = await ogc_fetch(
        COLL_CLIMATE_NORMALS,
        properties={"CLIMATE_IDENTIFIER": station_id},
        limit=50,
        ttl=CACHE_TTL_CLIMATE,
    )

    if not features:
        return None, was_cached

    # Use the first feature that has frost-free data
    for feature in features:
        p = feature.get("properties", {})
        frost_free = p.get("FROST_FREE_PERIOD")
        last_spring = p.get("LAST_SPRING_FROST_DATE_30YR")
        first_fall = p.get("FIRST_FALL_FROST_DATE_30YR")

        if frost_free is not None or last_spring is not None or first_fall is not None:
            return {
                "station_id": station_id,
                "station_name": p.get("STATION_NAME"),
                "last_spring_frost": last_spring,
                "first_fall_frost": first_fall,
                "growing_season_days": frost_free,
            }, was_cached

    # Return from first feature even if no frost data
    p = features[0].get("properties", {})
    return {
        "station_id": station_id,
        "station_name": p.get("STATION_NAME"),
        "last_spring_frost": None,
        "first_fall_frost": None,
        "growing_season_days": None,
    }, was_cached


async def fetch_heating_cooling_days(
    station_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 365,
) -> tuple[dict, bool]:
    """Fetch and sum heating and cooling degree days from climate-daily.

    Args:
        station_id: CLIMATE_IDENTIFIER for the station (e.g. "6105976").
        start_date: ISO date string for range start (e.g. "2025-01-01").
        end_date: ISO date string for range end (e.g. "2025-12-31").
        limit: Maximum number of daily records to fetch (default 365).

    Returns:
        (dict with total_heating_dd, total_cooling_dd, days_counted, was_cached).
    """
    datetime_filter: str | None = None
    if start_date and end_date:
        datetime_filter = f"{start_date}/{end_date}"
    elif start_date:
        datetime_filter = f"{start_date}/.."
    elif end_date:
        datetime_filter = f"../{end_date}"

    features, _, was_cached = await ogc_fetch(
        COLL_CLIMATE_DAILY,
        properties={"CLIMATE_IDENTIFIER": station_id},
        datetime_filter=datetime_filter,
        limit=limit,
        ttl=CACHE_TTL_CLIMATE,
    )

    total_heating = 0.0
    total_cooling = 0.0
    days_counted = 0

    for f in features:
        p = f.get("properties", {})
        hdd = p.get("HEATING_DEGREE_DAYS")
        cdd = p.get("COOLING_DEGREE_DAYS")
        if hdd is not None:
            total_heating += float(hdd)
        if cdd is not None:
            total_cooling += float(cdd)
        days_counted += 1

    period = datetime_filter or "all-available"

    return {
        "station_id": station_id,
        "period": period,
        "total_heating_dd": round(total_heating, 1),
        "total_cooling_dd": round(total_cooling, 1),
        "days_counted": days_counted,
    }, was_cached
