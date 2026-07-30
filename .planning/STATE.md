---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Statistics Canada + Datastore
current_phase: 21
current_phase_name: new-brunswick-government-open-data
status: executing
stopped_at: Completed 21-04-PLAN.md
last_updated: "2026-07-30T17:16:59.503Z"
last_activity: 2026-07-30
last_activity_desc: Phase 21 execution started
progress:
  total_phases: 38
  completed_phases: 19
  total_plans: 87
  completed_plans: 84
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** An agent can combine data from any Canadian government source in a single SQL query — turning isolated APIs into one queryable data platform.
**Current focus:** Phase 21 — new-brunswick-government-open-data

## Current Position

Phase: 21 (new-brunswick-government-open-data) — EXECUTING
Plan: 5 of 7
Status: Ready to execute
Last activity: 2026-07-30 — Phase 21 execution started

**Open decision before execution:** Plan 21-01 Task 2 carries a blocking `checkpoint:decision`.
A live probe during planning found `https://gnb.socrata.com` DOES exist (HTTP 200, 312 datasets,
keyless, already speakable by `shared/socrata.py`), contradicting CONTEXT.md D-01's "NB has no
provincial catalogue" framing. D-01 was NOT overridden — the checkpoint decides whether to add
Socrata tools, ship as locked, or repoint discovery. See COVERAGE.md Surface 5.

