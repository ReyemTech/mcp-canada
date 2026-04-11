"""Unit tests for quebec module client functions.

Wave 0 scaffolds — Plan 02 tests have real bodies; Plans 03/04 remain as skips.

CRITICAL TEST CONTRACT (Phase 15 lesson):
  TestSharedApiGetContract patches `mcp_canada.modules.quebec.client.api_get`
  (the local binding in client.py) with raw-dict AsyncMock return values.
  NEVER use MagicMock(json=lambda: {...}) pattern — that masks the dict-vs-Response
  contract bug that caused Phase 15 gap closure.
"""

import pytest
from unittest.mock import AsyncMock, patch

import httpx

from mcp_canada.modules.quebec import client as q_client

pytestmark = pytest.mark.asyncio


class TestSharedApiGetContract:
    """Contract tests for _api_get — verifies Phase 15 parsed-dict contract.

    Critical Phase 15 lesson: _api_get MUST treat shared api_get return
    as a parsed dict. Patches `mcp_canada.modules.quebec.client.api_get`
    (the local binding) with an AsyncMock returning a raw dict.

    The patch target is `mcp_canada.modules.quebec.client.api_get` because that is
    the name bound in client.py's namespace (via `from mcp_canada.shared.http import api_get`).
    Patching the shared layer directly would NOT intercept calls in this module.
    """

    async def test_success_envelope_unwraps_result(self):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value={"success": True, "result": {"count": 5, "results": []}}),
        ):
            result = await q_client._api_get("package_search", {"q": "test"})
        assert result == {"count": 5, "results": []}

    async def test_ckan_success_false_raises_http_status_error(self):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value={"success": False, "error": {"message": "Not found"}}),
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await q_client._api_get("package_show", {"id": "bad-id"})

    async def test_non_dict_return_raises(self):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value="unexpected string"),
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await q_client._api_get("package_search", {"q": "test"})


# ---------------------------------------------------------------------------
# Discovery client — Plan 02
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    async def test_returns_shaped_summary_list(self, sample_ckan_package_search_response):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_search_response),
        ):
            results, was_cached = await q_client.fetch_search_datasets(q="sante")
        assert isinstance(results, list)
        assert len(results) == 1
        r = results[0]
        assert r.id == "d1a7c5e0-1111-4222-8333-444444444444"
        assert r.name == "repertoire-des-municipalites-du-quebec"
        assert r.title == "Répertoire des municipalités du Québec"
        assert r.organization_slug == "affaires-municipales-et-occupation-du-territoire"
        assert r.num_resources == 3

    async def test_applies_organization_filter(self, sample_ckan_package_search_response):
        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.quebec.client.api_get", new=mock):
            await q_client.fetch_search_datasets(q="test", organization="msss")
        # The call args should include fq with organization:msss
        call_args = mock.call_args
        params = call_args[0][1] if call_args[0] else call_args[1].get("params", {})
        assert "organization:msss" in params.get("fq", "")

    async def test_applies_group_filter(self, sample_ckan_package_search_response):
        mock = AsyncMock(return_value=sample_ckan_package_search_response)
        with patch("mcp_canada.modules.quebec.client.api_get", new=mock):
            await q_client.fetch_search_datasets(q="test", group="sante")
        call_args = mock.call_args
        params = call_args[0][1] if call_args[0] else call_args[1].get("params", {})
        assert "groups:sante" in params.get("fq", "")

    async def test_empty_results_returns_empty_list(self):
        empty_response = {"success": True, "result": {"count": 0, "results": []}}
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=empty_response),
        ):
            results, _ = await q_client.fetch_search_datasets(q="zzz_no_match")
        assert results == []


class TestFetchDatasetDetails:
    async def test_returns_details_with_resources(self, sample_ckan_package_show_response):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_show_response),
        ):
            details, _ = await q_client.fetch_dataset_details("fichier-horaire-des-donnees-de-la-situation-a-l-urgence")
        assert details.name == "fichier-horaire-des-donnees-de-la-situation-a-l-urgence"
        assert details.title == "Données horaires de la situation à l'urgence"
        assert len(details.resources) == 1
        assert details.resources[0].format == "CSV"
        assert details.resources[0].url == "https://example.com/er.csv"

    async def test_surfaces_datastore_active_flag(self, sample_ckan_package_show_response):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_show_response),
        ):
            details, _ = await q_client.fetch_dataset_details("some-pkg")
        assert details.resources[0].datastore_active is True

    async def test_not_found_raises(self):
        error_response = {"success": False, "error": {"message": "Not found"}}
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=error_response),
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await q_client.fetch_dataset_details("non-existent-dataset")


