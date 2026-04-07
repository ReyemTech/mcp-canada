# Phase 7: Datastore + SSL - Research

**Researched:** 2026-04-07
**Domain:** aiosqlite async SQLite, SQL injection prevention, httpx SSL configuration
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Database file lives at `~/.mcp-canada/datastore.db` (global, user-level)
- Data persists across server restarts by default
- Configurable: `--ephemeral` flag for in-memory mode (no disk writes)
- Auto-created on first use — first `ds_create_table` call creates file + parent dirs
- WAL mode enabled on connection for concurrent read/write support
- `ds_query` allows: SELECT, PRAGMA, EXPLAIN, CREATE INDEX
- Default row limit: 1000 rows (agent can override with explicit LIMIT clause)
- All writes go through `ds_insert_data` and `ds_create_table` tools — no raw INSERT/UPDATE/DELETE in ds_query
- `ds_drop_table` executes immediately — no confirmation flag
- SQL injection prevention via regex allowlist on table/column identifiers: `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`
- Module prefix convention: `statcan_cpi_monthly`, `boc_exchange_rates`
- Column type inference from first row by default (TEXT, REAL, INTEGER)
- Optional explicit schema parameter for precise control
- Duplicate handling: simple INSERT (append all)
- SSL: Try certifi first (already bundled with httpx) — no new dependency if it works
- If certifi fails, fall back to scoped `verify=False` on statcan httpx client only
- Never touch `shared/http.py` or the lifespan shared client
- Do NOT add truststore as a dependency unless certifi fails AND truststore succeeds
- Quick test only — 30 min max effort on SSL

### Claude's Discretion

- Exact aiosqlite connection management pattern (singleton vs per-call)
- SQLite PRAGMA settings beyond WAL mode
- How to surface the `--ephemeral` flag in argparse (likely on the main parser, not subcommand)
- Error message wording for SQL injection rejections

### Deferred Ideas (OUT OF SCOPE)

- None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DS-01 | Agent can create a named SQLite table with specified columns and types | aiosqlite `execute()` + `CREATE TABLE IF NOT EXISTS` + identifier allowlist |
| DS-02 | Agent can insert rows of data into an existing table | aiosqlite `executemany()` + `await db.commit()` |
| DS-03 | Agent can run read-only SQL queries (SELECT/PRAGMA only) across any stored tables | aiosqlite `execute()` + `fetchmany(1000)` + keyword prefix guard |
| DS-04 | Agent can list all tables in the datastore | `SELECT name FROM sqlite_master WHERE type='table'` |
| DS-05 | Agent can view the schema (columns and types) of a specific table | `PRAGMA table_info(name)` with identifier allowlist |
| DS-06 | Agent can drop a table by name | `DROP TABLE IF EXISTS {name}` with identifier allowlist |
| DS-07 | Table and column names validated against regex allowlist to prevent SQL injection | `re.fullmatch(r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$', name)` before any SQL executes |
| DS-08 | All database operations use async SQLite (aiosqlite) to avoid blocking the event loop | aiosqlite 0.22.1 uses a dedicated thread per connection; never blocks asyncio loop |
| INF-01 | StatCan SSL certificate handling attempts proper cert resolution before falling back to scoped verify=False | httpx `AsyncClient(verify=True)` probe then `AsyncClient(verify=False)` scoped to statcan module |
</phase_requirements>

---

## Summary

Phase 7 delivers two independent deliverables: a `datastore` module (6 tools, aiosqlite-backed) and resolution of the StatCan SSL strategy. The two are logically orthogonal and can be implemented in parallel or sequentially.

The datastore module follows the established 5-file module pattern exactly. The only differences from API-backed modules are: no `cached_fetch()` (SQLite is not cached via aiocache), no rate limiter (local I/O, no external API), and a module-level connection singleton that persists for the server's lifetime rather than opening/closing per call.

