"""Unit tests for CKAN prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.ckan.prompts import (
    ckan_browse_by_tag,
    ckan_browse_organizations,
    ckan_explore_federal_data,
    ckan_portal_overview,
    ckan_quick_search,
)
from mcp_canada.modules.ckan.resources import (
    ckan_api_quirks_guide,
    ckan_dataset_summary_template,
    ckan_federal_organizations,
    ckan_popular_tags,
    ckan_resource_formats,
    ckan_resource_report_template,
    ckan_search_tips_guide,
)


class TestCKANPrompts:
    """Tests for the 5 CKAN @prompt functions."""

    # ------------------------------------------------------------------
    # ckan_explore_federal_data — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_federal_data_en_returns_messages(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_explore_federal_data_en_roles(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_federal_data_en_references_search_tool(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ckan_search_datasets" in full_text

    @pytest.mark.asyncio
    async def test_explore_federal_data_en_references_details_tool(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ckan_get_dataset_details" in full_text

    @pytest.mark.asyncio
    async def test_explore_federal_data_fr_returns_messages(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_explore_federal_data_fr_is_french(self):
        p = FunctionPrompt.from_function(ckan_explore_federal_data)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("données", "gouvernement", "fédéral", "jeux", "rechercher")
        )

    # ------------------------------------------------------------------
    # ckan_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ckan_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(ckan_quick_search)
        result = await p.render({"lang": "en"})
        assert "ckan_search_datasets" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(ckan_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(ckan_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ckan_search_datasets" in text
        assert any(word in text for word in ("requête", "Utilisez", "recherche", "jeux"))

    # ------------------------------------------------------------------
    # ckan_browse_organizations — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_browse_organizations_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ckan_browse_organizations)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_browse_organizations_en_references_tool(self):
        p = FunctionPrompt.from_function(ckan_browse_organizations)
        result = await p.render({"lang": "en"})
        assert "ckan_list_organizations" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_browse_organizations_fr_is_french(self):
        p = FunctionPrompt.from_function(ckan_browse_organizations)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("organisations", "ministères", "Utilisez", "liste"))

    # ------------------------------------------------------------------
    # ckan_browse_by_tag — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_browse_by_tag_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ckan_browse_by_tag)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_browse_by_tag_en_references_tool(self):
        p = FunctionPrompt.from_function(ckan_browse_by_tag)
        result = await p.render({"lang": "en"})
        assert "ckan_search_by_tag" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_browse_by_tag_fr_is_french(self):
        p = FunctionPrompt.from_function(ckan_browse_by_tag)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("étiquette", "tag", "Utilisez", "balise"))

    # ------------------------------------------------------------------
    # ckan_portal_overview — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_portal_overview_en_returns_messages(self):
        p = FunctionPrompt.from_function(ckan_portal_overview)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_portal_overview_en_references_stats_tool(self):
        p = FunctionPrompt.from_function(ckan_portal_overview)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ckan_get_dataset_stats" in full_text

    @pytest.mark.asyncio
    async def test_portal_overview_en_references_groups_tool(self):
        p = FunctionPrompt.from_function(ckan_portal_overview)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ckan_list_groups" in full_text

    @pytest.mark.asyncio
    async def test_portal_overview_fr_is_french(self):
        p = FunctionPrompt.from_function(ckan_portal_overview)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("portail", "aperçu", "données", "groupes", "statistiques")
        )


class TestCKANResources:
    """Tests for the 7 CKAN @resource functions."""

    # ------------------------------------------------------------------
    # data://ckan/federal-organizations
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_federal_organizations_is_valid_json(self):
        r = FunctionResource.from_function(
            ckan_federal_organizations, uri="data://ckan/federal-organizations"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_federal_organizations_has_bilingual_names(self):
        r = FunctionResource.from_function(
            ckan_federal_organizations, uri="data://ckan/federal-organizations"
        )
        content = await r.read()
        data = json.loads(content)
        first_val = next(iter(data.values()))
        assert "en" in first_val
        assert "fr" in first_val

    @pytest.mark.asyncio
    async def test_federal_organizations_has_multiple_entries(self):
        r = FunctionResource.from_function(
            ckan_federal_organizations, uri="data://ckan/federal-organizations"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 5

    # ------------------------------------------------------------------
    # data://ckan/popular-tags
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_popular_tags_is_valid_json(self):
        r = FunctionResource.from_function(
            ckan_popular_tags, uri="data://ckan/popular-tags"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_popular_tags_has_entries(self):
        r = FunctionResource.from_function(
            ckan_popular_tags, uri="data://ckan/popular-tags"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 3

    # ------------------------------------------------------------------
    # data://ckan/resource-formats
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resource_formats_is_valid_json(self):
        r = FunctionResource.from_function(
            ckan_resource_formats, uri="data://ckan/resource-formats"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_resource_formats_has_csv_and_json(self):
        r = FunctionResource.from_function(
            ckan_resource_formats, uri="data://ckan/resource-formats"
        )
        content = await r.read()
        data = json.loads(content)
        assert "CSV" in data or "csv" in data
        assert "JSON" in data or "json" in data

    # ------------------------------------------------------------------
    # docs://ckan/search-tips
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_tips_is_markdown(self):
        r = FunctionResource.from_function(
            ckan_search_tips_guide, uri="docs://ckan/search-tips"
        )
        content = await r.read()
        assert content.startswith("#"), "Search tips guide must start with # heading"

    @pytest.mark.asyncio
    async def test_search_tips_mentions_query(self):
        r = FunctionResource.from_function(
            ckan_search_tips_guide, uri="docs://ckan/search-tips"
        )
        content = await r.read()
        assert "query" in content.lower() or "search" in content.lower()

    # ------------------------------------------------------------------
    # docs://ckan/api-quirks
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_api_quirks_is_markdown(self):
        r = FunctionResource.from_function(
            ckan_api_quirks_guide, uri="docs://ckan/api-quirks"
        )
        content = await r.read()
        assert content.startswith("#"), "API quirks guide must start with # heading"

    @pytest.mark.asyncio
    async def test_api_quirks_mentions_pagination(self):
        r = FunctionResource.from_function(
            ckan_api_quirks_guide, uri="docs://ckan/api-quirks"
        )
        content = await r.read()
        assert "pagination" in content.lower() or "rows" in content.lower()

    # ------------------------------------------------------------------
    # template://ckan/dataset-summary
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_dataset_summary_template_is_markdown(self):
        r = FunctionResource.from_function(
            ckan_dataset_summary_template, uri="template://ckan/dataset-summary"
        )
        content = await r.read()
        assert content.startswith("#"), "Dataset summary template must start with # heading"

    @pytest.mark.asyncio
    async def test_dataset_summary_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ckan_dataset_summary_template, uri="template://ckan/dataset-summary"
        )
        content = await r.read()
        assert "{" in content and "}" in content

    # ------------------------------------------------------------------
    # template://ckan/resource-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resource_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            ckan_resource_report_template, uri="template://ckan/resource-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Resource report template must start with # heading"

    @pytest.mark.asyncio
    async def test_resource_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ckan_resource_report_template, uri="template://ckan/resource-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content

    # ------------------------------------------------------------------
    # Zero-param sanity
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            ckan_federal_organizations,
            ckan_popular_tags,
            ckan_resource_formats,
            ckan_search_tips_guide,
            ckan_api_quirks_guide,
            ckan_dataset_summary_template,
            ckan_resource_report_template,
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
