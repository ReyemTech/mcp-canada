"""Alberta prompts — 6 bilingual prompts (3 guided + 3 quick lookups).

Guided workflows (list[Message]) — multi-step tool chaining:
  alberta_explore_energy            — AER ST1/ST3/ST39 well/pipeline/production workflow
  alberta_explore_wildfires         — active fires + perimeters + bans + control orders workflow
  alberta_explore_health_or_transport — hospitals/EMS/AHS zones OR 511 events / winter roads / cameras

Quick lookups (str) — single-tool instructions:
  alberta_quick_dataset_search      — open.alberta.ca CKAN catalogue search
  alberta_check_road_conditions     — 511 Alberta winter road conditions
  alberta_active_fires_now          — WMBappServices Active_Wildfires_Dashboard_view lookup

IMPORTANT: All prompts accept `lang: Literal["en", "fr"] = "en"` via Annotated.
ZERO-parameter resources are in resources.py — see CLAUDE.md rule.
"""

from typing import Annotated, Literal

from fastmcp.prompts import prompt
from fastmcp.prompts.prompt import Message


__all__ = [
    # Guided workflows (list[Message])
    "alberta_explore_energy",
    "alberta_explore_wildfires",
    "alberta_explore_health_or_transport",
    # Quick lookups (str)
    "alberta_quick_dataset_search",
    "alberta_check_road_conditions",
    "alberta_active_fires_now",
]


# ---------------------------------------------------------------------------
# Guided workflows — return list[Message] with at least user + assistant roles
# ---------------------------------------------------------------------------


@prompt
async def alberta_explore_energy(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta energy data exploration — AER wells, pipelines, production.

    Chains alberta_get_well_licences_today -> alberta_get_production_volumes ->
    alberta_get_pipeline_statistics -> alberta_get_well_licences_archive for a
    comprehensive AER energy sector overview via static XLSX/TXT reports.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données énergétiques de l'Alberta — "
                "pétrole, gaz, pipelines, et puits de l'Alberta Energy Regulator (AER).",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les rapports statiques de l'AER en quatre étapes :\n\n"
                "**Étape 1 — Licences de puits du jour (ST1) :**\n"
                "Appelez `alberta_get_well_licences_today` pour obtenir la liste des licences "
                "de puits émises aujourd'hui (TXT mis à jour quotidiennement, "
                "rotation MON/TUE/WED/THU/FRI/SAT/SUN). Retourne numéro de licence, "
                "opérateur, nom du puits, code de champ.\n\n"
                "**Étape 2 — Volumes de production mensuels (ST3) :**\n"
                "Appelez `alberta_get_production_volumes(product='Oil')` "
                "(ou `'Gas'`, `'Butane'`, `'Ethane'`, `'NGL'`, `'Propane'`, `'Sulphur'`) "
                "pour les données de production mensuelles par produit. "
                "Attention : la casse du slug est sensible ('Oil' ✓, 'oil' ✗).\n\n"
                "**Étape 3 — Statistiques annuelles des pipelines (ST39) :**\n"
                "Appelez `alberta_get_pipeline_statistics(year=2024)` pour les "
                "statistiques de longueur, substance, et opérateur par année. "
                "Données disponibles pour 2018+ (XLSX).\n\n"
                "**Étape 4 — Archives historiques de licences de puits :**\n"
                "Appelez `alberta_get_well_licences_archive(year=2024, month=3)` "
                "pour obtenir l'URL du ZIP mensuel (dwll{YYYY}-{MM}.zip) à télécharger "
                "en externe. Les archives annuelles remontent à 1980.\n\n"
                "Note : Les données d'incidents/déversements (ST57) sont publiées en PDF "
                "seulement depuis 2014 — non exposées en JSON/CSV. L'API OneStop de l'AER "
                "(puits actifs en temps réel) nécessite une authentification — non disponible."
            ,
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Alberta energy data — oil, gas, pipelines, and wells "
            "from the Alberta Energy Regulator (AER).",
            role="user",
        ),
        Message(
            "I'll guide you through the AER static reports in four steps:\n\n"
            "**Step 1 — Today's well licences (ST1):**\n"
            "Call `alberta_get_well_licences_today` for the list of well licences "
            "issued today (TXT overwritten daily, rotates MON/TUE/WED/THU/FRI/SAT/SUN). "
            "Returns licence number, operator, well name, and field code.\n\n"
            "**Step 2 — Monthly production volumes (ST3):**\n"
            "Call `alberta_get_production_volumes(product='Oil')` "
            "(or `'Gas'`, `'Butane'`, `'Ethane'`, `'NGL'`, `'Propane'`, `'Sulphur'`) "
            "for monthly production by product. "
            "Note: slug casing is enforced ('Oil' ✓, 'oil' ✗ — returns INVALID_INPUT).\n\n"
            "**Step 3 — Annual pipeline statistics (ST39):**\n"
            "Call `alberta_get_pipeline_statistics(year=2024)` for length, substance, "
            "and operator statistics by year. XLSX data available for 2018+.\n\n"
            "**Step 4 — Historical well licence archives:**\n"
            "Call `alberta_get_well_licences_archive(year=2024, month=3)` to get the "
            "URL of the monthly ZIP archive (dwll{YYYY}-{MM}.zip) for external download. "
            "Annual archives go back to 1980.\n\n"
            "Tip: Incident/spill data (ST57) has been PDF-only since 2014 — not exposed "
            "as JSON/CSV. AER's OneStop API (real-time active wells) requires "
            "authentication and is not available via MCP.",
            role="assistant",
        ),
    ]


