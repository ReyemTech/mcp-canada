---
phase: 12-ontario-government-open-data
plan: 01
subsystem: api
tags: [ckan, ontario, open-data, httpx, pydantic, aiocache, bilingual]

requires:
  - phase: 11-ircc-immigration
    provides: shared fetch_and_parse parser for XLSX files used by population projections

provides:
  - Ontario CKAN client layer with 6 public functions returning (data, was_cached) tuples
  - Ontario module skeleton with MODULE_NAME/MODULE_DESCRIPTION for FileSystemProvider auto-registration
  - Population projections fetch delegating to shared parsers.fetch_and_parse
  - Full unit test suite (39 tests) with mocked HTTP covering all client functions

affects: [12-ontario-government-open-data, tools-phase]

tech-stack:
  added: []
  patterns:
    - "Ontario mirrors federal CKAN pattern exactly: same helper functions, same caching, same rate limiting, 'ontario:' cache key prefix"
    - "async fake_cached_fetch pattern for testing: side_effect with async def returns raw result — cleaner than patching httpx directly"
    - "fetch_population_projections delegates entirely to shared fetch_and_parse with XLSX URL from constants — no CKAN call needed"

key-files:
  created:
    - src/mcp_canada/modules/ontario/__init__.py
    - src/mcp_canada/modules/ontario/constants.py
    - src/mcp_canada/modules/ontario/schemas.py
    - src/mcp_canada/modules/ontario/client.py
    - src/mcp_canada/modules/ontario/__tests__/__init__.py
    - src/mcp_canada/modules/ontario/__tests__/conftest.py
    - src/mcp_canada/modules/ontario/__tests__/test_client.py
  modified: []

key-decisions:
  - "ontario: cache key prefix distinguishes Ontario datasets from federal CKAN (ckan:) keys in shared aiocache"
  - "Population projections XLSX has no FR variant URL — lang parameter accepted for API consistency but uses same URL for both languages"
  - "async fake_cached_fetch side_effect pattern: side_effect=async def fake(key, ttl, fetcher): return data, False — avoids asyncio coroutine not awaited warnings from lambda pattern"

patterns-established:
  - "Ontario CKAN module mirrors federal ckan module: identical private helpers (_truncate, _limit_resources, _shape_resource, _shape_dataset, _build_cache_key, _api_get), different BASE_URL and 'ontario:' prefix"
  - "Curated dataset URLs in constants.py: POPULATION_PROJECTIONS_RESOURCE_URL as direct XLSX download link, fetched via fetch_and_parse not CKAN API"

requirements-completed: [ONT-01, ONT-02, ONT-03, ONT-04, ONT-05, ONT-06]

duration: 15min
completed: 2026-04-09
---

# Phase 12 Plan 01: Ontario Module Skeleton Summary

**Ontario CKAN client layer with 6 async functions, bilingual title/description extraction, population projections XLSX parser integration, and 39 unit tests**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-09T14:14:00Z
- **Completed:** 2026-04-09T14:29:26Z
- **Tasks:** 1
- **Files modified:** 7

## Accomplishments
- Ontario module created with MODULE_NAME="ontario" for automatic FileSystemProvider registration
- 6 public client functions all returning (data, was_cached) tuples using cached_fetch and get_limiter
- Bilingual shaping (_shape_dataset) with title_translated/notes_translated fallback chain
- Population projections delegates to shared parsers.fetch_and_parse with the Ministry of Finance XLSX URL
- 39 unit tests covering all helpers, all public functions, happy paths, 404 errors, and bilingual extraction

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Ontario module skeleton and CKAN client layer** - `e048080` (feat)

## Files Created/Modified
- `src/mcp_canada/modules/ontario/__init__.py` - MODULE_NAME, MODULE_DESCRIPTION for auto-registration
- `src/mcp_canada/modules/ontario/constants.py` - BASE_URL, rate limiting, cache TTLs, POPULATION_PROJECTIONS_RESOURCE_URL
- `src/mcp_canada/modules/ontario/schemas.py` - Flat Pydantic v2 models: Resource, DatasetSummary, DatasetDetail, Organization
- `src/mcp_canada/modules/ontario/client.py` - 6 public async client functions with full caching and rate limiting
- `src/mcp_canada/modules/ontario/__tests__/conftest.py` - Fixtures with Ontario CKAN sample API responses
- `src/mcp_canada/modules/ontario/__tests__/test_client.py` - 39 unit tests, all passing

## Decisions Made
- `ontario:` cache key prefix: distinguishes Ontario datasets from federal CKAN keys sharing the same aiocache instance
- Population projections XLSX has no FR variant — lang parameter accepted for API consistency, same URL used for both languages
- Used `async def fake_cached_fetch` pattern for async test mocking (avoids `lambda` coroutine-not-awaited runtime warnings)

## Deviations from Plan

**1. [Rule 1 - Bug] Fixed async mock side_effect pattern in tests**
- **Found during:** Task 1 (initial test run after GREEN implementation)
- **Issue:** `side_effect=lambda key, ttl, fetcher: fetcher()` returns a coroutine object without awaiting it, causing `TypeError: cannot unpack non-iterable coroutine object`
- **Fix:** Replaced all async test mocks with `async def fake_cached_fetch(key, ttl, fetcher): return result, False` pattern
- **Files modified:** src/mcp_canada/modules/ontario/__tests__/test_client.py
- **Verification:** All 39 tests pass; ruff + pyright clean

---

**Total deviations:** 1 auto-fixed (Rule 1 bug fix)
**Impact on plan:** Necessary correctness fix in test mocking pattern. No scope creep.

## Issues Encountered
- Unused import `make_mock_response` caught by ruff after switching to fake_cached_fetch pattern — removed in same pass

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ontario client layer complete; ready for Plan 12-02 (tools layer: ontario_search_datasets, ontario_get_dataset, ontario_list_organizations, ontario_get_resource, ontario_get_dataset_count, ontario_get_population_projections)
- Module will auto-register when server starts — no server.py changes needed

---
*Phase: 12-ontario-government-open-data*
*Completed: 2026-04-09*

## Self-Check: PASSED

- FOUND: src/mcp_canada/modules/ontario/__init__.py
- FOUND: src/mcp_canada/modules/ontario/constants.py
- FOUND: src/mcp_canada/modules/ontario/schemas.py
- FOUND: src/mcp_canada/modules/ontario/client.py
- FOUND: src/mcp_canada/modules/ontario/__tests__/test_client.py
- FOUND commit: e048080
