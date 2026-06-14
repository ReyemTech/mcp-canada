---
phase: 18-manitoba-government-open-data
verified: 2026-06-14T00:00:00Z
status: passed
score: 18/18 must-haves verified
---

# Phase 18: Manitoba Government Open Data — Verification Report

**Phase Goal:** Add Manitoba's provincial open data surface to mcp-canada as a new `manitoba` module wrapping the geoportal.gov.mb.ca ArcGIS Hub (org mMUesHYPkXjaFGfS) — 5 discovery tools + curated FeatureServer tools across flood/hydrology, agriculture/drought, transport (conditional on 511 key), regional health, and environment/parks, plus 6 bilingual prompts + 7 zero-parameter resources, all discoverable via discover_tools and ≥95% test coverage.
**Verified:** 2026-06-14
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Manitoba module auto-registers via FileSystemProvider | VERIFIED | `MODULE_NAME = "manitoba"`, `MODULE_DESCRIPTION` + `MODULE_DESCRIPTION_FR` in `__init__.py` |
| 2 | ArcGIS Hub pattern used (org mMUesHYPkXjaFGfS); no data.manitoba.ca / mli.gov.mb.ca calls | VERIFIED | All references to those URLs are doc warnings ("NEVER reference"), not live calls |
| 3 | 20 @tool functions exist with correct conventions | VERIFIED | AST scan: 20 tools, all with `@tool` from `fastmcp.tools`, `lang` param, `Use for:`, 8+ Keywords |
| 4 | 511 tools return NOT_CONFIGURED when key absent (not exceptions) | VERIFIED | `except Five11NotConfigured` → `make_error("NOT_CONFIGURED", ...)` in all 3 transport tools |
| 5 | Manitoba Hydro/energy NOT implemented; drought + ag weather substituted | VERIFIED | No Hydro energy tools; `fetch_drought_status` + `fetch_ag_weather_stations` in client |
| 6 | 6 bilingual @prompt functions exist (3 guided + 3 quick-lookup) | VERIFIED | AST scan: 6 prompts with standalone `@prompt`, all with `lang` param |
| 7 | 7 zero-parameter @resource functions exist with data://, docs://, template:// URIs | VERIFIED | AST scan: 7 resources, zero params each, URIs correct |
| 8 | Integration tests call tools through MCP Client layer | VERIFIED | `TestManitobaToolScenarios` in `test_tool_scenarios.py` uses `call_tool()` via MCP server |
| 9 | Coverage ≥95% | VERIFIED | 96.75% — `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q` passed |
| 10 | README/CLAUDE/MODULES docs synced | VERIFIED | README: 237 tools (217+20), Manitoba row in module table, ArcGIS Hub row updated in CLAUDE.md |
| 11 | Wave 0 spike resolved 4 open questions | VERIFIED | 18-SPIKE.md present with all 4 findings: 511 GATED, Rural Health RESOLVED, Hog UNRESOLVED, River CSV |
| 12 | River conditions uses CSV feed (not FeatureServer) | VERIFIED | `RIVER_CONDITIONS_CSV_URL` constant; `fetch_and_parse` used in `fetch_river_stations` |
| 13 | Hog prices gracefully degrades when URL is None | VERIFIED | `HOG_PRICES_FS_URL = None`; `fetch_livestock_prices` returns empty with note, not exception |
| 14 | 511 functions use `_511_get` (NOT arcgis_hub) | VERIFIED | `fetch_road_events/winter_road_conditions/traffic_cameras` all call `await _511_get(...)` |
| 15 | _hub_get uses Hub JSON contract (never CKAN .get("success")) | VERIFIED | `_hub_get` checks `isinstance(result, dict)` and returns directly — no CKAN key access |
| 16 | `TestManitobaEnvelopes` + `TestManitobaLangParam` parametrized over all 20 tools | VERIFIED | `ALL_MANITOBA_TOOLS` list has 20 entries; assertion `len == 20` at module level |
| 17 | Unit suite passes completely | VERIFIED | 232 tests in `src/mcp_canada/modules/manitoba/__tests__/` — 232 passed, 0 failed |
| 18 | All MB-01…MB-18 requirements covered | VERIFIED | See Requirements Coverage table below |

