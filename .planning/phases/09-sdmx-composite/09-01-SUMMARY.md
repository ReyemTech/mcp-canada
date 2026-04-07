---
phase: 09-sdmx-composite
plan: "01"
subsystem: statcan/sdmx
tags: [sdmx, client, schemas, constants, tdd]
dependency_graph:
  requires:
    - Phase 08: statcan WDS client infrastructure (_make_statcan_client, _limiter_acquire, cached_fetch)
  provides:
    - get_sdmx_structure: fetches and caches SDMX 2.1 XML structure, returns SDMXStructure
    - get_sdmx_data: server-side filtered observations via SDMX-JSON
    - get_sdmx_vector_data: single-vector SDMX observations via SDMX-JSON
    - _parse_structure_xml, _make_suggested_key, _build_sdmx_key, _flatten_sdmx_json helpers
    - SDMXCodeValue, SDMXDimension, SDMXStructure, SDMXObservationRow schemas
    - SDMX_BASE_URL, _SDMX_API_NAME, SDMX_XML_NAMESPACES constants
  affects:
    - statcan/constants.py — SDMX constants appended
    - statcan/schemas.py — 4 SDMX models appended
    - statcan/client.py — 7 SDMX functions added
    - statcan/__tests__/conftest.py — 3 SDMX fixtures added
    - statcan/__tests__/test_client.py — 36 SDMX unit tests added
tech_stack:
  added:
    - xml.etree.ElementTree (stdlib) for SDMX 2.1 XML structure parsing
  patterns:
    - TDD Red-Green-Refactor across both tasks
    - statcan_sdmx: cache key prefix (no collision with statcan_wds: keys)
    - cached_fetch with CACHE_TTL_META (24hr) for structure only; data/vector NOT cached
    - Colon-first then dot-fallback delimiter detection in _flatten_sdmx_json
key_files:
  modified:
    - src/mcp_canada/modules/statcan/constants.py
    - src/mcp_canada/modules/statcan/schemas.py
    - src/mcp_canada/modules/statcan/client.py
    - src/mcp_canada/modules/statcan/__tests__/conftest.py
    - src/mcp_canada/modules/statcan/__tests__/test_client.py
decisions:
  - "Cache structure XML text (str), not parsed SDMXStructure — avoids Pydantic serialization complexity in aiocache"
  - "SDMX_XML_NAMESPACES constant in constants.py passed to every ElementTree find/findall to prevent silent empty results (Pitfall 3)"
  - "Ref element in XML has no namespace prefix — use plain .find('.//Ref') fallback after str:Enumeration/Ref search"
  - "Series key delimiter: try ':' first (SDMX-JSON spec), fall back to '.' (StatCan observed behavior)"
  - "get_sdmx_data and get_sdmx_vector_data are NOT cached — observation data changes frequently"
metrics:
  duration: "4 min"
  completed_date: "2026-04-07"
  tasks_completed: 2
  files_changed: 5
---

# Phase 9 Plan 01: SDMX Client Layer Summary

**One-liner:** SDMX client layer with XML structure parsing, SDMX-JSON flattening, and three public async functions for structure/data/vector queries using StatCan SDMX REST API.

## What Was Built

Three SDMX client functions that Plan 02 tools will wrap:

1. **`get_sdmx_structure(product_id)`** — fetches SDMX 2.1 XML from `/structure/Data_Structure_{pid}`, parses with ElementTree, caches with `statcan_sdmx:structure:{pid}` key (24hr TTL).

2. **`get_sdmx_data(product_id, key, *, start_period, end_period, last_n)`** — fetches SDMX-JSON from `/data/DF_{pid}/{key}` with mutual exclusion enforced (ValueError if both lastN and date range provided). NOT cached.

3. **`get_sdmx_vector_data(vector_id, *, start_period, end_period)`** — fetches SDMX-JSON from `/vector/v{vid}`. NOT cached.

Supporting helpers: `_parse_structure_xml`, `_make_suggested_key`, `_build_sdmx_key`, `_flatten_sdmx_json`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | SDMX constants, schemas, and test fixtures | bc0ab8f | constants.py, schemas.py, conftest.py, test_client.py |
| 2 | SDMX client functions with unit tests | 2fb10bc | client.py, test_client.py |

## Test Results

- 36 new SDMX unit tests added, all green
- 136 total statcan tests pass (no regressions)
- `uv run ruff check` — clean
- `uv run pyright` — 0 errors, 0 warnings

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] XML Ref element has no namespace prefix**
- **Found during:** Task 2 — `_parse_structure_xml` development
- **Issue:** SDMX 2.1 XML uses `<Ref id="CL_GEO" .../>` inside `<str:Enumeration>`, but `<Ref>` has no namespace prefix. Using `dim.find(".//str:Enumeration/Ref", ns)` would fail silently; `Ref` has no `str:` prefix.
- **Fix:** Added fallback: first try `".//str:Enumeration/Ref"` (namespace-qualified parent), then `".//Ref"` (bare element name). The fixture XML and the real StatCan SDMX XML both use bare `<Ref>` elements.
- **Files modified:** client.py
- **Commit:** 2fb10bc

**2. [Rule 1 - Bug] Stray `acquire_mock.assert_called_once()` line leaked into test**
- **Found during:** Task 1 RED phase verification
- **Issue:** An `acquire_mock.assert_called_once()` call appeared outside its test method scope due to edit boundary alignment.
- **Fix:** Removed the stray line during GREEN phase.
- **Files modified:** test_client.py
- **Commit:** bc0ab8f

**3. [Rule 2 - Missing] Unused import `cached_fetch` in test**
- **Found during:** Task 2 ruff check
- **Issue:** `from mcp_canada.shared.cache import cached_fetch` was imported but not used in `test_uses_statcan_sdmx_cache_key`.
- **Fix:** Removed unused import.
- **Files modified:** test_client.py
- **Commit:** 2fb10bc

## Self-Check: PASSED

- constants.py: FOUND
- schemas.py: FOUND
- client.py: FOUND
- Commit bc0ab8f (Task 1): FOUND
- Commit 2fb10bc (Task 2): FOUND
