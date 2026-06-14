"""Manitoba client unit tests.

Wave 0 placeholder classes — Plans 02-06 fill test bodies.
TestSharedApiGetContract patches mcp_canada.modules.manitoba.client.api_get
(module-local pattern from Phase 17 — achieves same regression guard as
shared-layer patch, works with Python from-import semantics).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_canada.modules.manitoba.client import (
    Five11NotConfigured,
    _hub_get,
    fetch_categories,
    fetch_dataset_details,
    fetch_organizations,
    fetch_query_dataset,
    fetch_search_datasets,
)

from .conftest import (
    HUB_ITEM_DETAIL,
    HUB_SEARCH_EMPTY,
    HUB_SEARCH_RAW,
)


# ---------------------------------------------------------------------------
# TestSharedApiGetContract — enforces parsed-dict convention for _hub_get
# ---------------------------------------------------------------------------


class TestSharedApiGetContract:
    """Ensure mcp_canada.shared.http.api_get is patched at the right layer.

    Verifies _hub_get:
      - calls api_get once with HUB_SEARCH_URL
      - returns the Hub JSON dict directly (never inspects .get("success"))
      - raises httpx.HTTPStatusError when api_get returns a non-dict
    """

    @pytest.mark.asyncio
    async def test_hub_get_calls_api_get_once(self):
        """_hub_get calls api_get exactly once with HUB_SEARCH_URL."""
        hub_response = {"numberMatched": 2, "features": [], "results": []}
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=hub_response,
        ) as mock_api_get:
            result = await _hub_get({"q": "parks"})
        mock_api_get.assert_called_once()
        # First positional arg should be HUB_SEARCH_URL
        from mcp_canada.modules.manitoba.constants import HUB_SEARCH_URL
        assert mock_api_get.call_args[0][0] == HUB_SEARCH_URL

    @pytest.mark.asyncio
    async def test_hub_get_returns_dict_directly(self):
        """_hub_get returns the Hub JSON dict without inspecting CKAN keys."""
        hub_response = {"numberMatched": 1, "features": [{"id": "x"}]}
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=hub_response,
        ):
            result = await _hub_get({"q": "flood"})
        assert result == hub_response
        # Ensure no CKAN envelope inspection — result is NOT envelope.get("result")
        assert "numberMatched" in result

    @pytest.mark.asyncio
    async def test_hub_get_raises_on_non_dict_response(self):
        """_hub_get raises HTTPStatusError when api_get returns a non-dict (list, str, etc)."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=["not", "a", "dict"],
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await _hub_get({"q": "test"})

    @pytest.mark.asyncio
    async def test_hub_get_raises_on_none_response(self):
        """_hub_get raises HTTPStatusError when api_get returns None."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await _hub_get({})


# ---------------------------------------------------------------------------
# TestManitobaSearchDatasets
# ---------------------------------------------------------------------------


class TestManitobaSearchDatasets:
    """Unit tests for fetch_search_datasets. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_results_and_total(self):
        """fetch_search_datasets returns dict with results list and total count."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_search_datasets("parks")
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 2
        assert data["total"] == 82

    @pytest.mark.asyncio
    async def test_returns_empty_results_for_no_match(self):
        """fetch_search_datasets returns empty results list when Hub finds nothing."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_EMPTY,
        ):
            data, cached = await fetch_search_datasets("nonexistent_xyzzy")
        assert data["results"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_raises_on_hub_error(self):
        """fetch_search_datasets propagates HTTPStatusError on non-dict api_get response."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value="bad",
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_search_datasets("parks")

    @pytest.mark.asyncio
    async def test_result_items_are_flat_summaries(self):
        """Returned items are flat dicts with id, title, snippet, type, url fields."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_search_datasets("parks")
        first = data["results"][0]
        assert "id" in first
        assert "title" in first


# ---------------------------------------------------------------------------
# TestManitobaGetDatasetDetails
# ---------------------------------------------------------------------------


class TestManitobaGetDatasetDetails:
    """Unit tests for fetch_dataset_details. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_details_with_feature_server_url(self):
        """fetch_dataset_details returns dict including feature_server_url."""
        # HUB_ITEM_DETAIL is a single-item Hub response (properties.url contains FS URL)
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_ITEM_DETAIL,
        ):
            data, cached = await fetch_dataset_details("b71a8d37a75e4215ba13b8695261a403")
        assert "details" in data
        details = data["details"]
        assert "feature_server_url" in details
        assert "title" in details

    @pytest.mark.asyncio
    async def test_raises_not_found_on_empty_result(self):
        """fetch_dataset_details raises ValueError when item not found (empty search)."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value={"numberMatched": 0, "numberReturned": 0, "features": []},
        ):
            with pytest.raises((ValueError, httpx.HTTPStatusError)):
                await fetch_dataset_details("nonexistent-id")

    @pytest.mark.asyncio
    async def test_returns_download_urls(self):
        """fetch_dataset_details includes download_urls list."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_ITEM_DETAIL,
        ):
            data, _ = await fetch_dataset_details("b71a8d37a75e4215ba13b8695261a403")
        assert "download_urls" in data["details"]
        assert isinstance(data["details"]["download_urls"], list)


# ---------------------------------------------------------------------------
# TestManitobaQueryDataset
# ---------------------------------------------------------------------------


class TestManitobaQueryDataset:
    """Unit tests for fetch_query_dataset (hybrid auto-router). Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_routes_feature_server_to_arcgis_hub(self):
        """fetch_query_dataset routes FeatureServer URL to arcgis_hub.query_feature_service."""
        feature_server_url = (
            "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_Parks/FeatureServer"
        )
        mock_rows = [{"NAME_E": "Hecla Park", "TYPE_E": "Provincial"}]
        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            data, cached = await fetch_query_dataset(feature_server_url)
        assert "data" in data
        assert data["data"] == mock_rows

    @pytest.mark.asyncio
    async def test_routes_csv_url_to_fetch_and_parse(self):
        """fetch_query_dataset routes CSV URL to fetch_and_parse."""
        csv_url = "https://example.com/data.csv"
        mock_rows = [{"col1": "a", "col2": "b"}]
        with patch(
            "mcp_canada.modules.manitoba.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            data, cached = await fetch_query_dataset(csv_url)
        assert "data" in data
        assert data["data"] == mock_rows

    @pytest.mark.asyncio
    async def test_routes_geojson_url_to_fetch_and_parse(self):
        """fetch_query_dataset routes .geojson URL to fetch_and_parse."""
        geojson_url = "https://example.com/data.geojson"
        mock_rows = [{"type": "Feature"}]
        with patch(
            "mcp_canada.modules.manitoba.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            data, cached = await fetch_query_dataset(geojson_url)
        assert "data" in data

    @pytest.mark.asyncio
    async def test_returns_metadata_only_for_pdf(self):
        """fetch_query_dataset returns metadata-only payload for PDF/binary URLs."""
        pdf_url = "https://example.com/report.pdf"
        data, cached = await fetch_query_dataset(pdf_url)
        assert "note" in data or "url" in data
        # Should NOT have data field with rows
        assert "data" not in data or data.get("note") is not None


# ---------------------------------------------------------------------------
# TestManitobaListOrgs
# ---------------------------------------------------------------------------


class TestManitobaListOrgs:
    """Unit tests for fetch_organizations. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_organizations_list(self):
        """fetch_organizations returns dict with organizations list."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_organizations()
        assert "organizations" in data
        assert isinstance(data["organizations"], list)

    @pytest.mark.asyncio
    async def test_organizations_are_non_empty_strings(self):
        """Returned organizations list contains non-empty strings."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_organizations()
        # HUB_SEARCH_RAW has owner="Manitoba_Government" on both features
        for org in data["organizations"]:
            assert isinstance(org, str)
            assert org  # non-empty


# ---------------------------------------------------------------------------
# TestManitobaListCategories
# ---------------------------------------------------------------------------


class TestManitobaListCategories:
    """Unit tests for fetch_categories. Plan 02 fills."""

    @pytest.mark.asyncio
    async def test_returns_categories_list(self):
        """fetch_categories returns dict with categories list."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_categories()
        assert "categories" in data
        assert isinstance(data["categories"], list)

    @pytest.mark.asyncio
    async def test_categories_are_non_empty_strings(self):
        """Returned categories are non-empty strings."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_categories()
        for cat in data["categories"]:
            assert isinstance(cat, str)
            assert cat


# ---------------------------------------------------------------------------
# Placeholder classes for Plans 03-06 (unfilled)
# ---------------------------------------------------------------------------


class TestManitobaGetFloodAlerts:
    """Unit tests for fetch_flood_alerts.

    Must include test_flood_alerts_empty_when_no_active_alerts
    verifying that empty features list is correct (not an error).
    """

    @pytest.mark.asyncio
    async def test_returns_features_and_count(self):
        """fetch_flood_alerts returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_flood_alerts
        from .conftest import SAMPLE_FLOOD_ALERTS_ACTIVE

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FLOOD_ALERTS_ACTIVE,
        ):
            data, cached = await fetch_flood_alerts()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert isinstance(data["features"], list)
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_flood_alerts_empty_when_no_active_alerts(self):
        """CRITICAL: empty features list is a VALID result when no alerts active — not an error."""
        from mcp_canada.modules.manitoba.client import fetch_flood_alerts
        from .conftest import SAMPLE_FLOOD_ALERTS_EMPTY

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FLOOD_ALERTS_EMPTY,
        ):
            # Must NOT raise; must return a valid (dict, bool) tuple
            data, was_cached = await fetch_flood_alerts()
        assert isinstance(data, dict)
        assert "features" in data
        assert data["features"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_flood_alerts_active_returns_bilingual_fields(self):
        """Active alerts contain Type_EN and Type_FR bilingual fields."""
        from mcp_canada.modules.manitoba.client import fetch_flood_alerts
        from .conftest import SAMPLE_FLOOD_ALERTS_ACTIVE

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FLOOD_ALERTS_ACTIVE,
        ):
            data, _ = await fetch_flood_alerts()
        first = data["features"][0]
        assert "Type_EN" in first or "Type_FR" in first  # at least one bilingual field present


