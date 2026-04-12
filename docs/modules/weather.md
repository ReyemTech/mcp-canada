# :cloud: MSC GeoMet Weather

Real-time weather, climate, air quality, hydrology, and more from [MSC GeoMet OGC API](https://api.weather.gc.ca/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (34)

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
| `wx_list_collections` | Browse all available MSC GeoMet weather data collections. | -- |
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
| `wx_get_hurricane_tracks` | Get active hurricane and tropical storm track data for Canada and adjacent waters. | -- |
| `wx_get_thunderstorm_outlook` | Get thunderstorm outlook regions and risk levels for Canada. | `province` |
| `wx_get_radar_data` | Get radar precipitation accumulation data for a location in Canada. | `lat`, `lon` |
| `wx_get_lightning` | Get lightning strike information for Canada. | -- |
| `wx_get_uv_index` | Get UV index forecast for a location in Canada. | `lat`, `lon`, `location` |
| `wx_get_snow_depth` | Get snow depth from the nearest SWOB real-time weather observation station. | `station_id`, `lat`, `lon` |
| `wx_get_snow_water_equivalent` | Get estimated snow water equivalent (SWE) from snow depth observations. | `station_id`, `lat`, `lon`, `density_factor` |
| `wx_get_weather_summary` | Get a comprehensive weather summary combining current conditions, forecast, active alerts, and air quality. | `lat`, `lon`, `location`, `province` |
| `wx_get_historical_extremes` | Get all-time weather records for a climate station: highest/lowest temperatures, most precipitation, most snowfall. | `station_id` |
| `wx_get_growing_season` | Get growing season dates and frost-free period for a climate station based on 30-year normals. | `station_id` |
| `wx_get_heating_cooling_days` | Get cumulative heating and cooling degree days for energy analysis at a climate station. | `station_id`, `start_date`, `end_date` |
<!-- CATALOG:weather:end -->

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `wx_check_weather` | Guided | Current conditions + forecast + alerts for a location |
| `wx_quick_forecast` | Quick | Get a quick weather forecast |
| `wx_analyze_climate` | Guided | Analyze historical climate data for a station |
| `wx_check_air_quality` | Guided | Get AQHI readings and health recommendations |
| `wx_water_conditions` | Guided | Check water levels and flood risk at a hydrometric station |
| `wx_severe_weather` | Quick | Check for active severe weather alerts |

## Resources (8)

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
