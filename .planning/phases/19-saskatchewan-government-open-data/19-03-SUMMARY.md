---
phase: 19-saskatchewan-government-open-data
plan: 03
subsystem: arcgis-hub
tags: [arcgis-hub, saskatchewan, agriculture, mining, crop-yields, grain-elevators, mineral-mines, featureserver-dispatch]
dependency_graph:
  requires:
    - phase: 19-01
      provides: "Saskatchewan module scaffold, constants (CROP_YIELDS_PROVINCE/REGIONS_FS_URL, GRAIN_ELEVATORS_FS_URL, MINERAL_MINES_FS_URLS dict, CROP_REGIONS), client stubs, conftest fixtures"
    - phase: 19-02
      provides: "5 discovery tools operational; _hub_get + _hub_limiter helpers confirmed working"
  provides:
    - "fetch_crop_yields: region dispatch → Province Summary vs Regions Only FeatureServer; 16-crop out_fields; CACHE_TTL_ANNUAL"
    - "fetch_grain_elevators: where=PR='SK' default; AND Railway filter; 6-field out_fields; CACHE_TTL_META"
    - "fetch_mineral_mines: MINERAL_MINES_FS_URLS dispatch; 9-field out_fields; ValueError for unknown mineral; CACHE_TTL_META"
    - "saskatchewan_get_crop_yields @tool: region enum, INVALID_INPUT guard, FR messages"
    - "saskatchewan_get_grain_elevators @tool: railway Literal filter"
    - "saskatchewan_get_mineral_mines @tool: mineral Literal, double-guard, FR messages"
  affects:
    - "19-07 (test + integration plan): will need to cover crop/grain/mineral tools"
tech-stack:
  added: []
  patterns:
    - "Region dispatch: 'provincial' → Province Summary FS (where=1=1); 5 region strings → Regions Only FS (where=Region='<Title>')"
    - "Mineral dispatch: MINERAL_MINES_FS_URLS[mineral.lower()] at client; tool double-guards with INVALID_INPUT before client call"
    - "Double-guard pattern (tool INVALID_INPUT + client ValueError): mirrors Alberta ST3 pattern"
    - "FR error messages: inline lang=='fr' ternary in tool layer; no t() import"
key-files:
  created: []
  modified:
    - src/mcp_canada/modules/saskatchewan/client.py
    - src/mcp_canada/modules/saskatchewan/tools.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_client.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py
key-decisions:
  - "CACHE_TTL_ANNUAL (7d) for crop yields — annual estimates change at most once per growing season; minerals and elevators use CACHE_TTL_META (24h)"
  - "Crop yields tool documents that weekly PDF crop reports are NOT machine-readable — the FeatureServer is the machine-readable substitute (in docstring where agents see it)"
  - "Double-guard on crop region: tool pre-checks region.lower() in _CROP_REGIONS tuple before calling client; client also raises ValueError as secondary guard"
  - "Double-guard on mineral: tool pre-checks mineral.lower() in _MINERALS tuple before calling client; client also raises ValueError via MINERAL_MINES_FS_URLS.get()"
  - "case-insensitive dispatch in client: mineral.lower() and region.lower() before lookup"
patterns-established:
  - "FeatureServer URL for envelope api_url: uses the FS URL + /0 suffix in make_response (not HUB_SEARCH_URL)"
  - "out_fields always explicit (never '*') to keep payloads lean and predictable for agents"
requirements-completed: [SK-06, SK-07, SK-08, SK-09]
duration: 18min
completed: 2026-06-15
---

# Phase 19 Plan 03: Saskatchewan Agriculture + Mining Tools Summary

**3 curated FeatureServer tools (crop yields with 5-region dispatch, grain elevators with railway filter, mineral mines with potash/uranium/helium/coal dispatch) covering Saskatchewan's signature agriculture and energy/mining domains**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-15T15:08:46Z
- **Completed:** 2026-06-15T15:27:00Z
- **Tasks:** 2 (TDD: client stubs, curated tools)
- **Files modified:** 4

## Accomplishments