**Score:** 18/18 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/modules/manitoba/__init__.py` | MODULE_NAME + bilingual descriptions | VERIFIED | `MODULE_NAME = "manitoba"`, FR description present |
| `src/mcp_canada/modules/manitoba/constants.py` | All FeatureServer URLs, org id, rate groups, TTLs | VERIFIED | `ARCGIS_ORG_ID = "mMUesHYPkXjaFGfS"`, `MAX_RECORDS = 5000`, `CACHE_KEY_PREFIX = "manitoba:"`, all URLs |
| `src/mcp_canada/modules/manitoba/schemas.py` | ~18 flat Pydantic v2 models | VERIFIED | All 18 models importable via `client.py` re-export |
| `src/mcp_canada/modules/manitoba/client.py` | `_hub_get`, `_511_get`, `Five11NotConfigured`, 18 client functions | VERIFIED | 39KB file, all functions implemented (no NotImplementedError stubs remaining) |
| `src/mcp_canada/modules/manitoba/tools.py` | 20 @tool functions | VERIFIED | 20 tools, all with `@tool`, `lang`, `make_response`/`make_error`, `manitoba_` prefix |
| `src/mcp_canada/modules/manitoba/prompts.py` | 6 @prompt functions | VERIFIED | 3 guided (list[Message]) + 3 quick-lookup (str), bilingual |
| `src/mcp_canada/modules/manitoba/resources.py` | 7 zero-parameter @resource functions | VERIFIED | 7 resources with correct type-prefixed URIs, zero params each |
| `src/mcp_canada/modules/manitoba/__tests__/conftest.py` | Fixtures for all response shapes | VERIFIED | 15KB conftest with ArcGIS Hub, flood-alert-empty, 511 fixtures |
| `src/mcp_canada/modules/manitoba/__tests__/test_client.py` | 19 test classes | VERIFIED | 19 classes including `TestSharedApiGetContract`, `TestManitoba511` |
| `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` | 22 test classes | VERIFIED | 20 per-tool classes + `TestManitobaEnvelopes` + `TestManitobaLangParam` |
| `src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py` | TestManitobaPrompts + TestManitobaResources | VERIFIED | Both classes present |
| `tests/integration/test_tool_scenarios.py` | TestManitobaToolScenarios | VERIFIED | 7 scenarios: flood-empty, parks, wait-times, drought, BM25 discovery, invalid-f_type, 511-NOT_CONFIGURED |
| `tests/integration/test_prompts_resources_scenarios.py` | TestManitobaPromptsResources | VERIFIED | Class present |
| `.planning/phases/18-manitoba-government-open-data/18-SPIKE.md` | Spike findings | VERIFIED | 4 questions resolved: 511 GATED, Rural Health RESOLVED, Hog UNRESOLVED, River CSV |
| `docs/modules/manitoba.md` | Manitoba module docs | VERIFIED | 7.1KB file, 20 tools listed |
| `README.md` | Manitoba section + count 237 | VERIFIED | Manitoba row in table (20 tools), header count = 237 |
| `CLAUDE.md` | Manitoba in ArcGIS Hub table row | VERIFIED | ArcGIS Hub row explicitly names Phase 18: Manitoba with org id |
| `EXAMPLES.md` | Manitoba cross-module example | VERIFIED | Example 25: Manitoba Surgical Wait Times + StatCan Population |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `__init__.py` | FileSystemProvider | `MODULE_NAME = "manitoba"` export | VERIFIED | Auto-discovery confirmed |
| `client.py` | `shared.http.api_get` | `from mcp_canada.shared.http import api_get` | VERIFIED | Import present; `_hub_get` wraps it |
| `client.py` | `shared.arcgis_hub` | `from mcp_canada.shared import arcgis_hub` | VERIFIED | All curated FeatureServer clients use `arcgis_hub.query_feature_service` |
| `client.py` | `shared.parsers.fetch_and_parse` | `from mcp_canada.shared.parsers import fetch_and_parse` | VERIFIED | Used in `fetch_river_stations` (CSV) and `fetch_query_dataset` auto-router |
| `client.py` | `shared.cache.cached_fetch` | `from mcp_canada.shared.cache import cached_fetch` | VERIFIED | Every client function wraps network call in `cached_fetch` |
| `tools.py` | `client` | `from . import client as _client` | VERIFIED | All 20 tools call `_client.fetch_*` |
| `tools.py` | `Five11NotConfigured` | `except Five11NotConfigured` catch in 3 transport tools | VERIFIED | Maps to `make_error("NOT_CONFIGURED", ...)` |
| 511 client fns | `_511_get` (not arcgis_hub) | `await _511_get("events/winterroads/cameras")` | VERIFIED | No `arcgis_hub` call inside any `fetch_road_events/winter_road_conditions/traffic_cameras` |
| Integration tests | MCP Client | `call_tool(mcp_server, "manitoba_*", {...})` | VERIFIED | 7 scenarios via `mcp_server` fixture with BM25SearchTransform |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| MB-01 | 18-02 | Search Hub by keyword/category/pagination | VERIFIED | `manitoba_search_datasets` in tools.py |
| MB-02 | 18-02 | Get dataset details (FeatureServer URL, download URLs) | VERIFIED | `manitoba_get_dataset_details` in tools.py |
| MB-03 | 18-02 | Auto-router (FeatureServer → arcgis_hub; CSV → fetch_and_parse; other → metadata) | VERIFIED | `fetch_query_dataset` with 3-branch router; `manitoba_query_dataset` |
| MB-04 | 18-02 | List publishing organizations | VERIFIED | `manitoba_list_organizations` |
| MB-05 | 18-02 | List dataset categories/tags | VERIFIED | `manitoba_list_categories` |
| MB-06 | 18-05 | Provincial parks (93, bilingual, park_type filter) | VERIFIED | `manitoba_get_provincial_parks`; `PROVINCIAL_PARKS_FS_URL` |
| MB-07 | 18-03 | Flood alerts (bilingual, empty = normal) | VERIFIED | `manitoba_get_flood_alerts`; empty-features test present |
| MB-08 | 18-03 | River station locations + flood status (CSV, not FeatureServer per spike) | VERIFIED | `fetch_river_stations` uses `fetch_and_parse(RIVER_CONDITIONS_CSV_URL)` |
| MB-09 | 18-03 | Provincial waterways (dike/floodway/dam, f_type filter) | VERIFIED | `manitoba_get_provincial_waterways`; INVALID_INPUT on bad f_type |
| MB-10 | 18-04 | Drought monitor D0-D4 with Manitoba bbox filter | VERIFIED | `manitoba_get_drought_status`; `MANITOBA_BBOX` in client |
| MB-11 | 18-04 | Ag weather stations (100+, AgRegion filter, URL per station) | VERIFIED | `manitoba_get_ag_weather_stations`; `AG_WEATHER_STATIONS_FS_URL` |
| MB-12 | 18-04 | Livestock prices (cattle/hog dispatch) | VERIFIED | `manitoba_get_livestock_prices`; hog degrades gracefully (HOG_PRICES_FS_URL=None) |
| MB-13 | 18-04 | Crop regions (bilingual REGION/RÉGION) | VERIFIED | `manitoba_get_crop_regions`; bilingual field names in out_fields |
| MB-14 | 18-05 | Surgical wait times (by procedure/year) | VERIFIED | `manitoba_get_surgical_wait_times`; `SURGICAL_WAIT_TIMES_FS_URL` |
| MB-15 | 18-05 | Fisheries waterbody data (350+, species/regs) | VERIFIED | `manitoba_get_fisheries_data`; focused field subset |
| MB-16 | 18-05 | Provincial forests + rural health facilities (RHA filter) | VERIFIED | `manitoba_get_provincial_forests` + `manitoba_get_health_facilities` |
| MB-17 | 18-06 | Transport 511 (road events, winter roads, cameras; NOT_CONFIGURED when key absent) | VERIFIED | 3 tools ship; `Five11NotConfigured` → NOT_CONFIGURED in every tool |
| MB-18 | 18-01, 18-08 | Conventions + discover_tools + 6 prompts + 7 resources + ≥95% coverage | VERIFIED | 232 unit tests passed; 96.75% coverage; parametrized envelope/lang tests over all 20 |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tools.py` | 37 | `PARK_TYPES` imported but unused (ruff F401) | Info | No runtime impact; fixable lint warning |
| `__tests__/test_client.py` | 17, 1248, 1260, 1272 | `Five11NotConfigured` imported at module level + re-imported inside test methods (ruff F811) | Info | No impact; tests pass |
| `__tests__/test_client.py` | 56, 546 | Local variables assigned but unused (ruff F841) | Info | No impact; tests pass |
| `prompts.py` | 20 | pyright `reportMissingImports` for `fastmcp.prompts.prompt` | Info | Type stub only — runtime import succeeds; all tests pass |

