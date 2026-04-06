"""Unit tests for severe weather @tool functions.

Tests:
- wx_get_radar_data: returns make_response envelope with precipitation data
- wx_get_lightning: returns make_error with NOT_FOUND and DataMart URL
- wx_get_uv_index: returns make_response with UV index data
- lang parameter passes through
- Docstring quality: Keywords line, Use for line
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_tools():
    import mcp_canada.modules.weather.severe.tools as tools_mod
    return tools_mod


SAMPLE_RADAR_DATA = [
    {
        "precipitation_mm": 12.5,
        "datetime": "2024-03-01T12:00:00Z",
        "lat": 45.4,
        "lon": -75.7,
    }
]

SAMPLE_UV_DATA = {
    "location_en": "Ottawa",
    "location_fr": "Ottawa",
    "uv_index": 8,
    "uv_category": "Very High",
    "period": "Today",
    "lat": 45.4,
    "lon": -75.7,
}


# ===========================================================================
# 1. wx_get_radar_data
# ===========================================================================

class TestWxGetRadarData:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """wx_get_radar_data returns make_response envelope with _meta and data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_radar_data",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RADAR_DATA, False)
            result = await tools.wx_get_radar_data(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_radar_data lang passes through to _meta envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_radar_data",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_RADAR_DATA, False)
            result = await tools.wx_get_radar_data(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_make_error_on_exception(self):
        """wx_get_radar_data returns make_error on exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_radar_data",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = Exception("Network error")
            result = await tools.wx_get_radar_data(lat=45.4, lon=-75.7)

        assert "error" in result

    def test_docstring_has_use_for(self):
        """wx_get_radar_data docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_radar_data.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_radar_data docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_radar_data.__doc__ or ""
        assert "Keywords:" in doc


# ===========================================================================
# 2. wx_get_lightning
# ===========================================================================

class TestWxGetLightning:

    @pytest.mark.asyncio
    async def test_returns_make_error_not_found(self):
        """wx_get_lightning returns make_error with NOT_FOUND code."""
        tools = import_tools()
        result = await tools.wx_get_lightning()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_error_message_mentions_datamart(self):
        """wx_get_lightning error message mentions MSC DataMart."""
        tools = import_tools()
        result = await tools.wx_get_lightning()

        message = result["error"]["message"]
        assert "DataMart" in message or "dd.weather.gc.ca" in message

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_lightning lang passes through to error envelope."""
        tools = import_tools()
        result = await tools.wx_get_lightning(lang="fr")

        assert result["error"]["lang"] == "fr"

    def test_docstring_has_use_for(self):
        """wx_get_lightning docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_lightning.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_lightning docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_lightning.__doc__ or ""
        assert "Keywords:" in doc


# ===========================================================================
# 3. wx_get_uv_index
# ===========================================================================

class TestWxGetUvIndex:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_uv_data(self):
        """wx_get_uv_index returns make_response envelope with UV data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_uv_index",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_UV_DATA, False)
            result = await tools.wx_get_uv_index(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_returns_make_error_when_no_data(self):
        """wx_get_uv_index returns make_error NOT_FOUND when no UV data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_uv_index",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (None, False)
            result = await tools.wx_get_uv_index(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_uv_index lang passes through to _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.severe.tools.fetch_uv_index",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_UV_DATA, False)
            result = await tools.wx_get_uv_index(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"

    def test_docstring_has_use_for(self):
        """wx_get_uv_index docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_uv_index.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_uv_index docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_uv_index.__doc__ or ""
        assert "Keywords:" in doc
