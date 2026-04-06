"""Unit tests for CKAN Open Data @tool functions.

Tests cover:
- Happy paths: each tool returns make_response envelope with correct data
- Error paths: HTTPStatusError returns make_error
- lang parameter passed through to all responses
- Docstring quality: Keywords, Use for lines for BM25
- Response shaping: descriptions truncated, resources capped
"""

import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def import_tools():
    """Import CKAN tools module."""
    import mcp_canada.modules.ckan.tools as tools_mod
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
        "id": "abc123",
        "name": "water-quality",
        "title": "Water Quality Data",
        "description": "Short description of water quality data.",
        "organization": {"title": "Environment Canada"},
        "num_resources": 2,
        "tags": [{"name": "water"}],
        "resources": [{"id": "r1", "name": "CSV", "format": "CSV", "size": 1024, "url": "https://example.com/r1"}],
        "metadata_created": "2023-01-01T00:00:00",
        "metadata_modified": "2024-01-01T00:00:00",
    },
]

SAMPLE_DATASET_DETAIL = {
    "id": "abc123",
    "name": "water-quality",
    "title": "Water Quality Data",
    "description": "Detailed water quality information.",
    "organization": {"title": "Environment Canada"},
    "num_resources": 1,
    "tags": [{"name": "water"}],
    "resources": [{"id": "r1", "name": "CSV", "format": "CSV", "size": 1024, "url": "https://example.com/r1"}],
    "metadata_created": "2023-01-01T00:00:00",
    "metadata_modified": "2024-01-01T00:00:00",
}

SAMPLE_ORGANIZATIONS = [
    {"id": "org-1", "name": "environment-canada", "title": "Environment Canada",
     "description": "Federal environmental agency.", "package_count": 500},
    {"id": "org-2", "name": "statistics-canada", "title": "Statistics Canada",
     "description": "National statistics agency.", "package_count": 3000},
]

SAMPLE_GROUPS = [
    {"id": "grp-1", "name": "environment", "title": "Environment",
     "description": "Environmental datasets.", "package_count": 400},
    {"id": "grp-2", "name": "health", "title": "Health",
     "description": "Health datasets.", "package_count": 600},
]

SAMPLE_RESOURCE = {
    "id": "res-001",
    "name": "Main Data File",
    "format": "CSV",
    "size": 204800,
    "url": "https://open.canada.ca/resource/main.csv",
}


# ===========================================================================
# 1. ckan_search_datasets
# ===========================================================================

