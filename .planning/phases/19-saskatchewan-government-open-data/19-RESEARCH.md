# Phase 19: Saskatchewan Government Open Data — Research

**Researched:** 2026-06-15
**Domain:** Saskatchewan provincial open data (geohub.saskatchewan.ca ArcGIS Hub + org `zcv98lgAl8xQ04cW` + SPSA GIS FeatureServers + WSA ArcGIS Hub org `7MBdlVpjqbfBhQer`)
**Confidence:** HIGH for ArcGIS Hub architecture and curated FeatureServer URLs (live-verified); MEDIUM for Saskatchewan Highway Hotline 511 API (key-gated, structure confirmed); LOW for health facilities (no confirmed public FeatureServer beyond eHealth coverage stats)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Portal strategy:** Research determines the portal technology. The ship-minimal-vs-defer decision is the PLANNER's, made post-research on evidence. Research must probe live.
- **Ship path** — if research finds a usable surface (provincial CKAN/ArcGIS Hub/WFS, or federal `open.canada.ca` Saskatchewan-filtered catalogue), build a lean module.
- **Defer path** — if even the federal-filtered surface proves unworkable and curated domains are HTML-only, defer the phase.
- **No-scraping discipline holds** — HTML-only or PDF-only sources are deferred, never scraped.
- Module prefix `saskatchewan_`; module name `saskatchewan`.
- **Portal-technology routing:** CKAN → `shared/http.py api_get`, ArcGIS Hub → `shared/arcgis_hub.py`, OGC WFS → `shared/ogc.py`, files → `shared/parsers.fetch_and_parse()`.
- **ArcGIS Hub prerequisite warning:** If Saskatchewan is ArcGIS Hub, the latent `shared/arcgis_hub.py:search_hub_datasets` `startindex` param bug must be fixed first.
- **All four signature domains in scope:** Agriculture, Energy/mining, Highways/511 (conditional), Health + environment/water. Curate only what's machine-readable.
- **Lean ~10-14 tools:** ~5 discovery + ~5-9 curated.
- **Transport DEFERRED unless keyless clean feed** — no NOT_CONFIGURED stubs.
- **6 bilingual prompts** (3 guided + 3 quick lookups) + **~7 zero-parameter resources**.
- Bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`; inline `lang == 'fr'` ternary; no `shared/i18n.py:t()`.

### Claude's Discretion

- Final portal technology and ship-minimal-vs-defer decision (planner, post-research).
- Final dataset selection per domain — research surfaces the most agent-friendly options.
- Whether to reuse the federal `ckan` module's client vs. a new `_api_get` for federal-proxy path.
- Cache TTLs per tool; final prompt/resource set.

### Deferred Ideas (OUT OF SCOPE)

- Saskatoon, Regina, and other Saskatchewan municipal portals (separate future phases).
- Full defer of the phase (a live option if research finds even the federal-filtered surface unworkable).
- `shared/arcgis_hub.py` startindex fix as an independent concern (but becomes a PREREQUISITE for this phase — see below).
- Federal-catalogue-proxy as a reusable pattern for data-sparse provinces.
- Bilingual `shared/i18n.py:t()` adoption.
- SaskPower / login-gated sources.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

Proposed `SK-XX` requirements for Phase 19. Planner must add these to REQUIREMENTS.md.

| ID | Description | Research Support |
|----|-------------|-----------------|
| SK-01 | Agent can search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue by keyword with optional category filter and pagination | Hub Search API `/api/search/v1/collections/all/items` live-verified; 181 items; org `zcv98lgAl8xQ04cW` |
| SK-02 | Agent can get full details for a Saskatchewan GeoHub dataset by ID, including FeatureServer URL, download links, and metadata | ArcGIS Hub item detail endpoint; same pattern as Manitoba Phase 18 |
| SK-03 | Agent can query a Saskatchewan dataset via auto-router — ESRI FeatureServer → `arcgis_hub.query_feature_service`; CSV/JSON/GeoJSON/XLSX → `fetch_and_parse`; other → metadata-only | 17 Feature Services confirmed in main GeoHub; same hybrid router pattern as Alberta Phase 17 and Manitoba Phase 18 |
| SK-04 | Agent can list Saskatchewan government organizations and categories on the geoportal | ArcGIS Hub groups/categories endpoint; same pattern as Manitoba MB-04/MB-05 |
| SK-05 | Agent can list dataset categories on the Saskatchewan geoportal | Hub tags/categories endpoint |
| SK-06 | Agent can get estimated crop yields by crop type and region (provincial summary + 5 regions: Southeast, Southwest, Central, Northeast, Northwest) | `Provincial_Estimated_Crop_Yields_Province_Summary` and `Provincial_Estimated_Crop_Yields_Regions_Only` FeatureServers live-verified; 16 crop types (HRSW, Durum, Canola, Lentil, Pea, Chickpea, Oat, Barley, etc.) |
| SK-07 | Agent can get grain elevator locations for Saskatchewan (station, railway, licensee, capacity in tonnes) from Western Canada Grain Elevators dataset | `Western_Canada_Grain_Elevator_2024/FeatureServer/0` live-verified; SK filter supported via `where=PR='SK'`; 2024 dataset |
| SK-08 | Agent can get potash mine locations with company, status, mine type, and date opened from Saskatchewan mineral deposit index | `Potash_2024_06_13/FeatureServer/0` live-verified; Saskatchewan holds ~1/3 of world potash reserves |
| SK-09 | Agent can get uranium mine locations with company, status, mine type from Saskatchewan mineral deposit index | `Uranium_2024_06_13/FeatureServer/0` live-verified; Cameco Eagle Point / Athabasca Basin context |
| SK-10 | Agent can get current live ambient air quality readings (hourly) across Saskatchewan monitoring stations (PM2.5, NO2, O3, SO2, CO, H2S, AQHI link) | `Hourly_Ambient_Air_Quality/FeatureServer/0` live-verified; 2026-06-15 confirmed current data; 6 communities incl. Regina, Saskatoon, Prince Albert, Estevan, Swift Current, Buffalo Narrows |
| SK-11 | Agent can get current fire ban status by municipality/province from SPSA Public Fire Ban FeatureServer — dispatched by ban_scope: Literal["urban", "rural", "provincial", "parks"] | `gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer` live-verified; 4 layers (Urban=0, Rural=2, Provincial=3, Parks=8); confirmed live data 2026-06-15 |
| SK-12 | Agent can get historical wildfire boundaries for Saskatchewan by year/status/cause | `Historic_Wildfire_Boundaries/FeatureServer/0` and `Historic_Wildfire_Origins/FeatureServer/0` live-verified; fields: YEAR, FIRENAME, CAUSE1, HECTARES, STATUS, STARTDATE |
| SK-13 | Agent can get WSA hydrometric gauging station locations with major basin, station class, operated-by, and links to graphs/photos | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Hydrometric_Gauging_Stations_V2/FeatureServer` live-verified; Station_Number, Major_Basin, HyperLink_Graph, HyperLink_Photo fields |
| SK-14 | Agent can get WSA reservoir locations with names, dam names | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Reservoirs/FeatureServer/26` live-verified; Reservoir_Name, Dam_Name, Water_Level_MASL |
| SK-15 | All Saskatchewan tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, saskatchewan_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider | Conventions established by Phases 12-18 |

**Recommendation: SHIP.** Saskatchewan has a well-populated ArcGIS Hub (`geohub.saskatchewan.ca`, org `zcv98lgAl8xQ04cW`, 181 public items) with 17+ publicly accessible FeatureServers covering all four signature domains. The WSA hub (org `7MBdlVpjqbfBhQer`) adds water infrastructure. No federal-proxy fallback is needed — provincial data is rich enough.

**Tool count at planning time:** 5 discovery (SK-01 to SK-05) + 9 curated (SK-06 to SK-14) = 14 tools. Within the ~10-14 target.

**Transport deferred:** Saskatchewan Highway Hotline API (`hotline.gov.sk.ca/api/v2/get/`) returns `<Error><Message>Invalid Key</Message></Error>` for keyless requests — confirmed key-gated. Per CONTEXT.md locked decision, NO NOT_CONFIGURED stubs; transport domain is omitted from this phase.

</phase_requirements>

---

## Summary

### Critical Finding: Saskatchewan has a USABLE ArcGIS Hub — SHIP RECOMMENDED

Pre-planning reconnaissance got ECONNREFUSED on most Saskatchewan domains. Live research with full web access resolves the picture definitively:

1. **`data.saskatchewan.ca` does not exist as a public CKAN portal.** The domain is unreachable (same as Manitoba's `data.manitoba.ca`). Saskatchewan has no provincial CKAN.

2. **`geohub.saskatchewan.ca` is Saskatchewan's primary public machine-readable data portal** — an ArcGIS Hub powered by ArcGIS Online org `zcv98lgAl8xQ04cW`. It has 181 publicly accessible items including 17+ Feature Services. Live-verified with direct API probes.

3. **The WSA (Water Security Agency) operates a separate ArcGIS Hub** at `geohub-wsask.hub.arcgis.com` (org `7MBdlVpjqbfBhQer`) with 60 items and confirmed live hydrometric, reservoir, water quality, and watershed FeatureServers.

4. **Multiple ministry-specific ArcGIS Hubs exist** and all resolve to the same primary org `zcv98lgAl8xQ04cW`:
   - `moh-geohub-saskatchewan.hub.arcgis.com` — Ministry of Highways (40 items, road network FeatureServers)
   - `er-saskatchewan.hub.arcgis.com` — Energy and Resources / Saskatchewan Geological Survey (67 items, geology/mining FeatureServers)
   - `environment-saskatchewan.hub.arcgis.com` — Environment (124 items, forest/air/environment FeatureServers)

5. **SPSA wildfire data is on a separate ArcGIS server** at `gis.saskatchewan.ca/egis/rest/services/Wildfire/` — public and live-verified. `Public_Fire_Ban/FeatureServer` has 4 layers (Urban/Rural/Provincial/Parks ban status).

6. **Federal fallback is viable but unnecessary.** The `open.canada.ca` CKAN has 413 datasets from the `sk` (Government of Saskatchewan) organization. However, all confirmed datasets there are geospatial (ESRI REST / GeoJSON / SHP formats) pointing to the same `gis.saskatchewan.ca/egis/rest/services/Economy/` endpoint. The provincial ArcGIS Hub is richer and more convenient.

7. **Saskatchewan Highway Hotline API (`hotline.gov.sk.ca/api/v2/get/`) is key-gated.** Returns `<Error><Message>Invalid Key</Message></Error>` without a key. Per CONTEXT.md locked decision: transport domain is deferred entirely — no NOT_CONFIGURED stubs.

8. **Agriculture data is confirmed machine-readable.** `Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer` returns provincial crop yield estimates for 16 crop types (canola, HRSW, lentil, pea, chickpea, durum, barley, oat, etc.) by 5 regions. `Western_Canada_Grain_Elevator_2024/FeatureServer` provides grain elevator locations filterable by `PR='SK'`.

9. **Energy/mining data is rich.** `Potash_2024_06_13`, `Uranium_2024_06_13`, `Helium_2024_12_31`, `Coal_2024_06_13` are all live FeatureServers with mine name, company, status, type. `gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer` has 21 layers (Vertical Wells, Facilities, Potash Restricted Drilling, Pool Land, etc.) — but queries return HTTP 400. The Petroleum endpoint requires a specific query structure.

10. **Health domain is thin.** No public hospital/facility FeatureServer was found. `eHealth_Coverage_by_Sex` and `eHealth_Coverage_By_Region_and_Community` are aggregate coverage stats (population enrolled in provincial eHealth by year/sex/region), not facility location data. Saskatchewan Health Authority does not appear to have a public-facing FeatureServer in the `zcv98lgAl8xQ04cW` org.

11. **Air quality is confirmed live.** `Hourly_Ambient_Air_Quality/FeatureServer` with `AQHI`, `PM2_5`, `NO2`, `O3`, `SO2`, `CO`, `H2S` fields for 6 communities was live and returning current data on 2026-06-15.

**Primary recommendation:** SHIP. Build 5 discovery tools + 9 curated tools = 14 total (within the ~10-14 target). Agriculture (2), Energy/mining (2), Environment/wildfire (2), Water (2), and Air quality (1) as curated domains. Health is thin — substitute with air quality. Transport deferred per CONTEXT.md.

**Prerequisite:** `shared/arcgis_hub.py:search_hub_datasets` uses `params["offset"] = offset` but Saskatchewan GeoHub (like Manitoba's) uses `startindex`, not `offset`. Confirmed: `?offset=3` returns `{numberMatched: null, numberReturned: null}` while `?startindex=3` returns correct pagination. This bug MUST be fixed before discovery tools will paginate correctly. Plan a Wave 0 task to fix `shared/arcgis_hub.py` (change `offset` → `startindex` in `search_hub_datasets`).

---

## Portal Architecture Discovery

### What Saskatchewan Actually Has (confirmed)

| Portal | URL | Technology | Auth | Items | Status |
|--------|-----|-----------|------|-------|--------|
| **Saskatchewan GeoHub (primary)** | `geohub.saskatchewan.ca` | ArcGIS Hub (Esri) | None | 181 | ACTIVE — 17+ FeatureServer services |
| WSA GeoHub | `geohub-wsask.hub.arcgis.com` | ArcGIS Hub (Esri) | None | 60 | ACTIVE — 12+ FeatureServer services |
| MoH GeoHub | `moh-geohub-saskatchewan.hub.arcgis.com` | ArcGIS Hub (Esri) | None | 40 | Highways-focused (same org as main GeoHub) |
| Environment Hub | `environment-saskatchewan.hub.arcgis.com` | ArcGIS Hub (Esri) | None | 124 | Air quality, forest, environment |
| ER/Geology Hub | `er-saskatchewan.hub.arcgis.com` | ArcGIS Hub (Esri) | None | 67 | Energy/Resources, Geological Survey |
| SPSA Wildfire GIS | `gis.saskatchewan.ca/egis/rest/services/Wildfire/` | ArcGIS REST (non-Hub) | None | 4 layers | ACTIVE — fire ban + fire boundaries |
| data.saskatchewan.ca | — | Unknown | — | — | UNREACHABLE / does not exist |
| Highway Hotline | `hotline.gov.sk.ca/api/v2/get/` | Custom REST API | **Key required** | 8+ endpoints | KEY GATED — `<Error>Invalid Key</Error>` |
| Federal CKAN | `open.canada.ca` (org: `sk`) | CKAN | None | 413 | All geospatial ESRI REST datasets |
| Old GeoHub | `geohub-old-saskatchewan.opendata.arcgis.com/` | ArcGIS Hub (legacy) | None | — | Superseded — redirect to main GeoHub |

### Saskatchewan ArcGIS Organizations

| Org ID | Base Services URL | Hub URL | Description |
|--------|------------------|---------|-------------|
| `zcv98lgAl8xQ04cW` | `https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/` | `geohub.saskatchewan.ca` | Saskatchewan Government primary (Ministry of Highways, Environment, Energy/Resources, Agriculture, Health) |
| `7MBdlVpjqbfBhQer` | `https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/` | `geohub-wsask.hub.arcgis.com` | Water Security Agency (WSA) — hydrometric, reservoirs, water quality, watershed, dams |

**NOTE on multi-hub architecture:** Saskatchewan uses a hub-per-ministry pattern where individual ministry-branded hubs (MoH, ER, Environment) point at items within the same primary `zcv98lgAl8xQ04cW` org. `geohub.saskatchewan.ca` is the canonical discovery entry point covering all ministries. The WSA is the only separate org.

### SPSA Non-Hub GIS Services (Wildfire)

The Saskatchewan Public Safety Agency (SPSA) maintains a separate ArcGIS REST server at `gis.saskatchewan.ca/egis/rest/services/Wildfire/` that is NOT part of the Hub. It requires direct `services/Wildfire/Public_Fire_Ban/FeatureServer` calls (not discovered via Hub Search). This is confirmed public and live.

### Discovery Tool Pattern (5 standard tools, ArcGIS Hub pattern)

```
saskatchewan_search_datasets     → Hub Search API /api/search/v1/collections/all/items (geohub.saskatchewan.ca)
saskatchewan_get_dataset_details → Hub item detail endpoint
saskatchewan_query_dataset       → arcgis_hub.query_feature_service (or fetch_and_parse for file resources)
saskatchewan_list_organizations  → Hub categories/orgs endpoint
saskatchewan_list_categories     → Hub tags endpoint
```

---

## Standard Stack

### Core (no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp` | 3.2.x | MCP server framework | Project standard |
| `httpx` | 0.28.x | Async HTTP | Shared infrastructure |
| `pydantic` | v2 | Flat schemas | Project standard |
| `aiocache` | latest | TTL caching via `cached_fetch` | Project standard |
| `tenacity` | latest | Retry in `shared/http.api_get` | Project standard |