No blocker anti-patterns found. All issues are lint-only and do not affect runtime or test correctness.

---

### Human Verification Required

The following items require human or live-network verification not possible from static analysis:

1. **Live ArcGIS Hub API responses**
   - Test: Run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "Manitoba"`
   - Expected: `test_flood_alerts_empty_is_success`, `test_provincial_parks`, `test_surgical_wait_times_for_cardiac`, `test_drought_status`, `test_discover_flood_alerts_via_bm25`, `test_invalid_f_type_returns_structured_error` pass against live `geoportal.gov.mb.ca`
   - Why human: Live API; connectivity varies; `test_511_not_configured_without_key` always passes (no key required)

2. **Hog prices resolution**
   - Test: Run the re-probe command in `18-SPIKE.md §3` against AgriMaps
   - Expected: Either confirm hog prices are within MB_Cattle_Prices_Current_year, or find the separate service on AgriMaps
   - Why human: Unresolved spike item; requires live API probe; current implementation degrades gracefully

---

### Gaps Summary

No gaps blocking goal achievement. The phase delivered all 18 observable truths. Minor notes:

- **Hog prices FS unresolved (expected):** `HOG_PRICES_FS_URL = None` is a documented spike finding, not a regression. `Manitoba_get_livestock_prices(livestock="hog")` returns an empty result with an explanatory note rather than failing. This matches the plan's "degrade gracefully" requirement.
- **MB-08 scope adjustment:** The requirement mentioned "FeatureServer" for river conditions, but the Wave 0 spike proved river data is published as CSV (no FeatureServer backing). The implementation correctly adapted to use `fetch_and_parse(RIVER_CONDITIONS_CSV_URL)`. This is the correct behaviour per the spike, not a deviation.
- **Ruff/pyright minor warnings:** 7 ruff issues (F401, F811, F841) in test files and tools.py. All are fixable with `ruff --fix` and have zero runtime impact. Coverage is 96.75%.

---

_Verified: 2026-06-14_
_Verifier: Claude (gsd-verifier)_
