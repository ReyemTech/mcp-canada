"""Unit tests for Ontario Open Data client functions.

Tests cover:
- _truncate: short/long strings, None handling
- _limit_resources: caps at max_count
- _shape_dataset: bilingual extraction with fallback, truncation, resource limiting
- _shape_resource: field extraction
- CKAN envelope unwrapping (_api_get returns result key)
- fetch_dataset_count: returns count from result.count
- fetch_population_projections: delegates to fetch_and_parse with correct URL
- _build_cache_key: deterministic with 'ontario:' prefix
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_canada.modules.ontario.client import (
    _truncate,
    _limit_resources,
    _shape_dataset,
    _shape_resource,
    _build_cache_key,
    fetch_search_datasets,
    fetch_dataset_details,
    fetch_organizations,
    fetch_resource,
    fetch_dataset_count,
    fetch_population_projections,
)
from mcp_canada.modules.ontario.__tests__.conftest import (
    LONG_DESCRIPTION,
    SAMPLE_ONT_DATASET_BILINGUAL,
    SAMPLE_ONT_DATASET_NO_TRANSLATION,
    SAMPLE_PACKAGE_SEARCH_RESPONSE,
    SAMPLE_PACKAGE_SHOW_RESPONSE,
    SAMPLE_ORGANIZATION_LIST_RESPONSE,
    SAMPLE_RESOURCE_SHOW_RESPONSE,
    SAMPLE_DATASET_COUNT_RESPONSE,
    SAMPLE_POPULATION_ROWS,
)


# ===========================================================================
# _truncate
# ===========================================================================

class TestTruncate:

    def test_short_string_not_truncated(self):
        """Strings under max_chars are returned unchanged."""
        text = "Short description."
        result = _truncate(text)
        assert result == text
        assert not result.endswith("...")

    def test_long_string_truncated_at_500(self):
        """Strings over 500 chars are truncated with '...' suffix."""
        result = _truncate(LONG_DESCRIPTION)
        assert result is not None
        assert len(result) <= 503  # 500 + len("...")
        assert result.endswith("...")

    def test_long_string_truncated_at_custom_limit(self):
        """Custom max_chars is respected."""
        text = "A" * 200
        result = _truncate(text, max_chars=100)
        assert result is not None
        assert len(result) == 103  # 100 chars + "..."
        assert result.endswith("...")

    def test_exactly_at_limit_not_truncated(self):
        """String exactly at limit is NOT truncated."""
        text = "A" * 500
        result = _truncate(text)
        assert result is not None
        assert result == text
        assert not result.endswith("...")

    def test_one_over_limit_truncated(self):
        """String one char over limit IS truncated."""
        text = "A" * 501
        result = _truncate(text)
        assert result is not None
        assert result.endswith("...")

    def test_none_returns_none(self):
        """None input returns None."""
        result = _truncate(None)
        assert result is None

    def test_empty_string_returns_empty(self):
        """Empty string returns empty string."""
        result = _truncate("")
        assert result == ""


# ===========================================================================
# _limit_resources
# ===========================================================================

class TestLimitResources:

    def test_list_under_max_unchanged(self):
        """Lists with fewer resources than max are returned as-is."""
        resources = [{"id": f"r{i}"} for i in range(5)]
        result = _limit_resources(resources)
        assert len(result) == 5

    def test_list_at_max_unchanged(self):
        """Lists with exactly max resources are returned unchanged."""
        resources = [{"id": f"r{i}"} for i in range(10)]
        result = _limit_resources(resources)
        assert len(result) == 10

    def test_list_over_max_capped(self):
        """Lists with more than max resources are capped at max."""
        resources = [{"id": f"r{i}"} for i in range(15)]
        result = _limit_resources(resources)
        assert len(result) == 10

    def test_custom_max_count_respected(self):
        """Custom max_count is used instead of default."""
        resources = [{"id": f"r{i}"} for i in range(20)]
        result = _limit_resources(resources, max_count=5)
        assert len(result) == 5

    def test_first_n_items_preserved(self):
        """Capping returns the FIRST N items, not random."""
        resources = [{"id": f"r{i}"} for i in range(15)]
        result = _limit_resources(resources, max_count=3)
        assert result[0]["id"] == "r0"
        assert result[1]["id"] == "r1"
        assert result[2]["id"] == "r2"

    def test_empty_list_returns_empty(self):
        """Empty list returns empty list."""
        result = _limit_resources([])
        assert result == []


# ===========================================================================
# _shape_dataset
# ===========================================================================

class TestShapeDataset:

    def test_bilingual_en_extraction(self):
        """English title and description extracted from title_translated/notes_translated."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert result["title"] == "Population projections"
        assert result["description"] is not None
        # Description should be truncated (long text)
        assert result["description"].endswith("...")

    def test_bilingual_fr_extraction(self):
        """French title and description extracted when lang='fr'."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="fr")
        assert result["title"] == "Projections demographiques"
        assert result["description"] == "Projections de la population de l'Ontario par région et groupe d'âge."

    def test_fallback_to_en_when_fr_missing(self):
        """Falls back to 'en' when requested language not in title_translated."""
        raw = dict(SAMPLE_ONT_DATASET_BILINGUAL)
        raw["title_translated"] = {"en": "English Only Title"}
        result = _shape_dataset(raw, lang="fr")
        assert result["title"] == "English Only Title"

    def test_fallback_to_raw_title_when_no_translation(self):
        """Falls back to raw 'title' field when title_translated is absent."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_NO_TRANSLATION, lang="en")
        assert result["title"] == "Simple Ontario Dataset"

    def test_resources_capped_at_10(self):
        """Resources are limited to first 10 even when dataset has 15."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert len(result["resources"]) == 10

    def test_num_resources_shows_total_count(self):
        """num_resources reflects the TOTAL count before limiting."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert result["num_resources"] == 15  # total, not capped count

    def test_id_name_org_included(self):
        """id, name, and organization are included in shaped result."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert result["id"] == "f52a6457-fb37-4267-acde-11a1e57c4dc8"
        assert result["name"] == "population-projections"
        assert result["organization"] == {"name": "finance", "title": "Finance"}

    def test_tags_included(self):
        """tags list is included in shaped result."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert result["tags"] == [{"name": "population"}, {"name": "projections"}]

    def test_metadata_timestamps_included(self):
        """metadata_created and metadata_modified are included."""
        result = _shape_dataset(SAMPLE_ONT_DATASET_BILINGUAL, lang="en")
        assert result["metadata_created"] == "2020-01-01T00:00:00.000000"
        assert result["metadata_modified"] == "2025-08-01T00:00:00.000000"


