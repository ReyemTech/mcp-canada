"""Unit tests for york_region/tools.py — discovery and curated tools.

Tests are organized into:
- TestYorkRegionDiscovery: happy path for each of the 5 discovery action types (york_region_ prefix)
- TestAllPrefixesExist: parametrized — verifies wiring for all 20 discovery tools
- TestNotFoundHandling: NoPortalError -> make_error("NOT_FOUND")
- TestHTTPErrorHandling: 404 -> NOT_FOUND, 5xx -> UPSTREAM_ERROR
- TestGenericExceptionHandling: bare Exception -> UPSTREAM_ERROR
- TestLangParameter: lang="fr" flows through to envelope
- TestQueryFeaturesInputClamp: max_records=9999 is clamped to 5000

Task 2 additions:
- TestYorkRegionCurated: happy paths for all curated York Region tools
- TestYorkRegionDispatch: invalid dispatch values -> make_error("INVALID_INPUT")
- TestMarkhamCurated: happy paths for Markham curated tools
- TestAllToolsReturnEnvelope: parametrized across all tools
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_canada.modules.york_region.client import NoPortalError


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_FAKE_SEARCH_RESULT = [
    {"id": "abc123", "title": "York Region Bus Stops", "type": "Feature Service"}
]
_FAKE_DETAILS_RESULT = {"id": "abc123", "title": "York Region Bus Stops"}
_FAKE_FEATURE_RESULT = {"features": [{"OBJECTID": 1}], "count": 1, "truncated": False}
_FAKE_ORGS_RESULT = ["YorkRegion_GIS", "YorkRegion_Health"]
_FAKE_CATS_RESULT = ["Transportation", "Health"]


def _make_http_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(f"HTTP {status_code}", request=request, response=response)


# ---------------------------------------------------------------------------
# Task 1: Discovery tools
# ---------------------------------------------------------------------------


class TestYorkRegionDiscovery:
    """Happy-path tests for all 5 discovery action types (york_region_ prefix)."""

    @pytest.mark.asyncio
    async def test_search_datasets_returns_meta_envelope(self):
        """york_region_search_datasets returns _meta envelope with arcgis-hub."""
        from mcp_canada.modules.york_region.tools import york_region_search_datasets

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(_FAKE_SEARCH_RESULT, False)),
        ):
            result = await york_region_search_datasets(query="transit", limit=5)

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "arcgis-hub"
        assert result["data"] == _FAKE_SEARCH_RESULT
        assert result["_meta"]["cached"] is False

    @pytest.mark.asyncio
    async def test_get_dataset_details_returns_meta_envelope(self):
        """york_region_get_dataset_details returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_dataset_details

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_get_dataset_details",
            new=AsyncMock(return_value=(_FAKE_DETAILS_RESULT, True)),
        ):
            result = await york_region_get_dataset_details(dataset_id="abc123")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "arcgis-hub"
        assert result["_meta"]["cached"] is True

    @pytest.mark.asyncio
    async def test_query_features_returns_meta_envelope(self):
        """york_region_query_features returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_query_features

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_query_features",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_query_features(
                service_url="https://example.com/FeatureServer",
                layer_id=0,
            )

        assert "_meta" in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_list_organizations_returns_meta_envelope(self):
        """york_region_list_organizations returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_list_organizations

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_list_organizations",
            new=AsyncMock(return_value=(_FAKE_ORGS_RESULT, False)),
        ):
            result = await york_region_list_organizations()

        assert "_meta" in result
        assert result["data"] == _FAKE_ORGS_RESULT

    @pytest.mark.asyncio
    async def test_list_categories_returns_meta_envelope(self):
        """york_region_list_categories returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_list_categories

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_list_categories",
            new=AsyncMock(return_value=(_FAKE_CATS_RESULT, False)),
        ):
            result = await york_region_list_categories()

        assert "_meta" in result
        assert result["data"] == _FAKE_CATS_RESULT


class TestAllPrefixesExist:
    """Verify all 20 discovery tools are properly wired (importable and return _meta)."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name,mock_target,mock_return", [
        # search_datasets
        ("york_region_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False)),
        ("markham_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False)),
        ("newmarket_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False)),
        ("aurora_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False)),
        # get_dataset_details
        ("york_region_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False)),
        ("markham_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False)),
        ("newmarket_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False)),
        ("aurora_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False)),
        # query_features
        ("york_region_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False)),
        ("markham_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False)),
        ("newmarket_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False)),
        ("aurora_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False)),
        # list_organizations
        ("york_region_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False)),
        ("markham_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False)),
        ("newmarket_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False)),
        ("aurora_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False)),
        # list_categories
        ("york_region_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False)),
        ("markham_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False)),
        ("newmarket_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False)),
        ("aurora_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False)),
    ])
    async def test_tool_wired_and_returns_meta(self, tool_name: str, mock_target: str, mock_return: Any):
        """Each of the 20 discovery tools is importable and returns a dict with _meta."""
        import mcp_canada.modules.york_region.tools as tools_module

        tool_fn = getattr(tools_module, tool_name)

        # Build kwargs depending on tool type
        if "search_datasets" in tool_name:
            kwargs = {"query": "test"}
        elif "get_dataset_details" in tool_name:
            kwargs = {"dataset_id": "abc123"}
        elif "query_features" in tool_name:
            kwargs = {"service_url": "https://example.com/FeatureServer", "layer_id": 0}
        elif "list_organizations" in tool_name or "list_categories" in tool_name:
            kwargs = {}
        else:
            kwargs = {}

        with patch(
            f"mcp_canada.modules.york_region.tools.{mock_target}",
            new=AsyncMock(return_value=mock_return),
        ):
            result = await tool_fn(**kwargs)

        assert isinstance(result, dict), f"{tool_name} should return dict"
        assert "_meta" in result, f"{tool_name} should have _meta key"


class TestNotFoundHandling:
    """NoPortalError from client -> make_error('NOT_FOUND')."""

    @pytest.mark.asyncio
    async def test_no_portal_error_returns_not_found(self):
        """Patching fetch_search_datasets to raise NoPortalError -> NOT_FOUND error response."""
        from mcp_canada.modules.york_region.tools import york_region_search_datasets

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_search_datasets",
            new=AsyncMock(side_effect=NoPortalError("vaughan has no portal")),
        ):
            result = await york_region_search_datasets(query="transit")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"
        assert "vaughan has no portal" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_value_error_dataset_not_found(self):
        """ValueError from fetch_get_dataset_details (dataset not found) -> UPSTREAM_ERROR."""
        from mcp_canada.modules.york_region.tools import york_region_get_dataset_details

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_get_dataset_details",
            new=AsyncMock(side_effect=ValueError("dataset not found: xyz")),
        ):
            result = await york_region_get_dataset_details(dataset_id="xyz")

        assert "error" in result
        # ValueError is caught by the generic Exception handler -> UPSTREAM_ERROR
        assert result["error"]["code"] in ("NOT_FOUND", "UPSTREAM_ERROR")


class TestHTTPErrorHandling:
    """HTTP errors from client -> appropriate make_error codes."""

    @pytest.mark.asyncio
    async def test_http_404_returns_not_found(self):
        """HTTPStatusError 404 -> make_error('NOT_FOUND')."""
        from mcp_canada.modules.york_region.tools import york_region_search_datasets

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_search_datasets",
            new=AsyncMock(side_effect=_make_http_error(404)),
        ):
            result = await york_region_search_datasets(query="test")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_http_500_returns_upstream_error(self):
        """HTTPStatusError 500 -> make_error('UPSTREAM_ERROR')."""
        from mcp_canada.modules.york_region.tools import york_region_search_datasets

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_search_datasets",
            new=AsyncMock(side_effect=_make_http_error(500)),
        ):
            result = await york_region_search_datasets(query="test")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestGenericExceptionHandling:
    """Generic Exception -> UPSTREAM_ERROR (tools must never raise)."""

    @pytest.mark.asyncio
    async def test_generic_exception_returns_upstream_error(self):
        """Any unexpected exception -> make_error('UPSTREAM_ERROR')."""
        from mcp_canada.modules.york_region.tools import york_region_list_organizations

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_list_organizations",
            new=AsyncMock(side_effect=RuntimeError("connection reset")),
        ):
            result = await york_region_list_organizations()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestLangParameter:
    """lang='fr' flows through to the _meta envelope."""

    @pytest.mark.asyncio
    async def test_lang_fr_in_envelope(self):
        """lang='fr' is recorded in _meta.lang."""
        from mcp_canada.modules.york_region.tools import york_region_search_datasets

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(_FAKE_SEARCH_RESULT, False)),
        ):
            result = await york_region_search_datasets(query="transit", lang="fr")

        assert result["_meta"]["lang"] == "fr"


class TestQueryFeaturesInputClamp:
    """max_records=9999 is clamped to 5000 before calling fetch_query_features."""

    @pytest.mark.asyncio
    async def test_max_records_clamped_to_5000(self):
        """Passing max_records=9999 results in fetch_query_features called with max_records=5000."""
        from mcp_canada.modules.york_region.tools import york_region_query_features

        mock_fn = AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False))
        with patch(
            "mcp_canada.modules.york_region.tools.fetch_query_features",
            new=mock_fn,
        ):
            await york_region_query_features(
                service_url="https://example.com/FeatureServer",
                layer_id=0,
                max_records=9999,
            )

        call_kwargs = mock_fn.call_args[1] if mock_fn.call_args[1] else {}
        call_args = mock_fn.call_args[0] if mock_fn.call_args[0] else ()
        # max_records should be 5000 (clamped), passed as positional or keyword
        # fetch_query_features signature: (portal_key, service_url, layer_id, where, out_fields, include_geometry, max_records)
        all_args = list(call_args) + list(call_kwargs.values())
        assert 5000 in all_args or call_kwargs.get("max_records") == 5000


# ---------------------------------------------------------------------------
# Task 2: Curated tools
# ---------------------------------------------------------------------------


class TestYorkRegionCurated:
    """Happy-path tests for all York Region curated tools."""

    @pytest.mark.asyncio
    async def test_get_transit_stops_returns_meta_envelope(self):
        """york_region_get_transit_stops returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_transit_stops

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_transit_stops",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_transit_stops(query="Finch")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "arcgis-hub"

    @pytest.mark.asyncio
    async def test_get_transit_routes_returns_meta_envelope(self):
        """york_region_get_transit_routes returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_transit_routes

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_transit_routes",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_transit_routes(route_short_name="60")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_road_network_returns_meta_envelope(self):
        """york_region_get_road_network returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_road_network

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_regional_roads",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_road_network()

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_public_health_beach_water_returns_meta_envelope(self):
        """york_region_get_public_health with beach_water returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_public_health

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_beach_water_testing",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_public_health(location_type="beach_water")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_public_health_hospital_returns_meta_envelope(self):
        """york_region_get_public_health with hospital returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_public_health

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_hospitals",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_public_health(location_type="hospital")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_public_health_drinking_water_returns_meta_envelope(self):
        """york_region_get_public_health with drinking_water returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_public_health

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_drinking_water_incidents",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_public_health(location_type="drinking_water")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_census_demographics_age_sex_returns_meta_envelope(self):
        """york_region_get_census_demographics with age_sex returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_census_demographics

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_census_age_sex",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_census_demographics(dataset="age_sex", csdname="Markham")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_census_demographics_income_returns_meta_envelope(self):
        """york_region_get_census_demographics with income returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_census_demographics

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_census_income",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_census_demographics(dataset="income")

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_waste_data_diversion_returns_meta_envelope(self):
        """york_region_get_waste_data with diversion_statistics returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_waste_data

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_waste_diversion",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_waste_data(dataset="diversion_statistics", year=2021)

        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_get_waste_data_sites_returns_meta_envelope(self):
        """york_region_get_waste_data with sites returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import york_region_get_waste_data

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_solid_waste_sites",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await york_region_get_waste_data(dataset="sites")

        assert "_meta" in result


class TestYorkRegionDispatch:
    """Dispatch error tests for tools that accept a type enum."""

    @pytest.mark.asyncio
    async def test_public_health_invalid_location_type(self):
        """Invalid location_type returns INVALID_INPUT error."""
        from mcp_canada.modules.york_region.tools import york_region_get_public_health

        result = await york_region_get_public_health(location_type="invalid")  # type: ignore[arg-type]

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "beach_water" in result["error"]["message"] or "valid" in str(result["error"])

    @pytest.mark.asyncio
    async def test_census_invalid_dataset(self):
        """Invalid dataset for census returns INVALID_INPUT error."""
        from mcp_canada.modules.york_region.tools import york_region_get_census_demographics

        result = await york_region_get_census_demographics(dataset="bad_value")  # type: ignore[arg-type]

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_waste_invalid_dataset(self):
        """Invalid dataset for waste returns INVALID_INPUT error."""
        from mcp_canada.modules.york_region.tools import york_region_get_waste_data

        result = await york_region_get_waste_data(dataset="invalid_type")  # type: ignore[arg-type]

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_public_health_hospital_dispatches_to_fetch_hospitals(self):
        """location_type='hospital' calls fetch_hospitals (not beach or drinking water)."""
        from mcp_canada.modules.york_region.tools import york_region_get_public_health

        mock_hospitals = AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False))
        mock_beach = AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False))
        mock_drinking = AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False))

        with (
            patch("mcp_canada.modules.york_region.tools.fetch_hospitals", new=mock_hospitals),
            patch("mcp_canada.modules.york_region.tools.fetch_beach_water_testing", new=mock_beach),
            patch("mcp_canada.modules.york_region.tools.fetch_drinking_water_incidents", new=mock_drinking),
        ):
            await york_region_get_public_health(location_type="hospital")

        mock_hospitals.assert_called_once()
        mock_beach.assert_not_called()
        mock_drinking.assert_not_called()


class TestMarkhamCurated:
    """Happy-path tests for Markham curated tools."""

    @pytest.mark.asyncio
    async def test_get_addresses_returns_meta_envelope(self):
        """markham_get_addresses returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import markham_get_addresses

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_markham_addresses",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await markham_get_addresses(street="Main")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "arcgis-hub"

    @pytest.mark.asyncio
    async def test_get_addresses_street_filter_passes_through(self):
        """street parameter is passed to fetch_markham_addresses."""
        from mcp_canada.modules.york_region.tools import markham_get_addresses

        mock_fn = AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False))
        with patch(
            "mcp_canada.modules.york_region.tools.fetch_markham_addresses",
            new=mock_fn,
        ):
            await markham_get_addresses(street="Oak")

        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args[1] if mock_fn.call_args[1] else {}
        call_args = mock_fn.call_args[0] if mock_fn.call_args[0] else ()
        assert "Oak" in str(call_args) or "Oak" in str(call_kwargs)

    @pytest.mark.asyncio
    async def test_get_road_network_returns_meta_envelope(self):
        """markham_get_road_network returns _meta envelope."""
        from mcp_canada.modules.york_region.tools import markham_get_road_network

        with patch(
            "mcp_canada.modules.york_region.tools.fetch_markham_roads",
            new=AsyncMock(return_value=(_FAKE_FEATURE_RESULT, False)),
        ):
            result = await markham_get_road_network(name="Oak")

        assert "_meta" in result


class TestAllToolsReturnEnvelope:
    """Parametrized: every tool returns a dict with _meta.source.api == 'arcgis-hub' and correct lang."""

    # All 27 (or 28) tools and what to mock to make them succeed
    _TOOL_MOCK_MAP = [
        # Discovery — york_region
        ("york_region_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False), {"query": "test"}),
        ("york_region_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False), {"dataset_id": "abc"}),
        ("york_region_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False), {"service_url": "https://x.com/FS", "layer_id": 0}),
        ("york_region_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False), {}),
        ("york_region_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False), {}),
        # Discovery — markham
        ("markham_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False), {"query": "test"}),
        ("markham_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False), {"dataset_id": "abc"}),
        ("markham_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False), {"service_url": "https://x.com/FS", "layer_id": 0}),
        ("markham_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False), {}),
        ("markham_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False), {}),
        # Discovery — newmarket
        ("newmarket_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False), {"query": "test"}),
        ("newmarket_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False), {"dataset_id": "abc"}),
        ("newmarket_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False), {"service_url": "https://x.com/FS", "layer_id": 0}),
        ("newmarket_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False), {}),
        ("newmarket_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False), {}),
        # Discovery — aurora
        ("aurora_search_datasets", "fetch_search_datasets", (_FAKE_SEARCH_RESULT, False), {"query": "test"}),
        ("aurora_get_dataset_details", "fetch_get_dataset_details", (_FAKE_DETAILS_RESULT, False), {"dataset_id": "abc"}),
        ("aurora_query_features", "fetch_query_features", (_FAKE_FEATURE_RESULT, False), {"service_url": "https://x.com/FS", "layer_id": 0}),
        ("aurora_list_organizations", "fetch_list_organizations", (_FAKE_ORGS_RESULT, False), {}),
        ("aurora_list_categories", "fetch_list_categories", (_FAKE_CATS_RESULT, False), {}),
        # Curated York Region
        ("york_region_get_transit_stops", "fetch_transit_stops", (_FAKE_FEATURE_RESULT, False), {}),
        ("york_region_get_transit_routes", "fetch_transit_routes", (_FAKE_FEATURE_RESULT, False), {}),
        ("york_region_get_road_network", "fetch_regional_roads", (_FAKE_FEATURE_RESULT, False), {}),
        # Curated York Region dispatch tools need special kwargs
        ("markham_get_addresses", "fetch_markham_addresses", (_FAKE_FEATURE_RESULT, False), {}),
        ("markham_get_road_network", "fetch_markham_roads", (_FAKE_FEATURE_RESULT, False), {}),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name,mock_target,mock_return,kwargs", _TOOL_MOCK_MAP)
    async def test_tool_returns_envelope(
        self,
        tool_name: str,
        mock_target: str,
        mock_return: Any,
        kwargs: dict,
    ):
        """Each tool returns dict with _meta.source.api == 'arcgis-hub'."""
        import mcp_canada.modules.york_region.tools as tools_module

        tool_fn = getattr(tools_module, tool_name)

        with patch(
            f"mcp_canada.modules.york_region.tools.{mock_target}",
            new=AsyncMock(return_value=mock_return),
        ):
            result = await tool_fn(**kwargs)

        assert isinstance(result, dict), f"{tool_name} must return dict"
        assert "_meta" in result, f"{tool_name} must have _meta"
        assert result["_meta"]["source"]["api"] == "arcgis-hub", f"{tool_name} api must be arcgis-hub"
        assert result["_meta"]["cached"] is False
        assert result["_meta"]["lang"] == "en"
