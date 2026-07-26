# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false
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
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path — returns `_meta` envelope with alberta-ahs-arcgis api and hospital payload."""
        from mcp_canada.modules.alberta.tools import alberta_get_hospitals

        payload = {
            "features": [
                {
                    "Location": "Foothills Medical Centre",
                    "Hospital_N": "Foothills",
                    "IP": 1,
                    "ED": 1,
                },
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_hospitals",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_hospitals()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-ahs-arcgis"
        assert out["_meta"]["lang"] == "en"
        assert out["data"]["count"] == 1
        assert out["data"]["features"][0]["IP"] == 1
        assert out["data"]["features"][0]["ED"] == 1

    @pytest.mark.asyncio
    async def test_french_error_on_upstream(self):
        """lang='fr' returns French UPSTREAM_ERROR when the client raises HTTPStatusError."""
        from mcp_canada.modules.alberta.tools import alberta_get_hospitals

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_hospitals",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_hospitals(lang="fr")
        assert "error" in out
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"
        msg = out["error"]["message"].lower()
        assert any(w in msg for w in ("échec", "erreur"))


class TestAlbertaAhsZonesTool:  # Plan 05
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path — 5-zone payload flows through with correct api_url."""
        from mcp_canada.modules.alberta.tools import alberta_get_ahs_zones
        from mcp_canada.modules.alberta.constants import AHS_ZONE_FS_URL

        payload = {
            "features": [
                {
                    "zone_name": "Calgary",
                    "zone_id": "Z2",
                    "pop_2006": 1_200_000,
                    "pop_2011": 1_400_000,
                    "pop_2016": 1_500_000,
                },
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_ahs_zones",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_ahs_zones()
        assert "_meta" in out
        assert out["_meta"]["source"]["url"] == AHS_ZONE_FS_URL
        assert out["data"]["features"][0]["pop_2016"] == 1_500_000


class TestAlbertaHealthFacilitiesTool:  # Plan 05
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("facility_type", "expected_url_const"),
        [
            ("ems", "AHS_EMS_FS_URL"),
            ("pcn_clinic", "PCN_CLINICS_FS_URL"),
        ],
    )
    async def test_facility_type_dispatch(self, facility_type, expected_url_const):
        """facility_type= routes to the right AHSGIS FeatureServer and sets api_url accordingly."""
        from mcp_canada.modules.alberta import constants as ab_constants
        from mcp_canada.modules.alberta.tools import alberta_get_health_facilities

        payload = {
            "features": [],
            "count": 0,
            "truncated": False,
            "facility_type": facility_type,
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_health_facilities",
            new=mock_fetch,
        ):
            out = await alberta_get_health_facilities(facility_type=facility_type)
        assert "_meta" in out
        assert out["_meta"]["source"]["url"] == getattr(ab_constants, expected_url_const)
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("facility_type") == facility_type

    @pytest.mark.asyncio
    async def test_invalid_facility_type_returns_invalid_input(self):
        """Invalid facility_type returns INVALID_INPUT without calling the client."""
        from mcp_canada.modules.alberta.tools import alberta_get_health_facilities

        mock_client = AsyncMock()
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_health_facilities",
            new=mock_client,
        ):
            out = await alberta_get_health_facilities(facility_type="bogus")  # type: ignore[arg-type]
        assert out.get("error", {}).get("code") == "INVALID_INPUT"
        assert out["error"].get("valid") == ["ems", "pcn_clinic"]
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_facility_type_french_message(self):
        """Invalid facility_type + lang='fr' returns French error message."""
        from mcp_canada.modules.alberta.tools import alberta_get_health_facilities

        out = await alberta_get_health_facilities(
            facility_type="bogus",  # type: ignore[arg-type]
            lang="fr",
        )
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["lang"] == "fr"
        # Contains French wording for "invalid"
        assert "invalide" in out["error"]["message"].lower()

    def test_docstring_mentions_er_wait_times_deferred(self):
        """Pitfall 9: tool must document that ER wait times are NOT included (widget-only)."""
        from mcp_canada.modules.alberta import tools

        doc = tools.alberta_get_health_facilities.__doc__ or ""
        # Must mention ER wait times and widget-only caveat
        doc_lower = doc.lower()
        assert "wait" in doc_lower or "widget" in doc_lower


