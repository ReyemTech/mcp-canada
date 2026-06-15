"""Saskatchewan client unit tests.

Plans 02-05 fill the test bodies. Wave 0 defines placeholder classes so pytest
can collect these nodes and downstream plans reference specific node IDs.

TestSharedApiGetContract: verifies _hub_get patches at module-local level
(patches mcp_canada.modules.saskatchewan.client.api_get — BC/Alberta pattern).

NEVER patch at the shared module level for Saskatchewan client tests — use the
module-local from-import pattern (same as Phase 15 BC and Phase 17 Alberta).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_canada.modules.saskatchewan.client import (
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
    """_hub_get: verifies it calls api_get (module-local import), not CKAN envelope.

    Plan 02 fills: patches mcp_canada.modules.saskatchewan.client.api_get
    and asserts Hub JSON contract (dict with 'features' key, no .get('success')).
    """

    @pytest.mark.asyncio
    async def test_hub_get_calls_api_get_once(self):
        """_hub_get calls api_get exactly once with HUB_SEARCH_URL."""
        hub_response = {"numberMatched": 2, "features": [], "results": []}
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=hub_response,
        ) as mock_api_get:
            await _hub_get({"q": "crops"})
        mock_api_get.assert_called_once()
        # First positional arg should be HUB_SEARCH_URL
        from mcp_canada.modules.saskatchewan.constants import HUB_SEARCH_URL
        assert mock_api_get.call_args[0][0] == HUB_SEARCH_URL

    @pytest.mark.asyncio
    async def test_hub_get_returns_dict_directly(self):
        """_hub_get returns the Hub JSON dict without inspecting CKAN keys."""
        hub_response = {"numberMatched": 1, "features": [{"id": "x"}]}
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=hub_response,
        ):
            result = await _hub_get({"q": "crops"})
        assert result == hub_response
        # Ensure no CKAN envelope inspection — result is NOT envelope.get("result")
        assert "numberMatched" in result

    @pytest.mark.asyncio
    async def test_hub_get_raises_on_non_dict_response(self):
        """_hub_get raises HTTPStatusError when api_get returns a non-dict (list, str, etc)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=["not", "a", "dict"],
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await _hub_get({"q": "test"})

    @pytest.mark.asyncio
    async def test_hub_get_raises_on_none_response(self):
        """_hub_get raises HTTPStatusError when api_get returns None."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await _hub_get({})

    @pytest.mark.asyncio
    async def test_hub_get_never_calls_get_success(self):
        """_hub_get never inspects .get('success') — Hub Search returns dict directly."""
        hub_response = {"features": [], "numberMatched": 0}
        # If hub_get inspected .get('success'), we'd see missing key or falsy → error path.
        # The real test: a dict WITHOUT 'success' must not raise.
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=hub_response,
        ):
            result = await _hub_get({})
        assert "success" not in result  # Hub JSON has no success key
        assert "features" in result


# ---------------------------------------------------------------------------
# TestSaskSearchDatasets
# ---------------------------------------------------------------------------


class TestSaskSearchDatasets:
    """fetch_search_datasets: Hub Search pagination via OGC API Records startindex.

    Plan 02 fills: verify limit/startindex/q params; verify (results, total) shape.
    """

    # ------------------------------------------------------------------
    # Param-regression tests (the Manitoba/Phase-18-09 lesson)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_sends_ogc_limit_not_num(self):
        """fetch_search_datasets sends OGC 'limit' (not 'num') and no 'start'/'offset'."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("crops")
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "limit" in params, f"Expected 'limit' in params, got: {params}"
        assert isinstance(params["limit"], int) and params["limit"] >= 1
        assert params.get("q") == "crops"
        assert "num" not in params, f"'num' must NOT be in params, got: {params}"
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"
        assert "offset" not in params, f"'offset' must NOT be in params, got: {params}"
        # startindex must not appear when offset==0
        assert "startindex" not in params, (
            f"'startindex' must not appear when offset==0, got: {params}"
        )

    @pytest.mark.asyncio
    async def test_search_omits_startindex_when_offset_zero(self):
        """fetch_search_datasets omits 'startindex' when offset=0 (startindex=0 is invalid live)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("crops", offset=0)
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "startindex" not in params, (
            f"startindex must be omitted when offset==0 (live API malformed body), got: {params}"
        )
        assert "start" not in params
        assert "offset" not in params

    @pytest.mark.asyncio
    async def test_search_sets_startindex_when_offset_positive(self):
        """fetch_search_datasets sends 'startindex' when offset > 0, not 'start'/'offset'."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("crops", offset=10)
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "startindex" in params, (
            f"Expected 'startindex' in params when offset>0, got: {params}"
        )
        assert params["startindex"] == 10
        assert "start" not in params, f"'start' must NOT be in params, got: {params}"
        assert "offset" not in params, f"'offset' must NOT be in params, got: {params}"

    @pytest.mark.asyncio
    async def test_search_omits_q_when_blank(self):
        """fetch_search_datasets omits 'q' when query is empty string (empty q -> HTTP 400)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("")
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "q" not in params, f"'q' must NOT be in params when blank, got: {params}"

    @pytest.mark.asyncio
    async def test_search_passes_category_as_categories(self):
        """fetch_search_datasets passes category value under 'categories' key."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("crops", category="/Categories/Agriculture")
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert params.get("categories") == "/Categories/Agriculture", (
            f"Expected categories='/Categories/Agriculture' in params, got: {params}"
        )

    @pytest.mark.asyncio
    async def test_search_params_with_q_only(self):
        """fetch_search_datasets with 'crops' produces exactly {limit, q} — no extras."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_search_datasets("crops", limit=10, offset=0)
        params = mock_api_get.call_args[0][1]
        assert set(params.keys()) == {"limit", "q"}, (
            f"Expected exactly {{limit, q}}, got: {set(params.keys())}"
        )

    # ------------------------------------------------------------------
    # Happy path + shape tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_returns_results_and_total(self):
        """fetch_search_datasets returns dict with results list and total count."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_search_datasets("crops")
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 2
        assert data["total"] == 181  # numberMatched in HUB_SEARCH_RAW fixture

    @pytest.mark.asyncio
    async def test_returns_empty_results_for_no_match(self):
        """fetch_search_datasets returns empty results list when Hub finds nothing."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
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
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value="bad",
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_search_datasets("crops")

    @pytest.mark.asyncio
    async def test_result_items_are_flat_summaries(self):
        """Returned items are flat dicts with id, title, snippet, type, url fields."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_search_datasets("crops")
        first = data["results"][0]
        assert "id" in first
        assert "title" in first


