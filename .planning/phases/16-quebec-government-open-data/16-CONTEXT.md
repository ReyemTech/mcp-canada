# Phase 16: Quebec Government Open Data - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Quebec's provincial open data catalogue to mcp-canada via **Données Québec** (`www.donneesquebec.ca/recherche/api/3/action/`) — a federated CKAN instance with ~1,593 datasets across 139 organizations. Phase 16 is **CKAN-only**: no secondary geospatial (WFS/ArcGIS) portal. Geospatial data is still queryable through resource-level CSV/GeoJSON/Shapefile parsing via the existing `shared/parsers.fetch_and_parse()`. Quebec municipalities (Montreal at Phase 27, Quebec City, Laval, Gatineau, Longueuil, Sherbrooke, Saguenay) are explicitly deferred to their own future phases — Phase 16 stays provincial-only.

</domain>

<decisions>
## Implementation Decisions

### Platform architecture
- Use Données Québec CKAN API at `https://www.donneesquebec.ca/recherche/api/3/action/` — standard CKAN + `User-Agent` header required (BC-CKAN-style) to receive real JSON instead of schema-description responses
- **NO secondary geospatial portal** in this phase. Géoportail Québec, MTQ ArcGIS Feature Services, and MELCCFP WFS endpoints are deferred to future sub-phases if demand proves out
- Geospatial datasets hosted on Données Québec are parsed from their file resources (CSV, GeoJSON, Shapefile) via `shared/parsers.fetch_and_parse()` — no new protocol support needed
- Module prefix: `quebec_` (consistent with full-name pattern: ontario_, toronto_, bc_)

### Language defaults
- Default `lang: Literal["en", "fr"] = "en"` — matches every other provincial module, consistent project-wide. Agents explicitly pass `lang="fr"` when they want French output
- Dataset metadata fallback: Données Québec titles/notes are primarily French; the client should surface both `title_fr`/`title_en` when the CKAN response exposes them (bcgov-style `title_translated` field) and return the user-requested language if available with fallback to the other
- All bilingual error messages use the inline `lang == "fr"` ternary pattern (matching BC Phase 15 post-gap-closure convention) — do NOT introduce `shared/i18n.py:t()` imports

### Catalog filter policy
- `quebec_search_datasets` returns results from **all 139 orgs by default** — no hardcoded allowlist
- Agents can narrow with an explicit `organization` param (CKAN `fq=organization:{slug}`)
- This means results WILL include Hydro-Québec, BIXI, Montreal ARTM, and civic NGOs alongside provincial ministries. Document this clearly in the `quebec_search_datasets` docstring so agents understand the federated nature of the catalog
- `quebec_list_organizations` returns all 139 orgs with their counts — no filtering

### Discovery tools (5 standard CKAN)
- `quebec_search_datasets`, `quebec_get_dataset_details`, `quebec_query_dataset` (file-parser wrapper, no WFS routing needed), `quebec_list_organizations`, `quebec_list_categories`
- `quebec_query_dataset` is a simplified version of `bc_query_features` — no two-step WFS routing since there's no WFS portal. Just picks the best file resource (CSV > GeoJSON > XLSX > JSON) and delegates to `fetch_and_parse()`

### Curated datasets (~13 curated tools target)

**Health / MSSS (~3 tools):**
- `quebec_get_hospitals` — hospital locations, type, region
- `quebec_get_clsc_locations` — CLSC (Centre local de services communautaires) network
- `quebec_get_hospital_wait_times` — ER wait times if published as an open dataset

**Transport / MTQ (~3 tools):**
- `quebec_get_road_conditions` — current road conditions (winter-critical)
- `quebec_get_highway_closures` — active highway closures/construction zones
- `quebec_get_bridge_inventory` — provincial bridge registry and condition data

**Wildfires / SOPFEU (~2 tools):**
- `quebec_get_active_fires` — current wildfire incidents (matches BC pattern)
- `quebec_get_fire_perimeters` — historical fire perimeters by year (required year param to bound response)

