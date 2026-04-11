"""BC open data prompts — 6 bilingual prompts for British Columbia data exploration.

Prompts guide agents through BC data exploration workflows:
- bc_explore_wildfires: guided multi-tool wildfire analysis (list[Message])
- bc_explore_forestry: guided multi-tool forestry analysis (list[Message])
- bc_explore_environment: guided multi-tool environment analysis (list[Message])
- bc_quick_dataset_search: quick lookup for dataset discovery (str)
- bc_check_water_quality: quick lookup for water quality data (str)
- bc_wildfire_status_now: quick lookup for current wildfire status (str)
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def bc_explore_wildfires(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a multi-step BC wildfire situation analysis.

    Chains bc_get_active_fires -> bc_get_fire_perimeters -> bc_get_wildfire_weather_stations
    for a comprehensive wildfire exploration covering active incidents, historical context,
    and weather station data from BC Geographic Warehouse (WFS).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre la situation actuelle des feux de forêt en Colombie-Britannique. "
                "Qu'est-ce qui brûle en ce moment?",
                role="user",
            ),
            Message(
                "Je vais vous aider à explorer les feux de forêt en C.-B. Voici les étapes recommandées:\n\n"
                "**Étape 1 — Incidents actifs:**\n"
                "Appelez `bc_get_active_fires` (sans filtre) pour obtenir les incidents actuels. "
                "Filtrez par `fire_centre` (ex. 'Kamloops') ou `fire_cause` ('Lightning', 'Human') "
                "pour affiner. Utilisez `status='Out of Control'` pour les feux les plus urgents.\n\n"
                "**Étape 2 — Contexte historique:**\n"
                "Pour les feux les plus importants, appelez `bc_get_fire_perimeters` avec "
                "`fire_year=<année_actuelle>` pour obtenir les polygones de périmètre historiques. "
                "Ajoutez `min_size=1000` pour filtrer les grands incendies (> 1 000 hectares).\n\n"
                "**Étape 3 — Résumé:**\n"
                "Résumez par centre des feux de forêt (Kamloops, Coastal, Northwest, Prince George, "
                "Southeast, Cariboo) et par cause. Appelez `bc_get_wildfire_weather_stations` pour "
                "les données météorologiques connexes des stations de surveillance.\n\n"
                "Conseil: Les données des feux actifs sont actualisées toutes les 5 minutes. "
                "Utilisez `include_geometry=true` pour les analyses spatiales.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to understand the current BC wildfire situation. What's burning right now?",
            role="user",
        ),
        Message(
            "I'll help you explore BC wildfires. Here are the recommended steps:\n\n"
            "**Step 1 — Active incidents:**\n"
            "Call `bc_get_active_fires` (no filter) to get current incidents. "
            "Filter by `fire_centre` (e.g. 'Kamloops') or `fire_cause` ('Lightning', 'Human') "
            "to narrow down. Use `status='Out of Control'` for the most urgent fires.\n\n"
            "**Step 2 — Historical context:**\n"
            "For the most significant fires, call `bc_get_fire_perimeters` with "
            "`fire_year=<current_year>` to get historical perimeter polygons. "
            "Add `min_size=1000` to filter for large fires (> 1,000 ha).\n\n"
            "**Step 3 — Summarize:**\n"
            "Summarize by fire centre (Kamloops, Coastal, Northwest, Prince George, "
            "Southeast, Cariboo) and by cause. Call `bc_get_wildfire_weather_stations` "
            "for related weather monitoring station data.\n\n"
            "Tip: Active fire data refreshes every 5 minutes. Use `include_geometry=true` "
            "for spatial analysis.",
            role="assistant",
        ),
    ]


@prompt
async def bc_explore_forestry(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through forestry tenure, cut blocks, and protected area analysis in BC.

    Chains bc_get_forest_tenure -> bc_get_cut_blocks -> bc_get_protected_areas for a
    comprehensive forestry land use analysis in BC's Geographic Warehouse (WFS).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre l'activité forestière et les terres protégées dans une région "
                "spécifique de la Colombie-Britannique.",
                role="user",
            ),
            Message(
                "Voici comment explorer les données forestières en C.-B. en trois étapes:\n\n"
                "**Étape 1 — Tenures forestières actives:**\n"
                "Appelez `bc_get_forest_tenure` avec `client_name='<entreprise>'` ou sans filtre "
                "pour obtenir tous les accords de tenure actifs. Le champ `LICENCE_ID` identifie "
                "chaque tenure; `CLIENT_NAME` indique le détenteur de la licence.\n\n"
                "**Étape 2 — Blocs de coupe récents:**\n"
                "Appelez `bc_get_cut_blocks` avec le même district ou sans filtre pour voir "
                "les zones récoltées. Comparez les blocs de coupe avec les tenures pour identifier "
                "où la récolte est active.\n\n"
                "**Étape 3 — Aires protégées:**\n"
                "Appelez `bc_get_protected_areas` (avec `designation='PROVINCIAL PARK'` ou sans) "
                "pour voir quelles terres sont protégées. Comparez les aires et les détenteurs de tenure.\n\n"
                "Conseil: Les données de tenure sont statiques (cache 24h). Ajoutez "
                "`include_geometry=true` pour superposer les couches sur une carte.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to understand forestry activity and protected land in a specific BC region.",
            role="user",
        ),
        Message(
            "Here's how to explore BC forestry data in three steps:\n\n"
            "**Step 1 — Active forest tenures:**\n"
            "Call `bc_get_forest_tenure` with `client_name='<company>'` or no filter to get all "
            "active tenure agreements. The `LICENCE_ID` field identifies each tenure; "
            "`CLIENT_NAME` shows the licence holder.\n\n"
            "**Step 2 — Recent cut blocks:**\n"
            "Call `bc_get_cut_blocks` with the same district or no filter to see harvesting activity. "
            "Compare cut blocks with tenures to identify where harvesting is active.\n\n"
            "**Step 3 — Protected areas:**\n"
            "Call `bc_get_protected_areas` (with `designation='PROVINCIAL PARK'` or no filter) "
            "to see what land is protected. Compare areas and tenure holders.\n\n"
            "Tip: Tenure data is static (24h cache). Add `include_geometry=true` "
            "to overlay layers on a map.",
            role="assistant",
        ),
    ]


@prompt
async def bc_explore_environment(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through environmental data exploration in BC.

    Chains bc_get_water_wells -> bc_get_local_parks -> bc_get_mining_tenure for a
    comprehensive environmental pressure analysis covering water, greenspace, and resource extraction.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comprendre les pressions environnementales dans une ville ou un aquifère "
                "en Colombie-Britannique.",
                role="user",
            ),
            Message(
                "Voici comment explorer les données environnementales en C.-B.:\n\n"
                "**Étape 1 — Puits d'eau souterraine:**\n"
                "Appelez `bc_get_water_wells` avec `city='<nom>'` ou `aquifer_id=<id>`. "
                "ATTENTION: sans filtre, cette couche contient 130 000+ enregistrements. "
                "Utilisez toujours `city` ou `aquifer_id`. Ajoutez `well_class='DRINKING WATER'` "
                "pour les puits d'eau potable uniquement.\n\n"
                "**Étape 2 — Espaces verts locaux:**\n"
                "Appelez `bc_get_local_parks` avec `municipality='<nom>'` pour voir les parcs "
                "municipaux et régionaux. Ajoutez `include_geometry=true` pour cartographier "
                "les emplacements et superposer avec les puits.\n\n"
                "**Étape 3 — Tenures minières à proximité:**\n"
                "Appelez `bc_get_mining_tenure` avec `tenure_type='mineral'` ou `tenure_type='placer'` "
                "pour les réclamations minérales à proximité. Utilisez `owner_name` pour filtrer "
                "par société minière spécifique.\n\n"
                "Conseil: Comparez les emplacements des puits, des parcs et des tenures minières "
                "pour identifier les conflits potentiels d'utilisation des terres.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to understand environmental pressures in a BC city or aquifer.",
            role="user",
        ),
        Message(
            "Here's how to explore BC environmental data:\n\n"
            "**Step 1 — Groundwater wells:**\n"
            "Call `bc_get_water_wells` with `city='<name>'` or `aquifer_id=<id>`. "
            "WARNING: without a filter, this layer has 130,000+ records. "
            "Always provide `city` or `aquifer_id`. Add `well_class='DRINKING WATER'` "
            "for drinking water wells only.\n\n"
            "**Step 2 — Local greenspace:**\n"
            "Call `bc_get_local_parks` with `municipality='<name>'` to see municipal and "
            "regional parks. Add `include_geometry=true` to map locations and overlay with wells.\n\n"
            "**Step 3 — Nearby mining tenure:**\n"
            "Call `bc_get_mining_tenure` with `tenure_type='mineral'` or `tenure_type='placer'` "
            "for nearby mineral claims. Use `owner_name` to filter by a specific mining company.\n\n"
            "Tip: Compare well, park, and mining tenure locations to identify potential "
            "land-use conflicts.",
            role="assistant",
        ),
    ]


@prompt
async def bc_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search BC Data Catalogue and explore a dataset in depth.

    Use for: one-shot BC dataset discovery via CKAN search, then deep-dive to WFS queryable layers.
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le Catalogue de données de la C.-B.:\n\n"
            "1. Appelez `bc_search_datasets` avec `q='<mot-clé>'` (ex. `q='wildfire'`, "
            "`q='water quality'`). Utilisez `fq='organization:<slug-org>'` pour filtrer "
            "par ministère.\n\n"
            "2. Pour en savoir plus sur un jeu de données, appelez `bc_get_dataset_details` "
            "avec le `id` retourné. Vérifiez le champ `queryable_via_wfs` — si `true`, "
            "vous pouvez interroger directement les entités géospatiales.\n\n"
            "3. Si `queryable_via_wfs=true`, utilisez `bc_query_features` avec `object_name` "
            "(ex. `WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW`) et un filtre CQL optionnel. "
            "Si `queryable_via_wfs=false`, le jeu de données est un fichier — utilisez le lien "
            "de ressource direct.\n\n"
            "Ressource de référence: consultez `docs://bc/wfs-query-guide` pour la syntaxe CQL "
            "complète et des exemples copiables."
        )
    return (
        "To search for data in the BC Data Catalogue:\n\n"
        "1. Call `bc_search_datasets` with `q='<keyword>'` (e.g. `q='wildfire'`, "
        "`q='water quality'`). Use `fq='organization:<org-slug>'` to filter by ministry.\n\n"
        "2. To learn more about a dataset, call `bc_get_dataset_details` with the returned `id`. "
        "Check the `queryable_via_wfs` field — if `true`, you can query geospatial features directly.\n\n"
        "3. If `queryable_via_wfs=true`, use `bc_query_features` with the `object_name` "
        "(e.g. `WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW`) and an optional CQL filter. "
        "If `queryable_via_wfs=false`, the dataset is a file — use the resource link directly.\n\n"
        "Reference: see `docs://bc/wfs-query-guide` for full CQL syntax and copyable examples."
    )


@prompt
async def bc_check_water_quality(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve BC groundwater well records for a city or aquifer.

    Use for: quick lookup of BC water wells by city, well class, or aquifer ID.
    Always provide at least one filter — the full layer has 130,000+ records.
    """
    if lang == "fr":
        return (
            "Pour récupérer des données sur les puits d'eau en C.-B., appelez "
            "`bc_get_water_wells` avec au moins l'un des filtres suivants:\n\n"
            "- `city='<nom>'` — ex. `city='Kelowna'`, `city='Prince George'`\n"
            "- `aquifer_id=<id>` — identifiant de l'aquifère du registre WELLS BC\n"
            "- `well_class='DRINKING WATER'` — puits d'eau potable uniquement "
            "(autres classes: 'IRRIGATION', 'INDUSTRIAL', 'MONITORING')\n\n"
            "IMPORTANT: sans filtre, cette couche contient 130 000+ enregistrements — "
            "une erreur INVALID_INPUT sera renvoyée. Fournissez toujours `city` ou `aquifer_id`.\n\n"
            "Champs clés dans la réponse: CITY, WELL_CLASS, AQUIFER_LITHOLOGY, DEPTH_WELL_DRILLED, "
            "WATER_DEPTH, YIELD_VALUE, ARTESIAN_FLOW."
        )
    return (
        "To retrieve BC groundwater well records, call `bc_get_water_wells` with at least one filter:\n\n"
        "- `city='<name>'` — e.g. `city='Kelowna'`, `city='Prince George'`\n"
        "- `aquifer_id=<id>` — aquifer identifier from the WELLS BC registry\n"
        "- `well_class='DRINKING WATER'` — drinking water wells only "
        "(other classes: 'IRRIGATION', 'INDUSTRIAL', 'MONITORING')\n\n"
        "IMPORTANT: without a filter, this layer has 130,000+ records — "
        "an INVALID_INPUT error will be returned. Always provide `city` or `aquifer_id`.\n\n"
        "Key fields in the response: CITY, WELL_CLASS, AQUIFER_LITHOLOGY, DEPTH_WELL_DRILLED, "
        "WATER_DEPTH, YIELD_VALUE, ARTESIAN_FLOW."
    )


