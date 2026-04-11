"""BC open data resources — 7 static resources for British Columbia data exploration.

Resources provide agents with reference data and documentation:
- data://bc/ministries — BC ministry/agency catalog (JSON, bilingual inline)
- data://bc/wildfire-status-codes — fire status + cause code reference (JSON)
- data://bc/object-name-prefixes — BCGW schema prefix reference (JSON)
- docs://bc/wfs-query-guide — CKAN->WFS two-step workflow guide (Markdown, bilingual)
- docs://bc/bcdc-api-quirks — BC Data Catalogue API notes (Markdown, bilingual)
- template://bc/wildfire-report — wildfire analysis report template (Markdown)
- template://bc/dataset-report — dataset exploration report template (Markdown)

IMPORTANT: All functions are zero-parameter. Adding any parameter (even lang) would make
FastMCP treat them as ResourceTemplate instead of FunctionResource, removing them from
resources/list. Bilingual content is embedded inline.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://bc/ministries",
    mime_type="application/json",
    name="bc_ministries",
    title="BC Ministry and Agency Catalog with CKAN Organization Slugs",
)
async def bc_ministries() -> str:
    """JSON catalog of BC ministry and agency CKAN organization slugs.

    Use slug values in bc_search_datasets fq='organization:<slug>' to filter datasets
    by a specific BC ministry or agency. Includes bilingual name and description.
    """
    return json.dumps(
        [
            {
                "slug": "bc-wildfire-service",
                "name_en": "BC Wildfire Service",
                "name_fr": "Service de lutte contre les incendies de forêt de la C.-B.",
                "description_en": "Province-wide wildfire management, active fire data, perimeters",
                "description_fr": "Gestion provinciale des feux de forêt, données de feux actifs, périmètres",
                "ministry": "Ministry of Forests",
                "ministry_fr": "Ministère des Forêts",
            },
            {
                "slug": "env-air-quality",
                "name_en": "Environmental Monitoring and Reporting",
                "name_fr": "Surveillance et rapports environnementaux",
                "description_en": "Air quality, water quality, environmental monitoring data",
                "description_fr": "Qualité de l'air, qualité de l'eau, données de surveillance environnementale",
                "ministry": "Ministry of Environment and Climate Change Strategy",
                "ministry_fr": "Ministère de l'Environnement et de la stratégie pour les changements climatiques",
            },
            {
                "slug": "min-forests",
                "name_en": "Ministry of Forests",
                "name_fr": "Ministère des Forêts",
                "description_en": "Forest tenure, cut blocks, timber supply, forest health",
                "description_fr": "Tenure forestière, blocs de coupe, approvisionnement en bois, santé des forêts",
                "ministry": "Ministry of Forests",
                "ministry_fr": "Ministère des Forêts",
            },
            {
                "slug": "empr-mining",
                "name_en": "Ministry of Energy, Mines and Low Carbon Innovation",
                "name_fr": "Ministère de l'Énergie, des Mines et de l'Innovation bas carbone",
                "description_en": "Mining tenure, mineral claims, energy permits, LNG data",
                "description_fr": "Tenure minière, réclamations minérales, permis d'énergie, données GNL",
                "ministry": "Ministry of Energy, Mines and Low Carbon Innovation",
                "ministry_fr": "Ministère de l'Énergie, des Mines et de l'Innovation bas carbone",
            },
            {
                "slug": "min-water-land",
                "name_en": "Ministry of Water, Land and Resource Stewardship",
                "name_fr": "Ministère de la Gestion des eaux, des terres et des ressources",
                "description_en": "Water wells, aquifer data, groundwater licensing, land use",
                "description_fr": "Puits d'eau, données d'aquifère, licences d'eau souterraine, utilisation des terres",
                "ministry": "Ministry of Water, Land and Resource Stewardship",
                "ministry_fr": "Ministère de la Gestion des eaux, des terres et des ressources",
            },
            {
                "slug": "health-gateway",
                "name_en": "Ministry of Health",
                "name_fr": "Ministère de la Santé",
                "description_en": "Health facilities, emergency rooms, walk-in clinics, health authority data",
                "description_fr": "Établissements de santé, urgences, cliniques sans rendez-vous, données des autorités sanitaires",
                "ministry": "Ministry of Health",
                "ministry_fr": "Ministère de la Santé",
            },
            {
                "slug": "mot-transportation",
                "name_en": "Ministry of Transportation and Transit",
                "name_fr": "Ministère des Transports et des Transports en commun",
                "description_en": "Highway profiles, road structures, bridges, BC Transit data",
                "description_fr": "Profils d'autoroutes, structures routières, ponts, données de BC Transit",
                "ministry": "Ministry of Transportation and Transit",
                "ministry_fr": "Ministère des Transports et des Transports en commun",
            },
            {
                "slug": "bcparks",
                "name_en": "BC Parks",
                "name_fr": "Parcs de la Colombie-Britannique",
                "description_en": "Provincial parks, protected areas, park facilities, trail data",
                "description_fr": "Parcs provinciaux, aires protégées, installations des parcs, données sur les sentiers",
                "ministry": "Ministry of Environment and Climate Change Strategy",
                "ministry_fr": "Ministère de l'Environnement et de la stratégie pour les changements climatiques",
            },
            {
                "slug": "bc-stats",
                "name_en": "BC Stats",
                "name_fr": "Statistique C.-B.",
                "description_en": "Population projections, economic statistics, census-derived BC data",
                "description_fr": "Projections démographiques, statistiques économiques, données du recensement de la C.-B.",
                "ministry": "Ministry of Finance",
                "ministry_fr": "Ministère des Finances",
            },
            {
                "slug": "dfo-regional-data",
                "name_en": "Fisheries and Oceans Canada (BC Region)",
                "name_fr": "Pêches et Océans Canada (région C.-B.)",
                "description_en": "Fish habitat, holding areas, marine and freshwater fisheries data for BC",
                "description_fr": "Habitat du poisson, zones de détention, données sur les pêches marines et en eau douce pour la C.-B.",
                "ministry": "Fisheries and Oceans Canada (Federal — BC data)",
                "ministry_fr": "Pêches et Océans Canada (fédéral — données de la C.-B.)",
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://bc/wildfire-status-codes",
    mime_type="application/json",
    name="bc_wildfire_status_codes",
    title="BC Wildfire Status and Cause Codes",
)
async def bc_wildfire_status_codes() -> str:
    """JSON catalog of BC wildfire FIRE_STATUS and FIRE_CAUSE codes with bilingual labels.

    Use these codes with bc_get_active_fires status= parameter and to interpret
    FIRE_CAUSE field values in wildfire feature responses from BCGW.
    """
    return json.dumps(
        {
            "fire_status": [
                {
                    "code": "Out of Control",
                    "label_en": "Out of Control",
                    "label_fr": "Hors de contrôle",
                    "description_en": "Fire is spreading beyond its perimeter and cannot be contained with current resources. Highest urgency.",
                    "description_fr": "Le feu se répand au-delà de son périmètre et ne peut être contenu avec les ressources actuelles. Urgence maximale.",
                    "urgency": "critical",
                },
                {
                    "code": "Active",
                    "label_en": "Active",
                    "label_fr": "Actif",
                    "description_en": "Fire is burning and being actively fought. General active status.",
                    "description_fr": "Le feu est en train de brûler et fait l'objet d'une intervention active.",
                    "urgency": "high",
                },
                {
                    "code": "Being Held",
                    "label_en": "Being Held",
                    "label_fr": "Maintenu",
                    "description_en": "Fire is not expected to spread beyond its current perimeter with existing resources.",
                    "description_fr": "On s'attend à ce que le feu ne se répande pas au-delà de son périmètre actuel avec les ressources existantes.",
                    "urgency": "medium",
                },
                {
                    "code": "Under Control",
                    "label_en": "Under Control",
                    "label_fr": "Sous contrôle",
                    "description_en": "Fire will not spread significantly; suppression operations continue to ensure it is fully extinguished.",
                    "description_fr": "Le feu ne se répandra pas de manière significative; les opérations de suppression se poursuivent.",
                    "urgency": "low",
                },
                {
                    "code": "Out",
                    "label_en": "Out",
                    "label_fr": "Éteint",
                    "description_en": "Fire has been fully extinguished. No further action required.",
                    "description_fr": "Le feu a été complètement éteint. Aucune action supplémentaire n'est requise.",
                    "urgency": "none",
                },
            ],
            "fire_cause": [
                {
                    "code": "Lightning",
                    "label_en": "Lightning",
                    "label_fr": "Foudre",
                    "description_en": "Fire started by a lightning strike. Natural cause.",
                    "description_fr": "Feu déclenché par la foudre. Cause naturelle.",
                },
                {
                    "code": "Human",
                    "label_en": "Human",
                    "label_fr": "Humain",
                    "description_en": "Fire caused by human activity (campfire, equipment, arson, etc.).",
                    "description_fr": "Feu causé par une activité humaine (feu de camp, équipement, incendie criminel, etc.).",
                },
                {
                    "code": "Person",
                    "label_en": "Person",
                    "label_fr": "Personne",
                    "description_en": "Fire caused by a person — used interchangeably with Human in some datasets.",
                    "description_fr": "Feu causé par une personne — utilisé de façon interchangeable avec Humain dans certains jeux de données.",
                },
                {
                    "code": "Unknown",
                    "label_en": "Unknown",
                    "label_fr": "Inconnu",
                    "description_en": "Cause of fire has not been determined.",
                    "description_fr": "La cause du feu n'a pas encore été déterminée.",
                },
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://bc/object-name-prefixes",
    mime_type="application/json",
    name="bc_object_name_prefixes",
    title="BC Geographic Warehouse (BCGW) Object Name Schema Prefixes",
)
async def bc_object_name_prefixes() -> str:
    """JSON reference for BCGW schema prefixes and the 15 curated mcp-canada WFS layers.

    BCGW object_name format: WHSE_CATEGORY.TABLE_NAME
    All 10 WHSE_* schema prefixes are listed with their domain descriptions.
    The curated_layers sub-dict maps the 15 mcp-canada bc_ tool names to their object_name.
    """
    return json.dumps(
        {
            "note_en": "BCGW object_name format: WHSE_CATEGORY.TABLE_NAME (e.g. WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW)",
            "note_fr": "Format de object_name BCGW: WHSE_CATEGORY.NOM_TABLE (ex. WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW)",
            "schema_prefixes": [
                {
                    "prefix": "WHSE_LAND_AND_NATURAL_RESOURCE",
                    "domain_en": "Land and natural resource management — includes wildfire, weather stations, protected lands",
                    "domain_fr": "Gestion des terres et des ressources naturelles — inclut les feux de forêt, les stations météo, les terres protégées",
                    "examples": ["PROT_CURRENT_FIRE_PNTS_SP", "PROT_HISTORICAL_FIRE_POLYS_SP", "PROT_WEATHER_STATIONS_SP"],
                },
                {
                    "prefix": "WHSE_FOREST_TENURE",
                    "domain_en": "Forest tenure agreements, cut blocks, and managed forest areas",
                    "domain_fr": "Accords de tenure forestière, blocs de coupe et zones forestières gérées",
                    "examples": ["FTEN_MANAGED_LICENCE_POLY_SVW", "FTEN_CUT_BLOCK_POLY_SVW"],
                },
                {
                    "prefix": "WHSE_TANTALIS",
                    "domain_en": "Crown land disposition, parks, protected areas — TANTALIS database",
                    "domain_fr": "Disposition des terres de la Couronne, parcs, aires protégées — base de données TANTALIS",
                    "examples": ["TA_PARK_ECORES_PA_SVW"],
                    "note_en": "Use WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW for parks — NOT WHSE_PARKS_ECOLOGY (returns 400)",
                    "note_fr": "Utilisez WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW pour les parcs — PAS WHSE_PARKS_ECOLOGY (renvoie 400)",
                },
                {
                    "prefix": "WHSE_MINERAL_TENURE",
                    "domain_en": "Mineral and placer mining claims, tenure records",
                    "domain_fr": "Réclamations minières et d'exploitation aurifère, registres de tenure",
                    "examples": ["MTA_ACQUIRED_TENURE_SVW"],
                },
                {
                    "prefix": "WHSE_WATER_MANAGEMENT",
                    "domain_en": "Water licensing, groundwater wells, aquifer data",
                    "domain_fr": "Licences d'eau, puits d'eau souterraine, données d'aquifère",
                    "examples": ["GW_WATER_WELLS_WRBC_SVW"],
                    "note_en": "GW_WATER_WELLS_WRBC_SVW has 130K+ records — always filter by city or aquifer_id",
                    "note_fr": "GW_WATER_WELLS_WRBC_SVW contient 130K+ enregistrements — filtrez toujours par ville ou aquifer_id",
                },
                {
                    "prefix": "WHSE_WILDLIFE_MANAGEMENT",
                    "domain_en": "Wildlife habitat, holding areas, wildlife management units",
                    "domain_fr": "Habitat faunique, zones de détention, unités de gestion de la faune",
                    "examples": ["CRIMS_HOLDING_AREAS"],
                },
                {
                    "prefix": "WHSE_ENVIRONMENTAL_MONITORING",
                    "domain_en": "Environmental monitoring stations, air/water quality monitoring",
                    "domain_fr": "Stations de surveillance environnementale, surveillance de la qualité de l'air et de l'eau",
                    "examples": [],
                },
                {
                    "prefix": "WHSE_IMAGERY_AND_BASE_MAPS",
                    "domain_en": "Base map features — health facilities, transportation infrastructure",
                    "domain_fr": "Éléments de la carte de base — établissements de santé, infrastructure de transport",
                    "examples": ["GSR_EMERGENCY_ROOMS_SV", "GSR_MED_WALK_IN_CLINICS_SV", "MOT_HIGHWAY_PROFILES_SP", "MOT_ROAD_STRUCTURE_SP"],
                },
                {
                    "prefix": "WHSE_BASEMAPPING",
                    "domain_en": "Local and regional greenspace, parks, base mapping layers",
                    "domain_fr": "Espaces verts locaux et régionaux, parcs, couches de cartographie de base",
                    "examples": ["GBA_LOCAL_REG_GREENSPACES_SP"],
                },
                {
                    "prefix": "WHSE_PARKS_ECOLOGY",
                    "domain_en": "Parks and ecology — NOTE: this schema prefix returns HTTP 400 on WFS queries. Use WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW instead.",
                    "domain_fr": "Parcs et écologie — NOTE: ce préfixe de schéma renvoie HTTP 400 sur les requêtes WFS. Utilisez WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW à la place.",
                    "examples": [],
                    "warning": "Returns HTTP 400 on WFS queries — use WHSE_TANTALIS instead",
                },
            ],
            "curated_layers": {
                "bc_get_active_fires": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP",
                "bc_get_fire_perimeters": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
                "bc_get_forest_tenure": "WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW",
                "bc_get_cut_blocks": "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW",
                "bc_get_protected_areas": "WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW",
                "bc_get_water_wells": "WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW",
                "bc_get_wildfire_weather_stations": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP",
                "bc_get_local_parks": "WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP",
                "bc_get_mining_tenure": "WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW",
                "bc_get_fish_habitat": "WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS",
                "bc_get_emergency_rooms": "WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV",
                "bc_get_walk_in_clinics": "WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV",
                "bc_get_highway_profiles": "WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP",
                "bc_get_road_structures": "WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP",
                "bc_get_climate_stations": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://bc/wfs-query-guide",
    mime_type="text/markdown",
    name="bc_wfs_query_guide",
    title="BC WFS Query Guide — CKAN to WFS Two-Step Workflow",
)
async def bc_wfs_query_guide() -> str:
    """Markdown guide explaining the CKAN-to-WFS two-step workflow for BC open data.

    Explains how to discover datasets via CKAN, check WFS queryability, and query
    geospatial features via WFS. Includes CQL syntax primer and pagination notes.
    Both English and French sections in one document.
    """
    return """# BC WFS Query Guide — CKAN to WFS Two-Step Workflow

