<p align="center">
  <h1 align="center">🍁 mcp-canada</h1>
  <p align="center">
    <strong>MCP server giving AI agents structured access to Canadian federal government data</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/mcp-canada/"><img src="https://img.shields.io/pypi/v/mcp-canada?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml"><img src="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/integration.yml"><img src="https://github.com/ReyemTech/mcp-canada/actions/workflows/integration.yml/badge.svg" alt="Integration Tests"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python 3.12+"></a>
    <a href="https://github.com/reyemtech/mcp-canada/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP Compatible"></a>
    <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/built%20with-FastMCP-orange" alt="Built with FastMCP"></a>
  </p>
</p>

---

**128 tools** across **9 federal APIs + 1 provincial API + 1 municipal API + 1 local SQLite datastore** — exchange rates, parliamentary data, product recalls, drug information, 80K+ open datasets, food nutrition data, real-time weather, immigration statistics, Ontario provincial data, Toronto municipal data, and persistent local storage. All bilingual (English/French).


## Quick Start

```bash
# Auto-configure your platform (interactive)
uvx mcp-canada install

# Or name platforms directly
uvx mcp-canada install claude-desktop cursor vscode
```

Supports 14 platforms: Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, Zed, Codex CLI, Gemini CLI, Amazon Q, OpenCode, Cline, Roo Code, Goose CLI, Junie CLI.

### Manual Setup

<details>
<summary>Claude Desktop</summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-canada": {
      "command": "uvx",
      "args": ["mcp-canada"]
    }
  }
}
```
</details>

<details>
<summary>Claude Code</summary>

```bash
claude mcp add mcp-canada -- uvx mcp-canada
```
</details>

<details>
<summary>From Source</summary>

```bash
git clone https://github.com/reyemtech/mcp-canada.git
cd mcp-canada
uv run mcp-canada
```
</details>

### Options

| Flag | Description | Example |
|------|-------------|---------|
| `--transport` | Transport protocol | `--transport sse` |
| `--port` | Port for SSE/HTTP | `--port 8000` |
| `--modules` | Load only specific modules | `--modules bank_of_canada,recalls` |
| `--verbose` | INFO-level logging | `--verbose` |
| `--debug` | DEBUG-level logging | `--debug` |

Environment variable: `MCP_CANADA_MODULES=bank_of_canada,recalls`

## Examples

See **[EXAMPLES.md](EXAMPLES.md)** for 23 cross-API intelligence scenarios — from tracing prairie drought to the Canadian dollar, to building pharmaceutical safety audits, to assembling MP accountability briefs, to joining data from multiple APIs in a single SQL query. Each example includes the exact prompt and tool chain you can run today.

## How Discovery Works

With 110 tools, listing all of them would consume half an agent's context window. Instead, **BM25 search** lets agents find exactly what they need:

```
Agent: "What tools do you have for exchange rates?"

→ discover_tools("exchange rate CAD")
→ Returns: boc_get_exchange_rates, boc_get_observations