# ---------------------------------------------------------------------------
# Transport / 511 tools — Plan 06
# ---------------------------------------------------------------------------


class TestAlbertaRoadEventsTool:  # Plan 06
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path: envelope with alberta-511 api_name + /event URL."""
        from mcp_canada.modules.alberta.constants import FIVE11_BASE_URL
        from mcp_canada.modules.alberta.tools import alberta_get_road_events

        payload = {
            "events": [{"ID": "e1", "EventType": "closure"}],
            "count": 1,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_road_events",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_road_events()
        assert "_meta" in out
        assert out["_meta"]["lang"] == "en"
        assert out["_meta"]["source"]["api"] == "alberta-511"
        assert out["_meta"]["source"]["url"] == f"{FIVE11_BASE_URL}/event"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_forwards_event_type(self):
        """event_type= passes through to the client unchanged."""
        from mcp_canada.modules.alberta.tools import alberta_get_road_events

        mock_fetch = AsyncMock(return_value=({"events": [], "count": 0}, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_road_events",
            new=mock_fetch,
        ):
            await alberta_get_road_events(event_type="Construction")
        assert mock_fetch.call_args.kwargs.get("event_type") == "Construction"

    @pytest.mark.asyncio
    async def test_french_error_on_upstream(self):
        """lang='fr' returns French UPSTREAM_ERROR when client raises HTTPStatusError."""
        from mcp_canada.modules.alberta.tools import alberta_get_road_events

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://511.alberta.ca/api/v2/get/event"),
            response=httpx.Response(502),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_road_events",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_road_events(lang="fr")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"
        assert "511" in out["error"]["message"]
        assert "502" in out["error"]["message"]


class TestAlbertaWinterRoadConditionsTool:  # Plan 06
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path: envelope with /winterroads URL."""
        from mcp_canada.modules.alberta.constants import FIVE11_BASE_URL
        from mcp_canada.modules.alberta.tools import (
            alberta_get_winter_road_conditions,
        )

        payload = {"conditions": [{"ID": "wr1"}], "count": 1}
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_winter_road_conditions",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_winter_road_conditions()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-511"
        assert out["_meta"]["source"]["url"] == f"{FIVE11_BASE_URL}/winterroads"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_forwards_area_name(self):
        """area_name= passes through to the client."""
        from mcp_canada.modules.alberta.tools import (
            alberta_get_winter_road_conditions,
        )

        mock_fetch = AsyncMock(
            return_value=({"conditions": [], "count": 0}, False)
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_winter_road_conditions",
            new=mock_fetch,
        ):
            await alberta_get_winter_road_conditions(area_name="Calgary")
        assert mock_fetch.call_args.kwargs.get("area_name") == "Calgary"


