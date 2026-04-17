"""Alberta resources — 7 zero-parameter static resources for Alberta data exploration.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same JSON or markdown body).

Catalog resources (data://):
  data://alberta/ministries      — 14 current provincial ministry slugs + bilingual labels
  data://alberta/forest-areas    — 10 Alberta Wildfire Forest Areas + approx hectares
  data://alberta/ahs-zones       — 5 Alberta Health Services zones + POP2006/2011/2016

Documentation guides (docs://):
  docs://alberta/aer-data-guide      — AER static reports (ST1/ST3/ST39) → tool mapping
  docs://alberta/wildfire-data-guide — WMBappServices vs CKAN, fire status codes,
                                       FWI deferral, AB-23 water-licence guidance

Templates (template://):
  template://alberta/dataset-report   — dataset exploration report template
  template://alberta/wildfire-report  — wildfire status report template
"""

import json

from fastmcp.resources import resource


__all__ = [
    "alberta_ministries",
    "alberta_forest_areas",
    "alberta_ahs_zones",
    "alberta_aer_data_guide",
    "alberta_wildfire_data_guide",
    "alberta_dataset_report_template",
    "alberta_wildfire_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://) — JSON via json.dumps
# ---------------------------------------------------------------------------


@resource(
    "data://alberta/ministries",
    mime_type="application/json",
    name="alberta_ministries",
    title="Alberta Provincial Ministry Catalog with CKAN Organization Slugs",
)
async def alberta_ministries() -> str:
    """JSON catalog of current Alberta provincial ministries with open.alberta.ca CKAN slugs.

    Use slug values in alberta_search_datasets organization= parameter to filter datasets
    by a specific Alberta ministry. Includes bilingual (EN/FR) name and description.
    Note: open.alberta.ca CKAN has 370 total orgs including ~150 historical predecessor
    ministries — call alberta_list_organizations for the full federated list.
    """
    ministries = [
        {
            "slug": "forestry-and-parks",
            "name_en": "Forestry and Parks",
            "name_fr": "Foresterie et Parcs",
            "description_en": "Provincial forests, wildfire management, Alberta Parks network",
            "description_fr": "Forêts provinciales, gestion des feux de forêt, réseau des parcs",
        },
        {
            "slug": "energy-and-minerals",
            "name_en": "Energy and Minerals",
            "name_fr": "Énergie et Mines",
            "description_en": "Oil, gas, minerals, energy policy (AER is a Crown agency, separate)",
            "description_fr": "Pétrole, gaz, minéraux, politique énergétique (AER est une société de la Couronne distincte)",
        },
        {
            "slug": "environment-and-protected-areas",
            "name_en": "Environment and Protected Areas",
            "name_fr": "Environnement et aires protégées",
            "description_en": "Air and water quality monitoring, protected areas, climate policy",
            "description_fr": "Surveillance qualité air et eau, aires protégées, politique climatique",
        },
        {
            "slug": "agriculture-and-irrigation",
            "name_en": "Agriculture and Irrigation",
            "name_fr": "Agriculture et Irrigation",
            "description_en": "Crop reports, farm data, irrigation districts, livestock statistics",
            "description_fr": "Rapports agricoles, données fermes, districts d'irrigation, statistiques bétail",
        },
        {
            "slug": "transportation-and-economic-corridors",
            "name_en": "Transportation and Economic Corridors",
            "name_fr": "Transport et corridors économiques",
            "description_en": "Highways, 511 Alberta road events, winter road conditions, cameras",
            "description_fr": "Autoroutes, événements routiers 511, conditions routières hivernales, caméras",
        },
        {
            "slug": "health",
            "name_en": "Health",
            "name_fr": "Santé",
            "description_en": "Health policy (AHS operates hospitals via AHSGIS FeatureServer)",
            "description_fr": "Politique de santé (AHS exploite les hôpitaux via FeatureServer AHSGIS)",
        },
        {
            "slug": "treasuryboardandfinance",
            "name_en": "Treasury Board and Finance",
            "name_fr": "Conseil du Trésor et Finances",
            "description_en": "Provincial budget, financial statements, economic indicators",
            "description_fr": "Budget provincial, états financiers, indicateurs économiques",
        },
        {
            "slug": "assisted-living-and-social-services",
            "name_en": "Assisted Living and Social Services",
            "name_fr": "Aide à la vie autonome et services sociaux",
            "description_en": "Continuing care, disability supports, income assistance",
            "description_fr": "Soins continus, soutiens pour handicap, aide au revenu",
        },
        {
            "slug": "education-and-childcare",
            "name_en": "Education and Childcare",
            "name_fr": "Éducation et services à l'enfance",
            "description_en": "K-12 schools, childcare facilities, student outcomes",
            "description_fr": "Écoles M-12, services à l'enfance, résultats des élèves",
        },
        {
            "slug": "children-and-family-services",
            "name_en": "Children and Family Services",
            "name_fr": "Services à l'enfance et à la famille",
            "description_en": "Child intervention, family supports, foster care programs",
            "description_fr": "Intervention enfance, soutiens famille, programmes d'accueil",
        },
        {
            "slug": "affordability-and-utilities",
            "name_en": "Affordability and Utilities",
            "name_fr": "Abordabilité et services publics",
            "description_en": "Utility rebates, consumer utility programs, cost of living data",
            "description_fr": "Remises sur services publics, programmes consommateurs, données coût de la vie",
        },
        {
            "slug": "servicealberta",
            "name_en": "Service Alberta",
            "name_fr": "Service Alberta",
            "description_en": "Registries, consumer protection, vital statistics, corporate data",
            "description_fr": "Registres, protection du consommateur, statistiques de l'état civil, données corporatives",
        },
        {
            "slug": "public-safety-and-emergency-services",
            "name_en": "Public Safety and Emergency Services",
            "name_fr": "Sécurité publique et services d'urgence",
            "description_en": "Police services, emergency management, fire services coordination",
            "description_fr": "Services de police, gestion d'urgence, coordination services incendie",
        },
        {
            "slug": "advancededucation",
            "name_en": "Advanced Education",
            "name_fr": "Enseignement supérieur",
            "description_en": "Post-secondary institutions, student aid, apprenticeship data",
            "description_fr": "Établissements postsecondaires, aide aux étudiants, données d'apprentissage",
        },
    ]
    return json.dumps(
        {
            "ministries": ministries,
            "_meta": {
                "description_en": (
                    "Current Alberta provincial ministry slugs for use as organization= in "
                    "alberta_search_datasets. Does not include the ~150 historical/predecessor "
                    "ministries also present in the 370-org federated catalog."
                ),
                "description_fr": (
                    "Slugs actuels des ministères provinciaux de l'Alberta à utiliser comme "
                    "organization= dans alberta_search_datasets. N'inclut pas les quelque 150 "
                    "ministères historiques/prédécesseurs également présents dans le catalogue "
                    "fédéré de 370 organisations."
                ),
                "note_en": "Call alberta_list_organizations for the full 370-org federated list.",
                "note_fr": "Appelez alberta_list_organizations pour la liste fédérée complète de 370 organisations.",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://alberta/forest-areas",
    mime_type="application/json",
    name="alberta_forest_areas",
    title="Alberta Wildfire Forest Areas (10 FA_NAMEs with approximate hectares)",
)
async def alberta_forest_areas() -> str:
    """JSON list of the 10 Alberta Wildfire Forest Areas with bilingual labels and approximate hectares.

    Forest Areas are the administrative divisions used by Wildfire Management Branch
    to assign fire response and publish fire control orders. Use alberta_get_fire_control_orders
    (category='forest_area') to query live polygons; this resource is a static reference
    catalog. AREA_HECTARES values are approximate — call the live tool for authoritative figures.
    """
    forest_areas = [
        {
            "fa_name": "High Level",
            "name_en": "High Level",
            "name_fr": "High Level",
            "area_hectares": 7_800_000,
        },
        {
            "fa_name": "Fort McMurray",
            "name_en": "Fort McMurray",
            "name_fr": "Fort McMurray",
            "area_hectares": 9_400_000,
        },
        {
            "fa_name": "Peace River",
            "name_en": "Peace River",
            "name_fr": "Rivière-la-Paix",
            "area_hectares": 4_200_000,
        },
        {
            "fa_name": "Slave Lake",
            "name_en": "Slave Lake",
            "name_fr": "Lac-des-Esclaves",
            "area_hectares": 4_100_000,
        },
        {
            "fa_name": "Lac La Biche",
            "name_en": "Lac La Biche",
            "name_fr": "Lac La Biche",
            "area_hectares": 3_900_000,
        },
        {
            "fa_name": "Grande Prairie",
            "name_en": "Grande Prairie",
            "name_fr": "Grande Prairie",
            "area_hectares": 3_500_000,
        },
        {
            "fa_name": "Whitecourt",
            "name_en": "Whitecourt",
            "name_fr": "Whitecourt",
            "area_hectares": 2_400_000,
        },
        {
            "fa_name": "Edson",
            "name_en": "Edson",
            "name_fr": "Edson",
            "area_hectares": 2_000_000,
        },
        {
            "fa_name": "Rocky Mountain House",
            "name_en": "Rocky Mountain House",
            "name_fr": "Rocky Mountain House",
            "area_hectares": 2_800_000,
        },
        {
            "fa_name": "Calgary",
            "name_en": "Calgary",
            "name_fr": "Calgary",
            "area_hectares": 1_800_000,
        },
    ]
    return json.dumps(
        {
            "forest_areas": forest_areas,
            "_meta": {
                "count": len(forest_areas),
                "description_en": (
                    "The 10 Alberta Wildfire Forest Areas used by Wildfire Management Branch "
                    "to coordinate fire response. Polygons are available via "
                    "alberta_get_fire_control_orders(category='forest_area')."
                ),
                "description_fr": (
                    "Les 10 zones forestières Alberta Wildfire utilisées par la Direction de "
                    "gestion des feux pour coordonner la réponse. Polygones disponibles via "
                    "alberta_get_fire_control_orders(category='forest_area')."
                ),
                "area_hectares_note_en": (
                    "Approximate values from Wildfire Management Branch summaries. "
                    "Call alberta_get_fire_control_orders(category='forest_area') for "
                    "authoritative geographic extents."
                ),
                "area_hectares_note_fr": (
                    "Valeurs approximatives des résumés de la Direction de gestion des feux. "
                    "Appelez alberta_get_fire_control_orders(category='forest_area') pour les "
                    "étendues géographiques autoritaires."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://alberta/ahs-zones",
    mime_type="application/json",
    name="alberta_ahs_zones",
    title="Alberta Health Services Zones (5 zones with POP2006/2011/2016)",
)
async def alberta_ahs_zones() -> str:
    """JSON list of the 5 Alberta Health Services (AHS) zones with historical population stats.

    AHS divides Alberta into 5 health-service zones: South, Calgary, Central, Edmonton, North.
    Population figures (pop_2006/pop_2011/pop_2016) are derived from Statistics Canada
    Census aggregates reported by AHS. Call alberta_get_ahs_zones for live boundaries and
    authoritative population totals from the AHS_Zone FeatureServer.
    """
    zones = [
        {
            "zone_id": 1,
            "zone_name": "South",
            "name_en": "South",
            "name_fr": "Sud",
            "pop_2006": 273_041,
            "pop_2011": 289_661,
            "pop_2016": 305_961,
        },
        {
            "zone_id": 2,
            "zone_name": "Calgary",
            "name_en": "Calgary",
            "name_fr": "Calgary",
            "pop_2006": 1_234_054,
            "pop_2011": 1_408_606,
            "pop_2016": 1_544_495,
        },
        {
            "zone_id": 3,
            "zone_name": "Central",
            "name_en": "Central",
            "name_fr": "Centre",
            "pop_2006": 425_989,
            "pop_2011": 453_469,
            "pop_2016": 480_944,
        },
        {
            "zone_id": 4,
            "zone_name": "Edmonton",
            "name_en": "Edmonton",
            "name_fr": "Edmonton",
            "pop_2006": 1_123_517,
            "pop_2011": 1_261_720,
            "pop_2016": 1_400_298,
        },
        {
            "zone_id": 5,
            "zone_name": "North",
            "name_en": "North",
            "name_fr": "Nord",
            "pop_2006": 433_378,
            "pop_2011": 447_740,
            "pop_2016": 466_100,
        },
    ]
    return json.dumps(
        {
            "zones": zones,
            "_meta": {
                "count": len(zones),
                "description_en": (
                    "The 5 Alberta Health Services zones used for hospitals, EMS stations, "
                    "and continuing care planning. Population stats are Statistics Canada "
                    "Census-derived aggregates reported by AHS."
                ),
                "description_fr": (
                    "Les 5 zones d'Alberta Health Services utilisées pour les hôpitaux, "
                    "stations EMS, et planification des soins continus. Statistiques de "
                    "population dérivées des recensements de Statistique Canada et reportées par AHS."
                ),
                "population_note_en": (
                    "Population fields are static references. Call alberta_get_ahs_zones "
                    "for live authoritative values from the AHS_Zone FeatureServer."
                ),
                "population_note_fr": (
                    "Les champs de population sont des références statiques. Appelez "
                    "alberta_get_ahs_zones pour les valeurs vivantes autoritaires du "
                    "FeatureServer AHS_Zone."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Documentation guides (docs://) — markdown with both languages inline
# ---------------------------------------------------------------------------


@resource(
    "docs://alberta/aer-data-guide",
    mime_type="text/markdown",
    name="alberta_aer_data_guide",
    title="Alberta Energy Regulator (AER) Data Surfaces and Tool Mapping",
)
async def alberta_aer_data_guide() -> str:
    """Markdown guide explaining AER (Alberta Energy Regulator) static report surfaces.

    Covers: ST1 daily well licences, ST3 monthly production XLSX, ST39 annual pipeline
    statistics, product slug casing, OneStop auth requirement, ST57 PDF-only status.
    """
    return """# Alberta Energy Regulator (AER) Data Guide / Guide des données AER

## English

The Alberta Energy Regulator (AER) publishes statistical reports as **static XLSX/TXT
files** at `https://static.aer.ca/prd/`. There is **no public REST API** — the OneStop
API requires authentication and is not available via MCP. ST57 (incident/spill) reports
have been PDF-only since 2014 and are not exposed as a tool.

### Tool → Source mapping

| Tool | AER Report | URL Pattern |
|------|-----------|-------------|
| `alberta_get_well_licences_today` | ST1 daily TXT | `static.aer.ca/prd/data/well-lic/WELLS{DAY}.TXT` |
| `alberta_get_well_licences_archive` | ST1 monthly ZIP | `static.aer.ca/prd/data/well-lic/dwll{YYYY}-{MM}.zip` |
| `alberta_get_pipeline_statistics` | ST39 annual XLSX | `static.aer.ca/prd/documents/sts/ST39-{YYYY}.xls` |
| `alberta_get_production_volumes` | ST3 monthly XLSX | `static.aer.ca/prd/documents/sts/st3/{Product}_current.xlsx` |

### ST1 daily rotation (day-of-week abbreviations)

AER overwrites `WELLS{DAY}.TXT` once per weekday. `DAY` values cycle: `MON`, `TUE`,
`WED`, `THU`, `FRI`, `SAT`, `SUN`. The tool computes today's abbreviation automatically
via `DAY_ABBR` in `constants.py`.

### ST3 product slugs — case-sensitive (Pitfall 8)

Valid product slugs (exact casing enforced by AER URL routing):

- `Butane`
- `Ethane`
- `NGL`
- `Oil`
- `Gas`
- `Propane`
- `Sulphur`

NOT valid: lowercase variants (`oil`, `gas`) return HTTP 404. Not separate products:
`Bitumen` is included inside `Oil`; `CrudeOil` is also inside `Oil`.

### Deferred / not available

- **ST57 (incidents / spills)**: PDF-only since 2014. Not exposed as a tool.
- **OneStop API (active wells real-time)**: requires authentication. Not available.
- **AER incident registry**: auth-protected; honors mcp-canada no-scraping discipline.

---

## Français

L'Alberta Energy Regulator (AER) publie des rapports statistiques sous forme de
**fichiers XLSX/TXT statiques** à `https://static.aer.ca/prd/`. **Aucune API REST
publique** — l'API OneStop nécessite une authentification et n'est pas disponible
via MCP. Les rapports ST57 (incidents/déversements) sont uniquement en PDF depuis
2014 et ne sont pas exposés comme outil.

### Cartographie outil → source

| Outil | Rapport AER | Modèle d'URL |
|-------|-------------|--------------|
| `alberta_get_well_licences_today` | ST1 TXT quotidien | `static.aer.ca/prd/data/well-lic/WELLS{JOUR}.TXT` |
| `alberta_get_well_licences_archive` | ST1 archive ZIP mensuelle | `static.aer.ca/prd/data/well-lic/dwll{AAAA}-{MM}.zip` |
| `alberta_get_pipeline_statistics` | ST39 annuel XLSX | `static.aer.ca/prd/documents/sts/ST39-{AAAA}.xls` |
| `alberta_get_production_volumes` | ST3 mensuel XLSX | `static.aer.ca/prd/documents/sts/st3/{Produit}_current.xlsx` |

### Rotation quotidienne ST1 (abréviations jours)

AER remplace `WELLS{JOUR}.TXT` chaque jour ouvré. Les valeurs de `JOUR` alternent :
`MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN`. L'outil calcule automatiquement
l'abréviation du jour via `DAY_ABBR` dans `constants.py`.

### Slugs de produits ST3 — sensibles à la casse (Pitfall 8)

Slugs de produits valides (casse exacte imposée par le routage d'URL AER) :
`Butane`, `Ethane`, `NGL`, `Oil`, `Gas`, `Propane`, `Sulphur`. Les variantes minuscules
(`oil`, `gas`) retournent HTTP 404. Le bitume et le pétrole brut sont inclus dans `Oil`.

### Différé / non disponible

- **ST57 (incidents / déversements)** : PDF uniquement depuis 2014. Non exposé.
- **API OneStop (puits actifs temps réel)** : requiert authentification. Non disponible.
- **Registre des incidents AER** : protégé par authentification ; respecte la discipline
  no-scraping de mcp-canada.
"""


@resource(
    "docs://alberta/wildfire-data-guide",
    mime_type="text/markdown",
    name="alberta_wildfire_data_guide",
    title="Alberta Wildfire Data Guide — WMBappServices vs CKAN, Status Codes, AB-23 Guidance",
)
async def alberta_wildfire_data_guide() -> str:
    """Markdown guide on Alberta wildfire data sources, status codes, FWI deferral, AB-23 guidance.

    Covers: WMBappServices vs CKAN source-of-truth policy, fire status codes,
    the 10 forest areas, FWI not exposed note, and the AB-23 water-licence-data
    CKAN package guidance (too large to fetch via alberta_query_dataset).
    """
    return """# Alberta Wildfire Data Guide / Guide des données sur les feux de forêt en Alberta

## English

### Source-of-Truth Matrix

| Use Case | Tool | Source |
|----------|------|--------|
| Current active fires | `alberta_get_active_fires` | WMBappServices `Active_Wildfires_Dashboard_view` FeatureServer |
| Active fire perimeters | `alberta_get_fire_perimeters(status='active')` | WMBappServices `Active_Wildfire_Perimeters_Simplified_view` |
| Historical perimeters | `alberta_get_fire_perimeters(status='extinguished')` | WMBappServices `Extinguished_Wildfire_Perimeters_Simplified_view` |
| Fire bans | `alberta_get_fire_bans` | WMBappServices `alberta_fire_ban_system` FeatureServer |
| Fire control orders / OHV restrictions / forest area boundaries | `alberta_get_fire_control_orders(category=...)` | WMBappServices `Fire_Control_Orders_Prod_View2`, `OHV_RestrictionL_Prod_View`, `Forest_Area_Prod_View2` |
| Historical 2006-2025 CSV | `alberta_query_dataset(dataset_id='wildfire-data')` | open.alberta.ca CKAN |

WMBappServices (Wildfire Management Branch on ArcGIS Online, org `Eb8P5h4CJk8utIBz`)
is the live source of truth. CKAN's `wildfire-data` package provides historical CSV
(~10MB) that complements the live FeatureServers.

### Fire Status Codes

- **Out / Extinguished** — fire fully suppressed
- **Out of Control** — actively spreading, highest priority
- **Being Held** — not spreading but not extinguished
- **Under Control** — extinguished within the fire perimeter

### Forest Areas (10)

High Level, Fort McMurray, Peace River, Slave Lake, Lac La Biche, Grande Prairie,
Whitecourt, Edson, Rocky Mountain House, Calgary. Use
`alberta_get_fire_control_orders(category='forest_area')` for live boundaries, or
see `data://alberta/forest-areas` for static reference with approximate hectares.

### Fire Weather Index (FWI) — NOT exposed

The Canadian Forest Fire Weather Index components (FFMC / DMC / DC) are **not
published** by WMBappServices, GeoDiscover Alberta, open.alberta.ca CKAN, or
MSC weather (Phase 4 module). The originally-planned `alberta_get_fire_weather`
tool was replaced with `alberta_get_fire_control_orders` during Plan 04.

### AB-23: Water-Licence Data Guidance

The Alberta water-licence-data CKAN package contains **~87 MB of active licences
and ~169 MB of inactive licences** across CSV resources — far too large to fetch
in full via `alberta_query_dataset`. Agents should:

1. Discover the package via `alberta_search_datasets(q='water licence')`.
2. Inspect metadata with `alberta_get_dataset_details(dataset_id='water-licence-data')`.
3. For retrieval, use external download tools (HTTP + streaming parsers) against
   the resource URLs returned in step 2. Do **not** call `alberta_query_dataset`
   against the full resources — it will time out or return truncated rows.

This is documentation-only guidance for requirement AB-23.

---

## Français

### Matrice source de vérité

| Cas d'usage | Outil | Source |
|-------------|-------|--------|
| Feux actifs courants | `alberta_get_active_fires` | WMBappServices `Active_Wildfires_Dashboard_view` |
| Périmètres de feux actifs | `alberta_get_fire_perimeters(status='active')` | WMBappServices `Active_Wildfire_Perimeters_Simplified_view` |
| Périmètres historiques | `alberta_get_fire_perimeters(status='extinguished')` | WMBappServices `Extinguished_Wildfire_Perimeters_Simplified_view` |
| Interdictions de feux | `alberta_get_fire_bans` | WMBappServices `alberta_fire_ban_system` |
| Ordres contrôle / restrictions OHV / zones forestières | `alberta_get_fire_control_orders(category=...)` | 3 FeatureServers WMBappServices |
| Archive CSV 2006-2025 | `alberta_query_dataset(dataset_id='wildfire-data')` | CKAN open.alberta.ca |

WMBappServices (Direction de gestion des feux sur ArcGIS Online, org `Eb8P5h4CJk8utIBz`)
est la source de vérité en direct. Le paquet CKAN `wildfire-data` fournit le CSV
historique (~10 Mo) qui complète les FeatureServers live.

### Codes de statut de feu

- **Out / Extinguished** — feu entièrement maîtrisé
- **Out of Control** — en propagation active, priorité maximale
- **Being Held** — contenu mais non éteint
- **Under Control** — éteint à l'intérieur du périmètre

### Zones forestières (10)

High Level, Fort McMurray, Peace River (Rivière-la-Paix), Slave Lake (Lac-des-Esclaves),
Lac La Biche, Grande Prairie, Whitecourt, Edson, Rocky Mountain House, Calgary.
Utilisez `alberta_get_fire_control_orders(category='forest_area')` pour les limites
en direct, ou voir `data://alberta/forest-areas` pour la référence statique.

### Indice forêt-météo (FWI) — NON exposé

Les composantes de l'Indice Canadien de Danger d'Incendie de Forêt (FFMC / DMC / DC)
ne sont **pas publiées** par WMBappServices, GeoDiscover Alberta, CKAN, ou MSC weather.
L'outil initialement prévu `alberta_get_fire_weather` a été remplacé par
`alberta_get_fire_control_orders` pendant le Plan 04.

### AB-23 : Orientation sur les licences d'eau

Le paquet CKAN water-licence-data Alberta contient **~87 Mo de licences actives
et ~169 Mo de licences inactives** en ressources CSV — bien trop volumineux pour
une récupération complète via `alberta_query_dataset`. Les agents doivent :

1. Découvrir le paquet via `alberta_search_datasets(q='water licence')`.
2. Inspecter les métadonnées avec `alberta_get_dataset_details(dataset_id='water-licence-data')`.
3. Pour la récupération, utiliser des outils de téléchargement externes (HTTP +
   analyseurs en flux) contre les URL de ressources retournées à l'étape 2.
   **Ne pas** appeler `alberta_query_dataset` contre les ressources complètes —
   cela expirera ou retournera des lignes tronquées.

Ceci constitue une orientation documentaire pour l'exigence AB-23.
"""


# ---------------------------------------------------------------------------
# Templates (template://) — markdown with {placeholder} syntax
# ---------------------------------------------------------------------------


@resource(
    "template://alberta/dataset-report",
    mime_type="text/markdown",
    name="alberta_dataset_report_template",
    title="Alberta Dataset Exploration Report Template",
)
async def alberta_dataset_report_template() -> str:
    """Markdown template for reporting Alberta dataset exploration findings.

    Fill in placeholders with actual values from alberta_search_datasets,
    alberta_get_dataset_details, and alberta_query_dataset calls.
    """
    return """# Alberta Dataset Exploration Report

**Date:** {date}
**Dataset searched:** {search_query}
**Organization filter:** {organization_filter}
**Format filter:** {format_filter}

## Search Results Summary

- **Total datasets found:** {total_count}
- **Results returned:** {results_count}
- **Format breakdown:** {format_breakdown}

## Dataset Spotlight

**Dataset slug:** {dataset_slug}
**Title:** {dataset_title}
**Organization:** {organization_name}
**License:** {license_id}
**Update frequency:** {update_frequency}
**Number of resources:** {num_resources}

### Best Machine-Readable Resource

- **Format:** {best_resource_format}
- **URL:** {best_resource_url}
- **Routing path:** {routing_path}

## Sample Data (first {sample_count} records)

{sample_data_table}

## Notes

- **Catalog:** open.alberta.ca CKAN (33,269 datasets across 370 orgs)
- **Federated nature:** Results include current ministries AND ~150 historical/predecessor ministries
- **PDF warning:** 86% of Alberta datasets are PDF reports — `format=` filter recommended
- **Auto-router:** `alberta_query_dataset` prefers FeatureServer over file resources when available

## Next Steps

- [ ] Refine with `alberta_search_datasets(q='{related_keyword}')`
- [ ] Check other formats via `alberta_list_categories`
- [ ] Filter by another org: `organization='{organization_slug}'`
"""


@resource(
    "template://alberta/wildfire-report",
    mime_type="text/markdown",
    name="alberta_wildfire_report_template",
    title="Alberta Wildfire Status Report Template",
)
async def alberta_wildfire_report_template() -> str:
    """Markdown template for reporting Alberta wildfire situational awareness.

    Fill in placeholders with actual values from alberta_get_active_fires,
    alberta_get_fire_perimeters, alberta_get_fire_bans, and
    alberta_get_fire_control_orders calls.
    """
    return """# Alberta Wildfire Status Report — {report_date}

**Data source:** WMBappServices FeatureServers (live, 5-min TTL)
**Fire season:** {season_window}

## Active Fires Summary

- **Total active fires:** {active_count}
- **Out of Control:** {out_of_control_count}
- **Being Held:** {being_held_count}
- **Under Control:** {under_control_count}

## Largest Active Fire

- **Fire number:** {largest_fire_number}
- **Area estimate (ha):** {largest_fire_area}
- **Status:** {largest_fire_status}
- **General cause:** {largest_fire_cause}
- **Responsible forest area:** {largest_fire_resp_area}

## Forest Area Breakdown

| Forest Area | Active Fires | Out of Control |
|-------------|--------------|----------------|
| {fa_name_1} | {fa_count_1} | {fa_ooc_1} |
| {fa_name_2} | {fa_count_2} | {fa_ooc_2} |
| {fa_name_3} | {fa_count_3} | {fa_ooc_3} |

See `data://alberta/forest-areas` for the full 10-area reference catalog.

## Active Fire Bans / Advisories

- **Total restriction zones:** {ban_zones_count}
- **Full fire bans:** {full_bans_count}
- **OHV restrictions:** {ohv_restrictions_count}

## Active Fire Control Orders

{control_orders_summary}

## Notes

- **Status codes:** `Out of Control` (spreading, highest priority), `Being Held`
  (contained but not out), `Under Control` (extinguished within perimeter),
  `Out` / `Extinguished` (fully suppressed).
- **FWI:** Canadian Forest Fire Weather Index components (FFMC/DMC/DC) are NOT
  published by Alberta — see `docs://alberta/wildfire-data-guide`.
- **Historical:** For 2006-2025 archive, call
  `alberta_query_dataset(dataset_id='wildfire-data')` (CSV ~10MB).

## Data Freshness

- **Active fires:** {active_fires_ts}
- **Perimeters:** {perimeters_ts}
- **Fire bans:** {fire_bans_ts}
"""
