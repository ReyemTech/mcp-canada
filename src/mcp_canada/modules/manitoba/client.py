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

from mcp_canada.shared import arcgis_hub
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse
from mcp_canada.shared.rate_limiter import get_limiter

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
    FLOOD_ALERTS_FS_URL,
    HOG_PRICES_FS_URL,  # noqa: F401
    HUB_SEARCH_URL,
    MANITOBA_BBOX,  # noqa: F401
    MAX_RECORDS,
    PROVINCIAL_FORESTS_FS_URL,  # noqa: F401
    PROVINCIAL_PARKS_FS_URL,  # noqa: F401
    PROVINCIAL_WATERWAYS_FS_URL,
    RATE_GROUP_511,
    RATE_GROUP_HUB,
    RATE_LIMIT_511,
    RATE_LIMIT_HUB,
    RIVER_CONDITIONS_CSV_URL,
    RURAL_HEALTH_FACILITIES_FS_URL,  # noqa: F401
    SURGICAL_WAIT_TIMES_FS_URL,  # noqa: F401
    USER_AGENT,
    WATERBODY_DATA_FS_URL,  # noqa: F401
    AG_WEATHER_STATIONS_FS_URL,  # noqa: F401
    WATERWAY_TYPES,
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
# Discovery — Plan 02
# ---------------------------------------------------------------------------

# File extensions/URL patterns that fetch_and_parse can handle
_PARSEABLE_EXTENSIONS: frozenset[str] = frozenset(
    {".csv", ".json", ".geojson", ".xlsx", ".xls"}
)
_PARSEABLE_FORMATS: frozenset[str] = frozenset(
    {"CSV", "JSON", "GEOJSON", "XLSX", "XLS"}
)


def _is_feature_server_url(url: str) -> bool:
    """Return True when the URL points to an ArcGIS FeatureServer (not MapServer)."""
    return "/FeatureServer" in url


def _is_parseable_url(url: str) -> bool:
    """Return True when the URL extension is a format fetch_and_parse can handle."""
    clean = url.split("?", 1)[0].rstrip("/").lower()
    return any(clean.endswith(ext) for ext in _PARSEABLE_EXTENSIONS)


def _flatten_hub_feature(feature: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single Hub Search API feature into a ManitobaDatasetSummary dict."""
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
    query: str,
    category: str | None = None,
    num: int = DEFAULT_PAGE_SIZE,
    start: int = 0,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Search Manitoba geoportal datasets via ArcGIS Hub Search API.

    Returns ({"results": [flat summaries], "total": N}, was_cached).
    OGC API Records params (NOT ArcGIS-REST): limit (page size), startindex
    (1-based offset; omitted when 0), q (keyword; omitted when blank).
    Public signature retains num/start for API stability.
    """
    # OGC API Records requires limit/startindex, NOT num/start (ArcGIS-REST).
    # Empty q="" causes HTTP 400 on the live OGC endpoint — omit when blank.
    params: dict[str, Any] = {"limit": min(max(num, 1), 100)}
    if query:
        params["q"] = query                   # omit q when blank (empty q -> 400)
    if start and start > 0:
        params["startindex"] = start          # 1-based; omit when 0 (startindex=0 invalid)
    if category:
        params["categories"] = category

    cache_key = f"{CACHE_KEY_PREFIX}search:{query}:{category}:{num}:{start}"

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
    item_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full metadata for a Manitoba geoportal item by ID.

    Searches Hub by exact item_id match. Returns
    ({"details": {feature_server_url, download_urls, metadata}}, was_cached).
    Raises ValueError if no item found.
    """
    cache_key = f"{CACHE_KEY_PREFIX}details:{item_id}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        # Hub item detail: search by id
        item_url = f"{HUB_SEARCH_URL}/{item_id}"
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
                raise ValueError(f"Dataset not found: {item_id}")
            raw = features[0]
        elif not isinstance(result, dict):
            raise httpx.HTTPStatusError(
                f"Hub returned non-dict for item {item_id}",
                request=httpx.Request("GET", item_url),
                response=httpx.Response(500),
            )
        else:
            raise ValueError(f"Dataset not found: {item_id}")

        props = raw.get("properties") or {}
        svc_url = props.get("url", "")
        # Detect FeatureServer URL
        feature_server_url: str | None = svc_url if _is_feature_server_url(svc_url) else None
        # Download URLs: links with rel=download or parseable extensions
        download_urls: list[str] = []
        links_raw = (result.get("links") or []) if isinstance(result, dict) else []
        for link in links_raw:
            href = link.get("href", "")
            if href and _is_parseable_url(href):
                download_urls.append(href)

        details = {
            "id": raw.get("id", item_id),
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
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Query a Manitoba FeatureServer or parse a file resource via auto-router.

    Routing:
      - URL contains /FeatureServer → arcgis_hub.query_feature_service
      - URL has CSV/JSON/GeoJSON/XLSX/XLS extension → fetch_and_parse
      - otherwise (PDF, ZIP, KML, WMS, …) → metadata-only response with 'note'
    """
    url = feature_server_url
    cache_key = f"{CACHE_KEY_PREFIX}query:{url}:{layer_id}:{where}:{out_fields}:{max_records}:{include_geometry}"

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
            "note": "binary/archive resource — use URL directly or call manitoba_search_datasets to find a machine-readable format",
        },
        False,
    )