### Supporting (all existing shared infra)

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `shared/arcgis_hub.py:query_feature_service` | All ArcGIS Hub FeatureServer queries | All curated tools (crop yields, minerals, wildfire, air quality, water) |
| `shared/arcgis_hub.py:search_hub_datasets` | Hub Search API discovery (AFTER startindex fix) | Discovery tools |
| `shared/arcgis_hub.py:get_layer_metadata` | Detect maxRecordCount before paginating | Once per layer (cached 24h) |
| `shared/parsers.py:fetch_and_parse` | File resources returned by `query_dataset` | Auto-router fallback (CSV/GeoJSON/XLSX) |
| `shared/http.py:api_get` | Direct REST calls where needed | SPSA fire ban (separate REST server) |
| `shared/cache.py:cached_fetch` | TTL caching | Every client function |
| `shared/rate_limiter.py:get_limiter` | Token bucket per source | Every client function |
| `shared/envelope.py` | `make_response` / `make_error` | Every tool function |

### No New Dependencies

The existing stack covers every Saskatchewan surface. `shared/arcgis_hub.py` is already proven (Phase 14 York Region, Phase 17 Alberta, Phase 18 Manitoba). The SPSA REST server uses standard `api_get`.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ArcGIS Hub pattern | CKAN (federal proxy) | NOT needed — provincial Hub is richer; 413 federal datasets are already in Hub format anyway |
| `shared/arcgis_hub.py` | New `shared/saskatchewanGIS.py` | Premature — same protocol, same client works unchanged after startindex fix |
| Separate WSA discovery tools | Merging WSA into main discovery | WSA's org `7MBdlVpjqbfBhQer` is separate; curated WSA tools call its FeatureServers directly without Hub search |

