"""Integration tests for MCP prompts and resources through the Client layer.

Each test simulates what an agent does with prompts and resources:
- client.list_prompts() → PromptInfo list
- client.get_prompt(name, arguments) → GetPromptResult with messages
- client.list_resources() → ResourceInfo list
- client.read_resource(uri) → resource content

Tests hit the full MCP stack with FileSystemProvider auto-discovery.

Run: uv run pytest tests/integration/test_prompts_resources_scenarios.py -v -m integration --timeout=120
"""

import json

import pytest
from fastmcp import Client
from tests.integration.conftest import mcp_server  # noqa: F401 — session fixture

pytestmark = pytest.mark.integration


# ─── Shared helpers ───────────────────────────────────────────────────────────


async def list_prompts(mcp_server) -> list:
    """Call list_prompts through the MCP Client layer."""
    async with Client(mcp_server) as client:
        results = await client.list_prompts()
        return results


async def get_prompt(mcp_server, name: str, arguments: dict | None = None) -> object:
    """Call get_prompt through the MCP Client layer."""
    async with Client(mcp_server) as client:
        return await client.get_prompt(name, arguments or {})


async def list_resources(mcp_server) -> list:
    """Call list_resources through the MCP Client layer."""
    async with Client(mcp_server) as client:
        return await client.list_resources()


async def read_resource(mcp_server, uri: str) -> str:
    """Call read_resource through the MCP Client layer, returns text content."""
    async with Client(mcp_server) as client:
        contents = await client.read_resource(uri)
        # contents is a list of ResourceContent; grab the first text item
        if contents:
            item = contents[0]
            if hasattr(item, "text"):
                return item.text
        return ""


