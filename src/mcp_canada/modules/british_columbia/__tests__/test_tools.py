"""Unit tests for british_columbia @tool functions.

Covers the 5 CKAN discovery tools (Plan 02) and placeholders for 15 curated
WFS tools (Plan 03). Patches at the tools-module namespace.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_result(result) -> dict:
    """Normalise tool return to dict (tools return dict directly)."""
    if isinstance(result, str):
        return json.loads(result)
    return result


def _wfs_details(queryable: bool = True) -> dict:
    """Return a fake fetch_dataset_details result."""
    if queryable:
        return {
            "id": "pkg-fire-001",
            "name": "bc-historical-fire-perimeters",
            "title": "BC Historical Fire Perimeters",
            "notes": "Sample notes.",
            "organization": "bc-wildfire-service",
            "resources": [
                {
                    "id": "res-001",
                    "name": "Fire Perimeters WFS",
                    "format": "wfs",
                    "url": "https://openmaps.gov.bc.ca/geo/ows",
                    "bcdc_type": "geographic",
                    "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
                    "resource_storage_location": "bc geographic warehouse",
                    "resource_type": "data",
                }
            ],
            "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP",
            "queryable_via_wfs": True,
            "projection": "epsg4326",
            "tags": ["wildfire", "fire"],
            "metadata_modified": "2026-01-15T10:00:00",
        }
    else:
        return {
            "id": "pkg-fire-002",
            "name": "bc-fire-report",
            "title": "BC Fire Report Dataset",
            "notes": "CSV download.",
            "organization": "bc-wildfire-service",
            "resources": [
                {
                    "id": "res-002",
                    "name": "Fire Report CSV",
                    "format": "csv",
                    "url": "https://example.com/bc-fire-report.csv",
                    "bcdc_type": "document",
                    "object_name": None,
                    "resource_storage_location": "pub.data.gov.bc.ca",
                    "resource_type": "data",
                }
            ],
            "object_name": None,
            "queryable_via_wfs": False,
            "projection": None,
            "tags": ["wildfire"],
            "metadata_modified": "2026-01-15T10:00:00",
        }


# ---------------------------------------------------------------------------
# Plan 02 — 5 CKAN Discovery Tools
# ---------------------------------------------------------------------------


class TestBcSearchDatasets:
    """Tests for bc_search_datasets (CKAN package_search tool)."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """bc_search_datasets returns _meta.source.api == 'bc-data-catalogue'."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        fake_data = [{"id": "pkg-1", "title": "Test Dataset"}]
        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(fake_data, False)),
        ):
            result = await bc_search_datasets(q="wildfire")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-data-catalogue"
        assert result["_meta"]["lang"] == "en"

    @pytest.mark.asyncio
    async def test_passes_q_to_client(self):
        """bc_search_datasets passes q parameter to fetch_search_datasets."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        mock_fetch = AsyncMock(return_value=([], False))
        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_search_datasets",
            new=mock_fetch,
        ):
            await bc_search_datasets(q="forestry")
        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args
        assert call_kwargs[1].get("q") == "forestry" or call_kwargs[0][0] == "forestry"

    @pytest.mark.asyncio
    async def test_supports_fq_organization(self):
        """bc_search_datasets builds fq from organization parameter."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        mock_fetch = AsyncMock(return_value=([], False))
        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_search_datasets",
            new=mock_fetch,
        ):
            await bc_search_datasets(q="fire", organization="bc-wildfire-service")
        call_kwargs = mock_fetch.call_args
        # fq should contain the organization slug
        fq_arg = call_kwargs[1].get("fq") or (call_kwargs[0][3] if len(call_kwargs[0]) > 3 else None)
        assert fq_arg is not None
        assert "bc-wildfire-service" in fq_arg

    @pytest.mark.asyncio
    async def test_propagates_lang_fr(self):
        """bc_search_datasets forwards lang=fr to the response envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_search_datasets",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await bc_search_datasets(q="incendies", lang="fr")
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_invalid_input_when_q_missing_or_empty(self):
        """bc_search_datasets returns INVALID_INPUT error when q is empty."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        result = await bc_search_datasets(q="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    def test_keywords_min_8(self):
        """bc_search_datasets docstring has at least 8 keywords on the Keywords: line."""
        from mcp_canada.modules.british_columbia.tools import bc_search_datasets

        doc = bc_search_datasets.__doc__ or ""
        assert "Keywords:" in doc
        kw_line = next(line for line in doc.splitlines() if "Keywords:" in line)
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


