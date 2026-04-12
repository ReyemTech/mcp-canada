# :bar_chart: Statistics Canada

Time series data, cube metadata, catalog search, and SDMX server-side filtering from the [Statistics Canada Web Data Service](https://www.statcan.gc.ca/en/developers/wds).

> Inspired by [mcp-statcan](https://github.com/aryanjhaveri/mcp-statcan) by Aryan Jhaveri.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (15)

<!-- CATALOG:statcan:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `sc_search_cubes` | Search Statistics Canada tables (cubes) by keyword using BM25 ranking. | `query`, `limit` |
| `sc_get_cube_metadata` | Get full metadata and dimension structure for a Statistics Canada table. | `product_id` |
| `sc_get_code_sets` | Get all WDS code sets for decoding numeric codes in StatCan responses. | -- |
| `sc_get_series_info_by_vector` | Get series metadata by vectorId (title, frequency, scalar factor, units). | `vector_id` |
| `sc_get_series_info_by_coord` | Get series metadata by productId + coordinate (dot-separated dimension members). | `product_id`, `coordinate` |
| `sc_get_data_by_vector` | Get the latest N observations for a Statistics Canada series by vectorId. | `vector_id`, `n` |
| `sc_get_data_by_coord` | Get the latest N observations for a Statistics Canada series by productId + coordinate. | `product_id`, `coordinate`, `n` |
| `sc_get_data_by_date_range` | Get Statistics Canada observations within a reference period date range. | `vector_id`, `start_date`, `end_date` |
| `sc_get_bulk_vector_data` | Get observations for multiple Statistics Canada series within a release date range. | `vector_ids`, `start_release`, `end_release` |
| `sc_get_changed_series` | Get the list of Statistics Canada series (vectors) that changed today. | -- |
| `sc_get_changed_cubes` | Get the list of Statistics Canada tables (cubes) that changed on a specific date. | `date` |
| `sc_get_sdmx_structure` | Get SDMX dimension codelists for a Statistics Canada table. | `product_id` |
| `sc_get_sdmx_data` | Get server-side filtered StatCan observations using SDMX key syntax. | `product_id`, `key`, `last_n`, `start_period`, `end_period`, `dimensions` |
| `sc_get_sdmx_vector_data` | Get observations for a single StatCan vector via SDMX with date range filtering. | `vector_id`, `start_period`, `end_period` |
| `sc_fetch_vectors_to_store` | Fetch multiple StatCan vectors and store them to the shared datastore for SQL queries. | `vector_ids`, `start_release`, `end_release`, `table_name` |
<!-- CATALOG:statcan:end -->

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `statcan_find_data` | Guided | Search for StatCan cubes and get vector data |
| `statcan_quick_vector` | Quick | Get the latest N observations for a known vectorId |
| `statcan_explore_sdmx` | Guided | Explore and filter StatCan data using SDMX key syntax |
| `statcan_store_and_query` | Guided | Cross-module flagship: fetch vectors -> store -> SQL JOIN |
| `statcan_monitor_changes` | Quick | Check which StatCan series changed today |
| `statcan_compare_series` | Guided | Compare multiple StatCan time series |

## Resources (8)

| URI | Type | Description |
|-----|------|-------------|
| `data://statcan/frequency-codes` | Catalog | WDS frequency codes with bilingual labels |
| `data://statcan/scalar-factor-codes` | Catalog | WDS scalar factor codes (units multipliers) |
| `data://statcan/status-codes` | Catalog | WDS data status codes (provisional, revised, etc.) |
| `data://statcan/uom-codes` | Catalog | WDS unit of measure codes with bilingual labels |
| `docs://statcan/wds-guide` | Guide | WDS API overview, productId structure, coordinate system |
| `docs://statcan/sdmx-key-syntax` | Guide | SDMX key syntax for filtered data retrieval |
| `docs://statcan/coordinate-system` | Guide | How to build dot-separated dimension coordinates |
| `template://statcan/time-series-report` | Template | Time series report with `{product_id}`, `{vector_id}`, `{observations}` |
