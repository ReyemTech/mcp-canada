"""MCP resources for the StatCan module.

Provides reference catalogs, documentation guides, and response templates for
the Statistics Canada WDS and SDMX APIs. All resources use type-prefixed URIs:
- data://statcan/...    — JSON reference catalogs (machine-parseable)
- docs://statcan/...    — Markdown documentation guides (human-readable)
- template://statcan/...— Markdown response templates with {placeholder} syntax

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
    "data://statcan/frequency-codes",
    mime_type="application/json",
    name="statcan_frequency_codes",
    title="Statistics Canada WDS Frequency Codes",
)
def statcan_frequency_codes() -> str:
    """Frequency codes used in Statistics Canada WDS cube and series metadata.

    Maps WDS frequencyCode integers to bilingual labels.
    Use this catalog to interpret the frequencyCode field in sc_get_cube_metadata.
    Format: {"code": {"en": "English label", "fr": "Libellé en français"}}

    Codes are transcribed from StatCan's published set (getCodeSets) and are NOT
    contiguous — there is no 3, 5, 8, or 10.
    """
    return json.dumps(
        {
            "1": {"en": "Daily", "fr": "Quotidienne"},
            "2": {"en": "Weekly", "fr": "Hebdomadaire"},
            "4": {"en": "Biweekly", "fr": "Aux 2 semaines"},
            "6": {"en": "Monthly", "fr": "Mensuelle"},
            "7": {"en": "Bimonthly", "fr": "Aux 2 mois"},
            "9": {"en": "Quarterly", "fr": "Trimestrielle"},
            "11": {"en": "Semi-annual", "fr": "Semestrielle"},
            "12": {"en": "Annual", "fr": "Annuelle"},
            "13": {"en": "Every 2 years", "fr": "Aux 2 ans"},
            "14": {"en": "Every 3 years", "fr": "Aux 3 ans"},
            "15": {"en": "Every 4 years", "fr": "Aux 4 ans"},
            "16": {"en": "Every 5 years", "fr": "Aux 5 ans"},
            "17": {"en": "Every 10 years", "fr": "Aux 10 ans"},
            "18": {"en": "Occasional", "fr": "Occasionnelle"},
            "19": {"en": "Occasional Quarterly", "fr": "Occasionnelle trimestrielle"},
            "20": {"en": "Occasional Monthly", "fr": "Occasionnelle mensuelle"},
            "21": {"en": "Occasional Daily", "fr": "Occasionnelle quotidienne"},
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://statcan/scalar-factor-codes",
    mime_type="application/json",
    name="statcan_scalar_factor_codes",
    title="Statistics Canada WDS Scalar Factor Codes",
)
def statcan_scalar_factor_codes() -> str:
    """Scalar factor codes used in Statistics Canada WDS series metadata.

    Maps WDS scalarFactorCode integers to bilingual labels indicating the
    unit multiplier applied to observation values.
    Format: {"code": {"en": "English label", "fr": "Libellé en français"}}

    Code N means 10^N. The published set is exactly 0-9; there is no 888.
    """
    return json.dumps(
        {
            "0": {"en": "units", "fr": "unités"},
            "1": {"en": "tens", "fr": "dizaines"},
            "2": {"en": "hundreds", "fr": "centaines"},
            "3": {"en": "thousands", "fr": "milliers"},
            "4": {"en": "tens of thousands", "fr": "dizaines de milliers"},
            "5": {"en": "hundreds of thousands", "fr": "centaines de milliers"},
            "6": {"en": "millions", "fr": "millions"},
            "7": {"en": "tens of millions", "fr": "dizaines de millions"},
            "8": {"en": "hundreds of millions", "fr": "centaines de millions"},
            "9": {"en": "billions", "fr": "milliards"},
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://statcan/status-codes",
    mime_type="application/json",
    name="statcan_status_codes",
    title="Statistics Canada WDS Observation Status Codes",
)
def statcan_status_codes() -> str:
    """Observation status symbols used in Statistics Canada WDS data responses.

    Maps WDS status letter codes to bilingual descriptions.
    An empty string status means the observation is a normal value.
    Format: {"symbol": {"en": "English meaning", "fr": "Signification en français"}}
    """
    return json.dumps(
        {
            "": {"en": "Normal observation (no qualifier)", "fr": "Observation normale (sans qualificatif)"},
            "A": {"en": "Preliminary data (subject to revision)", "fr": "Données préliminaires (sous réserve de révision)"},
            "B": {"en": "Revised data", "fr": "Données révisées"},
            "C": {"en": "Data corrected after publication", "fr": "Données corrigées après publication"},
            "D": {"en": "Data suppressed (confidential)", "fr": "Données supprimées (confidentielles)"},
            "E": {"en": "Estimate", "fr": "Estimation"},
            "F": {"en": "Forecasted data", "fr": "Données prévisionnelles"},
            "N": {"en": "Not available (no observation)", "fr": "Non disponible (aucune observation)"},
            "P": {"en": "Provisional", "fr": "Provisoire"},
            "S": {"en": "Survey values suppressed", "fr": "Valeurs d'enquête supprimées"},
            "V": {"en": "Validated data", "fr": "Données validées"},
            "X": {"en": "Suppressed to meet confidentiality requirements", "fr": "Supprimées pour respecter la confidentialité"},
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://statcan/uom-codes",
    mime_type="application/json",
    name="statcan_uom_codes",
    title="Statistics Canada WDS Units of Measure Codes",
)
def statcan_uom_codes() -> str:
    """Common units of measure (UOM) codes used in Statistics Canada WDS series.

    Maps WDS uomCode integers to bilingual unit descriptions.
    Use this catalog to interpret the uomCode field in sc_get_series_info_by_vector.
    Format: {"code": {"en": "English unit", "fr": "Unité en français"}}
    """
    return json.dumps(
        {
            "0": {"en": "Not applicable", "fr": "Sans objet"},
            "1": {"en": "Number", "fr": "Nombre"},
            "11": {"en": "Persons", "fr": "Personnes"},
            "15": {"en": "Dollars", "fr": "Dollars"},
            "17": {"en": "Canadian dollars", "fr": "Dollars canadiens"},
            "20": {"en": "Percentage", "fr": "Pourcentage"},
            "21": {"en": "Percent change", "fr": "Variation en pourcentage"},
            "22": {"en": "Rate per 1,000", "fr": "Taux pour 1 000"},
            "23": {"en": "Rate per 100,000", "fr": "Taux pour 100 000"},
            "39": {"en": "Index (2012=100)", "fr": "Indice (2012=100)"},
            "40": {"en": "Index (2002=100)", "fr": "Indice (2002=100)"},
            "50": {"en": "Hours", "fr": "Heures"},
            "60": {"en": "Kilograms", "fr": "Kilogrammes"},
            "81": {"en": "Tonnes", "fr": "Tonnes métriques"},
            "301": {"en": "Tonnes (thousands)", "fr": "Tonnes (milliers)"},
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://statcan/wds-guide",
    mime_type="text/markdown",
    name="statcan_wds_guide",
    title="Statistics Canada WDS API Guide",
)
def statcan_wds_guide() -> str:
    """Overview guide for the Statistics Canada WDS (Web Data Service) REST API.

    Covers rate limits, tiered caching strategy, available endpoints,
    and how mcp-canada wraps them into sc_* tools.
    """
    return """# Statistics Canada WDS API Guide

