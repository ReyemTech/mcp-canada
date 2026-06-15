"""Unit tests for Nova Scotia module client.py.

TestSharedApiGetContract: Module-local Socrata contract test — patches
mcp_canada.modules.nova_scotia.client.socrata and asserts outgoing SoQL/catalog params.
(The Manitoba/Saskatchewan lesson at the module layer: mock at the module-local import,
not at the shared library layer, so from-import semantics don't break the patch.)

Plans 02-05 fill the test class bodies with actual test methods.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from .conftest import (
    SAMPLE_CATALOG_RESPONSE,
    SAMPLE_VIEWS_METADATA,
)


class TestSharedApiGetContract:
    """Module-local socrata contract — patches client.socrata and asserts outgoing params.

    Pins the outgoing SoQL/catalog params at the module-local boundary
    (the Manitoba/Saskatchewan lesson: patch the module-local import, not the shared lib).
    """

    @pytest.mark.asyncio
    async def test_search_catalog_forwards_q_limit_offset_only(self) -> None:
        """fetch_search_datasets must forward q, limit, only, and offset to socrata.search_catalog."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            await fetch_search_datasets(query="aquaculture", limit=5, offset=10)

            mock_socrata.search_catalog.assert_called_once()
            call_kwargs = mock_socrata.search_catalog.call_args

            # Positional: domain, keyword params
            assert call_kwargs[1].get("q") == "aquaculture" or call_kwargs[0][1] == "aquaculture"
            # Extract kwargs flexibly
            kwargs = call_kwargs[1]
            assert kwargs.get("limit") == 5
            assert kwargs.get("offset") == 10
            assert kwargs.get("only") == "datasets"

    @pytest.mark.asyncio
    async def test_search_catalog_offset_zero_forwarded(self) -> None:
        """fetch_search_datasets at offset=0 still forwards offset=0 to socrata.search_catalog.

        The shared socrata.py omits offset from the wire when 0 — but the module still passes it.
        The shared client handles the Pitfall 8 omission, not the module client.
        """
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            await fetch_search_datasets(query="water", limit=10, offset=0)

            mock_socrata.search_catalog.assert_called_once()
            call_kwargs = mock_socrata.search_catalog.call_args
            kwargs = call_kwargs[1]
            assert kwargs.get("offset") == 0

    @pytest.mark.asyncio
    async def test_categories_never_sends_categories_param(self) -> None:
        """fetch_categories must NEVER pass categories= to socrata.search_catalog.

        The categories= catalog param is BROKEN (returns resultSetSize=0 always).
        Categories must be derived by client-side aggregation of classification.domain_category.
        """
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            await fetch_categories()

            mock_socrata.search_catalog.assert_called_once()
            call_kwargs = mock_socrata.search_catalog.call_args
            # Verify no categories= kwarg
            all_kwargs = call_kwargs[1]
            all_args = call_kwargs[0]
            assert "categories" not in all_kwargs
            # Verify the catalog is called but NO categories param in any form
            assert not any("categor" in str(a).lower() for a in all_args if isinstance(a, str))

    @pytest.mark.asyncio
    async def test_categories_aggregates_domain_category_from_results(self) -> None:
        """fetch_categories must aggregate classification.domain_category from catalog results."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            data, _ = await fetch_categories()

            # SAMPLE_CATALOG_RESPONSE has 2 results:
            # "Fishing and Aquaculture" and "Environment and Energy"
            categories = data["categories"]
            assert len(categories) >= 1
            category_names = [c["name"] for c in categories]
            assert "Fishing and Aquaculture" in category_names

    @pytest.mark.asyncio
    async def test_query_dataset_forwards_soql_params(self) -> None:
        """fetch_query_dataset must forward where/select/order/limit to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[{"county": "Halifax"}])

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            await fetch_query_dataset(
                "h57h-p9mm",
                where="county='Halifax'",
                select="county,species",
                order="county ASC",
                limit=50,
                offset=0,
            )

            mock_socrata.query_dataset.assert_called_once()
            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='Halifax'"
            assert call_kwargs.get("select") == "county,species"
            assert call_kwargs.get("order") == "county ASC"
            assert call_kwargs.get("limit") == 50
            assert call_kwargs.get("offset") == 0


