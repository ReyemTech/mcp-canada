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

    @pytest.mark.asyncio
    async def test_provincial_routes_to_province_summary_fs(self):
        """region='provincial' calls query_feature_service with CROP_YIELDS_PROVINCE_FS_URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields
        from mcp_canada.modules.saskatchewan.constants import CROP_YIELDS_PROVINCE_FS_URL
        from .conftest import SAMPLE_ARCGIS_CROP_YIELDS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_CROP_YIELDS,
        ) as mock_qfs:
            data, cached = await fetch_crop_yields(region="provincial")
        mock_qfs.assert_called_once()
        call_kwargs = mock_qfs.call_args
        # First positional arg is the FS URL
        assert call_kwargs[0][0] == CROP_YIELDS_PROVINCE_FS_URL, (
            f"Expected CROP_YIELDS_PROVINCE_FS_URL, got {call_kwargs[0][0]}"
        )
        # Where should be 1=1 for provincial
        assert call_kwargs[1].get("where") == "1=1"

    @pytest.mark.asyncio
    async def test_provincial_returns_features_and_count(self):
        """fetch_crop_yields returns dict with features, count, region keys."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields
        from .conftest import SAMPLE_ARCGIS_CROP_YIELDS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_CROP_YIELDS,
        ):
            data, cached = await fetch_crop_yields(region="provincial")
        assert "features" in data
        assert "count" in data
        assert "region" in data
        assert data["region"] == "provincial"
        # Canola field must be present in returned rows
        assert any("Canola" in row for row in data["features"])

    @pytest.mark.asyncio
    async def test_southeast_routes_to_regions_only_fs(self):
        """region='southeast' calls query_feature_service with CROP_YIELDS_REGIONS_FS_URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields
        from mcp_canada.modules.saskatchewan.constants import CROP_YIELDS_REGIONS_FS_URL
        from .conftest import SAMPLE_ARCGIS_CROP_YIELDS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_CROP_YIELDS,
        ) as mock_qfs:
            data, cached = await fetch_crop_yields(region="southeast")
        mock_qfs.assert_called_once()
        call_kwargs = mock_qfs.call_args
        assert call_kwargs[0][0] == CROP_YIELDS_REGIONS_FS_URL, (
            f"Expected CROP_YIELDS_REGIONS_FS_URL, got {call_kwargs[0][0]}"
        )
        # Where clause should filter by Region='Southeast' (Title-cased)
        assert call_kwargs[1].get("where") == "Region='Southeast'"

    @pytest.mark.asyncio
    async def test_northwest_region_title_case_where_clause(self):
        """region='northwest' produces WHERE Region='Northwest' (title-cased)."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields
        from .conftest import SAMPLE_ARCGIS_CROP_YIELDS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_CROP_YIELDS,
        ) as mock_qfs:
            await fetch_crop_yields(region="northwest")
        where = mock_qfs.call_args[1].get("where")
        assert where == "Region='Northwest'", f"Expected Region='Northwest', got: {where}"

    @pytest.mark.asyncio
    async def test_unknown_region_raises_value_error(self):
        """fetch_crop_yields raises ValueError for unknown region (tool maps to INVALID_INPUT)."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
        ):
            with pytest.raises(ValueError, match="region"):
                await fetch_crop_yields(region="bogusregion")

    @pytest.mark.asyncio
    async def test_explicit_out_fields_sent(self):
        """fetch_crop_yields sends explicit out_fields including Region and Canola."""
        from mcp_canada.modules.saskatchewan.client import fetch_crop_yields
        from .conftest import SAMPLE_ARCGIS_CROP_YIELDS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_CROP_YIELDS,
        ) as mock_qfs:
            await fetch_crop_yields(region="provincial")
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        assert "Canola" in out_fields, f"Expected Canola in out_fields, got: {out_fields}"
        assert "Region" in out_fields, f"Expected Region in out_fields, got: {out_fields}"


class TestSaskGetGrainElevators:
    """fetch_grain_elevators: default PR='SK' filter; optional railway= filter.

    Plan 03 fills.
    """

    @pytest.mark.asyncio
    async def test_default_where_clause_is_sk(self):
        """fetch_grain_elevators defaults to where=PR='SK'."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ) as mock_qfs:
            data, cached = await fetch_grain_elevators()
        mock_qfs.assert_called_once()
        where = mock_qfs.call_args[1].get("where")
        assert where == "PR='SK'", f"Expected PR='SK', got: {where}"

    @pytest.mark.asyncio
    async def test_railway_filter_appends_to_where(self):
        """fetch_grain_elevators with railway='CN' produces where=\"PR='SK' AND Railway='CN'\"."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ) as mock_qfs:
            await fetch_grain_elevators(railway="CN")
        where = mock_qfs.call_args[1].get("where")
        assert where == "PR='SK' AND Railway='CN'", f"Expected CN filter, got: {where}"

    @pytest.mark.asyncio
    async def test_shortline_railway_filter(self):
        """fetch_grain_elevators with railway='SHORTLINE' appends correctly."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ) as mock_qfs:
            await fetch_grain_elevators(railway="SHORTLINE")
        where = mock_qfs.call_args[1].get("where")
        assert "SHORTLINE" in where, f"Expected SHORTLINE in where, got: {where}"

    @pytest.mark.asyncio
    async def test_uses_grain_elevators_fs_url(self):
        """fetch_grain_elevators calls query_feature_service with GRAIN_ELEVATORS_FS_URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from mcp_canada.modules.saskatchewan.constants import GRAIN_ELEVATORS_FS_URL
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ) as mock_qfs:
            await fetch_grain_elevators()
        assert mock_qfs.call_args[0][0] == GRAIN_ELEVATORS_FS_URL

    @pytest.mark.asyncio
    async def test_returns_features_and_count(self):
        """fetch_grain_elevators returns dict with features, count, truncated."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ):
            data, cached = await fetch_grain_elevators()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == 2

    @pytest.mark.asyncio
    async def test_explicit_out_fields_sent(self):
        """fetch_grain_elevators sends explicit out_fields including Station and Capacity_tonne."""
        from mcp_canada.modules.saskatchewan.client import fetch_grain_elevators
        from .conftest import SAMPLE_ARCGIS_GRAIN_ELEVATORS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_GRAIN_ELEVATORS,
        ) as mock_qfs:
            await fetch_grain_elevators()
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        assert "Station" in out_fields
        assert "Capacity_tonne" in out_fields


