# Phase 20: Nova Scotia Government Open Data - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Nova Scotia's provincial open data surface to mcp-canada as a new `nova_scotia` module. Primary portal: **data.novascotia.ca**, a **Socrata** (Tyler Technologies) open-data platform — a **NEW portal technology** for this codebase (we currently support CKAN, ArcGIS Hub, OGC WFS). Socrata exposes the keyless SODA API (`/api/catalog/v1` discovery, `/resource/{id}.json` + CSV data) over 1,270 datasets. This phase establishes the Socrata pattern (first Socrata province; future Atlantic provinces and some municipalities may reuse it).

Delivers 5 discovery tools + a mid-band spread of curated tools across Nova Scotia's high-value domains. Nova Scotia municipalities (Halifax is Phase 33) and federal sources are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Socrata foundation — build a reusable shared client
- **Build `shared/socrata.py`** (a reusable SODA client), parallel to `shared/arcgis_hub.py` and `shared/ogc.py`. Rationale: other Atlantic provinces and some Canadian municipalities also run Socrata, so the investment amortizes. Adds a **4th row to the Portal Technologies table** in CLAUDE.md.
- The shared client should cover: catalog discovery (`/api/catalog/v1` and/or `/api/views.json`), per-dataset reads (`/resource/{id}.json` with SoQL params `$where`/`$select`/`$limit`/`$offset`/`$order`), and CSV/JSON handling. Keyless reads (standard Socrata throttling applies); design so an optional `X-App-Token` can be added later without API change.
- Reuse `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py`, and `shared/parsers.fetch_and_parse()` for any file resources.
- Module prefix: planner's discretion between `ns_` (brevity, like `bc_`) and `nova_scotia_` (full-name, like `manitoba_`/`saskatchewan_`). Module name: `nova_scotia`.

### Signature data domains — all four in scope
- **Fishing / aquaculture (signature)** — marine/finfish aquaculture leases, rockweed leases, fish hatchery stocking records, fisheries. NS's distinguishing Atlantic dataset (13 datasets).
- **Environment / energy** — coastal/water monitoring, tidal/offshore energy, air quality (18 datasets, the largest category).
- **Lands / forests / wildlife** — forestry, protected areas, wildlife (16 datasets).
- **Health + demographics** — Nova Scotia Health facilities/indicators (20 datasets) + population/demographics (13). Cross-references StatCan during research.
- **Curation bar:** curate the highest-value agent-friendly datasets per domain; mirror prior-province density for parity tools; leave the long tail to the discovery tools. Curate only what's confirmed machine-readable via SODA.

### Module size
- **Mid-band ~14-18 tools.** 5 discovery + ~9-13 curated. The 1,270-dataset Socrata catalogue is rich enough to support BC/Manitoba density without padding. Final count locked during planning.

### Discovery tools (5 standard, Socrata flavor)
- `{prefix}_search_datasets`, `{prefix}_get_dataset_details`, `{prefix}_query_dataset`, `{prefix}_list_organizations`/categories, `{prefix}_list_categories` — adapted to the Socrata catalog API (themes/tags → categories). `query_dataset` runs a SoQL query against `/resource/{id}` with `$where`/`$select`/`$limit` etc.

### Transport / 511 handling — defer (consistent with Saskatchewan)
- **Defer transport tools** — Nova Scotia 511 / Highway data is HTML-only (no Socrata dataset, no clean feed). No `NOT_CONFIGURED` stubs. Revisit only if research finds a clean keyless feed.

### Geospatial
- Secondary ArcGIS Hub exists (`novagis.maps.arcgis.com`) but no public WFS found and REST services appear viewer-only. **Socrata-first**; only add an ArcGIS path if research confirms public no-auth FeatureServers worth curating. Default: geospatial datasets come through Socrata (GeoJSON/CSV with lat/long via SODA).

### Prompts and Resources (Phase 40 pattern)
- **6 bilingual prompts** (3 guided + 3 quick lookups) + **~7 zero-parameter resources**, scaled to the shipped surface. Candidate resources: `data://{prefix}/departments`, `data://{prefix}/health-zones`, `data://{prefix}/fishing-areas`, `docs://{prefix}/socrata-guide` (how SODA/SoQL works + which tool to use), `docs://{prefix}/portal-guide`, plus templates. Finalize during planning.

### Bilingual support
- Carry forward: bilingual `lang: Literal["en","fr"] = "en"` on every `@tool`, inline `lang == "fr"` ternary for error messages — no `shared/i18n.py:t()` adoption. NS data is English-primary (note: NS has Acadian French communities, but open data is overwhelmingly English); FR responses surface English content with French structural messages.

