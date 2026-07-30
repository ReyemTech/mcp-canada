# API Coverage — New Brunswick (federal CKAN + GeoNB ArcGIS Server + NB 511 + gnb.socrata.com)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Enumerated live 2026-07-30 at plan time — the GeoNB service list below is the
> real `GET https://geonb.snb.ca/arcgis/rest/services?f=json` response (62 services),
> not an estimate.

**Curation bar (D-07):** curate the highest-value service per sub-domain and let the
discovery tools (`nb_list_geonb_services` → `nb_get_geonb_service_layers` →
`nb_query_geonb_layer`) reach the long tail. Every `OPT-OUT (long tail)` row below is
therefore *reachable at runtime*, not unreachable — it is un-**curated**, not un-shipped.

**Tool budget (D-08):** 22 tools — mid-band 18-22. Exhausted exactly.

---

## Surface 1 — Federal CKAN (`open.canada.ca`, `fq=organization:nb`, 221 datasets)

| capability | decision | reason |
|---|---|---|
| `package_search` filtered `organization:nb` | INTEGRATE | `nb_search_datasets` (NB-01) |
| `package_show` (dataset detail + bilingual metadata) | INTEGRATE | `nb_get_dataset_details` (NB-02) |
| resource fetch/parse (CSV / XLSX / GeoJSON) | INTEGRATE | `nb_query_dataset` (NB-03) via `shared/parsers.py:fetch_and_parse` |
| publisher aggregation (`org_title_at_publication`, `org_section`) | INTEGRATE | `nb_list_organizations` (NB-04) |
| facet aggregation (`subject`, `topic_category`) | INTEGRATE | `nb_list_categories` (NB-05) |
| `organization_list` | OPT-OUT | the `organization` facet under `fq=organization:nb` returns exactly one value (`nb`, 221) — live-verified; a one-row tool has no agent value |
| `group_list` | OPT-OUT | NB packages carry an empty `groups` array — live-verified across the 221 corpus; `subject`/`topic_category` facets replace it |
| `tag_list` | OPT-OUT | federal-wide and unfilterable by organization; the `keywords` facet inside `package_search` covers the same need NB-scoped |
| `datastore_search` / `datastore_search_sql` | OPT-OUT | CONTEXT.md Deferred Ideas — combining NB with the existing `datastore` module is its own design question, explicitly deferred to a later phase |
| `resource_show`, `package_autocomplete` | OPT-OUT | subsumed by `package_show` / `package_search`; no additional agent capability |

## Surface 2 — GeoNB ArcGIS Server REST operations (`geonb.snb.ca/arcgis/rest`)

| capability | decision | reason |
|---|---|---|
| `/services?f=json` service-directory enumeration | INTEGRATE | new `shared/arcgis_hub.py:list_arcgis_server_services` (NB-06) → `nb_list_geonb_services` (NB-07) |
| `/{service}/MapServer?f=json` layer enumeration | INTEGRATE | new `shared/arcgis_hub.py:get_arcgis_server_layers` (NB-06) → `nb_get_geonb_service_layers` (NB-08) |
| `/{service}/MapServer/{layer}/query` feature query | INTEGRATE | existing `query_feature_service`, unchanged (D-05) → `nb_query_geonb_layer` (NB-09) + all 11 curated tools |
| `/{service}/MapServer/{layer}?f=json` field metadata | INTEGRATE | existing `get_layer_metadata`, unchanged — surfaced through `nb_get_geonb_service_layers` |
| `returnCountOnly=true` | INTEGRATE | existing `get_count`, unchanged — backs the T-21-03 unbounded-query guards |
| `export` (map image) / tile fetch | OPT-OUT | returns raster pixels; an MCP text envelope cannot carry usable imagery |
| `identify` / `find` | OPT-OUT | `/query` with a WHERE clause covers the same need with explicit `outFields` control |
| ArcGIS **Hub** Search API (`geonb-snb.opendata.arcgis.com`) | OPT-OUT | HTTP 401 `"private org id ... is not accessible"` — verified dead end (D-01, D-06). Do not re-attempt |
| folder `Geocoding` | OPT-OUT | address geocoding is a distinct capability with its own request/response contract; `nb_get_civic_addresses` covers attribute-based address lookup. Candidate for a follow-up phase |
| folders `geoprocessing`, `GRP`, `RIPT`, `test`, `Utilities`, `GeoNB_Imagery_NBSD` | OPT-OUT | internal/utility/imagery folders — not published open attribute data |

