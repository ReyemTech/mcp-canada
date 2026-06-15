"""Unit tests for shared/socrata.py — Socrata SODA API async client.

TestSharedSocrataContract pins the OUTGOING request parameters (the Manitoba/Saskatchewan
lesson: mocked tests must assert the params dict, not just the URL).

Test classes:
    TestSharedSocrataContract — outgoing params for search_catalog and query_dataset
    TestSearchCatalog         — happy path, offset omission, app_token header
    TestQueryDataset          — happy path, SoQL params, $offset omission
    TestGetDatasetMetadata    — column flattening, license_name, description truncation
    TestShapeCatalogResult    — flat dict extraction, description truncation, department
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_canada.shared.socrata import (
    MAX_DESCRIPTION_CHARS,
    get_dataset_metadata,
    query_dataset,
    search_catalog,
    shape_catalog_result,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

CATALOG_RESPONSE: dict[str, Any] = {
    "results": [
        {
            "resource": {
                "id": "h57h-p9mm",
                "name": "Nova Scotia Marine Aquaculture Leases",
                "description": "Marine aquaculture lease locations with species, ownership, and area data.",
                "type": "dataset",
                "updatedAt": "2026-01-15T00:00:00.000Z",
                "columns_name": ["license_le", "ownership", "species", "county"],
                "columns_field_name": ["license_le", "ownership", "species", "county"],
                "download_count": 8495,
            },
            "classification": {
                "domain_category": "Fishing and Aquaculture",
                "domain_tags": ["marine", "aquaculture", "leases"],
                "categories": [],
                "tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Fisheries and Aquaculture"},
                    {"key": "Detailed-Metadata_Frequency", "value": "Monthly"},
                ],
            },
            "metadata": {"domain": "data.novascotia.ca"},
            "permalink": "https://data.novascotia.ca/d/h57h-p9mm",
            "link": "https://data.novascotia.ca/Fishing-and-Aquaculture/Leases/h57h-p9mm",
            "owner": {"id": "abc", "user_type": "organization", "display_name": "Open Data Nova Scotia"},
        }
    ],
    "resultSetSize": 706,
    "timings": {},
    "warnings": [],
}

VIEWS_RESPONSE: dict[str, Any] = {
    "id": "8e4a-m6fw",
    "name": "Nova Scotia Fish Hatchery Stocking Records",
    "category": "Fishing and Aquaculture",
    "description": "Stocking records for Nova Scotia fish hatcheries.",
    "columns": [
        {"name": "County", "fieldName": "county", "dataTypeName": "text", "description": "County name"},
        {"name": "Stock Species", "fieldName": "stock", "dataTypeName": "text", "description": "Fish species stocked"},
        {"name": "Number Released", "fieldName": "number_released", "dataTypeName": "number", "description": "Count released"},
    ],
    "attribution": "NS Fisheries and Aquaculture",
    "license": {"name": "Open Government Licence – Nova Scotia"},
    "publicationDate": "2024-01-01T00:00:00.000Z",
    "viewLastModified": 1700000000,
    "tags": ["hatchery", "stocking", "fisheries"],
}

ROWS_RESPONSE: list[dict[str, Any]] = [
    {"county": "Halifax", "species": "Atlantic Salmon", "license_le": "MRL-001"},
    {"county": "Inverness", "species": "Oyster", "license_le": "MRL-002"},
]


def _make_mock_client(json_return: Any) -> MagicMock:
    """Create a mock AsyncClient whose .get() returns a response with given JSON."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=json_return)
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


# ---------------------------------------------------------------------------
# TestSharedSocrataContract — pins the outgoing params dict
# ---------------------------------------------------------------------------


