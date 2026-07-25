---
phase: 17-alberta-government-open-data
verified: 2026-04-16T00:00:00Z
re_verified: 2026-07-25T00:00:00Z
status: passed
score: 27/27 must-haves verified (automated); 2 live-agent UAT items confirmed 2026-07-25; 3 doc-tracking gaps closed 2026-07-25
requirements_covered: 27/27
automated_gate: passed
human_verification:
  - test: "BM25 discovery surfaces alberta_ tools for natural-language queries"
    expected: "Queries like 'oil wells alberta' and 'alberta wildfires right now' rank alberta_ tools in top 5 results"
    why_human: "BM25 relevance ranking across 217 tools is sensitive to surrounding module docstrings; live agent feel is the final check even though the unit-level discovery test passes"
    result: pass
    verified_on: 2026-07-25
    evidence: |
      Ran discover_tools through the MCP Client + BM25SearchTransform (max_results=5).
      alberta_ tools in top 5 for every query; correct tool ranked #1 in 4 of 5:
        'oil wells alberta'          -> 4/5 alberta_ (#1 alberta_get_well_licences_today)
        'alberta wildfires right now'-> 3/5 alberta_ (#1 wx_get_current_conditions, #2 alberta_get_active_fires)
        'alberta road closures'      -> 3/5 alberta_ (#1 alberta_get_road_events)
        'alberta hospitals'          -> 5/5 alberta_ (#1 alberta_get_hospitals)
        'alberta fire ban camping'   -> 4/5 alberta_ (#1 alberta_get_fire_bans)
      The one non-alberta #1 (weather for "right now") is acceptable cross-module
      competition, not a discovery failure — the expected criterion was top-5 ranking.
  - test: "French-language (lang='fr') agent session returns bilingual error messages and _meta.lang='fr' end-to-end"
    expected: "A francophone agent asking Alberta questions gets French error strings + _meta.lang='fr' on every tool response"
    why_human: "Inline ternary `lang == 'fr'` pattern covers error messages but nuances (formatting, terminology) are subjective; only a conversational pass can confirm quality"
    result: pass
    verified_on: 2026-07-25
    evidence: |
      Error path (live, through MCP call_tool):
        alberta_get_dataset_details(package_id="definitely-not-real-xyz", lang="fr")
        -> {"error":{"code":"NOT_FOUND","message":"Jeu de données introuvable: definitely-not-real-xyz","lang":"fr"}}
      Success path (live, open.alberta.ca):
        alberta_list_categories(lang="fr") -> _meta.lang='fr', _meta.source.api='alberta-open-data'
      Note: Literal-typed params (e.g. category, ban_type) are rejected by Pydantic
      before the tool body runs, so their French INVALID_INPUT branches are
      unreachable through MCP. Not a defect — the type system is the earlier gate —
      but it means those specific French strings are dead code.
gaps_closed:
  - "REQUIREMENTS.md AB-18/AB-19/AB-20 flipped to Complete + [x] (2026-07-25)"
  - "ROADMAP.md Phase 17 plan checkboxes 17-01..17-09 flipped to [x] (2026-07-25)"
  - "STATE.md rolled forward off the stale 'Phase 7 of 10' position (2026-07-25)"
gaps:
  - truth: "REQUIREMENTS.md traceability table marks AB-01..26 + AB-27 as Complete"
    status: resolved
    resolved_on: 2026-07-25
    reason: "AB-18, AB-19, AB-20 rows still show 'Planned' in REQUIREMENTS.md traceability table even though 511 Alberta transport tools ship and are covered by live integration tests"
    artifacts:
      - path: ".planning/REQUIREMENTS.md"
        issue: "Lines 321-323 list AB-18/AB-19/AB-20 as 'Planned'; same rows' checklist entries at lines 161-163 are missing the `[x]` prefix while AB-01..17 + AB-21..27 have `[x]`"
    missing:
      - "Update REQUIREMENTS.md traceability table AB-18/AB-19/AB-20 rows to 'Complete' (lines 321-323)"
      - "Add `[x]` to the requirement checklist lines for AB-18/AB-19/AB-20 (lines 161-163)"
  - truth: "ROADMAP.md Phase 17 plan checklist shows 9/9 plans complete"
    status: resolved
    resolved_on: 2026-07-25
    reason: "Phase 17 header claims 'Plans: 9/9 plans complete' but all 9 individual plan checkbox rows are still rendered as `- [ ]` (unchecked)"
    artifacts:
      - path: ".planning/ROADMAP.md"
        issue: "Lines 216-224 list 9 plan entries with `- [ ]` markers; lines 203-205 (Phase 16) show the expected `- [x]` pattern for completed plans"
    missing:
      - "Flip each Phase 17 plan checkbox at ROADMAP.md lines 216-224 to `- [x]` so the header claim matches the individual entries"
  - truth: "STATE.md reflects Phase 17 as complete (completed_phases/total_phases/status)"
    status: resolved
    resolved_on: 2026-07-25
    reason: "STATE.md frontmatter shows `completed_phases: 12` and `status: planning` with `current_focus: Phase 7 — Datastore + SSL`; 17-09-SUMMARY ships a closing note but STATE.md has not been rolled forward to reflect Phase 17 completion"
    artifacts:
      - path: ".planning/STATE.md"
        issue: "Lines 10-14: progress.completed_phases=12 + percent=0; line 24: `Current focus: Phase 7 — Datastore + SSL`; line 28: `Phase: 7 of 10`"
    missing:
      - "Advance completed_phases counter to include Phase 17"
      - "Update `current_focus` / `Current Position` headings to reflect that Phase 17 is done (or point to next pending phase, e.g., Phase 18 Manitoba)"
---

# Phase 17: Alberta Government Open Data — Verification Report

**Phase Goal:** Add Alberta's provincial open data surface to mcp-canada via 24 `alberta_` tools (5 discovery + 19 curated). Primary CKAN at open.alberta.ca, ArcGIS Hub portals (GeoDiscover Alberta + WMBappServices + AHSGIS), AER static reports, 511 Alberta REST API. Bilingual, BM25-discoverable, integration-tested through MCP Client, ≥95% coverage.

**Verified:** 2026-04-16
**Status:** PASSED (27/27 automated must-haves; both live-agent UAT items confirmed 2026-07-25; all three planning-doc tracking gaps closed 2026-07-25)
**Re-verification:** Yes — 2026-07-25 reconciliation pass. See `human_verification[].evidence` in the frontmatter for the BM25-discovery and French-language transcripts.

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                         | Status      | Evidence                                                                                                                |
|----|-----------------------------------------------------------------------------------------------|-------------|-------------------------------------------------------------------------------------------------------------------------|
| 1  | Agent sees 24 `alberta_` tools through the MCP discover_tools / call_tool path                | ✓ VERIFIED  | 24 `@tool`-decorated async defs in `src/mcp_canada/modules/alberta/tools.py` (lines 116–1024)                           |
| 2  | Every tool has a matching `fetch_*` client implementation                                      | ✓ VERIFIED  | 24 `async def fetch_*` functions in `client.py` lines 326–1371                                                          |
| 3  | Every tool has BM25-discoverable docstring (Use for: + Keywords:)                              | ✓ VERIFIED  | 24 `Use for:` + 24 `Keywords:` lines in `tools.py` (`tests/test_quality.py` passes 5/5)                                 |
| 4  | Every tool returns `_meta` envelope and propagates `lang` to `_meta.lang`                      | ✓ VERIFIED  | `TestAlbertaEnvelopes` + `TestAlbertaLangParam`: **48/48 parametrized cases pass** (24 tools × 2 test classes)           |
| 5  | 6 prompts exist under `alberta_` prefix with `lang` parameter                                  | ✓ VERIFIED  | 6 `@prompt` async defs in `prompts.py` lines 40–392                                                                      |
| 6  | 7 zero-parameter `@resource` functions exist                                                   | ✓ VERIFIED  | 7 `@resource`-decorated functions in `resources.py`, all signatures are `() -> str`                                     |
| 7  | `_api_get` helper treats api_get return as parsed dict (no `.raise_for_status` / `.json`)      | ✓ VERIFIED  | `client.py` lines 172–204; only `.raise_for_status()` call at line 665 is an unrelated raw httpx block in ST1 fetcher   |
| 8  | `_511_get` helper for 511 Alberta list endpoints exists and is distinct                        | ✓ VERIFIED  | `client.py` lines 207–227; used by `fetch_road_events` / `fetch_winter_road_conditions` / `fetch_traffic_cameras`       |
| 9  | `TestSharedApiGetContract` regression guard covers the parsed-dict contract                    | ✓ VERIFIED  | `__tests__/test_client.py` lines 15–67 (3 scenarios: parsed dict / success=False / success=True)                        |
| 10 | Bilingual inline `lang == "fr"` pattern used (no shared/i18n.py:t() adoption)                  | ✓ VERIFIED  | 36 occurrences of `if lang == "fr"` in `tools.py`; zero imports from `shared.i18n`                                      |
| 11 | `alberta_list_categories` uses `package_search?facet.field=res_format` (NOT group_list)        | ✓ VERIFIED  | `client.py` lines 554–578: `params = {"facet.field": '["res_format"]', ...}`                                             |
| 12 | ST3 production volumes validates case-sensitive product tuple (Pitfall 8)                      | ✓ VERIFIED  | `client.py` lines 722–750 + `constants.py` lines 131–141 (`ST3_PRODUCTS` 7-tuple, exact case)                           |
| 13 | Wildfire tools use WMBappServices (not token-walled GeoDiscover)                               | ✓ VERIFIED  | `constants.py` lines 66–95 define `WMB_ORG_BASE = services.arcgis.com/Eb8P5h4CJk8utIBz/…`; all 4 wildfire fetchers use it |
| 14 | Health tools use AHSGIS (services5.arcgis.com/7KHJ4f28UDLgUq2U)                                | ✓ VERIFIED  | `constants.py` lines 101–110 define `AHS_*_FS_URL`; referenced in `fetch_hospitals`/`fetch_ahs_zones`/`fetch_health_facilities` |
| 15 | No `shared/aer.py` extracted (premature abstraction rejected)                                  | ✓ VERIFIED  | `ls src/mcp_canada/shared/` shows no `aer.py`; AER logic lives inline in `alberta/client.py`                            |
| 16 | Integration tests route through MCP Client (not direct client functions)                       | ✓ VERIFIED  | `tests/integration/conftest.py` lines 51–77 provide `call_tool`/`discover` helpers; `TestAlbertaToolScenarios` uses them |
| 17 | `TestAlbertaToolScenarios` present with ~7 live-API scenarios                                  | ✓ VERIFIED  | `tests/integration/test_tool_scenarios.py` lines 1833–1948 (7 scenarios: search, active_fires, hospitals, road_events, production_volumes, invalid product, BM25 discovery) |
| 18 | `TestAlbertaPromptsResources` verifies 6 prompts + 7 resources discoverable                    | ✓ VERIFIED  | `tests/integration/test_prompts_resources_scenarios.py` lines 650–709 (3 scenarios list_prompts / list_resources / read_resource) |
| 19 | Coverage ≥ 95% on alberta module                                                               | ✓ VERIFIED  | `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` → **96.84%** (198 unit tests pass)             |
| 20 | README.md updated with Alberta section and tool count                                          | ✓ VERIFIED  | `README.md` line 20 ("217 tools … + 5 provincial APIs"), line 133 (Alberta table row linking to `docs/modules/alberta.md`) |
| 21 | Per-module doc page exists (`docs/modules/alberta.md`)                                         | ✓ VERIFIED  | 7.0 KB page lists 24 tools grouped by 5 sections + 6 prompts + 7 resources                                              |
| 22 | EXAMPLES.md has an Alberta cross-module example                                                | ✓ VERIFIED  | `EXAMPLES.md` line 753 "Example 24: Alberta Energy + Wildfire — Production vs. Fire Season Map" (uses 5 alberta_ tools + datastore) |
| 23 | CLAUDE.md updated: Alberta listed in CKAN + ArcGIS Hub portal technology rows                  | ✓ VERIFIED  | `CLAUDE.md` line 71 (CKAN row includes Alberta), line 72 (ArcGIS Hub row includes Phase 17: Alberta)                    |
| 24 | 9 PLAN.md files have 9 matching SUMMARY.md files                                               | ✓ VERIFIED  | `ls 17-0*-PLAN.md` → 9 files; `ls 17-0*-SUMMARY.md` → 9 files                                                           |
| 25 | All 27 AB-XX requirement IDs claimed by at least one plan's `requirements:` frontmatter        | ✓ VERIFIED  | Union of plan 17-01..09 `requirements:` fields covers AB-01 through AB-27 with no gaps                                  |
| 26 | `test_quality.py` passes for all 24 alberta tools (BM25 docstring quality gate)                | ✓ VERIFIED  | `uv run pytest tests/test_quality.py` → 5/5 passed                                                                      |
| 27 | ROADMAP.md Phase 17 declares 9/9 plans complete in the header                                  | ✓ VERIFIED  | `ROADMAP.md` line 213: "**Plans:** 9/9 plans complete" (individual checkbox state tracked as a separate gap)            |

**Score:** 27/27 observable truths verified (automated checks only).

### Required Artifacts

| Artifact                                                                            | Expected                                                            | Status     | Details                                                   |
|-------------------------------------------------------------------------------------|---------------------------------------------------------------------|------------|-----------------------------------------------------------|
| `src/mcp_canada/modules/alberta/tools.py`                                           | 24 `@tool` async functions, `alberta_` prefix, bilingual            | ✓ VERIFIED | 1054 lines; 24 `@tool` blocks                              |
| `src/mcp_canada/modules/alberta/client.py`                                          | 24 `fetch_*` functions + `_api_get` + `_511_get`                    | ✓ VERIFIED | 1401 lines; 24 fetch_ functions; both helpers defined     |
| `src/mcp_canada/modules/alberta/prompts.py`                                         | 6 `@prompt` functions with `lang` param                             | ✓ VERIFIED | 442 lines; 6 `@prompt` async defs                          |
| `src/mcp_canada/modules/alberta/resources.py`                                       | 7 zero-parameter `@resource` functions                              | ✓ VERIFIED | 739 lines; 7 resources (3 data:// + 2 docs:// + 2 template://) |
| `src/mcp_canada/modules/alberta/constants.py`                                       | Portal URLs + ST3_PRODUCTS + rate groups                            | ✓ VERIFIED | 203 lines; `ST3_PRODUCTS` 7-tuple with exact casing       |
| `src/mcp_canada/modules/alberta/schemas.py`                                         | Pydantic v2 flat models                                             | ✓ VERIFIED | 390 lines                                                  |
| `src/mcp_canada/modules/alberta/__tests__/test_tools.py`                            | `TestAlbertaEnvelopes` + `TestAlbertaLangParam` × 24 tools          | ✓ VERIFIED | 1236+ lines; 48 parametrized cases green                  |
| `src/mcp_canada/modules/alberta/__tests__/test_client.py`                           | `TestSharedApiGetContract` regression guard                         | ✓ VERIFIED | Lines 15–67 cover parsed-dict / success=False / success=True |
| `tests/integration/test_tool_scenarios.py::TestAlbertaToolScenarios`                | 6–8 live-API scenarios via `Client(mcp)`                            | ✓ VERIFIED | 7 scenarios at lines 1833–1948                            |
| `tests/integration/test_prompts_resources_scenarios.py::TestAlbertaPromptsResources`| list_prompts / list_resources / read_resource                       | ✓ VERIFIED | 3 scenarios at lines 650–709                              |
| `README.md`                                                                         | Alberta row + tool count recount                                    | ✓ VERIFIED | 217 tools header, provincial row linking to per-module doc |
| `docs/modules/alberta.md`                                                           | Per-module catalog page (project convention vs. plan's `docs/MODULES.md` suggestion) | ✓ VERIFIED | 7.0 KB, 24 tools tabulated                                 |
| `EXAMPLES.md`                                                                       | Alberta cross-module example                                        | ✓ VERIFIED | Example 24 exists                                          |
| `CLAUDE.md`                                                                         | Alberta in CKAN + ArcGIS Hub portal rows                            | ✓ VERIFIED | Lines 71–72                                                |

### Key Link Verification

| From                              | To                                     | Via                                                 | Status    | Details                                                                    |
|-----------------------------------|----------------------------------------|-----------------------------------------------------|-----------|----------------------------------------------------------------------------|
| `alberta_*` tools (24)            | `alberta.client.fetch_*` (24)          | `from . import client as _client` + `await _client.fetch_*` | ✓ WIRED   | Every tool calls `_client.fetch_*` and wraps with `make_response`/`make_error` |
| CKAN fetchers                     | `shared.http.api_get`                  | `alberta.client.api_get` module-local binding       | ✓ WIRED   | `TestSharedApiGetContract` patches the module-local name to guard contract |
| 511 fetchers                      | `_511_get`                             | `_511_get("event"|"winterroads"|"cameras")`         | ✓ WIRED   | 3 call sites at `client.py` lines 1090, 1118, 1145                         |
| AER ST3                           | `shared.parsers.fetch_and_parse`       | `fetch_and_parse(url, ttl=CACHE_TTL_MONTHLY)`        | ✓ WIRED   | `fetch_production_volumes` at `client.py` line 747                         |
| Wildfire fetchers                 | `shared.arcgis_hub.query_feature_service` | `arcgis_hub.query_feature_service(url, 0, …)`    | ✓ WIRED   | All 4 wildfire fetchers use WMBappServices FeatureServer URLs              |
| Health fetchers                   | AHSGIS FeatureServers                  | `services5.arcgis.com/7KHJ4f28UDLgUq2U/.../FeatureServer` | ✓ WIRED   | 3 fetchers reference `AHS_*_FS_URL` constants                              |
| `TestAlbertaToolScenarios`        | MCP Client wiring (`Client(mcp_server)`) | `tests/integration/conftest.py::call_tool/discover` | ✓ WIRED   | Integration scenarios do **not** import client.py fetchers directly        |
| Tool docstrings                   | BM25 discover_tools                    | `Use for:` + `Keywords:` line pair                  | ✓ WIRED   | `test_quality.py` enforcement passes                                       |

### Requirements Coverage

| Requirement | Source Plan(s)    | Description                                                                  | Codebase Status | REQUIREMENTS.md Status | Evidence                                                                                   |
|-------------|-------------------|------------------------------------------------------------------------------|-----------------|------------------------|--------------------------------------------------------------------------------------------|
| AB-01       | 17-02             | Search open.alberta.ca CKAN by keyword / org / format                        | ✓ SATISFIED     | Complete               | `alberta_search_datasets` tool + `fetch_search_datasets` + unit + integration tests        |
| AB-02       | 17-02             | Full dataset details with 50+ Alberta extras flattened                       | ✓ SATISFIED     | Complete               | `alberta_get_dataset_details` + `AlbertaDatasetDetails` schema                              |
| AB-03       | 17-02             | Hybrid router — ESRI REST → arcgis_hub, CSV/XLSX → fetch_and_parse, PDF metadata-only | ✓ SATISFIED | Complete           | `fetch_query_dataset` at `client.py` lines 432–525; tool at `tools.py` line 195            |
| AB-04       | 17-02             | 370 federated organizations                                                  | ✓ SATISFIED     | Complete               | `alberta_list_organizations` + `fetch_organizations`                                        |
| AB-05       | 17-02             | res_format facet categories (Pitfall 1: NOT group_list)                      | ✓ SATISFIED     | Complete               | `fetch_format_categories` at `client.py` line 554                                           |
| AB-06       | 17-03             | AER ST1 daily well licences (day-of-week rotation)                           | ✓ SATISFIED     | Complete               | `fetch_well_licences_today` + `_parse_st1_txt` + `DAY_ABBR`                                 |
| AB-07       | 17-03             | AER ST1 monthly archive ZIP URL (discovery-only)                             | ✓ SATISFIED     | Complete               | `fetch_well_licences_archive` at `client.py` line 671                                       |
| AB-08       | 17-03             | AER ST39 annual pipeline statistics XLSX                                     | ✓ SATISFIED     | Complete               | `fetch_pipeline_statistics` at `client.py` line 702                                         |
| AB-09       | 17-03             | AER ST3 production — 7 case-sensitive products (Pitfall 8)                   | ✓ SATISFIED     | Complete               | `ST3_PRODUCTS` tuple + ValueError + `TestAlbertaInvalidProductReturnsStructuredError` integration |
| AB-10       | 17-04             | WMBappServices active wildfires                                              | ✓ SATISFIED     | Complete               | `fetch_active_fires` + `ACTIVE_WILDFIRES_FS_URL`                                            |
| AB-11       | 17-04             | Wildfire perimeters (active | extinguished)                                  | ✓ SATISFIED     | Complete               | `fetch_fire_perimeters` + ACTIVE/EXTINGUISHED URL pair                                      |
| AB-12       | 17-04             | Historical wildfire data documented as alberta_query_dataset route          | ✓ SATISFIED     | Complete               | Tool docstring at `tools.py` line 465 directs agents to CKAN `wildfire-data` package        |
| AB-13       | 17-04             | Current fire bans (WMBappServices `alberta_fire_ban_system`)                 | ✓ SATISFIED     | Complete               | `fetch_fire_bans` + `FIRE_BAN_SYSTEM_FS_URL`                                                |
| AB-14       | 17-04             | Fire control orders / OHV / forest areas (single tool, category-dispatched) | ✓ SATISFIED     | Complete               | `fetch_fire_control_orders` + 3-way dispatch table                                          |
| AB-15       | 17-05             | AHS hospitals with zone/IP/ED flags                                          | ✓ SATISFIED     | Complete               | `fetch_hospitals` + `AHS_HOSPITALS_FS_URL`                                                  |
| AB-16       | 17-05             | EMS / PCN clinics (facility_type dispatch, Pitfall 9 wait-times deferred)   | ✓ SATISFIED     | Complete               | `fetch_health_facilities` + 2-way dispatch + docstring note                                 |
| AB-17       | 17-05             | 5 AHS zones with 2006/2011/2016 population                                   | ✓ SATISFIED     | Complete               | `fetch_ahs_zones` + `AHS_ZONE_FS_URL`                                                       |
| AB-18       | 17-06             | 511 Alberta road events                                                      | ✓ SATISFIED     | **Planned** (STALE)    | `fetch_road_events` + `alberta_get_road_events` + integration test at line 1890             |
| AB-19       | 17-06             | 511 Alberta winter road conditions                                           | ✓ SATISFIED     | **Planned** (STALE)    | `fetch_winter_road_conditions` + `alberta_get_winter_road_conditions`                       |
| AB-20       | 17-06             | 511 Alberta traffic cameras                                                  | ✓ SATISFIED     | **Planned** (STALE)    | `fetch_traffic_cameras` + `alberta_get_traffic_cameras`                                     |
| AB-21       | 17-07             | 75 AQHI air quality stations                                                 | ✓ SATISFIED     | Complete               | `fetch_air_quality_stations` + `AQHI_AIR_LAYER_URL`                                         |
| AB-22       | 17-07             | Water advisories (5-way advisory_type dispatch)                              | ✓ SATISFIED     | Complete               | `fetch_water_advisories` + `RIVER_FORECAST_FS_URL`                                          |
| AB-23       | 17-02, 17-08      | Water licence registry documented as discovery-only with size caveat         | ✓ SATISFIED     | Complete               | `docs://alberta/wildfire-data-guide` resource at `resources.py` line 489                    |
| AB-24       | 17-07             | Historical crop production (2000–2014)                                       | ✓ SATISFIED     | Complete               | `fetch_crop_production` + `alberta_get_crop_production`                                     |
| AB-25       | 17-07             | Population estimates with breakdown Literal (CSD default)                    | ✓ SATISFIED     | Complete               | `fetch_population_estimates` + 6-value breakdown                                            |
| AB-26       | 17-07             | Provincial parks / protected areas                                           | ✓ SATISFIED     | Complete               | `fetch_provincial_parks` + `PROVINCIAL_PARKS_FS_URL`                                        |
| AB-27       | 17-01, 17-08, 17-09 | Conventions: @tool/make_response/Use-for+Keywords/alberta_ prefix; 6 prompts + 7 resources auto-discovered | ✓ SATISFIED | Complete | 48 parametrized envelope/lang cases green + `test_quality.py` green + 3 prompts/resources integration scenarios |

**Orphaned requirements:** None. All AB-01..27 referenced in REQUIREMENTS.md Phase 17 section appear in at least one plan's `requirements:` field.

**Coverage ratio:** 27/27 satisfied in code; 24/27 marked Complete in REQUIREMENTS.md traceability table (AB-18, AB-19, AB-20 stale → see gap 1).

### Anti-Patterns Found

| File                                              | Line    | Pattern                            | Severity | Impact                                                                 |
|---------------------------------------------------|---------|------------------------------------|----------|------------------------------------------------------------------------|
| `src/mcp_canada/modules/alberta/client.py`        | 665     | `resp.raise_for_status()`          | ℹ️ Info   | Inside AER ST1 raw-httpx block (TXT download, not CKAN `api_get`); does NOT violate the parsed-dict contract (which targets `_api_get`). Acceptable — AER TXT endpoint needs direct httpx to follow the 303 redirect to `static.aer.ca`. |
| (none)                                            | —       | TODO / FIXME / placeholder         | —        | `grep -E "TODO|FIXME|XXX|HACK|PLACEHOLDER"` on `modules/alberta/*.py` → 0 matches  |
| (none)                                            | —       | `return null`/`return []` / empty  | —        | No placeholder/dead-end implementations                                |

No blocker or warning anti-patterns.

### Human Verification Required

Two behaviors that automated checks cannot fully validate:

1. **BM25 natural-language discovery across 217 tools**
   - **Test:** From a fresh agent session, ask: "What oil wells were issued in Alberta today?" / "Show me active Alberta wildfires" / "Are there any road closures on the Yellowhead?"
   - **Expected:** `discover_tools` surfaces the corresponding alberta_ tool in the top 5 results for each query.
   - **Why human:** The unit-level BM25 test (`test_discover_alberta_via_bm25`) asserts ≥ 1 alberta_ tool appears for `"alberta wells oil energy regulator"`, but agent-side ranking across 217 tools with overlapping vocabularies (BC / Quebec wildfire tools, Ontario transport tools, etc.) is subjective and only verifiable in a live session.

2. **Bilingual (`lang='fr'`) conversational quality**
   - **Test:** In French, ask Alberta questions across the surface — wildfire status, hospital lookup, AER production, invalid-product error, dataset search — and inspect responses.
   - **Expected:** `_meta.lang == "fr"` on success; French error strings that read naturally (not broken by Python f-string interpolation); bilingual Alberta metadata passthrough is acknowledged when source data is English-only.
   - **Why human:** The inline `lang == "fr"` ternary pattern covers string selection, but translation quality (accent handling, terminology, punctuation) and the handling of English-only source data in a French response are judgment calls.

---

## Must-Haves Checklist

| # | Must-Have                                                                                                  | Pass/Fail |
|---|------------------------------------------------------------------------------------------------------------|-----------|
| 1  | 24 `@tool` functions in `tools.py` matching `ALL_ALBERTA_TOOLS`                                            | PASS      |
| 2  | 24 `fetch_*` client functions in `client.py`                                                               | PASS      |
| 3  | 6 `@prompt` functions + 7 zero-parameter `@resource` functions                                             | PASS      |
| 4  | `TestSharedApiGetContract` regression guard (parsed-dict contract)                                         | PASS      |
| 5  | `_api_get` helper treats api_get return as parsed dict (no `.raise_for_status` / `.json`)                  | PASS      |
| 6  | `_511_get` helper for 511 Alberta JSON list endpoints (distinct from `_api_get`)                           | PASS      |
| 7  | BM25 docstrings on every tool (Use for: + Keywords:)                                                       | PASS      |
| 8  | Bilingual inline `lang == "fr"` ternary pattern (NO shared/i18n.py:t() adoption)                            | PASS      |
| 9  | `alberta_list_categories` uses `package_search?facet.field=res_format` (NOT group_list)                    | PASS      |
| 10 | ST3 production volumes validates case-sensitive product tuple (Pitfall 8)                                  | PASS      |
| 11 | Wildfire/health tools use WMBappServices/AHSGIS (NOT token-walled GeoDiscover folders)                     | PASS      |
| 12 | NO `shared/aer.py` extracted (premature abstraction rejection)                                             | PASS      |
| 13 | `TestAlbertaEnvelopes` + `TestAlbertaLangParam` parametrized across 24 tools (48 cases) all green          | PASS      |
| 14 | Integration tests via `Client(mcp)` pattern (NOT direct client function calls)                             | PASS      |
| 15 | Coverage ≥ 95% on alberta module                                                                           | PASS (96.84%) |
| 16 | README.md updated with Alberta section and updated tool count                                              | PASS      |
| 17 | docs/MODULES.md (or docs/modules/alberta.md) updated                                                       | PASS (`docs/modules/alberta.md`) |
| 18 | EXAMPLES.md updated with Alberta example                                                                   | PASS      |
| 19 | CLAUDE.md updated with Alberta in provincial CKAN list (and ArcGIS Hub list)                               | PASS      |
| 20 | All 9 PLAN.md have matching SUMMARY.md (17-01 through 17-09)                                               | PASS      |
| 21 | STATE.md reflects phase 17 as In Progress / Complete                                                       | **FAIL** — STATE still shows `status: planning`, `current_focus: Phase 7`, `completed_phases: 12` (see gap 3) |
| 22 | ROADMAP.md Phase 17 has plan count 9/9                                                                      | PASS (header); individual checkbox lines still `[ ]` (see gap 2) |
| 23 | All AB-XX IDs in at least one plan's `requirements:` + REQUIREMENTS.md traceability table marked Complete  | PARTIAL — AB-18/19/20 traceability rows still say `Planned` though code ships (see gap 1) |

---

## Gaps Summary

All **code-level** and **test-level** must-haves pass. Three planning-document tracking discrepancies remain — all are pure bookkeeping (the code/tests/docs they point to are already in place):

1. **REQUIREMENTS.md traceability table out-of-sync for AB-18/AB-19/AB-20** (511 Alberta transport tools). The tools ship, have unit coverage, and live in the integration suite, but the table rows say `Planned` instead of `Complete`.
2. **ROADMAP.md Phase 17 plan checkboxes all `[ ]`** despite the `**Plans:** 9/9 plans complete` header and 9 matching SUMMARY files. Flip each `- [ ]` to `- [x]`.
3. **STATE.md frontmatter not advanced** to reflect Phase 17 completion (`completed_phases: 12`, `status: planning`, `current_focus: Phase 7 — Datastore + SSL`).

These are low-risk cosmetic fixes that do not require re-planning or re-execution; they should be handled by `/gsd:verify-work 17` post-verification housekeeping or a dedicated doc-sync pass.

## Next Steps

1. **Close the 3 planning-doc gaps above** (single-file edits, no code changes).
2. **Run the 2 human UAT items** in a live agent session (BM25 ranking + FR conversational quality).
3. Once the UAT and doc-sync are green, Phase 17 is ready for sign-off and the roadmap pointer can advance to Phase 18 (Manitoba).

---

_Verified: 2026-04-16_
_Verifier: Claude (gsd-verifier)_
_Automated gate: 48 parametrized + 198 unit + 5 quality + 7 integration (Alberta) = all green; coverage 96.84%._
