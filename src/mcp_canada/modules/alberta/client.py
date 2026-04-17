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

import datetime
from typing import Any, Literal

import httpx

from mcp_canada.shared import arcgis_hub  # noqa: F401 — used by Plans 04/05/07
from mcp_canada.shared.cache import cached_fetch  # noqa: F401 — used by Plans 02-07
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse  # noqa: F401 — used by Plans 02/03/07
from mcp_canada.shared.rate_limiter import get_limiter  # noqa: F401 — used by Plans 02-07

from .constants import (
    ACTIVE_FIRE_PERIMETERS_FS_URL,
    ACTIVE_WILDFIRES_FS_URL,
    AER_ST1_DAILY_BASE,
    AER_ST1_MONTHLY_BASE,
    AER_ST3_BASE,
    AER_ST39_BASE,
    AHS_EMS_FS_URL,
    AHS_HOSPITALS_FS_URL,
    AHS_ZONE_FS_URL,
    CACHE_KEY_PREFIX,
    CACHE_TTL_ANNUAL,
    CACHE_TTL_DAILY,
    CACHE_TTL_LIVE,
    CACHE_TTL_META,
    CACHE_TTL_MONTHLY,
    CACHE_TTL_SEARCH,
    CACHE_TTL_STATIC,
    CKAN_BASE_URL,
    DAY_ABBR,
    DEFAULT_HEADERS,
    EXTINGUISHED_PERIMETERS_FS_URL,
    FIRE_BAN_SYSTEM_FS_URL,
    FIRE_CONTROL_ORDERS_FS_URL,
    FIVE11_BASE_URL,
    FOREST_AREA_FS_URL,
    OHV_RESTRICTION_FS_URL,
    PCN_CLINICS_FS_URL,
    RATE_GROUP_511,
    RATE_GROUP_AER,
    RATE_GROUP_AHS,
    RATE_GROUP_CKAN,
    RATE_GROUP_WMB,
    RATE_LIMIT_511,
    RATE_LIMIT_AER,
    RATE_LIMIT_AHS,
    RATE_LIMIT_CKAN,
    RATE_LIMIT_WMB,
    ST3_PRODUCTS,
    USER_AGENT,
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
_aer_limiter = get_limiter(RATE_GROUP_AER, RATE_LIMIT_AER)


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


# ST1 fixed-width column layout — verified against AER ST1 daily TXT (WELLSSUN.TXT 2026-04-17).
#
# The AER ST1 daily report uses a simple space-padded column layout. Columns are
# detected by first locating the header row ("LIC_NUM" / "OPERATOR_NAME" / ...)
# and then reading subsequent data rows until EOF. Position-based slicing keeps
# the parser resilient when individual rows are shorter than the widest data row
# (trailing columns may be blank/missing for some licences).
_ST1_COLUMNS: tuple[tuple[str, int, int | None], ...] = (
    # (field_name, start_inclusive, end_exclusive_or_None_for_line_end)
    ("licence_number", 0, 9),
    ("operator", 9, 35),
    ("well_name", 35, 63),
    ("field_code", 63, None),
)


def _parse_st1_txt(text: str) -> list[dict[str, Any]]:
    """Parse AER ST1 fixed-width daily well-licence TXT into snake_case dict rows.

    The ST1 daily TXT rotates by day-of-week (WELLS{MON..SUN}.TXT). Each file
    begins with a few header / preamble lines ("Alberta Energy Regulator ...",
    "Run Date: YYYY-MM-DD"), then a column-header row (starts with "LIC_NUM"),
    then one data row per licence.

    Data rows start with a numeric licence number in cols 0-7. We detect the
    first such row and read to EOF. Rows shorter than the first data column's
    start position are skipped as blank/footer padding.

    Returns list[dict] with keys matching the AlbertaWellLicence schema plus the
    raw `field_code` surfaced for agents that want the field context.
    """
    lines = text.splitlines()
    data_start = next(
        (
            i
            for i, ln in enumerate(lines)
            if ln[:7].strip().isdigit()
        ),
        len(lines),
    )
    out: list[dict[str, Any]] = []
    for raw in lines[data_start:]:
        if not raw.strip():
            continue
        if not raw[:7].strip().isdigit():
            # Footer / summary lines (e.g. "Total licences issued: N") — stop
            # parsing once we leave the contiguous numeric-licence block.
            break
        record: dict[str, Any] = {}
        for field, start, end in _ST1_COLUMNS:
            segment = raw[start:end] if end is not None else raw[start:]
            value = segment.strip()
            record[field] = value or None
        out.append(record)
    return out


async def fetch_well_licences_today() -> tuple[list[dict[str, Any]], bool]:
    """Today's new well licences from AER ST1 daily TXT (WELLS{MON..SUN}.TXT).

    The AER rotates ST1 daily TXT files by day-of-week; this tool always returns
    the file for "today" based on the local weekday. The AER root URL returns a
    303 redirect to `static.aer.ca` — we use httpx with `follow_redirects=True`.

    Returns list[dict] rows with `licence_number`, `operator`, `well_name`, and
    `field_code` keys parsed from the fixed-width TXT via `_parse_st1_txt`.
    """
    today_abbr = DAY_ABBR[datetime.date.today().weekday()]
    url = f"{AER_ST1_DAILY_BASE}/WELLS{today_abbr}.TXT"
    cache_key = f"{CACHE_KEY_PREFIX}aer_st1_daily:{today_abbr}"

    async def _fetch() -> list[dict[str, Any]]:
        await _aer_limiter.acquire()
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
        ) as ac:
            resp = await ac.get(url)
            resp.raise_for_status()
            return _parse_st1_txt(resp.text)

    return await cached_fetch(cache_key, CACHE_TTL_DAILY, _fetch)