# ─── Prompt discovery ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestPromptDiscovery:

    async def test_all_prompts_discoverable(self, mcp_server):
        """All module prompts appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = [p.name for p in prompts]

        # Conservative lower bound: 12 real modules × ~4-6 prompts each = ~55
        # (_example is excluded from lower bound — it may or may not be present)
        real_prompts = [n for n in names if not n.startswith("example_")]
        assert len(real_prompts) >= 55, (
            f"Expected >= 55 prompts, got {len(real_prompts)}: {sorted(real_prompts)}"
        )

    async def test_boc_prompts_present(self, mcp_server):
        """Bank of Canada prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "boc_analyze_rates" in names
        assert "boc_get_policy_rate" in names
        assert "boc_compare_currencies" in names
        assert "boc_explore_commodities" in names
        assert "boc_check_inflation" in names

    async def test_statcan_prompts_present(self, mcp_server):
        """StatCan prompts appear alongside BoC prompts."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "statcan_find_data" in names
        assert "statcan_store_and_query" in names

    async def test_weather_prompts_present(self, mcp_server):
        """Weather prompts are discovered from the top-level weather/ directory."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "wx_check_weather" in names
        assert "wx_analyze_climate" in names
        assert "wx_check_air_quality" in names

    async def test_no_duplicate_weather_prompts(self, mcp_server):
        """Weather prompts from top-level weather/ are not duplicated per sub-module."""
        prompts = await list_prompts(mcp_server)
        names = [p.name for p in prompts]
        wx_prompts = [n for n in names if n.startswith("wx_")]
        unique_wx = set(wx_prompts)
        assert len(wx_prompts) == len(unique_wx), (
            f"Duplicate weather prompts found: {[n for n in wx_prompts if wx_prompts.count(n) > 1]}"
        )

    async def test_ircc_prompts_present(self, mcp_server):
        """IRCC prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "ircc_explore_immigration" in names
        assert "ircc_track_express_entry" in names

    async def test_ontario_toronto_prompts_present(self, mcp_server):
        """Ontario and Toronto prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "ontario_explore_data" in names
        assert "toronto_explore_city_data" in names

    async def test_parliament_recalls_prompts_present(self, mcp_server):
        """Parliament and Recalls prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "parl_research_bill" in names
        assert "recalls_investigate_alert" in names

    async def test_drug_nutrient_prompts_present(self, mcp_server):
        """Drug Database and Nutrient File prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "drug_research_medication" in names
        assert "nutrient_analyze_food" in names

    async def test_datastore_ckan_prompts_present(self, mcp_server):
        """Datastore and CKAN prompts are discoverable."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "ds_create_and_query" in names
        assert "ckan_explore_federal_data" in names


# ─── Guided workflow prompts (list[Message]) ──────────────────────────────────


@pytest.mark.asyncio
class TestGuidedWorkflowPrompts:

    async def test_boc_guided_workflow_en(self, mcp_server):
        """'How do I analyze CAD exchange rates?' — boc_analyze_rates in English."""
        result = await get_prompt(mcp_server, "boc_analyze_rates", {"lang": "en"})
        messages = result.messages
        assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
        roles = [m.role for m in messages]
        assert "user" in roles
        assert "assistant" in roles
        # Verify English content
        combined = " ".join(
            m.content.text if hasattr(m.content, "text") else str(m.content)
            for m in messages
        )
        assert any(word in combined.lower() for word in ["currency", "exchange", "cad"]), (
            f"Expected English content about exchange rates, got: {combined[:200]}"
        )

    async def test_boc_guided_workflow_fr(self, mcp_server):
        """'Comment analyser les taux de change?' — boc_analyze_rates in French."""
        result = await get_prompt(mcp_server, "boc_analyze_rates", {"lang": "fr"})
        messages = result.messages
        assert len(messages) == 2
        # Verify French content
        combined = " ".join(
            m.content.text if hasattr(m.content, "text") else str(m.content)
            for m in messages
        )
        assert any(word in combined.lower() for word in ["devise", "taux", "cad"]), (
            f"Expected French content about exchange rates, got: {combined[:200]}"
        )

    async def test_statcan_store_and_query_workflow(self, mcp_server):
        """Cross-module flagship: statcan_store_and_query chains sc_fetch_vectors_to_store → ds_query."""
        result = await get_prompt(mcp_server, "statcan_store_and_query", {"lang": "en"})
        messages = result.messages
        assert len(messages) >= 2
        combined = " ".join(
            m.content.text if hasattr(m.content, "text") else str(m.content)
            for m in messages
        )
        # Should reference both statcan and datastore tools
        assert any(kw in combined for kw in ["sc_fetch_vectors", "ds_query", "statcan", "datastore"])

    async def test_weather_check_weather_workflow(self, mcp_server):
        """'How do I check weather conditions?' — wx_check_weather guided workflow."""
        result = await get_prompt(mcp_server, "wx_check_weather", {"lang": "en"})
        messages = result.messages
        assert len(messages) >= 2
        combined = " ".join(
            m.content.text if hasattr(m.content, "text") else str(m.content)
            for m in messages
        )
        assert any(kw in combined.lower() for kw in ["weather", "forecast", "location", "province"])

    async def test_ircc_explore_immigration_workflow(self, mcp_server):
        """'How do I explore IRCC immigration data?' — guided workflow."""
        result = await get_prompt(mcp_server, "ircc_explore_immigration", {"lang": "en"})
        messages = result.messages
        assert len(messages) >= 2

    async def test_toronto_explore_neighbourhood_workflow(self, mcp_server):
        """'How do I explore Toronto neighbourhood data?' — guided workflow."""
        result = await get_prompt(mcp_server, "toronto_explore_neighbourhood", {"lang": "en"})
        messages = result.messages
        assert len(messages) >= 2
        combined = " ".join(
            m.content.text if hasattr(m.content, "text") else str(m.content)
            for m in messages
        )
        assert any(kw in combined.lower() for kw in ["neighbourhood", "toronto", "profile"])


# ─── Quick lookup prompts (str → single user message) ─────────────────────────


@pytest.mark.asyncio
class TestQuickLookupPrompts:

    async def test_boc_quick_policy_rate(self, mcp_server):
        """'What is the policy rate?' — quick lookup returns single message."""
        result = await get_prompt(mcp_server, "boc_get_policy_rate", {"lang": "en"})
        messages = result.messages
        assert len(messages) == 1
        msg = messages[0]
        text = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
        assert any(kw in text.lower() for kw in ["boc_get_interest_rates", "policy"])

    async def test_statcan_quick_vector(self, mcp_server):
        """Quick vector lookup returns a single message with tool reference."""
        result = await get_prompt(mcp_server, "statcan_quick_vector", {"lang": "en"})
        messages = result.messages
        assert len(messages) == 1
        text = messages[0].content.text if hasattr(messages[0].content, "text") else str(messages[0].content)
        assert "sc_get_data_by_vector" in text

    async def test_ckan_quick_search(self, mcp_server):
        """CKAN quick search returns a single message."""
        result = await get_prompt(mcp_server, "ckan_quick_search", {"lang": "en"})
        messages = result.messages
        assert len(messages) == 1

    async def test_toronto_quick_search(self, mcp_server):
        """Toronto quick search returns a single message."""
        result = await get_prompt(mcp_server, "toronto_quick_search", {"lang": "en"})
        messages = result.messages
        assert len(messages) == 1


# ─── Resource discovery ───────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestResourceDiscovery:

    async def test_all_resources_discoverable(self, mcp_server):
        """All module resources appear in resources/list."""
        resources = await list_resources(mcp_server)
        uris = [str(r.uri) for r in resources]

        # Conservative lower bound: 12 modules × ~6-8 resources each = ~70
        real_uris = [u for u in uris if "://example/" not in u]
        assert len(real_uris) >= 70, (
            f"Expected >= 70 resources, got {len(real_uris)}: {sorted(real_uris)}"
        )

    async def test_boc_resources_present(self, mcp_server):
        """Bank of Canada resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "data://boc/currency-codes" in uris
        assert "data://boc/interest-rate-types" in uris
        assert "docs://boc/series-naming" in uris
        assert "template://boc/rate-report" in uris

    async def test_statcan_resources_present(self, mcp_server):
        """StatCan resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "data://statcan/frequency-codes" in uris
        assert "docs://statcan/wds-guide" in uris
        assert "template://statcan/time-series-report" in uris

    async def test_weather_resources_present(self, mcp_server):
        """Weather resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "data://weather/province-codes" in uris
        assert "data://weather/aqhi-scale" in uris
        assert "docs://weather/station-guide" in uris
        assert "template://weather/forecast-report" in uris

    async def test_ircc_toronto_ontario_resources_present(self, mcp_server):
        """IRCC, Toronto, and Ontario resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "data://ircc/dataset-list" in uris
        assert "data://toronto/neighbourhood-list" in uris
        assert "data://ontario/ministries" in uris

    async def test_parliament_recalls_drug_nutrient_resources_present(self, mcp_server):
        """Parliament, Recalls, Drug DB, and Nutrient resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "data://parliament/party-codes" in uris
        assert "data://recalls/categories" in uris
        assert "data://drug/schedule-codes" in uris
        assert "data://nutrient/food-groups" in uris

    async def test_datastore_ckan_resources_present(self, mcp_server):
        """Datastore and CKAN resources are discoverable."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        assert "docs://datastore/sql-guide" in uris
        assert "data://ckan/federal-organizations" in uris


# ─── Resource content ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestResourceContent:

    async def test_catalog_resource_returns_valid_json(self, mcp_server):
        """'What currency codes can I use with BoC?' — data://boc/currency-codes."""
        text = await read_resource(mcp_server, "data://boc/currency-codes")
        data = json.loads(text)
        # Should have USD with bilingual labels
        assert "USD" in data
        usd = data["USD"]
        assert "en" in usd
        assert "fr" in usd

    async def test_docs_resource_returns_markdown(self, mcp_server):
        """'How does BoC series naming work?' — docs://boc/series-naming."""
        text = await read_resource(mcp_server, "docs://boc/series-naming")
        assert text.startswith("#"), f"Expected markdown starting with #, got: {text[:50]}"
        assert "FXUSDCAD" in text

    async def test_template_resource_returns_placeholders(self, mcp_server):
        """'How should I format a rate report?' — template://boc/rate-report."""
        text = await read_resource(mcp_server, "template://boc/rate-report")
        assert "{" in text and "}" in text, f"Expected placeholder syntax {{...}} in template: {text[:100]}"
        # Should contain at least one template placeholder
        import re
        placeholders = re.findall(r"\{[a-z_]+\}", text)
        assert len(placeholders) >= 1, f"No {{placeholder}} found in template: {text[:200]}"

    async def test_statcan_frequency_codes_json(self, mcp_server):
        """StatCan frequency codes resource returns valid JSON with bilingual entries."""
        text = await read_resource(mcp_server, "data://statcan/frequency-codes")
        data = json.loads(text)
        # WDS frequency code '1' = Daily
        assert "1" in data
        assert "en" in data["1"]
        assert "fr" in data["1"]

    async def test_weather_province_codes_json(self, mcp_server):
        """Weather province codes resource returns valid JSON."""
        text = await read_resource(mcp_server, "data://weather/province-codes")
        data = json.loads(text)
        # Should include ON (Ontario) at minimum
        assert "ON" in data or "on" in str(data).lower()

    async def test_ircc_dataset_list_json(self, mcp_server):
        """IRCC dataset list resource returns JSON with tool name mappings."""
        text = await read_resource(mcp_server, "data://ircc/dataset-list")
        data = json.loads(text)
        # Should have at least 5 dataset entries
        assert len(data) >= 5

    async def test_toronto_neighbourhood_list_json(self, mcp_server):
        """Toronto neighbourhood list has all 140 neighbourhoods embedded."""
        text = await read_resource(mcp_server, "data://toronto/neighbourhood-list")
        data = json.loads(text)
        # Full Toronto neighbourhood list = 140 entries
        assert len(data) >= 100, f"Expected >= 100 neighbourhoods, got {len(data)}"

    async def test_datastore_sql_guide_markdown(self, mcp_server):
        """Datastore SQL guide returns markdown with SQL examples."""
        text = await read_resource(mcp_server, "docs://datastore/sql-guide")
        assert "#" in text, "Expected markdown headers"
        assert "SELECT" in text or "sql" in text.lower()

    async def test_ckan_federal_organizations_json(self, mcp_server):
        """CKAN federal organizations resource returns org slug dictionary."""
        text = await read_resource(mcp_server, "data://ckan/federal-organizations")
        data = json.loads(text)
        # Should have multiple organizations; org slugs are used as API params
        assert len(data) >= 5


