"""Constants for the Ontario Open Data module."""

# Base URL for the Ontario CKAN API (action API v3)
BASE_URL = "https://data.ontario.ca/api/3/"

# Rate limiting — conservative; no published limit for data.ontario.ca
RATE_GROUP = "ontario"
RATE_LIMIT = 10.0  # requests per second

# Cache TTLs in seconds
CACHE_TTL_SEARCH = 3600    # 1 hour for search results and dataset details
CACHE_TTL_META = 86400     # 24 hours for org lists (rarely change)
CACHE_TTL_DATA = 86400     # 24 hours for parsed XLSX data

# Token-saving response shaping limits
MAX_DESCRIPTION_CHARS = 500
MAX_RESOURCES = 10

# Curated population projections dataset
POPULATION_PROJECTIONS_DATASET_ID = "f52a6457-fb37-4267-acde-11a1e57c4dc8"
POPULATION_PROJECTIONS_RESOURCE_URL = (
    "https://data.ontario.ca/dataset/f52a6457-fb37-4267-acde-11a1e57c4dc8"
    "/resource/31376797-1e4c-4426-ba75-0d93f4bb9f45"
    "/download/ontario_mof_population_projections_for_2024-2051.xlsx"
)
