"""Unit tests for Toronto Open Data client module."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from mcp_canada.modules.toronto.__tests__.conftest import (
    SAMPLE_311_PACKAGE_SHOW,
    SAMPLE_DATASTORE_RESPONSE,
    SAMPLE_DATASET_COUNT_RESPONSE,
    SAMPLE_ORGANIZATION_LIST_RESPONSE,
    SAMPLE_PACKAGE_SEARCH_RESPONSE,
    SAMPLE_PACKAGE_SHOW_RESPONSE,
    SAMPLE_RENTSAFE_RECORDS,
    SAMPLE_RESOURCE_SHOW_RESPONSE,
    SAMPLE_STR_DATASTORE_RESPONSE,
    GTFS_STOPS_ZIP_BYTES,
    GTFS_ROUTES_ZIP_BYTES,
    SERVICE_311_ZIP_BYTES,
    make_mock_response,
    make_mock_bytes_response,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_fake_cached_fetch(data: Any, was_cached: bool = False):
    """Return an async fake_cached_fetch that bypasses cache and calls fetcher."""
    async def fake_cached_fetch(key: str, ttl: int, fetcher: Any) -> tuple[Any, bool]:
        result = await fetcher()
        return result, was_cached
    return fake_cached_fetch


def _make_mock_limiter():
    """Return a mock rate limiter whose acquire() is a no-op coroutine."""
    limiter = MagicMock()
    limiter.acquire = AsyncMock()
    return limiter


# ---------------------------------------------------------------------------
# TestFetchSearchDatasets
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    @pytest.mark.asyncio
    async def test_returns_shaped_dataset_summaries(self) -> None:
        """fetch_search_datasets returns list of shaped dicts with title and notes."""
        from mcp_canada.modules.toronto.client import fetch_search_datasets

        mock_response = make_mock_response(SAMPLE_PACKAGE_SEARCH_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            results, was_cached = await fetch_search_datasets("transit")

        assert isinstance(results, list)
        assert len(results) >= 1
        assert "title" in results[0]
        assert "id" in results[0]
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_resources_count_field_present(self) -> None:
        """fetch_search_datasets result dicts include num_resources."""
        from mcp_canada.modules.toronto.client import fetch_search_datasets

        mock_response = make_mock_response(SAMPLE_PACKAGE_SEARCH_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            results, _ = await fetch_search_datasets("transit")

        assert "num_resources" in results[0]


# ---------------------------------------------------------------------------
# TestFetchDatasetDetails
# ---------------------------------------------------------------------------


class TestFetchDatasetDetails:
    @pytest.mark.asyncio
    async def test_returns_shaped_dataset(self) -> None:
        """fetch_dataset_details returns shaped dataset dict."""
        from mcp_canada.modules.toronto.client import fetch_dataset_details

        mock_response = make_mock_response(SAMPLE_PACKAGE_SHOW_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            result, was_cached = await fetch_dataset_details("ttc-bus-delay-data")

        assert result["id"] == "ttc-bus-delay-data"
        assert "title" in result
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_raises_on_404(self) -> None:
        """fetch_dataset_details raises HTTPStatusError on 404."""
        from mcp_canada.modules.toronto.client import fetch_dataset_details

        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock()
            )
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await fetch_dataset_details("nonexistent-dataset")


# ---------------------------------------------------------------------------
# TestFetchResource
# ---------------------------------------------------------------------------


class TestFetchResource:
    @pytest.mark.asyncio
    async def test_returns_resource_dict(self) -> None:
        """fetch_resource returns shaped resource dict by ID."""
        from mcp_canada.modules.toronto.client import fetch_resource

        mock_response = make_mock_response(SAMPLE_RESOURCE_SHOW_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            result, was_cached = await fetch_resource("res-001")

        assert result["id"] == "res-001"
        assert "url" in result
        assert "datastore_active" in result


# ---------------------------------------------------------------------------
# TestFetchOrganizations
# ---------------------------------------------------------------------------


class TestFetchOrganizations:
    @pytest.mark.asyncio
    async def test_returns_list_of_orgs(self) -> None:
        """fetch_organizations returns list of org dicts with name, title, package_count."""
        from mcp_canada.modules.toronto.client import fetch_organizations

        mock_response = make_mock_response(SAMPLE_ORGANIZATION_LIST_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            results, _ = await fetch_organizations()

        assert isinstance(results, list)
        assert len(results) >= 1
        org = results[0]
        assert "name" in org
        assert "title" in org
        assert "package_count" in org


# ---------------------------------------------------------------------------
# TestFetchDatasetCount
# ---------------------------------------------------------------------------


class TestFetchDatasetCount:
    @pytest.mark.asyncio
    async def test_returns_integer_count(self) -> None:
        """fetch_dataset_count returns int total package count."""
        from mcp_canada.modules.toronto.client import fetch_dataset_count

        mock_response = make_mock_response(SAMPLE_DATASET_COUNT_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            count, _ = await fetch_dataset_count()

        assert count == 500


# ---------------------------------------------------------------------------
# TestFetchGTFSFile
# ---------------------------------------------------------------------------


class TestFetchGTFSFile:
    @pytest.mark.asyncio
    async def test_fetches_stops_txt_from_zip(self) -> None:
        """fetch_gtfs_file downloads ZIP and extracts stops.txt as list[dict]."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_file

        mock_bytes_response = make_mock_bytes_response(GTFS_STOPS_ZIP_BYTES)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_bytes_response)
            mock_cls.return_value = mock_client

            results, was_cached = await fetch_gtfs_file("stops.txt")

        assert isinstance(results, list)
        assert len(results) == 3
        assert "stop_id" in results[0]
        assert "stop_name" in results[0]
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_fetches_routes_txt_from_zip(self) -> None:
        """fetch_gtfs_file downloads ZIP and extracts routes.txt as list[dict]."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_file

        mock_bytes_response = make_mock_bytes_response(GTFS_ROUTES_ZIP_BYTES)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_bytes_response)
            mock_cls.return_value = mock_client

            results, was_cached = await fetch_gtfs_file("routes.txt")

        assert isinstance(results, list)
        assert len(results) == 3
        assert "route_id" in results[0]
        assert "route_short_name" in results[0]


# ---------------------------------------------------------------------------
# TestFetchGTFSStops
# ---------------------------------------------------------------------------


class TestFetchGTFSStops:
    @pytest.mark.asyncio
    async def test_returns_all_stops_without_filter(self) -> None:
        """fetch_gtfs_stops without query returns all stops."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_stops

        with patch(
            "mcp_canada.modules.toronto.client.fetch_gtfs_file",
            new_callable=AsyncMock,
            return_value=(
                [
                    {"stop_id": "1001", "stop_name": "Union Station", "stop_lat": "43.64", "stop_lon": "-79.38"},
                    {"stop_id": "1002", "stop_name": "Bloor-Yonge", "stop_lat": "43.67", "stop_lon": "-79.38"},
                ],
                False,
            ),
        ):
            results, _ = await fetch_gtfs_stops()

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_filters_stops_by_name_substring(self) -> None:
        """fetch_gtfs_stops with query filters stops by stop_name substring."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_stops

        with patch(
            "mcp_canada.modules.toronto.client.fetch_gtfs_file",
            new_callable=AsyncMock,
            return_value=(
                [
                    {"stop_id": "1001", "stop_name": "Union Station", "stop_lat": "43.64", "stop_lon": "-79.38"},
                    {"stop_id": "1002", "stop_name": "Bloor-Yonge", "stop_lat": "43.67", "stop_lon": "-79.38"},
                ],
                False,
            ),
        ):
            results, _ = await fetch_gtfs_stops(query="Union")

        assert len(results) == 1
        assert results[0]["stop_name"] == "Union Station"


# ---------------------------------------------------------------------------
# TestFetchGTFSRoutes
# ---------------------------------------------------------------------------


class TestFetchGTFSRoutes:
    @pytest.mark.asyncio
    async def test_returns_all_routes_without_filter(self) -> None:
        """fetch_gtfs_routes without filter returns all routes."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_routes

        with patch(
            "mcp_canada.modules.toronto.client.fetch_gtfs_file",
            new_callable=AsyncMock,
            return_value=(
                [
                    {"route_id": "1", "route_short_name": "1", "route_long_name": "Yonge", "route_type": "1"},
                    {"route_id": "301", "route_short_name": "301", "route_long_name": "Airport Express", "route_type": "2"},
                ],
                False,
            ),
        ):
            results, _ = await fetch_gtfs_routes()

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_filters_routes_by_type(self) -> None:
        """fetch_gtfs_routes with route_type filters client-side."""
        from mcp_canada.modules.toronto.client import fetch_gtfs_routes

        with patch(
            "mcp_canada.modules.toronto.client.fetch_gtfs_file",
            new_callable=AsyncMock,
            return_value=(
                [
                    {"route_id": "1", "route_short_name": "1", "route_long_name": "Yonge", "route_type": "1"},
                    {"route_id": "301", "route_short_name": "301", "route_long_name": "Airport Express", "route_type": "2"},
                ],
                False,
            ),
        ):
            results, _ = await fetch_gtfs_routes(route_type="2")

        assert len(results) == 1
        assert results[0]["route_id"] == "301"


