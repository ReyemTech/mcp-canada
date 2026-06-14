"""Manitoba tools unit tests.

Wave 0 placeholder classes — Plans 02-06 fill test bodies.
TestManitobaEnvelopes and TestManitobaLangParam are parametrized by Plan 08.

Client is patched at the tools module namespace:
  mcp_canada.modules.manitoba.tools._client.<func>
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.modules.manitoba.tools import (
    manitoba_get_dataset_details,
    manitoba_list_categories,
    manitoba_list_organizations,
    manitoba_query_dataset,
    manitoba_search_datasets,
)


# ---------------------------------------------------------------------------
# TestManitobaSearchDatasets
# ---------------------------------------------------------------------------


class TestManitobaSearchDatasets:
    """Tool unit tests for manitoba_search_datasets. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_search_datasets returns _meta envelope on success."""
        mock_data = {
            "results": [{"id": "abc", "title": "Parks dataset"}],
            "total": 1,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_search_datasets(query="parks")
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["total"] == 1

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_search_datasets returns make_error on httpx.HTTPStatusError."""
        import httpx

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_search_datasets(query="parks")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        mock_data = {"results": [], "total": 0}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_search_datasets(query="test", lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_meta_source_is_hub(self):
        """_meta.source.api is 'manitoba-geoportal-hub'."""
        mock_data = {"results": [], "total": 0}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(mock_data, True),
        ):
            result = await manitoba_search_datasets(query="flood")
        assert result["_meta"]["source"]["api"] == "manitoba-geoportal-hub"


# ---------------------------------------------------------------------------
# TestManitobaGetDatasetDetails
# ---------------------------------------------------------------------------


class TestManitobaGetDatasetDetails:
    """Tool unit tests for manitoba_get_dataset_details. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_dataset_details returns _meta envelope with details."""
        mock_data = {
            "details": {
                "id": "abc123",
                "title": "Manitoba Parks",
                "feature_server_url": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer",
                "download_urls": [],
                "tags": ["parks"],
                "categories": ["/Categories/Environment"],
            }
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_dataset_details(dataset_id="abc123")
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["details"]["feature_server_url"] is not None

    @pytest.mark.asyncio
    async def test_returns_not_found_on_value_error(self):
        """manitoba_get_dataset_details returns NOT_FOUND on ValueError."""
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=ValueError("Dataset not found: bogus-id"),
        ):
            result = await manitoba_get_dataset_details(dataset_id="bogus-id")
        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_http_error(self):
        """manitoba_get_dataset_details returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_dataset_details(dataset_id="some-id")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_requires_non_empty_dataset_id(self):
        """manitoba_get_dataset_details returns INVALID_INPUT for empty dataset_id."""
        result = await manitoba_get_dataset_details(dataset_id="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        mock_data = {
            "details": {"id": "abc", "title": "Parks", "feature_server_url": None, "download_urls": []}
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_dataset_details(dataset_id="abc", lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


# ---------------------------------------------------------------------------
# TestManitobaQueryDataset
# ---------------------------------------------------------------------------


class TestManitobaQueryDataset:
    """Tool unit tests for manitoba_query_dataset. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_query_dataset returns _meta envelope on success."""
        mock_payload = {
            "data": [{"NAME_E": "Hecla Park"}],
            "url": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer",
            "rows": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(mock_payload, False),
        ):
            result = await manitoba_query_dataset(
                dataset_url="https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer"
            )
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_query_dataset returns UPSTREAM_ERROR on exception."""
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            side_effect=Exception("arcgis failed"),
        ):
            result = await manitoba_query_dataset(
                dataset_url="https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer"
            )
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_requires_non_empty_dataset_url(self):
        """manitoba_query_dataset returns INVALID_INPUT for empty dataset_url."""
        result = await manitoba_query_dataset(dataset_url="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_max_records_clamped_to_5000(self):
        """max_records > 5000 is silently clamped to 5000."""
        mock_payload = {"data": [], "url": "https://example.com/FeatureServer", "rows": 0}
        captured_kwargs: list = []

        async def _mock_fetch(**kwargs):
            captured_kwargs.append(kwargs)
            return (mock_payload, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_query_dataset",
            side_effect=_mock_fetch,
        ):
            await manitoba_query_dataset(dataset_url="https://example.com/FeatureServer", max_records=99999)
        assert len(captured_kwargs) == 1
        assert captured_kwargs[0].get("max_records", 0) <= 5000

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        mock_payload = {"data": [], "url": "https://example.com/FeatureServer", "rows": 0}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(mock_payload, False),
        ):
            result = await manitoba_query_dataset(
                dataset_url="https://example.com/FeatureServer", lang="fr"
            )
        assert result.get("_meta", {}).get("lang") == "fr"


