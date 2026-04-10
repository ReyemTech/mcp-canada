"""MCP resources for the York Region Municipal Open Data module.

Provides reference catalogs, documentation guides, and response templates for
the York Region ArcGIS Hub portals (york_region, markham, newmarket, aurora).
All resources use type-prefixed URIs:
- data://york_region/...    — JSON reference catalogs (machine-parseable)
- docs://york_region/...    — Markdown documentation guides (human-readable)
- template://york_region/...— Markdown response templates with {placeholder} syntax

IMPORTANT: All resource functions are zero-parameter. Adding any parameter
(even lang) would make FastMCP treat them as ResourceTemplate instead of
FunctionResource, removing them from resources/list.
Bilingual content is embedded inline in a single resource.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://york_region/portals",
    mime_type="application/json",
    name="york_region_portals",
    title="York Region ArcGIS Hub Portal Catalog (10 municipalities)",
)
def york_region_portals() -> str:
    """JSON catalog of all 10 York Region area municipalities with portal status.

    4 municipalities have verified ArcGIS Hub portals (status: 'verified').
    6 municipalities have no public portal (status: 'no_public_portal').
    Use portal_url with york_region_search_datasets and related discovery tools.
    """
    return json.dumps(
        [
            {
                "key": "york_region",
                "name_en": "York Region (Regional Government)",
                "name_fr": "Région de York (gouvernement régional)",
                "portal_url": "https://insights-york.opendata.arcgis.com",
                "item_count_approx": 442,
                "status": "verified",
                "tool_prefix": "york_region",
            },
            {
                "key": "markham",
                "name_en": "City of Markham",
                "name_fr": "Ville de Markham",
                "portal_url": "https://data-markham.opendata.arcgis.com",
                "item_count_approx": 65,
                "status": "verified",
                "tool_prefix": "markham",
            },
            {
                "key": "newmarket",
                "name_en": "Town of Newmarket",
                "name_fr": "Ville de Newmarket",
                "portal_url": "https://data-newmarket.opendata.arcgis.com",
                "item_count_approx": 61,
                "status": "verified",
                "tool_prefix": "newmarket",
            },
            {
                "key": "aurora",
                "name_en": "Town of Aurora",
                "name_fr": "Ville d'Aurora",
                "portal_url": "https://opendata-cityofaurora.hub.arcgis.com",
                "item_count_approx": 21,
                "status": "verified",
                "tool_prefix": "aurora",
            },
            {
                "key": "vaughan",
                "name_en": "City of Vaughan",
                "name_fr": "Ville de Vaughan",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "No public ArcGIS Hub portal as of 2026-04.",
                "note_fr": "Aucun portail ArcGIS Hub public en date de 2026-04.",
            },
            {
                "key": "richmond_hill",
                "name_en": "Town of Richmond Hill",
                "name_fr": "Ville de Richmond Hill",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "No public ArcGIS Hub portal as of 2026-04.",
                "note_fr": "Aucun portail ArcGIS Hub public en date de 2026-04.",
            },
            {
                "key": "king",
                "name_en": "Township of King",
                "name_fr": "Canton de King",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "No public ArcGIS Hub portal as of 2026-04.",
                "note_fr": "Aucun portail ArcGIS Hub public en date de 2026-04.",
            },
            {
                "key": "east_gwillimbury",
                "name_en": "Town of East Gwillimbury",
                "name_fr": "Ville d'East Gwillimbury",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "No public ArcGIS Hub portal as of 2026-04.",
                "note_fr": "Aucun portail ArcGIS Hub public en date de 2026-04.",
            },
            {
                "key": "whitchurch_stouffville",
                "name_en": "Town of Whitchurch-Stouffville",
                "name_fr": "Ville de Whitchurch-Stouffville",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "Census data only via york_region portal; no standalone public portal.",
                "note_fr": "Données du recensement uniquement via le portail york_region; aucun portail public autonome.",
            },
            {
                "key": "georgina",
                "name_en": "Town of Georgina",
                "name_fr": "Ville de Georgina",
                "portal_url": None,
                "item_count_approx": None,
                "status": "no_public_portal",
                "tool_prefix": None,
                "note_en": "No public ArcGIS Hub portal as of 2026-04.",
                "note_fr": "Aucun portail ArcGIS Hub public en date de 2026-04.",
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://york_region/municipalities",
    mime_type="application/json",
    name="york_region_municipalities",
    title="York Region Municipalities with Population and Area (2021 Census)",
)
def york_region_municipalities() -> str:
    """JSON list of all 9 local municipalities + York Region with 2021 Census population and area.

    Use has_portal to determine which municipalities have mcp-canada ArcGIS Hub tools.
    Population and area figures are approximate from the 2021 Census.
    """
    return json.dumps(
        [
            {
                "key": "york_region",
                "name_en": "York Region (Regional)",
                "name_fr": "Région de York (régionale)",
                "population_2021": 1173334,
                "area_km2": 1756,
                "has_portal": True,
                "municipality_type": "regional",
            },
            {
                "key": "markham",
                "name_en": "City of Markham",
                "name_fr": "Ville de Markham",
                "population_2021": 338503,
                "area_km2": 212,
                "has_portal": True,
                "municipality_type": "city",
            },
            {
                "key": "vaughan",
                "name_en": "City of Vaughan",
                "name_fr": "Ville de Vaughan",
                "population_2021": 323103,
                "area_km2": 273,
                "has_portal": False,
                "municipality_type": "city",
            },
            {
                "key": "richmond_hill",
                "name_en": "Town of Richmond Hill",
                "name_fr": "Ville de Richmond Hill",
                "population_2021": 202022,
                "area_km2": 101,
                "has_portal": False,
                "municipality_type": "town",
            },
            {
                "key": "newmarket",
                "name_en": "Town of Newmarket",
                "name_fr": "Ville de Newmarket",
                "population_2021": 90474,
                "area_km2": 38,
                "has_portal": True,
                "municipality_type": "town",
            },
            {
                "key": "aurora",
                "name_en": "Town of Aurora",
                "name_fr": "Ville d'Aurora",
                "population_2021": 67179,
                "area_km2": 50,
                "has_portal": True,
                "municipality_type": "town",
            },
            {
                "key": "whitchurch_stouffville",
                "name_en": "Town of Whitchurch-Stouffville",
                "name_fr": "Ville de Whitchurch-Stouffville",
                "population_2021": 48662,
                "area_km2": 208,
                "has_portal": False,
                "municipality_type": "town",
            },
            {
                "key": "georgina",
                "name_en": "Town of Georgina",
                "name_fr": "Ville de Georgina",
                "population_2021": 47530,
                "area_km2": 288,
                "has_portal": False,
                "municipality_type": "town",
            },
            {
                "key": "east_gwillimbury",
                "name_en": "Town of East Gwillimbury",
                "name_fr": "Ville d'East Gwillimbury",
                "population_2021": 36143,
                "area_km2": 250,
                "has_portal": False,
                "municipality_type": "town",
            },
            {
                "key": "king",
                "name_en": "Township of King",
                "name_fr": "Canton de King",
                "population_2021": 26700,
                "area_km2": 333,
                "has_portal": False,
                "municipality_type": "township",
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://york_region/feature_services",
    mime_type="application/json",
    name="york_region_feature_services",
    title="York Region OpenData FeatureServer Catalog",
)
def york_region_feature_services() -> str:
    """JSON catalog of York Region's major FeatureServer datasets on ww8.yorkmaps.ca.

    These are the curated Feature Services used by mcp-canada york_region tools.
    Use service_url with york_region_query_features for direct feature access.
    """
    return json.dumps(
        [
            {
                "name_en": "YRT/Viva Transit Stops",
                "name_fr": "Arrêts de transport YRT/Viva",
                "category": "transportation",
                "tool": "york_region_get_transit_stops",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "YRT/Viva Transit Routes",
                "name_fr": "Lignes de transport YRT/Viva",
                "category": "transportation",
                "tool": "york_region_get_transit_routes",
                "layer_id": 1,
                "has_feature_server": True,
            },
            {
                "name_en": "Regional Road Network",
                "name_fr": "Réseau routier régional",
                "category": "transportation",
                "tool": "york_region_get_road_network",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Beach Water Quality Testing",
                "name_fr": "Tests de qualité de l'eau des plages",
                "category": "health_safety",
                "tool": "york_region_get_public_health (location_type='beach_water')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Hospitals",
                "name_fr": "Hôpitaux",
                "category": "health_safety",
                "tool": "york_region_get_public_health (location_type='hospital')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Drinking Water Adverse Incidents",
                "name_fr": "Incidents défavorables d'eau potable",
                "category": "health_safety",
                "tool": "york_region_get_public_health (location_type='drinking_water')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "2021 Census by Dissemination Area - Age/Sex",
                "name_fr": "Recensement 2021 par aire de diffusion - Âge/Sexe",
                "category": "demographics",
                "tool": "york_region_get_census_demographics (dataset='age_sex')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "2021 Census by Dissemination Area - Income",
                "name_fr": "Recensement 2021 par aire de diffusion - Revenu",
                "category": "demographics",
                "tool": "york_region_get_census_demographics (dataset='income')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Solid Waste Diversion Statistics",
                "name_fr": "Statistiques de détournement des déchets solides",
                "category": "waste_management",
                "tool": "york_region_get_waste_data (dataset='diversion_statistics')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Solid Waste Sites",
                "name_fr": "Sites de gestion des déchets solides",
                "category": "waste_management",
                "tool": "york_region_get_waste_data (dataset='sites')",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Markham Civic Addresses",
                "name_fr": "Adresses civiques de Markham",
                "category": "markham_infrastructure",
                "tool": "markham_get_addresses",
                "layer_id": 0,
                "has_feature_server": True,
            },
            {
                "name_en": "Markham SLRN Road Network",
                "name_fr": "Réseau routier SLRN de Markham",
                "category": "markham_infrastructure",
                "tool": "markham_get_road_network",
                "layer_id": 0,
                "has_feature_server": True,
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://york_region/esri-field-naming",
    mime_type="text/markdown",
    name="york_region_esri_field_naming",
    title="ESRI Field Naming Conventions for York Region ArcGIS Data",
)
def york_region_esri_field_naming() -> str:
    """Markdown guide explaining ESRI/ArcGIS field naming conventions.

    Agents see ESRI field names verbatim — mcp-canada does NOT rename them.
    Use this guide to understand ALL_CAPS fields, OBJECTID, Shape__Length, etc.
    """
    return """# ESRI Field Naming Conventions — York Region ArcGIS Data

