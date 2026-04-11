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
    BASE_URL,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    DEFAULT_HEADERS,
    RATE_GROUP,
    RATE_LIMIT,
)
from .schemas import (
    QuebecCategory,
    QuebecDatasetDetails,
    QuebecDatasetSummary,
    QuebecOrganization,
    QuebecResource,
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


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Quebec CKAN envelope unwrap helper.

    CRITICAL: shared api_get already returns PARSED JSON (dict). NEVER call
    .raise_for_status() or .json() on the return value. This is the Phase 15 fix
    (see debug/resolved/bc-api-get-dict-mismatch.md).

    Args:
        path: Action API path (e.g. "package_search") relative to BASE_URL.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN result field (dict or list wrapped in a dict).

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
            g.get("name")
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
# Health / MSSS — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_health_installations(
    installation_type: str | None = None,
    region: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """MSSS health installations via datastore_search — Plan 03 implements.

    installation_type: 'clsc', 'hospital', 'chsld', 'chpsy', or None for all.
    """
    raise NotImplementedError("Plan 03 implements fetch_health_installations")


async def fetch_er_wait_times(
    q: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """MSSS ER hourly wait times via datastore_search — Plan 03 implements.

    116 rows (one per ER department), updated hourly.
    """
    raise NotImplementedError("Plan 03 implements fetch_er_wait_times")


async def fetch_population_by_municipality(
    region: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """MAMH municipality registry via fetch_and_parse(MAMH_MUN_CSV_URL) — Plan 03 implements.

    1,282 rows. Optional region filter on regadm (administrative region code).
    """
    raise NotImplementedError("Plan 03 implements fetch_population_by_municipality")


# ---------------------------------------------------------------------------
# Transport / MTQ — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_road_conditions(
    route: str | None = None,
    region: str | None = None,
    limit: int = 200,
) -> tuple[list[dict[str, Any]], bool]:
    """MTQ road conditions via WFS CSV (ms:conditions_routieres) — Plan 03 implements.

    LOW confidence on live WFS for this layer — test during implementation.
    Bilingual columns: DescriptionEtatChausseeFR/EN, DescriptionVisibiliteFR/EN.
    """
    raise NotImplementedError("Plan 03 implements fetch_road_conditions")


async def fetch_road_works(
    route: str | None = None,
    limit: int = 200,
) -> tuple[list[dict[str, Any]], bool]:
    """MTQ active road construction zones via WFS CSV (ms:chantiers_mtmdet) — Plan 03 implements.

    Confirmed working. Bilingual: descriptionFrancais / descriptionAnglais.
    """
    raise NotImplementedError("Plan 03 implements fetch_road_works")


async def fetch_road_events(
    route: str | None = None,
    limit: int = 200,
) -> tuple[list[dict[str, Any]], bool]:
    """MTQ active road events/warnings via WFS CSV (ms:evenements) — Plan 03 implements.

    French-only columns in this CSV — no English equivalent available.
    """
    raise NotImplementedError("Plan 03 implements fetch_road_events")


async def fetch_bridge_structures(
    route: str | None = None,
    municipality: str | None = None,
    structure_type: str | None = None,
    limit: int = 500,
) -> tuple[list[dict[str, Any]], bool]:
    """MTQ bridge inventory via WFS CSV (ms:gsq_v_desc_strct_tri) — Plan 03 implements.

    ~50K+ structures. At least one filter REQUIRED to avoid unbounded response.
    Use same guard pattern as bc_get_water_wells.
    """
    raise NotImplementedError("Plan 03 implements fetch_bridge_structures")


# ---------------------------------------------------------------------------
# Environment / Demographics / Energy — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_forest_fires_history() -> tuple[dict[str, Any], bool]:
    """MFFP/MRN forest fire archive metadata — Plan 04 implements.

    Returns CKAN package metadata + resource URLs (SHP/GPKG only — not parseable
    by fetch_and_parse). Metadata/discovery tool, not data extraction tool.
    """
    raise NotImplementedError("Plan 04 implements fetch_forest_fires_history")


async def fetch_air_quality_stations(
    active_only: bool = True,
) -> tuple[list[dict[str, Any]], bool]:
    """RSQAQ air quality stations via datastore_search — Plan 04 implements.

    245 rows total (active + closed). active_only=True filters DATE_FERMETURE=None.
    """
    raise NotImplementedError("Plan 04 implements fetch_air_quality_stations")


async def fetch_air_quality_index(
    limit: int = 200,
) -> tuple[list[dict[str, Any]], bool]:
    """MELCCFP air quality index via ArcGIS FeatureServer — Plan 04 implements.

    Source: AQ_INDEX_URL (ArcGIS REST, not CKAN datastore).
    Use api_get with ?f=json&where=1=1&outFields=*&resultRecordCount={limit}.
    """
    raise NotImplementedError("Plan 04 implements fetch_air_quality_index")


async def fetch_water_quality_monitoring() -> tuple[dict[str, Any], bool]:
    """MELCCFP water quality monitoring metadata — Plan 04 implements.

    Returns CKAN package metadata + download URLs (GeoJSON ZIP — not directly
    parseable by fetch_and_parse). Metadata/discovery tool.
    """
    raise NotImplementedError("Plan 04 implements fetch_water_quality_monitoring")


async def fetch_electricity_data() -> tuple[list[dict[str, Any]], bool]:
    """Hydro-Québec historical electricity production/consumption — Plan 04 implements.

    Source: historique-production-consommation (CSV via fetch_and_parse).
    Note: Current outages are NOT on DQ CKAN — redirect agents to hydroquebec.com/pannes/.
    """
    raise NotImplementedError("Plan 04 implements fetch_electricity_data")


async def fetch_protected_areas() -> tuple[dict[str, Any], bool]:
    """MELCCFP protected areas metadata — Plan 04 implements.

    Returns CKAN package metadata + resource URLs (SHP/GPKG/FGDB — not parseable
    by fetch_and_parse). Metadata/discovery tool.
    """
    raise NotImplementedError("Plan 04 implements fetch_protected_areas")
