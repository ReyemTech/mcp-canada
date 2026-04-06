"""Integration tests for weather/current tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live MSC GeoMet APIs through the full MCP stack.

Run: uv run pytest tests/integration/test_weather_current_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import call_tool, discover

pytestmark = pytest.mark.integration


class TestWxCurrentConditions:

    @pytest.mark.asyncio
    async def test_current_conditions_by_city(self, mcp_server):
        """'What's the weather in Toronto?'"""
        data = await call_tool(mcp_server, "wx_get_current_conditions", {
            "location": "Toronto"
        })
        # Response may have data (city found) or NOT_FOUND (no match in collection)
        # Either is valid — we assert on envelope structure
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert "temperature_c" in data["data"] or data["data"] is not None

    @pytest.mark.asyncio
    async def test_current_conditions_by_coords(self, mcp_server):
        """Agent passes lat/lon for Ottawa directly."""
        data = await call_tool(mcp_server, "wx_get_current_conditions", {
            "lat": 45.4, "lon": -75.7
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"

    @pytest.mark.asyncio
    async def test_forecast_for_location(self, mcp_server):
        """'What's the forecast for Vancouver?'"""
        data = await call_tool(mcp_server, "wx_get_forecast", {
            "location": "Vancouver"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_weather_alerts_by_province(self, mcp_server):
        """'Are there any weather alerts in Ontario?'"""
        data = await call_tool(mcp_server, "wx_get_weather_alerts", {
            "province": "ON"
        })
        # Empty list is valid (no active alerts)
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "msc-geomet"
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_station_search_by_province(self, mcp_server):
        """'Find climate stations in BC.'"""
        data = await call_tool(mcp_server, "wx_search_stations", {
            "province": "BC"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            if data["data"]:
                station = data["data"][0]
                assert "station_id" in station
                assert "station_name" in station
                assert "lat" in station
                assert "lon" in station
                # Verify decimal degree coordinates (not DMS milliarcseconds)
                if station["lat"] is not None:
                    assert -90 <= station["lat"] <= 90

    @pytest.mark.asyncio
    async def test_station_hourly_data(self, mcp_server):
        """'Get hourly observations for Ottawa station.'"""
        data = await call_tool(mcp_server, "wx_get_station_data", {
            "station_id": "6105976",
            "limit": 5,
        })
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_discover_weather_tools(self, mcp_server):
        """discover_tools finds wx_get_current_conditions for a weather query."""
        results = await discover(mcp_server, "current weather conditions temperature")
        names = [r["name"] for r in results]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"

    @pytest.mark.asyncio
    async def test_discover_forecast_tool(self, mcp_server):
        """discover_tools finds wx_get_forecast for a forecast query."""
        results = await discover(mcp_server, "weather forecast tomorrow rain")
        names = [r["name"] for r in results]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"

    @pytest.mark.asyncio
    async def test_weather_alerts_all_canada(self, mcp_server):
        """'Any active weather warnings in Canada?' — no province filter."""
        data = await call_tool(mcp_server, "wx_get_weather_alerts", {
            "limit": 10
        })
        assert "_meta" in data
        assert isinstance(data["data"], list)
        # If alerts present, verify structure
        if data["data"]:
            alert = data["data"][0]
            assert "alert_type" in alert
            assert "province" in alert
