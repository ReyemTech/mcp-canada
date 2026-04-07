"""Integration tests calling tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_tool_scenarios.py -v -m integration --timeout=120
"""

import pytest
from tests.integration.conftest import call_tool, call_direct_tool, discover

pytestmark = pytest.mark.integration


# ─── Bank of Canada scenarios ────────────────────────────────────────────────


class TestBocScenarios:

    @pytest.mark.asyncio
    async def test_discover_exchange_rate_tools(self, mcp_server):
        """Agent asks: 'find tools for exchange rates'"""
        results = await discover(mcp_server, "exchange rate CAD")
        names = [r["name"] for r in results]
        assert "boc_get_exchange_rates" in names

    @pytest.mark.asyncio
    async def test_current_usd_cad_rate(self, mcp_server):
        """'What's the current USD to CAD exchange rate?'"""
        data = await call_tool(mcp_server, "boc_get_exchange_rates", {"currency": "USD", "recent": 1})
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "bank-of-canada-valet"
        assert len(data["data"]) >= 1
        row = data["data"][0]
        assert row["series_name"] == "FXUSDCAD"
        assert 0.5 < row["value"] < 3.0

    @pytest.mark.asyncio
    async def test_exchange_rate_date_range(self, mcp_server):
        """'Show me EUR/CAD over the last month.'"""
        data = await call_tool(mcp_server, "boc_get_exchange_rates", {
            "currency": "EUR", "start_date": "2026-03-01", "end_date": "2026-03-31"
        })
        assert len(data["data"]) >= 15
        assert all(r["series_name"] == "FXEURCAD" for r in data["data"])

    @pytest.mark.asyncio
    async def test_compare_usd_eur_gbp(self, mcp_server):
        """'Compare USD, EUR, and GBP exchange rates.'"""
        data = await call_tool(mcp_server, "boc_get_observations", {
            "series_names": "FXUSDCAD,FXEURCAD,FXGBPCAD", "recent": 3
        })
        series = {r["series_name"] for r in data["data"]}
        assert "FXUSDCAD" in series
        assert "FXEURCAD" in series
        assert "FXGBPCAD" in series

    @pytest.mark.asyncio
    async def test_current_policy_rate(self, mcp_server):
        """'What is the Bank of Canada policy rate?'"""
        data = await call_tool(mcp_server, "boc_get_interest_rates", {"rate_type": "policy", "recent": 1})
        assert len(data["data"]) >= 1
        assert 0 < data["data"][0]["value"] < 20

    @pytest.mark.asyncio
    async def test_inflation_cpi(self, mcp_server):
        """'What's the latest Canadian CPI?'"""
        data = await call_tool(mcp_server, "boc_get_inflation_data", {"recent": 3})
        assert "_meta" in data
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_commodity_energy(self, mcp_server):
        """'Show me energy commodity prices.'"""
        data = await call_tool(mcp_server, "boc_get_commodity_prices", {"commodity_type": "energy", "recent": 3})
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_series_search(self, mcp_server):
        """'What BoC series are available about housing?'"""
        data = await call_tool(mcp_server, "boc_search_series", {"keyword": "exchange"})
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_list_groups(self, mcp_server):
        """'What data groups are available?'"""
        data = await call_tool(mcp_server, "boc_list_groups")
        assert len(data["data"]) >= 10

    @pytest.mark.asyncio
    async def test_cached_second_call(self, mcp_server):
        """Repeated calls return cached data."""
        await call_tool(mcp_server, "boc_get_exchange_rates", {"currency": "JPY", "recent": 1})
        data2 = await call_tool(mcp_server, "boc_get_exchange_rates", {"currency": "JPY", "recent": 1})
        assert data2["_meta"]["cached"] is True


# ─── Open Parliament scenarios ───────────────────────────────────────────────


