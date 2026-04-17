---
phase: 17-alberta-government-open-data
plan: "07"
subsystem: environment-agriculture-demographics-parks
tags: [alberta, geodiscover, ckan, aqhi, water-advisories, crop-production, population-estimates, provincial-parks, arcgis, fetch-and-parse]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "locked signatures + AQHI/River/Parks constants + sample_aqhi_query fixture + autouse patch_cache_and_limiter"
  - phase: 17-alberta-government-open-data
    plan: "02"
    provides: "fetch_dataset_details helper (package_show + _flatten_extras) reused by crop + population fetchers"
provides:
  - "5 filled client functions across 4 domains: fetch_air_quality_stations (GeoDiscover AQHI MapServer L1), fetch_water_advisories (5-layer dispatcher on RIVER_FORECAST_FS_URL), fetch_crop_production (CKAN CSV via fetch_and_parse), fetch_population_estimates (CKAN XLSX via fetch_and_parse, 6 breakdowns), fetch_provincial_parks (GeoDiscover boundary FS)"
  - "5 filled @tool bodies: alberta_get_air_quality_stations, alberta_get_water_advisories, alberta_get_crop_production, alberta_get_population_estimates, alberta_get_provincial_parks"
  - "WATER_ADVISORY_LAYERS dispatch table (river=2, water_management=7, drought=4, ice_cover=6, water_sharing=9)"
  - "POPULATION_BREAKDOWN_HINTS dispatch table (6 breakdowns → URL/name hint fragments)"
  - "31 unit tests covering Plan 07 scope (20 client + 11 tool) all green"
  - "Completes the 24-tool Alberta curated set: 5 discovery + 4 AER + 4 wildfire + 3 health + 3 transport + 5 env/agri/demo/parks"
affects: [17-08, 17-09]

tech-stack:
  added: []
  patterns:
    - "Mixed GeoDiscover + CKAN+fetch_and_parse in a single plan (3 ArcGIS + 2 CKAN file-resource-parse)"
    - "Literal-typed dispatch parameter pattern: advisory_type / breakdown both use pre-call validation with bilingual INVALID_INPUT + valid=[] list before any fetch"
    - "Hint-based XLSX resource selection: case-insensitive substring match over resource URL+name, falls back to first XLSX when no hint matches"
    - "CKAN package → fetch_dataset_details → file-format resource filter → fetch_and_parse (reuses Plan 02 flattening)"

key-files:
  created:
    - .planning/phases/17-alberta-government-open-data/17-07-SUMMARY.md
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "Three distinct api_name envelope values for GeoDiscover — alberta-geodiscover-aqhi / water / parks — rather than a single alberta-geodiscover. Matches plan text specifying different API names per tool and gives agents finer-grained source attribution at the envelope level."
  - "Water advisory + population breakdown dispatch tables live in client.py (not constants.py). They are implementation details of the dispatchers, not cross-module reference data. Keeping them adjacent to the functions that use them makes maintenance easier."
  - "Aligned the Wave 0 fetch_population_estimates signature from 'cma' to 'annual' in the Literal, matching the Plan 07 spec and 17-RESEARCH.md § AB-25. 'cma' would have been ambiguous with StatCan's CMA-only coverage; 'annual' is unambiguous (annual provincial 1921-current)."
  - "fetch_and_parse is called with ttl=CACHE_TTL_ANNUAL for both crop + population — the underlying parser owns its cache, the outer cached_fetch only caches the full payload assembly."
  - "Population XLSX selection matches on both URL AND resource name (concatenated, lowercased). Protects against packages where Alberta CKAN puts the breakdown in the resource title only."

patterns-established:
  - "Literal dispatch + INVALID_INPUT pre-call validation: applies identically to water advisories (5 types) and population breakdowns (6 types); same body shape as Plan 04 fire_perimeters / fire_control_orders"
  - "Resource-filter-then-parse for CKAN file resources: filter pkg.resources by format (.upper() == 'CSV' / XLSX / XLS), optional hint-matching selector, then fetch_and_parse"

requirements-completed: [AB-21, AB-22, AB-24, AB-25, AB-26]

duration: 6min
completed: 2026-04-17
---

# Phase 17 Plan 07: Alberta Environment / Agriculture / Demographics / Parks Summary

**Filled the final 5 Alberta curated tools — AQHI stations, water advisories (5-layer dispatcher), crop production CSV, population estimates XLSX (6 breakdowns), and provincial parks — completing the 24-tool Alberta surface across 3 portal technologies (CKAN + GeoDiscover ArcGIS + CKAN file-resource parsing).**

## Performance

