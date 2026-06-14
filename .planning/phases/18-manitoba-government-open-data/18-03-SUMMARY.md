---
phase: 18-manitoba-government-open-data
plan: "03"
subsystem: manitoba-flood-hydrology
tags: [flood, hydrology, arcgis-hub, csv, waterways, bilingual, wave-2]
dependency_graph:
  requires:
    - "18-01 (scaffold — client stubs, conftest fixtures, WATERWAY_TYPES constant)"
    - "18-02 (discovery tools — _hub_limiter established at module level)"
  provides:
    - "src/mcp_canada/modules/manitoba/client.py — fetch_flood_alerts, fetch_river_stations, fetch_provincial_waterways bodies"
    - "src/mcp_canada/modules/manitoba/tools.py — manitoba_get_flood_alerts, manitoba_get_river_stations, manitoba_get_provincial_waterways"
  affects:
    - "tests/integration/ — MB-07/MB-08/MB-09 scenarios (future plan)"
tech_stack:
  added: []
  patterns:
    - "arcgis_hub.query_feature_service for Overland_Flood_Alerts and Provincial_Waterways FeatureServers"
    - "fetch_and_parse(RIVER_CONDITIONS_CSV_URL) for river station discovery (CSV, not FeatureServer)"
    - "ValueError raised in client for invalid f_type; tool layer catches and returns make_error(INVALID_INPUT, valid=list(WATERWAY_TYPES))"
    - "Empty features list returned as valid payload — never treated as an error (CRITICAL flood edge case)"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
decisions:
  - "fetch_river_stations uses fetch_and_parse(RIVER_CONDITIONS_CSV_URL) — spike confirmed no FeatureServer backing the River Conditions web app; CSV at www.manitoba.ca/floodinfo is the authoritative source"
  - "Empty flood alert payload {features:[], count:0, truncated:False} is a valid success response — no alert period is the normal off-season state; tool must NOT convert this to an error"
  - "WATERWAY_TYPES validation in client (ValueError) rather than only in tool — ensures client-layer callers also get clean errors; tool catches and maps to INVALID_INPUT with valid= list"
  - "f_type WHERE clause uses title-case display values (Floodway, Dike, Dam...) mapped from user's lowercase input — matches ArcGIS stored values in Provincial_Waterways layer"
  - "_API_NAME_* per tool (not shared _API_NAME_HUB) — distinct source attribution for flood/river/waterways vs. Hub Search tools in _meta.source.api"
metrics:
  duration: "8 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 18 Plan 03: Manitoba Flood/Hydrology Tools Summary

Manitoba's flood/hydrology domain (MB-07, MB-08, MB-09) — 3 client function bodies + 3 @tool functions implementing the province's defining hazard data. Flood alerts are live bilingual polygons from ArcGIS Hub; river stations are CSV-sourced discovery points; waterways are static water-control infrastructure.

## What Was Built

### Client Bodies (3 functions filled)

**`fetch_flood_alerts(include_geometry, lang)`**
- Queries `Overland_Flood_Alerts/FeatureServer/0` via `arcgis_hub.query_feature_service`
- Out fields: `Type_EN, Type_FR, Start_Date, End_Date, Shape__Area` (bilingual)
- Returns `{features, count, truncated}` — empty list is valid during non-flood seasons
- Cache: `CACHE_TTL_LIVE` (5 min) at key `"manitoba:flood_alerts:{include_geometry}"`

**`fetch_river_stations(province, alert_only, lang)`**
- Source: `RIVER_CONDITIONS_CSV_URL` via `fetch_and_parse` (NOT ArcGIS FeatureServer)
- Spike resolution confirmed: no FeatureServer backs the River Conditions web app
- Optional `province` filter (CSV contains multi-province records)
- Optional `alert_only` filter excludes "No Flooding" / "No Current Data" records
- Returns `{stations, count}` — stations are discovery points, NOT real-time level readings

**`fetch_provincial_waterways(f_type, max_records, include_geometry, lang)`**
- Queries `Provincial_Waterways/FeatureServer/0` via `arcgis_hub.query_feature_service`
- Out fields: `F_TYPE, Name, Watershed, WCW, LengthKM`
- `f_type` validated against `WATERWAY_TYPES` tuple — raises `ValueError` on invalid value
- WHERE clause: `F_TYPE='Floodway'` (title-case mapped from user's lowercase input)
- Cache: `CACHE_TTL_META` (24 h) — static reference layer

### @tool Functions (3 added to tools.py)

| Tool | api_name | Source | Error paths |
|------|----------|--------|-------------|
| `manitoba_get_flood_alerts` | `manitoba-flood-alerts` | Overland_Flood_Alerts FeatureServer | UPSTREAM_ERROR |
| `manitoba_get_river_stations` | `manitoba-river-conditions` | RIVER_CONDITIONS_CSV_URL | UPSTREAM_ERROR |
| `manitoba_get_provincial_waterways` | `manitoba-provincial-waterways` | Provincial_Waterways FeatureServer | INVALID_INPUT (bad f_type + valid list), UPSTREAM_ERROR |

All 3 tools: standalone `@tool`, `lang: Literal["en","fr"]`, `make_response/make_error`, `Use for:` + 8+ `Keywords:` on single line, `manitoba_` prefix.

### Tests (20 new tests)

**test_client.py** — 9 tests added to 3 classes:
- `TestManitobaGetFloodAlerts` (3): features+count shape, **empty-alert valid result (critical)**, bilingual fields
- `TestManitobaGetRiverStations` (3): stations payload, empty CSV valid, alert field present
- `TestManitobaGetWaterways` (3): all waterways, f_type WHERE clause applied, invalid f_type ValueError

**test_tools.py** — 11 tests added to 3 classes:
- `TestManitobaGetFloodAlerts` (4): active alerts envelope, **empty alerts returns success NOT error**, lang, UPSTREAM_ERROR
- `TestManitobaGetRiverStations` (3): success envelope, UPSTREAM_ERROR, lang
- `TestManitobaGetProvincialWaterways` (4): success envelope, INVALID_INPUT + valid list, UPSTREAM_ERROR, lang

## Key Validation: Empty Flood Alert Edge Case

The empty-flood-alert edge case is explicitly tested in both client (`test_flood_alerts_empty_when_no_active_alerts`) and tool (`test_empty_flood_alerts_returns_success_not_error`) layers:

```python
# Client test — verifies raw payload shape
data, was_cached = await fetch_flood_alerts()
assert data["features"] == []
assert data["count"] == 0  # valid, not an error

# Tool test — verifies success envelope (not error envelope)
result = await manitoba_get_flood_alerts()
assert "error" not in result  # explicit: must NOT be an error
assert "_meta" in result       # must be a success response
assert result["data"]["features"] == []
```

## River Stations: CSV Source (Spike Resolution Confirmed)

Per 18-SPIKE.md and 18-01-SUMMARY.md: the Manitoba River Conditions web app uses a live CSV feed at `www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv`. No FeatureServer URL exists for this data. Implementation uses `fetch_and_parse(RIVER_CONDITIONS_CSV_URL)` exactly as the spike recommended.

Docstring explicitly states: "Returns station LOCATIONS and status only, NOT real-time water level readings — for actual HYDAT level/flow data use wateroffice.ec.gc.ca (ECCC)." (Pitfall 5 from RESEARCH.md honored.)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

All 4 modified files present. Both task commits exist (193d860, d4fb095). Module imports cleanly. Coverage: 96.63% (≥95%). 59/59 Manitoba tests pass.