@prompt
async def alberta_explore_wildfires(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta wildfire situational awareness — active fires, perimeters, bans.

    Chains alberta_get_active_fires -> alberta_get_fire_perimeters ->
    alberta_get_fire_bans -> alberta_get_fire_control_orders for a comprehensive
    wildfire emergency context from WMBappServices ArcGIS Online.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre la situation actuelle des feux de forêt en Alberta — "
                "feux actifs, périmètres, interdictions de feux, ordres de contrôle.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données WMBappServices de Wildfire "
                "Management Branch en quatre étapes :\n\n"
                "**Étape 1 — Feux actifs en temps réel :**\n"
                "Appelez `alberta_get_active_fires` (TTL 5 min). "
                "Filtrez par `status='Out of Control'`, `'Being Held'`, ou `'Under Control'` "
                "pour prioriser les feux les plus dangereux. Retourne `fire_number`, "
                "`area_estimate`, `general_cause`, `resp_area` (forest area responsable).\n\n"
                "**Étape 2 — Périmètres de feux (polygones) :**\n"
                "Appelez `alberta_get_fire_perimeters(status='active')` pour les périmètres "
                "en cours, `status='extinguished'` pour les archives historiques. "
                "Utilisez `include_geometry=True` pour obtenir les polygones GeoJSON.\n\n"
                "**Étape 3 — Interdictions de feux :**\n"
                "Appelez `alberta_get_fire_bans` pour les zones avec restrictions "
                "(interdictions totales, avis d'incendie, restrictions OHV). "
                "Consultez `data://alberta/forest-areas` pour les 10 codes de zone forestière.\n\n"
                "**Étape 4 — Ordres de contrôle de feux / restrictions OHV / zones forestières :**\n"
                "Appelez `alberta_get_fire_control_orders(category='fire_control')` "
                "(ou `'ohv_restriction'`, `'forest_area'`) — un outil unifié trois catégories "
                "via FeatureServers WMBappServices distincts.\n\n"
                "Pour l'archive historique (2006-2025), appelez "
                "`alberta_query_dataset(dataset_id='wildfire-data')` — CSV 10MB sur CKAN. "
                "Consultez `docs://alberta/wildfire-data-guide` pour la cartographie "
                "sources/outils et les codes de statut."
            ,
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to understand the current wildfire situation in Alberta — "
            "active fires, perimeters, fire bans, and control orders.",
            role="user",
        ),
        Message(
            "I'll guide you through WMBappServices (Wildfire Management Branch) data "
            "in four steps:\n\n"
            "**Step 1 — Real-time active fires:**\n"
            "Call `alberta_get_active_fires` (5-min cache TTL). "
            "Filter by `status='Out of Control'`, `'Being Held'`, or `'Under Control'` "
            "to prioritise the most dangerous fires. Returns `fire_number`, "
            "`area_estimate`, `general_cause`, and `resp_area` (responsible forest area).\n\n"
            "**Step 2 — Fire perimeters (polygons):**\n"
            "Call `alberta_get_fire_perimeters(status='active')` for in-progress perimeters, "
            "`status='extinguished'` for historical archives. "
            "Use `include_geometry=True` to get GeoJSON polygons.\n\n"
            "**Step 3 — Fire bans and advisories:**\n"
            "Call `alberta_get_fire_bans` for zones with active restrictions "
            "(full bans, fire advisories, OHV restrictions). "
            "See `data://alberta/forest-areas` for the 10 forest area codes used.\n\n"
            "**Step 4 — Fire control orders / OHV restrictions / forest area boundaries:**\n"
            "Call `alberta_get_fire_control_orders(category='fire_control')` "
            "(or `'ohv_restriction'`, `'forest_area'`) — one unified tool dispatches "
            "to three distinct WMBappServices FeatureServers by category.\n\n"
            "For the historical archive (2006-2025), call "
            "`alberta_query_dataset(dataset_id='wildfire-data')` — 10MB CSV on CKAN. "
            "See `docs://alberta/wildfire-data-guide` for the source-to-tool mapping "
            "and fire status codes.",
            role="assistant",
        ),
    ]


