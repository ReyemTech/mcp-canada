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

### York Region Municipal Open Data

- **YR-01**: Shared `shared/arcgis_hub.py` provides a reusable ArcGIS Hub Search API + FeatureServer async client usable by any Canadian municipal module that publishes via ArcGIS Hub
- **YR-02**: Client supports `/api/search/v1/collections/all/items` Hub Search endpoint with pagination via offset/limit (NOT the deprecated `/api/v2/datasets` which returns 404)
- **YR-03**: Client supports FeatureServer query with `&f=geojson` and auto-paginates while `exceededTransferLimit=true` up to a MAX_RECORDS cap of 5000 per call, returning a `truncated` flag
- **YR-04**: York Region module covers 4 verified ArcGIS Hub portals (york_region, markham, newmarket, aurora) and 6 municipalities without public portals return structured NOT_FOUND
- **YR-05**: Each verified portal gets 5 discovery tools: search_datasets, get_dataset_details, query_features, list_organizations, list_categories (total 20 discovery tools)
- **YR-06**: Agent can search YRT/Viva transit stops and routes from York Region Transportation FeatureServer
- **YR-07**: Agent can fetch York Region regional road network from the Transportation FeatureServer
- **YR-08**: Agent can query York Region public health & safety datasets (beach water testing, hospitals, drinking water adverse incidents)
- **YR-09**: Agent can query York Region 2021 Census demographics (age/sex or income) by Dissemination Area with optional CSDNAME filter, returning a focused field set
- **YR-10**: Agent can query York Region waste management data (annual diversion tonnages or solid waste site locations)
- **YR-11**: Agent can search Markham civic addresses and road network (SLRN) via curated tools
- **YR-12**: York Region module has prompts.py with 4-6 bilingual @prompt functions covering discovery workflows and curated data
- **YR-13**: York Region module has resources.py with 6-10 zero-parameter @resource functions using data://, docs://, template:// URI schemes, including a portal catalog and municipality list
- **YR-14**: All York Region tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, municipality prefix), are discoverable via discover_tools, and README reflects the new tool catalog

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

### Alberta Government Open Data

