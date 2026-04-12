# :round_pushpin: Ontario Government Open Data

Provincial datasets from the [Ontario Open Data Catalogue](https://data.ontario.ca) (CKAN 3 API) with 3,000+ datasets from Ontario ministries and agencies. Includes curated population projections from the Ministry of Finance.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (6)

<!-- CATALOG:ontario:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ontario_search_datasets` | Search Ontario's Open Data Catalogue (data.ontario.ca) for datasets by keyword. | `query`, `filters`, `rows` |
| `ontario_get_dataset_details` | Get full details for a specific Ontario Open Data dataset including all resources. | `dataset_id` |
| `ontario_get_resource` | Get details for a specific data resource (file) from the Ontario Open Data Catalogue. | `resource_id` |
| `ontario_list_organizations` | List all Ontario government ministries and agencies that publish open data. | `sort` |
| `ontario_get_dataset_stats` | Get aggregate statistics for the Ontario Open Data Catalogue (data.ontario.ca). | -- |
| `ontario_get_population_projections` | Fetch Ontario Ministry of Finance population projections by region (2024-2051). | `year`, `recent`, `filter` |
<!-- CATALOG:ontario:end -->

## Prompts (4)

| Prompt | Type | Description |
|--------|------|-------------|
| `ontario_explore_data` | Guided | Discover and download Ontario provincial datasets |
| `ontario_quick_search` | Quick | Search for Ontario datasets by keyword |
| `ontario_browse_ministries` | Quick | Browse datasets by Ontario ministry |
| `ontario_population_data` | Guided | Get Ontario population projections by region |

## Resources (6)

| URI | Type | Description |
|-----|------|-------------|
| `data://ontario/ministries` | Catalog | Ontario ministries and agencies with CKAN org slugs |
| `data://ontario/popular-datasets` | Catalog | Frequently accessed Ontario datasets |
| `data://ontario/resource-formats` | Catalog | Available file formats on data.ontario.ca |
| `docs://ontario/ckan-guide` | Guide | Ontario CKAN API structure, filtering, pagination |
| `docs://ontario/population-projections-guide` | Guide | Population projections XLSX structure, regions, years |
| `template://ontario/dataset-report` | Template | Ontario dataset report with `{title}`, `{organization}`, `{resources}` |
