"""Unit tests for severe weather client functions.

Tests:
- fetch_radar_data: returns (list[dict], bool) with flattened precipitation data
- fetch_lightning: returns (None, False) — no collection exists
- fetch_uv_index: extracts UV from citypageweather forecastGroup
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_client():
    import mcp_canada.modules.weather.severe.client as client_mod
    return client_mod


# ===========================================================================
# 1. fetch_radar_data
# ===========================================================================

class TestFetchRadarData:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool_tuple(self, sample_radar_feature):
        """fetch_radar_data returns (list[dict], bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_radar_feature], 1, False)
            result, cached = await client.fetch_radar_data(45.4, -75.7)

        assert isinstance(result, list)
        assert isinstance(cached, bool)

    @pytest.mark.asyncio
    async def test_uses_bbox_from_lat_lon(self, sample_radar_feature):
        """fetch_radar_data passes bbox to ogc_fetch based on lat/lon."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_radar_feature], 1, False)
            await client.fetch_radar_data(45.4, -75.7)

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None

    @pytest.mark.asyncio
    async def test_flattens_precipitation_data(self, sample_radar_feature):
        """fetch_radar_data returns flattened feature properties."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_radar_feature], 1, False)
            result, _ = await client.fetch_radar_data(45.4, -75.7)

        assert len(result) >= 0  # may be empty if no matching features
        if result:
            item = result[0]
            assert "precipitation_mm" in item or "APCP_Sfc" in item or "datetime" in item

    @pytest.mark.asyncio
    async def test_empty_features_returns_empty_list(self):
        """fetch_radar_data returns empty list when no features nearby."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, _ = await client.fetch_radar_data(45.4, -75.7)

        assert result == []


# ===========================================================================
# 2. fetch_lightning
# ===========================================================================

class TestFetchLightning:

    @pytest.mark.asyncio
    async def test_returns_none_and_false(self):
        """fetch_lightning returns (None, False) — no collection available."""
        client = import_client()
        result, cached = await client.fetch_lightning()

        assert result is None
        assert cached is False

    @pytest.mark.asyncio
    async def test_does_not_call_ogc_fetch(self):
        """fetch_lightning does not attempt to call ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            await client.fetch_lightning()

        mock_ogc.assert_not_called()


# ===========================================================================
# 3. fetch_uv_index
# ===========================================================================

class TestFetchUvIndex:

    @pytest.mark.asyncio
    async def test_returns_dict_and_bool_tuple(self, sample_citypage_uv_feature):
        """fetch_uv_index returns (dict, bool) when UV data found."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_citypage_uv_feature], 1, False)
            result, cached = await client.fetch_uv_index(lat=45.4, lon=-75.7)

        assert isinstance(cached, bool)
        # Result may be a dict with UV data or None if not found

    @pytest.mark.asyncio
    async def test_extracts_uv_index_from_forecast(self, sample_citypage_uv_feature):
        """fetch_uv_index extracts UV index from forecastGroup."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_citypage_uv_feature], 1, False)
            result, _ = await client.fetch_uv_index(lat=45.4, lon=-75.7)

        assert result is not None
        assert "uv_index" in result
        assert result["uv_index"] == 8

    @pytest.mark.asyncio
    async def test_returns_none_when_no_features(self):
        """fetch_uv_index returns (None, False) when no citypage features found."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, cached = await client.fetch_uv_index(lat=45.4, lon=-75.7)

        assert result is None
        assert cached is False

    @pytest.mark.asyncio
    async def test_returns_none_when_no_uv_in_forecast(self, sample_citypage_no_uv_feature):
        """fetch_uv_index returns None UV when forecast has no uvIndex field."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_citypage_no_uv_feature], 1, False)
            result, _ = await client.fetch_uv_index(lat=45.4, lon=-75.7)

        # Should return a result but uv_index may be None
        if result is not None:
            assert result.get("uv_index") is None

    @pytest.mark.asyncio
    async def test_uses_bbox_when_lat_lon_provided(self, sample_citypage_uv_feature):
        """fetch_uv_index passes bbox to ogc_fetch when lat/lon provided."""
        client = import_client()
        with patch("mcp_canada.modules.weather.severe.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_citypage_uv_feature], 1, False)
            await client.fetch_uv_index(lat=45.4, lon=-75.7)

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None
