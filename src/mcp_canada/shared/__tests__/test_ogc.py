"""Unit tests for shared/ogc.py — WFS 2.0 async client (GetFeature, pagination, XML error parsing)."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from mcp_canada.shared.ogc import (
    WfsError,
    wfs_count,
    wfs_get_features,
    wfs_page_all,
)

# ---------------------------------------------------------------------------
# Fixtures — sample data
# ---------------------------------------------------------------------------

WFS_BASE_URL = "https://openmaps.gov.bc.ca/geo/ows"
ACTIVE_FIRES_LAYER = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP"


def _make_geojson_response(n_features: int, number_returned: int | None = None) -> dict[str, Any]:
    """Build a minimal WFS GeoJSON FeatureCollection response."""
    if number_returned is None:
        number_returned = n_features
    features = [
        {
            "type": "Feature",
            "id": f"PROT_CURRENT_FIRE_PNTS_SP.{i}",
            "geometry": {"type": "Point", "coordinates": [-123.0 + i * 0.1, 51.0 + i * 0.1]},
            "properties": {
                "FIRE_NUMBER": f"C{i:05d}",
                "FIRE_YEAR": 2026,
                "FIRE_STATUS": "Active",
                "FIRE_CAUSE": "Lightning",
                "FIRE_CENTRE": "Kamloops Fire Centre",
                "CURRENT_SIZE": 12.5 + i,
                "LATITUDE": 51.0 + i * 0.1,
                "LONGITUDE": -123.0 + i * 0.1,
                "INCIDENT_NAME": f"Test Fire {i}",
            },
        }
        for i in range(n_features)
    ]
    return {
        "type": "FeatureCollection",
        "totalFeatures": 1500,
        "numberMatched": 1500,
        "numberReturned": number_returned,
        "features": features,
    }


WFS_EXCEPTION_REPORT_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport version="2.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
  <ows:Exception exceptionCode="InvalidParameterValue" locator="typeNames">
    <ows:ExceptionText>Feature type NO_SUCH_LAYER unknown</ows:ExceptionText>
  </ows:Exception>
</ows:ExceptionReport>"""


