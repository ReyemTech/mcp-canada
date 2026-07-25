"""Integration tests for weather/climate tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live MSC GeoMet APIs through the full MCP stack.

Run: uv run pytest tests/integration/test_weather_climate_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import assert_rows, call_tool, discover

pytestmark = pytest.mark.integration

# Well-known stable station: Ottawa CDA.
# 6158731 has climate-daily coverage; the climate-normals collection indexes
# Ottawa CDA under 6105976 (966 normals records). They are different stations,
# so normals must not be requested with the daily id.
OTTAWA_STATION = "6158731"
OTTAWA_NORMALS_STATION = "6105976"


class TestClimateScenarios:

    @pytest.mark.asyncio
    async def test_climate_daily_for_station(self, mcp_server):
        """'What was the daily temperature at Ottawa in January 2024?'"""
        data = await call_tool(mcp_server, "wx_get_climate_daily", {
            "station_id": OTTAWA_STATION,
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        })
        assert "_meta" in data, f"expected live envelope, got: {data}"
        assert data["_meta"]["source"]["api"] == "msc-geomet"
        # January 2024 at Ottawa CDA is closed historical data — an empty result
        # is a defect, not a live-data condition, so no allow_empty_reason.
        record = assert_rows(data, "wx_get_climate_daily")[0]
        assert "station_id" in record, f"record missing station_id: {record}"
        assert "date" in record, f"record missing date: {record}"

    @pytest.mark.asyncio
    async def test_climate_normals(self, mcp_server):
        """'What are the climate normals for Ottawa?'"""
        data = await call_tool(mcp_server, "wx_get_climate_normals", {
            "station_id": OTTAWA_NORMALS_STATION,
        })
        assert "_meta" in data, f"expected live envelope, got: {data}"
        # Ottawa CDA is a long-running station — normals must exist.
        record = assert_rows(data, "wx_get_climate_normals")[0]
        assert "station_id" in record, f"record missing station_id: {record}"
        assert "variable" in record or "period_begin" in record, (
            f"record missing both variable and period_begin: {record}"
        )

    @pytest.mark.asyncio
    async def test_climate_trends(self, mcp_server):
        """'What are the long-term precipitation trends in Canada?'"""
        # ahccd-trends carries precipitation only — "temperature" matches nothing.
        data = await call_tool(mcp_server, "wx_get_climate_trends", {
            "measurement_type": "total_precip",
        })
        assert "_meta" in data, f"expected live envelope, got: {data}"
        # National temperature trends are a published static series.
        record = assert_rows(data, "wx_get_climate_trends")[0]
        assert "measurement_type" in record or "trend" in record, (
            f"record missing both measurement_type and trend: {record}"
        )

    @pytest.mark.asyncio
    async def test_climate_projections_metadata(self, mcp_server):
        """'What CMIP5 climate projection data is available for Canada?'"""
        data = await call_tool(mcp_server, "wx_get_climate_projections", {
            "model": "cmip5",
        })
        assert "_meta" in data
        assert "data" in data
        # Projections returns metadata dict (not a list)
        meta = data["data"]
        assert isinstance(meta, dict)
        # Must include a note about limitation
        assert "note" in meta
        assert "metadata" in meta["note"].lower() or "400" in meta["note"]

    @pytest.mark.asyncio
    async def test_climate_monthly(self, mcp_server):
        """'What was the monthly climate summary for Ottawa in 2024?'"""
        data = await call_tool(mcp_server, "wx_get_climate_monthly", {
            "station_id": OTTAWA_STATION,
            "year": 2024,
        })
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_compare_climate_periods(self, mcp_server):
        """'Compare Ottawa climate between 2000-2010 and 2010-2020.'"""
        data = await call_tool(mcp_server, "wx_compare_climate_periods", {
            "station_id": OTTAWA_STATION,
            "period1_start": "2000-01-01",
            "period1_end": "2000-12-31",
            "period2_start": "2020-01-01",
            "period2_end": "2020-12-31",
        })
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drought_index(self, mcp_server):
        """'Get drought index data for the prairies.'"""
        data = await call_tool(mcp_server, "wx_get_drought_index", {
            "lat": 50.45,
            "lon": -104.6,
        })
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_discover_climate_tools(self, mcp_server):
        """Agent asks: 'find tools for historical climate data'"""
        results = await discover(mcp_server, "historical climate data")
        names = [r["name"] for r in results]
        # At least one climate tool should be discoverable
        [n for n in names if "climate" in n or "wx_" in n]
        assert any(n.startswith("wx_") for n in names), f"No wx_ tools found: {names}"
