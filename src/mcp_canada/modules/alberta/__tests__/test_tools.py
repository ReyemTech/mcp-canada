"""alberta module tool tests. Bodies added by Plans 02-07.

Plan 09 adds parametrized envelope/lang test classes (TestAlbertaEnvelopes,
TestAlbertaLangParam) that run across all 24 tools via pytest.mark.parametrize.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_canada.modules.alberta.schemas import (
    AlbertaCategory,
    AlbertaDatasetDetails,
    AlbertaOrganization,
    AlbertaResource,
)


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


class TestAlbertaSearchDatasetsTool:  # Plan 02
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path returns {_meta, data} envelope with lang='en'."""
        from mcp_canada.modules.alberta.tools import alberta_search_datasets

        fake_payload = {"count": 2, "results": []}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_search_datasets",
            new=AsyncMock(return_value=(fake_payload, False)),
        ):
            out = await alberta_search_datasets(q="wildfire")
        assert "_meta" in out
        assert out["_meta"]["lang"] == "en"
        assert out["_meta"]["source"]["api"] == "alberta-open-data"
        assert out["data"]["count"] == 2

    @pytest.mark.asyncio
    async def test_forwards_format_kwarg(self):
        """format= kwarg flows through to the client call unchanged."""
        from mcp_canada.modules.alberta.tools import alberta_search_datasets

        mock_fetch = AsyncMock(return_value=({"count": 0, "results": []}, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_search_datasets",
            new=mock_fetch,
        ):
            await alberta_search_datasets(q="fire", format="CSV")
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("format") == "CSV"

    @pytest.mark.asyncio
    async def test_french_error_on_upstream(self):
        """lang='fr' returns French error message on httpx.HTTPStatusError."""
        from mcp_canada.modules.alberta.tools import alberta_search_datasets

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_search_datasets",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_search_datasets(q="fire", lang="fr")
        assert "error" in out
        assert out["error"]["lang"] == "fr"
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        # French keyword in message
        msg = out["error"]["message"].lower()
        assert any(w in msg for w in ("échec", "erreur"))


class TestAlbertaGetDatasetDetailsTool:  # Plan 02
    @pytest.mark.asyncio
    async def test_returns_details_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_get_dataset_details

        fake = AlbertaDatasetDetails(
            id="x",
            name="x",
            title="X",
            resources=[AlbertaResource(id="r1", url="u", format="CSV")],
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_dataset_details",
            new=AsyncMock(return_value=(fake, False)),
        ):
            out = await alberta_get_dataset_details(package_id="x")
        assert "_meta" in out
        assert out["data"]["id"] == "x"

    @pytest.mark.asyncio
    async def test_not_found_error(self):
        from mcp_canada.modules.alberta.tools import alberta_get_dataset_details

        err = httpx.HTTPStatusError(
            "404",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(404),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_dataset_details",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_dataset_details(package_id="nope")
        assert "error" in out
        assert out["error"]["code"] == "NOT_FOUND"


class TestAlbertaQueryDatasetTool:  # Plan 02
    @pytest.mark.asyncio
    async def test_returns_payload_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_query_dataset

        payload = {"data": [{"a": 1}], "format": "CSV", "url": "u"}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_query_dataset",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_query_dataset(package_id="x")
        assert "_meta" in out
        assert out["data"]["format"] == "CSV"

    @pytest.mark.asyncio
    async def test_invalid_resource_index_returns_error(self):
        """Negative resource_index → INVALID_INPUT (no client call)."""
        from mcp_canada.modules.alberta.tools import alberta_query_dataset

        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_query_dataset",
            new=mock_client,
        ):
            out = await alberta_query_dataset(
                package_id="x", resource_index=-1
            )
        assert out.get("error", {}).get("code") == "INVALID_INPUT"
        mock_client.assert_not_called()


class TestAlbertaListOrganizationsTool:  # Plan 02
    @pytest.mark.asyncio
    async def test_returns_org_list(self):
        from mcp_canada.modules.alberta.tools import alberta_list_organizations

        orgs = [
            AlbertaOrganization(
                id="1",
                name="forestry-and-parks",
                title="Forestry and Parks",
                package_count=240,
            )
        ]
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_organizations",
            new=AsyncMock(return_value=(orgs, False)),
        ):
            out = await alberta_list_organizations()
        assert "_meta" in out
        assert isinstance(out["data"], list)
        assert out["data"][0]["name"] == "forestry-and-parks"


class TestAlbertaListCategoriesTool:  # Plan 02
    @pytest.mark.asyncio
    async def test_returns_format_categories(self):
        from mcp_canada.modules.alberta.tools import alberta_list_categories

        cats = [
            AlbertaCategory(format="PDF", count=28763),
            AlbertaCategory(format="CSV", count=224),
        ]
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_format_categories",
            new=AsyncMock(return_value=(cats, False)),
        ):
            out = await alberta_list_categories()
        assert "_meta" in out
        assert out["data"][0]["format"] == "PDF"

    def test_docstring_mentions_res_format_pitfall(self):
        """Pitfall 1 must be documented so agents understand why this isn't group_list."""
        from mcp_canada.modules.alberta import tools

        doc = tools.alberta_list_categories.__doc__ or ""
        assert "res_format" in doc
        # And document that group_list returns empty
        assert "group_list" in doc


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
