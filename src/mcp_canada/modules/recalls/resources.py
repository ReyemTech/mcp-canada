"""MCP resources for the Recalls module.

Provides reference catalogs, documentation guides, and response templates for
the Health Canada Recalls API. All resources use type-prefixed URIs:
- data://recalls/...    — JSON reference catalogs (machine-parseable)
- docs://recalls/...    — Markdown documentation guides (human-readable)
- template://recalls/...— Markdown response templates with {placeholder} syntax

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
    "data://recalls/categories",
    mime_type="application/json",
    name="recalls_categories",
    title="Health Canada Recall Categories",
)
def recalls_categories() -> str:
    """Valid recall category codes for the Health Canada Recalls API.

    Use these codes in the category parameter of recalls_search.
    Format: {"CODE": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "FOOD": {
                "en": "Food recalls and safety advisories",
                "fr": "Rappels d'aliments et avis de sécurité alimentaire",
                "tool": "recalls_get_food",
            },
            "VEHICLE": {
                "en": "Vehicle and child restraint system recalls",
                "fr": "Rappels de véhicules et de systèmes de retenue pour enfants",
                "tool": "recalls_get_vehicles",
            },
            "HEALTH": {
                "en": "Health product recalls (drugs, medical devices, natural health products)",
                "fr": "Rappels de produits de santé (médicaments, dispositifs médicaux, produits de santé naturels)",
                "tool": "recalls_get_health_products",
            },
            "CPS": {
                "en": "Consumer product safety alerts and recalls",
                "fr": "Alertes et rappels de produits de consommation",
                "tool": "recalls_search (with category='CPS')",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://recalls/severity-levels",
    mime_type="application/json",
    name="recalls_severity_levels",
    title="Health Canada Recall Severity and Risk Levels",
)
def recalls_severity_levels() -> str:
    """Recall severity and risk classification levels used by Health Canada.

    Helps interpret the risk level of a recall when returned by recalls_get_details.
    """
    return json.dumps(
        {
            "Class I": {
                "en": "Serious and immediate health risk — may cause serious health consequences or death",
                "fr": "Risque grave et immédiat pour la santé — peut causer des conséquences graves ou la mort",
                "urgency": "highest",
            },
            "Class II": {
                "en": "Potential health risk — may cause temporary adverse health consequences",
                "fr": "Risque potentiel pour la santé — peut causer des effets indésirables temporaires",
                "urgency": "moderate",
            },
            "Class III": {
                "en": "Low health risk — unlikely to cause any adverse health consequences",
                "fr": "Faible risque pour la santé — peu susceptible de causer des effets indésirables",
                "urgency": "low",
            },
            "Warning": {
                "en": "Safety warning — no product recall, advisory information only",
                "fr": "Avertissement de sécurité — aucun rappel de produit, informations consultatives seulement",
                "urgency": "advisory",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://recalls/search-tips",
    mime_type="text/markdown",
    name="recalls_search_tips",
    title="Tips for Effective Health Canada Recall Searches",
)
def recalls_search_tips() -> str:
    """Tips for searching Health Canada recalls and safety alerts effectively.

    Covers keyword strategies, category filtering, date filtering,
    and understanding search results.
    """
    return """# Health Canada Recalls: Effective Search Strategies

## Basic Search

Use `recalls_search` with a descriptive keyword:

```
recalls_search(query="listeria", lang="en")
recalls_search(query="Toyota", category="VEHICLE", lang="en")
recalls_search(query="allergen", category="FOOD", lang="en")
```

## Category Filtering

Always filter by category when you know the product type:
- `FOOD` — food and beverage recalls
- `VEHICLE` — automotive recalls (Transport Canada)
- `HEALTH` — drugs, medical devices, natural health products
- `CPS` — consumer products (toys, electronics, household items)

Filtering by category significantly improves result relevance.

## Specialized Category Tools

For common categories, use the dedicated tools for better results:
- `recalls_get_food` — food safety recalls (with optional recent count)
- `recalls_get_vehicles` — automotive recalls
- `recalls_get_health_products` — health product alerts

## Date Filtering

To find recalls in a specific timeframe, use date parameters:
- `start_date` / `end_date` in YYYY-MM-DD format

## Getting Full Details

`recalls_search` returns summary information only.
Always follow up with `recalls_get_details(recall_id=...)` to get:
- Full description and cause
- Complete list of affected products/models
- Consumer instructions (what to do)
- Contact information

## Bilingual Searches

Health Canada publishes recalls in both English and French.
Use `lang="fr"` to get French-language results, or search with French keywords.
"""


@resource(
    "docs://recalls/food-safety-guide",
    mime_type="text/markdown",
    name="recalls_food_safety_guide",
    title="Guide to Understanding Food Recall Notices",
)
def recalls_food_safety_guide() -> str:
    """Guide to understanding Health Canada food recall notices and safety advisories.

    Covers how to read food recall notices, allergen alerts, and what to do.
    """
    return """# Understanding Health Canada Food Recall Notices

## What Triggers a Food Recall?

Food recalls are initiated when a food product may pose a risk to consumers:
- **Pathogen contamination** — Listeria, Salmonella, E. coli, etc.
- **Undeclared allergens** — products containing allergens not listed on the label
- **Foreign material** — glass, metal, plastic fragments
- **Chemical contamination** — pesticides, heavy metals above safe limits
- **Mislabelling** — incorrect ingredients, missing safety warnings

## The Nine Priority Allergens in Canada

Health Canada recognizes these nine priority allergens (must be declared):
1. Peanuts
2. Tree nuts (almonds, cashews, walnuts, etc.)
3. Milk
4. Eggs
5. Fish
6. Shellfish/crustaceans
7. Sesame seeds
8. Wheat and triticale
9. Mustard

Recalls for undeclared allergens are common — always check `recalls_get_food`
if a client reports an allergic reaction to a packaged food.

## Reading a Food Recall Notice

Key fields in `recalls_get_details` for food recalls:
- **reason** — why the product was recalled
- **affected_products** — specific product names, SKUs, UPC codes
- **distribution** — which provinces/regions received the product
- **consumer_advice** — what consumers should do (return, discard)

## What Consumers Should Do

1. **Stop using the product** immediately
2. **Return it** to the place of purchase for a full refund
3. If consumed and feeling ill, **contact a healthcare provider**
4. If serious illness, **call 911 or visit emergency**

## Tools Reference

- `recalls_get_food` — List recent food safety recalls
- `recalls_search(category="FOOD")` — Search food recalls by keyword
- `recalls_get_details` — Full details for a specific recall
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://recalls/safety-alert",
    mime_type="text/markdown",
    name="recalls_safety_alert_template",
    title="Safety Alert Summary Template",
)
def recalls_safety_alert_template() -> str:
    """Template for formatting a Health Canada safety alert summary.

    Replace {placeholder} values with actual data from recalls_get_details
    before presenting to the user.
    """
    return """# Safety Alert: {product_name}

**Recall Number:** {recall_id}
**Date:** {recall_date}
**Category:** {category}
**Risk Level:** {risk_level}

## Summary

{summary}

## Affected Products

{affected_products}

## What To Do

{consumer_advice}

## Source

Health Canada Recalls and Safety Alerts
{recall_url}
"""


@resource(
    "template://recalls/recall-report",
    mime_type="text/markdown",
    name="recalls_recall_report_template",
    title="Detailed Recall Investigation Report Template",
)
def recalls_recall_report_template() -> str:
    """Template for formatting a detailed recall investigation report.

    Replace {placeholder} values with data from recalls_search and
    recalls_get_details before presenting to the user.
    """
    return """# Recall Investigation Report

**Query:** {search_query}
**Date Generated:** {report_date}
**Total Recalls Found:** {total_count}

## Recall Summary

| Recall ID | Product | Category | Date | Risk |
|-----------|---------|----------|------|------|
{recall_table_rows}

## Detailed Findings

{detailed_findings}

## Key Patterns

{key_patterns}

## Recommendations

{recommendations}

## Data Source

Health Canada Recalls and Safety Alerts API
Retrieved: {retrieval_timestamp}
"""
