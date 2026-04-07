# Architecture Patterns: statcan + datastore Modules

**Domain:** MCP server module integration (Statistics Canada API + SQLite datastore)
**Researched:** 2026-04-07
**Confidence:** HIGH — based on direct inspection of existing module source, WDS/SDMX official docs, and mcp-statcan reference implementation

---

## Recommended Architecture

Two new modules integrate into the existing FileSystemProvider auto-discovery system. Neither requires changes to `server.py`, `shared/`, or any existing module. Both follow the mandatory 5-file pattern.

```
src/mcp_canada/modules/
├── datastore/          ← new: SQLite tools (no upstream API)
│   ├── __init__.py
│   ├── constants.py    ← DB_PATH, DEFAULT_DB_NAME
│   ├── schemas.py      ← TableRow, QueryResult, SchemaInfo (flat Pydantic)
│   ├── client.py       ← sync sqlite3 wrapped in asyncio.to_thread()
│   ├── tools.py        ← ds_* tools
│   └── __tests__/
└── statcan/            ← new: WDS REST + SDMX tools
    ├── __init__.py
    ├── constants.py    ← WDS_BASE_URL, SDMX_BASE_URL, RATE_GROUP, CACHE_TTLs
    ├── schemas.py      ← CubeInfo, VectorRow, SeriesInfo, CodeSet (flat)
    ├── client.py       ← WDS + SDMX clients, SSL handling, rate limit, cache
    ├── tools.py        ← statcan_* tools (WDS, SDMX, composite)
    └── __tests__/
```

---

## Component Boundaries

### Component 1: `datastore` module

**Responsibility:** Generic SQLite CRUD operations. Completely API-agnostic — knows nothing about StatCan, BoC, or any upstream data source. Any module can call its client functions to persist data locally.

**Boundary:** The datastore module owns the SQLite connection lifecycle, schema management, and SQL execution. It does NOT know what data it stores — callers control table names and schemas.

**Key constraint:** No new dependency. Use `sqlite3` (stdlib) wrapped in `asyncio.to_thread()` for non-blocking behavior. Do NOT add `aiosqlite` as a dependency — the existing stack is sufficient.

```python
# client.py pattern for async-safe sqlite3 without new deps
import asyncio, sqlite3

async def execute_query(db_path: str, sql: str, params: tuple = ()) -> list[dict]:
    def _sync():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    return await asyncio.to_thread(_sync)
```

**DB file location:** `~/.mcp-canada/datastore.db` (resolved via `constants.py`, not hardcoded in tools). Configurable via environment variable `MCP_CANADA_DB_PATH`.

**Tools (ds_ prefix):**
- `ds_create_table` — DDL creation with caller-specified column definitions
- `ds_insert_rows` — bulk insert (list of dicts), create table if not exists
- `ds_query` — read-only SQL (enforce with `PRAGMA query_only = ON`)
- `ds_list_tables` — enumerate all user tables (exclude sqlite_* system tables)
- `ds_schema` — inspect columns, types for a named table
- `ds_drop_table` — remove table by name

**Does NOT use:** `cached_fetch`, `get_limiter`, `api_get` — these are API patterns. The datastore has no upstream, no rate limit, and no TTL.

**Does use:** `make_response`, `make_error` (envelope consistency), `lang` parameter (bilingual errors).

---

### Component 2: `statcan` module

**Responsibility:** Statistics Canada API access via both WDS REST and SDMX REST APIs. Follows the identical client/tools pattern as existing modules.

**Two API surfaces to wrap:**

| API | Base URL | Format | Best For |
|-----|----------|--------|----------|
| WDS REST | `https://www150.statcan.gc.ca/t1/wds/rest/` | JSON | Cube discovery, metadata, vector resolution, code sets |
| SDMX REST | `https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/` | JSON (via Accept header) | Server-side filtered data queries — fewer API roundtrips for large datasets |

**Tools (statcan_ prefix):**

