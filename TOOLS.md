# Tool Reference

Auto-generated from source. Do not edit manually.
Run `uv run python scripts/generate_catalog.py` to regenerate.
Browse the [documentation site](https://reyemtech.github.io/mcp-canada/tools/) for searchable navigation.

**295 tools** across 21 modules.

## Module: Meta / Discovery (3 tools)

Orchestration tools always available to agents — no discovery required.

### `execute_batch`

Execute multiple tool calls in parallel and return aggregated results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `calls` | `list[dict] | dict` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `list_modules`

List all registered API modules with tool counts and descriptions.

_No parameters._

### `plan_query`

Plan a multi-step query across Canadian government data APIs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `top_k` | `int` | `5` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: bank_of_canada (8 tools)

Bank of Canada Valet API tools: foreign exchange rates, interest rates (policy rate, CORRA, bond yields), commodity price indexes (BCPI), CPI inflation indicators, series metadata search, and group browsing.

### `boc_get_exchange_rates`

Get daily CAD exchange rates for one or all foreign currencies.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `currency` | `str | None` | `None` | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `recent` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_get_interest_rates`

Get Bank of Canada interest rates including policy rate, CORRA, and bond yields.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rate_type` | `str` | `'all'` | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `recent` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_get_commodity_prices`

Get Bank of Canada Commodity Price Index (BCPI) data by commodity category.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `commodity_type` | `str | None` | `None` | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `recent` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_get_inflation_data`

Get Consumer Price Index (CPI) inflation data from the Bank of Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `indicator` | `str | None` | `None` | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `recent` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_search_series`

Search available Bank of Canada Valet API data series by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_get_series_metadata`

Get metadata (label, description, link) for a specific Valet API series.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `series_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_get_observations`

Get raw time-series observations for any Bank of Canada Valet API series.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `series_names` | `str` | — | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `recent` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `boc_list_groups`

List all available data group collections in the Bank of Canada Valet API.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: open_parliament (10 tools)

Open Parliament API tools: search federal bills by keyword/session/status, get bill details and sponsor info, search MPs by name/party/province/riding, get party member lists, retrieve House of Commons vote records, get individual MP voting records, browse Hansard debate transcripts, and full-text search Hansard speeches.

### `parl_search_bills`

List Canadian federal bills filtered by session or status.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str | None` | `None` | — |
| `session` | `str | None` | `None` | — |
| `status` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_bill_details`

Get full details for a specific Canadian federal bill including sponsor and status history.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bill_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_politicians`

Search or list Canadian Members of Parliament by name, party, or province.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str | None` | `None` | — |
| `party` | `str | None` | `None` | — |
| `province` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_search_by_riding`

Find the MP or politician for a specific electoral riding in Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `riding` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_party_members`

Get the current Members of Parliament for a specific political party.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `party` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_votes`

Get House of Commons vote records, optionally filtered by session, bill, or result.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session` | `str | None` | `None` | — |
| `bill` | `str | None` | `None` | — |
| `result` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_voting_record`

Get votes an MP participated in, with house-wide totals per division.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `politician` | `str` | — | — |
| `session` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_debates`

Get Hansard debate transcripts from the House of Commons.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | `str | None` | `None` | — |
| `politician` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_search_hansard`

Full-text search of Canadian Hansard debate transcripts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `parl_get_ballots`

Get individual MP yea/nay ballots for a specific House of Commons vote.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vote_id` | `str` | — | — |
| `politician` | `str | None` | `None` | — |
| `page` | `int` | `1` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: recalls (6 tools)

Health Canada Recalls API tools: search and retrieve product recall information across all categories (food, vehicles, health products, consumer products). Get recent recalls, search by keyword, fetch full recall details with affected products, and filter by category.

### `recalls_get_recent`

Get the most recent product recalls across all Health Canada categories.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `25` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `recalls_search`

Search Health Canada recalls by keyword with optional category filter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str` | — | — |
| `category` | `str | None` | `None` | — |
| `limit` | `int` | `25` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `recalls_get_details`

Get full details of a specific Health Canada recall by recall ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `recall_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `recalls_get_food`

Get food product recalls from Health Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str | None` | `None` | — |
| `limit` | `int` | `25` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `recalls_get_vehicles`

Get vehicle recalls from Transport Canada and Health Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str | None` | `None` | — |
| `limit` | `int` | `25` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `recalls_get_health_products`

Get health product recalls from Health Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str | None` | `None` | — |
| `limit` | `int` | `25` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: drug_database (8 tools)

Health Canada Drug Product Database tools: search drugs by brand name, DIN, or company; get active ingredients, routes of administration, schedule classification, ATC therapeutic class, market status, and company details for Canadian drug products.

### `drug_search`

Search Health Canada's Drug Product Database for drug products.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `brand_name` | `str | None` | `None` | — |
| `din` | `str | None` | `None` | — |
| `company` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_details`

Get comprehensive details for a drug product in one call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_ingredients`

Get active ingredients for a Health Canada drug product.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_routes`

Get routes of administration for a Health Canada drug product.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_search_companies`

Search for pharmaceutical companies in Health Canada's Drug Product Database.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `company_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_schedule`

Get schedule classification for a Health Canada drug product.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_therapeutic_class`

Get ATC therapeutic classification for a Health Canada drug product.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `drug_get_status`

Get market status for a Health Canada drug product.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drug_code` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: ckan (7 tools)

CKAN Open Data portal tools (open.canada.ca): search 80,000+ Canadian government datasets by keyword or tag, get dataset details with resources, list federal organizations and thematic groups, retrieve individual resource metadata, and get portal-wide statistics. Descriptions truncated to save tokens.

### `ckan_search_datasets`

Search Canada's Open Data portal (open.canada.ca) for datasets by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `filters` | `str | None` | `None` | — |
| `rows` | `int` | `10` | — |
| `start` | `int` | `0` | — |
| `sort` | `str` | `'relevance asc'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_get_dataset_details`

Get full details for a specific Canadian Open Data dataset including all resources.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_list_organizations`

List all Canadian federal government organizations on the Open Data portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort` | `str` | `'name asc'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_search_by_tag`

Search Canadian Open Data portal datasets by tag or keyword label.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag` | `str` | — | — |
| `rows` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_get_resource`

Get details for a specific data resource (file) from Canada's Open Data portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resource_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_list_groups`

List thematic dataset groups available on Canada's Open Data portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ckan_get_dataset_stats`

Get aggregate statistics for Canada's Open Data portal (open.canada.ca).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: nutrient_file (8 tools)

Canadian Nutrient File tools: search foods by name, get detailed nutrition per 100g, serving sizes, food group browsing, list all nutrients and food groups, and compare nutritional content of 2-5 foods side by side. Data from Health Canada's Canadian Nutrient File database.

### `nutrient_search_foods`

Search Canadian Nutrient File foods by name using client-side filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_get_food_details`

Get detailed information about a specific food item from the Canadian Nutrient File.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `food_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_get_nutrient_amounts`

Get all nutrient amounts per 100g for a specific food from the Canadian Nutrient File.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `food_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_get_serving_sizes`

Get serving size measures and conversion factors for a food item.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `food_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_search_by_food_group`

List all foods within a specific food group from the Canadian Nutrient File.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `food_group_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_list_nutrients`

List all nutrients available in the Canadian Nutrient File database.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_list_food_groups`

List all food group categories in the Canadian Nutrient File database.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nutrient_compare_foods`

Compare nutritional content of 2-5 foods from the Canadian Nutrient File.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `food_ids` | `list[int]` | — | List of 2-5 food IDs to compare. |
| `format` | `Literal['by_food', 'by_nutrient']` | `'by_food'` | Output format — 'by_food' (food-keyed list) or 'by_nutrient' (nutrient pivot). |
| `nutrients` | `list[int] | None` | `None` | Optional list of nutrient_name_ids to filter comparison to specific nutrients. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Language code ('en' or 'fr'). |

## Module: weather (34 tools)

Environment Canada MSC GeoMet weather tools: current conditions, forecasts, alerts, climate data, air quality, hydrology, marine forecasts, severe weather, snow depth, and collection browsing. Covers 40+ tools across 9 sub-domains backed by the OGC API Features standard.

### `wx_get_aqhi`

Get current Air Quality Health Index (AQHI) reading for a location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `location_id` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_aqhi_forecast`

Get AQHI air quality forecast periods for a location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `location_id` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_aqhi_history`

Get historical AQHI observations for a location with optional date range.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location_id` | `str` | — | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `limit` | `int` | `50` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_climate_daily`

Get historical daily climate observations for a weather station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | Climate station identifier (e.g. "6158731" for Ottawa CDA). |
| `start_date` | `str | None` | `None` | Start of date range in ISO format (e.g. "2024-01-01"). |
| `end_date` | `str | None` | `None` | End of date range in ISO format (e.g. "2024-01-31"). |
| `limit` | `int` | `100` | Maximum records to return (default 100). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_get_climate_monthly`

Get monthly climate summary data for a weather station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | Climate station identifier. |
| `year` | `int | None` | `None` | Optional year filter (e.g. 2024). |
| `limit` | `int` | `12` | Maximum records to return (default 12). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_get_climate_normals`

Get 30-year climate normals for a weather station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | Climate station identifier. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_get_climate_projections`

Get CMIP5 or CMIP6 climate projection collection metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `Literal['cmip5', 'cmip6']` | `'cmip5'` | Climate model version — "cmip5" (default) or "cmip6". |
| `scenario` | `str | None` | `None` | Optional scenario label (informational only). |
| `variable` | `str | None` | `None` | Optional variable name (informational only). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_get_drought_index`

Get SPEI drought index collection metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float | None` | `None` | Optional latitude (informational context). |
| `lon` | `float | None` | `None` | Optional longitude (informational context). |
| `spei_period` | `int` | `3` | Accumulation period in months — 1, 3 (default), or 12. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_compare_climate_periods`

Compare daily climate averages between two time periods for a station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | Climate station identifier. |
| `period1_start` | `str` | — | First period start date (ISO format, e.g. "1990-01-01"). |
| `period1_end` | `str` | — | First period end date (ISO format, e.g. "1990-12-31"). |
| `period2_start` | `str` | — | Second period start date (ISO format, e.g. "2020-01-01"). |
| `period2_end` | `str` | — | Second period end date (ISO format, e.g. "2020-12-31"). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_get_climate_trends`

Get long-term climate trends from the AHCCD dataset.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str | None` | `None` | Optional AHCCD station id to filter trends (e.g. "1100120"). |
| `measurement_type` | `str | None` | `None` | Optional measurement type — "rain", "snow", or "total_precip". |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" (default) or "fr". |

### `wx_list_collections`

Browse all available MSC GeoMet weather data collections.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_collection_items`

Query any MSC GeoMet weather collection by ID and return its items.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_id` | `str` | — | — |
| `bbox` | `str | None` | `None` | — |
| `datetime_filter` | `str | None` | `None` | — |
| `properties` | `dict[str, Any] | None` | `None` | — |
| `limit` | `int` | `50` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_current_conditions`

Get current weather conditions for a Canadian location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `province` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_forecast`

Get the multi-day weather forecast for a Canadian location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `province` | `str | None` | `None` | — |
| `days` | `int` | `7` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_weather_alerts`

Get active weather alerts and warnings for Canada or a specific province.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `province` | `str | None` | `None` | — |
| `alert_type` | `str | None` | `None` | — |
| `limit` | `int` | `25` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_search_stations`

Search for Environment Canada climate observation stations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `province` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `name` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_station_data`

Get hourly climate observations from a specific Environment Canada station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | — |
| `date` | `str | None` | `None` | — |
| `limit` | `int` | `24` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_water_levels`

Get real-time water level readings at a Canadian hydrometric station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_number` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_water_flow`

Get real-time water discharge (flow rate) at a Canadian hydrometric station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_number` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_daily_mean_water`

Get daily mean water level and discharge for a hydrometric station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_number` | `str` | — | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_search_hydro_stations`

Search for hydrometric water monitoring stations by province or location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `province` | `str | None` | `None` | — |
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `name` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_flood_risk`

Get flood risk assessment for a hydrometric station by comparing current to historical max.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_number` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_marine_forecast`

Get marine weather forecasts for Canadian coastal and offshore waters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `province` | `str | None` | `None` | Two-letter province code to filter by region (e.g. "NS", "BC", "NL"). |
| `lat` | `float | None` | `None` | Latitude for location-based search. |
| `lon` | `float | None` | `None` | Longitude for location-based search. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_hurricane_tracks`

Get active hurricane and tropical storm track data for Canada and adjacent waters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_thunderstorm_outlook`

Get thunderstorm outlook regions and risk levels for Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `province` | `str | None` | `None` | Two-letter province code to filter results (e.g. "ON", "AB"). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_radar_data`

Get radar precipitation accumulation data for a location in Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | — | Latitude of the query location. |
| `lon` | `float` | — | Longitude of the query location. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_lightning`

Get lightning strike information for Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_uv_index`

Get UV index forecast for a location in Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float | None` | `None` | Latitude of the query location. |
| `lon` | `float | None` | `None` | Longitude of the query location. |
| `location` | `str | None` | `None` | Optional location name for context. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_snow_depth`

Get snow depth from the nearest SWOB real-time weather observation station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str | None` | `None` | MSC station ID for direct lookup (e.g. "6106000"). |
| `lat` | `float | None` | `None` | Latitude for nearest-station search. |
| `lon` | `float | None` | `None` | Longitude for nearest-station search. |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_snow_water_equivalent`

Get estimated snow water equivalent (SWE) from snow depth observations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str | None` | `None` | MSC station ID for direct lookup. |
| `lat` | `float | None` | `None` | Latitude for nearest-station search. |
| `lon` | `float | None` | `None` | Longitude for nearest-station search. |
| `density_factor` | `float` | `0.3` | Snow density as a fraction of water density (default 0.3). |
| `lang` | `Literal['en', 'fr']` | `'en'` | Response language — "en" for English, "fr" for French. |

### `wx_get_weather_summary`

Get a comprehensive weather summary combining current conditions, forecast, active alerts, and air quality.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float | None` | `None` | — |
| `lon` | `float | None` | `None` | — |
| `location` | `str | None` | `None` | — |
| `province` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_historical_extremes`

Get all-time weather records for a climate station: highest/lowest temperatures, most precipitation, most snowfall.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_growing_season`

Get growing season dates and frost-free period for a climate station based on 30-year normals.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `wx_get_heating_cooling_days`

Get cumulative heating and cooling degree days for energy analysis at a climate station.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_id` | `str` | — | — |
| `start_date` | `str | None` | `None` | — |
| `end_date` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: alberta (24 tools)

Alberta provincial government open data: CKAN catalogue (open.alberta.ca, 33,269 datasets), GeoDiscover Alberta ArcGIS REST 11.3, WMBappServices wildfire FeatureServers, AHSGIS health FeatureServers, Alberta Energy Regulator (AER) static reports (ST1/ST3/ST39), and 511 Alberta road/winter/camera APIs.

### `alberta_search_datasets`

Search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | `str` | `''` | — |
| `organization` | `str | None` | `None` | — |
| `format` | `str | None` | `None` | — |
| `rows` | `int` | `10` | — |
| `start` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_dataset_details`

Get full details (resources + curated extras) for a specific Alberta CKAN dataset.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_query_dataset`

Query a dataset's resource — auto-routes by format (ESRI REST -> ArcGIS query, CSV/XLSX/JSON -> file parse, others -> metadata only).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `resource_index` | `int` | `0` | — |
| `where` | `str | None` | `None` | — |
| `max_records` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_list_organizations`

List all 370 organizations publishing on open.alberta.ca CKAN.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_list_categories`

List dataset format categories from Alberta CKAN's res_format facet.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_well_licences_today`

Get today's AER well licences from ST1 daily report (TXT, rotates Mon-Sun).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_well_licences_archive`

Get monthly archive ZIP URL for AER ST1 well licences (discovery-only — large fixed-width files).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int` | — | — |
| `month` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_pipeline_statistics`

Get annual AER ST39 pipeline statistics XLSX (length by substance, year-by-year).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_production_volumes`

Get monthly oil/gas production volumes from AER ST3 (current month, 7 products).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_active_fires`

Get current active Alberta wildfires from WMBappServices ArcGIS Online (5-min refresh).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `None` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_fire_perimeters`

Get Alberta wildfire perimeters (active or extinguished) from WMBappServices simplified views.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `Literal['active', 'extinguished']` | `'active'` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_fire_bans`

Get current province-wide Alberta fire ban registry from WMBappServices.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_fire_control_orders`

Get Alberta fire control orders, OHV restrictions, or forest area boundaries from WMBappServices.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | `Literal['fire_control', 'ohv_restriction', 'forest_area']` | `'fire_control'` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_hospitals`

Get Alberta hospitals from AHSGIS AHS_Hospitals FeatureServer (~101 hospitals).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `zone` | `str | None` | `None` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_ahs_zones`

Get 5 Alberta Health Services (AHS) zones with boundaries and historical population.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_health_facilities`

Get Alberta health facilities from AHSGIS — EMS stations or PCN clinics (dispatched by facility_type).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `facility_type` | `Literal['ems', 'pcn_clinic']` | — | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_road_events`

Get Alberta road events (closures, construction, incidents, accidents) from 511 Alberta API.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `event_type` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_winter_road_conditions`

Get Alberta winter road conditions from 511 Alberta winterroads endpoint (~1,121 records).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `area_name` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_traffic_cameras`

Get Alberta traffic camera locations + snapshot URLs from 511 Alberta cameras endpoint (~376 cameras).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_air_quality_stations`

Get 75 Alberta AQHI air quality monitoring stations with current pollutant readings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_water_advisories`

Get Alberta water advisories from GeoDiscover River Forecast Centre — dispatched by advisory_type.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `advisory_type` | `Literal['river', 'water_management', 'drought', 'ice_cover', 'water_sharing']` | — | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_crop_production`

Get historical Alberta major crop production from open.alberta.ca CKAN (Alberta Official Statistic).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_population_estimates`

Get Alberta population estimates by breakdown — defaults to Census Subdivision (CSD) municipal level.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['csd', 'quarterly', 'annual', 'age_sex', 'sub_provincial', 'components_of_growth']` | `'csd'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `alberta_get_provincial_parks`

Get all Alberta provincial parks and protected areas from GeoDiscover boundary FeatureServer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: british_columbia (20 tools)

British Columbia provincial open data (BC Data Catalogue + BC Geographic Warehouse). Covers CKAN discovery at catalogue.data.gov.bc.ca PLUS direct WFS feature queries via openmaps.gov.bc.ca for geospatial layers. Curated topics: wildfires (active fires, historical perimeters), forestry (tenure, cut blocks), environment (protected areas, water wells, fish habitat), mining tenure, health facilities (emergency rooms, walk-in clinics), transportation (highways, road structures), and climate stations. All tools are prefixed bc_.

### `bc_search_datasets`

Search BC Data Catalogue for provincial open datasets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | `str` | — | — |
| `rows` | `int` | `20` | — |
| `start` | `int` | `0` | — |
| `organization` | `str | None` | `None` | — |
| `tag` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_dataset_details`

Get full BC dataset details including WFS routing metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_query_features`

Query features from a BC dataset via WFS or file download.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `filters` | `dict[str, Any] | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_list_organizations`

List BC government ministries and agencies that publish open data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_list_categories`

List BC Data Catalogue tag-based categories for dataset discovery.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_active_fires`

Query currently active wildfires in British Columbia from the BCGW WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `None` | — |
| `centre` | `str | None` | `None` | — |
| `min_size_hectares` | `float | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_fire_perimeters`

Query historical BC wildfire perimeters from the BCGW WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int | None` | `None` | — |
| `cause` | `str | None` | `None` | — |
| `min_size_hectares` | `float | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_forest_tenure`

Query BC forest tenure licences from the BCGW WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `'ACTIVE'` | — |
| `tenure_type` | `str | None` | `None` | — |
| `client_name` | `str | None` | `None` | — |
| `district` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_cut_blocks`

Query BC forest cut block polygons from the BCGW WFS (FTEN_CUT_BLOCK_POLY_SVW).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `'ACTIVE'` | — |
| `district` | `str | None` | `None` | — |
| `client_name` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_protected_areas`

Query BC protected lands from the BCGW WFS (WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `designation` | `str | None` | `None` | — |
| `min_area_ha` | `float | None` | `None` | — |
| `name` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_water_wells`

Query BC groundwater wells from the BCGW WFS (WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `city` | `str | None` | `None` | — |
| `well_class` | `str | None` | `None` | — |
| `aquifer_id` | `int | None` | `None` | — |
| `intended_use` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_wildfire_weather_stations`

Query BC wildfire weather monitoring stations from the BCGW WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str | None` | `None` | — |
| `min_elevation` | `int | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_local_parks`

Query BC local and regional parks from the BCGW WFS (WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `municipality` | `str | None` | `None` | — |
| `regional_district` | `str | None` | `None` | — |
| `park_type` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_mining_tenure`

Query BC mining tenure claims from the BCGW WFS (WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tenure_type` | `str | None` | `None` | — |
| `owner_name` | `str | None` | `None` | — |
| `min_area_ha` | `float | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_fish_habitat`

Query BC fish habitat holding areas from the BCGW WFS (WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `feature_code` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_emergency_rooms`

Query BC hospital emergency rooms from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `locality` | `str | None` | `None` | — |
| `wheelchair_accessible` | `bool | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_walk_in_clinics`

Query BC walk-in medical clinics from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `locality` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_highway_profiles`

Query BC highway profile segments from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `highway_number` | `str | None` | `None` | — |
| `admin_unit` | `str | None` | `None` | — |
| `min_lanes` | `int | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_road_structures`

Query BC road structures from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `structure_type` | `str | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `bc_get_climate_stations`

Query BC climate observation stations from the BCGW WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str | None` | `None` | — |
| `min_elevation` | `int | None` | `None` | — |
| `max_records` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: datastore (6 tools)

Local SQLite datastore tools: create tables, insert data, run SQL queries, list tables, inspect schemas, and drop tables. Persists data across server restarts at ~/.mcp-canada/datastore.db.

### `ds_create_table`

Create a named table in the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | — | — |
| `columns` | `list[dict] | None` | `None` | — |
| `data` | `list[dict] | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ds_insert_data`

Insert rows of data into an existing table in the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | — | — |
| `rows` | `list[dict]` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ds_query`

Run a read-only SQL query against the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sql` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ds_list_tables`

List all tables in the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ds_get_schema`

Get the column schema for a table in the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ds_drop_table`

Drop (delete) a table from the local SQLite datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: ircc (11 tools)

IRCC Immigration open data tools: permanent residents, study permits, work permits (TFWP and IMP), Express Entry admissions and invited candidates, TR-to-PR transitions, asylum claimants, operational processing, and Afghan refugees. Query immigration statistics by country, province, gender, age, and more.

### `ircc_get_permanent_residents`

Get IRCC permanent resident admissions data by breakdown dimension.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['country', 'province', 'gender', 'age', 'cma', 'noc', 'country_category', 'csd', 'adoptions']` | `'country'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_study_permits`

Get IRCC study permit issuance data by breakdown dimension.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['country', 'province_level', 'gender', 'annual_country', 'annual_province']` | `'country'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_work_permits`

Get IRCC work permit data for IMP (International Mobility Program) or TFWP (Temporary Foreign Worker Program).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `permit_type` | `Literal['imp', 'tfwp']` | `'imp'` | — |
| `breakdown` | `str` | `'province_program'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_express_entry`

Get IRCC Express Entry data for admissions or invited candidates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stream` | `Literal['admissions', 'invited']` | `'admissions'` | — |
| `breakdown` | `str` | `'gender'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_tr_to_pr`

Get IRCC data on temporary residents who transitioned to permanent residence.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['study_permit', 'imp', 'tfwp', 'pgwp']` | `'study_permit'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_asylum`

Get IRCC asylum claimant data by province and demographic breakdown.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['province_office', 'province_age', 'province_gender']` | `'province_office'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_ops`

Get IRCC operational processing statistics (monthly snapshots).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['pr_intake', 'copr_issued', 'study_processed', 'tr_processed', 'trv_intake', 'tr_approved', 'trv_v1_approved']` | `'pr_intake'` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_afghan`

Get IRCC data on Afghan refugees admitted to Canada.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['gender', 'age', 'education', 'language']` | `'gender'` | — |
| `year` | `int | None` | `None` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_adhoc_pr`

Get IRCC ad-hoc historical permanent resident data (1980-2023).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['category_1980', 'country_1980', 'province_cat_2000', 'province_citz_2000']` | `'category_1980'` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_get_citizenship`

Get IRCC new Canadian citizens data by country of birth (monthly).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breakdown` | `Literal['country']` | `'country'` | — |
| `recent` | `int | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ircc_list_datasets`

List all available IRCC open data datasets with their breakdown dimensions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: manitoba (20 tools)

Manitoba provincial government open data via geoportal.gov.mb.ca (Data MB) — an ArcGIS Hub powered by ArcGIS Online org mMUesHYPkXjaFGfS. 5 Hub discovery tools plus curated FeatureServer tools across flood/hydrology, agriculture & drought, environment/parks, regional health, and (conditional) Manitoba 511 transport.

### `manitoba_search_datasets`

Search Manitoba's geoportal.gov.mb.ca ArcGIS Hub catalogue by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `category` | `str | None` | `None` | — |
| `num` | `int` | `10` | — |
| `start` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_dataset_details`

Get full details for a Manitoba geoportal dataset by its Hub item ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_query_dataset`

Query a Manitoba dataset resource — auto-routes by URL type.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_url` | `str` | — | — |
| `where` | `str` | `'1=1'` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_list_organizations`

List Manitoba government organizations publishing on geoportal.gov.mb.ca.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_list_categories`

List dataset categories and themes on Manitoba's geoportal.gov.mb.ca.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_flood_alerts`

Get current overland flood watch and warning polygons for Manitoba.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_geometry` | `bool` | `True` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_river_stations`

Get Manitoba river and hydrometric station locations with flood status.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alert_only` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_provincial_waterways`

Get Manitoba provincial waterway infrastructure — dikes, floodways, dams, diversions, and reservoirs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `f_type` | `str | None` | `None` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_drought_status`

Get current drought monitor status for Manitoba from the Canada/USA Drought Monitor layer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter_province` | `bool` | `True` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_ag_weather_stations`

Get Manitoba agricultural weather station locations and live data links.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ag_region` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_livestock_prices`

Get Manitoba weekly livestock market prices from Manitoba Agriculture.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `livestock` | `str` | `'cattle'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_crop_regions`

Get Manitoba crop reporting region boundaries with bilingual region names.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_provincial_parks`

Get Manitoba provincial parks and protected areas (93 parks, bilingual).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `park_type` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_fisheries_data`

Get Manitoba fisheries and waterbody reference data (350+ water bodies).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `region` | `str | None` | `None` | — |
| `name` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_provincial_forests`

Get Manitoba provincial forest management boundaries.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_surgical_wait_times`

Get Manitoba diagnostic and surgical wait time averages by procedure and year.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `procedure` | `str | None` | `None` | — |
| `year` | `int | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_health_facilities`

Get Manitoba rural health care facilities with emergency, acute care, and PCH flags.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rha` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_road_events`

Get current road events (closures, construction, incidents) from Manitoba 511 API v3.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_winter_road_conditions`

Get winter road conditions on Manitoba's remote winter road network (seasonal).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `area_name` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `manitoba_get_traffic_cameras`

Get Manitoba highway traffic camera locations and snapshot image URLs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: new_brunswick (22 tools)

New Brunswick provincial government open data across four upstream surfaces: the federal open.canada.ca CKAN catalogue filtered to organization:nb (dataset discovery — NOT a provincial CKAN; data.gnb.ca/opendata.gnb.ca/nbopendata.ca do not resolve), gnb.socrata.com (New Brunswick's real provincial Socrata portal, 312 datasets, keyless), GeoNB (geonb.snb.ca) ArcGIS Server MapServer services (bare ArcGIS Server REST, NOT ArcGIS Hub — the Hub returns HTTP 401) covering flood hazard, wetlands, contaminated sites, Crown land, parcels, civic addresses, health facilities and public schools — minerals and provincial parks are reachable only through the long-tail nb_query_geonb_layer tool, not a dedicated curated tool — and NB 511 (511.gnb.ca) key-gated live road events, winter road conditions and traffic cameras.

### `nb_get_crown_land`

Get New Brunswick Crown Land parcels from GeoNB (geonb.snb.ca), layer 3.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `holder` | `int | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_search_datasets`

Search New Brunswick's federal-CKAN catalogue (open.canada.ca, 221 datasets).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `extra_fq` | `str | None` | `None` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_dataset_details`

Get full metadata for a single New Brunswick federal-CKAN dataset by id or name slug.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_query_dataset`

Query/parse a resource from a New Brunswick federal-CKAN dataset by resource index.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `resource_index` | `int` | `0` | — |
| `limit` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_list_organizations`

List New Brunswick's publishing organization and sections on the federal-CKAN catalogue.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_list_categories`

List New Brunswick's dataset subject, topic and format facets on the federal-CKAN catalogue.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_search_gnb_socrata_datasets`

Search New Brunswick's provincial Socrata portal (gnb.socrata.com, 312 datasets, keyless).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_query_gnb_socrata_dataset`

Query a New Brunswick gnb.socrata.com dataset via SoQL against /resource/{id}.json.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `where` | `str | None` | `None` | — |
| `select` | `str | None` | `None` | — |
| `limit` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_list_geonb_services`

List GeoNB's ArcGIS Server services via a live REST-directory walk.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `include_excluded` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_geonb_service_layers`

Get the layers/tables of a single GeoNB ArcGIS Server service, with

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_query_geonb_layer`

Query any GeoNB layer by service name and layer id — the long-tail

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_name` | `str` | — | — |
| `layer_id` | `int` | — | — |
| `where` | `str | None` | `None` | — |
| `out_fields` | `str` | `'*'` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_flood_hazard_areas`

Get New Brunswick flood hazard index polygons from GeoNB

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sheet` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_historical_floods`

Get New Brunswick's recorded historical flood limits from GeoNB

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `event` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_wetlands`

Get New Brunswick wetland polygons from GeoNB (GeoNB_ENV_Wetlands, layer 2).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wetland_class` | `str | None` | `None` | — |
| `status` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_contaminated_sites`

Get New Brunswick contaminated site points from GeoNB

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_parcels`

Get New Brunswick land parcels from GeoNB (GeoNB_SNB_Parcels, layer 0).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pid` | `str | None` | `None` | — |
| `county` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_civic_addresses`

Get New Brunswick civic addresses from GeoNB (GeoNB_DPS_Civic_Address, layer 0).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `community` | `str | None` | `None` | — |
| `street` | `str | None` | `None` | — |
| `civic_number` | `int | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_health_facilities`

Get New Brunswick health facilities from GeoNB (GeoNB_Health_Facilities),

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `facility_type` | `str` | — | — |
| `name` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_public_schools`

Get New Brunswick public schools from GeoNB (GeoNB_EECD_PublicSchools),

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sector` | `str` | `'anglophone'` | — |
| `district` | `str | None` | `None` | — |
| `limit` | `int` | `MAX_RECORDS` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_road_events`

Get current road events (closures, construction, incidents) from NB 511.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_winter_road_conditions`

Get winter road conditions on New Brunswick highways from NB 511 (seasonal).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `nb_get_traffic_cameras`

Get New Brunswick highway traffic camera locations from NB 511.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: nova_scotia (16 tools)

Nova Scotia provincial government open data via data.novascotia.ca — a Socrata (SODA API) portal. 5 catalog discovery tools plus curated tools across fishing/aquaculture (marine + landbased leases, hatchery stocking, production/employment), environment/water (surface water quality, boil-water advisories, protected areas, air-quality stations), and health + demographics (hospitals/LTC facilities, vital statistics, chronic disease prevalence). Keyless SODA reads; geometry excluded via $select. Transport/511 and the NS ArcGIS Hub (novagis) are deferred.

### `ns_search_datasets`

Search the Government of Nova Scotia open data catalogue on data.novascotia.ca (Socrata).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_dataset_details`

Get schema and metadata for a specific Nova Scotia dataset by its 4x4 dataset ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_query_dataset`

Run a SoQL query against any Nova Scotia Socrata dataset via /resource/{id}.json.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `where` | `str | None` | `None` | — |
| `select` | `str | None` | `None` | — |
| `order` | `str | None` | `None` | — |
| `limit` | `int` | `1000` | — |
| `offset` | `int` | `0` | — |
| `q` | `str | None` | `None` | — |
| `group` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_list_organizations`

List Nova Scotia government organizations and publishers on data.novascotia.ca.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_list_categories`

List Nova Scotia data categories from the data.novascotia.ca Socrata catalogue.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_marine_aquaculture_leases`

Get Nova Scotia marine aquaculture lease locations with species, owner, waterbody, county, status, and area.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `county` | `str | None` | `None` | — |
| `species_type` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_landbased_aquaculture_licenses`

Get Nova Scotia landbased aquaculture licenses with species type, owner, county, and operational status.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `county` | `str | None` | `None` | — |
| `species_type` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_fish_hatchery_stocking`

Get Nova Scotia fish hatchery stocking records with species, hatchery, county, fish size, count released, and stocking date.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stock` | `str | None` | `None` | — |
| `county` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_aquaculture_production`

Get Nova Scotia aquaculture production, value, and employment data by county and year.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `str | None` | `None` | — |
| `county` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_water_quality_monitoring`

Get Nova Scotia surface water quality continuous sensor readings (temperature, pH, conductance, dissolved oxygen).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `station_number` | `str | None` | `None` | — |
| `since` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_boil_water_advisories`

Get Nova Scotia boil water advisories with site name, county, date issued, date removed, facility type, and duration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `county` | `str | None` | `None` | — |
| `active_only` | `bool` | `False` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_protected_areas`

Get Nova Scotia protected areas with name, protection type, owner, authority, designation status, and area.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_air_quality_stations`

Get Nova Scotia ambient air quality monitoring station locations with measurements and monitoring period.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `city` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_health_facilities`

Get Nova Scotia hospital or long-term care facility locations by type, county, health zone, and beds.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `facility_type` | `str` | — | — |
| `county` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_vital_statistics`

Get Nova Scotia vital statistics (births, deaths, rates, natural increase) by county and year.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `county` | `str | None` | `None` | — |
| `year` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ns_get_chronic_disease_prevalence`

Get Nova Scotia chronic disease crude prevalence by health zone, sex, age group, and year.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `disease` | `str` | — | — |
| `health_zone` | `str | None` | `None` | — |
| `sex` | `str | None` | `None` | — |
| `year` | `str | None` | `None` | — |
| `limit` | `int` | `5000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: ontario (6 tools)

Ontario Government Open Data Catalogue (data.ontario.ca). 2,946+ datasets across 20+ ministries: Health, Education, Finance, Agriculture, Transportation, Environment, and more. Includes curated datasets such as population projections (2024–2051). Licensed under the Open Government Licence - Ontario.

### `ontario_search_datasets`

Search Ontario's Open Data Catalogue (data.ontario.ca) for datasets by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `filters` | `str | None` | `None` | — |
| `rows` | `int` | `10` | — |
| `start` | `int` | `0` | — |
| `sort` | `str` | `'relevance asc'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ontario_get_dataset_details`

Get full details for a specific Ontario Open Data dataset including all resources.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ontario_get_resource`

Get details for a specific data resource (file) from the Ontario Open Data Catalogue.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resource_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ontario_list_organizations`

List all Ontario government ministries and agencies that publish open data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort` | `str` | `'name asc'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ontario_get_dataset_stats`

Get aggregate statistics for the Ontario Open Data Catalogue (data.ontario.ca).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `ontario_get_population_projections`

Fetch Ontario Ministry of Finance population projections by age and gender (2024-2051).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | `str | None` | `None` | — |
| `year` | `int | None` | `None` | — |
| `gender` | `str | None` | `None` | — |
| `filter` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: quebec (18 tools)

Quebec Government Open Data — search the 1,593-dataset federated Données Québec catalogue (139 orgs) and access curated MSSS health, MTQ transport, environment, and demographics tools. CKAN discovery + datastore queries + MTQ WFS CSV endpoints. Default language: en.

### `quebec_search_datasets`

Search the Données Québec open data catalogue (1,593 datasets, 139 orgs).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | `str` | — | — |
| `rows` | `int` | `20` | — |
| `start` | `int` | `0` | — |
| `organization` | `str | None` | `None` | — |
| `group` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_dataset_details`

Get full details for a Données Québec dataset including resources list and datastore_active flags.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_query_dataset`

Query records from a Données Québec dataset's best resource (CSV > GeoJSON > JSON > XLSX).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `package_id` | `str` | — | — |
| `limit` | `int` | `100` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_list_organizations`

List all 139 organizations in the Données Québec federated catalog with package counts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_list_categories`

List the 10 thematic groups (Santé, Environnement, etc.) used to categorize Données Québec datasets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_health_installations`

Get Quebec health installations (hospitals, CLSCs, CHSLDs, psychiatric) from MSSS datastore.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `instal_type` | `str | None` | `None` | — |
| `rss_name` | `str | None` | `None` | — |
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_er_wait_times`

Get current Quebec emergency room wait times and stretcher occupancy (hourly refresh from MSSS).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `installation` | `str | None` | `None` | — |
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_population_by_municipality`

Get Quebec municipality population, area, and administrative region from the MAMH municipal registry.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `region` | `str | None` | `None` | — |
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_road_conditions`

Get current Quebec winter road conditions (pavement state, visibility) from MTQ WFS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_road_works`

Get current Quebec road construction zones and work sites from MTQ live WFS CSV.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_road_events`

Get current Quebec road events (accidents, incidents, warnings) from MTQ live WFS CSV.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_bridge_structures`

Get Quebec bridge, culvert, tunnel, and retaining wall inventory from MTQ structure registry.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route` | `str | None` | `None` | — |
| `municipality` | `str | None` | `None` | — |
| `region` | `str | None` | `None` | — |
| `limit` | `int` | `100` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_forest_fires_history`

Get the MFFP/MRN historical forest fire archive metadata and download URLs from Données Québec.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_air_quality_stations`

Get the RSQAQ air quality monitoring station network across Quebec (MELCCFP).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active_only` | `bool` | `True` | — |
| `limit` | `int` | `500` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_air_quality_index`

Get current Quebec air quality index (IQA) readings from the MELCCFP ArcGIS FeatureServer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_water_quality_monitoring`

Get the MELCCFP physicochemical water quality monitoring dataset metadata and download URLs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_electricity_data`

Get historical Quebec electricity production and consumption data from Hydro-Québec (via Données Québec CSV).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `500` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `quebec_get_protected_areas`

Get the MELCCFP protected areas registry (Registre des aires protégées) metadata and download URLs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: saskatchewan (13 tools)

Saskatchewan provincial government open data via geohub.saskatchewan.ca — an ArcGIS Hub powered by ArcGIS Online org zcv98lgAl8xQ04cW. 5 Hub discovery tools plus curated FeatureServer tools across agriculture (crop yields, grain elevators), energy/mining (potash/uranium/helium/coal), environment (fire bans, historic wildfires, air quality), and water (WSA hydrometric stations, reservoirs). Water data is on the separate WSA ArcGIS org 7MBdlVpjqbfBhQer; fire bans are on the SPSA REST server gis.saskatchewan.ca/egis.

### `saskatchewan_search_datasets`

Search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `category` | `str | None` | `None` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_dataset_details`

Get full metadata for a Saskatchewan GeoHub dataset by ID, including FeatureServer URL.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_query_dataset`

Query a Saskatchewan dataset via auto-router: FeatureServer, CSV/GeoJSON/XLSX, or metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `where` | `str` | `'1=1'` | — |
| `max_records` | `int` | `5000` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_list_organizations`

List Saskatchewan government publishing organizations on the geoportal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_list_categories`

List dataset categories and themes on Saskatchewan's ArcGIS Hub geoportal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_crop_yields`

Get Saskatchewan estimated crop yields (bu/acre) by region for 16 crop types.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `region` | `str` | `'provincial'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_grain_elevators`

Get Saskatchewan grain elevator locations with station, railway, licensee, and capacity.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `railway` | `Literal['CN', 'CP', 'SHORTLINE'] | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_mineral_mines`

Get Saskatchewan mineral mine locations for potash, uranium, helium, or coal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mineral` | `Literal['potash', 'uranium', 'helium', 'coal']` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_fire_bans`

Get current Saskatchewan fire ban status by scope from the SPSA Public Fire Ban FeatureServer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ban_scope` | `Literal['urban', 'rural', 'provincial', 'parks']` | `'urban'` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_historic_wildfires`

Get Saskatchewan historic wildfire boundaries with optional year and cause filters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int | None` | `None` | — |
| `cause` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_air_quality`

Get current hourly ambient air quality readings from Saskatchewan monitoring stations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `community` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_wsa_stations`

Get WSA hydrometric gauging station locations with basin, station class, and live graph links.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `basin` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `saskatchewan_get_wsa_reservoirs`

Get WSA reservoir locations with reservoir name, dam name, and water level (MASL).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: statcan (15 tools)

Statistics Canada tools: search tables, retrieve metadata, fetch time series data, and monitor data changes.

### `sc_search_cubes`

Search Statistics Canada tables (cubes) by keyword using BM25 ranking.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `limit` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_cube_metadata`

Get full metadata and dimension structure for a Statistics Canada table.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_code_sets`

Get all WDS code sets for decoding numeric codes in StatCan responses.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_series_info_by_vector`

Get series metadata by vectorId (title, frequency, scalar factor, units).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_series_info_by_coord`

Get series metadata by productId + coordinate (dot-separated dimension members).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product_id` | `int` | — | — |
| `coordinate` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_data_by_vector`

Get the latest N observations for a Statistics Canada series by vectorId.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_id` | `int` | — | — |
| `n` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_data_by_coord`

Get the latest N observations for a Statistics Canada series by productId + coordinate.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product_id` | `int` | — | — |
| `coordinate` | `str` | — | — |
| `n` | `int` | `10` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_data_by_date_range`

Get Statistics Canada observations within a reference period date range.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_id` | `int` | — | — |
| `start_date` | `str` | — | — |
| `end_date` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_bulk_vector_data`

Get observations for multiple Statistics Canada series within a release date range.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_ids` | `list[int]` | — | — |
| `start_release` | `str` | — | — |
| `end_release` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_changed_series`

Get the list of Statistics Canada series (vectors) that changed today.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_changed_cubes`

Get the list of Statistics Canada tables (cubes) that changed on a specific date.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_sdmx_structure`

Get SDMX dimension codelists for a Statistics Canada table.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product_id` | `int` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_sdmx_data`

Get server-side filtered StatCan observations using SDMX key syntax.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `product_id` | `int` | — | — |
| `key` | `str` | `''` | — |
| `start_period` | `str | None` | `None` | — |
| `end_period` | `str | None` | `None` | — |
| `last_n` | `int | None` | `None` | — |
| `dimensions` | `dict | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_get_sdmx_vector_data`

Get observations for a single StatCan vector via SDMX with date range filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_id` | `int` | — | — |
| `start_period` | `str | None` | `None` | — |
| `end_period` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `sc_fetch_vectors_to_store`

Fetch multiple StatCan vectors and store them to the shared datastore for SQL queries.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vector_ids` | `list[int]` | — | — |
| `start_release` | `str` | — | — |
| `end_release` | `str` | — | — |
| `table_name` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: toronto (12 tools)

Toronto Municipal Open Data Catalogue (open.toronto.ca). 300+ datasets: TTC transit GTFS (stops, routes, shapes), neighbourhood profiles (140 neighbourhoods, 2,000+ indicators), 311 service requests (annual ZIP+CSV), RentSafeTO apartment building evaluations, short-term rental (Airbnb) registrations, and city budget data. Licensed under the Open Government Licence - Toronto.

### `toronto_search_datasets`

Search Toronto's Open Data portal (open.toronto.ca) for datasets by keyword.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | — |
| `rows` | `int` | `10` | — |
| `start` | `int` | `0` | — |
| `sort` | `str` | `'score desc'` | — |
| `filter_query` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_dataset_details`

Get full details for a specific Toronto Open Data dataset including all resources.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_resource`

Get details for a specific data resource (file) from the Toronto Open Data portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resource_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_list_organizations`

List all City of Toronto divisions and agencies that publish open data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_dataset_stats`

Get aggregate statistics for the Toronto Open Data portal (open.toronto.ca).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_ttc_stops`

Search TTC (Toronto Transit Commission) stops by name from GTFS static schedule.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_ttc_routes`

List TTC (Toronto Transit Commission) routes from GTFS static schedule data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_type` | `str | None` | `None` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_neighbourhood_profile`

Get census indicator data for Toronto neighbourhoods from the Neighbourhood Profiles dataset.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `neighbourhood` | `str | None` | `None` | — |
| `characteristic` | `str | None` | `None` | — |
| `limit` | `int` | `100` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_compare_neighbourhoods`

Compare a single census indicator across all 140 Toronto neighbourhoods.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `characteristic` | `str` | — | — |
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_311_requests`

Fetch Toronto 311 service requests (citizen complaints and service calls) for a given year.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int` | — | — |
| `ward` | `str | None` | `None` | — |
| `service_type` | `str | None` | `None` | — |
| `status` | `str | None` | `None` | — |
| `limit` | `int` | `200` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_rentsafe_evaluations`

Query RentSafeTO apartment building evaluation scores from City of Toronto inspections.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ward` | `str | None` | `None` | — |
| `min_score` | `int | None` | `None` | — |
| `limit` | `int` | `100` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `toronto_get_short_term_rentals`

Query Toronto short-term rental (STR) operator registration records.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ward` | `str | None` | `None` | — |
| `status` | `str | None` | `None` | — |
| `limit` | `int` | `100` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

## Module: york_region (28 tools)

York Region and local municipal open data (Ontario). Covers 4 verified ArcGIS Hub portals: York Region regional government (transit, roads, demographics, public health, waste), City of Markham (addresses, roads), Town of Newmarket (discovery), and Town of Aurora (discovery). 6 other York Region municipalities have no public open data portal as of 2026-04 and their discovery tools return NOT_FOUND.

### `york_region_search_datasets`

Search York Region's ArcGIS Hub open data catalogue (insights-york.opendata.arcgis.com, ~442 datasets).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_dataset_details`

Get details for a specific dataset on York Region's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_query_features`

Query a York Region ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | `str` | — | — |
| `layer_id` | `int` | — | — |
| `where` | `str` | `'1=1'` | — |
| `out_fields` | `str` | `'*'` | — |
| `include_geometry` | `bool` | `False` | — |
| `max_records` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_list_organizations`

List all dataset owner organizations on York Region's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_list_categories`

List all dataset categories on York Region's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_search_datasets`

Search City of Markham's ArcGIS Hub open data catalogue (data-markham.opendata.arcgis.com).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_get_dataset_details`

Get details for a specific dataset on Markham's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_query_features`

Query a Markham ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | `str` | — | — |
| `layer_id` | `int` | — | — |
| `where` | `str` | `'1=1'` | — |
| `out_fields` | `str` | `'*'` | — |
| `include_geometry` | `bool` | `False` | — |
| `max_records` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_list_organizations`

List all dataset owner organizations on Markham's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_list_categories`

List all dataset categories on Markham's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `newmarket_search_datasets`

Search Town of Newmarket's ArcGIS Hub open data catalogue (navigate-newmarket.hub.arcgis.com).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `newmarket_get_dataset_details`

Get details for a specific dataset on Newmarket's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `newmarket_query_features`

Query a Newmarket ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | `str` | — | — |
| `layer_id` | `int` | — | — |
| `where` | `str` | `'1=1'` | — |
| `out_fields` | `str` | `'*'` | — |
| `include_geometry` | `bool` | `False` | — |
| `max_records` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `newmarket_list_organizations`

List all dataset owner organizations on Newmarket's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `newmarket_list_categories`

List all dataset categories on Newmarket's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `aurora_search_datasets`

Search Town of Aurora's ArcGIS Hub open data catalogue (town-of-aurora-data-hub-aurora.hub.arcgis.com).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `''` | — |
| `limit` | `int` | `10` | — |
| `offset` | `int` | `0` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `aurora_get_dataset_details`

Get details for a specific dataset on Aurora's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_id` | `str` | — | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `aurora_query_features`

Query an Aurora ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | `str` | — | — |
| `layer_id` | `int` | — | — |
| `where` | `str` | `'1=1'` | — |
| `out_fields` | `str` | `'*'` | — |
| `include_geometry` | `bool` | `False` | — |
| `max_records` | `int` | `1000` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `aurora_list_organizations`

List all dataset owner organizations on Aurora's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `aurora_list_categories`

List all dataset categories on Aurora's ArcGIS Hub portal.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_transit_stops`

Search York Region (YRT/Viva) transit stops from the GTFS-sourced FeatureServer. ~4,810 bus stops across the region.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_transit_routes`

List York Region (YRT/Viva) bus routes from the GTFS-sourced FeatureServer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_short_name` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_road_network`

Fetch the York Region regional road network (~762 regional roads).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_public_health`

Query York Region public health & safety datasets: beach water testing, hospital locations, or drinking water adverse incidents.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location_type` | `Literal['beach_water', 'hospital', 'drinking_water']` | — | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_census_demographics`

Fetch 2021 Canadian Census data (age/sex or income) by Dissemination Area for York Region municipalities.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset` | `Literal['age_sex', 'income']` | — | — |
| `csdname` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `york_region_get_waste_data`

Query York Region waste management data: annual diversion tonnages (2010-2021) or solid waste site locations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset` | `Literal['diversion_statistics', 'sites']` | — | — |
| `year` | `int | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_get_addresses`

Search Markham civic addresses (OD_ADDRESSES). Fields: FULL_ADDRESS, STREET, TYPE, MUNICIPALITY, WM_AREA.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `street` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |

### `markham_get_road_network`

Fetch the Markham Street & Linear Road Network (SLRN). Fields: NAME, TYPE, FULLNAME, OWNER. maxRecordCount=2000.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str | None` | `None` | — |
| `include_geometry` | `bool` | `False` | — |
| `lang` | `Literal['en', 'fr']` | `'en'` | — |
