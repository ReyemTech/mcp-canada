"""Manitoba module tools.

5 discovery tools (Plan 02): manitoba_search_datasets, manitoba_get_dataset_details,
manitoba_query_dataset, manitoba_list_organizations, manitoba_list_categories.

3 flood/hydrology tools (Plan 03): manitoba_get_flood_alerts,
manitoba_get_river_stations, manitoba_get_provincial_waterways.

Plans 04-06 add curated tools.

Every @tool:
  - Uses standalone `@tool` from fastmcp.tools (NEVER @mcp.tool)
  - Accepts lang: Literal["en", "fr"] = "en"
  - Returns make_response() on success / make_error() on failure
  - Has Use for: + single-line Keywords: (8+ terms) in docstring
  - Uses manitoba_ prefix
"""

from typing import Any, Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client
from .constants import (
    FLOOD_ALERTS_FS_URL,
    HUB_BASE_URL,
    HUB_SEARCH_URL,
    PROVINCIAL_WATERWAYS_FS_URL,
    RIVER_CONDITIONS_CSV_URL,
    WATERWAY_TYPES,
)

# Source identifiers for the _meta envelope
_API_NAME_HUB = "manitoba-geoportal-hub"
_API_NAME_FLOOD = "manitoba-flood-alerts"
_API_NAME_RIVER = "manitoba-river-conditions"
_API_NAME_WATERWAYS = "manitoba-provincial-waterways"

__all__ = [
    # Discovery (Plan 02)
    "manitoba_search_datasets",
    "manitoba_get_dataset_details",
    "manitoba_query_dataset",
    "manitoba_list_organizations",
    "manitoba_list_categories",
    # Flood / hydrology (Plan 03)
    "manitoba_get_flood_alerts",
    "manitoba_get_river_stations",
    "manitoba_get_provincial_waterways",
]


# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


