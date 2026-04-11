---
phase: 15-british-columbia-government-open-data
plan: 05
subsystem: api
tags: [british-columbia, ckan, wfs, bug-fix, bilingual, i18n, http, integration-tests]

requires:
  - phase: 15-british-columbia-government-open-data
    provides: BC module with CKAN discovery tools, WFS curated tools, prompts, resources

provides:
  - "_api_get in british_columbia/client.py treats shared api_get return as parsed dict — not httpx.Response"
  - "bc_get_water_wells 130K guard message localized via inline lang=='en' ternary"
  - "TestSharedApiGetContract — contract tests catching api_get return-type mismatches"
  - "BC integration suite: 0 failures (was 7 from _api_get blocker + 5 wrong test assertions)"

affects:
  - 15-british-columbia-government-open-data
  - any future CKAN module that calls shared api_get

tech-stack:
  added: []
  patterns:
    - "_api_get pattern: envelope = await api_get(...); check envelope.get('success'); return envelope.get('result', {})"
    - "Bilingual guard message: inline lang=='en' ternary before make_error call"
    - "Contract tests: AsyncMock returning raw dict (not MagicMock Response) verifies real shared api_get contract"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/british_columbia/client.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_client.py
    - src/mcp_canada/modules/british_columbia/tools.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_tools.py
    - tests/integration/test_tool_scenarios.py

key-decisions:
  - "BC _api_get: drop .raise_for_status()/.json() — shared api_get already returns parsed dict; only check CKAN envelope.get('success')"
  - "Water wells bilingual message: inline lang=='en' ternary (not t() import) — zero production t() imports make first import scope-creep; ternary matches prompts.py convention"
  - "Integration test fixes (Rule 1): wrong fire_year→year param, wrong data shape assertions (data.features not data list), wrong object_name→package_id for bc_query_features — pre-existing bugs exposed once CKAN blocker was cleared"
  - "No changes to shared/http.py — 5 other modules rely on parsed-JSON return contract"
  - "No systemic bilingual audit — 29 other make_error call sites are out of scope; this gap only required the single water wells guard message"

requirements-completed: [BC-CKAN-FIX, BC-I18N-FIX]

duration: 7min
completed: 2026-04-11
---

# Phase 15 Plan 05: BC Gap Closure Summary

**BC module CKAN tools unblocked by fixing _api_get dict-vs-Response contract mismatch; bc_get_water_wells guard bilingualized; integration suite drops from 7+5 failures to 0**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-11T04:17:38Z
- **Completed:** 2026-04-11T04:24:52Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Fixed root cause of UAT Gaps 1/2/3/5: `_api_get` in `client.py` called `.raise_for_status()` and `.json()` on the return value of `shared/http.py:api_get`, but `api_get` already returns parsed JSON (a dict). Every CKAN call raised `AttributeError: 'dict' object has no attribute 'raise_for_status'`. Fix: 4-line rewrite checking `envelope.get("success")` directly.
- Fixed UAT Gap 4: `bc_get_water_wells` guard message hardcoded in English. Added inline `lang == "en"` ternary with French translation `"bc_get_water_wells exige au moins un des paramètres city, well_class ou aquifer_id..."`. `make_error` is a pass-through builder — callers own localisation.
- Removed `_make_http_response` MagicMock helper from `test_client.py` (the root cause of why 22 unit tests masked the contract bug). All 22 tests now pass raw dicts directly to `AsyncMock(return_value=...)`.
- Added `TestSharedApiGetContract` class (3 tests) that would have caught the original bug pre-merge.
- Fixed 5 pre-existing integration test bugs (Rule 1): wrong `fire_year` param (→ `year`), wrong `data["data"]` list assertions (actual shape is `{"features": [...], "truncated": bool}`), wrong `object_name` param for `bc_query_features` (→ `package_id`).
- Integration suite: 11/11 BC tests pass (0 failures, was 7+5).

## Task Commits

1. **Task 1: Fix BC _api_get contract mismatch + rewrite test_client.py mock pattern** - `2125a92` (fix)
2. **Task 2: Bilingualize bc_get_water_wells 130K guard message** - `1f42468` (fix)

## Files Created/Modified

