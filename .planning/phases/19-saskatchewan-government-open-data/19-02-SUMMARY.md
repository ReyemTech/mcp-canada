---
phase: 19-saskatchewan-government-open-data
plan: 02
subsystem: saskatchewan/discovery
tags: [arcgis-hub, saskatchewan, discovery, ogc-params, hub-search, startindex-fix]
dependency_graph:
  requires: [19-01 (scaffold + shared/arcgis_hub.py startindex fix)]
  provides: [5 discovery tools SK-01..SK-05, TestSharedApiGetContract, OGC-param contract enforced]
  affects: [Plans 19-03 through 19-05 (curated tools build on these discovery functions)]
tech_stack:
  added: []
  patterns: [ArcGIS Hub OGC API Records limit/startindex, _hub_get Hub-JSON contract, auto-router FeatureServer/file/metadata-only]
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/saskatchewan/client.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_client.py
    - src/mcp_canada/modules/saskatchewan/tools.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py
decisions:
  - "OGC params: limit (not num), startindex (not start/offset) — omit startindex when 0, omit q when blank; param-regression asserts call_args[0][1] directly"
  - "auto-router prefers FeatureServer over MapServer; strips trailing /N layer suffix; CSV/JSON/GeoJSON/XLSX → fetch_and_parse; else metadata-only note"
  - "api_name='saskatchewan-geohub' for all 5 discovery tools _meta envelopes"
  - "NOT_FOUND on ValueError from fetch_dataset_details; UPSTREAM_ERROR on HTTPStatusError"
  - "_flatten_hub_feature reads feature.id and feature.properties — same shape as Manitoba"
metrics:
  duration: "6 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_modified: 4
---

# Phase 19 Plan 02: Saskatchewan Discovery Tools Summary

Implemented the 5 ArcGIS Hub discovery tools (SK-01…SK-05) for Saskatchewan's geohub.saskatchewan.ca. Filled the client stubs with OGC-correct param construction (the Manitoba lesson), filled TestSharedApiGetContract enforcing the Hub-JSON contract, and added 16 tool tests covering envelope/error/lang paths.

## One-Liner

5 Saskatchewan GeoHub discovery tools (search/details/query/orgs/categories) with Hub-JSON contract enforced, OGC API Records params pinned by param-regression tests, and auto-router for FeatureServer/file/metadata-only routing.

## Tasks Completed

| Task | Commit | Description |
|------|--------|-------------|
| 1. Client bodies + TestSharedApiGetContract + param-regression tests | 4636209 | 5 discovery client functions with OGC params; 31 client tests GREEN |
| 2. 5 discovery @tool functions + tool tests | eba3455 | Tools with standalone @tool, lang, make_response/make_error, docstrings; 16 tool tests GREEN |

## Task 1: Discovery Client Bodies

### OGC API Records param construction (the Manitoba lesson)

```python
params: dict[str, Any] = {"limit": min(max(limit, 1), 100)}
if query:
    params["q"] = query                   # omit q when blank (empty q -> 400)
if offset and offset > 0:
    params["startindex"] = offset         # 1-based; omit when 0 (startindex=0 invalid)
if category:
    params["categories"] = category
```

Param-regression tests assert `mock_api_get.call_args[0][1]` directly:
- `fetch_search_datasets("crops", limit=10, offset=0)` → params exactly `{"limit": 10, "q": "crops"}`
- No `num`, `start`, `offset` keys ever present
- `offset=10` → `params["startindex"] == 10`
- blank query → `"q" not in params`
- `fetch_organizations()` and `fetch_categories()` → `"q" not in params`, `"limit" in params`

### Hub-JSON contract (TestSharedApiGetContract)

5 tests patching `mcp_canada.modules.saskatchewan.client.api_get` (module-local, BC/Alberta pattern):
- `test_hub_get_calls_api_get_once` — api_get called once, first arg is HUB_SEARCH_URL
- `test_hub_get_returns_dict_directly` — returns Hub dict without inspecting "success"
- `test_hub_get_raises_on_non_dict_response` — list/str response → HTTPStatusError
- `test_hub_get_raises_on_none_response` — None → HTTPStatusError
- `test_hub_get_never_calls_get_success` — dict without "success" key must not raise

