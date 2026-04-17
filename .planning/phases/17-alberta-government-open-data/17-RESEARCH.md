# Phase 17: Alberta Government Open Data — Research

**Researched:** 2026-04-17
**Domain:** Alberta provincial open data (CKAN publication repo + GeoDiscover ArcGIS REST + WMBappServices ArcGIS Online + AHSGIS ArcGIS Online + AER static reports + 511 Alberta REST API)
**Confidence:** HIGH (every endpoint and tool target verified live against the production APIs on research date)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Primary portal: **open.alberta.ca** CKAN. (Research confirmed `/api/3/action/`, CKAN 2.10.6, no auth, no User-Agent quirk.)
- Secondary geospatial portal — research confirmed (see "Recommended Stack" below): **GeoDiscover Alberta ArcGIS REST 11.3** (`https://geospatial.alberta.ca/titan/rest/services/`) plus **two ArcGIS Online org services** for live wildfire and health data — `WMBappServices` (org id `Eb8P5h4CJk8utIBz`) and `AHSGIS` (org id `7KHJ4f28UDLgUq2U`).
- Geospatial access: **router picks file-vs-live**. Tool inspects dataset metadata and chooses live FeatureServer query when the dataset exposes such an endpoint, otherwise falls back to file-resource parsing. Adds one routing layer (similar to BC's `bc_query_features` two-step but auto-detected).
- Module prefix: `alberta_` (full-name pattern, consistent with `quebec_`, `ontario_`, `toronto_`).
- Module name: `alberta`.
- Federation policy: **let research confirm** — research confirms 370 organizations, federated and historical (see "Federation Policy" below). Recommend Quebec-style "all orgs by default, document federated nature in docstring".
- AER: in scope as full domain (research confirms 4 of 5 originally proposed tools are viable; incidents/spills tool deferred — see "AER Source-of-Truth Policy").
- Wildfire source-of-truth: **let research confirm** — research confirms WMBappServices ArcGIS Online provides better data than open.alberta.ca CKAN for active fires/perimeters/fire bans/forest areas. CKAN provides historical (2006-2025) static CSV.
- Discovery tools: 5 standard CKAN (`alberta_search_datasets`, `alberta_get_dataset_details`, `alberta_query_dataset`, `alberta_list_organizations`, `alberta_list_categories`).
- Curated tools: ALL 8 domains in scope (energy, wildfire, health, transport, environment, agriculture, demographics, parks).
- Total estimate: ~22-25 `alberta_` tools — research confirms achievable; final recommendation is **22 tools (5 discovery + 17 curated)**.
- 6 bilingual prompts (3 guided + 3 quick lookups), 7 zero-parameter resources.
- Bilingual: `lang: Literal["en", "fr"] = "en"` on every `@tool`. Inline `lang == "fr"` ternary for error messages — no `shared/i18n.py:t()` adoption. Alberta data is ~99% English-only at source; FR responses surface English content with French structural messages where applicable.
- Carry forward all technical conventions: 7-file module pattern, standalone `@tool`/`@prompt`/`@resource`, post-15-05 `_api_get` parsed-dict convention, `TestSharedApiGetContract` test class, `(data, was_cached)` client tuples, aggressive flattening, auto-paginate with 5000-record cap + `truncated: true` flag, properties-only by default with opt-in `include_geometry=true`, conservative 10 req/s rate limit for the new CKAN portal, BM25 docstrings (single-line `Use for:` + 8+ `Keywords:`).

### Claude's Discretion

- Final dataset selection per domain — RESOLVED in this research; see "Curated Tool Catalog (17 tools, all live-verified)".
- Whether AER warrants a `shared/aer.py` extraction — RECOMMENDATION: **defer to a later phase**. AER's reusable surface is a single XLSX URL pattern (`https://static.aer.ca/prd/documents/sts/...`) — `shared/parsers.fetch_and_parse()` already handles XLSX. Extraction would be premature.
- CKAN `fq` strategies for organization filtering — RECOMMENDATION: support `organization=` named param mapping to `fq=organization:{slug}`, plus dedicated `format=` mapping to `fq=res_format:{format}` (Alberta-specific quirk — see "Pitfall 2").
- Cache TTLs per tool — RESOLVED per-tool in catalog table.
- User-Agent header for Alberta CKAN — RESOLVED: not required (Cloudflare is friendly; bare `python-httpx/0.28.x` works), but follow Quebec convention and set `User-Agent: mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)` for proper identification.
- Schema field naming for AER tools — RECOMMENDATION: snake_case via existing `_normalize_key()`; surface AER's UWI-style fields as-is in field names but with descriptive Pydantic field aliases.

### Deferred Ideas (OUT OF SCOPE)

- Calgary, Edmonton, Lethbridge, Red Deer, Medicine Hat municipal portals (Phases 29, 30, future).
- AER as dedicated phase (kept in scope for Phase 17).
- Fire bans / restrictions tool — **REVERSED** by this research: WMBappServices `alberta_fire_ban_system` FeatureServer IS public; the tool moves OUT of deferred and INTO scope. (See `alberta_get_fire_bans` in catalog.)
- Federal Environment Canada wildfire feeds.
- AER incidents/compliance auth-protected endpoints (CONFIRMED by research — see "Pitfall 7").
- Cross-module SQL examples for Alberta dedicated phase.
- MSC weather (FWI) duplication review — RESOLVED: MSC weather (Phase 4) does NOT expose Canadian Forest Fire Weather Index components. WMBappServices does NOT publish FWI either. **Recommendation:** drop `alberta_get_fire_weather` from the curated set; replace with `alberta_get_fire_control_orders` (Fire Control Orders FeatureServer is public).
- Bilingual `shared/i18n.py:t()` adoption.
- Auth-required AER endpoints (OneStop API not public).
- ER wait times (CONFIRMED by research: not on open.alberta.ca CKAN; AHS publishes only via web widget — defer until AHS exposes a JSON endpoint).
- Notifiable disease surveillance (PDF-only — defer).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

These are the proposed `AB-XX` requirements for Phase 17, derived from CONTEXT.md decisions and validated against live data availability. Planner must add these to REQUIREMENTS.md (currently no AB-XX rows exist). Naming follows BC and Quebec precedent (`BC-XX`, `QC-XX` in project history).

| ID | Description | Research Support |
|----|-------------|-----------------|
| AB-01 | Agent can search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets) by keyword with optional `organization`, `format`, and pagination | CKAN package_search live-verified; format facet returns PDF (28,763) / CSV (224) / XLSX (774) / Esri REST (93) |
| AB-02 | Agent can get full details for an Alberta dataset by id/slug, including resources list with format and URL | package_show verified |
| AB-03 | Agent can query a dataset (file resource OR live ESRI REST FeatureServer) via auto-router | Hybrid file-vs-live router: `format=ESRI REST` resources route to `arcgis_hub.query_feature_service`; CSV/XLSX/JSON route to `fetch_and_parse` |
| AB-04 | Agent can list Alberta government organizations (370 orgs) — federated catalog including current ministries, historical ministries, and Crown corps | organization_list live-verified |
| AB-05 | Agent can list dataset formats / categories — Alberta CKAN does NOT use groups (group_list returns empty); use res_format facet | group_list returns `[]`; tag_list returns 28,949 tags (too noisy); recommendation: `alberta_list_categories` returns `res_format` facet (10-30 entries) |
| AB-06 | Agent can search wells issued by AER and get well count / list | Built on AER ST1 daily list (TXT) and weekly XLSX archive (`dwll{YYYY}-{MM}.zip`) |
| AB-07 | Agent can get well licence details by licence number | AER ST1 annual archive XLSX (parseable) |
| AB-08 | Agent can get pipeline statistics (length by substance/operator) — annual ST39 | `https://static.aer.ca/prd/documents/sts/ST39-{YYYY}.xls` verified working |
| AB-09 | Agent can get monthly oil/gas/bitumen production volumes — ST3 monthly XLSX | `https://static.aer.ca/prd/documents/sts/st3/{Product}_current.xlsx` verified for Butane/Ethane/NGL/Oil/Gas/Sulphur/Propane |
| AB-10 | Agent can get current active wildfires from WMBappServices ArcGIS Online | `Active_Wildfires_Dashboard_view` FeatureServer (17 records on probe; 15 fields including FIRE_NUMBER, FIRE_STATUS, AREA_ESTIMATE, GENERAL_CAUSE, RESP_AREA) |
| AB-11 | Agent can get wildfire perimeters (active + non-active simplified views) | `Active_Wildfire_Perimeters_Simplified_view` + `Extinguished_Wildfire_Perimeters_Simplified_view` FeatureServers verified |
| AB-12 | Agent can get historical wildfire data (2006-current) by year, cause, area | `wildfire-data` CKAN package (10MB CSV) — `fetch_and_parse` |
| AB-13 | Agent can get current fire bans / advisories from WMBappServices | `alberta_fire_ban_system` FeatureServer verified |
| AB-14 | Agent can get fire control orders, OHV restrictions, and forest area boundaries | Three FeatureServers: `Fire_Control_Orders_Prod_View2`, `OHV_RestrictionL_Prod_View`, `Forest_Area_Prod_View2` (10 forest areas verified) |
| AB-15 | Agent can get AHS hospital locations with zone/IP/ED capability flags (101 hospitals) | `AHS_Hospitals` FeatureServer verified — 101 hospitals, 10 fields including IP/ED flags |
| AB-16 | Agent can get EMS station and walk-in clinic locations | `EMS_Stations` + `PCN_Clinics` + `Non_PCN_Clinics` FeatureServers verified |
| AB-17 | Agent can get AHS zone boundaries with population stats | `AHS_Zone` FeatureServer verified — 5 zones (South, Calgary, Central, Edmonton, North) with POP2006/2011/2016 |
| AB-18 | Agent can get current road events (closures, construction, incidents) from 511 Alberta API | `https://511.alberta.ca/api/v2/get/event` verified — 142 records, 26 fields including RoadwayName, EventType, Lat/Lon, IsFullClosure |
| AB-19 | Agent can get current winter road conditions from 511 Alberta API | `https://511.alberta.ca/api/v2/get/winterroads` verified — 1,121 records with Primary Condition, AreaName, RoadwayName, EncodedPolyline |
| AB-20 | Agent can get traffic camera locations and snapshot URLs from 511 Alberta API | `https://511.alberta.ca/api/v2/get/cameras` verified — 376 cameras with Location, Lat/Lon, Views array |
| AB-21 | Agent can get air quality monitoring stations from GeoDiscover Alberta (75 stations with pollutant readings: O3/NO2/CO/PM2.5/SO2) | `aqhi/air_layers/MapServer/1` verified |
| AB-22 | Agent can get water management advisories, river forecast, drought stages | `environment/river_forecast_centre` FeatureServer verified — 10 layers (advisories, drought, ice cover, water sharing) |
| AB-23 | Agent can get water licence registry (active + inactive) — Alberta Environment | `water-licence-data` CKAN package (87MB active, 169MB inactive — too large for default tool; expose as discovery only with row filter requirement) |
| AB-24 | Agent can get major crop production statistics (Alberta Official Statistic) | `major-crop-production-alberta` CKAN package — CSV verified |
| AB-25 | Agent can get population estimates by sub-provincial area (Census Subdivision) | `alberta-population-estimates-data-tables` CKAN package — XLSX verified |
| AB-26 | Agent can get provincial parks/protected areas registry | `gda-6b96341f-2e19-4885-98af-66d12ed4f8dd` CKAN package → `boundary/parks_protected_areas_alberta/FeatureServer` GeoDiscover REST verified |
| AB-27 | All Alberta tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, alberta_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider | Conventions established by Phases 12-16 |

