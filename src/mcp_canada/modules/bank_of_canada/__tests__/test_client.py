"""Unit tests for Bank of Canada Valet API client functions."""

import pytest
from unittest.mock import AsyncMock, patch

from mcp_canada.modules.bank_of_canada.__tests__.conftest import (
    SAMPLE_FX_OBSERVATIONS,
    SAMPLE_GROUP_OBSERVATIONS,
    SAMPLE_SERIES_LIST,
    SAMPLE_GROUPS_LIST,
    SAMPLE_SERIES_METADATA,
    make_mock_response,
)
from mcp_canada.modules.bank_of_canada.schemas import ObservationRow, SeriesInfo, GroupInfo
from mcp_canada.modules.bank_of_canada.constants import CACHE_TTL_OBS, CACHE_TTL_META, RATE_GROUP


# ─── flatten_observations tests ──────────────────────────────────────────────


def test_flatten_observations_basic():
    """flatten_observations converts nested v-dicts to flat ObservationRow list."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_FX_OBSERVATIONS)
    assert isinstance(rows, list)
    assert len(rows) == 3
    assert all(isinstance(r, ObservationRow) for r in rows)


def test_flatten_observations_value_conversion():
    """flatten_observations converts {'v': '1.39'} to float 1.39."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_FX_OBSERVATIONS)
    # Find the non-null row
    non_null = [r for r in rows if r.value is not None][0]
    assert isinstance(non_null.value, float)
    assert non_null.value == pytest.approx(1.39, rel=1e-3)


def test_flatten_observations_null_value():
    """flatten_observations converts {'v': null} to value=None."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_FX_OBSERVATIONS)
    null_rows = [r for r in rows if r.value is None]
    assert len(null_rows) == 1
    assert null_rows[0].date == "2026-03-31"


def test_flatten_observations_newest_first():
    """flatten_observations returns rows sorted newest first."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_FX_OBSERVATIONS)
    dates = [r.date for r in rows]
    assert dates == sorted(dates, reverse=True)


def test_flatten_observations_includes_label_and_description():
    """flatten_observations populates label and description from seriesDetail."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_FX_OBSERVATIONS)
    row = rows[0]
    assert row.label == "USD/CAD"
    assert "dollar" in row.description.lower()


def test_flatten_observations_multi_series_group():
    """flatten_observations handles group responses with multiple series."""
    from mcp_canada.modules.bank_of_canada.client import flatten_observations

    rows = flatten_observations(SAMPLE_GROUP_OBSERVATIONS)
    # 2 observations * 2 series = 4 rows
    assert len(rows) == 4
    series_names = {r.series_name for r in rows}
    assert "FXUSDCAD" in series_names
    assert "FXEURCAD" in series_names


# ─── fetch_observations tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_observations_returns_rows_and_cached_flag(reset_cache):
    """fetch_observations returns (list[ObservationRow], was_cached)."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        rows, was_cached = await client.fetch_observations("FXUSDCAD")

    assert isinstance(rows, list)
    assert len(rows) > 0
    assert all(isinstance(r, ObservationRow) for r in rows)
    assert isinstance(was_cached, bool)


@pytest.mark.asyncio
async def test_fetch_observations_uses_obs_ttl(reset_cache):
    """fetch_observations caches with CACHE_TTL_OBS."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    cached_fetch_calls = []

    import mcp_canada.modules.bank_of_canada.client as client_mod
    from mcp_canada.shared import cache as cache_mod

    original_cached_fetch = cache_mod.cached_fetch

    async def spy_cached_fetch(key, ttl, fetcher):
        cached_fetch_calls.append({"key": key, "ttl": ttl})
        return await original_cached_fetch(key, ttl, fetcher)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Patch cached_fetch where client module binds it
        with patch.object(client_mod, "cached_fetch", spy_cached_fetch):
            await client.fetch_observations("FXUSDCAD")

    assert len(cached_fetch_calls) == 1
    assert cached_fetch_calls[0]["ttl"] == CACHE_TTL_OBS


@pytest.mark.asyncio
async def test_fetch_observations_second_call_cached(reset_cache):
    """Second call within TTL returns was_cached=True."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        _, first_cached = await client.fetch_observations("FXUSDCAD_cached_test")
        _, second_cached = await client.fetch_observations("FXUSDCAD_cached_test")

    assert first_cached is False
    assert second_cached is True


