"""MCP prompts for the York Region Municipal Open Data module.

Provides guided workflow prompts and quick lookup templates for the
York Region ArcGIS Hub portals (york_region, markham, newmarket, aurora).
All prompts are bilingual (en/fr) via the lang parameter and use the
york_region_, markham_ prefixes.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def york_region_explore_transit(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring YRT/Viva transit data from York Region.

    Chains york_region_get_transit_stops -> york_region_get_transit_routes
    for YRT/Viva bus stop and route discovery from the York Region ArcGIS Hub.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données du réseau de transport de York Region "
                "(YRT/Viva). Par où commencer?",
                role="user",
            ),
            Message(
                "Commencez par `york_region_get_transit_stops` pour rechercher des arrêts "
                "par nom (ex. query='Finch'), ou `york_region_get_transit_routes` pour lister "
                "toutes les lignes YRT/Viva. Ajoutez `include_geometry=true` pour l'analyse "
                "spatiale. Combinez avec `york_region_get_road_network` pour voir les lignes "
                "de transport en contexte routier. Pour explorer les jeux de données disponibles, "
                "utilisez `york_region_search_datasets` avec query='transit'.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore York Region transit data (YRT/Viva). Where should I start?",
            role="user",
        ),
        Message(
            "Start with `york_region_get_transit_stops` to search stops by name "
            "(e.g. query='Finch'), or `york_region_get_transit_routes` to list all YRT/Viva "
            "routes. For spatial analysis add `include_geometry=true`. Combine with "
            "`york_region_get_road_network` to see routes in context. To explore available "
            "datasets, use `york_region_search_datasets` with query='transit'.",
            role="assistant",
        ),
    ]


@prompt
async def york_region_explore_census(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through analyzing 2021 Census demographics across York Region.

    Uses york_region_get_census_demographics with optional CSDNAME filter to
    compare age/sex or income data across York Region municipalities.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux comparer les données démographiques du recensement 2021 "
                "dans les municipalités de la Région de York.",
                role="user",
            ),
            Message(
                "Utilisez `york_region_get_census_demographics` pour interroger les données "
                "du recensement 2021 par aire de diffusion. Étapes recommandées:\n\n"
                "1. `york_region_get_census_demographics(dataset='age_sex', csdname='Markham')` "
                "pour Markham.\n"
                "2. Répétez pour d'autres municipalités: Vaughan, Newmarket, Aurora, etc.\n"
                "3. Comparez TOT_POP, TOT_AVG_AGE_POP et les groupes d'âge (TOT_0_TO_14_YRS, "
                "TOT_15_TO_64_YRS, TOT_65_YRS_OVER).\n\n"
                "Note: l'ensemble de champs est limité à 10 colonnes. Pour accéder aux 364 "
                "champs complets, utilisez `york_region_query_features` directement avec "
                "le service FeatureServer YR_AGE_SEX_FS.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to compare demographics across York Region municipalities using the 2021 Census.",
            role="user",
        ),
        Message(
            "Use `york_region_get_census_demographics` to query 2021 Census data by "
            "Dissemination Area. Recommended steps:\n\n"
            "1. `york_region_get_census_demographics(dataset='age_sex', csdname='Markham')` "
            "for Markham.\n"
            "2. Repeat for other municipalities: Vaughan, Newmarket, Aurora, King, etc.\n"
            "3. Compare TOT_POP, TOT_AVG_AGE_POP and age groups (TOT_0_TO_14_YRS, "
            "TOT_15_TO_64_YRS, TOT_65_YRS_OVER).\n\n"
            "Note: the focused field set returns 10 columns. For all 364 fields, use "
            "`york_region_query_features` directly with the YR_AGE_SEX_FS FeatureServer URL.",
            role="assistant",
        ),
    ]


@prompt
async def york_region_explore_health(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring York Region public health and safety data.

    Uses york_region_get_public_health with location_type dispatch for
    beach water testing, hospital locations, and drinking water adverse incidents.
    """
    if lang == "fr":
        return [
            Message(
                "Quelles données de santé publique sont disponibles pour la Région de York?",
                role="user",
            ),
            Message(
                "Utilisez `york_region_get_public_health` avec le paramètre `location_type`:\n\n"
                "- `location_type='beach_water'` — résultats de tests de qualité de l'eau des plages\n"
                "- `location_type='hospital'` — emplacements des hôpitaux de York Region\n"
                "- `location_type='drinking_water'` — incidents défavorables d'eau potable\n\n"
                "Ajoutez `include_geometry=true` pour cartographier les emplacements. "
                "Pour d'autres ensembles de données de santé, utilisez "
                "`york_region_search_datasets` avec query='santé' ou query='health'.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What health and safety data is available for York Region?",
            role="user",
        ),
        Message(
            "Use `york_region_get_public_health` with the `location_type` parameter:\n\n"
            "- `location_type='beach_water'` — beach water quality testing results\n"
            "- `location_type='hospital'` — York Region hospital locations\n"
            "- `location_type='drinking_water'` — drinking water adverse incidents\n\n"
            "Add `include_geometry=true` for mapping. For additional health datasets, "
            "use `york_region_search_datasets` with query='health' or query='public health'.",
            role="assistant",
        ),
    ]


