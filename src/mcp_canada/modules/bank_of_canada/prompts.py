"""MCP prompts for the Bank of Canada module.

Provides guided workflow prompts and quick lookup templates for BoC Valet API data.
All prompts are bilingual (en/fr) via the lang parameter and use the boc_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def boc_analyze_rates(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a Bank of Canada exchange rate analysis workflow.

    Chains boc_search_series → boc_get_exchange_rates → boc_get_observations
    to answer comprehensive questions about CAD exchange rates.
    """
    if lang == "fr":
        return [
            Message(
                "Quelles devises souhaitez-vous analyser? "
                "Exemples: USD, EUR, GBP, JPY. "
                "Je peux récupérer les taux actuels et historiques en CAD.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser boc_search_series pour confirmer le nom de la série, "
                "puis boc_get_exchange_rates pour récupérer les données de taux de change "
                "depuis l'API Valet de la Banque du Canada. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which currencies would you like to analyze? "
            "Examples: USD, EUR, GBP, JPY. "
            "I can fetch current and historical CAD exchange rates.",
            role="user",
        ),
        Message(
            "I will first use boc_search_series to confirm the series name, "
            "then boc_get_exchange_rates to retrieve exchange rate data "
            "from the Bank of Canada Valet API. Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def boc_get_policy_rate(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve the current Bank of Canada overnight policy rate."""
    if lang == "fr":
        return (
            "Utilisez boc_get_interest_rates avec rate_type='policy' et recent=1 "
            "pour obtenir le taux directeur actuel de la Banque du Canada."
        )
    return (
        "Use boc_get_interest_rates with rate_type='policy' and recent=1 "
        "to get the current Bank of Canada overnight policy rate."
    )


@prompt
async def boc_compare_currencies(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing two currencies over a date range.

    Chains boc_get_exchange_rates twice (one per currency) then summarizes
    the relative movement between them using CAD as the base currency.
    """
    if lang == "fr":
        return [
            Message(
                "Quelles devises souhaitez-vous comparer, et sur quelle période? "
                "Exemples: comparer USD et EUR du 2024-01-01 au 2024-12-31.",
                role="user",
            ),
            Message(
                "Je vais utiliser boc_get_exchange_rates pour chaque devise sur la période "
                "choisie, puis calculer le mouvement relatif en utilisant le CAD comme "
                "devise de base. Je présenterai un tableau comparatif des taux.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which currencies would you like to compare, and over what date range? "
            "Example: compare USD and EUR from 2024-01-01 to 2024-12-31.",
            role="user",
        ),
        Message(
            "I will call boc_get_exchange_rates for each currency over the specified "
            "period, then calculate the relative movement using CAD as the base currency. "
            "I will present a comparative table of exchange rates.",
            role="assistant",
        ),
    ]


@prompt
async def boc_explore_commodities(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring Bank of Canada Commodity Price Index (BCPI) data.

    Chains boc_list_groups → boc_get_commodity_prices to help users understand
    available commodity categories and fetch price index history.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous explorer l'Indice des prix des produits de base (BCPI) "
                "de la Banque du Canada? Je peux récupérer les données pour l'énergie, "
                "les métaux, l'agriculture, la foresterie ou l'ensemble du panier.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser boc_list_groups pour afficher les groupes BCPI disponibles, "
                "puis boc_get_commodity_prices avec le commodity_type approprié "
                "(energy, metals, agriculture, forestry, fish, ou total) pour récupérer "
                "les données historiques mensuelles.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to explore the Bank of Canada Commodity Price Index (BCPI)? "
            "I can fetch data for energy, metals, agriculture, forestry, fish, "
            "or the total BCPI basket.",
            role="user",
        ),
        Message(
            "I will first use boc_list_groups to show available BCPI groups, "
            "then call boc_get_commodity_prices with the appropriate commodity_type "
            "(energy, metals, agriculture, forestry, fish, or total) "
            "to retrieve monthly historical price index data.",
            role="assistant",
        ),
    ]


@prompt
async def boc_check_inflation(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve current inflation data from the Bank of Canada."""
    if lang == "fr":
        return (
            "Utilisez boc_get_inflation_data sans paramètre indicator pour obtenir "
            "tous les indicateurs d'inflation (IPC total, IPC-tronqué, IPC-médian, "
            "IPC-commun) ou spécifiez indicator='total' pour le seul IPC global."
        )
    return (
        "Use boc_get_inflation_data without an indicator parameter to get "
        "all inflation indicators (total CPI, CPI-trim, CPI-median, CPI-common), "
        "or specify indicator='total' for the headline CPI only."
    )
