---
phase: 13-toronto-municipal-government-open-data
plan: "01"
subsystem: toronto-client
tags: [toronto, ckan, gtfs, geojson, parsers, client, tdd]
dependency_graph:
  requires:
    - src/mcp_canada/shared/cache.py
    - src/mcp_canada/shared/parsers.py
    - src/mcp_canada/shared/rate_limiter.py
  provides:
    - src/mcp_canada/shared/parsers._parse_geojson
    - src/mcp_canada/shared/parsers._parse_json
    - src/mcp_canada/modules/toronto (full module)
  affects:
    - Plan 13-02 (tools layer — consumes all client functions)
tech_stack:
  added: []
  patterns:
    - GeoJSON FeatureCollection parsing from bytes via stdlib json
    - GTFS ZIP parsing via stdlib zipfile + BytesIO (no new dependencies)
    - CKAN datastore_search with client-side filtering
    - 311 ZIP+CSV two-step fetch: package_show to discover URL, then download+parse
key_files:
  created:
    - src/mcp_canada/shared/parsers.py (extended with _parse_geojson, _parse_json)
    - src/mcp_canada/modules/toronto/__init__.py
    - src/mcp_canada/modules/toronto/constants.py
    - src/mcp_canada/modules/toronto/schemas.py
    - src/mcp_canada/modules/toronto/client.py
    - src/mcp_canada/modules/toronto/__tests__/__init__.py
    - src/mcp_canada/modules/toronto/__tests__/conftest.py
    - src/mcp_canada/modules/toronto/__tests__/test_client.py
  modified:
    - src/mcp_canada/shared/__tests__/test_parsers.py (10 new tests)
decisions:
  - "GeoJSON .geojson check before .json in fetch_and_parse: .geojson ends in json so ordering matters"
  - "fetch_311_requests two-step: package_show discovers year ZIP URL, then downloads — enables year-agnostic implementation"
  - "min_score filter in fetch_rentsafe_evaluations is client-side: CKAN filters require exact match, not >=; _safe_int helper prevents crashes on non-numeric scores"
  - "GTFS ZIP timeout=120s: 35.9 MB file requires long timeout; CKAN API uses default 30s"
  - "cache key prefix toronto: distinguishes Toronto datasets from federal CKAN keys in shared aiocache"
metrics:
  duration: 5min
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_modified: 8
---

# Phase 13 Plan 01: Toronto Module Skeleton and Shared Parsers Summary

**One-liner:** GeoJSON/JSON parsers added to shared layer + full Toronto CKAN client with GTFS ZIP, datastore, 311 ZIP+CSV, RentSafeTO, and STR functions.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add GeoJSON and JSON parsers to shared/parsers.py | 0f0d751 | parsers.py, test_parsers.py |
| 2 | Create Toronto module skeleton with full client layer | 3222438 | 7 new module files |

## What Was Built

### Task 1: Shared GeoJSON/JSON Parsers

Extended `src/mcp_canada/shared/parsers.py` with:

- `_parse_geojson(content: bytes, include_geometry: bool = False)`: Parses GeoJSON FeatureCollection, returns list of property dicts. Optionally includes geometry key.
- `_parse_json(content: bytes)`: Routes to `_parse_geojson` if root dict has `features`, returns list directly for arrays, wraps plain objects in list.
- Updated `fetch_and_parse` routing: `.geojson` checked before `.json` (critical: `.geojson` ends with `json`).
- 10 new unit tests across `TestGeoJSON`, `TestParseJSON`, `TestFetchAndParseGeoJsonRouting`.

### Task 2: Toronto Module (5 core files + test suite)

**`__init__.py`:** `MODULE_NAME = "toronto"` with description covering TTC GTFS, neighbourhood profiles, 311 requests, RentSafeTO, STR.

**`constants.py`:** `BASE_URL`, `RATE_GROUP = "toronto"`, `RATE_LIMIT = 5.0`, TTLs (search=1hr, meta=24hr, data=24hr, gtfs=6hr), curated resource IDs for GTFS, neighbourhood profiles, 311, RentSafeTO, and STR.

**`schemas.py`:** `GTFSStop` and `GTFSRoute` Pydantic v2 models for type safety.

**`client.py`:** 14 async client functions:
- CKAN discovery: `fetch_search_datasets`, `fetch_dataset_details`, `fetch_resource`, `fetch_organizations`, `fetch_dataset_count`
- GTFS: `fetch_gtfs_file` (ZIP download + extract via stdlib zipfile), `fetch_gtfs_stops` (name filter), `fetch_gtfs_routes` (type filter)
- Datastore: `fetch_datastore_records` (generic datastore_search helper)
- Neighbourhood: `fetch_neighbourhood_profile`, `fetch_neighbourhood_comparison`
- 311: `fetch_311_requests` (two-step: package_show → ZIP download → CSV parse, client-side filters)
- Housing: `fetch_rentsafe_evaluations` (min_score client-side), `fetch_short_term_rentals` (status client-side)

**`__tests__/`:** `conftest.py` with in-memory ZIP fixtures, CKAN response fixtures, 311 CSV fixtures; `test_client.py` with 23 tests covering all functions.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

All files exist and all commits verified:
- FOUND: src/mcp_canada/shared/parsers.py
- FOUND: src/mcp_canada/modules/toronto/__init__.py
- FOUND: src/mcp_canada/modules/toronto/constants.py
- FOUND: src/mcp_canada/modules/toronto/schemas.py
- FOUND: src/mcp_canada/modules/toronto/client.py
- FOUND: src/mcp_canada/modules/toronto/__tests__/test_client.py
- FOUND: commit 0f0d751 (feat: GeoJSON/JSON parsers)
- FOUND: commit 3222438 (feat: Toronto module)
