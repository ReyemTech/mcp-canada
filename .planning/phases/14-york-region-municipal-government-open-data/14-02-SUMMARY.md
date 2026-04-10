---
phase: 14-york-region-municipal-government-open-data
plan: 02
subsystem: york_region
tags: [arcgis-hub, tools, mcp-tools, york-region, markham, newmarket, aurora, bm25, discovery]
dependency_graph:
  requires: [modules/york_region/client.py, shared/arcgis_hub.py, shared/envelope.py]
  provides: [modules/york_region/tools.py]
  affects: [BM25 discovery index, FileSystemProvider tool registration]
tech_stack:
  added: []
  patterns: [_call_client error-centralisation, dispatch pattern for enum tools, max_records clamping]
key_files:
  created:
    - src/mcp_canada/modules/york_region/tools.py
    - src/mcp_canada/modules/york_region/__tests__/test_tools.py
  modified: []
decisions:
  - "_call_client private async helper centralises all error handling (NoPortalError → NOT_FOUND, HTTP 404 → NOT_FOUND, 5xx → UPSTREAM_ERROR, bare Exception → UPSTREAM_ERROR) — tools never raise"
  - "Dispatch tools (get_public_health, get_census_demographics, get_waste_data) return make_error('INVALID_INPUT') with valid= list for invalid enum values"
  - "max_records silently clamped to 5000 in all query_features tools — documented in docstring, not raised as error"
  - "Tasks 1 and 2 implemented together in a single TDD cycle (both share tools.py) — committed as one feat commit"
metrics:
  duration: 8min
  completed_date: "2026-04-10"
  tasks_completed: 2
  files_created: 2
  tests_added: 74
---

# Phase 14 Plan 02: York Region Tools Summary

**One-liner:** 27 standalone @tool functions (20 discovery × 4 portals + 7 curated) with BM25 docstrings, _call_client error-centralisation, and 74 unit tests at 99.89% coverage.

## What Was Built

### tools.py — 27 @tool functions

The full MCP tool surface for the york_region module, exposing the Plan 01 client layer through FastMCP's FileSystemProvider-compatible standalone @tool interface.

#### Discovery tools (20 — 5 per portal)

Each of the 4 verified portals (york_region, markham, newmarket, aurora) gets 5 discovery tools:

| Action | Tool pattern | Params |
|--------|-------------|--------|
| search_datasets | `{prefix}_search_datasets` | query, limit (clamped 1-100), offset, lang |
| get_dataset_details | `{prefix}_get_dataset_details` | dataset_id, lang |
| query_features | `{prefix}_query_features` | service_url, layer_id, where, out_fields, include_geometry, max_records (clamped 5000), lang |
| list_organizations | `{prefix}_list_organizations` | lang |
| list_categories | `{prefix}_list_categories` | lang |

#### Curated York Region tools (5)

| Tool | Description |
|------|-------------|
| `york_region_get_transit_stops` | YRT/Viva bus stops (~4,810) with optional name filter |
| `york_region_get_transit_routes` | YRT/Viva routes with optional route_short_name filter |
| `york_region_get_road_network` | Regional road network (~762 roads) |
| `york_region_get_public_health` | Dispatch: beach_water / hospital / drinking_water |
| `york_region_get_census_demographics` | Dispatch: age_sex / income (2021 Census, DA-level) |
| `york_region_get_waste_data` | Dispatch: diversion_statistics / sites |

#### Curated Markham tools (2)

| Tool | Description |
|------|-------------|
| `markham_get_addresses` | Civic addresses with optional street filter |
| `markham_get_road_network` | SLRN road network with optional name filter |

### Error handling architecture

`_call_client(coro, *, api_url, lang)` is a private async helper that wraps every client coroutine call:

- `NoPortalError` → `make_error("NOT_FOUND", ...)`
- `httpx.HTTPStatusError` 404 → `make_error("NOT_FOUND", ...)`
- `httpx.HTTPStatusError` other → `make_error("UPSTREAM_ERROR", f"HTTP {status}: ...")`
- `Exception` → `make_error("UPSTREAM_ERROR", str(e))` — tools NEVER raise

Dispatch tools (public_health, census, waste) validate their enum parameter before calling `_call_client` and return `make_error("INVALID_INPUT")` immediately on bad values.

### test_tools.py — 74 unit tests

| Class | Tests | Coverage |
|-------|-------|---------|
| TestYorkRegionDiscovery | 5 | happy path per action type (york_region_ prefix) |
| TestAllPrefixesExist | 20 parametrized | all 20 discovery tools wired and return _meta |
| TestNotFoundHandling | 2 | NoPortalError → NOT_FOUND, ValueError → UPSTREAM_ERROR |
| TestHTTPErrorHandling | 2 | 404 → NOT_FOUND, 500 → UPSTREAM_ERROR |
| TestGenericExceptionHandling | 1 | bare Exception → UPSTREAM_ERROR |
| TestLangParameter | 1 | lang="fr" flows to _meta.lang |
| TestQueryFeaturesInputClamp | 1 | max_records=9999 clamped to 5000 |
| TestYorkRegionCurated | 10 | happy path per curated tool |
| TestYorkRegionDispatch | 4 | invalid dispatch values + spy on hospital dispatch |
| TestMarkhamCurated | 3 | happy paths + street filter pass-through |
| TestAllToolsReturnEnvelope | 25 parametrized | every tool returns arcgis-hub envelope |

## Test Coverage

| File | Stmts | Miss | Cover |
|------|-------|------|-------|
| tools.py | 128 | 0 | 100% |
| client.py | 93 | 0 | 100% |
| constants.py | 34 | 0 | 100% |
| schemas.py | 14 | 0 | 100% |
| **Total** | **871** | **1** | **99.89%** |

## Deviations from Plan

### Merged Tasks 1 and 2 into one TDD cycle

Both tasks modify the same two files (tools.py, test_tools.py). Implementing them as separate commits would have required splitting an already-coherent green phase into two. All tests for both tasks were written together and committed as a single feat commit (737ed90). This is a scope deviation only — no behaviour or implementation deviation from the plan spec.

All other plan requirements executed exactly as written.

## Self-Check

### Files Created

- [x] `src/mcp_canada/modules/york_region/tools.py` — created (128 statements, 100% coverage)
- [x] `src/mcp_canada/modules/york_region/__tests__/test_tools.py` — created (74 tests)

### Commits

- [x] 737ed90 — feat(14-02): add york_region tools.py — 27 @tool functions with unit tests

### Verification Results

- [x] 124 tests pass (119 york_region + 5 test_quality)
- [x] Coverage 99.89% (≥95% required)
- [x] pyright: 0 errors, 0 warnings
- [x] ruff: all checks passed

## Self-Check: PASSED
