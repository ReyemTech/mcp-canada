# Phase 17: Alberta Government Open Data - Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Alberta's provincial open data surface to mcp-canada. Primary catalogue: **open.alberta.ca** (CKAN). Secondary geospatial portal (e.g., GeoDiscover Alberta ArcGIS Hub, AltaLIS WFS, or none) is **research-confirmed**, not pre-decided. Phase 17 also incorporates **Alberta Energy Regulator (AER)** data as a fully in-scope domain — wells, pipelines, production, and incidents — because Alberta's energy sector is the province's distinguishing data asset. Alberta municipalities (Calgary at Phase 29, Edmonton at Phase 30, Lethbridge, Red Deer, Medicine Hat, etc.) are explicitly deferred to their own future phases. Federal sources (e.g., Environment Canada wildfire feeds) remain out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Platform architecture
- Primary portal: **open.alberta.ca** CKAN. Confirm exact API base URL (`/opendata/api/3/action/` or similar) during research.
- Secondary portal: **let research confirm**. Three candidates ranked by research priority:
  1. GeoDiscover Alberta / ArcGIS Hub — would reuse `shared/arcgis_hub.py` (Phase 14 pattern)
  2. AltaLIS or other Alberta WFS — would reuse `shared/ogc.py` (Phase 15 pattern)
  3. CKAN-only (Quebec Phase 16 pattern) — file-resource parsing via `shared/parsers.fetch_and_parse()`
