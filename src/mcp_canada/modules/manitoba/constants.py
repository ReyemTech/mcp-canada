"""Manitoba module constants.

Manitoba uses ArcGIS Hub (geoportal.gov.mb.ca / org mMUesHYPkXjaFGfS), NOT CKAN.
NEVER reference data.manitoba.ca (unreachable) or mli.gov.mb.ca (retired 2022-02-09).

All FeatureServer URLs are under:
  https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/

Spike findings (18-SPIKE.md, 2026-06-14):
  - Rural Health FeatureServer: RESOLVED — Rural_Health_Care_Facilities_in_Manitoba/FeatureServer
  - Hog prices FS: UNRESOLVED — not found in org; Plan 04 investigates
  - River Conditions: RESOLVED as CSV (not FeatureServer) — www.manitoba.ca/floodinfo/.../agoldataV2.csv
  - Manitoba 511 key: GATED — account + explicit key request; tools return NOT_CONFIGURED
"""

from typing import Final

# ---------------------------------------------------------------------------
# Data MB — geoportal.gov.mb.ca (ArcGIS Hub)
# ---------------------------------------------------------------------------
HUB_BASE_URL: Final[str] = "https://geoportal.gov.mb.ca"
ARCGIS_ORG_ID: Final[str] = "mMUesHYPkXjaFGfS"
HUB_ORG_BASE: Final[str] = "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services"
HUB_SEARCH_URL: Final[str] = f"{HUB_BASE_URL}/api/search/v1/collections/all/items"

# ---------------------------------------------------------------------------
# Rate groups
# ---------------------------------------------------------------------------
RATE_GROUP_HUB: Final[str] = "manitoba_hub"
RATE_LIMIT_HUB: Final[float] = 10.0  # 10 req/s (ArcGIS Hub — conservative)

RATE_GROUP_511: Final[str] = "manitoba_511"
RATE_LIMIT_511: Final[float] = 2.0  # 10 calls/60s documented; conservative

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 300        # 5min — flood alerts, road events, winter roads, river CSV
CACHE_TTL_SEARCH: Final[int] = 3600     # 1h — hub search
CACHE_TTL_META: Final[int] = 86400      # 24h — parks, waterways, facilities, weather stations, livestock prices
CACHE_TTL_STATIC: Final[int] = 86400   # 24h — drought monitor (weekly update at source)
CACHE_TTL_ANNUAL: Final[int] = 604800   # 7d — surgical wait times (annual data)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# HTTP headers
# ---------------------------------------------------------------------------
USER_AGENT: Final[str] = "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"
CACHE_KEY_PREFIX: Final[str] = "manitoba:"

# ---------------------------------------------------------------------------
# Flood / Hydrology FeatureServers (all live-verified 2026-06-13)
# ---------------------------------------------------------------------------
FLOOD_ALERTS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Overland_Flood_Alerts/FeatureServer"
# Flood alerts layer 0 fields: OBJECTID, Type_EN, Type_FR, Start_Date, End_Date, Shape__Area
# MaxRecordCount: 2000. Returns [] when no alerts active — this is CORRECT, not an error.

PROVINCIAL_WATERWAYS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Provincial_Waterways/FeatureServer"
# Waterways layer 0 fields: F_TYPE (Dike/Floodway/Dam/Diversion/Reservoir/Waterway/...), Name, Watershed, WCW, LengthKM

# River Conditions: CSV feed (NOT a FeatureServer — spike resolution 2026-06-14)
RIVER_CONDITIONS_CSV_URL: Final[str] = (
    "https://www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv"
)
# CSV fields: id, stationId, stationName, latitude, longitude, measurementDate,
# measuredFlow, measuredLevel, forecastedFlow, forecastedLevel, forecastedPeakDate,
# floodStage, alert, wscRealTimeData, dateRecorded, waterLevel, discharge, province, ...
# alert values: "No Flooding" | "High Water Advisory" | "Flood Watch" | "Flood Warning" | "No Current Data"

# ---------------------------------------------------------------------------
# Agriculture / Drought FeatureServers (all live-verified 2026-06-13)
# ---------------------------------------------------------------------------
CATTLE_PRICES_FS_URL: Final[str] = f"{HUB_ORG_BASE}/MB_Cattle_Prices_Current_year/FeatureServer"
# Fields: week, Auction, Parameter, Measure, Value

