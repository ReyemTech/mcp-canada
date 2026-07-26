"""CKAN Open Data @tool functions.

Provides 7 intent-based MCP tools for querying Canada's Open Data portal
(open.canada.ca) with 80,000+ government datasets. Descriptions are
truncated to ~500 chars and resources capped at 10 per dataset to save
agent tokens.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.ckan.client import (
    fetch_dataset_count,
    fetch_dataset_details,
    fetch_groups,
    fetch_organizations,
    fetch_resource,
    fetch_search_datasets,
)
from mcp_canada.modules.ckan.constants import BASE_URL
from mcp_canada.shared.envelope import make_error, make_response, upstream_guard

# API name and base URL for _meta envelope
_API_NAME = "CKAN Open Data"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Search datasets
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_search_datasets(
    query: str,
    filters: str | None = None,
    rows: int = 10,
    start: int = 0,
    sort: str = "relevance asc",
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Canada's Open Data portal (open.canada.ca) for datasets by keyword.

    Use for: finding Canadian government datasets on any topic — environment,
    health, economy, transportation, science, social programs, and more.
    Descriptions are truncated to ~500 chars to save tokens.
    Keywords: search, dataset, open data, canada, government, federal, portal,
    find, discover, keyword, topic, catalogue, ckan, datasets.
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
            f"CKAN Open Data returned HTTP {exc.response.status_code}.",
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
@upstream_guard(_API_NAME)
async def ckan_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full details for a specific Canadian Open Data dataset including all resources.

    Use for: retrieving complete metadata, resources list, and description for a
    known dataset ID or slug from open.canada.ca. Resources capped at 10.
    Keywords: dataset, details, metadata, resources, files, open data, canada,
    package, description, organization, tags, ckan.
    """
    try:
        dataset, cached = await fetch_dataset_details(dataset_id=dataset_id, lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Dataset '{dataset_id}' not found." if exc.response.status_code == 404
            else f"CKAN Open Data returned HTTP {exc.response.status_code}.",
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
# Tool 3: List organizations
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_list_organizations(
    sort: str = "name asc",
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all Canadian federal government organizations on the Open Data portal.

    Use for: discovering which government departments and agencies publish open data,
    finding organizations by name, or browsing available data publishers on open.canada.ca.
    Keywords: organizations, departments, agencies, government, publishers, federal,
    canada, ministry, list, browse, ckan, open data.
    """
    try:
        orgs, cached = await fetch_organizations(sort=sort)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"CKAN Open Data returned HTTP {exc.response.status_code}.",
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
# Tool 4: Search by tag
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_search_by_tag(
    tag: str,
    rows: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Canadian Open Data portal datasets by tag or keyword label.

    Use for: finding all datasets with a specific topic tag such as 'climate',
    'health', 'agriculture', 'water', 'energy', or any other tag on open.canada.ca.
    Keywords: tag, label, topic, category, theme, search, datasets, open data,
    canada, filter, ckan, tagged, subject.
    """
    try:
        datasets, cached = await fetch_search_datasets(
            query="*:*",
            fq=f"tags:{tag}",
            rows=rows,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"CKAN Open Data returned HTTP {exc.response.status_code}.",
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
# Tool 5: Get resource details
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_get_resource(
    resource_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get details for a specific data resource (file) from Canada's Open Data portal.

    Use for: retrieving format, size, URL, and description for a known resource
    UUID from open.canada.ca datasets. Use after getting dataset details to inspect
    individual files.
    Keywords: resource, file, download, url, format, csv, excel, json, xml, pdf,
    size, open data, canada, ckan, dataset resource.
    """
    try:
        resource, cached = await fetch_resource(resource_id=resource_id)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Resource '{resource_id}' not found." if exc.response.status_code == 404
            else f"CKAN Open Data returned HTTP {exc.response.status_code}.",
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
# Tool 6: List groups
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_list_groups(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List thematic dataset groups available on Canada's Open Data portal.

    Use for: browsing thematic collections of datasets organized by subject area
    such as environment, health, economy, transportation, and science on open.canada.ca.
    Keywords: groups, themes, categories, subjects, collections, thematic, browse,
    open data, canada, ckan, list, dataset groups.
    """
    try:
        groups, cached = await fetch_groups()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"CKAN Open Data returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        groups,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Get portal statistics
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def ckan_get_dataset_stats(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get aggregate statistics for Canada's Open Data portal (open.canada.ca).

    Use for: finding out how many datasets are available on the portal, getting
    a high-level overview of the open.canada.ca data catalogue size and scope.
    Keywords: statistics, stats, count, total, datasets, portal, summary, overview,
    canada, open data, ckan, catalogue, how many.
    """
    try:
        count, cached = await fetch_dataset_count()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"CKAN Open Data returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    stats = {
        "total_datasets": count,
        "portal": "open.canada.ca",
        "api_version": "CKAN 3",
    }

    return make_response(
        stats,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
