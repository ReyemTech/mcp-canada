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
    """fetch_well_licences_today — AER ST1 daily TXT (WELLS{day}.TXT)."""

    @pytest.mark.asyncio
    async def test_today_parses_fixed_width(self, sample_aer_st1_text):
        """Parses ST1 fixed-width TXT → list of dicts with snake_case keys."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_response = AsyncMock()
        mock_response.text = sample_aer_st1_text
        mock_response.raise_for_status = lambda: None

        class _FakeClient:
            def __init__(self, *a, **kw):
                self._kwargs = kw

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def get(self, url, **kw):
                return mock_response

        with patch.object(ab_client.httpx, "AsyncClient", _FakeClient):
            rows, cached = await ab_client.fetch_well_licences_today()

        assert isinstance(rows, list)
        assert len(rows) == 3
        # Snake-case keys only, strings (or None) for values
        first = rows[0]
        assert "licence_number" in first
        assert first["licence_number"] == "0467890"
        # Either operator or well_name should carry the Tourmaline text
        text_values = " ".join(str(v or "") for v in first.values()).upper()
        assert "TOURMALINE" in text_values

    @pytest.mark.asyncio
    async def test_today_handles_303_redirect(self, sample_aer_st1_text):
        """httpx.AsyncClient is constructed with follow_redirects=True."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_response = AsyncMock()
        mock_response.text = sample_aer_st1_text
        mock_response.raise_for_status = lambda: None

        captured_kwargs: dict = {}

        class _FakeClient:
            def __init__(self, *a, **kw):
                captured_kwargs.update(kw)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def get(self, url, **kw):
                return mock_response

        with patch.object(ab_client.httpx, "AsyncClient", _FakeClient):
            await ab_client.fetch_well_licences_today()

        assert captured_kwargs.get("follow_redirects") is True

    @pytest.mark.asyncio
    async def test_today_uses_correct_day_url(self, sample_aer_st1_text, monkeypatch):
        """URL contains the day-of-week abbreviation matching today's weekday."""
        import datetime as _dt

        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import DAY_ABBR

        # Freeze "today" to a known Wednesday (2026-04-15 is a Wednesday per ISO)
        class _FrozenDate(_dt.date):
            @classmethod
            def today(cls):
                return cls(2026, 4, 15)  # Wednesday

        monkeypatch.setattr(ab_client.datetime, "date", _FrozenDate)

        captured_url: dict = {}
        mock_response = AsyncMock()
        mock_response.text = sample_aer_st1_text
        mock_response.raise_for_status = lambda: None

        class _FakeClient:
            def __init__(self, *a, **kw):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def get(self, url, **kw):
                captured_url["url"] = url
                return mock_response

        with patch.object(ab_client.httpx, "AsyncClient", _FakeClient):
            await ab_client.fetch_well_licences_today()

        expected_day = DAY_ABBR[2]  # weekday=2 -> WED
        assert expected_day == "WED"
        assert f"WELLS{expected_day}.TXT" in captured_url["url"]


class TestAlbertaWellLicencesArchive:  # Plan 03
    """fetch_well_licences_archive — discovery-only metadata (no fetch)."""

    @pytest.mark.asyncio
    async def test_archive_returns_metadata_only(self):
        """Returns dict with url/year/month/note — does NOT call fetch_and_parse."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_fap = AsyncMock(return_value=([], False))
        with patch.object(ab_client, "fetch_and_parse", mock_fap):
            payload, _ = await ab_client.fetch_well_licences_archive(2026, 3)

        mock_fap.assert_not_called()
        assert isinstance(payload, dict)
        assert payload["year"] == 2026
        assert payload["month"] == 3
        assert "url" in payload
        assert "dwll2026-03.zip" in payload["url"]
        assert "note" in payload


class TestAlbertaPipelineStatistics:  # Plan 03
    """fetch_pipeline_statistics — AER ST39 annual XLS via fetch_and_parse."""

    @pytest.mark.asyncio
    async def test_pipeline_statistics_uses_correct_url(
        self, sample_aer_st39_rows
    ):
        """Passes ST39-{year}.xls URL to fetch_and_parse."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_fap = AsyncMock(return_value=(sample_aer_st39_rows, False))
        with patch.object(ab_client, "fetch_and_parse", mock_fap):
            rows, _ = await ab_client.fetch_pipeline_statistics(2024)

        call = mock_fap.call_args
        url = call.args[0] if call.args else call.kwargs["url"]
        assert url.endswith("ST39-2024.xls")
        assert rows == sample_aer_st39_rows


