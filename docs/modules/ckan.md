# :open_file_folder: CKAN Open Data

80,000+ federal datasets from [open.canada.ca](https://open.canada.ca/data/en/api/3/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (7)

<!-- CATALOG:ckan:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ckan_search_datasets` | Search Canada's Open Data portal (open.canada.ca) for datasets by keyword. | `query`, `filters`, `rows`, `start`, `sort` |
| `ckan_get_dataset_details` | Get full details for a specific Canadian Open Data dataset including all resources. | `dataset_id` |
| `ckan_list_organizations` | List all Canadian federal government organizations on the Open Data portal. | `sort` |
| `ckan_search_by_tag` | Search Canadian Open Data portal datasets by tag or keyword label. | `tag`, `rows` |
| `ckan_get_resource` | Get details for a specific data resource (file) from Canada's Open Data portal. | `resource_id` |
| `ckan_list_groups` | List thematic dataset groups available on Canada's Open Data portal. | -- |
| `ckan_get_dataset_stats` | Get aggregate statistics for Canada's Open Data portal (open.canada.ca). | -- |
<!-- CATALOG:ckan:end -->

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `ckan_explore_federal_data` | Guided | Discover and download federal datasets from open.canada.ca |
| `ckan_quick_search` | Quick | Search for federal datasets by keyword |
| `ckan_browse_organizations` | Quick | Browse datasets by government organization |
| `ckan_browse_by_tag` | Quick | Browse datasets by topic tag |
| `ckan_portal_overview` | Quick | Get portal statistics and popular tags |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://ckan/federal-organizations` | Catalog | Federal org slugs for use in `organization=` search filter |
| `data://ckan/popular-tags` | Catalog | Most-used dataset tags on open.canada.ca |
| `data://ckan/resource-formats` | Catalog | Available resource file formats (CSV, XLSX, GeoJSON, etc.) |
| `docs://ckan/search-tips` | Guide | Advanced CKAN search syntax and filter examples |
| `docs://ckan/api-quirks` | Guide | Pagination, bilingual fields, resource vs dataset distinction |
| `template://ckan/dataset-summary` | Template | Dataset summary with `{title}`, `{organization}`, `{resources}` |
| `template://ckan/resource-report` | Template | Resource download report template |
