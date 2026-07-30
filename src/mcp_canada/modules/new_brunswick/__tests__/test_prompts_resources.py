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
import re

import pytest


def test_prompts_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import prompts  # noqa: F401


def test_resources_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import resources  # noqa: F401


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
    """Task 2 fills this — data://nb/geonb-services, data://nb/counties,
    data://nb/health-regions, data://nb/school-districts,
    docs://nb/portal-guide, docs://nb/geonb-query-guide,
    template://nb/flood-risk-report."""
