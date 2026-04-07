---
phase: 07-datastore-ssl
plan: 02
subsystem: database
tags: [sqlite, tools, tdd, mcp, integration, bm25, envelope]

# Dependency graph
requires: [07-01]
provides:
  - 6 ds_ @tool functions wrapping the client layer
  - 26 unit tests covering all 6 tools (envelope, error, lang, docstring quality)
  - 6 integration tests through MCP Client layer (TestDatastoreScenarios)
  - README updated with datastore tool catalog section
affects: [08-statcan, 09-statcan-tools]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tool wraps (data, was_cached) tuple: _, was_cached = await client.fn(); return make_response(..., cached=was_cached)"
    - "ValueError from _validate_identifier -> INVALID_INPUT; bare Exception -> DATASTORE_ERROR"
    - "Integration test isolation: autouse fixture patches client._db with in-memory aiosqlite connection"
    - "Keywords on single line in docstring — multi-line Keywords wraps to next line break the test_quality.py parser"
    - "ds_get_schema returns NOT_FOUND when col_info is empty (nonexistent table returns empty PRAGMA result)"

key-files:
  created:
    - src/mcp_canada/modules/datastore/tools.py
    - src/mcp_canada/modules/datastore/__tests__/test_tools.py
  modified:
    - tests/integration/test_tool_scenarios.py (added TestDatastoreScenarios + aiosqlite import)
    - README.md (added datastore catalog section, updated tool count 83→89)

key-decisions:
  - "Keywords must be on a single line — the test_quality.py docstring parser splits on newlines and only reads the Keywords: line, not continuation lines"
  - "ds_get_schema returns NOT_FOUND (not DATASTORE_ERROR) when PRAGMA table_info returns empty — empty result means table doesn't exist"
  - "Integration test DB isolation via autouse fixture patching client._db — avoids touching real datastore.db, no server restart needed"

patterns-established:
  - "Datastore tool pattern: import client, call client functions, unwrap (data, was_cached), return make_response/make_error"
  - "Integration test isolation for local I/O: autouse fixture patches module-level singleton before each test"

requirements-completed: [DS-01, DS-02, DS-03, DS-04, DS-05, DS-06]

# Metrics
duration: 5min
completed: 2026-04-07
---

# Phase 7 Plan 02: Datastore Tool Layer Summary

**6 ds_ @tool functions with TDD-verified unit tests and MCP Client integration tests, completing the datastore agent-facing API**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-07T15:47:36Z
- **Completed:** 2026-04-07T15:52:27Z
- **Tasks:** 2 (Task 1 TDD + Task 2 integration)
- **Files modified:** 4

## Accomplishments

- Implemented 6 standalone @tool functions (ds_create_table, ds_insert_data, ds_query, ds_list_tables, ds_get_schema, ds_drop_table) with full make_response/make_error envelope
- TDD: 26 failing tests written first (RED), then implementation to green (GREEN)
- All tools unwrap (data, was_cached) tuples from client functions per project convention
- ValueError from identifier validation -> INVALID_INPUT; other exceptions -> DATASTORE_ERROR
- BM25 docstrings with Use-for and 8+ Keywords per tool (all keywords on single line per parser requirement)
- 6 integration tests through MCP Client layer with in-memory DB isolation via autouse fixture
- Coverage: 96.15% (gate requires 95%), 777 total tests pass with no regressions
- README updated: datastore catalog section added, tool count updated 83 -> 89

## Task Commits

Each task was committed atomically:

1. **Task 1: Datastore tools with TDD** - `674623b` (feat)
2. **Task 2: Integration tests + coverage gate** - `07abd2a` (feat)

## Files Created/Modified

- `src/mcp_canada/modules/datastore/tools.py` — 6 @tool functions, 239 lines
- `src/mcp_canada/modules/datastore/__tests__/test_tools.py` — 26 unit tests across 7 test classes
- `tests/integration/test_tool_scenarios.py` — added TestDatastoreScenarios (6 integration tests)
- `README.md` — added datastore catalog section, updated tool count

## Decisions Made

- Keywords must be on a single line in docstrings. The test_quality.py parser reads the line containing "Keywords:" and splits on commas. If keywords wrap to the next line, only the first line's keywords are counted, causing the 8-keyword assertion to fail.
- ds_get_schema returns NOT_FOUND when PRAGMA table_info returns an empty result (nonexistent table) rather than DATASTORE_ERROR, as this is a user-input error not a system error.
- Integration test isolation uses an autouse pytest fixture that patches `client._db` with an in-memory aiosqlite connection before each test, then restores the original value after. This avoids creating a test database file while still exercising the full tool → client → SQL path through the MCP layer.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Keywords line parser requires single-line keywords**
- **Found during:** Task 1 (GREEN phase, docstring quality test)
- **Issue:** Multi-line Keywords docstrings (keywords wrapped to next line) caused test_all_tools_have_minimum_keywords to count only the keywords before the line break
- **Fix:** Consolidated all Keywords lines to single lines (e.g., "Keywords: datastore, create, table, sqlite, store, persist, schema, columns, local, database")
- **Files modified:** src/mcp_canada/modules/datastore/tools.py
- **Commit:** included in 674623b (same task commit)

## Self-Check

Files verified to exist:
- src/mcp_canada/modules/datastore/tools.py: FOUND
- src/mcp_canada/modules/datastore/__tests__/test_tools.py: FOUND
- .planning/phases/07-datastore-ssl/07-02-SUMMARY.md: FOUND (this file)

Commits verified:
- 674623b: feat(07-02): implement 6 ds_ datastore tools with TDD
- 07abd2a: feat(07-02): add TestDatastoreScenarios integration tests + coverage gate

## Self-Check: PASSED

---
*Phase: 07-datastore-ssl*
*Completed: 2026-04-07*