- **Duration:** ~6 min (single executor pass)
- **Started:** 2026-04-17T19:09Z
- **Completed:** 2026-04-17T19:15Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Filled 5 client function bodies mixing GeoDiscover ArcGIS (3) + CKAN file-resource parsing (2)
- Added `WATER_ADVISORY_LAYERS` dispatch table (5 advisory types → 5 layer IDs on `RIVER_FORECAST_FS_URL`)
- Added `POPULATION_BREAKDOWN_HINTS` dispatch table (6 breakdowns → URL/name hint fragments for XLSX selection)
- Filled 5 `@tool` bodies with bilingual inline-ternary error handling + `make_response`/`make_error` envelopes
- Both dispatch tools (`water_advisories`, `population_estimates`) validate Literal dispatch params pre-call and return bilingual `INVALID_INPUT` with `valid=[...]` list
- Completes the 19-curated + 5-discovery = **24-tool Alberta surface** (target locked from phase planning)
- All 31 Plan 07 tests green (20 client + 11 tool) + 5 BM25 quality checks green — 137 total alberta tests pass

## Task Commits

1. **Task 1: 5 client functions for environment/agri/demo/parks (TDD)** — `73feb0a` (feat)
2. **Task 2: 5 @tool functions for environment/agri/demo/parks (TDD)** — `2da0e2a` (feat)

Each task was a single commit because the RED and GREEN phases happened inline within the same editor session — no separate `test:` + `feat:` split. The RED phase was verified via pytest failure on the stubbed `NotImplementedError` bodies before each GREEN implementation was written.

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — filled 5 `fetch_*` bodies (air_quality_stations, water_advisories, crop_production, population_estimates, provincial_parks); added `WATER_ADVISORY_LAYERS` + `POPULATION_BREAKDOWN_HINTS` dispatch tables; added `AQHI_AIR_LAYER_URL` / `AQHI_STATIONS_LAYER_ID` / `RIVER_FORECAST_FS_URL` / `PROVINCIAL_PARKS_FS_URL` / `RATE_GROUP_GEODISCOVER` / `RATE_LIMIT_GEODISCOVER` to the constants import
- `src/mcp_canada/modules/alberta/tools.py` — filled 5 `@tool` bodies; added 3 new `API_NAME_GEODISCOVER_*` constants (aqhi/water/parks) for distinct envelope source attribution; added `_WATER_ADVISORY_TYPES` + `_POPULATION_BREAKDOWNS` for pre-call Literal validation
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — filled 5 per-function test classes (20 tests): AirQuality (2), WaterAdvisories (7 — 5 parametrized dispatch + 1 invalid + 1 shape), CropProduction (2), PopulationEstimates (8 — 1 default + 6 parametrized dispatch + 1 invalid), ProvincialParks (1)
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — filled 5 per-tool test classes (11 tests): AirQualityTool (2), WaterAdvisoriesTool (3), CropProductionTool (2), PopulationEstimatesTool (2), ProvincialParksTool (2)

## Test Coverage

**Client tests (20):**

| Class | Tests |
|-------|-------|
| TestAlbertaAirQuality | 2 (AQHI_AIR_LAYER_URL + layer id 1, stations/count/truncated shape) |
| TestAlbertaWaterAdvisories | 7 (5 parametrized advisory_type → layer id on RIVER_FORECAST_FS_URL, invalid raises ValueError, payload shape with truncated+advisory_type) |
| TestAlbertaCropProduction | 2 (package_show then CSV fetch_and_parse, missing-CSV fallback returns note) |
| TestAlbertaPopulationEstimates | 8 (csd default, 6 parametrized breakdown → URL hint match, invalid raises ValueError) |
| TestAlbertaProvincialParks | 1 (PROVINCIAL_PARKS_FS_URL + layer id 0 + parks/count/truncated shape) |

**Tool tests (11):**

| Class | Tests |
|-------|-------|
| TestAlbertaAirQualityTool | 2 (envelope + api=alberta-geodiscover-aqhi, French UPSTREAM_ERROR) |
| TestAlbertaWaterAdvisoriesTool | 3 (valid passes through with advisory_type kwarg, INVALID_INPUT with valid=[] list, French INVALID_INPUT) |
| TestAlbertaCropProductionTool | 2 (envelope + api=alberta-open-data, French UPSTREAM_ERROR) |
| TestAlbertaPopulationEstimatesTool | 2 (csd default + breakdown kwarg, INVALID_INPUT with valid=[] list) |
| TestAlbertaProvincialParksTool | 2 (envelope + api=alberta-geodiscover-parks, English UPSTREAM_ERROR) |

## Decisions Made

