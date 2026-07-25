"""Unit tests for climate sub-module client functions."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.modules.weather.climate.client import (
    compare_climate_periods,
    fetch_climate_daily,
    fetch_climate_monthly,
    fetch_climate_normals,
    fetch_climate_projections,
    fetch_climate_trends,
    fetch_drought_index,
)


class TestFetchClimateDaily:
    """Tests for fetch_climate_daily()."""

    @pytest.mark.asyncio
    async def test_returns_daily_records(self, sample_daily_feature):
        """Returns list of flattened daily climate dicts."""
        mock_features = [sample_daily_feature]
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=(mock_features, 1, False),
        ):
            result, cached = await fetch_climate_daily("6158731")
        assert isinstance(result, list)
        assert len(result) == 1
        record = result[0]
        assert record["station_id"] == "6158731"
        assert record["date"] == "2024-01-15"
        assert isinstance(record["max_temp_c"], float)
        assert isinstance(record["min_temp_c"], float)
        assert isinstance(record["mean_temp_c"], float)
        assert cached is False

    @pytest.mark.asyncio
    async def test_passes_date_filter(self, sample_daily_feature):
        """Passes datetime_filter when start/end dates provided."""
        mock_features = [sample_daily_feature]
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=(mock_features, 1, False),
        ) as mock_fetch:
            await fetch_climate_daily("6158731", start_date="2024-01-01", end_date="2024-01-31")
        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("datetime_filter") == "2024-01-01/2024-01-31"

    @pytest.mark.asyncio
    async def test_returns_empty_on_no_features(self):
        """Returns empty list when no features found."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([], 0, True),
        ):
            result, cached = await fetch_climate_daily("9999999")
        assert result == []
        assert cached is True


class TestFetchClimateMonthly:
    """Tests for fetch_climate_monthly()."""

    @pytest.mark.asyncio
    async def test_returns_monthly_records(self, sample_monthly_feature):
        """Returns list of flattened monthly climate dicts."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_monthly_feature], 1, False),
        ):
            result, cached = await fetch_climate_monthly("6158731")
        assert isinstance(result, list)
        assert len(result) == 1
        record = result[0]
        assert record["station_id"] == "6158731"
        assert record["year"] == "2024"
        assert record["month"] == "1"

    @pytest.mark.asyncio
    async def test_passes_year_property_filter(self, sample_monthly_feature):
        """Passes year as property filter when provided."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_monthly_feature], 1, False),
        ) as mock_fetch:
            await fetch_climate_monthly("6158731", year=2024)
        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("properties", {}).get("LOCAL_YEAR") == "2024"