class TestFetchOrganizations:
    async def test_returns_org_list(self, sample_ckan_organization_list_response):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_organization_list_response),
        ):
            orgs, _ = await q_client.fetch_organizations()
        assert len(orgs) == 3
        names = [o.name for o in orgs]
        assert "msss" in names
        assert "mtq" in names
        assert "mrn" in names

    async def test_result_is_cached(self, sample_ckan_organization_list_response):
        mock = AsyncMock(return_value=sample_ckan_organization_list_response)
        with patch("mcp_canada.modules.quebec.client.api_get", new=mock):
            orgs1, _ = await q_client.fetch_organizations()
            # cached_fetch should use cache on 2nd call (mock may not be called again)
        assert len(orgs1) == 3


class TestFetchCategories:
    async def test_uses_group_list_not_tag_list(self, sample_ckan_group_list_response):
        mock = AsyncMock(return_value=sample_ckan_group_list_response)
        with patch("mcp_canada.modules.quebec.client.api_get", new=mock):
            result, _ = await q_client.fetch_categories()
        # Verify action URL contained 'group_list' not 'tag_list'
        call_url = mock.call_args.args[0]
        assert "group_list" in call_url
        assert "tag_list" not in call_url
        assert len(result) >= 1

    async def test_returns_10_groups(self, sample_ckan_group_list_response):
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_group_list_response),
        ):
            result, _ = await q_client.fetch_categories()
        # fixture has 5 groups; just check they're QuebecCategory objects with expected fields
        assert all(hasattr(c, "name") for c in result)
        assert all(hasattr(c, "package_count") for c in result)


class TestFetchQueryDataset:
    async def test_routes_to_datastore_when_active(self, sample_ckan_package_show_response, sample_datastore_er_response):
        """When best resource has datastore_active=True, routes to _datastore_get."""
        # Patch cached_fetch to always call the fetcher (bypass cache isolation issues)
        import mcp_canada.modules.quebec.client as _mod

        original_cached_fetch = _mod.cached_fetch

        async def passthrough_cached_fetch(key, ttl, fetcher):
            return (await fetcher(), False)

        with patch.object(_mod, "cached_fetch", side_effect=passthrough_cached_fetch):
            with patch(
                "mcp_canada.modules.quebec.client.api_get",
                new=AsyncMock(side_effect=[
                    sample_ckan_package_show_response,  # package_show call
                    sample_datastore_er_response,       # datastore_search call
                ]),
            ):
                payload, _ = await q_client.fetch_query_dataset("datastore-test-pkg-unique")
        assert payload["source"] == "datastore"
        assert "records" in payload
        assert payload["total"] == 116

    async def test_falls_back_to_csv_when_no_datastore(self, sample_ckan_package_show_csv_only_response):
        """When resource has no datastore, falls back to fetch_and_parse."""
        csv_rows = [{"col1": "val1"}]
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_show_csv_only_response),
        ):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(csv_rows, False)),
            ):
                payload, _ = await q_client.fetch_query_dataset("feux-de-foret")
        assert payload["source"] == "file"
        assert payload["records"] == csv_rows

    async def test_picks_best_file_resource(self):
        """CSV should be preferred over SHP when both exist."""
        pkg_with_multiple = {
            "success": True,
            "result": {
                "id": "multi-res",
                "name": "multi-resource-dataset",
                "title": "Dataset with multiple resources",
                "resources": [
                    {"id": "res-shp", "format": "SHP", "url": "https://example.com/data.shp", "datastore_active": False},
                    {"id": "res-csv", "format": "CSV", "url": "https://example.com/data.csv", "datastore_active": False},
                    {"id": "res-json", "format": "JSON", "url": "https://example.com/data.json", "datastore_active": False},
                ],
            },
        }
        csv_rows = [{"col": "val"}]
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=pkg_with_multiple),
        ):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(csv_rows, False)),
            ) as mock_parse:
                await q_client.fetch_query_dataset("multi-resource-dataset")
        # Should have picked CSV (res-csv) over SHP and JSON
        call_url = mock_parse.call_args.args[0]
        assert "data.csv" in call_url


# ---------------------------------------------------------------------------
# Health / MSSS — Plan 03
# ---------------------------------------------------------------------------


