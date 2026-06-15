# Roadmap: mcp-canada

## Milestones

- ✅ **v1.0 MVP** - Phases 1-6 (shipped 2026-04-07)
- 🚧 **v1.1 Statistics Canada + Datastore** - Phases 7-10 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-6) - SHIPPED 2026-04-07</summary>

Phases 1-6 delivered 7 federal API modules (Bank of Canada, Open Parliament, Recalls, Drug Database, CKAN, Nutrient File, Weather/Climate), BM25 tool discovery, bilingual support, and multi-platform install. 81 tools total.

</details>

### 🚧 v1.1 Statistics Canada + Datastore (In Progress)

**Milestone Goal:** An agent can combine data from any Canadian government source in a single SQL query — turning 7 isolated APIs into one queryable data platform.

- [x] **Phase 7: Datastore + SSL** - SQLite persistence layer and StatCan SSL strategy resolved (completed 2026-04-07)
- [x] **Phase 8: StatCan WDS** - All WDS discovery, series, data, and monitoring tools live (completed 2026-04-07)
- [ ] **Phase 9: SDMX + Composite** - Server-side filtered queries and fetch-and-store bridge complete
- [x] **Phase 10: Tests + Docs** - Integration test coverage and README updated (completed 2026-04-08)

## Phase Details

### Phase 7: Datastore + SSL
**Goal**: Agents can persist any data to a local SQLite store and the StatCan SSL strategy is decided before any statcan client code is written
**Depends on**: Nothing (no external API dependency; SSL investigation is empirical)
**Requirements**: DS-01, DS-02, DS-03, DS-04, DS-05, DS-06, DS-07, DS-08, INF-01
**Success Criteria** (what must be TRUE):
  1. Agent can create a named table, insert rows, run SELECT queries, list tables, inspect schema, and drop a table — all without blocking the event loop
  2. Agent-supplied table and column names containing SQL metacharacters are rejected with a structured error before any SQL executes
  3. StatCan HTTP client uses either truststore-based cert resolution or a scoped verify=False limited strictly to the statcan module — never the shared lifespan client
  4. `aiosqlite` is listed in pyproject.toml; existing `uvx mcp-canada` invocation still works with no new mandatory configuration
**Plans:** 3/3 plans complete

Plans:
- [ ] 07-01-PLAN.md — Datastore module infrastructure: constants, schemas, async SQLite client, identifier validation, --ephemeral flag
- [ ] 07-02-PLAN.md — Datastore tools (6 @tool functions) + unit tests + integration tests
- [ ] 07-03-PLAN.md — StatCan SSL probe + statcan module stub with _make_statcan_client factory

### Phase 8: StatCan WDS
**Goal**: Agents can discover, explore, and retrieve Statistics Canada time series data through all WDS REST endpoints with proper caching, rate limiting, and bilingual support
**Depends on**: Phase 7 (SSL strategy decided; datastore available for composite testing in Phase 9)
**Requirements**: SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-09, SC-13, SC-14, INF-02, INF-03, INF-04, INF-05
**Success Criteria** (what must be TRUE):
  1. Agent can search 80,000+ Statistics Canada tables by keyword and receive ranked results (top 20 max)
  2. Agent can retrieve full dimension metadata for a productId and decode all numeric code fields (frequency, units, scalar factor, status) into human-readable labels
  3. Agent can fetch the latest N observations for a vector (by vectorId or productId+coordinate), retrieve historical data by date range, and fetch multiple vectors simultaneously
  4. Agent can list series and cubes that changed on a specific date, enabling change-monitoring workflows
  5. All StatCan tools respect the 20 req/s rate limit, apply tiered TTL caching (cube list 1hr, metadata 24hr, code sets 7d, observations 1hr), and return bilingual responses
**Plans:** 3/3 plans complete

Plans:
- [ ] 08-01-PLAN.md — Constants, schemas, BM25 search, getCubeMetadata, getCodeSets client functions + tests
- [ ] 08-02-PLAN.md — Series info, data retrieval, and change monitoring client functions + tests
- [ ] 08-03-PLAN.md — All 11 sc_ tool functions + integration tests through MCP Client

