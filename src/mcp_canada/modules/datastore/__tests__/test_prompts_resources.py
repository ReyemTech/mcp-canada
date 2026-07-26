# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Datastore prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.datastore.prompts import (
    ds_create_and_query,
    ds_cross_module_join,
    ds_explore_tables,
    ds_quick_query,
)
from mcp_canada.modules.datastore.resources import (
    ds_column_types,
    ds_cross_module_patterns_guide,
    ds_identifier_rules,
    ds_query_report_template,
    ds_schema_report_template,
    ds_sql_guide,
)


class TestDatastorePrompts:
    """Tests for the 4 Datastore @prompt functions."""

    # ------------------------------------------------------------------
    # ds_create_and_query — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_and_query_en_returns_messages(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_create_and_query_en_roles(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_create_and_query_en_references_create_tool(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ds_create_table" in full_text

    @pytest.mark.asyncio
    async def test_create_and_query_en_references_insert_tool(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ds_insert_data" in full_text

    @pytest.mark.asyncio
    async def test_create_and_query_en_references_query_tool(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "ds_query" in full_text

    @pytest.mark.asyncio
    async def test_create_and_query_fr_returns_messages(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_create_and_query_fr_is_french(self):
        p = FunctionPrompt.from_function(ds_create_and_query)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("table", "données", "stocker", "créer", "SQL")
        )

    # ------------------------------------------------------------------
    # ds_quick_query — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_query_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ds_quick_query)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_query_en_references_tool(self):
        p = FunctionPrompt.from_function(ds_quick_query)
        result = await p.render({"lang": "en"})
        assert "ds_query" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_query_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(ds_quick_query)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_query_fr_is_french(self):
        p = FunctionPrompt.from_function(ds_quick_query)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "ds_query" in text
        assert any(word in text for word in ("SELECT", "Utilisez", "requête", "table"))

    # ------------------------------------------------------------------
    # ds_explore_tables — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_tables_en_returns_single_message(self):
        p = FunctionPrompt.from_function(ds_explore_tables)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_explore_tables_en_references_list_tool(self):
        p = FunctionPrompt.from_function(ds_explore_tables)
        result = await p.render({"lang": "en"})
        assert "ds_list_tables" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_explore_tables_en_references_schema_tool(self):
        p = FunctionPrompt.from_function(ds_explore_tables)
        result = await p.render({"lang": "en"})
        assert "ds_get_schema" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_explore_tables_fr_is_french(self):
        p = FunctionPrompt.from_function(ds_explore_tables)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("tables", "schéma", "Utilisez", "structure"))

    # ------------------------------------------------------------------
    # ds_cross_module_join — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_cross_module_join_en_returns_messages(self):
        p = FunctionPrompt.from_function(ds_cross_module_join)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_cross_module_join_en_mentions_join(self):
        p = FunctionPrompt.from_function(ds_cross_module_join)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "JOIN" in full_text or "join" in full_text.lower()

    @pytest.mark.asyncio
    async def test_cross_module_join_fr_is_french(self):
        p = FunctionPrompt.from_function(ds_cross_module_join)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("combiner", "modules", "SQL", "données", "JOIN")
        )


class TestDatastoreResources:
    """Tests for the 6 Datastore @resource functions."""

    # ------------------------------------------------------------------
    # data://datastore/column-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_column_types_is_valid_json(self):
        r = FunctionResource.from_function(
            ds_column_types, uri="data://datastore/column-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_column_types_has_text_and_integer(self):
        r = FunctionResource.from_function(
            ds_column_types, uri="data://datastore/column-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert "TEXT" in data or "text" in data
        assert "INTEGER" in data or "integer" in data

    # ------------------------------------------------------------------
    # data://datastore/identifier-rules
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_identifier_rules_is_valid_json(self):
        r = FunctionResource.from_function(
            ds_identifier_rules, uri="data://datastore/identifier-rules"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_identifier_rules_has_pattern(self):
        r = FunctionResource.from_function(
            ds_identifier_rules, uri="data://datastore/identifier-rules"
        )
        content = await r.read()
        data = json.loads(content)
        assert "pattern" in data or "regex" in data

    # ------------------------------------------------------------------
    # docs://datastore/sql-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_sql_guide_is_markdown(self):
        r = FunctionResource.from_function(
            ds_sql_guide, uri="docs://datastore/sql-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "SQL guide must start with # heading"

    @pytest.mark.asyncio
    async def test_sql_guide_mentions_select(self):
        r = FunctionResource.from_function(
            ds_sql_guide, uri="docs://datastore/sql-guide"
        )
        content = await r.read()
        assert "SELECT" in content

    @pytest.mark.asyncio
    async def test_sql_guide_mentions_pragma(self):
        r = FunctionResource.from_function(
            ds_sql_guide, uri="docs://datastore/sql-guide"
        )
        content = await r.read()
        assert "PRAGMA" in content

    # ------------------------------------------------------------------
    # docs://datastore/cross-module-patterns
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_cross_module_guide_is_markdown(self):
        r = FunctionResource.from_function(
            ds_cross_module_patterns_guide, uri="docs://datastore/cross-module-patterns"
        )
        content = await r.read()
        assert content.startswith("#"), "Cross-module guide must start with # heading"

    @pytest.mark.asyncio
    async def test_cross_module_guide_mentions_join(self):
        r = FunctionResource.from_function(
            ds_cross_module_patterns_guide, uri="docs://datastore/cross-module-patterns"
        )
        content = await r.read()
        assert "JOIN" in content

    # ------------------------------------------------------------------
    # template://datastore/query-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_query_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            ds_query_report_template, uri="template://datastore/query-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Query report template must start with # heading"

    @pytest.mark.asyncio
    async def test_query_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ds_query_report_template, uri="template://datastore/query-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content

    # ------------------------------------------------------------------
    # template://datastore/schema-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_schema_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            ds_schema_report_template, uri="template://datastore/schema-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Schema report template must start with # heading"

    @pytest.mark.asyncio
    async def test_schema_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            ds_schema_report_template, uri="template://datastore/schema-report"
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
            ds_column_types,
            ds_identifier_rules,
            ds_sql_guide,
            ds_cross_module_patterns_guide,
            ds_query_report_template,
            ds_schema_report_template,
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
