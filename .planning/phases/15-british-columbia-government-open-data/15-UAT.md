---
status: complete
phase: 15-british-columbia-government-open-data
source:
  - 15-01-SUMMARY.md
  - 15-02-SUMMARY.md
  - 15-03-SUMMARY.md
  - 15-04-SUMMARY.md
started: 2026-04-10T00:00:00Z
updated: 2026-04-11T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. BC module auto-registers (behind BM25)
expected: Server starts; `list_modules` shows `british_columbia`; no registration errors. (Direct tool listing correctly hides the 20 bc_ tools behind BM25.)
result: pass

### 2. CKAN search returns BC datasets
expected: Call `bc_search_datasets(q="wildfire")` — returns a list of BC datasets (not empty) with `_meta.source.api == "bc-data-catalogue"`, each with id/title/name/resources_count fields.
result: issue
reported: "Error calling tool 'bc_search_datasets': 'dict' object has no attribute 'raise_for_status'"
severity: blocker

### 3. Dataset details surface queryable_via_wfs + object_name
expected: Call `bc_get_dataset_details` on a wildfire-related dataset. Response includes `queryable_via_wfs: true` and an `object_name` starting with `WHSE_` (e.g. `WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP`).
result: issue
reported: "Error calling tool 'bc_get_dataset_details': 'dict' object has no attribute 'raise_for_status'"
severity: blocker
notes: Same root cause as Test 2 — _api_get calls .raise_for_status() on a dict returned by shared api_get.

### 4. Active wildfires query returns live features
expected: Call `bc_get_active_fires()` — returns a features list from the live WFS. Each feature has properties like `FIRE_NUMBER`, `FIRE_STATUS`, `FIRE_CENTRE`, `CURRENT_SIZE`. `_meta.cached` false on first call, true within 5 min (active TTL).
result: pass

### 5. Fire perimeters require year filter
expected: Call `bc_get_fire_perimeters(year=2023)` — returns historical fire perimeter polygons. Year is required (large dataset); calling without year should fail or return a bounded subset per the tool docs.
result: pass

### 6. Protected areas use corrected BCGW object
expected: Call `bc_get_protected_areas()` — returns features (not a 400 error). Uses `WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW`, not the broken `WHSE_PARKS_ECOLOGY` prefix.
result: pass

### 7. Water wells 130K guard blocks unfiltered queries
expected: Call `bc_get_water_wells()` with no filter — returns an error envelope with `error.code == "INVALID_INPUT"` explaining that at least one filter (city, aquifer_id, or well_class) is required.
result: pass

### 8. Water wells with filter returns features
expected: Call `bc_get_water_wells(city="Kelowna")` — returns a features list (not the guard error), each with well metadata properties.
result: pass

### 9. bc_query_features routes WFS datasets correctly
expected: Call `bc_query_features` on a dataset where `queryable_via_wfs=true` — routes to the WFS path and returns geographic features. A file-only dataset routes to the file parser path instead (CSV/GeoJSON).
result: issue
reported: "Error calling tool 'bc_query_features': 'dict' object has no attribute 'raise_for_status'"
severity: blocker
notes: Same _api_get root cause — bc_query_features calls bc_get_dataset_details internally to decide routing.

### 10. Discovery finds BC tools via BM25
expected: Call `discover_tools(query="British Columbia wildfire")` — returns BC tools in the top results (e.g. `bc_get_active_fires`, `bc_explore_wildfires` prompt). The 20 bc_ tools are reachable through the BM25 discovery layer.
result: pass

### 11. bc_explore_wildfires prompt returns guided workflow
expected: Invoke the `bc_explore_wildfires` prompt — returns a multi-message conversation (user + assistant roles) walking through a 3-step wildfire analysis: active fires → perimeters → weather stations. Bilingual `lang="fr"` returns French content.
result: pass

### 12. docs://bc/wfs-query-guide resource is readable
expected: Read the `docs://bc/wfs-query-guide` resource — returns a markdown document explaining the CKAN → WFS two-step workflow with a concrete example. Content is bilingual (English + French sections).
result: pass

### 13. Bilingual error messages
expected: Call any `bc_` tool with invalid input and `lang="fr"` — error message is in French, not English. Envelope includes `_meta.lang: "fr"`.
result: issue
reported: "Error envelope has lang=fr but message text is still English: 'bc_get_water_wells requires at least one of city, well_class, or aquifer_id (dataset has 130K+ records — Pitfall 5).'"
severity: major
notes: Guard message is hardcoded English instead of going through shared/i18n.py t() lookup.

