# Tool Reference

Auto-generated from source. Do not edit manually.
Run `uv run python scripts/generate_catalog.py` to regenerate.

**84 tools** across 8 modules.

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
| `station_id` | `str | None` | `None` | Optional station identifier to filter trends. |
| `measurement_type` | `str | None` | `None` | Optional measurement type (e.g. "temperature", "precipitation"). |
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
