---
phase: 20-nova-scotia-government-open-data
plan: "02"
subsystem: nova-scotia-discovery-tools
tags:
  - socrata
  - soda-api
  - nova-scotia
  - discovery-tools
  - wave-1
  - categories-workaround
dependency_graph:
  requires:
    - 20-01 (shared/socrata.py + module scaffold + locked signatures)
  provides:
    - 5 NS discovery tools (ns_search_datasets, ns_get_dataset_details, ns_query_dataset, ns_list_organizations, ns_list_categories)
    - fetch_* client bodies for all 5 discovery functions
    - TestSharedApiGetContract (module-local Socrata param contract)
  affects:
    - Phase 20 Plans 03-05 (curated tools build on client.py; discovery tools usable immediately)
    - Plan 07 (integration tests hit real discovery tools via MCP Client)
tech_stack:
  added: []
  patterns:
    - Socrata categories= workaround: q="" + client-side domain_category aggregation (never categories=)
    - SoQL passthrough: fetch_query_dataset exposes full $where/$select/$order/$limit/$offset/$q/$group surface
    - limit clamp [1, 1000] in fetch_search_datasets (SODA max is 50000 but search endpoint is more conservative)
    - fetch_organizations: wide page (limit=1000) → aggregate owner.display_name with counts
    - fetch_categories: wide page (limit=1000) → aggregate classification.domain_category with counts
    - include_geometry=False + select=None → select stays None (Socrata returns all including the_geom; agent controls via $select)
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/tools.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
decisions:
  - "fetch_categories uses q='' + client-side domain_category aggregation (never categories= param — confirmed broken, returns resultSetSize=0)"
  - "fetch_search_datasets clamps limit to [1, 1000] before SODA call (conservative for catalog endpoint)"
  - "include_geometry=False + select=None leaves select as None (documented: Socrata returns all fields including the_geom; agent must use $select to exclude)"
  - "fetch_organizations aggregates owner.display_name (primary) with domain_metadata Department fallback; sorted by dataset_count DESC"
  - "api_name='nova-scotia-socrata' used for all 5 discovery tools in make_response envelope"
  - "pyright sort-key lambda fix: int(x['dataset_count']) and int(x['count']) to avoid str|int operator error"
metrics:
  duration: "6 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 20 Plan 02: Nova Scotia Discovery Tools Summary

5 Socrata catalog discovery tools via shared/socrata.py with categories= workaround and full SoQL passthrough.

## What Was Built

### Task 1: Discovery client bodies + TestSharedApiGetContract

Filled 5 `NotImplementedError` stubs in `client.py` with production implementations:

| Function | Endpoint | Returns |
|----------|---------|---------|
| `fetch_search_datasets(query, limit, offset)` | `/api/catalog/v1` | `({"results": [...shaped], "total": N}, cached)` |
| `fetch_dataset_details(dataset_id)` | `/api/views/{id}.json` | `({"details": flat_meta}, cached)` |
| `fetch_query_dataset(dataset_id, where, select, order, limit, offset, q, group, include_geometry)` | `/resource/{id}.json` | `({"rows": [...], "count": N, "truncated": bool}, cached)` |
| `fetch_organizations()` | `/api/catalog/v1` (wide) | `({"organizations": [{name, dataset_count}]}, cached)` |
| `fetch_categories()` | `/api/catalog/v1` (wide) | `({"categories": [{name, count}]}, cached)` |

**Categories= workaround (pinned by contract test):**
- `fetch_categories` sends `q=""` to catalog (never `categories=`)
- Aggregates `classification.domain_category` from results client-side
- `TestSharedApiGetContract::test_categories_never_sends_categories_param` asserts `"categories" not in call_kwargs`

**Socrata param contract (TestSharedApiGetContract, 5 tests):**
- `test_search_catalog_forwards_q_limit_offset_only` — asserts q/limit/offset/only forwarded
- `test_search_catalog_offset_zero_forwarded` — asserts offset=0 forwarded to shared client (shared client handles wire omission)
- `test_categories_never_sends_categories_param` — the broken-param regression guard
- `test_categories_aggregates_domain_category_from_results` — correct field path verified
- `test_query_dataset_forwards_soql_params` — where/select/order/limit/offset forwarded

