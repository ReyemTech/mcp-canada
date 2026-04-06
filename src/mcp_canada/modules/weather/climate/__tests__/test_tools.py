"""Unit tests for climate sub-module tool functions."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.modules.weather.climate.tools import (
    wx_compare_climate_periods,
    wx_get_climate_daily,
    wx_get_climate_monthly,
    wx_get_climate_normals,
    wx_get_climate_projections,
    wx_get_climate_trends,
    wx_get_drought_index,
)


class TestWxGetClimateDaily:
    """Tests for wx_get_climate_daily tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """Returns _meta envelope on success."""
        daily_records = [
            {"station_id": "6158731", "date": "2024-01-01", "mean_temp_c": -2.5,
             "max_temp_c": 1.0, "min_temp_c": -6.0, "total_precip_mm": 3.2,
             "total_snow_cm": 3.4, "snow_on_ground_cm": 12.0, "heating_dd": 20.5, "cooling_dd": 0.0}
        ]
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_daily",
            new_callable=AsyncMock,
            return_value=(daily_records, False),
        ):
            result = await wx_get_climate_daily(
                station_id="6158731", start_date="2024-01-01", end_date="2024-01-31"
            )
        assert "_meta" in result
        assert "data" in result
        assert result["_meta"]["lang"] == "en"

    @pytest.mark.asyncio
    async def test_lang_passes_through(self):
        """lang parameter propagates to envelope."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_daily",
            new_callable=AsyncMock,
            return_value=([], False),
        ):
            result = await wx_get_climate_daily(station_id="6158731", lang="fr")
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_daily",
            new_callable=AsyncMock,
            side_effect=Exception("connection error"),
        ):
            result = await wx_get_climate_daily(station_id="6158731")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestWxGetClimateMonthly:
    """Tests for wx_get_climate_monthly tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """Returns _meta envelope on success."""
        monthly_records = [
            {"station_id": "6158731", "year": "2024", "month": "1",
             "mean_temp_c": -6.4, "max_temp_c": -1.5, "min_temp_c": -11.3,
             "total_precip_mm": 52.3, "total_snow_cm": 45.1}
        ]
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_monthly",
            new_callable=AsyncMock,
            return_value=(monthly_records, False),
        ):
            result = await wx_get_climate_monthly(station_id="6158731", year=2024)
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_monthly",
            new_callable=AsyncMock,
            side_effect=Exception("timeout"),
        ):
            result = await wx_get_climate_monthly(station_id="6158731")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestWxGetClimateNormals:
    """Tests for wx_get_climate_normals tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """Returns _meta envelope on success."""
        normal_records = [
            {"station_id": "6158731", "period_begin": "1981", "period_end": "2010",
             "month": "1", "variable": "MEAN_TEMPERATURE", "value": -10.5}
        ]
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_normals",
            new_callable=AsyncMock,
            return_value=(normal_records, False),
        ):
            result = await wx_get_climate_normals(station_id="6158731")
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_docstring_mentions_1981_2010(self):
        """Docstring must mention 1981-2010 period (not 1991-2020)."""
        doc = wx_get_climate_normals.__doc__ or ""
        assert "1981" in doc
        assert "2010" in doc

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_normals",
            new_callable=AsyncMock,
            side_effect=Exception("timeout"),
        ):
            result = await wx_get_climate_normals(station_id="6158731")
        assert "error" in result


class TestWxGetClimateProjections:
    """Tests for wx_get_climate_projections tool."""

    @pytest.mark.asyncio
    async def test_returns_metadata_on_success(self):
        """Returns collection metadata (not items)."""
        meta = {
            "id": "climate:cmip5:projected:annual:anomaly",
            "title": "CMIP5 Projections",
            "description": "...",
            "note": "Returns collection metadata only. Grid-based projection data requires direct MSC API access.",
        }
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_projections",
            new_callable=AsyncMock,
            return_value=(meta, False),
        ):
            result = await wx_get_climate_projections(model="cmip5")
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_docstring_mentions_metadata_only(self):
        """Docstring must mention metadata-only limitation."""
        doc = wx_get_climate_projections.__doc__ or ""
        assert "metadata" in doc.lower()

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_projections",
            new_callable=AsyncMock,
            side_effect=Exception("error"),
        ):
            result = await wx_get_climate_projections(model="cmip5")
        assert "error" in result


class TestWxGetDroughtIndex:
    """Tests for wx_get_drought_index tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """Returns _meta envelope on success."""
        meta = {
            "id": "climate:spei-3:historical",
            "title": "SPEI Drought Index",
            "note": "Returns collection metadata only.",
        }
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_drought_index",
            new_callable=AsyncMock,
            return_value=(meta, False),
        ):
            result = await wx_get_drought_index(lat=45.0, lon=-75.0)
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_drought_index",
            new_callable=AsyncMock,
            side_effect=Exception("error"),
        ):
            result = await wx_get_drought_index(lat=45.0, lon=-75.0)
        assert "error" in result


class TestWxCompareClimatePeriods:
    """Tests for wx_compare_climate_periods tool."""

    @pytest.mark.asyncio
    async def test_returns_comparison_data(self):
        """Returns comparison data with deltas."""
        comparison = {
            "period1": {"start": "2000-01-01", "end": "2000-01-31", "mean_temp_c": 5.0,
                        "total_precip_mm": 10.0, "total_snow_cm": 2.0},
            "period2": {"start": "2020-01-01", "end": "2020-01-31", "mean_temp_c": 7.0,
                        "total_precip_mm": 12.0, "total_snow_cm": 1.0},
            "deltas": {"mean_temp_c": 2.0, "total_precip_mm": 2.0, "total_snow_cm": -1.0},
        }
        with patch(
            "mcp_canada.modules.weather.climate.tools.compare_climate_periods",
            new_callable=AsyncMock,
            return_value=(comparison, False),
        ):
            result = await wx_compare_climate_periods(
                station_id="6158731",
                period1_start="2000-01-01",
                period1_end="2000-01-31",
                period2_start="2020-01-01",
                period2_end="2020-01-31",
            )
        assert "_meta" in result
        assert "data" in result
        assert "deltas" in result["data"]

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.compare_climate_periods",
            new_callable=AsyncMock,
            side_effect=Exception("error"),
        ):
            result = await wx_compare_climate_periods(
                station_id="6158731",
                period1_start="2000-01-01",
                period1_end="2000-01-31",
                period2_start="2020-01-01",
                period2_end="2020-01-31",
            )
        assert "error" in result


class TestWxGetClimateTrends:
    """Tests for wx_get_climate_trends tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope(self):
        """Returns _meta envelope on success."""
        trend_records = [
            {"station_id": "6158731", "measurement_type": "temperature",
             "trend": 0.018, "year_begin": "1940", "year_end": "2020"}
        ]
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_trends",
            new_callable=AsyncMock,
            return_value=(trend_records, False),
        ):
            result = await wx_get_climate_trends(measurement_type="temperature")
        assert "_meta" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_returns_error_on_exception(self):
        """Returns make_error on unexpected exception."""
        with patch(
            "mcp_canada.modules.weather.climate.tools.fetch_climate_trends",
            new_callable=AsyncMock,
            side_effect=Exception("error"),
        ):
            result = await wx_get_climate_trends()
        assert "error" in result
