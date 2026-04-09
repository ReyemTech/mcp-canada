"""MCP resources for the Bank of Canada module.

Provides reference catalogs, documentation guides, and response templates for
the Bank of Canada Valet API. All resources use type-prefixed URIs:
- data://boc/...    — JSON reference catalogs (machine-parseable)
- docs://boc/...    — Markdown documentation guides (human-readable)
- template://boc/...— Markdown response templates with {placeholder} syntax

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
    "data://boc/currency-codes",
    mime_type="application/json",
    name="boc_currency_codes",
    title="Bank of Canada Currency Codes",
)
def boc_currency_codes() -> str:
    """Valid currency codes for the Bank of Canada Valet FX series.

    Use this catalog to find the currency parameter for boc_get_exchange_rates.
    Format: {"CODE": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "USD": {"en": "US Dollar", "fr": "Dollar américain"},
            "EUR": {"en": "Euro", "fr": "Euro"},
            "GBP": {"en": "British Pound", "fr": "Livre sterling"},
            "JPY": {"en": "Japanese Yen", "fr": "Yen japonais"},
            "CHF": {"en": "Swiss Franc", "fr": "Franc suisse"},
            "AUD": {"en": "Australian Dollar", "fr": "Dollar australien"},
            "NZD": {"en": "New Zealand Dollar", "fr": "Dollar néo-zélandais"},
            "SEK": {"en": "Swedish Krona", "fr": "Couronne suédoise"},
            "NOK": {"en": "Norwegian Krone", "fr": "Couronne norvégienne"},
            "DKK": {"en": "Danish Krone", "fr": "Couronne danoise"},
            "HKD": {"en": "Hong Kong Dollar", "fr": "Dollar de Hong Kong"},
            "SGD": {"en": "Singapore Dollar", "fr": "Dollar de Singapour"},
            "MXN": {"en": "Mexican Peso", "fr": "Peso mexicain"},
            "CNY": {"en": "Chinese Renminbi", "fr": "Renminbi chinois"},
            "INR": {"en": "Indian Rupee", "fr": "Roupie indienne"},
            "KRW": {"en": "South Korean Won", "fr": "Won sud-coréen"},
            "BRL": {"en": "Brazilian Real", "fr": "Réal brésilien"},
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://boc/interest-rate-types",
    mime_type="application/json",
    name="boc_interest_rate_types",
    title="Bank of Canada Interest Rate Types",
)
def boc_interest_rate_types() -> str:
    """Valid rate_type values for boc_get_interest_rates.

    Maps each rate_type key to bilingual descriptions of the series.
    Use 'all' to retrieve all rate types simultaneously.
    """
    return json.dumps(
        {
            "policy": {
                "en": "Target for the overnight rate (Bank of Canada policy rate)",
                "fr": "Cible du taux à un jour (taux directeur de la Banque du Canada)",
                "series": "V39079",
            },
            "corra": {
                "en": "CORRA — Canadian Overnight Repo Rate Average",
                "fr": "CORRA — Taux moyen des opérations de pension à un jour",
                "series": "AVG.INTWO",
            },
            "bond_2yr": {
                "en": "Government of Canada 2-year benchmark bond yield",
                "fr": "Taux de rendement des obligations de référence du Canada à 2 ans",
                "series": "BD.CDN.2YR.DQ.YLD",
            },
            "bond_5yr": {
                "en": "Government of Canada 5-year benchmark bond yield",
                "fr": "Taux de rendement des obligations de référence du Canada à 5 ans",
                "series": "BD.CDN.5YR.DQ.YLD",
            },
            "bond_10yr": {
                "en": "Government of Canada 10-year benchmark bond yield",
                "fr": "Taux de rendement des obligations de référence du Canada à 10 ans",
                "series": "BD.CDN.10YR.DQ.YLD",
            },
            "all": {
                "en": "All available interest rate series",
                "fr": "Toutes les séries de taux d'intérêt disponibles",
                "series": "multiple",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://boc/commodity-types",
    mime_type="application/json",
    name="boc_commodity_types",
    title="Bank of Canada Commodity Types (BCPI)",
)
def boc_commodity_types() -> str:
    """Valid commodity_type values for boc_get_commodity_prices.

    Maps each commodity_type key to bilingual descriptions of the BCPI sub-index.
    Omit commodity_type to fetch the full BCPI basket.
    """
    return json.dumps(
        {
            "total": {
                "en": "Total Bank of Canada Commodity Price Index (BCPI)",
                "fr": "Indice total des prix des produits de base (BCPI) de la Banque du Canada",
                "series": "M.BCPI",
            },
            "energy": {
                "en": "Energy sub-index (oil, natural gas)",
                "fr": "Sous-indice de l'énergie (pétrole, gaz naturel)",
                "series": "M.ENER",
            },
            "metals": {
                "en": "Metals and minerals sub-index",
                "fr": "Sous-indice des métaux et minéraux",
                "series": "M.MTLS",
            },
            "agriculture": {
                "en": "Agriculture sub-index (grains, oilseeds, livestock)",
                "fr": "Sous-indice de l'agriculture (céréales, oléagineux, bétail)",
                "series": "M.AGRI",
            },
            "forestry": {
                "en": "Forestry products sub-index (lumber, pulp)",
                "fr": "Sous-indice des produits forestiers (bois d'oeuvre, pâte)",
                "series": "M.FOPR",
            },
            "fish": {
                "en": "Fish and seafood sub-index",
                "fr": "Sous-indice des poissons et fruits de mer",
                "series": "M.FISH",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://boc/inflation-indicators",
    mime_type="application/json",
    name="boc_inflation_indicators",
    title="Bank of Canada Inflation Indicators (CPI)",
)
def boc_inflation_indicators() -> str:
    """Valid indicator values for boc_get_inflation_data.

    Maps each indicator key to bilingual descriptions of CPI measures.
    Omit indicator to fetch all CPI measures simultaneously.
    """
    return json.dumps(
        {
            "total": {
                "en": "Headline Consumer Price Index (total CPI, all items)",
                "fr": "Indice des prix à la consommation total (IPC global, tous les articles)",
                "series": "V41690973",
            },
            "trim": {
                "en": "CPI-trim: trims extreme price changes from the total CPI",
                "fr": "IPC-tronqué: élimine les variations extrêmes de prix de l'IPC total",
                "series": "CPI_TRIM",
            },
            "median": {
                "en": "CPI-median: monthly price change at the 50th percentile",
                "fr": "IPC-médian: variation mensuelle des prix au 50e centile",
                "series": "CPI_MEDIAN",
            },
            "common": {
                "en": "CPI-common: tracks common price changes across categories",
                "fr": "IPC-commun: suit les variations communes des prix entre catégories",
                "series": "CPI_COMMON",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://boc/series-naming",
    mime_type="text/markdown",
    name="boc_series_naming_guide",
    title="Bank of Canada Series Naming Convention",
)
def boc_series_naming_guide() -> str:
    """Guide to Bank of Canada Valet API series naming conventions and groups.

    Explains the FX{CURRENCY}CAD naming pattern, available groups,
    and how to discover series using boc_search_series or boc_list_groups.
    """
    return """# Bank of Canada Valet API: Series Naming Guide

## Exchange Rate Series

Exchange rate series follow the pattern `FX{CURRENCY}CAD`:
- `FXUSDCAD` — US Dollar to Canadian Dollar
- `FXEURCAD` — Euro to Canadian Dollar
- `FXGBPCAD` — British Pound to Canadian Dollar
- `FXJPYCAD` — Japanese Yen to Canadian Dollar

Use the `currency` parameter in `boc_get_exchange_rates` — the tool builds the
series name automatically (e.g., `currency='USD'` → `FXUSDCAD`).

## Interest Rate Series

Interest rate series have non-obvious Bank of Canada internal codes:
- `V39079` — Target for the overnight rate (policy rate)
- `AVG.INTWO` — CORRA overnight average
- `BD.CDN.2YR.DQ.YLD` — 2-year Government of Canada bond yield
- `BD.CDN.5YR.DQ.YLD` — 5-year bond yield
- `BD.CDN.10YR.DQ.YLD` — 10-year bond yield

Use `boc_get_interest_rates` with `rate_type` instead of raw series names.

## CPI / Inflation Series

- `V41690973` — Total CPI (all items)
- `CPI_TRIM` — CPI-trim
- `CPI_MEDIAN` — CPI-median
- `CPI_COMMON` — CPI-common

Use `boc_get_inflation_data` with the `indicator` parameter.

## BCPI Commodity Series

- `M.BCPI` — Total commodity price index
- `M.ENER` — Energy sub-index
- `M.MTLS` — Metals sub-index
- `M.AGRI` — Agriculture sub-index
- `M.FOPR` — Forestry sub-index
- `M.FISH` — Fish sub-index

Use `boc_get_commodity_prices` with the `commodity_type` parameter.

## Data Groups

Groups allow bulk retrieval of all series in a category:
- `FX_RATES_DAILY` — All daily FX exchange rates
- `BCPI_MONTHLY` — All monthly BCPI commodity price series
- `CPI_MONTHLY` — All monthly CPI inflation series

## Discovery Tools

- `boc_search_series` — Search by keyword to find series names
- `boc_list_groups` — Browse all available data groups
- `boc_get_series_metadata` — Get label/description for a known series code
"""


@resource(
    "docs://boc/api-quirks",
    mime_type="text/markdown",
    name="boc_api_quirks_guide",
    title="Bank of Canada Valet API Quirks",
)
def boc_api_quirks_guide() -> str:
    """Guide to known Bank of Canada Valet API quirks, limits, and gotchas.

    Read this before querying to understand date formats, null values,
    rate limiting, and group vs single-series response differences.
    """
    return """# Bank of Canada Valet API: Known Quirks

## Date Formats

- All dates use ISO 8601 format: `YYYY-MM-DD` (e.g., `2024-01-15`)
- The API ignores time components — date-only strings are correct
- `recent=N` returns the N most recent observations (default: 10)
- `start_date` + `end_date` override `recent` when both are provided

## Null Observations

Some observations have `{"v": null}` for days when no data was published
(weekends, holidays). The BoC tools filter these out before returning.

## Rate Limiting

The Valet API has no documented rate limit but responds best at ≤10 req/s.
The mcp-canada module enforces 10 req/s automatically via TokenBucket.

## Group vs Single-Series Responses

- Group endpoints (`/observations/group/{GROUP}/json`) return all series in one call
- Single-series endpoints (`/observations/{SERIES}/json`) support comma-separated names
- Multi-series single-series calls: use comma-separated in `boc_get_observations`

## Metadata Response Shape

- Series list: `{"series": {NAME: {label, description, link}}}`
- Series detail: `{"seriesDetails": {NAME: {...}}}` (note capital D, trailing S)
- Group list: `{"groups": {NAME: {label, description, link}}}`

## Cache TTLs

- Observation data: cached 1 hour (TTL 3600s)
- Series/group metadata: cached 24 hours (TTL 86400s)
- `_meta.cached: true` in responses indicates data from cache

## Common 404 Causes

1. Wrong series name (e.g., `FXCADUSD` doesn't exist — it's `FXUSDCAD`)
2. Querying FX series that the BoC doesn't publish (check currency codes catalog)
3. Typos in group names — use exact names from `boc_list_groups`

## BCPI Frequency

BCPI series are monthly, not daily. Date ranges spanning days within a month
will return the same monthly value. Always use month-start dates for BCPI.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://boc/rate-report",
    mime_type="text/markdown",
    name="boc_rate_report_template",
    title="Bank of Canada Rate Analysis Report Template",
)
def boc_rate_report_template() -> str:
    """Template for formatting a Bank of Canada exchange rate or interest rate report.

    Replace {placeholder} values with actual data from boc_get_exchange_rates
    or boc_get_interest_rates before presenting to the user.
    """
    return """# {currency} / CAD Exchange Rate Report

**Period:** {start_date} to {end_date}
**Source:** Bank of Canada Valet API

## Latest Rate

**{latest_value}** CAD per {currency} (as of {latest_date})

## Trend Summary

{trend_description}

## Data Table

| Date | Rate (CAD) | Change |
|------|-----------|--------|
{data_rows}

## Key Observations

- Highest rate: **{max_value}** on {max_date}
- Lowest rate: **{min_value}** on {min_date}
- Average rate: **{avg_value}** over the period

## Notes

Data retrieved from the Bank of Canada Valet API.
Exchange rates are noon buying rates quoted as foreign currency per CAD.
"""