class TestSaskGetMineralMines:
    """fetch_mineral_mines: dispatch by mineral to MINERAL_MINES_FS_URLS dict.

    Plan 03 fills: verify "potash" routes to Potash_2024_06_13 URL;
    ValueError for unknown mineral.
    """

    @pytest.mark.asyncio
    async def test_potash_routes_to_potash_fs_url(self):
        """fetch_mineral_mines(mineral='potash') routes to Potash_2024_06_13 FS URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from mcp_canada.modules.saskatchewan.constants import MINERAL_MINES_FS_URLS
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            data, cached = await fetch_mineral_mines(mineral="potash")
        assert mock_qfs.call_args[0][0] == MINERAL_MINES_FS_URLS["potash"]

    @pytest.mark.asyncio
    async def test_uranium_routes_to_uranium_fs_url(self):
        """fetch_mineral_mines(mineral='uranium') routes to Uranium_2024_06_13 FS URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from mcp_canada.modules.saskatchewan.constants import MINERAL_MINES_FS_URLS
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            await fetch_mineral_mines(mineral="uranium")
        assert mock_qfs.call_args[0][0] == MINERAL_MINES_FS_URLS["uranium"]

    @pytest.mark.asyncio
    async def test_helium_routes_to_helium_fs_url(self):
        """fetch_mineral_mines(mineral='helium') routes to Helium_2024_12_31 FS URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from mcp_canada.modules.saskatchewan.constants import MINERAL_MINES_FS_URLS
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            await fetch_mineral_mines(mineral="helium")
        assert mock_qfs.call_args[0][0] == MINERAL_MINES_FS_URLS["helium"]

    @pytest.mark.asyncio
    async def test_coal_routes_to_coal_fs_url(self):
        """fetch_mineral_mines(mineral='coal') routes to Coal_2024_06_13 FS URL."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from mcp_canada.modules.saskatchewan.constants import MINERAL_MINES_FS_URLS
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            await fetch_mineral_mines(mineral="coal")
        assert mock_qfs.call_args[0][0] == MINERAL_MINES_FS_URLS["coal"]

    @pytest.mark.asyncio
    async def test_unknown_mineral_raises_value_error(self):
        """fetch_mineral_mines raises ValueError for unknown mineral type."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
        ):
            with pytest.raises(ValueError, match="mineral"):
                await fetch_mineral_mines(mineral="gold")

    @pytest.mark.asyncio
    async def test_returns_features_count_and_mineral(self):
        """fetch_mineral_mines returns dict with features, count, truncated, mineral."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ):
            data, cached = await fetch_mineral_mines(mineral="potash")
        assert "features" in data
        assert "count" in data
        assert "mineral" in data
        assert data["mineral"] == "potash"

    @pytest.mark.asyncio
    async def test_explicit_out_fields_sent(self):
        """fetch_mineral_mines sends explicit out_fields including Name, Company, Status."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            await fetch_mineral_mines(mineral="potash")
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        assert "Name" in out_fields
        assert "Company" in out_fields
        assert "Status" in out_fields
        assert "DateOpened" in out_fields

    @pytest.mark.asyncio
    async def test_case_insensitive_mineral_lookup(self):
        """fetch_mineral_mines handles uppercase mineral input via .lower() dispatch."""
        from mcp_canada.modules.saskatchewan.client import fetch_mineral_mines
        from mcp_canada.modules.saskatchewan.constants import MINERAL_MINES_FS_URLS
        from .conftest import SAMPLE_ARCGIS_MINERAL_MINES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_MINERAL_MINES,
        ) as mock_qfs:
            await fetch_mineral_mines(mineral="POTASH")
        assert mock_qfs.call_args[0][0] == MINERAL_MINES_FS_URLS["potash"]


class TestSaskGetFireBans:
    """fetch_fire_bans: SPSA ban scope dispatch; empty list is a valid success.

    Plan 04 fills: verify "urban"→layer 0, "parks"→layer 8;
    empty features=[] does NOT raise.
    """

    @pytest.mark.asyncio
    async def test_urban_scope_dispatches_to_layer_0(self):
        """fetch_fire_bans(ban_scope='urban') calls query_feature_service with layer_id=0."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from mcp_canada.modules.saskatchewan.constants import FIRE_BAN_FS_URL
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            data, cached = await fetch_fire_bans(ban_scope="urban")
        mock_qfs.assert_called_once()
        # First positional arg is FS URL
        assert mock_qfs.call_args[0][0] == FIRE_BAN_FS_URL, (
            f"Expected FIRE_BAN_FS_URL, got {mock_qfs.call_args[0][0]}"
        )
        # Second positional arg is layer_id
        assert mock_qfs.call_args[0][1] == 0, (
            f"Expected layer_id=0 for 'urban', got {mock_qfs.call_args[0][1]}"
        )

    @pytest.mark.asyncio
    async def test_rural_scope_dispatches_to_layer_2(self):
        """fetch_fire_bans(ban_scope='rural') calls query_feature_service with layer_id=2."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            await fetch_fire_bans(ban_scope="rural")
        assert mock_qfs.call_args[0][1] == 2, (
            f"Expected layer_id=2 for 'rural', got {mock_qfs.call_args[0][1]}"
        )

    @pytest.mark.asyncio
    async def test_provincial_scope_dispatches_to_layer_3(self):
        """fetch_fire_bans(ban_scope='provincial') calls query_feature_service with layer_id=3."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            await fetch_fire_bans(ban_scope="provincial")
        assert mock_qfs.call_args[0][1] == 3, (
            f"Expected layer_id=3 for 'provincial', got {mock_qfs.call_args[0][1]}"
        )

    @pytest.mark.asyncio
    async def test_parks_scope_dispatches_to_layer_8(self):
        """fetch_fire_bans(ban_scope='parks') calls query_feature_service with layer_id=8."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            await fetch_fire_bans(ban_scope="parks")
        assert mock_qfs.call_args[0][1] == 8, (
            f"Expected layer_id=8 for 'parks', got {mock_qfs.call_args[0][1]}"
        )

    @pytest.mark.asyncio
    async def test_empty_fire_bans_is_valid_success_not_error(self):
        """CRITICAL: empty fire bans (off-season) returns valid payload count==0, never raises.

        This mirrors Manitoba flood alerts: no active bans is a NORMAL state, not an error.
        """
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_EMPTY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_EMPTY,
        ):
            data, cached = await fetch_fire_bans(ban_scope="urban")

        # Must NOT raise — empty list is a valid payload
        assert "features" in data, "Empty fire bans must return payload with 'features' key"
        assert data["features"] == [], f"Expected empty features list, got: {data['features']}"
        assert data["count"] == 0, f"Expected count==0 for empty bans, got: {data['count']}"
        assert "scope" in data, "Payload must include 'scope' key"

    @pytest.mark.asyncio
    async def test_active_fire_bans_returns_features_and_count(self):
        """fetch_fire_bans returns dict with features, count, truncated, scope keys."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ):
            data, cached = await fetch_fire_bans(ban_scope="urban")

        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert "scope" in data
        assert data["scope"] == "urban"
        assert data["count"] == 2
        assert len(data["features"]) == 2

    @pytest.mark.asyncio
    async def test_unknown_ban_scope_raises_value_error(self):
        """fetch_fire_bans raises ValueError for unknown ban_scope (tool maps to INVALID_INPUT)."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
        ):
            with pytest.raises(ValueError, match="ban_scope"):
                await fetch_fire_bans(ban_scope="forest")

    @pytest.mark.asyncio
    async def test_fire_ban_where_clause_is_1_equals_1(self):
        """fetch_fire_bans always uses where='1=1' (no filtering — return all active bans)."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            await fetch_fire_bans(ban_scope="urban")
        where = mock_qfs.call_args[1].get("where")
        assert where == "1=1", f"Expected where='1=1', got: {where}"

    @pytest.mark.asyncio
    async def test_fire_ban_uses_spsa_not_hub_url(self):
        """fetch_fire_bans calls the SPSA FS URL (gis.saskatchewan.ca/egis), NOT the Hub org."""
        from mcp_canada.modules.saskatchewan.client import fetch_fire_bans
        from mcp_canada.modules.saskatchewan.constants import FIRE_BAN_FS_URL
        from .conftest import SAMPLE_ARCGIS_FIRE_BANS_ACTIVE

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_FIRE_BANS_ACTIVE,
        ) as mock_qfs:
            await fetch_fire_bans(ban_scope="urban")
        url = mock_qfs.call_args[0][0]
        assert "gis.saskatchewan.ca/egis" in url, (
            f"Fire ban must use SPSA server (gis.saskatchewan.ca/egis), got: {url}"
        )
        assert url == FIRE_BAN_FS_URL