@tool
async def manitoba_search_datasets(
    query: str = "",
    category: str | None = None,
    num: int = 10,
    start: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Manitoba's geoportal.gov.mb.ca ArcGIS Hub catalogue by keyword.

    Use for: Discovering Manitoba provincial datasets on the government's primary geoportal. Searches 90+ ArcGIS Hub items including parks, flood alerts, waterways, agriculture, health, fisheries, and forests. NOTE: This is the Government of Manitoba's provincial ArcGIS Hub (geoportal.gov.mb.ca); municipal data (Winnipeg, Brandon) is on separate portals not covered by this tool.

    Keywords: manitoba search datasets geoportal hub arcgis catalogue discover datasets provincial government open data search browse
    """
    try:
        payload, cached = await _client.fetch_search_datasets(
            query=query,
            category=category,
            num=num,
            start=start,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du portail de données: {exc}"
            if lang == "fr"
            else f"Manitoba geoportal search failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full details for a Manitoba geoportal dataset by its Hub item ID.

    Use for: Inspecting a specific Manitoba dataset's metadata, FeatureServer URL, and download links. Use the ID from manitoba_search_datasets results. Returns feature_server_url (use with manitoba_query_dataset), download_urls, tags, categories, and licence information.

    Keywords: manitoba dataset details metadata feature server url download inspect hub item id arcgis geoportal
    """
    if not dataset_id or not dataset_id.strip():
        msg = "dataset_id est requis" if lang == "fr" else "dataset_id is required"
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        payload, cached = await _client.fetch_dataset_details(
            item_id=dataset_id.strip(),
            lang=lang,
        )
    except ValueError:
        msg = (
            f"Jeu de données introuvable: {dataset_id}"
            if lang == "fr"
            else f"Dataset not found: {dataset_id}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du portail: {exc}"
            if lang == "fr"
            else f"Geoportal error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HUB,
        api_url=f"{HUB_BASE_URL}/api/search/v1/collections/all/items/{dataset_id.strip()}",
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_query_dataset(
    dataset_url: str,
    where: str = "1=1",
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a Manitoba dataset resource — auto-routes by URL type.

    Use for: Fetching records from a Manitoba FeatureServer or file resource. Pass the feature_server_url from manitoba_get_dataset_details. Auto-routes: FeatureServer URL → ArcGIS query with WHERE clause; CSV/JSON/GeoJSON/XLSX → file parse; other (PDF, ZIP) → metadata-only with 'note'. max_records is capped at 5000.

    Keywords: manitoba query dataset feature server arcgis fetch records rows filter where clause csv geojson parse router
    """
    if not dataset_url or not dataset_url.strip():
        msg = "dataset_url est requis" if lang == "fr" else "dataset_url is required"
        return make_error("INVALID_INPUT", msg, lang=lang)
    clamped_max = max(1, min(max_records, 5000))
    try:
        payload, cached = await _client.fetch_query_dataset(
            feature_server_url=dataset_url.strip(),
            where=where,
            max_records=clamped_max,
            include_geometry=include_geometry,
            lang=lang,
        )
    except Exception as exc:
        msg = (
            f"Erreur lors de la requête: {exc}"
            if lang == "fr"
            else f"Query failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HUB,
        api_url=dataset_url.strip(),
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List Manitoba government organizations publishing on geoportal.gov.mb.ca.

    Use for: Discovering which Manitoba government departments and agencies publish data on the provincial ArcGIS Hub. Returns owner names usable as search context when calling manitoba_search_datasets. Includes Manitoba Government, Manitoba Agriculture, Conservation and Climate, and other provincial departments.

    Keywords: manitoba organizations publishers government departments arcgis hub geoportal data owners provincial list catalog
    """
    try:
        payload, cached = await _client.fetch_organizations(lang=lang)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du portail: {exc}"
            if lang == "fr"
            else f"Geoportal error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List dataset categories and themes on Manitoba's geoportal.gov.mb.ca.

    Use for: Discovering dataset categories on the Manitoba provincial ArcGIS Hub to narrow searches. Returns category path strings like '/Categories/Environment', '/Categories/Agriculture', '/Categories/Disaster Response'. Pass a category value as the category= parameter to manitoba_search_datasets to filter results by theme.

    Keywords: manitoba categories themes topics tags geoportal hub arcgis filter environment agriculture health disaster open data
    """
    try:
        payload, cached = await _client.fetch_categories(lang=lang)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur du portail: {exc}"
            if lang == "fr"
            else f"Geoportal error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HUB,
        api_url=HUB_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Flood / Hydrology (Plan 03)
# ---------------------------------------------------------------------------


@tool
async def manitoba_get_flood_alerts(
    include_geometry: bool = True,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current overland flood watch and warning polygons for Manitoba.

    Use for: Checking active flood alerts in Manitoba — returns bilingual Type_EN/Type_FR watch/warning polygons from Manitoba Infrastructure's Overland_Flood_Alerts layer. Returns empty features list when no alerts are active (this is NORMAL, not an error). Flood bulletin PDFs from the Hydrologic Forecast Centre are NOT available here.

    Keywords: manitoba flood alerts watch warning overland polygons bilingual flood zone active current hydrology emergency Manitoba Infrastructure
    """
    try:
        payload, cached = await _client.fetch_flood_alerts(
            include_geometry=include_geometry,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des alertes: {exc}"
            if lang == "fr"
            else f"Flood alerts fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_FLOOD,
        api_url=FLOOD_ALERTS_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_river_stations(
    alert_only: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba river and hydrometric station locations with flood status.

    Use for: Finding river monitoring station locations and current flood status across Manitoba. Returns station points with alert field (No Flooding / High Water Advisory / Flood Watch / Flood Warning). NOTE: Returns station LOCATIONS and status only, NOT real-time water level readings — for actual HYDAT level/flow data use wateroffice.ec.gc.ca (ECCC). Set alert_only=True to return only stations with active warnings.

    Keywords: manitoba river stations hydrometric flood watch warning alert locations water level status monitoring Red River Assiniboine CSV
    """
    try:
        payload, cached = await _client.fetch_river_stations(
            alert_only=alert_only,
            lang=lang,
        )
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des stations: {exc}"
            if lang == "fr"
            else f"River stations fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_RIVER,
        api_url=RIVER_CONDITIONS_CSV_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_provincial_waterways(
    f_type: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba provincial waterway infrastructure — dikes, floodways, dams, diversions, and reservoirs.

    Use for: Querying Manitoba's water control infrastructure from the Provincial_Waterways layer. Filter by f_type to get specific infrastructure: 'dike', 'floodway', 'dam', 'diversion', 'reservoir', or 'waterway'. Fields: F_TYPE, Name, Watershed, WCW (Water Control Works number), LengthKM. Includes the Red River Floodway (47 km) and Portage Diversion.

    Keywords: manitoba waterways dike floodway dam diversion reservoir water control infrastructure watershed Red River Portage Diversion WCW LengthKM
    """
    try:
        payload, cached = await _client.fetch_provincial_waterways(
            f_type=f_type,
            max_records=min(max(max_records, 1), 5000),
            include_geometry=include_geometry,
            lang=lang,
        )
    except ValueError as exc:
        msg = (
            f"Type de voie navigable invalide. Options valides: {', '.join(WATERWAY_TYPES)}"
            if lang == "fr"
            else str(exc)
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=list(WATERWAY_TYPES))
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des voies navigables: {exc}"
            if lang == "fr"
            else f"Waterways fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_WATERWAYS,
        api_url=PROVINCIAL_WATERWAYS_FS_URL,
        cached=cached,
        lang=lang,
    )