class TestAlbertaTrafficCamerasTool:  # Plan 06
    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        """Happy path: envelope with /cameras URL."""
        from mcp_canada.modules.alberta.constants import FIVE11_BASE_URL
        from mcp_canada.modules.alberta.tools import alberta_get_traffic_cameras

        payload = {
            "cameras": [
                {"ID": "c1", "Views": [{"Url": "https://x", "Direction": "N"}]}
            ],
            "count": 1,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_traffic_cameras",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_traffic_cameras()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-511"
        assert out["_meta"]["source"]["url"] == f"{FIVE11_BASE_URL}/cameras"
        assert out["data"]["count"] == 1
        assert out["data"]["cameras"][0]["Views"][0]["Url"] == "https://x"

    @pytest.mark.asyncio
    async def test_english_error_on_upstream(self):
        """Default lang='en' returns English UPSTREAM_ERROR when client raises."""
        from mcp_canada.modules.alberta.tools import alberta_get_traffic_cameras

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(503),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_traffic_cameras",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_traffic_cameras()
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "en"
        assert "503" in out["error"]["message"]


# ---------------------------------------------------------------------------
# Environment / agriculture / demographics / parks — Plan 07
# ---------------------------------------------------------------------------


class TestAlbertaAirQualityTool:  # Plan 07
    """@tool alberta_get_air_quality_stations — envelope + upstream error."""

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_get_air_quality_stations

        payload = {
            "stations": [{"station_name": "Calgary Central"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_air_quality_stations",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_air_quality_stations()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-geodiscover-aqhi"
        assert out["_meta"]["lang"] == "en"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_upstream_error_bilingual(self):
        from mcp_canada.modules.alberta.tools import alberta_get_air_quality_stations

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(503),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_air_quality_stations",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_air_quality_stations(lang="fr")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"
        assert "échec" in out["error"]["message"].lower()


class TestAlbertaWaterAdvisoriesTool:  # Plan 07
    """@tool alberta_get_water_advisories — advisory_type dispatch + INVALID_INPUT."""

    @pytest.mark.asyncio
    async def test_valid_advisory_type_passes_through(self):
        from mcp_canada.modules.alberta.tools import alberta_get_water_advisories

        payload = {
            "advisories": [{"advisory_id": "A-1"}],
            "count": 1,
            "truncated": False,
            "advisory_type": "river",
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_water_advisories",
            new=mock_fetch,
        ):
            out = await alberta_get_water_advisories(advisory_type="river")
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-geodiscover-water"
        assert out["data"]["count"] == 1
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("advisory_type") == "river"

    @pytest.mark.asyncio
    async def test_invalid_advisory_type_returns_invalid_input(self):
        """advisory_type outside the 5-value set → INVALID_INPUT with valid list."""
        from mcp_canada.modules.alberta.tools import alberta_get_water_advisories

        out = await alberta_get_water_advisories(advisory_type="bogus")  # type: ignore[arg-type]
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["valid"] == [
            "river",
            "water_management",
            "drought",
            "ice_cover",
            "water_sharing",
        ]

    @pytest.mark.asyncio
    async def test_invalid_advisory_type_french(self):
        from mcp_canada.modules.alberta.tools import alberta_get_water_advisories

        out = await alberta_get_water_advisories(
            advisory_type="bogus", lang="fr"
        )  # type: ignore[arg-type]
        assert out["error"]["lang"] == "fr"
        msg = out["error"]["message"].lower()
        assert "invalide" in msg or "entrée" in msg


class TestAlbertaCropProductionTool:  # Plan 07
    """@tool alberta_get_crop_production — envelope + upstream error."""

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_get_crop_production

        payload = {
            "rows": [{"year": 2013, "crop": "Wheat"}],
            "count": 1,
            "source_url": "https://open.alberta.ca/x.csv",
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_crop_production",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_crop_production()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-open-data"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_upstream_error(self):
        from mcp_canada.modules.alberta.tools import alberta_get_crop_production

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(500),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_crop_production",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_crop_production(lang="fr")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "fr"


class TestAlbertaPopulationEstimatesTool:  # Plan 07
    """@tool alberta_get_population_estimates — breakdown dispatch + INVALID_INPUT."""

    @pytest.mark.asyncio
    async def test_default_csd_breakdown(self):
        from mcp_canada.modules.alberta.tools import alberta_get_population_estimates

        payload = {
            "rows": [{"geo_code": "4806016", "geo_name": "Calgary"}],
            "count": 1,
            "breakdown": "csd",
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_population_estimates",
            new=mock_fetch,
        ):
            out = await alberta_get_population_estimates()  # default csd
        assert "_meta" in out
        assert out["data"]["breakdown"] == "csd"
        kwargs = mock_fetch.call_args.kwargs
        assert kwargs.get("breakdown") == "csd"

    @pytest.mark.asyncio
    async def test_invalid_breakdown_returns_invalid_input(self):
        from mcp_canada.modules.alberta.tools import alberta_get_population_estimates

        out = await alberta_get_population_estimates(breakdown="bogus")  # type: ignore[arg-type]
        assert out["error"]["code"] == "INVALID_INPUT"
        assert out["error"]["valid"] == [
            "csd",
            "quarterly",
            "annual",
            "age_sex",
            "sub_provincial",
            "components_of_growth",
        ]


class TestAlbertaProvincialParksTool:  # Plan 07
    """@tool alberta_get_provincial_parks — envelope + upstream error."""

    @pytest.mark.asyncio
    async def test_returns_envelope(self):
        from mcp_canada.modules.alberta.tools import alberta_get_provincial_parks

        payload = {
            "parks": [{"park_name": "Kananaskis Country"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_provincial_parks",
            new=AsyncMock(return_value=(payload, False)),
        ):
            out = await alberta_get_provincial_parks()
        assert "_meta" in out
        assert out["_meta"]["source"]["api"] == "alberta-geodiscover-parks"
        assert out["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_upstream_error(self):
        from mcp_canada.modules.alberta.tools import alberta_get_provincial_parks

        err = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://x"),
            response=httpx.Response(502),
        )
        with patch(
            "mcp_canada.modules.alberta.tools._client.fetch_provincial_parks",
            new=AsyncMock(side_effect=err),
        ):
            out = await alberta_get_provincial_parks(lang="en")
        assert out["error"]["code"] == "UPSTREAM_ERROR"
        assert out["error"]["lang"] == "en"


# ---------------------------------------------------------------------------
# Parametrized phase-wide tests — Plan 09
# ---------------------------------------------------------------------------

# (tool_name, client_fn_attribute_on_alberta.client, sample_kwargs, sample_client_return)
#
# Count check: 5 discovery + 4 AER + 4 wildfire + 3 health + 3 transport + 5 env/agri/demo/parks = 24
ALL_ALBERTA_TOOLS: list[tuple[str, str, dict, tuple]] = [
    # Discovery (Plan 02) — 5
    ("alberta_search_datasets", "fetch_search_datasets", {"q": ""}, ({"count": 0, "results": []}, False)),
    ("alberta_get_dataset_details", "fetch_dataset_details", {"package_id": "x"},
     (AlbertaDatasetDetails(id="x", name="x", title="X", resources=[]), False)),
    ("alberta_query_dataset", "fetch_query_dataset", {"package_id": "x"},
     ({"data": [], "format": "CSV", "url": "u"}, False)),
    ("alberta_list_organizations", "fetch_organizations", {}, ([], False)),
    ("alberta_list_categories", "fetch_format_categories", {}, ([], False)),
    # AER / energy (Plan 03) — 4
    ("alberta_get_well_licences_today", "fetch_well_licences_today", {}, ([], False)),
    ("alberta_get_well_licences_archive", "fetch_well_licences_archive",
     {"year": 2024, "month": 1}, ({"url": "x", "year": 2024, "month": 1}, False)),
    ("alberta_get_pipeline_statistics", "fetch_pipeline_statistics", {"year": 2024}, ([], False)),
    ("alberta_get_production_volumes", "fetch_production_volumes", {"product": "Gas"}, ([], False)),
    # Wildfire (Plan 04) — 4
    ("alberta_get_active_fires", "fetch_active_fires", {},
     ({"features": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_fire_perimeters", "fetch_fire_perimeters", {"status": "active"},
     ({"features": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_fire_bans", "fetch_fire_bans", {},
     ({"features": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_fire_control_orders", "fetch_fire_control_orders", {"category": "fire_control"},
     ({"features": [], "count": 0, "truncated": False}, False)),
    # Health (Plan 05) — 3
    ("alberta_get_hospitals", "fetch_hospitals", {},
     ({"features": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_ahs_zones", "fetch_ahs_zones", {},
     ({"features": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_health_facilities", "fetch_health_facilities", {"facility_type": "ems"},
     ({"features": [], "count": 0, "truncated": False, "facility_type": "ems"}, False)),
    # Transport / 511 (Plan 06) — 3
    ("alberta_get_road_events", "fetch_road_events", {},
     ({"events": [], "count": 0}, False)),
    ("alberta_get_winter_road_conditions", "fetch_winter_road_conditions", {},
     ({"conditions": [], "count": 0}, False)),
    ("alberta_get_traffic_cameras", "fetch_traffic_cameras", {},
     ({"cameras": [], "count": 0}, False)),
    # Environment / agriculture / demographics / parks (Plan 07) — 5
    ("alberta_get_air_quality_stations", "fetch_air_quality_stations", {},
     ({"stations": [], "count": 0, "truncated": False}, False)),
    ("alberta_get_water_advisories", "fetch_water_advisories", {"advisory_type": "river"},
     ({"advisories": [], "count": 0, "truncated": False, "advisory_type": "river"}, False)),
    ("alberta_get_crop_production", "fetch_crop_production", {},
     ({"rows": [], "count": 0, "source_url": "https://open.alberta.ca/x.csv"}, False)),
    ("alberta_get_population_estimates", "fetch_population_estimates", {"breakdown": "csd"},
     ({"rows": [], "count": 0, "breakdown": "csd"}, False)),
    ("alberta_get_provincial_parks", "fetch_provincial_parks", {},
     ({"parks": [], "count": 0, "truncated": False}, False)),
]

# Sanity: count must equal 24 (5 + 4 + 4 + 3 + 3 + 5)
assert len(ALL_ALBERTA_TOOLS) == 24, (
    f"ALL_ALBERTA_TOOLS must have 24 entries (got {len(ALL_ALBERTA_TOOLS)}) — "
    "adding or removing alberta tools requires updating this list in lockstep"
)


class TestAlbertaEnvelopes:
    """Plan 09 — parametrized over all 24 tools; verifies _meta envelope shape."""

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_ALBERTA_TOOLS,
        ids=[t[0] for t in ALL_ALBERTA_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_envelope_structure(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ):
        """Every tool returns `_meta` with {source.api, source.url, cached, lang, timestamp}."""
        from mcp_canada.modules.alberta import tools

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.alberta.tools._client.{client_fn}",
            new=AsyncMock(return_value=client_return),
        ):
            result = await tool_fn(**kwargs, lang="en")

        assert "_meta" in result, f"{tool_name} missing _meta envelope"
        meta = result["_meta"]
        for key in ("source", "cached", "lang", "timestamp"):
            assert key in meta, f"{tool_name} _meta missing '{key}'"
        assert "api" in meta["source"], f"{tool_name} _meta.source missing 'api'"
        assert "url" in meta["source"], f"{tool_name} _meta.source missing 'url'"
        assert meta["lang"] == "en", (
            f"{tool_name} should default _meta.lang to 'en', got {meta['lang']!r}"
        )


class TestAlbertaLangParam:
    """Plan 09 — parametrized over all 24 tools; verifies lang='fr' propagation to _meta.lang."""

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_ALBERTA_TOOLS,
        ids=[t[0] for t in ALL_ALBERTA_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_lang_propagation(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ):
        """Every tool propagates `lang='fr'` to the `_meta.lang` field on success."""
        from mcp_canada.modules.alberta import tools

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.alberta.tools._client.{client_fn}",
            new=AsyncMock(return_value=client_return),
        ):
            result = await tool_fn(**kwargs, lang="fr")

        assert result.get("_meta", {}).get("lang") == "fr", (
            f"{tool_name} did not propagate lang='fr' to _meta.lang — got {result.get('_meta')}"
        )