# ─── URI scheme coverage ──────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestAllUriSchemes:

    async def test_data_scheme_resolves(self, mcp_server):
        """data:// URI scheme resolves to machine-parseable JSON."""
        text = await read_resource(mcp_server, "data://boc/currency-codes")
        # Must be valid JSON
        data = json.loads(text)
        assert isinstance(data, dict)

    async def test_docs_scheme_resolves(self, mcp_server):
        """docs:// URI scheme resolves to human-readable markdown."""
        text = await read_resource(mcp_server, "docs://statcan/wds-guide")
        assert len(text) > 50, "Expected substantive markdown content"
        assert "#" in text

    async def test_template_scheme_resolves(self, mcp_server):
        """template:// URI scheme resolves to markdown with {placeholder} syntax."""
        text = await read_resource(mcp_server, "template://ircc/immigration-report")
        assert "{" in text and "}" in text

    async def test_all_three_schemes_from_different_modules(self, mcp_server):
        """All three URI schemes work across different modules."""
        data_text = await read_resource(mcp_server, "data://weather/aqhi-scale")
        docs_text = await read_resource(mcp_server, "docs://parliament/voting-guide")
        template_text = await read_resource(mcp_server, "template://toronto/neighbourhood-report")

        json.loads(data_text)  # data:// must be valid JSON
        assert "#" in docs_text  # docs:// must be markdown
        assert "{" in template_text  # template:// must have placeholders