## Surface 3 — GeoNB services (all 62, live-enumerated 2026-07-30)

### Curated (9 INTEGRATE)

> **Updated 2026-07-30 (21-07, closing the phase):** the original 11-row curated list below
> included `GeoNB_DNR_MineralOccurrences` and `GeoNB_DNR_ProvincialParks` as INTEGRATE. The
> 21-01 Task 2 blocking checkpoint (option-a: `gnb.socrata.com` joins the discovery surface via
> two new tools) required dropping two curated tools to hold the D-08 22-tool budget — both
> moved here, and both are documented as such in `21-01-SUMMARY.md` and `21-05-SUMMARY.md`. See
> the long-tail section below for their reclassification; both remain reachable via
> `nb_query_geonb_layer`, never unreachable.

| capability (service) | decision | reason |
|---|---|---|
| `GeoNB_ENV_FloodHazardIndex` | INTEGRATE | `nb_get_flood_hazard_areas` (NB-10) — layer 0, 269 polygons |
| `GeoNB_ENV_Historical_Floods` | INTEGRATE | `nb_get_historical_floods` (NB-11) — layer 0 main, layer 8 = 1973 event |
| `GeoNB_ENV_Wetlands` | INTEGRATE | `nb_get_wetlands` (NB-12) — layer 2, 163,206 polygons (filter-required, T-21-03) |
| `GeoNB_ELG_Contaminated_Sites` | INTEGRATE | `nb_get_contaminated_sites` (NB-13) — layer 0, 9,736 points |
| `GeoNB_DNR_Crown_Land` | INTEGRATE | `nb_get_crown_land` (NB-14) — layer **3** (not 0), 10,001 polygons; the phase tracer |
| `GeoNB_SNB_Parcels` | INTEGRATE | `nb_get_parcels` (NB-17) — layer 0, 604,520 polygons (filter-required, T-21-03) |
| `GeoNB_DPS_Civic_Address` | INTEGRATE | `nb_get_civic_addresses` (NB-18) — layer 0, 373,172 points (filter-required, T-21-03) |
| `GeoNB_Health_Facilities` | INTEGRATE | `nb_get_health_facilities` (NB-19) — layers 0-5 facility-type dispatch |
| `GeoNB_EECD_PublicSchools` | INTEGRATE | `nb_get_public_schools` (NB-20) — layers 0/1 Anglophone/Francophone dispatch |

### Excluded — dead or non-attribute (18 OPT-OUT)