class TestManitobaGetRiverStations:
    """Unit tests for fetch_river_stations (CSV source). Plan 03 fills."""

    @pytest.mark.asyncio
    async def test_returns_stations_payload(self):
        """fetch_river_stations returns {stations, count} payload from CSV."""
        from mcp_canada.modules.manitoba.client import fetch_river_stations
        from .conftest import SAMPLE_RIVER_STATIONS_FEATURES

        rows, _ = SAMPLE_RIVER_STATIONS_FEATURES
        with patch(
            "mcp_canada.modules.manitoba.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=(rows, False),
        ):
            data, cached = await fetch_river_stations()
        assert "stations" in data
        assert "count" in data
        assert isinstance(data["stations"], list)

    @pytest.mark.asyncio
    async def test_returns_valid_payload_on_empty_csv(self):
        """fetch_river_stations returns empty stations (not error) when CSV is empty."""
        from mcp_canada.modules.manitoba.client import fetch_river_stations

        with patch(
            "mcp_canada.modules.manitoba.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=([], False),
        ):
            data, _ = await fetch_river_stations()
        assert isinstance(data, dict)
        assert data["stations"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_station_has_alert_field(self):
        """Each station row includes an alert status field."""
        from mcp_canada.modules.manitoba.client import fetch_river_stations
        from .conftest import SAMPLE_RIVER_STATIONS_FEATURES

        rows, _ = SAMPLE_RIVER_STATIONS_FEATURES
        with patch(
            "mcp_canada.modules.manitoba.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=(rows, False),
        ):
            data, _ = await fetch_river_stations()
        # Stations should pass-through the alert field from the CSV
        if data["stations"]:
            assert "alert" in data["stations"][0]


class TestManitobaGetWaterways:
    """Unit tests for fetch_provincial_waterways. Plan 03 fills."""

    @pytest.mark.asyncio
    async def test_returns_all_waterways_no_filter(self):
        """fetch_provincial_waterways returns {features, count, truncated} with no f_type filter."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_waterways
        from .conftest import SAMPLE_WATERWAYS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_WATERWAYS_FEATURES,
        ):
            data, cached = await fetch_provincial_waterways()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data

    @pytest.mark.asyncio
    async def test_applies_f_type_filter(self):
        """fetch_provincial_waterways passes WHERE clause when f_type given."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_waterways

        captured_kwargs: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_kwargs.append(kwargs)
            return ([{"F_TYPE": "Floodway", "Name": "Red River Floodway"}], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            data, _ = await fetch_provincial_waterways(f_type="floodway")
        assert len(captured_kwargs) == 1
        # WHERE clause should reference the F_TYPE field
        where_clause = captured_kwargs[0].get("where", "")
        assert "F_TYPE" in where_clause or "Floodway" in where_clause

    @pytest.mark.asyncio
    async def test_invalid_f_type_raises_value_error(self):
        """fetch_provincial_waterways raises ValueError for unknown f_type."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_waterways

        with pytest.raises(ValueError, match="Invalid f_type"):
            await fetch_provincial_waterways(f_type="swamp")


class TestManitobaGetDroughtStatus:
    """Unit tests for fetch_drought_status. Plan 04 fills."""

    pass


class TestManitobaGetAgWeatherStations:
    """Unit tests for fetch_ag_weather_stations. Plan 04 fills."""

    pass


class TestManitobaGetLivestockPrices:
    """Unit tests for fetch_livestock_prices. Plan 04 fills."""

    pass


class TestManitobaGetCropRegions:
    """Unit tests for fetch_crop_regions. Plan 04 fills."""

    pass


class TestManitobaGetParks:
    """Unit tests for fetch_provincial_parks. Plan 05 fills."""

    pass


class TestManitobaGetFisheriesData:
    """Unit tests for fetch_fisheries_data. Plan 05 fills."""

    pass


class TestManitobaGetForests:
    """Unit tests for fetch_provincial_forests. Plan 05 fills."""

    pass


class TestManitobaGetWaitTimes:
    """Unit tests for fetch_surgical_wait_times. Plan 05 fills."""

    pass


class TestManitobaGetHealthFacilities:
    """Unit tests for fetch_health_facilities. Plan 05 fills."""

    pass


class TestManitoba511:
    """Unit tests for 511 client functions (fetch_road_events, etc.). Plan 06 fills.

    Must include:
    - test_raises_five11_not_configured_when_no_key
    - test_road_events_with_mocked_key
    - test_winter_roads_with_mocked_key
    - test_cameras_with_mocked_key
    """

    pass
