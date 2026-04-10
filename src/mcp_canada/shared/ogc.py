"""Reusable WFS 2.0 (OGC Web Feature Service) async client.

Used by any Canadian government module that publishes geospatial data through
an OGC-compliant WFS endpoint. BC Geographic Warehouse (openmaps.gov.bc.ca) is
the first consumer; Quebec and other provinces may follow.

Unlike ArcGIS FeatureServer (shared/arcgis_hub.py), WFS 2.0 uses standard OGC
parameters, CQL filters, and ows:ExceptionReport XML error bodies.

Public functions:
    wfs_get_features(base_url, type_name, ...) -> (list[dict], has_more)
    wfs_page_all(base_url, type_name, ...) -> (list[dict], truncated)
    wfs_count(base_url, type_name, ...) -> int
    WfsError — structured exception for ows:ExceptionReport errors
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

import httpx

# Imported at module level; defer inside function only if circular import arises.
from mcp_canada.shared.parsers import _parse_geojson

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 30.0
DEFAULT_PAGE_SIZE = 1000
MAX_RECORDS = 5000


# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------


class WfsError(Exception):
    """Raised when the WFS server returns an ows:ExceptionReport (typically HTTP 400).

    Attributes:
        code: The exceptionCode attribute from ows:Exception (e.g. "InvalidParameterValue").
        message: The text from ows:ExceptionText (e.g. "Feature type X unknown").
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"WfsError({code}): {message}")


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


