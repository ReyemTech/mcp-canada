"""Constants for the CKAN Open Data module."""

# Base URL for the CKAN API (action API v3)
BASE_URL = "https://open.canada.ca/data/en/api/3/"

# Rate limiting — conservative for a public portal
RATE_GROUP = "ckan"
RATE_LIMIT = 10.0  # requests per second

# Cache TTLs in seconds
CACHE_TTL_SEARCH = 3600   # 1 hour for search results and dataset details
CACHE_TTL_META = 86400    # 24 hours for org/group lists (rarely change)

# Token-saving response shaping limits
MAX_DESCRIPTION_CHARS = 500
MAX_RESOURCES = 10