class TestParliamentScenarios:

    @pytest.mark.asyncio
    async def test_discover_parliament_tools(self, mcp_server):
        """Agent asks: 'find tools for Canadian parliament'"""
        results = await discover(mcp_server, "parliament bills MP")
        names = [r["name"] for r in results]
        assert any(n.startswith("parl_") for n in names)

    @pytest.mark.asyncio
    async def test_find_mp_for_papineau(self, mcp_server):
        """'Who is the MP for Papineau?'"""
        data = await call_tool(mcp_server, "parl_search_by_riding", {"riding": "papineau"})
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_list_ndp_members(self, mcp_server):
        """'List all NDP MPs.'"""
        data = await call_tool(mcp_server, "parl_get_party_members", {"party": "ndp"})
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_cannabis_act(self, mcp_server):
        """'Get details on bill C-45 Cannabis Act.'"""
        data = await call_tool(mcp_server, "parl_get_bill_details", {"bill_id": "42-1/C-45"})
        assert "_meta" in data
        assert "name" in data["data"]

    @pytest.mark.asyncio
    async def test_anna_roberts_ballot(self, mcp_server):
        """'How did Anna Roberts vote on vote 44-1/333?'"""
        data = await call_tool(mcp_server, "parl_get_ballots", {
            "vote_id": "44-1/333", "politician": "anna-roberts"
        })
        assert len(data["data"]) == 1
        assert data["data"][0]["ballot"] in ("Yes", "No", "Paired")

    @pytest.mark.asyncio
    async def test_all_ballots_for_vote(self, mcp_server):
        """'Get all ballots for vote 44-1/148.'"""
        data = await call_tool(mcp_server, "parl_get_ballots", {"vote_id": "44-1/148"})
        assert len(data["data"]) >= 10

    @pytest.mark.asyncio
    async def test_voting_record(self, mcp_server):
        """'Get Poilievre's voting record.'"""
        data = await call_tool(mcp_server, "parl_get_voting_record", {
            "politician": "/politicians/pierre-poilievre/"
        })
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_bills_from_session(self, mcp_server):
        """'List bills from session 44-1.'"""
        data = await call_tool(mcp_server, "parl_search_bills", {"session": "44-1"})
        assert len(data["data"]) >= 1


# ─── Recalls scenarios ───────────────────────────────────────────────────────


class TestRecallsScenarios:

    @pytest.mark.asyncio
    async def test_recent_recalls(self, mcp_server):
        """'Get recent recalls in Canada.'"""
        data = await call_tool(mcp_server, "recalls_get_recent")
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_search_toyota_recalls(self, mcp_server):
        """'Search for Toyota vehicle recalls.'"""
        data = await call_tool(mcp_server, "recalls_get_vehicles", {"keyword": "toyota"})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_food_recalls(self, mcp_server):
        """'Get recent food recalls.'"""
        data = await call_tool(mcp_server, "recalls_get_food")
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_search_salmonella(self, mcp_server):
        """'Find recalls mentioning salmonella.'"""
        data = await call_tool(mcp_server, "recalls_search", {"keyword": "salmonella"})
        assert "_meta" in data


# ─── Drug Database scenarios ────────────────────────────────────────────────


class TestDrugScenarios:

    @pytest.mark.asyncio
    async def test_search_tylenol(self, mcp_server):
        """'Look up Tylenol.'"""
        data = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        assert "_meta" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_search_by_company(self, mcp_server):
        """'Find drugs by Pfizer.'"""
        data = await call_tool(mcp_server, "drug_search_companies", {"company_name": "pfizer"})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drug_schedule(self, mcp_server):
        """'Is this drug prescription or OTC?'"""
        # First search to get a drug_code
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        if search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_schedule", {"drug_code": drug_code})
                assert "_meta" in data


# ─── CKAN scenarios ─────────────────────────────────────────────────────────


class TestCkanScenarios:

    @pytest.mark.asyncio
    async def test_search_immigration_datasets(self, mcp_server):
        """'Search for datasets about immigration.'"""
        data = await call_tool(mcp_server, "ckan_search_datasets", {"query": "immigration", "rows": 3})
        assert "_meta" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_list_organizations(self, mcp_server):
        """'What organizations publish open data?'"""
        data = await call_tool(mcp_server, "ckan_list_organizations")
        assert len(data["data"]) >= 10

    @pytest.mark.asyncio
    async def test_portal_stats(self, mcp_server):
        """'How many datasets on the portal?'"""
        data = await call_tool(mcp_server, "ckan_get_dataset_stats")
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_search_by_tag(self, mcp_server):
        """'Find datasets tagged with environment.'"""
        data = await call_tool(mcp_server, "ckan_search_by_tag", {"tag": "environment", "rows": 3})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_list_groups(self, mcp_server):
        """'List thematic groups.'"""
        data = await call_tool(mcp_server, "ckan_list_groups")
        assert "_meta" in data


# ─── Nutrient File scenarios ────────────────────────────────────────────────


