# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content unions), and several cases
# deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportAttributeAccessIssue=false
"""Unit tests for new_brunswick/prompts.py and new_brunswick/resources.py.

TDD: assertions written first (RED against the Wave 0 import-only skeletons),
then prompts.py/resources.py filled in (GREEN).
"""

from __future__ import annotations

import inspect
import json
import re

import pytest


def test_prompts_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import prompts  # noqa: F401


def test_resources_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import resources  # noqa: F401


class TestModuleDescription:
    """G3 (Codex round 2): MODULE_DESCRIPTION is stale in two ways — it omits
    gnb.socrata.com (a fourth upstream surface added at the Wave 0 checkpoint)
    and still advertises minerals/parks as curated GeoNB coverage even though
    the same checkpoint dropped both to the long tail (reachable only via
    nb_query_geonb_layer). meta/list_modules.py returns MODULE_DESCRIPTION
    verbatim and the generated catalogue repeats it, so both errors are
    agent-visible.
    """

    def test_describes_four_upstream_surfaces_including_gnb_socrata(self):
        from mcp_canada.modules.new_brunswick import MODULE_DESCRIPTION

        assert "gnb.socrata.com" in MODULE_DESCRIPTION
        assert "four upstream surfaces" in MODULE_DESCRIPTION

    def test_fr_description_also_names_gnb_socrata(self):
        from mcp_canada.modules.new_brunswick import MODULE_DESCRIPTION_FR

        assert "gnb.socrata.com" in MODULE_DESCRIPTION_FR

    def test_minerals_and_parks_not_advertised_as_curated_coverage(self):
        # Dropped to the long tail at the 21-01 checkpoint (option-a) — no
        # dedicated nb_get_* tool exists for either, so the description must
        # not list them alongside genuinely curated GeoNB layers.
        from mcp_canada.modules.new_brunswick import MODULE_DESCRIPTION

        assert "minerals, parks" not in MODULE_DESCRIPTION


def _text(content) -> str:
    return content.text if hasattr(content, "text") else str(content)


def _nb_tool_tokens(text: str) -> set[str]:
    """Extract every nb_-prefixed identifier-shaped token from free text."""
    return set(re.findall(r"\bnb_[a-z0-9_]+\b", text))


