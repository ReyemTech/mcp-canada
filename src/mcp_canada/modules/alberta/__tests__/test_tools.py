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
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path returns {_meta, data} envelope with AER source identifier."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_well_licences_today,
        )

        fake_rows = [
            {"licence_number": "0467890", "operator": "TOURMALINE OIL CORP"},
        ]
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_well_licences_today",
            new=AsyncMock(return_value=(fake_rows, False)),
        ):
            out = await alberta_get_well_licences_today()
        assert "_meta" in out
        assert out["_meta"]["lang"] == "en"
        assert out["_meta"]["source"]["api"] == "alberta-aer-static"
        assert out["data"] == fake_rows

    @pytest.mark.asyncio
    async def test_french_lang_propagated(self):
        """lang='fr' surfaces in _meta envelope."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_well_licences_today,
        )

        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_well_licences_today",
            new=AsyncMock(return_value=([], False)),
        ):
            out = await alberta_get_well_licences_today(lang="fr")
        assert out["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_upstream_error_french_message(self):
        """httpx.HTTPStatusError → UPSTREAM_ERROR with French message."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_well_licences_today,
        )

        err = httpx.HTTPStatusError(
            "500",
            request=httpx.Request("GET", "https://static.aer.ca"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_well_licences_today",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_well_licences_today(lang="fr")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"
        msg = out["error"]["message"].lower()
        assert any(w in msg for w in ("échec", "erreur"))


class TestAlbertaWellLicencesArchiveTool:  # Plan 03
    @pytest.mark.asyncio
    async def test_returns_metadata_envelope(self):
        """Happy path returns {_meta, data} envelope with archive metadata."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_well_licences_archive,
        )

        fake_payload = {
            "url": "https://static.aer.ca/prd/data/well-lic/dwll2026-03.zip",
            "year": 2026,
            "month": 3,
            "note": "ZIP",
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_well_licences_archive",
            new=AsyncMock(return_value=(fake_payload, False)),
        ):
            out = await alberta_get_well_licences_archive(year=2026, month=3)
        assert "_meta" in out
        assert out["data"]["year"] == 2026
        assert out["data"]["month"] == 3
        assert out["data"]["url"].endswith("dwll2026-03.zip")


class TestAlbertaPipelineStatisticsTool:  # Plan 03
    @pytest.mark.asyncio
    async def test_returns_rows_envelope(self):
        """Happy path returns pipeline rows in data envelope."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_pipeline_statistics,
        )

        fake_rows = [
            {"substance": "Crude Oil", "length_km": 164_520, "year": 2024},
        ]
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_pipeline_statistics",
            new=AsyncMock(return_value=(fake_rows, False)),
        ):
            out = await alberta_get_pipeline_statistics(year=2024)
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-aer-static"
        assert out["data"] == fake_rows

    @pytest.mark.asyncio
    async def test_upstream_error_english_message(self):
        """httpx.HTTPStatusError → UPSTREAM_ERROR with English message by default."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_pipeline_statistics,
        )

        err = httpx.HTTPStatusError(
            "404",
            request=httpx.Request("GET", "https://static.aer.ca"),
            response=httpx.Response(404),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_pipeline_statistics",
            new=AsyncMock(side_effect=err),
        ):
            # Use a valid-range year so we exercise the UPSTREAM_ERROR branch,
            # not the INVALID_INPUT year validation.
            out = await alberta_get_pipeline_statistics(year=2009)
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "en"


class TestAlbertaProductionVolumesTool:  # Plan 03
    @pytest.mark.asyncio
    async def test_returns_rows_envelope(self):
        """Happy path with valid product returns data envelope."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_production_volumes,
        )

        fake_rows = [
            {"period": "2026-01", "product": "Gas", "volume_e3m3": 18523400},
        ]
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_production_volumes",
            new=AsyncMock(return_value=(fake_rows, False)),
        ):
            out = await alberta_get_production_volumes(product="Gas")
        assert "_meta" in out
        assert out["data"] == fake_rows

    @pytest.mark.asyncio
    async def test_invalid_product_english_error(self):
        """Invalid product 'Bitumen' → INVALID_INPUT with valid list (Pitfall 8)."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_production_volumes,
        )

        # Don't call client on invalid input
        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_production_volumes",
            new=mock_client,
        ):
            out = await alberta_get_production_volumes(product="Bitumen")
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["lang"] == "en"
        # valid= extras list should be present with all 7 products
        valid = out["error"].get("valid", [])
        assert set(valid) == {
            "Butane", "Ethane", "NGL", "Oil", "Gas", "Propane", "Sulphur",
        }
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_product_french_error(self):
        """Invalid product with lang='fr' → INVALID_INPUT French message + valid list."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_production_volumes,
        )

        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_production_volumes",
            new=mock_client,
        ):
            out = await alberta_get_production_volumes(
                product="Bitumen", lang="fr"
            )
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["lang"] == "fr"
        msg = out["error"]["message"].lower()
        assert "invalide" in msg or "valides" in msg
        valid = out["error"].get("valid", [])
        assert "Butane" in valid and "Sulphur" in valid
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_upstream_error_returns_error_envelope(self):
        """httpx.HTTPStatusError → UPSTREAM_ERROR."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_production_volumes,
        )

        err = httpx.HTTPStatusError(
            "500",
            request=httpx.Request("GET", "https://static.aer.ca"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_production_volumes",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_production_volumes(product="Gas")
        assert out["error"]["code"] == "UPSTREAM_ERROR"


# ---------------------------------------------------------------------------
# Wildfire tools — Plan 04
# ---------------------------------------------------------------------------


class TestAlbertaActiveFiresTool:  # Plan 04
    """@tool alberta_get_active_fires — envelope, lang, UPSTREAM_ERROR handling."""

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path: _meta.source.api == 'alberta-wmb-arcgis', data passes through."""
        from mcp_canada.modules.alberta.tools import alberta_get_active_fires

        payload = {"features": [{"FIRE_NUMBER": "X-1"}], "truncated": False, "count": 1}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_active_fires",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_active_fires()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-wmb-arcgis"
        assert out["_meta"]["lang"] == "en"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_french_lang_in_meta(self):
        """lang='fr' surfaces through to _meta.lang on success."""
        from mcp_canada.modules.alberta.tools import alberta_get_active_fires

        payload = {"features": [], "truncated": False, "count": 0}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_active_fires",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_active_fires(lang="fr")
        assert out["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_upstream_error_bilingual(self):
        """httpx.HTTPStatusError → UPSTREAM_ERROR with French message on lang='fr'."""
        from mcp_canada.modules.alberta.tools import alberta_get_active_fires

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_active_fires",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_active_fires(lang="fr")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"
        assert "échec" in out["error"]["message"].lower()


class TestAlbertaFirePerimetersTool:  # Plan 04
    """@tool alberta_get_fire_perimeters — status dispatch + invalid-input error."""

    @pytest.mark.asyncio
    async def test_active_status_passes_through(self):
        from mcp_canada.modules.alberta.tools import alberta_get_fire_perimeters

        payload = {"features": [{"FIRE_NUMBER": "P-1"}], "truncated": False, "count": 1}
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_fire_perimeters",
            new=mock_fetch,
        ):
            out = await alberta_get_fire_perimeters(status="active")
        assert "_meta" in out
        assert out["data"]["count"] == 1
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("status") == "active"

    @pytest.mark.asyncio
    async def test_invalid_status_returns_invalid_input(self):
        """status outside {active, extinguished} → INVALID_INPUT with valid list."""
        from mcp_canada.modules.alberta.tools import alberta_get_fire_perimeters

        # No patch required — the guard fires before the client call
        out = await alberta_get_fire_perimeters(status="bogus")  # type: ignore[arg-type]
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["valid"] == ["active", "extinguished"]

    @pytest.mark.asyncio
    async def test_invalid_status_bilingual(self):
        """INVALID_INPUT returns French message when lang='fr'."""
        from mcp_canada.modules.alberta.tools import alberta_get_fire_perimeters

        out = await alberta_get_fire_perimeters(status="bogus", lang="fr")  # type: ignore[arg-type]
        assert out["error"]["lang"] == "fr"
        # Accept either 'invalide' or 'entrée' in French error text
        msg = out["error"]["message"].lower()
        assert "invalide" in msg or "entrée" in msg


