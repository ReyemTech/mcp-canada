"""Constants for the Open Parliament API module."""

# Base URL for the Open Parliament API (trailing slash required for path building)
BASE_URL = "https://api.openparliament.ca/"

# Rate limiting
RATE_GROUP = "open-parliament"
RATE_LIMIT = 5.0  # requests per second — conservative per API guidelines

# Cache TTL in seconds
CACHE_TTL_DATA = 21600  # 6 hours for parliamentary data

# HTTP headers required by the Open Parliament API
API_HEADERS = {"Accept": "application/json"}
