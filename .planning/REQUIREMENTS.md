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

- [x] **TOR-01**: Shared parsers support GeoJSON FeatureCollection parsing with optional geometry inclusion
- [x] **TOR-02**: Shared parsers support JSON array/object parsing with GeoJSON auto-detection
- [x] **TOR-03**: Agent can search Toronto's Open Data Catalogue by keyword with pagination
- [x] **TOR-04**: Agent can get full details for a Toronto dataset including resources with datastore_active flag
- [x] **TOR-05**: Agent can search TTC stops by name from GTFS ZIP data
- [x] **TOR-06**: Agent can search TTC routes by type from GTFS ZIP data
- [x] **TOR-07**: Agent can get neighbourhood census profile indicators (2016 140-neighbourhood model via CKAN datastore)
- [x] **TOR-08**: Agent can compare a single census indicator across all 140 neighbourhoods
- [x] **TOR-09**: Agent can fetch 311 service requests filtered by year, ward, service type, and status (annual ZIP+CSV with client-side filtering)
- [x] **TOR-10**: Agent can query RentSafeTO apartment building evaluations by ward and minimum score
- [x] **TOR-11**: Agent can query short-term rental registrations by ward and status
- [x] **TOR-12**: All Toronto tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Keywords/Use-for docstrings, toronto_ prefix) and are discoverable via discover_tools

### York Region Municipal Open Data

- [x] **YR-01**: Shared `shared/arcgis_hub.py` provides a reusable ArcGIS Hub Search API + FeatureServer async client usable by any Canadian municipal module that publishes via ArcGIS Hub
- [x] **YR-02**: Client supports `/api/search/v1/collections/all/items` Hub Search endpoint with pagination via offset/limit (NOT the deprecated `/api/v2/datasets` which returns 404)
- [x] **YR-03**: Client supports FeatureServer query with `&f=geojson` and auto-paginates while `exceededTransferLimit=true` up to a MAX_RECORDS cap of 5000 per call, returning a `truncated` flag
- [x] **YR-04**: York Region module covers 4 verified ArcGIS Hub portals (york_region, markham, newmarket, aurora) and 6 municipalities without public portals return structured NOT_FOUND
- [x] **YR-05**: Each verified portal gets 5 discovery tools: search_datasets, get_dataset_details, query_features, list_organizations, list_categories (total 20 discovery tools)
- [x] **YR-06**: Agent can search YRT/Viva transit stops and routes from York Region Transportation FeatureServer
- [x] **YR-07**: Agent can fetch York Region regional road network from the Transportation FeatureServer
- [x] **YR-08**: Agent can query York Region public health & safety datasets (beach water testing, hospitals, drinking water adverse incidents)
- [x] **YR-09**: Agent can query York Region 2021 Census demographics (age/sex or income) by Dissemination Area with optional CSDNAME filter, returning a focused field set
- [x] **YR-10**: Agent can query York Region waste management data (annual diversion tonnages or solid waste site locations)
- [x] **YR-11**: Agent can search Markham civic addresses and road network (SLRN) via curated tools
- [x] **YR-12**: York Region module has prompts.py with 4-6 bilingual @prompt functions covering discovery workflows and curated data
- [x] **YR-13**: York Region module has resources.py with 6-10 zero-parameter @resource functions using data://, docs://, template:// URI schemes, including a portal catalog and municipality list
- [x] **YR-14**: All York Region tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, municipality prefix), are discoverable via discover_tools, and README reflects the new tool catalog

### British Columbia Government Open Data

Backfilled 2026-07-25 from shipped code — Phase 15 was planned with `Requirements: TBD` and never had REQ IDs assigned, leaving it invisible to the traceability table below. Every item was verified against `src/mcp_canada/modules/british_columbia/` at backfill time.

Two portals, two steps: the **BC Data Catalogue** (CKAN + bcgov extensions) for discovery, and the **BC Geographic Warehouse** (OGC WFS 2.0) for geospatial queries. Discovery yields an `object_name` + `queryable_via_wfs` flag that the WFS tools consume. Introduces `shared/ogc.py`, the third portal technology alongside CKAN and ArcGIS Hub. Module prefix `bc_`.

