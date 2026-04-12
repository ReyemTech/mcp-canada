"""Quebec module client — async functions returning (data, was_cached) tuples.

Plans 02/03/04 implement the bodies:
  - Plan 02: _api_get, _datastore_get, fetch_search_datasets, fetch_dataset_details,
             fetch_organizations, fetch_categories, fetch_query_dataset
  - Plan 03: fetch_health_installations, fetch_er_wait_times,
             fetch_population_by_municipality, fetch_road_conditions, fetch_road_works,
             fetch_road_events, fetch_bridge_structures
  - Plan 04: fetch_forest_fires_history, fetch_air_quality_stations,
             fetch_air_quality_index, fetch_water_quality_monitoring,
             fetch_electricity_data, fetch_protected_areas

CRITICAL (Phase 15 lesson — _api_get MUST follow this contract):
  shared.http.api_get returns a PARSED dict — NOT an httpx.Response.
  NEVER call .raise_for_status() or .json() on the return value.
  Pattern (post-15-05 fix):
    envelope = await api_get(url, params or {}, headers=DEFAULT_HEADERS)
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise httpx.HTTPStatusError(...)
    return envelope.get("result", {})
"""

from __future__ import annotations

from typing import Any

import httpx

from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    AQ_INDEX_URL,
    BASE_URL,
    CACHE_TTL_ACTIVE,
    CACHE_TTL_DAILY,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    DEFAULT_HEADERS,
    MAMH_MUN_CSV_URL,
    MSSS_ER_RESOURCE_ID,
    MSSS_INSTALLATIONS_RESOURCE_ID,
    MTQ_BRIDGES_URL,
    MTQ_ROAD_CONDITIONS_URL,
    MTQ_ROAD_EVENTS_URL,
    MTQ_ROAD_WORKS_URL,
    RATE_GROUP,
    RATE_LIMIT,
    RSQAQ_STATIONS_RESOURCE_ID,
)
from .schemas import (
    QuebecAirQualityStation,
    QuebecBridgeStructure,
    QuebecCategory,
    QuebecDatasetDetails,
    QuebecDatasetSummary,
    QuebecErWaitRow,
    QuebecHealthInstallation,
    QuebecOrganization,
    QuebecPopulationRow,
    QuebecResource,
    QuebecRoadEvent,
    QuebecRoadWork,
)

__all__ = [
    "_api_get",
    "_datastore_get",
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_organizations",
    "fetch_categories",
    "fetch_query_dataset",
    "fetch_health_installations",
    "fetch_er_wait_times",
    "fetch_population_by_municipality",
    "fetch_road_conditions",
    "fetch_road_works",
    "fetch_road_events",
    "fetch_bridge_structures",
    "fetch_forest_fires_history",
    "fetch_air_quality_stations",
    "fetch_air_quality_index",
    "fetch_water_quality_monitoring",
    "fetch_electricity_data",
    "fetch_protected_areas",
]

_limiter = get_limiter(RATE_GROUP, RATE_LIMIT)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Quebec CKAN envelope unwrap helper.

    CRITICAL: shared api_get already returns PARSED JSON (dict). NEVER call
    .raise_for_status() or .json() on the return value. This is the Phase 15 fix
    (see debug/resolved/bc-api-get-dict-mismatch.md).

    Args:
        path: Action API path (e.g. "package_search") relative to BASE_URL.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN result field (dict for package_search/package_show,
        list for organization_list/group_list/tag_list).

    Raises:
        httpx.HTTPStatusError: When CKAN returns success=False or api_get returns non-dict.
    """
    url = BASE_URL + path
    await _limiter.acquire()
    envelope = await api_get(url, params or {}, headers=DEFAULT_HEADERS)
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise httpx.HTTPStatusError(
            f"CKAN returned success=False for {path}",
            request=httpx.Request("GET", url),
            response=httpx.Response(500),
        )
    return envelope.get("result", {})


async def _datastore_get(
    resource_id: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Datastore search helper.

    Wraps CKAN datastore_search — returns the unwrapped `result` dict with
    `records`, `total`, and `fields`.
    """
    all_params = {"resource_id": resource_id, **(params or {})}
    return await _api_get("datastore_search", all_params)


