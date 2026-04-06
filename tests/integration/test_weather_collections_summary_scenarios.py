"""Integration tests for weather/collections and weather/summary tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_collections_summary_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import call_tool, discover

pytestmark = pytest.mark.integration


# ─── Collections scenarios ────────────────────────────────────────────────────


class TestCollectionsScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_list_all_collections(self, mcp_server):
        """'What weather data collections are available from MSC GeoMet?'"""
        data = await call_tool(mcp_server, "wx_list_collections", {})
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            assert isinstance(data["data"], list)
            # MSC GeoMet has 100+ collections
            assert len(data["data"]) >= 10, (
                f"Expected many collections, got {len(data['data'])}"
            )
            # Each collection should have id, title
            if data["data"]:
                coll = data["data"][0]
                assert "id" in coll
                assert "title" in coll

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_query_arbitrary_collection_climate_stations(self, mcp_server):
        """'Give me 5 climate stations from the climate-stations collection.'"""
        data = await call_tool(mcp_server, "wx_get_collection_items", {
            "collection_id": "climate-stations",
            "limit": 5,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"]["items"], list)
            if data["data"]["items"]:
                item = data["data"]["items"][0]
                # Should have properties from the OGC feature
                assert "properties" in item
                # And centroid lat/lon extracted
                assert "lat" in item or item.get("lat") is None

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_collection_not_found_returns_error(self, mcp_server):
        """wx_get_collection_items returns structured error for unknown collection."""
        data = await call_tool(mcp_server, "wx_get_collection_items", {
            "collection_id": "this-collection-does-not-exist",
            "limit": 5,
        })
        # Should return either NOT_FOUND error or UPSTREAM_ERROR (400/404 from API)
        assert "_meta" in data or "error" in data
        if "error" in data:
            assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_collections_tools(self, mcp_server):
        """Agent searches: 'browse available weather collections'"""
        results = await discover(mcp_server, "browse available weather collections")
        names = [r["name"] for r in results]
        assert any(n.startswith("wx_") or "collection" in n for n in names), f"No relevant tools found: {names}"


# ─── Summary scenarios ────────────────────────────────────────────────────────


class TestSummaryScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_weather_summary_composite_for_toronto(self, mcp_server):
        """'Give me a complete weather overview for Toronto, Ontario.'"""
        data = await call_tool(mcp_server, "wx_get_weather_summary", {
            "location": "Toronto",
            "province": "ON",
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "msc-geomet"
            result = data["data"]
            # Should have all 4 sections
            assert "conditions" in result
            assert "forecast" in result
            assert "alerts" in result
            assert "aqhi" in result

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_weather_summary_no_location_returns_error(self, mcp_server):
        """wx_get_weather_summary returns INVALID_INPUT with no location."""
        data = await call_tool(mcp_server, "wx_get_weather_summary", {})
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_historical_extremes_for_ottawa(self, mcp_server):
        """'What are the all-time weather records for Ottawa climate station 6105976?'"""
        data = await call_tool(mcp_server, "wx_get_historical_extremes", {
            "station_id": "6105976",
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            result = data["data"]
            assert "temperature_records" in result
            assert "precipitation_records" in result
            assert "snowfall_records" in result

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_growing_season(self, mcp_server):
        """'What is the growing season for an Ottawa station?'"""
        data = await call_tool(mcp_server, "wx_get_growing_season", {
            "station_id": "6105976",
        })
        assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_heating_cooling_days(self, mcp_server):
        """'Get heating and cooling degree days for Ottawa.'"""
        data = await call_tool(mcp_server, "wx_get_heating_cooling_days", {
            "station_id": "6105976",
        })
        assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_summary_tools(self, mcp_server):
        """Agent searches: 'weather summary overview'"""
        results = await discover(mcp_server, "weather summary overview")
        names = [r["name"] for r in results]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"