class TestBcGetDatasetDetails:
    """Tests for bc_get_dataset_details (CKAN package_show + queryable_via_wfs)."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_api_bc_data_catalogue(self):
        """bc_get_dataset_details returns _meta.source.api == 'bc-data-catalogue'."""
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
        ):
            result = await bc_get_dataset_details(package_id="pkg-fire-001")
        assert result["_meta"]["source"]["api"] == "bc-data-catalogue"

    @pytest.mark.asyncio
    async def test_surfaces_object_name_at_top_level(self):
        """bc_get_dataset_details surfaces object_name in data for WFS-queryable dataset."""
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
        ):
            result = await bc_get_dataset_details(package_id="pkg-fire-001")
        assert "data" in result
        assert isinstance(result["data"]["object_name"], str)

    @pytest.mark.asyncio
    async def test_surfaces_queryable_via_wfs_flag(self):
        """bc_get_dataset_details data includes queryable_via_wfs=True for WFS datasets."""
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
        ):
            result = await bc_get_dataset_details(package_id="pkg-fire-001")
        assert result["data"]["queryable_via_wfs"] is True

    @pytest.mark.asyncio
    async def test_returns_not_found_for_missing_id(self):
        """bc_get_dataset_details returns NOT_FOUND error for missing package."""
        import httpx
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        exc = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_resp)

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
            new=AsyncMock(side_effect=exc),
        ):
            result = await bc_get_dataset_details(package_id="nonexistent")
        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_propagates_lang_fr(self):
        """bc_get_dataset_details forwards lang=fr to the response envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(_wfs_details(), False)),
        ):
            result = await bc_get_dataset_details(package_id="pkg-1", lang="fr")
        assert result["_meta"]["lang"] == "fr"

    def test_keywords_min_8(self):
        """bc_get_dataset_details docstring has at least 8 keywords."""
        from mcp_canada.modules.british_columbia.tools import bc_get_dataset_details

        doc = bc_get_dataset_details.__doc__ or ""
        assert "Keywords:" in doc
        kw_line = next(line for line in doc.splitlines() if "Keywords:" in line)
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


