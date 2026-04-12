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
from .constants import AQ_INDEX_URL, BASE_URL

# Source identifier for the _meta envelope
API_NAME = "donnees-quebec"

__all__ = [
    "quebec_search_datasets",
    "quebec_get_dataset_details",
    "quebec_query_dataset",
    "quebec_list_organizations",
    "quebec_list_categories",
    "quebec_get_health_installations",
    "quebec_get_er_wait_times",
    "quebec_get_population_by_municipality",
    "quebec_get_road_conditions",
    "quebec_get_road_works",
    "quebec_get_road_events",
    "quebec_get_bridge_structures",
    "quebec_get_forest_fires_history",
    "quebec_get_air_quality_stations",
    "quebec_get_air_quality_index",
    "quebec_get_water_quality_monitoring",
    "quebec_get_electricity_data",
    "quebec_get_protected_areas",
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


# ---------------------------------------------------------------------------
# Health / MSSS curated tools — Plan 03
# ---------------------------------------------------------------------------

_VALID_INSTAL_TYPES = ("CLSC", "CHSGS", "CHSLD", "CHPSY")
_MTQ_WFS_API_URL = "https://ws.mapserver.transports.gouv.qc.ca/swtq"
_MAMH_CSV_URL = "https://donneesouvertes.affmunqc.net/repertoire/MUN.csv"


@tool
async def quebec_get_health_installations(
    instal_type: str | None = None,
    rss_name: str | None = None,
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Quebec health installations (hospitals, CLSCs, CHSLDs, psychiatric) from MSSS datastore.

    Use for: Finding MSSS health facilities by type (CLSC/CHSGS/CHSLD/CHPSY) or health region (RSS); covers 1,592 installations across Quebec.
    Keywords: quebec, health, hospital, clsc, chsld, chpsy, installations, msss, sante, etablissement, medical, facilities

    instal_type: One of CLSC (community clinic), CHSGS (hospital), CHSLD (long-term care), CHPSY (psychiatric). Omit for all types.
    rss_name: Health region (RSS) name filter (French, e.g. "Montréal", "Capitale-Nationale").
    """
    if instal_type is not None and instal_type.upper() not in _VALID_INSTAL_TYPES:
        msg = (
            f"Invalid instal_type. Valid: {', '.join(_VALID_INSTAL_TYPES)}"
            if lang == "en"
            else f"instal_type invalide. Valides: {', '.join(_VALID_INSTAL_TYPES)}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=list(_VALID_INSTAL_TYPES))
    try:
        rows, cached = await _client.fetch_health_installations(
            instal_type=instal_type.upper() if instal_type else None,
            rss_name=rss_name,
            limit=min(max(limit, 1), 2000),
        )
    except httpx.HTTPStatusError as exc:
        msg = f"MSSS datastore error: {exc}" if lang == "en" else f"Erreur datastore MSSS: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=BASE_URL + "datastore_search",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_er_wait_times(
    installation: str | None = None,
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current Quebec emergency room wait times and stretcher occupancy (hourly refresh from MSSS).

    Use for: Checking real-time ER congestion, stretcher occupancy, patients waiting 24h/48h at any Quebec hospital; 116 EDs updated hourly.
    Keywords: quebec, emergency, er, wait times, urgence, hospital, civieres, msss, real-time, stretchers, occupancy, temps attente

    installation: Full-text search on installation name (e.g. "Rimouski", "Sainte-Justine").
    """
    try:
        rows, cached = await _client.fetch_er_wait_times(
            installation=installation,
            limit=min(max(limit, 1), 500),
        )
    except httpx.HTTPStatusError as exc:
        msg = f"Upstream error: {exc}" if lang == "en" else f"Erreur: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=BASE_URL + "datastore_search",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_population_by_municipality(
    region: str | None = None,
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Quebec municipality population, area, and administrative region from the MAMH municipal registry.

    Use for: Municipal demographics across Quebec's 1,282 municipalities — includes population, area, MRC, admin region, mayor name.
    Keywords: quebec, population, municipalities, municipalites, mamh, demographics, regions, mrc, registry, census, repertoire, villages

    region: Administrative region code (e.g. "06" for Montreal, "03" for Capitale-Nationale).
    """
    try:
        rows, cached = await _client.fetch_population_by_municipality(
            region=region,
            limit=min(max(limit, 1), 2000),
        )
    except Exception as exc:
        msg = f"Upstream error: {exc}" if lang == "en" else f"Erreur: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=_MAMH_CSV_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Transport / MTQ curated tools — Plan 03
# ---------------------------------------------------------------------------


@tool
async def quebec_get_road_conditions(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current Quebec winter road conditions (pavement state, visibility) from MTQ WFS.

    Use for: Winter driving safety — current pavement status, visibility, snow presence across Quebec's road network. Returns bilingual columns based on lang.
    Keywords: quebec, road conditions, winter, mtq, pavement, visibility, driving, conditions routieres, hiver, transports, snow, neige

    Note: Winter-season data. May return empty list in summer. WFS endpoint confirmed working (phase 16-05 gap closure fixed a parser dispatch bug that previously masked this).
    """
    try:
        rows, cached = await _client.fetch_road_conditions(lang=lang)
    except Exception as exc:
        msg = f"MTQ WFS error: {exc}" if lang == "en" else f"Erreur WFS MTQ: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=API_NAME,
        api_url=_MTQ_WFS_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_road_works(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current Quebec road construction zones and work sites from MTQ live WFS CSV.

    Use for: Active construction zones, road closures, lane restrictions on Quebec provincial roads; continuous updates. Returns bilingual descriptions based on lang.
    Keywords: quebec, road works, construction, chantiers, mtq, detours, closures, lanes, travaux routiers, transports, zones, infrastructure

    Note: Live data, ~5min cache. Returns both French and English description columns via the `description` field selected by lang.
    """
    try:
        rows, cached = await _client.fetch_road_works(lang=lang)
    except Exception as exc:
        msg = f"MTQ WFS error: {exc}" if lang == "en" else f"Erreur WFS MTQ: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=_MTQ_WFS_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_road_events(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current Quebec road events (accidents, incidents, warnings) from MTQ live WFS CSV.

    Use for: Real-time road events affecting traffic — accidents, incidents, temporary warnings across Quebec provincial roads. French-only fields.
    Keywords: quebec, road events, accidents, incidents, warnings, mtq, evenements, traffic, avertissements, routiers, transports, live

    Note: Fields are French-only (no English equivalent in MTQ CSV). `lang` parameter affects error messages only.
    """
    try:
        rows, cached = await _client.fetch_road_events()
    except Exception as exc:
        msg = f"MTQ WFS error: {exc}" if lang == "en" else f"Erreur WFS MTQ: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=_MTQ_WFS_API_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_bridge_structures(
    route: str | None = None,
    municipality: str | None = None,
    region: str | None = None,
    limit: int = 100,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get Quebec bridge, culvert, tunnel, and retaining wall inventory from MTQ structure registry.

    Use for: Bridge and structure inventory — 50K+ structures statewide. Returns location, year, type, dimensions. REQUIRES at least one filter (route/municipality/region).
    Keywords: quebec, bridges, culverts, tunnels, structures, mtq, ponts, infrastructure, inventory, engineering, walls, civil

    Note: At least one of `route`, `municipality`, or `region` is required to avoid unbounded response. Mimics the BC water wells filter guard pattern.
    """
    if not any([route, municipality, region]):
        msg = (
            "quebec_get_bridge_structures requires at least one of route, municipality, or region "
            "to avoid returning the full 50K+ structure inventory"
            if lang == "en"
            else "quebec_get_bridge_structures nécessite au moins un des paramètres route, "
            "municipality ou region pour éviter de retourner l'inventaire complet de 50K+ structures"
        )
        return make_error("INVALID_INPUT", msg, lang=lang)
    try:
        rows, cached = await _client.fetch_bridge_structures(
            route=route,
            municipality=municipality,
            region=region,
            limit=min(max(limit, 1), 1000),
        )
    except Exception as exc:
        msg = f"MTQ WFS error: {exc}" if lang == "en" else f"Erreur WFS MTQ: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=_MTQ_WFS_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Environment / Demographics / Energy — Plan 04
# ---------------------------------------------------------------------------


@tool
async def quebec_get_forest_fires_history(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get the MFFP/MRN historical forest fire archive metadata and download URLs from Données Québec.

    Use for: Discovering the historical Quebec forest fire perimeter archive — returns metadata and download links for SHP/GPKG files (external download required for geometric data). Not a live SOPFEU feed.
    Keywords: quebec, forest fires, feux foret, mffp, mrn, historical, perimeters, wildfire, archive, incendies, shapefile, download, ressources naturelles

    Note: The underlying data is SHP/GPKG format only — not directly parseable via query tools.
    Download URLs are provided in the resources list. For real-time active fire data, visit sopfeu.qc.ca directly.
    """
    try:
        metadata, cached = await _client.fetch_forest_fires_history()
    except httpx.HTTPStatusError as exc:
        msg = (
            f"CKAN error fetching forest fires dataset: {exc}"
            if lang == "en"
            else f"Erreur CKAN pour le jeu de données feux de forêt: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=metadata,
        api_name=API_NAME,
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_air_quality_stations(
    active_only: bool = True,
    limit: int = 500,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get the RSQAQ air quality monitoring station network across Quebec (MELCCFP).

    Use for: Locating Quebec air quality stations by municipality, region, or environment type (urban/rural/industrial); 245 total stations including historical closed stations.
    Keywords: quebec, air quality, rsqaq, stations, monitoring, melccfp, pollution, qualite air, environnement, surveillance, network, reseau, atmospheric

    active_only: When True (default), returns only stations without a closure date. Set False for all 245 including historical stations.
    """
    try:
        rows, cached = await _client.fetch_air_quality_stations(
            active_only=active_only,
            limit=min(max(limit, 1), 1000),
        )
    except httpx.HTTPStatusError as exc:
        msg = f"Upstream error: {exc}" if lang == "en" else f"Erreur: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=[r.model_dump() for r in rows],
        api_name=API_NAME,
        api_url=BASE_URL + "datastore_search",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_air_quality_index(
    limit: int = 200,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get current Quebec air quality index (IQA) readings from the MELCCFP ArcGIS FeatureServer.

    Use for: Real-time air quality index readings across Quebec monitoring stations; includes IQA score, cote (rating), pollutant levels, station location.
    Keywords: quebec, air quality index, iqa, melccfp, rsqaq, real-time, pollution, air quality, indice qualite air, arcgis, monitoring, atmosphere, pm25, ozone

    Note: Data is sourced from ArcGIS REST FeatureServer, not CKAN datastore. Hourly refresh.
    """
    try:
        measurements, cached = await _client.fetch_air_quality_index(
            limit=min(max(limit, 1), 500),
        )
    except httpx.HTTPStatusError as exc:
        msg = f"ArcGIS error: {exc}" if lang == "en" else f"Erreur ArcGIS: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    except Exception as exc:
        msg = f"Unexpected error: {exc}" if lang == "en" else f"Erreur inattendue: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=measurements,
        api_name=API_NAME,
        api_url=AQ_INDEX_URL,
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_water_quality_monitoring(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get the MELCCFP physicochemical water quality monitoring dataset metadata and download URLs.

    Use for: Discovering Quebec river and fleuve water quality data — returns metadata and download links for GeoJSON/ZIP archives (external download required); covers physicochemical monitoring of rivers and the St. Lawrence.
    Keywords: quebec, water quality, rivers, fleuve, melccfp, physicochemical, monitoring, qualite eau, rivieres, st-lawrence, physicochimique, download, environnement

    Note: The underlying data is GeoJSON ZIP format — not directly parseable via this tool.
    Download URLs are in the resources list for external processing.
    """
    try:
        metadata, cached = await _client.fetch_water_quality_monitoring()
    except httpx.HTTPStatusError as exc:
        msg = f"CKAN error: {exc}" if lang == "en" else f"Erreur CKAN: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=metadata,
        api_name=API_NAME,
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_electricity_data(
    limit: int = 500,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get historical Quebec electricity production and consumption data from Hydro-Québec (via Données Québec CSV).

    Use for: Historical electricity generation and consumption statistics for Quebec — annual production/consumption totals by source, published by Hydro-Québec on Données Québec.
    Keywords: quebec, electricity, hydro-quebec, production, consommation, energy, power, energie, historique, generation, kwh, twh, renewable, electricite

    Note: This is historical production/consumption data — NOT current outage data.
    For current power outages, visit hydroquebec.com/pannes/ directly.
    """
    try:
        rows, cached = await _client.fetch_electricity_data(
            limit=min(max(limit, 1), 5000),
        )
    except Exception as exc:
        msg = (
            f"Error fetching electricity data: {exc}"
            if lang == "en"
            else f"Erreur lors de la récupération des données électriques: {exc}"
        )
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=rows,
        api_name=API_NAME,
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )


@tool
async def quebec_get_protected_areas(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get the MELCCFP protected areas registry (Registre des aires protégées) metadata and download URLs.

    Use for: Discovering Quebec protected areas — national parks, wildlife reserves, ecological areas; returns metadata and download links for SHP/GPKG/FGDB archives (~10K+ protected areas).
    Keywords: quebec, protected areas, aires protegees, melccfp, sepaq, parks, wildlife, reserves, ecological, parc national, biodiversity, conservation, download

    Note: The underlying data is SHP/GPKG/FGDB format only — not directly parseable via query tools.
    Download URLs are in the resources list for external GIS processing.
    """
    try:
        metadata, cached = await _client.fetch_protected_areas()
    except httpx.HTTPStatusError as exc:
        msg = f"CKAN error: {exc}" if lang == "en" else f"Erreur CKAN: {exc}"
        return make_error("UPSTREAM_ERROR", msg, lang=lang)
    return make_response(
        data=metadata,
        api_name=API_NAME,
        api_url=BASE_URL + "package_show",
        cached=cached,
        lang=lang,
    )
