"""MSC GeoMet climate tool functions.

Provides 7 MCP tools for historical climate data, 1981-2010 normals,
CMIP5/CMIP6 projection metadata, SPEI drought index metadata,
period comparison, and AHCCD long-term trend data.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.weather.climate.client import (
    compare_climate_periods,
    fetch_climate_daily,
    fetch_climate_monthly,
    fetch_climate_normals,
    fetch_climate_projections,
    fetch_climate_trends,
    fetch_drought_index,
)
from mcp_canada.modules.weather.constants import API_NAME, BASE_URL
from mcp_canada.shared.envelope import UPSTREAM_ERROR, make_error, make_response


@tool
async def wx_get_climate_daily(
    station_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get historical daily climate observations for a weather station.

    Returns daily records including max/min/mean temperature, total precipitation,
    snowfall, snow on ground, and heating/cooling degree days.

    Use for: historical weather data, daily temperature records, precipitation history,
    past climate conditions for a specific station and date range.

    Keywords: daily climate, historical weather, temperature daily, precipitation,
    snowfall, max temperature, min temperature, degree days, station observations,
    past weather data, climate record, snow on ground

    Args:
        station_id: Climate station identifier (e.g. "6158731" for Ottawa CDA).
        start_date: Start of date range in ISO format (e.g. "2024-01-01").
        end_date: End of date range in ISO format (e.g. "2024-01-31").
        limit: Maximum records to return (default 100).
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_climate_daily(
            station_id, start_date=start_date, end_date=end_date, limit=limit
        )
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections/climate-daily/items",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_get_climate_monthly(
    station_id: str,
    year: int | None = None,
    limit: int = 12,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get monthly climate summary data for a weather station.

    Returns monthly aggregates including mean/max/min temperature, total
    precipitation, and total snowfall. Optionally filter by year.

    Use for: monthly climate summaries, seasonal weather patterns, annual
    climate overview, monthly precipitation totals, monthly temperature averages.

    Keywords: monthly climate, monthly weather, monthly temperature, monthly precipitation,
    seasonal climate, monthly summary, climate monthly, annual climate, monthly snowfall,
    weather summary, station monthly data

    Args:
        station_id: Climate station identifier.
        year: Optional year filter (e.g. 2024).
        limit: Maximum records to return (default 12).
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_climate_monthly(station_id, year=year, limit=limit)
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections/climate-monthly/items",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_get_climate_normals(
    station_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get 30-year climate normals for a weather station.

    Returns the 1981-2010 climate normals for the station — monthly averages
    of temperature, precipitation, and other variables computed over the
    1981-2010 reference period.

    Note: Returns 1981-2010 normals. The 1991-2020 period is not yet available
    via this API. Each record contains the climate variable, month, and the
    30-year average value.

    Use for: climate baseline, 30-year averages, normal temperatures, average
    precipitation, climate reference period, seasonal norms, baseline climate,
    historical averages for a station.

    Keywords: climate normals, 30-year average, baseline climate, 1981 2010,
    normal temperature, average precipitation, climate reference, seasonal norms,
    monthly normals, historical average, climate baseline, normal snowfall

    Args:
        station_id: Climate station identifier.
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_climate_normals(station_id)
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections/climate-normals/items",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_get_climate_projections(
    model: Literal["cmip5", "cmip6"] = "cmip5",
    scenario: str | None = None,
    variable: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get CMIP5 or CMIP6 climate projection collection metadata.

    Returns collection metadata only (title, description, temporal/spatial extent,
    and links). Grid-based projection data requires direct MSC API access —
    the /items endpoint returns HTTP 400 for these colon-ID collections.

    Note: Returns collection metadata only. Grid-based projection data requires
    direct MSC API access. The CMIP5 collection covers projected annual anomalies;
    CMIP6 covers projected annual absolute values.

    Use for: climate projections, future climate scenarios, CMIP5, CMIP6,
    projected temperature change, climate model output, future climate outlook.

    Keywords: climate projections, CMIP5, CMIP6, future climate, climate model,
    projected temperature, climate scenario, RCP, SSP, climate change projections,
    annual anomaly, climate forecast model, projected climate

    Args:
        model: Climate model version — "cmip5" (default) or "cmip6".
        scenario: Optional scenario label (informational only).
        variable: Optional variable name (informational only).
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_climate_projections(model=model)
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_get_drought_index(
    lat: float | None = None,
    lon: float | None = None,
    spei_period: int = 3,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get SPEI drought index collection metadata.

    Returns collection metadata for the Standardized Precipitation Evapotranspiration
    Index (SPEI) drought dataset. The /items endpoint returns HTTP 400 for this
    colon-ID collection — metadata only is returned.

    Note: Returns collection metadata only. SPEI values require direct MSC API access.
    SPEI measures drought severity: negative values indicate drought, positive
    values indicate wet conditions.

    Use for: drought index, SPEI, drought monitoring, drought conditions,
    precipitation deficit, drought severity, water deficit Canada.

    Keywords: drought index, SPEI, drought monitoring, drought conditions,
    standardized precipitation, water deficit, drought severity, aridity,
    drought Canada, precipitation evapotranspiration, SPEI-3, SPEI-12, dry conditions

    Args:
        lat: Optional latitude (informational context).
        lon: Optional longitude (informational context).
        spei_period: Accumulation period in months — 1, 3 (default), or 12.
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_drought_index(lat=lat, lon=lon, spei_period=spei_period)
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_compare_climate_periods(
    station_id: str,
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Compare daily climate averages between two time periods for a station.

    Fetches daily observations for both periods and computes mean temperature,
    total precipitation, and total snowfall averages. Returns deltas
    (period2 - period1) to show how climate has changed between the two periods.

    Use for: climate change comparison, temperature trend between periods,
    comparing two time periods, climate shift, warming trend, how has climate
    changed at a station, decade comparison, climate before and after.

    Keywords: climate comparison, period comparison, temperature change, climate trend,
    warming, precipitation change, climate shift, before after climate, decade comparison,
    climate difference, two periods, historical comparison, climate change analysis

    Args:
        station_id: Climate station identifier.
        period1_start: First period start date (ISO format, e.g. "1990-01-01").
        period1_end: First period end date (ISO format, e.g. "1990-12-31").
        period2_start: Second period start date (ISO format, e.g. "2020-01-01").
        period2_end: Second period end date (ISO format, e.g. "2020-12-31").
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await compare_climate_periods(
            station_id, period1_start, period1_end, period2_start, period2_end
        )
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections/climate-daily/items",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)


@tool
async def wx_get_climate_trends(
    station_id: str | None = None,
    measurement_type: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get long-term climate trends from the AHCCD dataset.

    Returns Adjusted and Homogenized Canadian Climate Data (AHCCD) trend records
    showing long-term climate trends at stations across Canada. Can filter by
    station or measurement type (temperature, precipitation, etc.).

    Use for: long-term climate trends, AHCCD data, climate change evidence,
    temperature trend, precipitation trend, homogenized climate data, climate signal.

    Keywords: climate trends, AHCCD, long-term trend, temperature trend,
    precipitation trend, homogenized data, adjusted climate, climate signal,
    warming trend, climate change Canada, trend analysis, historical trend,
    long-term climate change

    Args:
        station_id: Optional station identifier to filter trends.
        measurement_type: Optional measurement type (e.g. "temperature", "precipitation").
        lang: Response language — "en" (default) or "fr".
    """
    try:
        data, cached = await fetch_climate_trends(
            station_id=station_id, measurement_type=measurement_type
        )
        return make_response(
            data,
            api_name=API_NAME,
            api_url=f"{BASE_URL}/collections/ahccd-trends/items",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error(UPSTREAM_ERROR, str(exc), lang=lang)
