# Phase 21: New Brunswick Government Open Data - Context

**Gathered:** 2026-07-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship a `new_brunswick` module exposing New Brunswick provincial data as MCP
tools — the 8th province in the rollout. Delivers the standard 5 discovery tools
plus curated tools across four data domains, following the 7-file module pattern.

**Not in this phase:** other Atlantic provinces (PEI is Phase 23, NL is Phase 22),
municipal NB portals, and any capability that would be its own phase.

</domain>

<decisions>
## Implementation Decisions

### Discovery — NB has no provincial catalogue (verified)

This is the structural difference from every prior province and the single most
important fact for planning.

- **D-01:** Discovery tools query the **federal CKAN filtered to
  `organization:nb`** — `https://open.canada.ca/data/api/3/action/package_search`
  with `fq=organization:nb`. Verified live: **221 first-party Government of New
  Brunswick datasets**, resource formats CSV 279 / HTML 197 / XML 112 / RSS 93 /
  RDF 74 / PDF 30 / SHP 20 / KML 18 / GeoJSON 17 (counted across the first 100
  packages). Reuses the existing CKAN plumbing (`shared/http.py` + a module-local
  `_api_get`) — no new client technology for discovery.
- **D-02:** GeoNB supplies the **curated geospatial** tools alongside CKAN
  discovery. The two surfaces are complementary, not alternatives: CKAN carries
  the tabular data (childcare, education, economic indicators), GeoNB carries the
  queryable geospatial layers.
- **D-03:** Do **not** use `q="New Brunswick"` as the discovery filter. It
  returns 906 results dominated by NRCan federal basemaps — noise.
  `organization:nb` is the precise filter. — **Reversibility:** reversible.

**Verified dead ends — do not re-investigate:**
- `data.gnb.ca` — DNS failure, does not exist
- `opendata.gnb.ca` — DNS failure, does not exist
- `nbopendata.ca` — DNS failure, does not exist
- GeoNB ArcGIS **Hub** (`geonb-snb.opendata.arcgis.com`) — HTTP 401,
  `"private org id ... is not accessible"`. The Hub Search API is unusable, so
  `shared/arcgis_hub.py:search_hub_datasets` cannot serve NB discovery.
- **CLAUDE.md's note "reuse for future Socrata portals PEI/NB" is wrong for NB.**
  There is no NB Socrata instance. Correct that line when this phase ships.

### ArcGIS — GeoNB is ArcGIS Server (MapServer), not Hub

- **D-04:** **Extend `shared/arcgis_hub.py`** rather than adding a new shared
  client or a module-local one. — **Reversibility:** costly — extraction into a
  separate `shared/arcgis_server.py` later would touch every NB call site plus
  the shared tests.
- **D-05:** `query_feature_service` **works against GeoNB MapServer unchanged** —
  verified live against `GeoNB_DNR_Crown_Land/MapServer` layer 3: returned 3
  feature dicts with keys `OBJECTID, HOLDER, Shape_Length, Shape_Area`. GeoNB
  honours `f=geojson`, and `{service_url}/{layer_id}/query` is the same path shape
  MapServer uses. **The query side needs no work.**
- **D-06:** The extension needed is on the **discovery side only** — a
  service-directory enumerator (`/arcgis/rest/services?f=json` → 62 services,
  then per-service `?f=json` for layers) to stand in for the unavailable Hub
  Search API.

**GeoNB facts for the researcher:**
- Base: `https://geonb.snb.ca/arcgis/rest/services`, ArcGIS Server 10.91
- **62 services, all `MapServer`, zero `FeatureServer`** — the layer `/query`
  endpoint is what makes them usable; `capabilities: Map,Query,Data`
- 5 of the 62 are basemaps (`GeoNB_Basemap_*`) — tiles, not data. Exclude.
- Service naming encodes the department: `GeoNB_{DEPT}_{Dataset}`

### Domains — all four in scope

54 of the 62 services, grouped by department prefix:

- **Flood & water (ENV 7 + ELG 7 = 14):** flood hazard index, historical floods,
  flood link, wetlands, protected watersheds, protected wellfields, coastal
  zones, lake/river water quality, contaminated sites, climate change adaptation
  plans, WAWA, local governance/service districts. **NB's signature domain** —
  the Saint John River flooding makes this the province's most distinctive data.
