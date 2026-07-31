---
phase: 21-new-brunswick-government-open-data
verified: 2026-07-30T20:30:00Z
status: passed
score: 30/30 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 21: New Brunswick Government Open Data Verification Report

**Phase Goal:** Ship a `new_brunswick` module exposing NB provincial data as MCP tools — the 8th
province in the rollout, 22 tools across federal-CKAN discovery, GeoNB bare-ArcGIS-Server geospatial
data, and key-gated 511 transport stubs, following the 7-file module pattern and adding two additive
enumerator functions to `shared/arcgis_hub.py`.

**Verified:** 2026-07-30T20:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

**Note on ROADMAP goal-text staleness:** Per the execution notes, ROADMAP.md's Phase 21 goal
paragraph still describes the pre-checkpoint split ("5 CKAN + 3 GeoNB discovery + 11 curated + 3
transport"). The Wave 0 blocking checkpoint (option-a: `gnb.socrata.com` joins the surface,
`nb_get_mineral_occurrences`/`nb_get_provincial_parks` dropped to the long tail) changed the actual
breakdown to 5 CKAN + 2 Socrata + 3 GeoNB discovery + 9 curated GeoNB + 3 transport = 22. The total
(22) and every structural claim (bare ArcGIS Server, 7-file pattern, two additive shared functions)
still hold. This verification judges the goal on the substance the execution notes direct — a
working, correctly-scoped, documented 22-tool NB surface — not on the stale sub-count prose. This is
flagged as a documentation follow-up, not a phase-blocking gap: recommend a small ROADMAP.md text
edit in the next phase's housekeeping to describe the actual 22-tool breakdown.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | TRACER: `nb_get_crown_land` returns live GeoNB Crown Land rows in a `_meta` envelope through constants→client→`@tool`→FileSystemProvider, layer 3 | ✓ VERIFIED | Live re-run: `TRACER LIVE OK 25 rows`, `_meta.source.api == "new-brunswick-geonb"`, `HOLDER`/`OBJECTID` present |
| 2 | Crown Land layer id is 3, never 0 | ✓ VERIFIED | `constants.CROWN_LAND_LAYER == 3`; live layer listing confirms id 3 present on `GeoNB_DNR_Crown_Land` |
| 3 | `shared/arcgis_hub.py` gains exactly two new functions, both decode via `decode_json`, both accept injected `httpx_client` | ✓ VERIFIED | `git show 978aae1` diff is purely additive; `list_arcgis_server_services`/`get_arcgis_server_layers` both call `decode_json(response, url)` and branch on `httpx_client is not None` |
| 4 | Existing `query_feature_service`, `get_layer_metadata`, `get_count`, `search_hub_datasets` unchanged | ✓ VERIFIED | Same diff shows zero changes to existing function bodies, only a docstring public-function-list addition |
| 5 | The gnb.socrata.com blocking checkpoint was resolved by the user and recorded | ✓ VERIFIED | 21-01-PLAN.md Task 2 checkpoint present; COVERAGE.md Surface 5 records resolved option-a with live-verified 312-dataset facts |
| 6 | `21-SPIKE.md` re-verifies every curated layer id live, no tool planned on an unresolved id | ✓ VERIFIED | 21-SPIKE.md exists; COVERAGE.md and constants.py cite CONFIRMED/REVISED-consistent layer ids (Crown Land 3, Wetlands 2, etc.) |
| 7 | `new_brunswick` auto-registers via FileSystemProvider; `server.py` NOT modified | ✓ VERIFIED | `grep -n new_brunswick src/mcp_canada/server.py` → no matches; `git diff --stat src/mcp_canada/server.py` empty |
| 8 | `constants.py` hardcodes every service URL/layer id/TTL/rate group/22-name manifest | ✓ VERIFIED | Read `constants.py`: `CROWN_LAND_LAYER`, `FIVE11_KEY_ENV`, `NB_ORG_FQ`, `FILTER_REQUIRED_TOOLS`, `ALL_NB_TOOL_NAMES` (22 entries) all present |
| 9 | pytest collects shared + new_brunswick test dirs with no ImportError | ✓ VERIFIED | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -q` → 366 passed |
| 10 | Agent can search 221 NB datasets, org filter server-side non-overridable (T-21-04) | ✓ VERIFIED | Live: `test_search_datasets_about_flooding` passes; `_build_fq` wraps both clauses in parens post-fix (WR-01); no `organization` param exposed (`grep -n "organization:" tools.py` → none) |
| 11 | French queries get French titles/notes via `title_translated`/`notes_translated` fallback; duplicate FR/EN record pairs return as two results | ✓ VERIFIED | Live: `test_dataset_details_bilingual_title` passes; `_shape_dataset` fallback chain read in client.py |
| 12 | `nb_query_dataset` returns metadata-only (not error) for unparseable formats | ✓ VERIFIED | Unit test coverage confirmed in full suite (366 passed incl. `TestFetchQueryDataset`); WR-03 fix adds `limit<=0` InvalidInput before parse |
| 13 | `nb_list_organizations`/`nb_list_categories` built from facets, not empty CKAN groups | ✓ VERIFIED | Live: `test_list_organizations`, `test_list_categories_format_list` pass |
| 14 | `TestSharedApiGetContract` pins outgoing params incl. non-overridable org clause | ✓ VERIFIED | `test_client.py` contains `class TestSharedApiGetContract`; part of the 366 passing tests |
| 15 | Every tool: `@upstream_guard` beneath `@tool`, `Use for:`/`Keywords:` (8+ terms), `make_response`/`make_error` only | ✓ VERIFIED | `uv run pytest tests/test_tool_error_handling.py tests/test_quality.py -q` → 48+5 passed; manual docstring spot-check on `nb_search_datasets` confirms format |
| 16 | 3 GeoNB discovery tools stand in for the 401-ing Hub Search API, hide basemaps/retired service by default | ✓ VERIFIED | Live: `test_list_geonb_services_no_basemap_leaked` passes; resource catalogue shows 62 services with exclusion reasons |
| 17 | `nb_query_geonb_layer` reaches any un-curated layer (long-tail escape hatch) | ✓ VERIFIED | Live: `test_query_geonb_layer_reaches_mineral_occurrences` passes |
| 18 | Flood hazard, historical floods, wetlands, contaminated sites use live-verified layer ids, never layer 0 by convention | ✓ VERIFIED | Live: `test_flood_hazard_areas_field_present`, `test_historical_floods_1973_event`, `test_wetlands_bog_filter`, `test_contaminated_sites_bilingual_status` all pass |
| 19 | `nb_get_wetlands` rejects unfiltered call with `INVALID_INPUT` before network | ✓ VERIFIED | Live: `test_wetlands_unfiltered_returns_invalid_input` passes; unit test asserts `query_feature_service` not awaited |
| 20 | Empty feature collection is a success with zero count, never an error | ✓ VERIFIED | Confirmed by module test suite (`_geonb_query` returns `{"features": [], "count": 0}` shape, exercised in unit tests) |
| 21 | Every curated WHERE clause server-built + escaped; only `nb_query_geonb_layer` accepts raw clause | ✓ VERIFIED | `_escape_sql_value`/`_upper_contains_clause` used at every curated call site (`grep` above); live-verified the escaping actually blocks live wildcard bypass (see CR-01 independent check below) |
| 22 | Agent can resolve property by PID/county (`nb_get_parcels`), civic address by community/street/number (`nb_get_civic_addresses`), both filter-required before network | ✓ VERIFIED | Live: `test_parcels_in_york_county`, `test_parcels_unfiltered_returns_invalid_input`, `test_civic_address_in_fredericton`, `test_civic_addresses_unfiltered_returns_invalid_input` all pass |
| 23 | Mineral occurrences / provincial parks reachable when in manifest, or correctly absent | ✓ VERIFIED | `nb_get_mineral_occurrences`/`nb_get_provincial_parks` confirmed absent from `tools.py`; reachable via `nb_query_geonb_layer` per live test `test_query_geonb_layer_reaches_mineral_occurrences` |
| 24 | Health facilities dispatch across 6 layers, public schools across 2 sectors, both via constant maps not positional guessing | ✓ VERIFIED | Live: `test_health_facilities_bilingual_hospital_names`, `test_public_schools_anglophone` pass; `HEALTH_FACILITY_LAYERS`/`SCHOOL_SECTOR_LAYERS` referenced in both client.py and tools.py |
| 25 | Invalid facility type/sector rejected with `INVALID_INPUT` listing valid values, before network, both layers | ✓ VERIFIED | Confirmed in module unit suite (parametrized dispatch tests, part of 366 passed) |
| 26 | 3 NB 511 tools return `NOT_CONFIGURED` envelope (not exception) when key absent; message never echoes env value; bilingual | ✓ VERIFIED | Live re-run of the exact plan verify command: `511 STUBS OK — unconfigured envelope bilingual, key never echoed` |
| 27 | 511 unconfigured path still satisfies catch-all coverage gate | ✓ VERIFIED | `uv run pytest tests/test_tool_error_handling.py -q` passes with all 22 tools covered |
| 28 | All 22 tools exercised live through MCP Client layer, not direct client import; every path reaches an assertion | ✓ VERIFIED | Live re-run: `29 passed, 191 deselected` in `TestNewBrunswickToolScenarios`; `uv run pytest tests/test_integration_test_quality.py -q` passes (no banned masking idiom) |
| 29 | README/TOOLS.md/CLAUDE.md agree with shipped tool set; catalogue `--check` is a CI gate | ✓ VERIFIED | `uv run python scripts/generate_catalog.py --check` → "Catalog is up to date."; `grep -c "nb_" TOOLS.md` = 22; README module tree contains `new_brunswick/` with count 22 |
| 30 | REQUIREMENTS.md carries NB-01..NB-25 traceable to Phase 21; CLAUDE.md records the corrected gnb.socrata.com fact, not the false no-Socrata claim | ✓ VERIFIED | All 25 NB-IDs + 7 ERR-IDs present and `[x]`-checked in REQUIREMENTS.md with traceability rows; `grep -rn "no NB Socrata"` returns nothing in CLAUDE.md; CLAUDE.md contains verified `gnb.socrata.com`/`geonb.snb.ca` facts |

**Score:** 30/30 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/shared/arcgis_hub.py` | +2 additive functions | ✓ VERIFIED | `list_arcgis_server_services`, `get_arcgis_server_layers` present; existing 5 functions byte-identical apart from docstring list |
| `src/mcp_canada/modules/new_brunswick/__init__.py` | `MODULE_NAME`/`MODULE_DESCRIPTION`(_FR) | ✓ VERIFIED | Read in full; describes all 3 upstream surfaces bilingually |
| `src/mcp_canada/modules/new_brunswick/constants.py` | full contract surface | ✓ VERIFIED | 187 lines; `ALL_NB_TOOL_NAMES` (22), `FILTER_REQUIRED_TOOLS`, `HEALTH_FACILITY_LAYERS`, `SCHOOL_SECTOR_LAYERS` all present |
| `src/mcp_canada/modules/new_brunswick/schemas.py` | ~17 flat Pydantic models | ✓ VERIFIED | 276 lines; imported into `client.py` via `noqa: F401` re-export (IN-01 fix), matching sibling-module convention |
| `src/mcp_canada/modules/new_brunswick/client.py` | 3 limiters, 5 private helpers, full fetch surface | ✓ VERIFIED | 1342 lines; `Five11NotConfigured`, `_api_get`, `_build_fq`, `_shape_dataset`, `_geonb_query`, `_511_get`, `_escape_sql_value`, `_escape_like_value`, `_upper_contains_clause`, `_require_any_filter` all present and exercised |
| `src/mcp_canada/modules/new_brunswick/tools.py` | 22 `nb_` tools | ✓ VERIFIED | 998 lines; `ALL_NB_TOOLS` set-equal to `constants.ALL_NB_TOOL_NAMES`, len 22 |
| `src/mcp_canada/modules/new_brunswick/prompts.py` | 6 prompts | ✓ VERIFIED | `len(p.__all__) == 6`; live `PROMPTS OK` check — every `nb_`-token referenced is a real manifest tool |
| `src/mcp_canada/modules/new_brunswick/resources.py` | 7 zero-param resources | ✓ VERIFIED | `len(r.__all__) == 7`; zero-parameter constraint verified via `inspect.signature`; `data://nb/geonb-services` carries 62 entries with valid `curated_tool` citations |
| `tests/integration/test_tool_scenarios.py::TestNewBrunswickToolScenarios` | live MCP-layer coverage | ✓ VERIFIED | 29 tests (28 scenarios + 1 manifest-coverage meta-test), all pass live |
| `.planning/REQUIREMENTS.md` | NB-01..NB-25 | ✓ VERIFIED | All 25 defined + 25 traceability rows, all "Complete" |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `new_brunswick/client.py` | `shared/arcgis_hub.py` | import, `query_feature_service`/enumerators | ✓ WIRED | `grep -n "arcgis_hub\."` shows live delegation in `_geonb_query`, discovery fetchers |
| `shared/arcgis_hub.py` | `shared/http.py` | `decode_json` on every new response | ✓ WIRED | Both new functions call `decode_json(response, url)` |
| `new_brunswick/__init__.py` | FileSystemProvider | `MODULE_NAME`/`MODULE_DESCRIPTION` exports, no `server.py` edit | ✓ WIRED | Confirmed by successful live tool invocation through the full MCP `call_tool` path in integration tests |
| `new_brunswick/client.py` | `open.canada.ca/data/api/3/action/package_search` | `_api_get` + `_build_fq` | ✓ WIRED | Live: `test_search_datasets_about_flooding` returns real results |
| `new_brunswick/client.py` | `shared/parsers.py` | `fetch_and_parse` on parseable resources | ✓ WIRED | Live: `test_query_dataset_resource` passes |
| `new_brunswick/tools.py` | `new_brunswick/constants.py` | `FILTER_REQUIRED_TOOLS` drives pre-network guard | ✓ WIRED | `grep` confirms both `client.py` and `tools.py` reference the constant; live-verified guard fires before network (see CR-01 independent check) |
| `new_brunswick/prompts.py` | `new_brunswick/constants.py` | tool names sourced from `ALL_NB_TOOL_NAMES` | ✓ WIRED | `PROMPTS OK` check passes — zero stale tool references |

