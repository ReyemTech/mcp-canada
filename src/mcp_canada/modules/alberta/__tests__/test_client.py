"""alberta module client tests. Bodies added by Plans 02-07.

Class stubs exist so pytest collection succeeds from Wave 0. Downstream plans
add test methods to the matching class.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest


class TestSharedApiGetContract:
    """Post-15-05 contract regression guard.

    shared/http.py:api_get returns PARSED JSON (dict or list) — NEVER an
    httpx.Response. _api_get must handle that raw-dict contract without
    calling .json() or .raise_for_status().

    The patch target is `mcp_canada.modules.alberta.client.api_get` — the
    module-local binding of the shared helper. This is the same pattern BC
    uses (test_client.py::TestSharedApiGetContract). A raw dict sent to code
    that still expects a Response will fail with AttributeError — which is
    exactly the Phase 15-05 regression this suite guards against.
    """

    @pytest.mark.asyncio
    async def test_ckan_api_get_returns_parsed_dict(self):
        """_api_get handles a parsed dict directly (no .json() / .raise_for_status())."""
        payload = {"success": True, "result": {"count": 5}}
        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=payload),
        ):
            from mcp_canada.modules.alberta.client import _api_get

            result = await _api_get("package_search")
        assert result == {"count": 5}

    @pytest.mark.asyncio
    async def test_ckan_success_false_raises(self):
        """Envelope success=False raises httpx.HTTPStatusError (not silent ignore)."""
        failure = {"success": False, "error": {"message": "boom"}}
        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=failure),
        ):
            from mcp_canada.modules.alberta.client import _api_get

            with pytest.raises(httpx.HTTPStatusError):
                await _api_get("package_search")

    @pytest.mark.asyncio
    async def test_ckan_success_true_returns_result(self):
        """Envelope success=True returns the unwrapped result dict."""
        payload = {"success": True, "result": {"count": 42, "results": [{"id": "x"}]}}
        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=payload),
        ):
            from mcp_canada.modules.alberta.client import _api_get

            result = await _api_get("package_search", {"q": "fire"})
        assert result["count"] == 42
        assert result["results"] == [{"id": "x"}]


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


class TestAlbertaSearchDatasets:  # Plan 02
    """fetch_search_datasets — CKAN package_search with fq= filters."""

    @pytest.mark.asyncio
    async def test_returns_shaped_results(self, sample_ckan_package_search_response):
        from mcp_canada.modules.alberta.client import fetch_search_datasets

        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_search_response),
        ):
            payload, cached = await fetch_search_datasets(q="wildfire")
        assert isinstance(payload, dict)
        assert payload["count"] == 33269
        assert isinstance(payload["results"], list)
        assert len(payload["results"]) == 2
        first = payload["results"][0].model_dump()
        # Flat summary with organization_slug extracted from nested org
        assert first["id"] == "ab-dataset-1"
        assert first["name"] == "wildfire-data"
        assert first["title"] == "Alberta Wildfire Data"
        assert first["organization_slug"] == "forestry-and-parks"
        assert first["num_resources"] == 2
        # formats deduped from resources[].format
        assert set(first["formats"]) == {"ESRI REST", "CSV"}

    @pytest.mark.asyncio
    async def test_format_filter(self, sample_ckan_package_search_response):
        """format='CSV' appends fq=res_format:CSV."""
        from mcp_canada.modules.alberta.client import fetch_search_datasets

        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.alberta.client.api_get", new=mock):
            await fetch_search_datasets(q="wildfire", format="CSV")
        call = mock.call_args
        params = call[0][1] if len(call[0]) > 1 else call.kwargs.get("params", {})
        fq = params.get("fq", "")
        assert "res_format:CSV" in fq

    @pytest.mark.asyncio
    async def test_organization_filter(self, sample_ckan_package_search_response):
        """organization=X appends fq=organization:X."""
        from mcp_canada.modules.alberta.client import fetch_search_datasets

        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.alberta.client.api_get", new=mock):
            await fetch_search_datasets(
                q="fire", organization="forestry-and-parks"
            )
        call = mock.call_args
        params = call[0][1] if len(call[0]) > 1 else call.kwargs.get("params", {})
        fq = params.get("fq", "")
        assert "organization:forestry-and-parks" in fq

    @pytest.mark.asyncio
    async def test_pagination_passthrough(self, sample_ckan_package_search_response):
        """rows and start are forwarded to api_get params."""
        from mcp_canada.modules.alberta.client import fetch_search_datasets

        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.alberta.client.api_get", new=mock):
            await fetch_search_datasets(q="fire", rows=5, start=10)
        call = mock.call_args
        params = call[0][1] if len(call[0]) > 1 else call.kwargs.get("params", {})
        assert params.get("rows") == 5
        assert params.get("start") == 10

    @pytest.mark.asyncio
    async def test_rows_capped_at_100(self, sample_ckan_package_search_response):
        """CKAN hard cap: rows > 100 is clamped to 100."""
        from mcp_canada.modules.alberta.client import fetch_search_datasets

        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.alberta.client.api_get", new=mock):
            await fetch_search_datasets(q="fire", rows=5000)
        call = mock.call_args
        params = call[0][1] if len(call[0]) > 1 else call.kwargs.get("params", {})
        assert params.get("rows") == 100


class TestAlbertaGetDatasetDetails:  # Plan 02
    """fetch_dataset_details — CKAN package_show + _flatten_alberta_extras."""

    @pytest.mark.asyncio
    async def test_flattens_50_plus_extras(self, sample_ckan_package_show_response):
        """55 extras in fixture flatten to a compact dict, no `extras` list leaks through."""
        from mcp_canada.modules.alberta.client import fetch_dataset_details

        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_show_response),
        ):
            details, _ = await fetch_dataset_details("wildfire-data")
        data = details.model_dump()
        # Core fields retained
        assert data["id"] == "wildfire-data"
        assert data["name"] == "wildfire-data"
        assert data["title"] == "Alberta Wildfire Data"
        assert data["organization_slug"] == "forestry-and-parks"
        # Resources survived flattening
        assert len(data["resources"]) == 2
        assert data["resources"][0]["format"] == "ESRI REST"

    @pytest.mark.asyncio
    async def test_keeps_useful_extras(self):
        """isopen / language / frequencyofupdate / creator are preserved in output."""
        from mcp_canada.modules.alberta.client import fetch_dataset_details

        pkg_with_useful_extras = {
            "success": True,
            "result": {
                "id": "x",
                "name": "x",
                "title": "X",
                "notes": "note",
                "organization": {"name": "org", "title": "Org"},
                "license_id": "open-gov-licence-alberta",
                "extras": [
                    {"key": "isopen", "value": "true"},
                    {"key": "language", "value": "English"},
                    {"key": "frequencyofupdate", "value": "monthly"},
                    {"key": "creator", "value": "Alberta Agriculture"},
                    {"key": "identifier-AGDEX-number", "value": "636"},
                    {"key": "identifier-ISBN-pdf", "value": "isbn"},
                    {"key": "audience", "value": "public"},
                ],
                "resources": [],
            },
        }
        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=pkg_with_useful_extras),
        ):
            details, _ = await fetch_dataset_details("x")
        data = details.model_dump()
        assert data["isopen"] is True
        assert data["language"] == "English"
        assert data["frequencyofupdate"] == "monthly"
        assert data["creator"] == "Alberta Agriculture"


class TestAlbertaQueryDataset:  # Plan 02
    """fetch_query_dataset — hybrid router (ESRI REST vs CSV vs metadata-only)."""

    @pytest.mark.asyncio
    async def test_routes_esri_rest_to_feature_server(
        self, sample_ckan_package_show_response
    ):
        """resources[0] is ESRI REST /FeatureServer/0 → arcgis_hub.query_feature_service."""
        from mcp_canada.modules.alberta import client as ab_client

        fake_rows = [{"FIRE_NUMBER": "ABC-1"}, {"FIRE_NUMBER": "ABC-2"}]
        with (
            patch(
                "mcp_canada.modules.alberta.client.api_get",
                new=AsyncMock(return_value=sample_ckan_package_show_response),
            ),
            patch.object(
                ab_client.arcgis_hub,
                "query_feature_service",
                new=AsyncMock(return_value=(fake_rows, False)),
            ) as mock_qfs,
        ):
            payload, _ = await ab_client.fetch_query_dataset(
                "wildfire-data", resource_index=0
            )
        mock_qfs.assert_called_once()
        # service_url should be the FeatureServer base (without trailing /0)
        call_args = mock_qfs.call_args
        service_url = call_args.args[0] if call_args.args else call_args.kwargs["service_url"]
        layer_id = call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs["layer_id"]
        assert service_url.endswith("/FeatureServer")
        assert layer_id == 0
        assert payload["data"] == fake_rows

    @pytest.mark.asyncio
    async def test_routes_csv_to_fetch_and_parse(self):
        """resources[1] format=CSV → fetch_and_parse."""
        from mcp_canada.modules.alberta import client as ab_client

        pkg = {
            "success": True,
            "result": {
                "id": "x",
                "name": "x",
                "title": "X",
                "notes": None,
                "organization": {"name": "org"},
                "extras": [],
                "resources": [
                    {
                        "id": "r1",
                        "name": "csv",
                        "format": "CSV",
                        "url": "https://example.alberta.ca/data.csv",
                    }
                ],
            },
        }
        fake_rows = [{"a": 1}, {"a": 2}, {"a": 3}]
        with (
            patch(
                "mcp_canada.modules.alberta.client.api_get",
                new=AsyncMock(return_value=pkg),
            ),
            patch(
                "mcp_canada.modules.alberta.client.fetch_and_parse",
                new=AsyncMock(return_value=(fake_rows, False)),
            ) as mock_fap,
        ):
            payload, _ = await ab_client.fetch_query_dataset("x", resource_index=0)
        mock_fap.assert_called_once()
        assert payload["data"] == fake_rows

    @pytest.mark.asyncio
    async def test_pdf_returns_metadata_only(self):
        """PDF resource returns metadata-only response (no download attempt)."""
        from mcp_canada.modules.alberta import client as ab_client

        pkg = {
            "success": True,
            "result": {
                "id": "x",
                "name": "x",
                "title": "X",
                "notes": None,
                "organization": {"name": "org"},
                "extras": [],
                "resources": [
                    {
                        "id": "r1",
                        "name": "report",
                        "format": "PDF",
                        "url": "https://example.alberta.ca/report.pdf",
                    }
                ],
            },
        }
        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=pkg),
        ):
            payload, _ = await ab_client.fetch_query_dataset("x", resource_index=0)
        assert payload.get("format") == "PDF"
        assert payload.get("url", "").endswith(".pdf")
        assert "note" in payload

    @pytest.mark.asyncio
    async def test_prefers_featureserver_over_mapserver(self):
        """Pitfall 12: when both FeatureServer and MapServer present, FS wins."""
        from mcp_canada.modules.alberta import client as ab_client

        pkg = {
            "success": True,
            "result": {
                "id": "x",
                "name": "x",
                "title": "X",
                "notes": None,
                "organization": {"name": "org"},
                "extras": [],
                "resources": [
                    {
                        "id": "r1",
                        "name": "MapServer",
                        "format": "ESRI REST",
                        "url": "https://services.arcgis.com/xxx/MapServer/0",
                    },
                    {
                        "id": "r2",
                        "name": "FeatureServer",
                        "format": "ESRI REST",
                        "url": "https://services.arcgis.com/xxx/FeatureServer/0",
                    },
                ],
            },
        }
        with (
            patch(
                "mcp_canada.modules.alberta.client.api_get",
                new=AsyncMock(return_value=pkg),
            ),
            patch.object(
                ab_client.arcgis_hub,
                "query_feature_service",
                new=AsyncMock(return_value=([], False)),
            ) as mock_qfs,
        ):
            await ab_client.fetch_query_dataset("x", resource_index=0)
        call_args = mock_qfs.call_args
        service_url = (
            call_args.args[0] if call_args.args else call_args.kwargs["service_url"]
        )
        assert "/FeatureServer" in service_url
        assert "/MapServer" not in service_url


class TestAlbertaListOrganizations:  # Plan 02
    """fetch_organizations — CKAN organization_list?all_fields=true."""

    @pytest.mark.asyncio
    async def test_returns_org_list_with_count(self, sample_ckan_organization_list):
        from mcp_canada.modules.alberta.client import fetch_organizations

        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=sample_ckan_organization_list),
        ):
            orgs, _ = await fetch_organizations()
        assert len(orgs) == 5
        first = orgs[0].model_dump()
        assert first["name"] == "forestry-and-parks"
        assert first["title"] == "Forestry and Parks"
        assert first["package_count"] == 240


class TestAlbertaListCategories:  # Plan 02
    """fetch_format_categories — package_search?facet.field=res_format (Pitfall 1)."""

    @pytest.mark.asyncio
    async def test_uses_format_facet_not_group_list(
        self, sample_ckan_format_facet
    ):
        """Pitfall 1: must call package_search with facet.field, NOT group_list."""
        from mcp_canada.modules.alberta.client import fetch_format_categories

        mock = AsyncMock(return_value=sample_ckan_format_facet)
        with patch("mcp_canada.modules.alberta.client.api_get", new=mock):
            await fetch_format_categories()
        call = mock.call_args
        url = call[0][0] if call[0] else call.kwargs["url"]
        params = call[0][1] if len(call[0]) > 1 else call.kwargs.get("params", {})
        assert url.endswith("package_search")
        # facet.field present (CKAN JSON-array-as-string form)
        assert "facet.field" in params
        assert "res_format" in str(params["facet.field"])
        assert params.get("rows") == 0

    @pytest.mark.asyncio
    async def test_returns_format_buckets_sorted_desc(
        self, sample_ckan_format_facet
    ):
        from mcp_canada.modules.alberta.client import fetch_format_categories

        with patch(
            "mcp_canada.modules.alberta.client.api_get",
            new=AsyncMock(return_value=sample_ckan_format_facet),
        ):
            cats, _ = await fetch_format_categories()
        assert len(cats) == 6
        # Highest count first
        assert cats[0].format == "PDF"
        assert cats[0].count == 28763
        # Sorted descending
        counts = [c.count for c in cats]
        assert counts == sorted(counts, reverse=True)


# ---------------------------------------------------------------------------
# AER tools — Plan 03
# ---------------------------------------------------------------------------


class TestAlbertaWellLicencesToday:  # Plan 03
    pass


class TestAlbertaWellLicencesArchive:  # Plan 03
    pass


class TestAlbertaPipelineStatistics:  # Plan 03
    pass


class TestAlbertaProductionVolumes:  # Plan 03
    pass


# ---------------------------------------------------------------------------
# Wildfire tools — Plan 04
# ---------------------------------------------------------------------------


class TestAlbertaActiveFires:  # Plan 04
    pass


class TestAlbertaFirePerimeters:  # Plan 04
    pass


class TestAlbertaFireBans:  # Plan 04
    pass


class TestAlbertaFireControlOrders:  # Plan 04
    pass


# ---------------------------------------------------------------------------
# Health tools — Plan 05
# ---------------------------------------------------------------------------


class TestAlbertaHospitals:  # Plan 05
    pass


class TestAlbertaAhsZones:  # Plan 05
    pass


class TestAlbertaHealthFacilities:  # Plan 05
    pass


# ---------------------------------------------------------------------------
# Transport / 511 tools — Plan 06
# ---------------------------------------------------------------------------


class TestAlbertaRoadEvents:  # Plan 06
    pass


class TestAlbertaWinterRoadConditions:  # Plan 06
    pass


class TestAlbertaTrafficCameras:  # Plan 06
    pass


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks tools — Plan 07
# ---------------------------------------------------------------------------


class TestAlbertaAirQuality:  # Plan 07
    pass


class TestAlbertaWaterAdvisories:  # Plan 07
    pass


class TestAlbertaCropProduction:  # Plan 07
    pass


class TestAlbertaPopulationEstimates:  # Plan 07
    pass


class TestAlbertaProvincialParks:  # Plan 07
    pass