async def fetch_well_licences_archive(
    year: int,
    month: int | None = None,
) -> tuple[dict[str, Any], bool]:
    """Discovery-only lookup of AER ST1 monthly / annual archive ZIP URL.

    Returns the URL and metadata for the archived well-licence ZIP for a given
    year (+ optional month). The contents are large fixed-width TXT files that
    should NOT be auto-parsed; agents are expected to download externally.

    URL pattern:
      - year + month: `{AER_ST1_MONTHLY_BASE}/dwll{YYYY}-{MM}.zip`
      - year only:    `{AER_ST1_MONTHLY_BASE}/dwll{YYYY}.zip`
    """
    if month is not None:
        filename = f"dwll{year}-{month:02d}.zip"
    else:
        filename = f"dwll{year}.zip"
    url = f"{AER_ST1_MONTHLY_BASE}/{filename}"
    payload: dict[str, Any] = {
        "url": url,
        "year": year,
        "month": month,
        "note": (
            "Monthly archive ZIP — fixed-width TXT contents. "
            "Download externally; do not auto-parse."
        ),
    }
    return payload, False


async def fetch_pipeline_statistics(
    year: int,
) -> tuple[list[dict[str, Any]], bool]:
    """Pipeline statistics from AER ST39 annual XLS.

    Fetches `ST39-{YYYY}.xls` from `static.aer.ca` and flattens multi-sheet
    content via `shared/parsers.fetch_and_parse`. Rows have snake_case keys
    (substance, length_km, operator, year — exact keys depend on sheet layout).
    """
    url = f"{AER_ST39_BASE}/ST39-{year}.xls"
    cache_key = f"{CACHE_KEY_PREFIX}aer_st39:{year}"

    async def _fetch() -> list[dict[str, Any]]:
        await _aer_limiter.acquire()
        rows, _ = await fetch_and_parse(url, ttl=CACHE_TTL_ANNUAL)
        return rows

    return await cached_fetch(cache_key, CACHE_TTL_ANNUAL, _fetch)


