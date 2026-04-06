"""Marine weather @tool functions for MSC GeoMet OGC API.

Provides 3 tools for marine safety and severe weather tracking:
- wx_get_marine_forecast — coastal/offshore marine weather forecasts
- wx_get_hurricane_tracks — active hurricane/tropical storm track data
- wx_get_thunderstorm_outlook — thunderstorm outlook regions and risk

Each tool follows the 5-file module pattern with standalone @tool decorator,
bilingual lang parameter, and make_response/make_error envelopes.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.modules.weather.marine.client import (
    fetch_hurricane_tracks,
    fetch_marine_forecast,
    fetch_thunderstorm_outlook,
)
from mcp_canada.shared.envelope import make_error, make_response

_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Marine weather forecasts (WX-18)
# ---------------------------------------------------------------------------

@tool
async def wx_get_marine_forecast(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get marine weather forecasts for Canadian coastal and offshore waters.

    Use for: getting marine weather forecasts for coastal waters, offshore zones,
    small craft advisories, wave heights, and wind conditions for sailors,
    boaters, and commercial fishing operations in Canadian waters.
    Keywords: marine, weather, coastal, offshore, forecast, boat, sailor, fishing,
    waves, wind, knots, small craft, advisory, warning, waters, nautical.

    Args:
        province: Two-letter province code to filter by region (e.g. "NS", "BC", "NL").
        lat: Latitude for location-based search.
        lon: Longitude for location-based search.
        lang: Response language — "en" for English, "fr" for French.
    """
    try:
        items, cached = await fetch_marine_forecast(
            province=province, lat=lat, lon=lon
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet marine weather API error: {exc}",
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
# Tool 2: Hurricane and tropical storm tracks (WX-19)
# ---------------------------------------------------------------------------

@tool
async def wx_get_hurricane_tracks(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get active hurricane and tropical storm track data for Canada and adjacent waters.

    Use for: tracking active hurricanes, tropical storms, tropical depressions,
    and post-tropical systems affecting or approaching Canadian coastal regions.
    Returns empty list with note when no active storms (normal off-season behaviour).
    Keywords: hurricane, tropical storm, cyclone, track, forecast, path, storm,
    category, wind, pressure, advisory, atlantic, pacific, season, tropical.

    Args:
        lang: Response language — "en" for English, "fr" for French.
    """
    try:
        tracks, cached = await fetch_hurricane_tracks()
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet hurricane tracks API error: {exc}",
            lang=lang,
        )

    if not tracks:
        return make_response(
            {
                "tracks": [],
                "note": "No active tropical storms or hurricanes currently. "
                        "This is normal outside of hurricane season (June–November).",
            },
            api_name=API_NAME,
            api_url=_API_URL,
            cached=cached,
            lang=lang,
        )

    return make_response(
        {"tracks": tracks, "count": len(tracks)},
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Thunderstorm outlook (WX-20)
# ---------------------------------------------------------------------------

@tool
async def wx_get_thunderstorm_outlook(
    province: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get thunderstorm outlook regions and risk levels for Canada.

    Use for: getting thunderstorm forecasts, severe storm outlook, convective
    risk levels, and storm prediction for Canadian regions. Returns empty list
    with note when no active outlook (off-season or no significant convective activity).
    Keywords: thunderstorm, storm, outlook, convective, severe, lightning risk,
    tornado, hail, wind, risk level, forecast, convection, warning, storm prediction.

    Args:
        province: Two-letter province code to filter results (e.g. "ON", "AB").
        lang: Response language — "en" for English, "fr" for French.
    """
    try:
        outlooks, cached = await fetch_thunderstorm_outlook(province=province)
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"MSC GeoMet thunderstorm outlook API error: {exc}",
            lang=lang,
        )

    if not outlooks:
        return make_response(
            {
                "outlooks": [],
                "note": "No active thunderstorm outlooks currently. "
                        "Outlooks are issued when significant convective activity is expected.",
            },
            api_name=API_NAME,
            api_url=_API_URL,
            cached=cached,
            lang=lang,
        )

    return make_response(
        {"outlooks": outlooks, "count": len(outlooks)},
        api_name=API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