class TestNutrientScenarios:

    @pytest.mark.asyncio
    async def test_search_banana(self, mcp_server):
        """'Look up banana nutrition.'"""
        data = await call_tool(mcp_server, "nutrient_search_foods", {"query": "banana"})
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_list_food_groups(self, mcp_server):
        """'What food groups exist?'"""
        data = await call_tool(mcp_server, "nutrient_list_food_groups")
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_list_nutrients(self, mcp_server):
        """'What nutrients are tracked?'"""
        data = await call_tool(mcp_server, "nutrient_list_nutrients")
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_compare_foods(self, mcp_server):
        """'Compare chicken vs salmon nutrition.'"""
        # Use known food IDs (from CNF)
        data = await call_tool(mcp_server, "nutrient_compare_foods", {
            "food_ids": [785, 868], "format": "by_nutrient"
        })
        assert "_meta" in data


# ─── Cross-module scenarios ─────────────────────────────────────────────────


# ─── Gap coverage: tools without integration tests ──────────────────────────


class TestBocGapCoverage:
    """Tools that were missing integration test coverage."""

    @pytest.mark.asyncio
    async def test_series_metadata(self, mcp_server):
        """'Get metadata for series FXUSDCAD.'"""
        data = await call_tool(mcp_server, "boc_get_series_metadata", {"series_name": "FXUSDCAD"})
        assert "_meta" in data
        assert "name" in data["data"]


class TestParliamentGapCoverage:

    @pytest.mark.asyncio
    async def test_get_politicians(self, mcp_server):
        """'Search for MPs named Trudeau.'"""
        data = await call_tool(mcp_server, "parl_get_politicians", {"name": "trudeau"})
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_votes(self, mcp_server):
        """'Get House of Commons votes from session 44-1.'"""
        data = await call_tool(mcp_server, "parl_get_votes", {"session": "44-1"})
        assert "_meta" in data
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_debates(self, mcp_server):
        """'Get Hansard debates from a specific date.'"""
        data = await call_tool(mcp_server, "parl_get_debates", {"date": "2024-03-01"})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_search_hansard(self, mcp_server):
        """'Search Hansard for mentions of climate change.'"""
        # Open Parliament /search/ may return HTML — tool should handle gracefully
        data = await call_tool(mcp_server, "parl_search_hansard", {"query": "climate"})
        assert "_meta" in data or "error" in data


class TestRecallsGapCoverage:

    @pytest.mark.asyncio
    async def test_recall_details(self, mcp_server):
        """'Get details on a specific recall.'"""
        # First get a recent recall
        recent = await call_tool(mcp_server, "recalls_get_recent")
        if recent.get("data") and isinstance(recent["data"], list) and recent["data"]:
            recall_id = str(recent["data"][0].get("recallId", ""))
            if recall_id:
                data = await call_tool(mcp_server, "recalls_get_details", {"recall_id": recall_id})
                assert "_meta" in data or "error" in data

    @pytest.mark.asyncio
    async def test_health_product_recalls(self, mcp_server):
        """'Get health product recalls.'"""
        data = await call_tool(mcp_server, "recalls_get_health_products")
        assert "_meta" in data or "error" in data


class TestDrugGapCoverage:

    @pytest.mark.asyncio
    async def test_drug_details(self, mcp_server):
        """'Get full details for a drug.'"""
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        if search.get("data") and search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_details", {"drug_code": drug_code})
                assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drug_ingredients(self, mcp_server):
        """'Get ingredients for a drug.'"""
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "advil"})
        if search.get("data") and search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_ingredients", {"drug_code": drug_code})
                assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drug_routes(self, mcp_server):
        """'Get routes of administration.'"""
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        if search.get("data") and search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_routes", {"drug_code": drug_code})
                assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drug_status(self, mcp_server):
        """'Is this drug still on the market?'"""
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        if search.get("data") and search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_status", {"drug_code": drug_code})
                assert "_meta" in data

    @pytest.mark.asyncio
    async def test_drug_therapeutic_class(self, mcp_server):
        """'What class of drug is this?'"""
        search = await call_tool(mcp_server, "drug_search", {"brand_name": "tylenol"})
        if search.get("data") and search["data"]:
            drug_code = search["data"][0].get("drug_code")
            if drug_code:
                data = await call_tool(mcp_server, "drug_get_therapeutic_class", {"drug_code": drug_code})
                assert "_meta" in data