## Overview

York Region and its municipalities publish data via ArcGIS Feature Services.
ESRI systems use specific field naming conventions that differ from conventional
snake_case or camelCase. mcp-canada returns these field names **verbatim** — they
are not renamed or normalized.

## Standard ESRI System Fields

| Field | Type | Description |
|-------|------|-------------|
| `OBJECTID` | Integer | Unique row identifier assigned by ArcGIS. Not a stable ID — may change on data refresh. |
| `GLOBALID` | String | UUID assigned by ArcGIS. More stable than OBJECTID but not guaranteed across exports. |
| `Shape__Length` | Double | Perimeter or line length in the layer's coordinate system units (usually metres for Canadian data). |
| `Shape__Area` | Double | Polygon area in the layer's coordinate system units. |
| `Shape` | Geometry | GeoJSON geometry object — only present when `include_geometry=true`. |

## ALL_CAPS Field Names

ESRI data often uses ALL_CAPS field names, especially for census and administrative data:

```
CSDNAME       — Census Subdivision name (e.g., "Markham")
DAUID         — Dissemination Area unique identifier (7-digit string)
TOT_POP       — Total population
M_TOTAL       — Male total
F_TOTAL       — Female total
TOT_AVG_AGE_POP — Average age of total population
```

These are the names returned by the FeatureServer — use them exactly in
`out_fields` parameters or WHERE clauses.

