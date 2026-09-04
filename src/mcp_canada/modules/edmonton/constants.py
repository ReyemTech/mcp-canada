"""Edmonton module constants.

Edmonton uses Socrata SODA (data.edmonton.ca), NOT CKAN — verified live 2026-09-04
via /api/catalog/v1 (resultSetSize=1421; first result "General Building Permits",
24uj-dj8v, category "Urban Planning & Economy"). The city's own Tyler Technologies
footer branding and dev.socrata.com developer link confirm Socrata, not a CKAN
action API.

Discovery-only module (no curated per-dataset tools) — mirrors the shape of
data.novascotia.ca's Plan 02 discovery slice. shared/socrata.py is reused verbatim,
same precedent as gnb.socrata.com (New Brunswick, Phase 21) — zero new client code
in shared/.
"""

from typing import Final

# ---------------------------------------------------------------------------
# Portal identifiers
# ---------------------------------------------------------------------------
BASE_DOMAIN: Final[str] = "data.edmonton.ca"
BASE_URL: Final[str] = f"https://{BASE_DOMAIN}"
CATALOG_URL: Final[str] = f"{BASE_URL}/api/catalog/v1"

# ---------------------------------------------------------------------------
# Rate limiting (keyless Socrata throttles ~1 req/sec per IP without a token)
# ---------------------------------------------------------------------------
RATE_GROUP: Final[str] = "edmonton_soda"
RATE_LIMIT: Final[float] = 2.0

# ---------------------------------------------------------------------------
# App token (read at module import; optional, raises throttle limits)
# ---------------------------------------------------------------------------
EDMONTON_APP_TOKEN_ENV: Final[str] = "EDMONTON_APP_TOKEN"

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_SEARCH: Final[int] = 3600    # 1h — catalog search / query results
CACHE_TTL_META: Final[int] = 86400     # 24h — dataset details, organizations, categories

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# Cache key prefix
# ---------------------------------------------------------------------------
CACHE_KEY_PREFIX: Final[str] = "edmonton:"