class TestSaskGetHistoricWildfires:
    """fetch_historic_wildfires: optional year/cause filters on STARTDATE/CAUSE1.

    Plan 04 fills.
    """

    @pytest.mark.asyncio
    async def test_no_filters_uses_1_equals_1_where(self):
        """fetch_historic_wildfires with no filters uses where='1=1'."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            data, cached = await fetch_historic_wildfires()
        where = mock_qfs.call_args[1].get("where")
        assert where == "1=1", f"Expected where='1=1' with no filters, got: {where}"

    @pytest.mark.asyncio
    async def test_year_filter_composes_where_clause(self):
        """fetch_historic_wildfires(year=2017) produces where='YEAR=2017'."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            await fetch_historic_wildfires(year=2017)
        where = mock_qfs.call_args[1].get("where")
        assert "YEAR=2017" in where, f"Expected YEAR=2017 in where, got: {where}"

    @pytest.mark.asyncio
    async def test_cause_filter_uses_like_clause(self):
        """fetch_historic_wildfires(cause='Lightning') produces CAUSE1 LIKE '%Lightning%'."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            await fetch_historic_wildfires(cause="Lightning")
        where = mock_qfs.call_args[1].get("where")
        assert "CAUSE1 LIKE '%Lightning%'" in where, (
            f"Expected CAUSE1 LIKE clause, got: {where}"
        )

    @pytest.mark.asyncio
    async def test_year_and_cause_both_compose_correctly(self):
        """fetch_historic_wildfires(year=2017, cause='Lightning') composes year AND cause."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            await fetch_historic_wildfires(year=2017, cause="Lightning")
        where = mock_qfs.call_args[1].get("where")
        assert "YEAR=2017" in where, f"Expected YEAR=2017 in where, got: {where}"
        assert "CAUSE1 LIKE '%Lightning%'" in where, (
            f"Expected CAUSE1 LIKE in where, got: {where}"
        )
        # must be joined with AND
        assert "AND" in where, f"Expected AND conjunction in where, got: {where}"

    @pytest.mark.asyncio
    async def test_uses_wildfire_boundaries_fs_url(self):
        """fetch_historic_wildfires calls WILDFIRE_BOUNDARIES_FS_URL (primary Hub org)."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from mcp_canada.modules.saskatchewan.constants import WILDFIRE_BOUNDARIES_FS_URL
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            await fetch_historic_wildfires()
        assert mock_qfs.call_args[0][0] == WILDFIRE_BOUNDARIES_FS_URL, (
            f"Expected WILDFIRE_BOUNDARIES_FS_URL, got: {mock_qfs.call_args[0][0]}"
        )

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_historic_wildfires returns dict with features, count, truncated."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ):
            data, cached = await fetch_historic_wildfires()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == 2
        assert data["features"][0]["FIRENAME"] == "PORCUPINE LAKE FIRE"

    @pytest.mark.asyncio
    async def test_explicit_out_fields_include_key_wildfire_fields(self):
        """fetch_historic_wildfires sends out_fields including YEAR, FIRENAME, CAUSE1, HECTARES."""
        from mcp_canada.modules.saskatchewan.client import fetch_historic_wildfires
        from .conftest import SAMPLE_ARCGIS_WILDFIRES

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WILDFIRES,
        ) as mock_qfs:
            await fetch_historic_wildfires()
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        for field in ("YEAR", "FIRENAME", "CAUSE1", "HECTARES"):
            assert field in out_fields, f"Expected {field} in out_fields, got: {out_fields}"


class TestSaskGetAirQuality:
    """fetch_air_quality: optional community= filter; live 15min cache TTL.

    Plan 04 fills.
    """

    @pytest.mark.asyncio
    async def test_no_community_uses_1_equals_1_where(self):
        """fetch_air_quality with no community filter uses where='1=1'."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ) as mock_qfs:
            data, cached = await fetch_air_quality()
        where = mock_qfs.call_args[1].get("where")
        assert where == "1=1", f"Expected where='1=1' with no community, got: {where}"

    @pytest.mark.asyncio
    async def test_community_filter_composes_where_clause(self):
        """fetch_air_quality(community='Regina') produces where=\"COMMUNITY='Regina'\"."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ) as mock_qfs:
            await fetch_air_quality(community="Regina")
        where = mock_qfs.call_args[1].get("where")
        assert where == "COMMUNITY='Regina'", (
            f"Expected COMMUNITY='Regina', got: {where}"
        )

    @pytest.mark.asyncio
    async def test_uses_air_quality_fs_url(self):
        """fetch_air_quality calls AIR_QUALITY_FS_URL (primary Hub org)."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from mcp_canada.modules.saskatchewan.constants import AIR_QUALITY_FS_URL
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ) as mock_qfs:
            await fetch_air_quality()
        assert mock_qfs.call_args[0][0] == AIR_QUALITY_FS_URL, (
            f"Expected AIR_QUALITY_FS_URL, got: {mock_qfs.call_args[0][0]}"
        )

    @pytest.mark.asyncio
    async def test_returns_features_with_aqhi_field(self):
        """fetch_air_quality returns features with AQHI (weather.gc.ca URL) present."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ):
            data, cached = await fetch_air_quality()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == 2
        # AQHI field must be present
        first = data["features"][0]
        assert "AQHI" in first, f"Expected AQHI in feature, got keys: {list(first.keys())}"
        assert "weather.gc.ca" in first["AQHI"], (
            f"Expected AQHI to be a weather.gc.ca URL, got: {first['AQHI']}"
        )

    @pytest.mark.asyncio
    async def test_explicit_out_fields_include_key_air_quality_fields(self):
        """fetch_air_quality sends out_fields including COMMUNITY, PM2_5, NO2, O3, AQHI, DATETIME."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ) as mock_qfs:
            await fetch_air_quality()
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        for field in ("COMMUNITY", "PM2_5", "NO2", "O3", "AQHI", "DATETIME"):
            assert field in out_fields, f"Expected {field} in out_fields, got: {out_fields}"

    @pytest.mark.asyncio
    async def test_saskatoon_community_filter(self):
        """fetch_air_quality(community='Saskatoon') produces where=\"COMMUNITY='Saskatoon'\"."""
        from mcp_canada.modules.saskatchewan.client import fetch_air_quality
        from .conftest import SAMPLE_ARCGIS_AIR_QUALITY

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_AIR_QUALITY,
        ) as mock_qfs:
            await fetch_air_quality(community="Saskatoon")
        where = mock_qfs.call_args[1].get("where")
        assert where == "COMMUNITY='Saskatoon'", f"Expected COMMUNITY='Saskatoon', got: {where}"