### Phase 9: SDMX + Composite
**Goal**: Agents can apply server-side dimension filters via SDMX for large tables and store multi-series fetches directly to the shared datastore in a single tool call
**Depends on**: Phase 7 (datastore), Phase 8 (WDS tools — productIds and coordinate structures needed to test SDMX filtering)
**Requirements**: SC-10, SC-11, SC-12, SC-15
**Success Criteria** (what must be TRUE):
  1. Agent can retrieve the dimension structure (codelists) for any StatCan table via SDMX
  2. Agent can retrieve server-side filtered observations using SDMX key syntax with date range or lastN support — but not both simultaneously (mutual exclusion enforced)
  3. Agent can fetch multiple vectors for a date range and have results written to the shared datastore in one tool call, enabling subsequent cross-module SQL queries
**Plans:** 1/2 plans executed

Plans:
- [ ] 09-01-PLAN.md — SDMX client layer: constants, schemas, 3 async client functions (structure/data/vector), unit tests
- [ ] 09-02-PLAN.md — SDMX + composite tools (4 @tool functions), unit tests, integration tests through MCP Client

### Phase 10: Tests + Docs
**Goal**: All new tools are covered by integration tests through the MCP Client layer and the README accurately reflects the expanded tool catalog
**Depends on**: Phase 9 (all tool surfaces must exist before integration sweep)
**Requirements**: INF-06, INF-07, INF-08, INF-09
**Success Criteria** (what must be TRUE):
  1. Unit test coverage for all new code is at or above 95% as reported by pytest-cov
  2. Every new tool has at least one integration test scenario that calls it through the MCP Client layer (not client functions directly) and asserts on response shape
  3. README tool catalog lists all new statcan and datastore tools with accurate descriptions and updated tool count
  4. EXAMPLES.md contains at least one end-to-end example showing cross-module SQL queries combining StatCan and another module's data
**Plans:** 2/2 plans complete

Plans:
- [ ] 10-01-PLAN.md — Integration test audit + coverage verification (INF-06, INF-07)
- [ ] 10-02-PLAN.md — README updates + EXAMPLES.md cross-module SQL examples (INF-08, INF-09)

## Progress

**Execution Order:** 7 → 8 → 9 → 10 (Phase 9 unblocks after both Phase 7 and Phase 8 complete)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 7. Datastore + SSL | 3/3 | Complete   | 2026-04-07 | - |
| 8. StatCan WDS | 3/3 | Complete   | 2026-04-07 | - |
| 9. SDMX + Composite | 1/2 | In Progress|  | - |
| 10. Tests + Docs | 2/2 | Complete    | 2026-04-08 | - |

### Phase 11: Shared File Parsers + IRCC Immigration
**Goal**: Build a shared XLSX/CSV/XLS parser library, then create an IRCC module that uses it to expose 10 actively-updated immigration datasets (150+ files) as clean ircc_ tools
**Depends on**: Phase 7 (datastore), Phase 10 (docs pattern)
**Requirements**: IRCC-01, IRCC-02, IRCC-03, IRCC-04, IRCC-05, IRCC-06, IRCC-07, IRCC-08, IRCC-09
**Success Criteria** (what must be TRUE):
  1. Shared parser can fetch and parse XLSX, CSV, and XLS files from any URL into list[dict] rows
  2. Agent can query permanent residents by country of citizenship, province, and immigration category
  3. Agent can query study permits, work permits, Express Entry, asylum claimants, and operational processing data
  4. IRCC tools handle privacy masking (`--` values), bilingual columns, and multi-sheet workbooks
  5. All IRCC tools follow mcp-canada conventions (envelopes, bilingual, BM25 keywords)
  6. Parsed IRCC data can be stored to the shared datastore for cross-module SQL queries
  7. Any future module can reuse the shared parser to fetch CKAN dataset resources
**Plans:** 4/4 plans complete

Plans:
- [x] 11-01-PLAN.md — Shared file parser library (parsers.py) + openpyxl dependency + unit tests
- [x] 11-02-PLAN.md — IRCC module skeleton: dataset registry, client functions, unit tests
- [x] 11-03-PLAN.md — IRCC tool functions, integration tests, README update
- [ ] 11-04-PLAN.md — Gap closure: IRCC multi-row merged header parsing (UAT blocker)

