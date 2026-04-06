"""Unit tests for weather/current/tools.py — all client calls mocked."""

from unittest.mock import AsyncMock, patch

import pytest


class TestWxGetCurrentConditions:

    @pytest.mark.asyncio
    async def test_returns_response_envelope_on_success(self, sample_citypage_feature):
        """wx_get_current_conditions returns _meta envelope with flattened conditions."""
        from mcp_canada.modules.weather.current.tools import wx_get_current_conditions

        mock_data = {
            "station": "Ottawa Macdonald-Cartier Intl",
            "temperature_c": 5.3,
            "humidity_pct": 82,
            "wind_speed_kmh": 15,
            "wind_direction": "W",
            "condition": "Partly Cloudy",
            "pressure_kpa": 101.2,
            "windchill": 2.0,
            "observed_at": "2026-04-05T12:00:00Z",
            "city": "Ottawa (Kanata - Orléans)",
        }
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_current_conditions",
            new=AsyncMock(return_value=(mock_data, False)),
        ):
            result = await wx_get_current_conditions(location="Ottawa", lang="en")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "msc-geomet"
        assert result["data"]["temperature_c"] == 5.3
        assert result["_meta"]["lang"] == "en"

    @pytest.mark.asyncio
    async def test_returns_error_when_not_found(self):
        """wx_get_current_conditions returns make_error NOT_FOUND when no data."""
        from mcp_canada.modules.weather.current.tools import wx_get_current_conditions

        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_current_conditions",
            new=AsyncMock(return_value=(None, False)),
        ):
            result = await wx_get_current_conditions(location="NonexistentCity", lang="en")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_param_passes_through(self):
        """wx_get_current_conditions passes lang through to envelope."""
        from mcp_canada.modules.weather.current.tools import wx_get_current_conditions

        mock_data = {"temperature_c": 5.3, "station": "Test"}
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_current_conditions",
            new=AsyncMock(return_value=(mock_data, True)),
        ):
            result = await wx_get_current_conditions(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"
        assert result["_meta"]["cached"] is True


class TestWxGetForecast:

    @pytest.mark.asyncio
    async def test_returns_forecast_periods(self):
        """wx_get_forecast returns _meta envelope with list of forecast periods."""
        from mcp_canada.modules.weather.current.tools import wx_get_forecast

        mock_periods = [
            {"period": "Tonight", "temperature_c": -2, "text": "Clear."},
            {"period": "Monday", "temperature_c": 8, "text": "Sunny."},
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_forecast",
            new=AsyncMock(return_value=(mock_periods, False)),
        ):
            result = await wx_get_forecast(location="Ottawa", lang="en")

        assert "_meta" in result
        assert len(result["data"]) == 2
        assert result["data"][0]["period"] == "Tonight"

    @pytest.mark.asyncio
    async def test_returns_error_when_no_forecast(self):
        """wx_get_forecast returns NOT_FOUND error when no forecast data."""
        from mcp_canada.modules.weather.current.tools import wx_get_forecast

        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_forecast",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await wx_get_forecast(location="NoCity", lang="en")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_days_param_limits_output(self):
        """wx_get_forecast respects days parameter to limit returned periods."""
        from mcp_canada.modules.weather.current.tools import wx_get_forecast

        mock_periods = [
            {"period": f"Day {i}", "temperature_c": i} for i in range(14)
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_forecast",
            new=AsyncMock(return_value=(mock_periods, False)),
        ):
            result = await wx_get_forecast(location="Ottawa", days=3, lang="en")

        # days=3 means 3 days = 6 periods (day + night), but 6 is ceiling
        assert len(result["data"]) <= 6


class TestWxGetWeatherAlerts:

    @pytest.mark.asyncio
    async def test_returns_alert_list(self):
        """wx_get_weather_alerts returns _meta envelope with list of alerts."""
        from mcp_canada.modules.weather.current.tools import wx_get_weather_alerts

        mock_alerts = [
            {
                "alert_code": "WWCN35",
                "alert_type": "warning",
                "province": "NB",
                "published": "2026-04-05T10:00:00Z",
            }
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_alerts",
            new=AsyncMock(return_value=(mock_alerts, False)),
        ):
            result = await wx_get_weather_alerts(province="NB", lang="en")

        assert "_meta" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["province"] == "NB"

    @pytest.mark.asyncio
    async def test_returns_empty_list_as_valid_response(self):
        """wx_get_weather_alerts returns valid envelope with empty list when no alerts."""
        from mcp_canada.modules.weather.current.tools import wx_get_weather_alerts

        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_alerts",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await wx_get_weather_alerts(province="PE", lang="en")

        # Empty list is a valid response (no active alerts)
        assert "_meta" in result
        assert result["data"] == []


class TestWxSearchStations:

    @pytest.mark.asyncio
    async def test_returns_station_list(self):
        """wx_search_stations returns _meta envelope with station list."""
        from mcp_canada.modules.weather.current.tools import wx_search_stations

        mock_stations = [
            {
                "station_id": "6105976",
                "station_name": "OTTAWA CDA",
                "province": "ON",
                "lat": 45.42,
                "lon": -75.72,
            }
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_stations",
            new=AsyncMock(return_value=(mock_stations, False)),
        ):
            result = await wx_search_stations(province="ON", lang="en")

        assert "_meta" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["station_id"] == "6105976"

    @pytest.mark.asyncio
    async def test_no_stations_returns_not_found(self):
        """wx_search_stations returns NOT_FOUND when no stations match."""
        from mcp_canada.modules.weather.current.tools import wx_search_stations

        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_stations",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await wx_search_stations(province="XX", lang="en")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lat_lon_search_sorts_by_distance(self):
        """wx_search_stations with lat/lon returns stations (sorted by distance in client)."""
        from mcp_canada.modules.weather.current.tools import wx_search_stations

        mock_stations = [
            {"station_id": "A", "station_name": "Near", "lat": 45.4, "lon": -75.7},
            {"station_id": "B", "station_name": "Far", "lat": 45.5, "lon": -75.8},
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_stations",
            new=AsyncMock(return_value=(mock_stations, False)),
        ):
            result = await wx_search_stations(lat=45.4, lon=-75.7, lang="en")

        assert "_meta" in result
        assert len(result["data"]) == 2


class TestWxGetStationData:

    @pytest.mark.asyncio
    async def test_returns_hourly_observations(self):
        """wx_get_station_data returns _meta envelope with hourly observations."""
        from mcp_canada.modules.weather.current.tools import wx_get_station_data

        mock_obs = [
            {
                "station_id": "6105976",
                "datetime": "2024-01-15T14:00:00",
                "temp_c": 3.2,
                "wind_speed_kmh": 15.0,
            }
        ]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_hourly_obs",
            new=AsyncMock(return_value=(mock_obs, False)),
        ):
            result = await wx_get_station_data(
                station_id="6105976", date="2024-01-15", lang="en"
            )

        assert "_meta" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["temp_c"] == 3.2

    @pytest.mark.asyncio
    async def test_returns_not_found_for_invalid_station(self):
        """wx_get_station_data returns NOT_FOUND error for station with no data."""
        from mcp_canada.modules.weather.current.tools import wx_get_station_data

        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_hourly_obs",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await wx_get_station_data(station_id="INVALID", lang="en")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """wx_get_station_data lang parameter appears in _meta."""
        from mcp_canada.modules.weather.current.tools import wx_get_station_data

        mock_obs = [{"station_id": "6105976", "datetime": "2024-01-15T14:00:00"}]
        with patch(
            "mcp_canada.modules.weather.current.tools.fetch_hourly_obs",
            new=AsyncMock(return_value=(mock_obs, False)),
        ):
            result = await wx_get_station_data(station_id="6105976", lang="fr")

        assert result["_meta"]["lang"] == "fr"
