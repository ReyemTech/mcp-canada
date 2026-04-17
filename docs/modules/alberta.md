# :maple_leaf: Alberta Open Data

Provincial datasets from [open.alberta.ca](https://open.alberta.ca) -- a federated CKAN catalogue (33,269 datasets across 370 organizations) combined with Alberta Energy Regulator (AER) static reports, WMBappServices wildfire FeatureServers, AHSGIS health FeatureServers, GeoDiscover Alberta environmental/parks layers, and the 511 Alberta v2 JSON API.

All tools accept `lang: "en" | "fr"` for bilingual support. Alberta metadata is overwhelmingly English-only at source; FR responses surface English content with French structural messages.

## Tools -- Discovery (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_search_datasets` | Search 33,269 Alberta CKAN datasets by keyword + format/organization filters. | `q`, `rows`, `start`, `organization`, `format` |
| `alberta_get_dataset_details` | Get full dataset details with 50+ Alberta extras flattened. | `package_id` |
| `alberta_query_dataset` | Hybrid router — routes ESRI REST -> ArcGIS query, CSV/XLSX/JSON -> fetch_and_parse. | `package_id`, `resource_index`, `where`, `max_records` |
| `alberta_list_organizations` | List 370 federated organizations (current ministries + ~150 historical predecessors + Crown corps). | -- |
| `alberta_list_categories` | List dataset format categories via `res_format` facet (Alberta has no CKAN groups). | -- |

## Tools -- AER Energy (4)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_get_well_licences_today` | Today's AER ST1 daily well licences (TXT, overwritten by day-of-week MON/TUE/WED/.../SUN). | -- |
| `alberta_get_well_licences_archive` | AER ST1 monthly archive ZIP URL (discovery-only -- ZIP too large to auto-parse). | `year`, `month` |
| `alberta_get_pipeline_statistics` | AER ST39 annual pipeline statistics XLSX (length by substance, operator). | `year` |
| `alberta_get_production_volumes` | AER ST3 monthly production XLSX -- 7 case-sensitive products (Butane/Ethane/NGL/Oil/Gas/Propane/Sulphur). | `product` |

## Tools -- Wildfire (4)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_get_active_fires` | Current Alberta wildfires from WMBappServices `Active_Wildfires_Dashboard_view` (5-min refresh). | `status`, `max_records`, `include_geometry` |
| `alberta_get_fire_perimeters` | Wildfire perimeters (active simplified view or extinguished historical). | `status`, `max_records`, `include_geometry` |
| `alberta_get_fire_bans` | Province-wide fire ban / advisory / OHV restriction registry from WMBappServices. | `max_records`, `include_geometry` |
| `alberta_get_fire_control_orders` | Fire control orders, OHV restrictions, or forest area boundaries (3 layers dispatched by category). | `category`, `max_records`, `include_geometry` |

## Tools -- Health (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_get_hospitals` | ~101 Alberta Health Services hospitals with IP/ED capability flags (inpatient / emergency department). | `zone`, `max_records`, `include_geometry` |
| `alberta_get_ahs_zones` | 5 AHS zones (South / Calgary / Central / Edmonton / North) with historical population (2006/2011/2016). | `include_geometry` |
| `alberta_get_health_facilities` | EMS stations or PCN (Primary Care Network) clinics -- dispatched by facility_type. | `facility_type`, `max_records`, `include_geometry` |

## Tools -- Transport / 511 Alberta (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_get_road_events` | Current road closures, construction, incidents, accidents from 511 Alberta v2 API. | `event_type` |
| `alberta_get_winter_road_conditions` | Winter road conditions (~1,121 records) -- pavement, visibility, snow/ice (November-April season). | `area_name` |
| `alberta_get_traffic_cameras` | Traffic camera locations + snapshot URLs (~376 cameras, locations stable 24h). | -- |

## Tools -- Environment / Agriculture / Demographics / Parks (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `alberta_get_air_quality_stations` | 75 AQHI air quality monitoring stations with current pollutant readings (SO2/NO2/O3/PM2.5/etc.). | `max_records`, `include_geometry` |
| `alberta_get_water_advisories` | Water advisories dispatched by type (river / water_management / drought / ice_cover / water_sharing). | `advisory_type`, `max_records`, `include_geometry` |
| `alberta_get_crop_production` | Historical major crop production (wheat/canola/barley, 2000-2014) from open.alberta.ca CKAN. | -- |
| `alberta_get_population_estimates` | Population estimates by breakdown (csd / quarterly / annual / age_sex / sub_provincial / components_of_growth). | `breakdown` |
| `alberta_get_provincial_parks` | Alberta Parks network -- provincial parks, wildland parks, ecological reserves, recreation areas. | `max_records`, `include_geometry` |

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `alberta_explore_energy` | Guided | AER ST1/ST3/ST39 well licences -> production volumes -> pipeline statistics workflow |
| `alberta_explore_wildfires` | Guided | Active fires -> perimeters -> fire bans -> control orders situational awareness |
| `alberta_explore_health_or_transport` | Guided | Branches between health (hospitals / AHS zones / EMS-PCN) and transport (events / winter / cameras) |
| `alberta_quick_dataset_search` | Quick | One-shot open.alberta.ca CKAN catalogue search with format / organization filters |
| `alberta_check_road_conditions` | Quick | 511 Alberta road events + winter conditions + traffic cameras |
| `alberta_active_fires_now` | Quick | WMBappServices Active_Wildfires_Dashboard_view lookup with status filter |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://alberta/ministries` | Catalog | 14 current Alberta ministry slugs with bilingual EN/FR labels |
| `data://alberta/forest-areas` | Catalog | 10 Alberta Wildfire Forest Areas (FA_NAMEs) with approximate hectares |
| `data://alberta/ahs-zones` | Catalog | 5 Alberta Health Services zones with POP2006/2011/2016 figures |
| `docs://alberta/aer-data-guide` | Guide | AER static report surfaces (ST1/ST3/ST39) -> tool mapping, product slug casing, OneStop / ST57 deferrals |
| `docs://alberta/wildfire-data-guide` | Guide | WMBappServices vs CKAN source-of-truth matrix, fire status codes, FWI deferral, AB-23 water-licence guidance |
| `template://alberta/dataset-report` | Template | Dataset exploration report template with {placeholder} fields |
| `template://alberta/wildfire-report` | Template | Wildfire status report template with {placeholder} fields |

## Source attribution

Most Alberta open data uses the **Open Government Licence -- Alberta 2.0**. Per-dataset license is returned in `alberta_get_dataset_details`'s `license_id` extra. AER static reports (ST1/ST3/ST39) are public but are governed by AER's publication terms -- see [static.aer.ca](https://static.aer.ca). WMBappServices, AHSGIS, and 511 Alberta feeds are operational government publications.