## Overview

BC open data uses two complementary systems:
- **BC Data Catalogue (BCDC)** — CKAN-based discovery portal for all 13,000+ BC datasets
- **BC Geographic Warehouse (BCGW)** — OGC WFS 2.0 endpoint for 870+ geospatial layers

The two-step workflow: **discover** (CKAN) → **query** (WFS).

---

## Step 1: Discover — bc_search_datasets + bc_get_dataset_details

```
bc_search_datasets(q="wildfire perimeters")
→ returns list of datasets with {id, title, organization, ...}

bc_get_dataset_details(package_id="<id from above>")
→ returns {title, organization, object_name, queryable_via_wfs, resources: [...]}
```

Key fields from `bc_get_dataset_details`:
- `object_name` — BCGW layer name in `WHSE_CATEGORY.TABLE_NAME` format
- `queryable_via_wfs` — `true` if this dataset can be queried via WFS
- `resources` — list of resource files (CSV, XLSX, GeoJSON, etc.) for non-WFS datasets

## Step 2a: Query via WFS (if queryable_via_wfs=true)

Use `bc_query_features` with the `object_name`:

```
bc_query_features(
    object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
    cql="FIRE_YEAR=2023",
    max_records=100,
    include_geometry=false
)
```

Or use a curated tool (faster, with named parameters):
```
bc_get_fire_perimeters(fire_year=2023, max_records=100)
```

