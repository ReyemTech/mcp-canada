# Phase 21 Plan 01 — Live GeoNB Spike

**Run:** 2026-07-30, against `https://geonb.snb.ca/arcgis/rest/services` using the newly-implemented
`shared/arcgis_hub.py:list_arcgis_server_services` / `get_arcgis_server_layers` (Task 3 of this
plan), plus the existing `get_layer_metadata` / `get_count`.

All 11 curated services in 21-RESEARCH.md's Code Examples table are re-verified live below.
**Verdict: 11/11 CONFIRMED — no layer id required correction in `constants.py`.**

## 1. GeoNB service directory (live)

`list_arcgis_server_services("https://geonb.snb.ca/arcgis/rest/services")` returned **62
services**, all `type: MapServer`, zero `FeatureServer` — confirms D-04/D-05's premise that GeoNB
is bare ArcGIS Server with no Hub Search API in front of it.

Full name/type list (62 entries, alphabetical as returned by the live directory):

```
GeoNB_Basemap_Grey                          MapServer
GeoNB_Basemap_Imagery                       MapServer
GeoNB_Basemap_NBRN                          MapServer
GeoNB_Basemap_Provinces_bare                MapServer
GeoNB_Basemap_Topo                          MapServer
GeoNB_DEM_Coastal_Erosion                   MapServer
GeoNB_DNR_Crown_Land                        MapServer
GeoNB_DNR_Forest                            MapServer
GeoNB_DNR_ForestSoils                       MapServer
GeoNB_DNR_MineralOccurrences                MapServer
GeoNB_DNR_NBHN                              MapServer
GeoNB_DNR_NonForest                         MapServer
GeoNB_DNR_ProvincialParks                   MapServer
GeoNB_DNR_WildlifeRefuges                   MapServer
GeoNB_DPS_Civic_Address                     MapServer
GeoNB_DPS_NB911_Communities                 MapServer
GeoNB_EECD_PublicSchools                    MapServer
GeoNB_ELG_Climate_Change_Adaptation_Plans   MapServer
GeoNB_ELG_CoastalZones                      MapServer
GeoNB_ELG_Contaminated_Sites                MapServer
GeoNB_ELG_Local_Governance                  MapServer
GeoNB_ELG_LocalServiceDistricts             MapServer
GeoNB_ELG_WaterQuality_Lakes_Rivers         MapServer
GeoNB_ELG_WAWA                              MapServer
GeoNB_ENB_Local_Government_Elections        MapServer
GeoNB_ENB_Provincial_Elections               MapServer
GeoNB_ENB_RegionalHealthAuthorities         MapServer
GeoNB_ENB_SchoolDistricts                    MapServer
GeoNB_ENV_Flood_Link                         MapServer
GeoNB_ENV_FloodHazardIndex                   MapServer
GeoNB_ENV_Flood                              MapServer
GeoNB_ENV_Historical_Floods                  MapServer
GeoNB_ENV_ProtectedWatersheds                MapServer
GeoNB_ENV_ProtectedWellfields                MapServer
GeoNB_ENV_Wetlands                           MapServer
GeoNB_Health_Boundaries                      MapServer
GeoNB_Health_Facilities                      MapServer
GeoNB_NRCan_FirstNations                     MapServer
GeoNB_NRCan_PlaceNames                       MapServer
GeoNB_PETL_WorkingNB_Boundaries              MapServer
GeoNB_ScriptedUpdateTrackingData             MapServer
GeoNB_SNB_atlas_index                        MapServer
GeoNB_SNB_Atlas                              MapServer
GeoNB_SNB_Buildings                          MapServer
GeoNB_SNB_Contours                           MapServer
GeoNB_SNB_Counties                           MapServer
GeoNB_SNB_dtdb_index                         MapServer
GeoNB_SNB_FSAs                               MapServer
GeoNB_SNB_Historical_Municipal_Areas         MapServer
GeoNB_SNB_ImageIndex                         MapServer
GeoNB_SNB_ImageryYear                        MapServer
GeoNB_SNB_LidarIndex                         MapServer
GeoNB_SNB_Municipal_Information              MapServer
GeoNB_SNB_Municipal_Planning                 MapServer
GeoNB_SNB_NBDEMgrid                          MapServer
GeoNB_SNB_NBDEMyear                          MapServer
GeoNB_SNB_NRWN                               MapServer
GeoNB_SNB_Pan                                MapServer
GeoNB_SNB_Parcels                            MapServer
GeoNB_SNB_Scanned_Topo_Map_Index             MapServer
GeoNB_SNB_Server_Log_Metrics                 MapServer
GeoNB_SNB_SurveyControlNetwork               MapServer
```

