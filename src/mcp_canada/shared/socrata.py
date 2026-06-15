"""Reusable Socrata SODA API async client.

Used by any Canadian provincial/municipal module that publishes via Socrata.
data.novascotia.ca is the first consumer.

Modeled structurally on shared/arcgis_hub.py and shared/ogc.py:
  - httpx_client injection kwarg on all public functions (enables tests without monkeypatching)
  - Returns parsed dicts/lists, NOT httpx.Response
  - No cached_fetch or get_limiter inside this file (caching is a module concern)
  - DEFAULT_TIMEOUT = 30.0 (same as arcgis_hub.py)
  - MAX_DESCRIPTION_CHARS = 500 (same as arcgis_hub.py)

Public functions:
    search_catalog(domain, q, limit, offset, only, *, app_token, httpx_client) -> dict
    get_dataset_metadata(domain, dataset_id, *, app_token, httpx_client) -> dict
    query_dataset(domain, dataset_id, where, select, order, limit, offset, q, group, *, app_token, httpx_client) -> list[dict]
    shape_catalog_result(result) -> dict

Pitfall 8 (from 20-RESEARCH.md): omit 'offset' and '$offset' from request params
when the value is 0 — Socrata treats absence the same as 0 but requests are cleaner.

The optional X-App-Token header raises Socrata's throttle limits (future enhancement).
Keyless default; add it when NS_APP_TOKEN env var is set (in the per-module client.py).
"""

from __future__ import annotations

from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT: float = 30.0
MAX_DESCRIPTION_CHARS: int = 500

CATALOG_PATH: str = "/api/catalog/v1"
RESOURCE_PATH: str = "/resource/{dataset_id}.json"
VIEWS_PATH: str = "/api/views/{dataset_id}.json"


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


async def search_catalog(
    domain: str,
    q: str = "",
    limit: int = 10,
    offset: int = 0,
    only: str = "datasets",
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Search a Socrata catalog for datasets matching a query.

    Args:
        domain: Socrata domain (e.g., "data.novascotia.ca").
        q: Free-text search (default: "" = all datasets).
        limit: Page size (default: 10).
        offset: Pagination offset (default: 0). Omitted from request when 0 (Pitfall 8).
        only: Filter to "datasets", "maps", "charts", "stories", "files" (default: "datasets").
        app_token: Optional Socrata app token for higher rate limits.
        httpx_client: Optional pre-built AsyncClient for dependency injection (tests).

    Returns:
        Raw catalog JSON: {results, resultSetSize, timings, warnings}

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    url = f"https://{domain}{CATALOG_PATH}"
    params: dict[str, Any] = {"domains": domain, "q": q, "limit": limit, "only": only}
    if offset > 0:
        params["offset"] = offset

    headers: dict[str, str] = {}
    if app_token:
        headers["X-App-Token"] = app_token

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_dataset_metadata(
    domain: str,
    dataset_id: str,
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Fetch schema and metadata for a specific dataset from /api/views/{id}.json.

    Args:
        domain: Socrata domain (e.g., "data.novascotia.ca").
        dataset_id: 4x4 dataset identifier (e.g., "h57h-p9mm").
        app_token: Optional Socrata app token.
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        Flat dict with: id, name, category, description, columns (list of
        {name, field_name, data_type, description}), attribution, license_name,
        publication_date, tags.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    url = f"https://{domain}{VIEWS_PATH.format(dataset_id=dataset_id)}"

    headers: dict[str, str] = {}
    if app_token:
        headers["X-App-Token"] = app_token

    if httpx_client is not None:
        response = await httpx_client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    else:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

    return _flatten_metadata(data)


async def query_dataset(
    domain: str,
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 1000,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Query a Socrata dataset via SoQL against /resource/{id}.json.

    Args:
        domain: Socrata domain.
        dataset_id: 4x4 dataset identifier (e.g., "h57h-p9mm").
        where: SoQL WHERE clause (e.g., "county='Halifax'").
        select: Comma-separated field names or "field, count(*) AS n".
        order: Sort clause (e.g., "year DESC").
        limit: Max rows (default 1000, Socrata max 50000).
        offset: Pagination offset (default 0). Omitted when 0 (Pitfall 8).
        q: Full-text search within the dataset.
        group: GROUP BY clause for aggregations.
        app_token: Optional Socrata app token.
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        List of flat row dicts from the SODA endpoint.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    url = f"https://{domain}{RESOURCE_PATH.format(dataset_id=dataset_id)}"
    params: dict[str, Any] = {"$limit": limit}

    # Add optional SoQL params only when provided (never add None values)
    if where is not None:
        params["$where"] = where
    if select is not None:
        params["$select"] = select
    if order is not None:
        params["$order"] = order
    if q is not None:
        params["$q"] = q
    if group is not None:
        params["$group"] = group
    # Pitfall 8: omit $offset when 0 (Socrata default = 0; cleaner requests)
    if offset > 0:
        params["$offset"] = offset

    headers: dict[str, str] = {}
    if app_token:
        headers["X-App-Token"] = app_token

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def shape_catalog_result(result: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single catalog results[i] entry to a flat dict.

    Extracts from result["resource"], result["classification"],
    result["metadata"], result["owner"], result["permalink"].

    Args:
        result: A single item from the catalog /api/catalog/v1 results array.

    Returns:
        Flat dict: id, name, description, category, tags, department,
        permalink, updated_at, download_count, type, column_names.
    """
    resource = result.get("resource") or {}
    classification = result.get("classification") or {}
    domain_metadata: list[dict[str, Any]] = classification.get("domain_metadata") or []

    description = resource.get("description") or ""
    if description and len(description) > MAX_DESCRIPTION_CHARS:
        description = description[:MAX_DESCRIPTION_CHARS] + "..."

    # Department: find first domain_metadata entry whose key ends with "Department"
    department: str | None = None
    for entry in domain_metadata:
        if isinstance(entry, dict) and str(entry.get("key", "")).endswith("Department"):
            department = entry.get("value")
            break

    # Column names: prefer columns_field_name, fall back to columns_name
    column_names: list[str] = (
        resource.get("columns_field_name")
        or resource.get("columns_name")
        or []
    )

    return {
        "id": resource.get("id"),
        "name": resource.get("name", ""),
        "description": description,
        "category": classification.get("domain_category"),
        "tags": classification.get("domain_tags") or [],
        "department": department,
        "permalink": result.get("permalink"),
        "updated_at": resource.get("updatedAt"),
        "download_count": resource.get("download_count"),
        "type": resource.get("type"),
        "column_names": column_names,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _flatten_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten /api/views/{id}.json response to a standard flat dict.

    Args:
        data: Raw JSON dict from the Socrata /api/views/{id}.json endpoint.

    Returns:
        Flat dict with id, name, category, description, columns, attribution,
        license_name, publication_date, tags.
    """
    description = data.get("description") or ""
    if description and len(description) > MAX_DESCRIPTION_CHARS:
        description = description[:MAX_DESCRIPTION_CHARS] + "..."

    # Columns: flatten each column to {name, field_name, data_type, description}
    raw_columns = data.get("columns") or []
    columns = [
        {
            "name": col.get("name", ""),
            "field_name": col.get("fieldName", ""),
            "data_type": col.get("dataTypeName", ""),
            "description": col.get("description", ""),
        }
        for col in raw_columns
    ]

    # License: nested dict license.name → flat license_name
    license_info = data.get("license") or {}
    license_name: str | None = license_info.get("name") if isinstance(license_info, dict) else None

    return {
        "id": data.get("id"),
        "name": data.get("name", ""),
        "category": data.get("category"),
        "description": description,
        "columns": columns,
        "attribution": data.get("attribution"),
        "license_name": license_name,
        "publication_date": data.get("publicationDate"),
        "tags": data.get("tags") or [],
    }
