# Phase 19: Saskatchewan Government Open Data - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Saskatchewan's provincial open data surface to mcp-canada as a new `saskatchewan` module. **Portal technology is UNCONFIRMED** — pre-planning reconnaissance could not resolve a unified Saskatchewan portal (sandbox connection-refused on `data.saskatchewan.ca`, `opendata.saskatchewan.ca`, `highways.gov.sk.ca`; `gis.saskatchewan.ca` returned 403). Saskatchewan has historically lagged peers on open data. **Research MUST determine the portal**, and the **planner decides ship-minimal-vs-defer based on the evidence** (see "Portal strategy" below).

Known anchor: the federal `open.canada.ca` CKAN catalogue contains **413 Saskatchewan datasets** — a viable fallback discovery surface. Regional pattern (Alberta + Manitoba both ArcGIS Hub) hints Saskatchewan *may* be ArcGIS Hub, unconfirmed.

Saskatchewan municipalities (Saskatoon, Regina — future phases) and federal sources are out of scope for this provincial phase.

</domain>

<decisions>
## Implementation Decisions

### Portal strategy — minimal/defer posture, planner decides post-research
- **Research determines the portal technology.** Probe (live, with WebFetch — the sandbox scout could not reach these): `data.saskatchewan.ca`, `opendata.saskatchewan.ca`, `gis.saskatchewan.ca`, SaskGeomatics / GeoSask, `hub.arcgis.com/organizations/saskgov` and any `services.arcgis.com/{orgId}` for Saskatchewan, plus the federal `open.canada.ca` Saskatchewan-filtered catalogue.
- **The ship-minimal-vs-defer decision is the PLANNER's, made post-research on evidence.** Capture both paths; do not pre-commit:
  - **Ship path** — if research finds a usable surface (a provincial CKAN/ArcGIS Hub/WFS portal, OR the federal `open.canada.ca` Saskatchewan-filtered catalogue as a discovery backbone), build a lean module.
  - **Defer path** — if even the federal-filtered surface proves unworkable and curated domains are HTML-only, defer the phase (document why; revisit when a real portal materializes).
- **No-scraping discipline holds** — HTML-only or PDF-only sources are deferred, never scraped.
- Module prefix `saskatchewan_`; module name `saskatchewan`.

### Portal-technology routing (research picks; reuse existing clients)
- **CKAN** (provincial or federal-proxy) → `shared/http.py` `api_get` parsed-dict pattern (Quebec/Ontario/federal-CKAN reference). If federal-proxy: reuse the existing `ckan` (federal) module's approach, filtered to Saskatchewan orgs.
- **ArcGIS Hub** → `shared/arcgis_hub.py` (Manitoba/Alberta/York pattern). **⚠ DEPENDENCY:** if Saskatchewan is ArcGIS Hub, the latent `shared/arcgis_hub.py:search_hub_datasets` `startindex` param bug (discovered in Manitoba Phase 18, affects York/Alberta discovery live) must be fixed first or the Saskatchewan discovery tools will inherit the same HTTP 400. Flag for planning.
- **OGC WFS** → `shared/ogc.py` (BC pattern).
- File resources (CSV/XLSX/GeoJSON/Shapefile) → `shared/parsers.fetch_and_parse()`.

