"""BC open data tools — Plan 02 adds 5 discovery tools, Plan 03 adds 15 curated WFS tools.

tools.py is edited by both Plan 02 and Plan 03, so they must be serialized:
Plan 02 first, Plan 03 depends_on Plan 02. FastMCP FileSystemProvider scans for
tools.py (not a tools/ package), so splitting is not an option.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response, upstream_guard
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
    CLIMATE_STATIONS_LAYER,
    CUT_BLOCKS_LAYER,
    EMERGENCY_ROOMS_LAYER,
    FIRE_PERIMETERS_LAYER,
    FISH_HABITAT_LAYER,
    FOREST_TENURE_LAYER,
    HIGHWAY_PROFILES_LAYER,
    LOCAL_PARKS_LAYER,
    MAX_RECORDS,
    MINING_TENURE_LAYER,
    PROTECTED_AREAS_LAYER,
    ROAD_STRUCTURES_LAYER,
    WALK_IN_CLINICS_LAYER,
    WATER_WELLS_LAYER,
    WEATHER_STATIONS_LAYER,
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
@upstream_guard('bc-data-catalogue')
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
@upstream_guard('bc-data-catalogue')
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
@upstream_guard('bc-data-catalogue')
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
@upstream_guard('bc-data-catalogue')
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
@upstream_guard('bc-wfs')
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
@upstream_guard('bc-wfs')
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
@upstream_guard('bc-wfs')
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
@upstream_guard('bc-wfs')
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
@upstream_guard('bc-wfs')
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


# ---------------------------------------------------------------------------
# Tool 11: bc_get_water_wells
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_water_wells(
    city: str | None = None,
    well_class: str | None = None,
    aquifer_id: int | None = None,
    intended_use: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC groundwater wells from the BCGW WFS (WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW).

    At least one of city, well_class, or aquifer_id is required — the dataset has 130K+ records
    and an unfiltered call would be very slow (RESEARCH Pitfall 5).
    Use for: Locating BC groundwater wells by city, well class, aquifer, or intended water use — use for water resource analysis, environmental review, and aquifer mapping.
    Keywords: british columbia, bc, water wells, groundwater, aquifer, well class, city, drinking water, domestic, irrigation, environmental
    """
    if city is None and well_class is None and aquifer_id is None:
        message = (
            "bc_get_water_wells requires at least one of city, well_class, or aquifer_id "
            "(dataset has 130K+ records — Pitfall 5)."
            if lang == "en"
            else "bc_get_water_wells exige au moins un des paramètres city, well_class ou "
                 "aquifer_id (l'ensemble de données contient plus de 130 000 enregistrements — Pitfall 5)."
        )
        return make_error("INVALID_INPUT", message, lang=lang)
    filters: dict[str, Any] = {}
    if city:
        filters["CITY"] = city
    if well_class:
        filters["WELL_CLASS"] = well_class
    if aquifer_id is not None:
        filters["AQUIFER_ID"] = int(aquifer_id)
    if intended_use:
        filters["INTENDED_WATER_USE"] = intended_use
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=WATER_WELLS_LAYER,
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
# Tool 12: bc_get_wildfire_weather_stations
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_wildfire_weather_stations(
    name: str | None = None,
    min_elevation: int | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC wildfire weather monitoring stations from the BCGW WFS.

    Use for: Finding BC wildfire weather stations by name or elevation — use for fire weather monitoring, FFMC/BUI/FWI calculation inputs, and station coverage analysis.
    Keywords: british columbia, bc, wildfire, weather stations, monitoring, temperature, humidity, rainfall, rh, ffmc, fire weather index, elevation
    """
    cql: str | None = None
    if name:
        cql = _append_like(cql, "STATION_NAME", name)
    if min_elevation is not None:
        cql = _append_gte(cql, "ELEVATION", min_elevation)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=WEATHER_STATIONS_LAYER,
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
# Tool 13: bc_get_local_parks
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_local_parks(
    municipality: str | None = None,
    regional_district: str | None = None,
    park_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC local and regional parks from the BCGW WFS (WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP).

    Use for: Locating BC local and regional parks, greenspaces, and recreational areas by municipality, regional district, or park type — use for urban planning, recreation analysis, and green space mapping.
    Keywords: british columbia, bc, local parks, municipal, regional, greenspace, recreation, municipality, district, parkland, trails, outdoors
    """
    filters: dict[str, Any] = {}
    if municipality:
        filters["MUNICIPALITY"] = municipality
    if regional_district:
        filters["REGIONAL_DISTRICT"] = regional_district
    if park_type:
        filters["PARK_TYPE"] = park_type
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=LOCAL_PARKS_LAYER,
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
# Tool 14: bc_get_mining_tenure
# ---------------------------------------------------------------------------

_TENURE_TYPE_MAP: dict[str, str] = {"mineral": "M", "placer": "P"}


@tool
@upstream_guard('bc-wfs')
async def bc_get_mining_tenure(
    tenure_type: str | None = None,
    owner_name: str | None = None,
    min_area_ha: float | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC mining tenure claims from the BCGW WFS (WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW).

    tenure_type must be 'mineral' or 'placer' if provided; maps to TENURE_TYPE_CODE 'M' or 'P'.
    Use for: Finding BC mining claims by tenure type (mineral/placer), owner name, or minimum area — use for mining rights analysis, resource extraction research, and prospecting zone identification.
    Keywords: british columbia, bc, mining tenure, mineral, placer, claim, owner, area, hectares, prospecting, acquisition, bcgw
    """
    if tenure_type is not None and tenure_type not in _TENURE_TYPE_MAP:
        return make_error(
            "INVALID_INPUT",
            f"tenure_type must be 'mineral' or 'placer', got '{tenure_type}'.",
            lang=lang,
        )
    filters: dict[str, Any] = {}
    if tenure_type:
        filters["TENURE_TYPE_CODE"] = _TENURE_TYPE_MAP[tenure_type]
    cql = _build_cql(filters)
    if owner_name:
        cql = _append_like(cql, "OWNER_NAME", owner_name)
    if min_area_ha is not None:
        cql = _append_gte(cql, "AREA_IN_HECTARES", min_area_ha)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=MINING_TENURE_LAYER,
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
# Tool 15: bc_get_fish_habitat
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_fish_habitat(
    feature_code: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC fish habitat holding areas from the BCGW WFS (WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS).

    Use for: Finding BC coastal and marine fish habitat areas, salmon holding zones, and herring spawn areas — use for fisheries management, marine conservation, and coastal resource analysis.
    Keywords: british columbia, bc, fish habitat, salmon, herring, coastal, holding area, crims, marine, wildlife, fisheries, spawn
    """
    filters: dict[str, Any] = {}
    if feature_code:
        filters["FEATURE_CODE"] = feature_code
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=FISH_HABITAT_LAYER,
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
# Tool 16: bc_get_emergency_rooms
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_emergency_rooms(
    locality: str | None = None,
    wheelchair_accessible: bool | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC hospital emergency rooms from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV).

    Use for: Locating BC emergency rooms by city or accessibility — use for health care access analysis, emergency planning, and patient routing.
    Keywords: british columbia, bc, emergency rooms, hospital, 24 hour, health care, er, accessibility, facility, acute care, locality
    """
    filters: dict[str, Any] = {}
    if locality:
        filters["LOCALITY"] = locality
    if wheelchair_accessible is not None:
        filters["WHEELCHAIR_ACCESSIBLE_IND"] = "Y" if wheelchair_accessible else "N"
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=EMERGENCY_ROOMS_LAYER,
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
# Tool 17: bc_get_walk_in_clinics
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_walk_in_clinics(
    locality: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC walk-in medical clinics from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV).

    Use for: Locating BC walk-in medical clinics by city — use for primary care access analysis, health service mapping, and patient navigation.
    Keywords: british columbia, bc, walk in clinic, medical, primary care, health facility, locality, provider, urgent care, physician
    """
    filters: dict[str, Any] = {}
    if locality:
        filters["LOCALITY"] = locality
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=WALK_IN_CLINICS_LAYER,
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
# Tool 18: bc_get_highway_profiles
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_highway_profiles(
    highway_number: str | None = None,
    admin_unit: str | None = None,
    min_lanes: int | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC highway profile segments from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP).

    Use for: Analyzing BC highway segments by route number, administrative unit, or lane count — use for transportation planning, road capacity analysis, and infrastructure reporting.
    Keywords: british columbia, bc, highway, profile, road, number, lanes, transportation, ministry, mot, segment, admin, route
    """
    filters: dict[str, Any] = {}
    if highway_number:
        filters["HIGHWAY_NUMBER"] = highway_number
    if admin_unit:
        filters["ADMIN_UNIT_NAME"] = admin_unit
    cql = _build_cql(filters)
    if min_lanes is not None:
        cql = _append_gte(cql, "NUMBER_OF_LANES", min_lanes)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=HIGHWAY_PROFILES_LAYER,
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
# Tool 19: bc_get_road_structures
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_road_structures(
    structure_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC road structures from the BCGW WFS (WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP).

    structure_type filters on STRUCTURE_TYPE_CODE (e.g. 'BRIDGE', 'CULVERT', 'TUNNEL').
    Note: Exact field values should be confirmed via a live query; typical values are BRIDGE and CULVERT.
    Use for: Locating BC road infrastructure structures like bridges, culverts, and tunnels — use for transportation asset management, infrastructure analysis, and route planning.
    Keywords: british columbia, bc, road structures, bridges, culverts, tunnels, infrastructure, transportation, ministry, mot, assets, highway
    """
    filters: dict[str, Any] = {}
    if structure_type:
        filters["STRUCTURE_TYPE_CODE"] = structure_type
    cql = _build_cql(filters)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=ROAD_STRUCTURES_LAYER,
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
# Tool 20: bc_get_climate_stations
# ---------------------------------------------------------------------------


@tool
@upstream_guard('bc-wfs')
async def bc_get_climate_stations(
    name: str | None = None,
    min_elevation: int | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Query BC climate observation stations from the BCGW WFS.

    This exposes the same BCGW layer as bc_get_wildfire_weather_stations
    (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP) from a climate-analysis
    perspective. For long-term climate normals use Environment Canada (ECCC) data via
    the weather module.
    Use for: Discovering BC climate observation stations for historical and current climate data — use for climate trend analysis, precipitation studies, and long-term temperature records.
    Keywords: british columbia, bc, climate, weather stations, temperature, precipitation, eccc, historical, normal, observation, elevation, environment canada
    """
    cql: str | None = None
    if name:
        cql = _append_like(cql, "STATION_NAME", name)
    if min_elevation is not None:
        cql = _append_gte(cql, "ELEVATION", min_elevation)
    try:
        (features, truncated), was_cached = await _wfs_fetch(
            layer=CLIMATE_STATIONS_LAYER,
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