async def fetch_production_volumes(
    product: str,
    period: Literal["current", "monthly"] = "current",
) -> tuple[list[dict[str, Any]], bool]:
    """Monthly production volumes from AER ST3 per-product XLSX.

    Valid products (Pitfall 8 — exact case):
      Butane, Ethane, NGL, Oil, Gas, Propane, Sulphur.

    `period="current"` (the only currently-supported value) hits
    `{Product}_current.xlsx`, which always reflects the latest month.

    Raises:
        ValueError: If `product` is not in `ST3_PRODUCTS` (includes hint).
    """
    if product not in ST3_PRODUCTS:
        raise ValueError(
            f"Invalid product '{product}'. "
            f"Valid products: {list(ST3_PRODUCTS)}"
        )
    url = f"{AER_ST3_BASE}/{product}_current.xlsx"
    cache_key = f"{CACHE_KEY_PREFIX}aer_st3:{product}:{period}"

    async def _fetch() -> list[dict[str, Any]]:
        await _aer_limiter.acquire()
        rows, _ = await fetch_and_parse(url, ttl=CACHE_TTL_MONTHLY)
        return rows

    return await cached_fetch(cache_key, CACHE_TTL_MONTHLY, _fetch)


# ---------------------------------------------------------------------------
# Wildfire (Plan 04)
# ---------------------------------------------------------------------------


# Module-level WMB limiter — shared by all 4 wildfire fetchers (5 r/s)
_wmb_limiter = get_limiter(RATE_GROUP_WMB, RATE_LIMIT_WMB)


async def fetch_active_fires(
    status: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Current active wildfires from WMBappServices Active_Wildfires_Dashboard_view (layer 0).

    Uses `shared/arcgis_hub.query_feature_service` — WMBappServices is a public
    ArcGIS Online org (`Eb8P5h4CJk8utIBz`) and does NOT require a token, unlike
    GeoDiscover's wildfire folder (Pitfall 3). Optional status= pushes through
    as a WHERE filter (`FIRE_STATUS='<status>'`); None returns all active fires.

    Returns:
        `({"features": list, "truncated": bool, "count": int}, was_cached)` —
        `truncated=True` when the 5000-record cap was hit with more available.
    """
    where = f"FIRE_STATUS='{status}'" if status else None
    cache_key = (
        f"{CACHE_KEY_PREFIX}wmb:active_fires:{status}:{max_records}:{include_geometry}"
    )

    async def _fetch() -> dict[str, Any]:
        await _wmb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            ACTIVE_WILDFIRES_FS_URL,
            0,
            where=where,
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "count": len(features)}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_fire_perimeters(
    status: Literal["active", "extinguished"] = "active",
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fire perimeters from WMB Active_/Extinguished_Wildfire_Perimeters_Simplified_view.

    Dispatches by status:
      - "active"        → ACTIVE_FIRE_PERIMETERS_FS_URL (LIVE 5-min cache)
      - "extinguished"  → EXTINGUISHED_PERIMETERS_FS_URL (STATIC 24h cache)

    Raises:
        ValueError: If `status` is not "active" or "extinguished".
    """
    if status == "active":
        url = ACTIVE_FIRE_PERIMETERS_FS_URL
        ttl = CACHE_TTL_LIVE
    elif status == "extinguished":
        url = EXTINGUISHED_PERIMETERS_FS_URL
        ttl = CACHE_TTL_STATIC
    else:
        raise ValueError(
            f"status must be 'active' or 'extinguished', got '{status}'"
        )

    cache_key = (
        f"{CACHE_KEY_PREFIX}wmb:perimeters:{status}:{max_records}:{include_geometry}"
    )

    async def _fetch() -> dict[str, Any]:
        await _wmb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            url,
            0,
            where=None,
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "count": len(features)}

    return await cached_fetch(cache_key, ttl, _fetch)


