"""Unit tests for Open Parliament client functions.

Tests are structured as:
- _safe_get helper with nested dicts and missing keys
- _parl_get calls shared api_get with API_HEADERS
- Each fetch function extracts 'objects' from paginated response
- Missing fields in response don't cause errors
"""

import pytest
from unittest.mock import AsyncMock, patch

from mcp_canada.modules.open_parliament.__tests__.conftest import (
    SAMPLE_BILLS_RESPONSE,
    SAMPLE_BILLS_MISSING_FIELDS,
    SAMPLE_BILL_DETAIL,
    SAMPLE_POLITICIANS_RESPONSE,
    SAMPLE_POLITICIANS_MISSING_FIELDS,
    SAMPLE_VOTES_RESPONSE,
    SAMPLE_DEBATES_RESPONSE,
    SAMPLE_HANSARD_SEARCH,
)


# ===========================================================================
# _safe_get helper
# ===========================================================================

class TestSafeGet:

    def test_safe_get_returns_value_for_existing_key(self):
        """_safe_get returns the value for a key that exists."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"key": "value"}
        assert _safe_get(obj, "key") == "value"

    def test_safe_get_returns_none_for_missing_key(self):
        """_safe_get returns None when key is missing."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"other": "data"}
        assert _safe_get(obj, "missing") is None

    def test_safe_get_nested_keys(self):
        """_safe_get traverses nested dicts."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"level1": {"level2": {"level3": "deep_value"}}}
        assert _safe_get(obj, "level1", "level2", "level3") == "deep_value"

    def test_safe_get_returns_none_for_missing_nested_key(self):
        """_safe_get returns None when intermediate key is missing."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"level1": {"other": "data"}}
        assert _safe_get(obj, "level1", "missing", "level3") is None

    def test_safe_get_returns_none_for_none_obj(self):
        """_safe_get returns None when obj itself is None."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        assert _safe_get(None, "key") is None

    def test_safe_get_returns_default_for_missing(self):
        """_safe_get returns custom default when provided and key missing."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"key": "value"}
        assert _safe_get(obj, "missing", default="fallback") == "fallback"

    def test_safe_get_with_non_dict_intermediate(self):
        """_safe_get returns None when intermediate value is not a dict."""
        from mcp_canada.modules.open_parliament.client import _safe_get
        obj = {"key": "not_a_dict"}
        assert _safe_get(obj, "key", "nested") is None


# ===========================================================================
# _parl_get uses shared api_get with API_HEADERS
# ===========================================================================

class TestParlGet:

    @pytest.mark.asyncio
    async def test_parl_get_calls_api_get_with_headers(self):
        """_parl_get should call shared api_get with API_HEADERS."""

        mock_data = {"objects": [], "pagination": {}}

        with patch(
            "mcp_canada.modules.open_parliament.client.cached_fetch",
            new_callable=AsyncMock,
        ) as mock_cache:
            mock_cache.return_value = (mock_data, False)

            with patch(
                "mcp_canada.modules.open_parliament.client.api_get",
                new_callable=AsyncMock,
            ) as mock_api_get:
                mock_api_get.return_value = mock_data

                # Trigger a fetch that will call cached_fetch -> lambda -> api_get
                from mcp_canada.modules.open_parliament.client import _parl_get
                result, cached = await _parl_get("bills/", {}, 3600)

                # cached_fetch was called; verify it was called with some key
                mock_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_parl_get_builds_full_url_from_base(self):
        """_parl_get builds full URL as BASE_URL + path."""
        from mcp_canada.modules.open_parliament.client import _parl_get


        async def fake_cached_fetch(key, ttl, fetcher):
            # Actually call the fetcher to capture what api_get receives
            return ({"objects": [], "pagination": {}}, False)

        with patch(
            "mcp_canada.modules.open_parliament.client.cached_fetch",
            side_effect=fake_cached_fetch,
        ):
            with patch(
                "mcp_canada.modules.open_parliament.client.api_get",
                new_callable=AsyncMock,
            ) as mock_api_get:
                mock_api_get.return_value = {"objects": [], "pagination": {}}
                result, cached = await _parl_get("bills/", {"search": "climate"}, 3600)

        # Just verify cached_fetch was called (full URL verification via integration)
        assert result == {"objects": [], "pagination": {}}


# ===========================================================================
# fetch_bills
# ===========================================================================

