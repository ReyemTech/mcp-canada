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
            await _hub_get({"q": "parks"})
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

    # ------------------------------------------------------------------
    # Param-regression tests (Plan 09 — RED before fix, GREEN after)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_sends_ogc_params(self):
        """fetch_search_datasets sends OGC 'limit' (not 'num') and no 'start' param."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("parks")
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "limit" in params, f"Expected 'limit' in params, got: {params}"
        # limit is clamped to max 100 by min(max(num,1), 100); value is a positive int
        assert isinstance(params["limit"], int) and params["limit"] >= 1
        assert params.get("q") == "parks"
        assert "num" not in params, f"'num' must NOT be in params, got: {params}"
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"
        assert "startindex" not in params, f"'startindex' must not appear when start==0, got: {params}"

    @pytest.mark.asyncio
    async def test_search_omits_startindex_when_start_zero(self):
        """fetch_search_datasets omits 'startindex' when start=0 (startindex=0 is invalid live)."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("parks_zero_start", start=0)
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "startindex" not in params, (
            f"startindex must be omitted when start==0 (live API returns 400), got: {params}"
        )
        assert "start" not in params

    @pytest.mark.asyncio
    async def test_search_sets_startindex_when_start_positive(self):
        """fetch_search_datasets sends 'startindex' (1-based) when start > 0, not 'start'."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("parks_paged", start=10)
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "startindex" in params, (
            f"Expected 'startindex' in params when start>0, got: {params}"
        )
        assert params["startindex"] == 10
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"

    @pytest.mark.asyncio
    async def test_search_passes_category_as_categories(self):
        """fetch_search_datasets passes category value under 'categories' key."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("parks_cat", category="/Categories/Environment")
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert params.get("categories") == "/Categories/Environment", (
            f"Expected categories='/Categories/Environment' in params, got: {params}"
        )

    # ------------------------------------------------------------------
    # Original tests (unchanged)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Param-regression test (Plan 09 — RED before fix, GREEN after)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_orgs_send_ogc_params_no_blank_q(self):
        """fetch_organizations sends 'limit' (not 'num'), no 'start', and no empty 'q'."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_organizations()
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "limit" in params, f"Expected 'limit' in params, got: {params}"
        assert "num" not in params, f"'num' must NOT be in params, got: {params}"
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"
        # Empty q="" causes HTTP 400 on the live API — must be omitted entirely
        assert "q" not in params, (
            f"Blank 'q' must be omitted (live API returns 400 for q=empty), got: {params}"
        )

    # ------------------------------------------------------------------
    # Original tests (unchanged)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Param-regression test (Plan 09 — RED before fix, GREEN after)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_categories_send_ogc_params_no_blank_q(self):
        """fetch_categories sends 'limit' (not 'num'), no 'start', and no empty 'q'."""
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_categories()
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "limit" in params, f"Expected 'limit' in params, got: {params}"
        assert "num" not in params, f"'num' must NOT be in params, got: {params}"
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"
        # Empty q="" causes HTTP 400 on the live API — must be omitted entirely
        assert "q" not in params, (
            f"Blank 'q' must be omitted (live API returns 400 for q=empty), got: {params}"
        )

    # ------------------------------------------------------------------
    # Original tests (unchanged)
    # ------------------------------------------------------------------

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

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_drought_status returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_drought_status
        from .conftest import SAMPLE_DROUGHT_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_DROUGHT_FEATURES,
        ):
            data, cached = await fetch_drought_status()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_filter_province_applies_bbox_geometry(self):
        """fetch_drought_status with filter_province=True sends geometry envelope to FeatureServer."""
        from mcp_canada.modules.manitoba.client import fetch_drought_status

        captured_calls: list[dict] = []

        async def mock_api_get(url, params, **kwargs):
            captured_calls.append({"url": url, "params": params})
            # Return a valid ArcGIS FeatureServer /query JSON response
            return {
                "features": [{"attributes": {"DM": "D1", "OBS_DATE": 1748995200000, "SOURCE": "NOAA"}}],
                "exceededTransferLimit": False,
            }

        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            side_effect=mock_api_get,
        ):
            data, _ = await fetch_drought_status(filter_province=True)

        # Must have called api_get with geometry params
        assert len(captured_calls) == 1
        call = captured_calls[0]
        # Geometry envelope param must be present
        assert "geometry" in call["params"]
        assert "geometryType" in call["params"]
        assert call["params"]["geometryType"] == "esriGeometryEnvelope"
        # Manitoba bbox values should be in the geometry string
        assert "101" in call["params"]["geometry"] or "48" in call["params"]["geometry"]
        # Spatial relationship must be set
        assert "spatialRel" in call["params"]

    @pytest.mark.asyncio
    async def test_no_filter_returns_all_features(self):
        """fetch_drought_status with filter_province=False queries without spatial filter."""
        from mcp_canada.modules.manitoba.client import fetch_drought_status
        from .conftest import SAMPLE_DROUGHT_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_DROUGHT_FEATURES,
        ):
            data, _ = await fetch_drought_status(filter_province=False)
        assert isinstance(data["features"], list)

    @pytest.mark.asyncio
    async def test_features_contain_dm_and_obs_date(self):
        """Drought features include DM intensity code and OBS_DATE fields."""
        from mcp_canada.modules.manitoba.client import fetch_drought_status
        from .conftest import SAMPLE_DROUGHT_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_DROUGHT_FEATURES,
        ):
            data, _ = await fetch_drought_status()
        if data["features"]:
            feat = data["features"][0]
            assert "DM" in feat or "dm" in feat or "OBS_DATE" in feat


class TestManitobaGetAgWeatherStations:
    """Unit tests for fetch_ag_weather_stations. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count(self):
        """fetch_ag_weather_stations returns {features, count} payload."""
        from mcp_canada.modules.manitoba.client import fetch_ag_weather_stations
        from .conftest import SAMPLE_AG_WEATHER_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_AG_WEATHER_FEATURES,
        ):
            data, cached = await fetch_ag_weather_stations()
        assert "features" in data
        assert "count" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_ag_region_filter_applied(self):
        """fetch_ag_weather_stations passes WHERE clause when ag_region provided."""
        from mcp_canada.modules.manitoba.client import fetch_ag_weather_stations

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_ag_weather_stations(ag_region="Southwest")

        assert len(captured) == 1
        where = captured[0].get("where", "")
        assert "Southwest" in where or "AgRegion" in where

    @pytest.mark.asyncio
    async def test_no_ag_region_returns_all(self):
        """fetch_ag_weather_stations with no region returns all stations."""
        from mcp_canada.modules.manitoba.client import fetch_ag_weather_stations
        from .conftest import SAMPLE_AG_WEATHER_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_AG_WEATHER_FEATURES,
        ):
            data, _ = await fetch_ag_weather_stations()
        assert data["count"] == 2

    @pytest.mark.asyncio
    async def test_station_has_url_field(self):
        """Each station includes URL field linking to live hourly data."""
        from mcp_canada.modules.manitoba.client import fetch_ag_weather_stations
        from .conftest import SAMPLE_AG_WEATHER_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_AG_WEATHER_FEATURES,
        ):
            data, _ = await fetch_ag_weather_stations()
        if data["features"]:
            assert "URL" in data["features"][0] or "url" in data["features"][0]