def _flatten_dataset_summary(raw: dict[str, Any]) -> QuebecDatasetSummary:
    org = raw.get("organization") or {}
    return QuebecDatasetSummary(
        id=raw.get("id", ""),
        name=raw.get("name", ""),
        title=raw.get("title", ""),
        notes=raw.get("notes"),
        organization_slug=org.get("name") if isinstance(org, dict) else None,
        organization_title=org.get("title") if isinstance(org, dict) else None,
        groups=[
            str(g.get("name"))
            for g in (raw.get("groups") or [])
            if isinstance(g, dict) and g.get("name")
        ],
        license_id=raw.get("license_id"),
        update_frequency=raw.get("update_frequency"),
        num_resources=int(raw.get("num_resources") or 0),
        num_tags=int(raw.get("num_tags") or 0),
    )


def _flatten_resource(raw: dict[str, Any]) -> QuebecResource:
    return QuebecResource(
        id=raw.get("id", ""),
        name=raw.get("name"),
        format=raw.get("format"),
        url=raw.get("url", ""),
        datastore_active=bool(raw.get("datastore_active") or False),
        size=raw.get("size"),
    )


# ---------------------------------------------------------------------------
# Discovery client functions — Plan 02
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    q: str = "",
    rows: int = 10,
    start: int = 0,
    organization: str | None = None,
    group: str | None = None,
) -> tuple[list[QuebecDatasetSummary], bool]:
    """Search Données Québec CKAN catalogue (1,593 datasets, 139 orgs)."""
    cache_key = f"quebec:search:{q}:{rows}:{start}:{organization}:{group}"

    async def _fetch() -> list[QuebecDatasetSummary]:
        fq_parts: list[str] = []
        if organization:
            fq_parts.append(f"organization:{organization}")
        if group:
            fq_parts.append(f"groups:{group}")
        p: dict[str, Any] = {"q": q, "rows": rows, "start": start}
        if fq_parts:
            p["fq"] = " ".join(fq_parts)
        result = await _api_get("package_search", p)
        return [_flatten_dataset_summary(r) for r in (result.get("results") or [])]

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_dataset_details(package_id: str) -> tuple[QuebecDatasetDetails, bool]:
    """Get full dataset details including resources list and datastore_active flags."""
    cache_key = f"quebec:dataset:{package_id}"

    async def _fetch() -> QuebecDatasetDetails:
        raw = await _api_get("package_show", {"id": package_id})
        org = raw.get("organization") or {}
        return QuebecDatasetDetails(
            id=raw.get("id", ""),
            name=raw.get("name", ""),
            title=raw.get("title", ""),
            notes=raw.get("notes"),
            organization_slug=org.get("name") if isinstance(org, dict) else None,
            organization_title=org.get("title") if isinstance(org, dict) else None,
            update_frequency=raw.get("update_frequency"),
            license_id=raw.get("license_id"),
            resources=[_flatten_resource(r) for r in (raw.get("resources") or [])],
        )

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_organizations() -> tuple[list[QuebecOrganization], bool]:
    """Get all Données Québec organizations (139 orgs in federated catalogue)."""
    cache_key = "quebec:orgs"

    async def _fetch() -> list[QuebecOrganization]:
        result = await _api_get("organization_list", {"all_fields": True})
        if not isinstance(result, list):
            return []
        return [
            QuebecOrganization(
                name=r.get("name", ""),
                title=r.get("title") or r.get("display_name") or r.get("name", ""),
                package_count=int(r.get("package_count") or 0),
            )
            for r in result
        ]

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_categories() -> tuple[list[QuebecCategory], bool]:
    """Get 10 thematic groups via group_list.

    Phase 16 lesson: DQ has 10 meaningful thematic groups (unlike BC which
    returns HTTP 403 on group_list). Uses group_list NOT tag_list (tag_list
    returns ~4,200 noisy tags).
    """
    cache_key = "quebec:categories"

    async def _fetch() -> list[QuebecCategory]:
        result = await _api_get("group_list", {"all_fields": True})
        if not isinstance(result, list):
            return []
        return [
            QuebecCategory(
                name=r.get("name", ""),
                title=r.get("title"),
                display_name=r.get("display_name"),
                package_count=int(r.get("package_count") or 0),
            )
            for r in result
        ]

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# Format priority for picking best resource: lower = better
_FORMAT_PRIORITY = {"CSV": 0, "GEOJSON": 1, "JSON": 2, "XLSX": 3, "XLS": 4}