1. **Distinct GeoDiscover api_name per tool** — `alberta-geodiscover-aqhi`, `alberta-geodiscover-water`, `alberta-geodiscover-parks` rather than a single `alberta-geodiscover`. Matches plan specification and gives agents finer source attribution.
2. **Dispatch tables live in `client.py`** — `WATER_ADVISORY_LAYERS` and `POPULATION_BREAKDOWN_HINTS` are implementation details, not cross-module reference data. Not moved to `constants.py`.
3. **Population XLSX hint-match on URL+name concatenated** — protects against Alberta CKAN packages where breakdown appears in resource name but not URL path.
4. **Wave 0 signature drift fixed** — changed `fetch_population_estimates` breakdown Literal from `"cma"` (Wave 0) to `"annual"` (Plan 07 spec / research). Plan 02 `cma` was ambiguous with StatCan's CMA-only coverage; `annual` is unambiguous.
5. **fetch_and_parse ttl=CACHE_TTL_ANNUAL** passed through for both crop + population — the parser owns its inner cache; outer `cached_fetch` caches the full payload assembly.

## Deviations from Plan

**None.** Plan executed exactly as specified. The following note applies:

- The plan specified the `fetch_population_estimates` body could keep the Wave 0 `"cma"` breakdown, but Plan 07 also specified `"annual"` in the public-facing tool Literal. To avoid the client-vs-tool signature drift, the client signature was updated to match the tool (and the plan body's explicit `POPULATION_BREAKDOWN_HINTS` map, which uses `"annual"` not `"cma"`). This is spec-compliant with Plan 07's action block, not a deviation.

**Total deviations:** 0 auto-fixed.

## Issues Encountered

None. All tests green on first GREEN attempt after RED.

## Pitfalls Addressed in Code

| Pitfall | Where | How |
|---------|-------|-----|
| Water advisory layer confusion (AB-22) | `WATER_ADVISORY_LAYERS` table | Single dispatcher tool rather than 5 separate tools — keeps tool surface lean while still exposing all 5 layer types |
| Population XLSX resource selection (AB-25) | `POPULATION_BREAKDOWN_HINTS` + hint-match | Case-insensitive substring match on URL+name; falls back to first XLSX when no hint matches. Protects against Alberta CKAN renaming resources |
| Literal dispatch validation | Pre-call guards in both tools | `advisory_type` / `breakdown` both validated at tool layer with `valid=[...]` list before any client call — identical pattern to Plan 04 fire_perimeters / fire_control_orders |

## Handoff to Next Plans

- **Plan 08 (Wave 4 Prompts + Resources):** The two dispatch tables (`WATER_ADVISORY_LAYERS`, `POPULATION_BREAKDOWN_HINTS`) are good candidates for documentation resources — consider `docs://alberta/water-advisory-guide` and `docs://alberta/population-breakdown-guide` to give agents the full layer-ID / breakdown-name map at resource-catalog time. The plan § "Note water advisory layer table and population breakdown hint table — both worth including in `docs://alberta/...` resources from Plan 08" is validated.
- **Plan 09 (Wave 5 Parametrized tests):** `TestAlbertaEnvelopes` / `TestAlbertaLangParam` can now run across all 24 Alberta tools — the 5 new Plan 07 tools all use the standard `make_response` / `make_error` envelope with `lang` propagation, so parametrized tests should pass without per-tool exceptions.
- **24-tool surface confirmed:** 5 discovery (Plan 02) + 4 AER (Plan 03) + 4 wildfire (Plan 04) + 3 health (Plan 05) + 3 transport (Plan 06) + 5 environment/agri/demo/parks (Plan 07) = 24 tools total. Matches 17-CONTEXT.md's locked count.

## User Setup Required

None - no external service configuration required. All portals (open.alberta.ca CKAN, GeoDiscover Alberta ArcGIS) are public and require no auth.

## Self-Check: PASSED

- Commit `73feb0a` found in git log (Task 1)
- Commit `2da0e2a` found in git log (Task 2)
- `src/mcp_canada/modules/alberta/client.py` modified — 5 `fetch_*` bodies filled + 2 dispatch tables + 6 constants added to imports
- `src/mcp_canada/modules/alberta/tools.py` modified — 5 `@tool` bodies filled + 3 API_NAME_GEODISCOVER_* constants + 2 validation lists
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` modified — 20 Plan 07 tests added
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` modified — 11 Plan 07 tests added
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -k "AirQuality or WaterAdvisories or CropProduction or PopulationEstimates or ProvincialParks"` → 31 passed
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py` → 137 passed
- `uv run python -c "from mcp_canada.modules.alberta.tools import alberta_get_air_quality_stations, alberta_get_water_advisories, alberta_get_crop_production, alberta_get_population_estimates, alberta_get_provincial_parks; print('5 tools importable')"` → "5 tools importable"

---
*Phase: 17-alberta-government-open-data*
*Completed: 2026-04-17*