## WHERE Clause Case Sensitivity

ArcGIS SQL uses **case-insensitive** matching for string fields by default on
most FeatureServer versions. However, rely on exact case for safety:

```sql
-- Safe
CSDNAME = 'Markham'

-- String contains (use LIKE)
STOP_NAME LIKE '%Finch%'
```

## Field Names in mcp-canada Responses

mcp-canada returns the feature `properties` dict verbatim. Example response from
`york_region_get_transit_stops`:

```json
{
  "STOP_ID": "14002",
  "STOP_NAME": "Finch / Yonge",
  "STOP_LAT": 43.7800,
  "STOP_LON": -79.4146,
  "WHEELCHAIR_BOARDING": 1,
  "OBJECTID": 42
}
```

## Census Field Naming Pattern

Census fields follow: `{PREFIX}_{AGE_GROUP}_{SEX}` where prefix is the measure type.
Example: `TOT_0_TO_14_YRS` = Total persons aged 0-14 years.

## Tips

- Use `out_fields='*'` in `york_region_query_features` to discover all available fields.
- Use `where='1=1'` to retrieve all records (up to max_records limit).
- `OBJECTID` is reliable as a row cursor but not as a stable entity identifier.
"""


@resource(
    "docs://york_region/portal-landscape",
    mime_type="text/markdown",
    name="york_region_portal_landscape",
    title="York Region Municipal Portal Landscape Guide",
)
def york_region_portal_landscape() -> str:
    """Markdown guide to York Region's 4-of-10 ArcGIS Hub portal landscape.

    Explains which municipalities have public portals, which don't, and
    what agents should expect when querying unavailable portals (NOT_FOUND).
    """
    return """# York Region Municipal Portal Landscape