### Behavioral Spot-Checks (independent, run by the verifier — not taken from SUMMARY claims)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Tracer live Crown Land fetch | `nb_get_crown_land(lang='en', limit=25)` | 25 rows, `HOLDER`/`OBJECTID` present, api name correct | ✓ PASS |
| CR-01 LIKE-wildcard escape, live against GeoNB | raw `httpx.get` with `LIKE '%\%%' ESCAPE '\'` vs unescaped `'%%%'` | escaped: `{"count": 0}`; unescaped (pre-fix shape): `{"count": 604520}`; real value `YORK`: `{"count": 64208}` | ✓ PASS — independently confirms the CR-01 fix is genuine and doesn't break real matching |
| Wetlands/parcels/civic-address guards fire before network | full module unit suite + live integration scenarios | `test_wetlands_unfiltered_returns_invalid_input`, `test_parcels_unfiltered_returns_invalid_input`, `test_civic_addresses_unfiltered_returns_invalid_input` all pass live | ✓ PASS |
| 511 unconfigured envelope, bilingual, no key leakage | plan's exact live verify script re-run | `511 STUBS OK — unconfigured envelope bilingual, key never echoed` | ✓ PASS |
| Manifest set-equality | `constants.ALL_NB_TOOL_NAMES` vs `tools.ALL_NB_TOOLS` | both len 22, set-equal | ✓ PASS |
| Checkpoint option-a correctly applied | absence of 2 swapped tools, presence of 2 Socrata tools | `CHECKPOINT OPTION-A CORRECTLY APPLIED` | ✓ PASS |
| Catalogue/doc sync | `generate_catalog.py --check`, README/CLAUDE.md grep | "Catalog is up to date."; all facts present, false claim absent | ✓ PASS |
| Full default unit suite | `uv run pytest -q` | 3550 passed, 2 skipped | ✓ PASS |
| Coverage gate | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q` | 97.37% | ✓ PASS |
| ruff / pyright | `uv run ruff check src/ tests/`, `uv run pyright` | both clean (repo-wide) | ✓ PASS |
| server.py / dependency files untouched | `git diff --stat src/mcp_canada/server.py pyproject.toml uv.lock` | empty | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| NB-01..NB-05 | 21-02 | Federal CKAN discovery (5 tools) | ✓ SATISFIED | Live tests pass; org filter non-overridable |
| NB-06 | 21-01 | 2 additive shared ArcGIS Server enumerator functions | ✓ SATISFIED | `git show 978aae1` purely additive diff |
| NB-07..NB-09 | 21-04 | GeoNB discovery trio | ✓ SATISFIED | Live: services/layers/query all pass |
| NB-10..NB-13 | 21-04 | Flood hazard, historical floods, wetlands (guarded), contaminated sites | ✓ SATISFIED | Live scenarios pass |
| NB-14 | 21-01 | Crown Land tracer, layer 3 | ✓ SATISFIED | Live tracer + `crown_land_holder_and_object_id` scenario |
| NB-15, NB-16 | 21-05 | Mineral occurrences, provincial parks — marked superseded by NB-09 | ✓ SATISFIED (superseded) | REQUIREMENTS.md correctly marks superseded status; reachable via `nb_query_geonb_layer`, confirmed live |
| NB-17, NB-18 | 21-05 | Parcels, civic addresses, both filter-required | ✓ SATISFIED | Live guard + filtered-result tests pass |
| NB-19, NB-20 | 21-06 | Health facilities, public schools dispatch | ✓ SATISFIED | Live tests pass |
| NB-21..NB-23 | 21-06 | 3 key-gated 511 stubs | ✓ SATISFIED | Live `NOT_CONFIGURED` envelope verified bilingually with no key leakage |
| NB-24 | 21-07 | Module conventions, discoverability, catalogue sync, coverage ≥95% | ✓ SATISFIED | All structural gates pass |
| NB-25 | 21-01/21-07 | gnb.socrata.com documented and decision recorded | ✓ SATISFIED | COVERAGE.md, CLAUDE.md, REQUIREMENTS.md all record the verified fact |
| ERR-01..ERR-07 | all plans | Catch-all coverage, error classification defaults, decode-json discipline | ✓ SATISFIED | `tests/test_tool_error_handling.py`, `tests/test_error_classification_defaults.py`, `tests/test_upstream_error_classification.py` all pass with NB tools present |

No orphaned requirements — every NB-ID cited in the seven plan frontmatters is defined in
REQUIREMENTS.md and vice versa (the plan 21-07 `REQ TRACEABILITY OK` self-check pattern was
independently re-verified by grepping REQUIREMENTS.md directly above).

### Anti-Patterns Found

None. `grep -rn "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` across all `new_brunswick/*.py` returns
no matches. No bare `raise ValueError`. No `@mcp.` decorator usage (only explanatory comments stating
what NOT to use). No raw `response.json()`/`json.loads()` outside `shared/http.py`.

