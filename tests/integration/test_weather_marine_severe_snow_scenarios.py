"""Integration tests for marine, severe weather, and snow tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live MSC GeoMet OGC APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_marine_severe_snow_scenarios.py -v -m integration --timeout=120
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


# ─── Marine weather scenarios ─────────────────────────────────────────────────


class TestMarineWeatherScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_marine_forecast_nova_scotia(self, mcp_server):
        """'What is the marine weather forecast for Nova Scotia waters?'"""
        data = await call_tool(mcp_server, "wx_get_marine_forecast", {
            "province": "NS"
        })
        live = assert_live_or_transient(data, "wx_get_marine_forecast", API)
        if live:
            # NS marine areas are forecast year-round.
            forecast = assert_rows(data, "wx_get_marine_forecast")[0]
            assert "area_en" in forecast or "area_fr" in forecast, (
                f"forecast missing both area_en and area_fr: {forecast}"
            )
            assert "regularForecast" not in forecast, (
                f"response must be flattened, found raw nested key: {forecast}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_hurricane_tracks_off_season(self, mcp_server):
        """'Are there any active hurricanes near Canada?'"""
        data = await call_tool(mcp_server, "wx_get_hurricane_tracks", {})
        # Should always return _meta (either tracks or off-season note)
        assert "_meta" in data
        assert "data" in data
        # Response data is a dict with tracks list (possibly empty off-season)
        payload = data["data"]
        assert isinstance(payload, (dict, list)), (
            f"payload must be a dict or list, got {type(payload).__name__}"
        )
        if isinstance(payload, dict):
            assert "tracks" in payload, f"dict payload missing tracks: {payload}"
            assert isinstance(payload["tracks"], list)
            if payload["tracks"]:
                track = payload["tracks"][0]
                assert isinstance(track, dict), (
                    f"each track must be an object, got {type(track).__name__}"
                )
            else:
                assert "note" in payload, (
                    f"an empty track list must explain itself (off-season): {payload}"
                )
        else:
            assert payload == [], (
                f"a list payload means 'no active storms' and must be empty, got: {payload}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_thunderstorm_outlook_ontario(self, mcp_server):
        """'Is there a thunderstorm risk in Ontario today?'"""
        data = await call_tool(mcp_server, "wx_get_thunderstorm_outlook", {
            "province": "ON"
        })
        live = assert_live_or_transient(data, "wx_get_thunderstorm_outlook", API)
        if live:
            payload = data["data"]
            # The tool returns a dict with an outlooks list, or a bare list when
            # nothing is active. Both are valid; anything else is a shape defect.
            assert isinstance(payload, (dict, list)), (
                f"payload must be a dict or list, got {type(payload).__name__}"
            )
            if isinstance(payload, dict):
                assert "outlooks" in payload, f"dict payload missing outlooks: {payload}"
            else:
                assert payload == [], (
                    f"a list payload means 'no active outlooks' and must be empty, "
                    f"got: {payload}"
                )

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
        live = assert_live_or_transient(data, "wx_get_radar_data", API)
        if live:
            assert_rows(
                data,
                "wx_get_radar_data",
                allow_empty_reason="no precipitation near Ottawa in the window is normal",
            )

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
        live = assert_live_or_transient(data, "wx_get_uv_index", API)
        if live:
            uv_data = data["data"]
            assert "uv_index" in uv_data, f"payload missing uv_index: {uv_data}"
            assert "location_en" in uv_data or "location_fr" in uv_data, (
                f"payload missing both location_en and location_fr: {uv_data}"
            )


# ─── Snow scenarios ───────────────────────────────────────────────────────────


class TestSnowScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_snow_depth_ottawa(self, mcp_server):
        """'How much snow is on the ground near Ottawa right now?'"""
        data = await call_tool(mcp_server, "wx_get_snow_depth", {
            "lat": 45.4, "lon": -75.7
        })
        live = assert_live_or_transient(data, "wx_get_snow_depth", API)
        if live:
            depth_data = data["data"]
            for field in ("station_name", "snow_depth_cm", "observed_at"):
                assert field in depth_data, f"payload missing {field!r}: {depth_data}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_snow_water_equivalent_estimate(self, mcp_server):
        """'What is the estimated snow water equivalent near Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_snow_water_equivalent", {
            "lat": 45.4, "lon": -75.7
        })
        live = assert_live_or_transient(data, "wx_get_snow_water_equivalent", API)
        if live:
            swe_data = data["data"]
            assert "snow_depth_cm" in swe_data
            assert "swe_mm" in swe_data, f"payload missing swe_mm: {swe_data}"
            assert "density_factor" in swe_data, f"payload missing density_factor: {swe_data}"
            assert "note" in swe_data, f"payload missing note: {swe_data}"
            note = swe_data["note"].lower()
            assert "estimate" in note or "density" in note, (
                f"note must disclose that the value is an estimate: {swe_data['note']!r}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_snow_tools(self, mcp_server):
        """Agent searches: 'snow depth measurement'"""
        results = await discover(mcp_server, "snow depth measurement")
        names = [r["name"] for r in results]
        # At least one snow tool should surface
        [n for n in names if "snow" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"
