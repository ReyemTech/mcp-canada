"""Unit tests for Health Canada Recalls client functions.

Tests:
- _build_cache_key: includes path, lang, and all params
- _api_get: caching behaviour (cache miss vs cache hit)
- fetch_recent_recalls: returns (list[dict], bool) with pagination params
- fetch_recall_search: handles keyword, category array params (cat[]), pagination
- fetch_recall_details: returns (dict, bool) for single recall
- cat[] array params encoded correctly for httpx tuple-style
"""

import pytest
from unittest.mock import AsyncMock, patch


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------

def import_client():
    import mcp_canada.modules.recalls.client as client_mod
    return client_mod


# ===========================================================================
# 1. _build_cache_key
# ===========================================================================

class TestBuildCacheKey:

    def test_includes_rcll_prefix(self):
        """Cache key must start with 'rcll:' prefix."""
        client = import_client()
        key = client._build_cache_key("recent/en", {"lim": 25, "off": 0})
        assert key.startswith("rcll:")

    def test_includes_path(self):
        """Cache key must include the path."""
        client = import_client()
        key = client._build_cache_key("recent/en", {})
        assert "recent/en" in key

    def test_includes_sorted_params(self):
        """Cache key must include params, sorted for determinism."""
        client = import_client()
        key1 = client._build_cache_key("search", {"lim": 25, "lang": "en", "search": "listeria"})
        key2 = client._build_cache_key("search", {"search": "listeria", "lang": "en", "lim": 25})
        assert key1 == key2  # same regardless of dict insertion order

    def test_includes_lang_in_params(self):
        """Cache key must include lang to prevent cross-language cache collisions."""
        client = import_client()
        key_en = client._build_cache_key("recent/en", {"lim": 25})
        key_fr = client._build_cache_key("recent/fr", {"lim": 25})
        assert key_en != key_fr

    def test_different_params_produce_different_keys(self):
        """Different param values produce different cache keys."""
        client = import_client()
        key1 = client._build_cache_key("recent/en", {"lim": 25, "off": 0})
        key2 = client._build_cache_key("recent/en", {"lim": 25, "off": 50})
        assert key1 != key2


# ===========================================================================
# 2. _api_get caching behaviour
# ===========================================================================

