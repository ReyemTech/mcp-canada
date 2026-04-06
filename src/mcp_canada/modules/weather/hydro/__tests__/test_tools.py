"""Unit tests for hydrometric @tool functions."""

import pytest
from unittest.mock import AsyncMock, patch


SAMPLE_LEVEL_READINGS = [
    {
        "station_number": "02LA004",
        "station_name": "RIDEAU RIVER AT OTTAWA",
        "level_m": 72.45,
        "discharge_m3s": 115.0,
        "datetime": "2026-04-05T10:00:00Z",
        "lat": 45.3,
        "lon": -76.4,
    }
]

SAMPLE_STATIONS = [
    {
        "station_number": "02LA004",
        "station_name": "RIDEAU RIVER AT OTTAWA",
        "province": "ON",
        "lat": 45.3,
        "lon": -76.4,
        "status": "Active",
        "real_time": True,
        "drainage_area_km2": 3828.0,
    }
]

SAMPLE_FLOOD_RISK = {
    "station_number": "02LA004",
    "station_name": "RIDEAU RIVER AT OTTAWA",
    "current_level": 72.45,
    "current_discharge": 115.0,
    "historical_max": 78.34,
    "historical_max_discharge": 488.0,
    "percent_of_max": 92.5,
    "risk_level": "high",
    "datetime": "2026-04-05T10:00:00Z",
}


class TestWxGetWaterLevels:
    """Tests for wx_get_water_levels tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_water_levels returns make_response envelope with _meta."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_LEVEL_READINGS, False)
            result = await wx_get_water_levels(station_number="02LA004")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "msc-geomet"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_readings(self):
        """wx_get_water_levels returns NOT_FOUND when no data available."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_water_levels(station_number="INVALID")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_no_location_returns_invalid_input(self):
        """wx_get_water_levels returns INVALID_INPUT when no location provided."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_levels

        result = await wx_get_water_levels()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_water_levels passes lang to _meta envelope."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_LEVEL_READINGS, False)
            result = await wx_get_water_levels(station_number="02LA004", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestWxGetWaterFlow:
    """Tests for wx_get_water_flow tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_water_flow returns make_response envelope with _meta."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_flow

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_water_flow",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_LEVEL_READINGS, False)
            result = await wx_get_water_flow(station_number="02LA004")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_no_location_returns_invalid_input(self):
        """wx_get_water_flow returns INVALID_INPUT when no location provided."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_flow

        result = await wx_get_water_flow()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_returns_error_when_no_data(self):
        """wx_get_water_flow returns NOT_FOUND when no data available."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_water_flow

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_water_flow",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_water_flow(station_number="INVALID")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"


class TestWxGetDailyMeanWater:
    """Tests for wx_get_daily_mean_water tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_daily_mean_water returns make_response with _meta."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_daily_mean_water

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_daily_mean_water",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_LEVEL_READINGS, False)
            result = await wx_get_daily_mean_water(station_number="02LA004")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_data(self):
        """wx_get_daily_mean_water returns NOT_FOUND when no data."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_daily_mean_water

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_daily_mean_water",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_daily_mean_water(station_number="INVALID")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"


class TestWxSearchHydroStations:
    """Tests for wx_search_hydro_stations tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_search_hydro_stations returns make_response envelope."""
        from mcp_canada.modules.weather.hydro.tools import wx_search_hydro_stations

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_hydro_stations",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_STATIONS, False)
            result = await wx_search_hydro_stations(province="ON")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_stations(self):
        """wx_search_hydro_stations returns NOT_FOUND when no stations found."""
        from mcp_canada.modules.weather.hydro.tools import wx_search_hydro_stations

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_hydro_stations",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_search_hydro_stations(province="ZZ")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_no_location_returns_error(self):
        """wx_search_hydro_stations returns INVALID_INPUT with no location."""
        from mcp_canada.modules.weather.hydro.tools import wx_search_hydro_stations

        result = await wx_search_hydro_stations()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


class TestWxGetFloodRisk:
    """Tests for wx_get_flood_risk tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_risk_level(self):
        """wx_get_flood_risk returns make_response with risk_level in data."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_flood_risk",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_FLOOD_RISK, False)
            result = await wx_get_flood_risk(station_number="02LA004")

        assert "_meta" in result
        assert result["data"]["risk_level"] == "high"

    @pytest.mark.asyncio
    async def test_returns_error_when_no_data(self):
        """wx_get_flood_risk returns NOT_FOUND when station has no data."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_flood_risk",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (None, False)
            result = await wx_get_flood_risk(station_number="INVALID")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_exception_returns_upstream_error(self):
        """wx_get_flood_risk returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.weather.hydro.tools import wx_get_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.tools.fetch_flood_risk",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Connection error")
            result = await wx_get_flood_risk(station_number="02LA004")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestDocstringQuality:
    """Verify BM25 docstring quality for all hydro tools."""

    def _get_tool_functions(self):
        import mcp_canada.modules.weather.hydro.tools as tools_mod
        import inspect
        return [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]

    def test_all_tools_have_use_for_line(self):
        """All wx_ tools must have 'Use for:' in their docstring."""
        fns = self._get_tool_functions()
        assert len(fns) >= 5, "Expected at least 5 wx_ tool functions in hydro"
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
        import mcp_canada.modules.weather.hydro.tools as tools_mod
        fns = [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, f"{fn.__name__} missing lang parameter"
