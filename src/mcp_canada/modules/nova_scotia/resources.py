"""Nova Scotia module resources — 7 zero-parameter @resource functions for the MCP server.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same JSON or markdown body).

URI scheme conventions:
  data:// — JSON catalogs: return json.dumps(...). Bilingual content inline.
  docs:// — Markdown guides: return raw markdown string. Both languages in same document.
  template:// — Markdown templates: return markdown with {placeholder} syntax.

Catalog resources (data://):
  data://ns/categories      — 26 NS domain categories with bilingual labels inline
  data://ns/health-zones    — 4 NS health zones (Western/Northern/Eastern/Central) with member counties
  data://ns/fishing-areas   — NS aquaculture lease counties + speciestyp values (Shellfish/Finfish/Marine Plant)
  data://ns/departments     — NS government departments publishing on data.novascotia.ca

Documentation guides (docs://):
  docs://ns/socrata-guide   — How SODA/SoQL works: $where/$select/$order/$group/$limit/$offset
                              with NS examples; categories= broken-param workaround;
                              geometry via $select; X-App-Token for higher throttle.
                              FIRST Socrata portal canonical how-to.
  docs://ns/portal-guide    — Socrata-first (4th portal technology); transport/511 deferred
                              (HTML-only, no stubs); NS ArcGIS Hub (novagis) deferred (no public
                              no-auth FeatureServers); air quality individual pollutant series
                              via ns_query_dataset; Open Government Licence NS v1.1.

Templates (template://):
  template://ns/aquaculture-report — Template with {placeholder} fields for aquaculture analysis
"""

from __future__ import annotations

import json

from fastmcp.resources import resource