## Step 2b: File download (if queryable_via_wfs=false)

Datasets without WFS support provide direct file URLs in their `resources` list.
Use the `url` field from the resource to download CSV/XLSX/GeoJSON directly.

---

## Concrete Example: 2023 Wildfire Perimeters

```
# Discover
results = bc_search_datasets(q="historical fire perimeters")
# Pick the result with title containing "Historical Fire Perimeters"

details = bc_get_dataset_details(package_id="<id>")
# object_name: "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"
# queryable_via_wfs: true

# Query with CQL filter
bc_query_features(
    object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
    cql="FIRE_YEAR=2023 AND FIRE_SIZE_HECTARES >= 1000",
    max_records=50
)
```

---

## CQL Syntax Primer

CQL (Common Query Language) is a SQL-like filter language for WFS queries.

### Equality
```
FIRE_YEAR=2023
FIRE_CAUSE='Lightning'
FIRE_STATUS='Out of Control'
```
Note: String values in single quotes. Numbers without quotes.

### Numeric comparison
```
FIRE_SIZE_HECTARES >= 1000
NUMBER_OF_LANES >= 4
ELEVATION >= 500
```

### String contains (LIKE)
```
CLIENT_NAME LIKE 'CANFOR%'
STATION_NAME LIKE 'Kamloops%'
```
The `%` wildcard matches any sequence. BCGW LIKE is case-sensitive — use uppercase.

