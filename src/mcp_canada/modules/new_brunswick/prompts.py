"""New Brunswick module prompts — 6 bilingual @prompt functions for the MCP server.

All prompts use standalone @prompt from fastmcp.prompts (NEVER @mcp.prompt).
All prompts include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en".
All prompts use the "nb_" prefix.

Every nb_-prefixed tool name mentioned below is a member of
`constants.ALL_NB_TOOL_NAMES` (the 22-tool manifest locked in 21-01 after the
Task 2 discovery-surface checkpoint). Two tools this module's earlier research
curated — mineral occurrences and provincial parks — dropped to the long tail
under that checkpoint (option-a): they are reachable ONLY through
`nb_query_geonb_layer`, never through a dedicated `nb_get_*` tool, so no
prompt below names either as a standalone tool.

Guided workflows (list[Message]) — multi-step tool chaining:
  nb_flood_risk_assessment  — civic addresses (location resolution, G4) + flood hazard index
                              + historical floods + wetlands
  nb_crown_land_report      — Crown land + GeoNB layer discovery + long-tail forestry/mineral query
  nb_property_lookup        — parcels + civic addresses + NB911 community boundary via GeoNB

Quick lookups (str) — single-tool instructions:
  nb_quick_dataset_search      — guide nb_search_datasets (federal CKAN, organization:nb-scoped)
  nb_health_facility_finder    — guide nb_get_health_facilities (facility_type dispatch)
  nb_bilingual_dataset_lookup  — guide nb_search_datasets/nb_get_dataset_details with lang='fr' (D-12)
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


__all__ = [
    # Guided workflows (list[Message])
    "nb_flood_risk_assessment",
    "nb_crown_land_report",
    "nb_property_lookup",
    # Quick lookups (str)
    "nb_quick_dataset_search",
    "nb_health_facility_finder",
    "nb_bilingual_dataset_lookup",
]


# ---------------------------------------------------------------------------
# Guided workflows — return list[Message] with at least user + assistant roles
# ---------------------------------------------------------------------------


@prompt
async def nb_flood_risk_assessment(
    location: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a New Brunswick flood risk assessment (the province's signature domain).

    Chains nb_get_civic_addresses (location -> point/county, G4) -> nb_get_flood_hazard_areas
    -> nb_get_historical_floods -> nb_get_wetlands for a comprehensive flood-risk picture
    along the Saint John River and its tributaries. No flood tool accepts a place name —
    they are filtered by source map sheet, historical event and wetland class/status
    respectively, never by location. All data from geonb.snb.ca (bare ArcGIS Server).
    """
    if lang == "fr":
        return [
            Message(
                f"Je veux évaluer le risque d'inondation près de « {location or '(non précisé)'} » "
                "au Nouveau-Brunswick — zone de risque d'inondation, limites historiques des "
                "inondations, milieux humides à proximité et adresses civiques touchées.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers l'évaluation du risque d'inondation du "
                "Nouveau-Brunswick en quatre étapes. **Aucun outil de couche d'inondation "
                "n'accepte un nom de lieu comme argument** — les outils d'indice de risque "
                "d'inondation, de limites historiques et de milieux humides ci-dessous sont "
                "filtrés par feuille de carte source, événement historique et classe/statut "
                "de milieu humide respectivement, jamais par emplacement. Résolvez d'abord "
                "l'emplacement.\n\n"
                "**Étape 1 — Résoudre l'emplacement en un point et un comté :**\n"
                "Appelez `nb_get_civic_addresses` avec `community=` et/ou `street=` dérivés de "
                f"« {location or '(non précisé)'} » — chaque résultat porte `LATITUDE`/"
                "`LONGITUDE` (le point résolu) ainsi que `COUNTY` et `PID`. C'est le seul "
                "chemin de géocodage offert par ce module ; passez la valeur de localisation "
                "uniquement comme argument d'outil (jamais comme fragment de clause WHERE brut) "
                "— l'outil construit le filtre côté serveur.\n\n"
                "**Étape 2 — Indice de risque d'inondation :**\n"
                "Appelez `nb_get_flood_hazard_areas` (source : GeoNB_ENV_FloodHazardIndex, "
                "couche 0, 269 polygones), en option avec `sheet=` si vous connaissez le "
                "numéro de feuille de carte source pertinent. Citez toujours les champs "
                "`Technical_` et `Sheet_Numb` dans votre rapport — ils identifient la feuille "
                "de carte source de l'organisme de réglementation, pas un simple attribut "
                "décoratif.\n\n"
                "**Étape 3 — Limites historiques des inondations :**\n"
                "Appelez `nb_get_historical_floods` (source : GeoNB_ENV_Historical_Floods — "
                "couche 0 pour les événements de 2008/2018, couche 8 pour l'événement de 1973). "
                "Retourne `ID`, `KEY`, `FEATURE`, `SOURCE`, `LIMIT`.\n\n"
                "**Étape 4 — Milieux humides à proximité (filtre obligatoire) :**\n"
                "Appelez `nb_get_wetlands` avec un filtre `wetland_class=` ou `status=` — "
                "cette couche compte 163 206 polygones et REJETTE un appel non filtré avant "
                "tout appel réseau (T-21-03).\n\n"
                "Conseil : Consultez `docs://nb/geonb-query-guide` pour la syntaxe WHERE et "
                "`template://nb/flood-risk-report` pour structurer votre rapport final.",
                role="assistant",
            ),
        ]
    return [
        Message(
            f"I want to assess flood risk near '{location or '(unspecified)'}' in New "
            "Brunswick — flood hazard zone, historical flood limits, nearby wetlands, and "
            "affected civic addresses.",
            role="user",
        ),
        Message(
            "I'll guide you through a New Brunswick flood risk assessment in four steps. "
            "**No flood-layer tool accepts a place name as an argument** — the flood hazard, "
            "historical flood and wetland tools below are filtered by source map sheet, "
            "historical event and wetland class/status respectively, never by location. "
            "Resolve the location first.\n\n"
            "**Step 1 — Resolve the location to a point and county:**\n"
            "Call `nb_get_civic_addresses` with `community=` and/or `street=` derived from "
            f"'{location or '(unspecified)'}' — each result carries `LATITUDE`/`LONGITUDE` "
            "(the resolved point) plus `COUNTY` and `PID`. This is the only geocoding path "
            "this module offers; pass the location value only as a tool argument (never as "
            "a raw WHERE clause fragment) — the tool builds the filter server-side.\n\n"
            "**Step 2 — Flood hazard index:**\n"
            "Call `nb_get_flood_hazard_areas` (source: GeoNB_ENV_FloodHazardIndex, layer 0, "
            "269 polygons), optionally with `sheet=` if you know the relevant source map "
            "sheet number. Always cite the `Technical_` and `Sheet_Numb` fields in your "
            "report — they identify the regulator's source map sheet, not a decorative "
            "attribute.\n\n"
            "**Step 3 — Historical flood limits:**\n"
            "Call `nb_get_historical_floods` (source: GeoNB_ENV_Historical_Floods — layer 0 "
            "for the 2008/2018 events, layer 8 for the 1973 event). Returns `ID`, `KEY`, "
            "`FEATURE`, `SOURCE`, `LIMIT`.\n\n"
            "**Step 4 — Nearby wetlands (filter required):**\n"
            "Call `nb_get_wetlands` with a `wetland_class=` or `status=` filter — this layer "
            "holds 163,206 polygons and REJECTS an unfiltered call before any network call "
            "(T-21-03).\n\n"
            "Tip: See `docs://nb/geonb-query-guide` for WHERE-clause syntax and "
            "`template://nb/flood-risk-report` to structure your final report.",
            role="assistant",
        ),
    ]


