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


# ─── British Columbia prompts & resources ─────────────────────────────────────


@pytest.mark.asyncio
class TestBcPromptsResources:
    """BC open data prompts and resources integration scenarios.

    Verifies BC prompts and resources are discoverable and readable through the MCP Client layer.
    """

    async def test_bc_prompts_discoverable_via_list_prompts(self, mcp_server):
        """BC prompts (bc_explore_wildfires etc.) appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = [p.name for p in prompts]
        bc_prompts = [n for n in names if n.startswith("bc_")]
        assert len(bc_prompts) >= 6, (
            f"Expected >= 6 bc_ prompts, got {len(bc_prompts)}: {sorted(bc_prompts)}"
        )
        # Verify all 6 expected prompts are present
        expected = [
            "bc_explore_wildfires",
            "bc_explore_forestry",
            "bc_explore_environment",
            "bc_quick_dataset_search",
            "bc_check_water_quality",
            "bc_wildfire_status_now",
        ]
        for name in expected:
            assert name in names, (
                f"Expected bc_ prompt '{name}' not found in prompts/list. "
                f"bc_ prompts found: {sorted(bc_prompts)}"
            )

    async def test_bc_resources_readable_via_read_resource(self, mcp_server):
        """BC resources (data://bc/*, docs://bc/*, template://bc/*) are readable."""
        resources = await list_resources(mcp_server)
        bc_resources = [r for r in resources if "/bc/" in str(r.uri)]
        assert len(bc_resources) >= 7, (
            f"Expected >= 7 bc/ resources, got {len(bc_resources)}: "
            f"{[str(r.uri) for r in bc_resources]}"
        )
        # Read each bc/ resource and assert content is non-empty
        for r in bc_resources:
            uri = str(r.uri)
            content = await read_resource(mcp_server, uri)
            assert content, f"Resource {uri} returned empty content"
            assert len(content) > 10, f"Resource {uri} content too short: {len(content)} chars"

    async def test_bc_wfs_query_guide_resource_returns_markdown(self, mcp_server):
        """docs://bc/wfs-query-guide returns markdown describing the CKAN->WFS two-step workflow."""
        content = await read_resource(mcp_server, "docs://bc/wfs-query-guide")
        assert content, "docs://bc/wfs-query-guide returned empty content"
        assert "CKAN" in content, "WFS query guide must mention CKAN"
        assert "WFS" in content, "WFS query guide must mention WFS"
        assert "bc_query_features" in content, "WFS query guide must reference bc_query_features"
        assert "#" in content, "WFS query guide must be markdown with headings"


# ─── Quebec prompts and resources scenarios ───────────────────────────────────


@pytest.mark.asyncio
class TestQuebecPromptsResources:
    """Integration tests for Quebec prompts and resources."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_prompts_discoverable(self, mcp_server):
        """Quebec prompts appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        prompt_names = [p.name for p in prompts]
        quebec_prompts = [n for n in prompt_names if n.startswith("quebec_")]
        assert len(quebec_prompts) >= 6, (
            f"Expected >= 6 quebec_ prompts, got {len(quebec_prompts)}: {sorted(quebec_prompts)}"
        )
        expected = {
            "quebec_explore_health",
            "quebec_explore_transport_conditions",
            "quebec_explore_environment",
            "quebec_quick_dataset_search",
            "quebec_check_road_conditions",
            "quebec_active_fires_now",
        }
        for p in expected:
            assert p in prompt_names, f"Missing Quebec prompt: {p}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_resources_discoverable(self, mcp_server):
        """Quebec resources (data://quebec/*, docs://quebec/*, template://quebec/*) appear in resources/list."""
        resources = await list_resources(mcp_server)
        quebec_resources = [r for r in resources if "/quebec/" in str(r.uri)]
        assert len(quebec_resources) >= 7, (
            f"Expected >= 7 quebec/ resources, got {len(quebec_resources)}: "
            f"{[str(r.uri) for r in quebec_resources]}"
        )
        uris = {str(r.uri) for r in quebec_resources}
        expected_uris = {
            "data://quebec/ministries",
            "data://quebec/regions",
            "data://quebec/mrcs",
            "docs://quebec/catalog-federation-quirks",
            "docs://quebec/bilingual-metadata-guide",
            "template://quebec/dataset-report",
            "template://quebec/road-conditions-report",
        }
        for uri in expected_uris:
            assert uri in uris, f"Missing Quebec resource URI: {uri}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ministries_resource_valid_json(self, mcp_server):
        """data://quebec/ministries returns valid JSON with ministry entries."""
        import json
        content = await read_resource(mcp_server, "data://quebec/ministries")
        assert content, "data://quebec/ministries returned empty content"
        parsed = json.loads(content)
        assert isinstance(parsed, list)
        assert len(parsed) >= 5
        slugs = [entry["slug"] for entry in parsed]
        assert "msss" in slugs
        assert "mtq" in slugs


# ─── Alberta prompts and resources scenarios ──────────────────────────────────


@pytest.mark.asyncio
class TestAlbertaPromptsResources:
    """Integration tests for Alberta prompts (6 bilingual) and resources (7 zero-param).

    Verifies discovery through client.list_prompts() / client.list_resources() and
    read_resource() round-trip for JSON-validation of the ministries catalog.
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_six_prompts_discoverable(self, mcp_server):
        """Alberta's 6 prompts (3 guided + 3 quick lookups) appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        expected = [
            "alberta_explore_energy",
            "alberta_explore_wildfires",
            "alberta_explore_health_or_transport",
            "alberta_quick_dataset_search",
            "alberta_check_road_conditions",
            "alberta_active_fires_now",
        ]
        for prompt_name in expected:
            assert prompt_name in names, (
                f"Missing Alberta prompt: {prompt_name}. "
                f"alberta_ prompts found: {sorted(n for n in names if n.startswith('alberta_'))}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_seven_resources_discoverable(self, mcp_server):
        """Alberta's 7 resources (3 data:// + 2 docs:// + 2 template://) appear in resources/list."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        expected_uris = [
            "data://alberta/ministries",
            "data://alberta/forest-areas",
            "data://alberta/ahs-zones",
            "docs://alberta/aer-data-guide",
            "docs://alberta/wildfire-data-guide",
            "template://alberta/dataset-report",
            "template://alberta/wildfire-report",
        ]
        for uri in expected_uris:
            assert uri in uris, (
                f"Missing Alberta resource URI: {uri}. "
                f"alberta/ URIs found: {sorted(u for u in uris if '/alberta/' in u)}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ministries_resource_returns_valid_json(self, mcp_server):
        """data://alberta/ministries returns valid JSON with energy-and-minerals ministry."""
        content = await read_resource(mcp_server, "data://alberta/ministries")
        assert content, "data://alberta/ministries returned empty content"
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        assert "ministries" in parsed
        ministries = parsed["ministries"]
        assert isinstance(ministries, list)
        assert len(ministries) >= 10
        slugs = [m["slug"] for m in ministries]
        assert "energy-and-minerals" in slugs, (
            f"Expected 'energy-and-minerals' ministry slug; got: {slugs}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wildfire_data_guide_mentions_ab23(self, mcp_server):
        """docs://alberta/wildfire-data-guide must include the AB-23 water-licence guidance."""
        content = await read_resource(mcp_server, "docs://alberta/wildfire-data-guide")
        assert content, "docs://alberta/wildfire-data-guide returned empty content"
        assert "AB-23" in content, (
            "wildfire-data-guide must keep AB-23 water-licence section (Plan 08 requirement)"
        )
        assert "water-licence" in content.lower() or "water licence" in content.lower()


# ─── Manitoba prompts and resources scenarios ─────────────────────────────────


@pytest.mark.asyncio
class TestManitobaPromptsResources:
    """Integration tests for Manitoba prompts (6) and resources (7).

    Verifies discovery via list_prompts() / list_resources() and content via read_resource()
    through the full MCP Client layer (FileSystemProvider auto-discovery).
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_six_prompts_discoverable(self, mcp_server):
        """Manitoba's 6 prompts (3 guided workflows + 3 quick lookups) appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        expected = [
            "manitoba_explore_flood_or_water",
            "manitoba_explore_transport",
            "manitoba_explore_agriculture_or_health",
            "manitoba_quick_dataset_search",
            "manitoba_check_road_conditions",
            "manitoba_flood_outlook_now",
        ]
        for prompt_name in expected:
            assert prompt_name in names, (
                f"Missing Manitoba prompt: {prompt_name}. "
                f"manitoba_ prompts found: {sorted(n for n in names if n.startswith('manitoba_'))}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_seven_resources_discoverable(self, mcp_server):
        """Manitoba's 7 resources (3 data:// + 2 docs:// + 2 template://) appear in resources/list."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        expected_uris = [
            "data://manitoba/departments",
            "data://manitoba/health-regions",
            "data://manitoba/major-rivers",
            "docs://manitoba/flood-data-guide",
            "docs://manitoba/portal-guide",
            "template://manitoba/dataset-report",
            "template://manitoba/flood-report",
        ]
        for uri in expected_uris:
            assert uri in uris, (
                f"Missing Manitoba resource URI: {uri}. "
                f"manitoba/ URIs found: {sorted(u for u in uris if '/manitoba/' in u)}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_departments_resource_returns_valid_json(self, mcp_server):
        """data://manitoba/departments returns valid JSON with Manitoba ministry entries."""
        content = await read_resource(mcp_server, "data://manitoba/departments")
        assert content, "data://manitoba/departments returned empty content"
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        assert "departments" in parsed
        departments = parsed["departments"]
        assert isinstance(departments, list)
        assert len(departments) >= 3
        # Verify expected fields exist in first entry
        first = departments[0]
        assert "name_en" in first or "name" in first, (
            f"Department entry missing name_en/name field: {first}"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_health_regions_resource_returns_valid_json(self, mcp_server):
        """data://manitoba/health-regions returns JSON with 5 Regional Health Authorities."""
        content = await read_resource(mcp_server, "data://manitoba/health-regions")
        assert content, "data://manitoba/health-regions returned empty content"
        parsed = json.loads(content)
        # Should contain 5 RHAs: WRHA, PMH, IERHA, SHSS, NHR
        if isinstance(parsed, dict):
            data = parsed.get("regions", parsed.get("health_regions", list(parsed.values())[0]))
        else:
            data = parsed
        assert isinstance(data, list)
        assert len(data) >= 3, f"Expected >= 3 RHAs, got {len(data)}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_major_rivers_resource_returns_valid_json(self, mcp_server):
        """data://manitoba/major-rivers returns JSON including Red River Floodway."""
        content = await read_resource(mcp_server, "data://manitoba/major-rivers")
        assert content, "data://manitoba/major-rivers returned empty content"
        parsed = json.loads(content)
        raw = json.dumps(parsed)
        # Floodway is a critical infrastructure entry per Plan 07 decisions
        assert "Floodway" in raw or "floodway" in raw.lower(), (
            "major-rivers resource must include Red River Floodway entry"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_flood_data_guide_is_markdown(self, mcp_server):
        """docs://manitoba/flood-data-guide returns markdown with Watch/Warning/Advisory table."""
        content = await read_resource(mcp_server, "docs://manitoba/flood-data-guide")
        assert content, "docs://manitoba/flood-data-guide returned empty content"
        assert "#" in content, "flood-data-guide must be markdown with headings"
        assert "Watch" in content or "Warning" in content, (
            "flood-data-guide must contain alert type guidance (Watch/Warning/Advisory)"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_portal_guide_mentions_mli_retirement(self, mcp_server):
        """docs://manitoba/portal-guide must document the MLI retirement (2022-02-09)."""
        content = await read_resource(mcp_server, "docs://manitoba/portal-guide")
        assert content, "docs://manitoba/portal-guide returned empty content"
        assert "MLI" in content or "mli.gov.mb.ca" in content, (
            "portal-guide must warn about MLI retirement (common pitfall from 18-RESEARCH)"
        )
        assert "#" in content, "portal-guide must be markdown with headings"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_dataset_report_template_has_placeholders(self, mcp_server):
        """template://manitoba/dataset-report returns markdown with {placeholder} syntax."""
        content = await read_resource(mcp_server, "template://manitoba/dataset-report")
        assert content, "template://manitoba/dataset-report returned empty content"
        assert "{" in content and "}" in content, (
            "template://manitoba/dataset-report must contain {placeholder} syntax for agents"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_flood_report_template_has_placeholders(self, mcp_server):
        """template://manitoba/flood-report returns markdown with {placeholder} syntax."""
        content = await read_resource(mcp_server, "template://manitoba/flood-report")
        assert content, "template://manitoba/flood-report returned empty content"
        assert "{" in content and "}" in content, (
            "template://manitoba/flood-report must contain {placeholder} syntax for agents"
        )


class TestSaskatchewanPromptsResources:
    """Integration tests for Saskatchewan prompts (6) and resources (7).

    Verifies discovery via list_prompts() / list_resources() and content via read_resource()
    through the full MCP Client layer (FileSystemProvider auto-discovery).
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_six_prompts_discoverable(self, mcp_server):
        """Saskatchewan's 6 prompts (3 guided + 3 quick lookups) appear in prompts/list."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        expected = [
            "saskatchewan_explore_agriculture",
            "saskatchewan_explore_environment",
            "saskatchewan_explore_water",
            "saskatchewan_quick_dataset_search",
            "saskatchewan_fire_ban_status_now",
            "saskatchewan_crop_yield_lookup",
        ]
        for prompt_name in expected:
            assert prompt_name in names, (
                f"Missing Saskatchewan prompt: {prompt_name}. "
                f"saskatchewan_ prompts found: "
                f"{sorted(n for n in names if n.startswith('saskatchewan_'))}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_seven_resources_discoverable(self, mcp_server):
        """Saskatchewan's 7 resources (3 data:// + 2 docs:// + 2 template://) appear in list."""
        resources = await list_resources(mcp_server)
        uris = {str(r.uri) for r in resources}
        expected_uris = [
            "data://saskatchewan/crop-regions",
            "data://saskatchewan/major-basins",
            "data://saskatchewan/health-regions",
            "docs://saskatchewan/portal-guide",
            "docs://saskatchewan/agriculture-data-guide",
            "template://saskatchewan/dataset-report",
            "template://saskatchewan/wildfire-report",
        ]
        for uri in expected_uris:
            assert uri in uris, (
                f"Missing Saskatchewan resource URI: {uri}. "
                f"saskatchewan/ URIs found: {sorted(u for u in uris if '/saskatchewan/' in u)}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_crop_regions_resource_returns_valid_json(self, mcp_server):
        """data://saskatchewan/crop-regions returns JSON with 5 SK crop reporting regions."""
        content = await read_resource(mcp_server, "data://saskatchewan/crop-regions")
        assert content, "data://saskatchewan/crop-regions returned empty content"
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        # Should contain 5 regions: southeast, southwest, central, northeast, northwest
        raw = json.dumps(parsed)
        assert "southeast" in raw.lower() or "Southeast" in raw, (
            "crop-regions must include Southeast region"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_major_basins_resource_returns_valid_json(self, mcp_server):
        """data://saskatchewan/major-basins returns JSON with SK river basin entries."""
        content = await read_resource(mcp_server, "data://saskatchewan/major-basins")
        assert content, "data://saskatchewan/major-basins returned empty content"
        parsed = json.loads(content)
        raw = json.dumps(parsed)
        # Should contain major SK basins like Saskatchewan River
        assert "Saskatchewan" in raw or "saskatchewan" in raw.lower(), (
            "major-basins must reference Saskatchewan River basin"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_health_regions_resource_returns_valid_json(self, mcp_server):
        """data://saskatchewan/health-regions returns JSON with SHA (2017 merged authority)."""
        content = await read_resource(mcp_server, "data://saskatchewan/health-regions")
        assert content, "data://saskatchewan/health-regions returned empty content"
        parsed = json.loads(content)
        raw = json.dumps(parsed)
        # Saskatchewan merged to single SHA in 2017
        assert "SHA" in raw or "Saskatchewan Health Authority" in raw, (
            "health-regions must reference the Saskatchewan Health Authority (SHA)"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_portal_guide_documents_multi_org(self, mcp_server):
        """docs://saskatchewan/portal-guide must document all 3 portal servers (Hub + WSA + SPSA)."""
        content = await read_resource(mcp_server, "docs://saskatchewan/portal-guide")
        assert content, "docs://saskatchewan/portal-guide returned empty content"
        assert "#" in content, "portal-guide must be markdown with headings"
        # Must document the two ArcGIS Hub org IDs
        assert "zcv98lgAl8xQ04cW" in content, (
            "portal-guide must document the primary Hub org ID (zcv98lgAl8xQ04cW)"
        )
        assert "7MBdlVpjqbfBhQer" in content, (
            "portal-guide must document the WSA org ID (7MBdlVpjqbfBhQer)"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_agriculture_data_guide_is_markdown(self, mcp_server):
        """docs://saskatchewan/agriculture-data-guide returns markdown about crop yields."""
        content = await read_resource(mcp_server, "docs://saskatchewan/agriculture-data-guide")
        assert content, "docs://saskatchewan/agriculture-data-guide returned empty content"
        assert "#" in content, "agriculture-data-guide must be markdown with headings"
        # Must document crop yields tool
        assert "crop" in content.lower() or "Crop" in content, (
            "agriculture-data-guide must document crop yield data"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_dataset_report_template_has_placeholders(self, mcp_server):
        """template://saskatchewan/dataset-report returns markdown with {placeholder} syntax."""
        content = await read_resource(mcp_server, "template://saskatchewan/dataset-report")
        assert content, "template://saskatchewan/dataset-report returned empty content"
        assert "{" in content and "}" in content, (
            "template://saskatchewan/dataset-report must contain {placeholder} syntax"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_wildfire_report_template_has_placeholders(self, mcp_server):
        """template://saskatchewan/wildfire-report returns markdown with {placeholder} syntax."""
        content = await read_resource(mcp_server, "template://saskatchewan/wildfire-report")
        assert content, "template://saskatchewan/wildfire-report returned empty content"
        assert "{" in content and "}" in content, (
            "template://saskatchewan/wildfire-report must contain {placeholder} syntax"
        )


# ─── Nova Scotia prompts + resources ─────────────────────────────────────────


@pytest.mark.asyncio
class TestNovaScotiaPromptsResources:
    """Integration tests for Nova Scotia MCP prompts and resources.

    Verifies:
    - All 6 ns_ prompts are discoverable via list_prompts()
    - All 7 ns_ resources are readable via read_resource()
    - Resource content is well-formed (JSON or markdown)
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_prompts_discoverable(self, mcp_server):
        """All 6 Nova Scotia prompts appear in list_prompts()."""
        prompts = await list_prompts(mcp_server)
        names = {p.name for p in prompts}
        expected_ns_prompts = {
            "ns_explore_aquaculture_data",
            "ns_health_zone_analysis",
            "ns_water_quality_analysis",
            "ns_quick_find_dataset",
            "ns_quick_protected_areas",
            "ns_quick_vital_stats",
        }
        for prompt_name in expected_ns_prompts:
            assert prompt_name in names, (
                f"Nova Scotia prompt '{prompt_name}' not found in list_prompts(). "
                f"NS prompts present: {sorted(n for n in names if n.startswith('ns_'))}"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_categories_resource_is_json(self, mcp_server):
        """data://ns/categories returns valid JSON with category list."""
        content = await read_resource(mcp_server, "data://ns/categories")
        assert content, "data://ns/categories returned empty content"
        data = json.loads(content)
        assert isinstance(data, (dict, list)), (
            "data://ns/categories must return valid JSON (dict or list)"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_health_zones_resource_is_json(self, mcp_server):
        """data://ns/health-zones returns valid JSON with zone info."""
        content = await read_resource(mcp_server, "data://ns/health-zones")
        assert content, "data://ns/health-zones returned empty content"
        data = json.loads(content)
        assert isinstance(data, (dict, list)), (
            "data://ns/health-zones must return valid JSON"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_fishing_areas_resource_is_json(self, mcp_server):
        """data://ns/fishing-areas returns valid JSON with species type info."""
        content = await read_resource(mcp_server, "data://ns/fishing-areas")
        assert content, "data://ns/fishing-areas returned empty content"
        data = json.loads(content)
        assert isinstance(data, (dict, list)), (
            "data://ns/fishing-areas must return valid JSON"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_departments_resource_is_json(self, mcp_server):
        """data://ns/departments returns valid JSON with NS government departments."""
        content = await read_resource(mcp_server, "data://ns/departments")
        assert content, "data://ns/departments returned empty content"
        data = json.loads(content)
        assert isinstance(data, (dict, list)), (
            "data://ns/departments must return valid JSON"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_socrata_guide_is_markdown(self, mcp_server):
        """docs://ns/socrata-guide returns markdown with SoQL documentation."""
        content = await read_resource(mcp_server, "docs://ns/socrata-guide")
        assert content, "docs://ns/socrata-guide returned empty content"
        assert "#" in content, "docs://ns/socrata-guide must be markdown with headings"
        assert "SoQL" in content or "soql" in content.lower(), (
            "docs://ns/socrata-guide must document SoQL query syntax"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_portal_guide_is_markdown(self, mcp_server):
        """docs://ns/portal-guide returns markdown documenting the Socrata portal."""
        content = await read_resource(mcp_server, "docs://ns/portal-guide")
        assert content, "docs://ns/portal-guide returned empty content"
        assert "#" in content, "docs://ns/portal-guide must be markdown with headings"
        assert "Socrata" in content or "socrata" in content.lower(), (
            "docs://ns/portal-guide must document Socrata as the portal technology"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.timeout(30)
    async def test_ns_aquaculture_report_template_has_placeholders(self, mcp_server):
        """template://ns/aquaculture-report returns markdown with {placeholder} syntax."""
        content = await read_resource(mcp_server, "template://ns/aquaculture-report")
        assert content, "template://ns/aquaculture-report returned empty content"
        assert "{" in content and "}" in content, (
            "template://ns/aquaculture-report must contain {placeholder} syntax"
        )