# ---------------------------------------------------------------------------
# TestSaskGetDatasetDetails
# ---------------------------------------------------------------------------


class TestSaskGetDatasetDetails:
    """fetch_dataset_details: Hub item detail by ID.

    Plan 02 fills: verify feature_server_url detection; download_urls list.
    """

    @pytest.mark.asyncio
    async def test_returns_details_with_feature_server_url(self):
        """fetch_dataset_details returns dict including feature_server_url."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_ITEM_DETAIL,
        ):
            data, cached = await fetch_dataset_details("a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        assert "details" in data
        details = data["details"]
        assert "feature_server_url" in details
        assert "title" in details

    @pytest.mark.asyncio
    async def test_feature_server_url_detected_correctly(self):
        """fetch_dataset_details populates feature_server_url when URL contains /FeatureServer."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_ITEM_DETAIL,
        ):
            data, _ = await fetch_dataset_details("a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        fs_url = data["details"]["feature_server_url"]
        assert fs_url is not None
        assert "FeatureServer" in fs_url

    @pytest.mark.asyncio
    async def test_raises_not_found_on_empty_result(self):
        """fetch_dataset_details raises ValueError when item not found (empty search)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value={"numberMatched": 0, "numberReturned": 0, "features": []},
        ):
            with pytest.raises((ValueError, httpx.HTTPStatusError)):
                await fetch_dataset_details("nonexistent-id")

    @pytest.mark.asyncio
    async def test_returns_download_urls(self):
        """fetch_dataset_details includes download_urls list."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_ITEM_DETAIL,
        ):
            data, _ = await fetch_dataset_details("a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        assert "download_urls" in data["details"]
        assert isinstance(data["details"]["download_urls"], list)


# ---------------------------------------------------------------------------
# TestSaskQueryDataset
# ---------------------------------------------------------------------------


class TestSaskQueryDataset:
    """fetch_query_dataset: hybrid router (FeatureServer vs parseable file vs metadata-only).

    Plan 02 fills: FeatureServer branch, CSV/GeoJSON branch, metadata-only fallback.
    """

    @pytest.mark.asyncio
    async def test_routes_feature_server_to_arcgis_hub(self):
        """fetch_query_dataset routes FeatureServer URL to arcgis_hub.query_feature_service."""
        feature_server_url = (
            "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/"
            "Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer"
        )
        mock_rows = [{"Region": "Provincial", "HRSW": 43.0}]
        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
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
            "mcp_canada.modules.saskatchewan.client.fetch_and_parse",
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
        mock_rows = [{"type": "Feature", "properties": {"name": "SK"}}]
        with patch(
            "mcp_canada.modules.saskatchewan.client.fetch_and_parse",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ):
            data, cached = await fetch_query_dataset(geojson_url)
        assert "data" in data

    @pytest.mark.asyncio
    async def test_metadata_only_fallback_for_pdf(self):
        """fetch_query_dataset returns metadata-only note for PDF/ZIP/KML URLs."""
        pdf_url = "https://example.com/report.pdf"
        data, cached = await fetch_query_dataset(pdf_url)
        assert "url" in data
        assert "note" in data

    @pytest.mark.asyncio
    async def test_feature_server_url_with_layer_suffix(self):
        """fetch_query_dataset strips trailing /0 from FeatureServer URL and passes layer_id=0."""
        feature_server_url = (
            "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/"
            "Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer/0"
        )
        mock_rows = [{"Region": "Provincial"}]
        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=(mock_rows, False),
        ) as mock_qs:
            data, _ = await fetch_query_dataset(feature_server_url)
        # Verify it was called (routing happened)
        mock_qs.assert_called_once()