### Phase 12: Ontario Government Open Data
**Goal**: Agents can search Ontario's 2,946 open datasets (data.ontario.ca), browse ministry organizations, get dataset/resource details, and fetch curated population projections data — reusing the proven CKAN client pattern and shared XLSX parser
**Depends on**: Phase 11 (shared parsers)
**Requirements**: ONT-01, ONT-02, ONT-03, ONT-04, ONT-05, ONT-06, ONT-07, ONT-08
**Success Criteria** (what must be TRUE):
  1. Agent can search Ontario datasets by keyword and get shaped results with bilingual title/description
  2. Agent can get full dataset details, resource details, list organizations, and get portal statistics
  3. Agent can fetch Ontario population projections from the Ministry of Finance XLSX file
  4. All Ontario tools follow mcp-canada conventions (ontario_ prefix, envelopes, bilingual, BM25 keywords)
  5. Ontario tools are discoverable via discover_tools and callable via call_tool through MCP Client
  6. Unit tests at 95%+ coverage; integration tests verify live API through MCP Client layer
**Plans:** 2/2 plans complete

Plans:
- [ ] 12-01-PLAN.md — Ontario module skeleton: constants, schemas, CKAN client layer, population projections parser, unit tests
- [ ] 12-02-PLAN.md — Ontario tool functions, unit tests, integration tests, README update

### Phase 13: Toronto Municipal Government Open Data
**Goal**: Agents can search Toronto's open data catalogue (open.toronto.ca), browse city divisions, get dataset/resource details, and use curated tools for TTC transit (GTFS), neighbourhood profiles, 311 service requests, RentSafeTO evaluations, and short-term rentals — with new shared GeoJSON/JSON parsers
**Depends on**: Phase 12 (Ontario CKAN pattern)
**Requirements**: TOR-01, TOR-02, TOR-03, TOR-04, TOR-05, TOR-06, TOR-07, TOR-08, TOR-09, TOR-10, TOR-11, TOR-12
**Success Criteria** (what must be TRUE):
  1. Shared parsers handle GeoJSON and JSON in addition to CSV/XLSX/XLS
  2. Agent can search Toronto datasets and get shaped results with bilingual title/description
  3. Agent can search TTC stops and routes from parsed GTFS ZIP data
  4. Agent can query neighbourhood census indicators and compare across neighbourhoods
  5. Agent can fetch 311 service requests with year/ward/type/status filters
  6. Agent can query RentSafeTO evaluations and short-term rental registrations
  7. All Toronto tools follow mcp-canada conventions (toronto_ prefix, envelopes, bilingual, BM25 keywords)
  8. Unit tests at 95%+ coverage; integration tests verify live API through MCP Client layer
**Plans:** 2/2 plans complete

Plans:
- [ ] 13-01-PLAN.md — Shared GeoJSON/JSON parsers + Toronto module skeleton: constants, schemas, client layer, unit tests
- [ ] 13-02-PLAN.md — Toronto tool functions, unit tests, integration tests, README update

### Phase 14: York Region Municipal Government Open Data