5 basemaps (`GeoNB_Basemap_*`) confirmed present, as documented in `GEONB_EXCLUDED_SERVICES`
(Task 4).

## 2. Curated layer-id re-verification

Each row calls `get_arcgis_server_layers` then, for the used layer(s), `get_layer_metadata` +
`get_count`.

| Service | Layer id used | Layer name | Record count | Key fields (raw, truncated shapefile names) | Verdict |
|---------|---------------|------------|---------------|-----------------------------------------------|---------|
| `GeoNB_ENV_FloodHazardIndex` | 0 | Flood Hazard / Risque d'innondation | 269 | `Sheet_Numb`, `Technical_`, `Flood_Haza`, `Technical1` | CONFIRMED |
| `GeoNB_ENV_Historical_Floods` | 0 (main) | 2008 and 2018 Flood Limits | 5 | `ID`, `KEY`, `FEATURE`, `SOURCE`, `LIMIT` | CONFIRMED |
| `GeoNB_ENV_Historical_Floods` | 8 (1973 event) | 1973 Flood Limits | 40 | `Id`, `Shape_Length` | CONFIRMED |
| `GeoNB_ENV_Wetlands` | 2 | Wetland | 163,206 | `Hectares`, `WETLAND_CLASS`, `STATUS`, `WC` | CONFIRMED |
| `GeoNB_ELG_Contaminated_Sites` | 0 | Contaminated Sites / Lieux contaminés | 9,736 | `Status_E`/`Status_F`, `FileOpenDate`, `PidType_E`/`PidType_F` | CONFIRMED |
| `GeoNB_DNR_Crown_Land` | 3 (only layer) | Crown Land / Terres de la Couronne | 10,001 | `HOLDER` (int, no domain — Pitfall 4), `OBJECTID` | CONFIRMED |
| `GeoNB_DNR_MineralOccurrences` | 0 | Mineral | 1,611 | `NAME`, `COMMODITIE`, `LAT`, `LON`; layer ids returned non-sequential (0,1,7,2,3,4,5,8,6) exactly as RESEARCH.md predicted | CONFIRMED |
| `GeoNB_DNR_ProvincialParks` | 0 | Provincial Parks | 24 | `NAME`/`Nom`, `AREA`, `Hectares` | CONFIRMED |
| `GeoNB_SNB_Parcels` | 0 (parcels; layer 1 is parcel labels, same 604,520 count) | parcels | 604,520 | `PID`, `COUNTY`, `Titles_Status`, `Gazette_Status` | CONFIRMED |
| `GeoNB_DPS_Civic_Address` | 0 | Civic_Addresses | 373,172 | `CIVIC_NUM`, `STREET`, `ST_TYPE_E`/`ST_TYPE_F`, `COMMUNITY` | CONFIRMED |
| `GeoNB_Health_Facilities` | 0-5 (facility-type dispatch) | Hospital(Horizon)/Hospital(Vitalité)/After-hours clinic/Adult residential centre/Licensed nursing home/Pharmacy | 12 / 11 / 33 / 493 / 68 / 234 | `Hospital_N`, `Hospital_O`, `Name_E`/`Name_F`, `Telephone_` (layers 0-1); layers 2-5 use a distinct, much wider Esri-geocoder-derived schema (see §4) | CONFIRMED |
| `GeoNB_EECD_PublicSchools` | 0 (Anglophone), 1 (Francophone) | Anglophone / Francophone | 206 / 89 | `strID`, `strNM`, `strAD1`, `strGR`, `strURL` | CONFIRMED |

**11/11 CONFIRMED.** No `constants.py` layer id needs correction from the RESEARCH.md Code
Examples table.

## 3. Retired-service check

`GeoNB_DNR_WildlifeRefuges` layer 0 live-verified: `name = "Retired Map Service"`, record count =
**1**. Confirms RESEARCH.md Pitfall 3 — this service is a dead placeholder, not live wildlife
refuge data. Stays in `GEONB_EXCLUDED_SERVICES` (Task 4); no curated tool is built on it.

## 4. Field-name capture

Exact `fields` array names for each curated layer (used for `schemas.py` field lists in Task 4 —
these are the live, truncated shapefile-derived names, not display names, per Pitfall 2):

- **FloodHazardIndex (layer 0):** `Shape`, `Map`, `Shape_Length`, `Shape_Area`, `OBJECTID_1`,
  `OBJECTID`, `Sheet_Numb`, `Technical_`, `Flood_Haza`, `Technical1`, `Shape_Leng`
