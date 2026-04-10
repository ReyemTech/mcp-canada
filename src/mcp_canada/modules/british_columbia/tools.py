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
from .constants import (
    ACTIVE_FIRES_LAYER,
    BASE_URL,
    CACHE_TTL_STATIC,
    CUT_BLOCKS_LAYER,
    FIRE_PERIMETERS_LAYER,
    FOREST_TENURE_LAYER,
    MAX_RECORDS,
    PROTECTED_AREAS_LAYER,
    WFS_BASE_URL,
)


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
            (features, truncated), was_cached = await _wfs_fetch(
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
                "features": features,
                "count": len(features),
                "truncated": truncated,
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


# ---------------------------------------------------------------------------
# Plan 03 helpers
# ---------------------------------------------------------------------------


def _append_gte(cql: str | None, field: str, value: float | int) -> str:
    """Append a >= clause to an existing CQL string, or create it if cql is None."""
    clause = f"{field} >= {value}"
    return f"{cql} AND {clause}" if cql else clause


def _append_like(cql: str | None, field: str, value: str) -> str:
    """Append a LIKE clause (value%) to an existing CQL string."""
    escaped = value.replace("'", "''")
    clause = f"{field} LIKE '{escaped}%'"
    return f"{cql} AND {clause}" if cql else clause


# ---------------------------------------------------------------------------
# Tool 6: bc_get_active_fires
# ---------------------------------------------------------------------------


@tool
async def bc_get_active_fires(
    status: str | None = None,
    centre: str | None = None,
    min_size_hectares: float | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query currently active wildfires in British Columbia from the BCGW WFS.

    Use for: Checking real-time BC wildfire incidents by status, fire centre, or minimum size — use for emergency awareness, fire season monitoring, and geographic analysis of active wildfire hotspots.
    Keywords: british columbia, bc, wildfire, active fire, incident, status, fire centre, emergency, province, size, current, real-time
    """
    filters: dict[str, Any] = {}
    if status:
        filters["FIRE_STATUS"] = status
    if centre:
        filters["FIRE_CENTRE"] = centre
    cql = _build_cql(filters)
    if min_size_hectares is not None:
        cql = _append_gte(cql, "CURRENT_SIZE", min_size_hectares)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=ACTIVE_FIRES_LAYER,
            cql=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except WfsError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"WFS error: {exc.message}",
            lang=lang,
            exception_code=exc.code,
        )
    return make_response(
        {"features": features, "truncated": truncated},
        api_name="bc-wfs",
        api_url=WFS_BASE_URL,
        cached=was_cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: bc_get_fire_perimeters
# ---------------------------------------------------------------------------


@tool
async def bc_get_fire_perimeters(
    year: int | None = None,
    cause: str | None = None,
    min_size_hectares: float | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query historical BC wildfire perimeters from the BCGW WFS.

    Year is required to bound the query (676+ fires per year in historical dataset).
    Use for: Analyzing historical BC wildfire burn areas by year, cause, or minimum size — use for post-fire analysis, land use planning, and historical fire pattern research.
    Keywords: british columbia, bc, wildfire, fire perimeters, historical, burn area, year, cause, hectares, polygon, boundary, forest
    """
    if year is None:
        return make_error(
            "INVALID_INPUT",
            "Parameter 'year' is required for bc_get_fire_perimeters (dataset has 676+ fires/year).",
            lang=lang,
        )
    filters: dict[str, Any] = {"FIRE_YEAR": int(year)}
    if cause:
        filters["FIRE_CAUSE"] = cause
    cql = _build_cql(filters)
    if min_size_hectares is not None:
        cql = _append_gte(cql, "FIRE_SIZE_HECTARES", min_size_hectares)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=FIRE_PERIMETERS_LAYER,
            cql=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except WfsError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"WFS error: {exc.message}",
            lang=lang,
            exception_code=exc.code,
        )
    return make_response(
        {"features": features, "truncated": truncated},
        api_name="bc-wfs",
        api_url=WFS_BASE_URL,
        cached=was_cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: bc_get_forest_tenure
# ---------------------------------------------------------------------------


@tool
async def bc_get_forest_tenure(
    status: str | None = "ACTIVE",
    tenure_type: str | None = None,
    client_name: str | None = None,
    district: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC forest tenure licences from the BCGW WFS.

    Use for: Finding BC forest tenure licence holders, active managed licences by district or client name — use for forestry compliance, resource extraction analysis, and tenure mapping.
    Keywords: british columbia, bc, forest tenure, licence, managed, client, district, forestry, cutting rights, bcgw, silviculture, tenure holder
    """
    filters: dict[str, Any] = {}
    if status:
        filters["LIFE_CYCLE_STATUS_CODE"] = status
    if tenure_type:
        filters["ML_TYPE_CODE"] = tenure_type
    if district:
        filters["ADMIN_DISTRICT_NAME"] = district
    cql = _build_cql(filters)
    if client_name:
        cql = _append_like(cql, "CLIENT_NAME", client_name)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=FOREST_TENURE_LAYER,
            cql=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except WfsError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"WFS error: {exc.message}",
            lang=lang,
            exception_code=exc.code,
        )
    return make_response(
        {"features": features, "truncated": truncated},
        api_name="bc-wfs",
        api_url=WFS_BASE_URL,
        cached=was_cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 9: bc_get_cut_blocks
# ---------------------------------------------------------------------------


@tool
async def bc_get_cut_blocks(
    status: str | None = "ACTIVE",
    district: str | None = None,
    client_name: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC forest cut block polygons from the BCGW WFS (FTEN_CUT_BLOCK_POLY_SVW).

    Use for: Analyzing BC forest harvesting cut blocks by status, district, or licence holder — use for timber supply analysis, post-harvest monitoring, and forest regeneration tracking.
    Keywords: british columbia, bc, cut blocks, harvest, forestry, logging, ften, polygon, district, status, timber, silviculture
    """
    filters: dict[str, Any] = {}
    if status:
        filters["LIFE_CYCLE_STATUS_CODE"] = status
    if district:
        filters["ADMIN_DISTRICT_NAME"] = district
    if client_name:
        filters["CLIENT_NAME"] = client_name
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=CUT_BLOCKS_LAYER,
            cql=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except WfsError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"WFS error: {exc.message}",
            lang=lang,
            exception_code=exc.code,
        )
    return make_response(
        {"features": features, "truncated": truncated},
        api_name="bc-wfs",
        api_url=WFS_BASE_URL,
        cached=was_cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 10: bc_get_protected_areas
# ---------------------------------------------------------------------------


@tool
async def bc_get_protected_areas(
    designation: str | None = None,
    min_area_ha: float | None = None,
    name: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC protected lands from the BCGW WFS (WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW).

    Use for: Discovering BC provincial parks, ecological reserves, and protected areas by designation, size, or name — use for conservation analysis, land use planning, and park boundary queries.
    Keywords: british columbia, bc, protected areas, provincial parks, ecological reserve, conservation, designation, hectares, tantalis, parkland, boundaries, wildlife
    """
    filters: dict[str, Any] = {}
    if designation:
        filters["PROTECTED_LANDS_DESIGNATION"] = designation
    cql = _build_cql(filters)
    if name:
        cql = _append_like(cql, "PROTECTED_LANDS_NAME", name)
    if min_area_ha is not None:
        cql = _append_gte(cql, "OFFICIAL_AREA_HA", min_area_ha)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=PROTECTED_AREAS_LAYER,
            cql=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except WfsError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"WFS error: {exc.message}",
            lang=lang,
            exception_code=exc.code,
        )
    return make_response(
        {"features": features, "truncated": truncated},
        api_name="bc-wfs",
        api_url=WFS_BASE_URL,
        cached=was_cached,
        lang=lang,
    )