The SSL investigation for StatCan is a time-boxed probe (30 min max). Because `httpx` already bundles `certifi` and consults it by default, `verify=True` (the default) will either succeed outright or fail. If it fails, a scoped `httpx.AsyncClient(verify=False)` is created exclusively in `modules/statcan/client.py` — never in `shared/http.py`. This is already common practice in the httpx ecosystem and well-understood.

**Primary recommendation:** Use a module-level `_db: aiosqlite.Connection | None = None` singleton initialized lazily on first call to any datastore tool. Enable WAL mode immediately after connecting. This pattern avoids connection overhead per-call while staying within the standard aiosqlite API.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `aiosqlite` | 0.22.1 | Async SQLite access — wraps sqlite3 in a dedicated thread | Only standard async SQLite bridge; zero transitive deps; mirrors stdlib sqlite3 API |
| `sqlite3` | stdlib | Underlying database engine | Built into Python; no install needed |
| `re` | stdlib | Identifier regex allowlist | Sufficient for `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`; no third-party dep |
| `pathlib.Path` | stdlib | `~/.mcp-canada/datastore.db` path resolution + `mkdir(parents=True)` | Already used in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `httpx` | existing | StatCan HTTPS client with scoped SSL | Already in project; `AsyncClient(verify=False)` scoped to statcan module |
| `certifi` | bundled with httpx | CA bundle used by httpx by default | No explicit import needed — httpx uses it automatically via `verify=True` |
| `truststore` | 0.10.4 | System CA store integration | Only add if certifi probe fails AND truststore probe succeeds |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Module-level singleton | Per-call `async with aiosqlite.connect(...)` | Per-call is simpler but adds ~1ms overhead per tool call; singleton is appropriate for a persistent server |
| Regex allowlist | SQLite quote wrapping (`"name"`) | Quote wrapping handles more identifiers but is harder to validate; allowlist is explicit and safe |
| `certifi` default | `truststore` system certs | `truststore` requires `pip install truststore`; try certifi first — if StatCan uses standard DigiCert/Entrust CAs, certifi works fine |

**Installation:**
```bash
# Add to pyproject.toml [project] dependencies
aiosqlite>=0.22.0
# truststore only if certifi fails during SSL probe:
# truststore>=0.10.0
```

---

## Architecture Patterns

### Recommended Project Structure
```
src/mcp_canada/modules/datastore/
├── __init__.py        # MODULE_NAME = "datastore", MODULE_DESCRIPTION
├── constants.py       # DB_PATH, EPHEMERAL_PATH, IDENTIFIER_RE, MAX_QUERY_ROWS
├── schemas.py         # TableSchema, ColumnDef, QueryResult Pydantic models
├── client.py          # _db singleton, get_db(), init_db(), all async DB operations
├── tools.py           # @tool functions: ds_create_table, ds_insert_data, etc.
└── __tests__/
    ├── conftest.py    # in-memory DB fixture, sample schemas
    ├── test_client.py # unit tests for client functions
    └── test_tools.py  # unit tests for @tool functions
```

The StatCan SSL probe lives in a stub file that Phase 8 will fill:
```
src/mcp_canada/modules/statcan/
└── client.py          # _make_client() returns AsyncClient with correct verify= setting
```

### Pattern 1: Module-Level Connection Singleton

**What:** A single `aiosqlite.Connection` held in a module-level variable, initialized lazily on first use, closed on process exit.

**When to use:** Long-lived MCP server processes where multiple tools share a single database. Avoids reconnect cost per tool call. WAL mode makes concurrent reads safe.

**Example:**
```python
# Source: aiosqlite 0.22.1 official API + project conventions
import aiosqlite
from pathlib import Path

_db: aiosqlite.Connection | None = None

async def get_db(db_path: Path | str = ":memory:") -> aiosqlite.Connection:
    """Return the shared DB connection, initializing it on first call."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(str(db_path))
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
        await _db.commit()
        _db.row_factory = aiosqlite.Row  # dict-like row access
    return _db

async def close_db() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None
```

