---
phase: 08-statcan-wds
plan: 01
subsystem: api
tags: [statcan, wds, bm25, pydantic, cache, rate-limiter, httpx]

# Dependency graph
requires:
  - phase: 07-datastore-ssl
    provides: _make_statcan_client() stub, STATCAN_VERIFY constant, TokenBucket rate limiter, cached_fetch shared utility

provides:
  - constants.py with CACHE_TTL_CUBES/META/CODESETS/OBS, FREQUENCY_CODES, SCALAR_FACTOR_CODES, _API_NAME
  - schemas.py with CubeLite, CubeMetadata, Dimension, DimensionMember, SeriesInfo, ObservationRow, CodeSetEntry, CodeSets
  - client.py with search_cubes (BM25), get_cube_metadata, get_code_sets, pad_coordinate, _unwrap, _limiter_acquire
  - conftest.py with WDS response fixtures for all endpoints
  - 27 unit tests covering all schemas, helpers, and client functions

affects:
  - 08-02 (getSeriesInfoFromCubePidCoord, getDataFromCubePidCoordAndLatestNPeriods depend on pad_coordinate, schemas, cache)
  - 08-03 (tools.py depends on all 3 client functions)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - BM25 Okapi scoring (k1=1.2, b=0.75) over cube title + subject + survey code fields
    - _unwrap() pattern for WDS SUCCESS/FAILED envelopes (list or dict)
    - _limiter_acquire() module-level async function to allow patch.object in tests
    - cached_fetch with tiered TTLs (1hr/24hr/7d) per endpoint category

key-files:
  created:
    - src/mcp_canada/modules/statcan/schemas.py
    - src/mcp_canada/modules/statcan/__tests__/conftest.py
    - src/mcp_canada/modules/statcan/__tests__/test_client.py
  modified:
    - src/mcp_canada/modules/statcan/constants.py
    - src/mcp_canada/modules/statcan/client.py

key-decisions:
  - "_limiter_acquire() is a module-level function (not inline in fetcher closures) so tests can patch.object without re-importing"
  - "BM25 index (avg_dl, df) stored as single cached tuple with cube list — avoids recomputing statistics on cache hit"
  - "Cache clear fixture uses mcp_canada.shared.cache._cache directly — ensures test isolation against the actual singleton"

patterns-established:
  - "pad_coordinate: split on '.', pad with '0' to 10 parts, truncate to 10, rejoin"
  - "_unwrap: list → take [0], check status == SUCCESS, return object; raise ValueError on FAILED"
  - "All WDS client functions return (data, was_cached) tuples"

requirements-completed: [SC-01, SC-02, SC-03, INF-02, INF-03]

# Metrics
duration: 4min
completed: 2026-04-07
---

# Phase 08 Plan 01: StatCan WDS Client Foundation Summary

**Okapi BM25 cube search over 80K+ entries plus getCubeMetadata and getCodeSets with tiered TTL caching (1hr/24hr/7d) and per-request rate limiting**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-07T18:51:12Z
- **Completed:** 2026-04-07T18:55:25Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- BM25 search infrastructure (`_build_doc_tokens`, `_build_search_index`, `_bm25_score`) over cubeTitleEn + cubeTitleFr + subjectCode + surveyCode
- `search_cubes()` lazily loads and caches the full cube list; stores (cubes, avg_dl, df) as a single cache entry to avoid recomputing statistics on hit
- `get_cube_metadata()` POSTs to getCubeMetadata, unwraps WDS envelope, flattens to `CubeMetadata` with decoded frequency
- `get_code_sets()` GETs getCodeSets, decodes all 6 code categories to `CodeSets` with 7-day TTL
- `pad_coordinate()` and `_unwrap()` helpers; `_limiter_acquire()` wrapper enabling clean mock in tests

## Task Commits

1. **Tasks 1 + 2: Foundation + client functions** - `ea7611f` (feat)

**Plan metadata:** (created with this summary)

_Note: Both tasks combined in single TDD cycle — all schemas were required for client function signatures_

## Files Created/Modified
- `src/mcp_canada/modules/statcan/constants.py` — Added TTL constants, FREQUENCY_CODES, SCALAR_FACTOR_CODES, _API_NAME
- `src/mcp_canada/modules/statcan/schemas.py` — CubeLite, CubeMetadata, Dimension, DimensionMember, SeriesInfo, ObservationRow, CodeSetEntry, CodeSets
- `src/mcp_canada/modules/statcan/client.py` — All helpers + 3 client functions; replaced stub
- `src/mcp_canada/modules/statcan/__tests__/conftest.py` — WDS response fixtures + autouse cache reset
- `src/mcp_canada/modules/statcan/__tests__/test_client.py` — 27 unit tests

## Decisions Made
- `_limiter_acquire()` extracted as module-level function to enable `patch.object(statcan_client, "_limiter_acquire")` in tests without re-importing the module
- BM25 index stored as a tuple `(cubes, avg_dl, df)` inside the cache — computing statistics on cache miss, unpacking on hit — avoids storing redundant data
- Cache isolation in conftest targets `mcp_canada.shared.cache._cache` directly (the singleton instance), not a fresh `SimpleMemoryCache()` which would be a different object

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused SCALAR_FACTOR_CODES import from client.py**
- **Found during:** Task 2 verification (ruff check)
- **Issue:** `SCALAR_FACTOR_CODES` imported in client.py but not used — ruff F401
- **Fix:** Removed the import; SCALAR_FACTOR_CODES is used only in schemas.py tests via constants import
- **Files modified:** src/mcp_canada/modules/statcan/client.py
- **Verification:** `ruff check` passes, all 27 tests still pass
- **Committed in:** ea7611f

---

**Total deviations:** 1 auto-fixed (1 unused import)
**Impact on plan:** Trivial linting fix, no scope change.

## Issues Encountered
- Cache isolation test failure when tests run in sequence: `autouse` fixture was creating a new `SimpleMemoryCache()` instance rather than clearing the actual module-level `_cache` singleton. Fixed by importing `_cache` from `mcp_canada.shared.cache` directly in the fixture.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All schemas, helpers, and discovery/metadata client functions are ready
- Plan 02 can implement `getSeriesInfoFromCubePidCoord` and `getDataFromCubePidCoordAndLatestNPeriods` using `pad_coordinate`, `_unwrap`, and the existing schemas
- Plan 03 can build tools.py using all 3 client functions
