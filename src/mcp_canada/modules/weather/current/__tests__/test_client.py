"""Unit tests for weather/current/client.py — all HTTP mocked."""

from unittest.mock import AsyncMock, patch

import pytest


class TestFetchCurrentConditions:

    @pytest.mark.asyncio
    async def test_by_lat_lon_returns_flattened_conditions(self, sample_citypage_feature):
        """fetch_current_conditions with lat/lon returns flat dict matching CurrentConditions."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, False)),
        ):
            result, was_cached = await fetch_current_conditions(lat=45.4, lon=-75.7)

        assert result is not None
        assert result["temperature_c"] == 5.3
        assert result["humidity_pct"] == 82
        assert result["wind_speed_kmh"] == 15
        assert result["wind_direction"] == "W"
        assert result["pressure_kpa"] == 101.2
        assert result["condition"] == "Partly Cloudy"
        assert result["windchill"] == 2.0
        assert result["observed_at"] == "2026-04-05T12:00:00Z"
        assert result["station"] == "Ottawa Macdonald-Cartier Intl"
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_by_location_name_filters_by_name(self, sample_citypage_feature):
        """fetch_current_conditions with location name filters features by name match."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, True)),
        ):
            result, was_cached = await fetch_current_conditions(location="Ottawa")

        assert result is not None
        assert result["temperature_c"] == 5.3
        assert was_cached is True

    @pytest.mark.asyncio
    async def test_location_not_found_returns_none(self, sample_citypage_feature):
        """fetch_current_conditions returns None when location name doesn't match."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, False)),
        ):
            result, was_cached = await fetch_current_conditions(location="Vancouver")

        assert result is None

    @pytest.mark.asyncio
    async def test_empty_features_returns_none(self):
        """fetch_current_conditions returns None when API returns no features."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([], 0, False)),
        ):
            result, was_cached = await fetch_current_conditions(lat=45.4, lon=-75.7)

        assert result is None

    @pytest.mark.asyncio
    async def test_province_uses_province_bbox(self, sample_citypage_feature):
        """fetch_current_conditions with province uses PROVINCE_BBOX for bbox."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        mock_fetch = AsyncMock(return_value=([sample_citypage_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            result, _ = await fetch_current_conditions(province="ON")

        assert result is not None
        # bbox should have been passed — verify ogc_fetch was called with bbox kwarg
        call_kwargs = mock_fetch.call_args.kwargs
        assert call_kwargs.get("bbox") is not None

    @pytest.mark.asyncio
    async def test_fr_lang_uses_french_values(self, sample_citypage_feature):
        """fetch_current_conditions with lang='fr' returns French-language fields."""
        from mcp_canada.modules.weather.current.client import fetch_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, False)),
        ):
            result, _ = await fetch_current_conditions(lat=45.4, lon=-75.7, lang="fr")

        assert result is not None
        assert result["condition"] == "Partiellement nuageux"
        assert result["wind_direction"] == "O"


class TestFetchForecast:

    @pytest.mark.asyncio
    async def test_returns_list_of_forecast_periods(self, sample_citypage_feature):
        """fetch_forecast returns a list of ForecastPeriod dicts."""
        from mcp_canada.modules.weather.current.client import fetch_forecast

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, False)),
        ):
            periods, was_cached = await fetch_forecast(lat=45.4, lon=-75.7)

        assert len(periods) == 2
        first = periods[0]
        assert first["period"] == "Tonight"
        assert first["temperature_c"] == -2
        assert first["text"] == "Clear. Low minus 2."
        assert first["wind_speed_kmh"] == 10
        assert first["wind_direction_deg"] == 225

    @pytest.mark.asyncio
    async def test_forecast_location_filter(self, sample_citypage_feature):
        """fetch_forecast filters by location name when lat/lon not given."""
        from mcp_canada.modules.weather.current.client import fetch_forecast

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_citypage_feature], 1, False)),
        ):
            periods, _ = await fetch_forecast(location="Ottawa")

        assert len(periods) == 2

    @pytest.mark.asyncio
    async def test_forecast_empty_returns_empty_list(self):
        """fetch_forecast returns empty list when no features found."""
        from mcp_canada.modules.weather.current.client import fetch_forecast

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([], 0, False)),
        ):
            periods, _ = await fetch_forecast(lat=45.4, lon=-75.7)

        assert periods == []


class TestFetchAlerts:

    @pytest.mark.asyncio
    async def test_by_province_returns_alert_list(self, sample_alert_feature):
        """fetch_alerts with province returns list of WeatherAlert dicts."""
        from mcp_canada.modules.weather.current.client import fetch_alerts

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_alert_feature], 1, False)),
        ):
            alerts, was_cached = await fetch_alerts(province="NB")

        assert len(alerts) == 1
        a = alerts[0]
        assert a["alert_code"] == "WWCN35_CWNT"
        assert a["alert_type"] == "warning"
        assert a["province"] == "NB"
        assert a["published"] == "2026-04-05T10:00:00Z"
        assert a["lat"] == 45.9
        assert a["lon"] == -66.5

    @pytest.mark.asyncio
    async def test_province_passed_as_property_filter(self, sample_alert_feature):
        """fetch_alerts passes province as OGC property filter, not bbox."""
        from mcp_canada.modules.weather.current.client import fetch_alerts

        mock_fetch = AsyncMock(return_value=([sample_alert_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            await fetch_alerts(province="NB")

        call_kwargs = mock_fetch.call_args.kwargs
        assert call_kwargs.get("properties", {}).get("province") == "NB"

    @pytest.mark.asyncio
    async def test_no_filters_returns_recent_alerts(self, sample_alert_feature):
        """fetch_alerts with no filters returns recent alerts without province filter."""
        from mcp_canada.modules.weather.current.client import fetch_alerts

        mock_fetch = AsyncMock(return_value=([sample_alert_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            alerts, _ = await fetch_alerts()

        assert len(alerts) == 1
        # Should not pass province property
        call_kwargs = mock_fetch.call_args.kwargs
        properties = call_kwargs.get("properties") or {}
        assert "province" not in properties

    @pytest.mark.asyncio
    async def test_alert_type_filter(self, sample_alert_feature):
        """fetch_alerts with alert_type passes it as property filter."""
        from mcp_canada.modules.weather.current.client import fetch_alerts

        mock_fetch = AsyncMock(return_value=([sample_alert_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            await fetch_alerts(alert_type="warning")

        call_kwargs = mock_fetch.call_args.kwargs
        assert call_kwargs.get("properties", {}).get("alert_type") == "warning"


class TestFetchStations:

    @pytest.mark.asyncio
    async def test_by_province_returns_station_list(self, sample_station_feature):
        """fetch_stations with province returns list of ClimateStation dicts."""
        from mcp_canada.modules.weather.current.client import fetch_stations

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_station_feature], 1, False)),
        ):
            stations, was_cached = await fetch_stations(province="ON")

        assert len(stations) == 1
        s = stations[0]
        assert s["station_id"] == "6105976"
        assert s["station_name"] == "OTTAWA CDA"
        assert s["province"] == "ON"
        # Must use geometry coordinates, NOT DMS properties
        assert s["lat"] == 45.42
        assert s["lon"] == -75.72

    @pytest.mark.asyncio
    async def test_by_lat_lon_uses_build_bbox(self, sample_station_feature):
        """fetch_stations with lat/lon passes bbox from build_bbox to ogc_fetch."""
        from mcp_canada.modules.weather.current.client import fetch_stations

        mock_fetch = AsyncMock(return_value=([sample_station_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            stations, _ = await fetch_stations(lat=45.4, lon=-75.7)

        call_kwargs = mock_fetch.call_args.kwargs
        assert call_kwargs.get("bbox") is not None

    @pytest.mark.asyncio
    async def test_uses_geometry_coordinates_not_dms(self, sample_station_feature):
        """Station lat/lon comes from geometry.coordinates (decimal), not LATITUDE/LONGITUDE properties (DMS)."""
        from mcp_canada.modules.weather.current.client import fetch_stations

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_station_feature], 1, False)),
        ):
            stations, _ = await fetch_stations(province="ON")

        s = stations[0]
        # geometry is [-75.72, 45.42] — these are decimal degrees
        assert abs(s["lat"] - 45.42) < 0.01
        assert abs(s["lon"] - (-75.72)) < 0.01
        # NOT the DMS values 454200000 or -757200000
        assert s["lat"] != 454200000


class TestFetchHourlyObs:

    @pytest.mark.asyncio
    async def test_returns_hourly_observations(self, sample_hourly_feature):
        """fetch_hourly_obs returns list of HourlyObservation dicts."""
        from mcp_canada.modules.weather.current.client import fetch_hourly_obs

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([sample_hourly_feature], 1, False)),
        ):
            obs, was_cached = await fetch_hourly_obs("6105976")

        assert len(obs) == 1
        o = obs[0]
        assert o["station_id"] == "6105976"
        assert o["datetime"] == "2024-01-15T14:00:00"
        assert o["temp_c"] == 3.2
        assert o["dew_point_c"] == -1.1
        assert o["wind_speed_kmh"] == 15.0
        assert o["pressure_kpa"] == 101.8

    @pytest.mark.asyncio
    async def test_passes_station_id_as_property_filter(self, sample_hourly_feature):
        """fetch_hourly_obs passes CLIMATE_IDENTIFIER as OGC property filter."""
        from mcp_canada.modules.weather.current.client import fetch_hourly_obs

        mock_fetch = AsyncMock(return_value=([sample_hourly_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            await fetch_hourly_obs("6105976")

        call_kwargs = mock_fetch.call_args.kwargs
        assert call_kwargs.get("properties", {}).get("CLIMATE_IDENTIFIER") == "6105976"

    @pytest.mark.asyncio
    async def test_passes_date_as_datetime_filter(self, sample_hourly_feature):
        """fetch_hourly_obs with date adds ISO 8601 datetime range filter."""
        from mcp_canada.modules.weather.current.client import fetch_hourly_obs

        mock_fetch = AsyncMock(return_value=([sample_hourly_feature], 1, False))
        with patch("mcp_canada.modules.weather.current.client.ogc_fetch", new=mock_fetch):
            await fetch_hourly_obs("6105976", date="2024-01-15")

        call_kwargs = mock_fetch.call_args.kwargs
        dt_filter = call_kwargs.get("datetime_filter")
        assert dt_filter is not None
        assert "2024-01-15" in dt_filter

    @pytest.mark.asyncio
    async def test_empty_station_returns_empty_list(self):
        """fetch_hourly_obs returns empty list when no records found."""
        from mcp_canada.modules.weather.current.client import fetch_hourly_obs

        with patch(
            "mcp_canada.modules.weather.current.client.ogc_fetch",
            new=AsyncMock(return_value=([], 0, False)),
        ):
            obs, _ = await fetch_hourly_obs("NONEXISTENT")

        assert obs == []
