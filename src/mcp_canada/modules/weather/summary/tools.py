"""Weather summary @tool functions for MSC GeoMet.

Provides 4 MCP tools for composite and specialized weather data:
- wx_get_weather_summary: one-call composite of conditions + forecast + alerts + AQHI
- wx_get_historical_extremes: all-time temperature/precipitation/snowfall records
- wx_get_growing_season: frost-free period and growing season dates from climate normals
- wx_get_heating_cooling_days: cumulative degree days for energy analysis
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.modules.weather.summary.client import (
    fetch_growing_season,
    fetch_heating_cooling_days,
    fetch_historical_extremes,
    fetch_weather_summary,
)
from mcp_canada.shared.envelope import INVALID_INPUT, NOT_FOUND, UPSTREAM_ERROR, make_error, make_response

_API_URL = BASE_URL


@tool
async def wx_get_weather_summary(
    lat: float | None = None,
    lon: float | None = None,
    location: str | None = None,
    province: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get a comprehensive weather summary combining current conditions, forecast, active alerts, and air quality.

    Use for: getting a complete weather overview in one call, checking everything about the weather
    at a location, full weather briefing, weather snapshot combining conditions forecast alerts air quality.
    Keywords: weather summary, overview, complete, comprehensive, conditions forecast alerts aqhi,
    all weather, weather briefing, current conditions forecast, air quality, composite,
    one-call weather, everything weather, weather overview, canada weather, environment canada.
    """
    if lat is None and lon is None and location is None and province is None:
        return make_error(
            INVALID_INPUT,
            "Provide at least one location input: lat/lon coordinates, a city name (location), or a province code.",
            lang=lang,
        )

    try:
        summary, cached = await fetch_weather_summary(
            lat=lat, lon=lon, location=location, province=province, lang=lang
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Weather summary error: {exc}", lang=lang)

    return make_response(
        summary,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_historical_extremes(
    station_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get all-time weather records for a climate station: highest/lowest temperatures, most precipitation, most snowfall.

    Use for: finding all-time records, historical extremes, record high temperature, record low temperature,
    most rain ever, most snow ever, climate records, long-term extremes for a station.
    Keywords: historical extremes, all-time records, record high, record low, temperature records,
    precipitation records, snowfall records, climate records, ltce, long-term climate extremes,
    maximum minimum, historical, station records, weather records, canada climate.
    """
    try:
        extremes, cached = await fetch_historical_extremes(station_id)
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Historical extremes API error: {exc}", lang=lang)

    return make_response(
        extremes,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_growing_season(
    station_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get growing season dates and frost-free period for a climate station based on 30-year normals.

    Use for: finding the last spring frost date, first fall frost date, frost-free period length,
    growing season length, planting dates, agriculture planning, gardening frost risk.
    Keywords: growing season, frost free, frost date, last spring frost, first fall frost,
    planting date, agriculture, gardening, climate normals, frost period, frost risk,
    growing days, frost free period, seasonal, plant hardiness, canada agriculture.
    """
    try:
        data, cached = await fetch_growing_season(station_id)
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Growing season API error: {exc}", lang=lang)

    if data is None:
        return make_error(
            NOT_FOUND,
            f"No climate normals found for station '{station_id}'. "
            "Use wx_search_stations to find a valid station ID.",
            lang=lang,
        )

    return make_response(
        data,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_heating_cooling_days(
    station_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get cumulative heating and cooling degree days for energy analysis at a climate station.

    Use for: heating degree days, cooling degree days, energy consumption analysis, HVAC planning,
    building energy modeling, degree days for a period, heating season summary, cooling season summary.
    Keywords: heating degree days, cooling degree days, hdd, cdd, energy, hvac, degree days,
    heating season, cooling season, energy analysis, climate daily, building energy, energy modeling,
    temperature base 18, cumulative degree days, climate data, station data.

    Note: Dates should be formatted as YYYY-MM-DD (e.g. '2025-01-01'). Omit dates to get all available data.
    """
    try:
        data, cached = await fetch_heating_cooling_days(
            station_id, start_date=start_date, end_date=end_date
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Heating/cooling degree days API error: {exc}", lang=lang)

    return make_response(
        data,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
