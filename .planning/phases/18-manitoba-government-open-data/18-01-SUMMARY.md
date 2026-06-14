---
phase: 18-manitoba-government-open-data
plan: "01"
subsystem: manitoba-module-scaffold
tags: [scaffold, arcgis-hub, wave-0, spike, constants, schemas, stubs]
dependency_graph:
  requires: []
  provides:
    - "src/mcp_canada/modules/manitoba/__init__.py — MODULE_NAME + MODULE_DESCRIPTION"
    - "src/mcp_canada/modules/manitoba/constants.py — all FeatureServer URLs + Hub constants"
    - "src/mcp_canada/modules/manitoba/schemas.py — 18 flat Pydantic v2 models"
    - "src/mcp_canada/modules/manitoba/client.py — _hub_get + _511_get + 18 client stubs"
    - "src/mcp_canada/modules/manitoba/__tests__/conftest.py — 16 fixtures for Plans 02-06"
    - ".planning/phases/18-manitoba-government-open-data/18-SPIKE.md — 4 open question resolutions"
  affects: []
tech_stack:
  added: []
  patterns:
    - "ArcGIS Hub Search API (_hub_get) — same pattern as York Region Phase 14"
    - "511 key-gated client (_511_get + Five11NotConfigured) — same pattern as Alberta Phase 17"
    - "CSV fetch for River Conditions — fetch_and_parse(RIVER_CONDITIONS_CSV_URL)"
    - "Wave 0 scaffold — signatures locked, bodies NotImplementedError"
key_files:
  created:
    - src/mcp_canada/modules/manitoba/__init__.py
    - src/mcp_canada/modules/manitoba/constants.py
    - src/mcp_canada/modules/manitoba/schemas.py
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/prompts.py
    - src/mcp_canada/modules/manitoba/resources.py
    - src/mcp_canada/modules/manitoba/__tests__/__init__.py
    - src/mcp_canada/modules/manitoba/__tests__/conftest.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py
    - .planning/phases/18-manitoba-government-open-data/18-SPIKE.md
  modified: []
decisions:
  - "_hub_get signature takes only params dict (no path arg) — Manitoba has one Hub Search URL; pattern cleaner than Alberta's multi-path _api_get"
  - "RIVER_CONDITIONS_CSV_URL instead of RIVER_CONDITIONS_FS_URL — spike proved no FeatureServer backing the river conditions web app; live CSV at www.manitoba.ca/floodinfo"
  - "HOG_PRICES_FS_URL = None (typed str | None) — unresolved in spike; Plan 04 probes MB_Cattle_Prices_Current_year for mixed data or AgriMaps fallback"
  - "Five11NotConfigured exception at module level — tools catch it and return NOT_CONFIGURED make_error; cleaner than try/except os.environ inline"
  - "Module-level _hub_limiter/_511_limiter — shared TokenBuckets at import; Plans 02-06 use these directly rather than calling get_limiter() per call"
  - "prompts.py uses 'from fastmcp.prompts import Message, prompt' — not 'from fastmcp.prompts.prompt import Message' (non-existent submodule)"
metrics:
  duration: "10 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 3
  files_created: 13
---

# Phase 18 Plan 01: Manitoba Module Scaffold Summary

Wave 0 scaffold for the Manitoba provincial open data module — ArcGIS Hub (geoportal.gov.mb.ca / org mMUesHYPkXjaFGfS) pattern with key-gated Manitoba 511 transport tools.

## What Was Built

13 files (12 module/test + 1 spike doc) establishing the locked contract surface for Plans 02-06 parallel implementation.

### Wave 0 Spike Results (18-SPIKE.md)

Four research open questions resolved before writing constants:

| Question | Status | Finding |
|----------|--------|---------|
| Manitoba 511 key | GATED | Account + explicit key request required; NOT instantly provisioned; tools return NOT_CONFIGURED |
| Rural Health FeatureServer | RESOLVED | `Rural_Health_Care_Facilities_in_Manitoba/FeatureServer/0` — live-verified, 2000 max records |
| Hog prices FeatureServer | UNRESOLVED | Not in mMUesHYPkXjaFGfS org (82 services checked); Plan 04 investigates cattle layer or AgriMaps |
| River Conditions FeatureServer | RESOLVED (CSV) | No FeatureServer exists — live CSV at `www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv` |

### Module Foundation (3 files)

- `__init__.py`: `MODULE_NAME = "manitoba"` + bilingual `MODULE_DESCRIPTION`/`MODULE_DESCRIPTION_FR`
- `constants.py`: All constants from 18-RESEARCH.md "Pattern 1" verbatim: Hub URLs, `ARCGIS_ORG_ID = "mMUesHYPkXjaFGfS"`, all FeatureServer URLs (11 confirmed + `HOG_PRICES_FS_URL = None`), `RIVER_CONDITIONS_CSV_URL`, 2 rate groups, 5 cache TTLs, `MAX_RECORDS = 5000`, `CACHE_KEY_PREFIX = "manitoba:"`, `MANITOBA_BBOX`, `FIVE11_KEY_ENV`, `PARK_TYPES`, `WATERWAY_TYPES`
- `schemas.py`: 18 flat Pydantic v2 models — `ManitobaDatasetSummary`, `ManitobaDatasetDetails`, `ManitobaOrganization`, `ManitobaCategory`, `ManitobaPark`, `ManitobaFloodAlert`, `ManitobaRiverStation`, `ManitobaWaterway`, `ManitobaDroughtPolygon`, `ManitobaAgWeatherStation`, `ManitobaLivestockPrice`, `ManitobaCropRegion`, `ManitobaWaitTime`, `ManitobaWaterbody`, `ManitobaForest`, `ManitobaHealthFacility`, `Manitoba511Event`, `Manitoba511WinterRoad`, `Manitoba511Camera`

