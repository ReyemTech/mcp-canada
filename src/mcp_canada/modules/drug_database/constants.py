"""Constants for the Health Canada Drug Product Database module."""

# Base URL for the Drug Product Database API (trailing slash required for path building)
BASE_URL = "https://health-products.canada.ca/api/drug/"

# Rate limiting — conservative for government server
RATE_GROUP = "drug-database"
RATE_LIMIT = 10.0  # requests per second

# Cache TTL in seconds — drug data changes slowly (12 hours)
CACHE_TTL = 43200  # 12 hours

# HTTP timeout — Drug API can be very slow (45s+ for broad searches)
HTTP_TIMEOUT = 60.0
