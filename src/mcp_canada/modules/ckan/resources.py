"""MCP resources for the CKAN module.

Provides reference catalogs, documentation guides, and response templates for
the Canadian federal government open data portal (open.canada.ca CKAN API).
All resources use type-prefixed URIs:
- data://ckan/...    — JSON reference catalogs (machine-parseable)
- docs://ckan/...    — Markdown documentation guides (human-readable)
- template://ckan/...— Markdown response templates with {placeholder} syntax

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
    "data://ckan/federal-organizations",
    mime_type="application/json",
    name="ckan_federal_organizations",
    title="Federal Government Organizations on open.canada.ca",
)
def ckan_federal_organizations() -> str:
    """Top federal organizations publishing open data on open.canada.ca.

    Maps organization slugs (used in ckan_search_datasets organization= parameter)
    to bilingual display names.
    Format: {"slug": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "statcan": {
                "en": "Statistics Canada",
                "fr": "Statistique Canada",
            },
            "ec": {
                "en": "Environment and Climate Change Canada",
                "fr": "Environnement et Changement climatique Canada",
            },
            "hc-sc": {
                "en": "Health Canada",
                "fr": "Santé Canada",
            },
            "nrcan-rncan": {
                "en": "Natural Resources Canada",
                "fr": "Ressources naturelles Canada",
            },
            "tc": {
                "en": "Transport Canada",
                "fr": "Transports Canada",
            },
            "fin": {
                "en": "Department of Finance Canada",
                "fr": "Ministère des Finances Canada",
            },
            "cic": {
                "en": "Immigration, Refugees and Citizenship Canada (IRCC)",
                "fr": "Immigration, Réfugiés et Citoyenneté Canada (IRCC)",
            },
            "agr": {
                "en": "Agriculture and Agri-Food Canada",
                "fr": "Agriculture et Agroalimentaire Canada",
            },
            "dfo-mpo": {
                "en": "Fisheries and Oceans Canada",
                "fr": "Pêches et Océans Canada",
            },
            "nrc-cnrc": {
                "en": "National Research Council Canada",
                "fr": "Conseil national de recherches Canada",
            },
            "phac-aspc": {
                "en": "Public Health Agency of Canada",
                "fr": "Agence de la santé publique du Canada",
            },
            "rcmp-grc": {
                "en": "Royal Canadian Mounted Police",
                "fr": "Gendarmerie royale du Canada",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ckan/popular-tags",
    mime_type="application/json",
    name="ckan_popular_tags",
    title="Popular Dataset Tags on open.canada.ca",
)
def ckan_popular_tags() -> str:
    """Common dataset tags used on the Government of Canada open data portal.

    Tags are primarily in English on the federal portal. Use these with
    ckan_search_by_tag to find datasets by topic.
    Format: {"tag": {"en": "English description", "fr": "Description en français"}}
    """
    return json.dumps(
        {
            "agriculture": {
                "en": "Agricultural and agri-food sector data",
                "fr": "Données du secteur agricole et agroalimentaire",
            },
            "environment": {
                "en": "Environmental data (climate, air quality, water)",
                "fr": "Données environnementales (climat, qualité de l'air, eau)",
            },
            "health": {
                "en": "Health statistics and public health data",
                "fr": "Statistiques de santé et données de santé publique",
            },
            "economy": {
                "en": "Economic indicators, GDP, trade data",
                "fr": "Indicateurs économiques, PIB, données commerciales",
            },
            "population": {
                "en": "Demographic and population data",
                "fr": "Données démographiques et de population",
            },
            "transportation": {
                "en": "Transportation and infrastructure data",
                "fr": "Données de transport et d'infrastructure",
            },
            "energy": {
                "en": "Energy production, consumption, and resources",
                "fr": "Production, consommation et ressources énergétiques",
            },
            "immigration": {
                "en": "Immigration, refugees, and citizenship data",
                "fr": "Données sur l'immigration, les réfugiés et la citoyenneté",
            },
            "crime": {
                "en": "Crime statistics and public safety data",
                "fr": "Statistiques criminelles et données de sécurité publique",
            },
            "education": {
                "en": "Education and training statistics",
                "fr": "Statistiques sur l'éducation et la formation",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ckan/resource-formats",
    mime_type="application/json",
    name="ckan_resource_formats",
    title="Common Resource Formats on open.canada.ca",
)
def ckan_resource_formats() -> str:
    """Common resource formats available in federal open datasets.

    Use the format key in ckan_search_datasets to filter by resource format.
    Format: {"FORMAT": {"description": "...", "use_for": "..."}}
    """
    return json.dumps(
        {
            "CSV": {
                "description": "Comma-separated values — tabular data",
                "use_for": "Most common format for structured data analysis",
                "machine_readable": True,
            },
            "JSON": {
                "description": "JavaScript Object Notation — structured data",
                "use_for": "Hierarchical or nested data, API responses",
                "machine_readable": True,
            },
            "XLSX": {
                "description": "Microsoft Excel spreadsheet",
                "use_for": "Tabular data with multiple sheets or formatting",
                "machine_readable": True,
            },
            "XML": {
                "description": "Extensible Markup Language",
                "use_for": "Structured data with metadata, government standards",
                "machine_readable": True,
            },
            "PDF": {
                "description": "Portable Document Format — document",
                "use_for": "Reports, publications (not machine-readable)",
                "machine_readable": False,
            },
            "SHP": {
                "description": "Shapefile — geospatial vector data",
                "use_for": "Geographic boundaries, spatial data",
                "machine_readable": True,
            },
            "GEOJSON": {
                "description": "GeoJSON — geospatial data in JSON",
                "use_for": "Geographic features with coordinates",
                "machine_readable": True,
            },
            "KML": {
                "description": "Keyhole Markup Language — geospatial data",
                "use_for": "Geographic data, Google Earth compatible",
                "machine_readable": True,
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://ckan/search-tips",
    mime_type="text/markdown",
    name="ckan_search_tips_guide",
    title="CKAN Search Tips for open.canada.ca",
)
def ckan_search_tips_guide() -> str:
    """Guide to effective search techniques for the Government of Canada open data portal.

    Covers query syntax, filtering by organization/tag/format, and
    how to use ckan_search_datasets parameters effectively.
    """
    return """# CKAN Search Tips: open.canada.ca

## Basic Search

Use `ckan_search_datasets` with natural language queries:
```
ckan_search_datasets(query="climate data by province")
ckan_search_datasets(query="federal government spending 2023")
```

## Filter by Organization

Narrow results to a specific federal department using the `organization` parameter:
```
ckan_search_datasets(query="immigration", organization="cic")
ckan_search_datasets(query="environment", organization="ec")
```

See the `data://ckan/federal-organizations` resource for organization slugs.

## Filter by Format

Filter for machine-readable formats using the `format` parameter:
```
ckan_search_datasets(query="employment", format="CSV")
ckan_search_datasets(query="geographic boundaries", format="GEOJSON")
```

## Browse by Tag

Use `ckan_search_by_tag` for topic-based discovery:
```
ckan_search_by_tag(tag="agriculture")
ckan_search_by_tag(tag="health")
```

See the `data://ckan/popular-tags` resource for common tags.

## Browse by Organization

Use `ckan_list_organizations` to discover all publishers,
then search within a specific org.

## Pagination

`ckan_search_datasets` returns up to 10 results per call. Use the `page` parameter
to paginate through more results:
```
ckan_search_datasets(query="environment", page=2)
```

## Bilingual Search

The portal has both English and French metadata. Searching in either language
returns datasets with titles/descriptions in that language. For bilingual coverage,
search once in English and once in French.

## Dataset ID

Each dataset has a stable `id` (UUID) and `name` (slug). Use `ckan_get_dataset_details`
with the `id` or `name` to get full metadata including all resources.

## Resource Access

A dataset may have multiple resources (CSV, PDF, API link, etc.). Use
`ckan_get_resource` with a `resource_id` from `ckan_get_dataset_details`
to access a specific file or URL.
"""


@resource(
    "docs://ckan/api-quirks",
    mime_type="text/markdown",
    name="ckan_api_quirks_guide",
    title="CKAN API Quirks for open.canada.ca",
)
def ckan_api_quirks_guide() -> str:
    """Guide to known quirks of the open.canada.ca CKAN API.

    Covers pagination behavior, bilingual metadata handling,
    resource access patterns, and rate limiting.
    """
    return """# open.canada.ca CKAN API: Known Quirks

## Pagination

- Search results are paginated: default 10 per page
- Use `page` parameter in `ckan_search_datasets` to access more results
- Total result count is returned in the response (`count` field)
- CKAN `rows` parameter maps to page size; mcp-canada fixes this at 10

## Bilingual Metadata

The federal portal stores metadata in both English and French:
- `title_translated` — dict with `en` and `fr` keys
- `notes_translated` — dict with `en` and `fr` keys
- `name` — URL-safe slug (English only)
- `id` — UUID stable across language changes

mcp-canada returns bilingual titles where available.

## Resource Access Patterns

A CKAN dataset (`package`) contains multiple resources (files):
1. Call `ckan_get_dataset_details(dataset_id)` to list all resources
2. Each resource has: `id`, `name`, `url`, `format`, `size`
3. Call `ckan_get_resource(resource_id)` to get the download URL
4. Download URLs can be direct file links or API endpoints

## Organization Slugs

Organization slugs used in API calls differ from display names:
- Statistics Canada → `statcan`
- Environment Canada → `ec`
- Health Canada → `hc-sc`

Use `ckan_list_organizations` to get the canonical slug list.

## Cache TTLs

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Search results | 1 hour | Datasets added frequently |
| Dataset details | 1 hour | Metadata updated periodically |
| Org/group lists | 24 hours | Organizations rarely change |

## Rate Limiting

- mcp-canada enforces 10 req/s for the CKAN portal
- The portal itself may throttle at higher rates
- No authentication required for public datasets

## Dataset vs Resource

- **Dataset (package):** A collection of related resources with metadata
- **Resource:** A specific file, URL, or API endpoint within a dataset
- Always inspect dataset details before fetching a resource

## Common 404 Causes

1. Wrong dataset ID — use the UUID `id`, not the display name
2. Resource deleted — datasets may have outdated resource lists
3. Private dataset — some government datasets require authentication
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://ckan/dataset-summary",
    mime_type="text/markdown",
    name="ckan_dataset_summary_template",
    title="CKAN Dataset Summary Report Template",
)
def ckan_dataset_summary_template() -> str:
    """Template for summarizing a federal open dataset from open.canada.ca.

    Replace {placeholder} values with actual data from ckan_get_dataset_details
    before presenting to the user.
    """
    return """# Dataset: {dataset_title}

**ID:** {dataset_id}
**Publisher:** {organization}
**Last updated:** {last_modified}
**License:** {license}

## Description

{description}

## Available Resources

| Name | Format | Size | URL |
|------|--------|------|-----|
{resource_rows}

## Tags

{tags}

## Notes

{notes}

**Source:** Government of Canada Open Data Portal (open.canada.ca)
"""


@resource(
    "template://ckan/resource-report",
    mime_type="text/markdown",
    name="ckan_resource_report_template",
    title="CKAN Resource Details Report Template",
)
def ckan_resource_report_template() -> str:
    """Template for reporting details of a specific resource in a federal open dataset.

    Replace {placeholder} values with actual data from ckan_get_resource
    before presenting to the user.
    """
    return """# Resource: {resource_name}

**Dataset:** {dataset_title}
**Resource ID:** {resource_id}
**Format:** {format}
**Size:** {size}
**Last modified:** {last_modified}

## Access

**Download URL:** {url}

## Description

{description}

## Data Preview

{preview}

## Notes

{notes}

**Source:** Government of Canada Open Data Portal (open.canada.ca)
"""
