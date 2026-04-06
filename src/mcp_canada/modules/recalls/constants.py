"""Constants for the Health Canada Recalls API module."""

# Base URL for the Recalls API (trailing slash required for path building)
BASE_URL = "https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/"

# Rate limiting
RATE_GROUP = "recalls"
RATE_LIMIT = 10.0  # requests per second — conservative, undocumented limit

# Cache TTLs in seconds
CACHE_TTL_SEARCH = 900    # 15 minutes for recent/search results
CACHE_TTL_DETAILS = 3600  # 1 hour for individual recall details

# Valid recall categories
CATEGORIES: dict[str, str] = {
    "FOOD": "Food",
    "VEHICLE": "Vehicle",
    "HEALTH": "Health Products",
    "CPS": "Consumer Products",
}