# ─── Cross-module prompt verification ─────────────────────────────────────────


@pytest.mark.asyncio
class TestCrossModulePrompts:

    async def test_statcan_prompts_alongside_boc(self, mcp_server):
        """StatCan prompts appear in the same list as BoC prompts."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        assert "boc_analyze_rates" in names
        assert "statcan_find_data" in names

    async def test_weather_prompts_present_once(self, mcp_server):
        """Weather prompts appear exactly once (top-level weather/ not duplicated)."""
        prompts = await list_prompts(mcp_server)
        wx_names = [p.name for p in prompts if p.name.startswith("wx_")]
        assert len(wx_names) == len(set(wx_names)), f"Duplicate wx_ prompts: {wx_names}"
        assert len(wx_names) >= 4, f"Expected >= 4 wx_ prompts, got {wx_names}"

    async def test_all_modules_have_at_least_one_prompt(self, mcp_server):
        """Each active module contributes at least one prompt."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        module_prefixes = ["boc_", "statcan_", "ds_", "ckan_", "parl_", "recalls_",
                           "drug_", "nutrient_", "wx_", "ircc_", "ontario_", "toronto_"]
        for prefix in module_prefixes:
            has_prompt = any(n.startswith(prefix) for n in names)
            assert has_prompt, f"No prompt found for module with prefix '{prefix}'"

    async def test_all_modules_have_at_least_one_resource(self, mcp_server):
        """Each active module contributes at least one resource."""
        resources = await list_resources(mcp_server)
        uris = [str(r.uri) for r in resources]
        module_namespaces = ["boc", "statcan", "datastore", "ckan", "parliament", "recalls",
                             "drug", "nutrient", "weather", "ircc", "ontario", "toronto"]
        for ns in module_namespaces:
            has_resource = any(f"://{ns}/" in u for u in uris)
            assert has_resource, f"No resource found for module namespace '{ns}'"