# ===========================================================================
# _shape_resource
# ===========================================================================

class TestShapeResource:

    def test_resource_fields_extracted(self):
        """id, name, format, size, url fields are extracted."""
        raw = {
            "id": "res-001",
            "name": "Main XLSX",
            "format": "XLSX",
            "size": 244000,
            "url": "https://data.ontario.ca/file.xlsx",
            "description": "An XLSX file.",
            "extra_field": "ignored",
        }
        result = _shape_resource(raw)
        assert result["id"] == "res-001"
        assert result["name"] == "Main XLSX"
        assert result["format"] == "XLSX"
        assert result["size"] == 244000
        assert result["url"] == "https://data.ontario.ca/file.xlsx"

    def test_missing_fields_are_none(self):
        """Missing fields default to None."""
        result = _shape_resource({"id": "r1"})
        assert result["name"] is None
        assert result["format"] is None
        assert result["size"] is None
        assert result["url"] is None


# ===========================================================================
# _build_cache_key
# ===========================================================================

class TestBuildCacheKey:

    def test_cache_key_has_ontario_prefix(self):
        """Cache key starts with 'ontario:' prefix."""
        key = _build_cache_key("action/package_search", {"q": "population"})
        assert key.startswith("ontario:")

    def test_cache_key_includes_path(self):
        """Cache key includes the path."""
        key = _build_cache_key("action/package_search", {})
        assert "action/package_search" in key

    def test_params_sorted_for_determinism(self):
        """Same params in different order produce the same key."""
        key1 = _build_cache_key("path", {"b": "2", "a": "1"})
        key2 = _build_cache_key("path", {"a": "1", "b": "2"})
        assert key1 == key2

    def test_different_prefix_from_ckan(self):
        """Ontario cache key is distinct from ckan module keys."""
        key = _build_cache_key("action/package_search", {"q": "water"})
        assert not key.startswith("ckan:")


# ===========================================================================
# fetch_search_datasets
# ===========================================================================

class TestFetchSearchDatasets:

    @pytest.mark.asyncio
    async def test_returns_shaped_dataset_list(self):
        """fetch_search_datasets returns (list[dict], bool) tuple."""
        search_result = SAMPLE_PACKAGE_SEARCH_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return search_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            result = await fetch_search_datasets("population")

        data, was_cached = result
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "population-projections"
        assert data[0]["title"] == "Population projections"

    @pytest.mark.asyncio
    async def test_fr_lang_extracts_french_fields(self):
        """fetch_search_datasets with lang='fr' extracts French title/description."""
        search_result = SAMPLE_PACKAGE_SEARCH_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return search_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            data, _ = await fetch_search_datasets("population", lang="fr")

        assert data[0]["title"] == "Projections demographiques"


# ===========================================================================
# fetch_dataset_details
# ===========================================================================

