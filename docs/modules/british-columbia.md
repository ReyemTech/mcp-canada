# :evergreen_tree: British Columbia Open Data

Provincial datasets from the [BC Data Catalogue](https://catalogue.data.gov.bc.ca) (CKAN 2.9 API) and the [BC Geographic Warehouse](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/bc-spatial-data-infrastructure/bc-geographic-warehouse) WFS 2.0 endpoint. 13,000+ datasets.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools -- Discovery (5)

<!-- CATALOG:bc_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `bc_search_datasets` | Search BC Data Catalogue for datasets by keyword, organization, or filter query. | `q`, `rows`, `start`, `fq` |
| `bc_get_dataset_details` | Get full metadata for a BC Data Catalogue dataset including WFS queryability. | `package_id` |
| `bc_query_features` | Query any BCGW WFS layer by object_name with optional CQL filter. | `object_name`, `cql`, `max_records`, `include_geometry` |
| `bc_list_organizations` | List all BC Data Catalogue organizations (ministries and agencies). | -- |
| `bc_list_categories` | List available BC Data Catalogue tags for subject-area discovery. | -- |
<!-- CATALOG:bc_discovery:end -->

## Tools -- Curated WFS (15)

<!-- CATALOG:bc_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `bc_get_active_fires` | Fetch current active wildfire point locations from BCGW. | `fire_centre`, `fire_cause`, `min_size`, `max_records`, `include_geometry` |
| `bc_get_fire_perimeters` | Fetch historical wildfire perimeter polygons from BCGW. | `fire_year`, `min_size`, `max_records`, `include_geometry` |
| `bc_get_forest_tenure` | Fetch active BC forest tenure agreements from BCGW. | `client_name`, `max_records`, `include_geometry` |
| `bc_get_cut_blocks` | Fetch BC cut block (harvested area) polygons from BCGW. | `admin_district`, `max_records`, `include_geometry` |
| `bc_get_protected_areas` | Fetch BC provincial parks and protected areas from BCGW. | `designation`, `min_area_ha`, `max_records`, `include_geometry` |
| `bc_get_water_wells` | Fetch BC groundwater well records from BCGW. | `city`, `well_class`, `aquifer_id`, `max_records`, `include_geometry` |
| `bc_get_wildfire_weather_stations` | Fetch BC wildfire weather monitoring station locations from BCGW. | `station_name`, `max_records`, `include_geometry` |
| `bc_get_local_parks` | Fetch BC local and regional park boundaries from BCGW. | `municipality`, `park_type`, `max_records`, `include_geometry` |
| `bc_get_mining_tenure` | Fetch BC active mining tenure claims from BCGW. | `tenure_type`, `owner_name`, `max_records`, `include_geometry` |
| `bc_get_fish_habitat` | Fetch BC fish habitat and holding area features from BCGW. | `max_records`, `include_geometry` |
| `bc_get_emergency_rooms` | Fetch BC emergency room and urgent care facility locations from BCGW. | `locality`, `max_records`, `include_geometry` |
| `bc_get_walk_in_clinics` | Fetch BC walk-in clinic locations from BCGW. | `locality`, `max_records`, `include_geometry` |
| `bc_get_highway_profiles` | Fetch BC provincial highway profile segments from BCGW. | `highway_number`, `max_records`, `include_geometry` |
| `bc_get_road_structures` | Fetch BC road structure (bridge, tunnel, overpass) records from BCGW. | `structure_type`, `max_records`, `include_geometry` |
| `bc_get_climate_stations` | Fetch BC climate monitoring station locations from BCGW. | `station_name`, `max_records`, `include_geometry` |
<!-- CATALOG:bc_curated:end -->

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `bc_explore_wildfires` | Guided | Multi-step wildfire analysis |
| `bc_explore_forestry` | Guided | Forestry land use analysis |
| `bc_explore_environment` | Guided | Environmental pressure analysis |
| `bc_quick_dataset_search` | Quick | Two-step BC dataset discovery: CKAN search -> WFS queryability check |
| `bc_check_water_quality` | Quick | Retrieve BC groundwater well records |
| `bc_wildfire_status_now` | Quick | Get current active wildfire status |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://bc/ministries` | Catalog | BC ministry and agency CKAN org slugs |
| `data://bc/wildfire-status-codes` | Catalog | FIRE_STATUS + FIRE_CAUSE codes |
| `data://bc/object-name-prefixes` | Catalog | WHSE schema prefixes + curated layer mappings |
| `docs://bc/wfs-query-guide` | Guide | CKAN->WFS two-step workflow, CQL syntax |
| `docs://bc/bcdc-api-quirks` | Guide | BCDC custom fields, queryable_via_wfs |
| `template://bc/wildfire-report` | Template | Wildfire season report template |
| `template://bc/dataset-report` | Template | Dataset exploration report template |
