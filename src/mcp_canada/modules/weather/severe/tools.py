"""Severe weather @tool functions for MSC GeoMet OGC API.

Provides 3 tools for severe weather monitoring:
- wx_get_radar_data — radar precipitation accumulation (24h)
- wx_get_lightning — structured error pointing to MSC DataMart (no OGC collection)
- wx_get_uv_index — UV index extracted from citypageweather forecast

Each tool uses standalone @tool decorator, bilingual lang parameter,
and make_response/make_error envelopes.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.modules.weather.severe.client import (
    fetch_radar_data,
    fetch_uv_index,
)
from mcp_canada.shared.envelope import make_error, make_response

_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 4: Radar precipitation data (WX-20)
# ---------------------------------------------------------------------------

@tool
async def wx_get_radar_data(
    lat: float,
    lon: float,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get radar precipitation accumulation data for a location in Canada.

    Use for: checking rainfall totals, precipitation accumulation from weather
    radar, how much rain or snow has fallen in the past 24 hours, RDPA analysis
    data, precipitation estimates near a given location.
    Keywords: radar, precipitation, accumulation, rainfall, snowfall, RDPA,
    24 hour, rain total, weather radar, precipitation analysis, mm, forecast.

    Args:
        lat: Latitude of the query location.
        lon: Longitude of the query location.
        lang: Response language — "en" for English, "fr" for French.
    """
    try:
        items, cached = await fetch_radar_data(lat=lat, lon=lon)
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet radar data API error: {exc}",
            lang=lang,
        )

    return make_response(
        items,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Lightning information (WX-20)
# ---------------------------------------------------------------------------

@tool
async def wx_get_lightning(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get lightning strike information for Canada.

    Use for: finding lightning strike data, thunderstorm activity, real-time
    lightning observations. Note: lightning data is NOT available via the MSC
    OGC API — this tool returns a structured error with the correct data source.
    Keywords: lightning, thunder, strike, bolt, thunderstorm, electrical storm,
    real-time lightning, lightning map, storm activity, lightning detection.

    Args:
        lang: Response language — "en" for English, "fr" for French.

    Note:
        Lightning strike data is not available through the MSC GeoMet OGC API
        Features endpoint. Use the MSC DataMart LDFA XML feed instead at
        https://dd.weather.gc.ca/
    """
    # Lightning strike data has no OGC collection — return structured error
    return make_error(
        "NOT_FOUND",
        "Lightning strike data is not available via the MSC OGC API. "
        "Use the MSC DataMart LDFA XML feed at https://dd.weather.gc.ca/ instead.",
        lang=lang,
        url="https://dd.weather.gc.ca/",
    )


# ---------------------------------------------------------------------------
# Tool 6: UV index (WX-20)
# ---------------------------------------------------------------------------

@tool
async def wx_get_uv_index(
    lat: float | None = None,
    lon: float | None = None,
    location: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get UV index forecast for a location in Canada.

    Use for: checking UV radiation levels, sun safety recommendations,
    UV exposure risk, sunscreen advice, outdoor activity planning based
    on UV index from Environment and Climate Change Canada city forecasts.
    Keywords: UV index, ultraviolet, sun safety, UV radiation, sunscreen,
    UV level, UV category, sun exposure, UV forecast, solar radiation, UV risk.

    Args:
        lat: Latitude of the query location.
        lon: Longitude of the query location.
        location: Optional location name for context.
        lang: Response language — "en" for English, "fr" for French.

    Note:
        UV index is extracted from citypageweather forecast data (forecastGroup).
        It is only available for daytime periods and may be absent in evening
        or nighttime forecasts.
    """
    try:
        uv_data, cached = await fetch_uv_index(lat=lat, lon=lon, location=location)
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet UV index API error: {exc}",
            lang=lang,
        )

    if uv_data is None:
        return make_error(
            "NOT_FOUND",
            "No UV index data found for the specified location. "
            "Try providing lat/lon coordinates near a Canadian city.",
            lang=lang,
        )

    return make_response(
        uv_data,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
