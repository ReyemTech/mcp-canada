"""Unit tests for weather/collections @tool functions."""

import pytest
from unittest.mock import AsyncMock, patch


SAMPLE_COLLECTIONS = [
    {"id": "climate-stations", "title": "Climate Stations", "description": "Historical climate stations"},
    {"id": "weather-alerts", "title": "Weather Alerts", "description": "Active weather alerts"},
    {"id": "aqhi-observations-realtime", "title": "AQHI Observations", "description": "Air quality readings"},
]

SAMPLE_ITEMS = [
    {
        "id": "station-1",
        "lat": 45.4,
        "lon": -75.7,
        "properties": {"CLIMATE_IDENTIFIER": "6105976", "STATION_NAME": "OTTAWA CDA"},
    }
]


class TestWxListCollections:
    """Tests for wx_list_collections tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_data(self):
        """wx_list_collections returns make_response envelope on success."""
        from mcp_canada.modules.weather.collections.tools import wx_list_collections

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collections",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_COLLECTIONS, False)
            result = await wx_list_collections()

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "msc-geomet"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 3

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_list_collections passes lang parameter to _meta envelope."""
        from mcp_canada.modules.weather.collections.tools import wx_list_collections

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collections",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_COLLECTIONS, False)
            result = await wx_list_collections(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_error_on_upstream_exception(self):
        """wx_list_collections returns UPSTREAM_ERROR when fetch raises."""
        from mcp_canada.modules.weather.collections.tools import wx_list_collections

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collections",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Network timeout")
            result = await wx_list_collections()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_returns_error_when_empty(self):
        """wx_list_collections returns NOT_FOUND when no collections available."""
        from mcp_canada.modules.weather.collections.tools import wx_list_collections

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collections",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_list_collections()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_cached_flag_passed_to_meta(self):
        """wx_list_collections reflects cached flag in _meta."""
        from mcp_canada.modules.weather.collections.tools import wx_list_collections

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collections",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_COLLECTIONS, True)
            result = await wx_list_collections()

        assert result["_meta"]["cached"] is True


class TestWxGetCollectionItems:
    """Tests for wx_get_collection_items tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_collection_items returns make_response envelope on success."""
        from mcp_canada.modules.weather.collections.tools import wx_get_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collection_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_ITEMS, 1, False)
            result = await wx_get_collection_items(collection_id="climate-stations")

        assert "_meta" in result
        assert "data" in result
        # data is a dict with items, total_matched, collection_id
        assert isinstance(result["data"]["items"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_empty(self):
        """wx_get_collection_items returns NOT_FOUND when no items found."""
        from mcp_canada.modules.weather.collections.tools import wx_get_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collection_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], 0, False)
            result = await wx_get_collection_items(collection_id="unknown-collection")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """wx_get_collection_items returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.collections.tools import wx_get_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collection_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Connection error")
            result = await wx_get_collection_items(collection_id="climate-stations")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_collection_items passes lang to _meta envelope."""
        from mcp_canada.modules.weather.collections.tools import wx_get_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.tools.fetch_collection_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_ITEMS, 1, False)
            result = await wx_get_collection_items(collection_id="climate-stations", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestDocstringQuality:
    """Verify BM25 docstring quality for all collections tools."""

    def _get_tool_functions(self):
        import mcp_canada.modules.weather.collections.tools as tools_mod
        import inspect
        return [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]

    def test_all_tools_have_use_for_line(self):
        """All wx_ tools must have 'Use for:' in their docstring."""
        fns = self._get_tool_functions()
        assert len(fns) >= 2, "Expected at least 2 wx_ tool functions"
        for fn in fns:
            doc = fn.__doc__ or ""
            assert "Use for:" in doc, f"{fn.__name__} missing 'Use for:' in docstring"

    def test_all_tools_have_keywords_line(self):
        """All wx_ tools must have 'Keywords:' in their docstring for BM25."""
        fns = self._get_tool_functions()
        for fn in fns:
            doc = fn.__doc__ or ""
            assert "Keywords:" in doc, f"{fn.__name__} missing 'Keywords:' in docstring"

    def test_all_tools_have_lang_parameter(self):
        """All wx_ tools must accept a lang parameter."""
        import inspect
        import mcp_canada.modules.weather.collections.tools as tools_mod
        fns = [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, f"{fn.__name__} missing lang parameter"
