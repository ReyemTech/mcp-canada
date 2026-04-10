---
phase: 14-york-region-municipal-government-open-data
plan: 01
subsystem: york_region
tags: [arcgis-hub, feature-service, municipal-data, york-region, shared-infrastructure]
dependency_graph:
  requires: [shared/parsers.py, shared/cache.py, shared/rate_limiter.py]
  provides: [shared/arcgis_hub.py, modules/york_region/client.py]
  affects: [future ArcGIS Hub modules (BC, other cities)]
tech_stack:
  added: []
  patterns: [ArcGIS Hub Search API, ArcGIS FeatureServer pagination, NoPortalError pattern]
key_files:
  created:
    - src/mcp_canada/shared/arcgis_hub.py
    - src/mcp_canada/shared/__tests__/test_arcgis_hub.py
    - src/mcp_canada/modules/york_region/__init__.py
    - src/mcp_canada/modules/york_region/constants.py
    - src/mcp_canada/modules/york_region/schemas.py
    - src/mcp_canada/modules/york_region/client.py
    - src/mcp_canada/modules/york_region/__tests__/__init__.py
    - src/mcp_canada/modules/york_region/__tests__/conftest.py
    - src/mcp_canada/modules/york_region/__tests__/test_client.py
  modified: []
decisions:
  - "Hub Search API uses /api/search/v1/collections/all/items (NOT /api/v2/datasets which 404s)"
  - "NoPortalError (not ValueError) for municipalities without public ArcGIS Hub portals — enables typed catch in tools"
  - "_fetch_features private helper centralizes rate limiting + caching for all curated FeatureServer functions"
  - "shape_hub_dataset in shared/arcgis_hub.py (not client.py) — reusable by future ArcGIS modules"
  - "PORTAL_URLS has 10 keys: 4 real URLs + 5 None + 1 census-only Whitchurch-Stouffville hub"
  - "query_feature_service passes returnGeometry=false when include_geometry=False — reduces payload size"
metrics:
  duration: 8min
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_created: 9
  tests_added: 64
---

# Phase 14 Plan 01: York Region Module Skeleton Summary

**One-liner:** ArcGIS Hub + FeatureServer reusable client in `shared/arcgis_hub.py` plus york_region module skeleton with 10-portal discovery and 12 curated feature fetchers backed by 64 unit tests.

## What Was Built

### Task 1: shared/arcgis_hub.py (TDD)

The first reusable ArcGIS Hub client in the project. Future modules (BC, other cities) will import directly:

- `search_hub_datasets(portal_base_url, query, limit, offset)` — calls `/api/search/v1/collections/all/items`, raises ValueError on None portal
- `query_feature_service(service_url, layer_id, ...)` — auto-paginates via `exceededTransferLimit`, caps at 5000 records, returns `(features, truncated)` tuple
- `get_layer_metadata(service_url, layer_id)` — reads `maxRecordCount`, fields, geometry_type for dynamic page-size tuning
- `get_count(service_url, layer_id, where)` — fast count query with `returnCountOnly=true`
- `shape_hub_dataset(feature)` — flattens Hub Search `features[i]` to flat dict, truncates descriptions at 500 chars

All functions accept an optional `httpx_client` parameter for dependency injection in tests. No caching or rate limiting at this layer — those belong in module-level client.py wrappers.

### Task 2: york_region module skeleton (TDD)

7-file module structure (minus tools/prompts/resources which come in Plan 02):

- `__init__.py`: MODULE_NAME="york_region", MODULE_DESCRIPTION covering 4 verified portals
- `constants.py`: 10 portal URLs (4 real + 5 None + 1 census-only), all YR/Markham FeatureServer URLs with layer IDs
- `schemas.py`: flat Pydantic v2 HubDataset + FeatureQueryResult models
- `client.py`: 5 discovery functions + 10 curated York Region + 2 curated Markham (all returning `(data, was_cached)`)

Key client patterns:
- `NoPortalError` (custom exception) raised by `_require_portal()` for municipalities without portals
- `_escape_where_value()` doubles single quotes to prevent SQL injection in ArcGIS WHERE clauses
- `_fetch_features()` private helper centralizes cached_fetch + get_limiter("arcgis_hub", 5.0) for all curated tools
- All cache keys prefixed `york_region:` per-module convention

## Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| test_arcgis_hub.py | 19 | search, query, metadata, count, shape functions |
| test_client.py | 45 | discovery, curated helpers, portal validation, SQL escaping |
| **Total** | **64** | |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

### Files Created

- [x] `src/mcp_canada/shared/arcgis_hub.py` — created
- [x] `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` — created
- [x] `src/mcp_canada/modules/york_region/__init__.py` — created
- [x] `src/mcp_canada/modules/york_region/constants.py` — created
- [x] `src/mcp_canada/modules/york_region/schemas.py` — created
- [x] `src/mcp_canada/modules/york_region/client.py` — created
- [x] `src/mcp_canada/modules/york_region/__tests__/__init__.py` — created
- [x] `src/mcp_canada/modules/york_region/__tests__/conftest.py` — created
- [x] `src/mcp_canada/modules/york_region/__tests__/test_client.py` — created

### Commits

- [x] d10f16f — feat(14-01): add shared/arcgis_hub.py ArcGIS Hub + FeatureServer client
- [x] db88ef2 — feat(14-01): add york_region module skeleton with client and unit tests

## Self-Check: PASSED