async def fetch_organizations(
    num: int = DEFAULT_PAGE_SIZE,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """List publishing organizations on the Manitoba geoportal.

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
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """List content categories/tags on the Manitoba geoportal.

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
# Flood / Hydrology — Plan 03 fills bodies
# ---------------------------------------------------------------------------


async def fetch_flood_alerts(
    include_geometry: bool = True,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch active overland flood alerts from Overland_Flood_Alerts FeatureServer.

    Returns {"features": [...], "count": N, "truncated": bool} payload.
    CRITICAL: empty features list [] is CORRECT when no alerts are active — not an error.
    Layer 0 fields: OBJECTID, Type_EN, Type_FR, Start_Date, End_Date, Shape__Area.
    """
    cache_key = f"{CACHE_KEY_PREFIX}flood_alerts:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            FLOOD_ALERTS_FS_URL,
            layer_id=0,
            where="1=1",
            out_fields="Type_EN,Type_FR,Start_Date,End_Date,Shape__Area",
            include_geometry=include_geometry,
            max_records=MAX_RECORDS,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_river_stations(
    province: str | None = None,
    alert_only: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba river/hydrometric station data from live CSV.

    Source: RIVER_CONDITIONS_CSV_URL (www.manitoba.ca/floodinfo/.../agoldataV2.csv)
    Uses fetch_and_parse (CSV), NOT arcgis_hub.query_feature_service.

    NOTE: Returns station LOCATIONS + flood status only — NOT real-time water level
    readings. For real-time HYDAT data use wateroffice.ec.gc.ca (ECCC).

    alert values: "No Flooding" | "High Water Advisory" | "Flood Watch" |
                  "Flood Warning" | "No Current Data"
    """
    cache_key = f"{CACHE_KEY_PREFIX}river_stations:{province}:{alert_only}"

    async def _fetch() -> dict[str, Any]:
        rows, _cached = await fetch_and_parse(RIVER_CONDITIONS_CSV_URL, ttl=CACHE_TTL_LIVE)
        stations: list[dict[str, Any]] = list(rows) if rows else []
        # Optional province filter (CSV includes multi-province records)
        if province:
            prov_upper = province.upper()
            stations = [
                s for s in stations
                if str(s.get("province", "")).upper() == prov_upper
            ]
        # Optional alert filter (exclude "No Flooding" / "No Current Data")
        if alert_only:
            inactive = {"no flooding", "no current data", ""}
            stations = [
                s for s in stations
                if str(s.get("alert", "")).lower() not in inactive
            ]
        return {"stations": stations, "count": len(stations)}

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_provincial_waterways(
    f_type: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba provincial waterways from Provincial_Waterways FeatureServer.

    f_type: one of WATERWAY_TYPES ("dike","floodway","dam","diversion","reservoir","waterway")
    or None for all types. Raises ValueError for unknown f_type values.
    Layer 0 fields: F_TYPE, Name, Watershed, WCW, LengthKM.
    """
    # Validate f_type before any network call
    if f_type is not None:
        f_type_lower = f_type.lower()
        if f_type_lower not in WATERWAY_TYPES:
            raise ValueError(
                f"Invalid f_type '{f_type}'. Must be one of: {', '.join(WATERWAY_TYPES)}"
            )
        # Map user-supplied lowercase value to title-case for WHERE clause
        # (ArcGIS stores values as e.g. "Floodway", "Dike", "Dam", "Reservoir",
        # "Waterway", "Diversion", "Detention Basin")
        _F_TYPE_DISPLAY: dict[str, str] = {
            "dike": "Dike",
            "floodway": "Floodway",
            "dam": "Dam",
            "diversion": "Diversion",
            "reservoir": "Reservoir",
            "waterway": "Waterway",
        }
        display_val = _F_TYPE_DISPLAY.get(f_type_lower, f_type.title())
    else:
        display_val = None

    cache_key = f"{CACHE_KEY_PREFIX}waterways:{f_type}:{max_records}:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        where = f"F_TYPE='{display_val}'" if display_val else "1=1"
        features, truncated = await arcgis_hub.query_feature_service(
            PROVINCIAL_WATERWAYS_FS_URL,
            layer_id=0,
            where=where,
            out_fields="F_TYPE,Name,Watershed,WCW,LengthKM",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# Agriculture / Drought — Plan 04 fills bodies
# ---------------------------------------------------------------------------


async def fetch_drought_status(
    filter_province: bool = True,
    dm_level: str | None = None,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch drought monitor polygons from Canada_USA_Drought_Monitor FeatureServer.

    filter_province=True (default) applies Manitoba bbox geometry filter
    (-101.36,48.99,-95.15,60.0) so only Manitoba polygons are returned (Pitfall 8:
    this layer has continental North America coverage; without filtering an agent
    receives all of Canada and the US).

    dm_level: None returns all intensity classes, or one of D0/D1/D2/D3/D4.
    Layer 0 fields: DM (intensity), OBS_DATE, SOURCE.
    """
    # Build WHERE clause
    where_parts: list[str] = []
    if dm_level is not None:
        where_parts.append(f"DM='{dm_level}'")
    where = " AND ".join(where_parts) if where_parts else "1=1"

    cache_key = f"{CACHE_KEY_PREFIX}drought:{filter_province}:{dm_level}:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()

        if filter_province:
            # Use geometry envelope to restrict to Manitoba bounding box.
            # query_feature_service does not expose geometry params directly, so we
            # call api_get against the FeatureServer /query endpoint with the
            # geometry filter (server-side, avoids fetching continental data).
            bbox_parts = MANITOBA_BBOX.split(",")  # xmin,ymin,xmax,ymax
            geometry_param = (
                f"{bbox_parts[0]},{bbox_parts[1]},{bbox_parts[2]},{bbox_parts[3]}"
            )
            params: dict[str, Any] = {
                "where": where,
                "geometry": geometry_param,
                "geometryType": "esriGeometryEnvelope",
                "spatialRel": "esriSpatialRelIntersects",
                "inSR": "4326",
                "outSR": "4326",
                "outFields": "DM,OBS_DATE,SOURCE",
                "returnGeometry": "true" if include_geometry else "false",
                "resultRecordCount": MAX_RECORDS,
                "f": "json",
            }
            raw = await api_get(
                f"{DROUGHT_MONITOR_FS_URL}/0/query",
                params,
                headers={"User-Agent": USER_AGENT},
            )
            # ArcGIS FeatureServer /query returns {"features": [...]} with attributes
            if isinstance(raw, dict):
                raw_features = raw.get("features", [])
                features = [f.get("attributes", f) for f in raw_features]
                truncated = raw.get("exceededTransferLimit", False)
            else:
                features = []
                truncated = False
        else:
            # No spatial filter — query the full continental layer
            features, truncated = await arcgis_hub.query_feature_service(
                DROUGHT_MONITOR_FS_URL,
                layer_id=0,
                where=where,
                out_fields="DM,OBS_DATE,SOURCE",
                include_geometry=include_geometry,
                max_records=MAX_RECORDS,
            )

        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


async def fetch_ag_weather_stations(
    ag_region: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba agricultural weather station locations from WeatherStations FeatureServer.

    ag_region: optional filter by AgRegion field value (e.g. "Southwest", "Central").
    Layer 0 fields: StnName, LatDD, LongDD, Elevation, AgRegion, URL.
    URL field links to live hourly readings per station at agrimaps.gov.mb.ca.
    """
    where = f"AgRegion='{ag_region}'" if ag_region else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}ag_weather:{ag_region}:{max_records}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            AG_WEATHER_STATIONS_FS_URL,
            layer_id=0,
            where=where,
            out_fields="StnName,LatDD,LongDD,Elevation,AgRegion,URL",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_livestock_prices(
    livestock: str = "cattle",
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba livestock market prices from MB_Cattle_Prices_Current_year FeatureServer.

    livestock: "cattle" queries MB_Cattle_Prices_Current_year FeatureServer.
    livestock: "hog" — HOG_PRICES_FS_URL is unresolved (spike finding); returns
    an empty result with a note rather than raising, to degrade gracefully.

    Raises ValueError if livestock not in {"cattle", "hog"}.
    Layer 0 fields: week, Auction, Parameter, Measure, Value.
    """
    valid = {"cattle", "hog"}
    if livestock not in valid:
        raise ValueError(
            f"Invalid livestock '{livestock}'. Must be one of: cattle, hog"
        )

    # Hog prices FeatureServer was not found in the Manitoba ArcGIS org during
    # Wave 0 spike. Return an empty-features graceful response rather than an error.
    if livestock == "hog" and HOG_PRICES_FS_URL is None:
        return (
            {
                "features": [],
                "count": 0,
                "truncated": False,
                "note": (
                    "Hog prices FeatureServer URL is unresolved (not found in "
                    "mMUesHYPkXjaFGfS ArcGIS org during Wave 0 spike). "
                    "Cattle prices available via livestock='cattle'."
                ),
            },
            False,
        )

    fs_url = CATTLE_PRICES_FS_URL if livestock == "cattle" else str(HOG_PRICES_FS_URL)
    cache_key = f"{CACHE_KEY_PREFIX}livestock:{livestock}:{max_records}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            fs_url,
            layer_id=0,
            where="1=1",
            out_fields="week,Auction,Parameter,Measure,Value",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_crop_regions(
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba crop reporting region boundaries from MbAg_Crop_Reporting_Regions FeatureServer.

    Layer 0 fields: OBJECTID, REGION (English), RÉGION (French).
    Returns bilingual boundary polygons for Manitoba Agriculture's 5 crop reporting regions.
    """
    cache_key = f"{CACHE_KEY_PREFIX}crop_regions:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            CROP_REGIONS_FS_URL,
            layer_id=0,
            where="1=1",
            out_fields="OBJECTID,REGION,RÉGION",
            include_geometry=include_geometry,
            max_records=MAX_RECORDS,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


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
    Layer 0 fields: NAME_E, NOM_F, BIOME, O_AREA, TYPE_E, TYPE_F, STATUS_E, PROTDATE, PRK_CLSS, URL.
    """
    where = f"TYPE_E='{park_type}'" if park_type else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}parks:{park_type}:{max_records}:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            PROVINCIAL_PARKS_FS_URL,
            layer_id=0,
            where=where,
            out_fields="NAME_E,NOM_F,BIOME,O_AREA,TYPE_E,TYPE_F,STATUS_E,PROTDATE,PRK_CLSS,URL",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_fisheries_data(
    name_query: str | None = None,
    fishing_division: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba waterbody/fisheries data from Manitoba_Waterbody_Data FeatureServer.

    350+ water bodies with fishing regulations, species, stocking records, Secchi depth.
    Focused field subset from the 26 available fields.

    name_query: filter by Name LIKE '%name_query%'
    fishing_division: filter by FishingDivision field
    Layer 0 fields (focused subset): ID, Name, SurfaceArea, AvgDepth, SecchiDepth,
    FishingDivision, Species, Regulations, BoatLaunch.
    """
    where_parts: list[str] = []
    if name_query:
        # Escape single quotes defensively
        safe_name = name_query.replace("'", "''")
        where_parts.append(f"Name LIKE '%{safe_name}%'")
    if fishing_division:
        safe_div = fishing_division.replace("'", "''")
        where_parts.append(f"FishingDivision='{safe_div}'")
    where = " AND ".join(where_parts) if where_parts else "1=1"

    cache_key = f"{CACHE_KEY_PREFIX}fisheries:{name_query}:{fishing_division}:{max_records}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            WATERBODY_DATA_FS_URL,
            layer_id=0,
            where=where,
            out_fields="ID,Name,SurfaceArea,AvgDepth,SecchiDepth,FishingDivision,Species,Regulations,BoatLaunch",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_provincial_forests(
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba provincial forests from Manitoba_Provincial_Forests___Version_6 FeatureServer.

    Returns provincial forest management unit boundaries.
    Layer 0: administrative forest regions.
    """
    cache_key = f"{CACHE_KEY_PREFIX}forests:{max_records}:{include_geometry}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            PROVINCIAL_FORESTS_FS_URL,
            layer_id=0,
            where="1=1",
            out_fields="*",
            include_geometry=include_geometry,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_STATIC, _fetch)


async def fetch_surgical_wait_times(
    year: int | None = None,
    procedure: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba diagnostic/surgical wait time averages from FeatureServer.

    Annual averages by Year and IndicatorDataArea (procedure type).
    Layer 0 fields: Year, IndicatorDataArea, Average_Wait.
    MaxRecordCount 1000 at source; up to 32,000 records covering many procedures.

    year: optional integer year filter (e.g. 2021)
    procedure: optional LIKE filter on IndicatorDataArea (e.g. "Cardiac surgery")
    """
    where_parts: list[str] = []
    if year is not None:
        where_parts.append(f"Year={year}")
    if procedure:
        safe_proc = procedure.replace("'", "''")
        where_parts.append(f"IndicatorDataArea LIKE '%{safe_proc}%'")
    where = " AND ".join(where_parts) if where_parts else "1=1"

    cache_key = f"{CACHE_KEY_PREFIX}wait_times:{year}:{procedure}:{max_records}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            SURGICAL_WAIT_TIMES_FS_URL,
            layer_id=0,
            where=where,
            out_fields="Year,IndicatorDataArea,Average_Wait",
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_ANNUAL, _fetch)


async def fetch_health_facilities(
    community: str | None = None,
    emergency_only: bool = False,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch Manitoba rural health care facilities from FeatureServer.

    Spike-resolved URL: Rural_Health_Care_Facilities_in_Manitoba/FeatureServer/0.
    Layer 0 MaxRecordCount: 2000.

    community: optional filter by Community_Name (e.g. "Selkirk", "Portage la Prairie")
    emergency_only: if True, filter to facilities with Emergency_Department_Availabili='Yes'
    Layer 0 fields: Community_Name, Facility_Name, Lat, Long,
    Emergency_Department_Availabili, Percentage_of_Time_Open__2015_,
    Nearest_Alternate_Emergency_Dep, Acute_Care_Availability, Acute_Care_Number_of_Beds.
    """
    where_parts: list[str] = []
    if community:
        safe_comm = community.replace("'", "''")
        where_parts.append(f"Community_Name LIKE '%{safe_comm}%'")
    if emergency_only:
        where_parts.append("Emergency_Department_Availabili='Yes'")
    where = " AND ".join(where_parts) if where_parts else "1=1"

    cache_key = f"{CACHE_KEY_PREFIX}health_facilities:{community}:{emergency_only}:{max_records}"

    async def _fetch() -> dict[str, Any]:
        await _hub_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            RURAL_HEALTH_FACILITIES_FS_URL,
            layer_id=0,
            where=where,
            out_fields=(
                "Community_Name,Facility_Name,Lat,Long,"
                "Emergency_Department_Availabili,Percentage_of_Time_Open__2015_,"
                "Nearest_Alternate_Emergency_Dep,Acute_Care_Availability,Acute_Care_Number_of_Beds"
            ),
            include_geometry=False,
            max_records=max_records,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# Transport / 511 — Plan 06 fills bodies
# ---------------------------------------------------------------------------


async def fetch_road_events(
    event_type: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch current road events from Manitoba 511 API v3 /events endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Returns raw list of event dicts flattened from the 511 response.
    Rate-limited to RATE_LIMIT_511 (2 r/s, documented limit 10/60s).

    NOTE: 511 returns a JSON list at the top level — NOT an ArcGIS/CKAN envelope.
    NEVER call arcgis_hub.query_feature_service for 511 endpoints.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:events:{event_type}"

    async def _fetch() -> list[dict]:
        await _511_limiter.acquire()
        rows = await _511_get("events")
        if event_type:
            rows = [r for r in rows if r.get("EventType") == event_type]
        return rows[:max_records]

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_winter_road_conditions(
    area_name: str | None = None,
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch winter road conditions from Manitoba 511 API v3 /winterroads endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Seasonal — returns [] outside winter road season (API returns empty list).
    Optional area_name performs client-side filtering on AreaName field.
    Rate-limited to RATE_LIMIT_511.

    NOTE: 511 returns a JSON list at the top level — NOT an ArcGIS/CKAN envelope.
    NEVER call arcgis_hub.query_feature_service for 511 endpoints.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:winterroads:{area_name}"

    async def _fetch() -> list[dict]:
        await _511_limiter.acquire()
        rows = await _511_get("winterroads")
        if area_name:
            rows = [r for r in rows if r.get("AreaName") == area_name]
        return rows[:max_records]

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_traffic_cameras(
    max_records: int = MAX_RECORDS,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch traffic camera locations from Manitoba 511 API v3 /cameras endpoint.

    KEY REQUIRED: reads MANITOBA_511_KEY from env. Raises Five11NotConfigured if absent.
    Camera locations are stable — cached at CACHE_TTL_META (24h).
    Each camera includes a Views array with Name and Url sub-entries.
    Rate-limited to RATE_LIMIT_511.

    NOTE: 511 returns a JSON list at the top level — NOT an ArcGIS/CKAN envelope.
    NEVER call arcgis_hub.query_feature_service for 511 endpoints.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:cameras"

    async def _fetch() -> list[dict]:
        await _511_limiter.acquire()
        rows = await _511_get("cameras")
        return rows[:max_records]

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