# ---------------------------------------------------------------------------
# TestManitobaListOrgs
# ---------------------------------------------------------------------------


class TestManitobaListOrgs:
    """Tool unit tests for manitoba_list_organizations. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_list_organizations returns _meta envelope with organizations."""
        mock_data = {"organizations": ["Manitoba_Government", "Manitoba_Agriculture"]}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_list_organizations()
        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"]["organizations"], list)

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_list_organizations returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_list_organizations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        mock_data = {"organizations": []}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_list_organizations(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


# ---------------------------------------------------------------------------
# TestManitobaListCategories
# ---------------------------------------------------------------------------


class TestManitobaListCategories:
    """Tool unit tests for manitoba_list_categories. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_list_categories returns _meta envelope with categories."""
        mock_data = {"categories": ["/Categories/Environment", "/Categories/Agriculture"]}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_list_categories()
        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"]["categories"], list)

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_list_categories returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_categories",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_list_categories()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        mock_data = {"categories": []}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_list_categories(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


# ---------------------------------------------------------------------------
# Placeholder classes for Plans 03-06 (unfilled)
# ---------------------------------------------------------------------------


class TestManitobaGetFloodAlerts:
    """Tool unit tests for manitoba_get_flood_alerts.

    Plan 03 fills — must include test_empty_flood_alerts_returns_success_not_error.
    """

    pass


class TestManitobaGetRiverStations:
    """Tool unit tests for manitoba_get_river_stations. Plan 03 fills."""

    pass


class TestManitobaGetProvincialWaterways:
    """Tool unit tests for manitoba_get_provincial_waterways. Plan 03 fills."""

    pass


class TestManitobaGetDroughtStatus:
    """Tool unit tests for manitoba_get_drought_status. Plan 04 fills."""

    pass


class TestManitobaGetAgWeatherStations:
    """Tool unit tests for manitoba_get_ag_weather_stations. Plan 04 fills."""

    pass


class TestManitobaGetLivestockPrices:
    """Tool unit tests for manitoba_get_livestock_prices. Plan 04 fills."""

    pass


class TestManitobaGetCropRegions:
    """Tool unit tests for manitoba_get_crop_regions. Plan 04 fills."""

    pass


class TestManitobaGetParks:
    """Tool unit tests for manitoba_get_provincial_parks. Plan 05 fills."""

    pass


class TestManitobaGetFisheriesData:
    """Tool unit tests for manitoba_get_fisheries_data. Plan 05 fills."""

    pass


class TestManitobaGetForests:
    """Tool unit tests for manitoba_get_provincial_forests. Plan 05 fills."""

    pass


class TestManitobaGetWaitTimes:
    """Tool unit tests for manitoba_get_surgical_wait_times. Plan 05 fills."""

    pass


class TestManitobaGetHealthFacilities:
    """Tool unit tests for manitoba_get_health_facilities. Plan 05 fills."""

    pass


class TestManitoba511RoadEvents:
    """Tool unit tests for manitoba_get_road_events.

    Plan 06 fills — must include test_returns_not_configured_without_key.
    """

    pass


class TestManitoba511WinterRoads:
    """Tool unit tests for manitoba_get_winter_road_conditions. Plan 06 fills."""

    pass


class TestManitoba511Cameras:
    """Tool unit tests for manitoba_get_traffic_cameras. Plan 06 fills."""

    pass


class TestManitobaEnvelopes:
    """Parametrized envelope tests for all Manitoba tools.

    Plan 08 fills — verifies _meta envelope structure across all ~15 tools.
    """

    pass


class TestManitobaLangParam:
    """Parametrized lang parameter tests for all Manitoba tools.

    Plan 08 fills — verifies lang='fr' passes through to envelope for all tools.
    """

    pass
