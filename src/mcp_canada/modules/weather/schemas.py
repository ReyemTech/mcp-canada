"""Pydantic v2 flat schemas for MSC GeoMet weather module responses.

All models use flat structures — no nested API response shapes.
Optional fields use X | None to gracefully handle missing API data.
"""

from pydantic import BaseModel


class CurrentConditions(BaseModel):
    """Current weather conditions at an observation station."""

    station: str | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    wind_speed_kmh: float | None = None
    wind_direction: str | None = None
    condition: str | None = None
    pressure_kpa: float | None = None
    windchill: float | None = None
    observed_at: str | None = None
    city: str | None = None


class ForecastPeriod(BaseModel):
    """A single forecast period from a city weather forecast."""

    period: str | None = None
    temperature_c: float | None = None
    text: str | None = None
    icon_code: str | None = None
    precip_probability_pct: float | None = None
    wind_speed_kmh: float | None = None
    wind_direction: str | None = None


class WeatherAlert(BaseModel):
    """A weather alert or warning issued by Environment Canada."""

    alert_code: str | None = None
    alert_type: str | None = None
    name: str | None = None
    province: str | None = None
    region: str | None = None
    text: str | None = None
    published: str | None = None
    expires: str | None = None
    lat: float | None = None
    lon: float | None = None


class ClimateStation(BaseModel):
    """A climate observation station from the MSC station network."""

    station_id: str | None = None
    station_name: str | None = None
    province: str | None = None
    lat: float | None = None
    lon: float | None = None
    elevation_m: float | None = None
    first_year: int | None = None
    last_year: int | None = None
    has_hourly: bool | None = None
    has_daily: bool | None = None
    has_monthly: bool | None = None


class HourlyObservation(BaseModel):
    """A single hourly climate observation record."""

    station_id: str | None = None
    datetime: str | None = None
    temp_c: float | None = None
    dew_point_c: float | None = None
    wind_dir_deg: float | None = None
    wind_speed_kmh: float | None = None
    weather_desc: str | None = None
    pressure_kpa: float | None = None


class DailyClimate(BaseModel):
    """A single daily climate summary record."""

    station_id: str | None = None
    date: str | None = None
    max_temp_c: float | None = None
    min_temp_c: float | None = None
    mean_temp_c: float | None = None
    total_precip_mm: float | None = None
    total_snow_cm: float | None = None
    snow_on_ground_cm: float | None = None
    heating_dd: float | None = None
    cooling_dd: float | None = None


class ClimateNormal(BaseModel):
    """A climate normal (30-year average) for a station and variable."""

    station_id: str | None = None
    period_begin: int | None = None
    period_end: int | None = None
    month: int | None = None
    variable: str | None = None
    value: float | None = None


class AqhiReading(BaseModel):
    """An Air Quality Health Index observation or forecast reading."""

    location_id: str | None = None
    location_name: str | None = None
    aqhi_value: float | None = None
    datetime: str | None = None
    lat: float | None = None
    lon: float | None = None


class HydroReading(BaseModel):
    """A hydrometric station water level or discharge reading."""

    station_number: str | None = None
    station_name: str | None = None
    level_m: float | None = None
    discharge_m3s: float | None = None
    datetime: str | None = None
    lat: float | None = None
    lon: float | None = None


class MarineForecast(BaseModel):
    """A marine weather forecast for a coastal or inland water area."""

    area: str | None = None
    region: str | None = None
    forecast_text: str | None = None
    warnings_count: int | None = None
    lat: float | None = None
    lon: float | None = None