class TestFetchClimateNormals:
    """Tests for fetch_climate_normals()."""

    @pytest.mark.asyncio
    async def test_returns_normals_records(self, sample_normal_feature):
        """Returns list of flattened climate normals dicts."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_normal_feature], 1, False),
        ):
            result, cached = await fetch_climate_normals("6158731")
        assert isinstance(result, list)
        assert len(result) == 1
        record = result[0]
        assert record["station_id"] == "6158731"
        assert record["period_begin"] == "1981"
        assert record["period_end"] == "2010"
        assert record["month"] == "1"
        assert record["variable"] == "MEAN_TEMPERATURE"
        assert isinstance(record["value"], float)


class TestFetchClimateProjections:
    """Tests for fetch_climate_projections()."""

    @pytest.mark.asyncio
    async def test_returns_metadata_not_items(self, sample_collection_metadata):
        """Returns collection metadata, not items (items endpoint returns 400)."""
        with patch(
            "mcp_canada.modules.weather.climate.client.api_get",
            new_callable=AsyncMock,
            return_value=sample_collection_metadata,
        ):
            result, cached = await fetch_climate_projections(model="cmip5")
        assert isinstance(result, dict)
        assert "title" in result or "id" in result
        # Must include a note about limitation
        note = result.get("note", "")
        assert "metadata" in note.lower() or "items" in note.lower() or "limitation" in note.lower()

    @pytest.mark.asyncio
    async def test_cmip6_model_selection(self, sample_collection_metadata):
        """Selects CMIP6 collection when model='cmip6'."""
        with patch(
            "mcp_canada.modules.weather.climate.client.api_get",
            new_callable=AsyncMock,
            return_value=sample_collection_metadata,
        ) as mock_get:
            await fetch_climate_projections(model="cmip6")
        url_called = mock_get.call_args[0][0]
        assert "cmip6" in url_called or "dcs" in url_called


class TestFetchDroughtIndex:
    """Tests for fetch_drought_index()."""

    @pytest.mark.asyncio
    async def test_returns_spei_metadata(self, sample_collection_metadata):
        """Returns SPEI collection metadata (items endpoint returns 400)."""
        spei_meta = {**sample_collection_metadata, "id": "climate:spei-3:historical"}
        with patch(
            "mcp_canada.modules.weather.climate.client.api_get",
            new_callable=AsyncMock,
            return_value=spei_meta,
        ):
            result, cached = await fetch_drought_index()
        assert isinstance(result, dict)
        assert "title" in result or "id" in result

    @pytest.mark.asyncio
    async def test_spei_period_12_maps_correct_collection(self, sample_collection_metadata):
        """SPEI period 12 maps to a different collection variant."""
        with patch(
            "mcp_canada.modules.weather.climate.client.api_get",
            new_callable=AsyncMock,
            return_value=sample_collection_metadata,
        ) as mock_get:
            await fetch_drought_index(spei_period=12)
        url_called = mock_get.call_args[0][0]
        assert "spei" in url_called


class TestFetchClimateTrends:
    """Tests for fetch_climate_trends()."""

    @pytest.mark.asyncio
    async def test_returns_trend_records(self, sample_trend_feature):
        """Returns list of flattened trend dicts."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_trend_feature], 1, False),
        ):
            result, cached = await fetch_climate_trends()
        assert isinstance(result, list)
        assert len(result) == 1
        record = result[0]
        assert record["station_id"] == "1100120"
        assert record["measurement_type"] == "total_precip"
        assert isinstance(record["trend"], float)

    @pytest.mark.asyncio
    async def test_filters_by_station_id(self, sample_trend_feature):
        """Passes station_id as property filter."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_trend_feature], 1, False),
        ) as mock_fetch:
            await fetch_climate_trends(station_id="1100120")
        props = mock_fetch.call_args[1].get("properties", {})
        assert props.get("station_id__id_station") == "1100120"

    @pytest.mark.asyncio
    async def test_filters_by_measurement_type(self, sample_trend_feature):
        """Passes measurement_type as property filter."""
        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([sample_trend_feature], 1, False),
        ) as mock_fetch:
            await fetch_climate_trends(measurement_type="total_precip")
        props = mock_fetch.call_args[1].get("properties", {})
        assert props.get("measurement_type__type_mesure") == "total_precip"


class TestCompareClimatePeriods:
    """Tests for compare_climate_periods()."""

    @pytest.mark.asyncio
    async def test_returns_comparison_with_deltas(self, sample_daily_feature):
        """Returns dict with period1, period2, and delta averages."""
        {
            **sample_daily_feature,
            "properties": {
                **sample_daily_feature["properties"],
                "MEAN_TEMPERATURE": "5.0",
                "TOTAL_PRECIPITATION": "10.0",
                "TOTAL_SNOW": "2.0",
            },
        }
        {
            **sample_daily_feature,
            "properties": {
                **sample_daily_feature["properties"],
                "MEAN_TEMPERATURE": "7.0",
                "TOTAL_PRECIPITATION": "12.0",
                "TOTAL_SNOW": "1.0",
            },
        }
        with patch(
            "mcp_canada.modules.weather.climate.client.fetch_climate_daily",
            new_callable=AsyncMock,
            side_effect=[
                ([{"station_id": "6158731", "date": "2000-01-01", "mean_temp_c": 5.0, "total_precip_mm": 10.0, "total_snow_cm": 2.0, "max_temp_c": None, "min_temp_c": None, "snow_on_ground_cm": None, "heating_dd": None, "cooling_dd": None}], False),
                ([{"station_id": "6158731", "date": "2020-01-01", "mean_temp_c": 7.0, "total_precip_mm": 12.0, "total_snow_cm": 1.0, "max_temp_c": None, "min_temp_c": None, "snow_on_ground_cm": None, "heating_dd": None, "cooling_dd": None}], False),
            ],
        ):
            result, cached = await compare_climate_periods(
                "6158731", "2000-01-01", "2000-01-31", "2020-01-01", "2020-01-31"
            )
        assert "period1" in result
        assert "period2" in result
        assert "deltas" in result
        assert result["deltas"]["mean_temp_c"] == pytest.approx(2.0)
        assert result["deltas"]["total_precip_mm"] == pytest.approx(2.0)


class TestClimateTrendsFieldNames:
    """AHCCD trends must use the collection's real property names.

    Regression cover for the Phase 20.1 defect: fetch_climate_trends filtered on
    CLIMATE_IDENTIFIER and MEASUREMENT_TYPE, but the ahccd-trends collection
    names those fields station_id__id_station and measurement_type__type_mesure.
    Every filtered call therefore matched zero records, and _flatten_trend read
    the same wrong keys so even an unfiltered call returned rows of all-None.

    The integration test could not catch it: it asserted shape only `if
    data["data"]:`, so an empty list skipped the body and passed.

    Property names confirmed against the live collection 2026-07-25:
        identifier__identifiant, station_id__id_station, station_name__nom_station,
        joined__rejoint, elevation__elevation, period__periode, province__province,
        year_range__annees, measurement_type__type_mesure, trend_value__valeur_tendance
    """

    LIVE_FEATURE = {
        "properties": {
            "identifier__identifiant": "1100120.Jan.total_precip",
            "station_id__id_station": "1100120",
            "station_name__nom_station": "AGASSIZ_CDA",
            "period__periode": "Jan",
            "province__province": "BC",
            "year_range__annees": "1890-2017",
            "measurement_type__type_mesure": "total_precip",
            "trend_value__valeur_tendance": 74.81,
        }
    }

    @pytest.mark.asyncio
    async def test_measurement_type_filter_uses_real_field_name(self):
        from mcp_canada.modules.weather.climate.client import fetch_climate_trends

        spy = AsyncMock(return_value=([self.LIVE_FEATURE], 1, False))
        with patch("mcp_canada.modules.weather.climate.client.ogc_fetch", new=spy):
            await fetch_climate_trends(measurement_type="total_precip")

        props = spy.await_args.kwargs["properties"]
        assert "measurement_type__type_mesure" in props, (
            f"ahccd-trends names this field measurement_type__type_mesure; "
            f"MEASUREMENT_TYPE matches zero records. Sent: {props}"
        )
        assert props["measurement_type__type_mesure"] == "total_precip"

    @pytest.mark.asyncio
    async def test_station_filter_uses_real_field_name(self):
        from mcp_canada.modules.weather.climate.client import fetch_climate_trends

        spy = AsyncMock(return_value=([self.LIVE_FEATURE], 1, False))
        with patch("mcp_canada.modules.weather.climate.client.ogc_fetch", new=spy):
            await fetch_climate_trends(station_id="1100120")

        props = spy.await_args.kwargs["properties"]
        assert "station_id__id_station" in props, (
            f"ahccd-trends names this field station_id__id_station, not "
            f"CLIMATE_IDENTIFIER. Sent: {props}"
        )

    @pytest.mark.asyncio
    async def test_flattener_reads_real_field_names(self):
        """Rows must carry values, not None from mis-keyed lookups."""
        from mcp_canada.modules.weather.climate.client import fetch_climate_trends

        with patch(
            "mcp_canada.modules.weather.climate.client.ogc_fetch",
            new=AsyncMock(return_value=([self.LIVE_FEATURE], 1, False)),
        ):
            rows, _ = await fetch_climate_trends()

        row = rows[0]
        assert row["station_id"] == "1100120", f"station_id not read: {row}"
        assert row["measurement_type"] == "total_precip", f"measurement_type not read: {row}"
        assert row["trend"] == 74.81, f"trend not read: {row}"
        assert row["station_name"] == "AGASSIZ_CDA", f"station_name not read: {row}"
        assert row["period"] == "Jan", f"period not read: {row}"
        assert row["year_range"] == "1890-2017", f"year_range not read: {row}"
        assert row["province"] == "BC", f"province not read: {row}"
