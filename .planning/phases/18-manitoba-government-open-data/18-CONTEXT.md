# Phase 18: Manitoba Government Open Data - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Manitoba's provincial open data surface to mcp-canada as a new `manitoba` module. Primary catalogue: **geoportal.gov.mb.ca** ("Data MB"), an **ArcGIS Hub** powered by ArcGIS Online org `mMUesHYPkXjaFGfS`. (Research correction 2026-06-13: `data.manitoba.ca` CKAN is unreachable and Manitoba Land Initiative is retired; Manitoba's machine-readable portal is ArcGIS Hub, so this module follows the **Alberta Phase 17 / York Region Phase 14 ArcGIS Hub pattern** via `shared/arcgis_hub.py`, NOT the CKAN pattern.) Delivers 5 standard ArcGIS-Hub discovery tools plus a **balanced spread** of curated FeatureServer tools across Manitoba's high-value data domains, following the same shape established by BC (Phase 15), Quebec (Phase 16), and Alberta (Phase 17).

Manitoba municipalities (Winnipeg = Phase 32; Brandon and others to be added to the roadmap as needed) are explicitly deferred to their own future phases. Federal sources remain out of scope for this provincial phase.

</domain>

<decisions>
## Implementation Decisions

### Signature data domains — balanced, no single anchor
- **No single signature anchor** (unlike Alberta, which went deep on AER energy). Mirror BC's even curation density across Manitoba's relevant domains rather than going deep on one.
- **In-scope domains (even spread)** — domain #2 corrected after research (Hydro dropped, drought/weather substituted):
  1. **Flood / hydrology** — overland flood alerts (Watch/Warning polygons), river conditions & hydrometric stations, provincial waterways (dikes/floodways/dams/reservoirs). Manitoba's defining hazard. CONFIRMED machine-readable via ArcGIS Hub (`Overland_Flood_Alerts`, `Provincial_Waterways` FeatureServers); flood bulletins themselves are PDF/HTML and out of scope.
  2. **Agriculture & climate** (replaces Manitoba Hydro/energy — **DROPPED**: hydro.mb.ca water levels are HTML-only, no API) — agricultural weather stations (100+), cattle/hog market prices, crop reporting regions, drought monitor (D0–D4). All CONFIRMED live on ArcGIS Hub.
  3. **Transport / 511 Manitoba** — road conditions, winter roads, closures/construction. **Conditional**: Manitoba 511 API v3 requires a free developer key (unlike Alberta's keyless feed). Plan transport tools to ship only if the key is freely obtainable in Wave 0; otherwise defer.
  4. **Regional health** — diagnostic & surgical wait times (CONFIRMED live), rural health facilities (service URL to resolve in Wave 0). Parity with Alberta AHS / Quebec MSSS.
  5. **Environment / parks** — provincial parks (93, bilingual), waterbody/fisheries reference data (350+ water bodies), provincial forests. CONFIRMED live on ArcGIS Hub.
- Curation bar per domain: curate the seasonal/high-volume queries (flood alerts, road conditions) and the Manitoba-distinguishing data (flood, drought, prairie ag/markets), and leave everything else to the discovery tools (search/detail/query).

### Module breadth / size
- **Target: mid-band ~14-18 tools.** 5 standard CKAN discovery tools + ~9-13 curated across the 6 balanced domains.
- Matches BC's density (~15); deliberately **not** Alberta's 24 — Manitoba's portal is smaller and less data-rich, so padding thin domains is the failure mode to avoid.
- Final count locked during planning based on how many agent-friendly datasets research actually surfaces per domain.

### Platform architecture / geospatial access (CORRECTED after research)
- Primary portal: **geoportal.gov.mb.ca** ArcGIS Hub (ArcGIS Online org `mMUesHYPkXjaFGfS`; base services URL `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/`). Module prefix `manitoba_` (full-name pattern). Module name: `manitoba`.
- **Geospatial: RESOLVED — ArcGIS Hub pattern** (Alberta Phase 17 / York Region Phase 14). Reuse `shared/arcgis_hub.py` unchanged for all FeatureServer queries. No CKAN, no WFS, no MLI (retired). `shared/parsers.fetch_and_parse()` remains the fallback for any CSV/JSON/GeoJSON file resources surfaced by Hub items.
- Discovery tools become **ArcGIS Hub search/detail/query** (Hub Search API `/api/search/v1/...`) rather than CKAN `/api/3/action/`. The query tool auto-routes: ESRI FeatureServer → `arcgis_hub.query_feature_service`; CSV/JSON/GeoJSON/XLSX → `fetch_and_parse`; else metadata-only.
- Honor the no-scraping discipline: HTML-only or PDF-only sources (Manitoba Hydro water levels, Hydrologic Forecast Centre bulletins) are deferred, not scraped.

### Default scope policy
- Discovery tools search the ArcGIS Hub catalogue by keyword/category/tag with pagination; org/group listing via Hub groups endpoint. Document the geoportal's ArcGIS-Hub nature in the `manitoba_search_datasets` docstring. (CKAN federation question is moot — not a CKAN portal.)

### Discovery tools (5 standard, ArcGIS Hub flavor — mirrors York Region/Alberta)
- `manitoba_search_datasets`, `manitoba_get_dataset_details`, `manitoba_query_dataset`, `manitoba_list_organizations`, `manitoba_list_categories`
- `manitoba_query_dataset` implements the ArcGIS-Hub/file auto-router described above.

### Prompts and Resources (Phase 40 pattern, from day 1)
- **6 bilingual prompts** (3 guided + 3 quick lookups). Suggested set, refine during planning:
  - Guided: `manitoba_explore_flood_or_water`, `manitoba_explore_transport`, `manitoba_explore_agriculture_or_health`
  - Quick lookups: `manitoba_quick_dataset_search`, `manitoba_check_road_conditions`, `manitoba_flood_outlook_now`
- **~7 resources** (zero-parameter, type-prefixed URIs). Suggested set, refine during planning:
  - `data://manitoba/departments` — provincial departments/ministries with bilingual labels
  - `data://manitoba/health-regions` — Regional Health Authorities (WRHA et al.) — analogous to Alberta's AHS zones
  - `data://manitoba/major-rivers` — Red, Assiniboine, Winnipeg river systems + key flood-monitoring points
  - `docs://manitoba/flood-data-guide` — markdown on flood-outlook vs. river-level vs. forecast distinctions and source portals
  - `docs://manitoba/portal-guide` — markdown on data.manitoba.ca structure, MLI geospatial access (if adopted), and which tool to use
  - `template://manitoba/dataset-report`
  - `template://manitoba/flood-report`

### Bilingual support
- Carry forward the BC/Quebec/Alberta convention: bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`, inline `lang == "fr"` ternary for error messages — **no `shared/i18n.py:t()` adoption** in this phase.
- Manitoba is officially bilingual under the Manitoba Act (French-language services); however source data is overwhelmingly English. FR responses surface English content with French structural messages where applicable. Document this in tool docstrings.

### Technical conventions (carry forward — no decisions needed)
- 7-file module pattern (`__init__`, `constants`, `schemas`, `client`, `tools`, `prompts`, `resources`) + `__tests__/`
- Standalone `@tool` / `@prompt` / `@resource` from `fastmcp.*` (NEVER `@mcp.*`) — FileSystemProvider auto-discovery
- Post-15-05 `_api_get` parsed-dict convention + `TestSharedApiGetContract` test class
- All client functions return `(data, was_cached)` tuples with `cached_fetch()` + `get_limiter()`
- Aggressive response flattening — flat Pydantic models, not API-mirroring nesting
- Auto-paginate with 5000-record cap, return `truncated: true` flag (Phase 14/15 pattern)
- Properties-only by default, opt-in `include_geometry=true` for geospatial
- Conservative rate limit: 10 req/s for new CKAN portal (Ontario/BC/Quebec/Alberta default)
- BM25 docstrings: single-line `Use for:` + 8+ `Keywords:` per tool

### Claude's Discretion
- Final dataset selection per domain — research surfaces the most agent-friendly options within each curated category
- Whether the geospatial router warrants the two-step pattern or CKAN-only — decide during planning based on MLI inspection
- CKAN `fq` strategies for organization filtering (slug discovery requires live inspection)
- Cache TTLs per tool (flood forecasts / road conditions need short TTL; agriculture/health registries tolerate long TTL)
- Whether Manitoba's CKAN requires a `User-Agent` header (Quebec quirk — verify during research)
- Final prompt/resource set naming and count

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/alberta/` — newest and closest reference: balanced CKAN module with optional geospatial routing and the post-15-05 `_api_get` parsed-dict convention. Copy this structure.
- `src/mcp_canada/modules/quebec/` — closest reference if Manitoba turns out CKAN-only (no live geospatial portal).
- `src/mcp_canada/modules/british_columbia/` — reference for two-step CKAN→WFS routing (if MLI exposes WFS).
- `src/mcp_canada/modules/york_region/` — reference for ArcGIS Hub integration (if MLI is ArcGIS Hub).
- `src/mcp_canada/modules/ontario/` — alternate CKAN reference.
- `shared/http.py` — `api_get(url, params, headers)` returns parsed JSON dict (NOT an httpx.Response). Phase 15-05 contract.
- `shared/parsers.py` — `fetch_and_parse()` handles CSV, XLSX, JSON, GeoJSON, Shapefile.
- `shared/ogc.py` — ready to reuse if MLI exposes a WFS endpoint.
- `shared/arcgis_hub.py` — ready to reuse if Manitoba uses an ArcGIS Hub portal.
- `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py`, `shared/geo.py`, `shared/reshape.py` — standard utilities.

### Established Patterns
- Module structure: 7-file pattern + `__tests__/`
- Tool prefix per module (full name: `manitoba_`)
- Bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`
- BM25 docstrings (single-line `Use for:` + 8+ `Keywords:`)
- Client functions return `(data, was_cached)` tuples; caching + rate limiting mandatory
- Aggressive response flattening; flat Pydantic models
- Standalone `@tool` / `@prompt` / `@resource` from `fastmcp.*` (NEVER `@mcp.*`)
- Zero-parameter `@resource` (embedded bilingual content via `json.dumps`)
- `_api_get` helper treats `shared.http.api_get` return as parsed CKAN envelope dict — NO `.raise_for_status()` / `.json()` calls
- `TestSharedApiGetContract` test class — patches `mcp_canada.shared.http.api_get` at the shared layer to prevent mock-masks-real-contract bugs

### Integration Points
- NEW: `src/mcp_canada/modules/manitoba/` — full 7-file module + `__tests__/`
- `tests/integration/test_tool_scenarios.py` — append `TestManitobaToolScenarios` class
- `tests/integration/test_prompts_resources_scenarios.py` — append `TestManitobaPromptsResources` class
- `README.md` — add Manitoba section, update tool count (currently reflects Alberta total → add ~14-18 new tools)
- `docs/MODULES.md` (per-module docs) — add Manitoba entry
- `CLAUDE.md` — add Manitoba to provincial CKAN list; if MLI adds a new portal-tech path, update the Portal Technologies table

</code_context>

<specifics>
## Specific Ideas

- **Primary CKAN:** data.manitoba.ca — confirm exact `/api/3/action/` path during research
- **Candidate geospatial portal to inspect:** Manitoba Land Initiative (mli.gov.mb.ca); check for WFS/ArcGIS endpoints
- **Flood forecasting sources to inspect:** Manitoba Infrastructure / Hydrologic Forecasting flood bulletins and outlooks; Red River Floodway data; verify machine-readable vs. HTML-only
- **511 Manitoba:** manitoba511.ca — confirm raw data feed availability (vs. scraping the public site); compare to Alberta's 511 v2 JSON approach
- **Health structure:** Manitoba uses Regional Health Authorities (Winnipeg RHA, Prairie Mountain Health, Interlake-Eastern, Northern, Southern Health-Santé Sud) — capture in `data://manitoba/health-regions`
- **River systems:** Red, Assiniboine, Winnipeg, Souris — capture key flood-monitoring points in `data://manitoba/major-rivers`
- **Manitoba Hydro:** research-risk — public machine-readable generation/flow data may be thin; curate only what exists cleanly
- **License:** confirm Manitoba's open data licence (likely an Open Government Licence variant) during research
- **Bilingual:** Manitoba is officially bilingual (Manitoba Act); source data overwhelmingly English

</specifics>

<deferred>
## Deferred Ideas

- **Winnipeg, Brandon, and other Manitoba municipal portals** — separate future phases (Winnipeg is Phase 32; smaller cities added to roadmap as needed).
- **Manitoba Hydro as a deep dedicated domain** — if research finds Hydro data rich enough to warrant depth, revisit; for now it's one of six balanced domains, curated only where clean data exists.
- **Flood tooling beyond outlooks/levels** — predictive flood modeling, floodway operations data, or historical flood archives are candidates for a future deepening if demand appears.
- **Live WFS/ArcGIS adoption if MLI is file-only now** — if MLI exposes only file downloads today, defer the two-step router to a future phase when a live endpoint appears.
- **Bilingual `shared/i18n.py:t()` adoption** — systemic concern flagged in Phases 15/16/17; remains its own future phase.
- **Cross-module SQL examples for Manitoba** — adding Manitoba-specific cross-module SQL examples to `EXAMPLES.md` is good Phase 18 work, but a dedicated cross-module-SQL deepening initiative is its own future phase.
- **Any source requiring scraping or auth** — defer per no-scraping discipline (e.g., 511 if only HTML, Hydro behind auth).

</deferred>

---

*Phase: 18-manitoba-government-open-data*
*Context gathered: 2026-06-13*
