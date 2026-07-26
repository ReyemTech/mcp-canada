# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Nutrient File prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.nutrient_file.prompts import (
    nutrient_analyze_food,
    nutrient_browse_food_groups,
    nutrient_check_daily_values,
    nutrient_compare_foods,
    nutrient_quick_search,
)
from mcp_canada.modules.nutrient_file.resources import (
    nutrient_cnf_guide,
    nutrient_common_nutrients,
    nutrient_comparison_report_template,
    nutrient_food_groups,
    nutrient_food_profile_template,
    nutrient_interpretation_guide,
    nutrient_serving_size_measures,
)


class TestNutrientPrompts:
    """Tests for the 5 Nutrient File @prompt functions."""

    # ------------------------------------------------------------------
    # nutrient_analyze_food — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_analyze_food_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(nutrient_analyze_food)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_analyze_food_en_roles(self):
        p = FunctionPrompt.from_function(nutrient_analyze_food)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_analyze_food_en_references_tools(self):
        p = FunctionPrompt.from_function(nutrient_analyze_food)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "nutrient_search_foods" in full_text
        assert "nutrient_get_nutrient_amounts" in full_text

    @pytest.mark.asyncio
    async def test_analyze_food_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(nutrient_analyze_food)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_analyze_food_fr_is_french(self):
        p = FunctionPrompt.from_function(nutrient_analyze_food)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("aliment", "nourriture", "nutritionnel", "analyser", "Quel")
        )

    # ------------------------------------------------------------------
    # nutrient_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(nutrient_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(nutrient_quick_search)
        result = await p.render({"lang": "en"})
        assert "nutrient_search_foods" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(nutrient_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(nutrient_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("Utilisez", "aliment", "chercher", "nom"))

    # ------------------------------------------------------------------
    # nutrient_compare_foods — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_compare_foods_en_returns_messages(self):
        p = FunctionPrompt.from_function(nutrient_compare_foods)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_compare_foods_en_references_tools(self):
        p = FunctionPrompt.from_function(nutrient_compare_foods)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "nutrient_search_foods" in full_text or "nutrient_compare_foods" in full_text

    @pytest.mark.asyncio
    async def test_compare_foods_fr_is_french(self):
        p = FunctionPrompt.from_function(nutrient_compare_foods)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("comparer", "aliments", "nourriture", "Quels", "nutriments")
        )

    # ------------------------------------------------------------------
    # nutrient_browse_food_groups — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_browse_food_groups_en_returns_single_message(self):
        p = FunctionPrompt.from_function(nutrient_browse_food_groups)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_browse_food_groups_en_references_tool(self):
        p = FunctionPrompt.from_function(nutrient_browse_food_groups)
        result = await p.render({"lang": "en"})
        text = result.messages[0].content.text
        assert "nutrient_list_food_groups" in text or "nutrient_search_by_food_group" in text

    @pytest.mark.asyncio
    async def test_browse_food_groups_fr_is_french(self):
        p = FunctionPrompt.from_function(nutrient_browse_food_groups)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(
            word in text
            for word in ("Utilisez", "groupe", "aliments", "catégorie", "parcourir")
        )

    # ------------------------------------------------------------------
    # nutrient_check_daily_values — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_daily_values_en_returns_messages(self):
        p = FunctionPrompt.from_function(nutrient_check_daily_values)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_check_daily_values_en_references_tool(self):
        p = FunctionPrompt.from_function(nutrient_check_daily_values)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "nutrient_get_nutrient_amounts" in full_text

    @pytest.mark.asyncio
    async def test_check_daily_values_fr_is_french(self):
        p = FunctionPrompt.from_function(nutrient_check_daily_values)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("quotidien", "apport", "valeur", "nutriment", "Quel")
        )


