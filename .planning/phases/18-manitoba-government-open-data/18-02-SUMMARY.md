---
phase: 18-manitoba-government-open-data
plan: "02"
subsystem: manitoba-discovery-tools
tags: [discovery, arcgis-hub, hub-search, auto-router, wave-1, tdd]
dependency_graph:
  requires:
    - "18-01: Manitoba scaffold (stubs + _hub_get + conftest fixtures)"
  provides:
    - "src/mcp_canada/modules/manitoba/client.py — 5 discovery client bodies"
    - "src/mcp_canada/modules/manitoba/tools.py — 5 discovery @tool functions"
    - "src/mcp_canada/modules/manitoba/__tests__/test_client.py — TestSharedApiGetContract + 5 client test classes (19 tests)"
    - "src/mcp_canada/modules/manitoba/__tests__/test_tools.py — 5 tool test classes (20 tests)"
  affects:
    - "Plans 03-06: client stubs remain NotImplementedError but signatures validated"
tech_stack:
  added: []
  patterns:
    - "_hub_get(params) — Hub JSON, NOT CKAN envelope; api_get returns parsed dict directly"
    - "fetch_query_dataset auto-router: /FeatureServer→arcgis_hub.query_feature_service; .csv/.json/.geojson/.xlsx→fetch_and_parse; else metadata-only"
    - "TestSharedApiGetContract: patches client.api_get at module-local layer (Phase 15/17 pattern)"
    - "fetch_dataset_details: Hub item endpoint /api/search/v1/collections/all/items/{id}"
    - "fetch_organizations/fetch_categories: derive unique owners/categories from Hub search results"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
decisions:
  - "fetch_query_dataset takes feature_server_url as positional arg (not package_id) — Manitoba has no CKAN; agents pass FeatureServer URL directly from get_dataset_details"
  - "fetch_organizations/categories derive from Hub search results (not separate Hub orgs endpoint) — Manitoba Hub doesn't expose a dedicated groups list"
  - "_hub_get Hub-JSON contract: never inspects .get('success') or .get('result'); Hub Search returns {features, numberMatched, ...} directly"
  - "fetch_dataset_details tries /api/search/v1/collections/all/items/{id} first (single-item shape), falls back to search shape if needed — flexible to Hub API behavior"
  - "Auto-router: _is_feature_server_url checks '/FeatureServer' in URL; _is_parseable_url checks lowercase extension (.csv/.json/.geojson/.xlsx/.xls)"
  - "max_records clamped to 5000 in tool layer (not client); tools layer is the enforcement point"
metrics:
  duration: "6 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_modified: 4
---

# Phase 18 Plan 02: Manitoba Discovery Tools Summary

5 ArcGIS Hub discovery tools (MB-01…MB-05) implemented via TDD — the entry point for agents to search Manitoba's provincial geoportal, inspect datasets, query any FeatureServer or file resource, and list organizations/categories.

## What Was Built

### 5 Discovery Client Bodies (client.py)

| Function | Backend | Cache TTL | Notes |
|----------|---------|-----------|-------|
| `fetch_search_datasets(query, category, num, start)` | `_hub_get` with q/num/start/categories params | 1h | Returns `{"results": [flat summaries], "total": N}` |
| `fetch_dataset_details(item_id)` | Hub item endpoint `HUB_SEARCH_URL/{id}` | 24h | Returns `{"details": {feature_server_url, download_urls, ...}}` |
| `fetch_query_dataset(feature_server_url, ...)` | Auto-router (see table below) | 24h | Returns `{"data": rows, "url": ..., "rows": N, "truncated": bool}` |
| `fetch_organizations()` | `_hub_get` with `q=""` | 24h | Derives unique `owner` strings from Hub features |
| `fetch_categories()` | `_hub_get` with `q=""` | 24h | Derives unique `categories` path strings from Hub features |

### Auto-Router Routing Table (fetch_query_dataset)

| URL Pattern | Route | Returns |
|-------------|-------|---------|
| Contains `/FeatureServer` | `arcgis_hub.query_feature_service` | `{"data": rows, "rows": N, "truncated": bool}` |
| Ends with `.csv`, `.json`, `.geojson`, `.xlsx`, `.xls` | `fetch_and_parse` | `{"data": rows[:max_records], "rows": N, "truncated": bool}` |
| Any other (PDF, ZIP, KML, WMS) | Metadata-only | `{"url": url, "note": "binary/archive resource..."}` |

