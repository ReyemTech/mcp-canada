# Phase 21: New Brunswick Government Open Data - Research

**Researched:** 2026-07-30
**Domain:** Federal CKAN (province-filtered) + ArcGIS Server MapServer service-directory enumeration + key-gated 511 stub
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Discovery — NB has no provincial catalogue (verified)**
- **D-01:** Discovery tools query the federal CKAN filtered to `organization:nb` —
  `https://open.canada.ca/data/api/3/action/package_search` with `fq=organization:nb`. Verified
  live: 221 first-party Government of New Brunswick datasets, resource formats CSV 279 / HTML 197 /
  XML 112 / RSS 93 / RDF 74 / PDF 30 / SHP 20 / KML 18 / GeoJSON 17 (counted across the first 100
  packages). Reuses the existing CKAN plumbing (`shared/http.py` + a module-local `_api_get`) — no
  new client technology for discovery.
- **D-02:** GeoNB supplies the curated geospatial tools alongside CKAN discovery. The two surfaces
  are complementary, not alternatives: CKAN carries the tabular data (childcare, education,
  economic indicators), GeoNB carries the queryable geospatial layers.
- **D-03:** Do not use `q="New Brunswick"` as the discovery filter. It returns 906 results
  dominated by NRCan federal basemaps — noise. `organization:nb` is the precise filter. —
  Reversibility: reversible.

**Verified dead ends — do not re-investigate:**
- `data.gnb.ca`, `opendata.gnb.ca`, `nbopendata.ca` — DNS failure, do not exist
- GeoNB ArcGIS Hub (`geonb-snb.opendata.arcgis.com`) — HTTP 401, "private org id ... is not
  accessible". The Hub Search API is unusable, so `shared/arcgis_hub.py:search_hub_datasets`
  cannot serve NB discovery.
- CLAUDE.md's note "reuse for future Socrata portals PEI/NB" is wrong for NB. There is no NB
  Socrata instance. Correct that line when this phase ships.

**ArcGIS — GeoNB is ArcGIS Server (MapServer), not Hub**
- **D-04:** Extend `shared/arcgis_hub.py` rather than adding a new shared client or a module-local
  one. — Reversibility: costly — extraction into a separate `shared/arcgis_server.py` later would
  touch every NB call site plus the shared tests.
- **D-05:** `query_feature_service` works against GeoNB MapServer unchanged — verified live against
  `GeoNB_DNR_Crown_Land/MapServer` layer 3: returned 3 feature dicts with keys `OBJECTID, HOLDER,
  Shape_Length, Shape_Area`. GeoNB honours `f=geojson`, and `{service_url}/{layer_id}/query` is the
  same path shape MapServer uses. The query side needs no work.
- **D-06:** The extension needed is on the discovery side only — a service-directory enumerator
  (`/arcgis/rest/services?f=json` → 62 services, then per-service `?f=json` for layers) to stand in
  for the unavailable Hub Search API.

**GeoNB facts:**
- Base: `https://geonb.snb.ca/arcgis/rest/services`, ArcGIS Server 10.91
- 62 services, all `MapServer`, zero `FeatureServer` — the layer `/query` endpoint is what makes
  them usable; `capabilities: Map,Query,Data`
- 5 of the 62 are basemaps (`GeoNB_Basemap_*`) — tiles, not data. Exclude.
- Service naming encodes the department: `GeoNB_{DEPT}_{Dataset}`

**Domains — all four in scope**

54 of the 62 services, grouped by department prefix:
- Flood & water (ENV 7 + ELG 7 = 14): flood hazard index, historical floods, flood link, wetlands,
  protected watersheds, protected wellfields, coastal zones, lake/river water quality, contaminated
  sites, climate change adaptation plans, WAWA, local governance/service districts. NB's signature
  domain.
- Crown land & forestry (DNR 8): Crown land, forest, non-forest, forest soils, mineral occurrences,
  NBHN hydrographic network, provincial parks, wildlife refuges. NB is ~85% forested.
- Parcels & civic address (SNB 21 + DPS 2 = 23): parcels, buildings, civic address, NB911
  communities, counties, municipal information, municipal planning, FSAs, historical municipal
  areas, contours, survey control network, imagery/lidar indexes. Largest group; strong for
  geocoding.
- Health, education & boundaries (Health 2 + ENB 4 + EECD 1 + PETL 1 + NRCan 2 = 9): health
  facilities, health boundaries, regional health authorities, public schools, school districts,
  provincial and local government elections, WorkingNB boundaries, First Nations, place names.
- **D-07:** Curation bar: curate the highest-value service per sub-domain and let the discovery
  tools reach the long tail — the bar every prior province used. Do not attempt one tool per
  service.

**Module size**
- **D-08:** Mid-band ~18-22 tools — 5 discovery + ~11-15 curated + 2 transport stubs. Matches
  Manitoba (20) and Nova Scotia (14-18). Final count locked during planning.

**Transport — NOT_CONFIGURED stubs**
- **D-09:** Ship NB 511 tools behind an env var returning `NOT_CONFIGURED` when absent — the
  Manitoba precedent (`Five11NotConfigured` → `MANITOBA_511_KEY`). Verified:
  `https://511.gnb.ca/api/v2/get/event` returns `<Error><Message>Invalid Key</Message></Error>`,
  so the endpoint exists and is key-gated rather than absent.
- Note this diverges from Saskatchewan/Nova Scotia, which deferred transport entirely. The user
  chose stubs so the capability is discoverable and ready.
- **D-10:** The tools must still satisfy ERR-01 (catch-all coverage) — a `NOT_CONFIGURED` return
  is a normal envelope, not an exception path.

**Bilingual — NB is Canada's only officially bilingual province**
- **D-11:** Carry forward the established pattern: `lang: Literal["en","fr"] = "en"` on every
  `@tool`, inline `lang == "fr"` ternary for messages, no `shared/i18n.py:t()` adoption.
- **D-12:** NB-specific opportunity: unlike prior provinces, the federal CKAN NB datasets carry
  genuine FR/EN title pairs (observed: "Établissements de garderies éducatives agréées" /
  "Licensed Early Learning and Childcare Facilities"). Where CKAN exposes French metadata, surface
  it for `lang="fr"` rather than returning English content with French structural messages.
  Research should confirm which CKAN fields carry the French variants. **Resolved by this
  research:** `title_translated`/`notes_translated` dict fields carry the variants; see Pattern 2
  and Pitfall 5 below.

### Claude's Discretion
- Module prefix: `nb_` (brevity, like `bc_`) vs `new_brunswick_` (full, like
  `manitoba_`/`saskatchewan_`). Module directory name is `new_brunswick`.
- Exact env var name for 511 (`NEW_BRUNSWICK_511_KEY` follows precedent)
- Final dataset/service selection within each of the four domains
- Cache TTLs per tool; SoQL-equivalent query strategies for CKAN datastore
- Final prompt/resource set (Phase 40 pattern — expect ~6 prompts, ~7 resources)
- Whether the GeoNB service-directory enumerator caches the 62-service listing