## Overview

The Statistics Canada Web Data Service (WDS) provides programmatic access to
the same data available on the Statistics Canada website (www150.statcan.gc.ca).
Data is organized into **cubes** (datasets) identified by a **productId**
(e.g., `14-10-0023-01` for employment by industry).

## Rate Limits

- **Documented limit:** 25 requests per second
- **mcp-canada limit:** 20 req/s (conservative, via TokenBucket rate limiter)
- Stay below 20 req/s to avoid HTTP 429 responses
- Bulk endpoints (e.g., sc_get_bulk_vector_data) count as 1 request regardless of vector count

## Caching Strategy (Tiered)

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Cube list | 1 hour | Released infrequently, large payload (~5MB) |
| Cube metadata | 24 hours | Dimensions/members rarely change |
| Code sets | 7 days | Frequency/scalar codes are stable |
| Observations | 1 hour | New data released daily/monthly/quarterly |

## Key Endpoints (via sc_* tools)

| Tool | Purpose |
|------|---------|
| `sc_search_cubes` | BM25 full-text search across all cube titles |
| `sc_get_cube_metadata` | Get dimensions, members, and series for a cube |
| `sc_get_code_sets` | Get frequency, scalar, status, and UOM code labels |
| `sc_get_series_info_by_vector` | Get metadata for a known vector ID |
| `sc_get_data_by_vector` | Get observations for one vector (recent N or date range) |
| `sc_get_data_by_coord` | Get observations using productId + coordinate string |
| `sc_get_data_by_date_range` | Get observations across a date range |
| `sc_get_bulk_vector_data` | Fetch multiple vectors in one request (efficient) |
| `sc_get_changed_series` | List vectors updated on a specific release date |
| `sc_get_changed_cubes` | List cubes updated on a specific release date |
| `sc_fetch_vectors_to_store` | Fetch vectors and store them in the local SQLite datastore |

