"""Unit tests for snow @tool functions.

Tests:
- wx_get_snow_depth: returns make_response with snow depth, handles no data
- wx_get_snow_water_equivalent: returns make_response with SWE estimate, documents approach
- lang parameter passes through
- Docstring quality: Keywords line, Use for line, density factor documentation
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_tools():
    import mcp_canada.modules.weather.snow.tools as tools_mod
    return tools_mod


SAMPLE_SNOW_DEPTH_DATA = {
    "station_name": "OTTAWA INTL A",
    "snow_depth_cm": 15.0,
    "observed_at": "2024-03-01T12:00:00Z",
    "air_temp_c": -5.0,
    "lat": 45.4,
    "lon": -75.7,
}

SAMPLE_SWE_DATA = {
    "station_name": "OTTAWA INTL A",
    "snow_depth_cm": 15.0,
    "swe_mm": 4.5,
    "density_factor": 0.3,
    "observed_at": "2024-03-01T12:00:00Z",
    "note": "Estimated from snow depth using density factor. Not a direct measurement.",
}


# ===========================================================================
# 1. wx_get_snow_depth
# ===========================================================================

class TestWxGetSnowDepth:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """wx_get_snow_depth returns make_response envelope with _meta and data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_depth",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_SNOW_DEPTH_DATA, False)
            result = await tools.wx_get_snow_depth(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_returns_make_error_when_no_data(self):
        """wx_get_snow_depth returns make_error NOT_FOUND when no data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_depth",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (None, False)
            result = await tools.wx_get_snow_depth(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_snow_depth lang passes through to _meta envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_depth",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_SNOW_DEPTH_DATA, False)
            result = await tools.wx_get_snow_depth(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_make_error_on_exception(self):
        """wx_get_snow_depth returns make_error on exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_depth",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = Exception("Connection error")
            result = await tools.wx_get_snow_depth(lat=45.4, lon=-75.7)

        assert "error" in result

    def test_docstring_has_use_for(self):
        """wx_get_snow_depth docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_snow_depth.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_snow_depth docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_snow_depth.__doc__ or ""
        assert "Keywords:" in doc

    def test_docstring_mentions_swob(self):
        """wx_get_snow_depth docstring mentions SWOB as data source."""
        tools = import_tools()
        doc = tools.wx_get_snow_depth.__doc__ or ""
        assert "swob" in doc.lower() or "SWOB" in doc


# ===========================================================================
# 2. wx_get_snow_water_equivalent
# ===========================================================================

class TestWxGetSnowWaterEquivalent:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """wx_get_snow_water_equivalent returns make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_water_equivalent",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_SWE_DATA, False)
            result = await tools.wx_get_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert "data" in result
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_returns_make_error_when_no_data(self):
        """wx_get_snow_water_equivalent returns make_error NOT_FOUND when no data."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_water_equivalent",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (None, False)
            result = await tools.wx_get_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """wx_get_snow_water_equivalent lang passes through to _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.weather.snow.tools.fetch_snow_water_equivalent",
                   new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = (SAMPLE_SWE_DATA, False)
            result = await tools.wx_get_snow_water_equivalent(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"

    def test_docstring_has_use_for(self):
        """wx_get_snow_water_equivalent docstring has 'Use for:' line."""
        tools = import_tools()
        doc = tools.wx_get_snow_water_equivalent.__doc__ or ""
        assert "Use for:" in doc

    def test_docstring_has_keywords(self):
        """wx_get_snow_water_equivalent docstring has 'Keywords:' line."""
        tools = import_tools()
        doc = tools.wx_get_snow_water_equivalent.__doc__ or ""
        assert "Keywords:" in doc

    def test_docstring_documents_estimation_approach(self):
        """wx_get_snow_water_equivalent docstring explains density factor estimation."""
        tools = import_tools()
        doc = tools.wx_get_snow_water_equivalent.__doc__ or ""
        assert "density" in doc.lower()
        assert "estimate" in doc.lower() or "estimated" in doc.lower()

    def test_docstring_mentions_not_direct_measurement(self):
        """wx_get_snow_water_equivalent docstring notes it's not a direct measurement."""
        tools = import_tools()
        doc = tools.wx_get_snow_water_equivalent.__doc__ or ""
        assert "not a direct measurement" in doc.lower() or "estimate" in doc.lower()