### Deferred Ideas (OUT OF SCOPE)
- Federal CKAN datastore queries for NB tabular data — the 221 datasets include CSV resources that
  could support SQL-style querying via the existing `datastore` module. Worth considering, but
  combining two modules is its own design question; note for a later phase if the discovery tools
  prove insufficient.
- NB municipal portals (Fredericton, Moncton, Saint John) — separate municipal phases, consistent
  with how Toronto/Montreal/Vancouver are scoped.
- GeoNB basemap/imagery services (5 services) — tiles and imagery indexes, not attribute data. No
  agent value; excluded deliberately.
- PEI Socrata assumption — CLAUDE.md's claim about PEI is untested. NB's turned out false; verify
  PEI's independently in Phase 23 rather than inheriting the note.
</user_constraints>

<phase_requirements>
## Phase Requirements

No concrete `NB-XX` requirement IDs exist yet — ROADMAP.md carries `Requirements: TBD` for Phase
21, matching every unplanned phase (20.1, 21-39). Per CONTEXT.md, the cross-cutting error-handling
requirements below apply to every tool this phase creates, and the planner should backfill
`NB-01..NB-NN` into REQUIREMENTS.md immediately after planning, following the Alberta (Phase 17) /
Manitoba (Phase 18) / Saskatchewan (Phase 19) / Nova Scotia (Phase 20) precedent.

| ID | Description | Research Support |
|----|-------------|-------------------|
| ERR-01 | Every `@tool` is covered by a catch-all (`@upstream_guard`, broad `except`, or a module helper that has one) | Pattern 4 (`Five11NotConfigured` + `except Exception`); every curated tool follows the same `@upstream_guard(<api_name>)` convention as Manitoba/Saskatchewan/Nova Scotia |
| ERR-02..ERR-04, ERR-06, ERR-07 | Blame declared at raise site via `shared/errors.py`; no bare `raise ValueError`; malformed bodies classified as upstream, not caller error | `shared/errors.py`/`shared/envelope.py` reviewed directly (Sources); no new decode paths bypass `decode_json`/`decode_json_bytes` |
| ERR-05 | Every shared client decodes JSON through `decode_json()`/`decode_json_bytes()` | The two new `shared/arcgis_hub.py` functions (Pattern 3) must use `decode_json`, matching every existing function in that module |
| (TBD) NB-01..05 | 5 discovery tools against federal CKAN filtered to `organization:nb` | D-01, D-03, Pattern 1, live-verified 221-dataset corpus |
| (TBD) NB-06..~20 | ~11-15 curated tools across flood/water, Crown land/forestry, parcels/civic address, health/education/boundaries | D-02, D-06, D-07; full layer-id/field resolution in Code Examples table |
| (TBD) NB-~21..23 | 2-3 transport (511) `NOT_CONFIGURED` stubs | D-09, D-10, Pattern 4 |
| (TBD) NB-final | Module conventions (standalone `@tool`, envelope, prefix, discoverability, 6 prompts + 7 resources) | Established pattern, `.claude/rules/modules.md` |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **7-file module pattern is mandatory:** `__init__.py`, `constants.py`, `schemas.py`, `client.py`,
  `tools.py`, `prompts.py`, `resources.py`, `__tests__/` — no deviation.
- **Standalone `@tool`/`@prompt`/`@resource`, never `@mcp.*`** — FileSystemProvider silently won't
  register `@mcp.tool`-decorated functions.
- **Every `@tool` needs:** `lang: Literal["en", "fr"] = "en"`, `make_response()`/`make_error()`
  return (never a raised exception), `Use for:` + `Keywords:` (8+) docstring lines, `nb_` module
  prefix (Claude's Discretion per CONTEXT.md — see also `new_brunswick_` alternative).
- **Catch-all error coverage is enforced by `tests/test_tool_error_handling.py`:** satisfy via
  `@upstream_guard(<api_name>)` beneath `@tool`, a broad `except Exception`/`httpx.HTTPError`, or a
  module helper that has one. Catching only `httpx.HTTPStatusError` is insufficient.
  Manitoba/Saskatchewan/Nova Scotia already model the correct shape for this phase to copy.
- **Never `raise ValueError`** — use `shared/errors.py`: `InvalidInput` → `INVALID_INPUT`,
  `NotFound` → `NOT_FOUND`, `UpstreamData` → `UPSTREAM_ERROR`. A plain `ValueError` defaults to
  `UPSTREAM_ERROR`; `except ValueError → INVALID_INPUT` is banned and enforced by
  `tests/test_error_classification_defaults.py`.
- **Never decode JSON outside `decode_json()`/`decode_json_bytes()`** (`shared/http.py`) —
  enforced by `tests/test_upstream_error_classification.py`. Applies to the two new
  `shared/arcgis_hub.py` functions this phase adds (Pattern 3) exactly as it applies to every
  existing decode site.
- **Client functions return `(data, was_cached)`**, use `cached_fetch()` + `get_limiter()`, flatten
  responses aggressively.
- **Don't:** add dependencies (none needed — see Standard Stack), modify `server.py` for the new
  module (FileSystemProvider auto-discovers it), put module tests outside
  `src/mcp_canada/modules/new_brunswick/__tests__/`, skip rate limiting, mix refactoring with
  feature work.
- **Integration tests must be able to fail** (`.claude/rules/tests.md`): every path through a
  `tests/integration/` test must reach an assertion; use `assert_live_or_transient` +
  `assert_rows`; tolerate only `UPSTREAM_ERROR`/`RATE_LIMITED`/`UPSTREAM_UNAVAILABLE`, never
  `NOT_FOUND` on a call that should succeed. The 511 `NOT_CONFIGURED` path is a *deterministic*
  success-shaped envelope (per Manitoba precedent), not a tolerated failure — assert its exact
  shape, don't wrap it in `tolerates_upstream_error`.
- **README.md and `scripts/generate_catalog.py --check` (TOOLS.md) must be regenerated/updated**
  when tools are added — CI gate.
- **CLAUDE.md itself needs a correction** as part of this phase's docs update: the Socrata portal
  row's "reuse for future Socrata portals PEI/NB" claim is confirmed false for NB (verified no NB
  Socrata instance exists) — update the row to remove NB, per CONTEXT.md.
- Coverage must stay ≥95% (`uv run pytest --cov=src/mcp_canada --cov-fail-under=95`).

## Summary

New Brunswick is structurally different from every prior province in this rollout: it has no
provincial CKAN or ArcGIS Hub catalogue. Discovery for tabular data comes from the **federal
open.canada.ca CKAN** filtered to `organization:nb` (verified live: 221 datasets), reusing the
`ckan`/`alberta` module's `_api_get` + `fq` pattern with zero new client code. Geospatial data
comes from **GeoNB**, a bare ArcGIS **Server** (not Hub) exposing 62 `MapServer` services with no
Hub Search API in front of them (the Hub UI at `geonb-snb.opendata.arcgis.com` 401s). This means
`shared/arcgis_hub.py:query_feature_service` needs zero changes — verified live against 13
services below, `f=geojson` and `/{layer_id}/query` behave identically to FeatureServer — but a
new discovery primitive is required: a service-directory enumerator that walks
`/arcgis/rest/services?f=json` (62 services) then each service's `?f=json` (layers). Layer ids are
non-guessable and were resolved live for every candidate curated service in this document.

