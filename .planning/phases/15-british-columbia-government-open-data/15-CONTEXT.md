# Phase 15: British Columbia Government Open Data - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Add British Columbia's provincial open data catalogue to mcp-canada. BC uses **CKAN** at `catalogue.data.gov.bc.ca` (DataBC, bcgov custom extensions) PLUS a unique **WMS/WFS geospatial layer** at `openmaps.gov.bc.ca` (BC Geographic Warehouse). The phase bridges CKAN discovery with WFS feature queries in a two-step workflow: discover datasets via CKAN, then query actual features via WFS using the dataset's `object_name`. BC municipalities (Vancouver, Victoria, Surrey, Burnaby, etc.) are explicitly out of scope — separate future phases.

</domain>

<decisions>
## Implementation Decisions

### Platform architecture
- Use the BC Data Catalogue (BCDC) CKAN API at `https://catalogue.data.gov.bc.ca/api/3/action/` — standard CKAN + bcgov extensions
- Add WFS (Web Feature Service) support for the 870 geospatial datasets hosted in the BC Geographic Warehouse (BCGW) via `https://openmaps.gov.bc.ca/geo/ows`
- NOT included: WMS (returns PNG map tiles, not queryable data — defer to future phase if needed)
- Two-step workflow: `bc_search_datasets` (CKAN) → `bc_get_dataset_details` (returns object_name + `queryable_via_wfs` flag) → `bc_query_features` (WFS or file parser depending on resource format)
- For non-BCGW datasets (CSV, XLSX, PDF), reuse `shared/parsers.fetch_and_parse()` (already handles these)

