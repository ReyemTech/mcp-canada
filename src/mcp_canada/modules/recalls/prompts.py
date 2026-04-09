"""MCP prompts for the Recalls module.

Provides guided workflow prompts and quick lookup templates for Health Canada Recalls.
All prompts are bilingual (en/fr) via the lang parameter and use the recalls_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def recalls_investigate_alert(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through investigating a Health Canada safety alert or recall.

    Chains recalls_search -> recalls_get_details to build a complete
    picture of a recall or safety advisory.
    """
    if lang == "fr":
        return [
            Message(
                "Quel rappel ou alerte de sécurité souhaitez-vous examiner? "
                "Vous pouvez fournir un mot-clé (ex: 'listeria', 'Ford F-150'), "
                "un numéro de rappel ou une marque de produit.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser recalls_search pour trouver les alertes correspondantes, "
                "puis recalls_get_details pour obtenir les informations complètes sur le rappel: "
                "cause, produits affectés, mesures à prendre et coordonnées.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which recall or safety alert would you like to investigate? "
            "You can provide a keyword (e.g., 'listeria', 'Ford F-150'), "
            "a recall number, or a brand name.",
            role="user",
        ),
        Message(
            "I will first use recalls_search to find matching alerts, "
            "then recalls_get_details to retrieve the complete recall information: "
            "cause, affected products, what to do, and contact information.",
            role="assistant",
        ),
    ]


@prompt
async def recalls_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for recalls by keyword."""
    if lang == "fr":
        return (
            "Utilisez recalls_search avec un mot-clé pour chercher dans les rappels et alertes de sécurité. "
            "Filtrez par catégorie ('FOOD', 'VEHICLE', 'HEALTH', 'CPS') "
            "ou par nombre de résultats récents avec le paramètre limit."
        )
    return (
        "Use recalls_search with a keyword to search recalls and safety alerts. "
        "Filter by category ('FOOD', 'VEHICLE', 'HEALTH', 'CPS') "
        "or limit the number of results with the limit parameter."
    )


@prompt
async def recalls_check_food_safety(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check recent food safety recalls."""
    if lang == "fr":
        return (
            "Utilisez recalls_get_food pour obtenir les rappels alimentaires récents de Santé Canada. "
            "Ajoutez le paramètre recent avec un nombre (ex: 10) pour limiter les résultats aux plus récents. "
            "Pour les allergènes spécifiques, utilisez recalls_search avec le nom de l'allergène."
        )
    return (
        "Use recalls_get_food to get recent food safety recalls from Health Canada. "
        "Add the recent parameter with a number (e.g., 10) to limit results to the most recent. "
        "For specific allergens, use recalls_search with the allergen name."
    )


@prompt
async def recalls_vehicle_safety(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through tracking vehicle safety recalls.

    Chains recalls_get_vehicles -> recalls_get_details to investigate
    vehicle recalls and identify affected models and components.
    """
    if lang == "fr":
        return [
            Message(
                "Quel véhicule ou rappel automobile souhaitez-vous vérifier? "
                "Vous pouvez fournir la marque et le modèle (ex: 'Toyota Camry 2020'), "
                "un composant (ex: 'airbag', 'freins') ou un numéro de rappel Transport Canada.",
                role="user",
            ),
            Message(
                "Je vais utiliser recalls_get_vehicles pour trouver les rappels automobiles récents, "
                "puis recalls_get_details pour les informations complètes: "
                "véhicules affectés, numéros VIN, défaut identifié et mesures correctives.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which vehicle or automotive recall would you like to check? "
            "You can provide the make and model (e.g., 'Toyota Camry 2020'), "
            "a component (e.g., 'airbag', 'brakes'), or a Transport Canada recall number.",
            role="user",
        ),
        Message(
            "I will use recalls_get_vehicles to find recent automotive recalls, "
            "then recalls_get_details for complete information: "
            "affected vehicles, VIN ranges, identified defect, and corrective action.",
            role="assistant",
        ),
    ]
