"""Unit tests for Toronto Open Data @tool functions.

Tests cover:
- Happy paths: each tool returns make_response envelope with correct data
- Error paths: HTTPStatusError returns make_error with correct code
- lang parameter passed through to all responses
- Docstring quality: Keywords, Use for lines for BM25
- NOT_FOUND on 404 for dataset/resource detail tools
- toronto_get_dataset_stats data shape (total_datasets, portal, api_version)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def import_tools():
    """Import Toronto tools module."""
    import mcp_canada.modules.toronto.tools as tools_mod
    return tools_mod


def make_http_error(status_code: int = 404) -> httpx.HTTPStatusError:
    """Create a mock HTTPStatusError."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    return httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_DATASETS = [
    {
        "id": "7795b45e-e65a-4465-81fc-c5b0dc4b531e",
        "name": "ttc-routes-and-schedules",
        "title": "TTC Routes and Schedules",
        "description": "TTC GTFS static schedule data.",
        "organization": {"name": "ttc", "title": "Toronto Transit Commission"},
        "num_resources": 1,
        "tags": [{"name": "transit"}],
        "resources": [{"id": "r1", "name": "GTFS ZIP", "format": "ZIP", "size": 37000000, "url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/r1", "datastore_active": False}],
        "metadata_created": "2020-01-01T00:00:00",
        "metadata_modified": "2025-01-01T00:00:00",
    },
]

SAMPLE_DATASET_DETAIL = {
    "id": "7795b45e-e65a-4465-81fc-c5b0dc4b531e",
    "name": "ttc-routes-and-schedules",
    "title": "TTC Routes and Schedules",
    "description": "TTC GTFS static schedule data.",
    "organization": {"name": "ttc", "title": "Toronto Transit Commission"},
    "num_resources": 1,
    "tags": [{"name": "transit"}],
    "resources": [{"id": "r1", "name": "GTFS ZIP", "format": "ZIP", "datastore_active": False}],
    "metadata_created": "2020-01-01T00:00:00",
    "metadata_modified": "2025-01-01T00:00:00",
}

SAMPLE_RESOURCE = {
    "id": "f17e0649-8a28-4ed6-b6b4-d89e5b8bee5d",
    "name": "ttc-routes-and-schedules.zip",
    "format": "ZIP",
    "size": 37000000,
    "url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/7795b45e/resource/f17e0649/download/ttc-routes-and-schedules.zip",
    "datastore_active": False,
}

SAMPLE_ORGANIZATIONS = [
    {"id": "org-1", "name": "ttc", "title": "Toronto Transit Commission", "package_count": 12},
    {"id": "org-2", "name": "city-planning", "title": "City Planning", "package_count": 87},
]

SAMPLE_GTFS_STOPS = [
    {"stop_id": "1001", "stop_name": "King Station", "stop_lat": "43.6489", "stop_lon": "-79.3817"},
    {"stop_id": "1002", "stop_name": "Queen Station", "stop_lat": "43.6523", "stop_lon": "-79.3804"},
]

SAMPLE_GTFS_ROUTES = [
    {"route_id": "1", "route_short_name": "1", "route_long_name": "YONGE", "route_type": "1"},
    {"route_id": "504", "route_short_name": "504", "route_long_name": "KING", "route_type": "0"},
]

SAMPLE_NEIGHBOURHOOD_PROFILE = [
    {"neighbourhood_id": "92", "neighbourhood_name": "Rosedale-Moore Park", "characteristic": "Population, 2016", "value": "24067"},
    {"neighbourhood_id": "92", "neighbourhood_name": "Rosedale-Moore Park", "characteristic": "Median household income", "value": "138567"},
]

SAMPLE_NEIGHBOURHOOD_COMPARISON = [
    {"neighbourhood_id": "92", "neighbourhood_name": "Rosedale-Moore Park", "characteristic": "Median household income", "value": "138567"},
    {"neighbourhood_id": "77", "neighbourhood_name": "Lawrence Park South", "characteristic": "Median household income", "value": "189012"},
]

SAMPLE_311_REQUESTS = [
    {"service_request_id": "123456", "service_name": "Pothole", "ward": "10", "status": "Closed", "open_date": "2024-03-01"},
    {"service_request_id": "123457", "service_name": "Noise", "ward": "10", "status": "Open", "open_date": "2024-03-02"},
]

SAMPLE_RENTSAFE = [
    {"RegistrationNumber": "R001", "WARDNAME": "Ward 10 - Spadina-Fort York", "SCORE": "85", "BUILDINGID": "123"},
    {"RegistrationNumber": "R002", "WARDNAME": "Ward 10 - Spadina-Fort York", "SCORE": "92", "BUILDINGID": "456"},
]

SAMPLE_SHORT_TERM_RENTALS = [
    {"operator_registration_number": "STR-001", "ward": "10", "status": "registered", "property_type": "entire-home"},
    {"operator_registration_number": "STR-002", "ward": "10", "status": "suspended", "property_type": "private-room"},
]


