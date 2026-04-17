"""Alberta tools — 24 @tool stubs across 6 domains.

All bodies `raise NotImplementedError` in this Wave 0 scaffold; Plans 02-07 fill
bodies. Docstrings (Use for: + Keywords:) are already in place so downstream
plans never need to change the signatures — only the bodies.

Domain coverage:
  - Discovery (Plan 02 — 5 tools): alberta_search_datasets, alberta_get_dataset_details,
    alberta_query_dataset, alberta_list_organizations, alberta_list_categories
  - AER / energy (Plan 03 — 4 tools): alberta_get_well_licences_today, _archive,
    alberta_get_pipeline_statistics, alberta_get_production_volumes
  - Wildfire (Plan 04 — 4 tools): alberta_get_active_fires, _perimeters, _bans,
    _control_orders
  - Health (Plan 05 — 3 tools): alberta_get_hospitals, alberta_get_ahs_zones,
    alberta_get_health_facilities
  - Transport / 511 (Plan 06 — 3 tools): alberta_get_road_events,
    alberta_get_winter_road_conditions, alberta_get_traffic_cameras
  - Environment / agriculture / demographics / parks (Plan 07 — 5 tools):
    alberta_get_air_quality_stations, alberta_get_water_advisories,
    alberta_get_crop_production, alberta_get_population_estimates,
    alberta_get_provincial_parks

Every tool:
  - Uses standalone `@tool` from `fastmcp.tools` (NEVER `@mcp.tool`)
  - Accepts `lang: Literal["en", "fr"] = "en"`
  - Returns `make_response()` on success / `make_error()` on failure (Plans 02-07 fill bodies)
  - Has `Use for:` + single-line `Keywords:` (8+ keywords) in docstring for BM25
"""

from typing import Any, Literal

import httpx  # noqa: F401 — used by Plans 02-07 for UPSTREAM_ERROR branches
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response  # noqa: F401 — used by Plans 02-07

from . import client as _client  # noqa: F401 — used by Plans 02-07

# Import constants used by Plans 02-07 for api_url in make_response envelopes.
from .constants import (  # noqa: F401
    ACTIVE_FIRE_PERIMETERS_FS_URL,
    ACTIVE_WILDFIRES_FS_URL,
    AER_ST1_DAILY_BASE,
    AER_ST1_MONTHLY_BASE,
    AER_ST3_BASE,
    AER_ST39_BASE,
    AHS_EMS_FS_URL,
    AHS_HOSPITALS_FS_URL,
    AHS_ZONE_FS_URL,
    AQHI_AIR_LAYER_URL,
    CKAN_BASE_URL,
    EXTINGUISHED_PERIMETERS_FS_URL,
    FIRE_BAN_SYSTEM_FS_URL,
    FIRE_CONTROL_ORDERS_FS_URL,
    FIVE11_BASE_URL,
    FOREST_AREA_FS_URL,
    OHV_RESTRICTION_FS_URL,
    PCN_CLINICS_FS_URL,
    PROVINCIAL_PARKS_FS_URL,
    RIVER_FORECAST_FS_URL,
    ST3_PRODUCTS,
)


# Source identifiers for the _meta envelope
API_NAME_CKAN = "alberta-open-data"
API_NAME_WMB = "alberta-wmb-arcgis"
API_NAME_AHS = "alberta-ahs-arcgis"
API_NAME_GEODISCOVER = "alberta-geodiscover"
API_NAME_AER = "alberta-aer-static"
API_NAME_511 = "alberta-511"


