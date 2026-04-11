---
phase: 16-quebec-government-open-data
plan: 03
subsystem: api
tags: [ckan, quebec, fastmcp, pydantic, mcp-tools, health, transport, mtq, msss, tdd]

# Dependency graph
requires:
  - phase: 16-02
    provides: "_api_get, _datastore_get, fetch_dataset_details — battle-tested from Plan 02"
provides:
  - "src/mcp_canada/modules/quebec/client.py — 7 new curated client functions (full bodies)"
  - "src/mcp_canada/modules/quebec/tools.py — 7 curated @tool functions (12 total Quebec tools)"
  - "49 new unit tests (18 client + 31 tools) — all green, RED→GREEN TDD"
  - "98.15% coverage on quebec module (>95% threshold)"
affects:
  - "16-04 (environment/energy tools reuse same client helpers)"
  - "README.md — Quebec section added, tool count updated to 187"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MSSS datastore filter: json.dumps({'CLSC': 'Oui'}) as params['filters'] — standard CKAN datastore filter format"
    - "MTQ WFS CSV bilingual: select descriptionFrancais/descriptionAnglais by lang param in _flatten_road_work"
    - "Bridge structures required-filter guard: not any([route, municipality, region]) in tool layer (not client)"
    - "fetch_road_conditions graceful error: try/except Exception in inner _fetch, returns [] on WFS failure"
    - "cached_fetch passthrough pattern for error tests: patch cached_fetch with always-calls-fetcher lambda"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/tools.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/modules/quebec/__tests__/test_tools.py
    - .planning/phases/16-quebec-government-open-data/16-VALIDATION.md
    - README.md

key-decisions:
  - "Filter guard stays in tool layer only (not client): client.fetch_bridge_structures can be called without filters; tool enforces the guard — this allows client reuse from fetch_query_dataset path"
  - "fetch_road_conditions returns [] on exception: LOW-confidence WFS endpoint (research flag) — graceful degradation preferred over raising UPSTREAM_ERROR on tool always-available pattern"
  - "cached_fetch passthrough in error tests: aiocache stores results from prior test runs under same cache key, so error tests that need a fresh _fetch call require patching cached_fetch to bypass caching"
  - "Tool count update: 175 + 12 (Plan 02 5 + Plan 03 7) = 187; provincial APIs count: 2 + 1 (Quebec) = 3"

requirements-completed: []

# Metrics
duration: 39min
completed: 2026-04-11
---

# Phase 16 Plan 03: Quebec Health + Transport Curated Tools Summary

**7 curated Quebec tools implemented with MSSS datastore and MTQ WFS CSV patterns — 12 of 18 total Quebec tools delivered, 98% coverage, bilingual guard on bridge structures filter**

## Performance

- **Duration:** 39 min
- **Started:** 2026-04-11T22:01:37Z
- **Completed:** 2026-04-11T22:40:17Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Implemented 7 client functions replacing Plan 03 `NotImplementedError` stubs:
  - `fetch_health_installations`: MSSS datastore with CLSC/CHSGS/CHSLD/CHPSY filter via `json.dumps({"CLSC": "Oui"})`
  - `fetch_er_wait_times`: MSSS hourly ER situation, 116 rows, optional full-text `q=` filter
  - `fetch_population_by_municipality`: MAMH MUN.csv via `fetch_and_parse`, post-parse `regadm` filter
  - `fetch_road_conditions`: MTQ WFS CSV with bilingual EN/FR column selection, graceful empty on exception
  - `fetch_road_works`: MTQ chantiers_mtmdet CSV, bilingual `descriptionFrancais`/`descriptionAnglais`
  - `fetch_road_events`: MTQ evenements CSV (French-only columns)
  - `fetch_bridge_structures`: MTQ gsq_v_desc_strct_tri CSV, post-parse route/municipality/region filters
