"""Unit tests for snow weather client functions.

Tests:
- fetch_snow_depth: extracts snw_dpth from SWOB, multi-sensor fallback (Pitfall 4)
- fetch_snow_water_equivalent: estimates SWE from snow depth with density factor
"""

import pytest
from unittest.mock import AsyncMock, patch


def import_client():
    import mcp_canada.modules.weather.snow.client as client_mod
    return client_mod


# ===========================================================================
# 1. fetch_snow_depth
# ===========================================================================

class TestFetchSnowDepth:

    @pytest.mark.asyncio
    async def test_returns_dict_or_none_and_bool(self, sample_swob_snow_feature):
        """fetch_snow_depth returns (dict | None, bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, cached = await client.fetch_snow_depth(lat=45.4, lon=-75.7)

        assert isinstance(cached, bool)
        # result is dict or None

    @pytest.mark.asyncio
    async def test_extracts_primary_snow_depth(self, sample_swob_snow_feature):
        """fetch_snow_depth extracts snw_dpth-value as primary sensor."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_depth(lat=45.4, lon=-75.7)

        assert result is not None
        assert result["snow_depth_cm"] == 15.0
        assert result["station_name"] == "OTTAWA INTL A"

    @pytest.mark.asyncio
    async def test_returns_expected_fields(self, sample_swob_snow_feature):
        """fetch_snow_depth returns station_name, snow_depth_cm, observed_at, air_temp_c."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_depth(lat=45.4, lon=-75.7)

        assert result is not None
        assert "station_name" in result
        assert "snow_depth_cm" in result
        assert "observed_at" in result
        assert "air_temp_c" in result
        assert "lat" in result
        assert "lon" in result

    @pytest.mark.asyncio
    async def test_fallback_to_backup_sensors_when_primary_missing(
        self, sample_swob_backup_only_feature
    ):
        """fetch_snow_depth averages snw_dpth_1/2 when primary snw_dpth is absent (Pitfall 4)."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_backup_only_feature], 1, False)
            result, _ = await client.fetch_snow_depth(lat=46.0, lon=-80.0)

        assert result is not None
        # Average of 20.0 and 22.0 = 21.0
        assert result["snow_depth_cm"] == pytest.approx(21.0)

    @pytest.mark.asyncio
    async def test_returns_none_when_no_snow_sensor(self, sample_swob_no_snow_feature):
        """fetch_snow_depth returns None snow_depth_cm when station lacks snow sensor."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_no_snow_feature], 1, False)
            result, _ = await client.fetch_snow_depth(lat=43.7, lon=-79.4)

        # Should return a result (station found), but snow_depth_cm may be None
        if result is not None:
            assert result.get("snow_depth_cm") is None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_features(self):
        """fetch_snow_depth returns (None, False) when no SWOB features found."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, cached = await client.fetch_snow_depth(lat=45.4, lon=-75.7)

        assert result is None
        assert cached is False

    @pytest.mark.asyncio
    async def test_with_station_id_uses_properties_filter(self, sample_swob_snow_feature):
        """fetch_snow_depth with station_id passes properties filter to ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            await client.fetch_snow_depth(station_id="6106000")

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("properties") is not None

    @pytest.mark.asyncio
    async def test_with_lat_lon_uses_bbox(self, sample_swob_snow_feature):
        """fetch_snow_depth with lat/lon passes bbox to ogc_fetch."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            await client.fetch_snow_depth(lat=45.4, lon=-75.7)

        call_kwargs = mock_ogc.call_args
        assert call_kwargs.kwargs.get("bbox") is not None


# ===========================================================================
# 2. fetch_snow_water_equivalent
# ===========================================================================

class TestFetchSnowWaterEquivalent:

    @pytest.mark.asyncio
    async def test_returns_dict_and_bool_tuple(self, sample_swob_snow_feature):
        """fetch_snow_water_equivalent returns (dict, bool) tuple."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, cached = await client.fetch_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert isinstance(cached, bool)

    @pytest.mark.asyncio
    async def test_calculates_swe_from_snow_depth(self, sample_swob_snow_feature):
        """fetch_snow_water_equivalent calculates SWE = snow_depth_cm * density_factor."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert result is not None
        # snow_depth = 15.0, density_factor = 0.3, SWE = 15.0 * 0.3 = 4.5mm
        assert result["swe_mm"] == pytest.approx(4.5)

    @pytest.mark.asyncio
    async def test_uses_custom_density_factor(self, sample_swob_snow_feature):
        """fetch_snow_water_equivalent uses provided density_factor."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_water_equivalent(
                lat=45.4, lon=-75.7, density_factor=0.1
            )

        assert result is not None
        # snow_depth = 15.0, density_factor = 0.1, SWE = 15.0 * 0.1 = 1.5mm
        assert result["swe_mm"] == pytest.approx(1.5)

    @pytest.mark.asyncio
    async def test_returns_expected_fields(self, sample_swob_snow_feature):
        """fetch_snow_water_equivalent returns all required fields."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert result is not None
        assert "station_name" in result
        assert "snow_depth_cm" in result
        assert "swe_mm" in result
        assert "density_factor" in result
        assert "observed_at" in result
        assert "note" in result

    @pytest.mark.asyncio
    async def test_note_mentions_estimation(self, sample_swob_snow_feature):
        """fetch_snow_water_equivalent note field explains estimation approach."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([sample_swob_snow_feature], 1, False)
            result, _ = await client.fetch_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert result is not None
        note = result["note"]
        assert "estimate" in note.lower() or "density" in note.lower()

    @pytest.mark.asyncio
    async def test_returns_none_when_no_snow_data(self):
        """fetch_snow_water_equivalent returns (None, False) when no snow data."""
        client = import_client()
        with patch("mcp_canada.modules.weather.snow.client.ogc_fetch",
                   new_callable=AsyncMock) as mock_ogc:
            mock_ogc.return_value = ([], 0, False)
            result, cached = await client.fetch_snow_water_equivalent(lat=45.4, lon=-75.7)

        assert result is None
        assert cached is False
