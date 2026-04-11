---
phase: 15-british-columbia-government-open-data
verified: 2026-04-10T00:00:00Z
status: passed
score: 20/20 must-haves verified
re_verification: false
---

# Phase 15: British Columbia Open Data — Verification Report

**Phase Goal:** Add British Columbia provincial open data catalogue (CKAN at catalogue.data.gov.bc.ca) + WFS/OGC geospatial support (openmaps.gov.bc.ca / BC Geographic Warehouse) via ~20 tools, reusable shared/ogc.py WFS client, two-step discovery->details->query workflow, 6 prompts + 7 resources, bilingual/BM25/envelope compliance, README + CLAUDE.md updates, >=95% coverage.
**Verified:** 2026-04-10
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | shared/ogc.py provides WfsError, wfs_get_features, wfs_page_all, wfs_count | VERIFIED | `src/mcp_canada/shared/ogc.py` 303 lines; all 4 exported symbols present |
| 2 | wfs_get_features uses typeNames (plural), count, startIndex, sortBy=OBJECTID, srsName, outputFormat=application/json | VERIFIED | Lines 98-108 of ogc.py confirm exact WFS 2.0 parameter names |
| 3 | HTTP 400 + XML content-type parsed as ows:ExceptionReport; .json() never called on 400s | VERIFIED | Lines 125-126: guard on `status_code==400` and `"xml"` in content-type before raise_for_status |
| 4 | wfs_page_all paginates until no more data or max_records cap; truncated=True only when cap hit | VERIFIED | Lines 171-202 of ogc.py; `return accumulated, False` on last page vs `return accumulated, True` on cap |
| 5 | shared/ogc.py delegates GeoJSON property extraction to shared/parsers._parse_geojson | VERIFIED | Line 25: `from mcp_canada.shared.parsers import _parse_geojson`; called at line 135 |
| 6 | british_columbia module auto-registers via FileSystemProvider (MODULE_NAME=british_columbia, MODULE_DESCRIPTION present) | VERIFIED | `__init__.py` has both constants; 7-file module pattern complete |
| 7 | constants.py hardcodes BASE_URL, WFS_BASE_URL, RATE_GROUP_CKAN/WFS, rate limits, cache TTLs, all 15 BCGW layer constants | VERIFIED | All constants verified in constants.py (83 lines); FTEN_CUT_BLOCK_POLY_SVW and TA_PARK_ECORES_PA_SVW exact matches |
| 8 | 20 bc_ tools registered: 5 CKAN discovery + 15 curated WFS tools | VERIFIED | 20 `@tool` decorators confirmed; `grep bc_` names match expected list |
| 9 | bc_query_features routes to wfs_page_all via _wfs_fetch when queryable_via_wfs=True; falls back to fetch_and_parse otherwise | VERIFIED | Two-branch routing confirmed in tools.py; both branches call make_response |
| 10 | bc_get_water_wells requires city, well_class, or aquifer_id — make_error(INVALID_INPUT) otherwise | VERIFIED | Guard at lines 758-762 of tools.py confirmed |
| 11 | bc_get_cut_blocks uses FTEN_CUT_BLOCK_POLY_SVW (not superseded name) | VERIFIED | constants.py line 55: `CUT_BLOCKS_LAYER = "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW"` |
| 12 | bc_get_protected_areas uses WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW | VERIFIED | constants.py line 58: `PROTECTED_AREAS_LAYER = "WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW"` |
| 13 | _wfs_fetch uses CACHE_TTL_ACTIVE for active fires, CACHE_TTL_STATIC for all other layers | VERIFIED | client.py line 322: TTL selected by `layer in _ACTIVE_LAYERS` frozenset |
| 14 | 6 bc_ prompts (3 guided workflow list[Message], 3 quick lookup str) | VERIFIED | prompts.py: bc_explore_wildfires, bc_explore_forestry, bc_explore_environment return list[Message]; bc_quick_dataset_search, bc_check_water_quality, bc_wildfire_status_now return str |
| 15 | 7 bc_ resources with data://, docs://, template:// URIs using json.dumps for data:// | VERIFIED | resources.py: 7 @resource functions, json.dumps confirmed for data://bc/* URIs |
| 16 | docs://bc/wfs-query-guide explains CKAN->WFS two-step workflow | VERIFIED | URI registered; references bc_query_features; confirmed in resources.py line 342 |
| 17 | Integration tests TestBcToolScenarios and TestBcPromptsResources populated (not stubs) | VERIFIED | TestBcToolScenarios has 8+ live test methods in test_tool_scenarios.py line 1408+; TestBcPromptsResources has 3 live tests in test_prompts_resources_scenarios.py line 524+; no xfail stubs remain |
| 18 | README.md has British Columbia section with 20 bc_ tools; tool count updated to 175 | VERIFIED | README line 20: "175 tools"; "### British Columbia Open Data — 20 tools" at line 516; 20 entries confirmed by grep |
| 19 | CLAUDE.md documents OGC WFS as third portal technology | VERIFIED | CLAUDE.md line 65: `ogc.py — OGC WFS 2.0 client`; line 73: WFS/OGC documented as distinct portal tech alongside CKAN and ArcGIS Hub |
| 20 | Coverage >=95% with BC module included | VERIFIED | Full suite result: 96.41% total coverage; `Required test coverage of 95% reached`; 1912 passed, 2 skipped |

