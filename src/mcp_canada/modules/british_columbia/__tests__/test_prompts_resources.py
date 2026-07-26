# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for British Columbia Open Data module prompts and resources."""

from __future__ import annotations

import inspect
import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.british_columbia.prompts import (
    bc_check_water_quality,
    bc_explore_environment,
    bc_explore_forestry,
    bc_explore_wildfires,
    bc_quick_dataset_search,
    bc_wildfire_status_now,
)
from mcp_canada.modules.british_columbia.resources import (
    bc_bcdc_api_quirks,
    bc_dataset_report_template,
    bc_ministries,
    bc_object_name_prefixes,
    bc_wfs_query_guide,
    bc_wildfire_report_template,
    bc_wildfire_status_codes,
)


class TestBcPrompts:
    """Tests for the 6 BC bilingual @prompt functions."""

    # ------------------------------------------------------------------
    # Module imports and structure
    # ------------------------------------------------------------------

    def test_prompts_module_imports(self):
        """All 6 BC prompt functions are importable from prompts module."""
        import mcp_canada.modules.british_columbia.prompts as prompts_mod

        expected = [
            "bc_explore_wildfires",
            "bc_explore_forestry",
            "bc_explore_environment",
            "bc_quick_dataset_search",
            "bc_check_water_quality",
            "bc_wildfire_status_now",
        ]
        for name in expected:
            assert hasattr(prompts_mod, name), f"prompts module missing {name}"

    # ------------------------------------------------------------------
    # Guided workflow: bc_explore_wildfires
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_explore_wildfires_returns_list_of_messages_en(self):
        """bc_explore_wildfires returns list[Message] with >= 2 messages in EN."""
        p = FunctionPrompt.from_function(bc_explore_wildfires)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2
        roles = [m.role for m in result.messages]
        assert "user" in roles
        assert "assistant" in roles

    @pytest.mark.asyncio
    async def test_bc_explore_wildfires_returns_list_of_messages_fr(self):
        """bc_explore_wildfires returns FR content when lang='fr'."""
        p = FunctionPrompt.from_function(bc_explore_wildfires)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) >= 2
        full_text = " ".join(m.content.text for m in result.messages)
        assert any(word in full_text for word in ("feux", "forêt", "C.-B.", "Colombie", "incendies"))

    @pytest.mark.asyncio
    async def test_bc_explore_wildfires_references_tools(self):
        """bc_explore_wildfires assistant message references bc_ tools."""
        p = FunctionPrompt.from_function(bc_explore_wildfires)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "bc_get_active_fires" in full_text
        assert "bc_get_fire_perimeters" in full_text

    # ------------------------------------------------------------------
    # Guided workflow: bc_explore_forestry
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_explore_forestry_guided_workflow_shape(self):
        """bc_explore_forestry returns user + assistant roles with forestry tool references."""
        p = FunctionPrompt.from_function(bc_explore_forestry)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2
        full_text = " ".join(m.content.text for m in result.messages)
        assert any(
            tool in full_text
            for tool in ("bc_get_forest_tenure", "bc_get_cut_blocks", "bc_get_protected_areas")
        )

    @pytest.mark.asyncio
    async def test_bc_explore_forestry_fr_content(self):
        """bc_explore_forestry returns French content when lang='fr'."""
        p = FunctionPrompt.from_function(bc_explore_forestry)
        en_result = await p.render({"lang": "en"})
        fr_result = await p.render({"lang": "fr"})
        en_text = " ".join(m.content.text for m in en_result.messages)
        fr_text = " ".join(m.content.text for m in fr_result.messages)
        assert en_text != fr_text
        assert any(word in fr_text for word in ("forestière", "tenure", "blocs", "coupes"))

    # ------------------------------------------------------------------
    # Guided workflow: bc_explore_environment
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_explore_environment_guided_workflow_shape(self):
        """bc_explore_environment returns user + assistant roles with environment tool references."""
        p = FunctionPrompt.from_function(bc_explore_environment)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2
        full_text = " ".join(m.content.text for m in result.messages)
        assert any(
            tool in full_text
            for tool in ("bc_get_water_wells", "bc_get_local_parks", "bc_get_mining_tenure")
        )

    # ------------------------------------------------------------------
    # Quick lookup: bc_quick_dataset_search
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_quick_dataset_search_returns_str(self):
        """bc_quick_dataset_search returns a single user message (quick lookup pattern)."""
        p = FunctionPrompt.from_function(bc_quick_dataset_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_bc_quick_dataset_search_references_tool(self):
        """bc_quick_dataset_search references bc_search_datasets."""
        p = FunctionPrompt.from_function(bc_quick_dataset_search)
        result = await p.render({"lang": "en"})
        assert "bc_search_datasets" in result.messages[0].content.text

    # ------------------------------------------------------------------
    # Quick lookup: bc_check_water_quality
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_check_water_quality_returns_str(self):
        """bc_check_water_quality returns a single user message (quick lookup pattern)."""
        p = FunctionPrompt.from_function(bc_check_water_quality)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_bc_check_water_quality_references_tool(self):
        """bc_check_water_quality references bc_get_water_wells."""
        p = FunctionPrompt.from_function(bc_check_water_quality)
        result = await p.render({"lang": "en"})
        assert "bc_get_water_wells" in result.messages[0].content.text

    # ------------------------------------------------------------------
    # Quick lookup: bc_wildfire_status_now
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_wildfire_status_now_returns_str(self):
        """bc_wildfire_status_now returns a single user message (quick lookup pattern)."""
        p = FunctionPrompt.from_function(bc_wildfire_status_now)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_bc_wildfire_status_now_references_tool(self):
        """bc_wildfire_status_now references bc_get_active_fires."""
        p = FunctionPrompt.from_function(bc_wildfire_status_now)
        result = await p.render({"lang": "en"})
        assert "bc_get_active_fires" in result.messages[0].content.text

    # ------------------------------------------------------------------
    # Shared invariants
    # ------------------------------------------------------------------

    def test_all_prompts_accept_lang_parameter(self):
        """All 6 BC prompts accept a 'lang' parameter."""
        fns = [
            bc_explore_wildfires,
            bc_explore_forestry,
            bc_explore_environment,
            bc_quick_dataset_search,
            bc_check_water_quality,
            bc_wildfire_status_now,
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, f"{fn.__name__} missing 'lang' parameter"

    def test_all_prompts_use_bc_prefix(self):
        """All 6 BC prompt functions use the bc_ prefix."""
        fns = [
            bc_explore_wildfires,
            bc_explore_forestry,
            bc_explore_environment,
            bc_quick_dataset_search,
            bc_check_water_quality,
            bc_wildfire_status_now,
        ]
        for fn in fns:
            assert fn.__name__.startswith("bc_"), (
                f"{fn.__name__} does not use bc_ prefix"
            )


class TestBcResources:
    """Tests for the 7 BC zero-parameter @resource functions."""

    # ------------------------------------------------------------------
    # Module imports and structure
    # ------------------------------------------------------------------

    def test_resources_module_imports(self):
        """All 7 BC resource functions are importable from resources module."""
        import mcp_canada.modules.british_columbia.resources as resources_mod

        expected = [
            "bc_ministries",
            "bc_wildfire_status_codes",
            "bc_object_name_prefixes",
            "bc_wfs_query_guide",
            "bc_bcdc_api_quirks",
            "bc_wildfire_report_template",
            "bc_dataset_report_template",
        ]
        for name in expected:
            assert hasattr(resources_mod, name), f"resources module missing {name}"

    # ------------------------------------------------------------------
    # data:// resources — valid JSON with bilingual entries
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_ministries_is_valid_json_with_bilingual_entries(self):
        """bc_ministries returns valid JSON with name_en and name_fr per entry."""
        r = FunctionResource.from_function(bc_ministries, uri="data://bc/ministries")
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, list), "bc_ministries should return a JSON list"
        assert len(data) >= 8, f"Expected >= 8 ministry entries, got {len(data)}"
        for entry in data:
            assert "slug" in entry, f"Entry missing 'slug': {entry}"
            assert "name_en" in entry, f"Entry missing 'name_en': {entry}"
            assert "name_fr" in entry, f"Entry missing 'name_fr': {entry}"
        # Verify known slug is present
        slugs = [e["slug"] for e in data]
        assert "bc-wildfire-service" in slugs, "bc-wildfire-service slug missing"

    @pytest.mark.asyncio
    async def test_bc_wildfire_status_codes_is_valid_json_with_fire_status_and_cause(self):
        """bc_wildfire_status_codes returns valid JSON with fire_status and fire_cause arrays."""
        r = FunctionResource.from_function(
            bc_wildfire_status_codes, uri="data://bc/wildfire-status-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert "fire_status" in data, "Missing 'fire_status' key"
        assert "fire_cause" in data, "Missing 'fire_cause' key"
        # Verify status codes
        status_codes = [s["code"] for s in data["fire_status"]]
        assert "Out of Control" in status_codes
        assert "Being Held" in status_codes
        assert "Under Control" in status_codes
        assert "Active" in status_codes
        assert "Out" in status_codes
        # Verify bilingual labels in status
        for entry in data["fire_status"]:
            assert "label_en" in entry, f"Status entry missing label_en: {entry}"
            assert "label_fr" in entry, f"Status entry missing label_fr: {entry}"
        # Verify cause codes
        cause_codes = [c["code"] for c in data["fire_cause"]]
        assert "Lightning" in cause_codes
        assert "Human" in cause_codes

    @pytest.mark.asyncio
    async def test_bc_object_name_prefixes_lists_all_10_whse_categories(self):
        """bc_object_name_prefixes returns JSON with all 10 WHSE schema prefixes."""
        r = FunctionResource.from_function(
            bc_object_name_prefixes, uri="data://bc/object-name-prefixes"
        )
        content = await r.read()
        data = json.loads(content)
        assert "schema_prefixes" in data, "Missing 'schema_prefixes' key"
        prefixes = [p["prefix"] for p in data["schema_prefixes"]]
        required = [
            "WHSE_LAND_AND_NATURAL_RESOURCE",
            "WHSE_FOREST_TENURE",
            "WHSE_TANTALIS",
            "WHSE_MINERAL_TENURE",
            "WHSE_WATER_MANAGEMENT",
            "WHSE_WILDLIFE_MANAGEMENT",
            "WHSE_ENVIRONMENTAL_MONITORING",
            "WHSE_IMAGERY_AND_BASE_MAPS",
            "WHSE_BASEMAPPING",
            "WHSE_PARKS_ECOLOGY",
        ]
        for prefix in required:
            assert prefix in prefixes, f"Missing WHSE prefix: {prefix}"
        # Verify curated_layers maps 15 tools
        assert "curated_layers" in data
        assert len(data["curated_layers"]) == 15, (
            f"Expected 15 curated layers, got {len(data['curated_layers'])}"
        )
        assert "bc_get_active_fires" in data["curated_layers"]
        assert "bc_get_fire_perimeters" in data["curated_layers"]

    # ------------------------------------------------------------------
    # docs:// resources — markdown with expected content
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_wfs_query_guide_is_markdown_with_cql_example(self):
        """bc_wfs_query_guide returns markdown with CQL syntax and bc_query_features reference."""
        r = FunctionResource.from_function(bc_wfs_query_guide, uri="docs://bc/wfs-query-guide")
        content = await r.read()
        assert len(content) > 500, f"wfs-query-guide too short: {len(content)} chars"
        assert "#" in content, "wfs-query-guide missing # heading"
        assert "CKAN" in content
        assert "WFS" in content
        assert "bc_query_features" in content
        # CQL examples
        assert "CQL" in content or "cql" in content.lower()
        assert "FIRE_YEAR" in content

    @pytest.mark.asyncio
    async def test_bc_bcdc_api_quirks_is_markdown_with_bilingual_content(self):
        """bc_bcdc_api_quirks returns markdown with bcgov custom fields and bilingual sections."""
        r = FunctionResource.from_function(bc_bcdc_api_quirks, uri="docs://bc/bcdc-api-quirks")
        content = await r.read()
        assert len(content) > 400, f"bcdc-api-quirks too short: {len(content)} chars"
        assert "#" in content, "bcdc-api-quirks missing # heading"
        assert "bcdc_type" in content
        assert "object_name" in content
        assert "queryable_via_wfs" in content
        # Bilingual — both EN and FR sections
        assert any(word in content for word in ("organization", "org"))

    # ------------------------------------------------------------------
    # template:// resources — {placeholder} syntax
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bc_wildfire_report_template_has_placeholders(self):
        """bc_wildfire_report_template contains required {placeholder} values."""
        r = FunctionResource.from_function(
            bc_wildfire_report_template, uri="template://bc/wildfire-report"
        )
        content = await r.read()
        assert "{fire_season}" in content, "Template missing {fire_season}"
        assert "{total_active_fires}" in content or "{total_fires}" in content
        assert "{largest_fire}" in content, "Template missing {largest_fire}"
        assert "{cause_breakdown}" in content or "{lightning_count}" in content
        assert content.startswith("#"), "Wildfire report template must start with # heading"

    @pytest.mark.asyncio
    async def test_bc_dataset_report_template_has_placeholders(self):
        """bc_dataset_report_template contains required {placeholder} values."""
        r = FunctionResource.from_function(
            bc_dataset_report_template, uri="template://bc/dataset-report"
        )
        content = await r.read()
        assert "{dataset_title}" in content or "{dataset_name}" in content
        assert "{organization}" in content, "Template missing {organization}"
        assert "{object_name}" in content, "Template missing {object_name}"
        assert "{queryable_via_wfs}" in content, "Template missing {queryable_via_wfs}"
        assert content.startswith("#"), "Dataset report template must start with # heading"

    # ------------------------------------------------------------------
    # Shared invariants
    # ------------------------------------------------------------------

    def test_all_resources_use_type_prefixed_uri(self):
        """All 7 BC resources use data://, docs://, or template:// URI prefix."""
        # Extract URIs from resource function attributes
        resource_funcs = [
            (bc_ministries, "data://bc/ministries"),
            (bc_wildfire_status_codes, "data://bc/wildfire-status-codes"),
            (bc_object_name_prefixes, "data://bc/object-name-prefixes"),
            (bc_wfs_query_guide, "docs://bc/wfs-query-guide"),
            (bc_bcdc_api_quirks, "docs://bc/bcdc-api-quirks"),
            (bc_wildfire_report_template, "template://bc/wildfire-report"),
            (bc_dataset_report_template, "template://bc/dataset-report"),
        ]
        valid_prefixes = ("data://", "docs://", "template://")
        for fn, uri in resource_funcs:
            assert any(uri.startswith(p) for p in valid_prefixes), (
                f"{fn.__name__} URI '{uri}' does not use data://, docs://, or template://"
            )

    def test_all_resources_use_bc_module_path(self):
        """All 7 BC resource URIs contain /bc/ in the path."""
        uris = [
            "data://bc/ministries",
            "data://bc/wildfire-status-codes",
            "data://bc/object-name-prefixes",
            "docs://bc/wfs-query-guide",
            "docs://bc/bcdc-api-quirks",
            "template://bc/wildfire-report",
            "template://bc/dataset-report",
        ]
        for uri in uris:
            assert "/bc/" in uri, f"URI '{uri}' does not contain /bc/"

    def test_no_resource_has_lang_parameter(self):
        """All 7 BC resource functions are zero-parameter (no lang or other params)."""
        resource_funcs = [
            bc_ministries,
            bc_wildfire_status_codes,
            bc_object_name_prefixes,
            bc_wfs_query_guide,
            bc_bcdc_api_quirks,
            bc_wildfire_report_template,
            bc_dataset_report_template,
        ]
        for fn in resource_funcs:
            sig = inspect.signature(fn)
            required_params = [
                name
                for name, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty
            ]
            assert required_params == [], (
                f"{fn.__name__} has required parameters {required_params}; "
                "resources must be zero-param functions"
            )
            # Also confirm no 'lang' param at all
            assert "lang" not in sig.parameters, (
                f"{fn.__name__} has 'lang' parameter — this would promote it to ResourceTemplate"
            )