class TestSaskGetWSAStations:
    """fetch_wsa_stations: WSA org URL; Province='SK' default; optional basin= filter.

    Plan 05 fills.
    """

    @pytest.mark.asyncio
    async def test_default_where_clause_is_province_sk(self):
        """fetch_wsa_stations defaults to where=\"Province='SK'\"."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            data, cached = await fetch_wsa_stations()
        mock_qfs.assert_called_once()
        where = mock_qfs.call_args[1].get("where")
        assert where == "Province='SK'", (
            f"Expected where=\"Province='SK'\", got: {where}"
        )

    @pytest.mark.asyncio
    async def test_basin_filter_appends_to_where(self):
        """fetch_wsa_stations with basin='Assiniboine' appends Major_Basin LIKE clause."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            await fetch_wsa_stations(basin="Assiniboine")
        where = mock_qfs.call_args[1].get("where")
        assert "Province='SK'" in where, f"Expected Province='SK' in where, got: {where}"
        assert "AND Major_Basin LIKE '%Assiniboine%'" in where, (
            f"Expected basin LIKE clause in where, got: {where}"
        )

    @pytest.mark.asyncio
    async def test_uses_wsa_stations_fs_url_not_hub_org(self):
        """fetch_wsa_stations calls WSA_STATIONS_FS_URL (services1 / 7MBdlVpjqbfBhQer), NOT Hub org."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from mcp_canada.modules.saskatchewan.constants import WSA_STATIONS_FS_URL
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            await fetch_wsa_stations()
        url = mock_qfs.call_args[0][0]
        assert url == WSA_STATIONS_FS_URL, (
            f"Expected WSA_STATIONS_FS_URL, got: {url}"
        )
        assert "services1.arcgis.com/7MBdlVpjqbfBhQer" in url, (
            f"Expected WSA org (7MBdlVpjqbfBhQer) in URL, got: {url}"
        )

    @pytest.mark.asyncio
    async def test_uses_layer_0(self):
        """fetch_wsa_stations calls query_feature_service with layer_id=0."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            await fetch_wsa_stations()
        layer_id = mock_qfs.call_args[0][1]
        assert layer_id == 0, f"Expected layer_id=0, got: {layer_id}"

    @pytest.mark.asyncio
    async def test_out_fields_includes_hyperlink_graph(self):
        """fetch_wsa_stations sends out_fields including HyperLink_Graph."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            await fetch_wsa_stations()
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        for field in ("Station_Number", "Major_Basin", "Station_Class", "Operated_By", "HyperLink_Graph"):
            assert field in out_fields, f"Expected {field} in out_fields, got: {out_fields}"

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_wsa_stations returns dict with features, count, truncated."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ):
            data, cached = await fetch_wsa_stations()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == 2
        # HyperLink_Graph present in returned rows
        first = data["features"][0]
        assert "HyperLink_Graph" in first, (
            f"Expected HyperLink_Graph in station row, got keys: {list(first.keys())}"
        )
        assert "wsask.ca" in first["HyperLink_Graph"], (
            f"Expected wsask.ca in HyperLink_Graph URL, got: {first['HyperLink_Graph']}"
        )

    @pytest.mark.asyncio
    async def test_no_basin_returns_all_sk_stations(self):
        """fetch_wsa_stations with no basin returns all SK stations."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_stations
        from .conftest import SAMPLE_ARCGIS_WSA_STATIONS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_STATIONS,
        ) as mock_qfs:
            data, _ = await fetch_wsa_stations(basin=None)
        where = mock_qfs.call_args[1].get("where")
        assert where == "Province='SK'", (
            f"Expected only Province='SK' when no basin, got: {where}"
        )
        assert "AND" not in where, f"Expected no AND clause when basin=None, got: {where}"


