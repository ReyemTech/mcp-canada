"""Constants for the Canadian Nutrient File module."""

# Base URL for the Canadian Nutrient File API
BASE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file/"

# Rate limiting
RATE_GROUP = "nutrient-file"
RATE_LIMIT = 10.0  # requests per second — conservative

# Cache TTL in seconds
CACHE_TTL = 604800  # 7 days — static database, rarely updated