# Hog prices: UNRESOLVED in Wave 0 spike — not found in mMUesHYPkXjaFGfS org services list.
# Plan 04 must probe MB_Cattle_Prices_Current_year for mixed cattle+hog data,
# or search AgriMaps (agrimaps.gov.mb.ca/arcgis/rest/services/AGRIMAPS/).
# Re-probe: curl -s "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MB_Cattle_Prices_Current_year/FeatureServer/0/query?where=1%3D1&outFields=Parameter%2CMeasure%2CAuction&resultRecordCount=20&f=json"
HOG_PRICES_FS_URL: Final[str | None] = None  # UNRESOLVED — Plan 04 resolves

AG_WEATHER_STATIONS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/WeatherStations/FeatureServer"
# Fields: StnName, LatDD, LongDD, Elevation, AgRegion, URL (link to live hourly data per station)

CROP_REGIONS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/MbAg_Crop_Reporting_Regions/FeatureServer"
# Fields: OBJECTID, REGION (English), RÉGION (French) — bilingual boundary polygons

DROUGHT_MONITOR_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Canada_USA_Drought_Monitor/FeatureServer"
# Fields: DM (D0/D1/D2/D3/D4), OBS_DATE, SOURCE — continental coverage (filter by Manitoba BBOX)

# ---------------------------------------------------------------------------
# Environment / Parks FeatureServers (all live-verified 2026-06-13)
# ---------------------------------------------------------------------------
PROVINCIAL_PARKS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Parks/FeatureServer"
# Layer 0, 93 parks, fields: NAME_E, NOM_F, BIOME, O_AREA, TYPE_E, TYPE_F, STATUS_E, PROTDATE, PRK_CLSS, URL

WATERBODY_DATA_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Waterbody_Data/FeatureServer"
# 350+ water bodies, 26 fields including species, stocking records, Secchi depth, fishing regulations

PROVINCIAL_FORESTS_FS_URL: Final[str] = f"{HUB_ORG_BASE}/Manitoba_Provincial_Forests___Version_6/FeatureServer"
# Provincial forest management unit polygons

# ---------------------------------------------------------------------------
# Health FeatureServers
# ---------------------------------------------------------------------------
SURGICAL_WAIT_TIMES_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages/FeatureServer"
)
# Fields: Year, IndicatorDataArea, Average_Wait — annual averages by procedure
# MaxRecordCount: 1000. Live-verified: cardiac surgery 60→144 days 2019-2021.

RURAL_HEALTH_FACILITIES_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Rural_Health_Care_Facilities_in_Manitoba/FeatureServer"
)
# Layer 0, MaxRecordCount 2000. Spike-resolved 2026-06-14.
# Fields: Community_Name, Facility_Name, Lat, Long, Emergency_Department_Availabili,
# Percentage_of_Time_Open__2015_, Nearest_Alternate_Emergency_Dep,
# Acute_Care_Availability, Acute_Care_Number_of_Beds, ...

# ---------------------------------------------------------------------------
# Manitoba 511 REST API (conditional — key required)
# VERDICT: GATED — requires account + explicit API key request (see 18-SPIKE.md § 1)
# ---------------------------------------------------------------------------
FIVE11_BASE_URL: Final[str] = "https://www.manitoba511.ca/api/v3/get"
FIVE11_KEY_ENV: Final[str] = "MANITOBA_511_KEY"
# Usage: tools read key from os.environ.get(FIVE11_KEY_ENV, "")
# If absent → return make_error("NOT_CONFIGURED", "Manitoba 511 API key required. ...")
# 511 endpoints return raw JSON list (NOT ArcGIS/CKAN envelope)
# Rate: 10 calls/60s documented; RATE_LIMIT_511 = 2.0 r/s (conservative)

# ---------------------------------------------------------------------------
# Spatial constants
# ---------------------------------------------------------------------------
# Manitoba approximate bounding box (lon_min, lat_min, lon_max, lat_max)
# Used by drought monitor and other province-wide filters (Pitfall 8 from research)
MANITOBA_BBOX: Final[str] = "-101.36,48.99,-95.15,60.0"

# ---------------------------------------------------------------------------
# Dispatch tuples (used by tools for Literal validation + WHERE clauses)
# ---------------------------------------------------------------------------
PARK_TYPES: Final[tuple[str, ...]] = (
    "Provincial",
    "Heritage",
    "Wilderness",
    "Recreation",
    "Natural",
    "Park Reserve",
    "Indigenous Traditional Use",
)

WATERWAY_TYPES: Final[tuple[str, ...]] = (
    "dike",
    "floodway",
    "dam",
    "diversion",
    "reservoir",
    "waterway",
)
