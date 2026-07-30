"""New Brunswick module tools — @tool functions for the MCP server.

Every tool:
  - Uses standalone `@tool` from fastmcp.tools (NEVER @mcp.tool)
  - Accepts lang: Literal["en", "fr"] = "en"
  - Returns make_response() on success / make_error() on failure via @upstream_guard
  - Has a docstring with a first line, `Use for:` and a single-line `Keywords:`
  - Uses the `nb_` prefix

Task 1 tracer — nb_get_crown_land. Task 2 adds the five federal-CKAN discovery
tools, scoped server-side to the NB organization (D-01). Task 3 adds the two
gnb.socrata.com discovery tools (checkpoint option-a). Plans 04-06 add the
remaining curated tools.
"""

from __future__ import annotations

import difflib
from typing import Any, Literal

from fastmcp.tools import tool

from mcp_canada.shared import socrata  # noqa: F401 — used by nb_search_gnb_socrata_datasets
from mcp_canada.shared.envelope import make_error, make_response, upstream_guard
from mcp_canada.shared.errors import InvalidInput, NotFound

from . import client as _client
from .constants import (
    ALL_NB_TOOL_NAMES,
    CKAN_BASE_URL,
    CONTAMINATED_SITES_SERVICE,
    CROWN_LAND_SERVICE,
    FILTER_REQUIRED_TOOLS,
    FLOOD_HAZARD_SERVICE,
    GEONB_BASE_URL,
    GNB_SOCRATA_DOMAIN,
    HISTORICAL_FLOODS_SERVICE,
    MAX_RECORDS,
    WETLANDS_SERVICE,
)

_API_NAME_GEONB = "new-brunswick-geonb"
_API_NAME_CKAN = "new-brunswick-federal-ckan"
_API_NAME_SOCRATA = "new-brunswick-gnb-socrata"

_CKAN_SEARCH_URL = f"{CKAN_BASE_URL}/action/package_search"
_CKAN_SHOW_URL = f"{CKAN_BASE_URL}/action/package_show"

# The module's locked tool-name registry — always identical to
# constants.ALL_NB_TOOL_NAMES (the single authoritative manifest, D-08/D-25).
# Cross-checked against it in tests/test_all_nb_tool_names_manifest so the two
# files can never silently drift as Plans 04-06 add the remaining tools.
ALL_NB_TOOLS: tuple[str, ...] = ALL_NB_TOOL_NAMES

__all__ = [
    "nb_get_crown_land",
    "nb_search_datasets",
    "nb_get_dataset_details",
    "nb_query_dataset",
    "nb_list_organizations",
    "nb_list_categories",
    "nb_search_gnb_socrata_datasets",
    "nb_query_gnb_socrata_dataset",
    "nb_list_geonb_services",
    "nb_get_geonb_service_layers",
    "nb_query_geonb_layer",
    "nb_get_flood_hazard_areas",
    "nb_get_historical_floods",
    "nb_get_wetlands",
    "nb_get_contaminated_sites",
]