@prompt
async def alberta_explore_health_or_transport(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta health OR transport network exploration — branched workflow.

    Branches between health (alberta_get_hospitals -> alberta_get_ahs_zones ->
    alberta_get_health_facilities) and transport (alberta_get_road_events ->
    alberta_get_winter_road_conditions -> alberta_get_traffic_cameras).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données de santé OU de transport de l'Alberta. "
                "Quel domaine devrais-je choisir et comment procéder ?",
                role="user",
            ),
            Message(
                "Voici deux flux de travail. Choisissez celui qui correspond à votre question :\n\n"
                "## Option A — Santé (Alberta Health Services / AHS)\n\n"
                "**Étape A1 — Hôpitaux (101 établissements) :**\n"
                "Appelez `alberta_get_hospitals` pour les emplacements avec drapeaux IP/ED "
                "(hospitalisation / urgences). Filtrez par `zone='Calgary'`, `'Edmonton'`, "
                "`'North'`, `'Central'`, ou `'South'`.\n\n"
                "**Étape A2 — 5 zones AHS avec statistiques de population :**\n"
                "Appelez `alberta_get_ahs_zones` pour les limites et chiffres de population "
                "(POP2006/2011/2016). Consultez `data://alberta/ahs-zones` pour la référence "
                "statique (Sud, Calgary, Centre, Edmonton, Nord).\n\n"
                "**Étape A3 — Services EMS et cliniques PCN :**\n"
                "Appelez `alberta_get_health_facilities(facility_type='ems')` pour les "
                "stations d'ambulance, `'pcn_clinic'` pour les cliniques du Primary Care "
                "Network, `'walk_in'` pour les cliniques sans rendez-vous.\n\n"
                "## Option B — Transport (511 Alberta)\n\n"
                "**Étape B1 — Événements routiers :**\n"
                "Appelez `alberta_get_road_events` pour fermetures, construction, incidents "
                "actifs sur le réseau provincial. Retourne latitude/longitude, type d'événement, "
                "indicateur `IsFullClosure`.\n\n"
                "**Étape B2 — Conditions routières hivernales :**\n"
                "Appelez `alberta_get_winter_road_conditions` (saison nov.-avr.). "
                "Données provenant du feed 511 Alberta (JSON).\n\n"
                "**Étape B3 — Caméras de circulation :**\n"
                "Appelez `alberta_get_traffic_cameras` pour les emplacements des caméras "
                "avec URL d'image. Cache 24h (emplacements stables).\n\n"
                "Conseil : Les outils 511 utilisent `_511_get` (liste JSON brute), "
                "pas l'enveloppe CKAN — voir Plan 06 Pitfall 6."
            ,
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Alberta health OR transport data. "
            "Which domain should I pick and how do I proceed?",
            role="user",
        ),
        Message(
            "Here are two workflows. Pick the one matching your question:\n\n"
            "## Option A — Health (Alberta Health Services / AHS)\n\n"
            "**Step A1 — Hospitals (101 facilities):**\n"
            "Call `alberta_get_hospitals` for locations with IP/ED flags "
            "(inpatient / emergency department capability). "
            "Filter by `zone='Calgary'`, `'Edmonton'`, `'North'`, `'Central'`, or `'South'`.\n\n"
            "**Step A2 — 5 AHS zones with population stats:**\n"
            "Call `alberta_get_ahs_zones` for boundaries and population figures "
            "(POP2006/2011/2016). See `data://alberta/ahs-zones` for the static reference "
            "catalog (South, Calgary, Central, Edmonton, North).\n\n"
            "**Step A3 — EMS stations and PCN clinics:**\n"
            "Call `alberta_get_health_facilities(facility_type='ems')` for ambulance "
            "stations, `'pcn_clinic'` for Primary Care Network clinics, `'walk_in'` for "
            "walk-in clinics.\n\n"
            "## Option B — Transport (511 Alberta)\n\n"
            "**Step B1 — Road events:**\n"
            "Call `alberta_get_road_events` for active closures, construction, and incidents "
            "on the provincial network. Returns lat/lon, event type, and `IsFullClosure` flag.\n\n"
            "**Step B2 — Winter road conditions:**\n"
            "Call `alberta_get_winter_road_conditions` (November-April season). "
            "Data comes from the 511 Alberta JSON feed.\n\n"
            "**Step B3 — Traffic cameras:**\n"
            "Call `alberta_get_traffic_cameras` for camera locations with image URLs. "
            "24h cache (locations are stable).\n\n"
            "Tip: The 511 tools use `_511_get` (raw JSON list), NOT the CKAN envelope "
            "unwrap — see Plan 06 Pitfall 6.",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Quick lookups — return str with specific tool + parameter instructions
# ---------------------------------------------------------------------------


@prompt
async def alberta_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search the open.alberta.ca CKAN catalogue (33,269 datasets).

    Use for: one-shot Alberta open data discovery — search the federated CKAN catalog,
    inspect dataset details, and query records from the best available resource.
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le catalogue open.alberta.ca (33 269 jeux de données) :\n\n"
            "1. Appelez `alberta_search_datasets` avec `q='<mot-clé>'` "
            "(p. ex. `q='wildfire'`, `q='oil production'`, `q='hospitals'`). "
            "**Important** : 86 % des jeux de données Alberta sont des rapports PDF — "
            "ajoutez `format='CSV'` (ou `'XLSX'`, `'ESRI REST'`) pour ne retenir que les "
            "données lisibles par machine. Ajoutez `organization='energy-and-minerals'` "
            "(ou autre slug du catalogue — voir `data://alberta/ministries`) pour filtrer "
            "par ministère.\n\n"
            "2. Pour inspecter un jeu de données, appelez `alberta_get_dataset_details` "
            "avec le `name` (slug) retourné. Vérifiez le champ `resources` — chaque ressource "
            "indique son format et son URL. Recherchez `format='ESRI REST'` pour accès live, "
            "sinon `format='CSV'` ou `'XLSX'` pour téléchargement.\n\n"
            "3. Pour récupérer des données, appelez `alberta_query_dataset` avec le `name`. "
            "Le routeur auto-détecte et choisit la meilleure ressource : FeatureServer ArcGIS "
            "live si disponible (préféré), sinon téléchargement + analyse CSV/XLSX/JSON.\n\n"
            "Conseil : Le catalogue fédéré contient 370 organisations dont environ 150 "
            "ministères historiques. Utilisez `alberta_list_organizations` pour la liste "
            "complète. Consultez `alberta_list_categories` pour les formats disponibles "
            "(Alberta n'utilise PAS groups — group_list est vide, tag_list trop bruyant)."
        )
    return (
        "To search for data in the open.alberta.ca catalogue (33,269 datasets):\n\n"
        "1. Call `alberta_search_datasets` with `q='<keyword>'` "
        "(e.g. `q='wildfire'`, `q='oil production'`, `q='hospitals'`). "
        "**Important**: 86% of Alberta datasets are PDF reports — "
        "add `format='CSV'` (or `'XLSX'`, `'ESRI REST'`) to keep only "
        "machine-readable data. Add `organization='energy-and-minerals'` "
        "(or another catalog slug — see `data://alberta/ministries`) to filter "
        "by ministry.\n\n"
        "2. To inspect a dataset, call `alberta_get_dataset_details` with the `name` "
        "(slug) returned. Check the `resources` field — each resource has its format "
        "and URL. Look for `format='ESRI REST'` for live access, otherwise "
        "`format='CSV'` or `'XLSX'` for download.\n\n"
        "3. To fetch data records, call `alberta_query_dataset` with the `name`. "
        "The router auto-detects and picks the best resource: live ArcGIS FeatureServer "
        "when available (preferred), otherwise download + parse CSV/XLSX/JSON.\n\n"
        "Tip: The federated catalog has 370 organizations including ~150 historical "
        "ministries. Use `alberta_list_organizations` for the full list. "
        "See `alberta_list_categories` for available formats (Alberta does NOT use "
        "groups — group_list is empty, tag_list is too noisy)."
    )


