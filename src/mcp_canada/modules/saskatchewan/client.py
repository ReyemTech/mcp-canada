"""Saskatchewan module client — async functions returning (data, was_cached) tuples.

Plans 02-05 fill bodies (this Wave 0 file defines helpers + all signatures):

  - Plan 02: fetch_search_datasets, fetch_dataset_details, fetch_query_dataset,
             fetch_organizations, fetch_categories
  - Plan 03: fetch_crop_yields, fetch_grain_elevators, fetch_mineral_mines
  - Plan 04: fetch_fire_bans, fetch_historic_wildfires, fetch_air_quality
  - Plan 05: fetch_wsa_stations, fetch_wsa_reservoirs

CRITICAL (Phase 15-05 contract — _hub_get MUST follow this):

  shared.http.api_get returns PARSED JSON (dict or list), NOT an httpx.Response.
  NEVER call `.raise_for_status()` or `.json()` on the return value.
  NEVER check `.get("success")` on ArcGIS Hub responses — Hub Search returns
  JSON directly (not CKAN envelope). The hub returns {"features": [...], "numberMatched": N}.

  _hub_get pattern:
    result = await api_get(HUB_SEARCH_URL, params, headers={...})
    if not isinstance(result, dict): raise httpx.HTTPStatusError(...)
    return result   # Hub returns dict directly with "features"/"numberMatched"

Saskatchewan-specific notes:
  - THREE ArcGIS bases: primary org (zcv98lgAl8xQ04cW), WSA org (7MBdlVpjqbfBhQer),
    SPSA egis (gis.saskatchewan.ca/egis/rest/services/Wildfire)
  - FIRE_BAN_LAYERS dispatch: {"urban":0, "rural":2, "provincial":3, "parks":8}
  - WSA_RESERVOIRS_LAYER = 26 (NOT 0 — spike-confirmed)
  - MINERAL_MINES_FS_URLS dispatch: potash/uranium/helium/coal → dated FeatureServers
  - NEVER reference data.saskatchewan.ca (domain does not exist)
"""

from __future__ import annotations

from typing import Any

import httpx

from mcp_canada.shared import arcgis_hub
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    AIR_QUALITY_FS_URL,  # noqa: F401
    CACHE_KEY_PREFIX,  # noqa: F401
    CACHE_TTL_ALERTS,  # noqa: F401
    CACHE_TTL_ANNUAL,  # noqa: F401
    CACHE_TTL_LIVE,  # noqa: F401
    CACHE_TTL_META,  # noqa: F401
    CACHE_TTL_SEARCH,  # noqa: F401
    CROP_YIELDS_PROVINCE_FS_URL,  # noqa: F401
    CROP_YIELDS_REGIONS_FS_URL,  # noqa: F401
    DEFAULT_PAGE_SIZE,  # noqa: F401
    FIRE_BAN_FS_URL,  # noqa: F401
    FIRE_BAN_LAYERS,  # noqa: F401
    GRAIN_ELEVATORS_FS_URL,  # noqa: F401
    HUB_SEARCH_URL,
    MAX_RECORDS,
    MINERAL_MINES_FS_URLS,  # noqa: F401
    RATE_GROUP_HUB,
    RATE_GROUP_SPSA,
    RATE_GROUP_WSA,
    RATE_LIMIT_HUB,
    RATE_LIMIT_SPSA,
    RATE_LIMIT_WSA,
    USER_AGENT,
    WILDFIRE_BOUNDARIES_FS_URL,  # noqa: F401
    WILDFIRE_ORIGINS_FS_URL,  # noqa: F401
    WSA_RESERVOIRS_FS_URL,  # noqa: F401
    WSA_RESERVOIRS_LAYER,  # noqa: F401
    WSA_STATIONS_FS_URL,  # noqa: F401
    WSA_STATIONS_LAYER,  # noqa: F401
)

