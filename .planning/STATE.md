---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Statistics Canada + Datastore
status: planning
stopped_at: Completed 16-04-PLAN.md
last_updated: "2026-04-11T23:47:20.125Z"
last_activity: 2026-04-07 — Roadmap created for v1.1 milestone
progress:
  total_phases: 34
  completed_phases: 11
  total_plans: 35
  completed_plans: 35
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** An agent can combine data from any Canadian government source in a single SQL query — turning isolated APIs into one queryable data platform.
**Current focus:** Phase 7 — Datastore + SSL

## Current Position

Phase: 7 of 10 (Datastore + SSL)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-04-07 — Roadmap created for v1.1 milestone

Progress: [░░░░░░░░░░] 0%

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

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 7]: SSL resolution outcome is empirical — truststore may fail in CI; decision protocol defined in STACK.md but outcome unknown until live endpoint test
- [Phase 8]: WDS 25 req/s limit + asyncio.gather burst could trigger rate limits even at 20 req/s TokenBucket — monitor during integration testing
- [Phase 9]: StatCan SDMX structure+json Accept header support unverified; may need stdlib XML parsing for structure queries

## Session Continuity

Last session: 2026-04-11T23:47:20.121Z
Stopped at: Completed 16-04-PLAN.md
Resume file: None