### Technical conventions (carry forward — no decisions needed)
- 7-file module pattern + `__tests__/`; standalone fastmcp decorators (NEVER `@mcp.*`)
- `(data, was_cached)` tuples with `cached_fetch()` + `get_limiter()`; aggressive flattening; flat Pydantic models
- A `TestSharedApiGetContract`-style test pinning the Socrata client's request contract (the Manitoba/Saskatchewan lesson — assert outgoing params, not just URL)
- Auto-paginate with a record cap + `truncated` flag (use SODA `$limit`/`$offset`); BM25 docstrings (`Use for:` + 8+ `Keywords:`)
- **Live-integration mandate:** integration tests MUST hit the real data.novascotia.ca SODA API and assert FIELD PRESENCE + non-null values (the lesson that caught Manitoba's live 400) — not just response shape.

### Claude's Discretion
- Final module prefix (`ns_` vs `nova_scotia_`); final dataset selection per domain
- Exact Socrata discovery surface (`/api/catalog/v1` vs `/api/views.json` vs data.json export) — research picks the most reliable
- SoQL query strategies; cache TTLs per tool; final prompt/resource set

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- NONE for Socrata yet — `shared/socrata.py` is NEW (the core deliverable of this phase's foundation).
- `shared/arcgis_hub.py` and `shared/ogc.py` are the structural templates for the new Socrata client (same shape: a focused async client returning flattened data).
- `shared/http.py` `api_get` (parsed-dict), `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py`, `shared/parsers.fetch_and_parse()` — all reused.
- `src/mcp_canada/modules/saskatchewan/` and `manitoba/` — closest module-structure references (newest 7-file modules; copy their tool/prompt/resource shape).

### Established Patterns
- 7-file module + `__tests__/`; tool prefix per module; bilingual `lang`; BM25 docstrings
- `(data, was_cached)` tuples; caching + rate limiting mandatory; aggressive flattening
- Standalone fastmcp decorators; zero-parameter resources
- Request-contract test class (assert outgoing params) + live field-presence integration tests

### Integration Points
- NEW: `src/mcp_canada/shared/socrata.py` + `shared/__tests__/test_socrata.py`
- NEW: `src/mcp_canada/modules/nova_scotia/` — full 7-file module + `__tests__/`
- `tests/integration/test_tool_scenarios.py` — append `TestNovaScotiaToolScenarios`
- `tests/integration/test_prompts_resources_scenarios.py` — append NS prompts/resources
- `README.md` / `docs/modules/nova-scotia.md` / `CLAUDE.md` — add NS section, update tool count, ADD SOCRATA as the 4th Portal Technology row
- `EXAMPLES.md` — add an NS cross-module example

</code_context>

<specifics>
## Specific Ideas

- **Primary portal:** data.novascotia.ca (Socrata) — confirmed via `X-Socrata-Region` header. ~1,270 datasets (`/api/views.json`).
- **SODA API:** `/api/catalog/v1` (catalog browse), `/api/views.json` (metadata), `/resource/{id}.json` + `/api/views/{id}/rows.csv?accessType=DOWNLOAD` (data). Keyless reads confirmed; optional `X-App-Token` raises throttle limits.
- **Example dataset:** Aquaculture Employment (`2bvk-dtnt`).
- **Signature domain sources:** Marine Aquaculture Leases, Rockweed Leases, Fish Hatchery Stocking Records, Wave/Current data.
- **Domain dataset counts:** Health 20, Environment/Energy 18, Lands/Forests/Wildlife 16, Roads/Transport 14 (HTML-only for 511), Fishing/Aquaculture 13, Demographics 13.
- **Geospatial:** `novagis.maps.arcgis.com` ArcGIS Online; no public WFS (`nsgi.novascotia.ca/wfs` → 404).
- **Federal fallback:** ~1,821 NS-mentioning datasets in open.canada.ca (not needed — provincial Socrata is rich).
- **Licence:** Open Government Licence (confirm exact variant during research).

</specifics>

<deferred>
## Deferred Ideas

- **Halifax and other NS municipal portals** — separate future phases (Halifax is Phase 33).
- **Transport / 511** — deferred (HTML-only, no clean feed). Revisit if a feed appears.
- **NS ArcGIS Hub (novagis) curated tools** — deferred unless research finds public no-auth FeatureServers worth curating; Socrata-first this phase.
- **Socrata `X-App-Token` / authenticated higher-throttle reads** — design for it, but keyless is the default; token support is a future enhancement if rate limits bite.
- **Generalizing `shared/socrata.py` for other Socrata portals** (other provinces/municipalities) — build it reusable now, but onboarding a 2nd Socrata portal is its own future phase.
- **Federal-catalogue-proxy** — not needed for NS (rich provincial Socrata); remains a pattern for data-sparse jurisdictions.
- **Bilingual `shared/i18n.py:t()` adoption** — systemic, its own future phase.

</deferred>

---

*Phase: 20-nova-scotia-government-open-data*
*Context gathered: 2026-06-15*