## Data Availability

- Most series go back 10-20+ years
- Release schedule varies by survey (monthly CPI, quarterly GDP, annual census)
- Use `sc_get_changed_series` to detect when new data arrives

## Common Errors

- **INVALID_SERIES**: Vector ID not found — check v prefix and numeric ID
- **UPSTREAM_UNAVAILABLE**: WDS maintenance window (usually 06:00-08:30 EST)
- **RATE_LIMITED**: Slow down requests (retry after retry_after seconds)
"""


@resource(
    "docs://statcan/sdmx-key-syntax",
    mime_type="text/markdown",
    name="statcan_sdmx_key_syntax_guide",
    title="Statistics Canada SDMX Dimension Key Syntax Guide",
)
def statcan_sdmx_key_syntax_guide() -> str:
    """Guide to constructing SDMX dimension keys for Statistics Canada data queries.

    Explains dot-separated key format, wildcard syntax, and how to discover
    valid dimension member codes via sc_get_sdmx_structure.
    """
    return """# Statistics Canada SDMX Dimension Key Syntax

## Overview

SDMX (Statistical Data and Metadata eXchange) provides structured access to
Statistics Canada data with precise dimension filtering. Use `sc_get_sdmx_structure`
to discover dimensions and `sc_get_sdmx_data` to retrieve filtered data.

## Key Format

SDMX dimension keys are dot-separated strings where each position corresponds to
a dimension in the data structure definition (DSD):

```
DIMENSION1.DIMENSION2.DIMENSION3.DIMENSION4
```

### Example: Labour Force Survey (14-10-0023-01)

Dimensions: Geography . Sex . Age Group . Labour Force Characteristic
```
01.1.1.3   → Canada, both sexes, 15 years and over, employment
01.2.1.3   → Canada, males, 15 years and over, employment
10.1.1.3   → Ontario, both sexes, 15 years and over, employment
```

## Wildcard Character

Use `.` (dot) by itself as a position to select ALL members of that dimension:

```
01..1.3   → Canada, all sexes, 15+, employment
01.1..3   → Canada, males, all age groups, employment
....      → All dimensions wildcard (returns everything — use with caution)
```

## Discovering Valid Codes

1. Call `sc_get_sdmx_structure` with the productId to get all dimensions
2. Each dimension has a list of members with their codes and labels
3. Construct the key by combining member codes in dimension order

## Period Filter

