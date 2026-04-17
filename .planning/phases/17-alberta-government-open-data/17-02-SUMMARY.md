---
phase: 17-alberta-government-open-data
plan: "02"
subsystem: discovery
tags: [alberta, ckan, discovery, arcgis-hub-router, parsed-dict-contract, pitfall-1, pitfall-11, pitfall-12]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "12-file alberta module surface + locked client/tool signatures + 14 CKAN/ArcGIS/511/AER fixtures + TestSharedApiGetContract skeleton"
provides:
  - "5 filled discovery client functions: fetch_search_datasets, fetch_dataset_details, fetch_query_dataset, fetch_organizations, fetch_format_categories"
  - "5 filled @tool bodies: alberta_search_datasets, alberta_get_dataset_details, alberta_query_dataset, alberta_list_organizations, alberta_list_categories"
  - "TestSharedApiGetContract: 3 regression tests enforcing post-15-05 parsed-dict api_get contract"
  - "_flatten_extras helper dropping 50+ publication-identifier extras (Pitfall 11); keeps isopen / language / frequencyofupdate / creator"
  - "Hybrid router fetch_query_dataset with FeatureServer-over-MapServer preference (Pitfall 12); CSV/XLSX/JSON/GeoJSON route via shared/parsers; PDF/ZIP/KML/WMS return metadata-only"
  - "27 unit tests covering Plan 02 scope (17 client + 10 tool) all green; BM25 docstring quality test green"
affects: [17-03, 17-04, 17-05, 17-06, 17-07, 17-08, 17-09]

tech-stack:
  added: []
  patterns:
    - "Hybrid router resource-format dispatch (ESRI REST→arcgis_hub, CSV/XLSX/JSON→fetch_and_parse, PDF/ZIP→metadata-only)"
    - "FeatureServer-over-MapServer preference at resource_index==0 (Pitfall 12 regression guard)"
    - "Multi-fq CKAN filter composition: organization:<slug> + res_format:<fmt> joined with space"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "TestSharedApiGetContract patches module-local `mcp_canada.modules.alberta.client.api_get` (not `mcp_canada.shared.http.api_get`) because Python's `from ... import` creates a local binding — patching the shared module wouldn't affect already-imported references. This is the same proven pattern used by BC's TestSharedApiGetContract and achieves the identical regression guard (parsed dict sent to code expecting Response raises AttributeError)."
  - "format= filter in fetch_search_datasets composes with organization via `fq` space-joined token list: `organization:{slug} res_format:{fmt}` (CKAN interprets space as implicit AND across fq tokens)."
  - "Hybrid router prefers FeatureServer at resource_index==0 by scanning all resources for any ESRI REST + /FeatureServer match. Explicit non-zero resource_index falls back to literal indexing — gives agents the escape hatch to force a specific resource when needed."
  - "_flatten_extras uses a frozenset whitelist instead of a blacklist (isopen / language / frequencyofupdate / creator only). Future additions must be explicit — prevents accidental leakage of the 50+ identifier fields we want to hide."
  - "Negative resource_index is rejected at the tool layer (INVALID_INPUT before any client call) rather than the client layer — keeps the client contract uniform with valid indices."

requirements-completed: [AB-01, AB-02, AB-03, AB-04, AB-05, AB-23]

duration: ~6min
completed: 2026-04-17
---

# Phase 17 Plan 02: Alberta Discovery Tools Summary

**Filled the 5 CKAN discovery tools that downstream curated tools build on: search, details, hybrid-router query, org list, and format categories — all gated behind a 3-test parsed-dict contract guard that prevents the Phase 15-05 regression class.**

## Performance

- **Duration:** ~6 min (single executor run)
- **Started:** 2026-04-17T18:38Z
- **Completed:** 2026-04-17T18:44Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Filled 5 client function bodies with `cached_fetch` + `get_limiter` wiring (per `.claude/rules/modules.md`)
- Filled 5 `@tool` bodies with bilingual inline-ternary error handling and `make_response` / `make_error` envelopes
- Implemented `_flatten_extras` whitelist helper and verified it both DROPS `identifier-*` fields (Pitfall 11) AND preserves `isopen`/`language`/`frequencyofupdate`/`creator`
- Implemented hybrid router: FeatureServer preference verified via dedicated test (`test_prefers_featureserver_over_mapserver` asserts no `/MapServer` in the chosen service URL)
- Verified via direct tests: `alberta_list_categories` docstring mentions both `res_format` and `group_list` (Pitfall 1 documented for agents)
- All 32 tests green (17 client + 10 tool + 5 BM25 quality guards)

## Task Commits

1. **Task 1: Client functions + TestSharedApiGetContract** — `ef984df` (feat)
2. **Task 2: 5 discovery @tool functions** — `01212af` (feat)

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — filled 5 `fetch_*` bodies; added `_flatten_extras`, `_coerce_bool`, `_build_summary`, `_build_resource`, `_build_details`, `_pick_esri_resource`, `_split_feature_server_url` helpers; imported `CACHE_TTL_META` / `CACHE_TTL_SEARCH` / `CACHE_KEY_PREFIX` from constants
- `src/mcp_canada/modules/alberta/tools.py` — filled 5 `@tool` bodies calling `_client.fetch_*`; inline `lang == "fr"` French error messages; `make_response` / `make_error` envelope wrapping
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — filled `TestSharedApiGetContract` (3 tests) + 5 per-function test classes (14 tests); total 17 client tests
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — filled 5 per-tool test classes (10 tests including French-error + docstring-pitfall-mention checks)