### Signature data domains — all four in scope, curate only what's machine-readable
- **Agriculture (signature)** — Saskatchewan is Canada's #1 ag exporter: canola/wheat/pulses, weekly crop reports, Saskatchewan Crop Insurance (SCIC). Highest-priority domain; most likely to have machine-readable data.
- **Energy / mining** — potash (world's largest reserves), oil & gas, uranium. Economic backbone; curate if exposed cleanly.
- **Highways / 511** — Highway Hotline / Sask 511 road conditions (winter-critical). **Conditional** — see 511 handling below.
- **Health + environment/water** — Saskatchewan Health Authority facilities/wait times; Water Security Agency monitoring; wildfire (Saskatchewan Public Safety Agency). Parity with other provinces where data exists.
- **Curation bar:** curate ONLY what research confirms is machine-readable. Do NOT pad thin domains — sparse data is the expected failure mode here. Anything uncurated falls back to the discovery tools.

### Module size
- **Lean ~10-14 tools.** ~5 discovery + ~5-9 curated. Deliberately smaller than Manitoba/BC — Saskatchewan's open data is uncertain/sparse. Can grow in a future phase if a richer portal materializes. Final count (or defer decision) locked during planning.

### Transport / 511 handling — MORE conservative than Manitoba
- **Defer transport tools UNLESS research finds a clean, keyless JSON/API feed.** Do NOT ship `NOT_CONFIGURED` stub tools (this is a deliberate departure from the Manitoba 511 pattern). If Sask 511 / Highway Hotline is key-gated or HTML/app-only, drop the transport domain entirely for this phase.

### Prompts and Resources (Phase 40 pattern — conditional on module shipping)
- **6 bilingual prompts** (3 guided + 3 quick lookups) + **~7 zero-parameter resources**, refined during planning, scaled to the actual shipped tool surface. Suggested resource candidates: `data://saskatchewan/ministries`, `data://saskatchewan/health-regions`, `data://saskatchewan/crop-districts`, `docs://saskatchewan/portal-guide`, plus templates. Finalize after research confirms the portal.

### Bilingual support
- Carry forward the convention: bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`, inline `lang == "fr"` ternary for error messages — no `shared/i18n.py:t()` adoption. Saskatchewan data is English-primary; FR responses surface English content with French structural messages.

### Technical conventions (carry forward — no decisions needed)
- 7-file module pattern + `__tests__/`; standalone `@tool`/`@prompt`/`@resource` from `fastmcp.*` (NEVER `@mcp.*`)
- `_api_get` parsed-dict convention + `TestSharedApiGetContract` (if CKAN); `(data, was_cached)` tuples with `cached_fetch()` + `get_limiter()`
- Aggressive response flattening — flat Pydantic models
- Auto-paginate with 5000-record cap + `truncated` flag; properties-only default + opt-in `include_geometry` for geospatial
- Conservative rate limit (10 req/s); BM25 docstrings (`Use for:` + 8+ `Keywords:`)

### Claude's Discretion
- Final portal technology and ship-minimal-vs-defer decision (planner, post-research)
- Final dataset selection per domain — research surfaces the most agent-friendly options
- Whether to reuse the federal `ckan` module's client vs. a new `saskatchewan` `_api_get` for the federal-proxy path
- Cache TTLs per tool; final prompt/resource set

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/ckan/` — the FEDERAL open.canada.ca CKAN module; the closest reference IF the federal-catalogue-proxy path is chosen (filter package_search to Saskatchewan orgs).
- `src/mcp_canada/modules/manitoba/` — newest ArcGIS Hub module; reference if Saskatchewan turns out ArcGIS Hub (note the param fix from 18-09: limit/startindex, not num/start).
- `src/mcp_canada/modules/quebec/` and `ontario/` — provincial CKAN references.
- `src/mcp_canada/modules/british_columbia/` — WFS reference.
- `shared/http.py` `api_get` (parsed-dict), `shared/arcgis_hub.py`, `shared/ogc.py`, `shared/parsers.py` `fetch_and_parse()`, `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py`.

### Established Patterns
- 7-file module + `__tests__/`; `saskatchewan_` tool prefix
- Bilingual `lang` param; BM25 docstrings; `(data, was_cached)` tuples; aggressive flattening
- Standalone fastmcp decorators; zero-parameter resources; `TestSharedApiGetContract`

### Integration Points
- NEW: `src/mcp_canada/modules/saskatchewan/` (full 7-file module + `__tests__/`) — IF the module ships
- `tests/integration/test_tool_scenarios.py` — append `TestSaskatchewanToolScenarios`
- `tests/integration/test_prompts_resources_scenarios.py` — append `TestSaskatchewanPromptsResources`
- `README.md` / `docs/modules/saskatchewan.md` / `CLAUDE.md` — add Saskatchewan section + update counts (IF ships)
- **⚠ Possible prerequisite:** `shared/arcgis_hub.py` `startindex` fix (if Saskatchewan is ArcGIS Hub) — see Portal-technology routing above.

</code_context>

<specifics>
## Specific Ideas

- **Reconnaissance gap is real** — sandbox could not reach Saskatchewan domains. Research must use live WebFetch and probe aggressively before assuming anything.
- **Candidate portals to probe:** `data.saskatchewan.ca`, `opendata.saskatchewan.ca`, `gis.saskatchewan.ca`, SaskGeomatics / GeoSask / Flintbox, `hub.arcgis.com/organizations/saskgov`, any `services.arcgis.com/{orgId}` for Saskatchewan.
- **Federal fallback:** `open.canada.ca` CKAN `/api/3/action/package_search` filtered to Saskatchewan-owning organizations (413 datasets reported).
- **Candidate domain sources to verify (machine-readable vs HTML):** Saskatchewan Agriculture crop reports + SCIC; Highway Hotline / Sask 511; Water Security Agency monitoring; Saskatchewan Health Authority; potash/oil&gas/uranium ministry data; SaskPower (login-gated — likely out).
- **Licence:** confirm Saskatchewan's open data licence during research.
- **511 is conservative:** defer transport entirely unless a clean keyless feed exists — no NOT_CONFIGURED stubs.

</specifics>

<deferred>
## Deferred Ideas

- **Saskatoon, Regina, and other Saskatchewan municipal portals** — separate future phases.
- **Full defer of the phase** — a live option if research finds even the federal-filtered surface unworkable and all curated domains HTML-only. Planner makes this call.
- **`shared/arcgis_hub.py` startindex fix** — cross-cutting (affects York Phase 14, Alberta Phase 17, and Saskatchewan IF ArcGIS Hub). Its own concern, but becomes a prerequisite for this phase if Saskatchewan is ArcGIS Hub. Surfaced from Manitoba Phase 18.
- **Federal-catalogue-proxy as a reusable pattern** — if the federal-filtered approach works well for Saskatchewan, generalizing it for other data-sparse provinces/territories (Phases 22-26: Atlantic + territories) is a future consideration, not this phase.
- **Bilingual `shared/i18n.py:t()` adoption** — systemic, its own future phase.
- **SaskPower / login-gated sources** — deferred (no-scraping/no-auth discipline).

</deferred>

---

*Phase: 19-saskatchewan-government-open-data*
*Context gathered: 2026-06-15*