def _pick_best_resource(resources: list[QuebecResource]) -> QuebecResource | None:
    """Pick the best downloadable resource by format priority (CSV > GeoJSON > JSON > XLSX)."""
    scored = [
        (_FORMAT_PRIORITY.get((r.format or "").upper(), 99), r)
        for r in resources
        if r.url
    ]
    if not scored:
        return None
    scored.sort(key=lambda t: t[0])
    return scored[0][1]


async def fetch_query_dataset(
    package_id: str,
    limit: int = 100,
) -> tuple[dict[str, Any], bool]:
    """Pick best resource and either datastore_search (when active) or fetch_and_parse."""
    details, _ = await fetch_dataset_details(package_id)
    picked = _pick_best_resource(details.resources)
    if picked is None:
        return ({"records": [], "total": 0, "source": "none"}, False)

    if picked.datastore_active:
        cache_key = f"quebec:query:datastore:{picked.id}:{limit}"

        async def _fetch_ds() -> dict[str, Any]:
            ds = await _datastore_get(picked.id, {"limit": limit})
            return {
                "records": ds.get("records") or [],
                "total": int(ds.get("total") or 0),
                "source": "datastore",
                "resource_id": picked.id,
                "resource_url": picked.url,
            }

        return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch_ds)

    cache_key = f"quebec:query:file:{picked.id}"
    rows, cached = await fetch_and_parse(picked.url, ttl=CACHE_TTL_SEARCH)
    return (
        {
            "records": rows[:limit],
            "total": len(rows),
            "source": "file",
            "resource_id": picked.id,
            "resource_url": picked.url,
            "format": picked.format,
        },
        cached,
    )


# ---------------------------------------------------------------------------
# Health / MSSS — Plan 03
# ---------------------------------------------------------------------------

_INSTAL_TYPE_COLUMN = {
    "CLSC": "CLSC",
    "CHSGS": "CHSGS",
    "CHSLD": "CHSLD",
    "CHPSY": "CHPSY",
}


def _safe_float(v: Any) -> float | None:
    try:
        return float(v) if v not in (None, "", "null") else None
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> int | None:
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _yes_no_to_bool(v: Any) -> bool:
    return str(v).strip().lower() == "oui"


def _flatten_installation(r: dict[str, Any]) -> QuebecHealthInstallation:
    return QuebecHealthInstallation(
        instal_code=r.get("INSTAL_COD"),
        instal_name=r.get("INSTAL_NOM"),
        etab_name=r.get("ETAB_NOM"),
        rss_name=r.get("RSS_NOM"),
        mrc_name=r.get("MRC_NOM"),
        municipality=r.get("MUN_NOM"),
        address=r.get("ADRESSE"),
        postal_code=r.get("CODE_POSTA"),
        latitude=_safe_float(r.get("LATITUDE")),
        longitude=_safe_float(r.get("LONGITUDE")),
        is_clsc=_yes_no_to_bool(r.get("CLSC")),
        is_chsgs=_yes_no_to_bool(r.get("CHSGS")),
        is_chsld=_yes_no_to_bool(r.get("CHSLD")),
        is_chpsy=_yes_no_to_bool(r.get("CHPSY")),
        date_updated=r.get("DATE_MAJ"),
    )


