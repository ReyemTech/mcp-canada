---
phase: 16-quebec-government-open-data
plan: 04
subsystem: api
tags: [ckan, quebec, fastmcp, pydantic, mcp-tools, environment, energy, arcgis, tdd, prompts, resources]

# Dependency graph
requires:
  - phase: 16-03
    provides: "7 health/transport client functions + 7 @tool functions — basis for Plan 04"
provides:
  - "src/mcp_canada/modules/quebec/client.py — 6 final client functions (environment/energy)"
  - "src/mcp_canada/modules/quebec/tools.py — 6 final @tool functions (18 total Quebec tools)"
  - "src/mcp_canada/modules/quebec/prompts.py — 6 bilingual @prompt functions"
  - "src/mcp_canada/modules/quebec/resources.py — 7 zero-parameter @resource functions"
  - "Unit tests: 22 client/tool + 15 prompt/resource tests, all RED->GREEN TDD"
  - "Integration tests: 9 tool scenarios + 3 prompt/resource scenarios via MCP Client"
  - "README.md — Quebec section complete (18 tools), total 187->193"
  - "CLAUDE.md — CKAN portal list updated with Quebec"
affects:
  - "README.md — tool count updated to 193, 4 provincial APIs"
  - "16-VALIDATION.md — all 16-04-* rows green"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "fetch_air_quality_index ArcGIS REST: api_get with f=json/where=1=1/outFields=*/resultRecordCount; features[] flattened with {**attrs, longitude, latitude}"
    - "Metadata-only tools return details.model_dump() directly — no parsing needed for SHP/GPKG archives"
    - "fetch_electricity_data two-step: fetch_dataset_details -> pick first CSV resource -> fetch_and_parse(csv_url)"
    - "Integration test class decorator @pytest.mark.asyncio at class level — avoids per-method decorator"
    - "Resource tests changed from sync+asyncio.get_event_loop() to async def — cleaner pytest-asyncio pattern"
    - "Quick lookup prompts (str): sopfeu_active_fires redirects to sopfeu.qc.ca since SOPFEU not on DQ CKAN"

key-files:
  created:
    - .planning/phases/16-quebec-government-open-data/16-04-SUMMARY.md
  modified:
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/tools.py
    - src/mcp_canada/modules/quebec/prompts.py
    - src/mcp_canada/modules/quebec/resources.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/modules/quebec/__tests__/test_tools.py
    - src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py
    - tests/integration/test_tool_scenarios.py
    - tests/integration/test_prompts_resources_scenarios.py
    - README.md
    - CLAUDE.md
    - .planning/phases/16-quebec-government-open-data/16-VALIDATION.md

key-decisions:
  - "ArcGIS REST for IQA: fetch_air_quality_index uses api_get directly (not shared/arcgis_hub.py) since endpoint is a simple GET with f=json param — no FeatureServer pagination or type-specific handling needed"
  - "Metadata-only tools return model_dump() directly: fetch_forest_fires_history/water_quality/protected_areas delegate to fetch_dataset_details and return the dict directly — no additional parsing for unparseable SHP/GPKG"
  - "Active fires redirects to SOPFEU: quebec_active_fires_now prompt explicitly redirects to sopfeu.qc.ca since SOPFEU is confirmed NOT on DQ CKAN (research finding)"
  - "Resource tests converted to async: sync tests with asyncio.get_event_loop() fail in Python 3.14 (no running event loop in main thread) — async def with pytestmark.asyncio is cleaner"
  - "tools.py __all__ extended in-place: 6 new tool names added to existing list before function definitions, avoiding a separate section"

requirements-completed: []

# Metrics
duration: 28min
completed: 2026-04-11T23:44:20Z
---

# Phase 16 Plan 04: Quebec Environment/Energy Tools, Prompts, and Resources Summary

**Quebec module complete — 18 tools, 6 prompts, 7 resources, live integration coverage, 96.51% coverage**

## Performance

- **Duration:** 28 min
- **Started:** 2026-04-11T23:16:16Z
- **Completed:** 2026-04-11T23:44:20Z
- **Tasks:** 4
- **Files modified:** 12

## Accomplishments

### Task 1: 6 Environment/Energy Client + Tool Functions

Implemented 6 client functions replacing Plan 04 `NotImplementedError` stubs:

- `fetch_air_quality_stations`: RSQAQ datastore_search with `active_only` filter (DATE_FERMETURE null check); returns `list[QuebecAirQualityStation]`
- `fetch_air_quality_index`: ArcGIS REST FeatureServer via `api_get` with `f=json&where=1=1&outFields=*`; features flattened with `{**attrs, longitude, latitude}`
- `fetch_water_quality_monitoring`: metadata-only, delegates to `fetch_dataset_details("suivi-physicochimique-des-rivieres-et-du-fleuve")` + `model_dump()`
- `fetch_electricity_data`: two-step — `fetch_dataset_details` picks first CSV resource URL → `fetch_and_parse(csv_url)`
- `fetch_forest_fires_history`: metadata-only, delegates to `fetch_dataset_details("feux-de-foret")` + `model_dump()`
- `fetch_protected_areas`: metadata-only, delegates to `fetch_dataset_details("aires-protegees-au-quebec")` + `model_dump()`