Use the `start_period` and `end_period` parameters (YYYY-MM or YYYY):
```
start_period="2020-01", end_period="2023-12"
```

Or use `lastN` for the N most recent periods.

## SDMX vs WDS

| Feature | WDS (sc_get_data_by_vector) | SDMX (sc_get_sdmx_data) |
|---------|---------------------------|-------------------------|
| Input | Vector ID (v123456) | Dimension key (1.2.3.) |
| Filtering | Single series only | Multi-dimension filtering |
| Discovery | sc_get_cube_metadata | sc_get_sdmx_structure |
| Use case | Known specific series | Slice a dataset by dimension |
"""


@resource(
    "docs://statcan/coordinate-system",
    mime_type="text/markdown",
    name="statcan_coordinate_system_guide",
    title="Statistics Canada WDS Coordinate System Guide",
)
def statcan_coordinate_system_guide() -> str:
    """Guide to the Statistics Canada WDS coordinate system.

    Explains how productId + coordinate string resolves to a vectorId,
    coordinate format, and when to use coord vs vector access.
    """
    return """# Statistics Canada WDS Coordinate System

## Overview

Every Statistics Canada data series has two equivalent identifiers:
- **Vector ID** (e.g., `v41690973`) — a unique numeric identifier
- **Coordinate** — a product ID + dimension member combination

Both point to the same underlying time series.

## Coordinate Format

A coordinate is a dot-separated string of dimension member positions:

```
productId  + "." + d1.d2.d3.d4.d5.d6.d7.d8.d9.d10
```

Example: CPI (Total, Canada)
```
productId: 18100004  (or "18-10-0004-01")
coordinate: 1.1.0.0.0.0.0.0.0.0
```

The coordinate has exactly 10 positions, with unused dimensions set to `0`.

## Looking Up a Coordinate

Use `sc_get_cube_metadata` with a productId to see:
- Available dimensions and their member codes
- How many dimension positions the cube uses

Example workflow:
1. `sc_search_cubes("consumer price index")` → find productId
2. `sc_get_cube_metadata(productId)` → see dimensions and member codes
3. Build coordinate from member positions
4. `sc_get_data_by_coord(productId, coordinate, recent=12)` → get data

## Vector vs Coordinate

| Approach | When to use |
|----------|-------------|
| Vector ID | When you already know the vectorId (e.g., from CANSIM documentation) |
| Coordinate | When exploring a cube interactively via sc_get_cube_metadata |
| SDMX key | When you need to filter by multiple dimensions simultaneously |

## Finding Vector IDs

- `sc_get_series_info_by_coord(productId, coordinate)` → returns vectorId
- `sc_get_cube_metadata` response includes vectorId for each series
- Statistics Canada tables list vector IDs in footnotes
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://statcan/time-series-report",
    mime_type="text/markdown",
    name="statcan_time_series_report_template",
    title="Statistics Canada Time Series Report Template",
)
def statcan_time_series_report_template() -> str:
    """Template for formatting a Statistics Canada time series data report.

    Replace {placeholder} values with actual data from sc_get_data_by_vector
    or sc_get_bulk_vector_data before presenting to the user.
    """
    return """# {product_title} — Time Series Report

**Product ID:** {product_id}
**Vector ID:** {vector_id}
**Period:** {start_date} to {end_date}
**Source:** Statistics Canada WDS

## Series Details

- **Unit of measure:** {unit_of_measure}
- **Scalar factor:** {scalar_factor}
- **Frequency:** {frequency}

## Latest Value

**{latest_value}** {unit_of_measure} (as of {latest_date})

## Trend Summary

{trend_description}

## Data Table

| Date | Value | Status |
|------|-------|--------|
{data_rows}

## Key Statistics

- Highest value: **{max_value}** on {max_date}
- Lowest value: **{min_value}** on {min_date}
- Average: **{avg_value}** over the period

## Notes

{notes}

Data retrieved from the Statistics Canada Web Data Service (WDS).
"""
