"""Quebec tools — discovery tools (Plan 02) + stubs for Plans 03/04.

Discovery tools (Plan 02):
  quebec_search_datasets, quebec_get_dataset_details, quebec_query_dataset,
  quebec_list_organizations, quebec_list_categories

Health/Transport tools (Plan 03):
  quebec_get_health_installations, quebec_get_er_wait_times,
  quebec_get_population_by_municipality, quebec_get_road_conditions,
  quebec_get_road_works, quebec_get_road_events, quebec_get_bridge_structures

Environment/Energy tools (Plan 04):
  quebec_get_forest_fires_history, quebec_get_air_quality_stations,
  quebec_get_air_quality_index, quebec_get_water_quality_monitoring,
  quebec_get_electricity_data, quebec_get_protected_areas
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client
from .constants import BASE_URL

# Source identifier for the _meta envelope
API_NAME = "donnees-quebec"

__all__ = [
    "quebec_search_datasets",
    "quebec_get_dataset_details",
    "quebec_query_dataset",
    "quebec_list_organizations",
    "quebec_list_categories",
]


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


@tool
async def quebec_search_datasets(
    q: str,
    rows: int = 20,
    start: int = 0,
    organization: str | None = None,
    group: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search the Données Québec open data catalogue (1,593 datasets, 139 orgs).

    Use for: Discovering Quebec provincial open data across health, transport, environment, demographics. Federated catalog includes municipal (Montreal BIXI/ARTM) and parastatal data.
    Keywords: quebec, open data, donnees quebec, ckan, search, catalog, datasets, provincial, francais, bilingual, dq, recherche

    Note: titles and descriptions are in French (primary language of Données Québec).
    Use `discover_tools` + `call_tool` with `lang="fr"` when you want all-French output.
    Montreal-specific data appears here but will be comprehensively covered in a future
    Phase 27 Montreal module.
    """
    if not q or not q.strip():
        msg = (
            "quebec_search_datasets requires a non-empty q parameter"
            if lang == "en"
            else "quebec_search_datasets nécessite un paramètre q non vide"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        results, cached = await _client.fetch_search_datasets(
            q=q.strip(),
            rows=min(max(rows, 1), 100),
            start=max(start, 0),
            organization=organization,
            group=group,
        )
    except httpx.HTTPStatusError as exc:
        msg = f"Upstream CKAN error: {exc}" if lang == "en" else f"Erreur CKAN: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in results],
        api_name=API_NAME,
        api_url=BASE_URL + "package_search",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_dataset_details(
    package_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full details for a Données Québec dataset including resources list and datastore_active flags.

    Use for: Inspecting a specific Quebec dataset's resources (CSV/GeoJSON/XLSX) and checking which are queryable via CKAN datastore_search.
    Keywords: quebec, dataset, details, metadata, resources, datastore, package show, ckan, donnees quebec, ressources

    Note: Use the `name` slug from quebec_search_datasets results as the package_id parameter.
    """
    if not package_id or not package_id.strip():
        msg = (
            "quebec_get_dataset_details requires a package_id"
            if lang == "en"
            else "quebec_get_dataset_details nécessite un package_id"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        details, cached = await _client.fetch_dataset_details(package_id.strip())
    except httpx.HTTPStatusError:
        msg = (
            f"Dataset not found or CKAN error: {package_id}"
            if lang == "en"
            else f"Jeu de données introuvable ou erreur CKAN: {package_id}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    return make_response(
        data=details.model_dump(),
        api_name=API_NAME,
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_query_dataset(
    package_id: str,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query records from a Données Québec dataset's best resource (CSV > GeoJSON > JSON > XLSX).

    Use for: Fetching actual data rows from a DQ dataset — routes datastore-active resources to datastore_search, otherwise parses the file resource via fetch_and_parse.
    Keywords: quebec, query, dataset, records, data, datastore, csv, geojson, xlsx, fetch, ckan, donnees

    Note: Routes datastore_active=True resources to CKAN datastore_search (fast, paginated).
    Otherwise falls back to fetch_and_parse() for file resources.
    """
    if not package_id or not package_id.strip():
        msg = "package_id required" if lang == "en" else "package_id requis"
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        payload, cached = await _client.fetch_query_dataset(
            package_id.strip(),
            limit=min(max(limit, 1), 1000),
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Error querying dataset: {exc}"
            if lang == "en"
            else f"Erreur lors de la requête: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = f"Unexpected error: {exc}" if lang == "en" else f"Erreur inattendue: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=API_NAME,
        api_url=payload.get("resource_url", BASE_URL),
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all 139 organizations in the Données Québec federated catalog with package counts.

    Use for: Discovering which Quebec provincial ministries, municipalities, and parastatal entities publish open data; finding org slugs for filtering quebec_search_datasets.
    Keywords: quebec, organizations, ministries, orgs, publishers, donnees quebec, federated, ckan, catalog, organisations, ministeres

    Note: The catalog is federated — includes municipal (Ville de Montréal) and parastatal (Hydro-Québec, BIXI) alongside provincial ministries.
    """
    try:
        orgs, cached = await _client.fetch_organizations()
    except httpx.HTTPStatusError as exc:
        msg = f"Upstream error: {exc}" if lang == "en" else f"Erreur: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[o.model_dump() for o in orgs],
        api_name=API_NAME,
        api_url=BASE_URL + "organization_list",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List the 10 thematic groups (Santé, Environnement, etc.) used to categorize Données Québec datasets.

    Use for: Browsing Quebec datasets by high-level theme; finding group slugs for the `group` filter on quebec_search_datasets.
    Keywords: quebec, categories, groups, themes, topics, donnees quebec, ckan, group list, sante, environnement, thematiques

    Note: Uses CKAN group_list (NOT tag_list). DQ has 10 meaningful thematic groups;
    tag_list returns 4,200+ noisy tags and is not exposed here.
    """
    try:
        cats, cached = await _client.fetch_categories()
    except httpx.HTTPStatusError as exc:
        msg = f"Upstream error: {exc}" if lang == "en" else f"Erreur: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[c.model_dump() for c in cats],
        api_name=API_NAME,
        api_url=BASE_URL + "group_list",
        cached=cached,
        lang=lang,
    )