class TestSaskGetWSAReservoirs:
    """fetch_wsa_reservoirs: WSA org URL; layer 26 (NOT 0).

    Plan 05 fills: assert layer_id=WSA_RESERVOIRS_LAYER (26) passed to query_feature_service.
    """

    @pytest.mark.asyncio
    async def test_uses_wsa_reservoirs_fs_url_not_hub_org(self):
        """fetch_wsa_reservoirs calls WSA_RESERVOIRS_FS_URL (services1 / 7MBdlVpjqbfBhQer), NOT Hub org."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_reservoirs
        from mcp_canada.modules.saskatchewan.constants import WSA_RESERVOIRS_FS_URL
        from .conftest import SAMPLE_ARCGIS_WSA_RESERVOIRS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_RESERVOIRS,
        ) as mock_qfs:
            data, cached = await fetch_wsa_reservoirs()
        url = mock_qfs.call_args[0][0]
        assert url == WSA_RESERVOIRS_FS_URL, (
            f"Expected WSA_RESERVOIRS_FS_URL, got: {url}"
        )
        assert "services1.arcgis.com/7MBdlVpjqbfBhQer" in url, (
            f"Expected WSA org (7MBdlVpjqbfBhQer) in URL, got: {url}"
        )

    @pytest.mark.asyncio
    async def test_CRITICAL_uses_layer_26_not_layer_0(self):
        """CRITICAL: fetch_wsa_reservoirs calls query_feature_service with layer_id=26 (NOT 0).

        Layer 0 is empty — all reservoir data is at layer 26 (spike-confirmed 2026-06-15).
        WSA_RESERVOIRS_LAYER constant must be used; never hardcode 0.
        """
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_reservoirs
        from mcp_canada.modules.saskatchewan.constants import WSA_RESERVOIRS_LAYER
        from .conftest import SAMPLE_ARCGIS_WSA_RESERVOIRS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_RESERVOIRS,
        ) as mock_qfs:
            await fetch_wsa_reservoirs()
        layer_id = mock_qfs.call_args[0][1]
        assert layer_id == WSA_RESERVOIRS_LAYER, (
            f"CRITICAL: Expected layer_id={WSA_RESERVOIRS_LAYER} (WSA_RESERVOIRS_LAYER), "
            f"got: {layer_id}. Layer 0 is EMPTY — all reservoir data is at layer 26."
        )
        assert layer_id == 26, (
            f"CRITICAL: layer_id must be 26, got: {layer_id}"
        )

    @pytest.mark.asyncio
    async def test_where_clause_is_1_equals_1(self):
        """fetch_wsa_reservoirs uses where='1=1' (fetch all reservoirs)."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_reservoirs
        from .conftest import SAMPLE_ARCGIS_WSA_RESERVOIRS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_RESERVOIRS,
        ) as mock_qfs:
            await fetch_wsa_reservoirs()
        where = mock_qfs.call_args[1].get("where")
        assert where == "1=1", f"Expected where='1=1', got: {where}"

    @pytest.mark.asyncio
    async def test_out_fields_includes_reservoir_and_dam_name(self):
        """fetch_wsa_reservoirs sends out_fields including Reservoir_Name, Dam_Name, Water_Level_MASL."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_reservoirs
        from .conftest import SAMPLE_ARCGIS_WSA_RESERVOIRS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_RESERVOIRS,
        ) as mock_qfs:
            await fetch_wsa_reservoirs()
        out_fields = mock_qfs.call_args[1].get("out_fields", "")
        for field in ("Reservoir_Name", "Dam_Name", "Water_Level_MASL"):
            assert field in out_fields, f"Expected {field} in out_fields, got: {out_fields}"

    @pytest.mark.asyncio
    async def test_returns_features_count_truncated(self):
        """fetch_wsa_reservoirs returns dict with features, count, truncated."""
        from mcp_canada.modules.saskatchewan.client import fetch_wsa_reservoirs
        from .conftest import SAMPLE_ARCGIS_WSA_RESERVOIRS

        with patch(
            "mcp_canada.modules.saskatchewan.client.arcgis_hub.query_feature_service",
            new_callable=AsyncMock,
            return_value=SAMPLE_ARCGIS_WSA_RESERVOIRS,
        ):
            data, cached = await fetch_wsa_reservoirs()
        assert "features" in data
        assert "count" in data
        assert "truncated" in data
        assert data["count"] == 2
        first = data["features"][0]
        assert "Reservoir_Name" in first, (
            f"Expected Reservoir_Name in reservoir row, got: {list(first.keys())}"
        )
        assert first["Reservoir_Name"] == "ADMIRAL RESERVOIR"
        assert "Dam_Name" in first, f"Expected Dam_Name in reservoir row"
