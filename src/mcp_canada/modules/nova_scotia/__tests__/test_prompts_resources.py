"""Unit tests for Nova Scotia module prompts.py and resources.py.

TDD: Tests written first (RED), then implementation (GREEN).
"""

from __future__ import annotations

import json

import pytest
import pytest_asyncio  # noqa: F401 — ensures asyncio mode available


class TestNsPrompts:
    """Tests for Nova Scotia @prompt functions.

    Guided workflow prompts (list[Message]) must verify:
    - Returns list with at least 2 messages (user + assistant roles)
    - First message has role="user"
    - Second message has role="assistant"
    - Content references correct ns_ tool names
    - lang="fr" produces different content from lang="en"

    Quick lookup prompts (str) must verify:
    - Returns a string
    - String mentions the correct ns_ tool name and key parameters
    - lang="fr" produces different content
    """

    # -----------------------------------------------------------------------
    # Guided workflow: ns_explore_aquaculture_data
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_explore_aquaculture_data_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_explore_aquaculture_data
        result = await ns_explore_aquaculture_data(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_ns_explore_aquaculture_data_roles(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_explore_aquaculture_data
        result = await ns_explore_aquaculture_data(lang="en")
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_ns_explore_aquaculture_data_references_tools(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_explore_aquaculture_data
        result = await ns_explore_aquaculture_data(lang="en")
        assistant_text = result[1].content.text if hasattr(result[1].content, "text") else str(result[1].content)
        assert "ns_get_marine_aquaculture_leases" in assistant_text
        assert "ns_get_landbased_aquaculture_licenses" in assistant_text
        assert "ns_get_fish_hatchery_stocking" in assistant_text
        assert "ns_get_aquaculture_production" in assistant_text

    @pytest.mark.asyncio
    async def test_ns_explore_aquaculture_data_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_explore_aquaculture_data
        en = await ns_explore_aquaculture_data(lang="en")
        fr = await ns_explore_aquaculture_data(lang="fr")
        en_text = en[0].content.text if hasattr(en[0].content, "text") else str(en[0].content)
        fr_text = fr[0].content.text if hasattr(fr[0].content, "text") else str(fr[0].content)
        assert en_text != fr_text

    # -----------------------------------------------------------------------
    # Guided workflow: ns_health_zone_analysis
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_health_zone_analysis_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_health_zone_analysis
        result = await ns_health_zone_analysis(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_ns_health_zone_analysis_roles(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_health_zone_analysis
        result = await ns_health_zone_analysis(lang="en")
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_ns_health_zone_analysis_references_tools(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_health_zone_analysis
        result = await ns_health_zone_analysis(lang="en")
        assistant_text = result[1].content.text if hasattr(result[1].content, "text") else str(result[1].content)
        assert "ns_get_health_facilities" in assistant_text
        assert "ns_get_chronic_disease_prevalence" in assistant_text
        assert "ns_get_vital_statistics" in assistant_text

    @pytest.mark.asyncio
    async def test_ns_health_zone_analysis_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_health_zone_analysis
        en = await ns_health_zone_analysis(lang="en")
        fr = await ns_health_zone_analysis(lang="fr")
        en_text = en[0].content.text if hasattr(en[0].content, "text") else str(en[0].content)
        fr_text = fr[0].content.text if hasattr(fr[0].content, "text") else str(fr[0].content)
        assert en_text != fr_text

    # -----------------------------------------------------------------------
    # Guided workflow: ns_water_quality_analysis
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_water_quality_analysis_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_water_quality_analysis
        result = await ns_water_quality_analysis(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_ns_water_quality_analysis_roles(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_water_quality_analysis
        result = await ns_water_quality_analysis(lang="en")
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_ns_water_quality_analysis_references_tools(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_water_quality_analysis
        result = await ns_water_quality_analysis(lang="en")
        assistant_text = result[1].content.text if hasattr(result[1].content, "text") else str(result[1].content)
        assert "ns_get_water_quality_monitoring" in assistant_text
        assert "ns_get_boil_water_advisories" in assistant_text

    @pytest.mark.asyncio
    async def test_ns_water_quality_analysis_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_water_quality_analysis
        en = await ns_water_quality_analysis(lang="en")
        fr = await ns_water_quality_analysis(lang="fr")
        en_text = en[0].content.text if hasattr(en[0].content, "text") else str(en[0].content)
        fr_text = fr[0].content.text if hasattr(fr[0].content, "text") else str(fr[0].content)
        assert en_text != fr_text

    # -----------------------------------------------------------------------
    # Quick lookup: ns_quick_find_dataset
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_quick_find_dataset_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_find_dataset
        result = await ns_quick_find_dataset(lang="en")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_ns_quick_find_dataset_mentions_tool(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_find_dataset
        result = await ns_quick_find_dataset(lang="en")
        assert "ns_search_datasets" in result

    @pytest.mark.asyncio
    async def test_ns_quick_find_dataset_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_find_dataset
        en = await ns_quick_find_dataset(lang="en")
        fr = await ns_quick_find_dataset(lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Quick lookup: ns_quick_protected_areas
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_quick_protected_areas_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_protected_areas
        result = await ns_quick_protected_areas(lang="en")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_ns_quick_protected_areas_mentions_tool(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_protected_areas
        result = await ns_quick_protected_areas(lang="en")
        assert "ns_get_protected_areas" in result

    @pytest.mark.asyncio
    async def test_ns_quick_protected_areas_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_protected_areas
        en = await ns_quick_protected_areas(lang="en")
        fr = await ns_quick_protected_areas(lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Quick lookup: ns_quick_vital_stats
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_quick_vital_stats_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_vital_stats
        result = await ns_quick_vital_stats(lang="en")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_ns_quick_vital_stats_mentions_tool(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_vital_stats
        result = await ns_quick_vital_stats(lang="en")
        assert "ns_get_vital_statistics" in result

    @pytest.mark.asyncio
    async def test_ns_quick_vital_stats_bilingual(self) -> None:
        from mcp_canada.modules.nova_scotia.prompts import ns_quick_vital_stats
        en = await ns_quick_vital_stats(lang="en")
        fr = await ns_quick_vital_stats(lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Total count: 6 prompts discoverable
    # -----------------------------------------------------------------------

    def test_six_prompts_defined(self) -> None:
        from mcp_canada.modules.nova_scotia import prompts as _m
        # @prompt returns a callable; count via __all__ which lists all 6
        assert hasattr(_m, "__all__"), "prompts.py must define __all__"
        assert len(_m.__all__) == 6, f"Expected 6 prompts in __all__, found {len(_m.__all__)}"
        # Verify each is callable
        for name in _m.__all__:
            assert hasattr(_m, name), f"Prompt {name} missing from module"
            assert callable(getattr(_m, name)), f"Prompt {name} must be callable"


class TestNsResources:
    """Tests for Nova Scotia @resource functions.

    data:// resources must verify:
    - Returns valid JSON string (json.loads succeeds)
    - Contains expected top-level keys

    docs:// resources must verify:
    - Returns a string
    - Contains expected headings or sections

    template:// resources must verify:
    - Returns a string with {placeholder} syntax

    Zero-parameter compliance: all functions tested above appear in resources/list.
    """

    # -----------------------------------------------------------------------
    # data://ns/categories
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_categories_returns_valid_json(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_categories
        result = await ns_categories()
        parsed = json.loads(result)
        assert "categories" in parsed
        assert "_meta" in parsed

    @pytest.mark.asyncio
    async def test_ns_categories_has_expected_entries(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_categories
        result = await ns_categories()
        parsed = json.loads(result)
        # Must include key NS categories
        assert any("Fishing" in str(c) for c in parsed["categories"])
        assert any("Health" in str(c) for c in parsed["categories"])
        assert len(parsed["categories"]) >= 10

    # -----------------------------------------------------------------------
    # data://ns/health-zones
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_health_zones_returns_valid_json(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_health_zones
        result = await ns_health_zones()
        parsed = json.loads(result)
        assert "zones" in parsed
        assert "_meta" in parsed

    @pytest.mark.asyncio
    async def test_ns_health_zones_has_four_zones(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_health_zones
        result = await ns_health_zones()
        parsed = json.loads(result)
        assert len(parsed["zones"]) == 4

    @pytest.mark.asyncio
    async def test_ns_health_zones_has_expected_zone_names(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_health_zones
        result = await ns_health_zones()
        parsed = json.loads(result)
        names_en = [z["name_en"] for z in parsed["zones"]]
        assert "Western" in names_en
        assert "Northern" in names_en
        assert "Eastern" in names_en
        assert "Central" in names_en

    # -----------------------------------------------------------------------
    # data://ns/fishing-areas
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_fishing_areas_returns_valid_json(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_fishing_areas
        result = await ns_fishing_areas()
        parsed = json.loads(result)
        assert "species_types" in parsed or "fishing_areas" in parsed or "areas" in parsed

    @pytest.mark.asyncio
    async def test_ns_fishing_areas_has_species_types(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_fishing_areas
        result = await ns_fishing_areas()
        parsed = json.loads(result)
        # Should mention Shellfish, Finfish, Marine Plant
        content = json.dumps(parsed)
        assert "Shellfish" in content
        assert "Finfish" in content

    # -----------------------------------------------------------------------
    # data://ns/departments
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_departments_returns_valid_json(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_departments
        result = await ns_departments()
        parsed = json.loads(result)
        assert "departments" in parsed
        assert "_meta" in parsed

    @pytest.mark.asyncio
    async def test_ns_departments_has_fisheries_entry(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_departments
        result = await ns_departments()
        parsed = json.loads(result)
        names = [d if isinstance(d, str) else d.get("name_en", "") for d in parsed["departments"]]
        assert any("Fisheries" in n or "Aquaculture" in n for n in names)

    # -----------------------------------------------------------------------
    # docs://ns/socrata-guide
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_socrata_guide_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_socrata_guide
        result = await ns_socrata_guide()
        assert isinstance(result, str)
        assert len(result) > 100

    @pytest.mark.asyncio
    async def test_ns_socrata_guide_mentions_soql_params(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_socrata_guide
        result = await ns_socrata_guide()
        assert "$where" in result
        assert "$select" in result
        assert "$order" in result
        assert "$limit" in result

    @pytest.mark.asyncio
    async def test_ns_socrata_guide_documents_categories_workaround(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_socrata_guide
        result = await ns_socrata_guide()
        # Must document the broken categories= param workaround
        assert "categories=" in result or "categories" in result
        assert "broken" in result.lower() or "not work" in result.lower() or "workaround" in result.lower()

    # -----------------------------------------------------------------------
    # docs://ns/portal-guide
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_portal_guide_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_portal_guide
        result = await ns_portal_guide()
        assert isinstance(result, str)
        assert len(result) > 100

    @pytest.mark.asyncio
    async def test_ns_portal_guide_documents_deferred_transport(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_portal_guide
        result = await ns_portal_guide()
        assert "511" in result or "transport" in result.lower() or "Transport" in result
        assert "defer" in result.lower() or "HTML" in result

    @pytest.mark.asyncio
    async def test_ns_portal_guide_documents_licence(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_portal_guide
        result = await ns_portal_guide()
        assert "Open Government Licence" in result or "Nova Scotia" in result
        assert "attribution" in result.lower() or "Attribution" in result

    # -----------------------------------------------------------------------
    # template://ns/aquaculture-report
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ns_aquaculture_report_template_returns_str(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_aquaculture_report_template
        result = await ns_aquaculture_report_template()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_ns_aquaculture_report_template_has_placeholders(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_aquaculture_report_template
        result = await ns_aquaculture_report_template()
        assert "{" in result and "}" in result

    @pytest.mark.asyncio
    async def test_ns_aquaculture_report_template_has_key_sections(self) -> None:
        from mcp_canada.modules.nova_scotia.resources import ns_aquaculture_report_template
        result = await ns_aquaculture_report_template()
        assert "county" in result.lower() or "County" in result
        assert "production" in result.lower() or "species" in result.lower()

    # -----------------------------------------------------------------------
    # Total count: 7 resources defined
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_seven_resources_defined(self) -> None:
        from mcp_canada.modules.nova_scotia import resources as _m
        # @resource returns a callable; count via __all__ which lists all 7
        assert hasattr(_m, "__all__"), "resources.py must define __all__"
        assert len(_m.__all__) == 7, f"Expected 7 resources in __all__, found {len(_m.__all__)}"
        # Verify each is callable
        for name in _m.__all__:
            assert hasattr(_m, name), f"Resource {name} missing from module"
            assert callable(getattr(_m, name)), f"Resource {name} must be callable"

    # -----------------------------------------------------------------------
    # URI scheme checks
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resource_uris_have_ns_prefix(self) -> None:
        from mcp_canada.modules.nova_scotia import resources as _m
        import inspect
        from fastmcp.resources import Resource
        for name, obj in inspect.getmembers(_m):
            if isinstance(obj, Resource):
                uri = str(obj.uri)
                assert "ns/" in uri or uri.startswith("data://ns") or "://ns/" in uri, (
                    f"Resource {name} URI {uri!r} missing ns/ prefix"
                )