### Installation

No new packages required. All dependencies already present.

---

## Domain Analysis (4 domains, honest assessment)

### Domain 1: Agriculture (signature)

**Verdict: CURATE 2 tools — confirmed machine-readable via ArcGIS Hub FeatureServers.**

Saskatchewan is Canada's breadbasket: #1 in canola, durum wheat, lentils, chickpeas. Weekly crop reports are PDF-only (confirmed at `saskatchewan.ca/business/agriculture.../crops-statistics/`) — do not plan a PDF-reading crop report tool. Machine-readable agricultural data comes through the Hub.

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Estimated Crop Yields — Province Summary** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer/0` | Region, HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean, Pea, Lentil, Chickpea, Canary_seed, Flax, Winter_wheat, Fall_rye, Other_wheat_ | Yields in bu/acre by province + 5 crop reporting regions (Southeast/Southwest/Central/Northeast/Northwest). Live-verified: 2 records (Provincial + each region). |
| **Estimated Crop Yields — Regions Only** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer/0` | Region, [same 16 crops] | Regional breakdown only (no provincial summary row). Same 16 crop fields. |
| **Western Canada Grain Elevators 2024** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Western_Canada_Grain_Elevator_2024/FeatureServer/0` | OBJECTID, Station, PR, Railway, Licensee, Elevator_type, Capacity_tonne | SK elevators only via `where=PR='SK'`; CN/CP railway, primary/process elevator types. Live-verified. |

**Recommended tools:**
- `saskatchewan_get_crop_yields` — Province Summary + Regions dispatch by `region: str | None = None`. Returns 16 crop type estimates.
- `saskatchewan_get_grain_elevators` — `Western_Canada_Grain_Elevator_2024` with default `where=PR='SK'`; optional `railway=` filter.

**NOT CURATE:** Saskatchewan Crop Insurance (SCIC) — `scic.ca` offers calculators and maps but no machine-readable API was found. Crop Production 2025 FeatureServer exists (`Crop_Production_2025/FeatureServer/0`) but has only Census Division boundary geometry and no crop data attributes (CDNAME, LANDAREAIN, Census_Div — just spatial boundaries).

### Domain 2: Energy / Mining

**Verdict: CURATE 2 tools — potash and uranium mines are confirmed live FeatureServers.**

Saskatchewan has 13 active potash mines (world's largest reserve), 3 uranium operations (Athabasca Basin), and producing oil & gas wells.

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Potash Mines** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Potash_2024_06_13/FeatureServer/0` | Commodity, Name, Status, Mine_Type, Company, Contact_In, Mine_Site, Regulation, UTM_Eastin, UTM_Northi, DateOpened, Website, TechDetails | Live-verified. K+S Bethune (solution mine) confirmed in sample. Dated 2024-06-13. |
| **Uranium Mines** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Uranium_2024_06_13/FeatureServer/0` | [same schema as Potash] | Live-verified. Cameco Eagle Point (care & maintenance) confirmed in sample. Dated 2024-06-13. |
| **Mineral Deposits Index** | `gis.saskatchewan.ca/egis/rest/services/Economy/Mineral_Exploration/FeatureServer/2` | Full mineral deposit registry | Live reference; reachable via hub GeoJSON export. For discovery; too broad for curated tool. |
| **Oil & Gas Wells (Petroleum)** | `gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0` | WELL_CWI, LEGACYWELLNAME, WELLLICENCENUMBER, WELLSTATUS, WELLLICENCEBUSINESSASSOCIATE, WELLLICENCEISSUEDATE | Returns HTTP 400 on open queries — schema confirmed via layer endpoint but data queries fail. NOT CURATE for now. |

**Recommended tools:**
- `saskatchewan_get_mineral_mines` — dispatch by `mineral: Literal["potash", "uranium", "helium", "coal"]`; routes to dated FeatureServers. Helium (`Helium_2024_12_31`) and Coal (`Coal_2024_06_13`) also confirmed; could be folded in as additional `mineral` values.
- OR split into `saskatchewan_get_potash_mines` + `saskatchewan_get_uranium_mines` + optional general `mineral` tool.

**Recommendation:** Single parametrized `saskatchewan_get_mineral_mines(mineral: Literal["potash","uranium","helium","coal"])` — one tool, four minerals, same schema. Reduces tool count while covering Saskatchewan's signature mining industries.

**Oil & gas wells (Petroleum FeatureServer layer 0) is NOT curated** — live queries return HTTP 400. Document as discovery-only via `saskatchewan_search_datasets` with query "petroleum wells".

### Domain 3: Transport / 511

**Verdict: DEFER ENTIRELY — key-gated. Per CONTEXT.md: no NOT_CONFIGURED stubs.**

Saskatchewan Highway Hotline API (`hotline.gov.sk.ca/api/v2/get/`) is documented at `hotline.gov.sk.ca/developers/doc` and has a v2 REST JSON API with endpoints: `roadconditions`, `cameras`, `events`, `winterroads`, `ferryterminals`, `iceroadsegments`, `events`, `advisories`, `trackmyplow`. Rate limit: 10 calls per 60 seconds.

**Authentication:** The API returns `<Error><Message>Invalid Key</Message></Error>` for all keyless requests (HTTP 400). Key registration appears to require a developer account but the signup page URL was not confirmed as freely accessible to the public (the developer page itself returned 404 during research). This is analogous to Manitoba 511 — but CONTEXT.md for Saskatchewan is MORE conservative: "Defer transport tools UNLESS research finds a clean, keyless JSON/API feed. Do NOT ship NOT_CONFIGURED stub tools."

**Decision:** Transport domain is fully deferred. The Highway Hotline is key-gated. Do not plan any transport tools. The HIGHWAY_OFFICIAL and ROADSEG FeatureServers (static road geometry, not live conditions) are discoverable via the Hub discovery tools.

### Domain 4: Health + Environment / Water

**Verdict: Environment (CURATE 3 tools) — Health (DEFER, no public facility FeatureServer found).**

#### Health Assessment

No public Saskatchewan Health Authority (SHA) facility FeatureServer was found in any searched org. The `zcv98lgAl8xQ04cW` org has:
- `eHealth_Coverage_by_Sex/FeatureServer` — provincial eHealth enrollment count by year/sex (Year: 2008..., Male: 515786, Female: 519758) — NOT facility locations
- `eHealth_Coverage_By_Region_and_Community/FeatureServer` — eHealth coverage by community — potentially useful as a coverage map but not hospital/clinic locations
- `Partner_Services_(View)/FeatureServer` — research partner directory (universities, companies) — not health facilities

The `moh-geohub-saskatchewan.hub.arcgis.com` (Ministry of Highways, named confusingly as "MoH" by Esri slug but = Ministry of Highways) has only road network data, confirming the MoH slug stands for "Ministry of Highways" not "Ministry of Health".

**Health domain deferred.** There is no confirmed public machine-readable SHA facility/wait time data surface. Do not pad with `eHealth_Coverage_by_Sex` (no agent value for basic enrollment counts without facilities). Note for future phases: SHA may have facility data in a restricted ArcGIS org.

#### Environment / Wildfire (confirmed)

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Current Fire Bans** | `gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer` | UMTYPE, Municipali, Fire_Depar, Start_Date, Contact_Nu, Type, Comment | Layers: 0=Urban, 2=Rural, 3=Provincial, 8=Parks. Live-verified with active bans on 2026-06-15. |
| **Historic Wildfire Boundaries** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Historic_Wildfire_Boundaries/FeatureServer/0` | OBJECTID, PROJECT, YEAR, FIRENAME, CAPTURE_DA, SOURCE, ACRES, HECTARES, STATUS, CAUSE1, STARTDATE, OUTDATE, TYPE | Live-verified. 2017 fires confirmed. Filter by YEAR. |
| **Historic Wildfire Origins (Points)** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Historic_Wildfire_Origins/FeatureServer/0` | OBJECTID, PROJECTNUM, FIRENUMBER, FIRENAME, STATUS, LATITUDE, LONGITUDE, HECTARES, CAUSE1, CAUSE2, STARTDATE, OUTDATE, VALUEBURNT, TYPE, YEAR | Live-verified. Point data for all historic fires. |
| **Hourly Ambient Air Quality** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Hourly_Ambient_Air_Quality/FeatureServer/0` | OBJECTID, COMMUNITY, STATIONID, PM2_5, NO2, O3, PM10, SO2, CO, NO, NOX, H2S, BLACKCARBON, WD, WS, TEMP, RH, BP, AQHI, RAWDATA, QAQC, DATETIME | Live-verified with current 2026-06-15 data. 6 communities. AQHI links to weather.gc.ca. |

