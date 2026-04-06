"""Unit tests for weather/summary client functions."""

import pytest
from unittest.mock import AsyncMock, patch


class TestFetchWeatherSummary:
    """Tests for fetch_weather_summary()."""

    @pytest.mark.asyncio
    async def test_returns_composite_dict_with_all_sections(self):
        """fetch_weather_summary returns dict with conditions, forecast, alerts, aqhi."""
        from mcp_canada.modules.weather.summary.client import fetch_weather_summary

        sample_conditions = {"city": "Ottawa", "temperature_c": 15.0}
        sample_forecast = [{"period": "Today", "temperature_c": 18.0}]
        sample_alerts = []
        sample_aqhi = [{"aqhi_value": 3.0}]

        with (
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_current_conditions",
                new_callable=AsyncMock,
                return_value=(sample_conditions, False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_forecast",
                new_callable=AsyncMock,
                return_value=(sample_forecast, False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_alerts",
                new_callable=AsyncMock,
                return_value=(sample_alerts, False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_aqhi",
                new_callable=AsyncMock,
                return_value=(sample_aqhi, False),
            ),
        ):
            result, was_cached = await fetch_weather_summary(location="Ottawa")

        assert "conditions" in result
        assert "forecast" in result
        assert "alerts" in result
        assert "aqhi" in result
        assert result["conditions"]["city"] == "Ottawa"
        assert isinstance(result["forecast"], list)

    @pytest.mark.asyncio
    async def test_handles_exception_in_one_section(self):
        """fetch_weather_summary handles exceptions gracefully with error key per section."""
        from mcp_canada.modules.weather.summary.client import fetch_weather_summary

        with (
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_current_conditions",
                new_callable=AsyncMock,
                side_effect=Exception("API timeout"),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_forecast",
                new_callable=AsyncMock,
                return_value=([], False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_alerts",
                new_callable=AsyncMock,
                return_value=([], False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_aqhi",
                new_callable=AsyncMock,
                return_value=([], False),
            ),
        ):
            result, was_cached = await fetch_weather_summary(location="Ottawa")

        # Should not raise; should have error key for conditions section
        assert "conditions" in result
        assert result["conditions"] is None or "error" in str(result.get("conditions", ""))

    @pytest.mark.asyncio
    async def test_was_cached_true_only_when_all_cached(self):
        """fetch_weather_summary: was_cached is True only if all fetches were cached."""
        from mcp_canada.modules.weather.summary.client import fetch_weather_summary

        with (
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_current_conditions",
                new_callable=AsyncMock,
                return_value=({"city": "Toronto"}, True),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_forecast",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_alerts",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_aqhi",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
        ):
            result, was_cached = await fetch_weather_summary(location="Toronto")

        assert was_cached is True

    @pytest.mark.asyncio
    async def test_was_cached_false_when_any_not_cached(self):
        """fetch_weather_summary: was_cached is False if any fetch was not cached."""
        from mcp_canada.modules.weather.summary.client import fetch_weather_summary

        with (
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_current_conditions",
                new_callable=AsyncMock,
                return_value=({"city": "Vancouver"}, False),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_forecast",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_alerts",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
            patch(
                "mcp_canada.modules.weather.summary.client.fetch_aqhi",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
        ):
            result, was_cached = await fetch_weather_summary(location="Vancouver")

        assert was_cached is False


class TestFetchHistoricalExtremes:
    """Tests for fetch_historical_extremes()."""

    @pytest.mark.asyncio
    async def test_returns_dict_with_three_record_types(
        self,
        sample_ltce_temp_feature,
        sample_ltce_precip_feature,
        sample_ltce_snow_feature,
    ):
        """fetch_historical_extremes returns temperature_records, precipitation_records, snowfall_records."""
        from mcp_canada.modules.weather.summary.client import fetch_historical_extremes

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.side_effect = [
                ([sample_ltce_temp_feature], 1, False),
                ([sample_ltce_precip_feature], 1, False),
                ([sample_ltce_snow_feature], 1, False),
            ]
            result, was_cached = await fetch_historical_extremes("6105976")

        assert "temperature_records" in result
        assert "precipitation_records" in result
        assert "snowfall_records" in result
        assert isinstance(result["temperature_records"], list)
        assert len(result["temperature_records"]) == 1

    @pytest.mark.asyncio
    async def test_filters_by_station_id(self, sample_ltce_temp_feature):
        """fetch_historical_extremes filters by CLIMATE_IDENTIFIER."""
        from mcp_canada.modules.weather.summary.client import fetch_historical_extremes

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_ltce_temp_feature], 1, False)
            await fetch_historical_extremes("6105976")

        for call in mock_ogc.call_args_list:
            kwargs = call[1]
            props = kwargs.get("properties", {})
            assert props.get("CLIMATE_IDENTIFIER") == "6105976"


class TestFetchGrowingSeason:
    """Tests for fetch_growing_season()."""

    @pytest.mark.asyncio
    async def test_returns_growing_season_dict(self, sample_climate_normal_growing):
        """fetch_growing_season returns frost-free period data."""
        from mcp_canada.modules.weather.summary.client import fetch_growing_season

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_climate_normal_growing], 1, False)
            result, was_cached = await fetch_growing_season("6105976")

        assert result is not None
        assert result["station_id"] == "6105976"
        assert "growing_season_days" in result

    @pytest.mark.asyncio
    async def test_returns_none_when_no_normals(self):
        """fetch_growing_season returns None when no normals found for station."""
        from mcp_canada.modules.weather.summary.client import fetch_growing_season

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, was_cached = await fetch_growing_season("UNKNOWN")

        assert result is None


class TestFetchHeatingCoolingDays:
    """Tests for fetch_heating_cooling_days()."""

    @pytest.mark.asyncio
    async def test_returns_degree_day_totals(self, sample_climate_daily_feature):
        """fetch_heating_cooling_days returns summed heating/cooling degree days."""
        from mcp_canada.modules.weather.summary.client import fetch_heating_cooling_days

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([sample_climate_daily_feature], 1, False)
            result, was_cached = await fetch_heating_cooling_days("6105976")

        assert result["station_id"] == "6105976"
        assert "total_heating_dd" in result
        assert "total_cooling_dd" in result
        assert "days_counted" in result
        assert result["total_heating_dd"] == pytest.approx(23.2)
        assert result["total_cooling_dd"] == pytest.approx(0.0)
        assert result["days_counted"] == 1

    @pytest.mark.asyncio
    async def test_passes_date_filter_when_provided(self):
        """fetch_heating_cooling_days passes datetime_filter to ogc_fetch when dates given."""
        from mcp_canada.modules.weather.summary.client import fetch_heating_cooling_days

        with patch(
            "mcp_canada.modules.weather.summary.client.ogc_fetch",
            new_callable=AsyncMock,
        ) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            await fetch_heating_cooling_days(
                "6105976", start_date="2025-01-01", end_date="2025-01-31"
            )

        call_kwargs = mock_ogc.call_args[1]
        assert call_kwargs.get("datetime_filter") is not None
        assert "2025-01-01" in call_kwargs["datetime_filter"]