Key points:
- `aiosqlite.connect()` returns a `Connection` that wraps sqlite3 in a single background thread — it does NOT block the asyncio event loop
- WAL mode: set once after connect; it persists on disk across reconnects
- `row_factory = aiosqlite.Row` enables `row["column_name"]` access

### Pattern 2: Identifier Validation Guard

**What:** Every function that accepts a table or column name from agent input calls `_validate_identifier()` before building any SQL string.

**When to use:** Before ANY string interpolation of agent-supplied names into SQL.

**Example:**
```python
import re

_IDENTIFIER_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$')

def _validate_identifier(name: str) -> None:
    """Raise ValueError if name contains SQL metacharacters.

    Args:
        name: Table or column name supplied by agent.

    Raises:
        ValueError: If name does not match allowlist pattern.
    """
    if not _IDENTIFIER_RE.fullmatch(name):
        raise ValueError(
            f"Invalid identifier '{name}'. "
            "Names must match ^[a-zA-Z_][a-zA-Z0-9_]{0,63}$"
        )
```

Call site in tools.py:
```python
try:
    _validate_identifier(table_name)
except ValueError as exc:
    return make_error("INVALID_INPUT", str(exc), lang=lang)
```

### Pattern 3: Type Inference from Python Values

**What:** When `schema` is not provided, infer SQLite column types from the first row of data.

**When to use:** `ds_create_table` and `ds_insert_data` when the agent does not supply explicit types.

**Example:**
```python
def _infer_sqlite_type(value: object) -> str:
    """Infer SQLite affinity from a Python value."""
    if isinstance(value, bool):
        return "INTEGER"  # bool is subclass of int — check first
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"  # str, None, datetime, etc. → TEXT
```

Rule: bool must be checked before int because `isinstance(True, int)` is `True`.

### Pattern 4: Ephemeral Flag and Connection Path

**What:** `--ephemeral` on the top-level parser switches the DB path from `~/.mcp-canada/datastore.db` to `":memory:"`.

**When to use:** Testing, demo environments, or when no persistence is needed.

**Example (server.py addition):**
```python
parser.add_argument(
    "--ephemeral",
    action="store_true",
    default=False,
    help="Use in-memory SQLite (no persistence, lost on exit)",
)
```

The datastore client reads `_config["ephemeral"]` from `server._config`:
```python
from mcp_canada import server as _server

def _db_path() -> str:
    if _server._config.get("ephemeral"):
        return ":memory:"
    path = Path.home() / ".mcp-canada" / "datastore.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)
```

### Pattern 5: ds_query Row Limit Enforcement

**What:** Apply a 1000-row cap if the agent's SQL has no explicit LIMIT clause; use `fetchmany()` to avoid loading all rows into memory.

**When to use:** `ds_query` tool — every SELECT/PRAGMA/EXPLAIN response.

**Example:**
```python
_QUERY_LIMIT = 1000
_ALLOWED_PREFIXES = ("SELECT", "PRAGMA", "EXPLAIN", "CREATE INDEX")

async def run_query(sql: str) -> list[dict]:
    sql_upper = sql.strip().upper()
    if not any(sql_upper.startswith(p) for p in _ALLOWED_PREFIXES):
        raise ValueError("Only SELECT, PRAGMA, EXPLAIN, CREATE INDEX are allowed.")

    db = await get_db()
    async with db.execute(sql) as cursor:
        rows = await cursor.fetchmany(_QUERY_LIMIT)
        columns = [d[0] for d in cursor.description or []]
    return [dict(zip(columns, row)) for row in rows]
```

### Pattern 6: SSL Strategy for StatCan

**What:** Probe `httpx.AsyncClient(verify=True)` against a known StatCan endpoint first. If it raises `ssl.SSLCertVerificationError`, fall back to `verify=False` scoped to the statcan client only.

**When to use:** One-time probe during Phase 7 to determine the value of `_STATCAN_VERIFY` constant.

