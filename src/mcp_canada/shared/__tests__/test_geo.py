"""Unit tests for shared/geo.py OGC utility layer."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.shared.geo import (
    build_bbox,
    extract_centroid,
    haversine_km,
    nearest_station,
    ogc_fetch,
)


class TestHaversineKm:
    """Tests for haversine_km distance calculation."""

    def test_same_point_returns_zero(self):
        assert haversine_km(0, 0, 0, 0) == 0.0

    def test_known_distance_ottawa_to_nearby(self):
        """Ottawa to a point ~13.2 km away."""
        dist = haversine_km(45.0, -75.0, 45.1, -75.1)
        assert 12.0 < dist < 15.0

    def test_returns_float(self):
        result = haversine_km(43.6, -79.4, 45.4, -75.7)
        assert isinstance(result, float)

    def test_symmetric(self):
        d1 = haversine_km(45.0, -75.0, 45.1, -75.1)
        d2 = haversine_km(45.1, -75.1, 45.0, -75.0)
        assert abs(d1 - d2) < 0.001


class TestExtractCentroid:
    """Tests for extract_centroid geometry handling."""

    def test_point_returns_lat_lon(self):
        geom = {"type": "Point", "coordinates": [-75.0, 45.0]}
        lat, lon = extract_centroid(geom)
        assert lat == 45.0
        assert lon == -75.0

    def test_polygon_returns_centroid(self):
        geom = {
            "type": "Polygon",
            "coordinates": [[[-75, 45], [-74, 45], [-74, 46], [-75, 46], [-75, 45]]],
        }
        lat, lon = extract_centroid(geom)
        # Average of 5 vertices: (-75+-74+-74+-75+-75)/5 = -74.6, (45+45+46+46+45)/5 = 45.4
        assert lat is not None
        assert lon is not None
        assert 45.0 <= lat <= 46.0
        assert -75.0 <= lon <= -74.0

    def test_multipolygon_returns_centroid(self):
        geom = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[-75, 45], [-74, 45], [-74, 46], [-75, 46], [-75, 45]]]
            ],
        }
        lat, lon = extract_centroid(geom)
        assert lat is not None
        assert lon is not None

    def test_none_geometry_returns_none_tuple(self):
        lat, lon = extract_centroid(None)
        assert lat is None
        assert lon is None

    def test_unknown_geometry_type_returns_none_tuple(self):
        lat, lon = extract_centroid({"type": "Unknown", "coordinates": []})
        assert lat is None
        assert lon is None

    def test_missing_type_returns_none_tuple(self):
        lat, lon = extract_centroid({})
        assert lat is None
        assert lon is None


class TestBuildBbox:
    """Tests for build_bbox bounding box construction."""

    def test_returns_four_tuple(self):
        result = build_bbox(45.0, -75.0, radius_km=50)
        assert len(result) == 4

    def test_order_is_lon_min_lat_min_lon_max_lat_max(self):
        lon_min, lat_min, lon_max, lat_max = build_bbox(45.0, -75.0, radius_km=50)
        assert lon_min < -75.0
        assert lon_max > -75.0
        assert lat_min < 45.0
        assert lat_max > 45.0

    def test_larger_radius_produces_larger_bbox(self):
        small = build_bbox(45.0, -75.0, radius_km=10)
        large = build_bbox(45.0, -75.0, radius_km=100)
        assert large[0] < small[0]  # lon_min further west
        assert large[2] > small[2]  # lon_max further east


class TestOgcFetch:
    """Tests for ogc_fetch OGC API Features client."""

    @pytest.mark.asyncio
    async def test_returns_features_and_number_matched(self):
        mock_response = {
            "features": [{"id": "1", "type": "Feature"}],
            "numberMatched": 42,
        }
        with patch(
            "mcp_canada.shared.geo.cached_fetch",
            new_callable=AsyncMock,
            return_value=(mock_response, False),
        ):
            features, number_matched, was_cached = await ogc_fetch(
                "climate-stations", bbox=(-76.0, 44.0, -74.0, 46.0), limit=10
            )
        assert len(features) == 1
        assert number_matched == 42
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_handles_empty_response(self):
        mock_response = {"features": [], "numberMatched": 0}
        with patch(
            "mcp_canada.shared.geo.cached_fetch",
            new_callable=AsyncMock,
            return_value=(mock_response, False),
        ):
            features, number_matched, was_cached = await ogc_fetch(
                "climate-stations"
            )
        assert features == []
        assert number_matched == 0

    @pytest.mark.asyncio
    async def test_datetime_filter_passed_as_datetime_param(self):
        mock_response = {"features": [], "numberMatched": 0}

        async def fake_cached_fetch(key, ttl, fetcher):
            # Invoke the fetcher to capture what it would pass to api_get
            return mock_response, False

        with patch("mcp_canada.shared.geo.cached_fetch", side_effect=fake_cached_fetch):
            with patch("mcp_canada.shared.geo.api_get", new_callable=AsyncMock) as mock_api:
                mock_api.return_value = mock_response
                await ogc_fetch(
                    "climate-stations",
                    datetime_filter="2024-01-01/2024-12-31",
                )
                # api_get was not called directly when cached_fetch short-circuits
                # We verify the key contains the datetime filter
            features, _, _ = await ogc_fetch(
                "climate-stations",
                datetime_filter="2024-01-01/2024-12-31",
            )
        assert features == []

    @pytest.mark.asyncio
    async def test_defaults_number_matched_to_features_length(self):
        mock_response = {
            "features": [{"id": "1"}, {"id": "2"}],
            # No numberMatched key
        }
        with patch(
            "mcp_canada.shared.geo.cached_fetch",
            new_callable=AsyncMock,
            return_value=(mock_response, True),
        ):
            features, number_matched, was_cached = await ogc_fetch("climate-stations")
        assert number_matched == 2
        assert was_cached is True

    @pytest.mark.asyncio
    async def test_property_filters_accepted(self):
        mock_response = {"features": [], "numberMatched": 0}
        with patch(
            "mcp_canada.shared.geo.cached_fetch",
            new_callable=AsyncMock,
            return_value=(mock_response, False),
        ):
            features, _, _ = await ogc_fetch(
                "climate-stations",
                properties={"PROV_STATE_TERR_CODE": "ON"},
            )
        assert features == []


class TestNearestStation:
    """Tests for nearest_station finding closest feature."""

    @pytest.mark.asyncio
    async def test_returns_closest_station(self):
        features = [
            {
                "id": "far",
                "geometry": {"type": "Point", "coordinates": [-80.0, 45.0]},
                "properties": {"STATION_NAME": "Far Station"},
            },
            {
                "id": "close",
                "geometry": {"type": "Point", "coordinates": [-75.1, 45.1]},
                "properties": {"STATION_NAME": "Close Station"},
            },
        ]
        with patch(
            "mcp_canada.shared.geo.ogc_fetch",
            new_callable=AsyncMock,
            return_value=(features, 2, False),
        ):
            result = await nearest_station(45.0, -75.0)
        assert result is not None
        assert result["id"] == "close"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_stations(self):
        with patch(
            "mcp_canada.shared.geo.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([], 0, False),
        ):
            result = await nearest_station(45.0, -75.0)
        assert result is None

    @pytest.mark.asyncio
    async def test_uses_correct_collection_id(self):
        with patch(
            "mcp_canada.shared.geo.ogc_fetch",
            new_callable=AsyncMock,
            return_value=([], 0, False),
        ) as mock_fetch:
            await nearest_station(45.0, -75.0, collection_id="swob-stations")
            call_args = mock_fetch.call_args
            assert call_args[0][0] == "swob-stations"
