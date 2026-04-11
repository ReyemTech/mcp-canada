---
phase: 15-british-columbia-government-open-data
plan: 05
verified: 2026-04-11T05:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 15 Plan 05: BC Gap Closure Verification Report

**Phase Goal:** Close all 5 UAT gaps diagnosed in 15-UAT.md — unblock CKAN-dependent tools by fixing `_api_get` contract mismatch (Gaps 1/2/3/5) and bilingualize `bc_get_water_wells` guard message (Gap 4).
**Verified:** 2026-04-11T05:00:00Z
**Status:** passed
**Re-verification:** No — initial verification of plan 05 gap closure

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `bc_search_datasets` returns BC datasets (no `raise_for_status` error) | VERIFIED | `_api_get` rewritten — `envelope = await api_get(...)` checked via `envelope.get("success")` directly; 11/11 integration tests pass including `test_search_finds_wildfire_data` |
| 2 | `bc_get_dataset_details` returns `queryable_via_wfs` + `object_name` | VERIFIED | Same `_api_get` fix resolves the cascade; integration `test_query_features_routes_to_wfs` exercises the full `fetch_dataset_details` → WFS routing path and passes |
| 3 | `bc_query_features` routes WFS-queryable datasets to WFS path and returns features | VERIFIED | Integration tests `test_query_features_routes_to_wfs` and `test_query_features_routes_to_file_parser` both pass |
| 4 | `bc_get_water_wells(lang='fr')` with no filter returns French error message containing `"au moins un"` | VERIFIED | `tools.py:700-708` uses inline `lang == "en"` ternary; `test_guard_returns_french_message_when_lang_fr` asserts `"au moins un" in error.message` and `"at least one" not in error.message` |
| 5 | Integration suite `pytest tests/integration/ -v -m integration --timeout=120 -k Bc` reports 0 failures | VERIFIED | Live run: 11 passed, 230 deselected, 3.70s — 0 failures (was 7 pre-fix) |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/modules/british_columbia/client.py` | `_api_get` treats `api_get` return as dict; contains `envelope.get("success"` | VERIFIED | Lines 55-77: `envelope = await api_get(url, params or {})`; `envelope.get("success", False)` check present; no `.raise_for_status()` or `.json()` calls |
| `src/mcp_canada/modules/british_columbia/tools.py` | `bc_get_water_wells` guard uses `lang == "en"` ternary; contains `"au moins un"` | VERIFIED | Lines 700-708: ternary present with exact French text `"au moins un des paramètres city, well_class ou aquifer_id"` |
| `src/mcp_canada/modules/british_columbia/__tests__/test_client.py` | `TestSharedApiGetContract` class patching `mcp_canada.modules.british_columbia.client.api_get` with raw dict returns | VERIFIED | Lines 640-692: class with 3 tests; all patch `mcp_canada.modules.british_columbia.client.api_get` with `AsyncMock(return_value=<dict>)`; `_make_http_response` helper deleted (confirmed by comment at line 23-24 and absence of `raise_for_status` in non-comment test code) |
| `src/mcp_canada/modules/british_columbia/__tests__/test_tools.py` | Regression tests asserting French guard message contains `"au moins un"` | VERIFIED | Lines 928-949: `test_guard_returns_french_message_when_lang_fr` and `test_guard_returns_english_message_when_lang_en` — both assertions present and correct |

### Artifact Depth Check

**Level 1 — Exists:** All 4 artifacts present.

**Level 2 — Substantive (not stub):**

- `client.py:_api_get`: 6-line real implementation, not a stub — checks `isinstance(envelope, dict)`, guards `envelope.get("success", False)`, raises a real `httpx.HTTPStatusError`, returns `envelope.get("result", {})`.
- `tools.py` guard: Ternary selects between two full-text message strings; `make_error` call uses the local `message` variable.
- `test_client.py:TestSharedApiGetContract`: 3 tests each with real assertions — list shape check, dict key presence, `pytest.raises(httpx.HTTPStatusError)` for the failure path.
- `test_tools.py` regression tests: Calls `bc_get_water_wells(lang="fr")` with no args; asserts `error.code`, `error.lang`, positive French substring, negative English substring.

**Level 3 — Wired:**

- `_api_get` is wired: imported `api_get` from `mcp_canada.shared.http` at line 19; called at line 70 as `envelope = await api_get(url, params or {})`.
- `tools.py` guard is wired: `make_error` called at line 708 with the pre-localised `message` variable; `lang` parameter propagated correctly.
- Contract tests are wired: `TestSharedApiGetContract` patches fire the local `client.api_get` binding and exercise the real `_api_get` code path.

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `client.py:_api_get` | `shared/http.py:api_get` | `envelope = await api_get(url, params or {})` — result treated as dict | WIRED | Line 70: assignment without `.raise_for_status()`/`.json()`; `envelope.get("success")` at line 71 confirms dict treatment |
| `tools.py:bc_get_water_wells guard` | `shared/envelope.py:make_error` | Pre-localised `message` via `lang == "en"` ternary, then `make_error("INVALID_INPUT", message, lang=lang)` | WIRED | Lines 701-708 implement the ternary and pass `message` to `make_error` |
| `test_client.py:TestSharedApiGetContract` | `shared/http.py:api_get` (via local binding) | `patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=<dict>))` | WIRED | Patching the local `client.api_get` binding (imported via `from mcp_canada.shared.http import api_get`) achieves identical contract verification — raw dict return exercises the same `_api_get` code path that would fail against the old `Response` expectation |

**Note on patch path:** The plan specified `mcp_canada.shared.http.api_get` as the patch target, but the implementation correctly patches `mcp_canada.modules.british_columbia.client.api_get` (the local module binding). This is the standard Python mock pattern when `from X import Y` creates a local binding — patching the source module would not intercept calls through the already-imported name. The SUMMARY documents this as a deliberate correction (Issues Encountered section). The contract goal — raw dict returns caught by the new `_api_get` implementation — is fully achieved.

---

### Scope Discipline Checks

| Check | Status | Evidence |
|-------|--------|---------|
| `shared/http.py` byte-identical (no modifications) | VERIFIED | `git diff HEAD -- src/mcp_canada/shared/http.py` produces no output |
| `README.md` unchanged | VERIFIED | `git diff HEAD -- README.md` produces no output |
| `CLAUDE.md` unchanged | VERIFIED | `git diff HEAD -- CLAUDE.md` produces no output |
| No `from mcp_canada.shared.i18n import t` in BC module | VERIFIED | Grep across `src/mcp_canada/modules/british_columbia/` returns no matches |
| `_make_http_response` helper deleted from `test_client.py` | VERIFIED | Grep for `_make_http_response` and `raise_for_status` in test_client.py finds only the class-docstring comment (`"because the old _api_get called .raise_for_status() on the dict"`) — no test code |
| Only lines 700-708 changed in `tools.py` (no other `make_error` sites touched) | VERIFIED | Grep for `au moins un` shows only lines 705-706 and their test assertions — no other guard sites modified |

---

### Test Run Results

**Unit tests (148 tests, BC module):**
```
uv run pytest src/mcp_canada/modules/british_columbia/ -x -q
148 passed in 1.44s
```

**Integration tests (BC, live APIs):**
```
uv run pytest tests/integration/ -v -m integration --timeout=120 -k Bc
11 passed, 230 deselected in 3.70s
```
Tests passing: `TestBcPromptsResources` (3) + `TestBcToolScenarios` (8) = 11 total (0 failures, was 7 pre-fix).

**Full project coverage:**
```
uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q
96.42% total coverage (1917 passed, 2 skipped)
Required test coverage of 95% reached.
```

---

### Anti-Patterns Found

None found in the modified files. No TODO/FIXME/placeholder patterns in `client.py`, `tools.py`, `test_client.py`, or `test_tools.py`.

---

### Human Verification Required

None. All 5 gap truths are verifiable programmatically via unit tests, integration tests against the live BC CKAN/WFS APIs, and static code inspection.

---

### Gaps Summary

No gaps. All 5 UAT gaps are resolved:

- **Gap 1 (Test 2):** `bc_search_datasets` — fixed by `_api_get` rewrite. Live integration test `test_search_finds_wildfire_data` passes.
- **Gap 2 (Test 3):** `bc_get_dataset_details` — fixed by same `_api_get` rewrite. `fetch_dataset_details` now returns `queryable_via_wfs` + `object_name` correctly.
- **Gap 3 (Test 9):** `bc_query_features` — fixed by same `_api_get` rewrite (it calls `fetch_dataset_details` internally). Both WFS and file-parser routing tests pass.
- **Gap 4 (Test 13):** `bc_get_water_wells(lang='fr')` — fixed by inline `lang == "en"` ternary. French message contains `"au moins un"`, English message unchanged.
- **Gap 5 (Test 14):** Integration suite — 11/11 BC tests pass (0 failures). The 5 additional pre-existing integration test bugs (wrong `fire_year` param, wrong data shape assertions, wrong `object_name` param) were also fixed as Rule 1 bugs in the same plan execution.

---

_Verified: 2026-04-11T05:00:00Z_
_Verifier: Claude (gsd-verifier)_