**Example (constants.py):**
```python
# Set during Phase 7 SSL probe. True if certifi validates statcan.gc.ca.
STATCAN_VERIFY: bool | str = True  # or False after probe
```

**Example (client.py stub for Phase 7, to be filled in Phase 8):**
```python
import httpx

def _make_statcan_client() -> httpx.AsyncClient:
    """Create an httpx client scoped to StatCan with correct SSL setting.

    verify=True uses certifi (httpx default).
    verify=False is scoped to this client only — never affects shared clients.
    """
    return httpx.AsyncClient(
        verify=STATCAN_VERIFY,
        timeout=httpx.Timeout(30.0),
        headers={"User-Agent": f"mcp-canada/{__version__}"},
    )
```

### Anti-Patterns to Avoid

- **Opening a connection per tool call:** `async with aiosqlite.connect(...) as db:` inside each tool call adds latency and prevents WAL mode from being reused. Use the singleton.
- **String-interpolating agent input directly into SQL:** `f"SELECT * FROM {table}"` without calling `_validate_identifier(table)` first is an injection vector even for SQLite.
- **Setting `verify=False` on the shared lifespan client:** This would disable SSL verification globally for all modules. StatCan's `verify=False` must stay inside `modules/statcan/client.py`.
- **Using `fetchall()` for unbounded queries:** Memory risk if a table has millions of rows. Use `fetchmany(1000)`.
- **`db.row_factory = aiosqlite.Row` after first query:** Row factory must be set before any queries run. Set it immediately after connecting in `get_db()`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async SQLite | `asyncio.to_thread(sqlite3.connect(...))` | `aiosqlite` | aiosqlite's thread model is optimized, tested, and handles cursor lifecycle correctly |
| Identifier escaping | Manual quote-wrapping logic | Regex allowlist + rejection | Allowlist is simpler and more auditable than escaping edge cases |
| Row limit | Post-query slice `rows[:1000]` | `cursor.fetchmany(1000)` | fetchmany avoids loading all rows from the cursor before slicing |
| SSL probe | Custom SSL socket handshake | `httpx.AsyncClient(verify=True)` with exception catch | httpx already wraps ssl module correctly |

**Key insight:** The SQLite identifier problem is genuinely harder than it looks. SQLite allows nearly anything inside double-quotes, but agent-supplied names may include semicolons, line breaks, or comment sequences. The regex allowlist (`^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`) is a clean rejection gate — no escaping required.

---

## Common Pitfalls

### Pitfall 1: bool Subclasses int in Python

**What goes wrong:** `_infer_sqlite_type(True)` returns `"INTEGER"` which is correct, but if you check `isinstance(value, int)` before `isinstance(value, bool)`, booleans are stored correctly but might confuse downstream code expecting 0/1.

**Why it happens:** `bool` is a subclass of `int` in Python.

**How to avoid:** Always check `isinstance(value, bool)` before `isinstance(value, int)` in type inference.

**Warning signs:** Boolean columns storing 0/1 when you expected True/False in the data dict.

### Pitfall 2: WAL Mode Not Persisting

**What goes wrong:** WAL mode is set but lost after reconnect.

**Why it happens:** Actually it does persist — WAL mode is stored in the database file header. This is a non-issue.

**How to avoid:** Still set it on connect anyway (`PRAGMA journal_mode=WAL`) as a safety net for freshly created files. It is idempotent.

### Pitfall 3: aiosqlite Row Factory Scope

**What goes wrong:** `cursor.row_factory = aiosqlite.Row` set on the cursor after `db.execute()` returns. Row objects from `fetchall()` are still tuples.

**Why it happens:** Row factory applies to future rows, not rows already fetched. Also, `db.row_factory` must be set on the connection, not the cursor.

**How to avoid:** Set `db.row_factory = aiosqlite.Row` immediately after `await aiosqlite.connect(...)`, before any query.

