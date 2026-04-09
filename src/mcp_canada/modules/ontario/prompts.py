"""MCP prompts for the Ontario Open Data module.

Provides guided workflow prompts and quick lookup templates for the
Ontario government open data portal (data.ontario.ca).
All prompts are bilingual (en/fr) via the lang parameter and use the ontario_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def ontario_explore_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring Ontario government open data.

    Chains ontario_search_datasets -> ontario_get_dataset_details -> ontario_get_resource
    to discover and retrieve data from the Ontario open data portal.
    """
    if lang == "fr":
        return [
            Message(
                "Quel type de données du gouvernement de l'Ontario recherchez-vous? "
                "Je peux explorer le portail de données ouvertes data.ontario.ca pour "
                "trouver des jeux de données sur la santé, l'éducation, l'environnement, "
                "les transports, les finances et bien d'autres sujets.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser ontario_search_datasets pour trouver les jeux de "
                "données pertinents, puis ontario_get_dataset_details pour voir les "
                "ressources disponibles, et enfin ontario_get_resource pour récupérer "
                "les données. Commençons par rechercher.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What type of Ontario government data are you looking for? "
            "I can explore the data.ontario.ca open data portal for datasets on "
            "health, education, environment, transportation, finance, and many other topics.",
            role="user",
        ),
        Message(
            "I will first use ontario_search_datasets to find relevant datasets, "
            "then ontario_get_dataset_details to see available resources, "
            "and finally ontario_get_resource to retrieve the data. "
            "Let's start by searching.",
            role="assistant",
        ),
    ]


@prompt
async def ontario_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for Ontario government datasets."""
    if lang == "fr":
        return (
            "Utilisez ontario_search_datasets avec query='votre sujet' pour rechercher des "
            "jeux de données sur data.ontario.ca. Ajoutez organization='nom-du-ministère' "
            "pour filtrer par ministère. Utilisez ontario_list_organizations pour voir "
            "les noms de ministères disponibles."
        )
    return (
        "Use ontario_search_datasets with query='your topic' to search for datasets "
        "on data.ontario.ca. Add organization='ministry-name' to filter by ministry. "
        "Use ontario_list_organizations to see available ministry names."
    )


@prompt
async def ontario_browse_ministries(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to browse Ontario ministries and their datasets."""
    if lang == "fr":
        return (
            "Utilisez ontario_list_organizations pour voir tous les ministères et organismes "
            "qui publient des données sur data.ontario.ca. Ensuite, utilisez "
            "ontario_search_datasets avec organization='nom-du-ministère' pour voir tous "
            "les jeux de données d'un ministère spécifique."
        )
    return (
        "Use ontario_list_organizations to see all ministries and agencies that publish "
        "data on data.ontario.ca. Then use ontario_search_datasets with "
        "organization='ministry-name' to see all datasets from a specific ministry."
    )


@prompt
async def ontario_population_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through retrieving Ontario population projection data.

    Uses ontario_get_population_projections to retrieve demographic projections
    by region and year for planning and analysis.
    """
    if lang == "fr":
        return [
            Message(
                "Vous souhaitez des projections de population pour l'Ontario? "
                "Je peux récupérer les données de projections pour 2024 à 2051, "
                "filtrées par région de planification ou par census division.",
                role="user",
            ),
            Message(
                "Je vais utiliser ontario_get_population_projections pour récupérer "
                "les projections démographiques du gouvernement de l'Ontario. "
                "Vous pouvez filtrer par region='nom-de-région' et spécifier "
                "une plage d'années pour cibler votre analyse. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Looking for Ontario population projections? "
            "I can retrieve projection data for 2024 to 2051, "
            "filtered by planning region or census division.",
            role="user",
        ),
        Message(
            "I will use ontario_get_population_projections to retrieve Ontario government "
            "demographic projections. You can filter by region='region-name' and specify "
            "a year range to focus your analysis. Let's get started.",
            role="assistant",
        ),
    ]