@prompt
async def nb_crown_land_report(
    county: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a New Brunswick Crown land and forestry report.

    Chains nb_get_crown_land -> nb_get_geonb_service_layers -> nb_query_geonb_layer
    for Crown land parcels plus the un-curated mineral, forest and non-forest long
    tail (GeoNB_DNR_MineralOccurrences / GeoNB_DNR_Forest / GeoNB_DNR_NonForest —
    reachable only through nb_query_geonb_layer since the 21-01 checkpoint dropped
    their dedicated curated tools to hold the 22-tool budget).
    """
    if lang == "fr":
        return [
            Message(
                f"Je veux un rapport sur les terres de la Couronne et la foresterie pour "
                f"« {county or '(comté non précisé)'} » au Nouveau-Brunswick — parcelles, "
                "occurrences minérales et données forestières.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers un rapport sur les terres de la Couronne et "
                "la foresterie du Nouveau-Brunswick en trois étapes :\n\n"
                "**Étape 1 — Parcelles de terres de la Couronne :**\n"
                "Appelez `nb_get_crown_land` (optionnel : `holder=<code entier>` si vous "
                "connaissez déjà un code). **Avertissement important :** le champ `HOLDER` "
                "est un CODE ENTIER brut, sans domaine de correspondance exposé par le "
                "serveur — ne le signalez JAMAIS comme un nom de personne ou d'organisation.\n\n"
                "**Étape 2 — Découvrir la couche des occurrences minérales :**\n"
                "Appelez `nb_get_geonb_service_layers` avec "
                "`service_name='GeoNB_DNR_MineralOccurrences'` pour confirmer l'identifiant "
                "de couche (couche 0, service `Mineral`) avant de l'interroger — les "
                "identifiants de couche GeoNB ne sont PAS devinables.\n\n"
                "**Étape 3 — Interroger les occurrences minérales et la foresterie (longue "
                "traîne) :**\n"
                "Appelez `nb_query_geonb_layer` avec `service_name='GeoNB_DNR_MineralOccurrences'`, "
                "`layer_id=0` pour les occurrences de minerai (nom, matière première, "
                "coordonnées). Répétez avec `service_name='GeoNB_DNR_Forest'` ou "
                "`'GeoNB_DNR_NonForest'` pour les données forestières — ces deux services ne "
                "disposent d'aucun outil dédié depuis la décision de bilan du 21-01 (option-a) "
                "et ne sont accessibles que via `nb_query_geonb_layer`.\n\n"
                "Conseil : Consultez `data://nb/geonb-services` pour le catalogue complet des "
                "62 services GeoNB avec leurs identifiants de couche cités et leurs raisons "
                "d'exclusion.",
                role="assistant",
            ),
        ]
    return [
        Message(
            f"I want a Crown land and forestry report for "
            f"'{county or '(county unspecified)'}' in New Brunswick — parcels, mineral "
            "occurrences, and forestry data.",
            role="user",
        ),
        Message(
            "I'll guide you through a New Brunswick Crown land and forestry report in "
            "three steps:\n\n"
            "**Step 1 — Crown land parcels:**\n"
            "Call `nb_get_crown_land` (optional: `holder=<integer code>` if you already have "
            "one). **Important warning:** the `HOLDER` field is a raw INTEGER CODE with no "
            "server-exposed lookup domain — NEVER report it as a person or organization "
            "name.\n\n"
            "**Step 2 — Discover the mineral occurrences layer:**\n"
            "Call `nb_get_geonb_service_layers` with "
            "`service_name='GeoNB_DNR_MineralOccurrences'` to confirm the layer id "
            "(layer 0, service `Mineral`) before querying it — GeoNB layer ids are NOT "
            "guessable.\n\n"
            "**Step 3 — Query mineral occurrences and forestry (long tail):**\n"
            "Call `nb_query_geonb_layer` with `service_name='GeoNB_DNR_MineralOccurrences'`, "
            "`layer_id=0` for ore occurrences (name, commodity, coordinates). Repeat with "
            "`service_name='GeoNB_DNR_Forest'` or `'GeoNB_DNR_NonForest'` for forestry data — "
            "neither service has a dedicated tool since the 21-01 checkpoint decision "
            "(option-a); both are reachable only through `nb_query_geonb_layer`.\n\n"
            "Tip: See `data://nb/geonb-services` for the full 62-service GeoNB catalogue "
            "with cited layer ids and exclusion reasons.",
            role="assistant",
        ),
    ]


@prompt
async def nb_property_lookup(
    pid: str = "",
    civic_address: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a New Brunswick property/parcel and civic address lookup.

    Chains nb_get_parcels -> nb_get_civic_addresses -> nb_get_geonb_service_layers ->
    nb_query_geonb_layer (against GeoNB_DPS_NB911_Communities) to resolve parcels,
    addresses, and the community boundary they sit inside.
    """
    if lang == "fr":
        return [
            Message(
                f"Je veux rechercher la propriété « {pid or '(PID non précisé)'} » ou "
                f"l'adresse civique « {civic_address or '(adresse non précisée)'} » au "
                "Nouveau-Brunswick — parcelle, adresse civique et limite communautaire.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers une recherche de propriété et d'adresse "
                "civique du Nouveau-Brunswick en trois étapes :\n\n"
                "**Étape 1 — Parcelle par PID ou comté :**\n"
                "Appelez `nb_get_parcels` avec `pid=` ou `county=`. **Filtre obligatoire :** "
                "cette couche compte 604 520 lignes et rejette un appel non filtré avant "
                "tout appel réseau. Retourne `PID`, `COUNTY`, `Titles_Status`, "
                "`Gazette_Status`.\n\n"
                "**Étape 2 — Adresse civique par communauté/rue :**\n"
                "Appelez `nb_get_civic_addresses` avec `community=` et/ou `street=`. "
                "**Filtre obligatoire également :** cette couche compte 373 172 lignes.\n\n"
                "**Étape 3 — Limite de la communauté NB911 :**\n"
                "Appelez `nb_get_geonb_service_layers` avec "
                "`service_name='GeoNB_DPS_NB911_Communities'` pour confirmer l'identifiant "
                "de couche, puis `nb_query_geonb_layer` avec ce `service_name` et "
                "`layer_id` pour résoudre la limite communautaire — ce service n'a pas "
                "d'outil dédié (`nb_get_civic_addresses` est le choix DPS/SNB de plus "
                "grande valeur selon D-07).\n\n"
                "Conseil : Consultez `data://nb/counties` pour les 15 comtés du "
                "Nouveau-Brunswick et `docs://nb/geonb-query-guide` pour la syntaxe WHERE.",
                role="assistant",
            ),
        ]
    return [
        Message(
            f"I want to look up property '{pid or '(PID unspecified)'}' or civic address "
            f"'{civic_address or '(address unspecified)'}' in New Brunswick — parcel, "
            "civic address, and the community boundary it sits inside.",
            role="user",
        ),
        Message(
            "I'll guide you through a New Brunswick property and civic address lookup in "
            "three steps:\n\n"
            "**Step 1 — Parcel by PID or county:**\n"
            "Call `nb_get_parcels` with `pid=` or `county=`. **Filter required:** this "
            "layer holds 604,520 rows and rejects an unfiltered call before any network "
            "call. Returns `PID`, `COUNTY`, `Titles_Status`, `Gazette_Status`.\n\n"
            "**Step 2 — Civic address by community/street:**\n"
            "Call `nb_get_civic_addresses` with `community=` and/or `street=`. **Also "
            "filter-required:** this layer holds 373,172 rows.\n\n"
            "**Step 3 — NB911 community boundary:**\n"
            "Call `nb_get_geonb_service_layers` with "
            "`service_name='GeoNB_DPS_NB911_Communities'` to confirm the layer id, then "
            "`nb_query_geonb_layer` with that `service_name` and `layer_id` to resolve the "
            "community boundary — this service has no dedicated tool "
            "(`nb_get_civic_addresses` is the higher-value DPS/SNB pick per D-07).\n\n"
            "Tip: See `data://nb/counties` for New Brunswick's 15 counties and "
            "`docs://nb/geonb-query-guide` for WHERE-clause syntax.",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Quick lookups — return str with specific tool + parameter instructions
# ---------------------------------------------------------------------------


@prompt
async def nb_quick_dataset_search(
    query: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search New Brunswick's federal-CKAN catalogue (open.canada.ca).

    Use for: one-shot NB open data discovery — search the federal CKAN catalogue,
    already restricted server-side to Government of New Brunswick datasets. There is
    no organization parameter to widen the scope (T-21-04).
    """
    if lang == "fr":
        return (
            "Pour rechercher des données dans le catalogue fédéral CKAN du "
            "Nouveau-Brunswick (open.canada.ca, 221 jeux de données, restreint côté "
            "serveur à l'organisation du gouvernement du Nouveau-Brunswick) :\n\n"
            "Appelez `nb_search_datasets` avec `query='<mot-clé>'` "
            f"(vous avez fourni : {query!r})"
            " — par exemple `query='flood'`, `query='crown land'`, `query='schools'`. "
            "**Remarque :** les résultats sont déjà restreints au Nouveau-Brunswick — il "
            "n'existe aucun paramètre `organization` pour élargir la portée.\n\n"
            "Pour une géodonnée provinciale (GeoNB) ou un jeu de données provincial "
            "distinct sur gnb.socrata.com, utilisez plutôt `nb_list_geonb_services` ou "
            "`nb_search_gnb_socrata_datasets`. Consultez `docs://nb/portal-guide` pour "
            "l'architecture complète des trois surfaces de découverte."
        )
    return (
        "To search for data in New Brunswick's federal-CKAN catalogue (open.canada.ca, "
        "221 datasets, server-side restricted to Government of New Brunswick):\n\n"
        f"Call `nb_search_datasets` with `query='<keyword>'` (you provided: {query!r}) — "
        "e.g. `query='flood'`, `query='crown land'`, `query='schools'`. **Note:** results "
        "are already restricted to New Brunswick — there is no `organization` parameter "
        "to widen the scope.\n\n"
        "For provincial geospatial data (GeoNB) or a separate provincial dataset on "
        "gnb.socrata.com, use `nb_list_geonb_services` or "
        "`nb_search_gnb_socrata_datasets` instead. See `docs://nb/portal-guide` for the "
        "full three-surface discovery architecture."
    )


@prompt
async def nb_health_facility_finder(
    facility_type: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to find New Brunswick health facilities by type.

    Use for: single-tool health facility lookup — dispatches nb_get_health_facilities
    by facility_type across GeoNB_Health_Facilities layers 0-5. Lists the valid
    facility_type values from constants.HEALTH_FACILITY_LAYERS.
    """
    if lang == "fr":
        return (
            "Pour trouver des établissements de santé au Nouveau-Brunswick "
            "(source : GeoNB_Health_Facilities, couches 0-5) :\n\n"
            f"Appelez `nb_get_health_facilities` avec `facility_type=` "
            f"(vous avez fourni : {facility_type!r}) — une valeur parmi :\n"
            "- `'hospital_horizon'` — couche 0 : hôpitaux du Réseau de santé Horizon\n"
            "- `'hospital_vitalite'` — couche 1 : hôpitaux du Réseau de santé Vitalité\n"
            "- `'after_hours_clinic'` — couche 2 : cliniques sans rendez-vous\n"
            "- `'adult_residential_centre'` — couche 3 : centres résidentiels pour adultes\n"
            "- `'nursing_home'` — couche 4 : foyers de soins\n"
            "- `'pharmacy'` — couche 5 : pharmacies\n\n"
            "**Remarque :** les couches 0-1 utilisent un schéma compact "
            "(`Hospital_N`, `Name_E`/`Name_F`, `Telephone_`); les couches 2-5 utilisent "
            "un schéma dérivé du géocodeur Esri, beaucoup plus large. Consultez "
            "`data://nb/health-regions` pour les deux réseaux de santé régionaux."
        )
    return (
        "To find New Brunswick health facilities "
        "(source: GeoNB_Health_Facilities, layers 0-5):\n\n"
        f"Call `nb_get_health_facilities` with `facility_type=` "
        f"(you provided: {facility_type!r}) — one of:\n"
        "- `'hospital_horizon'` — layer 0: Horizon Health Network hospitals\n"
        "- `'hospital_vitalite'` — layer 1: Vitalité Health Network hospitals\n"
        "- `'after_hours_clinic'` — layer 2: after-hours clinics\n"
        "- `'adult_residential_centre'` — layer 3: adult residential centres\n"
        "- `'nursing_home'` — layer 4: nursing homes\n"
        "- `'pharmacy'` — layer 5: pharmacies\n\n"
        "**Note:** layers 0-1 use a compact schema (`Hospital_N`, `Name_E`/`Name_F`, "
        "`Telephone_`); layers 2-5 use a much wider Esri-geocoder-derived schema. See "
        "`data://nb/health-regions` for the two regional health authorities."
    )


@prompt
async def nb_bilingual_dataset_lookup(
    query: str = "",
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction demonstrating bilingual dataset lookup on New Brunswick's catalogue.

    Use for: fetching French-language dataset metadata (D-12). Warns that New
    Brunswick sometimes publishes a dataset as two separate CKAN records (one
    French, one English) rather than one bilingual record — near-duplicate
    search results are expected and correct, not a bug.
    """
    if lang == "fr":
        return (
            "Pour obtenir des métadonnées de jeux de données en français au "
            f"Nouveau-Brunswick (recherche : {query!r}) :\n\n"
            "Appelez `nb_search_datasets` ou `nb_get_dataset_details` avec `lang='fr'`. "
            "Le titre et les notes suivent une chaîne de repli : la langue demandée "
            "d'abord, puis l'anglais, puis le champ brut.\n\n"
            "**Avertissement important (D-12) :** le Nouveau-Brunswick publie certains "
            "jeux de données comme DEUX enregistrements CKAN distincts — un en français, "
            "un en anglais — plutôt qu'un seul enregistrement bilingue. Des résultats "
            "quasi-identiques (même sujet, titres différents) dans "
            "`nb_search_datasets` sont donc ATTENDUS et CORRECTS, pas un doublon à "
            "signaler comme un bogue."
        )
    return (
        f"To get French-language dataset metadata in New Brunswick (query: {query!r}):\n\n"
        "Call `nb_search_datasets` or `nb_get_dataset_details` with `lang='fr'`. The "
        "title and notes follow a fallback chain: requested language first, then "
        "English, then the plain field.\n\n"
        "**Important warning (D-12):** New Brunswick publishes some datasets as TWO "
        "separate CKAN records — one French, one English — rather than one bilingual "
        "record. Near-duplicate results (same subject, different titles) in "
        "`nb_search_datasets` are therefore EXPECTED and CORRECT, not a duplicate to "
        "flag as a bug."
    )