class TestManitobaGetLivestockPrices:
    """Unit tests for fetch_livestock_prices. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_cattle_returns_features_count(self):
        """fetch_livestock_prices(livestock='cattle') returns {features, count} payload."""
        from mcp_canada.modules.manitoba.client import fetch_livestock_prices
        from .conftest import SAMPLE_LIVESTOCK_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_LIVESTOCK_FEATURES,
        ):
            data, cached = await fetch_livestock_prices(livestock="cattle")
        assert "features" in data
        assert "count" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_hog_degrades_gracefully(self):
        """fetch_livestock_prices(livestock='hog') returns empty or error gracefully when HOG_PRICES_FS_URL is None."""
        from mcp_canada.modules.manitoba.client import fetch_livestock_prices

        # Should not raise — must return (dict, bool) even when hog URL unresolved
        result = await fetch_livestock_prices(livestock="hog")
        assert isinstance(result, tuple)
        assert isinstance(result[0], dict)
        assert isinstance(result[1], bool)

    @pytest.mark.asyncio
    async def test_invalid_livestock_raises_value_error(self):
        """fetch_livestock_prices raises ValueError for livestock not in {'cattle','hog'}."""
        from mcp_canada.modules.manitoba.client import fetch_livestock_prices

        with pytest.raises(ValueError, match="cattle.*hog|hog.*cattle|livestock"):
            await fetch_livestock_prices(livestock="sheep")

    @pytest.mark.asyncio
    async def test_cattle_uses_cattle_fs_url(self):
        """fetch_livestock_prices for cattle queries CATTLE_PRICES_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_livestock_prices
        from mcp_canada.modules.manitoba.constants import CATTLE_PRICES_FS_URL

        captured: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_livestock_prices(livestock="cattle")

        assert len(captured) == 1
        assert CATTLE_PRICES_FS_URL in captured[0] or captured[0] == CATTLE_PRICES_FS_URL


class TestManitobaGetCropRegions:
    """Unit tests for fetch_crop_regions. Plan 04 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count(self):
        """fetch_crop_regions returns {features, count} payload."""
        from mcp_canada.modules.manitoba.client import fetch_crop_regions
        from .conftest import SAMPLE_CROP_REGIONS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_CROP_REGIONS_FEATURES,
        ):
            data, cached = await fetch_crop_regions()
        assert "features" in data
        assert "count" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_features_are_bilingual(self):
        """Crop region features include both REGION (EN) and RÉGION (FR) fields."""
        from mcp_canada.modules.manitoba.client import fetch_crop_regions
        from .conftest import SAMPLE_CROP_REGIONS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_CROP_REGIONS_FEATURES,
        ):
            data, _ = await fetch_crop_regions()
        if data["features"]:
            feat = data["features"][0]
            # Must have both English and French region name fields
            assert "REGION" in feat
            assert "RÉGION" in feat

    @pytest.mark.asyncio
    async def test_queries_crop_regions_fs_url(self):
        """fetch_crop_regions queries CROP_REGIONS_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_crop_regions
        from mcp_canada.modules.manitoba.constants import CROP_REGIONS_FS_URL

        captured: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_crop_regions()

        assert len(captured) == 1
        assert CROP_REGIONS_FS_URL in captured[0] or captured[0] == CROP_REGIONS_FS_URL