async def fetch_health_installations(
    instal_type: str | None = None,
    rss_name: str | None = None,
    limit: int = 200,
) -> tuple[list[QuebecHealthInstallation], bool]:
    """MSSS health installations via datastore_search.

    instal_type: One of CLSC, CHSGS, CHSLD, CHPSY. None returns all types.
    rss_name: Optional health region (RSS) name filter.
    limit: Max rows (default 200, max 2000).
    """
    cache_key = f"quebec:msss:installations:{instal_type}:{rss_name}:{limit}"

    async def _fetch() -> list[QuebecHealthInstallation]:
        import json

        params: dict[str, Any] = {"limit": limit}
        filters: dict[str, Any] = {}
        if instal_type and instal_type.upper() in _INSTAL_TYPE_COLUMN:
            filters[_INSTAL_TYPE_COLUMN[instal_type.upper()]] = "Oui"
        if rss_name:
            filters["RSS_NOM"] = rss_name
        if filters:
            params["filters"] = json.dumps(filters)
        result = await _datastore_get(MSSS_INSTALLATIONS_RESOURCE_ID, params)
        return [_flatten_installation(r) for r in (result.get("records") or [])]

    return await cached_fetch(cache_key, CACHE_TTL_DAILY, _fetch)


def _flatten_er_row(r: dict[str, Any]) -> QuebecErWaitRow:
    return QuebecErWaitRow(
        establishment=r.get("Nom_etablissement"),
        installation=r.get("Nom_installation"),
        functional_stretchers=_safe_int(r.get("Nombre_de_civieres_fonctionnelles")),
        occupied_stretchers=_safe_int(r.get("Nombre_de_civieres_occupees")),
        patients_over_24h=_safe_int(
            r.get("Nombre_de_patients_sur_civiere_plus_de_24_heures")
        ),
        patients_over_48h=_safe_int(
            r.get("Nombre_de_patients_sur_civiere_plus_de_48_heures")
        ),
        extraction_time=(
            r.get("Heure_de_l'extraction_(image)") or r.get("Heure_de_l_extraction")
        ),
        last_updated=r.get("Mise_a_jour"),
    )


async def fetch_er_wait_times(
    installation: str | None = None,
    limit: int = 200,
) -> tuple[list[QuebecErWaitRow], bool]:
    """MSSS ER hourly situation via datastore_search.

    installation: Full-text search on installation name (e.g. "Rimouski").
    116 rows total (one per hospital ER), updated hourly.
    """
    cache_key = f"quebec:msss:er:{installation}:{limit}"

    async def _fetch() -> list[QuebecErWaitRow]:
        params: dict[str, Any] = {"limit": limit}
        if installation:
            params["q"] = installation
        result = await _datastore_get(MSSS_ER_RESOURCE_ID, params)
        return [_flatten_er_row(r) for r in (result.get("records") or [])]

    return await cached_fetch(cache_key, CACHE_TTL_ACTIVE, _fetch)


def _flatten_population_row(r: dict[str, Any]) -> QuebecPopulationRow:
    return QuebecPopulationRow(
        mcode=r.get("mcode"),
        municipality=r.get("munnom"),
        admin_region=r.get("regadm"),
        mrc=r.get("mrc"),
        population=_safe_int(r.get("mpopul")),
        area_km2=_safe_float(r.get("msuperf")),
        municipal_type=r.get("mcodedesi"),
        mayor=r.get("mayor"),
    )


async def fetch_population_by_municipality(
    region: str | None = None,
    limit: int | None = None,
) -> tuple[list[QuebecPopulationRow], bool]:
    """MAMH municipality registry via fetch_and_parse(MAMH_MUN_CSV_URL).

    1,282 rows. Optional region filter on regadm (administrative region code).
    """
    cache_key = f"quebec:mamh:pop:{region}:{limit}"

    async def _fetch() -> list[QuebecPopulationRow]:
        rows, _ = await fetch_and_parse(MAMH_MUN_CSV_URL, ttl=CACHE_TTL_DAILY)
        out: list[QuebecPopulationRow] = []
        for r in rows:
            if region and str(r.get("regadm", "")).strip() != region.strip():
                continue
            out.append(_flatten_population_row(r))
            if limit is not None and len(out) >= limit:
                break
        return out

    return await cached_fetch(cache_key, CACHE_TTL_DAILY, _fetch)