class TestAlbertaProductionVolumes:  # Plan 03
    """fetch_production_volumes — AER ST3 monthly XLSX (7 products)."""

    @pytest.mark.asyncio
    async def test_production_volumes_valid_product(self, sample_aer_st3_xlsx_rows):
        """Valid product='Gas' → fetches Gas_current.xlsx, returns rows."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_fap = AsyncMock(return_value=(sample_aer_st3_xlsx_rows, False))
        with patch.object(ab_client, "fetch_and_parse", mock_fap):
            rows, _ = await ab_client.fetch_production_volumes("Gas")

        call = mock_fap.call_args
        url = call.args[0] if call.args else call.kwargs["url"]
        assert url.endswith("Gas_current.xlsx")
        assert rows == sample_aer_st3_xlsx_rows

    @pytest.mark.asyncio
    async def test_production_volumes_invalid_product_raises(self):
        """Invalid product='Bitumen' → ValueError with valid-product hint (Pitfall 8)."""
        from mcp_canada.modules.alberta import client as ab_client

        with pytest.raises(ValueError) as exc_info:
            await ab_client.fetch_production_volumes("Bitumen")
        msg = str(exc_info.value)
        assert "Bitumen" in msg or "invalid" in msg.lower()
        # Valid products list should be surfaced in the error message
        for product in ("Butane", "Gas", "Oil"):
            assert product in msg


# ---------------------------------------------------------------------------
# Wildfire tools — Plan 04
# ---------------------------------------------------------------------------


class TestAlbertaActiveFires:  # Plan 04
    """fetch_active_fires — WMBappServices Active_Wildfires_Dashboard_view layer 0."""

    @pytest.mark.asyncio
    async def test_calls_correct_featureserver(self, sample_arcgis_query_geojson):
        """service_url must be ACTIVE_WILDFIRES_FS_URL and layer_id == 0."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import ACTIVE_WILDFIRES_FS_URL

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_active_fires()
        call = mock_qfs.call_args
        service_url = call.args[0] if call.args else call.kwargs["service_url"]
        layer_id = call.args[1] if len(call.args) > 1 else call.kwargs["layer_id"]
        assert service_url == ACTIVE_WILDFIRES_FS_URL
        assert layer_id == 0

    @pytest.mark.asyncio
    async def test_status_filter(self, sample_arcgis_query_geojson):
        """status='Out of Control' passes where=\"FIRE_STATUS='Out of Control'\"."""
        from mcp_canada.modules.alberta import client as ab_client

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_active_fires(status="Out of Control")
        kwargs = mock_qfs.call_args.kwargs
        assert kwargs.get("where") == "FIRE_STATUS='Out of Control'"

    @pytest.mark.asyncio
    async def test_no_status_no_where_clause(self, sample_arcgis_query_geojson):
        """status=None → where=None passed through."""
        from mcp_canada.modules.alberta import client as ab_client

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_active_fires()
        kwargs = mock_qfs.call_args.kwargs
        assert kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_truncated_flag_propagates(self, sample_arcgis_query_geojson):
        """When query_feature_service reports truncated=True, result dict carries it."""
        from mcp_canada.modules.alberta import client as ab_client

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, True))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            payload, _ = await ab_client.fetch_active_fires()
        assert payload["truncated"] is True
        assert payload["count"] == len(features)
        assert payload["features"] == features


class TestAlbertaFirePerimeters:  # Plan 04
    """fetch_fire_perimeters — active vs extinguished dispatcher."""

    @pytest.mark.asyncio
    async def test_active_dispatch(self, sample_arcgis_query_geojson):
        """status='active' uses ACTIVE_FIRE_PERIMETERS_FS_URL."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import ACTIVE_FIRE_PERIMETERS_FS_URL

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_fire_perimeters(status="active")
        call = mock_qfs.call_args
        service_url = call.args[0] if call.args else call.kwargs["service_url"]
        assert service_url == ACTIVE_FIRE_PERIMETERS_FS_URL

    @pytest.mark.asyncio
    async def test_extinguished_dispatch(self, sample_arcgis_query_geojson):
        """status='extinguished' uses EXTINGUISHED_PERIMETERS_FS_URL."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import EXTINGUISHED_PERIMETERS_FS_URL

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_fire_perimeters(status="extinguished")
        call = mock_qfs.call_args
        service_url = call.args[0] if call.args else call.kwargs["service_url"]
        assert service_url == EXTINGUISHED_PERIMETERS_FS_URL

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        """status='bogus' raises ValueError (dispatcher guard)."""
        from mcp_canada.modules.alberta import client as ab_client

        with pytest.raises(ValueError):
            await ab_client.fetch_fire_perimeters(status="bogus")  # type: ignore[arg-type]


