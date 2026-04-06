"""Unit tests for marine weather client functions.

Tests:
- fetch_marine_forecast: flattens nested structure, returns (list[dict], bool)
- fetch_hurricane_tracks: returns empty list for off-season, tracks with data
- fetch_thunderstorm_outlook: returns empty with message when no features
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_client():
    import mcp_canada.modules.weather.marine.client as client_mod
    return client_mod


# ===========================================================================
# 1. fetch_marine_forecast
# ===========================================================================

class TestFetchMarineForecast:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool_tuple(self, sample_marine_feature):
        """fetch_marine_forecast returns (list[dict], bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_marine_feature], 1, False)
            result, cached = await client.fetch_marine_forecast()

        assert isinstance(result, list)
        assert isinstance(cached, bool)

    @pytest.mark.asyncio
    async def test_flattens_nested_structure(self, sample_marine_feature):
        """fetch_marine_forecast flattens nested bilingual structure (Pitfall 6)."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_marine_feature], 1, False)
            result, _ = await client.fetch_marine_forecast()

        assert len(result) == 1
        item = result[0]
        # Flat fields must be present
        assert "area_en" in item
        assert "area_fr" in item
        # Nested dicts must NOT be in the flattened output
        assert "regularForecast" not in item
        assert "waveForecast" not in item

    @pytest.mark.asyncio
    async def test_flattened_item_has_expected_keys(self, sample_marine_feature):
        """Flattened marine forecast item has area, forecast, and warnings fields."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_marine_feature], 1, False)
            result, _ = await client.fetch_marine_forecast()

        item = result[0]
        assert item["area_en"] == "Northumberland Strait"
        assert item["area_fr"] == "Détroit de Northumberland"
        assert "forecast_text_en" in item
        assert "forecast_text_fr" in item
        assert "warnings_count" in item

    @pytest.mark.asyncio
    async def test_with_province_uses_bbox(self, sample_marine_feature):
        """fetch_marine_forecast with province= passes bbox to ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_marine_feature], 1, False)
            await client.fetch_marine_forecast(province="NS")

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None

    @pytest.mark.asyncio
    async def test_with_lat_lon_uses_bbox(self, sample_marine_feature):
        """fetch_marine_forecast with lat/lon passes bbox to ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_marine_feature], 1, False)
            await client.fetch_marine_forecast(lat=44.8, lon=-63.5)

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None

    @pytest.mark.asyncio
    async def test_empty_features_returns_empty_list(self):
        """fetch_marine_forecast with no features returns empty list."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, _ = await client.fetch_marine_forecast()

        assert result == []


# ===========================================================================
# 2. fetch_hurricane_tracks
# ===========================================================================

class TestFetchHurricaneTracks:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool_tuple(self, sample_hurricane_feature):
        """fetch_hurricane_tracks returns (list[dict], bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_hurricane_feature], 1, False)
            result, cached = await client.fetch_hurricane_tracks()

        assert isinstance(result, list)
        assert isinstance(cached, bool)

    @pytest.mark.asyncio
    async def test_returns_empty_list_off_season(self):
        """fetch_hurricane_tracks returns ([], False) when no active tracks (Pitfall 7)."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, cached = await client.fetch_hurricane_tracks()

        assert result == []
        assert cached is False

    @pytest.mark.asyncio
    async def test_returns_track_data_when_present(self, sample_hurricane_feature):
        """fetch_hurricane_tracks returns features when active storm data exists."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_hurricane_feature], 1, False)
            result, _ = await client.fetch_hurricane_tracks()

        assert len(result) == 1


# ===========================================================================
# 3. fetch_thunderstorm_outlook
# ===========================================================================

class TestFetchThunderstormOutlook:

    @pytest.mark.asyncio
    async def test_returns_list_and_bool_tuple(self, sample_thunderstorm_feature):
        """fetch_thunderstorm_outlook returns (list[dict], bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_thunderstorm_feature], 1, False)
            result, cached = await client.fetch_thunderstorm_outlook()

        assert isinstance(result, list)
        assert isinstance(cached, bool)

    @pytest.mark.asyncio
    async def test_returns_empty_list_off_season(self):
        """fetch_thunderstorm_outlook returns ([], False) when no features."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, cached = await client.fetch_thunderstorm_outlook()

        assert result == []
        assert cached is False

    @pytest.mark.asyncio
    async def test_with_province_uses_bbox(self, sample_thunderstorm_feature):
        """fetch_thunderstorm_outlook with province= passes bbox to ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.marine.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_thunderstorm_feature], 1, False)
            await client.fetch_thunderstorm_outlook(province="ON")

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None
