"""Saskatchewan prompts — 6 bilingual prompts (3 guided + 3 quick lookups).

Guided workflows (list[Message]) — multi-step tool chaining:
  saskatchewan_explore_agriculture  — crop yields + grain elevators + mineral mines
  saskatchewan_explore_environment  — fire bans + historic wildfires + air quality
  saskatchewan_explore_water        — WSA gauging stations + WSA reservoirs

Quick lookups (str) — single-tool instructions:
  saskatchewan_quick_dataset_search   — geohub.saskatchewan.ca ArcGIS Hub catalogue search
  saskatchewan_fire_ban_status_now    — SPSA fire ban dispatch + empty=no-bans note
  saskatchewan_crop_yield_lookup      — provincial vs 5 crop regions

IMPORTANT: All prompts accept `lang: Literal["en", "fr"] = "en"` via Annotated.
ZERO-parameter resources are in resources.py — see CLAUDE.md rule.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


__all__ = [
    # Guided workflows (list[Message])
    "saskatchewan_explore_agriculture",
    "saskatchewan_explore_environment",
    "saskatchewan_explore_water",
    # Quick lookups (str)
    "saskatchewan_quick_dataset_search",
    "saskatchewan_fire_ban_status_now",
    "saskatchewan_crop_yield_lookup",
]


# ---------------------------------------------------------------------------
# Guided workflows — return list[Message] with at least user + assistant roles
# ---------------------------------------------------------------------------


@prompt
async def saskatchewan_explore_agriculture(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Saskatchewan agriculture and resource economy data exploration.

    Chains saskatchewan_get_crop_yields -> saskatchewan_get_grain_elevators ->
    saskatchewan_get_mineral_mines for a comprehensive picture of Saskatchewan's
    agriculture and natural resource sectors. Saskatchewan is Canada's largest
    producer of canola, durum wheat, lentils, and chickpeas, and holds ~1/3 of
    world potash reserves.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données agricoles et d'exploitation des ressources "
                "naturelles de la Saskatchewan — rendements des cultures, élévateurs à grain, "
                "et mines de minéraux.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données agricoles et minières de la "
                "Saskatchewan en trois étapes :\n\n"
                "**Étape 1 — Rendements estimés des cultures (par région) :**\n"
                "Appelez `saskatchewan_get_crop_yields` avec `region='provincial'` pour le "
                "résumé provincial (16 types de cultures : HRSW, Durum, Canola, Lentille, "
                "Pois, Pois chiche, Avoine, Orge, etc., en bu/acre). Pour des données "
                "régionales, utilisez `region='southeast'`, `'southwest'`, `'central'`, "
                "`'northeast'`, ou `'northwest'`. **Remarque :** Les rapports hebdomadaires "
                "de culture sont en format PDF uniquement — ce FeatureServer est le substitut "
                "lisible par machine. TTL 7 jours (données annuelles).\n\n"
                "**Étape 2 — Emplacements des élévateurs à grain (Saskatchewan) :**\n"
                "Appelez `saskatchewan_get_grain_elevators` pour les élévateurs de la "
                "Saskatchewan (filtre `PR='SK'` appliqué par défaut). Retourne station, "
                "chemin de fer (CN/CP/SHORTLINE), titulaire de licence, type d'élévateur "
                "(primaire/transformation), et capacité en tonnes. Filtrez par voie ferrée "
                "avec `railway='CN'`, `'CP'`, ou `'SHORTLINE'` si nécessaire.\n\n"
                "**Étape 3 — Mines de minéraux (potasse, uranium, hélium, charbon) :**\n"
                "Appelez `saskatchewan_get_mineral_mines` avec `mineral='potash'` pour les "
                "13 mines de potasse actives (la Saskatchewan détient ~1/3 des réserves "
                "mondiales — Mosaic, K+S Bethune, Nutrien). Utilisez `mineral='uranium'` "
                "pour les opérations du Bassin d'Athabasca (Cameco). Également disponibles : "
                "`'helium'` et `'coal'`. Retourne nom de la mine, compagnie, statut "
                "(actif/entretien/fermé), type de mine, et date d'ouverture.\n\n"
                "Conseil : Les données Petroleum FeatureServer (puits de pétrole et gaz) "
                "retournent HTTP 400 sur les requêtes ouvertes — utilisez "
                "`saskatchewan_search_datasets(query='petroleum')` pour la découverte. "
                "Consultez `docs://saskatchewan/agriculture-data-guide` pour les distinctions "
                "entre Crop_Production_2025 (limites spatiales uniquement) et les FS de "
                "rendements de culture (données réelles).",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Saskatchewan agriculture and natural resource economy data — "
            "crop yields, grain elevators, and mineral mines.",
            role="user",
        ),
        Message(
            "I'll guide you through Saskatchewan agriculture and mining data in three steps:\n\n"
            "**Step 1 — Estimated crop yields (by region):**\n"
            "Call `saskatchewan_get_crop_yields` with `region='provincial'` for the "
            "provincial summary (16 crop types: HRSW, Durum, Canola, Lentil, Pea, "
            "Chickpea, Oat, Barley, etc., in bu/acre). For regional breakdowns, use "
            "`region='southeast'`, `'southwest'`, `'central'`, `'northeast'`, or "
            "`'northwest'`. **Note:** Weekly crop reports are PDF-only — this FeatureServer "
            "is the machine-readable substitute. 7-day cache TTL (annual data).\n\n"
            "**Step 2 — Grain elevator locations (Saskatchewan):**\n"
            "Call `saskatchewan_get_grain_elevators` for Saskatchewan elevators (default "
            "`PR='SK'` filter applied). Returns station, railway (CN/CP/SHORTLINE), licensee, "
            "elevator type (primary/process), and capacity in tonnes. Filter by railway with "
            "`railway='CN'`, `'CP'`, or `'SHORTLINE'` if needed.\n\n"
            "**Step 3 — Mineral mines (potash, uranium, helium, coal):**\n"
            "Call `saskatchewan_get_mineral_mines` with `mineral='potash'` for the 13 "
            "active potash mines (Saskatchewan holds ~1/3 of world reserves — Mosaic, "
            "K+S Bethune, Nutrien). Use `mineral='uranium'` for Athabasca Basin operations "
            "(Cameco). Also available: `'helium'` and `'coal'`. Returns mine name, company, "
            "status (operating/care & maintenance/closed), mine type, and date opened.\n\n"
            "Tip: Petroleum FeatureServer (oil & gas wells) returns HTTP 400 on open queries "
            "— use `saskatchewan_search_datasets(query='petroleum')` for discovery instead. "
            "See `docs://saskatchewan/agriculture-data-guide` for the Crop_Production_2025 "
            "(boundary-only) vs yield estimate FeatureServer distinction.",
            role="assistant",
        ),
    ]


@prompt
async def saskatchewan_explore_environment(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Saskatchewan environment, wildfire, and air quality data.

    Chains saskatchewan_get_fire_bans -> saskatchewan_get_historic_wildfires ->
    saskatchewan_get_air_quality for a comprehensive Saskatchewan environment and
    wildfire situational awareness picture. Fire ban data comes from the separate
    SPSA ArcGIS REST server (not the main Hub); air quality and wildfire history
    are on the primary Saskatchewan GeoHub.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données environnementales de la Saskatchewan — "
                "interdictions de feu, historique des incendies de forêt, et qualité de l'air.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données environnementales de la "
                "Saskatchewan en trois étapes :\n\n"
                "**Étape 1 — Statut d'interdiction de feu (temps réel) :**\n"
                "Appelez `saskatchewan_get_fire_bans` avec `ban_scope='urban'` (couche 0), "
                "`'rural'` (couche 2), `'provincial'` (couche 3), ou `'parks'` (couche 8). "
                "**Remarque :** Une réponse vide `{features:[]}` est normale hors-saison — "
                "aucune interdiction active. **Important :** Ce service est sur le serveur "
                "SPSA séparé (`gis.saskatchewan.ca/egis`) — PAS sur le GeoHub principal. "
                "TTL 5 min (données d'urgence en temps réel).\n\n"
                "**Étape 2 — Limites historiques des incendies de forêt :**\n"
                "Appelez `saskatchewan_get_historic_wildfires` avec les filtres optionnels "
                "`year=<année>` (ex. `year=2020`) et `cause='Lightning'`, `'Human'`, ou "
                "`'Unknown'`. Retourne le nom du feu, l'année, la cause, les superficies "
                "en hectares, le statut, et les dates de début/extinction. Les deux filtres "
                "se composent si fournis ensemble. TTL 24 h.\n\n"
                "**Étape 3 — Qualité de l'air ambiant (lecture horaire actuelle) :**\n"
                "Appelez `saskatchewan_get_air_quality` avec le filtre optionnel "
                "`community='Regina'` (ou `'Saskatoon'`, `'Prince Albert'`, `'Estevan'`, "
                "`'Swift Current'`, `'Buffalo Narrows'`). Retourne PM2.5, NO2, O3, SO2, "
                "CO, H2S, et un champ AQHI liant à weather.gc.ca (pas une valeur numérique "
                "directe). TTL 15 min (données horaires).\n\n"
                "Conseil : Consultez `data://saskatchewan/crop-regions` pour les noms des "
                "5 régions de rapport et leurs cultures caractéristiques. Utilisez "
                "`docs://saskatchewan/portal-guide` pour comprendre l'architecture "
                "multi-organisation (GeoHub principal + SPSA).",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Saskatchewan environment data — fire bans, historic "
            "wildfires, and air quality.",
            role="user",
        ),
        Message(
            "I'll guide you through Saskatchewan environment data in three steps:\n\n"
            "**Step 1 — Fire ban status (real-time):**\n"
            "Call `saskatchewan_get_fire_bans` with `ban_scope='urban'` (layer 0), "
            "`'rural'` (layer 2), `'provincial'` (layer 3), or `'parks'` (layer 8). "
            "**Note:** An empty response `{features:[]}` is normal off-season — "
            "no active bans. **Important:** This service is on the separate SPSA server "
            "(`gis.saskatchewan.ca/egis`) — NOT the main GeoHub. 5-min cache TTL "
            "(live emergency data).\n\n"
            "**Step 2 — Historic wildfire boundaries:**\n"
            "Call `saskatchewan_get_historic_wildfires` with optional `year=<year>` "
            "(e.g. `year=2020`) and `cause='Lightning'`, `'Human'`, or `'Unknown'`. "
            "Returns fire name, year, cause, area in hectares, status, and start/out dates. "
            "Both filters compose when provided together. 24h cache TTL.\n\n"
            "**Step 3 — Ambient air quality (current hourly readings):**\n"
            "Call `saskatchewan_get_air_quality` with optional `community='Regina'` "
            "(or `'Saskatoon'`, `'Prince Albert'`, `'Estevan'`, `'Swift Current'`, "
            "`'Buffalo Narrows'`). Returns PM2.5, NO2, O3, SO2, CO, H2S, and an AQHI "
            "field linking to weather.gc.ca (not a direct numeric value). 15-min cache TTL "
            "(hourly data).\n\n"
            "Tip: See `data://saskatchewan/crop-regions` for the 5 crop reporting region "
            "names and their signature crops. Use `docs://saskatchewan/portal-guide` to "
            "understand the multi-org architecture (primary GeoHub + SPSA).",
            role="assistant",
        ),
    ]


@prompt
async def saskatchewan_explore_water(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Saskatchewan Water Security Agency (WSA) data exploration.

    Chains saskatchewan_get_wsa_stations -> saskatchewan_get_wsa_reservoirs for a
    comprehensive picture of Saskatchewan's water infrastructure. Both tools use the
    separate WSA ArcGIS org (7MBdlVpjqbfBhQer / services1.arcgis.com), NOT the
    primary Saskatchewan GeoHub org. WSA stations include HyperLink_Graph URLs
    to live hourly hydrographs at wsask.ca.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données d'infrastructure hydrique de la Saskatchewan "
                "— stations de jaugeage hydrométrique WSA et réservoirs.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers les données de l'Agence de sécurité de l'eau "
                "(WSA) de la Saskatchewan en deux étapes :\n\n"
                "**Architecture WSA :** Les deux outils utilisent l'org ArcGIS séparé de la "
                "WSA (`services1.arcgis.com/7MBdlVpjqbfBhQer/`), PAS l'org GeoHub principal "
                "(`services3.arcgis.com/zcv98lgAl8xQ04cW/`). Le champ `api_name` dans "
                "l'enveloppe `_meta` reflétera `'saskatchewan-wsa'`.\n\n"
                "**Étape 1 — Stations de jaugeage hydrométrique WSA :**\n"
                "Appelez `saskatchewan_get_wsa_stations` pour les emplacements des stations "
                "avec Station_Number, Station_Name, Major_Basin, Station_Class, Operated_By, "
                "et HyperLink_Graph (URL vers le hydrographe horaire en direct à "
                "`wsask.ca/hydrographs/{numéro}-hrly.html`). Filtrez par bassin avec "
                "`basin='Assiniboine'`, `'North Saskatchewan'`, `'Qu Appelle'`, "
                "`'Churchill'`, ou `'Athabasca'`. Consultez "
                "`data://saskatchewan/major-basins` pour la liste complète des bassins.\n\n"
                "**Étape 2 — Réservoirs WSA :**\n"
                "Appelez `saskatchewan_get_wsa_reservoirs` pour les réservoirs et barrages "
                "avec Reservoir_Name, Dam_Name, Imagery_Date, et Water_Level_MASL "
                "(mètres au-dessus du niveau de la mer). **Important :** Les données "
                "sont à la couche 26 du FeatureServer WSA_Reservoirs — PAS la couche 0 "
                "(qui est vide). Cela est géré automatiquement par l'outil. TTL 24 h.\n\n"
                "Conseil : Les lectures numériques de niveau d'eau en temps réel sont dans "
                "la base de données HYDAT d'ECCC (`wateroffice.ec.gc.ca`). Le champ "
                "HyperLink_Graph dans les stations WSA pointe vers les hydrographes "
                "wsask.ca pour les lectures horaires directement.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Saskatchewan water infrastructure data — WSA hydrometric "
            "gauging stations and reservoirs.",
            role="user",
        ),
        Message(
            "I'll guide you through Water Security Agency (WSA) Saskatchewan data in "
            "two steps:\n\n"
            "**WSA Architecture:** Both tools use the separate WSA ArcGIS org "
            "(`services1.arcgis.com/7MBdlVpjqbfBhQer/`), NOT the primary GeoHub org "
            "(`services3.arcgis.com/zcv98lgAl8xQ04cW/`). The `api_name` field in the "
            "`_meta` envelope will reflect `'saskatchewan-wsa'`.\n\n"
            "**Step 1 — WSA Hydrometric Gauging Stations:**\n"
            "Call `saskatchewan_get_wsa_stations` for station locations with "
            "Station_Number, Station_Name, Major_Basin, Station_Class, Operated_By, and "
            "HyperLink_Graph (a URL to the live hourly hydrograph at "
            "`wsask.ca/hydrographs/{number}-hrly.html`). Filter by basin with "
            "`basin='Assiniboine'`, `'North Saskatchewan'`, `'Qu Appelle'`, `'Churchill'`, "
            "or `'Athabasca'`. See `data://saskatchewan/major-basins` for the full basin "
            "list with WSA monitoring flags.\n\n"
            "**Step 2 — WSA Reservoirs:**\n"
            "Call `saskatchewan_get_wsa_reservoirs` for reservoir and dam data with "
            "Reservoir_Name, Dam_Name, Imagery_Date, and Water_Level_MASL (metres above "
            "sea level). **Important:** Data is at layer 26 of the WSA_Reservoirs "
            "FeatureServer — NOT layer 0 (which is empty). This is handled automatically "
            "by the tool. 24h cache TTL.\n\n"
            "Tip: Real-time numeric water level readings are in ECCC's HYDAT database "
            "(`wateroffice.ec.gc.ca`). The HyperLink_Graph field in WSA stations links "
            "to wsask.ca hydrographs for direct hourly readings.",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Quick lookups — return str with specific tool + parameter instructions
# ---------------------------------------------------------------------------


@prompt
async def saskatchewan_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue.

    Use for: one-shot Saskatchewan open data discovery — search the ArcGIS Hub catalog,
    inspect dataset details, and query records from FeatureServers or file resources.
    Note: data.saskatchewan.ca does not exist; geohub.saskatchewan.ca is the only
    provincial machine-readable open data portal.
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le géoportail Saskatchewan "
            "(geohub.saskatchewan.ca — ArcGIS Hub, org `zcv98lgAl8xQ04cW`, 181+ éléments) :\n\n"
            "1. Appelez `saskatchewan_search_datasets` avec `query='<mot-clé>'` "
            "(p. ex. `query='wildfire'`, `query='crop yields'`, `query='potash'`). "
            "**Remarque :** Le portail Saskatchewan utilise ArcGIS Hub Search API — "
            "il n'existe PAS de `data.saskatchewan.ca` CKAN. "
            "Ajoutez `category='<catégorie>'` pour filtrer par thème (ex. `/Categories/Agriculture`).\n\n"
            "2. Pour inspecter un jeu de données, appelez `saskatchewan_get_dataset_details` "
            "avec l'`id` (GUID) retourné. Vérifiez le champ `resources` pour l'URL du "
            "FeatureServer, les liens de téléchargement et les métadonnées.\n\n"
            "3. Pour récupérer des données, appelez `saskatchewan_query_dataset` avec "
            "l'URL du FeatureServer. Le routeur auto-détecte : FeatureServer ArcGIS "
            "(préféré) → `arcgis_hub.query_feature_service`, ou téléchargement CSV/GeoJSON/XLSX "
            "→ `fetch_and_parse`. Les ressources PDF/ZIP/KML retournent les métadonnées uniquement.\n\n"
            "**Conseil :** Les services de données WSA (hydrométrie, réservoirs) et les "
            "données SPSA (interdictions de feu) vivent sur des serveurs séparés — "
            "ils ne sont PAS découvrables via la recherche Hub. Utilisez les outils "
            "curés dédiés (`saskatchewan_get_wsa_stations`, `saskatchewan_get_fire_bans`). "
            "Consultez `docs://saskatchewan/portal-guide` pour l'architecture complète."
        )
    return (
        "To search for data in the Saskatchewan geoportal "
        "(geohub.saskatchewan.ca — ArcGIS Hub, org `zcv98lgAl8xQ04cW`, 181+ items):\n\n"
        "1. Call `saskatchewan_search_datasets` with `query='<keyword>'` "
        "(e.g. `query='wildfire'`, `query='crop yields'`, `query='potash'`). "
        "**Note:** Saskatchewan's geoportal uses ArcGIS Hub Search API — "
        "there is NO `data.saskatchewan.ca` CKAN portal. "
        "Add `category='<category>'` to filter by theme (e.g. `/Categories/Agriculture`).\n\n"
        "2. To inspect a dataset, call `saskatchewan_get_dataset_details` with the `id` "
        "(GUID) returned. Check the `resources` field for the FeatureServer URL, "
        "download links, and metadata.\n\n"
        "3. To fetch data records, call `saskatchewan_query_dataset` with the FeatureServer "
        "URL. The router auto-detects: ArcGIS FeatureServer (preferred) → "
        "`arcgis_hub.query_feature_service`, or CSV/GeoJSON/XLSX download → `fetch_and_parse`. "
        "PDF/ZIP/KML resources return metadata only.\n\n"
        "**Tip:** WSA water data (hydrometric stations, reservoirs) and SPSA fire ban data "
        "live on separate servers — they are NOT discoverable via Hub search. "
        "Use the dedicated curated tools (`saskatchewan_get_wsa_stations`, "
        "`saskatchewan_get_fire_bans`). See `docs://saskatchewan/portal-guide` "
        "for the full multi-org architecture."
    )


@prompt
async def saskatchewan_fire_ban_status_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Saskatchewan fire ban status from SPSA.

    Use for: quick fire ban situational awareness — dispatches to the SPSA
    Public_Fire_Ban FeatureServer by ban_scope (urban/rural/provincial/parks).
    Note: SPSA data is on a separate ArcGIS REST server, not the main GeoHub.
    An empty response means no active bans (normal off-season state).
    """
    if lang == "fr":
        return (
            "Pour vérifier le statut d'interdiction de feu actuel en Saskatchewan "
            "(source : SPSA Public_Fire_Ban FeatureServer, TTL 5 min) :\n\n"
            "**Serveur séparé :** Les données SPSA sont sur `gis.saskatchewan.ca/egis/` "
            "— PAS sur le GeoHub principal. Ne cherchez pas ces données via "
            "`saskatchewan_search_datasets`.\n\n"
            "Appelez `saskatchewan_get_fire_bans` avec le paramètre `ban_scope` :\n"
            "- `ban_scope='urban'` (défaut) — Couche 0 : Interdictions dans les "
            "municipalités urbaines\n"
            "- `ban_scope='rural'` — Couche 2 : Interdictions dans les municipalités "
            "rurales (zones d'amélioration rurale)\n"
            "- `ban_scope='provincial'` — Couche 3 : Interdictions provinciales à grande échelle\n"
            "- `ban_scope='parks'` — Couche 8 : Interdictions dans les parcs provinciaux\n\n"
            "**Résultat vide = aucune interdiction active :** Un résultat `{features:[]}` "
            "est la réponse normale hors-saison — ce N'est PAS une erreur.\n\n"
            "Appelez plusieurs fois avec différents `ban_scope` pour une image complète "
            "(par exemple, vérifiez `'urban'` ET `'rural'` ET `'provincial'` séparément)."
        )
    return (
        "To check current Saskatchewan fire ban status "
        "(source: SPSA Public_Fire_Ban FeatureServer, 5-min cache TTL):\n\n"
        "**Separate server:** SPSA data is on `gis.saskatchewan.ca/egis/` "
        "— NOT on the main GeoHub. Do not try to find this data via "
        "`saskatchewan_search_datasets`.\n\n"
        "Call `saskatchewan_get_fire_bans` with the `ban_scope` parameter:\n"
        "- `ban_scope='urban'` (default) — Layer 0: Bans in urban municipalities\n"
        "- `ban_scope='rural'` — Layer 2: Bans in rural municipalities (rural "
        "improvement districts)\n"
        "- `ban_scope='provincial'` — Layer 3: Province-wide fire restrictions\n"
        "- `ban_scope='parks'` — Layer 8: Bans within provincial parks\n\n"
        "**Empty result = no active bans:** A `{features:[]}` result is the normal "
        "off-season response — this is NOT an error.\n\n"
        "Call multiple times with different `ban_scope` values for a complete picture "
        "(e.g., check `'urban'` AND `'rural'` AND `'provincial'` separately)."
    )


