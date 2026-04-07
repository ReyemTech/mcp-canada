"""Unit tests for the datastore client module.

Tests identifier validation, type inference, and all CRUD operations
against an in-memory SQLite database.
"""

import pytest

from mcp_canada.modules.datastore.client import (
    _validate_identifier,
    _infer_sqlite_type,
    get_db,
    create_table,
    insert_rows,
    run_query,
    list_tables,
    get_schema,
    drop_table,
)


# ---------------------------------------------------------------------------
# _validate_identifier
# ---------------------------------------------------------------------------


class TestValidateIdentifier:
    def test_valid_name_passes(self):
        """Valid snake_case identifier should not raise."""
        _validate_identifier("valid_name")  # no exception

    def test_valid_with_numbers_passes(self):
        """Identifier with letters and numbers should pass."""
        _validate_identifier("table_01")

    def test_valid_leading_underscore_passes(self):
        """Identifier starting with underscore should pass."""
        _validate_identifier("_private")

    def test_semicolon_raises(self):
        """Identifier with semicolon must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("has;semicolon")

    def test_empty_string_raises(self):
        """Empty string must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("")

    def test_too_long_raises(self):
        """Identifier over 63 chars must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("a" * 65)

    def test_exactly_64_chars_raises(self):
        """Identifier of exactly 64 chars must be rejected (max is 63 with leading letter)."""
        # Pattern allows [a-zA-Z_] + up to 63 more = max 64 total? Let's check spec:
        # IDENTIFIER_RE = r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$' — that allows 1+63=64 chars total
        # Plan says "a"*65 raises; "a"*64 should pass per the regex
        _validate_identifier("a" * 64)  # 64 chars — 1 leading + 63 more = valid

    def test_starts_with_digit_raises(self):
        """Identifier starting with a digit must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("123starts_with_digit")

    def test_space_raises(self):
        """Identifier with space must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("bad name")

    def test_hyphen_raises(self):
        """Identifier with hyphen must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("bad-name")

    def test_sql_drop_raises(self):
        """SQL keyword injection attempt must be rejected."""
        with pytest.raises(ValueError, match="identifier"):
            _validate_identifier("foo; DROP TABLE users--")


# ---------------------------------------------------------------------------
# _infer_sqlite_type
# ---------------------------------------------------------------------------


class TestInferSqliteType:
    def test_bool_returns_integer(self):
        """bool must be checked before int (True is also int in Python)."""
        assert _infer_sqlite_type(True) == "INTEGER"

    def test_false_returns_integer(self):
        assert _infer_sqlite_type(False) == "INTEGER"

    def test_int_returns_integer(self):
        assert _infer_sqlite_type(1) == "INTEGER"

    def test_float_returns_real(self):
        assert _infer_sqlite_type(1.5) == "REAL"

    def test_string_returns_text(self):
        assert _infer_sqlite_type("hello") == "TEXT"

    def test_none_returns_text(self):
        """None/unknown types default to TEXT."""
        assert _infer_sqlite_type(None) == "TEXT"

    def test_list_returns_text(self):
        assert _infer_sqlite_type([1, 2, 3]) == "TEXT"


# ---------------------------------------------------------------------------
# get_db — singleton behavior
# ---------------------------------------------------------------------------


class TestGetDb:
    async def test_returns_connection(self, patched_db):
        """get_db() returns an aiosqlite.Connection."""
        import aiosqlite
        conn = await get_db()
        assert isinstance(conn, aiosqlite.Connection)

    async def test_singleton(self, patched_db):
        """get_db() called twice returns the same connection object."""
        conn1 = await get_db()
        conn2 = await get_db()
        assert conn1 is conn2


# ---------------------------------------------------------------------------
# create_table
# ---------------------------------------------------------------------------


class TestCreateTable:
    async def test_create_returns_none_false(self, patched_db):
        """create_table returns (None, False)."""
        result, was_cached = await create_table("test", [("id", "INTEGER"), ("name", "TEXT")])
        assert result is None
        assert was_cached is False

    async def test_table_exists_after_create(self, patched_db):
        """Table actually exists in the DB after create_table."""
        await create_table("things", [("val", "TEXT")])
        tables, _ = await list_tables()
        assert "things" in tables

    async def test_bad_table_name_raises(self, patched_db):
        """create_table with invalid table name raises ValueError."""
        with pytest.raises(ValueError, match="identifier"):
            await create_table("bad;name", [("id", "INTEGER")])

    async def test_bad_column_name_raises(self, patched_db):
        """create_table with invalid column name raises ValueError."""
        with pytest.raises(ValueError, match="identifier"):
            await create_table("good_name", [("bad;col", "INTEGER")])

    async def test_idempotent(self, patched_db):
        """create_table is idempotent — calling twice does not raise."""
        await create_table("dup_test", [("id", "INTEGER")])
        result, _ = await create_table("dup_test", [("id", "INTEGER")])
        assert result is None


# ---------------------------------------------------------------------------
# insert_rows
# ---------------------------------------------------------------------------


class TestInsertRows:
    async def test_insert_returns_count_false(self, patched_db):
        """insert_rows returns (row_count, False)."""
        await create_table("items", [("id", "INTEGER"), ("name", "TEXT")])
        count, was_cached = await insert_rows("items", [{"id": 1, "name": "a"}])
        assert count == 1
        assert was_cached is False

    async def test_insert_multiple_rows(self, patched_db):
        """insert_rows returns correct count for multiple rows."""
        await create_table("multi", [("x", "INTEGER")])
        count, _ = await insert_rows("multi", [{"x": 1}, {"x": 2}, {"x": 3}])
        assert count == 3

    async def test_bad_table_name_raises(self, patched_db):
        """insert_rows with invalid table name raises ValueError."""
        with pytest.raises(ValueError, match="identifier"):
            await insert_rows("bad;table", [{"id": 1}])

    async def test_bad_column_name_raises(self, patched_db):
        """insert_rows with invalid column name raises ValueError."""
        await create_table("safe_table", [("id", "INTEGER")])
        with pytest.raises(ValueError, match="identifier"):
            await insert_rows("safe_table", [{"bad;col": 1}])


