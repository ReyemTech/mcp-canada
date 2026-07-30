"""Unit tests for new_brunswick/tools.py.

TRACER SUBSET (Task 1) — TestNbGetCrownLandTools only. Task 4 adds placeholder
classes for the remaining 21 tools plus TestNbEnvelopes / TestNbLangParam.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest

from mcp_canada.modules.new_brunswick.constants import CROWN_LAND_SERVICE, MAX_RECORDS
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