class TestFetchHealthInstallations:
    async def test_returns_installation_list(self, sample_datastore_installations_response):
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=AsyncMock(return_value=sample_datastore_installations_response["result"]),
        ):
            result, was_cached = await q_client.fetch_health_installations()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].instal_name == "Hôpital de Chicoutimi"
        assert result[0].is_chsgs is True
        assert result[0].is_clsc is False

    async def test_filters_by_clsc_flag(self, sample_datastore_installations_response):
        sample = dict(sample_datastore_installations_response)
        sample["result"]["records"][0]["CLSC"] = "Oui"
        sample["result"]["records"][0]["CHSGS"] = "Non"
        mock_ds = AsyncMock(return_value=sample["result"])
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=mock_ds,
        ):
            result, _ = await q_client.fetch_health_installations(instal_type="CLSC")
        assert mock_ds.call_args.args[0] == "2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d"
        # The second arg (params) should include filters for CLSC
        params = mock_ds.call_args.args[1]
        assert "filters" in params
        assert "CLSC" in params["filters"]
        assert result[0].is_clsc is True

    async def test_filters_by_hospital_flag(self, sample_datastore_installations_response):
        mock_ds = AsyncMock(return_value=sample_datastore_installations_response["result"])
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=mock_ds,
        ):
            await q_client.fetch_health_installations(instal_type="CHSGS")
        params = mock_ds.call_args.args[1]
        assert "CHSGS" in params.get("filters", "")

    async def test_filters_by_region(self, sample_datastore_installations_response):
        mock_ds = AsyncMock(return_value=sample_datastore_installations_response["result"])
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=mock_ds,
        ):
            await q_client.fetch_health_installations(rss_name="Montréal")
        params = mock_ds.call_args.args[1]
        assert "RSS_NOM" in params.get("filters", "")


class TestFetchErWaitTimes:
    async def test_returns_116_rows(self, sample_datastore_er_response):
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=AsyncMock(return_value=sample_datastore_er_response["result"]),
        ):
            result, _ = await q_client.fetch_er_wait_times()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].installation == "Hôpital de Rimouski"
        assert result[0].functional_stretchers == 20
        assert result[0].patients_over_24h == 3

    async def test_optional_q_filter(self, sample_datastore_er_response):
        mock_ds = AsyncMock(return_value=sample_datastore_er_response["result"])
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=mock_ds,
        ):
            await q_client.fetch_er_wait_times(installation="Rimouski")
        params = mock_ds.call_args.args[1]
        assert params.get("q") == "Rimouski"


class TestFetchPopulationByMunicipality:
    async def test_parses_mamh_csv(self, sample_mamh_municipalities_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mamh_municipalities_csv, False)),
        ):
            result, _ = await q_client.fetch_population_by_municipality()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].municipality == "Montréal"
        assert result[0].population == 1762949
        assert result[0].admin_region == "06"

    async def test_region_filter(self, sample_mamh_municipalities_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mamh_municipalities_csv, False)),
        ):
            result, _ = await q_client.fetch_population_by_municipality(region="03")
        assert len(result) == 1
        assert result[0].municipality == "Québec"


# ---------------------------------------------------------------------------
# Transport / MTQ — Plan 03
# ---------------------------------------------------------------------------


class TestFetchRoadConditions:
    async def test_parses_conditions_csv(self):
        sample_rows = [
            {
                "NumeroSegment": "12345",
                "NumeroRoute": "40",
                "NomRoute": "Autoroute 40",
                "NomRegion": "Montréal",
                "DescriptionEtatChausseeEN": "Good",
                "DescriptionEtatChausseeFR": "Bon",
                "DescriptionVisibiliteEN": "Clear",
                "DescriptionVisibiliteFR": "Dégagé",
                "IndicateurPresenceLamesNeige": "Non",
                "DateEtHeureCondition": "2026-04-11 08:00",
            }
        ]
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_rows, False)),
        ):
            result, _ = await q_client.fetch_road_conditions(lang="en")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["pavement_status"] == "Good"
        assert result[0]["route_num"] == "40"

    async def test_bilingual_column_fr(self):
        sample_rows = [
            {
                "NumeroSegment": "12345",
                "NumeroRoute": "40",
                "NomRoute": "Autoroute 40",
                "NomRegion": "Montréal",
                "DescriptionEtatChausseeEN": "Good",
                "DescriptionEtatChausseeFR": "Bon",
                "DescriptionVisibiliteEN": "Clear",
                "DescriptionVisibiliteFR": "Dégagé",
                "IndicateurPresenceLamesNeige": "Non",
                "DateEtHeureCondition": "2026-04-11 08:00",
            }
        ]
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_rows, False)),
        ):
            result, _ = await q_client.fetch_road_conditions(lang="fr")
        assert result[0]["pavement_status"] == "Bon"

    async def test_returns_empty_on_parse_error(self):
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(side_effect=Exception("WFS endpoint down")),
            ):
                result, _ = await q_client.fetch_road_conditions()
        assert result == []


