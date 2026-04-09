# Requirements: mcp-canada v1.1

**Defined:** 2026-04-07
**Core Value:** An agent can combine data from any Canadian government source in a single SQL query — turning isolated APIs into one queryable data platform.

## v1 Requirements

### Datastore

- [x] **DS-01**: Agent can create a named SQLite table with specified columns and types
- [x] **DS-02**: Agent can insert rows of data into an existing table
- [x] **DS-03**: Agent can run read-only SQL queries (SELECT/PRAGMA only) across any stored tables
- [x] **DS-04**: Agent can list all tables in the datastore
- [x] **DS-05**: Agent can view the schema (columns and types) of a specific table
- [x] **DS-06**: Agent can drop a table by name
- [x] **DS-07**: Table and column names are validated against a regex allowlist to prevent SQL injection
- [x] **DS-08**: All database operations use async SQLite (aiosqlite) to avoid blocking the event loop

### StatCan Discovery

- [x] **SC-01**: Agent can search Statistics Canada tables by keyword (client-side search on cached cube list)
- [x] **SC-02**: Agent can retrieve detailed metadata for a specific table by productId (dimensions, members, footnotes)
- [x] **SC-03**: Agent can decode numeric codes used in StatCan responses (frequency, units, scalar factor, status)

### StatCan Series Info

- [x] **SC-04**: Agent can look up series metadata by vectorId (table, coordinate, frequency, units)
- [x] **SC-05**: Agent can look up series metadata by productId + coordinate (resolves to vectorId)

### StatCan WDS Data Retrieval

- [x] **SC-06**: Agent can retrieve the latest N observations for a given vectorId
- [x] **SC-07**: Agent can retrieve the latest N observations by productId + coordinate
- [x] **SC-08**: Agent can retrieve data for a vector within a specific reference period date range
- [x] **SC-09**: Agent can retrieve data for multiple vectors simultaneously within a release date range

### StatCan SDMX

- [x] **SC-10**: Agent can fetch the dimension structure (codelists) for a table via SDMX
- [x] **SC-11**: Agent can retrieve server-side filtered observations using SDMX key syntax with date range and lastN support
- [x] **SC-12**: Agent can retrieve observations for a single vector via SDMX with date range filtering

### StatCan Monitoring

- [x] **SC-13**: Agent can list series that changed today
- [x] **SC-14**: Agent can list cubes that changed on a specific date

### StatCan Composite

- [x] **SC-15**: Agent can fetch multiple vectors for a date range and store results directly to the shared datastore in one tool call

### Infrastructure

- [x] **INF-01**: StatCan SSL certificate handling attempts proper cert resolution before falling back to scoped verify=False
- [x] **INF-02**: StatCan API calls are rate-limited to 20 req/s via the shared TokenBucket rate limiter
- [x] **INF-03**: StatCan responses are cached with tiered TTLs (cube list 1hr, metadata 24hr, code sets 7d, observations 1hr)
- [x] **INF-04**: All StatCan and datastore tools support bilingual responses (lang: en/fr)
- [x] **INF-05**: All tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings)
- [x] **INF-06**: Unit tests achieve 95%+ coverage for all new code
- [x] **INF-07**: Integration tests verify live StatCan API calls through the MCP Client layer
- [x] **INF-08**: README updated with StatCan module and datastore documentation
- [x] **INF-09**: EXAMPLES.md updated with cross-module SQL query examples

### IRCC Immigration

- [x] **IRCC-01**: Shared parser can fetch and parse XLSX files from any URL into list[dict] rows with snake_case keys
- [x] **IRCC-02**: Shared parser can fetch and parse CSV files with BOM handling into list[dict] rows
- [x] **IRCC-03**: Privacy masking converts IRCC '--' suppressed values to None during parsing
- [x] **IRCC-04**: Agent can query permanent residents by country, province, gender, age, CMA, NOC, and immigration category
- [x] **IRCC-05**: Agent can query study permits, work permits (IMP + TFWP), Express Entry (admissions + invited), TR-to-PR transitions, asylum claimants, operational processing, and Afghan refugees
- [x] **IRCC-06**: IRCC tools handle bilingual file variants (EN/FR) and multi-sheet workbooks
- [x] **IRCC-07**: All IRCC tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings, ircc_ prefix)
- [x] **IRCC-08**: Parsed IRCC data can be stored to the shared datastore for cross-module SQL queries
- [x] **IRCC-09**: Shared parser is reusable by any future module (not IRCC-specific)