def _make_mock_client(
    response_body: dict[str, Any] | None = None,
    status_code: int = 200,
    content_type: str = "application/json",
    text: str | None = None,
) -> AsyncMock:
    """Build a mock httpx.AsyncClient that returns the given response."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = status_code
    mock_response.headers = {"content-type": content_type}
    if text is not None:
        mock_response.text = text
    if response_body is not None:
        body_bytes = json.dumps(response_body).encode("utf-8")
        mock_response.content = body_bytes
        mock_response.json.return_value = response_body
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(return_value=mock_response)
    return mock_client


# ---------------------------------------------------------------------------
# TestWfs — wfs_get_features
# ---------------------------------------------------------------------------


class TestWfs:
    """Tests for wfs_get_features, wfs_page_all, wfs_count, and WfsError."""

    @pytest.mark.asyncio
    async def test_wfs_get_features_returns_features_and_has_more(self):
        """Returns (features, True) when numberReturned equals count (more data available)."""
        body = _make_geojson_response(n_features=3, number_returned=1000)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}, {"a": 2}, {"a": 3}]):
            features, has_more = await wfs_get_features(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                count=1000,
                httpx_client=mock_client,
            )

        assert len(features) == 3
        assert has_more is True

    @pytest.mark.asyncio
    async def test_wfs_get_features_last_page_has_more_false(self):
        """Returns (features, False) when numberReturned < count (last page)."""
        body = _make_geojson_response(n_features=2, number_returned=500)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}, {"a": 2}]):
            features, has_more = await wfs_get_features(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                count=1000,
                httpx_client=mock_client,
            )

        assert has_more is False

    @pytest.mark.asyncio
    async def test_wfs_get_features_uses_typeNames_plural(self):
        """Outgoing request uses typeNames (plural) per WFS 2.0 spec — NOT typeName."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            await wfs_get_features(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)

        call_kwargs = mock_client.get.call_args
        params = call_kwargs[1].get("params") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1]["params"]
        assert "typeNames" in params, f"typeNames not in params: {params}"
        assert "typeName" not in params or params.get("typeName") is None, (
            "typeName (singular) must not be sent — WFS 2.0 uses typeNames"
        )

    @pytest.mark.asyncio
    async def test_wfs_get_features_uses_srsName_epsg4326_by_default(self):
        """srsName=EPSG:4326 is always included in the request params by default."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            await wfs_get_features(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)

        call_kwargs = mock_client.get.call_args
        params = call_kwargs[1].get("params") or call_kwargs[1]["params"]
        assert params.get("srsName") == "EPSG:4326"

    @pytest.mark.asyncio
    async def test_wfs_get_features_sets_sortBy_OBJECTID(self):
        """sortBy=OBJECTID is always included for stable pagination."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            await wfs_get_features(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)

        call_kwargs = mock_client.get.call_args
        params = call_kwargs[1].get("params") or call_kwargs[1]["params"]
        assert params.get("sortBy") == "OBJECTID"

    @pytest.mark.asyncio
    async def test_wfs_get_features_sets_outputFormat_application_json(self):
        """outputFormat=application/json is hardcoded (required for GeoJSON body)."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            await wfs_get_features(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)

        call_kwargs = mock_client.get.call_args
        params = call_kwargs[1].get("params") or call_kwargs[1]["params"]
        assert params.get("outputFormat") == "application/json"

    @pytest.mark.asyncio
    async def test_wfs_get_features_passes_cql_filter(self):
        """When cql_filter is provided, CQL_FILTER appears in request params."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            await wfs_get_features(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                cql_filter="FIRE_YEAR=2023",
                httpx_client=mock_client,
            )

        call_kwargs = mock_client.get.call_args
        params = call_kwargs[1].get("params") or call_kwargs[1]["params"]
        assert params.get("CQL_FILTER") == "FIRE_YEAR=2023"

    @pytest.mark.asyncio
    async def test_wfs_get_features_delegates_to_parse_geojson(self):
        """_parse_geojson is called with response bytes and include_geometry kwarg."""
        body = _make_geojson_response(n_features=2, number_returned=2)
        body_bytes = json.dumps(body).encode("utf-8")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = body_bytes
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]) as mock_parse:
            await wfs_get_features(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                include_geometry=True,
                httpx_client=mock_client,
            )

        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        # include_geometry should be True
        passed_geometry = call_args[1].get("include_geometry") or (
            call_args[0][1] if len(call_args[0]) > 1 else None
        )
        assert passed_geometry is True

    @pytest.mark.asyncio
    async def test_wfs_get_features_raises_WfsError_on_400_xml(self):
        """HTTP 400 with XML content-type and ows:ExceptionReport raises WfsError."""
        mock_client = _make_mock_client(
            status_code=400,
            content_type="application/xml",
            text=WFS_EXCEPTION_REPORT_XML,
        )

        with pytest.raises(WfsError) as exc_info:
            await wfs_get_features(WFS_BASE_URL, "NO_SUCH_LAYER", httpx_client=mock_client)

        err = exc_info.value
        assert err.code == "InvalidParameterValue"
        assert "NO_SUCH_LAYER" in err.message

    @pytest.mark.asyncio
    async def test_wfs_get_features_does_not_call_json_on_400(self):
        """response.json() is NEVER invoked on the 400 error path."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = WFS_EXCEPTION_REPORT_XML
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(WfsError):
            await wfs_get_features(WFS_BASE_URL, "NO_SUCH_LAYER", httpx_client=mock_client)

        mock_response.json.assert_not_called()

    # ---------------------------------------------------------------------------
    # wfs_page_all tests
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_wfs_page_all_paginates_until_last_page(self):
        """Two pages (1000 + 500) return 1500 features, truncated=False."""
        page1 = _make_geojson_response(n_features=3, number_returned=1000)
        page2 = _make_geojson_response(n_features=2, number_returned=500)

        call_count = 0

        async def mock_get_features(base_url, type_name, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return ([{"id": i} for i in range(1000)], True)
            return ([{"id": i} for i in range(1000, 1500)], False)

        with patch("mcp_canada.shared.ogc.wfs_get_features", side_effect=mock_get_features):
            features, truncated = await wfs_page_all(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                max_records=5000,
                page_size=1000,
            )

        assert len(features) == 1500
        assert truncated is False

    @pytest.mark.asyncio
    async def test_wfs_page_all_truncates_at_max_records(self):
        """max_records=2000 with 3 full pages returns exactly 2000 features, truncated=True."""
        call_count = 0

        async def mock_get_features(base_url, type_name, **kwargs):
            nonlocal call_count
            call_count += 1
            # Always has_more=True (infinite data source simulation)
            return ([{"id": call_count * 1000 + i} for i in range(1000)], True)

        with patch("mcp_canada.shared.ogc.wfs_get_features", side_effect=mock_get_features):
            features, truncated = await wfs_page_all(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                max_records=2000,
                page_size=1000,
            )

        assert len(features) == 2000
        assert truncated is True

    @pytest.mark.asyncio
    async def test_wfs_page_all_respects_page_size(self):
        """page_size=500 is passed as count to wfs_get_features."""
        async def mock_get_features(base_url, type_name, count=1000, **kwargs):
            return ([{"id": 0}], False)

        with patch("mcp_canada.shared.ogc.wfs_get_features", side_effect=mock_get_features) as mock_fn:
            await wfs_page_all(
                WFS_BASE_URL,
                ACTIVE_FIRES_LAYER,
                page_size=500,
            )

        # Verify count=500 was passed
        call_kwargs = mock_fn.call_args[1]
        assert call_kwargs.get("count") == 500

    # ---------------------------------------------------------------------------
    # wfs_count test
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_wfs_count_uses_resultType_hits(self):
        """wfs_count sends resultType=hits and reads totalFeatures from the response."""
        hits_body = {
            "type": "FeatureCollection",
            "totalFeatures": 42,
            "numberMatched": 42,
            "numberReturned": 0,
            "features": [],
        }
        mock_client = _make_mock_client(response_body=hits_body)

        count = await wfs_count(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)

        assert count == 42
        call_kwargs = mock_client.get.call_args[1].get("params") or mock_client.get.call_args[1]["params"]
        assert call_kwargs.get("resultType") == "hits"

    # ---------------------------------------------------------------------------
    # httpx client injection
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_httpx_client_injection_used_when_provided(self):
        """The passed-in AsyncClient is used directly — no new client is created."""
        body = _make_geojson_response(n_features=1, number_returned=1)
        mock_client = _make_mock_client(response_body=body)

        with patch("mcp_canada.shared.ogc._parse_geojson", return_value=[{"a": 1}]):
            with patch("httpx.AsyncClient") as mock_constructor:
                await wfs_get_features(WFS_BASE_URL, ACTIVE_FIRES_LAYER, httpx_client=mock_client)
                mock_constructor.assert_not_called()

        mock_client.get.assert_called_once()