The federal CKAN NB corpus resolves this phase's one open question (D-12): every result carries
`title_translated`/`notes_translated` dict fields, which the existing `ckan/client.py:_shape_dataset`
fallback pattern (`title_translated.get(lang) or title_translated.get("en") or raw.get("title")`)
already handles correctly — no new logic needed, just reuse of the established pattern inside the
NB module's own dataset-shaping function. NB 511 is confirmed key-gated (`HTTP 400` /
`Invalid Key` on the real endpoint, not absent) — the Manitoba `Five11NotConfigured` stub pattern
applies directly, with `NEW_BRUNSWICK_511_KEY` as the env var name.

**Primary recommendation:** Build `new_brunswick` as a two-surface module — 5 discovery tools
against federal CKAN (`organization:nb` fixed filter) plus ~11-15 curated tools against GeoNB
MapServer layers (using `arcgis_hub.query_feature_service`, unchanged) — and add exactly one new
function to `shared/arcgis_hub.py`: a service/layer enumerator for bare ArcGIS Server portals
without a Hub Search API in front of them.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Dataset discovery/search (tabular) | API / Backend (MCP tool -> federal CKAN) | — | Federal CKAN `package_search` is the only NB catalogue; no provincial equivalent exists |
| Bilingual title/notes resolution | API / Backend (client-side shaping) | — | `title_translated`/`notes_translated` already present in the upstream payload; tool layer just selects the right key |
| Geospatial service/layer discovery | API / Backend (`shared/arcgis_hub.py` new enumerator) | — | GeoNB has no Hub Search API; discovery must walk the ArcGIS Server REST directory directly |
| Geospatial feature query | API / Backend (`arcgis_hub.query_feature_service`, unchanged) | — | GeoNB MapServer `/query` endpoint behaves like FeatureServer; no new query code required |
| CSV/XLSX resource parsing (CKAN resources) | API / Backend (`shared/parsers.py:fetch_and_parse`) | — | 221 NB CKAN datasets skew CSV-heavy; existing parser handles this without changes |
| 511 transport data | API / Backend (env-var-gated stub, Manitoba pattern) | — | Endpoint exists and is key-gated server-side; MCP tool cannot bypass gating, only report `NOT_CONFIGURED` |
| Rate limiting / caching | API / Backend (`shared/rate_limiter.py`, `shared/cache.py`) | — | Standard cross-module infrastructure, unchanged |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | (pinned in pyproject, unchanged) | Async HTTP client for CKAN + GeoNB REST calls | Already the project's sole HTTP client; no new dependency |
| pydantic v2 | (pinned, unchanged) | Flat schema models for NB tool responses | Project-wide convention (`.claude/rules/modules.md`) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `shared/arcgis_hub.py` (existing) | in-repo | `query_feature_service`, `get_layer_metadata`, `get_count` — used unchanged against GeoNB MapServer | Every curated geospatial tool |
| `shared/http.py` (existing) | in-repo | `api_get`, `decode_json`/`decode_json_bytes` for CKAN calls | Every discovery tool |
| `shared/parsers.py` (existing) | in-repo | `fetch_and_parse` for CKAN CSV/XLSX resources | Discovery-routed tabular resources |
| `shared/cache.py`, `shared/rate_limiter.py` (existing) | in-repo | `cached_fetch`, `get_limiter` | Every client function |

**No new external dependencies are required for this phase** — verified against `.claude/rules/engineering-standards.md` dependency policy ("don't add dependencies").

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Federal CKAN `organization:nb` filter | `q="New Brunswick"` free-text search | Rejected — verified live to return 906 noisy NRCan-basemap-dominated results (D-03); `organization:nb` returns the precise 221 |
| New `shared/arcgis_server.py` client | Extend `shared/arcgis_hub.py` (D-04) | A separate client would duplicate `query_feature_service`/`get_layer_metadata`/`get_count` verbatim since GeoNB MapServer needs zero query-side changes; only discovery differs |
| GeoNB ArcGIS Hub Search API | Service-directory enumeration (`/arcgis/rest/services?f=json`) | Hub Search returns HTTP 401 "private org id ... is not accessible" — verified dead end, not usable |

**Installation:**
```bash
# No new packages — reuses existing httpx/pydantic/aiocache/tenacity stack
```

**Version verification:** No new packages introduced; existing pinned versions in `pyproject.toml`
remain unchanged for this phase.

## Package Legitimacy Audit

Not applicable — this phase introduces zero new external packages. All functionality is built on
already-vetted in-repo shared clients (`shared/arcgis_hub.py`, `shared/http.py`,
`shared/parsers.py`) and the standard library.

**Packages removed due to [SLOP] verdict:** none (no new packages).
**Packages flagged as suspicious [SUS]:** none (no new packages).

## Architecture Patterns

### System Architecture Diagram

```
Agent query
    │
    ▼
discover_tools (BM25) ──► call_tool
                              │
              ┌───────────────┴────────────────┐
              │                                 │
   nb_search_datasets /                 nb_query_features /
   nb_get_dataset_details /             nb_get_crown_land / etc.
   nb_query_dataset /                          │
   nb_list_organizations /                     ▼
   nb_list_categories                  shared/arcgis_hub.py
              │                         query_feature_service()
              ▼                         GET {geonb_service}/{layer_id}/query
  open.canada.ca CKAN                    ?f=geojson&where=...&outFields=*
  package_search?fq=organization:nb              │
              │                                  ▼
              ▼                          geonb.snb.ca ArcGIS Server
  221 NB datasets (CSV/HTML/XML/         (MapServer, 62 services,
  RSS/RDF/PDF/SHP/KML/GeoJSON)            non-guessable layer ids)
              │
              ▼
  title_translated[lang] / notes_translated[lang]
  fallback -> title_translated["en"] -> raw title
  (existing ckan/client.py pattern, reused)
              │
              ▼
  resource routing: CSV/XLSX -> shared/parsers.py:fetch_and_parse
                    other    -> metadata-only (discovery-only note)

  nb_get_road_events / nb_get_winter_road_conditions / nb_get_traffic_cameras
              │
              ▼
  os.environ["NEW_BRUNSWICK_511_KEY"] absent
              │
              ▼
  Five11NotConfigured  ──►  make_error("NOT_CONFIGURED", ...)
  (511.gnb.ca/api/v2/get/event exists and returns
   <Error><Message>Invalid Key</Message></Error> when unkeyed)

  Discovery side needs ONE new shared/arcgis_hub.py function:
  list_arcgis_server_services(base_url) -> walks /arcgis/rest/services?f=json
  get_arcgis_server_layers(service_url) -> walks {service}/MapServer?f=json
  (no Hub Search API exists in front of GeoNB — this replaces it for discovery only)
```