- `fetch_crop_yields`: region dispatch between two FeatureServers — `provincial` → Province Summary FS (where=1=1); southeast/southwest/central/northeast/northwest → Regions Only FS (where=Region='<Title>'); explicit 16-crop out_fields; CACHE_TTL_ANNUAL (7d); ValueError for unknown region
- `fetch_grain_elevators`: default where=`PR='SK'`; optional `AND Railway='<railway>'` suffix; 6-field out_fields; CACHE_TTL_META (24h)
- `fetch_mineral_mines`: dispatch via `MINERAL_MINES_FS_URLS[mineral.lower()]`; 9-field out_fields (Name, Company, Status, Mine_Type, Mine_Site, Regulation, DateOpened, Website); ValueError for unknown mineral
- 3 `@tool` functions with double-guard (pre-check enum + catch ValueError from client), FR error messages via inline ternary, `api_name='saskatchewan-geohub'`

## Crop-Region Dispatch Table

| region | FeatureServer | where clause |
|--------|--------------|-------------|
| `provincial` | `Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer` | `1=1` |
| `southeast` | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer` | `Region='Southeast'` |
| `southwest` | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer` | `Region='Southwest'` |
| `central` | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer` | `Region='Central'` |
| `northeast` | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer` | `Region='Northeast'` |
| `northwest` | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer` | `Region='Northwest'` |

**out_fields:** `Region,HRSW,Durum,Oat,Barley,Canola,Mustard,Soybean,Pea,Lentil,Chickpea,Canary_seed,Flax,Winter_wheat,Fall_rye,Other_wheat_`

## Mineral Mines Dispatch Table

| mineral | FeatureServer |
|---------|--------------|
| `potash` | `Potash_2024_06_13/FeatureServer` |
| `uranium` | `Uranium_2024_06_13/FeatureServer` |
| `helium` | `Helium_2024_12_31/FeatureServer` |
| `coal` | `Coal_2024_06_13/FeatureServer` |

**out_fields:** `Commodity,Name,Status,Mine_Type,Company,Mine_Site,Regulation,DateOpened,Website`

## Grain Elevators

**FeatureServer:** `Western_Canada_Grain_Elevator_2024/FeatureServer`
**out_fields:** `Station,PR,Railway,Licensee,Elevator_type,Capacity_tonne`
**Default where:** `PR='SK'`; optional AND clause for CN/CP/SHORTLINE railway filter

## Task Commits

Each task was committed atomically:

1. **Task 1: Agriculture + mining client bodies + client tests** - `217ff15` (feat)
2. **Task 2: 3 curated @tool functions + tool tests** - `d03a651` (feat)

## Files Created/Modified

- `src/mcp_canada/modules/saskatchewan/client.py` — filled 3 stubs: `fetch_crop_yields`, `fetch_grain_elevators`, `fetch_mineral_mines`
- `src/mcp_canada/modules/saskatchewan/tools.py` — added 3 @tool functions + `__all__` entries + constant imports
- `src/mcp_canada/modules/saskatchewan/__tests__/test_client.py` — 20 new tests (6 crop yield, 6 grain elevator, 8 mineral mines)
- `src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py` — 15 new tests (5 crop, 4 elevator, 6 mineral)

## Decisions Made

- CACHE_TTL_ANNUAL (7d) for crop yields: annual estimates change at most once per growing season; grain elevators and minerals use CACHE_TTL_META (24h).
- Crop yields tool docstring explicitly notes weekly PDF crop reports are NOT machine-readable — the FeatureServer is the substitute. Placed in docstring where agents will see it.
- Double-guard: tool pre-checks enum in `_CROP_REGIONS`/`_MINERALS` tuple before calling client; client also raises ValueError as secondary guard. Same pattern as Alberta ST3.
- `case-insensitive dispatch`: `mineral.lower()` and `region.lower()` at both client and tool layer.
- FeatureServer URL (not HUB_SEARCH_URL) used as `api_url` in `make_response` — more precise source attribution.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Plan 03 delivers SK-06 (crop yields), SK-07 (grain elevators), SK-08 (potash), SK-09 (uranium) — all via `saskatchewan_get_mineral_mines(mineral="potash"|"uranium")`.
- Remaining curated tools: Plan 04 (fire bans, wildfires, air quality) and Plan 05 (WSA stations, WSA reservoirs).
- Client stubs for Plans 04-05 remain as `NotImplementedError` in client.py — ready to fill.

## Self-Check: PASSED

All 4 required files modified exist. Commits 217ff15 and d03a651 verified in git log.
82 Saskatchewan module tests pass. Coverage 96.74%. Imports clean.

---
*Phase: 19-saskatchewan-government-open-data*
*Completed: 2026-06-15*