**Demographics + Environment + Energy (4 tools):**
- `quebec_get_population_by_region` — ISQ (Institut de la statistique du Québec) population by MRC/région administrative
- `quebec_get_air_quality_stations` + `quebec_get_water_quality_monitoring` — MELCCFP monitoring network (2 tools, not 1)
- `quebec_get_hydro_outages` — Hydro-Québec current outage registry (high seasonal demand during ice storms)
- `quebec_get_provincial_parks` — SEPAQ park network + MELCCFP protected-area registry

**Total estimate:** 5 discovery + 12-13 curated = **~17-18 `quebec_` tools**

### Prompts and Resources (Phase 40 pattern)
- Include prompts.py and resources.py from the start (7-file pattern)
- **6 bilingual prompts:** 3 guided workflows (`quebec_explore_health`, `quebec_explore_transport_conditions`, `quebec_explore_environment`) + 3 quick lookups (`quebec_quick_dataset_search`, `quebec_check_road_conditions`, `quebec_active_fires_now`)
- **7 resources:** `data://quebec/ministries` (catalog of provincial ministries with bilingual labels), `data://quebec/regions` (17 administrative regions), `data://quebec/mrcs` (regional county municipalities), `docs://quebec/catalog-federation-quirks` (explains the 139-org federated nature + Montreal overlap), `docs://quebec/bilingual-metadata-guide`, `template://quebec/dataset-report`, `template://quebec/road-conditions-report`

### Claude's Discretion
- Exact CKAN `fq` strategies for filtering federated catalog (Montreal org slugs, NGO exclusion patterns if needed at docstring level)
- Which specific MSSS datasets to curate (MSSS has many overlapping health datasets — pick the most agent-friendly)
- Whether SOPFEU wildfire data is on Données Québec or on a SOPFEU-specific portal (research should confirm — if SOPFEU is a separate portal, note it and adjust scope)
- Whether Hydro-Québec outages are on Données Québec CKAN or require the Hydro-Québec website API (research should confirm — if not on DQ, move to deferred)
- How to handle bilingual CKAN fields (`title_translated`, `notes_translated` vs plain `title_fr`/`title_en`) — inspect real responses during research
- Rate limit settings for Données Québec (conservative default 10 req/s matching Ontario/BC CKAN)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/british_columbia/` — closest CKAN pattern (post-gap-closure `_api_get` that correctly treats shared `api_get` return as parsed dict). Copy this, NOT the pre-15-05 version
- `src/mcp_canada/modules/ontario/` — alternate CKAN reference with different architectural choices (inline httpx client)
- `src/mcp_canada/modules/toronto/` — CKAN + datastore_search_sql reference for large datasets
- `shared/http.py` — `api_get(url, params, headers)` returns parsed JSON dict (NOT an httpx.Response) — contract is documented in 15-05 debug session
- `shared/parsers.py` — `fetch_and_parse()` handles CSV, XLSX, JSON, GeoJSON, Shapefile (post-Phase 13+)
- `shared/cache.py` — `cached_fetch(key, ttl, fetcher)` for all client functions
- `shared/rate_limiter.py` — `get_limiter(source, rate)` per-source TokenBucket
- `shared/envelope.py` — `make_response()` / `make_error()` for _meta envelope

### Established Patterns
- Module structure: 7-file pattern (__init__, constants, schemas, client, tools, prompts, resources) + __tests__/
- Tool prefix per module (full name: `quebec_`)
- Bilingual `lang: Literal["en", "fr"] = "en"` on every @tool
- BM25 docstrings with single-line `Use for:` + 8+ `Keywords:`
- All client functions return `(data, was_cached)` tuples with caching + rate limiting
- Aggressive response flattening — Pydantic models are flat, not mirror API nesting
- Standalone `@tool` from `fastmcp.tools` (NEVER `@mcp.tool`)
- Standalone `@prompt` from `fastmcp.prompts` (bilingual, module-prefixed)
- Zero-parameter `@resource` from `fastmcp.resources` (embedded bilingual content via `json.dumps`)
- `_api_get` helper MUST treat shared `api_get`'s return value as an already-parsed CKAN envelope dict — NO `.raise_for_status()` / `.json()` calls (lesson from Phase 15 gap closure)
- `TestSharedApiGetContract` test class pattern — patches `mcp_canada.shared.http.api_get` at the shared layer (not module-local) to prevent mock-masks-real-contract bugs

### Integration Points
- NEW: `src/mcp_canada/modules/quebec/` — full 7-file module
- `tests/integration/test_tool_scenarios.py` — append `TestQuebecToolScenarios` class
- `tests/integration/test_prompts_resources_scenarios.py` — append `TestQuebecPromptsResources` class
- `README.md` — add Quebec section, update tool count (currently 175 → ~193 with ~18 new tools)
- `CLAUDE.md` — add Quebec to CKAN portal list (no new portal technology row; CKAN is already documented)

</code_context>

<specifics>
## Specific Ideas

- Données Québec CKAN: `https://www.donneesquebec.ca/recherche/api/3/action/`
- Requires `User-Agent` header to receive real JSON (bare `curl` returns schema-description format — confirmed via live probe 2026-04-11)
- Dataset count: 1,593 packages (live count 2026-04-11)
- Organization count: 139 orgs (live count 2026-04-11) — federated with municipalities + NGOs
- License: Most data under "Licence Creative Commons 4.0 BY" or "Licence du gouvernement ouvert — Québec" (compatible with agent use)
- SOPFEU website: `www.sopfeu.qc.ca` — research should confirm if wildfire data is on Données Québec or a separate SOPFEU endpoint
- Hydro-Québec outages: historically published via their own website (`www.hydroquebec.com/pannes/`) — research should confirm CKAN availability or move to deferred
- MTQ road conditions: Québec 511 (`www.quebec511.info`) is the public site; research should confirm if raw data is on Données Québec or requires scraping
- MSSS hospital data: typically published under `gouv-du-quebec` or `ministere-de-la-sante-et-des-services-sociaux` org slug

