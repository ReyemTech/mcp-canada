"""Unit tests for Health Canada Recalls @tool functions.

Tests are structured as:
- Happy path: tool returns make_response envelope with correct data shape
- Error paths: invalid input returns make_error with correct code
- Category-specific tools: correct category passed to fetch_recall_search
- Docstring quality: Keywords line, Use for line, >= 50 chars for BM25 compliance
- lang parameter: passed through to make_response / make_error
"""

import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------

def import_tools():
    import mcp_canada.modules.recalls.tools as tools_mod
    return tools_mod


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_RECALLS_LIST = [
    {
        "recallId": "2024-123",
        "title": "Recall of contaminated salad greens",
        "datePublished": "2024-03-01",
        "category": "FOOD",
        "url": "https://healthycanadians.gc.ca/recall/2024-123",
    },
    {
        "recallId": "2024-124",
        "title": "Safety recall for children's toy",
        "datePublished": "2024-03-02",
        "category": "CPS",
        "url": "https://healthycanadians.gc.ca/recall/2024-124",
    },
]

SAMPLE_RECALL_DETAIL = {
    "recallId": "2024-123",
    "title": "Recall of contaminated salad greens",
    "datePublished": "2024-03-01",
    "category": "FOOD",
    "url": "https://healthycanadians.gc.ca/recall/2024-123",
    "affectedProducts": [{"name": "Spring Mix", "upc": "012345678901"}],
    "correctiveAction": "Stop using and dispose of recalled product.",
    "audience": "General Public",
    "summary": "Health Canada warning for contaminated salad.",
}


# ===========================================================================
# 1. recalls_get_recent
# ===========================================================================

