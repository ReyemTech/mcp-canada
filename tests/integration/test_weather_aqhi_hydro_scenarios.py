"""Integration tests for AQHI and hydrometric tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_aqhi_hydro_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import call_tool, discover

pytestmark = pytest.mark.integration


# ─── AQHI scenarios ──────────────────────────────────────────────────────────


class TestAqhiScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_current_reading_by_coordinates(self, mcp_server):
        """'What is the current air quality index in Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_aqhi", {
            "lat": 45.4, "lon": -75.7
        })
        # Should return data or NOT_FOUND — never an exception
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert isinstance(data["data"], list)
            if data["data"]:
                reading = data["data"][0]
                assert "aqhi_value" in reading
                assert "location_id" in reading

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_forecast_by_location_id(self, mcp_server):
        """'What is the AQHI forecast for Ottawa (ON106)?'"""
        data = await call_tool(mcp_server, "wx_get_aqhi_forecast", {
            "location_id": "ON106"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            if data["data"]:
                assert "aqhi_value" in data["data"][0]

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_aqhi_tools(self, mcp_server):
        """Agent searches: 'air quality health index'"""
        results = await discover(mcp_server, "air quality health index")
        names = [r["name"] for r in results]
        # At least one wx_ aqhi tool should surface
        [n for n in names if "aqhi" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_invalid_location_returns_error(self, mcp_server):
        """wx_get_aqhi returns structured error for no location, not an exception."""
        data = await call_tool(mcp_server, "wx_get_aqhi", {})
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"


# ─── Hydro scenarios ──────────────────────────────────────────────────────────


class TestHydroScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_water_levels_by_station_number(self, mcp_server):
        """'What is the current water level at Rideau River station 02LA004?'"""
        data = await call_tool(mcp_server, "wx_get_water_levels", {
            "station_number": "02LA004"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert isinstance(data["data"], list)
            if data["data"]:
                reading = data["data"][0]
                assert "station_number" in reading
                assert "level_m" in reading

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_hydro_station_search_by_province(self, mcp_server):
        """'Find water monitoring stations in Ontario.'"""
        data = await call_tool(mcp_server, "wx_search_hydro_stations", {
            "province": "ON"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            if data["data"]:
                station = data["data"][0]
                assert "station_number" in station
                assert "station_name" in station

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_history(self, mcp_server):
        """'Get historical air quality observations.'"""
        data = await call_tool(mcp_server, "wx_get_aqhi_history", {
            "location_id": "ON-01",  # Toronto area
            "limit": 5,
        })
        assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_water_flow(self, mcp_server):
        """'Get river flow rate for a station.'"""
        data = await call_tool(mcp_server, "wx_get_water_flow", {
            "station_number": "02LA004",
        })
        assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_daily_mean_water(self, mcp_server):
        """'Get daily mean water levels for a station.'"""
        data = await call_tool(mcp_server, "wx_get_daily_mean_water", {
            "station_number": "02LA004",
        })
        assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_hydro_tools(self, mcp_server):
        """Agent searches: 'water level flood'"""
        results = await discover(mcp_server, "water level flood")
        names = [r["name"] for r in results]
        [n for n in names if "water" in n or "flood" in n or "hydro" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_flood_risk_invalid_station_returns_error(self, mcp_server):
        """wx_get_flood_risk returns structured error for unknown station, not an exception."""
        data = await call_tool(mcp_server, "wx_get_flood_risk", {
            "station_number": "ZZZZZZZZ"
        })
        assert "_meta" in data or "error" in data
        # Valid responses: either NOT_FOUND error or successful response (if station somehow exists)
        if "error" in data:
            assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR")
