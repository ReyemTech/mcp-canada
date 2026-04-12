# :fleur_de_lis: Quebec (Donnees Quebec) Open Data

Provincial datasets from [Donnees Quebec](https://www.donneesquebec.ca) -- a federated CKAN instance with 1,593 datasets across 139 organizations. All metadata is French-primary.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools -- Discovery (5)

<!-- CATALOG:quebec_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `quebec_search_datasets` | Search the Donnees Quebec open data catalogue (1,593 datasets, 139 orgs). | `q`, `rows`, `start`, `organization`, `group` |
| `quebec_get_dataset_details` | Get full details for a Donnees Quebec dataset including resources list and datastore_active flags. | `package_id` |
| `quebec_query_dataset` | Query records from a Donnees Quebec dataset's best resource (CSV > GeoJSON > JSON > XLSX). | `package_id`, `limit` |
| `quebec_list_organizations` | List all 139 organizations in the Donnees Quebec federated catalog with package counts. | -- |
| `quebec_list_categories` | List the 10 thematic groups (Sante, Environnement, etc.) used to categorize Donnees Quebec datasets. | -- |
<!-- CATALOG:quebec_discovery:end -->

## Tools -- Curated (13)

<!-- CATALOG:quebec_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `quebec_get_health_installations` | Get Quebec health installations (hospitals, CLSCs, CHSLDs, psychiatric) from MSSS datastore. | `instal_type`, `rss_name`, `limit` |
| `quebec_get_er_wait_times` | Get current Quebec emergency room wait times and stretcher occupancy (hourly refresh from MSSS). | `installation`, `limit` |
| `quebec_get_population_by_municipality` | Get Quebec municipality population, area, and administrative region from the MAMH municipal registry. | `region`, `limit` |
| `quebec_get_road_conditions` | Get current Quebec winter road conditions (pavement state, visibility) from MTQ WFS. | -- |
| `quebec_get_road_works` | Get current Quebec road construction zones and work sites from MTQ live WFS CSV. | -- |
| `quebec_get_road_events` | Get current Quebec road events (accidents, incidents, warnings) from MTQ live WFS CSV. | -- |
| `quebec_get_bridge_structures` | Get Quebec bridge, culvert, tunnel, and retaining wall inventory from MTQ structure registry. | `route`, `municipality`, `region`, `limit` |
| `quebec_get_forest_fires_history` | Get the MFFP/MRN historical forest fire archive metadata and download URLs from Donnees Quebec. | -- |
| `quebec_get_air_quality_stations` | Get the RSQAQ air quality monitoring station network across Quebec (MELCCFP). | `active_only`, `limit` |
| `quebec_get_air_quality_index` | Get current Quebec air quality index (IQA) readings from the MELCCFP ArcGIS FeatureServer. | `limit` |
| `quebec_get_water_quality_monitoring` | Get the MELCCFP physicochemical water quality monitoring dataset metadata and download URLs. | -- |
| `quebec_get_electricity_data` | Get historical Quebec electricity production and consumption data from Hydro-Quebec (via Donnees Quebec CSV). | `limit` |
| `quebec_get_protected_areas` | Get the MELCCFP protected areas registry (Registre des aires protegees) metadata and download URLs. | -- |
<!-- CATALOG:quebec_curated:end -->

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `quebec_explore_health` | Guided | Quebec health analysis: installations -> ER wait times -> population |
| `quebec_explore_transport` | Guided | Quebec transport analysis: road conditions -> works -> events -> bridges |
| `quebec_explore_environment` | Guided | Quebec environment analysis: air quality -> water quality -> protected areas |
| `quebec_quick_dataset_search` | Quick | Search Donnees Quebec by keyword |
| `quebec_active_fires_now` | Quick | Redirects to sopfeu.qc.ca (not on Donnees Quebec) |
| `quebec_electricity_overview` | Quick | Historical electricity production data from Hydro-Quebec |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://quebec/organizations` | Catalog | Top Donnees Quebec publishers with package counts |
| `data://quebec/thematic-groups` | Catalog | 10 thematic group codes with French names |
| `data://quebec/mtq-endpoints` | Catalog | MTQ WFS CSV endpoint URLs and confidence levels |
| `docs://quebec/catalog-federation-quirks` | Guide | Federated 139-org nature, Montreal overlap caveat |
| `docs://quebec/bilingual-metadata-guide` | Guide | French-primary metadata, bilingual content patterns |
| `template://quebec/health-report` | Template | Quebec health analysis report template |
| `template://quebec/transport-report` | Template | Quebec transport analysis report template |
