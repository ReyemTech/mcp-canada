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
from .constants import BASE_URL, CATALOG_URL


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