class TestAlbertaFireBans:  # Plan 04
    """fetch_fire_bans — WMBappServices alberta_fire_ban_system FeatureServer."""

    @pytest.mark.asyncio
    async def test_calls_ban_system_featureserver(self, sample_arcgis_query_geojson):
        """service_url must be FIRE_BAN_SYSTEM_FS_URL and layer_id == 0."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import FIRE_BAN_SYSTEM_FS_URL

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            payload, _ = await ab_client.fetch_fire_bans()
        call = mock_qfs.call_args
        service_url = call.args[0] if call.args else call.kwargs["service_url"]
        layer_id = call.args[1] if len(call.args) > 1 else call.kwargs["layer_id"]
        assert service_url == FIRE_BAN_SYSTEM_FS_URL
        assert layer_id == 0
        assert payload["count"] == len(features)


class TestAlbertaFireControlOrders:  # Plan 04
    """fetch_fire_control_orders — category dispatcher over 3 URLs."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "category,expected_const_name",
        [
            ("fire_control", "FIRE_CONTROL_ORDERS_FS_URL"),
            ("ohv_restriction", "OHV_RESTRICTION_FS_URL"),
            ("forest_area", "FOREST_AREA_FS_URL"),
        ],
    )
    async def test_dispatches_by_category(
        self, sample_arcgis_query_geojson, category, expected_const_name
    ):
        """category dispatch: fire_control / ohv_restriction / forest_area each use its own URL."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta import constants as ab_const

        expected_url = getattr(ab_const, expected_const_name)
        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_fire_control_orders(category=category)  # type: ignore[arg-type]
        call = mock_qfs.call_args
        service_url = call.args[0] if call.args else call.kwargs["service_url"]
        assert service_url == expected_url

    @pytest.mark.asyncio
    async def test_forest_area_uses_static_ttl(self, sample_arcgis_query_geojson):
        """category='forest_area' passes CACHE_TTL_STATIC to cached_fetch."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import CACHE_TTL_STATIC

        features = sample_arcgis_query_geojson["features"]
        mock_qfs = AsyncMock(return_value=(features, False))

        captured_ttl: dict[str, int] = {}

        async def _capture_cached_fetch(key, ttl, fetcher):
            captured_ttl["ttl"] = ttl
            return (await fetcher(), False)

        with (
            patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs),
            patch(
                "mcp_canada.modules.alberta.client.cached_fetch",
                new=_capture_cached_fetch,
            ),
        ):
            await ab_client.fetch_fire_control_orders(category="forest_area")
        assert captured_ttl.get("ttl") == CACHE_TTL_STATIC

    @pytest.mark.asyncio
    async def test_invalid_category_raises(self):
        """category='bogus' raises ValueError (dispatcher guard)."""
        from mcp_canada.modules.alberta import client as ab_client

        with pytest.raises(ValueError):
            await ab_client.fetch_fire_control_orders(category="bogus")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Health tools — Plan 05
# ---------------------------------------------------------------------------