**Score:** 20/20 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/shared/ogc.py` | Reusable WFS 2.0 client | VERIFIED | 303 lines; wfs_get_features, wfs_page_all, wfs_count, WfsError all present and substantive |
| `src/mcp_canada/shared/__tests__/test_ogc.py` | WFS client unit tests | VERIFIED | 375 lines; 16 test methods including pagination, XML error parsing, GeoJSON happy path |
| `src/mcp_canada/modules/british_columbia/__init__.py` | MODULE_NAME + MODULE_DESCRIPTION | VERIFIED | Both constants present; MODULE_DESCRIPTION references CKAN + WFS + all curated domains |
| `src/mcp_canada/modules/british_columbia/constants.py` | BASE_URL, WFS_BASE_URL, rates, TTLs, 15 layers | VERIFIED | 83 lines; all expected constants present with correct values |
| `src/mcp_canada/modules/british_columbia/schemas.py` | Flat Pydantic v2 models | VERIFIED | Present; contains model classes |
| `src/mcp_canada/modules/british_columbia/client.py` | CKAN functions + _wfs_fetch | VERIFIED | 340 lines; all exported functions populated (fetch_search_datasets, fetch_dataset_details, fetch_organizations, fetch_tags, _wfs_fetch) |
| `src/mcp_canada/modules/british_columbia/tools.py` | 20 bc_ @tool functions | VERIFIED | 1173 lines; 20 @tool decorators; all 20 tool names confirmed |
| `src/mcp_canada/modules/british_columbia/prompts.py` | 6 bilingual @prompt functions | VERIFIED | 304 lines; 6 @prompt decorators; 3 list[Message] + 3 str return types |
| `src/mcp_canada/modules/british_columbia/resources.py` | 7 zero-parameter @resource functions | VERIFIED | 791 lines; 7 @resource decorators; data://, docs://, template:// URIs present; json.dumps for data:// |
| `src/mcp_canada/modules/british_columbia/__tests__/conftest.py` | 12 fixtures | VERIFIED | Present with pytest.fixture decorators |
| `src/mcp_canada/modules/british_columbia/__tests__/test_client.py` | Populated test classes | VERIFIED | TestWfsFetchShared present; queryable_via_wfs tested |
| `src/mcp_canada/modules/british_columbia/__tests__/test_tools.py` | 20 filled tool test classes | VERIFIED | 1322 lines; 84 test methods; no xfail stubs; make_response asserts present |
| `src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py` | Populated TestBcPrompts + TestBcResources | VERIFIED | list_prompts asserts present; template placeholder tests |
| `tests/integration/test_tool_scenarios.py` | TestBcToolScenarios populated | VERIFIED | 8 live test methods; uses call_tool through MCP Client layer; no xfail |
| `tests/integration/test_prompts_resources_scenarios.py` | TestBcPromptsResources populated | VERIFIED | 3 live tests; list_prompts + read_resource through MCP Client layer |
| `README.md` | British Columbia section + 175 tool count | VERIFIED | "175 tools" in header; 20 bc_ tools listed in catalog |
| `CLAUDE.md` | WFS/OGC as third portal technology | VERIFIED | ogc.py documented with WFS/OGC; BC two-step workflow explained |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `shared/ogc.py` | `shared/parsers.py` | `from mcp_canada.shared.parsers import _parse_geojson` | WIRED | Line 25 of ogc.py; used at line 135 for GeoJSON property extraction |
| `shared/ogc.py` | `xml.etree.ElementTree` | `import xml.etree.ElementTree as ET` | WIRED | Line 19 of ogc.py; used in `_parse_wfs_exception` |
| `modules/british_columbia/__init__.py` | FileSystemProvider auto-discovery | `MODULE_NAME` constant | WIRED | Both MODULE_NAME and MODULE_DESCRIPTION present |
| `modules/british_columbia/client.py` | `shared/ogc.py` | `from mcp_canada.shared.ogc import WfsError, wfs_page_all` | WIRED | Line 20; wfs_page_all called at line 328 inside _wfs_fetch |
| `modules/british_columbia/client.py` | `shared/cache.py` | `from mcp_canada.shared.cache import cached_fetch` | WIRED | Line 18; used in all 5 public fetch functions |
| `modules/british_columbia/client.py` | `shared/rate_limiter.py` | `get_limiter(RATE_GROUP_WFS, RATE_LIMIT_WFS)` | WIRED | Line 324 in _wfs_fetch; RATE_GROUP_CKAN used in CKAN functions |
| `modules/british_columbia/client.py` | `shared/http.py` | `from mcp_canada.shared.http import api_get` | WIRED | Line 19; used in _api_get helper |
| `modules/british_columbia/tools.py` | `modules/british_columbia/client.py` | `from .client import _wfs_fetch, fetch_dataset_details, ...` | WIRED | Lines 19-25; all 5 client functions imported and used |
| `modules/british_columbia/tools.py` | `shared/parsers.py` | `from mcp_canada.shared.parsers import fetch_and_parse` | WIRED | Line 17; used in bc_query_features file-download branch |
| `modules/british_columbia/tools.py` | `shared/envelope.py` | `from mcp_canada.shared.envelope import make_error, make_response` | WIRED | Line 15; all tools use make_response/make_error |
| `modules/british_columbia/prompts.py` | FileSystemProvider | Standalone `@prompt` decorator | WIRED | Line 17: `from fastmcp.prompts import Message, prompt`; all 6 use @prompt |
| `modules/british_columbia/resources.py` | FileSystemProvider | Standalone `@resource` decorator | WIRED | Line 19: `from fastmcp.resources import resource`; all 7 use @resource(uri=...) |
| `tests/integration/test_tool_scenarios.py::TestBcToolScenarios` | BCDC + BCGW WFS live endpoints | `client.call_tool` via MCP Client layer | WIRED | call_tool helper used in all 8 test methods |
| `tests/integration/test_prompts_resources_scenarios.py::TestBcPromptsResources` | FastMCP prompts/list and resources/list | `list_prompts()` and `read_resource()` | WIRED | Both used in 3 test methods |

---

## Requirements Coverage

Phase 15 PLAN frontmatter declares `requirements: []` for all four plans with an explanatory note: "Phase 15 has no explicit REQ IDs in REQUIREMENTS.md yet — delivers on milestone provincial coverage goal." A review of `.planning/REQUIREMENTS.md` confirms no Phase 15 REQ IDs exist there. This is consistent: the decision to omit REQ IDs was intentional and matches the REQUIREMENTS.md state.

No orphaned requirements found.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `__tests__/test_tools.py` | 3 (docstring) | Comment says "placeholders for 15 curated" | Info | Stale comment — the 15 curated test classes are actually filled in; no functional impact |

No blockers or warnings found. The one "placeholder" string appears in a comment describing the historical scaffolding context; all test classes are fully populated (84 test methods, 1322 lines, 0 xfail stubs).

---

## Human Verification Required

### 1. Live WFS endpoint availability

**Test:** Run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "TestBcToolScenarios or TestBcPromptsResources"`
**Expected:** All 8 tool scenarios and 3 prompts/resources scenarios pass (or skip gracefully if live endpoints are down)
**Why human:** Integration tests hit `openmaps.gov.bc.ca` WFS and `catalogue.data.gov.bc.ca` CKAN live; endpoint availability is an external dependency