Added 6 `@tool` functions extending Plan 03's 12 to 18 total Quebec tools:
- All tools: `lang: Literal["en", "fr"] = "en"`, inline ternary bilingual errors, `Use for:` + 8+ `Keywords:` per BM25 contract
- `AQ_INDEX_URL` constant imported into tools.py for ArcGIS URL in `_meta` envelope
- 22 new unit tests (8 client + 14 tools), all RED→GREEN TDD

### Task 2: 6 Bilingual Prompts + 7 Zero-Parameter Resources

**Prompts (6):**

Guided workflows (`list[Message]` with user+assistant roles):
- `quebec_explore_health`: health installations → ER wait times → demographics
- `quebec_explore_transport_conditions`: road conditions/works/events → bridge structures
- `quebec_explore_environment`: AQ stations → AQ index → water quality → protected areas

Quick lookups (`str` instructions):
- `quebec_quick_dataset_search`: CKAN search → details → query workflow
- `quebec_check_road_conditions`: MTQ road conditions/works/events quick guide
- `quebec_active_fires_now`: explicit SOPFEU redirect (not on DQ CKAN)

**Resources (7):**

- `data://quebec/ministries`: 9 key ministries with bilingual labels + CKAN org slugs (JSON)
- `data://quebec/regions`: 17 administrative regions with codes, FR/EN names (JSON)
- `data://quebec/mrcs`: 32 major MRCs with region codes (JSON)
- `docs://quebec/catalog-federation-quirks`: 139-org federation, Montreal overlap, SOPFEU/Hydro deferred (Markdown)
- `docs://quebec/bilingual-metadata-guide`: French-primary metadata, update_frequency values, bilingual columns (Markdown)
- `template://quebec/dataset-report`: dataset exploration report template (Markdown)
- `template://quebec/road-conditions-report`: road conditions analysis report template (Markdown)

15 unit tests (8 prompt + 7 resource) — all RED→GREEN TDD.

### Task 3: Live Integration Tests via MCP Client Layer

**TestQuebecToolScenarios (9 tests):**
- `test_search_datasets_live`: CKAN search returns results with `_meta` envelope
- `test_list_organizations_live`: 139 orgs returned (>=100 check)
- `test_list_categories_groups_not_tags`: groups (not tags) include sante/environnement
- `test_get_er_wait_times_live`: 116 EDs with hourly refresh
- `test_get_health_installations_live`: CLSC filter returns `is_clsc=True` rows
- `test_get_road_works_wfs_csv`: road works from MTQ live WFS CSV
- `test_get_bridge_structures_requires_filter`: no-filter returns INVALID_INPUT; with-filter succeeds
- `test_discover_tools_finds_quebec`: BM25 surfaces quebec_ tools from health query
- `test_invalid_package_id_returns_structured_error`: error envelope for invalid slug

**TestQuebecPromptsResources (3 tests):**
- `test_prompts_discoverable`: all 6 quebec_ prompts in prompts/list
- `test_resources_discoverable`: all 7 quebec/ URIs in resources/list
- `test_ministries_resource_valid_json`: data://quebec/ministries returns JSON with msss/mtq slugs

### Task 4: README, CLAUDE.md, VALIDATION.md Updates

- README: Quebec section 12→18 tools, total 187→193, "4 provincial APIs" in header
- CLAUDE.md: CKAN row updated with Quebec (Données Québec) — no new portal technology row
- 16-VALIDATION.md: all four 16-04-* task rows flipped to green (✅)

## Task Commits

1. **Task 1: 6 environment/energy client + tool functions** — `366abd6` (feat)
2. **Task 2: 6 bilingual prompts + 7 zero-parameter resources** — `39229b0` (feat)
3. **Task 3: Wire Quebec integration tests through MCP Client** — `b5303d3` (feat)
4. **Task 4: README, CLAUDE.md, VALIDATION.md updates** — `426a02c` (docs)

## Files Modified