class TestAlbertaHospitals:  # Plan 05
    """fetch_hospitals — AHSGIS AHS_Hospitals FeatureServer (101 hospitals)."""

    @pytest.mark.asyncio
    async def test_calls_correct_featureserver(self):
        """fetch_hospitals targets AHS_HOSPITALS_FS_URL layer 0."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import AHS_HOSPITALS_FS_URL

        mock_qfs = AsyncMock(return_value=([], False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_hospitals()
        call_args = mock_qfs.call_args
        url_arg = (
            call_args.args[0] if call_args.args else call_args.kwargs["service_url"]
        )
        layer_arg = (
            call_args.args[1]
            if len(call_args.args) > 1
            else call_args.kwargs["layer_id"]
        )
        assert url_arg == AHS_HOSPITALS_FS_URL
        assert layer_arg == 0

    @pytest.mark.asyncio
    async def test_zone_filter_applied(self):
        """zone='Calgary' filters features whose Location contains 'calgary' (case-insensitive)."""
        from mcp_canada.modules.alberta import client as ab_client

        fake_features = [
            {"Location": "Calgary South Health Campus", "Hospital_N": "Calgary South", "IP": 1, "ED": 1},
            {"Location": "Edmonton General", "Hospital_N": "Edmonton General", "IP": 1, "ED": 0},
            {"Location": "South Health Centre Calgary", "Hospital_N": "South Health", "IP": 0, "ED": 1},
            {"Location": "Foothills Medical Centre", "Hospital_N": "Foothills", "IP": 1, "ED": 1},
        ]
        with patch.object(
            ab_client.arcgis_hub,
            "query_feature_service",
            new=AsyncMock(return_value=(fake_features, False)),
        ):
            payload, _ = await ab_client.fetch_hospitals(zone="Calgary")
        locations = [
            (f.get("Location", "") or "").lower() for f in payload["features"]
        ]
        # At least the 2 Calgary entries survive the substring match
        assert sum("calgary" in loc for loc in locations) >= 2
        # Non-Calgary entries filtered out
        assert not any("edmonton general" == loc for loc in locations)
        # Filtered count matches the feature list length
        assert payload["count"] == len(payload["features"])

    @pytest.mark.asyncio
    async def test_ip_ed_flags_preserved(self):
        """Hospital IP/ED capability flags survive the fetch."""
        from mcp_canada.modules.alberta import client as ab_client

        fake = [
            {"Location": "Foothills", "Hospital_N": "Foothills Medical Centre", "IP": 1, "ED": 0},
        ]
        with patch.object(
            ab_client.arcgis_hub,
            "query_feature_service",
            new=AsyncMock(return_value=(fake, False)),
        ):
            payload, _ = await ab_client.fetch_hospitals()
        assert payload["features"][0]["IP"] == 1
        assert payload["features"][0]["ED"] == 0


class TestAlbertaAhsZones:  # Plan 05
    """fetch_ahs_zones — 5 AHS zones with POP2006/2011/2016 normalized to snake_case."""

    @pytest.mark.asyncio
    async def test_returns_5_zones(self):
        """Happy path: 5 zone features flow through with population field snake-cased."""
        from mcp_canada.modules.alberta import client as ab_client

        fake = [
            {"Zone_Name": "South", "Zone_ID": "Z1", "POP2006": 300_000, "POP2011": 320_000, "POP2016": 350_000},
            {"Zone_Name": "Calgary", "Zone_ID": "Z2", "POP2006": 1_200_000, "POP2011": 1_400_000, "POP2016": 1_500_000},
            {"Zone_Name": "Central", "Zone_ID": "Z3", "POP2006": 450_000, "POP2011": 470_000, "POP2016": 490_000},
            {"Zone_Name": "Edmonton", "Zone_ID": "Z4", "POP2006": 1_050_000, "POP2011": 1_200_000, "POP2016": 1_350_000},
            {"Zone_Name": "North", "Zone_ID": "Z5", "POP2006": 420_000, "POP2011": 450_000, "POP2016": 480_000},
        ]
        with patch.object(
            ab_client.arcgis_hub,
            "query_feature_service",
            new=AsyncMock(return_value=(fake, False)),
        ):
            payload, _ = await ab_client.fetch_ahs_zones()
        assert payload["count"] == 5
        names = {f["zone_name"] for f in payload["features"]}
        assert names == {"South", "Calgary", "Central", "Edmonton", "North"}
        for f in payload["features"]:
            assert "pop_2016" in f

    @pytest.mark.asyncio
    async def test_population_field_normalization(self):
        """POP2016=1500000 → pop_2016=1500000 in output."""
        from mcp_canada.modules.alberta import client as ab_client

        fake = [
            {"Zone_Name": "Calgary", "Zone_ID": "Z2", "POP2006": 1_200_000, "POP2011": 1_400_000, "POP2016": 1_500_000},
        ]
        with patch.object(
            ab_client.arcgis_hub,
            "query_feature_service",
            new=AsyncMock(return_value=(fake, False)),
        ):
            payload, _ = await ab_client.fetch_ahs_zones()
        f = payload["features"][0]
        assert f["pop_2006"] == 1_200_000
        assert f["pop_2011"] == 1_400_000
        assert f["pop_2016"] == 1_500_000
        assert f["zone_id"] == "Z2"


class TestAlbertaHealthFacilities:  # Plan 05
    """fetch_health_facilities — dispatch by facility_type (ems | pcn_clinic)."""

    @pytest.mark.asyncio
    async def test_ems_dispatch(self):
        """facility_type='ems' hits AHS_EMS_FS_URL."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import AHS_EMS_FS_URL

        mock_qfs = AsyncMock(return_value=([], False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_health_facilities(facility_type="ems")
        call_args = mock_qfs.call_args
        url_arg = (
            call_args.args[0] if call_args.args else call_args.kwargs["service_url"]
        )
        assert url_arg == AHS_EMS_FS_URL

    @pytest.mark.asyncio
    async def test_pcn_dispatch(self):
        """facility_type='pcn_clinic' hits PCN_CLINICS_FS_URL."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import PCN_CLINICS_FS_URL

        mock_qfs = AsyncMock(return_value=([], False))
        with patch.object(ab_client.arcgis_hub, "query_feature_service", new=mock_qfs):
            await ab_client.fetch_health_facilities(facility_type="pcn_clinic")
        call_args = mock_qfs.call_args
        url_arg = (
            call_args.args[0] if call_args.args else call_args.kwargs["service_url"]
        )
        assert url_arg == PCN_CLINICS_FS_URL

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        """facility_type='bogus' raises ValueError (client-layer contract)."""
        from mcp_canada.modules.alberta import client as ab_client

        with pytest.raises(ValueError):
            await ab_client.fetch_health_facilities(facility_type="bogus")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Transport / 511 tools — Plan 06
# ---------------------------------------------------------------------------


class TestAlbertaRoadEvents:  # Plan 06
    """fetch_road_events — 511 Alberta v2 /event (Pitfall 6: raw JSON list, not CKAN envelope)."""

    @pytest.mark.asyncio
    async def test_calls_event_endpoint(self, sample_511_event_list):
        """_511_get('event') is called (NOT _api_get — Pitfall 6)."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_get = AsyncMock(return_value=sample_511_event_list)
        with patch.object(ab_client, "_511_get", new=mock_get):
            payload, _ = await ab_client.fetch_road_events()
        assert mock_get.call_args.args[0] == "event"
        assert payload["count"] == 3
        assert len(payload["events"]) == 3

    @pytest.mark.asyncio
    async def test_event_type_filter(self, sample_511_event_list):
        """event_type='Closure' filters to rows whose EventType contains 'closure' (case-insensitive)."""
        from mcp_canada.modules.alberta import client as ab_client

        with patch.object(
            ab_client,
            "_511_get",
            new=AsyncMock(return_value=sample_511_event_list),
        ):
            payload, _ = await ab_client.fetch_road_events(event_type="Closure")
        assert payload["count"] == 1
        assert payload["events"][0]["EventType"] == "closure"

    @pytest.mark.asyncio
    async def test_no_filter_returns_all(self, sample_511_event_list):
        """event_type=None returns every event without filtering."""
        from mcp_canada.modules.alberta import client as ab_client

        with patch.object(
            ab_client,
            "_511_get",
            new=AsyncMock(return_value=sample_511_event_list),
        ):
            payload, _ = await ab_client.fetch_road_events(event_type=None)
        assert payload["count"] == 3
        assert {e["EventType"] for e in payload["events"]} == {
            "closure",
            "construction",
            "incident",
        }

    @pytest.mark.asyncio
    async def test_uses_live_ttl_and_511_rate_limit(self, sample_511_event_list):
        """cached_fetch ttl is CACHE_TTL_LIVE; get_limiter is called with RATE_GROUP_511."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import (
            CACHE_TTL_LIVE,
            RATE_GROUP_511,
            RATE_LIMIT_511,
        )

        captured_ttls: list[int] = []

        async def _capture_ttl(key, ttl, fetcher):
            captured_ttls.append(ttl)
            return (await fetcher(), False)

        limiter_calls: list[tuple[str, float]] = []

        def _capture_limiter(source, rate):
            limiter_calls.append((source, rate))
            mock_limiter = AsyncMock()
            mock_limiter.acquire = AsyncMock()
            return mock_limiter

        with (
            patch.object(ab_client, "cached_fetch", new=_capture_ttl),
            patch.object(ab_client, "get_limiter", new=_capture_limiter),
            patch.object(
                ab_client,
                "_511_get",
                new=AsyncMock(return_value=sample_511_event_list),
            ),
        ):
            await ab_client.fetch_road_events()
        assert CACHE_TTL_LIVE in captured_ttls
        assert (RATE_GROUP_511, RATE_LIMIT_511) in limiter_calls


class TestAlbertaWinterRoadConditions:  # Plan 06
    """fetch_winter_road_conditions — 511 /winterroads."""

    @pytest.mark.asyncio
    async def test_calls_winterroads_endpoint(self, sample_511_winter_roads):
        """_511_get('winterroads') is called (NOT _api_get — Pitfall 6)."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_get = AsyncMock(return_value=sample_511_winter_roads)
        with patch.object(ab_client, "_511_get", new=mock_get):
            payload, _ = await ab_client.fetch_winter_road_conditions()
        assert mock_get.call_args.args[0] == "winterroads"
        assert payload["count"] == 2
        assert len(payload["conditions"]) == 2

    @pytest.mark.asyncio
    async def test_area_name_filter(self):
        """area_name='Calgary' matches AreaName substring case-insensitively."""
        from mcp_canada.modules.alberta import client as ab_client

        rows = [
            {"ID": "wr-1", "AreaName": "Calgary Region", "RoadwayName": "Hwy 2"},
            {"ID": "wr-2", "AreaName": "Edmonton", "RoadwayName": "Hwy 16"},
            {"ID": "wr-3", "AreaName": "calgary south", "RoadwayName": "Hwy 22X"},
        ]
        with patch.object(
            ab_client, "_511_get", new=AsyncMock(return_value=rows)
        ):
            payload, _ = await ab_client.fetch_winter_road_conditions(
                area_name="Calgary"
            )
        assert payload["count"] == 2
        assert all(
            "calgary" in (c.get("AreaName", "") or "").lower()
            for c in payload["conditions"]
        )

    @pytest.mark.asyncio
    async def test_uses_live_ttl(self, sample_511_winter_roads):
        """Winter road conditions use CACHE_TTL_LIVE (refreshed every 5 min)."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import CACHE_TTL_LIVE

        captured_ttls: list[int] = []

        async def _capture_ttl(key, ttl, fetcher):
            captured_ttls.append(ttl)
            return (await fetcher(), False)

        with (
            patch.object(ab_client, "cached_fetch", new=_capture_ttl),
            patch.object(
                ab_client,
                "_511_get",
                new=AsyncMock(return_value=sample_511_winter_roads),
            ),
        ):
            await ab_client.fetch_winter_road_conditions()
        assert CACHE_TTL_LIVE in captured_ttls


class TestAlbertaTrafficCameras:  # Plan 06
    """fetch_traffic_cameras — 511 /cameras."""

    @pytest.mark.asyncio
    async def test_calls_cameras_endpoint(self, sample_511_cameras):
        """_511_get('cameras') is called (NOT _api_get — Pitfall 6)."""
        from mcp_canada.modules.alberta import client as ab_client

        mock_get = AsyncMock(return_value=sample_511_cameras)
        with patch.object(ab_client, "_511_get", new=mock_get):
            payload, _ = await ab_client.fetch_traffic_cameras()
        assert mock_get.call_args.args[0] == "cameras"
        assert payload["count"] == 2
        assert len(payload["cameras"]) == 2

    @pytest.mark.asyncio
    async def test_views_array_preserved(self, sample_511_cameras):
        """Views array with Url/Direction dicts flows through unmodified."""
        from mcp_canada.modules.alberta import client as ab_client

        with patch.object(
            ab_client,
            "_511_get",
            new=AsyncMock(return_value=sample_511_cameras),
        ):
            payload, _ = await ab_client.fetch_traffic_cameras()
        cam0 = payload["cameras"][0]
        assert isinstance(cam0["Views"], list)
        assert cam0["Views"][0]["Url"].startswith("https://511.alberta.ca/")

    @pytest.mark.asyncio
    async def test_uses_monthly_ttl(self, sample_511_cameras):
        """Cameras cached 24h (CACHE_TTL_MONTHLY) — locations stable."""
        from mcp_canada.modules.alberta import client as ab_client
        from mcp_canada.modules.alberta.constants import CACHE_TTL_MONTHLY

        captured_ttls: list[int] = []

        async def _capture_ttl(key, ttl, fetcher):
            captured_ttls.append(ttl)
            return (await fetcher(), False)

        with (
            patch.object(ab_client, "cached_fetch", new=_capture_ttl),
            patch.object(
                ab_client,
                "_511_get",
                new=AsyncMock(return_value=sample_511_cameras),
            ),
        ):
            await ab_client.fetch_traffic_cameras()
        assert CACHE_TTL_MONTHLY in captured_ttls


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
