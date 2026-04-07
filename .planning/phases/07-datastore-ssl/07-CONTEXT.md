# Phase 7: Datastore + SSL - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Shared SQLite persistence layer (datastore module) that any mcp-canada module can write to, plus the StatCan SSL certificate strategy. This phase delivers the `datastore` module with 6 tools and resolves how the statcan module will handle HTTPS. No StatCan API tools are built in this phase.

</domain>

<decisions>
## Implementation Decisions

### Database location & lifecycle
- Database file lives at `~/.mcp-canada/datastore.db` (global, user-level)
- Data persists across server restarts by default
- Configurable: `--ephemeral` flag for in-memory mode (no disk writes)
- Auto-created on first use — first `ds_create_table` call creates file + parent dirs
- WAL mode enabled on connection for concurrent read/write support

### Query safety boundaries
- `ds_query` allows: SELECT, PRAGMA, EXPLAIN, CREATE INDEX
- Default row limit: 1000 rows (agent can override with explicit LIMIT clause)
- All writes go through `ds_insert_data` and `ds_create_table` tools — no raw INSERT/UPDATE/DELETE in ds_query
- `ds_drop_table` executes immediately — no confirmation flag (data is re-fetchable from APIs)
- SQL injection prevention via regex allowlist on table/column identifiers: `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`

### Table naming & schema
- Module prefix convention for auto-stored data: `statcan_cpi_monthly`, `boc_exchange_rates`
- Column type inference from first row by default (TEXT, REAL, INTEGER)
- Optional explicit schema parameter for precise control — both modes supported
- Duplicate handling: simple INSERT (append all). Agent checks for duplicates via ds_query if needed

### SSL investigation
- Quick test only — 30 min max effort
- Try certifi first (already bundled with httpx) — no new dependency if it works
- If certifi fails, fall back to scoped `verify=False` on statcan httpx client only
- Never touch `shared/http.py` or the lifespan shared client
- Do NOT add truststore as a dependency unless certifi fails AND truststore succeeds

### Claude's Discretion
- Exact aiosqlite connection management pattern (singleton vs per-call)
- SQLite PRAGMA settings beyond WAL mode
- How to surface the --ephemeral flag in argparse (likely on the main parser, not subcommand)
- Error message wording for SQL injection rejections

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/envelope.py`: `make_response()` / `make_error()` — datastore tools use the same envelope pattern
- `shared/http.py`: `api_get()` with retry — statcan will NOT use this (needs its own client for SSL scoping), but the retry pattern (tenacity) is reusable
- `shared/rate_limiter.py`: `get_limiter()` — statcan Phase 8 will use this; not needed in Phase 7

### Established Patterns
- 5-file module pattern: `__init__.py`, `constants.py`, `schemas.py`, `client.py`, `tools.py`
- All tools use standalone `@tool` decorator from `fastmcp.tools`
- All tools accept `lang: Literal["en", "fr"]` parameter
- Client functions return `(data, was_cached)` tuples — datastore client may return `(data, False)` since SQLite isn't cached
- Tool docstrings require `Use for:` and `Keywords:` lines for BM25 discovery

### Integration Points
- `server.py` `_build_parser()` — needs `--ephemeral` flag added to top-level parser
- `pyproject.toml` — needs `aiosqlite>=0.22.0` added to dependencies
- Module auto-discovery via FileSystemProvider — new `modules/datastore/` dir auto-registers

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. The datastore should feel like a natural extension of the existing module system.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-datastore-ssl*
*Context gathered: 2026-04-07*
