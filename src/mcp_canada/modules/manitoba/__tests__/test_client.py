"""Manitoba client unit tests.

Wave 0 placeholder classes — Plans 02-06 fill test bodies.
TestSharedApiGetContract patches mcp_canada.modules.manitoba.client.api_get
(module-local pattern from Phase 17 — achieves same regression guard as
shared-layer patch, works with Python from-import semantics).
"""

from __future__ import annotations


class TestSharedApiGetContract:
    """Ensure mcp_canada.shared.http.api_get is patched at the right layer.

    Plan 02 fills — patches mcp_canada.modules.manitoba.client.api_get.
    Verifies _hub_get calls api_get once with Hub Search URL.
    """

    pass


class TestManitobaSearchDatasets:
    """Unit tests for fetch_search_datasets. Plan 02 fills."""

    pass


class TestManitobaGetDatasetDetails:
    """Unit tests for fetch_dataset_details. Plan 02 fills."""

    pass


class TestManitobaQueryDataset:
    """Unit tests for fetch_query_dataset (hybrid auto-router). Plan 02 fills."""

    pass


class TestManitobaListOrgs:
    """Unit tests for fetch_organizations. Plan 02 fills."""

    pass


class TestManitobaListCategories:
    """Unit tests for fetch_categories. Plan 02 fills."""

    pass


class TestManitobaGetFloodAlerts:
    """Unit tests for fetch_flood_alerts.

    Plan 03 fills — must include test_flood_alerts_empty_when_no_active_alerts
    verifying that empty features list is correct (not an error).
    """

    pass


class TestManitobaGetRiverStations:
    """Unit tests for fetch_river_stations (CSV source). Plan 03 fills."""

    pass


class TestManitobaGetWaterways:
    """Unit tests for fetch_provincial_waterways. Plan 03 fills."""

    pass


class TestManitobaGetDroughtStatus:
    """Unit tests for fetch_drought_status. Plan 04 fills."""

    pass


class TestManitobaGetAgWeatherStations:
    """Unit tests for fetch_ag_weather_stations. Plan 04 fills."""

    pass


class TestManitobaGetLivestockPrices:
    """Unit tests for fetch_livestock_prices. Plan 04 fills."""

    pass


class TestManitobaGetCropRegions:
    """Unit tests for fetch_crop_regions. Plan 04 fills."""

    pass


class TestManitobaGetParks:
    """Unit tests for fetch_provincial_parks. Plan 05 fills."""

    pass


class TestManitobaGetFisheriesData:
    """Unit tests for fetch_fisheries_data. Plan 05 fills."""

    pass


class TestManitobaGetForests:
    """Unit tests for fetch_provincial_forests. Plan 05 fills."""

    pass


class TestManitobaGetWaitTimes:
    """Unit tests for fetch_surgical_wait_times. Plan 05 fills."""

    pass


class TestManitobaGetHealthFacilities:
    """Unit tests for fetch_health_facilities. Plan 05 fills."""

    pass


class TestManitoba511:
    """Unit tests for 511 client functions (fetch_road_events, etc.). Plan 06 fills.

    Must include:
    - test_raises_five11_not_configured_when_no_key
    - test_road_events_with_mocked_key
    - test_winter_roads_with_mocked_key
    - test_cameras_with_mocked_key
    """

    pass