**Recommended tools:**
- `saskatchewan_get_fire_bans` — `Public_Fire_Ban/FeatureServer`; dispatch by `ban_scope: Literal["urban","rural","provincial","parks"]` → layer 0/2/3/8
- `saskatchewan_get_historic_wildfires` — `Historic_Wildfire_Boundaries/FeatureServer/0`; optional `year=` filter; optional `cause=` filter (Lightning/Human/etc.)
- `saskatchewan_get_air_quality` — `Hourly_Ambient_Air_Quality/FeatureServer/0`; optional `community=` filter; live current readings

#### Water (WSA — confirmed)

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Hydrometric Gauging Stations** | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Hydrometric_Gauging_Stations_V2/FeatureServer/0` | Station_Number, Station_Name, Province, Latitude, Longitude, Year_From, Operated_By, Major_Basin, GROSS_AREA__km_2_, Station_Type, Station_Class, HyperLink_Photo, HyperLink_Graph | Live-verified. SK=Saskatchewan filter on Province. Links to `wsask.ca/hydrographs/{num}-hrly.html`. |
| **WSA Reservoirs** | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Reservoirs/FeatureServer/26` | OBJECTID, Reservoir_Name, Dam_Name, Imagery_Date, Imagery_Comment, Water_Level_MASL | Live-verified. Layer 26 (not 0). 2000+ reservoir records expected. |
| **WSA Owned Dams** | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Owned_Dams/FeatureServer` | Dam details | Confirmed in WSA Hub search |
| **Primary Water Quality Monitoring Stations** | `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Primary_Water_Quality_Monitoring_Stations/FeatureServer/19` | Station_Number, Station_Name, Comment, Station_Description, Latitide, LONGITUDE | Live-verified. Layer 19 (not 0). MOE PRIMARY stations for water quality monitoring. |
| **Long Term Water Chemistry** | `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/LongTermWaterChemistry/FeatureServer/0` | 90+ parameters: Alkalinity, pH, heavy metals, BOD, Dissolved Oxygen, Turbidity, etc. | Live-verified. Historical lake/river chemistry with coordinates. Very wide schema — recommend projected field list. |

**Recommended tools:**
- `saskatchewan_get_wsa_stations` — `Hydrometric_Gauging_Stations_V2/FeatureServer/0` with `where=Province='SK'`; optional `basin=` filter; returns HyperLink_Graph URL for live readings
- `saskatchewan_get_wsa_reservoirs` — `WSA_Reservoirs/FeatureServer/26`; returns Reservoir_Name, Dam_Name, Water_Level_MASL

---

## Curated Tool Catalog (Research-recommended, 9 curated tools)

### Discovery (5 tools — ArcGIS Hub pattern)

| Tool | Backend | Cache TTL | Notes |
|------|---------|-----------|-------|
| `saskatchewan_search_datasets` | ArcGIS Hub Search `/api/search/v1/collections/all/items` | 1h | q=, limit=, offset= (maps to startindex in Hub API — AFTER shared fix) |
| `saskatchewan_get_dataset_details` | ArcGIS Hub item detail | 24h | Returns FeatureServer URLs, download links, metadata |
| `saskatchewan_query_dataset` | Hybrid router: ArcGIS FeatureServer or `fetch_and_parse` | 24h file / 5min live | Same pattern as `alberta_query_dataset` / `manitoba_query_dataset` |
| `saskatchewan_list_organizations` | ArcGIS Hub categories/orgs | 24h | Saskatchewan government publishing orgs |
| `saskatchewan_list_categories` | ArcGIS Hub tags/categories | 24h | Data categories/themes |

### Agriculture (2 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `saskatchewan_get_crop_yields` | `Provincial_Estimated_Crop_Yields_Province_Summary` or `Regions_Only/FeatureServer/0` | 7d (annual data) | `region: str = "provincial"` dispatch; "provincial" = summary, "southeast/southwest/central/northeast/northwest" = regional |
| `saskatchewan_get_grain_elevators` | `Western_Canada_Grain_Elevator_2024/FeatureServer/0` | 24h | Default `where=PR='SK'`; optional `railway: Literal["CN","CP","SHORTLINE"]` filter |

### Energy / Mining (1 tool)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `saskatchewan_get_mineral_mines` | `Potash_2024_06_13`, `Uranium_2024_06_13`, `Helium_2024_12_31`, `Coal_2024_06_13` FeatureServer/0 | 24h | `mineral: Literal["potash","uranium","helium","coal"]`; routes to respective dated service; returns Name, Status, Mine_Type, Company, DateOpened |

### Environment / Wildfire (3 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `saskatchewan_get_fire_bans` | `gis.sk.ca/egis/services/Wildfire/Public_Fire_Ban/FeatureServer` | 5min | `ban_scope: Literal["urban","rural","provincial","parks"]` → layers 0/2/3/8; **different base server than Hub** |
| `saskatchewan_get_historic_wildfires` | `Historic_Wildfire_Boundaries/FeatureServer/0` | 24h | Optional `year: int`, `cause: str` (Lightning/Human/Unknown) filters |
| `saskatchewan_get_air_quality` | `Hourly_Ambient_Air_Quality/FeatureServer/0` | 15min | Optional `community: str` filter (Regina/Saskatoon/Prince Albert/Estevan/Swift Current/Buffalo Narrows); includes AQHI link |

### Water — WSA (2 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `saskatchewan_get_wsa_stations` | `Hydrometric_Gauging_Stations_V2/FeatureServer/0` (WSA org) | 24h | `where=Province='SK'` default; optional `basin=` filter; includes HyperLink_Graph URLs |
| `saskatchewan_get_wsa_reservoirs` | `WSA_Reservoirs/FeatureServer/26` (WSA org) | 24h | Layer 26 (not 0); Reservoir_Name, Dam_Name, Water_Level_MASL |

**Total: 14 tools (5 discovery + 9 curated). Within the ~10-14 CONTEXT.md target.**

### Domain Density vs CONTEXT.md Targets

| Domain | CONTEXT.md target | Research-recommended | Delta |
|--------|-------------------|----------------------|-------|
| Agriculture (signature) | Highest priority | 2 (crop yields + grain elevators) | On target |
| Energy / mining | Curate if exposed | 1 (mineral mines dispatch, 4 minerals) | Compact but covers all 4 minerals |
| Highways / 511 | Conditional | **0 (DEFER — key-gated)** | Expected per locked decision |
| Health | Parity with other provinces | **0 (DEFER — no public FeatureServer)** | Below target; substitute with air quality |
| Environment / water | Parity | 5 (fire bans + wildfires + air quality + WSA stations + WSA reservoirs) | Above initial target; rich domain |
| **Curated Total** | **~5-9** | **9** | At target ceiling |
| Discovery | 5 | 5 | On target |
| **Grand Total** | **~10-14** | **14** | At target ceiling |

---

## Architecture Patterns

### Recommended Module Structure

```
src/mcp_canada/modules/saskatchewan/
├── __init__.py           # MODULE_NAME = "saskatchewan", MODULE_DESCRIPTION (en+fr)
├── constants.py          # BASE_URL (GeoHub), RATE_GROUPs, CACHE_TTLs, FeatureServer URLs
├── schemas.py            # Flat Pydantic v2 models
├── client.py             # ~14 async functions returning (data, was_cached) tuples
├── tools.py              # 14 @tool functions (5 discovery + 9 curated)
├── prompts.py            # 6 bilingual @prompt functions
├── resources.py          # 7 zero-parameter @resource functions
└── __tests__/
    ├── __init__.py
    ├── conftest.py        # Sample ArcGIS Hub JSON fixtures + FeatureServer fixtures
    ├── test_client.py     # Client unit tests + TestSharedApiGetContract
    ├── test_tools.py      # Tool unit tests (mocked client layer)
    └── test_prompts_resources.py
