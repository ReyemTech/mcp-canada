"""British Columbia open data client stubs.

Plans 02 and 03 fill in the function bodies.
All public functions return (data, was_cached) tuples and delegate to
shared/cache.py + shared/rate_limiter.py + shared/ogc.py.

CKAN response envelope: {"success": true, "result": ...}
For package_search: result = {"count": N, "results": [...]}
For package_show:   result = {<dataset dict>}
"""

from __future__ import annotations

from typing import Any

import httpx  # noqa: F401 — used by Plan 02/03 implementations

from mcp_canada.shared.cache import cached_fetch  # noqa: F401 — used by Plan 02/03
from mcp_canada.shared.http import api_get  # noqa: F401 — used by Plan 02
from mcp_canada.shared.ogc import WfsError, wfs_page_all  # noqa: F401 — used by Plan 03
from mcp_canada.shared.parsers import fetch_and_parse  # noqa: F401 — used by Plan 02
from mcp_canada.shared.rate_limiter import get_limiter  # noqa: F401 — used by Plan 02/03

from .constants import (
    BASE_URL,  # noqa: F401 — used by Plan 02
    CACHE_TTL_ACTIVE,  # noqa: F401 — used by Plan 03
    CACHE_TTL_META,  # noqa: F401 — used by Plan 02
    CACHE_TTL_SEARCH,  # noqa: F401 — used by Plan 02
    CACHE_TTL_STATIC,
    MAX_RECORDS,
    RATE_GROUP_CKAN,  # noqa: F401 — used by Plan 02
    RATE_GROUP_WFS,  # noqa: F401 — used by Plan 03
    RATE_LIMIT_CKAN,  # noqa: F401 — used by Plan 02
    RATE_LIMIT_WFS,  # noqa: F401 — used by Plan 03
    WFS_BASE_URL,  # noqa: F401 — used by Plan 03
    WFS_PAGE_SIZE,  # noqa: F401 — used by Plan 03
)

__all__ = [
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_organizations",
    "fetch_tags",
    "_wfs_fetch",
]


# ---------------------------------------------------------------------------
# CKAN Discovery — implemented in Plan 02
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    q: str = "",
    rows: int = 20,
    start: int = 0,
    fq: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Search BC Data Catalogue via CKAN package_search.

    Plan 02 implements this function body.
    """
    raise NotImplementedError("Plan 02 will implement fetch_search_datasets")


async def fetch_dataset_details(
    package_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch full dataset metadata via CKAN package_show, including resources.

    Plan 02 implements this function body. Must derive queryable_via_wfs flag
    from bcdc_type + resource_storage_location + object_name fields.
    """
    raise NotImplementedError("Plan 02 will implement fetch_dataset_details")


async def fetch_organizations() -> tuple[list[dict[str, Any]], bool]:
    """List all BC Data Catalogue organizations (ministries, agencies).

    Plan 02 implements this function body.
    """
    raise NotImplementedError("Plan 02 will implement fetch_organizations")


async def fetch_tags() -> tuple[list[str], bool]:
    """List all BC Data Catalogue tags for subject-area discovery.

    Plan 02 implements this function body.
    """
    raise NotImplementedError("Plan 02 will implement fetch_tags")


# ---------------------------------------------------------------------------
# WFS Feature Fetch — implemented in Plan 03
# ---------------------------------------------------------------------------


async def _wfs_fetch(
    layer: str,
    cql: str | None = None,
    max_records: int = MAX_RECORDS,
    include_geometry: bool = False,
    ttl: int = CACHE_TTL_STATIC,
) -> tuple[dict[str, Any], bool]:
    """Fetch features from a BCGW WFS layer with caching and rate limiting.

    Plan 03 implements this function body. Returns
    {"features": [...], "count": N, "truncated": bool} tuple.
    """
    raise NotImplementedError("Plan 03 will implement _wfs_fetch")
