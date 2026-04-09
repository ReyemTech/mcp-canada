---
phase: 13-toronto-municipal-government-open-data
verified: 2026-04-09T17:08:49Z
status: passed
score: 20/20 must-haves verified
re_verification: false
---

# Phase 13: Toronto Municipal Government Open Data — Verification Report

**Phase Goal:** Add Toronto's municipal open data catalogue to mcp-canada with CKAN discovery tools and curated high-value dataset tools for transit, neighbourhoods, 311 requests, housing, and budget data. Also extend shared parsers with GeoJSON and JSON support.
**Verified:** 2026-04-09T17:08:49Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GeoJSON FeatureCollection bytes parse into list of property dicts with optional geometry | VERIFIED | `_parse_geojson` in parsers.py L429-453; verified behavior in-process |
| 2 | JSON bytes parse into list[dict] handling arrays, objects, and FeatureCollection roots | VERIFIED | `_parse_json` in parsers.py L456-475; verified behavior in-process |
| 3 | fetch_and_parse routes .geojson and .json URLs to the new parsers | VERIFIED | parsers.py L518-521 — `.geojson` check before `.json` as required |
| 4 | Toronto CKAN search returns shaped dataset summaries with bilingual title/description | VERIFIED | `fetch_search_datasets` in client.py L141-173; calls `_shape_dataset` |
| 5 | GTFS ZIP stops.txt and routes.txt parse from in-memory ZIP into list[dict] | VERIFIED | `fetch_gtfs_file` in client.py L249-281; uses stdlib zipfile + BytesIO + 120s timeout |
| 6 | 311 annual ZIP CSV parses and filters by ward/service_type/status client-side | VERIFIED | `fetch_311_requests` in client.py L433-527; discovers ZIP URL, client-side filtering |
| 7 | Neighbourhood datastore_search returns records filtered by Characteristic | VERIFIED | `fetch_neighbourhood_profile` in client.py L375-401; calls fetch_datastore_records with q=characteristic |
| 8 | RentSafeTO and short-term rentals datastore_search returns filtered records | VERIFIED | `fetch_rentsafe_evaluations` L535-571, `fetch_short_term_rentals` L574-609 in client.py |
| 9 | Agent can search Toronto open data catalogue by keyword and get shaped results | VERIFIED | `toronto_search_datasets` tool in tools.py L47-82 |
| 10 | Agent can get full dataset details including resources with datastore_active flag | VERIFIED | `toronto_get_dataset_details` tool L91-116; `_shape_resource` includes datastore_active flag |
| 11 | Agent can search TTC stops by name and get structured stop data | VERIFIED | `toronto_get_ttc_stops` tool L229-253 |
| 12 | Agent can search TTC routes and filter by route type | VERIFIED | `toronto_get_ttc_routes` tool L262-286 |
| 13 | Agent can get neighbourhood census indicators for a single neighbourhood | VERIFIED | `toronto_get_neighbourhood_profile` tool L295-328 |
| 14 | Agent can compare a single indicator across all 140 neighbourhoods | VERIFIED | `toronto_compare_neighbourhoods` tool L337-365 |
| 15 | Agent can fetch 311 service requests filtered by year, ward, type, status | VERIFIED | `toronto_get_311_requests` tool L374-417 |
| 16 | Agent can query RentSafeTO apartment evaluations by ward and minimum score | VERIFIED | `toronto_get_rentsafe_evaluations` tool L426-456 |
| 17 | Agent can query short-term rental registrations by ward and status | VERIFIED | `toronto_get_short_term_rentals` tool L465-495 |
| 18 | All toronto_ tools are discoverable via discover_tools | VERIFIED | TestTorontoToolScenarios.test_toronto_discovery in integration tests; MODULE_NAME = "toronto" for FileSystemProvider auto-discovery |
| 19 | All toronto_ tools have valid Keywords/Use-for docstrings | VERIFIED | tests/test_quality.py passes (5/5); all 12 tools inspected — each has "Use for:" and "Keywords:" single lines |
| 20 | README lists all toronto_ tools with accurate descriptions | VERIFIED | README.md L423-451: Toronto section with 5 discovery + 7 curated tools; header shows 128 tools |