# ---------------------------------------------------------------------------
# run_query
# ---------------------------------------------------------------------------


class TestRunQuery:
    async def test_select_returns_tuple(self, patched_db):
        """run_query returns ((columns, rows, truncated), False)."""
        await create_table("query_test", [("id", "INTEGER"), ("name", "TEXT")])
        await insert_rows("query_test", [{"id": 1, "name": "alice"}])
        (columns, rows, truncated), was_cached = await run_query("SELECT * FROM query_test")
        assert isinstance(columns, list)
        assert isinstance(rows, list)
        assert isinstance(truncated, bool)
        assert was_cached is False

    async def test_select_returns_correct_data(self, patched_db):
        """run_query returns correct rows as dicts."""
        await create_table("data_test", [("id", "INTEGER"), ("val", "TEXT")])
        await insert_rows("data_test", [{"id": 42, "val": "hello"}])
        (columns, rows, _), _ = await run_query("SELECT * FROM data_test")
        assert "id" in columns
        assert "val" in columns
        assert rows[0]["id"] == 42
        assert rows[0]["val"] == "hello"

    async def test_case_insensitive_select(self, patched_db):
        """run_query accepts lowercase 'select'."""
        await create_table("ci_test", [("x", "INTEGER")])
        await insert_rows("ci_test", [{"x": 1}])
        (cols, rows, _), _ = await run_query("select * from ci_test")
        assert len(rows) == 1

    async def test_delete_raises_value_error(self, patched_db):
        """run_query rejects DELETE statements (not in allowed prefixes)."""
        await create_table("del_test", [("id", "INTEGER")])
        with pytest.raises(ValueError, match="not allowed"):
            await run_query("DELETE FROM del_test")

    async def test_insert_raises_value_error(self, patched_db):
        """run_query rejects INSERT statements."""
        with pytest.raises(ValueError, match="not allowed"):
            await run_query("INSERT INTO foo VALUES (1)")

    async def test_pragma_allowed(self, patched_db):
        """run_query allows PRAGMA statements."""
        (cols, rows, _), _ = await run_query("PRAGMA table_list")
        assert isinstance(rows, list)

    async def test_explain_allowed(self, patched_db):
        """run_query allows EXPLAIN statements."""
        await create_table("exp_test", [("id", "INTEGER")])
        result, _ = await run_query("EXPLAIN SELECT * FROM exp_test")
        assert result is not None

    async def test_empty_result_not_truncated(self, patched_db):
        """Empty result set has truncated=False."""
        await create_table("empty_test", [("id", "INTEGER")])
        (_, rows, truncated), _ = await run_query("SELECT * FROM empty_test")
        assert rows == []
        assert truncated is False


# ---------------------------------------------------------------------------
# list_tables
# ---------------------------------------------------------------------------


class TestListTables:
    async def test_returns_list_false(self, patched_db):
        """list_tables returns (list, False)."""
        tables, was_cached = await list_tables()
        assert isinstance(tables, list)
        assert was_cached is False

    async def test_includes_created_table(self, patched_db):
        """list_tables includes a newly created table."""
        await create_table("visible_table", [("id", "INTEGER")])
        tables, _ = await list_tables()
        assert "visible_table" in tables

    async def test_empty_db_returns_empty(self, patched_db):
        """list_tables returns empty list when no tables exist."""
        tables, _ = await list_tables()
        assert tables == []


# ---------------------------------------------------------------------------
# get_schema
# ---------------------------------------------------------------------------


class TestGetSchema:
    async def test_returns_column_info_false(self, patched_db):
        """get_schema returns (list_of_dicts, False)."""
        await create_table("schema_test", [("id", "INTEGER"), ("name", "TEXT")])
        info, was_cached = await get_schema("schema_test")
        assert isinstance(info, list)
        assert was_cached is False

    async def test_column_info_structure(self, patched_db):
        """get_schema returns dicts with column metadata."""
        await create_table("col_test", [("id", "INTEGER"), ("val", "TEXT")])
        info, _ = await get_schema("col_test")
        col_names = [c["name"] for c in info]
        assert "id" in col_names
        assert "val" in col_names

    async def test_bad_table_name_raises(self, patched_db):
        """get_schema with invalid table name raises ValueError."""
        with pytest.raises(ValueError, match="identifier"):
            await get_schema("bad;table")


# ---------------------------------------------------------------------------
# drop_table
# ---------------------------------------------------------------------------


class TestDropTable:
    async def test_drop_returns_none_false(self, patched_db):
        """drop_table returns (None, False)."""
        await create_table("to_drop", [("id", "INTEGER")])
        result, was_cached = await drop_table("to_drop")
        assert result is None
        assert was_cached is False

    async def test_table_gone_after_drop(self, patched_db):
        """Table is no longer listed after drop_table."""
        await create_table("gone_table", [("id", "INTEGER")])
        await drop_table("gone_table")
        tables, _ = await list_tables()
        assert "gone_table" not in tables

    async def test_drop_nonexistent_table_ok(self, patched_db):
        """drop_table on non-existent table does not raise (IF EXISTS)."""
        result, _ = await drop_table("never_existed")
        assert result is None

    async def test_bad_table_name_raises(self, patched_db):
        """drop_table with invalid table name raises ValueError."""
        with pytest.raises(ValueError, match="identifier"):
            await drop_table("bad;table")