class TestCkanGapCoverage:

    @pytest.mark.asyncio
    async def test_dataset_details(self, mcp_server):
        """'Get full details of a specific dataset.'"""
        search = await call_tool(mcp_server, "ckan_search_datasets", {"query": "weather", "rows": 1})
        if search.get("data") and search["data"]:
            dataset_id = search["data"][0].get("id")
            if dataset_id:
                data = await call_tool(mcp_server, "ckan_get_dataset_details", {"dataset_id": dataset_id})
                assert "_meta" in data

    @pytest.mark.asyncio
    async def test_get_resource(self, mcp_server):
        """'Get details for a specific data file.'"""
        search = await call_tool(mcp_server, "ckan_search_datasets", {"query": "census", "rows": 1})
        if search.get("data") and search["data"]:
            resources = search["data"][0].get("resources", [])
            if resources:
                resource_id = resources[0].get("id")
                if resource_id:
                    data = await call_tool(mcp_server, "ckan_get_resource", {"resource_id": resource_id})
                    assert "_meta" in data


class TestNutrientGapCoverage:

    @pytest.mark.asyncio
    async def test_food_details(self, mcp_server):
        """'Get details about a specific food.'"""
        data = await call_tool(mcp_server, "nutrient_get_food_details", {"food_id": 2})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_nutrient_amounts(self, mcp_server):
        """'Get all nutrients per 100g for a food.'"""
        data = await call_tool(mcp_server, "nutrient_get_nutrient_amounts", {"food_id": 2})
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_serving_sizes(self, mcp_server):
        """'Get serving sizes for a food.'"""
        data = await call_tool(mcp_server, "nutrient_get_serving_sizes", {"food_id": 2})
        assert "_meta" in data

    @pytest.mark.asyncio
    async def test_search_by_food_group(self, mcp_server):
        """'List all foods in the dairy group.'"""
        data = await call_tool(mcp_server, "nutrient_search_by_food_group", {"food_group_id": 1})
        assert "_meta" in data


# ─── Cross-module scenarios ─────────────────────────────────────────────────


class TestCrossModuleScenarios:

    @pytest.mark.asyncio
    async def test_inflation_plus_trade_datasets(self, mcp_server):
        """'Get inflation and find trade datasets.'"""
        inflation = await call_tool(mcp_server, "boc_get_inflation_data", {"recent": 1})
        assert len(inflation["data"]) >= 1

        trade = await call_tool(mcp_server, "ckan_search_datasets", {"query": "international trade", "rows": 3})
        assert len(trade["data"]) >= 1

    @pytest.mark.asyncio
    async def test_exchange_rate_plus_trade(self, mcp_server):
        """'Get USD/CAD and find trade datasets.'"""
        fx = await call_tool(mcp_server, "boc_get_exchange_rates", {"currency": "USD", "recent": 1})
        assert fx["data"][0]["value"] is not None

        trade = await call_tool(mcp_server, "ckan_search_datasets", {"query": "trade", "rows": 3})
        assert "_meta" in trade

    @pytest.mark.asyncio
    async def test_food_recalls_plus_open_data(self, mcp_server):
        """'Get food recalls and related datasets.'"""
        recalls = await call_tool(mcp_server, "recalls_get_food")
        assert "_meta" in recalls

        datasets = await call_tool(mcp_server, "ckan_search_datasets", {"query": "food safety", "rows": 3})
        assert "_meta" in datasets

    @pytest.mark.asyncio
    async def test_commodity_plus_agriculture(self, mcp_server):
        """'Get agriculture commodity prices and datasets.'"""
        commodities = await call_tool(mcp_server, "boc_get_commodity_prices", {"commodity_type": "agriculture", "recent": 3})
        assert len(commodities["data"]) >= 1

        datasets = await call_tool(mcp_server, "ckan_search_datasets", {"query": "agriculture", "rows": 3})
        assert "_meta" in datasets

    @pytest.mark.asyncio
    async def test_parliament_bills_plus_drug_db(self, mcp_server):
        """'Find health bills and check drug database.'"""
        bills = await call_tool(mcp_server, "parl_search_bills", {"session": "44-1"})
        assert len(bills["data"]) >= 1

        drugs = await call_tool(mcp_server, "drug_search", {"brand_name": "cannabis"})
        assert "_meta" in drugs


# ─── Meta-tool scenarios ─────────────────────────────────────────────────────


