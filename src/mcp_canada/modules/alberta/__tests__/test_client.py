"""alberta module client tests. Bodies added by Plans 02-07.

Class stubs exist so pytest collection succeeds from Wave 0. Downstream plans
add test methods to the matching class.
"""

from __future__ import annotations

import pytest  # noqa: F401 — used by Plans 02-07


class TestSharedApiGetContract:
    """Post-15-05 contract regression guard.

    Plan 02 fills three tests:
      - test_ckan_api_get_returns_parsed_dict
      - test_ckan_success_false_raises
      - test_ckan_success_true_returns_result

    Patches `mcp_canada.shared.http.api_get` at the shared layer (NOT the
    module-local import) so the real contract is exercised — preventing the
    mock-masks-real-contract bug from Phase 15-05.
    """

    pass


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


class TestAlbertaSearchDatasets:  # Plan 02
    pass


class TestAlbertaGetDatasetDetails:  # Plan 02
    pass


class TestAlbertaQueryDataset:  # Plan 02
    pass


class TestAlbertaListOrganizations:  # Plan 02
    pass


class TestAlbertaListCategories:  # Plan 02
    pass


# ---------------------------------------------------------------------------
# AER tools — Plan 03
# ---------------------------------------------------------------------------


class TestAlbertaWellLicencesToday:  # Plan 03
    pass


class TestAlbertaWellLicencesArchive:  # Plan 03
    pass


class TestAlbertaPipelineStatistics:  # Plan 03
    pass


class TestAlbertaProductionVolumes:  # Plan 03
    pass


# ---------------------------------------------------------------------------
# Wildfire tools — Plan 04
# ---------------------------------------------------------------------------


class TestAlbertaActiveFires:  # Plan 04
    pass


class TestAlbertaFirePerimeters:  # Plan 04
    pass


class TestAlbertaFireBans:  # Plan 04
    pass


class TestAlbertaFireControlOrders:  # Plan 04
    pass


# ---------------------------------------------------------------------------
# Health tools — Plan 05
# ---------------------------------------------------------------------------


class TestAlbertaHospitals:  # Plan 05
    pass


class TestAlbertaAhsZones:  # Plan 05
    pass


class TestAlbertaHealthFacilities:  # Plan 05
    pass


# ---------------------------------------------------------------------------
# Transport / 511 tools — Plan 06
# ---------------------------------------------------------------------------


class TestAlbertaRoadEvents:  # Plan 06
    pass


class TestAlbertaWinterRoadConditions:  # Plan 06
    pass


class TestAlbertaTrafficCameras:  # Plan 06
    pass


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks tools — Plan 07
# ---------------------------------------------------------------------------


class TestAlbertaAirQuality:  # Plan 07
    pass


class TestAlbertaWaterAdvisories:  # Plan 07
    pass


class TestAlbertaCropProduction:  # Plan 07
    pass


class TestAlbertaPopulationEstimates:  # Plan 07
    pass


class TestAlbertaProvincialParks:  # Plan 07
    pass