## Overview

York Region is a two-tier government covering 1 regional government and 9 local
municipalities. As of April 2026, only **4 of the 10** have public ArcGIS Hub portals.

## Verified Portals (4)

| Municipality | Type | Tool Prefix | Approx Datasets |
|--------------|------|-------------|-----------------|
| York Region (Regional) | Regional government | `york_region_` | ~442 |
| City of Markham | Local municipality | `markham_` | ~65 |
| Town of Newmarket | Local municipality | `newmarket_` | ~61 |
| Town of Aurora | Local municipality | `aurora_` | ~21 |

Each verified portal gets 5 discovery tools:
- `{prefix}_search_datasets` — keyword search
- `{prefix}_get_dataset_details` — dataset metadata
- `{prefix}_query_features` — direct FeatureServer query
- `{prefix}_list_organizations` — publisher list
- `{prefix}_list_categories` — category tags

## Municipalities Without Public Portals (6)

The following municipalities have **no public ArcGIS Hub portal** as of April 2026.
They are completely out of scope for mcp-canada ArcGIS Hub tools.

| Municipality | Population (2021) |
|--------------|------------------|
| City of Vaughan | 323,103 |
| Town of Richmond Hill | 202,022 |
| Town of Whitchurch-Stouffville | 48,662 |
| Town of Georgina | 47,530 |
| Town of East Gwillimbury | 36,143 |
| Township of King | 26,700 |

**Note on Whitchurch-Stouffville:** Census data for this municipality is accessible
via the York Region regional portal (use `york_region_get_census_demographics` with
`csdname='Whitchurch-Stouffville'`).

## NOT_FOUND Responses

If you attempt to call a tool for a portal-less municipality (e.g., search for a
`vaughan_` tool), it will not exist in the tool catalog. The tool registration is
limited to the 4 verified portals. Use `discover_tools` or `call_tool` only with
verified portal prefixes.

## York Region vs Local Municipality Data

York Region (regional government) data covers region-wide services:
- YRT/Viva transit (operated by the region)
- Regional roads
- Public health programs
- Census demographics (all 9 local municipalities)
- Waste management

Local municipality data covers city-level services:
- Civic addresses (Markham)
- Municipal roads (Markham SLRN)
- Local zoning and building permits

