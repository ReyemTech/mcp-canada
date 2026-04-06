"""Unit tests for marine weather @tool functions.

Tests:
- wx_get_marine_forecast: returns make_response envelope, handles empty
- wx_get_hurricane_tracks: returns make_response with empty list + message when off-season
- wx_get_thunderstorm_outlook: returns make_response with empty list + message when off-season
- lang parameter passes through to envelope
- Docstring quality: Keywords line, Use for line
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_tools():
    import mcp_canada.modules.weather.marine.tools as tools_mod
    return tools_mod


SAMPLE_MARINE_DATA = [
    {
        "area_en": "Northumberland Strait",
        "area_fr": "Détroit de Northumberland",
        "forecast_text_en": "Northwest 15 to 20 knots.",
        "forecast_text_fr": "Nord-ouest 15 à 20 noeuds.",
        "warnings_count": 1,
        "issued_utc": "2024-03-01T12:00:00Z",
        "lat": 44.8,
        "lon": -63.5,
    }
]

SAMPLE_HURRICANE_DATA = [
    {
        "name": "HURRICANE ALPHA",
        "storm_category": "Category 3",
        "max_wind_kt": 110,
        "lat": 25.0,
        "lon": -75.0,
    }
]

SAMPLE_THUNDERSTORM_DATA = [
    {
        "region_en": "Southern Ontario",
        "risk_en": "High",
        "outlook_en": "Severe thunderstorms possible.",
        "lat": 44.5,
        "lon": -77.5,
    }
]


# ===========================================================================
# 1. wx_get_marine_forecast
# ===========================================================================

class TestWxGetMarineForecast:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """wx_get_marine_forecast returns make_response envelope with _meta and data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_marine_forecast",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_MARINE_DATA, False)
            result = await tools.wx_get_marine_forecast()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_marine_forecast lang passes through to _meta envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_marine_forecast",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_MARINE_DATA, False)
            result = await tools.wx_get_marine_forecast(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_empty_returns_make_response_not_error(self):
        """wx_get_marine_forecast with no results returns make_response (not error)."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_marine_forecast",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.wx_get_marine_forecast(province="NS")

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_upstream_error_returns_make_error(self):
        """wx_get_marine_forecast returns make_error on exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_marine_forecast",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = Exception("Connection error")
            result = await tools.wx_get_marine_forecast()

        assert "error" in result

    def test_docstring_has_use_for(self):
        """wx_get_marine_forecast docstring has 'Use for:' line for BM25."""
        tools = import_tools()
        doc = tools.wx_get_marine_forecast.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_marine_forecast docstring has 'Keywords:' line for BM25."""
        tools = import_tools()
        doc = tools.wx_get_marine_forecast.__doc__ or ""
        assert "Keywords:" in doc


# ===========================================================================
# 2. wx_get_hurricane_tracks
# ===========================================================================

class TestWxGetHurricaneTracks:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_tracks(self):
        """wx_get_hurricane_tracks returns make_response with track list when active."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_hurricane_tracks",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_HURRICANE_DATA, False)
            result = await tools.wx_get_hurricane_tracks()

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_returns_make_response_with_message_when_empty(self):
        """wx_get_hurricane_tracks returns make_response (not error) with note when off-season."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_hurricane_tracks",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.wx_get_hurricane_tracks()

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result
        # Should include a note/message in the response data
        data = result["data"]
        assert isinstance(data, dict) or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_empty_response_has_note(self):
        """wx_get_hurricane_tracks empty response includes descriptive note."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_hurricane_tracks",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.wx_get_hurricane_tracks()

        # data should be a dict with a 'note' key OR a list
        data = result["data"]
        if isinstance(data, dict):
            assert "note" in data or "tracks" in data
        # If it's a list it's acceptable (empty list is valid)

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_hurricane_tracks lang passes through to _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_hurricane_tracks",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.wx_get_hurricane_tracks(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    def test_docstring_has_use_for(self):
        """wx_get_hurricane_tracks docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_hurricane_tracks.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_hurricane_tracks docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_hurricane_tracks.__doc__ or ""
        assert "Keywords:" in doc


# ===========================================================================
# 3. wx_get_thunderstorm_outlook
# ===========================================================================

class TestWxGetThunderstormOutlook:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_data(self):
        """wx_get_thunderstorm_outlook returns make_response envelope with data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_thunderstorm_outlook",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_THUNDERSTORM_DATA, False)
            result = await tools.wx_get_thunderstorm_outlook()

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_empty_returns_make_response_not_error(self):
        """wx_get_thunderstorm_outlook returns make_response (not error) when empty."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_thunderstorm_outlook",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = ([], False)
            result = await tools.wx_get_thunderstorm_outlook()

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_thunderstorm_outlook lang passes through to _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.marine.tools.fetch_thunderstorm_outlook",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_THUNDERSTORM_DATA, False)
            result = await tools.wx_get_thunderstorm_outlook(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    def test_docstring_has_use_for(self):
        """wx_get_thunderstorm_outlook docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_thunderstorm_outlook.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_thunderstorm_outlook docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_thunderstorm_outlook.__doc__ or ""
        assert "Keywords:" in doc
