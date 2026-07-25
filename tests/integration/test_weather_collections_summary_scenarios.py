"""Integration tests for weather/collections and weather/summary tools through MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_weather_collections_summary_scenarios.py -v -m integration --timeout=120
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


# ─── Collections scenarios ────────────────────────────────────────────────────


class TestCollectionsScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_list_all_collections(self, mcp_server):
        """'What weather data collections are available from MSC GeoMet?'"""
        data = await call_tool(mcp_server, "wx_list_collections", {})
        live = assert_live_or_transient(data, "wx_list_collections", API)
        if live:
            collections = assert_rows(data, "wx_list_collections")
            # MSC GeoMet publishes 100+ collections
            assert len(collections) >= 10, (
                f"Expected many collections, got {len(collections)}"
            )
            coll = collections[0]
            assert "id" in coll, f"collection missing id: {coll}"
            assert "title" in coll, f"collection missing title: {coll}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_query_arbitrary_collection_climate_stations(self, mcp_server):
        """'Give me 5 climate stations from the climate-stations collection.'"""
        data = await call_tool(mcp_server, "wx_get_collection_items", {
            "collection_id": "climate-stations",
            "limit": 5,
        })
        live = assert_live_or_transient(data, "wx_get_collection_items", API)
        if live:
            items = data["data"]["items"]
            assert isinstance(items, list), (
                f"items must be a list, got {type(items).__name__}"
            )
            # climate-stations is a static reference collection — asking for 5 and
            # getting none means the query is broken, not that the data is quiet.
            assert items, f"climate-stations returned no items: {data['data']}"
            item = items[0]
            assert "properties" in item, f"item missing OGC properties: {item}"
            assert "lat" in item, f"item missing extracted centroid lat: {item}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_collection_not_found_returns_error(self, mcp_server):
        """wx_get_collection_items returns structured error for unknown collection."""
        data = await call_tool(mcp_server, "wx_get_collection_items", {
            "collection_id": "this-collection-does-not-exist",
            "limit": 5,
        })
        # Error-PATH test: the collection genuinely does not exist, so NOT_FOUND
        # is the correct answer and is not treated as an outage.
        if "error" in data:
            assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR"), (
                f"unknown collection must yield NOT_FOUND (or UPSTREAM_ERROR if "
                f"the API 400s), got: {data['error']}"
            )
        else:
            assert "_meta" in data, f"expected an error or an envelope, got: {data}"

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
        live = assert_live_or_transient(data, "wx_get_weather_summary", API)
        if live:
            result = data["data"]
            for section in ("conditions", "forecast", "alerts", "aqhi"):
                assert section in result, (
                    f"composite summary missing {section!r} section: {list(result)}"
                )

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
        live = assert_live_or_transient(data, "wx_get_historical_extremes", API)
        if live:
            result = data["data"]
            for section in ("temperature_records", "precipitation_records", "snowfall_records"):
                assert section in result, (
                    f"extremes missing {section!r} section: {list(result)}"
                )

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
