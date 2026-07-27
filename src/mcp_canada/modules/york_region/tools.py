"""York Region and local municipal ArcGIS Hub tools.

Exposes 5 discovery tools × 4 verified portals (york_region, markham,
newmarket, aurora) + 5 curated York Region tools + 2 curated Markham tools.
Follows the standalone @tool pattern required by FileSystemProvider.
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.york_region.client import (
    NoPortalError,
    fetch_beach_water_testing,
    fetch_census_age_sex,
    fetch_census_income,
    fetch_drinking_water_incidents,
    fetch_get_dataset_details,
    fetch_list_categories,
    fetch_list_organizations,
    fetch_markham_addresses,
    fetch_markham_roads,
    fetch_query_features,
    fetch_regional_roads,
    fetch_search_datasets,
    fetch_solid_waste_sites,
    fetch_transit_routes,
    fetch_transit_stops,
    fetch_waste_diversion,
    fetch_hospitals,
)
from mcp_canada.modules.york_region.constants import PORTAL_URLS
from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared.errors import InvalidInput, NotFound, UpstreamData

API_NAME = "arcgis-hub"


# ---------------------------------------------------------------------------
# Private helper — centralises error handling for all tools
# ---------------------------------------------------------------------------


async def _call_client(
    coro,
    *,
    api_url: str,
    lang: str,
) -> dict[str, Any]:
    """Run a client coroutine and wrap result with make_response / make_error.

    Centralises the classified markers, NoPortalError -> NOT_FOUND,
    HTTP 404 -> NOT_FOUND, other HTTPStatusError -> UPSTREAM_ERROR,
    generic Exception -> UPSTREAM_ERROR.

    The marker arms must come first. These tools carry no ``@upstream_guard``
    (this helper is their catch-all), so without them an unknown dataset id
    raised as ``NotFound`` fell into the generic arm below and a routine
    missing record was reported as an upstream outage.
    """
    try:
        data, cached = await coro
        return make_response(
            data,
            api_name=API_NAME,
            api_url=api_url,
            cached=cached,
            lang=lang,
        )
    except InvalidInput as e:
        return make_error("INVALID_INPUT", str(e), lang=lang)
    except NotFound as e:
        return make_error("NOT_FOUND", str(e), lang=lang)
    except UpstreamData as e:
        return make_error("UPSTREAM_ERROR", f"upstream returned unusable data: {e}", lang=lang)
    except NoPortalError as e:
        return make_error("NOT_FOUND", str(e), lang=lang)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"Resource not found: {e.request.url}",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            lang=lang,
        )
    except Exception as e:  # noqa: BLE001 — tools must never raise
        return make_error("UPSTREAM_ERROR", str(e), lang=lang)


# ---------------------------------------------------------------------------
# Discovery tools — york_region (5)
# ---------------------------------------------------------------------------


@tool
async def york_region_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search York Region's ArcGIS Hub open data catalogue (insights-york.opendata.arcgis.com, ~442 datasets).

    Use for: discovering York Region regional datasets by keyword (transit, roads, demographics, health, waste).
    Keywords: york region, arcgis hub, open data, catalogue, search, datasets, regional, municipal, ontario, gta, transit, roads, discover
    """  # noqa: E501
    limit = max(1, min(limit, 100))
    return await _call_client(
        fetch_search_datasets("york_region", query, limit, offset, lang),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get details for a specific dataset on York Region's ArcGIS Hub portal.

    Use for: retrieving full metadata (URL, description, owner, tags) for a known York Region dataset ID.
    Keywords: york region, arcgis hub, dataset, details, metadata, open data, regional, ontario, gta, feature service
    """  # noqa: E501
    return await _call_client(
        fetch_get_dataset_details("york_region", dataset_id, lang),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_query_features(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a York Region ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

    Use for: querying any York Region FeatureServer layer with a custom SQL WHERE clause.
    Keywords: york region, arcgis, feature service, featureserver, query, where clause, layer, spatial, ontario, gta, filter, features
    """  # noqa: E501
    max_records = min(max_records, 5000)
    return await _call_client(
        fetch_query_features("york_region", service_url, layer_id, where, out_fields, include_geometry, max_records),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset owner organizations on York Region's ArcGIS Hub portal.

    Use for: discovering which organizations publish datasets on the York Region open data portal.
    Keywords: york region, arcgis hub, organizations, owners, publishers, open data, regional, ontario, gta, catalogue
    """  # noqa: E501
    return await _call_client(
        fetch_list_organizations("york_region", lang),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset categories on York Region's ArcGIS Hub portal.

    Use for: discovering available data categories on the York Region open data portal.
    Keywords: york region, arcgis hub, categories, themes, topics, open data, regional, ontario, gta, browse
    """  # noqa: E501
    return await _call_client(
        fetch_list_categories("york_region", lang),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Discovery tools — markham (5)
# ---------------------------------------------------------------------------


@tool
async def markham_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search City of Markham's ArcGIS Hub open data catalogue (data-markham.opendata.arcgis.com).

    Use for: discovering Markham municipal datasets by keyword (addresses, roads, planning, zoning).
    Keywords: markham, city of markham, arcgis hub, open data, gta, ontario, municipal, addresses, planning, zoning, search, discover
    """  # noqa: E501
    limit = max(1, min(limit, 100))
    return await _call_client(
        fetch_search_datasets("markham", query, limit, offset, lang),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


@tool
async def markham_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get details for a specific dataset on Markham's ArcGIS Hub portal.

    Use for: retrieving full metadata for a known Markham dataset ID or title.
    Keywords: markham, city of markham, arcgis hub, dataset, details, metadata, open data, gta, ontario, feature service
    """  # noqa: E501
    return await _call_client(
        fetch_get_dataset_details("markham", dataset_id, lang),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


@tool
async def markham_query_features(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a Markham ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

    Use for: querying any Markham FeatureServer layer with a custom SQL WHERE clause.
    Keywords: markham, arcgis, feature service, featureserver, query, where clause, layer, spatial, gta, ontario, filter, features
    """  # noqa: E501
    max_records = min(max_records, 5000)
    return await _call_client(
        fetch_query_features("markham", service_url, layer_id, where, out_fields, include_geometry, max_records),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


@tool
async def markham_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset owner organizations on Markham's ArcGIS Hub portal.

    Use for: discovering which organizations publish datasets on the Markham open data portal.
    Keywords: markham, city of markham, arcgis hub, organizations, owners, publishers, open data, gta, ontario, catalogue
    """  # noqa: E501
    return await _call_client(
        fetch_list_organizations("markham", lang),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


@tool
async def markham_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset categories on Markham's ArcGIS Hub portal.

    Use for: discovering available data categories on the Markham open data portal.
    Keywords: markham, city of markham, arcgis hub, categories, themes, topics, open data, gta, ontario, browse
    """  # noqa: E501
    return await _call_client(
        fetch_list_categories("markham", lang),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Discovery tools — newmarket (5)
# ---------------------------------------------------------------------------


@tool
async def newmarket_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Town of Newmarket's ArcGIS Hub open data catalogue (navigate-newmarket.hub.arcgis.com).

    Use for: discovering Newmarket municipal datasets by keyword.
    Keywords: newmarket, town of newmarket, arcgis hub, open data, gta, ontario, municipal, geographic, discovery, catalogue, search
    """  # noqa: E501
    limit = max(1, min(limit, 100))
    return await _call_client(
        fetch_search_datasets("newmarket", query, limit, offset, lang),
        api_url=PORTAL_URLS["newmarket"] or "",
        lang=lang,
    )


@tool
async def newmarket_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get details for a specific dataset on Newmarket's ArcGIS Hub portal.

    Use for: retrieving full metadata for a known Newmarket dataset ID or title.
    Keywords: newmarket, town of newmarket, arcgis hub, dataset, details, metadata, open data, gta, ontario, feature service
    """  # noqa: E501
    return await _call_client(
        fetch_get_dataset_details("newmarket", dataset_id, lang),
        api_url=PORTAL_URLS["newmarket"] or "",
        lang=lang,
    )


@tool
async def newmarket_query_features(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a Newmarket ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

    Use for: querying any Newmarket FeatureServer layer with a custom SQL WHERE clause.
    Keywords: newmarket, arcgis, feature service, featureserver, query, where clause, layer, spatial, gta, ontario, filter, features
    """  # noqa: E501
    max_records = min(max_records, 5000)
    return await _call_client(
        fetch_query_features("newmarket", service_url, layer_id, where, out_fields, include_geometry, max_records),
        api_url=PORTAL_URLS["newmarket"] or "",
        lang=lang,
    )


@tool
async def newmarket_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset owner organizations on Newmarket's ArcGIS Hub portal.

    Use for: discovering which organizations publish datasets on the Newmarket open data portal.
    Keywords: newmarket, town of newmarket, arcgis hub, organizations, owners, publishers, open data, gta, ontario, catalogue
    """  # noqa: E501
    return await _call_client(
        fetch_list_organizations("newmarket", lang),
        api_url=PORTAL_URLS["newmarket"] or "",
        lang=lang,
    )


@tool
async def newmarket_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset categories on Newmarket's ArcGIS Hub portal.

    Use for: discovering available data categories on the Newmarket open data portal.
    Keywords: newmarket, town of newmarket, arcgis hub, categories, themes, topics, open data, gta, ontario, browse
    """  # noqa: E501
    return await _call_client(
        fetch_list_categories("newmarket", lang),
        api_url=PORTAL_URLS["newmarket"] or "",
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Discovery tools — aurora (5)
# ---------------------------------------------------------------------------


@tool
async def aurora_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Town of Aurora's ArcGIS Hub open data catalogue (town-of-aurora-data-hub-aurora.hub.arcgis.com).

    Use for: discovering Aurora municipal datasets by keyword.
    Keywords: aurora, town of aurora, arcgis hub, open data, gta, ontario, municipal, local government, catalogue, search, discover
    """  # noqa: E501
    limit = max(1, min(limit, 100))
    return await _call_client(
        fetch_search_datasets("aurora", query, limit, offset, lang),
        api_url=PORTAL_URLS["aurora"] or "",
        lang=lang,
    )


@tool
async def aurora_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get details for a specific dataset on Aurora's ArcGIS Hub portal.

    Use for: retrieving full metadata for a known Aurora dataset ID or title.
    Keywords: aurora, town of aurora, arcgis hub, dataset, details, metadata, open data, gta, ontario, feature service
    """  # noqa: E501
    return await _call_client(
        fetch_get_dataset_details("aurora", dataset_id, lang),
        api_url=PORTAL_URLS["aurora"] or "",
        lang=lang,
    )


@tool
async def aurora_query_features(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query an Aurora ArcGIS FeatureServer layer with a WHERE clause. max_records is capped at 5000 per call.

    Use for: querying any Aurora FeatureServer layer with a custom SQL WHERE clause.
    Keywords: aurora, arcgis, feature service, featureserver, query, where clause, layer, spatial, gta, ontario, filter, features
    """  # noqa: E501
    max_records = min(max_records, 5000)
    return await _call_client(
        fetch_query_features("aurora", service_url, layer_id, where, out_fields, include_geometry, max_records),
        api_url=PORTAL_URLS["aurora"] or "",
        lang=lang,
    )


@tool
async def aurora_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset owner organizations on Aurora's ArcGIS Hub portal.

    Use for: discovering which organizations publish datasets on the Aurora open data portal.
    Keywords: aurora, town of aurora, arcgis hub, organizations, owners, publishers, open data, gta, ontario, catalogue
    """  # noqa: E501
    return await _call_client(
        fetch_list_organizations("aurora", lang),
        api_url=PORTAL_URLS["aurora"] or "",
        lang=lang,
    )


@tool
async def aurora_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all dataset categories on Aurora's ArcGIS Hub portal.

    Use for: discovering available data categories on the Aurora open data portal.
    Keywords: aurora, town of aurora, arcgis hub, categories, themes, topics, open data, gta, ontario, browse
    """  # noqa: E501
    return await _call_client(
        fetch_list_categories("aurora", lang),
        api_url=PORTAL_URLS["aurora"] or "",
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Curated York Region tools (6)
# ---------------------------------------------------------------------------


@tool
async def york_region_get_transit_stops(
    query: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search York Region (YRT/Viva) transit stops from the GTFS-sourced FeatureServer. ~4,810 bus stops across the region.

    Field names are ESRI-style ALL_CAPS: STOP_ID, STOP_NAME, WHEELCHAIR_BOARDING.

    Use for: finding YRT/Viva bus stops by name pattern.
    Keywords: york region, yrt, viva, transit, bus stops, public transit, gtfs, schedule, route, wheelchair, accessibility, gta
    """  # noqa: E501
    return await _call_client(
        fetch_transit_stops(query, include_geometry),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_transit_routes(
    route_short_name: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List York Region (YRT/Viva) bus routes from the GTFS-sourced FeatureServer.

    Use for: listing all YRT/Viva routes or finding a specific route by short name.
    Keywords: york region, yrt, viva, transit, bus routes, route, line, schedule, public transit, gtfs, service, gta
    """  # noqa: E501
    return await _call_client(
        fetch_transit_routes(route_short_name, include_geometry),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_road_network(
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Fetch the York Region regional road network (~762 regional roads).

    Use for: retrieving regional road infrastructure spatial data.
    Keywords: york region, roads, road network, regional roads, infrastructure, transportation, ontario, gta, routes, highway
    """  # noqa: E501
    return await _call_client(
        fetch_regional_roads(include_geometry),
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_public_health(
    location_type: Literal["beach_water", "hospital", "drinking_water"],
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query York Region public health & safety datasets: beach water testing, hospital locations, or drinking water adverse incidents.

    Use for: finding hospitals, beach water testing stations, or drinking water adverse incidents in York Region.
    Keywords: york region, public health, beach water, water testing, hospital, drinking water, adverse incident, safety, health, medical, gta
    """  # noqa: E501
    if location_type == "beach_water":
        coro = fetch_beach_water_testing(include_geometry)
    elif location_type == "hospital":
        coro = fetch_hospitals(include_geometry)
    elif location_type == "drinking_water":
        coro = fetch_drinking_water_incidents(include_geometry)
    else:
        return make_error(
            "INVALID_INPUT",
            f"location_type must be beach_water, hospital, or drinking_water; got {location_type!r}",
            lang=lang,
            valid=["beach_water", "hospital", "drinking_water"],
        )
    return await _call_client(
        coro,
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_census_demographics(
    dataset: Literal["age_sex", "income"],
    csdname: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Fetch 2021 Canadian Census data (age/sex or income) by Dissemination Area for York Region municipalities.

    csdname filters to a Census Subdivision name like 'Markham', 'Vaughan', 'Newmarket'. Returns a focused
    field set (10 key columns) — not all 364 census variables.

    Use for: querying 2021 census age/sex distribution or total income by Dissemination Area, optionally filtered to a specific Census Subdivision (e.g., Markham, Vaughan).
    Keywords: york region, 2021 census, demographics, population, age, sex, income, dissemination area, DA, CSD, statistics canada, ontario
    """  # noqa: E501
    if dataset == "age_sex":
        coro = fetch_census_age_sex(csdname, include_geometry)
    elif dataset == "income":
        coro = fetch_census_income(csdname, include_geometry)
    else:
        return make_error(
            "INVALID_INPUT",
            f"dataset must be age_sex or income; got {dataset!r}",
            lang=lang,
            valid=["age_sex", "income"],
        )
    return await _call_client(
        coro,
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


@tool
async def york_region_get_waste_data(
    dataset: Literal["diversion_statistics", "sites"],
    year: int | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query York Region waste management data: annual diversion tonnages (2010-2021) or solid waste site locations.

    Note: year parameter only applies to diversion_statistics (e.g., year=2021 returns that year's tonnage).
    For sites, year is ignored.

    Use for: analyzing waste diversion trends or mapping solid waste facilities.
    Keywords: york region, waste, recycling, diversion, tonnage, solid waste, landfill, environment, sustainability, gta, ontario, annual
    """  # noqa: E501
    if dataset == "diversion_statistics":
        coro = fetch_waste_diversion(year)
    elif dataset == "sites":
        coro = fetch_solid_waste_sites(include_geometry)
    else:
        return make_error(
            "INVALID_INPUT",
            f"dataset must be diversion_statistics or sites; got {dataset!r}",
            lang=lang,
            valid=["diversion_statistics", "sites"],
        )
    return await _call_client(
        coro,
        api_url=PORTAL_URLS["york_region"] or "",
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Curated Markham tools (2)
# ---------------------------------------------------------------------------


@tool
async def markham_get_addresses(
    street: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Markham civic addresses (OD_ADDRESSES). Fields: FULL_ADDRESS, STREET, TYPE, MUNICIPALITY, WM_AREA.

    Use for: finding civic addresses in Markham by street name substring.
    Keywords: markham, addresses, civic address, street, municipal, gta, ontario, address points, property, location, geocoding
    """  # noqa: E501
    return await _call_client(
        fetch_markham_addresses(street, include_geometry),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )


@tool
async def markham_get_road_network(
    name: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Fetch the Markham Street & Linear Road Network (SLRN). Fields: NAME, TYPE, FULLNAME, OWNER. maxRecordCount=2000.

    Use for: retrieving Markham road network spatial data, optionally filtered by road name substring.
    Keywords: markham, roads, road network, slrn, street, transportation, infrastructure, gta, ontario, linear road network, municipal
    """  # noqa: E501
    return await _call_client(
        fetch_markham_roads(name, include_geometry),
        api_url=PORTAL_URLS["markham"] or "",
        lang=lang,
    )
