---
phase: 20-nova-scotia-government-open-data
plan: "04"
subsystem: nova-scotia-environment-water-air
tags:
  - nova-scotia
  - socrata
  - environment
  - water-quality
  - boil-water
  - protected-areas
  - air-quality
  - wave-3
dependency_graph:
  requires:
    - 20-01 (shared/socrata.py + module scaffold + ACTIVE_ADVISORY_FILTER spike)
    - 20-02 (discovery tools + client helpers)
    - 20-03 (aquaculture curated tools)
  provides:
    - ns_get_water_quality_monitoring (NS-11)
    - ns_get_boil_water_advisories (NS-12)
    - ns_get_protected_areas (NS-15)
    - ns_get_air_quality_stations (NS-16)
  affects:
    - Plan 20-07 (integration tests for these 4 tools)
    - Plan 20-06 (air-quality-guide resource references ns_get_air_quality_stations)
tech_stack:
  added: []
  patterns:
    - ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL" (pinned from Wave 0 spike; empty-is-valid off-season pattern)
    - explicit $select geometry exclusion (protected areas ticv-5du5 MultiPolygon)
    - belt-and-suspenders the_geom strip at both client and tool layers
    - "since" date-filter pattern: date > '<iso>' in SoQL WHERE
    - station-catalog-only air quality (20+ per-station datasets → ns_query_dataset)
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/tools.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
decisions:
  - "ACTIVE_ADVISORY_FILTER = 'date_advisory_removed IS NULL' used for boil-water active_only; empty-string comparison causes type-mismatch error (spike-confirmed)"
  - "Protected areas (ticv-5du5) excludes the_geom via explicit $select; belt-and-suspenders strip at both client and tool layers"
  - "Empty boil-water advisory list is a valid success (count=0, _meta envelope) — not an error; mirrors Manitoba flood-alert lesson"
  - "Air quality tool is stations catalog only; 20+ per-station pollutant datasets directed to ns_query_dataset; air-quality-guide resource (Plan 06) documents the pattern"
  - "Water quality uses CACHE_TTL_SEARCH (1h) because dataset is historical through 2024-12 (not live sensor feed)"
metrics:
  duration: "6 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 20 Plan 04: Nova Scotia Environment / Water / Air Quality Tools Summary

4 curated environment, water, and air quality tools implementing NS-11, NS-12, NS-15, NS-16 over the shared Socrata SODA client.

## What Was Built

### Tools Implemented

| Tool | Dataset | NS Req | Key Behavior |
|------|---------|--------|-------------|
| `ns_get_water_quality_monitoring` | bkfi-mjgw | NS-11 | station_number + since filters; date DESC order; data through 2024-12 |
| `ns_get_boil_water_advisories` | 7t68-9xmm | NS-12 | active_only=ACTIVE_ADVISORY_FILTER; empty list is valid success |
| `ns_get_protected_areas` | ticv-5du5 | NS-15 | explicit $select excludes the_geom; belt-and-suspenders strip; status filter |
| `ns_get_air_quality_stations` | 3bbm-drnh | NS-16 | station catalog only; city filter; docstring directs to ns_query_dataset for pollutant series |

### Task 1: 4 Client Function Bodies (RED→GREEN)

**`fetch_water_quality_monitoring`** (bkfi-mjgw):
- station_number filter: `station_number='X'`
- since filter: `date > '<iso>'`
- Combined: joined with AND
- $select: `station_number,date,time,temperature_c,ph,specific_conductance_s_cm,dissolved_oxygen_mg_l`
- $order: `date DESC`
- Cache: CACHE_TTL_SEARCH (1h — historical dataset, not live)

**`fetch_boil_water_advisories`** (7t68-9xmm):
- `ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL"` applied when `active_only=True`
- county filter: `county='X'`; joined with AND when combined
- Empty rows list → `{"advisories": [], "count": 0, "truncated": False}` — valid success
- $order: `date_advisory_issued DESC`
- Cache: CACHE_TTL_LIVE (15min — safety-critical data)

**`fetch_protected_areas`** (ticv-5du5):
- $select: `objectid,pro_name,protect1,symbol,owner,authority,status,web_url,ha_gis` (NO the_geom)
- Belt-and-suspenders row strip: `{k: v for k, v in row.items() if k != "the_geom"}`
- status filter: `status='X'`
- $order: `pro_name ASC`
- Cache: CACHE_TTL_ANNUAL (7d — stable reference data)