### Pitfall 4: sqlite_master vs sqlite_schema

**What goes wrong:** `SELECT name FROM sqlite_schema WHERE type='table'` fails on older SQLite versions.

**Why it happens:** `sqlite_schema` was added in SQLite 3.33.0 (2020). `sqlite_master` is the older, universally supported alias.

**How to avoid:** Use `sqlite_master` — it works on all Python sqlite3 versions (Python 3.12 bundles SQLite 3.39+, but `sqlite_master` is always available as an alias).

### Pitfall 5: `--ephemeral` and Singleton State

**What goes wrong:** Server is restarted mid-test without `--ephemeral`, and the singleton still holds the old file-backed connection from the previous instance.

**Why it happens:** Module-level `_db` persists across the process lifetime, but not across process restarts (file connections are OS-level).

**How to avoid:** On process start, `_db` is always `None`. The first call to `get_db()` reads the current `_config["ephemeral"]` state. No issue.

**Warning signs:** Tests that rely on a clean database state should pass `:memory:` explicitly or reset `_db = None` in teardown.

### Pitfall 6: ds_query Keyword Check is Case-Sensitive

**What goes wrong:** Agent sends `select * from foo` (lowercase) and the keyword check rejects it.

**Why it happens:** `sql.startswith("SELECT")` fails on lowercase.

**How to avoid:** Always normalize with `.strip().upper()` before the prefix check.

### Pitfall 7: certifi and statcan.gc.ca

**What goes wrong:** certifi's bundle does not include the Entrust CA used by statcan.gc.ca, so `verify=True` (default) raises `ssl.SSLCertVerificationError`.

**Why it happens:** Government sites sometimes use intermediate CAs not in standard bundles. This is a known issue with Government of Canada HTTPS endpoints.

**How to avoid:** The SSL probe protocol resolves this empirically. If certifi fails, the statcan client is initialized with `verify=False`. This is scoped — no global impact.

**Warning signs:** `httpx.ConnectError` or `ssl.SSLCertVerificationError` in the probe test.

---

## Code Examples

Verified patterns from official sources and project conventions:

### Connect with WAL Mode (aiosqlite 0.22.1)
```python
# Source: aiosqlite PyPI / omnilib/aiosqlite GitHub
import aiosqlite

async def connect_with_wal(path: str) -> aiosqlite.Connection:
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    await db.commit()
    return db
```

### Create Table with Validated Identifiers
```python
async def create_table(
    db: aiosqlite.Connection,
    table: str,
    columns: list[tuple[str, str]],  # [(name, type), ...]
) -> None:
    _validate_identifier(table)
    for col_name, _ in columns:
        _validate_identifier(col_name)
    col_defs = ", ".join(f"{name} {affinity}" for name, affinity in columns)
    await db.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})")
    await db.commit()
```

### Insert Many Rows
```python
# Source: aiosqlite smoke tests + executemany API
async def insert_rows(
    db: aiosqlite.Connection,
    table: str,
    rows: list[dict[str, object]],
) -> int:
    _validate_identifier(table)
    if not rows:
        return 0
    columns = list(rows[0].keys())
    for col in columns:
        _validate_identifier(col)
    placeholders = ", ".join("?" * len(columns))
    col_list = ", ".join(columns)
    data = [tuple(row[c] for c in columns) for row in rows]
    await db.executemany(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
        data,
    )
    await db.commit()
    return len(data)
```

### Read-Only Query with Row Limit
```python
# Source: aiosqlite official API
async def run_query(db: aiosqlite.Connection, sql: str) -> list[dict]:
    sql_upper = sql.strip().upper()
    allowed = ("SELECT", "PRAGMA", "EXPLAIN", "CREATE INDEX")
    if not any(sql_upper.startswith(p) for p in allowed):
        raise ValueError(f"Query must start with one of: {allowed}")
    async with db.execute(sql) as cursor:
        rows = await cursor.fetchmany(1000)
        cols = [d[0] for d in cursor.description or []]
    return [dict(zip(cols, row)) for row in rows]
```