from .schemas import (  # noqa: F401 — re-exported for downstream plans
    SaskatchewanAirQuality,
    SaskatchewanCategory,
    SaskatchewanCropYield,
    SaskatchewanDatasetDetails,
    SaskatchewanDatasetSummary,
    SaskatchewanFireBan,
    SaskatchewanGrainElevator,
    SaskatchewanMineralMine,
    SaskatchewanOrganization,
    SaskatchewanWildfire,
    SaskatchewanWSAReservoir,
    SaskatchewanWSAStation,
)

__all__ = [
    # Private helpers (fully implemented in Wave 0)
    "_hub_get",
    # Discovery (Plan 02)
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_query_dataset",
    "fetch_organizations",
    "fetch_categories",
    # Agriculture + Mining (Plan 03)
    "fetch_crop_yields",
    "fetch_grain_elevators",
    "fetch_mineral_mines",
    # Environment (Plan 04)
    "fetch_fire_bans",
    "fetch_historic_wildfires",
    "fetch_air_quality",
    # Water / WSA (Plan 05)
    "fetch_wsa_stations",
    "fetch_wsa_reservoirs",
]


# ---------------------------------------------------------------------------
# Module-level limiters (Wave 0 — shared by all downstream calls)
# ---------------------------------------------------------------------------

_hub_limiter = get_limiter(RATE_GROUP_HUB, RATE_LIMIT_HUB)
_wsa_limiter = get_limiter(RATE_GROUP_WSA, RATE_LIMIT_WSA)
_spsa_limiter = get_limiter(RATE_GROUP_SPSA, RATE_LIMIT_SPSA)


# ---------------------------------------------------------------------------
# Private helpers — fully implemented (Wave 0)
# ---------------------------------------------------------------------------