class TestBcQueryFeatures:
    """Tests for bc_query_features (routes to WFS or file parser)."""

    @pytest.mark.asyncio
    async def test_routes_to_wfs_when_queryable_via_wfs_true(self):
        """bc_query_features calls _wfs_fetch when queryable_via_wfs=True."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        wfs_result = (([{"FIRE_NUMBER": "C00001"}], False), False)
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(return_value=wfs_result),
            ) as mock_wfs,
        ):
            await bc_query_features(package_id="pkg-fire-001")
        mock_wfs.assert_called_once()
        # layer should be the object_name from the dataset
        call_kwargs = mock_wfs.call_args
        layer_arg = call_kwargs[1].get("layer") or call_kwargs[0][0]
        assert layer_arg == "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"

    @pytest.mark.asyncio
    async def test_routes_to_fetch_and_parse_when_queryable_via_wfs_false(self):
        """bc_query_features calls fetch_and_parse when queryable_via_wfs=False."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        file_rows = [{"fire_id": "1", "status": "out"}]
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=False), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_and_parse",
                new=AsyncMock(return_value=(file_rows, False)),
            ) as mock_parse,
        ):
            await bc_query_features(package_id="pkg-fire-002")
        mock_parse.assert_called_once()
        # URL should be the CSV resource URL
        call_args = mock_parse.call_args
        url_arg = call_args[0][0] if call_args[0] else call_args[1].get("url")
        assert "bc-fire-report.csv" in url_arg

    @pytest.mark.asyncio
    async def test_passes_max_records_to_wfs_path(self):
        """bc_query_features passes max_records to _wfs_fetch."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        wfs_result = (([], False), False)
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(return_value=wfs_result),
            ) as mock_wfs,
        ):
            await bc_query_features(package_id="pkg-fire-001", max_records=100)
        call_kwargs = mock_wfs.call_args
        max_records_arg = call_kwargs[1].get("max_records")
        assert max_records_arg == 100

    @pytest.mark.asyncio
    async def test_passes_include_geometry_to_wfs_path(self):
        """bc_query_features passes include_geometry to _wfs_fetch."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        wfs_result = (([], False), False)
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(return_value=wfs_result),
            ) as mock_wfs,
        ):
            await bc_query_features(package_id="pkg-fire-001", include_geometry=True)
        call_kwargs = mock_wfs.call_args
        ig_arg = call_kwargs[1].get("include_geometry")
        assert ig_arg is True

    @pytest.mark.asyncio
    async def test_builds_cql_from_simplified_filters(self):
        """bc_query_features converts filter dict to CQL string before calling _wfs_fetch."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        wfs_result = (([], False), False)
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(return_value=wfs_result),
            ) as mock_wfs,
        ):
            await bc_query_features(
                package_id="pkg-fire-001",
                filters={"region": "Vancouver Island", "year": 2023},
            )
        call_kwargs = mock_wfs.call_args
        cql_arg = call_kwargs[1].get("cql")
        assert cql_arg is not None
        # String field should be quoted, int field should not
        assert "REGION='Vancouver Island'" in cql_arg
        assert "YEAR=2023" in cql_arg

    @pytest.mark.asyncio
    async def test_cql_escapes_single_quotes(self):
        """_build_cql escapes single quotes in string values (SQL injection safe)."""
        from mcp_canada.modules.british_columbia.tools import _build_cql

        cql = _build_cql({"name": "Smith's Ranch"})
        assert "Smith''s Ranch" in cql

    @pytest.mark.asyncio
    async def test_cql_casts_numerics(self):
        """_build_cql does not quote int or float filter values."""
        from mcp_canada.modules.british_columbia.tools import _build_cql

        cql = _build_cql({"year": 2023, "area": 100.5})
        assert "YEAR=2023" in cql
        assert "AREA=100.5" in cql
        # Should NOT wrap in quotes
        assert "YEAR='2023'" not in cql
        assert "AREA='100.5'" not in cql

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_wfs_error(self):
        """bc_query_features returns UPSTREAM_ERROR when _wfs_fetch raises WfsError."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features
        from mcp_canada.shared.ogc import WfsError

        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(side_effect=WfsError("InvalidParameterValue", "Feature type unknown")),
            ),
        ):
            result = await bc_query_features(package_id="pkg-fire-001")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_returns_truncated_flag_in_meta_when_cap_hit(self):
        """bc_query_features includes truncated=True in data when WFS cap is hit."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        wfs_result = (([{"X": 1}] * 5000, True), False)
        with (
            patch(
                "mcp_canada.modules.british_columbia.tools.fetch_dataset_details",
                new=AsyncMock(return_value=(_wfs_details(queryable=True), False)),
            ),
            patch(
                "mcp_canada.modules.british_columbia.tools._wfs_fetch",
                new=AsyncMock(return_value=wfs_result),
            ),
        ):
            result = await bc_query_features(package_id="pkg-fire-001")
        assert result["data"]["truncated"] is True

    @pytest.mark.asyncio
    async def test_returns_invalid_input_when_package_id_missing(self):
        """bc_query_features returns INVALID_INPUT when package_id is empty."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        result = await bc_query_features(package_id="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    def test_keywords_min_8(self):
        """bc_query_features docstring has at least 8 keywords."""
        from mcp_canada.modules.british_columbia.tools import bc_query_features

        doc = bc_query_features.__doc__ or ""
        assert "Keywords:" in doc
        kw_line = next(line for line in doc.splitlines() if "Keywords:" in line)
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


class TestBcListOrganizations:
    """Tests for bc_list_organizations (CKAN organization_list tool)."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_org_list(self):
        """bc_list_organizations returns _meta.source.api == 'bc-data-catalogue'."""
        from mcp_canada.modules.british_columbia.tools import bc_list_organizations

        fake_orgs = ["bc-wildfire-service", "min-forests", "env-air-quality"]
        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_organizations",
            new=AsyncMock(return_value=(fake_orgs, False)),
        ):
            result = await bc_list_organizations()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-data-catalogue"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_propagates_lang(self):
        """bc_list_organizations forwards lang to the response envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_list_organizations

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_organizations",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await bc_list_organizations(lang="fr")
        assert result["_meta"]["lang"] == "fr"

    def test_keywords_min_8(self):
        """bc_list_organizations docstring has at least 8 keywords."""
        from mcp_canada.modules.british_columbia.tools import bc_list_organizations

        doc = bc_list_organizations.__doc__ or ""
        assert "Keywords:" in doc
        kw_line = next(line for line in doc.splitlines() if "Keywords:" in line)
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


