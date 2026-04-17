"""Alberta module client — async functions returning (data, was_cached) tuples.

Plans 02-07 fill bodies (this Wave 0 file only defines signatures + two helpers):

  - Plan 02: fetch_search_datasets, fetch_dataset_details, fetch_query_dataset,
             fetch_organizations, fetch_format_categories
  - Plan 03: fetch_well_licences_today, fetch_well_licences_archive,
             fetch_pipeline_statistics, fetch_production_volumes
  - Plan 04: fetch_active_fires, fetch_fire_perimeters, fetch_fire_bans,
             fetch_fire_control_orders
  - Plan 05: fetch_hospitals, fetch_ahs_zones, fetch_health_facilities
  - Plan 06: fetch_road_events, fetch_winter_road_conditions, fetch_traffic_cameras
  - Plan 07: fetch_air_quality_stations, fetch_water_advisories,
             fetch_crop_production, fetch_population_estimates,
             fetch_provincial_parks

CRITICAL (Phase 15-05 contract — _api_get MUST follow this):

  shared.http.api_get returns PARSED JSON (dict or list), NOT an httpx.Response.
  NEVER call `.raise_for_status()` or `.json()` on the return value.

  Post-15-05 pattern (enforced by TestSharedApiGetContract in Plan 02):

      envelope = await api_get(url, params or {}, headers=DEFAULT_HEADERS)
      if not isinstance(envelope, dict) or not envelope.get("success", False):
          raise httpx.HTTPStatusError(...)
      return envelope.get("result", {})

  `_511_get` is a sibling helper for the 511 Alberta endpoints, which return a
  raw JSON **list** (NOT a CKAN envelope) — so no `.success`/`.result` unwrap.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx

from mcp_canada.shared import arcgis_hub  # noqa: F401 — used by Plans 04/05/07
from mcp_canada.shared.cache import cached_fetch  # noqa: F401 — used by Plans 02-07
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse  # noqa: F401 — used by Plans 02/03/07
from mcp_canada.shared.rate_limiter import get_limiter  # noqa: F401 — used by Plans 02-07

from .constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    CKAN_BASE_URL,
    DEFAULT_HEADERS,
    FIVE11_BASE_URL,
    RATE_GROUP_511,
    RATE_GROUP_CKAN,
    RATE_LIMIT_511,
    RATE_LIMIT_CKAN,
)
from .schemas import (  # noqa: F401 — re-exported for downstream plans to import from .client if needed
    Alberta511Camera,
    Alberta511Event,
    Alberta511WinterRoad,
    AlbertaActiveFire,
    AlbertaAhsZone,
    AlbertaAqhiStation,
    AlbertaCategory,
    AlbertaCropProductionRow,
    AlbertaDatasetDetails,
    AlbertaDatasetSummary,
    AlbertaEmsStation,
    AlbertaFireBan,
    AlbertaFireControlOrder,
    AlbertaFirePerimeter,
    AlbertaForestArea,
    AlbertaHospital,
    AlbertaOrganization,
    AlbertaPcnClinic,
    AlbertaPipelineRow,
    AlbertaPopulationEstimate,
    AlbertaProductionRow,
    AlbertaProvincialPark,
    AlbertaResource,
    AlbertaWaterAdvisory,
    AlbertaWellLicence,
)

__all__ = [
    # Private helpers (fully implemented in Wave 0)
    "_api_get",
    "_511_get",
    # Discovery (Plan 02)
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_query_dataset",
    "fetch_organizations",
    "fetch_format_categories",
    # AER / energy (Plan 03)
    "fetch_well_licences_today",
    "fetch_well_licences_archive",
    "fetch_pipeline_statistics",
    "fetch_production_volumes",
    # Wildfire (Plan 04)
    "fetch_active_fires",
    "fetch_fire_perimeters",
    "fetch_fire_bans",
    "fetch_fire_control_orders",
    # Health (Plan 05)
    "fetch_hospitals",
    "fetch_ahs_zones",
    "fetch_health_facilities",
    # Transport / 511 (Plan 06)
    "fetch_road_events",
    "fetch_winter_road_conditions",
    "fetch_traffic_cameras",
    # Environment / agriculture / demographics / parks (Plan 07)
    "fetch_air_quality_stations",
    "fetch_water_advisories",
    "fetch_crop_production",
    "fetch_population_estimates",
    "fetch_provincial_parks",
]


# ---------------------------------------------------------------------------
# Module-level limiters (per-source TokenBuckets, shared by all downstream calls)
# ---------------------------------------------------------------------------

_ckan_limiter = get_limiter(RATE_GROUP_CKAN, RATE_LIMIT_CKAN)
_511_limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)


# ---------------------------------------------------------------------------
# Private helpers — fully implemented (Wave 0)
# ---------------------------------------------------------------------------


async def _api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """CKAN Action API call against open.alberta.ca.

    Returns the parsed CKAN `result` field. Raises `httpx.HTTPStatusError` on
    success=False or when the upstream returns a non-dict envelope.

    Phase 15-05 contract (enforced by TestSharedApiGetContract):
      - api_get returns already-parsed JSON — do NOT call .raise_for_status()
        or .json() on the return value.
      - For `package_search` / `package_show` the result is a dict.
      - For `organization_list` / `group_list` / `tag_list` the result is a list,
        which the caller must handle.

    Args:
        path: Action API path (e.g. "package_search") relative to CKAN_BASE_URL.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN `result` field (dict OR list depending on endpoint).

    Raises:
        httpx.HTTPStatusError: When the CKAN envelope is missing or success=False.
    """
    url = CKAN_BASE_URL + path
    await _ckan_limiter.acquire()
    envelope = await api_get(url, params or {}, headers=DEFAULT_HEADERS)
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise httpx.HTTPStatusError(
            f"CKAN returned success=False for {path}",
            request=httpx.Request("GET", url),
            response=httpx.Response(500),
        )
    return envelope.get("result", {})


async def _511_get(
    endpoint: str, params: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """511 Alberta v2 API call — returns a raw JSON list (NOT a CKAN envelope).

    511 Alberta's public v2 endpoints return arrays directly — `event`,
    `winterroads`, `cameras`. The `format=json` query param forces JSON output
    (the server otherwise content-negotiates with XML).

    Args:
        endpoint: 511 endpoint name (e.g. "event", "winterroads", "cameras").
        params: Optional query parameters. `format=json` is injected if absent.

    Returns:
        A list of parsed JSON records. Empty list if the response is not a list.
    """
    url = f"{FIVE11_BASE_URL}/{endpoint}"
    merged_params = {"format": "json", **(params or {})}
    await _511_limiter.acquire()
    rows = await api_get(url, merged_params, headers=DEFAULT_HEADERS)
    return rows if isinstance(rows, list) else []


# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


# Subset of CKAN `extras` keys worth surfacing (Pitfall 11 — 50+ publication-
# identifier fields are dropped; these few contain agent-useful metadata).
_USEFUL_EXTRA_KEYS: frozenset[str] = frozenset(
    {"isopen", "language", "frequencyofupdate", "creator"}
)


def _flatten_extras(extras: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Flatten CKAN `extras` list into a dict, keeping only agent-useful keys.

    Alberta CKAN attaches 50+ publication-repository extras per dataset
    (identifier-AGDEX-number, identifier-ISBN-pdf, audience, contributor1..6,
    alternatetitle1..3, Extent, etc.). Pitfall 11: surface only isopen /
    language / frequencyofupdate / creator — everything else is publication
    metadata that wastes agent context tokens.
    """
    if not extras:
        return {}
    out: dict[str, Any] = {}
    for entry in extras:
        if not isinstance(entry, dict):
            continue
        key = entry.get("key")
        if key in _USEFUL_EXTRA_KEYS:
            out[key] = entry.get("value")
    return out


