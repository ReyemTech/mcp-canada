"""Unit tests for Nova Scotia module tools.py.

Plans 02-05 fill the per-tool test class bodies.
Plan 07 fills TestNsEnvelopes and TestNsLangParam with parametrized tests
covering all tools for envelope structure and bilingual lang= passthrough.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from .conftest import (
    SAMPLE_CATALOG_RESPONSE,
    SAMPLE_VIEWS_METADATA,
)

# Sample shaped catalog results (what client returns after shape_catalog_result)
SAMPLE_SEARCH_DATA = {
    "results": [
        {
            "id": "h57h-p9mm",
            "name": "Nova Scotia Marine Aquaculture Leases",
            "category": "Fishing and Aquaculture",
            "tags": ["marine", "aquaculture"],
        },
        {
            "id": "7t68-9xmm",
            "name": "Boil Water Advisories",
            "category": "Environment and Energy",
            "tags": ["water", "advisory"],
        },
    ],
    "total": 706,
}

SAMPLE_DETAILS_DATA = {
    "details": {
        "id": "8e4a-m6fw",
        "name": "Nova Scotia Fish Hatchery Stocking Records",
        "category": "Fishing and Aquaculture",
        "columns": [
            {"name": "County", "field_name": "county", "data_type": "text", "description": "NS county"},
        ],
        "attribution": "NS Fisheries and Aquaculture",
        "license_name": "Open Government Licence – Nova Scotia",
        "publication_date": "2024-01-01T00:00:00.000Z",
        "tags": ["hatchery"],
    }
}

SAMPLE_QUERY_DATA = {
    "rows": [{"county": "Halifax", "species": "Oyster"}],
    "count": 1,
    "truncated": False,
}

SAMPLE_ORGS_DATA = {
    "organizations": [
        {"name": "Open Data Nova Scotia", "dataset_count": 706},
    ]
}

SAMPLE_CATS_DATA = {
    "categories": [
        {"name": "Fishing and Aquaculture", "count": 85},
        {"name": "Environment and Energy", "count": 62},
    ]
}


class TestNsSearchDatasetsTools:
    """ns_search_datasets tool tests."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        """Returns _meta envelope with results, total, offset, limit."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_search_datasets

            result = await ns_search_datasets(query="aquaculture", limit=10, offset=0, lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert result["data"]["total"] == 706
            assert len(result["data"]["results"]) == 2

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            side_effect=Exception("connection timeout"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_search_datasets

            result = await ns_search_datasets(query="broken", lang="en")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"
            assert "message" in result["error"]

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang in response."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, True),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_search_datasets

            result = await ns_search_datasets(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_offset_and_limit_in_data(self) -> None:
        """Response data includes offset and limit for pagination."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(SAMPLE_SEARCH_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_search_datasets

            result = await ns_search_datasets(query="water", limit=5, offset=20)

            assert result["data"]["offset"] == 20
            assert result["data"]["limit"] == 5


class TestNsGetDatasetDetailsTool:
    """ns_get_dataset_details tool tests."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        """Returns _meta envelope with dataset details."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(SAMPLE_DETAILS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_dataset_details

            result = await ns_get_dataset_details(dataset_id="8e4a-m6fw", lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            details = result["data"]["details"]
            assert details["id"] == "8e4a-m6fw"
            assert "columns" in details
            assert "attribution" in details
            assert "license_name" in details

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=Exception("not found"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_dataset_details

            result = await ns_get_dataset_details(dataset_id="xxxx-xxxx")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(SAMPLE_DETAILS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_dataset_details

            result = await ns_get_dataset_details(dataset_id="8e4a-m6fw", lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestNsQueryDatasetTool:
    """ns_query_dataset tool tests."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        """Returns _meta envelope with rows, count, truncated."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(SAMPLE_QUERY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_query_dataset

            result = await ns_query_dataset(
                dataset_id="h57h-p9mm",
                where="county='Halifax'",
                limit=10,
                lang="en",
            )

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "rows" in result["data"]
            assert "count" in result["data"]
            assert "truncated" in result["data"]

    @pytest.mark.asyncio
    async def test_all_soql_params_forwarded(self) -> None:
        """All SoQL params (where/select/order/limit/offset/q/group/include_geometry) reach client."""
        mock_fetch = AsyncMock(return_value=(SAMPLE_QUERY_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_query_dataset",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_query_dataset

            await ns_query_dataset(
                dataset_id="h57h-p9mm",
                where="county='Halifax'",
                select="county,species",
                order="county ASC",
                limit=50,
                offset=10,
                q="oyster",
                group="county",
                include_geometry=True,
                lang="en",
            )

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("where") == "county='Halifax'"
            assert call_kwargs.get("select") == "county,species"
            assert call_kwargs.get("order") == "county ASC"
            assert call_kwargs.get("limit") == 50
            assert call_kwargs.get("offset") == 10
            assert call_kwargs.get("q") == "oyster"
            assert call_kwargs.get("group") == "county"
            assert call_kwargs.get("include_geometry") is True

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            side_effect=Exception("SoQL error"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_query_dataset

            result = await ns_query_dataset(dataset_id="h57h-p9mm")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(SAMPLE_QUERY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_query_dataset

            result = await ns_query_dataset(dataset_id="h57h-p9mm", lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestNsListOrganizationsTool:
    """ns_list_organizations tool tests."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        """Returns _meta envelope with organizations list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(SAMPLE_ORGS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_organizations

            result = await ns_list_organizations(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "organizations" in result["data"]

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_organizations

            result = await ns_list_organizations()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(SAMPLE_ORGS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_organizations

            result = await ns_list_organizations(lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestNsListCategoriesTool:
    """ns_list_categories tool tests."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope(self) -> None:
        """Returns _meta envelope with categories list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(SAMPLE_CATS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_categories

            result = await ns_list_categories(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "categories" in result["data"]
            cats = result["data"]["categories"]
            assert len(cats) == 2
            assert cats[0]["name"] == "Fishing and Aquaculture"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_categories",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_categories

            result = await ns_list_categories()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(SAMPLE_CATS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_categories

            result = await ns_list_categories(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_cached_true_passes_through(self) -> None:
        """cached=True from client passes through to _meta.cached."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(SAMPLE_CATS_DATA, True),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_list_categories

            result = await ns_list_categories()

            assert result["_meta"]["cached"] is True


# ---------------------------------------------------------------------------
# Plan 03-05 placeholder classes (filled by future plans)
# ---------------------------------------------------------------------------


class TestNsGetMarineAquacultureLeasesTool:
    """ns_get_marine_aquaculture_leases tool tests. Plan 03 fills."""

    pass


class TestNsGetLandbasedAquacultureLicensesTool:
    """ns_get_landbased_aquaculture_licenses tool tests. Plan 03 fills."""

    pass


class TestNsGetFishHatcheryStockingTool:
    """ns_get_fish_hatchery_stocking tool tests. Plan 03 fills."""

    pass


class TestNsGetAquacultureProductionTool:
    """ns_get_aquaculture_production tool tests. Plan 03 fills."""

    pass


class TestNsGetWaterQualityMonitoringTool:
    """ns_get_water_quality_monitoring tool tests. Plan 04 fills."""

    pass


class TestNsGetBoilWaterAdvisoriesTool:
    """ns_get_boil_water_advisories tool tests. Plan 04 fills.

    CRITICAL: must include a test that verifies empty advisory list returns
    make_response (not make_error) — no active advisories is a valid state.
    """

    pass


class TestNsGetProtectedAreasTool:
    """ns_get_protected_areas tool tests. Plan 04 fills."""

    pass


class TestNsGetAirQualityStationsTool:
    """ns_get_air_quality_stations tool tests. Plan 04 fills."""

    pass


class TestNsGetHealthFacilitiesTool:
    """ns_get_health_facilities tool tests. Plan 05 fills."""

    pass


class TestNsGetVitalStatisticsTool:
    """ns_get_vital_statistics tool tests. Plan 05 fills."""

    pass


class TestNsGetChronicDiseasePrevalenceTool:
    """ns_get_chronic_disease_prevalence tool tests. Plan 05 fills."""

    pass


class TestNsEnvelopes:
    """Parametrized envelope tests for all ns_ tools. Plan 07 fills.

    Must verify:
    - _meta key present in all tool responses
    - _meta.source.api == "nova-scotia-socrata"
    - _meta.cached is bool
    - _meta.lang matches the lang= argument
    - error responses have error.code and error.message
    """

    pass


class TestNsLangParam:
    """Parametrized lang= passthrough tests for all ns_ tools. Plan 07 fills.

    Must verify:
    - lang='fr' passes through to make_response → _meta.lang == 'fr'
    - lang='en' passes through to make_response → _meta.lang == 'en'
    """

    pass
