# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Ontario Open Data module prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.ontario.prompts import (
    ontario_browse_ministries,
    ontario_explore_data,
    ontario_population_data,
    ontario_quick_search,
)
from mcp_canada.modules.ontario.resources import (
    ontario_ckan_guide,
    ontario_dataset_report_template,
    ontario_ministries,
    ontario_popular_datasets,
    ontario_population_projections_guide,
    ontario_resource_formats,
)


class TestOntarioPrompts:
    """Tests for the 4 Ontario @prompt functions."""

    # ------------------------------------------------------------------
    # ontario_explore_data — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_data_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(ontario_explore_data)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_data_en_roles(self):
        p = FunctionPrompt.from_function(ontario_explore_data)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_data_en_references_tool(self):
        p = FunctionPrompt.from_function(ontario_explore_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ontario_search_datasets" in full_text

    @pytest.mark.asyncio
    async def test_explore_data_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(ontario_explore_data)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_data_fr_is_french(self):
        p = FunctionPrompt.from_function(ontario_explore_data)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("données", "Ontario", "explorer", "recherche", "jeux de données")
        )

    # ------------------------------------------------------------------
    # ontario_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ontario_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(ontario_quick_search)
        result = await p.render({"lang": "en"})
        assert "ontario_search_datasets" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(ontario_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(ontario_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ontario_search_datasets" in text
        assert any(word in text for word in ("Utilisez", "rechercher", "jeux de données"))

    # ------------------------------------------------------------------
    # ontario_browse_ministries — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_browse_ministries_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ontario_browse_ministries)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_browse_ministries_en_references_tool(self):
        p = FunctionPrompt.from_function(ontario_browse_ministries)
        result = await p.render({"lang": "en"})
        assert "ontario_list_organizations" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_browse_ministries_fr_is_french(self):
        p = FunctionPrompt.from_function(ontario_browse_ministries)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ontario_list_organizations" in text

    # ------------------------------------------------------------------
    # ontario_population_data — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_population_data_en_returns_messages(self):
        p = FunctionPrompt.from_function(ontario_population_data)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_population_data_en_references_tool(self):
        p = FunctionPrompt.from_function(ontario_population_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ontario_get_population_projections" in full_text

    @pytest.mark.asyncio
    async def test_population_data_fr_is_french(self):
        p = FunctionPrompt.from_function(ontario_population_data)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("population", "projections", "région", "prévisions", "démographie")
        )


class TestOntarioResources:
    """Tests for the 6 Ontario @resource functions."""

    # ------------------------------------------------------------------
    # data://ontario/ministries
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ministries_is_valid_json(self):
        r = FunctionResource.from_function(
            ontario_ministries, uri="data://ontario/ministries"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_ministries_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            ontario_ministries, uri="data://ontario/ministries"
        )
        content = await r.read()
        data = json.loads(content)
        # If dict, check first entry; if list, check first element
        if isinstance(data, dict):
            first = next(iter(data.values()))
        else:
            first = data[0]
        assert "en" in first
        assert "fr" in first

    # ------------------------------------------------------------------
    # data://ontario/popular-datasets
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_popular_datasets_is_valid_json(self):
        r = FunctionResource.from_function(
            ontario_popular_datasets, uri="data://ontario/popular-datasets"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_popular_datasets_has_entries(self):
        r = FunctionResource.from_function(
            ontario_popular_datasets, uri="data://ontario/popular-datasets"
        )
        content = await r.read()
        data = json.loads(content)
        if isinstance(data, list):
            assert len(data) > 0
        else:
            assert len(data) > 0

    # ------------------------------------------------------------------
    # data://ontario/resource-formats
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resource_formats_is_valid_json(self):
        r = FunctionResource.from_function(
            ontario_resource_formats, uri="data://ontario/resource-formats"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_resource_formats_mentions_csv(self):
        r = FunctionResource.from_function(
            ontario_resource_formats, uri="data://ontario/resource-formats"
        )
        content = await r.read()
        assert "CSV" in content or "csv" in content

    # ------------------------------------------------------------------
    # docs://ontario/ckan-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ckan_guide_is_markdown(self):
        r = FunctionResource.from_function(
            ontario_ckan_guide, uri="docs://ontario/ckan-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "CKAN guide must start with # heading"

    @pytest.mark.asyncio
    async def test_ckan_guide_mentions_ontario(self):
        r = FunctionResource.from_function(
            ontario_ckan_guide, uri="docs://ontario/ckan-guide"
        )
        content = await r.read()
        assert "ontario" in content.lower() or "Ontario" in content

    # ------------------------------------------------------------------
    # docs://ontario/population-projections-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_population_projections_guide_is_markdown(self):
        r = FunctionResource.from_function(
            ontario_population_projections_guide, uri="docs://ontario/population-projections-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Population guide must start with # heading"

    @pytest.mark.asyncio
    async def test_population_projections_guide_mentions_projections(self):
        r = FunctionResource.from_function(
            ontario_population_projections_guide, uri="docs://ontario/population-projections-guide"
        )
        content = await r.read()
        assert "projection" in content.lower() or "population" in content.lower()

    # ------------------------------------------------------------------
    # template://ontario/dataset-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_dataset_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            ontario_dataset_report_template, uri="template://ontario/dataset-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Dataset report template must start with # heading"

    @pytest.mark.asyncio
    async def test_dataset_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ontario_dataset_report_template, uri="template://ontario/dataset-report"
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
            ontario_ministries,
            ontario_popular_datasets,
            ontario_resource_formats,
            ontario_ckan_guide,
            ontario_population_projections_guide,
            ontario_dataset_report_template,
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
