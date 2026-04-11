"""Unit tests for quebec module client functions.

Wave 0 scaffolds — all test bodies are pytest.skip("Plan NN implements").
Plans 02/03/04 replace skip bodies with real assertions.

CRITICAL TEST CONTRACT (Phase 15 lesson):
  TestSharedApiGetContract patches `mcp_canada.modules.quebec.client.api_get`
  (the local binding in client.py) with raw-dict AsyncMock return values.
  NEVER use MagicMock(json=lambda: {...}) pattern — that masks the dict-vs-Response
  contract bug that caused Phase 15 gap closure.
"""

import pytest
from unittest.mock import AsyncMock, patch

import httpx

from mcp_canada.modules.quebec import client as q_client

pytestmark = pytest.mark.asyncio


class TestSharedApiGetContract:
    """Contract tests for _api_get — Plan 02 fills.

    Critical Phase 15 lesson: _api_get MUST treat shared api_get return
    as a parsed dict. Patches `mcp_canada.modules.quebec.client.api_get`
    (the local binding) with an AsyncMock returning a raw dict.

    The patch target is `mcp_canada.modules.quebec.client.api_get` because that is
    the name bound in client.py's namespace (via `from mcp_canada.shared.http import api_get`).
    Patching the shared layer directly would NOT intercept calls in this module.
    """

    async def test_success_envelope_unwraps_result(self):
        pytest.skip("Plan 02 implements")

    async def test_ckan_success_false_raises_http_status_error(self):
        pytest.skip("Plan 02 implements")

    async def test_non_dict_return_raises(self):
        pytest.skip("Plan 02 implements")


# ---------------------------------------------------------------------------
# Discovery client — Plan 02
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    async def test_returns_shaped_summary_list(self):
        pytest.skip("Plan 02")

    async def test_applies_organization_filter(self):
        pytest.skip("Plan 02")

    async def test_applies_group_filter(self):
        pytest.skip("Plan 02")

    async def test_empty_results_returns_empty_list(self):
        pytest.skip("Plan 02")


class TestFetchDatasetDetails:
    async def test_returns_details_with_resources(self):
        pytest.skip("Plan 02")

    async def test_surfaces_datastore_active_flag(self):
        pytest.skip("Plan 02")

    async def test_not_found_raises(self):
        pytest.skip("Plan 02")


class TestFetchOrganizations:
    async def test_returns_org_list(self):
        pytest.skip("Plan 02")

    async def test_result_is_cached(self):
        pytest.skip("Plan 02")


class TestFetchCategories:
    async def test_uses_group_list_not_tag_list(self):
        pytest.skip("Plan 02")

    async def test_returns_10_groups(self):
        pytest.skip("Plan 02")


class TestFetchQueryDataset:
    async def test_picks_best_file_resource(self):
        pytest.skip("Plan 02")

    async def test_routes_to_datastore_when_active(self):
        pytest.skip("Plan 02")

    async def test_falls_back_to_csv_when_no_datastore(self):
        pytest.skip("Plan 02")


# ---------------------------------------------------------------------------
# Health / MSSS — Plan 03
# ---------------------------------------------------------------------------


class TestFetchHealthInstallations:
    async def test_returns_installation_list(self):
        pytest.skip("Plan 03")

    async def test_filters_by_clsc_flag(self):
        pytest.skip("Plan 03")

    async def test_filters_by_hospital_flag(self):
        pytest.skip("Plan 03")

    async def test_filters_by_region(self):
        pytest.skip("Plan 03")


class TestFetchErWaitTimes:
    async def test_returns_116_rows(self):
        pytest.skip("Plan 03")

    async def test_optional_q_filter(self):
        pytest.skip("Plan 03")


class TestFetchPopulationByMunicipality:
    async def test_parses_mamh_csv(self):
        pytest.skip("Plan 03")

    async def test_region_filter(self):
        pytest.skip("Plan 03")


# ---------------------------------------------------------------------------
# Transport / MTQ — Plan 03
# ---------------------------------------------------------------------------


class TestFetchRoadConditions:
    async def test_parses_conditions_csv(self):
        pytest.skip("Plan 03")

    async def test_optional_route_filter(self):
        pytest.skip("Plan 03")


class TestFetchRoadWorks:
    async def test_parses_mtq_wfs_csv(self):
        pytest.skip("Plan 03")

    async def test_optional_route_filter(self):
        pytest.skip("Plan 03")


class TestFetchRoadEvents:
    async def test_parses_evenements_csv(self):
        pytest.skip("Plan 03")


class TestFetchBridgeStructures:
    async def test_returns_bridge_rows(self):
        pytest.skip("Plan 03")

    async def test_requires_at_least_one_filter(self):
        pytest.skip("Plan 03")

    async def test_route_filter(self):
        pytest.skip("Plan 03")

    async def test_municipality_filter(self):
        pytest.skip("Plan 03")


# ---------------------------------------------------------------------------
# Environment / Energy — Plan 04
# ---------------------------------------------------------------------------


class TestFetchForestFiresHistory:
    async def test_returns_package_metadata_only(self):
        pytest.skip("Plan 04")


class TestFetchAirQualityStations:
    async def test_returns_station_list(self):
        pytest.skip("Plan 04")

    async def test_filters_active_stations(self):
        pytest.skip("Plan 04")


class TestFetchAirQualityIndex:
    async def test_calls_arcgis_rest(self):
        pytest.skip("Plan 04")

    async def test_returns_measurements(self):
        pytest.skip("Plan 04")


class TestFetchWaterQualityMonitoring:
    async def test_returns_package_metadata(self):
        pytest.skip("Plan 04")


class TestFetchElectricityData:
    async def test_parses_hydro_quebec_csv(self):
        pytest.skip("Plan 04")


class TestFetchProtectedAreas:
    async def test_returns_package_metadata(self):
        pytest.skip("Plan 04")
