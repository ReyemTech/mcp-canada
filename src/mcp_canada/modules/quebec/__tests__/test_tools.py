"""Unit tests for quebec_ tool functions.

Plan 02 tests have real bodies (discovery tools).
Plans 03/04 remain as skips.

Total: 18 tools (5 discovery + 13 curated).
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from mcp_canada.modules.quebec import tools as q_tools
from mcp_canada.modules.quebec.schemas import (
    QuebecCategory,
    QuebecDatasetDetails,
    QuebecDatasetSummary,
    QuebecOrganization,
    QuebecResource,
)

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Discovery tools — Plan 02
# ---------------------------------------------------------------------------


class TestQuebecSearchDatasets:
    async def test_happy_path(self):
        summary = QuebecDatasetSummary(
            id="abc123",
            name="test-dataset",
            title="Titre en français",
            organization_slug="msss",
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_search_datasets",
            new=AsyncMock(return_value=([summary], False)),
        ):
            result = await q_tools.quebec_search_datasets(q="sante")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "donnees-quebec"
        assert isinstance(result["data"], list)
        assert result["data"][0]["title"] == "Titre en français"
        assert result["data"][0]["name"] == "test-dataset"

    async def test_invalid_empty_q(self):
        result = await q_tools.quebec_search_datasets(q="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "q" in result["error"]["message"].lower() or "requires" in result["error"]["message"].lower()

    async def test_lang_fr_error(self):
        result = await q_tools.quebec_search_datasets(q="", lang="fr")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "nécessite" in result["error"]["message"]

    async def test_organization_filter(self):
        summary = QuebecDatasetSummary(
            id="xyz",
            name="msss-dataset",
            title="Dataset MSSS",
            organization_slug="msss",
        )
        mock = AsyncMock(return_value=([summary], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_search_datasets", new=mock):
            result = await q_tools.quebec_search_datasets(q="sante", organization="msss")
        assert "_meta" in result
        mock.assert_called_once()
        call_kwargs = mock.call_args.kwargs
        assert call_kwargs.get("organization") == "msss"

    async def test_meta_envelope_shape(self):
        summary = QuebecDatasetSummary(id="1", name="test", title="Test")
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_search_datasets",
            new=AsyncMock(return_value=([summary], True)),
        ):
            result = await q_tools.quebec_search_datasets(q="test")
        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert result["_meta"]["cached"] is True

    async def test_upstream_error_returns_error_envelope(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_search_datasets",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_search_datasets(q="sante")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetDatasetDetails:
    async def test_happy_path(self):
        resource = QuebecResource(
            id="res1",
            format="CSV",
            url="https://example.com/data.csv",
            datastore_active=True,
        )
        details = QuebecDatasetDetails(
            id="pkg1",
            name="test-pkg",
            title="Titre du jeu de données",
            organization_slug="msss",
            resources=[resource],
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_dataset_details",
            new=AsyncMock(return_value=(details, False)),
        ):
            result = await q_tools.quebec_get_dataset_details(package_id="test-pkg")
        assert "_meta" in result
        assert result["data"]["name"] == "test-pkg"
        assert result["data"]["title"] == "Titre du jeu de données"
        assert len(result["data"]["resources"]) == 1
        assert result["data"]["resources"][0]["datastore_active"] is True

    async def test_not_found(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_dataset_details",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(404),
            )),
        ):
            result = await q_tools.quebec_get_dataset_details(package_id="bad-id")
        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    async def test_empty_package_id_returns_invalid_input(self):
        result = await q_tools.quebec_get_dataset_details(package_id="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    async def test_lang_fr_empty_package_id(self):
        result = await q_tools.quebec_get_dataset_details(package_id="", lang="fr")
        assert "error" in result
        assert "nécessite" in result["error"]["message"]

    async def test_surfaces_datastore_active_flag(self):
        resource = QuebecResource(
            id="res2",
            format="CSV",
            url="https://example.com/data.csv",
            datastore_active=True,
        )
        details = QuebecDatasetDetails(
            id="pkg2",
            name="some-pkg",
            title="Test",
            resources=[resource],
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_dataset_details",
            new=AsyncMock(return_value=(details, False)),
        ):
            result = await q_tools.quebec_get_dataset_details(package_id="some-pkg")
        assert result["data"]["resources"][0]["datastore_active"] is True


class TestQuebecQueryDataset:
    async def test_routes_to_datastore(self):
        payload = {
            "records": [{"col": "val"}],
            "total": 116,
            "source": "datastore",
            "resource_id": "res-id",
            "resource_url": "https://example.com",
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_query_dataset",
            new=AsyncMock(return_value=(payload, False)),
        ):
            result = await q_tools.quebec_query_dataset(package_id="some-pkg")
        assert "_meta" in result
        assert result["data"]["source"] == "datastore"
        assert result["data"]["total"] == 116

    async def test_routes_to_fetch_and_parse(self):
        payload = {
            "records": [{"a": "b"}],
            "total": 50,
            "source": "file",
            "resource_id": "file-res",
            "resource_url": "https://example.com/data.csv",
            "format": "CSV",
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_query_dataset",
            new=AsyncMock(return_value=(payload, False)),
        ):
            result = await q_tools.quebec_query_dataset(package_id="another-pkg")
        assert "_meta" in result
        assert result["data"]["source"] == "file"

    async def test_no_parseable_resources_returns_error(self):
        """When package_id is empty, tool returns INVALID_INPUT error."""
        result = await q_tools.quebec_query_dataset(package_id="")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    async def test_upstream_error_returns_error_envelope(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_query_dataset",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_query_dataset(package_id="some-pkg")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    async def test_generic_exception_returns_error_envelope(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_query_dataset",
            new=AsyncMock(side_effect=ValueError("unexpected")),
        ):
            result = await q_tools.quebec_query_dataset(package_id="some-pkg")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecListOrganizations:
    async def test_returns_orgs(self):
        orgs = [
            QuebecOrganization(name="msss", title="Ministère de la Santé", package_count=42),
            QuebecOrganization(name="mtq", title="Ministère des Transports", package_count=35),
        ]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_organizations",
            new=AsyncMock(return_value=(orgs, False)),
        ):
            result = await q_tools.quebec_list_organizations()
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "msss"

    async def test_meta_envelope_shape(self):
        orgs = [QuebecOrganization(name="mrn", title="MRN", package_count=10)]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_organizations",
            new=AsyncMock(return_value=(orgs, False)),
        ):
            result = await q_tools.quebec_list_organizations()
        assert "source" in result["_meta"]
        assert result["_meta"]["source"]["api"] == "donnees-quebec"
        assert "organization_list" in result["_meta"]["source"]["url"]

    async def test_upstream_error_returns_error_envelope(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_organizations",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_list_organizations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecListCategories:
    async def test_uses_groups_not_tags(self):
        cats = [
            QuebecCategory(name="sante", display_name="Santé", package_count=120),
            QuebecCategory(name="environnement", display_name="Environnement", package_count=65),
        ]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_categories",
            new=AsyncMock(return_value=(cats, False)),
        ):
            result = await q_tools.quebec_list_categories()
        assert "_meta" in result
        assert isinstance(result["data"], list)
        # URL should reference group_list (not tag_list)
        assert "group_list" in result["_meta"]["source"]["url"]

    async def test_returns_10_groups(self):
        cats = [
            QuebecCategory(name=f"group-{i}", display_name=f"Group {i}", package_count=i * 10)
            for i in range(10)
        ]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_categories",
            new=AsyncMock(return_value=(cats, False)),
        ):
            result = await q_tools.quebec_list_categories()
        assert len(result["data"]) == 10

    async def test_upstream_error_returns_error_envelope(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_categories",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_list_categories()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ---------------------------------------------------------------------------
# Health / MSSS — Plan 03
# ---------------------------------------------------------------------------


class TestQuebecGetHealthInstallations:
    async def test_happy_path(self):
        from mcp_canada.modules.quebec.schemas import QuebecHealthInstallation
        row = QuebecHealthInstallation(
            instal_code="12345",
            instal_name="Hôpital de Chicoutimi",
            rss_name="Saguenay-Lac-Saint-Jean",
            is_chsgs=True,
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_health_installations",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_health_installations()
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["instal_name"] == "Hôpital de Chicoutimi"

    async def test_filter_by_type_clsc(self):
        from mcp_canada.modules.quebec.schemas import QuebecHealthInstallation
        row = QuebecHealthInstallation(instal_code="99", instal_name="CLSC Test", is_clsc=True)
        mock = AsyncMock(return_value=([row], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_health_installations", new=mock):
            result = await q_tools.quebec_get_health_installations(instal_type="CLSC")
        assert "_meta" in result
        mock.assert_called_once()
        assert mock.call_args.kwargs.get("instal_type") == "CLSC"

    async def test_filter_by_type_hospital(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_health_installations", new=mock):
            result = await q_tools.quebec_get_health_installations(instal_type="CHSGS")
        assert "_meta" in result
        assert mock.call_args.kwargs.get("instal_type") == "CHSGS"

    async def test_lang_fr_error(self):
        result = await q_tools.quebec_get_health_installations(instal_type="BOGUS", lang="fr")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "invalide" in result["error"]["message"]

    async def test_meta_envelope_shape(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_health_installations",
            new=AsyncMock(return_value=([], True)),
        ):
            result = await q_tools.quebec_get_health_installations()
        assert "_meta" in result
        assert result["_meta"]["cached"] is True
        assert result["_meta"]["source"]["api"] == "donnees-quebec"

    async def test_invalid_instal_type_en_error(self):
        result = await q_tools.quebec_get_health_installations(instal_type="INVALID")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "Invalid" in result["error"]["message"]

    async def test_upstream_error(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_health_installations",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_get_health_installations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetErWaitTimes:
    async def test_happy_path(self):
        from mcp_canada.modules.quebec.schemas import QuebecErWaitRow
        row = QuebecErWaitRow(
            installation="Hôpital de Rimouski",
            functional_stretchers=20,
            occupied_stretchers=25,
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_er_wait_times",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_er_wait_times()
        assert "_meta" in result
        assert result["data"][0]["installation"] == "Hôpital de Rimouski"

    async def test_meta_envelope_shape(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_er_wait_times",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await q_tools.quebec_get_er_wait_times()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "donnees-quebec"
        assert "datastore_search" in result["_meta"]["source"]["url"]

    async def test_q_filter(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_er_wait_times", new=mock):
            await q_tools.quebec_get_er_wait_times(installation="Rimouski")
        assert mock.call_args.kwargs.get("installation") == "Rimouski"

    async def test_upstream_error(self):
        import httpx
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_er_wait_times",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_get_er_wait_times()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetPopulationByMunicipality:
    async def test_happy_path(self):
        from mcp_canada.modules.quebec.schemas import QuebecPopulationRow
        row = QuebecPopulationRow(municipality="Montréal", admin_region="06", population=1762949)
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_population_by_municipality",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_population_by_municipality()
        assert "_meta" in result
        assert result["data"][0]["municipality"] == "Montréal"

    async def test_region_filter(self):
        mock = AsyncMock(return_value=([], False))
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_population_by_municipality",
            new=mock,
        ):
            await q_tools.quebec_get_population_by_municipality(region="06")
        assert mock.call_args.kwargs.get("region") == "06"

    async def test_meta_envelope_shape(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_population_by_municipality",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await q_tools.quebec_get_population_by_municipality()
        assert "_meta" in result
        assert "MUN.csv" in result["_meta"]["source"]["url"]

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_population_by_municipality",
            new=AsyncMock(side_effect=Exception("CSV unavailable")),
        ):
            result = await q_tools.quebec_get_population_by_municipality()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ---------------------------------------------------------------------------
# MTQ Transport — Plan 03
# ---------------------------------------------------------------------------


class TestQuebecGetRoadConditions:
    async def test_happy_path(self):
        rows = [{"segment_id": "1", "route_num": "40", "pavement_status": "Good"}]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_conditions",
            new=AsyncMock(return_value=(rows, False)),
        ):
            result = await q_tools.quebec_get_road_conditions()
        assert "_meta" in result
        assert result["data"][0]["pavement_status"] == "Good"

    async def test_bilingual_column_selection_en(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_road_conditions", new=mock):
            await q_tools.quebec_get_road_conditions(lang="en")
        assert mock.call_args.kwargs.get("lang") == "en"

    async def test_bilingual_column_selection_fr(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_road_conditions", new=mock):
            await q_tools.quebec_get_road_conditions(lang="fr")
        assert mock.call_args.kwargs.get("lang") == "fr"

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_conditions",
            new=AsyncMock(side_effect=Exception("WFS down")),
        ):
            result = await q_tools.quebec_get_road_conditions()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetRoadWorks:
    async def test_happy_path(self):
        from mcp_canada.modules.quebec.schemas import QuebecRoadWork
        row = QuebecRoadWork(route="A-25", description="One lane closed", location="km 8")
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_works",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_road_works()
        assert "_meta" in result
        assert result["data"][0]["route"] == "A-25"

    async def test_bilingual_description_en(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_road_works", new=mock):
            await q_tools.quebec_get_road_works(lang="en")
        assert mock.call_args.kwargs.get("lang") == "en"

    async def test_bilingual_description_fr(self):
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_road_works", new=mock):
            await q_tools.quebec_get_road_works(lang="fr")
        assert mock.call_args.kwargs.get("lang") == "fr"

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_works",
            new=AsyncMock(side_effect=Exception("WFS error")),
        ):
            result = await q_tools.quebec_get_road_works()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetRoadEvents:
    async def test_happy_path(self):
        from mcp_canada.modules.quebec.schemas import QuebecRoadEvent
        row = QuebecRoadEvent(route="A-40", cause="Collision", municipality="Montréal")
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_events",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_road_events()
        assert "_meta" in result
        assert result["data"][0]["route"] == "A-40"

    async def test_meta_envelope_shape(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_events",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await q_tools.quebec_get_road_events()
        assert "_meta" in result
        assert "mapserver" in result["_meta"]["source"]["url"]

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_road_events",
            new=AsyncMock(side_effect=Exception("WFS error")),
        ):
            result = await q_tools.quebec_get_road_events()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetBridgeStructures:
    async def test_requires_filter_error(self):
        result = await q_tools.quebec_get_bridge_structures()
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "route" in result["error"]["message"].lower() or "filter" in result["error"]["message"].lower()

    async def test_lang_fr_error_message(self):
        result = await q_tools.quebec_get_bridge_structures(lang="fr")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "au moins un" in result["error"]["message"]

    async def test_route_filter(self):
        from mcp_canada.modules.quebec.schemas import QuebecBridgeStructure
        row = QuebecBridgeStructure(structure_id="S-1", route_num="10", municipality="Granby")
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_bridge_structures",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_bridge_structures(route="10")
        assert "_meta" in result
        assert result["data"][0]["route_num"] == "10"

    async def test_municipality_filter(self):
        from mcp_canada.modules.quebec.schemas import QuebecBridgeStructure
        row = QuebecBridgeStructure(structure_id="S-1", municipality="Granby")
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_bridge_structures",
            new=AsyncMock(return_value=([row], False)),
        ):
            result = await q_tools.quebec_get_bridge_structures(municipality="Granby")
        assert "_meta" in result
        assert result["data"][0]["structure_id"] == "S-1"

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_bridge_structures",
            new=AsyncMock(side_effect=Exception("WFS error")),
        ):
            result = await q_tools.quebec_get_bridge_structures(municipality="Granby")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ---------------------------------------------------------------------------
# Environment / Demographics / Energy — Plan 04
# ---------------------------------------------------------------------------


class TestQuebecGetForestFiresHistory:
    async def test_returns_metadata(self):
        """quebec_get_forest_fires_history returns metadata dict with _meta envelope."""
        metadata = {
            "id": "fires-uuid",
            "name": "feux-de-foret",
            "title": "Feux de forêt",
            "notes": "Données historiques...",
            "organization_slug": "mrn",
            "organization_title": "MRN",
            "update_frequency": "annuel",
            "license_id": "cc-by",
            "resources": [
                {"id": "shp-001", "name": "Feux SHP", "format": "SHP",
                 "url": "https://example.com/feux.shp", "datastore_active": False, "size": None},
            ],
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_forest_fires_history",
            new=AsyncMock(return_value=(metadata, False)),
        ):
            result = await q_tools.quebec_get_forest_fires_history()
        assert "_meta" in result
        assert result["data"]["name"] == "feux-de-foret"

    async def test_includes_download_urls(self):
        """Resources list in response includes SHP/GPKG download URLs."""
        metadata = {
            "id": "fires-uuid",
            "name": "feux-de-foret",
            "title": "Feux de forêt",
            "notes": None,
            "organization_slug": "mrn",
            "organization_title": "MRN",
            "update_frequency": "annuel",
            "license_id": "cc-by",
            "resources": [
                {"id": "shp-001", "name": "Feux SHP", "format": "SHP",
                 "url": "https://example.com/feux.shp", "datastore_active": False, "size": None},
                {"id": "gpkg-001", "name": "Feux GPKG", "format": "GPKG",
                 "url": "https://example.com/feux.gpkg", "datastore_active": False, "size": None},
            ],
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_forest_fires_history",
            new=AsyncMock(return_value=(metadata, False)),
        ):
            result = await q_tools.quebec_get_forest_fires_history()
        assert "_meta" in result
        resources = result["data"]["resources"]
        assert len(resources) == 2
        formats = {r["format"] for r in resources}
        assert "SHP" in formats


class TestQuebecGetAirQualityStations:
    async def test_happy_path(self):
        """quebec_get_air_quality_stations returns station list with _meta envelope."""
        from mcp_canada.modules.quebec.schemas import QuebecAirQualityStation
        station = QuebecAirQualityStation(
            station_id="06033",
            station_name="Montréal - Anjou",
            admin_region="06",
            municipality="Montréal",
            milieu_type="Urbain",
            latitude=45.6041,
            longitude=-73.5626,
        )
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_air_quality_stations",
            new=AsyncMock(return_value=([station], False)),
        ):
            result = await q_tools.quebec_get_air_quality_stations()
        assert "_meta" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["station_id"] == "06033"

    async def test_active_only_filter(self):
        """active_only param is passed through to client."""
        mock = AsyncMock(return_value=([], False))
        with patch("mcp_canada.modules.quebec.tools._client.fetch_air_quality_stations", new=mock):
            await q_tools.quebec_get_air_quality_stations(active_only=False)
        assert mock.call_args.kwargs.get("active_only") is False

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_air_quality_stations",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_get_air_quality_stations()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetAirQualityIndex:
    async def test_happy_path(self):
        """quebec_get_air_quality_index returns measurements list with _meta envelope."""
        measurements = [
            {"NOM_STATION": "Montréal - Anjou", "IQA": 25, "COTE": "Bon",
             "longitude": -73.5626, "latitude": 45.6041}
        ]
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_air_quality_index",
            new=AsyncMock(return_value=(measurements, False)),
        ):
            result = await q_tools.quebec_get_air_quality_index()
        assert "_meta" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["NOM_STATION"] == "Montréal - Anjou"

    async def test_meta_envelope_shape(self):
        """_meta must include api and url fields pointing to ArcGIS FeatureServer."""
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_air_quality_index",
            new=AsyncMock(return_value=([], False)),
        ):
            result = await q_tools.quebec_get_air_quality_index()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "donnees-quebec"
        assert "arcgis" in result["_meta"]["source"]["url"].lower() or "IQA" in result["_meta"]["source"]["url"]

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_air_quality_index",
            new=AsyncMock(side_effect=httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(500),
            )),
        ):
            result = await q_tools.quebec_get_air_quality_index()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetWaterQualityMonitoring:
    async def test_returns_metadata(self):
        """quebec_get_water_quality_monitoring returns dataset metadata with _meta envelope."""
        metadata = {
            "id": "wq-uuid",
            "name": "suivi-physicochimique-des-rivieres-et-du-fleuve",
            "title": "Suivi physicochimique des rivières et du fleuve",
            "notes": "Données sur la qualité...",
            "organization_slug": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques",
            "organization_title": "MELCCFP",
            "update_frequency": "annuel",
            "license_id": "cc-by",
            "resources": [],
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_water_quality_monitoring",
            new=AsyncMock(return_value=(metadata, False)),
        ):
            result = await q_tools.quebec_get_water_quality_monitoring()
        assert "_meta" in result
        assert result["data"]["name"] == "suivi-physicochimique-des-rivieres-et-du-fleuve"


class TestQuebecGetElectricityData:
    """Tests updated for phase 16-05: fetch_electricity_data now returns 3-tuple (rows, source_url, was_cached)."""

    async def test_happy_path(self):
        """quebec_get_electricity_data returns rows with _meta envelope (3-tuple client return)."""
        rows = [{"annee": "2023", "production_twh": "200.5"}]
        xlsx_url = "https://www.hydroquebec.com/data/suivi-2021.xlsx"
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_electricity_data",
            new=AsyncMock(return_value=(rows, xlsx_url, False)),
        ):
            result = await q_tools.quebec_get_electricity_data()
        assert "_meta" in result
        assert result["data"] == rows

    async def test_meta_envelope_shape(self):
        xlsx_url = "https://www.hydroquebec.com/data/suivi-2021.xlsx"
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_electricity_data",
            new=AsyncMock(return_value=([], xlsx_url, False)),
        ):
            result = await q_tools.quebec_get_electricity_data()
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "donnees-quebec"

    async def test_upstream_error(self):
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_electricity_data",
            new=AsyncMock(side_effect=Exception("CSV unavailable")),
        ):
            result = await q_tools.quebec_get_electricity_data()
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestQuebecGetElectricityDataEnvelope:
    """Regression for UAT Gap 3 — envelope URL must reflect real fetched XLSX, not package_show."""

    async def test_envelope_source_url_points_at_xlsx_not_package_show(self) -> None:
        """_meta.source.url must be the actual XLSX URL, not the CKAN package_show endpoint."""
        xlsx_url = "https://www.hydroquebec.com/data/documents-donnees/xls/suivi-2021-de-l-entente-globale-cadre.xlsx"
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_electricity_data",
            new=AsyncMock(return_value=([{"year": 2021, "prod": 100}], xlsx_url, False)),
        ):
            result = await q_tools.quebec_get_electricity_data(limit=10, lang="en")

        assert "_meta" in result
        assert result["_meta"]["source"]["url"] == xlsx_url
        assert "package_show" not in result["_meta"]["source"]["url"]
        assert len(result["data"]) == 1


class TestQuebecGetProtectedAreas:
    async def test_returns_metadata(self):
        """quebec_get_protected_areas returns dataset metadata with _meta envelope."""
        metadata = {
            "id": "pa-uuid",
            "name": "aires-protegees-au-quebec",
            "title": "Aires protégées au Québec",
            "notes": "Registre...",
            "organization_slug": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques",
            "organization_title": "MELCCFP",
            "update_frequency": "semiannuel",
            "license_id": "cc-by",
            "resources": [
                {"id": "gpkg-001", "name": "Aires GPKG", "format": "GPKG",
                 "url": "https://example.com/aires.gpkg", "datastore_active": False, "size": None},
            ],
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_protected_areas",
            new=AsyncMock(return_value=(metadata, False)),
        ):
            result = await q_tools.quebec_get_protected_areas()
        assert "_meta" in result
        assert result["data"]["name"] == "aires-protegees-au-quebec"

    async def test_includes_download_urls(self):
        """Resources list includes format and URL for each download resource."""
        metadata = {
            "id": "pa-uuid",
            "name": "aires-protegees-au-quebec",
            "title": "Aires protégées au Québec",
            "notes": None,
            "organization_slug": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques",
            "organization_title": "MELCCFP",
            "update_frequency": "semiannuel",
            "license_id": "cc-by",
            "resources": [
                {"id": "gpkg-001", "name": "Aires GPKG", "format": "GPKG",
                 "url": "https://example.com/aires.gpkg", "datastore_active": False, "size": None},
                {"id": "shp-001", "name": "Aires SHP", "format": "SHP",
                 "url": "https://example.com/aires.shp", "datastore_active": False, "size": None},
            ],
        }
        with patch(
            "mcp_canada.modules.quebec.tools._client.fetch_protected_areas",
            new=AsyncMock(return_value=(metadata, False)),
        ):
            result = await q_tools.quebec_get_protected_areas()
        resources = result["data"]["resources"]
        assert len(resources) == 2
        assert any(r["format"] == "GPKG" for r in resources)


class TestQuebecGetErWaitTimesKeywords:
    """Regression for UAT Gap 4 — BM25 discovery must match 'Quebec hospitals health' queries."""

    def test_keywords_contain_health_tokens(self) -> None:
        """Keywords line must contain health, medical, sante tokens."""
        doc = q_tools.quebec_get_er_wait_times.__doc__ or ""
        keywords_line = next(
            (line for line in doc.splitlines() if line.strip().startswith("Keywords:")),
            "",
        )
        assert "health" in keywords_line.lower()
        assert "medical" in keywords_line.lower()
        assert "sante" in keywords_line.lower()

    def test_keywords_still_contain_original_tokens(self) -> None:
        """Keywords line must still contain original pre-fix tokens (additive, not replacement)."""
        doc = q_tools.quebec_get_er_wait_times.__doc__ or ""
        keywords_line = next(
            (line for line in doc.splitlines() if line.strip().startswith("Keywords:")),
            "",
        )
        for token in ("er", "urgence", "hospital", "wait times", "civieres", "msss"):
            assert token in keywords_line.lower(), f"Lost original token: {token}"