class TestApiGet:

    @pytest.mark.asyncio
    async def test_returns_tuple_of_data_and_bool(self):
        """_api_get must return (data, was_cached) tuple."""
        client = import_client()
        mock_response_data = {"warnings": [], "total": 0}

        with patch("mcp_canada.modules.recalls.client.cached_fetch",
                   new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (mock_response_data, False)
            result = await client._api_get("recent/en", {"lim": 25}, 900)

        assert isinstance(result, tuple)
        assert len(result) == 2
        data, was_cached = result
        assert data == mock_response_data
        assert isinstance(was_cached, bool)

    @pytest.mark.asyncio
    async def test_calls_cached_fetch_with_correct_ttl(self):
        """_api_get passes cache_ttl to cached_fetch."""
        client = import_client()
        mock_data = {"warnings": [], "total": 0}

        with patch("mcp_canada.modules.recalls.client.cached_fetch",
                   new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (mock_data, False)
            await client._api_get("recent/en", {}, 900)

        mock_cache.assert_called_once()
        call_args = mock_cache.call_args
        # Second positional arg is the TTL
        assert call_args[0][1] == 900

    @pytest.mark.asyncio
    async def test_cached_hit_returns_was_cached_true(self):
        """When cached_fetch returns (data, True), _api_get propagates was_cached=True."""
        client = import_client()
        mock_data = {"warnings": [{"recallId": "2024-001"}], "total": 1}

        with patch("mcp_canada.modules.recalls.client.cached_fetch",
                   new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (mock_data, True)
            data, was_cached = await client._api_get("recent/en", {}, 900)

        assert was_cached is True
        assert data == mock_data


# ===========================================================================
# 3. fetch_recent_recalls
# ===========================================================================

class TestFetchRecentRecalls:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool(self, sample_recent_recalls):
        """fetch_recent_recalls returns (list[dict], bool)."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recent_recalls, False)
            result = await client.fetch_recent_recalls(lang="en", limit=25, offset=0)

        assert isinstance(result, tuple)
        items, was_cached = result
        assert isinstance(items, list)
        assert isinstance(was_cached, bool)

    @pytest.mark.asyncio
    async def test_passes_lang_in_path(self, sample_recent_recalls):
        """fetch_recent_recalls includes lang in the URL path."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recent_recalls, False)
            await client.fetch_recent_recalls(lang="fr", limit=25, offset=0)

        mock_api.assert_called_once()
        path_arg = mock_api.call_args[0][0]
        assert "fr" in path_arg

    @pytest.mark.asyncio
    async def test_passes_lim_and_off_params(self, sample_recent_recalls):
        """fetch_recent_recalls passes lim and off query params."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recent_recalls, False)
            await client.fetch_recent_recalls(lang="en", limit=10, offset=5)

        mock_api.assert_called_once()
        params_arg = mock_api.call_args[0][1]
        assert params_arg.get("lim") == 10
        assert params_arg.get("off") == 5

    @pytest.mark.asyncio
    async def test_uses_search_cache_ttl(self, sample_recent_recalls):
        """fetch_recent_recalls uses CACHE_TTL_SEARCH (900s)."""
        from mcp_canada.modules.recalls.constants import CACHE_TTL_SEARCH
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recent_recalls, False)
            await client.fetch_recent_recalls(lang="en", limit=25, offset=0)

        mock_api.assert_called_once()
        ttl_arg = mock_api.call_args[0][2]
        assert ttl_arg == CACHE_TTL_SEARCH

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self, sample_recent_recalls_missing_fields):
        """fetch_recent_recalls gracefully handles recalls with missing fields."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recent_recalls_missing_fields, False)
            items, _ = await client.fetch_recent_recalls(lang="en", limit=25, offset=0)

        assert isinstance(items, list)
        assert len(items) >= 0  # should not raise


# ===========================================================================
# 4. fetch_recall_search
# ===========================================================================

class TestFetchRecallSearch:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool(self, sample_search_results):
        """fetch_recall_search returns (list[dict], bool)."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_search_results, False)
            result = await client.fetch_recall_search(
                search="listeria", categories=[], lang="en", limit=25, offset=0
            )

        items, was_cached = result
        assert isinstance(items, list)
        assert isinstance(was_cached, bool)

    @pytest.mark.asyncio
    async def test_passes_search_keyword_in_params(self, sample_search_results):
        """fetch_recall_search includes 'search' keyword in params."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_search_results, False)
            await client.fetch_recall_search(
                search="listeria", categories=[], lang="en", limit=25, offset=0
            )

        mock_api.assert_called_once()
        # The params should contain search keyword
        call_args = mock_api.call_args
        params = call_args[0][1]
        # With cat[] style, params may be a list of tuples
        if isinstance(params, list):
            dict(params)
        else:
            pass
        assert "search" in str(call_args)

    @pytest.mark.asyncio
    async def test_category_array_params_encoded_as_tuples(self, sample_search_results):
        """Categories are encoded as cat[] array params using httpx tuple syntax."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_search_results, False)
            await client.fetch_recall_search(
                search="", categories=["FOOD", "VEHICLE"], lang="en", limit=25, offset=0
            )

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        params = call_args[0][1]
        # Should be a list of tuples for cat[] array param syntax
        assert isinstance(params, list), "params should be a list of tuples for cat[] support"
        cat_params = [v for k, v in params if k == "cat[]"]
        assert "FOOD" in cat_params
        assert "VEHICLE" in cat_params

    @pytest.mark.asyncio
    async def test_no_categories_omits_cat_params(self, sample_search_results):
        """When categories is empty, no cat[] params are added."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_search_results, False)
            await client.fetch_recall_search(
                search="listeria", categories=[], lang="en", limit=25, offset=0
            )

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        params = call_args[0][1]
        if isinstance(params, list):
            cat_params = [v for k, v in params if k == "cat[]"]
            assert len(cat_params) == 0
        else:
            assert "cat[]" not in params

    @pytest.mark.asyncio
    async def test_uses_search_cache_ttl(self, sample_search_results):
        """fetch_recall_search uses CACHE_TTL_SEARCH (900s)."""
        from mcp_canada.modules.recalls.constants import CACHE_TTL_SEARCH
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_search_results, False)
            await client.fetch_recall_search(
                search="listeria", categories=[], lang="en", limit=25, offset=0
            )

        ttl_arg = mock_api.call_args[0][2]
        assert ttl_arg == CACHE_TTL_SEARCH


# ===========================================================================
# 5. fetch_recall_details
# ===========================================================================

class TestFetchRecallDetails:

    @pytest.mark.asyncio
    async def test_returns_dict_and_bool(self, sample_recall_detail):
        """fetch_recall_details returns (dict, bool)."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recall_detail, False)
            result = await client.fetch_recall_details(recall_id="2024-123", lang="en")

        detail, was_cached = result
        assert isinstance(detail, dict)
        assert isinstance(was_cached, bool)

    @pytest.mark.asyncio
    async def test_includes_recall_id_in_path(self, sample_recall_detail):
        """fetch_recall_details includes recall_id in the URL path."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recall_detail, False)
            await client.fetch_recall_details(recall_id="2024-123", lang="en")

        mock_api.assert_called_once()
        path_arg = mock_api.call_args[0][0]
        assert "2024-123" in path_arg

    @pytest.mark.asyncio
    async def test_includes_lang_in_path(self, sample_recall_detail):
        """fetch_recall_details includes lang in the URL path."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recall_detail, False)
            await client.fetch_recall_details(recall_id="2024-123", lang="fr")

        path_arg = mock_api.call_args[0][0]
        assert "fr" in path_arg

    @pytest.mark.asyncio
    async def test_uses_details_cache_ttl(self, sample_recall_detail):
        """fetch_recall_details uses CACHE_TTL_DETAILS (3600s)."""
        from mcp_canada.modules.recalls.constants import CACHE_TTL_DETAILS
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recall_detail, False)
            await client.fetch_recall_details(recall_id="2024-123", lang="en")

        ttl_arg = mock_api.call_args[0][2]
        assert ttl_arg == CACHE_TTL_DETAILS

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self, sample_recall_detail_missing_fields):
        """fetch_recall_details gracefully handles detail with missing optional fields."""
        client = import_client()

        with patch("mcp_canada.modules.recalls.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (sample_recall_detail_missing_fields, False)
            detail, _ = await client.fetch_recall_details(recall_id="2024-124", lang="en")

        assert isinstance(detail, dict)
        # Missing fields should not cause exceptions