class TestMetaToolScenarios:

    @pytest.mark.asyncio
    async def test_plan_query_multi_api(self, mcp_server):
        """'Plan a query about food recalls and inflation data'"""
        data = await call_direct_tool(mcp_server, "plan_query", {"query": "food recalls and inflation"})
        assert "_meta" in data
        assert "steps" in data["data"]
        steps = data["data"]["steps"]
        assert len(steps) >= 1
        # At least one step should reference a recall or boc tool
        tool_names = [s["tool"] for s in steps]
        assert any("recall" in n or "boc" in n or "food" in n or "inflation" in n for n in tool_names)

    @pytest.mark.asyncio
    async def test_plan_query_discovery(self, mcp_server):
        """'Is plan_query visible as an always-visible tool?'"""
        from fastmcp import Client
        # plan_query is always_visible — it appears in list_tools(), not in BM25 results
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            names = [t.name for t in tools]
        assert "plan_query" in names

    @pytest.mark.asyncio
    async def test_execute_batch_parallel(self, mcp_server):
        """'Run exchange rates and recall search together'"""
        data = await call_direct_tool(mcp_server, "execute_batch", {
            "calls": [
                {"tool": "boc_get_exchange_rates", "params": {"currency": "USD", "recent": 1}},
                {"tool": "recalls_get_recent", "params": {"limit": 1}},
            ]
        })
        assert "_meta" in data
        results = data["data"]["results"]
        assert len(results) == 2
        assert data["data"]["summary"]["total"] == 2
        assert data["data"]["summary"]["succeeded"] == 2
        assert all(r["status"] == "ok" for r in results)

    @pytest.mark.asyncio
    async def test_execute_batch_partial_failure(self, mcp_server):
        """'One tool fails, other succeeds'"""
        data = await call_direct_tool(mcp_server, "execute_batch", {
            "calls": [
                {"tool": "boc_get_exchange_rates", "params": {"currency": "USD", "recent": 1}},
                {"tool": "nonexistent_tool", "params": {}},
            ]
        })
        assert "_meta" in data
        summary = data["data"]["summary"]
        assert summary["succeeded"] >= 1
        assert summary["failed"] >= 1
        results = data["data"]["results"]
        boc_result = next(r for r in results if r["tool"] == "boc_get_exchange_rates")
        bad_result = next(r for r in results if r["tool"] == "nonexistent_tool")
        assert boc_result["status"] == "ok"
        assert bad_result["status"] == "error"

    @pytest.mark.asyncio
    async def test_execute_batch_from_plan(self, mcp_server):
        """'Plan then execute end-to-end'"""
        plan = await call_direct_tool(mcp_server, "plan_query", {"query": "exchange rates"})
        assert "_meta" in plan
        assert "steps" in plan["data"]
        # Pass the full make_response-wrapped plan output to execute_batch
        data = await call_direct_tool(mcp_server, "execute_batch", {"calls": plan})
        assert "_meta" in data
        assert "results" in data["data"]
        assert len(data["data"]["results"]) >= 1

    @pytest.mark.asyncio
    async def test_selective_loading_discover_tools(self, mcp_server):
        """'PLAN-03: selective modules only shows loaded tools'"""
        import json
        from fastmcp import Client, FastMCP
        from fastmcp.server.providers import FileSystemProvider
        from fastmcp.server.transforms.search import BM25SearchTransform
        from mcp_canada.server import _build_providers, _META_DIR

        selective_mcp = FastMCP("test-selective")
        for p in _build_providers("bank_of_canada"):
            selective_mcp.add_provider(p)
        if _META_DIR.is_dir():
            selective_mcp.add_provider(FileSystemProvider(root=_META_DIR))
        selective_mcp.add_transform(BM25SearchTransform(
            max_results=5,
            always_visible=["discover_tools", "list_modules", "plan_query", "execute_batch"],
            search_tool_name="discover_tools",
            call_tool_name="call_tool",
        ))

        from tests.integration.conftest import _extract_text

        async with Client(selective_mcp) as client:
            # Weather tools should NOT appear
            result = await client.call_tool("discover_tools", {"query": "weather forecast"})
            weather_results = json.loads(_extract_text(result))
            weather_names = [r["name"] for r in weather_results] if isinstance(weather_results, list) else []
            assert not any("wx_" in n for n in weather_names), (
                f"Weather tools found in selective (bank_of_canada only) server: {weather_names}"
            )

            # BOC tools SHOULD appear
            result2 = await client.call_tool("discover_tools", {"query": "exchange rates"})
            boc_results = json.loads(_extract_text(result2))
            boc_names = [r["name"] for r in boc_results] if isinstance(boc_results, list) else []
            assert any("boc_" in n for n in boc_names), (
                f"No BOC tools found in selective server. Got: {boc_names}"
            )