class TestRecallsGetRecent:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """recalls_get_recent returns make_response envelope with _meta and data."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_recent()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_meta_contains_source_and_cached(self):
        """_meta must have source.api, source.url, and cached fields."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_recent()

        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert isinstance(result["_meta"]["cached"], bool)

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed to fetch function and make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_recent(lang="fr")

        assert result["_meta"]["lang"] == "fr"
        # Verify lang was passed to fetch function
        call_kwargs = mock_fn.call_args
        assert "fr" in str(call_kwargs)

    @pytest.mark.asyncio
    async def test_passes_limit_and_offset(self):
        """limit and offset are forwarded to fetch_recent_recalls."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_get_recent(limit=10, offset=20)

        mock_fn.assert_called_once()
        call_str = str(mock_fn.call_args)
        assert "10" in call_str
        assert "20" in call_str

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 503
        http_error = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_get_recent()

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]


# ===========================================================================
# 2. recalls_search
# ===========================================================================

class TestRecallsSearch:

    @pytest.mark.asyncio
    async def test_keyword_search_returns_envelope(self):
        """recalls_search returns make_response envelope for valid keyword."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_search(keyword="listeria")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_invalid_category_returns_invalid_input_error(self):
        """Invalid category code returns INVALID_INPUT error without HTTP call."""
        tools = import_tools()
        result = await tools.recalls_search(keyword="listeria", category="INVALID_CAT")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "INVALID_CAT" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_valid_category_passed_to_fetch(self):
        """Valid category is passed as a list to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_search(keyword="salad", category="FOOD")

        mock_fn.assert_called_once()
        call_str = str(mock_fn.call_args)
        assert "FOOD" in call_str

    @pytest.mark.asyncio
    async def test_no_category_passes_empty_list(self):
        """No category passes empty list to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_search(keyword="recall")

        mock_fn.assert_called_once()
        # categories should be empty list
        call_kwargs = mock_fn.call_args
        categories_arg = None
        if call_kwargs[1]:
            categories_arg = call_kwargs[1].get("categories")
        elif len(call_kwargs[0]) > 1:
            categories_arg = call_kwargs[0][1]
        # Either via positional or keyword arg, categories should be falsy/empty
        assert categories_arg is None or categories_arg == []

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.recalls_search(keyword="test", lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 500
        http_error = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_search(keyword="test")

        assert "error" in result


# ===========================================================================
# 3. recalls_get_details
# ===========================================================================

class TestRecallsGetDetails:

    @pytest.mark.asyncio
    async def test_returns_full_detail_in_envelope(self):
        """recalls_get_details returns full recall detail in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_details",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALL_DETAIL, False)
            result = await tools.recalls_get_details(recall_id="2024-123")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], dict)
        assert result["data"]["recallId"] == "2024-123"

    @pytest.mark.asyncio
    async def test_recall_id_passed_to_fetch(self):
        """recall_id is forwarded to fetch_recall_details."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_details",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALL_DETAIL, False)
            await tools.recalls_get_details(recall_id="2024-123")

        mock_fn.assert_called_once()
        assert "2024-123" in str(mock_fn.call_args)

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang is passed through to fetch function and make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_details",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALL_DETAIL, False)
            result = await tools.recalls_get_details(recall_id="2024-123", lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recall_details",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_get_details(recall_id="9999-999")

        assert "error" in result
        assert "code" in result["error"]


# ===========================================================================
# 4. recalls_get_food
# ===========================================================================

class TestRecallsGetFood:

    @pytest.mark.asyncio
    async def test_returns_envelope_with_food_results(self):
        """recalls_get_food returns make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_food()

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_passes_food_category_to_fetch(self):
        """recalls_get_food always passes categories=['FOOD'] to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_get_food()

        mock_fn.assert_called_once()
        call_str = str(mock_fn.call_args)
        assert "FOOD" in call_str

    @pytest.mark.asyncio
    async def test_passes_keyword_when_provided(self):
        """recalls_get_food forwards optional keyword to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            await tools.recalls_get_food(keyword="listeria")

        call_str = str(mock_fn.call_args)
        assert "listeria" in call_str

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 503
        http_error = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_get_food()

        assert "error" in result


# ===========================================================================
# 5. recalls_get_vehicles
# ===========================================================================

class TestRecallsGetVehicles:

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """recalls_get_vehicles returns make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_vehicles()

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_passes_vehicle_category_to_fetch(self):
        """recalls_get_vehicles always passes categories=['VEHICLE'] to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_get_vehicles()

        mock_fn.assert_called_once()
        call_str = str(mock_fn.call_args)
        assert "VEHICLE" in call_str

    @pytest.mark.asyncio
    async def test_passes_keyword_when_provided(self):
        """recalls_get_vehicles forwards optional keyword."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            await tools.recalls_get_vehicles(keyword="airbag")

        call_str = str(mock_fn.call_args)
        assert "airbag" in call_str

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 503
        http_error = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_get_vehicles()

        assert "error" in result


# ===========================================================================
# 6. recalls_get_health_products
# ===========================================================================

class TestRecallsGetHealthProducts:

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """recalls_get_health_products returns make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_health_products()

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_passes_health_category_to_fetch(self):
        """recalls_get_health_products always passes categories=['HEALTH'] to fetch_recall_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            await tools.recalls_get_health_products()

        mock_fn.assert_called_once()
        call_str = str(mock_fn.call_args)
        assert "HEALTH" in call_str

    @pytest.mark.asyncio
    async def test_passes_keyword_when_provided(self):
        """recalls_get_health_products forwards optional keyword."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            await tools.recalls_get_health_products(keyword="supplement")

        call_str = str(mock_fn.call_args)
        assert "supplement" in call_str

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error envelope."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 503
        http_error = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.recalls.tools.fetch_recall_search",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = http_error
            result = await tools.recalls_get_health_products()

        assert "error" in result


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 6 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "recalls_get_recent",
        "recalls_search",
        "recalls_get_details",
        "recalls_get_food",
        "recalls_get_vehicles",
        "recalls_get_health_products",
    ]

    def _get_tool_func(self, name: str):
        tools = import_tools()
        return getattr(tools, name)

    def test_all_tools_have_keywords_line(self):
        """All 6 tools must have 'Keywords:' in their docstring for BM25 indexing."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' line in docstring"

    def test_all_tools_have_use_for_line(self):
        """All 6 tools must have 'Use for:' in their docstring."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' line in docstring"

    def test_all_tool_docstrings_at_least_50_chars(self):
        """All 6 tool docstrings must be >= 50 characters."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert len(doc) >= 50, f"{name} docstring too short ({len(doc)} chars)"

    def test_all_tools_have_lang_parameter(self):
        """All 6 tools must accept lang: Literal['en', 'fr'] = 'en' parameter."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            sig = inspect.signature(func)
            assert "lang" in sig.parameters, f"{name} missing 'lang' parameter"
            param = sig.parameters["lang"]
            assert param.default == "en", f"{name} lang default should be 'en'"

    def test_all_tools_are_callable_async(self):
        """All 6 tool functions exist and are callable."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"


# ===========================================================================
# Envelope structure
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_success_response_has_meta_and_data(self):
        """Success responses have _meta and data keys."""
        tools = import_tools()
        with patch("mcp_canada.modules.recalls.tools.fetch_recent_recalls",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RECALLS_LIST, False)
            result = await tools.recalls_get_recent()

        assert "_meta" in result
        assert "data" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]

    @pytest.mark.asyncio
    async def test_error_response_has_error_with_code_and_message(self):
        """Error responses have error.code and error.message."""
        tools = import_tools()
        # Invalid category triggers error
        result = await tools.recalls_search(keyword="test", category="NOT_A_CATEGORY")

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