# ---------------------------------------------------------------------------
# Transport / MTQ — Plan 03
# ---------------------------------------------------------------------------


async def fetch_road_conditions(
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """MTQ winter road conditions via WFS CSV (ms:conditions_routieres).

    Confirmed working — live MTQ WFS endpoint returns ~100KB of CSV with bilingual columns.
    Errors propagate to the @tool layer.
    Bilingual columns: DescriptionEtatChausseeFR/EN, DescriptionVisibiliteFR/EN.
    """
    cache_key = f"quebec:mtq:road_cond:{lang}"

    async def _fetch() -> list[dict[str, Any]]:
        rows, _ = await fetch_and_parse(MTQ_ROAD_CONDITIONS_URL, ttl=CACHE_TTL_ACTIVE)
        desc_col = "DescriptionEtatChausseeFR" if lang == "fr" else "DescriptionEtatChausseeEN"
        vis_col = "DescriptionVisibiliteFR" if lang == "fr" else "DescriptionVisibiliteEN"
        out = []
        for r in rows:
            out.append({
                "segment_id": r.get("NumeroSegment"),
                "route_num": r.get("NumeroRoute"),
                "route_name": r.get("NomRoute"),
                "region": r.get("NomRegion"),
                "pavement_status": r.get(desc_col),
                "visibility": r.get(vis_col),
                "has_snow_presence": r.get("IndicateurPresenceLamesNeige"),
                "timestamp": r.get("DateEtHeureCondition"),
            })
        return out

    return await cached_fetch(cache_key, CACHE_TTL_ACTIVE, _fetch)


def _flatten_road_work(r: dict[str, Any], lang: str) -> QuebecRoadWork:
    desc = r.get("descriptionFrancais") if lang == "fr" else r.get("descriptionAnglais")
    return QuebecRoadWork(
        identifier=r.get("identifiant"),
        chantier_id=r.get("identifiantChantier"),
        route=r.get("routeAutoroute"),
        obstruction_type=r.get("entraveType"),
        start=r.get("debut"),
        end=r.get("fin"),
        updated=r.get("miseAJour"),
        work_description=r.get("identificationDesTravaux"),
        location=r.get("localisation"),
        direction=r.get("direction"),
        description=desc,
    )


async def fetch_road_works(
    lang: str = "en",
) -> tuple[list[QuebecRoadWork], bool]:
    """MTQ active road construction zones via WFS CSV (ms:chantiers_mtmdet).

    Confirmed working. Bilingual: descriptionFrancais / descriptionAnglais.
    """
    cache_key = f"quebec:mtq:road_works:{lang}"

    async def _fetch() -> list[QuebecRoadWork]:
        rows, _ = await fetch_and_parse(MTQ_ROAD_WORKS_URL, ttl=CACHE_TTL_ACTIVE)
        return [_flatten_road_work(r, lang) for r in rows]

    return await cached_fetch(cache_key, CACHE_TTL_ACTIVE, _fetch)


def _flatten_road_event(r: dict[str, Any]) -> QuebecRoadEvent:
    return QuebecRoadEvent(
        identifier=r.get("identifiant"),
        obstruction=r.get("entrave"),
        route=r.get("numeroRoute"),
        location=r.get("localisation"),
        direction=r.get("direction"),
        municipality=r.get("municipalite"),
        duration=r.get("duree"),
        cause=r.get("cause"),
        consequence=r.get("consequence"),
        detour=r.get("detour"),
        regions=r.get("regions"),
        active_since=r.get("enVigueurDepuis"),
    )


async def fetch_road_events() -> tuple[list[QuebecRoadEvent], bool]:
    """MTQ active road events/warnings via WFS CSV (ms:evenements).

    French-only columns in this CSV — no English equivalent available.
    """
    cache_key = "quebec:mtq:road_events"

    async def _fetch() -> list[QuebecRoadEvent]:
        rows, _ = await fetch_and_parse(MTQ_ROAD_EVENTS_URL, ttl=CACHE_TTL_ACTIVE)
        return [_flatten_road_event(r) for r in rows]

    return await cached_fetch(cache_key, CACHE_TTL_ACTIVE, _fetch)


def _flatten_bridge(r: dict[str, Any]) -> QuebecBridgeStructure:
    return QuebecBridgeStructure(
        structure_id=r.get("ide_strct"),
        dossier_num=r.get("num_dossr"),
        year=_safe_int(r.get("val_annee_")),
        status_code=r.get("code_des_s"),
        route_name=r.get("nom_route"),
        obstacle=r.get("nom_obstc"),
        municipality=r.get("nom_muncp"),
        municipality_code=r.get("cod_muncp"),
        structure_name=r.get("nom_strct"),
        route_num=r.get("num_route"),
        latitude=_safe_float(r.get("geo_lattd")),
        longitude=_safe_float(r.get("geo_longt")),
        length=_safe_float(r.get("val_longr")),
        width=_safe_float(r.get("val_largr_")),
        structure_type=r.get("cod_type_s"),
    )


async def fetch_bridge_structures(
    route: str | None = None,
    municipality: str | None = None,
    region: str | None = None,
    limit: int = 100,
) -> tuple[list[QuebecBridgeStructure], bool]:
    """MTQ bridge inventory via WFS CSV (ms:gsq_v_desc_strct_tri).

    ~50K+ structures. At least one filter REQUIRED (enforced in the @tool layer)
    to avoid unbounded response. Post-parse filter since MTQ WFS CSV has no
    server-side filter params.
    """
    cache_key = f"quebec:mtq:bridges:{route}:{municipality}:{region}:{limit}"

    async def _fetch() -> list[QuebecBridgeStructure]:
        rows, _ = await fetch_and_parse(MTQ_BRIDGES_URL, ttl=CACHE_TTL_META)
        out: list[QuebecBridgeStructure] = []
        for r in rows:
            if route and str(r.get("num_route", "")).strip() != route.strip():
                continue
            if municipality and municipality.lower() not in str(
                r.get("nom_muncp", "")
            ).lower():
                continue
            if region and region.lower() not in str(r.get("nom_route", "")).lower():
                continue
            out.append(_flatten_bridge(r))
            if len(out) >= limit:
                break
        return out

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# Environment / Demographics / Energy — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_forest_fires_history() -> tuple[dict[str, Any], bool]:
    """MFFP/MRN forest fire archive metadata (package_show only).

    Returns CKAN package metadata + resource download URLs (SHP/GPKG format only —
    not parseable by fetch_and_parse). This is a metadata/discovery tool.
    Agents should download the SHP/GPKG archives externally for geometric data.
    """
    details, cached = await fetch_dataset_details("feux-de-foret")
    return (details.model_dump(), cached)


async def fetch_air_quality_stations(
    active_only: bool = True,
    limit: int = 500,
) -> tuple[list[QuebecAirQualityStation], bool]:
    """RSQAQ air quality stations via datastore_search.

    245 rows total (active + historical closed stations).
    active_only=True (default) filters out stations where DATE_FERMETURE is not None.
    """
    cache_key = f"quebec:rsqaq:stations:{active_only}:{limit}"

    async def _fetch() -> list[QuebecAirQualityStation]:
        params: dict[str, Any] = {"limit": limit}
        result = await _datastore_get(RSQAQ_STATIONS_RESOURCE_ID, params)
        out: list[QuebecAirQualityStation] = []
        for r in (result.get("records") or []):
            if active_only and r.get("DATE_FERMETURE"):
                continue
            out.append(QuebecAirQualityStation(
                station_id=r.get("ID_STATION"),
                station_name=r.get("NOM_STATION"),
                admin_region=r.get("RA"),
                address=r.get("ADRESSE"),
                municipality=r.get("MUNICIPALITE"),
                milieu_type=r.get("TYPE_MILIEU"),
                date_opened=r.get("DATE_OUVERTURE"),
                date_closed=r.get("DATE_FERMETURE"),
                latitude=_safe_float(r.get("LATITUDE")),
                longitude=_safe_float(r.get("LONGITUDE")),
            ))
        return out

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_air_quality_index(
    limit: int = 200,
) -> tuple[list[dict[str, Any]], bool]:
    """MELCCFP air quality index via ArcGIS REST FeatureServer.

    Source: AQ_INDEX_URL (ArcGIS REST, not CKAN datastore).
    Calls api_get with ?f=json&where=1=1&outFields=*&resultRecordCount={limit}.
    Returns flattened feature list with attributes merged with lat/lon from geometry.
    """
    cache_key = f"quebec:rsqaq:index:{limit}"

    async def _fetch() -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "f": "json",
            "where": "1=1",
            "outFields": "*",
            "resultRecordCount": limit,
        }
        await _limiter.acquire()
        envelope = await api_get(AQ_INDEX_URL, params, headers=DEFAULT_HEADERS)
        if not isinstance(envelope, dict):
            return []
        features = envelope.get("features") or []
        out: list[dict[str, Any]] = []
        for f in features:
            attrs = f.get("attributes") or {}
            geom = f.get("geometry") or {}
            out.append({**attrs, "longitude": geom.get("x"), "latitude": geom.get("y")})
        return out

    return await cached_fetch(cache_key, CACHE_TTL_ACTIVE, _fetch)