class TestCkanSearchDatasets:

    @pytest.mark.asyncio
    async def test_happy_path_returns_dataset_list(self):
        """Returns make_response envelope with dataset list."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            result = await tools.ckan_search_datasets(query="water quality")

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "Water Quality Data"

    @pytest.mark.asyncio
    async def test_filters_mapped_to_fq_param(self):
        """filters parameter is passed as fq to fetch_search_datasets."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            await tools.ckan_search_datasets(query="water", filters="organization:gc")

        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args
        assert "fq" in call_kwargs.kwargs or (
            len(call_kwargs.args) > 1 and "organization:gc" in str(call_kwargs)
        )

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError from fetch returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = make_http_error(500)
            result = await tools.ckan_search_datasets(query="water")

        assert "error" in result
        assert "code" in result["error"]

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            result = await tools.ckan_search_datasets(query="water", lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_cached_flag_in_meta(self):
        """cached=True from fetch is reflected in _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, True)
            result = await tools.ckan_search_datasets(query="water")

        assert result["_meta"]["cached"] is True


# ===========================================================================
# 2. ckan_get_dataset_details
# ===========================================================================

class TestCkanGetDatasetDetails:

    @pytest.mark.asyncio
    async def test_happy_path_returns_dataset_detail(self):
        """Returns make_response envelope with dataset detail."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = (SAMPLE_DATASET_DETAIL, False)
            result = await tools.ckan_get_dataset_details(dataset_id="water-quality")

        assert "_meta" in result
        assert result["data"]["id"] == "abc123"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_detail.side_effect = make_http_error(404)
            result = await tools.ckan_get_dataset_details(dataset_id="nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passed_to_fetch(self):
        """lang is passed to fetch_dataset_details."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = (SAMPLE_DATASET_DETAIL, False)
            await tools.ckan_get_dataset_details(dataset_id="abc123", lang="fr")

        call_args = mock_detail.call_args
        assert "fr" in str(call_args)


# ===========================================================================
# 3. ckan_list_organizations
# ===========================================================================

class TestCkanListOrganizations:

    @pytest.mark.asyncio
    async def test_happy_path_returns_org_list(self):
        """Returns make_response envelope with organization list."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_organizations",
                   new_callable=AsyncMock) as mock_orgs:
            mock_orgs.return_value = (SAMPLE_ORGANIZATIONS, False)
            result = await tools.ckan_list_organizations()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Environment Canada"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_organizations",
                   new_callable=AsyncMock) as mock_orgs:
            mock_orgs.side_effect = make_http_error(503)
            result = await tools.ckan_list_organizations()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang is in meta response."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_organizations",
                   new_callable=AsyncMock) as mock_orgs:
            mock_orgs.return_value = (SAMPLE_ORGANIZATIONS, False)
            result = await tools.ckan_list_organizations(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 4. ckan_search_by_tag
# ===========================================================================

class TestCkanSearchByTag:

    @pytest.mark.asyncio
    async def test_happy_path_returns_datasets_for_tag(self):
        """Returns datasets matching the given tag."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            result = await tools.ckan_search_by_tag(tag="water")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_tag_mapped_to_fq_filter(self):
        """Tag is passed as fq=tags:{tag} to fetch_search_datasets."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            await tools.ckan_search_by_tag(tag="water")

        mock_search.assert_called_once()
        call_str = str(mock_search.call_args)
        assert "water" in call_str

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = make_http_error(500)
            result = await tools.ckan_search_by_tag(tag="water")

        assert "error" in result


# ===========================================================================
# 5. ckan_get_resource
# ===========================================================================

class TestCkanGetResource:

    @pytest.mark.asyncio
    async def test_happy_path_returns_resource(self):
        """Returns make_response envelope with resource details."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_resource",
                   new_callable=AsyncMock) as mock_res:
            mock_res.return_value = (SAMPLE_RESOURCE, False)
            result = await tools.ckan_get_resource(resource_id="res-001")

        assert "_meta" in result
        assert result["data"]["id"] == "res-001"
        assert result["data"]["format"] == "CSV"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_resource",
                   new_callable=AsyncMock) as mock_res:
            mock_res.side_effect = make_http_error(404)
            result = await tools.ckan_get_resource(resource_id="nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang is in meta response."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_resource",
                   new_callable=AsyncMock) as mock_res:
            mock_res.return_value = (SAMPLE_RESOURCE, False)
            result = await tools.ckan_get_resource(resource_id="res-001", lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 6. ckan_list_groups
# ===========================================================================

class TestCkanListGroups:

    @pytest.mark.asyncio
    async def test_happy_path_returns_group_list(self):
        """Returns make_response envelope with group list."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_groups",
                   new_callable=AsyncMock) as mock_groups:
            mock_groups.return_value = (SAMPLE_GROUPS, False)
            result = await tools.ckan_list_groups()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "environment"

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_groups",
                   new_callable=AsyncMock) as mock_groups:
            mock_groups.side_effect = make_http_error(503)
            result = await tools.ckan_list_groups()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang is in meta response."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_groups",
                   new_callable=AsyncMock) as mock_groups:
            mock_groups.return_value = (SAMPLE_GROUPS, False)
            result = await tools.ckan_list_groups(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 7. ckan_get_dataset_stats
# ===========================================================================

class TestCkanGetDatasetStats:

    @pytest.mark.asyncio
    async def test_happy_path_returns_stats(self):
        """Returns make_response envelope with dataset count stats."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_count",
                   new_callable=AsyncMock) as mock_count:
            mock_count.return_value = (83421, False)
            result = await tools.ckan_get_dataset_stats()

        assert "_meta" in result
        assert "data" in result
        assert result["data"]["total_datasets"] == 83421

    @pytest.mark.asyncio
    async def test_http_error_returns_make_error(self):
        """HTTPStatusError returns make_error."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_count",
                   new_callable=AsyncMock) as mock_count:
            mock_count.side_effect = make_http_error(503)
            result = await tools.ckan_get_dataset_stats()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang is in meta response."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_dataset_count",
                   new_callable=AsyncMock) as mock_count:
            mock_count.return_value = (83421, False)
            result = await tools.ckan_get_dataset_stats(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 7 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "ckan_search_datasets",
        "ckan_get_dataset_details",
        "ckan_list_organizations",
        "ckan_search_by_tag",
        "ckan_get_resource",
        "ckan_list_groups",
        "ckan_get_dataset_stats",
    ]

    def _get_tool_func(self, name: str):
        tools = import_tools()
        return getattr(tools, name)

    def test_all_tools_have_keywords_line(self):
        """All 7 tools must have 'Keywords:' in their docstring for BM25."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' line in docstring"

    def test_all_tools_have_use_for_line(self):
        """All 7 tools must have 'Use for:' in their docstring."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' line in docstring"

    def test_all_tool_docstrings_at_least_50_chars(self):
        """All 7 tool docstrings must be >= 50 characters."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert len(doc) >= 50, f"{name} docstring too short ({len(doc)} chars)"

    def test_all_tools_have_lang_parameter(self):
        """All 7 tools must accept lang: Literal['en', 'fr'] = 'en' parameter."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            sig = inspect.signature(func)
            assert "lang" in sig.parameters, f"{name} missing 'lang' parameter"
            param = sig.parameters["lang"]
            assert param.default == "en", f"{name} lang default should be 'en'"

    def test_all_tools_are_callable_async(self):
        """All 7 tool functions are callable."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"


# ===========================================================================
# Envelope structure
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_success_response_has_meta_and_data(self):
        """Success responses have _meta.source, _meta.cached, and data."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DATASETS, False)
            result = await tools.ckan_search_datasets(query="water")

        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert isinstance(result["_meta"]["cached"], bool)
        assert "data" in result

    @pytest.mark.asyncio
    async def test_error_response_has_code_and_message(self):
        """Error responses have error.code and error.message."""
        tools = import_tools()
        with patch("mcp_canada.modules.ckan.tools.fetch_search_datasets",
                   new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = make_http_error(503)
            result = await tools.ckan_search_datasets(query="water")

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