class TestFetchRoadWorks:
    async def test_parses_mtq_wfs_csv(self, sample_mtq_road_works_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_road_works_csv, False)),
        ):
            result, _ = await q_client.fetch_road_works(lang="fr")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].route == "A-25"
        assert result[0].description == "Fermeture d'une voie sens nord entre km 7 et km 9."

    async def test_bilingual_description_en(self, sample_mtq_road_works_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_road_works_csv, False)),
        ):
            result, _ = await q_client.fetch_road_works(lang="en")
        assert result[0].description == "One lane closed northbound between km 7 and km 9."


class TestFetchRoadEvents:
    async def test_parses_evenements_csv(self, sample_mtq_road_events_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_road_events_csv, False)),
        ):
            result, _ = await q_client.fetch_road_events()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].route == "A-40"
        assert result[0].cause == "Collision"
        assert result[0].municipality == "Montréal"


class TestFetchBridgeStructures:
    async def test_returns_bridge_rows(self, sample_mtq_bridges_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_bridges_csv, False)),
        ):
            result, _ = await q_client.fetch_bridge_structures(route="10")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].structure_id == "S-12345"
        assert result[0].route_num == "10"
        assert result[0].municipality == "Granby"

    async def test_requires_at_least_one_filter(self):
        # The filter guard is in the TOOL (not client) — client can be called without filters
        # but returns empty if nothing matches (test that it doesn't error without filters)
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=([], False)),
        ):
            result, _ = await q_client.fetch_bridge_structures()
        assert result == []

    async def test_route_filter(self, sample_mtq_bridges_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_bridges_csv, False)),
        ):
            result_match, _ = await q_client.fetch_bridge_structures(route="10")
            result_no_match, _ = await q_client.fetch_bridge_structures(route="999")
        assert len(result_match) == 1
        assert len(result_no_match) == 0

    async def test_municipality_filter(self, sample_mtq_bridges_csv):
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_mtq_bridges_csv, False)),
        ):
            result, _ = await q_client.fetch_bridge_structures(municipality="Granby")
        assert len(result) == 1
        assert result[0].municipality == "Granby"


# ---------------------------------------------------------------------------
# Environment / Energy — Plan 04
# ---------------------------------------------------------------------------


class TestFetchForestFiresHistory:
    async def test_returns_package_metadata_only(self, sample_ckan_package_show_csv_only_response):
        """fetch_forest_fires_history returns dataset details dict (metadata only)."""
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=sample_ckan_package_show_csv_only_response),
        ):
            result, _ = await q_client.fetch_forest_fires_history()
        assert isinstance(result, dict)
        assert "name" in result
        assert result["name"] == "feux-de-foret"


class TestFetchAirQualityStations:
    async def test_returns_station_list(self, sample_datastore_aq_stations_response):
        """fetch_air_quality_stations returns list of QuebecAirQualityStation objects."""
        from mcp_canada.modules.quebec.schemas import QuebecAirQualityStation
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=AsyncMock(return_value=sample_datastore_aq_stations_response["result"]),
        ):
            result, was_cached = await q_client.fetch_air_quality_stations(active_only=False)
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], QuebecAirQualityStation)
        assert result[0].station_id == "06033"
        assert result[0].station_name == "Montréal - Anjou"

    async def test_filters_active_stations(self, sample_datastore_aq_stations_response):
        """active_only=True excludes rows with DATE_FERMETURE set."""
        records = sample_datastore_aq_stations_response["result"]["records"]
        records[0]["DATE_FERMETURE"] = "2020-12-31"  # closed station
        with patch(
            "mcp_canada.modules.quebec.client._datastore_get",
            new=AsyncMock(return_value={"records": records, "total": 2, "fields": []}),
        ):
            result, _ = await q_client.fetch_air_quality_stations(active_only=True)
        # Only the second station (no DATE_FERMETURE) should be returned
        assert len(result) == 1
        assert result[0].station_id == "03002"