WDS Discovery:
- `statcan_search_cubes` — search cubes by title keyword
- `statcan_get_cube_metadata` — dimensions, members, date ranges for a productId
- `statcan_get_code_sets` — decode numeric frequency/unit/status codes
- `statcan_get_changed_cubes` — tables updated on a given date

WDS Series/Vector:
- `statcan_get_series_info` — productId + coordinate → vectorId
- `statcan_get_vector_data` — fetch N latest observations from one or more vectorIds
- `statcan_get_series_by_range` — observations for vectorId within date range

SDMX (server-side filtered):
- `statcan_sdmx_structure` — get dimension codelists and key syntax for a dataflow
- `statcan_sdmx_data` — filtered observations with period/key constraints

Composite (statcan + datastore):
- `statcan_fetch_vectors_to_store` — fetch multiple vectors and write to datastore in one call

**SSL handling boundary:** SSL concerns are contained within `statcan/client.py` only. Do not touch `shared/http.py`. The statcan client creates its own `httpx.AsyncClient` with either (a) certifi bundle or (b) scoped `verify=False` if cert bundling fails at startup — determined by a single constant in `constants.py`.

**SDMX JSON vs XML:** Request JSON via `Accept: application/vnd.sdmx.data+json` header. Parse with stdlib `json`. Do not introduce an SDMX parsing library.

---

### Component 3: `shared/` utilities (unchanged)

All existing shared utilities remain unchanged. The `statcan` module uses `cached_fetch`, `get_limiter`, and `make_response`/`make_error` in the same way as existing modules. The `datastore` module uses only `make_response` and `make_error`.

| Utility | Used by statcan | Used by datastore |
|---------|----------------|-------------------|
| `cache.py` cached_fetch | Yes (WDS + SDMX responses) | No (local I/O, no TTL needed) |
| `rate_limiter.py` get_limiter | Yes (RATE_GROUP = "statcan") | No |
| `http.py` api_get | No (custom SSL client needed) | No |
| `envelope.py` make_response/make_error | Yes | Yes |
| `i18n.py` t() | Yes (bilingual errors) | Yes (bilingual errors) |

---

## Data Flow

### Flow 1: Standard StatCan API query (WDS or SDMX)

```
Agent
  → discover_tools / call_tool  (BM25SearchTransform layer)
  → statcan_get_vector_data(vectorIds=[...], n=10, lang="en")
      → statcan/tools.py @tool function
      → statcan/client.py fetch_vector_data()
          → shared/rate_limiter.py get_limiter("statcan")
          → shared/cache.py cached_fetch(key, ttl=3600, fetcher)
              → httpx.AsyncClient (SSL: certifi or scoped verify=False)
              → WDS REST POST /getDataFromVectorsAndLatestNPeriods
              → (flatten, validate via Pydantic, sort newest-first)
          → (data, was_cached)
      → shared/envelope.py make_response(data, api_name="statcan-wds", ...)
  → {"_meta": {...}, "data": [...]}  back to agent
```

### Flow 2: Composite fetch-and-store (cross-module)

```
Agent
  → statcan_fetch_vectors_to_store(vectorIds=[...], table="gdp_series", n=20)
      → statcan/tools.py composite @tool function
      → statcan/client.py fetch_vector_data(vectorIds, n=20)
          → [WDS API call as in Flow 1]
          → returns list[VectorRow]
      → datastore/client.py insert_rows(table="gdp_series", rows=vector_rows_as_dicts)
          → asyncio.to_thread(sqlite3 INSERT OR REPLACE ...)
      → make_response({
            "rows_written": N,
            "table": "gdp_series",
            "source_api": "statcan-wds",
            "cached": False
        }, api_name="statcan-wds", ...)
```

**Key architectural decision:** The composite tool lives in `statcan/tools.py`, not in `datastore/`. The statcan module imports from datastore's client — the dependency is one-directional: statcan → datastore. The datastore never imports from statcan.

### Flow 3: Cross-module SQL query (agent-driven)