@prompt
async def york_region_quick_dataset_search(
    query: str,
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search York Region and Markham/Newmarket/Aurora open data portals.

    Use for: one-shot dataset search across York Region ArcGIS Hub portals.
    """
    if lang == "fr":
        return (
            f"Utilisez `york_region_search_datasets` avec query='{query}' et limit=10 "
            f"pour rechercher dans le portail régional. Pour les municipalités locales: "
            f"Markham → `markham_search_datasets`, Newmarket → `newmarket_search_datasets`, "
            f"Aurora → `aurora_search_datasets`. Combinez les résultats si vous cherchez "
            f"des données à l'échelle de la région."
        )
    return (
        f"Call `york_region_search_datasets` with query='{query}' and limit=10 to search "
        f"the regional portal. For local municipality portals: "
        f"Markham → `markham_search_datasets`, Newmarket → `newmarket_search_datasets`, "
        f"Aurora → `aurora_search_datasets`. Combine results if looking for region-wide data."
    )


@prompt
async def markham_explore_infrastructure(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring Markham civic infrastructure data.

    Chains markham_get_addresses -> markham_get_road_network to explore
    Markham's civic address registry and SLRN road network.
    """
    if lang == "fr":
        return [
            Message(
                "Je veux explorer les données d'infrastructure civique de Markham "
                "(adresses et réseau routier).",
                role="user",
            ),
            Message(
                "Utilisez ces outils pour explorer l'infrastructure de Markham:\n\n"
                "- `markham_get_addresses(street='Main St')` — rechercher des adresses "
                "civiques par rue. Laissez `street` vide pour obtenir toutes les adresses "
                "(tronquées à 5 000 enregistrements).\n"
                "- `markham_get_road_network(name='Highway 7')` — interroger le réseau "
                "routier SLRN (Street Location Reference Network) par nom de route.\n"
                "- Combinez avec `markham_search_datasets` pour découvrir d'autres "
                "ensembles de données liés aux rues et au zonage.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to explore Markham's civic infrastructure — addresses and road network.",
            role="user",
        ),
        Message(
            "Use these tools to explore Markham's civic infrastructure:\n\n"
            "- `markham_get_addresses(street='Main St')` — search civic addresses by street name. "
            "Leave `street` empty to retrieve all addresses (truncated at 5,000 records).\n"
            "- `markham_get_road_network(name='Highway 7')` — query the SLRN road network "
            "(Street Location Reference Network) by road name.\n"
            "- Combine with `markham_search_datasets` to discover additional street, "
            "zoning, and infrastructure datasets.",
            role="assistant",
        ),
    ]
