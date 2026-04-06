"""Client functions for MSC GeoMet climate data collections.

Covers historical daily/monthly observations, 1981-2010 climate normals,
AHCCD long-term trends, and metadata for CMIP5/CMIP6 projections and SPEI
drought index (items endpoint returns 400 for colon-ID collections).
"""

from mcp_canada.modules.weather.constants import (
    BASE_URL,
    CACHE_TTL_CLIMATE,
    COLL_AHCCD_TRENDS,
    COLL_CLIMATE_DAILY,
    COLL_CLIMATE_MONTHLY,
    COLL_CLIMATE_NORMALS,
    COLL_CMIP5,
    COLL_CMIP6,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.geo import ogc_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.rate_limiter import get_limiter

# SPEI collection IDs keyed by period length
_SPEI_COLLECTIONS: dict[int, str] = {
    1: "climate:spei-1:historical",
    3: "climate:spei-3:historical",
    12: "climate:spei-12:historical",
}


def _safe_float(value: object) -> float | None:
    """Convert a string or number to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return None


def _flatten_daily(feature: dict) -> dict:
    """Flatten an OGC climate-daily feature to a plain dict."""
    props = feature.get("properties") or {}
    return {
        "station_id": props.get("CLIMATE_IDENTIFIER"),
        "date": props.get("LOCAL_DATE"),
        "max_temp_c": _safe_float(props.get("MAX_TEMPERATURE")),
        "min_temp_c": _safe_float(props.get("MIN_TEMPERATURE")),
        "mean_temp_c": _safe_float(props.get("MEAN_TEMPERATURE")),
        "total_precip_mm": _safe_float(props.get("TOTAL_PRECIPITATION")),
        "total_snow_cm": _safe_float(props.get("TOTAL_SNOW")),
        "snow_on_ground_cm": _safe_float(props.get("SNOW_ON_GROUND")),
        "heating_dd": _safe_float(props.get("HEATING_DEGREE_DAYS")),
        "cooling_dd": _safe_float(props.get("COOLING_DEGREE_DAYS")),
    }


def _flatten_monthly(feature: dict) -> dict:
    """Flatten an OGC climate-monthly feature to a plain dict."""
    props = feature.get("properties") or {}
    return {
        "station_id": props.get("CLIMATE_IDENTIFIER"),
        "year": props.get("LOCAL_YEAR"),
        "month": props.get("LOCAL_MONTH"),
        "mean_temp_c": _safe_float(props.get("MEAN_TEMPERATURE")),
        "max_temp_c": _safe_float(props.get("MAX_TEMPERATURE")),
        "min_temp_c": _safe_float(props.get("MIN_TEMPERATURE")),
        "total_precip_mm": _safe_float(props.get("TOTAL_PRECIPITATION")),
        "total_snow_cm": _safe_float(props.get("TOTAL_SNOW")),
    }


def _flatten_normal(feature: dict) -> dict:
    """Flatten an OGC climate-normals feature to a plain dict."""
    props = feature.get("properties") or {}
    return {
        "station_id": props.get("CLIMATE_IDENTIFIER"),
        "period_begin": props.get("PERIOD_BEGIN"),
        "period_end": props.get("PERIOD_END"),
        "month": props.get("MONTH"),
        "variable": props.get("NORMAL_CODE"),
        "value": _safe_float(props.get("NORMAL_VALUE")),
    }


def _flatten_trend(feature: dict) -> dict:
    """Flatten an OGC ahccd-trends feature to a plain dict."""
    props = feature.get("properties") or {}
    return {
        "station_id": props.get("CLIMATE_IDENTIFIER"),
        "measurement_type": props.get("MEASUREMENT_TYPE"),
        "trend": _safe_float(props.get("TREND")),
        "year_begin": props.get("YEAR_BEGIN"),
        "year_end": props.get("YEAR_END"),
    }


async def fetch_climate_daily(
    station_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> tuple[list[dict], bool]:
    """Fetch historical daily climate observations for a station.

    Args:
        station_id: Climate station identifier (e.g. "6158731").
        start_date: ISO date string start of range (e.g. "2024-01-01").
        end_date: ISO date string end of range (e.g. "2024-01-31").
        limit: Max number of records to return.

    Returns:
        (list of flattened daily dicts, was_cached) tuple.
    """
    properties: dict[str, str] = {"CLIMATE_IDENTIFIER": station_id}
    datetime_filter: str | None = None
    if start_date and end_date:
        datetime_filter = f"{start_date}/{end_date}"

    features, _count, was_cached = await ogc_fetch(
        COLL_CLIMATE_DAILY,
        properties=properties,
        datetime_filter=datetime_filter,
        limit=limit,
        ttl=CACHE_TTL_CLIMATE,
    )
    return [_flatten_daily(f) for f in features], was_cached


async def fetch_climate_monthly(
    station_id: str,
    year: int | None = None,
    limit: int = 12,
) -> tuple[list[dict], bool]:
    """Fetch monthly climate summary records for a station.

    Args:
        station_id: Climate station identifier.
        year: Optional year to filter by (e.g. 2024).
        limit: Max number of records to return.

    Returns:
        (list of flattened monthly dicts, was_cached) tuple.
    """
    properties: dict[str, str] = {"CLIMATE_IDENTIFIER": station_id}
    if year is not None:
        properties["LOCAL_YEAR"] = str(year)

    features, _count, was_cached = await ogc_fetch(
        COLL_CLIMATE_MONTHLY,
        properties=properties,
        limit=limit,
        ttl=CACHE_TTL_CLIMATE,
    )
    return [_flatten_monthly(f) for f in features], was_cached


async def fetch_climate_normals(
    station_id: str,
    limit: int = 100,
) -> tuple[list[dict], bool]:
    """Fetch 1981-2010 climate normals for a station.

    Note: the available normals period is 1981-2010. The 1991-2020 normals are
    NOT yet available via this API endpoint.

    Args:
        station_id: Climate station identifier.
        limit: Max number of records to return.

    Returns:
        (list of flattened normal dicts, was_cached) tuple.
    """
    features, _count, was_cached = await ogc_fetch(
        COLL_CLIMATE_NORMALS,
        properties={"CLIMATE_IDENTIFIER": station_id},
        limit=limit,
        ttl=CACHE_TTL_CLIMATE,
    )
    return [_flatten_normal(f) for f in features], was_cached


async def fetch_climate_projections(
    model: str = "cmip5",
) -> tuple[dict, bool]:
    """Fetch collection metadata for CMIP5 or CMIP6 climate projections.

    IMPORTANT: The /items endpoint returns HTTP 400 for colon-ID collections
    like CMIP5 and CMIP6. This function fetches collection-level metadata only
    (title, description, extent, links). Grid-based projection data requires
    direct MSC API access outside this OGC endpoint.

    Args:
        model: Either "cmip5" (default) or "cmip6".

    Returns:
        (metadata dict with limitation note, was_cached) tuple.
    """
    collection_id = COLL_CMIP6 if model.lower() == "cmip6" else COLL_CMIP5
    cache_key = f"wx:climate:proj:{model.lower()}"

    async def _fetch() -> dict:
        limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)
        await limiter.acquire()
        url = f"{BASE_URL}/collections/{collection_id}?f=json"
        return await api_get(url)

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_CLIMATE, _fetch)

    result: dict = dict(raw) if raw else {}
    result["note"] = (
        "Returns collection metadata only. "
        "The /items endpoint returns 400 for this collection. "
        "Grid-based projection data requires direct MSC API access."
    )
    return result, was_cached


async def fetch_drought_index(
    lat: float | None = None,
    lon: float | None = None,
    spei_period: int = 3,
) -> tuple[dict, bool]:
    """Fetch collection metadata for the SPEI drought index.

    IMPORTANT: The /items endpoint returns HTTP 400 for SPEI colon-ID
    collections. This function returns collection-level metadata only.

    Args:
        lat: Optional latitude (informational, not used in API query).
        lon: Optional longitude (informational, not used in API query).
        spei_period: SPEI accumulation period in months: 1, 3, or 12 (default 3).

    Returns:
        (metadata dict with limitation note, was_cached) tuple.
    """
    collection_id = _SPEI_COLLECTIONS.get(spei_period, _SPEI_COLLECTIONS[3])
    cache_key = f"wx:climate:spei:{spei_period}"

    async def _fetch() -> dict:
        limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)
        await limiter.acquire()
        url = f"{BASE_URL}/collections/{collection_id}?f=json"
        return await api_get(url)

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_CLIMATE, _fetch)

    result: dict = dict(raw) if raw else {}
    result["note"] = (
        "Returns collection metadata only. "
        "The /items endpoint returns 400 for this collection. "
        "SPEI values require direct MSC API access."
    )
    return result, was_cached


async def fetch_climate_trends(
    station_id: str | None = None,
    measurement_type: str | None = None,
    limit: int = 100,
) -> tuple[list[dict], bool]:
    """Fetch long-term climate trend data from the AHCCD dataset.

    Args:
        station_id: Optional climate station identifier to filter.
        measurement_type: Optional type filter (e.g. "temperature", "precipitation").
        limit: Max number of records to return.

    Returns:
        (list of flattened trend dicts, was_cached) tuple.
    """
    properties: dict[str, str] = {}
    if station_id is not None:
        properties["CLIMATE_IDENTIFIER"] = station_id
    if measurement_type is not None:
        properties["MEASUREMENT_TYPE"] = measurement_type

    features, _count, was_cached = await ogc_fetch(
        COLL_AHCCD_TRENDS,
        properties=properties if properties else None,
        limit=limit,
        ttl=CACHE_TTL_CLIMATE,
    )
    return [_flatten_trend(f) for f in features], was_cached


async def compare_climate_periods(
    station_id: str,
    p1_start: str,
    p1_end: str,
    p2_start: str,
    p2_end: str,
) -> tuple[dict, bool]:
    """Compare climate averages between two date periods for a station.

    Fetches daily observations for both periods and computes averages for
    mean temperature, total precipitation, and total snowfall. Returns
    deltas (period2 - period1) for each variable.

    Args:
        station_id: Climate station identifier.
        p1_start: Period 1 start date (ISO format, e.g. "2000-01-01").
        p1_end: Period 1 end date.
        p2_start: Period 2 start date.
        p2_end: Period 2 end date.

    Returns:
        (comparison dict with period1, period2, deltas, was_cached) tuple.
        was_cached is True only if BOTH fetches were cached.
    """
    records1, cached1 = await fetch_climate_daily(station_id, p1_start, p1_end, limit=500)
    records2, cached2 = await fetch_climate_daily(station_id, p2_start, p2_end, limit=500)

    def _avg(records: list[dict], field: str) -> float | None:
        vals = [r[field] for r in records if r.get(field) is not None]
        return sum(vals) / len(vals) if vals else None

    def _total(records: list[dict], field: str) -> float | None:
        vals = [r[field] for r in records if r.get(field) is not None]
        return sum(vals) if vals else None

    p1_mean_temp = _avg(records1, "mean_temp_c")
    p2_mean_temp = _avg(records2, "mean_temp_c")
    p1_precip = _total(records1, "total_precip_mm")
    p2_precip = _total(records2, "total_precip_mm")
    p1_snow = _total(records1, "total_snow_cm")
    p2_snow = _total(records2, "total_snow_cm")

    def _delta(v1: float | None, v2: float | None) -> float | None:
        if v1 is not None and v2 is not None:
            return round(v2 - v1, 4)
        return None

    comparison = {
        "station_id": station_id,
        "period1": {
            "start": p1_start,
            "end": p1_end,
            "records": len(records1),
            "mean_temp_c": p1_mean_temp,
            "total_precip_mm": p1_precip,
            "total_snow_cm": p1_snow,
        },
        "period2": {
            "start": p2_start,
            "end": p2_end,
            "records": len(records2),
            "mean_temp_c": p2_mean_temp,
            "total_precip_mm": p2_precip,
            "total_snow_cm": p2_snow,
        },
        "deltas": {
            "mean_temp_c": _delta(p1_mean_temp, p2_mean_temp),
            "total_precip_mm": _delta(p1_precip, p2_precip),
            "total_snow_cm": _delta(p1_snow, p2_snow),
        },
    }
    return comparison, (cached1 and cached2)