- **Crown land & forestry (DNR 8):** Crown land, forest, non-forest, forest
  soils, mineral occurrences, NBHN hydrographic network, provincial parks,
  wildlife refuges. NB is ~85% forested.
- **Parcels & civic address (SNB 21 + DPS 2 = 23):** parcels, buildings, civic
  address, NB911 communities, counties, municipal information, municipal
  planning, FSAs, historical municipal areas, contours, survey control network,
  imagery/lidar indexes. Largest group; strong for geocoding.
- **Health, education & boundaries (Health 2 + ENB 4 + EECD 1 + PETL 1 + NRCan 2
  = 9):** health facilities, health boundaries, regional health authorities,
  public schools, school districts, provincial and local government elections,
  WorkingNB boundaries, First Nations, place names.

- **D-07:** **Curation bar:** curate the highest-value service per sub-domain and
  let the discovery tools reach the long tail — the bar every prior province
  used. Do not attempt one tool per service.

### Module size

- **D-08:** **Mid-band ~18-22 tools** — 5 discovery + ~11-15 curated + 2 transport
  stubs. Matches Manitoba (20) and Nova Scotia (14-18). Final count locked during
  planning.

### Transport — NOT_CONFIGURED stubs

- **D-09:** Ship NB 511 tools behind an env var returning `NOT_CONFIGURED` when
  absent — the **Manitoba precedent** (`Five11NotConfigured` →
  `MANITOBA_511_KEY`). Verified: `https://511.gnb.ca/api/v2/get/event` returns
  `<Error><Message>Invalid Key</Message></Error>`, so the endpoint exists and is
  key-gated rather than absent.
- Note this diverges from Saskatchewan/Nova Scotia, which deferred transport
  entirely. The user chose stubs so the capability is discoverable and ready.
- **D-10:** The tools must still satisfy ERR-01 (catch-all coverage) — a
  `NOT_CONFIGURED` return is a normal envelope, not an exception path.

### Bilingual — NB is Canada's only officially bilingual province

- **D-11:** Carry forward the established pattern: `lang: Literal["en","fr"] =
  "en"` on every `@tool`, inline `lang == "fr"` ternary for messages, no
  `shared/i18n.py:t()` adoption.