### Code Review Follow-Through

A post-execution code review (`21-REVIEW.md`) found 1 critical + 4 warnings + 1 info. All 6 were
fixed with TDD-style reproduction tests (`21-REVIEW-FIX.md`, commits `84192e3`, `791f30b`, `f9626dd`,
`2ff6931`, `a32b398`, `734f54b`). This verifier independently re-derived and live-confirmed the most
severe finding (CR-01, the `FILTER_REQUIRED_TOOLS` LIKE-wildcard/whitespace bypass) rather than
trusting the fix report: a raw `LIKE '%\%%' ESCAPE '\'` clause against the live
`GeoNB_SNB_Parcels` layer returns 0 rows for a literal `%`, while the pre-fix unescaped shape
(`LIKE '%%%'`) returns all 604,520 rows, and a real value (`YORK`) still matches correctly
(64,208 rows) — the fix is genuine and doesn't regress ordinary filtering. No further instance of
the same bypass class was found: every `_upper_contains_clause` call site (parcels, civic address,
mineral occurrences, school district) routes through the fixed escaping helper.

### Human Verification Required

None. Every truth in this phase is either a static/structural property (grep, import, count) or a
live-callable API behavior, both fully exercisable and exercised without human judgment. No UI,
no visual, no real-time-only behavior in this phase's surface.

### Gaps Summary

No gaps. All must-haves across all 7 plans, the roadmap Success Criteria, and both ERR-* and NB-*
requirement families are verified against the live codebase and live upstream APIs — not against
SUMMARY.md claims. The only observation worth carrying forward is the stale ROADMAP.md goal-text
sub-count breakdown described above, which is cosmetic and does not block phase completion.

---

_Verified: 2026-07-30T20:30:00Z_
_Verifier: Claude (gsd-verifier)_
