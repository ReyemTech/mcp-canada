"""Constants for the york_region module — portal URLs, Feature Service endpoints, rate/cache config."""

from typing import Final

# ---------------------------------------------------------------------------
# Portal base URLs — None means no public ArcGIS Hub as of 2026-04
# ---------------------------------------------------------------------------

PORTAL_URLS: Final[dict[str, str | None]] = {
    "york_region": "https://insights-york.opendata.arcgis.com",
    "markham": "https://data-markham.opendata.arcgis.com",
    "newmarket": "https://navigate-newmarket.hub.arcgis.com",
    "aurora": "https://town-of-aurora-data-hub-aurora.hub.arcgis.com",
    "vaughan": None,
    "richmond_hill": None,
    "king": None,
    "east_gwillimbury": None,
    "whitchurch_stouffville": "https://whitchurch-stouffville-census-hub-2021-townofws.hub.arcgis.com",  # census-only
    "georgina": None,
}

# ---------------------------------------------------------------------------
# York Region on-premise ArcGIS Server
# ---------------------------------------------------------------------------

YR_FEATURE_SERVER_BASE: Final[str] = "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData"

# Transportation
YR_TRANSIT_FS: Final[str] = f"{YR_FEATURE_SERVER_BASE}/Transportation/FeatureServer"
YR_REGIONAL_ROADS_LAYER: Final[int] = 0    # 762 records
YR_ALL_ROADS_LAYER: Final[int] = 1
YR_BUS_STOPS_LAYER: Final[int] = 2         # 4,810 records, maxRecordCount=1000
YR_BUS_ROUTES_LAYER: Final[int] = 3

# Health & Safety
YR_HEALTH_FS: Final[str] = f"{YR_FEATURE_SERVER_BASE}/Health_And_Safety/FeatureServer"
YR_BEACH_TESTING_LAYER: Final[int] = 0
YR_HOSPITAL_LAYER: Final[int] = 1

# Environmental
YR_ENVIRONMENTAL_FS: Final[str] = f"{YR_FEATURE_SERVER_BASE}/Environmental/FeatureServer"
YR_SOLID_WASTE_SITES_LAYER: Final[int] = 0

# Drinking Water
YR_DRINKING_WATER_FS: Final[str] = f"{YR_FEATURE_SERVER_BASE}/DrinkingWater/FeatureServer"
YR_DRINKING_WATER_ADVERSE_LAYER: Final[int] = 0

# ---------------------------------------------------------------------------
# Census on ArcGIS Online (York Region org)
# ---------------------------------------------------------------------------

YR_CENSUS_ORG: Final[str] = "GzvOwaQBbX7KLiuG"
YR_CENSUS_BASE: Final[str] = f"https://services1.arcgis.com/{YR_CENSUS_ORG}/arcgis/rest/services"
YR_AGE_SEX_FS: Final[str] = (
    f"{YR_CENSUS_BASE}/myProfile_of_Age_and_Sex_by_Dissemination_Area__2021_Census/FeatureServer"
)
YR_INCOME_FS: Final[str] = (
    f"{YR_CENSUS_BASE}/myProfile_of_Total_Income_by_Census_Dissemination_Area__2021_Census/FeatureServer"
)
YR_WASTE_DIVERSION_FS: Final[str] = (
    f"{YR_CENSUS_BASE}/Waste_Diversion_Statistics_(Annual_Waste_Tonnages_-_Collected)/FeatureServer"
)
YR_CENSUS_LAYER: Final[int] = 0

# Focused field sets (all 364 census fields is too many by default)
YR_CENSUS_AGE_FIELDS: Final[str] = (
    "CSDNAME,DAUID,TOT_POP,M_TOTAL,F_TOTAL,TOT_AVG_AGE_POP,TOT_MED_AGE_POP,"
    "TOT_0_TO_14_YRS,TOT_15_TO_64_YRS,TOT_65_YRS_OVER"
)
YR_CENSUS_INCOME_FIELDS: Final[str] = (
    "CSDNAME,DAUID,MEDIAN_INCOME,AVERAGE_INCOME,LOW_INCOME_CUT_OFF"
)

# ---------------------------------------------------------------------------
# Markham curated FS (proxied URLs via utility.arcgis.com — may rotate)
# ---------------------------------------------------------------------------

MARKHAM_ADDRESSES_FS: Final[str] = (
    "https://utility.arcgis.com/usrsvcs/servers/"
    "7791a0d2e3d3422b8eab3c800be5c4e7/rest/services/OpenData/OD_ADDRESSES/FeatureServer"
)
MARKHAM_ROADS_FS: Final[str] = (
    "https://utility.arcgis.com/usrsvcs/servers/"
    "264f35f118324ee0a40ffa53714b23fe/rest/services/OpenData/OD_SLRN/FeatureServer"
)
MARKHAM_ADDRESSES_LAYER: Final[int] = 0
MARKHAM_ROADS_LAYER: Final[int] = 0

# ---------------------------------------------------------------------------
# Rate limiting & cache TTLs
# ---------------------------------------------------------------------------

RATE_GROUP: Final[str] = "arcgis_hub"
RATE_LIMIT: Final[float] = 5.0     # req/s shared across all 4 portals

CACHE_TTL_SEARCH: Final[int] = 3600     # 1hr for Hub Search results
CACHE_TTL_META: Final[int] = 86400      # 24hr for layer metadata
CACHE_TTL_DATA: Final[int] = 3600       # 1hr for Feature Service data
CACHE_TTL_ORGS: Final[int] = 86400      # 24hr for org/category listings

MAX_DESCRIPTION_CHARS: Final[int] = 500
