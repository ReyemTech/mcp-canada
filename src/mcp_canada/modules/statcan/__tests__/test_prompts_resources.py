"""Unit tests for StatCan prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.statcan.prompts import (
    statcan_compare_series,
    statcan_explore_sdmx,
    statcan_find_data,
    statcan_monitor_changes,
    statcan_quick_vector,
    statcan_store_and_query,
)
from mcp_canada.modules.statcan.resources import (
    statcan_coordinate_system_guide,
    statcan_frequency_codes,
    statcan_scalar_factor_codes,
    statcan_sdmx_key_syntax_guide,
    statcan_status_codes,
    statcan_time_series_report_template,
    statcan_uom_codes,
    statcan_wds_guide,
)


class TestStatCanPrompts:
    """Tests for the 6 StatCan @prompt functions."""

    # ------------------------------------------------------------------
    # statcan_find_data — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_find_data_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_find_data_en_roles(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_find_data_en_references_tool(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_search_cubes" in full_text

    @pytest.mark.asyncio
    async def test_find_data_en_references_metadata_tool(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_get_cube_metadata" in full_text

    @pytest.mark.asyncio
    async def test_find_data_en_references_data_tool(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_get_data_by_vector" in full_text

    @pytest.mark.asyncio
    async def test_find_data_fr_returns_messages(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_find_data_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_find_data)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("données", "statistiques", "chercher", "sujet", "recherche")
        )

    # ------------------------------------------------------------------
    # statcan_quick_vector — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_vector_en_returns_single_message(self):
        p = FunctionPrompt.from_function(statcan_quick_vector)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_vector_en_references_tool(self):
        p = FunctionPrompt.from_function(statcan_quick_vector)
        result = await p.render({"lang": "en"})
        assert "sc_get_data_by_vector" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_vector_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(statcan_quick_vector)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_vector_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_quick_vector)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "sc_get_data_by_vector" in text
        assert any(word in text for word in ("vecteur", "Utilisez", "récentes", "récents"))

    # ------------------------------------------------------------------
    # statcan_explore_sdmx — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_sdmx_en_returns_messages(self):
        p = FunctionPrompt.from_function(statcan_explore_sdmx)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_explore_sdmx_en_roles(self):
        p = FunctionPrompt.from_function(statcan_explore_sdmx)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_sdmx_en_references_tool(self):
        p = FunctionPrompt.from_function(statcan_explore_sdmx)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_get_sdmx_structure" in full_text

    @pytest.mark.asyncio
    async def test_explore_sdmx_en_references_data_tool(self):
        p = FunctionPrompt.from_function(statcan_explore_sdmx)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_get_sdmx_data" in full_text

    @pytest.mark.asyncio
    async def test_explore_sdmx_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_explore_sdmx)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("SDMX", "données", "structure", "dimensions")
        )

    # ------------------------------------------------------------------
    # statcan_store_and_query — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_store_and_query_en_returns_messages(self):
        p = FunctionPrompt.from_function(statcan_store_and_query)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_store_and_query_en_references_fetch_tool(self):
        p = FunctionPrompt.from_function(statcan_store_and_query)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_fetch_vectors_to_store" in full_text

    @pytest.mark.asyncio
    async def test_store_and_query_en_references_query_tool(self):
        p = FunctionPrompt.from_function(statcan_store_and_query)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ds_query" in full_text

    @pytest.mark.asyncio
    async def test_store_and_query_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_store_and_query)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("stocker", "SQL", "requête", "données", "vecteurs")
        )

    # ------------------------------------------------------------------
    # statcan_monitor_changes — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_monitor_changes_en_returns_single_message(self):
        p = FunctionPrompt.from_function(statcan_monitor_changes)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_monitor_changes_en_references_tool(self):
        p = FunctionPrompt.from_function(statcan_monitor_changes)
        result = await p.render({"lang": "en"})
        assert "sc_get_changed_series" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_monitor_changes_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_monitor_changes)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "sc_get_changed_series" in text or "sc_get_changed_cubes" in text
        assert any(word in text for word in ("mises", "changé", "Utilisez", "modifiées"))

    # ------------------------------------------------------------------
    # statcan_compare_series — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_compare_series_en_returns_messages(self):
        p = FunctionPrompt.from_function(statcan_compare_series)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_compare_series_en_references_tool(self):
        p = FunctionPrompt.from_function(statcan_compare_series)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "sc_get_bulk_vector_data" in full_text

    @pytest.mark.asyncio
    async def test_compare_series_fr_is_french(self):
        p = FunctionPrompt.from_function(statcan_compare_series)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("comparer", "vecteurs", "séries", "plusieurs")
        )


class TestStatCanResources:
    """Tests for the 8 StatCan @resource functions."""

    # ------------------------------------------------------------------
    # data://statcan/frequency-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_frequency_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            statcan_frequency_codes, uri="data://statcan/frequency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_frequency_codes_has_daily_and_monthly(self):
        r = FunctionResource.from_function(
            statcan_frequency_codes, uri="data://statcan/frequency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        # Should have entries for common frequencies
        values = [str(v) for v in data.values()]
        all_text = " ".join(str(v) for v in data.values())
        assert any("daily" in str(v).lower() or "Daily" in str(v) for v in data.values())

    @pytest.mark.asyncio
    async def test_frequency_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            statcan_frequency_codes, uri="data://statcan/frequency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        # Get first value and check it has en/fr keys
        first_val = next(iter(data.values()))
        assert "en" in first_val
        assert "fr" in first_val

    # ------------------------------------------------------------------
    # data://statcan/scalar-factor-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_scalar_factor_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            statcan_scalar_factor_codes, uri="data://statcan/scalar-factor-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_scalar_factor_codes_has_millions(self):
        r = FunctionResource.from_function(
            statcan_scalar_factor_codes, uri="data://statcan/scalar-factor-codes"
        )
        content = await r.read()
        data = json.loads(content)
        all_text = " ".join(str(v) for v in data.values())
        assert "million" in all_text.lower()

    # ------------------------------------------------------------------
    # data://statcan/status-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_status_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            statcan_status_codes, uri="data://statcan/status-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_status_codes_has_entries(self):
        r = FunctionResource.from_function(
            statcan_status_codes, uri="data://statcan/status-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) >= 3

    # ------------------------------------------------------------------
    # data://statcan/uom-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_uom_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            statcan_uom_codes, uri="data://statcan/uom-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_uom_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            statcan_uom_codes, uri="data://statcan/uom-codes"
        )
        content = await r.read()
        data = json.loads(content)
        first_val = next(iter(data.values()))
        assert "en" in first_val
        assert "fr" in first_val

    # ------------------------------------------------------------------
    # docs://statcan/wds-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_wds_guide_is_markdown(self):
        r = FunctionResource.from_function(
            statcan_wds_guide, uri="docs://statcan/wds-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "WDS guide must start with # heading"

    @pytest.mark.asyncio
    async def test_wds_guide_mentions_rate_limit(self):
        r = FunctionResource.from_function(
            statcan_wds_guide, uri="docs://statcan/wds-guide"
        )
        content = await r.read()
        assert "rate" in content.lower() or "req/s" in content

    # ------------------------------------------------------------------
    # docs://statcan/sdmx-key-syntax
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_sdmx_guide_is_markdown(self):
        r = FunctionResource.from_function(
            statcan_sdmx_key_syntax_guide, uri="docs://statcan/sdmx-key-syntax"
        )
        content = await r.read()
        assert content.startswith("#"), "SDMX guide must start with # heading"

    @pytest.mark.asyncio
    async def test_sdmx_guide_mentions_dimensions(self):
        r = FunctionResource.from_function(
            statcan_sdmx_key_syntax_guide, uri="docs://statcan/sdmx-key-syntax"
        )
        content = await r.read()
        assert "dimension" in content.lower() or "SDMX" in content

    # ------------------------------------------------------------------
    # docs://statcan/coordinate-system
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_coordinate_guide_is_markdown(self):
        r = FunctionResource.from_function(
            statcan_coordinate_system_guide, uri="docs://statcan/coordinate-system"
        )
        content = await r.read()
        assert content.startswith("#"), "Coordinate guide must start with # heading"

    @pytest.mark.asyncio
    async def test_coordinate_guide_mentions_vector(self):
        r = FunctionResource.from_function(
            statcan_coordinate_system_guide, uri="docs://statcan/coordinate-system"
        )
        content = await r.read()
        assert "vector" in content.lower() or "vectorId" in content

    # ------------------------------------------------------------------
    # template://statcan/time-series-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_time_series_template_is_markdown(self):
        r = FunctionResource.from_function(
            statcan_time_series_report_template, uri="template://statcan/time-series-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Template must start with # heading"

    @pytest.mark.asyncio
    async def test_time_series_template_has_placeholders(self):
        r = FunctionResource.from_function(
            statcan_time_series_report_template, uri="template://statcan/time-series-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    @pytest.mark.asyncio
    async def test_time_series_template_has_product_id_placeholder(self):
        r = FunctionResource.from_function(
            statcan_time_series_report_template, uri="template://statcan/time-series-report"
        )
        content = await r.read()
        assert "{product_id}" in content or "{vector_id}" in content

    # ------------------------------------------------------------------
    # Zero-param sanity — resources must have no parameters
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            statcan_frequency_codes,
            statcan_scalar_factor_codes,
            statcan_status_codes,
            statcan_uom_codes,
            statcan_wds_guide,
            statcan_sdmx_key_syntax_guide,
            statcan_coordinate_system_guide,
            statcan_time_series_report_template,
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