- Geospatial access: **router picks file-vs-live**. Tool inspects dataset metadata and chooses live WFS/Feature query when the dataset exposes such an endpoint, otherwise falls back to file-resource parsing. Adds one routing layer (similar to BC's `bc_query_features` two-step but auto-detected).
- Module prefix: `alberta_` (full-name pattern, consistent with `quebec_`, `ontario_`, `toronto_`).
- Module name: `alberta`.

### Catalog filter / federation policy
- **Let research confirm structure**. Inspect open.alberta.ca's organization list before deciding default scope:
  - If federated (municipalities, Crown corps, First Nations included) → Quebec pattern: return all orgs by default, document federated nature in `alberta_search_datasets` docstring, agents can filter via `organization` param.
  - If provincial-only by design → no filter needed; default behavior is already clean.
- AER datasets surfaced via federation (if any) will appear alongside native AER tools — document the duplication so agents know which path is preferred.

### Discovery tools (5 standard CKAN, like every prior provincial module)
- `alberta_search_datasets`, `alberta_get_dataset_details`, `alberta_query_dataset`, `alberta_list_organizations`, `alberta_list_categories`
- `alberta_query_dataset` implements the file-vs-live router described above.

### Curated tools — broad scope
**All 8 domains in scope**, with signature-Alberta data getting depth and the BC-density baseline preserved everywhere else:

**Energy / oil & gas (AER, ~4-6 tools — fully in-scope)**
- `alberta_search_wells` — UWI/license/operator/location lookup
- `alberta_get_well_details` — well status, spud date, license, operator
- `alberta_get_pipelines` — registry: location, operator, substance, length
- `alberta_get_production_volumes` — ST3/ST39/ST98 monthly oil/gas/bitumen production
- `alberta_get_energy_incidents` — spills, leaks, non-compliance orders (auth-dependent — research must verify public availability)

**Wildfire (~3 tools — BC/Quebec parity + fire weather)**
- `alberta_get_active_fires` — current incidents
- `alberta_get_fire_perimeters` — perimeters (current and/or year-bounded historical, per BC pattern)
- `alberta_get_fire_weather` — Canadian Forest Fire Weather Index components (FFMC/DMC/DC) by station/date — **note tension:** this exceeds BC/Quebec parity by one tool; justified because fire weather is a distinct query class. Cross-check with MSC weather module (Phase 4) during research to avoid duplication.
- (Fire bans / restrictions: candidate tool deferred until research confirms machine-readable availability.)

**Health / AHS (~2-3 tools)**
- `alberta_get_hospitals` — hospital locations + zone (AHS structure)
- `alberta_get_er_wait_times` — if published as an open dataset (matches Quebec MSSS pattern)
- Optional: continuing-care or surveillance dataset if research finds an agent-friendly endpoint

**Transport / 511 Alberta (~2-3 tools)**
- `alberta_get_road_conditions` — current road conditions (winter-critical, mountain passes, prairies)
- `alberta_get_highway_closures` — active closures and construction
- Optional: ferry status if Alberta exposes it

**Environment (~2 tools)**
- `alberta_get_air_quality_stations` — AQHI station readings
- `alberta_get_water_quality_monitoring` — provincial monitoring network

**Agriculture (~1-2 tools)**
- `alberta_get_crop_reports` — weekly/seasonal crop reports (Alberta Agriculture and Irrigation)
- Optional: farm cash receipts or livestock counts if exposed cleanly

**Demographics (~1 tool)**
- `alberta_get_population_by_region` — population by census division / municipal district. Cross-check StatCan overlap during research.

**Parks / recreation (~1 tool)**
- `alberta_get_provincial_parks` — Alberta Parks network (parks, campgrounds, day-use)

**Total estimate:** 5 discovery + ~17-20 curated = **~22-25 `alberta_` tools** — the largest provincial module so far. Final count to be tightened during planning if a dataset proves unviable.

### AER source-of-truth policy
- **Let research confirm**. AER exposes data through multiple surfaces (OneStop, ST-Open, ST1/ST3/ST98 published reports, REST endpoints).
- Honor mcp-canada's no-scraping discipline: if AER endpoint isn't a clean REST/JSON/CSV/XLSX surface, defer that tool rather than scraping HTML.
- Consider whether AER warrants its own `shared/aer.py` client (extractable for future federal/provincial energy phases) — defer that decision to planning, based on research findings.

### Wildfire source-of-truth policy
- **Let research confirm**. Inspect both `open.alberta.ca` CKAN and `wildfirestatus.alberta.ca`. Document chosen source per-tool in docstrings.

### Curation bar (shared across domains)
- Hybrid of "high-value + signature-Alberta" and "mirror BC's curation density":
  - Curate the seasonal/high-volume queries (active fires, road conditions, ER wait times)
  - Curate Alberta-distinguishing data (oil & gas wells, pipelines, production, fire weather)
  - For the rest, mirror what BC already exposes (parks, hospitals, air quality stations) for cross-province consistency
  - Anything outside these criteria → use `alberta_search_datasets` (no curation)

### Prompts and Resources (Phase 40 pattern, from day 1)
- **6 bilingual prompts** (3 guided + 3 quick lookups). Suggested set, refine during planning:
  - Guided: `alberta_explore_energy`, `alberta_explore_wildfires`, `alberta_explore_health_or_transport`
  - Quick lookups: `alberta_quick_dataset_search`, `alberta_check_road_conditions`, `alberta_active_fires_now`
- **7 resources** (zero-parameter, type-prefixed URIs):
  - `data://alberta/ministries` — provincial ministries with bilingual labels
  - `data://alberta/forest-areas` — Alberta Wildfire Forest Area codes
  - `data://alberta/ahs-zones` — Alberta Health Services zones
  - `docs://alberta/aer-data-guide` — markdown explaining AER surfaces (ST1/ST3/ST98, OneStop, ST-Open) and which tool to use
  - `docs://alberta/wildfire-data-guide` — markdown on incident/perimeter/weather distinctions and source portals
  - `template://alberta/dataset-report`
  - `template://alberta/wildfire-report`

### Bilingual support
- Carry forward the BC/Quebec convention: bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`, inline `lang == "fr"` ternary for error messages — **no `shared/i18n.py:t()` adoption** in this phase.
- Alberta data is overwhelmingly English-only at source; FR responses surface English content with French structural messages where applicable. Document this clearly in tool docstrings.

### Technical conventions (carry forward — no decisions needed)
- 7-file module pattern (`__init__`, `constants`, `schemas`, `client`, `tools`, `prompts`, `resources`) + `__tests__/`
- Standalone `@tool` / `@prompt` / `@resource` from `fastmcp.*` (NEVER `@mcp.*`) — FileSystemProvider auto-discovery
- Post-15-05 `_api_get` parsed-dict convention + `TestSharedApiGetContract` test class
- All client functions return `(data, was_cached)` tuples with `cached_fetch()` + `get_limiter()`
- Aggressive response flattening — flat Pydantic models, not API-mirroring nesting
- Auto-paginate with 5000-record cap, return `truncated: true` flag (Phase 14/15 pattern)
- Properties-only by default, opt-in `include_geometry=true` for geospatial
- Conservative rate limit: 10 req/s for new CKAN portal (Ontario/BC/Quebec default)
- BM25 docstrings: single-line `Use for:` + 8+ `Keywords:` per tool

### Claude's Discretion
- Final dataset selection per domain — research will surface the most agent-friendly options within each curated category
- Whether AER warrants a `shared/aer.py` extraction or stays in-module — decide during planning based on reusability evidence
- CKAN `fq` strategies for organization filtering (slug discovery requires live inspection)
- Cache TTLs per tool (current wildfires need short TTL; well registry tolerates long TTL)
- Whether Alberta's CKAN requires a `User-Agent` header (Quebec quirk — verify during research)
- Schema field naming for AER tools (mirror AER's UWI/license terminology vs. Anglicize)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/quebec/` — closest reference: CKAN-only provincial module with the post-15-05 `_api_get` parsed-dict convention. Copy this structure.
- `src/mcp_canada/modules/british_columbia/` — reference for two-step CKAN→WFS routing (if Alberta's secondary portal turns out to be WFS).
- `src/mcp_canada/modules/york_region/` — reference for ArcGIS Hub integration (if Alberta's secondary portal turns out to be ArcGIS Hub).
- `src/mcp_canada/modules/ontario/` — alternate CKAN reference (different httpx client style).
- `shared/http.py` — `api_get(url, params, headers)` returns parsed JSON dict (NOT an httpx.Response). Documented contract from Phase 15-05.
- `shared/parsers.py` — `fetch_and_parse()` handles CSV, XLSX, JSON, GeoJSON, Shapefile.
- `shared/arcgis_hub.py` — ready to reuse if GeoDiscover Alberta is the chosen secondary portal.
- `shared/ogc.py` — ready to reuse if AltaLIS or another Alberta WFS is the chosen secondary portal.
- `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py` — standard utilities.

### Established Patterns
- Module structure: 7-file pattern + `__tests__/`
- Tool prefix per module (full name: `alberta_`)
- Bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`
- BM25 docstrings (single-line `Use for:` + 8+ `Keywords:`)
- Client functions return `(data, was_cached)` tuples; caching + rate limiting mandatory
- Aggressive response flattening; flat Pydantic models
- Standalone `@tool` from `fastmcp.tools` (NEVER `@mcp.tool`)
- Standalone `@prompt` from `fastmcp.prompts` (bilingual, module-prefixed)
- Zero-parameter `@resource` from `fastmcp.resources` (embedded bilingual content via `json.dumps`)
- `_api_get` helper treats `shared.http.api_get` return as parsed CKAN envelope dict — NO `.raise_for_status()` / `.json()` calls
- `TestSharedApiGetContract` test class — patches `mcp_canada.shared.http.api_get` at the shared layer to prevent mock-masks-real-contract bugs

### Integration Points
- NEW: `src/mcp_canada/modules/alberta/` — full 7-file module + `__tests__/`
- Possibly NEW: `src/mcp_canada/shared/aer.py` — extracted AER client (decide during planning based on reuse potential)
- `tests/integration/test_tool_scenarios.py` — append `TestAlbertaToolScenarios` class
- `tests/integration/test_prompts_resources_scenarios.py` — append `TestAlbertaPromptsResources` class
- `README.md` — add Alberta section, update tool count (currently ~193 → ~215-220 with ~22-25 new tools)
- `docs/MODULES.md` (per-module docs) — add Alberta entry
- `CLAUDE.md` — add Alberta to provincial CKAN list; if a new portal tech is adopted, update the Portal Technologies table

</code_context>

<specifics>
## Specific Ideas

- **Primary CKAN:** open.alberta.ca — confirm exact `/api/3/action/` path during research
- **Candidate secondary portals to inspect:**
  - GeoDiscover Alberta — ArcGIS Hub style (would reuse `shared/arcgis_hub.py`)
  - AltaLIS — provincial geospatial data society (may expose WFS)
  - Alberta Geospatial Services Centre — possible WFS/WMS endpoints
- **AER candidate endpoints to inspect:**
  - OneStop — public-facing portal
  - ST-Open — published statistical reports
  - ST1 / ST3 / ST39 / ST98 — well/production/disposition reports (CSV/XLSX downloads)
  - aer.ca REST endpoints (if any)
- **Wildfire candidate endpoints:**
  - wildfirestatus.alberta.ca — dedicated dashboard
  - open.alberta.ca CKAN federated copies (if any)
- **511 Alberta:** 511.alberta.ca — confirm raw data availability (vs. scraping the public site)
- **Alberta uses zones for AHS** (5 zones: South, Calgary, Central, Edmonton, North) — capture in `data://alberta/ahs-zones` resource
- **Alberta uses Forest Areas for wildfire** (Calgary, Rocky Mountain House, Edson, Whitecourt, Slave Lake, Lac La Biche, Fort McMurray, Peace River, Grande Prairie, High Level) — capture in `data://alberta/forest-areas`
- **License:** Most Alberta open data uses the Open Government Licence – Alberta 2.0 (compatible with agent use). Verify during research.
- **Federation question:** Quebec was 139-orgs federated; BC bcgov was provincial-only. Alberta TBD.

</specifics>

<deferred>
## Deferred Ideas

- **Calgary, Edmonton, Lethbridge, Red Deer, Medicine Hat municipal portals** — separate future phases (Calgary is Phase 29, Edmonton is Phase 30; smaller cities to be added to roadmap as needed).
- **AER as its own dedicated phase** — considered, rejected for Phase 17 (user chose full in-scope coverage). If AER turns out to be vast enough during research that wells/pipelines/production/incidents can't fit alongside the rest of Alberta in a single phase, the wildfire/health/transport/environment scope can be split into Phase 17a, with AER becoming Phase 17b.
- **Fire bans / restrictions tool** — pending research confirmation that Alberta publishes machine-readable fire-ban data (vs. only HTML on a public-info page).
- **Federal Environment Canada wildfire feeds** — out of scope for a provincial Alberta phase. Future federal-wildfire phase if demand exists.
- **AER incidents/compliance auth-protected endpoints** — if AER's incident registry requires authentication or rate-limited credentials, that tool is deferred (no-scraping discipline applies).
- **Cross-module SQL examples for Alberta** — adding Alberta-specific cross-module SQL examples to `EXAMPLES.md` is good Phase 17 work, but a dedicated cross-module-SQL deepening initiative is its own future phase.
- **MSC weather (FWI) duplication review** — if research finds MSC weather already exposes Canadian FFWI components, the `alberta_get_fire_weather` tool may be replaced by a province-filter on the MSC tool. Decide during planning.
- **Bilingual `shared/i18n.py:t()` adoption** — systemic concern flagged in Phase 15/16; remains its own future phase.
- **Auth-required AER endpoints** — defer; honor no-scraping discipline.

</deferred>

---

*Phase: 17-alberta-government-open-data*
*Context gathered: 2026-04-17*
