"""alberta module tool tests. Bodies added by Plans 02-07.

Plan 09 adds parametrized envelope/lang test classes (TestAlbertaEnvelopes,
TestAlbertaLangParam) that run across all 24 tools via pytest.mark.parametrize.
"""

from __future__ import annotations

import pytest  # noqa: F401 — used by Plans 02-09


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


class TestAlbertaSearchDatasetsTool:  # Plan 02
    pass


class TestAlbertaGetDatasetDetailsTool:  # Plan 02
    pass


class TestAlbertaQueryDatasetTool:  # Plan 02
    pass


class TestAlbertaListOrganizationsTool:  # Plan 02
    pass


class TestAlbertaListCategoriesTool:  # Plan 02
    pass


# ---------------------------------------------------------------------------
# AER tools — Plan 03
# ---------------------------------------------------------------------------


class TestAlbertaWellLicencesTodayTool:  # Plan 03
    pass


class TestAlbertaWellLicencesArchiveTool:  # Plan 03
    pass


class TestAlbertaPipelineStatisticsTool:  # Plan 03
    pass


class TestAlbertaProductionVolumesTool:  # Plan 03
    pass


# ---------------------------------------------------------------------------
# Wildfire tools — Plan 04
# ---------------------------------------------------------------------------


class TestAlbertaActiveFiresTool:  # Plan 04
    pass


class TestAlbertaFirePerimetersTool:  # Plan 04
    pass


class TestAlbertaFireBansTool:  # Plan 04
    pass


class TestAlbertaFireControlOrdersTool:  # Plan 04
    pass


# ---------------------------------------------------------------------------
# Health tools — Plan 05
# ---------------------------------------------------------------------------


class TestAlbertaHospitalsTool:  # Plan 05
    pass


class TestAlbertaAhsZonesTool:  # Plan 05
    pass


class TestAlbertaHealthFacilitiesTool:  # Plan 05
    pass


# ---------------------------------------------------------------------------
# Transport / 511 tools — Plan 06
# ---------------------------------------------------------------------------


class TestAlbertaRoadEventsTool:  # Plan 06
    pass


class TestAlbertaWinterRoadConditionsTool:  # Plan 06
    pass


class TestAlbertaTrafficCamerasTool:  # Plan 06
    pass


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks — Plan 07
# ---------------------------------------------------------------------------


class TestAlbertaAirQualityTool:  # Plan 07
    pass


class TestAlbertaWaterAdvisoriesTool:  # Plan 07
    pass


class TestAlbertaCropProductionTool:  # Plan 07
    pass


class TestAlbertaPopulationEstimatesTool:  # Plan 07
    pass


class TestAlbertaProvincialParksTool:  # Plan 07
    pass


# ---------------------------------------------------------------------------
# Parametrized phase-wide tests — Plan 09
# ---------------------------------------------------------------------------


class TestAlbertaEnvelopes:  # Plan 09 — parametrized over all 24 tools
    pass


class TestAlbertaLangParam:  # Plan 09 — parametrized over all 24 tools
    pass