- Added 7 `@tool` functions extending Plan 02's 5 to 12 total Quebec tools
- Bridge structures guard: `not any([route, municipality, region])` → bilingual INVALID_INPUT (BC water wells pattern)
- Health installations invalid type: bilingual INVALID_INPUT listing CLSC/CHSGS/CHSLD/CHPSY
- All tools: `lang: Literal["en", "fr"] = "en"`, inline ternary bilingual errors (no `t()` import), `Use for:` + 8+ `Keywords:` per BM25 contract
- 49 new unit tests: 18 client + 31 tools, all RED→GREEN TDD
- 98.15% coverage on quebec module (threshold 95%)
- `test_quality.py` green (BM25 docstring quality enforced)
- `pyright` green (0 errors)
- README updated: Quebec section added (12 tools), tool count 175 → 187, provincial APIs 2 → 3
- 16-VALIDATION.md: rows 16-03-01/02 flipped to green

## Task Commits

1. **Task 1: 7 Health/MTQ client functions** - `29f3401` (feat)
2. **Task 2: 7 curated @tool functions** - `7699f72` (feat)

## Files Modified

- `src/mcp_canada/modules/quebec/client.py` — 7 stub NotImplementedError bodies replaced with real implementations; imports extended with Plan 03 constants + schemas
- `src/mcp_canada/modules/quebec/tools.py` — 7 curated tools added (Plan 02's 5 + Plan 03's 7 = 12 total); `__all__` extended; `_MTQ_WFS_API_URL` and `_MAMH_CSV_URL` constants added
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — 18 real test bodies (Plan 03 skips replaced); cached_fetch passthrough pattern for error tests
- `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — 31 real test bodies (Plan 03 skips replaced); bilingual error tests for health + bridge guards
- `.planning/phases/16-quebec-government-open-data/16-VALIDATION.md` — tasks 16-03-01/02 flipped to green
- `README.md` — Quebec section (12 tools), tool count 175 → 187, provincial APIs 2 → 3

## Decisions Made

- Filter guard in tool layer (not client): `fetch_bridge_structures` can be called without filters; the `@tool` enforces the guard. This allows `fetch_query_dataset` and other client-level callers to use the function freely.
- `fetch_road_conditions` returns `[]` on WFS exception: research flagged LOW confidence on `ms:conditions_routieres` typename. Graceful empty is better than always-UPSTREAM_ERROR for a seasonally-variable endpoint.
- `cached_fetch` passthrough in error path tests: `aiocache` stores results from prior test runs under the same cache key (e.g., `"quebec:mtq:road_cond:en"`), so error tests that need the inner `_fetch` to be called must patch `cached_fetch` with a passthrough to bypass the cache.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed cache key collision in `test_returns_empty_on_parse_error`**
- **Found during:** Task 1 GREEN verification
- **Issue:** `test_parses_conditions_csv` (lang="en") ran first and cached results under `"quebec:mtq:road_cond:en"`. Then `test_returns_empty_on_parse_error` (also lang="en" default) hit the cache and got the previous result, bypassing the mocked exception entirely.
- **Fix:** Added a `cached_fetch` passthrough mock in the error test so the inner `_fetch` function always executes. Pattern consistent with `fetch_query_dataset` tests from Plan 02.
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_client.py`
- **Commit:** `29f3401` (included in Task 1)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Test isolation fix only. No scope creep.

## Issues Encountered

None beyond the test isolation bug documented above.

## Next Phase Readiness

- All Plan 03 client and tool functions implemented with real bodies
- Plan 04 stubs remain as `NotImplementedError` with breadcrumb comments
- 16-VALIDATION.md rows 16-03-01/02 flipped to green
- 12 of 18 Quebec tools complete (5 discovery from Plan 02 + 7 curated here)
- Plan 04 target: 6 environment/energy tools + 6 prompts + 7 resources

---

## Self-Check: PASSED

- `src/mcp_canada/modules/quebec/client.py` — FOUND
- `src/mcp_canada/modules/quebec/tools.py` — FOUND
- `.planning/phases/16-quebec-government-open-data/16-03-SUMMARY.md` — FOUND
- Commit `29f3401` (feat: 7 client functions) — FOUND
- Commit `7699f72` (feat: 7 curated tools) — FOUND
- 98.15% coverage threshold (95%) — PASSED
- `pyright` — 0 errors
- `test_quality.py` — green
