"""Unit tests for Edmonton module tools.py.

Covers all 5 discovery tools: envelope structure, error handling, lang passthrough.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

SAMPLE_SEARCH_DATA = {
    "results": [
        {"id": "24uj-dj8v", "name": "General Building Permits", "category": "Urban Planning & Economy", "tags": ["permits"]},
        {"id": "msh8-if28", "name": "Property Assessment Data", "category": "City Administration", "tags": ["assessment"]},
    ],
    "total": 1421,
}

SAMPLE_DETAILS_DATA = {
    "details": {
        "id": "24uj-dj8v",
        "name": "General Building Permits",
        "category": "Urban Planning & Economy",
        "columns": [
            {"name": "Permit Date", "field_name": "permit_date", "data_type": "calendar_date", "description": ""},
        ],
        "attribution": "City of Edmonton",
        "license_name": "Open Government Licence – Edmonton",
        "publication_date": "2024-01-01T00:00:00.000Z",
        "tags": ["permits"],
    }
}

SAMPLE_QUERY_DATA = {
    "rows": [{"status": "Issued", "job_description": "New single family dwelling"}],
    "count": 1,
    "truncated": False,
}

SAMPLE_ORGS_DATA = {"organizations": [{"name": "City of Edmonton", "dataset_count": 1421}]}

SAMPLE_CATS_DATA = {
    "categories": [
        {"name": "Urban Planning & Economy", "count": 200},
        {"name": "City Administration", "count": 150},
    ]
}


class TestEdmontonSearchDatasetsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_search_datasets

            result = await edmonton_search_datasets(query="permits", limit=10, offset=0, lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "edmonton-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert result["data"]["total"] == 1421
            assert len(result["data"]["results"]) == 2

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_search_datasets

            result = await edmonton_search_datasets(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passthrough(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_search_datasets

            result = await edmonton_search_datasets(lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestEdmontonGetDatasetDetailsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(SAMPLE_DETAILS_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_get_dataset_details

            result = await edmonton_get_dataset_details(dataset_id="24uj-dj8v", lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "edmonton-socrata"
            assert "data" in result
            assert result["data"]["details"]["id"] == "24uj-dj8v"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_get_dataset_details

            result = await edmonton_get_dataset_details(dataset_id="nope", lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestEdmontonQueryDatasetTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(SAMPLE_QUERY_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_query_dataset

            result = await edmonton_query_dataset(dataset_id="24uj-dj8v", where="status='Issued'", lang="en")

            assert "_meta" in result
            assert "data" in result
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_query_dataset

            result = await edmonton_query_dataset(dataset_id="24uj-dj8v", lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestEdmontonListOrganizationsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(SAMPLE_ORGS_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_list_organizations

            result = await edmonton_list_organizations(lang="en")

            assert "_meta" in result
            assert result["data"]["organizations"][0]["name"] == "City of Edmonton"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_list_organizations

            result = await edmonton_list_organizations(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestEdmontonListCategoriesTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(SAMPLE_CATS_DATA, False),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_list_categories

            result = await edmonton_list_categories(lang="en")

            assert "_meta" in result
            names = {c["name"] for c in result["data"]["categories"]}
            assert "Urban Planning & Economy" in names

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.edmonton.tools._client.fetch_categories",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.edmonton.tools import edmonton_list_categories

            result = await edmonton_list_categories(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"