class TestNbPrompts:
    """6 @prompt functions: 3 guided workflows (list[Message]) + 3 quick lookups (str).

    Every nb_-prefixed tool name referenced in any prompt's OUTPUT must be a
    member of constants.ALL_NB_TOOL_NAMES — the manifest locked in 21-01 after
    the Task 2 discovery-surface checkpoint.
    """

    # -----------------------------------------------------------------------
    # Guided workflow: nb_flood_risk_assessment
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_roles(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_names_at_least_three_distinct_tools(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        text = _text(result[1].content)
        assert "nb_get_flood_hazard_areas" in text
        assert "nb_get_historical_floods" in text
        assert "nb_get_wetlands" in text
        assert "nb_get_civic_addresses" in text
        assert len(_nb_tool_tokens(text)) >= 3

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_cites_technical_and_sheet_fields(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        text = _text(result[1].content)
        assert "Technical_" in text
        assert "Sheet_Numb" in text

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        en = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        fr = await nb_flood_risk_assessment(location="Fredericton", lang="fr")
        assert _text(en[1].content) != _text(fr[1].content)

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_does_not_invent_a_location_parameter(self) -> None:
        # G4 (Codex round 2): none of nb_get_flood_hazard_areas,
        # nb_get_historical_floods or nb_get_wetlands accept a location/place
        # name — they're filtered by map sheet, event and wetland
        # class/status respectively. The prompt must say so explicitly
        # rather than implying a location can be passed to those tools, and
        # must resolve the location via nb_get_civic_addresses BEFORE
        # instructing the flood-layer calls (not after, as a final step).
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="en")
        text = _text(result[1].content)
        assert "accepts a place name" in text.lower()
        civic_idx = text.index("nb_get_civic_addresses")
        hazard_idx = text.index("nb_get_flood_hazard_areas")
        assert civic_idx < hazard_idx, (
            "location resolution via nb_get_civic_addresses must be "
            "instructed before the flood-layer tool calls, not after"
        )

    @pytest.mark.asyncio
    async def test_flood_risk_assessment_fr_does_not_invent_a_location_parameter(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_flood_risk_assessment
        result = await nb_flood_risk_assessment(location="Fredericton", lang="fr")
        text = _text(result[1].content)
        civic_idx = text.index("nb_get_civic_addresses")
        hazard_idx = text.index("nb_get_flood_hazard_areas")
        assert civic_idx < hazard_idx

    # -----------------------------------------------------------------------
    # Guided workflow: nb_crown_land_report
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_crown_land_report_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_crown_land_report
        result = await nb_crown_land_report(county="York", lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_crown_land_report_names_at_least_three_distinct_tools(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_crown_land_report
        result = await nb_crown_land_report(county="York", lang="en")
        text = _text(result[1].content)
        assert "nb_get_crown_land" in text
        assert "nb_query_geonb_layer" in text
        assert len(_nb_tool_tokens(text)) >= 3

    @pytest.mark.asyncio
    async def test_crown_land_report_warns_holder_is_not_a_name(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_crown_land_report
        result = await nb_crown_land_report(county="York", lang="en")
        text = _text(result[1].content)
        assert "HOLDER" in text
        assert "integer" in text.lower() or "entier" in text.lower()

    @pytest.mark.asyncio
    async def test_crown_land_report_never_names_dropped_curated_tools(self) -> None:
        """Mineral occurrences / provincial parks have no dedicated nb_get_* tool
        since the 21-01 checkpoint (option-a) — only nb_query_geonb_layer reaches them."""
        from mcp_canada.modules.new_brunswick.prompts import nb_crown_land_report
        result = await nb_crown_land_report(county="York", lang="en")
        text = _text(result[1].content)
        assert "nb_get_mineral_occurrences" not in text
        assert "nb_get_provincial_parks" not in text

    @pytest.mark.asyncio
    async def test_crown_land_report_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_crown_land_report
        en = await nb_crown_land_report(county="York", lang="en")
        fr = await nb_crown_land_report(county="York", lang="fr")
        assert _text(en[1].content) != _text(fr[1].content)

    # -----------------------------------------------------------------------
    # Guided workflow: nb_property_lookup
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_property_lookup_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_property_lookup
        result = await nb_property_lookup(pid="01234567", lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_property_lookup_names_at_least_three_distinct_tools(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_property_lookup
        result = await nb_property_lookup(pid="01234567", lang="en")
        text = _text(result[1].content)
        assert "nb_get_parcels" in text
        assert "nb_get_civic_addresses" in text
        assert "nb_query_geonb_layer" in text
        assert len(_nb_tool_tokens(text)) >= 3

    @pytest.mark.asyncio
    async def test_property_lookup_states_filter_required(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_property_lookup
        result = await nb_property_lookup(pid="01234567", lang="en")
        text = _text(result[1].content)
        assert "604,520" in text
        assert "373,172" in text

    @pytest.mark.asyncio
    async def test_property_lookup_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_property_lookup
        en = await nb_property_lookup(pid="01234567", lang="en")
        fr = await nb_property_lookup(pid="01234567", lang="fr")
        assert _text(en[1].content) != _text(fr[1].content)

    # -----------------------------------------------------------------------
    # Quick lookup: nb_quick_dataset_search
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_dataset_search_returns_str(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_quick_dataset_search
        result = await nb_quick_dataset_search(query="flood", lang="en")
        assert isinstance(result, str)
        assert "nb_search_datasets" in result

    @pytest.mark.asyncio
    async def test_quick_dataset_search_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_quick_dataset_search
        en = await nb_quick_dataset_search(query="flood", lang="en")
        fr = await nb_quick_dataset_search(query="flood", lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Quick lookup: nb_health_facility_finder
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_health_facility_finder_returns_str(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_health_facility_finder
        result = await nb_health_facility_finder(facility_type="pharmacy", lang="en")
        assert isinstance(result, str)
        assert "nb_get_health_facilities" in result

    @pytest.mark.asyncio
    async def test_health_facility_finder_lists_valid_facility_types(self) -> None:
        from mcp_canada.modules.new_brunswick import constants as c
        from mcp_canada.modules.new_brunswick.prompts import nb_health_facility_finder
        result = await nb_health_facility_finder(facility_type="", lang="en")
        for key in c.HEALTH_FACILITY_LAYERS:
            assert key in result

    @pytest.mark.asyncio
    async def test_health_facility_finder_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_health_facility_finder
        en = await nb_health_facility_finder(facility_type="pharmacy", lang="en")
        fr = await nb_health_facility_finder(facility_type="pharmacy", lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Quick lookup: nb_bilingual_dataset_lookup
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bilingual_dataset_lookup_returns_str(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_bilingual_dataset_lookup
        result = await nb_bilingual_dataset_lookup(query="flood", lang="en")
        assert isinstance(result, str)
        assert "nb_search_datasets" in result or "nb_get_dataset_details" in result

    @pytest.mark.asyncio
    async def test_bilingual_dataset_lookup_warns_duplicate_records(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_bilingual_dataset_lookup
        result = await nb_bilingual_dataset_lookup(query="flood", lang="en")
        assert "duplicate" in result.lower() or "separate" in result.lower()

    @pytest.mark.asyncio
    async def test_bilingual_dataset_lookup_bilingual(self) -> None:
        from mcp_canada.modules.new_brunswick.prompts import nb_bilingual_dataset_lookup
        en = await nb_bilingual_dataset_lookup(query="flood", lang="en")
        fr = await nb_bilingual_dataset_lookup(query="flood", lang="fr")
        assert en != fr

    # -----------------------------------------------------------------------
    # Total count: 6 prompts discoverable
    # -----------------------------------------------------------------------

    def test_six_prompts_defined(self) -> None:
        from mcp_canada.modules.new_brunswick import prompts as _m
        assert hasattr(_m, "__all__"), "prompts.py must define __all__"
        assert len(_m.__all__) == 6, f"Expected 6 prompts in __all__, found {len(_m.__all__)}"
        for name in _m.__all__:
            assert hasattr(_m, name), f"Prompt {name} missing from module"
            assert callable(getattr(_m, name)), f"Prompt {name} must be callable"

    def test_no_mcp_decorator_used(self) -> None:
        """No line is an actual `@mcp.*` decorator (prose mentioning it, e.g. in a
        docstring explaining what NOT to do, is expected and not a violation —
        the 21-01 precedent for this exact pattern in tools.py)."""
        import pathlib
        src = pathlib.Path(
            inspect.getfile(__import__("mcp_canada.modules.new_brunswick.prompts", fromlist=["x"]))
        ).read_text()
        for line in src.splitlines():
            assert not line.strip().startswith("@mcp."), f"Found @mcp. decorator: {line}"

    # -----------------------------------------------------------------------
    # Manifest cross-check: every nb_-prefixed tool token in every prompt's
    # output is a member of constants.ALL_NB_TOOL_NAMES (the locked manifest).
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_every_referenced_tool_name_is_in_the_locked_manifest(self) -> None:
        from mcp_canada.modules.new_brunswick import constants as c
        from mcp_canada.modules.new_brunswick import prompts as p

        names = set(c.ALL_NB_TOOL_NAMES)
        bad: list[tuple[str, str]] = []
        for prompt_name in p.__all__:
            fn = getattr(p, prompt_name)
            out = await fn(lang="en")
            text = out if isinstance(out, str) else " ".join(_text(m.content) for m in out)
            # Exclude the prompt's own name (a prompt, not a tool) from the scan.
            tokens = _nb_tool_tokens(text) - {prompt_name}
            for tok in tokens:
                if tok not in names:
                    bad.append((prompt_name, tok))
        assert not bad, f"Prompt(s) reference tool name(s) outside ALL_NB_TOOL_NAMES: {bad}"


class TestNbResources:
    """7 zero-parameter @resource functions across data://, docs://, template://.

    Zero-parameter compliance: any parameter (including lang) would promote a
    function to a ResourceTemplate and remove it from resources/list.
    """

    # -----------------------------------------------------------------------
    # data://nb/geonb-services
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_geonb_services_returns_valid_json(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        assert "services" in parsed
        assert "_meta" in parsed

    @pytest.mark.asyncio
    async def test_geonb_services_has_62_entries(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        assert len(parsed["services"]) == 62

    @pytest.mark.asyncio
    async def test_geonb_services_entries_have_required_fields(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        for entry in parsed["services"]:
            assert "name" in entry
            assert "department" in entry
            assert "curated_tool" in entry  # present, possibly null

    @pytest.mark.asyncio
    async def test_geonb_services_excluded_entries_have_a_reason(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        excluded = [e for e in parsed["services"] if e["status"] == "excluded"]
        assert len(excluded) >= 5  # at minimum the 5 basemaps
        for entry in excluded:
            assert entry["reason"]

    @pytest.mark.asyncio
    async def test_geonb_services_curated_tools_are_in_the_locked_manifest(self) -> None:
        from mcp_canada.modules.new_brunswick import constants as c
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        names = set(c.ALL_NB_TOOL_NAMES)
        cited = {e["curated_tool"] for e in parsed["services"] if e["curated_tool"]}
        assert cited, "expected at least one curated tool cited"
        assert cited <= names

    @pytest.mark.asyncio
    async def test_geonb_services_notes_crown_land_layer_3(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_services
        result = await nb_geonb_services()
        parsed = json.loads(result)
        crown_land = next(e for e in parsed["services"] if e["name"] == "GeoNB_DNR_Crown_Land")
        assert crown_land["curated_layer_id"] == 3
        assert crown_land["curated_tool"] == "nb_get_crown_land"

    # -----------------------------------------------------------------------
    # data://nb/counties
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_counties_returns_valid_json(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_counties
        result = await nb_counties()
        parsed = json.loads(result)
        assert "counties" in parsed
        assert "_meta" in parsed

    @pytest.mark.asyncio
    async def test_counties_has_15_entries_with_both_languages(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_counties
        result = await nb_counties()
        parsed = json.loads(result)
        assert len(parsed["counties"]) == 15
        for county in parsed["counties"]:
            assert county["name_en"]
            assert county["name_fr"]

    @pytest.mark.asyncio
    async def test_counties_includes_saint_john_and_york(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_counties
        result = await nb_counties()
        parsed = json.loads(result)
        names_en = [c["name_en"] for c in parsed["counties"]]
        assert "Saint John" in names_en
        assert "York" in names_en

    # -----------------------------------------------------------------------
    # data://nb/health-regions
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_health_regions_returns_valid_json(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_health_regions
        result = await nb_health_regions()
        parsed = json.loads(result)
        assert "authorities" in parsed
        assert "facility_types" in parsed

    @pytest.mark.asyncio
    async def test_health_regions_has_horizon_and_vitalite(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_health_regions
        result = await nb_health_regions()
        parsed = json.loads(result)
        ids = [a["id"] for a in parsed["authorities"]]
        assert "horizon" in ids
        assert "vitalite" in ids

    @pytest.mark.asyncio
    async def test_health_regions_facility_types_match_constants(self) -> None:
        from mcp_canada.modules.new_brunswick import constants as c
        from mcp_canada.modules.new_brunswick.resources import nb_health_regions
        result = await nb_health_regions()
        parsed = json.loads(result)
        values = {f["value"] for f in parsed["facility_types"]}
        assert values == set(c.HEALTH_FACILITY_LAYERS.keys())

    # -----------------------------------------------------------------------
    # data://nb/school-districts
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_school_districts_returns_valid_json(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_school_districts
        result = await nb_school_districts()
        parsed = json.loads(result)
        assert "sectors" in parsed

    @pytest.mark.asyncio
    async def test_school_districts_has_anglophone_and_francophone(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_school_districts
        result = await nb_school_districts()
        parsed = json.loads(result)
        ids = [s["id"] for s in parsed["sectors"]]
        assert "anglophone" in ids
        assert "francophone" in ids

    @pytest.mark.asyncio
    async def test_school_districts_notes_truncated_field_names(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_school_districts
        result = await nb_school_districts()
        parsed = json.loads(result)
        content = json.dumps(parsed)
        assert "strID" in content

    # -----------------------------------------------------------------------
    # docs://nb/portal-guide
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_portal_guide_returns_str_with_heading(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_portal_guide
        result = await nb_portal_guide()
        assert isinstance(result, str)
        assert result.strip().startswith("#")

    @pytest.mark.asyncio
    async def test_portal_guide_documents_every_surface(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_portal_guide
        result = await nb_portal_guide()
        assert "geonb.snb.ca" in result
        assert "open.canada.ca" in result
        assert "gnb.socrata.com" in result
        assert "511.gnb.ca" in result
        assert "NEW_BRUNSWICK_511_KEY" in result

    @pytest.mark.asyncio
    async def test_portal_guide_documents_dead_ends(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_portal_guide
        result = await nb_portal_guide()
        assert "data.gnb.ca" in result
        assert "opendata.gnb.ca" in result
        assert "nbopendata.ca" in result
        assert "401" in result

    @pytest.mark.asyncio
    async def test_portal_guide_does_not_claim_nb_has_no_provincial_catalogue(self) -> None:
        """21-CONTEXT.md's 'NB has no provincial Socrata instance' claim is FALSE
        and must not be propagated — gnb.socrata.com is documented as live."""
        from mcp_canada.modules.new_brunswick.resources import nb_portal_guide
        result = await nb_portal_guide()
        assert "312 datasets" in result
        assert "option-a" in result

    # -----------------------------------------------------------------------
    # docs://nb/geonb-query-guide
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_geonb_query_guide_returns_str_with_heading(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_query_guide
        result = await nb_geonb_query_guide()
        assert isinstance(result, str)
        assert result.strip().startswith("#")

    @pytest.mark.asyncio
    async def test_geonb_query_guide_has_crown_land_worked_example(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_query_guide
        result = await nb_geonb_query_guide()
        assert "GeoNB_DNR_Crown_Land" in result

    @pytest.mark.asyncio
    async def test_geonb_query_guide_documents_filter_required_layers(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_geonb_query_guide
        result = await nb_geonb_query_guide()
        assert "nb_get_parcels" in result
        assert "nb_get_civic_addresses" in result
        assert "nb_get_wetlands" in result

    # -----------------------------------------------------------------------
    # template://nb/flood-risk-report
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_flood_risk_report_template_returns_str(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_flood_risk_report_template
        result = await nb_flood_risk_report_template()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_flood_risk_report_template_has_at_least_three_placeholders(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_flood_risk_report_template
        result = await nb_flood_risk_report_template()
        placeholders = set(re.findall(r"\{([a-z0-9_]+)\}", result))
        assert len(placeholders) >= 3

    @pytest.mark.asyncio
    async def test_flood_risk_report_template_covers_key_fields(self) -> None:
        from mcp_canada.modules.new_brunswick.resources import nb_flood_risk_report_template
        result = await nb_flood_risk_report_template()
        assert "{location}" in result
        assert "{hazard_classification}" in result
        assert "{data_retrieval_date}" in result

    # -----------------------------------------------------------------------
    # Total count: 7 resources + zero parameters + URI scheme
    # -----------------------------------------------------------------------

    def test_seven_resources_defined(self) -> None:
        from mcp_canada.modules.new_brunswick import resources as _m
        assert hasattr(_m, "__all__"), "resources.py must define __all__"
        assert len(_m.__all__) == 7, f"Expected 7 resources in __all__, found {len(_m.__all__)}"
        for name in _m.__all__:
            assert hasattr(_m, name), f"Resource {name} missing from module"
            assert callable(getattr(_m, name)), f"Resource {name} must be callable"

    def test_all_resources_have_zero_parameters(self) -> None:
        from mcp_canada.modules.new_brunswick import resources as _m
        for name in _m.__all__:
            fn = getattr(_m, name)
            target = inspect.unwrap(fn) if hasattr(fn, "__wrapped__") else fn
            sig = inspect.signature(target)
            assert len(sig.parameters) == 0, (name, list(sig.parameters))

    def test_no_mcp_decorator_used(self) -> None:
        import pathlib
        src = pathlib.Path(
            inspect.getfile(__import__("mcp_canada.modules.new_brunswick.resources", fromlist=["x"]))
        ).read_text()
        for line in src.splitlines():
            assert not line.strip().startswith("@mcp."), f"Found @mcp. decorator: {line}"

    def test_resource_uris_are_type_and_module_prefixed(self) -> None:
        """@resource returns the plain function (not a Resource instance, same
        lesson as @prompt — see nova_scotia/__tests__/test_prompts_resources.py),
        so the URI lives only in the decorator's source argument. Verify it
        directly from source rather than via inspect.getmembers/isinstance."""
        import pathlib
        src = pathlib.Path(
            inspect.getfile(__import__("mcp_canada.modules.new_brunswick.resources", fromlist=["x"]))
        ).read_text()
        uris = re.findall(r'@resource\(\s*\n?\s*"((?:data|docs|template)://nb/[a-z0-9-]+)"', src)
        assert len(uris) == 7, f"Expected 7 nb/-prefixed resource URIs, found {uris}"
