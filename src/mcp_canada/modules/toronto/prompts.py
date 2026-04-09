"""MCP prompts for the Toronto Municipal Open Data module.

Provides guided workflow prompts and quick lookup templates for the
City of Toronto open data portal (open.toronto.ca).
All prompts are bilingual (en/fr) via the lang parameter and use the toronto_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def toronto_explore_city_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring City of Toronto open data.

    Chains toronto_search_datasets -> toronto_get_dataset_details -> toronto_get_resource
    to discover and retrieve data from the Toronto open data portal.
    """
    if lang == "fr":
        return [
            Message(
                "Quel type de données municipales de Toronto recherchez-vous? "
                "Je peux explorer le portail de données ouvertes de Toronto pour "
                "trouver des jeux de données sur les transports, les quartiers, "
                "les demandes de service 311, le logement et bien d'autres sujets.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser toronto_search_datasets pour trouver les jeux de "
                "données pertinents, puis toronto_get_dataset_details pour voir les "
                "ressources disponibles, et enfin toronto_get_resource pour récupérer "
                "les données. Commençons par rechercher.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What type of Toronto municipal data are you looking for? "
            "I can explore the City of Toronto open data portal for datasets on "
            "transportation, neighbourhoods, 311 service requests, housing, and more.",
            role="user",
        ),
        Message(
            "I will first use toronto_search_datasets to find relevant datasets, "
            "then toronto_get_dataset_details to see available resources, "
            "and finally toronto_get_resource to retrieve the data. "
            "Let's start by searching.",
            role="assistant",
        ),
    ]


@prompt
async def toronto_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for City of Toronto datasets."""
    if lang == "fr":
        return (
            "Utilisez toronto_search_datasets avec query='votre sujet' pour rechercher des "
            "jeux de données sur le portail de données ouvertes de Toronto. "
            "Ajoutez organization='nom-de-division' pour filtrer par division municipale. "
            "Consultez data://toronto/city-divisions pour les noms de divisions disponibles."
        )
    return (
        "Use toronto_search_datasets with query='your topic' to search the City of Toronto "
        "open data portal. Add organization='division-name' to filter by city division. "
        "Check data://toronto/city-divisions for available division names."
    )


@prompt
async def toronto_explore_neighbourhood(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a Toronto neighbourhood analysis.

    Chains toronto_get_neighbourhood_profile -> toronto_compare_neighbourhoods
    to explore socioeconomic and demographic characteristics of Toronto neighbourhoods.
    """
    if lang == "fr":
        return [
            Message(
                "Quel quartier ou arrondissement de Toronto souhaitez-vous analyser? "
                "Je peux récupérer des profils détaillés sur la population, les revenus, "
                "le logement et d'autres indicateurs de recensement pour les 140 quartiers "
                "officiels de Toronto.",
                role="user",
            ),
            Message(
                "Je vais utiliser toronto_get_neighbourhood_profile pour récupérer le profil "
                "socioéconomique complet du quartier. Si vous souhaitez comparer deux quartiers, "
                "j'utiliserai toronto_compare_neighbourhoods. Les données proviennent du "
                "recensement de 2016 et comprennent 2383 indicateurs. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which Toronto neighbourhood would you like to analyze? "
            "I can retrieve detailed profiles covering population, income, housing, "
            "and other census indicators for all 140 official Toronto neighbourhoods.",
            role="user",
        ),
        Message(
            "I will use toronto_get_neighbourhood_profile to retrieve the full socioeconomic "
            "profile. If you want to compare two neighbourhoods, I will use "
            "toronto_compare_neighbourhoods. Data comes from the 2016 Census and includes "
            "2,383 indicators. Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def toronto_ttc_transit(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring Toronto Transit Commission (TTC) data.

    Chains toronto_get_ttc_stops -> toronto_get_ttc_routes for transit information
    from the TTC GTFS static schedule feed.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous explorer les données du réseau de transport en commun de "
                "Toronto (TTC)? Je peux récupérer les arrêts, les lignes et les horaires "
                "à partir des données GTFS statiques du TTC.",
                role="user",
            ),
            Message(
                "Je vais utiliser toronto_get_ttc_stops pour récupérer les arrêts dans "
                "une zone géographique, et toronto_get_ttc_routes pour les lignes et leurs "
                "arrêts. Les données GTFS sont mises à jour périodiquement et comprennent "
                "les métros, tramways et autobus. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to explore Toronto Transit Commission (TTC) data? "
            "I can retrieve stops, routes, and schedules from the TTC GTFS static feed.",
            role="user",
        ),
        Message(
            "I will use toronto_get_ttc_stops to find stops in a geographic area, "
            "and toronto_get_ttc_routes for routes and their stops. "
            "GTFS data is periodically updated and covers subway, streetcar, and bus. "
            "Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def toronto_check_311(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve 311 service request data from Toronto."""
    if lang == "fr":
        return (
            "Utilisez toronto_get_311_requests avec year=2023 (ou l'année souhaitée) "
            "pour récupérer les demandes de service 311 initiées par les citoyens. "
            "Filtrez par ward='25' pour un quartier spécifique ou par "
            "service_request_type='Graffiti' pour un type de service. "
            "Données disponibles depuis 2009."
        )
    return (
        "Use toronto_get_311_requests with year=2023 (or desired year) to retrieve "
        "citizen-initiated 311 service requests. Filter by ward='25' for a specific ward "
        "or by service_request_type='Graffiti' for a service type. "
        "Data available from 2009 onwards."
    )


@prompt
async def toronto_rental_analysis(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a Toronto rental market analysis.

    Combines toronto_get_rentsafe_evaluations + toronto_get_short_term_rentals
    to provide a comprehensive overview of the Toronto rental market.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous analyser le marché locatif de Toronto? "
                "Je peux récupérer les évaluations RentSafeTO pour les immeubles d'appartements "
                "et les données sur les locations de courte durée (Airbnb, etc.).",
                role="user",
            ),
            Message(
                "Je vais utiliser toronto_get_rentsafe_evaluations pour les scores d'évaluation "
                "des immeubles d'appartements du programme RentSafeTO, et "
                "toronto_get_short_term_rentals pour les données du registre des opérateurs "
                "de location de courte durée. Ensemble, ces données brossent un tableau "
                "du parc locatif de Toronto. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to analyze Toronto's rental market? "
            "I can retrieve RentSafeTO apartment building evaluations and "
            "short-term rental operator registration data.",
            role="user",
        ),
        Message(
            "I will use toronto_get_rentsafe_evaluations for apartment building evaluation "
            "scores from the RentSafeTO program, and toronto_get_short_term_rentals for "
            "short-term rental operator registration data (Airbnb, etc.). Together these "
            "datasets paint a picture of Toronto's rental stock. Let's get started.",
            role="assistant",
        ),
    ]
