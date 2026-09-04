# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportPrivateImportUsage=false
"""Integration tests calling tools through the MCP Client layer.

Each test simulates what an agent does: discover_tools → call_tool → parse response.
Tests hit live APIs through the full MCP stack, not client functions directly.

Run: uv run pytest tests/integration/test_tool_scenarios.py -v -m integration --timeout=120
"""

import aiosqlite
import pytest
from tests.integration.conftest import (
    assert_feature_payload,
    assert_live_or_transient,
    assert_rows,
    assert_series_payload,
    call_direct_tool,
    call_tool,
    discover,
)

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
        payload = assert_series_payload(data, "boc_get_exchange_rates", "FXUSDCAD")
        rates = list(payload["FXUSDCAD"]["observations"].values())
        assert all(0.5 < v < 3.0 for v in rates), (
            f"USD/CAD outside a plausible range: {rates}"
        )

    @pytest.mark.asyncio
    async def test_exchange_rate_date_range(self, mcp_server):
        """'Show me EUR/CAD over the last month.'"""
        data = await call_tool(mcp_server, "boc_get_exchange_rates", {
            "currency": "EUR", "start_date": "2026-03-01", "end_date": "2026-03-31"
        })
        payload = assert_series_payload(data, "boc_get_exchange_rates", "FXEURCAD")
        observations = payload["FXEURCAD"]["observations"]
        # ~21 banking days in March; allow for holidays but require a full month.
        assert len(observations) >= 15, (
            f"expected a month of EUR/CAD observations, got {len(observations)}: "
            f"{sorted(observations)[:5]}"
        )
        assert list(payload) == ["FXEURCAD"], (
            f"a single-currency query must return exactly one series: {list(payload)}"
        )

    @pytest.mark.asyncio
    async def test_compare_usd_eur_gbp(self, mcp_server):
        """'Compare USD, EUR, and GBP exchange rates.'"""
        data = await call_tool(mcp_server, "boc_get_observations", {
            "series_names": "FXUSDCAD,FXEURCAD,FXGBPCAD", "recent": 3
        })
        assert_series_payload(
            data, "boc_get_observations", "FXUSDCAD", "FXEURCAD", "FXGBPCAD"
        )

    @pytest.mark.asyncio
    async def test_current_policy_rate(self, mcp_server):
        """'What is the Bank of Canada policy rate?'"""
        data = await call_tool(mcp_server, "boc_get_interest_rates", {"rate_type": "policy", "recent": 1})
        payload = assert_series_payload(data, "boc_get_interest_rates")
        assert payload, f"policy rate query returned no series: {payload}"
        rates = [v for s in payload.values() for v in s["observations"].values()]
        assert rates, f"policy rate series carried no observations: {payload}"
        assert all(0 < v < 20 for v in rates), (
            f"policy rate outside a plausible range: {rates}"
        )

    @pytest.mark.asyncio
    async def test_inflation_cpi(self, mcp_server):
        """'What's the latest Canadian CPI?'"""
        data = await call_tool(mcp_server, "boc_get_inflation_data", {"recent": 3})
        assert "_meta" in data
        assert assert_series_payload(data, "boc_get_inflation_data")

    @pytest.mark.asyncio
    async def test_commodity_energy(self, mcp_server):
        """'Show me energy commodity prices.'"""
        data = await call_tool(mcp_server, "boc_get_commodity_prices", {"commodity_type": "energy", "recent": 3})
        assert assert_series_payload(data, "boc_get_commodity_prices")

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
        fx_payload = assert_series_payload(fx, "boc_get_exchange_rates", "FXUSDCAD")
        assert all(
            v is not None for v in fx_payload["FXUSDCAD"]["observations"].values()
        ), f"USD/CAD observations must carry values: {fx_payload}"

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
        # StatCan WDS has a documented 00:00-08:30 EST maintenance window and
        # reports UPSTREAM_UNAVAILABLE during it, which is tolerated.
        live = assert_live_or_transient(data, "sc_get_changed_cubes", "statcan-wds")
        if live:
            assert_rows(
                data,
                "sc_get_changed_cubes",
                allow_empty_reason="no tables have changed yet today is normal",
            )

    @pytest.mark.asyncio
    async def test_get_changed_series(self, mcp_server):
        """'Which series changed today?'"""
        data = await call_tool(mcp_server, "sc_get_changed_series")
        live = assert_live_or_transient(data, "sc_get_changed_series", "statcan-wds")
        if live:
            assert_rows(
                data,
                "sc_get_changed_series",
                allow_empty_reason="no series have changed yet today is normal",
            )

    @pytest.mark.asyncio
    async def test_error_handling_invalid_product_id(self, mcp_server):
        """'Get metadata for a nonexistent table ID'"""
        data = await call_tool(mcp_server, "sc_get_cube_metadata", {"product_id": 999999999})
        # Error-PATH test: product 999999999 does not exist, so an error IS the
        # expected result. Asserted in both arms rather than tolerated.
        if "error" in data:
            assert "code" in data["error"], f"error must carry a code: {data['error']}"
            assert data["error"]["code"] in ("UPSTREAM_ERROR", "UPSTREAM_UNAVAILABLE"), (
                f"unexpected error code for a nonexistent product: {data['error']}"
            )
        else:
            assert "_meta" in data, f"expected an error or an envelope, got: {data}"

    @pytest.mark.asyncio
    async def test_get_series_info_by_coord(self, mcp_server):
        """'Get series info for CPI Canada all-items by product and coordinate'"""
        # Coordinate 2.2.0.0... is CPI all-items Canada (vector 41690973).
        # 1.1.0.0... is syntactically valid but identifies NO published series —
        # StatCan answers it with responseStatusCode 2 and all-null fields, which
        # is what the companion no-series test below covers.
        data = await call_tool(mcp_server, "sc_get_series_info_by_coord", {
            "product_id": 18100004,
            "coordinate": "2.2.0.0.0.0.0.0.0.0",
        })
        live = assert_live_or_transient(data, "sc_get_series_info_by_coord", "statcan-wds")
        if live:
            info = data["data"]
            for field in ("product_id", "vector_id", "frequency"):
                assert field in info, f"series info missing {field!r}: {info}"
            assert info["vector_id"] == 41690973, (
                f"coordinate 2.2.0.0... is CPI all-items = vector 41690973, "
                f"got {info['vector_id']}"
            )
            assert info["frequency"] == "Monthly", (
                f"CPI is monthly, got {info['frequency']!r}"
            )

    @pytest.mark.asyncio
    async def test_coordinate_with_no_series_is_not_found(self, mcp_server):
        """'Get series info for a coordinate that has no data' — must be NOT_FOUND.

        Regression cover: StatCan answers an unpopulated coordinate with
        status=SUCCESS, responseStatusCode=2 and all-null fields. The client used
        to feed that straight into SeriesInfo and surface
        "UPSTREAM_ERROR: 6 validation errors", blaming the service for what is
        really an empty lookup.
        """
        data = await call_tool(mcp_server, "sc_get_series_info_by_coord", {
            "product_id": 18100004,
            "coordinate": "1.1.0.0.0.0.0.0.0.0",
        })
        assert "error" in data, f"expected a structured error, got: {data}"
        code = data["error"]["code"]
        # UPSTREAM_UNAVAILABLE is possible during the 00:00-08:30 EST window.
        assert code in ("NOT_FOUND", "UPSTREAM_UNAVAILABLE"), (
            f"an empty coordinate is NOT_FOUND, not a service fault: {data['error']}"
        )
        if code == "NOT_FOUND":
            assert "validation error" not in data["error"]["message"].lower(), (
                f"the error must not leak a Pydantic failure: {data['error']}"
            )

    @pytest.mark.asyncio
    async def test_get_data_by_coord(self, mcp_server):
        """'Get the latest 3 observations for CPI Canada all-items by coordinate'"""
        data = await call_tool(mcp_server, "sc_get_data_by_coord", {
            "product_id": 18100004,
            "coordinate": "2.2.0.0.0.0.0.0.0.0",
            "n": 3,
        })
        live = assert_live_or_transient(data, "sc_get_data_by_coord", "statcan-wds")
        if live:
            rows = assert_rows(data, "sc_get_data_by_coord")
            row = rows[0]
            assert "ref_per" in row, f"row missing ref_per: {row}"
            assert "value" in row, f"row missing value: {row}"

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
        live = assert_live_or_transient(data, "sc_get_bulk_vector_data", "statcan-wds")
        if live:
            # Bulk fetch returns a dict keyed by vector id, not a flat list —
            # the key IS the answer to "which vector is this row from", so a
            # flat list would have to repeat it on every row. Same rationale as
            # the BOC series-keyed shape (D-05, decided case by case).
            payload = data["data"]
            assert isinstance(payload, dict), (
                f"bulk vector data is keyed by vector id, got "
                f"{type(payload).__name__}: {payload!r:.120}"
            )
            assert payload, f"both requested vectors returned nothing: {payload}"
            for vector_id, rows in payload.items():
                assert isinstance(rows, list), (
                    f"vector {vector_id} must map to a list of rows, got "
                    f"{type(rows).__name__}"
                )
                for row in rows:
                    assert "ref_per" in row, f"row missing ref_per: {row}"
                    assert "value" in row, f"row missing value: {row}"


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
        """'What happens with a bad breakdown?'

        `breakdown` is Literal-typed, so Pydantic rejects an unknown value at
        the MCP boundary BEFORE the tool body runs. The tool's own INVALID_INPUT
        branch is therefore unreachable for this parameter — the type system is
        the earlier and better gate, and the resulting ToolError names every
        valid option, which a bare INVALID_INPUT string would not.

        This test previously expected a dict and failed with an unhandled
        ToolError; it now asserts the behaviour that actually protects the agent.
        """
        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError) as exc:
            await call_tool(
                mcp_server,
                "ircc_get_permanent_residents",
                {"breakdown": "nonexistent"},
            )

        message = str(exc.value)
        assert "breakdown" in message, f"error must name the offending parameter: {message}"
        for valid in ("country", "province", "gender"):
            assert valid in message, (
                f"the rejection must list valid options so the agent can retry; "
                f"{valid!r} missing from: {message}"
            )

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
        # 2023 PR data is a closed historical year — empty means the fetch broke,
        # so this asserts rather than skipping. (It skipped until 2026-07-25,
        # which hid the datastore dict-binding failure further down.)
        assert rows, f"IRCC returned no PR rows for 2023: {pr_result}"
        sample_rows = rows[:3]

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
        live = assert_live_or_transient(data, "york_region_get_transit_stops", "arcgis-hub")
        if live:
            assert_feature_payload(data, "york_region_get_transit_stops")

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_york_region_hospitals(self, mcp_server):
        """'Where are York Region hospitals?'"""
        data = await call_tool(mcp_server, "york_region_get_public_health", {
            "location_type": "hospital",
        })
        live = assert_live_or_transient(data, "york_region_get_public_health", "arcgis-hub")
        if live:
            payload = assert_feature_payload(data, "york_region_get_public_health")
            assert payload["features"], (
                f"York Region has hospitals — an empty feature list means the "
                f"location_type filter is broken: {payload}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_markham_search_addresses(self, mcp_server):
        """'Find Main Street addresses in Markham'"""
        data = await call_tool(mcp_server, "markham_get_addresses", {
            "street": "Main",
        })
        live = assert_live_or_transient(data, "markham_get_addresses", "arcgis-hub")
        if live:
            payload = assert_feature_payload(data, "markham_get_addresses")
            assert payload["features"], (
                f"Markham has Main Street addresses — empty means the street "
                f"filter is broken: {payload}"
            )

    @pytest.mark.asyncio
    async def test_aurora_list_categories_live(self, mcp_server):
        """'What dataset categories exist in Aurora open data?'"""
        data = await call_tool(mcp_server, "aurora_list_categories")
        live = assert_live_or_transient(data, "aurora_list_categories", "arcgis-hub")
        if live:
            # Regression cover: this returned UPSTREAM_ERROR until 2026-07-25
            # because the shared Hub client sent `q=` on a no-query listing and
            # every Hub portal 400s on an empty q.
            assert_rows(data, "aurora_list_categories")

    @pytest.mark.asyncio
    async def test_newmarket_search_datasets_live(self, mcp_server):
        """'Search Newmarket open data for any datasets'"""
        data = await call_tool(mcp_server, "newmarket_search_datasets", {
            "query": "",
            "limit": 5,
        })
        live = assert_live_or_transient(data, "newmarket_search_datasets", "arcgis-hub")
        if live:
            # Same empty-q regression as aurora_list_categories — an empty query
            # is the whole point of this test, so it exercises the fixed path.
            assert_rows(data, "newmarket_search_datasets")

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
    """BC open data tool integration scenarios — live BCDC CKAN + BCGW WFS endpoints.

    Pinned package ids (D-11): the WFS-routing tests used to discover a dataset
    by searching, then pytest.skip() when the search came back empty. A skip
    reports neither pass nor fail, so "BCDC search returned no results" silently
    meant the routing path under test was never exercised. These two datasets are
    canonical, long-lived BCDC entries; if either ever disappears the test fails
    loudly, which is the point.
    """

    #: BC Wildfire Fire Perimeters - Historical (queryable_via_wfs=True,
    #: WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP)
    WFS_PACKAGE_ID = "22c7cb44-1463-48f7-8e47-88857f207702"
    #: BC Greenhouse Gas Emissions (queryable_via_wfs=False, 11 file resources)
    NON_WFS_PACKAGE_ID = "7ec1a555-122e-4173-9536-1731dfd63b5c"

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_search_finds_wildfire_data(self, mcp_server):
        """'Search BC open data for wildfire datasets'"""
        data = await call_tool(mcp_server, "bc_search_datasets", {
            "q": "wildfire",
            "rows": 5,
        })
        live = assert_live_or_transient(data, "bc_search_datasets")
        if live:
            results = assert_rows(data, "bc_search_datasets")
            titles = [d.get("title", "").lower() for d in results]
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
        live = assert_live_or_transient(data, "bc_get_active_fires", "bc-wfs")
        if live:
            payload = data["data"]
            assert isinstance(payload, dict), (
                f"WFS tools return a dict, got {type(payload).__name__}"
            )
            assert "features" in payload, f"payload missing features: {payload}"
            assert isinstance(payload["features"], list)
            assert "truncated" in payload, f"payload missing truncated: {payload}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_fire_perimeters_by_year(self, mcp_server):
        """'Get historical fire perimeters for 2023 in BC'"""
        data = await call_tool(mcp_server, "bc_get_fire_perimeters", {
            "year": 2023,
            "max_records": 10,
        })
        live = assert_live_or_transient(data, "bc_get_fire_perimeters", "bc-wfs")
        if live:
            payload = data["data"]
            assert isinstance(payload, dict), (
                f"WFS tools return a dict, got {type(payload).__name__}"
            )
            assert "features" in payload, f"payload missing features: {payload}"
            # 2023 was a record BC fire season — an empty result is a defect.
            assert payload["features"] or payload.get("truncated") is True, (
                f"2023 fire perimeters must return features: {payload}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_protected_areas_returns_parks(self, mcp_server):
        """'List provincial parks in BC'"""
        data = await call_tool(mcp_server, "bc_get_protected_areas", {
            "designation": "PROVINCIAL PARK",
            "max_records": 10,
        })
        live = assert_live_or_transient(data, "bc_get_protected_areas", "bc-wfs")
        if live:
            payload = data["data"]
            assert "features" in payload, f"payload missing features: {payload}"
            # BC has hundreds of provincial parks — empty means broken.
            features = payload["features"]
            assert features, f"PROVINCIAL PARK designation returned nothing: {payload}"
            sample = features[0]
            assert any(
                k in sample
                for k in ("PROTECTED_LANDS_NAME", "PROTECTED_LANDS_DESIGNATION", "PROT_LANDS_NAME")
            ), f"Expected park field names not found: {list(sample.keys())[:10]}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_mining_tenure_mineral_claims(self, mcp_server):
        """'Show me mineral claims in the Kamloops area'"""
        data = await call_tool(mcp_server, "bc_get_mining_tenure", {
            "tenure_type": "mineral",
            "max_records": 5,
        })
        live = assert_live_or_transient(data, "bc_get_mining_tenure", "bc-wfs")
        if live:
            payload = data["data"]
            assert "features" in payload, f"payload missing features: {payload}"
            assert payload["features"], (
                f"BC has thousands of active mineral claims — empty means the "
                f"tenure_type filter is broken: {payload}"
            )

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
    async def test_dataset_details_exposes_wfs_routing_metadata(self, mcp_server):
        """The two-step workflow depends on details carrying the WFS routing flags."""
        details = await call_tool(mcp_server, "bc_get_dataset_details", {
            "package_id": self.WFS_PACKAGE_ID,
        })
        live = assert_live_or_transient(details, "bc_get_dataset_details")
        if live:
            dd = details["data"]
            assert dd.get("queryable_via_wfs") is True, (
                f"{self.WFS_PACKAGE_ID} (BC Wildfire Fire Perimeters - Historical) "
                f"must be WFS-queryable — bc_query_features routing depends on this "
                f"flag. Got: {dd.get('queryable_via_wfs')!r}"
            )
            assert dd.get("object_name"), (
                f"a WFS-queryable dataset must expose object_name: {dd}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_query_features_routes_to_wfs(self, mcp_server):
        """bc_query_features routes to WFS when dataset has queryable_via_wfs=True."""
        result = await call_tool(mcp_server, "bc_query_features", {
            "package_id": self.WFS_PACKAGE_ID,
            "max_records": 3,
        })
        live = assert_live_or_transient(result, "bc_query_features", "bc-wfs")
        if live:
            payload = result["data"]
            assert isinstance(payload, dict), (
                f"the WFS route returns a dict, got {type(payload).__name__} — "
                f"a list would mean it fell through to the file parser"
            )
            assert "features" in payload, f"WFS payload missing features: {payload}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_query_features_routes_to_file_parser(self, mcp_server):
        """bc_query_features routes to the file parser when queryable_via_wfs=False."""
        details = await call_tool(mcp_server, "bc_get_dataset_details", {
            "package_id": self.NON_WFS_PACKAGE_ID,
        })
        live = assert_live_or_transient(details, "bc_get_dataset_details")
        if live:
            dd = details["data"]
            assert dd.get("queryable_via_wfs") is False, (
                f"{self.NON_WFS_PACKAGE_ID} (BC Greenhouse Gas Emissions) is a "
                f"file-resource dataset and must NOT be WFS-queryable — this test "
                f"exercises the non-WFS branch. Got: {dd.get('queryable_via_wfs')!r}"
            )
            resources = dd.get("resources") or []
            assert isinstance(resources, list) and resources, (
                f"the file-parser route needs downloadable resources: {dd}"
            )


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
        assert "_meta" in data, f"Expected live success from quebec_search_datasets, got: {data}"
        assert data["_meta"]["source"]["api"] == "donnees-quebec"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_organizations_live(self, mcp_server):
        """'List all organizations on Données Québec.'"""
        data = await call_tool(mcp_server, "quebec_list_organizations", {})
        assert "_meta" in data, f"Expected live success from quebec_list_organizations, got: {data}"
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
        assert "_meta" in data, f"Expected live success from quebec_list_categories, got: {data}"
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
        assert "_meta" in data, f"Expected live success from quebec_get_er_wait_times, got: {data}"
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
        assert "_meta" in data, f"Expected live success from quebec_get_health_installations, got: {data}"
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
        assert "_meta" in data, f"Expected live success from quebec_get_road_works, got: {data}"
        rows = assert_rows(
            data,
            "quebec_get_road_works",
            allow_empty_reason="no active construction zones province-wide is possible",
        )
        for row in rows[:1]:
            assert "route" in row or "identifier" in row, (
                f"road works row missing both route and identifier: {row}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_road_conditions_fields_populated(self, mcp_server):
        """'What are current road conditions in Quebec?' — rows must have non-null route/region/status."""
        data = await call_tool(mcp_server, "quebec_get_road_conditions", {})
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        rows = assert_rows(
            data,
            "quebec_get_road_conditions",
            allow_empty_reason="MTQ winter road conditions are not published outside winter",
        )
        for row in rows[:1]:
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
    @pytest.mark.timeout(120)
    async def test_bridges_route_filter_row_types(self, mcp_server):
        """'Show bridges on Autoroute 20 with strict type assertions.' — 16-07 gap closure.

        After shared/parsers.py:_mask_privacy turns digit-only CSV cells into int,
        _flatten_bridge must re-stringify ID columns so QuebecBridgeStructure
        validates. route_num must be zero-padded to match the normalizer output.
        """
        data = await call_tool(mcp_server, "quebec_get_bridge_structures", {
            "route": "A-20",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        assert len(data["data"]) > 0, (
            f"Expected non-empty A-20 bridge list, got: {data}"
        )
        for row in data["data"]:
            assert isinstance(row["structure_id"], str), (
                f"structure_id must be str, got "
                f"{type(row['structure_id']).__name__}={row['structure_id']}"
            )
            assert isinstance(row["dossier_num"], str), (
                f"dossier_num must be str, got "
                f"{type(row['dossier_num']).__name__}={row['dossier_num']}"
            )
            assert isinstance(row["municipality_code"], str), (
                f"municipality_code must be str, got "
                f"{type(row['municipality_code']).__name__}={row['municipality_code']}"
            )
            assert isinstance(row["route_num"], str), (
                f"route_num must be str, got "
                f"{type(row['route_num']).__name__}={row['route_num']}"
            )
            assert "0020" in row["route_num"] or row["route_num"] == "00020", (
                f"route_num should be zero-padded form '00020', got {row['route_num']}"
            )
            assert row["route_num"] != "00204", (
                "Route 204 row leaked through A-20 filter — substring match bug"
            )
            # route_name is nullable upstream; when present it must not be a
            # Route 204 leak. `or ""` keeps the assertion on every row.
            assert "route 204" not in (row.get("route_name") or "").lower(), (
                f"Route 204 name leaked: {row.get('route_name')}"
            )
            assert isinstance(row["structure_type"], str), (
                f"structure_type must be str, got "
                f"{type(row['structure_type']).__name__}={row['structure_type']}"
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

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(120)
    async def test_electricity_first_row_is_real(self, mcp_server):
        """'First row of electricity data must be real, not the XLSX legend.' — 16-07 gap closure.

        Hydro-Québec XLSX files document column formulas in the first data row
        (null indexing cells, cells like '5=1-2+3+4'). fetch_electricity_data
        filters this out so data[0]['rang'] == 1 (the real first hour).
        """
        data = await call_tool(mcp_server, "quebec_get_electricity_data", {"limit": 5})
        assert "_meta" in data, f"Expected _meta envelope, got: {data}"
        assert len(data["data"]) > 0, "Expected non-empty electricity rows"
        first = data["data"][0]
        assert first.get("rang") == 1, (
            "First row should be real data with rang=1 (legend row should be "
            f"filtered out). Got: {first}"
        )
        # Defensive: no formula strings should leak
        for k, v in first.items():
            assert not (
                isinstance(v, str) and "=" in v and any(ch.isdigit() for ch in v)
            ), f"Formula string leaked into first row [{k}]={v!r}"


# ─── Alberta Government Open Data scenarios ──────────────────────────────────


@pytest.mark.asyncio
class TestAlbertaToolScenarios:
    """Live open.alberta.ca CKAN + WMBappServices + AHSGIS + 511 Alberta + AER integration tests.

    Every test calls alberta tools through the MCP Client layer (via call_tool/discover_tools),
    not the client functions directly — the same path an agent takes. Assertions are
    shape-focused, not value-specific (counts, statuses, and prices drift daily).
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_search_wildfire_datasets(self, mcp_server):
        """'Find Alberta wildfire datasets' — live open.alberta.ca CKAN search."""
        data = await call_tool(mcp_server, "alberta_search_datasets", {
            "q": "wildfire",
            "format": "CSV",
            "rows": 5,
        })
        live = assert_live_or_transient(data, "alberta_search_datasets", "alberta-open-data")
        if live:
            payload = data["data"]
            assert "results" in payload, f"payload missing results: {list(payload)}"
            # open.alberta.ca has thousands of wildfire CSVs — zero means the
            # search or the format filter is broken, not that Alberta is quiet.
            assert payload["results"], (
                f"wildfire+CSV search returned nothing: {payload}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_active_fires_now(self, mcp_server):
        """'How many active wildfires in Alberta right now?' — live WMBappServices FeatureServer."""
        data = await call_tool(mcp_server, "alberta_get_active_fires", {})
        live = assert_live_or_transient(data, "alberta_get_active_fires", "alberta-wmb-arcgis")
        if live:
            # Feature count is NOT asserted — active fires vary seasonally and
            # zero is a legitimate winter reading. The shape must still hold.
            assert_feature_payload(data, "alberta_get_active_fires")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_alberta_hospitals(self, mcp_server):
        """'List Alberta hospitals' — live AHSGIS FeatureServer (~101 hospitals)."""
        data = await call_tool(mcp_server, "alberta_get_hospitals", {})
        live = assert_live_or_transient(data, "alberta_get_hospitals", "alberta-ahs-arcgis")
        if live:
            payload = assert_feature_payload(data, "alberta_get_hospitals")
            count = payload.get("count")
            assert isinstance(count, int), (
                f"the AHS hospital layer must report a count, got {count!r} — "
                f"a missing count previously skipped this assertion entirely"
            )
            # ~101 hospitals expected; generous window for live drift.
            assert 50 <= count <= 250, (
                f"Alberta hospital count unexpectedly far from ~101: {count}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_alberta_road_events(self, mcp_server):
        """'What's happening on Alberta roads right now?' — live 511 Alberta JSON feed."""
        data = await call_tool(mcp_server, "alberta_get_road_events", {})
        assert "_meta" in data or "error" in data
        if "_meta" in data:
            assert data["_meta"]["source"]["api"] == "alberta-511"
            assert "events" in data["data"]
            assert isinstance(data["data"]["events"], list)
        else:
            assert data["error"]["code"] in {"UPSTREAM_ERROR", "RATE_LIMITED"}, (
                f"Road events error must be UPSTREAM_ERROR/RATE_LIMITED, got: {data.get('error')}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(90)
    async def test_alberta_production_volumes_gas(self, mcp_server):
        """'Get Alberta natural gas monthly production' — live AER static XLSX."""
        data = await call_tool(mcp_server, "alberta_get_production_volumes", {
            "product": "Gas",
        })
        assert "_meta" in data or "error" in data
        # Either success with rows OR graceful upstream/rate-limit error — no silent shape drift.
        # AER sometimes returns a redirect / XLSX parse fails during republish windows;
        # accept UPSTREAM_ERROR or RATE_LIMITED as legitimate transient outcomes.
        if "_meta" in data:
            # `data` from fetch_production_volumes is the parsed row list (see client.py)
            # which surfaces as `data["data"]` — may be a list (rows) or dict wrapping rows.
            payload = data["data"]
            # Shape sanity: either we got rows, or a wrapper with rows, or a dict at minimum.
            assert isinstance(payload, (list, dict)), (
                f"Unexpected data payload shape: {type(payload).__name__}"
            )
        else:
            assert data.get("error", {}).get("code") in {"UPSTREAM_ERROR", "RATE_LIMITED"}, (
                f"Expected UPSTREAM_ERROR or RATE_LIMITED, got: {data.get('error')}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_alberta_invalid_product_returns_structured_error(self, mcp_server):
        """'Get Bitumen production' — should fail with INVALID_INPUT (Pitfall 8, case-sensitive)."""
        data = await call_tool(mcp_server, "alberta_get_production_volumes", {
            "product": "Bitumen",  # Not a valid slug; Bitumen is bundled inside Oil
        })
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"
        # valid= extras list must be present with all 7 products
        assert "valid" in data["error"]
        assert "Butane" in data["error"]["valid"]
        assert "Gas" in data["error"]["valid"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_alberta_via_bm25(self, mcp_server):
        """'alberta wells oil energy regulator' — BM25 must surface alberta_ tools in top 5."""
        results = await discover(mcp_server, "alberta wells oil energy regulator")
        names = [r["name"] for r in results]
        assert any(n.startswith("alberta_") for n in names), (
            f"No alberta_ tool found in BM25 discovery results: {names}"
        )


# ─── Manitoba scenarios ──────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestManitobaToolScenarios:
    """Integration tests calling Manitoba tools through the MCP Client layer.

    Tests simulate what an agent would ask via natural-language prompts:
    - Flood alerts (empty list = normal, must NOT be an error)
    - Provincial parks
    - Surgical wait times
    - Drought status
    - BM25 discovery of manitoba_get_flood_alerts
    - Invalid f_type returns structured INVALID_INPUT error
    - 511 NOT_CONFIGURED when key absent (always-testable without a key)
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_flood_alerts_empty_is_success(self, mcp_server):
        """'Current Manitoba flood alerts' — empty list is NORMAL and must return _meta not error."""
        data = await call_tool(mcp_server, "manitoba_get_flood_alerts", {})
        # Must return either a _meta envelope (with possibly empty features) or an UPSTREAM_ERROR
        # (transient ArcGIS connectivity issue). Must NEVER return NOT_FOUND or INVALID_INPUT.
        assert "_meta" in data or "error" in data
        if "error" in data:
            assert data["error"]["code"] == "UPSTREAM_ERROR", (
                "Flood alerts error must be UPSTREAM_ERROR, not any other code"
            )
        else:
            assert "_meta" in data
            assert data["_meta"]["source"]["api"] == "manitoba-flood-alerts"
            payload = data["data"]
            # features may be empty (off-season) or populated — both are valid
            assert "features" in payload
            assert isinstance(payload["features"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_provincial_parks(self, mcp_server):
        """'What are Manitoba provincial parks?' — live ArcGIS FeatureServer (93 parks)."""
        data = await call_tool(mcp_server, "manitoba_get_provincial_parks", {})
        assert "_meta" in data, f"Expected live success from manitoba_get_provincial_parks, got: {data}"
        assert data["_meta"]["source"]["api"] == "manitoba-provincial-parks"
        payload = data["data"]
        assert "features" in payload
        assert isinstance(payload["features"], list)
        # ~93 parks expected; don't assert exact count (data drift)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_surgical_wait_times_for_cardiac(self, mcp_server):
        """'Manitoba surgical wait times for cardiac surgery' — live FeatureServer."""
        data = await call_tool(mcp_server, "manitoba_get_surgical_wait_times", {
            "procedure": "Cardiac",
        })
        assert "_meta" in data, f"Expected live success from manitoba_get_surgical_wait_times, got: {data}"
        assert data["_meta"]["source"]["api"] == "manitoba-surgical-wait-times"
        payload = data["data"]
        assert "features" in payload
        assert isinstance(payload["features"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_drought_status(self, mcp_server):
        """'Manitoba drought status' — live continental Drought Monitor FeatureServer."""
        data = await call_tool(mcp_server, "manitoba_get_drought_status", {})
        assert "_meta" in data, f"Expected live success from manitoba_get_drought_status, got: {data}"
        assert "drought" in data["_meta"]["source"]["api"]
        payload = data["data"]
        assert "features" in payload
        assert isinstance(payload["features"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_flood_alerts_via_bm25(self, mcp_server):
        """'manitoba flood alerts warnings' — BM25 must surface manitoba_get_flood_alerts."""
        results = await discover(mcp_server, "manitoba flood alerts warnings")
        names = [r["name"] for r in results]
        assert "manitoba_get_flood_alerts" in names, (
            f"Expected manitoba_get_flood_alerts in BM25 results, got: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_invalid_f_type_returns_structured_error(self, mcp_server):
        """Invalid f_type 'swamp' → INVALID_INPUT with valid= list (not an exception)."""
        data = await call_tool(mcp_server, "manitoba_get_provincial_waterways", {
            "f_type": "swamp",
        })
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"
        assert "valid" in data["error"]
        valid_types = data["error"]["valid"]
        assert isinstance(valid_types, list)
        # Must include the real waterway types (dike, floodway, etc.)
        assert len(valid_types) >= 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_511_not_configured_without_key(self, mcp_server):
        """Manitoba 511 road events returns NOT_CONFIGURED when MANITOBA_511_KEY absent.

        This test exercises the NOT_CONFIGURED path WITHOUT needing the actual API key.
        The error is deterministic: key absent = NOT_CONFIGURED, no flakiness.
        """
        import os
        key = os.environ.pop("MANITOBA_511_KEY", None)
        try:
            data = await call_tool(mcp_server, "manitoba_get_road_events", {})
        finally:
            if key is not None:
                os.environ["MANITOBA_511_KEY"] = key

        if key is None:
            # Key was absent during test — must get NOT_CONFIGURED
            assert "error" in data
            assert data["error"]["code"] == "NOT_CONFIGURED", (
                f"Expected NOT_CONFIGURED for missing 511 key, got: {data}"
            )
            assert "511" in data["error"]["message"] or "MANITOBA_511_KEY" in data["error"]["message"]
        else:
            # Key was present — either live data or UPSTREAM_ERROR is acceptable
            assert "_meta" in data or "error" in data

    # ------------------------------------------------------------------
    # Plan 09 gap-closure: live OGC param fix for 3 discovery tools
    # These call the REAL geoportal — mocks masked the bug, so a live
    # check is the only reliable acceptance test.
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_datasets_live(self, mcp_server):
        """'Search the Manitoba geoportal for parks' — live OGC Hub Search (was HTTP 400 before fix)."""
        data = await call_tool(mcp_server, "manitoba_search_datasets", {"query": "parks"})
        assert "_meta" in data or "error" in data
        assert "error" not in data, (
            f"Live search must not return error after OGC param fix: {data.get('error')}"
        )
        assert data["_meta"]["source"]["api"] == "manitoba-geoportal-hub"
        payload = data["data"]
        assert "results" in payload and isinstance(payload["results"], list)
        assert payload["total"] >= 1, "'parks' must return at least 1 live dataset"
        assert len(payload["results"]) >= 1
        first = payload["results"][0]
        assert "id" in first and "title" in first

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_organizations_live(self, mcp_server):
        """'Who publishes data on the Manitoba geoportal?' — live OGC Hub Search (was HTTP 400)."""
        data = await call_tool(mcp_server, "manitoba_list_organizations", {})
        assert "error" not in data, (
            f"Live orgs must not return error after OGC param fix: {data.get('error')}"
        )
        assert data["_meta"]["source"]["api"] == "manitoba-geoportal-hub"
        orgs = data["data"]["organizations"]
        assert isinstance(orgs, list) and len(orgs) >= 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_categories_live(self, mcp_server):
        """'What dataset categories exist on the Manitoba geoportal?' — live OGC Hub Search (was HTTP 400)."""
        data = await call_tool(mcp_server, "manitoba_list_categories", {})
        assert "error" not in data, (
            f"Live categories must not return error after OGC param fix: {data.get('error')}"
        )
        assert data["_meta"]["source"]["api"] == "manitoba-geoportal-hub"
        cats = data["data"]["categories"]
        assert isinstance(cats, list) and len(cats) >= 1


class TestSaskatchewanToolScenarios:
    """Integration tests calling Saskatchewan tools through the MCP Client layer.

    The Manitoba lesson: mocks masked a live 400. Every test here must assert FIELD
    PRESENCE + non-null values (not just _meta shape) against the REAL endpoints.

    Tests simulate what an agent would ask:
    - Crop yields: 'Canola' key present and non-null (field-presence assertion)
    - Grain elevators: at least one row with Capacity_tonne and PR=='SK' non-null
    - Potash mines: Name + Company non-null (INVALID_INPUT for unsupported mineral)
    - Air quality: AQHI field present (weather.gc.ca URL) and at least one pollutant
    - Fire bans: empty list is VALID (no error envelope in off-season)
    - WSA stations: HyperLink_Graph present in >=1 result (catches layer-ID / org bug)
    - WSA reservoirs: Reservoir_Name in >=1 result (PROVES layer 26, not 0)
    - Discovery: discover_tools finds saskatchewan_search_datasets; tool returns numberMatched>=1
    - Error: invalid mineral -> structured INVALID_INPUT, not an exception
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_crop_yields_canola_field_present(self, mcp_server):
        """'Saskatchewan crop yields' — 'Canola' key present with non-null numeric value.

        THE MANITOBA LESSON: asserts field presence + non-null, not just _meta shape.
        """
        data = await call_tool(mcp_server, "saskatchewan_get_crop_yields", {
            "region": "provincial",
        })
        assert "_meta" in data, f"Expected live success from saskatchewan_get_crop_yields, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        features = data["data"]["features"]
        assert isinstance(features, list), "Crop yields must return a features list"
        assert len(features) >= 1, "Crop yields must return at least 1 row"
        # FIELD PRESENCE: Canola must be present and non-null in at least one row
        canola_values = [row.get("Canola") for row in features if row.get("Canola") is not None]
        assert len(canola_values) >= 1, (
            f"FIELD PRESENCE FAILED: 'Canola' key must be present with a non-null value "
            f"in at least one row. Got features: {[list(f.keys()) for f in features[:2]]}"
        )
        assert isinstance(canola_values[0], (int, float)), (
            f"Canola value must be numeric, got {type(canola_values[0])}: {canola_values[0]}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_grain_elevators_capacity_and_province(self, mcp_server):
        """'Saskatchewan grain elevators' — at least one row with Capacity_tonne and PR=='SK'."""
        data = await call_tool(mcp_server, "saskatchewan_get_grain_elevators", {})
        assert "_meta" in data, f"Expected live success from saskatchewan_get_grain_elevators, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) >= 1, "Grain elevators must return at least 1 SK elevator"
        # FIELD PRESENCE: at least one row must have Capacity_tonne non-null and PR='SK'
        sk_elevators = [f for f in features if f.get("PR") == "SK" and f.get("Capacity_tonne") is not None]
        assert len(sk_elevators) >= 1, (
            f"FIELD PRESENCE FAILED: At least one row must have PR='SK' and non-null Capacity_tonne. "
            f"Got {len(features)} rows. PR values: {[f.get('PR') for f in features[:5]]}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_potash_mines_name_and_company(self, mcp_server):
        """'Saskatchewan potash mines' — Name + Company present and non-null."""
        data = await call_tool(mcp_server, "saskatchewan_get_mineral_mines", {
            "mineral": "potash",
        })
        assert "_meta" in data, f"Expected live success from saskatchewan_get_mineral_mines, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) >= 1, "Potash mines must return at least 1 mine record"
        # FIELD PRESENCE: Name and Company must be non-null in at least one row
        first = features[0]
        assert first.get("Name") is not None, (
            f"FIELD PRESENCE FAILED: 'Name' must be non-null. Got: {first}"
        )
        assert first.get("Company") is not None, (
            f"FIELD PRESENCE FAILED: 'Company' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_air_quality_aqhi_field_present(self, mcp_server):
        """'Saskatchewan air quality in Regina' — AQHI field present and at least one pollutant."""
        data = await call_tool(mcp_server, "saskatchewan_get_air_quality", {})
        assert "_meta" in data, f"Expected live success from saskatchewan_get_air_quality, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) >= 1, "Air quality must return at least 1 station reading"
        # FIELD PRESENCE: AQHI must be present (weather.gc.ca URL or value)
        aqhi_values = [f.get("AQHI") for f in features if f.get("AQHI") is not None]
        assert len(aqhi_values) >= 1, (
            f"FIELD PRESENCE FAILED: 'AQHI' key must be present with a non-null value "
            f"in at least one row. Keys in first row: {list(features[0].keys())}"
        )
        # At least one pollutant reading present in any row
        pollutant_fields = ("PM2_5", "NO2", "O3", "SO2", "CO", "H2S", "PM10")
        for row in features:
            if any(row.get(p) is not None for p in pollutant_fields):
                break
        else:
            assert False, (
                f"FIELD PRESENCE FAILED: At least one pollutant reading (PM2_5/NO2/O3/etc.) "
                f"must be non-null across all rows. Keys: {list(features[0].keys())}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_fire_bans_empty_is_valid_not_error(self, mcp_server):
        """'Saskatchewan fire bans' — empty list is VALID (no bans in off-season is correct).

        The empty-is-valid lesson: fire bans tool must NEVER convert an empty FeatureServer
        result to an error. Off-season = no active bans = success with count=0.
        """
        data = await call_tool(mcp_server, "saskatchewan_get_fire_bans", {
            "ban_scope": "urban",
        })
        # Must NOT return an error (empty result is valid off-season state)
        assert "error" not in data, (
            f"Empty fire bans MUST NOT return error. Got: {data.get('error')}"
        )
        assert "_meta" in data, (
            f"Fire bans must return _meta envelope (even with 0 bans). Got: {data}"
        )
        assert "spsa" in data["_meta"]["source"]["api"], (
            f"Fire bans must use SPSA api_name. Got: {data['_meta']['source']['api']}"
        )
        payload = data["data"]
        assert "features" in payload, "Fire bans payload must include 'features' key"
        assert isinstance(payload["features"], list), (
            f"features must be a list (may be empty). Got: {type(payload['features'])}"
        )
        # count >= 0 (0 in off-season, >=1 if bans are active)
        assert payload.get("count", -1) >= 0, (
            f"Fire bans count must be >= 0. Got: {payload.get('count')}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wsa_stations_hyperlink_graph_present(self, mcp_server):
        """'Saskatchewan WSA hydrometric stations' — HyperLink_Graph field present in >=1 result.

        THE CRITICAL FIELD PRESENCE TEST: HyperLink_Graph is the unique field that catches
        a layer-ID bug or wrong-org bug. If the wrong layer or org is used, this field is absent.
        """
        data = await call_tool(mcp_server, "saskatchewan_get_wsa_stations", {})
        assert "_meta" in data, f"Expected live success from saskatchewan_get_wsa_stations, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-wsa", (
            f"WSA stations must use 'saskatchewan-wsa' api_name. "
            f"Got: {data['_meta']['source']['api']}"
        )
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) >= 1, "WSA stations must return at least 1 station"
        # FIELD PRESENCE: HyperLink_Graph must be present in >=1 result
        hyperlink_rows = [f for f in features if f.get("HyperLink_Graph") is not None]
        assert len(hyperlink_rows) >= 1, (
            f"FIELD PRESENCE FAILED: 'HyperLink_Graph' must be non-null in >=1 station row. "
            f"This catches the wrong-org or wrong-layer bug (layer 0 has no graph links). "
            f"Keys in first row: {list(features[0].keys())}"
        )
        # The HyperLink_Graph should be a wsask.ca URL
        first_link = hyperlink_rows[0]["HyperLink_Graph"]
        assert isinstance(first_link, str) and len(first_link) > 0, (
            f"HyperLink_Graph must be a non-empty string, got: {first_link!r}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wsa_reservoirs_reservoir_name_proves_layer_26(self, mcp_server):
        """'Saskatchewan WSA reservoirs' — Reservoir_Name present PROVES layer 26 (not layer 0).

        THE CRITICAL LAYER TEST: WSA_Reservoirs FeatureServer layer 0 returns EMPTY (0 features).
        Only layer 26 returns Reservoir_Name. This test PROVES the implementation uses layer 26.
        """
        data = await call_tool(mcp_server, "saskatchewan_get_wsa_reservoirs", {})
        assert "_meta" in data, f"Expected live success from saskatchewan_get_wsa_reservoirs, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-wsa", (
            f"WSA reservoirs must use 'saskatchewan-wsa' api_name. "
            f"Got: {data['_meta']['source']['api']}"
        )
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) >= 1, (
            "WSA reservoirs must return at least 1 reservoir. "
            "An empty list means the WRONG LAYER (layer 0) was used — layer 26 is required."
        )
        # FIELD PRESENCE: Reservoir_Name must be present (PROVES layer 26 was used)
        reservoir_name_rows = [f for f in features if f.get("Reservoir_Name") is not None]
        assert len(reservoir_name_rows) >= 1, (
            f"FIELD PRESENCE FAILED: 'Reservoir_Name' must be non-null in >=1 row. "
            f"This PROVES layer 26 was used (layer 0 returns no data). "
            f"Keys in first row: {list(features[0].keys())}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_saskatchewan_search_datasets(self, mcp_server):
        """'Saskatchewan crops' — BM25 must surface saskatchewan_search_datasets."""
        results = await discover(mcp_server, "Saskatchewan crops agriculture")
        names = [r["name"] for r in results]
        assert "saskatchewan_search_datasets" in names or any(
            "saskatchewan" in n for n in names
        ), (
            f"Expected a saskatchewan_ tool in BM25 results for 'Saskatchewan crops agriculture', "
            f"got: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_datasets_returns_number_matched(self, mcp_server):
        """'Search Saskatchewan datasets for crops' — numberMatched>=1 (proves startindex pagination).

        This is the startindex-pagination acceptance test. Before the shared/arcgis_hub.py fix,
        the OGC Hub Search returned numberMatched=null, masking pagination failures.
        After the fix, startindex works and numberMatched>0 for any real query.
        """
        data = await call_tool(mcp_server, "saskatchewan_search_datasets", {"query": "crops"})
        assert "_meta" in data, f"Expected live success from saskatchewan_search_datasets, got: {data}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        payload = data["data"]
        assert "total" in payload, f"response must include 'total' key: {payload}"
        assert payload["total"] >= 1, (
            f"STARTINDEX PAGINATION FAILED: 'crops' query must return total>=1. "
            f"Got total={payload.get('total')} — this indicates the OGC startindex fix "
            f"is not working or the Hub has no crop datasets."
        )
        assert "results" in payload and isinstance(payload["results"], list)
        assert len(payload["results"]) >= 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_invalid_mineral_returns_structured_error(self, mcp_server):
        """Invalid mineral 'gold' -> rejected (not an exception that crashes the server).

        FastMCP validates the Literal["potash","uranium","helium","coal"] at the MCP layer
        (Pydantic), so 'gold' raises a ToolError before reaching the tool's INVALID_INPUT
        handler. Either outcome is correct: Pydantic validation error (MCP layer) or
        INVALID_INPUT (tool layer). Both prove the system rejects invalid input gracefully.
        """
        from fastmcp.client.mixins.tools import ToolError

        # The tool parameter is typed Literal["potash", "uranium", "helium", "coal"]
        # FastMCP/Pydantic may reject "gold" at the MCP layer before the tool runs.
        try:
            data = await call_tool(mcp_server, "saskatchewan_get_mineral_mines", {
                "mineral": "gold",
            })
            # If the tool ran (no ToolError): must be a structured error, not a crash
            assert "error" in data, (
                f"Invalid mineral 'gold' must return error envelope, got: {data}"
            )
            assert data["error"]["code"] == "INVALID_INPUT", (
                f"Expected INVALID_INPUT, got {data['error']['code']}"
            )
        except (ToolError, Exception) as exc:
            # FastMCP Pydantic validation raised ToolError — the input was rejected
            # This is the correct behavior (invalid enum value rejected at MCP layer)
            err_msg = str(exc).lower()
            assert "potash" in err_msg or "literal" in err_msg or "invalid" in err_msg or "gold" in err_msg, (
                f"ToolError for invalid mineral must mention the constraint. Got: {exc}"
            )


# ─── Nova Scotia scenarios ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestNovaScotiaToolScenarios:
    """Live data.novascotia.ca Socrata SODA integration tests.

    THE MANITOBA LESSON: every test here asserts FIELD PRESENCE + non-null values,
    not just _meta shape. This catches a live 400 or wrong-endpoint bug that mocks
    would mask.

    Tests simulate what an agent would ask:
    - Marine leases: license_le non-null + the_geom ABSENT (geometry-exclusion proof)
    - Hatchery stocking: stock/number_released non-null (field presence)
    - Aquaculture production: kgs/total_value non-null (field presence)
    - Water quality: temperature_c non-null (field presence)
    - Boil water: no error envelope; empty list is VALID success
    - Protected areas: pro_name non-null + the_geom ABSENT (geometry-exclusion proof)
    - Air quality stations: station_name/latitude non-null (field presence)
    - Health facilities: facility_name non-null (both hospital and LTC)
    - Vital statistics: counties/live_births non-null (field presence)
    - Chronic disease: zone + crude_prevalence_rate non-null (zone normalization proof)
    - Categories: >=20 categories incl. "Fishing and Aquaculture" (broken-param workaround proof)
    - Discovery: ns_search_datasets returns h57h-p9mm (catalog search)
    - Error: invalid disease/facility_type → structured INVALID_INPUT (not an exception)
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_marine_leases_license_le_and_no_the_geom(self, mcp_server):
        """'Nova Scotia marine aquaculture leases (Shellfish)' — license_le non-null, the_geom ABSENT.

        THE GEOMETRY EXCLUSION PROOF: if the_geom appears in any row, the $select exclusion
        or belt-and-suspenders strip is broken. This is the primary validation for Socrata
        geometry handling.
        """
        data = await call_tool(mcp_server, "ns_get_marine_aquaculture_leases", {
            "species_type": "Shellfish",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success from ns_get_marine_aquaculture_leases, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        leases = data["data"]["leases"]
        assert isinstance(leases, list)
        assert len(leases) >= 1, "Marine leases must return at least 1 Shellfish lease"
        # FIELD PRESENCE: license_le must be non-null in at least one row
        first = leases[0]
        assert first.get("license_le") is not None, (
            f"FIELD PRESENCE FAILED: 'license_le' must be non-null in first lease row. "
            f"Got keys: {list(first.keys())}"
        )
        # GEOMETRY EXCLUSION: the_geom must NOT appear in any row
        for row in leases:
            assert "the_geom" not in row, (
                f"GEOMETRY EXCLUSION FAILED: 'the_geom' must not be in lease rows — "
                f"found it in row with license_le={row.get('license_le')!r}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_fish_hatchery_stocking_field_presence(self, mcp_server):
        """'Nova Scotia hatchery stocking for Brook Trout' — stock/number_released non-null."""
        data = await call_tool(mcp_server, "ns_get_fish_hatchery_stocking", {
            "stock": "Brook Trout",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success from ns_get_fish_hatchery_stocking, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        records = data["data"]["stocking_records"]
        assert isinstance(records, list)
        assert len(records) >= 1, "Hatchery stocking must return at least 1 Brook Trout record"
        first = records[0]
        # FIELD PRESENCE
        assert first.get("stock") is not None, (
            f"FIELD PRESENCE FAILED: 'stock' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("number_released") is not None, (
            f"FIELD PRESENCE FAILED: 'number_released' must be non-null. Got: {first}"
        )
        assert first.get("stocking_date") is not None, (
            f"FIELD PRESENCE FAILED: 'stocking_date' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_aquaculture_production_kgs_and_total_value(self, mcp_server):
        """'NS aquaculture production' — kgs/total_value non-null in at least one row."""
        data = await call_tool(mcp_server, "ns_get_aquaculture_production", {
            "limit": 10,
        })
        assert "_meta" in data, f"Expected live success from ns_get_aquaculture_production, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        production = data["data"]["production"]
        assert isinstance(production, list)
        assert len(production) >= 1, "Aquaculture production must return at least 1 row"
        # FIELD PRESENCE: kgs and total_value must be non-null in at least one row
        rows_with_kgs = [r for r in production if r.get("kgs") is not None]
        assert len(rows_with_kgs) >= 1, (
            f"FIELD PRESENCE FAILED: 'kgs' must be non-null in >=1 row. "
            f"Keys in first row: {list(production[0].keys())}"
        )
        rows_with_value = [r for r in production if r.get("total_value") is not None]
        assert len(rows_with_value) >= 1, (
            f"FIELD PRESENCE FAILED: 'total_value' must be non-null in >=1 row. "
            f"Keys in first row: {list(production[0].keys())}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_water_quality_temperature_c_field_present(self, mcp_server):
        """'NS water quality monitoring' — temperature_c non-null in at least one reading."""
        data = await call_tool(mcp_server, "ns_get_water_quality_monitoring", {
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success from ns_get_water_quality_monitoring, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        readings = data["data"]["readings"]
        assert isinstance(readings, list)
        assert len(readings) >= 1, "Water quality must return at least 1 reading"
        first = readings[0]
        # FIELD PRESENCE: station_number and date must be non-null
        assert first.get("station_number") is not None, (
            f"FIELD PRESENCE FAILED: 'station_number' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("date") is not None, (
            f"FIELD PRESENCE FAILED: 'date' must be non-null. Got: {first}"
        )
        # temperature_c must be non-null in at least one row
        temp_rows = [r for r in readings if r.get("temperature_c") is not None]
        assert len(temp_rows) >= 1, (
            f"FIELD PRESENCE FAILED: 'temperature_c' must be non-null in >=1 row. "
            f"Got keys: {list(readings[0].keys())}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_boil_water_advisories_empty_is_valid_not_error(self, mcp_server):
        """'NS boil water advisories (active only)' — empty list is a valid success, not an error.

        THE EMPTY-IS-VALID LESSON: if no active advisories, the response must have _meta
        (not an error envelope). This mirrors Manitoba flood alerts and SK fire bans.
        """
        data = await call_tool(mcp_server, "ns_get_boil_water_advisories", {
            "active_only": True,
            "limit": 200,
        })
        # Must NOT be an error — empty advisory list is normal off-season state
        assert "error" not in data, (
            f"Boil water advisories MUST NOT return error on empty list. Got: {data.get('error')}"
        )
        assert "_meta" in data, (
            f"Boil water advisories must return _meta envelope (even with 0 advisories). Got: {data}"
        )
        advisories = data["data"]["advisories"]
        assert isinstance(advisories, list)
        count = data["data"].get("count", -1)
        assert count >= 0, f"Boil water count must be >= 0, got {count}"
        # If advisories present, assert field presence
        if advisories:
            first = advisories[0]
            assert first.get("site_name") is not None, (
                f"FIELD PRESENCE FAILED: 'site_name' must be non-null when advisories present. Got: {first}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_protected_areas_pro_name_and_no_the_geom(self, mcp_server):
        """'NS protected areas (Designated)' — pro_name non-null, the_geom ABSENT.

        THE GEOMETRY EXCLUSION PROOF for protected areas (ticv-5du5): proves both the
        explicit $select and belt-and-suspenders strip work on the MultiPolygon dataset.
        """
        data = await call_tool(mcp_server, "ns_get_protected_areas", {
            "status": "Designated",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success from ns_get_protected_areas, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        areas = data["data"]["protected_areas"]
        assert isinstance(areas, list)
        assert len(areas) >= 1, "Protected areas must return at least 1 Designated area"
        first = areas[0]
        # FIELD PRESENCE
        assert first.get("pro_name") is not None, (
            f"FIELD PRESENCE FAILED: 'pro_name' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("protect1") is not None or first.get("owner") is not None, (
            f"FIELD PRESENCE FAILED: 'protect1' or 'owner' must be present. Got: {first}"
        )
        # GEOMETRY EXCLUSION: the_geom must NOT appear in any row
        for row in areas:
            assert "the_geom" not in row, (
                f"GEOMETRY EXCLUSION FAILED: 'the_geom' must not appear in protected area rows. "
                f"Found in row with pro_name={row.get('pro_name')!r}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_air_quality_stations_name_and_coordinates(self, mcp_server):
        """'NS air quality stations' — station_name/latitude/longitude non-null."""
        data = await call_tool(mcp_server, "ns_get_air_quality_stations", {
            "limit": 10,
        })
        assert "_meta" in data, f"Expected live success from ns_get_air_quality_stations, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        stations = data["data"]["stations"]
        assert isinstance(stations, list)
        assert len(stations) >= 1, "Air quality stations must return at least 1 station"
        first = stations[0]
        # FIELD PRESENCE
        assert first.get("station_name") is not None, (
            f"FIELD PRESENCE FAILED: 'station_name' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("latitude") is not None, (
            f"FIELD PRESENCE FAILED: 'latitude' must be non-null. Got: {first}"
        )
        assert first.get("longitude") is not None, (
            f"FIELD PRESENCE FAILED: 'longitude' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_health_facilities_hospital_field_presence(self, mcp_server):
        """'NS hospitals' — facility_name/county/type non-null (live 200 required)."""
        data = await call_tool(mcp_server, "ns_get_health_facilities", {
            "facility_type": "hospital",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        facilities = data["data"]["facilities"]
        assert isinstance(facilities, list)
        assert len(facilities) >= 1, "Hospital facilities must return at least 1 hospital"
        first = facilities[0]
        # FIELD PRESENCE — all three must be non-null from the normalized output
        assert first.get("facility_name") is not None, (
            f"FIELD PRESENCE FAILED: 'facility_name' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("county") is not None, (
            f"FIELD PRESENCE FAILED: 'county' must be non-null. Got: {first}"
        )
        assert first.get("type") is not None, (
            f"FIELD PRESENCE FAILED: 'type' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_health_facilities_ltc_beds_and_zone(self, mcp_server):
        """'NS long-term care facilities' — beds/zone/facility_name present (live 200 required)."""
        data = await call_tool(mcp_server, "ns_get_health_facilities", {
            "facility_type": "long_term_care",
            "limit": 10,
        })
        assert "_meta" in data, f"Expected live success, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        facilities = data["data"]["facilities"]
        assert isinstance(facilities, list)
        assert len(facilities) >= 1, "LTC facilities must return at least 1 facility"
        first = facilities[0]
        assert first.get("facility_name") is not None, (
            f"FIELD PRESENCE FAILED: 'facility_name' must be non-null. Got: {first}"
        )
        # FIELD PRESENCE: beds and zone should be present in LTC data
        rows_with_beds = [f for f in facilities if f.get("beds") is not None]
        assert len(rows_with_beds) >= 1, (
            f"FIELD PRESENCE FAILED: 'beds' must be non-null in >=1 LTC row. "
            f"Keys in first row: {list(facilities[0].keys())}"
        )
        rows_with_zone = [f for f in facilities if f.get("zone") is not None]
        assert len(rows_with_zone) >= 1, (
            f"FIELD PRESENCE FAILED: 'zone' must be non-null in >=1 LTC row. "
            f"Keys in first row: {list(facilities[0].keys())}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_vital_statistics_live_births_field_present(self, mcp_server):
        """'NS vital statistics' — counties/year/population/live_births non-null."""
        data = await call_tool(mcp_server, "ns_get_vital_statistics", {
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success from ns_get_vital_statistics, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        # Key is "statistics" (set by fetch_vital_statistics client function)
        payload = data["data"]
        stats = payload.get("statistics") or payload.get("vital_stats") or []
        assert isinstance(stats, list), (
            f"Vital statistics response data must contain 'statistics' list. Got keys: {list(payload.keys())}"
        )
        assert len(stats) >= 1, "Vital statistics must return at least 1 row"
        first = stats[0]
        # FIELD PRESENCE: counties + year + live_births must be non-null
        assert first.get("counties") is not None, (
            f"FIELD PRESENCE FAILED: 'counties' (UPPERCASE field name) must be non-null. "
            f"Got keys: {list(first.keys())} — if 'county' appears instead of 'counties', "
            f"the Pitfall 4 schema fix is missing."
        )
        assert first.get("live_births") is not None, (
            f"FIELD PRESENCE FAILED: 'live_births' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_chronic_disease_zone_and_prevalence_rate(self, mcp_server):
        """'NS chronic disease AMI' — year/zone/crude_prevalence_rate non-null.

        THE ZONE NORMALIZATION PROOF: AMI uses 'health_zone' in the source dataset but
        client _normalize_zone_field must rename it to 'zone' in the output. If 'zone' is
        absent and 'health_zone' appears instead, normalization is broken.

        Queried WITHOUT a sex filter: AMI has no sex column, so filtering by it
        returns nothing and used to leave this proof unasserted. The sex-filter
        behaviour is covered separately below.
        """
        data = await call_tool(mcp_server, "ns_get_chronic_disease_prevalence", {
            "disease": "ami",
            "limit": 5,
        })
        assert "_meta" in data, f"Expected live success, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"

        rows = data["data"]["rows"]
        assert rows, (
            f"AMI is a published NS chronic-disease dataset — an empty result "
            f"means the query is broken: {data['data']}"
        )
        first = rows[0]
        # ZONE NORMALIZATION PROOF: 'zone' must be present (not 'health_zone')
        assert "zone" in first, (
            f"ZONE NORMALIZATION FAILED: 'zone' must be in the output (AMI source uses "
            f"'health_zone' renamed to 'zone' by _normalize_zone_field). "
            f"Got keys: {list(first.keys())}"
        )
        assert first.get("zone") is not None, (
            f"FIELD PRESENCE FAILED: 'zone' must be non-null. Got: {first}"
        )
        assert first.get("crude_prevalence_rate") is not None, (
            f"FIELD PRESENCE FAILED: 'crude_prevalence_rate' must be non-null. Got: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    @pytest.mark.tolerates_upstream_error(
        reason="AMI has no sex column upstream, so Socrata may 400 on the filter "
               "or return zero rows; both are correct answers for this dataset"
    )
    async def test_chronic_disease_sex_filter_on_dataset_without_sex(self, mcp_server):
        """'AMI prevalence for women' — documents that AMI carries no sex breakdown.

        Kept as an explicit exemption rather than folded into the zone-normalization
        test above, where it silently skipped the proof whenever the filter matched
        nothing.
        """
        data = await call_tool(mcp_server, "ns_get_chronic_disease_prevalence", {
            "disease": "ami",
            "sex": "F",
            "limit": 5,
        })
        if "error" in data:
            assert data["error"]["code"] in ("UPSTREAM_ERROR", "INVALID_INPUT"), (
                f"a filter on a nonexistent column should surface as an upstream "
                f"or input error, got: {data['error']}"
            )
        else:
            assert isinstance(data["data"]["rows"], list), (
                f"a non-matching filter must still return a rows list: {data['data']}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_categories_20_plus_including_fishing(self, mcp_server):
        """'NS data categories' — >=20 categories incl. 'Fishing and Aquaculture'.

        THE CATEGORIES= WORKAROUND PROOF: ns_list_categories uses q='' + client-side
        domain_category aggregation (not the broken categories= param which returns 0
        results). If this returns <20 categories or lacks "Fishing and Aquaculture",
        the workaround is broken.
        """
        data = await call_tool(mcp_server, "ns_list_categories", {})
        assert "_meta" in data, f"Expected live success from ns_list_categories, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        categories = data["data"]["categories"]
        assert isinstance(categories, list)
        # THE PROOF: at least 20 categories (confirms workaround works)
        assert len(categories) >= 20, (
            f"CATEGORIES WORKAROUND FAILED: Expected >=20 categories but got {len(categories)}. "
            f"If categories= API param was used (not q=), it returns 0. Got: {categories}"
        )
        # 'Fishing and Aquaculture' must be present
        category_names = [c["name"] for c in categories]
        assert "Fishing and Aquaculture" in category_names, (
            f"FIELD PRESENCE FAILED: 'Fishing and Aquaculture' must be in categories. "
            f"Got: {sorted(category_names)}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_ns_search_datasets(self, mcp_server):
        """'Nova Scotia aquaculture data' — BM25 must surface ns_search_datasets."""
        results = await discover(mcp_server, "Nova Scotia aquaculture data")
        names = [r["name"] for r in results]
        assert any(n.startswith("ns_") for n in names), (
            f"No ns_ tool found in BM25 discovery results for 'Nova Scotia aquaculture data': {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_datasets_returns_h57h_p9mm(self, mcp_server):
        """'Search NS datasets for aquaculture' — must return h57h-p9mm (marine leases dataset).

        PROVES catalog search + pagination works. If h57h-p9mm is absent, the SODA
        /api/catalog/v1 endpoint or query parsing is broken.
        """
        data = await call_tool(mcp_server, "ns_search_datasets", {
            "query": "aquaculture",
            "limit": 20,
        })
        assert "_meta" in data, f"Expected live success from ns_search_datasets, got: {data}"
        assert data["_meta"]["source"]["api"] == "nova-scotia-socrata"
        results = data["data"]["results"]
        total = data["data"]["total"]
        assert isinstance(results, list)
        assert total >= 10, (
            f"Expected total>=10 aquaculture datasets on NS Socrata, got {total}"
        )
        # h57h-p9mm (Marine Aquaculture Leases) must appear in results
        ids = [r["id"] for r in results if "id" in r]
        assert "h57h-p9mm" in ids, (
            f"CATALOG SEARCH FAILED: 'h57h-p9mm' (Marine Aquaculture Leases) must appear "
            f"in top 20 aquaculture results. Got IDs: {ids}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_invalid_disease_returns_structured_error(self, mcp_server):
        """Invalid disease 'tuberculosis' → INVALID_INPUT with valid= list (not an exception)."""
        data = await call_tool(mcp_server, "ns_get_chronic_disease_prevalence", {
            "disease": "tuberculosis",
        })
        assert "error" in data, (
            f"Invalid disease must return error envelope, got: {data}"
        )
        assert data["error"]["code"] == "INVALID_INPUT", (
            f"Expected INVALID_INPUT for invalid disease, got {data['error']['code']}"
        )
        assert "valid" in data["error"], (
            f"INVALID_INPUT must include 'valid=' list. Got: {data['error']}"
        )
        assert "ami" in data["error"]["valid"], (
            f"valid= list must include 'ami'. Got: {data['error']['valid']}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_invalid_facility_type_returns_structured_error(self, mcp_server):
        """Invalid facility_type 'clinic' → INVALID_INPUT with valid= list (not an exception)."""
        data = await call_tool(mcp_server, "ns_get_health_facilities", {
            "facility_type": "clinic",
        })
        assert "error" in data, (
            f"Invalid facility_type must return error envelope, got: {data}"
        )
        assert data["error"]["code"] == "INVALID_INPUT", (
            f"Expected INVALID_INPUT for 'clinic', got {data['error']['code']}"
        )
        assert "valid" in data["error"], (
            f"INVALID_INPUT must include 'valid=' list. Got: {data['error']}"
        )
        assert "hospital" in data["error"]["valid"], (
            f"valid= list must include 'hospital'. Got: {data['error']['valid']}"
        )


# ─── New Brunswick scenarios ─────────────────────────────────────────────────


class TestNewBrunswickToolScenarios:
    """Live geonb.snb.ca / open.canada.ca / gnb.socrata.com integration tests.

    All 22 nb_ tools are exercised through the MCP Client layer, the way an
    agent uses them — never a direct client-function import. A meta-test at
    the bottom binds constants.ALL_NB_TOOL_NAMES to the tool names this class
    actually invokes, so a future 23rd tool cannot ship untested.

    Tests simulate what an agent would ask:
    - 'What New Brunswick datasets are there about flooding?' — dataset search
    - 'Show me the details of that New Brunswick dataset' — dataset details, FR title
    - 'What data formats does New Brunswick publish?' — category listing
    - 'What map services does GeoNB have?' — service listing, no basemap leaked
    - 'Which layer of the Crown Land service holds the parcels?' — layer 3
    - 'Where are New Brunswick's flood hazard areas?' — Flood_Haza field present
    - 'Where did the Saint John River flood historically?' — historical floods
    - 'What wetlands are classified as bog?' — wetlands with a filter
    - 'Show me contaminated sites in New Brunswick' — bilingual status
    - 'Who holds this Crown land?' — HOLDER + OBJECTID fields
    - 'What parcels are in York County?' — parcels with a filter
    - 'Show me every New Brunswick parcel' — parcels unfiltered, INVALID_INPUT
    - 'What is the civic address for this street in Fredericton?' — civic addresses
    - 'List every civic address in New Brunswick' — unfiltered, INVALID_INPUT
    - 'Where are New Brunswick's hospitals?' — bilingual Name_E/Name_F
    - 'What anglophone schools are in New Brunswick?' — public schools
    - 'Are there road closures in New Brunswick?' — unconfigured envelope
    - 'What are winter road conditions in New Brunswick?' — unconfigured
    - 'Show me New Brunswick traffic cameras' — unconfigured
    - 'Find me New Brunswick government data tools' — BM25 discovery
    - a cross-module scenario pairing an nb_ tool with the federal ckan_ module
    - the gnb.socrata.com discovery pair (checkpoint option-a)
    - the long-tail escape hatch reaching mineral occurrences (dropped by the
      21-01 checkpoint, still reachable via nb_query_geonb_layer)
    """

    # ------------------------------------------------------------------
    # Federal CKAN discovery (organization:nb) — D-01
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_datasets_about_flooding(self, mcp_server):
        """'What New Brunswick datasets are there about flooding?'"""
        data = await call_tool(mcp_server, "nb_search_datasets", {"query": "flood", "limit": 5})
        live = assert_live_or_transient(data, "nb_search_datasets", "new-brunswick-federal-ckan")
        if live:
            payload = data["data"]
            assert "results" in payload and isinstance(payload["results"], list)
            results = payload["results"]
            assert results, f"nb_search_datasets('flood') must return at least 1 dataset, got: {payload}"
            assert results[0].get("id") is not None, (
                f"FIELD PRESENCE FAILED: 'id' must be non-null. Got: {results[0]}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_dataset_details_bilingual_title(self, mcp_server):
        """'Show me the details of that New Brunswick dataset' — French title resolution."""
        search = await call_tool(mcp_server, "nb_search_datasets", {"query": "flood", "limit": 5})
        live = assert_live_or_transient(search, "nb_search_datasets", "new-brunswick-federal-ckan")
        if live:
            results = search["data"]["results"]
            assert results, f"nb_search_datasets('flood') must return at least 1 dataset, got: {search['data']}"
            dataset_id = results[0]["name"] or results[0]["id"]

            data_en = await call_tool(
                mcp_server, "nb_get_dataset_details", {"dataset_id": dataset_id, "lang": "en"}
            )
            live_en = assert_live_or_transient(data_en, "nb_get_dataset_details", "new-brunswick-federal-ckan")
            assert live_en, (
                f"nb_get_dataset_details must succeed for a dataset just returned by search: {data_en}"
            )
            assert data_en["data"].get("title") is not None, (
                f"FIELD PRESENCE FAILED: 'title' must be non-null. Got: {data_en['data']}"
            )

            data_fr = await call_tool(
                mcp_server, "nb_get_dataset_details", {"dataset_id": dataset_id, "lang": "fr"}
            )
            live_fr = assert_live_or_transient(data_fr, "nb_get_dataset_details", "new-brunswick-federal-ckan")
            assert live_fr, f"nb_get_dataset_details (fr) must succeed for the same dataset: {data_fr}"
            assert data_fr["_meta"]["lang"] == "fr"
            assert data_fr["data"].get("title") is not None, (
                f"FIELD PRESENCE FAILED (fr): 'title' must be non-null. Got: {data_fr['data']}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(60)
    async def test_query_dataset_resource(self, mcp_server):
        """'Pull the rows out of that New Brunswick resource' — auto-router, never an error."""
        search = await call_tool(mcp_server, "nb_search_datasets", {"query": "flood", "limit": 5})
        live = assert_live_or_transient(search, "nb_search_datasets", "new-brunswick-federal-ckan")
        if live:
            results = search["data"]["results"]
            assert results, f"nb_search_datasets('flood') must return at least 1 dataset, got: {search['data']}"
            dataset_id = next((r["name"] or r["id"] for r in results if r.get("num_resources")), None)
            if dataset_id is None:
                dataset_id = results[0]["name"] or results[0]["id"]

            data = await call_tool(
                mcp_server, "nb_query_dataset", {"dataset_id": dataset_id, "resource_index": 0}
            )
            live_q = assert_live_or_transient(data, "nb_query_dataset", "new-brunswick-federal-ckan")
            if live_q:
                payload = data["data"]
                # Auto-router: either parsed rows, or a metadata-only note naming
                # the download url — both are success outcomes, never an error.
                assert "rows" in payload, f"nb_query_dataset payload missing 'rows': {payload}"
                assert isinstance(payload["rows"], list)
                assert "resource" in payload, f"nb_query_dataset payload missing 'resource': {payload}"

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_organizations(self, mcp_server):
        """'Who publishes New Brunswick's federal CKAN data?'"""
        data = await call_tool(mcp_server, "nb_list_organizations", {})
        live = assert_live_or_transient(data, "nb_list_organizations", "new-brunswick-federal-ckan")
        if live:
            orgs = data["data"]["organizations"]
            assert isinstance(orgs, list) and len(orgs) >= 1
            assert orgs[0].get("name") is not None, (
                f"FIELD PRESENCE FAILED: 'name' must be non-null. Got: {orgs[0]}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_categories_format_list(self, mcp_server):
        """'What data formats does New Brunswick publish?'"""
        data = await call_tool(mcp_server, "nb_list_categories", {})
        live = assert_live_or_transient(data, "nb_list_categories", "new-brunswick-federal-ckan")
        if live:
            payload = data["data"]
            assert "formats" in payload, f"nb_list_categories payload missing 'formats': {payload}"
            formats = payload["formats"]
            assert isinstance(formats, list) and len(formats) >= 1, (
                f"FIELD PRESENCE FAILED: 'formats' must be a non-empty list. Got: {formats}"
            )
            assert formats[0].get("name") is not None

    # ------------------------------------------------------------------
    # gnb.socrata.com — checkpoint option-a
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_search_gnb_socrata_datasets(self, mcp_server):
        """'Search New Brunswick's provincial Socrata portal' — gnb.socrata.com, keyless."""
        data = await call_tool(mcp_server, "nb_search_gnb_socrata_datasets", {"query": "", "limit": 10})
        live = assert_live_or_transient(data, "nb_search_gnb_socrata_datasets", "new-brunswick-gnb-socrata")
        if live:
            payload = data["data"]
            assert "results" in payload and isinstance(payload["results"], list)
            assert payload.get("total", 0) >= 1, (
                f"FIELD PRESENCE FAILED: total must be >=1 across gnb.socrata.com's 312 datasets. Got: {payload}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_query_gnb_socrata_dataset(self, mcp_server):
        """'Query a New Brunswick provincial Socrata dataset via SoQL.'"""
        search = await call_tool(mcp_server, "nb_search_gnb_socrata_datasets", {"query": "", "limit": 10})
        live = assert_live_or_transient(search, "nb_search_gnb_socrata_datasets", "new-brunswick-gnb-socrata")
        if live:
            results = search["data"]["results"]
            assert results, "gnb.socrata.com must return at least one dataset for an empty query"
            dataset_id = results[0]["id"]

            data = await call_tool(
                mcp_server, "nb_query_gnb_socrata_dataset", {"dataset_id": dataset_id, "limit": 5}
            )
            live_q = assert_live_or_transient(data, "nb_query_gnb_socrata_dataset", "new-brunswick-gnb-socrata")
            if live_q:
                payload = data["data"]
                assert "rows" in payload and isinstance(payload["rows"], list)
                for row in payload["rows"]:
                    assert not any(k.lower().startswith("the_geom") for k in row), (
                        f"GEOMETRY EXCLUSION FAILED: no the_geom* key expected by default. Got keys: {list(row)}"
                    )

    # ------------------------------------------------------------------
    # GeoNB discovery — stands in for the 401-ing Hub Search API (D-06)
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_list_geonb_services_no_basemap_leaked(self, mcp_server):
        """'What map services does GeoNB have?' — no basemap tile service by default."""
        data = await call_tool(mcp_server, "nb_list_geonb_services", {})
        assert "_meta" in data, f"Expected live success from nb_list_geonb_services, got: {data}"
        assert data["_meta"]["source"]["api"] == "new-brunswick-geonb"
        services = data["data"]["services"]
        assert isinstance(services, list) and len(services) >= 1
        names = [s["name"] for s in services]
        assert not any("Basemap" in n for n in names), (
            f"EXCLUSION FAILED: no basemap service should appear by default. Got: {names}"
        )
        assert "GeoNB_DNR_WildlifeRefuges" not in names, (
            "EXCLUSION FAILED: the retired placeholder service must be hidden by default"
        )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_crown_land_service_layers_layer_3(self, mcp_server):
        """'Which layer of the Crown Land service holds the parcels?' — layer 3, never 0."""
        data = await call_tool(mcp_server, "nb_get_geonb_service_layers", {
            "service_name": "GeoNB_DNR_Crown_Land",
        })
        assert "_meta" in data, f"Expected live success from nb_get_geonb_service_layers, got: {data}"
        assert data["_meta"]["source"]["api"] == "new-brunswick-geonb"
        layers = data["data"]["layers"]
        assert isinstance(layers, list) and len(layers) >= 1
        layer_ids = [layer["id"] for layer in layers]
        assert 3 in layer_ids, (
            f"LAYER ID PROOF FAILED: Crown Land's real layer id is 3 (layer 0 does not exist "
            f"on this service). Got layer ids: {layer_ids}"
        )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_query_geonb_layer_reaches_mineral_occurrences(self, mcp_server):
        """'Find New Brunswick mineral occurrences' — the long-tail escape hatch.

        nb_get_mineral_occurrences was dropped to the long tail by the 21-01
        checkpoint (option-a, tool-budget tradeoff) — this proves it stayed
        reachable via nb_query_geonb_layer rather than becoming unreachable.
        """
        data = await call_tool(mcp_server, "nb_query_geonb_layer", {
            "service_name": "GeoNB_DNR_MineralOccurrences",
            "layer_id": 0,
            "limit": 10,
        })
        live = assert_live_or_transient(data, "nb_query_geonb_layer", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_query_geonb_layer")
            assert len(payload["features"]) >= 1, (
                "GeoNB_DNR_MineralOccurrences layer 0 must return at least 1 feature "
                "(1,611 points recorded in COVERAGE.md)"
            )

    # ------------------------------------------------------------------
    # Curated flood / water
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_flood_hazard_areas_field_present(self, mcp_server):
        """'Where are New Brunswick's flood hazard areas?' — Flood_Haza field present."""
        data = await call_tool(mcp_server, "nb_get_flood_hazard_areas", {"limit": 25})
        live = assert_live_or_transient(data, "nb_get_flood_hazard_areas", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_flood_hazard_areas")
            assert len(payload["features"]) >= 1, "Flood hazard index must return at least 1 polygon"
            hazard_rows = [f for f in payload["features"] if f.get("Flood_Haza") is not None]
            assert len(hazard_rows) >= 1, (
                f"FIELD PRESENCE FAILED: 'Flood_Haza' must be non-null in >=1 row. "
                f"Keys in first row: {list(payload['features'][0].keys())}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_historical_floods_1973_event(self, mcp_server):
        """'Where did the Saint John River flood historically?' — the 1973 event, layer 8."""
        data = await call_tool(mcp_server, "nb_get_historical_floods", {"event": "1973", "limit": 25, "lang": "fr"})
        live = assert_live_or_transient(data, "nb_get_historical_floods", "new-brunswick-geonb")
        if live:
            assert data["_meta"]["lang"] == "fr"
            payload = assert_feature_payload(data, "nb_get_historical_floods")
            assert len(payload["features"]) >= 1, "The 1973 historical flood layer must return >=1 feature"

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wetlands_bog_filter(self, mcp_server):
        """'What wetlands are classified as bog?' — wetlands with a filter."""
        data = await call_tool(mcp_server, "nb_get_wetlands", {"wetland_class": "Bog", "limit": 10})
        live = assert_live_or_transient(data, "nb_get_wetlands", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_wetlands")
            assert len(payload["features"]) >= 1, "wetland_class='Bog' must return at least 1 polygon"
            assert all(f.get("WETLAND_CLASS") == "Bog" for f in payload["features"]), (
                f"FILTER FAILED: every row must have WETLAND_CLASS=='Bog'. "
                f"Got: {[f.get('WETLAND_CLASS') for f in payload['features']]}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wetlands_unfiltered_returns_invalid_input(self, mcp_server):
        """'Show me every New Brunswick wetland' — unfiltered call rejected (163,206 rows)."""
        data = await call_tool(mcp_server, "nb_get_wetlands", {})
        assert "error" in data, f"Unfiltered nb_get_wetlands must be rejected, got: {data}"
        assert data["error"]["code"] == "INVALID_INPUT", (
            f"Expected INVALID_INPUT for an unfiltered wetlands call, got {data['error']['code']}"
        )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_contaminated_sites_bilingual_status(self, mcp_server):
        """'Show me contaminated sites in New Brunswick' — bilingual status fields."""
        data = await call_tool(mcp_server, "nb_get_contaminated_sites", {"limit": 25})
        live = assert_live_or_transient(data, "nb_get_contaminated_sites", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_contaminated_sites")
            assert len(payload["features"]) >= 1, "Contaminated sites must return at least 1 point"
            first = payload["features"][0]
            assert first.get("Status_E") is not None, (
                f"FIELD PRESENCE FAILED: 'Status_E' must be non-null. Keys: {list(first.keys())}"
            )
            assert first.get("Status_F") is not None, (
                f"FIELD PRESENCE FAILED: 'Status_F' must be non-null. Got: {first}"
            )
            # Code-review fix F4: Latitude/Longitude must be in the projection
            # so a returned site can actually be located on a map.
            assert "Latitude" in first, (
                f"FIELD PRESENCE FAILED: 'Latitude' must be in the out_fields "
                f"projection. Keys: {list(first.keys())}"
            )
            assert "Longitude" in first, (
                f"FIELD PRESENCE FAILED: 'Longitude' must be in the out_fields "
                f"projection. Keys: {list(first.keys())}"
            )

    # ------------------------------------------------------------------
    # Crown land — the phase tracer
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_crown_land_holder_and_object_id(self, mcp_server):
        """'Who holds this Crown land?' — HOLDER + OBJECTID fields, layer 3."""
        data = await call_tool(mcp_server, "nb_get_crown_land", {"limit": 25})
        assert "_meta" in data, f"Expected live success from nb_get_crown_land, got: {data}"
        assert data["_meta"]["source"]["api"] == "new-brunswick-geonb"
        payload = assert_feature_payload(data, "nb_get_crown_land")
        assert len(payload["features"]) >= 1, "Crown Land layer 3 must return at least 1 parcel"
        first = payload["features"][0]
        assert first.get("OBJECTID") is not None, (
            f"FIELD PRESENCE FAILED: 'OBJECTID' must be non-null. Keys: {list(first.keys())}"
        )
        assert first.get("HOLDER") is not None, (
            f"FIELD PRESENCE FAILED: 'HOLDER' must be non-null. Got: {first}"
        )

    # ------------------------------------------------------------------
    # Parcels / civic addresses — the geocoding pair, both filter-required
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_parcels_in_york_county(self, mcp_server):
        """'What parcels are in York County?' — parcels with a filter."""
        data = await call_tool(mcp_server, "nb_get_parcels", {"county": "YORK", "limit": 25})
        live = assert_live_or_transient(data, "nb_get_parcels", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_parcels")
            assert len(payload["features"]) >= 1, "county='YORK' must return at least 1 parcel"
            assert all("york" in (f.get("COUNTY") or "").lower() for f in payload["features"]), (
                f"FILTER FAILED: every row's COUNTY must contain 'york'. "
                f"Got: {[f.get('COUNTY') for f in payload['features']]}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_parcels_unfiltered_returns_invalid_input(self, mcp_server):
        """'Show me every New Brunswick parcel' — unfiltered call rejected (604,520 rows)."""
        data = await call_tool(mcp_server, "nb_get_parcels", {})
        assert "error" in data, f"Unfiltered nb_get_parcels must be rejected, got: {data}"
        assert data["error"]["code"] == "INVALID_INPUT", (
            f"Expected INVALID_INPUT for an unfiltered parcels call, got {data['error']['code']}"
        )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_civic_address_in_fredericton(self, mcp_server):
        """'What is the civic address for this street in Fredericton?' — bilingual street type."""
        data = await call_tool(mcp_server, "nb_get_civic_addresses", {"community": "FREDERICTON", "limit": 25})
        live = assert_live_or_transient(data, "nb_get_civic_addresses", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_civic_addresses")
            assert len(payload["features"]) >= 1, "community='FREDERICTON' must return at least 1 address"
            first = payload["features"][0]
            assert first.get("ST_TYPE_E") is not None, (
                f"FIELD PRESENCE FAILED: 'ST_TYPE_E' must be non-null. Keys: {list(first.keys())}"
            )
            assert first.get("ST_TYPE_F") is not None, (
                f"FIELD PRESENCE FAILED: 'ST_TYPE_F' must be non-null. Got: {first}"
            )
            # Code-review fix F5: LATITUDE/LONGITUDE/COUNTY/PID must be in the
            # projection so the documented address -> point / address ->
            # parcel geocoding workflow is actually completable.
            for field in ("LATITUDE", "LONGITUDE", "COUNTY", "PID"):
                assert field in first, (
                    f"FIELD PRESENCE FAILED: '{field}' must be in the out_fields "
                    f"projection. Keys: {list(first.keys())}"
                )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_civic_addresses_unfiltered_returns_invalid_input(self, mcp_server):
        """'List every civic address in New Brunswick' — unfiltered call rejected (373,172 rows)."""
        data = await call_tool(mcp_server, "nb_get_civic_addresses", {})
        assert "error" in data, f"Unfiltered nb_get_civic_addresses must be rejected, got: {data}"
        assert data["error"]["code"] == "INVALID_INPUT", (
            f"Expected INVALID_INPUT for an unfiltered civic-address call, got {data['error']['code']}"
        )

    # ------------------------------------------------------------------
    # Health / education dispatch tools
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_health_facilities_bilingual_hospital_names(self, mcp_server):
        """'Where are New Brunswick's hospitals?' — both official-language name fields."""
        data = await call_tool(mcp_server, "nb_get_health_facilities", {
            "facility_type": "hospital_horizon",
            "limit": 25,
        })
        live = assert_live_or_transient(data, "nb_get_health_facilities", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_health_facilities")
            assert len(payload["features"]) >= 1, "hospital_horizon must return at least 1 facility"
            first = payload["features"][0]
            assert first.get("Name_E") is not None, (
                f"FIELD PRESENCE FAILED: 'Name_E' must be non-null. Keys: {list(first.keys())}"
            )
            assert first.get("Name_F") is not None, (
                f"FIELD PRESENCE FAILED: 'Name_F' must be non-null. Got: {first}"
            )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_public_schools_anglophone(self, mcp_server):
        """'What anglophone schools are in New Brunswick?'"""
        data = await call_tool(mcp_server, "nb_get_public_schools", {"sector": "anglophone", "limit": 25})
        live = assert_live_or_transient(data, "nb_get_public_schools", "new-brunswick-geonb")
        if live:
            payload = assert_feature_payload(data, "nb_get_public_schools")
            assert len(payload["features"]) >= 1, "anglophone sector must return at least 1 school"
            assert payload["features"][0].get("strNM") is not None, (
                f"FIELD PRESENCE FAILED: 'strNM' must be non-null. Got: {payload['features'][0]}"
            )

    # ------------------------------------------------------------------
    # NB 511 — key-gated, deterministic unconfigured envelope (never tolerated)
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_road_events_not_configured_without_key(self, mcp_server):
        """'Are there road closures in New Brunswick?' — NOT_CONFIGURED when key absent.

        Deterministic: an unset key is never an outage, so this is asserted by
        exact shape and is never wrapped in assert_live_or_transient tolerance.
        """
        import os
        key = os.environ.pop("NEW_BRUNSWICK_511_KEY", None)
        try:
            data = await call_tool(mcp_server, "nb_get_road_events", {})
        finally:
            if key is not None:
                os.environ["NEW_BRUNSWICK_511_KEY"] = key

        if key is None:
            assert "error" in data, f"Expected NOT_CONFIGURED envelope, got: {data}"
            assert data["error"]["code"] == "NOT_CONFIGURED", (
                f"Expected NOT_CONFIGURED for missing 511 key, got: {data}"
            )
            assert "NEW_BRUNSWICK_511_KEY" in data["error"]["message"]
            assert "SENTINEL" not in str(data)
        else:
            assert "_meta" in data or "error" in data

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_winter_road_conditions_not_configured_without_key(self, mcp_server):
        """'What are winter road conditions in New Brunswick?' — NOT_CONFIGURED when key absent."""
        import os
        key = os.environ.pop("NEW_BRUNSWICK_511_KEY", None)
        try:
            data = await call_tool(mcp_server, "nb_get_winter_road_conditions", {})
        finally:
            if key is not None:
                os.environ["NEW_BRUNSWICK_511_KEY"] = key

        if key is None:
            assert "error" in data, f"Expected NOT_CONFIGURED envelope, got: {data}"
            assert data["error"]["code"] == "NOT_CONFIGURED", (
                f"Expected NOT_CONFIGURED for missing 511 key, got: {data}"
            )
            assert "NEW_BRUNSWICK_511_KEY" in data["error"]["message"]
        else:
            assert "_meta" in data or "error" in data

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_traffic_cameras_not_configured_without_key(self, mcp_server):
        """'Show me New Brunswick traffic cameras' — NOT_CONFIGURED when key absent."""
        import os
        key = os.environ.pop("NEW_BRUNSWICK_511_KEY", None)
        try:
            data = await call_tool(mcp_server, "nb_get_traffic_cameras", {})
        finally:
            if key is not None:
                os.environ["NEW_BRUNSWICK_511_KEY"] = key

        if key is None:
            assert "error" in data, f"Expected NOT_CONFIGURED envelope, got: {data}"
            assert data["error"]["code"] == "NOT_CONFIGURED", (
                f"Expected NOT_CONFIGURED for missing 511 key, got: {data}"
            )
            assert "NEW_BRUNSWICK_511_KEY" in data["error"]["message"]
        else:
            assert "_meta" in data or "error" in data

    # ------------------------------------------------------------------
    # Discovery + cross-module
    # ------------------------------------------------------------------

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_nb_tool(self, mcp_server):
        """'Find me New Brunswick government data tools' — BM25 discovery."""
        results = await discover(mcp_server, "New Brunswick government open data")
        names = [r["name"] for r in results]
        assert any(n.startswith("nb_") for n in names), (
            f"No nb_ tool found in BM25 discovery results for "
            f"'New Brunswick government open data': {names}"
        )

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_cross_module_nb_and_federal_ckan(self, mcp_server):
        """A single agent turn combining nb_search_datasets with the federal ckan_ module."""
        nb_data = await call_tool(mcp_server, "nb_search_datasets", {"query": "flood", "limit": 5})
        live_nb = assert_live_or_transient(nb_data, "nb_search_datasets", "new-brunswick-federal-ckan")

        ckan_data = await call_tool(mcp_server, "ckan_search_datasets", {"query": "flood", "rows": 5})
        live_ckan = assert_live_or_transient(ckan_data, "ckan_search_datasets")

        if live_nb:
            nb_results = nb_data["data"]["results"]
            assert isinstance(nb_results, list) and nb_results, (
                f"nb_search_datasets('flood') must return at least 1 dataset, got: {nb_data['data']}"
            )
        if live_ckan:
            assert_rows(ckan_data, "ckan_search_datasets")

    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_french_language_propagates_on_live_call(self, mcp_server):
        """An agent asking in French gets _meta.lang == 'fr' on a live GeoNB call."""
        data = await call_tool(mcp_server, "nb_get_crown_land", {"limit": 5, "lang": "fr"})
        live = assert_live_or_transient(data, "nb_get_crown_land", "new-brunswick-geonb")
        if live:
            assert data["_meta"]["lang"] == "fr"

    # ------------------------------------------------------------------
    # Manifest-coverage meta-test — every ALL_NB_TOOL_NAMES entry is invoked above
    # ------------------------------------------------------------------

    @pytest.mark.timeout(10)
    def test_every_manifest_tool_is_covered_by_a_scenario(self):
        """constants.ALL_NB_TOOL_NAMES must be a subset of the tool names this
        class actually invokes through call_tool — enforced by the suite, not
        by review, so a future 23rd tool cannot ship without a live scenario.
        """
        import inspect

        from mcp_canada.modules.new_brunswick.constants import ALL_NB_TOOL_NAMES

        source = inspect.getsource(TestNewBrunswickToolScenarios)
        uncovered = [name for name in ALL_NB_TOOL_NAMES if f'"{name}"' not in source]
        assert not uncovered, (
            f"{len(uncovered)} nb_ tool(s) in constants.ALL_NB_TOOL_NAMES have no "
            f"live scenario in TestNewBrunswickToolScenarios: {uncovered}"
        )


# ─── Calgary scenarios ────────────────────────────────────────────────────


class TestCalgaryToolScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_calgary_search_datasets(self, mcp_server):
        """'Calgary open data' — BM25 must surface calgary_search_datasets."""
        results = await discover(mcp_server, "Calgary open data traffic")
        names = [r["name"] for r in results]
        assert any(n.startswith("calgary_") for n in names), (
            f"No calgary_ tool found in BM25 discovery results: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_search_datasets_returns_live_results(self, mcp_server):
        """'Search Calgary datasets for traffic' — proves the Socrata catalog works."""
        data = await call_tool(mcp_server, "calgary_search_datasets", {
            "query": "traffic",
            "limit": 10,
        })
        live = assert_live_or_transient(data, "calgary_search_datasets", "calgary-socrata")
        if live:
            results = data["data"]["results"]
            total = data["data"]["total"]
            assert isinstance(results, list)
            assert total >= 1, f"Expected at least 1 traffic dataset on Calgary Socrata, got {total}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_list_categories_returns_transportation(self, mcp_server):
        """Calgary's live catalog must include a Transportation/Transit-shaped category."""
        data = await call_tool(mcp_server, "calgary_list_categories", {})
        live = assert_live_or_transient(data, "calgary_list_categories", "calgary-socrata")
        if live:
            categories = data["data"]["categories"]
            names = [c["name"] for c in categories]
            assert any("Transportation" in n for n in names), (
                f"Expected a Transportation-shaped category. Got: {sorted(names)}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_french_language_propagates_on_live_call(self, mcp_server):
        """An agent asking in French gets _meta.lang == 'fr' on a live Calgary call."""
        data = await call_tool(mcp_server, "calgary_search_datasets", {"limit": 5, "lang": "fr"})
        live = assert_live_or_transient(data, "calgary_search_datasets", "calgary-socrata")
        if live:
            assert data["_meta"]["lang"] == "fr"


# ─── Edmonton scenarios ───────────────────────────────────────────────────


class TestEdmontonToolScenarios:

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_discover_tools_finds_edmonton_search_datasets(self, mcp_server):
        """'Edmonton open data' — BM25 must surface edmonton_search_datasets."""
        results = await discover(mcp_server, "Edmonton open data building permits")
        names = [r["name"] for r in results]
        assert any(n.startswith("edmonton_") for n in names), (
            f"No edmonton_ tool found in BM25 discovery results: {names}"
        )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_search_datasets_returns_live_results(self, mcp_server):
        """'Search Edmonton datasets for permits' — proves the Socrata catalog works."""
        data = await call_tool(mcp_server, "edmonton_search_datasets", {
            "query": "permits",
            "limit": 10,
        })
        live = assert_live_or_transient(data, "edmonton_search_datasets", "edmonton-socrata")
        if live:
            results = data["data"]["results"]
            total = data["data"]["total"]
            assert isinstance(results, list)
            assert total >= 1, f"Expected at least 1 permits dataset on Edmonton Socrata, got {total}"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_list_categories_returns_urban_planning(self, mcp_server):
        """Edmonton's live catalog must include an Urban Planning & Economy-shaped category."""
        data = await call_tool(mcp_server, "edmonton_list_categories", {})
        live = assert_live_or_transient(data, "edmonton_list_categories", "edmonton-socrata")
        if live:
            categories = data["data"]["categories"]
            names = [c["name"] for c in categories]
            assert any("Urban Planning" in n for n in names), (
                f"Expected an Urban Planning-shaped category. Got: {sorted(names)}"
            )

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_french_language_propagates_on_live_call(self, mcp_server):
        """An agent asking in French gets _meta.lang == 'fr' on a live Edmonton call."""
        data = await call_tool(mcp_server, "edmonton_search_datasets", {"limit": 5, "lang": "fr"})
        live = assert_live_or_transient(data, "edmonton_search_datasets", "edmonton-socrata")
        if live:
            assert data["_meta"]["lang"] == "fr"


@pytest.mark.integration
class TestStatCanCodeSetDrift:
    """Guard the hardcoded WDS decode maps against StatCan's live code set.

    Regression cover for 08-UAT.md Gap 1: `FREQUENCY_CODES` was shifted from code
    6 onward (monthly CPI reported as "Bi-monthly") and `SCALAR_FACTOR_CODES` was
    shifted from code 1 onward (a 100x magnitude misread). Unit tests could not
    catch it — they asserted the maps against themselves — and the server
    contradicted itself, because `sc_get_code_sets` proxies the live endpoint
    while every other sc_ tool decoded against the stale local copy.

    These tests fail if the local maps and upstream ever diverge again.
    """

    @pytest.mark.asyncio
    async def test_frequency_map_matches_live_code_set(self, mcp_server):
        """'Do our frequency labels still match what StatCan publishes?'"""
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        data = await call_tool(mcp_server, "sc_get_code_sets", {})
        assert "_meta" in data, f"expected envelope, got: {data}"
        live = {e["code"]: e["desc_en"] for e in data["data"]["frequency"]}

        assert live, "live frequency code set came back empty"
        assert FREQUENCY_CODES == live, (
            "FREQUENCY_CODES has drifted from StatCan's published set.\n"
            f"  only local: {set(FREQUENCY_CODES) - set(live)}\n"
            f"  only live:  {set(live) - set(FREQUENCY_CODES)}\n"
            f"  mismatched: "
            f"{ {k: (FREQUENCY_CODES[k], live[k]) for k in set(FREQUENCY_CODES) & set(live) if FREQUENCY_CODES[k] != live[k]} }"
        )

    @pytest.mark.asyncio
    async def test_scalar_map_matches_live_code_set(self, mcp_server):
        """'Do our scalar multiplier labels still match StatCan?'"""
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES

        data = await call_tool(mcp_server, "sc_get_code_sets", {})
        live = {e["code"]: e["desc_en"] for e in data["data"]["scalar"]}

        assert live, "live scalar code set came back empty"
        assert SCALAR_FACTOR_CODES == live, (
            "SCALAR_FACTOR_CODES has drifted from StatCan's published set.\n"
            f"  only local: {set(SCALAR_FACTOR_CODES) - set(live)}\n"
            f"  only live:  {set(live) - set(SCALAR_FACTOR_CODES)}\n"
            f"  mismatched: "
            f"{ {k: (SCALAR_FACTOR_CODES[k], live[k]) for k in set(SCALAR_FACTOR_CODES) & set(live) if SCALAR_FACTOR_CODES[k] != live[k]} }"
        )

    @pytest.mark.asyncio
    async def test_monthly_cpi_is_labelled_monthly(self, mcp_server):
        """'Is monthly CPI actually reported as monthly?' — the original defect.

        Vector 41690973 is CPI all-items Canada, frequencyCode 6. Before the fix
        every observation came back labelled "Bi-monthly" despite reference
        periods exactly one month apart.
        """
        data = await call_tool(
            mcp_server, "sc_get_data_by_vector", {"vector_id": 41690973, "n": 3}
        )
        assert "_meta" in data, f"expected envelope, got: {data}"
        rows = data["data"]
        assert rows, "no observations returned"
        for row in rows:
            assert row["frequency_code"] == 6, (
                f"CPI should be frequencyCode 6, got {row['frequency_code']}"
            )
            assert row["frequency"] == "Monthly", (
                f"frequencyCode 6 must decode to 'Monthly', got {row['frequency']!r}"
            )

    @pytest.mark.asyncio
    async def test_resource_catalog_agrees_with_live_code_set(self, mcp_server):
        """The data:// catalog agents read must not contradict the live API."""
        import json as _json
        from mcp_canada.modules.statcan.resources import statcan_frequency_codes

        data = await call_tool(mcp_server, "sc_get_code_sets", {})
        live = {e["code"]: e["desc_en"] for e in data["data"]["frequency"]}
        catalog = {int(k): v["en"] for k, v in _json.loads(statcan_frequency_codes()).items()}

        assert catalog == live, (
            "data://statcan/frequency-codes disagrees with the live code set: "
            f"{ {k: (catalog.get(k), live.get(k)) for k in set(catalog) | set(live) if catalog.get(k) != live.get(k)} }"
        )

    @pytest.mark.asyncio
    async def test_series_info_decodes_uom_label(self, mcp_server):
        """'What unit is this CPI series in?' — 08-UAT Gap 2.

        Vector 41690973 is memberUomCode 17, which upstream means "2002=100"
        (the CPI index base). Before the fix the response carried the bare code
        with no label, and the data://statcan/uom-codes catalog claimed 17 meant
        "Canadian dollars".
        """
        data = await call_tool(
            mcp_server, "sc_get_series_info_by_vector", {"vector_id": 41690973}
        )
        assert "_meta" in data, f"expected envelope, got: {data}"
        info = data["data"]
        assert info["uom_code"] == 17
        assert info.get("uom") == "2002=100", (
            f"uom_code must be decoded alongside frequency/scalar, got {info.get('uom')!r}"
        )

    @pytest.mark.asyncio
    async def test_uom_catalog_subset_matches_live(self, mcp_server):
        """Every embedded UOM entry must be a real upstream value."""
        import json as _json
        from mcp_canada.modules.statcan.resources import statcan_uom_codes

        data = await call_tool(mcp_server, "sc_get_code_sets", {})
        live = {e["code"]: e["desc_en"] for e in data["data"]["uom"]}
        catalog = {
            int(k): v["en"]
            for k, v in _json.loads(statcan_uom_codes()).items()
            if not k.startswith("_")
        }

        wrong = {k: (v, live.get(k)) for k, v in catalog.items() if live.get(k) != v}
        assert not wrong, (
            f"data://statcan/uom-codes has entries that do not exist upstream: {wrong}"
        )
