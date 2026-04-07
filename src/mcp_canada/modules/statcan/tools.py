"""Statistics Canada WDS @tool functions.

Provides 11 sc_ tools for searching the StatCan cube catalog, retrieving
time series metadata, fetching observations, and monitoring data changes.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
- 409 maintenance window returns UPSTREAM_UNAVAILABLE
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.statcan.client import (
    get_bulk_vector_data,
    get_changed_cubes,
    get_changed_series,
    get_code_sets,
    get_cube_metadata,
    get_data_by_ref_period,
    get_latest_n_by_coord,
    get_latest_n_by_vector,
    get_series_info_by_coord,
    get_series_info_by_vector,
    search_cubes,
)
from mcp_canada.modules.statcan.constants import BASE_URL, _API_NAME
from mcp_canada.shared.envelope import make_error, make_response

_API_URL = BASE_URL

_MAINTENANCE_MSG = (
    "StatCan WDS is in its maintenance window (00:00-08:30 EST). "
    "Try again after 08:30 EST."
)


# ---------------------------------------------------------------------------
# Tool 1: Search cubes
# ---------------------------------------------------------------------------


@tool
async def sc_search_cubes(
    query: str,
    limit: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Statistics Canada tables (cubes) by keyword using BM25 ranking.

    Use for: finding relevant Statistics Canada data tables when you know a
    topic but not the exact productId. Searches over 80,000 tables by title,
    subject, and survey code.
    Keywords: statcan, statistics canada, table, cube, search, find, catalog, browse, dataset, survey, subject, BM25, keyword, lookup
    """
    try:
        data, was_cached = await search_cubes(query, limit=limit)
        return make_response(
            [item.model_dump() for item in data],
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 2: Get cube metadata
# ---------------------------------------------------------------------------


@tool
async def sc_get_cube_metadata(
    product_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full metadata and dimension structure for a Statistics Canada table.

    Use for: retrieving table title, frequency, date range, and all dimension
    members (geography, product groups, etc.) for a known productId.
    Keywords: statcan, statistics canada, table, metadata, dimensions, product id, cube, structure, frequency, geography, members, schema
    """
    try:
        data, was_cached = await get_cube_metadata(product_id)
        return make_response(
            data.model_dump(),
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 3: Get code sets
# ---------------------------------------------------------------------------


@tool
async def sc_get_code_sets(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get all WDS code sets for decoding numeric codes in StatCan responses.

    Use for: decoding frequencyCode, scalarFactorCode, statusCode, symbolCode,
    and uomCode fields that appear in series info and observation responses.
    Keywords: statcan, statistics canada, code sets, frequency, scalar, status, symbol, uom, decode, legend, reference, lookup
    """
    try:
        data, was_cached = await get_code_sets()
        return make_response(
            data.model_dump(),
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 4: Series info by vector
# ---------------------------------------------------------------------------


@tool
async def sc_get_series_info_by_vector(
    vector_id: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get series metadata by vectorId (title, frequency, scalar factor, units).

    Use for: looking up series title, frequency, and scalar factor when you
    have a vectorId from a previous search or observation response.
    Keywords: statcan, statistics canada, series, vector, metadata, vectorId, frequency, scalar, units, title, time series, info
    """
    try:
        data, was_cached = await get_series_info_by_vector(vector_id)
        return make_response(
            data.model_dump(),
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 5: Series info by coordinate
# ---------------------------------------------------------------------------


@tool
async def sc_get_series_info_by_coord(
    product_id: int,
    coordinate: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get series metadata by productId + coordinate (dot-separated dimension members).

    Use for: looking up a series when you know the table (productId) and the
    dimension combination (coordinate) but not the vectorId. Coordinate is
    auto-padded to 10 parts.
    Keywords: statcan, statistics canada, series, coordinate, product id, table, dimension, members, metadata, frequency, scalar, time series
    """
    try:
        data, was_cached = await get_series_info_by_coord(product_id, coordinate)
        return make_response(
            data.model_dump(),
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 6: Latest N observations by vector
# ---------------------------------------------------------------------------


@tool
async def sc_get_data_by_vector(
    vector_id: int,
    n: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the latest N observations for a Statistics Canada series by vectorId.

    Use for: fetching recent data points for a known series (vectorId). Returns
    observations sorted newest-first with decoded frequency and scalar labels.
    Keywords: statcan, statistics canada, observations, data, vector, vectorId, latest, recent, time series, values, historical, n periods
    """
    try:
        data, was_cached = await get_latest_n_by_vector(vector_id, n)
        return make_response(
            [item.model_dump() for item in data],
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 7: Latest N observations by coordinate
# ---------------------------------------------------------------------------


@tool
async def sc_get_data_by_coord(
    product_id: int,
    coordinate: str,
    n: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the latest N observations for a Statistics Canada series by productId + coordinate.

    Use for: fetching recent data points when you know the table (productId)
    and dimension combination (coordinate) but not the vectorId. Coordinate
    is auto-padded to 10 parts.
    Keywords: statcan, statistics canada, observations, data, coordinate, product id, dimension, latest, recent, time series, n periods, values
    """
    try:
        data, was_cached = await get_latest_n_by_coord(product_id, coordinate, n)
        return make_response(
            [item.model_dump() for item in data],
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 8: Data by reference period range
# ---------------------------------------------------------------------------


@tool
async def sc_get_data_by_date_range(
    vector_id: int,
    start_date: str,
    end_date: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Statistics Canada observations within a reference period date range.

    Use for: fetching all data points between two reference period dates for a
    known series (vectorId). Use when you need a specific date window, not
    just the latest N periods.
    Keywords: statcan, statistics canada, observations, date range, reference period, vector, time series, historical, start date, end date, range, filter
    """
    try:
        data, was_cached = await get_data_by_ref_period(vector_id, start_date, end_date)
        return make_response(
            [item.model_dump() for item in data],
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except ValueError as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 9: Bulk vector data by release date range
# ---------------------------------------------------------------------------


@tool
async def sc_get_bulk_vector_data(
    vector_ids: list[int],
    start_release: str,
    end_release: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get observations for multiple Statistics Canada series within a release date range.

    Use for: efficiently fetching data for many series at once when you care
    about when the data was released (not the reference period). Partial
    failures are handled — check for missing vectorIds in the result.
    Keywords: statcan, statistics canada, bulk, multiple, vectors, release date, observations, batch, parallel, time series, data, efficient
    """
    try:
        # WDS requires datetime format (e.g. "2024-01-01T00:00"); auto-append if plain date
        sr = start_release if "T" in start_release else start_release + "T00:00"
        er = end_release if "T" in end_release else end_release + "T23:59"
        data, was_cached = await get_bulk_vector_data(vector_ids, sr, er)
        # Convert int keys to str for JSON serialization, serialize ObservationRow lists
        serialized = {
            str(vid): [row.model_dump() for row in rows]
            for vid, rows in data.items()
        }
        return make_response(
            serialized,
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 10: Changed series (today)
# ---------------------------------------------------------------------------


@tool
async def sc_get_changed_series(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the list of Statistics Canada series (vectors) that changed today.

    Use for: monitoring which series were updated in today's release cycle.
    Returns lightweight records with vectorId, productId, coordinate, and
    releaseTime. May return an empty list before the daily release at 08:30 EST.
    Keywords: statcan, statistics canada, changed, updated, series, vectors, today, monitoring, release, daily, changes, refresh
    """
    try:
        data, was_cached = await get_changed_series()
        return make_response(
            data,
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)


# ---------------------------------------------------------------------------
# Tool 11: Changed cubes (by date)
# ---------------------------------------------------------------------------


@tool
async def sc_get_changed_cubes(
    date: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the list of Statistics Canada tables (cubes) that changed on a specific date.

    Use for: finding which tables were updated on a given date (YYYY-MM-DD).
    Useful for cache invalidation or checking if a specific table has been
    refreshed. May return an empty list for dates with no releases.
    Keywords: statcan, statistics canada, changed, updated, cubes, tables, date, monitoring, release, history, changes, refresh
    """
    try:
        data, was_cached = await get_changed_cubes(date)
        return make_response(
            data,
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return make_error("UPSTREAM_UNAVAILABLE", _MAINTENANCE_MSG, lang=lang)
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", f"Unexpected error: {exc}", lang=lang)