**Goal**: Agents can search 4 verified ArcGIS Hub portals in York Region (York Region regional, Markham, Newmarket, Aurora) and use curated tools for YRT/Viva transit, regional roads, public health, 2021 census demographics, and waste management — reusing a new `shared/arcgis_hub.py` client that will template future ArcGIS Hub modules. 6 York Region municipalities without public portals return structured NOT_FOUND.
**Requirements**: YR-01, YR-02, YR-03, YR-04, YR-05, YR-06, YR-07, YR-08, YR-09, YR-10, YR-11, YR-12, YR-13, YR-14
**Depends on**: Phase 13 (shared parsers with _parse_geojson reused)
**Success Criteria** (what must be TRUE):
  1. `shared/arcgis_hub.py` provides a reusable ArcGIS Hub Search API + FeatureServer client (search, query, layer metadata, count)
  2. Agent can search each of 4 verified portals (york_region, markham, newmarket, aurora) via 5 discovery tools per prefix (20 total)
  3. Agent can fetch curated York Region data: YRT/Viva transit stops/routes, regional road network, public health (beach water/hospital/drinking water), 2021 census age/sex/income by Dissemination Area, waste diversion and solid waste sites
  4. Agent can query curated Markham data: civic addresses and SLRN road network
  5. Municipalities without public ArcGIS Hub portals (Vaughan, Richmond Hill, King, East Gwillimbury, Georgina, Whitchurch-Stouffville general data) return structured NOT_FOUND via NoPortalError
  6. Module follows 7-file pattern with prompts.py (4-6 bilingual prompts) and resources.py (6-10 resources covering portal catalog, municipality list, ESRI field naming, census variable reference, ArcGIS query patterns, response templates)
  7. Unit test coverage ≥95%; integration tests verify live ArcGIS Hub endpoints through MCP Client layer
  8. README reflects new tool catalog (~27 tools) and ArcGIS Hub as a second portal technology alongside CKAN
**Plans:** 3/3 plans complete

Plans:
- [ ] 14-01-PLAN.md — Shared ArcGIS Hub client + York Region module skeleton (constants, schemas, client, unit tests)
- [ ] 14-02-PLAN.md — York Region tool functions (20 discovery × 4 portals + 7 curated) + unit tests
- [ ] 14-03-PLAN.md — Prompts, resources, integration tests, README, and REQUIREMENTS.md finalization

### Phase 15: British Columbia Government Open Data

**Goal:** Agents can search the BC Data Catalogue (CKAN + bcgov custom extensions) and query BC Geographic Warehouse geospatial layers via WFS 2.0, with 20 curated bc_ tools (5 discovery + 15 WFS-backed) covering wildfire, forestry, environment, natural resources, health, transportation, and climate. Introduces a reusable `shared/ogc.py` WFS client (third portal tech alongside CKAN and ArcGIS Hub) plus 6 prompts and 7 resources.
**Requirements**: TBD (no explicit REQ IDs yet — delivers on milestone provincial coverage goal)
**Depends on:** Phase 14
**Plans:** 5/5 plans complete

Plans:
- [ ] 15-01-PLAN.md — shared/ogc.py WFS 2.0 client + british_columbia module skeleton + Wave 0 test stubs
- [ ] 15-02-PLAN.md — CKAN client functions + 5 discovery tools (bc_search_datasets, bc_get_dataset_details, bc_query_features, bc_list_organizations, bc_list_categories)
- [ ] 15-03-PLAN.md — _wfs_fetch caching layer + 15 curated WFS tools (wildfire, forestry, environment, mining, health, transportation, climate)
- [ ] 15-04-PLAN.md — 6 prompts + 7 resources + integration tests + README + CLAUDE.md updates

### Phase 16: Quebec Government Open Data

**Goal:** Agents can search the Données Québec CKAN catalogue (1,593 datasets, 139 orgs, 10 thematic groups) and access curated MSSS health, MTQ transport, environment, demographics, and energy data via 18 `quebec_` tools (5 discovery + 13 curated), reusing the post-15-05 `_api_get` parsed-dict pattern and Phase 15 `TestSharedApiGetContract` test class from day 1.
**Requirements**: TBD (no explicit REQ IDs yet — delivers on milestone provincial coverage goal)
**Depends on:** Phase 15
**Plans:** 8/8 plans complete + 1 gap-closure plan (18-09)

Plans:
- [x] 16-01-PLAN.md — Quebec module skeleton + Wave 0 test scaffolds
- [x] 16-02-PLAN.md — CKAN client + 5 discovery tools + TestSharedApiGetContract
- [x] 16-03-PLAN.md — Health (MSSS) + Transport (MTQ) curated tools (7)
- [x] 16-04-PLAN.md — Environment/Demographics/Energy tools (6) + prompts + resources + integration + docs
- [x] 16-05-PLAN.md — Gap closure cycle 1 (post-UAT)
- [x] 16-06-PLAN.md — Gap closure cycle 2 (WFS paging, snake_case mapper, Hydro-Québec SECLEVEL=1 SSL)
- [x] 16-07-PLAN.md — Gap closure cycle 3 (bridges int->str coercion, electricity XLSX legend row filter)
- [ ] 16-08-PLAN.md — Gap closure cycle 4 (route filter substring match bug)

