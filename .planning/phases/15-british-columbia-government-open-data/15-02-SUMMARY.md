---
phase: 15
plan: 02
subsystem: british_columbia-ckan-discovery
tags: [ckan, bc, british-columbia, discovery, wfs-routing, tdd, wave-2]
dependency_graph:
  requires:
    - shared/ogc.py (WfsError, wfs_page_all)
    - modules/british_columbia/constants.py (BASE_URL, RATE_GROUP_CKAN, CACHE_TTL_* constants)
    - modules/british_columbia/schemas.py (BcResource, BcDatasetDetails)
    - shared/cache.py (cached_fetch)
    - shared/rate_limiter.py (get_limiter)
    - shared/http.py (api_get)
    - shared/parsers.py (fetch_and_parse)
    - shared/envelope.py (make_response, make_error)
  provides:
    - modules/british_columbia/client.py (fetch_search_datasets, fetch_dataset_details, fetch_organizations, fetch_tags, _compute_queryable_via_wfs)
    - modules/british_columbia/tools.py (bc_search_datasets, bc_get_dataset_details, bc_query_features, bc_list_organizations, bc_list_categories, _build_cql, _pick_file_resource)
  affects:
    - Plan 03 (depends on _wfs_fetch contract and _build_cql helper in tools.py)
    - Plan 04 (depends on discovery tools being functional for prompts/resources)
tech_stack:
  added: []
  patterns:
    - TDD RED→GREEN for both client and tools layers
    - _compute_queryable_via_wfs: synchronous pure helper, deterministic from CKAN resource metadata
    - _build_cql: upper-cases field names, escapes single-quotes, casts numerics — no new deps
    - _pick_file_resource: prefers CSV > XLSX > GEOJSON > JSON > XLS
    - queryable_via_wfs routing: WFS path vs file-parser path in bc_query_features
    - CKAN _api_get helper mirrors Ontario pattern (success envelope unwrap + raise_for_status)
    - cache key prefix "bc:" isolates BC keys from other CKAN modules (Ontario: "ontario:")
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/british_columbia/client.py
    - src/mcp_canada/modules/british_columbia/tools.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_client.py
    - src/mcp_canada/modules/british_columbia/__tests__/test_tools.py
    - .planning/phases/15-british-columbia-government-open-data/15-VALIDATION.md
decisions:
  - "_api_get helper in client.py mirrors Ontario pattern exactly: BASE_URL + path, response.raise_for_status(), envelope['result'] unwrap"
  - "_compute_queryable_via_wfs is synchronous pure logic (no I/O) — takes resources list, returns (bool, str|None)"
  - "cache key prefix bc: isolates BC CKAN keys (bc:search:*, bc:details:*, bc:orgs, bc:tags) from other modules"
  - "bc_list_categories surfaces tags (not groups) — BC CKAN group_list returns HTTP 403 per RESEARCH Pitfall 7"
  - "_build_cql upper-cases field names to match BCGW convention (all uppercase field names per RESEARCH Pitfall 6)"
  - "bc_query_features routes to _wfs_fetch stub (Plan 03 will implement body) for WFS path — interface contract established"
  - "fetch_and_parse called with ttl=CACHE_TTL_STATIC for file-path routing in bc_query_features"
metrics:
  duration: "~5 minutes"
  completed_date: "2026-04-10"
  tasks_completed: 2
  files_created: 0
  files_modified: 5
---

# Phase 15 Plan 02: BC CKAN Discovery Tools Summary

Implemented the 4 CKAN client functions and 5 standalone `@tool` discovery tools for the BC Data Catalogue, including the `queryable_via_wfs` derivation logic and the two-step WFS routing primitive in `bc_query_features`.

## What Was Built

### Task 1: CKAN Client Functions (TDD)

Filled in all 4 `NotImplementedError` stubs in `client.py`:

- **`_compute_queryable_via_wfs(resources)`** — synchronous pure helper. Scans resource list for the three-field match: `bcdc_type == "geographic"` AND `resource_storage_location == "bc geographic warehouse"` AND `bool(object_name)`. Returns `(True, object_name)` on first match or `(False, None)`. Deterministic from CKAN metadata — no runtime WFS probing.

- **`fetch_search_datasets(q, rows, start, fq)`** — CKAN `package_search` with bc: prefixed cache keys, `CACHE_TTL_SEARCH` (1hr), rate-limited to `bc_ckan` at 10 req/s. Shapes results to flat summary dicts including `resources_count`.

- **`fetch_dataset_details(package_id)`** — CKAN `package_show` with `queryable_via_wfs` and `object_name` surfaced at top level. Flattens tags list, org name, and resource dicts.

- **`fetch_organizations()`** — CKAN `organization_list?all_fields=true` with `CACHE_TTL_META` (86400s).

- **`fetch_tags()`** — CKAN `tag_list` with `CACHE_TTL_META` (86400s).

Private `_api_get` helper mirrors Ontario pattern: `BASE_URL + path`, `response.raise_for_status()`, `envelope["result"]` unwrap, raises `httpx.HTTPStatusError` on `success=False`.

22 unit tests green covering: shaped summaries, pagination params, fq forwarding, caching, rate limiting, queryable_via_wfs detection (5 edge cases).

### Task 2: 5 Discovery @tool Functions (TDD)

5 standalone `@tool` functions in `tools.py` with complete BM25 docstrings:

1. **`bc_search_datasets`** — Validates `q` non-empty, builds `fq` from optional `organization`/`tag` params, calls `fetch_search_datasets`. Returns `make_response` with `api_name="bc-data-catalogue"`.

2. **`bc_get_dataset_details`** — Surfaces `object_name` and `queryable_via_wfs` from `fetch_dataset_details`. Returns `NOT_FOUND` on 404.

3. **`bc_query_features`** — The two-step routing primitive: fetches dataset details, then routes to either `_wfs_fetch` (WFS path, Plan 03 implements body) or `fetch_and_parse` (file path). Builds CQL via `_build_cql`, picks file resource via `_pick_file_resource`. Catches `WfsError` and returns `UPSTREAM_ERROR`.

4. **`bc_list_organizations`** — Delegates to `fetch_organizations`. `api_url = BASE_URL + "organization_list"`.

5. **`bc_list_categories`** — Delegates to `fetch_tags` (BC has no CKAN groups — Pitfall 7). Docstring explicitly documents the BC quirk.

Private helpers:
- `_build_cql(filters)` — upper-cases field names, doubles single quotes in strings, no-quotes for int/float, IN clause for lists.
- `_pick_file_resource(resources)` — prefers CSV > XLSX > GEOJSON > JSON > XLS.

29 unit tests green covering: envelope shapes, routing logic, CQL escaping, CQL numeric casting, WfsError propagation, truncated flag, empty-input validation.

## Decisions Made

- `_api_get` mirrors Ontario pattern exactly for CKAN envelope unwrapping — consistent module pattern across provincial CKAN modules.
- `bc:` prefix isolates BC cache keys from Ontario (`ontario:`), Toronto (`toronto:`), and federal CKAN keys.
- `bc_list_categories` surfaces tags, not groups — BC CKAN `group_list` returns HTTP 403 (RESEARCH Pitfall 7). Docstring explicitly notes this for agents.
- `_build_cql` upper-cases all field names — BCGW fields are uppercase (RESEARCH Pitfall 6). This prevents silent filter mismatches for agents passing lowercase field names.
- `bc_query_features` calls `_wfs_fetch` stub (raises `NotImplementedError`) — the function contract (params, return shape) is established here; Plan 03 fills the body.

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

Verified below.