### Ontario Open Data

- [ ] **ONT-01**: Agent can search Ontario's Open Data Catalogue (data.ontario.ca) by keyword with pagination
- [ ] **ONT-02**: Agent can get full details for a specific Ontario dataset including resources and metadata
- [ ] **ONT-03**: Agent can get details for a specific Ontario data resource by resource ID
- [ ] **ONT-04**: Agent can list Ontario government organizations (ministries) that publish open data
- [ ] **ONT-05**: Agent can get aggregate Ontario portal statistics (total dataset count)
- [ ] **ONT-06**: Agent can fetch and parse Ontario population projections data (XLSX from Ministry of Finance)
- [ ] **ONT-07**: All Ontario tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings, ontario_ prefix)
- [ ] **ONT-08**: Ontario tools are discoverable via discover_tools and callable via call_tool through the MCP Client layer

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
| Generic CKAN resource parser tool | Scope creep — shared/parsers.py makes this trivial to add later |
| IRCC data change detection | Monitoring feature, not core |
| Ontario ZIP resources (vehicle population, energy) | ZIP archives exceed reasonable MCP context budget |
| Ontario education enrollment tools | Deferred to future phase — multi-sheet XLSX layout needs inspection |
| Ontario hospital wait times | Restricted dataset — access_level prevents download |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DS-01 | Phase 7 | Complete |
| DS-02 | Phase 7 | Complete |
| DS-03 | Phase 7 | Complete |
| DS-04 | Phase 7 | Complete |
| DS-05 | Phase 7 | Complete |
| DS-06 | Phase 7 | Complete |
| DS-07 | Phase 7 | Complete |
| DS-08 | Phase 7 | Complete |
| SC-01 | Phase 8 | Complete |
| SC-02 | Phase 8 | Complete |
| SC-03 | Phase 8 | Complete |
| SC-04 | Phase 8 | Complete |
| SC-05 | Phase 8 | Complete |
| SC-06 | Phase 8 | Complete |
| SC-07 | Phase 8 | Complete |
| SC-08 | Phase 8 | Complete |
| SC-09 | Phase 8 | Complete |
| SC-10 | Phase 9 | Complete |
| SC-11 | Phase 9 | Complete |
| SC-12 | Phase 9 | Complete |
| SC-13 | Phase 8 | Complete |
| SC-14 | Phase 8 | Complete |
| SC-15 | Phase 9 | Complete |
| INF-01 | Phase 7 | Complete |
| INF-02 | Phase 8 | Complete |
| INF-03 | Phase 8 | Complete |
| INF-04 | Phase 8 | Complete |
| INF-05 | Phase 8 | Complete |
| INF-06 | Phase 10 | Complete |
| INF-07 | Phase 10 | Complete |
| INF-08 | Phase 10 | Complete |
| INF-09 | Phase 10 | Complete |
| IRCC-01 | Phase 11 | Planned |
| IRCC-02 | Phase 11 | Planned |
| IRCC-03 | Phase 11 | Planned |
| IRCC-04 | Phase 11 | Planned |
| IRCC-05 | Phase 11 | Planned |
| IRCC-06 | Phase 11 | Planned |
| IRCC-07 | Phase 11 | Planned |
| IRCC-08 | Phase 11 | Planned |
| IRCC-09 | Phase 11 | Planned |
| ONT-01 | Phase 12 | Planned |
| ONT-02 | Phase 12 | Planned |
| ONT-03 | Phase 12 | Planned |
| ONT-04 | Phase 12 | Planned |
| ONT-05 | Phase 12 | Planned |
| ONT-06 | Phase 12 | Planned |
| ONT-07 | Phase 12 | Planned |
| ONT-08 | Phase 12 | Planned |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0
- IRCC requirements: 9 total (Phase 11)
- Ontario requirements: 8 total (Phase 12)

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-08 after Phase 12 planning*
