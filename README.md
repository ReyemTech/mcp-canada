<p align="center">
  <h1 align="center">🍁 mcp-canada</h1>
  <p align="center">
    <strong>MCP server giving AI agents structured access to Canadian federal government data</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/mcp-canada/"><img src="https://img.shields.io/pypi/v/mcp-canada?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml"><img src="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/coverage-96%25-brightgreen" alt="Coverage 96%"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/integration.yml"><img src="https://github.com/ReyemTech/mcp-canada/actions/workflows/integration.yml/badge.svg" alt="Integration Tests"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python 3.12+"></a>
    <a href="https://github.com/reyemtech/mcp-canada/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP Compatible"></a>
    <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/built%20with-FastMCP-orange" alt="Built with FastMCP"></a>
  </p>
</p>

---

**175 tools, ~75 prompts, and ~103 resources** across **9 federal APIs + 2 provincial APIs + 2 municipal APIs + 1 local SQLite datastore** — exchange rates, parliamentary data, product recalls, drug information, 80K+ open datasets, food nutrition data, real-time weather, immigration statistics, Ontario provincial data, Toronto municipal data, York Region ArcGIS Hub data, British Columbia CKAN + WFS geospatial data, and persistent local storage. All bilingual (English/French).

> **First ArcGIS Hub module** — shared infrastructure in `shared/arcgis_hub.py` is reusable for future Canadian municipal modules (BC, Calgary, Edmonton, and other cities publishing via ArcGIS Hub).
> **First OGC WFS module** — BC introduces WFS 2.0 (OGC) support via `shared/ogc.py`, making WFS the third portal technology alongside CKAN and ArcGIS Hub. See `docs://bc/wfs-query-guide` for the CKAN→WFS two-step workflow.


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

### 🏗️ York Region Municipal Open Data — 27 tools

Municipal datasets from **4 verified ArcGIS Hub portals** (York Region regional government, Markham, Newmarket, Aurora). York Region is the first ArcGIS Hub module in mcp-canada — a second portal technology alongside CKAN, covering Canada's 4th-largest regional municipality and its 1.17M residents. 6 of the 10 York Region area municipalities have no public ArcGIS Hub portal and are explicitly out of scope.

**Note:** Each portal gets the same 5 discovery tools with a portal-specific prefix (`york_region_`, `markham_`, `newmarket_`, `aurora_`). York Region regional portal additionally gets 5 curated tools (transit, census, health, roads, waste). Markham gets 2 curated tools (addresses, road network).

#### Discovery Tools — 20 (5 per portal)

<!-- CATALOG:york_region_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `york_region_search_datasets` | Search York Region regional ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `york_region_get_dataset_details` | Get full details for a York Region regional Hub dataset by ID. | `dataset_id` |
| `york_region_query_features` | Query any York Region FeatureServer layer with WHERE clause and field selection. | `service_url`, `layer_id`, `where`, `out_fields`, `max_records` |
| `york_region_list_organizations` | List publisher organizations on the York Region Hub portal. | — |
| `york_region_list_categories` | List dataset category tags on the York Region Hub portal. | — |
| `markham_search_datasets` | Search City of Markham ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `markham_get_dataset_details` | Get full details for a Markham Hub dataset by ID. | `dataset_id` |
| `markham_query_features` | Query any Markham FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `markham_list_organizations` | List publisher organizations on the Markham Hub portal. | — |
| `markham_list_categories` | List dataset category tags on the Markham Hub portal. | — |
| `newmarket_search_datasets` | Search Town of Newmarket ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `newmarket_get_dataset_details` | Get full details for a Newmarket Hub dataset by ID. | `dataset_id` |
| `newmarket_query_features` | Query any Newmarket FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `newmarket_list_organizations` | List publisher organizations on the Newmarket Hub portal. | — |
| `newmarket_list_categories` | List dataset category tags on the Newmarket Hub portal. | — |
| `aurora_search_datasets` | Search Town of Aurora ArcGIS Hub portal by keyword. | `query`, `limit`, `offset` |
| `aurora_get_dataset_details` | Get full details for an Aurora Hub dataset by ID. | `dataset_id` |
| `aurora_query_features` | Query any Aurora FeatureServer layer. | `service_url`, `layer_id`, `where`, `out_fields` |
| `aurora_list_organizations` | List publisher organizations on the Aurora Hub portal. | — |
| `aurora_list_categories` | List dataset category tags on the Aurora Hub portal. | — |
<!-- CATALOG:york_region_discovery:end -->