@prompt
async def alberta_check_road_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Alberta road events and winter road conditions.

    Use for: quick lookup of 511 Alberta highway events, winter road conditions, and
    traffic cameras on Alberta's provincial road network.
    """
    if lang == "fr":
        return (
            "Pour consulter les conditions routières actuelles en Alberta (source : "
            "511 Alberta JSON feed) :\n\n"
            "**Événements routiers (fermetures, accidents, construction) :**\n"
            "Appelez `alberta_get_road_events` pour les événements actifs sur les "
            "autoroutes provinciales. Retourne `RoadwayName`, `EventType`, `Lat`, `Lon`, "
            "et le drapeau `IsFullClosure` pour identifier les fermetures complètes. "
            "TTL 5 min (mises à jour continues).\n\n"
            "**Conditions routières hivernales (nov.-avr.) :**\n"
            "Appelez `alberta_get_winter_road_conditions` pour l'état de la chaussée, "
            "la présence de neige, et les avertissements de poudrerie. "
            "Note : flux 511 saisonnier — peut être vide hors saison hivernale.\n\n"
            "**Caméras de circulation en direct :**\n"
            "Appelez `alberta_get_traffic_cameras` pour les emplacements des caméras "
            "routières avec URL d'image (statique, rafraîchie à la demande). "
            "TTL 24 h (emplacements stables).\n\n"
            "Conseil : Les trois outils utilisent `_511_get` (liste JSON brute) et non "
            "l'enveloppe CKAN — les réponses retournent directement un tableau d'objets. "
            "Pour filtrer par zone géographique, inspectez `Lat`/`Lon` dans la réponse."
        )
    return (
        "To check current road conditions in Alberta (source: 511 Alberta JSON feed):\n\n"
        "**Road events (closures, accidents, construction):**\n"
        "Call `alberta_get_road_events` for active events on the provincial highway network. "
        "Returns `RoadwayName`, `EventType`, `Lat`, `Lon`, and the `IsFullClosure` flag to "
        "identify full closures. 5-min cache TTL (continuous updates).\n\n"
        "**Winter road conditions (November-April):**\n"
        "Call `alberta_get_winter_road_conditions` for pavement state, snow presence, and "
        "blowing snow warnings. "
        "Note: seasonal 511 feed — may be empty outside winter season.\n\n"
        "**Live traffic cameras:**\n"
        "Call `alberta_get_traffic_cameras` for camera locations with image URLs "
        "(static, refreshed on demand). 24h cache TTL (locations are stable).\n\n"
        "Tip: All three tools use `_511_get` (raw JSON list) and NOT the CKAN envelope — "
        "responses return a plain array of objects. To filter by geographic area, inspect "
        "`Lat`/`Lon` in the response."
    )


@prompt
async def alberta_active_fires_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Alberta active wildfires from WMBappServices.

    Use for: quick wildfire situational awareness during fire season (May-October).
    Returns instruction to call alberta_get_active_fires with an optional status filter.
    """
    if lang == "fr":
        return (
            "Pour consulter les feux de forêt actifs en Alberta (source : WMBappServices "
            "Active_Wildfires_Dashboard_view, TTL 5 min) :\n\n"
            "**Feux actifs :**\n"
            "Appelez `alberta_get_active_fires` sans filtre pour tous les feux actifs. "
            "Ajoutez `status='Out of Control'` pour les feux les plus dangereux, "
            "`'Being Held'` pour les feux contenus mais non éteints, "
            "`'Under Control'` pour les feux maîtrisés dans leur périmètre.\n\n"
            "**Périmètres de feux (polygones) :**\n"
            "Pour obtenir les périmètres en cours, appelez "
            "`alberta_get_fire_perimeters(status='active', include_geometry=True)`.\n\n"
            "**Interdictions et ordres de contrôle :**\n"
            "Pour les zones avec restrictions, appelez `alberta_get_fire_bans`. "
            "Pour les ordres de contrôle spécifiques, appelez "
            "`alberta_get_fire_control_orders(category='fire_control')`.\n\n"
            "Conseil : La saison des feux en Alberta s'étend de mai à octobre. "
            "L'indice Canadien de Danger d'Incendie (FWI) N'est PAS exposé — "
            "WMBappServices ne publie pas les composantes FFMC/DMC/DC, et MSC weather "
            "non plus. Consultez `docs://alberta/wildfire-data-guide` pour les codes "
            "de statut et la cartographie source-à-outil."
        )
    return (
        "To check current Alberta active wildfires (source: WMBappServices "
        "Active_Wildfires_Dashboard_view, 5-min cache TTL):\n\n"
        "**Active fires:**\n"
        "Call `alberta_get_active_fires` with no filter for all active fires. "
        "Add `status='Out of Control'` for the most dangerous fires, "
        "`'Being Held'` for fires contained but not extinguished, "
        "`'Under Control'` for fires suppressed within their perimeter.\n\n"
        "**Fire perimeters (polygons):**\n"
        "To get in-progress perimeters, call "
        "`alberta_get_fire_perimeters(status='active', include_geometry=True)`.\n\n"
        "**Fire bans and control orders:**\n"
        "For zones with active restrictions, call `alberta_get_fire_bans`. "
        "For specific control orders, call "
        "`alberta_get_fire_control_orders(category='fire_control')`.\n\n"
        "Tip: Alberta fire season runs May-October. "
        "The Canadian Forest Fire Weather Index (FWI) is NOT exposed — "
        "WMBappServices does not publish FFMC/DMC/DC components, and MSC weather "
        "does not either. See `docs://alberta/wildfire-data-guide` for fire status "
        "codes and the source-to-tool mapping."
    )
