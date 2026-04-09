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

- [x] **ONT-01**: Agent can search Ontario's Open Data Catalogue (data.ontario.ca) by keyword with pagination
- [x] **ONT-02**: Agent can get full details for a specific Ontario dataset including resources and metadata
- [x] **ONT-03**: Agent can get details for a specific Ontario data resource by resource ID
- [x] **ONT-04**: Agent can list Ontario government organizations (ministries) that publish open data
- [x] **ONT-05**: Agent can get aggregate Ontario portal statistics (total dataset count)
- [x] **ONT-06**: Agent can fetch and parse Ontario population projections data (XLSX from Ministry of Finance)
- [x] **ONT-07**: All Ontario tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings, ontario_ prefix)
- [x] **ONT-08**: Ontario tools are discoverable via discover_tools and callable via call_tool through the MCP Client layer

### Toronto Open Data

- **TOR-01**: Shared parsers support GeoJSON FeatureCollection parsing with optional geometry inclusion
- **TOR-02**: Shared parsers support JSON array/object parsing with GeoJSON auto-detection
- **TOR-03**: Agent can search Toronto's Open Data Catalogue by keyword with pagination
- **TOR-04**: Agent can get full details for a Toronto dataset including resources with datastore_active flag
- **TOR-05**: Agent can search TTC stops by name from GTFS ZIP data
- **TOR-06**: Agent can search TTC routes by type from GTFS ZIP data
- **TOR-07**: Agent can get neighbourhood census profile indicators (2016 140-neighbourhood model via CKAN datastore)
- **TOR-08**: Agent can compare a single census indicator across all 140 neighbourhoods
- **TOR-09**: Agent can fetch 311 service requests filtered by year, ward, service type, and status (annual ZIP+CSV with client-side filtering)
- **TOR-10**: Agent can query RentSafeTO apartment building evaluations by ward and minimum score
- **TOR-11**: Agent can query short-term rental registrations by ward and status
- **TOR-12**: All Toronto tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings, toronto_ prefix) and are discoverable via discover_tools

### MCP Prompts and Resources

- **PR-01**: Every module has a prompts.py with 4-6 @prompt functions auto-discovered by FileSystemProvider
- **PR-02**: Guided workflow prompts return list[Message] with user + assistant roles priming multi-tool conversations
- **PR-03**: Quick lookup prompts return str with specific tool name and parameter instructions
- **PR-04**: All prompts accept bilingual lang parameter (Annotated[Literal["en", "fr"]]) and return content in chosen language
- **PR-05**: Every module has a resources.py with 6-10 @resource functions using type-prefixed URIs (data://, docs://, template://)
- **PR-06**: Catalog resources (data://) return valid JSON with bilingual en/fr labels for reference data agents need repeatedly
- **PR-07**: Documentation resources (docs://) return markdown guides for API quirks, naming conventions, and interpretation
- **PR-08**: Template resources (template://) return markdown with {placeholder} syntax for response formatting
- **PR-09**: All resources use zero-parameter functions (not ResourceTemplate) with bilingual content inline
- **PR-10**: Prompts follow module prefix naming convention (boc_, sc_, parl_, wx_, etc.)
- **PR-11**: Resources use type-prefixed URIs: data://module/name, docs://module/name, template://module/name
- **PR-12**: Prompts appear as slash-commands via prompts/list; resources appear via resources/list (native MCP visibility)
- **PR-13**: No server.py changes needed — FileSystemProvider auto-discovers prompts and resources
- **PR-14**: Bank of Canada module has prompts for rate analysis, policy rate lookup, currency comparison, commodity exploration, and inflation check
- **PR-15**: StatCan module has prompts for data discovery, SDMX exploration, vector retrieval, store-and-query, and change monitoring
- **PR-16**: Weather module has a single top-level prompts.py covering all sub-modules (current, climate, marine, hydro, etc.)
- **PR-17**: IRCC, Ontario, and Toronto modules have prompts for their respective data exploration workflows
- **PR-18**: Integration tests verify prompts discoverable via client.list_prompts() and resources via client.read_resource()
- **PR-19**: README updated with prompt catalog (~60 prompts) and resource catalog (~80-100 resources)
- **PR-20**: CLAUDE.md updated with 7-file module pattern and prompt/resource coding conventions

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
| Toronto building permits curated tool | 232K+ active permits too large for client-side filter; use toronto_search_datasets discovery instead |
| Toronto budget curated tool | Annual XLSX with no datastore access; discoverable via toronto_search_datasets |
| Toronto 2021 neighbourhood profiles | XLSX-only (158-model), not datastore-active; use 2016 CSV (140-model) instead |

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
| TOR-01 | Phase 13 | Planned |
| TOR-02 | Phase 13 | Planned |
| TOR-03 | Phase 13 | Planned |
| TOR-04 | Phase 13 | Planned |
| TOR-05 | Phase 13 | Planned |
| TOR-06 | Phase 13 | Planned |
| TOR-07 | Phase 13 | Planned |
| TOR-08 | Phase 13 | Planned |
| TOR-09 | Phase 13 | Planned |
| TOR-10 | Phase 13 | Planned |
| TOR-11 | Phase 13 | Planned |
| TOR-12 | Phase 13 | Planned |
| PR-01 | Phase 40 | Planned |
| PR-02 | Phase 40 | Planned |
| PR-03 | Phase 40 | Planned |
| PR-04 | Phase 40 | Planned |
| PR-05 | Phase 40 | Planned |
| PR-06 | Phase 40 | Planned |
| PR-07 | Phase 40 | Planned |
| PR-08 | Phase 40 | Planned |
| PR-09 | Phase 40 | Planned |
| PR-10 | Phase 40 | Planned |
| PR-11 | Phase 40 | Planned |
| PR-12 | Phase 40 | Planned |
| PR-13 | Phase 40 | Planned |
| PR-14 | Phase 40 | Planned |
| PR-15 | Phase 40 | Planned |
| PR-16 | Phase 40 | Planned |
| PR-17 | Phase 40 | Planned |
| PR-18 | Phase 40 | Planned |
| PR-19 | Phase 40 | Planned |
| PR-20 | Phase 40 | Planned |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0
- IRCC requirements: 9 total (Phase 11)
- Ontario requirements: 8 total (Phase 12)
- Toronto requirements: 12 total (Phase 13)
- Prompts & Resources requirements: 20 total (Phase 40)

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-09 after Phase 40 planning*
