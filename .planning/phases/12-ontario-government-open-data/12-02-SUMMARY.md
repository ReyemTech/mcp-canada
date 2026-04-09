---
phase: 12-ontario-government-open-data
plan: "02"
subsystem: ontario
tags: [tools, mcp, ontario, ckan, open-data, integration-tests, readme]
dependency_graph:
  requires: ["12-01"]
  provides: ["ontario-tools-layer", "ontario-integration-tests"]
  affects: ["README.md", "tests/integration/test_tool_scenarios.py"]
tech_stack:
  added: []
  patterns: ["standalone-@tool", "make_response/make_error-envelope", "reshape_temporal_columns", "BM25-docstrings"]
key_files:
  created:
    - src/mcp_canada/modules/ontario/tools.py
    - src/mcp_canada/modules/ontario/__tests__/test_tools.py
  modified:
    - tests/integration/test_tool_scenarios.py
    - README.md
decisions:
  - "Patch client functions at tools module namespace (mcp_canada.modules.ontario.tools.*) not client module — functions are imported into tools.py namespace"
metrics:
  duration: "3m 23s"
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_modified: 4
---

# Phase 12 Plan 02: Ontario Tool Functions, Unit Tests, Integration Tests, README

One-liner: 6 ontario_ MCP tools with BM25 docstrings calling Ontario CKAN client, 27 unit tests + 6 integration tests through MCP Client, README updated to 116 tools.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Create Ontario tool functions and unit tests (TDD) | 97c8617 | tools.py, test_tools.py |
| 2 | Add integration tests and update README | 8b70d1a | test_tool_scenarios.py, README.md |

## What Was Built

### Task 1: Ontario Tool Functions + Unit Tests

Created `src/mcp_canada/modules/ontario/tools.py` with 6 standalone `@tool` functions:

- `ontario_search_datasets` — search by keyword with optional filter, rows, sort
- `ontario_get_dataset_details` — full dataset metadata by ID/slug; NOT_FOUND on 404
- `ontario_get_resource` — resource file details by UUID; NOT_FOUND on 404
- `ontario_list_organizations` — list Ontario ministries/agencies publishing data
- `ontario_get_dataset_stats` — portal stats: total_datasets, portal, api_version
- `ontario_get_population_projections` — MOF population projections with `reshape_temporal_columns` for year/recent/filter support

All tools:
- Use standalone `@tool` from `fastmcp.tools`
- Have `lang: Literal["en", "fr"] = "en"` parameter
- Return `make_response()` on success, `make_error()` on failure (never raise)
- Have `Use for:` and `Keywords:` lines in docstrings (BM25 discovery ready)
- Have `ontario_` prefix

Created 27 unit tests covering happy path, error path, lang passthrough, and docstring quality for all 6 tools.

### Task 2: Integration Tests + README

Added `TestOntarioToolScenarios` class (6 tests) to existing integration test file, calling tools through MCP Client (`call_tool`) — not client functions directly:

1. `test_ontario_search_population` — search with query="population"
2. `test_ontario_dataset_details` — details for "population-projections" dataset
3. `test_ontario_list_organizations` — list Ontario ministries
4. `test_ontario_portal_stats` — portal statistics with integer total_datasets
5. `test_ontario_discovery` — BM25 discover_tools finds ontario_ tool
6. `test_ontario_search_error_handling` — nonexistent dataset returns error envelope

Updated `README.md`:
- Added `### Ontario Government Open Data — 6 tools` section
- Listed all 6 tools with descriptions and key parameters
- Updated header tool count from 110 to 116 tools

## Verification

- `uv run pytest src/mcp_canada/modules/ontario/__tests__/ -x -v` — 66 passed
- `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` — 95.71% coverage, 1095 passed
- `uv run pyright src/mcp_canada/modules/ontario/` — 0 errors, 0 warnings
- `uv run ruff check src/mcp_canada/modules/ontario/` — all checks passed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Patch path pointed to client module, not tools namespace**
- **Found during:** Task 1 — first GREEN phase run
- **Issue:** Tests patched `mcp_canada.modules.ontario.client.fetch_*` but tools.py imports functions directly into its namespace; the live client was called instead
- **Fix:** Changed all patch paths to `mcp_canada.modules.ontario.tools.fetch_*`
- **Files modified:** `src/mcp_canada/modules/ontario/__tests__/test_tools.py`
- **Commit:** 97c8617

**2. [Rule 3 - Lint] Unused `inspect` import in test file**
- **Found during:** Task 1 — ruff lint check after GREEN phase
- **Fix:** Removed unused `import inspect` from test_tools.py
- **Files modified:** `src/mcp_canada/modules/ontario/__tests__/test_tools.py`
- **Commit:** 97c8617

## Self-Check: PASSED

- [x] `src/mcp_canada/modules/ontario/tools.py` — exists, 6 @tool functions
- [x] `src/mcp_canada/modules/ontario/__tests__/test_tools.py` — exists, 27 tests
- [x] `tests/integration/test_tool_scenarios.py` — contains TestOntarioToolScenarios
- [x] `README.md` — contains "Ontario" section with 6 tools
- [x] Commits 97c8617 and 8b70d1a — verified in git log