| capability (service) | decision | reason |
|---|---|---|
| `GeoNB_Basemap_Grey` | OPT-OUT | tile basemap, not attribute data — no agent value |
| `GeoNB_Basemap_Imagery` | OPT-OUT | tile basemap, not attribute data — no agent value |
| `GeoNB_Basemap_NBRN` | OPT-OUT | tile basemap, not attribute data — no agent value |
| `GeoNB_Basemap_Provinces_bare` | OPT-OUT | tile basemap, not attribute data — no agent value |
| `GeoNB_Basemap_Topo` | OPT-OUT | tile basemap, not attribute data — no agent value |
| `GeoNB_DNR_WildlifeRefuges` | OPT-OUT | layer 0 is literally named `"Retired Map Service"` and holds 1 placeholder polygon — live-verified dead service (RESEARCH Pitfall 3) |
| `GeoNB_SNB_ImageIndex` | OPT-OUT | imagery tile index, not attribute data |
| `GeoNB_SNB_ImageryYear` | OPT-OUT | imagery capture-year index, not attribute data |
| `GeoNB_SNB_LidarIndex` | OPT-OUT | lidar tile index, not attribute data |
| `GeoNB_SNB_NBDEMgrid` | OPT-OUT | elevation grid tile index, not attribute data |
| `GeoNB_SNB_NBDEMyear` | OPT-OUT | elevation capture-year index, not attribute data |
| `GeoNB_SNB_Scanned_Topo_Map_Index` | OPT-OUT | scanned-map tile index, not attribute data |
| `GeoNB_SNB_atlas_index` | OPT-OUT | atlas sheet index, not attribute data |
| `GeoNB_SNB_dtdb_index` | OPT-OUT | digital-topographic sheet index, not attribute data |
| `GeoNB_SNB_Atlas` | OPT-OUT | cartographic atlas rendering service, not attribute data |
| `GeoNB_SNB_Pan` | OPT-OUT | panchromatic imagery rendering service, not attribute data |
| `GeoNB_SNB_Server_Log_Metrics` | OPT-OUT | GeoNB server telemetry — operator diagnostics, not open data |
| `GeoNB_ScriptedUpdateTrackingData` | OPT-OUT | GeoNB internal ETL update tracking — operator diagnostics, not open data |

### Long tail — reachable, un-curated (35 OPT-OUT)

Every row below: **reason = reachable at runtime via `nb_list_geonb_services` → `nb_get_geonb_service_layers` → `nb_query_geonb_layer`; not individually curated per D-07 (highest-value service per sub-domain), tool budget at the D-08 ceiling of 22.** Each row adds its own specific note.