__all__ = [
    # Discovery (Plan 02)
    "alberta_search_datasets",
    "alberta_get_dataset_details",
    "alberta_query_dataset",
    "alberta_list_organizations",
    "alberta_list_categories",
    # AER / energy (Plan 03)
    "alberta_get_well_licences_today",
    "alberta_get_well_licences_archive",
    "alberta_get_pipeline_statistics",
    "alberta_get_production_volumes",
    # Wildfire (Plan 04)
    "alberta_get_active_fires",
    "alberta_get_fire_perimeters",
    "alberta_get_fire_bans",
    "alberta_get_fire_control_orders",
    # Health (Plan 05)
    "alberta_get_hospitals",
    "alberta_get_ahs_zones",
    "alberta_get_health_facilities",
    # Transport / 511 (Plan 06)
    "alberta_get_road_events",
    "alberta_get_winter_road_conditions",
    "alberta_get_traffic_cameras",
    # Environment / agriculture / demographics / parks (Plan 07)
    "alberta_get_air_quality_stations",
    "alberta_get_water_advisories",
    "alberta_get_crop_production",
    "alberta_get_population_estimates",
    "alberta_get_provincial_parks",
]


# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


@tool
async def alberta_search_datasets(
    q: str = "",
    organization: str | None = None,
    format: str | None = None,
    rows: int = 10,
    start: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets).

    Use for: Discovering Alberta provincial datasets across 370 organizations including current ministries, historical predecessor ministries, and Crown corporations. NOTE: 86% of Alberta CKAN is PDF reports — pass format='CSV' or format='ESRI REST' or format='XLSX' for machine-readable data. For water licence registry data (87MB+ active, 169MB inactive), use this tool with format='CSV' AND specific organization filter — never call alberta_query_dataset on full water-licence resources without row limits.

    Keywords: alberta open data search ckan datasets discovery catalogue dataset_search find browse query provincial
    """
    try:
        payload, cached = await _client.fetch_search_datasets(
            q=q,
            organization=organization,
            format=format,
            rows=rows,
            start=start,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête CKAN: {exc}"
            if lang == "fr"
            else f"CKAN search failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    # Convert Pydantic summaries to plain dicts for JSON serialisation
    results_dicts = [r.model_dump() for r in payload.get("results", [])]
    data = {"count": payload.get("count", 0), "results": results_dicts}
    return make_response(
        data=data,
        api_name=API_NAME_CKAN,
        api_url=CKAN_BASE_URL + "package_search",
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_dataset_details(
    package_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full details (resources + curated extras) for a specific Alberta CKAN dataset.

    Use for: Inspecting an Alberta CKAN dataset's resources, formats, and curated extras (isopen, language, frequencyofupdate, creator). Hides 50+ publication-identifier extras (identifier-AGDEX-number, identifier-ISBN-pdf, audience, etc.) — see Pitfall 11. Pass the dataset `name` (slug) returned by alberta_search_datasets.

    Keywords: alberta dataset details package_show ckan resources inspect metadata description extras slug
    """
    if not package_id or not package_id.strip():
        msg = (
            "package_id est requis"
            if lang == "fr"
            else "package_id is required"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        details, cached = await _client.fetch_dataset_details(package_id.strip())
    except httpx.HTTPStatusError:
        msg = (
            f"Jeu de données introuvable: {package_id}"
            if lang == "fr"
            else f"Dataset not found: {package_id}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    return make_response(
        data=details.model_dump(),
        api_name=API_NAME_CKAN,
        api_url=CKAN_BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_query_dataset(
    package_id: str,
    resource_index: int = 0,
    where: str | None = None,
    max_records: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a dataset's resource — auto-routes by format (ESRI REST -> ArcGIS query, CSV/XLSX/JSON -> file parse, others -> metadata only).

    Use for: Fetching parsed rows from any Alberta CKAN dataset. Picks resources[resource_index] (default 0); when format is ESRI REST and URL contains /FeatureServer, queries the FeatureServer with optional WHERE clause; when format is CSV/XLSX/JSON/GeoJSON/XLS, downloads and parses the file. Returns metadata-only for PDF/ZIP/KML/WMS resources. Caveat: very large CSVs (e.g., water-licence-data: 87MB) — pass max_records or filter via where.

    Keywords: alberta query dataset resource fetch parse esri rest featureserver csv xlsx geojson router auto-detect
    """
    if not package_id or not package_id.strip():
        msg = "package_id est requis" if lang == "fr" else "package_id is required"
        return make_error("INVALID_INPUT", msg, lang=lang)
    if resource_index < 0:
        msg = (
            "resource_index doit être >= 0"
            if lang == "fr"
            else "resource_index must be >= 0"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        payload, cached = await _client.fetch_query_dataset(
            package_id=package_id.strip(),
            resource_index=resource_index,
            where=where,
            max_records=max(1, min(max_records, 5000)),
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur lors de la requête: {exc}"
            if lang == "fr"
            else f"Query failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:  # parser errors, arcgis errors
        msg = (
            f"Erreur inattendue: {exc}"
            if lang == "fr"
            else f"Unexpected error: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=API_NAME_CKAN,
        api_url=payload.get("url", CKAN_BASE_URL),
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List all 370 organizations publishing on open.alberta.ca CKAN.

    Use for: Discovering Alberta CKAN organization slugs for use as organization= parameter in alberta_search_datasets. Includes ~30 current ministries, ~150 historical/predecessor ministries (e.g., agriculturefoodandruraldevelopment1992-2006), Crown corporations, and advisory committees. Most queries should pass a current ministry slug to focus results.

    Keywords: alberta organizations ministries list orgs federated historical crown corp ministry slug catalog provincial
    """
    try:
        orgs, cached = await _client.fetch_organizations()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur CKAN: {exc}"
            if lang == "fr"
            else f"CKAN organization_list failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[o.model_dump() for o in orgs],
        api_name=API_NAME_CKAN,
        api_url=CKAN_BASE_URL + "organization_list",
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List dataset format categories from Alberta CKAN's res_format facet.

    Use for: Discovering what file formats Alberta CKAN datasets are published in (PDF=28763, CSV=224, XLSX=774, ESRI REST=93, etc.). Alberta CKAN does NOT use the standard CKAN groups feature — group_list returns []. This tool uses res_format facet instead, returning format buckets sorted by count.

    Keywords: alberta categories formats catalog facets list browse classification taxonomy types res_format
    """
    try:
        cats, cached = await _client.fetch_format_categories()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Erreur CKAN: {exc}"
            if lang == "fr"
            else f"CKAN facet search failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[c.model_dump() for c in cats],
        api_name=API_NAME_CKAN,
        api_url=CKAN_BASE_URL + "package_search",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# AER / energy (Plan 03)
# ---------------------------------------------------------------------------


@tool
async def alberta_get_well_licences_today(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get today's AER well licences from ST1 daily report (TXT, rotates Mon-Sun).

    Use for: Daily snapshot of newly-issued or modified Alberta well licences from the Alberta Energy Regulator (AER). The ST1 daily TXT is overwritten by day-of-week — running this tool always returns today's data, regardless of date. For historical data, use alberta_get_well_licences_archive.

    Keywords: alberta well licences AER ST1 daily wells oil gas energy regulator licence operator today
    """
    try:
        rows, cached = await _client.fetch_well_licences_today()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec du téléchargement ST1 : {exc}"
            if lang == "fr"
            else f"AER ST1 daily fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=API_NAME_AER,
        api_url=AER_ST1_DAILY_BASE,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_well_licences_archive(
    year: int,
    month: int,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get monthly archive ZIP URL for AER ST1 well licences (discovery-only — large fixed-width files).

    Use for: Looking up the AER ST1 monthly archive ZIP URL for a specific year/month. Returns metadata only (URL, year, month) — agents must download externally. Auto-parsing is disabled because fixed-width TXT contents per ZIP can be very large.

    Keywords: alberta well licences AER ST1 monthly archive ZIP historical wells oil gas regulator year
    """
    if month < 1 or month > 12:
        msg = (
            "Mois invalide : doit être entre 1 et 12"
            if lang == "fr"
            else "Invalid month: must be between 1 and 12"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        payload, cached = await _client.fetch_well_licences_archive(year, month)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la recherche de l'archive ST1 : {exc}"
            if lang == "fr"
            else f"AER ST1 archive lookup failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=payload,
        api_name=API_NAME_AER,
        api_url=AER_ST1_MONTHLY_BASE,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_pipeline_statistics(
    year: int,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get annual AER ST39 pipeline statistics XLSX (length by substance, year-by-year).

    Use for: Pipeline-network statistics for Alberta — total pipeline length, distribution by substance (oil, gas, water disposal, etc.), and operator counts. Multi-sheet XLSX flattened into rows. Pass year (e.g., 2024) — confirmed working for recent years; older XLS files (pre-2010) may use different sheet structure.

    Keywords: alberta pipelines AER ST39 statistics infrastructure oil gas substance length operator annual
    """
    if year < 1960 or year > 2100:
        msg = (
            f"Année invalide : {year} (doit être entre 1960 et 2100)"
            if lang == "fr"
            else f"Invalid year: {year} (must be between 1960 and 2100)"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        rows, cached = await _client.fetch_pipeline_statistics(year)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec du téléchargement ST39-{year} : {exc}"
            if lang == "fr"
            else f"AER ST39-{year} fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=API_NAME_AER,
        api_url=f"{AER_ST39_BASE}/ST39-{year}.xls",
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_production_volumes(
    product: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get monthly oil/gas production volumes from AER ST3 (current month, 7 products).

    Use for: Monthly Alberta production volumes from the Alberta Energy Regulator (AER) ST3 report. Valid products: Butane, Ethane, NGL, Oil, Gas, Propane, Sulphur (case-sensitive — Bitumen is included in Oil; CrudeOil is also in Oil). Returns rows from the latest XLSX (always current month). For historical data per year, use alberta_query_dataset with the AER static URL pattern.

    Keywords: alberta production volumes AER ST3 monthly oil gas butane ethane propane sulphur NGL energy
    """
    if product not in ST3_PRODUCTS:
        msg = (
            f"Produit invalide. Valides : {', '.join(ST3_PRODUCTS)}"
            if lang == "fr"
            else f"Invalid product. Valid: {', '.join(ST3_PRODUCTS)}"
        )
        return make_error(
            "INVALID_INPUT",
            msg,
            lang=lang,
            valid=list(ST3_PRODUCTS),
        )
    try:
        rows, cached = await _client.fetch_production_volumes(product)
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec du téléchargement ST3 {product} : {exc}"
            if lang == "fr"
            else f"AER ST3 {product} fetch failed: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=API_NAME_AER,
        api_url=f"{AER_ST3_BASE}/{product}_current.xlsx",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Wildfire (Plan 04)
# ---------------------------------------------------------------------------


@tool
async def alberta_get_active_fires(
    status: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current active Alberta wildfires from WMBappServices ArcGIS Online (5-min refresh).

    Use for: Live wildfire status during fire season (May-October). Optional status= filter ('Out of Control', 'Being Held', 'Under Control'). Returns up to 5000 features with FIRE_NUMBER, FIRE_STATUS, AREA_ESTIMATE, GENERAL_CAUSE, RESP_AREA, LATITUDE, LONGITUDE. Pass include_geometry=true for polygon outlines (use alberta_get_fire_perimeters instead for cleaner polygon data). For historical fires (2006-2025), use alberta_query_dataset with the wildfire-data CKAN package.

    Keywords: alberta wildfire fires active wmb arcgis live status incident emergency forestry season
    """
    try:
        data, cached = await _client.fetch_active_fires(
            status=status,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête WMBappServices : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"WMBappServices query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=data,
        api_name=API_NAME_WMB,
        api_url=ACTIVE_WILDFIRES_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_fire_perimeters(
    status: Literal["active", "extinguished"] = "active",
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta wildfire perimeters (active or extinguished) from WMBappServices simplified views.

    Use for: Fire boundary polygons during or after a wildfire. status='active' returns currently-burning perimeters (5-min refresh); status='extinguished' returns historical extinguished perimeters (24h cache). Pass include_geometry=true for polygon coordinates. Active perimeters are the simplified polygon view (smoother edges than full ESRI dataset).

    Keywords: alberta wildfire perimeter polygon fire boundary area wmb arcgis active extinguished historical map
    """
    if status not in ("active", "extinguished"):
        msg = (
            f"Statut invalide : '{status}'"
            if lang == "fr"
            else f"Invalid status: '{status}'"
        )
        return make_error(
            "INVALID_INPUT",
            msg,
            lang=lang,
            valid=["active", "extinguished"],
        )
    try:
        data, cached = await _client.fetch_fire_perimeters(
            status=status,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête WMBappServices : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"WMBappServices query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    api_url = (
        ACTIVE_FIRE_PERIMETERS_FS_URL
        if status == "active"
        else EXTINGUISHED_PERIMETERS_FS_URL
    )
    return make_response(
        data=data,
        api_name=API_NAME_WMB,
        api_url=api_url,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_fire_bans(
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current province-wide Alberta fire ban registry from WMBappServices.

    Use for: Checking active fire bans, fire restrictions, and OFRA (off-road vehicle restriction areas) — the same data backing the public albertafirebans.ca dashboard. Use during fire season for travel/camping advisories. Refreshed every 5 minutes by source.

    Keywords: alberta fire bans restrictions advisory wmb wildfire ban OHV camping travel forestry season
    """
    try:
        data, cached = await _client.fetch_fire_bans(
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête WMBappServices : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"WMBappServices query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=data,
        api_name=API_NAME_WMB,
        api_url=FIRE_BAN_SYSTEM_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_fire_control_orders(
    category: Literal["fire_control", "ohv_restriction", "forest_area"] = "fire_control",
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta fire control orders, OHV restrictions, or forest area boundaries from WMBappServices.

    Use for: Operational fire-suppression context — fire control orders (closures and restrictions issued during active fires), OHV vehicle restriction areas, and the 10 Alberta Forest Areas (Calgary, Rocky Mountain House, Edson, Whitecourt, Slave Lake, Lac La Biche, Fort McMurray, Peace River, Grande Prairie, High Level). category='forest_area' is static reference data (24h cache); others are LIVE (5-min cache).

    Keywords: alberta fire control orders OHV restrictions forest area boundary wmb operational closures advisory
    """
    valid_categories = ["fire_control", "ohv_restriction", "forest_area"]
    if category not in valid_categories:
        msg = (
            f"Catégorie invalide : '{category}'"
            if lang == "fr"
            else f"Invalid category: '{category}'"
        )
        return make_error(
            "INVALID_INPUT",
            msg,
            lang=lang,
            valid=valid_categories,
        )
    try:
        data, cached = await _client.fetch_fire_control_orders(
            category=category,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête WMBappServices : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"WMBappServices query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    url_by_category = {
        "fire_control": FIRE_CONTROL_ORDERS_FS_URL,
        "ohv_restriction": OHV_RESTRICTION_FS_URL,
        "forest_area": FOREST_AREA_FS_URL,
    }
    return make_response(
        data=data,
        api_name=API_NAME_WMB,
        api_url=url_by_category[category],
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Health (Plan 05)
# ---------------------------------------------------------------------------


@tool
async def alberta_get_hospitals(
    zone: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta hospitals from AHSGIS AHS_Hospitals FeatureServer (~101 hospitals).

    Use for: Alberta hospital locations, addresses, phone numbers, postal codes, and capability flags (IP=inpatient services, ED=emergency department). Optional zone= performs a case-insensitive substring match on the Location field (e.g., zone='Calgary' returns Calgary-area hospitals) — no polygon containment. For zone boundaries with population stats, use alberta_get_ahs_zones.

    Keywords: alberta hospitals AHS AHSGIS arcgis health facility inpatient emergency department zone address calgary edmonton
    """
    try:
        data, cached = await _client.fetch_hospitals(
            zone=zone,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête AHSGIS : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"AHSGIS query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=data,
        api_name=API_NAME_AHS,
        api_url=AHS_HOSPITALS_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_ahs_zones(
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get 5 Alberta Health Services (AHS) zones with boundaries and historical population.

    Use for: AHS administrative zones — South, Calgary, Central, Edmonton, North. Each zone includes name, ID, and census population (pop_2006, pop_2011, pop_2016). Pass include_geometry=true for zone boundary polygons. These are the zones referenced by every AHS facility record.

    Keywords: alberta AHS zones health services boundary administrative South Calgary Central Edmonton North population census
    """
    try:
        data, cached = await _client.fetch_ahs_zones(
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête AHSGIS : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"AHSGIS query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=data,
        api_name=API_NAME_AHS,
        api_url=AHS_ZONE_FS_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def alberta_get_health_facilities(
    facility_type: Literal["ems", "pcn_clinic"],
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta health facilities from AHSGIS — EMS stations or PCN clinics (dispatched by facility_type).

    Use for: Non-hospital Alberta health facilities. facility_type='ems' returns EMS (Emergency Medical Services) stations; facility_type='pcn_clinic' returns PCN (Primary Care Network) clinics. For hospitals, use alberta_get_hospitals. For zones, use alberta_get_ahs_zones. NOTE: ER wait times are NOT exposed by AHS in machine-readable form (Pitfall 9 — AHS publishes via the web widget at albertahealthservices.ca/Webapps/WaitTimes/ only); this tool does NOT include wait-time data.

    Keywords: alberta health facilities EMS ambulance PCN primary care clinic walk-in AHS AHSGIS dispatch zone emergency
    """
    valid_types = ["ems", "pcn_clinic"]
    if facility_type not in valid_types:
        msg = (
            "Type d'installation invalide"
            if lang == "fr"
            else "Invalid facility_type"
        )
        return make_error(
            "INVALID_INPUT",
            msg,
            lang=lang,
            valid=valid_types,
        )
    try:
        data, cached = await _client.fetch_health_facilities(
            facility_type=facility_type,
            max_records=max_records,
            include_geometry=include_geometry,
        )
    except httpx.HTTPStatusError as exc:
        msg = (
            f"Échec de la requête AHSGIS : HTTP {exc.response.status_code}"
            if lang == "fr"
            else f"AHSGIS query failed: HTTP {exc.response.status_code}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    api_url = AHS_EMS_FS_URL if facility_type == "ems" else PCN_CLINICS_FS_URL
    return make_response(
        data=data,
        api_name=API_NAME_AHS,
        api_url=api_url,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Transport / 511 (Plan 06)
# ---------------------------------------------------------------------------


@tool
async def alberta_get_road_events(
    event_type: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta road events (closures, construction, incidents, accidents) from 511 Alberta API.

    Use for: Province-wide active road events on Alberta's highway network — includes full closures, partial closures, construction zones, incidents, and accidents. Optional event_type= filter (e.g., 'closures', 'construction', 'incidents', 'accidents'). Each event includes location (lat/lon), roadway name, description, and reporting timestamp.

    Keywords: alberta road events 511 closures construction incidents accidents highway travel advisory
    """
    raise NotImplementedError("Plan 06 implements")


@tool
async def alberta_get_winter_road_conditions(
    area_name: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta winter road conditions from 511 Alberta winterroads endpoint.

    Use for: Mountain passes, prairies, and highway segments during winter season. Optional area_name= substring filter on the AreaName field (e.g., area_name='Calgary' returns Calgary-region roads). Returns primary condition, secondary conditions, visibility, and encoded polyline for each segment.

    Keywords: alberta winter road conditions 511 visibility prairies mountain highway snow ice travel
    """
    raise NotImplementedError("Plan 06 implements")


@tool
async def alberta_get_traffic_cameras(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta traffic camera locations + live snapshot URLs from 511 Alberta cameras endpoint.

    Use for: Locating Alberta traffic cameras (~376 total) with location names, coordinates, and current snapshot image URLs. Each camera entry includes a `views` array of snapshot URLs (multi-directional cameras have several views). Cache 24h — camera locations are stable.

    Keywords: alberta traffic cameras 511 live snapshot views highway webcam monitoring locations
    """
    raise NotImplementedError("Plan 06 implements")


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks (Plan 07)
# ---------------------------------------------------------------------------


@tool
async def alberta_get_air_quality_stations(
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get 75 Alberta AQHI air quality monitoring stations with current pollutant readings.

    Use for: Alberta air quality monitoring station network from GeoDiscover Alberta. Each station includes current readings for SO2, H2S, TRS, O3, NOX, NO, NO2, NH3, CO, PM2.5, THC, NMHC, CH4, PAH, C2H4, BTEX, and Calib. Updated every 5 minutes. For AQHI index values, use the per-station readings.

    Keywords: alberta air quality AQHI monitoring stations pollutant ozone nitrogen dioxide PM2.5 environment readings
    """
    raise NotImplementedError("Plan 07 implements")


@tool
async def alberta_get_water_advisories(
    advisory_type: Literal["river", "water_management", "drought", "ice_cover", "water_sharing"],
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta water advisories from GeoDiscover River Forecast Centre — dispatched by advisory_type.

    Use for: Provincial water-management advisories — river forecast advisories (drought, ice cover, water sharing). advisory_type='river' returns river forecast advisories; 'water_management' returns water management advisories; 'drought' returns drought stages; 'ice_cover' returns river ice cover; 'water_sharing' returns water sharing agreements. Each is a different layer in the same FeatureServer.

    Keywords: alberta water advisory river forecast drought ice cover sharing environment management hydro flood
    """
    raise NotImplementedError("Plan 07 implements")


@tool
async def alberta_get_crop_production(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get historical Alberta major crop production from open.alberta.ca CKAN (Alberta Official Statistic).

    Use for: Historical statistics on major Alberta crops (wheat, canola, barley, etc.) — area seeded, area harvested, production tonnes, yield. Covers 2000-2014. NOTE: This dataset is updated infrequently — for in-season weekly crop reports, search via alberta_search_datasets (those reports are PDF on the Agriculture and Irrigation ministry website).

    Keywords: alberta crop production agriculture historical wheat canola barley yield harvest farm statistics CKAN
    """
    raise NotImplementedError("Plan 07 implements")


@tool
async def alberta_get_population_estimates(
    breakdown: Literal[
        "csd", "quarterly", "annual", "age_sex", "sub_provincial", "components_of_growth"
    ] = "csd",
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Alberta population estimates by breakdown — defaults to Census Subdivision (CSD) municipal level.

    Use for: Alberta-specific population data complementing StatCan (which provides CMA-level only). breakdown='csd' (default) returns municipal/Census Subdivision estimates; 'quarterly' returns quarterly provincial; 'annual' returns annual provincial 1921-current; 'age_sex' returns by age and sex; 'sub_provincial' returns sub-provincial regions; 'components_of_growth' returns birth/death/migration components. NO duplicate with StatCan — Alberta provides CSD-level municipal data; StatCan provides CMA-level only.

    Keywords: alberta population estimates census subdivision CSD municipal quarterly annual age sex statistics demographics
    """
    raise NotImplementedError("Plan 07 implements")


@tool
async def alberta_get_provincial_parks(
    max_records: int = 5000,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get all Alberta provincial parks and protected areas from GeoDiscover boundary FeatureServer.

    Use for: Alberta Parks network — provincial parks, wildland parks, ecological reserves, natural areas, recreation areas. Includes park name, designation, area in hectares, and centroid lat/lon. Pass include_geometry=true for boundary polygons. Cache 24h — park boundaries are stable.

    Keywords: alberta parks provincial protected areas wildland ecological reserve recreation natural area boundary geodiscover
    """
    raise NotImplementedError("Plan 07 implements")
