---
phase: 16-quebec-government-open-data
plan: 02
subsystem: api
tags: [ckan, quebec, fastmcp, pydantic, mcp-tools, discovery, tdd, phase15-lesson]

# Dependency graph
requires:
  - phase: 16-01
    provides: "Quebec module skeleton with 7 files, constants, schemas, Wave 0 test stubs"
  - phase: 15-british-columbia-government-open-data
    provides: "Post-15-05 _api_get dict-contract pattern (the ROOT CAUSE lesson)"
provides:
  - "src/mcp_canada/modules/quebec/client.py — _api_get, _datastore_get, 5 fetch_* functions (full bodies)"
  - "src/mcp_canada/modules/quebec/tools.py — 5 discovery @tool functions (quebec_search_datasets, quebec_get_dataset_details, quebec_query_dataset, quebec_list_organizations, quebec_list_categories)"
  - "TestSharedApiGetContract: 3 green contract tests verifying Phase 15 parsed-dict pattern"
  - "96% unit test coverage (tools.py 100%, full suite 96.44%)"
affects:
  - "16-03 (curated health/transport tools can now call _api_get, _datastore_get, fetch_dataset_details)"
  - "16-04 (environment/energy tools use same client pattern)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase 15 parsed-dict _api_get: api_get returns dict, NEVER call .raise_for_status()/.json()"
    - "_api_get returns Any (not dict[str, Any]) — organization_list/group_list return lists at result level"
    - "group_list for categories: DQ has 10 thematic groups (BC returned HTTP 403); tag_list has 4,200 noisy tags"
    - "fetch_query_dataset: datastore_active=True resources route to _datastore_get; else _pick_best_resource + fetch_and_parse"
    - "Cache isolation in tests: use passthrough_cached_fetch when testing multi-call flows with side_effect mocks"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/tools.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/modules/quebec/__tests__/test_tools.py
    - .planning/phases/16-quebec-government-open-data/16-VALIDATION.md

key-decisions:
  - "_api_get return type is Any (not dict[str, Any]): CKAN organization_list and group_list return lists at result level, not dicts — typing with dict triggers pyright errors on .get() calls in list comprehensions"
  - "Cache passthrough pattern in tests: when testing multi-step flows that span two cached_fetch calls (e.g. fetch_dataset_details + datastore_search in fetch_query_dataset), mock cached_fetch to always call the fetcher to avoid cache key collisions between tests"
  - "groups list uses str() cast: _flatten_dataset_summary groups comprehension needed str() to satisfy pyright's list[str] type for QuebecDatasetSummary.groups"

requirements-completed: []

# Metrics
duration: 24min
completed: 2026-04-11
---

# Phase 16 Plan 02: Quebec CKAN Discovery Layer Summary

**Quebec CKAN client with Phase 15 parsed-dict contract baked in from day 1 — 5 discovery tools registered via FileSystemProvider, 32 tests green, 96% coverage**

## Performance

- **Duration:** 24 min
- **Started:** 2026-04-11T20:59:46Z
- **Completed:** 2026-04-11T21:23:28Z
- **Tasks:** 2
- **Files modified:** 4 (plus 16-VALIDATION.md)

## Accomplishments

- Implemented `_api_get` with Phase 15 parsed-dict contract (NEVER `.raise_for_status()` or `.json()`) — baked in from day 1, no gap closure needed
- `_api_get` sends `DEFAULT_HEADERS` (User-Agent: mcp-canada/1.0) on every call to Données Québec
- `_api_get` returns `Any` (not `dict[str, Any]`) to handle both dict results (package_search/package_show) and list results (organization_list/group_list)
- `_datastore_get` wraps `datastore_search` with resource_id + params passthrough
- 5 `fetch_*` client functions: search_datasets, dataset_details, organizations, categories, query_dataset
- `fetch_categories` confirmed to use `group_list` (NOT `tag_list` — DQ has 10 thematic groups, tag_list returns 4,200 noisy tags)
- `fetch_query_dataset` routes `datastore_active=True` resources to `_datastore_get`, otherwise picks best file resource (CSV > GeoJSON > JSON > XLSX) via `_pick_best_resource` and calls `fetch_and_parse`
- 5 standalone `@tool` functions: `quebec_search_datasets`, `quebec_get_dataset_details`, `quebec_query_dataset`, `quebec_list_organizations`, `quebec_list_categories`
- All tools: `lang: Literal["en", "fr"] = "en"`, `make_response`/`make_error` envelope, `Use for:` + 8+ `Keywords:` docstrings, `quebec_` prefix
- Bilingual error messages use inline `lang == "en"` ternary (not `t()` import)
- `TestSharedApiGetContract`: 3 green tests patching `mcp_canada.modules.quebec.client.api_get` (local binding) — would have caught BC's pre-15-05 bug
- tools.py at 100% coverage; overall suite 96.44% (>95% threshold)
- `test_quality.py` green (BM25 Keywords quality)