### Recommended Project Structure
```
src/mcp_canada/modules/new_brunswick/
├── __init__.py          # MODULE_NAME = "new_brunswick", MODULE_DESCRIPTION
├── constants.py          # BASE_URL (federal CKAN), GEONB_BASE_URL, layer-id map, RATE_GROUP/RATE_LIMIT, CACHE_TTLs, FIVE11_KEY_ENV
├── schemas.py             # Flat Pydantic models: NBDatasetSummary, NBDatasetDetails, NBFloodHazardArea, NBCrownLandParcel, NBCivicAddress, NB511Event, ...
├── client.py              # fetch_search_datasets/fetch_dataset_details/fetch_query_dataset (federal CKAN via fq=organization:nb)
│                           # fetch_flood_hazard_areas/fetch_historical_floods/fetch_wetlands/... (arcgis_hub.query_feature_service against GeoNB)
│                           # Five11NotConfigured + _511_get (Manitoba pattern) for 3 transport stubs
├── tools.py                # nb_ prefixed @tool functions, @upstream_guard(...) on each
├── prompts.py               # ~6 @prompt functions
├── resources.py              # ~7 @resource functions (data://, docs://, template://)
└── __tests__/
    ├── conftest.py
    ├── test_client.py
    ├── test_tools.py
    └── test_prompts_resources.py

src/mcp_canada/shared/
└── arcgis_hub.py           # + list_arcgis_server_services(), get_arcgis_server_layers()
    __tests__/test_arcgis_hub.py  # + TestListArcgisServerServices, TestGetArcgisServerLayers
```

### Pattern 1: Federal CKAN discovery fixed to `organization:nb`
**What:** Every NB discovery tool composes `fq="organization:nb"` (optionally AND-ed with a
caller-supplied `fq` fragment for format/tag filters) rather than exposing an open `organization`
parameter like Alberta/BC do against their own provincial CKAN.
**When to use:** All 5 discovery tools (`search_datasets`, `get_dataset_details`,
`query_dataset`, `list_organizations`, `list_categories`).
**Example:**
```python
# Source: verified live 2026-07-30 against open.canada.ca
# GET https://open.canada.ca/data/api/3/action/package_search
#     ?fq=organization:nb&rows=5
# -> {"success": true, "result": {"count": 221, "results": [...]}}
async def fetch_search_datasets(
    query: str = "",
    extra_fq: str | None = None,
    rows: int = 10,
    start: int = 0,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    fq = "organization:nb"
    if extra_fq:
        fq = f"{fq} AND {extra_fq}"
    result, cached = await _api_get(
        "action/package_search",
        {"q": query, "fq": fq, "rows": rows, "start": start},
        CACHE_TTL_SEARCH,
    )
    ...
```

### Pattern 2: Bilingual title/notes resolution (reuse, do not reinvent)
**What:** Federal CKAN NB records carry `title_translated`/`notes_translated` dicts. Verified live:
some records are genuinely bilingual within one record (`Submerged Lands Management Areas` /
`Zones de gestion des terres submergées` — different EN/FR text in the same record), while others
are separately-published FR and EN datasets whose `title_translated` mirrors the same language in
both `en`/`fr` keys (e.g. the childcare dataset pair — two distinct CKAN `name`/`id` values, one
all-French, one all-English). **Both cases are handled correctly by the same fallback chain** — no
special-casing is needed for the duplicate-record case.
**When to use:** Every discovery tool's dataset-shaping function.
**Example:**
```python
# Source: mcp_canada/modules/ckan/client.py:_shape_dataset (existing, verified pattern)
title_translated = raw.get("title_translated")
if title_translated:
    title = title_translated.get(lang) or title_translated.get("en") or raw.get("title")
else:
    title = raw.get("title")

notes_translated = raw.get("notes_translated")
if notes_translated:
    description = notes_translated.get(lang) or notes_translated.get("en") or raw.get("notes")
else:
    description = raw.get("notes")
```

### Pattern 3: GeoNB service-directory enumeration (new `shared/arcgis_hub.py` function)
**What:** A thin pair of functions that walk the ArcGIS Server REST directory instead of a Hub
Search API. `list_arcgis_server_services` hits `{base_url}?f=json` and returns the `services` list
(filtering out `?f=json`-only folders); `get_arcgis_server_layers` hits `{service_url}/MapServer?f=json`
and returns the `layers`/`tables` array with `id`/`name`. Both are read-only GET calls with the same
`decode_json` discipline as every other shared client function.
**When to use:** NB's 2 discovery-adjacent geospatial tools (`nb_list_geonb_services`,
`nb_get_geonb_service_layers`) that stand in for the missing Hub Search API. Curated tools call
`get_layer_metadata`/`query_feature_service` directly with the layer id resolved once at
research/planning time (hardcoded per curated tool, same as every other province's curated
FeatureServer/MapServer tools) — they do NOT call the new enumerator at runtime.
**Example:**
```python
# Source: verified live 2026-07-30 against geonb.snb.ca
# GET https://geonb.snb.ca/arcgis/rest/services?f=json
# -> {"folders": [...], "services": [{"name": "GeoNB_DNR_Crown_Land", "type": "MapServer"}, ...]}  (62 entries)
async def list_arcgis_server_services(
    base_url: str,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    url = base_url.rstrip("/")
    params = {"f": "json"}
    client_cm = httpx_client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
    ...
    data = decode_json(response, url)
    return data.get("services", [])


async def get_arcgis_server_layers(
    service_url: str,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    # GET {service_url}/MapServer?f=json -> {"layers": [...], "tables": [...]}
    url = f"{service_url.rstrip('/')}/MapServer"
    ...
    data = decode_json(response, url)
    return {
        "layers": [{"id": l.get("id"), "name": l.get("name")} for l in data.get("layers", [])],
        "tables": [{"id": t.get("id"), "name": t.get("name")} for t in data.get("tables", [])],
    }
```

### Pattern 4: NOT_CONFIGURED 511 stub (Manitoba precedent, copied verbatim)
**What:** `Five11NotConfigured` exception raised when `NEW_BRUNSWICK_511_KEY` is absent; tool layer
catches it and returns `make_error("NOT_CONFIGURED", ...)` — a normal envelope, not an exception
path, satisfying D-10/ERR-01.
**When to use:** The 3 NB 511 tools (road events, winter road conditions, traffic cameras) — same
shape as Manitoba's 3 511 tools.
**Example:**
```python
# Source: mcp_canada/modules/manitoba/client.py (existing, verified pattern) + live NB endpoint check
# GET https://511.gnb.ca/api/v2/get/event -> HTTP 400, body: <Error><Message>Invalid Key</Message></Error>
class Five11NotConfigured(Exception):
    """Raised when NEW_BRUNSWICK_511_KEY env var is not set."""

async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict]:
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set.")
    rows = await api_get(f"{FIVE11_BASE_URL}/{endpoint}", {**(params or {}), "key": key})
    return rows if isinstance(rows, list) else []
```

