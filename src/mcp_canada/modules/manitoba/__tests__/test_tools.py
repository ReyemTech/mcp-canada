"""Manitoba tools unit tests.

Wave 0 placeholder classes — Plans 02-06 fill test bodies.
TestManitobaEnvelopes and TestManitobaLangParam are parametrized by Plan 08.
"""

from __future__ import annotations


class TestManitobaSearchDatasets:
    """Tool unit tests for manitoba_search_datasets. Plan 02 fills."""

    pass


class TestManitobaGetDatasetDetails:
    """Tool unit tests for manitoba_get_dataset_details. Plan 02 fills."""

    pass


class TestManitobaQueryDataset:
    """Tool unit tests for manitoba_query_dataset. Plan 02 fills."""

    pass


class TestManitobaListOrgs:
    """Tool unit tests for manitoba_list_organizations. Plan 02 fills."""

    pass


class TestManitobaListCategories:
    """Tool unit tests for manitoba_list_categories. Plan 02 fills."""

    pass


class TestManitobaGetFloodAlerts:
    """Tool unit tests for manitoba_get_flood_alerts.

    Plan 03 fills — must include test_empty_flood_alerts_returns_success_not_error.
    """

    pass


class TestManitobaGetRiverStations:
    """Tool unit tests for manitoba_get_river_stations. Plan 03 fills."""

    pass


class TestManitobaGetProvincialWaterways:
    """Tool unit tests for manitoba_get_provincial_waterways. Plan 03 fills."""

    pass


class TestManitobaGetDroughtStatus:
    """Tool unit tests for manitoba_get_drought_status. Plan 04 fills."""

    pass


class TestManitobaGetAgWeatherStations:
    """Tool unit tests for manitoba_get_ag_weather_stations. Plan 04 fills."""

    pass


class TestManitobaGetLivestockPrices:
    """Tool unit tests for manitoba_get_livestock_prices. Plan 04 fills."""

    pass


class TestManitobaGetCropRegions:
    """Tool unit tests for manitoba_get_crop_regions. Plan 04 fills."""

    pass


class TestManitobaGetParks:
    """Tool unit tests for manitoba_get_provincial_parks. Plan 05 fills."""

    pass


class TestManitobaGetFisheriesData:
    """Tool unit tests for manitoba_get_fisheries_data. Plan 05 fills."""

    pass


class TestManitobaGetForests:
    """Tool unit tests for manitoba_get_provincial_forests. Plan 05 fills."""

    pass


class TestManitobaGetWaitTimes:
    """Tool unit tests for manitoba_get_surgical_wait_times. Plan 05 fills."""

    pass


class TestManitobaGetHealthFacilities:
    """Tool unit tests for manitoba_get_health_facilities. Plan 05 fills."""

    pass


class TestManitoba511RoadEvents:
    """Tool unit tests for manitoba_get_road_events.

    Plan 06 fills — must include test_returns_not_configured_without_key.
    """

    pass


class TestManitoba511WinterRoads:
    """Tool unit tests for manitoba_get_winter_road_conditions. Plan 06 fills."""

    pass


class TestManitoba511Cameras:
    """Tool unit tests for manitoba_get_traffic_cameras. Plan 06 fills."""

    pass


class TestManitobaEnvelopes:
    """Parametrized envelope tests for all Manitoba tools.

    Plan 08 fills — verifies _meta envelope structure across all ~15 tools.
    """

    pass


class TestManitobaLangParam:
    """Parametrized lang parameter tests for all Manitoba tools.

    Plan 08 fills — verifies lang='fr' passes through to envelope for all tools.
    """

    pass
