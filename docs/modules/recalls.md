# :warning: Recalls & Safety Alerts

Food, vehicle, and health product recalls from [Healthy Canadians](https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (6)

<!-- CATALOG:recalls:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `recalls_get_recent` | Get the most recent product recalls across all Health Canada categories. | `limit`, `offset` |
| `recalls_search` | Search Health Canada recalls by keyword with optional category filter. | `keyword`, `category`, `limit`, `offset` |
| `recalls_get_details` | Get full details of a specific Health Canada recall by recall ID. | `recall_id` |
| `recalls_get_food` | Get food product recalls from Health Canada. | `keyword`, `limit`, `offset` |
| `recalls_get_vehicles` | Get vehicle recalls from Transport Canada and Health Canada. | `keyword`, `limit`, `offset` |
| `recalls_get_health_products` | Get health product recalls from Health Canada. | `keyword`, `limit`, `offset` |
<!-- CATALOG:recalls:end -->

## Prompts (4)

| Prompt | Type | Description |
|--------|------|-------------|
| `recalls_investigate_alert` | Guided | Investigate a recall -- search -> details -> related alerts |
| `recalls_quick_search` | Quick | Search for recalls by keyword |
| `recalls_check_food_safety` | Quick | Check for food product recalls |
| `recalls_vehicle_safety` | Quick | Check for vehicle recalls |

## Resources (6)

| URI | Type | Description |
|-----|------|-------------|
| `data://recalls/categories` | Catalog | Recall category codes (food, vehicle, health-product, etc.) |
| `data://recalls/severity-levels` | Catalog | Recall risk severity levels |
| `docs://recalls/search-tips` | Guide | Search strategies, category filtering, pagination |
| `docs://recalls/food-safety-guide` | Guide | How to interpret food recall risk levels and actions |
| `template://recalls/safety-alert` | Template | Safety alert summary with `{product}`, `{hazard}`, `{action}` |
| `template://recalls/recall-report` | Template | Full recall report template |
