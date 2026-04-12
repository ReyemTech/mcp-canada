---
phase: 16-quebec-government-open-data
verified: 2026-04-12T04:30:00Z
status: passed
score: 17/17 must-haves verified (14 original + 2 cycle-3 closures + 1 cycle-4 closure)
re_verification:
  previous_status: passed
  previous_score: 16/16
  cycle: 4
  gap_closure_plan: 16-08
  commits_verified:
    - d30d3a9  # test(16-08): add failing test for route filter substring match bug
    - 2768478  # fix(16-08): remove nom_route substring fallback — exact num_route match only
    - bcea3af  # test(16-08): tighten integration test to reject Route 204 in A-20 results
  gaps_closed:
    - "Test 8 (final): route='A-20' filter no longer returns Route 204 bridges — nom_route substring fallback removed entirely, exact num_route match only"
  gaps_remaining: []
  regressions: []
---

# Phase 16: Quebec Government Open Data Verification Report (Re-verification Cycle 4)

**Phase Goal:** Add Quebec provincial open data to mcp-canada via Donnees Quebec CKAN catalogue. Deliver 5 discovery + 13 curated = 18 `quebec_` tools covering Health/MSSS, Transport/MTQ, Environment/MELCCFP, Demographics/ISQ, Energy/Hydro-Quebec, Forest/MFFP. 6 bilingual prompts + 7 zero-parameter resources. Full 7-file module pattern. Bilingual/BM25/envelope compliance. README + CLAUDE.md updates. >=95% coverage. Phase 15 lessons applied from day 1.

**Re-verified:** 2026-04-12 (post-16-08 gap closure cycle 4)
**Status:** PASSED
**Previous status:** PASSED (16/16 at cycle 3; UAT retest 3 flagged 1 remaining route substring bug in Test 8)
**Re-verification mode:** Cycle 4 -- focused on 16-08 must-have (exact route match) + regression check on all prior cycles

---

## Gap Closure Summary (Cycles 1-4)

| Cycle | Plan | UAT Tests Fixed | Status |
|-------|------|-----------------|--------|
| 1 | 16-05 | Test 12 (BM25 `quebec_get_er_wait_times` keywords: added health/medical/sante) | CLOSED in cycle 1, REGRESSION-FREE in cycle 4 |
| 2 | 16-06 | Test 9 (`fetch_road_conditions` snake_case keys `numeroroute`), WFS paging, Hydro-Quebec TLS SECLEVEL=1 | CLOSED in cycle 2, REGRESSION-FREE in cycle 4 |
| 3 | 16-07 | Test 8 partial (bridge Pydantic int->str via `_str_or_none`), Test 11 (electricity XLSX legend row filter) | CLOSED in cycle 3, REGRESSION-FREE in cycle 4 |
| 4 | 16-08 | Test 8 final (route='A-20' substring match returning Route 204 bridges) | CLOSED THIS CYCLE |

---

## Cycle 4 Observable Truth (16-08 must_have)

| # | Truth (from 16-08 PLAN) | Status | Evidence |
|---|--------------------------|--------|----------|
| 20 | `fetch_bridge_structures(route='A-20')` uses exact normalized `num_route` match only -- no `nom_route` substring fallback that would let Route 204 leak through | VERIFIED | client.py:698-702 shows the filter is now `if num != norm: continue` with no `nom_route` fallback. Git diff `397cf4f..bcea3af -- client.py` confirms removal of 3 lines (`nom = ...`, `raw_digits = ...`, `and raw_digits not in nom`). Unit test `TestQuebecBridgeRouteSubstringFix::test_a20_excludes_route_204` passes with mixed fixture containing both A-20 and Route 204 rows. |

**Cycle 4 score:** 1/1 new must-have verified.

---

## Regression Check -- All 16 Previous Must-Haves

