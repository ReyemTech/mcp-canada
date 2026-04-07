---
phase: 09-sdmx-composite
plan: "02"
subsystem: statcan-sdmx
tags: [sdmx, tools, composite, datastore, integration]
dependency_graph:
  requires: ["09-01"]
  provides: ["sc_get_sdmx_structure", "sc_get_sdmx_data", "sc_get_sdmx_vector_data", "sc_fetch_vectors_to_store"]
  affects: ["statcan module tools layer", "datastore composite bridge"]
tech_stack:
  added: []
  patterns: ["Tool layer wrapping SDMX client functions", "Composite tool pattern (multi-module)", "In-memory DB fixture for integration test isolation"]
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/statcan/tools.py
    - src/mcp_canada/modules/statcan/__tests__/test_tools.py
    - tests/integration/test_tool_scenarios.py
    - README.md
decisions:
  - "sc_get_sdmx_data mutual exclusion (lastN + date range) enforced at tool layer not client layer — keeps client simple, tool provides user-friendly error"
  - "sc_fetch_vectors_to_store validates table_name via IDENTIFIER_RE before any network call — fail-fast, no wasted API calls on bad input"
  - "sc_get_sdmx_data dimensions dict with non-empty key: key wins without fetching structure — avoids unnecessary network round-trip"
metrics:
  duration: "18min"
  completed_date: "2026-04-07"
  tasks_completed: 2
  files_modified: 4
---

# Phase 09 Plan 02: SDMX Tool Layer + Composite Summary

**One-liner:** 4 new @tool functions — 3 SDMX wrappers and 1 composite fetch-and-store — with 16 unit tests and 6 integration tests through MCP Client.

## What Was Built

### sc_get_sdmx_structure (SC-10)
Wraps `get_sdmx_structure()`, serializes dimensions with position/id/codelist_id/codes and includes `suggested_key` at top level. Returns `statcan-sdmx` api_name envelope.

### sc_get_sdmx_data (SC-11)
Accepts raw `key` string OR `dimensions` dict (auto-fetches structure to build key via `_build_sdmx_key`). Key wins over dimensions when both provided. Enforces mutual exclusion: `last_n` + date range returns `INVALID_INPUT` immediately without touching the network.

### sc_get_sdmx_vector_data (SC-12)
Wraps `get_sdmx_vector_data()` with `start_period`/`end_period` pass-through. Serializes `SDMXObservationRow` list via `.model_dump()`.

### sc_fetch_vectors_to_store (SC-15)
Composite tool spanning StatCan WDS + Datastore modules:
1. Validates `table_name` via `IDENTIFIER_RE` before any network call
2. Calls `get_bulk_vector_data()` (WDS release-date endpoint)
3. Flattens observations, adds `vector_id` field per row
4. Infers SQLite schema from first row via `_infer_sqlite_type`
5. Creates table (IF NOT EXISTS — append semantics) then inserts rows
6. Returns `{stored, table, vectors}` envelope

## Commits

| Hash | Description |
|------|-------------|
| ea11f5a | feat(09-02): add 4 SDMX tool functions with unit tests |
| 9ea359f | feat(09-02): add TestSdmxScenarios integration tests |

## Test Results

- Unit tests (statcan module): 159 passed
- Coverage: 96.39% (threshold: 95%)
- Ruff: clean
- Pyright: 0 errors

## Integration Tests Added

`TestSdmxScenarios` in `tests/integration/test_tool_scenarios.py`:
1. `test_sdmx_structure_for_cpi_table` — dimensions list + suggested_key shape
2. `test_sdmx_data_last_n` — observations envelope through MCP client
3. `test_sdmx_data_mutual_exclusion` — INVALID_INPUT for lastN + date range
4. `test_sdmx_vector_data` — vector observations endpoint
5. `test_discover_sdmx_tools` — BM25 discovery of SDMX tools
6. `test_fetch_vectors_to_store` — composite store + ds_query roundtrip (in-memory DB)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- src/mcp_canada/modules/statcan/tools.py — FOUND (sc_get_sdmx_structure defined)
- src/mcp_canada/modules/statcan/__tests__/test_tools.py — FOUND (TestScGetSdmxStructure present)
- tests/integration/test_tool_scenarios.py — FOUND (TestSdmxScenarios present)
- Commits ea11f5a and 9ea359f — verified in git log
