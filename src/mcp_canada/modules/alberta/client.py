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


async def fetch_search_datasets(
    q: str = "",
    organization: str | None = None,
    format: str | None = None,
    rows: int = 10,
    start: int = 0,
) -> tuple[list[AlbertaDatasetSummary], bool]:
    """Search Alberta's open.alberta.ca CKAN catalogue (33,269 datasets). Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_dataset_details(package_id: str) -> tuple[AlbertaDatasetDetails, bool]:
    """Full dataset record (flat) — hides 50+ publication-identifier extras. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_query_dataset(
    package_id: str,
    resource_index: int = 0,
    where: str | None = None,
    max_records: int = 1000,
) -> tuple[dict[str, Any], bool]:
    """Query a dataset resource — auto-routes ESRI REST -> arcgis_hub, CSV/XLSX/JSON -> fetch_and_parse. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_organizations() -> tuple[list[AlbertaOrganization], bool]:
    """List all 370 organizations publishing on open.alberta.ca. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_format_categories() -> tuple[list[AlbertaCategory], bool]:
    """List dataset format categories from the res_format facet (NOT group_list — Pitfall 1). Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


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
