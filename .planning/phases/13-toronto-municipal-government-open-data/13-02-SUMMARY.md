---
phase: 13-toronto-municipal-government-open-data
plan: "02"
subsystem: toronto-tools
tags: [toronto, tools, tdd, integration-tests, readme, bm25]
dependency_graph:
  requires:
    - src/mcp_canada/modules/toronto/client.py
    - src/mcp_canada/shared/envelope.py
  provides:
    - src/mcp_canada/modules/toronto/tools.py (12 @tool functions)
    - tests/integration/test_tool_scenarios.py (TestTorontoToolScenarios)
  affects:
    - README.md (Toronto section added, tool count updated)
tech_stack:
  added: []
  patterns:
    - Standalone @tool functions with BM25 docstrings (Use for: + Keywords:)
    - Generic Exception catch for GTFS/datastore tools (not just HTTPStatusError)
    - fetch_organizations called without lang param (Toronto client differs from Ontario)
key_files:
  created:
    - src/mcp_canada/modules/toronto/tools.py
    - src/mcp_canada/modules/toronto/__tests__/test_tools.py
  modified:
    - tests/integration/test_tool_scenarios.py (TestTorontoToolScenarios appended)
    - README.md (Toronto section + tool count 116->128)
decisions:
  - "Toronto fetch_organizations takes no lang param — Toronto client omits the lang arg (Ontario client differs)"
  - "GTFS/datastore tools catch generic Exception (not just HTTPStatusError) since network and ZIP errors are not always HTTP errors"
  - "No BASE_URL import needed in tools.py — _API_URL defined as a string literal matching open.toronto.ca"
metrics:
  duration: 5min
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_modified: 4
---

# Phase 13 Plan 02: Toronto Tool Functions and Integration Tests Summary

**One-liner:** 12 toronto_ @tool functions with BM25 docstrings, 52 unit tests (TDD), 8 integration tests through MCP Client layer, and README updated with Toronto section.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create Toronto tool functions and unit tests (TDD) | 623409d | tools.py, test_tools.py |
| 2 | Add integration tests and update README | 6e04ace | test_tool_scenarios.py, README.md |
| fix | Remove unused import, fix fetch_organizations call | a82993d | tools.py |

## What Was Built

### Task 1: 12 Toronto Tool Functions + 52 Unit Tests

Created `src/mcp_canada/modules/toronto/tools.py` with 12 standalone `@tool` functions:

**Discovery (5):**
- `toronto_search_datasets` — CKAN package_search with query, rows, sort, filter
- `toronto_get_dataset_details` — package_show by ID/slug; NOT_FOUND on 404
- `toronto_get_resource` — resource_show by UUID; NOT_FOUND on 404
- `toronto_list_organizations` — organization_list with full fields
- `toronto_get_dataset_stats` — dataset count + portal/api_version stats

**Curated (7):**
- `toronto_get_ttc_stops` — GTFS stop search by name; catches generic Exception (ZIP)
- `toronto_get_ttc_routes` — GTFS routes with optional route_type filter
- `toronto_get_neighbourhood_profile` — 2016 census indicators filtered by neighbourhood/characteristic
- `toronto_compare_neighbourhoods` — single indicator across all 140 neighbourhoods
- `toronto_get_311_requests` — annual ZIP+CSV service requests with ward/type/status filters; NOT_FOUND on 404
- `toronto_get_rentsafe_evaluations` — apartment evaluation scores with ward/min_score filters
- `toronto_get_short_term_rentals` — STR registration records with ward/status filters

**Unit tests:** 52 tests in `test_tools.py` — happy path (make_response envelope), NOT_FOUND on 404, UPSTREAM_ERROR on 500 or generic Exception, lang parameter pass-through, docstring quality (Use for: + Keywords:).

### Task 2: Integration Tests + README

**Integration tests** (`TestTorontoToolScenarios`, 8 tests) appended to `tests/integration/test_tool_scenarios.py`:
1. `test_toronto_discovery` — BM25 discover_tools finds toronto_ tools
2. `test_toronto_dataset_details` — real TTC dataset details via open.toronto.ca CKAN
3. `test_toronto_ttc_stops` — real GTFS stop search (120s timeout for ZIP download)
4. `test_toronto_ttc_routes` — real GTFS route list
5. `test_toronto_neighbourhood_profile` — Rosedale census data from datastore
6. `test_toronto_rentsafe` — RentSafeTO evaluations by ward
7. `test_toronto_short_term_rentals` — STR registrations with status filter
8. `test_toronto_compare_neighbourhoods` — median income comparison across neighbourhoods

**README updates:**
- Added Toronto section after Ontario (12 tools in two groups: Discovery 5 + Curated 7)
- Updated tool count: 116 → 128
- Updated description: added "1 municipal API" and "Toronto municipal data"
- Updated architecture section: added ontario/ and toronto/ module entries

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed fetch_organizations call — no lang parameter in Toronto client**
- **Found during:** pyright type check after Task 2
- **Issue:** tools.py called `fetch_organizations(lang=lang)` but Toronto's client function signature is `fetch_organizations(all_fields=True, sort="name asc")` — no lang param (unlike Ontario's client)
- **Fix:** Changed call to `fetch_organizations()` without lang argument
- **Files modified:** src/mcp_canada/modules/toronto/tools.py
- **Commit:** a82993d

**2. [Rule 1 - Bug] Removed unused BASE_URL import**
- **Found during:** ruff lint check
- **Issue:** `from mcp_canada.modules.toronto.constants import BASE_URL` unused since _API_URL is defined inline
- **Fix:** Removed the import line
- **Files modified:** src/mcp_canada/modules/toronto/tools.py
- **Commit:** a82993d

## Self-Check: PASSED

All files exist and all commits verified:
- FOUND: src/mcp_canada/modules/toronto/tools.py
- FOUND: src/mcp_canada/modules/toronto/__tests__/test_tools.py
- FOUND: TestTorontoToolScenarios in tests/integration/test_tool_scenarios.py
- FOUND: Toronto section in README.md
- FOUND: commit 623409d
- FOUND: commit 6e04ace
- FOUND: commit a82993d