- [x] **BC-01**: Agent can search the BC Data Catalogue by keyword with optional `organization` and `tag` filters and `rows`/`start` pagination
- [x] **BC-02**: Agent can get full BC dataset details by package id, including the WFS routing metadata (`object_name`, `queryable_via_wfs`) that `bc_query_features` needs
- [x] **BC-03**: Agent can query features from a BC dataset via WFS or file download, with CQL filters, `max_records`, and opt-in geometry
- [x] **BC-04**: Agent can list BC government ministries and agencies that publish open data
- [x] **BC-05**: Agent can list BC Data Catalogue tag-based categories for dataset discovery
- [x] **BC-06**: Agent can query currently active BC wildfires with `status`, `centre`, and `min_size_hectares` filters from the BCGW WFS
- [x] **BC-07**: Agent can query historical BC wildfire perimeters with `year`, `cause`, and `min_size_hectares` filters
- [x] **BC-08**: Agent can query BC forest tenure licences by `status`, `tenure_type`, `client_name`, and `district`
- [x] **BC-09**: Agent can query BC forest cut block polygons (`FTEN_CUT_BLOCK_POLY_SVW`) by `status`, `district`, and `client_name`
- [x] **BC-10**: Agent can query BC protected lands (`WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW`) by `designation`, `min_area_ha`, and `name`
- [x] **BC-11**: Agent can query BC groundwater wells (`GW_WATER_WELLS_WRBC_SVW`) by `city`, `well_class`, `aquifer_id`, and `intended_use`
- [x] **BC-12**: Agent can query BC wildfire weather monitoring stations by `name` and `min_elevation`
- [x] **BC-13**: Agent can query BC local and regional parks (`GBA_LOCAL_REG_GREENSPACES_SP`) by `municipality`, `regional_district`, and `park_type`
- [x] **BC-14**: Agent can query BC mining tenure claims (`MTA_ACQUIRED_TENURE_SVW`) by `tenure_type`, `owner_name`, and `min_area_ha`
- [x] **BC-15**: Agent can query BC fish habitat holding areas (`CRIMS_HOLDING_AREAS`) by `feature_code`
- [x] **BC-16**: Agent can query BC hospital emergency rooms (`GSR_EMERGENCY_ROOMS_SV`) by `locality` and `wheelchair_accessible`
- [x] **BC-17**: Agent can query BC walk-in medical clinics (`GSR_MED_WALK_IN_CLINICS_SV`) by `locality`
- [x] **BC-18**: Agent can query BC highway profile segments (`MOT_HIGHWAY_PROFILES_SP`) by `highway_number`, `admin_unit`, and `min_lanes`
- [x] **BC-19**: Agent can query BC road structures (`MOT_ROAD_STRUCTURE_SP`) by `structure_type`
- [x] **BC-20**: Agent can query BC climate observation stations by `name` and `min_elevation`
- [x] **BC-21**: A reusable OGC WFS 2.0 client lives in `shared/ogc.py` (`GetFeature` + CQL_FILTER, paging via `wfs_page_all`) and is not BC-specific — available to Quebec and any other province with a WFS portal
- [x] **BC-22**: All BC tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, `bc_` prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

### Quebec Government Open Data

Backfilled 2026-07-25 from shipped code — Phase 16 was planned with `Requirements: TBD` and never had REQ IDs assigned. Every item was verified against `src/mcp_canada/modules/quebec/` at backfill time.

Primary portal is **Données Québec** (CKAN — 1,593 datasets, 139 orgs, 10 thematic groups). Curated tools draw on MSSS (health), MTQ (transport, live WFS CSV), MELCCFP (environment), MAMH (municipal), and Hydro-Québec. Reuses the post-15-05 `_api_get` parsed-dict pattern and the Phase 15 `TestSharedApiGetContract` guard from day 1. Module prefix `quebec_`.

- [x] **QC-01**: Agent can search the Données Québec catalogue by keyword with optional `organization` and `group` filters and `rows`/`start` pagination
- [x] **QC-02**: Agent can get full details for a Données Québec dataset including the resources list and `datastore_active` flags
- [x] **QC-03**: Agent can query records from a dataset's best resource, preferring CSV > GeoJSON > JSON > XLSX
- [x] **QC-04**: Agent can list all 139 organizations in the federated catalog with package counts
- [x] **QC-05**: Agent can list the 10 thematic groups (Santé, Environnement, etc.) used to categorize datasets
- [x] **QC-06**: Agent can get Quebec health installations (hospitals, CLSCs, CHSLDs, psychiatric) from the MSSS datastore, filterable by `instal_type` and `rss_name`
- [x] **QC-07**: Agent can get current Quebec emergency room wait times and stretcher occupancy (hourly refresh from MSSS), filterable by `installation`
- [x] **QC-08**: Agent can get Quebec municipality population, area, and administrative region from the MAMH municipal registry, filterable by `region`
- [x] **QC-09**: Agent can get current Quebec winter road conditions (pavement state, visibility) from the MTQ WFS
- [x] **QC-10**: Agent can get current Quebec road construction zones and work sites from the MTQ live WFS CSV
- [x] **QC-11**: Agent can get current Quebec road events (accidents, incidents, warnings) from the MTQ live WFS CSV
- [x] **QC-12**: Agent can get the Quebec bridge, culvert, tunnel, and retaining wall inventory from the MTQ structure registry, filterable by `route`, `municipality`, and `region`
- [x] **QC-13**: Agent can get MFFP/MRN historical forest fire archive metadata and download URLs (discovery-only — the archive is a bulk download, not a queryable endpoint)
- [x] **QC-14**: Agent can get the RSQAQ air quality monitoring station network (MELCCFP), filterable by `active_only`
- [x] **QC-15**: Agent can get current Quebec air quality index (IQA) readings from the MELCCFP ArcGIS FeatureServer
- [x] **QC-16**: Agent can get MELCCFP physicochemical water quality monitoring metadata and download URLs (discovery-only)
- [x] **QC-17**: Agent can get historical Quebec electricity production and consumption data from Hydro-Québec via Données Québec CSV
- [x] **QC-18**: Agent can get the MELCCFP protected areas registry (Registre des aires protégées) metadata and download URLs (discovery-only)
- [x] **QC-19**: All Quebec tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, `quebec_` prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

### Integration Test Integrity (Phase 20.1)