### Client Helpers (fully implemented)

`_hub_get(params)`: Calls ArcGIS Hub Search API — returns dict directly (NOT CKAN envelope). Raises `httpx.HTTPStatusError` on non-dict response. Phase 15-05 contract respected.

`_511_get(endpoint, params)`: Reads `MANITOBA_511_KEY` from env. Raises `Five11NotConfigured` if absent. Returns raw JSON list (not ArcGIS/CKAN envelope). Alberta 511 pattern adapted for Manitoba v3 key requirement.

`Five11NotConfigured(Exception)`: Module-level exception; tools catch and return `make_error("NOT_CONFIGURED")`.

### Client Stubs (18 functions — signatures locked)

Grouped by plan:
- **Plan 02** (5): `fetch_search_datasets`, `fetch_dataset_details`, `fetch_query_dataset`, `fetch_organizations`, `fetch_categories`
- **Plan 03** (3): `fetch_flood_alerts`, `fetch_river_stations`, `fetch_provincial_waterways`
- **Plan 04** (4): `fetch_drought_status`, `fetch_ag_weather_stations`, `fetch_livestock_prices`, `fetch_crop_regions`
- **Plan 05** (5): `fetch_provincial_parks`, `fetch_fisheries_data`, `fetch_provincial_forests`, `fetch_surgical_wait_times`, `fetch_health_facilities`
- **Plan 06** (3): `fetch_road_events`, `fetch_winter_road_conditions`, `fetch_traffic_cameras`

All stubs raise `NotImplementedError("Plan NN implements")` with full signatures returning `tuple[dict[str, Any], bool]` or `tuple[list[dict], bool]`.

### Skeleton Files (zero definitions)

- `tools.py`: standalone `tool` import + `make_response`/`make_error` + `client as _client`
- `prompts.py`: `Message, prompt` from `fastmcp.prompts`
- `resources.py`: `json` + `resource` from `fastmcp.resources`

### Test Scaffolds

`conftest.py`: 16 fixtures covering all Plans 02-06 response shapes:
- Hub Search: `HUB_SEARCH_RAW`, `HUB_SEARCH_EMPTY`, `HUB_ITEM_DETAIL`
- ArcGIS features: `SAMPLE_PARKS_FEATURES`, `SAMPLE_FLOOD_ALERTS_EMPTY` (critical edge case), `SAMPLE_FLOOD_ALERTS_ACTIVE`, `SAMPLE_WATERWAYS_FEATURES`, `SAMPLE_DROUGHT_FEATURES`, `SAMPLE_AG_WEATHER_FEATURES`, `SAMPLE_LIVESTOCK_FEATURES`, `SAMPLE_CROP_REGIONS_FEATURES`, `SAMPLE_WAIT_TIMES_FEATURES`, `SAMPLE_FISHERIES_FEATURES`, `SAMPLE_FORESTS_FEATURES`, `SAMPLE_RIVER_STATIONS_FEATURES`, `SAMPLE_HEALTH_FACILITIES_FEATURES`
- 511 lists: `SAMPLE_511_EVENTS`, `SAMPLE_511_WINTER_ROADS`, `SAMPLE_511_CAMERAS`
- Autouse `patch_cache_and_limiter` fixture (York Region pattern)

`test_client.py`: 19 placeholder classes (TestSharedApiGetContract + 18 per-client-function)
`test_tools.py`: 22 placeholder classes (including TestManitobaEnvelopes + TestManitobaLangParam for Plan 08)
`test_prompts_resources.py`: TestManitobaPrompts + TestManitobaResources

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed prompts.py incorrect Message import path**
- **Found during:** Task 3 post-task pyright check
- **Issue:** `from fastmcp.prompts.prompt import Message` — `fastmcp.prompts.prompt` submodule does not exist
- **Fix:** `from fastmcp.prompts import Message, prompt` (matches york_region/bc/alberta pattern)
- **Files modified:** `src/mcp_canada/modules/manitoba/prompts.py`
- **Commit:** 29e428c

### Pattern Deviations from Alberta

**_hub_get takes only params (no path arg):** Alberta's `_api_get` takes both `path` and `params` because it serves multiple CKAN endpoints. Manitoba's Hub Search has a single search URL (`HUB_SEARCH_URL`), so `_hub_get(params)` is cleaner. Item detail calls will use a separate URL construction in Plan 02.

**`RIVER_CONDITIONS_CSV_URL` instead of `RIVER_CONDITIONS_FS_URL`:** Spike revealed the River Conditions web app uses a CSV feed, not ArcGIS FeatureServer. `fetch_river_stations` uses `fetch_and_parse` in Plan 03.

**`HOG_PRICES_FS_URL: Final[str | None] = None`:** Hog prices service not found in `mMUesHYPkXjaFGfS` org. Type annotation allows Plan 04 to set it after investigation without changing the constant name.

## Self-Check: PASSED

All 13 created files verified present. All 4 task commits exist (e40b94d, fdd1a04, e052963, 29e428c). Module imports cleanly. Pyright: 0 errors.