def _coerce_bool(value: Any) -> bool | None:
    """CKAN `isopen` can be a string ('true'/'false'), a bool, or missing."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _build_summary(raw: dict[str, Any]) -> AlbertaDatasetSummary:
    org = raw.get("organization") or {}
    resources = raw.get("resources") or []
    formats = sorted(
        {(r.get("format") or "").strip() for r in resources if r.get("format")}
    )
    return AlbertaDatasetSummary(
        id=raw.get("id", ""),
        name=raw.get("name", ""),
        title=raw.get("title", ""),
        notes=raw.get("notes"),
        organization_slug=org.get("name") if isinstance(org, dict) else None,
        license_id=raw.get("license_id"),
        num_resources=int(raw.get("num_resources") or len(resources) or 0),
        metadata_modified=raw.get("metadata_modified"),
        formats=formats,
    )


def _build_resource(raw: dict[str, Any]) -> AlbertaResource:
    size_raw = raw.get("size")
    try:
        size = int(size_raw) if size_raw not in (None, "") else None
    except (TypeError, ValueError):
        size = None
    return AlbertaResource(
        id=raw.get("id", ""),
        name=raw.get("name"),
        format=raw.get("format"),
        url=raw.get("url", ""),
        datastore_active=bool(raw.get("datastore_active") or False),
        size=size,
    )


def _build_details(raw: dict[str, Any]) -> AlbertaDatasetDetails:
    org = raw.get("organization") or {}
    useful = _flatten_extras(raw.get("extras"))
    return AlbertaDatasetDetails(
        id=raw.get("id", ""),
        name=raw.get("name", ""),
        title=raw.get("title", ""),
        notes=raw.get("notes"),
        organization_slug=org.get("name") if isinstance(org, dict) else None,
        license_id=raw.get("license_id"),
        isopen=_coerce_bool(useful.get("isopen")),
        language=useful.get("language"),
        frequencyofupdate=useful.get("frequencyofupdate"),
        creator=useful.get("creator"),
        metadata_modified=raw.get("metadata_modified"),
        resources=[_build_resource(r) for r in (raw.get("resources") or [])],
    )


async def fetch_search_datasets(
    q: str = "",
    organization: str | None = None,
    format: str | None = None,
    rows: int = 10,
    start: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets).

    Returns a dict `{"count": int, "results": [AlbertaDatasetSummary, ...]}`
    — `count` is the total matching dataset count from CKAN, `results` is the
    current page of flattened summaries.

    Filters:
      - organization: appends `fq=organization:<slug>`
      - format: appends `fq=res_format:<format>` (e.g. CSV / ESRI REST / XLSX)

    CKAN enforces `rows <= 100` per request — larger values are silently clamped.
    """
    params: dict[str, Any] = {
        "q": q,
        "rows": min(max(rows, 1), 100),
        "start": max(start, 0),
    }
    fq_parts: list[str] = []
    if organization:
        fq_parts.append(f"organization:{organization}")
    if format:
        fq_parts.append(f"res_format:{format}")
    if fq_parts:
        params["fq"] = " ".join(fq_parts)

    cache_key = f"{CACHE_KEY_PREFIX}search:{q}:{organization}:{format}:{rows}:{start}"

    async def _fetch() -> dict[str, Any]:
        result = await _api_get("package_search", params)
        raw_results = result.get("results") or []
        return {
            "count": int(result.get("count") or 0),
            "results": [_build_summary(r) for r in raw_results],
        }

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_dataset_details(package_id: str) -> tuple[AlbertaDatasetDetails, bool]:
    """Full dataset record (flat) — hides 50+ publication-identifier extras.

    Pitfall 11: CKAN attaches ~55 extras per Alberta dataset (AGDEX numbers,
    ISBN, audience, author, alternatetitle1..3, etc.). Only the useful subset
    (isopen / language / frequencyofupdate / creator) survives flattening.
    """
    cache_key = f"{CACHE_KEY_PREFIX}details:{package_id}"

    async def _fetch() -> AlbertaDatasetDetails:
        raw = await _api_get("package_show", {"id": package_id})
        return _build_details(raw)

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


