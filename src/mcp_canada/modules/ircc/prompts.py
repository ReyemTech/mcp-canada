"""MCP prompts for the IRCC Immigration module.

Provides guided workflow prompts and quick lookup templates for Immigration,
Refugees and Citizenship Canada (IRCC) open data.
All prompts are bilingual (en/fr) via the lang parameter and use the ircc_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def ircc_explore_immigration(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through exploring IRCC immigration data.

    Chains ircc_list_datasets -> ircc_get_permanent_residents (or study/work permits)
    to discover and retrieve immigration data.
    """
    if lang == "fr":
        return [
            Message(
                "Quel type de données sur l'immigration souhaitez-vous explorer? "
                "Je peux accéder aux données sur les résidents permanents, les permis "
                "d'études, les permis de travail, l'Entrée express, les demandeurs d'asile "
                "et d'autres ensembles de données d'IRCC.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser ircc_list_datasets pour vous montrer tous les "
                "ensembles de données IRCC disponibles avec leurs descriptions, puis je "
                "pourrai récupérer les données spécifiques avec l'outil approprié. "
                "Commençons par explorer ce qui est disponible.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "What type of immigration data would you like to explore? "
            "I can access data on permanent residents, study permits, work permits, "
            "Express Entry, asylum claimants, and other IRCC datasets.",
            role="user",
        ),
        Message(
            "I will first use ircc_list_datasets to show all available IRCC datasets "
            "with their descriptions, then retrieve the specific data with the appropriate "
            "tool. Let's start by exploring what's available.",
            role="assistant",
        ),
    ]


@prompt
async def ircc_quick_pr(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve permanent resident data from IRCC."""
    if lang == "fr":
        return (
            "Utilisez ircc_get_permanent_residents avec breakdown='country' pour les données "
            "par pays d'origine, 'province' pour les données par province de destination, "
            "ou 'gender' / 'age' / 'cma' pour d'autres ventilations. "
            "Filtrez par pays='India' ou province='ON' si nécessaire."
        )
    return (
        "Use ircc_get_permanent_residents with breakdown='country' for data by source country, "
        "'province' for data by destination province, or 'gender' / 'age' / 'cma' for other "
        "breakdowns. Filter by country='India' or province='ON' if needed."
    )


@prompt
async def ircc_track_express_entry(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve Express Entry immigration data from IRCC."""
    if lang == "fr":
        return (
            "Utilisez ircc_get_express_entry avec stream='FSW' pour les travailleurs "
            "qualifiés fédéraux, 'CEC' pour l'expérience canadienne, 'FST' pour les "
            "métiers spécialisés fédéraux, ou laissez stream vide pour toutes les catégories. "
            "Spécifiez dataset='admissions' ou dataset='invited' selon votre besoin."
        )
    return (
        "Use ircc_get_express_entry with stream='FSW' for Federal Skilled Workers, "
        "'CEC' for Canadian Experience Class, 'FST' for Federal Skilled Trades, "
        "or leave stream empty for all streams. "
        "Specify dataset='admissions' or dataset='invited' depending on your need."
    )


@prompt
async def ircc_compare_pathways(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing immigration pathways to Canada.

    Combines ircc_get_permanent_residents + ircc_get_study_permits + ircc_get_work_permits
    to compare immigration pathway volumes and trends.
    """
    if lang == "fr":
        return [
            Message(
                "Quelles voies d'immigration souhaitez-vous comparer? "
                "Je peux analyser les résidents permanents, les permis d'études et les "
                "permis de travail pour vous aider à comprendre les tendances par pays "
                "d'origine, province ou catégorie.",
                role="user",
            ),
            Message(
                "Je vais utiliser ircc_get_permanent_residents pour les admissions de RP, "
                "ircc_get_study_permits pour les permis d'études, et ircc_get_work_permits "
                "pour les permis de travail (IMP et TFWP). Je présenterai un tableau "
                "comparatif des volumes par voie d'immigration. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which immigration pathways would you like to compare? "
            "I can analyze permanent residents, study permits, and work permits "
            "to help you understand trends by source country, province, or category.",
            role="user",
        ),
        Message(
            "I will use ircc_get_permanent_residents for PR admissions, "
            "ircc_get_study_permits for study permits, and ircc_get_work_permits "
            "for work permits (IMP and TFWP). I will present a comparative table "
            "of volumes by immigration pathway. Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def ircc_analyze_trends(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a multi-year immigration trend analysis.

    Uses ircc_get_permanent_residents with year filters across multiple years
    to identify trends in immigration volumes and composition.
    """
    if lang == "fr":
        return [
            Message(
                "Sur quelle période souhaitez-vous analyser les tendances d'immigration? "
                "Je peux récupérer les données des dernières années et identifier les "
                "tendances dans les volumes, les pays d'origine et les catégories.",
                role="user",
            ),
            Message(
                "Je vais utiliser ircc_get_permanent_residents avec le paramètre year "
                "pour plusieurs années afin de constituer une série temporelle. "
                "Je comparerai ensuite les volumes totaux, la répartition par pays "
                "et les changements de catégorie d'une année à l'autre. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which time period would you like to analyze for immigration trends? "
            "I can retrieve data across multiple years and identify trends in "
            "volumes, source countries, and categories.",
            role="user",
        ),
        Message(
            "I will use ircc_get_permanent_residents with the year parameter across "
            "multiple years to build a time series. I will then compare total volumes, "
            "source country distribution, and category shifts year-over-year. "
            "Let's get started.",
            role="assistant",
        ),
    ]
