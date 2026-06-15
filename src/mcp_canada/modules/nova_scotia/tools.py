"""Nova Scotia module tools — @tool functions for the MCP server.

All tools use standalone @tool from fastmcp.tools (NEVER @mcp.tool).
All tools include lang: Literal["en", "fr"] = "en" parameter.
All tools return make_response() on success, make_error() on failure.
All tools use the "ns_" prefix.

Discovery tools (Plan 02):
  ns_search_datasets, ns_get_dataset_details, ns_query_dataset,
  ns_list_organizations, ns_list_categories

Curated tools added by Plans 03-05.
"""

from __future__ import annotations

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared import socrata  # noqa: F401 — used by discovery tools

from . import client as _client
from .constants import (
    BASE_URL,
    CATALOG_URL,
    DS_MARINE_AQUACULTURE_LEASES,
    DS_LANDBASED_AQUACULTURE_LICENSES,
    DS_FISH_HATCHERY_STOCKING,
    DS_AQUACULTURE_PRODUCTION,
)


# ---------------------------------------------------------------------------
# Discovery tools (Plan 02)
# ---------------------------------------------------------------------------


@tool
async def ns_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search the Government of Nova Scotia open data catalogue on data.novascotia.ca (Socrata).

    Use for: searching Nova Scotia's open data portal; discovering datasets by keyword; browsing the NS Socrata catalogue; finding provincial government data; paginating through dataset results.
    Keywords: nova scotia open data catalogue search datasets socrata soda portal browse discover inventory find provincial government data novascotia
    """
    try:
        data, cached = await _client.fetch_search_datasets(query=query, limit=limit, offset=offset)
        return make_response(
            {
                "results": data.get("results", []),
                "total": data.get("total", 0),
                "offset": offset,
                "limit": limit,
            },
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get schema and metadata for a specific Nova Scotia dataset by its 4x4 dataset ID.

    Use for: inspecting a Nova Scotia dataset schema; finding column names and types; getting attribution, license, and publication date for a specific dataset.
    Keywords: nova scotia dataset details schema columns metadata views attribution license socrata dataset info fields inspect
    """
    try:
        data, cached = await _client.fetch_dataset_details(dataset_id=dataset_id)
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/api/views/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_query_dataset(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 1000,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Run a SoQL query against any Nova Scotia Socrata dataset via /resource/{id}.json.

    Use for: querying any NS dataset with filters; running SoQL against Nova Scotia open data; getting specific rows from a provincial dataset; aggregating NS data by field.
    Keywords: nova scotia query dataset soql where select order limit offset filter socrata resource sql data rows fetch

    Note: geometry (the_geom) is returned in rows when include_geometry=True or when
    $select is not specified. Use $select to exclude the_geom when not needed.
    Example: dataset_id='h57h-p9mm', where="county='Halifax'", select="county,species,ownership", limit=100
    """
    try:
        data, cached = await _client.fetch_query_dataset(
            dataset_id=dataset_id,
            where=where,
            select=select,
            order=order,
            limit=limit,
            offset=offset,
            q=q,
            group=group,
            include_geometry=include_geometry,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Nova Scotia government organizations and publishers on data.novascotia.ca.

    Use for: discovering which NS departments publish open data; finding organization names for Nova Scotia's Socrata portal; browsing data publishers by dataset count.
    Keywords: nova scotia organizations publishers departments attributions government agencies data owners socrata portal list browse
    """
    try:
        data, cached = await _client.fetch_organizations()
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Nova Scotia data categories from the data.novascotia.ca Socrata catalogue.

    Use for: discovering all topic categories in Nova Scotia's open data portal; finding categories like Fishing and Aquaculture, Health and Wellness, Environment and Energy; browsing NS dataset subjects.
    Keywords: nova scotia categories topics domains classification fisheries health environment energy agriculture government socrata catalogue browse subjects

    Note: The catalog categories= API parameter is broken (returns 0 results always).
    This tool uses q= full-text search + client-side aggregation of
    classification.domain_category — never the broken categories= parameter.
    """
    try:
        data, cached = await _client.fetch_categories()
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Fishing / Aquaculture curated tools (Plan 03)
# ---------------------------------------------------------------------------


@tool
async def ns_get_marine_aquaculture_leases(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia marine aquaculture lease locations with species, owner, waterbody, county, status, and area.

    Use for: finding NS marine aquaculture leases by county or species type; discovering shellfish or finfish lease locations; marine aquaculture licensing queries in Nova Scotia.
    Keywords: nova scotia marine aquaculture lease shellfish finfish oyster salmon waterbody county status ownership hectares coordinates fishing aquaculture NS

    Note: geometry (the_geom MultiPolygon boundaries) is excluded from this tool's response.
    To retrieve polygon boundaries, use ns_query_dataset with dataset_id='h57h-p9mm' and
    include $select=...,the_geom explicitly. County names use title case (e.g., 'Inverness').
    Species type values: 'Shellfish', 'Finfish', 'Marine Plant'.
    """
    try:
        data, cached = await _client.fetch_marine_aquaculture_leases(
            county=county,
            species_type=species_type,
            limit=limit,
        )
        # Belt-and-suspenders: strip the_geom from any row that still has it
        leases = [{k: v for k, v in row.items() if k != "the_geom"} for row in data.get("leases", [])]
        return make_response(
            {**data, "leases": leases},
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_MARINE_AQUACULTURE_LEASES}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_landbased_aquaculture_licenses(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia landbased aquaculture licenses with species type, owner, county, and operational status.

    Use for: finding NS landbased aquaculture operations by county or species type; Atlantic Salmon or Rainbow Trout license queries; finfish farm locations; aquaculture licensing in Nova Scotia.
    Keywords: nova scotia landbased aquaculture license finfish salmon rainbow trout county ownership status lat long coordinates farm facility NS aquaculture

    Note: County names use title case (e.g., 'Hants', 'Colchester').
    Species type values: 'Finfish', 'Shellfish'. Finfish (Atlantic Salmon) dominates this dataset.
    """
    try:
        data, cached = await _client.fetch_landbased_aquaculture_licenses(
            county=county,
            species_type=species_type,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_LANDBASED_AQUACULTURE_LICENSES}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_fish_hatchery_stocking(
    stock: str | None = None,
    county: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia fish hatchery stocking records with species, hatchery, county, fish size, count released, and stocking date.

    Use for: querying NS hatchery stocking records by species or county; finding Brook Trout or Atlantic Salmon releases; hatchery production data; stocking history by waterbody in Nova Scotia.
    Keywords: nova scotia fish hatchery stocking brook trout atlantic salmon releases county hatchery fingerling smolt number released stocking date NS fisheries aquaculture

    Note: Records are ordered newest-first (stocking_date DESC). Data current to 2025-11.
    Brook Trout is the dominant stocked species. County names use title case (e.g., 'Antigonish').
    Common stock values: 'Brook Trout', 'Atlantic Salmon', 'Brown Trout', 'Rainbow Trout'.
    """
    try:
        data, cached = await _client.fetch_fish_hatchery_stocking(
            stock=stock,
            county=county,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_FISH_HATCHERY_STOCKING}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_aquaculture_production(
    year: str | None = None,
    county: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia aquaculture production, value, and employment data by county and year.

    Use for: querying NS aquaculture economic data by county and year; production volume (kg) and total value by region; employment statistics for NS aquaculture sector; annual industry analysis.
    Keywords: nova scotia aquaculture production value employment county year kg kgs full time jobs economic annual industry data NS fisheries shellfish finfish

    Note: year is stored as a text field — use the year as a string (e.g., year='2022').
    Annual data by county. Fields: year, county, kgs, total_value, full_time, pt_employ_6_mth,
    pt_employ_6_mth_1, total_employ. Results ordered most recent year first.
    """
    try:
        data, cached = await _client.fetch_aquaculture_production(
            year=year,
            county=county,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_AQUACULTURE_PRODUCTION}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