async def fetch_water_quality_monitoring() -> tuple[dict[str, Any], bool]:
    """MELCCFP water quality monitoring metadata (package_show only).

    Returns CKAN package metadata + download URLs (GeoJSON ZIP at Azure Blob —
    not directly parseable by fetch_and_parse). Metadata/discovery tool.
    """
    details, cached = await fetch_dataset_details(
        "suivi-physicochimique-des-rivieres-et-du-fleuve"
    )
    return (details.model_dump(), cached)


async def fetch_electricity_data(
    limit: int = 500,
) -> tuple[list[dict[str, Any]], str, bool]:
    """Hydro-Québec historical electricity production/consumption file.

    Picks the first CSV/XLSX/XLS resource (non-empty URL) from the
    historique-production-consommation package and parses it via fetch_and_parse.
    Returns (rows, source_url, was_cached). The Hydro-Québec package publishes
    XLSX files (years 2018-2021) — no CSV resources exist.

    Raises ValueError if no parseable resource is found.

    Note: Current outages are NOT on DQ CKAN — redirect agents to hydroquebec.com/pannes/.
    """
    cache_key = f"quebec:hydro:electricity:v2:{limit}"

    async def _fetch() -> tuple[list[dict[str, Any]], str]:
        details, _ = await fetch_dataset_details("historique-production-consommation")
        file_url: str | None = None
        for r in details.resources:
            fmt = (r.format or "").upper()
            if fmt in ("CSV", "XLSX", "XLS") and r.url:
                file_url = r.url
                break
        if file_url is None:
            raise ValueError(
                "No parseable CSV/XLSX/XLS resource found in "
                "historique-production-consommation package"
            )
        rows, _ = await fetch_and_parse(file_url, ttl=CACHE_TTL_META)
        return rows[:limit], file_url

    bundled, was_cached = await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
    rows, source_url = bundled
    return rows, source_url, was_cached


async def fetch_protected_areas() -> tuple[dict[str, Any], bool]:
    """MELCCFP protected areas metadata (package_show only).

    Returns CKAN package metadata + resource download URLs (SHP/GPKG/FGDB format —
    not parseable by fetch_and_parse). Metadata/discovery tool.
    ~10,000+ protected areas in the Registre des aires protégées et des AMCE.
    """
    details, cached = await fetch_dataset_details("aires-protegees-au-quebec")
    return (details.model_dump(), cached)