### List Tables
```python
async def list_tables(db: aiosqlite.Connection) -> list[str]:
    async with db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ) as cursor:
        rows = await cursor.fetchall()
    return [row["name"] for row in rows]
```

### Table Schema via PRAGMA
```python
async def get_schema(db: aiosqlite.Connection, table: str) -> list[dict]:
    _validate_identifier(table)
    async with db.execute(f"PRAGMA table_info({table})") as cursor:
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]
# PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
```

### Drop Table
```python
async def drop_table(db: aiosqlite.Connection, table: str) -> None:
    _validate_identifier(table)
    await db.execute(f"DROP TABLE IF EXISTS {table}")
    await db.commit()
```

### StatCan SSL Probe (INF-01)
```python
# Source: httpx official SSL docs + project conventions
import httpx
import ssl

STATCAN_PROBE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401"

async def probe_statcan_ssl() -> bool:
    """Return True if certifi validates statcan.gc.ca, False otherwise."""
    try:
        async with httpx.AsyncClient(verify=True, timeout=10.0) as client:
            r = await client.get(STATCAN_PROBE_URL)
            r.raise_for_status()
        return True
    except (ssl.SSLCertVerificationError, httpx.ConnectError):
        return False
```

### Scoped StatCan Client (verify=False fallback)
```python
# Source: httpx SSL docs — verify= is set at client instantiation, not per-request
def _make_statcan_client(verify: bool = True) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        verify=verify,
        timeout=httpx.Timeout(30.0),
        headers={"User-Agent": f"mcp-canada/{__version__}"},
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `asyncio.to_thread(sqlite3.connect(...))` | `aiosqlite.connect(...)` directly | aiosqlite 0.17+ | Cleaner API, proper connection lifecycle |
| `sqlite_schema` (newer alias) | `sqlite_master` (stable) | SQLite 3.33.0 (2020) | `sqlite_master` is the safer universal choice |
| Per-request `async with aiosqlite.connect(...)` | Module-level singleton | Community best practice | Avoids reconnect overhead for long-lived servers |
| `requests` + `verify=False` globally | `httpx.AsyncClient(verify=False)` scoped | httpx era | SSL bypass is now scoped to one client instance |

**Deprecated/outdated:**
- `aiosqlite.Row` accessed as tuple: still works but use `row["col"]` for clarity
- `cursor.description` may be `None` for DDL statements (CREATE, DROP) — guard with `or []`

---

## Open Questions

1. **SSL outcome for statcan.gc.ca**
   - What we know: httpx uses certifi by default; Government of Canada uses Entrust/DigiCert CAs; certifi 2024+ includes major government CAs
   - What's unclear: Whether statcan.gc.ca specifically validates with the certifi bundle in the CI environment
   - Recommendation: Run the 5-line SSL probe script during Wave 1 of Phase 7 execution. Record the result in `modules/statcan/constants.py` as `STATCAN_VERIFY: bool = True/False`. If outcome is `False`, document the reason in a code comment.

2. **Ephemeral flag and test isolation**
   - What we know: Module-level `_db` singleton is process-scoped; in-memory `:memory:` is connection-scoped
   - What's unclear: Whether unit tests for the datastore module need to reset `_db = None` between tests or use a fresh path each time
   - Recommendation: In `conftest.py`, create an `async def db_fixture()` that directly calls `aiosqlite.connect(":memory:")` and patches `client._db` — avoids touching `_config` at all in unit tests.

3. **`_config` coupling in datastore client**
   - What we know: `server._config` is a module-level dict set in `main()`; other modules do not import from `server`
   - What's unclear: Whether importing from `server` in `client.py` creates a circular import
   - Recommendation: Pass the DB path at module import time using an env var or a dedicated `configure(db_path: str)` function called from `server.py` after args are parsed. This avoids any circular import risk.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio 0.23+ |
| Config file | `pyproject.toml` (`asyncio_mode = "auto"`) |
| Quick run command | `uv run pytest src/mcp_canada/modules/datastore/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DS-01 | `ds_create_table` creates table, returns make_response | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsCreateTable -x` | ❌ Wave 0 |
| DS-02 | `ds_insert_data` inserts rows, returns row count | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsInsertData -x` | ❌ Wave 0 |
| DS-03 | `ds_query` returns SELECT results, enforces 1000-row cap | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsQuery -x` | ❌ Wave 0 |
| DS-04 | `ds_list_tables` returns table names | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsListTables -x` | ❌ Wave 0 |
| DS-05 | `ds_get_schema` returns column definitions | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsGetSchema -x` | ❌ Wave 0 |
| DS-06 | `ds_drop_table` drops table immediately | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py::TestDsDropTable -x` | ❌ Wave 0 |
| DS-07 | Identifier with semicolon returns INVALID_INPUT error | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_client.py::TestValidateIdentifier -x` | ❌ Wave 0 |
| DS-08 | All ops are async (no `asyncio.to_thread` or `run_in_executor`) | unit (code inspection) | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_client.py -x` | ❌ Wave 0 |
| INF-01 | SSL probe runs without error; result captured in constants.py | smoke (manual) | `uv run python -c "import asyncio; from mcp_canada.modules.statcan.client import probe_statcan_ssl; print(asyncio.run(probe_statcan_ssl()))"` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/datastore/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/datastore/__tests__/conftest.py` — in-memory DB fixture, `_db` patch
- [ ] `src/mcp_canada/modules/datastore/__tests__/test_client.py` — covers DS-07, DS-08
- [ ] `src/mcp_canada/modules/datastore/__tests__/test_tools.py` — covers DS-01 through DS-06
- [ ] `tests/integration/test_tool_scenarios.py` additions — `TestDatastoreScenarios` class
- [ ] Framework already installed: `pytest`, `pytest-asyncio` in dev deps

---

## Sources

### Primary (HIGH confidence)
- [aiosqlite 0.22.1 PyPI page](https://pypi.org/project/aiosqlite/) — version, API, executemany, row_factory, connection lifecycle
- [aiosqlite smoke tests (GitHub)](https://github.com/omnilib/aiosqlite/blob/main/aiosqlite/tests/smoke.py) — executemany, row_factory, async iteration
- [httpx SSL documentation](https://www.python-httpx.org/advanced/ssl/) — `verify=False` scoping, certifi default, AsyncClient instantiation
- Existing project code — module pattern, envelope, test structure, server.py argparse shape

### Secondary (MEDIUM confidence)
- [truststore PyPI](https://pypi.org/project/truststore/) — 0.10.4, httpx integration via `ssl.SSLContext`; truststore is a fallback-only dep per locked decisions
- [SQLite WAL documentation](https://www.sqlite.org/wal.html) — WAL mode persistence, concurrent read/write semantics
- [SQLite PRAGMA documentation](https://sqlite.org/pragma.html) — `table_info`, `journal_mode`, `foreign_keys`
- [SQLite Datatypes](https://www.sqlite.org/datatype3.html) — TEXT/REAL/INTEGER affinity rules

### Tertiary (LOW confidence)
- None — all claims verified against official sources.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — aiosqlite 0.22.1 confirmed on PyPI; httpx SSL behavior confirmed on official docs
- Architecture: HIGH — patterns derived directly from aiosqlite official API and existing project conventions
- Pitfalls: HIGH — identifier injection, bool/int subclass, WAL mode — all verified against SQLite/Python official docs
- SSL probe outcome: LOW — empirical; outcome unknown until live endpoint test against statcan.gc.ca

**Research date:** 2026-04-07
**Valid until:** 2026-05-07 (aiosqlite is stable; httpx SSL API is stable; SSL probe outcome may change if StatCan updates their cert chain)
