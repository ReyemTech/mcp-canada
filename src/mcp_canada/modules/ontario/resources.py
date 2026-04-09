"""MCP resources for the Ontario Open Data module.

Provides reference catalogs, documentation guides, and response templates for
the Ontario government open data portal (data.ontario.ca). All resources use
type-prefixed URIs:
- data://ontario/...    — JSON reference catalogs (machine-parseable)
- docs://ontario/...    — Markdown documentation guides (human-readable)
- template://ontario/...— Markdown response templates with {placeholder} syntax

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
    "data://ontario/ministries",
    mime_type="application/json",
    name="ontario_ministries",
    title="Ontario Government Ministries and Organizations",
)
def ontario_ministries() -> str:
    """Ontario government ministries and agencies that publish open data.

    Use these organization names with ontario_search_datasets(organization=...)
    to filter datasets by publishing ministry.
    Format: {"slug": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "ministry-of-health": {
                "en": "Ministry of Health",
                "fr": "Ministère de la Santé",
            },
            "ministry-of-education": {
                "en": "Ministry of Education",
                "fr": "Ministère de l'Éducation",
            },
            "ministry-of-finance": {
                "en": "Ministry of Finance",
                "fr": "Ministère des Finances",
            },
            "ministry-of-transportation": {
                "en": "Ministry of Transportation",
                "fr": "Ministère des Transports",
            },
            "ministry-of-the-environment-conservation-and-parks": {
                "en": "Ministry of the Environment, Conservation and Parks",
                "fr": "Ministère de l'Environnement, de la Protection de la nature et des Parcs",
            },
            "ministry-of-municipal-affairs-and-housing": {
                "en": "Ministry of Municipal Affairs and Housing",
                "fr": "Ministère des Affaires municipales et du Logement",
            },
            "ministry-of-agriculture-food-and-rural-affairs": {
                "en": "Ministry of Agriculture, Food and Rural Affairs",
                "fr": "Ministère de l'Agriculture, de l'Alimentation et des Affaires rurales",
            },
            "ontario-health": {
                "en": "Ontario Health",
                "fr": "Santé Ontario",
            },
            "ontario-institute-for-cancer-research": {
                "en": "Ontario Institute for Cancer Research",
                "fr": "Institut ontarien de recherche sur le cancer",
            },
            "ministry-of-labour-immigration-training-and-skills-development": {
                "en": "Ministry of Labour, Immigration, Training and Skills Development",
                "fr": "Ministère du Travail, de l'Immigration, de la Formation et du Développement des compétences",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ontario/popular-datasets",
    mime_type="application/json",
    name="ontario_popular_datasets",
    title="Popular Ontario Open Datasets",
)
def ontario_popular_datasets() -> str:
    """Commonly used Ontario government datasets with IDs and descriptions.

    Use dataset IDs with ontario_get_dataset_details to retrieve full metadata.
    """
    return json.dumps(
        [
            {
                "id": "f52a6457-fb37-4267-acde-11a1e57c4dc8",
                "en": "Ontario Population Projections (2024-2051) — regional demographic forecasts",
                "fr": "Projections de population de l'Ontario (2024-2051) — prévisions démographiques régionales",
                "tool": "ontario_get_population_projections",
            },
            {
                "id": "covid-19-vaccine-data-in-ontario",
                "en": "COVID-19 Vaccination Data in Ontario — cumulative doses by PHU",
                "fr": "Données sur la vaccination contre la COVID-19 en Ontario — doses cumulatives par bureau de santé",
                "tool": "ontario_get_resource",
            },
            {
                "id": "school-information-and-student-demographics",
                "en": "School Information and Student Demographics — all Ontario schools",
                "fr": "Information sur les écoles et données démographiques des élèves — toutes les écoles de l'Ontario",
                "tool": "ontario_get_resource",
            },
            {
                "id": "ontario-air-quality-data",
                "en": "Ontario Air Quality Data — provincial monitoring network",
                "fr": "Données sur la qualité de l'air en Ontario — réseau de surveillance provincial",
                "tool": "ontario_get_resource",
            },
            {
                "id": "ministry-of-transportation-open-data",
                "en": "Ontario Traffic Volumes — annual AADT counts at highway locations",
                "fr": "Volumes de circulation en Ontario — débits journaliers annuels moyens sur les autoroutes",
                "tool": "ontario_get_resource",
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ontario/resource-formats",
    mime_type="application/json",
    name="ontario_resource_formats",
    title="Ontario Open Data Resource Formats",
)
def ontario_resource_formats() -> str:
    """Available resource file formats on data.ontario.ca.

    Use these format identifiers to filter resources when calling
    ontario_get_dataset_details. Not all formats are available for every dataset.
    """
    return json.dumps(
        {
            "CSV": {
                "en": "Comma-separated values — most common tabular format, machine-readable",
                "fr": "Valeurs séparées par des virgules — format tabulaire le plus courant, lisible par machine",
            },
            "XLSX": {
                "en": "Microsoft Excel workbook — may contain multiple sheets",
                "fr": "Classeur Microsoft Excel — peut contenir plusieurs feuilles",
            },
            "JSON": {
                "en": "JavaScript Object Notation — structured data, machine-readable",
                "fr": "Notation d'objet JavaScript — données structurées, lisible par machine",
            },
            "GEOJSON": {
                "en": "GeoJSON — geographic features with geometry",
                "fr": "GeoJSON — entités géographiques avec géométrie",
            },
            "SHP": {
                "en": "Shapefile — geographic vector data format (GIS)",
                "fr": "Fichier de forme — format de données vectorielles géographiques (SIG)",
            },
            "PDF": {
                "en": "Portable Document Format — human-readable reports",
                "fr": "Format de document portable — rapports lisibles par l'humain",
            },
            "XML": {
                "en": "Extensible Markup Language — structured data",
                "fr": "Langage de balisage extensible — données structurées",
            },
            "API": {
                "en": "Application Programming Interface — live data endpoint",
                "fr": "Interface de programmation d'application — point de terminaison de données en direct",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://ontario/ckan-guide",
    mime_type="text/markdown",
    name="ontario_ckan_guide",
    title="Ontario Open Data Portal (data.ontario.ca) Guide",
)
def ontario_ckan_guide() -> str:
    """Overview of the Ontario open data portal, CKAN API usage, and search tips.

    Explains how to navigate data.ontario.ca using the CKAN API,
    common search strategies, and how to download resources.
    """
    return """# Ontario Open Data Portal Guide (data.ontario.ca)

## Overview

The Ontario government open data portal (data.ontario.ca) is powered by CKAN
and contains thousands of datasets from Ontario ministries and agencies.

**API Base URL:** `https://data.ontario.ca/api/3/`
**Portal URL:** `https://data.ontario.ca`

## Searching Datasets

Use `ontario_search_datasets` to search by keyword:
```
ontario_search_datasets(query="school enrollment", limit=10)
```

Filter by organization (ministry):
```
ontario_search_datasets(query="health", organization="ministry-of-health")
```

Use `ontario_list_organizations` to see all available organization names.

## Dataset Details

Once you find a dataset, use `ontario_get_dataset_details` with the dataset ID
or slug to get full metadata including all available resource files:
```
ontario_get_dataset_details("f52a6457-fb37-4267-acde-11a1e57c4dc8")
```

## Downloading Resources

Each dataset has one or more resource files (CSV, XLSX, GeoJSON, etc.).
Use `ontario_get_resource` with the resource ID to download and parse:
```
ontario_get_resource("resource-id-here")
```

## Dataset Statistics

Use `ontario_get_dataset_stats` to get summary statistics for a dataset
without downloading the full file.

## Search Tips

- Use specific terms (e.g., "elementary school enrollment" not just "school")
- Ontario dataset titles are in English only (no French titles in CKAN)
- Tags and descriptions may contain French content
- Ministry names use lowercase hyphenated slugs (e.g., "ministry-of-health")
- Some datasets have "datastore_active: true" meaning they support SQL-like queries

## Data Licenses

Most Ontario open data is licensed under the Open Government Licence – Ontario:
`https://www.ontario.ca/page/open-government-licence-ontario`

Data may be freely used, modified, and distributed with attribution.
"""


@resource(
    "docs://ontario/population-projections-guide",
    mime_type="text/markdown",
    name="ontario_population_projections_guide",
    title="Ontario Population Projections Data Guide",
)
def ontario_population_projections_guide() -> str:
    """Guide to Ontario population projections data source, methodology, and regions.

    Explains the Ontario Ministry of Finance population projections model,
    available planning regions, and how to interpret the data.
    """
    return """# Ontario Population Projections Guide

## Data Source

Ontario population projections are produced by the Ontario Ministry of Finance.
The current dataset covers **2024 to 2051** across all Ontario planning regions.

**Tool:** `ontario_get_population_projections`
**Dataset ID:** `f52a6457-fb37-4267-acde-11a1e57c4dc8`

## Projection Methodology

The Ontario Ministry of Finance uses a cohort-component model:
- Starts with a base population (Statistics Canada census estimates)
- Models births, deaths, and migration for each future year
- Produces projections at the provincial, regional, and sub-regional level

Note: Projections are **not forecasts** — they show what would happen under
assumed demographic trends, not what will definitely happen.

## Available Geographic Levels

| Level | Description |
|-------|-------------|
| Province | Total Ontario population |
| Planning region | 8 planning regions (e.g., GTA, Eastern Ontario) |
| Census division (CD) | 49 census divisions across Ontario |

## Planning Regions

1. Greater Toronto Area (GTA)
2. Central Ontario (excluding GTA)
3. Hamilton-Niagara Peninsula
4. Kitchener-Waterloo-Barrie
5. London
6. Ottawa
7. Northeast Ontario
8. Northwest Ontario

## Data Variables

The projections include:
- Total population by year
- Population by 5-year age group and sex
- Age dependency ratios
- Population growth rates

## Usage Notes

- No French variant of this dataset exists (English-only XLSX)
- The `lang` parameter is accepted but uses the same source file for both languages
- Year range available: 2024 to 2051 (annual intervals)
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://ontario/dataset-report",
    mime_type="text/markdown",
    name="ontario_dataset_report_template",
    title="Ontario Open Data Dataset Summary Report Template",
)
def ontario_dataset_report_template() -> str:
    """Template for formatting an Ontario open data dataset summary report.

    Replace {placeholder} values with actual data from Ontario tools
    before presenting to the user.
    """
    return """# Ontario Open Data Report: {dataset_title}

**Dataset ID:** {dataset_id}
**Organization:** {organization}
**Last Updated:** {last_updated}
**Source:** data.ontario.ca

## Description

{description}

## Resources Available

| Name | Format | Size | Last Modified |
|------|--------|------|---------------|
{resource_rows}

## Data Preview

{data_preview}

## Key Statistics

- Total rows: {row_count}
- Columns: {column_names}
- Date range: {date_range}

## Notes

{notes}

Data retrieved from the Ontario Open Data Portal (data.ontario.ca).
Licensed under the Open Government Licence – Ontario.
"""
