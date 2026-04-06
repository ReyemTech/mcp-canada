"""Unit tests for hydrometric client functions."""

import pytest
from unittest.mock import AsyncMock, patch



class TestFetchWaterLevels:
    """Tests for fetch_water_levels client function."""

    @pytest.mark.asyncio
    async def test_fetch_by_station_number(self, sample_hydro_realtime_feature):
        """fetch_water_levels(station_number=...) uses property filter."""
        from mcp_canada.modules.weather.hydro.client import fetch_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_realtime_feature], 1, False)
            readings, cached = await fetch_water_levels(station_number="02LA004")

        assert len(readings) == 1
        r = readings[0]
        assert r["station_number"] == "02LA004"
        assert r["station_name"] == "RIDEAU RIVER AT OTTAWA"
        assert r["level_m"] == 72.45
        assert r["discharge_m3s"] == 115.0
        assert r["lat"] == 45.3
        assert r["lon"] == -76.4
        call_kwargs = mock_ogc.call_args.kwargs
        assert call_kwargs.get("properties", {}).get("STATION_NUMBER") == "02LA004"

    @pytest.mark.asyncio
    async def test_fetch_by_lat_lon_uses_nearest_station(self, sample_hydro_realtime_feature, sample_hydro_station_feature):
        """fetch_water_levels(lat, lon) calls nearest_station then queries by station_number."""
        from mcp_canada.modules.weather.hydro.client import fetch_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.client.nearest_station",
            new_callable=AsyncMock,
        ) as mock_nearest, patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_nearest.return_value = sample_hydro_station_feature
            mock_ogc.return_value = ([sample_hydro_realtime_feature], 1, False)
            readings, cached = await fetch_water_levels(lat=45.3, lon=-76.4)

        assert len(readings) == 1
        mock_nearest.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fetch_returns_cached_flag(self, sample_hydro_realtime_feature):
        """fetch_water_levels passes through was_cached flag."""
        from mcp_canada.modules.weather.hydro.client import fetch_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_realtime_feature], 1, True)
            _, cached = await fetch_water_levels(station_number="02LA004")

        assert cached is True

    @pytest.mark.asyncio
    async def test_fetch_empty_returns_empty_list(self):
        """fetch_water_levels returns empty list when no features found."""
        from mcp_canada.modules.weather.hydro.client import fetch_water_levels

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            readings, _ = await fetch_water_levels(station_number="INVALID")

        assert readings == []


class TestFetchWaterFlow:
    """Tests for fetch_water_flow client function."""

    @pytest.mark.asyncio
    async def test_fetch_returns_discharge_data(self, sample_hydro_realtime_feature):
        """fetch_water_flow returns readings with discharge_m3s populated."""
        from mcp_canada.modules.weather.hydro.client import fetch_water_flow

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_realtime_feature], 1, False)
            readings, cached = await fetch_water_flow(station_number="02LA004")

        assert len(readings) == 1
        assert readings[0]["discharge_m3s"] == 115.0
        assert readings[0]["station_number"] == "02LA004"


class TestFetchDailyMeanWater:
    """Tests for fetch_daily_mean_water client function."""

    @pytest.mark.asyncio
    async def test_fetch_with_date_range(self, sample_hydro_daily_feature):
        """fetch_daily_mean_water passes datetime_filter when date range provided."""
        from mcp_canada.modules.weather.hydro.client import fetch_daily_mean_water

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_daily_feature], 1, False)
            readings, _ = await fetch_daily_mean_water(
                "02LA004", start_date="2026-04-01", end_date="2026-04-04"
            )

        call_kwargs = mock_ogc.call_args.kwargs
        assert call_kwargs.get("datetime_filter") == "2026-04-01/2026-04-04"
        assert call_kwargs.get("properties", {}).get("STATION_NUMBER") == "02LA004"

    @pytest.mark.asyncio
    async def test_fetch_returns_flattened_daily_data(self, sample_hydro_daily_feature):
        """fetch_daily_mean_water returns flat dict with daily readings."""
        from mcp_canada.modules.weather.hydro.client import fetch_daily_mean_water

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_daily_feature], 1, False)
            readings, _ = await fetch_daily_mean_water("02LA004")

        assert len(readings) == 1
        assert readings[0]["station_number"] == "02LA004"
        assert readings[0]["level_m"] == 72.10