def _pick_esri_resource(
    resources: list[AlbertaResource], preferred_index: int
) -> AlbertaResource | None:
    """Pitfall 12: prefer FeatureServer over MapServer for ESRI REST resources.

    When `preferred_index == 0` (default) and one of the resources is an ESRI
    REST FeatureServer, pick that one regardless of position. Otherwise fall
    back to literal `resources[preferred_index]`.
    """
    if preferred_index == 0:
        for r in resources:
            fmt = (r.format or "").upper()
            if fmt == "ESRI REST" and "/FeatureServer" in (r.url or ""):
                return r
    if 0 <= preferred_index < len(resources):
        return resources[preferred_index]
    return None


def _split_feature_server_url(url: str) -> tuple[str, int] | None:
    """Split `.../FeatureServer/<N>` into (base, layer_id). Returns None if no match."""
    if "/FeatureServer" not in url:
        return None
    # Strip query string if any
    clean = url.split("?", 1)[0].rstrip("/")
    parts = clean.rsplit("/FeatureServer", 1)
    if len(parts) != 2:
        return None
    tail = parts[1].strip("/")
    base = parts[0] + "/FeatureServer"
    if not tail:
        # URL ends at /FeatureServer — no layer index; default to 0
        return base, 0
    try:
        layer_id = int(tail.split("/")[0])
    except ValueError:
        return base, 0
    return base, layer_id


