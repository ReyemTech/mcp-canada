"""Quebec module client — async functions returning (data, was_cached) tuples.

ALL functions are stubs raising NotImplementedError.
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

from typing import Any

from mcp_canada.shared.http import api_get  # REAL import — do NOT shadow with local alias

from .constants import BASE_URL, DEFAULT_HEADERS  # noqa: F401 — Plan 02 uses these

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


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """CKAN envelope unwrap helper — Plan 02 implements correctly (parsed-dict contract).

    Calls BASE_URL + path, passes DEFAULT_HEADERS, unwraps result.
    Raises httpx.HTTPStatusError on success=False or non-dict return.
    """
    raise NotImplementedError("Plan 02 implements _api_get")


async def _datastore_get(
    resource_id: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Datastore search helper — Plan 02 implements.

    Calls datastore_search with resource_id and optional params.
    Returns the unwrapped result dict (records, total, fields).
    """
    raise NotImplementedError("Plan 02 implements _datastore_get")


# ---------------------------------------------------------------------------
# Discovery client functions — Plan 02 fills bodies
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    q: str = "",
    rows: int = 10,
    start: int = 0,
    organization: str | None = None,
    group: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Search Données Québec CKAN catalogue — Plan 02 implements."""
    raise NotImplementedError("Plan 02 implements fetch_search_datasets")


async def fetch_dataset_details(package_id: str) -> tuple[dict[str, Any], bool]:
    """Get full dataset details (package_show) — Plan 02 implements."""
    raise NotImplementedError("Plan 02 implements fetch_dataset_details")


async def fetch_organizations() -> tuple[list[dict[str, Any]], bool]:
    """Get all 139 Données Québec organizations — Plan 02 implements."""
    raise NotImplementedError("Plan 02 implements fetch_organizations")


async def fetch_categories() -> tuple[list[dict[str, Any]], bool]:
    """Get 10 thematic groups via group_list — Plan 02 implements.

    Uses group_list (not tag_list) — DQ has 10 meaningful thematic groups.
    BC returns HTTP 403 on group_list; DQ does not.
    """
    raise NotImplementedError("Plan 02 implements fetch_categories")


async def fetch_query_dataset(
    package_id: str,
    q: str = "",
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], bool]:
    """Pick best file resource or route to datastore — Plan 02 implements.

    Routing logic: if resource has datastore_active=True, use _datastore_get.
    Otherwise pick best file resource (CSV > GeoJSON > JSON > XLSX) and
    delegate to fetch_and_parse().
    """
    raise NotImplementedError("Plan 02 implements fetch_query_dataset")


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