</specifics>

<deferred>
## Deferred Ideas

- **Géoportail Québec / ArcGIS Feature Services** — Secondary geospatial portal for live WFS/Feature queries. Defer to a future phase once Phase 16 CKAN surface is proven useful. Would reuse `shared/ogc.py` (Phase 15) or `shared/arcgis_hub.py` (Phase 14) depending on which protocol Géoportail exposes.
- **Quebec City municipal open data** (`donnees.ville.quebec.qc.ca`) — separate CKAN/municipal portal. Its own future phase.
- **Laval, Gatineau, Longueuil, Sherbrooke, Saguenay municipal portals** — each has its own portal or sub-page. Defer to their own phases.
- **SOPFEU-specific portal** (if wildfire data proves not to be on Données Québec) — could become a dedicated sub-phase.
- **Hydro-Québec outages API** (if outages data proves not to be on Données Québec) — would require scraping or a private API agreement; defer.
- **MTQ Quebec 511 scraping** (if road conditions data proves not to be on Données Québec) — defer; scraping is out of project scope (no dependencies policy).
- **MSS (Montreal ARTM) transit** — Montreal-specific transit data shows up in the Données Québec federated catalog but belongs in Phase 27. Document the overlap in `quebec_search_datasets` docstring so agents know to use the eventual Montreal module for ARTM.
- **Bilingual `shared/i18n.py:t()` adoption** — Phase 15 audit noted 29 hardcoded-English `make_error` sites across modules. This is a systemic concern for a dedicated future phase, not Phase 16 scope.

</deferred>

---

*Phase: 16-quebec-government-open-data*
*Context gathered: 2026-04-11*
