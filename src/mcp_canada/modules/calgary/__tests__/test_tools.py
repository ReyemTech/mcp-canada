"""Unit tests for Calgary module tools.py.

Covers all 5 discovery tools: envelope structure, error handling, lang passthrough.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

SAMPLE_SEARCH_DATA = {
    "results": [
        {"id": "35ra-9556", "name": "Traffic Incidents", "category": "Transportation/Transit", "tags": ["traffic"]},
        {"id": "6933-unw5", "name": "Building Permits", "category": "Business and Economic Activity", "tags": ["permits"]},
    ],
    "total": 418,
}

SAMPLE_DETAILS_DATA = {
    "details": {
        "id": "35ra-9556",
        "name": "Traffic Incidents",
        "category": "Transportation/Transit",
        "columns": [
            {"name": "Start Dt", "field_name": "start_dt", "data_type": "calendar_date", "description": ""},
        ],
        "attribution": "Calgary Roads",
        "license_name": "Open Government Licence – Calgary",
        "publication_date": "2024-01-01T00:00:00.000Z",
        "tags": ["traffic"],
    }
}

SAMPLE_QUERY_DATA = {
    "rows": [{"quadrant": "NW", "description": "Signal light out"}],
    "count": 1,
    "truncated": False,
}

SAMPLE_ORGS_DATA = {"organizations": [{"name": "Open Calgary", "dataset_count": 418}]}

SAMPLE_CATS_DATA = {
    "categories": [
        {"name": "Transportation/Transit", "count": 60},
        {"name": "Business and Economic Activity", "count": 40},
    ]
}


class TestCalgarySearchDatasetsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_search_datasets

            result = await calgary_search_datasets(query="traffic", limit=10, offset=0, lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "calgary-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert result["data"]["total"] == 418
            assert len(result["data"]["results"]) == 2

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.calgary.tools import calgary_search_datasets

            result = await calgary_search_datasets(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passthrough(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_search_datasets

            result = await calgary_search_datasets(lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestCalgaryGetDatasetDetailsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(SAMPLE_DETAILS_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_get_dataset_details

            result = await calgary_get_dataset_details(dataset_id="35ra-9556", lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "calgary-socrata"
            assert "data" in result
            assert result["data"]["details"]["id"] == "35ra-9556"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.calgary.tools import calgary_get_dataset_details

            result = await calgary_get_dataset_details(dataset_id="nope", lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestCalgaryQueryDatasetTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(SAMPLE_QUERY_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_query_dataset

            result = await calgary_query_dataset(dataset_id="35ra-9556", where="quadrant='NW'", lang="en")

            assert "_meta" in result
            assert "data" in result
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.calgary.tools import calgary_query_dataset

            result = await calgary_query_dataset(dataset_id="35ra-9556", lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestCalgaryListOrganizationsTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(SAMPLE_ORGS_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_list_organizations

            result = await calgary_list_organizations(lang="en")

            assert "_meta" in result
            assert result["data"]["organizations"][0]["name"] == "Open Calgary"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.calgary.tools import calgary_list_organizations

            result = await calgary_list_organizations(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestCalgaryListCategoriesTool:
    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(SAMPLE_CATS_DATA, False),
        ):
            from mcp_canada.modules.calgary.tools import calgary_list_categories

            result = await calgary_list_categories(lang="en")

            assert "_meta" in result
            names = {c["name"] for c in result["data"]["categories"]}
            assert "Transportation/Transit" in names

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        with patch(
            "mcp_canada.modules.calgary.tools._client.fetch_categories",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            from mcp_canada.modules.calgary.tools import calgary_list_categories

            result = await calgary_list_categories(lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"
