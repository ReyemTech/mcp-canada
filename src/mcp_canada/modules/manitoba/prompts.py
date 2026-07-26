"""Manitoba prompts — 6 bilingual prompts (3 guided + 3 quick lookups).

Guided workflows (list[Message]) — multi-step tool chaining:
  manitoba_explore_flood_or_water       — flood alerts + river stations + waterways workflow
  manitoba_explore_transport            — 511 road events / winter roads / cameras workflow
  manitoba_explore_agriculture_or_health — drought / livestock / surgical wait / facilities

Quick lookups (str) — single-tool instructions:
  manitoba_quick_dataset_search   — geoportal.gov.mb.ca ArcGIS Hub catalogue search
  manitoba_check_road_conditions  — 511 Manitoba winter road conditions (key required)
  manitoba_flood_outlook_now      — flood alert lookup from Overland_Flood_Alerts FeatureServer

IMPORTANT: All prompts accept `lang: Literal["en", "fr"] = "en"` via Annotated.
ZERO-parameter resources are in resources.py — see CLAUDE.md rule.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


__all__ = [
    # Guided workflows (list[Message])
    "manitoba_explore_flood_or_water",
    "manitoba_explore_transport",
    "manitoba_explore_agriculture_or_health",
    # Quick lookups (str)
    "manitoba_quick_dataset_search",
    "manitoba_check_road_conditions",
    "manitoba_flood_outlook_now",
]


# ---------------------------------------------------------------------------
# Guided workflows — return list[Message] with at least user + assistant roles
# ---------------------------------------------------------------------------


@prompt
async def manitoba_explore_flood_or_water(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Manitoba flood and water infrastructure data exploration.

    Chains manitoba_get_flood_alerts -> manitoba_get_river_stations ->
    manitoba_get_provincial_waterways for a comprehensive flood situational
    awareness picture from Manitoba's ArcGIS Hub (geoportal.gov.mb.ca).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre la situation d'inondation actuelle au Manitoba — "
                "alertes d'inondation, stations de rivières, et infrastructure hydrique.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données de gestion des eaux du Manitoba "
                "en trois étapes :\n\n"
                "**Étape 1 — Alertes d'inondation de surface (temps réel) :**\n"
                "Appelez `manitoba_get_flood_alerts` (TTL 5 min). "
                "Retourne des polygones de surveillance/avertissement d'inondation avec les champs "
                "bilingues `Type_EN`/`Type_FR`, dates de début/fin, et superficie. "
                "**Remarque :** Une réponse vide `{features:[]}` est normale hors-saison — "
                "il n'y a simplement aucune alerte active. Consultez "
                "`data://manitoba/major-rivers` pour la liste des principaux systèmes fluviaux "
                "et leurs niveaux de risque d'inondation.\n\n"
                "**Étape 2 — Stations de conditions des rivières :**\n"
                "Appelez `manitoba_get_river_stations` pour les emplacements des stations "
                "hydrométriques avec statut d'alerte (Normal, Avis Hautes Eaux, "
                "Surveillance Crue, Avertissement Crue). Les données proviennent d'un flux "
                "CSV du Manitoba — les lectures de niveau réelles sont dans la base de données "
                "HYDAT d'ECCC (non exposée via ce module).\n\n"
                "**Étape 3 — Voies navigables provinciales (infrastructure) :**\n"
                "Appelez `manitoba_get_provincial_waterways` pour les digues, "
                "voies de dérivation, barrages, réservoirs et voies d'eau provinciales. "
                "Filtrez par `f_type='dike'`, `'floodway'`, `'dam'`, `'diversion'`, "
                "`'reservoir'`, ou `'waterway'`. Le détournement Red River (chenal de crue) "
                "à l'est de Winnipeg est le principal élément d'infrastructure.\n\n"
                "Conseil : Les bulletins d'inondation du Centre de prévision hydrologique (HFC) "
                "sont en format PDF uniquement — non accessibles via machine. "
                "Les couches ArcGIS Hub ci-dessus sont la source lisible par machine "
                "faisant autorité. Consultez `docs://manitoba/flood-data-guide` pour "
                "la cartographie complète des sources.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to understand the current flood situation in Manitoba — "
            "flood alerts, river stations, and water infrastructure.",
            role="user",
        ),
        Message(
            "I'll guide you through Manitoba water management data in three steps:\n\n"
            "**Step 1 — Overland flood alerts (real-time):**\n"
            "Call `manitoba_get_flood_alerts` (5-min cache TTL). "
            "Returns flood Watch/Warning polygons with bilingual `Type_EN`/`Type_FR` fields, "
            "start/end dates, and area. "
            "**Note:** An empty response `{features:[]}` is normal off-season — "
            "it means no active alerts. See `data://manitoba/major-rivers` for the list "
            "of major river systems and their flood risk levels.\n\n"
            "**Step 2 — River conditions stations:**\n"
            "Call `manitoba_get_river_stations` for hydrometric station locations with "
            "flood alert status (Normal, High Water Advisory, Flood Watch, Flood Warning). "
            "Data comes from a Manitoba CSV feed — actual level readings are in ECCC's "
            "HYDAT database (not exposed through this module).\n\n"
            "**Step 3 — Provincial waterways (infrastructure):**\n"
            "Call `manitoba_get_provincial_waterways` for dikes, floodways, dams, "
            "reservoirs, diversions, and other water control infrastructure. "
            "Filter by `f_type='dike'`, `'floodway'`, `'dam'`, `'diversion'`, "
            "`'reservoir'`, or `'waterway'`. The Red River Floodway (bypass channel) "
            "east of Winnipeg is the key infrastructure piece.\n\n"
            "Tip: Flood bulletins from the Hydrologic Forecast Centre (HFC) are PDF-only — "
            "not machine-readable. The ArcGIS Hub layers above are the authoritative "
            "machine-readable source. See `docs://manitoba/flood-data-guide` for the "
            "full source-to-tool mapping.",
            role="assistant",
        ),
    ]


@prompt
async def manitoba_explore_transport(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Manitoba 511 transport network data exploration.

    Chains manitoba_get_road_events -> manitoba_get_winter_road_conditions ->
    manitoba_get_traffic_cameras for a comprehensive provincial road network picture
    from Manitoba 511 API v3 (key required — returns NOT_CONFIGURED if absent).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les conditions routières actuelles au Manitoba — "
                "événements routiers, routes d'hiver, et caméras de circulation.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données Manitoba 511 en trois étapes :\n\n"
                "**Important — Clé API requise :**\n"
                "L'API Manitoba 511 v3 (`www.manitoba511.ca/api/v3/get/`) nécessite une "
                "clé développeur enregistrée. Si la variable d'environnement "
                "`MANITOBA_511_KEY` n'est pas définie, les trois outils retournent "
                "`NOT_CONFIGURED` avec des instructions pour obtenir une clé. "
                "Inscription : `https://www.manitoba511.ca/developers/doc`\n\n"
                "**Étape 1 — Événements routiers (fermetures, accidents, construction) :**\n"
                "Appelez `manitoba_get_road_events` pour les événements actifs sur le "
                "réseau routier provincial. Retourne `LocationDescription`, `EventType`, "
                "`EncodedPolyline`, et `AreaName`. TTL 5 min (mises à jour continues).\n\n"
                "**Étape 2 — Conditions des routes d'hiver (saison nov.-avr.) :**\n"
                "Appelez `manitoba_get_winter_road_conditions` pour l'état de la chaussée, "
                "conditions secondaires, et visibilité sur les routes d'hiver du nord du Manitoba. "
                "Filtrez par `area_name='Thompson'` (ou autre zone) si nécessaire. "
                "Flux saisonnier — peut être vide hors saison.\n\n"
                "**Étape 3 — Caméras de circulation :**\n"
                "Appelez `manitoba_get_traffic_cameras` pour les emplacements des caméras "
                "avec URL des images. TTL 24 h (emplacements stables, images rafraîchies "
                "périodiquement à la source).\n\n"
                "Conseil : Contrairement à Alberta 511 (sans clé), Manitoba 511 exige une "
                "inscription. Les outils fonctionnent identiquement une fois la clé définie.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore current road conditions in Manitoba — "
            "road events, winter roads, and traffic cameras.",
            role="user",
        ),
        Message(
            "I'll guide you through Manitoba 511 data in three steps:\n\n"
            "**Important — API key required:**\n"
            "The Manitoba 511 API v3 (`www.manitoba511.ca/api/v3/get/`) requires a "
            "registered developer key. If the `MANITOBA_511_KEY` environment variable "
            "is not set, all three tools return `NOT_CONFIGURED` with instructions to "
            "obtain a key. Registration: `https://www.manitoba511.ca/developers/doc`\n\n"
            "**Step 1 — Road events (closures, accidents, construction):**\n"
            "Call `manitoba_get_road_events` for active events on the provincial road "
            "network. Returns `LocationDescription`, `EventType`, `EncodedPolyline`, "
            "and `AreaName`. 5-min cache TTL (continuous updates).\n\n"
            "**Step 2 — Winter road conditions (November-April season):**\n"
            "Call `manitoba_get_winter_road_conditions` for pavement state, secondary "
            "conditions, and visibility on northern Manitoba winter roads. "
            "Filter by `area_name='Thompson'` (or another area) if needed. "
            "Seasonal feed — may be empty outside winter season.\n\n"
            "**Step 3 — Traffic cameras:**\n"
            "Call `manitoba_get_traffic_cameras` for camera locations with image URLs. "
            "24h cache TTL (locations are stable, images refreshed periodically at source).\n\n"
            "Tip: Unlike Alberta 511 (keyless), Manitoba 511 requires registration. "
            "The tools work identically once the key is set.",
            role="assistant",
        ),
    ]


@prompt
async def manitoba_explore_agriculture_or_health(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Manitoba agriculture OR health data exploration — branched workflow.

    Branches between agriculture (manitoba_get_drought_status / manitoba_get_livestock_prices /
    manitoba_get_ag_weather_stations) and health (manitoba_get_surgical_wait_times /
    manitoba_get_health_facilities) from Manitoba's ArcGIS Hub.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données d'agriculture OU de santé du Manitoba. "
                "Quel domaine devrais-je choisir et comment procéder ?",
                role="user",
            ),
            Message(
                "Voici deux flux de travail. Choisissez celui qui correspond à votre question :\n\n"
                "## Option A — Agriculture (ArcGIS Hub Manitoba)\n\n"
                "**Étape A1 — Statut de sécheresse :**\n"
                "Appelez `manitoba_get_drought_status` pour les polygones D0-D4 du Moniteur "
                "de sécheresse Canada/USA. Filtre bbox Manitoba appliqué par défaut "
                "(lat 48.99–60.0, lon -101.36 à -95.15). D0 = Sécheresse anormalement "
                "sèche, D4 = Sécheresse exceptionnelle. TTL 24 h (mise à jour hebdomadaire).\n\n"
                "**Étape A2 — Prix du bétail (bovins et porcs) :**\n"
                "Appelez `manitoba_get_livestock_prices(livestock='cattle')` pour les prix "
                "hebdomadaires des ventes aux enchères de bovins. Utilisez `livestock='hog'` "
                "pour les porcs (remarque : le service ArcGIS pour les porcs peut être vide — "
                "retourne une liste vide avec une note explicative). "
                "Optionnel : `historical=True` pour les archives décennales.\n\n"
                "**Étape A3 — Stations météo agricoles :**\n"
                "Appelez `manitoba_get_ag_weather_stations` pour 100+ emplacements de stations "
                "avec `AgRegion` et un champ `URL` vers les données horaires en direct "
                "de Manitoba Agriculture. Filtrez par `ag_region='Central'` si nécessaire.\n\n"
                "## Option B — Santé (ArcGIS Hub Manitoba)\n\n"
                "**Étape B1 — Temps d'attente chirurgicaux :**\n"
                "Appelez `manitoba_get_surgical_wait_times` pour les moyennes annuelles "
                "par procédure (`IndicatorDataArea`) et année (`Year`). "
                "Couvre 32 000+ enregistrements : chirurgie cardiaque, orthopédie, "
                "ophtalmologie, etc. TTL 7 jours (données annuelles).\n\n"
                "**Étape B2 — Établissements de santé ruraux :**\n"
                "Appelez `manitoba_get_health_facilities` pour les établissements de soins "
                "ruraux avec drapeaux d'urgence/soins aigus/SLD. Filtrez par `rha='WRHA'` "
                "(ou `'PMH'`, `'IERHA'`, `'SHSS'`, `'NHR'`). "
                "Consultez `data://manitoba/health-regions` pour les 5 RRS et "
                "leurs hôpitaux principaux.\n\n"
                "Conseil : Les temps d'attente aux urgences en temps réel ne sont PAS "
                "publiés au Manitoba — données annuelles uniquement.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Manitoba agriculture OR health data. "
            "Which domain should I pick and how do I proceed?",
            role="user",
        ),
        Message(
            "Here are two workflows. Pick the one matching your question:\n\n"
            "## Option A — Agriculture (Manitoba ArcGIS Hub)\n\n"
            "**Step A1 — Drought status:**\n"
            "Call `manitoba_get_drought_status` for D0-D4 drought polygons from the "
            "Canada/USA Drought Monitor. Manitoba bounding-box filter applied by default "
            "(lat 48.99–60.0, lon -101.36 to -95.15). D0 = Abnormally Dry, "
            "D4 = Exceptional Drought. 24h cache TTL (weekly update at source).\n\n"
            "**Step A2 — Livestock prices (cattle and hogs):**\n"
            "Call `manitoba_get_livestock_prices(livestock='cattle')` for weekly cattle "
            "auction prices. Use `livestock='hog'` for hogs (note: the hog ArcGIS service "
            "may be unavailable — returns empty list with an explanatory note). "
            "Optional: `historical=True` for the 10-year archive.\n\n"
            "**Step A3 — Agricultural weather stations:**\n"
            "Call `manitoba_get_ag_weather_stations` for 100+ station locations with "
            "`AgRegion` and a `URL` field linking to live hourly data from Manitoba "
            "Agriculture. Filter by `ag_region='Central'` if needed.\n\n"
            "## Option B — Health (Manitoba ArcGIS Hub)\n\n"
            "**Step B1 — Surgical wait times:**\n"
            "Call `manitoba_get_surgical_wait_times` for annual averages by procedure "
            "(`IndicatorDataArea`) and year (`Year`). Covers 32,000+ records: cardiac "
            "surgery, orthopedics, ophthalmology, and more. 7-day cache TTL (annual data).\n\n"
            "**Step B2 — Rural health care facilities:**\n"
            "Call `manitoba_get_health_facilities` for rural health facilities with "
            "emergency/acute care/LTC flags. Filter by `rha='WRHA'` "
            "(or `'PMH'`, `'IERHA'`, `'SHSS'`, `'NHR'`). "
            "See `data://manitoba/health-regions` for the 5 RHAs and major hospitals.\n\n"
            "Tip: Real-time ER wait times are NOT published in Manitoba — annual data only.",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Quick lookups — return str with specific tool + parameter instructions
# ---------------------------------------------------------------------------


@prompt
async def manitoba_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search Manitoba's geoportal.gov.mb.ca ArcGIS Hub catalogue.

    Use for: one-shot Manitoba open data discovery — search the ArcGIS Hub catalog,
    inspect dataset details, and query records from FeatureServers or file resources.
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le géoportail Manitoba (geoportal.gov.mb.ca — "
            "ArcGIS Hub, 93+ services FeatureServer) :\n\n"
            "1. Appelez `manitoba_search_datasets` avec `q='<mot-clé>'` "
            "(p. ex. `q='flood'`, `q='parks'`, `q='agriculture'`). "
            "Le géoportail Manitoba utilise ArcGIS Hub Search API — pas une API CKAN. "
            "Ajoutez `category='<catégorie>'` pour filtrer par thème si disponible.\n\n"
            "2. Pour inspecter un jeu de données, appelez `manitoba_get_dataset_details` "
            "avec l'`id` (GUID) retourné. Vérifiez le champ `resources` — chaque ressource "
            "indique son type (FeatureServer, CSV, GeoJSON, etc.) et son URL.\n\n"
            "3. Pour récupérer des données, appelez `manitoba_query_dataset` avec l'URL "
            "du FeatureServer (champ `feature_server_url` dans les détails). "
            "Le routeur auto-détecte : FeatureServer ArcGIS live (préféré), "
            "ou téléchargement + analyse CSV/GeoJSON/XLSX.\n\n"
            "Consultez `data://manitoba/departments` pour les ministères provinciaux et "
            "leurs domaines de données principaux. Utilisez `manitoba_list_organizations` "
            "pour les organismes publiants sur le géoportail."
        )
    return (
        "To search for data in the Manitoba geoportal (geoportal.gov.mb.ca — "
        "ArcGIS Hub, 93+ FeatureServer services):\n\n"
        "1. Call `manitoba_search_datasets` with `q='<keyword>'` "
        "(e.g. `q='flood'`, `q='parks'`, `q='agriculture'`). "
        "Manitoba's geoportal uses ArcGIS Hub Search API — not a CKAN API. "
        "Add `category='<category>'` to filter by theme if available.\n\n"
        "2. To inspect a dataset, call `manitoba_get_dataset_details` with the `id` "
        "(GUID) returned. Check the `resources` field — each resource shows its type "
        "(FeatureServer, CSV, GeoJSON, etc.) and URL.\n\n"
        "3. To fetch data records, call `manitoba_query_dataset` with the FeatureServer "
        "URL (the `feature_server_url` field in dataset details). "
        "The router auto-detects: live ArcGIS FeatureServer (preferred), "
        "or download + parse CSV/GeoJSON/XLSX.\n\n"
        "See `data://manitoba/departments` for provincial ministries and their key data "
        "domains. Use `manitoba_list_organizations` for publishing organizations on the geoportal."
    )


@prompt
async def manitoba_check_road_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Manitoba road events and winter road conditions via 511.

    Use for: quick lookup of Manitoba 511 highway events, winter road conditions, and
    traffic cameras on the provincial road network. Note: requires MANITOBA_511_KEY
    environment variable — tools return NOT_CONFIGURED if the key is absent.
    """
    if lang == "fr":
        return (
            "Pour consulter les conditions routières actuelles au Manitoba "
            "(source : API Manitoba 511 v3) :\n\n"
            "**Clé API requise :** Définissez `MANITOBA_511_KEY` dans l'environnement. "
            "Sans clé, les outils retournent `NOT_CONFIGURED` avec des instructions "
            "pour s'inscrire sur `https://www.manitoba511.ca/developers/doc`.\n\n"
            "**Conditions des routes d'hiver (nov.-avr.) :**\n"
            "Appelez `manitoba_get_winter_road_conditions` pour l'état de la chaussée "
            "et la visibilité sur les routes d'hiver du Nord Manitoba. "
            "Filtrez par `area_name='Thompson'` (ou `'The Pas'`, `'Flin Flon'`) "
            "pour les conditions régionales. Flux saisonnier — peut être vide hors saison.\n\n"
            "**Événements routiers (fermetures, construction, incidents) :**\n"
            "Appelez `manitoba_get_road_events` pour les événements actifs avec "
            "`LocationDescription`, `EventType`, et `EncodedPolyline`. TTL 5 min.\n\n"
            "**Caméras de circulation :**\n"
            "Appelez `manitoba_get_traffic_cameras` pour les emplacements avec URL d'image. "
            "TTL 24 h (emplacements stables)."
        )
    return (
        "To check current road conditions in Manitoba "
        "(source: Manitoba 511 API v3):\n\n"
        "**API key required:** Set `MANITOBA_511_KEY` in the environment. "
        "Without a key, tools return `NOT_CONFIGURED` with instructions to "
        "register at `https://www.manitoba511.ca/developers/doc`.\n\n"
        "**Winter road conditions (November-April):**\n"
        "Call `manitoba_get_winter_road_conditions` for pavement state and visibility "
        "on northern Manitoba winter roads. "
        "Filter by `area_name='Thompson'` (or `'The Pas'`, `'Flin Flon'`) for "
        "regional conditions. Seasonal feed — may be empty outside winter season.\n\n"
        "**Road events (closures, construction, incidents):**\n"
        "Call `manitoba_get_road_events` for active events with `LocationDescription`, "
        "`EventType`, and `EncodedPolyline`. 5-min cache TTL.\n\n"
        "**Traffic cameras:**\n"
        "Call `manitoba_get_traffic_cameras` for camera locations with image URLs. "
        "24h cache TTL (locations are stable)."
    )


