"""Valet API client for the Bank of Canada module.

Provides async functions for fetching, flattening, caching, and rate-limiting
all Valet API endpoints. All public functions return (data, was_cached) tuples.

Sort convention: observation rows are returned newest-first (index 0 = most recent).
"""

import difflib
from typing import Any

import httpx

from mcp_canada.modules.bank_of_canada.constants import (
    BASE_URL,
    CACHE_TTL_META,
    CACHE_TTL_OBS,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.modules.bank_of_canada.schemas import GroupInfo, ObservationRow, SeriesInfo
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter


def _build_cache_key(path: str, params: dict[str, Any]) -> str:
    """Build a deterministic cache key from path and sorted params."""
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"boc:{path}?{sorted_params}"


async def _valet_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Valet API with caching and rate limiting.

    Args:
        path: API path relative to BASE_URL (e.g. "observations/FXUSDCAD/json").
        params: Query parameters dict.
        cache_ttl: Cache TTL in seconds.

    Returns:
        (response_json, was_cached)
    """
    url = BASE_URL + path
    cache_key = _build_cache_key(path, params)
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            return response.json()

    return await cached_fetch(cache_key, cache_ttl, fetcher)


def flatten_observations(raw_json: dict[str, Any]) -> list[ObservationRow]:
    """Flatten raw Valet API observations response into a list of ObservationRow.

    Extracts seriesDetail metadata and converts nested {"v": "1.39"} values
    to floats. Null values become None. Returns rows sorted newest-first.

    Args:
        raw_json: Raw JSON from a Valet observations endpoint.

    Returns:
        list[ObservationRow] sorted by date descending (newest first).
    """
    series_detail: dict[str, Any] = raw_json.get("seriesDetail", {})
    observations: list[dict[str, Any]] = raw_json.get("observations", [])

    rows: list[ObservationRow] = []
    for obs in observations:
        date = obs["d"]
        for series_name, series_meta in series_detail.items():
            raw_val = obs.get(series_name, {})
            v = raw_val.get("v") if isinstance(raw_val, dict) else None

            if v is None:
                value = None
            else:
                try:
                    value = float(v)
                except (TypeError, ValueError):
                    value = None

            rows.append(
                ObservationRow(
                    date=date,
                    series_name=series_name,
                    value=value,
                    label=series_meta.get("label", ""),
                    description=series_meta.get("description", ""),
                )
            )

    # Sort newest first
    rows.sort(key=lambda r: r.date, reverse=True)
    return rows


async def fetch_observations(
    series_names: str,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int | None = None,
) -> tuple[list[ObservationRow], bool]:
    """Fetch and flatten observations for one or more series.

    Args:
        series_names: Comma-separated series name(s) (e.g. "FXUSDCAD" or "FXUSDCAD,FXEURCAD").
        start_date: Optional start date filter (ISO 8601 date string, e.g. "2026-01-01").
        end_date: Optional end date filter (ISO 8601 date string).
        recent: Optional number of most recent observations to fetch.

    Returns:
        (list[ObservationRow], was_cached)
    """
    params: dict[str, Any] = {"order_dir": "desc"}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    # Valet API rejects recent + date range together
    if recent is not None and start_date is None and end_date is None:
        params["recent"] = recent

    raw, was_cached = await _valet_get(
        f"observations/{series_names}/json", params, CACHE_TTL_OBS
    )
    return flatten_observations(raw), was_cached


async def fetch_group_observations(
    group_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    recent: int = 10,
) -> tuple[list[ObservationRow], bool]:
    """Fetch and flatten observations for all series in a group.

    Args:
        group_name: Valet group name (e.g. "FX_RATES_DAILY").
        start_date: Optional start date filter (ISO 8601 date string).
        end_date: Optional end date filter (ISO 8601 date string).
        recent: Number of most recent observations to fetch (default 10).

    Returns:
        (list[ObservationRow], was_cached)
    """
    params: dict[str, Any] = {"order_dir": "desc"}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    # Valet API rejects recent + date range together
    if start_date is None and end_date is None:
        params["recent"] = recent

    raw, was_cached = await _valet_get(
        f"observations/group/{group_name}/json", params, CACHE_TTL_OBS
    )
    return flatten_observations(raw), was_cached


async def fetch_series_metadata(
    series_name: str,
) -> tuple[SeriesInfo, bool]:
    """Fetch metadata for a single series.

    NOTE: The /series/{name}/json endpoint returns 'seriesDetails' (plural S),
    unlike the observations endpoint which uses 'seriesDetail' (singular).

    Args:
        series_name: Valet series name (e.g. "FXUSDCAD").

    Returns:
        (SeriesInfo, was_cached)
    """
    raw, was_cached = await _valet_get(
        f"series/{series_name}/json", {}, CACHE_TTL_META
    )
    # Note: plural 'seriesDetails' (different from observations 'seriesDetail')
    details: dict[str, Any] = raw.get("seriesDetails", {})
    series_data = details.get(series_name, {})

    info = SeriesInfo(
        name=series_name,
        label=series_data.get("label", ""),
        description=series_data.get("description", ""),
        link=series_data.get("link"),
    )
    return info, was_cached


async def fetch_all_series() -> tuple[dict[str, SeriesInfo], bool]:
    """Fetch the full catalog of all available Valet series.

    Cached for 24 hours (CACHE_TTL_META).

    Returns:
        (dict[str, SeriesInfo], was_cached) — keyed by series name.
    """
    raw, was_cached = await _valet_get("lists/series/json", {}, CACHE_TTL_META)
    series_raw: dict[str, Any] = raw.get("series", {})

    result: dict[str, SeriesInfo] = {}
    for name, meta in series_raw.items():
        result[name] = SeriesInfo(
            name=name,
            label=meta.get("label", ""),
            description=meta.get("description", ""),
            link=meta.get("link"),
        )
    return result, was_cached


async def search_series(keyword: str) -> list[SeriesInfo]:
    """Search the series catalog by keyword (case-insensitive).

    Filters on series name, label, and description. Benefits from the 24h
    cache on fetch_all_series so repeated searches are cheap.

    Args:
        keyword: Search term (matched case-insensitively against name, label, description).

    Returns:
        list[SeriesInfo] of matching series.
    """
    all_series, _ = await fetch_all_series()
    kw = keyword.lower()
    return [
        info
        for info in all_series.values()
        if kw in info.name.lower()
        or kw in info.label.lower()
        or kw in info.description.lower()
    ]


async def fetch_all_groups() -> tuple[list[GroupInfo], bool]:
    """Fetch the full catalog of all available Valet series groups.

    Cached for 24 hours (CACHE_TTL_META).

    Returns:
        (list[GroupInfo], was_cached)
    """
    raw, was_cached = await _valet_get("lists/groups/json", {}, CACHE_TTL_META)
    groups_raw: dict[str, Any] = raw.get("groups", {})

    groups: list[GroupInfo] = [
        GroupInfo(
            name=name,
            label=meta.get("label", ""),
            description=meta.get("description", ""),
            link=meta.get("link"),
        )
        for name, meta in groups_raw.items()
    ]
    return groups, was_cached


def suggest_series(bad_name: str, all_series_names: list[str]) -> list[str]:
    """Return close matches for a misspelled or unknown series name.

    Uses difflib.get_close_matches with cutoff=0.6.

    Args:
        bad_name: The series name that wasn't found.
        all_series_names: Full list of valid series names to match against.

    Returns:
        list[str] of up to 5 close matches.
    """
    return difflib.get_close_matches(bad_name, all_series_names, n=5, cutoff=0.6)
