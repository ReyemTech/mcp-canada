---
phase: 18-manitoba-government-open-data
plan: "04"
subsystem: manitoba-agriculture-drought
tags: [arcgis-hub, drought, agriculture, livestock, crop-regions, wave-3]
dependency_graph:
  requires:
    - "18-01 — Wave 0 scaffold (constants, schemas, client stubs, conftest fixtures)"
    - "18-03 — Flood/hydrology client bodies (confirms arcgis_hub.query_feature_service pattern)"
  provides:
    - "fetch_drought_status — server-side Manitoba bbox geometry filter via api_get direct"
    - "fetch_ag_weather_stations — AgRegion WHERE filter + URL field per station"
    - "fetch_livestock_prices — cattle/hog dispatch with graceful hog degradation"
    - "fetch_crop_regions — bilingual REGION/RÉGION fields"
    - "manitoba_get_drought_status @tool"
    - "manitoba_get_ag_weather_stations @tool"
    - "manitoba_get_livestock_prices @tool"
    - "manitoba_get_crop_regions @tool"
  affects:
    - "src/mcp_canada/modules/manitoba/client.py (4 stubs filled)"
    - "src/mcp_canada/modules/manitoba/tools.py (4 @tool functions added)"
tech_stack:
  added: []
  patterns:
    - "Server-side geometry envelope filter via api_get direct call (drought FeatureServer /0/query with geometry + geometryType=esriGeometryEnvelope + spatialRel=esriSpatialRelIntersects + inSR/outSR=4326)"
    - "HOG_PRICES_FS_URL=None graceful degradation — empty success payload with 'note' field instead of error"
    - "CATTLE_PRICES_FS_URL dispatched by livestock='cattle'; hog early-return on None URL before cache/network"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
decisions:
  - "Drought bbox filter uses api_get direct (not arcgis_hub.query_feature_service) to pass geometry envelope params — query_feature_service signature does not expose geometry/geometryType/spatialRel params; direct /0/query call enables server-side spatial intersection without client-side filtering"
  - "filter_province=True is the default for drought — avoids returning continental North America data (Pitfall 8 from research); continental coverage query requires explicit filter_province=False"
  - "HOG_PRICES_FS_URL=None degrades to empty success (not error) — HOG_PRICES_FS_URL remains None per spike; tool returns {features:[], count:0, note:'...'} so agents can read the note rather than hitting UPSTREAM_ERROR"
  - "fetch_livestock_prices validates livestock in {'cattle','hog'} via ValueError before any network call; tool catches ValueError and returns INVALID_INPUT with valid=['cattle','hog']"
  - "Crop regions out_fields explicitly includes 'RÉGION' (French accented) — ArcGIS returns the field name exactly as defined in the layer schema"
metrics:
  duration: "5 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 18 Plan 04: Agriculture & Drought Tools Summary

4 agriculture/drought @tool functions + client bodies for MB-10…MB-13 — the prairie-distinguishing data domain replacing the dropped Manitoba Hydro/energy domain.

## What Was Built

### Client Bodies (4 functions filled in client.py)

**fetch_drought_status(filter_province, dm_level, include_geometry, lang)**
- When `filter_province=True` (default): uses `api_get` directly against `DROUGHT_MONITOR_FS_URL/0/query` with ArcGIS geometry envelope parameters (`geometry=-101.36,48.99,-95.15,60.0`, `geometryType=esriGeometryEnvelope`, `spatialRel=esriSpatialRelIntersects`, `inSR/outSR=4326`). This is server-side filtering — avoids fetching the full continental North America layer (Pitfall 8 from research).
- When `filter_province=False`: uses `arcgis_hub.query_feature_service` (standard pattern).
- Optional `dm_level` filter (D0-D4) via WHERE clause.
- Returns `{features, count, truncated}` with CACHE_TTL_STATIC (24h — matches weekly source update cadence).

**fetch_ag_weather_stations(ag_region, max_records, lang)**
- Optional `AgRegion` WHERE clause filter (e.g. `"Southwest"`, `"Central"`).
- Out fields: `StnName, LatDD, LongDD, Elevation, AgRegion, URL` — URL links to live hourly data per station at agrimaps.gov.mb.ca.
- CACHE_TTL_META (24h).

