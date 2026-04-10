"""Unit tests for british_columbia client functions.

Covers CKAN search/show/org/tag and the queryable_via_wfs derivation logic.
All HTTP calls are patched at the client module namespace.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_canada.modules.british_columbia.client import (
    _compute_queryable_via_wfs,
    fetch_dataset_details,
    fetch_organizations,
    fetch_search_datasets,
    fetch_tags,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_http_response(json_data: dict, status_code: int = 200):
    """Build a mock httpx.Response-like object."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# TestFetchSearchDatasets
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    """Tests for fetch_search_datasets (CKAN package_search)."""

    @pytest.mark.asyncio
    async def test_returns_shaped_summaries(self, sample_ckan_package_search_response):
        """fetch_search_datasets returns list of flat summary dicts."""
        mock_resp = _make_http_response(sample_ckan_package_search_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            results, was_cached = await fetch_search_datasets(q="wildfire")
        assert isinstance(results, list)
        assert len(results) == 2
        # Check required summary fields
        for r in results:
            assert "id" in r
            assert "name" in r
            assert "title" in r
            assert "notes" in r
            assert "organization" in r
            assert "metadata_modified" in r

    @pytest.mark.asyncio
    async def test_passes_rows_and_start_pagination_params(self, sample_ckan_package_search_response):
        """fetch_search_datasets forwards rows and start to api_get."""
        mock_resp = _make_http_response(sample_ckan_package_search_response)
        mock_api_get = AsyncMock(return_value=mock_resp)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=mock_api_get):
            await fetch_search_datasets(q="test", rows=5, start=10)
        call_kwargs = mock_api_get.call_args
        # params is second positional arg (url, params, ...)
        params = call_kwargs[0][1] if call_kwargs[0] else call_kwargs[1].get("params", {})
        assert params.get("rows") == 5
        assert params.get("start") == 10

    @pytest.mark.asyncio
    async def test_passes_fq_filter_when_provided(self, sample_ckan_package_search_response):
        """fetch_search_datasets includes fq in CKAN params when provided."""
        mock_resp = _make_http_response(sample_ckan_package_search_response)
        mock_api_get = AsyncMock(return_value=mock_resp)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=mock_api_get):
            await fetch_search_datasets(q="fire", fq="organization:bc-wildfire-service")
        call_kwargs = mock_api_get.call_args
        params = call_kwargs[0][1] if call_kwargs[0] else call_kwargs[1].get("params", {})
        assert params.get("fq") == "organization:bc-wildfire-service"

    @pytest.mark.asyncio
    async def test_second_call_is_cached(self, sample_ckan_package_search_response, monkeypatch):
        """Second fetch_search_datasets call uses cache (was_cached=True)."""
        # We override the autouse fixture to simulate cache hit on second call
        call_count = 0

        async def fake_cached_fetch_with_hit(key, ttl, fetcher):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return (await fetcher(), False)
            return (await fetcher(), True)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch_with_hit,
        )
        mock_resp = _make_http_response(sample_ckan_package_search_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            _, first_cached = await fetch_search_datasets(q="fire")
            _, second_cached = await fetch_search_datasets(q="fire")
        assert first_cached is False
        assert second_cached is True

    @pytest.mark.asyncio
    async def test_rate_limited_by_bc_ckan(self, sample_ckan_package_search_response, monkeypatch):
        """fetch_search_datasets calls get_limiter with bc_ckan and rate=10.0."""
        from mcp_canada.modules.british_columbia.constants import RATE_GROUP_CKAN, RATE_LIMIT_CKAN

        captured = {}
        mock_limiter = MagicMock()
        mock_limiter.acquire = AsyncMock()

        def fake_get_limiter(source, rate):
            captured["source"] = source
            captured["rate"] = rate
            return mock_limiter

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.get_limiter",
            fake_get_limiter,
        )
        mock_resp = _make_http_response(sample_ckan_package_search_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            await fetch_search_datasets(q="fire")
        assert captured["source"] == RATE_GROUP_CKAN
        assert captured["rate"] == RATE_LIMIT_CKAN


# ---------------------------------------------------------------------------
# TestFetchDatasetDetails
# ---------------------------------------------------------------------------


class TestFetchDatasetDetails:
    """Tests for fetch_dataset_details (CKAN package_show + queryable_via_wfs derivation)."""

    @pytest.mark.asyncio
    async def test_returns_dataset_with_resources(self, sample_ckan_package_show_wfs_response):
        """fetch_dataset_details returns dict with resources list."""
        mock_resp = _make_http_response(sample_ckan_package_show_wfs_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, _ = await fetch_dataset_details("pkg-fire-001")
        assert "resources" in result
        assert isinstance(result["resources"], list)

    @pytest.mark.asyncio
    async def test_computes_queryable_via_wfs_true_when_bcgw_geographic_resource(
        self, sample_ckan_package_show_wfs_response
    ):
        """WFS dataset with bc geographic warehouse storage gets queryable_via_wfs=True."""
        mock_resp = _make_http_response(sample_ckan_package_show_wfs_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, _ = await fetch_dataset_details("pkg-fire-001")
        assert result["queryable_via_wfs"] is True

    @pytest.mark.asyncio
    async def test_computes_queryable_via_wfs_false_when_file_only(
        self, sample_ckan_package_show_file_response
    ):
        """File-only dataset gets queryable_via_wfs=False."""
        mock_resp = _make_http_response(sample_ckan_package_show_file_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, _ = await fetch_dataset_details("pkg-fire-002")
        assert result["queryable_via_wfs"] is False

    @pytest.mark.asyncio
    async def test_surfaces_object_name_from_first_queryable_resource(
        self, sample_ckan_package_show_wfs_response
    ):
        """fetch_dataset_details surfaces object_name from the first WFS-queryable resource."""
        mock_resp = _make_http_response(sample_ckan_package_show_wfs_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, _ = await fetch_dataset_details("pkg-fire-001")
        assert result["object_name"] == "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"

    @pytest.mark.asyncio
    async def test_object_name_is_none_when_no_queryable_resource(
        self, sample_ckan_package_show_file_response
    ):
        """File-only dataset has object_name=None."""
        mock_resp = _make_http_response(sample_ckan_package_show_file_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, _ = await fetch_dataset_details("pkg-fire-002")
        assert result["object_name"] is None

    @pytest.mark.asyncio
    async def test_raises_not_found_for_missing_package(self):
        """fetch_dataset_details raises httpx.HTTPStatusError on 404."""
        import httpx

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_resp
        )
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_dataset_details("nonexistent-package")

    @pytest.mark.asyncio
    async def test_caches_per_package_id(self, sample_ckan_package_show_wfs_response, monkeypatch):
        """Second call for same package_id uses cache."""
        call_count = 0

        async def fake_cached_fetch_with_hit(key, ttl, fetcher):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return (await fetcher(), False)
            return (await fetcher(), True)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch_with_hit,
        )
        mock_resp = _make_http_response(sample_ckan_package_show_wfs_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            _, first_cached = await fetch_dataset_details("pkg-fire-001")
            _, second_cached = await fetch_dataset_details("pkg-fire-001")
        assert first_cached is False
        assert second_cached is True


# ---------------------------------------------------------------------------
# TestFetchOrganizations
# ---------------------------------------------------------------------------


class TestFetchOrganizations:
    """Tests for fetch_organizations (CKAN organization_list)."""

    @pytest.mark.asyncio
    async def test_returns_list_of_org_dicts(self, sample_ckan_organization_list_response):
        """fetch_organizations returns list of organization dicts."""
        mock_resp = _make_http_response(sample_ckan_organization_list_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, was_cached = await fetch_organizations()
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_cached_24h(self, sample_ckan_organization_list_response, monkeypatch):
        """fetch_organizations uses CACHE_TTL_META (86400s) TTL."""
        from mcp_canada.modules.british_columbia.constants import CACHE_TTL_META

        captured_ttl = {}

        async def fake_cached_fetch_capture(key, ttl, fetcher):
            captured_ttl["ttl"] = ttl
            return (await fetcher(), False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch_capture,
        )
        mock_resp = _make_http_response(sample_ckan_organization_list_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            await fetch_organizations()
        assert captured_ttl["ttl"] == CACHE_TTL_META


# ---------------------------------------------------------------------------
# TestFetchTags
# ---------------------------------------------------------------------------


class TestFetchTags:
    """Tests for fetch_tags (CKAN tag_list)."""

    @pytest.mark.asyncio
    async def test_returns_list_of_tag_strings(self, sample_ckan_tag_list_response):
        """fetch_tags returns a list of tag name strings."""
        mock_resp = _make_http_response(sample_ckan_tag_list_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            result, was_cached = await fetch_tags()
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)
        assert "wildfire" in result

    @pytest.mark.asyncio
    async def test_cached_24h(self, sample_ckan_tag_list_response, monkeypatch):
        """fetch_tags uses CACHE_TTL_META (86400s) TTL."""
        from mcp_canada.modules.british_columbia.constants import CACHE_TTL_META

        captured_ttl = {}

        async def fake_cached_fetch_capture(key, ttl, fetcher):
            captured_ttl["ttl"] = ttl
            return (await fetcher(), False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch_capture,
        )
        mock_resp = _make_http_response(sample_ckan_tag_list_response)
        with patch("mcp_canada.modules.british_columbia.client.api_get", new=AsyncMock(return_value=mock_resp)):
            await fetch_tags()
        assert captured_ttl["ttl"] == CACHE_TTL_META


# ---------------------------------------------------------------------------
# TestQueryableViaWfsDetection
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# TestWfsFetchShared
# ---------------------------------------------------------------------------


class TestWfsFetchShared:
    """Tests for _wfs_fetch — caching strategy, rate limiting, and WfsError propagation."""

    @pytest.mark.asyncio
    async def test_wfs_fetch_uses_wfs_base_url(self, monkeypatch):
        """_wfs_fetch calls wfs_page_all with WFS_BASE_URL as base_url."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch
        from mcp_canada.modules.british_columbia.constants import ACTIVE_FIRES_LAYER, WFS_BASE_URL

        captured = {}

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            captured["base_url"] = base_url
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch(ACTIVE_FIRES_LAYER)
        assert captured["base_url"] == WFS_BASE_URL

    @pytest.mark.asyncio
    async def test_wfs_fetch_passes_layer_to_type_name(self, monkeypatch):
        """_wfs_fetch forwards the layer string as type_name to wfs_page_all."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        captured = {}

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            captured["type_name"] = type_name
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW")
        assert captured["type_name"] == "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW"

    @pytest.mark.asyncio
    async def test_wfs_fetch_forwards_cql_filter(self, monkeypatch):
        """_wfs_fetch passes cql parameter as cql_filter to wfs_page_all."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        captured = {}

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            captured["cql_filter"] = kwargs.get("cql_filter")
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("SOME_LAYER", cql="FIRE_YEAR=2023")
        assert captured["cql_filter"] == "FIRE_YEAR=2023"

    @pytest.mark.asyncio
    async def test_wfs_fetch_respects_max_records(self, monkeypatch):
        """_wfs_fetch passes max_records to wfs_page_all."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        captured = {}

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            captured["max_records"] = kwargs.get("max_records")
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("SOME_LAYER", max_records=100)
        assert captured["max_records"] == 100

    @pytest.mark.asyncio
    async def test_wfs_fetch_forwards_include_geometry(self, monkeypatch):
        """_wfs_fetch passes include_geometry to wfs_page_all."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        captured = {}

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            captured["include_geometry"] = kwargs.get("include_geometry")
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("SOME_LAYER", include_geometry=True)
        assert captured["include_geometry"] is True

    @pytest.mark.asyncio
    async def test_wfs_fetch_cache_key_incorporates_layer_cql_max_records_include_geometry(
        self, monkeypatch
    ):
        """_wfs_fetch cache key includes layer, cql, max_records, include_geometry."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        captured_key = {}

        async def fake_cached_fetch(key, ttl, fetcher):
            captured_key["key"] = key
            return (await fetcher(), False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch,
        )

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("MY_LAYER", cql="X=1", max_records=50, include_geometry=True)
        key = captured_key["key"]
        assert "MY_LAYER" in key
        assert "X=1" in key
        assert "50" in key
        assert "True" in key

    @pytest.mark.asyncio
    async def test_wfs_fetch_uses_active_ttl_for_active_fires_layer(self, monkeypatch):
        """_wfs_fetch uses CACHE_TTL_ACTIVE for ACTIVE_FIRES_LAYER."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch
        from mcp_canada.modules.british_columbia.constants import (
            ACTIVE_FIRES_LAYER,
            CACHE_TTL_ACTIVE,
        )

        captured_ttl = {}

        async def fake_cached_fetch(key, ttl, fetcher):
            captured_ttl["ttl"] = ttl
            return (await fetcher(), False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch,
        )

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch(ACTIVE_FIRES_LAYER)
        assert captured_ttl["ttl"] == CACHE_TTL_ACTIVE

    @pytest.mark.asyncio
    async def test_wfs_fetch_uses_static_ttl_for_other_layers(self, monkeypatch):
        """_wfs_fetch uses CACHE_TTL_STATIC for all non-active-fires layers."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch
        from mcp_canada.modules.british_columbia.constants import CACHE_TTL_STATIC

        captured_ttl = {}

        async def fake_cached_fetch(key, ttl, fetcher):
            captured_ttl["ttl"] = ttl
            return (await fetcher(), False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.cached_fetch",
            fake_cached_fetch,
        )

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW")
        assert captured_ttl["ttl"] == CACHE_TTL_STATIC

    @pytest.mark.asyncio
    async def test_wfs_fetch_rate_limited_bc_wfs_5hz(self, monkeypatch):
        """_wfs_fetch calls get_limiter with bc_wfs and rate=5.0."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch
        from mcp_canada.modules.british_columbia.constants import RATE_GROUP_WFS, RATE_LIMIT_WFS
        from unittest.mock import AsyncMock, MagicMock

        captured = {}
        mock_limiter = MagicMock()
        mock_limiter.acquire = AsyncMock()

        def fake_get_limiter(source, rate):
            captured["source"] = source
            captured["rate"] = rate
            return mock_limiter

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.get_limiter",
            fake_get_limiter,
        )

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            return ([], False)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        await _wfs_fetch("SOME_LAYER")
        assert captured["source"] == RATE_GROUP_WFS
        assert captured["rate"] == RATE_LIMIT_WFS

    @pytest.mark.asyncio
    async def test_wfs_fetch_wraps_wfs_error(self, monkeypatch):
        """_wfs_fetch lets WfsError from wfs_page_all propagate (not caught)."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch
        from mcp_canada.shared.ogc import WfsError

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            raise WfsError("InvalidParameterValue", "Feature type unknown")

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        with pytest.raises(WfsError) as exc_info:
            await _wfs_fetch("BAD_LAYER")
        assert exc_info.value.code == "InvalidParameterValue"

    @pytest.mark.asyncio
    async def test_wfs_fetch_returns_features_and_truncated(self, monkeypatch):
        """_wfs_fetch returns ((features, truncated), was_cached)."""
        from mcp_canada.modules.british_columbia.client import _wfs_fetch

        sample_features = [{"FIRE_NUMBER": "C00001"}]

        async def fake_wfs_page_all(base_url, type_name, **kwargs):
            return (sample_features, True)

        monkeypatch.setattr(
            "mcp_canada.modules.british_columbia.client.wfs_page_all",
            fake_wfs_page_all,
        )
        result, was_cached = await _wfs_fetch("SOME_LAYER")
        features, truncated = result
        assert features == sample_features
        assert truncated is True
        assert was_cached is False


class TestQueryableViaWfsDetection:
    """Unit tests for _compute_queryable_via_wfs helper (synchronous pure logic)."""

    def test_returns_true_for_bcgw_geographic_with_object_name(self):
        """Returns (True, object_name) for a BCGW geographic resource."""
        resources = [
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "bc geographic warehouse",
                "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP",
            }
        ]
        queryable, object_name = _compute_queryable_via_wfs(resources)
        assert queryable is True
        assert object_name == "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP"

    def test_returns_false_when_bcdc_type_is_webservice(self):
        """bcdc_type=webservice (WMS/KML) does not qualify as WFS-queryable."""
        resources = [
            {
                "bcdc_type": "webservice",
                "resource_storage_location": "bc geographic warehouse",
                "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.SOME_LAYER",
            }
        ]
        queryable, object_name = _compute_queryable_via_wfs(resources)
        assert queryable is False
        assert object_name is None

    def test_returns_false_when_storage_location_is_pub_data_gov_bc_ca(self):
        """pub.data.gov.bc.ca storage = file download, not WFS queryable."""
        resources = [
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "pub.data.gov.bc.ca",
                "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.SOME_LAYER",
            }
        ]
        queryable, object_name = _compute_queryable_via_wfs(resources)
        assert queryable is False
        assert object_name is None

    def test_returns_false_when_storage_location_is_esri_arcgis_online(self):
        """esri arcgis online storage = ArcGIS REST endpoint, not WFS queryable."""
        resources = [
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "esri arcgis online",
                "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.SOME_LAYER",
            }
        ]
        queryable, object_name = _compute_queryable_via_wfs(resources)
        assert queryable is False
        assert object_name is None

    def test_returns_false_when_object_name_is_empty_string_or_missing(self):
        """Empty string or missing object_name does not qualify for WFS routing."""
        resources_empty = [
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "bc geographic warehouse",
                "object_name": "",
            }
        ]
        queryable, _ = _compute_queryable_via_wfs(resources_empty)
        assert queryable is False

        resources_missing = [
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "bc geographic warehouse",
            }
        ]
        queryable2, _ = _compute_queryable_via_wfs(resources_missing)
        assert queryable2 is False

    def test_returns_true_with_multiple_resources_if_any_one_matches(self):
        """Returns (True, object_name) if any resource in the list qualifies."""
        resources = [
            {
                "bcdc_type": "document",
                "resource_storage_location": "pub.data.gov.bc.ca",
                "object_name": None,
            },
            {
                "bcdc_type": "geographic",
                "resource_storage_location": "bc geographic warehouse",
                "object_name": "WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW",
            },
        ]
        queryable, object_name = _compute_queryable_via_wfs(resources)
        assert queryable is True
        assert object_name == "WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW"
