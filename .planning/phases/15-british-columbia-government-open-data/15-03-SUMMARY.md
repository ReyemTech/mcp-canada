---
phase: 15-british-columbia-government-open-data
plan: "03"
subsystem: british_columbia
tags: [wfs, curated-tools, wildfire, forestry, environment, health, transportation, climate, cql]
dependency_graph:
  requires: ["15-01", "15-02"]
  provides: ["bc_get_active_fires", "bc_get_fire_perimeters", "bc_get_forest_tenure", "bc_get_cut_blocks", "bc_get_protected_areas", "bc_get_water_wells", "bc_get_wildfire_weather_stations", "bc_get_local_parks", "bc_get_mining_tenure", "bc_get_fish_habitat", "bc_get_emergency_rooms", "bc_get_walk_in_clinics", "bc_get_highway_profiles", "bc_get_road_structures", "bc_get_climate_stations"]
  affects: []
tech_stack:
  added: []
  patterns: ["_wfs_fetch shared fetch helper with active/static TTL split", "_append_gte / _append_like CQL helpers for non-equality operators", "_TENURE_TYPE_MAP mineral->M / placer->P translation", "130K-record guard with INVALID_INPUT before network call"]
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/british_columbia/client.py
    - src/mcp_canada/modules/british_columbia/tools.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_client.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_tools.py
    - README.md
decisions:
  - "CLIMATE_STATIONS_LAYER intentionally aliases WEATHER_STATIONS_LAYER — same BCGW layer, climate-oriented docstring for the 15th curated bc_ tool"
  - "Two private helpers _append_gte/_append_like added to tools.py for >= and LIKE CQL clauses — _build_cql handles equality only, helpers compose on top"
  - "_TENURE_TYPE_MAP module-level dict translates mineral/placer user input to TENURE_TYPE_CODE M/P before CQL construction"
  - "bc_get_water_wells 130K-record guard returns INVALID_INPUT before any network call when no filter provided"
metrics:
  duration: "~45min"
  completed: "2026-04-10"
  tasks_completed: 2
  files_changed: 5
---

# Phase 15 Plan 03: British Columbia WFS Curated Tools Summary

**One-liner:** 15 curated bc_ WFS tools covering wildfire, forestry, environment, health, transport, and climate via a shared _wfs_fetch helper with active/static TTL split.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | _wfs_fetch + 5 wildfire/forestry tools | a4992c4 | client.py, tools.py, test_client.py, test_tools.py |
| 2 | 10 environment/health/transport/climate tools | 0088a7f | tools.py, test_tools.py, README.md |

## What Was Built

### `_wfs_fetch` in client.py

Private async helper that wraps `wfs_page_all` from `shared/ogc.py` with:
- **TTL selection**: `CACHE_TTL_ACTIVE` (5min) for `ACTIVE_FIRES_LAYER`, `CACHE_TTL_STATIC` (24h) for all other layers — `_ACTIVE_LAYERS` frozenset for O(1) lookup
- **Cache key**: `bc:wfs:{layer}:{cql}:{max_records}:{include_geometry}`
- **Rate limiting**: `get_limiter(RATE_GROUP_WFS, RATE_LIMIT_WFS)` — 5 req/s
- **Return type**: `((features, truncated), was_cached)` — tuple of tuple + bool
- **WfsError propagation**: NOT caught here; propagates to curated tools for per-tool translation to `make_error(UPSTREAM_ERROR, exception_code=e.code)`

### CQL helpers in tools.py

Two module-level private helpers compose non-equality CQL clauses on top of `_build_cql(filters)`:
- `_append_gte(cql, field, value)` — appends `FIELD >= value` clause
- `_append_like(cql, field, value)` — appends `FIELD LIKE 'value%'` clause with single-quote escaping

### 15 Curated Tools

All 15 follow the same pattern: build equality `filters` dict → `_build_cql` → manually append LIKE/GTE clauses → `_wfs_fetch` → catch `WfsError` → `make_response`.

