# Manitoba Open Data

Provincial datasets from [geoportal.gov.mb.ca](https://geoportal.gov.mb.ca) — the Government of Manitoba's ArcGIS Hub portal (org `mMUesHYPkXjaFGfS`, 90+ datasets) combined with the Manitoba 511 v3 JSON API for transport data.

All tools accept `lang: "en" | "fr"` for bilingual support. Manitoba Hub metadata is English-primary; FR responses surface English content with French structural messages.

**Important notes:**
- `data.manitoba.ca` is unreachable (HTTP 404/connection reset) — do NOT use it
- `mli.gov.mb.ca` (Manitoba Land Initiative) was retired 2022-02-09
- Manitoba 511 requires `MANITOBA_511_KEY` environment variable (free key via [https://www.manitoba511.ca/my511/register](https://www.manitoba511.ca/my511/register))
- ArcGIS Hub Search API is at `/api/search/v1/collections/all/items` (NOT `/api/v2/datasets` which 404s)

Licence: [Open Manitoba Licence](https://www.gov.mb.ca/maps/open_data/index.html) (use, modify, share with attribution).

## Tools — Discovery (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `manitoba_search_datasets` | Search Manitoba's geoportal ArcGIS Hub by keyword, category, or owner. | `query`, `category`, `num`, `start` |
| `manitoba_get_dataset_details` | Get full metadata for a Hub dataset by its item ID — returns `feature_server_url`, download URLs, tags, categories. | `dataset_id` |
| `manitoba_query_dataset` | Auto-routes by URL type: FeatureServer → ArcGIS query; CSV/JSON/GeoJSON/XLSX → parse; other → metadata-only. | `dataset_url`, `where`, `max_records`, `include_geometry` |
| `manitoba_list_organizations` | List Manitoba government departments publishing on geoportal.gov.mb.ca (derived from Hub search). | -- |
| `manitoba_list_categories` | List dataset category paths on the Hub (e.g., `/Categories/Environment`, `/Categories/Agriculture`). | -- |

## Tools — Flood / Hydrology (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `manitoba_get_flood_alerts` | Current overland flood watch/warning polygons from Manitoba Infrastructure's Hub layer. Empty list = normal off-season. | `include_geometry` |
| `manitoba_get_river_stations` | Manitoba river/hydrometric station locations and current flood status (No Flooding/High Water/Watch/Warning) from live CSV. | `alert_only` |
| `manitoba_get_provincial_waterways` | Manitoba water control infrastructure — dikes, floodways, dams, diversions, reservoirs (Provincial_Waterways layer). | `f_type`, `max_records`, `include_geometry` |

## Tools — Agriculture / Drought (4)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `manitoba_get_drought_status` | Current drought intensity (D0–D4) for Manitoba from the continental Canada/USA Drought Monitor FeatureServer (filtered to MB bbox). | `filter_province` |
| `manitoba_get_ag_weather_stations` | Manitoba Agriculture weather station locations with links to live hourly data at agrimaps.gov.mb.ca. | `ag_region` |
| `manitoba_get_livestock_prices` | Weekly Manitoba cattle auction prices (MB_Cattle_Prices_Current_year). livestock='hog' supported provisionally (unresolved FS URL). | `livestock` |
| `manitoba_get_crop_regions` | Manitoba Agriculture 5 crop reporting region boundaries with bilingual names (REGION/RÉGION). | -- |

## Tools — Environment / Parks / Health (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `manitoba_get_provincial_parks` | 93 Manitoba provincial parks with bilingual names (NAME_E/NOM_F), type (TYPE_E/TYPE_F), biome, area, and status. | `park_type` |
| `manitoba_get_fisheries_data` | 350+ Manitoba waterbody records with fishing regulations, species lists, Secchi depth, boat launch availability. | `name`, `region` |
| `manitoba_get_provincial_forests` | Manitoba provincial forest management unit boundaries from Manitoba_Provincial_Forests_Version_6. | -- |
| `manitoba_get_surgical_wait_times` | Annual average wait times (days) by diagnostic/surgical procedure from Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages. NOTE: Annual averages, NOT live ER waits. | `procedure`, `year` |
| `manitoba_get_health_facilities` | Rural health care facilities with emergency department, acute care, and PCH flags (Rural_Health_Care_Facilities_in_Manitoba, spike-resolved). | `rha` |

## Tools — Transport / 511 Manitoba (3)

Requires `MANITOBA_511_KEY` environment variable. Returns `NOT_CONFIGURED` error with registration instructions if absent.

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `manitoba_get_road_events` | Current road closures, construction, and incidents from Manitoba 511 v3 Events endpoint. | -- |
| `manitoba_get_winter_road_conditions` | Seasonal winter road conditions on Manitoba's remote ice road network (Northern communities). Returns empty list outside season — normal. | `area_name` |
| `manitoba_get_traffic_cameras` | Manitoba highway traffic camera locations + snapshot image URLs (Views array per camera, locations cached 24h). | -- |

## Prompts (6)

**Guided workflows (list[Message]):**

| Prompt | Tools Chained | Purpose |
|--------|--------------|---------|
| `manitoba_explore_flood_or_water` | `manitoba_get_flood_alerts` → `manitoba_get_river_stations` → `manitoba_get_provincial_waterways` | Flood situational awareness with Watch/Warning context and HFC PDF caveat |
| `manitoba_explore_transport` | `manitoba_get_road_events` → `manitoba_get_winter_road_conditions` → `manitoba_get_traffic_cameras` | 511 road network; documents NOT_CONFIGURED for missing API key |
| `manitoba_explore_agriculture_or_health` | `manitoba_get_drought_status` / `manitoba_get_livestock_prices` OR `manitoba_get_surgical_wait_times` / `manitoba_get_health_facilities` | Branched agriculture OR health workflow |

**Quick lookups (str):**

| Prompt | Tool Referenced | Key Guidance |
|--------|----------------|-------------|
| `manitoba_quick_dataset_search` | `manitoba_search_datasets` | ArcGIS Hub API; links to data://manitoba/departments |
| `manitoba_check_road_conditions` | `manitoba_get_winter_road_conditions` | NOT_CONFIGURED key guidance; area_name filter |
| `manitoba_flood_outlook_now` | `manitoba_get_flood_alerts` | Watch/Warning/Advisory type table; HYDAT redirect for levels |

## Resources (7)

| URI | Scheme | Content |
|-----|--------|---------|
| `data://manitoba/departments` | data | 6 provincial ministries with name_en/name_fr and data domains |
| `data://manitoba/health-regions` | data | 5 RHAs (WRHA/PMH/IERHA/SHSS/NHR) with coverage and major hospitals |
| `data://manitoba/major-rivers` | data | 6 entries: Red/Assiniboine/Winnipeg/Souris rivers + Red River Floodway + Lake Manitoba |
| `docs://manitoba/flood-data-guide` | docs | ArcGIS Hub layers vs HFC PDFs; HYDAT note; alert type table; flood season context |
| `docs://manitoba/portal-guide` | docs | geoportal.gov.mb.ca structure; MLI retirement warning; OpenMB licence |
| `template://manitoba/dataset-report` | template | Dataset analysis report template with {search_query}, {dataset_title}, {sample_data_table} |
| `template://manitoba/flood-report` | template | Flood situational report template with {report_date}, {alert_count}, river status table |