## Test Coverage

**Client tests (17):**

| Class | Tests |
|-------|-------|
| TestSharedApiGetContract | 3 (parsed-dict return, success=False raises, success=True unwraps) |
| TestAlbertaSearchDatasets | 5 (shape, format-filter, org-filter, pagination, rows clamp) |
| TestAlbertaGetDatasetDetails | 2 (flattens 55 extras, preserves useful 4) |
| TestAlbertaQueryDataset | 4 (ESRI REST routing, CSV routing, PDF metadata-only, FS>MS preference) |
| TestAlbertaListOrganizations | 1 (5-org fixture flattened) |
| TestAlbertaListCategories | 2 (facet URL + params, sorted desc) |

**Tool tests (10):**

| Class | Tests |
|-------|-------|
| TestAlbertaSearchDatasetsTool | 3 (envelope, format pass-through, French error) |
| TestAlbertaGetDatasetDetailsTool | 2 (envelope, NOT_FOUND on HTTPStatusError) |
| TestAlbertaQueryDatasetTool | 2 (envelope, INVALID_INPUT on resource_index<0) |
| TestAlbertaListOrganizationsTool | 1 (envelope + model_dump) |
| TestAlbertaListCategoriesTool | 2 (envelope, docstring mentions res_format & group_list) |

## Deviations from Plan

**[Rule 3 - Blocking] Patch target for TestSharedApiGetContract.**

- **Found during:** Task 1 RED phase
- **Issue:** The plan prescribed `patch("mcp_canada.shared.http.api_get", ...)` to patch "the shared layer." When executed, that patch did not take effect — the test hit live `open.alberta.ca` and returned count=33270 instead of the mocked count=5.
- **Root cause:** `client.py` uses `from mcp_canada.shared.http import api_get` which creates a module-local reference in `mcp_canada.modules.alberta.client`. Python's `patch()` only affects the target namespace — patching `shared.http.api_get` rebinds that name in `shared.http` but the local binding inside `alberta.client` still points to the original function.
- **Fix:** Patch `mcp_canada.modules.alberta.client.api_get` (same pattern BC's `TestSharedApiGetContract` uses at `british_columbia/__tests__/test_client.py:TestSharedApiGetContract`). The regression guard intent is preserved: a raw-dict return value sent to code that still expects a Response will fail with `AttributeError` — which is the exact Phase 15-05 bug class.
- **Files modified:** `src/mcp_canada/modules/alberta/__tests__/test_client.py` only
- **Commit:** `ef984df`

No other deviations. Plan text + action steps executed as specified.

## Pitfalls Addressed in Code

| Pitfall | Where | How |
|---------|-------|-----|
| **Pitfall 1** (group_list empty) | `fetch_format_categories` + `alberta_list_categories` docstring | Uses `package_search?facet.field=["res_format"]&rows=0` NOT `group_list`; docstring documents it explicitly |
| **Pitfall 11** (50+ identifier extras) | `_flatten_extras` in client.py + `AlbertaDatasetDetails` schema | Whitelist keeps only isopen / language / frequencyofupdate / creator; everything else is dropped silently |
| **Pitfall 12** (MapServer vs FeatureServer) | `_pick_esri_resource` in client.py | At `resource_index==0`, scans all resources for any `ESRI REST + /FeatureServer` match first; `test_prefers_featureserver_over_mapserver` regression-tests this |

## Handoff to Next Plans

- **Plan 03 (Wave 2 AER):** Discovery surface is ready — AER curated tools can call `_client.fetch_query_dataset` if any AER static URL needs CKAN metadata, though the plan's design is for AER tools to call `fetch_and_parse` directly against static URLs. No dependency leaks; Plan 03's stubs remain untouched.
- **Plan 04 (Wave 2 Wildfire):** `arcgis_hub.query_feature_service` is already imported and used by this plan's `fetch_query_dataset`. Plan 04 follows the same shape for `fetch_active_fires` etc.
- **Plan 05 (Wave 2 Health), Plan 06 (Wave 3 Transport), Plan 07 (Wave 3 Environment):** Independent — don't depend on Plan 02 beyond the `_api_get` helper (already ready from Wave 0).
- **Plan 09 (Wave 5 Parametrized tests):** `TestAlbertaEnvelopes` / `TestAlbertaLangParam` can now run against all 5 Plan 02 tools (envelope + lang propagation verified per-tool already, so parametrized version should pass without surprises).

## Self-Check: PASSED

- Commit `ef984df` found in git log (Task 1)
- Commit `01212af` found in git log (Task 2)
- `src/mcp_canada/modules/alberta/client.py` modified — 5 bodies filled, 7 helpers added
- `src/mcp_canada/modules/alberta/tools.py` modified — 5 `@tool` bodies filled
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` modified — 17 tests added (3 contract + 14 per-function)
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` modified — 10 tests added
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py -x` → 32 passed
- `uv run python -c "from mcp_canada.modules.alberta.tools import <5 tools>; print('5 tools importable')"` → "5 tools importable"
