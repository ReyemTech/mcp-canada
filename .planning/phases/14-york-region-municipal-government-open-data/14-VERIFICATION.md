---
phase: 14-york-region-municipal-government-open-data
verified: 2026-04-09T00:00:00Z
status: passed
score: 14/14 must-haves verified
re_verification: false
---

# Phase 14: York Region Municipal Government Open Data — Verification Report

**Phase Goal:** Add York Region's municipal open data to mcp-canada via 4 verified ArcGIS Hub portals (York Region regional, Markham, Newmarket, Aurora). Build shared/arcgis_hub.py as reusable ArcGIS REST Feature Service client for future ArcGIS Hub modules. Include prompts.py and resources.py from the start (7-file pattern).
**Verified:** 2026-04-09T00:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                               | Status     | Evidence                                                                                                             |
|----|---------------------------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------------------------------------------------------|
| 1  | shared/arcgis_hub.py provides a reusable ArcGIS Hub Search API + FeatureServer client                              | VERIFIED   | File exists (9.8K), exports search_hub_datasets, query_feature_service, get_layer_metadata, get_count, shape_hub_dataset |
| 2  | Hub Search API call uses /api/search/v1/collections/all/items (correct endpoint)                                    | VERIFIED   | Line 29: `HUB_SEARCH_PATH = "/api/search/v1/collections/all/items"` used in search_hub_datasets                     |
| 3  | FeatureServer query auto-paginates while exceededTransferLimit is true, caps at 5000, returns truncated flag        | VERIFIED   | Lines 139-156: _run_pagination loop checks exceededTransferLimit, sets truncated=True at max_records cap             |
| 4  | Layer metadata fetch reads maxRecordCount                                                                           | VERIFIED   | Lines 200-208: get_layer_metadata returns {"max_record_count": int(data.get("maxRecordCount", ...))}                 |
| 5  | york_region module auto-registers via FileSystemProvider (MODULE_NAME + MODULE_DESCRIPTION)                         | VERIFIED   | __init__.py: MODULE_NAME = "york_region", MODULE_DESCRIPTION with 4-portal description                               |
| 6  | constants.py lists all 4 verified portal URLs and None for 6 municipalities without portals                         | VERIFIED   | PORTAL_URLS has 10 keys: york_region, markham, newmarket, aurora (real URLs) + 5 None + 1 census-only               |
| 7  | york_region/client.py wraps shared/arcgis_hub.py with portal-specific constants and (data, was_cached) tuples      | VERIFIED   | Imports from arcgis_hub, uses cached_fetch + get_limiter("arcgis_hub", 5.0), all fetch_ return tuples               |
| 8  | NoPortalError raised for municipalities without portals, tools translate to NOT_FOUND                               | VERIFIED   | class NoPortalError at line 64, _require_portal raises it; tools.py _call_client catches and returns make_error NOT_FOUND |
| 9  | Agent can search all 4 portals, query features, list orgs/categories via {prefix} tools (20 discovery tools)       | VERIFIED   | 31 @tool decorators in tools.py; 20 discovery tools (5 × 4 portals) confirmed                                        |
| 10 | Curated York Region tools cover transit, roads, public health, census, waste                                        | VERIFIED   | fetch_transit_stops, fetch_transit_routes, fetch_regional_roads, fetch_beach_water_testing, fetch_hospitals, fetch_waste_diversion, fetch_census_age_sex, fetch_census_income confirmed in client.py |
| 11 | Curated Markham tools cover addresses and road network                                                               | VERIFIED   | fetch_markham_addresses, fetch_markham_roads present and wired from tools.py                                          |
| 12 | prompts.py has bilingual @prompt functions                                                                           | VERIFIED   | 5 @prompt functions; from fastmcp.prompts import Message, prompt confirmed                                            |
| 13 | resources.py has zero-parameter @resource functions with data://, docs://, template:// URIs                         | VERIFIED   | 8 @resource functions; from fastmcp.resources import resource confirmed                                               |
| 14 | Integration tests call tools through MCP Client layer and verify prompt/resource discovery                          | VERIFIED   | TestYorkRegionToolScenarios at line 1305 in test_tool_scenarios.py; TestYorkRegionPromptsResources at line 483 in test_prompts_resources_scenarios.py |

**Score:** 14/14 truths verified

### Required Artifacts

