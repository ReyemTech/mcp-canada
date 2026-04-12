# :house_with_garden: York Region Municipal Open Data

Municipal datasets from **4 verified ArcGIS Hub portals** (York Region regional government, Markham, Newmarket, Aurora). First ArcGIS Hub module in mcp-canada -- second portal technology alongside CKAN.

> **Note:** Each portal gets the same 5 discovery tools with a portal-specific prefix (`york_region_`, `markham_`, `newmarket_`, `aurora_`). York Region additionally gets 5+1 curated tools. Markham gets 2 curated tools.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools -- Discovery (20, 5 per portal)

<!-- CATALOG:york_region_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `york_region_search_datasets` | Search York Region regional ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `york_region_get_dataset_details` | Get full details for a York Region regional Hub dataset by ID. | `dataset_id` |
| `york_region_query_features` | Query any York Region FeatureServer layer with WHERE clause and field selection. | `service_url`, `layer_id`, `where`, `out_fields`, `max_records` |
| `york_region_list_organizations` | List publisher organizations on the York Region Hub portal. | -- |
| `york_region_list_categories` | List dataset category tags on the York Region Hub portal. | -- |
| `markham_search_datasets` | Search City of Markham ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `markham_get_dataset_details` | Get full details for a Markham Hub dataset by ID. | `dataset_id` |
| `markham_query_features` | Query any Markham FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `markham_list_organizations` | List publisher organizations on the Markham Hub portal. | -- |
| `markham_list_categories` | List dataset category tags on the Markham Hub portal. | -- |
| `newmarket_search_datasets` | Search Town of Newmarket ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `newmarket_get_dataset_details` | Get full details for a Newmarket Hub dataset by ID. | `dataset_id` |
| `newmarket_query_features` | Query any Newmarket FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `newmarket_list_organizations` | List publisher organizations on the Newmarket Hub portal. | -- |
| `newmarket_list_categories` | List dataset category tags on the Newmarket Hub portal. | -- |
| `aurora_search_datasets` | Search Town of Aurora ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `aurora_get_dataset_details` | Get full details for an Aurora Hub dataset by ID. | `dataset_id` |
| `aurora_query_features` | Query any Aurora FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `aurora_list_organizations` | List publisher organizations on the Aurora Hub portal. | -- |
| `aurora_list_categories` | List dataset category tags on the Aurora Hub portal. | -- |
<!-- CATALOG:york_region_discovery:end -->

## Tools -- York Region Curated (5+1)

<!-- CATALOG:york_region_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `york_region_get_transit_stops` | Search YRT/Viva bus stops by name from York Region Transportation FeatureServer. | `query`, `include_geometry`, `max_records` |
| `york_region_get_transit_routes` | List YRT/Viva transit routes from York Region Transportation FeatureServer. | `route_short_name`, `include_geometry` |
| `york_region_get_road_network` | Fetch York Region regional road network (~762 roads) from FeatureServer. | `name`, `include_geometry`, `max_records` |
| `york_region_get_public_health` | Query York Region public health & safety data by location type (beach_water, hospital, drinking_water). | `location_type`, `include_geometry` |
| `york_region_get_census_demographics` | Query York Region 2021 Census demographics by Dissemination Area with optional municipality filter. | `dataset`, `csdname`, `max_records` |
| `york_region_get_waste_data` | Query York Region waste management data (diversion_statistics or sites). | `dataset`, `include_geometry` |
<!-- CATALOG:york_region_curated:end -->

## Tools -- Markham Curated (2)

<!-- CATALOG:markham_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `markham_get_addresses` | Search Markham civic address registry with optional street name filter. | `street`, `include_geometry`, `max_records` |
| `markham_get_road_network` | Query Markham SLRN (Street Location Reference Network) road network by road name. | `name`, `include_geometry`, `max_records` |
<!-- CATALOG:markham_curated:end -->

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `york_region_explore_transit` | Guided | YRT/Viva transit analysis |
| `york_region_explore_census` | Guided | Compare 2021 Census demographics across York Region municipalities |
| `york_region_explore_health` | Guided | Explore public health data -- beach water, hospitals, drinking water |
| `york_region_quick_dataset_search` | Quick | One-shot search across York Region and municipality portals |
| `markham_explore_infrastructure` | Guided | Explore Markham civic addresses and SLRN road network |

## Resources (8)

| URI | Type | Description |
|-----|------|-------------|
| `data://york_region/portals` | Catalog | All 10 York Region municipalities with portal status |
| `data://york_region/municipalities` | Catalog | All 9 local municipalities + region with 2021 Census data |
| `data://york_region/feature_services` | Catalog | York Region curated FeatureServer catalog |
| `docs://york_region/esri-field-naming` | Guide | ESRI field naming conventions |
| `docs://york_region/portal-landscape` | Guide | Which municipalities have ArcGIS Hub portals |
| `docs://york_region/census-variables` | Guide | 2021 Census focused field set |
| `docs://york_region/arcgis-query-patterns` | Guide | ArcGIS SQL WHERE clause syntax |
| `template://york_region/transit-query-response` | Template | YRT/Viva transit results template |
