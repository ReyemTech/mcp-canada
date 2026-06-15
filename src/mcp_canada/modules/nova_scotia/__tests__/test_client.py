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
    """fetch_marine_aquaculture_leases returns leases dict; excludes the_geom. Plan 03 fills."""

    pass


class TestNsGetLandbasedAquacultureLicenses:
    """fetch_landbased_aquaculture_licenses returns licenses dict. Plan 03 fills."""

    pass


class TestNsGetFishHatcheryStocking:
    """fetch_fish_hatchery_stocking returns stocking records; default order=stocking_date DESC. Plan 03 fills."""

    pass


class TestNsGetAquacultureProduction:
    """fetch_aquaculture_production returns production dict; year filter as string. Plan 03 fills."""

    pass


class TestNsGetWaterQualityMonitoring:
    """fetch_water_quality_monitoring returns readings; since filter uses ISO timestamps. Plan 04 fills."""

    pass


class TestNsGetBoilWaterAdvisories:
    """fetch_boil_water_advisories returns advisories; active_only uses ACTIVE_ADVISORY_FILTER. Plan 04 fills.

    CRITICAL test: empty list is a VALID success response (no active advisories),
    not an error. Plan 04 must include a test that verifies empty list returns
    make_response with count=0, NOT make_error.
    """

    pass


class TestNsGetProtectedAreas:
    """fetch_protected_areas returns areas; excludes the_geom. Plan 04 fills."""

    pass


class TestNsGetAirQualityStations:
    """fetch_air_quality_stations returns stations catalog. Plan 04 fills."""

    pass


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
