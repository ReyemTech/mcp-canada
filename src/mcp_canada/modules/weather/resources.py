"""MCP resources for the Weather module (MSC GeoMet OGC API).

Provides reference catalogs, documentation guides, and response templates for
Environment Canada weather, climate, and hydrological data. All resources use
type-prefixed URIs:
- data://weather/...    — JSON reference catalogs (machine-parseable)
- docs://weather/...    — Markdown documentation guides (human-readable)
- template://weather/...— Markdown response templates with {placeholder} syntax

NOTE: This file is at the top-level weather/ directory. FileSystemProvider scans
recursively — placing resources here avoids duplicate discovery from sub-modules.

IMPORTANT: All resource functions are zero-parameter. Adding any parameter
(even lang) would make FastMCP treat them as ResourceTemplate instead of
FunctionResource, removing them from resources/list.
Bilingual content is embedded inline in a single resource.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://weather/province-codes",
    mime_type="application/json",
    name="wx_province_codes",
    title="Canadian Province and Territory Codes",
)
def wx_province_codes() -> str:
    """Valid province and territory codes for weather station searches.

    Use these 2-letter codes with wx_search_stations (province parameter)
    or with PROVINCE_BBOX for geographic bounding box queries.
    Format: {"CODE": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "BC": {"en": "British Columbia", "fr": "Colombie-Britannique"},
            "AB": {"en": "Alberta", "fr": "Alberta"},
            "SK": {"en": "Saskatchewan", "fr": "Saskatchewan"},
            "MB": {"en": "Manitoba", "fr": "Manitoba"},
            "ON": {"en": "Ontario", "fr": "Ontario"},
            "QC": {"en": "Quebec", "fr": "Québec"},
            "NB": {"en": "New Brunswick", "fr": "Nouveau-Brunswick"},
            "NS": {"en": "Nova Scotia", "fr": "Nouvelle-Écosse"},
            "PE": {"en": "Prince Edward Island", "fr": "Île-du-Prince-Édouard"},
            "NL": {"en": "Newfoundland and Labrador", "fr": "Terre-Neuve-et-Labrador"},
            "YT": {"en": "Yukon", "fr": "Yukon"},
            "NT": {"en": "Northwest Territories", "fr": "Territoires du Nord-Ouest"},
            "NU": {"en": "Nunavut", "fr": "Nunavut"},
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://weather/common-stations",
    mime_type="application/json",
    name="wx_common_stations",
    title="Common Canadian Weather Stations",
)
def wx_common_stations() -> str:
    """Major Canadian city weather stations with their station IDs.

    Use these station_id values directly with wx_get_current_conditions,
    wx_get_forecast, or wx_get_weather_alerts without needing wx_search_stations.
    """
    return json.dumps(
        [
            {
                "city": "Toronto (Pearson)",
                "province": "ON",
                "station_id": "s0000458",
                "en": "Toronto Pearson International Airport",
                "fr": "Aéroport international Pearson de Toronto",
            },
            {
                "city": "Vancouver (YVR)",
                "province": "BC",
                "station_id": "s0000141",
                "en": "Vancouver International Airport",
                "fr": "Aéroport international de Vancouver",
            },
            {
                "city": "Montreal",
                "province": "QC",
                "station_id": "s0000635",
                "en": "Montreal (Pierre Elliott Trudeau Airport)",
                "fr": "Montréal (aéroport Pierre-Elliott-Trudeau)",
            },
            {
                "city": "Calgary",
                "province": "AB",
                "station_id": "s0000047",
                "en": "Calgary International Airport",
                "fr": "Aéroport international de Calgary",
            },
            {
                "city": "Ottawa",
                "province": "ON",
                "station_id": "s0000430",
                "en": "Ottawa (Macdonald-Cartier Airport)",
                "fr": "Ottawa (aéroport Macdonald-Cartier)",
            },
            {
                "city": "Edmonton",
                "province": "AB",
                "station_id": "s0000045",
                "en": "Edmonton International Airport",
                "fr": "Aéroport international d'Edmonton",
            },
            {
                "city": "Winnipeg",
                "province": "MB",
                "station_id": "s0000193",
                "en": "Winnipeg James Armstrong Richardson Airport",
                "fr": "Aéroport international James Armstrong Richardson de Winnipeg",
            },
            {
                "city": "Halifax",
                "province": "NS",
                "station_id": "s0000318",
                "en": "Halifax (Stanfield International Airport)",
                "fr": "Halifax (aéroport international Stanfield)",
            },
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://weather/aqhi-scale",
    mime_type="application/json",
    name="wx_aqhi_scale",
    title="AQHI Scale — Air Quality Health Index",
)
def wx_aqhi_scale() -> str:
    """AQHI (Air Quality Health Index) scale with risk levels and health guidance.

    Maps AQHI values 1-10+ to risk categories and en/fr health messages.
    Use this to interpret results from wx_get_aqhi and wx_get_aqhi_forecast.
    """
    return json.dumps(
        {
            "scale": [
                {
                    "range": "1-3",
                    "risk": "low",
                    "en": "Low health risk — ideal for outdoor activities",
                    "fr": "Risque faible — idéal pour les activités extérieures",
                },
                {
                    "range": "4-6",
                    "risk": "moderate",
                    "en": "Moderate health risk — consider reducing prolonged outdoor exertion",
                    "fr": "Risque modéré — envisager de réduire les efforts prolongés à l'extérieur",
                },
                {
                    "range": "7-10",
                    "risk": "high",
                    "en": "High health risk — reduce outdoor exertion; at-risk individuals stay indoors",
                    "fr": "Risque élevé — réduire les activités extérieures; personnes à risque rester à l'intérieur",
                },
                {
                    "range": "10+",
                    "risk": "very high",
                    "en": "Very high health risk — avoid outdoor physical activity; at-risk individuals must stay indoors",
                    "fr": "Risque très élevé — éviter toute activité physique extérieure; personnes à risque doivent rester à l'intérieur",
                },
            ],
            "note_en": "AQHI is based on three pollutants: ground-level ozone (O3), nitrogen dioxide (NO2), and fine particulate matter (PM2.5)",
            "note_fr": "L'IQSA est basé sur trois polluants: l'ozone troposphérique (O3), le dioxyde d'azote (NO2) et les particules fines (PM2,5)",
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://weather/climate-normals-periods",
    mime_type="application/json",
    name="wx_climate_normals_periods",
    title="Available Climate Normals Periods",
)
def wx_climate_normals_periods() -> str:
    """Available climate normals periods for wx_get_climate_normals.

    Climate normals are 30-year averages used as baseline reference for comparing
    current climate conditions. The most recent period (1991-2020) is recommended.
    """
    return json.dumps(
        {
            "periods": [
                {
                    "period": "1981-2010",
                    "label_en": "1981–2010 Climate Normals",
                    "label_fr": "Normales climatiques 1981–2010",
                    "status": "previous",
                    "note_en": "Used in older research; still widely referenced",
                    "note_fr": "Utilisées dans les anciennes études; encore largement citées",
                },
                {
                    "period": "1991-2020",
                    "label_en": "1991–2020 Climate Normals",
                    "label_fr": "Normales climatiques 1991–2020",
                    "status": "current",
                    "note_en": "Current standard period — use this for most analyses",
                    "note_fr": "Période standard actuelle — utiliser pour la plupart des analyses",
                },
            ],
            "elements_en": [
                "Daily mean temperature",
                "Daily maximum temperature",
                "Daily minimum temperature",
                "Total precipitation",
                "Total snowfall",
                "Snow depth",
                "Wind speed",
                "Days with precipitation >= 0.2mm",
            ],
            "elements_fr": [
                "Température moyenne quotidienne",
                "Température maximale quotidienne",
                "Température minimale quotidienne",
                "Précipitations totales",
                "Chutes de neige totales",
                "Épaisseur de neige",
                "Vitesse du vent",
                "Jours avec précipitations >= 0,2 mm",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://weather/station-guide",
    mime_type="text/markdown",
    name="wx_station_guide",
    title="MSC GeoMet Weather Station Guide",
)
def wx_station_guide() -> str:
    """Guide to finding and using weather stations in the MSC GeoMet API.

    Explains station ID format, search methods, coverage areas,
    and differences between SWOB, CityPage, AQHI, and hydrometric station networks.
    """
    return """# MSC GeoMet Weather Station Guide

## Station ID Format

MSC GeoMet weather station IDs use the format `s{7-digit-number}` (e.g., `s0000458`).
These are stable identifiers that do not change when stations are renamed.

## Finding a Station

### By City Name

Use `wx_search_stations` with the city name as the query:
```
wx_search_stations(query="Toronto", province="ON")
```

### By Geographic Area

Use `wx_search_stations` with `bbox=[lon_min, lat_min, lon_max, lat_max]`:
```
wx_search_stations(bbox=[-79.6, 43.6, -79.3, 43.8])
```

### Common Stations Catalog

Check the `data://weather/common-stations` resource for major city station IDs
without needing to search.

## Station Networks

| Network | Collection | Tools | Coverage |
|---------|-----------|-------|---------|
| CityPage (urban) | citypageweather-realtime | wx_get_current_conditions, wx_get_forecast | 700+ cities |
| SWOB (surface obs) | swob-realtime | wx_get_station_data | 1,800+ stations |
| AQHI | aqhi-observations-realtime | wx_get_aqhi, wx_get_aqhi_forecast | 130+ communities |
| Hydrometric | hydrometric-realtime | wx_get_water_levels, wx_get_water_flow | 1,700+ stations |
| Climate | climate-daily, climate-monthly | wx_get_climate_daily, wx_get_climate_monthly | 8,000+ historical |

## Province Bounding Boxes

Use `data://weather/province-codes` for the 2-letter province/territory codes
accepted by `wx_search_stations(province=...)`.

## Notes

- CityPage station IDs and SWOB station IDs are **not interchangeable**
- AQHI stations have separate IDs from weather stations
- Hydrometric stations use Water Survey of Canada (WSC) IDs (e.g., `05HD008`)
- Climate stations use 7-digit climate IDs (e.g., `6158731`)
"""


@resource(
    "docs://weather/climate-data-guide",
    mime_type="text/markdown",
    name="wx_climate_data_guide",
    title="MSC GeoMet Climate vs Weather Data Guide",
)
def wx_climate_data_guide() -> str:
    """Guide to climate data types, normals vs observations, and data quality flags.

    Explains the difference between weather (current/forecast) and climate
    (historical/statistical) data, and how to use climate tools effectively.
    """
    return """# MSC GeoMet: Climate vs Weather Data Guide

## Weather Data (Short-term)

**Current observations:** Real-time data updated every 10-60 minutes.
- Tools: `wx_get_current_conditions`, `wx_get_station_data`, `wx_get_aqhi`
- Data: Temperature, humidity, wind, barometric pressure, visibility
- Availability: ~1,800 SWOB stations across Canada

**Forecasts:** Environment Canada public forecasts for 700+ cities.
- Tools: `wx_get_forecast`, `wx_get_aqhi_forecast`
- Horizon: 7-day (hourly for first 24h, then daily)

## Climate Data (Long-term)

**Historical observations:** Daily/monthly records from climate station network.
- Tools: `wx_get_climate_daily`, `wx_get_climate_monthly`
- Availability: Data from the 1800s at some stations; 8,000+ stations

**Climate normals:** 30-year statistical averages for temperature and precipitation.
- Tools: `wx_get_climate_normals`
- Periods: 1981-2010 (previous), 1991-2020 (current)
- Use for: Understanding what is "normal" for a location

**Long-term trends:** Adjusted historical climate data for trend analysis.
- Tools: `wx_get_climate_trends`
- Dataset: AHCCD (Adjusted and Homogenized Canadian Climate Data)
- Use for: Detecting climate change signals (temperature trends, shifting normals)

**Climate projections:** Future climate scenarios under different emission pathways.
- Tools: `wx_get_climate_projections`
- Dataset: CMIP5 and CMIP6 (global climate model ensembles)
- Use for: Adaptation planning, future risk assessment

## Data Quality Flags

Climate observation data includes quality flags:
- `M` — Missing value
- `E` — Estimated value
- `T` — Trace (amount too small to measure)
- `†` — Value may have been affected by station relocation

## Climate Normals vs Historical Observations

| | Normals | Observations |
|---|---------|-------------|
| What | Statistical average | Actual recorded values |
| Timeframe | 30-year period | Day-by-day records |
| Tool | `wx_get_climate_normals` | `wx_get_climate_daily` |
| Use case | "What is typical?" | "What actually happened?" |

## Drought Index (SPEI)

The Standardized Precipitation Evapotranspiration Index (SPEI) measures drought severity:
- Tool: `wx_get_drought_index`
- Dataset: SPEI-3 (3-month accumulation period)
- Values: Negative = drought, Positive = wet conditions
"""


@resource(
    "docs://weather/ogc-api-guide",
    mime_type="text/markdown",
    name="wx_ogc_api_guide",
    title="MSC GeoMet OGC API Features Guide",
)
def wx_ogc_api_guide() -> str:
    """Overview of the MSC GeoMet OGC API, collection types, and query patterns.

    The MSC GeoMet API follows the OGC API Features standard. Understanding
    collection IDs and item query patterns helps with advanced data retrieval.
    """
    return """# MSC GeoMet OGC API Features Guide

## API Overview

The MSC GeoMet OGC API (api.weather.gc.ca) provides access to Environment Canada
meteorological, hydrological, and climate data via the OGC API Features standard.

**Base URL:** `https://api.weather.gc.ca`
**Standard:** OGC API - Features (ISO 19168-1:2020)
**Format:** GeoJSON (default), CSV, CSV-GEOM

## Key Endpoints

| Endpoint | Purpose |
|---------|--------|
| `/collections` | List all available data collections |
| `/collections/{collectionId}` | Collection metadata and spatial extent |
| `/collections/{collectionId}/items` | Query features (data items) |
| `/collections/{collectionId}/items/{featureId}` | Single feature by ID |

## Collection Types

### Real-time Collections (updated 10-60min)
- `citypageweather-realtime` — CityPage weather for 700+ cities
- `swob-realtime` — Surface Weather Observation (SWOB) stations
- `aqhi-observations-realtime` — Air quality (AQHI) observations
- `hydrometric-realtime` — Water level and flow (hourly)
- `weather-alerts` — Active watches, warnings, advisories

### Climate Collections (historical)
- `climate-daily` — Daily climate station observations
- `climate-monthly` — Monthly climate summaries
- `climate-normals` — 30-year climate normals
- `ahccd-trends` — Long-term adjusted climate trends

### Model/Projection Collections
- `climate:cmip5:projected:annual:anomaly` — CMIP5 projections
- `climate:dcs:projected:annual:absolute` — CMIP6 projections
- `climate:spei-3:historical` — SPEI drought index

## Common Query Parameters

| Parameter | Description | Example |
|---------|-------------|---------|
| `bbox` | Bounding box [lon_min, lat_min, lon_max, lat_max] | `-79.6,43.6,-79.3,43.8` |
| `limit` | Max features to return (default 10, max 10000) | `100` |
| `offset` | Pagination offset | `100` |
| `datetime` | Filter by date/time | `2024-01-15` or `2024-01-01/2024-01-31` |
| `properties` | Select specific fields | `TEMP_MEAN,TOTAL_PRECIP` |

## Browsing Collections

Use `wx_list_collections` to see all available collection IDs and descriptions.
Use `wx_get_collection_items` to query any collection with custom parameters.

## Rate Limits

The MSC GeoMet API is publicly accessible with no authentication required.
mcp-canada enforces 20 req/s via TokenBucket to avoid server overload.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://weather/forecast-report",
    mime_type="text/markdown",
    name="wx_forecast_report_template",
    title="Weather Forecast Report Template",
)
def wx_forecast_report_template() -> str:
    """Template for formatting a weather forecast report.

    Replace {placeholder} values with actual data from wx_get_current_conditions
    and wx_get_forecast before presenting to the user.
    """
    return """# Weather Report: {city}

**Station:** {station_name} ({station_id})
**Province:** {province}
**As of:** {observation_time}
**Source:** Environment Canada MSC GeoMet

## Current Conditions

| Metric | Value |
|--------|-------|
| Temperature | {temperature}°C |
| Feels Like | {feels_like}°C |
| Humidity | {humidity}% |
| Wind | {wind_direction} {wind_speed} km/h |
| Visibility | {visibility} km |
| Condition | {condition} |

## Forecast

{forecast_periods}

## Alerts

{alerts_or_none}

## Notes

Data from Environment Canada via the MSC GeoMet OGC API.
"""
