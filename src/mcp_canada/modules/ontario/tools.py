"""Ontario Open Data Catalogue @tool functions.

Provides 6 intent-based MCP tools for querying the Ontario Government's
Open Data Catalogue (data.ontario.ca) with 3,000+ provincial datasets.
Descriptions are truncated to ~500 chars and resources capped at 10 per
dataset to save agent tokens.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.ontario.client import (
    fetch_dataset_count,
    fetch_dataset_details,
    fetch_organizations,
    fetch_population_projections,
    fetch_resource,
    fetch_search_datasets,
)
from mcp_canada.modules.ontario.constants import BASE_URL
from mcp_canada.shared.envelope import make_error, make_response

# API name and base URL for _meta envelope
_API_NAME = "Ontario Data Catalogue"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Search datasets
# ---------------------------------------------------------------------------


@tool
async def ontario_search_datasets(
    query: str,
    filters: str | None = None,
    rows: int = 10,
    start: int = 0,
    sort: str = "relevance asc",
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Ontario's Open Data Catalogue (data.ontario.ca) for datasets by keyword.

    Use for: finding Ontario provincial government datasets on any topic — health, education, population, housing, transit, environment, finance, infrastructure, energy, and more.
    Keywords: ontario, provincial, open data, search, dataset, catalogue, government, ministry, health, education, population, housing, transit, environment, finance, infrastructure.
    """
    try:
        datasets, cached = await fetch_search_datasets(
            query=query,
            fq=filters,
            rows=rows,
            start=start,
            sort=sort,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        datasets,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Get dataset details
# ---------------------------------------------------------------------------


@tool
async def ontario_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full details for a specific Ontario Open Data dataset including all resources.

    Use for: retrieving complete metadata, resources list, and description for a known dataset ID or name slug from data.ontario.ca. Resources capped at 10.
    Keywords: ontario, dataset, details, metadata, resources, files, open data, provincial, package, description, organization, tags, ckan, ministry.
    """
    try:
        dataset, cached = await fetch_dataset_details(dataset_id=dataset_id, lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Dataset '{dataset_id}' not found." if exc.response.status_code == 404
            else f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        dataset,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Get resource details
# ---------------------------------------------------------------------------


@tool
async def ontario_get_resource(
    resource_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get details for a specific data resource (file) from the Ontario Open Data Catalogue.

    Use for: retrieving format, size, URL, and description for a known resource UUID from data.ontario.ca datasets. Use after ontario_get_dataset_details to inspect individual files.
    Keywords: ontario, resource, file, download, url, format, csv, excel, xlsx, json, xml, pdf, size, open data, provincial, dataset resource.
    """
    try:
        resource, cached = await fetch_resource(resource_id=resource_id)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Resource '{resource_id}' not found." if exc.response.status_code == 404
            else f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        resource,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: List organizations
# ---------------------------------------------------------------------------


@tool
async def ontario_list_organizations(
    sort: str = "name asc",
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all Ontario government ministries and agencies that publish open data.

    Use for: discovering which Ontario ministries and departments publish datasets, finding organizations by name, or browsing available data publishers on data.ontario.ca.
    Keywords: ontario, ministries, organizations, departments, publishers, provincial, government, agencies, list, browse, open data, catalogue.
    """
    try:
        orgs, cached = await fetch_organizations(sort=sort)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        orgs,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Get portal statistics
# ---------------------------------------------------------------------------


@tool
async def ontario_get_dataset_stats(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get aggregate statistics for the Ontario Open Data Catalogue (data.ontario.ca).

    Use for: finding out how many datasets are available on the Ontario Open Data portal, getting a high-level overview of the data.ontario.ca catalogue size and scope.
    Keywords: ontario, statistics, stats, count, total, datasets, portal, summary, overview, provincial, open data, catalogue, how many.
    """
    try:
        count, cached = await fetch_dataset_count()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    stats = {
        "total_datasets": count,
        "portal": "data.ontario.ca",
        "api_version": "CKAN 3",
    }

    return make_response(
        stats,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Get population projections
# ---------------------------------------------------------------------------


def _filter_population_rows(
    rows: list[dict[str, Any]],
    scenario: str | None = None,
    year: int | None = None,
    gender: str | None = None,
    filter_value: str | None = None,
) -> list[dict[str, Any]]:
    """Filter population projection rows by scenario, year, gender, or label substring."""
    result = rows
    if scenario is not None:
        needle = scenario.upper()
        result = [r for r in result if str(r.get("scenario", "")).upper() == needle]
    if year is not None:
        result = [r for r in result if r.get("year_july_1") == year]
    if gender is not None:
        needle = gender.upper()
        result = [r for r in result if str(r.get("gender", "")).upper() == needle]
    if filter_value is not None:
        needle = filter_value.lower()
        result = [
            r for r in result
            if any(needle in str(v).lower() for v in r.values() if v is not None)
        ]
    return result


@tool
async def ontario_get_population_projections(
    scenario: str | None = None,
    year: int | None = None,
    gender: str | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Fetch Ontario Ministry of Finance population projections by age and gender (2024-2051).

    Data is row-per-observation with scenario (REFERENCE/LOW-GROWTH/HIGH-GROWTH),
    year, gender (MEN+/WOMEN+/TOTAL), and population counts by age group.
    Filter by scenario, year, gender, or free-text search.
    Use for: getting Ontario population forecasts, demographic projections, provincial growth estimates, age distribution, gender breakdown from the Ministry of Finance.
    Keywords: ontario, population, projections, forecast, demographics, growth, ministry of finance, provincial, age, gender, scenario, reference, 2024, 2051, estimates.
    """
    try:
        rows, cached = await fetch_population_projections(lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Ontario Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    filtered = _filter_population_rows(
        rows, scenario=scenario, year=year, gender=gender, filter_value=filter,
    )

    return make_response(
        filtered,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
