"""Unit tests for weather/collections client functions."""

import pytest
from unittest.mock import AsyncMock, patch


class TestFetchCollections:
    """Tests for fetch_collections()."""

    @pytest.mark.asyncio
    async def test_returns_list_of_collections(self, sample_collections_response):
        """fetch_collections returns a list of {id, title, description} dicts."""
        from mcp_canada.modules.weather.collections.client import fetch_collections

        with patch(
            "mcp_canada.modules.weather.collections.client.cached_fetch",
            new_callable=AsyncMock,
        ) as mock_cache:
            mock_cache.return_value = (sample_collections_response, False)
            result, was_cached = await fetch_collections()

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["id"] == "climate-stations"
        assert result[0]["title"] == "Climate Stations"
        assert "description" in result[0]

    @pytest.mark.asyncio
    async def test_returns_was_cached_flag(self, sample_collections_response):
        """fetch_collections returns (list, was_cached) tuple."""
        from mcp_canada.modules.weather.collections.client import fetch_collections

        with patch(
            "mcp_canada.modules.weather.collections.client.cached_fetch",
            new_callable=AsyncMock,
        ) as mock_cache:
            mock_cache.return_value = (sample_collections_response, True)
            result, was_cached = await fetch_collections()

        assert was_cached is True

    @pytest.mark.asyncio
    async def test_handles_empty_response(self):
        """fetch_collections returns empty list when API returns no collections."""
        from mcp_canada.modules.weather.collections.client import fetch_collections

        with patch(
            "mcp_canada.modules.weather.collections.client.cached_fetch",
            new_callable=AsyncMock,
        ) as mock_cache:
            mock_cache.return_value = ({"collections": []}, False)
            result, was_cached = await fetch_collections()

        assert result == []

    @pytest.mark.asyncio
    async def test_cache_key_uses_wx_collections(self, sample_collections_response):
        """fetch_collections uses 'wx:collections' cache key."""
        from mcp_canada.modules.weather.collections.client import fetch_collections

        with patch(
            "mcp_canada.modules.weather.collections.client.cached_fetch",
            new_callable=AsyncMock,
        ) as mock_cache:
            mock_cache.return_value = (sample_collections_response, False)
            await fetch_collections()

        call_args = mock_cache.call_args
        assert call_args[0][0] == "wx:collections"


class TestFetchCollectionItems:
    """Tests for fetch_collection_items()."""

    @pytest.mark.asyncio
    async def test_returns_features_with_centroid(self, sample_collection_items):
        """fetch_collection_items returns list of features with lat/lon from centroid."""
        from mcp_canada.modules.weather.collections.client import fetch_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = (sample_collection_items, 2, False)
            result, total, was_cached = await fetch_collection_items("climate-stations")

        assert isinstance(result, list)
        assert len(result) == 2
        # extract_centroid should add lat/lon to each item
        assert "lat" in result[0]
        assert "lon" in result[0]

    @pytest.mark.asyncio
    async def test_passes_collection_id_to_ogc_fetch(self, sample_collection_items):
        """fetch_collection_items passes collection_id to ogc_fetch."""
        from mcp_canada.modules.weather.collections.client import fetch_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = (sample_collection_items, 2, False)
            await fetch_collection_items("climate-stations")

        call_kwargs = mock_ogc.call_args
        assert call_kwargs[0][0] == "climate-stations"

    @pytest.mark.asyncio
    async def test_returns_total_count(self, sample_collection_items):
        """fetch_collection_items returns (items, total, was_cached) tuple."""
        from mcp_canada.modules.weather.collections.client import fetch_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = (sample_collection_items, 100, False)
            result, total, was_cached = await fetch_collection_items("climate-stations")

        assert total == 100

    @pytest.mark.asyncio
    async def test_passes_bbox_to_ogc_fetch(self):
        """fetch_collection_items passes bbox parameter to ogc_fetch."""
        from mcp_canada.modules.weather.collections.client import fetch_collection_items

        with patch(
            "mcp_canada.modules.weather.collections.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            await fetch_collection_items("climate-stations", bbox=(-76.0, 45.0, -75.0, 46.0))

        call_kwargs = mock_ogc.call_args[1]
        assert call_kwargs.get("bbox") == (-76.0, 45.0, -75.0, 46.0)