Phase 20.4 is COMPLETE and MERGED to main (PR #5, merge commit caa4d66).

Phase 20.1 is COMPLETE and MERGED to main (PR #2, merge commit 98dee90).

Progress: [██████████] 97%

**Executed and verified:** phases 07-20, 20.1, 20.2 and 40 (17 phases, 78 plans, all verification `passed`).
Suite at merge: 3145 passed, 2 skipped, 97.09% coverage. Live: 317 integration tests green.

**CI gates green for the first time (2026-07-26).** The workflow ignores `main` and
runs only on `pull_request`, so these had never executed against this codebase.
Measured on origin/main before the fix: ruff 96 errors, catalog stale by 189 tools.
All now pass on Python 3.12, 3.13 and 3.14 (3.14 added in Phase 20.2).

**Reconciliation of 2026-07-25** (see git history for the commit):

- Phase 17 (Alberta): was `human_needed`. Both live-agent UAT items re-run and
  confirmed (BM25 discovery ranks `alberta_` tools top-5 on all 5 probe queries;
  French error strings + `_meta.lang='fr'` verified live). All 3 doc-tracking gaps closed.

- Phase 11 (IRCC): was mechanically `stale` — the report predated plan 11-04, a
  gap-closure plan. Re-verified with 3 added truths covering 11-04; 11-UAT was
  already 10/10 against the post-11-04 build.

- REQUIREMENTS.md: 100 checklist boxes and 117 traceability rows were still
  "Planned" for shipped work. Flipped to Complete against on-disk evidence.

- ROADMAP.md: 61 plan checkboxes flipped to `[x]`.

## Open Items

All items from the 2026-07-25 reconciliation are closed:

1. ~~StatCan `FREQUENCY_CODES` is wrong~~ — **FIXED.** Frequency *and* scalar-factor
   maps were both shifted; rebuilt from StatCan's published code set, catalogs
   updated, tautological assertions replaced with literals, live-drift guard added.

2. ~~`sc_get_series_info_by_vector` returns no UOM label~~ — **FIXED.** Decoded `uom`
   added, sourced from live getCodeSets. Turned up a third fabricated catalog
   (`data://statcan/uom-codes`, all 15 entries wrong) — replaced with a verified subset.

3. ~~Phases 15 (BC) and 16 (Quebec) have no REQUIREMENTS.md entries~~ — **BACKFILLED.**
   BC-01..22 and QC-01..19 derived from shipped code and verified against the modules;
   ROADMAP `Requirements: TBD` lines replaced. Every executed phase now has traceability.

4. ~~3 active debug sessions~~ — **CLOSED.** All three were fixed long ago:
   `ircc-header-parsing` moved to resolved/ (plan 11-04 shipped its recommendation
   verbatim); the two BC sessions were stale duplicates of newer files already in
   resolved/.

Open defect (found 2026-07-26, deferred to its own phase):

- **Alberta wildfire tools are dead upstream.** The entire WMB FeatureServer group
  now returns `499 Token Required`: `ACTIVE_WILDFIRES`, `ACTIVE_FIRE_PERIMETERS`,
  `EXTINGUISHED_WILDFIRES`, `EXTINGUISHED_PERIMETERS`, `FIRE_CONTROL_ORDERS`,
  `OHV_RESTRICTION`. This kills `alberta_get_active_fires`,
  `alberta_get_fire_perimeters` and `alberta_get_fire_control_orders`.
  Only `alberta_get_active_fires` has an integration test, and it uses
  `assert_live_or_transient`, so the token error is tolerated as `UPSTREAM_ERROR`
  and the test passes silently — the exact masking pattern `.claude/rules/tests.md`
  warns about after the TTC incident. The other fire tools have no live coverage.
  Needs a decision: find an unauthenticated endpoint, or return `NOT_CONFIGURED`
  behind an env-var key like Manitoba 511. Alberta AHS, parks, forest-area and
  Saskatchewan/Manitoba Hub services were probed at the same time and are healthy.

- ~~**Malformed-JSON masking is broader than the spot Codex flagged.**~~ → **CLOSED by Phase 20.2** (PR #3). The sweep found the problem was wider than this note assumed: 108 of 271 tools had no catch-all at all, not just 7 modules with a mislabelling `ValueError` arm. Codex then found two further defects in the fix itself — `upstream_guard` was never a true catch-all (a `KeyError` still escaped), and `pydantic.ValidationError` also subclasses `ValueError`, so upstream schema drift was blamed on the caller. Both fixed. Original note kept below for the record:
  `upstream_guard` is fixed, which covers drug_database and nutrient_file (they use
  their own clients). But `shared/http.py:api_get` returns `response.json()` with no
  decode guard, and ~40 `except ValueError -> INVALID_INPUT` arms across statcan,
  ircc, manitoba, saskatchewan, nova_scotia, british_columbia and datastore sit
  downstream of it, so an upstream HTML error page still surfaces as caller error
  there. Pre-existing, not introduced by Phase 20.1.

  Correction to the first note taken on this: it is **not** a one-line fix inside
  `api_get`. `httpx.DecodingError` is an `HTTPError` but **not** an
  `HTTPStatusError`, and 5 of 24 modules (bank_of_canada, ckan, ircc, ontario,
  recalls) catch only `HTTPStatusError` — a naive central guard would turn a
  mislabelled error into an *unhandled* one in those five, which is strictly worse
  and is the exact failure 20.1 removed. Handler shape must be normalized across
  all 24 modules first. Sequenced before Phase 21 so ~19 future modules inherit the
  correct shape.

Remaining backlog (not defects):

- `.planning/todos/pending/2026-04-12-research-cross-canada-er-wait-times-datasets.md`
  — research item; premises refreshed 2026-07-25 against what phases 17-20 learned.

- ROADMAP phases 20.1 and 21-39 carry `Requirements: TBD` — correct, they are unplanned.

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 07-datastore-ssl P03 | 15 | 1 tasks | 7 files |
| Phase 07-datastore-ssl P01 | 3 | 1 tasks | 9 files |
| Phase 07-datastore-ssl P02 | 5min | 2 tasks | 4 files |
| Phase 08-statcan-wds P01 | 4min | 2 tasks | 5 files |
| Phase 08-statcan-wds P02 | 12min | 2 tasks | 3 files |
| Phase 08-statcan-wds P03 | 7min | 2 tasks | 8 files |
| Phase 09-sdmx-composite P01 | 4min | 2 tasks | 5 files |
| Phase 09-sdmx-composite P02 | 18min | 2 tasks | 4 files |
| Phase 10-tests-docs P02 | 8min | 2 tasks | 2 files |
| Phase 10-tests-docs P01 | 10 | 2 tasks | 1 files |
| Phase 11-ircc-immigration P01 | 8min | 1 tasks | 4 files |
| Phase 11-ircc-immigration P02 | 4min | 2 tasks | 7 files |
| Phase 11-ircc-immigration P03 | 18min | 2 tasks | 4 files |
| Phase 11-ircc-immigration P04 | 8min | 2 tasks | 5 files |
| Phase 12-ontario-government-open-data P01 | 15min | 1 tasks | 7 files |
| Phase 12-ontario-government-open-data P02 | 3min | 2 tasks | 4 files |
| Phase 13-toronto-municipal-government-open-data P01 | 5min | 2 tasks | 8 files |
| Phase 13-toronto-municipal-government-open-data P02 | 5min | 2 tasks | 4 files |
| Phase 40-mcp-prompts-and-resources P01 | 10min | 2 tasks | 5 files |
| Phase 40-mcp-prompts-and-resources P02 | 18min | 2 tasks | 9 files |
| Phase 40-mcp-prompts-and-resources P03 | 12min | 2 tasks | 12 files |
| Phase 40-mcp-prompts-and-resources P04 | 12min | 2 tasks | 13 files |
| Phase 40-mcp-prompts-and-resources P05 | 4min | 2 tasks | 3 files |
| Phase 14-york-region-municipal-government-open-data P01 | 8min | 2 tasks | 9 files |
| Phase 14-york-region-municipal-government-open-data P02 | 8min | 2 tasks | 2 files |
| Phase 14-york-region-municipal-government-open-data P03 | 10min | 2 tasks | 7 files |
| Phase 15-british-columbia-government-open-data P01 | 8min | 3 tasks | 18 files |
| Phase 15-british-columbia-government-open-data P02 | 5min | 2 tasks | 5 files |
| Phase 15-british-columbia-government-open-data P03 | 45min | 2 tasks | 5 files |
| Phase 15-british-columbia-government-open-data P04 | 10min | 2 tasks | 7 files |
| Phase 15-british-columbia-government-open-data P05 | 7min | 2 tasks | 5 files |
| Phase 16-quebec-government-open-data P01 | 5min | 2 tasks | 15 files |
| Phase 16-quebec-government-open-data P03 | 39 | 2 tasks | 6 files |
| Phase 16-quebec-government-open-data P04 | 28 | 4 tasks | 12 files |
| Phase 16-quebec-government-open-data P05 | 8min | 3 tasks | 7 files |
| Phase 16-quebec-government-open-data P06 | 9min | 3 tasks | 5 files |
| Phase 16-quebec-government-open-data P07 | 8min | 3 tasks | 3 files |
| Phase 16-quebec-government-open-data P08 | 2min | 2 tasks | 3 files |
| Phase 17-alberta-government-open-data P02 | 6min | 2 tasks | 4 files |
| Phase 17-alberta-government-open-data P03 | 5min | 2 tasks tasks | 4 files files |
| Phase 17-alberta-government-open-data P05 | 7 min | 2 tasks | 4 files |
| Phase 17-alberta-government-open-data P04 | 13min | 2 tasks | 4 files |
| Phase 17 P06 | 4min | 2 tasks | 4 files |
| Phase 17-alberta-government-open-data P07 | 6min | 2 tasks | 4 files |
| Phase 17-alberta-government-open-data P08 | 6min | 2 tasks | 3 files |
| Phase 17 P09 | 392 | 3 tasks | 6 files |
| Phase 18-manitoba-government-open-data P01 | 10min | 3 tasks | 13 files |
| Phase 18-manitoba-government-open-data P02 | 6min | 2 tasks | 4 files |
| Phase 18-manitoba-government-open-data P03 | 8min | 2 tasks | 4 files |
| Phase 18-manitoba-government-open-data P04 | 5min | 2 tasks | 4 files |
| Phase 18-manitoba-government-open-data P05 | 15min | 2 tasks | 4 files |
| Phase 18-manitoba-government-open-data P06 | 4min | 2 tasks | 4 files |
| Phase 18-manitoba-government-open-data P07 | 7min | 2 tasks | 3 files |
| Phase 18-manitoba-government-open-data P08 | 7min | 2 tasks | 7 files |
| Phase 18-manitoba-government-open-data P09 | 4min | 3 tasks | 3 files |
| Phase 19-saskatchewan-government-open-data P01 | 10min | 3 tasks | 15 files |
| Phase 19-saskatchewan-government-open-data P02 | 6min | 2 tasks | 4 files |
| Phase 19-saskatchewan-government-open-data P03 | 18min | 2 tasks | 4 files |
| Phase 19-saskatchewan-government-open-data P04 | 6min | 2 tasks | 4 files |
| Phase 19-saskatchewan-government-open-data P05 | 3min | 2 tasks | 4 files |
| Phase 19-saskatchewan-government-open-data P06 | 8min | 2 tasks | 3 files |
| Phase 19-saskatchewan-government-open-data P07 | 15min | 2 tasks | 7 files |
| Phase 20-nova-scotia-government-open-data P01 | 11min | 3 tasks | 15 files |
| Phase 20-nova-scotia-government-open-data P02 | 6min | 2 tasks | 4 files |
| Phase 20-nova-scotia-government-open-data P03 | 5min | 2 tasks | 4 files |
| Phase 20-nova-scotia-government-open-data P04 | 6min | 2 tasks | 4 files |
| Phase 20-nova-scotia-government-open-data P05 | 6min | 2 tasks | 4 files |
| Phase 20-nova-scotia-government-open-data P06 | 8min | 2 tasks | 3 files |
| Phase 20-nova-scotia-government-open-data P07 | 12min | 2 tasks | 7 files |
| Phase 20-nova-scotia-government-open-data P20-08 | 5min | 3 tasks | 5 files |
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 21 P01 | 24min | 4 tasks | 15 files |
| Phase 21 P02 | 35min | 3 tasks | 4 files |
| Phase 21-new-brunswick-government-open-data P03 | 45min | 2 tasks | 3 files |
| Phase 21 P04 | 55min | 3 tasks | 4 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Pre-Phase 7]: Use `aiosqlite==0.22.1` for async SQLite — cleaner than asyncio.to_thread; zero transitive deps
- [Pre-Phase 7]: SQL injection prevention via regex allowlist `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$` must be in place from first commit
- [Pre-Phase 7]: SSL — attempt `truststore` first; fall back to scoped `verify=False` on statcan client only; never touch shared http.py
- [Phase 07-datastore-ssl]: STATCAN_VERIFY=True — certifi validates statcan.gc.ca, no truststore or verify=False needed
- [Phase 07-datastore-ssl]: Scoped client pattern: _make_statcan_client() owns its verify= setting, shared http.py never touched
- [Phase 07-datastore-ssl]: aiosqlite module-level singleton pattern — lazy init in get_db(); was_cached always False for local SQLite I/O
- [Phase 07-datastore-ssl]: IDENTIFIER_RE regex allowlist ^[a-zA-Z_][a-zA-Z0-9_]{0,63}$ rejects SQL metacharacters before any SQL executes
- [Phase 07-datastore-ssl]: Keywords in tool docstrings must be on a single line — multi-line Keywords wrap causes test_quality.py parser to undercount
- [Phase 07-datastore-ssl]: ds_get_schema returns NOT_FOUND for nonexistent tables (empty PRAGMA result = user input error, not system error)
- [Phase 07-datastore-ssl]: Datastore integration test isolation: autouse fixture patches client._db with in-memory connection per test
- [Phase 08-statcan-wds]: _limiter_acquire() is a module-level function to allow patch.object in tests without re-importing
- [Phase 08-statcan-wds]: BM25 index stored as (cubes, avg_dl, df) tuple in cache — single cache entry, statistics computed once
- [Phase 08-statcan-wds]: _flatten_observation shared helper: 4 data functions share identical observation-flattening logic; extracted to private helper to avoid duplication
- [Phase 08-statcan-wds]: get_bulk_vector_data iterates raw list directly without _unwrap: bulk endpoint per-element status envelopes, not outer SUCCESS wrapper
- [Phase 08-statcan-wds]: changed series/cubes return list[dict] not Pydantic models: monitoring endpoints where full schema validation adds cost without benefit
- [Phase 08-statcan-wds]: UPSTREAM_UNAVAILABLE (not UPSTREAM_ERROR) on HTTP 409 — maintenance window is predictable, agents should retry after 08:30 EST
- [Phase 08-statcan-wds]: DimensionMember.parent_member_id: int | None (top-level members have null parentMemberId in real WDS)
- [Phase 08-statcan-wds]: CodeSetEntry.desc_en/desc_fr: str | None (uomCode=0 has null descriptions in real WDS)
- [Phase 09-sdmx-composite]: Cache structure XML text (str) not SDMXStructure object - avoids Pydantic serialization in aiocache
- [Phase 09-sdmx-composite]: SDMX Ref element has no namespace prefix in real XML - use bare Ref fallback after str:Enumeration/Ref search
- [Phase 09-sdmx-composite]: Series key delimiter: try colon first (SDMX-JSON spec) then dot fallback (StatCan observed behavior)
- [Phase 09-sdmx-composite]: sc_get_sdmx_data mutual exclusion enforced at tool layer: lastN + date range check before any network call
- [Phase 09-sdmx-composite]: sc_fetch_vectors_to_store validates table_name via IDENTIFIER_RE before any network call — fail-fast pattern
- [Phase 09-sdmx-composite]: key wins over dimensions in sc_get_sdmx_data to avoid unnecessary structure fetch when raw key provided
- [Phase 10-tests-docs]: StatCan credit placed in Statistics Canada section as blockquote, not in the README header
- [Phase 10-tests-docs]: Cross-module SQL examples show full 3-phase workflow: fetch from API, store to datastore, JOIN in SQL
- [Phase 10-tests-docs]: Range-based WDS tools assert shape only (not count) — releases may be absent for fixed historical date ranges
- [Phase 10-tests-docs]: CPI Canada coordinate '1.1.0.0.0.0.0.0.0.0' confirmed as stable anchor for coord-based WDS integration tests
- [Phase 11-ircc-immigration]: Parser uses pandas when available (better multi-sheet/encoding/types), falls back to openpyxl on ImportError
- [Phase 11-ircc-immigration]: fetch_and_parse caches only successful results; errors propagate from _fetch() — never return [] on failure
- [Phase 11-ircc-immigration]: DATASET_REGISTRY triple-nested dict (dataset, breakdown, lang) -> URL is single source of truth for IRCC module
- [Phase 11-ircc-immigration]: adhoc_pr English-only: lang=fr raises ValueError since no fr key exists in registry for that dataset
- [Phase 11-ircc-immigration]: _fetch_dataset private helper: all 11 IRCC client functions are one-liners delegating to this shared helper
- [Phase 11-ircc-immigration]: Work permits (IMP + TFWP) combined into ircc_get_work_permits(permit_type); Express Entry combined into ircc_get_express_entry(stream) to reduce tool count
- [Phase 11-ircc-immigration]: Year filtering via _filter_by_year checks year/annee/annee/Year column variants for EN/FR XLSX compatibility
- [Phase 11-ircc-immigration]: Last-row-only raw-value guard prevents spurious forward-fill in month header row for Year Total columns
- [Phase 11-ircc-immigration]: Label col suffix (_{n}) added when multiple label cols share a merged header cell to prevent dict key collisions
- [Phase 12-ontario-government-open-data]: ontario: cache key prefix distinguishes Ontario datasets from federal CKAN keys in shared aiocache
- [Phase 12-ontario-government-open-data]: Population projections XLSX has no FR variant — lang parameter accepted for API consistency, same URL used for both languages
- [Phase 12-ontario-government-open-data]: Patch client functions at tools module namespace (mcp_canada.modules.ontario.tools.*) not client module — functions are imported into tools.py namespace
- [Phase 13-toronto-municipal-government-open-data]: GeoJSON .geojson check before .json in fetch_and_parse routing: .geojson ends with json so ordering matters
- [Phase 13-toronto-municipal-government-open-data]: fetch_311_requests two-step: package_show discovers year ZIP URL then downloads — enables year-agnostic URL discovery
- [Phase 13-toronto-municipal-government-open-data]: toronto: cache key prefix distinguishes Toronto datasets from federal CKAN keys in shared aiocache
- [Phase 13-toronto-municipal-government-open-data]: Toronto fetch_organizations takes no lang param — tools.py calls without lang arg (Ontario client differs)
- [Phase 13-toronto-municipal-government-open-data]: GTFS/datastore tools catch generic Exception (not just HTTPStatusError) since ZIP errors are not HTTP errors
- [Phase 40-mcp-prompts-and-resources]: Guided workflow prompts (list[Message]) for multi-step tool chaining; quick lookups (str) for single-tool instructions
- [Phase 40-mcp-prompts-and-resources]: Resources are zero-parameter functions — lang param would promote to ResourceTemplate and remove from resources/list
- [Phase 40-mcp-prompts-and-resources]: StatCan resources use string keys ('1', '5', '9') for frequency/scalar codes matching JSON serialization of integer keys
- [Phase 40-mcp-prompts-and-resources]: statcan_store_and_query prompt is the cross-module flagship: demonstrates sc_fetch_vectors_to_store -> ds_query chain
- [Phase 40-mcp-prompts-and-resources]: ckan_federal_organizations uses org slugs as keys (not display names) — slugs are what the CKAN API organization= parameter accepts
- [Phase 40-mcp-prompts-and-resources]: Guided workflow prompts (list[Message]) for multi-step tool chaining; quick lookups (str) for single-tool instructions — same pattern across all 4 modules
- [Phase 40-mcp-prompts-and-resources]: Drug schedule codes follow Health Canada classification (Prescription/OTC/Schedule I-III/Unscheduled); Nutrient food groups use canonical CNF group IDs (1-25) matching the API's actual group_id values
- [Phase 40-mcp-prompts-and-resources]: Weather prompts.py at top-level weather/ (not in sub-modules) — FileSystemProvider recursively scans so one file avoids duplicate discovery
- [Phase 40-mcp-prompts-and-resources]: IRCC ircc_dataset_list resource maps all 10 dataset keys to tool names — provides complete discovery catalog for agents
- [Phase 40-mcp-prompts-and-resources]: Toronto neighbourhood-list embeds all 140 neighbourhoods inline — avoids HTTP call to retrieve static reference data
- [Phase 40-mcp-prompts-and-resources]: r.uri on FastMCP ResourceInfo is AnyUrl not str — must str(r.uri) before string containment tests in integration tests
- [Phase 14-york-region-municipal-government-open-data]: Hub Search API uses /api/search/v1/collections/all/items (NOT /api/v2/datasets which 404s)
- [Phase 14-york-region-municipal-government-open-data]: NoPortalError (not ValueError) for municipalities without public ArcGIS Hub portals — enables typed catch in tools
- [Phase 14-york-region-municipal-government-open-data]: PORTAL_URLS has 10 keys: 4 real URLs + 5 None + 1 census-only Whitchurch-Stouffville hub
- [Phase 14-york-region-municipal-government-open-data]: query_feature_service passes returnGeometry=false when include_geometry=False — reduces response payload
- [Phase 14-york-region-municipal-government-open-data]: _call_client private async helper centralises all error handling across all 27 york_region tools
- [Phase 14-york-region-municipal-government-open-data]: Dispatch tools (get_public_health, get_census_demographics, get_waste_data) return make_error('INVALID_INPUT') with valid= list for invalid enum values
- [Phase 14-york-region-municipal-government-open-data]: max_records silently clamped to 5000 in all query_features tools, documented in docstring
- [Phase 14-york-region-municipal-government-open-data]: york_region_quick_dataset_search takes query: str + lang — quick lookup prompts can accept content params alongside lang
- [Phase 14-york-region-municipal-government-open-data]: York Region resources embed bilingual content inline (name_en/name_fr per entry) — avoids lang param which would convert FunctionResource to ResourceTemplate
- [Phase 15-british-columbia-government-open-data]: shared/ogc.py uses response.content (bytes) for _parse_geojson — satisfies no-json-on-400-path rule and reuses existing _parse_geojson(bytes) signature
- [Phase 15-british-columbia-government-open-data]: typeNames (plural) serialization from type_name (singular) Python kwarg — WFS 2.0 spec requirement documented with inline comment
- [Phase 15-british-columbia-government-open-data]: CLIMATE_STATIONS_LAYER intentionally aliases WEATHER_STATIONS_LAYER — same BCGW layer, climate-oriented docstring for the 15th curated bc_ tool
- [Phase Phase 15]: _api_get mirrors Ontario CKAN pattern: BASE_URL + path, envelope unwrap, raises HTTPStatusError on success=False
- [Phase Phase 15]: bc: prefix isolates BC cache keys from Ontario/Toronto/federal CKAN keys in shared aiocache
- [Phase Phase 15]: _compute_queryable_via_wfs is synchronous pure helper — returns (bool, object_name|None) from resource list
- [Phase Phase 15]: bc_list_categories surfaces tags not groups — BC CKAN group_list returns HTTP 403 (RESEARCH Pitfall 7)
- [Phase Phase 15]: _build_cql upper-cases all field names to match BCGW uppercase convention (RESEARCH Pitfall 6)
- [Phase Phase 15-british-columbia-government-open-data]: Two private helpers _append_gte/_append_like added to tools.py for >= and LIKE CQL clauses — _build_cql handles equality only, helpers compose on top
- [Phase Phase 15-british-columbia-government-open-data]: bc_get_water_wells 130K-record guard returns INVALID_INPUT before any network call when no filter provided (Pitfall 5)
- [Phase Phase 15]: bc_quick_dataset_search and bc_wildfire_status_now are parameter-free quick lookups (return str instructions) — agents supply their own parameters; contrast with york_region_quick_dataset_search which takes query:str
- [Phase Phase 15]: BC resources.py uses async def for consistency with York Region pattern — both async and sync def work with FastMCP FunctionResource
- [Phase Phase 15]: WFS/OGC documented as third portal technology in CLAUDE.md alongside CKAN and ArcGIS Hub — shared/ogc.py reusable for Quebec and other provinces
- [Phase 15-british-columbia-government-open-data]: BC _api_get fix: treat shared api_get return as parsed dict; drop .raise_for_status()/.json(); check envelope.get('success') directly
- [Phase 15-british-columbia-government-open-data]: Water wells bilingual guard: inline lang=='en' ternary (not t() import) — matches prompts.py convention, avoids first t() production import for one-off message
- [Phase 16-quebec-government-open-data]: Quebec module is CKAN-only: no secondary geospatial portal; Géoportail Québec deferred
- [Phase 16-quebec-government-open-data]: MTQ WFS CSV-only: always outputformat=csv — GeoJSON returns HTTP 400 (MapServer json.tmpl missing)
- [Phase 16-quebec-government-open-data]: DQ metadata French-primary: title/notes French-only, no title_translated; lang affects error messages only
- [Phase 16-quebec-government-open-data]: SOPFEU/Hydro-Québec deferred: not on DQ CKAN; replaced by road events + electricity production tools
- [Phase 16]: _api_get return type is Any (not dict[str, Any]): CKAN org/group list returns lists at result level
- [Phase 16]: group_list for categories: DQ has 10 thematic groups; tag_list returns 4200+ noisy tags
- [Phase 16-quebec-government-open-data]: Bridge structures filter guard in tool layer only (not client) — client can be called without filters; tool enforces the guard for safe agent use
- [Phase 16-quebec-government-open-data]: fetch_road_conditions returns [] on WFS exception (graceful degradation) — LOW-confidence MTQ endpoint; empty list preferred over always-UPSTREAM_ERROR
- [Phase 16-quebec-government-open-data]: ArcGIS REST for IQA calls api_get directly (not shared/arcgis_hub.py) — simple GET endpoint, no pagination or FeatureServer-specific handling needed
- [Phase 16-quebec-government-open-data]: Metadata-only tools return model_dump() directly — no additional parsing layer for SHP/GPKG archives that fetch_and_parse cannot handle
- [Phase 16-quebec-government-open-data]: quebec_active_fires_now prompt explicitly redirects to sopfeu.qc.ca — SOPFEU confirmed not registered on Données Québec
- [Phase 16-quebec-government-open-data]: Resource tests converted from sync+asyncio.get_event_loop() to async def — Python 3.14 raises RuntimeError for get_event_loop() without a running loop in main thread
- [Phase 16-quebec-government-open-data]: fetch_and_parse query-string format detection: urllib.parse.parse_qs with case-insensitive key normalization — zero new deps, backward-compatible with path-suffix detection
- [Phase 16-quebec-government-open-data]: fetch_electricity_data 3-tuple (rows, source_url, was_cached): bundled in _fetch() tuple so single cache entry holds both; cache key uses v2 suffix to invalidate stale entries
- [Phase 16-quebec-government-open-data]: Hydro-Québec historique-production-consommation package is XLSX-only (years 2018-2021; 2020 empty URL): format matcher expanded from CSV-only to (CSV, XLSX, XLS)
- [Phase 16-quebec-government-open-data]: _normalize_route zfill(5): 'A-20' -> '00020'; nom_route digit-substring fallback for WFS data mismatch
- [Phase 16-quebec-government-open-data]: fetch_road_conditions mapper uses _normalize_key output: 'numerosegment' not 'NumeroSegment'; 'envigueurdepuis' not 'DateEtHeureCondition'
- [Phase 16-quebec-government-open-data]: SECLEVEL=1 SSLContext scoped to hydroquebec.com in fetch_electricity_data; fetch_and_parse ssl_context param with ssl_flag in cache key
- [Phase 16-quebec-government-open-data]: Quebec int->str coercion: _str_or_none helper lives in quebec/client.py per-mapper; shared _mask_privacy untouched
- [Phase 16-quebec-government-open-data]: _flatten_bridge emits _normalize_route(str(num_route)) so post-parse filter and emitted route_num both use zero-padded form
- [Phase 16-quebec-government-open-data]: _is_real_electricity_row lives in quebec/client.py caller — domain-specific XLSX legend row filter, no shared/parsers.py edit
- [Phase 16-quebec-government-open-data]: Replicate int->str fix: _flatten_population_row.mcode + _flatten_road_work.identifier/chantier_id + _flatten_road_event.identifier (latent same-root-cause bugs)
- [Phase 16]: Removed nom_route substring fallback entirely — exact num_route match is only reliable filter path
- [Phase 17-alberta-government-open-data]: TestSharedApiGetContract patches module-local client.api_get (BC pattern) — achieves same regression guard as shared-layer patch, works with Python from-import semantics
- [Phase 17-alberta-government-open-data]: Alberta fetch_search_datasets composes organization+format filters via space-joined fq (CKAN implicit AND across tokens)
- [Phase 17-alberta-government-open-data]: Hybrid router prefers FeatureServer over MapServer at resource_index==0 (Pitfall 12); explicit non-zero index falls back to literal indexing for agent control
- [Phase 17-alberta-government-open-data]: ST1 column layout: licence_number (0-9), operator (9-35), well_name (35-63), field_code (63-EOL) — derived from fixture, auto-detected via numeric-licence-block rule
- [Phase 17-alberta-government-open-data]: ST3 INVALID_INPUT includes valid=[7 products] in error extras (Pitfall 8); French inline ternary via lang == 'fr'
- [Phase 17-alberta-government-open-data]: No shared/aer.py extraction — AER tools use fetch_and_parse() + direct httpx for ~30 LOC ST1 parsing (reuse threshold not met)
- [Phase 17-alberta-government-open-data]: Plan 05 AHS tools: fetch_* functions return dict payloads (features/count/truncated), double-guard on facility_type (tool INVALID_INPUT + client ValueError), hospital zone filter via case-insensitive Location substring (no polygon containment)
- [Phase 17-alberta-government-open-data]: Wildfire tools use shared WMB module-level limiter (_wmb_limiter) at module scope; 4 fetchers share the 5 r/s TokenBucket; no GeoDiscover wildfire folder calls (Pitfall 3 honored)
- [Phase 17-alberta-government-open-data]: fetch_fire_weather (FWI) dropped — not publicly available on any Alberta portal; replaced by fetch_fire_control_orders surfacing control orders / OHV / forest area boundaries via single category-dispatched tool
- [Phase 17-alberta-government-open-data]: Wave 0 scaffold signatures for fetch_fire_perimeters (dropped year param) and fetch_fire_control_orders (added category param) updated inline during Plan 04 implementation to match plan spec
- [Phase 17]: Plan 06: use _511_get (not _api_get) for 3 Alberta 511 transport tools — 511 returns raw JSON list, not CKAN envelope (Pitfall 6)
- [Phase 17]: Plan 06: MONTHLY 24h TTL for cameras (stable locations), LIVE 5min TTL for events and winter road conditions
- [Phase 17-alberta-government-open-data]: Plan 07: Distinct GeoDiscover api_name per tool (alberta-geodiscover-aqhi/water/parks) for finer envelope source attribution
- [Phase 17-alberta-government-open-data]: Plan 07: WATER_ADVISORY_LAYERS + POPULATION_BREAKDOWN_HINTS dispatch tables live in client.py (implementation detail, not shared constants)
- [Phase 17-alberta-government-open-data]: Plan 07: fetch_population_estimates breakdown Literal aligned to 'annual' (not Wave 0 'cma') — matches research § AB-25 and avoids StatCan CMA overlap
- [Phase 17-alberta-government-open-data]: Plan 08: Kept alberta quick-lookup prompts at lang-only signatures — honors Plan 01 'signatures locked at Wave 0' invariant and matches BC/Quebec precedent
- [Phase 17-alberta-government-open-data]: Plan 08: AB-23 water-licence guidance placed in docs://alberta/wildfire-data-guide as documentation-only — resources too large (87MB+ active, 169MB+ inactive) for alberta_query_dataset; agents directed to external download tools
- [Phase 17]: Phase 17 closed: 24 alberta tools covered by 48 parametrized envelope/lang tests + 11 live-API integration scenarios through MCP Client; coverage 96.84%; AB-XX matrix 1-26 implemented + AB-27 convention compliance verified
- [Phase 18-manitoba-government-open-data]: RIVER_CONDITIONS_CSV_URL replaces FS URL — spike proved River Conditions web app uses live CSV (not FeatureServer); Plan 03 uses fetch_and_parse
- [Phase 18-manitoba-government-open-data]: HOG_PRICES_FS_URL=None typed as str|None — hog prices service not found in mMUesHYPkXjaFGfS org; Plan 04 investigates
- [Phase 18-manitoba-government-open-data]: Manitoba 511 key GATED — account signup + explicit key request; tools return NOT_CONFIGURED via Five11NotConfigured exception pattern
- [Phase 18-manitoba-government-open-data]: fetch_query_dataset takes feature_server_url directly (not package_id) — no CKAN layer in Manitoba; agents have URL from get_dataset_details
- [Phase 18-manitoba-government-open-data]: fetch_organizations/categories derive from Hub search results (unique owners/categories) — Manitoba Hub has no dedicated orgs endpoint
- [Phase 18-manitoba-government-open-data]: _hub_get Hub-JSON contract enforced by TestSharedApiGetContract: never inspects .get('success') — Hub Search returns {features, numberMatched} directly
- [Phase 18-manitoba-government-open-data]: fetch_river_stations uses fetch_and_parse(RIVER_CONDITIONS_CSV_URL) — spike confirmed no FeatureServer backing the River Conditions web app
- [Phase 18-manitoba-government-open-data]: Empty flood alert {features:[]} is a valid success response — no alert period is the normal off-season state; tool must NOT convert this to an error
- [Phase 18-manitoba-government-open-data]: WATERWAY_TYPES validation in client (ValueError) — tool catches and maps to INVALID_INPUT with valid= list
- [Phase 18-manitoba-government-open-data]: Drought bbox filter uses api_get direct (not arcgis_hub.query_feature_service) — geometry envelope params not exposed by query_feature_service; server-side Manitoba bbox intersection via /0/query endpoint
- [Phase 18-manitoba-government-open-data]: HOG_PRICES_FS_URL=None degrades to empty success with note field — livestock='hog' returns {features:[],count:0,note:'...'} not UPSTREAM_ERROR; valid=['cattle','hog'] preserved in INVALID_INPUT
- [Phase 18-manitoba-government-open-data]: fetch_fisheries_data focuses on 9 of 26 available fields (ID,Name,SurfaceArea,AvgDepth,SecchiDepth,FishingDivision,Species,Regulations,BoatLaunch) — reduces agent context cost
- [Phase 18-manitoba-government-open-data]: manitoba_get_health_facilities passes rha= as community= to client — no dedicated RHA field in layer; Community_Name LIKE filter covers all RHA queries
- [Phase 18-manitoba-government-open-data]: Emergency_Department_Availabili is the actual truncated ArcGIS field name — matched exactly as spike-confirmed for emergency_only=True filter
- [Phase 18-manitoba-government-open-data]: Manitoba 511 key GATED (confirmed spike): tools return NOT_CONFIGURED via Five11NotConfigured; live integration deferred until free key confirmed
- [Phase 18-manitoba-government-open-data]: Plan 06: area_name filter for winter roads is client-side (511 API has no server-side area param); camera locations cached at CACHE_TTL_META (24h)
- [Phase 18-manitoba-government-open-data]: Resources have ZERO function parameters (no lang) — lang param would promote to ResourceTemplate and drop from resources/list
- [Phase 18-manitoba-government-open-data]: data://manitoba/major-rivers includes Red River Floodway as a sixth entry — critical flood infrastructure reference
- [Phase 18]: ALL_MANITOBA_TOOLS count=20 (5+3+4+5+3) matches tools.py __all__; 511 NOT_CONFIGURED integration test pops env var to guarantee deterministic result without needing real key
- [Phase 18-manitoba-government-open-data]: Manitoba Hub Search uses OGC API Records params (limit/startindex) not ArcGIS-REST (num/start); blank q= omitted (not sent empty); startindex omitted when 0
- [Phase 19-saskatchewan-government-open-data]: startindex param fix is in shared/arcgis_hub.py:search_hub_datasets (not per-module workaround); Manitoba fetch_search_datasets builds params directly so no double-application
- [Phase 19-saskatchewan-government-open-data]: WSA_RESERVOIRS_LAYER=26 confirmed by live probe; Petroleum FS HTTP 400 was transient (HTTP 200 live); WSA Water Quality layer 19 has 24 stations (not 0); both remain per plan scope (deferred/not curated)
- [Phase 19-saskatchewan-government-open-data]: 3 module-level limiters in client.py (_hub_limiter/_wsa_limiter/_spsa_limiter) for 3 separate rate groups (Saskatchewan has most fragmented portal architecture)
- [Phase 19-saskatchewan-government-open-data]: OGC params: limit/startindex, omit startindex when 0, omit q when blank; param-regression asserts call_args[0][1] directly
- [Phase 19-saskatchewan-government-open-data]: auto-router: FeatureServer → query_feature_service; CSV/JSON/GeoJSON/XLSX → fetch_and_parse; else metadata-only note
- [Phase 19-saskatchewan-government-open-data]: api_name='saskatchewan-geohub' for all 5 discovery tools; NOT_FOUND on ValueError; UPSTREAM_ERROR on HTTPStatusError
- [Phase 19-saskatchewan-government-open-data]: CACHE_TTL_ANNUAL (7d) for crop yields — annual estimates; minerals/elevators use CACHE_TTL_META (24h)
- [Phase 19-saskatchewan-government-open-data]: Double-guard on crop region + mineral: tool pre-checks enum tuple before client call; client raises ValueError as secondary guard (mirrors Alberta ST3 pattern)
- [Phase 19-saskatchewan-government-open-data]: Crop yields tool docstring notes PDF reports are NOT machine-readable — FeatureServer is the substitute (placed where agents see it)
- [Phase 19-saskatchewan-government-open-data]: fetch_fire_bans validates ban_scope before calling arcgis_hub (double-guard: tool INVALID_INPUT + client ValueError) — mirrors Alberta ST3 + mineral dispatch patterns
- [Phase 19-saskatchewan-government-open-data]: api_name='saskatchewan-spsa-firebans' for fire bans (distinguishes SPSA server from Hub in _meta envelope); historic wildfires + air quality use 'saskatchewan-geohub'
- [Phase 19-saskatchewan-government-open-data]: Empty fire bans payload explicitly tested as valid success (count=0, _meta envelope) not error — same lesson as Manitoba flood alerts
- [Phase 19-saskatchewan-government-open-data]: api_name='saskatchewan-wsa' for WSA tools (distinguishes WSA org from Hub in _meta envelope)
- [Phase 19-saskatchewan-government-open-data]: WSA_RESERVOIRS_LAYER=26 used as constant in client call and api_url; layer 26 pinned via call_args assertion in test
- [Phase 19-saskatchewan-government-open-data]: Message.content is TextContent (not str) — access via m.content.text in tests (matches Manitoba pattern)
- [Phase 19-saskatchewan-government-open-data]: Resources are ZERO-parameter — lang param would promote to ResourceTemplate and drop from resources/list; deferred domains (transport key-gated, health no public FeatureServer) surfaced in portal-guide and health-regions data resource
- [Phase 19-saskatchewan-government-open-data]: Literal enum (mineral) caught at Pydantic/MCP layer (ToolError) before tool INVALID_INPUT handler — both outcomes are correct invalid-input rejection
- [Phase 19-saskatchewan-government-open-data]: ALL_SASKATCHEWAN_TOOLS has 13 entries matching __all__ in tools.py (5+3+3+2); plan says 14 but code is authoritative
- [Phase 20-nova-scotia-government-open-data]: shared/socrata.py is the 4th portal client (CKAN/ArcGIS Hub/OGC WFS/Socrata SODA); httpx injection, parsed dicts, no cached_fetch/get_limiter inside
- [Phase 20-nova-scotia-government-open-data]: ACTIVE_ADVISORY_FILTER = 'date_advisory_removed IS NULL' (spike-confirmed; empty-string = type-mismatch error on date column)
- [Phase 20-nova-scotia-government-open-data]: AMI chronic disease uses health_zone (→zone) and has no sex field; hypertension uses hypertension_count+prevalence_rate (non-standard); NovaScotiaChronicDiseaseRow uses nullable fields
- [Phase 20-nova-scotia-government-open-data]: fetch_categories uses q='' + client-side domain_category aggregation (never categories= param — confirmed broken, returns resultSetSize=0)
- [Phase 20-nova-scotia-government-open-data]: include_geometry=False + select=None leaves select as None in fetch_query_dataset (documented: Socrata returns all fields including the_geom; agent must use $select to exclude)
- [Phase 20-nova-scotia-government-open-data]: api_name='nova-scotia-socrata' used for all 5 discovery tools in make_response envelope
- [Phase 20-nova-scotia-government-open-data]: Defensive the_geom strip applied at both client and tool layers for marine leases — belt-and-suspenders; $select is primary, row strip handles any API anomaly
- [Phase 20-nova-scotia-government-open-data]: CACHE_TTL_ANNUAL (7d) for aquaculture production (annual dataset); leases/licenses/hatchery use CACHE_TTL_META (24h)
- [Phase 20-nova-scotia-government-open-data]: Empty boil-water advisory list (active_only=True returning []) is make_response with count=0 — mirrors Manitoba flood-alert and Saskatchewan fire-ban patterns
- [Phase 20-nova-scotia-government-open-data]: Protected areas (ticv-5du5) the_geom excluded via explicit $select + belt-and-suspenders row strip at both client and tool layers
- [Phase 20-nova-scotia-government-open-data]: Air quality tool (ns_get_air_quality_stations) is station-catalog-only; 20+ per-station pollutant datasets routed to ns_query_dataset; directs to docs://ns/air-quality-guide (Plan 06)
- [Phase 20-nova-scotia-government-open-data]: fetch_health_facilities normalizes both hospital and LTC rows to common shape; facility_category=facility_type; beds=None for hospitals
- [Phase 20-nova-scotia-government-open-data]: _normalize_zone_field accepts disease param for CHRONIC_DISEASE_ZONE_FIELD lookup; zone filter applied on source field name before normalization
- [Phase 20-nova-scotia-government-open-data]: vital stats field is 'counties' (not 'county') UPPERCASE matching r794-fttm dataset schema (Pitfall 4)
- [Phase 20-nova-scotia-government-open-data]: @prompt/@resource count tests use __all__ (not isinstance check) — decorators return callables not Prompt/Resource instances in fastmcp
- [Phase 20-nova-scotia-government-open-data]: docs://ns/socrata-guide is the canonical SODA/SoQL how-to for all agents (first Socrata portal); portal-guide documents deferred transport/511 and novagis ArcGIS Hub
- [Phase 20-nova-scotia-government-open-data]: ALL_NS_TOOLS has 16 entries (code is authoritative over plan spec of 17; same pattern as SK 13 vs planned 14)
- [Phase 20-nova-scotia-government-open-data]: length_of_advisory_in_days is the actual Socrata column name (not length_of_advisory); live 400 unmasked by integration test
- [Phase 20-nova-scotia-government-open-data]: Socrata added as 4th Portal Technology in CLAUDE.md; shared/socrata.py documented for reuse by future Socrata portals (PEI, NB)
- [Phase 20-nova-scotia-government-open-data]: fetch_health_facilities: per-dataset SoQL (HOSPITAL_SELECT/LTC_SELECT) for incompatible raw Socrata schemas; county filter hospital-only; post-fetch normalization via _normalize_hospital_row/_normalize_ltc_row
- [Phase ?]: [Phase 21-01]: Checkpoint option-a selected — gnb.socrata.com joins discovery via two new nb_ tools reusing shared/socrata.py; D-01 federal-CKAN discovery stays locked
- [Phase ?]: [Phase 21-01]: nb_get_provincial_parks and nb_get_mineral_occurrences dropped to the long tail (reachable via nb_query_geonb_layer) to hold the 22-tool budget after adding the two Socrata tools
- [Phase ?]: [Phase 21-01]: All 11 curated GeoNB layer ids in 21-RESEARCH.md live-CONFIRMED in 21-SPIKE.md — zero constants.py corrections needed
- [Phase ?]: [Phase 21-01]: Added a fourth module-level rate limiter (_socrata_limiter) since gnb.socrata.com is a fourth upstream surface introduced by the checkpoint decision
- [Phase ?]: Checkpoint option-a (gnb.socrata.com) implemented in 21-02: two new nb_ tools reuse shared/socrata.py verbatim, zero new dependencies
- [Phase ?]: tools.ALL_NB_TOOLS aliases constants.ALL_NB_TOOL_NAMES directly (not a manually-grown list) so the two files can never silently drift across Plans 02-06
- [Phase ?]: 21-03: nb_crown_land_report routes checkpoint-dropped tools (mineral occurrences, provincial parks) exclusively through nb_get_geonb_service_layers + nb_query_geonb_layer, never as standalone tool names
- [Phase ?]: 21-03: data://nb/geonb-services classifies all 62 GeoNB services as curated=9/excluded=18/long_tail=35 post-checkpoint (mineral occurrences and provincial parks moved from curated to long_tail)
- [Phase ?]: 21-04: FILTER_REQUIRED_TOOLS guard implemented as a single reusable _require_any_filter client helper (not a wetlands-only inline check) so Plan 05's nb_get_parcels/nb_get_civic_addresses can reuse it directly

### Roadmap Evolution

- Phase 11 added: IRCC Immigration — fetch and parse IRCC open data XLSX files (PR by country, province, category; study permits)
- Phase 12 added: Ontario Government Open Data
- Phase 13 added: Toronto Municipal Government Open Data
- Phase 14 added: York Region Municipal Government Open Data
- Phase 15 added: British Columbia Government Open Data
- Phase 16 added: Quebec Government Open Data
- Phase 17 added: Alberta Government Open Data
- Phases 18-26 added: Remaining provinces and territories (MB, SK, NS, NB, NL, PE, NT, YT, NU)
- Phases 27-34 added: Major municipalities (Montreal, Vancouver, Calgary, Edmonton, Ottawa, Winnipeg, Halifax, Mississauga)
- Phases 35-39 added: Regional municipalities (Peel, Durham, Halton, Waterloo, Metro Vancouver)
- Phase 40 added: MCP Prompts and Resources — workflow prompts for guided data exploration, static resources for reference data across all modules
- Phase 20.1 inserted after Phase 20: Remove UPSTREAM_ERROR escape-hatch pattern from all provincial integration tests (MB/SK/AB/QC/NS) and re-run live integration to surface masked upstream failures before pushing Phase 20 (URGENT)
- Phase 20.2 inserted after Phase 20.1: Normalize tool error handling and guard malformed upstream JSON — root cause of a masking class surfaced by Codex review on PR #2; sequenced before Phase 21 so ~19 future modules inherit the correct handler shape
- Phase 20.3 inserted after Phase 20.2: Route every shared portal client through the JSON decode guard — 20.2 fixed api_get only, leaving ArcGIS Hub, OGC WFS and Socrata exposed; 5 tools reproducibly returned INVALID_INPUT for an upstream outage
- Phase 20.4 inserted after Phase 20.3: Invert the ValueError default — root cause of all four Codex findings across PRs 2/3/4; caller error becomes opt-in via shared/errors.py markers

### Pending Todos

- [research] Research cross-Canada ER wait times datasets — `.planning/todos/pending/2026-04-12-research-cross-canada-er-wait-times-datasets.md`

### Blockers/Concerns

- [Phase 7]: SSL resolution outcome is empirical — truststore may fail in CI; decision protocol defined in STACK.md but outcome unknown until live endpoint test
- [Phase 8]: WDS 25 req/s limit + asyncio.gather burst could trigger rate limits even at 20 req/s TokenBucket — monitor during integration testing
- [Phase 9]: StatCan SDMX structure+json Accept header support unverified; may need stdlib XML parsing for structure queries
- [Quick-1 finding]: Live integration suite surfaced 17 PRE-EXISTING failures in out-of-scope modules (NOT MB/SK/AB/QC/NS) — BOC exchange rates (4, data["data"] shape→dict-by-series), Toronto TTC GTFS (2, UPSTREAM_ERROR) + cross-module (1, ReadTimeout), StatCan coord (2, null-field Pydantic) + bulk_vector (1, dict-vs-list drift), SDMX data_last_n (1, JSON parse), IRCC invalid_breakdown (1) + cross-module (1), York Region shape (3, dict-vs-list drift). Deferred to separate investigation.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 1 | Remove UPSTREAM_ERROR escape-hatch pattern from provincial integration tests and re-run live integration | 2026-06-17 | 2bdf450 | [1-remove-upstream-error-escape-hatch-patte](./quick/1-remove-upstream-error-escape-hatch-patte/) |

## Session Continuity

Last session: 2026-07-30T17:16:59.442Z
Stopped at: Completed 21-04-PLAN.md
Resume file: None
