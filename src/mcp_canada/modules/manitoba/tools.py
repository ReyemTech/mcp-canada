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

from mcp_canada.shared.envelope import make_error, make_response, upstream_guard

from . import client as _client
from .client import Five11NotConfigured
from .constants import (
    AG_WEATHER_STATIONS_FS_URL,
    CATTLE_PRICES_FS_URL,
    CROP_REGIONS_FS_URL,
    DROUGHT_MONITOR_FS_URL,
    FIVE11_BASE_URL,
    FLOOD_ALERTS_FS_URL,
    HUB_BASE_URL,
    HUB_SEARCH_URL,
    PROVINCIAL_FORESTS_FS_URL,
    PROVINCIAL_PARKS_FS_URL,
    PROVINCIAL_WATERWAYS_FS_URL,
    RIVER_CONDITIONS_CSV_URL,
    RURAL_HEALTH_FACILITIES_FS_URL,
    SURGICAL_WAIT_TIMES_FS_URL,
    WATERBODY_DATA_FS_URL,
    WATERWAY_TYPES,
)

# Source identifiers for the _meta envelope
_API_NAME_511 = "manitoba-511"
_API_NAME_HUB = "manitoba-geoportal-hub"
_API_NAME_FLOOD = "manitoba-flood-alerts"
_API_NAME_RIVER = "manitoba-river-conditions"
_API_NAME_WATERWAYS = "manitoba-provincial-waterways"
_API_NAME_DROUGHT = "manitoba-drought-monitor"
_API_NAME_AG_WEATHER = "manitoba-ag-weather-stations"
_API_NAME_LIVESTOCK = "manitoba-livestock-prices"
_API_NAME_CROP_REGIONS = "manitoba-crop-reporting-regions"
_API_NAME_PARKS = "manitoba-provincial-parks"
_API_NAME_FISHERIES = "manitoba-fisheries-waterbody"
_API_NAME_FORESTS = "manitoba-provincial-forests"
_API_NAME_WAIT_TIMES = "manitoba-surgical-wait-times"
_API_NAME_HEALTH_FACILITIES = "manitoba-rural-health-facilities"

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
    # Agriculture / drought (Plan 04)
    "manitoba_get_drought_status",
    "manitoba_get_ag_weather_stations",
    "manitoba_get_livestock_prices",
    "manitoba_get_crop_regions",
    # Environment / parks / health (Plan 05)
    "manitoba_get_provincial_parks",
    "manitoba_get_fisheries_data",
    "manitoba_get_provincial_forests",
    "manitoba_get_surgical_wait_times",
    "manitoba_get_health_facilities",
    # Transport / 511 (Plan 06)
    "manitoba_get_road_events",
    "manitoba_get_winter_road_conditions",
    "manitoba_get_traffic_cameras",
]


# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_HUB)
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
@upstream_guard(_API_NAME_HUB)
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
@upstream_guard(_API_NAME_HUB)
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
@upstream_guard(_API_NAME_HUB)
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
@upstream_guard(_API_NAME_FLOOD)
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
@upstream_guard(_API_NAME_WATERWAYS)
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


# ---------------------------------------------------------------------------
# Agriculture / Drought (Plan 04)
# ---------------------------------------------------------------------------


