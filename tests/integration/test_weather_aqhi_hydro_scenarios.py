"""Integration tests for AQHI and hydrometric tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_aqhi_hydro_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import (
    assert_live_or_transient,
    assert_rows,
    call_tool,
    discover,
)

pytestmark = pytest.mark.integration

API = "msc-geomet"

# AQHI location_ids are opaque 5-letter MSC codes, NOT province-prefixed strings.
# Earlier revisions of this file used invented ids ("ON106", "ON-01") that match
# nothing, and the masked assertions hid the resulting NOT_FOUND.
# Resolved from the live collections 2026-07-25 by filtering location_name_en.
# Note the id differs per collection for the same city: Toronto observations are
# FDQBU while Toronto forecasts are FCWYG. Ottawa is FEVNT in both.
OTTAWA_AQHI = "FEVNT"


# ─── AQHI scenarios ──────────────────────────────────────────────────────────


class TestAqhiScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_current_reading_by_coordinates(self, mcp_server):
        """'What is the current air quality index in Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_aqhi", {
            "lat": 45.4, "lon": -75.7
        })
        live = assert_live_or_transient(data, "wx_get_aqhi", API)
        if live:
            # Ottawa is inside an AQHI forecast region and readings are hourly.
            reading = assert_rows(data, "wx_get_aqhi")[0]
            assert "aqhi_value" in reading, f"reading missing aqhi_value: {reading}"
            assert "location_id" in reading, f"reading missing location_id: {reading}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_forecast_by_location_id(self, mcp_server):
        """'What is the AQHI forecast for Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_aqhi_forecast", {
            "location_id": OTTAWA_AQHI
        })
        live = assert_live_or_transient(data, "wx_get_aqhi_forecast", API)
        if live:
            rows = assert_rows(data, "wx_get_aqhi_forecast")
            assert "aqhi_value" in rows[0], f"forecast row missing aqhi_value: {rows[0]}"

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
        live = assert_live_or_transient(data, "wx_get_water_levels", API)
        if live:
            reading = assert_rows(data, "wx_get_water_levels")[0]
            assert "station_number" in reading, f"reading missing station_number: {reading}"
            assert "level_m" in reading, f"reading missing level_m: {reading}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_hydro_station_search_by_province(self, mcp_server):
        """'Find water monitoring stations in Ontario.'"""
        data = await call_tool(mcp_server, "wx_search_hydro_stations", {
            "province": "ON"
        })
        live = assert_live_or_transient(data, "wx_search_hydro_stations", API)
        if live:
            # Ontario always has hydrometric stations.
            station = assert_rows(data, "wx_search_hydro_stations")[0]
            assert "station_number" in station, f"station missing station_number: {station}"
            assert "station_name" in station, f"station missing station_name: {station}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_aqhi_history(self, mcp_server):
        """'Get historical air quality observations.'"""
        data = await call_tool(mcp_server, "wx_get_aqhi_history", {
            "location_id": OTTAWA_AQHI,
            "limit": 5,
        })
        assert_live_or_transient(data, "wx_get_aqhi_history")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_water_flow(self, mcp_server):
        """'Get river flow rate for a station.'"""
        data = await call_tool(mcp_server, "wx_get_water_flow", {
            "station_number": "02LA004",
        })
        assert_live_or_transient(data, "wx_get_water_flow")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_daily_mean_water(self, mcp_server):
        """'Get daily mean water levels for a station.'"""
        data = await call_tool(mcp_server, "wx_get_daily_mean_water", {
            "station_number": "02LA004",
        })
        assert_live_or_transient(data, "wx_get_daily_mean_water")

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
        # This is an error-PATH test: station ZZZZZZZZ does not exist, so
        # NOT_FOUND is the correct answer and must not be treated as an outage.
        if "error" in data:
            assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR"), (
                f"unknown station must yield NOT_FOUND (or a transient "
                f"UPSTREAM_ERROR), got: {data['error']}"
            )
        else:
            assert "_meta" in data, f"expected an error or an envelope, got: {data}"
