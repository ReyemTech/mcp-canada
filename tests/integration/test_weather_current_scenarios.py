"""Integration tests for weather/current tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live MSC GeoMet APIs through the full MCP stack.

Run: uv run pytest tests/integration/test_weather_current_scenarios.py -v -m integration --timeout=120
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


class TestWxCurrentConditions:

    @pytest.mark.asyncio
    async def test_current_conditions_by_city(self, mcp_server):
        """'What's the weather in Toronto?'"""
        data = await call_tool(mcp_server, "wx_get_current_conditions", {
            "location": "Toronto"
        })
        live = assert_live_or_transient(data, "wx_get_current_conditions", API)
        if live:
            assert data["data"] is not None, (
                f"Toronto is a major station — a live response must carry a payload. "
                f"Got: {data['data']!r}"
            )

    @pytest.mark.asyncio
    async def test_current_conditions_by_coords(self, mcp_server):
        """Agent passes lat/lon for Ottawa directly."""
        data = await call_tool(mcp_server, "wx_get_current_conditions", {
            "lat": 45.4, "lon": -75.7
        })
        live = assert_live_or_transient(data, "wx_get_current_conditions", API)
        if live:
            assert data["data"] is not None, (
                f"Ottawa coordinates must resolve to a payload. Got: {data['data']!r}"
            )

    @pytest.mark.asyncio
    async def test_forecast_for_location(self, mcp_server):
        """'What's the forecast for Vancouver?'"""
        data = await call_tool(mcp_server, "wx_get_forecast", {
            "location": "Vancouver"
        })
        live = assert_live_or_transient(data, "wx_get_forecast", API)
        if live:
            assert isinstance(data["data"], list), (
                f"Forecast data must be a list, got {type(data['data']).__name__}"
            )

    @pytest.mark.asyncio
    async def test_weather_alerts_by_province(self, mcp_server):
        """'Are there any weather alerts in Ontario?'"""
        data = await call_tool(mcp_server, "wx_get_weather_alerts", {
            "province": "ON"
        })
        live = assert_live_or_transient(data, "wx_get_weather_alerts", API)
        if live:
            assert_rows(
                data,
                "wx_get_weather_alerts",
                allow_empty_reason="no active alerts in Ontario is the normal case",
            )

    @pytest.mark.asyncio
    async def test_station_search_by_province(self, mcp_server):
        """'Find climate stations in BC.'"""
        data = await call_tool(mcp_server, "wx_search_stations", {
            "province": "BC"
        })
        live = assert_live_or_transient(data, "wx_search_stations", API)
        if live:
            # BC always has climate stations — an empty result here is a defect,
            # so no allow_empty_reason.
            stations = assert_rows(data, "wx_search_stations")
            station = stations[0]
            for field in ("station_id", "station_name", "lat", "lon"):
                assert field in station, (
                    f"station row missing {field!r}: {station}"
                )
            # Decimal degrees, not DMS milliarcseconds
            assert station["lat"] is None or -90 <= station["lat"] <= 90, (
                f"lat must be decimal degrees, got {station['lat']!r} — a value "
                f"outside [-90, 90] means DMS milliarcseconds leaked through"
            )

    @pytest.mark.asyncio
    async def test_station_hourly_data(self, mcp_server):
        """'Get hourly observations for Ottawa station.'"""
        data = await call_tool(mcp_server, "wx_get_station_data", {
            "station_id": "6105976",
            "limit": 5,
        })
        assert_live_or_transient(data, "wx_get_station_data")

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
        live = assert_live_or_transient(data, "wx_get_weather_alerts", API)
        if live:
            alerts = assert_rows(
                data,
                "wx_get_weather_alerts",
                allow_empty_reason="no active alerts anywhere in Canada is possible in calm weather",
            )
            for alert in alerts[:1]:
                assert "alert_type" in alert, f"alert row missing alert_type: {alert}"
                assert "province" in alert, f"alert row missing province: {alert}"