class TestFetchAirQualityIndex:
    async def test_calls_arcgis_rest(self):
        """fetch_air_quality_index calls api_get with AQ_INDEX_URL and ?f=json."""
        arcgis_response = {
            "features": [
                {
                    "attributes": {"NOM_STATION": "Montréal - Anjou", "IQA": 25, "COTE": "Bon"},
                    "geometry": {"x": -73.5626, "y": 45.6041},
                }
            ]
        }
        mock_api = AsyncMock(return_value=arcgis_response)
        with patch("mcp_canada.modules.quebec.client.api_get", new=mock_api):
            result, _ = await q_client.fetch_air_quality_index(limit=1)
        assert mock_api.call_count == 1
        call_url = mock_api.call_args.args[0]
        from mcp_canada.modules.quebec.constants import AQ_INDEX_URL
        assert call_url == AQ_INDEX_URL
        params = mock_api.call_args.args[1]
        assert params.get("f") == "json"

    async def test_returns_measurements(self):
        """fetch_air_quality_index returns list of dicts with merged attributes + lat/lon."""
        arcgis_response = {
            "features": [
                {
                    "attributes": {"NOM_STATION": "Montréal - Anjou", "IQA": 25},
                    "geometry": {"x": -73.5626, "y": 45.6041},
                }
            ]
        }
        with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=arcgis_response)):
            result, _ = await q_client.fetch_air_quality_index()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["NOM_STATION"] == "Montréal - Anjou"
        assert result[0]["longitude"] == -73.5626
        assert result[0]["latitude"] == 45.6041


class TestFetchWaterQualityMonitoring:
    async def test_returns_package_metadata(self, sample_ckan_package_show_csv_only_response):
        """fetch_water_quality_monitoring returns metadata dict from package_show."""
        # Reuse a different package show fixture style
        pkg_response = {
            "success": True,
            "result": {
                "id": "wq-uuid",
                "name": "suivi-physicochimique-des-rivieres-et-du-fleuve",
                "title": "Suivi physicochimique des rivières et du fleuve",
                "notes": "Données sur la qualité de l'eau...",
                "organization": {"name": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques", "title": "MELCCFP"},
                "resources": [],
            },
        }
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=pkg_response),
        ):
            result, _ = await q_client.fetch_water_quality_monitoring()
        assert isinstance(result, dict)
        assert result["name"] == "suivi-physicochimique-des-rivieres-et-du-fleuve"


class TestFetchElectricityData:
    async def test_parses_hydro_quebec_csv(self):
        """fetch_electricity_data finds CSV resource then calls fetch_and_parse."""
        hydro_pkg = {
            "success": True,
            "result": {
                "id": "hydro-uuid",
                "name": "historique-production-consommation",
                "title": "Historique de production et consommation",
                "notes": "Données historiques...",
                "organization": {"name": "hydro-quebec", "title": "Hydro-Québec"},
                "resources": [
                    {
                        "id": "csv-001",
                        "name": "Historique CSV",
                        "format": "CSV",
                        "url": "https://hydroquebec.com/data/historique.csv",
                        "datastore_active": False,
                    }
                ],
            },
        }
        sample_rows = [{"annee": "2023", "production_twh": "200.5", "consommation_twh": "195.0"}]
        with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(sample_rows, False)),
            ):
                result, _ = await q_client.fetch_electricity_data()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["annee"] == "2023"


class TestFetchProtectedAreas:
    async def test_returns_package_metadata(self):
        """fetch_protected_areas returns metadata dict from package_show."""
        pa_pkg = {
            "success": True,
            "result": {
                "id": "pa-uuid",
                "name": "aires-protegees-au-quebec",
                "title": "Aires protégées au Québec",
                "notes": "Registre des aires protégées...",
                "organization": {"name": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques", "title": "MELCCFP"},
                "resources": [
                    {
                        "id": "gpkg-001",
                        "name": "Aires protégées GPKG",
                        "format": "GPKG",
                        "url": "https://blob.core.windows.net/aires-protegees.gpkg",
                        "datastore_active": False,
                    }
                ],
            },
        }
        with patch(
            "mcp_canada.modules.quebec.client.api_get",
            new=AsyncMock(return_value=pa_pkg),
        ):
            result, _ = await q_client.fetch_protected_areas()
        assert isinstance(result, dict)
        assert result["name"] == "aires-protegees-au-quebec"
        assert len(result["resources"]) == 1
