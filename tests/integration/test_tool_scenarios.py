"""Integration tests calling tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_tool_scenarios.py -v -m integration --timeout=120
"""

import aiosqlite
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


# ─── Toronto scenarios ───────────────────────────────────────────────────────


class TestTorontoToolScenarios:

    @pytest.mark.asyncio
    async def test_toronto_discovery(self, mcp_server):
        """'What Toronto datasets are about cycling?'"""
        results = await discover(mcp_server, "Toronto cycling datasets open data")
        names = [r["name"] for r in results]
        assert any(n.startswith("toronto_") for n in names)

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_toronto_dataset_details(self, mcp_server):
        """'Tell me about the TTC routes dataset.'"""
        data = await call_tool(mcp_server, "toronto_get_dataset_details", {
            "dataset_id": "ttc-routes-and-schedules"
        })
        assert "_meta" in data
        assert "data" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_toronto_ttc_stops(self, mcp_server):
        """'Where are the subway stops?'"""
        data = await call_tool(mcp_server, "toronto_get_ttc_stops", {"query": "station"})
        assert "_meta" in data
        assert isinstance(data.get("data", []), list)

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_toronto_ttc_routes(self, mcp_server):
        """'What TTC routes exist?'"""
        data = await call_tool(mcp_server, "toronto_get_ttc_routes")
        assert "_meta" in data
        assert isinstance(data.get("data", []), list)

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_toronto_neighbourhood_profile(self, mcp_server):
        """'What\'s the population of Rosedale?'"""
        data = await call_tool(mcp_server, "toronto_get_neighbourhood_profile", {
            "neighbourhood": "Rosedale",
            "limit": 10
        })
        assert "_meta" in data
        assert "data" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_toronto_rentsafe(self, mcp_server):
        """'Show me apartment buildings in Ward 10.'"""
        data = await call_tool(mcp_server, "toronto_get_rentsafe_evaluations", {
            "ward": "10",
            "limit": 5
        })
        assert "_meta" in data
        assert "data" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_toronto_short_term_rentals(self, mcp_server):
        """'List active Airbnb registrations.'"""
        data = await call_tool(mcp_server, "toronto_get_short_term_rentals", {
            "status": "registered",
            "limit": 5
        })
        assert "_meta" in data
        assert "data" in data

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_toronto_compare_neighbourhoods(self, mcp_server):
        """'Compare median household income across Toronto neighbourhoods.'"""
        data = await call_tool(mcp_server, "toronto_compare_neighbourhoods", {
            "characteristic": "Median household income",
            "limit": 20
        })
        assert "_meta" in data
        assert "data" in data

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


# ─── Datastore scenarios ──────────────────────────────────────────────────────


# ─── Statistics Canada WDS scenarios ─────────────────────────────────────────


