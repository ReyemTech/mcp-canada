"""Hydrometric @tool functions for MSC GeoMet water monitoring data.

Provides 5 MCP tools for querying real-time water levels, discharge, daily means,
station search, and flood risk assessment from the Water Survey of Canada
hydrometric network via MSC GeoMet OGC API.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.hydro.client import (
    fetch_daily_mean_water,
    fetch_flood_risk,
    fetch_hydro_stations,
    fetch_water_flow,
    fetch_water_levels,
)
from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.shared.envelope import INVALID_INPUT, NOT_FOUND, UPSTREAM_ERROR, make_error, make_response

_API_URL = BASE_URL


@tool
async def wx_get_water_levels(
    station_number: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get real-time water level readings at a Canadian hydrometric station.

    Use for: getting current water level, river height, lake level, stream gauge
    reading, or water stage at a Canadian monitoring station.
    Keywords: water level, river, lake, stream, gauge, hydrology, stage, height,
    hydrometric, monitoring, wsc, water survey, realtime, current, station, flood,
    level, metre, waterbody, canadian.
    """
    if station_number is None and (lat is None or lon is None):
        return make_error(
            INVALID_INPUT,
            "Provide a station_number or lat/lon coordinates to get water level readings.",
            lang=lang,
        )

    try:
        readings, cached = await fetch_water_levels(
            station_number=station_number, lat=lat, lon=lon
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Hydrometric API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            "No water level data found for the given station or location.",
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
async def wx_get_water_flow(
    station_number: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get real-time water discharge (flow rate) at a Canadian hydrometric station.

    Use for: getting current river flow, stream discharge, water flow rate,
    cubic metres per second reading, or streamflow at a Canadian monitoring station.
    Keywords: water flow, discharge, streamflow, flow rate, river, cubic metres,
    m3s, hydrometric, wsc, water survey, realtime, current, station, flood,
    hydrology, runoff, waterbody, canadian.
    """
    if station_number is None and (lat is None or lon is None):
        return make_error(
            INVALID_INPUT,
            "Provide a station_number or lat/lon coordinates to get water flow data.",
            lang=lang,
        )

    try:
        readings, cached = await fetch_water_flow(
            station_number=station_number, lat=lat, lon=lon
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Hydrometric API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            "No water flow data found for the given station or location.",
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
async def wx_get_daily_mean_water(
    station_number: str,
    start_date: str | None = None,
    end_date: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get daily mean water level and discharge for a hydrometric station.

    Use for: historical daily water level averages, mean river flow over time,
    daily discharge trends, water level history for flood or drought analysis.
    Keywords: daily mean, water level, discharge, historical, average, trend,
    river, stream, hydrology, hydrometric, wsc, daily, flow, date range,
    station, analysis, flood, drought, canadian.
    """
    try:
        readings, cached = await fetch_daily_mean_water(
            station_number,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Hydrometric daily API error: {exc}", lang=lang)

    if not readings:
        return make_error(
            NOT_FOUND,
            f"No daily mean data found for station '{station_number}'.",
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
async def wx_search_hydro_stations(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    name: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search for hydrometric water monitoring stations by province or location.

    Use for: finding Water Survey of Canada stations near a location, listing
    hydrometric gauges in a province, searching for river monitoring stations.
    Keywords: hydrometric station, water station, gauge, wsc, water survey,
    river, monitoring, search, province, location, nearby, list, stations,
    hydrology, flood monitoring, realtime, canadian, infrastructure.
    """
    if province is None and lat is None and lon is None:
        return make_error(
            INVALID_INPUT,
            "Provide a province code (e.g. 'ON') or lat/lon coordinates to search for stations.",
            lang=lang,
        )

    try:
        stations, cached = await fetch_hydro_stations(
            province=province, lat=lat, lon=lon, name=name
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Hydrometric stations API error: {exc}", lang=lang)

    if not stations:
        return make_error(
            NOT_FOUND,
            "No hydrometric stations found for the given criteria.",
            lang=lang,
        )

    return make_response(
        stations,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def wx_get_flood_risk(
    station_number: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get flood risk assessment for a hydrometric station by comparing current to historical max.

    Composites real-time water levels with historical annual peak discharge records
    to classify current flood risk as low, moderate, high, or critical.
    Current discharge is expressed as a percentage of the station's recorded maximum.

    Use for: assessing flood risk, comparing current river conditions to historical
    peaks, evaluating flood threat level, flood safety assessment, water management.
    Keywords: flood risk, flooding, risk level, river, discharge, historical maximum,
    peak discharge, flood assessment, water level, hydrometric, wsc, safety,
    emergency management, percent of max, flood threat, critical, high risk,
    moderate, flood monitoring, canadian, water survey.
    """
    try:
        risk, cached = await fetch_flood_risk(station_number)
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, f"Flood risk API error: {exc}", lang=lang)

    if risk is None:
        return make_error(
            NOT_FOUND,
            f"No data available for flood risk assessment at station '{station_number}'.",
            lang=lang,
        )

    return make_response(
        risk,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
