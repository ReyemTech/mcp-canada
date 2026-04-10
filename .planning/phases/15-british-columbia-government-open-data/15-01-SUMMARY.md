---
phase: 15
plan: 01
subsystem: shared-ogc + british_columbia-module
tags: [wfs, ogc, bc, british-columbia, shared-client, tdd, wave-0]
dependency_graph:
  requires: []
  provides:
    - shared/ogc.py (WfsError, wfs_get_features, wfs_page_all, wfs_count)
    - modules/british_columbia/* (7-file skeleton)
    - Wave 0 test stubs (20 tool classes, 6 client classes, 2 prompts/resources classes)
    - TestBcToolScenarios (8 integration placeholders)
    - TestBcPromptsResources (3 integration placeholders)
  affects:
    - tests/integration/test_tool_scenarios.py (TestBcToolScenarios appended)
    - tests/integration/test_prompts_resources_scenarios.py (TestBcPromptsResources appended)
    - Plans 02/03/04 (reference specific pytest node IDs from Wave 0 stubs)
tech_stack:
  added:
    - shared/ogc.py: WFS 2.0 client (xml.etree.ElementTree stdlib for ExceptionReport parsing)
  patterns:
    - TDD RED→GREEN (test_ogc.py written before ogc.py)
    - httpx_client injection for testability (same as arcgis_hub.py)
    - typeNames (plural) serialization from type_name (singular) Python param — WFS 2.0 spec
    - _parse_wfs_exception: namespace-robust ET.iter() with tag.split("}")[-1] local name
    - Wave 0 xfail scaffolds for downstream plan dependency ordering
key_files:
  created:
    - src/mcp_canada/shared/ogc.py
    - src/mcp_canada/shared/__tests__/test_ogc.py
    - src/mcp_canada/modules/british_columbia/__init__.py
    - src/mcp_canada/modules/british_columbia/constants.py
    - src/mcp_canada/modules/british_columbia/schemas.py
    - src/mcp_canada/modules/british_columbia/client.py
    - src/mcp_canada/modules/british_columbia/tools.py
    - src/mcp_canada/modules/british_columbia/prompts.py
    - src/mcp_canada/modules/british_columbia/resources.py
    - src/mcp_canada/modules/british_columbia/__tests__/__init__.py
    - src/mcp_canada/modules/british_columbia/__tests__/conftest.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_client.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_tools.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py
    - .planning/phases/15-british-columbia-government-open-data/15-VALIDATION.md (updated)
  modified:
    - tests/integration/test_tool_scenarios.py (TestBcToolScenarios appended)
    - tests/integration/test_prompts_resources_scenarios.py (TestBcPromptsResources appended)
decisions:
  - "shared/ogc.py uses response.content (bytes) for _parse_geojson then json.loads(response.content) separately for numberReturned — avoids calling response.json() at all (consistent with error-path no-json rule)"
  - "typeNames (plural) is the WFS 2.0 spec requirement; Python kwarg is type_name (singular) for clean API — a line comment documents this above the params dict"
  - "_parse_wfs_exception uses tag.split('}')[-1] local-name extraction for namespace-robustness across ows/1.0 and ows/1.1"
  - "wfs_page_all returns truncated=True only when max_records cap was hit AND has_more=True — natural end of data returns False"
  - "CLIMATE_STATIONS_LAYER intentionally aliases WEATHER_STATIONS_LAYER — same BCGW layer, climate-oriented docstring for the 15th curated tool"
  - "client.py stub imports all use noqa: F401 comments — Plans 02/03 will use these imports in function bodies"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-04-10"
  tasks_completed: 3
  files_created: 15
  files_modified: 3
---

# Phase 15 Plan 01: BC Infrastructure + Wave 0 Stubs Summary

Implemented `shared/ogc.py` (reusable WFS 2.0 client) and scaffolded the complete `modules/british_columbia/` 7-file skeleton with all Wave 0 test stubs, enabling Plans 02/03/04 to reference deterministic pytest node IDs.

## What Was Built

### Task 1: shared/ogc.py WFS 2.0 Client (TDD)

New shared utility at `src/mcp_canada/shared/ogc.py` providing three public functions and one exception class:

- **`WfsError(code, message)`** — structured exception for HTTP 400 + ows:ExceptionReport XML responses
- **`wfs_get_features`** — single-page WFS GetFeature request. Always sends `typeNames` (plural per WFS 2.0 spec), `sortBy=OBJECTID`, `outputFormat=application/json`, `srsName=EPSG:4326`. Supports `CQL_FILTER`, `BBOX`, `propertyName`. Delegates to `_parse_geojson(response.content, include_geometry)` for GeoJSON parsing.
- **`wfs_page_all`** — auto-paginating wrapper with `max_records` cap (default 5000). Returns `(features, truncated)` where `truncated=True` only when the cap was hit with more data available.
- **`wfs_count`** — uses `resultType=hits` to read `totalFeatures` without fetching features.

Error handling: HTTP 400 with XML content-type → `_parse_wfs_exception()` via stdlib `xml.etree.ElementTree` using namespace-robust `tag.split("}")[-1]` local name extraction. `response.json()` is never called on the error path.

15 unit tests written RED-first, all GREEN. Zero new dependencies.

### Task 2: british_columbia Module Skeleton

7-file module at `src/mcp_canada/modules/british_columbia/`:

- `__init__.py`: `MODULE_NAME = "british_columbia"` for FileSystemProvider auto-registration
- `constants.py`: 15 verified WHSE_* layer constants, RATE_LIMIT_CKAN=10.0, RATE_LIMIT_WFS=5.0, CACHE_TTL_ACTIVE=300, CACHE_TTL_STATIC=86400
- `schemas.py`: `BcResource`, `BcDatasetSummary`, `BcDatasetDetails` (with `object_name` + `queryable_via_wfs: bool`), `BcFeature` — all flat Pydantic v2 with `extra="ignore"`
- `client.py`: stub functions raising `NotImplementedError` with Plan 02/03 comments; correct imports for downstream plans
- `tools.py`, `prompts.py`, `resources.py`: empty scaffolds with correct standalone imports

### Task 3: Wave 0 Test Stubs

Complete test scaffold in `src/mcp_canada/modules/british_columbia/__tests__/`:

- **conftest.py**: 12 fixtures (CKAN search/show/org/tag, WFS active fires/perimeters/parks/mining/wells/exception XML/two-page) + autouse cache/limiter patches
- **test_client.py**: 6 class scaffolds (TestFetchSearchDatasets, TestFetchDatasetDetails, TestFetchOrganizations, TestFetchTags, TestWfsFetchShared, TestQueryableViaWfsDetection)
- **test_tools.py**: 20 class scaffolds — 5 CKAN discovery + 15 curated WFS; `TestBcGetWaterWells` includes `test_requires_at_least_one_filter` placeholder for the 130K-record guard
- **test_prompts_resources.py**: `TestBcPrompts` + `TestBcResources`

Integration stubs appended:
- `TestBcToolScenarios` (8 xfail methods) in `tests/integration/test_tool_scenarios.py`
- `TestBcPromptsResources` (3 xfail methods) in `tests/integration/test_prompts_resources_scenarios.py`

`15-VALIDATION.md` updated with per-task map (29 rows), `wave_0_complete: true`, `nyquist_compliant: true`.

## Decisions Made

- `shared/ogc.py` uses `response.content` (bytes) for `_parse_geojson` + `json.loads(response.content)` separately for `numberReturned`. This satisfies both the no-json-on-400-path rule and the reuse of `_parse_geojson(bytes)` signature.
- `typeNames` (plural) serialization from `type_name` (singular) Python kwarg — documented with inline comment above params dict.
- `_parse_wfs_exception` uses `tag.split('}')[-1]` namespace stripping — robust to `ows/1.0` vs `ows/1.1` variations.
- `CLIMATE_STATIONS_LAYER` intentionally aliases `WEATHER_STATIONS_LAYER` — same BCGW layer, two tool docstrings (climate vs wildfire weather).
- Client stub `noqa: F401` pattern allows Plans 02/03 to import from client.py without file edits to the import block.

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

Verified below.
