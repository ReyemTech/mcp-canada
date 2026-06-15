# Nova Scotia Government Open Data

Provincial datasets from [data.novascotia.ca](https://data.novascotia.ca) — the Government of Nova Scotia's open data portal, powered by **Socrata SODA** (the fourth portal technology in mcp-canada alongside CKAN, ArcGIS Hub, and OGC WFS).

All tools accept `lang: "en" | "fr"` for bilingual support. Nova Scotia Socrata metadata is English-primary; FR responses surface English content with French structural messages.

**Important notes (Socrata quirks):**
- The `categories=` catalog API parameter is **broken** — it returns `resultSetSize=0` for any category. Use `ns_list_categories` (which uses `q=` + client-side aggregation) to browse categories.
- Geometry columns (`the_geom`) are excluded by default from curated tools via explicit `$select`. Two datasets have geometry: marine leases (`h57h-p9mm`) and protected areas (`ticv-5du5`). Use `ns_query_dataset` with `include_geometry=True` to retrieve boundaries.
- The `date_advisory_removed IS NULL` filter is spike-confirmed for boil water active advisories. An empty advisory list is a **valid success** (off-season state).
- Transport/511 and NS ArcGIS Hub (novagis) are deferred: NS 511 is HTML-only with no machine-readable feed; novagis has no public no-auth FeatureServers.

Licence: [Open Government Licence – Nova Scotia v1.1](https://novascotia.ca/opendata/licence.asp).

## Tools — Discovery (5)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ns_search_datasets` | Search the Government of Nova Scotia open data catalogue on data.novascotia.ca (Socrata). | `query`, `limit`, `offset` |
| `ns_get_dataset_details` | Get schema and metadata for a specific Nova Scotia dataset by its 4x4 dataset ID. | `dataset_id` |
| `ns_query_dataset` | Run a SoQL query against any Nova Scotia Socrata dataset via /resource/{id}.json. | `dataset_id`, `where`, `select`, `order`, `limit`, `offset`, `q`, `group`, `include_geometry` |
| `ns_list_organizations` | List Nova Scotia government organizations and publishers on data.novascotia.ca. | -- |
| `ns_list_categories` | List Nova Scotia data categories from the data.novascotia.ca Socrata catalogue (categories= workaround). | -- |

## Tools — Fishing & Aquaculture (4)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ns_get_marine_aquaculture_leases` | Get Nova Scotia marine aquaculture lease locations with species, owner, waterbody, county, status, and area. | `county`, `species_type`, `limit` |
| `ns_get_landbased_aquaculture_licenses` | Get Nova Scotia landbased aquaculture licenses with species type, owner, county, and operational status. | `county`, `species_type`, `limit` |
| `ns_get_fish_hatchery_stocking` | Get Nova Scotia fish hatchery stocking records with species, hatchery, county, fish size, count released, and stocking date. | `stock`, `county`, `limit` |
| `ns_get_aquaculture_production` | Get Nova Scotia aquaculture production, value, and employment data by county and year. | `year`, `county`, `limit` |

## Tools — Environment, Water & Air Quality (4)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ns_get_water_quality_monitoring` | Get Nova Scotia surface water quality continuous sensor readings (temperature, pH, conductance, dissolved oxygen). | `station_number`, `since`, `limit` |
| `ns_get_boil_water_advisories` | Get Nova Scotia boil water advisories with site name, county, date issued, date removed, facility type, and duration. | `county`, `active_only`, `limit` |
| `ns_get_protected_areas` | Get Nova Scotia protected areas with name, protection type, owner, authority, designation status, and area (geometry excluded). | `status`, `limit` |
| `ns_get_air_quality_stations` | Get Nova Scotia ambient air quality monitoring station locations with measurements and monitoring period. | `city`, `limit` |

## Tools — Health & Demographics (3)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ns_get_health_facilities` | Get Nova Scotia hospital or long-term care facility locations by type, county, health zone, and beds. | `facility_type` ("hospital" or "long_term_care"), `county`, `limit` |
| `ns_get_vital_statistics` | Get Nova Scotia vital statistics (births, deaths, rates, natural increase) by county and year. | `county`, `year`, `limit` |
| `ns_get_chronic_disease_prevalence` | Get Nova Scotia chronic disease crude prevalence by health zone, sex, age group, and year. | `disease` ("ami"/"diabetes"/"copd"/"hypertension"/"asthma"), `health_zone`, `sex`, `year`, `limit` |

## Prompts (6)

| Prompt | Type | Description |
|--------|------|-------------|
| `ns_explore_aquaculture_data` | Guided | Marine leases → landbased licenses → hatchery stocking → production — aquaculture sector analysis |
| `ns_health_zone_analysis` | Guided | Hospitals → LTC facilities → chronic disease → vital stats — health zone analysis workflow |
| `ns_water_quality_analysis` | Guided | Air quality stations → water quality monitoring → boil water advisories — water quality workflow |
| `ns_quick_find_dataset` | Quick | One-shot data.novascotia.ca Socrata catalogue search (categories= workaround documented) |
| `ns_quick_protected_areas` | Quick | Protected areas by designation status; geometry retrieval via ns_query_dataset |
| `ns_quick_vital_stats` | Quick | Vital statistics lookup (UPPERCASE county + year-as-string pitfalls documented) |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://ns/categories` | Catalog | 26 NS Socrata domain categories with bilingual labels; categories= broken-param warning |
| `data://ns/health-zones` | Catalog | 4 NS health zones (Western/Northern/Eastern/Central) with member counties and zone filter values |
| `data://ns/fishing-areas` | Catalog | speciestyp values (Shellfish/Finfish/Marine Plant); hatchery stocks; county case conventions |
| `data://ns/departments` | Catalog | 8 NS government departments publishing on data.novascotia.ca with related tools |
| `docs://ns/socrata-guide` | Guide | Canonical SODA/SoQL how-to: $where/$select/$order/$group/$limit/$offset with NS examples; geometry control; X-App-Token |
| `docs://ns/portal-guide` | Guide | Socrata as 4th portal technology; transport/511 deferred; novagis ArcGIS Hub deferred; air quality per-station pattern |
| `template://ns/aquaculture-report` | Template | Aquaculture sector analysis with `{placeholder}` syntax for lease counts, production, employment |

## Architecture Notes

Nova Scotia uses the **Socrata SODA API** — the fourth portal technology introduced in mcp-canada:

- **Discovery:** `/api/catalog/v1` (NOT `/api/views.json` — views has no pagination metadata)
- **Data queries:** `/resource/{dataset_id}.json` with SoQL parameters (`$where`, `$select`, `$order`, `$limit`, `$offset`, `$group`, `$q`)
- **Shared client:** `shared/socrata.py` — `search_catalog()`, `query_dataset()`, `get_dataset_metadata()`
- **Rate limiting:** 2 req/s (conservative; keyless Socrata throttles ~1 req/s per IP without X-App-Token)
- **Cache TTLs:** 15min (boil water — safety-critical), 1h (search), 24h (facilities/stations), 7d (annual production/vital stats/chronic disease)

### Chronic Disease Zone Normalization

AMI (acute myocardial infarction) dataset uses `health_zone` as the field name; all other disease datasets use `zone`. The `_normalize_zone_field(row, disease)` helper in `client.py` renames `health_zone → zone` for AMI and normalizes `agegroup → age_group` for diabetes/COPD. All tools surface a consistent `zone` key.

### Geometry Exclusion

Two datasets have `the_geom` MultiPolygon columns:
- Marine leases (`h57h-p9mm`): excluded via explicit `$select`; belt-and-suspenders row strip at both client and tool layers
- Protected areas (`ticv-5du5`): same two-layer defense

To retrieve polygon boundaries, use `ns_query_dataset` with the dataset ID and `include_geometry=True`.

### Deferred Domains

- **Transport/511:** NS 511 portal is HTML-only; no machine-readable API or JSON feed
- **NS ArcGIS Hub (novagis):** No public no-auth FeatureServers confirmed
- **Rockweed leases (exhe-htib):** 3 attribute fields (geometry-only dataset); discoverable via `ns_query_dataset`
- **Per-station air quality time series:** 20+ datasets per pollutant per station; routed to `ns_query_dataset` via dataset IDs in the `ns_get_air_quality_stations` catalog