# ---------------------------------------------------------------------------
# Tool 1: toronto_search_datasets
# ---------------------------------------------------------------------------


class TestTorontoSearchDatasets:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_search_datasets returns _meta envelope with data key on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(SAMPLE_DATASETS, False)),
        ):
            result = await tools.toronto_search_datasets(query="cycling")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 1

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """toronto_search_datasets returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_search_datasets",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.toronto_search_datasets(query="cycling")

        assert "error" in result
        assert "code" in result["error"]

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(SAMPLE_DATASETS, False)),
        ):
            result = await tools.toronto_search_datasets(query="cycling", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_search_datasets.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 2: toronto_get_dataset_details
# ---------------------------------------------------------------------------


class TestTorontoGetDatasetDetails:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_dataset_details returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(SAMPLE_DATASET_DETAIL, False)),
        ):
            result = await tools.toronto_get_dataset_details(dataset_id="ttc-routes-and-schedules")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_not_found_on_404(self):
        """toronto_get_dataset_details returns NOT_FOUND error on 404."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_details",
            new=AsyncMock(side_effect=make_http_error(404)),
        ):
            result = await tools.toronto_get_dataset_details(dataset_id="nonexistent")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_500(self):
        """toronto_get_dataset_details returns UPSTREAM_ERROR on 500."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_details",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.toronto_get_dataset_details(dataset_id="some-id")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(SAMPLE_DATASET_DETAIL, True)),
        ):
            result = await tools.toronto_get_dataset_details(dataset_id="ttc-routes-and-schedules", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_dataset_details.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 3: toronto_get_resource
# ---------------------------------------------------------------------------


class TestTorontoGetResource:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_resource returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_resource",
            new=AsyncMock(return_value=(SAMPLE_RESOURCE, False)),
        ):
            result = await tools.toronto_get_resource(resource_id="f17e0649-8a28-4ed6-b6b4-d89e5b8bee5d")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_not_found_on_404(self):
        """toronto_get_resource returns NOT_FOUND error on 404."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_resource",
            new=AsyncMock(side_effect=make_http_error(404)),
        ):
            result = await tools.toronto_get_resource(resource_id="nonexistent-uuid")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_500(self):
        """toronto_get_resource returns UPSTREAM_ERROR on 500."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_resource",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.toronto_get_resource(resource_id="some-uuid")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_resource",
            new=AsyncMock(return_value=(SAMPLE_RESOURCE, False)),
        ):
            result = await tools.toronto_get_resource(resource_id="some-uuid", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_resource.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 4: toronto_list_organizations
# ---------------------------------------------------------------------------


class TestTorontoListOrganizations:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_list_organizations returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_organizations",
            new=AsyncMock(return_value=(SAMPLE_ORGANIZATIONS, False)),
        ):
            result = await tools.toronto_list_organizations()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """toronto_list_organizations returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_organizations",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.toronto_list_organizations()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_organizations",
            new=AsyncMock(return_value=(SAMPLE_ORGANIZATIONS, False)),
        ):
            result = await tools.toronto_list_organizations(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_list_organizations.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 5: toronto_get_dataset_stats
# ---------------------------------------------------------------------------


class TestTorontoGetDatasetStats:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_stats(self):
        """toronto_get_dataset_stats returns _meta envelope with total_datasets."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(500, False)),
        ):
            result = await tools.toronto_get_dataset_stats()

        assert "_meta" in result
        assert "data" in result
        assert "total_datasets" in result["data"]
        assert result["data"]["total_datasets"] == 500

    @pytest.mark.asyncio
    async def test_stats_data_has_portal_and_api_version(self):
        """toronto_get_dataset_stats data contains portal and api_version."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(500, False)),
        ):
            result = await tools.toronto_get_dataset_stats()

        assert result["data"]["portal"] == "open.toronto.ca"
        assert result["data"]["api_version"] == "CKAN 2.9"

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """toronto_get_dataset_stats returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_count",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.toronto_get_dataset_stats()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(500, False)),
        ):
            result = await tools.toronto_get_dataset_stats(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_dataset_stats.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 6: toronto_get_ttc_stops
# ---------------------------------------------------------------------------


class TestTorontoGetTtcStops:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_ttc_stops returns _meta envelope with stops list."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_stops",
            new=AsyncMock(return_value=(SAMPLE_GTFS_STOPS, False)),
        ):
            result = await tools.toronto_get_ttc_stops()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_ttc_stops returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_stops",
            new=AsyncMock(side_effect=Exception("GTFS fetch failed")),
        ):
            result = await tools.toronto_get_ttc_stops()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_stops",
            new=AsyncMock(return_value=(SAMPLE_GTFS_STOPS, True)),
        ):
            result = await tools.toronto_get_ttc_stops(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_ttc_stops.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 7: toronto_get_ttc_routes
# ---------------------------------------------------------------------------


class TestTorontoGetTtcRoutes:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_ttc_routes returns _meta envelope with routes list."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_routes",
            new=AsyncMock(return_value=(SAMPLE_GTFS_ROUTES, False)),
        ):
            result = await tools.toronto_get_ttc_routes()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_ttc_routes returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_routes",
            new=AsyncMock(side_effect=Exception("GTFS fetch failed")),
        ):
            result = await tools.toronto_get_ttc_routes()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_gtfs_routes",
            new=AsyncMock(return_value=(SAMPLE_GTFS_ROUTES, False)),
        ):
            result = await tools.toronto_get_ttc_routes(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_ttc_routes.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 8: toronto_get_neighbourhood_profile
# ---------------------------------------------------------------------------


class TestTorontoGetNeighbourhoodProfile:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_neighbourhood_profile returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_profile",
            new=AsyncMock(return_value=(SAMPLE_NEIGHBOURHOOD_PROFILE, False)),
        ):
            result = await tools.toronto_get_neighbourhood_profile(neighbourhood="Rosedale")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_neighbourhood_profile returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_profile",
            new=AsyncMock(side_effect=Exception("fetch failed")),
        ):
            result = await tools.toronto_get_neighbourhood_profile()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_profile",
            new=AsyncMock(return_value=(SAMPLE_NEIGHBOURHOOD_PROFILE, True)),
        ):
            result = await tools.toronto_get_neighbourhood_profile(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_neighbourhood_profile.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 9: toronto_compare_neighbourhoods
# ---------------------------------------------------------------------------


class TestTorontoCompareNeighbourhoods:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_compare_neighbourhoods returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_comparison",
            new=AsyncMock(return_value=(SAMPLE_NEIGHBOURHOOD_COMPARISON, False)),
        ):
            result = await tools.toronto_compare_neighbourhoods(characteristic="Median household income")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_compare_neighbourhoods returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_comparison",
            new=AsyncMock(side_effect=Exception("fetch failed")),
        ):
            result = await tools.toronto_compare_neighbourhoods(characteristic="Population, 2016")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_neighbourhood_comparison",
            new=AsyncMock(return_value=(SAMPLE_NEIGHBOURHOOD_COMPARISON, False)),
        ):
            result = await tools.toronto_compare_neighbourhoods(characteristic="Population, 2016", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_compare_neighbourhoods.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 10: toronto_get_311_requests
# ---------------------------------------------------------------------------


class TestTorontoGet311Requests:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_311_requests returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_311_requests",
            new=AsyncMock(return_value=(SAMPLE_311_REQUESTS, False)),
        ):
            result = await tools.toronto_get_311_requests(year=2024)

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_not_found_when_year_zip_missing(self):
        """toronto_get_311_requests returns NOT_FOUND when year ZIP not found."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_311_requests",
            new=AsyncMock(side_effect=make_http_error(404)),
        ):
            result = await tools.toronto_get_311_requests(year=1999)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_311_requests returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_311_requests",
            new=AsyncMock(side_effect=Exception("fetch failed")),
        ):
            result = await tools.toronto_get_311_requests(year=2024)

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_311_requests",
            new=AsyncMock(return_value=(SAMPLE_311_REQUESTS, False)),
        ):
            result = await tools.toronto_get_311_requests(year=2024, lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_311_requests.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 11: toronto_get_rentsafe_evaluations
# ---------------------------------------------------------------------------


class TestTorontoGetRentsafeEvaluations:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_rentsafe_evaluations returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_rentsafe_evaluations",
            new=AsyncMock(return_value=(SAMPLE_RENTSAFE, False)),
        ):
            result = await tools.toronto_get_rentsafe_evaluations()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_rentsafe_evaluations returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_rentsafe_evaluations",
            new=AsyncMock(side_effect=Exception("fetch failed")),
        ):
            result = await tools.toronto_get_rentsafe_evaluations()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_rentsafe_evaluations",
            new=AsyncMock(return_value=(SAMPLE_RENTSAFE, True)),
        ):
            result = await tools.toronto_get_rentsafe_evaluations(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_rentsafe_evaluations.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 12: toronto_get_short_term_rentals
# ---------------------------------------------------------------------------


class TestTorontoGetShortTermRentals:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """toronto_get_short_term_rentals returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_short_term_rentals",
            new=AsyncMock(return_value=(SAMPLE_SHORT_TERM_RENTALS, False)),
        ):
            result = await tools.toronto_get_short_term_rentals()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_generic_exception(self):
        """toronto_get_short_term_rentals returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_short_term_rentals",
            new=AsyncMock(side_effect=Exception("fetch failed")),
        ):
            result = await tools.toronto_get_short_term_rentals()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.toronto.tools.fetch_short_term_rentals",
            new=AsyncMock(return_value=(SAMPLE_SHORT_TERM_RENTALS, False)),
        ):
            result = await tools.toronto_get_short_term_rentals(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.toronto_get_short_term_rentals.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc
