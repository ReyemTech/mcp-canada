"""New Brunswick module client — async functions returning (data, was_cached) tuples.

TRACER SUBSET (Task 1) — one fully-implemented function proving the shared
arcgis_hub.query_feature_service contract works unchanged against a bare
ArcGIS Server MapServer (D-05). Task 4 adds the remaining limiters, private
helpers and every downstream client function as a locked-signature stub.
"""

from __future__ import annotations

from typing import Any

from mcp_canada.shared import arcgis_hub
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_META,
    CROWN_LAND_FIELDS,
    CROWN_LAND_LAYER,
    CROWN_LAND_SERVICE,
    MAX_RECORDS,
    RATE_GROUP_GEONB,
    RATE_LIMIT_GEONB,
)

__all__ = ["fetch_crown_land"]

# ---------------------------------------------------------------------------
# Module-level limiters
# ---------------------------------------------------------------------------

_geonb_limiter = get_limiter(RATE_GROUP_GEONB, RATE_LIMIT_GEONB)


# ---------------------------------------------------------------------------
# Crown Land — Task 1 tracer
# ---------------------------------------------------------------------------


async def fetch_crown_land(
    holder: int | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch New Brunswick Crown Land parcels from GeoNB_DNR_Crown_Land layer 3.

    Builds the WHERE clause server-side from the typed `holder` argument — never
    from a caller-supplied clause string. `holder` is a raw integer holder code
    with no server-exposed name domain (RESEARCH Pitfall 4).

    Returns ({"features": [...], "count": N, "truncated": bool}, was_cached).
    """
    where = f"HOLDER={holder}" if holder is not None else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}crown_land:{holder}:{limit}"

    async def _fetch() -> dict[str, Any]:
        await _geonb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            CROWN_LAND_SERVICE,
            layer_id=CROWN_LAND_LAYER,
            where=where,
            out_fields=CROWN_LAND_FIELDS,
            include_geometry=False,
            max_records=limit,
        )
        return {
            "features": features,
            "count": len(features),
            "truncated": truncated,
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
