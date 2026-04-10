"""BC open data tools — Plan 02 adds 5 discovery tools, Plan 03 adds 15 curated WFS tools.

tools.py is edited by both Plan 02 and Plan 03, so they must be serialized:
Plan 02 first, Plan 03 depends_on Plan 02. FastMCP FileSystemProvider scans for
tools.py (not a tools/ package), so splitting is not an option.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared.ogc import WfsError
from mcp_canada.shared.parsers import fetch_and_parse

from .client import (
    _wfs_fetch,
    fetch_dataset_details,
    fetch_organizations,
    fetch_search_datasets,
    fetch_tags,
)
from .constants import BASE_URL, MAX_RECORDS, WFS_BASE_URL, CACHE_TTL_STATIC


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_cql(filters: dict[str, Any] | None) -> str | None:
    """Translate a simplified filter dict into a CQL_FILTER string.

    Field names are upper-cased (BCGW field names are uppercase per RESEARCH).
    String values are single-quoted with internal single-quotes doubled.
    Numeric (int/float) values are not quoted.
    List values produce a CQL IN clause.

    Args:
        filters: Dict mapping field names to filter values, or None.

    Returns:
        CQL filter string like "FIRE_YEAR=2023 AND REGION='Vancouver Island'",
        or None if filters is empty or None.

    Raises:
        ValueError: If a value type is not str, int, float, or list.
    """
    if not filters:
        return None

    clauses: list[str] = []
    for key, value in filters.items():
        field = key.upper()
        if isinstance(value, bool):
            # bool must come before int since bool is a subclass of int
            clauses.append(f"{field}={str(value).upper()}")
        elif isinstance(value, (int, float)):
            clauses.append(f"{field}={value}")
        elif isinstance(value, str):
            escaped = value.replace("'", "''")
            clauses.append(f"{field}='{escaped}'")
        elif isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, (int, float)):
                    items.append(str(item))
                else:
                    items.append(f"'{str(item).replace(chr(39), chr(39)*2)}'")
            clauses.append(f"{field} IN ({','.join(items)})")
        else:
            raise ValueError(f"Unsupported filter value type for '{key}': {type(value)}")

    return " AND ".join(clauses) if clauses else None


def _pick_file_resource(resources: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the best file resource for non-WFS datasets.

    Prefers formats in order: CSV, XLSX, GEOJSON, JSON, XLS.
    Case-insensitive format matching.

    Args:
        resources: List of resource dicts from fetch_dataset_details.

    Returns:
        The first matching resource dict, or None if no parseable resource found.
    """
    preferred_order = ["csv", "xlsx", "geojson", "json", "xls"]
    for preferred_format in preferred_order:
        for resource in resources:
            fmt = (resource.get("format") or "").lower()
            if fmt == preferred_format:
                return resource
    return None


# ---------------------------------------------------------------------------
# Tool 1: bc_search_datasets
# ---------------------------------------------------------------------------