### 2. BM25 discovery of bc_ tools with natural language

**Test:** Start the MCP server and call `discover_tools` with "british columbia wildfire", "BC provincial parks", "water wells BC"
**Expected:** At least one `bc_` prefixed tool appears in top 5 results for each query
**Why human:** BM25 index is built at runtime from docstring keywords; integration test covers a subset but broader query coverage is best verified interactively

### 3. Bilingual prompt output quality

**Test:** Call `bc_explore_wildfires(lang="fr")` and `bc_explore_environment(lang="fr")` through an MCP client
**Expected:** French content is complete, tool names are correct, step-by-step instructions are coherent
**Why human:** Content quality and completeness of French translations requires human judgment

---

## Gaps Summary

No gaps. All 20 must-haves verified against the actual codebase.

The phase delivered:
- `shared/ogc.py` — reusable WFS 2.0 client (303 lines) with WfsError, wfs_get_features, wfs_page_all, wfs_count; XML ExceptionReport parsing via stdlib ET; delegates to _parse_geojson
- Complete 7-file `modules/british_columbia/` pattern: constants (15 verified BCGW layers), client (CKAN + WFS fetch with caching/rate limiting), 20 @tool functions, 6 @prompt functions, 7 @resource functions
- Two-step routing in bc_query_features: WFS branch for queryable_via_wfs=True, file-download branch via fetch_and_parse otherwise
- bc_get_water_wells 130K-record guard (requires at least one of city/well_class/aquifer_id)
- All curated WFS tools catch WfsError and return make_error(UPSTREAM_ERROR, exception_code=e.code)
- Integration tests populated (not stubs) through MCP Client layer for both tool scenarios and prompts/resources
- README updated to 175 tools with full BC catalog section; CLAUDE.md documents WFS/OGC as third portal technology
- Coverage: 96.41% (requirement: >=95%)

---

_Verified: 2026-04-10_
_Verifier: Claude (gsd-verifier)_