### 5 Discovery @tool Functions (tools.py)

| Tool | Client Delegate | Error Codes |
|------|----------------|-------------|
| `manitoba_search_datasets(query, category, num, start, lang)` | `fetch_search_datasets` | `UPSTREAM_ERROR` |
| `manitoba_get_dataset_details(dataset_id, lang)` | `fetch_dataset_details` | `INVALID_INPUT`, `NOT_FOUND`, `UPSTREAM_ERROR` |
| `manitoba_query_dataset(dataset_url, where, max_records, include_geometry, lang)` | `fetch_query_dataset` | `INVALID_INPUT`, `UPSTREAM_ERROR` |
| `manitoba_list_organizations(lang)` | `fetch_organizations` | `UPSTREAM_ERROR` |
| `manitoba_list_categories(lang)` | `fetch_categories` | `UPSTREAM_ERROR` |

All tools: standalone `@tool`, `lang: Literal["en", "fr"] = "en"`, `make_response`/`make_error`, `_meta.source.api = "manitoba-geoportal-hub"`, `manitoba_` prefix, single-line `Use for:` + `Keywords:` (8+ terms).

### Hub Search API Parameters Discovered

The Manitoba geoportal uses standard ArcGIS Hub Search API v1:
- Pagination: `num` (not `limit`; `limit` is the v2 param) + `start` (not `offset`)
- Category filter: `categories` (string path like `/Categories/Environment`)
- Base URL: `https://geoportal.gov.mb.ca/api/search/v1/collections/all/items`
- Item detail: append `/{item_id}` to the search URL

### TestSharedApiGetContract (19 tests)

Enforces the parsed-dict contract on `_hub_get`:
- Patches `mcp_canada.modules.manitoba.client.api_get` at the module-local layer (Phase 15/17 pattern)
- Verifies `_hub_get` calls `api_get` once with `HUB_SEARCH_URL`
- Verifies `_hub_get` returns the Hub JSON dict directly (never inspects `CKAN` keys like `.get("success")`)
- Verifies `_hub_get` raises `httpx.HTTPStatusError` on non-dict/None responses

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] TypeError on None links in fetch_dataset_details**
- **Found during:** Task 1 GREEN run (test_returns_details_with_feature_server_url failed)
- **Issue:** `result.get("links")` returned `None` making `for link in None` fail with `TypeError`
- **Fix:** `links_raw = (result.get("links") or []) if isinstance(result, dict) else []`
- **Files modified:** `src/mcp_canada/modules/manitoba/client.py`
- **Commit:** inline during Task 1 RED→GREEN cycle

**2. [Rule 1 - Bug] Mock signature mismatch in test_max_records_clamped_to_5000**
- **Found during:** Task 2 GREEN run
- **Issue:** `_mock_fetch` with positional `url` param didn't match actual client call using all kwargs
- **Fix:** Changed to `**kwargs` signature + assert on `captured_kwargs[0].get("max_records")`
- **Files modified:** `test_tools.py`
- **Commit:** inline during Task 2 RED→GREEN cycle

### Pattern Deviations from Alberta

**`fetch_query_dataset` takes `feature_server_url` directly (not `package_id`):**
Alberta's `fetch_query_dataset` takes a `package_id` and then calls `fetch_dataset_details` internally to resolve the FeatureServer URL. Manitoba has no CKAN layer — agents already have the URL from `fetch_dataset_details` — so the client takes the URL directly. This is cleaner and avoids a redundant cache lookup.

**`fetch_organizations`/`fetch_categories` derive from search results:**
Alberta has a CKAN `organization_list` endpoint. Manitoba's Hub Search API is the only discovery surface — organizations are derived as unique `owner` values from Hub features. Categories are derived as unique `categories` path strings. This produces a smaller list but avoids a missing API endpoint.

## Self-Check: PASSED

Files verified present:
- `src/mcp_canada/modules/manitoba/client.py` — FOUND
- `src/mcp_canada/modules/manitoba/tools.py` — FOUND
- `src/mcp_canada/modules/manitoba/__tests__/test_client.py` — FOUND
- `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` — FOUND

Commits verified:
- `c8bb74d` (Task 1: client bodies + contract tests) — FOUND
- `f6c05aa` (Task 2: tool functions + tool tests) — FOUND

Test suite: 39/39 tests passing (19 client + 20 tools)
Coverage: 96.61% (≥95% required)
Pyright: 0 errors, 0 warnings
test_quality.py: 5/5 BM25 docstring checks pass