@pytest.mark.asyncio
async def test_fetch_observations_passes_start_end_date(reset_cache):
    """fetch_observations passes start_date and end_date as query params."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Unique key to avoid cache hits from other tests
        await client.fetch_observations(
            "FXUSDCAD_dates_test", start_date="2026-01-01", end_date="2026-04-01"
        )

    assert "start_date" in captured_params
    assert captured_params["start_date"] == "2026-01-01"
    assert "end_date" in captured_params
    assert captured_params["end_date"] == "2026-04-01"


@pytest.mark.asyncio
async def test_fetch_observations_passes_recent(reset_cache):
    """fetch_observations passes recent param to Valet."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Unique key to avoid cache hits from other tests
        await client.fetch_observations("FXUSDCAD_recent_test", recent=5)

    assert "recent" in captured_params
    assert captured_params["recent"] == 5


@pytest.mark.asyncio
async def test_fetch_observations_default_order_desc(reset_cache):
    """fetch_observations uses order_dir='desc' by default (newest first)."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Unique key to avoid cache hits from other tests
        await client.fetch_observations("FXUSDCAD_order_test")

    assert captured_params.get("order_dir") == "desc"


# ─── fetch_observations: recent vs date range mutual exclusion ────────────────


@pytest.mark.asyncio
async def test_fetch_observations_no_recent_when_dates_provided(reset_cache):
    """recent param must NOT be sent when start_date/end_date are set (Valet returns 400)."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await client.fetch_observations(
            "FXUSDCAD_norecent_test",
            start_date="2025-01-01",
            end_date="2026-01-01",
            recent=10,
        )

    assert "start_date" in captured_params
    assert "end_date" in captured_params
    assert "recent" not in captured_params, (
        "recent must not be sent with date range — Valet API returns 400"
    )


@pytest.mark.asyncio
async def test_fetch_observations_recent_sent_when_no_dates(reset_cache):
    """recent param IS sent when no date range is provided."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await client.fetch_observations("FXUSDCAD_withrecent_test", recent=5)

    assert "recent" in captured_params
    assert captured_params["recent"] == 5
    assert "start_date" not in captured_params
    assert "end_date" not in captured_params


# ─── fetch_group_observations: recent vs date range mutual exclusion ─────────


@pytest.mark.asyncio
async def test_fetch_group_observations_no_recent_when_dates_provided(reset_cache):
    """recent param must NOT be sent when start_date/end_date are set (Valet returns 400)."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_GROUP_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await client.fetch_group_observations(
            "FX_RATES_DAILY_norecent_test",
            start_date="2025-01-01",
            end_date="2026-01-01",
            recent=10,
        )

    assert "start_date" in captured_params
    assert "end_date" in captured_params
    assert "recent" not in captured_params, (
        "recent must not be sent with date range — Valet API returns 400"
    )


@pytest.mark.asyncio
async def test_fetch_group_observations_recent_sent_when_no_dates(reset_cache):
    """recent param IS sent when no date range is provided."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_GROUP_OBSERVATIONS)
    captured_params = {}

    async def capture_get(url, params=None, **kwargs):
        captured_params.update(params or {})
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=capture_get)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await client.fetch_group_observations(
            "FX_RATES_DAILY_withrecent_test", recent=5
        )

    assert "recent" in captured_params
    assert captured_params["recent"] == 5
    assert "start_date" not in captured_params


# ─── fetch_group_observations tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_group_observations_returns_rows(reset_cache):
    """fetch_group_observations returns list of flattened rows from all series."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_GROUP_OBSERVATIONS)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        rows, was_cached = await client.fetch_group_observations("FX_RATES_DAILY")

    assert isinstance(rows, list)
    assert len(rows) > 0
    assert all(isinstance(r, ObservationRow) for r in rows)