```
Agent (multi-step conversation)
  Step 1: statcan_fetch_vectors_to_store(vectorIds=[V1, V2], table="gdp")
  Step 2: boc_get_exchange_rates(currency="USD")
          → agent writes result to datastore manually via ds_insert_rows
  Step 3: ds_query("SELECT g.ref_period, g.value as gdp, e.value as usd_cad
                    FROM gdp g JOIN exchange_rates e ON g.ref_period = e.date")
          → datastore/tools.py @tool function
          → datastore/client.py execute_query(...)
          → make_response(rows, api_name="datastore-sqlite", api_url="local://datastore")
```

This is the core value: the agent orchestrates — it calls statcan tools to fetch, datastore tools to store other sources' data, then ds_query to join across sources. No module needs special cross-module awareness.

---

## Module Interaction Rules

1. **statcan → datastore (allowed, one-way):** Composite tools in `statcan/tools.py` may call `datastore/client.py` functions directly. This is the only cross-module import.

2. **datastore → statcan (forbidden):** The datastore must remain domain-agnostic. It cannot import from statcan.

3. **existing modules → datastore (allowed, future):** Any module's tools could call `datastore/client.py` to persist fetched data. v1.1 does not require this — the PROJECT.md explicitly scopes this out.

4. **shared/ → modules (forbidden):** Shared utilities never import from modules.

---

## Build Order

**Build datastore first, statcan second.**

Rationale:
- `statcan` composite tools (`statcan_fetch_vectors_to_store`) import from `datastore/client.py`. If built in parallel, composite tools cannot be tested end-to-end until datastore exists.
- `datastore` has no external API dependency — it can reach green (tests passing) entirely with stdlib, no network mocks needed. Faster feedback loop, no blocking on SSL investigation.
- SSL investigation for statcan can proceed while datastore is being built, resolving the cert approach before any statcan client code is written.

**Recommended phase sequence:**

| Phase | Work | Depends On |
|-------|------|-----------|
| 1 | `datastore` module: all 6 tools + full test coverage | nothing |
| 2 | StatCan SSL investigation + `statcan/constants.py` + cert strategy decision | nothing (parallel with phase 1) |
| 3 | `statcan/client.py` WDS tools (no composite) + `statcan/tools.py` WDS tools | datastore (complete), SSL decision |
| 4 | `statcan/client.py` SDMX + `statcan/tools.py` SDMX tools | phase 3 |
| 5 | Composite tools (`statcan_fetch_vectors_to_store`) | phases 1, 3 |
| 6 | Integration tests + README | phases 3, 4, 5 |

Phases 1 and 2 can run in parallel. Phase 3 blocks on both completing.

---

## Cache Strategy for statcan

StatCan WDS serves 80,000+ tables. Cache TTLs must be aggressive for catalogue endpoints:

| Endpoint | TTL | Rationale |
|----------|-----|-----------|
| getAllCubesListLite | 24h (86400s) | Catalogue rarely changes intra-day |
| getCubeMetadata | 24h (86400s) | Dimension structure is stable |
| getCodeSets | 7 days (604800s) | Code definitions are near-static |
| getDataFromVectors | 1h (3600s) | Data releases are daily |
| getChangedCubeList | 15min (900s) | Change detection should be fresher |
| SDMX structure | 24h (86400s) | Same as WDS metadata |
| SDMX data | 1h (3600s) | Same as WDS observations |

---

## Rate Limiting for statcan

StatCan WDS has no documented rate limit, but the cube list endpoint (`getAllCubesList`) returns a large payload (~1MB) and should not be hammered. Use conservative defaults:

```python
RATE_GROUP = "statcan-wds"
RATE_LIMIT = 5.0   # requests/second — conservative, matches mcp-statcan reference
```

Use a separate rate group for SDMX:

```python
SDMX_RATE_GROUP = "statcan-sdmx"
SDMX_RATE_LIMIT = 5.0
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Composite tool in datastore module

**What:** Putting `statcan_fetch_vectors_to_store` in `datastore/tools.py` so it "lives near the storage logic."
**Why bad:** Creates a circular or bidirectional dependency. Datastore imports statcan's client. Datastore is no longer domain-agnostic. Future modules cannot use it cleanly.
**Instead:** Composite tool lives in `statcan/tools.py`. The statcan module owns "fetch + store" as a workflow.

### Anti-Pattern 2: Shared SQLite connection at module level

**What:** Opening a single `sqlite3.connect()` at module import time and sharing it across all calls.
**Why bad:** sqlite3 connections are not thread-safe. `asyncio.to_thread` dispatches to a thread pool — concurrent requests will corrupt the connection state.
**Instead:** Open, use, and close a connection inside each `asyncio.to_thread` call. Use `check_same_thread=False` if connection must be shared, but per-call connections are simpler and safer at this scale.

### Anti-Pattern 3: Disabling SSL globally

**What:** Setting `httpx.AsyncClient(verify=False)` in `shared/http.py` or at server initialization.
**Why bad:** Disables SSL verification for ALL modules, not just StatCan. BoC, Parliament, Drug Database, etc. would all lose certificate validation.
**Instead:** The statcan client creates its own `httpx.AsyncClient` with SSL handling scoped to that module only.

### Anti-Pattern 4: Storing nested API responses in SQLite

**What:** Inserting raw WDS JSON blobs (`{"vectorId": 123, "object": {...}}`) into the datastore without flattening.
**Why bad:** Agents querying via SQL cannot use JSON blob columns meaningfully. Wastes storage.
**Instead:** Flatten before insert (same rule as Pydantic schemas). `statcan_fetch_vectors_to_store` transforms `VectorRow` objects to flat dicts before calling `datastore/client.py`.

### Anti-Pattern 5: Adding the datastore to the BM25 tool-discovery flow as "internal only"

**What:** Hiding ds_* tools or marking them non-discoverable because they're "infrastructure."
**Why bad:** Agents need to discover and call `ds_query` to realize the cross-module SQL value. If the tools aren't discoverable, the core value proposition of the datastore is inaccessible.
**Instead:** All ds_* tools have full `Keywords:` and `Use for:` docstrings. Agents discover them normally via `discover_tools`.

---

## Scalability Considerations

The datastore and statcan modules are designed for single-user local MCP usage (stdio transport). Neither needs horizontal scaling provisions.

| Concern | At 1 user | Notes |
|---------|-----------|-------|
| SQLite concurrency | Not relevant | MCP stdio is single-process, single-agent |
| StatCan API rate | 5 req/s sufficient | No evidence of stricter limits |
| Cache memory | aiocache SimpleMemoryCache — fine for 80K cube catalogue | Restart clears cache |
| DB file size | ~10MB for typical agent sessions | Agents drop tables when done |

---

## Sources

- WDS REST API endpoints: [Statistics Canada Web Data Service User Guide](https://www.statcan.gc.ca/en/developers/wds/user-guide) — HIGH confidence (official)
- SDMX REST API: [Statistics Canada SDMX User Guide](https://www.statcan.gc.ca/en/developers/sdmx/user-guide) — HIGH confidence (official)
- Reference implementation: [mcp-statcan by Aryan Jhaveri](https://github.com/Aryan-Jhaveri/mcp-statcan) — MEDIUM confidence (inspected, used as design reference only — not a dependency)
- httpx SSL options: [httpx SSL documentation](https://www.python-httpx.org/advanced/ssl/) — HIGH confidence (official)
- asyncio.to_thread for sqlite3: Python stdlib docs — HIGH confidence (stdlib)
- aiosqlite (not adopted): [aiosqlite PyPI](https://pypi.org/project/aiosqlite/) — researched, ruled out due to no-new-dependencies constraint
- Existing module patterns: direct source inspection of `bank_of_canada/`, `shared/` — HIGH confidence
