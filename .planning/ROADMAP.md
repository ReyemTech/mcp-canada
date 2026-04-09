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

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 11
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 12 to break down)

### Phase 13: Toronto Municipal Government Open Data

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 12
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 13 to break down)

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