_PARSEABLE_FORMATS: frozenset[str] = frozenset(
    {"CSV", "JSON", "GEOJSON", "XLSX", "XLS"}
)


async def fetch_query_dataset(
    package_id: str,
    resource_index: int = 0,
    where: str | None = None,
    max_records: int = 1000,
) -> tuple[dict[str, Any], bool]:
    """Query a dataset resource — auto-routes by format.

    Routing (Pattern 3 hybrid router):
      - ESRI REST + /FeatureServer URL → arcgis_hub.query_feature_service
        (Pitfall 12: when both FeatureServer and MapServer are present in
        resources[], FeatureServer wins regardless of order.)
      - CSV / JSON / GEOJSON / XLSX / XLS → shared.parsers.fetch_and_parse
      - PDF / ZIP / KML / WMS / other → metadata-only response with a `note`

    Args:
        package_id: CKAN dataset slug.
        resource_index: Index into details.resources (default 0). Ignored for
          FeatureServer preference when resource_index == 0.
        where: Optional WHERE clause for ESRI REST routing.
        max_records: Row cap (default 1000). Applied to both FS and file paths.

    Returns:
        ({data|url|format|note, ...}, was_cached)
    """
    details, _ = await fetch_dataset_details(package_id)
    resources = details.resources
    if not resources:
        return (
            {"error": "Dataset has no resources", "resources": 0},
            False,
        )
    picked = _pick_esri_resource(resources, resource_index)
    if picked is None:
        return (
            {"error": f"resource_index {resource_index} out of range"},
            False,
        )

    fmt = (picked.format or "").upper()
    url = picked.url or ""

    # ESRI REST branch (prefer FeatureServer over MapServer)
    if fmt == "ESRI REST" and "/FeatureServer" in url:
        split = _split_feature_server_url(url)
        if split is not None:
            base, layer_id = split
            rows, cached = await arcgis_hub.query_feature_service(
                base,
                layer_id,
                where=where or "1=1",
                include_geometry=False,
                max_records=max_records,
            )
            return (
                {
                    "data": rows,
                    "format": fmt,
                    "url": url,
                    "resource_id": picked.id,
                    "rows": len(rows),
                },
                cached,
            )

    # File-parseable branch
    if fmt in _PARSEABLE_FORMATS:
        rows, cached = await fetch_and_parse(url, ttl=CACHE_TTL_META)
        truncated = len(rows) > max_records
        return (
            {
                "data": rows[:max_records],
                "format": fmt,
                "url": url,
                "resource_id": picked.id,
                "rows": min(len(rows), max_records),
                "truncated": truncated,
            },
            cached,
        )

    # Metadata-only fallback (PDF, ZIP, KML, WMS, unknown)
    return (
        {
            "format": fmt or None,
            "url": url,
            "resource_id": picked.id,
            "name": picked.name,
            "size": picked.size,
            "note": "binary/archive resource — use URL directly",
        },
        False,
    )


