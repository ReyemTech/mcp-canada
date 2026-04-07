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

- [ ] **Phase 7: Datastore + SSL** - SQLite persistence layer and StatCan SSL strategy resolved
- [ ] **Phase 8: StatCan WDS** - All WDS discovery, series, data, and monitoring tools live
- [ ] **Phase 9: SDMX + Composite** - Server-side filtered queries and fetch-and-store bridge complete
- [ ] **Phase 10: Tests + Docs** - Integration test coverage and README updated

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
**Plans:** 1/3 plans executed

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
**Plans**: TBD

### Phase 9: SDMX + Composite
**Goal**: Agents can apply server-side dimension filters via SDMX for large tables and store multi-series fetches directly to the shared datastore in a single tool call
**Depends on**: Phase 7 (datastore), Phase 8 (WDS tools — productIds and coordinate structures needed to test SDMX filtering)
**Requirements**: SC-10, SC-11, SC-12, SC-15
**Success Criteria** (what must be TRUE):
  1. Agent can retrieve the dimension structure (codelists) for any StatCan table via SDMX
  2. Agent can retrieve server-side filtered observations using SDMX key syntax with date range or lastN support — but not both simultaneously (mutual exclusion enforced)
  3. Agent can fetch multiple vectors for a date range and have results written to the shared datastore in one tool call, enabling subsequent cross-module SQL queries
**Plans**: TBD

### Phase 10: Tests + Docs
**Goal**: All new tools are covered by integration tests through the MCP Client layer and the README accurately reflects the expanded tool catalog
**Depends on**: Phase 9 (all tool surfaces must exist before integration sweep)
**Requirements**: INF-06, INF-07, INF-08, INF-09
**Success Criteria** (what must be TRUE):
  1. Unit test coverage for all new code is at or above 95% as reported by pytest-cov
  2. Every new tool has at least one integration test scenario that calls it through the MCP Client layer (not client functions directly) and asserts on response shape
  3. README tool catalog lists all new statcan and datastore tools with accurate descriptions and updated tool count
  4. EXAMPLES.md contains at least one end-to-end example showing cross-module SQL queries combining StatCan and another module's data
**Plans**: TBD

## Progress

**Execution Order:** 7 → 8 → 9 → 10 (Phase 9 unblocks after both Phase 7 and Phase 8 complete)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 7. Datastore + SSL | 1/3 | In Progress|  | - |
| 8. StatCan WDS | v1.1 | 0/TBD | Not started | - |
| 9. SDMX + Composite | v1.1 | 0/TBD | Not started | - |
| 10. Tests + Docs | v1.1 | 0/TBD | Not started | - |
