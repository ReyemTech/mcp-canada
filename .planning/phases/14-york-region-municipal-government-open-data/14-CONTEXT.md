# Phase 14: York Region Municipal Government Open Data - Context

**Gathered:** 2026-04-10
**Updated:** 2026-04-10 (scope adjusted post-research — 6 municipalities have no public portal)
**Status:** Ready for planning

<domain>
## Phase Boundary

Add York Region's municipal open data to mcp-canada. York Region uses **ArcGIS Hub** (Esri), not CKAN — this is the FIRST ArcGIS Hub module in the project and requires building new shared infrastructure. Covers **4 verified ArcGIS Hub portals**: York Region regional government + Markham + Newmarket + Aurora. Research confirmed that Vaughan, Richmond Hill, King, East Gwillimbury, Whitchurch-Stouffville, and Georgina do NOT have public ArcGIS Hub portals and are explicitly out of scope.

</domain>

<decisions>
## Implementation Decisions

### API strategy
- Use ArcGIS REST Feature Service API directly via httpx — NO new dependency
- Explicitly rejected: `arcgis` Python SDK (~800MB dependency footprint with numpy/pandas/shapely/GDAL transitive deps — violates no-new-deps policy)
- Use `&f=geojson` query parameter to get native GeoJSON responses (reuses existing `_parse_geojson` from shared/parsers.py added in Phase 13)
- Server-side filtering via simplified named parameters (ward=, category=, min_year=) that the client translates to ArcGIS WHERE clauses internally — agents don't need SQL knowledge
- Auto-paginate with a cap (max 5000 records per tool call), return `truncated: true` flag when cap hit

### Federation scope (REVISED post-research)
- Single `src/mcp_canada/modules/york_region/` module covering **4 verified portals** (down from 10)
- Tool prefixes per portal: `york_region_`, `markham_`, `newmarket_`, `aurora_`
- All 4 portals get the same 5 discovery tools: search_datasets, get_dataset_details, query_features, list_organizations, list_categories
- **Out of scope (no public portals exist):** Vaughan, Richmond Hill, King, East Gwillimbury, Whitchurch-Stouffville, Georgina — these can be added as their own future phases if portals become available
- Portal base URLs stored in constants.py per-portal mapping

### Curated datasets (REVISED post-research)
- **York Region regional portal** gets 5 curated areas: transit (YRT/Viva stops + routes via Feature Service, no licensed GTFS), road network, census/demographics (2021 DA-level), public health/safety (beach water, hospitals), waste management
- **Markham** gets 2 curated tools: civic addresses + road network (SLRN) — URLs verified
- **Newmarket and Aurora:** discovery-only (small portals, 61 and 21 items respectively)
- YRT/Viva transit: use ArcGIS Feature Services only — skip the licensed GTFS feed (avoids license dependency)

### Geometry handling
- Properties-only by default, opt-in `include_geometry=true` parameter — same pattern as Phase 13 GeoJSON parser
- When geometry is requested, return native GeoJSON (requested from API via `&f=geojson`)

### Shared infrastructure
- Create `shared/arcgis_hub.py` as a reusable ArcGIS REST Feature Service client
- Future ArcGIS Hub modules (likely British Columbia, several other cities) reuse it — same way Ontario's CKAN client effectively templated Toronto's
- york_region/client.py wraps shared/arcgis_hub.py with portal-specific constants
- Catalog search via `/api/search/v1/collections/all/items` (research-verified endpoint — the previously assumed `/api/v2/datasets` returns 404)
- Fetch layer metadata first to read `maxRecordCount` before paginating (varies: 1000 for Transportation Layer 2, 2000 for most others)

### Prompts and Resources (Phase 40 pattern)
- Include prompts.py and resources.py from the start (7-file pattern, not retrofit)
- 4-6 bilingual prompts total covering discovery workflows + regional curated data (transit, health, roads)
- 6-10 resources: portal catalog (list of all 10 portals with URLs), municipality list with population/area, dataset naming conventions docs, response templates

