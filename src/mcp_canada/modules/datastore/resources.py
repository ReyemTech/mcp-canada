"""MCP resources for the Datastore module.

Provides reference catalogs, documentation guides, and response templates for
the local SQLite datastore. All resources use type-prefixed URIs:
- data://datastore/...    — JSON reference catalogs (machine-parseable)
- docs://datastore/...    — Markdown documentation guides (human-readable)
- template://datastore/...— Markdown response templates with {placeholder} syntax

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
    "data://datastore/column-types",
    mime_type="application/json",
    name="ds_column_types",
    title="Datastore Supported SQLite Column Types",
)
def ds_column_types() -> str:
    """Supported SQLite column types for ds_create_table.

    Maps each supported type to its description and usage guidance.
    Use this catalog to choose the correct type when defining table columns.
    Format: {"TYPE": {"description": "...", "use_for": "...", "example": "..."}}
    """
    return json.dumps(
        {
            "TEXT": {
                "description": "Variable-length text string",
                "use_for": "Names, labels, codes, dates stored as strings, JSON blobs",
                "example": "city TEXT, date TEXT, category TEXT",
            },
            "INTEGER": {
                "description": "Signed integer (up to 8 bytes)",
                "use_for": "Counts, IDs, year values, boolean flags (0/1)",
                "example": "count INTEGER, year INTEGER, id INTEGER",
            },
            "REAL": {
                "description": "Floating-point number (8-byte IEEE 754)",
                "use_for": "Rates, percentages, prices, any decimal value",
                "example": "rate REAL, price REAL, percentage REAL",
            },
            "BLOB": {
                "description": "Binary data stored exactly as provided",
                "use_for": "Raw binary content (uncommon in mcp-canada)",
                "example": "data BLOB",
            },
            "NUMERIC": {
                "description": "Flexible numeric type (SQLite affinity)",
                "use_for": "Values that may be integer or floating-point",
                "example": "value NUMERIC",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://datastore/identifier-rules",
    mime_type="application/json",
    name="ds_identifier_rules",
    title="Datastore Table and Column Naming Rules",
)
def ds_identifier_rules() -> str:
    """Naming rules for table names and column names in the datastore.

    The datastore enforces strict identifier validation to prevent SQL injection.
    Use this catalog to understand valid name formats before calling ds_create_table.
    """
    return json.dumps(
        {
            "pattern": r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$",
            "max_length": 64,
            "rules": [
                "Must start with a letter (a-z, A-Z) or underscore (_)",
                "Remaining characters: letters, digits (0-9), or underscores only",
                "Maximum length: 64 characters",
                "Case-sensitive: 'MyTable' and 'mytable' are different",
                "No spaces, hyphens, dots, or special characters allowed",
            ],
            "valid_examples": [
                "exchange_rates",
                "statcan_cpi",
                "boc_2024",
                "_temp_data",
                "employment_by_province",
            ],
            "invalid_examples": [
                "my-table (hyphen not allowed)",
                "2024data (must start with letter or underscore)",
                "my table (space not allowed)",
                "data.set (dot not allowed)",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://datastore/sql-guide",
    mime_type="text/markdown",
    name="ds_sql_guide",
    title="Datastore SQL Query Guide",
)
def ds_sql_guide() -> str:
    """Guide to supported SQL syntax for ds_query in the local SQLite datastore.

    Covers allowed statements (SELECT, PRAGMA), blocked operations (INSERT/UPDATE/DELETE),
    and practical query examples.
    """
    return """# Datastore SQL Query Guide

## Supported Statements in ds_query

The `ds_query` tool accepts **read-only** SQL statements:

| Statement | Purpose | Example |
|-----------|---------|---------|
| `SELECT` | Query data from one or more tables | `SELECT * FROM rates LIMIT 10` |
| `PRAGMA table_info(name)` | Show column names and types | `PRAGMA table_info(exchange_rates)` |
| `PRAGMA table_list` | List all tables in the database | `PRAGMA table_list` |
| `EXPLAIN` | Show query plan (debugging) | `EXPLAIN SELECT * FROM rates` |

## Blocked Operations

These operations are rejected by ds_query (use the dedicated tools instead):

| Blocked | Use Instead |
|---------|------------|
| `INSERT INTO ...` | `ds_insert_data` |
| `UPDATE ...` | Not supported — drop and recreate |
| `DELETE FROM ...` | `ds_drop_table` to remove entire table |
| `CREATE TABLE ...` | `ds_create_table` |
| `DROP TABLE ...` | `ds_drop_table` |

## Common Query Patterns

### List all tables
```sql
PRAGMA table_list
```

### See table schema
```sql
PRAGMA table_info(my_table)
```

### Select all rows
```sql
SELECT * FROM my_table LIMIT 100
```

### Filter and sort
```sql
SELECT date, value FROM rates
WHERE currency = 'USD'
ORDER BY date DESC
LIMIT 20
```