class TestSharedSocrataContract:
    """Asserts shared/socrata.py sends exactly the right params to the SODA API.

    The Manitoba/Saskatchewan lesson: mocked tests that only assert the URL
    miss silent parameter errors (wrong key names, missing keys, extra keys)
    that cause live 400s. This class asserts the full params dict.
    """

    @pytest.mark.asyncio
    async def test_search_catalog_sends_correct_params_with_offset(self) -> None:
        """search_catalog(offset=10) must include 'offset' key in params."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client({"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
            MockClient.return_value = mock_client

            await search_catalog(
                "data.novascotia.ca",
                q="aquaculture",
                limit=5,
                offset=10,
                only="datasets",
            )

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            params = call_args[1].get("params", {})

            assert "data.novascotia.ca/api/catalog/v1" in url
            assert params["domains"] == "data.novascotia.ca"
            assert params["q"] == "aquaculture"
            assert params["limit"] == 5
            assert params["offset"] == 10
            assert params["only"] == "datasets"

    @pytest.mark.asyncio
    async def test_search_catalog_omits_offset_when_zero(self) -> None:
        """search_catalog(offset=0) must NOT include 'offset' in params (Pitfall 8)."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client({"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
            MockClient.return_value = mock_client

            await search_catalog("data.novascotia.ca", q="water", limit=10, offset=0)

            call_args = mock_client.get.call_args
            params = call_args[1].get("params", {})

            assert "offset" not in params

    @pytest.mark.asyncio
    async def test_search_catalog_adds_app_token_header_when_set(self) -> None:
        """search_catalog with app_token must include X-App-Token header."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client({"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
            MockClient.return_value = mock_client

            await search_catalog("data.novascotia.ca", q="water", app_token="test-token-abc")

            call_args = mock_client.get.call_args
            headers = call_args[1].get("headers", {})
            assert headers.get("X-App-Token") == "test-token-abc"

    @pytest.mark.asyncio
    async def test_search_catalog_no_app_token_header_when_none(self) -> None:
        """search_catalog without app_token must NOT include X-App-Token header."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client({"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
            MockClient.return_value = mock_client

            await search_catalog("data.novascotia.ca", q="water", app_token=None)

            call_args = mock_client.get.call_args
            headers = call_args[1].get("headers", {})
            assert "X-App-Token" not in headers

    @pytest.mark.asyncio
    async def test_query_dataset_sends_soql_params(self) -> None:
        """query_dataset must send $where, $select, $limit to /resource/{id}.json."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client([{"county": "Halifax"}])
            MockClient.return_value = mock_client

            await query_dataset(
                "data.novascotia.ca",
                "h57h-p9mm",
                where="county='Halifax'",
                select="county,species",
                limit=50,
                offset=0,
            )

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            params = call_args[1].get("params", {})

            assert "data.novascotia.ca/resource/h57h-p9mm.json" in url
            assert params["$where"] == "county='Halifax'"
            assert params["$select"] == "county,species"
            assert params["$limit"] == 50
            # offset=0 must NOT appear (Pitfall 8 / Socrata default)
            assert "$offset" not in params

    @pytest.mark.asyncio
    async def test_query_dataset_includes_offset_when_nonzero(self) -> None:
        """query_dataset(offset=100) must include '$offset' == 100 in params."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client([{"county": "Halifax"}])
            MockClient.return_value = mock_client

            await query_dataset(
                "data.novascotia.ca",
                "h57h-p9mm",
                limit=50,
                offset=100,
            )

            call_args = mock_client.get.call_args
            params = call_args[1].get("params", {})
            assert params["$offset"] == 100

    @pytest.mark.asyncio
    async def test_query_dataset_omits_optional_params_when_none(self) -> None:
        """query_dataset omits $where/$select/$order/$q/$group when not provided."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client([])
            MockClient.return_value = mock_client

            await query_dataset("data.novascotia.ca", "h57h-p9mm", limit=10)

            call_args = mock_client.get.call_args
            params = call_args[1].get("params", {})

            assert "$limit" in params
            assert "$where" not in params
            assert "$select" not in params
            assert "$order" not in params
            assert "$q" not in params
            assert "$group" not in params
            assert "$offset" not in params

    @pytest.mark.asyncio
    async def test_query_dataset_app_token_header(self) -> None:
        """query_dataset with app_token must include X-App-Token header."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client([])
            MockClient.return_value = mock_client

            await query_dataset("data.novascotia.ca", "h57h-p9mm", app_token="mytoken")

            call_args = mock_client.get.call_args
            headers = call_args[1].get("headers", {})
            assert headers.get("X-App-Token") == "mytoken"


# ---------------------------------------------------------------------------
# TestSearchCatalog — return shape + edge cases
# ---------------------------------------------------------------------------


