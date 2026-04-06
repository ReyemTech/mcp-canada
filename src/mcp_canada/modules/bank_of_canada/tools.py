"""Bank of Canada @tool functions for the Valet API.

Provides 8 intent-based and raw-access MCP tools for querying Bank of Canada
economic data: exchange rates, interest rates, commodity prices, inflation
indicators, series search, metadata, raw observations, and group listings.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.bank_of_canada.client import (
    fetch_all_groups,
    fetch_all_series,
    fetch_group_observations,
    fetch_observations,
    fetch_series_metadata,
    search_series,
    suggest_series,
)
from mcp_canada.modules.bank_of_canada.constants import (
    BASE_URL,
    BCPI_GROUP,
    BCPI_SERIES,
    CPI_GROUP,
    CPI_SERIES,
    FX_GROUP,
    INTEREST_RATE_SERIES,
)
from mcp_canada.shared.envelope import make_error, make_response

# API name and base URL for _meta envelope
_API_NAME = "bank-of-canada-valet"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _get_all_series_names() -> list[str]:
    """Return all Valet series names (cached 24h via fetch_all_series)."""
    all_series, _ = await fetch_all_series()
    return list(all_series.keys())


# ---------------------------------------------------------------------------
# Tool 1: Exchange rates
# ---------------------------------------------------------------------------

@tool
async def boc_get_exchange_rates(
    currency: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get daily CAD exchange rates for one or all foreign currencies.

    Use for: getting current or historical exchange rates between CAD and foreign
    currencies such as USD, EUR, GBP, JPY, and many others from the Bank of Canada.
    Keywords: exchange, currency, forex, cad, usd, eur, gbp, jpy, rate, conversion,
    fx, dollar, pound, euro, yen, foreign, daily.
    """
    try:
        if currency is not None:
            series_name = f"FX{currency.upper()}CAD"
            rows, cached = await fetch_observations(
                series_name,
                start_date=start_date,
                end_date=end_date,
                recent=recent,
            )
        else:
            rows, cached = await fetch_group_observations(
                FX_GROUP,
                start_date=start_date,
                end_date=end_date,
                recent=recent,
            )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            bad_name = f"FX{currency.upper()}CAD" if currency else "FX_GROUP"
            all_names = await _get_all_series_names()
            suggestions = suggest_series(bad_name, all_names)
            return make_error(
                "INVALID_SERIES",
                f"Series '{bad_name}' not found in Valet API.",
                lang=lang,
                suggestions=suggestions,
            )
        raise

    return make_response(
        [row.model_dump() for row in rows],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Interest rates
# ---------------------------------------------------------------------------

@tool
async def boc_get_interest_rates(
    rate_type: str = "all",
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Bank of Canada interest rates including policy rate, CORRA, and bond yields.

    Use for: fetching current or historical interest rates such as the overnight
    policy rate, CORRA, and 2/5/10-year government bond yields.
    Keywords: interest, rate, policy, prime, overnight, corra, bond, yield,
    benchmark, target, monetary, central bank.
    """
    valid_types = list(INTEREST_RATE_SERIES.keys()) + ["all"]
    if rate_type not in valid_types:
        return make_error(
            "INVALID_INPUT",
            f"Invalid rate_type '{rate_type}'. Valid values: {valid_types}",
            lang=lang,
        )

    if rate_type == "all":
        series_names = ",".join(INTEREST_RATE_SERIES.values())
    else:
        series_names = INTEREST_RATE_SERIES[rate_type]

    rows, cached = await fetch_observations(
        series_names,
        start_date=start_date,
        end_date=end_date,
        recent=recent,
    )

    return make_response(
        [row.model_dump() for row in rows],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Commodity prices (BCPI)
# ---------------------------------------------------------------------------

@tool
async def boc_get_commodity_prices(
    commodity_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Bank of Canada Commodity Price Index (BCPI) data by commodity category.

    Use for: fetching commodity price indexes for energy, metals, agriculture,
    forestry, fisheries, or the full BCPI basket from the Bank of Canada.
    Keywords: commodity, price, bcpi, energy, metals, agriculture, forestry,
    fisheries, fish, index, raw materials, resource.
    """
    if commodity_type is not None:
        valid_types = list(BCPI_SERIES.keys())
        if commodity_type not in valid_types:
            return make_error(
                "INVALID_INPUT",
                f"Invalid commodity_type '{commodity_type}'. Valid values: {valid_types}",
                lang=lang,
            )
        series_name = BCPI_SERIES[commodity_type]
        rows, cached = await fetch_observations(
            series_name,
            start_date=start_date,
            end_date=end_date,
            recent=recent,
        )
    else:
        rows, cached = await fetch_group_observations(
            BCPI_GROUP,
            start_date=start_date,
            end_date=end_date,
            recent=recent,
        )

    return make_response(
        [row.model_dump() for row in rows],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Inflation data (CPI)
# ---------------------------------------------------------------------------

@tool
async def boc_get_inflation_data(
    indicator: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Consumer Price Index (CPI) inflation data from the Bank of Canada.

    Use for: fetching current or historical inflation indicators including total
    CPI, CPI-trim, CPI-median, and CPI-common from the Bank of Canada.
    Keywords: inflation, cpi, consumer, price, index, trim, median, common,
    cost of living, purchasing power, core inflation.
    """
    if indicator is not None:
        valid_types = list(CPI_SERIES.keys())
        if indicator not in valid_types:
            return make_error(
                "INVALID_INPUT",
                f"Invalid indicator '{indicator}'. Valid values: {valid_types}",
                lang=lang,
            )
        series_name = CPI_SERIES[indicator]
        rows, cached = await fetch_observations(
            series_name,
            start_date=start_date,
            end_date=end_date,
            recent=recent,
        )
    else:
        rows, cached = await fetch_group_observations(
            CPI_GROUP,
            start_date=start_date,
            end_date=end_date,
            recent=recent,
        )

    return make_response(
        [row.model_dump() for row in rows],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Search series
# ---------------------------------------------------------------------------

@tool
async def boc_search_series(
    keyword: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search available Bank of Canada Valet API data series by keyword.

    Use for: finding the names and descriptions of available data series when
    you don't know the exact series code. Searches name, label, and description.
    Keywords: search, series, find, lookup, data, valet, available, discover,
    browse, catalog.
    """
    if len(keyword) < 2:
        return make_error(
            "INVALID_INPUT",
            "Keyword must be at least 2 characters long.",
            lang=lang,
        )

    results = await search_series(keyword)

    return make_response(
        [series.model_dump() for series in results],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=False,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Series metadata
# ---------------------------------------------------------------------------

@tool
async def boc_get_series_metadata(
    series_name: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get metadata (label, description, link) for a specific Valet API series.

    Use for: retrieving the label and description of a known Bank of Canada
    series code such as FXUSDCAD or V39079 to understand what it represents.
    Keywords: metadata, series, detail, label, description, info, FXUSDCAD,
    series code, documentation.
    """
    try:
        info, cached = await fetch_series_metadata(series_name)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            all_names = await _get_all_series_names()
            suggestions = suggest_series(series_name, all_names)
            return make_error(
                "INVALID_SERIES",
                f"Series '{series_name}' not found in Valet API.",
                lang=lang,
                suggestions=suggestions,
            )
        raise

    return make_response(
        info.model_dump(),
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Raw observations
# ---------------------------------------------------------------------------

@tool
async def boc_get_observations(
    series_names: str,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get raw time-series observations for any Bank of Canada Valet API series.

    Use for: directly fetching observations when you know the exact series
    name(s). Accepts comma-separated series for multi-series queries.
    Keywords: observations, data, raw, series, values, timeseries, historical,
    FXUSDCAD, valet, time series.
    """
    try:
        rows, cached = await fetch_observations(
            series_names,
            start_date=start_date,
            end_date=end_date,
            recent=recent,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            # Use first series name for suggestion matching
            first_name = series_names.split(",")[0].strip()
            all_names = await _get_all_series_names()
            suggestions = suggest_series(first_name, all_names)
            return make_error(
                "INVALID_SERIES",
                f"Series '{series_names}' not found in Valet API.",
                lang=lang,
                suggestions=suggestions,
            )
        raise

    return make_response(
        [row.model_dump() for row in rows],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: List groups
# ---------------------------------------------------------------------------

@tool
async def boc_list_groups(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all available data group collections in the Bank of Canada Valet API.

    Use for: discovering what groups of economic data series are available,
    such as FX_RATES_DAILY, BCPI_MONTHLY, or CPI_MONTHLY.
    Keywords: groups, list, categories, available, collections, datasets,
    valet, browse, catalog, series groups.
    """
    groups, cached = await fetch_all_groups()

    return make_response(
        [group.model_dump() for group in groups],
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