async def _hub_get(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """ArcGIS Hub Search API call against geohub.saskatchewan.ca.

    Saskatchewan's Hub Search returns JSON directly — NOT wrapped in a CKAN
    success/result envelope. Never call .get("success") on the result.

    Phase 15-05 contract: api_get returns parsed JSON. Do NOT call
    .raise_for_status() or .json() on the return value.

    OGC API Records format: {"type": "FeatureCollection", "numberMatched": N,
    "numberReturned": N, "features": [...]}
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


# ---------------------------------------------------------------------------
# Discovery — Plan 02 fills bodies
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search Saskatchewan GeoHub datasets via ArcGIS Hub Search API.

    Returns ({"results": [flat summaries], "total": N}, was_cached).
    OGC API Records params: limit (page size), startindex (offset in shared helper).
    Filled by Plan 02.
    """
    raise NotImplementedError("Plan 02 implements")


async def fetch_dataset_details(
    dataset_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch full metadata for a Saskatchewan GeoHub item by ID.

    Returns ({"details": {feature_server_url, download_urls, metadata}}, was_cached).
    Filled by Plan 02.
    """
    raise NotImplementedError("Plan 02 implements")


async def fetch_query_dataset(
    feature_server_url: str,
    layer_id: int = 0,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Query a Saskatchewan FeatureServer or auto-route to fetch_and_parse for file resources.

    Routing: FeatureServer URL → arcgis_hub.query_feature_service;
    CSV/JSON/GeoJSON/XLSX extension → fetch_and_parse; other → metadata-only.
    Filled by Plan 02.
    """
    raise NotImplementedError("Plan 02 implements")


async def fetch_organizations(
    num: int = DEFAULT_PAGE_SIZE,
) -> tuple[dict[str, Any], bool]:
    """List publishing organizations on the Saskatchewan GeoHub.

    Returns ({"organizations": [name, ...]}, was_cached).
    Derives unique owner names from Hub Search results.
    Filled by Plan 02.
    """
    raise NotImplementedError("Plan 02 implements")


async def fetch_categories(
) -> tuple[dict[str, Any], bool]:
    """List content categories on the Saskatchewan GeoHub.

    Returns ({"categories": ["/Categories/Environment", ...]}, was_cached).
    Derives unique category strings from Hub Search results.
    Filled by Plan 02.
    """
    raise NotImplementedError("Plan 02 implements")


# ---------------------------------------------------------------------------
# Agriculture + Mining — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_crop_yields(
    region: str = "provincial",
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch estimated crop yields by region from Saskatchewan FeatureServers.

    region: "provincial" → Province Summary FS; "southeast"/"southwest"/"central"/
    "northeast"/"northwest" → Regions Only FS.
    16 crop types: HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean, Pea, Lentil,
    Chickpea, Canary_seed, Flax, Winter_wheat, Fall_rye, Other_wheat_.
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


async def fetch_grain_elevators(
    railway: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch grain elevator locations in Saskatchewan from Western_Canada_Grain_Elevator_2024.

    Default filter: PR='SK' (Saskatchewan only).
    railway: optional filter on Railway field (CN, CP, SHORTLINE).
    Fields: Station, PR, Railway, Licensee, Elevator_type, Capacity_tonne.
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


async def fetch_mineral_mines(
    mineral: str,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch mineral mine records dispatched by mineral type to dated FeatureServers.

    mineral: one of "potash", "uranium", "helium", "coal" — routes to MINERAL_MINES_FS_URLS.
    Raises ValueError for unknown mineral (tool layer catches and maps to INVALID_INPUT).
    Fields: Commodity, Name, Status, Mine_Type, Company, Mine_Site, Regulation, DateOpened, Website.
    Filled by Plan 03.
    """
    raise NotImplementedError("Plan 03 implements")


# ---------------------------------------------------------------------------
# Environment — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_fire_bans(
    ban_scope: str = "urban",
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch current fire bans from SPSA Public_Fire_Ban FeatureServer (separate REST server).

    ban_scope dispatches to FIRE_BAN_LAYERS: "urban"→0, "rural"→2, "provincial"→3, "parks"→8.
    NOTE: SPSA uses gis.saskatchewan.ca/egis NOT the main Hub org.
    CRITICAL: empty features list [] is CORRECT when no bans active — NOT an error.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


async def fetch_historic_wildfires(
    year: int | None = None,
    cause: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch historic wildfire boundaries from Historic_Wildfire_Boundaries FeatureServer.

    year: optional integer year filter (e.g. 2017).
    cause: optional filter on CAUSE1 (Lightning/Human/Unknown).
    Fields: YEAR, FIRENAME, CAUSE1, HECTARES, STATUS, STARTDATE, OUTDATE, TYPE.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


async def fetch_air_quality(
    community: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch hourly ambient air quality readings from Hourly_Ambient_Air_Quality FeatureServer.

    community: optional filter (Regina/Saskatoon/Prince Albert/Estevan/Swift Current/Buffalo Narrows).
    Returns live current readings (15min cache TTL).
    Fields: COMMUNITY, STATIONID, PM2_5, NO2, O3, SO2, CO, H2S, AQHI (URL link), DATETIME.
    Filled by Plan 04.
    """
    raise NotImplementedError("Plan 04 implements")


# ---------------------------------------------------------------------------
# Water / WSA — Plan 05 fills bodies
# ---------------------------------------------------------------------------


async def fetch_wsa_stations(
    basin: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch WSA hydrometric gauging stations from Hydrometric_Gauging_Stations_V2 FeatureServer.

    Uses WSA org (7MBdlVpjqbfBhQer / services1.arcgis.com) — NOT the primary Hub org.
    Default where=Province='SK'; optional basin= filter on Major_Basin field.
    Fields: Station_Number, Station_Name, Province, Latitude, Longitude,
    Major_Basin, Station_Type, Station_Class, Operated_By, HyperLink_Graph.
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")


async def fetch_wsa_reservoirs(
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch WSA reservoir records from WSA_Reservoirs FeatureServer layer 26.

    Uses WSA org (7MBdlVpjqbfBhQer / services1.arcgis.com) — NOT the primary Hub org.
    CRITICAL: Layer 26 (NOT layer 0) — spike-confirmed 2026-06-15; layer 0 returns empty.
    Fields: Reservoir_Name, Dam_Name, Imagery_Date, Water_Level_MASL.
    Filled by Plan 05.
    """
    raise NotImplementedError("Plan 05 implements")
