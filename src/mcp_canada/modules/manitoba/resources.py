"""Manitoba resources — 7 zero-parameter static resources for Manitoba data exploration.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same JSON or markdown body).

Catalog resources (data://):
  data://manitoba/departments    — 6 provincial ministries with bilingual labels + data domains
  data://manitoba/health-regions — 5 RHAs (WRHA, PMH, IERHA, SHSS, NHR) + major hospitals
  data://manitoba/major-rivers   — Red, Assiniboine, Winnipeg, Souris + Red River Floodway

Documentation guides (docs://):
  docs://manitoba/flood-data-guide — ArcGIS Hub layers vs HFC PDFs; HYDAT note; Watch/Warning
  docs://manitoba/portal-guide     — geoportal.gov.mb.ca ArcGIS Hub; MLI deprecation; OpenMB

Templates (template://):
  template://manitoba/dataset-report — dataset exploration report template
  template://manitoba/flood-report   — flood situational report template
"""

import json

from fastmcp.resources import resource


__all__ = [
    "manitoba_departments",
    "manitoba_health_regions",
    "manitoba_major_rivers",
    "manitoba_flood_data_guide",
    "manitoba_portal_guide",
    "manitoba_dataset_report_template",
    "manitoba_flood_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://) — JSON via json.dumps
# ---------------------------------------------------------------------------


@resource(
    "data://manitoba/departments",
    mime_type="application/json",
    name="manitoba_departments",
    title="Manitoba Provincial Departments/Ministries with Bilingual Labels and Data Domains",
)
async def manitoba_departments() -> str:
    """JSON catalog of current Manitoba provincial departments with bilingual names and data domains.

    Use to understand which Manitoba ministry publishes what data on geoportal.gov.mb.ca.
    data_domains describe the key datasets each ministry contributes to the ArcGIS Hub.
    Note: Manitoba's ArcGIS Hub uses publisher display names, not CKAN org slugs.
    Call manitoba_list_organizations for the full list of publishing organizations on the Hub.
    """
    departments = [
        {
            "name_en": "Manitoba Transportation and Infrastructure",
            "name_fr": "Transports et Infrastructure Manitoba",
            "description_en": "Flood forecasting, roads, highways, provincial infrastructure",
            "description_fr": "Prévision des crues, routes, autoroutes, infrastructure provinciale",
            "data_domains": [
                "Flood alerts and waterways",
                "Provincial road network",
                "Winter road conditions",
            ],
        },
        {
            "name_en": "Manitoba Agriculture",
            "name_fr": "Agriculture Manitoba",
            "description_en": "Crop reports, livestock prices, agricultural weather stations, crop reporting regions",
            "description_fr": "Rapports agricoles, prix du bétail, stations météo agricoles, régions de rapport de culture",
            "data_domains": [
                "Livestock prices (cattle/hog)",
                "Agricultural weather stations",
                "Crop reporting regions",
                "Drought monitoring",
            ],
        },
        {
            "name_en": "Manitoba Sustainable Development (Environment and Climate)",
            "name_fr": "Développement durable Manitoba (Environnement et Changements climatiques)",
            "description_en": "Water quality, air quality (via ECCC), provincial parks, wildlife",
            "description_fr": "Qualité de l'eau, qualité de l'air (via ECCC), parcs provinciaux, faune",
            "data_domains": [
                "Provincial parks (93 parks)",
                "Fisheries and waterbody data",
                "Provincial forests",
            ],
        },
        {
            "name_en": "Manitoba Health, Seniors and Long-Term Care",
            "name_fr": "Santé, Aînés et Soins de longue durée Manitoba",
            "description_en": "Regional Health Authorities, wait times, health facilities",
            "description_fr": "Offices régionaux de la santé, temps d'attente, établissements de santé",
            "data_domains": [
                "Surgical and diagnostic wait times",
                "Rural health care facilities",
                "Regional Health Authority boundaries",
            ],
        },
        {
            "name_en": "Manitoba Conservation and Climate",
            "name_fr": "Conservation et Changements climatiques Manitoba",
            "description_en": "Provincial forests, wildlife, biodiversity, protected areas",
            "description_fr": "Forêts provinciales, faune, biodiversité, zones protégées",
            "data_domains": [
                "Provincial forest boundaries",
                "Wildlife management zones",
            ],
        },
        {
            "name_en": "Manitoba Economic Development and Jobs",
            "name_fr": "Développement économique et Emploi Manitoba",
            "description_en": "Labour market, trade statistics, economic development zones",
            "description_fr": "Marché du travail, statistiques commerciales, zones de développement économique",
            "data_domains": [
                "Labour market data",
                "Economic development zones",
            ],
        },
    ]
    return json.dumps(
        {
            "departments": departments,
            "_meta": {
                "count": len(departments),
                "description_en": (
                    "Current Manitoba provincial departments and their key data domains on "
                    "geoportal.gov.mb.ca (ArcGIS Hub, org mMUesHYPkXjaFGfS). "
                    "Call manitoba_list_organizations for the full list of Hub publishers."
                ),
                "description_fr": (
                    "Ministères provinciaux actuels du Manitoba et leurs domaines de données "
                    "sur geoportal.gov.mb.ca (ArcGIS Hub, org mMUesHYPkXjaFGfS). "
                    "Appelez manitoba_list_organizations pour la liste complète des éditeurs Hub."
                ),
                "licence_en": "OpenMB Information and Data Use Licence (similar to CC-BY 4.0)",
                "licence_fr": "Licence OpenMB d'utilisation de l'information et des données (similaire à CC-BY 4.0)",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://manitoba/health-regions",
    mime_type="application/json",
    name="manitoba_health_regions",
    title="Manitoba's 5 Regional Health Authorities (RHAs) with Coverage and Major Hospitals",
)
async def manitoba_health_regions() -> str:
    """JSON list of Manitoba's 5 Regional Health Authorities with coverage and major hospitals.

    Manitoba divides health services into 5 RHAs: WRHA, PMH, IERHA, SHSS, NHR.
    Use short_name values as rha= parameter in manitoba_get_health_facilities.
    Call manitoba_get_surgical_wait_times for procedure wait time averages by year.
    Note: Real-time ER wait times are NOT published in Manitoba — annual data only.
    """
    health_regions = [
        {
            "short_name": "WRHA",
            "name_en": "Winnipeg Regional Health Authority",
            "name_fr": "Office régional de la santé de Winnipeg",
            "coverage_en": "City of Winnipeg, Churchill, East St. Paul, West St. Paul",
            "coverage_fr": "Ville de Winnipeg, Churchill, Est-St-Paul, Ouest-St-Paul",
            "major_hospitals": [
                "Health Sciences Centre",
                "St. Boniface Hospital",
                "Grace Hospital",
                "Victoria Hospital",
            ],
        },
        {
            "short_name": "PMH",
            "name_en": "Prairie Mountain Health",
            "name_fr": "Santé des Prairies et des Montagnes",
            "coverage_en": "Western Manitoba — Brandon and surrounding region",
            "coverage_fr": "Ouest du Manitoba — Brandon et région environnante",
            "major_hospitals": [
                "Brandon Regional Health Centre",
                "Dauphin Regional Health Centre",
                "Minnedosa Health Centre",
            ],
        },
        {
            "short_name": "IERHA",
            "name_en": "Interlake-Eastern Regional Health Authority",
            "name_fr": "Office régional de la santé d'Interlake-Eastern",
            "coverage_en": "Eastern Manitoba and Interlake region — 10 hospitals, 16 PCHs",
            "coverage_fr": "Est du Manitoba et région de l'Interlac — 10 hôpitaux, 16 SLD",
            "major_hospitals": [
                "Selkirk Regional Health Centre",
                "Beausejour District Hospital",
                "Pinawa Hospital",
            ],
        },
        {
            "short_name": "SHSS",
            "name_en": "Southern Health-Santé Sud",
            "name_fr": "Southern Health-Santé Sud",
            "coverage_en": "Southern Manitoba — 17 hospitals (3 with 24/7 ER)",
            "coverage_fr": "Sud du Manitoba — 17 hôpitaux (3 avec urgence 24/7)",
            "major_hospitals": [
                "Boundary Trails Health Centre",
                "Portage District General Hospital",
                "Altona Community Memorial Health Centre",
            ],
        },
        {
            "short_name": "NHR",
            "name_en": "Northern Health Region",
            "name_fr": "Régie régionale de la santé du Nord",
            "coverage_en": "Northern Manitoba — Thompson and remote northern communities",
            "coverage_fr": "Nord du Manitoba — Thompson et collectivités nordiques éloignées",
            "major_hospitals": [
                "Thompson General Hospital",
                "The Pas Health Complex",
                "Flin Flon General Hospital",
            ],
        },
    ]
    return json.dumps(
        {
            "health_regions": health_regions,
            "_meta": {
                "count": len(health_regions),
                "description_en": (
                    "Manitoba's 5 Regional Health Authorities (RHAs). "
                    "Use short_name as rha= filter in manitoba_get_health_facilities. "
                    "Call manitoba_get_surgical_wait_times for annual procedure wait averages."
                ),
                "description_fr": (
                    "Les 5 Offices régionaux de la santé (ORS) du Manitoba. "
                    "Utilisez short_name comme filtre rha= dans manitoba_get_health_facilities. "
                    "Appelez manitoba_get_surgical_wait_times pour les moyennes annuelles d'attente."
                ),
                "er_wait_note_en": "Real-time ER wait times are NOT published by Manitoba — annual data only.",
                "er_wait_note_fr": "Les temps d'attente aux urgences en temps réel ne sont PAS publiés au Manitoba — données annuelles uniquement.",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://manitoba/major-rivers",
    mime_type="application/json",
    name="manitoba_major_rivers",
    title="Manitoba Major River Systems with Flood Risk Levels and Key Cities",
)
async def manitoba_major_rivers() -> str:
    """JSON list of Manitoba's major river systems with flood risk levels and key cities.

    Includes the Red River, Assiniboine River, Winnipeg River, Souris River,
    and the Red River Floodway (bypass diversion). Use with manitoba_get_flood_alerts
    to contextualize alert polygons and manitoba_get_river_stations for monitoring points.
    Flood risk levels are qualitative — call the live tools for authoritative data.
    """
    rivers = [
        {
            "name": "Red River",
            "direction": "Flows north into Lake Winnipeg",
            "key_cities": ["Emerson", "Morris", "Winnipeg"],
            "flood_risk": "Very High",
            "flood_risk_fr": "Très élevé",
            "notes_en": (
                "Major spring flood corridor. Drains US Great Plains; snowmelt-driven. "
                "Protected by Red River Floodway since 1968."
            ),
            "notes_fr": (
                "Principal corridor d'inondation printanière. Draine les Grandes Plaines américaines; "
                "alimenté par la fonte des neiges. Protégé par le détournement de la rivière Rouge depuis 1968."
            ),
        },
        {
            "name": "Assiniboine River",
            "direction": "Flows east, joins Red River at Winnipeg (The Forks)",
            "key_cities": ["Brandon", "Portage la Prairie", "Winnipeg"],
            "flood_risk": "High",
            "flood_risk_fr": "Élevé",
            "notes_en": (
                "2011 near-record flood required Portage Diversion spillway activation. "
                "Drains Saskatchewan prairie agricultural land."
            ),
            "notes_fr": (
                "La crue quasi-record de 2011 a nécessité l'activation du déversoir de détournement de Portage. "
                "Draine les terres agricoles des prairies de la Saskatchewan."
            ),
        },
        {
            "name": "Winnipeg River",
            "direction": "Flows west from Lake of the Woods into Lake Winnipeg",
            "key_cities": ["Kenora (ON)", "Seven Sisters Falls", "Pine Falls"],
            "flood_risk": "Moderate",
            "flood_risk_fr": "Modéré",
            "notes_en": "Regulated by Manitoba Hydro dams; major hydroelectric corridor.",
            "notes_fr": "Régulé par les barrages de Manitoba Hydro ; principal corridor hydroélectrique.",
        },
        {
            "name": "Souris River",
            "direction": "Flows north from North Dakota into the Assiniboine at Wawanesa",
            "key_cities": ["Wawanesa", "Hartney", "Melita"],
            "flood_risk": "Moderate",
            "flood_risk_fr": "Modéré",
            "notes_en": (
                "Trans-boundary river (ND-MB). 2011 significant flooding at Wawanesa. "
                "International Joint Commission governs apportionment."
            ),
            "notes_fr": (
                "Rivière transfrontalière (Dakota du Nord-Manitoba). Inondations importantes à Wawanesa en 2011. "
                "La Commission mixte internationale régit le partage des eaux."
            ),
        },
        {
            "name": "Red River Floodway",
            "direction": "Bypass channel east of Winnipeg; diverts Red River flood flows around city",
            "key_cities": ["Winnipeg"],
            "flood_risk": "Managed",
            "flood_risk_fr": "Contrôlé",
            "notes_en": (
                "33 km earthen channel completed 1968; expanded 2006. Protects ~300,000 Winnipeg residents. "
                "Operated by Manitoba Infrastructure. Use manitoba_get_provincial_waterways(f_type='floodway')."
            ),
            "notes_fr": (
                "Canal de 33 km complété en 1968 ; élargi en 2006. Protège ~300 000 résidents de Winnipeg. "
                "Exploité par Infrastructure Manitoba. Utilisez manitoba_get_provincial_waterways(f_type='floodway')."
            ),
        },
        {
            "name": "Lake Manitoba",
            "direction": "Central drainage basin; receives inflows from Assiniboine via Portage Diversion",
            "key_cities": ["Ebb and Flow", "St. Laurent", "Lundar"],
            "flood_risk": "High",
            "flood_risk_fr": "Élevé",
            "notes_en": (
                "2011 unprecedented flooding; Portage Diversion overflow forced record lake levels. "
                "Lake drains north via Fairford River to Lake Winnipeg."
            ),
            "notes_fr": (
                "Inondations sans précédent en 2011 ; le débordement du détournement de Portage a forcé "
                "des niveaux record du lac. Le lac se déverse au nord via la rivière Fairford dans le lac Winnipeg."
            ),
        },
    ]
    return json.dumps(
        {
            "rivers": rivers,
            "_meta": {
                "count": len(rivers),
                "description_en": (
                    "Manitoba's major river systems and flood risk context. "
                    "Use with manitoba_get_flood_alerts for active alert polygons and "
                    "manitoba_get_river_stations for hydrometric monitoring points. "
                    "Flood risk levels are qualitative reference data — not real-time."
                ),
                "description_fr": (
                    "Principaux systèmes fluviaux du Manitoba et contexte de risque d'inondation. "
                    "Utilisez avec manitoba_get_flood_alerts pour les polygones d'alerte actifs et "
                    "manitoba_get_river_stations pour les points de surveillance hydrométrique. "
                    "Les niveaux de risque sont des données de référence qualitatives — pas en temps réel."
                ),
                "hydat_note_en": (
                    "Actual water level readings are in ECCC's HYDAT database (wateroffice.ec.gc.ca), "
                    "not on Manitoba's ArcGIS Hub. manitoba_get_river_stations returns station locations "
                    "and alert status flags, not numeric level measurements."
                ),
                "hydat_note_fr": (
                    "Les lectures réelles du niveau d'eau sont dans la base de données HYDAT d'ECCC "
                    "(wateroffice.ec.gc.ca), pas sur l'ArcGIS Hub du Manitoba. "
                    "manitoba_get_river_stations retourne les emplacements des stations "
                    "et les indicateurs de statut d'alerte, pas les mesures numériques de niveau."
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
    "docs://manitoba/flood-data-guide",
    mime_type="text/markdown",
    name="manitoba_flood_data_guide",
    title="Manitoba Flood Data Guide — ArcGIS Hub Layers vs HFC PDFs, River Levels, HYDAT",
)
async def manitoba_flood_data_guide() -> str:
    """Markdown guide explaining Manitoba flood data sources and tool mapping.

    Covers: flood-outlook vs river-level vs forecast distinctions; ArcGIS Hub layers
    vs HFC PDF bulletins; HYDAT note for actual level readings; Watch vs Warning types.
    """
    return """# Manitoba Flood Data Guide / Guide des données d'inondation du Manitoba

## English

### Source-of-Truth Matrix

| Use Case | Tool | Source |
|----------|------|--------|
| Active flood watch/warning areas | `manitoba_get_flood_alerts` | ArcGIS Hub `Overland_Flood_Alerts` FeatureServer (5-min TTL) |
| River monitoring station locations + alert status | `manitoba_get_river_stations` | Manitoba River Conditions CSV (5-min TTL) |
| Water control infrastructure (dikes, floodways, dams) | `manitoba_get_provincial_waterways` | ArcGIS Hub `Provincial_Waterways` FeatureServer (24h TTL) |
| Provincial parks near flood zones | `manitoba_get_provincial_parks` | ArcGIS Hub `Manitoba_Parks` FeatureServer (24h TTL) |
| Historical flood archive (dataset search) | `manitoba_search_datasets(q='flood')` | geoportal.gov.mb.ca ArcGIS Hub search |

### What Is NOT Machine-Readable

The **Manitoba Hydrologic Forecast Centre (HFC)** publishes flood outlooks, flood bulletins,
and daily flood sheets as **PDF and HTML documents only**. There is no JSON/CSV download
and no ArcGIS integration for HFC bulletins. Do NOT attempt to fetch:

- `gov.mb.ca/mit/floodinfo/` (HTML pages with daily flood sheets)
- HFC PDF spring flood outlooks (February/March publications)

The ArcGIS Hub layers above (`Overland_Flood_Alerts`, `Provincial_Waterways`) are the
authoritative machine-readable flood data sources.

### Actual Water Levels: ECCC HYDAT

River station locations and alert flags are available via `manitoba_get_river_stations`.
However, **actual numeric water level and flow readings** are stored in ECCC's HYDAT
database (`wateroffice.ec.gc.ca`), not on Manitoba's ArcGIS Hub. HYDAT is a separate
federal database — use the MSC GeoMet module (Phase 4 weather module) or the ECCC
Water Office website for live hydrometric readings.

### Alert Type Reference

| Type (EN) | Type (FR) | Meaning |
|-----------|-----------|---------|
| Flood Warning | Avertissement d'inondation | Flooding is occurring or imminent — act now |
| Flood Watch | Surveillance des crues | Conditions favourable for flooding — prepare |
| High Water Advisory | Avis Hautes Eaux | Elevated water levels, moderate risk |
| Overland Flood Advisory | Avis d'inondation de surface | Surface water flooding risk |

### Flood Season Context

- **Typical Red River spring flood:** March to May
- **Highest risk rivers:** Red River (Very High), Assiniboine River (High), Lake Manitoba (High)
- **Red River Floodway:** Completed 1968, expanded 2006. 33 km bypass channel protects Winnipeg.
  Query via `manitoba_get_provincial_waterways(f_type='floodway')`.
- **Portage Diversion:** Controls Assiniboine overflow into Lake Manitoba.
  Both are in the `Provincial_Waterways` FeatureServer.

---

## Français

### Matrice source de vérité

| Cas d'usage | Outil | Source |
|-------------|-------|--------|
| Zones de surveillance/avertissement actives | `manitoba_get_flood_alerts` | ArcGIS Hub `Overland_Flood_Alerts` FeatureServer (TTL 5 min) |
| Emplacements stations + statut d'alerte | `manitoba_get_river_stations` | CSV Conditions des rivières Manitoba (TTL 5 min) |
| Infrastructure (digues, détournements, barrages) | `manitoba_get_provincial_waterways` | ArcGIS Hub `Provincial_Waterways` FeatureServer (TTL 24 h) |
| Archive historique inondations | `manitoba_search_datasets(q='flood')` | Recherche ArcGIS Hub geoportal.gov.mb.ca |

### Ce qui N'est PAS lisible par machine

Le **Centre de prévision hydrologique (HFC)** du Manitoba publie ses perspectives d'inondation,
bulletins et fiches quotidiennes uniquement en **PDF et HTML**. Aucun téléchargement JSON/CSV
ni intégration ArcGIS. N'essayez PAS d'interroger :

- `gov.mb.ca/mit/floodinfo/` (pages HTML avec fiches quotidiennes)
- PDF de perspectives d'inondation printanière HFC (publications fév./mars)

Les couches ArcGIS Hub ci-dessus sont les sources de données d'inondation lisibles par machine
faisant autorité.

### Niveaux réels d'eau : HYDAT d'ECCC

Les emplacements des stations et les indicateurs d'alerte sont disponibles via
`manitoba_get_river_stations`. Cependant, les **lectures numériques réelles** de niveau d'eau
et de débit sont stockées dans la base de données HYDAT d'ECCC (`wateroffice.ec.gc.ca`),
pas sur l'ArcGIS Hub du Manitoba. Utilisez le module MSC GeoMet (module météo Phase 4)
ou le site Bureau de l'eau d'ECCC pour les lectures hydrométriques en direct.

### Référence des types d'alerte

| Type (FR) | Signification |
|-----------|---------------|
| Avertissement d'inondation | Inondation en cours ou imminente — agissez maintenant |
| Surveillance des crues | Conditions propices aux inondations — préparez-vous |
| Avis Hautes Eaux | Niveaux d'eau élevés, risque modéré |
| Avis d'inondation de surface | Risque d'inondation de surface |
"""


@resource(
    "docs://manitoba/portal-guide",
    mime_type="text/markdown",
    name="manitoba_portal_guide",
    title="Manitoba Open Data Portal Guide — geoportal.gov.mb.ca ArcGIS Hub, MLI Retirement, OpenMB",
)
async def manitoba_portal_guide() -> str:
    """Markdown guide on Manitoba's open data portals, ArcGIS Hub structure, and OpenMB licence.

    Covers: geoportal.gov.mb.ca ArcGIS Hub structure, which tool to use per data type,
    data.manitoba.ca status, MLI retirement (2022), and OpenMB licence permissions.
    """
    return """# Manitoba Open Data Portal Guide / Guide du portail de données ouvertes du Manitoba

## English

### Primary Portal: geoportal.gov.mb.ca (ArcGIS Hub)

Manitoba's primary machine-readable open data portal is **geoportal.gov.mb.ca** —
an ArcGIS Hub instance powered by the ArcGIS Online organization `mMUesHYPkXjaFGfS`.

| Property | Value |
|----------|-------|
| Portal URL | `https://geoportal.gov.mb.ca` |
| ArcGIS Org ID | `mMUesHYPkXjaFGfS` |
| Base Services URL | `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/` |
| Licence | OpenMB Information and Data Use Licence |
| Authentication | None (public) |
| Dataset count | 93+ FeatureServer services |

### Which Tool to Use

| Data Need | Tool |
|-----------|------|
| Search datasets by keyword | `manitoba_search_datasets` |
| Inspect a specific dataset | `manitoba_get_dataset_details` |
| Query a FeatureServer or file resource | `manitoba_query_dataset` |
| List publishing organizations | `manitoba_list_organizations` |
| List available categories/themes | `manitoba_list_categories` |
| Flood alert polygons (live) | `manitoba_get_flood_alerts` |
| Provincial parks (93 parks) | `manitoba_get_provincial_parks` |
| Drought monitor (D0-D4) | `manitoba_get_drought_status` |
| Livestock prices (weekly) | `manitoba_get_livestock_prices` |
| Surgical wait times (annual) | `manitoba_get_surgical_wait_times` |

### data.manitoba.ca Status

The `data.manitoba.ca` domain does **not** resolve to a live CKAN API. Manitoba's
machine-readable data is on `geoportal.gov.mb.ca` (ArcGIS Hub), not a CKAN endpoint.
Do NOT call `data.manitoba.ca/api/3/action/` — these calls will time out.

### Manitoba Land Initiative (MLI) — RETIRED

`mli.gov.mb.ca` received its last updates on **February 9, 2022**. MLI (Manitoba Land
Initiative) has been officially retired and superseded by `geoportal.gov.mb.ca`.
Do NOT call `mli.gov.mb.ca` — it no longer receives data updates.

All MLI content has migrated to the geoportal. Use `manitoba_search_datasets` to find
datasets previously hosted on MLI.

### OpenMB Information and Data Use Licence

Manitoba's open data is released under the **OpenMB Information and Data Use Licence**:

- **Permitted:** Commercial use, non-commercial use, reproduction, adaptation, distribution
- **Required:** Attribution — standard attribution statement required
- **Compatibility:** Similar to CC-BY 4.0; compatible with other Canadian OGL variants
- **Agent use:** CONFIRMED permitted — building agents and AI applications is explicitly
  an allowed use case under the OpenMB licence
- **Licence PDF:** `https://www.gov.mb.ca/asset_library/en/legal/OpenMB-Information-Data-Use-Licence.pdf`

---

## Français

### Portail principal : geoportal.gov.mb.ca (ArcGIS Hub)

Le portail de données ouvertes lisibles par machine du Manitoba est **geoportal.gov.mb.ca** —
une instance ArcGIS Hub alimentée par l'organisation ArcGIS Online `mMUesHYPkXjaFGfS`.

| Propriété | Valeur |
|-----------|--------|
| URL du portail | `https://geoportal.gov.mb.ca` |
| ID org ArcGIS | `mMUesHYPkXjaFGfS` |
| URL base des services | `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/` |
| Licence | Licence OpenMB d'utilisation de l'information et des données |
| Authentification | Aucune (public) |
| Nombre de jeux de données | 93+ services FeatureServer |

### Statut de data.manitoba.ca

Le domaine `data.manitoba.ca` ne résout PAS vers une API CKAN active. Les données lisibles
par machine du Manitoba sont sur `geoportal.gov.mb.ca` (ArcGIS Hub), pas sur un point
de terminaison CKAN. N'appelez PAS `data.manitoba.ca/api/3/action/` — ces appels expirent.

### Initiative des terres du Manitoba (ITM) — RETIRÉE

`mli.gov.mb.ca` a reçu ses dernières mises à jour le **9 février 2022**. L'ITM (Initiative
des terres du Manitoba) a été officiellement retirée et remplacée par `geoportal.gov.mb.ca`.
N'appelez PAS `mli.gov.mb.ca` — il ne reçoit plus de mises à jour de données.

### Licence OpenMB

Les données ouvertes du Manitoba sont publiées sous la **Licence OpenMB d'utilisation de
l'information et des données** :

- **Permis :** Usage commercial, non commercial, reproduction, adaptation, distribution
- **Obligatoire :** Attribution — déclaration d'attribution standard requise
- **Compatibilité :** Similaire à CC-BY 4.0 ; compatible avec les variantes canadiennes de la LGO
- **Usage agent :** CONFIRMÉ permis — la construction d'agents et d'applications IA est
  explicitement un cas d'usage autorisé sous la licence OpenMB
"""


# ---------------------------------------------------------------------------
# Templates (template://) — markdown with {placeholder} syntax
# ---------------------------------------------------------------------------


@resource(
    "template://manitoba/dataset-report",
    mime_type="text/markdown",
    name="manitoba_dataset_report_template",
    title="Manitoba Dataset Exploration Report Template",
)
async def manitoba_dataset_report_template() -> str:
    """Markdown template for reporting Manitoba geoportal dataset exploration findings.

    Fill in placeholders with actual values from manitoba_search_datasets,
    manitoba_get_dataset_details, and manitoba_query_dataset calls.
    """
    return """# Manitoba Dataset Exploration Report

**Date:** {report_date}
**Dataset searched:** {search_query}
**Category filter:** {category_filter}
**Portal:** geoportal.gov.mb.ca (ArcGIS Hub, org mMUesHYPkXjaFGfS)

## Search Results Summary

- **Total datasets found:** {total_count}
- **Results returned:** {results_count}
- **Data types found:** {data_types}

## Dataset Spotlight

**Dataset ID (GUID):** {dataset_id}
**Title:** {dataset_title}
**Publisher:** {publisher_name}
**License:** OpenMB Information and Data Use Licence
**Last modified:** {last_modified}
**Number of resources:** {num_resources}

### Best Resource

- **Type:** {resource_type}
- **URL:** {resource_url}
- **Routing path:** {routing_path}

## Sample Data (first {sample_count} records)

{sample_data_table}

## Notes

- **Portal:** geoportal.gov.mb.ca uses ArcGIS Hub Search API (NOT CKAN API)
- **Authentication:** None required — public access
- **Licence:** OpenMB — commercial and non-commercial use permitted with attribution
- **MLI note:** mli.gov.mb.ca is retired (2022-02-09) — all data migrated to geoportal
- **Auto-router:** `manitoba_query_dataset` prefers FeatureServer over file resources

## Next Steps

- [ ] Refine with `manitoba_search_datasets(q='{related_keyword}')`
- [ ] Check dataset details via `manitoba_get_dataset_details(id='{dataset_id}')`
- [ ] Filter by category: `category='{category_filter}'`
- [ ] See `data://manitoba/departments` for ministry data domains
"""


@resource(
    "template://manitoba/flood-report",
    mime_type="text/markdown",
    name="manitoba_flood_report_template",
    title="Manitoba Flood Situational Report Template",
)
async def manitoba_flood_report_template() -> str:
    """Markdown template for reporting Manitoba flood situational awareness.

    Fill in placeholders with actual values from manitoba_get_flood_alerts,
    manitoba_get_river_stations, and manitoba_get_provincial_waterways calls.
    """
    return """# Manitoba Flood Situational Report — {report_date}

**Data source:** Manitoba ArcGIS Hub (geoportal.gov.mb.ca) FeatureServers
**Cache TTL:** 5 minutes (flood alerts and river stations)

## Flood Alert Summary

- **Active flood alerts:** {alert_count}
- **Flood Warnings (highest severity):** {warning_count}
- **Flood Watches:** {watch_count}
- **High Water Advisories:** {advisory_count}

## Active Alert Areas

| Alert Type | Start Date | End Date | Area (sq km) |
|------------|------------|----------|--------------|
| {alert_type_1} | {start_date_1} | {end_date_1} | {area_1} |
| {alert_type_2} | {start_date_2} | {end_date_2} | {area_2} |

## River Station Status

- **Total monitoring stations:** {station_count}
- **Flood Warning stations:** {fw_station_count}
- **Flood Watch stations:** {fwch_station_count}
- **High Water Advisory stations:** {hwa_station_count}
- **Normal stations:** {normal_station_count}

## Key River Risk Status

| River | Flood Risk | Current Status |
|-------|-----------|----------------|
| Red River | Very High | {red_river_status} |
| Assiniboine River | High | {assiniboine_status} |
| Lake Manitoba | High | {lake_manitoba_status} |
| Souris River | Moderate | {souris_status} |

## Water Control Infrastructure

- **Red River Floodway operational:** {floodway_operational}
- **Portage Diversion status:** {portage_diversion_status}
- **Total dikes in database:** {dike_count}

## Notes

- **Alert types:** `Flood Warning` (act now) > `Flood Watch` (prepare) > `High Water Advisory`
- **Empty alerts** (`{alert_count}` = 0) is normal off-season — no active alerts
- **Actual water levels:** Available in ECCC HYDAT database (`wateroffice.ec.gc.ca`),
  not on Manitoba ArcGIS Hub
- **HFC bulletins:** PDF-only — not machine-readable; see `docs://manitoba/flood-data-guide`
- **Floodway reference:** `data://manitoba/major-rivers` for risk levels per river system

## Data Freshness

- **Flood alerts queried:** {alerts_query_ts}
- **River stations queried:** {stations_query_ts}
"""