### Auto-router (fetch_query_dataset)

| Input URL | Route |
|-----------|-------|
| Contains `/FeatureServer` | `arcgis_hub.query_feature_service`; strips trailing `/N` layer suffix |
| Ends in `.csv`, `.json`, `.geojson`, `.xlsx`, `.xls` | `fetch_and_parse(url)` |
| Other (PDF, ZIP, KML, WMS) | metadata-only `{"url": ..., "note": "..."}` |

### Other client functions

- `fetch_dataset_details`: GETs `/collections/all/items/{id}`; handles single-item and search-shaped responses; detects FeatureServer URL via `"/FeatureServer" in url`; collects parseable download links from `links` array
- `fetch_organizations`: `_hub_get({"limit": min(num, 100)})` → derives unique owners
- `fetch_categories`: `_hub_get({"limit": 100})` → derives unique `/Categories/*` strings

## Task 2: Discovery Tool Functions

### 5 tools (all standalone @tool, lang Literal en/fr, make_response/make_error)

| Tool | Client fn | api_name | Error mapping |
|------|-----------|----------|---------------|
| `saskatchewan_search_datasets` | `fetch_search_datasets` | `saskatchewan-geohub` | HTTPStatusError → UPSTREAM_ERROR |
| `saskatchewan_get_dataset_details` | `fetch_dataset_details` | `saskatchewan-geohub` | ValueError → NOT_FOUND; HTTPStatusError → UPSTREAM_ERROR |
| `saskatchewan_query_dataset` | `fetch_query_dataset` | `saskatchewan-geohub` | HTTPStatusError → UPSTREAM_ERROR |
| `saskatchewan_list_organizations` | `fetch_organizations` | `saskatchewan-geohub` | HTTPStatusError → UPSTREAM_ERROR |
| `saskatchewan_list_categories` | `fetch_categories` | `saskatchewan-geohub` | HTTPStatusError → UPSTREAM_ERROR |

### Docstring note in saskatchewan_search_datasets

> NOTE: This is the Government of Saskatchewan provincial ArcGIS Hub (org zcv98lgAl8xQ04cW); WSA water data and SPSA fire-ban data live on separate services and are reached via the curated tools, NOT Hub Search.

### Tool test coverage (16 tests)

Each of the 5 discovery tools covered by 3 tests:
1. `_meta` envelope present + `api == "saskatchewan-geohub"`
2. Error path (HTTPStatusError/ValueError → make_error with correct code)
3. `lang="fr"` passes through to `_meta.lang`

## Deviations from Plan

### Auto-fix: make_response wraps payload under "data" key

**Found during:** Task 2 tool test writing
**Issue:** Test assertions used `data["results"]` but `make_response` wraps the payload dict under a `"data"` key, so the correct path is `data["data"]["results"]`
**Fix:** Updated test assertions to use `data["data"]["results"]` and `data["data"]["organizations"]` / `data["data"]["categories"]`
**Files modified:** `test_tools.py`
**Rule:** Rule 1 (Bug — incorrect test assertion for envelope structure)

## Success Criteria Check

- [x] 5 discovery tools (SK-01…SK-05) implemented and callable
- [x] TestSharedApiGetContract green (5 tests, parsed-dict contract enforced)
- [x] Outgoing Hub params use limit/startindex, omit blank q — pinned by param-regression tests
- [x] Auto-router handles FeatureServer / file / metadata-only
- [x] All discovery tools follow conventions (standalone @tool, lang, envelope, prefix, docstrings)
- [x] 47 Saskatchewan module tests pass
- [x] Coverage 96.73% (≥95% requirement)

## Self-Check: PASSED

Files modified confirmed present:
- `src/mcp_canada/modules/saskatchewan/client.py` — 5 discovery function bodies + helpers
- `src/mcp_canada/modules/saskatchewan/__tests__/test_client.py` — 31 tests GREEN
- `src/mcp_canada/modules/saskatchewan/tools.py` — 5 @tool functions
- `src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py` — 16 tests GREEN

Commits verified: `4636209` (Task 1), `eba3455` (Task 2) — both in git log.
Full suite: 2559 passed, coverage 96.73%.