### Aggregate
```sql
SELECT currency, AVG(rate) as avg_rate, COUNT(*) as n
FROM exchange_rates
GROUP BY currency
ORDER BY avg_rate DESC
```

### JOIN two tables
```sql
SELECT a.date, a.value AS cpi, b.rate AS usd_cad
FROM cpi_data a
JOIN exchange_rates b ON a.date = b.date
WHERE a.date >= '2024-01-01'
ORDER BY a.date
```

### Subquery
```sql
SELECT * FROM rates
WHERE value > (SELECT AVG(value) FROM rates WHERE currency = 'USD')
```

## Row Limit

`ds_query` returns a maximum of 1,000 rows per query. Use `LIMIT` and `OFFSET`
for pagination, or add aggregations to reduce result size.

## Date Handling

SQLite has no native date type. Store dates as TEXT in ISO 8601 format
(`YYYY-MM-DD`) to enable string-based date comparisons and sorting.
"""


@resource(
    "docs://datastore/cross-module-patterns",
    mime_type="text/markdown",
    name="ds_cross_module_patterns_guide",
    title="Datastore Cross-Module SQL Join Patterns",
)
def ds_cross_module_patterns_guide() -> str:
    """Examples of combining data from multiple mcp-canada modules using SQL JOINs.

    Demonstrates the fetch-store-join workflow: fetch from APIs, store in tables,
    then combine with SQL for unified analytics across data sources.
    """
    return """# Cross-Module SQL JOIN Patterns

## Overview

The datastore acts as a local integration layer. Fetch data from any mcp-canada
module, store it, then JOIN across modules using SQL for unified analytics.

## Pattern 1: Exchange Rates + CPI (BoC + StatCan)

**Goal:** Compare USD/CAD rate with inflation over the same period.

**Step 1:** Fetch and store BoC exchange rates
```
boc_get_exchange_rates(currency="USD", recent=24)
→ ds_create_table(table_name="usd_rates", columns=["date TEXT", "rate REAL"])
→ ds_insert_data(table_name="usd_rates", rows=[...])
```

**Step 2:** Fetch and store StatCan CPI
```
sc_fetch_vectors_to_store(vector_ids=["v41690973"], table_name="cpi_data", recent=24)
```

**Step 3:** JOIN and analyze
```sql
SELECT
    r.date,
    r.rate AS usd_cad,
    c.value AS cpi
FROM usd_rates r
JOIN cpi_data c ON r.date = c.ref_period
WHERE r.date >= '2023-01-01'
ORDER BY r.date
```

## Pattern 2: Employment by Province (StatCan)

**Goal:** Compare employment across all provinces in one query.

```
sc_fetch_vectors_to_store(
    vector_ids=["v2057609", "v2057610", "v2057611", ...],
    table_name="employment",
    recent=12
)
```

```sql
SELECT ref_period, vector_id, value
FROM employment
WHERE ref_period >= '2024-01-01'
ORDER BY ref_period, vector_id
```

## Pattern 3: Federal Dataset + StatCan (CKAN + StatCan)

**Goal:** Enrich a CKAN dataset with StatCan economic context.

```
ckan_get_resource(resource_id="...")  → parse and store as ds_insert_data
sc_fetch_vectors_to_store(...)         → store StatCan data

SELECT a.*, b.value AS gdp_growth
FROM ckan_data a
LEFT JOIN statcan_gdp b ON a.year = b.ref_period
```

## Key Tips

- Always include a **date column** (TEXT, ISO 8601) for time-based JOINs
- StatCan `sc_fetch_vectors_to_store` stores: `vector_id`, `ref_period`, `value`, `status`
- Use `COALESCE` for missing values in LEFT JOINs
- Store raw values; apply multipliers (scalar factor) at query time
- Max 1,000 rows per `ds_query` call — use aggregations for large datasets
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://datastore/query-report",
    mime_type="text/markdown",
    name="ds_query_report_template",
    title="Datastore SQL Query Results Report Template",
)
def ds_query_report_template() -> str:
    """Template for formatting SQL query results from the local datastore.

    Replace {placeholder} values with actual data from ds_query
    before presenting to the user.
    """
    return """# SQL Query Results: {table_name}

**Query:** `{sql_query}`
**Rows returned:** {row_count} of {total_rows}
**Executed:** {timestamp}

## Results

{results_table}

## Summary

{summary_description}

## Notes

- Data sourced from local SQLite datastore
- {source_description}
"""


@resource(
    "template://datastore/schema-report",
    mime_type="text/markdown",
    name="ds_schema_report_template",
    title="Datastore Table Schema Report Template",
)
def ds_schema_report_template() -> str:
    """Template for displaying the schema of a datastore table.

    Replace {placeholder} values with actual data from ds_get_schema
    before presenting to the user.
    """
    return """# Table Schema: {table_name}

**Source:** Local SQLite Datastore
**Created:** {created_at}
**Row count:** {row_count}

## Columns

| Column | Type | Notes |
|--------|------|-------|
{column_rows}

## Sample Data

{sample_rows}

## Notes

{notes}
"""
