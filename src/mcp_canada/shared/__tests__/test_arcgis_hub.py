"""Unit tests for shared/arcgis_hub.py — ArcGIS Hub Search API + FeatureServer client."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from mcp_canada.shared.arcgis_hub import (
    get_count,
    get_layer_metadata,
    query_feature_service,
    search_hub_datasets,
    shape_hub_dataset,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HUB_SEARCH_SAMPLE: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 442,
    "numberReturned": 2,
    "features": [
        {
            "id": "abc123",
            "properties": {
                "title": "York Region Bus Stops",
                "type": "Feature Service",
                "description": "All YRT/Viva bus stop locations in York Region.",
                "url": "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer/2",
                "owner": "YorkRegion_GIS",
                "tags": ["transit", "bus", "stops"],
                "categories": ["Transportation"],
                "created": "2021-01-15T00:00:00.000Z",
                "modified": "2024-06-01T00:00:00.000Z",
            },
        },
        {
            "id": "def456",
            "properties": {
                "title": "Beach Water Testing",
                "type": "Feature Service",
                "description": "Annual beach water testing results for York Region beaches.",
                "url": "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Health_And_Safety/FeatureServer/0",
                "owner": "YorkRegion_Health",
                "tags": ["health", "beaches", "water"],
                "categories": ["Health", "Environment"],
                "created": "2020-05-01T00:00:00.000Z",
                "modified": "2023-08-15T00:00:00.000Z",
            },
        },
    ],
    "links": [],
}

# A very long description to test truncation
_LONG_DESC = "A" * 600

HUB_SEARCH_SAMPLE_LONG_DESC: dict[str, Any] = {
    "type": "FeatureCollection",
    "numberMatched": 1,
    "numberReturned": 1,
    "features": [
        {
            "id": "ghi789",
            "properties": {
                "title": "Long Description Dataset",
                "type": "Table",
                "description": _LONG_DESC,
                "url": None,
                "owner": "TestOwner",
                "tags": [],
                "categories": [],
                "created": None,
                "modified": None,
            },
        }
    ],
    "links": [],
}

# Two-page paginated GeoJSON
FEATURE_SERVICE_PAGE_1_WITH_LIMIT = json.dumps({
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"OBJECTID": 1, "STOP_NAME": "Stop A"}, "geometry": None},
        {"type": "Feature", "properties": {"OBJECTID": 2, "STOP_NAME": "Stop B"}, "geometry": None},
    ],
    "exceededTransferLimit": True,
}).encode()

FEATURE_SERVICE_PAGE_2_FINAL = json.dumps({
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"OBJECTID": 3, "STOP_NAME": "Stop C"}, "geometry": None},
    ],
}).encode()

FEATURE_SERVICE_EMPTY = json.dumps({
    "type": "FeatureCollection",
    "features": [],
}).encode()

FEATURE_SERVICE_WITH_GEOMETRY = json.dumps({
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"OBJECTID": 1, "STOP_NAME": "Stop A"},
            "geometry": {"type": "Point", "coordinates": [-79.12, 43.87]},
        }
    ],
}).encode()

LAYER_METADATA_SAMPLE = {
    "maxRecordCount": 2000,
    "fields": [
        {"name": "OBJECTID", "type": "esriFieldTypeOID"},
        {"name": "STOP_NAME", "type": "esriFieldTypeString"},
    ],
    "geometryType": "esriGeometryPoint",
    "name": "Bus Stops",
}

COUNT_SAMPLE = {"count": 4810}


# ---------------------------------------------------------------------------
# Helper to build a mock httpx.AsyncClient
# ---------------------------------------------------------------------------

def _make_mock_client(responses: list[bytes | dict]) -> MagicMock:
    """Build a MagicMock AsyncClient with .get() returning successive responses."""
    mock_client = MagicMock()
    mock_responses = []
    for resp_data in responses:
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.raise_for_status = MagicMock()
        if isinstance(resp_data, bytes):
            mock_resp.content = resp_data
            mock_resp.json.return_value = json.loads(resp_data)
        else:
            mock_resp.content = json.dumps(resp_data).encode()
            mock_resp.json.return_value = resp_data
        mock_responses.append(mock_resp)

    get_mock = AsyncMock(side_effect=mock_responses)
    mock_client.get = get_mock
    return mock_client


# ---------------------------------------------------------------------------
# TestSearchHubDatasets
# ---------------------------------------------------------------------------


class TestSearchHubDatasets:
    @pytest.mark.asyncio
    async def test_happy_path_returns_raw_dict(self):
        """search_hub_datasets returns raw dict with features list on success."""
        mock_client = _make_mock_client([HUB_SEARCH_SAMPLE])

        result = await search_hub_datasets(
            "https://insights-york.opendata.arcgis.com",
            query="bus stops",
            limit=10,
            offset=0,
            httpx_client=mock_client,
        )

        assert result["type"] == "FeatureCollection"
        assert result["numberMatched"] == 442
        assert len(result["features"]) == 2
        assert result["features"][0]["properties"]["title"] == "York Region Bus Stops"

    @pytest.mark.asyncio
    async def test_raises_value_error_when_portal_none(self):
        """search_hub_datasets raises ValueError when portal_base_url is None."""
        with pytest.raises(ValueError, match="no public ArcGIS Hub"):
            await search_hub_datasets(None, query="transit")

    @pytest.mark.asyncio
    async def test_empty_query_works(self):
        """Empty query string is allowed and returns all items."""
        mock_client = _make_mock_client([HUB_SEARCH_SAMPLE])

        result = await search_hub_datasets(
            "https://insights-york.opendata.arcgis.com",
            query="",
            httpx_client=mock_client,
        )

        assert "features" in result
        # Verify the GET call was made with empty q param
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params.get("q", "") == ""

    @pytest.mark.asyncio
    async def test_offset_zero_omitted_from_params(self):
        """offset=0 omits BOTH 'offset' and 'startindex' from query params.

        OGC API Records: startindex=0 is invalid (returns malformed body live).
        Must omit entirely when offset==0.
        """
        mock_client = _make_mock_client([HUB_SEARCH_SAMPLE])

        await search_hub_datasets(
            "https://insights-york.opendata.arcgis.com",
            query="transit",
            offset=0,
            httpx_client=mock_client,
        )

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert "offset" not in params
        assert "startindex" not in params

    @pytest.mark.asyncio
    async def test_offset_positive_sends_startindex_not_offset(self):
        """offset > 0 sends 'startindex' (OGC API Records), NOT 'offset'.

        Saskatchewan GeoHub (OGC API Records) requires startindex, not offset.
        ?offset=N returns {numberMatched: null}; ?startindex=N returns correct pagination.
        """
        mock_client = _make_mock_client([HUB_SEARCH_SAMPLE])

        await search_hub_datasets(
            "https://insights-york.opendata.arcgis.com",
            query="transit",
            offset=10,
            httpx_client=mock_client,
        )

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params.get("startindex") == 10
        assert "offset" not in params


# ---------------------------------------------------------------------------
# TestQueryFeatureService
# ---------------------------------------------------------------------------


class TestQueryFeatureService:
    @pytest.mark.asyncio
    async def test_single_page_returns_features_no_truncation(self):
        """Single page with no exceededTransferLimit returns features, truncated=False."""
        mock_client = _make_mock_client([FEATURE_SERVICE_PAGE_2_FINAL])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert len(features) == 1
        assert not truncated
        assert features[0]["STOP_NAME"] == "Stop C"

    @pytest.mark.asyncio
    async def test_multi_page_pagination_follows_exceeded_transfer_limit(self):
        """Pagination continues until exceededTransferLimit is False."""
        mock_client = _make_mock_client([
            FEATURE_SERVICE_PAGE_1_WITH_LIMIT,
            FEATURE_SERVICE_PAGE_2_FINAL,
        ])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert len(features) == 3
        assert not truncated
        assert features[0]["STOP_NAME"] == "Stop A"
        assert features[2]["STOP_NAME"] == "Stop C"

    @pytest.mark.asyncio
    async def test_max_records_cap_sets_truncated_true(self):
        """When max_records cap hit with exceededTransferLimit still True, truncated=True."""
        # Each page returns 2 features with exceededTransferLimit, cap at 2
        mock_client = _make_mock_client([FEATURE_SERVICE_PAGE_1_WITH_LIMIT])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            max_records=2,  # cap at 2
            httpx_client=mock_client,
        )

        assert len(features) == 2
        assert truncated is True

    @pytest.mark.asyncio
    async def test_empty_feature_collection_returns_empty_list(self):
        """Empty FeatureCollection returns ([], False)."""
        mock_client = _make_mock_client([FEATURE_SERVICE_EMPTY])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert features == []
        assert truncated is False

    @pytest.mark.asyncio
    async def test_include_geometry_true_includes_geometry_key(self):
        """include_geometry=True includes 'geometry' key in returned dicts."""
        mock_client = _make_mock_client([FEATURE_SERVICE_WITH_GEOMETRY])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            include_geometry=True,
            httpx_client=mock_client,
        )

        assert len(features) == 1
        assert "geometry" in features[0]
        assert features[0]["geometry"]["type"] == "Point"

    @pytest.mark.asyncio
    async def test_include_geometry_false_excludes_geometry_key(self):
        """include_geometry=False (default) excludes 'geometry' key."""
        mock_client = _make_mock_client([FEATURE_SERVICE_WITH_GEOMETRY])

        features, truncated = await query_feature_service(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            include_geometry=False,
            httpx_client=mock_client,
        )

        assert len(features) == 1
        assert "geometry" not in features[0]


# ---------------------------------------------------------------------------
# TestGetLayerMetadata
# ---------------------------------------------------------------------------


class TestGetLayerMetadata:
    @pytest.mark.asyncio
    async def test_returns_shaped_metadata(self):
        """get_layer_metadata returns {max_record_count, fields, geometry_type, name}."""
        mock_client = _make_mock_client([LAYER_METADATA_SAMPLE])

        result = await get_layer_metadata(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert result["max_record_count"] == 2000
        assert len(result["fields"]) == 2
        assert result["fields"][0]["name"] == "OBJECTID"
        assert result["geometry_type"] == "esriGeometryPoint"
        assert result["name"] == "Bus Stops"

    @pytest.mark.asyncio
    async def test_handles_no_geometry_type(self):
        """get_layer_metadata handles layers with no geometryType (tables)."""
        table_meta = {
            "maxRecordCount": 1000,
            "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"}],
            "name": "Adverse Incidents",
        }
        mock_client = _make_mock_client([table_meta])

        result = await get_layer_metadata(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/DrinkingWater/FeatureServer",
            layer_id=0,
            httpx_client=mock_client,
        )

        assert result["geometry_type"] is None
        assert result["name"] == "Adverse Incidents"


# ---------------------------------------------------------------------------
# TestGetCount
# ---------------------------------------------------------------------------


class TestGetCount:
    @pytest.mark.asyncio
    async def test_returns_integer_count(self):
        """get_count returns integer from count response."""
        mock_client = _make_mock_client([COUNT_SAMPLE])

        count = await get_count(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert count == 4810

    @pytest.mark.asyncio
    async def test_returns_zero_on_missing_count_key(self):
        """get_count returns 0 when 'count' key absent from response."""
        mock_client = _make_mock_client([{}])

        count = await get_count(
            "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
            layer_id=2,
            httpx_client=mock_client,
        )

        assert count == 0


# ---------------------------------------------------------------------------
# TestShapeHubDataset
# ---------------------------------------------------------------------------


class TestShapeHubDataset:
    def test_maps_properties_to_flat_dict(self):
        """shape_hub_dataset returns a flat dict with expected keys."""
        feature = HUB_SEARCH_SAMPLE["features"][0]
        result = shape_hub_dataset(feature)

        assert result["id"] == "abc123"
        assert result["title"] == "York Region Bus Stops"
        assert result["type"] == "Feature Service"
        assert result["owner"] == "YorkRegion_GIS"
        assert result["tags"] == ["transit", "bus", "stops"]
        assert result["categories"] == ["Transportation"]
        assert result["url"] is not None

    def test_truncates_long_descriptions(self):
        """shape_hub_dataset truncates descriptions longer than MAX_DESCRIPTION_CHARS."""
        feature = HUB_SEARCH_SAMPLE_LONG_DESC["features"][0]
        result = shape_hub_dataset(feature)

        assert len(result["description"]) <= 503  # 500 + "..."
        assert result["description"].endswith("...")

    def test_handles_missing_optional_fields(self):
        """shape_hub_dataset handles features with missing/None optional fields."""
        feature = {
            "properties": {
                "title": "Minimal Dataset",
                # no id at top level
            }
        }
        result = shape_hub_dataset(feature)

        assert result["title"] == "Minimal Dataset"
        assert result.get("id") is None
        assert result.get("type") is None
        assert result.get("tags") == []
        assert result.get("categories") == []

    def test_short_description_not_truncated(self):
        """Descriptions under 500 chars are not truncated or modified."""
        feature = HUB_SEARCH_SAMPLE["features"][0]
        original_desc = feature["properties"]["description"]
        result = shape_hub_dataset(feature)

        assert result["description"] == original_desc
        assert not result["description"].endswith("...")


class TestEmptyQueryOmitsQParam:
    """An empty query must omit `q`, not send `q=`.

    Every ArcGIS Hub portal rejects an empty q with HTTP 400 (verified
    2026-07-25 against aurora, newmarket, york_region, markham and manitoba —
    all five return 400 for q='' and 200 when q is omitted).

    This broke every "list everything" call across the four Hub-backed modules:
    York Region's aurora_list_categories and newmarket_search_datasets both
    surfaced UPSTREAM_ERROR. It read as an upstream outage, and the integration
    tests' `if "data" in data:` guards skipped their assertions on the error
    response, so it stayed invisible.

    Mirrors the startindex handling directly below it — startindex=0 is invalid
    upstream and is likewise omitted rather than sent as zero.
    """

    @pytest.mark.asyncio
    async def test_empty_query_omits_q(self):
        from mcp_canada.shared.arcgis_hub import search_hub_datasets

        client = AsyncMock()
        response = MagicMock()
        response.json.return_value = {"features": []}
        response.raise_for_status = MagicMock()
        client.get = AsyncMock(return_value=response)

        await search_hub_datasets("https://example.hub.arcgis.com", query="", httpx_client=client)

        params = client.get.await_args.kwargs["params"]
        assert "q" not in params, (
            f"an empty q is rejected with HTTP 400 by every Hub portal — omit it "
            f"instead of sending an empty string. Sent: {params}"
        )
        assert params["limit"]

    @pytest.mark.asyncio
    async def test_whitespace_only_query_omits_q(self):
        from mcp_canada.shared.arcgis_hub import search_hub_datasets

        client = AsyncMock()
        response = MagicMock()
        response.json.return_value = {"features": []}
        response.raise_for_status = MagicMock()
        client.get = AsyncMock(return_value=response)

        await search_hub_datasets("https://example.hub.arcgis.com", query="   ", httpx_client=client)

        assert "q" not in client.get.await_args.kwargs["params"], (
            "a whitespace-only query is equivalent to no query"
        )

    @pytest.mark.asyncio
    async def test_real_query_still_sends_q(self):
        from mcp_canada.shared.arcgis_hub import search_hub_datasets

        client = AsyncMock()
        response = MagicMock()
        response.json.return_value = {"features": []}
        response.raise_for_status = MagicMock()
        client.get = AsyncMock(return_value=response)

        await search_hub_datasets("https://example.hub.arcgis.com", query="transit", httpx_client=client)

        assert client.get.await_args.kwargs["params"]["q"] == "transit"
