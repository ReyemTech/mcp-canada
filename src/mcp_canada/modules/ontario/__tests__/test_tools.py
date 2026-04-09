"""Unit tests for Ontario Open Data @tool functions.

Tests cover:
- Happy paths: each tool returns make_response envelope with correct data
- Error paths: HTTPStatusError returns make_error
- lang parameter passed through to all responses
- Docstring quality: Keywords, Use for lines for BM25
- ontario_get_dataset_stats data shape (total_datasets, portal, api_version)
- NOT_FOUND on 404 for dataset/resource detail tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def import_tools():
    """Import Ontario tools module."""
    import mcp_canada.modules.ontario.tools as tools_mod
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
        "id": "f52a6457-fb37-4267-acde-11a1e57c4dc8",
        "name": "population-projections",
        "title": "Population projections",
        "description": "Ontario population projections by region.",
        "organization": {"name": "finance", "title": "Finance"},
        "num_resources": 2,
        "tags": [{"name": "population"}],
        "resources": [{"id": "r1", "name": "XLSX", "format": "XLSX", "size": 244000, "url": "https://data.ontario.ca/r1"}],
        "metadata_created": "2020-01-01T00:00:00",
        "metadata_modified": "2025-01-01T00:00:00",
    },
]

SAMPLE_DATASET_DETAIL = {
    "id": "f52a6457-fb37-4267-acde-11a1e57c4dc8",
    "name": "population-projections",
    "title": "Population projections",
    "description": "Detailed Ontario population projections.",
    "organization": {"name": "finance", "title": "Finance"},
    "num_resources": 1,
    "tags": [{"name": "population"}],
    "resources": [{"id": "r1", "name": "XLSX", "format": "XLSX", "size": 244000, "url": "https://data.ontario.ca/r1"}],
    "metadata_created": "2020-01-01T00:00:00",
    "metadata_modified": "2025-01-01T00:00:00",
}

SAMPLE_RESOURCE = {
    "id": "31376797-1e4c-4426-ba75-0d93f4bb9f45",
    "name": "ontario_mof_population_projections_for_2024-2051.xlsx",
    "format": "XLSX",
    "size": 244000,
    "url": "https://data.ontario.ca/download/file.xlsx",
}

SAMPLE_ORGANIZATIONS = [
    {"id": "org-1", "name": "finance", "title": "Finance", "description": "Ministry of Finance.", "package_count": 42},
    {"id": "org-2", "name": "health", "title": "Health", "description": "Ministry of Health.", "package_count": 115},
]

SAMPLE_POPULATION_ROWS = [
    {"geography": "Ontario", "year": 2024, "population": 15000000},
    {"geography": "Toronto", "year": 2024, "population": 3000000},
]


# ---------------------------------------------------------------------------
# Tool 1: ontario_search_datasets
# ---------------------------------------------------------------------------


class TestOntarioSearchDatasets:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """ontario_search_datasets returns _meta envelope with data key on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(SAMPLE_DATASETS, False)),
        ):
            result = await tools.ontario_search_datasets(query="population")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 1

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """ontario_search_datasets returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_search_datasets",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_search_datasets(query="population")

        assert "error" in result
        assert "code" in result["error"]

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_search_datasets",
            new=AsyncMock(return_value=(SAMPLE_DATASETS, False)),
        ):
            result = await tools.ontario_search_datasets(query="population", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_search_datasets.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 2: ontario_get_dataset_details
# ---------------------------------------------------------------------------


class TestOntarioGetDatasetDetails:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """ontario_get_dataset_details returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(SAMPLE_DATASET_DETAIL, False)),
        ):
            result = await tools.ontario_get_dataset_details(dataset_id="population-projections")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_not_found_on_404(self):
        """ontario_get_dataset_details returns NOT_FOUND error on 404."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_details",
            new=AsyncMock(side_effect=make_http_error(404)),
        ):
            result = await tools.ontario_get_dataset_details(dataset_id="nonexistent")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_500(self):
        """ontario_get_dataset_details returns UPSTREAM_ERROR on 500."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_details",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_get_dataset_details(dataset_id="some-id")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_details",
            new=AsyncMock(return_value=(SAMPLE_DATASET_DETAIL, True)),
        ):
            result = await tools.ontario_get_dataset_details(dataset_id="population-projections", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_get_dataset_details.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 3: ontario_get_resource
# ---------------------------------------------------------------------------


class TestOntarioGetResource:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """ontario_get_resource returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_resource",
            new=AsyncMock(return_value=(SAMPLE_RESOURCE, False)),
        ):
            result = await tools.ontario_get_resource(resource_id="31376797-1e4c-4426-ba75-0d93f4bb9f45")

        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_not_found_on_404(self):
        """ontario_get_resource returns NOT_FOUND error on 404."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_resource",
            new=AsyncMock(side_effect=make_http_error(404)),
        ):
            result = await tools.ontario_get_resource(resource_id="nonexistent-uuid")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_500(self):
        """ontario_get_resource returns UPSTREAM_ERROR on 500."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_resource",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_get_resource(resource_id="some-uuid")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_resource",
            new=AsyncMock(return_value=(SAMPLE_RESOURCE, False)),
        ):
            result = await tools.ontario_get_resource(resource_id="some-uuid", lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_get_resource.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 4: ontario_list_organizations
# ---------------------------------------------------------------------------


class TestOntarioListOrganizations:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """ontario_list_organizations returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_organizations",
            new=AsyncMock(return_value=(SAMPLE_ORGANIZATIONS, False)),
        ):
            result = await tools.ontario_list_organizations()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """ontario_list_organizations returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_organizations",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_list_organizations()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_organizations",
            new=AsyncMock(return_value=(SAMPLE_ORGANIZATIONS, False)),
        ):
            result = await tools.ontario_list_organizations(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_list_organizations.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 5: ontario_get_dataset_stats
# ---------------------------------------------------------------------------


class TestOntarioGetDatasetStats:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_with_stats(self):
        """ontario_get_dataset_stats returns _meta envelope with total_datasets."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(2946, False)),
        ):
            result = await tools.ontario_get_dataset_stats()

        assert "_meta" in result
        assert "data" in result
        assert "total_datasets" in result["data"]
        assert result["data"]["total_datasets"] == 2946

    @pytest.mark.asyncio
    async def test_stats_data_has_portal_and_api_version(self):
        """ontario_get_dataset_stats data contains portal and api_version."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(2946, False)),
        ):
            result = await tools.ontario_get_dataset_stats()

        assert result["data"]["portal"] == "data.ontario.ca"
        assert result["data"]["api_version"] == "CKAN 3"

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """ontario_get_dataset_stats returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_count",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_get_dataset_stats()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_dataset_count",
            new=AsyncMock(return_value=(2946, False)),
        ):
            result = await tools.ontario_get_dataset_stats(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_get_dataset_stats.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc


# ---------------------------------------------------------------------------
# Tool 6: ontario_get_population_projections
# ---------------------------------------------------------------------------


class TestOntarioGetPopulationProjections:

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """ontario_get_population_projections returns _meta envelope on success."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_population_projections",
            new=AsyncMock(return_value=(SAMPLE_POPULATION_ROWS, False)),
        ):
            result = await tools.ontario_get_population_projections()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_on_http_error(self):
        """ontario_get_population_projections returns error envelope on HTTPStatusError."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_population_projections",
            new=AsyncMock(side_effect=make_http_error(500)),
        ):
            result = await tools.ontario_get_population_projections()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter is passed through to the response envelope."""
        tools = import_tools()
        with patch(
            "mcp_canada.modules.ontario.tools.fetch_population_projections",
            new=AsyncMock(return_value=(SAMPLE_POPULATION_ROWS, False)),
        ):
            result = await tools.ontario_get_population_projections(lang="fr")

        assert "_meta" in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_docstring_quality(self):
        """Tools must have Use for: and Keywords: lines in docstrings."""
        tools = import_tools()
        doc = tools.ontario_get_population_projections.__doc__ or ""
        assert "Use for:" in doc
        assert "Keywords:" in doc
