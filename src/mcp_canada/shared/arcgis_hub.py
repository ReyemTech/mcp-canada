"""Reusable ArcGIS Hub Search API + FeatureServer client.

Used by any Canadian municipal open data module that publishes through ArcGIS Hub
(e.g., york_region, future BC modules). See 14-RESEARCH.md for API reference and
verified endpoints.

Public functions:
    search_hub_datasets(portal_base_url, query, limit, offset) -> dict
    query_feature_service(service_url, layer_id, where, out_fields, include_geometry, max_records) -> (list[dict], bool)
    get_layer_metadata(service_url, layer_id) -> dict
    get_count(service_url, layer_id, where) -> int
    shape_hub_dataset(feature) -> dict
"""

from __future__ import annotations

from typing import Any

import httpx

from mcp_canada.shared.parsers import _parse_geojson

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RECORDS = 5000           # cap per tool call — prevents runaway pagination
DEFAULT_PAGE_SIZE = 1000     # safe default; actual maxRecordCount varies 1000-2000
HUB_SEARCH_PATH = "/api/search/v1/collections/all/items"
DEFAULT_TIMEOUT = 30.0
MAX_DESCRIPTION_CHARS = 500


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


async def search_hub_datasets(
    portal_base_url: str | None,
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Search an ArcGIS Hub portal for datasets matching the given query.

    Args:
        portal_base_url: Base URL of the ArcGIS Hub portal (e.g.,
            "https://insights-york.opendata.arcgis.com"). Pass None for
            municipalities that have no public portal — raises ValueError.
        query: Free-text search query. Empty string returns all items.
        limit: Maximum number of results to return (default: 10).
        offset: Pagination offset (default: 0). Omitted from request if 0.
        httpx_client: Optional pre-built AsyncClient for dependency injection
            (mainly for tests). Defaults to creating a new client per call.

    Returns:
        Raw JSON dict from the Hub Search API, containing:
            {type, numberMatched, numberReturned, features: [...], links: [...]}

    Raises:
        ValueError: If portal_base_url is None (municipality has no public portal).
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    if portal_base_url is None:
        raise ValueError("portal has no public ArcGIS Hub open data portal")

    url = portal_base_url.rstrip("/") + HUB_SEARCH_PATH
    params: dict[str, Any] = {"limit": limit}
    if query and query.strip():
        params["q"] = query   # empty q is rejected with HTTP 400 by every Hub portal, so omit it
    if offset > 0:
        params["startindex"] = offset   # OGC API Records pagination (NOT offset); startindex=0 is invalid so omit at 0

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def query_feature_service(
    service_url: str,
    layer_id: int,
    where: str | None = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    max_records: int = MAX_RECORDS,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Query an ArcGIS FeatureServer layer and return all matching features.

    Automatically paginates using resultOffset/resultRecordCount until all
    records are retrieved or the max_records cap is reached.

    Args:
        service_url: FeatureServer base URL (without layer id).
        layer_id: Layer/table index (0-based).
        where: SQL-92 WHERE clause (default: "1=1" for all records).
        out_fields: Comma-separated field names or "*" for all.
        include_geometry: If True, include GeoJSON geometry in each dict.
        max_records: Maximum total records to return (default: 5000).
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        (features, truncated) where features is a list of property dicts and
        truncated is True if the max_records cap was hit with more data available.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    query_url = f"{service_url.rstrip('/')}/{layer_id}/query"
    all_features: list[dict[str, Any]] = []
    truncated = False
    offset = 0

    _client_to_use = httpx_client

    async def _fetch_page(client: httpx.AsyncClient) -> bytes:
        page_size = min(DEFAULT_PAGE_SIZE, max_records - offset)
        params: dict[str, Any] = {
            # httpx drops None-valued params; ArcGIS /query rejects a request
            # with no `where`, which surfaces as a bogus UPSTREAM_ERROR.
            "where": where or "1=1",
            "outFields": out_fields,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }
        if not include_geometry:
            params["returnGeometry"] = "false"
        response = await client.get(query_url, params=params)
        response.raise_for_status()
        return response.content

    async def _run_pagination(client: httpx.AsyncClient) -> None:
        nonlocal offset, truncated

        while offset < max_records:
            raw_content = await _fetch_page(client)
            raw_json = _parse_raw_json(raw_content)

            batch = _parse_geojson(raw_content, include_geometry=include_geometry)
            all_features.extend(batch)

            exceeded = raw_json.get("exceededTransferLimit", False)
            if not exceeded:
                break

            offset += len(batch)
            if offset >= max_records:
                truncated = True
                break

    if _client_to_use is not None:
        await _run_pagination(_client_to_use)
    else:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            await _run_pagination(client)

    return all_features, truncated


async def get_layer_metadata(
    service_url: str,
    layer_id: int,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Fetch metadata for a specific FeatureServer layer.

    Args:
        service_url: FeatureServer base URL (without layer id).
        layer_id: Layer/table index (0-based).
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        Dict with keys: max_record_count (int), fields (list of {name, type}),
        geometry_type (str | None), name (str).

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    url = f"{service_url.rstrip('/')}/{layer_id}"
    params = {"f": "json"}

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    else:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

    return {
        "max_record_count": int(data.get("maxRecordCount", DEFAULT_PAGE_SIZE)),
        "fields": [
            {"name": f.get("name"), "type": f.get("type")}
            for f in data.get("fields", [])
        ],
        "geometry_type": data.get("geometryType"),
        "name": data.get("name", ""),
    }


async def get_count(
    service_url: str,
    layer_id: int,
    where: str | None = "1=1",
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> int:
    """Get the total record count for a FeatureServer layer matching a WHERE clause.

    Args:
        service_url: FeatureServer base URL (without layer id).
        layer_id: Layer/table index (0-based).
        where: SQL-92 WHERE clause (default: "1=1" for all records).
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        Integer count of matching records.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
    url = f"{service_url.rstrip('/')}/{layer_id}/query"
    params: dict[str, Any] = {
        # See query_feature_service: a None `where` would be dropped by httpx.
        "where": where or "1=1",
        "returnCountOnly": "true",
        "f": "json",
    }

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    else:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

    return int(data.get("count", 0))


def shape_hub_dataset(feature: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single Hub Search features[i] entry to a flat dict.

    Args:
        feature: A single item from the Hub Search API features array.

    Returns:
        Flat dict with keys: id, title, type, description, url, owner,
        tags, categories, created, modified.
    """
    props = feature.get("properties") or {}
    description = props.get("description")
    if description and len(description) > MAX_DESCRIPTION_CHARS:
        description = description[:MAX_DESCRIPTION_CHARS] + "..."

    return {
        "id": feature.get("id"),
        "title": props.get("title", ""),
        "type": props.get("type"),
        "description": description,
        "url": props.get("url"),
        "owner": props.get("owner"),
        "tags": props.get("tags") or [],
        "categories": props.get("categories") or [],
        "created": props.get("created"),
        "modified": props.get("modified"),
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _parse_raw_json(content: bytes) -> dict[str, Any]:
    """Parse raw bytes as JSON and return the dict (for checking vendor extensions)."""
    import json
    return json.loads(content)
