"""Unit tests for AQHI client functions."""

import pytest
from unittest.mock import AsyncMock, patch



class TestFetchAqhi:
    """Tests for fetch_aqhi client function."""

    @pytest.mark.asyncio
    async def test_fetch_by_lat_lon_returns_flattened_readings(self, sample_aqhi_obs_feature):
        """fetch_aqhi(lat, lon) calls ogc_fetch with bbox and returns flat dicts."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, False)
            readings, cached = await fetch_aqhi(lat=45.4, lon=-75.7)

        assert cached is False
        assert len(readings) == 1
        r = readings[0]
        assert r["location_id"] == "ON106"
        assert r["location_name"] == "Ottawa"
        assert r["aqhi_value"] == 3.0
        assert r["lat"] == 45.4
        assert r["lon"] == -75.7
        # ogc_fetch called with bbox
        call_kwargs = mock_ogc.call_args.kwargs
        assert "bbox" in call_kwargs

    @pytest.mark.asyncio
    async def test_fetch_by_location_id_uses_property_filter(self, sample_aqhi_obs_feature):
        """fetch_aqhi(location_id=...) calls ogc_fetch with properties filter, no bbox."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, False)
            readings, cached = await fetch_aqhi(location_id="ON106")

        assert len(readings) == 1
        call_kwargs = mock_ogc.call_args.kwargs
        assert "bbox" not in call_kwargs
        assert call_kwargs.get("properties", {}).get("location_id") == "ON106"

    @pytest.mark.asyncio
    async def test_fetch_returns_cached_flag(self, sample_aqhi_obs_feature):
        """fetch_aqhi passes through the was_cached flag from ogc_fetch."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, True)
            _, cached = await fetch_aqhi(lat=45.4, lon=-75.7)

        assert cached is True

    @pytest.mark.asyncio
    async def test_fetch_empty_returns_empty_list(self):
        """fetch_aqhi returns empty list when ogc_fetch returns no features."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            readings, cached = await fetch_aqhi(lat=45.4, lon=-75.7)

        assert readings == []
        assert cached is False


class TestFetchAqhiForecast:
    """Tests for fetch_aqhi_forecast client function."""

    @pytest.mark.asyncio
    async def test_fetch_forecast_by_lat_lon(self, sample_aqhi_forecast_feature):
        """fetch_aqhi_forecast(lat, lon) returns flattened forecast readings."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi_forecast

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_forecast_feature], 1, False)
            readings, cached = await fetch_aqhi_forecast(lat=45.4, lon=-75.7)

        assert len(readings) == 1
        r = readings[0]
        assert r["location_id"] == "ON106"
        assert r["aqhi_value"] == 2.0

    @pytest.mark.asyncio
    async def test_fetch_forecast_by_location_id(self, sample_aqhi_forecast_feature):
        """fetch_aqhi_forecast(location_id=...) uses property filter."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi_forecast

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_forecast_feature], 1, False)
            readings, cached = await fetch_aqhi_forecast(location_id="ON106")

        call_kwargs = mock_ogc.call_args.kwargs
        assert call_kwargs.get("properties", {}).get("location_id") == "ON106"


class TestFetchAqhiHistory:
    """Tests for fetch_aqhi_history client function."""

    @pytest.mark.asyncio
    async def test_fetch_history_with_date_range(self, sample_aqhi_obs_feature):
        """fetch_aqhi_history passes datetime_filter when start/end dates provided."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, False)
            readings, cached = await fetch_aqhi_history(
                "ON106", start_date="2026-03-01", end_date="2026-03-31"
            )

        call_kwargs = mock_ogc.call_args.kwargs
        assert call_kwargs.get("datetime_filter") == "2026-03-01/2026-03-31"
        assert call_kwargs.get("properties", {}).get("location_id") == "ON106"

    @pytest.mark.asyncio
    async def test_fetch_history_no_dates(self, sample_aqhi_obs_feature):
        """fetch_aqhi_history without dates passes None datetime_filter."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, False)
            readings, _ = await fetch_aqhi_history("ON106")

        call_kwargs = mock_ogc.call_args.kwargs
        assert call_kwargs.get("datetime_filter") is None

    @pytest.mark.asyncio
    async def test_fetch_history_returns_flattened_readings(self, sample_aqhi_obs_feature):
        """fetch_aqhi_history returns correctly flattened readings."""
        from mcp_canada.modules.weather.aqhi.client import fetch_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_aqhi_obs_feature], 1, False)
            readings, _ = await fetch_aqhi_history("ON106")

        assert readings[0]["location_id"] == "ON106"
        assert readings[0]["aqhi_value"] == 3.0