**fetch_livestock_prices(livestock, max_records, lang)**
- Validates `livestock` in `{"cattle", "hog"}` before any network call — raises `ValueError` on invalid input.
- `livestock="cattle"` → queries `CATTLE_PRICES_FS_URL` (confirmed live).
- `livestock="hog"` → `HOG_PRICES_FS_URL` is `None` (unresolved in Wave 0 spike) → early return with `{features:[], count:0, truncated:False, note:"..."}` — graceful degradation, not an error.
- Out fields: `week, Auction, Parameter, Measure, Value`.

**fetch_crop_regions(include_geometry, lang)**
- Out fields explicitly include `REGION` (English) and `RÉGION` (French with accented É) — bilingual boundary polygons for Manitoba Agriculture's 5 crop reporting regions.
- CACHE_TTL_STATIC (24h — static reference layer).

### @tool Functions (4 added to tools.py)

| Tool | Source | Key Behavior |
|------|--------|-------------|
| `manitoba_get_drought_status` | `Canada_USA_Drought_Monitor/FeatureServer` | `filter_province=True` default; Pitfall 8 documented in docstring |
| `manitoba_get_ag_weather_stations` | `WeatherStations/FeatureServer` | optional `ag_region` filter; URL field to live readings |
| `manitoba_get_livestock_prices` | `MB_Cattle_Prices_Current_year/FeatureServer` | INVALID_INPUT with valid=["cattle","hog"]; hog graceful empty |
| `manitoba_get_crop_regions` | `MbAg_Crop_Reporting_Regions/FeatureServer` | bilingual REGION/RÉGION passthrough |

All follow conventions: standalone `@tool`, `lang: Literal["en","fr"] = "en"`, `make_response()`/`make_error()`, 8+ Keywords in single-line docstring, `manitoba_` prefix.

### Tests

- **15 new client tests** across 4 classes: `TestManitobaGetDroughtStatus` (4), `TestManitobaGetAgWeatherStations` (4), `TestManitobaGetLivestockPrices` (4), `TestManitobaGetCropRegions` (3).
- **18 new tool tests** across 4 classes: drought (5), ag-weather (4), livestock (5), crop-regions (4).
- Total Manitoba test count: 59 → 92 (+33 tests).
- Coverage: 96.67% (well above 95% threshold).

## Hog Prices Resolution

The Wave 0 spike found `HOG_PRICES_FS_URL = None` (hog prices FeatureServer not found in mMUesHYPkXjaFGfS org after checking 82 services). Plan 04 implementation probed the cattle layer — the `MB_Cattle_Prices_Current_year` layer does NOT contain hog data (Parameter field values are cattle grades: "D1 Steers", "D2 Steers", etc.).

**Resolution chosen:** `livestock="hog"` returns `{features:[], count:0, note:"Hog prices FeatureServer URL is unresolved..."}` — an empty success response rather than an error. Agents can read the `note` field. The `valid=["cattle","hog"]` list is preserved in INVALID_INPUT errors so agents know "hog" is a recognized option even if data is temporarily unavailable.

## Drought Bbox Filter Approach

The `Canada_USA_Drought_Monitor` FeatureServer covers continental North America. Without filtering, a query returns all D0-D4 polygons for the US and Canada (~hundreds of features per observation date). The plan specified server-side geometry filter.

`arcgis_hub.query_feature_service` does not expose `geometry`/`geometryType`/`spatialRel` params (it uses a `where` SQL clause only). A bbox cannot be expressed as a SQL WHERE predicate on this polygon layer. Therefore the `filter_province=True` path calls `api_get` directly against the `/0/query` endpoint with ArcGIS REST geometry parameters.

The `filter_province=False` path uses `arcgis_hub.query_feature_service` for the standard pattern (useful for agents querying Canadian-wide drought comparison).

## Deviations from Plan

None — plan executed as written. The geometry-filter approach choice (direct api_get for province filter vs. arcgis_hub for unfiltered) was noted as open in the plan and resolved inline.

## Self-Check: PASSED

All 4 modified files verified. Both commits exist.
