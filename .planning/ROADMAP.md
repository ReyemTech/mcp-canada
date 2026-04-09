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

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 13
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 14 to break down)

### Phase 15: British Columbia Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 14
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 15 to break down)

### Phase 16: Quebec Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 15
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 16 to break down)

### Phase 17: Alberta Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 16
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 17 to break down)

### Phase 18: Manitoba Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 17
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 18 to break down)

### Phase 19: Saskatchewan Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 18
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 19 to break down)

### Phase 20: Nova Scotia Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 19
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 20 to break down)

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
**Plans:** 1/5 plans executed

Plans:
- [ ] 40-01-PLAN.md — Reference implementation: BoC prompts + resources + _example update + unit tests
- [ ] 40-02-PLAN.md — StatCan + Datastore + CKAN prompts/resources + unit tests
- [ ] 40-03-PLAN.md — Open Parliament + Recalls + Drug Database + Nutrient File prompts/resources + unit tests
- [ ] 40-04-PLAN.md — Weather + IRCC + Ontario + Toronto prompts/resources + unit tests
- [ ] 40-05-PLAN.md — Integration tests + README + CLAUDE.md documentation updates