class TestFetchDatasetDetails:

    @pytest.mark.asyncio
    async def test_returns_shaped_dataset(self):
        """fetch_dataset_details returns (dict, bool) for a valid dataset."""
        dataset_result = SAMPLE_PACKAGE_SHOW_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return dataset_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            result = await fetch_dataset_details("population-projections")

        data, was_cached = result
        assert isinstance(data, dict)
        assert data["id"] == "f52a6457-fb37-4267-acde-11a1e57c4dc8"

    @pytest.mark.asyncio
    async def test_raises_on_404(self):
        """fetch_dataset_details raises httpx.HTTPStatusError on 404."""
        import httpx as _httpx

        async def fake_cached_fetch(key, ttl, fetcher):
            return await fetcher()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("mcp_canada.modules.ontario.client.cached_fetch",
                       side_effect=fake_cached_fetch):
                with pytest.raises(_httpx.HTTPStatusError):
                    await fetch_dataset_details("nonexistent-dataset")


# ===========================================================================
# fetch_organizations
# ===========================================================================

class TestFetchOrganizations:

    @pytest.mark.asyncio
    async def test_returns_org_list(self):
        """fetch_organizations returns (list[dict], bool) tuple."""
        org_result = SAMPLE_ORGANIZATION_LIST_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return org_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            result = await fetch_organizations()

        data, was_cached = result
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "finance"
        assert data[0]["package_count"] == 42


# ===========================================================================
# fetch_resource
# ===========================================================================

class TestFetchResource:

    @pytest.mark.asyncio
    async def test_returns_shaped_resource(self):
        """fetch_resource returns (dict, bool) with shaped fields."""
        resource_result = SAMPLE_RESOURCE_SHOW_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return resource_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            result = await fetch_resource("31376797-1e4c-4426-ba75-0d93f4bb9f45")

        data, was_cached = result
        assert isinstance(data, dict)
        assert data["id"] == "31376797-1e4c-4426-ba75-0d93f4bb9f45"
        assert data["format"] == "XLSX"

    @pytest.mark.asyncio
    async def test_raises_on_404(self):
        """fetch_resource raises httpx.HTTPStatusError on 404."""
        import httpx as _httpx

        async def fake_cached_fetch(key, ttl, fetcher):
            return await fetcher()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("mcp_canada.modules.ontario.client.cached_fetch",
                       side_effect=fake_cached_fetch):
                with pytest.raises(_httpx.HTTPStatusError):
                    await fetch_resource("nonexistent-uuid")


# ===========================================================================
# fetch_dataset_count
# ===========================================================================

class TestFetchDatasetCount:

    @pytest.mark.asyncio
    async def test_returns_count_int(self):
        """fetch_dataset_count returns (int, bool) tuple."""
        count_result = SAMPLE_DATASET_COUNT_RESPONSE["result"]

        async def fake_cached_fetch(key, ttl, fetcher):
            return count_result, False

        with patch("mcp_canada.modules.ontario.client.cached_fetch",
                   side_effect=fake_cached_fetch):
            result = await fetch_dataset_count()

        count, was_cached = result
        assert isinstance(count, int)
        assert count == 2946


# ===========================================================================
# fetch_population_projections
# ===========================================================================

class TestFetchPopulationProjections:

    @pytest.mark.asyncio
    async def test_delegates_to_fetch_and_parse(self):
        """fetch_population_projections calls fetch_and_parse with XLSX URL."""
        from mcp_canada.modules.ontario.constants import POPULATION_PROJECTIONS_RESOURCE_URL

        with patch("mcp_canada.modules.ontario.client.fetch_and_parse",
                   new_callable=AsyncMock,
                   return_value=(SAMPLE_POPULATION_ROWS, False)) as mock_parse:
            data, was_cached = await fetch_population_projections()

        assert data == SAMPLE_POPULATION_ROWS
        assert was_cached is False
        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        # First positional arg is the URL
        assert call_args[0][0] == POPULATION_PROJECTIONS_RESOURCE_URL

    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self):
        """fetch_population_projections returns (list[dict], bool)."""
        with patch("mcp_canada.modules.ontario.client.fetch_and_parse",
                   new_callable=AsyncMock,
                   return_value=(SAMPLE_POPULATION_ROWS, True)):
            data, was_cached = await fetch_population_projections()

        assert isinstance(data, list)
        assert was_cached is True

    @pytest.mark.asyncio
    async def test_passes_correct_ttl(self):
        """fetch_population_projections uses CACHE_TTL_DATA for TTL."""
        from mcp_canada.modules.ontario.constants import CACHE_TTL_DATA

        with patch("mcp_canada.modules.ontario.client.fetch_and_parse",
                   new_callable=AsyncMock,
                   return_value=(SAMPLE_POPULATION_ROWS, False)) as mock_parse:
            await fetch_population_projections()

        call_kwargs = mock_parse.call_args[1]
        assert call_kwargs.get("ttl") == CACHE_TTL_DATA
