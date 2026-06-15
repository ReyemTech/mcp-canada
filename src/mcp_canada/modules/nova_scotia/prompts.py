"""Nova Scotia module prompts — 6 bilingual @prompt functions for the MCP server.

All prompts use standalone @prompt from fastmcp.prompts (NEVER @mcp.prompt).
All prompts include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en".
All prompts use the "ns_" prefix.

Guided workflows (list[Message]) — multi-step tool chaining:
  ns_explore_aquaculture_data  — marine leases + landbased licenses + hatchery stocking + production
  ns_health_zone_analysis      — hospitals + LTC facilities + chronic disease + vital statistics
  ns_water_quality_analysis    — air quality stations + water quality monitoring + boil water advisories

Quick lookups (str) — single-tool instructions:
  ns_quick_find_dataset        — guide ns_search_datasets (q= keyword; categories= workaround)
  ns_quick_protected_areas     — guide ns_get_protected_areas (status filter; geometry via ns_query_dataset)
  ns_quick_vital_stats         — guide ns_get_vital_statistics (county UPPERCASE + year-as-string)
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.prompts import prompt
from fastmcp.prompts.prompt import Message


__all__ = [
    # Guided workflows (list[Message])
    "ns_explore_aquaculture_data",
    "ns_health_zone_analysis",
    "ns_water_quality_analysis",
    # Quick lookups (str)
    "ns_quick_find_dataset",
    "ns_quick_protected_areas",
    "ns_quick_vital_stats",
]


# ---------------------------------------------------------------------------
# Guided workflows — return list[Message] with at least user + assistant roles
# ---------------------------------------------------------------------------


@prompt
async def ns_explore_aquaculture_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Nova Scotia aquaculture data exploration (the province's signature domain).

    Chains ns_get_marine_aquaculture_leases -> ns_get_landbased_aquaculture_licenses ->
    ns_get_fish_hatchery_stocking -> ns_get_aquaculture_production for a comprehensive
    picture of Nova Scotia's fishing and aquaculture sector. All data from
    data.novascotia.ca (Socrata SODA API, keyless, Open Government Licence NS v1.1).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données aquacoles de la Nouvelle-Écosse — "
                "baux marins, licences terrestres, empoissonnements des piscicultures, "
                "et données de production.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données aquacoles de la Nouvelle-Écosse "
                "(domaine signature de la province) en quatre étapes :\n\n"
                "**Étape 1 — Baux d'aquaculture marine :**\n"
                "Appelez `ns_get_marine_aquaculture_leases` (optionnel : `county='Inverness'`, "
                "`species_type='Shellfish'` ou `'Finfish'` ou `'Marine Plant'`). Retourne "
                "license_le, ownership, species, waterbody, county, sitestatus, speciestyp, "
                "hectares, lat_dms, long_dms. La géométrie (MultiPolygon) est exclue — "
                "utilisez `ns_query_dataset` avec le jeu de données `h57h-p9mm` et "
                "`$select=...,the_geom` pour les frontières polygonales. "
                "Les noms de comtés utilisent la casse de titre (ex. `'Inverness'`).\n\n"
                "**Étape 2 — Licences d'aquaculture terrestre :**\n"
                "Appelez `ns_get_landbased_aquaculture_licenses` (optionnel : `county=`, "
                "`species_type='Finfish'`). Le saumon de l'Atlantique (Finfish) domine "
                "ce jeu de données. Retourne license_le, species, county, speciestyp, "
                "ownership, sitestatus, lat_dms, long_dms.\n\n"
                "**Étape 3 — Empoissonnements des piscicultures :**\n"
                "Appelez `ns_get_fish_hatchery_stocking` (optionnel : `stock='Brook Trout'`, "
                "`county=`). Les données sont ordonnées de la plus récente à la plus ancienne "
                "(stocking_date DESC). Données actuelles à novembre 2025. La truite mouchetée "
                "est l'espèce dominante. Valeurs communes de stock : 'Brook Trout', "
                "'Atlantic Salmon', 'Brown Trout', 'Rainbow Trout'.\n\n"
                "**Étape 4 — Production, valeur et emplois en aquaculture :**\n"
                "Appelez `ns_get_aquaculture_production` (optionnel : `year='2022'`, "
                "`county=`). **IMPORTANT :** year est stocké comme texte — utilisez des "
                "chaînes de caractères (ex. `year='2022'`). Retourne year, county, kgs, "
                "total_value, full_time, pt_employ_6_mth, pt_employ_6_mth_1, total_employ. "
                "Données annuelles par comté. TTL 7 jours (données annuelles).\n\n"
                "Conseil : Consultez `data://ns/fishing-areas` pour les valeurs valides "
                "de speciestyp et les comtés producteurs clés. Utilisez "
                "`docs://ns/socrata-guide` pour la syntaxe SoQL complète ($where/$select/"
                "$order/$group).",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Nova Scotia aquaculture data — marine leases, landbased "
            "licenses, fish hatchery stocking records, and production statistics.",
            role="user",
        ),
        Message(
            "I'll guide you through Nova Scotia aquaculture data (the province's signature "
            "domain) in four steps:\n\n"
            "**Step 1 — Marine aquaculture leases:**\n"
            "Call `ns_get_marine_aquaculture_leases` (optional: `county='Inverness'`, "
            "`species_type='Shellfish'` or `'Finfish'` or `'Marine Plant'`). Returns "
            "license_le, ownership, species, waterbody, county, sitestatus, speciestyp, "
            "hectares, lat_dms, long_dms. Geometry (MultiPolygon) is excluded — use "
            "`ns_query_dataset` with dataset `h57h-p9mm` and `$select=...,the_geom` "
            "for polygon boundaries. County names use title case (e.g. `'Inverness'`).\n\n"
            "**Step 2 — Landbased aquaculture licenses:**\n"
            "Call `ns_get_landbased_aquaculture_licenses` (optional: `county=`, "
            "`species_type='Finfish'`). Atlantic Salmon (Finfish) dominates this dataset. "
            "Returns license_le, species, county, speciestyp, ownership, sitestatus, "
            "lat_dms, long_dms.\n\n"
            "**Step 3 — Fish hatchery stocking records:**\n"
            "Call `ns_get_fish_hatchery_stocking` (optional: `stock='Brook Trout'`, "
            "`county=`). Records are ordered newest-first (stocking_date DESC). Data "
            "current to November 2025. Brook Trout is the dominant stocked species. "
            "Common stock values: 'Brook Trout', 'Atlantic Salmon', 'Brown Trout', "
            "'Rainbow Trout'.\n\n"
            "**Step 4 — Aquaculture production, value, and employment:**\n"
            "Call `ns_get_aquaculture_production` (optional: `year='2022'`, `county=`). "
            "**IMPORTANT:** year is stored as text — use string values (e.g. `year='2022'`). "
            "Returns year, county, kgs, total_value, full_time, pt_employ_6_mth, "
            "pt_employ_6_mth_1, total_employ. Annual data by county. 7-day cache TTL.\n\n"
            "Tip: See `data://ns/fishing-areas` for valid speciestyp values and key "
            "producing counties. Use `docs://ns/socrata-guide` for the full SoQL syntax "
            "($where/$select/$order/$group).",
            role="assistant",
        ),
    ]


@prompt
async def ns_health_zone_analysis(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Nova Scotia health zone data exploration.

    Chains ns_get_health_facilities (hospital) -> ns_get_health_facilities (long_term_care)
    -> ns_get_chronic_disease_prevalence -> ns_get_vital_statistics for a comprehensive
    picture of Nova Scotia's health system and demographics. Nova Scotia has 4 health zones:
    Western, Northern, Eastern, Central (see data://ns/health-zones for county mapping).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux analyser les données de santé de la Nouvelle-Écosse par zone — "
                "hôpitaux, établissements de soins de longue durée, prévalence des maladies "
                "chroniques et statistiques vitales.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données de santé de la Nouvelle-Écosse "
                "en quatre étapes. La province est divisée en 4 zones de santé : "
                "Occidentale (Western), Nord (Northern), Orientale (Eastern) et "
                "Centrale (Central).\n\n"
                "**Étape 1 — Hôpitaux par comté :**\n"
                "Appelez `ns_get_health_facilities` avec `facility_type='hospital'` "
                "(optionnel : `county='Halifax'`). Retourne facility_name, address, town, "
                "county, type (Regional/District/Community), x_coordinate, y_coordinate. "
                "TTL 7 jours (emplacements stables).\n\n"
                "**Étape 2 — Établissements de soins de longue durée :**\n"
                "Appelez `ns_get_health_facilities` avec `facility_type='long_term_care'` "
                "(optionnel : `county=`). Retourne facility_name, address, town, county, "
                "zone (Central/Eastern/Northern/Western), beds, x_coordinate, y_coordinate. "
                "Le champ `beds` reflète nursing_homes_nh_no_of_beds. TTL 7 jours.\n\n"
                "**Étape 3 — Prévalence des maladies chroniques par zone :**\n"
                "Appelez `ns_get_chronic_disease_prevalence` avec `disease=` (une parmi : "
                "`'ami'`, `'diabetes'`, `'copd'`, `'hypertension'`, `'asthma'`). Filtrez "
                "avec `health_zone='Zone 1 - Western'`, `sex='F'` ou `'M'`, `year='2020'`. "
                "**Note :** L'IAM (ami) n'a pas de champ sex. Toutes les maladies partagent "
                "le champ normalisé `zone`. TTL 7 jours (données annuelles).\n\n"
                "**Étape 4 — Statistiques vitales (naissances et décès) par comté :**\n"
                "Appelez `ns_get_vital_statistics` (optionnel : `county='ANNAPOLIS'`, "
                "`year='2020'`). **IMPORTANT :** Les noms de comtés sont en MAJUSCULES "
                "(ex. `'ANNAPOLIS'`, `'HALIFAX'`, `'LUNENBURG'`). year est en texte "
                "(ex. `year='2020'`). Retourne counties, year, population, live_births, "
                "birth_rate, deaths, death_rate, natural_increase_rate.\n\n"
                "Conseil : Consultez `data://ns/health-zones` pour la liste complète "
                "des 4 zones avec leurs comtés membres. Utilisez "
                "`template://ns/aquaculture-report` comme modèle de rapport.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to analyze Nova Scotia health data by zone — hospitals, long-term "
            "care facilities, chronic disease prevalence, and vital statistics.",
            role="user",
        ),
        Message(
            "I'll guide you through Nova Scotia health data in four steps. The province "
            "is divided into 4 health zones: Western, Northern, Eastern, and Central.\n\n"
            "**Step 1 — Hospitals by county:**\n"
            "Call `ns_get_health_facilities` with `facility_type='hospital'` "
            "(optional: `county='Halifax'`). Returns facility_name, address, town, county, "
            "type (Regional/District/Community), x_coordinate, y_coordinate. "
            "7-day cache TTL (stable locations).\n\n"
            "**Step 2 — Long-term care facilities:**\n"
            "Call `ns_get_health_facilities` with `facility_type='long_term_care'` "
            "(optional: `county=`). Returns facility_name, address, town, county, "
            "zone (Central/Eastern/Northern/Western), beds, x_coordinate, y_coordinate. "
            "The `beds` field reflects nursing_homes_nh_no_of_beds. 7-day cache TTL.\n\n"
            "**Step 3 — Chronic disease prevalence by health zone:**\n"
            "Call `ns_get_chronic_disease_prevalence` with `disease=` (one of: "
            "`'ami'`, `'diabetes'`, `'copd'`, `'hypertension'`, `'asthma'`). Filter "
            "with `health_zone='Zone 1 - Western'`, `sex='F'` or `'M'`, `year='2020'`. "
            "**Note:** AMI (ami) has no sex field. All diseases surface a normalized "
            "`zone` key. 7-day cache TTL (annual data).\n\n"
            "**Step 4 — Vital statistics (births and deaths) by county:**\n"
            "Call `ns_get_vital_statistics` (optional: `county='ANNAPOLIS'`, "
            "`year='2020'`). **IMPORTANT:** County names are UPPERCASE in this dataset "
            "(e.g. `'ANNAPOLIS'`, `'HALIFAX'`, `'LUNENBURG'`). year is text "
            "(e.g. `year='2020'`). Returns counties, year, population, live_births, "
            "birth_rate, deaths, death_rate, natural_increase_rate.\n\n"
            "Tip: See `data://ns/health-zones` for the complete list of 4 zones with "
            "their member counties. See `docs://ns/portal-guide` for the NS licence.",
            role="assistant",
        ),
    ]


@prompt
async def ns_water_quality_analysis(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Nova Scotia water quality and environmental monitoring data.

    Chains ns_get_air_quality_stations -> ns_get_water_quality_monitoring ->
    ns_get_boil_water_advisories for a comprehensive environmental monitoring picture.
    Includes tips on date-range filtering, active advisory detection, and the
    air-quality station-catalog vs individual pollutant dataset pattern.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux analyser les données de qualité de l'eau et de l'environnement "
                "de la Nouvelle-Écosse — stations de surveillance, lectures continues "
                "de qualité de l'eau et avis d'ébullition.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données environnementales de la "
                "Nouvelle-Écosse en trois étapes :\n\n"
                "**Étape 1 — Stations de surveillance de la qualité de l'air :**\n"
                "Appelez `ns_get_air_quality_stations` (optionnel : `city='Halifax'`). "
                "Retourne le catalogue des stations (noms, coordonnées, types de mesures, "
                "période de surveillance). **Note importante :** Les séries temporelles "
                "individuelles par polluant (O3, PM2.5, SO2, CO par station) se trouvent "
                "dans 20+ jeux de données séparés. Utilisez `ns_query_dataset` avec l'ID "
                "du jeu de données de la station pour lire les lectures de polluants. "
                "Consultez `docs://ns/portal-guide` pour le schéma complet.\n\n"
                "**Étape 2 — Surveillance continue de la qualité de l'eau :**\n"
                "Appelez `ns_get_water_quality_monitoring` (optionnel : "
                "`station_number='NS01EF0002'`, `since='2024-01-01'`, `limit=5000`). "
                "Les résultats sont ordonnés du plus récent au plus ancien. Données "
                "actuelles à décembre 2024. Retourne date, time, temperature_c, ph, "
                "specific_conductance_s_cm, dissolved_oxygen_mg_l, station_number. "
                "Utilisez `ns_query_dataset` avec le jeu de données des stations "
                "(i9ee-9hct) pour les emplacements des stations. TTL 1 heure.\n\n"
                "**Étape 3 — Avis d'ébullition :**\n"
                "Appelez `ns_get_boil_water_advisories` (optionnel : `county=`, "
                "`active_only=True`). Utilisez `active_only=True` pour les avis actuels "
                "(date_advisory_removed IS NULL). **Important :** Une liste vide est une "
                "réponse de SUCCÈS valide — aucun avis actif est l'état normal hors-saison. "
                "Les noms de comtés sont en MAJUSCULES "
                "(ex. `'ANNAPOLIS COUNTY'`, `'INVERNESS COUNTY'`). "
                "Données actuelles à 2025. TTL 15 minutes (données en temps réel).\n\n"
                "Conseil : Filtrez par plage de dates avec `since='YYYY-MM-DD'` pour la "
                "qualité de l'eau. Consultez `docs://ns/socrata-guide` pour les "
                "opérateurs SoQL complets ($where IS NULL, comparaisons de dates ISO 8601).",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to analyze Nova Scotia water quality and environmental monitoring data — "
            "air quality stations, continuous water quality readings, and boil water advisories.",
            role="user",
        ),
        Message(
            "I'll guide you through Nova Scotia environmental monitoring data in three steps:\n\n"
            "**Step 1 — Air quality monitoring stations:**\n"
            "Call `ns_get_air_quality_stations` (optional: `city='Halifax'`). Returns the "
            "station catalog (names, coordinates, measurement types, monitoring period). "
            "**Important note:** Individual pollutant time series (O3, PM2.5, SO2, CO by "
            "station) are in 20+ separate datasets. Use `ns_query_dataset` with the "
            "specific dataset ID from the station record to read pollutant readings. "
            "See `docs://ns/portal-guide` for the full air quality pattern.\n\n"
            "**Step 2 — Continuous surface water quality monitoring:**\n"
            "Call `ns_get_water_quality_monitoring` (optional: `station_number='NS01EF0002'`, "
            "`since='2024-01-01'`, `limit=5000`). Results are ordered newest-first. Data "
            "current through December 2024. Returns date, time, temperature_c, ph, "
            "specific_conductance_s_cm, dissolved_oxygen_mg_l, station_number. Use "
            "`ns_query_dataset` with the stations dataset (i9ee-9hct) for station "
            "locations. 1-hour cache TTL.\n\n"
            "**Step 3 — Boil water advisories:**\n"
            "Call `ns_get_boil_water_advisories` (optional: `county=`, `active_only=True`). "
            "Use `active_only=True` for current advisories (date_advisory_removed IS NULL). "
            "**Important:** An empty list is a VALID success response — no active advisories "
            "is the normal off-season state. County names are UPPERCASE "
            "(e.g. `'ANNAPOLIS COUNTY'`, `'INVERNESS COUNTY'`). Data current to 2025. "
            "15-min cache TTL (live data).\n\n"
            "Tip: Filter by date range with `since='YYYY-MM-DD'` for water quality. "
            "See `docs://ns/socrata-guide` for full SoQL operators ($where IS NULL, "
            "ISO 8601 date comparisons).",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Quick lookups — return str with specific tool + parameter instructions
# ---------------------------------------------------------------------------


@prompt
async def ns_quick_find_dataset(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search Nova Scotia's data.novascotia.ca Socrata catalogue.

    Use for: one-shot NS open data discovery — search the Socrata catalog by keyword,
    inspect dataset schema, and query records via SoQL. Clarifies that categories=
    filtering is broken and must be done client-side. Socrata is the 4th portal
    technology (CKAN / ArcGIS Hub / OGC WFS / Socrata SODA).
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le portail ouvert de la Nouvelle-Écosse "
            "(data.novascotia.ca — Socrata SODA, 706 jeux de données publics) :\n\n"
            "1. Appelez `ns_search_datasets` avec `query='<mot-clé>'` "
            "(ex. `query='aquaculture'`, `query='protected areas'`, `query='vital statistics'`). "
            "**IMPORTANT :** Le paramètre `categories=` de l'API Socrata est **cassé** "
            "sur ce portail (retourne 0 résultats). Utilisez plutôt `q=` pour la "
            "recherche par thème, ou filtrez côté client sur `domain_category`. "
            "Utilisez `ns_list_categories` pour voir toutes les catégories disponibles.\n\n"
            "2. Pour inspecter un jeu de données, appelez `ns_get_dataset_details` avec "
            "`dataset_id='xxxx-xxxx'` (ID à 4x4 tirets). Retourne le schéma complet "
            "(colonnes, types, attribution, licence, date de publication).\n\n"
            "3. Pour récupérer des données, appelez `ns_query_dataset` avec `dataset_id=`, "
            "et les paramètres SoQL optionnels : `where=`, `select=`, `order=`, `limit=`, "
            "`offset=`, `q=`, `group=`. Exemple : "
            "`ns_query_dataset(dataset_id='h57h-p9mm', where=\"speciestyp='Shellfish'\", "
            "select='county,ownership,hectares', order='county ASC', limit=100)`.\n\n"
            "**Conseil :** Excluez la géométrie avec `select=` (sans `the_geom`) pour éviter "
            "les réponses volumineuses. Consultez `docs://ns/socrata-guide` pour la "
            "référence complète de syntaxe SoQL."
        )
    return (
        "To search for data in the Nova Scotia open data portal "
        "(data.novascotia.ca — Socrata SODA API, 706 public datasets):\n\n"
        "1. Call `ns_search_datasets` with `query='<keyword>'` "
        "(e.g. `query='aquaculture'`, `query='protected areas'`, `query='vital statistics'`). "
        "**IMPORTANT:** The Socrata API `categories=` parameter is **broken** on this portal "
        "(returns 0 results always). Use `q=` keyword search for topic filtering instead, "
        "or filter client-side on `domain_category`. Use `ns_list_categories` to discover "
        "all available categories.\n\n"
        "2. To inspect a dataset, call `ns_get_dataset_details` with `dataset_id='xxxx-xxxx'` "
        "(hyphenated 4x4 ID format). Returns full schema (columns, types, attribution, "
        "licence, publication date).\n\n"
        "3. To fetch data records, call `ns_query_dataset` with `dataset_id=` and optional "
        "SoQL params: `where=`, `select=`, `order=`, `limit=`, `offset=`, `q=`, `group=`. "
        "Example: `ns_query_dataset(dataset_id='h57h-p9mm', where=\"speciestyp='Shellfish'\", "
        "select='county,ownership,hectares', order='county ASC', limit=100)`.\n\n"
        "**Tip:** Exclude geometry with `select=` (omit `the_geom`) to avoid bloated responses. "
        "See `docs://ns/socrata-guide` for the full SoQL syntax reference."
    )


@prompt
async def ns_quick_protected_areas(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to query Nova Scotia's protected areas inventory.

    Use for: single-tool protected areas lookup — retrieves the NS Protected Areas
    System dataset (ticv-5du5) with designation status filter. Geometry (MultiPolygon
    boundaries) is excluded by default; ns_query_dataset with $select adds it back.
    """
    if lang == "fr":
        return (
            "Pour interroger les aires protégées de la Nouvelle-Écosse "
            "(source : jeu de données ticv-5du5, Le Système des aires protégées de la "
            "Nouvelle-Écosse, TTL 7 jours) :\n\n"
            "Appelez `ns_get_protected_areas` avec le paramètre optionnel `status=` :\n"
            "- `status='Designated'` — Aires officiellement désignées (la majorité)\n"
            "- `status='Candidate'` — Aires candidates proposées pour désignation\n"
            "- `status='Proposed'` — Aires dans les premières étapes de planification\n"
            "- Aucun filtre — retourne toutes les aires protégées\n\n"
            "Retourne : objectid, pro_name, protect1, symbol, owner, authority, status, "
            "web_url, ha_gis. La **géométrie (MultiPolygon)** est exclue par défaut.\n\n"
            "**Pour inclure les frontières polygonales :**\n"
            "Utilisez `ns_query_dataset(dataset_id='ticv-5du5', select='pro_name,status,"
            "owner,ha_gis,the_geom', where=\"status='Designated'\", limit=100)`. "
            "La géométrie peut être très volumineuse — utilisez toujours `select=` "
            "et `limit=` pour les requêtes avec `the_geom`.\n\n"
            "Conseil : Filtrez par propriétaire avec `ns_query_dataset` et "
            "`where=\"owner='Province of Nova Scotia'\"`. "
            "Consultez `docs://ns/socrata-guide` pour la syntaxe SoQL complète."
        )
    return (
        "To query Nova Scotia's protected areas inventory "
        "(source: dataset ticv-5du5, The Nova Scotia Protected Areas System, 7-day cache TTL):\n\n"
        "Call `ns_get_protected_areas` with the optional `status=` parameter:\n"
        "- `status='Designated'` — Officially designated protected areas (the majority)\n"
        "- `status='Candidate'` — Candidate areas proposed for designation\n"
        "- `status='Proposed'` — Areas in early planning stages\n"
        "- No filter — returns all protected areas\n\n"
        "Returns: objectid, pro_name, protect1, symbol, owner, authority, status, "
        "web_url, ha_gis. **Geometry (MultiPolygon)** is excluded by default to reduce "
        "context size.\n\n"
        "**To include polygon boundaries:**\n"
        "Use `ns_query_dataset(dataset_id='ticv-5du5', select='pro_name,status,owner,"
        "ha_gis,the_geom', where=\"status='Designated'\", limit=100)`. Geometry can be "
        "very large — always use `select=` and `limit=` when including `the_geom`.\n\n"
        "Tip: Filter by owner with `ns_query_dataset` and `where=\"owner='Province of "
        "Nova Scotia'\"`. See `docs://ns/socrata-guide` for full SoQL syntax."
    )


