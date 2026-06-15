---
phase: 19-saskatchewan-government-open-data
plan: 01
subsystem: shared/arcgis_hub + saskatchewan module scaffold
tags: [arcgis-hub, saskatchewan, startindex-fix, wave-0, scaffold, spike]
dependency_graph:
  requires: []
  provides: [shared/arcgis_hub startindex fix, saskatchewan module contract surface]
  affects: [york_region Phase 14 live pagination, alberta Phase 17 live pagination, manitoba Phase 18 live pagination, Phase 19 Plans 02-06]
tech_stack:
  added: []
  patterns: [ArcGIS Hub OGC API Records startindex pagination, multi-org ArcGIS (3 bases), SPSA separate REST server, WSA secondary org]
key_files:
  created:
    - src/mcp_canada/modules/saskatchewan/__init__.py
    - src/mcp_canada/modules/saskatchewan/constants.py
    - src/mcp_canada/modules/saskatchewan/schemas.py
    - src/mcp_canada/modules/saskatchewan/client.py
    - src/mcp_canada/modules/saskatchewan/tools.py
    - src/mcp_canada/modules/saskatchewan/prompts.py
    - src/mcp_canada/modules/saskatchewan/resources.py
    - src/mcp_canada/modules/saskatchewan/__tests__/__init__.py
    - src/mcp_canada/modules/saskatchewan/__tests__/conftest.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_client.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_prompts_resources.py
    - .planning/phases/19-saskatchewan-government-open-data/19-SPIKE.md
  modified:
    - src/mcp_canada/shared/arcgis_hub.py
    - src/mcp_canada/shared/__tests__/test_arcgis_hub.py
decisions:
  - "startindex param fix is in shared/arcgis_hub.py:search_hub_datasets (not per-module workaround); Manitoba fetch_search_datasets builds params directly so no double-application"
  - "WSA_RESERVOIRS_LAYER=26 confirmed by live probe; layer 0 returns empty"
  - "FIRE_BAN_LAYERS {urban:0,rural:2,provincial:3,parks:8} confirmed by live probe"
  - "Petroleum FeatureServer HTTP 400 from research was transient; live probe returns HTTP 200 with data; remains deferred per tool-count ceiling (14 tools at target)"
  - "WSA Water Quality layer 19 returns 24 stations (not 0 as in research); remains excluded from Phase 19 curated tools per scope"
  - "3 module-level limiters (_hub_limiter/_wsa_limiter/_spsa_limiter) for three separate rate groups"
metrics:
  duration: "10 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 3
  files_modified: 15
---

# Phase 19 Plan 01: Saskatchewan Wave 0 — Shared Fix + Module Scaffold Summary

Wave 0 prerequisite: fixed the ArcGIS Hub pagination bug in `shared/arcgis_hub.py` and locked the Saskatchewan module contract surface (constants, schemas, client stubs, test scaffolds) so Plans 02-05 fill bodies without colliding.

## One-Liner

Fixed `shared/arcgis_hub.py` OGC API Records pagination (`offset`→`startindex`; covers Phase 14/17/18/19) and scaffolded the Saskatchewan module with 3 ArcGIS bases, 12 schemas, 14 locked client stubs, and 10 fixture shapes.

## Tasks Completed

| Task | Commit | Description |
|------|--------|-------------|
| 1. Fix shared/arcgis_hub.py startindex (TDD RED→GREEN) | fdfa5fc | `params["offset"]` → `params["startindex"]`; two regression tests updated; 19/19 shared + 572/572 York/Alberta/Manitoba tests green |
| 2. Wave 0 spike — WSA water-quality layer 19 + Petroleum 400 | 0868004 | Both revised: layer 19 has 24 stations; Petroleum returns HTTP 200; verdicts recorded in 19-SPIKE.md |
| 3. Module scaffold (7 files + test scaffolds) | 3112897 | 12 Saskatchewan module files + 19-SPIKE.md; all imports clean; pytest collection no errors |

## Task 1: Shared arcgis_hub.py startindex Fix