### AND / OR
```
FIRE_YEAR=2023 AND FIRE_CAUSE='Lightning'
DESIGNATION='PROVINCIAL PARK' OR DESIGNATION='ECOLOGICAL RESERVE'
```

### Field names are UPPERCASE in BCGW
BCGW follows the convention that all field names are ALL_CAPS.
Use: `FIRE_STATUS='Active'` not `fire_status='Active'`

---

## Pagination and Truncation

The default cap is **5,000 records per call**. When the result is truncated:
```json
{"features": [...], "truncated": true}
```

Use `max_records` to set a lower limit. For layers with millions of records (e.g.
water wells: 130K+), always filter with CQL before querying.

---

---

# Guide de requête WFS en C.-B. — Flux de travail CKAN vers WFS en deux étapes

## Vue d'ensemble

Les données ouvertes de la C.-B. utilisent deux systèmes complémentaires:
- **Catalogue de données de la C.-B. (BCDC)** — portail de découverte CKAN pour 13 000+ jeux de données
- **BC Geographic Warehouse (BCGW)** — point de terminaison OGC WFS 2.0 pour 870+ couches géospatiales

Flux de travail en deux étapes: **découverte** (CKAN) → **requête** (WFS).

## Étape 1: Découverte — bc_search_datasets + bc_get_dataset_details

