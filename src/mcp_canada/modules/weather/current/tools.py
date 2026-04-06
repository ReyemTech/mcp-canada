"""MCP tool functions for weather/current sub-module.

Provides 5 tools: current conditions, forecast, weather alerts,
station search, and hourly station observations.

All tools use the wx_ prefix, accept lang: Literal["en", "fr"],
and return make_response() / make_error() envelopes.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.modules.weather.current.client import (
    fetch_alerts,
    fetch_current_conditions,
    fetch_forecast,
    fetch_hourly_obs,
    fetch_stations,
)
from mcp_canada.shared.envelope import make_error, make_response


@tool
async def wx_get_current_conditions(
    location: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    province: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get current weather conditions for a Canadian location.

    Returns temperature, humidity, wind, pressure, and sky conditions
    from the nearest Environment Canada city weather station.
    Provide a city name, lat/lon coordinates, or province code.

    Use for: current weather, temperature right now, what is the weather,
    current conditions, wind speed, humidity, feels like, wind chill

    Keywords: current weather conditions temperature humidity wind pressure
    sky condition weather now real-time observation city forecast station
    """
    data, was_cached = await fetch_current_conditions(
        location=location, lat=lat, lon=lon, province=province, lang=lang
    )
    if data is None:
        return make_error(
            "NOT_FOUND",
            "No current conditions found for the specified location.",
            lang=lang,
        )
    return make_response(
        data,
        api_name=API_NAME,
        api_url=BASE_URL,
        cached=was_cached,
        lang=lang,
    )


@tool
async def wx_get_forecast(
    location: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    province: str | None = None,
    days: int = 7,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the multi-day weather forecast for a Canadian location.

    Returns forecast periods (day/night pairs) with temperature, text
    summary, precipitation probability, and wind information.
    Forecasts come from Environment Canada's citypageweather collection.

    Use for: weather forecast, tomorrow weather, weekend forecast,
    week forecast, will it rain, precipitation probability, temperature high low

    Keywords: weather forecast tomorrow this weekend week rain snow temperature
    high low precipitation probability wind forecast period city Canada
    """
    periods, was_cached = await fetch_forecast(
        location=location, lat=lat, lon=lon, province=province, lang=lang
    )
    if not periods:
        return make_error(
            "NOT_FOUND",
            "No forecast data found for the specified location.",
            lang=lang,
        )

    # Limit to requested number of days (2 periods per day: day + night)
    max_periods = days * 2
    limited = periods[:max_periods]

    return make_response(
        limited,
        api_name=API_NAME,
        api_url=BASE_URL,
        cached=was_cached,
        lang=lang,
    )


@tool
async def wx_get_weather_alerts(
    province: str | None = None,
    alert_type: str | None = None,
    limit: int = 25,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get active weather alerts and warnings for Canada or a specific province.

    Returns current weather alerts including warnings, watches, advisories,
    and statements issued by Environment Canada. Filter by province code
    (e.g. "ON", "BC", "QC") or alert type (e.g. "warning", "watch").

    Use for: weather alerts warnings watches advisories active alerts
    weather warnings by province severe weather emergency alert

    Keywords: weather alert warning watch advisory statement severe weather
    environment Canada storm warning blizzard tornado flood heat warning
    province alert active emergency meteorological
    """
    alerts, was_cached = await fetch_alerts(
        province=province, alert_type=alert_type, limit=limit
    )
    return make_response(
        alerts,
        api_name=API_NAME,
        api_url=BASE_URL,
        cached=was_cached,
        lang=lang,
    )


@tool
async def wx_search_stations(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    name: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search for Environment Canada climate observation stations.

    Returns matching stations with ID, name, province, coordinates,
    elevation, and date ranges for available data types (hourly, daily, monthly).
    Search by province code, coordinates (nearest stations), or station name.

    Use for: find weather station, climate station search, nearest station,
    station ID lookup, observation station coordinates

    Keywords: climate station weather station observation station find station
    Environment Canada MSC station ID coordinates province hourly daily data
    CLIMATE_IDENTIFIER nearby stations
    """
    stations, was_cached = await fetch_stations(
        province=province, lat=lat, lon=lon, name=name
    )
    if not stations:
        return make_error(
            "NOT_FOUND",
            "No climate stations found for the specified location.",
            lang=lang,
        )
    return make_response(
        stations,
        api_name=API_NAME,
        api_url=BASE_URL,
        cached=was_cached,
        lang=lang,
    )


@tool
async def wx_get_station_data(
    station_id: str,
    date: str | None = None,
    limit: int = 24,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get hourly climate observations from a specific Environment Canada station.

    Returns raw hourly observation records including temperature, dew point,
    wind speed/direction, weather description, and station pressure.
    Use wx_search_stations to find a station_id (CLIMATE_IDENTIFIER).

    Use for: hourly observations station data raw climate data temperature
    readings wind measurements dew point historical hourly data

    Keywords: hourly climate observations station data CLIMATE_IDENTIFIER
    temperature dew point wind direction speed pressure weather description
    raw observations historical hourly readings Environment Canada
    """
    obs, was_cached = await fetch_hourly_obs(
        station_id=station_id, date=date, limit=limit
    )
    if not obs:
        return make_error(
            "NOT_FOUND",
            f"No hourly observations found for station '{station_id}'.",
            lang=lang,
        )
    return make_response(
        obs,
        api_name=API_NAME,
        api_url=BASE_URL,
        cached=was_cached,
        lang=lang,
    )
