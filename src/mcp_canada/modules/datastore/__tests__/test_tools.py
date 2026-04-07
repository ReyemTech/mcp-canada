"""Unit tests for datastore tool functions.

Tests each of the 6 ds_ tools using the patched_db fixture to use
an in-memory SQLite connection instead of the real file-based DB.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok(result: dict) -> dict:
    """Assert result is a make_response envelope and return data."""
    assert "_meta" in result, f"Expected _meta key, got: {result}"
    assert "data" in result, f"Expected data key, got: {result}"
    return result["data"]


def _err(result: dict) -> dict:
    """Assert result is a make_error envelope and return error dict."""
    assert "error" in result, f"Expected error key, got: {result}"
    assert "code" in result["error"], f"Expected error.code, got: {result}"
    return result["error"]


# ---------------------------------------------------------------------------
# TestDsCreateTable
# ---------------------------------------------------------------------------


class TestDsCreateTable:
    @pytest.mark.asyncio
    async def test_create_table_explicit_columns(self, patched_db):
        """ds_create_table with explicit columns dict returns table name and column count."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(
            table_name="test_tbl",
            columns=[{"name": "id", "type": "INTEGER"}, {"name": "val", "type": "TEXT"}],
        )
        data = _ok(result)
        assert data["table"] == "test_tbl"
        assert data["columns"] == 2

    @pytest.mark.asyncio
    async def test_create_table_infer_types_from_data(self, patched_db):
        """ds_create_table with data= and no columns= infers types from first row."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(
            table_name="inferred_tbl",
            data=[{"id": 1, "val": "a", "score": 3.14}],
        )
        data = _ok(result)
        assert data["table"] == "inferred_tbl"
        assert data["columns"] == 3

    @pytest.mark.asyncio
    async def test_create_table_invalid_name(self, patched_db):
        """ds_create_table with invalid table name returns INVALID_INPUT error."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(table_name="bad;name", columns=[{"name": "id", "type": "INTEGER"}])
        err = _err(result)
        assert err["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_create_table_no_schema_no_data(self, patched_db):
        """ds_create_table with neither columns nor data returns error."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(table_name="empty_tbl")
        err = _err(result)
        assert err["code"] in ("INVALID_INPUT", "DATASTORE_ERROR")

    @pytest.mark.asyncio
    async def test_create_table_lang_passes_through(self, patched_db):
        """ds_create_table passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(
            table_name="lang_tbl",
            columns=[{"name": "x", "type": "TEXT"}],
            lang="fr",
        )
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_create_table_meta_api_name(self, patched_db):
        """ds_create_table _meta.source.api is 'datastore'."""
        from mcp_canada.modules.datastore.tools import ds_create_table

        result = await ds_create_table(
            table_name="meta_tbl",
            columns=[{"name": "id", "type": "INTEGER"}],
        )
        assert result["_meta"]["source"]["api"] == "datastore"


# ---------------------------------------------------------------------------
# TestDsInsertData
# ---------------------------------------------------------------------------


class TestDsInsertData:
    @pytest.mark.asyncio
    async def test_insert_rows_returns_count(self, patched_db):
        """ds_insert_data returns the number of inserted rows."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_insert_data

        await ds_create_table(
            table_name="ins_tbl",
            columns=[{"name": "id", "type": "INTEGER"}, {"name": "val", "type": "TEXT"}],
        )
        result = await ds_insert_data("ins_tbl", rows=[{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
        data = _ok(result)
        assert data["inserted"] == 2

    @pytest.mark.asyncio
    async def test_insert_into_nonexistent_table_returns_error(self, patched_db):
        """ds_insert_data into a table that doesn't exist returns make_error."""
        from mcp_canada.modules.datastore.tools import ds_insert_data

        result = await ds_insert_data("nonexistent_tbl", rows=[{"id": 1}])
        err = _err(result)
        assert err["code"] == "DATASTORE_ERROR"

    @pytest.mark.asyncio
    async def test_insert_lang_passes_through(self, patched_db):
        """ds_insert_data passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_insert_data

        await ds_create_table(
            table_name="fr_tbl",
            columns=[{"name": "x", "type": "TEXT"}],
        )
        result = await ds_insert_data("fr_tbl", rows=[{"x": "hello"}], lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# TestDsQuery
# ---------------------------------------------------------------------------


class TestDsQuery:
    @pytest.mark.asyncio
    async def test_query_returns_columns_and_rows(self, patched_db):
        """ds_query SELECT returns QueryResult-shaped data with columns and rows."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_insert_data, ds_query

        await ds_create_table(
            table_name="q_tbl",
            columns=[{"name": "id", "type": "INTEGER"}, {"name": "name", "type": "TEXT"}],
        )
        await ds_insert_data("q_tbl", rows=[{"id": 1, "name": "Alice"}])

        result = await ds_query("SELECT * FROM q_tbl")
        data = _ok(result)
        assert "columns" in data
        assert "rows" in data
        assert "row_count" in data
        assert "truncated" in data
        assert data["row_count"] == 1
        assert data["rows"][0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_query_disallowed_statement(self, patched_db):
        """ds_query DELETE returns INVALID_INPUT error."""
        from mcp_canada.modules.datastore.tools import ds_query

        result = await ds_query("DELETE FROM some_table")
        err = _err(result)
        assert err["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_query_lang_passes_through(self, patched_db):
        """ds_query passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_query

        await ds_create_table(
            table_name="qlang_tbl",
            columns=[{"name": "x", "type": "INTEGER"}],
        )
        result = await ds_query("SELECT * FROM qlang_tbl", lang="fr")
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_query_empty_result_set(self, patched_db):
        """ds_query on empty table returns zero rows and not truncated."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_query

        await ds_create_table(
            table_name="empty_q",
            columns=[{"name": "id", "type": "INTEGER"}],
        )
        result = await ds_query("SELECT * FROM empty_q")
        data = _ok(result)
        assert data["row_count"] == 0
        assert data["truncated"] is False


# ---------------------------------------------------------------------------
# TestDsListTables
# ---------------------------------------------------------------------------


class TestDsListTables:
    @pytest.mark.asyncio
    async def test_list_tables_returns_names(self, patched_db):
        """ds_list_tables returns a list of table names."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_list_tables

        await ds_create_table(
            table_name="list_tbl_a",
            columns=[{"name": "id", "type": "INTEGER"}],
        )
        await ds_create_table(
            table_name="list_tbl_b",
            columns=[{"name": "x", "type": "TEXT"}],
        )

        result = await ds_list_tables()
        data = _ok(result)
        assert "tables" in data
        assert "list_tbl_a" in data["tables"]
        assert "list_tbl_b" in data["tables"]

    @pytest.mark.asyncio
    async def test_list_tables_count_field(self, patched_db):
        """ds_list_tables includes count field."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_list_tables

        await ds_create_table("cnt_tbl", columns=[{"name": "id", "type": "INTEGER"}])
        result = await ds_list_tables()
        data = _ok(result)
        assert "count" in data
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_list_tables_lang_passes_through(self, patched_db):
        """ds_list_tables passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_list_tables

        result = await ds_list_tables(lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# TestDsGetSchema
# ---------------------------------------------------------------------------


class TestDsGetSchema:
    @pytest.mark.asyncio
    async def test_get_schema_returns_columns(self, patched_db):
        """ds_get_schema returns column definitions for an existing table."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_get_schema

        await ds_create_table(
            table_name="schema_tbl",
            columns=[{"name": "id", "type": "INTEGER"}, {"name": "label", "type": "TEXT"}],
        )
        result = await ds_get_schema("schema_tbl")
        data = _ok(result)
        assert "columns" in data
        col_names = [c["name"] for c in data["columns"]]
        assert "id" in col_names
        assert "label" in col_names

    @pytest.mark.asyncio
    async def test_get_schema_nonexistent_table(self, patched_db):
        """ds_get_schema for a nonexistent table returns make_error."""
        from mcp_canada.modules.datastore.tools import ds_get_schema

        result = await ds_get_schema("nonexistent_schema_tbl")
        err = _err(result)
        assert err["code"] in ("NOT_FOUND", "DATASTORE_ERROR")

    @pytest.mark.asyncio
    async def test_get_schema_invalid_name(self, patched_db):
        """ds_get_schema with invalid identifier returns INVALID_INPUT."""
        from mcp_canada.modules.datastore.tools import ds_get_schema

        result = await ds_get_schema("bad;table")
        err = _err(result)
        assert err["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_get_schema_lang_passes_through(self, patched_db):
        """ds_get_schema passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_get_schema

        await ds_create_table(
            table_name="lang_schema_tbl",
            columns=[{"name": "x", "type": "INTEGER"}],
        )
        result = await ds_get_schema("lang_schema_tbl", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# TestDsDropTable
# ---------------------------------------------------------------------------


class TestDsDropTable:
    @pytest.mark.asyncio
    async def test_drop_existing_table(self, patched_db):
        """ds_drop_table drops the table and confirms via make_response."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_drop_table, ds_list_tables

        await ds_create_table(
            table_name="drop_me",
            columns=[{"name": "id", "type": "INTEGER"}],
        )
        result = await ds_drop_table("drop_me")
        data = _ok(result)
        assert data["dropped"] == "drop_me"

        # Verify it's really gone
        tables_result = await ds_list_tables()
        tables_data = _ok(tables_result)
        assert "drop_me" not in tables_data["tables"]

    @pytest.mark.asyncio
    async def test_drop_table_invalid_name(self, patched_db):
        """ds_drop_table with invalid identifier returns INVALID_INPUT."""
        from mcp_canada.modules.datastore.tools import ds_drop_table

        result = await ds_drop_table("bad;name")
        err = _err(result)
        assert err["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_drop_table_lang_passes_through(self, patched_db):
        """ds_drop_table passes lang to envelope."""
        from mcp_canada.modules.datastore.tools import ds_create_table, ds_drop_table

        await ds_create_table(
            table_name="drop_fr",
            columns=[{"name": "id", "type": "INTEGER"}],
        )
        result = await ds_drop_table("drop_fr", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# Docstring quality checks
# ---------------------------------------------------------------------------


class TestDocstringQuality:
    """Ensure all tools have required docstring elements."""

    def _get_tools(self):
        from mcp_canada.modules.datastore import tools as t
        return [
            t.ds_create_table,
            t.ds_insert_data,
            t.ds_query,
            t.ds_list_tables,
            t.ds_get_schema,
            t.ds_drop_table,
        ]

    def test_all_tools_have_use_for(self):
        """All tools must have 'Use for:' line in docstring."""
        for fn in self._get_tools():
            doc = fn.__doc__ or ""
            assert "Use for:" in doc, f"{fn.__name__} missing 'Use for:' in docstring"

    def test_all_tools_have_keywords(self):
        """All tools must have 'Keywords:' line in docstring."""
        for fn in self._get_tools():
            doc = fn.__doc__ or ""
            assert "Keywords:" in doc, f"{fn.__name__} missing 'Keywords:' in docstring"

    def test_all_tools_have_minimum_keywords(self):
        """All tools must have at least 8 keywords."""
        for fn in self._get_tools():
            doc = fn.__doc__ or ""
            kw_line = next((ln for ln in doc.splitlines() if "Keywords:" in ln), "")
            keywords = [k.strip() for k in kw_line.replace("Keywords:", "").split(",") if k.strip()]
            assert len(keywords) >= 8, (
                f"{fn.__name__} has only {len(keywords)} keywords (need 8+): {kw_line}"
            )