@prompt
async def manitoba_flood_outlook_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Manitoba flood alerts from ArcGIS Hub.

    Use for: quick flood situational awareness — checks the Overland_Flood_Alerts
    FeatureServer for active Watch/Warning polygons. Returns instruction to call
    manitoba_get_flood_alerts with optional type filter.
    """
    if lang == "fr":
        return (
            "Pour consulter les alertes d'inondation actuelles au Manitoba "
            "(source : FeatureServer Overland_Flood_Alerts, TTL 5 min) :\n\n"
            "**Alertes actives :**\n"
            "Appelez `manitoba_get_flood_alerts` sans filtre pour toutes les alertes actives. "
            "Retourne des polygones avec `Type_EN`/`Type_FR` (Flood Watch / Flood Warning / "
            "Overland Flood Advisory), dates de début/fin, et superficie.\n\n"
            "**Surveillance vs Avertissement :**\n"
            "- *Flood Watch* : conditions propices aux inondations — préparez-vous\n"
            "- *Flood Warning* : inondation en cours ou imminente — agissez\n"
            "- *High Water Advisory* : niveaux d'eau élevés, risque modéré\n\n"
            "**Stations de rivières (localisation) :**\n"
            "Pour les points de station de surveillance avec statut d'alerte, "
            "appelez `manitoba_get_river_stations`. "
            "Les lectures de niveau réelles sont dans la base de données HYDAT d'ECCC.\n\n"
            "**Saison de crues :** La saison typique de crues printanières de la rivière "
            "Rouge est de mars à mai. Le niveau de risque le plus élevé est la rivière "
            "Rouge (risque très élevé) et la rivière Assiniboine (risque élevé). "
            "Consultez `data://manitoba/major-rivers` pour les données de risque de "
            "chaque rivière et `docs://manitoba/flood-data-guide` pour les "
            "distinctions entre sources."
        )
    return (
        "To check current Manitoba flood alerts "
        "(source: Overland_Flood_Alerts FeatureServer, 5-min cache TTL):\n\n"
        "**Active alerts:**\n"
        "Call `manitoba_get_flood_alerts` with no filter for all active alerts. "
        "Returns polygons with `Type_EN`/`Type_FR` (Flood Watch / Flood Warning / "
        "Overland Flood Advisory), start/end dates, and area.\n\n"
        "**Watch vs Warning:**\n"
        "- *Flood Watch*: conditions favourable for flooding — prepare\n"
        "- *Flood Warning*: flooding is occurring or imminent — act now\n"
        "- *High Water Advisory*: elevated water levels, moderate risk\n\n"
        "**River stations (locations):**\n"
        "For monitoring station points with alert status, call `manitoba_get_river_stations`. "
        "Actual level readings are in ECCC's HYDAT database.\n\n"
        "**Flood season:** The typical Red River spring flood season is March to May. "
        "Highest risk rivers are the Red River (Very High risk) and Assiniboine River "
        "(High risk). See `data://manitoba/major-rivers` for per-river risk data and "
        "`docs://manitoba/flood-data-guide` for source distinctions."
    )