- **D-12:** **NB-specific opportunity:** unlike prior provinces, the federal CKAN
  NB datasets carry genuine **FR/EN title pairs** (observed: "Établissements de
  garderies éducatives agréées" / "Licensed Early Learning and Childcare
  Facilities"). Where CKAN exposes French metadata, surface it for `lang="fr"`
  rather than returning English content with French structural messages. Research
  should confirm which CKAN fields carry the French variants.

### Claude's Discretion

- Module prefix: `nb_` (brevity, like `bc_`) vs `new_brunswick_` (full, like
  `manitoba_`/`saskatchewan_`). Module directory name is `new_brunswick`.
- Exact env var name for 511 (`NEW_BRUNSWICK_511_KEY` follows precedent)
- Final dataset/service selection within each of the four domains
- Cache TTLs per tool; SoQL-equivalent query strategies for CKAN datastore
- Final prompt/resource set (Phase 40 pattern — expect ~6 prompts, ~7 resources)
- Whether the GeoNB service-directory enumerator caches the 62-service listing

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project conventions
- `CLAUDE.md` — module pattern, portal technologies table, core rules. **Contains
  a known error to fix in this phase:** the Socrata row claims "reuse for future
  Socrata portals PEI/NB" — NB has no Socrata instance.
- `.claude/rules/modules.md` — tool/client function requirements, error codes
- `.claude/rules/tests.md` — TDD, integration-test mandate, banned masking idioms
- `.claude/rules/engineering-standards.md` — change sizing, anti-rationalization

### Closest analog phases
- `.planning/phases/20-nova-scotia-government-open-data/20-CONTEXT.md` — the
  Atlantic-province template; most technical conventions carry forward verbatim
- `.planning/phases/18-*/` (Manitoba) — the `NOT_CONFIGURED` 511 pattern this
  phase adopts, and the multi-org ArcGIS structure
- `.planning/phases/19-*/` (Saskatchewan) — multi-base ArcGIS precedent

### Error-classification contract (Phases 20.2-20.4 — all merged)
- `src/mcp_canada/shared/errors.py` — `InvalidInput` / `NotFound` /
  `UpstreamData`. **Never `raise ValueError`.**
- `src/mcp_canada/shared/envelope.py` — `upstream_guard`, `make_response`,
  `make_error`
- `src/mcp_canada/shared/http.py` — `decode_json` / `decode_json_bytes`.
  **Never decode JSON outside these.**
- `tests/test_tool_error_handling.py`, `tests/test_error_classification_defaults.py`,
  `tests/test_upstream_error_classification.py` — structural guards that will
  fail this phase's code if the contracts are broken

### Requirements
- `.planning/REQUIREMENTS.md` — ERR-01..ERR-07 apply to every new tool

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/arcgis_hub.py:query_feature_service` — **works against GeoNB MapServer
  with no modification** (verified). Needs a sibling service-directory enumerator.
- `shared/http.py:api_get` + `decode_json` — the CKAN discovery path; the federal
  CKAN is the same API surface already used by the `ckan` module
- `shared/cache.py:cached_fetch`, `shared/rate_limiter.py:get_limiter` — standard
- `shared/parsers.py:fetch_and_parse` — for CKAN CSV/XLSX resources (221 datasets
  are CSV-heavy, so this will see real use)
- `modules/manitoba/client.py:Five11NotConfigured` — copy this pattern for 511

### Established Patterns
- 7-file module + `__tests__/`; standalone `@tool`/`@prompt`/`@resource` (never
  `@mcp.*`); `(data, was_cached)` tuples; aggressive flattening; flat Pydantic
- `@upstream_guard(<api_name>)` beneath `@tool` — enforced by
  `test_tool_error_handling.py`
- Auto-paginate with a record cap + `truncated` flag
- BM25 docstrings: `Use for:` + 8+ `Keywords:`

### Integration Points
- New module auto-registers via FileSystemProvider — **do not modify `server.py`**
- `scripts/generate_catalog.py --check` is a CI gate — regenerate `TOOLS.md`
- README tool catalogue must be updated (`.claude/rules/modules.md`)
- New shared-client behaviour needs a `TestSharedApiGetContract`-style test
  asserting **outgoing params**, not just the URL (the Manitoba/Saskatchewan lesson)

</code_context>

<specifics>
## Specific Ideas

- **Live-integration mandate:** integration tests MUST hit the real
  `geonb.snb.ca` and `open.canada.ca` endpoints and assert **field presence and
  non-null values**, not just response shape. This is the lesson that caught
  Manitoba's live 400 and Saskatchewan's wrong-layer bug.
- **Layer ids are not guessable.** Crown Land's only layer is id **3**, not 0 —
  exactly the Saskatchewan WSA_Reservoirs trap (layer 26, not 0). The planner
  must resolve layer ids from each service's `?f=json` rather than assuming 0.
- Flood is the signature domain — if a demo or prompt needs one showcase tool,
  make it flood hazard or historical floods.

</specifics>

<deferred>
## Deferred Ideas

- **Federal CKAN datastore queries for NB tabular data** — the 221 datasets
  include CSV resources that could support SQL-style querying via the existing
  `datastore` module. Worth considering, but combining two modules is its own
  design question; note for a later phase if the discovery tools prove insufficient.
- **NB municipal portals** (Fredericton, Moncton, Saint John) — separate
  municipal phases, consistent with how Toronto/Montreal/Vancouver are scoped.
- **GeoNB basemap/imagery services** (5 services) — tiles and imagery indexes,
  not attribute data. No agent value; excluded deliberately.
- **PEI Socrata assumption** — CLAUDE.md's claim about PEI is untested. NB's
  turned out false; verify PEI's independently in Phase 23 rather than inheriting
  the note.

### Reviewed Todos (not folded)
- `2026-04-12-research-cross-canada-er-wait-times-datasets.md` — no match to this
  phase (`todo.match-phase 21` returned zero matches). NB health data here is
  facilities and boundaries, not ER wait times.

</deferred>

---

*Phase: 21-new-brunswick-government-open-data*
*Context gathered: 2026-07-27*