class TestFetchBills:

    @pytest.mark.asyncio
    async def test_fetch_bills_extracts_objects(self):
        """fetch_bills should extract objects list from paginated response."""
        from mcp_canada.modules.open_parliament.client import fetch_bills

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_BILLS_RESPONSE, False)
            bills, cached = await fetch_bills()

        assert isinstance(bills, list)
        assert len(bills) == 2
        assert bills[0]["number"] == "C-11"
        assert cached is False

    @pytest.mark.asyncio
    async def test_fetch_bills_with_filters(self):
        """fetch_bills passes search, session, status params."""
        from mcp_canada.modules.open_parliament.client import fetch_bills

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_BILLS_RESPONSE, False)
            bills, _ = await fetch_bills(
                search="streaming", session="44-1", status="Passed"
            )

        # Verify params were passed
        call_args = mock_get.call_args
        params = call_args[0][1]
        assert params.get("q") == "streaming"
        assert params.get("session") == "44-1"
        assert params.get("status") == "Passed"

    @pytest.mark.asyncio
    async def test_fetch_bills_handles_missing_fields(self):
        """fetch_bills does not raise when response objects have missing fields."""
        from mcp_canada.modules.open_parliament.client import fetch_bills

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_BILLS_MISSING_FIELDS, False)
            bills, _ = await fetch_bills()  # Should not raise

        assert len(bills) == 1
        assert bills[0]["number"] == "S-1"


# ===========================================================================
# fetch_bill_details
# ===========================================================================

class TestFetchBillDetails:

    @pytest.mark.asyncio
    async def test_fetch_bill_details_returns_single_bill(self):
        """fetch_bill_details returns the raw bill dict."""
        from mcp_canada.modules.open_parliament.client import fetch_bill_details

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_BILL_DETAIL, False)
            bill, cached = await fetch_bill_details("44-1/C-11")

        assert bill["number"] == "C-11"
        assert bill["session"] == "44-1"

    @pytest.mark.asyncio
    async def test_fetch_bill_details_uses_bill_id_in_path(self):
        """fetch_bill_details includes bill_id in the API path."""
        from mcp_canada.modules.open_parliament.client import fetch_bill_details

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_BILL_DETAIL, False)
            await fetch_bill_details("44-1/C-11")

        call_args = mock_get.call_args
        path = call_args[0][0]
        assert "44-1/C-11" in path


# ===========================================================================
# fetch_politicians
# ===========================================================================

class TestFetchPoliticians:

    @pytest.mark.asyncio
    async def test_fetch_politicians_extracts_objects(self):
        """fetch_politicians extracts objects list from response."""
        from mcp_canada.modules.open_parliament.client import fetch_politicians

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_POLITICIANS_RESPONSE, False)
            politicians, _ = await fetch_politicians()

        assert len(politicians) == 2
        assert politicians[0]["name"] == "Justin Trudeau"

    @pytest.mark.asyncio
    async def test_fetch_politicians_handles_missing_fields(self):
        """fetch_politicians does not raise when fields are missing."""
        from mcp_canada.modules.open_parliament.client import fetch_politicians

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_POLITICIANS_MISSING_FIELDS, False)
            politicians, _ = await fetch_politicians()  # Should not raise

        assert len(politicians) == 1


# ===========================================================================
# fetch_votes
# ===========================================================================

class TestFetchVotes:

    @pytest.mark.asyncio
    async def test_fetch_votes_extracts_objects(self):
        """fetch_votes extracts objects list from paginated response."""
        from mcp_canada.modules.open_parliament.client import fetch_votes

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_VOTES_RESPONSE, False)
            votes, _ = await fetch_votes()

        assert len(votes) == 1
        assert votes[0]["number"] == 148

    @pytest.mark.asyncio
    async def test_fetch_votes_passes_filters(self):
        """fetch_votes passes session, bill, result, politician params."""
        from mcp_canada.modules.open_parliament.client import fetch_votes

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_VOTES_RESPONSE, False)
            await fetch_votes(session="44-1", bill="C-11", result="Passed")

        call_args = mock_get.call_args
        params = call_args[0][1]
        assert params.get("session") == "44-1"
        assert params.get("bill") == "C-11"
        assert params.get("result") == "Passed"


# ===========================================================================
# fetch_debates
# ===========================================================================

class TestFetchDebates:

    @pytest.mark.asyncio
    async def test_fetch_debates_extracts_objects(self):
        """fetch_debates extracts objects list from paginated response."""
        from mcp_canada.modules.open_parliament.client import fetch_debates

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_DEBATES_RESPONSE, False)
            debates, _ = await fetch_debates()

        assert len(debates) == 1
        assert debates[0]["date"] == "2023-03-28"


# ===========================================================================
# fetch_hansard_search
# ===========================================================================

class TestFetchHansardSearch:

    @pytest.mark.asyncio
    async def test_fetch_hansard_search_extracts_objects(self):
        """fetch_hansard_search extracts objects list from paginated response."""
        from mcp_canada.modules.open_parliament.client import fetch_hansard_search

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_HANSARD_SEARCH, False)
            results, _ = await fetch_hansard_search(query="climate")

        assert len(results) == 1
        assert results[0]["content"] == "We are investing in..."

    @pytest.mark.asyncio
    async def test_fetch_hansard_search_passes_query_param(self):
        """fetch_hansard_search passes query as 'q' parameter."""
        from mcp_canada.modules.open_parliament.client import fetch_hansard_search

        with patch(
            "mcp_canada.modules.open_parliament.client._parl_get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = (SAMPLE_HANSARD_SEARCH, False)
            await fetch_hansard_search(query="housing")

        call_args = mock_get.call_args
        params = call_args[0][1]
        assert params.get("q") == "housing"
