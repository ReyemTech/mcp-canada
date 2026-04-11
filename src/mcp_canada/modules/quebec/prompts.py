"""Quebec prompts — 6 bilingual prompts for Quebec data exploration.

Guided workflows (list[Message]) — multi-step tool chaining:
  quebec_explore_health, quebec_explore_transport_conditions, quebec_explore_environment

Quick lookups (str) — single-tool instructions:
  quebec_quick_dataset_search, quebec_check_road_conditions, quebec_active_fires_now

IMPORTANT: All prompts accept lang: Literal["en", "fr"] = "en" parameter.
ZERO-parameter resources are in resources.py — see CLAUDE.md rule.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


__all__ = [
    "quebec_explore_health",
    "quebec_explore_transport_conditions",
    "quebec_explore_environment",
    "quebec_quick_dataset_search",
    "quebec_check_road_conditions",
    "quebec_active_fires_now",
]


@prompt
async def quebec_explore_health(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Quebec health data exploration — installations, ER wait times, demographics.

    Chains quebec_get_health_installations -> quebec_get_er_wait_times ->
    quebec_get_population_by_municipality for a comprehensive health-system overview.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données de santé au Québec — établissements, "
                "temps d'attente aux urgences, et données démographiques par région.",
                role="user",
            ),
            Message(
                "Je vais vous guider dans l'exploration des données de santé au Québec "
                "en trois étapes:\n\n"
                "**Étape 1 — Établissements de santé:**\n"
                "Appelez `quebec_get_health_installations` sans filtre pour toutes les installations "
                "(1 592 au total), ou filtrez avec `instal_type='CHSGS'` pour les hôpitaux seulement, "
                "`instal_type='CLSC'` pour les centres communautaires, "
                "`instal_type='CHSLD'` pour les soins de longue durée. "
                "Ajoutez `rss_name='Montréal'` pour limiter à une région sociosanitaire.\n\n"
                "**Étape 2 — Urgences en temps réel:**\n"
                "Appelez `quebec_get_er_wait_times` pour toutes les 116 urgences hospitalières "
                "(mise à jour toutes les heures). Utilisez `installation='Rimouski'` pour filtrer "
                "par nom d'installation. Vérifiez `patients_over_24h` et `occupied_stretchers` "
                "pour identifier les urgences surchargées.\n\n"
                "**Étape 3 — Données démographiques:**\n"
                "Appelez `quebec_get_population_by_municipality` avec `region='06'` (Montréal), "
                "`region='03'` (Capitale-Nationale), ou sans filtre pour toutes les 1 282 "
                "municipalités. Croisez avec les données d'établissements pour estimer "
                "la couverture santé par région.\n\n"
                "Conseil: Les données d'urgence sont rafraîchies toutes les heures. "
                "Les installations sont mises à jour semestriellement.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Quebec health data — facilities, ER wait times, and "
            "regional demographics.",
            role="user",
        ),
        Message(
            "I'll guide you through Quebec health data exploration in three steps:\n\n"
            "**Step 1 — Health installations:**\n"
            "Call `quebec_get_health_installations` with no filter for all 1,592 installations, "
            "or filter with `instal_type='CHSGS'` for hospitals only, "
            "`instal_type='CLSC'` for community clinics, "
            "`instal_type='CHSLD'` for long-term care. "
            "Add `rss_name='Montréal'` to limit to a health region (RSS).\n\n"
            "**Step 2 — Real-time ER wait times:**\n"
            "Call `quebec_get_er_wait_times` for all 116 hospital emergency departments "
            "(updated hourly). Use `installation='Rimouski'` to filter by facility name. "
            "Check `patients_over_24h` and `occupied_stretchers` to identify overwhelmed ERs.\n\n"
            "**Step 3 — Demographics:**\n"
            "Call `quebec_get_population_by_municipality` with `region='06'` (Montreal), "
            "`region='03'` (Capitale-Nationale), or no filter for all 1,282 municipalities. "
            "Cross-reference with installation data to estimate health coverage by region.\n\n"
            "Tip: ER data refreshes hourly. Installations are updated semi-annually. "
            "All titles are in French (Données Québec is French-primary).",
            role="assistant",
        ),
    ]


@prompt
async def quebec_explore_transport_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Quebec transport data exploration — road conditions, works, events.

    Chains quebec_get_road_conditions -> quebec_get_road_works -> quebec_get_road_events ->
    quebec_get_bridge_structures for a comprehensive road network analysis.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux analyser les conditions routières et les travaux en cours au Québec. "
                "Que se passe-t-il sur le réseau routier en ce moment?",
                role="user",
            ),
            Message(
                "Voici comment explorer les données de transport du MTQ en quatre étapes:\n\n"
                "**Étape 1 — Conditions routières hivernales:**\n"
                "Appelez `quebec_get_road_conditions` (données WFS MTQ, fiabilité variable "
                "hors saison hivernale). Retourne l'état de la chaussée, la visibilité, "
                "la présence de neige. Utilisez `lang='fr'` pour des descriptions en français.\n\n"
                "**Étape 2 — Chantiers actifs:**\n"
                "Appelez `quebec_get_road_works` pour tous les chantiers de construction actifs "
                "sur le réseau provincial (flux WFS continu). Les colonnes de description sont "
                "bilingues — sélectionnées par le paramètre `lang`.\n\n"
                "**Étape 3 — Événements routiers:**\n"
                "Appelez `quebec_get_road_events` pour les accidents, incidents et avertissements "
                "actifs (colonnes en français uniquement). Filtrez par `municipalite` ou `regions` "
                "dans la réponse.\n\n"
                "**Étape 4 — Inventaire des structures:**\n"
                "Appelez `quebec_get_bridge_structures` avec `municipality='Granby'` ou "
                "`route='10'` pour les ponts et ponceaux. AU MOINS UN FILTRE REQUIS "
                "(l'inventaire contient 50 000+ structures).\n\n"
                "Conseil: Les données routières sont continues (~5 min de cache). "
                "L'inventaire des structures est mis à jour quotidiennement.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to analyze current road conditions and ongoing construction in Quebec. "
            "What's happening on the road network right now?",
            role="user",
        ),
        Message(
            "Here's how to explore MTQ transport data in four steps:\n\n"
            "**Step 1 — Winter road conditions:**\n"
            "Call `quebec_get_road_conditions` (MTQ WFS data, reliability varies outside winter). "
            "Returns pavement state, visibility, snow presence. Use `lang='fr'` for "
            "French descriptions.\n\n"
            "**Step 2 — Active construction zones:**\n"
            "Call `quebec_get_road_works` for all active road construction on the provincial "
            "network (continuous WFS feed). Description columns are bilingual — selected by `lang`.\n\n"
            "**Step 3 — Road events:**\n"
            "Call `quebec_get_road_events` for active accidents, incidents, and warnings "
            "(French-only columns). Filter by `municipalite` or `regions` in the response.\n\n"
            "**Step 4 — Structure inventory:**\n"
            "Call `quebec_get_bridge_structures` with `municipality='Granby'` or "
            "`route='10'` for bridges and culverts. AT LEAST ONE FILTER REQUIRED "
            "(inventory has 50,000+ structures).\n\n"
            "Tip: Road data refreshes ~every 5 min. Structure inventory updates daily. "
            "Route numbers are strings (e.g. `route='10'` for Autoroute 10).",
            role="assistant",
        ),
    ]


@prompt
async def quebec_explore_environment(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Quebec environmental data — air quality, water, protected areas.

    Chains quebec_get_air_quality_stations -> quebec_get_air_quality_index ->
    quebec_get_water_quality_monitoring -> quebec_get_protected_areas.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre les données environnementales au Québec — "
                "qualité de l'air, qualité de l'eau et aires protégées.",
                role="user",
            ),
            Message(
                "Voici comment explorer les données environnementales du MELCCFP en quatre étapes:\n\n"
                "**Étape 1 — Réseau de surveillance de la qualité de l'air (RSQAQ):**\n"
                "Appelez `quebec_get_air_quality_stations` pour localiser les stations de "
                "surveillance actives (par défaut `active_only=True`). Filtrez dans la réponse "
                "par `admin_region`, `municipality` ou `milieu_type` (Urbain/Rural/Industriel).\n\n"
                "**Étape 2 — Indice de la qualité de l'air (IQA) en temps réel:**\n"
                "Appelez `quebec_get_air_quality_index` pour les mesures actuelles de l'IQA "
                "de toutes les stations actives (ArcGIS FeatureServer, actualisé toutes les heures). "
                "Vérifiez le champ `COTE` (Bon/Acceptable/Mauvais) pour identifier les zones "
                "à risque.\n\n"
                "**Étape 3 — Surveillance de la qualité de l'eau:**\n"
                "Appelez `quebec_get_water_quality_monitoring` pour les métadonnées et les URL "
                "de téléchargement du jeu de données physicochimique des rivières. "
                "Les données géospatiales sont en ZIP/GeoJSON — téléchargement externe requis.\n\n"
                "**Étape 4 — Aires protégées:**\n"
                "Appelez `quebec_get_protected_areas` pour les métadonnées et URL du Registre "
                "des aires protégées (10 000+ zones, format SHP/GPKG). "
                "Pour l'électricité, consultez `quebec_get_electricity_data` "
                "(statistiques historiques Hydro-Québec).\n\n"
                "Conseil: Les données IQA sont actualisées toutes les heures. "
                "Les archives géospatiales (SHP/GPKG) nécessitent un logiciel SIG externe.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Quebec environmental data — air quality, water quality, "
            "and protected areas.",
            role="user",
        ),
        Message(
            "Here's how to explore MELCCFP environmental data in four steps:\n\n"
            "**Step 1 — Air quality monitoring stations (RSQAQ):**\n"
            "Call `quebec_get_air_quality_stations` to locate active monitoring stations "
            "(default `active_only=True`). Filter the response by `admin_region`, "
            "`municipality`, or `milieu_type` (Urbain/Rural/Industriel).\n\n"
            "**Step 2 — Real-time air quality index (IQA):**\n"
            "Call `quebec_get_air_quality_index` for current IQA readings across all active "
            "stations (ArcGIS FeatureServer, hourly refresh). Check the `COTE` field "
            "(Bon/Acceptable/Mauvais) to identify at-risk areas.\n\n"
            "**Step 3 — Water quality monitoring:**\n"
            "Call `quebec_get_water_quality_monitoring` for metadata and download URLs of "
            "the physicochemical river monitoring dataset. Geospatial data is ZIP/GeoJSON "
            "format — external download required.\n\n"
            "**Step 4 — Protected areas:**\n"
            "Call `quebec_get_protected_areas` for the Registre des aires protégées metadata "
            "and download URLs (10,000+ areas, SHP/GPKG format). "
            "For electricity, use `quebec_get_electricity_data` (Hydro-Québec historical stats).\n\n"
            "Tip: IQA data refreshes hourly. Geospatial archives (SHP/GPKG) require external "
            "GIS software. All dataset titles are in French (Données Québec is French-primary).",
            role="assistant",
        ),
    ]


@prompt
async def quebec_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search the Données Québec catalogue and explore a dataset.

    Use for: one-shot Quebec open data discovery — search the federated CKAN catalog,
    inspect dataset details, and query records from the best available resource.
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le catalogue Données Québec:\n\n"
            "1. Appelez `quebec_search_datasets` avec `q='<mot-clé>'` "
            "(ex. `q='qualité de l'eau'`, `q='hôpitaux'`). "
            "Ajoutez `organization='msss'` pour filtrer par ministère, "
            "ou `group='sante'` pour le groupe thématique Santé.\n\n"
            "2. Pour inspecter un jeu de données, appelez `quebec_get_dataset_details` "
            "avec le `name` (slug) retourné. Vérifiez le champ `resources` — chaque ressource "
            "indique le format (CSV/GeoJSON/SHP) et si `datastore_active=true`.\n\n"
            "3. Pour récupérer des données, appelez `quebec_query_dataset` avec le `name` "
            "du jeu de données. Route automatiquement vers `datastore_search` si disponible, "
            "sinon télécharge et analyse le fichier CSV/GeoJSON directement.\n\n"
            "Conseil: Les titres et descriptions sont en français uniquement. "
            "Utilisez `quebec_list_organizations` pour découvrir les 139 organisations "
            "du catalogue fédéré (ministères provinciaux, municipalités, Hydro-Québec, etc.)."
        )
    return (
        "To search for data in the Données Québec catalogue:\n\n"
        "1. Call `quebec_search_datasets` with `q='<keyword>'` "
        "(e.g. `q='water quality'`, `q='hospitals'`). "
        "Add `organization='msss'` to filter by ministry, "
        "or `group='sante'` for the Santé thematic group.\n\n"
        "2. To inspect a dataset, call `quebec_get_dataset_details` with the `name` (slug) "
        "returned. Check the `resources` field — each resource shows format (CSV/GeoJSON/SHP) "
        "and whether `datastore_active=true`.\n\n"
        "3. To fetch data records, call `quebec_query_dataset` with the dataset `name`. "
        "Automatically routes to `datastore_search` when available, otherwise downloads "
        "and parses the CSV/GeoJSON file directly.\n\n"
        "Note: All titles and descriptions are French-only (Données Québec is French-primary). "
        "Use `quebec_list_organizations` to discover all 139 federated catalog organizations "
        "(provincial ministries, municipalities, Hydro-Québec, BIXI, etc.)."
    )


@prompt
async def quebec_check_road_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Quebec road conditions and active construction zones.

    Use for: quick lookup of MTQ road conditions, active work zones, and road events
    on Quebec's provincial road network.
    """
    if lang == "fr":
        return (
            "Pour consulter les conditions routières actuelles au Québec:\n\n"
            "**Conditions hivernales:**\n"
            "Appelez `quebec_get_road_conditions` (lang='fr' pour les descriptions en français). "
            "Note: données WFS à fiabilité variable hors saison hivernale — "
            "peut retourner une liste vide en été.\n\n"
            "**Chantiers de construction actifs:**\n"
            "Appelez `quebec_get_road_works` pour tous les chantiers provinciaux actifs. "
            "Le champ `description` est en français avec lang='fr', anglais sinon. "
            "Filtrez dans la réponse par `route` (ex. 'A-25') ou `direction`.\n\n"
            "**Événements routiers (accidents, incidents):**\n"
            "Appelez `quebec_get_road_events` pour les avertissements actifs. "
            "Colonnes en français uniquement (pas d'équivalent anglais dans ce flux WFS).\n\n"
            "Conseil: Toutes les données MTQ sont actualisées en continu (~5 min de cache). "
            "Les conditions hivernales couvrent uniquement la saison novembre-avril."
        )
    return (
        "To check current road conditions in Quebec:\n\n"
        "**Winter road conditions:**\n"
        "Call `quebec_get_road_conditions` (use `lang='fr'` for French descriptions). "
        "Note: WFS endpoint has variable reliability outside winter season — "
        "may return empty list in summer.\n\n"
        "**Active construction zones:**\n"
        "Call `quebec_get_road_works` for all active provincial construction sites. "
        "The `description` field is in English (or French with lang='fr'). "
        "Filter the response by `route` (e.g. 'A-25') or `direction`.\n\n"
        "**Road events (accidents, incidents):**\n"
        "Call `quebec_get_road_events` for active road warnings. "
        "Columns are French-only (no English equivalent in this MTQ WFS feed).\n\n"
        "Tip: All MTQ data refreshes continuously (~5 min cache). "
        "Winter conditions cover November-April season only."
    )