# ---------------------------------------------------------------------------
# Crown Land — Task 1 tracer
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_crown_land(
    holder: int | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick Crown Land parcels from GeoNB (geonb.snb.ca), layer 3.

    Use for: retrieving Crown Land parcel records administered by NB Natural
    Resources — holder codes, parcel geometry area/length — from the live
    GeoNB_DNR_Crown_Land ArcGIS Server MapServer. NOTE: `holder` is a raw
    integer holder code with no server-exposed name domain — it is NOT a
    person or organization name; use it only if you already have the code
    from a prior result.

    Keywords: new brunswick crown land parcel holder geonb dnr natural resources provincial forestry tenure arcgis mapserver crown
    """
    payload, cached = await _client.fetch_crown_land(holder=holder, limit=limit)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=CROWN_LAND_SERVICE,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Federal CKAN discovery, scoped server-side to the NB organization — Task 2, D-01
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_CKAN)
async def nb_search_datasets(
    query: str = "",
    extra_fq: str | None = None,
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search New Brunswick's federal-CKAN catalogue (open.canada.ca, 221 datasets).

    Use for: discovering Government of New Brunswick open datasets by keyword. Results
    are restricted server-side to the NB publishing organization and this CANNOT be
    widened — there is no organization parameter to override the New Brunswick filter
    (T-21-04). Optional
    extra_fq ANDs an additional CKAN filter-query fragment onto the NB clause (e.g.
    "res_format:CSV"); the NB clause always stays first.

    Keywords: new brunswick nouveau-brunswick gnb open data catalogue dataset search discover ckan federal portal bilingual provincial
    """
    payload, cached = await _client.fetch_search_datasets(
        query=query, extra_fq=extra_fq, limit=limit, offset=offset, lang=lang
    )
    return make_response(
        {**payload, "limit": limit, "offset": offset},
        api_name=_API_NAME_CKAN,
        api_url=_CKAN_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_CKAN)
async def nb_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get full metadata for a single New Brunswick federal-CKAN dataset by id or name slug.

    Use for: retrieving complete metadata for a specific NB dataset — resources (format,
    name, url), license, publication date, maintainer, frequency and spatial extent.
    French titles and notes are returned when the CKAN record carries them (D-12); when
    the id does not exist, close-name suggestions are included in the error.

    Keywords: new brunswick nouveau-brunswick gnb dataset details metadata resources license bilingual ckan federal portal provincial
    """
    try:
        payload, cached = await _client.fetch_dataset_details(dataset_id, lang=lang)
    except NotFound:
        suggestions: list[str] = []
        try:
            search_payload, _ = await _client.fetch_search_datasets(
                query=dataset_id, limit=20, lang=lang
            )
            names = [
                r.get("name") for r in search_payload.get("results", []) if r.get("name")
            ]
            suggestions = difflib.get_close_matches(dataset_id, names, n=5, cutoff=0.4)
        except Exception:
            suggestions = []
        msg = (
            f"Ensemble de données introuvable : {dataset_id}"
            if lang == "fr"
            else f"Dataset not found: {dataset_id}"
        )
        return make_error("NOT_FOUND", msg, lang=lang, suggestions=suggestions)
    return make_response(
        payload,
        api_name=_API_NAME_CKAN,
        api_url=_CKAN_SHOW_URL,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_CKAN)
async def nb_query_dataset(
    dataset_id: str,
    resource_index: int = 0,
    limit: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query/parse a resource from a New Brunswick federal-CKAN dataset by resource index.

    Use for: pulling actual rows out of a CSV, XLSX, XLS, JSON or GeoJSON NB resource.
    A resource in a format this server cannot parse (PDF, ZIP, KML, SHP, ...) returns a
    metadata-only success naming the download url — never an error. An out-of-range
    resource_index returns INVALID_INPUT naming the valid range.

    Keywords: new brunswick nouveau-brunswick gnb query dataset resource csv xlsx json geojson download rows ckan federal
    """
    try:
        payload, cached = await _client.fetch_query_dataset(
            dataset_id, resource_index=resource_index, limit=limit, lang=lang
        )
    except InvalidInput as exc:
        valid_range: str | None = None
        try:
            details_payload, _ = await _client.fetch_dataset_details(dataset_id, lang=lang)
            num_resources = len(details_payload.get("resources") or [])
            valid_range = f"0-{num_resources - 1}" if num_resources else "no resources available"
        except Exception:
            valid_range = None
        msg = (
            f"Index de ressource invalide : {exc}"
            if lang == "fr"
            else f"Invalid resource index: {exc}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid_range=valid_range)
    return make_response(
        payload,
        api_name=_API_NAME_CKAN,
        api_url=_CKAN_SHOW_URL,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_CKAN)
async def nb_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List New Brunswick's publishing organization and sections on the federal-CKAN catalogue.

    Use for: seeing how NB's catalogue is sliced by publishing department. NB publishes
    under a single federal CKAN publishing organization — the useful decomposition
    is the publishing section (org_section), which is empty on most packages.

    Keywords: new brunswick nouveau-brunswick gnb organizations publishers departments sections ckan federal portal provincial catalogue
    """
    payload, cached = await _client.fetch_organizations(lang=lang)
    return make_response(
        {"organizations": payload},
        api_name=_API_NAME_CKAN,
        api_url=_CKAN_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_CKAN)
async def nb_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List New Brunswick's dataset subject, topic and format facets on the federal-CKAN catalogue.

    Use for: seeing how NB's catalogue is sliced by subject/topic/format. NB packages
    carry an empty CKAN groups array — subject, topic_category and res_format facets are
    returned instead of a group listing (do not expect a groups-based category tool).

    Keywords: new brunswick nouveau-brunswick gnb categories subjects topics formats facets ckan federal portal provincial catalogue
    """
    payload, cached = await _client.fetch_categories(lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_CKAN,
        api_url=_CKAN_SEARCH_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# gnb.socrata.com discovery — Task 3, checkpoint option-a
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_SOCRATA)
async def nb_search_gnb_socrata_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Search New Brunswick's provincial Socrata portal (gnb.socrata.com, 312 datasets, keyless).

    Use for: discovering New Brunswick provincial open datasets published directly on
    gnb.socrata.com — a separate catalogue from the federal-CKAN discovery tools
    (nb_search_datasets). No X-App-Token is sent; keyless reads are verified working.

    Keywords: new brunswick nouveau-brunswick gnb socrata provincial portal open data catalogue search discover keyless dataset
    """
    payload, cached = await _client.fetch_gnb_socrata_search(
        query=query, limit=limit, offset=offset
    )
    return make_response(
        payload,
        api_name=_API_NAME_SOCRATA,
        api_url=f"https://{GNB_SOCRATA_DOMAIN}/api/catalog/v1",
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_SOCRATA)
async def nb_query_gnb_socrata_dataset(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    limit: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query a New Brunswick gnb.socrata.com dataset via SoQL against /resource/{id}.json.

    Use for: fetching actual rows from a gnb.socrata.com dataset (find dataset_id via
    nb_search_gnb_socrata_datasets). A limit above this module's record cap returns
    INVALID_INPUT before any network call. Geometry columns are stripped by default
    when select is not provided (Nova Scotia precedent). No X-App-Token is sent.

    Keywords: new brunswick nouveau-brunswick gnb socrata provincial soql query dataset resource where select filter portal
    """
    try:
        payload, cached = await _client.fetch_gnb_socrata_query(
            dataset_id, where=where, select=select, limit=limit
        )
    except InvalidInput as exc:
        msg = f"Limite invalide : {exc}" if lang == "fr" else f"Invalid limit: {exc}"
        return make_error("INVALID_INPUT", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_SOCRATA,
        api_url=f"https://{GNB_SOCRATA_DOMAIN}/resource/{dataset_id}.json",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# GeoNB discovery — Task 1, D-06 (stands in for the 401-ing Hub Search API)
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_list_geonb_services(
    query: str = "",
    include_excluded: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """List GeoNB's ArcGIS Server services via a live REST-directory walk.

    Use for: discovering which of GeoNB's ~62 map services exist before querying
    a layer. GeoNB has no ArcGIS Hub Search API in front of it — the Hub at
    geonb-snb.opendata.arcgis.com returns HTTP 401 — so this tool walks the bare
    ArcGIS Server REST directory instead. The 5 basemap tile services and the
    retired GeoNB_DNR_WildlifeRefuges placeholder are hidden by default; pass
    include_excluded=True to see them, each carrying an exclusion_reason. Each
    entry names its curated_tool when a dedicated nb_get_* tool already covers it.

    Keywords: new brunswick geonb services directory discover list map arcgis server catalogue enumeration rest walk
    """
    services, cached = await _client.fetch_geonb_services(
        query=query, include_excluded=include_excluded
    )
    return make_response(
        {"services": services, "count": len(services)},
        api_name=_API_NAME_GEONB,
        api_url=GEONB_BASE_URL,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_geonb_service_layers(
    service_name: str,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get the layers/tables of a single GeoNB ArcGIS Server service, with
    each layer's live record count and real field names.

    Use for: finding a service's real layer ids before querying it — GeoNB
    layer ids are NOT guessable and do not always start at 0. Worked example:
    GeoNB_DNR_Crown_Land has exactly one layer and its id is 3, not 0 (layer 0
    does not exist on that service). Find service_name via
    nb_list_geonb_services first.

    Keywords: new brunswick geonb service layers fields record count discover layer id mapserver arcgis metadata schema worked example
    """
    try:
        payload, cached = await _client.fetch_geonb_service_layers(service_name)
    except NotFound as exc:
        msg = (
            f"Service GeoNB introuvable : {exc}"
            if lang == "fr"
            else f"GeoNB service not found: {exc}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=f"{GEONB_BASE_URL}/{service_name}/MapServer",
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_query_geonb_layer(
    service_name: str,
    layer_id: int,
    where: str | None = None,
    out_fields: str = "*",
    limit: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Query any GeoNB layer by service name and layer id — the long-tail
    escape hatch that keeps every un-curated GeoNB service reachable.

    Use for: reaching any of GeoNB's un-curated services — including the
    equivalents of nb_get_provincial_parks and nb_get_mineral_occurrences,
    which are not dedicated tools. Find service_name via nb_list_geonb_services
    and layer_id via nb_get_geonb_service_layers. The where argument reaches
    ArcGIS's own SQL-92 parser directly — that parser is the trust boundary
    for this tool, exactly as on every other ArcGIS-backed province (york_region,
    alberta, manitoba, saskatchewan). This is a read-only public server with no
    write surface.

    Keywords: new brunswick geonb query layer where clause sql arcgis mapserver escape hatch generic feature service uncurated long tail
    """
    try:
        payload, cached = await _client.fetch_geonb_layer_features(
            service_name,
            layer_id,
            where=where,
            out_fields=out_fields,
            limit=limit,
            include_geometry=include_geometry,
        )
    except NotFound as exc:
        msg = (
            f"Service GeoNB introuvable : {exc}"
            if lang == "fr"
            else f"GeoNB service not found: {exc}"
        )
        return make_error("NOT_FOUND", msg, lang=lang)
    except InvalidInput as exc:
        msg = f"Limite invalide : {exc}" if lang == "fr" else f"Invalid limit: {exc}"
        return make_error("INVALID_INPUT", msg, lang=lang)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=f"{GEONB_BASE_URL}/{service_name}/MapServer/{layer_id}/query",
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Flood — hazard index and historical flood limits (Task 2)
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_flood_hazard_areas(
    sheet: str | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick flood hazard index polygons from GeoNB
    (GeoNB_ENV_FloodHazardIndex, layer 0).

    Use for: New Brunswick's signature open-data domain — mapped flood hazard
    classification along the Saint John River and other NB waterways. This is
    a mapped hazard classification, NOT a live river gauge reading. The
    technical and sheet fields identify the authoritative source map sheet an
    agent should cite alongside any result.

    Keywords: new brunswick flood hazard inundation saint john river historical high water geospatial risk mapping sheet classification
    """
    payload, cached = await _client.fetch_flood_hazard_areas(sheet=sheet, limit=limit)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=FLOOD_HAZARD_SERVICE,
        cached=cached,
        lang=lang,
    )


_HISTORICAL_FLOOD_EVENTS: tuple[str, ...] = ("2008", "2018", "1973")


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_historical_floods(
    event: str | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick's recorded historical flood limits from GeoNB
    (GeoNB_ENV_Historical_Floods).

    Use for: retrieving mapped historical high-water extents on the Saint John
    River and other NB waterways — the 2008/2018 flood limits by default,
    or the separately-mapped 1973 event via event="1973". event accepts
    "2008", "2018" or "1973"; any other value is rejected.

    Keywords: new brunswick historical flood limits saint john river high water 1973 2008 2018 inundation geospatial extent recorded
    """
    if event is not None and event not in _HISTORICAL_FLOOD_EVENTS:
        msg = (
            f"Événement invalide : {event!r}. Valeurs valides : {list(_HISTORICAL_FLOOD_EVENTS)}"
            if lang == "fr"
            else f"Invalid event: {event!r}. Valid values: {list(_HISTORICAL_FLOOD_EVENTS)}"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=list(_HISTORICAL_FLOOD_EVENTS))
    try:
        payload, cached = await _client.fetch_historical_floods(event=event, limit=limit)
    except InvalidInput as exc:
        msg = f"Événement invalide : {exc}" if lang == "fr" else f"Invalid event: {exc}"
        return make_error("INVALID_INPUT", msg, lang=lang, valid=list(_HISTORICAL_FLOOD_EVENTS))
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=HISTORICAL_FLOODS_SERVICE,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Water — wetlands (filter-required) and contaminated sites (Task 3)
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_wetlands(
    wetland_class: str | None = None,
    status: str | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick wetland polygons from GeoNB (GeoNB_ENV_Wetlands, layer 2).

    Use for: retrieving mapped wetlands (Provincially Significant Wetlands and
    their 30m buffers) filtered by class or status. At least one of
    wetland_class or status is REQUIRED — this layer holds 163,206 rows and an
    unfiltered call is rejected with INVALID_INPUT before any network request.

    Keywords: new brunswick wetlands psw provincially significant wetland bog marsh swamp fen environment geospatial buffer class status filter required
    """
    if "nb_get_wetlands" in FILTER_REQUIRED_TOOLS and not wetland_class and not status:
        msg = (
            "nb_get_wetlands exige au moins un des paramètres wetland_class ou "
            "status (la couche compte 163 206 lignes)."
            if lang == "fr"
            else "nb_get_wetlands requires at least one of wetland_class or "
            "status (the layer has 163,206 rows)."
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=["wetland_class", "status"])
    try:
        payload, cached = await _client.fetch_wetlands(
            wetland_class=wetland_class, status=status, limit=limit
        )
    except InvalidInput as exc:
        msg = f"Paramètre invalide : {exc}" if lang == "fr" else f"Invalid input: {exc}"
        return make_error("INVALID_INPUT", msg, lang=lang, valid=["wetland_class", "status"])
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=WETLANDS_SERVICE,
        cached=cached,
        lang=lang,
    )


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_contaminated_sites(
    status: str | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick contaminated site points from GeoNB
    (GeoNB_ELG_Contaminated_Sites, layer 0).

    Use for: retrieving mapped contaminated site locations and their status.
    Status text is published in both official languages: Status_E carries the
    English status text and Status_F carries the French status text — both
    are always returned regardless of which field status filters against.

    Keywords: new brunswick contaminated sites environment remediation status bilingual elg property identifier file open date cleanup
    """
    payload, cached = await _client.fetch_contaminated_sites(status=status, limit=limit)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=CONTAMINATED_SITES_SERVICE,
        cached=cached,
        lang=lang,
    )