async def fetch_organizations() -> tuple[list[AlbertaOrganization], bool]:
    """List all 370 organizations publishing on open.alberta.ca.

    Includes current ministries, historical predecessor ministries, Crown
    corporations, and advisory committees — all surfaced as slugs suitable for
    `fq=organization:<slug>` in fetch_search_datasets.
    """
    cache_key = f"{CACHE_KEY_PREFIX}orgs:all"

    async def _fetch() -> list[AlbertaOrganization]:
        result = await _api_get("organization_list", {"all_fields": True})
        if not isinstance(result, list):
            return []
        return [
            AlbertaOrganization(
                id=str(r.get("id") or r.get("name") or ""),
                name=r.get("name", ""),
                title=r.get("title") or r.get("display_name") or r.get("name", ""),
                package_count=int(r.get("package_count") or 0),
            )
            for r in result
            if isinstance(r, dict)
        ]

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_format_categories() -> tuple[list[AlbertaCategory], bool]:
    """List dataset format categories from the res_format facet (NOT group_list — Pitfall 1).

    Pitfall 1: open.alberta.ca's `group_list` returns an empty list — Alberta
    CKAN doesn't use the CKAN groups feature. Instead we surface the
    `res_format` facet (PDF / CSV / XLSX / ESRI REST / HTML / JSON / ...),
    sorted by count descending.
    """
    cache_key = f"{CACHE_KEY_PREFIX}format_facet"
    params = {"facet.field": '["res_format"]', "rows": 0, "facet.limit": 50}

    async def _fetch() -> list[AlbertaCategory]:
        result = await _api_get("package_search", params)
        facets = result.get("facets") or {}
        buckets = facets.get("res_format") or {}
        if not isinstance(buckets, dict):
            return []
        pairs = sorted(buckets.items(), key=lambda kv: kv[1], reverse=True)
        return [
            AlbertaCategory(format=str(k), count=int(v))
            for k, v in pairs
            if k
        ]

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# AER / energy (Plan 03)
# ---------------------------------------------------------------------------


async def fetch_well_licences_today() -> tuple[list[AlbertaWellLicence], bool]:
    """Today's new well licences from AER ST1 daily TXT (WELLS{MON..SUN}.TXT). Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_well_licences_archive(
    year: int,
    month: int | None = None,
) -> tuple[list[AlbertaWellLicence], bool]:
    """Archived well licences from AER ST1 monthly/annual ZIP. Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_pipeline_statistics(
    year: int,
) -> tuple[list[AlbertaPipelineRow], bool]:
    """Pipeline statistics from AER ST39 annual XLSX. Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


async def fetch_production_volumes(
    product: str,
    period: Literal["current", "monthly"] = "current",
) -> tuple[list[AlbertaProductionRow], bool]:
    """Monthly production volumes from AER ST3 per-product XLSX (Butane/Ethane/NGL/Oil/Gas/Propane/Sulphur). Filled by Plan 03."""
    raise NotImplementedError("Plan 03 implements")


# ---------------------------------------------------------------------------
# Wildfire (Plan 04)
# ---------------------------------------------------------------------------


async def fetch_active_fires(
    status: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaActiveFire], bool]:
    """Current active wildfires from WMBappServices Active_Wildfires_Dashboard_view. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_fire_perimeters(
    status: Literal["active", "extinguished"] = "active",
    year: int | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaFirePerimeter], bool]:
    """Fire perimeters from WMB Active_/Extinguished_Wildfire_Perimeters_Simplified_view. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_fire_bans(
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaFireBan], bool]:
    """Fire bans and restrictions from WMB alberta_fire_ban_system FeatureServer. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