### Anti-Patterns to Avoid
- **Assuming layer 0 for any GeoNB service:** Verified false for Crown Land (only layer is `3`),
  Historical Floods (main combined layer is `0` but the oldest event, 1973, is layer `8`),
  Mineral Occurrences (`0,1,7,2,3,4,5,8,6` — non-sequential), Counties (Counties is `0`, Parishes is
  `1`). Always resolve via `{service}/MapServer?f=json` before writing a curated tool.
- **Treating `GeoNB_DNR_WildlifeRefuges` as live data:** Verified its only layer (id 0) is literally
  named `"Retired Map Service"` and returns exactly 1 dummy polygon. Exclude from curation —
  documented as a dead end alongside the other 5 basemap services.
- **Calling GeoNB Hub Search API:** `geonb-snb.opendata.arcgis.com` returns HTTP 401 "private org
  id ... is not accessible" — already verified dead in CONTEXT.md; do not re-attempt.
- **Adding an `organization` parameter to NB's federal CKAN discovery tools:** Unlike Alberta/BC
  discovery tools (which query their OWN provincial CKAN and legitimately let callers pick any
  organization), NB discovery is filtered federal CKAN — the `organization:nb` fq must be
  non-optional so the tool never accidentally returns non-NB federal datasets.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ArcGIS MapServer layer querying (pagination, geojson parsing) | A NB-specific fetch loop | `shared/arcgis_hub.py:query_feature_service` (unchanged) | Verified live to work against GeoNB MapServer identically to FeatureServer; reimplementing would duplicate pagination/geometry logic already correct |
| CKAN envelope handling / bilingual title fallback | A NB-specific `_shape_dataset` from scratch | The exact fallback chain already in `ckan/client.py`/`alberta/client.py` | Federal CKAN envelope shape and `title_translated`/`notes_translated` behavior is identical across all federal-CKAN-backed provinces; the logic is already correct and tested |
| 511 key-gating detection | Custom retry/backoff around the "Invalid Key" XML error | `Five11NotConfigured` + env-var check before any network call (Manitoba pattern) | The gating is server-side and permanent without a real key; no amount of client retry logic changes that — the correct behavior is a fast, cache-free `NOT_CONFIGURED` |
| JSON decoding of GeoNB/CKAN responses | Raw `response.json()` | `shared/http.py:decode_json`/`decode_json_bytes` | ERR-05 contract — a malformed GeoNB or CKAN body must raise `httpx.DecodingError`, not a `ValueError` subclass that gets blamed on the caller |

**Key insight:** This phase's only genuinely new code is a ~30-40 line discovery-side addition to
`shared/arcgis_hub.py`. Every other capability — CKAN discovery, MapServer querying, bilingual
metadata, 511 stubbing — is a direct application of a pattern already shipped and tested in a prior
province phase. The risk in this phase is not missing capability, it's re-deriving something that
already exists correctly elsewhere in the codebase.

## Common Pitfalls

### Pitfall 1: Guessing layer ids instead of resolving them
**What goes wrong:** A curated tool is written against layer `0` by convention (as with
FeatureServer-based provinces where layer 0 is usually the primary layer), but GeoNB MapServer
services frequently have layer 0 be a secondary/derived layer, or no layer 0 at all.
**Why it happens:** Every prior FeatureServer-based province (Manitoba, Saskatchewan, Alberta)
mostly used layer 0 by convention; MapServer services published from legacy shapefile/geodatabase
exports do not follow that convention.
**How to avoid:** Every curated tool's layer id in this research was resolved via a live
`{service}/MapServer?f=json` call (see Code Examples). Copy those ids verbatim; if a new service is
added during planning/execution that isn't in this document, resolve its layers the same way before
writing the tool.
**Warning signs:** A `query_feature_service` call returning 0 features when the ArcGIS REST catalog
UI (or `?f=json`) shows non-zero features on a different layer id.

### Pitfall 2: Treating GeoNB field names as self-describing
**What goes wrong:** Several services expose truncated, shapefile-derived field names —
`Flood_Haza`, `Technical_`, `Hospital_N`, `Hospital_O`, `strID`, `strDST` (public schools) — that do
not match their human-readable meaning and are easy to typo or misattribute.
**Why it happens:** GeoNB's underlying data was originally shapefile/geodatabase (10-character
field name limits), then published to ArcGIS Server without renaming.
**How to avoid:** Verify exact field names via `{service}/MapServer/{layer_id}?f=json` (`fields`
array) before writing a tool's `out_fields`/response-shaping code — do not infer from the layer's
display name. Field lists for all shortlisted curated layers are captured in Code Examples below.
**Warning signs:** A tool returns `null`/missing values for a field name that "should" exist based
on the layer's display name.

### Pitfall 3: Assuming every service in the 62-service directory is live, current data
**What goes wrong:** `GeoNB_DNR_WildlifeRefuges` layer 0 is literally titled `"Retired Map
Service"` and holds exactly one placeholder polygon (verified live). A tool built against it would
silently ship broken/meaningless data.
**Why it happens:** The service-directory listing includes historical/retired services alongside
current ones with no `status` flag distinguishing them.
**How to avoid:** Before curating any service, fetch its layer(s) `?f=json` (checking name/geometry
plausibility) AND run a `returnCountOnly=true` query to sanity-check record count is non-trivial.
**Warning signs:** A layer name containing "Retired", "Archive", "Old", or a record count of 0-2
against a dataset that should plausibly have dozens+ records.

### Pitfall 4: `HOLDER` (and similarly coded integer fields) have no server-exposed domain
**What goes wrong:** `GeoNB_DNR_Crown_Land` layer 3's `HOLDER` field is `esriFieldTypeSmallInteger`
with `"domain": null` — the raw integer code (e.g. `2`) has no machine-readable lookup exposed by
the service itself.
**Why it happens:** Not every ArcGIS Server field carries a coded-value domain even when the
underlying data is categorical; NB published this one without a domain.
**How to avoid:** Document in the tool's docstring that `holder` is returned as a raw code with no
in-service decoding available (agents should not assume it is a free-text holder name). Do not
invent a code-to-name mapping without an authoritative NB source — flag as an Assumption if one is
added.
**Warning signs:** An agent asking "who holds this Crown land parcel" gets back a bare integer.

### Pitfall 5: CKAN duplicate FR/EN dataset publishing looks like a bilingual-metadata bug but isn't
**What goes wrong:** Seeing two CKAN records with near-identical `notes` content but different
`name`/`id` values (one all-French, one all-English) can look like a data-quality bug in NB's
federal CKAN feed.
**Why it happens:** NB publishes some open datasets as two separate CKAN records (one per
language) rather than one bilingual record — verified live for the childcare-facilities dataset
pair.
**How to avoid:** Do not attempt to deduplicate or merge these pairs in the discovery tool. The
existing `title_translated.get(lang) or title_translated.get("en") or raw.get("title")` fallback
already returns the correct-language title for whichever record id is fetched — this pattern
requires no special handling for the duplicate-record case.
**Warning signs:** Search results appearing to contain "duplicate" datasets under different names.

