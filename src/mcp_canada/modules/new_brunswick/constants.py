"""New Brunswick module constants.

TRACER SUBSET (Task 1) — Task 4 expands this file with the full contract surface
(federal CKAN, remaining GeoNB services, 511, cache TTLs, ALL_NB_TOOL_NAMES).

GeoNB is ArcGIS **Server** (62 MapServer services), NOT ArcGIS Hub — the Hub at
geonb-snb.opendata.arcgis.com returns HTTP 401. Layer ids on GeoNB services are
non-guessable and are resolved live from {service}/MapServer?f=json — Crown Land is
the worked case here: layer 3, NOT layer 0 (layer 0 does not exist on that service,
per 21-RESEARCH.md Pitfall 1).
"""

from typing import Final

# ---------------------------------------------------------------------------
# GeoNB — ArcGIS Server (bare MapServer REST, no Hub in front)
# ---------------------------------------------------------------------------

GEONB_BASE_URL: Final[str] = "https://geonb.snb.ca/arcgis/rest/services"

CROWN_LAND_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_DNR_Crown_Land/MapServer"
CROWN_LAND_LAYER: Final[int] = 3
CROWN_LAND_FIELDS: Final[str] = "OBJECTID,HOLDER,Shape_Length,Shape_Area"

RATE_GROUP_GEONB: Final[str] = "new_brunswick_geonb"
RATE_LIMIT_GEONB: Final[float] = 5.0

CACHE_KEY_PREFIX: Final[str] = "new_brunswick:"
CACHE_TTL_META: Final[int] = 86400

MAX_RECORDS: Final[int] = 5000
