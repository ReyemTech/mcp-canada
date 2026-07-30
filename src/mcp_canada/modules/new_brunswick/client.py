"""New Brunswick module client — async functions returning (data, was_cached) tuples.

Wave 0 (this file) implements: three module-level limiters (federal CKAN, GeoNB,
511) plus a fourth for gnb.socrata.com (checkpoint option-a — a fourth upstream
surface joined the discovery side, Rule 2: rate limiting is a correctness
requirement per CLAUDE.md, not optional), five fully-implemented private
helpers (`_api_get`, `_build_fq`, `_shape_dataset`, `_geonb_query`, `_511_get`),
`fetch_crown_land` (the Task 1 tracer, fully implemented), and every remaining
downstream function as a `raise NotImplementedError` stub with a LOCKED
signature. Plans 02-06 fill bodies only — they never edit a signature here.

  - Plan 02 (federal CKAN + gnb.socrata.com): fetch_search_datasets,
    fetch_dataset_details, fetch_query_dataset, fetch_organizations,
    fetch_categories, fetch_gnb_socrata_search, fetch_gnb_socrata_query
  - Plan 04 (GeoNB discovery + flood/water): fetch_geonb_services,
    fetch_geonb_service_layers, fetch_geonb_layer_features,
    fetch_flood_hazard_areas, fetch_historical_floods, fetch_wetlands,
    fetch_contaminated_sites
  - Plan 05 (parcels/civic address): fetch_parcels, fetch_civic_addresses
  - Plan 06 (health/education + 511): fetch_health_facilities,
    fetch_public_schools, fetch_road_events, fetch_winter_road_conditions,
    fetch_traffic_cameras

CHECKPOINT (option-a): fetch_mineral_occurrences and fetch_provincial_parks
are NOT stubbed here — both dropped to the long tail, reachable through
fetch_geonb_layer_features / nb_query_geonb_layer.
"""

from __future__ import annotations

import os
from typing import Any

from mcp_canada.shared import arcgis_hub
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.errors import UpstreamData
from mcp_canada.shared.http import api_get
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_META,
    CKAN_BASE_URL,
    CROWN_LAND_FIELDS,
    CROWN_LAND_LAYER,
    CROWN_LAND_SERVICE,
    FIVE11_BASE_URL,
    FIVE11_KEY_ENV,
    GNB_SOCRATA_DOMAIN,  # noqa: F401 — used by Plan 02
    MAX_RECORDS,
    NB_ORG_FQ,
    RATE_GROUP_511,
    RATE_GROUP_CKAN,
    RATE_GROUP_GEONB,
    RATE_GROUP_SOCRATA,
    RATE_LIMIT_511,
    RATE_LIMIT_CKAN,
    RATE_LIMIT_GEONB,
    RATE_LIMIT_SOCRATA,
    USER_AGENT,
)

__all__ = [
    # Private helpers (fully implemented in Wave 0)
    "_api_get",
    "_build_fq",
    "_shape_dataset",
    "_geonb_query",
    "_511_get",
    "Five11NotConfigured",
    # Federal CKAN discovery (Plan 02)
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_query_dataset",
    "fetch_organizations",
    "fetch_categories",
    # gnb.socrata.com discovery (Plan 02, checkpoint option-a)
    "fetch_gnb_socrata_search",
    "fetch_gnb_socrata_query",
    # GeoNB discovery + flood/water (Plan 04)
    "fetch_geonb_services",
    "fetch_geonb_service_layers",
    "fetch_geonb_layer_features",
    "fetch_flood_hazard_areas",
    "fetch_historical_floods",
    "fetch_wetlands",
    "fetch_contaminated_sites",
    # Crown land — Task 1 tracer (fully implemented)
    "fetch_crown_land",
    # Parcels / civic address (Plan 05)
    "fetch_parcels",
    "fetch_civic_addresses",
    # Health / education + 511 (Plan 06)
    "fetch_health_facilities",
    "fetch_public_schools",
    "fetch_road_events",
    "fetch_winter_road_conditions",
    "fetch_traffic_cameras",
]


# ---------------------------------------------------------------------------
# Exception for missing 511 key
# ---------------------------------------------------------------------------


class Five11NotConfigured(Exception):
    """Raised when NEW_BRUNSWICK_511_KEY env var is not set.

    The message states only that the env var is unset and links 511.gnb.ca —
    it MUST NOT interpolate the value read from the environment (T-21-02).
    """