## ArcGIS Hub vs CKAN

mcp-canada's first ArcGIS Hub module. Shared infrastructure is in
`shared/arcgis_hub.py` and is reusable for future Canadian municipal modules
that publish via ArcGIS Hub (British Columbia, Calgary, Edmonton, etc.).

Prior modules (Ontario, Toronto, federal CKAN) use CKAN-based portals — a
different API with different search and retrieval patterns.
"""


@resource(
    "docs://york_region/census-variables",
    mime_type="text/markdown",
    name="york_region_census_variables",
    title="York Region 2021 Census Focused Field Set Guide",
)
def york_region_census_variables() -> str:
    """Guide to the focused census field set returned by york_region_get_census_demographics.

    Explains the 10 returned columns, the 2021 Census 140-DA model for York Region,
    and how to access the full 364-field set via york_region_query_features.
    """
    return """# York Region 2021 Census — Variables Guide

## Tool: `york_region_get_census_demographics`

Queries the 2021 Census of Population data at the Dissemination Area (DA) level
for all of York Region. Returns a **focused 10-column set** to reduce context size.

## Focused Field Set (10 columns)

| Field | Description |
|-------|-------------|
| `CSDNAME` | Census Subdivision Name — which municipality the DA falls in (e.g., "Markham", "Vaughan") |
| `DAUID` | Dissemination Area Unique Identifier — 7-digit DA code from Statistics Canada |
| `TOT_POP` | Total population (all sexes, all ages) |
| `M_TOTAL` | Total male population |
| `F_TOTAL` | Total female population |
| `TOT_AVG_AGE_POP` | Average age of total population |
| `TOT_MED_AGE_POP` | Median age of total population |
| `TOT_0_TO_14_YRS` | Total persons aged 0 to 14 years |
| `TOT_15_TO_64_YRS` | Total persons aged 15 to 64 years |
| `TOT_65_YRS_OVER` | Total persons aged 65 years and over |

## Dataset Parameter

| Value | Data |
|-------|------|
| `'age_sex'` | Age/sex breakdown at DA level |
| `'income'` | Income statistics at DA level |

## Optional CSDNAME Filter

Use the `csdname` parameter to filter to a specific municipality:

```
york_region_get_census_demographics(dataset='age_sex', csdname='Markham')
york_region_get_census_demographics(dataset='age_sex', csdname='Vaughan')
york_region_get_census_demographics(dataset='age_sex', csdname='Aurora')
```

Available CSDNAME values: Markham, Vaughan, Richmond Hill, Newmarket, Aurora,
Whitchurch-Stouffville, Georgina, East Gwillimbury, King.

## Full Field Set

The 2021 Census FeatureServer has **364 fields** per DA record. To access
additional fields not in the focused set, use `york_region_query_features`
directly with the FeatureServer URL from `constants.py` and specify
`out_fields='DAUID,CSDNAME,{your_field}'`.

## 2021 Census Geography

York Region has approximately 559 Dissemination Areas across its 9 local
municipalities. Each DA typically represents 400-700 persons. The data aligns
with Statistics Canada's 2021 Census geography boundaries.

## Data Source

Statistics Canada 2021 Census, published via York Region Open Data ArcGIS Hub.
Dissemination area boundaries and field definitions are Statistics Canada
property. See: https://www12.statcan.gc.ca/census-recensement/2021/
"""


@resource(
    "docs://york_region/arcgis-query-patterns",
    mime_type="text/markdown",
    name="york_region_arcgis_query_patterns",
    title="ArcGIS FeatureServer Query Patterns for York Region",
)
def york_region_arcgis_query_patterns() -> str:
    """Markdown guide to ArcGIS SQL WHERE clause syntax for York Region FeatureServer queries.

    Covers ESRI SQL-92 subset, LIKE operator, case sensitivity, single-quote escaping,
    and provides examples for transit stops, census, and hospital queries.
    """
    return """# ArcGIS FeatureServer Query Patterns

## Overview