## Task Commits

1. **Task 1: CKAN client implementation** - `6cd94ea` (feat)
2. **Task 2: 5 discovery tools** - `2d06d90` (feat)

## Files Modified

- `src/mcp_canada/modules/quebec/client.py` — full implementation (was 20 NotImplementedError stubs; Plan 02 stubs replaced with real bodies; Plan 03/04 stubs remain)
- `src/mcp_canada/modules/quebec/tools.py` — 5 discovery tools (was empty scaffold)
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — real test bodies for TestSharedApiGetContract + 6 Plan 02 client test classes (Plan 03/04 remain skipped)
- `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — real test bodies for 5 discovery tool classes (Plan 03/04 remain skipped)
- `.planning/phases/16-quebec-government-open-data/16-VALIDATION.md` — tasks 16-02-01/02/03 flipped to green

## Decisions Made

- `_api_get` return type changed from `dict[str, Any]` to `Any` — pyright flagged errors on `.get()` calls when result is a list (from `organization_list`/`group_list`). BC client has same pattern but uses looser typing; Quebec follows same approach.
- Cache isolation in TDD tests: `fetch_query_dataset` test that exercises both `package_show` + `datastore_search` paths required patching `cached_fetch` with a passthrough (always calls fetcher) to avoid aiocache storing the `package_show` result from a prior test under the same `"quebec:dataset:some-pkg"` key.
- `groups` list in `_flatten_dataset_summary` uses `str()` cast to satisfy `list[str]` type annotation on `QuebecDatasetSummary.groups`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Changed `_api_get` return type from `dict[str, Any]` to `Any`**
- **Found during:** Task 1 pyright verification
- **Issue:** Pyright reported 10 errors: `Attribute "get" unknown for class "str"` — because `organization_list` and `group_list` CKAN actions return a list at the result level, but the annotation `dict[str, Any]` told pyright to expect only dict
- **Fix:** Changed return type annotation to `Any`; the runtime `isinstance(result, list)` guard already handles both cases correctly
- **Files modified:** `src/mcp_canada/modules/quebec/client.py`
- **Commit:** `6cd94ea` (included in Task 1)

**2. [Rule 2 - Missing critical functionality] Added error path tests for coverage**
- **Found during:** Task 2 coverage check (94% < 95% threshold)
- **Issue:** The `UPSTREAM_ERROR` exception paths in all 5 tools and the `INVALID_INPUT` path in `quebec_get_dataset_details` were untested
- **Fix:** Added 8 additional test methods covering all error paths (httpx.HTTPStatusError in 4 tools, generic Exception in query_dataset, INVALID_INPUT in get_dataset_details)
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_tools.py`
- **Commit:** `2d06d90` (included in Task 2)

---

**Total deviations:** 2 auto-fixed (Rule 1 + Rule 2)
**Impact on plan:** Both necessary for correctness and coverage. No scope creep.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## Next Phase Readiness

- All Plan 02 client and tool functions implemented with real bodies
- Plan 03/04 stubs remain as `NotImplementedError` with breadcrumb comments
- 16-VALIDATION.md rows 16-02-01/02/03 flipped to green
- `_api_get` and `_datastore_get` are battle-tested for Plan 03 curated tools to reuse directly

---
*Phase: 16-quebec-government-open-data*
*Completed: 2026-04-11*
