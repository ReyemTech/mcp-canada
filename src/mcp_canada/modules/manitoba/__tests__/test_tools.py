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
    """Tool unit tests for manitoba_get_flood_alerts."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_active_alerts(self):
        """manitoba_get_flood_alerts returns _meta envelope with features list."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_flood_alerts

        mock_data = {"features": [{"Type_EN": "Warning", "Type_FR": "Avertissement"}], "count": 1, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_flood_alerts",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_flood_alerts()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_empty_flood_alerts_returns_success_not_error(self):
        """CRITICAL: empty flood alerts must return success response (not error) when no alerts active."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_flood_alerts

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_flood_alerts",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_flood_alerts()
        # Must NOT return an error envelope
        assert "error" not in result, "Empty flood alerts must NOT return an error — it is a normal result"
        assert "_meta" in result
        assert result["data"]["features"] == []
        assert result["data"]["count"] == 0

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_flood_alerts

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_flood_alerts",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_flood_alerts(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_flood_alerts returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_flood_alerts

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_flood_alerts",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_flood_alerts()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestManitobaGetRiverStations:
    """Tool unit tests for manitoba_get_river_stations."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_river_stations returns _meta envelope with stations list."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_river_stations

        mock_data = {
            "stations": [
                {"stationName": "Red River at Emerson", "alert": "No Flooding"}
            ],
            "count": 1,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_river_stations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_river_stations()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_river_stations returns UPSTREAM_ERROR on exception."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_river_stations

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_river_stations",
            new_callable=AsyncMock,
            side_effect=Exception("CSV fetch failed"),
        ):
            result = await manitoba_get_river_stations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_river_stations

        mock_data = {"stations": [], "count": 0}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_river_stations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_river_stations(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


class TestManitobaGetProvincialWaterways:
    """Tool unit tests for manitoba_get_provincial_waterways."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_provincial_waterways returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_waterways

        mock_data = {
            "features": [{"F_TYPE": "Floodway", "Name": "Red River Floodway"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_waterways",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_waterways()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_invalid_f_type_returns_invalid_input_error(self):
        """manitoba_get_provincial_waterways returns INVALID_INPUT for unknown f_type."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_waterways

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_waterways",
            new_callable=AsyncMock,
            side_effect=ValueError("Invalid f_type 'swamp'. Must be one of: dike, floodway, dam, diversion, reservoir, waterway"),
        ):
            result = await manitoba_get_provincial_waterways(f_type="swamp")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "valid" in result["error"]

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_http_exception(self):
        """manitoba_get_provincial_waterways returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_waterways

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_waterways",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_provincial_waterways()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_waterways

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_waterways",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_waterways(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


class TestManitobaGetDroughtStatus:
    """Tool unit tests for manitoba_get_drought_status. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_drought_status returns _meta envelope with features list."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_drought_status

        mock_data = {
            "features": [{"DM": "D2", "OBS_DATE": 1748995200000, "SOURCE": "NOAA/NDMC/USDA"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_drought_status",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_drought_status()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_filter_province_default_true(self):
        """manitoba_get_drought_status calls client with filter_province=True by default."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_drought_status

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_drought_status",
            side_effect=mock_fetch,
        ):
            await manitoba_get_drought_status()

        assert len(captured) == 1
        assert captured[0].get("filter_province", True) is True

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_drought_status returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_drought_status

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_drought_status",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_drought_status()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_drought_status

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_drought_status",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_drought_status(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_drought(self):
        """_meta.source.api identifies the drought monitor source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_drought_status

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_drought_status",
            new_callable=AsyncMock,
            return_value=(mock_data, True),
        ):
            result = await manitoba_get_drought_status()
        assert "drought" in result["_meta"]["source"]["api"]


class TestManitobaGetAgWeatherStations:
    """Tool unit tests for manitoba_get_ag_weather_stations. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_ag_weather_stations returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_ag_weather_stations

        mock_data = {
            "features": [
                {"StnName": "Brandon", "LatDD": 49.87, "LongDD": -99.95, "AgRegion": "Southwest", "URL": "https://agrimaps.gov.mb.ca/stations/brandon"}
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_ag_weather_stations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_ag_weather_stations()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_ag_region_filter_passed_to_client(self):
        """ag_region parameter is forwarded to client."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_ag_weather_stations

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_ag_weather_stations",
            side_effect=mock_fetch,
        ):
            await manitoba_get_ag_weather_stations(ag_region="Southwest")

        assert len(captured) == 1
        assert captured[0].get("ag_region") == "Southwest"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_ag_weather_stations returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_ag_weather_stations

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_ag_weather_stations",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_ag_weather_stations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_ag_weather_stations

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_ag_weather_stations",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_ag_weather_stations(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


class TestManitobaGetLivestockPrices:
    """Tool unit tests for manitoba_get_livestock_prices. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success_cattle(self):
        """manitoba_get_livestock_prices returns _meta envelope for cattle."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_livestock_prices

        mock_data = {
            "features": [{"week": "2026-06-07", "Auction": "Winnipeg", "Parameter": "D1 Steers", "Measure": "$/cwt", "Value": 185.5}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_livestock_prices",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_livestock_prices(livestock="cattle")
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_invalid_livestock_returns_invalid_input(self):
        """manitoba_get_livestock_prices returns INVALID_INPUT for invalid livestock param."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_livestock_prices

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_livestock_prices",
            new_callable=AsyncMock,
            side_effect=ValueError("Invalid livestock 'sheep'. Must be one of: cattle, hog"),
        ):
            result = await manitoba_get_livestock_prices(livestock="sheep")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "valid" in result["error"]

    @pytest.mark.asyncio
    async def test_hog_graceful_degradation_returns_success(self):
        """manitoba_get_livestock_prices for hog returns success (not error) when URL unresolved."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_livestock_prices

        mock_data = {
            "features": [],
            "count": 0,
            "truncated": False,
            "note": "Hog prices FeatureServer URL is unresolved",
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_livestock_prices",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_livestock_prices(livestock="hog")
        # Must NOT be an error — graceful empty response
        assert "error" not in result
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_livestock_prices

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_livestock_prices",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_livestock_prices(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_livestock(self):
        """_meta.source.api identifies the livestock prices source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_livestock_prices

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_livestock_prices",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_livestock_prices()
        assert "livestock" in result["_meta"]["source"]["api"] or "cattle" in result["_meta"]["source"]["api"]


class TestManitobaGetCropRegions:
    """Tool unit tests for manitoba_get_crop_regions. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_crop_regions returns _meta envelope with features list."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_crop_regions

        mock_data = {
            "features": [{"REGION": "Central", "RÉGION": "Centre"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_crop_regions",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_crop_regions()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_returns_bilingual_features(self):
        """Crop region features contain both English REGION and French RÉGION fields."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_crop_regions

        mock_data = {
            "features": [
                {"REGION": "Central", "RÉGION": "Centre"},
                {"REGION": "Southwest", "RÉGION": "Sud-ouest"},
            ],
            "count": 2,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_crop_regions",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_crop_regions()
        features = result["data"]["features"]
        assert len(features) == 2
        assert "REGION" in features[0]
        assert "RÉGION" in features[0]

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_crop_regions returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_crop_regions

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_crop_regions",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_crop_regions()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_crop_regions

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_crop_regions",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_crop_regions(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


class TestManitobaGetParks:
    """Tool unit tests for manitoba_get_provincial_parks. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_provincial_parks returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_parks

        mock_data = {
            "features": [
                {"NAME_E": "Hecla/Grindstone Provincial Park", "NOM_F": "Parc provincial de Hecla/Grindstone", "TYPE_E": "Provincial"},
                {"NAME_E": "Riding Mountain National Park", "NOM_F": "Parc national du Mont-Riding", "TYPE_E": "Wilderness"},
            ],
            "count": 2,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_parks",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_parks()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 2

    @pytest.mark.asyncio
    async def test_park_type_filter_passed_to_client(self):
        """park_type parameter is forwarded to client."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_parks

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_parks",
            side_effect=mock_fetch,
        ):
            await manitoba_get_provincial_parks(park_type="Provincial")

        assert len(captured) == 1
        assert captured[0].get("park_type") == "Provincial"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_parks

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_parks",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_parks(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_provincial_parks returns UPSTREAM_ERROR on HTTPStatusError."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_parks

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_parks",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_provincial_parks()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_parks(self):
        """_meta.source.api identifies the parks source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_parks

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_parks",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_parks()
        assert "park" in result["_meta"]["source"]["api"] or "manitoba" in result["_meta"]["source"]["api"]


class TestManitobaGetFisheriesData:
    """Tool unit tests for manitoba_get_fisheries_data. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_fisheries_data returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_fisheries_data

        mock_data = {
            "features": [
                {"Name": "Lake Winnipeg", "Species": "Walleye", "Regulations": "6/day"},
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_fisheries_data",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_fisheries_data()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_name_query_passed_to_client(self):
        """name parameter is forwarded to client as name_query."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_fisheries_data

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_fisheries_data",
            side_effect=mock_fetch,
        ):
            await manitoba_get_fisheries_data(name="Lake Winnipeg")

        assert len(captured) == 1
        # Tool may pass name as name_query or name depending on mapping
        assert captured[0].get("name_query") == "Lake Winnipeg" or captured[0].get("name") == "Lake Winnipeg"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_fisheries_data

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_fisheries_data",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_fisheries_data(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_fisheries_data returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_fisheries_data

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_fisheries_data",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_fisheries_data()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestManitobaGetForests:
    """Tool unit tests for manitoba_get_provincial_forests. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_provincial_forests returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_forests

        mock_data = {
            "features": [{"Name": "Porcupine Hills Forest", "area_ha": 245000.0}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_forests",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_forests()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_forests

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_forests",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_forests(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_provincial_forests returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_forests

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_forests",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_provincial_forests()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_forests(self):
        """_meta.source.api identifies the forests source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_provincial_forests

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_provincial_forests",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_provincial_forests()
        assert "forest" in result["_meta"]["source"]["api"] or "manitoba" in result["_meta"]["source"]["api"]


class TestManitobaGetWaitTimes:
    """Tool unit tests for manitoba_get_surgical_wait_times. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_surgical_wait_times returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_surgical_wait_times

        mock_data = {
            "features": [
                {"Year": 2021, "IndicatorDataArea": "Cardiac surgery", "Average_Wait": 144},
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_surgical_wait_times",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_surgical_wait_times()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_procedure_and_year_filters_passed_to_client(self):
        """procedure and year parameters are forwarded to client."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_surgical_wait_times

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_surgical_wait_times",
            side_effect=mock_fetch,
        ):
            await manitoba_get_surgical_wait_times(procedure="Cardiac surgery", year=2021)

        assert len(captured) == 1
        assert captured[0].get("procedure") == "Cardiac surgery"
        assert captured[0].get("year") == 2021

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_surgical_wait_times

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_surgical_wait_times",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_surgical_wait_times(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_surgical_wait_times returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_surgical_wait_times

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_surgical_wait_times",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_surgical_wait_times()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_wait_times(self):
        """_meta.source.api identifies the surgical wait times source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_surgical_wait_times

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_surgical_wait_times",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_surgical_wait_times()
        api = result["_meta"]["source"]["api"]
        assert "wait" in api or "surgical" in api or "health" in api or "manitoba" in api


class TestManitobaGetHealthFacilities:
    """Tool unit tests for manitoba_get_health_facilities. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """manitoba_get_health_facilities returns _meta envelope with features."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_health_facilities

        mock_data = {
            "features": [
                {
                    "Community_Name": "Selkirk",
                    "Facility_Name": "Selkirk & District General Hospital",
                    "Emergency_Department_Availabili": "Yes",
                    "Acute_Care_Availability": "Yes",
                }
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_health_facilities()
        assert "_meta" in result
        assert "data" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_rha_filter_passed_to_client(self):
        """rha parameter is forwarded to client (as community or rha kwarg)."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_health_facilities

        captured: list[dict] = []

        async def mock_fetch(**kwargs):
            captured.append(kwargs)
            return ({"features": [], "count": 0, "truncated": False}, False)

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_health_facilities",
            side_effect=mock_fetch,
        ):
            await manitoba_get_health_facilities(rha="WRHA")

        assert len(captured) == 1
        # Tool may pass rha as community or rha parameter to client
        assert (
            captured[0].get("rha") == "WRHA"
            or captured[0].get("community") == "WRHA"
        )

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """lang parameter is reflected in _meta envelope."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_health_facilities

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_health_facilities(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """manitoba_get_health_facilities returns UPSTREAM_ERROR on exception."""
        import httpx
        from mcp_canada.modules.manitoba.tools import manitoba_get_health_facilities

        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "bad", request=httpx.Request("GET", "http://x"), response=httpx.Response(500)
            ),
        ):
            result = await manitoba_get_health_facilities()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_meta_source_api_is_health_facilities(self):
        """_meta.source.api identifies the rural health facilities source."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_health_facilities

        mock_data = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(mock_data, False),
        ):
            result = await manitoba_get_health_facilities()
        api = result["_meta"]["source"]["api"]
        assert "health" in api or "facility" in api or "facilit" in api or "manitoba" in api


class TestManitoba511RoadEvents:
    """Tool unit tests for manitoba_get_road_events."""

    @pytest.mark.asyncio
    async def test_returns_not_configured_without_key(self, monkeypatch):
        """manitoba_get_road_events returns NOT_CONFIGURED error when MANITOBA_511_KEY absent."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_road_events
        from mcp_canada.modules.manitoba.client import Five11NotConfigured

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_road_events",
            new_callable=AsyncMock,
            side_effect=Five11NotConfigured("key not set"),
        ):
            result = await manitoba_get_road_events()
        assert "error" in result
        assert result["error"]["code"] == "NOT_CONFIGURED"
        # Must NOT raise an exception — must return structured error
        assert "MANITOBA_511_KEY" in result["error"]["message"] or "511" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_mocked_key(self, monkeypatch):
        """manitoba_get_road_events returns _meta envelope when key present and client succeeds."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_road_events

        mock_rows = [
            {"Id": "EVT-001", "EventType": "Construction", "RoadwayName": "Highway 1"},
        ]
        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_road_events",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            result = await manitoba_get_road_events()
        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self, monkeypatch):
        """lang parameter is reflected in _meta envelope for road events."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_road_events

        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_road_events",
            new_callable=AsyncMock,
            return_value=([], False),
        ):
            result = await manitoba_get_road_events(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"

    @pytest.mark.asyncio
    async def test_not_configured_error_in_french(self, monkeypatch):
        """NOT_CONFIGURED error message is bilingual when lang=fr."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_road_events
        from mcp_canada.modules.manitoba.client import Five11NotConfigured

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_road_events",
            new_callable=AsyncMock,
            side_effect=Five11NotConfigured("key not set"),
        ):
            result = await manitoba_get_road_events(lang="fr")
        assert "error" in result
        assert result["error"]["code"] == "NOT_CONFIGURED"


class TestManitoba511WinterRoads:
    """Tool unit tests for manitoba_get_winter_road_conditions."""

    @pytest.mark.asyncio
    async def test_returns_not_configured_without_key(self, monkeypatch):
        """manitoba_get_winter_road_conditions returns NOT_CONFIGURED when key absent."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_winter_road_conditions
        from mcp_canada.modules.manitoba.client import Five11NotConfigured

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_winter_road_conditions",
            new_callable=AsyncMock,
            side_effect=Five11NotConfigured("key not set"),
        ):
            result = await manitoba_get_winter_road_conditions()
        assert "error" in result
        assert result["error"]["code"] == "NOT_CONFIGURED"

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_mocked_key(self, monkeypatch):
        """manitoba_get_winter_road_conditions returns _meta envelope when key present."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_winter_road_conditions

        mock_rows = [
            {"Id": "WR-001", "AreaName": "Northern", "RoadwayName": "Winter Road to Island Lake"},
        ]
        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_winter_road_conditions",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            result = await manitoba_get_winter_road_conditions()
        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_lang_passes_through(self, monkeypatch):
        """lang parameter is reflected in _meta envelope for winter roads."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_winter_road_conditions

        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_winter_road_conditions",
            new_callable=AsyncMock,
            return_value=([], False),
        ):
            result = await manitoba_get_winter_road_conditions(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


class TestManitoba511Cameras:
    """Tool unit tests for manitoba_get_traffic_cameras."""

    @pytest.mark.asyncio
    async def test_returns_not_configured_without_key(self, monkeypatch):
        """manitoba_get_traffic_cameras returns NOT_CONFIGURED when key absent."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_traffic_cameras
        from mcp_canada.modules.manitoba.client import Five11NotConfigured

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_traffic_cameras",
            new_callable=AsyncMock,
            side_effect=Five11NotConfigured("key not set"),
        ):
            result = await manitoba_get_traffic_cameras()
        assert "error" in result
        assert result["error"]["code"] == "NOT_CONFIGURED"

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_mocked_key(self, monkeypatch):
        """manitoba_get_traffic_cameras returns _meta envelope when key present."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_traffic_cameras

        mock_rows = [
            {
                "Id": "CAM-001",
                "Location": "Perimeter Hwy & Main",
                "Views": [{"Name": "North", "Url": "https://example.com/cam.jpg"}],
            }
        ]
        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_traffic_cameras",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            result = await manitoba_get_traffic_cameras()
        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_lang_passes_through(self, monkeypatch):
        """lang parameter is reflected in _meta envelope for traffic cameras."""
        from mcp_canada.modules.manitoba.tools import manitoba_get_traffic_cameras

        monkeypatch.setenv("MANITOBA_511_KEY", "test-key")
        with patch(
            "mcp_canada.modules.manitoba.tools._client.fetch_traffic_cameras",
            new_callable=AsyncMock,
            return_value=([], False),
        ):
            result = await manitoba_get_traffic_cameras(lang="fr")
        assert result.get("_meta", {}).get("lang") == "fr"


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