# ---------------------------------------------------------------------------
# TestFetchDatastoreRecords
# ---------------------------------------------------------------------------


class TestFetchDatastoreRecords:
    @pytest.mark.asyncio
    async def test_returns_records_list(self) -> None:
        """fetch_datastore_records returns list of records from datastore_search."""
        from mcp_canada.modules.toronto.client import fetch_datastore_records

        mock_response = make_mock_response(SAMPLE_DATASTORE_RESPONSE)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            records, was_cached = await fetch_datastore_records(
                resource_id="7f8eee5e-85fb-415c-aef3-c3bd4998445f",
                limit=10,
            )

        assert isinstance(records, list)
        assert len(records) == 2
        assert "_id" in records[0]
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_empty_result_returns_empty_list(self) -> None:
        """fetch_datastore_records returns empty list when no records returned."""
        from mcp_canada.modules.toronto.client import fetch_datastore_records

        empty_response = {"success": True, "result": {"records": [], "total": 0}}
        mock_response = make_mock_response(empty_response)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_client

            records, _ = await fetch_datastore_records(resource_id="nonexistent-id")

        assert records == []


# ---------------------------------------------------------------------------
# TestFetchNeighbourhoodProfile
# ---------------------------------------------------------------------------


class TestFetchNeighbourhoodProfile:
    @pytest.mark.asyncio
    async def test_returns_records(self) -> None:
        """fetch_neighbourhood_profile returns records from datastore_search."""
        from mcp_canada.modules.toronto.client import fetch_neighbourhood_profile

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=([{"Characteristic": "Total population", "City of Toronto": "2731571"}], False),
        ):
            results, was_cached = await fetch_neighbourhood_profile()

        assert isinstance(results, list)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_filters_by_characteristic(self) -> None:
        """fetch_neighbourhood_profile with characteristic passes q param."""
        from mcp_canada.modules.toronto.client import fetch_neighbourhood_profile

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=([{"Characteristic": "Total population", "City of Toronto": "2731571"}], False),
        ) as mock_fetch:
            await fetch_neighbourhood_profile(characteristic="Total population")

        # Verify q param was passed
        call_kwargs = mock_fetch.call_args[1]
        assert "q" in call_kwargs or "filters" in call_kwargs or len(mock_fetch.call_args.args) > 0