class TestBcListCategories:
    """Tests for bc_list_categories (CKAN tag_list tool).

    BC has no CKAN groups (HTTP 403). Categories are surfaced as tags.
    """

    @pytest.mark.asyncio
    async def test_returns_tag_list_as_categories(self):
        """bc_list_categories returns tag list as the categories data."""
        from mcp_canada.modules.british_columbia.tools import bc_list_categories

        fake_tags = ["wildfire", "forestry", "water", "mining", "parks"]
        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_tags",
            new=AsyncMock(return_value=(fake_tags, False)),
        ):
            result = await bc_list_categories()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-data-catalogue"
        assert isinstance(result["data"], list)
        assert "wildfire" in result["data"]

    @pytest.mark.asyncio
    async def test_propagates_lang(self):
        """bc_list_categories forwards lang to the response envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_list_categories

        with patch(
            "mcp_canada.modules.british_columbia.tools.fetch_tags",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await bc_list_categories(lang="fr")
        assert result["_meta"]["lang"] == "fr"

    def test_keywords_min_8(self):
        """bc_list_categories docstring has at least 8 keywords."""
        from mcp_canada.modules.british_columbia.tools import bc_list_categories

        doc = bc_list_categories.__doc__ or ""
        assert "Keywords:" in doc
        kw_line = next(line for line in doc.splitlines() if "Keywords:" in line)
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


# ---------------------------------------------------------------------------
# Plan 03 — 15 Curated WFS Tools
# ---------------------------------------------------------------------------


_SAMPLE_FIRE_FEATURES = [{"FIRE_NUMBER": "C00001", "FIRE_STATUS": "Active", "CURRENT_SIZE": 50.0}]
_SAMPLE_PERIM_FEATURES = [{"FIRE_YEAR": 2023, "FIRE_SIZE_HECTARES": 500.0}]
_SAMPLE_FORESTTEN_FEATURES = [{"LIFE_CYCLE_STATUS_CODE": "ACTIVE", "CLIENT_NAME": "Weyerhaeuser"}]
_SAMPLE_CUTBLOCK_FEATURES = [{"LIFE_CYCLE_STATUS_CODE": "ACTIVE", "ADMIN_DISTRICT_NAME": "DKM"}]
_SAMPLE_PROTAREA_FEATURES = [{"PROTECTED_LANDS_NAME": "Test Park", "OFFICIAL_AREA_HA": 5000.0}]


class TestBcGetActiveFires:
    """Tests for bc_get_active_fires (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP)."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_bc_wfs_api(self):
        """bc_get_active_fires returns _meta with api=bc-wfs."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, False), False)),
        ):
            result = await bc_get_active_fires()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-wfs"

    @pytest.mark.asyncio
    async def test_builds_cql_with_status_and_centre_filters(self):
        """bc_get_active_fires passes FIRE_STATUS and FIRE_CENTRE via CQL to _wfs_fetch."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_active_fires(status="Out", centre="Cariboo Fire Centre")
        cql = mock_wfs.call_args[1].get("cql") or mock_wfs.call_args[0][1] if mock_wfs.call_args[0] else mock_wfs.call_args[1].get("cql")
        assert cql is not None
        assert "FIRE_STATUS='Out'" in cql
        assert "FIRE_CENTRE='Cariboo Fire Centre'" in cql

    @pytest.mark.asyncio
    async def test_no_cql_when_all_filters_none(self):
        """bc_get_active_fires passes cql=None to _wfs_fetch when no filters given."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_active_fires()
        cql = mock_wfs.call_args[1].get("cql")
        assert cql is None

    @pytest.mark.asyncio
    async def test_min_size_uses_gte_operator(self):
        """bc_get_active_fires appends CURRENT_SIZE >= N to CQL for min_size_hectares."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_active_fires(min_size_hectares=1000.0)
        cql = mock_wfs.call_args[1].get("cql")
        assert cql is not None
        assert "CURRENT_SIZE" in cql
        assert "1000" in cql

    @pytest.mark.asyncio
    async def test_wraps_wfs_error_as_upstream_error(self):
        """bc_get_active_fires returns UPSTREAM_ERROR when WfsError is raised."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires
        from mcp_canada.shared.ogc import WfsError

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(side_effect=WfsError("InvalidParameterValue", "Bad layer")),
        ):
            result = await bc_get_active_fires()
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_propagates_lang_fr(self):
        """bc_get_active_fires respects lang=fr in _meta."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, False), False)),
        ):
            result = await bc_get_active_fires(lang="fr")
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_truncated_flag(self):
        """bc_get_active_fires includes truncated=True when WFS cap is hit."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FIRE_FEATURES, True), False)),
        ):
            result = await bc_get_active_fires()
        assert result["data"]["truncated"] is True

    def test_docstring_has_8_plus_keywords(self):
        """bc_get_active_fires docstring has at least 8 keywords."""
        from mcp_canada.modules.british_columbia.tools import bc_get_active_fires

        doc = bc_get_active_fires.__doc__ or ""
        kw_line = next((line for line in doc.splitlines() if "Keywords:" in line), "")
        keywords = [k.strip() for k in kw_line.split("Keywords:")[-1].split(",") if k.strip()]
        assert len(keywords) >= 8


class TestBcGetFirePerimeters:
    """Tests for bc_get_fire_perimeters (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP)."""

    @pytest.mark.asyncio
    async def test_requires_year_param(self):
        """bc_get_fire_perimeters returns INVALID_INPUT when year is None."""
        from mcp_canada.modules.british_columbia.tools import bc_get_fire_perimeters

        result = await bc_get_fire_perimeters(year=None)
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_builds_cql_with_year(self):
        """bc_get_fire_perimeters passes FIRE_YEAR=2023 in CQL."""
        from mcp_canada.modules.british_columbia.tools import bc_get_fire_perimeters

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PERIM_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_fire_perimeters(year=2023)
        cql = mock_wfs.call_args[1].get("cql")
        assert cql is not None
        assert "FIRE_YEAR=2023" in cql

    @pytest.mark.asyncio
    async def test_optional_cause_filter(self):
        """bc_get_fire_perimeters appends FIRE_CAUSE filter when cause is given."""
        from mcp_canada.modules.british_columbia.tools import bc_get_fire_perimeters

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PERIM_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_fire_perimeters(year=2023, cause="Human")
        cql = mock_wfs.call_args[1].get("cql")
        assert "FIRE_CAUSE='Human'" in cql

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """bc_get_fire_perimeters returns proper _meta envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_get_fire_perimeters

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PERIM_FEATURES, False), False)),
        ):
            result = await bc_get_fire_perimeters(year=2023)
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-wfs"