### Phase 17: Alberta Government Open Data

**Goal:** Add Alberta's provincial open data surface to mcp-canada via 24 alberta_ tools (5 discovery + 19 curated) covering open.alberta.ca CKAN catalogue (33,269 datasets), GeoDiscover Alberta ArcGIS REST 11.3, WMBappServices wildfire FeatureServers, AHSGIS health FeatureServers, AER (Alberta Energy Regulator) static reports (ST1/ST3/ST39), and 511 Alberta road API. Reuses shared/arcgis_hub.py + shared/parsers.fetch_and_parse — NO new shared utilities. Adds 6 prompts + 7 resources from day 1.
**Requirements**: AB-01, AB-02, AB-03, AB-04, AB-05, AB-06, AB-07, AB-08, AB-09, AB-10, AB-11, AB-12, AB-13, AB-14, AB-15, AB-16, AB-17, AB-18, AB-19, AB-20, AB-21, AB-22, AB-23, AB-24, AB-25, AB-26, AB-27
**Depends on:** Phase 16
**Plans:** 9/9 plans complete

Plans:
- [ ] 17-01-PLAN.md — Module scaffolding: 7-file pattern + Wave 0 test stubs + _api_get/_511_get helpers + 24 client function stubs
- [ ] 17-02-PLAN.md — 5 CKAN discovery tools + TestSharedApiGetContract regression guard
- [ ] 17-03-PLAN.md — 4 AER tools (ST1 daily, ST1 archive, ST39 pipelines, ST3 production)
- [ ] 17-04-PLAN.md — 4 wildfire tools (active fires, perimeters, fire bans, fire control orders)
- [ ] 17-05-PLAN.md — 3 AHS health tools (hospitals, zones, EMS/PCN clinics)
- [ ] 17-06-PLAN.md — 3 transport tools (511 road events, winter conditions, cameras)
- [ ] 17-07-PLAN.md — 5 environment/agriculture/demographics/parks tools
- [ ] 17-08-PLAN.md — 6 prompts + 7 resources (Phase 40 pattern)
- [ ] 17-09-PLAN.md — Parametrized envelope/lang tests + integration tests + README/docs/EXAMPLES updates + 95% coverage gate

### Phase 18: Manitoba Government Open Data

**Goal:** Add Manitoba's provincial open data as a new `manitoba` module via the geoportal.gov.mb.ca ArcGIS Hub (org mMUesHYPkXjaFGfS) — 5 Hub discovery tools + ~15 curated FeatureServer tools across flood/hydrology, agriculture & drought, environment/parks, regional health, and conditional Manitoba 511 transport, with 6 bilingual prompts + 7 resources. ArcGIS Hub pattern (Alberta Phase 17 / York Region Phase 14), NOT CKAN.
**Requirements**: MB-01, MB-02, MB-03, MB-04, MB-05, MB-06, MB-07, MB-08, MB-09, MB-10, MB-11, MB-12, MB-13, MB-14, MB-15, MB-16, MB-17, MB-18
**Depends on:** Phase 17
**Plans:** 9/9 plans complete

Plans:
- [ ] 18-01-PLAN.md — Module scaffold (7 files + test scaffolds, stubs, fixtures) + Wave 0 spike (511 key + resolve 3 FeatureServer URLs)
- [ ] 18-02-PLAN.md — 5 ArcGIS Hub discovery tools (search, details, query auto-router, organizations, categories)
- [ ] 18-03-PLAN.md — 3 flood/hydrology tools (flood alerts, river stations, provincial waterways)
- [ ] 18-04-PLAN.md — 4 agriculture/drought tools (drought monitor, ag weather stations, livestock prices, crop regions)
- [ ] 18-05-PLAN.md — 5 environment/health/parks tools (parks, surgical wait times, fisheries, forests, health facilities)
- [ ] 18-06-PLAN.md — 3 transport tools (511 road events, winter conditions, cameras — conditional, NOT_CONFIGURED fallback)
- [ ] 18-07-PLAN.md — 6 bilingual prompts + 7 resources (Phase 40 pattern)
- [ ] 18-08-PLAN.md — Parametrized envelope/lang tests + integration tests + README/MODULES/CLAUDE/EXAMPLES sync + 95% coverage gate
- [ ] 18-09-PLAN.md — Gap closure: fix 3 ArcGIS-Hub discovery tools (OGC limit/startindex params, omit blank q) + param-regression tests + live integration check [MB-01, MB-04, MB-05]

