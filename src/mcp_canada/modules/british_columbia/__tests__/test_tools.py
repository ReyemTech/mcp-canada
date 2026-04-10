"""Wave 0 test class scaffolds for british_columbia tools.

Plans 02 (5 discovery tools) and 03 (15 curated WFS tools) fill in implementations.
Each class has one xfail placeholder so pytest --collect-only counts all 20 tool classes.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Plan 02 — 5 CKAN Discovery Tools
# ---------------------------------------------------------------------------


class TestBcSearchDatasets:
    """Tests for bc_search_datasets (CKAN package_search tool). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetDatasetDetails:
    """Tests for bc_get_dataset_details (CKAN package_show + queryable_via_wfs). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcQueryFeatures:
    """Tests for bc_query_features (routes to WFS or file parser based on queryable_via_wfs). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcListOrganizations:
    """Tests for bc_list_organizations (CKAN organization_list tool). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcListCategories:
    """Tests for bc_list_categories (CKAN tag_list tool). Plan 02 implements."""

    @pytest.mark.xfail(reason="Plan 02 will implement", strict=False)
    def test_placeholder(self):
        assert False


# ---------------------------------------------------------------------------
# Plan 03 — 15 Curated WFS Tools
# ---------------------------------------------------------------------------


class TestBcGetActiveFires:
    """Tests for bc_get_active_fires (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetFirePerimeters:
    """Tests for bc_get_fire_perimeters (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetForestTenure:
    """Tests for bc_get_forest_tenure (WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetCutBlocks:
    """Tests for bc_get_cut_blocks (WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetProtectedAreas:
    """Tests for bc_get_protected_areas (WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetWaterWells:
    """Tests for bc_get_water_wells (WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW). Plan 03 implements.

    IMPORTANT: Must include test_requires_at_least_one_filter — water wells has ~130K records
    (RESEARCH Pitfall 5). Tool must require at least one filter (city, aquifer_id, well_class)
    to prevent runaway WFS fetches.
    """

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False

    @pytest.mark.xfail(reason="Plan 03 will implement — 130K-record guard", strict=False)
    def test_requires_at_least_one_filter(self):
        """bc_get_water_wells must return INVALID_INPUT when no filter provided (130K-record guard)."""
        assert False


class TestBcGetWildfireWeatherStations:
    """Tests for bc_get_wildfire_weather_stations (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetLocalParks:
    """Tests for bc_get_local_parks (WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetMiningTenure:
    """Tests for bc_get_mining_tenure (WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetFishHabitat:
    """Tests for bc_get_fish_habitat (WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetEmergencyRooms:
    """Tests for bc_get_emergency_rooms (WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetWalkInClinics:
    """Tests for bc_get_walk_in_clinics (WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetHighwayProfiles:
    """Tests for bc_get_highway_profiles (WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetRoadStructures:
    """Tests for bc_get_road_structures (WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcGetClimateStations:
    """Tests for bc_get_climate_stations (WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP — climate alias). Plan 03 implements."""

    @pytest.mark.xfail(reason="Plan 03 will implement", strict=False)
    def test_placeholder(self):
        assert False