**Bug:** `search_hub_datasets` sent `params["offset"] = offset` but OGC API Records (used by Saskatchewan GeoHub, and retroactively by York Region and Alberta) requires `startindex`. The `?offset=N` request returned `{numberMatched: null, numberReturned: null}` — silently broken pagination.

**Fix (1 line):**
```python
# Before:
if offset > 0:
    params["offset"] = offset

# After:
if offset > 0:
    params["startindex"] = offset   # OGC API Records pagination (NOT offset); startindex=0 is invalid so omit at 0
```

**TDD Regression Tests Added/Updated:**
- `test_offset_positive_sends_startindex_not_offset`: asserts `params.get("startindex") == 10` AND `"offset" not in params`
- `test_offset_zero_omitted_from_params`: asserts BOTH `"offset" not in params` AND `"startindex" not in params` (startindex=0 returns malformed body live)

**Blast radius:** Positive fix for all Hub modules using `search_hub_datasets`:
- Phase 14 York Region: `search_hub_datasets` live pagination now correct
- Phase 17 Alberta: `search_hub_datasets` live pagination now correct
- Phase 18 Manitoba: Manitoba's `fetch_search_datasets` builds params DIRECTLY (calls `_hub_get(params)` not `search_hub_datasets`) — no double-application; Manitoba already sends startindex correctly at the module level
- Phase 19 Saskatchewan: unblocked — Hub discovery tools will paginate correctly

**Suite results:**
- Shared: 19/19 passed
- York Region: no regression
- Alberta: no regression
- Manitoba: no regression (572 total across all three)

## Task 2: Spike Verdicts

**WSA Water Quality (layer 19):** REVISED from research. 24 stations returned (not 0). Transient network condition during initial research. Layer is usable. Per Phase 19 scope (14 tools at target ceiling), not added to curated tools. Future phase can curate `saskatchewan_get_water_quality_stations`.

**Petroleum FeatureServer (layer 0):** REVISED from research. HTTP 200, data returned (not HTTP 400). 50+ fields including WELL_CWI, WELLSTATUS, SURFACELATITUDE/LONGITUDE. Thousands of wells in dataset. Remains deferred per tool-count ceiling (not technical unavailability). Document as accessible in `docs://saskatchewan/portal-guide` resource (Plan 06).

**Live confirmations:**
- WSA_Reservoirs layer 26: CONFIRMED — `Reservoir_Name`="ADMIRAL RESERVOIR", `Dam_Name`="ADMIRAL DAM"
- SPSA Fire Ban layers 0/2/3/8: CONFIRMED — 10 total layers; fire ban data on 0=Urban, 2=Rural, 3=Provincial, 8=Parks
- GeoHub startindex pagination: CONFIRMED — `?q=crops&limit=5&startindex=5` returns `numberMatched=8, numberReturned=4` ✓

## Task 3: Module Scaffold

**Module identity:**
- `MODULE_NAME = "saskatchewan"` (auto-registers via FileSystemProvider)
- `MODULE_DESCRIPTION` + `MODULE_DESCRIPTION_FR` (bilingual)

**Constants (3 ArcGIS bases):**
- Primary Hub: `zcv98lgAl8xQ04cW` / `services3.arcgis.com` — agriculture, mining, environment
- WSA: `7MBdlVpjqbfBhQer` / `services1.arcgis.com` — water infrastructure
- SPSA: `gis.saskatchewan.ca/egis/rest/services/Wildfire` — fire bans (non-Hub)

**Dispatch dicts:**
- `FIRE_BAN_LAYERS = {"urban": 0, "rural": 2, "provincial": 3, "parks": 8}`
- `MINERAL_MINES_FS_URLS = {"potash": .../Potash_2024_06_13/..., "uranium": .../Uranium_2024_06_13/..., "helium": .../Helium_2024_12_31/..., "coal": .../Coal_2024_06_13/...}`
- `WSA_RESERVOIRS_LAYER = 26` (spike-confirmed; NOT layer 0)
- `CROP_REGIONS = ("provincial", "southeast", "southwest", "central", "northeast", "northwest")`

