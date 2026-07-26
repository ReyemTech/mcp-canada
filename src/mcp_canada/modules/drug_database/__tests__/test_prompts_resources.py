# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Drug Database prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.drug_database.prompts import (
    drug_check_company,
    drug_check_status,
    drug_compare_generics,
    drug_quick_search,
    drug_research_medication,
)
from mcp_canada.modules.drug_database.resources import (
    drug_din_guide,
    drug_medication_report_template,
    drug_route_codes,
    drug_schedule_codes,
    drug_search_tips,
    drug_status_codes,
    drug_therapeutic_classes,
)


class TestDrugPrompts:
    """Tests for the 5 Drug Database @prompt functions."""

    # ------------------------------------------------------------------
    # drug_research_medication — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_research_medication_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(drug_research_medication)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_research_medication_en_roles(self):
        p = FunctionPrompt.from_function(drug_research_medication)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_research_medication_en_references_tools(self):
        p = FunctionPrompt.from_function(drug_research_medication)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "drug_search" in full_text
        assert "drug_get_details" in full_text
        assert "drug_get_ingredients" in full_text

    @pytest.mark.asyncio
    async def test_research_medication_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(drug_research_medication)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_research_medication_fr_is_french(self):
        p = FunctionPrompt.from_function(drug_research_medication)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("médicament", "marque", "générique", "Quel", "DIN")
        )

    # ------------------------------------------------------------------
    # drug_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(drug_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(drug_quick_search)
        result = await p.render({"lang": "en"})
        assert "drug_search" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(drug_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(drug_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(
            word in text
            for word in ("Utilisez", "médicament", "marque", "générique", "nom")
        )

    # ------------------------------------------------------------------
    # drug_check_company — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_company_en_returns_single_message(self):
        p = FunctionPrompt.from_function(drug_check_company)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_company_en_references_tool(self):
        p = FunctionPrompt.from_function(drug_check_company)
        result = await p.render({"lang": "en"})
        assert "drug_search_companies" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_company_fr_is_french(self):
        p = FunctionPrompt.from_function(drug_check_company)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("Utilisez", "entreprise", "fabricant", "compagnie"))

    # ------------------------------------------------------------------
    # drug_compare_generics — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_compare_generics_en_returns_messages(self):
        p = FunctionPrompt.from_function(drug_compare_generics)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_compare_generics_en_references_tools(self):
        p = FunctionPrompt.from_function(drug_compare_generics)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "drug_search" in full_text

    @pytest.mark.asyncio
    async def test_compare_generics_fr_is_french(self):
        p = FunctionPrompt.from_function(drug_compare_generics)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("générique", "comparer", "médicaments", "marques", "Quel")
        )

    # ------------------------------------------------------------------
    # drug_check_status — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_status_en_returns_single_message(self):
        p = FunctionPrompt.from_function(drug_check_status)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_status_en_references_tool(self):
        p = FunctionPrompt.from_function(drug_check_status)
        result = await p.render({"lang": "en"})
        assert "drug_get_status" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_status_fr_is_french(self):
        p = FunctionPrompt.from_function(drug_check_status)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("Utilisez", "statut", "DIN", "marché"))


class TestDrugResources:
    """Tests for the 7 Drug Database @resource functions."""

    # ------------------------------------------------------------------
    # data://drug/schedule-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_schedule_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            drug_schedule_codes, uri="data://drug/schedule-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_schedule_codes_has_rx_and_otc(self):
        r = FunctionResource.from_function(
            drug_schedule_codes, uri="data://drug/schedule-codes"
        )
        content = await r.read()
        data = json.loads(content)
        content_lower = json.dumps(data).lower()
        assert "prescription" in content_lower or "rx" in content_lower

    @pytest.mark.asyncio
    async def test_schedule_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            drug_schedule_codes, uri="data://drug/schedule-codes"
        )
        content = await r.read()
        data = json.loads(content)
        first_key = list(data.keys())[0]
        assert "en" in data[first_key]
        assert "fr" in data[first_key]

    # ------------------------------------------------------------------
    # data://drug/route-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_route_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            drug_route_codes, uri="data://drug/route-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_route_codes_has_oral_and_topical(self):
        r = FunctionResource.from_function(
            drug_route_codes, uri="data://drug/route-codes"
        )
        content = await r.read()
        data = json.loads(content)
        content_lower = json.dumps(data).lower()
        assert "oral" in content_lower or "topical" in content_lower

    # ------------------------------------------------------------------
    # data://drug/status-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_status_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            drug_status_codes, uri="data://drug/status-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_status_codes_has_entries(self):
        r = FunctionResource.from_function(
            drug_status_codes, uri="data://drug/status-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 3

    # ------------------------------------------------------------------
    # data://drug/therapeutic-classes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_therapeutic_classes_is_valid_json(self):
        r = FunctionResource.from_function(
            drug_therapeutic_classes, uri="data://drug/therapeutic-classes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_therapeutic_classes_has_atc_codes(self):
        r = FunctionResource.from_function(
            drug_therapeutic_classes, uri="data://drug/therapeutic-classes"
        )
        content = await r.read()
        data = json.loads(content)
        # ATC codes are single letters or alphanumeric
        assert len(data) >= 5

    # ------------------------------------------------------------------
    # docs://drug/din-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_din_guide_is_markdown(self):
        r = FunctionResource.from_function(
            drug_din_guide, uri="docs://drug/din-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "DIN guide must start with # heading"

    @pytest.mark.asyncio
    async def test_din_guide_mentions_din(self):
        r = FunctionResource.from_function(
            drug_din_guide, uri="docs://drug/din-guide"
        )
        content = await r.read()
        assert "DIN" in content

    # ------------------------------------------------------------------
    # docs://drug/search-tips
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_tips_is_markdown(self):
        r = FunctionResource.from_function(
            drug_search_tips, uri="docs://drug/search-tips"
        )
        content = await r.read()
        assert content.startswith("#"), "Search tips must start with # heading"

    @pytest.mark.asyncio
    async def test_search_tips_mentions_brand_and_generic(self):
        r = FunctionResource.from_function(
            drug_search_tips, uri="docs://drug/search-tips"
        )
        content = await r.read()
        assert "brand" in content.lower() or "generic" in content.lower()

    # ------------------------------------------------------------------
    # template://drug/medication-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_medication_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            drug_medication_report_template, uri="template://drug/medication-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Medication report template must start with # heading"

    @pytest.mark.asyncio
    async def test_medication_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            drug_medication_report_template, uri="template://drug/medication-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    # ------------------------------------------------------------------
    # Zero-param sanity
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            drug_schedule_codes,
            drug_route_codes,
            drug_status_codes,
            drug_therapeutic_classes,
            drug_din_guide,
            drug_search_tips,
            drug_medication_report_template,
        ]
        for fn in resources:
            sig = inspect.signature(fn)
            params = [
                name
                for name, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty
            ]
            assert params == [], (
                f"{fn.__name__} has required parameters {params}; "
                "resources must be zero-param functions"
            )