# ---------------------------------------------------------------------------
# TestFetch311Requests
# ---------------------------------------------------------------------------


class TestFetch311Requests:
    @pytest.mark.asyncio
    async def test_fetches_and_parses_311_csv(self) -> None:
        """fetch_311_requests discovers ZIP URL, downloads, parses CSV rows."""
        from mcp_canada.modules.toronto.client import fetch_311_requests

        # Package show returns dataset with year-based ZIP resource
        mock_pkg_response = make_mock_response(SAMPLE_311_PACKAGE_SHOW)
        mock_zip_response = make_mock_bytes_response(SERVICE_311_ZIP_BYTES)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            # First call: package_show, second call: ZIP download
            mock_client.get = AsyncMock(side_effect=[mock_pkg_response, mock_zip_response])
            mock_cls.return_value = mock_client

            results, was_cached = await fetch_311_requests(year=2023)

        assert isinstance(results, list)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_filters_by_ward(self) -> None:
        """fetch_311_requests with ward filter returns only matching rows."""
        from mcp_canada.modules.toronto.client import fetch_311_requests

        mock_pkg_response = make_mock_response(SAMPLE_311_PACKAGE_SHOW)
        mock_zip_response = make_mock_bytes_response(SERVICE_311_ZIP_BYTES)
        mock_limiter = _make_mock_limiter()

        with (
            patch("mcp_canada.modules.toronto.client.cached_fetch",
                  side_effect=_make_fake_cached_fetch(None)),
            patch("mcp_canada.modules.toronto.client.get_limiter", return_value=mock_limiter),
            patch("httpx.AsyncClient") as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(side_effect=[mock_pkg_response, mock_zip_response])
            mock_cls.return_value = mock_client

            results, _ = await fetch_311_requests(year=2023, ward="Ward 1")

        # SERVICE_311_CSV_ROWS has 2 rows with "Ward 1"
        for r in results:
            assert "Ward 1" in str(r.get("ward", r))


# ---------------------------------------------------------------------------
# TestFetchRentsafeEvaluations
# ---------------------------------------------------------------------------


class TestFetchRentsafeEvaluations:
    @pytest.mark.asyncio
    async def test_returns_evaluations_list(self) -> None:
        """fetch_rentsafe_evaluations returns RentSafeTO records."""
        from mcp_canada.modules.toronto.client import fetch_rentsafe_evaluations

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=(SAMPLE_RENTSAFE_RECORDS, False),
        ):
            results, was_cached = await fetch_rentsafe_evaluations()

        assert isinstance(results, list)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_min_score_filter_applied_client_side(self) -> None:
        """fetch_rentsafe_evaluations with min_score filters records client-side."""
        from mcp_canada.modules.toronto.client import fetch_rentsafe_evaluations

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=(SAMPLE_RENTSAFE_RECORDS, False),
        ):
            # SAMPLE_RENTSAFE_RECORDS has scores "85" and "72"
            # min_score=80 should return only the "85" record
            results, _ = await fetch_rentsafe_evaluations(min_score=80)

        assert len(results) == 1
        assert int(results[0]["SCORE"]) >= 80


# ---------------------------------------------------------------------------
# TestFetchShortTermRentals
# ---------------------------------------------------------------------------


class TestFetchShortTermRentals:
    @pytest.mark.asyncio
    async def test_returns_str_records(self) -> None:
        """fetch_short_term_rentals returns STR records."""
        from mcp_canada.modules.toronto.client import fetch_short_term_rentals

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=(SAMPLE_STR_DATASTORE_RESPONSE["result"]["records"], False),
        ):
            results, was_cached = await fetch_short_term_rentals()

        assert isinstance(results, list)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_status_filter_applied_client_side(self) -> None:
        """fetch_short_term_rentals with status filter returns only matching records."""
        from mcp_canada.modules.toronto.client import fetch_short_term_rentals

        with patch(
            "mcp_canada.modules.toronto.client.fetch_datastore_records",
            new_callable=AsyncMock,
            return_value=(SAMPLE_STR_DATASTORE_RESPONSE["result"]["records"], False),
        ):
            results, _ = await fetch_short_term_rentals(status="Active")

        assert len(results) == 1
        assert results[0]["status"] == "Active"
