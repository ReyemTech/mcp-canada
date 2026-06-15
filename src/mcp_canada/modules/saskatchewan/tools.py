"""Saskatchewan module tools.

5 discovery tools (Plan 02): saskatchewan_search_datasets,
saskatchewan_get_dataset_details, saskatchewan_query_dataset,
saskatchewan_list_organizations, saskatchewan_list_categories.

Plans 03-05 add curated tools.

Every @tool:
  - Uses standalone `@tool` from fastmcp.tools (NEVER @mcp.tool)
  - Accepts lang: Literal["en", "fr"] = "en"
  - Returns make_response() on success / make_error() on failure
  - Has Use for: + single-line Keywords: (8+ terms) in docstring
  - Uses saskatchewan_ prefix
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client
from .constants import (
    GRAIN_ELEVATORS_FS_URL,
    HUB_BASE_URL,
    HUB_ORG_BASE,
    HUB_SEARCH_URL,
    MINERAL_MINES_FS_URLS,
)

# Source identifier for the _meta envelope (all discovery tools)
_API_NAME_HUB = "saskatchewan-geohub"

__all__ = [
    # Discovery (Plan 02)
    "saskatchewan_search_datasets",
    "saskatchewan_get_dataset_details",
    "saskatchewan_query_dataset",
    "saskatchewan_list_organizations",
    "saskatchewan_list_categories",
    # Agriculture + Mining (Plan 03)
    "saskatchewan_get_crop_yields",
    "saskatchewan_get_grain_elevators",
    "saskatchewan_get_mineral_mines",
]


# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


@tool
async def saskatchewan_search_datasets(
    query: str = "",
    category: str | None = None,
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Saskatchewan's geohub.saskatchewan.ca ArcGIS Hub catalogue by keyword.

    Use for: Discovering Saskatchewan provincial datasets on the government's primary geoportal (geohub.saskatchewan.ca). Searches 180+ ArcGIS Hub items covering agriculture, mining, wildfire, air quality, water, and environment. NOTE: This is the Government of Saskatchewan provincial ArcGIS Hub (org zcv98lgAl8xQ04cW); WSA water data and SPSA fire-ban data live on separate services and are reached via the curated tools, NOT Hub Search.

    Keywords: saskatchewan search datasets geohub hub arcgis catalogue discover provincial government open data browse keyword
    """
    try:
        payload, cached = await _client.fetch_search_datasets(
            query=query,
            category=category,
            limit=limit,
            offset=offset,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full metadata for a Saskatchewan GeoHub dataset by ID, including FeatureServer URL.

    Use for: Retrieving complete metadata for a specific Saskatchewan geoportal dataset. Returns FeatureServer URL, download links, description, tags, and categories. Use after saskatchewan_search_datasets to get the URL needed for saskatchewan_query_dataset.

    Keywords: saskatchewan dataset details metadata feature server url download hub item arcgis geohub
    """
    try:
        payload, cached = await _client.fetch_dataset_details(dataset_id=dataset_id)
    except ValueError as exc:
        msg = (
            f"Ensemble de données introuvable: {dataset_id}"
            if lang == "fr"
            else f"Dataset not found: {dataset_id}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=f"{HUB_SEARCH_URL}/{dataset_id}",
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_query_dataset(
    dataset_id: str,
    where: str = "1=1",
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a Saskatchewan dataset via auto-router: FeatureServer, CSV/GeoJSON/XLSX, or metadata.

    Use for: Fetching actual data records from a Saskatchewan GeoHub dataset. Provide the FeatureServer URL or file URL from saskatchewan_get_dataset_details. Auto-routes to arcgis_hub.query_feature_service for FeatureServer URLs, fetch_and_parse for CSV/GeoJSON/XLSX files, and returns metadata-only for PDF/ZIP/KML archives.

    Keywords: saskatchewan query dataset feature server data records arcgis geohub csv geojson xlsx download fetch
    """
    try:
        payload, cached = await _client.fetch_query_dataset(
            feature_server_url=dataset_id,
            where=where,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors de la requête du jeu de données: {exc.response.status_code}"
            if lang == "fr"
            else f"Dataset query error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=dataset_id,
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List Saskatchewan government publishing organizations on the geoportal.

    Use for: Discovering which government bodies publish data on Saskatchewan's ArcGIS Hub (geohub.saskatchewan.ca). Returns unique owner names derived from Hub Search results. Useful for narrowing subsequent searches by organization.

    Keywords: saskatchewan organizations publishers government bodies geohub hub arcgis owners agencies ministries list
    """
    try:
        payload, cached = await _client.fetch_organizations()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List dataset categories and themes on Saskatchewan's ArcGIS Hub geoportal.

    Use for: Discovering data categories available on Saskatchewan's geoportal (geohub.saskatchewan.ca). Returns unique category strings (e.g. /Categories/Agriculture, /Categories/Environment) derived from Hub Search results. Use returned categories as the category= filter in saskatchewan_search_datasets.

    Keywords: saskatchewan categories themes topics geohub hub arcgis agriculture environment mining wildfire water browse filter
    """
    try:
        payload, cached = await _client.fetch_categories()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Agriculture + Mining (Plan 03)
# ---------------------------------------------------------------------------

_CROP_REGIONS = ("provincial", "southeast", "southwest", "central", "northeast", "northwest")
_MINERALS = ("potash", "uranium", "helium", "coal")


@tool
async def saskatchewan_get_crop_yields(
    region: str = "provincial",
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Saskatchewan estimated crop yields (bu/acre) by region for 16 crop types.

    Use for: Retrieving Saskatchewan provincial estimated crop yields by crop reporting region. Dispatches between provincial summary and 5 sub-regions: southeast, southwest, central, northeast, northwest. Returns 16 crop estimates: HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean, Pea, Lentil, Chickpea, Canary_seed, Flax, Winter_wheat, Fall_rye, Other_wheat_. NOTE: yields are estimated bu/acre from the annual crop report cycle; weekly PDF crop reports are NOT machine-readable — this FeatureServer is the machine-readable substitute.

    Keywords: saskatchewan crop yields agriculture canola wheat lentil chickpea barley pea durum HRSW region harvest estimate bu/acre annual
    """
    from .constants import CROP_YIELDS_PROVINCE_FS_URL, CROP_YIELDS_REGIONS_FS_URL

    valid = list(_CROP_REGIONS)
    if region.lower() not in _CROP_REGIONS:
        msg = (
            f"Région invalide: {region!r}. Valeurs valides: {valid}"
            if lang == "fr"
            else f"Invalid region: {region!r}. Valid: {valid}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=valid)

    # Build the FS URL for envelope source attribution
    fs_url = (
        CROP_YIELDS_PROVINCE_FS_URL
        if region.lower() == "provincial"
        else CROP_YIELDS_REGIONS_FS_URL
    )

    try:
        payload, cached = await _client.fetch_crop_yields(region=region)
    except ValueError as exc:
        msg = (
            f"Région invalide: {exc}"
            if lang == "fr"
            else f"Invalid region: {exc}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=valid)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=f"{fs_url}/0",
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_get_grain_elevators(
    railway: Literal["CN", "CP", "SHORTLINE"] | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Saskatchewan grain elevator locations with station, railway, licensee, and capacity.

    Use for: Finding grain elevator locations in Saskatchewan with railway line, licensee, elevator type, and capacity in tonnes. Default returns all SK elevators from the Western Canada Grain Elevators 2024 dataset. Optional railway filter: CN, CP, or SHORTLINE.

    Keywords: saskatchewan grain elevator station railway CN CP SHORTLINE capacity tonne licensee primary process agriculture export terminal
    """
    try:
        payload, cached = await _client.fetch_grain_elevators(railway=railway)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=f"{GRAIN_ELEVATORS_FS_URL}/0",
        cached=cached,
        lang=lang,
    )


@tool
async def saskatchewan_get_mineral_mines(
    mineral: Literal["potash", "uranium", "helium", "coal"],
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Saskatchewan mineral mine locations for potash, uranium, helium, or coal.

    Use for: Retrieving Saskatchewan mineral mine data by mineral type. Dispatches to dated FeatureServers (2024 publication): potash (13 active mines, world's largest reserve), uranium (Athabasca Basin, Cameco operations), helium (emerging sector), coal (historical and active). Returns mine name, company, status, mine type, site, regulation, and date opened.

    Keywords: saskatchewan mineral mines potash uranium helium coal mining Cameco Mosaic Athabasca Basin K+S company status operating care maintenance
    """
    valid = list(_MINERALS)
    if mineral.lower() not in _MINERALS:
        msg = (
            f"Minéral invalide: {mineral!r}. Valeurs valides: {valid}"
            if lang == "fr"
            else f"Invalid mineral: {mineral!r}. Valid: {valid}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=valid)

    fs_url = MINERAL_MINES_FS_URLS.get(mineral.lower(), "")

    try:
        payload, cached = await _client.fetch_mineral_mines(mineral=mineral)
    except ValueError as exc:
        msg = (
            f"Minéral invalide: {exc}"
            if lang == "fr"
            else f"Invalid mineral: {exc}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=valid)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du géoportail Saskatchewan: {exc.response.status_code}"
            if lang == "fr"
            else f"Saskatchewan geoportal error: {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_HUB,
        api_url=f"{fs_url}/0",
        cached=cached,
        lang=lang,
    )
