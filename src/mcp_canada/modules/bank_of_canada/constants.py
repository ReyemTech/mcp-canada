"""Constants for the Bank of Canada Valet API module."""

# Base URL for the Valet API (trailing slash required for path building)
BASE_URL = "https://www.bankofcanada.ca/valet/"

# Rate limiting
RATE_GROUP = "bank-of-canada"
RATE_LIMIT = 10.0  # requests per second — conservative, no documented limit

# Cache TTLs in seconds
CACHE_TTL_OBS = 3600    # 1 hour for observation data
CACHE_TTL_META = 86400  # 24 hours for metadata (series lists, groups)

# Observation group names
FX_GROUP = "FX_RATES_DAILY"
BCPI_GROUP = "BCPI_MONTHLY"
CPI_GROUP = "CPI_MONTHLY"

# Interest rate series — maps rate_type to Valet series name
INTEREST_RATE_SERIES: dict[str, str] = {
    "policy": "V39079",              # Target for the overnight rate
    "corra": "AVG.INTWO",            # CORRA overnight average
    "bond_2yr": "BD.CDN.2YR.DQ.YLD",
    "bond_5yr": "BD.CDN.5YR.DQ.YLD",
    "bond_10yr": "BD.CDN.10YR.DQ.YLD",
    # Prime rate series TBD — V80691319 returns 404, discover via /lists/series
}

# BCPI (Bank of Canada Commodity Price Index) series — maps commodity_type to series name
BCPI_SERIES: dict[str, str] = {
    "total": "M.BCPI",
    "energy": "M.ENER",
    "metals": "M.MTLS",
    "agriculture": "M.AGRI",
    "forestry": "M.FOPR",
    "fish": "M.FISH",
}

# CPI (Consumer Price Index) series — maps indicator_type to series name
CPI_SERIES: dict[str, str] = {
    "total": "V41690973",
    "trim": "CPI_TRIM",
    "median": "CPI_MEDIAN",
    "common": "CPI_COMMON",
}
