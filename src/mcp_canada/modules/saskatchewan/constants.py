"""Saskatchewan module constants.

Saskatchewan uses ArcGIS Hub (geohub.saskatchewan.ca / org zcv98lgAl8xQ04cW), NOT CKAN.
NEVER reference data.saskatchewan.ca — this domain does NOT exist (Saskatchewan has no CKAN portal).
Water = WSA org 7MBdlVpjqbfBhQer (services1.arcgis.com);
Fire bans = SPSA gis.saskatchewan.ca/egis (separate ArcGIS REST server, NOT part of the Hub).

Three ArcGIS bases:
  1. Primary Hub org: services3.arcgis.com/zcv98lgAl8xQ04cW — agriculture, mining, environment
  2. WSA org: services1.arcgis.com/7MBdlVpjqbfBhQer — water infrastructure (WSA)
  3. SPSA egis: gis.saskatchewan.ca/egis/rest/services/Wildfire — fire bans (non-Hub REST)

Spike findings (19-SPIKE.md, 2026-06-15):
  - Petroleum FeatureServer: REVISED — HTTP 200 confirmed (not 400 as in research);
    deferred per tool-count ceiling (14 tools at target). Document as accessible.
  - WSA Water Quality layer 19: REVISED — 24 stations usable; not in Phase 19 curated tools.
  - WSA_Reservoirs layer 26: CONFIRMED — Reservoir_Name present.
  - SPSA Fire Ban layers 0/2/3/8: CONFIRMED — all 4 ban layers exist.
  - GeoHub startindex pagination: CONFIRMED working after shared/arcgis_hub.py fix.
"""

from typing import Final

# ---------------------------------------------------------------------------
# Saskatchewan GeoHub (primary org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
HUB_BASE_URL: Final[str] = "https://geohub.saskatchewan.ca"
ARCGIS_ORG_ID: Final[str] = "zcv98lgAl8xQ04cW"
HUB_ORG_BASE: Final[str] = f"https://services3.arcgis.com/{ARCGIS_ORG_ID}/arcgis/rest/services"
HUB_SEARCH_URL: Final[str] = f"{HUB_BASE_URL}/api/search/v1/collections/all/items"

# ---------------------------------------------------------------------------
# SPSA Wildfire GIS (separate REST server — NOT ArcGIS Hub)
# NEVER use /arcgis/rest/services/ (no /egis/) — returns 499 Token Required
# ---------------------------------------------------------------------------
SPSA_BASE_URL: Final[str] = "https://gis.saskatchewan.ca/egis/rest/services/Wildfire"
FIRE_BAN_FS_URL: Final[str] = f"{SPSA_BASE_URL}/Public_Fire_Ban/FeatureServer"

# Spike-confirmed layers (2026-06-15): 0=Urban, 2=Rural, 3=Provincial, 8=Parks
# Layers 1,5,6,7,9,10 are reference/display-only — NOT ban data
FIRE_BAN_LAYERS: Final[dict[str, int]] = {
    "urban": 0,
    "rural": 2,
    "provincial": 3,
    "parks": 8,
}

RATE_GROUP_SPSA: Final[str] = "saskatchewan_spsa"
RATE_LIMIT_SPSA: Final[float] = 5.0

# ---------------------------------------------------------------------------
# WSA GeoHub (org: 7MBdlVpjqbfBhQer — Water Security Agency)
# ---------------------------------------------------------------------------
WSA_ORG_ID: Final[str] = "7MBdlVpjqbfBhQer"
WSA_ORG_BASE: Final[str] = f"https://services1.arcgis.com/{WSA_ORG_ID}/arcgis/rest/services"

RATE_GROUP_WSA: Final[str] = "saskatchewan_wsa"
RATE_LIMIT_WSA: Final[float] = 5.0

# ---------------------------------------------------------------------------
# Rate group for Hub and agriculture/mining (primary org)
# ---------------------------------------------------------------------------
RATE_GROUP_HUB: Final[str] = "saskatchewan_hub"
RATE_LIMIT_HUB: Final[float] = 10.0

# ---------------------------------------------------------------------------
# Agriculture FeatureServers (org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
CROP_YIELDS_PROVINCE_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer"
)
CROP_YIELDS_REGIONS_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer"
)
GRAIN_ELEVATORS_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Western_Canada_Grain_Elevator_2024/FeatureServer"
)

# Valid crop regions (provincial dispatches to Province Summary FS; others to Regions Only FS)
CROP_REGIONS: Final[tuple[str, ...]] = (
    "provincial",
    "southeast",
    "southwest",
    "central",
    "northeast",
    "northwest",
)

# ---------------------------------------------------------------------------
# Energy / Mining FeatureServers (org: zcv98lgAl8xQ04cW)
# Dated services — filenames carry the publication date
# ---------------------------------------------------------------------------
MINERAL_MINES_FS_URLS: Final[dict[str, str]] = {
    "potash": f"{HUB_ORG_BASE}/Potash_2024_06_13/FeatureServer",
    "uranium": f"{HUB_ORG_BASE}/Uranium_2024_06_13/FeatureServer",
    "helium": f"{HUB_ORG_BASE}/Helium_2024_12_31/FeatureServer",
    "coal": f"{HUB_ORG_BASE}/Coal_2024_06_13/FeatureServer",
}

# ---------------------------------------------------------------------------
# Environment / Wildfire FeatureServers (org: zcv98lgAl8xQ04cW)
# ---------------------------------------------------------------------------
WILDFIRE_BOUNDARIES_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Historic_Wildfire_Boundaries/FeatureServer"
)
WILDFIRE_ORIGINS_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Historic_Wildfire_Origins/FeatureServer"
)
AIR_QUALITY_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Hourly_Ambient_Air_Quality/FeatureServer"
)
AIR_QUALITY_COMMUNITIES: Final[list[str]] = [
    "Regina",
    "Saskatoon",
    "Prince Albert",
    "Estevan",
    "Swift Current",
    "Buffalo Narrows",
]

# ---------------------------------------------------------------------------
# WSA Water Infrastructure FeatureServers (org: 7MBdlVpjqbfBhQer)
# ---------------------------------------------------------------------------
WSA_STATIONS_FS_URL: Final[str] = (
    f"{WSA_ORG_BASE}/Hydrometric_Gauging_Stations_V2/FeatureServer"
)
WSA_STATIONS_LAYER: Final[int] = 0

WSA_RESERVOIRS_FS_URL: Final[str] = f"{WSA_ORG_BASE}/WSA_Reservoirs/FeatureServer"
WSA_RESERVOIRS_LAYER: Final[int] = 26  # NOT layer 0 — spike-confirmed 2026-06-15

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 900        # 15min — air quality (hourly readings)
CACHE_TTL_ALERTS: Final[int] = 300      # 5min — fire bans (live emergency data)
CACHE_TTL_SEARCH: Final[int] = 3600     # 1h — hub search
CACHE_TTL_META: Final[int] = 86400      # 24h — grain elevators, minerals, WSA, wildfires
CACHE_TTL_ANNUAL: Final[int] = 604800   # 7d — crop yields (annual estimates)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# HTTP headers
# ---------------------------------------------------------------------------
USER_AGENT: Final[str] = "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"
CACHE_KEY_PREFIX: Final[str] = "saskatchewan:"