class TestManitobaGetParks:
    """Unit tests for fetch_provincial_parks. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_provincial_parks returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_parks
        from .conftest import SAMPLE_PARKS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_PARKS_FEATURES,
        ):
            data, cached = await fetch_provincial_parks()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_returns_bilingual_name_fields(self):
        """Parks features include NAME_E (English) and NOM_F (French) fields."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_parks
        from .conftest import SAMPLE_PARKS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_PARKS_FEATURES,
        ):
            data, _ = await fetch_provincial_parks()
        if data["features"]:
            feat = data["features"][0]
            assert "NAME_E" in feat
            assert "NOM_F" in feat

    @pytest.mark.asyncio
    async def test_park_type_filter_applied(self):
        """fetch_provincial_parks builds WHERE TYPE_E=... clause for park_type filter."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_parks

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_provincial_parks(park_type="Provincial")

        assert len(captured) == 1
        where = captured[0].get("where", "")
        assert "TYPE_E" in where or "Provincial" in where

    @pytest.mark.asyncio
    async def test_no_park_type_returns_all(self):
        """fetch_provincial_parks with no park_type returns all parks (WHERE 1=1)."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_parks
        from .conftest import SAMPLE_PARKS_FEATURES

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return SAMPLE_PARKS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_provincial_parks()

        assert captured[0].get("where", "") == "1=1"

    @pytest.mark.asyncio
    async def test_queries_parks_fs_url(self):
        """fetch_provincial_parks calls query_feature_service with PROVINCIAL_PARKS_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_parks
        from mcp_canada.modules.manitoba.constants import PROVINCIAL_PARKS_FS_URL

        captured_urls: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_urls.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_provincial_parks()

        assert len(captured_urls) == 1
        assert PROVINCIAL_PARKS_FS_URL in captured_urls[0] or captured_urls[0] == PROVINCIAL_PARKS_FS_URL


class TestManitobaGetFisheriesData:
    """Unit tests for fetch_fisheries_data. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_fisheries_data returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_fisheries_data
        from .conftest import SAMPLE_FISHERIES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FISHERIES_FEATURES,
        ):
            data, cached = await fetch_fisheries_data()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_features_include_species_and_regulations(self):
        """Fisheries features include Species and Regulations fields."""
        from mcp_canada.modules.manitoba.client import fetch_fisheries_data
        from .conftest import SAMPLE_FISHERIES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FISHERIES_FEATURES,
        ):
            data, _ = await fetch_fisheries_data()
        if data["features"]:
            feat = data["features"][0]
            # Should include species and regulations from the 26-field focused subset
            assert "Species" in feat or "Regulations" in feat or "Name" in feat

    @pytest.mark.asyncio
    async def test_name_query_filter_applied(self):
        """fetch_fisheries_data builds WHERE Name LIKE ... clause for name_query."""
        from mcp_canada.modules.manitoba.client import fetch_fisheries_data

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_fisheries_data(name_query="Lake Winnipeg")

        assert len(captured) == 1
        where = captured[0].get("where", "")
        assert "Lake Winnipeg" in where or "Name" in where or "LIKE" in where

    @pytest.mark.asyncio
    async def test_fishing_division_filter_applied(self):
        """fetch_fisheries_data filters by FishingDivision when provided."""
        from mcp_canada.modules.manitoba.client import fetch_fisheries_data

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_fisheries_data(fishing_division="Division 1")

        assert len(captured) == 1
        where = captured[0].get("where", "")
        assert "Division 1" in where or "FishingDivision" in where

    @pytest.mark.asyncio
    async def test_queries_waterbody_fs_url(self):
        """fetch_fisheries_data calls query_feature_service with WATERBODY_DATA_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_fisheries_data
        from mcp_canada.modules.manitoba.constants import WATERBODY_DATA_FS_URL

        captured_urls: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_urls.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_fisheries_data()

        assert len(captured_urls) == 1
        assert WATERBODY_DATA_FS_URL in captured_urls[0] or captured_urls[0] == WATERBODY_DATA_FS_URL


class TestManitobaGetForests:
    """Unit tests for fetch_provincial_forests. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_provincial_forests returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_forests
        from .conftest import SAMPLE_FORESTS_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_FORESTS_FEATURES,
        ):
            data, cached = await fetch_provincial_forests()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_queries_forests_fs_url(self):
        """fetch_provincial_forests calls query_feature_service with PROVINCIAL_FORESTS_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_forests
        from mcp_canada.modules.manitoba.constants import PROVINCIAL_FORESTS_FS_URL

        captured_urls: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_urls.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_provincial_forests()

        assert len(captured_urls) == 1
        assert PROVINCIAL_FORESTS_FS_URL in captured_urls[0] or captured_urls[0] == PROVINCIAL_FORESTS_FS_URL

    @pytest.mark.asyncio
    async def test_include_geometry_false_by_default(self):
        """fetch_provincial_forests defaults to include_geometry=False."""
        from mcp_canada.modules.manitoba.client import fetch_provincial_forests

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_provincial_forests()

        assert captured[0].get("include_geometry", True) is False


class TestManitobaGetWaitTimes:
    """Unit tests for fetch_surgical_wait_times. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_surgical_wait_times returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_surgical_wait_times
        from .conftest import SAMPLE_WAIT_TIMES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_WAIT_TIMES_FEATURES,
        ):
            data, cached = await fetch_surgical_wait_times()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_features_include_year_procedure_avg_wait(self):
        """Wait time features include Year, IndicatorDataArea, Average_Wait fields."""
        from mcp_canada.modules.manitoba.client import fetch_surgical_wait_times
        from .conftest import SAMPLE_WAIT_TIMES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_WAIT_TIMES_FEATURES,
        ):
            data, _ = await fetch_surgical_wait_times()
        if data["features"]:
            feat = data["features"][0]
            assert "Year" in feat
            assert "IndicatorDataArea" in feat
            assert "Average_Wait" in feat

    @pytest.mark.asyncio
    async def test_year_filter_applied(self):
        """fetch_surgical_wait_times builds WHERE Year=... clause for year filter."""
        from mcp_canada.modules.manitoba.client import fetch_surgical_wait_times

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_surgical_wait_times(year=2021)

        where = captured[0].get("where", "")
        assert "Year" in where or "2021" in where

    @pytest.mark.asyncio
    async def test_procedure_filter_applied(self):
        """fetch_surgical_wait_times builds WHERE with LIKE clause for procedure."""
        from mcp_canada.modules.manitoba.client import fetch_surgical_wait_times

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_surgical_wait_times(procedure="Cardiac surgery")

        where = captured[0].get("where", "")
        assert "Cardiac surgery" in where or "IndicatorDataArea" in where or "LIKE" in where

    @pytest.mark.asyncio
    async def test_queries_wait_times_fs_url(self):
        """fetch_surgical_wait_times calls query_feature_service with SURGICAL_WAIT_TIMES_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_surgical_wait_times
        from mcp_canada.modules.manitoba.constants import SURGICAL_WAIT_TIMES_FS_URL

        captured_urls: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_urls.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_surgical_wait_times()

        assert len(captured_urls) == 1
        assert SURGICAL_WAIT_TIMES_FS_URL in captured_urls[0] or captured_urls[0] == SURGICAL_WAIT_TIMES_FS_URL


class TestManitobaGetHealthFacilities:
    """Unit tests for fetch_health_facilities. Plan 05 fills."""

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_health_facilities returns {features, count, truncated} payload."""
        from mcp_canada.modules.manitoba.client import fetch_health_facilities
        from .conftest import SAMPLE_HEALTH_FACILITIES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_HEALTH_FACILITIES_FEATURES,
        ):
            data, cached = await fetch_health_facilities()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == len(data["features"])

    @pytest.mark.asyncio
    async def test_features_include_community_and_facility(self):
        """Health facility features include Community_Name and Facility_Name fields."""
        from mcp_canada.modules.manitoba.client import fetch_health_facilities
        from .conftest import SAMPLE_HEALTH_FACILITIES_FEATURES

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_HEALTH_FACILITIES_FEATURES,
        ):
            data, _ = await fetch_health_facilities()
        if data["features"]:
            feat = data["features"][0]
            assert "Community_Name" in feat or "Facility_Name" in feat

    @pytest.mark.asyncio
    async def test_community_filter_applied(self):
        """fetch_health_facilities builds WHERE with Community_Name filter."""
        from mcp_canada.modules.manitoba.client import fetch_health_facilities

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_health_facilities(community="Selkirk")

        where = captured[0].get("where", "")
        assert "Selkirk" in where or "Community_Name" in where

    @pytest.mark.asyncio
    async def test_emergency_only_filter_applied(self):
        """fetch_health_facilities builds WHERE clause for emergency_only=True."""
        from mcp_canada.modules.manitoba.client import fetch_health_facilities

        captured: list[dict] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured.append(kwargs)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_health_facilities(emergency_only=True)

        where = captured[0].get("where", "")
        # Should filter for facilities with emergency departments available
        assert "Emergency" in where or "Yes" in where or "1=1" not in where

    @pytest.mark.asyncio
    async def test_queries_rural_health_facilities_fs_url(self):
        """fetch_health_facilities calls query_feature_service with RURAL_HEALTH_FACILITIES_FS_URL."""
        from mcp_canada.modules.manitoba.client import fetch_health_facilities
        from mcp_canada.modules.manitoba.constants import RURAL_HEALTH_FACILITIES_FS_URL

        captured_urls: list[str] = []

        async def mock_qfs(url, layer_id, **kwargs):
            captured_urls.append(url)
            return ([], False)

        with patch(
            "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            side_effect=mock_qfs,
        ):
            await fetch_health_facilities()

        assert len(captured_urls) == 1
        assert RURAL_HEALTH_FACILITIES_FS_URL in captured_urls[0] or captured_urls[0] == RURAL_HEALTH_FACILITIES_FS_URL