async def fetch_fire_control_orders(
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaFireControlOrder], bool]:
    """Fire Control Orders from WMB Fire_Control_Orders_Prod_View2. Filled by Plan 04."""
    raise NotImplementedError("Plan 04 implements")


# ---------------------------------------------------------------------------
# Health (Plan 05)
# ---------------------------------------------------------------------------


async def fetch_hospitals(
    zone: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaHospital], bool]:
    """Hospitals from AHSGIS AHS_Hospitals FeatureServer (~101 hospitals, IP/ED flags). Filled by Plan 05."""
    raise NotImplementedError("Plan 05 implements")


async def fetch_ahs_zones(
    include_geometry: bool = False,
) -> tuple[list[AlbertaAhsZone], bool]:
    """5 AHS zones (South/Calgary/Central/Edmonton/North) with census population. Filled by Plan 05."""
    raise NotImplementedError("Plan 05 implements")


async def fetch_health_facilities(
    facility_type: Literal["ems", "pcn_clinic"],
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaEmsStation] | list[AlbertaPcnClinic], bool]:
    """Dispatch helper for EMS stations or PCN clinics from AHSGIS FeatureServers. Filled by Plan 05."""
    raise NotImplementedError("Plan 05 implements")


# ---------------------------------------------------------------------------
# Transport / 511 (Plan 06)
# ---------------------------------------------------------------------------


async def fetch_road_events(
    event_type: str | None = None,
) -> tuple[list[Alberta511Event], bool]:
    """Active road events (closures, construction, incidents, accidents) from 511 /event. Filled by Plan 06."""
    raise NotImplementedError("Plan 06 implements")


async def fetch_winter_road_conditions(
    area_name: str | None = None,
) -> tuple[list[Alberta511WinterRoad], bool]:
    """Winter road conditions from 511 /winterroads. Filled by Plan 06."""
    raise NotImplementedError("Plan 06 implements")


async def fetch_traffic_cameras() -> tuple[list[Alberta511Camera], bool]:
    """376 traffic camera locations + snapshot URLs from 511 /cameras. Filled by Plan 06."""
    raise NotImplementedError("Plan 06 implements")


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks (Plan 07)
# ---------------------------------------------------------------------------


async def fetch_air_quality_stations(
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaAqhiStation], bool]:
    """75 AQHI air monitoring stations from GeoDiscover aqhi/air_layers MapServer/1. Filled by Plan 07."""
    raise NotImplementedError("Plan 07 implements")


async def fetch_water_advisories(
    advisory_type: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaWaterAdvisory], bool]:
    """Water management advisories from GeoDiscover environment/river_forecast_centre. Filled by Plan 07."""
    raise NotImplementedError("Plan 07 implements")


async def fetch_crop_production(
    year: int | None = None,
    crop: str | None = None,
) -> tuple[list[AlbertaCropProductionRow], bool]:
    """Major crop production (historical CSV) from Alberta Agriculture and Irrigation. Filled by Plan 07."""
    raise NotImplementedError("Plan 07 implements")


async def fetch_population_estimates(
    breakdown: Literal[
        "csd", "cma", "quarterly", "age_sex", "sub_provincial", "components_of_growth"
    ] = "csd",
    year: int | None = None,
) -> tuple[list[AlbertaPopulationEstimate], bool]:
    """Population estimates from alberta-population-estimates-data-tables XLSX. Filled by Plan 07."""
    raise NotImplementedError("Plan 07 implements")


async def fetch_provincial_parks(
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[list[AlbertaProvincialPark], bool]:
    """Provincial parks / protected areas from GeoDiscover boundary/parks_protected_areas_alberta. Filled by Plan 07."""
    raise NotImplementedError("Plan 07 implements")
