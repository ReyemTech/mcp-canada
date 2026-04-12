# :city_sunrise: Toronto Open Data

Municipal datasets from the [City of Toronto Open Data Portal](https://open.toronto.ca) (CKAN 2.9 API) with 500+ datasets. Includes TTC transit schedules (GTFS), neighbourhood census profiles, 311 service requests, RentSafeTO apartment evaluations, and short-term rental registrations.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools -- Discovery (5)

<!-- CATALOG:toronto_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `toronto_search_datasets` | Search Toronto's Open Data portal (open.toronto.ca) for datasets by keyword. | `query`, `filter_query`, `rows` |
| `toronto_get_dataset_details` | Get full details for a specific Toronto Open Data dataset including all resources. | `dataset_id` |
| `toronto_get_resource` | Get details for a specific data resource (file) from the Toronto Open Data portal. | `resource_id` |
| `toronto_list_organizations` | List all City of Toronto divisions and agencies that publish open data. | -- |
| `toronto_get_dataset_stats` | Get aggregate statistics for the Toronto Open Data portal (open.toronto.ca). | -- |
<!-- CATALOG:toronto_discovery:end -->

## Tools -- Curated (7)

<!-- CATALOG:toronto_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `toronto_get_ttc_stops` | Search TTC (Toronto Transit Commission) stops by name from GTFS static schedule. | `query` |
| `toronto_get_ttc_routes` | List TTC (Toronto Transit Commission) routes from GTFS static schedule data. | `route_type` |
| `toronto_get_neighbourhood_profile` | Get census indicator data for Toronto neighbourhoods from the Neighbourhood Profiles dataset. | `neighbourhood`, `characteristic`, `limit` |
| `toronto_compare_neighbourhoods` | Compare a single census indicator across all 140 Toronto neighbourhoods. | `characteristic`, `limit` |
| `toronto_get_311_requests` | Fetch Toronto 311 service requests (citizen complaints and service calls) for a given year. | `year`, `ward`, `service_type`, `status`, `limit` |
| `toronto_get_rentsafe_evaluations` | Query RentSafeTO apartment building evaluation scores from City of Toronto inspections. | `ward`, `min_score`, `limit` |
| `toronto_get_short_term_rentals` | Query Toronto short-term rental (STR) operator registration records. | `ward`, `status`, `limit` |
<!-- CATALOG:toronto_curated:end -->

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `toronto_explore_city_data` | Guided | Discover and download Toronto municipal datasets |
| `toronto_quick_search` | Quick | Search for Toronto datasets by keyword |
| `toronto_explore_neighbourhood` | Guided | Explore census and service data for a neighbourhood |
| `toronto_ttc_transit` | Guided | Look up TTC stops and routes from GTFS data |
| `toronto_check_311` | Guided | Analyze 311 service requests by year/ward/type |
| `toronto_rental_analysis` | Guided | Analyze rental data -- RentSafeTO + short-term rentals |

## Resources (8)

| URI | Type | Description |
|-----|------|-------------|
| `data://toronto/city-divisions` | Catalog | City of Toronto divisions and agencies |
| `data://toronto/ward-list` | Catalog | All 25 Toronto city council wards with names |
| `data://toronto/neighbourhood-list` | Catalog | All 140 official Toronto neighbourhoods |
| `data://toronto/311-service-types` | Catalog | Common 311 service request type codes |
| `docs://toronto/ckan-guide` | Guide | Toronto CKAN API structure, dataset vs resource distinction |
| `docs://toronto/neighbourhood-profiles-guide` | Guide | Census indicator categories, how to look up characteristics |
| `docs://toronto/gtfs-guide` | Guide | TTC GTFS structure, stop vs route vs trip distinction |
| `template://toronto/neighbourhood-report` | Template | Neighbourhood profile with `{neighbourhood}`, `{indicators}`, `{ward}` |