class TestManitoba511:
    """Unit tests for 511 client functions (fetch_road_events, etc.). Plan 06."""

    # ------------------------------------------------------------------
    # Key-absent path: Five11NotConfigured must be raised
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_raises_five11_not_configured_when_no_key_road_events(self, monkeypatch):
        """fetch_road_events raises Five11NotConfigured when MANITOBA_511_KEY absent."""
        from mcp_canada.modules.manitoba.client import (
            fetch_road_events,
        )

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with pytest.raises(Five11NotConfigured):
            await fetch_road_events()

    @pytest.mark.asyncio
    async def test_raises_five11_not_configured_when_no_key_winter_roads(self, monkeypatch):
        """fetch_winter_road_conditions raises Five11NotConfigured when MANITOBA_511_KEY absent."""
        from mcp_canada.modules.manitoba.client import (
            fetch_winter_road_conditions,
        )

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with pytest.raises(Five11NotConfigured):
            await fetch_winter_road_conditions()

    @pytest.mark.asyncio
    async def test_raises_five11_not_configured_when_no_key_cameras(self, monkeypatch):
        """fetch_traffic_cameras raises Five11NotConfigured when MANITOBA_511_KEY absent."""
        from mcp_canada.modules.manitoba.client import (
            fetch_traffic_cameras,
        )

        monkeypatch.delenv("MANITOBA_511_KEY", raising=False)
        with pytest.raises(Five11NotConfigured):
            await fetch_traffic_cameras()

    # ------------------------------------------------------------------
    # Key-present path (mocked api_get): must return (list, bool) tuples
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_road_events_with_mocked_key(self, monkeypatch):
        """fetch_road_events(key present) returns (list_of_events, bool) tuple."""
        from mcp_canada.modules.manitoba.client import fetch_road_events
        from .conftest import SAMPLE_511_EVENTS

        monkeypatch.setenv("MANITOBA_511_KEY", "test-api-key-12345")
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=SAMPLE_511_EVENTS,
        ):
            rows, was_cached = await fetch_road_events()
        assert isinstance(rows, list)
        assert isinstance(was_cached, bool)
        assert len(rows) == 2
        assert rows[0]["Id"] == "EVT-001"

    @pytest.mark.asyncio
    async def test_winter_roads_with_mocked_key(self, monkeypatch):
        """fetch_winter_road_conditions(key present) returns (list, bool) tuple."""
        from mcp_canada.modules.manitoba.client import fetch_winter_road_conditions
        from .conftest import SAMPLE_511_WINTER_ROADS

        monkeypatch.setenv("MANITOBA_511_KEY", "test-api-key-12345")
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=SAMPLE_511_WINTER_ROADS,
        ):
            rows, was_cached = await fetch_winter_road_conditions()
        assert isinstance(rows, list)
        assert isinstance(was_cached, bool)
        assert len(rows) == 2
        assert rows[0]["AreaName"] == "Northern"

    @pytest.mark.asyncio
    async def test_cameras_with_mocked_key(self, monkeypatch):
        """fetch_traffic_cameras(key present) returns (list, bool) tuple."""
        from mcp_canada.modules.manitoba.client import fetch_traffic_cameras
        from .conftest import SAMPLE_511_CAMERAS

        monkeypatch.setenv("MANITOBA_511_KEY", "test-api-key-12345")
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=SAMPLE_511_CAMERAS,
        ):
            rows, was_cached = await fetch_traffic_cameras()
        assert isinstance(rows, list)
        assert isinstance(was_cached, bool)
        assert len(rows) == 2
        # Views array is preserved (cameras include Views sub-list)
        assert "Views" in rows[0]

    @pytest.mark.asyncio
    async def test_road_events_area_name_filter(self, monkeypatch):
        """fetch_winter_road_conditions area_name= performs client-side filtering."""
        from mcp_canada.modules.manitoba.client import fetch_winter_road_conditions
        from .conftest import SAMPLE_511_WINTER_ROADS

        monkeypatch.setenv("MANITOBA_511_KEY", "test-api-key-12345")
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=SAMPLE_511_WINTER_ROADS,
        ):
            rows, _ = await fetch_winter_road_conditions(area_name="Northern")
        # All results should match the area filter
        assert all(r.get("AreaName") == "Northern" for r in rows)

    @pytest.mark.asyncio
    async def test_511_never_calls_arcgis_hub(self, monkeypatch):
        """511 client functions never call arcgis_hub.query_feature_service."""
        from mcp_canada.modules.manitoba.client import fetch_road_events
        from .conftest import SAMPLE_511_EVENTS

        monkeypatch.setenv("MANITOBA_511_KEY", "test-api-key-12345")
        with patch(
            "mcp_canada.modules.manitoba.client.api_get",
            new_callable=AsyncMock,
            return_value=SAMPLE_511_EVENTS,
        ):
            with patch(
                "mcp_canada.modules.manitoba.client.arcgis_hub.query_feature_service",
            ) as mock_arcgis:
                await fetch_road_events()
        mock_arcgis.assert_not_called()
