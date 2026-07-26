# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for York Region Open Data module prompts and resources."""

import inspect
import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.york_region.prompts import (
    markham_explore_infrastructure,
    york_region_explore_census,
    york_region_explore_health,
    york_region_explore_transit,
    york_region_quick_dataset_search,
)
from mcp_canada.modules.york_region.resources import (
    york_region_arcgis_query_patterns,
    york_region_census_variables,
    york_region_esri_field_naming,
    york_region_feature_services,
    york_region_municipalities,
    york_region_portal_landscape,
    york_region_portals,
    york_region_transit_query_response_template,
)


class TestYorkRegionPrompts:
    """Tests for the 5 York Region @prompt functions."""

    # ------------------------------------------------------------------
    # test_all_prompts_have_lang_param
    # ------------------------------------------------------------------

    def test_all_prompts_have_lang_param(self):
        """All guided and quick prompts accept a lang parameter."""
        fns = [
            york_region_explore_transit,
            york_region_explore_census,
            york_region_explore_health,
            york_region_quick_dataset_search,
            markham_explore_infrastructure,
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, (
                f"{fn.__name__} missing 'lang' parameter"
            )

    # ------------------------------------------------------------------
    # Guided workflow prompts return list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_guided_workflow_prompts_return_list_message(self):
        """Guided workflow prompts return list with >= 2 messages."""
        guided = [
            york_region_explore_transit,
            york_region_explore_census,
            york_region_explore_health,
            markham_explore_infrastructure,
        ]
        for fn in guided:
            p = FunctionPrompt.from_function(fn)
            result = await p.render({"lang": "en"})
            assert len(result.messages) >= 2, (
                f"{fn.__name__} should return >= 2 messages, got {len(result.messages)}"
            )
            for msg in result.messages:
                assert hasattr(msg, "role"), f"{fn.__name__} message missing .role"

    # ------------------------------------------------------------------
    # Quick lookup returns str (single message)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_lookup_returns_str(self):
        """york_region_quick_dataset_search returns a single user message (str)."""
        p = FunctionPrompt.from_function(york_region_quick_dataset_search)
        result = await p.render({"query": "transit", "lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_lookup_mentions_tool(self):
        """Quick lookup references york_region_search_datasets."""
        p = FunctionPrompt.from_function(york_region_quick_dataset_search)
        result = await p.render({"query": "hospitals", "lang": "en"})
        text = result.messages[0].content.text
        assert "york_region_search_datasets" in text

    # ------------------------------------------------------------------
    # Bilingual (French) variants
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_french_variants(self):
        """All prompts return different content for lang='fr' vs lang='en'."""
        guided = [
            york_region_explore_transit,
            york_region_explore_census,
            york_region_explore_health,
            markham_explore_infrastructure,
        ]
        for fn in guided:
            p = FunctionPrompt.from_function(fn)
            en_result = await p.render({"lang": "en"})
            fr_result = await p.render({"lang": "fr"})
            en_text = " ".join(m.content.text for m in en_result.messages)
            fr_text = " ".join(m.content.text for m in fr_result.messages)
            assert en_text != fr_text, (
                f"{fn.__name__} should produce different EN vs FR output"
            )
            # FR text should contain some French vocabulary
            assert any(
                word in fr_text
                for word in ("Région", "données", "utilisez", "Markham", "transit", "santé", "York")
            ), f"{fn.__name__} FR text does not appear to be French: {fr_text[:200]}"

    @pytest.mark.asyncio
    async def test_transit_prompt_en_references_tools(self):
        """york_region_explore_transit references the transit tools."""
        p = FunctionPrompt.from_function(york_region_explore_transit)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert any(
            kw in full_text
            for kw in ("york_region_get_transit_stops", "york_region_get_transit_routes")
        )

    @pytest.mark.asyncio
    async def test_census_prompt_en_references_tool(self):
        """york_region_explore_census references the census demographics tool."""
        p = FunctionPrompt.from_function(york_region_explore_census)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "york_region_get_census_demographics" in full_text

    @pytest.mark.asyncio
    async def test_health_prompt_en_references_tool(self):
        """york_region_explore_health references the public health tool."""
        p = FunctionPrompt.from_function(york_region_explore_health)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "york_region_get_public_health" in full_text


class TestYorkRegionResources:
    """Tests for the 8 York Region @resource functions."""

    # ------------------------------------------------------------------
    # All resources must be zero-parameter
    # ------------------------------------------------------------------

    def test_all_resources_zero_params(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        resources = [
            york_region_portals,
            york_region_municipalities,
            york_region_feature_services,
            york_region_esri_field_naming,
            york_region_portal_landscape,
            york_region_census_variables,
            york_region_arcgis_query_patterns,
            york_region_transit_query_response_template,
        ]
        for fn in resources:
            sig = inspect.signature(fn)
            required = [
                name
                for name, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty
            ]
            assert required == [], (
                f"{fn.__name__} has required parameters {required}; "
                "resources must be zero-param functions"
            )

    # ------------------------------------------------------------------
    # data:// resources return valid JSON
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_data_resources_valid_json(self):
        """All data:// resources return valid JSON."""
        data_resources = [
            (york_region_portals, "data://york_region/portals"),
            (york_region_municipalities, "data://york_region/municipalities"),
            (york_region_feature_services, "data://york_region/feature_services"),
        ]
        for fn, uri in data_resources:
            r = FunctionResource.from_function(fn, uri=uri)
            content = await r.read()
            try:
                json.loads(content)
            except Exception as exc:
                pytest.fail(f"{fn.__name__} returned invalid JSON: {exc}")

    @pytest.mark.asyncio
    async def test_portals_catalog_has_all_10(self):
        """york_region_portals() returns 10 municipalities."""
        r = FunctionResource.from_function(
            york_region_portals, uri="data://york_region/portals"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) == 10, f"Expected 10 portals, got {len(data)}"
        # At least 4 have portal_url set (the verified portals)
        with_portal = [entry for entry in data if entry.get("portal_url")]
        assert len(with_portal) >= 4, (
            f"Expected >= 4 entries with portal_url, got {len(with_portal)}"
        )
        # At least 5 have portal_url: null (no public portal)
        without_portal = [entry for entry in data if not entry.get("portal_url")]
        assert len(without_portal) >= 5, (
            f"Expected >= 5 entries with portal_url null, got {len(without_portal)}"
        )

    @pytest.mark.asyncio
    async def test_municipalities_has_entries(self):
        """york_region_municipalities() returns a list of municipalities."""
        r = FunctionResource.from_function(
            york_region_municipalities, uri="data://york_region/municipalities"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, list)
        assert len(data) >= 9, f"Expected >= 9 municipalities, got {len(data)}"
        # Each entry should have has_portal boolean
        for entry in data:
            assert "has_portal" in entry, f"Missing has_portal in {entry}"

    # ------------------------------------------------------------------
    # docs:// resources return non-empty markdown
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_docs_resources_non_empty_markdown(self):
        """All docs:// resources return non-empty markdown with at least 200 chars and # heading."""
        docs_resources = [
            (york_region_esri_field_naming, "docs://york_region/esri-field-naming"),
            (york_region_portal_landscape, "docs://york_region/portal-landscape"),
            (york_region_census_variables, "docs://york_region/census-variables"),
            (york_region_arcgis_query_patterns, "docs://york_region/arcgis-query-patterns"),
        ]
        for fn, uri in docs_resources:
            r = FunctionResource.from_function(fn, uri=uri)
            content = await r.read()
            assert len(content) > 200, (
                f"{fn.__name__} content too short: {len(content)} chars"
            )
            assert "#" in content, f"{fn.__name__} missing # heading"

    @pytest.mark.asyncio
    async def test_esri_field_naming_mentions_objectid(self):
        """ESRI field naming guide mentions OBJECTID."""
        r = FunctionResource.from_function(
            york_region_esri_field_naming, uri="docs://york_region/esri-field-naming"
        )
        content = await r.read()
        assert "OBJECTID" in content

    @pytest.mark.asyncio
    async def test_census_variables_mentions_key_fields(self):
        """Census variables guide mentions key field names."""
        r = FunctionResource.from_function(
            york_region_census_variables, uri="docs://york_region/census-variables"
        )
        content = await r.read()
        assert "CSDNAME" in content
        assert "TOT_POP" in content

    # ------------------------------------------------------------------
    # template:// resources contain {placeholder} syntax
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_template_resources_have_placeholders(self):
        """york_region_transit_query_response_template has {stop_name} and {route_short_name}."""
        r = FunctionResource.from_function(
            york_region_transit_query_response_template,
            uri="template://york_region/transit-query-response",
        )
        content = await r.read()
        assert "{stop_name}" in content, "Template missing {stop_name}"
        assert "{route_short_name}" in content, "Template missing {route_short_name}"

    @pytest.mark.asyncio
    async def test_template_is_markdown(self):
        """Template resource starts with # heading."""
        r = FunctionResource.from_function(
            york_region_transit_query_response_template,
            uri="template://york_region/transit-query-response",
        )
        content = await r.read()
        assert content.startswith("#"), "Transit query template must start with # heading"