- `src/mcp_canada/modules/british_columbia/client.py` - `_api_get` rewritten to treat `api_get` return as parsed dict; drops `.raise_for_status()`/`.json()`; checks `envelope.get("success", False)` directly
- `src/mcp_canada/modules/british_columbia/__tests__/test_client.py` - `_make_http_response` helper removed; 22 existing tests migrated to raw-dict AsyncMock returns; `TestSharedApiGetContract` class added (3 contract tests)
- `src/mcp_canada/modules/british_columbia/tools.py` - `bc_get_water_wells` guard at line 700 uses inline `lang == "en"` ternary with French translation
- `src/mcp_canada/modules/british_columbia/__tests__/test_tools.py` - 2 new regression tests for bilingual guard (fr: asserts `"au moins un"` in message; en: sanity check)
- `tests/integration/test_tool_scenarios.py` - 5 pre-existing test bugs fixed: `fire_year`→`year`, `data["data"]` shape assertions, `object_name`→`package_id` for bc_query_features

## Decisions Made

- `_api_get` fix is minimum-diff: 4 lines changed. Drop `.raise_for_status()`/`.json()`, add `isinstance(envelope, dict)` guard before `envelope.get("success")`. HTTP-level errors are already raised inside `shared/http.py:_fetch()`.
- Bilingual ternary pattern (not `t()` import): zero production code currently imports `shared/i18n.py:t()`. First import for one guard message would establish a new precedent without the systemic audit needed to make it consistent. Inline ternary matches the established pattern across 7+ modules' `prompts.py` files.
- Integration test assertion fixes classified as Rule 1 (pre-existing bugs): the wrong parameter names and data shape assertions were silent before the CKAN blocker was fixed (CKAN tests were raising AttributeError before reaching any assertions). Once CKAN worked, these bugs became visible.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed 5 pre-existing integration test bugs exposed by CKAN fix**
- **Found during:** Task 1 (Step 6 — Run BC integration suite against live CKAN)
- **Issue:** After the CKAN blocker was resolved, 5 WFS integration tests failed due to wrong param names and wrong data shape assertions that were previously masked by the AttributeError (tests never reached assertions). Specifically: `fire_year` param doesn't exist (tool uses `year`); `data["data"]` assertions checked for list but actual response shape is `{"features": [...], "truncated": bool}`; `bc_query_features` called with `object_name` param (tool requires `package_id`).
- **Fix:** Updated `tests/integration/test_tool_scenarios.py` — 5 test methods corrected to use correct param names and match actual response shape.
- **Files modified:** `tests/integration/test_tool_scenarios.py`
- **Verification:** `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Bc` → 11/11 passed
- **Committed in:** `2125a92` (Task 1 commit, included as part of the integration fix)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** Pre-existing bugs in integration tests; fixing them was necessary to achieve the 0-failure integration target. No scope creep — only tests modified, not production code.

## Issues Encountered

- Initial `TestSharedApiGetContract` implementation used `"mcp_canada.shared.http.api_get"` as the patch path. Python's `from module import name` creates a local binding in `client.py`, so patching the source module doesn't intercept already-imported calls. Corrected to patch `"mcp_canada.modules.british_columbia.client.api_get"` (the local binding) while returning raw dicts — this achieves the same contract-verification goal.

## Non-Goals Honoured

- `shared/http.py` is byte-identical (git diff shows zero changes) — 5 other modules rely on its parsed-JSON return contract.
- No `shared/i18n.py:t()` import introduced — the inline ternary is the minimum-diff approach for one guard message.
- No audit of the other ~29 `make_error` call sites in `bc/tools.py` — systemic bilingual coverage belongs in a future dedicated phase.
- No changes to `README.md` or `CLAUDE.md` — purely internal bug fixes with zero user-facing API surface changes.

## UAT Status After Fix

All 5 gaps are now resolved:
1. Gap 1 (Test 2): `bc_search_datasets` returns BC datasets with `_meta.source.api == "bc-data-catalogue"` — PASS
2. Gap 2 (Test 3): `bc_get_dataset_details` surfaces `queryable_via_wfs` and `object_name` — PASS
3. Gap 3 (Test 9): `bc_query_features` routes WFS-queryable datasets to the WFS path — PASS
4. Gap 4 (Test 13): `bc_get_water_wells(lang="fr")` returns French error message with `"au moins un"` — PASS
5. Gap 5 (Test 14): Integration suite 0 failures (was 7+5) — PASS

Suggest: Update `.planning/phases/15-british-columbia-government-open-data/15-UAT.md` to reflect `status: complete` with `passed: 14, issues: 0`.

## Next Phase Readiness

- BC module is fully operational against live APIs.
- CKAN search/details/query path works end-to-end.
- WFS curated tools all functional.
- Bilingual error message pattern established for bc_get_water_wells guard.
- Ready to proceed to Quebec (Phase 16) or other provincial modules.

---
*Phase: 15-british-columbia-government-open-data*
*Completed: 2026-04-11*