| capability (service) | decision | reason |
|---|---|---|
| `GeoNB_DNR_MineralOccurrences` | OPT-OUT | long tail (moved from Curated 2026-07-30) — reachable via `nb_query_geonb_layer(service_name="GeoNB_DNR_MineralOccurrences", layer_id=0)`, layer 0, 1,611 points; dropped by the 21-01 Task 2 checkpoint (option-a) to hold the D-08 22-tool budget after adding the two `gnb.socrata.com` tools — NB-15 in REQUIREMENTS.md is marked superseded by NB-09 |
| `GeoNB_DNR_ProvincialParks` | OPT-OUT | long tail (moved from Curated 2026-07-30) — reachable via `nb_query_geonb_layer(service_name="GeoNB_DNR_ProvincialParks", layer_id=0)`, layer 0, 24 polygons; same 21-01 checkpoint tradeoff as `GeoNB_DNR_MineralOccurrences` — NB-16 in REQUIREMENTS.md is marked superseded by NB-09 |
| `GeoNB_DEM_Coastal_Erosion` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; coastal erosion is covered thematically by `GeoNB_ELG_CoastalZones`, also un-curated |
| `GeoNB_DNR_Forest` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; 6 treatment/location tier layers need per-tier curation beyond the budget |
| `GeoNB_DNR_ForestSoils` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; soils are a specialist sub-domain below the D-07 bar |
| `GeoNB_DNR_NBHN` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; hydrographic network is a basemap-grade reference layer |
| `GeoNB_DNR_NonForest` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; 7 category tier layers need per-tier curation beyond the budget |
| `GeoNB_DPS_NB911_Communities` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; `nb_get_civic_addresses` is the higher-value SNB/DPS pick per D-07 |
| `GeoNB_ELG_Climate_Change_Adaptation_Plans` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; plan-document pointers rather than measurements |
| `GeoNB_ELG_CoastalZones` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; flood hazard + historical floods are the higher-value flood picks |
| `GeoNB_ELG_Local_Governance` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; administrative boundary layer below the D-07 bar |
| `GeoNB_ELG_LocalServiceDistricts` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; superseded by NB's 2023 local governance reform, historical value only |
| `GeoNB_ELG_WaterQuality_Lakes_Rivers` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; station catalogue only, no readings; contaminated sites is the higher-value ELG pick |
| `GeoNB_ELG_WAWA` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; Watercourse and Wetland Alteration Act permit areas overlap `nb_get_wetlands` |
| `GeoNB_ENB_Local_Government_Elections` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; electoral boundaries below the D-07 bar for this budget |
| `GeoNB_ENB_Provincial_Elections` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer` (layer 2 = 2024 districts); electoral boundaries below the D-07 bar |
| `GeoNB_ENB_RegionalHealthAuthorities` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; RHA names are shipped statically in `data://nb/health-regions` |
| `GeoNB_ENB_SchoolDistricts` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; district names are shipped statically in `data://nb/school-districts` |
| `GeoNB_ENV_Flood` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; overlaps `GeoNB_ENV_FloodHazardIndex`, the curated pick |
| `GeoNB_ENV_Flood_Link` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; link-out layer to external PDF flood maps, no queryable attributes of value |
| `GeoNB_ENV_ProtectedWatersheds` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; zone-tiered across layers 0-4, needs per-tier curation |
| `GeoNB_ENV_ProtectedWellfields` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; narrow regulatory layer below the D-07 bar |
| `GeoNB_Health_Boundaries` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; `nb_get_health_facilities` is the higher-value Health pick |
| `GeoNB_NRCan_FirstNations` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; federal NRCan layer republished, not first-party NB data |
| `GeoNB_NRCan_PlaceNames` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; federal NRCan gazetteer republished, not first-party NB data |
| `GeoNB_PETL_WorkingNB_Boundaries` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; single administrative boundary layer below the D-07 bar |
| `GeoNB_SNB_Buildings` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; building footprints carry no attributes beyond geometry |
| `GeoNB_SNB_Contours` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; elevation contours are cartographic geometry, not agent-queryable attributes |
| `GeoNB_SNB_Counties` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; NB's 15 counties are shipped statically in `data://nb/counties` |
| `GeoNB_SNB_FSAs` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; forward sortation areas are Canada Post reference geography, not NB data |
| `GeoNB_SNB_Historical_Municipal_Areas` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; pre-2023-reform boundaries, historical value only |
| `GeoNB_SNB_Municipal_Information` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; municipal attributes overlap the parcel/civic-address curated pair |
| `GeoNB_SNB_Municipal_Planning` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; zoning/planning overlays are municipality-scoped (municipal NB portals are a separate phase per CONTEXT.md) |
| `GeoNB_SNB_NRWN` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; national road network reference geometry, not NB attribute data |
| `GeoNB_SNB_SurveyControlNetwork` | OPT-OUT | long tail — reachable via `nb_query_geonb_layer`; geodetic survey monuments are a surveyor tool, no general agent value |

## Surface 4 — NB 511 (`511.gnb.ca/api/v2`, key-gated)

Every path probed 2026-07-30 returns **HTTP 400 `<Error><Message>Invalid Key</Message></Error>`** — the
endpoint set cannot be enumerated without a key, so the shipped surface mirrors Manitoba's three
tools (D-09).

| capability | decision | reason |
|---|---|---|
| `get/event` | INTEGRATE | `nb_get_road_events` (NB-21) — `NOT_CONFIGURED` stub until `NEW_BRUNSWICK_511_KEY` is set |
| `get/winterroads` | INTEGRATE | `nb_get_winter_road_conditions` (NB-22) — `NOT_CONFIGURED` stub |
| `get/cameras` | INTEGRATE | `nb_get_traffic_cameras` (NB-23) — `NOT_CONFIGURED` stub |
| `get/roadconditions` | OPT-OUT | not needed yet — shape unverifiable without a key; `get/winterroads` covers the road-surface need per the Manitoba precedent |
| `get/alerts` | OPT-OUT | not needed yet — shape unverifiable without a key; overlaps `get/event` |
| `get/ferries` | OPT-OUT | not needed yet — shape unverifiable without a key; NB ferry service is a narrow sub-domain |
| `get/constructionprojects` | OPT-OUT | not needed yet — shape unverifiable without a key; overlaps `get/event` |
| any further undocumented `get/*` paths | OPT-OUT | not enumerable — every path returns `Invalid Key` before revealing whether it exists. Revisit the whole surface when a key is obtained |