| # | Truth | Status | Regression Evidence |
|---|-------|--------|---------------------|
| 1 | Quebec module registers with 7-file pattern | VERIFIED (unchanged) | 7 files present; no module structure changes in 16-08 |
| 2 | Exactly 18 `quebec_` tools | VERIFIED (unchanged) | `len(tools.__all__) == 18` confirmed |
| 3 | 6 bilingual prompts registered | VERIFIED (unchanged) | `len(prompts.__all__) == 6` confirmed |
| 4 | 7 zero-parameter resources registered | VERIFIED (unchanged) | `len(resources.__all__) == 7` confirmed |
| 5 | `_api_get` parsed-dict contract | VERIFIED (unchanged) | Not touched by 16-08 diff |
| 6 | `TestSharedApiGetContract` test class | VERIFIED (unchanged) | Not touched |
| 7 | `User-Agent` header sent in CKAN requests | VERIFIED (unchanged) | `constants.py` unchanged |
| 8 | Inline bilingual ternary pattern | VERIFIED (unchanged) | `tools.py` not touched |
| 9 | `fetch_categories` uses `group_list` | VERIFIED (unchanged) | Not touched |
| 10 | Integration test classes populated | VERIFIED + ENHANCED | 2 new tests added by 16-08 |
| 11 | SOPFEU replaced with `quebec_get_forest_fires_history` | VERIFIED (unchanged) | Not touched |
| 12 | Hydro-Quebec `quebec_get_electricity_data` | VERIFIED (unchanged) | Not touched by 16-08 |
| 13 | README has Quebec section + tool count (193) | VERIFIED (unchanged) | README not in 16-08 diff |
| 14 | >=95% test coverage | VERIFIED | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` -> **96.59%** (2076 passed, 2 skipped). Previous: 96.58% / 2074 tests. +2 tests from 16-08. |
| 15-19 | Cycle 3 must-haves (bridge int->str coercion, electricity legend row filter) | VERIFIED (unchanged) | `_str_or_none` at client.py:356, `_is_real_electricity_row` at client.py:813, both untouched by 16-08 |

**Additional cycle 1-2 fixes (regression check):**

| Cycle 1-2 Fix | Status | Evidence |
|----------------|--------|----------|
| 16-05: `quebec_get_er_wait_times` BM25 keywords (Test 12) | INTACT | `tools.py:291` unchanged |
| 16-06: `fetch_road_conditions` snake_case mapper keys (Test 9) | INTACT | `client.py:536` still uses `r.get("numeroroute")` |
| 16-06: WFS paging loop for `fetch_bridge_structures` | INTACT | While loop with `count=500&startIndex=...` unchanged |
| 16-06: `_normalize_route` helper | INTACT | `client.py:617` unchanged |
| 16-06: Hydro-Quebec SECLEVEL=1 SSLContext | INTACT | `client.py:870` unchanged |

**Regression score:** 16/16 previous truths still hold. No regression.

---

## Required Artifacts (Cycle 4 Changes)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/modules/quebec/client.py` -- route filter (lines 698-702) | Exact `num_route` match only; no `nom_route` fallback | VERIFIED | `if num != norm: continue` -- three lines of substring fallback removed |
| `src/mcp_canada/modules/quebec/__tests__/test_client.py` -- `TestQuebecBridgeRouteSubstringFix` | Mixed fixture with A-20 and Route 204 rows; bidirectional exclusion tests | VERIFIED | Class at line 905 with `test_a20_excludes_route_204` and `test_route_204_excludes_a20` |
| `tests/integration/test_tool_scenarios.py` -- Route 204 rejection assertions | Explicit `route_num != '00204'` check in A-20 integration test | VERIFIED | 7 lines added to `test_bridges_route_filter_row_types` |

---

## Key Link Verification (Cycle 4)

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `fetch_bridge_structures` filter | `_normalize_route` | `num = _normalize_route(str(num_raw))` at client.py:700 | VERIFIED | Exact match comparison `num != norm`; no secondary path |
| Unit test `test_a20_excludes_route_204` | `fetch_bridge_structures` | Mock fetch returning mixed A-20 + Route 204 rows | VERIFIED | Asserts only A-20 rows returned, Route 204 excluded |
| Integration test rejection assertion | `quebec_get_bridge_structures` tool | Via MCP `call_tool` with `route="A-20"` | VERIFIED | Asserts `route_num != '00204'` for every returned row |

---

## Scope Boundary Enforcement (Cycle 4)

| Constraint | Expected | Actual | Status |
|------------|----------|--------|--------|
| Files modified (code) | Exactly 3 | `client.py`, `__tests__/test_client.py`, `test_tool_scenarios.py` | MATCHES |
| `src/mcp_canada/shared/parsers.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/schemas.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/tools.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/prompts.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/resources.py` NOT touched | No edits | Not in diff | SATISFIED |
| `README.md` NOT touched | No edits | Not in diff | SATISFIED |