**Score:** 20/20 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/shared/parsers.py` | _parse_geojson and _parse_json + routing in fetch_and_parse | VERIFIED | Both functions present at L429, L456; routing at L518-521 |
| `src/mcp_canada/modules/toronto/__init__.py` | MODULE_NAME and MODULE_DESCRIPTION for auto-registration | VERIFIED | MODULE_NAME = "toronto"; 377-char description |
| `src/mcp_canada/modules/toronto/constants.py` | BASE_URL, RATE_GROUP, cache TTLs, curated dataset/resource IDs | VERIFIED | All curated IDs present: GTFS_DATASET_ID, NEIGHBOURHOOD_PROFILES_RESOURCE_ID, SERVICE_REQUESTS_DATASET_ID, RENTSAFE_EVAL_RESOURCE_ID, SHORT_TERM_RENTALS_RESOURCE_ID |
| `src/mcp_canada/modules/toronto/schemas.py` | Flat Pydantic v2 models | VERIFIED | GTFSStop and GTFSRoute models present |
| `src/mcp_canada/modules/toronto/client.py` | All async client functions returning (data, was_cached) tuples | VERIFIED | 12 public async functions; all return (data, bool) tuples |
| `src/mcp_canada/modules/toronto/__tests__/test_client.py` | Unit tests for all client functions | VERIFIED | 13 test classes; 116 passed, 2 skipped in test run |
| `src/mcp_canada/modules/toronto/tools.py` | 12 @tool functions with toronto_ prefix | VERIFIED | Exactly 12 toronto_ tools confirmed by grep |
| `src/mcp_canada/modules/toronto/__tests__/test_tools.py` | Unit tests for all 12 tools | VERIFIED | 12 test classes, one per tool |
| `tests/integration/test_tool_scenarios.py` | TestTorontoToolScenarios integration tests | VERIFIED | Class at line 504; 8 test methods |
| `README.md` | Toronto section in tool catalog + updated tool count | VERIFIED | Section at L421-451; count 128 tools includes Toronto's 12 |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `toronto/client.py` | `shared/cache.py` | `from mcp_canada.shared.cache import cached_fetch` | WIRED | Import at client.py L36; used in `_api_get`, `fetch_gtfs_file`, `fetch_311_requests` |
| `toronto/client.py` | `shared/rate_limiter.py` | `get_limiter` | WIRED | Import at client.py L38; used in `_api_get`, `fetch_gtfs_file`, `fetch_311_requests` |
| `shared/parsers.py` | fetch_and_parse routing | `.geojson and .json URL suffix detection` | WIRED | L518-521: `.geojson` check precedes `.json`; both call correct parsers |
| `toronto/tools.py` | `toronto/client.py` | `from mcp_canada.modules.toronto.client import` | WIRED | Import at tools.py L20-33; all 12 client functions imported and used |
| `toronto/tools.py` | `shared/envelope.py` | `make_response` and `make_error` | WIRED | Import at tools.py L34; used in every tool's return paths |
| `tests/integration/test_tool_scenarios.py` | MCP Client layer | `call_tool('call_tool', ...)` | WIRED | 7 direct `call_tool` invocations targeting toronto_ tools (L517-577) |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| TOR-01 | 13-01-PLAN | Shared parsers support GeoJSON FeatureCollection parsing with optional geometry | SATISFIED | `_parse_geojson` L429-453; include_geometry param; verified behavior |
| TOR-02 | 13-01-PLAN | Shared parsers support JSON array/object parsing with GeoJSON auto-detection | SATISFIED | `_parse_json` L456-475; routes to `_parse_geojson` on "features" key |
| TOR-03 | 13-01-PLAN, 13-02-PLAN | Agent can search Toronto Open Data Catalogue by keyword with pagination | SATISFIED | `toronto_search_datasets` tool; fetch_search_datasets with rows/start/sort params |
| TOR-04 | 13-01-PLAN, 13-02-PLAN | Agent can get full details for a Toronto dataset including resources with datastore_active flag | SATISFIED | `toronto_get_dataset_details`; `_shape_resource` includes datastore_active |
| TOR-05 | 13-01-PLAN, 13-02-PLAN | Agent can search TTC stops by name from GTFS ZIP data | SATISFIED | `toronto_get_ttc_stops`; `fetch_gtfs_stops` with stop_name substring filter |
| TOR-06 | 13-01-PLAN, 13-02-PLAN | Agent can search TTC routes by type from GTFS ZIP data | SATISFIED | `toronto_get_ttc_routes`; `fetch_gtfs_routes` with route_type filter |
| TOR-07 | 13-01-PLAN, 13-02-PLAN | Agent can get neighbourhood census profile indicators (2016 140-neighbourhood model via CKAN datastore) | SATISFIED | `toronto_get_neighbourhood_profile`; uses NEIGHBOURHOOD_PROFILES_RESOURCE_ID |
| TOR-08 | 13-01-PLAN, 13-02-PLAN | Agent can compare a single census indicator across all 140 neighbourhoods | SATISFIED | `toronto_compare_neighbourhoods`; `fetch_neighbourhood_comparison` |
| TOR-09 | 13-01-PLAN, 13-02-PLAN | Agent can fetch 311 service requests filtered by year, ward, service type, and status | SATISFIED | `toronto_get_311_requests`; `fetch_311_requests` with all four filters |
| TOR-10 | 13-01-PLAN, 13-02-PLAN | Agent can query RentSafeTO apartment building evaluations by ward and minimum score | SATISFIED | `toronto_get_rentsafe_evaluations`; min_score client-side filter in `_safe_int` |
| TOR-11 | 13-01-PLAN, 13-02-PLAN | Agent can query short-term rental registrations by ward and status | SATISFIED | `toronto_get_short_term_rentals`; `fetch_short_term_rentals` with ward/status |
| TOR-12 | 13-02-PLAN | All Toronto tools follow mcp-canada conventions (standalone @tool, make_response/make_error, Keywords/Use-for, toronto_ prefix, discoverable) | SATISFIED | Standalone @tool used; all 12 tools return make_response/make_error; test_quality.py passes; MODULE_NAME = "toronto" |

**No orphaned requirements.** All 12 TOR requirement IDs are claimed by Plan 01 or 02 and have implementation evidence.

---

### Anti-Patterns Found

No anti-patterns detected. Scanned `tools.py` and `client.py` for:
- TODO/FIXME/placeholder comments: none
- Empty implementations (return null / return {} / return []): none
- Stub handlers (only console.log or e.preventDefault): not applicable (Python)
- API routes returning static data without DB/external queries: none

---

### Human Verification Required

#### 1. Live GTFS ZIP download

**Test:** Call `toronto_get_ttc_stops` with `query="King"` via the running MCP server.
**Expected:** Returns list of stops whose names contain "King" with stop_id, stop_lat, stop_lon. First call may take up to 60s (35.9 MB ZIP download).
**Why human:** GTFS ZIP is 35.9 MB; automated tests use in-memory fixtures. Live download path not covered by unit tests.

#### 2. Live 311 ZIP+CSV parsing

**Test:** Call `toronto_get_311_requests` with `year=2023, limit=5`.
**Expected:** Returns list of service request dicts with _meta envelope. First call may be slow.
**Why human:** Integration test skips the 311 tool (no integration test for `toronto_get_311_requests`). The year-detection logic (resource name/URL matching) is only unit-tested with fixtures.

#### 3. Neighbourhood profile data structure

**Test:** Call `toronto_get_neighbourhood_profile` with `characteristic="Population"`.
**Expected:** Returns rows where "Characteristic" column contains "Population", with 140+ neighbourhood columns as dict values.
**Why human:** The 2016 profile resource uses an unusual indicator-per-row transpose model. Live data shape (column names for 140 neighbourhoods) cannot be confirmed from unit tests alone.

---

### Gaps Summary

No gaps found. All 20 must-have truths are verified, all 10 required artifacts exist and are substantive and wired, all 6 key links confirmed, and all 12 TOR requirements are satisfied with implementation evidence.

Test suite results: 116 unit tests passed (2 skipped) across toronto module + parsers; 5/5 quality docstring checks passed; coverage at 95.72% (above 95% threshold); pyright: 0 errors; ruff: all checks passed.

---

_Verified: 2026-04-09T17:08:49Z_
_Verifier: Claude (gsd-verifier)_