- `src/mcp_canada/modules/quebec/client.py` — 6 NotImplementedError stubs replaced; `AQ_INDEX_URL` + `RSQAQ_STATIONS_RESOURCE_ID` + `QuebecAirQualityStation` imported
- `src/mcp_canada/modules/quebec/tools.py` — 6 new @tool functions; `AQ_INDEX_URL` imported; `__all__` extended
- `src/mcp_canada/modules/quebec/prompts.py` — stub filled in with 6 bilingual prompts (3 guided + 3 quick lookups)
- `src/mcp_canada/modules/quebec/resources.py` — stub filled in with 7 zero-parameter resources (3 data + 2 docs + 2 template)
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — Plan 04 skips replaced with 8 real test bodies
- `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — Plan 04 skips replaced with 14 real test bodies; `httpx` import added
- `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py` — all 15 tests implemented (async def pattern)
- `tests/integration/test_tool_scenarios.py` — xfail stubs replaced with 9 live integration tests; class-level `@pytest.mark.asyncio`
- `tests/integration/test_prompts_resources_scenarios.py` — xfail stubs replaced with 3 live integration tests
- `README.md` — Quebec section 12→18 tools, total 187→193
- `CLAUDE.md` — CKAN portal list includes Quebec
- `.planning/phases/16-quebec-government-open-data/16-VALIDATION.md` — 16-04-01/02/03/04 flipped to green

## Decisions Made

- ArcGIS REST for IQA calls `api_get` directly (not `shared/arcgis_hub.py`) — simple GET endpoint, no pagination or FeatureServer-specific handling needed
- Metadata-only tools return `model_dump()` directly — no additional parsing layer for SHP/GPKG archives that `fetch_and_parse` cannot handle
- `quebec_active_fires_now` prompt explicitly redirects to `sopfeu.qc.ca` — SOPFEU is confirmed not registered on Données Québec
- Resource tests converted from sync+`asyncio.get_event_loop()` to `async def` — Python 3.14 raises RuntimeError for `get_event_loop()` without a running loop in the main thread

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Resource tests used asyncio.get_event_loop() which fails in Python 3.14**
- **Found during:** Task 2 GREEN verification
- **Issue:** Test file used `asyncio.get_event_loop().run_until_complete(...)` in sync test functions; Python 3.14 raises `RuntimeError: There is no current event loop in thread 'MainThread'`
- **Fix:** Converted all 7 resource tests to `async def` matching pytest-asyncio pattern (consistent with all other test files in this module)
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py`
- **Commit:** `39229b0` (included in Task 2)

**2. [Rule 1 - Bug] test_tools.py missing httpx import for error path tests**
- **Found during:** Task 1 GREEN verification
- **Issue:** Plan 04 tool test skeletons for `TestQuebecGetAirQualityStations.test_upstream_error` referenced `httpx.HTTPStatusError` without importing `httpx` at the module level
- **Fix:** Added `import httpx` to test_tools.py imports
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_tools.py`
- **Commit:** `366abd6` (included in Task 1)

**3. [Rule 1 - Bug] FastMCP Message.content is TextContent (not str)**
- **Found during:** Task 2 GREEN verification, `test_explore_health_bilingual`
- **Issue:** Test asserted `m.content for m in result if isinstance(m.content, str)` — but FastMCP wraps prompt message content as `TextContent(type='text', text='...')`, not a plain string
- **Fix:** Changed to `m.content.text for m in result if hasattr(m.content, "text")`
- **Files modified:** `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py`
- **Commit:** `39229b0` (included in Task 2)

---

**Total deviations:** 3 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Test isolation fixes only. No scope creep.

## Phase 16 Complete

All 18 `quebec_` tools are now implemented and tested:

| Group | Tools | Source |
|-------|-------|--------|
| Discovery (5) | search_datasets, get_dataset_details, query_dataset, list_organizations, list_categories | DQ CKAN |
| Health (3) | get_health_installations, get_er_wait_times, get_population_by_municipality | MSSS/MAMH datastore |
| Transport (4) | get_road_conditions, get_road_works, get_road_events, get_bridge_structures | MTQ WFS CSV |
| Environment/Energy (6) | get_forest_fires_history, get_air_quality_stations, get_air_quality_index, get_water_quality_monitoring, get_electricity_data, get_protected_areas | RSQAQ/ArcGIS/MELCCFP/Hydro-QC |

Phase 16 is complete. Next: Phase 17 (Alberta Government Open Data) or other phases in the roadmap.

---

## Self-Check: PASSED

- `src/mcp_canada/modules/quebec/client.py` — FOUND
- `src/mcp_canada/modules/quebec/tools.py` — FOUND
- `src/mcp_canada/modules/quebec/prompts.py` — FOUND (6 prompts)
- `src/mcp_canada/modules/quebec/resources.py` — FOUND (7 resources)
- `tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios` — FOUND (9 tests)
- `tests/integration/test_prompts_resources_scenarios.py::TestQuebecPromptsResources` — FOUND (3 tests)
- `.planning/phases/16-quebec-government-open-data/16-04-SUMMARY.md` — FOUND
- Commit `366abd6` (feat: 6 client + tool functions) — FOUND
- Commit `39229b0` (feat: 6 prompts + 7 resources) — FOUND
- Commit `b5303d3` (feat: integration tests) — FOUND
- Commit `426a02c` (docs: README + CLAUDE.md + VALIDATION.md) — FOUND
- 96.51% coverage threshold (95%) — PASSED
- `pyright` — 0 errors
- Full test suite: 2042 passed, 2 skipped