# ─── York Region prompts and resources ───────────────────────────────────────


@pytest.mark.asyncio
class TestYorkRegionPromptsResources:
    """York Region ArcGIS Hub prompts and resources integration tests.

    Tests verify that prompts are discoverable via list_prompts() and resources
    are readable via read_resource() through the full MCP Client layer.
    """

    async def test_york_region_prompts_discoverable(self, mcp_server):
        """York Region prompts appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = [p.name for p in prompts]
        yr_prompts = [n for n in names if n.startswith("york_region_") or n.startswith("markham_")]
        assert len(yr_prompts) >= 5, (
            f"Expected >= 5 York Region/Markham prompts, got {len(yr_prompts)}: {sorted(yr_prompts)}"
        )
        # Verify specific prompt names
        assert "york_region_explore_transit" in names, (
            f"york_region_explore_transit not in prompts list: {sorted(yr_prompts)}"
        )

    async def test_york_region_portals_resource(self, mcp_server):
        """data://york_region/portals returns JSON with 10 municipalities."""
        import json
        text = await read_resource(mcp_server, "data://york_region/portals")
        assert text, "york_region/portals resource returned empty content"
        data = json.loads(text)
        assert isinstance(data, list)
        assert len(data) >= 10, f"Expected >= 10 portal entries, got {len(data)}"

    async def test_york_region_esri_field_naming_docs(self, mcp_server):
        """docs://york_region/esri-field-naming returns markdown containing OBJECTID."""
        text = await read_resource(mcp_server, "docs://york_region/esri-field-naming")
        assert text, "york_region/esri-field-naming resource returned empty content"
        assert "OBJECTID" in text, "ESRI field naming guide must mention OBJECTID"
        assert "#" in text, "ESRI field naming guide must be markdown with headings"