```

### Pattern 1: Constants for Multi-Org ArcGIS Setup

```python
# src/mcp_canada/modules/saskatchewan/constants.py
from typing import Final

# ---------------------------------------------------------------------------
# Saskatchewan GeoHub (primary org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
HUB_BASE_URL: Final[str] = "https://geohub.saskatchewan.ca"
ARCGIS_ORG_ID: Final[str] = "zcv98lgAl8xQ04cW"
HUB_ORG_BASE: Final[str] = f"https://services3.arcgis.com/{ARCGIS_ORG_ID}/arcgis/rest/services"
RATE_GROUP_HUB: Final[str] = "saskatchewan_hub"
RATE_LIMIT_HUB: Final[float] = 10.0

# ---------------------------------------------------------------------------
# SPSA Wildfire GIS (separate REST server — NOT ArcGIS Hub)
# ---------------------------------------------------------------------------
SPSA_BASE_URL: Final[str] = "https://gis.saskatchewan.ca/egis/rest/services/Wildfire"
FIRE_BAN_FS_URL: Final[str] = f"{SPSA_BASE_URL}/Public_Fire_Ban/FeatureServer"
FIRE_BAN_LAYERS: Final[dict[str, int]] = {
    "urban": 0,
    "rural": 2,
    "provincial": 3,
    "parks": 8,
}
RATE_GROUP_SPSA: Final[str] = "saskatchewan_spsa"
RATE_LIMIT_SPSA: Final[float] = 5.0

# ---------------------------------------------------------------------------
# WSA GeoHub (org: 7MBdlVpjqbfBhQer)
# ---------------------------------------------------------------------------
WSA_ORG_ID: Final[str] = "7MBdlVpjqbfBhQer"
WSA_ORG_BASE: Final[str] = f"https://services1.arcgis.com/{WSA_ORG_ID}/arcgis/rest/services"
RATE_GROUP_WSA: Final[str] = "saskatchewan_wsa"
RATE_LIMIT_WSA: Final[float] = 5.0

# ---------------------------------------------------------------------------
# Agriculture FeatureServers (org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
CROP_YIELDS_PROVINCE_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer"
CROP_YIELDS_REGIONS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer"
GRAIN_ELEVATORS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Western_Canada_Grain_Elevator_2024/FeatureServer"

# ---------------------------------------------------------------------------
# Energy / Mining FeatureServers (org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
MINERAL_MINES_FS_URLS: Final[dict[str, str]] = {
    "potash": f"{HUB_ORG_BASE}/Potash_2024_06_13/FeatureServer",
    "uranium": f"{HUB_ORG_BASE}/Uranium_2024_06_13/FeatureServer",
    "helium": f"{HUB_ORG_BASE}/Helium_2024_12_31/FeatureServer",
    "coal": f"{HUB_ORG_BASE}/Coal_2024_06_13/FeatureServer",
}

# ---------------------------------------------------------------------------
# Environment / Wildfire FeatureServers (org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
WILDFIRE_BOUNDARIES_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Historic_Wildfire_Boundaries/FeatureServer"
WILDFIRE_ORIGINS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Historic_Wildfire_Origins/FeatureServer"
AIR_QUALITY_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Hourly_Ambient_Air_Quality/FeatureServer"
AIR_QUALITY_COMMUNITIES: Final[list[str]] = [
    "Regina", "Saskatoon", "Prince Albert", "Estevan", "Swift Current", "Buffalo Narrows"
]

# ---------------------------------------------------------------------------
# WSA Water Infrastructure FeatureServers (org: 7MBdlVpjqbfBhQer)
# ---------------------------------------------------------------------------
WSA_STATIONS_FS_URL: Final[str] = f"{WSA_ORG_BASE}/Hydrometric_Gauging_Stations_V2/FeatureServer"
WSA_RESERVOIRS_FS_URL: Final[str] = f"{WSA_ORG_BASE}/WSA_Reservoirs/FeatureServer"
WSA_RESERVOIRS_LAYER: Final[int] = 26  # NOT layer 0 — live-verified
WSA_STATIONS_LAYER: Final[int] = 0

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 900       # 15min — air quality
CACHE_TTL_ALERTS: Final[int] = 300     # 5min — fire bans (live emergency data)
CACHE_TTL_SEARCH: Final[int] = 3600    # 1h — hub search
CACHE_TTL_META: Final[int] = 86400     # 24h — grain elevators, minerals, WSA
CACHE_TTL_ANNUAL: Final[int] = 604800  # 7d — crop yields (annual)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000
```

### Pattern 2: Hub Discovery Helper (with startindex — post-fix)

```python
# src/mcp_canada/modules/saskatchewan/client.py
# Uses shared/arcgis_hub.py AFTER the startindex bug is fixed.
# The fix changes params["offset"] → params["startindex"] in search_hub_datasets.

async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict, bool]:
    cache_key = f"saskatchewan:hub:search:{query}:{limit}:{offset}"
    limiter = get_limiter(RATE_GROUP_HUB, rate=RATE_LIMIT_HUB)

    async def fetcher():
        await limiter.acquire()
        return await arcgis_hub.search_hub_datasets(
            HUB_BASE_URL,
            query=query,
            limit=limit,
            offset=offset,   # maps to startindex internally after fix
        )

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)
```

### Pattern 3: Curated FeatureServer Client Functions (two-org pattern)

```python
# Saskatchewan has TWO ArcGIS orgs — the curated tools must use the correct org URL

async def fetch_fire_bans(
    ban_scope: str = "urban",
    max_records: int = MAX_RECORDS,
) -> tuple[dict, bool]:
    """Fetch current fire bans from SPSA (NOT ArcGIS Hub org — separate server)."""
    layer_id = FIRE_BAN_LAYERS.get(ban_scope, 0)
    cache_key = f"saskatchewan:fireban:{ban_scope}"
    limiter = get_limiter(RATE_GROUP_SPSA, rate=RATE_LIMIT_SPSA)

    async def fetcher():
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            FIRE_BAN_FS_URL,
            layer_id=layer_id,
            where="1=1",
            out_fields="UMTYPE,Municipali,Fire_Depar,Start_Date,Contact_Nu,Type,Comment",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "scope": ban_scope}

    return await cached_fetch(cache_key, CACHE_TTL_ALERTS, fetcher)


async def fetch_wsa_stations(
    basin: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict, bool]:
    """Fetch WSA hydrometric stations — uses WSA org (7MBdlVpjqbfBhQer), NOT primary org."""
    where = "Province='SK'"
    if basin:
        where += f" AND Major_Basin LIKE '%{basin}%'"
    cache_key = f"saskatchewan:wsa:stations:{basin or 'all'}"
    limiter = get_limiter(RATE_GROUP_WSA, rate=RATE_LIMIT_WSA)

    async def fetcher():
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            WSA_STATIONS_FS_URL,
            layer_id=WSA_STATIONS_LAYER,
            where=where,
            out_fields="Station_Number,Station_Name,Province,Latitude,Longitude,Major_Basin,Station_Type,Station_Class,Operated_By,HyperLink_Graph",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "count": len(features)}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
