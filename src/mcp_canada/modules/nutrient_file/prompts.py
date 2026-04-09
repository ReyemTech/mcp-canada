"""MCP prompts for the Nutrient File module.

Provides guided workflow prompts and quick lookup templates for the Canadian Nutrient File.
All prompts are bilingual (en/fr) via the lang parameter and use the nutrient_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def nutrient_analyze_food(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a complete food nutrition analysis workflow.

    Chains nutrient_search_foods -> nutrient_get_food_details ->
    nutrient_get_nutrient_amounts -> nutrient_get_serving_sizes
    to build a full nutritional profile.
    """
    if lang == "fr":
        return [
            Message(
                "Quel aliment souhaitez-vous analyser sur le plan nutritionnel? "
                "Vous pouvez fournir le nom de l'aliment (ex: 'boeuf haché', 'pomme', 'lait 2%'). "
                "Je rechercherai sa composition nutritionnelle dans le Fichier canadien sur les éléments nutritifs.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser nutrient_search_foods pour trouver l'aliment, "
                "puis nutrient_get_food_details pour confirmer sa description, "
                "nutrient_get_nutrient_amounts pour obtenir la composition nutritionnelle complète, "
                "et nutrient_get_serving_sizes pour les portions de référence.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which food would you like to analyze nutritionally? "
            "You can provide the food name (e.g., 'ground beef', 'apple', '2% milk'). "
            "I will look up its nutritional composition in the Canadian Nutrient File.",
            role="user",
        ),
        Message(
            "I will first use nutrient_search_foods to find the food, "
            "then nutrient_get_food_details to confirm its description, "
            "nutrient_get_nutrient_amounts to get the complete nutritional composition, "
            "and nutrient_get_serving_sizes for reference portion sizes.",
            role="assistant",
        ),
    ]


@prompt
async def nutrient_quick_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search for a food by name in the Canadian Nutrient File."""
    if lang == "fr":
        return (
            "Utilisez nutrient_search_foods avec le nom de l'aliment pour le chercher dans le "
            "Fichier canadien sur les éléments nutritifs. "
            "Le résultat inclut un food_code que vous pouvez utiliser avec nutrient_get_nutrient_amounts "
            "pour obtenir la composition nutritionnelle complète."
        )
    return (
        "Use nutrient_search_foods with the food name to search the Canadian Nutrient File. "
        "The result includes a food_code that you can use with nutrient_get_nutrient_amounts "
        "to get the complete nutritional composition."
    )


@prompt
async def nutrient_compare_foods(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing the nutritional profiles of two or more foods.

    Chains nutrient_search_foods (x2+) -> nutrient_compare_foods
    to provide a side-by-side nutrient comparison.
    """
    if lang == "fr":
        return [
            Message(
                "Quels aliments souhaitez-vous comparer sur le plan nutritionnel? "
                "Je peux comparer deux aliments ou plus côte à côte. "
                "Exemples: comparer 'boeuf haché' et 'poitrine de poulet', ou comparer 'lait entier' et 'lait 2%'.",
                role="user",
            ),
            Message(
                "Je vais utiliser nutrient_search_foods pour trouver chaque aliment et obtenir son code, "
                "puis nutrient_compare_foods avec les codes des aliments pour générer "
                "un tableau comparatif des nutriments côte à côte.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which foods would you like to compare nutritionally? "
            "I can compare two or more foods side by side. "
            "Examples: compare 'ground beef' and 'chicken breast', or compare 'whole milk' and '2% milk'.",
            role="user",
        ),
        Message(
            "I will use nutrient_search_foods to find each food and get its food code, "
            "then nutrient_compare_foods with the food codes to generate "
            "a side-by-side nutrient comparison table.",
            role="assistant",
        ),
    ]


@prompt
async def nutrient_browse_food_groups(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to browse foods by food group category."""
    if lang == "fr":
        return (
            "Utilisez nutrient_list_food_groups pour voir tous les groupes alimentaires disponibles, "
            "puis nutrient_search_by_food_group avec l'identifiant du groupe "
            "pour parcourir les aliments dans cette catégorie. "
            "Consultez data://nutrient/food-groups pour la liste des groupes avec identifiants."
        )
    return (
        "Use nutrient_list_food_groups to see all available food groups, "
        "then nutrient_search_by_food_group with the group ID "
        "to browse foods in that category. "
        "See data://nutrient/food-groups for the list of groups with IDs."
    )


@prompt
async def nutrient_check_daily_values(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through interpreting nutrient amounts against recommended daily values.

    Chains nutrient_get_nutrient_amounts -> interprets results against
    Canadian daily reference intake values.
    """
    if lang == "fr":
        return [
            Message(
                "Pour quel aliment souhaitez-vous vérifier les apports nutritifs quotidiens? "
                "Je comparerai la composition nutritionnelle avec les valeurs nutritives de référence canadiennes.",
                role="user",
            ),
            Message(
                "Je vais utiliser nutrient_get_nutrient_amounts pour récupérer la composition nutritionnelle complète, "
                "puis interpréter chaque nutriment par rapport aux valeurs quotidiennes recommandées (VQ) "
                "selon les guides canadiens — Santé Canada recommande 2000 kcal/jour comme référence adulte standard.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which food would you like to check against recommended daily values? "
            "I will compare the nutritional composition against Canadian daily reference intake values.",
            role="user",
        ),
        Message(
            "I will use nutrient_get_nutrient_amounts to retrieve the complete nutritional composition, "
            "then interpret each nutrient against recommended Daily Values (DV) "
            "following Canadian guidelines — Health Canada uses 2000 kcal/day as the standard adult reference.",
            role="assistant",
        ),
    ]
