# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Recalls prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.recalls.prompts import (
    recalls_check_food_safety,
    recalls_investigate_alert,
    recalls_quick_search,
    recalls_vehicle_safety,
)
from mcp_canada.modules.recalls.resources import (
    recalls_categories,
    recalls_food_safety_guide,
    recalls_recall_report_template,
    recalls_safety_alert_template,
    recalls_search_tips,
    recalls_severity_levels,
)


class TestRecallsPrompts:
    """Tests for the 4 Recalls @prompt functions."""

    # ------------------------------------------------------------------
    # recalls_investigate_alert — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_investigate_alert_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(recalls_investigate_alert)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_investigate_alert_en_roles(self):
        p = FunctionPrompt.from_function(recalls_investigate_alert)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_investigate_alert_en_references_tools(self):
        p = FunctionPrompt.from_function(recalls_investigate_alert)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "recalls_search" in full_text
        assert "recalls_get_details" in full_text

    @pytest.mark.asyncio
    async def test_investigate_alert_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(recalls_investigate_alert)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_investigate_alert_fr_is_french(self):
        p = FunctionPrompt.from_function(recalls_investigate_alert)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("rappel", "alerte", "sécurité", "Quel", "rechercher")
        )

    # ------------------------------------------------------------------
    # recalls_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(recalls_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(recalls_quick_search)
        result = await p.render({"lang": "en"})
        assert "recalls_search" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(recalls_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(recalls_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("Utilisez", "rappel", "recherche", "mot-clé"))

    # ------------------------------------------------------------------
    # recalls_check_food_safety — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_food_safety_en_returns_single_message(self):
        p = FunctionPrompt.from_function(recalls_check_food_safety)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_food_safety_en_references_tool(self):
        p = FunctionPrompt.from_function(recalls_check_food_safety)
        result = await p.render({"lang": "en"})
        assert "recalls_get_food" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_food_safety_fr_is_french(self):
        p = FunctionPrompt.from_function(recalls_check_food_safety)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("Utilisez", "aliments", "nourriture", "alimentaire"))

    # ------------------------------------------------------------------
    # recalls_vehicle_safety — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_vehicle_safety_en_returns_messages(self):
        p = FunctionPrompt.from_function(recalls_vehicle_safety)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_vehicle_safety_en_references_tool(self):
        p = FunctionPrompt.from_function(recalls_vehicle_safety)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "recalls_get_vehicles" in full_text

    @pytest.mark.asyncio
    async def test_vehicle_safety_fr_is_french(self):
        p = FunctionPrompt.from_function(recalls_vehicle_safety)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("véhicule", "automobile", "rappel", "Quel")
        )


class TestRecallsResources:
    """Tests for the 6 Recalls @resource functions."""

    # ------------------------------------------------------------------
    # data://recalls/categories
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_categories_is_valid_json(self):
        r = FunctionResource.from_function(
            recalls_categories, uri="data://recalls/categories"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_categories_has_food_vehicle_health(self):
        r = FunctionResource.from_function(
            recalls_categories, uri="data://recalls/categories"
        )
        content = await r.read()
        data = json.loads(content)
        content_lower = json.dumps(data).lower()
        assert "food" in content_lower or "aliment" in content_lower
        assert "vehicle" in content_lower or "véhicule" in content_lower

    @pytest.mark.asyncio
    async def test_categories_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            recalls_categories, uri="data://recalls/categories"
        )
        content = await r.read()
        data = json.loads(content)
        first_key = list(data.keys())[0]
        assert "en" in data[first_key]
        assert "fr" in data[first_key]

    # ------------------------------------------------------------------
    # data://recalls/severity-levels
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_severity_levels_is_valid_json(self):
        r = FunctionResource.from_function(
            recalls_severity_levels, uri="data://recalls/severity-levels"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_severity_levels_has_entries(self):
        r = FunctionResource.from_function(
            recalls_severity_levels, uri="data://recalls/severity-levels"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 2

    # ------------------------------------------------------------------
    # docs://recalls/search-tips
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_tips_is_markdown(self):
        r = FunctionResource.from_function(
            recalls_search_tips, uri="docs://recalls/search-tips"
        )
        content = await r.read()
        assert content.startswith("#"), "Search tips must start with # heading"

    @pytest.mark.asyncio
    async def test_search_tips_mentions_search(self):
        r = FunctionResource.from_function(
            recalls_search_tips, uri="docs://recalls/search-tips"
        )
        content = await r.read()
        assert "search" in content.lower() or "recall" in content.lower()

    # ------------------------------------------------------------------
    # docs://recalls/food-safety-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_food_safety_guide_is_markdown(self):
        r = FunctionResource.from_function(
            recalls_food_safety_guide, uri="docs://recalls/food-safety-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Food safety guide must start with # heading"

    @pytest.mark.asyncio
    async def test_food_safety_guide_mentions_food(self):
        r = FunctionResource.from_function(
            recalls_food_safety_guide, uri="docs://recalls/food-safety-guide"
        )
        content = await r.read()
        assert "food" in content.lower() or "allergen" in content.lower()

    # ------------------------------------------------------------------
    # template://recalls/safety-alert
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_safety_alert_template_is_markdown(self):
        r = FunctionResource.from_function(
            recalls_safety_alert_template, uri="template://recalls/safety-alert"
        )
        content = await r.read()
        assert content.startswith("#"), "Safety alert template must start with # heading"

    @pytest.mark.asyncio
    async def test_safety_alert_template_has_placeholders(self):
        r = FunctionResource.from_function(
            recalls_safety_alert_template, uri="template://recalls/safety-alert"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    # ------------------------------------------------------------------
    # template://recalls/recall-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_recall_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            recalls_recall_report_template, uri="template://recalls/recall-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Recall report template must start with # heading"

    @pytest.mark.asyncio
    async def test_recall_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            recalls_recall_report_template, uri="template://recalls/recall-report"
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
            recalls_categories,
            recalls_severity_levels,
            recalls_search_tips,
            recalls_food_safety_guide,
            recalls_safety_alert_template,
            recalls_recall_report_template,
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
