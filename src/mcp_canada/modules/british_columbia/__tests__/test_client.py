"""Wave 0 test class scaffolds for british_columbia client functions.

Plans 02 and 03 fill in the actual test implementations.
Each class has one xfail placeholder so pytest --collect-only counts them.
"""

from __future__ import annotations

import pytest


class TestFetchSearchDatasets:
    """Tests for fetch_search_datasets (CKAN package_search). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestFetchDatasetDetails:
    """Tests for fetch_dataset_details (CKAN package_show) including queryable_via_wfs derivation.

    Plan 02 asserts that datasets with bcdc_type=geographic + bc geographic warehouse
    storage_location + object_name get queryable_via_wfs=True.
    """

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestFetchOrganizations:
    """Tests for fetch_organizations (CKAN organization_list). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestFetchTags:
    """Tests for fetch_tags (CKAN tag_list). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestWfsFetchShared:
    """Tests for _wfs_fetch — caching, rate limiting, pagination cap. Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestQueryableViaWfsDetection:
    """Tests for the queryable_via_wfs derivation logic in fetch_dataset_details.

    A dataset is WFS-queryable when it has a resource with:
    - bcdc_type = "geographic"
    - resource_storage_location containing "bc geographic warehouse"
    - object_name is not None/empty

    Plan 02 implements this logic.
    """

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False
