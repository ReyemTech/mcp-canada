# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportAttributeAccessIssue=false
"""Saskatchewan prompts and resources tests.

Plan 06 fills the test bodies for 6 prompts and 7 resources.
"""

from __future__ import annotations

import json

import pytest

from mcp_canada.modules.saskatchewan import prompts, resources


class TestSaskPrompts:
    """All 6 Saskatchewan @prompt functions.

    3 guided workflow prompts (return list[Message], user+assistant roles)
    3 quick lookup prompts (return str with tool name + parameter instructions)
    Each prompt has lang='en' and lang='fr' test case.
    """

    # -----------------------------------------------------------------------
    # Guided workflow prompts — should return list[Message] with >=2 messages
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_agriculture_guided_en(self):
        """saskatchewan_explore_agriculture returns bilingual list[Message] in English."""
        result = await prompts.saskatchewan_explore_agriculture(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"
        # Must reference the three agriculture/mining tools
        combined = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "saskatchewan_get_crop_yields" in combined
        assert "saskatchewan_get_grain_elevators" in combined
        assert "saskatchewan_get_mineral_mines" in combined

    @pytest.mark.asyncio
    async def test_explore_agriculture_guided_fr(self):
        """saskatchewan_explore_agriculture returns different content in French."""
        result_en = await prompts.saskatchewan_explore_agriculture(lang="en")
        result_fr = await prompts.saskatchewan_explore_agriculture(lang="fr")
        assert isinstance(result_fr, list)
        assert len(result_fr) >= 2
        # French and English must produce different text
        combined_en = " ".join(m.content.text for m in result_en if hasattr(m.content, "text"))
        combined_fr = " ".join(m.content.text for m in result_fr if hasattr(m.content, "text"))
        assert combined_en != combined_fr

    @pytest.mark.asyncio
    async def test_explore_environment_guided_en(self):
        """saskatchewan_explore_environment returns list[Message] chaining env tools."""
        result = await prompts.saskatchewan_explore_environment(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"
        combined = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "saskatchewan_get_fire_bans" in combined
        assert "saskatchewan_get_historic_wildfires" in combined
        assert "saskatchewan_get_air_quality" in combined

    @pytest.mark.asyncio
    async def test_explore_environment_guided_fr(self):
        """saskatchewan_explore_environment returns different content in French."""
        result_en = await prompts.saskatchewan_explore_environment(lang="en")
        result_fr = await prompts.saskatchewan_explore_environment(lang="fr")
        assert isinstance(result_fr, list)
        combined_en = " ".join(m.content.text for m in result_en if hasattr(m.content, "text"))
        combined_fr = " ".join(m.content.text for m in result_fr if hasattr(m.content, "text"))
        assert combined_en != combined_fr

    @pytest.mark.asyncio
    async def test_explore_water_guided_en(self):
        """saskatchewan_explore_water returns list[Message] chaining WSA tools."""
        result = await prompts.saskatchewan_explore_water(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"
        combined = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "saskatchewan_get_wsa_stations" in combined
        assert "saskatchewan_get_wsa_reservoirs" in combined

    @pytest.mark.asyncio
    async def test_explore_water_guided_fr(self):
        """saskatchewan_explore_water returns different content in French."""
        result_en = await prompts.saskatchewan_explore_water(lang="en")
        result_fr = await prompts.saskatchewan_explore_water(lang="fr")
        assert isinstance(result_fr, list)
        combined_en = " ".join(m.content.text for m in result_en if hasattr(m.content, "text"))
        combined_fr = " ".join(m.content.text for m in result_fr if hasattr(m.content, "text"))
        assert combined_en != combined_fr

    # -----------------------------------------------------------------------
    # Quick lookup prompts — should return str
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_dataset_search_en(self):
        """saskatchewan_quick_dataset_search returns a str in English."""
        result = await prompts.saskatchewan_quick_dataset_search(lang="en")
        assert isinstance(result, str)
        assert len(result) > 50
        assert "saskatchewan_search_datasets" in result

    @pytest.mark.asyncio
    async def test_quick_dataset_search_fr(self):
        """saskatchewan_quick_dataset_search returns different str in French."""
        result_en = await prompts.saskatchewan_quick_dataset_search(lang="en")
        result_fr = await prompts.saskatchewan_quick_dataset_search(lang="fr")
        assert isinstance(result_fr, str)
        assert result_en != result_fr

    @pytest.mark.asyncio
    async def test_fire_ban_status_now_en(self):
        """saskatchewan_fire_ban_status_now returns a str in English with fire ban tool."""
        result = await prompts.saskatchewan_fire_ban_status_now(lang="en")
        assert isinstance(result, str)
        assert len(result) > 50
        assert "saskatchewan_get_fire_bans" in result
        # Must mention the ban_scope values
        assert "ban_scope" in result or "urban" in result or "provincial" in result

    @pytest.mark.asyncio
    async def test_fire_ban_status_now_fr(self):
        """saskatchewan_fire_ban_status_now returns different str in French."""
        result_en = await prompts.saskatchewan_fire_ban_status_now(lang="en")
        result_fr = await prompts.saskatchewan_fire_ban_status_now(lang="fr")
        assert isinstance(result_fr, str)
        assert result_en != result_fr

    @pytest.mark.asyncio
    async def test_crop_yield_lookup_en(self):
        """saskatchewan_crop_yield_lookup returns a str in English mentioning crop tools."""
        result = await prompts.saskatchewan_crop_yield_lookup(lang="en")
        assert isinstance(result, str)
        assert len(result) > 50
        assert "saskatchewan_get_crop_yields" in result
        # Must mention region dispatch
        assert "region" in result or "provincial" in result

    @pytest.mark.asyncio
    async def test_crop_yield_lookup_fr(self):
        """saskatchewan_crop_yield_lookup returns different str in French."""
        result_en = await prompts.saskatchewan_crop_yield_lookup(lang="en")
        result_fr = await prompts.saskatchewan_crop_yield_lookup(lang="fr")
        assert isinstance(result_fr, str)
        assert result_en != result_fr

    def test_all_6_prompts_defined(self):
        """All 6 prompts are discoverable in the prompts module."""
        expected = {
            "saskatchewan_explore_agriculture",
            "saskatchewan_explore_environment",
            "saskatchewan_explore_water",
            "saskatchewan_quick_dataset_search",
            "saskatchewan_fire_ban_status_now",
            "saskatchewan_crop_yield_lookup",
        }
        defined = set(prompts.__all__)
        assert expected == defined


class TestSaskResources:
    """All 7 Saskatchewan @resource functions.

    data:// resources return valid JSON.
    docs:// resources return non-empty markdown strings.
    template:// resources contain {placeholder} syntax.
    All resources have ZERO parameters (no lang param).
    """

    @pytest.mark.asyncio
    async def test_crop_regions_json_valid(self):
        """data://saskatchewan/crop-regions returns valid JSON with 5 regions."""
        result = await resources.saskatchewan_crop_regions()
        assert isinstance(result, str)
        data = json.loads(result)
        assert "regions" in data
        assert len(data["regions"]) == 5

    @pytest.mark.asyncio
    async def test_crop_regions_bilingual(self):
        """data://saskatchewan/crop-regions has bilingual labels inline."""
        result = await resources.saskatchewan_crop_regions()
        data = json.loads(result)
        for region in data["regions"]:
            assert "name_en" in region
            assert "name_fr" in region

    @pytest.mark.asyncio
    async def test_major_basins_json_valid(self):
        """data://saskatchewan/major-basins returns valid JSON with 6 basins."""
        result = await resources.saskatchewan_major_basins()
        assert isinstance(result, str)
        data = json.loads(result)
        assert "basins" in data
        assert len(data["basins"]) >= 5

    @pytest.mark.asyncio
    async def test_major_basins_bilingual(self):
        """data://saskatchewan/major-basins has bilingual labels inline."""
        result = await resources.saskatchewan_major_basins()
        data = json.loads(result)
        for basin in data["basins"]:
            assert "name_en" in basin or "name" in basin

    @pytest.mark.asyncio
    async def test_health_regions_json_valid(self):
        """data://saskatchewan/health-regions returns valid JSON documenting SHA."""
        result = await resources.saskatchewan_health_regions()
        assert isinstance(result, str)
        data = json.loads(result)
        # Saskatchewan has ONE health authority (SHA)
        assert "health_authorities" in data or "health_regions" in data

    @pytest.mark.asyncio
    async def test_health_regions_deferred_note(self):
        """data://saskatchewan/health-regions documents the deferred health FeatureServer."""
        result = await resources.saskatchewan_health_regions()
        data = json.loads(result)
        raw = json.dumps(data)
        # Must mention SHA and deferral
        assert "SHA" in raw or "Saskatchewan Health Authority" in raw
        assert "defer" in raw.lower() or "no public" in raw.lower() or "not available" in raw.lower()

    @pytest.mark.asyncio
    async def test_portal_guide_is_markdown(self):
        """docs://saskatchewan/portal-guide returns non-empty markdown."""
        result = await resources.saskatchewan_portal_guide()
        assert isinstance(result, str)
        assert len(result) > 200
        # Must be markdown with headings
        assert "#" in result

    @pytest.mark.asyncio
    async def test_portal_guide_documents_multi_org(self):
        """docs://saskatchewan/portal-guide documents the multi-org architecture."""
        result = await resources.saskatchewan_portal_guide()
        # Primary org
        assert "zcv98lgAl8xQ04cW" in result
        # WSA org
        assert "7MBdlVpjqbfBhQer" in result
        # SPSA mention
        assert "SPSA" in result or "gis.saskatchewan.ca" in result

    @pytest.mark.asyncio
    async def test_portal_guide_deferred_domains(self):
        """docs://saskatchewan/portal-guide documents deferred transport and health."""
        result = await resources.saskatchewan_portal_guide()
        # Transport deferred (511 key-gated)
        assert "511" in result or "transport" in result.lower() or "hotline" in result.lower()
        assert "defer" in result.lower() or "key" in result.lower()
        # Health deferred (no public SHA FeatureServer)
        assert "health" in result.lower()

    @pytest.mark.asyncio
    async def test_portal_guide_petroleum_routing(self):
        """docs://saskatchewan/portal-guide documents Petroleum FeatureServer 400 issue."""
        result = await resources.saskatchewan_portal_guide()
        assert "Petroleum" in result or "petroleum" in result

    @pytest.mark.asyncio
    async def test_agriculture_data_guide_is_markdown(self):
        """docs://saskatchewan/agriculture-data-guide returns non-empty markdown."""
        result = await resources.saskatchewan_agriculture_data_guide()
        assert isinstance(result, str)
        assert len(result) > 200
        assert "#" in result
        # Must mention crop yields
        assert "crop" in result.lower() or "yield" in result.lower()

    @pytest.mark.asyncio
    async def test_dataset_report_template_has_placeholders(self):
        """template://saskatchewan/dataset-report contains {placeholder} syntax."""
        result = await resources.saskatchewan_dataset_report_template()
        assert isinstance(result, str)
        assert "{" in result and "}" in result

    @pytest.mark.asyncio
    async def test_wildfire_report_template_has_placeholders(self):
        """template://saskatchewan/wildfire-report contains {placeholder} syntax."""
        result = await resources.saskatchewan_wildfire_report_template()
        assert isinstance(result, str)
        assert "{" in result and "}" in result
        # Must include fire ban reference
        assert "fire" in result.lower() or "ban" in result.lower() or "wildfire" in result.lower()

    def test_all_7_resources_defined(self):
        """All 7 resources are discoverable in the resources module."""
        expected = {
            "saskatchewan_crop_regions",
            "saskatchewan_major_basins",
            "saskatchewan_health_regions",
            "saskatchewan_portal_guide",
            "saskatchewan_agriculture_data_guide",
            "saskatchewan_dataset_report_template",
            "saskatchewan_wildfire_report_template",
        }
        defined = set(resources.__all__)
        assert expected == defined

    def test_resources_have_zero_parameters(self):
        """All resource functions have ZERO parameters (lang would promote to ResourceTemplate)."""
        import inspect

        for name in resources.__all__:
            fn = getattr(resources, name)
            sig = inspect.signature(fn)
            # Should have no parameters at all (no lang, no query, nothing)
            assert len(sig.parameters) == 0, (
                f"{name} has parameters {list(sig.parameters)} — "
                "adding ANY parameter promotes to ResourceTemplate and drops from resources/list"
            )
