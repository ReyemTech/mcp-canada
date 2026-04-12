---
phase: 16-quebec-government-open-data
plan: 05
subsystem: api
tags: [parsers, quebec, ckan, wfs, mtq, hydro-quebec, bm25, gap-closure]

# Dependency graph
requires:
  - phase: 16-quebec-government-open-data
    provides: Quebec CKAN + MTQ WFS tools with 4 UAT gaps to close

provides:
  - fetch_and_parse query-string format detection (outputformat/format/f keys)
  - fetch_road_conditions without exception swallow — errors propagate to tool layer
  - fetch_electricity_data with CSV/XLSX/XLS matcher, empty-URL skip, 3-tuple return
  - quebec_get_electricity_data envelope points at real fetched XLSX URL
  - quebec_get_er_wait_times with health/medical/sante BM25 keywords

affects: [17-alberta-government-open-data, 18-26-provinces-territories, shared-parsers-callers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "urllib.parse.parse_qs query-string format inspection added to fetch_and_parse — callers with WFS ?outputformat=csv URLs now route to _parse_csv without path suffix"
    - "3-tuple (rows, source_url, was_cached) return from fetch_electricity_data — bundles source URL into single cache entry"
    - "cached_fetch passthrough pattern in tests — patch.object(_mod, 'cached_fetch', side_effect=passthrough) avoids cache key collision across tests"

key-files:
  created: []
  modified:
    - src/mcp_canada/shared/parsers.py
    - src/mcp_canada/shared/__tests__/test_parsers.py
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/tools.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/modules/quebec/__tests__/test_tools.py
    - .planning/phases/16-quebec-government-open-data/16-RESEARCH.md

key-decisions:
  - "fetch_and_parse query-string format detection: urllib.parse.parse_qs with case-insensitive key normalization — zero new dependencies, fully backward-compatible with existing path-suffix detection"
  - "fetch_road_conditions try/except Exception swallow removed — errors propagate to @tool layer which already wraps as UPSTREAM_ERROR; was masking BadZipFile from parser dispatch bug"
  - "fetch_electricity_data 3-tuple (rows, source_url, was_cached): bundled in _fetch() tuple so single cache entry holds both rows and source URL; cache key uses v2 suffix to invalidate stale 2-tuple entries"
  - "Hydro-Québec package is XLSX-only (years 2018-2021; 2020 has empty URL): format matcher expanded from CSV-only to (CSV, XLSX, XLS)"
  - "cached_fetch passthrough in electricity tests: patch.object(_mod, 'cached_fetch') to prevent cache key collision across tests sharing the same limit=500 default"

patterns-established:
  - "query-string format hints: _matches(ext, fmt) checks path suffix OR query_formats set — single predicate, no duplication"

requirements-completed: [QC-PARSER-FIX, QC-ROAD-COND-FIX, QC-HYDRO-XLSX-FIX, QC-BM25-HEALTH]

# Metrics
duration: 8min
completed: 2026-04-12
---

# Phase 16 Plan 05: Quebec Gap Closure Summary

**Fixed 4 UAT gaps: MTQ WFS CSV parser dispatch bug (4 tools), Hydro-Québec XLSX matcher, electricity envelope URL, ER wait times BM25 keywords**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-12T02:22:45Z
- **Completed:** 2026-04-12T02:30:50Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Extended `fetch_and_parse` to inspect `outputformat`/`format`/`f` query-string keys, fixing all 4 MTQ WFS CSV tools that were routing to `_parse_xlsx` and raising `BadZipFile` on CSV bytes
- Fixed `fetch_electricity_data` to accept XLSX/XLS resources (Hydro-Québec has zero CSV), skip empty-URL entries, return `(rows, source_url, was_cached)` 3-tuple, and raise `ValueError` on no parseable resource instead of silent `[]`
- Fixed `quebec_get_electricity_data` envelope: `_meta.source.url` now reflects the actual Hydro-Québec XLSX URL instead of the hardcoded `package_show` endpoint
- Added `health`, `medical`, `sante` to `quebec_get_er_wait_times` Keywords line for BM25 discoverability on "Quebec hospitals health" queries
- Removed exception swallow in `fetch_road_conditions` — errors now propagate to tool layer for structured `UPSTREAM_ERROR` responses

## Task Commits

Each task was committed atomically:

1. **Task 1: fix fetch_and_parse query-string format detection + road_conditions exception swallow** - `83b8a5b` (fix)
2. **Task 2: fix fetch_electricity_data XLSX matcher + envelope URL honesty** - `f90075e` (fix)
3. **Task 3: add health/medical/sante Keywords to ER wait times** - `5c371cb` (fix)
4. **Lint fix: remove pre-existing unused variable** - `61a59e3` (chore, Rule 1 auto-fix)

## Files Created/Modified

- `src/mcp_canada/shared/parsers.py` — Added `urllib.parse` query-string format detection to `fetch_and_parse`
- `src/mcp_canada/shared/__tests__/test_parsers.py` — Added 5 new `TestFetchAndParse` routing tests
- `src/mcp_canada/modules/quebec/client.py` — Removed exception swallow from `fetch_road_conditions`; rewrote `fetch_electricity_data` for XLSX support + 3-tuple return
- `src/mcp_canada/modules/quebec/tools.py` — Updated `quebec_get_electricity_data` to unpack 3-tuple and use `source_url`; added health/medical/sante keywords to `quebec_get_er_wait_times`; updated road_conditions Note docstring
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — Added `test_propagates_parser_exceptions_no_silent_swallow`; replaced 1 electricity test with 4 new tests; updated all electricity tests to 3-tuple contract; removed unused variable
- `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — Updated electricity tests to 3-tuple mock; added `TestQuebecGetElectricityDataEnvelope` + `TestQuebecGetErWaitTimesKeywords`
- `.planning/phases/16-quebec-government-open-data/16-RESEARCH.md` — Corrected LOW-confidence flag on `ms:conditions_routieres`; marked Hydro-Québec as XLSX-only; resolved open questions 1 and 2

## Decisions Made

- Used `urllib.parse.parse_qs` (stdlib) for query-string parsing — zero new dependencies
- Cache key uses `v2:` suffix for `fetch_electricity_data` to invalidate stale 2-tuple in-memory entries from old contract
- Tests use `patch.object(_mod, "cached_fetch", side_effect=passthrough)` to prevent aiocache cross-test pollution at default `limit=500`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Remove pre-existing unused variable in test_client.py**
- **Found during:** Task 2 verification (ruff lint)
- **Issue:** `original_cached_fetch = _mod.cached_fetch` at line 187 was assigned but never used (ruff F841)
- **Fix:** Removed the unused assignment
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_client.py`
- **Verification:** `uv run ruff check src/mcp_canada/modules/quebec/` passes
- **Committed in:** `61a59e3` (chore, separate from task commits)

---

**Total deviations:** 1 auto-fixed (Rule 1 - pre-existing lint bug)
**Impact on plan:** Trivial cleanup required for `ruff check` to pass. No scope creep.

## Issues Encountered

- **Cache isolation in electricity tests:** First attempt at adding new electricity tests without bypassing `cached_fetch` caused test-ordering failures (cache from first test leaked into second test via shared aiocache). Fixed by adding `patch.object(_mod, "cached_fetch", side_effect=passthrough)` in all 4 electricity client tests. This pattern was already established in `TestFetchRoadConditions` — just not applied to the original electricity test.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 4 UAT gaps closed; UAT tests 8/9/11/12 can be flipped from `issue` to `pass` manually
- `fetch_and_parse` query-string format detection is available for any future WFS-style module (Alberta, BC, etc.) without further changes
- Quebec module at 97.97% coverage — well above 95% floor

---
*Phase: 16-quebec-government-open-data*
*Completed: 2026-04-12*