async def fetch_fire_bans(
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Province-wide fire ban registry from WMB alberta_fire_ban_system FeatureServer.

    Same data backing the public albertafirebans.ca SPA dashboard (research
    confirmed it's federated and public). 5-minute cache because bans can be
    issued/lifted during active fire events.
    """
    cache_key = (
        f"{CACHE_KEY_PREFIX}wmb:fire_bans:{max_records}:{include_geometry}"
    )

    async def _fetch() -> dict[str, Any]:
        await _wmb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            FIRE_BAN_SYSTEM_FS_URL,
            0,
            where=None,
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "count": len(features)}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_fire_control_orders(
    category: Literal["fire_control", "ohv_restriction", "forest_area"] = "fire_control",
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Fire control orders / OHV restrictions / forest area boundaries from WMBappServices.

    Dispatches by category:
      - "fire_control"    → FIRE_CONTROL_ORDERS_FS_URL (LIVE 5-min cache)
      - "ohv_restriction" → OHV_RESTRICTION_FS_URL (LIVE 5-min cache)
      - "forest_area"     → FOREST_AREA_FS_URL (STATIC 24h cache — 10 Alberta
                            forest areas; stable reference data)

    Raises:
        ValueError: If `category` is not one of the 3 accepted values.
    """
    url_map: dict[str, tuple[str, int]] = {
        "fire_control": (FIRE_CONTROL_ORDERS_FS_URL, CACHE_TTL_LIVE),
        "ohv_restriction": (OHV_RESTRICTION_FS_URL, CACHE_TTL_LIVE),
        "forest_area": (FOREST_AREA_FS_URL, CACHE_TTL_STATIC),
    }
    if category not in url_map:
        raise ValueError(
            f"category must be one of {list(url_map)}, got '{category}'"
        )
    url, ttl = url_map[category]
    cache_key = (
        f"{CACHE_KEY_PREFIX}wmb:fco:{category}:{max_records}:{include_geometry}"
    )

    async def _fetch() -> dict[str, Any]:
        await _wmb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            url,
            0,
            where=None,
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "truncated": truncated, "count": len(features)}

    return await cached_fetch(cache_key, ttl, _fetch)


# ---------------------------------------------------------------------------
# Health (Plan 05)
# ---------------------------------------------------------------------------


async def fetch_hospitals(
    zone: str | None = None,
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """101 AHS hospitals with IP/ED capability flags from AHSGIS.

    Fetches all hospitals from the AHS_Hospitals FeatureServer (layer 0). When
    `zone` is provided, performs a post-fetch case-insensitive substring match
    on the `Location` field (name-substring only — no polygon containment).

    Fields surfaced per feature include: Location, Hospital_N, St_Address,
    PostalCode, Phone, H_Code, IP (inpatient flag), ED (emergency flag), Label.

    Returns (`{"features": [...], "count": int, "truncated": bool}`, was_cached).
    TTL=STATIC (24h).
    """
    cache_key = (
        f"{CACHE_KEY_PREFIX}ahs:hospitals:{zone}:{max_records}:{include_geometry}"
    )
    limiter = get_limiter(RATE_GROUP_AHS, RATE_LIMIT_AHS)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            AHS_HOSPITALS_FS_URL,
            0,
            where="1=1",
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        if zone:
            z = zone.lower()
            features = [
                f
                for f in features
                if z in (f.get("Location", "") or "").lower()
                or z in (f.get("location", "") or "").lower()
            ]
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


async def fetch_ahs_zones(
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """5 AHS zones (South/Calgary/Central/Edmonton/North) with POP2006/2011/2016.

    Population field names are normalized from ArcGIS ALL-CAPS (POP2006/POP2011/
    POP2016) to snake_case (pop_2006/pop_2011/pop_2016) for schema consistency.
    Zone_Name and Zone_ID are also snake-cased.

    Returns (`{"features": [...], "count": int, "truncated": bool}`, was_cached).
    TTL=STATIC (24h).
    """
    cache_key = f"{CACHE_KEY_PREFIX}ahs:zones:{include_geometry}"
    limiter = get_limiter(RATE_GROUP_AHS, RATE_LIMIT_AHS)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            AHS_ZONE_FS_URL,
            0,
            where="1=1",
            out_fields="*",
            include_geometry=include_geometry,
            max_records=10,
        )
        normalized: list[dict[str, Any]] = []
        for f in features:
            entry: dict[str, Any] = {
                "zone_name": f.get("Zone_Name") or f.get("zone_name"),
                "zone_id": f.get("Zone_ID") or f.get("zone_id"),
                "pop_2006": f.get("POP2006") or f.get("pop_2006"),
                "pop_2011": f.get("POP2011") or f.get("pop_2011"),
                "pop_2016": f.get("POP2016") or f.get("pop_2016"),
            }
            if include_geometry and "geometry" in f:
                entry["geometry"] = f.get("geometry")
            normalized.append(entry)
        return {
            "features": normalized,
            "count": len(normalized),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


async def fetch_health_facilities(
    facility_type: Literal["ems", "pcn_clinic"],
    max_records: int = 5000,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Dispatch helper for EMS stations or PCN clinics from AHSGIS.

    facility_type='ems' hits AHS_EMS_FS_URL (Alberta EMS stations).
    facility_type='pcn_clinic' hits PCN_CLINICS_FS_URL (Primary Care Network
    clinics). Any other value raises ValueError (enforced at client layer).

    NOTE: ER wait times are NOT exposed by AHS in machine-readable form (Pitfall
    9 — AHS publishes via a JavaScript widget only). This tool slot is used for
    facility-type dispatch instead.

    Returns (`{"features": [...], "count": int, "truncated": bool, "facility_type": str}`,
    was_cached). TTL=STATIC (24h).
    """
    url_map = {
        "ems": AHS_EMS_FS_URL,
        "pcn_clinic": PCN_CLINICS_FS_URL,
    }
    if facility_type not in url_map:
        raise ValueError(
            f"facility_type must be one of {list(url_map)}, got {facility_type!r}"
        )
    url = url_map[facility_type]
    cache_key = (
        f"{CACHE_KEY_PREFIX}ahs:facility:{facility_type}:{max_records}:{include_geometry}"
    )
    limiter = get_limiter(RATE_GROUP_AHS, RATE_LIMIT_AHS)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            url,
            0,
            where="1=1",
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
            "facility_type": facility_type,
        }

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


# ---------------------------------------------------------------------------
# Transport / 511 (Plan 06)
# ---------------------------------------------------------------------------


async def fetch_road_events(
    event_type: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Active road events (closures, construction, incidents) from 511 Alberta /event.

    Uses `_511_get` (NOT `_api_get` — Pitfall 6: 511 returns a raw JSON list,
    not a CKAN envelope). Optional `event_type` performs a case-insensitive
    substring match on the `EventType` field (e.g. "Closure", "Construction").

    Returns:
        `({"events": list[dict], "count": int}, was_cached)` with TTL=LIVE (5min).
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:event:{event_type}"
    limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        rows = await _511_get("event")
        if event_type:
            needle = event_type.lower()
            rows = [
                r for r in rows if needle in (r.get("EventType", "") or "").lower()
            ]
        return {"events": rows, "count": len(rows)}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_winter_road_conditions(
    area_name: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Winter road conditions (~1,121 segments) from 511 Alberta /winterroads.

    Uses `_511_get` (Pitfall 6: raw JSON list). Optional `area_name` performs a
    case-insensitive substring match on the `AreaName` field.

    Returns:
        `({"conditions": list[dict], "count": int}, was_cached)` with TTL=LIVE
        (5min — source refreshes every 5 minutes during winter operations).
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:winterroads:{area_name}"
    limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        rows = await _511_get("winterroads")
        if area_name:
            needle = area_name.lower()
            rows = [
                r for r in rows if needle in (r.get("AreaName", "") or "").lower()
            ]
        return {"conditions": rows, "count": len(rows)}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_traffic_cameras() -> tuple[dict[str, Any], bool]:
    """~376 traffic camera locations + snapshot URLs from 511 Alberta /cameras.

    Uses `_511_get` (Pitfall 6: raw JSON list). Each camera includes a Views
    array of snapshot URLs — the Views URLs are stable; the camera image bytes
    refresh continuously upstream.

    Returns:
        `({"cameras": list[dict], "count": int}, was_cached)` with TTL=MONTHLY
        (24h — camera locations are stable).
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:cameras"
    limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)

    async def _fetch() -> dict[str, Any]:
        await limiter.acquire()
        rows = await _511_get("cameras")
        return {"cameras": rows, "count": len(rows)}

    return await cached_fetch(cache_key, CACHE_TTL_MONTHLY, _fetch)


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
