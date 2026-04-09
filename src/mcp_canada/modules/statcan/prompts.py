"""MCP prompts for the StatCan module.

Provides guided workflow prompts and quick lookup templates for the Statistics Canada
WDS and SDMX APIs. All prompts are bilingual (en/fr) via the lang parameter.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def statcan_find_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a Statistics Canada data discovery workflow.

    Chains sc_search_cubes -> sc_get_cube_metadata -> sc_get_code_sets ->
    sc_get_data_by_vector for a complete data exploration.
    """
    if lang == "fr":
        return [
            Message(
                "Sur quel sujet souhaitez-vous des données statistiques? "
                "Exemples: population, emploi, inflation, PIB, commerce. "
                "Je vais rechercher les cubes de données pertinents sur Statistique Canada.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser sc_search_cubes pour trouver les cubes de données "
                "pertinents, puis sc_get_cube_metadata pour examiner la structure du cube "
                "(dimensions, membres, codes), puis sc_get_code_sets pour comprendre les "
                "codes de fréquence et d'unité, et enfin sc_get_data_by_vector pour "
                "récupérer les observations. Commençons par votre sujet de recherche.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What statistical topic would you like data on? "
            "Examples: population, employment, inflation, GDP, trade. "
            "I will search Statistics Canada's data cubes for relevant datasets.",
            role="user",
        ),
        Message(
            "I will first use sc_search_cubes to find relevant data cubes, "
            "then sc_get_cube_metadata to examine the cube structure "
            "(dimensions, members, codes), then sc_get_code_sets to understand "
            "frequency and unit codes, and finally sc_get_data_by_vector to "
            "retrieve observations. Let's start with your topic.",
            role="assistant",
        ),
    ]


@prompt
async def statcan_quick_vector(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve Statistics Canada data by vector ID."""
    if lang == "fr":
        return (
            "Utilisez sc_get_data_by_vector avec vectorId (ex: 'v41690973') et "
            "recent=10 pour les 10 observations les plus récentes, ou spécifiez "
            "start_date et end_date pour une plage de dates spécifique."
        )
    return (
        "Use sc_get_data_by_vector with vectorId (e.g., 'v41690973') and "
        "recent=10 for the 10 most recent observations, or specify "
        "start_date and end_date for a specific date range."
    )


@prompt
async def statcan_explore_sdmx(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring Statistics Canada data via SDMX.

    Chains sc_get_sdmx_structure -> sc_get_sdmx_data with dimension filtering
    for structured data access using the SDMX standard.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous accéder aux données de Statistique Canada via le format SDMX? "
                "SDMX permet un filtrage précis par dimensions (géographie, âge, sexe, etc.). "
                "Quel est le numéro de produit (ex: 14-10-0023-01 pour l'emploi)?",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser sc_get_sdmx_structure avec le productId pour "
                "découvrir les dimensions et leurs membres disponibles, puis "
                "sc_get_sdmx_data avec une clé de dimension (ex: '1.2.3..' où '.' est "
                "un caractère générique) pour récupérer les données filtrées. "
                "La structure SDMX révèle tous les codes valides pour chaque dimension.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to access Statistics Canada data via SDMX format? "
            "SDMX allows precise filtering by dimensions (geography, age, sex, etc.). "
            "What is the product number (e.g., 14-10-0023-01 for employment)?",
            role="user",
        ),
        Message(
            "I will first use sc_get_sdmx_structure with the productId to discover "
            "available dimensions and their members, then sc_get_sdmx_data with a "
            "dimension key (e.g., '1.2.3..' where '.' is a wildcard) to retrieve "
            "filtered data. The SDMX structure reveals all valid codes per dimension.",
            role="assistant",
        ),
    ]


@prompt
async def statcan_store_and_query(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through storing StatCan vectors in the datastore and querying with SQL.

    Chains sc_fetch_vectors_to_store -> ds_query for cross-module SQL analytics.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous stocker des données de Statistique Canada dans le "
                "datastore local pour les analyser avec SQL? Quels vecteurs voulez-vous "
                "stocker et quel nom de table utiliser?",
                role="user",
            ),
            Message(
                "Je vais utiliser sc_fetch_vectors_to_store avec les vectorIds et un "
                "nom de table pour stocker les données dans SQLite, puis ds_query avec "
                "une requête SELECT pour analyser les résultats. Cette approche permet "
                "aussi de combiner des données de plusieurs modules avec des JOIN SQL.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to store Statistics Canada vectors in the local datastore "
            "for SQL analysis? Which vectors would you like to store and what table name?",
            role="user",
        ),
        Message(
            "I will use sc_fetch_vectors_to_store with vectorIds and a table name to "
            "store the data in SQLite, then ds_query with a SELECT statement to analyze "
            "the results. This approach also enables combining data from multiple modules "
            "using SQL JOINs.",
            role="assistant",
        ),
    ]


@prompt
async def statcan_monitor_changes(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to monitor recently changed Statistics Canada series and cubes."""
    if lang == "fr":
        return (
            "Utilisez sc_get_changed_series avec release_date (ex: '2024-01-15') pour "
            "lister les séries (vecteurs) mises à jour ce jour-là, ou "
            "sc_get_changed_cubes pour voir les cubes entiers qui ont été modifiés. "
            "Ces outils de surveillance sont utiles pour détecter les nouvelles données."
        )
    return (
        "Use sc_get_changed_series with release_date (e.g., '2024-01-15') to list "
        "series (vectors) updated on that date, or sc_get_changed_cubes to see "
        "which entire cubes were updated. These monitoring tools are useful for "
        "detecting when new data has been released."
    )


@prompt
async def statcan_compare_series(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing multiple Statistics Canada vector series.

    Uses sc_get_bulk_vector_data to fetch multiple vectors in a single call
    for side-by-side comparison.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous comparer plusieurs séries de Statistique Canada? "
                "Exemples: comparer l'emploi dans plusieurs provinces, ou plusieurs "
                "indicateurs économiques simultanément. Quels vecteurs voulez-vous comparer?",
                role="user",
            ),
            Message(
                "Je vais utiliser sc_get_bulk_vector_data avec une liste de vectorIds "
                "(ex: ['v123', 'v456', 'v789']) et recent=12 pour récupérer toutes les "
                "séries en un seul appel. Cette méthode est plus efficace que plusieurs "
                "appels séparés à sc_get_data_by_vector pour des comparaisons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to compare multiple Statistics Canada series? "
            "Examples: comparing employment across provinces, or multiple economic "
            "indicators side by side. Which vectors would you like to compare?",
            role="user",
        ),
        Message(
            "I will use sc_get_bulk_vector_data with a list of vectorIds "
            "(e.g., ['v123', 'v456', 'v789']) and recent=12 to fetch all series "
            "in a single call. This is more efficient than separate sc_get_data_by_vector "
            "calls when comparing multiple series.",
            role="assistant",
        ),
    ]
