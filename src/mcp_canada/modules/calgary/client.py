"""Calgary module client — async functions returning (data, was_cached) tuples.

Discovery-only slice, mirroring data.novascotia.ca's Plan 02 client functions.
shared/socrata.py provides search_catalog, get_dataset_metadata, query_dataset.
cached_fetch + get_limiter live here (NOT inside shared/socrata.py).
"""

from __future__ import annotations

import os
from typing import Any

from mcp_canada.shared import socrata
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    BASE_DOMAIN,
    CACHE_KEY_PREFIX,  # noqa: F401
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    CALGARY_APP_TOKEN_ENV,
    DEFAULT_PAGE_SIZE,
    RATE_GROUP,
    RATE_LIMIT,
)

# ---------------------------------------------------------------------------
# Module-level setup
# ---------------------------------------------------------------------------

# App token: read from environment at module import; passed to all socrata.* calls.
# Default is None (keyless). Set CALGARY_APP_TOKEN env var for higher throttle limits.
APP_TOKEN: str | None = os.environ.get(CALGARY_APP_TOKEN_ENV)

# Single shared rate limiter for all Calgary SODA calls.
_limiter = get_limiter(RATE_GROUP, RATE_LIMIT)


# ---------------------------------------------------------------------------
# Discovery client functions
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search the Calgary Socrata catalog by keyword with pagination.

    Returns shaped results: {"results": [...], "total": int}.
    Limit is clamped to [1, 1000] before forwarding to the SODA API.
    """
    clamped_limit = max(1, min(limit, 1000))
    cache_key = f"{CACHE_KEY_PREFIX}catalog:search:{query}:{clamped_limit}:{offset}"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q=query,
            limit=clamped_limit,
            offset=offset,
            only="datasets",
            app_token=APP_TOKEN,
        )
        results = [socrata.shape_catalog_result(r) for r in raw.get("results", [])]
        return {"results": results, "total": raw.get("resultSetSize", 0)}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_dataset_details(
    dataset_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch /api/views/{id}.json metadata for a dataset.

    Returns {"details": flat_metadata_dict}.
    """
    cache_key = f"{CACHE_KEY_PREFIX}metadata:{dataset_id}"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        flat = await socrata.get_dataset_metadata(
            BASE_DOMAIN,
            dataset_id,
            app_token=APP_TOKEN,
        )
        return {"details": flat}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_query_dataset(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Pass-through SoQL query for any Calgary dataset.

    When include_geometry=False (default) AND select is None, select is left as None —
    Socrata returns all fields including the_geom. Agents should pass explicit $select
    to exclude geometry. When include_geometry=False AND select is provided, select
    passes through unchanged.
    """
    cache_key = (
        f"{CACHE_KEY_PREFIX}query:{dataset_id}:{where}:{select}:"
        f"{order}:{limit}:{offset}:{q}:{group}:{include_geometry}"
    )

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        rows = await socrata.query_dataset(
            BASE_DOMAIN,
            dataset_id,
            where=where,
            select=select,
            order=order,
            limit=limit,
            offset=offset,
            q=q,
            group=group,
            app_token=APP_TOKEN,
        )
        return {"rows": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_organizations() -> tuple[dict[str, Any], bool]:
    """List unique organization attributions from the Calgary Socrata catalog.

    Fetches a wide catalog page and aggregates unique owner.display_name /
    attribution values with dataset counts. Never uses a dedicated organizations
    endpoint — derives from catalog results (same approach as Nova Scotia).
    """
    cache_key = f"{CACHE_KEY_PREFIX}organizations"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q="",
            limit=1000,
            offset=0,
            only="datasets",
            app_token=APP_TOKEN,
        )
        org_counts: dict[str, int] = {}
        for result in raw.get("results", []):
            owner = result.get("owner") or {}
            name = owner.get("display_name")
            if not name:
                for meta in (result.get("classification") or {}).get("domain_metadata") or []:
                    if isinstance(meta, dict) and str(meta.get("key", "")).endswith("Department"):
                        name = meta.get("value")
                        break
            if name:
                org_counts[name] = org_counts.get(name, 0) + 1

        organizations = sorted(
            [{"name": k, "dataset_count": v} for k, v in org_counts.items()],
            key=lambda x: (-int(x["dataset_count"]), str(x["name"])),
        )
        return {"organizations": organizations}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)


async def fetch_categories() -> tuple[dict[str, Any], bool]:
    """List domain categories from the Calgary Socrata catalog.

    Uses q= (or empty q) + client-side aggregation of classification.domain_category
    to enumerate categories, the same defensive approach Nova Scotia uses — the
    categories= catalog param is unreliable across Socrata portals (confirmed broken
    on data.novascotia.ca) and was never live-verified as working on Calgary either,
    so it is never sent here.
    """
    cache_key = f"{CACHE_KEY_PREFIX}categories"

    async def fetcher() -> dict[str, Any]:
        await _limiter.acquire()
        raw = await socrata.search_catalog(
            BASE_DOMAIN,
            q="",
            limit=1000,
            offset=0,
            only="datasets",
            app_token=APP_TOKEN,
        )
        cat_counts: dict[str, int] = {}
        for result in raw.get("results", []):
            classification = result.get("classification") or {}
            cat = classification.get("domain_category")
            if cat:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        categories = sorted(
            [{"name": k, "count": v} for k, v in cat_counts.items()],
            key=lambda x: (-int(x["count"]), str(x["name"])),
        )
        return {"categories": categories}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