York Region's curated tools accept a `where` parameter that maps to the ArcGIS
FeatureServer `where` query parameter. The syntax is ESRI SQL-92 (a subset of SQL).

## Basic WHERE Syntax

### Get all records
```
where="1=1"
```

### Exact string match
```
where="CSDNAME = 'Markham'"
```
Note: Single quotes required for string literals. Double quotes are reserved for
field names (which are typically not needed in simple queries).

### String contains (LIKE)
```
where="STOP_NAME LIKE '%Finch%'"
```
The `%` wildcard matches any sequence of characters.

### Single-quote escaping
If your search string contains a single quote, double it:
```
where="STOP_NAME LIKE '%Tim''s%'"  -- Matches "Tim's Dairy"
```

### Numeric comparison
```
where="TOT_POP > 1000"
where="TOT_65_YRS_OVER >= 100"
```

### AND / OR / NOT
```
where="CSDNAME = 'Markham' AND TOT_POP > 500"
where="CSDNAME = 'Aurora' OR CSDNAME = 'Newmarket'"
```

## Case Sensitivity

ArcGIS FeatureServer string comparisons are **case-insensitive** on most
York Region services. `CSDNAME = 'markham'` and `CSDNAME = 'Markham'`
return the same results. However, use proper case for safety.

## Examples by Domain

### Transit Stop Queries
```
where="STOP_NAME LIKE '%Finch%'"
where="STOP_NAME LIKE '%Yonge%'"
where="WHEELCHAIR_BOARDING = 1"     -- Wheelchair accessible stops only
```

### Census Queries
```
where="CSDNAME = 'Vaughan'"
where="TOT_POP > 500 AND CSDNAME = 'Markham'"
where="TOT_65_YRS_OVER > 200"
```

### Hospital / Health Queries
```
where="1=1"     -- All hospitals (small dataset, safe to return all)
where="CITY = 'Newmarket'"
```

## Pagination and Record Limits

All curated tools cap at **5,000 records per call** (`max_records` parameter,
default varies by tool). When the result is truncated, the response includes:
```json
{"truncated": true, "truncated_at": 5000}
```

Use the `where` parameter to filter down before hitting the cap.
Use `offset` (via `york_region_query_features`) for pagination.

## Field Discovery

To discover all available fields for a Feature Service layer, use:
```
york_region_query_features(
    service_url="<FeatureServer URL>",
    layer_id=0,
    where="1=1",
    out_fields="*",
    max_records=1
)
```

The first record's keys show all available field names.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://york_region/transit-query-response",
    mime_type="text/markdown",
    name="york_region_transit_query_response_template",
    title="YRT/Viva Transit Query Response Template",
)
def york_region_transit_query_response_template() -> str:
    """Template for formatting a YRT/Viva transit stop or route query response.

    Replace {placeholder} values with actual data from york_region_get_transit_stops
    or york_region_get_transit_routes before presenting to the user.
    """
    return """# YRT/Viva Transit Query Results

**Query:** {query}
**Data source:** York Region Transportation FeatureServer
**Records returned:** {record_count} of {total_count} {truncated_note}

## Stop Results

| Stop ID | Stop Name | Lat | Lon | Wheelchair |
|---------|-----------|-----|-----|------------|
| {stop_id} | {stop_name} | {stop_lat} | {stop_lon} | {wheelchair_boarding} |

## Route Results

| Route ID | Short Name | Long Name | Route Type |
|----------|-----------|-----------|------------|
| {route_id} | {route_short_name} | {route_long_name} | {route_type} |

## Notes

- **YRT/Viva** operates regional bus service across York Region.
- Data comes from the ArcGIS Feature Service — not a live GTFS-Realtime feed.
- For real-time positions, YRT publishes a separate feed (not available in mcp-canada).
- `wheelchair_boarding`: 1 = accessible, 0 = not accessible, 2 = no information.
- Route types: 3 = bus, 0 = streetcar, 1 = subway.

**Cached:** {cached}
**Retrieved:** {timestamp}
"""
