---
phase: 19-saskatchewan-government-open-data
plan: 05
subsystem: saskatchewan module — WSA water tools (SK-13, SK-14)
tags: [arcgis-hub, saskatchewan, wsa, water, hydrometric, reservoirs, wave-4]
dependency_graph:
  requires: [19-04 (environment tools), 19-01 (constants: WSA_STATIONS_FS_URL, WSA_RESERVOIRS_FS_URL, WSA_RESERVOIRS_LAYER=26)]
  provides: [fetch_wsa_stations, fetch_wsa_reservoirs, saskatchewan_get_wsa_stations, saskatchewan_get_wsa_reservoirs]
  affects: [19-07 (integration tests), 19-06 (prompts/resources referencing WSA tools)]
tech_stack:
  added: []
  patterns: [WSA secondary ArcGIS org (services1/7MBdlVpjqbfBhQer), WSA_RESERVOIRS_LAYER=26 non-zero layer, HyperLink_Graph live hydrograph URL, api_name=saskatchewan-wsa envelope distinction]
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/saskatchewan/client.py
    - src/mcp_canada/modules/saskatchewan/tools.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_client.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py
decisions:
  - "api_name='saskatchewan-wsa' used for both WSA tools to distinguish WSA org from primary Hub in _meta envelope — mirrors Phase 17 GeoDiscover per-tool api_name pattern"
  - "_wsa_limiter (module-level) used for both WSA client functions (not _hub_limiter) — each ArcGIS org has its own rate group"
  - "WSA_RESERVOIRS_LAYER constant (=26) used directly in query_feature_service call and api_url; never hardcoded as 0 — layer 26 is spike-confirmed"
  - "layer 26 bug pinned at mock level via call_args assertion (test_CRITICAL_uses_layer_26_not_layer_0) — mocks cannot prove live behavior but can encode the contract at the call-arg level"
metrics:
  duration: "3 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_modified: 4
---

# Phase 19 Plan 05: Saskatchewan WSA Water Tools (SK-13, SK-14) Summary

Implemented 2 curated WSA water tools against the SEPARATE WSA ArcGIS org (services1.arcgis.com/7MBdlVpjqbfBhQer): hydrometric gauging stations with live graph links, and reservoirs at layer 26.

## One-Liner

2 WSA water tools (hydrometric stations + reservoirs at layer 26) against the WSA org (7MBdlVpjqbfBhQer), completing Saskatchewan's 9-curated-tool + 5-discovery = 14-tool surface.

## Tasks Completed

| Task | Commit | Description |
|------|--------|-------------|
| 1. WSA client bodies + client tests (TDD RED→GREEN) | 5e9bf67 | fetch_wsa_stations + fetch_wsa_reservoirs; 12 client tests; layer 26 pinned via call_args |
| 2. 2 WSA @tool functions + tool tests (TDD RED→GREEN) | 7efe9b1 | saskatchewan_get_wsa_stations + saskatchewan_get_wsa_reservoirs; 11 tool tests; 96.71% coverage |

## SK-13: saskatchewan_get_wsa_stations

**Client:** `fetch_wsa_stations(basin=None, max_records=5000)`
- Queries `WSA_STATIONS_FS_URL` (`Hydrometric_Gauging_Stations_V2/FeatureServer`) at layer 0
- Uses WSA org `services1.arcgis.com/7MBdlVpjqbfBhQer` — NOT the primary Hub org
- Default `where="Province='SK'"` — filters to Saskatchewan stations
- Optional `basin=`: appends `AND Major_Basin LIKE '%<basin>%'`
- `out_fields`: Station_Number, Station_Name, Province, Latitude, Longitude, Major_Basin, Station_Type, Station_Class, Operated_By, **HyperLink_Graph**
- Rate: `_wsa_limiter` (RATE_GROUP_WSA, 5 r/s); Cache: `CACHE_TTL_META` (24h)
- Returns `{"features": [...], "count": N, "truncated": bool}`

