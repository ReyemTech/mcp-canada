"""Constants for the alberta module — quad-source layout.

All URLs, rate groups, TTLs, product tuples, and org slugs are live-verified against
production APIs (2026-04-17). See 17-RESEARCH.md § "Pattern 1: Quad-Source Constants
Layout" for the canonical specification.

Four portals:
  - CKAN: open.alberta.ca  (33,269 datasets; 370 orgs; res_format facet used for categories)
  - GeoDiscover Alberta ArcGIS REST 11.3: geospatial.alberta.ca/titan/rest/services
  - WMBappServices (ArcGIS Online): services.arcgis.com/Eb8P5h4CJk8utIBz (wildfire)
  - AHSGIS (ArcGIS Online): services5.arcgis.com/7KHJ4f28UDLgUq2U (health)
  - AER static: static.aer.ca/prd (ST1 well licences, ST3 production, ST39 pipelines, ST98)
  - 511 Alberta: 511.alberta.ca/api/v2/get (road events, winter roads, cameras)

Pitfall 8 (ST3 product casing): product slugs MUST match exact-case URL segments;
Butane_current.xlsx is valid while butane_current.xlsx 404s.
"""

from typing import Final

# ---------------------------------------------------------------------------
# HTTP identification — set for proper API identification (Quebec convention)
# ---------------------------------------------------------------------------

USER_AGENT: Final[str] = "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"
DEFAULT_HEADERS: Final[dict[str, str]] = {"User-Agent": USER_AGENT}

# Alberta-specific cache key prefix — distinguishes alberta keys from federal
# CKAN / BC / Quebec / Ontario / Toronto in the shared aiocache store.
CACHE_KEY_PREFIX: Final[str] = "alberta:"

# ---------------------------------------------------------------------------
# CKAN — open.alberta.ca
# ---------------------------------------------------------------------------

CKAN_BASE_URL: Final[str] = "https://open.alberta.ca/api/3/action/"
RATE_GROUP_CKAN: Final[str] = "alberta_ckan"
RATE_LIMIT_CKAN: Final[float] = 10.0

# ---------------------------------------------------------------------------
# GeoDiscover Alberta — Esri ArcGIS REST 11.3
# ---------------------------------------------------------------------------

GEODISCOVER_BASE_URL: Final[str] = "https://geospatial.alberta.ca/titan/rest/services"
RATE_GROUP_GEODISCOVER: Final[str] = "alberta_geodiscover"
RATE_LIMIT_GEODISCOVER: Final[float] = 5.0

# AQHI air monitoring
AQHI_AIR_LAYER_URL: Final[str] = (
    f"{GEODISCOVER_BASE_URL}/aqhi/air_layers/MapServer"
)
AQHI_STATIONS_LAYER_ID: Final[int] = 1
# Water / river forecast
RIVER_FORECAST_FS_URL: Final[str] = (
    f"{GEODISCOVER_BASE_URL}/environment/river_forecast_centre/FeatureServer"
)
# Parks
PROVINCIAL_PARKS_FS_URL: Final[str] = (
    f"{GEODISCOVER_BASE_URL}/boundary/parks_protected_areas_alberta/FeatureServer"
)

# ---------------------------------------------------------------------------
# WMBappServices ArcGIS Online — Wildfire Management Branch
# ---------------------------------------------------------------------------

WMB_ORG_BASE: Final[str] = (
    "https://services.arcgis.com/Eb8P5h4CJk8utIBz/arcgis/rest/services"
)
RATE_GROUP_WMB: Final[str] = "alberta_wmb"
RATE_LIMIT_WMB: Final[float] = 5.0

ACTIVE_WILDFIRES_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Active_Wildfires_Dashboard_view/FeatureServer"
)
ACTIVE_FIRE_PERIMETERS_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Active_Wildfire_Perimeters_Simplified_view/FeatureServer"
)
EXTINGUISHED_WILDFIRES_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Extinguished_Wildfires_Locations/FeatureServer"
)
EXTINGUISHED_PERIMETERS_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Extinguished_Wildfire_Perimeters_Simplified_view/FeatureServer"
)
FIRE_BAN_SYSTEM_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/alberta_fire_ban_system/FeatureServer"
)
FIRE_CONTROL_ORDERS_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Fire_Control_Orders_Prod_View2/FeatureServer"
)
OHV_RESTRICTION_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/OHV_RestrictionL_Prod_View/FeatureServer"
)
FOREST_AREA_FS_URL: Final[str] = (
    f"{WMB_ORG_BASE}/Forest_Area_Prod_View2/FeatureServer"
)

# ---------------------------------------------------------------------------
# AHSGIS ArcGIS Online — Alberta Health Services
# ---------------------------------------------------------------------------

AHS_ORG_BASE: Final[str] = (
    "https://services5.arcgis.com/7KHJ4f28UDLgUq2U/arcgis/rest/services"
)
RATE_GROUP_AHS: Final[str] = "alberta_ahs"
RATE_LIMIT_AHS: Final[float] = 5.0

