"""Unit tests for IRCC Immigration module prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.ircc.prompts import (
    ircc_analyze_trends,
    ircc_compare_pathways,
    ircc_explore_immigration,
    ircc_quick_pr,
    ircc_track_express_entry,
)
from mcp_canada.modules.ircc.resources import (
    ircc_data_guide,
    ircc_dataset_list,
    ircc_express_entry_streams,
    ircc_immigration_categories,
    ircc_immigration_report_template,
    ircc_work_permit_types,
    ircc_xlsx_quirks_guide,
)


class TestIrccPrompts:
    """Tests for the 5 IRCC @prompt functions."""

    # ------------------------------------------------------------------
    # ircc_explore_immigration — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_immigration_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(ircc_explore_immigration)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_immigration_en_roles(self):
        p = FunctionPrompt.from_function(ircc_explore_immigration)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_immigration_en_references_tool(self):
        p = FunctionPrompt.from_function(ircc_explore_immigration)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ircc_list_datasets" in full_text or "ircc_get_permanent_residents" in full_text

    @pytest.mark.asyncio
    async def test_explore_immigration_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(ircc_explore_immigration)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_immigration_fr_is_french(self):
        p = FunctionPrompt.from_function(ircc_explore_immigration)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("immigration", "données", "résidents permanents", "explorer")
        )

    # ------------------------------------------------------------------
    # ircc_quick_pr — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_pr_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ircc_quick_pr)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_pr_en_references_tool(self):
        p = FunctionPrompt.from_function(ircc_quick_pr)
        result = await p.render({"lang": "en"})
        assert "ircc_get_permanent_residents" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_pr_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(ircc_quick_pr)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_pr_fr_is_french(self):
        p = FunctionPrompt.from_function(ircc_quick_pr)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ircc_get_permanent_residents" in text
        assert any(word in text for word in ("Utilisez", "résidents", "pays", "province"))

    # ------------------------------------------------------------------
    # ircc_track_express_entry — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_track_express_entry_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ircc_track_express_entry)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_track_express_entry_en_references_tool(self):
        p = FunctionPrompt.from_function(ircc_track_express_entry)
        result = await p.render({"lang": "en"})
        assert "ircc_get_express_entry" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_track_express_entry_fr_is_french(self):
        p = FunctionPrompt.from_function(ircc_track_express_entry)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ircc_get_express_entry" in text

    # ------------------------------------------------------------------
    # ircc_compare_pathways — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_compare_pathways_en_returns_messages(self):
        p = FunctionPrompt.from_function(ircc_compare_pathways)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_compare_pathways_en_references_tools(self):
        p = FunctionPrompt.from_function(ircc_compare_pathways)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ircc_get_permanent_residents" in full_text or "ircc_get_study_permits" in full_text

    @pytest.mark.asyncio
    async def test_compare_pathways_fr_is_french(self):
        p = FunctionPrompt.from_function(ircc_compare_pathways)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("voies", "comparer", "immigration", "résidents", "permis")
        )

    # ------------------------------------------------------------------
    # ircc_analyze_trends — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_analyze_trends_en_returns_messages(self):
        p = FunctionPrompt.from_function(ircc_analyze_trends)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_analyze_trends_en_references_tool(self):
        p = FunctionPrompt.from_function(ircc_analyze_trends)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ircc_get_permanent_residents" in full_text

    @pytest.mark.asyncio
    async def test_analyze_trends_fr_is_french(self):
        p = FunctionPrompt.from_function(ircc_analyze_trends)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("tendances", "années", "analyse", "immigration", "données")
        )


class TestIrccResources:
    """Tests for the 7 IRCC @resource functions."""

    # ------------------------------------------------------------------
    # data://ircc/immigration-categories
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_immigration_categories_is_valid_json(self):
        r = FunctionResource.from_function(
            ircc_immigration_categories, uri="data://ircc/immigration-categories"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_immigration_categories_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            ircc_immigration_categories, uri="data://ircc/immigration-categories"
        )
        content = await r.read()
        data = json.loads(content)
        first_key = next(iter(data))
        entry = data[first_key]
        assert "en" in entry
        assert "fr" in entry

    # ------------------------------------------------------------------
    # data://ircc/dataset-list
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_dataset_list_is_valid_json(self):
        r = FunctionResource.from_function(
            ircc_dataset_list, uri="data://ircc/dataset-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_dataset_list_has_pr_entry(self):
        r = FunctionResource.from_function(
            ircc_dataset_list, uri="data://ircc/dataset-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert "pr" in data or "permanent_residents" in data

    # ------------------------------------------------------------------
    # data://ircc/express-entry-streams
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_express_entry_streams_is_valid_json(self):
        r = FunctionResource.from_function(
            ircc_express_entry_streams, uri="data://ircc/express-entry-streams"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_express_entry_streams_has_fsw(self):
        r = FunctionResource.from_function(
            ircc_express_entry_streams, uri="data://ircc/express-entry-streams"
        )
        content = await r.read()
        data = json.loads(content)
        content_str = json.dumps(data)
        assert "FSW" in content_str or "Federal Skilled Worker" in content_str

    # ------------------------------------------------------------------
    # data://ircc/work-permit-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_work_permit_types_is_valid_json(self):
        r = FunctionResource.from_function(
            ircc_work_permit_types, uri="data://ircc/work-permit-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_work_permit_types_has_imp_and_tfwp(self):
        r = FunctionResource.from_function(
            ircc_work_permit_types, uri="data://ircc/work-permit-types"
        )
        content = await r.read()
        data = json.loads(content)
        content_str = json.dumps(data)
        assert "IMP" in content_str or "TFWP" in content_str

    # ------------------------------------------------------------------
    # docs://ircc/data-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_data_guide_is_markdown(self):
        r = FunctionResource.from_function(
            ircc_data_guide, uri="docs://ircc/data-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "IRCC data guide must start with # heading"

    @pytest.mark.asyncio
    async def test_data_guide_mentions_privacy_masking(self):
        r = FunctionResource.from_function(
            ircc_data_guide, uri="docs://ircc/data-guide"
        )
        content = await r.read()
        assert "--" in content or "privacy" in content.lower() or "masked" in content.lower()

    # ------------------------------------------------------------------
    # docs://ircc/xlsx-quirks
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_xlsx_quirks_is_markdown(self):
        r = FunctionResource.from_function(
            ircc_xlsx_quirks_guide, uri="docs://ircc/xlsx-quirks"
        )
        content = await r.read()
        assert content.startswith("#"), "XLSX quirks guide must start with # heading"

    @pytest.mark.asyncio
    async def test_xlsx_quirks_mentions_sheets(self):
        r = FunctionResource.from_function(
            ircc_xlsx_quirks_guide, uri="docs://ircc/xlsx-quirks"
        )
        content = await r.read()
        assert "sheet" in content.lower() or "header" in content.lower()

    # ------------------------------------------------------------------
    # template://ircc/immigration-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_immigration_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            ircc_immigration_report_template, uri="template://ircc/immigration-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Immigration report template must start with # heading"

    @pytest.mark.asyncio
    async def test_immigration_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ircc_immigration_report_template, uri="template://ircc/immigration-report"
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
            ircc_immigration_categories,
            ircc_dataset_list,
            ircc_express_entry_streams,
            ircc_work_permit_types,
            ircc_data_guide,
            ircc_xlsx_quirks_guide,
            ircc_immigration_report_template,
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