- [x] **AB-01**: Agent can search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets) by keyword with optional `organization`, `format`, and pagination filters
- [x] **AB-02**: Agent can get full details for an Alberta dataset by id/slug, including resources list with format and URL — flattening 50+ Alberta CKAN extras (publication identifiers) to the agent-useful subset
- [x] **AB-03**: Agent can query a dataset (file resource OR live ESRI REST FeatureServer) via auto-router — routes ESRI REST → arcgis_hub.query_feature_service; CSV/XLSX/JSON → fetch_and_parse; PDF/ZIP/KML → metadata-only; FeatureServer preferred over MapServer
- [x] **AB-04**: Agent can list 370 federated Alberta organizations (current ministries + ~150 historical predecessor ministries + Crown corps + advisory committees)
- [x] **AB-05**: Agent can list dataset format categories — Alberta CKAN does NOT use groups (group_list returns empty); uses res_format facet via package_search
- [x] **AB-06**: Agent can fetch today's AER ST1 daily well licences from static.aer.ca/prd/data/well-lic/WELLS{day}.TXT (rotates by day-of-week, fixed-width plain-text parsed inline)
- [x] **AB-07**: Agent can get the AER ST1 monthly archive ZIP URL by year/month (discovery-only — files are large fixed-width TXT, not auto-parsed)
- [x] **AB-08**: Agent can fetch AER ST39 annual pipeline statistics XLSX for a verified year (length by substance/operator)
- [x] **AB-09**: Agent can fetch AER ST3 monthly oil/gas/bitumen production volumes for one of 7 verified products (Butane/Ethane/NGL/Oil/Gas/Propane/Sulphur — case-sensitive, Pitfall 8)
- **AB-10**: Agent can get current active wildfires from WMBappServices Active_Wildfires_Dashboard_view FeatureServer with optional fire_status filter
- **AB-11**: Agent can get wildfire perimeters dispatched by status: Literal["active","extinguished"] from WMBappServices simplified-view FeatureServers
- **AB-12**: Historical wildfire data (2006-current CSV) is documented as routed via alberta_query_dataset (CKAN wildfire-data package) — NO dedicated tool
- **AB-13**: Agent can get current province-wide fire bans from WMBappServices alberta_fire_ban_system FeatureServer (the data backend behind albertafirebans.ca)
- **AB-14**: Agent can get fire control orders, OHV restrictions, and forest area boundaries via single tool dispatched by category param (replaces deferred alberta_get_fire_weather since FWI is not publicly published)
- **AB-15**: Agent can get 101 AHS hospitals with zone/IP/ED capability flags from AHSGIS AHS_Hospitals FeatureServer
- **AB-16**: Agent can get EMS station OR PCN clinic locations from AHSGIS via single tool dispatched by facility_type param (subsumes deferred ER wait times — Pitfall 9)
- **AB-17**: Agent can get 5 AHS zone boundaries (South, Calgary, Central, Edmonton, North) with POP2006/2011/2016 population from AHS_Zone FeatureServer
- **AB-18**: Agent can get current road events (closures, construction, incidents) from 511 Alberta v2 API at /api/v2/get/event with optional event_type filter
- **AB-19**: Agent can get current winter road conditions (~1121 records) from 511 Alberta v2 API at /api/v2/get/winterroads with optional area_name filter
- **AB-20**: Agent can get traffic camera locations and snapshot URLs (~376 cameras) from 511 Alberta v2 API at /api/v2/get/cameras
- **AB-21**: Agent can get 75 air quality monitoring stations with current pollutant readings (SO2/H2S/TRS/O3/NO2/CO/PM2.5/etc.) from GeoDiscover Alberta AQHI MapServer layer 1
- **AB-22**: Agent can get water management advisories dispatched by advisory_type: Literal["river","water_management","drought","ice_cover","water_sharing"] from GeoDiscover river forecast centre FeatureServer
- [x] **AB-23**: Water licence registry (87MB+ active, 169MB+ inactive) is exposed as discovery-only via alberta_search_datasets / alberta_get_dataset_details with row-filter requirement documented in tool docstring + docs://alberta/wildfire-data-guide resource
- **AB-24**: Agent can get historical major crop production statistics (2000-2014 Alberta Official Statistic) from open.alberta.ca CKAN major-crop-production-alberta package CSV
- **AB-25**: Agent can get population estimates with optional breakdown: csd (default) / quarterly / annual / age_sex / sub_provincial / components_of_growth — complementing StatCan (Alberta provides CSD-level municipal; StatCan provides CMA-level only)
- **AB-26**: Agent can get all Alberta provincial parks and protected areas from GeoDiscover boundary/parks_protected_areas_alberta FeatureServer
- **AB-27**: All Alberta tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, alberta_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

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
| YR-01 | Phase 14 | Planned |
| YR-02 | Phase 14 | Planned |
| YR-03 | Phase 14 | Planned |
| YR-04 | Phase 14 | Planned |
| YR-05 | Phase 14 | Planned |
| YR-06 | Phase 14 | Planned |
| YR-07 | Phase 14 | Planned |
| YR-08 | Phase 14 | Planned |
| YR-09 | Phase 14 | Planned |
| YR-10 | Phase 14 | Planned |
| YR-11 | Phase 14 | Planned |
| YR-12 | Phase 14 | Planned |
| YR-13 | Phase 14 | Planned |
| YR-14 | Phase 14 | Planned |
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
| AB-01 | Phase 17 | Complete |
| AB-02 | Phase 17 | Complete |
| AB-03 | Phase 17 | Complete |
| AB-04 | Phase 17 | Complete |
| AB-05 | Phase 17 | Complete |
| AB-06 | Phase 17 | Complete |
| AB-07 | Phase 17 | Complete |
| AB-08 | Phase 17 | Complete |
| AB-09 | Phase 17 | Complete |
| AB-10 | Phase 17 | Planned |
| AB-11 | Phase 17 | Planned |
| AB-12 | Phase 17 | Planned |
| AB-13 | Phase 17 | Planned |
| AB-14 | Phase 17 | Planned |
| AB-15 | Phase 17 | Planned |
| AB-16 | Phase 17 | Planned |
| AB-17 | Phase 17 | Planned |
| AB-18 | Phase 17 | Planned |
| AB-19 | Phase 17 | Planned |
| AB-20 | Phase 17 | Planned |
| AB-21 | Phase 17 | Planned |
| AB-22 | Phase 17 | Planned |
| AB-23 | Phase 17 | Complete |
| AB-24 | Phase 17 | Planned |
| AB-25 | Phase 17 | Planned |
| AB-26 | Phase 17 | Planned |
| AB-27 | Phase 17 | Planned |

**Coverage:**
- v1 requirements: 73 total (added 27 Alberta requirements in Phase 17)
- Mapped to phases: 73
- Unmapped: 0
- York Region requirements: 14 total (Phase 14)
- IRCC requirements: 9 total (Phase 11)
- Ontario requirements: 8 total (Phase 12)
- Toronto requirements: 12 total (Phase 13)
- Alberta requirements: 27 total (Phase 17)
- Prompts & Resources requirements: 20 total (Phase 40)

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-17 after Phase 17 planning*