```

### Pattern 4: Mineral Mines Dispatch

```python
async def fetch_mineral_mines(
    mineral: str,
    max_records: int = MAX_RECORDS,
) -> tuple[dict, bool]:
    """Dispatch to correct dated FeatureServer by mineral type."""
    fs_url = MINERAL_MINES_FS_URLS.get(mineral.lower())
    if fs_url is None:
        raise ValueError(f"Unknown mineral: {mineral}. Valid: {list(MINERAL_MINES_FS_URLS)}")
    cache_key = f"saskatchewan:mines:{mineral.lower()}"
    limiter = get_limiter(RATE_GROUP_HUB, rate=RATE_LIMIT_HUB)

    async def fetcher():
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            fs_url,
            layer_id=0,
            where="1=1",
            out_fields="Commodity,Name,Status,Mine_Type,Company,Mine_Site,Regulation,DateOpened,Website",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "mineral": mineral}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
```

### Anti-Patterns to Avoid

- **NEVER call `data.saskatchewan.ca`** — domain does not exist; Saskatchewan has no CKAN portal.
- **NEVER use `params["offset"]` in Hub Search for Saskatchewan** — the Hub uses OGC API Records with `startindex`, not `offset`. Confirmed: `?offset=3` returns `{numberMatched: null}` while `?startindex=3` works. This must be fixed in `shared/arcgis_hub.py` before discovery tools will paginate.
- **NEVER use layer 0 for WSA Reservoirs** — layer is at index 26 (`WSA_Reservoirs/FeatureServer/26`), not 0. Queries to layer 0 return empty.
- **NEVER use layer 0 for WSA Primary Water Quality Monitoring Stations** — layer is at index 19.
- **NEVER call `gis.saskatchewan.ca/arcgis/rest/services/` (no `/egis/`)** — the public endpoint is `gis.saskatchewan.ca/egis/rest/services/`. The non-egis path returns 499 Token Required.
- **NEVER scrape hotline.gov.sk.ca** — Highway Hotline data requires a developer API key. Key-gated: `<Error>Invalid Key</Error>`. No NOT_CONFIGURED stubs per locked decision.
- **NEVER assume Petroleum FeatureServer layer 0 returns open data** — queries to `gis.sk.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0` return HTTP 400. Well data may require authentication or specific query structure. Do not plan a curated oil/gas wells tool.
- **NEVER call `.raise_for_status()` or `.json()` on `shared/http.py:api_get` return** — `api_get` returns parsed JSON dict, not an httpx.Response. (Phase 15 root-cause pitfall.)
- **NEVER use `@mcp.tool`** — use standalone `@tool` from `fastmcp.tools`. (FileSystemProvider requires standalone decorators.)

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ArcGIS FeatureServer pagination | Custom page loop | `shared/arcgis_hub.py:query_feature_service` | Already handles `exceededTransferLimit` to 5000-record cap |
| Hub Search API | Custom HTTP client | `shared/arcgis_hub.py:search_hub_datasets` (after startindex fix) | Phase 14 pattern proven |
| File resource parsing | Custom CSV/GeoJSON parser | `shared/parsers.py:fetch_and_parse` | Handles CSV/XLSX/GeoJSON/Shapefile |
| Cache / rate limiting | Per-tool custom logic | `cached_fetch` + `get_limiter` | All modules use this |
| Response envelope | Per-tool JSON schema | `make_response` / `make_error` | Every tool must use this |
| Crop data scraping | HTML/PDF parser | None — FeatureServer has yield estimates | Weekly PDF reports are HTML-only; the `Provincial_Estimated_Crop_Yields` FS is the machine-readable substitute |

**Key insight:** Two ArcGIS orgs (`zcv98lgAl8xQ04cW` and `7MBdlVpjqbfBhQer`) plus one separate SPSA server mean Saskatchewan has the most fragmented portal architecture of any province researched so far. Use `constants.py` as the single source of truth for all service URLs — the planner must never let a FeatureServer URL slip into tool code directly.

---

## Common Pitfalls

### Pitfall 1: The startindex / offset pagination bug in shared/arcgis_hub.py
**What goes wrong:** `search_hub_datasets` uses `params["offset"] = offset` internally. But Saskatchewan GeoHub (OGC API Records spec) requires `startindex`, not `offset`. `?offset=3` returns `{numberMatched: null, numberReturned: null}` — silently broken pagination.
**Why it happens:** The OGC API Records spec uses `startindex`. The `shared/arcgis_hub.py` was written assuming generic ArcGIS Hub behavior, and Manitoba's fix was local to the manitoba module. The shared helper was never updated.
**How to avoid:** Wave 0 prerequisite task: fix `shared/arcgis_hub.py:search_hub_datasets` to use `params["startindex"] = offset` (not `offset`). This affects York Region (Phase 14), Alberta (Phase 17), Manitoba (Phase 18), and Saskatchewan (Phase 19) — any module using Hub Search pagination.
**Warning signs:** Hub search returns `null` for `numberMatched` or same first page repeatedly despite different offset values in tests.

### Pitfall 2: WSA FeatureServer layer IDs are NOT 0
**What goes wrong:** Calling `WSA_Reservoirs/FeatureServer/0` returns empty features. Layer 0 does not exist at that index for WSA services.
**Why it happens:** WSA's ArcGIS publishing assigns non-zero layer IDs — confirmed: `WSA_Reservoirs` layer is at index 26, `Primary_Water_Quality_Monitoring_Stations` is at index 19.
**How to avoid:** Always fetch the FeatureServer metadata first (`/FeatureServer?f=json`) to confirm layer IDs before querying. Add `WSA_RESERVOIRS_LAYER = 26` constant. Never assume layer 0.
**Warning signs:** `resultRecordCount=3` returns 0 features with no error.

### Pitfall 3: SPSA fire ban uses a different REST server than the Hub
**What goes wrong:** Using the Hub Search to find the current fire ban — the SPSA `Public_Fire_Ban` FeatureServer is not discoverable via `geohub.saskatchewan.ca` Hub Search. It's on `gis.saskatchewan.ca/egis/rest/services/Wildfire/`.
**Why it happens:** SPSA operates its own ArcGIS REST server, not on the primary `zcv98lgAl8xQ04cW` org.
**How to avoid:** Curated fire ban tools call `FIRE_BAN_FS_URL` directly. Discovery tools will not return SPSA datasets via Hub Search — document this in the `saskatchewan_search_datasets` docstring.

### Pitfall 4: The Petroleum FeatureServer (oil & gas wells) returns HTTP 400 on open queries
**What goes wrong:** Querying `gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0` with `where=1=1` returns HTTP 400 "Unable to complete operation."
**Why it happens:** The Petroleum data layer may require specific filter conditions or is not fully public despite being on the public egis server. The schema is accessible (`/FeatureServer/0?f=json` returns field list) but data queries fail.
**How to avoid:** Do not build a curated oil/gas wells tool. Reference petroleum data through discovery tools pointing to the federal CKAN (which has geological Survey structure maps). Document the limitation in `docs://saskatchewan/portal-guide` resource.

### Pitfall 5: Crop Production 2025 FeatureServer has no crop data
**What goes wrong:** `Crop_Production_2025/FeatureServer/0` sounds like what agents want for crop statistics but only has `CDNAME` (Census Division Name), `LANDAREAIN` (land area in km²), and `Census_Div` (division number) — just boundary geometry, no crop data.
**Why it happens:** This is a spatial boundary layer used as a base map for crop production maps, not a data table.
**How to avoid:** Use `Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer/0` for actual crop yield data. Document the distinction in the `docs://saskatchewan/portal-guide` resource.

### Pitfall 6: Multiple-hub confusion (all same org)
**What goes wrong:** Developer finds `moh-geohub-saskatchewan.hub.arcgis.com`, `environment-saskatchewan.hub.arcgis.com`, `er-saskatchewan.hub.arcgis.com`, `geohub.saskatchewan.ca` and treats them as separate portals requiring separate discovery tools.
**Why it happens:** Saskatchewan uses a per-ministry branding pattern but all resolve to the same ArcGIS Online org `zcv98lgAl8xQ04cW`. Only WSA is a separate org.
**How to avoid:** One set of discovery tools against `geohub.saskatchewan.ca` covers ALL ministry data (confirmed by sampling items from ministry hubs that all appear in main GeoHub). WSA is the only exception; curated WSA tools call `services1.arcgis.com/7MBdlVpjqbfBhQer/` directly.

