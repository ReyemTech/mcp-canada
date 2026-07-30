"""Unit tests for new_brunswick/tools.py.

TestNbGetCrownLandTools is the Task 1 tracer, fully tested. Every remaining
tool in constants.ALL_NB_TOOL_NAMES gets a placeholder class asserting
membership in the locked manifest, until its owning plan implements the tool
itself (at which point the placeholder is replaced with real behavior tests).
TestNbEnvelopes / TestNbLangParam are parametrized by Plan 07 once every tool
exists.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest

from mcp_canada.modules.new_brunswick.constants import ALL_NB_TOOL_NAMES, CROWN_LAND_SERVICE, MAX_RECORDS
from mcp_canada.modules.new_brunswick.tools import nb_get_crown_land


class TestNbGetCrownLandTools:
    """nb_get_crown_land — the Task 1 tracer tool."""

    @pytest.mark.asyncio
    async def test_no_filter_returns_envelope_with_features(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        payload = {"features": features, "count": len(features), "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_crown_land", mock_fetch
        )

        result = await nb_get_crown_land(lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"
        assert len(result["data"]["features"]) > 0
        assert "count" in result["data"]
        assert "truncated" in result["data"]

    @pytest.mark.asyncio
    async def test_features_carry_objectid_and_holder(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        payload = {"features": features, "count": len(features), "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_crown_land", mock_fetch
        )

        result = await nb_get_crown_land(lang="en")

        for feature in result["data"]["features"]:
            assert "OBJECTID" in feature
            assert "HOLDER" in feature

    @pytest.mark.asyncio
    async def test_holder_filter_returns_only_matching_rows(self, monkeypatch, crown_land_geojson):
        matching = [crown_land_geojson["features"][0]["properties"]]  # HOLDER == 2
        payload = {"features": matching, "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_crown_land", mock_fetch
        )

        result = await nb_get_crown_land(holder=2, lang="en")

        mock_fetch.assert_awaited_once_with(holder=2, limit=MAX_RECORDS)
        assert all(f["HOLDER"] == 2 for f in result["data"]["features"])

    @pytest.mark.asyncio
    async def test_lang_fr_sets_meta_lang(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        payload = {"features": features, "count": len(features), "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_crown_land", mock_fetch
        )

        result = await nb_get_crown_land(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_http_status_error_returns_upstream_error_envelope(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", CROWN_LAND_SERVICE),
            response=httpx.Response(500),
        )
        mock_fetch = AsyncMock(side_effect=error)
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_crown_land", mock_fetch
        )

        result = await nb_get_crown_land(lang="en")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_layer_id_passed_to_query_feature_service_is_three(
        self, monkeypatch, crown_land_geojson
    ):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_crown_land(lang="en")

        assert "error" not in result
        assert mock_query.call_args.kwargs["layer_id"] == 3


# ---------------------------------------------------------------------------
# Locked manifest — every tool name in ALL_NB_TOOL_NAMES is accounted for
# ---------------------------------------------------------------------------


class TestAllNbToolNamesManifest:
    def test_manifest_has_22_entries(self):
        assert len(ALL_NB_TOOL_NAMES) == 22

    def test_crown_land_tracer_tool_is_in_manifest(self):
        assert "nb_get_crown_land" in ALL_NB_TOOL_NAMES

    def test_checkpoint_option_a_socrata_tools_are_in_manifest(self):
        assert "nb_search_gnb_socrata_datasets" in ALL_NB_TOOL_NAMES
        assert "nb_query_gnb_socrata_dataset" in ALL_NB_TOOL_NAMES

    def test_checkpoint_option_a_dropped_tools_are_not_in_manifest(self):
        assert "nb_get_provincial_parks" not in ALL_NB_TOOL_NAMES
        assert "nb_get_mineral_occurrences" not in ALL_NB_TOOL_NAMES

    def test_every_tool_name_uses_nb_prefix(self):
        for name in ALL_NB_TOOL_NAMES:
            assert name.startswith("nb_"), name


# ---------------------------------------------------------------------------
# Placeholder classes — one per remaining tool (owning plan implements + tests)
# ---------------------------------------------------------------------------


class TestNbSearchDatasets:
    """Plan 02 implements + tests."""


class TestNbGetDatasetDetails:
    """Plan 02 implements + tests."""


class TestNbQueryDataset:
    """Plan 02 implements + tests."""


class TestNbListOrganizations:
    """Plan 02 implements + tests."""


class TestNbListCategories:
    """Plan 02 implements + tests."""


class TestNbSearchGnbSocrataDatasets:
    """Plan 02 implements + tests (checkpoint option-a)."""


class TestNbQueryGnbSocrataDataset:
    """Plan 02 implements + tests (checkpoint option-a)."""


class TestNbListGeonbServices:
    """Plan 04 implements + tests."""


class TestNbGetGeonbServiceLayers:
    """Plan 04 implements + tests."""


class TestNbQueryGeonbLayer:
    """Plan 04 implements + tests."""


class TestNbGetFloodHazardAreas:
    """Plan 04 implements + tests."""


class TestNbGetHistoricalFloods:
    """Plan 04 implements + tests."""


class TestNbGetWetlands:
    """Plan 04 implements + tests. FILTER_REQUIRED — rejects unfiltered calls."""


class TestNbGetContaminatedSites:
    """Plan 04 implements + tests."""


class TestNbGetParcels:
    """Plan 05 implements + tests. FILTER_REQUIRED — rejects unfiltered calls."""


class TestNbGetCivicAddresses:
    """Plan 05 implements + tests. FILTER_REQUIRED — rejects unfiltered calls."""


class TestNbGetHealthFacilities:
    """Plan 06 implements + tests."""


class TestNbGetPublicSchools:
    """Plan 06 implements + tests."""


class TestNbGetRoadEvents:
    """Plan 06 implements + tests. NOT_CONFIGURED when 511 key absent."""


class TestNbGetWinterRoadConditions:
    """Plan 06 implements + tests. NOT_CONFIGURED when 511 key absent."""


class TestNbGetTrafficCameras:
    """Plan 06 implements + tests. NOT_CONFIGURED when 511 key absent."""


# ---------------------------------------------------------------------------
# Cross-tool envelope / lang contract — Plan 07 parametrizes across every tool
# ---------------------------------------------------------------------------


class TestNbEnvelopes:
    """Plan 07 parametrizes: every tool returns make_response/make_error shape."""


class TestNbLangParam:
    """Plan 07 parametrizes: every tool accepts lang='en'/'fr' and sets _meta.lang."""
