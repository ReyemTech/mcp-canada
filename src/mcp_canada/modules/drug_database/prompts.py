"""MCP prompts for the Drug Database module.

Provides guided workflow prompts and quick lookup templates for the Health Canada
Drug Product Database. All prompts are bilingual (en/fr) via the lang parameter
and use the drug_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def drug_research_medication(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a complete medication research workflow.

    Chains drug_search -> drug_get_details -> drug_get_ingredients -> drug_get_routes
    to build a full profile of a drug product in the Health Canada database.
    """
    if lang == "fr":
        return [
            Message(
                "Quel médicament souhaitez-vous rechercher? "
                "Vous pouvez fournir le nom de marque (ex: 'Tylenol'), "
                "le nom générique (ex: 'acétaminophène') ou un numéro d'identification du médicament (DIN).",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser drug_search pour trouver le médicament, "
                "puis drug_get_details pour les informations générales (fabricant, statut, classe), "
                "drug_get_ingredients pour les ingrédients actifs et non médicinaux, "
                "et drug_get_routes pour les voies d'administration approuvées.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which medication would you like to research? "
            "You can provide a brand name (e.g., 'Tylenol'), "
            "a generic name (e.g., 'acetaminophen'), or a Drug Identification Number (DIN).",
            role="user",
        ),
        Message(
            "I will first use drug_search to find the medication, "
            "then drug_get_details for general information (manufacturer, status, class), "
            "drug_get_ingredients for active and non-medicinal ingredients, "
            "and drug_get_routes for approved routes of administration.",
            role="assistant",
        ),
    ]


@prompt
async def drug_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for a drug by brand name or generic name."""
    if lang == "fr":
        return (
            "Utilisez drug_search avec le nom de marque ou le nom générique du médicament. "
            "Vous pouvez aussi filtrer par entreprise pharmaceutique ou classe thérapeutique. "
            "Pour les recherches exactes, utilisez drug_get_details avec un DIN."
        )
    return (
        "Use drug_search with the brand name or generic name of the medication. "
        "You can also filter by pharmaceutical company or therapeutic class. "
        "For exact lookups, use drug_get_details with a DIN."
    )


@prompt
async def drug_check_company(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to find drug products by pharmaceutical company."""
    if lang == "fr":
        return (
            "Utilisez drug_search_companies pour trouver une entreprise pharmaceutique par nom. "
            "Une fois l'entreprise identifiée, utilisez drug_search avec le nom de l'entreprise "
            "pour voir tous ses médicaments homologués au Canada."
        )
    return (
        "Use drug_search_companies to find a pharmaceutical company by name. "
        "Once you have the company name, use drug_search with the company name "
        "to see all their Health Canada approved drug products."
    )


@prompt
async def drug_compare_generics(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing a brand-name drug with its generic equivalents.

    Chains drug_search -> drug_get_details + drug_get_therapeutic_class
    to compare brand and generic versions of a medication.
    """
    if lang == "fr":
        return [
            Message(
                "Quel médicament de marque souhaitez-vous comparer avec ses génériques? "
                "Vous pouvez fournir le nom de marque (ex: 'Lipitor') "
                "ou le nom générique (ex: 'atorvastatine').",
                role="user",
            ),
            Message(
                "Je vais utiliser drug_search pour trouver tous les produits avec le même ingrédient actif, "
                "puis drug_get_details pour chaque produit afin de comparer le fabricant, le statut et la forme, "
                "et drug_get_therapeutic_class pour confirmer la classification thérapeutique ATC.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which brand-name medication would you like to compare with its generics? "
            "You can provide the brand name (e.g., 'Lipitor') "
            "or the generic name (e.g., 'atorvastatin').",
            role="user",
        ),
        Message(
            "I will use drug_search to find all products with the same active ingredient, "
            "then drug_get_details for each product to compare manufacturer, status, and form, "
            "and drug_get_therapeutic_class to confirm the ATC therapeutic classification.",
            role="assistant",
        ),
    ]


@prompt
async def drug_check_status(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check the market status of a drug by DIN."""
    if lang == "fr":
        return (
            "Utilisez drug_get_status avec le numéro DIN du médicament "
            "pour vérifier son statut sur le marché canadien "
            "(approuvé, annulé, dormant, etc.). "
            "Si vous n'avez pas le DIN, utilisez d'abord drug_search pour le trouver."
        )
    return (
        "Use drug_get_status with the drug's DIN number "
        "to check its current market status in Canada "
        "(approved, cancelled, dormant, etc.). "
        "If you don't have the DIN, use drug_search first to find it."
    )