→ call_tool("boc_get_exchange_rates", {"currency": "USD", "recent": 3})
→ Returns: {"_meta": {...}, "data": [{"date": "2026-04-02", "value": 1.3918, ...}]}
```

Agents see **5 always-visible tools**:

| Tool | Purpose |
|------|---------|
| `discover_tools` | BM25 natural language search across all tools |
| `call_tool` | Execute any discovered tool by name |
| `list_modules` | List available API modules with tool counts |
| `plan_query` | Plan a multi-step query across Canadian government data APIs |
| `execute_batch` | Run multiple tool calls in parallel with per-step error isolation |

---

## Tool Catalog

All tools accept `lang: "en" | "fr"` for bilingual support. Responses include a `_meta` envelope with source attribution and cache status.

### 🔍 Meta / Discovery — 5 tools (always visible)

Orchestration tools always available to agents — no discovery required.

<!-- CATALOG:meta:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `execute_batch` | Execute multiple tool calls in parallel and return aggregated results. | `calls` |
| `list_modules` | List all registered API modules with tool counts and descriptions. | — |
| `plan_query` | Plan a multi-step query across Canadian government data APIs. | `query`, `top_k` |
<!-- CATALOG:meta:end -->

---

### 🏦 Bank of Canada — 8 tools

Exchange rates, interest rates, commodity prices, and inflation data from the [Valet API](https://www.bankofcanada.ca/valet/).

<!-- CATALOG:bank_of_canada:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `boc_get_exchange_rates` | Get daily CAD exchange rates for one or all foreign currencies. | `currency`, `start_date`, `end_date`, `recent` |
| `boc_get_interest_rates` | Get Bank of Canada interest rates including policy rate, CORRA, and bond yields. | `rate_type`, `start_date`, `end_date`, `recent` |
| `boc_get_commodity_prices` | Get Bank of Canada Commodity Price Index (BCPI) data by commodity category. | `commodity_type`, `start_date`, `end_date`, `recent` |
| `boc_get_inflation_data` | Get Consumer Price Index (CPI) inflation data from the Bank of Canada. | `indicator`, `start_date`, `end_date`, `recent` |
| `boc_search_series` | Search available Bank of Canada Valet API data series by keyword. | `keyword` |
| `boc_get_series_metadata` | Get metadata (label, description, link) for a specific Valet API series. | `series_name` |
| `boc_get_observations` | Get raw time-series observations for any Bank of Canada Valet API series. | `series_names`, `start_date`, `end_date`, `recent` |
| `boc_list_groups` | List all available data group collections in the Bank of Canada Valet API. | — |
<!-- CATALOG:bank_of_canada:end -->

<details>
<summary>Example: Get USD/CAD exchange rate</summary>

```
call_tool("boc_get_exchange_rates", {"currency": "USD", "recent": 3})
```

```json
{
  "_meta": {
    "source": {"api": "bank-of-canada-valet", "url": "https://www.bankofcanada.ca/valet/"},
    "cached": false,
    "lang": "en",
    "timestamp": "2026-04-04T22:16:54.133649+00:00"
  },
  "data": [
    {"date": "2026-04-02", "series_name": "FXUSDCAD", "value": 1.3918, "label": "USD/CAD", "description": "US dollar to Canadian dollar daily exchange rate"},
    {"date": "2026-04-01", "series_name": "FXUSDCAD", "value": 1.3888, "label": "USD/CAD", "description": "..."},
    {"date": "2026-03-31", "series_name": "FXUSDCAD", "value": 1.3939, "label": "USD/CAD", "description": "..."}
  ]
}
```

</details>

---

### 🏛️ Open Parliament — 10 tools

Bills, MPs, votes, ballots, and Hansard debates from the [Open Parliament API](https://api.openparliament.ca/).

<!-- CATALOG:open_parliament:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `parl_search_bills` | List Canadian federal bills filtered by session or status. | `keyword`, `session`, `status`, `page` |
| `parl_get_bill_details` | Get full details for a specific Canadian federal bill including sponsor and status history. | `bill_id` |
| `parl_get_politicians` | Search or list Canadian Members of Parliament by name, party, or province. | `name`, `party`, `province`, `page` |
| `parl_search_by_riding` | Find the MP or politician for a specific electoral riding in Canada. | `riding` |
| `parl_get_party_members` | Get the current Members of Parliament for a specific political party. | `party` |
| `parl_get_votes` | Get House of Commons vote records, optionally filtered by session, bill, or result. | `session`, `bill`, `result`, `page` |
| `parl_get_voting_record` | Get votes an MP participated in, with house-wide totals per division. | `politician`, `session`, `page` |
| `parl_get_debates` | Get Hansard debate transcripts from the House of Commons. | `date`, `politician`, `page` |
| `parl_search_hansard` | Full-text search of Canadian Hansard debate transcripts. | `query`, `page` |
| `parl_get_ballots` | Get individual MP yea/nay ballots for a specific House of Commons vote. | `vote_id`, `politician`, `page` |
<!-- CATALOG:open_parliament:end -->

<details>
<summary>Example: How did an MP vote on a specific bill?</summary>

```
call_tool("parl_get_ballots", {"vote_id": "44-1/333", "politician": "anna-roberts"})
```

```json
{
  "_meta": {"source": {"api": "Open Parliament", "url": "https://api.openparliament.ca/"}, "cached": false, "lang": "en", "timestamp": "..."},
  "data": [
    {"vote_url": "/votes/44-1/333/", "politician_url": "/politicians/anna-roberts/", "ballot": "No"}
  ]
}
```

</details>

> **Note:** `parl_get_voting_record` returns house-wide totals, not individual MP votes. Use `parl_get_ballots` for how a specific MP voted on a specific division.

---

### ⚠️ Recalls & Safety Alerts — 6 tools

Food, vehicle, and health product recalls from [Healthy Canadians](https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/).

<!-- CATALOG:recalls:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `recalls_get_recent` | Get the most recent product recalls across all Health Canada categories. | `limit`, `offset` |
| `recalls_search` | Search Health Canada recalls by keyword with optional category filter. | `keyword`, `category`, `limit`, `offset` |
| `recalls_get_details` | Get full details of a specific Health Canada recall by recall ID. | `recall_id` |
| `recalls_get_food` | Get food product recalls from Health Canada. | `keyword`, `limit`, `offset` |
| `recalls_get_vehicles` | Get vehicle recalls from Transport Canada and Health Canada. | `keyword`, `limit`, `offset` |
| `recalls_get_health_products` | Get health product recalls from Health Canada. | `keyword`, `limit`, `offset` |
<!-- CATALOG:recalls:end -->

---

### 💊 Drug Product Database — 8 tools

Drug information from [Health Canada's DPD](https://health-products.canada.ca/api/drug/).

<!-- CATALOG:drug_database:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `drug_search` | Search Health Canada's Drug Product Database for drug products. | `brand_name`, `din`, `company` |
| `drug_get_details` | Get comprehensive details for a drug product in one call. | `drug_code` |
| `drug_get_ingredients` | Get active ingredients for a Health Canada drug product. | `drug_code` |
| `drug_get_routes` | Get routes of administration for a Health Canada drug product. | `drug_code` |
| `drug_search_companies` | Search for pharmaceutical companies in Health Canada's Drug Product Database. | `company_name` |
| `drug_get_schedule` | Get schedule classification for a Health Canada drug product. | `drug_code` |
| `drug_get_therapeutic_class` | Get ATC therapeutic classification for a Health Canada drug product. | `drug_code` |
| `drug_get_status` | Get market status for a Health Canada drug product. | `drug_code` |
<!-- CATALOG:drug_database:end -->

> **Note:** `drug_code` is the internal database ID (from `drug_search` results), NOT the DIN.

---

### 📊 CKAN Open Data — 7 tools

80,000+ federal datasets from [open.canada.ca](https://open.canada.ca/data/en/api/3/).

<!-- CATALOG:ckan:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ckan_search_datasets` | Search Canada's Open Data portal (open.canada.ca) for datasets by keyword. | `query`, `filters`, `rows`, `start`, `sort` |
| `ckan_get_dataset_details` | Get full details for a specific Canadian Open Data dataset including all resources. | `dataset_id` |
| `ckan_list_organizations` | List all Canadian federal government organizations on the Open Data portal. | `sort` |
| `ckan_search_by_tag` | Search Canadian Open Data portal datasets by tag or keyword label. | `tag`, `rows` |
| `ckan_get_resource` | Get details for a specific data resource (file) from Canada's Open Data portal. | `resource_id` |
| `ckan_list_groups` | List thematic dataset groups available on Canada's Open Data portal. | — |
| `ckan_get_dataset_stats` | Get aggregate statistics for Canada's Open Data portal (open.canada.ca). | — |
<!-- CATALOG:ckan:end -->