**Tool:** `saskatchewan_get_wsa_stations(basin=None, lang="en")`
- api_name: `"saskatchewan-wsa"` (distinguishes WSA org in _meta envelope)
- HyperLink_Graph links to live hourly hydrographs at `wsask.ca`
- Docstring notes: live hydrograph URLs at wsask.ca (where agents will see it)

## SK-14: saskatchewan_get_wsa_reservoirs

**Client:** `fetch_wsa_reservoirs(max_records=5000)`
- Queries `WSA_RESERVOIRS_FS_URL` (`WSA_Reservoirs/FeatureServer`) at **layer 26** (`WSA_RESERVOIRS_LAYER`)
- CRITICAL: Layer 26 is spike-confirmed (2026-06-15); layer 0 returns empty — always use `WSA_RESERVOIRS_LAYER` constant
- Uses WSA org `services1.arcgis.com/7MBdlVpjqbfBhQer` — NOT the primary Hub org
- `where="1=1"` (fetch all reservoirs)
- `out_fields`: Reservoir_Name, Dam_Name, Imagery_Date, Water_Level_MASL
- Rate: `_wsa_limiter` (RATE_GROUP_WSA, 5 r/s); Cache: `CACHE_TTL_META` (24h)
- Returns `{"features": [...], "count": N, "truncated": bool}`

**Tool:** `saskatchewan_get_wsa_reservoirs(lang="en")`
- api_name: `"saskatchewan-wsa"` (distinguishes WSA org in _meta envelope)
- api_url includes `/26` suffix (from `WSA_RESERVOIRS_LAYER` constant)
- Docstring explicitly notes layer 26 (not 0) — agents who read the docstring won't be confused

## Layer 26 Contract at Mock Level

The critical layer-ID bug is pinned at the call-arg level in `test_CRITICAL_uses_layer_26_not_layer_0`:

```python
layer_id = mock_qfs.call_args[0][1]
assert layer_id == WSA_RESERVOIRS_LAYER  # 26
assert layer_id == 26
```

This test fails immediately if the implementation uses `0` or any value other than `WSA_RESERVOIRS_LAYER`. The live integration test (Plan 07) is what fully proves it against the real API.

## Tool Count Confirmation

Phase 19 now has all 14 tools implemented:

| Group | Tools | Status |
|-------|-------|--------|
| Discovery (Plan 02) | search_datasets, get_dataset_details, query_dataset, list_organizations, list_categories | Done |
| Agriculture (Plan 03) | get_crop_yields, get_grain_elevators, get_mineral_mines | Done |
| Environment (Plan 04) | get_fire_bans, get_historic_wildfires, get_air_quality | Done |
| Water/WSA (Plan 05) | **get_wsa_stations, get_wsa_reservoirs** | Done ← this plan |
| **Total** | **14 tools** | **All done** |

## Test Coverage

| Test Class | Tests | All pass |
|------------|-------|----------|
| TestSaskGetWSAStations (client) | 7 | Yes |
| TestSaskGetWSAReservoirs (client) | 5 | Yes |
| TestSaskGetWSAStationsTool | 6 | Yes |
| TestSaskGetWSAReservoirsTool | 5 | Yes |
| **Total new tests** | **23** | **Yes** |
| **Full module suite** | **146** | **Yes** |
| **Coverage** | **96.71%** | **>= 95%** |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

All 4 modified files verified. Both task commits found in git log.
- 5e9bf67: WSA client bodies + 12 client tests
- 7efe9b1: WSA tool functions + 11 tool tests
- 146/146 Saskatchewan module tests passing
- 96.71% coverage (>= 95% requirement)
- `from mcp_canada.modules.saskatchewan import tools; hasattr(tools,'saskatchewan_get_wsa_stations') and hasattr(tools,'saskatchewan_get_wsa_reservoirs')` → OK