__all__ = [
    "ns_categories",
    "ns_health_zones",
    "ns_fishing_areas",
    "ns_departments",
    "ns_socrata_guide",
    "ns_portal_guide",
    "ns_aquaculture_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://) — JSON via json.dumps, bilingual inline
# ---------------------------------------------------------------------------


@resource(
    "data://ns/categories",
    mime_type="application/json",
    name="ns_categories",
    title="Nova Scotia Open Data Categories — 26 Domain Categories on data.novascotia.ca",
)
async def ns_categories() -> str:
    """JSON catalog of all 26 domain categories on Nova Scotia's data.novascotia.ca Socrata portal.

    Use to understand the topic taxonomy for ns_search_datasets queries. NOTE: The Socrata
    categories= API parameter is broken (returns resultSetSize=0). Use q= keyword search
    for category-specific discovery, or filter client-side on domain_category. These
    categories are aggregated from live catalog enumeration (2026-06-15, 706 datasets).
    See docs://ns/socrata-guide for the categories= workaround explanation.
    """
    categories = [
        {
            "id": "Agriculture and Agri-business",
            "name_en": "Agriculture and Agri-business",
            "name_fr": "Agriculture et agroalimentaire",
        },
        {
            "id": "Business and Economy",
            "name_en": "Business and Economy",
            "name_fr": "Affaires et économie",
        },
        {
            "id": "Business and Industry",
            "name_en": "Business and Industry",
            "name_fr": "Affaires et industrie",
        },
        {
            "id": "Communications",
            "name_en": "Communications",
            "name_fr": "Communications",
        },
        {
            "id": "Community Services",
            "name_en": "Community Services",
            "name_fr": "Services communautaires",
        },
        {
            "id": "Crime and Justice",
            "name_en": "Crime and Justice",
            "name_fr": "Crime et justice",
        },
        {
            "id": "Education - Early Childhood",
            "name_en": "Education - Early Childhood",
            "name_fr": "Éducation — petite enfance",
        },
        {
            "id": "Education - Post-Secondary and Skills Training",
            "name_en": "Education - Post-Secondary and Skills Training",
            "name_fr": "Éducation — postsecondaire et formation professionnelle",
        },
        {
            "id": "Education - Primary to Grade 12",
            "name_en": "Education - Primary to Grade 12",
            "name_fr": "Éducation — primaire à 12e année",
        },
        {
            "id": "Employment and Labour",
            "name_en": "Employment and Labour",
            "name_fr": "Emploi et travail",
        },
        {
            "id": "Environment and Energy",
            "name_en": "Environment and Energy",
            "name_fr": "Environnement et énergie",
        },
        {
            "id": "Financial Services",
            "name_en": "Financial Services",
            "name_fr": "Services financiers",
        },
        {
            "id": "Fishing and Aquaculture",
            "name_en": "Fishing and Aquaculture",
            "name_fr": "Pêche et aquaculture",
        },
        {
            "id": "Government Administration",
            "name_en": "Government Administration",
            "name_fr": "Administration gouvernementale",
        },
        {
            "id": "Health and Wellness",
            "name_en": "Health and Wellness",
            "name_fr": "Santé et mieux-être",
        },
        {
            "id": "Immigration and Migration",
            "name_en": "Immigration and Migration",
            "name_fr": "Immigration et migration",
        },
        {
            "id": "Internal Government Services",
            "name_en": "Internal Government Services",
            "name_fr": "Services gouvernementaux internes",
        },
        {
            "id": "Lands, Forests and Wildlife",
            "name_en": "Lands, Forests and Wildlife",
            "name_fr": "Terres, forêts et faune",
        },
        {
            "id": "Mines and Minerals",
            "name_en": "Mines and Minerals",
            "name_fr": "Mines et minéraux",
        },
        {
            "id": "Municipalities",
            "name_en": "Municipalities",
            "name_fr": "Municipalités",
        },
        {
            "id": "Nature and Environment",
            "name_en": "Nature and Environment",
            "name_fr": "Nature et environnement",
        },
        {
            "id": "Permits and Licensing",
            "name_en": "Permits and Licensing",
            "name_fr": "Permis et licences",
        },
        {
            "id": "Population and Demographics",
            "name_en": "Population and Demographics",
            "name_fr": "Population et démographie",
        },
        {
            "id": "Procurement and Contracts",
            "name_en": "Procurement and Contracts",
            "name_fr": "Approvisionnement et contrats",
        },
        {
            "id": "Public Opinion Research",
            "name_en": "Public Opinion Research",
            "name_fr": "Recherche sur l'opinion publique",
        },
        {
            "id": "Roads, Driving and Transport",
            "name_en": "Roads, Driving and Transport",
            "name_fr": "Routes, conduite et transport",
        },
    ]
    return json.dumps(
        {
            "categories": categories,
            "_meta": {
                "count": len(categories),
                "portal": "data.novascotia.ca",
                "technology": "Socrata SODA",
                "total_datasets": 706,
                "enumerated_date": "2026-06-15",
                "categories_param_warning_en": (
                    "The Socrata API categories= parameter DOES NOT WORK on data.novascotia.ca "
                    "(returns resultSetSize=0 always). Use q= keyword search instead, or "
                    "filter client-side on classification.domain_category. "
                    "See docs://ns/socrata-guide for the workaround."
                ),
                "categories_param_warning_fr": (
                    "Le paramètre categories= de l'API Socrata NE FONCTIONNE PAS sur "
                    "data.novascotia.ca (retourne toujours resultSetSize=0). Utilisez "
                    "plutôt la recherche par mot-clé q=, ou filtrez côté client sur "
                    "classification.domain_category. Consultez docs://ns/socrata-guide."
                ),
                "signature_category_en": (
                    "Nova Scotia's signature category is 'Fishing and Aquaculture' — "
                    "4 curated tools cover marine leases, landbased licenses, hatchery "
                    "stocking, and production/employment data."
                ),
                "signature_category_fr": (
                    "La catégorie signature de la Nouvelle-Écosse est 'Pêche et aquaculture' — "
                    "4 outils curés couvrent les baux marins, les licences terrestres, "
                    "les empoissonnements et les données de production/emploi."
                ),
                "tool_categories_en": "Use ns_list_categories for a live enumeration from the API",
                "tool_categories_fr": "Utilisez ns_list_categories pour une énumération en direct de l'API",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://ns/health-zones",
    mime_type="application/json",
    name="ns_health_zones",
    title="Nova Scotia 4 Health Zones with Member Counties (Western/Northern/Eastern/Central)",
)
async def ns_health_zones() -> str:
    """JSON catalog of Nova Scotia's 4 health zones with their member counties.

    Use to understand the zone= filter values for ns_get_chronic_disease_prevalence and
    ns_get_health_facilities (facility_type='long_term_care' returns a zone field).
    Zone names match the data in Nova Scotia's chronic disease prevalence datasets.
    County membership based on public NS Health Authority documentation.
    See docs://ns/portal-guide for the chronic disease dataset schemas.
    """
    zones = [
        {
            "id": "western",
            "name_en": "Western",
            "name_fr": "Occidentale",
            "zone_filter_en": "Zone 1 - Western",
            "zone_filter_fr": "Zone 1 - Occidentale",
            "counties_en": [
                "Annapolis", "Digby", "Yarmouth", "Shelburne", "Queens", "Lunenburg", "Kings"
            ],
            "counties_fr": [
                "Annapolis", "Digby", "Yarmouth", "Shelburne", "Queens", "Lunenburg", "Kings"
            ],
            "major_communities_en": ["Bridgewater", "Wolfville", "Yarmouth", "Liverpool"],
            "major_communities_fr": ["Bridgewater", "Wolfville", "Yarmouth", "Liverpool"],
            "notes_en": (
                "South-western NS. Kings County contains the Annapolis Valley wine region. "
                "Lunenburg is a UNESCO World Heritage fishing port."
            ),
            "notes_fr": (
                "Sud-ouest de la N.-É. Le comté de Kings contient la région viticole "
                "de la vallée d'Annapolis. Lunenburg est un port de pêche du patrimoine UNESCO."
            ),
        },
        {
            "id": "northern",
            "name_en": "Northern",
            "name_fr": "Nord",
            "zone_filter_en": "Zone 2 - Northern",
            "zone_filter_fr": "Zone 2 - Nord",
            "counties_en": ["Cumberland", "Colchester", "Pictou", "Antigonish"],
            "counties_fr": ["Cumberland", "Colchester", "Pictou", "Antigonish"],
            "major_communities_en": ["Truro", "New Glasgow", "Antigonish", "Amherst"],
            "major_communities_fr": ["Truro", "New Glasgow", "Antigonish", "Amherst"],
            "notes_en": (
                "Northern mainland NS. Truro is the province's geographic centre. "
                "Antigonish hosts StFX University."
            ),
            "notes_fr": (
                "Nord du continent néo-écossais. Truro est le centre géographique de la province. "
                "Antigonish abrite l'Université StFX."
            ),
        },
        {
            "id": "eastern",
            "name_en": "Eastern",
            "name_fr": "Orientale",
            "zone_filter_en": "Zone 3 - Eastern",
            "zone_filter_fr": "Zone 3 - Orientale",
            "counties_en": ["Cape Breton", "Inverness", "Victoria", "Richmond", "Guysborough"],
            "counties_fr": ["Cape Breton", "Inverness", "Victoria", "Richmond", "Guysborough"],
            "major_communities_en": ["Sydney", "Glace Bay", "Port Hawkesbury", "Baddeck"],
            "major_communities_fr": ["Sydney", "Glace Bay", "Port Hawkesbury", "Baddeck"],
            "notes_en": (
                "Cape Breton Island + eastern mainland NS. Inverness County is a major "
                "marine aquaculture area (shellfish leases in the Bras d'Or Lakes)."
            ),
            "notes_fr": (
                "Île du Cap-Breton + est du continent néo-écossais. Le comté d'Inverness "
                "est une zone majeure d'aquaculture marine (baux ostréicoles dans le lac Bras d'Or)."
            ),
        },
        {
            "id": "central",
            "name_en": "Central",
            "name_fr": "Centrale",
            "zone_filter_en": "Zone 4 - Central",
            "zone_filter_fr": "Zone 4 - Centrale",
            "counties_en": ["Halifax", "Hants"],
            "counties_fr": ["Halifax", "Hants"],
            "major_communities_en": ["Halifax", "Dartmouth", "Bedford", "Windsor"],
            "major_communities_fr": ["Halifax", "Dartmouth", "Bedford", "Windsor"],
            "notes_en": (
                "Halifax Regional Municipality (HRM) and Hants County. Halifax is the "
                "provincial capital and most populous health zone (~50% of NS population)."
            ),
            "notes_fr": (
                "Municipalité régionale de Halifax (MRH) et comté de Hants. Halifax est "
                "la capitale provinciale et la zone de santé la plus peuplée (~50% de la pop. NS)."
            ),
        },
    ]
    return json.dumps(
        {
            "zones": zones,
            "_meta": {
                "count": len(zones),
                "description_en": (
                    "Nova Scotia has 4 health zones. Use zone_filter_en as the health_zone= "
                    "parameter in ns_get_chronic_disease_prevalence. LTC facilities returned by "
                    "ns_get_health_facilities(facility_type='long_term_care') include a zone field."
                ),
                "description_fr": (
                    "La Nouvelle-Écosse a 4 zones de santé. Utilisez zone_filter_fr comme "
                    "paramètre health_zone= dans ns_get_chronic_disease_prevalence. Les "
                    "établissements de SLD retournés par ns_get_health_facilities incluent un champ zone."
                ),
                "chronic_disease_tool": "ns_get_chronic_disease_prevalence",
                "facility_tool": "ns_get_health_facilities",
                "vital_stats_tool": "ns_get_vital_statistics",
                "vital_stats_county_note_en": (
                    "For ns_get_vital_statistics, county names must be UPPERCASE and use the "
                    "counties field name (not county). Example: county='ANNAPOLIS', 'CAPE BRETON', "
                    "'GUYSBOROUGH', 'HANTS', 'INVERNESS', 'LUNENBURG', 'RICHMOND', 'VICTORIA'."
                ),
                "vital_stats_county_note_fr": (
                    "Pour ns_get_vital_statistics, les noms de comtés doivent être en MAJUSCULES "
                    "et utiliser le champ counties. Exemple : county='ANNAPOLIS', 'CAPE BRETON'."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://ns/fishing-areas",
    mime_type="application/json",
    name="ns_fishing_areas",
    title="Nova Scotia Aquaculture Fishing Areas — Counties, Species Types, and Lease Reference Data",
)
async def ns_fishing_areas() -> str:
    """JSON reference data for Nova Scotia aquaculture fishing areas and species types.

    Provides the valid speciestyp values and major producing counties for
    ns_get_marine_aquaculture_leases and ns_get_landbased_aquaculture_licenses.
    County names use title case (e.g. 'Inverness', not 'INVERNESS') for aquaculture
    datasets — unlike vital statistics which requires UPPERCASE.
    Source: Nova Scotia Marine Aquaculture Leases dataset (h57h-p9mm) live enumeration.
    """
    species_types = [
        {
            "value": "Shellfish",
            "value_fr": "Mollusques et crustacés",
            "description_en": "Oysters, mussels, clams, scallops — dominant in marine leases",
            "description_fr": "Huîtres, moules, palourdes, pétoncles — dominant dans les baux marins",
            "primary_tool": "ns_get_marine_aquaculture_leases",
            "key_counties": ["Inverness", "Digby", "Lunenburg", "Queens", "Shelburne"],
        },
        {
            "value": "Finfish",
            "value_fr": "Poissons",
            "description_en": "Atlantic Salmon, Rainbow Trout — dominant in landbased licenses",
            "description_fr": "Saumon de l'Atlantique, truite arc-en-ciel — dominant dans les licences terrestres",
            "primary_tool": "ns_get_landbased_aquaculture_licenses",
            "key_counties": ["Colchester", "Hants", "Kings", "Lunenburg", "Pictou"],
        },
        {
            "value": "Marine Plant",
            "value_fr": "Plantes marines",
            "description_en": "Seaweed/kelp leases (smaller number than Shellfish/Finfish)",
            "description_fr": "Baux de varech/goémon (moins nombreux que coquillages/poissons)",
            "primary_tool": "ns_get_marine_aquaculture_leases",
            "key_counties": ["Lunenburg", "Shelburne", "Queens"],
        },
    ]
    hatchery_stocks = [
        {"stock": "Brook Trout", "stock_fr": "Truite mouchetée", "dominant": True},
        {"stock": "Atlantic Salmon", "stock_fr": "Saumon de l'Atlantique", "dominant": False},
        {"stock": "Brown Trout", "stock_fr": "Truite brune", "dominant": False},
        {"stock": "Rainbow Trout", "stock_fr": "Truite arc-en-ciel", "dominant": False},
    ]
    return json.dumps(
        {
            "species_types": species_types,
            "hatchery_stocks": hatchery_stocks,
            "_meta": {
                "count_species_types": len(species_types),
                "count_hatchery_stocks": len(hatchery_stocks),
                "marine_leases_dataset": "h57h-p9mm",
                "landbased_licenses_dataset": "yqwg-f62a",
                "hatchery_stocking_dataset": "8e4a-m6fw",
                "production_dataset": "v2ex-ev63",
                "county_case_note_en": (
                    "Aquaculture dataset county names use TITLE CASE (e.g. 'Inverness', 'Digby'). "
                    "This differs from vital statistics which uses UPPERCASE ('ANNAPOLIS'). "
                    "See data://ns/health-zones for health zone to county mapping."
                ),
                "county_case_note_fr": (
                    "Les noms de comtés dans les jeux de données aquacoles utilisent la CASSE DE TITRE "
                    "(ex. 'Inverness', 'Digby'). Cela diffère des statistiques vitales qui "
                    "utilisent les MAJUSCULES ('ANNAPOLIS')."
                ),
                "geometry_note_en": (
                    "Marine aquaculture leases (h57h-p9mm) have MultiPolygon geometry in the_geom. "
                    "The ns_get_marine_aquaculture_leases tool excludes geometry by default. "
                    "Use ns_query_dataset with $select including the_geom to retrieve boundaries."
                ),
                "geometry_note_fr": (
                    "Les baux d'aquaculture marine (h57h-p9mm) ont une géométrie MultiPolygone "
                    "dans the_geom. L'outil ns_get_marine_aquaculture_leases l'exclut par défaut. "
                    "Utilisez ns_query_dataset avec $select incluant the_geom pour les frontières."
                ),
                "licence_en": "Open Government Licence – Nova Scotia v1.1 (commercial use OK, attribution required)",
                "licence_fr": "Licence du gouvernement ouvert – Nouvelle-Écosse v1.1 (usage commercial autorisé, attribution obligatoire)",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://ns/departments",
    mime_type="application/json",
    name="ns_departments",
    title="Nova Scotia Government Departments Publishing on data.novascotia.ca",
)
async def ns_departments() -> str:
    """JSON catalog of Nova Scotia government departments publishing data on data.novascotia.ca.

    Derived from the domain_metadata Department values observed in catalog results
    across all 706 datasets. Use to understand which departments publish open data
    and which tools correspond to their datasets. Attribution values in ns_search_datasets
    results reflect these department names.
    """
    departments = [
        {
            "name_en": "Fisheries and Aquaculture",
            "name_fr": "Pêches et aquaculture",
            "key_datasets_en": "Marine aquaculture leases, landbased licenses, hatchery stocking, production",
            "key_datasets_fr": "Baux marins, licences terrestres, empoissonnements, production",
            "related_tools": ["ns_get_marine_aquaculture_leases", "ns_get_landbased_aquaculture_licenses", "ns_get_fish_hatchery_stocking", "ns_get_aquaculture_production"],
        },
        {
            "name_en": "Environment and Climate Change",
            "name_fr": "Environnement et changements climatiques",
            "key_datasets_en": "Protected areas system, crown land, surface water quality monitoring",
            "key_datasets_fr": "Système d'aires protégées, terres de la Couronne, surveillance de la qualité de l'eau",
            "related_tools": ["ns_get_protected_areas", "ns_get_water_quality_monitoring"],
        },
        {
            "name_en": "Natural Resources and Renewables",
            "name_fr": "Ressources naturelles et renouvelables",
            "key_datasets_en": "Lands, forests, wildlife, old growth forest policy",
            "key_datasets_fr": "Terres, forêts, faune, politique sur la forêt ancienne",
            "related_tools": ["ns_get_protected_areas"],
        },
        {
            "name_en": "Health and Wellness",
            "name_fr": "Santé et mieux-être",
            "key_datasets_en": "Hospitals, LTC/RCF facilities, boil water advisories, chronic disease prevalence",
            "key_datasets_fr": "Hôpitaux, établissements de SLD, avis d'ébullition, prévalence des maladies chroniques",
            "related_tools": ["ns_get_health_facilities", "ns_get_boil_water_advisories", "ns_get_chronic_disease_prevalence"],
        },
        {
            "name_en": "Finance and Treasury Board",
            "name_fr": "Finances et Conseil du Trésor",
            "key_datasets_en": "Vital statistics, births and deaths by county and year",
            "key_datasets_fr": "Statistiques vitales, naissances et décès par comté et année",
            "related_tools": ["ns_get_vital_statistics"],
        },
        {
            "name_en": "Municipal Affairs and Housing",
            "name_fr": "Affaires municipales et logement",
            "key_datasets_en": "Municipal boundaries, population projections",
            "key_datasets_fr": "Limites municipales, projections de population",
            "related_tools": [],
        },
        {
            "name_en": "Department of Energy and Mines",
            "name_fr": "Ministère de l'Énergie et des Mines",
            "key_datasets_en": "Mineral resources, energy infrastructure",
            "key_datasets_fr": "Ressources minières, infrastructure énergétique",
            "related_tools": [],
        },
        {
            "name_en": "Open Data Nova Scotia (central publisher)",
            "name_fr": "Données ouvertes Nouvelle-Écosse (éditeur central)",
            "key_datasets_en": "Air quality monitoring stations, aggregated provincial data",
            "key_datasets_fr": "Stations de surveillance de la qualité de l'air, données provinciales agrégées",
            "related_tools": ["ns_get_air_quality_stations"],
        },
    ]
    return json.dumps(
        {
            "departments": departments,
            "_meta": {
                "count": len(departments),
                "portal": "data.novascotia.ca",
                "description_en": (
                    "Nova Scotia government departments that publish open data on data.novascotia.ca. "
                    "Attribution values in ns_search_datasets and ns_get_dataset_details results "
                    "reflect these department names. The domain_metadata field in catalog results "
                    "contains Detailed-Metadata_Department key-value pairs."
                ),
                "description_fr": (
                    "Ministères du gouvernement de la Nouvelle-Écosse qui publient des données "
                    "ouvertes sur data.novascotia.ca. Les valeurs d'attribution dans les résultats "
                    "de ns_search_datasets et ns_get_dataset_details reflètent ces noms de ministères."
                ),
                "licence_en": "Open Government Licence – Nova Scotia v1.1",
                "licence_fr": "Licence du gouvernement ouvert – Nouvelle-Écosse v1.1",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Documentation guides (docs://) — markdown with both languages inline
# ---------------------------------------------------------------------------


@resource(
    "docs://ns/socrata-guide",
    mime_type="text/markdown",
    name="ns_socrata_guide",
    title="Nova Scotia Socrata SODA API Guide — SoQL Syntax, Categories Workaround, Geometry Control",
)
async def ns_socrata_guide() -> str:
    """Markdown guide on the Nova Scotia Socrata SODA API (the first Socrata portal in mcp-canada).

    Covers: $where/$select/$order/$group/$limit/$offset SoQL syntax with NS examples;
    the categories= broken-param workaround (use q= or client-side filter instead);
    geometry control via $select (exclude the_geom to prevent bloated responses);
    optional X-App-Token header for higher throttle; catalog vs resource endpoint choice.
    This is the canonical Socrata how-to for all agents using Nova Scotia data.
    """
    return """# Nova Scotia Socrata SODA API Guide

## English

### Portal Overview

`data.novascotia.ca` runs **Socrata** (Tyler Technologies) — the 4th portal technology
in this module suite (alongside CKAN, ArcGIS Hub, and OGC WFS). Nova Scotia's Socrata
catalog contains **706 public datasets** (confirmed 2026-06-15) under the
**Open Government Licence – Nova Scotia v1.1** (free, commercial use allowed, attribution required).

The SODA API is **fully keyless** — no registration required for reads.
An optional `X-App-Token` header raises throttle limits but requires no API surface change.

### Endpoint Architecture

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /api/catalog/v1` | Discover datasets by keyword | `?domains=data.novascotia.ca&q=aquaculture&limit=10` |
| `GET /resource/{4x4-id}.json` | Query rows with SoQL | `?$where=county='Inverness'&$select=license_le,species` |
| `GET /api/views/{4x4-id}.json` | Get dataset schema | `?` (no params needed) |

**Dataset ID format:** 8-char with hyphen: `h57h-p9mm`, `8e4a-m6fw`, `r794-fttm`

### SoQL Parameters (all start with `$`)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `$where` | SQL-like filter clause | `$where=county='Inverness'` |
| `$select` | Field projection (CSV of field names) | `$select=county,species,hectares` |
| `$order` | Sort clause | `$order=stocking_date DESC` |
| `$group` | GROUP BY for aggregations (with COUNT in $select) | `$group=county,speciestyp` |
| `$limit` | Max rows (default 1000, max 50000) | `$limit=100` |
| `$offset` | Pagination skip (omit when 0) | `$offset=100` |
| `$q` | Full-text search within dataset | `$q=salmon` |

### SoQL Examples (NS-Specific)

```
# Marine aquaculture leases — Shellfish in Inverness County
GET /resource/h57h-p9mm.json
  ?$where=speciestyp='Shellfish' AND county='Inverness'
  &$select=license_le,ownership,species,waterbody,county,sitestatus,hectares
  &$order=county ASC
  &$limit=100

# Boil water — active advisories only (removed IS NULL)
GET /resource/7t68-9xmm.json
  ?$where=date_advisory_removed IS NULL

# Vital statistics — Halifax in 2020 (year is TEXT, county is UPPERCASE)
GET /resource/r794-fttm.json
  ?$where=counties='HALIFAX' AND year='2020'

# Aggregation — lease count by county and species type
GET /resource/h57h-p9mm.json
  ?$select=county,speciestyp,count(*) AS count
  &$group=county,speciestyp
  &$order=count DESC
  &$limit=50

# Date filter — water quality readings since 2024-01-01
GET /resource/bkfi-mjgw.json
  ?$where=date > '2024-01-01T00:00:00.000'
  &$order=date DESC
  &$limit=1000
```

### CRITICAL: categories= Parameter is Broken

The Socrata catalog `categories=` parameter **DOES NOT WORK** on data.novascotia.ca:

```
# WRONG — always returns resultSetSize: 0
GET /api/catalog/v1?domains=data.novascotia.ca&categories=Fishing+and+Aquaculture
→ {"results": [], "resultSetSize": 0}
```

**Workaround:** Use `q=` keyword search instead:
```
# CORRECT — full-text search across name/description/tags
GET /api/catalog/v1?domains=data.novascotia.ca&q=aquaculture&limit=10&only=datasets
→ {"results": [...], "resultSetSize": 65}
```

Or use `ns_list_categories` to enumerate categories, then filter client-side on
`classification.domain_category` in the returned results.

The `search_context=` URL format also returns HTTP 404 on this portal.

### Geometry Control via `$select`

Many NS datasets include `the_geom` (GeoJSON geometry) in their default field set.
This can bloat responses significantly (MultiPolygon coordinates = hundreds of KB per row).

**Exclude geometry** by naming only the fields you need:
```
$select=license_le,ownership,species,county,status,hectares
```

**Include geometry** by explicitly adding `the_geom`:
```
$select=pro_name,status,owner,ha_gis,the_geom
```

Datasets with geometry: marine aquaculture leases (`h57h-p9mm`), protected areas
(`ticv-5du5`), hospitals (`tmfr-3h8a`).

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `categories=` filter | Returns 0 results | Use `q=` keyword search instead |
| `year=2020` (integer) | HTTP 400 | Use `year='2020'` (string) — year is a text column in r794-fttm |
| `county='Annapolis'` in vital stats | 0 results | Use `county='ANNAPOLIS'` (UPPERCASE in r794-fttm) |
| `$offset=0` sent explicitly | Noisy requests | Omit `$offset` when 0 (Socrata default is 0) |
| `the_geom` in default `*` select | Huge response | Use explicit `$select` without `the_geom` |
| `date_advisory_removed=''` | May miss records | Use `IS NULL` (Socrata stores removals as proper NULL) |

### Rate Limiting and X-App-Token

Socrata throttles keyless requests at ~1 req/sec per IP. The `ns_` tools use a
conservative `RATE_LIMIT = 2.0` token bucket to avoid throttling.

To get higher limits: set `NS_APP_TOKEN` environment variable with a Socrata app token
(registered at `data.novascotia.ca/signup`). The client will include the
`X-App-Token: {token}` header automatically when the env var is set.

---

## Français

### Aperçu du portail

`data.novascotia.ca` utilise **Socrata** (Tyler Technologies) — la 4e technologie de
portail dans cette suite de modules (avec CKAN, ArcGIS Hub et OGC WFS). Le catalogue
Socrata de la Nouvelle-Écosse contient **706 jeux de données publics** sous la
**Licence du gouvernement ouvert – Nouvelle-Écosse v1.1** (gratuit, usage commercial autorisé).

### Paramètres SoQL (commencent par `$`)

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `$where` | Filtre SQL | `$where=county='Inverness'` |
| `$select` | Projection de champs | `$select=county,species,hectares` |
| `$order` | Tri | `$order=stocking_date DESC` |
| `$group` | GROUP BY (avec COUNT dans $select) | `$group=county,speciestyp` |
| `$limit` | Max enregistrements (défaut 1000, max 50000) | `$limit=100` |
| `$offset` | Pagination (omettre si 0) | `$offset=100` |
| `$q` | Recherche plein texte dans le jeu de données | `$q=salmon` |

### CRITIQUE : Le paramètre categories= est cassé

Le paramètre `categories=` de l'API catalogue Socrata **NE FONCTIONNE PAS** sur
data.novascotia.ca — retourne toujours `resultSetSize: 0`. Utilisez `q=` à la place.

### Contrôle de la géométrie via `$select`

Excluez `the_geom` en ne nommant que les champs nécessaires dans `$select`.
Incluez `the_geom` explicitement dans `$select` pour récupérer les géométries.
"""


@resource(
    "docs://ns/portal-guide",
    mime_type="text/markdown",
    name="ns_portal_guide",
    title="Nova Scotia Open Data Portal Guide — Socrata Tech, Deferred Domains, NS Open Government Licence v1.1",
)
async def ns_portal_guide() -> str:
    """Markdown guide on Nova Scotia's open data portal architecture, deferred domains, and licence.

    Covers: data.novascotia.ca is Socrata (4th portal technology); Socrata-first geospatial;
    transport/511 fully deferred (HTML-only, no clean feed, no NOT_CONFIGURED stubs);
    NS ArcGIS Hub (novagis) deferred (no public no-auth FeatureServers confirmed);
    rockweed (exhe-htib) geometry-only discovery-only; air quality individual pollutant
    series via ns_query_dataset; Open Government Licence – Nova Scotia v1.1 (commercial
    use OK, attribution required).
    """
    return """# Nova Scotia Open Data Portal Guide

## English

### Portal Technology: Socrata (4th Technology in mcp-canada)

`data.novascotia.ca` is a **Socrata** portal (Tyler Technologies), confirmed by the
`X-Socrata-Region` response header. This is the **4th portal technology** in this module suite:

| Technology | Client | Used by | Canonical guide |
|-----------|--------|---------|-----------------|
| CKAN | `shared/http.py` | Federal, Ontario, BC, Quebec, Alberta | `docs://ckan/api-guide` |
| ArcGIS Hub | `shared/arcgis_hub.py` | York Region, Manitoba, Saskatchewan, Alberta | `docs://arcgis/hub-guide` |
| OGC WFS 2.0 | `shared/ogc.py` | British Columbia | `docs://bc/wfs-query-guide` |
| **Socrata SODA** | **`shared/socrata.py`** | **Nova Scotia (+ future portals)** | **`docs://ns/socrata-guide`** |

### Active Tools (17 total)

**Discovery tools (5):** `ns_search_datasets`, `ns_get_dataset_details`, `ns_query_dataset`,
`ns_list_organizations`, `ns_list_categories`

**Aquaculture curated (4):** `ns_get_marine_aquaculture_leases`, `ns_get_landbased_aquaculture_licenses`,
`ns_get_fish_hatchery_stocking`, `ns_get_aquaculture_production`

**Environment/Water curated (3):** `ns_get_water_quality_monitoring`, `ns_get_boil_water_advisories`,
`ns_get_protected_areas`

**Air quality (1):** `ns_get_air_quality_stations`

**Health + demographics (4):** `ns_get_health_facilities`, `ns_get_vital_statistics`,
`ns_get_chronic_disease_prevalence`, (`ns_get_ltc_waitlist` if needed via `ns_query_dataset`)

### Deferred Domains

#### Transport / 511 — HTML-Only, Fully Deferred

NS 511 (`511ns.ca`) is **HTML-only** — no machine-readable API or clean data feed was
found. There are no transport tools in this module and **no NOT_CONFIGURED stubs**.

The province's road condition information is published via a web interface only.
If transport data is needed, use `ns_search_datasets(query='roads transport driving')`
to see if any Socrata datasets cover road conditions — the "Roads, Driving and Transport"
category exists in the catalog.

#### NS ArcGIS Hub (novagis) — Deferred

`novagis.maps.arcgis.com` exists but **no public no-auth FeatureServer endpoints**
were confirmed during research (2026-06-15). Per the Phase 20 locked decision:
Socrata-first geospatial; ArcGIS Hub only if public no-auth FeatureServers confirmed.

**Result:** No ArcGIS Hub tools are implemented in this module. The Socrata catalog
(706 datasets) is rich enough to cover all priority domains without ArcGIS.

#### Rockweed Leases (exhe-htib) — Geometry-Only, Discovery Only

The rockweed leases dataset (`exhe-htib`) exists in the catalog but contains **geometry
only** (the_geom as polygon) with minimal tabular attributes. It is not curated with a
dedicated tool. Use `ns_query_dataset(dataset_id='exhe-htib')` for exploration.

### Air Quality: Station Catalog + Individual Pollutant Datasets Pattern

`ns_get_air_quality_stations` returns the **station catalog** (locations, measurement
types, monitoring periods) from dataset `3bbm-drnh`. Individual pollutant time series
are in **20+ separate per-station datasets**:

- O3 at Lake Major (Musquodoboit)
- PM2.5 at Halifax Dartmouth
- SO2, CO, H2S, NO2 at each station × year

**Pattern for individual readings:**
1. Call `ns_get_air_quality_stations` to get station names and NAPS IDs
2. Call `ns_search_datasets(query='PM2.5 Halifax')` to find the specific pollutant dataset
3. Call `ns_query_dataset(dataset_id='{found_id}', order='date DESC', limit=100)` to read

This is documented in the station catalog tool docstring as well.

### Open Government Licence – Nova Scotia v1.1

All data on `data.novascotia.ca` is published under the
**Open Government Licence – Nova Scotia v1.1**:

- **Permitted:** Reproduction, distribution, adaptation, commercial use, non-commercial use,
  building AI applications and other tools
- **Required:** Attribution statement in the form:
  "Contains information licensed under the Open Government Licence – Nova Scotia"
- **Source:** `support.novascotia.ca/services/open-data-portal-licence`
- **Agent use:** CONFIRMED permitted — building MCP agents is an explicitly allowed use case

### Useful Dataset IDs (for ns_query_dataset direct access)

| Dataset | ID | Notes |
|---------|-----|-------|
| Marine Aquaculture Leases | `h57h-p9mm` | GeoJSON geometry + flat attrs; Shellfish dominant |
| Landbased Aquaculture Licenses | `yqwg-f62a` | Finfish (Atlantic Salmon) dominant |
| Fish Hatchery Stocking | `8e4a-m6fw` | Brook Trout dominant; current to 2025-11 |
| Aquaculture Production | `v2ex-ev63` | Annual by county; year is text field |
| Surface Water Quality | `bkfi-mjgw` | Continuous sensor data through 2024-12 |
| Water Quality Stations | `i9ee-9hct` | Station locations (separate from readings) |
| Boil Water Advisories | `7t68-9xmm` | Active = date_advisory_removed IS NULL |
| Protected Areas System | `ticv-5du5` | GeoJSON MultiPolygon; use $select to control geometry |
| Air Quality Stations | `3bbm-drnh` | Station catalog only; readings in 20+ separate datasets |
| Hospitals | `tmfr-3h8a` | Regional, District, Community types |
| LTC / RCF Facilities | `x76a-axw2` | Zone, beds (nursing_homes_nh_no_of_beds) |
| Vital Statistics | `r794-fttm` | UPPERCASE counties; year as text column |
| AMI Prevalence | `24qf-ntke` | health_zone field (normalized to zone in output) |
| Diabetes Prevalence | `cumi-sw99` | Standard zone, sex, agegroup schema |
| COPD Prevalence | `ua9e-4pss` | Standard schema |
| Hypertension | `sztc-sewr` | hypertension_count, prevalence_rate field names |
| Asthma | `2bih-5dgk` | Standard schema |

---

## Français

### Technologie du portail : Socrata (4e technologie dans mcp-canada)

`data.novascotia.ca` est un portail **Socrata** (Tyler Technologies) — la **4e technologie**
de portail dans cette suite de modules (CKAN, ArcGIS Hub, OGC WFS, Socrata SODA).

### Domaines différés

#### Transport / 511 — HTML seulement, entièrement différé

NS 511 (`511ns.ca`) est **HTML uniquement** — aucune API lisible par machine ni flux de
données propre n'a été trouvé. **Aucun outil de transport** n'est fourni dans ce module
et **aucun stub NOT_CONFIGURED**.

#### GeoHub NS ArcGIS (novagis) — Différé

`novagis.maps.arcgis.com` existe mais **aucun FeatureServer public sans authentification**
n'a été confirmé lors de la recherche. Approche : Socrata en premier; ArcGIS Hub seulement
si des points de terminaison publics sans auth sont confirmés.

### Licence du gouvernement ouvert – Nouvelle-Écosse v1.1

Toutes les données sur `data.novascotia.ca` sont publiées sous la **Licence du gouvernement
ouvert – Nouvelle-Écosse v1.1** :

- **Permis :** Reproduction, distribution, adaptation, usage commercial et non commercial,
  développement d'applications IA et d'outils
- **Obligatoire :** Déclaration d'attribution :
  « Contient des renseignements autorisés en vertu de la Licence du gouvernement ouvert – Nouvelle-Écosse »
- **Source :** `support.novascotia.ca/services/open-data-portal-licence`
"""


# ---------------------------------------------------------------------------
# Templates (template://) — markdown with {placeholder} syntax
# ---------------------------------------------------------------------------


@resource(
    "template://ns/aquaculture-report",
    mime_type="text/markdown",
    name="ns_aquaculture_report_template",
    title="Nova Scotia Aquaculture Sector Analysis Report Template",
)
async def ns_aquaculture_report_template() -> str:
    """Markdown template for reporting Nova Scotia aquaculture sector analysis.

    Fill in {placeholder} fields with actual values from ns_get_marine_aquaculture_leases,
    ns_get_landbased_aquaculture_licenses, ns_get_fish_hatchery_stocking, and
    ns_get_aquaculture_production calls.
    """
    return """# Nova Scotia Aquaculture Sector Analysis — {report_date}

**Data source:** data.novascotia.ca (Socrata SODA API, keyless)
**Licence:** Open Government Licence – Nova Scotia v1.1
**Counties analyzed:** {counties_analyzed}
**Reference year (production):** {production_year}

## Marine Aquaculture Leases

| County | Shellfish Leases | Finfish Leases | Marine Plant Leases | Total Area (ha) |
|--------|-----------------|----------------|---------------------|-----------------|
| {marine_county_1} | {shellfish_count_1} | {finfish_count_1} | {plant_count_1} | {area_ha_1} |
| {marine_county_2} | {shellfish_count_2} | {finfish_count_2} | {plant_count_2} | {area_ha_2} |
| {marine_county_3} | {shellfish_count_3} | {finfish_count_3} | {plant_count_3} | {area_ha_3} |
| **Total** | **{total_shellfish}** | **{total_finfish}** | **{total_plant}** | **{total_area_ha}** |

**Top waterbodies:** {top_waterbodies}
**Active vs Inactive:** {active_count} active / {inactive_count} inactive

## Landbased Aquaculture Licenses

- **Total licenses:** {landbased_total}
- **Finfish (Atlantic Salmon, Rainbow Trout):** {landbased_finfish}
- **Shellfish:** {landbased_shellfish}
- **Key counties:** {landbased_counties}

## Fish Hatchery Stocking (recent 12 months)

| Species | Records | Number Released | Key Hatcheries |
|---------|---------|-----------------|----------------|
| Brook Trout | {bt_records} | {bt_released} | {bt_hatcheries} |
| Atlantic Salmon | {as_records} | {as_released} | {as_hatcheries} |
| Other | {other_records} | {other_released} | {other_hatcheries} |

**Data current to:** {hatchery_data_date}

## Production, Value, and Employment ({production_year})

| County | Production (kg) | Total Value ($) | Full-Time Jobs | Part-Time Jobs | Total Employed |
|--------|----------------|-----------------|----------------|----------------|----------------|
| {prod_county_1} | {kgs_1} | {value_1} | {full_time_1} | {pt_1} | {total_employ_1} |
| {prod_county_2} | {kgs_2} | {value_2} | {full_time_2} | {pt_2} | {total_employ_2} |
| **Provincial Total** | **{total_kgs}** | **{total_value}** | **{total_full_time}** | **{total_pt}** | **{total_province_employ}** |

## Key Findings

1. {finding_1}
2. {finding_2}
3. {finding_3}

## Data Notes

- Marine lease county names use title case (e.g. 'Inverness', 'Digby')
- Production year field is TEXT in the dataset — filtered with year='{production_year}'
- Geometry (MultiPolygon lease boundaries) excluded from this report; use
  `ns_query_dataset(dataset_id='h57h-p9mm', select='...,the_geom')` for spatial analysis

## Next Steps

- [ ] Cross-reference with vital statistics for economic impact per capita
- [ ] Query hatchery stocking by stock for species-specific trends
- [ ] Use `ns_query_dataset` with $group for aggregation by waterbody
- [ ] See `data://ns/fishing-areas` for speciestyp reference values
- [ ] See `docs://ns/socrata-guide` for SoQL aggregation syntax ($group + COUNT)
"""
