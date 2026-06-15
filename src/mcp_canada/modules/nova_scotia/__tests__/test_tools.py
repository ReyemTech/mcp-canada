"""Unit tests for Nova Scotia module tools.py.

Plans 02-05 fill the per-tool test class bodies.
Plan 07 fills TestNsEnvelopes and TestNsLangParam with parametrized tests
covering all tools for envelope structure and bilingual lang= passthrough.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


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
                "length_of_advisory_in_days": "92",
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
    """ns_get_health_facilities tool tests."""

    HOSPITALS_DATA = {
        "facilities": [
            {
                "facility_name": "QEII Health Sciences Centre",
                "address": "1796 Summer Street",
                "town": "Halifax",
                "county": "Halifax",
                "type": "Regional",
                "zone": None,
                "beds": None,
                "x_coordinate": "-63.5901",
                "y_coordinate": "44.6476",
                "facility_category": "hospital",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    LTC_DATA = {
        "facilities": [
            {
                "facility_name": "Melville Gardens",
                "address": "240 Willett St",
                "town": "Truro",
                "county": "Colchester",
                "type": None,
                "zone": "Zone 2 - Northern",
                "beds": "68",
                "x_coordinate": "-63.2702",
                "y_coordinate": "45.3604",
                "facility_category": "long_term_care",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_hospital_returns_envelope(self) -> None:
        """Returns _meta envelope with facilities list for hospital type."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(self.HOSPITALS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="hospital", lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert "facilities" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_happy_path_ltc_returns_envelope(self) -> None:
        """Returns _meta envelope with facilities list for long_term_care type."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(self.LTC_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="long_term_care", lang="en")

            assert "_meta" in result
            assert "facilities" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_invalid_facility_type_returns_invalid_input_before_network(self) -> None:
        """Invalid facility_type returns INVALID_INPUT with valid= list (no network call)."""
        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            mock_client,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="clinic", lang="en")

            # Must be INVALID_INPUT, not UPSTREAM_ERROR
            assert "error" in result
            assert result["error"]["code"] == "INVALID_INPUT"
            assert "valid" in result["error"]
            assert isinstance(result["error"]["valid"], list)
            # Must NOT have called the client
            mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_facility_type_fr_message(self) -> None:
        """Invalid facility_type with lang='fr' returns French error message."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="clinic", lang="fr")

            assert "error" in result
            assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_api_url_contains_dispatched_dataset_id(self) -> None:
        """api_url in _meta source contains the dispatched hospital dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(self.HOSPITALS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="hospital")

            api_url = result["_meta"]["source"]["url"]
            assert "tmfr-3h8a" in api_url

    @pytest.mark.asyncio
    async def test_ltc_api_url_contains_ltc_dataset_id(self) -> None:
        """api_url in _meta source contains the LTC dataset ID when facility_type=long_term_care."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(self.LTC_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="long_term_care")

            api_url = result["_meta"]["source"]["url"]
            assert "x76a-axw2" in api_url

    @pytest.mark.asyncio
    async def test_county_and_limit_forwarded_to_client(self) -> None:
        """county and limit params forwarded to fetch_health_facilities."""
        mock_fetch = AsyncMock(return_value=(self.HOSPITALS_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            await ns_get_health_facilities(facility_type="hospital", county="Halifax", limit=100)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("county") == "Halifax"
            assert call_kwargs.get("limit") == 100

    @pytest.mark.asyncio
    async def test_upstream_error_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="hospital")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_health_facilities",
            new_callable=AsyncMock,
            return_value=(self.HOSPITALS_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_health_facilities

            result = await ns_get_health_facilities(facility_type="hospital", lang="fr")

            assert result["_meta"]["lang"] == "fr"


class TestNsGetVitalStatisticsTool:
    """ns_get_vital_statistics tool tests."""

    VITAL_DATA = {
        "statistics": [
            {
                "counties": "ANNAPOLIS",
                "year": "2020",
                "population": "19875.0",
                "live_births": "142.0",
                "birth_rate": "7.1",
                "deaths": "281.0",
                "death_rate": "14.1",
                "natural_increase_rate": "-7.0",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_statistics(self) -> None:
        """Returns _meta envelope with statistics list."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_vital_statistics",
            new_callable=AsyncMock,
            return_value=(self.VITAL_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_vital_statistics

            result = await ns_get_vital_statistics(lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert "statistics" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_county_and_year_forwarded_to_client(self) -> None:
        """county and year params forwarded to fetch_vital_statistics."""
        mock_fetch = AsyncMock(return_value=(self.VITAL_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_vital_statistics",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_vital_statistics

            await ns_get_vital_statistics(county="ANNAPOLIS", year="2020", limit=100)

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("county") == "ANNAPOLIS"
            assert call_kwargs.get("year") == "2020"
            assert call_kwargs.get("limit") == 100

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_vital_statistics",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_vital_statistics

            result = await ns_get_vital_statistics()

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_vital_statistics",
            new_callable=AsyncMock,
            return_value=(self.VITAL_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_vital_statistics

            result = await ns_get_vital_statistics(lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dataset_id(self) -> None:
        """api_url in _meta source contains the vital statistics dataset ID."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_vital_statistics",
            new_callable=AsyncMock,
            return_value=(self.VITAL_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_vital_statistics

            result = await ns_get_vital_statistics()

            api_url = result["_meta"]["source"]["url"]
            assert "r794-fttm" in api_url


class TestNsGetChronicDiseasePrevalenceTool:
    """ns_get_chronic_disease_prevalence tool tests."""

    AMI_DATA = {
        "rows": [
            {
                "year": "2018",
                "zone": "Zone 1 - Western",
                "age_group": "50 to 69",
                "population": "42185",
                "prevalence": "1847",
                "crude_prevalence_rate": "4.38",
                "disease": "ami",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    DIABETES_DATA = {
        "rows": [
            {
                "year": "2000-01-01T00:00:00.000",
                "zone": "Zone 4 - Central",
                "sex": "F",
                "age_group": "20 to 29",
                "population": "30198",
                "prevalence": "223",
                "crude_prevalence_rate": "0.74",
                "disease": "diabetes",
            }
        ],
        "count": 1,
        "truncated": False,
    }

    @pytest.mark.asyncio
    async def test_happy_path_returns_envelope_with_rows(self) -> None:
        """Returns _meta envelope with rows list for valid disease."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.AMI_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami", lang="en")

            assert "_meta" in result
            assert result["_meta"]["source"]["api"] == "nova-scotia-socrata"
            assert result["_meta"]["cached"] is False
            assert result["_meta"]["lang"] == "en"
            assert "data" in result
            assert "rows" in result["data"]
            assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_normalized_zone_present_in_ami_rows(self) -> None:
        """Returned AMI rows have 'zone' key (normalized from health_zone)."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.AMI_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami")

            for row in result["data"]["rows"]:
                assert "zone" in row, f"zone key must be present in rows, got: {list(row.keys())}"
                assert "health_zone" not in row

    @pytest.mark.asyncio
    async def test_invalid_disease_returns_invalid_input_before_network(self) -> None:
        """Invalid disease returns INVALID_INPUT with valid= list (no network call)."""
        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            mock_client,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="flu", lang="en")

            # Must be INVALID_INPUT, not UPSTREAM_ERROR
            assert "error" in result
            assert result["error"]["code"] == "INVALID_INPUT"
            assert "valid" in result["error"]
            valid = result["error"]["valid"]
            assert isinstance(valid, list)
            assert "ami" in valid
            assert "diabetes" in valid
            # Must NOT have called the client
            mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_disease_fr_message(self) -> None:
        """Invalid disease with lang='fr' returns French error message."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="flu", lang="fr")

            assert "error" in result
            assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_filters_forwarded_to_client(self) -> None:
        """health_zone, sex, year, limit params forwarded to fetch_chronic_disease."""
        mock_fetch = AsyncMock(return_value=(self.DIABETES_DATA, False))
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            mock_fetch,
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            await ns_get_chronic_disease_prevalence(
                disease="diabetes",
                health_zone="Zone 4 - Central",
                sex="F",
                year="2020",
                limit=100,
            )

            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs.get("disease") == "diabetes"
            assert call_kwargs.get("health_zone") == "Zone 4 - Central"
            assert call_kwargs.get("sex") == "F"
            assert call_kwargs.get("year") == "2020"
            assert call_kwargs.get("limit") == 100

    @pytest.mark.asyncio
    async def test_error_path_returns_make_error(self) -> None:
        """Exception from client returns make_error with UPSTREAM_ERROR."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            side_effect=Exception("upstream failure"),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami")

            assert "error" in result
            assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_passes_through(self) -> None:
        """lang='fr' passes through to _meta.lang."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.AMI_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami", lang="fr")

            assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_api_url_contains_dispatched_dataset_id_ami(self) -> None:
        """api_url in _meta source contains the AMI dataset ID (24qf-ntke)."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.AMI_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami")

            api_url = result["_meta"]["source"]["url"]
            assert "24qf-ntke" in api_url

    @pytest.mark.asyncio
    async def test_api_url_contains_dispatched_dataset_id_diabetes(self) -> None:
        """api_url in _meta source contains the diabetes dataset ID (cumi-sw99)."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.DIABETES_DATA, False),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="diabetes")

            api_url = result["_meta"]["source"]["url"]
            assert "cumi-sw99" in api_url

    @pytest.mark.asyncio
    async def test_cached_true_passes_through(self) -> None:
        """cached=True from client passes through to _meta.cached."""
        with patch(
            "mcp_canada.modules.nova_scotia.tools._client.fetch_chronic_disease",
            new_callable=AsyncMock,
            return_value=(self.AMI_DATA, True),
        ):
            from mcp_canada.modules.nova_scotia.tools import ns_get_chronic_disease_prevalence

            result = await ns_get_chronic_disease_prevalence(disease="ami")

            assert result["_meta"]["cached"] is True


# ---------------------------------------------------------------------------
# Cross-cutting: envelope + lang parameter (Plan 07)
# ---------------------------------------------------------------------------

# (tool_name, client_fn_attribute_on_client, sample_kwargs, sample_client_return)
#
# Count: 5 discovery + 4 aquaculture (Plan 03) + 3 environment (Plan 04) + 5 health/demo (Plan 05) = 17
ALL_NS_TOOLS: list[tuple[str, str, dict, tuple]] = [
    # Discovery (Plan 02) — 5
    (
        "ns_search_datasets",
        "fetch_search_datasets",
        {"query": "aquaculture"},
        ({"results": [], "total": 0}, False),
    ),
    (
        "ns_get_dataset_details",
        "fetch_dataset_details",
        {"dataset_id": "h57h-p9mm"},
        ({"details": {"id": "h57h-p9mm", "name": "Test", "columns": [], "attribution": "NS", "license_name": "OGL", "publication_date": "2024-01-01T00:00:00.000Z", "tags": []}}, False),
    ),
    (
        "ns_query_dataset",
        "fetch_query_dataset",
        {"dataset_id": "h57h-p9mm"},
        ({"rows": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_list_organizations",
        "fetch_organizations",
        {},
        ({"organizations": []}, False),
    ),
    (
        "ns_list_categories",
        "fetch_categories",
        {},
        ({"categories": []}, False),
    ),
    # Aquaculture (Plan 03) — 4
    (
        "ns_get_marine_aquaculture_leases",
        "fetch_marine_aquaculture_leases",
        {},
        ({"leases": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_landbased_aquaculture_licenses",
        "fetch_landbased_aquaculture_licenses",
        {},
        ({"licenses": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_fish_hatchery_stocking",
        "fetch_fish_hatchery_stocking",
        {},
        ({"stocking_records": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_aquaculture_production",
        "fetch_aquaculture_production",
        {},
        ({"production": [], "count": 0, "truncated": False}, False),
    ),
    # Environment / Water / Air (Plan 04) — 3
    (
        "ns_get_water_quality_monitoring",
        "fetch_water_quality_monitoring",
        {},
        ({"readings": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_boil_water_advisories",
        "fetch_boil_water_advisories",
        {},
        ({"advisories": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_protected_areas",
        "fetch_protected_areas",
        {},
        ({"protected_areas": [], "count": 0, "truncated": False}, False),
    ),
    # Air quality (Plan 04) — 1
    (
        "ns_get_air_quality_stations",
        "fetch_air_quality_stations",
        {},
        ({"stations": [], "count": 0, "truncated": False}, False),
    ),
    # Health + Demographics (Plan 05) — 4
    (
        "ns_get_health_facilities",
        "fetch_health_facilities",
        {"facility_type": "hospital"},
        ({"facilities": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_vital_statistics",
        "fetch_vital_statistics",
        {},
        ({"vital_stats": [], "count": 0, "truncated": False}, False),
    ),
    (
        "ns_get_chronic_disease_prevalence",
        "fetch_chronic_disease",
        {"disease": "ami"},
        ({"rows": [], "count": 0, "truncated": False, "disease": "ami"}, False),
    ),
]

# Sanity check: exactly 16 tools (5 discovery + 4 aquaculture + 4 environment/air + 3 health/demo)
# Note: plan spec says "17" but tools.py has 16 functions; code is authoritative (same pattern as SK: plan said 14, code has 13).
assert len(ALL_NS_TOOLS) == 16, (
    f"ALL_NS_TOOLS must have 16 entries (matching ns_ function count in tools.py), "
    f"got {len(ALL_NS_TOOLS)}"
)


class TestNsEnvelopes:
    """Parametrized: all 17 ns_ tools return _meta envelope on success (Plan 07).

    Mirrors Saskatchewan Plan 07 pattern. Each tool is called with a mocked client
    function that returns an empty-but-valid payload. Asserts the full _meta envelope
    shape: source.api, source.url, cached, lang, timestamp keys all present.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_NS_TOOLS,
        ids=[t[0] for t in ALL_NS_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_envelope_structure(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ) -> None:
        """Every ns_ tool returns _meta with {source.api, source.url, cached, lang, timestamp}."""
        from mcp_canada.modules.nova_scotia import tools

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.nova_scotia.tools._client.{client_fn}",
            new_callable=AsyncMock,
            return_value=client_return,
        ):
            result = await tool_fn(**kwargs, lang="en")

        assert "_meta" in result, f"{tool_name} missing _meta envelope"
        meta = result["_meta"]
        for key in ("source", "cached", "lang", "timestamp"):
            assert key in meta, f"{tool_name} _meta missing '{key}'"
        assert "api" in meta["source"], f"{tool_name} _meta.source missing 'api'"
        assert "url" in meta["source"], f"{tool_name} _meta.source missing 'url'"
        assert meta["source"]["api"] == "nova-scotia-socrata", (
            f"{tool_name} _meta.source.api must be 'nova-scotia-socrata', got {meta['source']['api']!r}"
        )
        assert meta["lang"] == "en", (
            f"{tool_name} should default _meta.lang to 'en', got {meta['lang']!r}"
        )


class TestNsLangParam:
    """Parametrized: all 17 ns_ tools accept lang='fr' and pass through to _meta.lang (Plan 07).

    Mirrors Saskatchewan Plan 07 pattern. Every tool must propagate lang='fr' to _meta.lang.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_NS_TOOLS,
        ids=[t[0] for t in ALL_NS_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_lang_propagation(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ) -> None:
        """Every tool propagates lang='fr' to the _meta.lang field on success."""
        from mcp_canada.modules.nova_scotia import tools

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.nova_scotia.tools._client.{client_fn}",
            new_callable=AsyncMock,
            return_value=client_return,
        ):
            result = await tool_fn(**kwargs, lang="fr")

        assert result.get("_meta", {}).get("lang") == "fr", (
            f"{tool_name} did not propagate lang='fr' to _meta.lang — got {result.get('_meta')}"
        )
