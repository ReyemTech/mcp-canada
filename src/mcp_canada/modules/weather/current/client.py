"""Client functions for weather/current sub-module.

Fetches current conditions, forecasts, weather alerts, climate stations,
and hourly observations from MSC GeoMet OGC API.

All functions return (data, was_cached) tuples.
HTTP is handled by ogc_fetch() in shared/geo.py.
"""

from mcp_canada.modules.weather.constants import (
    CACHE_TTL_ALERTS,
    CACHE_TTL_FORECAST,
    CACHE_TTL_REALTIME,
    CACHE_TTL_STATIONS,
    COLL_ALERTS,
    COLL_CITYPAGE,
    COLL_CLIMATE_HOURLY,
    COLL_CLIMATE_STATIONS,
    PROVINCE_BBOX,
)
from mcp_canada.shared.geo import build_bbox, extract_centroid, ogc_fetch


def _name_filter(location: str | None, lat: float | None, province: str | None,
                 lang: str) -> dict[str, str] | None:
    """Server-side property filter for a city-name lookup, or None.

    The citypage collection holds 844 cities. Filtering must happen upstream —
    pulling one `limit`-sized page and filtering it locally only finds cities
    that happen to fall in that arbitrary page, which is why every major-city
    lookup used to return NOT_FOUND while lat/lon worked (Phase 20.1).

    The upstream filter is a case-insensitive token match, so `name.en=Toronto`
    matches both "Toronto" and "Toronto Island" — see _pick_city for the
    exact-match preference that resolves it.
    """
    if location is None or lat is not None or province is not None:
        return None
    field = "name.fr" if lang == "fr" else "name.en"
    return {field: location}


def _pick_city(features: list[dict], location: str | None, lang: str) -> dict | None:
    """Choose the best feature for a name lookup, preferring an exact match.

    `name.en=Toronto` returns ["Toronto Island", "Toronto"] in that order, so
    taking features[0] answers "weather in Toronto" with Toronto Island.
    """
    if not features:
        return None
    if location is None:
        return features[0]

    wanted = location.strip().lower()

    def _names(feature: dict) -> tuple[str, str]:
        names = feature.get("properties", {}).get("name", {})
        return (
            str(names.get(lang, "")).strip().lower(),
            str(names.get("en", "")).strip().lower(),
        )

    # Exact match wins: "Toronto" should not resolve to "Toronto Island".
    for feature in features:
        if wanted in _names(feature):
            return feature

    # Otherwise accept a containing match — "Ottawa" legitimately resolves to
    # "Ottawa (Kanata - Orleans)". This also re-checks the upstream filter
    # client-side: if the server ever ignores the name parameter and returns an
    # unrelated city, we return None rather than answering with the wrong place.
    for feature in features:
        if any(wanted in name for name in _names(feature)):
            return feature

    return None


async def fetch_current_conditions(
    location: str | None = None,
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: str = "en",
) -> tuple[dict | None, bool]:
    """Fetch current weather conditions from citypageweather-realtime.

    Location resolution priority: lat/lon > province > location name search.

    Args:
        location: City name for text-match filtering (case-insensitive).
        province: Province code (e.g. "ON") — uses PROVINCE_BBOX.
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        lang: Language for bilingual value extraction ("en" or "fr").

    Returns:
        (flat conditions dict, was_cached), or (None, was_cached) if not found.
    """
    bbox: tuple[float, float, float, float] | None = None

    if lat is not None and lon is not None:
        # 0.3-degree bbox (~30 km) around the point
        bbox = (lon - 0.3, lat - 0.3, lon + 0.3, lat + 0.3)
    elif province is not None:
        bbox = PROVINCE_BBOX.get(province.upper())

    name_filter = _name_filter(location, lat, province, lang)

    features, _, was_cached = await ogc_fetch(
        COLL_CITYPAGE,
        bbox=bbox,
        properties=name_filter,
        limit=50,
        ttl=CACHE_TTL_REALTIME,
    )

    feature = _pick_city(features, location if name_filter else None, lang)
    if feature is None:
        return None, was_cached

    props = feature["properties"]
    cc = props.get("currentConditions", {})

    def _val(nested: dict, *keys: str) -> object:
        """Safely navigate nested bilingual dict, returning lang-specific value."""
        obj = nested
        for k in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(k)
        if isinstance(obj, dict):
            return obj.get(lang) if lang in obj else obj.get("en")
        return obj

    city_name = props.get("name", {}).get(lang) or props.get("name", {}).get("en")

    return {
        "station": _val(cc, "station", "value"),
        "temperature_c": _val(cc, "temperature", "value"),
        "humidity_pct": _val(cc, "relativeHumidity", "value"),
        "wind_speed_kmh": _val(cc, "wind", "speed", "value"),
        "wind_direction": _val(cc, "wind", "direction", "value"),
        "condition": cc.get("condition", {}).get(lang) or cc.get("condition", {}).get("en"),
        "pressure_kpa": _val(cc, "pressure", "value"),
        "windchill": _val(cc, "windChill", "value"),
        "observed_at": cc.get("timestamp", {}).get(lang) or cc.get("timestamp", {}).get("en"),
        "city": city_name,
    }, was_cached


