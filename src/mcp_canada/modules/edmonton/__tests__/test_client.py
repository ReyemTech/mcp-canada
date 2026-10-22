"""Unit tests for Edmonton module client.py.

TDD: written against the discovery-only client (search, details, query,
organizations, categories) mirroring nova_scotia's Plan 02 test shape.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from .conftest import SAMPLE_CATALOG_RESPONSE


class TestFetchSearchDatasets:
    """fetch_search_datasets returns shaped results with count."""

    @pytest.mark.asyncio
    async def test_returns_shaped_results_and_total(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)
            mock_socrata.shape_catalog_result = lambda r: {
                "id": r["resource"]["id"],
                "name": r["resource"]["name"],
                "category": r["classification"]["domain_category"],
            }

            from mcp_canada.modules.edmonton.client import fetch_search_datasets

            data, was_cached = await fetch_search_datasets(query="permits", limit=10, offset=0)

            assert "results" in data
            assert "total" in data
            assert data["total"] == 1421
            assert len(data["results"]) == 2
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_passes_app_token(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_search_datasets

            await fetch_search_datasets()

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert "app_token" in call_kwargs

    @pytest.mark.asyncio
    async def test_limit_clamped_to_1000(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_search_datasets

            await fetch_search_datasets(limit=9999)

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert call_kwargs.get("limit") <= 1000

    @pytest.mark.asyncio
    async def test_limit_clamped_minimum_1(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_search_datasets

            await fetch_search_datasets(limit=0)

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert call_kwargs.get("limit") >= 1


class TestFetchDatasetDetails:
    """fetch_dataset_details returns metadata dict."""

    @pytest.mark.asyncio
    async def test_returns_details_with_columns(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.get_dataset_metadata = AsyncMock(
                return_value={
                    "id": "24uj-dj8v",
                    "name": "General Building Permits",
                    "category": "Urban Planning & Economy",
                    "description": "List of issued building permits.",
                    "columns": [
                        {"name": "Permit Date", "field_name": "permit_date", "data_type": "calendar_date", "description": ""},
                    ],
                    "attribution": "City of Edmonton",
                    "license_name": "Open Government Licence – Edmonton",
                    "publication_date": "2024-01-01T00:00:00.000Z",
                    "tags": ["permits", "building"],
                }
            )

            from mcp_canada.modules.edmonton.client import fetch_dataset_details

            data, was_cached = await fetch_dataset_details("24uj-dj8v")

            assert "details" in data
            details = data["details"]
            assert details["id"] == "24uj-dj8v"
            assert "columns" in details
            assert "attribution" in details
            assert "license_name" in details
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_passes_dataset_id_and_app_token(self) -> None:
        flat_meta = {
            "id": "msh8-if28",
            "name": "Property Assessment Data",
            "columns": [],
            "attribution": "Assessment and Taxation",
            "license_name": "Open Government",
            "publication_date": None,
            "tags": [],
        }
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.get_dataset_metadata = AsyncMock(return_value=flat_meta)

            from mcp_canada.modules.edmonton.client import fetch_dataset_details

            await fetch_dataset_details("msh8-if28")

            call_args = mock_socrata.get_dataset_metadata.call_args
            assert "msh8-if28" in call_args[0]
            assert "app_token" in call_args[1]


class TestFetchQueryDataset:
    """fetch_query_dataset passes SoQL params through to socrata.query_dataset."""

    @pytest.mark.asyncio
    async def test_returns_rows_count_and_truncated(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(
                return_value=[{"status": "Issued", "job_description": "New single family dwelling"}]
            )

            from mcp_canada.modules.edmonton.client import fetch_query_dataset

            data, was_cached = await fetch_query_dataset(
                "24uj-dj8v", where="status='Issued'", limit=100
            )

            assert data["rows"] == [{"status": "Issued", "job_description": "New single family dwelling"}]
            assert data["count"] == 1
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_hit_limit(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[{"a": 1}, {"a": 2}])

            from mcp_canada.modules.edmonton.client import fetch_query_dataset

            data, _ = await fetch_query_dataset("24uj-dj8v", limit=2)

            assert data["truncated"] is True

    @pytest.mark.asyncio
    async def test_passes_soql_params(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.edmonton.client import fetch_query_dataset

            await fetch_query_dataset(
                "24uj-dj8v",
                where="status='Issued'",
                select="status,job_description",
                order="permit_date DESC",
                q="dwelling",
                group=None,
            )

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs["where"] == "status='Issued'"
            assert call_kwargs["select"] == "status,job_description"
            assert call_kwargs["order"] == "permit_date DESC"
            assert call_kwargs["q"] == "dwelling"


class TestFetchOrganizations:
    """fetch_organizations aggregates unique owner display names from the catalog."""

    @pytest.mark.asyncio
    async def test_aggregates_organizations_with_counts(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_organizations

            data, was_cached = await fetch_organizations()

            assert "organizations" in data
            names = {o["name"] for o in data["organizations"]}
            assert "City of Edmonton" in names
            assert was_cached is False


class TestFetchCategories:
    """fetch_categories aggregates domain_category client-side (never sends categories=)."""

    @pytest.mark.asyncio
    async def test_aggregates_categories_with_counts(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_categories

            data, was_cached = await fetch_categories()

            assert "categories" in data
            names = {c["name"] for c in data["categories"]}
            assert "Urban Planning & Economy" in names
            assert "City Administration" in names
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_never_sends_categories_param(self) -> None:
        with patch("mcp_canada.modules.edmonton.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.edmonton.client import fetch_categories

            await fetch_categories()

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert "categories" not in call_kwargs