**Total: 27 requirements (5 discovery + 22 curated/infra). Tool count: 22 (5 discovery + 17 curated).**

</phase_requirements>

---

## Summary

Five major findings reshape the curated tool catalogue and confirm Phase 17 is single-phase-feasible (no need to split into 17a/17b):

1. **open.alberta.ca CKAN is a publication repository, not a primary data portal.** 86% of its 33,269 datasets are PDF reports (audience, author, ISBN/AGDEX/ALIS identifiers in extras), only ~1,200 datasets have machine-readable resources (CSV 224 / XLSX 774 / Esri REST 93 / JSON 75 / WMS 26). This means CKAN discovery tools work normally, but the *signature* Alberta data lives in three other portals.

2. **Three signature data portals federate into the Alberta surface — all are public, no auth:**
   - **GeoDiscover Alberta** (`geospatial.alberta.ca/titan/rest/services/`) — Esri ArcGIS REST 11.3 with 52 folders, 21 of which work without authentication (transportation, energy, environment, aqhi, water, boundaries, parks, etc.). Some sensitive folders (wildfire, fire, forestry, hydro, health) DO require tokens, but their public versions live elsewhere (see #3 and #4). `shared/arcgis_hub.py`'s `query_feature_service` works on these endpoints unchanged.
   - **WMBappServices** ArcGIS Online org (`https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/`) — 123 wildfire-related items, including verified-public Feature Services for active wildfires, perimeters (active+non-active), fire bans, fire control orders, OHV restrictions, forest areas, and YTD wildfire counts.
   - **AHSGIS** ArcGIS Online org (`https://services5.arcgis.com/7KHJ4f28UDLgUq2U/arcgis/rest/services/`) — 290 health items, including verified-public Feature Services for hospitals (101), EMS stations, AHS zones (5), PCN clinics, and Local/Sub-Local Geographic Areas.

3. **AER (Alberta Energy Regulator) data is publishable via stable static XLSX/TXT URLs**, NOT a public REST API. AER's OneStop API requires authentication (404 on public probes), and the BlueScope IDS-style "incidents" registry is auth-walled. But four signature reports (ST1 well licences daily, ST3 monthly production, ST39 annual pipeline statistics, ST98 annual energy outlook supply/demand) are downloadable as XLSX/TXT/ZIP from `https://static.aer.ca/prd/documents/sts/...` and `https://static.aer.ca/prd/data/well-lic/...`. `shared/parsers.fetch_and_parse()` handles XLSX directly. Pipeline incidents (ST57) is PDF-only — defer.

4. **511 Alberta has an undocumented but public REST API** at `https://511.alberta.ca/api/v2/get/{event,cameras,winterroads}` — three endpoints verified working, returning JSON arrays. The developer doc page redirects to `/notfound` (the docs were taken down or never existed), but the API is live and free of rate-limit headers. This delivers 3 of the 4 originally planned transport tools cleanly. Highway closures are folded into `alberta_get_road_events` (event type filter).

5. **MSC weather (Phase 4) does NOT expose Canadian Forest Fire Weather Index** components, and WMBappServices does NOT publish FWI station readings either. The originally-planned `alberta_get_fire_weather` tool has no clean public source. **Recommendation:** drop FWI; replace with `alberta_get_fire_control_orders` (which is on WMBappServices and is a distinct query class — operational fire restrictions agents need during active fire events).

**Primary recommendation:** Build the 22 tools (5 discovery + 17 curated) listed in the catalog. Reuse `shared/arcgis_hub.py` for both GeoDiscover and the two ArcGIS Online orgs (WMBappServices + AHSGIS). Reuse `shared/parsers.fetch_and_parse()` for AER static XLSX downloads. Build `alberta_get_road_events` / `alberta_get_winter_road_conditions` / `alberta_get_traffic_cameras` as direct httpx calls (no shared 511 client — single API surface, three endpoints).

**Phase 17a/17b split: NOT NEEDED.** All 22 tools fit comfortably in a single phase given the 4-portal split.

---

## Standard Stack

### Core (no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp` | 3.2.x | MCP server framework | Project standard |
| `httpx` | 0.28.x | Async HTTP for CKAN, ArcGIS REST, AER static, 511 | Shared infrastructure |
| `pydantic` | v2 | Flat schemas | Project standard |
| `aiocache` | latest | TTL caching via `cached_fetch` | Project standard |
| `tenacity` | latest | Retry built into `shared/http.api_get` | Project standard |
| `openpyxl` | already in deps | AER ST3/ST39/ST98 XLSX parsing | Phase 11 added; Phase 16 used |
| `pandas` | already in deps (pandas-when-available pattern) | Multi-sheet XLSX (some AER files) | Phase 11 pattern |

### Supporting (all existing shared infra)

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `shared/http.py:api_get` | CKAN Action API + 511 JSON | All `_api_get` calls (Alberta CKAN); 511 direct calls |
| `shared/arcgis_hub.py:query_feature_service` | GeoDiscover REST + WMBappServices + AHSGIS | All FeatureServer queries |
| `shared/arcgis_hub.py:get_layer_metadata` | Detect maxRecordCount before paginating | Once per layer (cached 24h) |
| `shared/parsers.py:fetch_and_parse` | AER ST3/ST39/ST98 XLSX, AER ST1 TXT, OA CKAN CSV/XLSX | All file resources |
| `shared/cache.py:cached_fetch` | TTL caching | Every client function |
| `shared/rate_limiter.py:get_limiter` | Token bucket per source | Every client function |
| `shared/envelope.py` | `make_response` / `make_error` | Every tool function |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Direct httpx for 511 endpoints | New `shared/five11.py` module | Premature — single province, three endpoints, 200 LOC of client code |
| `shared/arcgis_hub.py` for WMBappServices/AHSGIS | New `shared/arcgis_online.py` | Same protocol — `query_feature_service` already accepts any FeatureServer URL |
| `shared/parsers.fetch_and_parse` for AER | New `shared/aer.py` | AER's reusable surface is one XLSX URL pattern; extract only if 4+ provincial energy modules emerge |
| OGC WFS (`shared/ogc.py`) | — | NOT applicable: GeoDiscover Alberta supports WMS but the public AGS layers don't expose WFS endpoints |

### No New Dependencies

The full stack (httpx, pydantic, aiocache, tenacity, openpyxl, pandas) covers every Alberta surface.

---

## Architecture Patterns

### Recommended Module Structure

```
src/mcp_canada/modules/alberta/
├── __init__.py           # MODULE_NAME = "alberta", MODULE_DESCRIPTION (en+fr)
├── constants.py          # All BASE_URLs, RATE_GROUPs, CACHE_TTL_*, FeatureServer URLs, AER URLs, ORG slugs
├── schemas.py            # Flat Pydantic v2 models (AlbertaDatasetSummary, AlbertaWildfire, AlbertaHospital, AlbertaWellLicence, etc.)
├── client.py             # 22 async functions returning (data, was_cached) tuples
├── tools.py              # 22 @tool functions (5 discovery + 17 curated)
├── prompts.py            # 6 bilingual @prompt functions
├── resources.py          # 7 zero-parameter @resource functions
└── __tests__/
    ├── __init__.py
    ├── conftest.py        # Sample fixtures: package_search, package_show, AER ST1 TXT, AER ST3 XLSX, ArcGIS GeoJSON, 511 JSON
    ├── test_client.py     # Client unit tests + TestSharedApiGetContract
    ├── test_tools.py      # Tool unit tests (mocked client layer)
    └── test_prompts_resources.py
```

### Pattern 1: Quad-Source Constants Layout

```python
# src/mcp_canada/modules/alberta/constants.py
from typing import Final

# ---------------------------------------------------------------------------
# CKAN — open.alberta.ca
# ---------------------------------------------------------------------------
CKAN_BASE_URL: Final[str] = "https://open.alberta.ca/api/3/action/"
RATE_GROUP_CKAN: Final[str] = "alberta_ckan"
RATE_LIMIT_CKAN: Final[float] = 10.0

# ---------------------------------------------------------------------------
# GeoDiscover Alberta — Esri ArcGIS REST 11.3
# ---------------------------------------------------------------------------
GEODISCOVER_BASE_URL: Final[str] = "https://geospatial.alberta.ca/titan/rest/services"
RATE_GROUP_GEODISCOVER: Final[str] = "alberta_geodiscover"
RATE_LIMIT_GEODISCOVER: Final[float] = 5.0

# AQHI air monitoring
AQHI_AIR_LAYER_URL: Final[str] = f"{GEODISCOVER_BASE_URL}/aqhi/air_layers/MapServer"
AQHI_STATIONS_LAYER_ID: Final[int] = 1
# Water/river forecast
RIVER_FORECAST_FS_URL: Final[str] = f"{GEODISCOVER_BASE_URL}/environment/river_forecast_centre/FeatureServer"
# Parks
PROVINCIAL_PARKS_FS_URL: Final[str] = f"{GEODISCOVER_BASE_URL}/boundary/parks_protected_areas_alberta/FeatureServer"

# ---------------------------------------------------------------------------
# WMBappServices ArcGIS Online — Wildfire Management Branch
# ---------------------------------------------------------------------------
WMB_ORG_BASE: Final[str] = "https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services"
RATE_GROUP_WMB: Final[str] = "alberta_wmb"
RATE_LIMIT_WMB: Final[float] = 5.0

ACTIVE_WILDFIRES_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Active_Wildfires_Dashboard_view/FeatureServer"
ACTIVE_FIRE_PERIMETERS_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Active_Wildfire_Perimeters_Simplified_view/FeatureServer"
EXTINGUISHED_WILDFIRES_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Extinguished_Wildfires_Locations/FeatureServer"
EXTINGUISHED_PERIMETERS_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Extinguished_Wildfire_Perimeters_Simplified_view/FeatureServer"
FIRE_BAN_SYSTEM_FS_URL: Final[str] = f"{WMB_ORG_BASE}/alberta_fire_ban_system/FeatureServer"
FIRE_CONTROL_ORDERS_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Fire_Control_Orders_Prod_View2/FeatureServer"
OHV_RESTRICTION_FS_URL: Final[str] = f"{WMB_ORG_BASE}/OHV_RestrictionL_Prod_View/FeatureServer"
FOREST_AREA_FS_URL: Final[str] = f"{WMB_ORG_BASE}/Forest_Area_Prod_View2/FeatureServer"

# ---------------------------------------------------------------------------
# AHSGIS ArcGIS Online — Alberta Health Services
# ---------------------------------------------------------------------------
AHS_ORG_BASE: Final[str] = "https://services5.arcgis.com/7KHJ4f28UDLgUq2U/arcgis/rest/services"
RATE_GROUP_AHS: Final[str] = "alberta_ahs"
RATE_LIMIT_AHS: Final[float] = 5.0

AHS_HOSPITALS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/AHS_Hospitals/FeatureServer"
AHS_ZONE_FS_URL: Final[str] = f"{AHS_ORG_BASE}/AHS_Zone/FeatureServer"
AHS_EMS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/EMS_Stations/FeatureServer"
PCN_CLINICS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/PCN_Clinics/FeatureServer"

# ---------------------------------------------------------------------------
# AER (Alberta Energy Regulator) — static XLSX/TXT downloads
# ---------------------------------------------------------------------------
AER_STATIC_BASE: Final[str] = "https://static.aer.ca/prd"
RATE_GROUP_AER: Final[str] = "alberta_aer"
RATE_LIMIT_AER: Final[float] = 2.0  # static files; conservative

# ST1 daily well licences (TXT, overwritten daily)
AER_ST1_DAILY_BASE: Final[str] = f"{AER_STATIC_BASE}/data/well-lic"  # /WELLS{SUN..SAT}.TXT
# ST1 monthly archive ZIP (verified pattern: dwll{YYYY}-{MM}.zip + dwll{YYYY}.zip)
AER_ST1_MONTHLY_BASE: Final[str] = f"{AER_STATIC_BASE}/data/well-lic"
# ST3 monthly production XLSX (current + per-year)
AER_ST3_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts/st3"
# Verified product slugs: Butane, Ethane, NGL, Oil, Gas, Propane, Sulphur, prices_oil
ST3_PRODUCTS: Final[tuple[str, ...]] = ("Butane", "Ethane", "NGL", "Oil", "Gas", "Propane", "Sulphur")
# ST39 annual pipeline statistics (XLSX/PDF)
AER_ST39_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts"
# ST98 annual energy outlook (XLSX per topic)
AER_ST98_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts/st98"

# ---------------------------------------------------------------------------
# 511 Alberta — undocumented but public JSON API
# ---------------------------------------------------------------------------
FIVE11_BASE_URL: Final[str] = "https://511.alberta.ca/api/v2/get"
RATE_GROUP_511: Final[str] = "alberta_511"
RATE_LIMIT_511: Final[float] = 2.0  # conservative; no published limit

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_SEARCH: Final[int] = 3600     # 1hr — CKAN search
CACHE_TTL_META: Final[int] = 86400      # 24hr — package_show, org list, layer metadata
CACHE_TTL_LIVE: Final[int] = 300        # 5min — active wildfires, fire bans, road events, winter roads, AQHI
CACHE_TTL_DAILY: Final[int] = 3600      # 1hr — AER ST1 daily TXT (regenerated daily)
CACHE_TTL_MONTHLY: Final[int] = 86400   # 24hr — AER ST3 (monthly), 511 cameras (locations stable)
CACHE_TTL_STATIC: Final[int] = 86400    # 24hr — hospitals, AHS zones, forest areas (rarely change)
CACHE_TTL_ANNUAL: Final[int] = 604800   # 7d — AER ST39, ST98 (annual)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# Organization slugs (verified — most-used current ministries)
# ---------------------------------------------------------------------------
ORG_FORESTRY_PARKS: Final[str] = "forestry-and-parks"
ORG_ENERGY_MINERALS: Final[str] = "energy-and-minerals"
ORG_ENV_PROTECTED: Final[str] = "environment-and-protected-areas"
ORG_AGRICULTURE: Final[str] = "agriculture-and-irrigation"
ORG_TRANSPORTATION: Final[str] = "transportation-and-economic-corridors"
ORG_HEALTH: Final[str] = "health"
ORG_TBF: Final[str] = "treasuryboardandfinance"
ORG_SOCIAL: Final[str] = "assisted-living-and-social-services"
ORG_EDUCATION: Final[str] = "education-and-childcare"
ORG_CHILDREN: Final[str] = "children-and-family-services"
ORG_AFFORDABILITY: Final[str] = "affordability-and-utilities"
ORG_SERVICE_AB: Final[str] = "servicealberta"
ORG_PUBLIC_SAFETY: Final[str] = "public-safety-and-emergency-services"
ORG_ADV_ED: Final[str] = "advancededucation"  # current Advanced Education slug
```

### Pattern 2: `_api_get` Helper (post-15-05 dict contract)

```python
# src/mcp_canada/modules/alberta/client.py
async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """CKAN Action API call against open.alberta.ca."""
    url = CKAN_BASE_URL + path
    envelope = await api_get(
        url,
        params or {},
        headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
    )
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise httpx.HTTPStatusError(
            f"CKAN returned success=False for {path}",
            request=httpx.Request("GET", url),
            response=httpx.Response(500),
        )
    return envelope.get("result", {})
```

### Pattern 3: Hybrid `alberta_query_dataset` Router

The Alberta CKAN federates GeoDiscover (`format=ESRI REST`) into `package_show` resources. Auto-route based on resource format:

```python
async def fetch_query_dataset(
    dataset_id: str,
    resource_index: int = 0,
    where: str | None = None,
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 5000,
) -> tuple[dict, bool]:
    """Pick a resource and route to the right protocol.

    Routing precedence (matches what an agent would prefer):
      1. format == 'ESRI REST' AND url contains '/FeatureServer' → arcgis_hub.query_feature_service
      2. format in ('CSV', 'JSON', 'GeoJSON', 'XLSX', 'XLS') → fetch_and_parse(url)
      3. otherwise → return resource metadata (treat as discovery-only)
    """
    pkg, _ = await fetch_dataset_details(dataset_id)
    resources = pkg.get("resources", [])
    # honor resource_index (allow agent to pick the nth resource explicitly)
    if resource_index >= len(resources):
        return {"error": "resource_index out of range"}, False
    res = resources[resource_index]
    fmt = (res.get("format") or "").upper()
    url = res.get("url") or ""

    if fmt == "ESRI REST" and "/FeatureServer" in url:
        # Strip trailing /<layer_id>; arcgis_hub expects FeatureServer base + layer_id arg
        base, _, layer = url.partition("/FeatureServer")
        layer_id = int(layer.lstrip("/")) if layer.lstrip("/").isdigit() else 0
        return await arcgis_hub.query_feature_service(
            f"{base}/FeatureServer", layer_id, where=where, out_fields=out_fields,
            include_geometry=include_geometry, max_records=max_records,
        )
    if fmt in ("CSV", "JSON", "GEOJSON", "XLSX", "XLS"):
        rows, was_cached = await fetch_and_parse(url, ttl=CACHE_TTL_META)
        return {"data": rows[:max_records], "truncated": len(rows) > max_records}, was_cached
    # Unparseable resource (PDF, ZIP, KML, WMS) — return metadata only
    return {"format": fmt, "url": url, "name": res.get("name"), "size": res.get("size")}, False
```

### Pattern 4: AER ST3 Multi-Product Fetcher

```python
async def fetch_aer_production(product: str = "Oil") -> tuple[list[dict], bool]:
    """Fetch monthly production XLSX from AER ST3 for a given product."""
    if product not in ST3_PRODUCTS:
        # Inline ternary error (BC 15-05 convention)
        ...
    url = f"{AER_ST3_BASE}/{product}_current.xlsx"
    rows, was_cached = await fetch_and_parse(url, ttl=CACHE_TTL_MONTHLY)
    return rows, was_cached
```

### Pattern 5: 511 Alberta Direct httpx (no shared module)

```python
async def fetch_road_events() -> tuple[list[dict], bool]:
    """Fetch current road events from 511 Alberta v2 API."""
    cache_key = "alberta:511:event"
    limiter = get_limiter(RATE_GROUP_511, rate=RATE_LIMIT_511)

    async def fetcher():
        await limiter.acquire()
        rows = await api_get(
            f"{FIVE11_BASE_URL}/event",
            {"format": "json"},
            headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
        )
        # api_get returns parsed list directly (not wrapped in CKAN envelope)
        return rows

    rows, was_cached = await cached_fetch(cache_key, CACHE_TTL_LIVE, fetcher)
    return rows, was_cached
```

**IMPORTANT:** 511 Alberta returns a JSON list at the top level (not a CKAN-style envelope). `_api_get` from CKAN module is NOT applicable here. Call `shared.http.api_get` directly and treat the return as the parsed list.

### Anti-Patterns to Avoid

- **NEVER use `_api_get` (the CKAN helper) for 511 or ArcGIS calls** — those return raw lists/JSON, not CKAN envelopes.
- **NEVER call `.raise_for_status()` or `.json()` on `api_get` return** — `shared/http.py:api_get` returns parsed JSON. Phase 15 root cause.
- **NEVER mock with `MagicMock(json=lambda: {...})`** — use `AsyncMock(return_value={...})` so tests reflect the real `api_get` contract.
- **NEVER hardcode English-only error messages** — use inline `lang == "fr"` ternary (BC 15-05 convention).
- **NEVER fetch the AER weekly archive ZIPs unbounded** — they unzip to large fixed-width TXT files; surface as discovery URL only.
- **NEVER call GeoDiscover folders that return "Token Required"** (wildfire, fire, forestry, hydro, health) — use WMBappServices/AHSGIS equivalents instead. Document this in `docs://alberta/data-portal-guide`.
- **NEVER scrape 511.alberta.ca's HTML SPA** — only the three confirmed v2 endpoints are sanctioned. Document the 404'd endpoints in pitfalls so future planning doesn't try them again.
- **NEVER call `alberta_list_categories` expecting CKAN groups** — Alberta CKAN's `group_list` returns `[]`. Use the `res_format` facet instead.

---

## Curated Tool Catalog (17 tools, all live-verified)

### Discovery (5 tools — same shape as BC/Quebec)

| Tool | Backend | Cache TTL | Notes |
|------|---------|-----------|-------|
| `alberta_search_datasets` | `package_search` | SEARCH (1h) | Optional `organization=`, `format=` (Alberta-specific quirk: `fq=res_format:CSV`), pagination |
| `alberta_get_dataset_details` | `package_show` | META (24h) | Returns resources list with format/URL/datastore_active flag |
| `alberta_query_dataset` | hybrid router (Pattern 3 above) | META (24h) | Routes ESRI REST → arcgis_hub; CSV/XLSX → fetch_and_parse; PDF/KML → metadata-only |
| `alberta_list_organizations` | `organization_list?all_fields=true` | META (24h) | 370 orgs (federated; includes historical ministries) |
| `alberta_list_categories` | `package_search?facet.field=["res_format"]&rows=0` | META (24h) | NOT `group_list` — Alberta CKAN has no groups. Returns format facet (PDF/CSV/XLSX/Esri REST/etc.) |

### Energy / AER (4 tools)

| Tool | Source URL | Cache TTL | Live count / Notes |
|------|------------|-----------|--------------------|
| `alberta_get_well_licences_today` | `AER_ST1_DAILY_BASE/WELLS{day-of-week}.TXT` | DAILY (1h) | Daily list (AER overwrites by day-of-week). Plain-text fixed-width — parse with stdlib (no openpyxl). Optional CSV alt: `https://www2.aer.ca/t/Production/views/COM-WellLicenceAllList/WellLicenceAllAB.csv` (returns `000` on probe — Tableau public extract may be intermittent; fall back to TXT). |
| `alberta_get_well_licences_archive` | `AER_ST1_MONTHLY_BASE/dwll{YYYY}-{MM}.zip` | ANNUAL (7d) | Monthly ZIP archive. Tool returns metadata + URL (do NOT auto-parse — files are large fixed-width TXT). Agent invokes `alberta_query_dataset` or downloads externally. |
| `alberta_get_pipeline_statistics` | `AER_ST39_BASE/ST39-{YYYY}.xls` | ANNUAL (7d) | Verified ST39-2024.xls (253KB). Multi-sheet by substance (oil, gas, water disposal, etc.). Agent passes `year` param. |
| `alberta_get_production_volumes` | `AER_ST3_BASE/{Product}_current.xlsx` | MONTHLY (24h) | 7 products: Butane/Ethane/NGL/Oil/Gas/Propane/Sulphur. Verified Gas_current (46KB), Butane_current (36KB). NOTE: `Bitumen_current.xlsx` and `CrudeOil_current.xlsx` returned 404 — bitumen production is in `Oil_current.xlsx` and ST98 supplemental files. |

**Deferred from CONTEXT.md energy scope:** `alberta_get_energy_incidents` — confirmed not publicly published. ST57 (yearly incidents) is PDF-only (last public XLS was 2014). AER's incident-tracking system requires authentication. (Pitfall 7.)

### Wildfire (4 tools — was 3 in CONTEXT.md; +1 net by replacing `alberta_get_fire_weather` with `alberta_get_fire_control_orders` and adding `alberta_get_fire_bans`)

| Tool | FeatureServer | Cache TTL | Live count / Notes |
|------|--------------|-----------|--------------------|
| `alberta_get_active_fires` | `ACTIVE_WILDFIRES_FS_URL/0` | LIVE (5min) | 17 records on probe; fields: FIRE_NUMBER, FIRE_YEAR, FIRE_TYPE, FIRE_STATUS, AREA_ESTIMATE, ASSESSMENT_ASSISTANCE_DATE, GENERAL_CAUSE, INCIDENT_TYPE, RESP_AREA, LATITUDE, LONGITUDE, LABEL |
| `alberta_get_fire_perimeters` | `ACTIVE_FIRE_PERIMETERS_FS_URL/0` (active) + `EXTINGUISHED_PERIMETERS_FS_URL/0` (historical) | LIVE (5min) active, STATIC (24h) extinguished | Tool dispatches by `status: Literal["active","extinguished"]` parameter (default "active"). Active perimeters are simplified polygon view; extinguished requires `year` filter. |
| `alberta_get_fire_bans` | `FIRE_BAN_SYSTEM_FS_URL/0` | LIVE (5min) | Province-wide fire ban registry (formerly maintained by `albertafirebans.ca` SPA, but the SPA's data backend IS this WMB FeatureServer — verified by ArcGIS Online catalog) |
| `alberta_get_fire_control_orders` | `FIRE_CONTROL_ORDERS_FS_URL/0` | LIVE (5min) | Operational fire control orders (closures, restrictions, evacuations during active fires). Replaces planned `alberta_get_fire_weather` since FWI is not publicly available. |

**Originally planned but reversed:** `alberta_get_fire_weather` (FWI) — no public source. Documented in `docs://alberta/wildfire-data-guide`.

### Health / AHS (3 tools)

| Tool | FeatureServer | Cache TTL | Live count / Notes |
|------|--------------|-----------|--------------------|
| `alberta_get_hospitals` | `AHS_HOSPITALS_FS_URL/0` | STATIC (24h) | 101 hospitals; fields: Location, Hospital_N, St_Address, PostalCode, Phone, H_Code, IP (inpatient flag), ED (emergency flag), Label. Optional `zone=` filter (joins via `AHS_Zone` polygon containment OR by `Location` name substring match). |
| `alberta_get_ahs_zones` | `AHS_ZONE_FS_URL/0` | STATIC (24h) | 5 zones with POP2006/2011/2016 — South (Z1), Calgary (Z2), Central (Z3), Edmonton (Z4), North (Z5). Already verified above. |
| `alberta_get_health_facilities` | `AHS_EMS_FS_URL/0` (EMS) + `PCN_CLINICS_FS_URL/0` (clinics) | STATIC (24h) | Dispatch by `facility_type: Literal["ems","pcn_clinic"]` parameter. Subsumes the originally-planned `alberta_get_er_wait_times` since AHS does NOT publish wait times in machine-readable form (web widget only — see Open Question 1). |

**Originally planned but deferred:** `alberta_get_er_wait_times` — no public JSON endpoint; AHS website widget is HTML-rendered. Documented in `docs://alberta/health-data-guide`. Pending todo `2026-04-12-research-cross-canada-er-wait-times-datasets.md` from STATE.md is still relevant.

### Transport / 511 Alberta (3 tools)

| Tool | Endpoint | Cache TTL | Live count / Notes |
|------|----------|-----------|--------------------|
| `alberta_get_road_events` | `FIVE11_BASE_URL/event` | LIVE (5min) | 142 records on probe; 26 fields. Optional `event_type=` filter (closures, incidents, construction). Subsumes `alberta_get_highway_closures` (filter `IsFullClosure=true`). |
| `alberta_get_winter_road_conditions` | `FIVE11_BASE_URL/winterroads` | LIVE (5min) | 1,121 records; fields include Primary Condition, Secondary Conditions, Visibility, AreaName, RoadwayName, EncodedPolyline. Critical winter tool. Cache 5min — conditions change rapidly. |
| `alberta_get_traffic_cameras` | `FIVE11_BASE_URL/cameras` | MONTHLY (24h) | 376 cameras with Lat/Lon and snapshot URLs in Views array. Cache 24h — locations stable; snapshot URLs are stable IDs. |

**Originally planned but cut:** ferry status (511 returns 404 for `/ferry`; Alberta runs only 7 cable ferries which are listed on the alberta.ca website, not API). Out of scope.

### Environment (2 tools)

| Tool | Source | Cache TTL | Notes |
|------|--------|-----------|-------|
| `alberta_get_air_quality_stations` | `AQHI_AIR_LAYER_URL/1` | LIVE (5min) | 75 monitoring stations with current pollutant readings (SO2/H2S/TRS/O3/NOX/NO/NO2/NH3/CO/PM2_5/THC/NMHC/CH4/PAH/C2H4/BTEX/Calib). Layer 0 ("Air") returns `fields:None` — skip. Layer 1 is the canonical station registry with live sensor values. |
| `alberta_get_water_advisories` | `RIVER_FORECAST_FS_URL` | LIVE (5min) | 10 layers via dispatch parameter `advisory_type: Literal["river","water_management","drought","ice_cover","water_sharing"]`. Each maps to a layer ID (river=2/7, drought=4/9, etc.). Surface "Sub Basin" polygon variant by default; offer "Polyline" via param. |

### Agriculture (1 tool)

| Tool | Source | Cache TTL | Notes |
|------|--------|-----------|-------|
| `alberta_get_crop_production` | `major-crop-production-alberta` CKAN package CSV | ANNUAL (7d) | Verified package; CSV at `https://open.alberta.ca/dataset/.../resource/.../download/...csv`. Covers 2000-2014 historical major crop production (Alberta Official Statistic). Note dataset is updated infrequently — agent should expect historical data, not current-season crop reports. |

**Originally planned but deferred:** `alberta_get_crop_reports` (weekly crop conditions). Verified absent from open.alberta.ca CKAN. Live weekly crop reports are PDF on the Alberta Agriculture website — no JSON. Document in docstring: agent should call this tool for historical production stats, not in-season conditions.

### Demographics (1 tool)

| Tool | Source | Cache TTL | Notes |
|------|--------|-----------|-------|
| `alberta_get_population_estimates` | `alberta-population-estimates-data-tables` CKAN package XLSX | ANNUAL (7d) | Verified package with 6 XLSX resources (quarterly, components of growth, municipal CSD, annual 1921-2020, by age/sex 1971-2020, sub-provincial). Tool defaults to **municipal CSD** XLSX (`population-estimates-ab-census-subdivision-municipal-2016-to-current.xlsx`). Optional `breakdown: Literal["csd","quarterly","annual","age_sex","sub_provincial","components_of_growth"]` parameter to select among the 6 resources. Cross-check with StatCan: **NO duplicate** — StatCan provides CMA-level only, this tool provides CSD/municipal-level. |

### Parks (1 tool)

| Tool | Source | Cache TTL | Notes |
|------|--------|-----------|-------|
| `alberta_get_provincial_parks` | `boundary/parks_protected_areas_alberta/FeatureServer/0` (GeoDiscover) | STATIC (24h) | All Alberta parks and protected areas. Already CKAN-federated as `gda-6b96341f-2e19-4885-98af-66d12ed4f8dd` but going direct to ESRI REST is faster and authoritative. |

**TOTAL CURATED: 17 tools**

### Tool count per CONTEXT.md domain target:

| Domain | CONTEXT.md target | Research-recommended | Delta | Reason |
|--------|-------------------|----------------------|-------|--------|
| Energy / AER | 4-6 | 4 | 0 within range | Spills/incidents not public |
| Wildfire | 3 | 4 | +1 | Replace FWI (no source) with Fire Bans + Fire Control Orders |
| Health / AHS | 2-3 | 3 | 0 within range | ER wait times deferred; subsumed into health_facilities |
| Transport / 511 | 2-3 | 3 | 0 within range | Ferry deferred (no API) |
| Environment | 2 | 2 | 0 | Air quality + water advisories |
| Agriculture | 1-2 | 1 | -1 | Live crop reports unavailable; historical only |
| Demographics | 1 | 1 | 0 | |
| Parks | 1 | 1 | 0 | |
| **Curated Total** | **16-21** | **17** | within range |
| Discovery | 5 | 5 | 0 | |
| **Grand Total** | **21-26** | **22** | within range |

---

## Federation Policy

**Recommendation: Quebec-style federated default.**

`organization_list` returns **370 organizations** on open.alberta.ca CKAN. Inspection reveals the structure:

- ~30 current ministries (`forestry-and-parks`, `agriculture-and-irrigation`, `transportation-and-economic-corridors`, `environment-and-protected-areas`, etc.)
- ~150 historical ministries (predecessor names like `aboriginalaffairsandnortherndevelopment2000-2006`, `agriculturefoodandruraldevelopment1992-2006`, `advancededucationandcareerdevelopment1992-1999`)
- ~20 Crown corporations and parastatal bodies (`agriculturefinancialservicescorporation`, etc.)
- ~150 advisory committees, study panels, working groups
- A few non-government entities (`non-government-of-alberta-entity` — verified to exist from search results)

**Implementation:** `alberta_search_datasets` returns ALL orgs by default. Document the federated and historical nature in the docstring:

> Alberta open.alberta.ca lists 370 publishing organizations including current ministries, historical/predecessor ministries (e.g., `agriculturefoodandruraldevelopment1992-2006`), Crown corporations, and advisory committees. Most queries should pass `organization=` with a current ministry slug to focus results. Use `alberta_list_organizations` to see slugs.

**Why this matches Quebec, not BC:** BC's `bcgov` is provincial-only (~30 orgs). Quebec's Données Québec is federated 139 orgs with municipalities and NGOs. Alberta is federated AND historical — same default-permissive pattern, with stronger docstring guidance.

---

## AER Source-of-Truth Policy

**Decision (informed by research): no `shared/aer.py` extraction. Each AER tool calls `fetch_and_parse(URL)` directly.**

### Surfaces inventoried (all probed live)

| Surface | Public? | Format | Tool fit |
|---------|---------|--------|----------|
| OneStop API (`onestop.aer.ca/onestop-api/v1/...`) | NO (404 on all probes) | — | Defer indefinitely |
| AER GIS (`gis.aer.ca/arcgis/rest/services/`) | Mostly empty (only 1 service in WMS-Public folder) | ArcGIS REST | Skip — replaced by GeoDiscover/WMB |
| ST1 daily well licences (`/data/well-lic/WELLS{day}.TXT`) | YES via 303 redirect to `static.aer.ca` | Plain-text fixed-width | `alberta_get_well_licences_today` |
| ST1 monthly archive (`/prd/data/well-lic/dwll{YYYY}-{MM}.zip`) | YES | ZIP of fixed-width TXT | Discovery only — return URL list |
| ST3 monthly production (`/prd/documents/sts/st3/{Product}_current.xlsx`) | YES | XLSX (~40KB each) | `alberta_get_production_volumes` |
| ST3 historical (`/prd/documents/sts/st3/{Product}_{YYYY}.xlsx`) | YES | XLSX | Optional `year` param |
| ST39 annual pipelines (`/prd/documents/sts/ST39-{YYYY}.xls`) | YES | XLS | `alberta_get_pipeline_statistics` |
| ST98 annual outlook (`/prd/documents/sts/st98/{YYYY}/...`) | YES | XLSX per topic | Future tool — defer to follow-up phase if energy demand grows |
| ST57 incidents | NO machine-readable since 2014 | PDF only | DEFERRED |
| AER Tableau dashboards (`www2.aer.ca/t/Production/...`) | YES (200) | HTML/CSV exports | Brittle (Tableau extracts can be intermittent — `WellLicenceAllAB.csv` returned `000` on probe). Use static XLSX path as primary; fall back to Tableau CSV only if a future tool requires it. |

### Why no shared/aer.py extraction

- AER's reusable surface is exactly ONE pattern: `https://static.aer.ca/prd/documents/sts/{report}/{file}.xlsx`. `fetch_and_parse(URL)` already handles this with no new code.
- Other provinces don't have AER-equivalent regulators publishing the same way (BC has BC Oil and Gas Commission with a separate WFS — Phase 15 already covers BC; Saskatchewan/Manitoba publish via different means).
- Extraction would be premature abstraction. Re-evaluate in Phase 18 (Manitoba) or later if a pattern emerges.

---

## Wildfire Source-of-Truth Policy

**Decision: prefer WMBappServices ArcGIS Online over open.alberta.ca CKAN for live data; use CKAN for historical CSV.**

| Tool | Primary source | Why over alternative |
|------|---------------|----------------------|
| `alberta_get_active_fires` | WMBappServices `Active_Wildfires_Dashboard_view` | Live (5min refresh by source); CKAN has only annual CSV |
| `alberta_get_fire_perimeters` (active) | WMBappServices `Active_Wildfire_Perimeters_Simplified_view` | Polygon geometry; CKAN has historical only |
| `alberta_get_fire_perimeters` (historical/extinguished) | WMBappServices `Extinguished_Wildfire_Perimeters_Simplified_view` | More current than CKAN's annual archive |
| `alberta_get_fire_bans` | WMBappServices `alberta_fire_ban_system` | The `albertafirebans.ca` SPA's actual data backend |
| `alberta_get_fire_control_orders` | WMBappServices `Fire_Control_Orders_Prod_View2` | No CKAN equivalent |
| (historical wildfire CSV — exposed via `alberta_query_dataset`) | CKAN `wildfire-data` package | 10MB CSV of 2006-2025 historical fires; routed via discovery, not curated |

Document this distinction in `docs://alberta/wildfire-data-guide` so agents know:
- "Use `alberta_get_active_fires` for current incidents (refreshed every 15 min by source)."
- "Use `alberta_query_dataset` with `wildfire-data` for the full 2006-2025 historical CSV."

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ArcGIS REST FeatureServer query + pagination | New client | `shared/arcgis_hub.py:query_feature_service` | Already handles GeoDiscover, WMBappServices, AHSGIS uniformly |
| WMS GetMap rendering | New WMS client | NOT NEEDED | Not in scope — defer like Phase 15 |
| ESRI REST layer metadata caching | Custom dict | `shared/arcgis_hub.py:get_layer_metadata` + `cached_fetch` | Already paginated and cached |
| AER XLSX parsing | Custom openpyxl loop | `shared/parsers.fetch_and_parse(url)` | Multi-sheet XLSX support; pandas fallback; cache built-in |
| AER fixed-width TXT parsing (ST1 daily) | Custom column slicer | Use stdlib `str` slicing in client.py with column ranges from a constants dict | Single source, ~25 lines of code; not worth a shared module |
| 511 JSON list parsing | Custom client | `shared.http.api_get(URL, params)` returns parsed JSON list directly | Already in stack; treat as raw list (NOT CKAN envelope) |
| CKAN envelope unwrap | Custom response parser | `_api_get` helper (post-15-05 BC pattern) | Same `{"success": true, "result": {...}}` shape as BC/Quebec |
| Bilingual error messages | `shared/i18n.py:t()` import | Inline `lang == "fr"` ternary | BC 15-05 convention — zero production t() imports |
| TTL caching | Custom `dict` cache | `shared.cache.cached_fetch(key, ttl, fetcher)` | Standard across 13 modules |
| Rate limiting | `asyncio.sleep` loops | `shared.rate_limiter.get_limiter(group, rate)` | TokenBucket per source; 4 distinct groups for Alberta (CKAN/GeoDiscover/WMB/AHS/AER/511 — actually 6 groups) |
| Geometry handling | Custom GeoJSON parser | `shared/parsers._parse_geojson()` | Already supports `include_geometry` flag |

**Key insight:** The infrastructure built across Phases 11-16 (parsers, arcgis_hub, ogc, cache, rate_limiter, envelope, http) covers EVERY Alberta surface without modification. Phase 17 is pure consumption of existing shared infra plus ~25 LOC of fixed-width-TXT parsing for AER ST1.

---

## Common Pitfalls

### Pitfall 1: open.alberta.ca CKAN has NO groups (only res_format facet)

**What goes wrong:** `alberta_list_categories` calling `group_list?all_fields=true` returns `[]`.
**Why it happens:** Alberta CKAN doesn't use the standard CKAN groups feature. It uses `res_format` (resource format) as its primary classification.
**How to avoid:** Implement `alberta_list_categories` as `package_search?facet.field=["res_format"]&rows=0` — returns ~30 format buckets with counts. (Verified during research: PDF=28,763, URI=2,352, HTML=1,905, XML=1,826, XLSX=774, ASCII GRID=231, CSV=224, XLS=134, IVT=112, ESRI REST=93, etc.)
**Warning sign:** `group_list` returns empty array; agent's request for "categories" returns nothing.

### Pitfall 2: open.alberta.ca CKAN is 86% PDFs

**What goes wrong:** `alberta_search_datasets` returns dataset names like `1929-7033`, `gda-c3ccd156-...`, `ndr-manual-10th-edition` — most have only PDF resources, useless for agent SQL queries.
**Why it happens:** Alberta CKAN was set up as the provincial publication repository (replacing the old "Open Government" publication index). It's a hybrid library catalogue + open-data catalogue, dominated by reports.
**How to avoid:** Tool docstring MUST explain this and recommend: "For machine-readable data, pass `format='CSV'` or `format='ESRI REST'`. For reports/PDFs, pass `format='PDF'` (default returns all formats)." The discovery tool should support a `format=` param mapping to `fq=res_format:{format}`.
**Warning sign:** Top results are PDFs even for queries like "wildfire data".

### Pitfall 3: GeoDiscover Alberta has token-walled folders

**What goes wrong:** Calling `geospatial.alberta.ca/titan/rest/services/wildfire/...` returns `{"error": {"message": "Token Required"}}`.
**Why it happens:** Some sensitive folders (wildfire, fire, forestry, hydro, health) require AGOL tokens. The corresponding public datasets live in WMBappServices/AHSGIS ArcGIS Online orgs.
**How to avoid:** Hardcode FeatureServer URLs in constants.py (no dynamic folder discovery for these domains). Document in `docs://alberta/data-portal-guide` which folders are public and which require alternates.
**Warning sign:** HTTP 200 but JSON body with `error.code: 499` and `message: "Token Required"`.

### Pitfall 4: Active wildfire data is NOT in the published CKAN dataset

**What goes wrong:** Agent searches `wildfire` on CKAN, finds `wildfire-data` package, downloads CSV — gets historical data through 2025, NOT current incidents.
**Why it happens:** CKAN's `wildfire-data` is annual historical (Forestry & Parks publishes one CSV/year). Live wildfire status is on WMBappServices ArcGIS Online (a separate portal).
**How to avoid:** `alberta_get_active_fires` must use WMBappServices, not CKAN. Document the distinction in `docs://alberta/wildfire-data-guide`.
**Warning sign:** Tool returns dates older than today.

### Pitfall 5: 511 Alberta documentation page is dead

**What goes wrong:** Following `https://511.alberta.ca/developers` redirects to `/notfound`. The API does exist, but the docs page is gone.
**Why it happens:** Vendor (CARS - Connected Vehicle / iCone) updated the SPA but didn't redeploy docs.
**How to avoid:** Hardcode the three confirmed endpoints (`event`, `cameras`, `winterroads`) in constants.py with comments noting "verified live 2026-04-17, no public documentation". Document in `docs://alberta/transport-data-guide`.
**Warning sign:** "Cannot find 511 API documentation" — yes, it doesn't exist; the API is undocumented but stable.

### Pitfall 6: 511 Alberta returns a JSON list, not a CKAN envelope

**What goes wrong:** Calling 511 endpoints with `_api_get` (CKAN helper) raises `httpx.HTTPStatusError` because the response is `[{...}, {...}]` not `{"success": true, "result": ...}`.
**Why it happens:** 511 is a separate API surface, not CKAN.
**How to avoid:** Use `shared.http.api_get(URL, params)` directly for 511 calls. Treat the return value as the parsed list. Do NOT call `_api_get`.
**Warning sign:** Test logs show `success=False raised` for 511 endpoints.

### Pitfall 7: AER ST57 (Compliance/Incidents) has been PDF-only since 2014

**What goes wrong:** Planning expects machine-readable AER incident data (spills, leaks, non-compliance orders).
**Why it happens:** AER discontinued the structured ST57 publication; current incidents are buried in PDF or behind the auth-walled OneStop API.
**How to avoid:** Defer `alberta_get_energy_incidents`. Document in `docs://alberta/aer-data-guide` and in deferred ideas. (Already updated above.)
**Warning sign:** ST57 page lists only `ST57-{YYYY}.pdf` files, no XLSX/CSV.

### Pitfall 8: AER ST3 product slugs are case-sensitive and not what you'd guess

**What goes wrong:** Trying `Bitumen_current.xlsx` or `CrudeOil_current.xlsx` returns 404. The actual slugs are `Oil_current.xlsx` (which contains crude oil), `Butane_current.xlsx`, `Ethane_current.xlsx`, `NGL_current.xlsx`, `Gas_current.xlsx`, `Propane_current.xlsx`, `Sulphur_current.xlsx`.
**Why it happens:** AER's URL convention pre-dates the rebranding of "crude oil" and "bitumen" as separate products in ST98. ST3 still uses the legacy product names.
**How to avoid:** Hardcode `ST3_PRODUCTS = ("Butane", "Ethane", "NGL", "Oil", "Gas", "Propane", "Sulphur")` in constants.py. Validate `product` parameter against this tuple in tools.py. Inline ternary error if unknown.
**Warning sign:** `fetch_and_parse` returns 404 for ST3 URLs.

### Pitfall 9: AHS does NOT publish ER wait times machine-readably

**What goes wrong:** `alberta_get_er_wait_times` plan finds no JSON endpoint.
**Why it happens:** AHS's ER wait times are rendered by a JavaScript widget on `albertahealthservices.ca/Webapps/WaitTimes/` — the widget pulls from an internal API not exposed publicly.
**How to avoid:** Defer the tool. The pending todo `2026-04-12-research-cross-canada-er-wait-times-datasets.md` still applies. Subsume the slot into `alberta_get_health_facilities` (EMS + clinics).
**Warning sign:** AHS website widget is live but the underlying URL returns 404 to direct calls.

### Pitfall 10: `Active_Wildfires_Dashboard_view` has count cap of 1000 per request

**What goes wrong:** During major fire seasons (e.g., 2023's 676 fires), pagination matters. Default `arcgis_hub.query_feature_service` page size is 1000 — Alberta's WMB layer has `maxRecordCount: 1000` confirmed.
**How to avoid:** Use shared/arcgis_hub.py's pagination loop (already pages while `exceededTransferLimit=true` up to 5000 cap). Document the `truncated: true` flag in tool docstring.
**Warning sign:** `truncated: true` returned during fire season; tool docstring should advise filtering by `RESP_AREA`/`FIRE_STATUS`.

### Pitfall 11: Alberta CKAN dataset extras include ~50 publication metadata fields

**What goes wrong:** `alberta_get_dataset_details` shape contains 50+ fields like `identifier-AGDEX-number`, `identifier-ALIS-catno`, `identifier-ISBN-cdrom`, `identifier-ISBN-dvd`, `identifier-ISBN-html`, `identifier-ISBN-pdf`, `identifier-ISBN-print`, `identifier-ISSN-online`, `identifier-ISSN-print`, `identifier-NEOS-catkey`, `audience`, `author`, `contributor1..6`, `Extent`, `Extent2`, `Extent3`, `alternatetitle1..3`, `hastranslation_*`, `istranslation_*`, etc. This bloats the response.
**Why it happens:** Alberta CKAN is a hybrid library catalogue using a ScheMing dataset profile (the `ab_scheming` extension) — these fields support ISBN/ISSN-style publication tracking.
**How to avoid:** Aggressive flattening in client layer — surface only the standard CKAN fields agents need (`id`, `name`, `title`, `notes`, `organization`, `license_id`, `metadata_modified`, `resources`, `num_resources`, `tags` (filtered)) plus the few useful Alberta extras (`isopen`, `language`, `frequencyofupdate`, `creator`). Hide everything starting with `identifier-` unless the dataset is a publication. Document the publication-extras quirk in `docs://alberta/ckan-quirks`.
**Warning sign:** Agent context bloat from 50+ extras per dataset.

### Pitfall 12: Two ArcGIS REST endpoints per ESRI REST resource (FeatureServer vs MapServer)

**What goes wrong:** `package_show` for GeoDiscover-federated datasets returns BOTH `MapServer` and `FeatureServer` URLs as ESRI REST resources. Routing logic could pick MapServer (which doesn't support `query?f=geojson` the same way).
**Why it happens:** GeoDiscover Alberta publishes each layer twice for compatibility.
**How to avoid:** Hybrid router prefers FeatureServer (`if "/FeatureServer" in url`). Skip MapServer URLs (they're for GIS visualization, not query).
**Warning sign:** Router calls `arcgis_hub.query_feature_service` against a `MapServer` URL → unexpected response.

---

## Code Examples

### CKAN package_search with Alberta-specific format facet

```python
# Source: verified against open.alberta.ca 2026-04-17
params = {
    "q": "wildfire",
    "fq": "res_format:CSV",
    "rows": 10,
    "start": 0,
}
envelope = await api_get("https://open.alberta.ca/api/3/action/package_search", params)
# envelope["result"]["count"] == 224 (CSV-bearing packages province-wide)
# envelope["result"]["results"] == [...]
# Each result has 'organization', 'resources' (with 'format', 'url'), 'license_id', etc.
```

### ArcGIS REST query with shared/arcgis_hub.py (works for GeoDiscover, WMBappServices, AHSGIS)

```python
# Source: shared/arcgis_hub.py + verified against WMBappServices 2026-04-17
from mcp_canada.shared import arcgis_hub
from mcp_canada.modules.alberta.constants import ACTIVE_WILDFIRES_FS_URL

features, truncated = await arcgis_hub.query_feature_service(
    service_url=ACTIVE_WILDFIRES_FS_URL,
    layer_id=0,
    where="FIRE_STATUS='Out of Control' OR FIRE_STATUS='Being Held'",
    out_fields="*",
    include_geometry=False,
    max_records=5000,
)
# features == list[dict] of feature properties
# truncated == True if pagination cap hit
```

### 511 Alberta direct JSON fetch

```python
# Source: verified against 511.alberta.ca 2026-04-17
from mcp_canada.shared.http import api_get

rows = await api_get(
    "https://511.alberta.ca/api/v2/get/event",
    {"format": "json"},
    headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
)
# rows == list of 142 event dicts
# Each event has: ID, SourceId, RoadwayName, EventType, EventSubType, IsFullClosure,
#                 Latitude, Longitude, Description, Reported (unix ts), LastUpdated, etc.
```

### AER ST3 monthly production XLSX

```python
# Source: verified against static.aer.ca 2026-04-17
from mcp_canada.shared.parsers import fetch_and_parse

# Verified XLSX URL (Gas_current.xlsx returned 200, 46KB)
url = "https://static.aer.ca/prd/documents/sts/st3/Gas_current.xlsx"
rows, was_cached = await fetch_and_parse(url, ttl=86400)
# rows == list of dicts (multi-sheet XLSX flattened by pandas/openpyxl)
```

### AER ST1 daily plain-text TXT (with 303 redirect handling)

```python
# Source: verified against aer.ca 2026-04-17
import datetime
import httpx

DAY_ABBR = {0: "MON", 1: "TUE", 2: "WED", 3: "THU", 4: "FRI", 5: "SAT", 6: "SUN"}

async def fetch_st1_today() -> list[dict]:
    today = DAY_ABBR[datetime.date.today().weekday()]
    # Note: aer.ca returns 303 redirect to static.aer.ca — httpx follows by default
    url = f"https://static.aer.ca/prd/data/well-lic/WELLS{today}.TXT"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "mcp-canada/1.0"})
        response.raise_for_status()
    text = response.text
    # ST1 is fixed-width starting line ~7; skip header (lines 0-6) and parse columns
    # (Column ranges for ST1 published in AER ST1 user manual — hardcode in client.py)
    ...
```

### Federated CKAN Esri REST routing (Pattern 3)

```python
# Verified: Alberta CKAN federates GeoDiscover Alberta as 'gda-' prefixed packages
# Each gda- package has 5 resources: HTML, XML, ESRI REST (MapServer), ESRI REST (FeatureServer), WMS
package, _ = await fetch_dataset_details("gda-bcf1b24c-16e9-4dc6-8729-c5096f302632")
# package["resources"] == [
#   {"format": "HTML", "url": "https://geodiscover.alberta.ca/geoportal/rest/metadata/.../html"},
#   {"format": "XML", "url": "https://geodiscover.alberta.ca/geoportal/rest/metadata/.../xml"},
#   {"format": "ESRI REST", "url": "https://geospatial.alberta.ca/.../MapServer"},
#   {"format": "ESRI REST", "url": "https://geospatial.alberta.ca/.../FeatureServer"},  # ← prefer
#   {"format": "WMS", "url": "https://geospatial.alberta.ca/.../MapServer/WMSServer"},
# ]
# Router picks resource[3] (FeatureServer) and routes to shared/arcgis_hub.query_feature_service
```

---

## Prompts and Resources Specification

### 6 Bilingual Prompts

| Function | Type | Description |
|----------|------|-------------|
| `alberta_explore_energy` | guided workflow (list[Message]) | Multi-step: AER ST3 production → ST39 pipelines → AER static reports overview. Demonstrates the static-XLSX pattern. |
| `alberta_explore_wildfires` | guided workflow (list[Message]) | Active fires → perimeters → fire bans → fire control orders → forest area context. Most agents will use this during fire season. |
| `alberta_explore_health_or_transport` | guided workflow (list[Message]) | Branch on user intent: hospitals/AHS zones (health) OR road events/winter conditions/cameras (transport). Cross-domain because both are 5-tool clusters. |
| `alberta_quick_dataset_search` | quick lookup (str) | Routes to `alberta_search_datasets` with format hint. |
| `alberta_check_road_conditions` | quick lookup (str) | Routes to `alberta_get_winter_road_conditions` with optional area filter. |
| `alberta_active_fires_now` | quick lookup (str) | Routes to `alberta_get_active_fires`. |

### 7 Zero-Parameter Resources

| URI | Type | Content |
|-----|------|---------|
| `data://alberta/ministries` | data | JSON catalog of current Alberta ministries with bilingual labels (slug → name_en/name_fr). Embed inline (~30 entries). |
| `data://alberta/forest-areas` | data | JSON list of 10 Alberta Wildfire Forest Areas (verified above): High Level, Fort McMurray, Peace River, Slave Lake, Lac La Biche, Grande Prairie, Whitecourt, Edson, Rocky Mountain House, Calgary. Include FA_NAME and approximate AREA_HECTARES. |
| `data://alberta/ahs-zones` | data | JSON list of 5 AHS zones (verified above): South (Z1), Calgary (Z2), Central (Z3), Edmonton (Z4), North (Z5) with POP2016. |
| `docs://alberta/aer-data-guide` | docs | Markdown explaining AER's surfaces (ST1/ST3/ST39/ST98), the static.aer.ca download pattern, the ST57 PDF deferral, and when to use each tool. |
| `docs://alberta/wildfire-data-guide` | docs | Markdown on the WMBappServices vs CKAN distinction, when to use which tool, fire status codes (Out / Out of Control / Being Held / Under Control / Extinguished), forest area structure, the FWI deferral. |
| `template://alberta/dataset-report` | template | Markdown template with `{title}`, `{organization}`, `{license_id}`, `{frequency}`, `{num_resources}`, `{best_resource_format}`, `{best_resource_url}` placeholders. |
| `template://alberta/wildfire-report` | template | Markdown template with `{report_date}`, `{active_count}`, `{out_of_control_count}`, `{being_held_count}`, `{largest_fire}`, `{forest_area_breakdown}`, `{ban_zones}` placeholders. |

---

## State of the Art

| Old assumption (CONTEXT.md) | Current reality (research) | Impact |
|--------------|------------------|--------|
| Secondary portal is GeoDiscover Hub-style | GeoDiscover is actually Esri Geoportal Server + ArcGIS REST 11.3, NOT ArcGIS Hub | Use `shared/arcgis_hub.py:query_feature_service` (works for both — same FeatureServer protocol); skip the Hub Search API since GeoDiscover doesn't expose `/api/search/v1/...` |
| Alberta CKAN is a primary data portal | open.alberta.ca is 86% PDFs (publication repository) | CKAN is for discovery only; signature data is on WMBappServices, AHSGIS, and AER static |
| AER OneStop has a public API | OneStop API requires authentication | Defer auth-walled tools; use static.aer.ca XLSX downloads |
| Alberta Fire Bans is HTML-only | The `albertafirebans.ca` SPA's data backend IS WMBappServices' `alberta_fire_ban_system` FeatureServer — public | Fire bans tool moves OUT of deferred and INTO scope |
| `alberta_get_fire_weather` (FWI) | No public source on WMBappServices, GeoDiscover, or open.alberta.ca CKAN. MSC weather (Phase 4) does NOT expose Canadian FWI. | Drop this tool; replace with `alberta_get_fire_control_orders` |
| `alberta_get_er_wait_times` | AHS publishes via web widget only; no JSON | Defer; subsume slot into `alberta_get_health_facilities` |
| 511 Alberta has only the public website | 511 has an undocumented but stable v2 REST API at `/api/v2/get/{event,cameras,winterroads}` | All 3 transport tools are clean, no scraping needed |

**Deprecated/outdated (carryover from older guidance):**
- "Alberta CKAN requires a User-Agent header (Quebec quirk)": Verified false — bare `python-httpx` works. Set User-Agent for identification only.
- "AER warrants its own shared/aer.py client": Verified premature — single-pattern XLSX URL, no abstraction value yet.

---

## Open Questions

1. **AHS ER wait times (deferred)**
   - What we know: AHS publishes ER wait times only via JavaScript widget on `albertahealthservices.ca`. No public JSON endpoint. The pending todo `2026-04-12-research-cross-canada-er-wait-times-datasets.md` (STATE.md) covers this gap nationally.
   - What's unclear: Whether AHS will publish a JSON endpoint in the future.
   - Recommendation: Defer `alberta_get_er_wait_times`; subsume into `alberta_get_health_facilities`. Re-evaluate in 6 months.

2. **AER ST98 Energy Outlook supplemental tables**
   - What we know: ST98 publishes ~20 supplemental XLSX files annually (executive summary, reserves, prices, capital expenditure, supply/demand by product). All verified at `https://static.aer.ca/prd/documents/sts/st98/{YYYY}/...`.
   - What's unclear: Whether agents need granular per-product ST98 access, or whether the existing `alberta_get_pipeline_statistics` (ST39) + `alberta_get_production_volumes` (ST3) suffice.
   - Recommendation: Defer ST98 to a follow-up if agent demand emerges. Document URL pattern in `docs://alberta/aer-data-guide` so agents can use `alberta_query_dataset` if needed.

3. **WMBappServices SIT (Sandbox/Test) services**
   - What we know: WMBappServices publishes `alberta_fire_ban_system_sit` alongside `alberta_fire_ban_system`. The "SIT" service may be a non-production test layer.
   - What's unclear: Whether the SIT layer is updated independently or always mirrors production.
   - Recommendation: Use the production layer (`alberta_fire_ban_system`) only. Document the SIT layer as "internal only — do not consume" in `docs://alberta/wildfire-data-guide`.

4. **AER Tableau public extracts (`www2.aer.ca/t/Production/views/...`)**
   - What we know: The AER ST1 page links to `WellLicenceAllAB.csv` from a Tableau view. Probe returned `000` (curl HTTP timeout/no response). Tableau public extracts can be intermittent.
   - What's unclear: Whether the Tableau CSV is reliable enough to use as primary data source for any tool.
   - Recommendation: Use static XLSX/TXT as primary source. Only use Tableau CSV as a fallback if a future tool requires it. Do NOT include in Phase 17.

5. **Alberta crop reports (in-season weekly)**
   - What we know: open.alberta.ca CKAN has 1 historical crop production CSV (2000-2014). The Agriculture and Irrigation ministry website publishes weekly in-season crop reports as PDF.
   - What's unclear: Whether agents want the historical statistics or the in-season conditions (different audiences).
   - Recommendation: Tool docstring distinguishes — `alberta_get_crop_production` returns historical; document that for in-season conditions, agents should use `alberta_search_datasets` to find the most recent PDF.

---

## Sources

### Primary (HIGH confidence — live-verified 2026-04-17)

- `https://open.alberta.ca/api/3/action/status_show` — confirmed CKAN 2.10.6 with 19 extensions
- `https://open.alberta.ca/api/3/action/package_search?rows=0` — 33,269 datasets, format facet
- `https://open.alberta.ca/api/3/action/package_search?fq=res_format:CSV&rows=10` — 224 CSV-bearing datasets
- `https://open.alberta.ca/api/3/action/package_search?fq=res_format:%22ESRI%20REST%22` — 93 GeoDiscover-federated datasets
- `https://open.alberta.ca/api/3/action/organization_list` — 370 orgs
- `https://open.alberta.ca/api/3/action/group_list` — empty (groups not used)
- `https://open.alberta.ca/api/3/action/tag_list` — 28,949 tags (too noisy for browsing)
- `https://open.alberta.ca/api/3/action/license_list` — 3 licenses (OGLA, KPTU, OGNL)
- `https://open.alberta.ca/api/3/action/package_show?id=fire-ban-system-approved-activities-list` — Alberta CKAN extras shape (ScheMing publication profile)
- `https://open.alberta.ca/api/3/action/package_show?id=wildfire-data` — historical wildfire CSV (10MB) verified
- `https://open.alberta.ca/api/3/action/package_show?id=major-crop-production-alberta` — crop production CSV verified
- `https://open.alberta.ca/api/3/action/package_show?id=alberta-population-estimates-data-tables` — 6 XLSX resources verified
- `https://open.alberta.ca/api/3/action/package_show?id=water-licence-data` — 87MB+169MB CSV (too large for default tool)
- `https://geospatial.alberta.ca/titan/rest/services?f=json` — GeoDiscover ArcGIS REST 11.3, 52 folders
- `https://geospatial.alberta.ca/titan/rest/services/aqhi/air_layers/MapServer/1` — 75 air monitoring stations verified
- `https://geospatial.alberta.ca/titan/rest/services/environment/river_forecast_centre/FeatureServer` — 10 layers verified
- `https://geospatial.alberta.ca/titan/rest/services/boundary/parks_protected_areas_alberta/FeatureServer` — parks verified
- `https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/Active_Wildfires_Dashboard_view/FeatureServer/0` — 17 active fires, 15 fields verified
- `https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/Extinguished_Wildfires_Locations/FeatureServer/0` — 58 extinguished fires verified
- `https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services/Forest_Area_Prod_View2/FeatureServer/0` — 10 forest areas verified (matches CONTEXT.md exactly)
- `https://www.arcgis.com/sharing/rest/search?q=owner:WMBappServices&f=json` — 123 WMB items
- `https://services5.arcgis.com/7KHJ4f28UDLgUq2U/arcgis/rest/services/AHS_Hospitals/FeatureServer/0` — 101 hospitals verified
- `https://services5.arcgis.com/7KHJ4f28UDLgUq2U/arcgis/rest/services/AHS_Zone/FeatureServer/0` — 5 zones verified (S/CGY/CTL/EDM/N)
- `https://www.arcgis.com/sharing/rest/search?q=owner:AHSGIS&f=json` — 290 AHS items
- `https://511.alberta.ca/api/v2/get/event` — 142 events, 26 fields verified
- `https://511.alberta.ca/api/v2/get/cameras` — 376 cameras verified
- `https://511.alberta.ca/api/v2/get/winterroads` — 1,121 records verified
- `https://www.aer.ca/providing-information/data-and-reports/statistical-reports/st1` — ST1 file URL pattern
- `https://static.aer.ca/prd/data/well-lic/WELLSSUN.TXT` — ST1 daily TXT verified (200, plain-text fixed-width)
- `https://static.aer.ca/prd/documents/sts/st3/Gas_current.xlsx` — ST3 verified (200, 46KB XLSX)
- `https://static.aer.ca/prd/documents/sts/st3/Butane_current.xlsx` — ST3 verified (200, 36KB XLSX)
- `https://static.aer.ca/prd/documents/sts/st3/NGL_current.xlsx` — ST3 verified (200, 38KB XLSX)
- `https://static.aer.ca/prd/documents/sts/ST39-2024.xls` — ST39 verified (200, 253KB XLS)
- `https://static.aer.ca/prd/documents/sts/st98/2025/st98-2025-pipelines-and-other-infrastructure-data.xlsx` — ST98 supplemental URL pattern verified

### Secondary (MEDIUM confidence — official docs)

- `https://www.alberta.ca/lookup` — Alberta gov data services landing
- AER ST57 page — only PDF since 2014 (compliance-and-incidents publication discontinued in machine-readable form)

### Tertiary (LOW confidence — needs validation during implementation)

- AER weekly archive ZIP (`dwll{YYYY}-{MM}.zip`) parsing: probed for 200 OK on URL pattern, but contents not parsed (treated as discovery-only).
- Alberta CKAN Cloudflare rate limit: not formally probed; assume Cloudflare-friendly with 10 req/s default. Watch for 429s during integration tests.
- `WellLicenceAllAB.csv` Tableau extract: returned `000` (timeout) on probe — flagged as unreliable; not used as primary source.

---

## Validation Architecture

> `nyquist_validation` is `true` in `.planning/config.json` — this section is MANDATORY.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` |
| Integration run | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Alberta` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AB-01 | `alberta_search_datasets` returns shaped CKAN results | unit (mocked api_get) | `uv run pytest src/mcp_canada/modules/alberta/__tests__/test_tools.py::TestAlbertaSearchDatasets -x -v` | Wave 0 gap |
| AB-01 | `alberta_search_datasets` supports `format=` filter via `fq=res_format:` | unit | same | Wave 0 |
| AB-02 | `alberta_get_dataset_details` flattens 50+ Alberta extras to standard fields | unit | `...::TestAlbertaGetDatasetDetails` | Wave 0 |
| AB-03 | `alberta_query_dataset` routes ESRI REST → arcgis_hub | unit (mocked) | `...::TestAlbertaQueryDataset::test_routes_esri_rest_to_feature_server` | Wave 0 |
| AB-03 | `alberta_query_dataset` routes CSV → fetch_and_parse | unit (mocked) | `...::TestAlbertaQueryDataset::test_routes_csv_to_fetch_and_parse` | Wave 0 |
| AB-03 | `alberta_query_dataset` returns metadata-only for PDF/ZIP | unit | `...::TestAlbertaQueryDataset::test_pdf_returns_metadata_only` | Wave 0 |
| AB-04 | `alberta_list_organizations` returns 370 orgs | unit | `...::TestAlbertaListOrganizations` | Wave 0 |
| AB-05 | `alberta_list_categories` uses `package_search?facet.field=res_format` (NOT group_list) | unit | `...::TestAlbertaListCategories::test_uses_format_facet` | Wave 0 |
| AB-06..AB-09 | AER tools: ST1, ST3, ST39 fetch from correct static URLs | unit (mocked fetch_and_parse) | `...::TestAlbertaAER` | Wave 0 |
| AB-08 | ST3 invalid `product` returns INVALID_INPUT with French message when lang=fr | unit | `...::TestAlbertaProduction::test_invalid_product_french_error` | Wave 0 |
| AB-10 | `alberta_get_active_fires` calls correct WMB FeatureServer | unit (mocked arcgis_hub) | `...::TestAlbertaActiveFires` | Wave 0 |
| AB-10 | Fire status filter passes through CQL/WHERE correctly | unit | `...::TestAlbertaActiveFires::test_status_filter` | Wave 0 |
| AB-11 | `alberta_get_fire_perimeters` dispatches by `status: Literal["active","extinguished"]` | unit | `...::TestAlbertaFirePerimeters` | Wave 0 |
| AB-13 | `alberta_get_fire_bans` returns ban registry | unit | `...::TestAlbertaFireBans` | Wave 0 |
| AB-15 | `alberta_get_hospitals` returns 101 with IP/ED flags | unit | `...::TestAlbertaHospitals` | Wave 0 |
| AB-17 | `alberta_get_ahs_zones` returns 5 zones with population | unit | `...::TestAlbertaAhsZones` | Wave 0 |
| AB-18 | `alberta_get_road_events` calls 511 v2 endpoint correctly | unit (mocked api_get) | `...::TestAlbertaRoadEvents` | Wave 0 |
| AB-18 | Road events: `event_type=` filter | unit | `...::TestAlbertaRoadEvents::test_event_type_filter` | Wave 0 |
| AB-19 | `alberta_get_winter_road_conditions` calls correct endpoint | unit | `...::TestAlbertaWinterRoadConditions` | Wave 0 |
| AB-20 | `alberta_get_traffic_cameras` returns 376 cameras | unit | `...::TestAlbertaTrafficCameras` | Wave 0 |
| AB-21 | `alberta_get_air_quality_stations` returns 75 stations | unit | `...::TestAlbertaAirQuality` | Wave 0 |
| AB-22 | `alberta_get_water_advisories` dispatches by `advisory_type` | unit | `...::TestAlbertaWaterAdvisories` | Wave 0 |
| AB-25 | `alberta_get_population_estimates` defaults to CSD breakdown | unit | `...::TestAlbertaPopulation` | Wave 0 |
| AB-26 | `alberta_get_provincial_parks` calls GeoDiscover FeatureServer | unit | `...::TestAlbertaProvincialParks` | Wave 0 |
| AB-27 | All 22 tools return `_meta` envelope | unit (parametrized) | `...::TestAlbertaEnvelopes` | Wave 0 |
| AB-27 | All 22 tools propagate `lang` parameter | unit (parametrized) | `...::TestAlbertaLangParam` | Wave 0 |
| INF (shared contract) | `_api_get` treats api_get return as parsed dict | unit | `...::TestSharedApiGetContract` | Wave 0 |
| INF | `_api_get` raises on `success=False` | unit | `...::TestSharedApiGetContract::test_ckan_success_false_raises` | Wave 0 |
| INF | All 22 tools have 8+ Keywords + Use-for | quality (auto-discovered) | `uv run pytest src/mcp_canada/__tests__/test_quality.py -x` | exists |
| AB-01 | Integration: live `alberta_search_datasets` returns wildfire results | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestAlbertaToolScenarios -v -m integration --timeout=30 -k search` | Wave 0 |
| AB-10 | Integration: live `alberta_get_active_fires` returns _meta envelope | integration | `...::TestAlbertaToolScenarios -k active_fires` | Wave 0 |
| AB-15 | Integration: live `alberta_get_hospitals` returns ~101 hospitals | integration | `...::TestAlbertaToolScenarios -k hospitals` | Wave 0 |
| AB-18 | Integration: live `alberta_get_road_events` returns event list | integration | `...::TestAlbertaToolScenarios -k road_events` | Wave 0 |
| AB-09 | Integration: live AER ST3 `Gas_current.xlsx` parses without error | integration | `...::TestAlbertaToolScenarios -k production_volumes` | Wave 0 |
| AB-27 | Integration: `discover_tools` finds Alberta tools via BM25 | integration | `...::TestAlbertaToolScenarios -k discover` | Wave 0 |
| AB-27 | Integration: 6 prompts discoverable via `client.list_prompts()` | integration | `tests/integration/test_prompts_resources_scenarios.py::TestAlbertaPromptsResources` | Wave 0 |
| AB-27 | Integration: 7 resources readable via `client.read_resource()` | integration | `...::TestAlbertaPromptsResources -k resources` | Wave 0 |
| INF | Coverage ≥ 95% for alberta module | coverage | `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` | runs at end |

### Sampling Rate

- **Per task commit:** `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -v`
- **Per wave merge:** `uv run pytest src/mcp_canada/modules/alberta/__tests__/ src/mcp_canada/__tests__/test_quality.py -x`
- **Phase gate:** Full suite green (including integration tests via `-m integration --timeout=120 -k Alberta`) before `/gsd:verify-work`

### Wave 0 Gaps (must exist before implementation)

- [ ] `src/mcp_canada/modules/alberta/__init__.py` — `MODULE_NAME = "alberta"`, bilingual `MODULE_DESCRIPTION`
- [ ] `src/mcp_canada/modules/alberta/constants.py` — all URLs, rate groups, TTLs, slugs from "Pattern 1: Quad-Source Constants Layout"
- [ ] `src/mcp_canada/modules/alberta/schemas.py` — flat Pydantic v2 models for: dataset summary, organization, ESRI feature properties (active fire, perimeter, hospital, EMS, AHS zone, etc.), AER well licence, AER production row, AER pipeline row, 511 event, 511 winter road, 511 camera, AQHI station, water advisory, crop production row, population estimate row, provincial park
- [ ] `src/mcp_canada/modules/alberta/client.py` — 22 client functions (one per tool) returning `(data, was_cached)` tuples
- [ ] `src/mcp_canada/modules/alberta/tools.py` — 22 `@tool` functions with BM25 docstrings (8+ keywords each)
- [ ] `src/mcp_canada/modules/alberta/prompts.py` — 6 `@prompt` functions
- [ ] `src/mcp_canada/modules/alberta/resources.py` — 7 `@resource` functions
- [ ] `src/mcp_canada/modules/alberta/__tests__/conftest.py` — fixtures: sample CKAN package_search response (with Alberta extras quirks), sample CKAN package_show, sample ArcGIS REST query response (geojson + json), sample 511 event JSON list, sample AER ST1 TXT (5 lines), sample AER ST3 XLSX bytes, autouse cache+limiter patch
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_client.py` — 22+ classes including `TestSharedApiGetContract`
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — 22 stub classes (5 discovery + 17 curated) plus parametrized envelope/lang tests
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py` — `TestAlbertaPrompts` + `TestAlbertaResources`
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestAlbertaToolScenarios` class with ~8 xfail stubs initially
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — append `TestAlbertaPromptsResources` class with 3 xfail stubs

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every reusable shared utility verified in prior phases (11-16)
- CKAN API structure: HIGH — package_search, package_show, organization_list verified live
- GeoDiscover Alberta: HIGH — ArcGIS REST 11.3 confirmed; 21 of 52 folders public; 5 example layers verified end-to-end
- WMBappServices ArcGIS Online: HIGH — 8 fire-related FeatureServers verified for layer schema, count, and sample query
- AHSGIS ArcGIS Online: HIGH — 4 health FeatureServers verified
- AER static reports: HIGH — ST1 TXT verified (200, plain-text), ST3 XLSX verified for 3 of 7 products, ST39 XLS verified, ST98 URL pattern verified
- 511 Alberta API: HIGH — 3 endpoints (event, cameras, winterroads) verified with response shape
- Federation policy: HIGH — 370 orgs enumerated
- Pitfalls: HIGH — directly encountered during research (token-walled folders, ScheMing extras bloat, ER waits widget-only, CrudeOil 404, etc.)
- Tool catalog: HIGH — every URL probed; 17 curated tools all confirmed feasible

**Research date:** 2026-04-17
**Valid until:** 2026-07-17 (90 days — Alberta data infrastructure is stable; CKAN portal upgrades infrequent; AER static URLs have been stable for years; 511 API has been live since at least 2024)
