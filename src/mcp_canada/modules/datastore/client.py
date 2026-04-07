"""Async SQLite client for the datastore module.

All public functions return (data, was_cached) tuples per project convention.
was_cached is always False — SQLite is local I/O, not a cached remote API.
"""

from __future__ import annotations

import aiosqlite

from mcp_canada.modules.datastore.constants import (
    ALLOWED_QUERY_PREFIXES,
    DB_PATH,
    IDENTIFIER_RE,
    MAX_QUERY_ROWS,
)

# Module-level singleton connection
_db: aiosqlite.Connection | None = None


def _validate_identifier(name: str) -> None:
    """Raise ValueError if `name` is not a safe SQLite identifier.

    Uses an allowlist regex: must start with a letter or underscore,
    followed by letters, digits, or underscores, max 64 chars total.
    This prevents SQL injection through table and column names.
    """
    if not IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Invalid identifier {name!r}: must match ^[a-zA-Z_][a-zA-Z0-9_]{{0,63}}$ "
            "(letters, digits, underscores only; cannot start with a digit; max 64 chars)"
        )


def _infer_sqlite_type(value: object) -> str:
    """Infer the SQLite column type for a Python value.

    Note: bool must be checked before int because bool is a subclass of int.
    """
    if isinstance(value, bool):
        return "INTEGER"
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"


def _db_path() -> str:
    """Return the database path string.

    Reads server._config to determine if ephemeral (in-memory) mode is active.
    Creates parent directories for the file path if needed.
    """
    try:
        from mcp_canada import server as _server

        if _server._config.get("ephemeral"):
            return ":memory:"
    except Exception:
        pass

    # File-based path: ensure parent directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)


async def get_db() -> aiosqlite.Connection:
    """Return the shared aiosqlite connection (lazy singleton).

    On first call: connects, enables WAL mode, foreign keys, and row_factory.
    Subsequent calls return the same connection object.
    """
    global _db
    if _db is None:
        path = _db_path()
        _db = await aiosqlite.connect(path)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
    return _db


async def close_db() -> None:
    """Close and release the shared connection."""
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def create_table(
    table: str, columns: list[tuple[str, str]]
) -> tuple[None, bool]:
    """Create a table with the given column definitions.

    Args:
        table: Table name (must pass identifier validation).
        columns: List of (column_name, sqlite_type) tuples.

    Returns:
        (None, False) — no data to return; was_cached always False.

    Raises:
        ValueError: If table name or any column name is invalid.
    """
    _validate_identifier(table)
    for col_name, _ in columns:
        _validate_identifier(col_name)

    col_defs = ", ".join(f"{col} {col_type}" for col, col_type in columns)
    sql = f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})"

    conn = await get_db()
    await conn.execute(sql)
    await conn.commit()
    return (None, False)


async def insert_rows(
    table: str, rows: list[dict]
) -> tuple[int, bool]:
    """Insert one or more rows into a table.

    Column names are validated against the identifier regex.
    Values are passed as parameters (safe from SQL injection).

    Args:
        table: Target table name.
        rows: List of dicts mapping column names to values.

    Returns:
        (row_count, False) — number of rows inserted; was_cached always False.

    Raises:
        ValueError: If table name or any column name is invalid.
    """
    if not rows:
        return (0, False)

    _validate_identifier(table)

    # Validate all column names across all rows
    for row in rows:
        for col in row:
            _validate_identifier(col)

    # Build INSERT statement from first row's keys (all rows must have same shape)
    columns = list(rows[0].keys())
    col_list = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

    values = [[row[col] for col in columns] for row in rows]

    conn = await get_db()
    await conn.executemany(sql, values)
    await conn.commit()
    return (len(rows), False)


async def run_query(sql: str) -> tuple[tuple[list[str], list[dict], bool], bool]:
    """Execute a read-only SQL query and return results.

    Only SELECT, PRAGMA, EXPLAIN, and CREATE INDEX statements are allowed.
    Results are capped at MAX_QUERY_ROWS rows; truncated flag is set if more exist.

    Args:
        sql: SQL statement to execute.

    Returns:
        ((columns, rows_as_dicts, truncated), False).

    Raises:
        ValueError: If the SQL prefix is not in ALLOWED_QUERY_PREFIXES.
    """
    stripped = sql.strip()
    upper = stripped.upper()

    allowed = any(upper.startswith(prefix) for prefix in ALLOWED_QUERY_PREFIXES)
    if not allowed:
        raise ValueError(
            f"Query not allowed. Only {', '.join(ALLOWED_QUERY_PREFIXES)} statements are permitted."
        )

    conn = await get_db()
    async with conn.execute(stripped) as cursor:
        col_names = [desc[0] for desc in (cursor.description or [])]
        raw_rows: list = list(await cursor.fetchmany(MAX_QUERY_ROWS + 1))

    truncated = len(raw_rows) > MAX_QUERY_ROWS
    if truncated:
        raw_rows = raw_rows[:MAX_QUERY_ROWS]

    rows_as_dicts = [dict(zip(col_names, row)) for row in raw_rows]
    return ((col_names, rows_as_dicts, truncated), False)


async def list_tables() -> tuple[list[str], bool]:
    """Return a sorted list of all user-created table names.

    Returns:
        (table_names, False) — list of table name strings; was_cached always False.
    """
    conn = await get_db()
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ) as cursor:
        rows = await cursor.fetchall()

    return ([row[0] for row in rows], False)


async def get_schema(table: str) -> tuple[list[dict], bool]:
    """Return column metadata for a table via PRAGMA table_info.

    Args:
        table: Table name (must pass identifier validation).

    Returns:
        (column_info_dicts, False) where each dict has: cid, name, type,
        notnull, dflt_value, pk; was_cached always False.

    Raises:
        ValueError: If table name is invalid.
    """
    _validate_identifier(table)

    conn = await get_db()
    async with conn.execute(f"PRAGMA table_info({table})") as cursor:
        rows = await cursor.fetchall()

    col_info = [dict(row) for row in rows]
    return (col_info, False)


async def drop_table(table: str) -> tuple[None, bool]:
    """Drop a table if it exists.

    Args:
        table: Table name (must pass identifier validation).

    Returns:
        (None, False) — no data to return; was_cached always False.

    Raises:
        ValueError: If table name is invalid.
    """
    _validate_identifier(table)

    conn = await get_db()
    await conn.execute(f"DROP TABLE IF EXISTS {table}")
    await conn.commit()
    return (None, False)