class TestBcGetForestTenure:
    """Tests for bc_get_forest_tenure (WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW)."""

    @pytest.mark.asyncio
    async def test_defaults_to_active_status(self):
        """bc_get_forest_tenure uses LIFE_CYCLE_STATUS_CODE='ACTIVE' by default."""
        from mcp_canada.modules.british_columbia.tools import bc_get_forest_tenure

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FORESTTEN_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_forest_tenure()
        cql = mock_wfs.call_args[1].get("cql")
        assert cql is not None
        assert "LIFE_CYCLE_STATUS_CODE='ACTIVE'" in cql

    @pytest.mark.asyncio
    async def test_client_name_uses_like_operator(self):
        """bc_get_forest_tenure uses CLIENT_NAME LIKE 'value%' for partial match."""
        from mcp_canada.modules.british_columbia.tools import bc_get_forest_tenure

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FORESTTEN_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_forest_tenure(client_name="Weyerhaeuser")
        cql = mock_wfs.call_args[1].get("cql")
        assert "CLIENT_NAME" in cql
        assert "LIKE" in cql
        assert "Weyerhaeuser" in cql

    @pytest.mark.asyncio
    async def test_meta_envelope(self):
        """bc_get_forest_tenure returns proper _meta envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_get_forest_tenure

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_FORESTTEN_FEATURES, False), False)),
        ):
            result = await bc_get_forest_tenure()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-wfs"


class TestBcGetCutBlocks:
    """Tests for bc_get_cut_blocks (WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW)."""

    @pytest.mark.asyncio
    async def test_uses_ften_cut_block_poly_svw_layer(self):
        """bc_get_cut_blocks uses FTEN_CUT_BLOCK_POLY_SVW layer (not deprecated POLYGONS). Pitfall 9."""
        from mcp_canada.modules.british_columbia.tools import bc_get_cut_blocks

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_CUTBLOCK_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_cut_blocks()
        layer = mock_wfs.call_args[1].get("layer") or mock_wfs.call_args[0][0]
        assert "FTEN_CUT_BLOCK_POLY_SVW" in layer

    @pytest.mark.asyncio
    async def test_defaults_to_active_status(self):
        """bc_get_cut_blocks uses LIFE_CYCLE_STATUS_CODE='ACTIVE' by default."""
        from mcp_canada.modules.british_columbia.tools import bc_get_cut_blocks

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_CUTBLOCK_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_cut_blocks()
        cql = mock_wfs.call_args[1].get("cql")
        assert cql is not None
        assert "LIFE_CYCLE_STATUS_CODE='ACTIVE'" in cql

    @pytest.mark.asyncio
    async def test_meta_envelope(self):
        """bc_get_cut_blocks returns proper _meta envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_get_cut_blocks

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_CUTBLOCK_FEATURES, False), False)),
        ):
            result = await bc_get_cut_blocks()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-wfs"