```
bc_search_datasets(q="périmètres de feux de forêt")
→ retourne une liste de jeux de données avec {id, title, organization, ...}

bc_get_dataset_details(package_id="<id ci-dessus>")
→ retourne {title, organization, object_name, queryable_via_wfs, resources: [...]}
```

## Étape 2: Requête via WFS (si queryable_via_wfs=true)

```
bc_query_features(
    object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
    cql="FIRE_YEAR=2023",
    max_records=100
)
```

## Exemple concret: Périmètres de feux 2023

```
details = bc_get_dataset_details(package_id="<id>")
# object_name: "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"
# queryable_via_wfs: true

bc_query_features(
    object_name="WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
    cql="FIRE_YEAR=2023 AND FIRE_SIZE_HECTARES >= 1000",
    max_records=50
)
```
"""


@resource(
    "docs://bc/bcdc-api-quirks",
    mime_type="text/markdown",
    name="bc_bcdc_api_quirks",
    title="BC Data Catalogue (BCDC) API Quirks and Custom Fields",
)
async def bc_bcdc_api_quirks() -> str:
    """Markdown guide documenting BCDC API quirks, bcgov custom fields, and known limitations.

    Covers bcdc_type, object_name, queryable_via_wfs derivation, no-groups quirk,
    and known ministry organization slugs. Bilingual — both EN and FR in one document.
    """
    return """# BC Data Catalogue (BCDC) API Quirks