# ---------------------------------------------------------------------------
# Module-level limiters
# ---------------------------------------------------------------------------

_ckan_limiter = get_limiter(RATE_GROUP_CKAN, RATE_LIMIT_CKAN)
_geonb_limiter = get_limiter(RATE_GROUP_GEONB, RATE_LIMIT_GEONB)
_socrata_limiter = get_limiter(RATE_GROUP_SOCRATA, RATE_LIMIT_SOCRATA)
_511_limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)


# ---------------------------------------------------------------------------
# Private helpers — fully implemented (Wave 0)
# ---------------------------------------------------------------------------


async def _api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Federal CKAN Action API call against open.canada.ca (organization:nb).

    Modeled on alberta/client.py:_api_get. `api_get` returns already-parsed
    JSON — do NOT call `.raise_for_status()` or `.json()` on its return.
    Unwraps the CKAN `{"success": ..., "result": ...}` envelope and raises
    `UpstreamData` (-> UPSTREAM_ERROR, never the caller's fault) when the
    envelope reports failure or is not a dict.

    Args:
        path: Action API path (e.g. "package_search") relative to
            `{CKAN_BASE_URL}/action/`.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN `result` field (dict OR list depending on action).

    Raises:
        UpstreamData: When the CKAN envelope is missing, malformed, or reports
            `success: false`.
    """
    url = f"{CKAN_BASE_URL}/action/{path}"
    await _ckan_limiter.acquire()
    envelope = await api_get(url, params or {}, headers={"User-Agent": USER_AGENT})
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise UpstreamData(f"federal CKAN returned an unusable envelope for {path}")
    return envelope.get("result", {})


def _build_fq(extra_fq: str | None) -> str:
    """Compose the fq (filter query) clause for federal CKAN discovery calls.

    The NB organization clause is always first and is NEVER caller-overridable
    (T-21-04) — no `organization` parameter is exposed to any discovery tool.

    Args:
        extra_fq: An optional caller-supplied fq fragment (e.g. a format or
            tag filter) to AND onto the NB clause.

    Returns:
        `"organization:nb"` alone, or `"organization:nb AND {extra_fq}"`.
    """
    if extra_fq:
        return f"{NB_ORG_FQ} AND {extra_fq}"
    return NB_ORG_FQ


def _shape_dataset(raw: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    """Shape a raw federal CKAN dataset dict for token-efficient consumption.

    Copies the bilingual fallback chain from ckan/client.py:_shape_dataset
    verbatim (D-12, Pattern 2): prefer the requested language from
    `title_translated`/`notes_translated`, then their English key, then the
    plain `title`/`notes`. NB's separately-published FR/EN record pairs are
    handled correctly by this same chain — no deduplication (RESEARCH
    Pitfall 5): each CKAN record already carries only its own language.

    Args:
        raw: Raw dataset dict from federal CKAN package_show/package_search.
        lang: Language code ('en' or 'fr').

    Returns:
        Flat dict: id, name, title, description, organization, num_resources,
        tags, resources (capped to 10), metadata_modified.
    """
    title_translated: dict[str, str] | None = raw.get("title_translated")
    if title_translated:
        title = title_translated.get(lang) or title_translated.get("en") or raw.get("title")
    else:
        title = raw.get("title")

    notes_translated: dict[str, str] | None = raw.get("notes_translated")
    if notes_translated:
        description = notes_translated.get(lang) or notes_translated.get("en") or raw.get("notes")
    else:
        description = raw.get("notes")

    raw_resources: list[dict[str, Any]] = raw.get("resources") or []

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "title": title,
        "description": description,
        "organization": raw.get("organization"),
        "num_resources": len(raw_resources),
        "tags": [t.get("name") for t in (raw.get("tags") or []) if isinstance(t, dict)],
        "resources": raw_resources[:10],
        "metadata_modified": raw.get("metadata_modified"),
    }


async def _geonb_query(
    service_url: str,
    layer_id: int,
    where: str | None = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    limit: int = MAX_RECORDS,
    ttl: int = CACHE_TTL_META,
    cache_key: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Shared curated-tool helper: query a GeoNB MapServer layer via
    `shared/arcgis_hub.py:query_feature_service` (unchanged, D-05), rate
    limited and cached.

    Every curated GeoNB tool's client function delegates here rather than
    calling `arcgis_hub.query_feature_service` directly, so the limiter
    acquisition and cache-key convention live in one place.

    Returns ({"features": [...], "count": N, "truncated": bool}, was_cached).
    """
    key = cache_key or f"{CACHE_KEY_PREFIX}geonb:{service_url}:{layer_id}:{where}:{out_fields}:{limit}"

    async def _fetch() -> dict[str, Any]:
        await _geonb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            service_url,
            layer_id=layer_id,
            where=where,
            out_fields=out_fields,
            include_geometry=include_geometry,
            max_records=limit,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(key, ttl, _fetch)


async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """NB 511 REST API v2 call. Returns raw JSON list.

    GATED: requires NEW_BRUNSWICK_511_KEY environment variable — verified live
    against `511.gnb.ca/api/v2/get/event`, which exists and returns
    `<Error><Message>Invalid Key</Message></Error>` when unkeyed (D-09).
    If the key is absent, raises `Five11NotConfigured` — the tool layer
    catches it and returns `make_error("NOT_CONFIGURED", ...)` (D-10, a
    normal envelope, not an exception path).

    Args:
        endpoint: 511 endpoint name (e.g. "event", "winterroadcondition",
            "camera").
        params: Optional extra query parameters.

    Returns:
        Raw JSON list from the 511 API.

    Raises:
        Five11NotConfigured: When NEW_BRUNSWICK_511_KEY is unset.
    """
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured(
            f"{FIVE11_KEY_ENV} not set. NB 511 requires an API key — see https://511.gnb.ca"
        )
    rows = await api_get(
        f"{FIVE11_BASE_URL}/{endpoint}",
        {**(params or {}), "key": key, "format": "json"},
        headers={"User-Agent": USER_AGENT},
    )
    return rows if isinstance(rows, list) else []


# ---------------------------------------------------------------------------
# Crown Land — Task 1 tracer (fully implemented)
# ---------------------------------------------------------------------------


async def fetch_crown_land(
    holder: int | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch New Brunswick Crown Land parcels from GeoNB_DNR_Crown_Land layer 3.

    Builds the WHERE clause server-side from the typed `holder` argument — never
    from a caller-supplied clause string. `holder` is a raw integer holder code
    with no server-exposed name domain (RESEARCH Pitfall 4).

    Returns ({"features": [...], "count": N, "truncated": bool}, was_cached).
    """
    where = f"HOLDER={holder}" if holder is not None else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}crown_land:{holder}:{limit}"
    return await _geonb_query(
        CROWN_LAND_SERVICE,
        layer_id=CROWN_LAND_LAYER,
        where=where,
        out_fields=CROWN_LAND_FIELDS,
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


# ---------------------------------------------------------------------------
# Federal CKAN discovery — Plan 02 fills bodies
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    extra_fq: str | None = None,
    limit: int = 10,
    offset: int = 0,
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """Search federal CKAN datasets filtered to organization:nb.

    Plan 02 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_search_datasets")


async def fetch_dataset_details(
    dataset_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full details for a single federal CKAN dataset.

    Plan 02 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_dataset_details")


async def fetch_query_dataset(
    dataset_id: str,
    resource_index: int = 0,
    limit: int = 1000,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Query/parse a resource from a federal CKAN NB dataset.

    Plan 02 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_query_dataset")


async def fetch_organizations(
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """List organizations among NB federal CKAN datasets.

    Plan 02 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_organizations")


async def fetch_categories(
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """List categories/groups among NB federal CKAN datasets.

    Plan 02 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_categories")


# ---------------------------------------------------------------------------
# gnb.socrata.com discovery — Plan 02 fills bodies (checkpoint option-a)
# ---------------------------------------------------------------------------


async def fetch_gnb_socrata_search(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """Search gnb.socrata.com's catalog (keyless, 312 datasets).

    Plan 02 implements via `shared/socrata.py:search_catalog` +
    `shape_catalog_result`. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_gnb_socrata_search")


async def fetch_gnb_socrata_query(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    limit: int = 1000,
) -> tuple[list[dict[str, Any]], bool]:
    """Query a gnb.socrata.com dataset via SoQL.

    Plan 02 implements via `shared/socrata.py:query_dataset`. Locked
    signature — do not change.
    """
    raise NotImplementedError("Plan 02 implements fetch_gnb_socrata_query")


# ---------------------------------------------------------------------------
# GeoNB discovery + flood/water — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_geonb_services(
    query: str = "",
    include_excluded: bool = False,
) -> tuple[list[dict[str, Any]], bool]:
    """List GeoNB services via the live service-directory enumerator (D-06).

    Plan 04 implements via `shared/arcgis_hub.py:list_arcgis_server_services`.
    Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_geonb_services")


async def fetch_geonb_service_layers(
    service_name: str,
) -> tuple[dict[str, Any], bool]:
    """List the layers/tables of a single GeoNB service.

    Plan 04 implements via `shared/arcgis_hub.py:get_arcgis_server_layers`.
    Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_geonb_service_layers")


async def fetch_geonb_layer_features(
    service_name: str,
    layer_id: int,
    where: str | None = None,
    out_fields: str = "*",
    limit: int = MAX_RECORDS,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Query any GeoNB layer by service name + layer id — the long-tail escape
    hatch that keeps `nb_get_provincial_parks`/`nb_get_mineral_occurrences`
    reachable after the checkpoint option-a manifest change.

    Plan 04 implements via `_geonb_query`. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_geonb_layer_features")


async def fetch_flood_hazard_areas(
    sheet: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch flood hazard index polygons (GeoNB_ENV_FloodHazardIndex layer 0).

    Plan 04 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_flood_hazard_areas")


async def fetch_historical_floods(
    event: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch historical flood limits/extents (GeoNB_ENV_Historical_Floods,
    layer 0 for 2008/2018 events, layer 8 for the 1973 event).

    Plan 04 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_historical_floods")


async def fetch_wetlands(
    wetland_class: str | None = None,
    status: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch wetland polygons (GeoNB_ENV_Wetlands layer 2). FILTER_REQUIRED —
    163,206 rows; the tool layer rejects an unfiltered call (T-21-03).

    Plan 04 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_wetlands")


async def fetch_contaminated_sites(
    status: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch contaminated site points (GeoNB_ELG_Contaminated_Sites layer 0).

    Plan 04 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 04 implements fetch_contaminated_sites")


# ---------------------------------------------------------------------------
# Parcels / civic address — Plan 05 fills bodies
# ---------------------------------------------------------------------------


async def fetch_parcels(
    pid: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch land parcels (GeoNB_SNB_Parcels layer 0). FILTER_REQUIRED —
    604,520 rows; the tool layer rejects an unfiltered call (T-21-03).

    Plan 05 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 05 implements fetch_parcels")


async def fetch_civic_addresses(
    community: str | None = None,
    street: str | None = None,
    civic_number: int | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch civic addresses (GeoNB_DPS_Civic_Address layer 0). FILTER_REQUIRED
    — 373,172 rows; the tool layer rejects an unfiltered call (T-21-03).

    Plan 05 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 05 implements fetch_civic_addresses")


# ---------------------------------------------------------------------------
# Health / education + 511 — Plan 06 fills bodies
# ---------------------------------------------------------------------------


async def fetch_health_facilities(
    facility_type: str,
    name: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch health facilities (GeoNB_Health_Facilities, HEALTH_FACILITY_LAYERS
    dispatch by facility_type).

    Plan 06 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 06 implements fetch_health_facilities")


async def fetch_public_schools(
    sector: str = "anglophone",
    district: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch public schools (GeoNB_EECD_PublicSchools, SCHOOL_SECTOR_LAYERS
    dispatch by sector).

    Plan 06 implements. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 06 implements fetch_public_schools")


async def fetch_road_events() -> tuple[list[dict[str, Any]], bool]:
    """Fetch current road events from NB 511 (key-gated).

    Plan 06 implements via `_511_get`. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 06 implements fetch_road_events")


async def fetch_winter_road_conditions() -> tuple[list[dict[str, Any]], bool]:
    """Fetch winter road conditions from NB 511 (key-gated).

    Plan 06 implements via `_511_get`. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 06 implements fetch_winter_road_conditions")


async def fetch_traffic_cameras() -> tuple[list[dict[str, Any]], bool]:
    """Fetch traffic camera locations from NB 511 (key-gated).

    Plan 06 implements via `_511_get`. Locked signature — do not change.
    """
    raise NotImplementedError("Plan 06 implements fetch_traffic_cameras")