class TestStatcanWdsScenarios:
    """StatCan WDS integration tests through the MCP Client layer.

    Tests assert on envelope shape, not specific values (data changes daily).
    All tests marked @pytest.mark.integration — live API required.
    """

    @pytest.mark.asyncio
    async def test_discover_statcan_tools_tables(self, mcp_server):
        """'Find tools for statistics canada tables'"""
        results = await discover(mcp_server, "statistics canada tables")
        names = [r["name"] for r in results]
        assert any(n.startswith("sc_") for n in names), (
            f"No sc_ tools found for 'statistics canada tables'. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_discover_statcan_tools_time_series(self, mcp_server):
        """'Find tools for statcan time series data'"""
        results = await discover(mcp_server, "statcan time series data")
        names = [r["name"] for r in results]
        assert any(n.startswith("sc_") for n in names), (
            f"No sc_ tools found for 'statcan time series data'. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_search_cubes_consumer_price_index(self, mcp_server):
        """'Search for Statistics Canada tables about consumer price index'"""
        data = await call_tool(mcp_server, "sc_search_cubes", {"query": "consumer price index"})
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-wds"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_cube_metadata_cpi_table(self, mcp_server):
        """'Get dimensions for the CPI table (18100004)'"""
        data = await call_tool(mcp_server, "sc_get_cube_metadata", {"product_id": 18100004})
        assert "_meta" in data
        assert "product_id" in data["data"]
        assert data["data"]["product_id"] == 18100004
        assert "dimensions" in data["data"]
        assert isinstance(data["data"]["dimensions"], list)

    @pytest.mark.asyncio
    async def test_get_code_sets(self, mcp_server):
        """'Get all WDS code set references'"""
        data = await call_tool(mcp_server, "sc_get_code_sets")
        assert "_meta" in data
        assert "frequency" in data["data"]
        assert "scalar" in data["data"]
        assert isinstance(data["data"]["frequency"], list)
        assert len(data["data"]["frequency"]) >= 1

    @pytest.mark.asyncio
    async def test_get_series_info_by_vector(self, mcp_server):
        """'Get series info for vector 41690973 (CPI Canada all-items)'"""
        data = await call_tool(mcp_server, "sc_get_series_info_by_vector", {"vector_id": 41690973})
        assert "_meta" in data
        assert "product_id" in data["data"]
        assert "vector_id" in data["data"]
        assert "frequency" in data["data"]

    @pytest.mark.asyncio
    async def test_get_data_by_vector(self, mcp_server):
        """'Get the latest 3 observations for CPI all-items vector'"""
        data = await call_tool(mcp_server, "sc_get_data_by_vector", {"vector_id": 41690973, "n": 3})
        assert "_meta" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        row = data["data"][0]
        assert "ref_per" in row
        assert "value" in row

    @pytest.mark.asyncio
    async def test_get_changed_cubes_today(self, mcp_server):
        """'What tables changed today?'"""
        import datetime
        today = datetime.date.today().isoformat()
        data = await call_tool(mcp_server, "sc_get_changed_cubes", {"date": today})
        # Shape assertion only — may be empty list before 08:30 EST
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_changed_series(self, mcp_server):
        """'Which series changed today?'"""
        data = await call_tool(mcp_server, "sc_get_changed_series")
        # Shape assertion only — may be empty list before 08:30 EST
        assert "_meta" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_error_handling_invalid_product_id(self, mcp_server):
        """'Get metadata for a nonexistent table ID'"""
        data = await call_tool(mcp_server, "sc_get_cube_metadata", {"product_id": 999999999})
        # Should return structured error, not raise exception
        assert "error" in data or "_meta" in data
        if "error" in data:
            assert "code" in data["error"]
            assert data["error"]["code"] in ("UPSTREAM_ERROR", "UPSTREAM_UNAVAILABLE")

    @pytest.mark.asyncio
    async def test_get_series_info_by_coord(self, mcp_server):
        """'Get series info for CPI Canada all-items by product and coordinate'"""
        data = await call_tool(mcp_server, "sc_get_series_info_by_coord", {
            "product_id": 18100004,
            "coordinate": "1.1.0.0.0.0.0.0.0.0",
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-wds"
        assert "product_id" in data["data"]
        assert "vector_id" in data["data"]
        assert "frequency" in data["data"]

    @pytest.mark.asyncio
    async def test_get_data_by_coord(self, mcp_server):
        """'Get the latest 3 observations for CPI Canada all-items by coordinate'"""
        data = await call_tool(mcp_server, "sc_get_data_by_coord", {
            "product_id": 18100004,
            "coordinate": "1.1.0.0.0.0.0.0.0.0",
            "n": 3,
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-wds"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        row = data["data"][0]
        assert "ref_per" in row
        assert "value" in row

    @pytest.mark.asyncio
    async def test_get_data_by_date_range(self, mcp_server):
        """'Get CPI all-items vector observations from Q1 2024'"""
        data = await call_tool(mcp_server, "sc_get_data_by_date_range", {
            "vector_id": 41690973,
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-wds"
        assert isinstance(data["data"], list)
        # Accept empty list if no data for range; just verify shape
        for row in data["data"]:
            assert "ref_per" in row
            assert "value" in row

    @pytest.mark.asyncio
    async def test_get_bulk_vector_data(self, mcp_server):
        """'Get the most recent releases for multiple StatCan vectors in bulk'"""
        data = await call_tool(mcp_server, "sc_get_bulk_vector_data", {
            "vector_ids": [41690973, 74804],
            "start_release": "2024-01-01",
            "end_release": "2024-03-31",
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-wds"
        assert isinstance(data["data"], list)
        # May be empty if no releases in range — assert shape only
        for row in data["data"]:
            assert "vector_id" in row
            assert "ref_per" in row
            assert "value" in row


# ─── SDMX scenarios ───────────────────────────────────────────────────────────


class TestSdmxScenarios:
    """SDMX integration tests through the MCP Client layer.

    Tests assert on envelope shape, not specific values (data changes daily).
    test_fetch_vectors_to_store uses an in-memory DB to avoid persisting data.
    All tests marked @pytest.mark.integration — live API required.
    """

    @pytest.fixture(autouse=False)
    async def in_memory_db(self):
        """Patch datastore client._db with in-memory connection for store tests."""
        from mcp_canada.modules.datastore import client as datastore_client

        conn = await aiosqlite.connect(":memory:")
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")

        original = datastore_client._db
        datastore_client._db = conn
        yield conn
        datastore_client._db = original
        await conn.close()

    @pytest.mark.asyncio
    async def test_sdmx_structure_for_cpi_table(self, mcp_server):
        """'Get the SDMX dimension codelists for the CPI table (18100004)'"""
        data = await call_tool(mcp_server, "sc_get_sdmx_structure", {"product_id": 18100004})
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-sdmx"
        assert "dimensions" in data["data"]
        assert isinstance(data["data"]["dimensions"], list)
        assert len(data["data"]["dimensions"]) >= 1
        assert "suggested_key" in data["data"]
        assert isinstance(data["data"]["suggested_key"], str)
        assert len(data["data"]["suggested_key"]) > 0
        # Each dimension must have position, id, codes
        for dim in data["data"]["dimensions"]:
            assert "position" in dim
            assert "id" in dim
            assert "codes" in dim
            assert isinstance(dim["codes"], list)

    @pytest.mark.asyncio
    async def test_sdmx_data_last_n(self, mcp_server):
        """'Get the 5 most recent CPI observations for Canada all-items via SDMX'"""
        data = await call_tool(mcp_server, "sc_get_sdmx_data", {
            "product_id": 18100004,
            "key": "1.1",
            "last_n": 5,
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-sdmx"
        assert isinstance(data["data"], list)
        # Each observation must have period, value, dimensions
        for obs in data["data"]:
            assert "period" in obs
            assert "value" in obs
            assert "dimensions" in obs

    @pytest.mark.asyncio
    async def test_sdmx_data_mutual_exclusion(self, mcp_server):
        """'Get CPI data with both last_n and start_period — should error'"""
        data = await call_tool(mcp_server, "sc_get_sdmx_data", {
            "product_id": 18100004,
            "key": "1.1",
            "last_n": 5,
            "start_period": "2024-01",
        })
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_sdmx_vector_data(self, mcp_server):
        """'Get CPI all-items vector observations via SDMX for 2023'"""
        data = await call_tool(mcp_server, "sc_get_sdmx_vector_data", {
            "vector_id": 41690973,
            "start_period": "2023-01",
            "end_period": "2023-12",
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "statcan-sdmx"
        assert isinstance(data["data"], list)
        # Accept empty list if no data in range — just assert shape
        for obs in data["data"]:
            assert "period" in obs
            assert "value" in obs

    @pytest.mark.asyncio
    async def test_discover_sdmx_tools(self, mcp_server):
        """'Find tools for SDMX structure codelist server filter'"""
        results = await discover(mcp_server, "SDMX structure codelist server filter")
        names = [r["name"] for r in results]
        sdmx_tools = [n for n in names if "sdmx" in n.lower()]
        assert len(sdmx_tools) >= 1, (
            f"No SDMX tools found for 'SDMX structure codelist server filter'. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_fetch_vectors_to_store(self, mcp_server, in_memory_db):
        """'Fetch CPI vectors and store them to the datastore for SQL queries'"""
        result = await call_tool(mcp_server, "sc_fetch_vectors_to_store", {
            "vector_ids": [41690973, 74804],
            "start_release": "2024-01-01",
            "end_release": "2024-03-31",
            "table_name": "test_sdmx_integration",
        })
        assert "_meta" in result
        assert result["data"]["stored"] > 0
        assert result["data"]["table"] == "test_sdmx_integration"
        assert isinstance(result["data"]["vectors"], list)

        # Verify data is queryable via ds_query
        query_result = await call_tool(mcp_server, "ds_query", {
            "sql": "SELECT COUNT(*) as cnt FROM test_sdmx_integration"
        })
        assert "_meta" in query_result
        assert query_result["data"]["row_count"] >= 1
        row = query_result["data"]["rows"][0]
        assert row["cnt"] > 0


# ─── Datastore scenarios ──────────────────────────────────────────────────────


class TestDatastoreScenarios:
    """Datastore integration tests through the MCP Client layer.

    Each test patches client._db with an in-memory aiosqlite connection to
    avoid touching the real ~/.mcp-canada/datastore.db file.
    """

    @pytest.fixture(autouse=True)
    async def in_memory_db(self):
        """Patch datastore client._db with an in-memory connection for each test."""
        from mcp_canada.modules.datastore import client as datastore_client

        conn = await aiosqlite.connect(":memory:")
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")

        original = datastore_client._db
        datastore_client._db = conn
        yield conn
        datastore_client._db = original
        await conn.close()

    @pytest.mark.asyncio
    async def test_create_table_and_query(self, mcp_server):
        """'Create a table called test_prices with columns date TEXT and price REAL, then query it.'"""
        result = await call_tool(mcp_server, "ds_create_table", {
            "table_name": "test_prices",
            "columns": [{"name": "date", "type": "TEXT"}, {"name": "price", "type": "REAL"}],
        })
        assert "_meta" in result
        assert result["data"]["table"] == "test_prices"
        assert result["data"]["columns"] == 2

        query_result = await call_tool(mcp_server, "ds_query", {"sql": "SELECT * FROM test_prices"})
        assert "_meta" in query_result
        assert query_result["data"]["row_count"] == 0
        assert query_result["data"]["truncated"] is False

    @pytest.mark.asyncio
    async def test_insert_and_retrieve(self, mcp_server):
        """'Store some exchange rates and get them back.'"""
        await call_tool(mcp_server, "ds_create_table", {
            "table_name": "exchange_rates",
            "columns": [{"name": "date", "type": "TEXT"}, {"name": "rate", "type": "REAL"}],
        })

        insert_result = await call_tool(mcp_server, "ds_insert_data", {
            "table_name": "exchange_rates",
            "rows": [
                {"date": "2026-04-01", "rate": 1.38},
                {"date": "2026-04-02", "rate": 1.39},
                {"date": "2026-04-03", "rate": 1.37},
            ],
        })
        assert insert_result["data"]["inserted"] == 3

        query_result = await call_tool(mcp_server, "ds_query", {"sql": "SELECT * FROM exchange_rates"})
        assert query_result["data"]["row_count"] == 3
        assert len(query_result["data"]["rows"]) == 3

    @pytest.mark.asyncio
    async def test_list_and_schema(self, mcp_server):
        """'What tables are in the datastore and what is their structure?'"""
        await call_tool(mcp_server, "ds_create_table", {
            "table_name": "rates_a",
            "columns": [{"name": "date", "type": "TEXT"}, {"name": "value", "type": "REAL"}],
        })
        await call_tool(mcp_server, "ds_create_table", {
            "table_name": "rates_b",
            "columns": [{"name": "id", "type": "INTEGER"}],
        })

        list_result = await call_tool(mcp_server, "ds_list_tables")
        assert "_meta" in list_result
        assert "rates_a" in list_result["data"]["tables"]
        assert "rates_b" in list_result["data"]["tables"]

        schema_result = await call_tool(mcp_server, "ds_get_schema", {"table_name": "rates_a"})
        assert "_meta" in schema_result
        col_names = [c["name"] for c in schema_result["data"]["columns"]]
        assert "date" in col_names
        assert "value" in col_names

    @pytest.mark.asyncio
    async def test_drop_table(self, mcp_server):
        """'Delete the test_prices table.'"""
        await call_tool(mcp_server, "ds_create_table", {
            "table_name": "to_drop",
            "columns": [{"name": "id", "type": "INTEGER"}],
        })

        drop_result = await call_tool(mcp_server, "ds_drop_table", {"table_name": "to_drop"})
        assert "_meta" in drop_result
        assert drop_result["data"]["dropped"] == "to_drop"

        list_result = await call_tool(mcp_server, "ds_list_tables")
        assert "to_drop" not in list_result["data"]["tables"]

    @pytest.mark.asyncio
    async def test_discover_datastore_tools(self, mcp_server):
        """'I need to store some data.'"""
        results = await discover(mcp_server, "store data sqlite table")
        names = [r["name"] for r in results]
        assert any(n.startswith("ds_") for n in names), (
            f"No datastore tools found for 'store data sqlite table'. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_invalid_table_name(self, mcp_server):
        """'Create a table called drop;--' (SQL injection attempt)."""
        result = await call_tool(mcp_server, "ds_create_table", {
            "table_name": "drop;--",
            "columns": [{"name": "id", "type": "INTEGER"}],
        })
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


# ─── IRCC Immigration scenarios ──────────────────────────────────────────────


class TestIrccScenarios:

    @pytest.mark.asyncio
    async def test_ircc_permanent_residents_by_country(self, mcp_server):
        """'How many permanent residents came from India in 2023?'"""
        result = await call_tool(
            mcp_server,
            "ircc_get_permanent_residents",
            {"breakdown": "country", "year": 2023},
        )
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "IRCC Open Data"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_ircc_study_permits(self, mcp_server):
        """'How many study permits were issued by country?'"""
        result = await call_tool(
            mcp_server,
            "ircc_get_study_permits",
            {"breakdown": "country"},
        )
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "IRCC Open Data"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_ircc_discover_tools(self, mcp_server):
        """'Find tools about Canadian immigration'"""
        results = await discover(mcp_server, "immigration permanent residents Canada IRCC")
        names = [r["name"] for r in results]
        assert any(n.startswith("ircc_") for n in names), (
            f"No ircc_ tools found for immigration query. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_ircc_invalid_breakdown(self, mcp_server):
        """'What happens with a bad breakdown?'"""
        result = await call_tool(
            mcp_server,
            "ircc_get_permanent_residents",
            {"breakdown": "nonexistent"},
        )
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_ircc_list_datasets(self, mcp_server):
        """'What IRCC datasets are available?'"""
        result = await call_tool(mcp_server, "ircc_list_datasets", {})
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 10

    @pytest.mark.asyncio
    async def test_store_pr_data_to_datastore(self, mcp_server):
        """Cross-module: fetch PR data then store to datastore and query it."""
        pr_result = await call_tool(
            mcp_server,
            "ircc_get_permanent_residents",
            {"breakdown": "country", "year": 2023},
        )
        assert "_meta" in pr_result
        rows = pr_result["data"]
        assert isinstance(rows, list)

        # Create table and insert rows (use a subset to keep test fast)
        sample_rows = rows[:3] if len(rows) >= 3 else rows
        if not sample_rows:
            pytest.skip("No PR data returned for year 2023 — skip cross-module test")

        # Derive columns from the first row keys
        first_row = sample_rows[0]
        columns = [{"name": str(k), "type": "TEXT"} for k in first_row.keys()]

        create_result = await call_tool(mcp_server, "ds_create_table", {
            "table_name": "ircc_pr_test",
            "columns": columns,
        })
        assert "_meta" in create_result

        insert_result = await call_tool(mcp_server, "ds_insert_data", {
            "table_name": "ircc_pr_test",
            "rows": sample_rows,
        })
        assert "_meta" in insert_result

        query_result = await call_tool(mcp_server, "ds_query", {
            "sql": "SELECT * FROM ircc_pr_test",
        })
        assert "_meta" in query_result
        assert query_result["data"]["row_count"] >= 1

        # Cleanup
        await call_tool(mcp_server, "ds_drop_table", {"table_name": "ircc_pr_test"})


# ─── Ontario Government Open Data scenarios ───────────────────────────────────


class TestOntarioToolScenarios:
    """Ontario Open Data integration tests through the MCP Client layer.

    Tests assert on response shape, not specific values (data changes daily).
    All tests marked @pytest.mark.integration — live API required.
    """

    @pytest.mark.asyncio
    async def test_ontario_search_population(self, mcp_server):
        """'What Ontario datasets exist about population?'"""
        data = await call_tool(mcp_server, "ontario_search_datasets", {
            "query": "population",
            "rows": 3,
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "Ontario Data Catalogue"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_ontario_dataset_details(self, mcp_server):
        """'Show me details of a specific Ontario dataset'"""
        data = await call_tool(mcp_server, "ontario_get_dataset_details", {
            "dataset_id": "population-projections",
        })
        assert "_meta" in data
        assert "id" in data["data"]
        assert "title" in data["data"]

    @pytest.mark.asyncio
    async def test_ontario_list_organizations(self, mcp_server):
        """'What Ontario ministries publish data?'"""
        data = await call_tool(mcp_server, "ontario_list_organizations")
        assert "_meta" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    @pytest.mark.asyncio
    async def test_ontario_portal_stats(self, mcp_server):
        """'How many datasets does Ontario have?'"""
        data = await call_tool(mcp_server, "ontario_get_dataset_stats")
        assert "_meta" in data
        assert "total_datasets" in data["data"]
        assert isinstance(data["data"]["total_datasets"], int)

    @pytest.mark.asyncio
    async def test_ontario_discovery(self, mcp_server):
        """discover_tools with query 'Ontario provincial data' finds at least one ontario_ tool."""
        results = await discover(mcp_server, "Ontario provincial data")
        names = [r["name"] for r in results]
        assert any(n.startswith("ontario_") for n in names), (
            f"No ontario_ tools found for 'Ontario provincial data'. Got: {names}"
        )

    @pytest.mark.asyncio
    async def test_ontario_search_error_handling(self, mcp_server):
        """'Get details for a nonexistent Ontario dataset'"""
        data = await call_tool(mcp_server, "ontario_get_dataset_details", {
            "dataset_id": "nonexistent-dataset-zzz-abc-123",
        })
        assert "error" in data
        assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR")


# ─── York Region Municipal Open Data scenarios ────────────────────────────────


class TestYorkRegionToolScenarios:
    """York Region ArcGIS Hub integration tests through the MCP Client layer.

    Tests assert on response shape only — live ArcGIS Hub APIs required.
    All tests marked @pytest.mark.integration. Use timeout=90s for feature queries.
    """

    @pytest.mark.asyncio
    async def test_york_region_search_transit(self, mcp_server):
        """'What York Region datasets are about transit?'"""
        data = await call_tool(mcp_server, "york_region_search_datasets", {
            "query": "transit",
            "limit": 5,
        })
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "arcgis-hub"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_york_region_transit_stops_live(self, mcp_server):
        """'Where are the YRT bus stops near Finch?'"""
        data = await call_tool(mcp_server, "york_region_get_transit_stops", {
            "query": "Finch",
        })
        assert "_meta" in data
        # Response has features list (may be empty on API error but structure must be present)
        assert "data" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_york_region_hospitals(self, mcp_server):
        """'Where are York Region hospitals?'"""
        data = await call_tool(mcp_server, "york_region_get_public_health", {
            "location_type": "hospital",
        })
        assert "_meta" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_markham_search_addresses(self, mcp_server):
        """'Find Main Street addresses in Markham'"""
        data = await call_tool(mcp_server, "markham_get_addresses", {
            "street": "Main",
        })
        assert "_meta" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_aurora_list_categories_live(self, mcp_server):
        """'What dataset categories exist in Aurora open data?'"""
        data = await call_tool(mcp_server, "aurora_list_categories")
        assert "_meta" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_newmarket_search_datasets_live(self, mcp_server):
        """'Search Newmarket open data for any datasets'"""
        data = await call_tool(mcp_server, "newmarket_search_datasets", {
            "query": "",
            "limit": 5,
        })
        assert "_meta" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_no_vaughan_tools_in_catalog(self, mcp_server):
        """Municipalities without portals (vaughan, richmond_hill, etc.) have no registered tools."""
        from fastmcp import Client
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        no_portal_prefixes = [
            "vaughan_", "richmond_hill_", "king_", "east_gwillimbury_", "georgina_"
        ]
        for prefix in no_portal_prefixes:
            matching = [n for n in tool_names if n.startswith(prefix)]
            assert matching == [], (
                f"Unexpected tools found for portal-less municipality '{prefix}': {matching}"
            )

    @pytest.mark.asyncio
    async def test_discovery_finds_york_region_tool(self, mcp_server):
        """BM25 discovery with 'york region transit bus stops' finds york_region_get_transit_stops."""
        results = await discover(mcp_server, "york region transit bus stops")
        names = [r["name"] for r in results]
        assert any(
            n in names for n in ("york_region_get_transit_stops", "york_region_search_datasets")
        ), f"No york_region transit tool found in BM25 results: {names}"


# ─── British Columbia scenarios ───────────────────────────────────────────────


@pytest.mark.asyncio
class TestBcToolScenarios:
    """BC open data tool integration scenarios — live BCDC CKAN + BCGW WFS endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_search_finds_wildfire_data(self, mcp_server):
        """'Search BC open data for wildfire datasets'"""
        data = await call_tool(mcp_server, "bc_search_datasets", {
            "q": "wildfire",
            "rows": 5,
        })
        assert "_meta" in data or "error" in data
        if "data" in data:
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1
            titles = [d.get("title", "").lower() for d in data["data"]]
            assert any("wildfire" in t or "fire" in t for t in titles), (
                f"No wildfire-related dataset found: {titles}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_active_fires_returns_meta(self, mcp_server):
        """'Show me current active wildfires in BC'"""
        data = await call_tool(mcp_server, "bc_get_active_fires", {
            "max_records": 5,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "bc-wfs"
            assert "data" in data
            # data is {"features": [...], "truncated": bool}
            assert isinstance(data["data"], dict)
            assert "features" in data["data"]
            assert isinstance(data["data"]["features"], list)
            assert "truncated" in data["data"]

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_fire_perimeters_by_year(self, mcp_server):
        """'Get historical fire perimeters for 2023 in BC'"""
        data = await call_tool(mcp_server, "bc_get_fire_perimeters", {
            "year": 2023,
            "max_records": 10,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "bc-wfs"
            # data is {"features": [...], "truncated": bool}
            assert isinstance(data["data"], dict)
            assert "features" in data["data"]
            features = data["data"]["features"]
            assert len(features) >= 1 or data["data"].get("truncated") is True

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_protected_areas_returns_parks(self, mcp_server):
        """'List provincial parks in BC'"""
        data = await call_tool(mcp_server, "bc_get_protected_areas", {
            "designation": "PROVINCIAL PARK",
            "max_records": 10,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "bc-wfs"
            # data is {"features": [...], "truncated": bool}
            assert isinstance(data["data"], dict)
            assert "features" in data["data"]
            features = data["data"]["features"]
            if features:
                # Verify known field names are present
                sample = features[0]
                assert any(
                    k in sample for k in ("PROTECTED_LANDS_NAME", "PROTECTED_LANDS_DESIGNATION", "PROT_LANDS_NAME")
                ), f"Expected park field names not found: {list(sample.keys())[:10]}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_mining_tenure_mineral_claims(self, mcp_server):
        """'Show me mineral claims in the Kamloops area'"""
        data = await call_tool(mcp_server, "bc_get_mining_tenure", {
            "tenure_type": "mineral",
            "max_records": 5,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "bc-wfs"
            # data is {"features": [...], "truncated": bool}
            assert isinstance(data["data"], dict)
            assert "features" in data["data"]

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_discover_bc_wildfire_tools(self, mcp_server):
        """BM25 discovery with 'british columbia wildfire' finds bc_ tools."""
        results = await discover(mcp_server, "british columbia wildfire")
        names = [r["name"] for r in results]
        assert any(n.startswith("bc_") for n in names), (
            f"No bc_ tool found in BM25 results: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_query_features_routes_to_wfs(self, mcp_server):
        """bc_query_features routes to WFS when dataset has queryable_via_wfs=True."""
        # Step 1: search for a known WFS dataset
        search_data = await call_tool(mcp_server, "bc_search_datasets", {
            "q": "fire perimeters",
            "rows": 5,
        })
        if "error" in search_data or not search_data.get("data"):
            pytest.skip("BCDC search returned no results")
        # Step 2: find a dataset with queryable_via_wfs
        wfs_dataset = None
        for ds in search_data["data"]:
            details = await call_tool(mcp_server, "bc_get_dataset_details", {
                "package_id": ds["id"],
            })
            if details.get("data", {}).get("queryable_via_wfs"):
                wfs_dataset = details["data"]
                break
        if wfs_dataset is None:
            pytest.skip("No WFS-queryable dataset found in search results")
        # Step 3: query via bc_query_features (requires package_id, not object_name)
        pkg_id = wfs_dataset.get("id")
        if not pkg_id:
            pytest.skip("Dataset has no id")
        result = await call_tool(mcp_server, "bc_query_features", {
            "package_id": pkg_id,
            "max_records": 3,
        })
        assert "_meta" in result or "error" in result
        if "_meta" in result:
            assert result["_meta"]["source"]["api"] == "bc-wfs"

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_query_features_routes_to_file_parser(self, mcp_server):
        """bc_query_features routes to file parser when dataset has queryable_via_wfs=False."""
        # Search for likely non-WFS datasets (e.g. XLSX/CSV-only)
        search_data = await call_tool(mcp_server, "bc_search_datasets", {
            "q": "statistics report",
            "rows": 10,
        })
        if "error" in search_data or not search_data.get("data"):
            pytest.skip("BCDC search returned no results")
        csv_dataset = None
        for ds in search_data["data"]:
            details = await call_tool(mcp_server, "bc_get_dataset_details", {
                "package_id": ds["id"],
            })
            details_data = details.get("data", {})
            if not details_data.get("queryable_via_wfs") and details_data.get("resources"):
                # Must have at least one downloadable resource
                csv_dataset = details_data
                break
        if csv_dataset is None:
            pytest.skip("No non-WFS dataset with resources found in search results")
        # Verify structure — the tool should return _meta or error, not raise an exception
        assert csv_dataset.get("queryable_via_wfs") is False
        assert isinstance(csv_dataset.get("resources", []), list)


# ─── Quebec Government Open Data scenarios ───────────────────────────────────


@pytest.mark.asyncio
class TestQuebecToolScenarios:
    """Live Données Québec + MTQ WFS CSV integration tests."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_datasets_live(self, mcp_server):
        """'Search for health datasets on Données Québec.'"""
        data = await call_tool(mcp_server, "quebec_search_datasets", {
            "q": "santé",
            "rows": 5,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "donnees-quebec"
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_organizations_live(self, mcp_server):
        """'List all organizations on Données Québec.'"""
        data = await call_tool(mcp_server, "quebec_list_organizations", {})
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            # Must have at least 100 orgs (139 confirmed)
            assert len(data["data"]) >= 100
            slugs = [o["name"] for o in data["data"]]
            assert "msss" in slugs
            assert "mtq" in slugs

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_categories_groups_not_tags(self, mcp_server):
        """'What thematic categories exist on Données Québec?' — must use groups not tags."""
        data = await call_tool(mcp_server, "quebec_list_categories", {})
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            # DQ has 10 thematic groups
            assert len(data["data"]) >= 5
            names = [c["name"] for c in data["data"]]
            assert any("sante" in n or "environnement" in n for n in names), (
                f"No health/environment group found: {names}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_get_er_wait_times_live(self, mcp_server):
        """'What are the current ER wait times in Quebec hospitals?'"""
        data = await call_tool(mcp_server, "quebec_get_er_wait_times", {})
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "donnees-quebec"
            assert isinstance(data["data"], list)
            # 116 EDs in the MSSS datastore
            assert len(data["data"]) >= 50
            row = data["data"][0]
            assert "installation" in row or "establishment" in row

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_get_health_installations_live(self, mcp_server):
        """'Show me CLSCs in Quebec (all health regions).'"""
        data = await call_tool(mcp_server, "quebec_get_health_installations", {
            "instal_type": "CLSC",
            "limit": 10,
        })
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1
            for row in data["data"]:
                assert row["is_clsc"] is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_get_road_works_wfs_csv(self, mcp_server):
        """'What road construction zones are currently active?'"""
        data = await call_tool(mcp_server, "quebec_get_road_works", {})
        # Road works may be empty if no active construction; accept both
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert isinstance(data["data"], list)
            # If data present, verify shape
            if data["data"]:
                row = data["data"][0]
                assert "route" in row or "identifier" in row

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_road_conditions_fields_populated(self, mcp_server):
        """'What are current road conditions in Quebec?' — rows must have non-null route/region/status."""
        data = await call_tool(mcp_server, "quebec_get_road_conditions", {})
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        if data["data"]:
            row = data["data"][0]
            assert row.get("route_num") is not None, (
                "route_num is None — mapper still uses PascalCase keys (expected 'numeroroute')"
            )
            assert row.get("region") is not None, (
                "region is None — mapper still uses PascalCase keys (expected 'nomregion')"
            )
            assert row.get("pavement_status") is not None, (
                "pavement_status is None — mapper uses wrong bilingual column key"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_get_bridge_structures_requires_filter(self, mcp_server):
        """'List bridges in Granby.' — must require at least one filter."""
        # Without filter should return INVALID_INPUT error
        no_filter = await call_tool(mcp_server, "quebec_get_bridge_structures", {})
        assert "error" in no_filter
        assert no_filter["error"]["code"] == "INVALID_INPUT"

        # With municipality filter should succeed (strict assertion — tolerant OR removed)
        with_filter = await call_tool(mcp_server, "quebec_get_bridge_structures", {
            "municipality": "Granby",
            "limit": 5,
        })
        assert "_meta" in with_filter, f"Expected _meta envelope, got: {with_filter}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(120)
    async def test_bridges_route_filter_returns_rows(self, mcp_server):
        """'Show bridges on Autoroute 20.' — WFS paging must reach A-20 rows beyond first 30."""
        data = await call_tool(mcp_server, "quebec_get_bridge_structures", {
            "route": "A-20",
            "limit": 10,
        })
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        assert len(data["data"]) > 0, (
            "Expected non-empty bridge list for A-20 — check WFS paging loop and route normalizer"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_quebec(self, mcp_server):
        """'Find tools for Quebec health data.' — BM25 must surface quebec_ tools."""
        results = await discover(mcp_server, "Quebec health installations MSSS")
        names = [r["name"] for r in results]
        assert any("quebec_" in n for n in names), (
            f"No quebec_ tool found in BM25 results: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_invalid_package_id_returns_structured_error(self, mcp_server):
        """Error handling — invalid dataset slug returns structured error."""
        data = await call_tool(mcp_server, "quebec_get_dataset_details", {
            "package_id": "this-dataset-does-not-exist-xyzzy12345",
        })
        assert "error" in data
        assert data["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_electricity_data_returns_rows(self, mcp_server):
        """'Show Hydro-Québec historical electricity data.' — SSL handshake must succeed."""
        data = await call_tool(mcp_server, "quebec_get_electricity_data", {})
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        assert len(data["data"]) > 0, (
            "Expected non-empty electricity data — SSL handshake to hydroquebec.com failed or "
            "no XLSX resource found. Check fetch_and_parse ssl_context and SECLEVEL=1 fix."
        )