### Phase 19: Saskatchewan Government Open Data

**Goal:** Add Saskatchewan's provincial open data as a new `saskatchewan` module via the geohub.saskatchewan.ca ArcGIS Hub (primary org `zcv98lgAl8xQ04cW`), the separate WSA org (`7MBdlVpjqbfBhQer`), and the SPSA wildfire REST server (`gis.saskatchewan.ca/egis`) — a lean 14 tools (5 Hub discovery + 9 curated) across agriculture (crop yields, grain elevators), energy/mining (potash/uranium/helium/coal), environment (fire bans, historic wildfires, air quality), and water (WSA hydrometric stations, reservoirs), with 6 bilingual prompts + 7 resources. ArcGIS Hub pattern (Manitoba Phase 18 / Alberta Phase 17), NOT CKAN. Wave 0 fixes the shared `arcgis_hub.py` startindex pagination bug (benefits York/Alberta/Manitoba too). Transport (511 key-gated) and Health (no public SHA FeatureServer) are deferred — no NOT_CONFIGURED stubs.
**Requirements**: SK-01, SK-02, SK-03, SK-04, SK-05, SK-06, SK-07, SK-08, SK-09, SK-10, SK-11, SK-12, SK-13, SK-14, SK-15
**Depends on:** Phase 18
**Plans:** 7/7 plans complete

Plans:
- [ ] 19-01-PLAN.md — Wave 0: shared/arcgis_hub.py startindex fix + York/Alberta/Manitoba no-regression check + module scaffold (7 files + test scaffolds, constants for 3 bases, ~14 client stubs) + spike (WSA water-quality layer 19 + Petroleum 400)
- [ ] 19-02-PLAN.md — 5 ArcGIS Hub discovery tools (search/details/query auto-router/orgs/categories) with OGC params (limit/startindex, omit blank q) + TestSharedApiGetContract
- [ ] 19-03-PLAN.md — Agriculture (crop yields, grain elevators) + Energy/mining (mineral mines dispatch: potash/uranium/helium/coal) — 3 curated tools
- [ ] 19-04-PLAN.md — Environment (fire bans via SPSA, historic wildfires, air quality) — 3 curated tools
- [ ] 19-05-PLAN.md — Water/WSA (hydrometric stations, reservoirs layer 26) — 2 curated tools
- [ ] 19-06-PLAN.md — 6 bilingual prompts + 7 resources (Phase 40 pattern), portal-guide documents multi-org architecture + deferred domains
- [ ] 19-07-PLAN.md — Parametrized envelope/lang tests + LIVE field-presence integration (Manitoba lesson) + README/MODULES/CLAUDE/EXAMPLES sync + 95% coverage gate

### Phase 20: Nova Scotia Government Open Data

**Goal:** Add Nova Scotia provincial open data via data.novascotia.ca (Socrata SODA API) as a new `nova_scotia` module, establishing a reusable `shared/socrata.py` client (the 4th portal technology). Ship 5 discovery tools + 12 curated tools (17 total) across fishing/aquaculture, environment/water, lands, air quality, and health + demographics, with 6 bilingual prompts and 7 zero-parameter resources.
**Requirements**: NS-01…NS-18
**Depends on:** Phase 19
**Plans:** 4/7 plans executed