class TestBcGetProtectedAreas:
    """Tests for bc_get_protected_areas (WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW)."""

    @pytest.mark.asyncio
    async def test_uses_whse_tantalis_layer(self):
        """bc_get_protected_areas uses WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW. Pitfall 8."""
        from mcp_canada.modules.british_columbia.tools import bc_get_protected_areas

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PROTAREA_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_protected_areas()
        layer = mock_wfs.call_args[1].get("layer") or mock_wfs.call_args[0][0]
        assert "WHSE_TANTALIS" in layer
        assert "TA_PARK_ECORES_PA_SVW" in layer

    @pytest.mark.asyncio
    async def test_designation_filter(self):
        """bc_get_protected_areas passes PROTECTED_LANDS_DESIGNATION in CQL."""
        from mcp_canada.modules.british_columbia.tools import bc_get_protected_areas

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PROTAREA_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_protected_areas(designation="PROVINCIAL PARK")
        cql = mock_wfs.call_args[1].get("cql")
        assert "PROTECTED_LANDS_DESIGNATION='PROVINCIAL PARK'" in cql

    @pytest.mark.asyncio
    async def test_min_area_filter(self):
        """bc_get_protected_areas appends OFFICIAL_AREA_HA >= N for min_area_ha."""
        from mcp_canada.modules.british_columbia.tools import bc_get_protected_areas

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PROTAREA_FEATURES, False), False)),
        ) as mock_wfs:
            await bc_get_protected_areas(min_area_ha=100.0)
        cql = mock_wfs.call_args[1].get("cql")
        assert "OFFICIAL_AREA_HA" in cql
        assert "100" in cql

    @pytest.mark.asyncio
    async def test_meta_envelope(self):
        """bc_get_protected_areas returns proper _meta envelope."""
        from mcp_canada.modules.british_columbia.tools import bc_get_protected_areas

        with patch(
            "mcp_canada.modules.british_columbia.tools._wfs_fetch",
            new=AsyncMock(return_value=((_SAMPLE_PROTAREA_FEATURES, False), False)),
        ):
            result = await bc_get_protected_areas()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bc-wfs"


class TestBcGetWaterWells:
    """Tests for bc_get_water_wells (WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW). Plan 03 implements.

    IMPORTANT: Must include test_requires_at_least_one_filter — water wells has ~130K records
    (RESEARCH Pitfall 5). Tool must require at least one filter (city, aquifer_id, well_class)
    to prevent runaway WFS fetches.
    """

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False

    @pytest.mark.xfail(reason="Plan 03 will implement — 130K-record guard", strict=False)
    def test_requires_at_least_one_filter(self):
        """bc_get_water_wells must return INVALID_INPUT when no filter provided (130K-record guard)."""
        assert False


class TestBcGetWildfireWeatherStations:
    """Tests for bc_get_wildfire_weather_stations (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetLocalParks:
    """Tests for bc_get_local_parks (WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetMiningTenure:
    """Tests for bc_get_mining_tenure (WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetFishHabitat:
    """Tests for bc_get_fish_habitat (WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetEmergencyRooms:
    """Tests for bc_get_emergency_rooms (WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetWalkInClinics:
    """Tests for bc_get_walk_in_clinics (WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetHighwayProfiles:
    """Tests for bc_get_highway_profiles (WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetRoadStructures:
    """Tests for bc_get_road_structures (WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetClimateStations:
    """Tests for bc_get_climate_stations (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP — climate alias). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False
