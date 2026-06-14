"""Manitoba module client — async functions returning (data, was_cached) tuples.

Plans 02-06 fill bodies (this Wave 0 file defines helpers + all signatures):

  - Plan 02: fetch_search_datasets, fetch_dataset_details, fetch_query_dataset,
             fetch_organizations, fetch_categories
  - Plan 03: fetch_flood_alerts, fetch_river_stations, fetch_provincial_waterways
  - Plan 04: fetch_drought_status, fetch_ag_weather_stations, fetch_livestock_prices,
             fetch_crop_regions
  - Plan 05: fetch_provincial_parks, fetch_fisheries_data, fetch_provincial_forests,
             fetch_surgical_wait_times, fetch_health_facilities
  - Plan 06: fetch_road_events, fetch_winter_road_conditions, fetch_traffic_cameras

CRITICAL (Phase 15-05 contract — _hub_get MUST follow this):

  shared.http.api_get returns PARSED JSON (dict or list), NOT an httpx.Response.
  NEVER call `.raise_for_status()` or `.json()` on the return value.
  NEVER check `.get("success")` on ArcGIS Hub responses — Hub Search returns
  JSON directly (not CKAN envelope).

  _hub_get pattern:
    result = await api_get(HUB_SEARCH_URL, params, headers={...})
    if not isinstance(result, dict): raise httpx.HTTPStatusError(...)
    return result   # Hub returns dict directly with "features"/"results" list

  _511_get pattern:
    rows = await api_get(url, params, headers={...})
    return rows if isinstance(rows, list) else []  # 511 returns raw JSON list
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from mcp_canada.shared import arcgis_hub  # noqa: F401 — used by Plans 03/04/05
from mcp_canada.shared.cache import cached_fetch  # noqa: F401 — used by Plans 02-06
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse  # noqa: F401 — used by Plans 02/03
from mcp_canada.shared.rate_limiter import get_limiter  # noqa: F401 — used by Plans 02-06

from .constants import (
    CACHE_KEY_PREFIX,  # noqa: F401
    CACHE_TTL_ANNUAL,  # noqa: F401
    CACHE_TTL_LIVE,  # noqa: F401
    CACHE_TTL_META,  # noqa: F401
    CACHE_TTL_SEARCH,  # noqa: F401
    CACHE_TTL_STATIC,  # noqa: F401
    CATTLE_PRICES_FS_URL,  # noqa: F401
    CROP_REGIONS_FS_URL,  # noqa: F401
    DEFAULT_PAGE_SIZE,  # noqa: F401
    DROUGHT_MONITOR_FS_URL,  # noqa: F401
    FIVE11_BASE_URL,
    FIVE11_KEY_ENV,
    FLOOD_ALERTS_FS_URL,  # noqa: F401
    HOG_PRICES_FS_URL,  # noqa: F401
    HUB_SEARCH_URL,
    MANITOBA_BBOX,  # noqa: F401
    MAX_RECORDS,
    PROVINCIAL_FORESTS_FS_URL,  # noqa: F401
    PROVINCIAL_PARKS_FS_URL,  # noqa: F401
    PROVINCIAL_WATERWAYS_FS_URL,  # noqa: F401
    RATE_GROUP_511,
    RATE_GROUP_HUB,
    RATE_LIMIT_511,
    RATE_LIMIT_HUB,
    RIVER_CONDITIONS_CSV_URL,  # noqa: F401
    RURAL_HEALTH_FACILITIES_FS_URL,  # noqa: F401
    SURGICAL_WAIT_TIMES_FS_URL,  # noqa: F401
    USER_AGENT,
    WATERBODY_DATA_FS_URL,  # noqa: F401
    AG_WEATHER_STATIONS_FS_URL,  # noqa: F401
)

from .schemas import (  # noqa: F401 — re-exported for downstream plans
    Manitoba511Camera,
    Manitoba511Event,
    Manitoba511WinterRoad,
    ManitobaAgWeatherStation,
    ManitobaCategory,
    ManitobaCropRegion,
    ManitobaDatasetDetails,
    ManitobaDatasetSummary,
    ManitobaDroughtPolygon,
    ManitobaFloodAlert,
    ManitobaForest,
    ManitobaHealthFacility,
    ManitobaLivestockPrice,
    ManitobaOrganization,
    ManitobaPark,
    ManitobaRiverStation,
    ManitobaWaitTime,
    ManitobaWaterbody,
    ManitobaWaterway,
)

__all__ = [
    # Private helpers (fully implemented in Wave 0)
    "_hub_get",
    "_511_get",
    "Five11NotConfigured",
    # Discovery (Plan 02)
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_query_dataset",
    "fetch_organizations",
    "fetch_categories",
    # Flood / hydrology (Plan 03)
    "fetch_flood_alerts",
    "fetch_river_stations",
    "fetch_provincial_waterways",
    # Agriculture / drought (Plan 04)
    "fetch_drought_status",
    "fetch_ag_weather_stations",
    "fetch_livestock_prices",
    "fetch_crop_regions",
    # Environment / parks / health (Plan 05)
    "fetch_provincial_parks",
    "fetch_fisheries_data",
    "fetch_provincial_forests",
    "fetch_surgical_wait_times",
    "fetch_health_facilities",
    # Transport / 511 (Plan 06)
    "fetch_road_events",
    "fetch_winter_road_conditions",
    "fetch_traffic_cameras",
]


# ---------------------------------------------------------------------------
# Exception for missing 511 key
# ---------------------------------------------------------------------------


class Five11NotConfigured(Exception):
    """Raised when MANITOBA_511_KEY env var is not set."""


# ---------------------------------------------------------------------------
# Private helpers — fully implemented (Wave 0)
# ---------------------------------------------------------------------------


async def _hub_get(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """ArcGIS Hub Search API call against geoportal.gov.mb.ca.

    Manitoba's Hub Search returns JSON directly — NOT wrapped in a CKAN
    success/result envelope. Never call .get("success") on the result.

    Phase 15-05 contract: api_get returns parsed JSON. Do NOT call
    .raise_for_status() or .json() on the return value.
    """
    result = await api_get(
        HUB_SEARCH_URL,
        params or {},
        headers={"User-Agent": USER_AGENT},
    )
    if not isinstance(result, dict):
        raise httpx.HTTPStatusError(
            f"Hub returned non-dict response (got {type(result).__name__})",
            request=httpx.Request("GET", HUB_SEARCH_URL),
            response=httpx.Response(500),
        )
    return result


async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict]:
    """Manitoba 511 REST API v3 call. Returns raw JSON list.

    GATED: requires MANITOBA_511_KEY environment variable.
    If key is absent, raises Five11NotConfigured.
    Tool layer catches Five11NotConfigured and returns make_error("NOT_CONFIGURED").

    511 returns a JSON list at the top level — NOT an ArcGIS/CKAN envelope.
    """
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured(
            "MANITOBA_511_KEY not set. Register at https://www.manitoba511.ca/my511/register "
            "then request a developer API key."
        )
    rows = await api_get(
        f"{FIVE11_BASE_URL}/{endpoint}",
        {**(params or {}), "key": key, "format": "json"},
        headers={"User-Agent": USER_AGENT},
    )
    return rows if isinstance(rows, list) else []


# ---------------------------------------------------------------------------
# Module-level limiters (Wave 0 — shared by all downstream calls)
# ---------------------------------------------------------------------------

_hub_limiter = get_limiter(RATE_GROUP_HUB, RATE_LIMIT_HUB)
_511_limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)


# ---------------------------------------------------------------------------
# Discovery — Plan 02 fills bodies
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str,
    category: str | None = None,
    num: int = DEFAULT_PAGE_SIZE,
    start: int = 0,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Search Manitoba geoportal datasets via ArcGIS Hub Search API. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_dataset_details(
    item_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full metadata for a Manitoba geoportal item by ID. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_query_dataset(
    feature_server_url: str,
    layer_id: int = 0,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Query a Manitoba FeatureServer or parse a file resource. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_organizations(
    num: int = DEFAULT_PAGE_SIZE,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """List publishing organizations on the Manitoba geoportal. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