class TestSearchCatalog:
    """Happy path and edge cases for search_catalog."""

    @pytest.mark.asyncio
    async def test_returns_raw_catalog_json(self) -> None:
        """search_catalog returns the raw catalog JSON dict."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(CATALOG_RESPONSE)
            MockClient.return_value = mock_client

            result = await search_catalog("data.novascotia.ca", q="aquaculture")

            assert isinstance(result, dict)
            assert "results" in result
            assert result["resultSetSize"] == 706

    @pytest.mark.asyncio
    async def test_only_param_defaults_to_datasets(self) -> None:
        """search_catalog passes only='datasets' by default."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client({"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
            MockClient.return_value = mock_client

            await search_catalog("data.novascotia.ca")

            call_args = mock_client.get.call_args
            params = call_args[1].get("params", {})
            assert params["only"] == "datasets"

    @pytest.mark.asyncio
    async def test_uses_injected_httpx_client(self) -> None:
        """search_catalog uses httpx_client kwarg when provided (dependency injection)."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value={"results": [], "resultSetSize": 0, "timings": {}, "warnings": []})
        injected = MagicMock()
        injected.get = AsyncMock(return_value=mock_resp)

        result = await search_catalog("data.novascotia.ca", httpx_client=injected)

        injected.get.assert_called_once()
        assert "results" in result


# ---------------------------------------------------------------------------
# TestQueryDataset — SoQL params, return type
# ---------------------------------------------------------------------------


class TestQueryDataset:
    """Happy path and parameter handling for query_dataset."""

    @pytest.mark.asyncio
    async def test_returns_list_of_row_dicts(self) -> None:
        """query_dataset returns parsed list of row dicts."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(ROWS_RESPONSE)
            MockClient.return_value = mock_client

            result = await query_dataset(
                "data.novascotia.ca",
                "h57h-p9mm",
                where="county='Halifax'",
                limit=10,
            )

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["county"] == "Halifax"

    @pytest.mark.asyncio
    async def test_all_soql_params_sent_when_provided(self) -> None:
        """All optional SoQL params appear in request when provided."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client([])
            MockClient.return_value = mock_client

            await query_dataset(
                "data.novascotia.ca",
                "h57h-p9mm",
                where="county='Halifax'",
                select="county,species",
                order="county ASC",
                limit=25,
                offset=50,
                q="salmon",
                group="county",
            )

            call_args = mock_client.get.call_args
            params = call_args[1].get("params", {})
            assert params["$where"] == "county='Halifax'"
            assert params["$select"] == "county,species"
            assert params["$order"] == "county ASC"
            assert params["$limit"] == 25
            assert params["$offset"] == 50
            assert params["$q"] == "salmon"
            assert params["$group"] == "county"

    @pytest.mark.asyncio
    async def test_uses_injected_client(self) -> None:
        """query_dataset uses httpx_client kwarg when provided."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=[])
        injected = MagicMock()
        injected.get = AsyncMock(return_value=mock_resp)

        result = await query_dataset("data.novascotia.ca", "h57h-p9mm", httpx_client=injected)

        injected.get.assert_called_once()
        assert result == []


# ---------------------------------------------------------------------------
# TestGetDatasetMetadata — column flattening, description truncation
# ---------------------------------------------------------------------------