#### York Region Curated — 5

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

#### Markham Curated — 2

<!-- CATALOG:markham_curated:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `markham_get_addresses` | Search Markham civic address registry with optional street name filter. | `street`, `include_geometry`, `max_records` |
| `markham_get_road_network` | Query Markham SLRN (Street Location Reference Network) road network by road name. | `name`, `include_geometry`, `max_records` |
<!-- CATALOG:markham_curated:end -->

---

### 🌲 British Columbia Open Data — 20 tools

Provincial datasets from the [BC Data Catalogue](https://catalogue.data.gov.bc.ca) (CKAN 2.9 API) and the [BC Geographic Warehouse](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/bc-spatial-data-infrastructure/bc-geographic-warehouse) WFS 2.0 endpoint. 13,000+ datasets including active wildfires, fire perimeters, protected areas, mining tenure, water wells, and highway infrastructure.

#### Discovery (5)

<!-- CATALOG:bc_discovery:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `bc_search_datasets` | Search BC Data Catalogue for datasets by keyword, organization, or filter query. | `q`, `rows`, `start`, `fq` |
| `bc_get_dataset_details` | Get full metadata for a BC Data Catalogue dataset including WFS queryability. | `package_id` |
| `bc_query_features` | Query any BCGW WFS layer by object_name with optional CQL filter. | `object_name`, `cql`, `max_records`, `include_geometry` |
| `bc_list_organizations` | List all BC Data Catalogue organizations (ministries and agencies). | — |
| `bc_list_categories` | List available BC Data Catalogue tags for subject-area discovery. | — |
<!-- CATALOG:bc_discovery:end -->

#### Curated WFS (15)

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

---

## Prompt Catalog

~75 workflow prompts across 14 modules. Prompts appear as slash-commands in Claude Desktop and other MCP-compatible clients. Discoverable via `client.list_prompts()`.

All prompts accept `lang: "en" | "fr"`. **Guided workflows** return `list[Message]` (user + assistant roles for multi-step chaining). **Quick lookups** return a single user message with tool invocation instructions.

### 🏦 Bank of Canada (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `boc_analyze_rates` | Guided | Exchange rate analysis workflow — chains `boc_search_series` → `boc_get_exchange_rates` |
| `boc_get_policy_rate` | Quick | Get current BoC overnight policy rate |
| `boc_compare_currencies` | Guided | Compare two currencies over a date range |
| `boc_explore_commodities` | Guided | Explore BCPI commodity prices — chains `boc_list_groups` → `boc_get_commodity_prices` |
| `boc_check_inflation` | Quick | Get CPI inflation data |

### 📊 Statistics Canada (6 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `statcan_find_data` | Guided | Search for StatCan cubes and get vector data |
| `statcan_quick_vector` | Quick | Get the latest N observations for a known vectorId |
| `statcan_explore_sdmx` | Guided | Explore and filter StatCan data using SDMX key syntax |
| `statcan_store_and_query` | Guided | Cross-module flagship: fetch vectors → store → SQL JOIN |
| `statcan_monitor_changes` | Quick | Check which StatCan series changed today |
| `statcan_compare_series` | Guided | Compare multiple StatCan time series |

### 🗄️ Local Datastore (4 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `ds_create_and_query` | Guided | Create a table, insert data, and run SQL queries |
| `ds_quick_query` | Quick | Run a SQL query against an existing datastore table |
| `ds_explore_tables` | Quick | List tables and inspect schemas |
| `ds_cross_module_join` | Guided | Fetch data from two APIs and JOIN in SQL |

### 📊 CKAN Open Data (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `ckan_explore_federal_data` | Guided | Discover and download federal datasets from open.canada.ca |
| `ckan_quick_search` | Quick | Search for federal datasets by keyword |
| `ckan_browse_organizations` | Quick | Browse datasets by government organization |
| `ckan_browse_by_tag` | Quick | Browse datasets by topic tag |
| `ckan_portal_overview` | Quick | Get portal statistics and popular tags |

### 🏛️ Open Parliament (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `parl_research_bill` | Guided | Research a federal bill — search → details → sponsor → votes |
| `parl_find_mp` | Quick | Look up an MP's profile and riding |
| `parl_track_voting` | Guided | Track how an MP votes on bills |
| `parl_search_debates` | Quick | Search Hansard debate transcripts |
| `parl_party_breakdown` | Guided | Get all MPs from a political party |

### ⚠️ Recalls (4 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `recalls_investigate_alert` | Guided | Investigate a recall — search → details → related alerts |
| `recalls_quick_search` | Quick | Search for recalls by keyword |
| `recalls_check_food_safety` | Quick | Check for food product recalls |
| `recalls_vehicle_safety` | Quick | Check for vehicle recalls |

### 💊 Drug Database (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `drug_research_medication` | Guided | Research a drug — search → ingredients → schedule → status |
| `drug_quick_search` | Quick | Search drugs by brand name or DIN |
| `drug_check_company` | Quick | Look up a pharmaceutical company's products |
| `drug_compare_generics` | Guided | Compare a brand drug to its generic equivalents |
| `drug_check_status` | Quick | Get market status for a drug product |

### 🥗 Canadian Nutrient File (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `nutrient_analyze_food` | Guided | Full nutrition analysis — search → amounts → serving sizes |
| `nutrient_quick_search` | Quick | Search for foods in the Canadian Nutrient File |
| `nutrient_compare_foods` | Guided | Compare nutritional content across multiple foods |
| `nutrient_browse_food_groups` | Quick | List all foods in a food group category |
| `nutrient_check_daily_values` | Quick | Look up daily value nutrient thresholds |

### 🌤️ MSC GeoMet Weather (6 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `wx_check_weather` | Guided | Current conditions + forecast + alerts for a location |
| `wx_quick_forecast` | Quick | Get a quick weather forecast |
| `wx_analyze_climate` | Guided | Analyze historical climate data for a station |
| `wx_check_air_quality` | Guided | Get AQHI readings and health recommendations |
| `wx_water_conditions` | Guided | Check water levels and flood risk at a hydrometric station |
| `wx_severe_weather` | Quick | Check for active severe weather alerts |

### 🍁 IRCC Immigration (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `ircc_explore_immigration` | Guided | Explore IRCC immigration data — choose dataset → breakdown → year |
| `ircc_quick_pr` | Quick | Get permanent resident admissions data |
| `ircc_track_express_entry` | Guided | Track Express Entry admissions and invite rounds |
| `ircc_compare_pathways` | Guided | Compare immigration pathways (PR vs study vs work) |
| `ircc_analyze_trends` | Guided | Analyze multi-year immigration trends |

### 🏛️ Ontario Open Data (4 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `ontario_explore_data` | Guided | Discover and download Ontario provincial datasets |
| `ontario_quick_search` | Quick | Search for Ontario datasets by keyword |
| `ontario_browse_ministries` | Quick | Browse datasets by Ontario ministry |
| `ontario_population_data` | Guided | Get Ontario population projections by region |

### 🏙️ Toronto Open Data (6 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `toronto_explore_city_data` | Guided | Discover and download Toronto municipal datasets |
| `toronto_quick_search` | Quick | Search for Toronto datasets by keyword |
| `toronto_explore_neighbourhood` | Guided | Explore census and service data for a neighbourhood |
| `toronto_ttc_transit` | Guided | Look up TTC stops and routes from GTFS data |
| `toronto_check_311` | Guided | Analyze 311 service requests by year/ward/type |
| `toronto_rental_analysis` | Guided | Analyze rental data — RentSafeTO + short-term rentals |

### 🏗️ York Region Municipal Open Data (5 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `york_region_explore_transit` | Guided | YRT/Viva transit analysis — chains `york_region_get_transit_stops` → `york_region_get_transit_routes` |
| `york_region_explore_census` | Guided | Compare 2021 Census demographics across York Region municipalities |
| `york_region_explore_health` | Guided | Explore public health data — beach water, hospitals, drinking water |
| `york_region_quick_dataset_search` | Quick | One-shot search across York Region and municipality portals |
| `markham_explore_infrastructure` | Guided | Explore Markham civic addresses and SLRN road network |

### 🌲 British Columbia Open Data (6 prompts)

| Prompt | Type | Description |
|--------|------|-------------|
| `bc_explore_wildfires` | Guided | Multi-step wildfire analysis — chains `bc_get_active_fires` → `bc_get_fire_perimeters` → `bc_get_wildfire_weather_stations` |
| `bc_explore_forestry` | Guided | Forestry land use analysis — chains `bc_get_forest_tenure` → `bc_get_cut_blocks` → `bc_get_protected_areas` |
| `bc_explore_environment` | Guided | Environmental pressure analysis — chains `bc_get_water_wells` → `bc_get_local_parks` → `bc_get_mining_tenure` |
| `bc_quick_dataset_search` | Quick | Two-step BC dataset discovery: CKAN search → WFS queryability check |
| `bc_check_water_quality` | Quick | Retrieve BC groundwater well records by city, well class, or aquifer ID |
| `bc_wildfire_status_now` | Quick | Get current active wildfire status filtered by urgency or fire centre |

---

## Resource Catalog

~103 reference resources across 14 modules. Resources provide instant context without tool calls — agents can read them without consuming API rate limits. Discoverable via `client.list_resources()`.

**URI scheme conventions:**
- `data://` — JSON catalogs (machine-parseable key→value mappings)
- `docs://` — Markdown documentation guides (human-readable explanations)
- `template://` — Markdown response templates with `{placeholder}` syntax

### 🏦 Bank of Canada (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://boc/currency-codes` | Catalog | 17 FX currency codes with bilingual labels |
| `data://boc/interest-rate-types` | Catalog | Rate types mapped to Valet series codes |
| `data://boc/commodity-types` | Catalog | BCPI commodity categories with bilingual descriptions |
| `data://boc/inflation-indicators` | Catalog | CPI measures with series codes and bilingual descriptions |
| `docs://boc/series-naming` | Guide | FX/rate/CPI/BCPI series naming conventions |
| `docs://boc/api-quirks` | Guide | Date formats, null values, cache TTLs, common 404 causes |
| `template://boc/rate-report` | Template | Exchange rate report with `{currency}`, `{start_date}`, `{latest_value}` |

### 📊 Statistics Canada (8 resources)

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

### 🗄️ Local Datastore (6 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://datastore/column-types` | Catalog | Supported SQLite column types with examples |
| `data://datastore/identifier-rules` | Catalog | Identifier regex pattern and allowed characters |
| `docs://datastore/sql-guide` | Guide | Supported SQL statements, query examples, safety rules |
| `docs://datastore/cross-module-patterns` | Guide | Fetch-store-JOIN workflow for cross-API analytics |
| `template://datastore/query-report` | Template | SQL query result report template |
| `template://datastore/schema-report` | Template | Table schema description template |

### 📊 CKAN Open Data (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://ckan/federal-organizations` | Catalog | Federal org slugs for use in `organization=` search filter |
| `data://ckan/popular-tags` | Catalog | Most-used dataset tags on open.canada.ca |
| `data://ckan/resource-formats` | Catalog | Available resource file formats (CSV, XLSX, GeoJSON, etc.) |
| `docs://ckan/search-tips` | Guide | Advanced CKAN search syntax and filter examples |
| `docs://ckan/api-quirks` | Guide | Pagination, bilingual fields, resource vs dataset distinction |
| `template://ckan/dataset-summary` | Template | Dataset summary with `{title}`, `{organization}`, `{resources}` |
| `template://ckan/resource-report` | Template | Resource download report template |

### 🏛️ Open Parliament (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://parliament/party-codes` | Catalog | Political party codes and bilingual names |
| `data://parliament/session-format` | Catalog | Session ID format and recent sessions |
| `data://parliament/bill-types` | Catalog | Bill type codes (C-, S-, M-) with descriptions |
| `docs://parliament/voting-guide` | Guide | How divisions work, yea/nay/paired, how to look up ballots |
| `docs://parliament/hansard-guide` | Guide | Hansard transcript structure and full-text search tips |
| `docs://parliament/api-quirks` | Guide | Pagination, URL slug format, URL-based IDs |
| `template://parliament/mp-profile` | Template | MP profile with `{name}`, `{party}`, `{riding}`, `{votes}` |

### ⚠️ Recalls (6 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://recalls/categories` | Catalog | Recall category codes (food, vehicle, health-product, etc.) |
| `data://recalls/severity-levels` | Catalog | Recall risk severity levels |
| `docs://recalls/search-tips` | Guide | Search strategies, category filtering, pagination |
| `docs://recalls/food-safety-guide` | Guide | How to interpret food recall risk levels and actions |
| `template://recalls/safety-alert` | Template | Safety alert summary with `{product}`, `{hazard}`, `{action}` |
| `template://recalls/recall-report` | Template | Full recall report template |

### 💊 Drug Database (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://drug/schedule-codes` | Catalog | Health Canada schedule classification (Prescription/OTC/Schedule I-III) |
| `data://drug/route-codes` | Catalog | Routes of administration with bilingual labels |
| `data://drug/status-codes` | Catalog | Market status codes (marketed, discontinued, etc.) |
| `data://drug/therapeutic-classes` | Catalog | ATC therapeutic class codes and descriptions |
| `docs://drug/din-guide` | Guide | DIN vs drug_code distinction, how to find a drug_code |
| `docs://drug/search-tips` | Guide | Brand vs generic search, company name matching |
| `template://drug/medication-report` | Template | Drug profile with `{drug_code}`, `{brand_name}`, `{schedule}`, `{ingredients}` |

### 🥗 Canadian Nutrient File (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://nutrient/food-groups` | Catalog | CNF food group IDs (1-25) with bilingual names |
| `data://nutrient/common-nutrients` | Catalog | Key nutrient IDs for common dietary analysis |
| `data://nutrient/serving-size-measures` | Catalog | Common measure units used in CNF serving sizes |
| `docs://nutrient/cnf-guide` | Guide | CNF data structure, food_id vs food_code, API overview |
| `docs://nutrient/interpretation-guide` | Guide | How to interpret per-100g nutrient values and daily values |
| `template://nutrient/food-profile` | Template | Food nutrition profile with `{food_name}`, `{nutrients}`, `{serving_size}` |
| `template://nutrient/comparison-report` | Template | Multi-food comparison report template |

### 🌤️ MSC GeoMet Weather (8 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://weather/province-codes` | Catalog | Two-letter province/territory codes for station search |
| `data://weather/common-stations` | Catalog | Well-known climate station IDs across provinces |
| `data://weather/aqhi-scale` | Catalog | AQHI risk categories 1-10+ with health messages |
| `data://weather/climate-normals-periods` | Catalog | Available 30-year climate normal periods |
| `docs://weather/station-guide` | Guide | How to find station IDs, station types, coverage |
| `docs://weather/climate-data-guide` | Guide | Daily vs monthly vs normals vs AHCCD distinctions |
| `docs://weather/ogc-api-guide` | Guide | OGC API collections structure, bbox/datetime filtering |
| `template://weather/forecast-report` | Template | Weather forecast report with `{location}`, `{conditions}`, `{forecast}` |

### 🍁 IRCC Immigration (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://ircc/immigration-categories` | Catalog | Immigration category codes and bilingual names |
| `data://ircc/dataset-list` | Catalog | All 10 IRCC datasets mapped to tool names and breakdowns |
| `data://ircc/express-entry-streams` | Catalog | Express Entry stream codes and descriptions |
| `data://ircc/work-permit-types` | Catalog | IMP vs TFWP work permit program codes |
| `docs://ircc/data-guide` | Guide | IRCC open data structure, XLSX format, suppression rules |
| `docs://ircc/xlsx-quirks` | Guide | Multi-sheet XLSX parsing, suppressed values, year totals |
| `template://ircc/immigration-report` | Template | Immigration data report with `{dataset}`, `{breakdown}`, `{year}`, `{data}` |

### 🏛️ Ontario Open Data (6 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://ontario/ministries` | Catalog | Ontario ministries and agencies with CKAN org slugs |
| `data://ontario/popular-datasets` | Catalog | Frequently accessed Ontario datasets |
| `data://ontario/resource-formats` | Catalog | Available file formats on data.ontario.ca |
| `docs://ontario/ckan-guide` | Guide | Ontario CKAN API structure, filtering, pagination |
| `docs://ontario/population-projections-guide` | Guide | Population projections XLSX structure, regions, years |
| `template://ontario/dataset-report` | Template | Ontario dataset report with `{title}`, `{organization}`, `{resources}` |

### 🏙️ Toronto Open Data (8 resources)

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

### 🏗️ York Region Municipal Open Data (8 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://york_region/portals` | Catalog | All 10 York Region municipalities with portal status (4 verified, 6 no portal) |
| `data://york_region/municipalities` | Catalog | All 9 local municipalities + region with 2021 Census population and area |
| `data://york_region/feature_services` | Catalog | York Region curated FeatureServer catalog with tool names and layer IDs |
| `docs://york_region/esri-field-naming` | Guide | ESRI field naming conventions (OBJECTID, ALL_CAPS, Shape__Length) |
| `docs://york_region/portal-landscape` | Guide | Which 4 of 10 municipalities have ArcGIS Hub portals and why others don't |
| `docs://york_region/census-variables` | Guide | 2021 Census focused field set (10 columns), CSDNAME filter, full 364-field access |
| `docs://york_region/arcgis-query-patterns` | Guide | ArcGIS SQL WHERE clause syntax — LIKE, case sensitivity, quoting, 1=1 pattern |
| `template://york_region/transit-query-response` | Template | YRT/Viva transit results with `{stop_name}`, `{route_short_name}`, `{wheelchair_boarding}` |

### 🌲 British Columbia Open Data (7 resources)

| URI | Type | Description |
|-----|------|-------------|
| `data://bc/ministries` | Catalog | BC ministry and agency CKAN org slugs with bilingual names and descriptions |
| `data://bc/wildfire-status-codes` | Catalog | FIRE_STATUS codes (Active, Out of Control, Being Held, etc.) + FIRE_CAUSE codes with bilingual labels |
| `data://bc/object-name-prefixes` | Catalog | All 10 WHSE schema prefixes + 15 curated mcp-canada layer `object_name` mappings |
| `docs://bc/wfs-query-guide` | Guide | CKAN→WFS two-step workflow, CQL syntax primer, pagination notes (bilingual) |
| `docs://bc/bcdc-api-quirks` | Guide | BCDC custom fields (bcdc_type, object_name), queryable_via_wfs derivation, no-groups quirk |
| `template://bc/wildfire-report` | Template | Wildfire season report with `{fire_season}`, `{total_active_fires}`, `{largest_fire}`, centre breakdown |
| `template://bc/dataset-report` | Template | Dataset exploration report with `{object_name}`, `{queryable_via_wfs}`, `{sample_data}` |

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
    ├── york_region/       # 27 tools — York Region ArcGIS Hub (4 portals: york_region, markham, newmarket, aurora)
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

Each module follows a **7-file pattern**:

| File | Purpose |
|------|---------|
| `__init__.py` | Module name and description |
| `constants.py` | Base URL, rate limits, cache TTLs, API mappings |
| `schemas.py` | Pydantic v2 response models (always flat) |
| `client.py` | Async HTTP functions with caching and rate limiting |
| `tools.py` | `@tool` decorated MCP tool functions |
| `prompts.py` | `@prompt` functions — guided workflows + quick lookups |
| `resources.py` | `@resource` functions — catalogs, docs, templates |

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

1. Create `src/mcp_canada/modules/your_api/` with the 7-file pattern
2. Add colocated `__tests__/` with unit tests
3. Add integration tests in `tests/integration/test_tool_scenarios.py`
4. Update this README's tool, prompt, and resource catalogs

See [CLAUDE.md](CLAUDE.md) for coding conventions.

## License

[MIT](LICENSE) — [Reyem Tech](https://reyem.tech)
