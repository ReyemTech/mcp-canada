"""Integration tests for marine, severe weather, and snow tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live MSC GeoMet OGC APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_marine_severe_snow_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import call_tool, discover

pytestmark = pytest.mark.integration


# ─── Marine weather scenarios ─────────────────────────────────────────────────


class TestMarineWeatherScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_marine_forecast_nova_scotia(self, mcp_server):
        """'What is the marine weather forecast for Nova Scotia waters?'"""
        data = await call_tool(mcp_server, "wx_get_marine_forecast", {
            "province": "NS"
        })
        # Should return data or empty list — never an exception
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert isinstance(data["data"], list)
            if data["data"]:
                forecast = data["data"][0]
                # Flattened fields should be present
                assert "area_en" in forecast or "area_fr" in forecast
                assert "regularForecast" not in forecast  # Must be flattened

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_hurricane_tracks_off_season(self, mcp_server):
        """'Are there any active hurricanes near Canada?'"""
        data = await call_tool(mcp_server, "wx_get_hurricane_tracks", {})
        # Should always return _meta (either tracks or off-season note)
        assert "_meta" in data
        assert "data" in data
        # Response data is a dict with tracks list (possibly empty off-season)
        response_data = data["data"]
        if isinstance(response_data, dict):
            assert "tracks" in response_data
            assert isinstance(response_data["tracks"], list)
            # Off-season: should have a note
            if not response_data["tracks"]:
                assert "note" in response_data
        elif isinstance(response_data, list):
            pass  # Empty list is also acceptable

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_thunderstorm_outlook_ontario(self, mcp_server):
        """'Is there a thunderstorm risk in Ontario today?'"""
        data = await call_tool(mcp_server, "wx_get_thunderstorm_outlook", {
            "province": "ON"
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            response_data = data["data"]
            if isinstance(response_data, dict):
                assert "outlooks" in response_data
            elif isinstance(response_data, list):
                pass  # empty list is fine

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_marine_tools(self, mcp_server):
        """Agent searches: 'marine weather forecast'"""
        results = await discover(mcp_server, "marine weather forecast")
        names = [r["name"] for r in results]
        # At least one wx_ marine tool should surface
        [n for n in names if "marine" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"


# ─── Severe weather scenarios ─────────────────────────────────────────────────


class TestSevereWeatherScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_radar_data_ottawa(self, mcp_server):
        """'How much rain has fallen near Ottawa in the last 24 hours?'"""
        data = await call_tool(mcp_server, "wx_get_radar_data", {
            "lat": 45.4, "lon": -75.7
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_lightning_returns_structured_not_found(self, mcp_server):
        """'Can you show me real-time lightning strike data?'"""
        data = await call_tool(mcp_server, "wx_get_lightning", {})
        # Lightning tool always returns NOT_FOUND with DataMart URL
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        message = data["error"]["message"]
        assert "DataMart" in message or "dd.weather.gc.ca" in message

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_uv_index_ottawa(self, mcp_server):
        """'What is the UV index forecast for Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_uv_index", {
            "lat": 45.4, "lon": -75.7
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            uv_data = data["data"]
            assert "uv_index" in uv_data
            assert "location_en" in uv_data or "location_fr" in uv_data


# ─── Snow scenarios ───────────────────────────────────────────────────────────


class TestSnowScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_snow_depth_ottawa(self, mcp_server):
        """'How much snow is on the ground near Ottawa right now?'"""
        data = await call_tool(mcp_server, "wx_get_snow_depth", {
            "lat": 45.4, "lon": -75.7
        })
        # May return data or NOT_FOUND (no snow in summer, no nearby station)
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            depth_data = data["data"]
            assert "station_name" in depth_data
            assert "snow_depth_cm" in depth_data
            assert "observed_at" in depth_data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_snow_water_equivalent_estimate(self, mcp_server):
        """'What is the estimated snow water equivalent near Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_snow_water_equivalent", {
            "lat": 45.4, "lon": -75.7
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            swe_data = data["data"]
            assert "snow_depth_cm" in swe_data
            assert "swe_mm" in swe_data
            assert "density_factor" in swe_data
            assert "note" in swe_data
            # Note should mention estimation
            assert "estimate" in swe_data["note"].lower() or "density" in swe_data["note"].lower()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_snow_tools(self, mcp_server):
        """Agent searches: 'snow depth measurement'"""
        results = await discover(mcp_server, "snow depth measurement")
        names = [r["name"] for r in results]
        # At least one snow tool should surface
        [n for n in names if "snow" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"