### Pitfall 7: Highway Hotline API key requirement
**What goes wrong:** Planning transport tools assuming the Highway Hotline is keyless like Alberta's 511.
**Why it happens:** Saskatchewan's Highway Hotline has the same technical structure as Alberta 511 (v2 REST JSON) but adds a `key` query parameter requirement. All keyless requests return `<Error><Message>Invalid Key</Message></Error>` (HTTP 400).
**How to avoid:** Per CONTEXT.md locked decision: do NOT plan any transport tools. Do NOT ship NOT_CONFIGURED stubs. Transport is deferred entirely. This is a stricter position than Manitoba Phase 18.

### Pitfall 8: Health domain assumption
**What goes wrong:** Expecting Saskatchewan Health Authority (SHA) facility locations in the ArcGIS Hub — SHA does not appear to have a public-facing FeatureServer in `zcv98lgAl8xQ04cW` or any discovered org.
**Why it happens:** Alberta (AHSGIS), Manitoba (geoportal) both had health facility FeatureServers. Saskatchewan may keep health data in a restricted org or have not yet published it to the Hub.
**How to avoid:** Health domain is deferred. The air quality domain (`Hourly_Ambient_Air_Quality`) is substituted as the 3rd environment tool to keep the curated count at target.

---

## Saskatchewan-Specific Reference Data (for Resources)

### Saskatchewan's Health Regions (for data://saskatchewan/health-regions)

| Region | Short Name | Coverage | Notes |
|--------|-----------|----------|-------|
| Saskatchewan Health Authority | SHA | Province-wide (merged all former RHAs in 2017) | Single provincial health authority since 2017 — unlike Manitoba (5 RHAs) |

**Note:** Saskatchewan merged all 12 former Regional Health Authorities into a single SHA in 2017. This simplifies health region data but means no FeatureServer provides SHA facility locations at this time.

### Saskatchewan's Major River Basins (for data://saskatchewan/major-basins)

| Basin | Major River | WSA Monitor? | Notes |
|-------|-------------|--------------|-------|
| Qu'Appelle | Qu'Appelle River | Yes | Eastern prairies, Last Mountain Lake |
| North Saskatchewan | North Saskatchewan River | Yes | Flows through Saskatoon → Manitoba |
| South Saskatchewan | South Saskatchewan River | Yes | Joins North Sask at Prince Albert |
| Assiniboine | Assiniboine River | Yes | SE Saskatchewan → Manitoba |
| Churchill | Churchill River | Yes | Northern Saskatchewan |
| Athabasca | Athabasca River | Yes | NW Saskatchewan → Alberta |

### Saskatchewan's Crop Reporting Regions (for data://saskatchewan/crop-regions)

| Region | Location | Signature Crops |
|--------|----------|----------------|
| Southeast | Weyburn/Estevan area | Lentils, chickpeas, canola |
| Southwest | Swift Current area | Durum, winter wheat, lentils |
| Central | Saskatoon area | Canola, HRSW, peas |
| Northeast | Prince Albert area | Canola, oats, barley |
| Northwest | North Battleford area | Canola, flax, barley |

### Open Data Licence

- **Name:** Government of Saskatchewan Standard Unrestricted Use Data Licence (Version 2.0) — "GOS Standard Unrestricted Use Data Licence v2.0"
- **Published:** July 24, 2024
- **Contact:** egis@gov.sk.ca
- **Status:** Permits commercial and non-commercial use, reproduction, adaptation, distribution; attribution required
- **Source:** `https://open.canada.ca/data/en/dataset/d807f951-bc0e-1ec0-a978-6de55d031de9` (listed in federal catalogue as attached to Saskatchewan geospatial datasets)
- **Compatibility:** Similar to OGL Canada 2.0; compatible with other Canadian provincial OGL variants

---

## Code Examples

### Hub Search Discovery (after startindex fix)

```python
# Source: Manitoba Phase 18 pattern — same OGC API Records structure
# Pagination uses startindex, NOT offset (confirmed: offset returns null)
result = await api_get(
    "https://geohub.saskatchewan.ca/api/search/v1/collections/all/items",
    {"q": query, "limit": page_size, "startindex": offset},
    headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
)
# result is a dict with "features" list — NOT CKAN envelope
# numberMatched: 181 (total items)
items = result.get("features", [])
```

### SPSA Fire Ban Query (confirmed working 2026-06-15)

```python
# Source: Live-verified — SPSA fire ban layer 0 (Urban Municipalities)
features, truncated = await arcgis_hub.query_feature_service(
    "https://gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer",
    layer_id=0,  # 0=Urban, 2=Rural, 3=Provincial, 8=Parks
    where="1=1",
    out_fields="UMTYPE,Municipali,Fire_Depar,Start_Date,Contact_Nu,Type,Comment",
    include_geometry=False,
    max_records=MAX_RECORDS,
)
# Sample result:
# {'UMTYPE': 'T', 'Municipali': 'Arborfield', 'Fire_Depar': 'Arborfield',
#  'Start_Date': '20260611', 'Type': 'Ban',
#  'Comment': "Level 1 Ban - Supervised incinerators..."}
```

### WSA Hydrometric Stations (confirmed working 2026-06-15)

```python
# Source: Live-verified — layer 0, Province='SK' filter
features, truncated = await arcgis_hub.query_feature_service(
    "https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Hydrometric_Gauging_Stations_V2/FeatureServer",
    layer_id=0,
    where="Province='SK'",
    out_fields="Station_Number,Station_Name,Major_Basin,Station_Type,Station_Class,Operated_By,HyperLink_Graph",
    include_geometry=False,
    max_records=MAX_RECORDS,
)
# Sample: {'Station_Number': '05MB006', 'Station_Name': 'CROOKED HILL CREEK NEAR CANORA',
#          'Major_Basin': 'Assiniboine River', 'Station_Class': 'Seasonal',
#          'HyperLink_Graph': 'https://www.wsask.ca/hydrographs/05MB006-hrly.html'}
```

### WSA Reservoirs (layer 26 — NOT 0)

```python
# Source: Live-verified — layer_id=26 is CRITICAL, layer 0 returns empty
features, truncated = await arcgis_hub.query_feature_service(
    "https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Reservoirs/FeatureServer",
    layer_id=26,  # NOT layer 0 — confirmed via FeatureServer metadata
    where="1=1",
    out_fields="Reservoir_Name,Dam_Name,Imagery_Date,Water_Level_MASL",
    include_geometry=False,
    max_records=MAX_RECORDS,
)
# Sample: {'Reservoir_Name': 'ADMIRAL RESERVOIR', 'Dam_Name': 'ADMIRAL DAM'}
```

### Crop Yield Query (confirmed working 2026-06-15)

```python
# Source: Live-verified
features, truncated = await arcgis_hub.query_feature_service(
    "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer",
    layer_id=0,
    where="1=1",
    out_fields="Region,HRSW,Durum,Oat,Barley,Canola,Pea,Lentil,Chickpea,Canary_seed,Flax,Mustard,Soybean,Winter_wheat,Fall_rye,Other_wheat_",
    include_geometry=False,
    max_records=10,
)
# Returns: Region='Provincial', HRSW=43, Durum=36, Canola=34, Lentil=1369, Chickpea=1123 (bu/acre)
```

### Air Quality Live Readings (confirmed current 2026-06-15)

```python
# Source: Live-verified — Hourly_Ambient_Air_Quality (current readings)
features, truncated = await arcgis_hub.query_feature_service(
    "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Hourly_Ambient_Air_Quality/FeatureServer",
    layer_id=0,
    where="COMMUNITY='Regina'",  # or '1=1' for all communities
    out_fields="COMMUNITY,STATIONID,PM2_5,NO2,O3,PM10,SO2,CO,H2S,AQHI,DATETIME",
    include_geometry=False,
    max_records=10,
)
# AQHI field contains URL: 'https://weather.gc.ca/airquality/pages/skaq-001_e.html'
```

---

## State of the Art / Shared Fix Required

### Critical: shared/arcgis_hub.py startindex fix