async def wfs_get_features(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    bbox: str | None = None,
    count: int = DEFAULT_PAGE_SIZE,
    start_index: int = 0,
    srs: str = "EPSG:4326",
    property_names: list[str] | None = None,
    include_geometry: bool = False,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a single page of WFS features as a list of property dicts.

    Args:
        base_url: WFS endpoint base URL (e.g. "https://openmaps.gov.bc.ca/geo/ows").
        type_name: WFS layer name (BCGW object_name, e.g. "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP").
            The Python param is type_name but it serializes as typeNames (plural) per WFS 2.0 spec.
        cql_filter: Optional CQL_FILTER string (e.g. "FIRE_YEAR=2023").
        bbox: Optional BBOX string "minLon,minLat,maxLon,maxLat".
        count: Page size — number of features to request (default: 1000).
        start_index: Pagination offset (default: 0).
        srs: Coordinate reference system (default: "EPSG:4326").
        property_names: Optional list of property names to return. None returns all.
        include_geometry: If True, each dict includes a 'geometry' key.
        httpx_client: Optional pre-built AsyncClient for dependency injection (mainly tests).

    Returns:
        (features, has_more) where features is a list of property dicts and
        has_more is True when numberReturned >= count (i.e. another page likely exists).

    Raises:
        WfsError: When the server returns HTTP 400 with an ows:ExceptionReport XML body.
        httpx.HTTPStatusError: On other 4xx/5xx responses.
    """
    # WFS 2.0 spec requires typeNames (PLURAL). The Python kwarg is type_name
    # (singular) for a clean API, but it always serializes as typeNames in the URL.
    params: dict[str, Any] = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": type_name,  # typeNames (plural) — WFS 2.0 spec
        "outputFormat": "application/json",
        "count": count,
        "startIndex": start_index,
        "sortBy": "OBJECTID",    # required for stable pagination
        "srsName": srs,
    }

    if cql_filter is not None:
        params["CQL_FILTER"] = cql_filter
    if bbox is not None:
        params["BBOX"] = bbox
    if property_names is not None:
        params["propertyName"] = ",".join(property_names)

    response = await _do_get(base_url, params, httpx_client)

    # Error handling order (DO NOT change):
    # a. 400 + XML content-type → parse ExceptionReport and raise WfsError
    # b. raise_for_status() for other 4xx/5xx
    # c. parse GeoJSON body
    # Never call response.json() on the 400 path.

    if response.status_code == 400 and "xml" in response.headers.get("content-type", "").lower():
        raise _parse_wfs_exception(response.text)

    response.raise_for_status()

    # Use response.content (bytes) so _parse_geojson handles JSON parsing internally.
    # We also need numberReturned for the has_more flag — parse once via json module.
    import json as _json  # noqa: PLC0415 — avoids shadowing top-level json if user imports this

    body = _json.loads(response.content)
    features = _parse_geojson(response.content, include_geometry=include_geometry)
    has_more = body.get("numberReturned", 0) >= count
    return features, has_more


async def wfs_page_all(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    bbox: str | None = None,
    max_records: int = MAX_RECORDS,
    page_size: int = DEFAULT_PAGE_SIZE,
    srs: str = "EPSG:4326",
    include_geometry: bool = False,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch all matching WFS features with automatic pagination.

    Loops wfs_get_features until all pages are retrieved or max_records cap hit.

    Args:
        base_url: WFS endpoint base URL.
        type_name: WFS layer name (BCGW object_name).
        cql_filter: Optional CQL_FILTER string.
        bbox: Optional BBOX string.
        max_records: Maximum total records to return (default: 5000). Acts as a cap.
        page_size: Records per page (default: 1000).
        srs: Coordinate reference system (default: "EPSG:4326").
        include_geometry: If True, include geometry in each feature dict.
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        (features, truncated) where features is the accumulated list and
        truncated is True ONLY when the max_records cap was hit with more data available.
    """
    accumulated: list[dict[str, Any]] = []
    start_index = 0

    while len(accumulated) < max_records:
        remaining = max_records - len(accumulated)
        this_page = min(page_size, remaining)

        batch, has_more = await wfs_get_features(
            base_url,
            type_name,
            cql_filter=cql_filter,
            bbox=bbox,
            count=this_page,
            start_index=start_index,
            srs=srs,
            include_geometry=include_geometry,
            httpx_client=httpx_client,
        )

        accumulated.extend(batch)
        start_index += len(batch)

        if not has_more:
            # Last page — no more data
            return accumulated[:max_records], False

        if len(accumulated) >= max_records:
            # Cap hit while more data exists
            return accumulated[:max_records], True

    # Reached max_records exactly — check if has_more for truncated flag
    return accumulated[:max_records], True


async def wfs_count(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> int:
    """Get total feature count using WFS resultType=hits (no features returned).

    Uses the WFS 2.0 hits mechanism: empty FeatureCollection with totalFeatures populated.

    Args:
        base_url: WFS endpoint base URL.
        type_name: WFS layer name (BCGW object_name).
        cql_filter: Optional CQL_FILTER string.
        httpx_client: Optional pre-built AsyncClient for dependency injection.

    Returns:
        Integer count of matching features.

    Raises:
        WfsError: On ows:ExceptionReport XML error responses.
        httpx.HTTPStatusError: On other 4xx/5xx responses.
    """
    params: dict[str, Any] = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": type_name,  # typeNames (plural) — WFS 2.0 spec
        "resultType": "hits",
        "outputFormat": "application/json",
    }

    if cql_filter is not None:
        params["CQL_FILTER"] = cql_filter

    response = await _do_get(base_url, params, httpx_client)

    if response.status_code == 400 and "xml" in response.headers.get("content-type", "").lower():
        raise _parse_wfs_exception(response.text)

    response.raise_for_status()

    import json as _json  # noqa: PLC0415

    body = _json.loads(response.content)
    return int(body.get("totalFeatures", 0))


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _do_get(
    url: str,
    params: dict[str, Any],
    httpx_client: httpx.AsyncClient | None,
) -> httpx.Response:
    """Execute a GET request using the provided client or a new one."""
    if httpx_client is not None:
        return await httpx_client.get(url, params=params)
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        return await client.get(url, params=params)


def _parse_wfs_exception(xml_text: str) -> WfsError:
    """Parse an ows:ExceptionReport XML string into a WfsError.

    Robust to any ows namespace version — iterates elements and checks
    tag local name (after stripping namespace) rather than relying on
    exact namespace prefix.

    Args:
        xml_text: Raw XML string from the 400 response body.

    Returns:
        WfsError with code and message populated from the first ows:Exception.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return WfsError("UnknownError", xml_text[:200])

    code = "UnknownError"
    message = ""

    for elem in root.iter():
        # Strip namespace: "{http://www.opengis.net/ows/1.1}Exception" → "Exception"
        local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if local == "Exception":
            code = elem.get("exceptionCode", "UnknownError")

        if local == "ExceptionText":
            message = (elem.text or "").strip()
            break  # First ExceptionText wins

    return WfsError(code, message)
