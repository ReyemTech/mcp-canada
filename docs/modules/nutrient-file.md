# :apple: Canadian Nutrient File

Food nutrition data from [Health Canada's CNF](https://food-nutrition.canada.ca/api/canadian-nutrient-file/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (8)

<!-- CATALOG:nutrient-file:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `nutrient_search_foods` | Search Canadian Nutrient File foods by name using client-side filtering. | `query` |
| `nutrient_get_food_details` | Get detailed information about a specific food item from the Canadian Nutrient File. | `food_id` |
| `nutrient_get_nutrient_amounts` | Get all nutrient amounts per 100g for a specific food from the Canadian Nutrient File. | `food_id` |
| `nutrient_get_serving_sizes` | Get serving size measures and conversion factors for a food item. | `food_id` |
| `nutrient_search_by_food_group` | List all foods within a specific food group from the Canadian Nutrient File. | `food_group_id` |
| `nutrient_list_nutrients` | List all nutrients available in the Canadian Nutrient File database. | -- |
| `nutrient_list_food_groups` | List all food group categories in the Canadian Nutrient File database. | -- |
| `nutrient_compare_foods` | Compare nutritional content of 2-5 foods from the Canadian Nutrient File. | `food_ids`, `format`, `nutrients` |
<!-- CATALOG:nutrient-file:end -->

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `nutrient_analyze_food` | Guided | Full nutrition analysis -- search -> amounts -> serving sizes |
| `nutrient_quick_search` | Quick | Search for foods in the Canadian Nutrient File |
| `nutrient_compare_foods` | Guided | Compare nutritional content across multiple foods |
| `nutrient_browse_food_groups` | Quick | List all foods in a food group category |
| `nutrient_check_daily_values` | Quick | Look up daily value nutrient thresholds |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://nutrient/food-groups` | Catalog | CNF food group IDs (1-25) with bilingual names |
| `data://nutrient/common-nutrients` | Catalog | Key nutrient IDs for common dietary analysis |
| `data://nutrient/serving-size-measures` | Catalog | Common measure units used in CNF serving sizes |
| `docs://nutrient/cnf-guide` | Guide | CNF data structure, food_id vs food_code, API overview |
| `docs://nutrient/interpretation-guide` | Guide | How to interpret per-100g nutrient values and daily values |
| `template://nutrient/food-profile` | Template | Food nutrition profile with `{food_name}`, `{nutrients}`, `{serving_size}` |
| `template://nutrient/comparison-report` | Template | Multi-food comparison report template |