## Custom Fields (bcgov CKAN Extensions)

BCDC extends standard CKAN with bcgov-specific fields on dataset packages:

| Field | Where | Description |
|-------|-------|-------------|
| `bcdc_type` | `extras` | Dataset type: `'Application'`, `'Dataset'`, `'Geographic Dataset'`, `'WebService'` |
| `object_name` | `extras` | BCGW layer name for geospatial datasets (e.g. `WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW`) |
| `resource_storage_location` | resource extras | Where data is stored: `'BC Geographic Warehouse'`, `'Catalogue Data Store'`, `'External'` |
| `projection_name` | resource extras | CRS for geospatial layers (e.g. `'EPSG_3005'` = BC Albers) |

## queryable_via_wfs Derivation

`queryable_via_wfs` is not a direct CKAN field — mcp-canada computes it:
```
queryable_via_wfs = True if:
    any resource has resource_storage_location == 'BC Geographic Warehouse'
    AND object_name is present in package extras
```

A dataset can have multiple resources (one WFS + one CSV backup). If the WFS resource
exists, `queryable_via_wfs=True` and `object_name` will be set.

## No Groups — Use Tags Instead

**BC CKAN group_list returns HTTP 403.** Groups are disabled on BCDC.
Use `bc_list_categories` (which calls `tag_list`) to browse subject areas.

```
# FAILS on BCDC:
# GET /api/3/action/group_list → 403 Forbidden

# Use instead:
bc_list_categories()   # calls tag_list — returns all subject tags
bc_search_datasets(fq="tags:<tag>")   # search by tag
```

## Organization Slugs

Always use the machine-readable slug (not the display name) in search filters:
```
bc_search_datasets(fq="organization:bc-wildfire-service")
bc_search_datasets(fq="organization:min-forests")
```

See `data://bc/ministries` for the full list of ministry slugs.

## Search Syntax Notes

- `q` parameter supports simple keyword matching (not full Solr syntax)
- `fq` supports Solr filter queries: `fq="organization:bc-wildfire-service tags:wildfire"`
- `rows` defaults to 10 — increase to 100 for broader results
- Results are ordered by relevance score by default
- `start` parameter enables pagination: `start=0`, `start=100`, etc.

## WFS Endpoint Details

- Base URL: `https://openmaps.gov.bc.ca/geo/ows`
- Protocol: OGC WFS 2.0.0
- Output format: `application/json` (GeoJSON)
- CQL filter parameter: `CQL_FILTER`
- Type name parameter: `typeNames` (not `typeName` — WFS 2.0 uses plural)
- Coordinate system: EPSG:4326 (WGS84) for GeoJSON output

## Common Pitfalls

1. **WHSE_PARKS_ECOLOGY** — returns HTTP 400. Use `WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW` instead.
2. **FTEN_CUT_BLOCK_POLYGONS** — deprecated. Use `FTEN_CUT_BLOCK_POLY_SVW`.
3. **group_list** — returns 403. Use `tag_list` via `bc_list_categories`.
4. **Water wells without filter** — 130K+ records. Always filter by city or aquifer_id.
5. **Field names in CQL** — must be ALL_CAPS to match BCGW convention.
6. **WFS truncation** — max 5,000 records per call. Check `truncated: true` in response.

---

# Particularités de l'API du Catalogue de données de la C.-B. (BCDC)

## Champs personnalisés (extensions CKAN de bcgov)

Le BCDC étend le CKAN standard avec des champs spécifiques à bcgov:

| Champ | Emplacement | Description |
|-------|-------------|-------------|
| `bcdc_type` | `extras` | Type de jeu de données: `'Application'`, `'Dataset'`, `'Geographic Dataset'`, `'WebService'` |
| `object_name` | `extras` | Nom de la couche BCGW pour les jeux de données géospatiaux |
| `resource_storage_location` | extras de ressource | Emplacement de stockage: `'BC Geographic Warehouse'`, etc. |
| `projection_name` | extras de ressource | SRC pour les couches géospatiales (ex. `'EPSG_3005'` = BC Albers) |

## Pas de groupes — utilisez les tags