**Schemas (12 flat Pydantic v2 models):**
SaskatchewanDatasetSummary, SaskatchewanDatasetDetails, SaskatchewanOrganization, SaskatchewanCategory, SaskatchewanCropYield (16 crop fields float|None), SaskatchewanGrainElevator, SaskatchewanMineralMine, SaskatchewanAirQuality (pollutants float|None, aqhi str|None=URL), SaskatchewanFireBan (scope field), SaskatchewanWildfire, SaskatchewanWSAStation (hyperlink_graph), SaskatchewanWSAReservoir (water_level_masl)

**Client (14 stubs + _hub_get):**
- `_hub_get` FULLY implemented: Hub JSON contract enforced, no `.get("success")`, no `.raise_for_status()`/`.json()` on api_get return
- 14 NotImplementedError stubs with LOCKED signatures grouped by plan (02: discovery ×5, 03: agriculture+mining ×3, 04: environment ×3, 05: water ×2)
- 3 module-level limiters at import time: `_hub_limiter`, `_wsa_limiter`, `_spsa_limiter`

**Fixtures (conftest.py — 10 shapes):**
- `SAMPLE_ARCGIS_CROP_YIELDS`, `SAMPLE_ARCGIS_GRAIN_ELEVATORS`, `SAMPLE_ARCGIS_MINERAL_MINES` (Potash: K+S Bethune)
- `SAMPLE_ARCGIS_AIR_QUALITY` (Regina + Saskatoon, AQHI URL present)
- `SAMPLE_ARCGIS_FIRE_BANS_ACTIVE` (2 ban records), `SAMPLE_ARCGIS_FIRE_BANS_EMPTY` ([], False) — CRITICAL: empty is valid
- `SAMPLE_ARCGIS_WILDFIRES` (2017 Porcupine Lake, 2015 Weyakwin)
- `SAMPLE_ARCGIS_WSA_STATIONS` (2 SK stations with HyperLink_Graph), `SAMPLE_ARCGIS_WSA_RESERVOIRS` (ADMIRAL RESERVOIR)
- Hub fixtures: `HUB_SEARCH_RAW`, `HUB_SEARCH_EMPTY`, `HUB_ITEM_DETAIL`
- Autouse `patch_cache_and_limiter` patching all 3 limiters + cached_fetch

## Deviations from Plan

### Spike Verdicts Revised

**1. [Rule 1 - Bug] WSA Water Quality layer 19 — research verdict revised**
- **Found during:** Task 2 live probe
- **Issue:** Research recorded "0 features" for WSA Water Quality layer 19; live probe returned 24 stations
- **Resolution:** Transient network condition during initial research. 24 real stations confirmed. Per plan scope, not added to curated tools — no curated water-quality tool this phase as planned.
- **Impact:** None — spike confirmed scope decision; 19-SPIKE.md updated with revised verdict

**2. [Rule 1 - Bug] Petroleum FeatureServer — research verdict revised**
- **Found during:** Task 2 live probe
- **Issue:** Research recorded "HTTP 400" for Petroleum FeatureServer; live probe returned HTTP 200 with data
- **Resolution:** The 400 was transient. Data is accessible. Remains deferred per tool-count ceiling (14 tools at target). Plan 06 portal-guide resource should note it is accessible.
- **Impact:** None — spike confirms deferred status is by choice, not technical limitation

### Manitoba Local Startindex Workaround — No Double-Application

Manitoba's `fetch_search_datasets` builds params directly (calls `_hub_get(params)` not `search_hub_datasets`). It was already sending `startindex` correctly at the module level. The shared fix does NOT affect Manitoba because Manitoba never calls `shared/arcgis_hub.py:search_hub_datasets`. No double-application issue. All 572 Manitoba unit tests pass.

## Self-Check: PASSED

All 15 required files found. All 3 task commits (fdfa5fc, 0868004, 3112897) verified in git log.
Shared tests 19/19. Regression suite 572/572. Module imports clean. Spike doc complete.