@tool
async def bc_search_datasets(
    q: str,
    rows: int = 20,
    start: int = 0,
    organization: str | None = None,
    tag: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search BC Data Catalogue for provincial open datasets.

    Use for: Searching BC provincial datasets in the BC Data Catalogue to discover
    available data on any topic — wildfires, forestry, environment, mining, health,
    transportation, climate, water, parks, and more.
    Keywords: british columbia, bc, data catalogue, search, discover, datasets, ckan, province, bcdc, open data, provincial, government, ministry, geographic, environment
    """
    if not q or not q.strip():
        return make_error(
            "INVALID_INPUT",
            "Search query 'q' is required and cannot be empty.",
            lang=lang,
        )

    # Build fq filter from optional organization/tag params
    fq_parts: list[str] = []
    if organization:
        fq_parts.append(f"organization:{organization}")
    if tag:
        fq_parts.append(f"tags:{tag}")
    fq = " AND ".join(fq_parts) if fq_parts else None

    try:
        datasets, cached = await fetch_search_datasets(
            q=q,
            rows=rows,
            start=start,
            fq=fq,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"BC Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        datasets,
        api_name="bc-data-catalogue",
        api_url=BASE_URL + "package_search",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: bc_get_dataset_details
# ---------------------------------------------------------------------------


@tool
async def bc_get_dataset_details(
    package_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full BC dataset details including WFS routing metadata.

    Use for: Getting full BC dataset details including the object_name and
    queryable_via_wfs flag for the two-step WFS workflow — use after
    bc_search_datasets to determine if a dataset can be queried via WFS.
    Keywords: british columbia, bc, dataset, details, resources, object_name, wfs, queryable, routing, metadata, bcdc, package, ckan, geographic, warehouse
    """
    if not package_id or not package_id.strip():
        return make_error(
            "INVALID_INPUT",
            "Parameter 'package_id' is required and cannot be empty.",
            lang=lang,
        )

    try:
        details, cached = await fetch_dataset_details(package_id)
    except httpx.HTTPStatusError as exc:
        code = "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR"
        msg = (
            f"Dataset '{package_id}' not found."
            if exc.response.status_code == 404
            else f"BC Data Catalogue returned HTTP {exc.response.status_code}."
        )
        return make_error(code, msg, lang=lang)

    return make_response(
        details,
        api_name="bc-data-catalogue",
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: bc_query_features
# ---------------------------------------------------------------------------


@tool
async def bc_query_features(
    package_id: str,
    filters: dict[str, Any] | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query features from a BC dataset via WFS or file download.

    Routes to WFS (BC Geographic Warehouse) when queryable_via_wfs=True,
    or parses CSV/XLSX/GeoJSON/JSON file resources otherwise. First call
    bc_get_dataset_details to confirm the dataset is queryable and retrieve
    the object_name used for WFS routing.
    Use for: Querying features from a BC dataset — routes via WFS for geographic
    layers or a file parser for CSV/XLSX/JSON/GeoJSON downloads.
    Keywords: british columbia, bc, features, query, wfs, cql, filter, geographic, dataset, resources, two step, bcgw, warehouse, spatial, data
    """
    if not package_id or not package_id.strip():
        return make_error(
            "INVALID_INPUT",
            "Parameter 'package_id' is required and cannot be empty.",
            lang=lang,
        )

    # Fetch dataset details to determine routing
    try:
        details, _ = await fetch_dataset_details(package_id)
    except httpx.HTTPStatusError as exc:
        code = "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR"
        msg = (
            f"Dataset '{package_id}' not found."
            if exc.response.status_code == 404
            else f"BC Data Catalogue returned HTTP {exc.response.status_code}."
        )
        return make_error(code, msg, lang=lang)

    # Build CQL filter from simplified filter dict
    try:
        cql = _build_cql(filters)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)

    if details.get("queryable_via_wfs"):
        # Route 1: WFS query via BC Geographic Warehouse
        object_name = details["object_name"]
        try:
            wfs_result, was_cached = await _wfs_fetch(
                layer=object_name,
                cql=cql,
                max_records=max_records,
                include_geometry=include_geometry,
            )
        except WfsError as exc:
            return make_error(
                "UPSTREAM_ERROR",
                f"WFS query failed: {exc.message}",
                lang=lang,
                exception_code=exc.code,
            )

        return make_response(
            {
                "features": wfs_result.get("features", []),
                "count": wfs_result.get("count", len(wfs_result.get("features", []))),
                "truncated": wfs_result.get("truncated", False),
            },
            api_name="bc-wfs",
            api_url=WFS_BASE_URL,
            cached=was_cached,
            lang=lang,
        )

    else:
        # Route 2: File download (CSV, XLSX, GeoJSON, JSON)
        resources = details.get("resources") or []
        resource = _pick_file_resource(resources)
        if resource is None:
            return make_error(
                "NOT_FOUND",
                f"No queryable resource found for dataset '{package_id}'. "
                "Dataset is not WFS-queryable and has no CSV/XLSX/GeoJSON/JSON resources.",
                lang=lang,
            )

        try:
            rows, was_cached = await fetch_and_parse(resource["url"], ttl=CACHE_TTL_STATIC)
        except Exception as exc:
            return make_error(
                "UPSTREAM_ERROR",
                f"Failed to parse file resource: {exc}",
                lang=lang,
            )

        return make_response(
            {"features": rows, "truncated": False},
            api_name="bc-data-catalogue-file",
            api_url=resource["url"],
            cached=was_cached,
            lang=lang,
        )


# ---------------------------------------------------------------------------
# Tool 4: bc_list_organizations
# ---------------------------------------------------------------------------


@tool
async def bc_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List BC government ministries and agencies that publish open data.

    Use for: Listing BC government ministries and agencies that publish open data
    on the BC Data Catalogue — use to find the organization slug needed for
    filtering bc_search_datasets by organization.
    Keywords: british columbia, bc, organizations, ministries, agencies, bcdc, ckan, catalogue, publishers, metadata, government, provincial, browse, list
    """
    try:
        orgs, cached = await fetch_organizations()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"BC Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        orgs,
        api_name="bc-data-catalogue",
        api_url=BASE_URL + "organization_list",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: bc_list_categories
# ---------------------------------------------------------------------------


@tool
async def bc_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List BC Data Catalogue tag-based categories for dataset discovery.

    Note: BC does not use CKAN groups (group_list returns HTTP 403). This tool
    surfaces tags instead, which serve as the category taxonomy in the BC Data
    Catalogue. Use tag names as the 'tag' parameter in bc_search_datasets.
    Use for: Listing BC Data Catalogue tag-based categories for dataset discovery —
    BC uses tags instead of groups; use returned tags in bc_search_datasets to filter by topic.
    Keywords: british columbia, bc, categories, tags, taxonomy, subject, bcdc, catalogue, discovery, topics, classification, filter, search, theme
    """
    try:
        tags, cached = await fetch_tags()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"BC Data Catalogue returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    return make_response(
        tags,
        api_name="bc-data-catalogue",
        api_url=BASE_URL + "tag_list",
        cached=cached,
        lang=lang,
    )
