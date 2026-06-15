"""Unit tests for Nova Scotia module client.py.

TestSharedApiGetContract: Module-local Socrata contract test — patches
mcp_canada.modules.nova_scotia.client.socrata and asserts outgoing SoQL/catalog params.
(The Manitoba/Saskatchewan lesson at the module layer: mock at the module-local import,
not at the shared library layer, so from-import semantics don't break the patch.)

Plans 02-05 fill the test class bodies with actual test methods.
"""

from __future__ import annotations


class TestSharedApiGetContract:
    """Module-local socrata contract — patches client.socrata and asserts outgoing params.

    Plan 02 fills this class with:
    - test_search_catalog_params: asserts domains/q/limit/only sent to socrata.search_catalog
    - test_query_dataset_params: asserts $where/$select/$limit sent to socrata.query_dataset
    - test_offset_omitted_at_zero: asserts offset=0 omitted from both catalog + resource calls
    """

    pass  # Plan 02 fills


class TestNsSearchDatasets:
    """fetch_search_datasets returns shaped results with count. Plan 02 fills."""

    pass


class TestNsGetDatasetDetails:
    """fetch_dataset_details returns metadata dict. Plan 02 fills."""

    pass


class TestNsQueryDataset:
    """fetch_query_dataset passes SoQL params; strips geometry when include_geometry=False. Plan 02 fills."""

    pass


class TestNsListOrganizations:
    """fetch_organizations derives unique attributions from catalog results. Plan 02 fills."""

    pass


class TestNsListCategories:
    """fetch_categories derives unique domain_category values. Plan 02 fills."""

    pass


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