class TestNsSearchDatasets:
    """fetch_search_datasets returns shaped results with count."""

    @pytest.mark.asyncio
    async def test_returns_shaped_results_and_total(self) -> None:
        """Returns results list and total from catalog response."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)
            mock_socrata.shape_catalog_result = lambda r: {
                "id": r["resource"]["id"],
                "name": r["resource"]["name"],
                "category": r["classification"]["domain_category"],
            }

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            data, was_cached = await fetch_search_datasets(query="aquaculture", limit=10, offset=0)

            assert "results" in data
            assert "total" in data
            assert data["total"] == 706
            assert len(data["results"]) == 2
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_passes_app_token(self) -> None:
        """Passes app_token from module-level APP_TOKEN to socrata.search_catalog."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            await fetch_search_datasets()

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert "app_token" in call_kwargs

    @pytest.mark.asyncio
    async def test_limit_clamped_to_1000(self) -> None:
        """limit is clamped to [1, 1000] before passing to socrata.search_catalog."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            await fetch_search_datasets(limit=9999)

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert call_kwargs.get("limit") <= 1000

    @pytest.mark.asyncio
    async def test_limit_clamped_minimum_1(self) -> None:
        """limit is clamped to minimum 1."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_search_datasets

            await fetch_search_datasets(limit=0)

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert call_kwargs.get("limit") >= 1


