"""Unit tests for york_region/client.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.modules.york_region.client import (
    NoPortalError,
    _escape_where_value,
    _require_portal,
    fetch_beach_water_testing,
    fetch_census_age_sex,
    fetch_census_income,
    fetch_drinking_water_incidents,
    fetch_get_dataset_details,
    fetch_hospitals,
    fetch_list_categories,
    fetch_list_organizations,
    fetch_markham_addresses,
    fetch_markham_roads,
    fetch_query_features,
    fetch_regional_roads,
    fetch_search_datasets,
    fetch_solid_waste_sites,
    fetch_transit_routes,
    fetch_transit_stops,
    fetch_waste_diversion,
)

from .conftest import (
    FEATURE_RESULT_SINGLE_PAGE,
    FEATURE_RESULT_TRUNCATED,
    HUB_SEARCH_EMPTY,
    HUB_SEARCH_RAW,
)


# ---------------------------------------------------------------------------
# TestRequirePortal
# ---------------------------------------------------------------------------

class TestRequirePortal:
    def test_valid_york_region_returns_url(self):
        url = _require_portal("york_region")
        assert "insights-york.opendata.arcgis.com" in url

    def test_valid_markham_returns_url(self):
        url = _require_portal("markham")
        assert "data-markham.opendata.arcgis.com" in url

    def test_valid_newmarket_returns_url(self):
        url = _require_portal("newmarket")
        assert "newmarket" in url.lower()

    def test_valid_aurora_returns_url(self):
        url = _require_portal("aurora")
        assert "aurora" in url.lower()

    def test_none_entry_raises_no_portal_error_vaughan(self):
        with pytest.raises(NoPortalError, match="vaughan"):
            _require_portal("vaughan")

    def test_none_entry_raises_no_portal_error_richmond_hill(self):
        with pytest.raises(NoPortalError, match="richmond_hill"):
            _require_portal("richmond_hill")

    def test_none_entry_raises_no_portal_error_king(self):
        with pytest.raises(NoPortalError, match="king"):
            _require_portal("king")

    def test_none_entry_raises_no_portal_error_east_gwillimbury(self):
        with pytest.raises(NoPortalError, match="east_gwillimbury"):
            _require_portal("east_gwillimbury")

    def test_none_entry_raises_no_portal_error_georgina(self):
        with pytest.raises(NoPortalError, match="georgina"):
            _require_portal("georgina")

    def test_whitchurch_stouffville_has_census_url(self):
        # This municipality has a census-only hub URL
        url = _require_portal("whitchurch_stouffville")
        assert url is not None
        assert "stouffville" in url.lower() or "townofws" in url.lower()

    def test_unknown_key_raises_no_portal_error(self):
        with pytest.raises(NoPortalError):
            _require_portal("nonexistent_city")


# ---------------------------------------------------------------------------
# TestFetchSearchDatasets
# ---------------------------------------------------------------------------

class TestFetchSearchDatasets:
    @pytest.mark.asyncio
    async def test_happy_path_returns_shaped_list(self):
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = HUB_SEARCH_RAW
            result, was_cached = await fetch_search_datasets("york_region", query="transit")

        assert was_cached is False
        assert len(result) == 2
        # Each item should be shaped with flat keys
        assert "title" in result[0]
        assert "url" in result[0]
        assert "description" in result[0]

    @pytest.mark.asyncio
    async def test_description_truncated_to_500_chars(self):
        raw = dict(HUB_SEARCH_RAW)
        raw["features"] = [
            {
                "id": "x",
                "properties": {
                    "title": "Test",
                    "description": "A" * 600,
                    "type": None,
                    "url": None,
                    "owner": None,
                    "tags": [],
                    "categories": [],
                    "created": None,
                    "modified": None,
                },
            }
        ]
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = raw
            result, _ = await fetch_search_datasets("york_region", query="test")

        assert len(result[0]["description"]) <= 503
        assert result[0]["description"].endswith("...")

    @pytest.mark.asyncio
    async def test_raises_no_portal_error_for_vaughan(self):
        with pytest.raises(NoPortalError):
            await fetch_search_datasets("vaughan", query="transit")

    @pytest.mark.asyncio
    async def test_cache_key_uses_york_region_prefix(self):
        captured_keys = []

        async def _recording_cached_fetch(key, ttl, fetcher):
            captured_keys.append(key)
            return (await fetcher(), False)

        with patch("mcp_canada.modules.york_region.client.cached_fetch", _recording_cached_fetch):
            with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
                mock_search.return_value = HUB_SEARCH_RAW
                await fetch_search_datasets("york_region", query="transit")

        assert any(k.startswith("york_region:") for k in captured_keys)


# ---------------------------------------------------------------------------
# TestFetchGetDatasetDetails
# ---------------------------------------------------------------------------

class TestFetchGetDatasetDetails:
    @pytest.mark.asyncio
    async def test_returns_shaped_dict_for_first_feature(self):
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = HUB_SEARCH_RAW
            result, was_cached = await fetch_get_dataset_details("york_region", "abc123")

        assert result["id"] == "abc123"
        assert result["title"] == "York Region Bus Stops"

    @pytest.mark.asyncio
    async def test_raises_value_error_when_empty_results(self):
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = HUB_SEARCH_EMPTY
            with pytest.raises(ValueError, match="dataset not found"):
                await fetch_get_dataset_details("york_region", "nonexistent")

    @pytest.mark.asyncio
    async def test_raises_no_portal_error_for_vaughan(self):
        with pytest.raises(NoPortalError):
            await fetch_get_dataset_details("vaughan", "abc")


# ---------------------------------------------------------------------------
# TestFetchQueryFeatures
# ---------------------------------------------------------------------------

class TestFetchQueryFeatures:
    @pytest.mark.asyncio
    async def test_returns_dict_with_features_count_truncated(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            result, was_cached = await fetch_query_features(
                "york_region",
                "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
                layer_id=2,
            )

        assert "features" in result
        assert "count" in result
        assert "truncated" in result
        assert result["count"] == 2
        assert result["truncated"] is False

    @pytest.mark.asyncio
    async def test_truncated_flag_propagated(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_TRUNCATED
            result, _ = await fetch_query_features(
                "york_region",
                "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer",
                layer_id=2,
            )

        assert result["truncated"] is True
        assert result["count"] == 5000

    @pytest.mark.asyncio
    async def test_cache_key_contains_service_url_and_layer_id(self):
        captured_keys = []

        async def _recording_cached_fetch(key, ttl, fetcher):
            captured_keys.append(key)
            return (await fetcher(), False)

        with patch("mcp_canada.modules.york_region.client.cached_fetch", _recording_cached_fetch):
            with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
                mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
                service_url = "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer"
                await fetch_query_features("york_region", service_url, layer_id=2)

        assert any("Transportation" in k and "2" in k for k in captured_keys)


# ---------------------------------------------------------------------------
# TestFetchListOrganizations
# ---------------------------------------------------------------------------

class TestFetchListOrganizations:
    @pytest.mark.asyncio
    async def test_returns_unique_sorted_owner_list(self):
        raw = dict(HUB_SEARCH_RAW)
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = raw
            result, was_cached = await fetch_list_organizations("york_region")

        assert isinstance(result, list)
        # Both owners from HUB_SEARCH_RAW should appear
        assert "YorkRegion_GIS" in result
        assert "YorkRegion_Health" in result
        # Should be sorted
        assert result == sorted(result)

    @pytest.mark.asyncio
    async def test_raises_no_portal_error_for_none_portal(self):
        with pytest.raises(NoPortalError):
            await fetch_list_organizations("vaughan")

    @pytest.mark.asyncio
    async def test_uses_cache_ttl_orgs(self):
        from mcp_canada.modules.york_region.constants import CACHE_TTL_ORGS

        captured = []

        async def _recording_cached_fetch(key, ttl, fetcher):
            captured.append(ttl)
            return (await fetcher(), False)

        with patch("mcp_canada.modules.york_region.client.cached_fetch", _recording_cached_fetch):
            with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
                mock_search.return_value = HUB_SEARCH_RAW
                await fetch_list_organizations("york_region")

        assert captured[0] == CACHE_TTL_ORGS


# ---------------------------------------------------------------------------
# TestFetchListCategories
# ---------------------------------------------------------------------------

class TestFetchListCategories:
    @pytest.mark.asyncio
    async def test_returns_unique_categories(self):
        with patch("mcp_canada.modules.york_region.client.search_hub_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = HUB_SEARCH_RAW
            result, _ = await fetch_list_categories("york_region")

        assert isinstance(result, list)
        assert "Transportation" in result
        assert "Health" in result
        assert "Environment" in result
        # No duplicates
        assert len(result) == len(set(result))

    @pytest.mark.asyncio
    async def test_raises_no_portal_error_for_none_portal(self):
        with pytest.raises(NoPortalError):
            await fetch_list_categories("king")


# ---------------------------------------------------------------------------
# TestCuratedYorkRegion
# ---------------------------------------------------------------------------

class TestCuratedYorkRegion:
    @pytest.mark.asyncio
    async def test_fetch_transit_stops_calls_correct_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_transit_stops()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        layer_id = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("layer_id")
        assert "Transportation" in service_url
        assert layer_id == 2  # YR_BUS_STOPS_LAYER

    @pytest.mark.asyncio
    async def test_fetch_transit_stops_with_query_produces_like_where(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_transit_stops(query="Finch")

        call_kwargs = mock_qfs.call_args
        # Find the 'where' parameter
        args = call_kwargs[0]
        kwargs = call_kwargs[1]
        where_clause = args[2] if len(args) > 2 else kwargs.get("where", "")
        assert "STOP_NAME" in where_clause
        assert "Finch" in where_clause
        assert "LIKE" in where_clause

    @pytest.mark.asyncio
    async def test_fetch_transit_routes_calls_correct_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_transit_routes()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        layer_id = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("layer_id")
        assert "Transportation" in service_url
        assert layer_id == 3  # YR_BUS_ROUTES_LAYER

    @pytest.mark.asyncio
    async def test_fetch_regional_roads_calls_correct_layer(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_regional_roads()

        call_kwargs = mock_qfs.call_args
        layer_id = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("layer_id")
        assert layer_id == 0  # YR_REGIONAL_ROADS_LAYER

    @pytest.mark.asyncio
    async def test_fetch_beach_water_testing_calls_health_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_beach_water_testing()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        layer_id = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("layer_id")
        assert "Health_And_Safety" in service_url
        assert layer_id == 0

    @pytest.mark.asyncio
    async def test_fetch_hospitals_calls_health_service_layer_1(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_hospitals()

        call_kwargs = mock_qfs.call_args
        layer_id = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("layer_id")
        assert layer_id == 1

    @pytest.mark.asyncio
    async def test_fetch_drinking_water_incidents_calls_drinking_water_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_drinking_water_incidents()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "DrinkingWater" in service_url

    @pytest.mark.asyncio
    async def test_fetch_solid_waste_sites_calls_environmental_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_solid_waste_sites()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "Environmental" in service_url

    @pytest.mark.asyncio
    async def test_fetch_census_age_sex_with_csdname_filter(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_census_age_sex(csdname="Markham")

        call_kwargs = mock_qfs.call_args
        args = call_kwargs[0]
        kwargs = call_kwargs[1]
        where_clause = args[2] if len(args) > 2 else kwargs.get("where", "")
        assert "CSDNAME" in where_clause
        assert "Markham" in where_clause

    @pytest.mark.asyncio
    async def test_fetch_census_income_calls_income_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_census_income()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "Income" in service_url or "income" in service_url.lower()

    @pytest.mark.asyncio
    async def test_fetch_waste_diversion_calls_waste_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_waste_diversion()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "Waste" in service_url or "waste" in service_url.lower()


# ---------------------------------------------------------------------------
# TestCuratedMarkham
# ---------------------------------------------------------------------------

class TestCuratedMarkham:
    @pytest.mark.asyncio
    async def test_fetch_markham_addresses_calls_addresses_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_markham_addresses()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "ADDRESSES" in service_url or "addresses" in service_url.lower()

    @pytest.mark.asyncio
    async def test_fetch_markham_addresses_with_street_filter(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_markham_addresses(street="Main")

        call_kwargs = mock_qfs.call_args
        args = call_kwargs[0]
        kwargs = call_kwargs[1]
        where_clause = args[2] if len(args) > 2 else kwargs.get("where", "")
        assert "STREET" in where_clause
        assert "Main" in where_clause
        assert "LIKE" in where_clause

    @pytest.mark.asyncio
    async def test_fetch_markham_roads_calls_roads_service(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_markham_roads()

        call_kwargs = mock_qfs.call_args
        service_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("service_url", "")
        assert "SLRN" in service_url or "roads" in service_url.lower()

    @pytest.mark.asyncio
    async def test_fetch_markham_roads_with_name_filter(self):
        with patch("mcp_canada.modules.york_region.client.query_feature_service", new_callable=AsyncMock) as mock_qfs:
            mock_qfs.return_value = FEATURE_RESULT_SINGLE_PAGE
            await fetch_markham_roads(name="Warden")

        call_kwargs = mock_qfs.call_args
        args = call_kwargs[0]
        kwargs = call_kwargs[1]
        where_clause = args[2] if len(args) > 2 else kwargs.get("where", "")
        assert "NAME" in where_clause
        assert "Warden" in where_clause
        assert "LIKE" in where_clause


# ---------------------------------------------------------------------------
# TestEscapeWhere
# ---------------------------------------------------------------------------

class TestEscapeWhere:
    def test_single_quote_doubled(self):
        result = _escape_where_value("O'Brien")
        assert result == "O''Brien"

    def test_no_single_quotes_unchanged(self):
        result = _escape_where_value("Finch Ave")
        assert result == "Finch Ave"

    def test_multiple_single_quotes_all_doubled(self):
        result = _escape_where_value("it's o'clock")
        assert result == "it''s o''clock"

    def test_empty_string_unchanged(self):
        result = _escape_where_value("")
        assert result == ""