**No out-of-scope edits.** Cycle 4 is strictly scoped to the route filter fix.

---

## Requirements Coverage

| Requirement ID | Source Plan | Description | Status | Evidence |
|----------------|-------------|-------------|--------|----------|
| QC-BRIDGE-ROUTE-SUBSTRING-FIX | 16-08 | `route='A-20'` must not return Route 204 bridges via substring match | SATISFIED | Substring fallback removed; exact `num_route` match only; unit + integration tests |
| QC-BRIDGES-INT-STR-COERCION | 16-07 | Bridge mapper must not fail Pydantic validation for int-valued CSV ID cells | REGRESSION-FREE | `_str_or_none` helper intact |
| QC-ELECTRICITY-LEGEND-ROW | 16-07 | `fetch_electricity_data` must skip XLSX formula legend row | REGRESSION-FREE | `_is_real_electricity_row` filter intact |
| (prior cycles) 16-05, 16-06 | 16-05, 16-06 | Road conditions mapper, ER wait BM25 keywords, WFS paging, SECLEVEL=1 TLS | REGRESSION-FREE | All fixes verified intact |

---

## Anti-Patterns Found (Cycle 4)

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | -- | -- | -- | Cycle 4 removed 3 lines of dead code and added 2 test classes. No TODO/FIXME/stub patterns introduced. |

Pre-existing pytest warnings on two test methods incorrectly marked `@pytest.mark.asyncio` on non-async functions are inherited from earlier cycles and not part of 16-08 scope.

---

## Verification Commands Run

| Check | Command | Result |
|-------|---------|--------|
| Quebec unit suite | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ -q --tb=no` | 151 passed, 2 warnings (pre-existing) |
| Full suite + coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q --tb=no` | **2076 passed, 2 skipped, 96.59% coverage** |
| Git scope diff | `git diff 397cf4f..bcea3af -- src/mcp_canada/shared/parsers.py src/mcp_canada/modules/quebec/schemas.py README.md` | Empty (no out-of-scope edits) |
| Commit verification | `git show d30d3a9 --stat && git show 2768478 --stat && git show bcea3af --stat` | 3 commits match 16-08 SUMMARY claims |
| Tool/prompt/resource counts | Python import check | 18 tools, 6 prompts, 7 resources |

---

## Human Verification Required

| # | Test | Expected | Why Human |
|---|------|----------|-----------|
| 1 | Run UAT retest 4 against live MTQ WFS endpoint: `uv run pytest tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios::test_bridges_route_filter_row_types -m integration --timeout=120` | A-20 query returns only Autoroute 20 bridges; no `route_num == '00204'` rows | Live WFS data may contain edge cases not covered by fixtures |

---

## Summary

**Gap closure cycle 4 (Plan 16-08) achieved its goal.**

The final UAT retest 3 defect -- Test 8 route filter substring match bug where `route='A-20'` returned Route 204 bridges via `nom_route` fallback -- is closed. The fix removed the `nom_route` substring fallback entirely (3 lines deleted from client.py), leaving only the exact zero-padded `num_route` comparison path. This is the correct design because `_normalize_route` already handles all user input formats (`A-20`, `a20`, `20`, `0020`).

**All 4 gap closure cycles are now complete:**
- Cycle 1 (16-05): BM25 keywords for ER wait times -- CLOSED
- Cycle 2 (16-06): Road conditions snake_case, WFS paging, SECLEVEL=1 -- CLOSED
- Cycle 3 (16-07): Bridge int->str coercion, electricity legend row -- CLOSED
- Cycle 4 (16-08): Route filter substring match -- CLOSED

**No regressions:** All 16 previous must-haves hold. Coverage at 96.59% (above 95% threshold). 2076 tests passing. Ruff clean.

**Phase 16 readiness:** All known UAT defects are resolved. Phase 16 is ready for final UAT retest and phase completion marking.

**Final score: 17/17 must-haves verified (14 original + 3 gap closure truths across cycles 3-4).**

---

_Re-verified: 2026-04-12 (cycle 4)_
_Verifier: Claude (gsd-verifier)_
_Previous verification: 2026-04-12 (cycle 3, 16/16 passed)_