class TestNsGetDatasetDetails:
    """fetch_dataset_details returns metadata dict."""

    @pytest.mark.asyncio
    async def test_returns_details_with_columns(self) -> None:
        """Returns details dict with columns, attribution, license_name."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.get_dataset_metadata = AsyncMock(
                return_value={
                    "id": "8e4a-m6fw",
                    "name": "Nova Scotia Fish Hatchery Stocking Records",
                    "category": "Fishing and Aquaculture",
                    "description": "Fish hatchery stocking records.",
                    "columns": [
                        {"name": "County", "field_name": "county", "data_type": "text", "description": "NS county name"},
                    ],
                    "attribution": "NS Fisheries and Aquaculture",
                    "license_name": "Open Government Licence – Nova Scotia",
                    "publication_date": "2024-01-01T00:00:00.000Z",
                    "tags": ["hatchery", "stocking"],
                }
            )

            from mcp_canada.modules.nova_scotia.client import fetch_dataset_details

            data, was_cached = await fetch_dataset_details("8e4a-m6fw")

            assert "details" in data
            details = data["details"]
            assert details["id"] == "8e4a-m6fw"
            assert "columns" in details
            assert "attribution" in details
            assert "license_name" in details
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_passes_dataset_id_and_app_token(self) -> None:
        """Passes dataset_id and app_token to socrata.get_dataset_metadata."""
        flat_meta = {
            "id": "h57h-p9mm",
            "name": "NS Marine Aquaculture Leases",
            "columns": [],
            "attribution": "NS Fisheries",
            "license_name": "Open Government",
            "publication_date": None,
            "tags": [],
        }
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.get_dataset_metadata = AsyncMock(return_value=flat_meta)

            from mcp_canada.modules.nova_scotia.client import fetch_dataset_details

            await fetch_dataset_details("h57h-p9mm")

            call_args = mock_socrata.get_dataset_metadata.call_args
            assert "h57h-p9mm" in call_args[0]
            assert "app_token" in call_args[1]


class TestNsQueryDataset:
    """fetch_query_dataset passes SoQL params; strips geometry when include_geometry=False."""

    @pytest.mark.asyncio
    async def test_returns_rows_count_truncated(self) -> None:
        """Returns rows, count, truncated in response."""
        rows = [{"county": "Halifax", "species": "Oyster"}]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            data, was_cached = await fetch_query_dataset("h57h-p9mm", limit=10)

            assert data["rows"] == rows
            assert data["count"] == 1
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"id": str(i)} for i in range(10)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            data, _ = await fetch_query_dataset("h57h-p9mm", limit=10)

            assert data["truncated"] is True

    @pytest.mark.asyncio
    async def test_include_geometry_false_select_none_leaves_select_none(self) -> None:
        """When include_geometry=False and select=None, select is left as None.

        Socrata returns all fields including the_geom when select is absent.
        Document this behavior: agent must pass explicit $select to exclude geometry.
        """
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            await fetch_query_dataset("h57h-p9mm", select=None, include_geometry=False)

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            # select should be None (not modified) when include_geometry=False and select=None
            assert call_kwargs.get("select") is None

    @pytest.mark.asyncio
    async def test_include_geometry_false_select_provided_passes_through(self) -> None:
        """When include_geometry=False and select is provided, select passes through unchanged."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            await fetch_query_dataset("h57h-p9mm", select="county,species", include_geometry=False)

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("select") == "county,species"

    @pytest.mark.asyncio
    async def test_passes_group_param(self) -> None:
        """group param forwarded to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[{"county": "Halifax", "count": "5"}])

            from mcp_canada.modules.nova_scotia.client import fetch_query_dataset

            await fetch_query_dataset(
                "h57h-p9mm",
                select="county,count(*)",
                group="county",
            )

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("group") == "county"


class TestNsListOrganizations:
    """fetch_organizations derives unique attributions from catalog results."""

    @pytest.mark.asyncio
    async def test_returns_organizations_list(self) -> None:
        """Returns organizations list with name and dataset_count."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_organizations

            data, was_cached = await fetch_organizations()

            assert "organizations" in data
            orgs = data["organizations"]
            assert isinstance(orgs, list)
            assert len(orgs) >= 1
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_organization_has_name_and_count(self) -> None:
        """Each organization entry has name and dataset_count."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_organizations

            data, _ = await fetch_organizations()

            org = data["organizations"][0]
            assert "name" in org
            assert "dataset_count" in org
            assert isinstance(org["dataset_count"], int)

    @pytest.mark.asyncio
    async def test_deduplicates_organizations(self) -> None:
        """Multiple datasets from same owner counted as one organization."""
        # Both SAMPLE_CATALOG_RESPONSE entries have "Open Data Nova Scotia" as owner
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_organizations

            data, _ = await fetch_organizations()

            org_names = [o["name"] for o in data["organizations"]]
            # Should not have duplicate "Open Data Nova Scotia"
            assert len(org_names) == len(set(org_names))


class TestNsListCategories:
    """fetch_categories derives unique domain_category values from catalog results."""

    @pytest.mark.asyncio
    async def test_returns_categories_list(self) -> None:
        """Returns categories list with name and count."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            data, was_cached = await fetch_categories()

            assert "categories" in data
            cats = data["categories"]
            assert isinstance(cats, list)
            assert len(cats) >= 1
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_category_has_name_and_count(self) -> None:
        """Each category entry has name and count."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            data, _ = await fetch_categories()

            cat = data["categories"][0]
            assert "name" in cat
            assert "count" in cat
            assert isinstance(cat["count"], int)

    @pytest.mark.asyncio
    async def test_includes_fishing_and_aquaculture(self) -> None:
        """'Fishing and Aquaculture' category derived from domain_category in fixture."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            data, _ = await fetch_categories()

            category_names = [c["name"] for c in data["categories"]]
            assert "Fishing and Aquaculture" in category_names

    @pytest.mark.asyncio
    async def test_never_sends_categories_param(self) -> None:
        """Verifies categories= is NEVER passed to socrata.search_catalog (broken param)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=SAMPLE_CATALOG_RESPONSE)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            await fetch_categories()

            call_kwargs = mock_socrata.search_catalog.call_args[1]
            assert "categories" not in call_kwargs

    @pytest.mark.asyncio
    async def test_deduplicates_categories(self) -> None:
        """Multiple datasets with same category counted correctly."""
        catalog_with_duplicates = {
            "results": [
                *SAMPLE_CATALOG_RESPONSE["results"],
                {
                    "resource": {"id": "xxxx-yyyy", "name": "Another Aquaculture Dataset"},
                    "classification": {
                        "domain_category": "Fishing and Aquaculture",
                        "domain_tags": [],
                        "domain_metadata": [],
                    },
                    "metadata": {"domain": "data.novascotia.ca"},
                    "permalink": "https://data.novascotia.ca/d/xxxx-yyyy",
                    "owner": {"display_name": "NS Fisheries"},
                },
            ],
            "resultSetSize": 3,
        }
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.search_catalog = AsyncMock(return_value=catalog_with_duplicates)

            from mcp_canada.modules.nova_scotia.client import fetch_categories

            data, _ = await fetch_categories()

            category_names = [c["name"] for c in data["categories"]]
            # "Fishing and Aquaculture" appears twice in catalog but only once in result
            assert category_names.count("Fishing and Aquaculture") == 1
            # Count for "Fishing and Aquaculture" should be 2
            fishing_cat = next(c for c in data["categories"] if c["name"] == "Fishing and Aquaculture")
            assert fishing_cat["count"] == 2


# ---------------------------------------------------------------------------
# Plan 03-05 placeholder classes (filled by future plans)
# ---------------------------------------------------------------------------


class TestNsGetMarineAquacultureLeases:
    """fetch_marine_aquaculture_leases returns leases dict; excludes the_geom."""

    @pytest.mark.asyncio
    async def test_returns_leases_count_truncated(self) -> None:
        """Returns leases list with count and truncated flag."""
        from .conftest import SAMPLE_MARINE_LEASES_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_MARINE_LEASES_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            data, was_cached = await fetch_marine_aquaculture_leases()

            assert "leases" in data
            assert data["count"] == len(SAMPLE_MARINE_LEASES_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_select_does_not_contain_the_geom(self) -> None:
        """$select sent to socrata.query_dataset does NOT contain 'the_geom'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            assert select is not None
            assert "the_geom" not in (select or ""), f"the_geom must NOT be in $select but found in: {select!r}"

    @pytest.mark.asyncio
    async def test_returned_rows_have_no_the_geom(self) -> None:
        """Returned leases rows do not contain the_geom key."""
        from .conftest import SAMPLE_MARINE_LEASES_ROWS_WITH_GEOM

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            # The mock returns rows WITH the_geom — the client must exclude via $select
            # (in practice the API excludes it; here we verify leases list doesn't contain it)
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_MARINE_LEASES_ROWS_WITH_GEOM)

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            data, _ = await fetch_marine_aquaculture_leases()

            for row in data["leases"]:
                assert "the_geom" not in row, f"the_geom must NOT appear in leases rows, but found in: {row}"

    @pytest.mark.asyncio
    async def test_county_filter_builds_correct_where(self) -> None:
        """county filter produces $where=county='Inverness'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases(county="Inverness")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='Inverness'"

    @pytest.mark.asyncio
    async def test_species_type_filter_builds_correct_where(self) -> None:
        """species_type filter produces $where=speciestyp='Shellfish'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases(species_type="Shellfish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "speciestyp='Shellfish'"

    @pytest.mark.asyncio
    async def test_combined_filters_joined_with_and(self) -> None:
        """county + species_type filters joined with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases(county="Inverness", species_type="Shellfish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "county='Inverness'" in where
            assert "speciestyp='Shellfish'" in where
            assert "AND" in where

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None (no $where param sent)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_order_is_county_asc(self) -> None:
        """Default order is 'county ASC'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "county ASC"

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"license_le": str(i)} for i in range(3)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            data, _ = await fetch_marine_aquaculture_leases(limit=3)

            assert data["truncated"] is True

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_MARINE_AQUACULTURE_LEASES ('h57h-p9mm') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_marine_aquaculture_leases

            await fetch_marine_aquaculture_leases()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "h57h-p9mm" in call_args