---

### 🥗 Canadian Nutrient File — 8 tools

Food nutrition data from [Health Canada's CNF](https://food-nutrition.canada.ca/api/canadian-nutrient-file/).

<!-- CATALOG:nutrient_file:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `nutrient_search_foods` | Search Canadian Nutrient File foods by name using client-side filtering. | `query` |
| `nutrient_get_food_details` | Get detailed information about a specific food item from the Canadian Nutrient File. | `food_id` |
| `nutrient_get_nutrient_amounts` | Get all nutrient amounts per 100g for a specific food from the Canadian Nutrient File. | `food_id` |
| `nutrient_get_serving_sizes` | Get serving size measures and conversion factors for a food item. | `food_id` |
| `nutrient_search_by_food_group` | List all foods within a specific food group from the Canadian Nutrient File. | `food_group_id` |
| `nutrient_list_nutrients` | List all nutrients available in the Canadian Nutrient File database. | — |
| `nutrient_list_food_groups` | List all food group categories in the Canadian Nutrient File database. | — |
| `nutrient_compare_foods` | Compare nutritional content of 2-5 foods from the Canadian Nutrient File. | `food_ids`, `format`, `nutrients` |
<!-- CATALOG:nutrient_file:end -->

---

### 🌤️ MSC GeoMet Weather — 34 tools

Real-time weather, climate, air quality, hydrology, and more from [MSC GeoMet OGC API](https://api.weather.gc.ca/).

<!-- CATALOG:weather:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `wx_get_aqhi` | Get current Air Quality Health Index (AQHI) reading for a location. | `lat`, `lon`, `location_id` |
| `wx_get_aqhi_forecast` | Get AQHI air quality forecast periods for a location. | `lat`, `lon`, `location_id` |
| `wx_get_aqhi_history` | Get historical AQHI observations for a location with optional date range. | `location_id`, `start_date`, `end_date`, `limit` |
| `wx_get_climate_daily` | Get historical daily climate observations for a weather station. | `station_id`, `start_date`, `end_date`, `limit` |
| `wx_get_climate_monthly` | Get monthly climate summary data for a weather station. | `station_id`, `year`, `limit` |
| `wx_get_climate_normals` | Get 30-year climate normals for a weather station. | `station_id` |
| `wx_get_climate_projections` | Get CMIP5 or CMIP6 climate projection collection metadata. | `model`, `scenario`, `variable` |
| `wx_get_drought_index` | Get SPEI drought index collection metadata. | `lat`, `lon`, `spei_period` |
| `wx_compare_climate_periods` | Compare daily climate averages between two time periods for a station. | `station_id`, `period1_start`, `period1_end`, `period2_start`, `period2_end` |
| `wx_get_climate_trends` | Get long-term climate trends from the AHCCD dataset. | `station_id`, `measurement_type` |
| `wx_list_collections` | Browse all available MSC GeoMet weather data collections. | — |
| `wx_get_collection_items` | Query any MSC GeoMet weather collection by ID and return its items. | `collection_id`, `bbox`, `datetime_filter`, `properties`, `limit` |
| `wx_get_current_conditions` | Get current weather conditions for a Canadian location. | `location`, `lat`, `lon`, `province` |
| `wx_get_forecast` | Get the multi-day weather forecast for a Canadian location. | `location`, `lat`, `lon`, `province`, `days` |
| `wx_get_weather_alerts` | Get active weather alerts and warnings for Canada or a specific province. | `province`, `alert_type`, `limit` |
| `wx_search_stations` | Search for Environment Canada climate observation stations. | `province`, `lat`, `lon`, `name` |
| `wx_get_station_data` | Get hourly climate observations from a specific Environment Canada station. | `station_id`, `date`, `limit` |
| `wx_get_water_levels` | Get real-time water level readings at a Canadian hydrometric station. | `station_number`, `lat`, `lon` |
| `wx_get_water_flow` | Get real-time water discharge (flow rate) at a Canadian hydrometric station. | `station_number`, `lat`, `lon` |
| `wx_get_daily_mean_water` | Get daily mean water level and discharge for a hydrometric station. | `station_number`, `start_date`, `end_date` |
| `wx_search_hydro_stations` | Search for hydrometric water monitoring stations by province or location. | `province`, `lat`, `lon`, `name` |
| `wx_get_flood_risk` | Get flood risk assessment for a hydrometric station by comparing current to historical max. | `station_number` |
| `wx_get_marine_forecast` | Get marine weather forecasts for Canadian coastal and offshore waters. | `province`, `lat`, `lon` |
| `wx_get_hurricane_tracks` | Get active hurricane and tropical storm track data for Canada and adjacent waters. | — |
| `wx_get_thunderstorm_outlook` | Get thunderstorm outlook regions and risk levels for Canada. | `province` |
| `wx_get_radar_data` | Get radar precipitation accumulation data for a location in Canada. | `lat`, `lon` |
| `wx_get_lightning` | Get lightning strike information for Canada. | — |
| `wx_get_uv_index` | Get UV index forecast for a location in Canada. | `lat`, `lon`, `location` |
| `wx_get_snow_depth` | Get snow depth from the nearest SWOB real-time weather observation station. | `station_id`, `lat`, `lon` |
| `wx_get_snow_water_equivalent` | Get estimated snow water equivalent (SWE) from snow depth observations. | `station_id`, `lat`, `lon`, `density_factor` |
| `wx_get_weather_summary` | Get a comprehensive weather summary combining current conditions, forecast, active alerts, and air quality. | `lat`, `lon`, `location`, `province` |
| `wx_get_historical_extremes` | Get all-time weather records for a climate station: highest/lowest temperatures, most precipitation, most snowfall. | `station_id` |
| `wx_get_growing_season` | Get growing season dates and frost-free period for a climate station based on 30-year normals. | `station_id` |
| `wx_get_heating_cooling_days` | Get cumulative heating and cooling degree days for energy analysis at a climate station. | `station_id`, `start_date`, `end_date` |
<!-- CATALOG:weather:end -->

---

### 📊 Statistics Canada WDS + SDMX — 15 tools

Time series data, cube metadata, catalog search, and SDMX server-side filtering from the [Statistics Canada Web Data Service](https://www.statcan.gc.ca/en/developers/wds).

> Inspired by [mcp-statcan](https://github.com/aryanjhaveri/mcp-statcan) by Aryan Jhaveri.

<!-- CATALOG:statcan:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `sc_search_cubes` | Search Statistics Canada tables (cubes) by keyword using BM25 ranking. | `query`, `limit` |
| `sc_get_cube_metadata` | Get full metadata and dimension structure for a Statistics Canada table. | `product_id` |
| `sc_get_code_sets` | Get all WDS code sets for decoding numeric codes in StatCan responses. | — |
| `sc_get_series_info_by_vector` | Get series metadata by vectorId (title, frequency, scalar factor, units). | `vector_id` |
| `sc_get_series_info_by_coord` | Get series metadata by productId + coordinate (dot-separated dimension members). | `product_id`, `coordinate` |
| `sc_get_data_by_vector` | Get the latest N observations for a Statistics Canada series by vectorId. | `vector_id`, `n` |
| `sc_get_data_by_coord` | Get the latest N observations for a Statistics Canada series by productId + coordinate. | `product_id`, `coordinate`, `n` |
| `sc_get_data_by_date_range` | Get Statistics Canada observations within a reference period date range. | `vector_id`, `start_date`, `end_date` |
| `sc_get_bulk_vector_data` | Get observations for multiple Statistics Canada series within a release date range. | `vector_ids`, `start_release`, `end_release` |
| `sc_get_changed_series` | Get the list of Statistics Canada series (vectors) that changed today. | — |
| `sc_get_changed_cubes` | Get the list of Statistics Canada tables (cubes) that changed on a specific date. | `date` |
| `sc_get_sdmx_structure` | Get SDMX dimension codelists for a Statistics Canada table. | `product_id` |
| `sc_get_sdmx_data` | Get server-side filtered StatCan observations using SDMX key syntax. | `product_id`, `key`, `last_n`, `start_period`, `end_period`, `dimensions` |
| `sc_get_sdmx_vector_data` | Get observations for a single StatCan vector via SDMX with date range filtering. | `vector_id`, `start_period`, `end_period` |
| `sc_fetch_vectors_to_store` | Fetch multiple StatCan vectors and store them to the shared datastore for SQL queries. | `vector_ids`, `start_release`, `end_release`, `table_name` |
<!-- CATALOG:statcan:end -->

---

### 🗄️ Local Datastore — 6 tools

Local SQLite persistence layer for storing agent-generated data, fetched API results, or any structured data. Tables persist across sessions at `~/.mcp-canada/datastore.db`.

<!-- CATALOG:datastore:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ds_create_table` | Create a named table in the local SQLite datastore. | `table_name`, `columns`, `data` |
| `ds_insert_data` | Insert rows of data into an existing table in the local SQLite datastore. | `table_name`, `rows` |
| `ds_query` | Run a read-only SQL query against the local SQLite datastore. | `sql` |
| `ds_list_tables` | List all tables in the local SQLite datastore. | — |
| `ds_get_schema` | Get the column schema for a table in the local SQLite datastore. | `table_name` |
| `ds_drop_table` | Drop (delete) a table from the local SQLite datastore. | `table_name` |
<!-- CATALOG:datastore:end -->

> **Note:** `ds_query` supports SELECT, PRAGMA, EXPLAIN, and CREATE INDEX only — no mutations via query. Use `ds_insert_data` to write data. Table and column names are validated against an allowlist regex to prevent SQL injection.

---

### 🍁 IRCC Immigration — 10 tools

Permanent residents, temporary workers, study permits, Express Entry, asylum, and refugee data from [IRCC Open Data](https://www.ircc.canada.ca/opendata-donneesouvertes/data/).

<!-- CATALOG:ircc:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ircc_get_permanent_residents` | Get IRCC permanent resident admissions data by breakdown dimension. | `breakdown`, `year` |
| `ircc_get_study_permits` | Get IRCC study permit issuance data by breakdown dimension. | `breakdown`, `year` |
| `ircc_get_work_permits` | Get IRCC work permit data for IMP or TFWP programs. | `permit_type`, `breakdown`, `year` |
| `ircc_get_express_entry` | Get IRCC Express Entry data for admissions or invited candidates. | `stream`, `breakdown`, `year` |
| `ircc_get_tr_to_pr` | Get IRCC data on temporary residents who transitioned to permanent residence. | `breakdown`, `year` |
| `ircc_get_asylum` | Get IRCC asylum claimant data by province and demographic breakdown. | `breakdown`, `year` |
| `ircc_get_ops` | Get IRCC operational processing statistics (monthly snapshots). | `breakdown` |
| `ircc_get_afghan` | Get IRCC data on Afghan refugees admitted to Canada. | `breakdown`, `year` |
| `ircc_get_adhoc_pr` | Get IRCC ad-hoc historical permanent resident data (1980-2023, English-only). | `breakdown` |
| `ircc_list_datasets` | List all available IRCC open data datasets with their breakdown dimensions. | — |
<!-- CATALOG:ircc:end -->

> **Note:** IRCC suppresses values between 0-5 (shown as null) and rounds all other values to the nearest multiple of 5 for privacy protection. Ad-hoc PR files (`ircc_get_adhoc_pr`) are English-only.

---

### 🏛️ Ontario Government Open Data — 6 tools

Provincial datasets from the [Ontario Open Data Catalogue](https://data.ontario.ca) (CKAN 3 API) with 3,000+ datasets from Ontario ministries and agencies. Includes curated population projections from the Ministry of Finance.

<!-- CATALOG:ontario:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ontario_search_datasets` | Search Ontario's Open Data Catalogue (data.ontario.ca) for datasets by keyword. | `query`, `filters`, `rows` |
| `ontario_get_dataset_details` | Get full details for a specific Ontario Open Data dataset including all resources. | `dataset_id` |
| `ontario_get_resource` | Get details for a specific data resource (file) from the Ontario Open Data Catalogue. | `resource_id` |
| `ontario_list_organizations` | List all Ontario government ministries and agencies that publish open data. | `sort` |
| `ontario_get_dataset_stats` | Get aggregate statistics for the Ontario Open Data Catalogue (data.ontario.ca). | — |
| `ontario_get_population_projections` | Fetch Ontario Ministry of Finance population projections by region (2024-2051). | `year`, `recent`, `filter` |
<!-- CATALOG:ontario:end -->

---

### 🏙️ Toronto Open Data — 12 tools

Municipal datasets from the [City of Toronto Open Data Portal](https://open.toronto.ca) (CKAN 2.9 API) with 500+ datasets. Includes TTC transit schedules (GTFS), neighbourhood census profiles, 311 service requests, RentSafeTO apartment evaluations, and short-term rental registrations.

#### Discovery (5)

<!-- CATALOG:toronto_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `toronto_search_datasets` | Search Toronto's Open Data portal (open.toronto.ca) for datasets by keyword. | `query`, `filter_query`, `rows` |
| `toronto_get_dataset_details` | Get full details for a specific Toronto Open Data dataset including all resources. | `dataset_id` |
| `toronto_get_resource` | Get details for a specific data resource (file) from the Toronto Open Data portal. | `resource_id` |
| `toronto_list_organizations` | List all City of Toronto divisions and agencies that publish open data. | — |
| `toronto_get_dataset_stats` | Get aggregate statistics for the Toronto Open Data portal (open.toronto.ca). | — |
<!-- CATALOG:toronto_discovery:end -->

#### Curated (7)

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

---

## Response Format

All tools return a consistent envelope:

```json
{
  "_meta": {
    "source": {"api": "bank-of-canada-valet", "url": "https://..."},
    "cached": true,
    "lang": "en",
    "timestamp": "2026-04-04T12:00:00Z"
  },
  "data": [ ... ]
}
```

Errors return:

```json
{
  "error": {
    "code": "INVALID_SERIES",
    "message": "Series 'FXXYZCAD' not found.",
    "suggestions": ["FXUSDCAD", "FXEURCAD"]
  }
}
```

## Architecture

```
src/mcp_canada/
├── server.py              # FastMCP entry point, transport, module loading
├── shared/                # Cross-module utilities
│   ├── cache.py           # TTL-based in-memory cache (aiocache)
│   ├── envelope.py        # Response/error envelope (make_response/make_error)
│   ├── http.py            # Shared HTTP client with retry (tenacity)
│   ├── rate_limiter.py    # Per-source token bucket
│   └── i18n.py            # Bilingual error messages
├── meta/
│   └── list_modules.py    # list_modules meta-tool
└── modules/
    ├── bank_of_canada/    # 8 tools — Valet API
    ├── open_parliament/   # 10 tools — Parliament API
    ├── recalls/           # 6 tools — Healthy Canadians API
    ├── drug_database/     # 8 tools — Health Canada DPD
    ├── ckan/              # 7 tools — Open Data Portal
    ├── nutrient_file/     # 8 tools — Canadian Nutrient File
    ├── datastore/         # 6 tools — local SQLite persistence
    ├── ircc/              # 10 tools — IRCC Immigration Open Data
    ├── ontario/           # 6 tools — Ontario Open Data Catalogue
    ├── toronto/           # 12 tools — City of Toronto Open Data Portal
    └── weather/           # 34 tools — MSC GeoMet OGC API
        ├── current/       # 5 tools — realtime conditions, forecast, alerts
        ├── climate/       # 7 tools — daily/monthly/normals/trends
        ├── aqhi/          # 3 tools — air quality health index
        ├── hydro/         # 5 tools — water levels, flow, flood risk
        ├── marine/        # 3 tools — marine forecasts, hurricane tracks
        ├── severe/        # 3 tools — radar, lightning, UV index
        ├── snow/          # 2 tools — snow depth, snow water equivalent
        ├── collections/   # 2 tools — collection browser and direct query
        └── summary/       # 4 tools — composite summary, extremes, growing season, degree days
```

Each module follows a **5-file pattern**:

| File | Purpose |
|------|---------|
| `__init__.py` | Module name and description |
| `constants.py` | Base URL, rate limits, cache TTLs, API mappings |
| `schemas.py` | Pydantic v2 response models (always flat) |
| `client.py` | Async HTTP functions with caching and rate limiting |
| `tools.py` | `@tool` decorated MCP tool functions |

New modules are auto-discovered — drop a folder in `modules/` and it registers via FileSystemProvider.

## Development

```bash
# Install dependencies
uv sync

# Run tests (653 unit tests, ~10s)
uv run pytest

# Run integration tests against live APIs (~2min)
uv run pytest tests/integration/ -v -m integration --timeout=120

# Type check and lint
uv run pyright
uv run ruff check src/ tests/

# Coverage (must be ≥95%)
uv run pytest --cov=src/mcp_canada --cov-fail-under=95
```

## Contributing

Each module is self-contained. To add a new API:

1. Create `src/mcp_canada/modules/your_api/` with the 5-file pattern
2. Add colocated `__tests__/` with unit tests
3. Add integration tests in `tests/integration/test_tool_scenarios.py`
4. Update this README's tool catalog

See [CLAUDE.md](CLAUDE.md) for coding conventions.

## License

[MIT](LICENSE) — [Reyem Tech](https://reyem.tech)
