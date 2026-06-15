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
    """ns_get_marine_aquaculture_leases tool tests."""

    LEASES_DATA = {
        "leases": [
            {
                "license_le": "MRL-001",
                "ownership": "Atlantic Shellfish Inc.",
                "species": "Eastern Oyster",
                "waterbody": "Bras d'Or Lake",
                "county": "Inverness",
                "sitestatus": "Active",
                "speciestyp": "Shellfish",
                "hectares": "3.2",
                "lat_dms": "46°01'N",
                "long_dms": "60°45'W",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_leases(self) -> None:
        """Returns _meta envelope with leases list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            new_callable=AsyncMock,
            return_value=(self.LEASES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            result = await ns_get_marine_aquaculture_leases(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert "leases" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_leases_rows_have_no_the_geom(self) -> None:
        """Returned leases data does not contain the_geom."""
        leases_with_geom = {
            "leases": [{**self.LEASES_DATA["leases"][0], "the_geom": {"type": "MultiPolygon"}}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            new_callable=AsyncMock,
            return_value=(leases_with_geom, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            result = await ns_get_marine_aquaculture_leases(lang="en")

            for row in result["data"]["leases"]:
                assert "the_geom" not in row

    @pytest.mark.asyncio
    async def test_county_and_species_type_forwarded_to_client(self) -> None:
        """county and species_type params forwarded to fetch_marine_aquaculture_leases."""
        mock_fetch = AsyncMock(return_value=(self.LEASES_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            await ns_get_marine_aquaculture_leases(county="Inverness", species_type="Shellfish", limit=100)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("county") == "Inverness"
            assert call_kwargs.get("species_type") == "Shellfish"
            assert call_kwargs.get("limit") == 100

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            result = await ns_get_marine_aquaculture_leases()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            new_callable=AsyncMock,
            return_value=(self.LEASES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            result = await ns_get_marine_aquaculture_leases(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the marine leases dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_marine_aquaculture_leases",
            new_callable=AsyncMock,
            return_value=(self.LEASES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_marine_aquaculture_leases

            result = await ns_get_marine_aquaculture_leases()

            api_url = result["_meta"]["source"]["url"]
            assert "h57h-p9mm" in api_url


class TestNsGetLandbasedAquacultureLicensesTool:
    """ns_get_landbased_aquaculture_licenses tool tests."""

    LICENSES_DATA = {
        "licenses": [
            {
                "license_le": "LBL-001",
                "species": "Atlantic Salmon",
                "speciestyp": "Finfish",
                "county": "Hants",
                "ownership": "Hatchery Farm Ltd.",
                "sitestatus": "Active",
                "lat_dms": "45°05'N",
                "long_dms": "63°44'W",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_licenses(self) -> None:
        """Returns _meta envelope with licenses list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_landbased_aquaculture_licenses",
            new_callable=AsyncMock,
            return_value=(self.LICENSES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_landbased_aquaculture_licenses

            result = await ns_get_landbased_aquaculture_licenses(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "licenses" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_county_and_species_type_forwarded_to_client(self) -> None:
        """county and species_type params forwarded to fetch_landbased_aquaculture_licenses."""
        mock_fetch = AsyncMock(return_value=(self.LICENSES_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_landbased_aquaculture_licenses",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_landbased_aquaculture_licenses

            await ns_get_landbased_aquaculture_licenses(county="Hants", species_type="Finfish", limit=50)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("county") == "Hants"
            assert call_kwargs.get("species_type") == "Finfish"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_landbased_aquaculture_licenses",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_landbased_aquaculture_licenses

            result = await ns_get_landbased_aquaculture_licenses()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_landbased_aquaculture_licenses",
            new_callable=AsyncMock,
            return_value=(self.LICENSES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_landbased_aquaculture_licenses

            result = await ns_get_landbased_aquaculture_licenses(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url contains the landbased licenses dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_landbased_aquaculture_licenses",
            new_callable=AsyncMock,
            return_value=(self.LICENSES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_landbased_aquaculture_licenses

            result = await ns_get_landbased_aquaculture_licenses()

            api_url = result["_meta"]["source"]["url"]
            assert "yqwg-f62a" in api_url


class TestNsGetFishHatcheryStockingTool:
    """ns_get_fish_hatchery_stocking tool tests."""

    STOCKING_DATA = {
        "stocking_records": [
            {
                "county": "Antigonish",
                "name": "Antigonish River",
                "type": "Stream",
                "stock": "Brook Trout",
                "stock_strain": "NS Wild",
                "hatchery": "Barra Glen Hatchery",
                "fish_length_cm": "12.5",
                "fish_weight_g": "25.0",
                "number_released": "5000",
                "stocking_date": "2025-11-19T00:00:00.000",
                "mark": "None",
                "growth_stage": "Fingerling",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_stocking_records(self) -> None:
        """Returns _meta envelope with stocking_records list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_fish_hatchery_stocking",
            new_callable=AsyncMock,
            return_value=(self.STOCKING_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_fish_hatchery_stocking

            result = await ns_get_fish_hatchery_stocking(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "stocking_records" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_stock_and_county_forwarded_to_client(self) -> None:
        """stock and county params forwarded to fetch_fish_hatchery_stocking."""
        mock_fetch = AsyncMock(return_value=(self.STOCKING_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_fish_hatchery_stocking",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_fish_hatchery_stocking

            await ns_get_fish_hatchery_stocking(stock="Brook Trout", county="Antigonish", limit=200)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("stock") == "Brook Trout"
            assert call_kwargs.get("county") == "Antigonish"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_fish_hatchery_stocking",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_fish_hatchery_stocking

            result = await ns_get_fish_hatchery_stocking()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_fish_hatchery_stocking",
            new_callable=AsyncMock,
            return_value=(self.STOCKING_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_fish_hatchery_stocking

            result = await ns_get_fish_hatchery_stocking(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url contains the hatchery stocking dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_fish_hatchery_stocking",
            new_callable=AsyncMock,
            return_value=(self.STOCKING_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_fish_hatchery_stocking

            result = await ns_get_fish_hatchery_stocking()

            api_url = result["_meta"]["source"]["url"]
            assert "8e4a-m6fw" in api_url


class TestNsGetAquacultureProductionTool:
    """ns_get_aquaculture_production tool tests."""

    PRODUCTION_DATA = {
        "production": [
            {
                "year": "2022",
                "county": "Guysborough",
                "kgs": "1250000.0",
                "total_value": "8500000.0",
                "full_time": "45.0",
                "total_employ": "60.0",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_production(self) -> None:
        """Returns _meta envelope with production list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            new_callable=AsyncMock,
            return_value=(self.PRODUCTION_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            result = await ns_get_aquaculture_production(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert "data" in result
            assert "production" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_year_and_county_forwarded_to_client(self) -> None:
        """year and county params forwarded to fetch_aquaculture_production."""
        mock_fetch = AsyncMock(return_value=(self.PRODUCTION_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            await ns_get_aquaculture_production(year="2022", county="Guysborough", limit=500)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("year") == "2022"
            assert call_kwargs.get("county") == "Guysborough"

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            result = await ns_get_aquaculture_production()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            new_callable=AsyncMock,
            return_value=(self.PRODUCTION_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            result = await ns_get_aquaculture_production(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url contains the aquaculture production dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            new_callable=AsyncMock,
            return_value=(self.PRODUCTION_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            result = await ns_get_aquaculture_production()

            api_url = result["_meta"]["source"]["url"]
            assert "v2ex-ev63" in api_url

    @pytest.mark.asyncio
    async def test_cached_true_passes_through(self) -> None:
        """cached=True from client passes through to _meta.cached."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_aquaculture_production",
            new_callable=AsyncMock,
            return_value=(self.PRODUCTION_DATA, True),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_aquaculture_production

            result = await ns_get_aquaculture_production()

            assert result["_meta"]["cached"] is True


class TestNsGetWaterQualityMonitoringTool:
    """ns_get_water_quality_monitoring tool tests."""

    WATER_QUALITY_DATA = {
        "readings": [
            {
                "station_number": "NS01EF0002",
                "date": "2024-12-06T00:00:00.000",
                "time": "12:00",
                "temperature_c": "8.3",
                "ph": "7.1",
                "specific_conductance_s_cm": "142.5",
                "dissolved_oxygen_mg_l": "11.2",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_readings(self) -> None:
        """Returns _meta envelope with readings list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_water_quality_monitoring",
            new_callable=AsyncMock,
            return_value=(self.WATER_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_water_quality_monitoring

            result = await ns_get_water_quality_monitoring(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert "readings" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_station_number_and_since_forwarded_to_client(self) -> None:
        """station_number and since params forwarded to fetch_water_quality_monitoring."""
        mock_fetch = AsyncMock(return_value=(self.WATER_QUALITY_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_water_quality_monitoring",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_water_quality_monitoring

            await ns_get_water_quality_monitoring(
                station_number="NS01EF0002", since="2024-01-01", limit=100
            )

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("station_number") == "NS01EF0002"
            assert call_kwargs.get("since") == "2024-01-01"
            assert call_kwargs.get("limit") == 100

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_water_quality_monitoring",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_water_quality_monitoring

            result = await ns_get_water_quality_monitoring()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_water_quality_monitoring",
            new_callable=AsyncMock,
            return_value=(self.WATER_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_water_quality_monitoring

            result = await ns_get_water_quality_monitoring(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the water quality readings dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_water_quality_monitoring",
            new_callable=AsyncMock,
            return_value=(self.WATER_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_water_quality_monitoring

            result = await ns_get_water_quality_monitoring()

            api_url = result["_meta"]["source"]["url"]
            assert "bkfi-mjgw" in api_url


class TestNsGetBoilWaterAdvisoriesTool:
    """ns_get_boil_water_advisories tool tests.

    CRITICAL: empty advisory list must return make_response (not make_error).
    """

    ADVISORIES_DATA = {
        "advisories": [
            {
                "site_name": "Murphy Road Water Distribution System",
                "county": "ANNAPOLIS COUNTY",
                "date_advisory_issued": "2025-03-15T00:00:00.000",
                "date_advisory_removed": None,
                "facility_type": "Community Water Supply",
                "length_of_advisory": "92",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    ADVISORIES_EMPTY_DATA = {
        "advisories": [],
        "count": 0,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_advisories(self) -> None:
        """Returns _meta envelope with advisories list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            new_callable=AsyncMock,
            return_value=(self.ADVISORIES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            result = await ns_get_boil_water_advisories(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert "data" in result
            assert "advisories" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_empty_advisories_is_valid_success_not_error(self) -> None:
        """Empty advisory list returns make_response (not make_error) — off-season valid state."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            new_callable=AsyncMock,
            return_value=(self.ADVISORIES_EMPTY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            result = await ns_get_boil_water_advisories(active_only=True)

            # Must have _meta (success), NOT error key
            assert "_meta" in result, "Empty advisory list must return make_response, not make_error"
            assert "error" not in result
            assert result["data"]["count"] == 0
            assert result["data"]["advisories"] == []

    @pytest.mark.asyncio
    async def test_county_and_active_only_forwarded_to_client(self) -> None:
        """county and active_only params forwarded to fetch_boil_water_advisories."""
        mock_fetch = AsyncMock(return_value=(self.ADVISORIES_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            await ns_get_boil_water_advisories(county="INVERNESS COUNTY", active_only=True, limit=200)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("county") == "INVERNESS COUNTY"
            assert call_kwargs.get("active_only") is True
            assert call_kwargs.get("limit") == 200

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            result = await ns_get_boil_water_advisories()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            new_callable=AsyncMock,
            return_value=(self.ADVISORIES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            result = await ns_get_boil_water_advisories(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the boil water advisories dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_boil_water_advisories",
            new_callable=AsyncMock,
            return_value=(self.ADVISORIES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_boil_water_advisories

            result = await ns_get_boil_water_advisories()

            api_url = result["_meta"]["source"]["url"]
            assert "7t68-9xmm" in api_url


class TestNsGetProtectedAreasTool:
    """ns_get_protected_areas tool tests."""

    PROTECTED_AREAS_DATA = {
        "protected_areas": [
            {
                "objectid": "1",
                "pro_name": "Kejimkujik National Park",
                "protect1": "National Park",
                "symbol": "NP",
                "owner": "Federal",
                "authority": "Parks Canada",
                "status": "Designated",
                "web_url": "https://parks.canada.ca/kejimkujik",
                "ha_gis": "381.28",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_protected_areas(self) -> None:
        """Returns _meta envelope with protected_areas list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            new_callable=AsyncMock,
            return_value=(self.PROTECTED_AREAS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            result = await ns_get_protected_areas(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert "data" in result
            assert "protected_areas" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_protected_areas_rows_have_no_the_geom(self) -> None:
        """Returned protected_areas data does not contain the_geom."""
        areas_with_geom = {
            "protected_areas": [
                {**self.PROTECTED_AREAS_DATA["protected_areas"][0], "the_geom": {"type": "MultiPolygon"}}
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            new_callable=AsyncMock,
            return_value=(areas_with_geom, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            result = await ns_get_protected_areas(lang="en")

            for row in result["data"]["protected_areas"]:
                assert "the_geom" not in row

    @pytest.mark.asyncio
    async def test_status_forwarded_to_client(self) -> None:
        """status param forwarded to fetch_protected_areas."""
        mock_fetch = AsyncMock(return_value=(self.PROTECTED_AREAS_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            await ns_get_protected_areas(status="Designated", limit=500)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("status") == "Designated"
            assert call_kwargs.get("limit") == 500

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            result = await ns_get_protected_areas()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            new_callable=AsyncMock,
            return_value=(self.PROTECTED_AREAS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            result = await ns_get_protected_areas(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the protected areas dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_protected_areas",
            new_callable=AsyncMock,
            return_value=(self.PROTECTED_AREAS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_protected_areas

            result = await ns_get_protected_areas()

            api_url = result["_meta"]["source"]["url"]
            assert "ticv-5du5" in api_url


class TestNsGetAirQualityStationsTool:
    """ns_get_air_quality_stations tool tests."""

    AIR_QUALITY_DATA = {
        "stations": [
            {
                "national_air_pollution_surveillance_network_id": "NS001",
                "station_name": "Halifax Central",
                "city": "Halifax",
                "latitude": "44.6501",
                "longitude": "-63.5751",
                "measurements": "PM2.5, O3, NO2, SO2",
                "monitoring_period": "2000-present",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_stations(self) -> None:
        """Returns _meta envelope with stations list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_air_quality_stations",
            new_callable=AsyncMock,
            return_value=(self.AIR_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_air_quality_stations

            result = await ns_get_air_quality_stations(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert "data" in result
            assert "stations" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_city_forwarded_to_client(self) -> None:
        """city param forwarded to fetch_air_quality_stations."""
        mock_fetch = AsyncMock(return_value=(self.AIR_QUALITY_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_air_quality_stations",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_air_quality_stations

            await ns_get_air_quality_stations(city="Dartmouth", limit=50)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("city") == "Dartmouth"
            assert call_kwargs.get("limit") == 50

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_air_quality_stations",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_air_quality_stations

            result = await ns_get_air_quality_stations()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_air_quality_stations",
            new_callable=AsyncMock,
            return_value=(self.AIR_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_air_quality_stations

            result = await ns_get_air_quality_stations(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the air quality stations dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_air_quality_stations",
            new_callable=AsyncMock,
            return_value=(self.AIR_QUALITY_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_air_quality_stations

            result = await ns_get_air_quality_stations()

            api_url = result["_meta"]["source"]["url"]
            assert "3bbm-drnh" in api_url


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