| Symptom | Root Cause | Fix Required |
|---------|------------|--------------|
| Discovery tools silently return same first page for all offsets | `search_hub_datasets` uses `params["offset"]` which OGC API Records ignores | Change to `params["startindex"]` |
| Manitoba Phase 18 worked around this with a local per-module patch | Fix was never propagated to `shared/arcgis_hub.py` | Single shared fix benefits YR-14, MB-01, AB-01, SK-01 |

**Wave 0 prerequisite task:** Fix `shared/arcgis_hub.py` line 72:
```python
# BEFORE (broken for OGC API Records hubs):
if offset > 0:
    params["offset"] = offset

# AFTER (correct for Saskatchewan, Manitoba, Alberta, York Region):
if offset > 0:
    params["startindex"] = offset
```

This is a one-line change but must be the FIRST task in Wave 0 for Phase 19, before any Hub Search tests are written.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/saskatchewan/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| Integration command | `uv run pytest tests/integration/ -v -m integration --timeout=120` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | Wave 0? |
|--------|----------|-----------|-------------------|---------|
| SK-01 | Hub Search returns items, pagination works with startindex | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskSearchDatasets -x` | fixture needed |
| SK-02 | Hub item detail returns FeatureServer URL | unit (mock) | `pytest src/.../test_tools.py::TestSaskGetDatasetDetails -x` | fixture needed |
| SK-03 | Query auto-router: FeatureServer→ArcGIS, CSV→parsers | unit (mock) | `pytest src/.../test_tools.py::TestSaskQueryDataset -x` | fixture needed |
| SK-04 | Organizations list returns SK gov orgs | unit (mock) | `pytest src/.../test_tools.py::TestSaskListOrgs -x` | fixture needed |
| SK-05 | Categories list returns themes | unit (mock) | `pytest src/.../test_tools.py::TestSaskListCategories -x` | fixture needed |
| SK-06 | Crop yields returns 16 crop types, Provincial + Region dispatch | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetCropYields -x` | fixture needed |
| SK-07 | Grain elevators returns SK stations with capacity | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetGrainElevators -x` | fixture needed |
| SK-08 | Potash mines: Name, Company, Status, Mine_Type returned | unit (mock) + integration (live) | via SK-09 dispatch test | fixture needed |
| SK-09 | Uranium mines: Name, Company, Status returned | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetMineralMines -x` | fixture needed |
| SK-10 | Air quality: PM2_5, NO2, AQHI link returned for communities | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetAirQuality -x` | fixture needed |
| SK-11 | Fire bans: ban_scope dispatch, active bans returned | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetFireBans -x` | fixture needed |
| SK-12 | Historic wildfires: YEAR, CAUSE1, HECTARES returned | unit (mock) | `pytest src/.../test_tools.py::TestSaskGetHistoricWildfires -x` | fixture needed |
| SK-13 | WSA stations: Province='SK' filter, HyperLink_Graph returned | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetWSAStations -x` | fixture needed |
| SK-14 | WSA reservoirs: layer 26, Reservoir_Name returned | unit (mock) + integration (live) | `pytest src/.../test_tools.py::TestSaskGetWSAReservoirs -x` | fixture needed |
| SK-15 | discover_tools finds saskatchewan_ tools, call_tool executes | integration (live) | `pytest tests/integration/test_tool_scenarios.py::TestSaskatchewanToolScenarios -x` | test class needed |

### MANDATORY: Live Integration Test Strategy (Manitoba Lesson)

**Critical lesson from Manitoba Phase 18:** Mocked unit tests masked a live HTTP 400 bug (the Manitoba discovery tests all passed with mocks, but the live API returned 400 because the `_hub_get` function was not passing the right params). For Saskatchewan, the following integration tests MUST hit real endpoints:

1. **SK-01 Discovery integration test:** Call `discover_tools` with query "Saskatchewan crops" through MCP Client layer — confirm `saskatchewan_search_datasets` appears in results AND that calling it returns `numberMatched > 0` from the live Hub.

2. **SK-06 Crop yields live test:** Call `saskatchewan_get_crop_yields` through MCP Client and assert `"Canola"` field exists in response with a non-null value. Do NOT just assert response shape — the Alberta crop stats lesson showed that asserting field presence prevents silent data-structure regressions.

3. **SK-11 Fire bans live test:** Call `saskatchewan_get_fire_bans(ban_scope="urban")` through MCP Client. Assert `_meta.source.api` matches expected and response contains a list (even empty in off-season is valid — same as Manitoba flood alerts).

4. **SK-13 WSA stations live test:** Call `saskatchewan_get_wsa_stations()` through MCP Client. Assert Station_Number and HyperLink_Graph fields are present in at least one result. This catches the layer-ID bug (layer 0 vs 26) that mocks would miss.

### Sampling Rate

- **Per task commit:** `uv run pytest src/mcp_canada/modules/saskatchewan/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green + integration scenarios pass before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `shared/arcgis_hub.py` — fix `offset` → `startindex` (1-line change, PREREQUISITE)
- [ ] `src/mcp_canada/modules/saskatchewan/__init__.py` — MODULE_NAME, MODULE_DESCRIPTION
- [ ] `src/mcp_canada/modules/saskatchewan/constants.py` — all FeatureServer URLs (see Pattern 1 above)
- [ ] `src/mcp_canada/modules/saskatchewan/__tests__/conftest.py` — Hub Search fixture + FeatureServer fixture (crop yields, fire bans, WSA stations, mineral mines, air quality)
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestSaskatchewanToolScenarios` class (at minimum: discovery + crop yields + fire bans + WSA stations live scenarios)

---

## Sources

### Primary (HIGH confidence — live-verified endpoints)

- `geohub.saskatchewan.ca` — ArcGIS Hub Search API, live probed 2026-06-15; 181 items; org `zcv98lgAl8xQ04cW`
- `services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/` — direct FeatureServer queries for Crop Yields, Mineral Mines, Wildfire Boundaries, Air Quality; all live-verified
- `gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer` — live fire bans with active data confirmed 2026-06-15
- `services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/` — WSA Hydrometric Gauging Stations V2 + WSA Reservoirs (layer 26); live-verified
- `geohub-wsask.hub.arcgis.com` — WSA ArcGIS Hub; 60 items; live-verified
- `open.canada.ca/data/api/3/action/organization_show?id=sk` — Government of Saskatchewan on federal CKAN; 413 packages confirmed

### Secondary (MEDIUM confidence — verified via web search + page structure)

- Saskatchewan Highway Hotline API (`hotline.gov.sk.ca/api/v2/get/`) — key-gated confirmed via live test returning `<Error>Invalid Key</Error>`; developer documentation structure confirmed via WebSearch
- GOS Standard Unrestricted Use Data Licence v2.0 — published 2024-07-24 on open.canada.ca; egis@gov.sk.ca contact confirmed
- Ministry-hub structure (moh-geohub, er-saskatchewan, environment-saskatchewan all under same org `zcv98lgAl8xQ04cW`) — confirmed via `orgId` field in Hub Search API responses

### Tertiary (LOW confidence — single-source, needs implementation validation)

- WSA Primary Water Quality Monitoring Stations (layer 19) — layer ID confirmed via FeatureServer metadata but data queries returned 0 features (may be empty off-season or require filter)
- SPSA `Fire_Ban_Map` FeatureServer (additional layers beyond Public_Fire_Ban) — layers listed but not all sampled

---

## Metadata

**Confidence breakdown:**
- Portal identification: HIGH — live Hub Search confirmed, org IDs confirmed, 181 items verified
- Standard stack: HIGH — same ArcGIS Hub pattern as Manitoba (Phase 18)
- Agriculture tools: HIGH — FeatureServer queries live-verified with real crop data
- Energy/mining tools: HIGH — Potash, Uranium FeatureServers live-verified with real mine data
- Wildfire tools: HIGH — SPSA fire bans live with active data; historic wildfires live-verified
- Air quality tools: HIGH — Hourly_Ambient_Air_Quality current data live-verified
- WSA water tools: HIGH (stations) / MEDIUM (reservoirs layer 26, live-verified but off-season data)
- Transport (511): HIGH confidence it's key-gated; LOW confidence on key acquisition path
- Health domain: MEDIUM confidence it doesn't exist as public data (searched extensively, found nothing)
- startindex bug: HIGH — confirmed `offset` returns null, `startindex` works

**Research date:** 2026-06-15
**Valid until:** 2026-09-15 (90 days; ArcGIS Hub portals are stable; dated mineral FeatureServers may get annual refreshes; crop yields update seasonally)
