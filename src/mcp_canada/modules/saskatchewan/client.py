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
# Discovery — Plan 02
# ---------------------------------------------------------------------------

# File extensions that fetch_and_parse can handle
_PARSEABLE_EXTENSIONS: frozenset[str] = frozenset(
    {".csv", ".json", ".geojson", ".xlsx", ".xls"}
)


def _is_feature_server_url(url: str) -> bool:
    """Return True when the URL points to an ArcGIS FeatureServer (not MapServer)."""
    return "/FeatureServer" in url


def _is_parseable_url(url: str) -> bool:
    """Return True when the URL extension is a format fetch_and_parse can handle."""
    clean = url.split("?", 1)[0].rstrip("/").lower()
    return any(clean.endswith(ext) for ext in _PARSEABLE_EXTENSIONS)


def _flatten_hub_feature(feature: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single Hub Search API feature into a SaskatchewanDatasetSummary dict."""
    props = feature.get("properties") or {}
    return {
        "id": feature.get("id", ""),
        "title": props.get("title", ""),
        "snippet": props.get("snippet"),
        "type": props.get("type"),
        "owner": props.get("owner"),
        "url": props.get("url"),
        "num_views": props.get("numViews"),
        "modified": props.get("modified"),
        "source": props.get("source"),
    }


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    category: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Search Saskatchewan GeoHub datasets via ArcGIS Hub Search API.

    Returns ({"results": [flat summaries], "total": N}, was_cached).
    OGC API Records params: limit (page size), startindex (offset in shared helper).
    Empty query omits 'q' (empty q -> HTTP 400 live). startindex omitted when 0
    (startindex=0 returns malformed body live).
    """
    # OGC API Records requires limit/startindex, NOT num/start (ArcGIS-REST).
    # Empty q="" causes HTTP 400 on the live OGC endpoint — omit when blank.
    params: dict[str, Any] = {"limit": min(max(limit, 1), 100)}
    if query:
        params["q"] = query                   # omit q when blank (empty q -> 400)
    if offset and offset > 0:
        params["startindex"] = offset         # 1-based; omit when 0 (startindex=0 invalid)
    if category:
        params["categories"] = category

    cache_key = f"{CACHE_KEY_PREFIX}search:{query}:{category}:{limit}:{offset}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        raw = await _hub_get(params)
        features = raw.get("features", [])
        total = raw.get("numberMatched", len(features))
        return {
            "results": [_flatten_hub_feature(f) for f in features],
            "total": total,
        }

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_dataset_details(
    dataset_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch full metadata for a Saskatchewan GeoHub item by ID.

    GETs /collections/all/items/{id}; returns
    ({"details": {feature_server_url, download_urls, metadata}}, was_cached).
    Raises ValueError if no item found.
    """
    cache_key = f"{CACHE_KEY_PREFIX}details:{dataset_id}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        item_url = f"{HUB_SEARCH_URL}/{dataset_id}"
        result = await api_get(
            item_url,
            {},
            headers={"User-Agent": USER_AGENT},
        )
        if isinstance(result, dict) and "properties" in result:
            # Single-item response shape (Hub item endpoint)
            raw = result
        elif isinstance(result, dict) and "features" in result:
            # Search-response shape — pick first matching feature
            features = result.get("features", [])
            if not features:
                raise ValueError(f"Dataset not found: {dataset_id}")
            raw = features[0]
        elif not isinstance(result, dict):
            raise httpx.HTTPStatusError(
                f"Hub returned non-dict for item {dataset_id}",
                request=httpx.Request("GET", item_url),
                response=httpx.Response(500),
            )
        else:
            raise ValueError(f"Dataset not found: {dataset_id}")

        props = raw.get("properties") or {}
        svc_url = props.get("url", "")
        # Detect FeatureServer URL
        feature_server_url: str | None = (
            svc_url if _is_feature_server_url(svc_url) else None
        )
        # Download URLs: parseable file extensions
        download_urls: list[str] = []
        links_raw = (result.get("links") or []) if isinstance(result, dict) else []
        for link in links_raw:
            href = link.get("href", "")
            if href and _is_parseable_url(href):
                download_urls.append(href)

        details = {
            "id": raw.get("id", dataset_id),
            "title": props.get("title", ""),
            "snippet": props.get("snippet"),
            "description": props.get("description"),
            "type": props.get("type"),
            "owner": props.get("owner"),
            "url": svc_url,
            "feature_server_url": feature_server_url,
            "download_urls": download_urls,
            "tags": props.get("tags") or [],
            "categories": props.get("categories") or [],
            "modified": props.get("modified"),
            "num_views": props.get("numViews"),
            "access": props.get("access"),
            "licence_info": props.get("licenseInfo"),
        }
        return {"details": details}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_query_dataset(
    feature_server_url: str,
    layer_id: int = 0,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Query a Saskatchewan FeatureServer or auto-route to fetch_and_parse for file resources.

    Routing:
      - URL contains /FeatureServer → arcgis_hub.query_feature_service
      - URL has CSV/JSON/GeoJSON/XLSX/XLS extension → fetch_and_parse
      - otherwise (PDF, ZIP, KML, WMS, …) → metadata-only response with 'note'
    """
    url = feature_server_url
    cache_key = (
        f"{CACHE_KEY_PREFIX}query:{url}:{layer_id}:{where}:"
        f"{out_fields}:{max_records}:{include_geometry}"
    )

    # FeatureServer branch
    if _is_feature_server_url(url):
        # Split trailing layer index if present (e.g. .../FeatureServer/0)
        base = url
        detected_layer = layer_id
        clean = url.rstrip("/")
        parts = clean.rsplit("/FeatureServer", 1)
        if len(parts) == 2:
            tail = parts[1].strip("/")
            base = parts[0] + "/FeatureServer"
            if tail:
                try:
                    detected_layer = int(tail.split("/")[0])
                except ValueError:
                    pass

        async def _fetch_fs() -> dict[str, Any]:
            await _hub_limiter.acquire()
            rows, truncated = await arcgis_hub.query_feature_service(
                base,
                detected_layer,
                where=where,
                out_fields=out_fields,
                include_geometry=include_geometry,
                max_records=max_records,
            )
            return {"data": rows, "url": url, "rows": len(rows), "truncated": truncated}

        return await cached_fetch(cache_key, CACHE_TTL_META, _fetch_fs)

    # Parseable file branch
    if _is_parseable_url(url):
        async def _fetch_file() -> dict[str, Any]:
            rows, _cached = await fetch_and_parse(url, ttl=CACHE_TTL_META)
            truncated = len(rows) > max_records
            return {
                "data": rows[:max_records],
                "url": url,
                "rows": min(len(rows), max_records),
                "truncated": truncated,
            }

        return await cached_fetch(cache_key, CACHE_TTL_META, _fetch_file)

    # Metadata-only fallback (PDF, ZIP, KML, WMS, etc.)
    return (
        {
            "url": url,
            "note": (
                "binary/archive resource — use URL directly or call "
                "saskatchewan_search_datasets to find a machine-readable format"
            ),
        },
        False,
    )


async def fetch_organizations(
    num: int = DEFAULT_PAGE_SIZE,
) -> tuple[dict[str, Any], bool]:
    """List publishing organizations on the Saskatchewan GeoHub.

    Returns ({"organizations": [name, ...]}, was_cached).
    Derives unique owner names from Hub Search results.
    """
    cache_key = f"{CACHE_KEY_PREFIX}orgs:all"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        # OGC API Records: use limit (not num/start); omit q (empty q -> 400)
        raw = await _hub_get({"limit": min(num, 100)})
        features = raw.get("features", [])
        owners: set[str] = set()
        for f in features:
            owner = (f.get("properties") or {}).get("owner")
            if owner:
                owners.add(owner)
        return {"organizations": sorted(owners)}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_categories(
) -> tuple[dict[str, Any], bool]:
    """List content categories on the Saskatchewan GeoHub.

    Returns ({"categories": ["/Categories/Environment", ...]}, was_cached).
    Derives unique category strings from Hub Search results.
    """
    cache_key = f"{CACHE_KEY_PREFIX}categories:all"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        # OGC API Records: use limit (not num/start); omit q (empty q -> 400)
        raw = await _hub_get({"limit": 100})
        features = raw.get("features", [])
        all_cats: set[str] = set()
        for f in features:
            cats = (f.get("properties") or {}).get("categories") or []
            all_cats.update(cats)
        return {"categories": sorted(all_cats)}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# Agriculture + Mining — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_crop_yields(
    region: str = "provincial",
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch estimated crop yields by region from Saskatchewan FeatureServers.

    region: "provincial" → Province Summary FS (where="1=1"); one of 5 non-provincial
    crop regions → Regions Only FS with where="Region='<Title-cased region>'".
    16 crop types: HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean, Pea, Lentil,
    Chickpea, Canary_seed, Flax, Winter_wheat, Fall_rye, Other_wheat_.
    Raises ValueError for unknown region (tool catches and returns INVALID_INPUT).
    """
    from .constants import CROP_REGIONS  # local import to keep module-level imports lean

    region_lower = region.lower()
    if region_lower not in CROP_REGIONS:
        raise ValueError(
            f"Unknown region: {region!r}. Valid: {list(CROP_REGIONS)}"
        )

    if region_lower == "provincial":
        fs_url = CROP_YIELDS_PROVINCE_FS_URL
        where = "1=1"
    else:
        fs_url = CROP_YIELDS_REGIONS_FS_URL
        where = f"Region='{region_lower.title()}'"

    # 16 crop fields + Region
    out_fields = (
        "Region,HRSW,Durum,Oat,Barley,Canola,Mustard,Soybean,Pea,Lentil,"
        "Chickpea,Canary_seed,Flax,Winter_wheat,Fall_rye,Other_wheat_"
    )
    cache_key = f"{CACHE_KEY_PREFIX}crop_yields:{region_lower}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            fs_url,
            layer_id=0,
            where=where,
            out_fields=out_fields,
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
            "region": region_lower,
        }

    return await cached_fetch(cache_key, CACHE_TTL_ANNUAL, _fetch)


async def fetch_grain_elevators(
    railway: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch grain elevator locations in Saskatchewan from Western_Canada_Grain_Elevator_2024.

    Default filter: PR='SK' (Saskatchewan only).
    railway: optional filter on Railway field (CN, CP, SHORTLINE).
    Fields: Station, PR, Railway, Licensee, Elevator_type, Capacity_tonne.
    """
    where = "PR='SK'"
    if railway:
        where += f" AND Railway='{railway}'"

    out_fields = "Station,PR,Railway,Licensee,Elevator_type,Capacity_tonne"
    cache_key = f"{CACHE_KEY_PREFIX}grain_elevators:{railway or 'all'}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            GRAIN_ELEVATORS_FS_URL,
            layer_id=0,
            where=where,
            out_fields=out_fields,
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_mineral_mines(
    mineral: str,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch mineral mine records dispatched by mineral type to dated FeatureServers.

    mineral: one of "potash", "uranium", "helium", "coal" — routes to MINERAL_MINES_FS_URLS.
    Raises ValueError for unknown mineral (tool layer catches and maps to INVALID_INPUT).
    Fields: Commodity, Name, Status, Mine_Type, Company, Mine_Site, Regulation, DateOpened, Website.
    """
    mineral_lower = mineral.lower()
    fs_url = MINERAL_MINES_FS_URLS.get(mineral_lower)
    if fs_url is None:
        raise ValueError(
            f"Unknown mineral: {mineral!r}. Valid: {list(MINERAL_MINES_FS_URLS)}"
        )

    out_fields = (
        "Commodity,Name,Status,Mine_Type,Company,Mine_Site,Regulation,DateOpened,Website"
    )
    cache_key = f"{CACHE_KEY_PREFIX}mineral_mines:{mineral_lower}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            fs_url,
            layer_id=0,
            where="1=1",
            out_fields=out_fields,
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
            "mineral": mineral_lower,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# Environment — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_fire_bans(
    ban_scope: str = "urban",
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch current fire bans from SPSA Public_Fire_Ban FeatureServer (separate REST server).

    ban_scope dispatches to FIRE_BAN_LAYERS: "urban"→0, "rural"→2, "provincial"→3, "parks"→8.
    NOTE: SPSA uses gis.saskatchewan.ca/egis NOT the main Hub org — FIRE_BAN_FS_URL directly.
    CRITICAL: empty features list [] is CORRECT when no bans are active (off-season) — NOT an error.
    Same pattern as Manitoba flood alerts (Phase 18).
    """
    if ban_scope not in FIRE_BAN_LAYERS:
        raise ValueError(
            f"Unknown ban_scope: {ban_scope!r}. Valid: {list(FIRE_BAN_LAYERS)}"
        )

    layer_id = FIRE_BAN_LAYERS[ban_scope]
    cache_key = f"{CACHE_KEY_PREFIX}fire_bans:{ban_scope}"

    async def _fetch() -> dict[str, Any]:
        await _spsa_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            FIRE_BAN_FS_URL,
            layer_id,
            where="1=1",
            out_fields="UMTYPE,Municipali,Fire_Depar,Start_Date,Contact_Nu,Type,Comment",
            include_geometry=False,
            max_records=max_records,
        )
        # Empty features is VALID (no active bans in off-season) — never an error
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
            "scope": ban_scope,
        }

    return await cached_fetch(cache_key, CACHE_TTL_ALERTS, _fetch)


async def fetch_historic_wildfires(
    year: int | None = None,
    cause: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch historic wildfire boundaries from Historic_Wildfire_Boundaries FeatureServer.

    year: optional integer year filter (e.g. 2017) → WHERE YEAR=<int>.
    cause: optional filter on CAUSE1 (Lightning/Human/Unknown) → CAUSE1 LIKE '%..%'.
    Composed with AND when both provided; "1=1" when neither.
    Fields: YEAR, FIRENAME, CAUSE1, HECTARES, STATUS, STARTDATE, OUTDATE, TYPE.
    """
    # Build WHERE clause
    clauses: list[str] = []
    if year is not None:
        clauses.append(f"YEAR={year}")
    if cause is not None:
        clauses.append(f"CAUSE1 LIKE '%{cause}%'")
    where = " AND ".join(clauses) if clauses else "1=1"

    cache_key = f"{CACHE_KEY_PREFIX}wildfires:{year}:{cause}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            WILDFIRE_BOUNDARIES_FS_URL,
            0,
            where=where,
            out_fields="YEAR,FIRENAME,CAUSE1,HECTARES,STATUS,STARTDATE,OUTDATE,TYPE",
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_air_quality(
    community: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch hourly ambient air quality readings from Hourly_Ambient_Air_Quality FeatureServer.

    community: optional filter (Regina/Saskatoon/Prince Albert/Estevan/Swift Current/Buffalo Narrows).
    Returns live current readings (15min cache TTL — data refreshes hourly on the FeatureServer).
    AQHI field is a weather.gc.ca URL link (not a numeric value).
    Fields: COMMUNITY, STATIONID, PM2_5, NO2, O3, PM10, SO2, CO, H2S, AQHI, DATETIME.
    """
    where = f"COMMUNITY='{community}'" if community else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}air_quality:{community or 'all'}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            AIR_QUALITY_FS_URL,
            0,
            where=where,
            out_fields=(
                "COMMUNITY,STATIONID,PM2_5,NO2,O3,PM10,SO2,CO,H2S,AQHI,DATETIME"
            ),
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


# ---------------------------------------------------------------------------
# Water / WSA — Plan 05 fills bodies
# ---------------------------------------------------------------------------


async def fetch_wsa_stations(
    basin: str | None = None,
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch WSA hydrometric gauging stations from Hydrometric_Gauging_Stations_V2 FeatureServer.

    Uses WSA org (7MBdlVpjqbfBhQer / services1.arcgis.com) — NOT the primary Hub org.
    Default where=Province='SK'; optional basin= filter on Major_Basin field (LIKE).
    Fields: Station_Number, Station_Name, Province, Latitude, Longitude,
    Major_Basin, Station_Type, Station_Class, Operated_By, HyperLink_Graph.
    HyperLink_Graph links to live hourly hydrographs at wsask.ca.
    """
    where = "Province='SK'"
    if basin:
        where += f" AND Major_Basin LIKE '%{basin}%'"
    cache_key = f"{CACHE_KEY_PREFIX}wsa:stations:{basin or 'all'}"

    async def _fetch() -> dict[str, Any]:
        await _wsa_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            WSA_STATIONS_FS_URL,
            WSA_STATIONS_LAYER,
            where=where,
            out_fields=(
                "Station_Number,Station_Name,Province,Latitude,Longitude,"
                "Major_Basin,Station_Type,Station_Class,Operated_By,HyperLink_Graph"
            ),
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_wsa_reservoirs(
    max_records: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch WSA reservoir records from WSA_Reservoirs FeatureServer layer 26.

    Uses WSA org (7MBdlVpjqbfBhQer / services1.arcgis.com) — NOT the primary Hub org.
    CRITICAL: Layer 26 (NOT layer 0) — spike-confirmed 2026-06-15; layer 0 returns empty.
    WSA_RESERVOIRS_LAYER constant (=26) must be used; never hardcode layer 0 for reservoirs.
    Fields: Reservoir_Name, Dam_Name, Imagery_Date, Water_Level_MASL.
    """
    cache_key = f"{CACHE_KEY_PREFIX}wsa:reservoirs:all"

    async def _fetch() -> dict[str, Any]:
        await _wsa_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            WSA_RESERVOIRS_FS_URL,
            WSA_RESERVOIRS_LAYER,  # 26 — NOT 0 (layer 0 is empty, spike-confirmed)
            where="1=1",
            out_fields="Reservoir_Name,Dam_Name,Imagery_Date,Water_Level_MASL",
            include_geometry=False,
            max_records=max_records,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
