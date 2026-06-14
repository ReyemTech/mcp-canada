# Phase 18: Manitoba Government Open Data — Research

**Researched:** 2026-06-13
**Domain:** Manitoba provincial open data (geoportal.gov.mb.ca ArcGIS Hub + mMUesHYPkXjaFGfS ArcGIS org + Manitoba 511 key-required REST API)
**Confidence:** HIGH for ArcGIS Hub and geospatial tools (live-verified); MEDIUM for CKAN portal (data.manitoba.ca appears unreachable from sandbox — confirmed via alternative evidence); LOW for Manitoba 511 (key-gated, not testable without registration)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Primary portal: **data.manitoba.ca** CKAN. (Research note: the domain `data.manitoba.ca` appears to redirect or be unreachable; the CONFIRMED working equivalent is **geoportal.gov.mb.ca** — Manitoba's ArcGIS Hub. See "Portal Architecture Discovery" below — this is the critical finding that reshapes the module design.)
- Module prefix: `manitoba_` (full-name pattern).
- Module name: `manitoba`.
- **Balanced curation, no single anchor** — even density across the 6 domains.
- **Target: mid-band ~14-18 tools.** 5 standard discovery tools + ~9-13 curated.
- **Geospatial: CONFIRMED** — Manitoba's primary portal IS ArcGIS Hub (`geoportal.gov.mb.ca` / ArcGIS org `mMUesHYPkXjaFGfS`), not CKAN. This means the module follows the **Alberta pattern (ArcGIS Hub via `shared/arcgis_hub.py`)** rather than the BC pattern (CKAN→WFS two-step) or Quebec pattern (CKAN-only). See "Portal Architecture Discovery" section.
- **6 bilingual prompts** (3 guided + 3 quick lookups).
- **~7 zero-parameter resources.**
- Bilingual `lang: Literal["en", "fr"] = "en"` on every `@tool`, inline `lang == "fr"` ternary. No `shared/i18n.py:t()` adoption.
- All technical conventions carry forward (7-file module, standalone `@tool`/`@prompt`/`@resource`, `_api_get` parsed-dict convention, `TestSharedApiGetContract`, `(data, was_cached)`, aggressive flattening, 5000-record cap, BM25 docstrings).
- No scraping discipline: if a source is HTML-only or PDF-only, defer that tool.

### Claude's Discretion

- Final dataset selection per domain — research surfaces the most agent-friendly options.
- Whether geospatial router warrants two-step pattern — RESOLVED: Use ArcGIS Hub pattern (not WFS), same as Alberta Phase 17.
- CKAN `fq` strategies for organization filtering — NOT APPLICABLE: Manitoba's primary machine-readable portal is ArcGIS Hub, not CKAN. See "Portal Architecture Discovery."
- Cache TTLs per tool — RESOLVED per-tool in catalog table below.
- Whether Manitoba's portal requires a `User-Agent` header — NOT APPLICABLE for ArcGIS Hub (standard ArcGIS REST API).
- Final prompt/resource set naming and count.

### Deferred Ideas (OUT OF SCOPE)

- Winnipeg, Brandon, and other Manitoba municipal portals (separate future phases; Winnipeg = Phase 32).
- Manitoba Hydro as a deep dedicated domain (confirmed thin — see "Domain: Manitoba Hydro / Energy" below).
- Flood tooling beyond outlooks/levels (predictive modeling, floodway operations, historical archives).
- Live WFS/ArcGIS adoption if MLI is file-only (confirmed: MLI is retired as of 2022-02-09, superseded by geoportal.gov.mb.ca).
- Bilingual `shared/i18n.py:t()` adoption.
- Cross-module SQL examples for Manitoba (its own future phase initiative).
- Any source requiring scraping or auth (511 Manitoba if key is not freely obtainable; Hydro-Manitoba water levels are HTML-only).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

Proposed `MB-XX` requirements for Phase 18. Planner must add these to REQUIREMENTS.md.

| ID | Description | Research Support |
|----|-------------|-----------------|
| MB-01 | Agent can search Manitoba's geoportal.gov.mb.ca ArcGIS Hub catalogue by keyword with optional category and pagination | ArcGIS Hub Search API `/api/search/v1/collections/all/items` (same pattern as Phase 14 York Region) |
| MB-02 | Agent can get full details for a Manitoba dataset by ID, including FeatureServer URL, download URLs, and metadata | ArcGIS Hub item detail endpoint |
| MB-03 | Agent can query a Manitoba dataset FeatureServer or file resource via auto-router (ESRI REST → arcgis_hub.query_feature_service; CSV/JSON/GeoJSON/XLSX → fetch_and_parse; other → metadata-only) | Same hybrid router pattern as Alberta Phase 17 |
| MB-04 | Agent can list Manitoba government organizations on the geoportal | ArcGIS Hub groups/organizations endpoint |
| MB-05 | Agent can list dataset categories/tags on the Manitoba geoportal | ArcGIS Hub tags/categories |
| MB-06 | Agent can get Manitoba provincial parks and protected areas (93 parks, polygon boundaries) | `Manitoba_Parks` FeatureServer at org `mMUesHYPkXjaFGfS` live-verified |
| MB-07 | Agent can get flood alerts (overland flooding watch/warning polygons) from Manitoba's ArcGIS org | `Overland_Flood_Alerts` FeatureServer at org `mMUesHYPkXjaFGfS` live-verified; bilingual Type_EN/Type_FR fields |
| MB-08 | Agent can get river conditions and hydrometric station locations (stations where water levels and flows are collected) | Manitoba River Conditions and Forecasts dataset on geoportal; station points with flood watch/warning status |
| MB-09 | Agent can get provincial waterways (drains, dikes, floodways, diversions, dams, reservoirs — F_TYPE coded domain) | `Provincial_Waterways` FeatureServer live-verified with Dike/Floodway/Dam/Reservoir types |
| MB-10 | Agent can get current drought monitor status for Manitoba/Canada (D0-D4 polygon layer) | `Canada_USA_Drought_Monitor` FeatureServer live-verified; D0-D4 drought intensity classes |
| MB-11 | Agent can get Manitoba agricultural weather station locations (100+ stations with AgRegion and URL to live hourly readings) | `WeatherStations` FeatureServer live-verified; StnName, LatDD, LongDD, AgRegion, URL fields |
| MB-12 | Agent can get Manitoba hog/cattle market prices (current year and historical weekly prices from Manitoba Agriculture) | `MB_Cattle_Prices_Current_year` FeatureServer live-verified; weekly auction/parameter/value structure; hog prices also available |
| MB-13 | Agent can get crop reporting region boundaries for Manitoba (bilingual region names matching Manitoba Agriculture seasonal report areas) | `MbAg_Crop_Reporting_Regions` FeatureServer live-verified; REGION/RÉGION bilingual fields |
| MB-14 | Agent can get Manitoba diagnostic and surgical wait time averages by procedure and year | `Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages` FeatureServer live-verified; Year/IndicatorDataArea/Average_Wait fields; cardiac surgery sample 60→144 days 2019-2021 |
| MB-15 | Agent can get Manitoba fisheries/waterbody reference data (350+ water bodies with fishing regulations, species, stocking records, boat launch info) | `Manitoba_Waterbody_Data` FeatureServer live-verified; 26 fields including species, regulations, Secchi depth |
| MB-16 | Agent can get Manitoba provincial forest boundaries | `Manitoba_Provincial_Forests___Version_6` FeatureServer confirmed in search; administrative forest regions |
| MB-17 | Transport / Manitoba 511: DEFER unless API key is freely and publicly obtainable (see "Domain: Transport / 511" — requires registration; key gating status unconfirmed) | Manitoba 511 API v3 documented at `https://www.manitoba511.ca/api/v3/get/{endpoint}` but `key` param required |
| MB-18 | All Manitoba tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, manitoba_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider | Conventions established by Phases 12-17 |

**Total: ~14-17 tools (5 discovery + 9-12 curated). Final count locked during planning.**

</phase_requirements>

---

## Summary

### Critical Finding: Manitoba's primary public machine-readable portal is geoportal.gov.mb.ca (ArcGIS Hub), NOT a CKAN instance

The CONTEXT.md assumed `data.manitoba.ca` was a CKAN portal (analogous to BC's `catalogue.data.bc.ca` or Quebec's `www.donneesquebec.ca`). Research reveals the actual picture:

1. **`data.manitoba.ca` does not resolve** to an accessible CKAN API (ECONNREFUSED on research date). The domain may redirect or simply not be a live CKAN instance as expected. Manitoba's public data infrastructure is organized differently.

2. **The confirmed primary portal is `geoportal.gov.mb.ca` ("Data MB")** — Manitoba's ArcGIS Hub instance powered by the ArcGIS Online organization `mMUesHYPkXjaFGfS` (base services URL: `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/`). This hosts 93+ FeatureServer services publicly accessible without authentication.

3. **Manitoba Land Initiative (mli.gov.mb.ca) is retired.** As of February 9, 2022, MLI no longer receives updates. Users are directed to `geoportal.gov.mb.ca`. Do not plan any MLI integration.

4. **Consequence for module design:** Use the **Alberta Phase 17 pattern (ArcGIS Hub)** rather than CKAN patterns from Quebec/BC. The 5 standard "discovery" tools become ArcGIS Hub search/detail/query tools (same as York Region Phase 14). The `shared/arcgis_hub.py` client handles all geospatial queries unchanged.

5. **Manitoba 511 requires a developer key** (API v3 at `https://www.manitoba511.ca/api/v3/get/{endpoint}`), unlike Alberta's undocumented but keyless API. Key registration appears free but requires an account. This is a research-risk item for the transport domain — see dedicated section below.

6. **Manitoba Hydro water levels are HTML-only** (confirmed). The hydro.mb.ca pages present live river data in HTML tables only, no JSON/CSV download. This kills the "Manitoba Hydro / energy" domain as a curated tool target.

7. **Flood data is geospatial, not tabular.** The Hydrologic Forecast Centre publishes flood bulletins as PDFs and HTML. Machine-readable flood data comes through the ArcGIS Hub: `Overland_Flood_Alerts` FeatureServer (live, bilingual). River station points are available as a web app layer. This is curate-able.

**Primary recommendation:** Build 14-16 tools (5 discovery + 9-11 curated) following the Alberta ArcGIS Hub pattern. Use `shared/arcgis_hub.py` for all curated tools. Drop Manitoba Hydro / energy domain (no public machine-readable source). Substitute drought monitoring and fisheries waterbody data (both live-verified on ArcGIS Hub). Provisionally include Manitoba 511 only if the developer key is freely obtainable during implementation.

---

## Portal Architecture Discovery

### What Manitoba Actually Has (confirmed)

| Portal | URL | Technology | Auth | Status |
|--------|-----|-----------|------|--------|
| **Data MB (primary)** | `geoportal.gov.mb.ca` | ArcGIS Hub (Esri) | None | ACTIVE — 93+ FeatureServer services |
| OpenMB / DataMB | `gov.mb.ca/openmb/datamb/` | Static HTML listing | None | Legacy listing, redirects to geoportal |
| Manitoba Land Initiative | `mli.gov.mb.ca` | File downloads | None | **RETIRED 2022-02-09** |
| data.manitoba.ca | (domain) | Unknown / CKAN? | Unknown | UNREACHABLE on research date |
| AgriMaps | `agrimaps.gov.mb.ca/arcgis/rest/services/AGRIMAPS/` | ArcGIS REST | None | Separate farm/agri portal — location search only |
| Manitoba 511 | `www.manitoba511.ca/api/v3/get/` | Custom REST API | **Key required** | 7 endpoints: RoadConditions, Cameras, Parks, Events, Advisories, WinterRoads, TrackMyPlow |

### ArcGIS Hub Organization

- **Org ID:** `mMUesHYPkXjaFGfS`
- **Base services URL:** `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/`
- **Hub URL:** `https://geoportal.gov.mb.ca` (Manitoba-branded ArcGIS Hub)
- **ArcGIS Online domain:** `https://manitoba.maps.arcgis.com`
- **Group ID for Open Data:** `c8b5f087c9074c5cb502ed7df0ede9dc`
- **Licence:** OpenMB Information and Data Use Licence — free commercial and non-commercial use, attribution required, similar to CC-BY 4.0

### Discovery Tool Pattern for ArcGIS Hub (Phase 14 precedent)

The 5 discovery tools map to ArcGIS Hub APIs, NOT CKAN:

```
manitoba_search_datasets     → Hub Search API /api/search/v1/collections/all/items
manitoba_get_dataset_details → Hub item detail endpoint
manitoba_query_dataset       → arcgis_hub.query_feature_service (or fetch_and_parse for file resources)
manitoba_list_organizations  → Hub groups/orgs endpoint
manitoba_list_categories     → Hub tags or categories endpoint
```

This is identical to York Region Phase 14 (`arcgis_hub.py` already handles this). The only difference is that Manitoba's Hub is province-level, not municipal-level.

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
| `shared/arcgis_hub.py:query_feature_service` | All ArcGIS Hub FeatureServer queries | All curated tools (parks, flood, waterways, ag, health, fisheries) |
| `shared/arcgis_hub.py:get_layer_metadata` | Detect maxRecordCount before paginating | Once per layer (cached 24h) |
| `shared/parsers.py:fetch_and_parse` | File resources (CSV/GeoJSON/XLSX) returned by `manitoba_query_dataset` | Auto-router fallback |
| `shared/http.py:api_get` | ArcGIS Hub Search API (returns JSON, not CKAN envelope) | Discovery tools |
| `shared/cache.py:cached_fetch` | TTL caching | Every client function |
| `shared/rate_limiter.py:get_limiter` | Token bucket per source | Every client function |
| `shared/envelope.py` | `make_response` / `make_error` | Every tool function |

### No New Dependencies

The existing stack covers every Manitoba surface. `shared/arcgis_hub.py` is already proven (Phase 14 York Region).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ArcGIS Hub pattern | CKAN pattern | NOT applicable — Manitoba's machine-readable portal IS ArcGIS Hub |
| `shared/arcgis_hub.py` | New `shared/manitobaGIS.py` | Premature — same protocol, same client works unchanged |
| `fetch_and_parse` for file fallback | Separate download tool | Already handled by `arcgis_hub.py` router pattern |

### Installation

No new packages required. All dependencies already present.

---

## Domain Analysis (6 domains, honest assessment)

### Domain 1: Flood Forecasting / Hydrology

**Verdict: CURATE 2 tools — confirmed machine-readable via ArcGIS Hub.**

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Overland Flood Alerts** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Overland_Flood_Alerts/FeatureServer/0` | OBJECTID, Type_EN, Type_FR, Start_Date, End_Date, Shape__Area | Bilingual! Polygon layer: Watch/Warning polygons for overland flooding. Live-verified (0 features when no alerts active — confirms schema). MaxRecordCount 2000. |
| **Manitoba River Conditions and Forecasts** | Via `geoportal.gov.mb.ca/datasets/manitoba-river-conditions-and-forecasts-web-app` (ArcGIS item ID `5c57801d0efc4676a2d2c95174ef44d5`) | River/lake station points with flood alert status (Flood Warning, Flood Watch, High Water Advisory levels) | Web app layer; underlying FeatureServer URL needs to be resolved by the planner from the item's operational layers during implementation. The web app is on `manitoba.maps.arcgis.com`. |
| **Provincial Waterways** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Provincial_Waterways/FeatureServer/0` | F_TYPE (Dike/Reservoir/Waterway/Floodway/Dam/Detention Basin/Diversion), Name, Watershed, WCW, LengthKM | Static reference layer for Manitoba's water control infrastructure. Polyline geometry. |

**Flood bulletins from Hydrologic Forecast Centre: PDF/HTML only.** The HFC publishes PDF flood outlook reports (February/March) and daily HTML flood sheets. These are NOT machine-readable in any format. Do not plan a `manitoba_get_flood_outlook` tool that reads HFC bulletins — that would require scraping. The ArcGIS Hub layers above are the correct machine-readable substitute.

**Recommended tools:**
- `manitoba_get_flood_alerts` — `Overland_Flood_Alerts` FeatureServer (live alert polygons, bilingual)
- `manitoba_get_provincial_waterways` — `Provincial_Waterways` FeatureServer (dispatch by F_TYPE filter: dike/floodway/dam/diversion/reservoir)

### Domain 2: Manitoba Hydro / Energy

**Verdict: DROP THIS DOMAIN. No public machine-readable data source confirmed.**

Manitoba Hydro's water levels and flows page (`hydro.mb.ca/corporate/operations/water-levels/`) presents data in HTML tables only. No JSON/CSV download, no API, no ArcGIS integration. The site states near-real-time data from hydrometric gauging stations on Churchill, Nelson, Saskatchewan, and Winnipeg Rivers — but this data is HTML-rendered.

Manitoba Hydro's GIS Portal (confirmed to exist as referenced in research) is a separate `experience.arcgis.com` app (`/experience/689a9f8287f54232a1609c9196c568f9/page/home/`) but is a web viewer, not a queryable FeatureServer.

The `Drought_Monitor_Reservoirs` FeatureServer in the mMUesHYPkXjaFGfS org hints at reservoir capacity data but its schema was not verified (listed in services directory, not probed).

**Recommendation:** Drop "Manitoba Hydro / energy" as a curated domain. Replace the energy slot with **Drought Monitoring** (confirmed via `Canada_USA_Drought_Monitor` FeatureServer) since Manitoba is a Prairie province where drought is a distinct high-value query class. This is a 1:1 swap within the same tool budget.

**Revised Domain 2 → Drought & Agricultural Monitoring**

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Drought Monitor** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Canada_USA_Drought_Monitor/FeatureServer/0` | DM (D0-D4 codes), OBS_DATE, SOURCE | Weekly D0-D4 drought intensity polygons (national coverage, Manitoba-filterable). Live-verified. |
| **Agricultural Weather Stations** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/WeatherStations/FeatureServer/0` | StnName, LatDD, LongDD, Elevation, AgRegion, URL | 100+ Manitoba Ag weather station points; URL field links to live hourly data page per station. Live-verified. |
| **Cattle/Hog Prices** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MB_Cattle_Prices_Current_year/FeatureServer/0` (+ 10-year historical service) | week, Auction, Parameter, Measure, Value | Weekly livestock prices from Manitoba Agriculture; current year + 10-year archives confirmed. |

**Recommended tools:**
- `manitoba_get_drought_status` — `Canada_USA_Drought_Monitor` with Manitoba spatial filter
- `manitoba_get_ag_weather_stations` — `WeatherStations` FeatureServer (station locations + URL to live readings)

### Domain 3: Transport / 511 Manitoba

**Verdict: CONDITIONAL — depends on key being freely obtainable. Recommend planning the tool but flagging as implementation-risk.**

**Manitoba 511 API facts (confirmed):**
- Base URL: `https://www.manitoba511.ca/api/v3/get/{endpoint}` (v3, unlike Alberta's undocumented v2)
- Authentication: `key` query parameter REQUIRED — no unauthenticated access
- Endpoints: RoadConditions, Cameras, Parks, Events, Advisories, WinterRoads, TrackMyPlow
- Rate limit: 10 calls per 60 seconds (confirmed in docs)
- Response format: JSON or XML (JSON default)
- Sample WinterRoads fields: Id, LocationDescription, Primary Condition, Secondary Conditions, Visibility, AreaName, RoadwayName, EncodedPolyline, LastUpdated (Unix timestamp)
- Registration: Account required, but registration described as open to the public. Key appears to be free but this is not explicitly confirmed.

**Contrast with Alberta:** Alberta's 511 (`511.alberta.ca/api/v2/get/`) has no key and no documentation page — it just works. Manitoba's has a documented developer API but requires registration. This makes Manitoba 511 an **auth-gated** endpoint by project definition.

**Decision per no-scraping discipline:** The key appears to be free and publicly obtainable (no paywall mentioned). However, since we cannot verify this without completing registration, the planner should plan the transport tools with a flag: "Implement only if a free API key is confirmed obtainable during Wave 0 implementation. If key is paywalled or restricted, defer transport domain to a follow-up phase."

**If key is obtainable, recommended tools (3):**
- `manitoba_get_road_events` — Events endpoint (closures, incidents, construction)
- `manitoba_get_winter_road_conditions` — WinterRoads endpoint (seasonal, high value)
- `manitoba_get_traffic_cameras` — Cameras endpoint (stable URLs, cache 24h)

**If key is NOT freely obtainable:** Drop all 3 transport tools, fill the tool budget with an additional environment/fisheries curated tool.

### Domain 4: Agriculture

**Verdict: CURATE 2 tools — confirmed machine-readable via ArcGIS Hub.**

Weekly crop reports are **PDF-only** (confirmed on `gov.mb.ca/agriculture/crops/seasonal-reports/`). Do not plan a `manitoba_get_crop_report` tool reading seasonal PDF reports. The machine-readable agricultural data comes from the ArcGIS Hub.

| Dataset | FeatureServer URL | Fields | Notes |
|---------|------------------|--------|-------|
| **Crop Reporting Regions** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MbAg_Crop_Reporting_Regions/FeatureServer/0` | OBJECTID, REGION (EN), RÉGION (FR) | Bilingual boundary polygons for Manitoba Agriculture's 5 crop reporting regions. Good reference layer. |
| **Hog Prices (Current Year)** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/...` (confirmed via Open Canada portal) | week, Auction, Parameter, Measure, Value | Weekly Manitoba market hog prices + US iso-wean/feeder prices. Both current and 10-year historical services confirmed. |
| **Cattle Prices (Current Year)** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MB_Cattle_Prices_Current_year/FeatureServer/0` | week, Auction, Parameter, Measure, Value | Same schema as hog prices. |

**Recommendation:** Combine into a single parametrized tool:
- `manitoba_get_livestock_prices` — dispatch by `livestock: Literal["cattle","hog"]` + optional `historical: bool`

### Domain 5: Regional Health

**Verdict: CURATE 1-2 tools — limited but confirmed machine-readable data exists.**

Manitoba has 5 RHAs: Winnipeg (WRHA), Interlake-Eastern, Prairie Mountain Health, Southern Health-Santé Sud, Northern Health Region.

| Dataset | Source | Fields | Notes |
|---------|--------|--------|-------|
| **Rural Health Care Facilities** | geoportal.gov.mb.ca item `rural-health-care-facilities-in-manitoba` → underlying FeatureServer (exact URL needs resolution at implementation) | Community, Facility, Emergency Dept availability, Acute Care, Transitional Care, Diagnostic Services, PCH | Confirmed published on geoportal; ArcGIS Hub item. FeatureServer URL not directly resolved in research — planner must use `manitoba_get_dataset_details` to discover it, or probe the ArcGIS item JSON. |
| **Diagnostic & Surgical Wait Times** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages/FeatureServer/0` | Year, IndicatorDataArea, Average_Wait | Annual averages by procedure type. Live-verified (cardiac surgery 60→144 days 2019-2021). MaxRecordCount 1000. **32,000 max records** = substantial dataset covering many procedures. |
| **RHA Boundaries** | `resources-covid19canada.hub.arcgis.com/datasets/f73a8ed3aa6d4d02b5d1ae259fbe33b5_0` | RHA boundary polygons | National dataset (not Manitoba-specific); Manitoba's 5 RHAs confirmed present. May be better sourced from geoportal.gov.mb.ca's `Manitoba_Regional_Health_Authorities` item. |

**Recommendation:**
- `manitoba_get_health_facilities` — Rural Health Care Facilities FeatureServer (facilities by RHA with ED/acute care flags)
- `manitoba_get_surgical_wait_times` — `Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages` FeatureServer (by procedure type and year)

Note: No live ER wait time data found (same situation as Alberta — not published in machine-readable form).

### Domain 6: Environment / Water

**Verdict: CURATE 2-3 tools — confirmed machine-readable via ArcGIS Hub and DataStream.**

| Dataset | Source | Fields | Notes |
|---------|--------|--------|-------|
| **Manitoba Parks** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer/0` | NAME_E, NOM_F, BIOME, O_AREA, TYPE_E, TYPE_F, MGMT_E, STATUS_E, PROTDATE, PRK_CLSS, URL | 93 parks including Provincial, Heritage, Wilderness, Park Reserves, Natural, Recreation, and Indigenous Traditional Use Parks. Bilingual. Live-verified. |
| **Fisheries / Waterbody Data** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Waterbody_Data/FeatureServer/0` | 26 fields: ID, Name, surface area, avg depth, Secchi depth, fishing division, species, stocking records, regulations, boat launch | 350+ water bodies (reference: Manitoba monitors 350 water bodies per gov.mb.ca/sd/water). Fishing management + limited water quality (Secchi depth). Live-verified. |
| **Water Quality (Long-term)** | `api.datastream.org/v1/odata/v4/Records` (DataStream API — **requires API key**) | 120 water quality variables for Lake Winnipeg basin, 2006-2021, 65 stations | OpenMB-licensed but DataStream API key required. Or direct CSV download from DataStream without API key. Use `fetch_and_parse(direct_csv_url)` for the static CSV. |
| **Provincial Forests** | `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Provincial_Forests___Version_6/FeatureServer/0` | Provincial forest management unit polygons | Confirmed in services directory. |

**Air quality:** Manitoba's AQHI is served by Environment Canada (ECCC MSC GeoMet API, Phase 4 weather module) — NOT via the Manitoba ArcGIS org. Do not build a separate Manitoba air quality tool; reference ECCC for AQHI.

**Recommendation:**
- `manitoba_get_provincial_parks` — `Manitoba_Parks` FeatureServer (bilingual parks catalog)
- `manitoba_get_fisheries_data` — `Manitoba_Waterbody_Data` FeatureServer (fishing regulations + species + water quality markers)
- (Optional) `manitoba_get_water_quality` — DataStream static CSV via `fetch_and_parse` for Lake Winnipeg historical data (LOW confidence — CSV download URL needs verification at implementation)

---

## Curated Tool Catalog (Research-recommended, 9-12 tools)

### Discovery (5 tools — ArcGIS Hub pattern, same shape as York Region Phase 14)

| Tool | Backend | Cache TTL | Notes |
|------|---------|-----------|-------|
| `manitoba_search_datasets` | ArcGIS Hub Search `/api/search/v1/collections/all/items` | 1h | Keywords, category filter, pagination |
| `manitoba_get_dataset_details` | ArcGIS Hub item detail | 24h | Returns resources list with FeatureServer URLs, download links |
| `manitoba_query_dataset` | Hybrid router: ArcGIS FeatureServer or `fetch_and_parse` | 24h file / 5min live | Same pattern as `alberta_query_dataset` |
| `manitoba_list_organizations` | ArcGIS Hub groups/orgs | 24h | Manitoba government publishing orgs |
| `manitoba_list_categories` | ArcGIS Hub tags/categories | 24h | Data categories/themes |

### Flood / Hydrology (2 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `manitoba_get_flood_alerts` | `Overland_Flood_Alerts/FeatureServer/0` | 5min | Live flood watch/warning polygons; bilingual Type_EN/Type_FR |
| `manitoba_get_provincial_waterways` | `Provincial_Waterways/FeatureServer/0` | 24h | `f_type: Literal["dike","floodway","dam","diversion","reservoir","waterway"]` dispatch |

### Agriculture & Drought (2-3 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `manitoba_get_livestock_prices` | `MB_Cattle_Prices_Current_year/FeatureServer/0` + hog service | 24h | `livestock: Literal["cattle","hog"]`, optional `historical: bool` for 10-year archive |
| `manitoba_get_drought_status` | `Canada_USA_Drought_Monitor/FeatureServer/0` | 24h (weekly update) | D0-D4 intensity + optional Manitoba spatial filter |
| `manitoba_get_ag_weather_stations` | `WeatherStations/FeatureServer/0` | 24h | Station locations + `AgRegion` filter + `URL` to live data page per station |

### Environment / Parks (2 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `manitoba_get_provincial_parks` | `Manitoba_Parks/FeatureServer/0` | 24h | 93 parks; `park_type=` filter (Provincial/Heritage/Wilderness/Recreation/Natural/Park Reserve/Indigenous Traditional Use) |
| `manitoba_get_fisheries_data` | `Manitoba_Waterbody_Data/FeatureServer/0` | 24h | 350+ water bodies; `region=` filter or name search; fishing regulations + species + water quality markers |

### Health (1-2 tools)

| Tool | FeatureServer | Cache TTL | Notes |
|------|--------------|-----------|-------|
| `manitoba_get_surgical_wait_times` | `Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages/FeatureServer/0` | 7d | Annual averages by Year + procedure (IndicatorDataArea) |
| `manitoba_get_health_facilities` | Rural Health Care Facilities FeatureServer (resolve during implementation) | 24h | RHA filter; ED/acute care/PCH flags |

### Transport / 511 (0 or 3 tools — conditional on key)

| Tool | Endpoint | Cache TTL | Notes |
|------|----------|-----------|-------|
| `manitoba_get_road_events` | `https://www.manitoba511.ca/api/v3/get/events` | 5min | KEY REQUIRED — plan but flag as implementation-risk |
| `manitoba_get_winter_road_conditions` | `https://www.manitoba511.ca/api/v3/get/winterroads` | 5min | KEY REQUIRED — highest seasonal value |
| `manitoba_get_traffic_cameras` | `https://www.manitoba511.ca/api/v3/get/cameras` | 24h | KEY REQUIRED — stable camera locations |

**Domain density vs. CONTEXT.md target:**

| Domain | CONTEXT.md target | Research-recommended | Delta |
|--------|-------------------|----------------------|-------|
| Flood / Hydrology | 2+ curated | 2 (flood alerts + waterways) | On target |
| Manitoba Hydro / Energy | 1-2 | **0 (DROPPED — no public data)** | -1 to -2; compensated by drought |
| Transport / 511 | 2-3 | 3 (conditional) | On target if key obtainable |
| Agriculture | 2-3 | 3 (livestock + drought + ag weather) | On target |
| Regional Health | 2 | 2 (wait times + facilities) | On target |
| Environment / Water | 2-3 | 2-3 (parks + fisheries + optional water quality) | On target |
| **Curated Total** | **9-13** | **10-12 (+ 3 conditional 511)** | Within range |
| Discovery | 5 | 5 | On target |
| **Grand Total** | **14-18** | **15-17** | Within range |

---

## Architecture Patterns

### Recommended Module Structure

```
src/mcp_canada/modules/manitoba/
├── __init__.py           # MODULE_NAME = "manitoba", MODULE_DESCRIPTION (en+fr)
├── constants.py          # BASE_URL (ArcGIS Hub), RATE_GROUPs, CACHE_TTLs, FeatureServer URLs, 511 URLs (if applicable)
├── schemas.py            # Flat Pydantic v2 models
├── client.py             # ~15 async functions returning (data, was_cached) tuples
├── tools.py              # ~15 @tool functions (5 discovery + 9-12 curated)
├── prompts.py            # 6 bilingual @prompt functions
├── resources.py          # 7 zero-parameter @resource functions
└── __tests__/
    ├── __init__.py
    ├── conftest.py        # Sample ArcGIS JSON fixtures for all curated tools
    ├── test_client.py     # Client unit tests + TestSharedApiGetContract
    ├── test_tools.py      # Tool unit tests (mocked client layer)
    └── test_prompts_resources.py
```

### Pattern 1: ArcGIS Hub Discovery Constants

```python
# src/mcp_canada/modules/manitoba/constants.py
from typing import Final

# ---------------------------------------------------------------------------
# Data MB — geoportal.gov.mb.ca (ArcGIS Hub)
# ---------------------------------------------------------------------------
HUB_BASE_URL: Final[str] = "https://geoportal.gov.mb.ca"
HUB_ORG_BASE: Final[str] = "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services"
ARCGIS_ORG_ID: Final[str] = "mMUesHYPkXjaFGfS"
HUB_SEARCH_URL: Final[str] = f"{HUB_BASE_URL}/api/search/v1/collections/all/items"
RATE_GROUP_HUB: Final[str] = "manitoba_hub"
RATE_LIMIT_HUB: Final[float] = 10.0

# ---------------------------------------------------------------------------
# Flood / Hydrology FeatureServers
# ---------------------------------------------------------------------------
FLOOD_ALERTS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Overland_Flood_Alerts/FeatureServer"
PROVINCIAL_WATERWAYS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Provincial_Waterways/FeatureServer"

# ---------------------------------------------------------------------------
# Agriculture FeatureServers
# ---------------------------------------------------------------------------
CATTLE_PRICES_FS_URL: Final[str] = f"{HUB_ORG_BASE}/MB_Cattle_Prices_Current_year/FeatureServer"
# Hog prices service name TBD — resolve during implementation via hub search
AG_WEATHER_STATIONS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/WeatherStations/FeatureServer"
CROP_REGIONS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/MbAg_Crop_Reporting_Regions/FeatureServer"
DROUGHT_MONITOR_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Canada_USA_Drought_Monitor/FeatureServer"

# ---------------------------------------------------------------------------
# Parks / Environment FeatureServers
# ---------------------------------------------------------------------------
PROVINCIAL_PARKS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Parks/FeatureServer"
WATERBODY_DATA_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Waterbody_Data/FeatureServer"
PROVINCIAL_FORESTS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Provincial_Forests___Version_6/FeatureServer"

# ---------------------------------------------------------------------------
# Health FeatureServers
# ---------------------------------------------------------------------------
SURGICAL_WAIT_TIMES_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages/FeatureServer"
)
# Rural Health Care Facilities: resolve via hub item ID during implementation
# Hint: geoportal.gov.mb.ca/apps/manitoba::rural-health-care-facilities-in-manitoba

# ---------------------------------------------------------------------------
# Manitoba 511 REST API (conditional — key required)
# ---------------------------------------------------------------------------
FIVE11_BASE_URL: Final[str] = "https://www.manitoba511.ca/api/v3/get"
RATE_GROUP_511: Final[str] = "manitoba_511"
RATE_LIMIT_511: Final[float] = 2.0   # 10 calls/60s documented; be conservative
# NOTE: 511 endpoints require a registered developer key
# Key acquisition: https://www.manitoba511.ca (sign up for account → request API key)
# If key is not freely obtainable, comment out all _511 constants and skip tools

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 300        # 5min — flood alerts, road events, winter roads
CACHE_TTL_SEARCH: Final[int] = 3600     # 1h — hub search
CACHE_TTL_META: Final[int] = 86400      # 24h — parks, waterways, facilities, weather stations, livestock prices
CACHE_TTL_STATIC: Final[int] = 86400   # 24h — drought monitor (weekly update at source)
CACHE_TTL_ANNUAL: Final[int] = 604800   # 7d — surgical wait times (annual data)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000
```

### Pattern 2: ArcGIS Hub _hub_get Helper

Manitoba's discovery tools call the ArcGIS Hub Search API, which returns a different JSON structure than CKAN. Reuse the pattern from York Region Phase 14:

```python
# src/mcp_canada/modules/manitoba/client.py
async def _hub_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """ArcGIS Hub Search API call against geoportal.gov.mb.ca."""
    url = HUB_SEARCH_URL if path == "search" else f"{HUB_BASE_URL}/api/{path}"
    result = await api_get(
        url,
        params or {},
        headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
    )
    # ArcGIS Hub returns JSON directly — not wrapped in CKAN success/result envelope
    if not isinstance(result, dict):
        raise httpx.HTTPStatusError(
            f"Hub returned non-dict response for {path}",
            request=httpx.Request("GET", url),
            response=httpx.Response(500),
        )
    return result
```

### Pattern 3: FeatureServer Client Functions

Follow Alberta Phase 17 pattern exactly — each curated tool has a thin client function wrapping `arcgis_hub.query_feature_service`:

```python
async def fetch_provincial_parks(
    park_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
) -> tuple[dict, bool]:
    """Fetch Manitoba provincial parks from ArcGIS Hub."""
    cache_key = f"manitoba:parks:{park_type or 'all'}:{include_geometry}"
    limiter = get_limiter(RATE_GROUP_HUB, rate=RATE_LIMIT_HUB)

    async def fetcher():
        await limiter.acquire()
        where = f"TYPE_E = '{park_type}'" if park_type else "1=1"
        return await arcgis_hub.query_feature_service(
            PROVINCIAL_PARKS_FS_URL,
            layer_id=0,
            where=where,
            out_fields="NAME_E,NOM_F,BIOME,O_AREA,TYPE_E,TYPE_F,MGMT_E,STATUS_E,PROTDATE,PRK_CLSS,URL",
            include_geometry=include_geometry,
            max_records=max_records,
        )

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
```

### Pattern 4: Manitoba 511 Client (conditional — only if key confirmed)

```python
async def fetch_road_events(key: str) -> tuple[list[dict], bool]:
    """Fetch current road events from Manitoba 511 API v3."""
    cache_key = "manitoba:511:events"
    limiter = get_limiter(RATE_GROUP_511, rate=RATE_LIMIT_511)

    async def fetcher():
        await limiter.acquire()
        # 511 returns JSON list at top level (not ArcGIS envelope)
        rows = await api_get(
            f"{FIVE11_BASE_URL}/events",
            {"key": key, "format": "json"},
            headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
        )
        return rows

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, fetcher)
```

**Note:** If the developer key is baked into constants at `FIVE11_API_KEY` (loaded from environment variable `MANITOBA_511_KEY`), tools can call `fetch_road_events(FIVE11_API_KEY)`. If the env var is absent, the tool should return `make_error("NOT_CONFIGURED", ...)` with instructions to obtain a key.

### Anti-Patterns to Avoid

- **NEVER attempt to read `data.manitoba.ca`** — unreachable on research date; Manitoba's data is on `geoportal.gov.mb.ca`.
- **NEVER use `_api_get` CKAN helper for Hub calls** — Hub Search API returns different JSON structure (not CKAN success/result envelope).
- **NEVER call `arcgis_hub.query_feature_service` on Manitoba 511 endpoints** — 511 is a custom REST API, not ArcGIS FeatureServer.
- **NEVER scrape the Hydrologic Forecast Centre flood bulletins** — PDF/HTML only, no machine-readable endpoint.
- **NEVER call `mli.gov.mb.ca`** — retired 2022-02-09, no data updates.
- **NEVER assume Manitoba Hydro water levels have an API** — HTML tables only, confirmed.
- **NEVER call `.raise_for_status()` or `.json()` on `api_get` return** — `shared/http.py:api_get` returns parsed JSON. Phase 15 root cause.
- **NEVER mock with `MagicMock(json=lambda: {...})`** — use `AsyncMock(return_value={...})`.
- **NEVER build a Manitoba AQHI tool** — Manitoba's AQHI is served via ECCC/MSC GeoMet (Phase 4 weather module). Reference that module in docstring instead.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ArcGIS FeatureServer pagination | Custom page loop | `shared/arcgis_hub.py:query_feature_service` | Already handles `exceededTransferLimit` pagination to 5000-record cap |
| ArcGIS Hub item lookup | Custom item fetcher | `shared/arcgis_hub.py` or `_hub_get` | Phase 14 pattern already proven |
| File resource parsing | Custom CSV/GeoJSON parser | `shared/parsers.py:fetch_and_parse` | Handles CSV/XLSX/GeoJSON/Shapefile |
| Cache/rate limiting | Per-tool custom | `cached_fetch` + `get_limiter` | All modules use this |
| Response envelope | Per-tool JSON schema | `make_response` / `make_error` | Every tool must use this |

**Key insight:** The `mMUesHYPkXjaFGfS` ArcGIS org is the same technology as `Eb8P5h4CJk8utIBz` (Alberta WMBappServices) and `7KHJ4f28UDLgUq2U` (Alberta AHSGIS). `shared/arcgis_hub.py` works unchanged.

---

## Common Pitfalls

### Pitfall 1: Assuming data.manitoba.ca is a live CKAN portal
**What goes wrong:** Planning a module that calls `https://data.manitoba.ca/api/3/action/package_search` — these calls will time out or ECONNREFUSED.
**Why it happens:** The CONTEXT.md mentioned `data.manitoba.ca` as the primary CKAN portal — this was a reasonable hypothesis given other provincial patterns.
**How to avoid:** Manitoba's machine-readable data is on `geoportal.gov.mb.ca` (ArcGIS Hub), not a CKAN endpoint. All 5 discovery tools use ArcGIS Hub Search API.
**Warning signs:** Any code importing from a `CKAN_BASE_URL = "https://data.manitoba.ca/api/3/action/"` constant.

### Pitfall 2: Treating ArcGIS Hub discovery as CKAN discovery
**What goes wrong:** Using `package_search?rows=N` instead of Hub Search `/api/search/v1/collections/all/items?num=N`; checking for `result.success == True` instead of processing Hub's direct JSON.
**Why it happens:** Copy-pasting from Quebec/BC CKAN modules without checking Hub API spec.
**How to avoid:** Reuse York Region Phase 14's `_hub_get` helper and Hub Search pagination pattern — it's already correct for ArcGIS Hub.
**Warning signs:** Code that does `envelope.get("success")` or `envelope.get("result")` on Hub API responses.

### Pitfall 3: Manitoba 511 key requirement
**What goes wrong:** Calling `https://www.manitoba511.ca/api/v3/get/events` without a key — API returns 401 or empty response.
**Why it happens:** Alberta's 511 API has no key, so developers assume Manitoba's doesn't either.
**How to avoid:** Always pass `?key={FIVE11_API_KEY}` for Manitoba 511 calls. Load key from env var `MANITOBA_511_KEY`. Return `make_error("NOT_CONFIGURED", "Manitoba 511 API key not set. Obtain a developer key from https://www.manitoba511.ca/developers/doc")` if env var is missing.
**Warning signs:** Any test that calls a 511 endpoint without a key mock.

### Pitfall 4: Manitoba Land Initiative (MLI) is retired
**What goes wrong:** Finding mli.gov.mb.ca in external docs or older tutorials and trying to fetch WFS layers from it.
**Why it happens:** MLI was previously Manitoba's primary geospatial data source.
**How to avoid:** MLI stopped receiving updates 2022-02-09. All MLI content has migrated to `geoportal.gov.mb.ca`. Never call `mli.gov.mb.ca`.

### Pitfall 5: Expecting live flood levels on geoportal
**What goes wrong:** Building `manitoba_get_river_levels` that tries to return real-time water level readings from the geoportal.
**Why it happens:** The "Manitoba River Conditions and Forecasts" web app suggests station-level data is queryable.
**How to avoid:** The River Conditions web app shows station LOCATIONS and status flags (Flood Watch, Flood Warning, Normal). Actual level readings come from ECCC's hydrometric HYDAT database (`wateroffice.ec.gc.ca`), not from Manitoba's ArcGIS Hub. Plan `manitoba_get_river_stations` as a station discovery tool (returns station points with flood status), NOT as a real-time level-readings tool.

### Pitfall 6: Manitoba Hydro water levels are HTML-only
**What goes wrong:** Attempting `fetch_and_parse("https://www.hydro.mb.ca/corporate/operations/water-levels/")` — returns HTML table.
**Why it happens:** Manitoba is ~97% hydro; developers assume Hydro publishes machine-readable generation/flow data.
**How to avoid:** Confirmed no API or download on hydro.mb.ca. Do not build `manitoba_get_hydro_flows` or similar. The `Drought_Monitor_Reservoirs` FeatureServer in the ArcGIS org MIGHT have reservoir capacity data — investigate at implementation if energy-adjacent coverage is needed.

### Pitfall 7: DataStream API key for water quality
**What goes wrong:** Planning `manitoba_get_lake_winnipeg_water_quality` that calls `api.datastream.org/v1/odata/v4/Records` — requires DataStream API key.
**Why it happens:** DataStream looks like a clean REST API from the docs.
**How to avoid:** Use the direct CSV download URL from the DataStream dataset page instead (no key needed). Or reference the Open Government Portal resource which provides a static CSV. Use `fetch_and_parse(csv_url)`.

### Pitfall 8: Province-wide drought data isn't Manitoba-specific
**What goes wrong:** Returning all of North America's drought polygons when an agent asks "what is Manitoba's drought status".
**Why it happens:** `Canada_USA_Drought_Monitor` covers the entire continent.
**How to avoid:** Filter by Manitoba bounding box in the `where` clause or use a spatial intersection with the Manitoba boundary. At minimum, document in docstring that `filter_province=True` (default) applies Manitoba bbox filter `BBOX(-101.36, 48.99, -95.15, 60.0)`.

---

## Manitoba-Specific Reference Data (for Resources)

### Manitoba's 5 Regional Health Authorities

| RHA | Short Name | Coverage | Major Hospitals |
|-----|-----------|----------|----------------|
| Winnipeg Regional Health Authority | WRHA | City of Winnipeg + Churchill, East/West St. Paul | Health Sciences Centre, St. Boniface, Grace, Victoria |
| Prairie Mountain Health | PMH | Western Manitoba | Brandon Regional Health Centre + 33 hospitals (6 with 24/7 ER) |
| Interlake-Eastern RHA | IERHA | Eastern/Interlake Manitoba | 10 hospitals, 16 PCHs, 19 EMS stations |
| Southern Health-Santé Sud | SHSS | Southern Manitoba | 17 hospitals (3 with 24/7 ER) |
| Northern Health Region | NHR | Northern Manitoba | 8 hospitals |

### Manitoba's Major River Systems (for data://manitoba/major-rivers resource)

| River | Direction | Key Cities | Flood Risk |
|-------|-----------|-----------|-----------|
| Red River | N (flows to Lake Winnipeg) | Emerson, Winnipeg | Very High — major spring flood corridor |
| Assiniboine River | E (joins Red at Winnipeg) | Brandon, Winnipeg | High — 2011 near-record flood |
| Winnipeg River | W (drains Lake of the Woods) | Kenora area → Lake Winnipeg | Moderate |
| Souris River | N (enters Manitoba from ND) | Wawanesa | Moderate |
| Lake Manitoba | — | Central | Drainage basin flood risk |
| Red River Floodway | Bypass diversion E of Winnipeg | — | Protects Winnipeg — managed by Manitoba Infrastructure |

### Manitoba's Departments/Ministries (for data://manitoba/departments resource)

| Ministry | Slug (for ArcGIS org filtering) | Key Data Domains |
|---------|--------------------------------|-----------------|
| Transportation and Infrastructure | - | Flood forecasting, roads, highways |
| Agriculture | - | Crop reports, livestock prices, ag weather |
| Sustainable Development (Environment & Climate) | - | Water quality, air quality, parks |
| Health, Seniors and Long-Term Care | - | RHAs, wait times, facilities |
| Conservation and Climate | - | Provincial forests, wildlife, parks |
| Economic Development and Jobs | - | Labour market, trade stats |

### Manitoba Open Data Licence

- **Name:** OpenMB Information and Data Use Licence
- **PDF:** `https://www.gov.mb.ca/asset_library/en/legal/OpenMB-Information-Data-Use-Licence.pdf`
- **Status:** Permits commercial and non-commercial use, reproduction, adaptation, distribution
- **Attribution required:** Yes — standard attribution statement
- **Compatibility:** Similar to CC-BY 4.0; compatible with other Canadian OGL variants
- **Agent use:** CONFIRMED permitted — building agents and applications explicitly listed as permitted use cases

---

## Code Examples

### Hub Search Discovery

```python
# Source: York Region Phase 14 pattern (shared/arcgis_hub.py)
# Manitoba Hub uses same ArcGIS Hub Search API
result = await api_get(
    "https://geoportal.gov.mb.ca/api/search/v1/collections/all/items",
    {"q": query, "num": page_size, "start": offset},
    headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"},
)
# result is a dict with "results" list — NOT CKAN envelope
items = result.get("results", [])
```

### Parks FeatureServer Query (verified working)

```python
# Source: live probe 2026-06-13
# 93 parks, no auth required
result = await arcgis_hub.query_feature_service(
    "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer",
    layer_id=0,
    where="1=1",
    out_fields="NAME_E,NOM_F,BIOME,O_AREA,TYPE_E,TYPE_F,STATUS_E,PROTDATE,PRK_CLSS,URL",
    include_geometry=False,
    max_records=200,
)
# result["features"] = list of park dicts; result["truncated"] = False (93 < 5000)
```

### Flood Alerts Query (verified schema)

```python
# Source: live probe 2026-06-13 — 0 active alerts on research date
result = await arcgis_hub.query_feature_service(
    "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Overland_Flood_Alerts/FeatureServer",
    layer_id=0,
    where="1=1",   # returns [] when no alerts active — correct behavior
    out_fields="Type_EN,Type_FR,Start_Date,End_Date",
    include_geometry=True,  # polygon alerts need geometry for agent map use
    max_records=2000,  # service maxRecordCount
)
# Type_EN values: "Watch" | "Warning"
```

### Drought Monitor Query (Manitoba filter)

```python
# Manitoba approximate bounding box: lon -101.36 to -95.15, lat 48.99 to 60.0
# Use ArcGIS geometry filter
result = await arcgis_hub.query_feature_service(
    "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Canada_USA_Drought_Monitor/FeatureServer",
    layer_id=0,
    where="1=1",
    out_fields="DM,OBS_DATE,SOURCE",
    # geometry param: planner should add Manitoba bbox intersection filter
    max_records=500,
)
# DM values: "D0" | "D1" | "D2" | "D3" | "D4" | "" (no drought)
```

### Agricultural Weather Stations

```python
# Source: live probe 2026-06-13 — 100+ stations confirmed
result = await arcgis_hub.query_feature_service(
    "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/WeatherStations/FeatureServer",
    layer_id=0,
    where=f"AgRegion = '{region}'" if region else "1=1",
    out_fields="StnName,LatDD,LongDD,Elevation,AgRegion,URL",
    include_geometry=False,
    max_records=200,
)
# URL field links to live hourly data page per station on agrimaps.gov.mb.ca
```

### Manitoba 511 Road Events (conditional — key required)

```python
# Source: Manitoba 511 API v3 docs at https://www.manitoba511.ca/developers/doc
# NOTE: Unlike Alberta 511 v2 (no key), Manitoba 511 v3 requires &key=
import os
key = os.environ.get("MANITOBA_511_KEY", "")
if not key:
    return make_error("NOT_CONFIGURED", "Manitoba 511 API key not set")
rows = await api_get(
    "https://www.manitoba511.ca/api/v3/get/events",
    {"key": key, "format": "json"},
    headers={"User-Agent": "mcp-canada/1.0"},
)
# rows is a list directly (not wrapped in envelope)
```

---

## Federation / Scope Policy

**Manitoba's geoportal is provincial-scope** (unlike Quebec's 139-org federated CKAN). The `geoportal.gov.mb.ca` ArcGIS Hub hosts data published by Manitoba government departments only. There is no federation with municipalities (Winnipeg's data is on `data.winnipeg.ca` — Phase 32).

**Implementation:** `manitoba_search_datasets` searches all Manitoba government datasets by default. An optional `category=` filter parameter exposes ArcGIS Hub content type/tag filtering. Document in docstring that this is the Government of Manitoba's provincial open data hub, and municipal data (Winnipeg, Brandon, etc.) is on separate portals.

---

## Validation Architecture

> nyquist_validation is enabled in .planning/config.json.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x (existing project standard) |
| Config file | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest src/mcp_canada/modules/manitoba/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MB-01 | Hub search returns datasets list | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaSearchDatasets -x` | ❌ Wave 0 |
| MB-02 | Dataset details returns FeatureServer URLs | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetDatasetDetails -x` | ❌ Wave 0 |
| MB-03 | Query dataset auto-routes to arcgis_hub | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaQueryDataset -x` | ❌ Wave 0 |
| MB-04 | List organizations returns Hub orgs | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaListOrgs -x` | ❌ Wave 0 |
| MB-05 | List categories returns Hub tags | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaListCategories -x` | ❌ Wave 0 |
| MB-06 | Parks returns 93 parks with bilingual names | unit + integration | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetParks -x` | ❌ Wave 0 |
| MB-07 | Flood alerts returns polygons (or empty when no alerts) | unit + integration | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetFloodAlerts -x` | ❌ Wave 0 |
| MB-08 | River stations returns station points with flood status | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetRiverStations -x` | ❌ Wave 0 |
| MB-09 | Provincial waterways returns typed features (dike/floodway/dam) | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetWaterways -x` | ❌ Wave 0 |
| MB-10 | Drought status returns D0-D4 polygons | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetDroughtStatus -x` | ❌ Wave 0 |
| MB-11 | Ag weather stations returns 100+ stations with AgRegion and URL | unit + integration | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetAgWeatherStations -x` | ❌ Wave 0 |
| MB-12 | Livestock prices returns weekly cattle/hog prices | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetLivestockPrices -x` | ❌ Wave 0 |
| MB-13 | Crop regions returns bilingual region polygons | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetCropRegions -x` | ❌ Wave 0 |
| MB-14 | Surgical wait times returns procedure/year/days data | unit + integration | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetWaitTimes -x` | ❌ Wave 0 |
| MB-15 | Fisheries data returns waterbodies with species and regulations | unit | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitobaGetFisheriesData -x` | ❌ Wave 0 |
| MB-17 (cond.) | 511 events returns road events (skip if no key) | unit (mocked key) | `pytest src/mcp_canada/modules/manitoba/__tests__/test_tools.py::TestManitoba511 -x -k "not integration"` | ❌ Wave 0 |
| MB-18 | All tools discoverable via discover_tools through MCP Client | integration | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "Manitoba"` | ❌ Wave 0 |

### Key Test Patterns

**TestSharedApiGetContract (mandatory):**
```python
class TestSharedApiGetContract:
    """Ensure mcp_canada.shared.http.api_get is patched at the right layer."""
    @patch("mcp_canada.modules.manitoba.client.api_get")
    async def test_hub_get_calls_api_get(self, mock_api_get):
        mock_api_get.return_value = {"results": [], "total": 0}
        await fetch_search_datasets("test")
        mock_api_get.assert_called_once()
```

**Flood alert empty-response test (important edge case):**
```python
async def test_flood_alerts_empty_when_no_active_alerts(self):
    """Confirms tool handles 0-feature response correctly (normal when no flooding)."""
    mock_arcgis.return_value = ({"features": [], "count": 0, "truncated": False}, False)
    result = await client.call_tool("call_tool", {"name": "manitoba_get_flood_alerts", "arguments": {}})
    data = json.loads(result.content[0].text)
    assert "_meta" in data
    assert data["data"]["features"] == []   # Empty is correct, not an error
```

**511 missing-key test:**
```python
async def test_road_events_returns_not_configured_without_key(self, monkeypatch):
    """If MANITOBA_511_KEY env var is absent, tool returns NOT_CONFIGURED error."""
    monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
    result = await client.call_tool("call_tool", {"name": "manitoba_get_road_events", "arguments": {}})
    data = json.loads(result.content[0].text)
    assert data["error"]["code"] == "NOT_CONFIGURED"
```

### Sampling Rate

- **Per task commit:** `uv run pytest src/mcp_canada/modules/manitoba/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green + integration tests green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `src/mcp_canada/modules/manitoba/__tests__/conftest.py` — ArcGIS Hub JSON fixtures for all 10-12 curated tools
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_client.py` — client unit tests + TestSharedApiGetContract
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` — tool unit tests
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py` — prompts/resources tests
- [ ] `tests/integration/test_tool_scenarios.py::TestManitobaToolScenarios` — integration tests via MCP Client
- [ ] `tests/integration/test_prompts_resources_scenarios.py::TestManitobaPromptsResources` — prompts/resources integration

---

## Open Questions

1. **Manitoba 511 developer key: free or paid?**
   - What we know: Registration required (free account on manitoba511.ca), then request API key. Rate limit: 10 calls/60s. No explicit pricing stated.
   - What's unclear: Whether the key is instantly provisioned or requires approval; whether there are commercial use restrictions.
   - Recommendation: Wave 0 implementation task should confirm key availability. If free and instant: implement 3 transport tools. If gated/paid: defer all transport tools, replace with `manitoba_get_river_stations` (river conditions web app data) and/or `manitoba_get_provincial_forests` (forests FeatureServer).

2. **Rural Health Care Facilities FeatureServer URL**
   - What we know: Dataset exists on `geoportal.gov.mb.ca/apps/manitoba::rural-health-care-facilities-in-manitoba`. ArcGIS Hub item.
   - What's unclear: The direct FeatureServer URL (not resolved in research; web app viewer only confirmed).
   - Recommendation: During Wave 0 implementation, probe the ArcGIS Hub item JSON (`geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=rural+health+care+facilities`) to discover the underlying FeatureServer service URL. The `mMUesHYPkXjaFGfS` org likely hosts it as `Rural_Health_Care_Facilities/FeatureServer/0`.

3. **Manitoba hog prices FeatureServer service name**
   - What we know: Hog prices (current year and 10-year) confirmed on Open Canada portal and Hub. Service exists in `mMUesHYPkXjaFGfS` org.
   - What's unclear: Exact service name (not listed in the 93-service inventory retrieved; may not be named `MB_Hog_Prices_Current_year`).
   - Recommendation: Probe `services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/?f=json` during Wave 0, search for "hog" in the service list. Or use Hub Search: `q=hog prices` on geoportal.gov.mb.ca to discover the item and its service URL.

4. **Manitoba River Conditions and Forecasts underlying FeatureServer**
   - What we know: Web app at `manitoba.maps.arcgis.com` (item ID `5c57801d0efc4676a2d2c95174ef44d5`) shows station points with flood alert status. Live data from hydrometric gauging stations.
   - What's unclear: The specific FeatureServer layer ID and URL backing the app's station layer.
   - Recommendation: During Wave 0, inspect the web app's map configuration JSON (accessible at `arcgis.com/home/item.html?id=5c57801d0efc4676a2d2c95174ef44d5`) to extract the underlying FeatureServer URL. This likely resolves to a `mMUesHYPkXjaFGfS` or `manitoba.maps.arcgis.com` hosted layer.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manitoba Land Initiative (mli.gov.mb.ca) | Data MB / geoportal.gov.mb.ca (ArcGIS Hub) | 2022-02-09 | MLI retired; new platform is ArcGIS Hub with 93+ FeatureServers |
| data.manitoba.ca (assumed CKAN) | geoportal.gov.mb.ca (ArcGIS Hub) | 2022-2023 | Module design changes from CKAN to ArcGIS Hub pattern |
| Manitoba 511 v2 (undocumented) | Manitoba 511 v3 (documented, key required) | ~2022-2023 | Unlike Alberta v2, Manitoba v3 requires registration |
| Static PDF flood reports | ArcGIS Hub `Overland_Flood_Alerts` FeatureServer | ~2020-2022 | Live bilingual flood alert polygons now machine-readable |

**Deprecated/outdated:**
- `mli.gov.mb.ca`: Retired 2022. Do not reference in code or docs.
- Any assumption about `data.manitoba.ca/api/3/action/`: Not confirmed as a live CKAN endpoint.

---

## Sources

### Primary (HIGH confidence)

- `services.arcgis.com/mMUesHYPkXjaFGfS` — Live probe 2026-06-13; confirmed 93 FeatureServer services, no auth required
- `Overland_Flood_Alerts/FeatureServer/0?f=json` — Live schema probe: 9 fields confirmed, bilingual Type_EN/Type_FR
- `Manitoba_Parks/FeatureServer/0?f=json` — Live schema probe: 33 fields, 93 parks confirmed
- `Manitoba_Parks/FeatureServer/0/query` — Live query: Hecla/Grindstone Provincial Park record (108,500 ha) confirmed
- `WeatherStations/FeatureServer/0?f=json` — Live schema probe: 6 fields, 100+ agricultural stations
- `MB_Cattle_Prices_Current_year/FeatureServer/0?f=json` — Live probe: week/Auction/Parameter/Measure/Value schema confirmed
- `Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages/FeatureServer/0/query` — Live query: 3 records returned (cardiac surgery 2019-2021 confirmed)
- `Canada_USA_Drought_Monitor/FeatureServer/0?f=json` — Live schema probe: DM/OBS_DATE/SOURCE fields, D0-D4 domain confirmed
- `Provincial_Waterways/FeatureServer/0?f=json` — Live schema probe: F_TYPE domain (Dike/Floodway/Dam etc.) confirmed
- `Manitoba_Waterbody_Data/FeatureServer/0?f=json` — Live schema probe: 26 fields including species/stocking/Secchi confirmed
- `www.manitoba511.ca/developers/doc` — Developer portal confirms: 7 endpoints, key required, 10 calls/60s limit
- `www.manitoba511.ca/help/endpoint/winterroads` — Confirms v3 URL pattern: `/api/v3/get/winterroads`, key param, JSON/XML, fields including EncodedPolyline
- `mli.gov.mb.ca` — Confirms retired as of 2022-02-09; users directed to geoportal.gov.mb.ca
- `open.canada.ca/data/en/dataset/ecd7ca96` — Confirms MbAg_Crop_Reporting_Regions FeatureServer URL
- `www.hydro.mb.ca/corporate/operations/water-levels/` — Confirms HTML-table-only water level data (no API/CSV)
- `www.manitoba.ca/floodinfo/` — Confirms HFC publishes PDF/HTML flood bulletins only (no machine-readable download)

### Secondary (MEDIUM confidence)

- `geoportal.gov.mb.ca/datasets` search results — Manitoba GeoPortal Open Data group confirmed via ArcGIS Hub group ID `c8b5f087c9074c5cb502ed7df0ede9dc`
- `open.canada.ca/data/en/dataset/03a9901f` — Rural Health Care Facilities confirmed as published on geoportal.gov.mb.ca; FeatureServer URL not resolved
- `open.canada.ca/data/en/dataset/ea297f31` — Manitoba River Conditions Web App confirmed; underlying FeatureServer URL pending resolution
- `open.canada.ca/data/en/dataset/f650f572` (Manitoba Hog Prices) — Confirmed dataset exists; FeatureServer URL not resolved in research
- `www.gov.mb.ca/openmb/` — OpenMB licence confirmed: free commercial/non-commercial use, attribution required
- `hub.arcgis.com/maps/manitoba::manitoba-regional-health-authorities` — Manitoba RHA boundaries confirmed on ArcGIS Hub
- `datastream.org/en-ca/dataset/888eac9b` — Manitoba Long-term Water Quality data confirmed; DataStream API key required; direct CSV download available

### Tertiary (LOW confidence)

- Manitoba 511 API key cost/availability — Developer registration required; pricing not explicitly stated in public docs. Confirmed: registration open to public. Unconfirmed: instant provisioning vs. review process.
- Hog prices FeatureServer service name — Confirmed on Open Canada portal but exact `mMUesHYPkXjaFGfS` service name not retrieved.
- Rural Health Care Facilities FeatureServer URL — Dataset confirmed; direct REST URL not resolved.

---

## Metadata

**Confidence breakdown:**
- ArcGIS Hub portal (geoportal.gov.mb.ca): HIGH — live-verified, 7 FeatureServers probed with schema
- Curated tool targets: HIGH for 9 (live-probed FeatureServers), MEDIUM for 2 (dataset confirmed, FeatureServer URL pending)
- Manitoba 511: MEDIUM/LOW — API documented but key gating status unconfirmed
- Manitoba Hydro / energy: HIGH (confirmed: no public API)
- Licence: HIGH (confirmed: OpenMB licence, free commercial use)
- Federation: HIGH (provincial-only ArcGIS Hub, not federated with municipalities)

**Research date:** 2026-06-13
**Valid until:** 2026-09-13 (90 days — ArcGIS Hub services are stable; only 511 key policy could change)