- **Historical_Floods (layer 0, "2008 and 2018 Flood Limits"):** `OBJECTID_1`, `Shape`,
  `OBJECTID`, `ID`, `KEY`, `FEATURE`, `SOURCE`, `THEME`, `LENGTH`, `MINZ`, `MAXZ`, `LIMIT`,
  `Shape_Leng`, `Shape_Length`
- **Historical_Floods (layer 8, "1973 Flood Limits"):** `OBJECTID`, `Shape`, `Id`, `Shape_Length`
- **Wetlands (layer 2, "Wetland"):** `OBJECTID`, `Shape`, `ID`, `Shape_Length`, `Shape_Area`,
  `Hectares`, `WC`, `WETLAND_CLASS`, `STATUS`
- **Contaminated_Sites (layer 0):** `OBJECTID`, `Shape`, `Latitude`, `Longitude`, `PidType_F`,
  `PidType_E`, `FileOpenDate`, `FileNumber`, `FileClosedDate`, `Status_F`, `Status_E`,
  `Source_PID`, `PidInt`, `Location_Source_E`, `Location_Source_F`
- **Crown_Land (layer 3):** `OBJECTID`, `Shape`, `HOLDER`, `Shape_Length`, `Shape_Area`
- **MineralOccurrences (layer 0, "Mineral"):** `Shape`, `URN`, `LAT`, `LON`, `NAME`, `COMMODITIE`,
  `MIN_OCCR_U`, `OBJECTID`
- **ProvincialParks (layer 0):** `OBJECTID`, `NAME`, `Nom`, `Shape`, `Shape_Length`, `Shape_Area`,
  `AREA`, `Hectares`
- **SNB_Parcels (layer 0, "parcels"):** `OBJECTID`, `Shape`, `FEATURE`, `PID`, `PID_INT`,
  `LAST_UPDATE`, `COUNTY`, `PROPERTY_MAP`, `PAN_CODE`, `Titles_Status`, `Gazette_Status`,
  `Shape_Length`, `Shape_Area`
- **DPS_Civic_Address (layer 0):** `OBJECTID`, `Shape`, `CIVIC_NUM`, `ADDR_SYM`, `ADDR_DESC`,
  `NUM_SUFFIX`, `PID`, `STREET`, `ST_TYPE_E`, `ST_TYPE_F`, `RD_SIDE_E`, `RD_SIDE_F`, `ST_DIR_E`,
  `ST_DIR_F`, `COMMUNITY`, `ADD_TYPE_E`, `ADD_TYPE_F`, `DESCRIPT`, `STRUCT_E`, `STRUCT_F`,
  `STRU_NAME`, `ALT_ACCESS`, `COLL_MTHD`, `CREATED`, `MODIFIED`, `LATITUDE`, `LONGITUDE`,
  `CIV_ID`, `COUNTY`, `SUB_COUNT`
- **Health_Facilities (layer 0, Hospital/Horizon):** `OBJECTID`, `Shape`, `Hospital_N`,
  `Hospital_O`, `Mailing_Ad`, `Telephone_`, `Fax`, `Number_of_`, `Website___`, `POINT_X`,
  `POINT_Y`, `Name_E`, `Name_F`
- **Health_Facilities (layer 1, Hospital/Vitalité):** same shape as layer 0 minus `Number_of_`
- **Health_Facilities (layers 2-5, After-hours/Adult residential/Nursing home/Pharmacy):**
  publish through a much wider Esri-geocoder-derived schema (`Match_addr`, `LongLabel`,
  `AddNum`/`StName`/`StType` address-component fields, `Total__of_beds`,
  `F__of_current_clients`, etc. for layer 3) rather than the compact `Name_E`/`Telephone_` shape
  of layers 0-1 — `schemas.py`'s `NBHealthFacility` model normalizes across both shapes rather
  than mirroring either verbatim.
- **EECD_PublicSchools (layer 0, Anglophone):** `strID`, `strDST`, `strSEC`, `strNM`, `strAD1`,
  `strAD2`, `StrCM`, `strCT`, `strPC`, `strGR`, `strILEn`, `strILFr`, `strURL`, `intBuilt`,
  `OBJECTID`
- **EECD_PublicSchools (layer 1, Francophone):** same field set as layer 0

## 5. Summary

- 62-service directory live-confirmed via `list_arcgis_server_services` (D-06 proven).
- `get_arcgis_server_layers` + existing `get_layer_metadata`/`get_count` live-confirmed against
  all 11 curated services plus the retired-service check — 12 total live calls beyond the Task 1
  tracer, zero errors.
- Every layer id in 21-RESEARCH.md's Code Examples table is CONFIRMED; `constants.py` (Task 4)
  uses the RESEARCH.md values as-is.
- `GeoNB_DNR_WildlifeRefuges` layer 0 confirmed retired (1 placeholder record) — excluded.