@tool
async def manitoba_get_drought_status(
    filter_province: bool = True,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current drought monitor status for Manitoba from the Canada/USA Drought Monitor layer.

    Use for: Checking current drought intensity (D0-D4) across Manitoba. Returns polygon features from the Canada_USA_Drought_Monitor FeatureServer filtered to Manitoba by default (Pitfall: this is a continental layer — filter_province=True applies Manitoba bounding box to avoid returning all of North America). D0=Abnormally Dry, D1=Moderate, D2=Severe, D3=Extreme, D4=Exceptional drought.

    Keywords: manitoba drought monitor D0 D1 D2 D3 D4 intensity polygon agricultural dry conditions prairie drought severity weekly status
    """
    try:
        payload, cached = await _client.fetch_drought_status(
            filter_province=filter_province,
            lang=lang,
        )
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement du moniteur de sécheresse: {exc}"
            if lang == "fr"
            else f"Drought monitor fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_DROUGHT,
        api_url=DROUGHT_MONITOR_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_ag_weather_stations(
    ag_region: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba agricultural weather station locations and live data links.

    Use for: Finding Manitoba Agriculture weather monitoring station locations and accessing live hourly readings per station. Returns StnName, coordinates (LatDD/LongDD), Elevation, AgRegion, and URL (links to live hourly weather data page at agrimaps.gov.mb.ca per station). Optional ag_region filter (e.g. 'Southwest', 'Central', 'Northwest', 'Southeast', 'Interlake').

    Keywords: manitoba agriculture weather stations hourly data AgRegion temperature precipitation ag climate monitoring Brandon Winnipeg Southwest Central farm weather
    """
    try:
        payload, cached = await _client.fetch_ag_weather_stations(
            ag_region=ag_region,
            lang=lang,
        )
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des stations météo agricoles: {exc}"
            if lang == "fr"
            else f"Agricultural weather stations fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_AG_WEATHER,
        api_url=AG_WEATHER_STATIONS_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_livestock_prices(
    livestock: str = "cattle",
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba weekly livestock market prices from Manitoba Agriculture.

    Use for: Retrieving weekly cattle or hog market prices from Manitoba Agriculture auctions. livestock='cattle' returns current year weekly prices from MB_Cattle_Prices_Current_year (auction, grade/parameter, $/cwt). livestock='hog' is provisionally supported but the hog FeatureServer URL was unresolved during spike — returns an empty result with a note if unresolved. Fields: week, Auction, Parameter, Measure, Value.

    Keywords: manitoba livestock prices cattle hog market auction weekly agriculture $/cwt grade steer heifer feeder market prices Winnipeg Brandon
    """
    try:
        payload, cached = await _client.fetch_livestock_prices(
            livestock=livestock,
            lang=lang,
        )
    except ValueError as exc:
        msg = (
            "Type de bétail invalide. Options valides: cattle, hog"
            if lang == "fr"
            else str(exc)
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=["cattle", "hog"])
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des prix du bétail: {exc}"
            if lang == "fr"
            else f"Livestock prices fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_LIVESTOCK,
        api_url=CATTLE_PRICES_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_crop_regions(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba crop reporting region boundaries with bilingual region names.

    Use for: Retrieving Manitoba Agriculture's 5 crop reporting region boundary polygons with bilingual names (REGION in English, RÉGION in French). Used to contextualize seasonal crop reports, yield estimates, and weather summaries published by Manitoba Agriculture. Regions: Central, Southwest, Northwest, Southeast, Interlake.

    Keywords: manitoba crop reporting regions boundaries bilingual agriculture REGION RÉGION polygon seasonal crop zones Central Southwest Northwest Southeast Interlake
    """
    try:
        payload, cached = await _client.fetch_crop_regions(lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des régions agricoles: {exc}"
            if lang == "fr"
            else f"Crop regions fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_CROP_REGIONS,
        api_url=CROP_REGIONS_FS_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Environment / Parks / Health (Plan 05)
# ---------------------------------------------------------------------------


@tool
async def manitoba_get_provincial_parks(
    park_type: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba provincial parks and protected areas (93 parks, bilingual).

    Use for: Retrieving Manitoba provincial parks, heritage parks, wilderness areas, park reserves, and Indigenous Traditional Use parks from the Manitoba_Parks FeatureServer. Returns bilingual NAME_E (English) and NOM_F (French) park names plus TYPE_E/TYPE_F, BIOME, O_AREA, STATUS_E, PROTDATE, PRK_CLSS, and URL. Optional park_type filter: 'Provincial', 'Heritage', 'Wilderness', 'Recreation', 'Natural', 'Park Reserve', 'Indigenous Traditional Use'.

    Keywords: manitoba parks provincial protected areas heritage wilderness bilingual NAME_E NOM_F park type BIOME area status recreation natural Indigenous Traditional Use
    """
    try:
        payload, cached = await _client.fetch_provincial_parks(
            park_type=park_type,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des parcs: {exc}"
            if lang == "fr"
            else f"Provincial parks fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des parcs: {exc}"
            if lang == "fr"
            else f"Provincial parks fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_PARKS,
        api_url=PROVINCIAL_PARKS_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_fisheries_data(
    region: str | None = None,
    name: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba fisheries and waterbody reference data (350+ water bodies).

    Use for: Retrieving Manitoba fisheries management data including fishing regulations, species lists, stocking records, Secchi depth (water clarity), and boat launch availability. Covers 350+ water bodies monitored by Manitoba Sustainable Development. Focused field subset: Name, SurfaceArea, AvgDepth, SecchiDepth, FishingDivision, Species, Regulations, BoatLaunch. Use name= to search for a specific lake or river. Use region= to filter by FishingDivision (e.g. 'Division 1').

    Keywords: manitoba fisheries waterbody fishing regulations species stocking Secchi depth boat launch lake river water quality Division walleye pickerel perch
    """
    try:
        payload, cached = await _client.fetch_fisheries_data(
            name_query=name,
            fishing_division=region,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des données halieutiques: {exc}"
            if lang == "fr"
            else f"Fisheries data fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des données halieutiques: {exc}"
            if lang == "fr"
            else f"Fisheries data fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_FISHERIES,
        api_url=WATERBODY_DATA_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_provincial_forests(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba provincial forest management boundaries.

    Use for: Retrieving Manitoba provincial forest management unit polygons from Manitoba_Provincial_Forests___Version_6 FeatureServer. Returns administrative forest region boundaries used for forest management planning and resource allocation across Manitoba's boreal and transitional forest zones. Useful for timber harvesting context, wildfire management zones, and conservation planning.

    Keywords: manitoba provincial forests forest management boundaries boreal timber harvesting conservation planning administrative zones resource management Version_6
    """
    try:
        payload, cached = await _client.fetch_provincial_forests(lang=lang)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des forêts provinciales: {exc}"
            if lang == "fr"
            else f"Provincial forests fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des forêts provinciales: {exc}"
            if lang == "fr"
            else f"Provincial forests fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_FORESTS,
        api_url=PROVINCIAL_FORESTS_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_surgical_wait_times(
    procedure: str | None = None,
    year: int | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba diagnostic and surgical wait time averages by procedure and year.

    Use for: Retrieving annual average wait times (in days) for diagnostic and surgical procedures across Manitoba from Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages FeatureServer. Fields: Year, IndicatorDataArea (procedure type), Average_Wait (days). NOTE: These are ANNUAL AVERAGES, not live ER wait times — real-time ER waits are not published in machine-readable form. Filter by procedure= (LIKE search on IndicatorDataArea) or year= for specific years. Manitoba's 5 RHAs: WRHA, PMH, IERHA, SHSS, NHR.

    Keywords: manitoba surgical wait times diagnostic procedure annual averages hospital health care wait list days cardiac orthopedic cataract colonoscopy MRI CT scan RHA
    """
    try:
        payload, cached = await _client.fetch_surgical_wait_times(
            procedure=procedure,
            year=year,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des temps d'attente: {exc}"
            if lang == "fr"
            else f"Surgical wait times fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des temps d'attente: {exc}"
            if lang == "fr"
            else f"Surgical wait times fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_WAIT_TIMES,
        api_url=SURGICAL_WAIT_TIMES_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_health_facilities(
    rha: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba rural health care facilities with emergency, acute care, and PCH flags.

    Use for: Retrieving rural health care facility locations and service availability across Manitoba from Rural_Health_Care_Facilities_in_Manitoba FeatureServer (spike-resolved). Fields: Community_Name, Facility_Name, coordinates, Emergency_Department_Availabili (Yes/No), Percentage_of_Time_Open__2015_, Nearest_Alternate_Emergency_Dep, Acute_Care_Availability, Acute_Care_Number_of_Beds. Optional rha= filter to search by community name substring. Manitoba's 5 RHAs: WRHA (Winnipeg), PMH (Prairie Mountain Health), IERHA (Interlake-Eastern), SHSS (Southern Health-Santé Sud), NHR (Northern Health Region).

    Keywords: manitoba rural health care facilities emergency department acute care PCH hospital community RHA WRHA PMH IERHA SHSS NHR Selkirk Brandon Portage facilities beds
    """
    try:
        payload, cached = await _client.fetch_health_facilities(
            community=rha,
            lang=lang,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors du chargement des établissements de santé: {exc}"
            if lang == "fr"
            else f"Health facilities fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des établissements de santé: {exc}"
            if lang == "fr"
            else f"Health facilities fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=_API_NAME_HEALTH_FACILITIES,
        api_url=RURAL_HEALTH_FACILITIES_FS_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Transport / 511 (Plan 06)
# ---------------------------------------------------------------------------

_NOT_CONFIGURED_MSG_EN = (
    "Manitoba 511 API key not set. "
    "Obtain a free developer key: sign up at https://www.manitoba511.ca/my511/register "
    "then request an API key, and set the MANITOBA_511_KEY environment variable."
)
_NOT_CONFIGURED_MSG_FR = (
    "Clé API Manitoba 511 non configurée. "
    "Obtenez une clé gratuite: inscrivez-vous à https://www.manitoba511.ca/my511/register "
    "puis demandez une clé API et définissez la variable d'environnement MANITOBA_511_KEY."
)


@tool
async def manitoba_get_road_events(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current road events (closures, construction, incidents) from Manitoba 511 API v3.

    Use for: Checking active road events on Manitoba highways — closures, construction zones, accidents, and other incidents from the Manitoba 511 Events endpoint. Requires MANITOBA_511_KEY environment variable (free developer key from https://www.manitoba511.ca/my511/register). Returns NOT_CONFIGURED error with registration instructions if key is absent. NOTE: Never calls ArcGIS FeatureServer — 511 is a custom REST API.

    Keywords: manitoba road events closures construction incidents highway 511 transport traffic accidents closures PTH Trans-Canada real-time current road conditions
    """
    try:
        rows, cached = await _client.fetch_road_events(lang=lang)
    except Five11NotConfigured:
        msg = _NOT_CONFIGURED_MSG_FR if lang == "fr" else _NOT_CONFIGURED_MSG_EN
        return make_error("NOT_CONFIGURED", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des événements routiers: {exc}"
            if lang == "fr"
            else f"Road events fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=_API_NAME_511,
        api_url=f"{FIVE11_BASE_URL}/events",
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_winter_road_conditions(
    area_name: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get winter road conditions on Manitoba's remote winter road network (seasonal).

    Use for: Checking current conditions on Manitoba's seasonal winter roads — surface condition (Good/Fair/Poor), visibility, and polyline route data. Highest seasonal value for access to northern and remote communities (Island Lake, Berens River, etc.) when ice roads are open. Requires MANITOBA_511_KEY environment variable (free developer key). Optional area_name filters by AreaName field (e.g. 'Northern'). Returns empty list outside winter road season — this is normal. Returns NOT_CONFIGURED error if MANITOBA_511_KEY is absent.

    Keywords: manitoba winter roads seasonal ice roads northern remote communities condition visibility snow drifting PTH 511 winter driving January February March
    """
    try:
        rows, cached = await _client.fetch_winter_road_conditions(
            area_name=area_name,
            lang=lang,
        )
    except Five11NotConfigured:
        msg = _NOT_CONFIGURED_MSG_FR if lang == "fr" else _NOT_CONFIGURED_MSG_EN
        return make_error("NOT_CONFIGURED", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des conditions des routes d'hiver: {exc}"
            if lang == "fr"
            else f"Winter road conditions fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=_API_NAME_511,
        api_url=f"{FIVE11_BASE_URL}/winterroads",
        cached=cached,
        lang=lang,
    )


@tool
async def manitoba_get_traffic_cameras(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Manitoba highway traffic camera locations and snapshot image URLs.

    Use for: Retrieving Manitoba 511 traffic camera locations and live snapshot URLs. Each camera includes Location, coordinates, and a Views array with directional snapshot image URLs (North/South/East/West). Camera locations are stable — cached 24h. Requires MANITOBA_511_KEY environment variable (free developer key from https://www.manitoba511.ca/my511/register). Returns NOT_CONFIGURED error if key is absent. NOTE: Never calls ArcGIS FeatureServer — 511 is a custom REST API.

    Keywords: manitoba traffic cameras 511 highway webcam snapshot images live view road conditions visual Perimeter Highway Trans-Canada PTH camera URL image
    """
    try:
        rows, cached = await _client.fetch_traffic_cameras(lang=lang)
    except Five11NotConfigured:
        msg = _NOT_CONFIGURED_MSG_FR if lang == "fr" else _NOT_CONFIGURED_MSG_EN
        return make_error("NOT_CONFIGURED", msg, lang=lang)
    except Exception as exc:
        msg = (
            f"Erreur lors du chargement des caméras de trafic: {exc}"
            if lang == "fr"
            else f"Traffic cameras fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=_API_NAME_511,
        api_url=f"{FIVE11_BASE_URL}/cameras",
        cached=cached,
        lang=lang,
    )