**Wildfire (2):**
- `bc_get_active_fires` — ACTIVE_FIRES_LAYER, CACHE_TTL_ACTIVE, CQL: FIRE_STATUS/FIRE_CENTRE/CURRENT_SIZE >=
- `bc_get_fire_perimeters` — FIRE_PERIMETERS_LAYER, year REQUIRED to bound 676+ historical polygons/year

**Forestry (3):**
- `bc_get_forest_tenure` — FOREST_TENURE_LAYER, CLIENT_NAME LIKE, default status ACTIVE
- `bc_get_cut_blocks` — FTEN_CUT_BLOCK_POLY_SVW (not deprecated FTEN_CUT_BLOCK_POLYGONS — Pitfall 9)
- `bc_get_protected_areas` — WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW (not WHSE_PARKS_ECOLOGY which 400s — Pitfall 8)

**Environment (3):**
- `bc_get_water_wells` — 130K-record guard: returns INVALID_INPUT when no filter provided; CQL on CITY/WELL_CLASS/AQUIFER_ID
- `bc_get_wildfire_weather_stations` — WEATHER_STATIONS_LAYER, STATION_NAME LIKE, ELEVATION >=
- `bc_get_local_parks` — LOCAL_PARKS_LAYER, equality on MUNICIPALITY/REGIONAL_DISTRICT/PARK_TYPE

**Natural Resources (2):**
- `bc_get_mining_tenure` — `_TENURE_TYPE_MAP` translates mineral→M / placer→P; OWNER_NAME LIKE; AREA_IN_HECTARES >=
- `bc_get_fish_habitat` — FISH_HABITAT_LAYER, equality on FEATURE_CODE

**Health (2):**
- `bc_get_emergency_rooms` — EMERGENCY_ROOMS_LAYER, WHEELCHAIR_ACCESSIBLE_IND maps bool→Y/N
- `bc_get_walk_in_clinics` — WALK_IN_CLINICS_LAYER, equality on LOCALITY

**Transportation (2):**
- `bc_get_highway_profiles` — HIGHWAY_PROFILES_LAYER, NUMBER_OF_LANES >=
- `bc_get_road_structures` — ROAD_STRUCTURES_LAYER, equality on STRUCTURE_TYPE_CODE

**Climate (1):**
- `bc_get_climate_stations` — aliases WEATHER_STATIONS_LAYER (same BCGW layer as bc_get_wildfire_weather_stations); docstring explicitly documents shared layer and redirects to ECCC for climate normals

## Verification

```
uv run pytest src/mcp_canada/modules/british_columbia/__tests__/ -x -q
# 117 passed, 2 xfailed in 0.78s

uv run ruff check src/mcp_canada/modules/british_columbia/
# All checks passed!

grep -c "^async def bc_" src/mcp_canada/modules/british_columbia/tools.py
# 20

uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q
# 96.39% coverage — 1886 passed, 2 xfailed
```

## Deviations from Plan

None — plan executed exactly as written.

## Decisions Made

1. **Two private helpers _append_gte/_append_like** — Plan suggested extending `_build_cql` or adding a `_build_cql_advanced`. Chose two focused private helpers instead: simpler, no API change to existing `_build_cql`, composable.

2. **_TENURE_TYPE_MAP module-level dict** — Mining tenure type translation placed at module level (not inline) to enable direct assertion in tests: `tools._TENURE_TYPE_MAP["mineral"] == "M"`.

3. **bc_get_climate_stations docstring** — Explicitly includes "ECCC" and the shared BCGW layer name per plan requirement, so `test_docstring_mentions_shared_layer_and_eccc` can assert both terms.

## Self-Check: PASSED

Files confirmed:
- src/mcp_canada/modules/british_columbia/client.py — contains `_wfs_fetch`
- src/mcp_canada/modules/british_columbia/tools.py — contains 20 bc_ tools
- .planning/phases/15-british-columbia-government-open-data/15-03-SUMMARY.md — this file

Commits confirmed:
- a4992c4 — feat(15-03): implement _wfs_fetch + 5 curated wildfire/forestry tools
- 0088a7f — feat(15-03): implement 10 curated environment/health/transport/climate tools