| Artifact                                                              | Expected                                                         | Status     | Details                                                                        |
|-----------------------------------------------------------------------|------------------------------------------------------------------|------------|--------------------------------------------------------------------------------|
| `src/mcp_canada/shared/arcgis_hub.py`                                 | Reusable ArcGIS Hub Search API + FeatureServer async client      | VERIFIED   | 9.8K file, 289 lines, exports all 5 public functions, imports _parse_geojson   |
| `src/mcp_canada/shared/__tests__/test_arcgis_hub.py`                  | Unit tests for shared ArcGIS Hub client                          | VERIFIED   | 16.1K file, contains class Test, 19 tests (per SUMMARY)                        |
| `src/mcp_canada/modules/york_region/__init__.py`                      | MODULE_NAME + MODULE_DESCRIPTION for auto-registration           | VERIFIED   | MODULE_NAME = "york_region", MODULE_DESCRIPTION present                        |
| `src/mcp_canada/modules/york_region/constants.py`                     | PORTAL_URLS mapping, FeatureServer URLs, rate/cache constants    | VERIFIED   | PORTAL_URLS with 10 keys, all FeatureServer URLs, RATE_GROUP, RATE_LIMIT, CACHE_TTL constants |
| `src/mcp_canada/modules/york_region/schemas.py`                       | Flat Pydantic v2 models                                          | VERIFIED   | File exists with class definitions                                              |
| `src/mcp_canada/modules/york_region/client.py`                        | Portal-specific fetch functions wrapping shared/arcgis_hub.py    | VERIFIED   | 504 lines, 12 async def fetch_ functions                                        |
| `src/mcp_canada/modules/york_region/tools.py`                         | 27+ @tool functions with BM25 docstrings                         | VERIFIED   | 665 lines, 31 @tool decorators, min_lines=400 satisfied                        |
| `src/mcp_canada/modules/york_region/prompts.py`                       | 4-6 bilingual @prompt functions with york_region_ prefix         | VERIFIED   | 5 @prompt functions, bilingual (en/fr), from fastmcp.prompts import            |
| `src/mcp_canada/modules/york_region/resources.py`                     | 6-10 zero-parameter @resource functions                          | VERIFIED   | 8 @resource functions, zero-parameter, data://, docs://, template:// URIs      |
| `src/mcp_canada/modules/york_region/__tests__/test_tools.py`          | Unit tests for all tools                                         | VERIFIED   | 74 tests per SUMMARY (155 total york_region tests pass)                        |
| `src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py` | Unit tests for prompts and resources                          | VERIFIED   | 17 tests per SUMMARY, file exists                                               |
| `tests/integration/test_tool_scenarios.py`                            | TestYorkRegionToolScenarios integration tests                    | VERIFIED   | class TestYorkRegionToolScenarios at line 1305 confirmed                       |
| `tests/integration/test_prompts_resources_scenarios.py`               | TestYorkRegionPromptsResources integration tests                 | VERIFIED   | class TestYorkRegionPromptsResources at line 483 confirmed                     |
| `README.md`                                                            | York Region section with tool list + updated total count         | VERIFIED   | Section "York Region Municipal Open Data — 27 tools" at line 458; header shows 155 tools |
| `.planning/REQUIREMENTS.md`                                            | YR-01 through YR-14 definitions + traceability rows              | VERIFIED   | All 14 definitions present, 14 traceability rows present                       |

### Key Link Verification

| From                                  | To                              | Via                                         | Status   | Details                                                          |
|---------------------------------------|---------------------------------|---------------------------------------------|----------|------------------------------------------------------------------|
| `york_region/client.py`               | `shared/arcgis_hub.py`          | from mcp_canada.shared.arcgis_hub import    | WIRED    | Import confirmed at line 19                                      |
| `shared/arcgis_hub.py`                | `shared/parsers.py`             | from mcp_canada.shared.parsers import _parse_geojson | WIRED | Import confirmed at line 21                                |
| `york_region/client.py`               | `shared/cache.py`               | from mcp_canada.shared.cache import cached_fetch | WIRED | Import confirmed; used in _fetch_features private helper    |
| `york_region/client.py`               | `shared/rate_limiter.py`        | get_limiter("arcgis_hub", 5.0)              | WIRED    | Import at line 27, usage at line 109: get_limiter(RATE_GROUP, RATE_LIMIT) |
| `york_region/tools.py`                | `york_region/client.py`         | from mcp_canada.modules.york_region.client import | WIRED | All fetch_ functions imported at lines 13-32                |
| `york_region/tools.py`                | `shared/envelope.py`            | make_response / make_error                  | WIRED    | from mcp_canada.shared.envelope import make_error, make_response confirmed |
| `york_region/tools.py`                | NoPortalError handling          | try/except NoPortalError -> make_error(NOT_FOUND) | WIRED | _call_client catches NoPortalError at line 64-65 in tools.py |
| `york_region/prompts.py`              | fastmcp.prompts @prompt         | from fastmcp.prompts import Message, prompt | WIRED    | Import confirmed at line 14 of prompts.py                       |
| `york_region/resources.py`            | fastmcp.resources @resource     | from fastmcp.resources import resource      | WIRED    | Import confirmed at line 18 of resources.py                     |
| `tests/integration/test_tool_scenarios.py` | MCP Client layer via call_tool | call_tool('call_tool', {'name': 'york_region_...'}) | WIRED | york_region_search_datasets, york_region_get_transit_stops, york_region_get_public_health, markham_get_addresses calls confirmed |