**24 client tests, all green.**

### Task 2: 5 discovery @tool functions + tool tests

| Tool | Description | api_name |
|------|-------------|---------|
| `ns_search_datasets` | Search NS Socrata catalog by keyword; data has results/total/offset/limit | nova-scotia-socrata |
| `ns_get_dataset_details` | Get schema + metadata for a dataset by 4x4 ID | nova-scotia-socrata |
| `ns_query_dataset` | SoQL passthrough: $where/$select/$order/$limit/$offset/$q/$group; include_geometry controls the_geom | nova-scotia-socrata |
| `ns_list_organizations` | List NS publishers with dataset counts | nova-scotia-socrata |
| `ns_list_categories` | List domain categories; docstring notes categories= is broken + workaround | nova-scotia-socrata |

**ns_query_dataset geometry control behavior:**
- `include_geometry=False` + `select=None` → select stays None (Socrata returns all fields including the_geom)
- `include_geometry=False` + `select="county,species"` → select passes through unchanged
- Docstring notes: "geometry (the_geom) is returned in rows when include_geometry=True or when $select is not specified"

**All tools follow conventions:**
- Standalone `@tool` from `fastmcp.tools`
- `lang: Literal["en", "fr"] = "en"` parameter
- `make_response(data, api_name="nova-scotia-socrata", ...)` on success
- `make_error("UPSTREAM_ERROR", ...)` on exception
- Single-line `Use for:` + `Keywords:` (10+ terms each)
- `ns_` prefix

**18 tool tests, all green** — happy path + error path + lang passthrough for each tool.

## Socrata Param Contract

| Claim | Verified by |
|-------|-------------|
| `categories=` never sent | `TestSharedApiGetContract::test_categories_never_sends_categories_param` |
| `domain_category` aggregated client-side | `TestSharedApiGetContract::test_categories_aggregates_domain_category_from_results` |
| `q`/`limit`/`offset`/`only` forwarded | `TestSharedApiGetContract::test_search_catalog_forwards_q_limit_offset_only` |
| `$where`/`$select`/`$order`/`$limit` forwarded | `TestSharedApiGetContract::test_query_dataset_forwards_soql_params` |
| `offset=0` forwarded to shared client | `TestSharedApiGetContract::test_search_catalog_offset_zero_forwarded` |

## Coverage

- Module test suite: 42 tests, all pass
- Overall project coverage: 96.82% (≥95% threshold maintained)
- `shared/socrata.py`: 95% covered

## Deviations from Plan

**1. [Rule 1 - Bug] Pyright sort-key lambda type error**
- **Found during:** Task 2 verification (`uv run pyright`)
- **Issue:** `key=lambda x: (-x["count"], ...)` — pyright infers `x` as `dict[str, str | int]` from list-comp mixing string and int values; `-` not supported for `str | int`
- **Fix:** Changed to `(-int(x["count"]), str(x["name"]))` and `(-int(x["dataset_count"]), str(x["name"]))`
- **Files modified:** `src/mcp_canada/modules/nova_scotia/client.py`
- **Commit:** 1bbc80a

**2. Pre-existing pyright error in prompts.py (deferred, out of scope)**
- `fastmcp.prompts.prompt` import path causes pyright false-positive in Wave 0 scaffold
- Runtime works fine; same pattern used across all prior phase scaffolds
- Logged for Plan 06 (prompts implementation) to resolve

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `src/mcp_canada/modules/nova_scotia/client.py` | FOUND |
| `src/mcp_canada/modules/nova_scotia/tools.py` | FOUND |
| `src/mcp_canada/modules/nova_scotia/__tests__/test_client.py` | FOUND |
| `src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py` | FOUND |
| Commit 22bb983 (Task 1) | FOUND |
| Commit 1bbc80a (Task 2) | FOUND |
| `ns_search_datasets` importable | FOUND |
| `ns_get_dataset_details` importable | FOUND |
| `ns_query_dataset` importable | FOUND |
| `ns_list_organizations` importable | FOUND |
| `ns_list_categories` importable | FOUND |
| 42 module tests pass | PASSED |
| Coverage ≥ 95% | 96.82% |