@prompt
async def quebec_active_fires_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction for Quebec active wildfire status — redirects to SOPFEU external site.

    Use for: Quebec active wildfire situational awareness. SOPFEU data is NOT on Données Québec
    CKAN — this prompt redirects agents to the SOPFEU external portal.
    Historical fire perimeter archive (SHP) is available via quebec_get_forest_fires_history.
    """
    if lang == "fr":
        return (
            "**Important:** Les données SOPFEU sur les feux actifs NE sont PAS disponibles "
            "dans le catalogue Données Québec (CKAN). SOPFEU n'est pas enregistré comme "
            "organisation sur la plateforme DQ.\n\n"
            "Pour les feux actifs en temps réel:\n"
            "- Visitez **sopfeu.qc.ca** directement — carte interactive des feux actifs, "
            "indices de danger, zones d'interdiction.\n"
            "- L'API publique SOPFEU n'est pas disponible via MCP pour l'instant.\n\n"
            "Pour l'archive historique des périmètres de feux:\n"
            "Appelez `quebec_get_forest_fires_history` pour les métadonnées MFFP/MRN "
            "et les URL de téléchargement des archives SHP/GPKG (données annuelles, "
            "traitement SIG externe requis pour les polygones).\n\n"
            "Pour les prévisions météorologiques liées aux incendies:\n"
            "Consultez les outils MSC (`wx_get_current_conditions`) pour les stations "
            "météorologiques proches des zones à risque."
        )
    return (
        "**Important:** SOPFEU active fire data is NOT available in the Données Québec "
        "CKAN catalogue. SOPFEU is not registered as an organization on the DQ platform.\n\n"
        "For real-time active fires:\n"
        "- Visit **sopfeu.qc.ca** directly — interactive active fire map, "
        "danger indices, restriction zones.\n"
        "- The SOPFEU public API is not available via MCP at this time.\n\n"
        "For historical fire perimeter archive:\n"
        "Call `quebec_get_forest_fires_history` for MFFP/MRN metadata and download "
        "URLs of SHP/GPKG archives (annual data, external GIS software needed for polygons).\n\n"
        "For weather conditions near fire zones:\n"
        "Use MSC tools (`wx_get_current_conditions`) for weather stations near at-risk areas."
    )