Plans:
- [ ] 20-01-PLAN.md — Wave 0: build shared/socrata.py + TestSharedSocrataContract, scaffold nova_scotia module, resolve the 3 dataset-shape spikes (NS-01)
- [ ] 20-02-PLAN.md — 5 Socrata catalog discovery tools incl. the categories=-broken workaround (NS-02…NS-06)
- [ ] 20-03-PLAN.md — Fishing/aquaculture curated tools: marine + landbased leases, hatchery stocking, production (NS-07…NS-10)
- [ ] 20-04-PLAN.md — Environment/water/air curated tools: water quality, boil-water advisories, protected areas, air-quality stations (NS-11, NS-12, NS-15, NS-16)
- [ ] 20-05-PLAN.md — Health + demographics curated tools: health facilities (dispatch), vital statistics, chronic disease prevalence (NS-13, NS-14, NS-17)
- [ ] 20-06-PLAN.md — 6 bilingual prompts + 7 zero-parameter resources incl. the Socrata/SoQL guide (NS-18)
- [ ] 20-07-PLAN.md — Parametrized + LIVE field-presence integration tests, docs sync (Socrata as 4th portal tech), 95% coverage (NS-18)

### Phase 21: New Brunswick Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 20
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 21 to break down)

### Phase 22: Newfoundland and Labrador Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 21
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 22 to break down)

### Phase 23: Prince Edward Island Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 22
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 23 to break down)

### Phase 24: Northwest Territories Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 23
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 24 to break down)

### Phase 25: Yukon Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 24
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 25 to break down)

### Phase 26: Nunavut Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 25
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 26 to break down)

### Phase 27: Montreal Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 26
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 27 to break down)

### Phase 28: Vancouver Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 27
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 28 to break down)

### Phase 29: Calgary Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 28
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 29 to break down)

### Phase 30: Edmonton Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 29
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 30 to break down)

### Phase 31: Ottawa Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 30
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 31 to break down)

### Phase 32: Winnipeg Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 31
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 32 to break down)

### Phase 33: Halifax Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 32
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 33 to break down)

### Phase 34: Mississauga Municipal Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 33
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 34 to break down)

### Phase 35: Peel Region Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 34
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 35 to break down)

### Phase 36: Durham Region Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 35
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 36 to break down)

### Phase 37: Halton Region Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 36
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 37 to break down)

### Phase 38: Waterloo Region Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 37
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 38 to break down)

### Phase 39: Metro Vancouver Regional Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 38
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 39 to break down)

### Phase 40: MCP Prompts and Resources

**Goal**: Add MCP prompts (guided workflow templates and quick lookup instructions) and resources (reference catalogs, documentation guides, response templates) to all 12 modules, extending the 5-file module pattern to 7-file with prompts.py and resources.py auto-discovered by FileSystemProvider
**Depends on**: Phase 13 (all modules must exist)
**Requirements**: PR-01, PR-02, PR-03, PR-04, PR-05, PR-06, PR-07, PR-08, PR-09, PR-10, PR-11, PR-12, PR-13, PR-14, PR-15, PR-16, PR-17, PR-18, PR-19, PR-20
**Success Criteria** (what must be TRUE):
  1. Every module has prompts.py with 4-6 bilingual @prompt functions (guided workflows + quick lookups) auto-discovered by FileSystemProvider
  2. Every module has resources.py with 6-10 zero-parameter @resource functions using data://, docs://, template:// URI schemes
  3. Prompts appear via prompts/list and resources via resources/list natively in MCP clients with no server.py changes
  4. Integration tests verify discovery of >= 55 prompts and >= 70 resources through MCP Client layer
  5. README catalogs all prompts and resources; CLAUDE.md documents 7-file module pattern
**Plans:** 5/5 plans complete

Plans:
- [ ] 40-01-PLAN.md — Reference implementation: BoC prompts + resources + _example update + unit tests
- [ ] 40-02-PLAN.md — StatCan + Datastore + CKAN prompts/resources + unit tests
- [ ] 40-03-PLAN.md — Open Parliament + Recalls + Drug Database + Nutrient File prompts/resources + unit tests
- [ ] 40-04-PLAN.md — Weather + IRCC + Ontario + Toronto prompts/resources + unit tests
- [ ] 40-05-PLAN.md — Integration tests + README + CLAUDE.md documentation updates