class TestAlbertaFireBansTool:  # Plan 04
    """@tool alberta_get_fire_bans — basic envelope + upstream error handling."""

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_get_fire_bans

        payload = {"features": [{"BAN_TYPE": "Fire Ban"}], "truncated": False, "count": 1}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_fire_bans",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_fire_bans()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-wmb-arcgis"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_upstream_error(self):
        from mcp_canada.modules.alberta.tools import alberta_get_fire_bans

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(503),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_fire_bans",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_fire_bans(lang="en")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "en"


class TestAlbertaFireControlOrdersTool:  # Plan 04
    """@tool alberta_get_fire_control_orders — category dispatch + INVALID_INPUT."""

    @pytest.mark.asyncio
    async def test_fire_control_default(self):
        from mcp_canada.modules.alberta.tools import alberta_get_fire_control_orders

        payload = {"features": [{"ORDER": "x"}], "truncated": False, "count": 1}
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_fire_control_orders",
            new=mock_fetch,
        ):
            out = await alberta_get_fire_control_orders()  # default 'fire_control'
        assert "_meta" in out
        assert out["data"]["count"] == 1
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("category") == "fire_control"

    @pytest.mark.asyncio
    async def test_ohv_restriction_dispatch(self):
        from mcp_canada.modules.alberta.tools import alberta_get_fire_control_orders

        payload = {"features": [], "truncated": False, "count": 0}
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_fire_control_orders",
            new=mock_fetch,
        ):
            await alberta_get_fire_control_orders(category="ohv_restriction")
        assert mock_fetch.call_args.kwargs["category"] == "ohv_restriction"

    @pytest.mark.asyncio
    async def test_invalid_category_returns_invalid_input(self):
        """category outside the 3 options → INVALID_INPUT with valid list."""
        from mcp_canada.modules.alberta.tools import alberta_get_fire_control_orders

        out = await alberta_get_fire_control_orders(category="bogus")  # type: ignore[arg-type]
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["valid"] == [
            "fire_control",
            "ohv_restriction",
            "forest_area",
        ]


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
