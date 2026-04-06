"""Unit tests for weather/summary @tool functions."""

import pytest
from unittest.mock import AsyncMock, patch


SAMPLE_SUMMARY = {
    "conditions": {"city": "Ottawa", "temperature_c": 15.0},
    "forecast": [{"period": "Today", "temperature_c": 18.0}],
    "alerts": [],
    "aqhi": [{"aqhi_value": 3.0}],
}

SAMPLE_EXTREMES = {
    "temperature_records": [
        {
            "station_id": "6105976",
            "month": 7,
            "day": 15,
            "record_high_c": 38.9,
            "record_high_year": 1953,
            "record_low_c": -37.8,
            "record_low_year": 1994,
        }
    ],
    "precipitation_records": [
        {
            "station_id": "6105976",
            "month": 9,
            "day": 21,
            "record_max_precip_mm": 63.0,
            "record_year": 1975,
        }
    ],
    "snowfall_records": [
        {
            "station_id": "6105976",
            "month": 11,
            "day": 12,
            "record_max_snowfall_cm": 42.0,
            "record_year": 1971,
        }
    ],
}

SAMPLE_GROWING = {
    "station_id": "6105976",
    "last_spring_frost": "1981-05-05",
    "first_fall_frost": "1981-10-01",
    "growing_season_days": 148,
}

SAMPLE_DEGREE_DAYS = {
    "station_id": "6105976",
    "period": "2025-01-01/2025-01-31",
    "total_heating_dd": 450.5,
    "total_cooling_dd": 0.0,
    "days_counted": 31,
}


class TestWxGetWeatherSummary:
    """Tests for wx_get_weather_summary tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_weather_summary returns make_response envelope on success."""
        from mcp_canada.modules.weather.summary.tools import wx_get_weather_summary

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_weather_summary",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_SUMMARY, False)
            result = await wx_get_weather_summary(location="Ottawa")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "msc-geomet"
        assert "data" in result

    @pytest.mark.asyncio
    async def test_requires_at_least_one_location_input(self):
        """wx_get_weather_summary returns INVALID_INPUT when no location provided."""
        from mcp_canada.modules.weather.summary.tools import wx_get_weather_summary

        result = await wx_get_weather_summary()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_returns_error_on_upstream_exception(self):
        """wx_get_weather_summary returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.summary.tools import wx_get_weather_summary

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_weather_summary",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            result = await wx_get_weather_summary(location="Ottawa")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_weather_summary passes lang to _meta envelope."""
        from mcp_canada.modules.weather.summary.tools import wx_get_weather_summary

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_weather_summary",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_SUMMARY, False)
            result = await wx_get_weather_summary(location="Ottawa", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestWxGetHistoricalExtremes:
    """Tests for wx_get_historical_extremes tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_historical_extremes returns make_response envelope on success."""
        from mcp_canada.modules.weather.summary.tools import wx_get_historical_extremes

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_historical_extremes",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_EXTREMES, False)
            result = await wx_get_historical_extremes(station_id="6105976")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """wx_get_historical_extremes returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.summary.tools import wx_get_historical_extremes

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_historical_extremes",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("API down")
            result = await wx_get_historical_extremes(station_id="6105976")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_historical_extremes passes lang to _meta."""
        from mcp_canada.modules.weather.summary.tools import wx_get_historical_extremes

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_historical_extremes",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_EXTREMES, True)
            result = await wx_get_historical_extremes(station_id="6105976", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestWxGetGrowingSeason:
    """Tests for wx_get_growing_season tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_growing_season returns make_response envelope on success."""
        from mcp_canada.modules.weather.summary.tools import wx_get_growing_season

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_growing_season",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_GROWING, False)
            result = await wx_get_growing_season(station_id="6105976")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_not_found_when_no_data(self):
        """wx_get_growing_season returns NOT_FOUND when no normals data available."""
        from mcp_canada.modules.weather.summary.tools import wx_get_growing_season

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_growing_season",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (None, False)
            result = await wx_get_growing_season(station_id="UNKNOWN")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """wx_get_growing_season returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.summary.tools import wx_get_growing_season

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_growing_season",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            result = await wx_get_growing_season(station_id="6105976")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestWxGetHeatingCoolingDays:
    """Tests for wx_get_heating_cooling_days tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_heating_cooling_days returns make_response envelope on success."""
        from mcp_canada.modules.weather.summary.tools import wx_get_heating_cooling_days

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_heating_cooling_days",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_DEGREE_DAYS, False)
            result = await wx_get_heating_cooling_days(station_id="6105976")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """wx_get_heating_cooling_days returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.summary.tools import wx_get_heating_cooling_days

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_heating_cooling_days",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            result = await wx_get_heating_cooling_days(station_id="6105976")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_heating_cooling_days passes lang to _meta."""
        from mcp_canada.modules.weather.summary.tools import wx_get_heating_cooling_days

        with patch(
            "mcp_canada.modules.weather.summary.tools.fetch_heating_cooling_days",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_DEGREE_DAYS, True)
            result = await wx_get_heating_cooling_days(station_id="6105976", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestDocstringQuality:
    """Verify BM25 docstring quality for all summary tools."""

    def _get_tool_functions(self):
        import mcp_canada.modules.weather.summary.tools as tools_mod
        import inspect
        return [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]

    def test_all_tools_have_use_for_line(self):
        """All wx_ tools must have 'Use for:' in their docstring."""
        fns = self._get_tool_functions()
        assert len(fns) >= 4, "Expected at least 4 wx_ tool functions"
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
        import mcp_canada.modules.weather.summary.tools as tools_mod
        fns = [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, f"{fn.__name__} missing lang parameter"