# ─── fetch_series_metadata tests ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_series_metadata_returns_series_info(reset_cache):
    """fetch_series_metadata returns SeriesInfo with label and description."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_SERIES_METADATA)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        info, was_cached = await client.fetch_series_metadata("FXUSDCAD")

    assert isinstance(info, SeriesInfo)
    assert info.label == "USD/CAD"
    assert "dollar" in info.description.lower()


@pytest.mark.asyncio
async def test_fetch_series_metadata_uses_series_details_key(reset_cache):
    """fetch_series_metadata uses 'seriesDetails' key (plural S — metadata endpoint)."""
    from mcp_canada.modules.bank_of_canada import client

    # Response with seriesDetails (plural) — must be handled correctly
    metadata_with_plural_s = {
        "seriesDetails": {
            "FXUSDCAD": {
                "label": "USD/CAD",
                "description": "US dollar rate",
                "link": "/valet/series/FXUSDCAD/json",
            }
        }
    }
    mock_resp = make_mock_response(metadata_with_plural_s)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        info, _ = await client.fetch_series_metadata("FXUSDCAD")

    assert info.name == "FXUSDCAD"


@pytest.mark.asyncio
async def test_fetch_series_metadata_uses_meta_ttl(reset_cache):
    """fetch_series_metadata caches with CACHE_TTL_META (24h)."""
    from mcp_canada.modules.bank_of_canada import client
    import mcp_canada.modules.bank_of_canada.client as client_mod
    from mcp_canada.shared import cache as cache_mod

    mock_resp = make_mock_response(SAMPLE_SERIES_METADATA)
    cached_fetch_calls = []

    original_cached_fetch = cache_mod.cached_fetch

    async def spy_cached_fetch(key, ttl, fetcher):
        cached_fetch_calls.append({"key": key, "ttl": ttl})
        return await original_cached_fetch(key, ttl, fetcher)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch.object(client_mod, "cached_fetch", spy_cached_fetch):
            await client.fetch_series_metadata("FXUSDCAD")

    assert any(call["ttl"] == CACHE_TTL_META for call in cached_fetch_calls)


# ─── fetch_all_series tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_all_series_returns_dict(reset_cache):
    """fetch_all_series returns dict of {name: SeriesInfo}, cached for 24h."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_SERIES_LIST)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        series_dict, was_cached = await client.fetch_all_series()

    assert isinstance(series_dict, dict)
    assert "FXUSDCAD" in series_dict
    assert isinstance(series_dict["FXUSDCAD"], SeriesInfo)


# ─── search_series tests ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_series_filters_by_keyword(reset_cache):
    """search_series filters cached series list and returns matching SeriesInfo."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_SERIES_LIST)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results = await client.search_series("exchange")

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, SeriesInfo) for r in results)
    # V39079 (overnight rate) should not match "exchange"
    names = [r.name for r in results]
    assert "FXUSDCAD" in names or "FXEURCAD" in names


@pytest.mark.asyncio
async def test_search_series_case_insensitive(reset_cache):
    """search_series is case-insensitive."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_SERIES_LIST)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results_lower = await client.search_series("exchange")

    mock_resp2 = make_mock_response(SAMPLE_SERIES_LIST)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp2
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results_upper = await client.search_series("EXCHANGE")

    assert {r.name for r in results_lower} == {r.name for r in results_upper}


# ─── fetch_all_groups tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_all_groups_returns_list(reset_cache):
    """fetch_all_groups returns list[GroupInfo], cached for 24h."""
    from mcp_canada.modules.bank_of_canada import client

    mock_resp = make_mock_response(SAMPLE_GROUPS_LIST)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        groups, was_cached = await client.fetch_all_groups()

    assert isinstance(groups, list)
    assert len(groups) > 0
    assert all(isinstance(g, GroupInfo) for g in groups)


# ─── suggest_series tests ─────────────────────────────────────────────────────


def test_suggest_series_close_matches():
    """suggest_series returns close matches via difflib.get_close_matches."""
    from mcp_canada.modules.bank_of_canada.client import suggest_series

    all_names = ["FXUSDCAD", "FXEURCAD", "FXGBPCAD", "V39079"]
    suggestions = suggest_series("FXUSDCA", all_names)
    assert isinstance(suggestions, list)
    assert "FXUSDCAD" in suggestions


def test_suggest_series_no_match():
    """suggest_series returns empty list when nothing is close."""
    from mcp_canada.modules.bank_of_canada.client import suggest_series

    all_names = ["FXUSDCAD", "FXEURCAD"]
    suggestions = suggest_series("ZZZZZZZ", all_names)
    assert suggestions == []


# ─── Rate limiter integration ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_calls_get_limiter(reset_cache):
    """All fetch functions call get_limiter(RATE_GROUP) before HTTP requests."""
    from mcp_canada.modules.bank_of_canada import client
    import mcp_canada.modules.bank_of_canada.client as client_mod
    from mcp_canada.shared import rate_limiter as rl_mod

    mock_resp = make_mock_response(SAMPLE_FX_OBSERVATIONS)
    limiter_calls = []

    original_get_limiter = rl_mod.get_limiter

    def spy_get_limiter(source, rate=10.0, capacity=10):
        limiter_calls.append(source)
        return original_get_limiter(source, rate=rate, capacity=capacity)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Patch get_limiter where the client module binds it
        with patch.object(client_mod, "get_limiter", spy_get_limiter):
            await client.fetch_observations("FXUSDCAD_ratelimit_test")

    assert any(s == RATE_GROUP for s in limiter_calls)