@prompt
async def bc_wildfire_status_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to get current active wildfire status in BC.

    Use for: immediate wildfire situational awareness — current active fires, optionally
    filtered by status (Out of Control, Being Held, Under Control) or fire centre.
    """
    if lang == "fr":
        return (
            "Pour obtenir le statut actuel des feux de forêt actifs en C.-B., "
            "appelez `bc_get_active_fires`.\n\n"
            "Filtres optionnels:\n"
            "- `status='Out of Control'` — pour les feux les plus urgents uniquement\n"
            "- `status='Being Held'` — feux contenus mais non éteints\n"
            "- `status='Under Control'` — feux maîtrisés\n"
            "- `fire_centre='Kamloops'` — limiter à un centre des feux spécifique "
            "(centres: Kamloops, Coastal, Northwest, Prince George, Southeast, Cariboo)\n"
            "- `min_size=100` — feux de plus de 100 hectares\n\n"
            "Les données sont actualisées toutes les 5 minutes. "
            "Champs clés: FIRE_NUMBER, FIRE_STATUS, FIRE_CAUSE, CURRENT_SIZE, FIRE_CENTRE."
        )
    return (
        "To get current active wildfire status in BC, call `bc_get_active_fires`.\n\n"
        "Optional filters:\n"
        "- `status='Out of Control'` — for the most urgent fires only\n"
        "- `status='Being Held'` — contained but not extinguished\n"
        "- `status='Under Control'` — fires being managed\n"
        "- `fire_centre='Kamloops'` — limit to a specific fire centre "
        "(centres: Kamloops, Coastal, Northwest, Prince George, Southeast, Cariboo)\n"
        "- `min_size=100` — fires larger than 100 hectares\n\n"
        "Data refreshes every 5 minutes. "
        "Key fields: FIRE_NUMBER, FIRE_STATUS, FIRE_CAUSE, CURRENT_SIZE, FIRE_CENTRE."
    )