### Shared infrastructure
- Create `shared/ogc.py` as a reusable WFS client — BC is the first OGC user, but Quebec and other provinces may follow (same strategic decision as Phase 14's `shared/arcgis_hub.py`)
- WFS client supports: GetCapabilities, GetFeature with CQL filters, GeoJSON output via `outputFormat=application/json`
- Separate from `shared/arcgis_hub.py` — WFS and ArcGIS REST are superficially similar but protocol-incompatible

### Filtering and response shape
- CQL (Common Query Language) filter strings — simple SQL-like syntax (`POP_2021 > 10000 AND REGION = 'Vancouver Island'`)
- Simplified named parameters in tool layer translate to CQL internally (agents don't need CQL knowledge)
- Auto-paginate with 5000-record cap, return `truncated: true` flag when cap hit (same as Phase 14)
- Properties-only by default, opt-in `include_geometry=true` parameter
- WFS requires GeoJSON output format to reuse existing `_parse_geojson` from `shared/parsers.py`

### Curated datasets (~20 tools target)
- **Forestry:** forest tenure, cut blocks, protected areas — BC's most politically significant data, publicly available
- **Wildfire:** active fires (current incidents) + historical fire perimeters by year/region — high query volume during fire season
- **Environment:** water quality monitoring stations, air quality (provincial network), provincial parks
- **Natural resources:** mining tenure, fisheries licenses
- **Health:** hospital locations, epidemiology summaries
- **Transportation:** BC Transit (provincial, not Vancouver TransLink), highways
- **Climate:** climate stations, long-term normals

### Discovery tools
- 5 standard CKAN discovery tools: `bc_search_datasets`, `bc_get_dataset_details`, `bc_query_features`, `bc_list_organizations`, `bc_list_categories`
- `bc_get_dataset_details` MUST surface the `object_name` field and a `queryable_via_wfs` boolean flag so agents know which datasets can be queried directly
- Tool prefix: `bc_` (consistent with full-name-like pattern; `british_columbia_` too long)

### Tool count estimate
- 5 CKAN discovery + ~15 curated (3 forestry + 2 wildfire + 3 environment + 2 natural resources + 2 health + 2 transportation + 1 climate) = **~20 tools total**

### Prompts and Resources (Phase 40 pattern)
- Include prompts.py and resources.py from the start (7-file pattern)
- **6 bilingual prompts:** `bc_explore_wildfires` (guided workflow), `bc_explore_forestry` (guided), `bc_explore_environment` (guided), `bc_quick_dataset_search` (lookup), `bc_check_water_quality` (lookup), `bc_wildfire_status_now` (lookup)
- **7 resources:** `data://bc/ministries` (catalog), `data://bc/wildfire-status-codes` (catalog), `data://bc/object-name-prefixes` (BCGW schema reference), `docs://bc/wfs-query-guide` (markdown: explains the CKAN → WFS two-step workflow), `docs://bc/bcdc-api-quirks` (markdown), `template://bc/wildfire-report`, `template://bc/dataset-report`
- Dedicated `docs://bc/wfs-query-guide` is critical — agents need to understand the two-step workflow

### Claude's Discretion
- Exact CKAN organization filter strategies for BC (many ministries with overlapping scopes)
- Which specific forestry datasets to curate (tenure detail varies — pick the most agent-friendly)
- Wildfire perimeter dataset selection (multiple historical layers exist)
- How to handle WFS `GetCapabilities` caching (large XML response, changes infrequently)
- CQL filter escaping and injection prevention patterns
- Whether `bc_query_features` should auto-detect WFS vs file download based on resource format, or require explicit routing
- Exact simplified parameter names for common filters (e.g., `region=`, `year=`, `status=`)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/ontario/` — established CKAN client pattern for provincial data catalogue; copy structure and swap BASE_URL
- `src/mcp_canada/modules/toronto/` — another CKAN reference with datastore_search patterns
- `shared/parsers.py` — `_parse_geojson()`, `_parse_json()`, `fetch_and_parse()` handle CSV/XLSX/GeoJSON/JSON from file URLs
- `shared/arcgis_hub.py` (from Phase 14) — similar in spirit to the new shared/ogc.py, can inform the design (pagination, caching, error handling patterns)
- `shared/cache.py` — `cached_fetch()` for all client functions
- `shared/rate_limiter.py` — `get_limiter()` per-source TokenBucket
- `shared/envelope.py` — `make_response()`/`make_error()` for all tool returns
- `shared/i18n.py` — bilingual message system

### Established Patterns
- Module structure: 7-file pattern (__init__, constants, schemas, client, tools, prompts, resources)
- Tool prefix naming per module (ontario_, toronto_, bc_)
- Bilingual `lang: Literal["en", "fr"] = "en"` on every @tool
- BM25 docstrings with single-line Use-for + Keywords (8+ keywords)
- All client functions return `(data, was_cached)` tuples with caching and rate limiting
- Aggressive response flattening — Pydantic models are flat, not mirrored API nesting
- Standalone `@tool` from `fastmcp.tools` (NEVER `@mcp.tool`)
- Standalone `@prompt` from `fastmcp.prompts` (bilingual, module-prefixed)
- Zero-parameter `@resource` from `fastmcp.resources` (embedded bilingual content)

### Integration Points
- NEW: `src/mcp_canada/shared/ogc.py` — reusable WFS client (sibling of existing shared utilities)
- `tests/integration/test_tool_scenarios.py` — append `TestBcToolScenarios` class
- `tests/integration/test_prompts_resources_scenarios.py` — add bc prompt/resource assertions
- `README.md` — add BC section, update tool count (currently 155 → ~175 with ~20 new tools)
- `CLAUDE.md` — note WMS/WFS/OGC as third portal technology alongside CKAN and ArcGIS Hub

</code_context>

<specifics>
## Specific Ideas

- BC Data Catalogue: `https://catalogue.data.gov.bc.ca/api/3/action/`
- WFS endpoint: `https://openmaps.gov.bc.ca/geo/ows?service=WFS&version=2.0.0&request=GetFeature`
- WFS GeoJSON output: `&outputFormat=application/json`
- CQL filter parameter: `&CQL_FILTER=POP_2021 > 10000`
- BCGW object name pattern: `WHSE_{CATEGORY}.{TABLE_NAME}` (e.g., `WHSE_FOREST_VEGETATION.VEG_COMP_LYR_R1_POLY`)
- Dataset count: ~2,000-4,000 active datasets (Ontario-scale)
- Geospatial dataset count: 870 WMS/WFS-enabled layers
- BC wildfire data: extremely high query volume during summer months
- Most data is under OpenGov License - British Columbia (compatible with agent use)
- bcgov custom CKAN extensions expose additional filter fields: object_name, storage_location, bcdc_type, license_id

</specifics>

<deferred>
## Deferred Ideas

- **WMS GetMap support** — returns PNG map tiles for visual rendering. Useful for passing map images to vision models, but not core agent query flow. Add in a future phase if demanded.
- **Vancouver municipal open data** — separate ArcGIS Hub/Socrata portal at `opendata.vancouver.ca`. Future phase.
- **Victoria, Surrey, Burnaby municipal portals** — each has its own portal, separate future phases.
- **BC-specific fisheries/DFO cross-reference** — federal fisheries data would require coordination with a federal DFO module (not yet planned).
- **BCGW GetCapabilities caching infrastructure** — large XML document, may warrant its own cache tier in a future optimization phase.

</deferred>

---

*Phase: 15-british-columbia-government-open-data*
*Context gathered: 2026-04-10*
