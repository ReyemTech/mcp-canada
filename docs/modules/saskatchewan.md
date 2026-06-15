# Saskatchewan Government Open Data

Provincial datasets from [geohub.saskatchewan.ca](https://geohub.saskatchewan.ca) — the Government of Saskatchewan's ArcGIS Hub portal (org `zcv98lgAl8xQ04cW`, 180+ datasets) combined with the Water Security Agency (WSA) ArcGIS org (`7MBdlVpjqbfBhQer`) for water infrastructure data, and the Saskatchewan Public Safety Agency (SPSA) REST server (`gis.saskatchewan.ca/egis`) for fire ban status.

All tools accept `lang: "en" | "fr"` for bilingual support. Saskatchewan GeoHub metadata is English-primary; FR responses surface English content with French structural messages.

**Important notes:**
- `data.saskatchewan.ca` does NOT exist — Saskatchewan uses ArcGIS Hub, not CKAN
- WSA water data (hydrometric stations, reservoirs) uses a **separate ArcGIS org** (`7MBdlVpjqbfBhQer`) — NOT discoverable via `saskatchewan_search_datasets`
- SPSA fire ban data is on a **separate REST server** (`gis.saskatchewan.ca/egis`) — also not Hub-discoverable
- WSA_Reservoirs FeatureServer: use **layer 26** (not layer 0 — layer 0 returns empty)
- Transport (Highway Hotline 511) is key-gated and deferred; health (SHA) has no public FeatureServer
- Petroleum FeatureServer is accessible (HTTP 200) but deferred per tool-count ceiling

Licence: [GOS Standard Unrestricted Use Data Licence v2.0](https://www.saskatchewan.ca/government/about-the-government-of-saskatchewan/open-government/open-data/open-data-licence).

## Tools — Discovery (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `saskatchewan_search_datasets` | Search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue by keyword. | `query`, `category`, `limit`, `offset` |
| `saskatchewan_get_dataset_details` | Get full metadata for a Saskatchewan GeoHub dataset by ID, including FeatureServer URL. | `dataset_id` |
| `saskatchewan_query_dataset` | Query a Saskatchewan dataset via auto-router: FeatureServer, CSV/GeoJSON/XLSX, or metadata. | `dataset_id`, `where`, `max_records`, `include_geometry` |
| `saskatchewan_list_organizations` | List Saskatchewan government publishing organizations on the geoportal. | -- |
| `saskatchewan_list_categories` | List dataset categories and themes on Saskatchewan's ArcGIS Hub geoportal. | -- |

## Tools — Agriculture + Mining (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `saskatchewan_get_crop_yields` | Get Saskatchewan estimated crop yields (bu/acre) by region for 16 crop types. | `region` |
| `saskatchewan_get_grain_elevators` | Get Saskatchewan grain elevator locations with station, railway, licensee, and capacity. | `railway` |
| `saskatchewan_get_mineral_mines` | Get Saskatchewan mineral mine locations for potash, uranium, helium, or coal. | `mineral` |

## Tools — Environment (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `saskatchewan_get_fire_bans` | Get current Saskatchewan fire ban status by scope from the SPSA Public Fire Ban FeatureServer. | `ban_scope` |
| `saskatchewan_get_historic_wildfires` | Get Saskatchewan historic wildfire boundaries with optional year and cause filters. | `year`, `cause` |
| `saskatchewan_get_air_quality` | Get current hourly ambient air quality readings from Saskatchewan monitoring stations. | `community` |

## Tools — Water / WSA (2)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `saskatchewan_get_wsa_stations` | Get WSA hydrometric gauging station locations with basin, station class, and live graph links. | `basin` |
| `saskatchewan_get_wsa_reservoirs` | Get WSA reservoir locations with reservoir name, dam name, and water level (MASL). | -- |

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `saskatchewan_explore_agriculture` | Guided | Crop yields → grain elevators → mineral mines — agriculture + resource economy workflow |
| `saskatchewan_explore_environment` | Guided | Fire bans → historic wildfires → air quality — environmental situational awareness |
| `saskatchewan_explore_water` | Guided | WSA hydrometric stations → reservoirs — water infrastructure exploration |
| `saskatchewan_quick_dataset_search` | Quick | One-shot geohub.saskatchewan.ca ArcGIS Hub catalogue search |
| `saskatchewan_fire_ban_status_now` | Quick | SPSA fire ban dispatch by scope (urban/rural/provincial/parks); empty=no-bans noted |
| `saskatchewan_crop_yield_lookup` | Quick | Provincial vs 5 regional crop yield lookup; notes PDF reports are not machine-readable |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://saskatchewan/crop-regions` | Catalog | 5 crop reporting regions (SE/SW/Central/NE/NW) with signature crops and bilingual labels |
| `data://saskatchewan/major-basins` | Catalog | 6 major river basins (Qu'Appelle, N/S Saskatchewan, Assiniboine, Churchill, Athabasca) with WSA flags |
| `data://saskatchewan/health-regions` | Catalog | Single SHA (province-wide since 2017 merger); health domain deferred; major facilities |
| `docs://saskatchewan/portal-guide` | Guide | 3-server architecture (GeoHub + WSA + SPSA); deferred transport + health; layer-26 quirk; GOS licence |
| `docs://saskatchewan/agriculture-data-guide` | Guide | Crop yields vs PDF weekly reports; mineral mine dispatch table; grain elevator filter |
| `template://saskatchewan/dataset-report` | Template | Dataset exploration report with `{placeholder}` syntax for agents |
| `template://saskatchewan/wildfire-report` | Template | Fire ban status + historic wildfire + air quality situational report template |

## Architecture Notes

Saskatchewan uses **3 separate ArcGIS services** — the most fragmented portal architecture of any province implemented so far:

1. **Primary Hub** (`services3.arcgis.com/zcv98lgAl8xQ04cW`) — agriculture, mining, environment, air quality, historic wildfires
2. **WSA org** (`services1.arcgis.com/7MBdlVpjqbfBhQer`) — Water Security Agency hydrometric stations and reservoirs
3. **SPSA egis** (`gis.saskatchewan.ca/egis/rest/services/Wildfire`) — Public Safety Agency fire ban FeatureServers

Three module-level rate limiters (`_hub_limiter`, `_wsa_limiter`, `_spsa_limiter`) enforce separate rate groups for each server.

### Key Technical Details

- **WSA_RESERVOIRS_LAYER = 26** (spike-confirmed 2026-06-15; layer 0 returns 0 features)
- **FIRE_BAN_LAYERS**: `{"urban": 0, "rural": 2, "provincial": 3, "parks": 8}` (layers 1/5/6/7/9/10 are display-only)
- **startindex pagination**: fixed in `shared/arcgis_hub.py` (Phase 19, benefits all Hub modules)
- **Empty fire bans** = normal off-season state — NOT an error (same lesson as Manitoba flood alerts)

### Deferred (Out of Scope for Phase 19)

- **Transport**: Highway Hotline 511 — account signup + explicit key request required
- **Health**: Saskatchewan Health Authority — no public ArcGIS FeatureServer
- **Petroleum**: Accessible (HTTP 200 confirmed) but deferred per 13-tool ceiling
- **WSA Water Quality**: 24 stations accessible (layer 19) but deferred per scope
