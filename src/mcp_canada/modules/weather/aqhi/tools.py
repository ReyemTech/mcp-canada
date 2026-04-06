"""AQHI (Air Quality Health Index) @tool functions for MSC GeoMet.

Provides 3 MCP tools for querying real-time and historical air quality data
from Environment and Climate Change Canada's AQHI network.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.aqhi.client import (
    fetch_aqhi,
    fetch_aqhi_forecast,
    fetch_aqhi_history,
)
from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.shared.envelope import INVALID_INPUT, NOT_FOUND, UPSTREAM_ERROR, make_error, make_response

_API_URL = BASE_URL


@tool
async def wx_get_aqhi(
    lat: float | None = None,
    lon: float | None = None,
    location_id: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get current Air Quality Health Index (AQHI) reading for a location.

    Use for: checking current air quality health index, AQI, air pollution level,
    smog advisory, or air quality risk at a location in Canada.
    Keywords: aqhi, air quality, health index, pollution, smog, aqi, outdoor air,
    breathe, ozone, particulate, environment canada, air, quality, advisory,
    atmosphere, environment, health, risk, realtime, current.
    """
    if lat is None and lon is None and location_id is None:
        return make_error(
            INVALID_INPUT,
            "Provide lat/lon coordinates or a location_id to get AQHI readings.",
            lang=lang,
        )

    try:
        readings, cached = await fetch_aqhi(lat=lat, lon=lon, location_id=location_id)
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"AQHI API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            "No AQHI readings found for the given location.",
            lang=lang,
        )

    return make_response(
        readings,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_aqhi_forecast(
    lat: float | None = None,
    lon: float | None = None,
    location_id: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get AQHI air quality forecast periods for a location.

    Use for: getting forecasted air quality health index, future air quality,
    upcoming smog or pollution forecast, tomorrow's air quality in Canada.
    Keywords: aqhi, forecast, air quality, future, tomorrow, smog, pollution,
    aqi, outdoor, breathe, environment canada, air, quality, prediction,
    upcoming, advisory, period, health, risk, forecast.
    """
    if lat is None and lon is None and location_id is None:
        return make_error(
            INVALID_INPUT,
            "Provide lat/lon coordinates or a location_id to get AQHI forecasts.",
            lang=lang,
        )

    try:
        readings, cached = await fetch_aqhi_forecast(
            lat=lat, lon=lon, location_id=location_id
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"AQHI forecast API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            "No AQHI forecast found for the given location.",
            lang=lang,
        )

    return make_response(
        readings,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_aqhi_history(
    location_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get historical AQHI observations for a location with optional date range.

    Use for: historical air quality health index data, past AQHI readings,
    air quality trend analysis, seasonal pollution patterns at a Canadian location.
    Keywords: aqhi, history, historical, past, air quality, trend, analysis,
    seasonal, pollution, smog, location_id, date range, observations,
    environment canada, air, quality, health, index, record, archive.
    """
    try:
        readings, cached = await fetch_aqhi_history(
            location_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"AQHI history API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            f"No historical AQHI data found for location_id '{location_id}'.",
            lang=lang,
        )

    return make_response(
        readings,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