## Code Examples

Verified patterns from live sources (2026-07-30):

### GeoNB service-directory listing (62 services, all MapServer)
```bash
# Source: live GET https://geonb.snb.ca/arcgis/rest/services?f=json
# folders: ['Geocoding', 'GeoNB_Imagery_NBSD', 'geoprocessing', 'GRP', 'RIPT', 'test', 'Utilities']
# services: 62 entries, ALL type "MapServer" — zero FeatureServer
# 5 basemap services (GeoNB_Basemap_Grey/Imagery/NBRN/Provinces_bare/Topo) — exclude, tiles not data
```

### Federal CKAN NB filter (221 datasets, verified)
```bash
# Source: live GET https://open.canada.ca/data/api/3/action/package_search?fq=organization:nb&rows=5
# {"success": true, "result": {"count": 221, "results": [...]}}
# Resource formats across first 100: CSV 279, HTML 197, XML 112, RSS 93, RDF 74, PDF 30, SHP 20,
# KML 18, GeoJSON 17 (per CONTEXT.md D-01, re-confirmed live)
```

### Resolved layer ids and fields for curation candidates (all verified live)

| Service | Layer id | Layer name | Geometry | Record count | Key fields |
|---------|---------|------------|----------|---------------|------------|
| `GeoNB_ENV_FloodHazardIndex` | **0** | Flood Hazard | Polygon | 269 | `Flood_Haza`, `Technical_`, `Sheet_Numb` |
| `GeoNB_ENV_Historical_Floods` | **0** (main), **8** (1973 event) | 2008/2018 Flood Limits; 1973 Flood Limits | Polyline | 5 (layer 0) | `ID`, `KEY`, `FEATURE`, `SOURCE`, `LIMIT` |
| `GeoNB_ENV_Flood_Link` | **0** | Flood hazard maps | — | — | link-out layer to external flood maps |
| `GeoNB_ENV_Wetlands` | **2** (Wetland; 1=PSW, 0=30m buffer) | Wetland | Polygon | 163,206 | `Hectares`, `WETLAND_CLASS`, `STATUS` |
| `GeoNB_ENV_ProtectedWatersheds` | **0** (overview), 1-4 (zone detail) | Protected Watersheds | — | — | zone-tiered; use layer 0 for overview |
| `GeoNB_ENV_ProtectedWellfields` | **0** | ELG Wellfields | — | — | — |
| `GeoNB_ELG_WaterQuality_Lakes_Rivers` | **0** (Stations) | Stations | Point | — | — |
| `GeoNB_ELG_CoastalZones` | **0** | NB_Zones | — | — | — |
| `GeoNB_ELG_Contaminated_Sites` | **0** | Contaminated Sites | Point | 9,736 | `Status_E`/`Status_F`, `FileOpenDate`, `PidType_E`/`PidType_F` |
| `GeoNB_DNR_Crown_Land` | **3** (only layer) | Crown Land | Polygon | 10,001 | `HOLDER` (int, no domain — Pitfall 4), `OBJECTID` |
| `GeoNB_DNR_Forest` | 0-5 (Treatment/Location tiers) | — | — | — | tiered by treatment type / location |
| `GeoNB_DNR_NonForest` | 0-6 (category tiers) | Agricultural/Wilderness/Urban/... | — | — | category-per-layer |
| `GeoNB_DNR_MineralOccurrences` | **0** (Mineral) | Mineral | Point | 1,611 | `NAME`, `COMMODITIE`, `LAT`, `LON`; layer ids non-sequential (0,1,7,2,3,4,5,8,6) |
| `GeoNB_DNR_ProvincialParks` | **0** | Provincial Parks | Polygon | 24 | `NAME`/`Nom`, `AREA`, `Hectares` |
| `GeoNB_DNR_WildlifeRefuges` | 0 | **"Retired Map Service"** | Polygon | **1** | EXCLUDE — dead/placeholder (Pitfall 3) |
| `GeoNB_SNB_Parcels` | **0** (parcels), 1 (labels) | parcels | Polygon | 604,520 | `PID`, `COUNTY`, `Titles_Status`, `Gazette_Status` |
| `GeoNB_SNB_Buildings` | **0** | Buildings | — | — | — |
| `GeoNB_DPS_Civic_Address` | **0** | Civic_Addresses | Point | 373,172 | `CIVIC_NUM`, `STREET`, `ST_TYPE_E`/`ST_TYPE_F`, `COMMUNITY` |
| `GeoNB_DPS_NB911_Communities` | **0** | Communities | Polygon | 1,197 | `COMMUNITY_CD`, `COMMUNITY_NAME`, `BELL_COMMUNITY_NAME` |
| `GeoNB_SNB_Counties` | **0** (Counties), 1 (Parishes) | Counties | — | — | — |
| `GeoNB_Health_Facilities` | **0-5** (facility-type dispatch) | Hospital(Horizon)/Hospital(Vitalité)/After-hours/Adult residential/Nursing home/Pharmacy | Point | 12 (hospitals) | `Hospital_N`, `Hospital_O`, `Name_E`/`Name_F`, `Telephone_` |
| `GeoNB_Health_Boundaries` | 0 (NBDOH regions), 1 (NBHC communities) | — | — | — | — |
| `GeoNB_EECD_PublicSchools` | **0** (Anglophone), 1 (Francophone) | — | Point | 206 (Anglophone) | `strID`, `strNM`, `strAD1`, `strGR`, `strURL` |
| `GeoNB_ENB_Provincial_Elections` | **2** (2024 districts — most current) | Provincial Electoral Districts 2024 | Polygon | 49 | `DIST_ID`, `PED_Names_B` |
| `GeoNB_NRCan_FirstNations` | **0** | First Nations Land | — | — | — |

**Verified: `f=geojson` on GeoNB behaves identically to FeatureServer** — confirmed live against
`GeoNB_DNR_Crown_Land/MapServer/3/query?f=geojson` returning a standard `FeatureCollection` with
`OBJECTID`/`HOLDER`/`Shape_Length`/`Shape_Area` properties, matching CONTEXT.md D-05 exactly.

