"""Unit tests for new_brunswick/client.py.

Task 1 tracer (fetch_crown_land) is fully tested here plus the fully-
implemented Wave 0 private helpers (_build_fq, _geonb_query, _511_get,
Five11NotConfigured). TestSharedApiGetContract and TestShapeDatasetBilingual
are placeholders — Plan 02 fills them once fetch_search_datasets exists to
drive `_api_get`/`_shape_dataset` through a real call path. Every remaining
`fetch_*` stub gets a placeholder class asserting it raises NotImplementedError
until its owning plan fills the body.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from mcp_canada.modules.new_brunswick import client as nb_client
from mcp_canada.modules.new_brunswick.constants import CROWN_LAND_LAYER, FIVE11_KEY_ENV, NB_ORG_FQ


# ---------------------------------------------------------------------------
# Fully-implemented Wave 0 private helpers
# ---------------------------------------------------------------------------


class TestBuildFq:
    def test_no_extra_fq_returns_nb_org_clause_alone(self):
        assert nb_client._build_fq(None) == NB_ORG_FQ

    def test_extra_fq_is_and_ed_after_nb_org_clause(self):
        result = nb_client._build_fq("res_format:CSV")
        assert result == f"{NB_ORG_FQ} AND res_format:CSV"
        assert result.startswith(NB_ORG_FQ)  # NB clause always first (T-21-04)


class TestShapeDatasetBilingual:
    """Plan 02 fills this once fetch_search_datasets drives _shape_dataset via
    a real federal CKAN call path."""


class TestSharedApiGetContract:
    """Plan 02 fills this — patches the module-local api_get and asserts the
    outgoing params dict including the non-overridable NB organization clause."""


class TestGeonbQueryHelper:
    @pytest.mark.asyncio
    async def test_returns_features_count_truncated_shape(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client._geonb_query(
            "https://geonb.snb.ca/arcgis/rest/services/GeoNB_DNR_Crown_Land/MapServer",
            layer_id=CROWN_LAND_LAYER,
        )

        assert payload["count"] == len(features)
        assert payload["truncated"] is False
        assert cached is False
        assert mock_query.call_args.kwargs["layer_id"] == CROWN_LAND_LAYER


class TestFive11Get:
    @pytest.mark.asyncio
    async def test_raises_five11_not_configured_when_key_absent(self, monkeypatch):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)

        with pytest.raises(nb_client.Five11NotConfigured):
            await nb_client._511_get("event")

    @pytest.mark.asyncio
    async def test_not_configured_message_never_leaks_key_value(self, monkeypatch):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)

        with pytest.raises(nb_client.Five11NotConfigured) as exc_info:
            await nb_client._511_get("event")

        assert "SENTINEL" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_returns_list_when_key_set(self, monkeypatch, five11_event_sample):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        mock_api_get = AsyncMock(return_value=five11_event_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        rows = await nb_client._511_get("event")

        assert rows == five11_event_sample

    @pytest.mark.asyncio
    async def test_non_list_response_coerced_to_empty_list(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        mock_api_get = AsyncMock(return_value={"Error": {"Message": "Invalid Key"}})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        rows = await nb_client._511_get("event")

        assert rows == []


# ---------------------------------------------------------------------------
# Task 1 tracer — fetch_crown_land, exercised directly at the client layer
# ---------------------------------------------------------------------------


class TestFetchCrownLand:
    @pytest.mark.asyncio
    async def test_no_holder_sends_match_all_where(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_crown_land()

        assert mock_query.call_args.kwargs["where"] == "1=1"
        assert payload["count"] == len(features)

    @pytest.mark.asyncio
    async def test_holder_builds_equality_where(self, monkeypatch, crown_land_geojson):
        matching = [crown_land_geojson["features"][0]["properties"]]
        mock_query = AsyncMock(return_value=(matching, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_crown_land(holder=2)

        assert mock_query.call_args.kwargs["where"] == "HOLDER=2"


# ---------------------------------------------------------------------------
# Placeholder classes — one per locked-signature client stub (owning plan fills)
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    """Plan 02 fills this."""


class TestFetchDatasetDetails:
    """Plan 02 fills this."""


class TestFetchQueryDataset:
    """Plan 02 fills this."""


class TestFetchOrganizations:
    """Plan 02 fills this."""


class TestFetchCategories:
    """Plan 02 fills this."""


class TestFetchGnbSocrataSearch:
    """Plan 02 fills this (checkpoint option-a)."""


class TestFetchGnbSocrataQuery:
    """Plan 02 fills this (checkpoint option-a)."""


class TestFetchGeonbServices:
    """Plan 04 fills this."""


class TestFetchGeonbServiceLayers:
    """Plan 04 fills this."""


class TestFetchGeonbLayerFeatures:
    """Plan 04 fills this."""


class TestFetchFloodHazardAreas:
    """Plan 04 fills this."""


class TestFetchHistoricalFloods:
    """Plan 04 fills this."""


class TestFetchWetlands:
    """Plan 04 fills this."""


class TestFetchContaminatedSites:
    """Plan 04 fills this."""


class TestFetchParcels:
    """Plan 05 fills this."""


class TestFetchCivicAddresses:
    """Plan 05 fills this."""


class TestFetchHealthFacilities:
    """Plan 06 fills this."""


class TestFetchPublicSchools:
    """Plan 06 fills this."""


class TestFetchRoadEvents:
    """Plan 06 fills this."""


class TestFetchWinterRoadConditions:
    """Plan 06 fills this."""


class TestFetchTrafficCameras:
    """Plan 06 fills this."""


# ---------------------------------------------------------------------------
# Locked-signature stub contract — every stub raises NotImplementedError today
# ---------------------------------------------------------------------------


class TestStubsRaiseNotImplementedError:
    """Every locked-signature stub raises NotImplementedError until its owning
    plan fills the body — pins the signature so Plans 02-06 never collide."""

    @pytest.mark.asyncio
    async def test_fetch_search_datasets(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_search_datasets()

    @pytest.mark.asyncio
    async def test_fetch_dataset_details(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_dataset_details("some-id")

    @pytest.mark.asyncio
    async def test_fetch_query_dataset(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_query_dataset("some-id")

    @pytest.mark.asyncio
    async def test_fetch_organizations(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_organizations()

    @pytest.mark.asyncio
    async def test_fetch_categories(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_categories()

    @pytest.mark.asyncio
    async def test_fetch_gnb_socrata_search(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_gnb_socrata_search()

    @pytest.mark.asyncio
    async def test_fetch_gnb_socrata_query(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_gnb_socrata_query("4zbh-z2ij")

    @pytest.mark.asyncio
    async def test_fetch_geonb_services(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_geonb_services()

    @pytest.mark.asyncio
    async def test_fetch_geonb_service_layers(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_geonb_service_layers("GeoNB_DNR_Crown_Land")

    @pytest.mark.asyncio
    async def test_fetch_geonb_layer_features(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_geonb_layer_features("GeoNB_DNR_ProvincialParks", 0)

    @pytest.mark.asyncio
    async def test_fetch_flood_hazard_areas(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_flood_hazard_areas()

    @pytest.mark.asyncio
    async def test_fetch_historical_floods(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_historical_floods()

    @pytest.mark.asyncio
    async def test_fetch_wetlands(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_wetlands()

    @pytest.mark.asyncio
    async def test_fetch_contaminated_sites(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_contaminated_sites()

    @pytest.mark.asyncio
    async def test_fetch_parcels(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_parcels()

    @pytest.mark.asyncio
    async def test_fetch_civic_addresses(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_civic_addresses()

    @pytest.mark.asyncio
    async def test_fetch_health_facilities(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_health_facilities("hospital_horizon")

    @pytest.mark.asyncio
    async def test_fetch_public_schools(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_public_schools()

    @pytest.mark.asyncio
    async def test_fetch_road_events(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_road_events()

    @pytest.mark.asyncio
    async def test_fetch_winter_road_conditions(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_winter_road_conditions()

    @pytest.mark.asyncio
    async def test_fetch_traffic_cameras(self):
        with pytest.raises(NotImplementedError):
            await nb_client.fetch_traffic_cameras()