@prompt
async def saskatchewan_crop_yield_lookup(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to look up Saskatchewan estimated crop yields by region.

    Use for: single-tool crop yield lookup — retrieves estimated bu/acre yields
    for 16 crop types at provincial or regional level. Clarifies provincial vs 5
    regional dispatch and notes that weekly PDF crop reports are not machine-readable.
    """
    if lang == "fr":
        return (
            "Pour consulter les rendements estimés des cultures en Saskatchewan "
            "(source : FeatureServers Provincial_Estimated_Crop_Yields, TTL 7 jours) :\n\n"
            "Appelez `saskatchewan_get_crop_yields` avec le paramètre `region` :\n"
            "- `region='provincial'` (défaut) — Résumé provincial combiné de toutes les régions\n"
            "- `region='southeast'` — Région de déclaration du Sud-Est\n"
            "- `region='southwest'` — Région de déclaration du Sud-Ouest\n"
            "- `region='central'` — Région de déclaration du Centre\n"
            "- `region='northeast'` — Région de déclaration du Nord-Est\n"
            "- `region='northwest'` — Région de déclaration du Nord-Ouest\n\n"
            "**16 types de cultures retournés :** HRSW (blé rouge de printemps), Durum, "
            "Avoine, Orge, Canola, Moutarde, Soja, Pois, Lentille, Pois chiche, "
            "Graine de canaris, Lin, Blé d'hiver, Seigle d'automne, Autre blé. "
            "Les rendements sont en bu/acre (boisseaux par acre).\n\n"
            "**Remarque importante :** Les rapports hebdomadaires de culture "
            "(publiés par Saskatchewan Agriculture) sont en format PDF uniquement "
            "— ils ne sont PAS lisibles par machine. Ce FeatureServer est le substitut "
            "officiel lisible par machine. "
            "Consultez `docs://saskatchewan/agriculture-data-guide` pour l'explication "
            "complète des sources de données agricoles."
        )
    return (
        "To look up Saskatchewan estimated crop yields "
        "(source: Provincial_Estimated_Crop_Yields FeatureServers, 7-day cache TTL):\n\n"
        "Call `saskatchewan_get_crop_yields` with the `region` parameter:\n"
        "- `region='provincial'` (default) — Combined provincial summary across all regions\n"
        "- `region='southeast'` — Southeast crop reporting region\n"
        "- `region='southwest'` — Southwest crop reporting region\n"
        "- `region='central'` — Central crop reporting region\n"
        "- `region='northeast'` — Northeast crop reporting region\n"
        "- `region='northwest'` — Northwest crop reporting region\n\n"
        "**16 crop types returned:** HRSW (hard red spring wheat), Durum, Oat, Barley, "
        "Canola, Mustard, Soybean, Pea, Lentil, Chickpea, Canary_seed, Flax, "
        "Winter_wheat, Fall_rye, Other_wheat. Yields are in bu/acre (bushels per acre).\n\n"
        "**Important note:** Weekly Saskatchewan crop reports (published by Saskatchewan "
        "Agriculture) are PDF-only — they are NOT machine-readable. This FeatureServer "
        "is the official machine-readable substitute. "
        "See `docs://saskatchewan/agriculture-data-guide` for the full agriculture "
        "data source guide."
    )
