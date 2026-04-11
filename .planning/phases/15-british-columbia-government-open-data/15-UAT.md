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
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "bc_get_dataset_details returns queryable_via_wfs and object_name for a wildfire dataset"
  status: failed
  reason: "User reported: Error calling tool 'bc_get_dataset_details': 'dict' object has no attribute 'raise_for_status' (same _api_get bug as Test 2)"
  severity: blocker
  test: 3
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "bc_query_features routes WFS-queryable datasets to the WFS path and returns features"
  status: failed
  reason: "User reported: Error calling tool 'bc_query_features': 'dict' object has no attribute 'raise_for_status' (cascades from bc_get_dataset_details — same _api_get bug)"
  severity: blocker
  test: 9
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "Error envelopes produced by bc_ tools contain French text when lang='fr'"
  status: failed
  reason: "User reported: Error envelope has lang=fr but message text is still English: 'bc_get_water_wells requires at least one of city, well_class, or aquifer_id (dataset has 130K+ records — Pitfall 5).'"
  severity: major
  test: 13
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "Integration test suite passes for BC tool and prompt/resource scenarios"
  status: failed
  reason: "User reported: 7 failed"
  severity: major
  test: 14
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