**`fetch_air_quality_stations`** (3bbm-drnh):
- $select: `national_air_pollution_surveillance_network_id,station_name,province,city,country,latitude,longitude,measurements,monitoring_period`
- city filter: `city='X'`
- Cache: CACHE_TTL_META (24h — stable station locations)

**33 new client tests** (test_client.py):
- `test_active_only_uses_active_advisory_filter` — asserts ACTIVE_ADVISORY_FILTER in $where
- `test_empty_result_is_valid_success_not_error` — count=0, no exception raised
- `test_select_does_not_contain_the_geom` — $select sent to API has no the_geom
- `test_returned_rows_have_no_the_geom` — even when mock returns rows with the_geom, result strips it
- `test_since_filter_builds_date_gt_clause` — date > '<iso>' SoQL construction
- `test_select_does_not_use_empty_string_filter` — asserts IS NULL not = '' in ACTIVE_ADVISORY_FILTER

### Task 2: 4 Curated @tool Functions (RED→GREEN)

All 4 tools follow conventions:
- Standalone `@tool` from `fastmcp.tools`
- `lang: Literal["en", "fr"] = "en"` parameter
- `make_response()` on success, `make_error("UPSTREAM_ERROR", ...)` on exception
- `ns_` prefix
- Single-line `Use for:` + 8+ `Keywords:` in docstring

Key docstring content:
- **Water quality**: notes data is through 2024-12 (not live); documents `since=` date format; directs to i9ee-9hct for station locations
- **Boil water**: documents `active_only=True` behavior; explicitly notes empty list = valid success; county name uppercase convention
- **Protected areas**: notes geometry excluded; directs to `ns_query_dataset` with `dataset_id='ticv-5du5'` for polygon boundaries; documents status values
- **Air quality**: explicitly states STATION CATALOG ONLY; directs to `ns_query_dataset` with per-station dataset IDs for pollutant readings; references `docs://ns/air-quality-guide`

**22 new tool tests** (test_tools.py):
- `test_empty_advisories_is_valid_success_not_error` — asserts `_meta` in result, `error` NOT in result
- `test_protected_areas_rows_have_no_the_geom` — even when mock provides rows with the_geom, tool strips it
- `test_api_url_contains_dataset_id` — all 4 tools assert correct dataset ID in `_meta.source.url`
- Error path + lang passthrough for all 4 tools

## ACTIVE_ADVISORY_FILTER Value

`"date_advisory_removed IS NULL"` — spike-confirmed (2026-06-15):
- Returns 82 active advisories
- Empty-string alternative (`= ''`) causes `query.soql.type-mismatch` on the date column

## Protected Areas Geometry Exclusion

Two-layer defense:
1. `$select` passed to `socrata.query_dataset` does NOT include `the_geom` (primary defense)
2. Belt-and-suspenders row strip at both client and tool layers: `{k: v for k, v in row.items() if k != "the_geom"}`

Tests assert: (a) $select sent to API has no `the_geom`; (b) even when mock returns rows WITH `the_geom`, the result has no `the_geom`.

## Empty Boil-Water Advisory — Valid Success

When `fetch_boil_water_advisories(active_only=True)` returns `[]`:
- Client returns: `{"advisories": [], "count": 0, "truncated": False}`
- Tool returns: `make_response(data, ...)` — `_meta` key present, `error` key absent
- Matches Manitoba flood-alert and Saskatchewan fire-ban patterns

## Air Quality Discovery-Only Note

`ns_get_air_quality_stations` returns only the station catalog (3bbm-drnh). The ~20 per-station pollutant datasets (e.g., `gqhb-4cnd` O3 at Lake Major, `36wx-n4y2` PM2.5 at Halifax) require `ns_query_dataset` with the specific dataset ID. The docstring explicitly states this and references `docs://ns/air-quality-guide` (Plan 06).

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- `src/mcp_canada/modules/nova_scotia/client.py` exists — fetch_water_quality_monitoring, fetch_boil_water_advisories, fetch_protected_areas, fetch_air_quality_stations all implemented
- `src/mcp_canada/modules/nova_scotia/tools.py` exists — ns_get_water_quality_monitoring, ns_get_boil_water_advisories, ns_get_protected_areas, ns_get_air_quality_stations all defined
- `ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL"` in constants.py
- 152 nova_scotia tests pass (90 client + 62 tool)
- Coverage: 96.96% (≥95% required)
- Pyright: 0 errors in client.py and tools.py

## Self-Check: PASSED
