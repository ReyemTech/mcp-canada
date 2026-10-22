"""Calgary module tools — @tool functions for the MCP server.

All tools use standalone @tool from fastmcp.tools (NEVER @mcp.tool).
All tools include lang: Literal["en", "fr"] = "en" parameter.
All tools return make_response() on success, make_error() on failure.
All tools use the "calgary_" prefix.

Discovery tools (this module's entire scope):
  calgary_search_datasets, calgary_get_dataset_details, calgary_query_dataset,
  calgary_list_organizations, calgary_list_categories
"""

from __future__ import annotations

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client
from .constants import BASE_URL, CATALOG_URL


@tool
async def calgary_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search the City of Calgary open data catalogue on data.calgary.ca (Socrata).

    Use for: searching Calgary's open data portal; discovering datasets by keyword; browsing the Calgary Socrata catalogue; finding municipal government data; paginating through dataset results.
    Keywords: calgary open data catalogue search datasets socrata soda portal browse discover inventory find municipal government data alberta city
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
            api_name="calgary-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def calgary_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get schema and metadata for a specific Calgary dataset by its 4x4 dataset ID.

    Use for: inspecting a Calgary dataset schema; finding column names and types; getting attribution, license, and publication date for a specific dataset.
    Keywords: calgary dataset details schema columns metadata views attribution license socrata dataset info fields inspect alberta city
    """
    try:
        data, cached = await _client.fetch_dataset_details(dataset_id=dataset_id)
        return make_response(
            data,
            api_name="calgary-socrata",
            api_url=f"{BASE_URL}/api/views/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def calgary_query_dataset(
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
    """Run a SoQL query against any Calgary Socrata dataset via /resource/{id}.json.

    Use for: querying any Calgary dataset with filters; running SoQL against Calgary open data; getting specific rows from a municipal dataset; aggregating Calgary data by field.
    Keywords: calgary query dataset soql where select order limit offset filter socrata resource sql data rows fetch alberta city

    Note: geometry (the_geom) is returned in rows when include_geometry=True or when
    $select is not specified. Use $select to exclude the_geom when not needed.
    Example: dataset_id='35ra-9556', select="incident_description,start_dt,description", limit=100
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
            api_name="calgary-socrata",
            api_url=f"{BASE_URL}/resource/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def calgary_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List City of Calgary departments and publishers on data.calgary.ca.

    Use for: discovering which Calgary departments publish open data; finding organization names for Calgary's Socrata portal; browsing data publishers by dataset count.
    Keywords: calgary organizations publishers departments attributions municipal agencies data owners socrata portal list browse alberta city
    """
    try:
        data, cached = await _client.fetch_organizations()
        return make_response(
            data,
            api_name="calgary-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def calgary_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Calgary data categories from the data.calgary.ca Socrata catalogue.

    Use for: discovering all topic categories in Calgary's open data portal; finding categories like Transportation/Transit, Environment, Business and Economic Activity; browsing Calgary dataset subjects.
    Keywords: calgary categories topics domains classification transportation environment business government socrata catalogue browse subjects alberta city

    Note: aggregates classification.domain_category client-side from a wide catalog
    page rather than relying on the categories= API parameter, which is unverified
    on this portal and confirmed broken on the sibling Nova Scotia Socrata portal.
    """
    try:
        data, cached = await _client.fetch_categories()
        return make_response(
            data,
            api_name="calgary-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