### NB 511 key-gating (confirmed live)
```
GET https://511.gnb.ca/api/v2/get/event
-> HTTP 400
-> Content-Type: application/xml
-> <Error><Message>Invalid Key</Message></Error>
```
Endpoint exists, is reachable, and rejects unkeyed requests with a structured error — same shape
Manitoba 511 v3 exhibited. No public/free-key registration page was found for NB 511 in this
research pass (unlike Manitoba's documented `manitoba511.ca/my511/register`); this is flagged as
an open question below — the `NOT_CONFIGURED` message should point agents to the general
`511.gnb.ca` site rather than a specific unverified registration URL.

### Verified dead ends (do not re-investigate — reconfirmed live 2026-07-30)
```
data.gnb.ca        -> DNS/connect failure (curl exit, no HTTP response)
opendata.gnb.ca    -> DNS/connect failure
nbopendata.ca      -> DNS/connect failure
geonb-snb.opendata.arcgis.com -> HTTP 401 "private org id ... is not accessible" (per CONTEXT.md; not re-probed this pass to avoid hammering a known-401 host)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Provincial-catalogue-first discovery (CKAN/ArcGIS Hub/Socrata, as in every prior province) | Federal-CKAN-filtered discovery (`organization:nb`) | This phase (first federal-CKAN-only province) | Discovery tools cannot expose an open `organization=` parameter the way BC/Alberta do — it must default to (and often be locked to) `nb` |
| ArcGIS Hub Search as the geospatial discovery layer (York Region, Alberta, Manitoba, Saskatchewan) | Raw ArcGIS Server REST directory enumeration (`?f=json`) | This phase (first bare-ArcGIS-Server province) | `shared/arcgis_hub.py` needs its second orthogonal discovery primitive (Hub Search vs. Server directory) — module name stays the same per D-04, but the two code paths are unrelated |

**Deprecated/outdated:** None — this is additive, not a replacement of any existing shared code.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `NEW_BRUNSWICK_511_KEY` follows the `MANITOBA_511_KEY` naming precedent and there is no publicly documented free-registration URL for NB 511 (unlike Manitoba's `manitoba511.ca/my511/register`) | Common Pitfalls / Code Examples (511 section), Validation Architecture | If a registration URL does exist and isn't surfaced, the `NOT_CONFIGURED` message is less helpful than Manitoba's; low risk since the stub behavior itself does not depend on the URL text |
| A2 | The curated-tool shortlist (26 services checked, ~20 recommended for curation) satisfies D-07's "highest-value service per sub-domain" bar without executing a full per-service value assessment against all 62 services | Standard Stack / Code Examples table | Low — the planner may substitute 1-2 services within a domain during planning; the layer-id resolution methodology transfers directly to any substitute |
| A3 | Layer field values documented here (e.g., `HOLDER` as raw integer with no domain) reflect the current GeoNB publish state and will not change before implementation | Common Pitfalls (Pitfall 4) | Low — GeoNB services are described in CONTEXT.md as stable ArcGIS Server 10.91; re-verify at Wave 0 per the Validation Architecture "Wave 0 Gaps" below |

**Risk summary:** All core structural claims (221 CKAN datasets, 62 GeoNB services, specific layer
ids, `title_translated` shape, 511 key-gating) were verified live during this research session, not
assumed. The assumptions above are narrow and low-risk.

## Open Questions

1. **Does NB 511 have a public free-key registration process like Manitoba's?**
   - What we know: The endpoint (`511.gnb.ca/api/v2/get/event`) exists and returns a structured
     "Invalid Key" error, confirming it is key-gated rather than absent.
   - What's unclear: No public registration/developer-portal URL for NB 511 was located in this
     research pass (Manitoba's `manitoba511.ca/my511/register` has no NB equivalent found).
   - Recommendation: Ship the `NOT_CONFIGURED` stub pointing agents to `https://511.gnb.ca` (the
     general public site) rather than inventing a specific registration URL; note in the tool
     docstring that a developer key must be obtained directly from the NB Department of
     Transportation and Infrastructure. Do not block the phase on finding this — the Manitoba
     precedent explicitly ships stubs even when the key isn't freely obtainable (D-09).

2. **Exact curated-service shortlist for the "highest-value per sub-domain" (D-07) bar.**
   - What we know: All layer ids/fields for a ~20-service candidate shortlist across the four
     domains are resolved and documented above (Code Examples table).
   - What's unclear: Whether the planner wants exactly this set or a slightly different mix within
     the 11-15 curated tool budget (D-08: ~18-22 total tools).
   - Recommendation: Treat the Code Examples table as the menu; the planner selects the final
     11-15 curated tools from it (or adds 1-2 more via the same live-resolution methodology) during
     plan authoring.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Network access to `open.canada.ca` | CKAN discovery tools | ✓ (verified live during research) | — | — |