async def fetch_categories(
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """List content categories/tags on the Manitoba geoportal. Filled by Plan 02."""
    raise NotImplementedError("Plan 02 implements")


# ---------------------------------------------------------------------------
# Flood / Hydrology — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_flood_alerts(
    include_geometry: bool = True,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch active overland flood alerts from Overland_Flood_Alerts FeatureServer.

    Returns {"features": [...], "count": N, "truncated": False} payload.
    IMPORTANT: empty features list [] is CORRECT when no alerts are active — not an error.
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


async def fetch_river_stations(
    province: str | None = None,
    alert_only: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba river/hydrometric station data from live CSV.

    Source: RIVER_CONDITIONS_CSV_URL (www.manitoba.ca/floodinfo/.../agoldataV2.csv)
    Uses fetch_and_parse (CSV), NOT arcgis_hub.query_feature_service.
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


async def fetch_provincial_waterways(
    f_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba provincial waterways from Provincial_Waterways FeatureServer.

    f_type: "dike" | "floodway" | "dam" | "diversion" | "reservoir" | "waterway"
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


# ---------------------------------------------------------------------------
# Agriculture / Drought — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_drought_status(
    filter_province: bool = True,
    dm_level: str | None = None,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba drought monitor polygons from Canada_USA_Drought_Monitor FeatureServer.

    filter_province=True applies Manitoba bbox (-101.36,48.99,-95.15,60.0) (Pitfall 8).
    dm_level: None returns all, or one of "D0"/"D1"/"D2"/"D3"/"D4".
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


async def fetch_ag_weather_stations(
    ag_region: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba agricultural weather station locations from WeatherStations FeatureServer.

    ag_region: optional filter by AgRegion field value.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


async def fetch_livestock_prices(
    livestock: str = "cattle",
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba livestock market prices from MB_Cattle_Prices_Current_year FeatureServer.

    livestock: "cattle" | "hog" — note hog prices FS unresolved in Wave 0 spike.
    Plan 04 investigates whether cattle FeatureServer contains hog data too.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


async def fetch_crop_regions(
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba crop reporting region boundaries from MbAg_Crop_Reporting_Regions FeatureServer.

    Bilingual REGION (EN) and RÉGION (FR) fields.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


# ---------------------------------------------------------------------------
# Environment / Parks / Health — Plan 05 fills bodies
# ---------------------------------------------------------------------------


async def fetch_provincial_parks(
    park_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba provincial parks from Manitoba_Parks FeatureServer.

    park_type: one of PARK_TYPES tuple values or None for all 93 parks.
    Bilingual NAME_E/NOM_F fields.
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_fisheries_data(
    name_query: str | None = None,
    fishing_division: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba waterbody/fisheries data from Manitoba_Waterbody_Data FeatureServer.

    350+ water bodies with fishing regulations, species, stocking records, Secchi depth.
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_provincial_forests(
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba provincial forests from Manitoba_Provincial_Forests___Version_6 FeatureServer.

    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_surgical_wait_times(
    year: int | None = None,
    procedure: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba diagnostic/surgical wait time averages from FeatureServer.

    Annual averages by Year and IndicatorDataArea (procedure type).
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_health_facilities(
    community: str | None = None,
    emergency_only: bool = False,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba rural health care facilities from FeatureServer.

    Spike-resolved URL: Rural_Health_Care_Facilities_in_Manitoba/FeatureServer/0
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


# ---------------------------------------------------------------------------
# Transport / 511 — Plan 06 fills bodies
# ---------------------------------------------------------------------------


async def fetch_road_events(
    event_type: str | None = None,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch current road events from Manitoba 511 API v3 /events endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Returns raw list of event dicts.
    Filled by Plan 06.
    """
    raise NotImplementedError("Plan 06 implements")


async def fetch_winter_road_conditions(
    area_name: str | None = None,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch winter road conditions from Manitoba 511 API v3 /winterroads endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Seasonal — returns [] outside winter road season.
    Filled by Plan 06.
    """
    raise NotImplementedError("Plan 06 implements")


async def fetch_traffic_cameras(
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch traffic camera locations from Manitoba 511 API v3 /cameras endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Camera locations are stable — cached 24h.
    Filled by Plan 06.
    """
    raise NotImplementedError("Plan 06 implements")
