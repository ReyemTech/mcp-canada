---
phase: 07-datastore-ssl
plan: 01
subsystem: database
tags: [aiosqlite, sqlite, async, tdd, identifier-validation, singleton]

# Dependency graph
requires: []
provides:
  - Async SQLite singleton client with WAL mode and identifier validation
  - datastore module skeleton (constants, schemas, client)
  - aiosqlite dependency in pyproject.toml
  - --ephemeral server flag for in-memory mode
  - 47 unit tests covering all CRUD operations and validation
affects: [07-02, 08-statcan, 09-statcan-tools]

# Tech tracking
tech-stack:
  added: [aiosqlite>=0.22.0]
  patterns:
    - "Module-level async singleton: global _db variable, get_db() lazy init"
    - "Identifier validation via regex allowlist before any SQL executes"
    - "All public client functions return (data, False) tuples — was_cached always False for local I/O"
    - "TDD red-green-refactor: 47 failing tests written first, then full implementation"

key-files:
  created:
    - src/mcp_canada/modules/datastore/__init__.py
    - src/mcp_canada/modules/datastore/constants.py
    - src/mcp_canada/modules/datastore/schemas.py
    - src/mcp_canada/modules/datastore/client.py
    - src/mcp_canada/modules/datastore/__tests__/__init__.py
    - src/mcp_canada/modules/datastore/__tests__/conftest.py
    - src/mcp_canada/modules/datastore/__tests__/test_client.py
  modified:
    - pyproject.toml (added aiosqlite>=0.22.0)
    - src/mcp_canada/server.py (added --ephemeral flag)

key-decisions:
  - "aiosqlite module-level singleton pattern (global _db) — lazy init on first get_db() call"
  - "was_cached always False for datastore client — SQLite is local I/O not a cached remote API"
  - "IDENTIFIER_RE allows max 64 chars (1 leading + up to 63 more) per regex ^[a-zA-Z_][a-zA-Z0-9_]{0,63}$"
  - "fetchmany result cast to list[] for pyright compatibility with len() and slice operations"

patterns-established:
  - "Datastore client pattern: no cached_fetch, no get_limiter — local I/O only"
  - "conftest.py pattern: async db fixture with :memory: connection + patched_db fixture to swap client._db"

requirements-completed: [DS-07, DS-08]

# Metrics
duration: 3min
completed: 2026-04-07
---

# Phase 7 Plan 01: Datastore Module Skeleton + Client Summary

**Async SQLite persistence layer with regex-based identifier validation, WAL mode singleton, and 47 TDD-verified tests covering all 6 CRUD operations**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-07T15:42:13Z
- **Completed:** 2026-04-07T15:45:33Z
- **Tasks:** 1 (TDD: RED + GREEN + lint/type fixes)
- **Files modified:** 9

## Accomplishments
- Created complete datastore module skeleton following the 5-file module pattern
- Implemented async SQLite singleton client (get_db, close_db, create_table, insert_rows, run_query, list_tables, get_schema, drop_table) — all returning (data, False) tuples
- Identifier validation via IDENTIFIER_RE regex rejects SQL metacharacters before any SQL executes
- Added --ephemeral flag to server.py _build_parser() for in-memory mode
- 47 unit tests written in RED phase, all passing green (751 total tests pass, no regressions)

## Task Commits

Each task was committed atomically:

1. **Task 1: Datastore module skeleton + client with TDD** - `c0bfade` (feat)

**Plan metadata:** (docs commit follows)

_Note: TDD — tests written in RED phase first, then full implementation in GREEN phase._

## Files Created/Modified
- `src/mcp_canada/modules/datastore/__init__.py` - MODULE_NAME and MODULE_DESCRIPTION
- `src/mcp_canada/modules/datastore/constants.py` - DB_PATH, IDENTIFIER_RE, MAX_QUERY_ROWS, ALLOWED_QUERY_PREFIXES
- `src/mcp_canada/modules/datastore/schemas.py` - ColumnDef, QueryResult, TableInfo Pydantic v2 models
- `src/mcp_canada/modules/datastore/client.py` - Full async client with singleton, validation, all CRUD ops
- `src/mcp_canada/modules/datastore/__tests__/conftest.py` - async db and patched_db fixtures
- `src/mcp_canada/modules/datastore/__tests__/test_client.py` - 47 tests across all public functions
- `pyproject.toml` - added aiosqlite>=0.22.0 to dependencies
- `src/mcp_canada/server.py` - added --ephemeral flag to _build_parser()

## Decisions Made
- Used module-level `_db: aiosqlite.Connection | None = None` singleton (lazy init in get_db()). Avoids per-call connection overhead while remaining async-safe for single-process MCP server.
- Cast `fetchmany()` result to `list` explicitly (`list(await cursor.fetchmany(...))`) to satisfy pyright's type narrowing — `Iterable[Row]` lacks `__len__` and `__getitem__`.
- `was_cached` is always `False` for all datastore operations. SQLite is local I/O, not a cached remote API. The tuple convention is maintained for interface consistency with other modules.

## Deviations from Plan

None - plan executed exactly as written. One minor auto-fix for pyright type annotation (cast to `list`) included in the same task commit.

## Issues Encountered
- pyright flagged `fetchmany()` return type as `Iterable[Row]` (lacks `len()` and slice). Fixed by explicitly casting to `list`. No behavioral change.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- datastore client is fully tested and ready for Plan 02 (tools.py with ds_create_table, ds_insert_data, ds_query, ds_list_tables, ds_get_schema, ds_drop_table)
- FileSystemProvider will auto-discover the datastore module on server start
- --ephemeral flag is wired through _config so client.py can read it via server._config.get("ephemeral")

---
*Phase: 07-datastore-ssl*
*Completed: 2026-04-07*