**La liste de groupes CKAN retourne HTTP 403 sur le BCDC.** Utilisez `bc_list_categories`
(qui appelle `tag_list`) pour parcourir les domaines thématiques.

## Slugs d'organisation

Utilisez toujours le slug lisible par machine (pas le nom affiché) dans les filtres:
```
bc_search_datasets(fq="organization:bc-wildfire-service")
```
Consultez `data://bc/ministries` pour la liste complète des slugs de ministères.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://bc/wildfire-report",
    mime_type="text/markdown",
    name="bc_wildfire_report_template",
    title="BC Wildfire Season Analysis Report Template",
)
async def bc_wildfire_report_template() -> str:
    """Template for a BC wildfire season or situation report.

    Replace {placeholder} values with actual data from bc_get_active_fires,
    bc_get_fire_perimeters, and bc_get_wildfire_weather_stations before presenting.
    """
    return """# BC Wildfire Season Report

**Season:** {fire_season}
**Report date:** {report_date}
**Data source:** BC Wildfire Service — BC Geographic Warehouse (BCGW)

---

## Situation Summary

**Total active fires:** {total_active_fires}
**Total area burned (ha):** {total_area_ha}
**Largest fire:** {largest_fire} ({largest_fire_ha} ha) — {largest_fire_location}
**Most urgent status:** {most_urgent_status}

---

## Fires by Centre

| Fire Centre | Active | Out of Control | Being Held | Under Control |
|-------------|--------|----------------|------------|---------------|
| Kamloops | {kamloops_active} | {kamloops_ooc} | {kamloops_bh} | {kamloops_uc} |
| Coastal | {coastal_active} | {coastal_ooc} | {coastal_bh} | {coastal_uc} |
| Northwest | {northwest_active} | {northwest_ooc} | {northwest_bh} | {northwest_uc} |
| Prince George | {pg_active} | {pg_ooc} | {pg_bh} | {pg_uc} |
| Southeast | {southeast_active} | {southeast_ooc} | {southeast_bh} | {southeast_uc} |
| Cariboo | {cariboo_active} | {cariboo_ooc} | {cariboo_bh} | {cariboo_uc} |

---

## Cause Breakdown

| Cause | Count | % of Total |
|-------|-------|------------|
| Lightning | {lightning_count} | {lightning_pct}% |
| Human | {human_count} | {human_pct}% |
| Unknown | {unknown_count} | {unknown_pct}% |

---

## Historical Context

**Fire perimeters (historical season):** {perimeter_count} recorded perimeters
**Largest historical fire (same season):** {historical_largest} ({historical_ha} ha)

---

## Notes

- Data retrieved: {timestamp}
- Cached: {cached}
- Active fire data refreshes every 5 minutes from BCGW
- Perimeter data is updated daily during active fire season
"""


@resource(
    "template://bc/dataset-report",
    mime_type="text/markdown",
    name="bc_dataset_report_template",
    title="BC Dataset Exploration Report Template",
)
async def bc_dataset_report_template() -> str:
    """Template for a BC open data dataset exploration report.

    Replace {placeholder} values with actual data from bc_get_dataset_details
    and bc_query_features or bc_search_datasets before presenting.
    """
    return """# BC Dataset Exploration Report

**Dataset:** {dataset_title}
**Organization:** {organization}
**Report date:** {report_date}

---

## Dataset Metadata

| Field | Value |
|-------|-------|
| Dataset ID | {dataset_id} |
| Organization slug | {organization_slug} |
| BCDC type | {bcdc_type} |
| Object name (BCGW) | {object_name} |
| Queryable via WFS | {queryable_via_wfs} |
| Resources count | {resources_count} |
| License | {license} |
| Last modified | {last_modified} |

---

## Resource Files

| Format | Description | URL |
|--------|-------------|-----|
| {resource_format_1} | {resource_desc_1} | {resource_url_1} |
| {resource_format_2} | {resource_desc_2} | {resource_url_2} |

---

## Sample Data (first {sample_rows} records)

```json
{sample_data}
```

---

## Key Fields

{field_list}

---

## WFS Query Example

```
bc_query_features(
    object_name="{object_name}",
    cql="{example_cql}",
    max_records=100
)
```

---

## Notes

- Truncated: {truncated}
- Cached: {cached}
- Retrieved: {timestamp}
- For full CQL syntax, see: docs://bc/wfs-query-guide
"""