@prompt
async def ns_quick_vital_stats(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to look up Nova Scotia vital statistics by county and year.

    Use for: single-tool vital statistics lookup — births, deaths, rates, natural
    increase by county and year. Clarifies UPPERCASE county names and year-as-string
    requirement (common SoQL pitfalls with the r794-fttm dataset).
    """
    if lang == "fr":
        return (
            "Pour consulter les statistiques vitales de la Nouvelle-Écosse "
            "(naissances, décès, taux, accroissement naturel) — "
            "source : jeu de données r794-fttm, TTL 7 jours :\n\n"
            "Appelez `ns_get_vital_statistics` avec les filtres optionnels :\n"
            "- `county='ANNAPOLIS'` — filtrer par comté "
            "(**MAJUSCULES obligatoires** : 'ANNAPOLIS', 'HALIFAX', 'CAPE BRETON', "
            "'COLCHESTER', 'CUMBERLAND', 'DIGBY', 'GUYSBOROUGH', 'HANTS', "
            "'INVERNESS', 'KINGS', 'LUNENBURG', 'PICTOU', 'QUEENS', 'RICHMOND', "
            "'SHELBURNE', 'VICTORIA', 'YARMOUTH')\n"
            "- `year='2020'` — filtrer par année "
            "(**texte obligatoire** : utilisez `'2020'` pas `2020`)\n\n"
            "Retourne : counties, year, population, live_births, birth_rate, deaths, "
            "death_rate, excess_of_births_over_deaths, natural_increase_rate.\n\n"
            "**Pièges courants :**\n"
            "- `$where=year=2020` → HTTP 400 (year est une colonne texte)\n"
            "- `$where=county='Annapolis'` → 0 résultats (casse titre, non MAJUSCULES)\n\n"
            "Conseil : Omettez les deux filtres pour obtenir toutes les années et "
            "tous les comtés. Combinez `county=` et `year=` pour une cellule spécifique. "
            "Consultez `data://ns/health-zones` pour les comtés regroupés par zone de santé."
        )
    return (
        "To look up Nova Scotia vital statistics (births, deaths, rates, natural increase) "
        "by county and year — source: dataset r794-fttm, 7-day cache TTL:\n\n"
        "Call `ns_get_vital_statistics` with the optional filters:\n"
        "- `county='ANNAPOLIS'` — filter by county "
        "(**UPPERCASE required**: 'ANNAPOLIS', 'HALIFAX', 'CAPE BRETON', 'COLCHESTER', "
        "'CUMBERLAND', 'DIGBY', 'GUYSBOROUGH', 'HANTS', 'INVERNESS', 'KINGS', "
        "'LUNENBURG', 'PICTOU', 'QUEENS', 'RICHMOND', 'SHELBURNE', 'VICTORIA', "
        "'YARMOUTH')\n"
        "- `year='2020'` — filter by year "
        "(**string required**: use `'2020'` not `2020`)\n\n"
        "Returns: counties, year, population, live_births, birth_rate, deaths, "
        "death_rate, excess_of_births_over_deaths, natural_increase_rate.\n\n"
        "**Common pitfalls:**\n"
        "- `$where=year=2020` → HTTP 400 (year is a text column, not integer)\n"
        "- `$where=county='Annapolis'` → 0 results (title case, not UPPERCASE)\n\n"
        "Tip: Omit both filters to get all years and counties. Combine `county=` and "
        "`year=` for a specific cell. See `data://ns/health-zones` for counties grouped "
        "by health zone."
    )