class TestFetchHydroStations:
    """Tests for fetch_hydro_stations client function."""

    @pytest.mark.asyncio
    async def test_fetch_by_province(self, sample_hydro_station_feature):
        """fetch_hydro_stations(province='ON') uses province bbox from PROVINCE_BBOX."""
        from mcp_canada.modules.weather.hydro.client import fetch_hydro_stations

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_station_feature], 1, False)
            stations, _ = await fetch_hydro_stations(province="ON")

        call_kwargs = mock_ogc.call_args.kwargs
        assert "bbox" in call_kwargs

    @pytest.mark.asyncio
    async def test_fetch_by_lat_lon(self, sample_hydro_station_feature):
        """fetch_hydro_stations(lat, lon) uses build_bbox."""
        from mcp_canada.modules.weather.hydro.client import fetch_hydro_stations

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_station_feature], 1, False)
            stations, _ = await fetch_hydro_stations(lat=45.3, lon=-76.4)

        call_kwargs = mock_ogc.call_args.kwargs
        assert "bbox" in call_kwargs

    @pytest.mark.asyncio
    async def test_fetch_returns_station_info(self, sample_hydro_station_feature):
        """fetch_hydro_stations returns flat station dicts with required fields."""
        from mcp_canada.modules.weather.hydro.client import fetch_hydro_stations

        with patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_hydro_station_feature], 1, False)
            stations, _ = await fetch_hydro_stations(province="ON")

        assert len(stations) == 1
        s = stations[0]
        assert s["station_number"] == "02LA004"
        assert s["station_name"] == "RIDEAU RIVER AT OTTAWA"
        assert s["province"] == "ON"


class TestFetchFloodRisk:
    """Tests for fetch_flood_risk composite function."""

    @pytest.mark.asyncio
    async def test_fetch_returns_risk_assessment(
        self, sample_hydro_realtime_feature, sample_hydro_peak_feature
    ):
        """fetch_flood_risk returns current_level, historical_max, percent_of_max, risk_level."""
        from mcp_canada.modules.weather.hydro.client import fetch_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.client.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_levels, patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_levels.return_value = (
                [
                    {
                        "station_number": "02LA004",
                        "station_name": "RIDEAU RIVER AT OTTAWA",
                        "level_m": 72.45,
                        "discharge_m3s": 115.0,
                        "datetime": "2026-04-05T10:00:00Z",
                        "lat": 45.3,
                        "lon": -76.4,
                    }
                ],
                False,
            )
            mock_ogc.return_value = ([sample_hydro_peak_feature], 1, False)
            result, cached = await fetch_flood_risk("02LA004")

        assert result is not None
        assert "current_level" in result
        assert "historical_max" in result
        assert "percent_of_max" in result
        assert "risk_level" in result
        assert result["risk_level"] in ("low", "moderate", "high", "critical")

    @pytest.mark.asyncio
    async def test_fetch_risk_level_classification(
        self, sample_hydro_realtime_feature, sample_hydro_peak_feature
    ):
        """fetch_flood_risk returns 'critical' when level exceeds historical max."""
        from mcp_canada.modules.weather.hydro.client import fetch_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.client.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_levels, patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            # Current level much higher than historical max
            mock_levels.return_value = (
                [
                    {
                        "station_number": "02LA004",
                        "station_name": "RIDEAU RIVER AT OTTAWA",
                        "level_m": 200.0,
                        "discharge_m3s": 800.0,
                        "datetime": "2026-04-05T10:00:00Z",
                        "lat": 45.3,
                        "lon": -76.4,
                    }
                ],
                False,
            )
            # Historical max: DISCHARGE=488.0
            mock_ogc.return_value = ([sample_hydro_peak_feature], 1, False)
            result, _ = await fetch_flood_risk("02LA004")

        assert result is not None
        assert result["risk_level"] == "critical"

    @pytest.mark.asyncio
    async def test_fetch_no_current_data_returns_none(self):
        """fetch_flood_risk returns None result when no current readings available."""
        from mcp_canada.modules.weather.hydro.client import fetch_flood_risk

        with patch(
            "mcp_canada.modules.weather.hydro.client.fetch_water_levels",
            new_callable=AsyncMock,
        ) as mock_levels, patch(
            "mcp_canada.modules.weather.hydro.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_levels.return_value = ([], False)
            mock_ogc.return_value = ([], 0, False)
            result, _ = await fetch_flood_risk("INVALID")

        assert result is None
