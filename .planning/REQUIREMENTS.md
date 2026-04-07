# Requirements: mcp-canada v1.1

**Defined:** 2026-04-07
**Core Value:** An agent can combine data from any Canadian government source in a single SQL query — turning isolated APIs into one queryable data platform.

## v1 Requirements

### Datastore

- [ ] **DS-01**: Agent can create a named SQLite table with specified columns and types
- [ ] **DS-02**: Agent can insert rows of data into an existing table
- [ ] **DS-03**: Agent can run read-only SQL queries (SELECT/PRAGMA only) across any stored tables
- [ ] **DS-04**: Agent can list all tables in the datastore
- [ ] **DS-05**: Agent can view the schema (columns and types) of a specific table
- [ ] **DS-06**: Agent can drop a table by name
- [ ] **DS-07**: Table and column names are validated against a regex allowlist to prevent SQL injection
- [ ] **DS-08**: All database operations use async SQLite (aiosqlite) to avoid blocking the event loop

### StatCan Discovery

- [ ] **SC-01**: Agent can search Statistics Canada tables by keyword (client-side search on cached cube list)
- [ ] **SC-02**: Agent can retrieve detailed metadata for a specific table by productId (dimensions, members, footnotes)
- [ ] **SC-03**: Agent can decode numeric codes used in StatCan responses (frequency, units, scalar factor, status)

### StatCan Series Info

- [ ] **SC-04**: Agent can look up series metadata by vectorId (table, coordinate, frequency, units)
- [ ] **SC-05**: Agent can look up series metadata by productId + coordinate (resolves to vectorId)

### StatCan WDS Data Retrieval

- [ ] **SC-06**: Agent can retrieve the latest N observations for a given vectorId
- [ ] **SC-07**: Agent can retrieve the latest N observations by productId + coordinate
- [ ] **SC-08**: Agent can retrieve data for a vector within a specific reference period date range
- [ ] **SC-09**: Agent can retrieve data for multiple vectors simultaneously within a release date range

### StatCan SDMX

- [ ] **SC-10**: Agent can fetch the dimension structure (codelists) for a table via SDMX
- [ ] **SC-11**: Agent can retrieve server-side filtered observations using SDMX key syntax with date range and lastN support
- [ ] **SC-12**: Agent can retrieve observations for a single vector via SDMX with date range filtering

### StatCan Monitoring

- [ ] **SC-13**: Agent can list series that changed today
- [ ] **SC-14**: Agent can list cubes that changed on a specific date

### StatCan Composite

- [ ] **SC-15**: Agent can fetch multiple vectors for a date range and store results directly to the shared datastore in one tool call

### Infrastructure

- [ ] **INF-01**: StatCan SSL certificate handling attempts proper cert resolution before falling back to scoped verify=False
- [ ] **INF-02**: StatCan API calls are rate-limited to 20 req/s via the shared TokenBucket rate limiter
- [ ] **INF-03**: StatCan responses are cached with tiered TTLs (cube list 1hr, metadata 24hr, code sets 7d, observations 1hr)
- [ ] **INF-04**: All StatCan and datastore tools support bilingual responses (lang: en/fr)
- [ ] **INF-05**: All tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings)
- [ ] **INF-06**: Unit tests achieve 95%+ coverage for all new code
- [ ] **INF-07**: Integration tests verify live StatCan API calls through the MCP Client layer
- [ ] **INF-08**: README updated with StatCan module and datastore documentation
- [ ] **INF-09**: EXAMPLES.md updated with cross-module SQL query examples

## v2 Requirements

### Extended Datastore

- **DS-V2-01**: Existing modules (BoC, weather, nutrient) can optionally store fetched data to the shared datastore
- **DS-V2-02**: Datastore supports full-text search on stored table contents

### Extended StatCan

- **SC-V2-01**: Agent can subscribe to daily change notifications for specific tables
- **SC-V2-02**: Agent can compare two time periods of the same series with summary statistics

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full table CSV/SDMX downloads | Files routinely exceed 100MB — unsuitable for MCP context |
| getAllCubesList (full) | Multi-MB response with dimension detail; use Lite + targeted metadata |
| Delta file ingestion | Bulk sync mechanism for high-volume consumers, not MCP agents |
| Data visualization | Agent responsibility, not server responsibility |
| Store cube metadata to SQLite | High complexity, low utility — agents rarely SQL-query dimension structure |
| HTTP transport for datastore | SQLite is local-only by design |
| SQLite full-text search on cube titles | BM25 discovery + in-memory cache handles this |
| Migrating existing modules to use datastore | Future enhancement for v1.2+ |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DS-01 | Phase 7 | Pending |
| DS-02 | Phase 7 | Pending |
| DS-03 | Phase 7 | Pending |
| DS-04 | Phase 7 | Pending |
| DS-05 | Phase 7 | Pending |
| DS-06 | Phase 7 | Pending |
| DS-07 | Phase 7 | Pending |
| DS-08 | Phase 7 | Pending |
| SC-01 | Phase 8 | Pending |
| SC-02 | Phase 8 | Pending |
| SC-03 | Phase 8 | Pending |
| SC-04 | Phase 8 | Pending |
| SC-05 | Phase 8 | Pending |
| SC-06 | Phase 8 | Pending |
| SC-07 | Phase 8 | Pending |
| SC-08 | Phase 8 | Pending |
| SC-09 | Phase 8 | Pending |
| SC-10 | Phase 9 | Pending |
| SC-11 | Phase 9 | Pending |
| SC-12 | Phase 9 | Pending |
| SC-13 | Phase 8 | Pending |
| SC-14 | Phase 8 | Pending |
| SC-15 | Phase 9 | Pending |
| INF-01 | Phase 7 | Pending |
| INF-02 | Phase 8 | Pending |
| INF-03 | Phase 8 | Pending |
| INF-04 | Phase 8 | Pending |
| INF-05 | Phase 8 | Pending |
| INF-06 | Phase 10 | Pending |
| INF-07 | Phase 10 | Pending |
| INF-08 | Phase 10 | Pending |
| INF-09 | Phase 10 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-07 after roadmap creation*