def _bilingual(obj: object, lang: str = "en") -> object:
    """Extract a value from a bilingual dict {en: ..., fr: ...}, or return as-is."""
    if isinstance(obj, dict):
        return obj.get(lang) if lang in obj else obj.get("en")
    return obj


async def fetch_forecast(
    location: str | None = None,
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch multi-day weather forecast from citypageweather-realtime.

    Extracts forecastGroup.forecasts and flattens each period.

    Args:
        location: City name for text-match filtering.
        province: Province code for bbox filtering.
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        lang: Language for bilingual fields ("en" or "fr").

    Returns:
        (list of ForecastPeriod dicts, was_cached).
    """
    bbox: tuple[float, float, float, float] | None = None

    if lat is not None and lon is not None:
        bbox = (lon - 0.3, lat - 0.3, lon + 0.3, lat + 0.3)
    elif province is not None:
        bbox = PROVINCE_BBOX.get(province.upper())

    name_filter = _name_filter(location, lat, province, lang)

    features, _, was_cached = await ogc_fetch(
        COLL_CITYPAGE,
        bbox=bbox,
        properties=name_filter,
        limit=50,
        ttl=CACHE_TTL_FORECAST,
    )

    feature = _pick_city(features, location if name_filter else None, lang)
    if feature is None:
        return [], was_cached

    props = feature["properties"]
    forecast_group = props.get("forecastGroup", {})
    raw_forecasts = forecast_group.get("forecasts", [])

    periods: list[dict] = []
    for fc in raw_forecasts:
        period_name = _bilingual(fc.get("period", {}).get("textForecastName"), lang)

        # temperatures.temperature is a LIST of objects, not a dict
        temps_list = fc.get("temperatures", {}).get("temperature", [])
        temperature = None
        if isinstance(temps_list, list) and temps_list:
            temperature = _bilingual(temps_list[0].get("value"), lang)
        elif isinstance(temps_list, dict):
            temperature = _bilingual(temps_list.get("value"), lang)

        text = _bilingual(fc.get("textSummary"), lang)
        abbr_text = _bilingual(fc.get("abbreviatedForecast", {}).get("textSummary"), lang)

        # Wind from winds.periods[] (not abbreviatedForecast)
        wind_speed = None
        wind_dir = None
        winds_periods = fc.get("winds", {}).get("periods", [])
        if isinstance(winds_periods, list) and winds_periods:
            wp = winds_periods[0]
            wind_speed = _bilingual(wp.get("speed", {}).get("value"), lang)
            wind_dir = _bilingual(wp.get("bearing", {}).get("value"), lang)

        # Precipitation from cloudPrecip if available
        pop = None
        cloud_precip = fc.get("cloudPrecip", {})
        if isinstance(cloud_precip, dict):
            pop_obj = cloud_precip.get("precipType", {})
            if isinstance(pop_obj, dict):
                pop = _bilingual(pop_obj.get("amount"), lang)

        periods.append({
            "period": period_name,
            "temperature_c": temperature,
            "text": text or abbr_text,
            "precip_probability_pct": pop,
            "wind_speed_kmh": wind_speed,
            "wind_direction_deg": wind_dir,
        })

    return periods, was_cached


async def fetch_alerts(
    province: str | None = None,
    alert_type: str | None = None,
    limit: int = 25,
) -> tuple[list[dict], bool]:
    """Fetch active weather alerts from weather-alerts OGC collection.

    Province filter is passed as a property filter to the OGC API
    (confirmed working for weather-alerts collection).

    Args:
        province: Province code (e.g. "NB") — OGC property filter, not bbox.
        alert_type: Alert type string (e.g. "warning", "watch", "advisory").
        limit: Maximum number of alerts to return (default 25).

    Returns:
        (list of WeatherAlert dicts, was_cached).
    """
    properties: dict[str, str] = {}
    if province is not None:
        properties["province"] = province.upper()
    if alert_type is not None:
        properties["alert_type"] = alert_type

    features, _, was_cached = await ogc_fetch(
        COLL_ALERTS,
        properties=properties if properties else None,
        limit=limit,
        ttl=CACHE_TTL_ALERTS,
    )

    alerts: list[dict] = []
    for f in features:
        p = f["properties"]
        lat, lon = extract_centroid(f.get("geometry"))
        alerts.append({
            "alert_code": p.get("alert_code"),
            "alert_type": p.get("alert_type"),
            "name": p.get("alert_name_en"),
            "province": p.get("province"),
            "region": p.get("feature_name_en"),
            "text": p.get("alert_text_en"),
            "published": p.get("publication_datetime"),
            "expires": p.get("expiration_datetime"),
            "lat": lat,
            "lon": lon,
        })

    return alerts, was_cached


async def fetch_stations(
    province: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    name: str | None = None,
    limit: int = 50,
) -> tuple[list[dict], bool]:
    """Fetch climate stations from climate-stations OGC collection.

    Uses geometry.coordinates for lat/lon (decimal degrees) — NOT the
    LATITUDE/LONGITUDE properties which are in DMS (milliarcseconds) format.

    Args:
        province: Province code for bbox filtering via PROVINCE_BBOX.
        lat: Latitude in decimal degrees for nearby search.
        lon: Longitude in decimal degrees for nearby search.
        name: Station name text filter (applied post-fetch).
        limit: Maximum number of stations to return (default 50).

    Returns:
        (list of ClimateStation dicts, was_cached).
    """
    bbox: tuple[float, float, float, float] | None = None

    if lat is not None and lon is not None:
        bbox = build_bbox(lat, lon, radius_km=100)
    elif province is not None:
        bbox = PROVINCE_BBOX.get(province.upper())

    features, _, was_cached = await ogc_fetch(
        COLL_CLIMATE_STATIONS, bbox=bbox, limit=limit, ttl=CACHE_TTL_STATIONS
    )

    # Optional name filter
    if name:
        name_lower = name.lower()
        features = [
            f for f in features
            if name_lower in f["properties"].get("STATION_NAME", "").lower()
        ]

    stations: list[dict] = []
    for f in features:
        p = f["properties"]
        # CRITICAL: Use geometry.coordinates (decimal degrees), NOT LATITUDE/LONGITUDE (DMS)
        feat_lat, feat_lon = extract_centroid(f.get("geometry"))

        first_date = p.get("FIRST_DATE", "")
        last_date = p.get("LAST_DATE", "")
        first_year = int(first_date[:4]) if first_date and len(first_date) >= 4 else None
        last_year = int(last_date[:4]) if last_date and len(last_date) >= 4 else None

        stations.append({
            "station_id": p.get("CLIMATE_IDENTIFIER"),
            "station_name": p.get("STATION_NAME"),
            "province": p.get("PROVINCE_CODE"),
            "lat": feat_lat,
            "lon": feat_lon,
            "elevation_m": p.get("ELEVATION"),
            "first_year": first_year,
            "last_year": last_year,
            "has_hourly": p.get("HLY_FIRST_DATE") is not None,
            "has_daily": p.get("DLY_FIRST_DATE") is not None,
            "has_monthly": p.get("MLY_FIRST_DATE") is not None,
        })

    return stations, was_cached


async def fetch_hourly_obs(
    station_id: str,
    date: str | None = None,
    limit: int = 24,
) -> tuple[list[dict], bool]:
    """Fetch hourly climate observations for a specific station.

    Args:
        station_id: CLIMATE_IDENTIFIER (e.g. "6105976").
        date: ISO date string (YYYY-MM-DD) to filter observations to one day.
        limit: Maximum number of records to return (default 24 = one day).

    Returns:
        (list of HourlyObservation dicts, was_cached).
    """
    properties: dict[str, str] = {"CLIMATE_IDENTIFIER": station_id}
    datetime_filter: str | None = None

    if date is not None:
        datetime_filter = f"{date}T00:00:00Z/{date}T23:59:59Z"

    features, _, was_cached = await ogc_fetch(
        COLL_CLIMATE_HOURLY,
        properties=properties,
        datetime_filter=datetime_filter,
        limit=limit,
        ttl=CACHE_TTL_REALTIME,
    )

    observations: list[dict] = []
    for f in features:
        p = f["properties"]
        observations.append({
            "station_id": p.get("CLIMATE_IDENTIFIER"),
            "datetime": p.get("LOCAL_DATE"),
            "temp_c": p.get("TEMP"),
            "dew_point_c": p.get("DEW_POINT_TEMP"),
            "wind_dir_deg": p.get("WIND_DIRECTION"),
            "wind_speed_kmh": p.get("WIND_SPEED"),
            "weather_desc": p.get("WEATHER_ENG_DESC"),
            "pressure_kpa": p.get("STATION_PRESSURE"),
        })

    return observations, was_cached