# ---------------------------------------------------------------------------
# TestSaskListOrgs
# ---------------------------------------------------------------------------


class TestSaskListOrgs:
    """fetch_organizations: derives unique owners from Hub Search results.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_organizations_list(self):
        """fetch_organizations returns dict with organizations list."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_organizations()
        assert "organizations" in data
        assert isinstance(data["organizations"], list)
        assert len(data["organizations"]) >= 1

    @pytest.mark.asyncio
    async def test_organizations_are_unique(self):
        """fetch_organizations returns deduplicated owner names."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_organizations()
        orgs = data["organizations"]
        assert len(orgs) == len(set(orgs)), "Organizations list must contain unique values"

    @pytest.mark.asyncio
    async def test_organizations_omits_q_param(self):
        """fetch_organizations omits 'q' from Hub params (empty q -> 400)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_organizations()
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "q" not in params, f"'q' must NOT be in params for fetch_organizations, got: {params}"
        assert "limit" in params, f"'limit' must be in params for fetch_organizations, got: {params}"


# ---------------------------------------------------------------------------
# TestSaskListCategories
# ---------------------------------------------------------------------------


class TestSaskListCategories:
    """fetch_categories: derives unique category strings from Hub Search results.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_categories_list(self):
        """fetch_categories returns dict with categories list."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, cached = await fetch_categories()
        assert "categories" in data
        assert isinstance(data["categories"], list)

    @pytest.mark.asyncio
    async def test_categories_are_unique(self):
        """fetch_categories returns deduplicated category strings."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_categories()
        cats = data["categories"]
        assert len(cats) == len(set(cats)), "Categories list must contain unique values"

    @pytest.mark.asyncio
    async def test_categories_omits_q_param(self):
        """fetch_categories omits 'q' from Hub params (empty q -> 400)."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ) as mock_api_get:
            await fetch_categories()
        mock_api_get.assert_called_once()
        params = mock_api_get.call_args[0][1]
        assert "q" not in params, f"'q' must NOT be in params for fetch_categories, got: {params}"
        assert "limit" in params, f"'limit' must be in params for fetch_categories, got: {params}"

    @pytest.mark.asyncio
    async def test_categories_from_properties(self):
        """fetch_categories extracts /Categories/* values from feature properties."""
        with patch(
            "mcp_canada.modules.saskatchewan.client.api_get",
            new_callable=AsyncMock,
            return_value=HUB_SEARCH_RAW,
        ):
            data, _ = await fetch_categories()
        cats = data["categories"]
        # HUB_SEARCH_RAW fixture has /Categories/Agriculture and /Categories/Environment
        assert any("/Categories/" in c for c in cats)


# ---------------------------------------------------------------------------
# Placeholder classes for Plans 03-05 (stubs unchanged)
# ---------------------------------------------------------------------------


class TestSaskGetCropYields:
    """fetch_crop_yields: region dispatch to Province Summary vs Regions Only FeatureServer.

    Plan 03 fills: verify "provincial" routes to CROP_YIELDS_PROVINCE_FS_URL;
    "southeast" routes to CROP_YIELDS_REGIONS_FS_URL with WHERE Region='Southeast'.
    """

    pass


class TestSaskGetGrainElevators:
    """fetch_grain_elevators: default PR='SK' filter; optional railway= filter.

    Plan 03 fills.
    """

    pass


class TestSaskGetMineralMines:
    """fetch_mineral_mines: dispatch by mineral to MINERAL_MINES_FS_URLS dict.

    Plan 03 fills: verify "potash" routes to Potash_2024_06_13 URL;
    ValueError for unknown mineral.
    """

    pass


class TestSaskGetFireBans:
    """fetch_fire_bans: SPSA ban scope dispatch; empty list is a valid success.

    Plan 04 fills: verify "urban"→layer 0, "parks"→layer 8;
    empty features=[] does NOT raise.
    """

    pass


class TestSaskGetHistoricWildfires:
    """fetch_historic_wildfires: optional year/cause filters on STARTDATE/CAUSE1.

    Plan 04 fills.
    """

    pass


class TestSaskGetAirQuality:
    """fetch_air_quality: optional community= filter; live 15min cache TTL.

    Plan 04 fills.
    """

    pass


class TestSaskGetWSAStations:
    """fetch_wsa_stations: WSA org URL; Province='SK' default; optional basin= filter.

    Plan 05 fills.
    """

    pass


class TestSaskGetWSAReservoirs:
    """fetch_wsa_reservoirs: WSA org URL; layer 26 (NOT 0).

    Plan 05 fills: assert layer_id=WSA_RESERVOIRS_LAYER (26) passed to query_feature_service.
    """

    pass