Backfilled 2026-07-25 alongside the phase, which was inserted as urgent work without REQ IDs. These describe the guarantees the phase delivered, verified against the suite at close.

- [x] **TEST-01**: Every path through an integration test reaches an assertion — no one-armed guards over the response, no bare `return`, no data-dependent `pytest.skip`
- [x] **TEST-02**: A test may tolerate an upstream outage only by asserting the error code is transient (`UPSTREAM_ERROR`, `RATE_LIMITED`, `UPSTREAM_UNAVAILABLE`); `NOT_FOUND` or `INVALID_INPUT` on a call that should succeed fails loudly
- [x] **TEST-03**: Reintroducing a masking idiom fails the DEFAULT unit suite, not only a live run (`tests/test_integration_test_quality.py`)
- [x] **TEST-04**: A test that genuinely cannot assert in every branch declares itself with `@pytest.mark.tolerates_upstream_error(reason=...)`; the reason is mandatory and exemptions are capped at 10% of the suite
- [x] **TEST-05**: Every tool returns a structured error envelope on upstream failure and never raises — enforced for drug_database and nutrient_file via `shared/envelope.py:upstream_guard` (generalised to all 271 tools by ERR-01)

### Error Classification (Phase 20.2)

- [x] **ERR-01**: Every `@tool` is covered by a catch-all — `@upstream_guard`, a broad `except Exception`/`httpx.HTTPError`, or a module helper that has one. Catching only `httpx.HTTPStatusError` does not count: it covers a 500 but not a timeout, connect error or malformed body
- [x] **ERR-02**: Reintroducing an uncovered tool fails the DEFAULT unit suite (`tests/test_tool_error_handling.py`), and the detector carries a self-test so it cannot pass vacuously
- [x] **ERR-03**: A malformed upstream body is classified as an upstream failure, never as caller error — `shared/http.py:api_get` raises `httpx.DecodingError` (an `HTTPError`, not a `ValueError`) so it bypasses `except ValueError -> INVALID_INPUT` arms
- [x] **ERR-04**: Genuine argument-validation `ValueError`s still return `INVALID_INPUT` — the decode fix does not swallow real caller errors

### MCP Prompts and Resources

