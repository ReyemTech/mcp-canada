"""Snow conditions @tool functions for MSC GeoMet OGC API.

Provides 2 tools for Canadian snow conditions:
- wx_get_snow_depth — snow depth in cm from nearest SWOB real-time station
- wx_get_snow_water_equivalent — estimated SWE with configurable density factor

Each tool uses standalone @tool decorator, bilingual lang parameter,
and make_response/make_error envelopes.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.modules.weather.snow.client import (
    fetch_snow_depth,
    fetch_snow_water_equivalent,
)
from mcp_canada.shared.envelope import make_error, make_response

_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 7: Snow depth from SWOB observations
# ---------------------------------------------------------------------------

@tool
async def wx_get_snow_depth(
    station_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get snow depth from the nearest SWOB real-time weather observation station.

    Use for: checking current snow depth at a location in Canada, snow cover
    measurement, how much snow is on the ground, snowpack depth, snow conditions
    at an airport or weather station from SWOB real-time observations.
    Keywords: snow depth, snowpack, snow cover, snowfall, winter, cm, snow on ground,
    SWOB, surface observation, weather station, real-time, snow measurement, winter storm.

    Args:
        station_id: MSC station ID for direct lookup (e.g. "6106000").
        lat: Latitude for nearest-station search.
        lon: Longitude for nearest-station search.
        lang: Response language — "en" for English, "fr" for French.

    Note:
        Data is from SWOB (Surface Weather Observation Bulletin) real-time collection.
        Not all stations have snow depth sensors. In summer, readings may be 0 or absent.
        Primary sensor snw_dpth is used; backup sensors snw_dpth_1/2 are averaged as fallback.
    """
    try:
        data, cached = await fetch_snow_depth(
            station_id=station_id, lat=lat, lon=lon
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet SWOB snow depth API error: {exc}",
            lang=lang,
        )

    if data is None:
        return make_error(
            "NOT_FOUND",
            "No SWOB observation data found for the specified location. "
            "Try providing lat/lon coordinates near a Canadian weather station, "
            "or provide a valid station_id.",
            lang=lang,
        )

    return make_response(
        data,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Snow water equivalent estimate
# ---------------------------------------------------------------------------

@tool
async def wx_get_snow_water_equivalent(
    station_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    density_factor: float = 0.3,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get estimated snow water equivalent (SWE) from snow depth observations.

    Use for: estimating how much liquid water is stored in the snowpack, SWE
    estimation for hydrology, water resources planning, snowmelt runoff prediction,
    or comparing snow water content at different locations.
    Keywords: snow water equivalent, SWE, snowpack, water content, snow density,
    hydrology, water storage, snowmelt, runoff, snowpack water, precipitation equivalent.

    Args:
        station_id: MSC station ID for direct lookup.
        lat: Latitude for nearest-station search.
        lon: Longitude for nearest-station search.
        density_factor: Snow density as a fraction of water density (default 0.3).
                        Adjust for different snow types: 0.05-0.1 for fresh powder,
                        0.3 for settled snow, 0.5 for old compacted snow.
        lang: Response language — "en" for English, "fr" for French.

    Note:
        Snow water equivalent is estimated from snow depth using a density factor
        (default 0.3). This is not a direct measurement. Adjust density_factor for
        different snow types: 0.05-0.1 for fresh powder, 0.3 for settled snow,
        0.5 for old compacted snow. For accurate SWE, use a snow pillow network.
    """
    try:
        data, cached = await fetch_snow_water_equivalent(
            station_id=station_id,
            lat=lat,
            lon=lon,
            density_factor=density_factor,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet SWOB snow water equivalent API error: {exc}",
            lang=lang,
        )

    if data is None:
        return make_error(
            "NOT_FOUND",
            "No snow depth data found for the specified location. "
            "Cannot estimate SWE without snow depth measurement.",
            lang=lang,
        )

    return make_response(
        data,
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