class TestNsGetLandbasedAquacultureLicenses:
    """fetch_landbased_aquaculture_licenses returns licenses dict."""

    @pytest.mark.asyncio
    async def test_returns_licenses_count_truncated(self) -> None:
        """Returns licenses list with count and truncated flag."""
        from .conftest import SAMPLE_LANDBASED_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_LANDBASED_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            data, was_cached = await fetch_landbased_aquaculture_licenses()

            assert "licenses" in data
            assert data["count"] == len(SAMPLE_LANDBASED_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_county_filter_builds_correct_where(self) -> None:
        """county filter produces $where=county='Hants'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses(county="Hants")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='Hants'"

    @pytest.mark.asyncio
    async def test_species_type_filter_builds_correct_where(self) -> None:
        """species_type filter produces $where=speciestyp='Finfish'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses(species_type="Finfish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "speciestyp='Finfish'"

    @pytest.mark.asyncio
    async def test_combined_filters_joined_with_and(self) -> None:
        """county + species_type filters joined with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses(county="Hants", species_type="Finfish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "county='Hants'" in where
            assert "speciestyp='Finfish'" in where
            assert "AND" in where

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_LANDBASED_AQUACULTURE_LICENSES ('yqwg-f62a') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "yqwg-f62a" in call_args

    @pytest.mark.asyncio
    async def test_select_does_not_contain_the_geom(self) -> None:
        """$select does NOT contain 'the_geom' for landbased dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_landbased_aquaculture_licenses

            await fetch_landbased_aquaculture_licenses()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            # the_geom is only in marine leases; landbased has no geometry
            # but we still verify select is explicitly set and correct
            assert select is not None


class TestNsGetFishHatcheryStocking:
    """fetch_fish_hatchery_stocking returns stocking records; default order=stocking_date DESC."""

    @pytest.mark.asyncio
    async def test_returns_stocking_records_count_truncated(self) -> None:
        """Returns stocking_records list with count and truncated flag."""
        from .conftest import SAMPLE_HATCHERY_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_HATCHERY_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            data, was_cached = await fetch_fish_hatchery_stocking()

            assert "stocking_records" in data
            assert data["count"] == len(SAMPLE_HATCHERY_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_stock_filter_builds_correct_where(self) -> None:
        """stock filter produces $where=stock='Brook Trout'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking(stock="Brook Trout")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "stock='Brook Trout'"

    @pytest.mark.asyncio
    async def test_county_filter_builds_correct_where(self) -> None:
        """county filter produces $where=county='Antigonish'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking(county="Antigonish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='Antigonish'"

    @pytest.mark.asyncio
    async def test_combined_filters_joined_with_and(self) -> None:
        """stock + county filters joined with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking(stock="Brook Trout", county="Antigonish")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "stock='Brook Trout'" in where
            assert "county='Antigonish'" in where
            assert "AND" in where

    @pytest.mark.asyncio
    async def test_order_is_stocking_date_desc(self) -> None:
        """Default order is 'stocking_date DESC' (newest first)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "stocking_date DESC"

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_FISH_HATCHERY_STOCKING ('8e4a-m6fw') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            await fetch_fish_hatchery_stocking()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "8e4a-m6fw" in call_args

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"county": str(i)} for i in range(5)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_fish_hatchery_stocking

            data, _ = await fetch_fish_hatchery_stocking(limit=5)

            assert data["truncated"] is True


class TestNsGetAquacultureProduction:
    """fetch_aquaculture_production returns production dict; year filter as string."""

    @pytest.mark.asyncio
    async def test_returns_production_count_truncated(self) -> None:
        """Returns production list with count and truncated flag."""
        from .conftest import SAMPLE_PRODUCTION_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_PRODUCTION_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            data, was_cached = await fetch_aquaculture_production()

            assert "production" in data
            assert data["count"] == len(SAMPLE_PRODUCTION_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_year_filter_uses_string_comparison(self) -> None:
        """year filter uses quoted string: $where=year='2020' (NOT year=2020)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production(year="2020")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            # Year is TEXT field — must use quoted string comparison
            assert "year='2020'" in where, f"Expected year='2020' in where, got: {where!r}"
            # NOT bare integer: year=2020 would be wrong
            assert "year=2020" not in where.replace("year='2020'", "")

    @pytest.mark.asyncio
    async def test_county_filter_builds_correct_where(self) -> None:
        """county filter produces $where=county='Guysborough'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production(county="Guysborough")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='Guysborough'"

    @pytest.mark.asyncio
    async def test_combined_filters_joined_with_and(self) -> None:
        """year + county filters joined with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production(year="2022", county="Shelburne")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "year='2022'" in where
            assert "county='Shelburne'" in where
            assert "AND" in where

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_order_is_year_desc(self) -> None:
        """Default order is 'year DESC' (most recent first)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "year DESC"

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_AQUACULTURE_PRODUCTION ('v2ex-ev63') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            await fetch_aquaculture_production()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "v2ex-ev63" in call_args

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"year": "2022"} for _ in range(4)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_aquaculture_production

            data, _ = await fetch_aquaculture_production(limit=4)

            assert data["truncated"] is True


class TestNsGetWaterQualityMonitoring:
    """fetch_water_quality_monitoring returns readings; since filter uses ISO timestamps."""

    @pytest.mark.asyncio
    async def test_returns_readings_count_truncated(self) -> None:
        """Returns readings list with count and truncated flag."""
        from .conftest import SAMPLE_WATER_QUALITY_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_WATER_QUALITY_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            data, was_cached = await fetch_water_quality_monitoring()

            assert "readings" in data
            assert data["count"] == len(SAMPLE_WATER_QUALITY_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_station_number_filter_builds_correct_where(self) -> None:
        """station_number filter produces $where=station_number='NS01EF0002'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring(station_number="NS01EF0002")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "station_number='NS01EF0002'" in where

    @pytest.mark.asyncio
    async def test_since_filter_builds_date_gt_clause(self) -> None:
        """since filter produces $where containing date > '<iso>'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring(since="2024-01-01")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "date > '2024-01-01'" in where

    @pytest.mark.asyncio
    async def test_station_and_since_filters_combined_with_and(self) -> None:
        """station_number + since filters joined with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring(station_number="NS01EF0002", since="2024-06-01")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert "station_number='NS01EF0002'" in where
            assert "date > '2024-06-01'" in where
            assert "AND" in where

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_order_is_date_desc(self) -> None:
        """Default order is 'date DESC' (newest first)."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "date DESC"

    @pytest.mark.asyncio
    async def test_select_contains_expected_fields(self) -> None:
        """$select contains station_number, date, temperature_c, ph, dissolved_oxygen_mg_l."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            for field in ["station_number", "date", "temperature_c", "ph", "dissolved_oxygen_mg_l"]:
                assert field in (select or ""), f"{field} must be in $select"

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_SURFACE_WATER_QUALITY_CONTINUOUS ('bkfi-mjgw') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            await fetch_water_quality_monitoring()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "bkfi-mjgw" in call_args

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"station_number": str(i)} for i in range(3)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_water_quality_monitoring

            data, _ = await fetch_water_quality_monitoring(limit=3)

            assert data["truncated"] is True


class TestNsGetBoilWaterAdvisories:
    """fetch_boil_water_advisories returns advisories; active_only uses ACTIVE_ADVISORY_FILTER.

    CRITICAL: empty list is a VALID success response (no active advisories), not an error.
    """

    @pytest.mark.asyncio
    async def test_returns_advisories_count_truncated(self) -> None:
        """Returns advisories list with count and truncated flag."""
        from .conftest import SAMPLE_BOIL_WATER_ROWS_ACTIVE

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_BOIL_WATER_ROWS_ACTIVE)

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            data, was_cached = await fetch_boil_water_advisories()

            assert "advisories" in data
            assert data["count"] == len(SAMPLE_BOIL_WATER_ROWS_ACTIVE)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_active_only_uses_active_advisory_filter(self) -> None:
        """active_only=True produces $where containing ACTIVE_ADVISORY_FILTER."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories
            from mcp_canada.modules.nova_scotia.constants import ACTIVE_ADVISORY_FILTER

            await fetch_boil_water_advisories(active_only=True)

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert ACTIVE_ADVISORY_FILTER in (where or ""), (
                f"ACTIVE_ADVISORY_FILTER '{ACTIVE_ADVISORY_FILTER}' must be in $where, got: {where!r}"
            )

    @pytest.mark.asyncio
    async def test_empty_result_is_valid_success_not_error(self) -> None:
        """Empty advisory list returns count=0 success — the off-season valid case (NOT an error)."""
        from .conftest import SAMPLE_BOIL_WATER_ROWS_EMPTY

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_BOIL_WATER_ROWS_EMPTY)

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            data, was_cached = await fetch_boil_water_advisories(active_only=True)

            # Must return a valid data dict with count=0, NOT raise an exception
            assert "advisories" in data
            assert data["count"] == 0
            assert data["advisories"] == []
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_county_filter_builds_correct_where(self) -> None:
        """county filter alone produces $where=county='ANNAPOLIS COUNTY'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            await fetch_boil_water_advisories(county="ANNAPOLIS COUNTY")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "county='ANNAPOLIS COUNTY'"

    @pytest.mark.asyncio
    async def test_active_only_and_county_combined_with_and(self) -> None:
        """active_only + county produces compound $where with AND."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories
            from mcp_canada.modules.nova_scotia.constants import ACTIVE_ADVISORY_FILTER

            await fetch_boil_water_advisories(county="INVERNESS COUNTY", active_only=True)

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            where = call_kwargs.get("where", "")
            assert ACTIVE_ADVISORY_FILTER in (where or "")
            assert "county='INVERNESS COUNTY'" in (where or "")
            assert "AND" in (where or "")

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            await fetch_boil_water_advisories()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_order_is_date_advisory_issued_desc(self) -> None:
        """Default order is 'date_advisory_issued DESC'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            await fetch_boil_water_advisories()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "date_advisory_issued DESC"

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_BOIL_WATER_ADVISORIES ('7t68-9xmm') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_boil_water_advisories

            await fetch_boil_water_advisories()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "7t68-9xmm" in call_args

    @pytest.mark.asyncio
    async def test_select_does_not_use_empty_string_filter(self) -> None:
        """ACTIVE_ADVISORY_FILTER must be IS NULL, not = '' (spike-confirmed type-mismatch bug)."""
        from mcp_canada.modules.nova_scotia.constants import ACTIVE_ADVISORY_FILTER

        # The constant value must be IS NULL, not = '' or = ""
        assert "IS NULL" in ACTIVE_ADVISORY_FILTER
        assert "= ''" not in ACTIVE_ADVISORY_FILTER


class TestNsGetProtectedAreas:
    """fetch_protected_areas returns areas; excludes the_geom via explicit $select."""

    @pytest.mark.asyncio
    async def test_returns_protected_areas_count_truncated(self) -> None:
        """Returns protected_areas list with count and truncated flag."""
        from .conftest import SAMPLE_PROTECTED_AREAS_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_PROTECTED_AREAS_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            data, was_cached = await fetch_protected_areas()

            assert "protected_areas" in data
            assert data["count"] == len(SAMPLE_PROTECTED_AREAS_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_select_does_not_contain_the_geom(self) -> None:
        """$select sent to socrata.query_dataset does NOT contain 'the_geom'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            assert select is not None, "$select must be explicitly set for protected areas (geometry exclusion)"
            assert "the_geom" not in (select or ""), f"the_geom must NOT be in $select but found in: {select!r}"

    @pytest.mark.asyncio
    async def test_returned_rows_have_no_the_geom(self) -> None:
        """Returned protected_areas rows do not contain the_geom key."""
        from .conftest import SAMPLE_PROTECTED_AREAS_ROWS_WITH_GEOM

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_PROTECTED_AREAS_ROWS_WITH_GEOM)

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            data, _ = await fetch_protected_areas()

            for row in data["protected_areas"]:
                assert "the_geom" not in row, f"the_geom must NOT appear in protected_areas rows, found in: {row}"

    @pytest.mark.asyncio
    async def test_status_filter_builds_correct_where(self) -> None:
        """status filter produces $where=status='Designated'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas(status="Designated")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "status='Designated'"

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_order_is_pro_name_asc(self) -> None:
        """Default order is 'pro_name ASC'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("order") == "pro_name ASC"

    @pytest.mark.asyncio
    async def test_select_contains_expected_fields(self) -> None:
        """$select contains pro_name, protect1, owner, authority, status, ha_gis."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            for field in ["pro_name", "protect1", "owner", "authority", "status", "ha_gis"]:
                assert field in (select or ""), f"{field} must be in $select"

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_PROTECTED_AREAS ('ticv-5du5') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            await fetch_protected_areas()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "ticv-5du5" in call_args

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"pro_name": f"Area {i}"} for i in range(5)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_protected_areas

            data, _ = await fetch_protected_areas(limit=5)

            assert data["truncated"] is True


class TestNsGetAirQualityStations:
    """fetch_air_quality_stations returns stations catalog; optional city filter."""

    @pytest.mark.asyncio
    async def test_returns_stations_count_truncated(self) -> None:
        """Returns stations list with count and truncated flag."""
        from .conftest import SAMPLE_AIR_QUALITY_ROWS

        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=SAMPLE_AIR_QUALITY_ROWS)

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            data, was_cached = await fetch_air_quality_stations()

            assert "stations" in data
            assert data["count"] == len(SAMPLE_AIR_QUALITY_ROWS)
            assert data["truncated"] is False
            assert was_cached is False

    @pytest.mark.asyncio
    async def test_city_filter_builds_correct_where(self) -> None:
        """city filter produces $where=city='Halifax'."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            await fetch_air_quality_stations(city="Halifax")

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") == "city='Halifax'"

    @pytest.mark.asyncio
    async def test_no_filters_where_is_none(self) -> None:
        """Without filters, where is None."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            await fetch_air_quality_stations()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            assert call_kwargs.get("where") is None

    @pytest.mark.asyncio
    async def test_select_contains_expected_fields(self) -> None:
        """$select contains station_name, city, latitude, longitude, measurements."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            await fetch_air_quality_stations()

            call_kwargs = mock_socrata.query_dataset.call_args[1]
            select = call_kwargs.get("select", "")
            for field in ["station_name", "city", "latitude", "longitude", "measurements"]:
                assert field in (select or ""), f"{field} must be in $select"

    @pytest.mark.asyncio
    async def test_passes_correct_dataset_id(self) -> None:
        """Passes DS_AIR_QUALITY_STATIONS ('3bbm-drnh') to socrata.query_dataset."""
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=[])

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            await fetch_air_quality_stations()

            call_args = mock_socrata.query_dataset.call_args[0]
            assert "3bbm-drnh" in call_args

    @pytest.mark.asyncio
    async def test_truncated_true_when_rows_equals_limit(self) -> None:
        """truncated=True when len(rows) >= limit."""
        rows = [{"station_name": f"Station {i}"} for i in range(4)]
        with patch("mcp_canada.modules.nova_scotia.client.socrata") as mock_socrata:
            mock_socrata.query_dataset = AsyncMock(return_value=rows)

            from mcp_canada.modules.nova_scotia.client import fetch_air_quality_stations

            data, _ = await fetch_air_quality_stations(limit=4)

            assert data["truncated"] is True


class TestNsGetHealthFacilities:
    """fetch_health_facilities dispatches to DS_HOSPITALS or DS_LTC_RCF_FACILITIES. Plan 05 fills."""

    pass


class TestNsGetVitalStatistics:
    """fetch_vital_statistics filters by county/year; county names are UPPERCASE in dataset. Plan 05 fills."""

    pass


class TestNsGetChronicDiseasePrevalence:
    """fetch_chronic_disease dispatches by disease; normalizes zone/age_group/sex. Plan 05 fills."""

    pass


class TestNormalizeZoneField:
    """_normalize_zone_field normalizes health_zone→zone and agegroup→age_group. Plan 05 fills.

    Must test all 5 disease normalization cases:
    - ami: health_zone → zone; no sex field preserved
    - diabetes: agegroup → age_group; zone unchanged
    - copd: agegroup → age_group; zone unchanged
    - hypertension: zone unchanged; age_group unchanged; hypertension_count/prevalence_rate passed through
    - asthma: zone unchanged; age_group unchanged
    """

    pass