### Requirements Coverage

| Requirement | Source Plan | Description                                                                                 | Status    | Evidence                                                              |
|-------------|------------|----------------------------------------------------------------------------------------------|-----------|-----------------------------------------------------------------------|
| YR-01       | 14-01      | shared/arcgis_hub.py reusable ArcGIS Hub Search API + FeatureServer client                  | SATISFIED | File exists with all 5 public functions; imports _parse_geojson       |
| YR-02       | 14-01      | Hub Search uses /api/search/v1/collections/all/items (not deprecated /api/v2/datasets)       | SATISFIED | HUB_SEARCH_PATH constant and usage confirmed in arcgis_hub.py         |
| YR-03       | 14-01      | FeatureServer auto-paginates while exceededTransferLimit, caps at 5000, returns truncated    | SATISFIED | _run_pagination loop logic and truncated flag verified in arcgis_hub.py |
| YR-04       | 14-01      | 4 verified portals, 6 municipalities without portals return structured NOT_FOUND             | SATISFIED | PORTAL_URLS has 4 real URLs + 5 None + 1 census-only; NoPortalError wired to NOT_FOUND |
| YR-05       | 14-01      | Each verified portal gets 5 discovery tools (20 total)                                       | SATISFIED | 20 discovery tools confirmed across 4 portals (york_region, markham, newmarket, aurora) |
| YR-06       | 14-02      | Agent can search YRT/Viva transit stops and routes from York Region FeatureServer             | SATISFIED | york_region_get_transit_stops, york_region_get_transit_routes tools present |
| YR-07       | 14-02      | Agent can fetch York Region regional road network                                             | SATISFIED | york_region_get_road_network tool present                             |
| YR-08       | 14-02      | Agent can query York Region public health (beach water, hospitals, drinking water)            | SATISFIED | york_region_get_public_health dispatch tool with beach_water/hospital/drinking_water variants |
| YR-09       | 14-02      | Agent can query York Region 2021 Census demographics by DA with CSDNAME filter               | SATISFIED | york_region_get_census_demographics dispatch tool with age_sex/income variants |
| YR-10       | 14-02      | Agent can query York Region waste management data                                             | SATISFIED | york_region_get_waste_data dispatch tool with diversion_statistics/sites variants |
| YR-11       | 14-02      | Agent can search Markham civic addresses and road network                                     | SATISFIED | markham_get_addresses, markham_get_road_network tools present        |
| YR-12       | 14-03      | York Region module has prompts.py with 4-6 bilingual @prompt functions                       | SATISFIED | 5 @prompt functions confirmed in prompts.py                          |
| YR-13       | 14-03      | York Region module has resources.py with 6-10 zero-parameter @resource functions             | SATISFIED | 8 @resource functions with data://, docs://, template:// URIs confirmed |
| YR-14       | 14-03      | All tools follow conventions, discoverable via discover_tools, README reflects catalog        | SATISFIED | 1,754 tests pass (incl. test_quality.py BM25 enforcement); README updated; pyright 0 errors |

**Note:** REQUIREMENTS.md traceability table shows "Planned" for all YR rows rather than "Complete". This is a documentation-only gap — the phase is fully implemented and all 14 requirements are satisfied by the code. No functional impact.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | No TODOs, placeholders, empty stubs, or console-only implementations found | — | — |

### Human Verification Required

#### 1. ArcGIS Hub Portal Availability

**Test:** Run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k york_region` against live endpoints.
**Expected:** Integration tests pass — York Region ArcGIS Hub portals respond and return real data.
**Why human:** ArcGIS Hub endpoints are external services that can become unavailable, rotate URLs, or change authentication. The utility.arcgis.com proxy URLs for Markham are especially noted in constants.py as potentially rotating.

#### 2. BM25 Discover-ability of York Region Tools

**Test:** Connect an MCP client and call `discover_tools` with queries like "York Region transit stops", "Markham addresses", "york region open data".
**Expected:** York Region tools surface in top 5 BM25 results for domain-relevant queries.
**Why human:** BM25 relevance ranking is not directly verifiable by grep. Keyword coverage looks correct (8+ keywords per tool), but actual discovery ranking depends on the full index of all 155 tools.

### Gaps Summary

No gaps found. All 14 observable truths verified, all 15 artifacts present and substantive, all 10 key links wired. 1,754 tests pass at 96.56% coverage (requirement: 95%). Production code passes pyright with 0 errors.

The REQUIREMENTS.md traceability rows retain "Planned" status rather than "Complete" — this is a cosmetic documentation issue that does not affect phase goal achievement.

---

_Verified: 2026-04-09T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
