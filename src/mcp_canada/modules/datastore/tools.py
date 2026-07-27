"""Datastore @tool functions for the local SQLite persistence layer.

Provides 6 agent-facing tools for creating tables, inserting data, querying,
listing tables, viewing schemas, and dropping tables.

Each tool wraps a client function in the make_response/make_error envelope
with BM25-optimized docstrings for tool discovery.
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.datastore import client
from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared.errors import InvalidInput

_API_NAME = "datastore"
_API_URL = ""


# ---------------------------------------------------------------------------
# Tool 1: Create table
# ---------------------------------------------------------------------------


@tool
async def ds_create_table(
    table_name: str,
    columns: list[dict] | None = None,
    data: list[dict] | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Create a named table in the local SQLite datastore.

    Use for: creating tables to store data from any source, setting up
    structured storage for agent-generated or fetched data.
    Keywords: datastore, create, table, sqlite, store, persist, schema, columns, local, database
    """
    try:
        if columns is not None:
            # Explicit schema provided
            col_tuples: list[tuple[str, str]] = [
                (c["name"], c["type"]) for c in columns
            ]
        elif data is not None and len(data) > 0:
            # Infer types from the first row
            col_tuples = [
                (col_name, client._infer_sqlite_type(val))
                for col_name, val in data[0].items()
            ]
        else:
            return make_error(
                "INVALID_INPUT",
                "Must provide either 'columns' (explicit schema) or 'data' (for type inference).",
                lang=lang,
            )

        _, was_cached = await client.create_table(table_name, col_tuples)
        return make_response(
            {"table": table_name, "columns": len(col_tuples)},
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except InvalidInput as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Tool 2: Insert data
# ---------------------------------------------------------------------------


@tool
async def ds_insert_data(
    table_name: str,
    rows: list[dict],
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Insert rows of data into an existing table in the local SQLite datastore.

    Use for: storing fetched data, saving agent results, or populating
    tables created with ds_create_table.
    Keywords: datastore, insert, rows, data, store, sqlite, write, append, persist, save, record, bulk
    """
    try:
        row_count, was_cached = await client.insert_rows(table_name, rows)
        return make_response(
            {"table": table_name, "inserted": row_count},
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except InvalidInput as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Tool 3: Query
# ---------------------------------------------------------------------------


@tool
async def ds_query(
    sql: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Run a read-only SQL query against the local SQLite datastore.

    Use for: retrieving, filtering, joining, or aggregating data stored in
    the local datastore. Supports SELECT, PRAGMA, EXPLAIN, and CREATE INDEX.
    Returns up to 1000 rows by default.
    Keywords: datastore, query, select, sql, sqlite, search, filter, retrieve, join, aggregate, rows, results
    """
    try:
        (columns, rows, truncated), was_cached = await client.run_query(sql)
        return make_response(
            {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated,
            },
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except InvalidInput as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Tool 4: List tables
# ---------------------------------------------------------------------------


@tool
async def ds_list_tables(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all tables in the local SQLite datastore.

    Use for: discovering what tables exist in the local datastore, checking
    if a table has been created, or auditing stored data.
    Keywords: datastore, list, tables, show, sqlite, catalog, discover, available, names, database
    """
    try:
        table_names, was_cached = await client.list_tables()
        return make_response(
            {"tables": table_names, "count": len(table_names)},
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Tool 5: Get schema
# ---------------------------------------------------------------------------


@tool
async def ds_get_schema(
    table_name: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the column schema for a table in the local SQLite datastore.

    Use for: inspecting the structure of an existing table, verifying column
    names and types before querying or inserting data.
    Keywords: datastore, schema, columns, structure, sqlite, table, describe, inspect, types, definition, metadata, info
    """
    try:
        col_info, was_cached = await client.get_schema(table_name)
        if not col_info:
            return make_error(
                "NOT_FOUND",
                f"Table '{table_name}' not found or has no columns.",
                lang=lang,
            )
        return make_response(
            {"table": table_name, "columns": col_info},
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except InvalidInput as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Tool 6: Drop table
# ---------------------------------------------------------------------------


@tool
async def ds_drop_table(
    table_name: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Drop (delete) a table from the local SQLite datastore.

    Use for: removing tables that are no longer needed, cleaning up
    temporary tables, or resetting the datastore.
    Keywords: datastore, drop, delete, remove, table, sqlite, cleanup, reset, destroy, clear, purge, truncate
    """
    try:
        _, was_cached = await client.drop_table(table_name)
        return make_response(
            {"dropped": table_name},
            api_name=_API_NAME,
            api_url=_API_URL,
            cached=was_cached,
            lang=lang,
        )
    except InvalidInput as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except Exception as exc:
        return make_error("DATASTORE_ERROR", str(exc), lang=lang)