class TestNutrientResources:
    """Tests for the 7 Nutrient File @resource functions."""

    # ------------------------------------------------------------------
    # data://nutrient/food-groups
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_food_groups_is_valid_json(self):
        r = FunctionResource.from_function(
            nutrient_food_groups, uri="data://nutrient/food-groups"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_food_groups_has_dairy_and_meat(self):
        r = FunctionResource.from_function(
            nutrient_food_groups, uri="data://nutrient/food-groups"
        )
        content = await r.read()
        data = json.loads(content)
        content_lower = json.dumps(data).lower()
        assert "dairy" in content_lower or "milk" in content_lower or "meat" in content_lower

    @pytest.mark.asyncio
    async def test_food_groups_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            nutrient_food_groups, uri="data://nutrient/food-groups"
        )
        content = await r.read()
        data = json.loads(content)
        first_key = list(data.keys())[0]
        assert "en" in data[first_key]
        assert "fr" in data[first_key]

    # ------------------------------------------------------------------
    # data://nutrient/common-nutrients
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_common_nutrients_is_valid_json(self):
        r = FunctionResource.from_function(
            nutrient_common_nutrients, uri="data://nutrient/common-nutrients"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_common_nutrients_has_protein_and_fat(self):
        r = FunctionResource.from_function(
            nutrient_common_nutrients, uri="data://nutrient/common-nutrients"
        )
        content = await r.read()
        data = json.loads(content)
        content_lower = json.dumps(data).lower()
        assert "protein" in content_lower or "fat" in content_lower

    @pytest.mark.asyncio
    async def test_common_nutrients_has_units(self):
        r = FunctionResource.from_function(
            nutrient_common_nutrients, uri="data://nutrient/common-nutrients"
        )
        content = await r.read()
        data = json.loads(content)
        # Each entry should have a unit
        first_key = list(data.keys())[0]
        assert "unit" in data[first_key]

    # ------------------------------------------------------------------
    # data://nutrient/serving-size-measures
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_serving_size_measures_is_valid_json(self):
        r = FunctionResource.from_function(
            nutrient_serving_size_measures, uri="data://nutrient/serving-size-measures"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_serving_size_measures_has_entries(self):
        r = FunctionResource.from_function(
            nutrient_serving_size_measures, uri="data://nutrient/serving-size-measures"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 5

    # ------------------------------------------------------------------
    # docs://nutrient/cnf-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_cnf_guide_is_markdown(self):
        r = FunctionResource.from_function(
            nutrient_cnf_guide, uri="docs://nutrient/cnf-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "CNF guide must start with # heading"

    @pytest.mark.asyncio
    async def test_cnf_guide_mentions_cnf(self):
        r = FunctionResource.from_function(
            nutrient_cnf_guide, uri="docs://nutrient/cnf-guide"
        )
        content = await r.read()
        assert "CNF" in content or "Canadian Nutrient File" in content

    # ------------------------------------------------------------------
    # docs://nutrient/interpretation-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_interpretation_guide_is_markdown(self):
        r = FunctionResource.from_function(
            nutrient_interpretation_guide, uri="docs://nutrient/interpretation-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Interpretation guide must start with # heading"

    @pytest.mark.asyncio
    async def test_interpretation_guide_mentions_daily_intake(self):
        r = FunctionResource.from_function(
            nutrient_interpretation_guide, uri="docs://nutrient/interpretation-guide"
        )
        content = await r.read()
        assert "daily" in content.lower() or "intake" in content.lower()

    # ------------------------------------------------------------------
    # template://nutrient/food-profile
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_food_profile_template_is_markdown(self):
        r = FunctionResource.from_function(
            nutrient_food_profile_template, uri="template://nutrient/food-profile"
        )
        content = await r.read()
        assert content.startswith("#"), "Food profile template must start with # heading"

    @pytest.mark.asyncio
    async def test_food_profile_template_has_placeholders(self):
        r = FunctionResource.from_function(
            nutrient_food_profile_template, uri="template://nutrient/food-profile"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    # ------------------------------------------------------------------
    # template://nutrient/comparison-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_comparison_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            nutrient_comparison_report_template, uri="template://nutrient/comparison-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Comparison report template must start with # heading"

    @pytest.mark.asyncio
    async def test_comparison_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            nutrient_comparison_report_template, uri="template://nutrient/comparison-report"
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
            nutrient_food_groups,
            nutrient_common_nutrients,
            nutrient_serving_size_measures,
            nutrient_cnf_guide,
            nutrient_interpretation_guide,
            nutrient_food_profile_template,
            nutrient_comparison_report_template,
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
