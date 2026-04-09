"""MCP resources for the Nutrient File module.

Provides reference catalogs, documentation guides, and response templates for
the Canadian Nutrient File. All resources use type-prefixed URIs:
- data://nutrient/...    — JSON reference catalogs (machine-parseable)
- docs://nutrient/...    — Markdown documentation guides (human-readable)
- template://nutrient/...— Markdown response templates with {placeholder} syntax

IMPORTANT: All resource functions are zero-parameter. Adding any parameter
(even lang) would make FastMCP treat them as ResourceTemplate instead of
FunctionResource, removing them from resources/list.
Bilingual content is embedded inline in a single resource.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://nutrient/food-groups",
    mime_type="application/json",
    name="nutrient_food_groups",
    title="Canadian Nutrient File Food Groups",
)
def nutrient_food_groups() -> str:
    """Food group IDs and bilingual names from the Canadian Nutrient File.

    Use these IDs with nutrient_search_by_food_group to browse foods by category.
    Format: {"id": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "1": {
                "en": "Dairy and Egg Products",
                "fr": "Produits laitiers et oeufs",
            },
            "2": {
                "en": "Spices and Herbs",
                "fr": "Épices et fines herbes",
            },
            "3": {
                "en": "Baby Foods",
                "fr": "Aliments pour bébés",
            },
            "4": {
                "en": "Fats and Oils",
                "fr": "Corps gras et huiles",
            },
            "5": {
                "en": "Poultry Products",
                "fr": "Produits de volaille",
            },
            "6": {
                "en": "Soups, Sauces, and Gravies",
                "fr": "Soupes, sauces et jus de viande",
            },
            "7": {
                "en": "Sausages and Luncheon Meats",
                "fr": "Saucisses et charcuteries",
            },
            "8": {
                "en": "Breakfast Cereals",
                "fr": "Céréales de petit-déjeuner",
            },
            "9": {
                "en": "Fruits and Fruit Juices",
                "fr": "Fruits et jus de fruits",
            },
            "10": {
                "en": "Pork Products",
                "fr": "Produits de porc",
            },
            "11": {
                "en": "Vegetables and Vegetable Products",
                "fr": "Légumes et produits de légumes",
            },
            "12": {
                "en": "Nut and Seed Products",
                "fr": "Noix et graines",
            },
            "13": {
                "en": "Beef Products",
                "fr": "Produits de boeuf",
            },
            "14": {
                "en": "Beverages",
                "fr": "Boissons",
            },
            "15": {
                "en": "Finfish and Shellfish Products",
                "fr": "Poissons et crustacés",
            },
            "16": {
                "en": "Legumes and Legume Products",
                "fr": "Légumineuses et produits de légumineuses",
            },
            "17": {
                "en": "Lamb, Veal, and Game Products",
                "fr": "Produits d'agneau, de veau et de gibier",
            },
            "18": {
                "en": "Baked Products",
                "fr": "Produits de boulangerie",
            },
            "19": {
                "en": "Sweets",
                "fr": "Confiseries et sucreries",
            },
            "20": {
                "en": "Cereal Grains and Pasta",
                "fr": "Céréales et pâtes",
            },
            "21": {
                "en": "Fast Foods",
                "fr": "Restauration rapide",
            },
            "22": {
                "en": "Meals, Entrees, and Sidedishes",
                "fr": "Repas, plats principaux et accompagnements",
            },
            "23": {
                "en": "Snacks",
                "fr": "Grignotines",
            },
            "25": {
                "en": "Restaurant Foods",
                "fr": "Aliments de restaurant",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://nutrient/common-nutrients",
    mime_type="application/json",
    name="nutrient_common_nutrients",
    title="Common Nutrient IDs and Units in the Canadian Nutrient File",
)
def nutrient_common_nutrients() -> str:
    """Key nutrient IDs, names, and units from the Canadian Nutrient File.

    Use these IDs to filter results from nutrient_get_nutrient_amounts.
    Format: {"nutrient_id": {"name_en": "...", "name_fr": "...", "unit": "..."}}
    """
    return json.dumps(
        {
            "208": {
                "name_en": "Energy (kcal)",
                "name_fr": "Énergie (kcal)",
                "unit": "kcal",
                "category": "macronutrient",
            },
            "203": {
                "name_en": "Protein",
                "name_fr": "Protéines",
                "unit": "g",
                "category": "macronutrient",
            },
            "204": {
                "name_en": "Total Fat",
                "name_fr": "Lipides totaux",
                "unit": "g",
                "category": "macronutrient",
            },
            "205": {
                "name_en": "Carbohydrates (total)",
                "name_fr": "Glucides totaux",
                "unit": "g",
                "category": "macronutrient",
            },
            "291": {
                "name_en": "Fibre (total dietary)",
                "name_fr": "Fibres alimentaires totales",
                "unit": "g",
                "category": "macronutrient",
            },
            "269": {
                "name_en": "Sugars (total)",
                "name_fr": "Sucres totaux",
                "unit": "g",
                "category": "macronutrient",
            },
            "307": {
                "name_en": "Sodium",
                "name_fr": "Sodium",
                "unit": "mg",
                "category": "mineral",
            },
            "301": {
                "name_en": "Calcium",
                "name_fr": "Calcium",
                "unit": "mg",
                "category": "mineral",
            },
            "303": {
                "name_en": "Iron",
                "name_fr": "Fer",
                "unit": "mg",
                "category": "mineral",
            },
            "306": {
                "name_en": "Potassium",
                "name_fr": "Potassium",
                "unit": "mg",
                "category": "mineral",
            },
            "401": {
                "name_en": "Vitamin C",
                "name_fr": "Vitamine C",
                "unit": "mg",
                "category": "vitamin",
            },
            "418": {
                "name_en": "Vitamin B12",
                "name_fr": "Vitamine B12",
                "unit": "µg",
                "category": "vitamin",
            },
            "324": {
                "name_en": "Vitamin D",
                "name_fr": "Vitamine D",
                "unit": "IU",
                "category": "vitamin",
            },
            "601": {
                "name_en": "Cholesterol",
                "name_fr": "Cholestérol",
                "unit": "mg",
                "category": "fat",
            },
            "606": {
                "name_en": "Saturated Fat",
                "name_fr": "Acides gras saturés",
                "unit": "g",
                "category": "fat",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://nutrient/serving-size-measures",
    mime_type="application/json",
    name="nutrient_serving_size_measures",
    title="Common Serving Size Measure Descriptions",
)
def nutrient_serving_size_measures() -> str:
    """Common serving size measure descriptions used in the Canadian Nutrient File.

    Use this to interpret the measure_description field from nutrient_get_serving_sizes.
    Format: {"measure": {"en": "English description", "fr": "Description en français", "grams_approx": number}}
    """
    return json.dumps(
        {
            "100g": {
                "en": "100 grams (standard reference amount)",
                "fr": "100 grammes (quantité de référence standard)",
                "grams_approx": 100,
            },
            "cup": {
                "en": "1 cup (236 mL for liquids, ~240g for water)",
                "fr": "1 tasse (236 mL pour les liquides, ~240g pour l'eau)",
                "grams_approx": 236,
            },
            "tbsp": {
                "en": "1 tablespoon (15 mL)",
                "fr": "1 cuillère à soupe (15 mL)",
                "grams_approx": 15,
            },
            "tsp": {
                "en": "1 teaspoon (5 mL)",
                "fr": "1 cuillère à thé (5 mL)",
                "grams_approx": 5,
            },
            "slice": {
                "en": "1 slice (varies by food; typically 25-30g for bread)",
                "fr": "1 tranche (varie selon l'aliment; typiquement 25-30g pour le pain)",
                "grams_approx": 28,
            },
            "piece": {
                "en": "1 piece (varies greatly by food)",
                "fr": "1 morceau (varie considérablement selon l'aliment)",
                "grams_approx": None,
            },
            "oz": {
                "en": "1 ounce (28.35 grams)",
                "fr": "1 once (28,35 grammes)",
                "grams_approx": 28,
            },
            "fl_oz": {
                "en": "1 fluid ounce (30 mL)",
                "fr": "1 once liquide (30 mL)",
                "grams_approx": 30,
            },
            "medium": {
                "en": "1 medium-sized unit (e.g., medium apple ~182g, medium egg ~44g)",
                "fr": "1 unité de taille moyenne (ex: pomme moyenne ~182g, oeuf moyen ~44g)",
                "grams_approx": None,
            },
            "large": {
                "en": "1 large-sized unit (e.g., large egg ~50g, large banana ~136g)",
                "fr": "1 unité de grande taille (ex: grand oeuf ~50g, grande banane ~136g)",
                "grams_approx": None,
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://nutrient/cnf-guide",
    mime_type="text/markdown",
    name="nutrient_cnf_guide",
    title="Guide to the Canadian Nutrient File (CNF)",
)
def nutrient_cnf_guide() -> str:
    """Guide to what the Canadian Nutrient File (CNF) is, its data source, and update frequency.

    Covers CNF scope, how data is collected, and how to use the mcp-canada tools.
    """
    return """# Canadian Nutrient File (CNF) Guide

## What is the CNF?

The Canadian Nutrient File (CNF) is Health Canada's comprehensive database of
nutritional values for foods consumed in Canada. It serves as the standard
reference for nutritional analysis in Canada.

**Website:** https://food-nutrition.canada.ca/cnf-fce/

## Scope and Coverage

The CNF contains approximately **5,800+ foods** organized into 25 food groups,
including:
- Raw, unprocessed foods (meat, poultry, fish, produce, dairy)
- Processed and manufactured foods (breakfast cereals, baked goods)
- Fast food items from Canadian chains
- Restaurant foods
- Baby foods
- Ethnic and regional Canadian foods

## Nutrient Data Available

For each food, the CNF provides values per 100g for up to **150+ nutrients**:
- Macronutrients (energy, protein, fat, carbohydrates, fibre)
- Vitamins (A, B-complex, C, D, E, K)
- Minerals (calcium, iron, potassium, sodium, zinc)
- Fatty acids (saturated, monounsaturated, polyunsaturated, omega-3/6)
- Amino acids
- Phytosterols and other bioactive compounds

## Data Sources

CNF data comes from:
1. **Analytical data** — laboratory testing of Canadian food samples
2. **Recipe calculation** — nutrient values calculated from ingredients
3. **Borrowed data** — from USDA Nutrient Database (for foods not yet tested in Canada)
4. **Manufacturer data** — from food labels and product specifications

## Update Frequency

The CNF is a **static reference database** — it does not change daily.
Updates occur periodically when Health Canada conducts new analyses.
The mcp-canada module caches CNF data for 7 days (TTL: 604800s).

## Limitations

- **Not real-time** — nutrient values may differ from current product formulations
- **Per 100g values** — all amounts are per 100 grams; use serving sizes to convert
- **Average values** — nutrient content varies by season, geography, and cooking method
- **No brand-specific data** — CNF uses generic food descriptions, not specific product brands

## Tools Reference

- `nutrient_search_foods` — Search foods by name
- `nutrient_get_food_details` — Get food description and food group
- `nutrient_get_nutrient_amounts` — Get complete nutritional values per 100g
- `nutrient_get_serving_sizes` — Get reference portion sizes with gram equivalents
- `nutrient_search_by_food_group` — Browse foods by category
- `nutrient_list_food_groups` — List all 25 food groups
- `nutrient_compare_foods` — Side-by-side comparison of two foods
"""


@resource(
    "docs://nutrient/interpretation-guide",
    mime_type="text/markdown",
    name="nutrient_interpretation_guide",
    title="Guide to Interpreting Nutrient Amounts and Daily Values",
)
def nutrient_interpretation_guide() -> str:
    """Guide to interpreting nutrient amounts and comparing against daily intake values.

    Covers Canadian daily reference values, how to interpret per 100g values,
    and how to calculate percent daily value.
    """
    return """# Interpreting Nutrient Amounts: A Guide

## CNF Values Are Per 100 Grams

All nutrient amounts in the Canadian Nutrient File are expressed **per 100 grams**
of the food as described (raw, cooked, drained, etc.).

To calculate for a specific portion:
```
nutrient_in_portion = (amount_per_100g / 100) × portion_weight_in_grams
```

Example: 300g of chicken breast with 31g protein per 100g:
```
(31 / 100) × 300 = 93g protein in that serving
```

## Canadian Daily Reference Intake Values

Health Canada uses **2000 kcal/day** as the standard reference for adults.

### Key Daily Values (Adequate Intake / Recommended Dietary Allowance)

| Nutrient | Daily Value | Notes |
|---------|------------|-------|
| Energy | 2000 kcal | Reference for adult (varies by age/sex) |
| Protein | 50 g | 0.8 g/kg body weight |
| Total Fat | 65 g | ≤30% of calories |
| Saturated Fat | 20 g | ≤10% of calories |
| Carbohydrates | 300 g | 45-65% of calories |
| Dietary Fibre | 28 g | Adults; 38g for men |
| Sodium | 2300 mg | Upper limit (AI: 1500mg) |
| Calcium | 1000 mg | 1200mg for adults 51+ |
| Iron | 8 mg | 18mg for women 19-50 |
| Potassium | 4700 mg | Adequate Intake |
| Vitamin C | 75 mg | 90mg for men |
| Vitamin D | 600 IU | 800 IU for adults 71+ |

## Calculating Percent Daily Value (%DV)

```
%DV = (nutrient_in_portion / daily_value) × 100
```

**Canadian food label interpretation:**
- **5% DV or less** = a little (low)
- **15% DV or more** = a lot (high)

## Adjusting for Cooking

Raw vs cooked values differ significantly:
- Meat loses ~25% weight when cooked (concentrates nutrients per 100g)
- Vegetables may lose water-soluble vitamins (C, B-vitamins) when boiled
- Use `nutrient_search_foods` with "cooked" to find cooked-state values

## Energy Calculation

Total energy is calculated as:
- Protein: 4 kcal/g
- Carbohydrates: 4 kcal/g
- Fat: 9 kcal/g
- Alcohol: 7 kcal/g (not tracked in CNF)
- Fibre: 2 kcal/g (partially fermented)
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://nutrient/food-profile",
    mime_type="text/markdown",
    name="nutrient_food_profile_template",
    title="Single Food Nutrient Profile Report Template",
)
def nutrient_food_profile_template() -> str:
    """Template for formatting a single food nutritional profile.

    Replace {placeholder} values with actual data from nutrient_get_nutrient_amounts
    and nutrient_get_serving_sizes before presenting to the user.
    """
    return """# Nutrient Profile: {food_name}

**CNF Food Code:** {food_code}
**Food Group:** {food_group}
**Description:** {food_description}

## Nutritional Values (per 100g)

### Macronutrients

| Nutrient | Amount | % Daily Value |
|---------|--------|--------------|
| Energy | {energy} kcal | {energy_pct}% |
| Protein | {protein} g | {protein_pct}% |
| Total Fat | {total_fat} g | {fat_pct}% |
| Saturated Fat | {saturated_fat} g | {sat_fat_pct}% |
| Carbohydrates | {carbohydrates} g | {carb_pct}% |
| Dietary Fibre | {fibre} g | {fibre_pct}% |
| Total Sugars | {sugars} g | — |

### Key Micronutrients

| Nutrient | Amount | % Daily Value |
|---------|--------|--------------|
| Sodium | {sodium} mg | {sodium_pct}% |
| Calcium | {calcium} mg | {calcium_pct}% |
| Iron | {iron} mg | {iron_pct}% |
| Potassium | {potassium} mg | — |
| Vitamin C | {vitamin_c} mg | {vitamin_c_pct}% |
| Vitamin D | {vitamin_d} IU | {vitamin_d_pct}% |

## Serving Sizes

| Measure | Weight | Energy |
|---------|--------|--------|
{serving_size_rows}

## Source

Canadian Nutrient File (CNF), Health Canada
Retrieved: {retrieval_timestamp}
"""


@resource(
    "template://nutrient/comparison-report",
    mime_type="text/markdown",
    name="nutrient_comparison_report_template",
    title="Food Nutrient Comparison Report Template",
)
def nutrient_comparison_report_template() -> str:
    """Template for formatting a side-by-side food nutrient comparison report.

    Replace {placeholder} values with actual data from nutrient_compare_foods
    before presenting to the user.
    """
    return """# Nutrient Comparison: {food_1_name} vs {food_2_name}

**Per 100 grams of each food**
**Source:** Canadian Nutrient File (CNF), Health Canada

## Macronutrient Comparison

| Nutrient | {food_1_name} | {food_2_name} | Difference |
|---------|--------------|--------------|------------|
| Energy (kcal) | {food_1_energy} | {food_2_energy} | {energy_diff} |
| Protein (g) | {food_1_protein} | {food_2_protein} | {protein_diff} |
| Total Fat (g) | {food_1_fat} | {food_2_fat} | {fat_diff} |
| Carbohydrates (g) | {food_1_carbs} | {food_2_carbs} | {carb_diff} |
| Fibre (g) | {food_1_fibre} | {food_2_fibre} | {fibre_diff} |

## Micronutrient Comparison

| Nutrient | {food_1_name} | {food_2_name} | Better Source |
|---------|--------------|--------------|--------------|
| Sodium (mg) | {food_1_sodium} | {food_2_sodium} | {sodium_winner} |
| Calcium (mg) | {food_1_calcium} | {food_2_calcium} | {calcium_winner} |
| Iron (mg) | {food_1_iron} | {food_2_iron} | {iron_winner} |
| Vitamin C (mg) | {food_1_vit_c} | {food_2_vit_c} | {vit_c_winner} |

## Summary

{comparison_summary}

Retrieved: {retrieval_timestamp}
"""
