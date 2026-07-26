"""Toronto Open Data @tool functions.

Provides 12 intent-based MCP tools for querying the City of Toronto's
Open Data portal (open.toronto.ca) with 500+ municipal datasets.
Includes TTC GTFS transit data, neighbourhood census profiles,
311 service requests, RentSafeTO evaluations, and short-term rentals.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.toronto.client import (
    fetch_311_requests,
    fetch_dataset_count,
    fetch_dataset_details,
    fetch_gtfs_routes,
    fetch_gtfs_stops,
    fetch_neighbourhood_comparison,
    fetch_neighbourhood_profile,
    fetch_organizations,
    fetch_rentsafe_evaluations,
    fetch_resource,
    fetch_search_datasets,
    fetch_short_term_rentals,
)
from mcp_canada.shared.envelope import make_error, make_response, upstream_guard

# API name and base URL for _meta envelope
_API_NAME = "toronto-open-data"
_API_URL = "https://open.toronto.ca"


# ---------------------------------------------------------------------------
# Tool 1: Search datasets
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME)
async def toronto_search_datasets(
    query: str,
    rows: int = 10,
    start: int = 0,
    sort: str = "score desc",
    filter_query: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Toronto's Open Data portal (open.toronto.ca) for datasets by keyword.

    Use for: finding Toronto municipal datasets on any topic — transit, cycling, housing, parks, permits, zoning, crime, elections, parking, and more.
    Keywords: toronto, municipal, open data, search, dataset, catalogue, city, TTC, transit, housing, parks, permits, zoning, cycling, elections.
    """
    try:
        datasets, cached = await fetch_search_datasets(
            query=query,
            rows=rows,
            start=start,
            sort=sort,
            fq=filter_query,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
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
async def toronto_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full details for a specific Toronto Open Data dataset including all resources.

    Use for: retrieving complete metadata, resources list, and description for a known dataset ID or slug from open.toronto.ca. Resources include datastore_active flag indicating CKAN datastore availability.
    Keywords: toronto, dataset, details, metadata, resources, files, open data, municipal, package, description, organization, tags, ckan, city hall.
    """
    try:
        dataset, cached = await fetch_dataset_details(dataset_id=dataset_id, lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Dataset '{dataset_id}' not found." if exc.response.status_code == 404
            else f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
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
@upstream_guard(_API_NAME)
async def toronto_get_resource(
    resource_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get details for a specific data resource (file) from the Toronto Open Data portal.

    Use for: retrieving format, size, URL, datastore_active flag, and description for a known resource UUID from open.toronto.ca datasets. Use after toronto_get_dataset_details to inspect individual files.
    Keywords: toronto, resource, file, download, url, format, csv, json, geojson, zip, size, open data, municipal, dataset resource, datastore.
    """
    try:
        resource, cached = await fetch_resource(resource_id=resource_id)
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"Resource '{resource_id}' not found." if exc.response.status_code == 404
            else f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
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
@upstream_guard(_API_NAME)
async def toronto_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all City of Toronto divisions and agencies that publish open data.

    Use for: discovering which Toronto city departments and agencies publish datasets, finding organizations by name, or browsing available data publishers on open.toronto.ca.
    Keywords: toronto, organizations, divisions, departments, agencies, publishers, municipal, government, city, list, browse, open data, catalogue.
    """
    try:
        orgs, cached = await fetch_organizations()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
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
@upstream_guard(_API_NAME)
async def toronto_get_dataset_stats(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get aggregate statistics for the Toronto Open Data portal (open.toronto.ca).

    Use for: finding out how many datasets are available on the Toronto Open Data portal, getting a high-level overview of the open.toronto.ca catalogue size and scope.
    Keywords: toronto, statistics, stats, count, total, datasets, portal, summary, overview, municipal, open data, catalogue, how many, city.
    """
    try:
        count, cached = await fetch_dataset_count()
    except httpx.HTTPStatusError as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
            lang=lang,
        )

    stats = {
        "total_datasets": count,
        "portal": "open.toronto.ca",
        "api_version": "CKAN 2.9",
    }

    return make_response(
        stats,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Get TTC stops
# ---------------------------------------------------------------------------


@tool
async def toronto_get_ttc_stops(
    query: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search TTC (Toronto Transit Commission) stops by name from GTFS static schedule.

    Use for: finding TTC subway stations, bus stops, or streetcar stops by name. Returns stop ID, name, and GPS coordinates. Filter by partial name (e.g., "King" finds King Station).
    Keywords: TTC, transit, stops, subway, bus, streetcar, Toronto, public transit, station, GTFS, schedule, location, GPS, coordinates.
    """
    try:
        stops, cached = await fetch_gtfs_stops(query=query)
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch TTC GTFS stop data.",
            lang=lang,
        )

    return make_response(
        stops,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Get TTC routes
# ---------------------------------------------------------------------------


@tool
async def toronto_get_ttc_routes(
    route_type: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List TTC (Toronto Transit Commission) routes from GTFS static schedule data.

    Use for: listing all TTC routes, filtering by type (0=streetcar, 1=subway, 3=bus). Returns route ID, short name, long name, and type. Note: route_type is a GTFS code string.
    Keywords: TTC, routes, bus, subway, streetcar, transit, schedule, Toronto, line, service, GTFS, route number, route type.
    """
    try:
        routes, cached = await fetch_gtfs_routes(route_type=route_type)
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch TTC GTFS route data.",
            lang=lang,
        )

    return make_response(
        routes,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Get neighbourhood profile
# ---------------------------------------------------------------------------


@tool
async def toronto_get_neighbourhood_profile(
    neighbourhood: str | None = None,
    characteristic: str | None = None,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get census indicator data for Toronto neighbourhoods from the Neighbourhood Profiles dataset.

    Data from the 2016 census, covering 140 neighbourhoods and 2,383 characteristics including
    population, income, housing, education, and demographics. Filter by neighbourhood name or
    characteristic keyword.
    Use for: getting population statistics, income levels, housing tenure, education, demographics for a specific Toronto neighbourhood. Data covers the 140-neighbourhood model used by City planning.
    Keywords: neighbourhood, census, profile, demographics, population, income, housing, Toronto, ward, community, education, age, 2016, characteristics.
    """
    try:
        rows, cached = await fetch_neighbourhood_profile(
            neighbourhood=neighbourhood,
            characteristic=characteristic,
            limit=limit,
        )
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch neighbourhood profile data.",
            lang=lang,
        )

    return make_response(
        rows,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 9: Compare neighbourhoods
# ---------------------------------------------------------------------------


@tool
async def toronto_compare_neighbourhoods(
    characteristic: str,
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Compare a single census indicator across all 140 Toronto neighbourhoods.

    Use for: ranking or comparing neighbourhoods by a specific census characteristic — e.g., "Median household income", "Population, 2016", "Average age". Returns all 140 neighbourhoods with their value for the specified indicator.
    Keywords: neighbourhood, comparison, indicator, census, demographics, ranking, Toronto, community, statistics, benchmark, 2016, income, population, age.
    """
    try:
        rows, cached = await fetch_neighbourhood_comparison(
            characteristic=characteristic,
            limit=limit,
        )
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch neighbourhood comparison data.",
            lang=lang,
        )

    return make_response(
        rows,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 10: Get 311 service requests
# ---------------------------------------------------------------------------


@tool
async def toronto_get_311_requests(
    year: int,
    ward: str | None = None,
    service_type: str | None = None,
    status: str | None = None,
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Fetch Toronto 311 service requests (citizen complaints and service calls) for a given year.

    Note: data is fetched as an annual ZIP file — first call for a year may be slow (large download).
    Supports filtering by ward number, service type (e.g., "Pothole", "Noise"), and status (Open/Closed).
    Use for: analyzing municipal service requests, complaint volumes, ward-level service issues, pothole reports, noise complaints, garbage collection requests, bylaw enforcement calls.
    Keywords: 311, service request, complaint, Toronto, ward, bylaw, noise, garbage, pothole, parking, graffiti, rodent, snow, inspection, open closed.
    """
    try:
        requests, cached = await fetch_311_requests(
            year=year,
            ward=ward,
            service_type=service_type,
            status=status,
            limit=limit,
        )
    except httpx.HTTPStatusError as exc:
        return make_error(
            "NOT_FOUND" if exc.response.status_code == 404 else "UPSTREAM_ERROR",
            f"311 data for year {year} not found." if exc.response.status_code == 404
            else f"Toronto Open Data portal returned HTTP {exc.response.status_code}.",
            lang=lang,
        )
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch 311 service request data for year {year}.",
            lang=lang,
        )

    return make_response(
        requests,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 11: Get RentSafeTO apartment evaluations
# ---------------------------------------------------------------------------


@tool
async def toronto_get_rentsafe_evaluations(
    ward: str | None = None,
    min_score: int | None = None,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query RentSafeTO apartment building evaluation scores from City of Toronto inspections.

    Use for: finding apartment building safety ratings, comparing evaluation scores by ward, identifying buildings below a minimum score, tenant research on landlord compliance, rental housing inspection results.
    Keywords: RentSafeTO, apartment, building, evaluation, score, ward, housing, inspection, Toronto, tenant, landlord, rental, compliance, safety.
    """
    try:
        evaluations, cached = await fetch_rentsafe_evaluations(
            ward=ward,
            min_score=min_score,
            limit=limit,
        )
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch RentSafeTO evaluation data.",
            lang=lang,
        )

    return make_response(
        evaluations,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 12: Get short-term rental registrations
# ---------------------------------------------------------------------------


@tool
async def toronto_get_short_term_rentals(
    ward: str | None = None,
    status: str | None = None,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query Toronto short-term rental (STR) operator registration records.

    Use for: researching Airbnb or VRBO registrations in Toronto, checking STR licence compliance by ward, finding active vs. suspended rental operators, analyzing short-term rental density by neighbourhood.
    Keywords: short-term rental, Airbnb, VRBO, registration, Toronto, housing, ward, licence, accommodation, vacation, operator, STR, rental, platform.
    """
    try:
        rentals, cached = await fetch_short_term_rentals(
            ward=ward,
            status=status,
            limit=limit,
        )
    except Exception:
        return make_error(
            "UPSTREAM_ERROR",
            "Failed to fetch short-term rental registration data.",
            lang=lang,
        )

    return make_response(
        rentals,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
