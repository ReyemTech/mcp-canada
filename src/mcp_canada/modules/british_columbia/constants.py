"""Constants for the british_columbia module — CKAN base URLs, WFS endpoint, rate/cache config,
and the 15 curated BCGW object_name layer constants.

NOTE: CLIMATE_STATIONS_LAYER intentionally aliases WEATHER_STATIONS_LAYER — both reference the
same BCGW layer (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP) but bc_get_climate_stations
exposes it with a climate-oriented docstring and query parameters, per RESEARCH.md §Climate (1 tool).
"""

from typing import Final

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

BASE_URL: Final[str] = "https://catalogue.data.gov.bc.ca/api/3/action/"
WFS_BASE_URL: Final[str] = "https://openmaps.gov.bc.ca/geo/ows"

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

RATE_GROUP_CKAN: Final[str] = "bc_ckan"
RATE_GROUP_WFS: Final[str] = "bc_wfs"
RATE_LIMIT_CKAN: Final[float] = 10.0    # req/s for BC Data Catalogue CKAN API
RATE_LIMIT_WFS: Final[float] = 5.0      # req/s for BC Geographic Warehouse WFS

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------

CACHE_TTL_SEARCH: Final[int] = 3600     # 1hr — CKAN search results
CACHE_TTL_META: Final[int] = 86400      # 24hr — CKAN dataset metadata (package_show)
CACHE_TTL_ACTIVE: Final[int] = 300      # 5min — active fires (refresh every 15min on source)
CACHE_TTL_STATIC: Final[int] = 86400   # 24hr — parks, tenure, water wells, climate stations
CACHE_TTL_CAPS: Final[int] = 3600      # 1hr — WFS GetCapabilities (large XML, changes rarely)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

MAX_RECORDS: Final[int] = 5000
WFS_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# BCGW curated layer object_name constants
# (verified against BC Geographic Warehouse — see 15-RESEARCH.md §Curated Dataset Catalog)
# ---------------------------------------------------------------------------

# Wildfire
ACTIVE_FIRES_LAYER: Final[str] = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP"
FIRE_PERIMETERS_LAYER: Final[str] = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"

# Forestry
FOREST_TENURE_LAYER: Final[str] = "WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW"
CUT_BLOCKS_LAYER: Final[str] = "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW"

# Environment / Protected Areas
PROTECTED_AREAS_LAYER: Final[str] = "WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW"
WATER_WELLS_LAYER: Final[str] = "WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW"

# Wildfire Weather
WEATHER_STATIONS_LAYER: Final[str] = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP"

# Parks
LOCAL_PARKS_LAYER: Final[str] = "WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP"

# Mining
MINING_TENURE_LAYER: Final[str] = "WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW"

# Wildlife / Fish
FISH_HABITAT_LAYER: Final[str] = "WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS"

# Health Facilities
EMERGENCY_ROOMS_LAYER: Final[str] = "WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV"
WALK_IN_CLINICS_LAYER: Final[str] = "WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV"

# Transportation
HIGHWAY_PROFILES_LAYER: Final[str] = "WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP"
ROAD_STRUCTURES_LAYER: Final[str] = "WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP"

# Climate — intentionally aliases WEATHER_STATIONS_LAYER (same BCGW layer, climate docstring)
CLIMATE_STATIONS_LAYER: Final[str] = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP"
