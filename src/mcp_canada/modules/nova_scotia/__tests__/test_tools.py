"""Unit tests for Nova Scotia module tools.py.

Plans 02-05 fill the per-tool test class bodies.
Plan 07 fills TestNsEnvelopes and TestNsLangParam with parametrized tests
covering all tools for envelope structure and bilingual lang= passthrough.
"""

from __future__ import annotations


class TestNsSearchDatasetsTools:
    """ns_search_datasets tool tests. Plan 02 fills."""

    pass


class TestNsGetDatasetDetailsTool:
    """ns_get_dataset_details tool tests. Plan 02 fills."""

    pass


class TestNsQueryDatasetTool:
    """ns_query_dataset tool tests. Plan 02 fills."""

    pass


class TestNsListOrganizationsTool:
    """ns_list_organizations tool tests. Plan 02 fills."""

    pass


class TestNsListCategoriesTool:
    """ns_list_categories tool tests. Plan 02 fills."""

    pass


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