class TestGetDatasetMetadata:
    """Tests for get_dataset_metadata column flattening and field extraction."""

    @pytest.mark.asyncio
    async def test_returns_flat_dict_with_expected_keys(self) -> None:
        """get_dataset_metadata returns a flat dict with standard keys."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(VIEWS_RESPONSE)
            MockClient.return_value = mock_client

            result = await get_dataset_metadata("data.novascotia.ca", "8e4a-m6fw")

            assert result["id"] == "8e4a-m6fw"
            assert result["name"] == "Nova Scotia Fish Hatchery Stocking Records"
            assert result["category"] == "Fishing and Aquaculture"
            assert result["license_name"] == "Open Government Licence – Nova Scotia"
            assert result["attribution"] == "NS Fisheries and Aquaculture"
            assert isinstance(result["columns"], list)
            assert isinstance(result["tags"], list)

    @pytest.mark.asyncio
    async def test_columns_are_flattened(self) -> None:
        """Columns list is flattened to {name, field_name, data_type, description}."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(VIEWS_RESPONSE)
            MockClient.return_value = mock_client

            result = await get_dataset_metadata("data.novascotia.ca", "8e4a-m6fw")

            assert len(result["columns"]) == 3
            col = result["columns"][0]
            assert "name" in col
            assert "field_name" in col
            assert "data_type" in col
            assert "description" in col
            assert col["field_name"] == "county"

    @pytest.mark.asyncio
    async def test_description_truncated_at_max_chars(self) -> None:
        """Long descriptions are truncated at MAX_DESCRIPTION_CHARS."""
        long_desc = "x" * (MAX_DESCRIPTION_CHARS + 100)
        views_with_long_desc = {**VIEWS_RESPONSE, "description": long_desc}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(views_with_long_desc)
            MockClient.return_value = mock_client

            result = await get_dataset_metadata("data.novascotia.ca", "8e4a-m6fw")

            assert len(result["description"]) <= MAX_DESCRIPTION_CHARS + 3  # +3 for "..."
            assert result["description"].endswith("...")

    @pytest.mark.asyncio
    async def test_hits_correct_views_url(self) -> None:
        """get_dataset_metadata hits /api/views/{id}.json URL."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = _make_mock_client(VIEWS_RESPONSE)
            MockClient.return_value = mock_client

            await get_dataset_metadata("data.novascotia.ca", "8e4a-m6fw")

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert "data.novascotia.ca/api/views/8e4a-m6fw.json" in url


# ---------------------------------------------------------------------------
# TestShapeCatalogResult — flat dict extraction
# ---------------------------------------------------------------------------


class TestShapeCatalogResult:
    """Tests for shape_catalog_result flatten helper."""

    def test_returns_flat_dict_with_expected_keys(self) -> None:
        """shape_catalog_result returns all documented flat keys."""
        raw_result = CATALOG_RESPONSE["results"][0]
        shaped = shape_catalog_result(raw_result)

        assert shaped["id"] == "h57h-p9mm"
        assert shaped["name"] == "Nova Scotia Marine Aquaculture Leases"
        assert shaped["category"] == "Fishing and Aquaculture"
        assert shaped["tags"] == ["marine", "aquaculture", "leases"]
        assert shaped["department"] == "Fisheries and Aquaculture"
        assert shaped["permalink"] == "https://data.novascotia.ca/d/h57h-p9mm"
        assert shaped["download_count"] == 8495
        assert shaped["type"] == "dataset"
        assert isinstance(shaped["column_names"], list)
        assert "license_le" in shaped["column_names"]

    def test_description_truncated_at_max_chars(self) -> None:
        """shape_catalog_result truncates description at MAX_DESCRIPTION_CHARS."""
        long_desc = "A" * (MAX_DESCRIPTION_CHARS + 200)
        result = {
            "resource": {
                "id": "test-id",
                "name": "Test Dataset",
                "description": long_desc,
                "type": "dataset",
                "updatedAt": "2026-01-01T00:00:00.000Z",
                "columns_name": [],
                "columns_field_name": [],
                "download_count": 0,
            },
            "classification": {
                "domain_category": "Test",
                "domain_tags": [],
                "domain_metadata": [],
            },
            "metadata": {"domain": "data.novascotia.ca"},
            "permalink": "https://data.novascotia.ca/d/test-id",
            "owner": {"display_name": "Test"},
        }
        shaped = shape_catalog_result(result)
        assert len(shaped["description"]) <= MAX_DESCRIPTION_CHARS + 3
        assert shaped["description"].endswith("...")

    def test_department_extracted_from_domain_metadata(self) -> None:
        """department is extracted from domain_metadata where key endswith 'Department'."""
        result = {
            "resource": {
                "id": "x",
                "name": "Test",
                "description": "desc",
                "type": "dataset",
                "updatedAt": "",
                "columns_name": [],
                "columns_field_name": [],
                "download_count": 0,
            },
            "classification": {
                "domain_category": "Environment",
                "domain_tags": [],
                "domain_metadata": [
                    {"key": "Detailed-Metadata_Department", "value": "Environment and Climate Change"},
                    {"key": "Detailed-Metadata_Frequency", "value": "Annual"},
                ],
            },
            "metadata": {"domain": "data.novascotia.ca"},
            "permalink": "https://data.novascotia.ca/d/x",
            "owner": {"display_name": "NS Gov"},
        }
        shaped = shape_catalog_result(result)
        assert shaped["department"] == "Environment and Climate Change"

    def test_department_none_when_no_metadata(self) -> None:
        """department is None when domain_metadata has no Department key."""
        result = {
            "resource": {
                "id": "y",
                "name": "Test2",
                "description": "",
                "type": "dataset",
                "updatedAt": "",
                "columns_name": [],
                "columns_field_name": [],
                "download_count": 0,
            },
            "classification": {
                "domain_category": "Government Administration",
                "domain_tags": [],
                "domain_metadata": [],
            },
            "metadata": {},
            "permalink": "https://data.novascotia.ca/d/y",
            "owner": {},
        }
        shaped = shape_catalog_result(result)
        assert shaped["department"] is None

    def test_updated_at_surfaced(self) -> None:
        """updated_at is extracted from resource.updatedAt."""
        raw_result = CATALOG_RESPONSE["results"][0]
        shaped = shape_catalog_result(raw_result)
        assert shaped["updated_at"] == "2026-01-15T00:00:00.000Z"