| Network access to `geonb.snb.ca` | GeoNB curated tools | ✓ (verified live during research) | ArcGIS Server 10.91 | — |
| Network access to `511.gnb.ca` | 511 transport stubs | ✓ (reachable, key-gated) | — | `NOT_CONFIGURED` stub (no key present) |
| `NEW_BRUNSWICK_511_KEY` env var | Live 511 integration tests | ✗ (not set in this environment) | — | Tests assert `NOT_CONFIGURED` envelope shape (same as Manitoba's pattern) rather than live 511 data |
| Python 3.14.6 / uv 0.11.32 / pytest 9.0.2 | Test execution | ✓ | matches CI matrix (3.12/3.13/3.14) | — |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:**
- `NEW_BRUNSWICK_511_KEY` — no key available in this environment; ship the `NOT_CONFIGURED` path
  and defer live 511 integration coverage until/unless a key is obtained (mirrors Manitoba MB-17).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 (via `uv run pytest`) |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -x` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

No REQ-IDs are assigned to this phase yet (ROADMAP.md carries `Requirements: TBD`; per CONTEXT.md,
ERR-01..ERR-07 apply to every new tool as a cross-cutting requirement). The table below maps this
phase's functional surface — to be assigned concrete REQ-IDs (`NB-01`, `NB-02`, ...) during
planning, following the Alberta/Manitoba/Saskatchewan/Nova Scotia precedent of backfilling
REQUIREMENTS.md immediately after planning.

| Capability | Behavior | Test Type | Automated Command | File Exists? |
|------------|----------|-----------|-------------------|-------------|
| CKAN search | `nb_search_datasets` returns NB-only results filtered by `organization:nb` | unit + integration | `pytest src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py -k search -x` | ❌ Wave 0 |
| CKAN dataset details | `nb_get_dataset_details` surfaces `title_translated`/`notes_translated` correctly for `lang="fr"` | unit | `pytest .../test_client.py -k bilingual -x` | ❌ Wave 0 |
| GeoNB service enumeration | `shared/arcgis_hub.py:list_arcgis_server_services` returns 62 services | unit (shared) | `pytest src/mcp_canada/shared/__tests__/test_arcgis_hub.py -k ArcgisServer -x` | ❌ Wave 0 |
| GeoNB curated query | Each curated tool queries its resolved (non-zero-assumed) layer id and returns non-empty features | integration (live, `assert_rows`) | `pytest tests/integration/test_tool_scenarios.py -k new_brunswick -m integration --timeout=120` | ❌ Wave 0 |
| 511 stub | `nb_get_road_events` returns `NOT_CONFIGURED` when `NEW_BRUNSWICK_511_KEY` absent | unit | `pytest .../test_tools.py -k not_configured -x` | ❌ Wave 0 |
| Error classification | Every `nb_` tool has catch-all coverage (ERR-01) and never raises a bare `ValueError` (ERR-06/07) | unit (structural, project-wide) | `pytest tests/test_tool_error_handling.py tests/test_error_classification_defaults.py -x` | ✅ (project-wide guard, already exists) |
| Malformed JSON | `decode_json`/`decode_json_bytes` used for every new decode site | unit (structural, project-wide) | `pytest tests/test_upstream_error_classification.py -x` | ✅ (project-wide guard, already exists) |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green (unit + structural guards) before `/gsd-verify-work`; live
  integration suite (`uv run pytest tests/integration/ -v -m integration --timeout=120`) run at
  least once before shipping, per the "Live-integration mandate" in CONTEXT.md.

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/conftest.py` — sample CKAN `package_search`
  fixture (NB-filtered), sample GeoNB `?f=json` service-directory fixture, sample MapServer layer
  `?f=json` fixture, sample GeoJSON feature-query fixture
- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`, `test_tools.py`,
  `test_prompts_resources.py` — do not exist yet (new module)
- [ ] `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` — add
  `TestListArcgisServerServices`/`TestGetArcgisServerLayers` classes for the two new functions,
  following the existing `TestSearchHubDatasets`/`TestQueryFeatureService` structure
- [ ] `tests/integration/test_tool_scenarios.py` — add NB scenarios per `.claude/rules/tests.md`
  (happy path, discovery, error handling, cross-module), using `assert_live_or_transient` +
  `assert_rows` — never a one-armed guard
- [ ] Framework install: none — `pytest`, `httpx`, `pydantic` already present

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Module has no auth of its own; 511 key is an upstream API credential, not user auth |
| V3 Session Management | No | Stateless MCP tool calls |
| V4 Access Control | No | Public open-data APIs, no access control layer in this module |
| V5 Input Validation | Yes | `lang: Literal["en","fr"]` enum validation (Pydantic/MCP layer rejects invalid values before the tool body runs, per Saskatchewan precedent); CKAN `fq`/`q` query strings passed through as opaque search terms (Solr handles escaping server-side, same as every prior CKAN-backed module); GeoNB `where` clauses use only project-controlled constants (`"1=1"` or literal field=value strings built by the tool, never raw user-supplied WHERE injection — same discipline as BC/Quebec WFS `_build_cql`) |
| V6 Cryptography | No | No credential storage beyond `os.environ.get(FIVE11_KEY_ENV)` — read-only env var access, never logged or echoed back in responses (mirrors Manitoba's `Five11NotConfigured` message, which never includes the key value) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| SQL/CQL injection via a `where=` or `fq=` parameter built from unsanitized agent input | Tampering | Never accept a raw WHERE/CQL string from the agent for curated tools — build `where` from typed, validated parameters server-side (mirrors BC's `_build_cql` upper-casing/allowlisting discipline); `nb_query_dataset`/`nb_query_features` (if a raw-query escape hatch is offered, as other provinces do) must document that ArcGIS's own SQL-92 WHERE parser is the trust boundary, same as every prior ArcGIS-backed province |
| Leaking the 511 API key in error messages or logs | Information Disclosure | `Five11NotConfigured`'s message must never include `os.environ.get(FIVE11_KEY_ENV)` — only state whether it is set; mirrors the Manitoba implementation exactly |
| Unbounded GeoNB query returning huge payloads (e.g., 604,520-record Parcels layer, 373,172-record Civic_Address layer) | Denial of Service (resource exhaustion for the agent's context window) | `arcgis_hub.query_feature_service`'s existing `MAX_RECORDS=5000` cap + `truncated` flag already handles this — curated tools over the largest layers (Parcels, Civic_Address, Wetlands) MUST require at least one filter parameter before allowing an unfiltered query, following BC's `bc_get_water_wells` 130K-record guard precedent (INVALID_INPUT before any network call when no filter provided) |

## Sources

### Primary (HIGH confidence)
- Live `curl` verification, 2026-07-30: `https://geonb.snb.ca/arcgis/rest/services?f=json` (62
  services enumerated)
- Live `curl` verification, 2026-07-30: `https://geonb.snb.ca/arcgis/rest/services/{service}/MapServer?f=json`
  for 26 candidate services (layer ids, names, field lists, record counts)
- Live `curl` verification, 2026-07-30: `https://open.canada.ca/data/api/3/action/package_search?fq=organization:nb`
  (221 datasets, `title_translated`/`notes_translated` shape confirmed on 5 sampled records)
- Live `curl` verification, 2026-07-30: `https://511.gnb.ca/api/v2/get/event` (HTTP 400, `Invalid
  Key` XML body)
- Live `curl` verification, 2026-07-30: `data.gnb.ca`, `opendata.gnb.ca`, `nbopendata.ca` (all
  unreachable — confirms CONTEXT.md dead ends)
- `src/mcp_canada/shared/arcgis_hub.py` (read in full) — existing `query_feature_service`,
  `get_layer_metadata`, `get_count`, `search_hub_datasets` implementations and docstrings
- `src/mcp_canada/modules/ckan/client.py` — existing `title_translated`/`notes_translated`
  fallback pattern (`_shape_dataset`)
- `src/mcp_canada/modules/manitoba/client.py` and `tools.py` — existing `Five11NotConfigured` /
  `NOT_CONFIGURED` stub pattern
- `src/mcp_canada/modules/alberta/client.py` — existing federal/provincial CKAN `fq`-composition
  pattern
- `src/mcp_canada/shared/errors.py`, `src/mcp_canada/shared/envelope.py` — error classification
  contract (`InvalidInput`/`NotFound`/`UpstreamData`, `make_response`/`make_error`)
- `.planning/phases/21-new-brunswick-government-open-data/21-CONTEXT.md` — locked decisions
  (D-01..D-12) from `/gsd-discuss-phase`

### Secondary (MEDIUM confidence)
- `.planning/STATE.md`, `.planning/REQUIREMENTS.md` — cross-referenced prior-phase precedents
  (Manitoba MB-17, Saskatchewan SK-11..14, Nova Scotia NS-01/06) for pattern reuse justification

### Tertiary (LOW confidence)
- None — every load-bearing claim in this document was verified live or against on-disk code
  during this research session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; every client function is a direct reuse of
  already-shipped, tested shared code
- Architecture: HIGH — service-directory shape, layer ids, and field names all confirmed via live
  `?f=json` calls against the actual GeoNB and federal CKAN endpoints during this session
- Pitfalls: HIGH — each pitfall (non-guessable layer ids, retired service, truncated field names,
  undomained coded fields, duplicate FR/EN CKAN records) was independently reproduced live, not
  inferred from documentation

**Research date:** 2026-07-30
**Valid until:** 2026-08-29 (30 days — GeoNB is a stable ArcGIS Server 10.91 instance and federal
CKAN's NB corpus changes incrementally; re-verify layer ids only if a specific curated service
returns unexpected results during implementation)