## Surface 5 — `gnb.socrata.com` (NB provincial Socrata portal — **resolved 2026-07-30, option-a**)

> **This surface contradicted CONTEXT.md's core premise, and the contradiction was resolved in
> New Brunswick's favour.** 21-CONTEXT.md states NB has no provincial catalogue and that "there
> is no NB Socrata instance" — that claim is FALSE and must not be repeated. Live-verified
> 2026-07-30: `https://gnb.socrata.com` answers `/api/catalog/v1` (**312 datasets**, 674 assets),
> `/resource/{id}.json` SoQL and `/api/views/{id}.json` — all HTTP 200, keyless. The federal-CKAN
> NB resource URLs point *at it* (`gnb.socrata.com/api/views/4zbh-z2ij/rows.csv`). Categories are
> populated (`GeoNB` 26, `Public Accounts` 24, `Senior Executive Expenses` 14, `Population and
> Demographics` 7, `Health and Wellness` 5, …). `shared/socrata.py` from Phase 20 applies with
> **zero new client code**. The `checkpoint:decision` in `21-01-PLAN.md` Task 2 resolved
> **option-a**: two new `nb_` tools join the discovery surface, reusing `shared/socrata.py`
> verbatim; D-01's federal-CKAN discovery stays locked and untouched. To hold the D-08 22-tool
> budget after adding these two tools, `nb_get_mineral_occurrences` and `nb_get_provincial_parks`
> were dropped to the long tail (see Surface 3 above) — both remain reachable via
> `nb_query_geonb_layer`.

| capability | decision | reason |
|---|---|---|
| `/api/catalog/v1` discovery (312 datasets) | INTEGRATE | `nb_search_gnb_socrata_datasets` (NB-25) — resolved by the 21-01 Task 2 checkpoint, option-a |
| `/resource/{id}.json` SoQL reads | INTEGRATE | `nb_query_gnb_socrata_dataset` (NB-25) — resolved by the 21-01 Task 2 checkpoint, option-a |
| `/api/views/{id}.json` dataset metadata | INTEGRATE | folded into `nb_query_gnb_socrata_dataset`, never a standalone tool — resolved by the 21-01 Task 2 checkpoint, option-a |
| `domain_category` aggregation | OPT-OUT | `nb_list_categories` already covers categorisation from the federal CKAN `subject`/`topic_category` facets — a redundant capability, not part of the checkpoint's promoted surface |
| `X-App-Token` authenticated reads | OPT-OUT | not needed — keyless reads verified working; matches the Nova Scotia precedent where the token slot exists but is unset |

---

## Recorded exclusions (not gaps)

- **Deferred Ideas (21-CONTEXT.md):** CKAN datastore SQL over NB tabular data; NB municipal portals
  (Fredericton, Moncton, Saint John); GeoNB basemap/imagery services; the PEI Socrata assumption.
- **Scoped to other phases:** Newfoundland and Labrador (Phase 22), Prince Edward Island (Phase 23).
- **Verified dead ends (do not re-investigate):** `data.gnb.ca`, `opendata.gnb.ca`, `nbopendata.ca`
  (all DNS failure); `geonb-snb.opendata.arcgis.com` Hub Search (HTTP 401).

*Matrix produced at plan time 2026-07-30. Every row carries a decision; every OPT-OUT carries a reason.*
