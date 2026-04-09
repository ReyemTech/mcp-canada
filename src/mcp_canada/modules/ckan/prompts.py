"""MCP prompts for the CKAN module.

Provides guided workflow prompts and quick lookup templates for the Canadian
federal government open data portal (open.canada.ca CKAN API).
All prompts are bilingual (en/fr) via the lang parameter.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def ckan_explore_federal_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through discovering and accessing federal open data on open.canada.ca.

    Chains ckan_search_datasets -> ckan_get_dataset_details -> ckan_get_resource
    for complete dataset discovery and resource access.
    """
    if lang == "fr":
        return [
            Message(
                "Quel type de données gouvernementales fédérales cherchez-vous? "
                "Exemples: données sur le climat, immigration, budget fédéral, "
                "finances publiques, transport. Je vais chercher sur le portail "
                "ouvert du gouvernement du Canada (open.canada.ca).",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser ckan_search_datasets pour trouver les jeux "
                "de données pertinents, puis ckan_get_dataset_details pour examiner "
                "les ressources disponibles (CSV, JSON, XLSX), et enfin ckan_get_resource "
                "pour accéder aux données d'une ressource spécifique. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What type of federal government data are you looking for? "
            "Examples: climate data, immigration, federal budget, public finances, "
            "transportation. I will search the Government of Canada open data portal "
            "(open.canada.ca).",
            role="user",
        ),
        Message(
            "I will first use ckan_search_datasets to find relevant datasets, "
            "then ckan_get_dataset_details to examine available resources "
            "(CSV, JSON, XLSX), and finally ckan_get_resource to access the data "
            "from a specific resource. Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def ckan_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for datasets on the federal open data portal."""
    if lang == "fr":
        return (
            "Utilisez ckan_search_datasets avec une requête en langage naturel "
            "(ex: 'données sur l'immigration par province') pour trouver des jeux "
            "de données fédéraux. Ajoutez organization='statcan' pour filtrer par "
            "organisme, ou format='CSV' pour des formats spécifiques."
        )
    return (
        "Use ckan_search_datasets with a natural language query "
        "(e.g., 'immigration data by province') to find federal datasets. "
        "Add organization='statcan' to filter by department, "
        "or format='CSV' for specific resource formats."
    )


@prompt
async def ckan_browse_organizations(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to browse federal organizations publishing open data."""
    if lang == "fr":
        return (
            "Utilisez ckan_list_organizations pour voir la liste des organisations "
            "fédérales qui publient des données ouvertes sur open.canada.ca, "
            "puis ckan_search_datasets avec organization='nom-org' pour voir "
            "tous les jeux de données d'un ministère spécifique."
        )
    return (
        "Use ckan_list_organizations to see all federal organizations publishing "
        "open data on open.canada.ca, then ckan_search_datasets with "
        "organization='org-name' to browse datasets from a specific department."
    )


@prompt
async def ckan_browse_by_tag(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to discover datasets by topic tag on the federal open data portal."""
    if lang == "fr":
        return (
            "Utilisez ckan_search_by_tag avec une balise thématique "
            "(ex: 'agriculture', 'environment', 'health') pour trouver tous les "
            "jeux de données étiquetés sur ce sujet sur open.canada.ca. "
            "Les étiquettes sont en anglais sur le portail fédéral."
        )
    return (
        "Use ckan_search_by_tag with a topic tag "
        "(e.g., 'agriculture', 'environment', 'health') to find all datasets "
        "tagged on that subject on open.canada.ca. Tags are in English "
        "on the federal portal."
    )


@prompt
async def ckan_portal_overview(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through getting a high-level overview of the federal open data portal.

    Chains ckan_get_dataset_stats -> ckan_list_groups to show portal scope
    and available thematic categories.
    """
    if lang == "fr":
        return [
            Message(
                "Pouvez-vous me donner un aperçu du portail de données ouvertes "
                "du gouvernement du Canada? Je voudrais savoir combien de jeux de "
                "données sont disponibles et quels sont les groupes thématiques.",
                role="user",
            ),
            Message(
                "Je vais utiliser ckan_get_dataset_stats pour obtenir les statistiques "
                "globales du portail (nombre de jeux de données, organisations, formats), "
                "puis ckan_list_groups pour afficher les groupes thématiques disponibles "
                "(environnement, santé, économie, etc.). Cela donnera une vue complète "
                "du contenu disponible sur open.canada.ca.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Can you give me an overview of the Government of Canada open data portal? "
            "I would like to know how many datasets are available and what thematic "
            "groups exist.",
            role="user",
        ),
        Message(
            "I will use ckan_get_dataset_stats to get portal-wide statistics "
            "(dataset count, organizations, formats), then ckan_list_groups to show "
            "available thematic groups (environment, health, economy, etc.). "
            "This will provide a complete picture of what is available on open.canada.ca.",
            role="assistant",
        ),
    ]