AHS_HOSPITALS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/AHS_Hospitals/FeatureServer"
AHS_ZONE_FS_URL: Final[str] = f"{AHS_ORG_BASE}/AHS_Zone/FeatureServer"
AHS_EMS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/EMS_Stations/FeatureServer"
PCN_CLINICS_FS_URL: Final[str] = f"{AHS_ORG_BASE}/PCN_Clinics/FeatureServer"

# ---------------------------------------------------------------------------
# AER (Alberta Energy Regulator) — static XLSX / TXT / ZIP downloads
# ---------------------------------------------------------------------------

AER_STATIC_BASE: Final[str] = "https://static.aer.ca/prd"
RATE_GROUP_AER: Final[str] = "alberta_aer"
RATE_LIMIT_AER: Final[float] = 2.0  # static files; conservative

# ST1 daily well licences (TXT overwritten daily — WELLS{MON..SUN}.TXT)
AER_ST1_DAILY_BASE: Final[str] = f"{AER_STATIC_BASE}/data/well-lic"
# ST1 monthly / annual archive ZIP (pattern: dwll{YYYY}-{MM}.zip, dwll{YYYY}.zip)
AER_ST1_MONTHLY_BASE: Final[str] = f"{AER_STATIC_BASE}/data/well-lic"
# ST3 monthly production XLSX (per product)
AER_ST3_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts/st3"
# ST39 annual pipeline statistics (XLSX/PDF) and general STS folder
AER_ST39_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts"
# ST98 annual energy outlook (XLSX per topic)
AER_ST98_BASE: Final[str] = f"{AER_STATIC_BASE}/documents/sts/st98"

# ST3 product slugs — EXACT CASE verified 2026-04-17 (Pitfall 8).
# Butane_current.xlsx works; butane_current.xlsx 404s.
ST3_PRODUCTS: Final[tuple[str, ...]] = (
    "Butane",
    "Ethane",
    "NGL",
    "Oil",
    "Gas",
    "Propane",
    "Sulphur",
)

# ---------------------------------------------------------------------------
# 511 Alberta — undocumented but public JSON API
# ---------------------------------------------------------------------------

FIVE11_BASE_URL: Final[str] = "https://511.alberta.ca/api/v2/get"
RATE_GROUP_511: Final[str] = "alberta_511"
RATE_LIMIT_511: Final[float] = 2.0  # conservative; no published limit

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------

CACHE_TTL_SEARCH: Final[int] = 3600     # 1hr — CKAN search
CACHE_TTL_META: Final[int] = 86400      # 24hr — package_show, org list, layer metadata
CACHE_TTL_LIVE: Final[int] = 300        # 5min — active fires, fire bans, road events, AQHI
CACHE_TTL_DAILY: Final[int] = 3600      # 1hr — AER ST1 daily TXT (regenerated daily)
CACHE_TTL_MONTHLY: Final[int] = 86400   # 24hr — AER ST3 monthly, 511 cameras (stable)
CACHE_TTL_STATIC: Final[int] = 86400    # 24hr — hospitals, AHS zones, forest areas
CACHE_TTL_ANNUAL: Final[int] = 604800   # 7d — AER ST39, ST98 (annual)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# Organization slugs (verified live 2026-04-17 — 370-org federated catalogue)
# ---------------------------------------------------------------------------

ORG_FORESTRY_PARKS: Final[str] = "forestry-and-parks"
ORG_ENERGY_MINERALS: Final[str] = "energy-and-minerals"
ORG_ENV_PROTECTED: Final[str] = "environment-and-protected-areas"
ORG_AGRICULTURE: Final[str] = "agriculture-and-irrigation"
ORG_TRANSPORTATION: Final[str] = "transportation-and-economic-corridors"
ORG_HEALTH: Final[str] = "health"
ORG_TBF: Final[str] = "treasuryboardandfinance"
ORG_SOCIAL: Final[str] = "assisted-living-and-social-services"
ORG_EDUCATION: Final[str] = "education-and-childcare"
ORG_CHILDREN: Final[str] = "children-and-family-services"
ORG_AFFORDABILITY: Final[str] = "affordability-and-utilities"
ORG_SERVICE_AB: Final[str] = "servicealberta"
ORG_PUBLIC_SAFETY: Final[str] = "public-safety-and-emergency-services"
ORG_ADV_ED: Final[str] = "advancededucation"

# ---------------------------------------------------------------------------
# AER ST1 daily TXT — day-of-week abbreviation map
# ---------------------------------------------------------------------------
# AER publishes WELLS{MON}.TXT ... WELLS{SUN}.TXT overwritten each weekday.
# datetime.weekday() returns 0=Mon..6=Sun; map to the AER URL suffix.

DAY_ABBR: Final[dict[int, str]] = {
    0: "MON",
    1: "TUE",
    2: "WED",
    3: "THU",
    4: "FRI",
    5: "SAT",
    6: "SUN",
}