- [x] **PR-01**: Every module has a prompts.py with 4-6 @prompt functions auto-discovered by FileSystemProvider
- [x] **PR-02**: Guided workflow prompts return list[Message] with user + assistant roles priming multi-tool conversations
- [x] **PR-03**: Quick lookup prompts return str with specific tool name and parameter instructions
- [x] **PR-04**: All prompts accept bilingual lang parameter (Annotated[Literal["en", "fr"]]) and return content in chosen language
- [x] **PR-05**: Every module has a resources.py with 6-10 @resource functions using type-prefixed URIs (data://, docs://, template://)
- [x] **PR-06**: Catalog resources (data://) return valid JSON with bilingual en/fr labels for reference data agents need repeatedly
- [x] **PR-07**: Documentation resources (docs://) return markdown guides for API quirks, naming conventions, and interpretation
- [x] **PR-08**: Template resources (template://) return markdown with {placeholder} syntax for response formatting
- [x] **PR-09**: All resources use zero-parameter functions (not ResourceTemplate) with bilingual content inline
- [x] **PR-10**: Prompts follow module prefix naming convention (boc_, sc_, parl_, wx_, etc.)
- [x] **PR-11**: Resources use type-prefixed URIs: data://module/name, docs://module/name, template://module/name
- [x] **PR-12**: Prompts appear as slash-commands via prompts/list; resources appear via resources/list (native MCP visibility)
- [x] **PR-13**: No server.py changes needed — FileSystemProvider auto-discovers prompts and resources
- [x] **PR-14**: Bank of Canada module has prompts for rate analysis, policy rate lookup, currency comparison, commodity exploration, and inflation check
- [x] **PR-15**: StatCan module has prompts for data discovery, SDMX exploration, vector retrieval, store-and-query, and change monitoring
- [x] **PR-16**: Weather module has a single top-level prompts.py covering all sub-modules (current, climate, marine, hydro, etc.)
- [x] **PR-17**: IRCC, Ontario, and Toronto modules have prompts for their respective data exploration workflows
- [x] **PR-18**: Integration tests verify prompts discoverable via client.list_prompts() and resources via client.read_resource()
- [x] **PR-19**: README updated with prompt catalog (~60 prompts) and resource catalog (~80-100 resources)
- [x] **PR-20**: CLAUDE.md updated with 7-file module pattern and prompt/resource coding conventions

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
- [x] **AB-10**: Agent can get current active wildfires from WMBappServices Active_Wildfires_Dashboard_view FeatureServer with optional fire_status filter
- [x] **AB-11**: Agent can get wildfire perimeters dispatched by status: Literal["active","extinguished"] from WMBappServices simplified-view FeatureServers
- [x] **AB-12**: Historical wildfire data (2006-current CSV) is documented as routed via alberta_query_dataset (CKAN wildfire-data package) — NO dedicated tool
- [x] **AB-13**: Agent can get current province-wide fire bans from WMBappServices alberta_fire_ban_system FeatureServer (the data backend behind albertafirebans.ca)
- [x] **AB-14**: Agent can get fire control orders, OHV restrictions, and forest area boundaries via single tool dispatched by category param (replaces deferred alberta_get_fire_weather since FWI is not publicly published)
- [x] **AB-15**: Agent can get 101 AHS hospitals with zone/IP/ED capability flags from AHSGIS AHS_Hospitals FeatureServer
- [x] **AB-16**: Agent can get EMS station OR PCN clinic locations from AHSGIS via single tool dispatched by facility_type param (subsumes deferred ER wait times — Pitfall 9)
- [x] **AB-17**: Agent can get 5 AHS zone boundaries (South, Calgary, Central, Edmonton, North) with POP2006/2011/2016 population from AHS_Zone FeatureServer
- [x] **AB-18**: Agent can get current road events (closures, construction, incidents) from 511 Alberta v2 API at /api/v2/get/event with optional event_type filter
- [x] **AB-19**: Agent can get current winter road conditions (~1121 records) from 511 Alberta v2 API at /api/v2/get/winterroads with optional area_name filter
- [x] **AB-20**: Agent can get traffic camera locations and snapshot URLs (~376 cameras) from 511 Alberta v2 API at /api/v2/get/cameras
- [x] **AB-21**: Agent can get 75 air quality monitoring stations with current pollutant readings (SO2/H2S/TRS/O3/NO2/CO/PM2.5/etc.) from GeoDiscover Alberta AQHI MapServer layer 1
- [x] **AB-22**: Agent can get water management advisories dispatched by advisory_type: Literal["river","water_management","drought","ice_cover","water_sharing"] from GeoDiscover river forecast centre FeatureServer
- [x] **AB-23**: Water licence registry (87MB+ active, 169MB+ inactive) is exposed as discovery-only via alberta_search_datasets / alberta_get_dataset_details with row-filter requirement documented in tool docstring + docs://alberta/wildfire-data-guide resource
- [x] **AB-24**: Agent can get historical major crop production statistics (2000-2014 Alberta Official Statistic) from open.alberta.ca CKAN major-crop-production-alberta package CSV
- [x] **AB-25**: Agent can get population estimates with optional breakdown: csd (default) / quarterly / annual / age_sex / sub_provincial / components_of_growth — complementing StatCan (Alberta provides CSD-level municipal; StatCan provides CMA-level only)
- [x] **AB-26**: Agent can get all Alberta provincial parks and protected areas from GeoDiscover boundary/parks_protected_areas_alberta FeatureServer
- [x] **AB-27**: All Alberta tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, alberta_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

### Manitoba Government Open Data

Primary portal is **geoportal.gov.mb.ca** ArcGIS Hub (ArcGIS Online org `mMUesHYPkXjaFGfS`) — NOT a CKAN instance. Follows the Alberta Phase 17 / York Region Phase 14 ArcGIS Hub pattern via `shared/arcgis_hub.py`. Module prefix `manitoba_`.

- [x] **MB-01**: Agent can search Manitoba's geoportal.gov.mb.ca ArcGIS Hub catalogue by keyword with optional category filter and pagination (Hub Search API `/api/search/v1/collections/all/items`)
- [x] **MB-02**: Agent can get full details for a Manitoba dataset by ID, including FeatureServer URL, download URLs, and metadata (ArcGIS Hub item detail endpoint)
- [x] **MB-03**: Agent can query a Manitoba dataset via auto-router — routes ESRI FeatureServer → arcgis_hub.query_feature_service; CSV/JSON/GeoJSON/XLSX → fetch_and_parse; other → metadata-only (same hybrid router as Alberta Phase 17)
- [x] **MB-04**: Agent can list Manitoba government organizations publishing on the geoportal (ArcGIS Hub groups/organizations endpoint)
- [x] **MB-05**: Agent can list dataset categories/tags on the Manitoba geoportal (ArcGIS Hub tags/categories)
- [x] **MB-06**: Agent can get Manitoba provincial parks and protected areas (93 parks, bilingual NAME_E/NOM_F, polygon boundaries) from `Manitoba_Parks` FeatureServer with optional park_type filter
- [x] **MB-07**: Agent can get flood alerts (overland flooding watch/warning polygons, bilingual Type_EN/Type_FR) from `Overland_Flood_Alerts` FeatureServer — returns empty when no alerts active (correct, not an error)
- [x] **MB-08**: Agent can get Manitoba river/hydrometric station locations with flood watch/warning status from the Manitoba River Conditions and Forecasts FeatureServer (station discovery, not real-time level readings)
- [x] **MB-09**: Agent can get provincial waterways (dikes, floodways, diversions, dams, reservoirs — F_TYPE coded domain) from `Provincial_Waterways` FeatureServer with optional f_type filter
- [x] **MB-10**: Agent can get current drought monitor status for Manitoba (D0-D4 polygon classes) from `Canada_USA_Drought_Monitor` FeatureServer with default Manitoba bbox filter
- [x] **MB-11**: Agent can get Manitoba agricultural weather station locations (100+ stations with AgRegion and per-station URL to live hourly readings) from `WeatherStations` FeatureServer
- [x] **MB-12**: Agent can get Manitoba cattle/hog market prices (current year and historical weekly prices) from the `MB_Cattle_Prices_Current_year` FeatureServer + hog price service, dispatched by livestock param
- [x] **MB-13**: Agent can get crop reporting region boundaries for Manitoba (bilingual REGION/RÉGION fields) from `MbAg_Crop_Reporting_Regions` FeatureServer
- [x] **MB-14**: Agent can get Manitoba diagnostic and surgical wait time averages by procedure and year from `Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages` FeatureServer
- [x] **MB-15**: Agent can get Manitoba fisheries/waterbody reference data (350+ water bodies with species, fishing regulations, stocking records, Secchi depth) from `Manitoba_Waterbody_Data` FeatureServer
- [x] **MB-16**: Agent can get Manitoba provincial forest boundaries from `Manitoba_Provincial_Forests___Version_6` FeatureServer; AND agent can get Manitoba rural health care facilities (ED/acute care/PCH flags by RHA) from the Rural Health Care Facilities FeatureServer (URL resolved in Wave 0)
- [x] **MB-17**: Transport / Manitoba 511 — agent can get road events, winter road conditions, and traffic cameras from Manitoba 511 API v3 (key required). Tools ship with NOT_CONFIGURED behaviour when MANITOBA_511_KEY env var is absent; live integration deferred if key is not freely obtainable (resolved in Wave 0 spike)
- [x] **MB-18**: All Manitoba tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, manitoba_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

### Saskatchewan Government Open Data

Primary portal is **geohub.saskatchewan.ca** ArcGIS Hub (ArcGIS Online org `zcv98lgAl8xQ04cW`) — NOT a CKAN instance (`data.saskatchewan.ca` does not exist). Water infrastructure is on the separate WSA ArcGIS Hub (org `7MBdlVpjqbfBhQer`); wildfire/fire-ban data is on the SPSA ArcGIS REST server (`gis.saskatchewan.ca/egis`). Follows the Manitoba Phase 18 / Alberta Phase 17 ArcGIS Hub pattern via `shared/arcgis_hub.py`. Module prefix `saskatchewan_`. Transport (Highway Hotline 511) is DEFERRED — key-gated; no NOT_CONFIGURED stubs. Health is DEFERRED — no public SHA facility FeatureServer.

- [x] **SK-01**: Agent can search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue by keyword with optional category filter and pagination (Hub Search API `/api/search/v1/collections/all/items`, OGC API Records `limit`/`startindex` params)
- [x] **SK-02**: Agent can get full details for a Saskatchewan GeoHub dataset by ID, including FeatureServer URL, download links, and metadata (ArcGIS Hub item detail endpoint)
- [x] **SK-03**: Agent can query a Saskatchewan dataset via auto-router — routes ESRI FeatureServer → arcgis_hub.query_feature_service; CSV/JSON/GeoJSON/XLSX → fetch_and_parse; other → metadata-only (same hybrid router as Alberta Phase 17 / Manitoba Phase 18)
- [x] **SK-04**: Agent can list Saskatchewan government organizations publishing on the geoportal (ArcGIS Hub organizations endpoint)
- [x] **SK-05**: Agent can list dataset categories on the Saskatchewan geoportal (ArcGIS Hub tags/categories)
- [x] **SK-06**: Agent can get estimated crop yields by crop type and region (provincial summary + 5 crop reporting regions: Southeast, Southwest, Central, Northeast, Northwest; 16 crop types incl. Canola, HRSW, Durum, Lentil, Chickpea, Pea) from the `Provincial_Estimated_Crop_Yields` FeatureServers
- [x] **SK-07**: Agent can get grain elevator locations for Saskatchewan (station, railway, licensee, capacity in tonnes) from the `Western_Canada_Grain_Elevator_2024` FeatureServer with default `where=PR='SK'` and optional railway filter
- [x] **SK-08**: Agent can get potash mine locations with company, status, mine type, and date opened from the Saskatchewan mineral deposit index `Potash_2024_06_13` FeatureServer
- [x] **SK-09**: Agent can get mineral mine locations dispatched by mineral type (potash, uranium, helium, coal) from the dated Saskatchewan mineral deposit FeatureServers, returning Name, Company, Status, Mine_Type, DateOpened
- [x] **SK-10**: Agent can get current live ambient air quality readings (hourly) across Saskatchewan monitoring stations (PM2.5, NO2, O3, SO2, CO, H2S, AQHI link) from the `Hourly_Ambient_Air_Quality` FeatureServer with optional community filter
- [x] **SK-11**: Agent can get current fire ban status dispatched by ban_scope (urban/rural/provincial/parks → layers 0/2/3/8) from the SPSA `Public_Fire_Ban` FeatureServer (`gis.saskatchewan.ca/egis` — separate REST server, not the Hub); empty result in off-season is valid, not an error
- [x] **SK-12**: Agent can get historical wildfire boundaries for Saskatchewan with optional year/cause filters (YEAR, FIRENAME, CAUSE1, HECTARES, STATUS) from the `Historic_Wildfire_Boundaries` FeatureServer
- [x] **SK-13**: Agent can get WSA hydrometric gauging station locations with major basin, station class, operated-by, and HyperLink_Graph URL to live readings from the `Hydrometric_Gauging_Stations_V2` FeatureServer (WSA org `7MBdlVpjqbfBhQer`, `where=Province='SK'`)
- [x] **SK-14**: Agent can get WSA reservoir locations with reservoir names and dam names from the `WSA_Reservoirs` FeatureServer (WSA org, layer 26 — NOT layer 0)
- [x] **SK-15**: All Saskatchewan tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, saskatchewan_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

### Nova Scotia Government Open Data

Primary portal is **data.novascotia.ca** — a **Socrata** (Tyler Technologies) open-data platform exposing the keyless **SODA API** (`/api/catalog/v1` discovery, `/resource/{id}.json` SoQL reads). Socrata is a NEW (4th) portal technology for this codebase (after CKAN, ArcGIS Hub, OGC WFS), served by the new reusable `shared/socrata.py` client. Module prefix `ns_`. Transport / 511 is DEFERRED (HTML-only, no clean feed; no NOT_CONFIGURED stubs). NS ArcGIS Hub (novagis) is DEFERRED (no public no-auth FeatureServers confirmed). Geospatial datasets come through Socrata; geometry (`the_geom`) excluded via explicit `$select` in curated tools.

- [x] **NS-01**: `shared/socrata.py` provides a reusable SODA client — `search_catalog(domain, q, limit, offset, only)`, `get_dataset_metadata(domain, dataset_id)`, `query_dataset(domain, dataset_id, where, select, order, limit, offset, q, group)`, and `shape_catalog_result(result)` — returning parsed dicts (consistent with the `api_get` parsed-dict contract), with an optional `X-App-Token` slot (keyless default), `httpx_client` injection, and no caching/rate-limiting inside the shared client. Adds Socrata as the 4th Portal Technologies row in CLAUDE.md.
- [x] **NS-02**: Agent can search Nova Scotia's data.novascotia.ca Socrata catalogue by keyword with pagination (`/api/catalog/v1?domains=data.novascotia.ca&q=...&limit=...&offset=...&only=datasets`)
- [x] **NS-03**: Agent can get full metadata (schema columns, attribution, license) for a specific Nova Scotia dataset by ID via `/api/views/{id}.json`
- [x] **NS-04**: Agent can run a SoQL query against any Nova Scotia dataset via `/resource/{id}.json` with `$where`, `$select`, `$order`, `$limit`, `$offset`, `$q`, `$group` (geometry inclusion controlled via `$select`)
- [x] **NS-05**: Agent can list Nova Scotia government organizations (publishers/attributions) that publish on data.novascotia.ca (derived from catalog `owner`/`attribution`/`domain_metadata`)
- [x] **NS-06**: Agent can list Nova Scotia data categories — the catalog `categories=` param is BROKEN (returns 0 live); `ns_list_categories` MUST use `q=` + client-side `classification.domain_category` aggregation, returning 20+ categories incl. "Fishing and Aquaculture"
- [x] **NS-07**: Agent can get Nova Scotia marine aquaculture lease locations (`h57h-p9mm`) with license_le, ownership, species, waterbody, county, sitestatus, speciestyp, hectares, lat_dms, long_dms — geometry (`the_geom`) excluded via `$select`
- [x] **NS-08**: Agent can get Nova Scotia landbased aquaculture licenses (`yqwg-f62a`) with license_le, species, speciestyp, county, ownership, sitestatus, lat_dms, long_dms
- [x] **NS-09**: Agent can get Nova Scotia fish hatchery stocking records (`8e4a-m6fw`) with county, stock, stock_strain, hatchery, fish_length_cm, fish_weight_g, number_released, stocking_date, mark (current to 2025)
- [x] **NS-10**: Agent can get Nova Scotia aquaculture production, value, and employment data by county and year (`v2ex-ev63`) with year, county, kgs, total_value, full_time, total_employ
- [x] **NS-11**: Agent can get Nova Scotia surface water quality continuous monitoring readings (`bkfi-mjgw`) with station_number, date, time, temperature_c, ph, specific_conductance_s_cm, dissolved_oxygen_mg_l
- [x] **NS-12**: Agent can get Nova Scotia boil water advisories (`7t68-9xmm`) with site_name, county, date_advisory_issued, date_advisory_removed, facility_type, length_of_advisory; active-advisory filter resolved by Wave 0 spike (NULL vs empty string for date_advisory_removed)
- [x] **NS-13**: Agent can get Nova Scotia hospital and long-term care facility locations dispatched by facility_type: Literal["hospital","long_term_care"] (Hospitals `tmfr-3h8a` + LTC/RCF `x76a-axw2`) with facility name, address, town, county, type, zone, beds, coordinates
- [x] **NS-14**: Agent can get Nova Scotia vital statistics (`r794-fttm`) — births, deaths, rates, natural increase — by county and year (counties UPPERCASE; year is text)
- [x] **NS-15**: Agent can get Nova Scotia protected areas (`ticv-5du5`) with pro_name, protect1, symbol, owner, authority, status, web_url, ha_gis — geometry excluded via `$select`
- [x] **NS-16**: Agent can get Nova Scotia ambient air quality monitoring station locations (`3bbm-drnh`) with station_name, city, latitude, longitude, measurements, monitoring_period (reference catalog; individual pollutant time series are discovery-only via ns_query_dataset)
- [x] **NS-17**: Agent can get Nova Scotia chronic disease prevalence dispatched by disease: Literal["ami","diabetes","copd","hypertension","asthma"] (`24qf-ntke`, `cumi-sw99`, `ua9e-4pss`, `sztc-sewr`, `2bih-5dgk`) with year, zone (normalized from health_zone/zone), sex, agegroup, population, crude_prevalence_rate; invalid disease returns INVALID_INPUT
- [x] **NS-18**: All Nova Scotia tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, ns_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider

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
| Manitoba Hydro / energy domain | hydro.mb.ca water levels are HTML-only (no API/CSV); dropped — substituted by drought monitor + ag weather |
| Manitoba Land Initiative (mli.gov.mb.ca) | Retired 2022-02-09; superseded by geoportal.gov.mb.ca |
| Manitoba Hydrologic Forecast Centre flood bulletins | PDF/HTML only — no machine-readable endpoint; use Overland_Flood_Alerts FeatureServer instead |

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
| IRCC-01 | Phase 11 | Complete |
| IRCC-02 | Phase 11 | Complete |
| IRCC-03 | Phase 11 | Complete |
| IRCC-04 | Phase 11 | Complete |
| IRCC-05 | Phase 11 | Complete |
| IRCC-06 | Phase 11 | Complete |
| IRCC-07 | Phase 11 | Complete |
| IRCC-08 | Phase 11 | Complete |
| IRCC-09 | Phase 11 | Complete |
| ONT-01 | Phase 12 | Complete |
| ONT-02 | Phase 12 | Complete |
| ONT-03 | Phase 12 | Complete |
| ONT-04 | Phase 12 | Complete |
| ONT-05 | Phase 12 | Complete |
| ONT-06 | Phase 12 | Complete |
| ONT-07 | Phase 12 | Complete |
| ONT-08 | Phase 12 | Complete |
| TOR-01 | Phase 13 | Complete |
| TOR-02 | Phase 13 | Complete |
| TOR-03 | Phase 13 | Complete |
| TOR-04 | Phase 13 | Complete |
| TOR-05 | Phase 13 | Complete |
| TOR-06 | Phase 13 | Complete |
| TOR-07 | Phase 13 | Complete |
| TOR-08 | Phase 13 | Complete |
| TOR-09 | Phase 13 | Complete |
| TOR-10 | Phase 13 | Complete |
| TOR-11 | Phase 13 | Complete |
| TOR-12 | Phase 13 | Complete |
| YR-01 | Phase 14 | Complete |
| YR-02 | Phase 14 | Complete |
| YR-03 | Phase 14 | Complete |
| YR-04 | Phase 14 | Complete |
| YR-05 | Phase 14 | Complete |
| YR-06 | Phase 14 | Complete |
| YR-07 | Phase 14 | Complete |
| YR-08 | Phase 14 | Complete |
| YR-09 | Phase 14 | Complete |
| YR-10 | Phase 14 | Complete |
| YR-11 | Phase 14 | Complete |
| YR-12 | Phase 14 | Complete |
| YR-13 | Phase 14 | Complete |
| YR-14 | Phase 14 | Complete |
| BC-01 | Phase 15 | Complete |
| BC-02 | Phase 15 | Complete |
| BC-03 | Phase 15 | Complete |
| BC-04 | Phase 15 | Complete |
| BC-05 | Phase 15 | Complete |
| BC-06 | Phase 15 | Complete |
| BC-07 | Phase 15 | Complete |
| BC-08 | Phase 15 | Complete |
| BC-09 | Phase 15 | Complete |
| BC-10 | Phase 15 | Complete |
| BC-11 | Phase 15 | Complete |
| BC-12 | Phase 15 | Complete |
| BC-13 | Phase 15 | Complete |
| BC-14 | Phase 15 | Complete |
| BC-15 | Phase 15 | Complete |
| BC-16 | Phase 15 | Complete |
| BC-17 | Phase 15 | Complete |
| BC-18 | Phase 15 | Complete |
| BC-19 | Phase 15 | Complete |
| BC-20 | Phase 15 | Complete |
| BC-21 | Phase 15 | Complete |
| BC-22 | Phase 15 | Complete |
| QC-01 | Phase 16 | Complete |
| QC-02 | Phase 16 | Complete |
| QC-03 | Phase 16 | Complete |
| QC-04 | Phase 16 | Complete |
| QC-05 | Phase 16 | Complete |
| QC-06 | Phase 16 | Complete |
| QC-07 | Phase 16 | Complete |
| QC-08 | Phase 16 | Complete |
| QC-09 | Phase 16 | Complete |
| QC-10 | Phase 16 | Complete |
| QC-11 | Phase 16 | Complete |
| QC-12 | Phase 16 | Complete |
| QC-13 | Phase 16 | Complete |
| QC-14 | Phase 16 | Complete |
| QC-15 | Phase 16 | Complete |
| QC-16 | Phase 16 | Complete |
| QC-17 | Phase 16 | Complete |
| QC-18 | Phase 16 | Complete |
| QC-19 | Phase 16 | Complete |
| TEST-01 | Phase 20.1 | Complete |
| TEST-02 | Phase 20.1 | Complete |
| TEST-03 | Phase 20.1 | Complete |
| TEST-04 | Phase 20.1 | Complete |
| TEST-05 | Phase 20.1 | Complete |
| ERR-01 | Phase 20.2 | Complete |
| ERR-02 | Phase 20.2 | Complete |
| ERR-03 | Phase 20.2 | Complete |
| ERR-04 | Phase 20.2 | Complete |
| PR-01 | Phase 40 | Complete |
| PR-02 | Phase 40 | Complete |
| PR-03 | Phase 40 | Complete |
| PR-04 | Phase 40 | Complete |
| PR-05 | Phase 40 | Complete |
| PR-06 | Phase 40 | Complete |
| PR-07 | Phase 40 | Complete |
| PR-08 | Phase 40 | Complete |
| PR-09 | Phase 40 | Complete |
| PR-10 | Phase 40 | Complete |
| PR-11 | Phase 40 | Complete |
| PR-12 | Phase 40 | Complete |
| PR-13 | Phase 40 | Complete |
| PR-14 | Phase 40 | Complete |
| PR-15 | Phase 40 | Complete |
| PR-16 | Phase 40 | Complete |
| PR-17 | Phase 40 | Complete |
| PR-18 | Phase 40 | Complete |
| PR-19 | Phase 40 | Complete |
| PR-20 | Phase 40 | Complete |
| AB-01 | Phase 17 | Complete |
| AB-02 | Phase 17 | Complete |
| AB-03 | Phase 17 | Complete |
| AB-04 | Phase 17 | Complete |
| AB-05 | Phase 17 | Complete |
| AB-06 | Phase 17 | Complete |
| AB-07 | Phase 17 | Complete |
| AB-08 | Phase 17 | Complete |
| AB-09 | Phase 17 | Complete |
| AB-10 | Phase 17 | Complete |
| AB-11 | Phase 17 | Complete |
| AB-12 | Phase 17 | Complete |
| AB-13 | Phase 17 | Complete |
| AB-14 | Phase 17 | Complete |
| AB-15 | Phase 17 | Complete |
| AB-16 | Phase 17 | Complete |
| AB-17 | Phase 17 | Complete |
| AB-18 | Phase 17 | Complete |
| AB-19 | Phase 17 | Complete |
| AB-20 | Phase 17 | Complete |
| AB-21 | Phase 17 | Complete |
| AB-22 | Phase 17 | Complete |
| AB-23 | Phase 17 | Complete |
| AB-24 | Phase 17 | Complete |
| AB-25 | Phase 17 | Complete |
| AB-26 | Phase 17 | Complete |
| AB-27 | Phase 17 | Complete |
| MB-01 | Phase 18 | Complete |
| MB-02 | Phase 18 | Complete |
| MB-03 | Phase 18 | Complete |
| MB-04 | Phase 18 | Complete |
| MB-05 | Phase 18 | Complete |
| MB-06 | Phase 18 | Complete |
| MB-07 | Phase 18 | Complete |
| MB-08 | Phase 18 | Complete |
| MB-09 | Phase 18 | Complete |
| MB-10 | Phase 18 | Complete |
| MB-11 | Phase 18 | Complete |
| MB-12 | Phase 18 | Complete |
| MB-13 | Phase 18 | Complete |
| MB-14 | Phase 18 | Complete |
| MB-15 | Phase 18 | Complete |
| MB-16 | Phase 18 | Complete |
| MB-17 | Phase 18 | Complete |
| MB-18 | Phase 18 | Complete |
| SK-01 | Phase 19 | Complete |
| SK-02 | Phase 19 | Complete |
| SK-03 | Phase 19 | Complete |
| SK-04 | Phase 19 | Complete |
| SK-05 | Phase 19 | Complete |
| SK-06 | Phase 19 | Complete |
| SK-07 | Phase 19 | Complete |
| SK-08 | Phase 19 | Complete |
| SK-09 | Phase 19 | Complete |
| SK-10 | Phase 19 | Complete |
| SK-11 | Phase 19 | Complete |
| SK-12 | Phase 19 | Complete |
| SK-13 | Phase 19 | Complete |
| SK-14 | Phase 19 | Complete |
| SK-15 | Phase 19 | Complete |
| NS-01 | Phase 20 | Complete |
| NS-02 | Phase 20 | Complete |
| NS-03 | Phase 20 | Complete |
| NS-04 | Phase 20 | Complete |
| NS-05 | Phase 20 | Complete |
| NS-06 | Phase 20 | Complete |
| NS-07 | Phase 20 | Complete |
| NS-08 | Phase 20 | Complete |
| NS-09 | Phase 20 | Complete |
| NS-10 | Phase 20 | Complete |
| NS-11 | Phase 20 | Complete |
| NS-12 | Phase 20 | Complete |
| NS-13 | Phase 20 | Complete |
| NS-14 | Phase 20 | Complete |
| NS-15 | Phase 20 | Complete |
| NS-16 | Phase 20 | Complete |
| NS-17 | Phase 20 | Complete |
| NS-18 | Phase 20 | Complete |

**Coverage:**
- v1 requirements: 73 total (added 27 Alberta requirements in Phase 17)
- Mapped to phases: 73
- Unmapped: 0
- York Region requirements: 14 total (Phase 14)
- IRCC requirements: 9 total (Phase 11)
- Ontario requirements: 8 total (Phase 12)
- Toronto requirements: 12 total (Phase 13)
- Alberta requirements: 27 total (Phase 17)
- Manitoba requirements: 18 total (Phase 18)
- Saskatchewan requirements: 15 total (Phase 19)
- Nova Scotia requirements: 18 total (Phase 20)
- Prompts & Resources requirements: 20 total (Phase 40)

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-06-15 after Phase 20 planning (added NS-01…NS-18)*