### 14. Integration test suite passes
expected: Run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Bc` — all `TestBcToolScenarios` (8 scenarios) and `TestBcPromptsResources` (3 scenarios) pass against the live APIs.
result: issue
reported: "7 failed"
severity: major
notes: Cascades from the _api_get blocker — CKAN-dependent integration scenarios hit the real api_get (which returns a dict, not a Response), unlike unit tests which mocked httpx with a fake Response.

## Summary

total: 14
passed: 9
issues: 5
pending: 0
skipped: 0

## Gaps

- truth: "bc_search_datasets returns a list of BC datasets with _meta.source.api == 'bc-data-catalogue'"
  status: failed
  reason: "User reported: Error calling tool 'bc_search_datasets': 'dict' object has no attribute 'raise_for_status'"
  severity: blocker
  test: 2
  root_cause: "british_columbia/client.py:_api_get calls .raise_for_status()/.json() on the return value of shared/http.py:api_get, but shared api_get already returns parsed JSON (dict), not an httpx.Response."
  artifacts:
    - path: "src/mcp_canada/modules/british_columbia/client.py"
      issue: "Lines 69-71: `response = await api_get(...); response.raise_for_status(); envelope = response.json()` — dict has no raise_for_status."
    - path: "src/mcp_canada/shared/http.py"
      issue: "Lines 34-58: api_get contract returns `response.json()` (parsed dict/list), not a Response. BC is the only caller that misuses it."
    - path: "src/mcp_canada/modules/british_columbia/__tests__/test_client.py"
      issue: "Lines 25-31 `_make_http_response()` helper builds a MagicMock with .raise_for_status()+.json() and patches client.api_get with it, masking the real contract mismatch across 22 tests."
  missing:
    - "Rewrite british_columbia/client.py:55-78 _api_get to treat api_get return as parsed dict — drop .raise_for_status()/.json(), check `envelope.get('success')` directly and return `envelope.get('result', {})`."
    - "Add a 'contract' unit test that patches `mcp_canada.shared.http.api_get` (not the module-local import) with an AsyncMock returning a raw dict."
    - "Re-run test 2 live against https://catalogue.data.gov.bc.ca/api/3/action/package_search."
  debug_session: ".planning/debug/bc-api-get-dict-mismatch.md"

- truth: "bc_get_dataset_details returns queryable_via_wfs and object_name for a wildfire dataset"
  status: failed
  reason: "User reported: Error calling tool 'bc_get_dataset_details': 'dict' object has no attribute 'raise_for_status' (same _api_get bug as Test 2)"
  severity: blocker
  test: 3
  root_cause: "Same as Test 2 — british_columbia/client.py:_api_get treats shared api_get's parsed-JSON return as an httpx.Response. fetch_dataset_details at line 217 calls the broken helper via package_show."
  artifacts:
    - path: "src/mcp_canada/modules/british_columbia/client.py"
      issue: "Line 217 calls `_api_get('package_show', {'id': package_id})` — routes through the broken helper at lines 69-71."
  missing:
    - "Covered by the _api_get fix for Gap 1 — no separate code change needed."
    - "Re-run test 3 live to confirm queryable_via_wfs + object_name surface correctly for a real wildfire dataset id."
  debug_session: ".planning/debug/bc-api-get-dict-mismatch.md"

- truth: "bc_query_features routes WFS-queryable datasets to the WFS path and returns features"
  status: failed
  reason: "User reported: Error calling tool 'bc_query_features': 'dict' object has no attribute 'raise_for_status' (cascades from bc_get_dataset_details — same _api_get bug)"
  severity: blocker
  test: 9
  root_cause: "bc_query_features calls fetch_dataset_details internally to decide between the WFS and file-parser routing paths — so it hits the same broken _api_get as Tests 2/3 before it can read queryable_via_wfs."
  artifacts:
    - path: "src/mcp_canada/modules/british_columbia/client.py"
      issue: "Same _api_get bug at lines 69-71 — reached via fetch_dataset_details (line 217) when bc_query_features resolves WFS-vs-file routing."
  missing:
    - "Covered by the _api_get fix for Gap 1 — no separate code change needed."
    - "Re-run test 9 live with both a WFS-queryable dataset (should hit the WFS path) and a file-only dataset (should hit the file parser path) to verify routing logic works end-to-end once _api_get is fixed."
  debug_session: ".planning/debug/bc-api-get-dict-mismatch.md"

- truth: "Error envelopes produced by bc_ tools contain French text when lang='fr'"
  status: failed
  reason: "User reported: Error envelope has lang=fr but message text is still English: 'bc_get_water_wells requires at least one of city, well_class, or aquifer_id (dataset has 130K+ records — Pitfall 5).'"
  severity: major
  test: 13
  root_cause: "bc_get_water_wells at tools.py:700-706 passes a hardcoded English literal to make_error. make_error (shared/envelope.py:48-67) only stamps lang into the envelope — it does not translate the message; the caller owns localisation. So error.lang == 'fr' but error.message stays English. This is actually the project-wide convention: zero @tool functions in any module (bank_of_canada, ontario, BC, all others) branch error text on lang or import shared/i18n.py:t(). The bilingual infrastructure in shared/i18n.py exists but has no production imports. Test 13 is the first UAT that asserts on localised error text, so it exposes the latent systemic gap via the most docstring-visible guard."
  artifacts:
    - path: "src/mcp_canada/modules/british_columbia/tools.py"
      issue: "Lines 700-706: bc_get_water_wells guard passes a hardcoded English string to make_error with lang=lang — message is not conditional on lang. All other make_error call sites in this file (lines 143, 165, 198, 213, 248, 264, 270, 283, 307, 317, 351, 387, 455, 491, 510, 563, 613, 663, 725, 771, 821, 859, 880, 924, 971, 1015, 1065, 1111, 1161) have the same latent defect but are not asserted on by Test 13."
    - path: "src/mcp_canada/shared/envelope.py"
      issue: "Lines 48-67: make_error is a pure pass-through builder. By contract, it stamps 'lang' into error.lang but never translates 'message'. The caller must pre-localise the string. No fix needed here — this is working as designed."
    - path: "src/mcp_canada/shared/i18n.py"
      issue: "t() helper and LABELS catalog exist (error.invalid_input already has a French template 'Entrée invalide : {detail}') but grep across src/ shows ZERO production imports. Only tests/test_i18n.py imports it. Infrastructure is orphaned."
  missing:
    - "Localise the bc_get_water_wells guard at tools.py:700-706 with an inline lang=='en'/'fr' ternary, mirroring the existing lang=='fr' pattern used in 7+ modules' prompts.py files. French text: 'bc_get_water_wells exige au moins un des paramètres city, well_class ou aquifer_id (l'ensemble de données contient plus de 130 000 enregistrements — Pitfall 5).'"
    - "Add a regression test in src/mcp_canada/modules/british_columbia/__tests__/test_tools.py asserting bc_get_water_wells(lang='fr') with no filters returns error.lang=='fr' AND error.message contains a French-only substring (e.g. 'au moins un')."
    - "Re-run UAT Test 13 by calling bc_get_water_wells(lang='fr') with no filters to confirm French message is returned."
    - "Out of scope for Gap 4 but recommended as a follow-up phase: audit every tool's error paths for bilingual coverage — the hardcoded-English pattern is systemic across all modules, and any future UAT that asserts on French error text will hit the same defect."
  debug_session: ".planning/debug/bc-bilingual-error-messages.md"

- truth: "Integration test suite passes for BC tool and prompt/resource scenarios"
  status: failed
  reason: "User reported: 7 failed"
  severity: major
  test: 14
  root_cause: "All 7 failures cascade from the same _api_get contract bug — integration tests exercise the real shared/http.py:api_get (which returns a dict), unlike unit tests which mocked api_get with a fake Response wrapper. Every CKAN-dependent integration scenario hits the AttributeError before reaching its assertions."
  artifacts:
    - path: "src/mcp_canada/modules/british_columbia/client.py"
      issue: "Same _api_get bug at lines 69-71; affects fetch_search_datasets, fetch_dataset_details, fetch_organizations, fetch_tags, and bc_query_features (via fetch_dataset_details)."
    - path: "tests/integration/test_tool_scenarios.py"
      issue: "TestBcToolScenarios scenarios that call bc_search_datasets / bc_get_dataset_details / bc_query_features will fail until _api_get is fixed. WFS-only scenarios (bc_get_active_fires, bc_get_fire_perimeters, bc_get_protected_areas, bc_get_water_wells) already pass because they bypass _api_get and go through _wfs_fetch."
  missing:
    - "Covered by the _api_get fix for Gap 1."
    - "Re-run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Bc` after the fix — expect 0 failures across TestBcToolScenarios and TestBcPromptsResources."
  debug_session: ".planning/debug/bc-api-get-dict-mismatch.md"