### Claude's Discretion
- Exact dataset IDs and Feature Service URLs per portal (discovered during research)
- Whether to wrap the ArcGIS REST client as a context manager or bare async functions
- How to handle Feature Services with non-standard field names (ESRI systems often use ALL_CAPS or `OBJECTID`)
- Exact shape of WHERE clause translation (LIKE vs =, case sensitivity)
- Whether to expose MapServer endpoints in addition to FeatureServer endpoints

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/parsers.py` — `_parse_geojson()` and `_parse_json()` added in Phase 13 work directly with ArcGIS Feature Service `&f=geojson` responses
- `shared/cache.py` — `cached_fetch()` for all client functions
- `shared/rate_limiter.py` — `get_limiter()` per-source TokenBucket (one per portal or one shared `arcgis_hub` group)
- `shared/envelope.py` — `make_response()`/`make_error()` for all tool returns
- `shared/i18n.py` — `t(key, lang)` bilingual message system
- `src/mcp_canada/modules/toronto/` — established municipal tool structure with curated + discovery split
- `src/mcp_canada/modules/ontario/` — established CKAN client pattern (different API but similar architecture)

### Established Patterns
- Module structure: 7-file pattern (__init__, constants, schemas, client, tools, prompts, resources) after Phase 40
- Tool prefix = full municipality name
- BM25 docstrings: `Use for:` + `Keywords:` on single lines
- Bilingual `lang: Literal["en", "fr"] = "en"` on every @tool
- All client functions return `(data, was_cached)` tuples
- Aggressive response flattening — Pydantic models are flat, not mirror API nesting
- Standalone `@tool` from fastmcp.tools (NEVER `@mcp.tool`)

### Integration Points
- New: `shared/arcgis_hub.py` — reusable ArcGIS REST client (sibling of existing shared/ utilities)
- `tests/integration/test_tool_scenarios.py` — append `TestYorkRegionToolScenarios` class
- `tests/integration/test_prompts_resources_scenarios.py` — add york_region prompt/resource checks
- `README.md` — add York Region section, update tool count (currently 128 tools → ~195 with ~65 new tools)
- `CLAUDE.md` — mention ArcGIS Hub as a second portal technology alongside CKAN

</code_context>

<specifics>
## Specific Ideas

- York Region regional portal: `https://insights-york.opendata.arcgis.com/`
- Markham portal: `https://data-markham.opendata.arcgis.com/`
- Aurora portal: `https://opendata-cityofaurora.hub.arcgis.com/`
- Other local portals: URLs to be confirmed during research
- ArcGIS REST Feature Service pattern: `{portal_base}/arcgis/rest/services/{service_name}/FeatureServer/{layer_id}/query?where=...&outFields=*&f=geojson`
- Hub catalog search: `{portal_base}/api/v2/datasets?filter[source]={org_id}&q={keyword}`
- Max records per request: typically 1000-2000 (varies by Feature Service configuration — detect via `maxRecordCount` metadata)
- York Region is a two-tier government — regional data (transit, health, roads, demographics) vs local data (addresses, zoning, building permits)
- Tool count estimate (REVISED): 5 discovery × 4 portals + 5 curated (York Region) + 2 curated (Markham) = ~27 tools

</specifics>

<deferred>
## Deferred Ideas

- Vaughan municipal open data — no public ArcGIS Hub or CKAN portal exists as of 2026-04. Re-evaluate when portal becomes available.
- Richmond Hill municipal open data — same as Vaughan, no public portal.
- King Township, East Gwillimbury, Whitchurch-Stouffville (general), Georgina — no standalone open data portals. Revisit if they publish portals.
- YRT/Viva real-time GTFS feed — requires license agreement with YRT. Could be added later as a separate phase if license is obtained.

</deferred>

---

*Phase: 14-york-region-municipal-government-open-data*
*Context gathered: 2026-04-10*
