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
    """Tests for fetch_road_conditions — updated with REAL live CSV header fixture (16-06).

    The MTQ conditions_routieres CSV uses PascalCase headers (NumeroSegment, NumeroRoute…).
    _parse_csv normalizes them to snake_case via _normalize_key (e.g. 'numerosegment').
    The mapper MUST use the normalized keys — old tests used synthetic PascalCase rows
    that masked the bug (both fixture and mapper were wrong in the same direction).
    """

    async def test_parses_conditions_csv_with_real_headers(self):
        """Real normalized keys from live MTQ CSV — segment_id/route_num must be non-null."""
        # These rows mirror what _parse_csv returns after applying _normalize_key
        # to the real live CSV headers (PascalCase -> lowercase, accents stripped)
        sample_rows = [
            {
                "numerosegment": "3201",
                "numeroroute": "117",
                "nomroute": "route 117",
                "nomregion": "abitibi-temiscamingue",
                "descriptionetatchausseeen": "Bare and Dry",
                "descriptionetatchausseefr": "Degagee et seche",
                "descriptionvisibiliteen": "Good",
                "descriptionvisibilitefr": "Bonne",
                "indicateurpresencelamesneige": "N",
                "envigueurdepuis": "2026/04/11 05:02:04",
            }
        ]
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_rows, False)),
        ):
            result, _ = await q_client.fetch_road_conditions(lang="en")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["segment_id"] == "3201", "segment_id was None — mapper uses wrong key"
        assert result[0]["route_num"] == "117", "route_num was None — mapper uses wrong key"
        assert result[0]["region"] == "abitibi-temiscamingue"
        assert result[0]["pavement_status"] == "Bare and Dry"
        assert result[0]["timestamp"] == "2026/04/11 05:02:04"

    async def test_bilingual_column_fr(self):
        sample_rows = [
            {
                "numerosegment": "3201",
                "numeroroute": "117",
                "nomroute": "route 117",
                "nomregion": "abitibi-temiscamingue",
                "descriptionetatchausseeen": "Bare and Dry",
                "descriptionetatchausseefr": "Degagee et seche",
                "descriptionvisibiliteen": "Good",
                "descriptionvisibilitefr": "Bonne",
                "indicateurpresencelamesneige": "N",
                "envigueurdepuis": "2026/04/11 05:02:04",
            }
        ]
        with patch(
            "mcp_canada.modules.quebec.client.fetch_and_parse",
            new=AsyncMock(return_value=(sample_rows, False)),
        ):
            result, _ = await q_client.fetch_road_conditions(lang="fr")
        assert result[0]["pavement_status"] == "Degagee et seche"
        assert result[0]["visibility"] == "Bonne"

    async def test_timestamp_maps_to_envigueurdepuis(self):
        """timestamp field must map to 'envigueurdepuis', NOT the non-existent 'DateEtHeureCondition'."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        sample_rows = [
            {
                "numerosegment": "9999",
                "numeroroute": "20",
                "nomroute": "autoroute 20",
                "nomregion": "monteregie",
                "descriptionetatchausseeen": "Wet",
                "descriptionetatchausseefr": "Mouille",
                "descriptionvisibiliteen": "Good",
                "descriptionvisibilitefr": "Bonne",
                "indicateurpresencelamesneige": "N",
                "envigueurdepuis": "2026/01/15 12:00:00",
            }
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(sample_rows, False)),
            ):
                result, _ = await q_client.fetch_road_conditions(lang="en")
        assert result[0]["timestamp"] == "2026/01/15 12:00:00", (
            "timestamp must map to 'envigueurdepuis', not 'DateEtHeureCondition' (column doesn't exist)"
        )

    async def test_returns_empty_on_parse_error(self):
        # NOTE: This test is updated as part of phase 16-05 gap closure.
        # The old contract (return [] on error) was a bug — errors should propagate.
        # This test now asserts that exceptions are NOT swallowed.
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(side_effect=Exception("WFS endpoint down")),
            ):
                with pytest.raises(Exception, match="WFS endpoint down"):
                    await q_client.fetch_road_conditions()

    async def test_propagates_parser_exceptions_no_silent_swallow(self) -> None:
        """fetch_road_conditions must raise parser exceptions — gap 16-02 regression.

        Before the fix, client.py:502-505 caught Exception and returned [], masking
        the real BadZipFile error from fetch_and_parse. The fix removes the try/except
        so errors propagate to the @tool layer where they become structured UPSTREAM_ERROR.
        """
        import zipfile
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(side_effect=zipfile.BadZipFile("File is not a zip file")),
            ):
                with pytest.raises(zipfile.BadZipFile):
                    await q_client.fetch_road_conditions(lang="en")


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
        # 16-07: _flatten_bridge normalizes route_num via _normalize_route so
        # the emitted value matches the filter normalization. "10" -> "00010".
        assert result[0].route_num == "00010"
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


class TestFetchBridgeStructuresPaging:
    """Tests for WFS paging loop and route normalizer (16-06 gap closure)."""

    async def test_paging_collects_all_rows(self):
        """Paging loop: page 1 returns PAGE_SIZE rows (fetch more), page 2 returns less (stop)."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        # Page 1: 500 rows with no A-20 (use num_route "00999")
        page1_rows = [
            {
                "ide_strct": f"S-{i}", "num_dossr": str(i), "val_annee_": "2000",
                "code_des_s": "Bon", "nom_route": "Route 999", "nom_obstc": "Riviere",
                "nom_muncp": "Ville", "cod_muncp": "12345", "nom_strct": f"Pont {i}",
                "num_route": "00999", "geo_lattd": "45.0", "geo_longt": "-72.0",
                "val_longr": "10.0", "val_largr_": "5.0", "cod_type_s": "Pont",
            }
            for i in range(500)
        ]
        # Page 2: 3 rows with A-20
        page2_rows = [
            {
                "ide_strct": "S-A20-1", "num_dossr": "9001", "val_annee_": "1985",
                "code_des_s": "Bon", "nom_route": "Autoroute 20 Ouest", "nom_obstc": "Riviere",
                "nom_muncp": "Saint-Hyacinthe", "cod_muncp": "47017", "nom_strct": "Pont A-20",
                "num_route": "00020", "geo_lattd": "45.5", "geo_longt": "-73.0",
                "val_longr": "42.5", "val_largr_": "12.0", "cod_type_s": "Pont",
            },
            {
                "ide_strct": "S-A20-2", "num_dossr": "9002", "val_annee_": "1990",
                "code_des_s": "Bon", "nom_route": "Autoroute 20 Est", "nom_obstc": "Canal",
                "nom_muncp": "Vaudreuil-Dorion", "cod_muncp": "71095", "nom_strct": "Pont A-20 Est",
                "num_route": "00020", "geo_lattd": "45.4", "geo_longt": "-74.0",
                "val_longr": "55.0", "val_largr_": "12.0", "cod_type_s": "Pont",
            },
            {
                "ide_strct": "S-A20-3", "num_dossr": "9003", "val_annee_": "2000",
                "code_des_s": "Bon", "nom_route": "Autoroute 20", "nom_obstc": "Riviere B",
                "nom_muncp": "Dorval", "cod_muncp": "06030", "nom_strct": "Pont A-20 Dorval",
                "num_route": "00020", "geo_lattd": "45.4", "geo_longt": "-73.8",
                "val_longr": "30.0", "val_largr_": "10.0", "cod_type_s": "Pont",
            },
        ]

        call_count = 0

        async def fake_fetch_and_parse(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "startIndex=0" in url:
                return page1_rows, False
            elif "startIndex=500" in url:
                return page2_rows, False
            return [], False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(route="A-20", limit=100)

        # Must have fetched both pages
        assert call_count == 2
        # Must have filtered to only A-20 rows
        assert len(result) == 3
        assert all(r.route_num == "00020" for r in result)

    async def test_route_normalizer_a20_maps_to_zero_padded(self):
        """route='A-20' normalizes to '00020' and matches num_route='00020'."""
        from mcp_canada.modules.quebec.client import _normalize_route

        assert _normalize_route("A-20") == "00020"
        assert _normalize_route("Autoroute 20") == "00020"
        assert _normalize_route("autoroute 20") == "00020"
        assert _normalize_route("20") == "00020"

    async def test_route_normalizer_132_formats(self):
        """route='Route 132', '132', '00132' all normalize to '00132'."""
        from mcp_canada.modules.quebec.client import _normalize_route

        assert _normalize_route("Route 132") == "00132"
        assert _normalize_route("132") == "00132"
        assert _normalize_route("00132") == "00132"

    async def test_paging_stops_when_page_smaller_than_count(self):
        """Loop terminates when page returns fewer rows than PAGE_SIZE."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        call_count = 0

        async def fake_fetch_and_parse(url, **kwargs):
            nonlocal call_count
            call_count += 1
            # First page returns 10 rows (< PAGE_SIZE=500) — loop should stop
            return [
                {
                    "ide_strct": f"S-{i}", "num_dossr": str(i), "val_annee_": "2000",
                    "code_des_s": "Bon", "nom_route": "Route 132", "nom_obstc": "Mer",
                    "nom_muncp": "Rimouski", "cod_muncp": "97047", "nom_strct": f"Pont {i}",
                    "num_route": "00132", "geo_lattd": "48.0", "geo_longt": "-68.5",
                    "val_longr": "20.0", "val_largr_": "8.0", "cod_type_s": "Pont",
                }
                for i in range(10)
            ], False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(route="132", limit=100)

        # Only one page fetched (10 < 500 = stop)
        assert call_count == 1
        assert len(result) == 10

    async def test_municipality_filter_regression_with_paging(self):
        """Municipality filter still works after paging collects all rows."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        rows = [
            {
                "ide_strct": "S-1", "num_dossr": "1", "val_annee_": "2000",
                "code_des_s": "Bon", "nom_route": "Route 132", "nom_obstc": "Mer",
                "nom_muncp": "Granby", "cod_muncp": "47017", "nom_strct": "Pont 1",
                "num_route": "00132", "geo_lattd": "45.0", "geo_longt": "-72.0",
                "val_longr": "10.0", "val_largr_": "5.0", "cod_type_s": "Pont",
            },
            {
                "ide_strct": "S-2", "num_dossr": "2", "val_annee_": "2000",
                "code_des_s": "Bon", "nom_route": "Route 132", "nom_obstc": "Mer",
                "nom_muncp": "Rimouski", "cod_muncp": "97047", "nom_strct": "Pont 2",
                "num_route": "00132", "geo_lattd": "48.0", "geo_longt": "-68.5",
                "val_longr": "20.0", "val_largr_": "8.0", "cod_type_s": "Pont",
            },
        ]

        async def fake_fetch_and_parse(url, **kwargs):
            return rows, False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(municipality="Granby")

        assert len(result) == 1
        assert result[0].municipality == "Granby"


class TestQuebecBridgeStructuresTypeCoercion:
    """Tests for 16-07 gap closure: int→str coercion in _flatten_bridge.

    Background: shared/parsers.py:_mask_privacy auto-coerces digit-only CSV cells
    to int (e.g. "00020" -> 20, "200645" -> 200645). QuebecBridgeStructure
    declares structure_id/dossier_num/municipality_code/route_num/structure_type
    as `str | None`. Pydantic v2 does NOT coerce int -> str, so every row fails
    validation. Fix: stringify in the Quebec mapper only (no shared parser edit).
    """

    async def test_int_csv_values_produce_string_schema_fields(self) -> None:
        """Fixture simulates _parse_csv+_mask_privacy output with int ID cells.

        Every str-typed ID field on the Pydantic model must end up a string
        after _flatten_bridge runs. Must FAIL before the mapper fix.
        """
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        # Values match what _parse_csv + _mask_privacy produces on the live bridge CSV:
        # ide_strct / num_dossr / cod_muncp / num_route / cod_type_s all become int.
        page_rows = [
            {
                "ide_strct":  200645,              # int — post-_mask_privacy
                "num_dossr":  4116,                # int
                "val_annee_": 1985,                # int (year, schema already int — OK)
                "code_des_s": "Bon",               # str (alpha code)
                "nom_route":  "Autoroute 20 Ouest",
                "nom_obstc":  "Rivière",
                "nom_muncp":  "Saint-Hyacinthe",
                "cod_muncp":  17010,               # int
                "nom_strct":  "Pont A-20",
                "num_route":  20,                  # int — zero-padding lost
                "geo_lattd":  45.5,
                "geo_longt": -73.0,
                "val_longr":  42.5,
                "val_largr_": 12.0,
                "cod_type_s": 1,                   # int — post-_mask_privacy
            },
        ]

        async def fake_fetch_and_parse(url, **kwargs):
            return page_rows, False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(route="A-20", limit=10)

        assert len(result) == 1
        row = result[0]
        assert isinstance(row.structure_id, str) and row.structure_id == "200645"
        assert isinstance(row.dossier_num, str) and row.dossier_num == "4116"
        assert isinstance(row.municipality_code, str) and row.municipality_code == "17010"
        assert isinstance(row.route_num, str) and row.route_num == "00020"
        assert isinstance(row.structure_type, str) and row.structure_type == "1"

    async def test_float_integer_value_produces_string_without_decimal(self) -> None:
        """Defensive: if a CSV numeric cell is parsed as float whose value is an
        integer (e.g. 20.0), the mapper must emit '20' not '20.0'."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        page_rows = [
            {
                "ide_strct":  200645.0,            # float whole number
                "num_dossr":  4116,
                "val_annee_": 1985,
                "code_des_s": "Bon",
                "nom_route":  "Autoroute 20 Ouest",
                "nom_obstc":  "Rivière",
                "nom_muncp":  "Saint-Hyacinthe",
                "cod_muncp":  17010,
                "nom_strct":  "Pont A-20",
                "num_route":  20,
                "geo_lattd":  45.5,
                "geo_longt": -73.0,
                "val_longr":  42.5,
                "val_largr_": 12.0,
                "cod_type_s": 1,
            },
        ]

        async def fake_fetch_and_parse(url, **kwargs):
            return page_rows, False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(route="A-20", limit=10)

        assert len(result) == 1
        assert result[0].structure_id == "200645"


class TestQuebecBridgeStructuresIntFilter:
    """Regression: post-parse route filter must handle int num_route after _mask_privacy.

    Before fix 1B, the filter compared str(20) == "00020" (always false) and
    silently fell back to a nom_route substring match — brittle if nom_route
    lacks the raw digits.
    """

    async def test_int_num_route_matches_via_normalizer_roundtrip(self) -> None:
        """route='A-20' should match int num_route=20 via _normalize_route roundtrip,
        and reject int num_route=132 (raw_digits '20' is not a substring of nom_route)."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        page_rows = [
            {
                "ide_strct":  200645,
                "num_dossr":  4116,
                "val_annee_": 1985,
                "code_des_s": "Bon",
                # Note: nom_route intentionally contains NO digits so we know the
                # match came from num_route normalization, not the substring fallback.
                "nom_route":  "Autoroute Jean-Lesage",
                "nom_obstc":  "Rivière",
                "nom_muncp":  "Saint-Hyacinthe",
                "cod_muncp":  17010,
                "nom_strct":  "Pont Jean-Lesage",
                "num_route":  20,              # int — must be recognized as A-20
                "geo_lattd":  45.5,
                "geo_longt": -73.0,
                "val_longr":  42.5,
                "val_largr_": 12.0,
                "cod_type_s": 1,
            },
            {
                "ide_strct":  300001,
                "num_dossr":  5000,
                "val_annee_": 1990,
                "code_des_s": "Bon",
                # Same: nom_route with no digits, so no substring crutch.
                "nom_route":  "Route Rive-Sud",
                "nom_obstc":  "Fleuve",
                "nom_muncp":  "Levis",
                "cod_muncp":  25213,
                "nom_strct":  "Pont Rive-Sud",
                "num_route":  132,             # int — must NOT be returned for A-20
                "geo_lattd":  46.8,
                "geo_longt": -71.2,
                "val_longr":  100.0,
                "val_largr_": 15.0,
                "cod_type_s": 1,
            },
        ]

        async def fake_fetch_and_parse(url, **kwargs):
            return page_rows, False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                side_effect=fake_fetch_and_parse,
            ):
                result, _ = await q_client.fetch_bridge_structures(route="A-20", limit=10)

        assert len(result) == 1, (
            f"Expected only the A-20 row (num_route=20), got {len(result)}: {result}"
        )
        assert result[0].structure_id == "200645"
        assert result[0].route_num == "00020"


class TestQuebecPopulationIntCoercion:
    """Latent replicate-check: MAMH mcode is digit-only → int after _mask_privacy."""

    async def test_int_mcode_becomes_string(self) -> None:
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        fixture_rows = [
            {
                "mcode": 80005,          # int — post-_mask_privacy
                "munnom": "Montréal",
                "regadm": "06",
                "mrc": "Communauté métropolitaine",
                "mpopul": 1780000,
                "msuperf": 365.13,
                "mcodedesi": "Ville",
                "mayor": "Mayor Name",
            }
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(fixture_rows, False)),
            ):
                result, _ = await q_client.fetch_population_by_municipality()
        assert len(result) == 1
        assert isinstance(result[0].mcode, str)
        assert result[0].mcode == "80005"


class TestQuebecRoadWorkIntCoercion:
    """Latent replicate-check: MTQ chantiers identifiant / identifiantChantier int coercion."""

    async def test_int_identifiants_become_strings(self) -> None:
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        fixture_rows = [
            {
                "identifiant": 12345,                # int
                "identifiantChantier": 67890,        # int
                "routeAutoroute": "A-25",
                "entraveType": "Fermeture",
                "debut": "2026-04-10",
                "fin": "2026-04-15",
                "miseAJour": "2026-04-11 06:00",
                "identificationDesTravaux": "Réfection",
                "localisation": "km 8",
                "direction": "Nord",
                "descriptionFrancais": "Travaux routiers",
                "descriptionAnglais": "Road works",
            }
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(fixture_rows, False)),
            ):
                result, _ = await q_client.fetch_road_works(lang="en")
        assert len(result) == 1
        assert isinstance(result[0].identifier, str)
        assert result[0].identifier == "12345"
        assert isinstance(result[0].chantier_id, str)
        assert result[0].chantier_id == "67890"


class TestQuebecRoadEventIntCoercion:
    """Latent replicate-check: MTQ evenements identifiant int coercion."""

    async def test_int_identifiant_becomes_string(self) -> None:
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        fixture_rows = [
            {
                "identifiant": 202601,              # int — post-_mask_privacy
                "entrave": "Accident",
                "numeroRoute": "A-40",
                "localisation": "km 20",
                "direction": "Est",
                "municipalite": "Montréal",
                "duree": "2h",
                "cause": "Collision",
                "consequence": "Ralentissement",
                "detour": "Aucun",
                "regions": "Montréal",
                "enVigueurDepuis": "2026-04-11 08:00",
            }
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.fetch_and_parse",
                new=AsyncMock(return_value=(fixture_rows, False)),
            ):
                result, _ = await q_client.fetch_road_events()
        assert len(result) == 1
        assert isinstance(result[0].identifier, str)
        assert result[0].identifier == "202601"


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
    """Tests for fetch_electricity_data — updated for phase 16-05 3-tuple contract.

    The Hydro-Québec historique-production-consommation package publishes XLSX files
    (years 2018-2021), NOT CSV. The old CSV-only matcher never hit; fixed to accept
    CSV/XLSX/XLS. Return type changed from (rows, was_cached) to (rows, source_url, was_cached).
    """

    async def test_parses_hydro_quebec_csv(self):
        """fetch_electricity_data finds CSV resource then calls fetch_and_parse (3-tuple return)."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
        # 16-07: fetch_electricity_data now applies _is_real_electricity_row to
        # strip the XLSX legend row. Fixture rows must include the indexing
        # cells (rang/mois/jour/heure) so they pass the filter.
        sample_rows = [{
            "rang": 1, "mois": 1, "jour": 1, "heure": 1,
            "annee": "2023", "production_twh": "200.5", "consommation_twh": "195.0",
        }]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(sample_rows, False)),
                ):
                    rows, source_url, was_cached = await q_client.fetch_electricity_data()
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0]["annee"] == "2023"
        assert source_url == "https://hydroquebec.com/data/historique.csv"

    async def test_matches_xlsx_resource_when_no_csv_present(self) -> None:
        """Hydro-Québec package has ZERO CSV — must accept XLSX format resources."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
                        "id": "xlsx-2021",
                        "name": "Suivi 2021 XLSX",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2021.xlsx",
                        "datastore_active": False,
                    },
                    {
                        "id": "xlsx-2019",
                        "name": "Suivi 2019 XLSX",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2019.xlsx",
                        "datastore_active": False,
                    },
                ],
            },
        }
        # 16-07: include indexing cells so the row survives _is_real_electricity_row.
        sample_rows = [{
            "rang": 1, "mois": 1, "jour": 1, "heure": 1,
            "year": 2021, "production": 100,
        }]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(sample_rows, False)),
                ):
                    rows, source_url, was_cached = await q_client.fetch_electricity_data()
        assert len(rows) > 0
        assert source_url == "https://www.hydroquebec.com/data/suivi-2021.xlsx"
        assert was_cached is False

    async def test_skips_empty_url_resources(self) -> None:
        """Resources with url='' (real 2020 Hydro-Québec entry) must be skipped."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
                        "id": "xlsx-2020",
                        "name": "Suivi 2020 XLSX — empty URL",
                        "format": "XLSX",
                        "url": "",  # real 2020 entry has empty URL
                        "datastore_active": False,
                    },
                    {
                        "id": "xlsx-2019",
                        "name": "Suivi 2019 XLSX",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2019.xlsx",
                        "datastore_active": False,
                    },
                ],
            },
        }
        # 16-07: include indexing cells so the row survives _is_real_electricity_row.
        sample_rows = [{
            "rang": 1, "mois": 1, "jour": 1, "heure": 1,
            "year": 2019, "production": 90,
        }]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(sample_rows, False)),
                ):
                    rows, source_url, was_cached = await q_client.fetch_electricity_data()
        assert source_url == "https://www.hydroquebec.com/data/suivi-2019.xlsx"
        assert len(rows) > 0

    async def test_hydroquebec_url_gets_seclevel1_ssl_context(self) -> None:
        """fetch_electricity_data passes ssl_context with SECLEVEL=1 for hydroquebec.com URLs."""
        import ssl
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
                        "id": "xlsx-2021",
                        "name": "Suivi 2021",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2021.xlsx",
                        "datastore_active": False,
                    }
                ],
            },
        }
        captured_kwargs: dict = {}

        async def capture_fetch_and_parse(url, **kwargs):
            captured_kwargs.update(kwargs)
            return [{
                "rang": 1, "mois": 1, "jour": 1, "heure": 1,
                "year": 2021,
            }], False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    side_effect=capture_fetch_and_parse,
                ):
                    await q_client.fetch_electricity_data()

        assert "ssl_context" in captured_kwargs, (
            "fetch_and_parse must receive ssl_context kwarg for hydroquebec.com URLs"
        )
        ssl_ctx = captured_kwargs["ssl_context"]
        assert isinstance(ssl_ctx, ssl.SSLContext), (
            f"Expected ssl.SSLContext, got {type(ssl_ctx)}"
        )

    async def test_non_hydroquebec_url_gets_no_ssl_context(self) -> None:
        """Non-hydroquebec.com URLs get ssl_context=None — scoped fix only."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
                        "name": "Other XLSX",
                        "format": "XLSX",
                        "url": "https://example.com/data.xlsx",
                        "datastore_active": False,
                    }
                ],
            },
        }
        captured_kwargs: dict = {}

        async def capture_fetch_and_parse(url, **kwargs):
            captured_kwargs.update(kwargs)
            return [{
                "rang": 1, "mois": 1, "jour": 1, "heure": 1,
                "year": 2020,
            }], False

        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    side_effect=capture_fetch_and_parse,
                ):
                    await q_client.fetch_electricity_data()

        assert captured_kwargs.get("ssl_context") is None, (
            "Non-hydroquebec.com URLs must not get ssl_context (scoped fix only)"
        )

    async def test_raises_when_no_parseable_resource(self) -> None:
        """If all resources are SHP/GPKG (unparseable), raise ValueError — not silent empty."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

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
                        "id": "shp-001",
                        "name": "Shapefile",
                        "format": "SHP",
                        "url": "https://example.com/a.shp",
                        "datastore_active": False,
                    },
                    {
                        "id": "gpkg-001",
                        "name": "GeoPackage",
                        "format": "GPKG",
                        "url": "https://example.com/b.gpkg",
                        "datastore_active": False,
                    },
                ],
            },
        }
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch("mcp_canada.modules.quebec.client.api_get", new=AsyncMock(return_value=hydro_pkg)):
                with pytest.raises(ValueError, match="No parseable"):
                    await q_client.fetch_electricity_data(limit=100)

    async def test_skips_legend_formula_row(self) -> None:
        """Hydro-Québec XLSX legend/formula row (first data row) must be filtered out.

        The real Hydro-Québec historique XLSX files document column formulas
        in the FIRST row after the header: cells like '5=1-2+3+4', '7=5-6',
        '9=7-8', '13=11x12' with null indexing cells (rang/mois/jour/heure).
        Phase 16-07 adds _is_real_electricity_row to strip this row so that
        data[0] is always real data. Must FAIL before the filter exists.
        """
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        hydro_pkg = {
            "success": True,
            "result": {
                "id": "hydro-uuid",
                "name": "historique-production-consommation",
                "title": "Historique",
                "notes": "",
                "organization": {"name": "hydro-quebec", "title": "Hydro-Québec"},
                "resources": [
                    {
                        "id": "xlsx-2021",
                        "name": "2021",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2021.xlsx",
                        "datastore_active": False,
                    },
                ],
            },
        }
        # Row 0 = legend (indexing cells None, formula strings in computed columns)
        # Row 1, 2 = real data
        mock_parsed_rows = [
            {
                "rang": None, "mois": None, "jour": None, "heure": None,
                "prod_1": None, "prod_2": None, "prod_3": None, "prod_4": None,
                "prod_5": "5=1-2+3+4", "cons_6": None, "cons_7": "7=5-6",
                "cons_8": None, "cons_9": "9=7-8", "cons_13": "13=11x12",
            },
            {
                "rang": 1, "mois": 1, "jour": 1, "heure": 1,
                "prod_1": 21065.13, "prod_2": 0.0, "prod_3": 0.0, "prod_4": 0.0,
                "prod_5": 21065.13, "cons_6": 1200.0, "cons_7": 19865.13,
                "cons_8": 0.0, "cons_9": 19865.13, "cons_13": 4000.0,
            },
            {
                "rang": 2, "mois": 1, "jour": 1, "heure": 2,
                "prod_1": 20500.0, "prod_2": 0.0, "prod_3": 0.0, "prod_4": 0.0,
                "prod_5": 20500.0, "cons_6": 1150.0, "cons_7": 19350.0,
                "cons_8": 0.0, "cons_9": 19350.0, "cons_13": 3900.0,
            },
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.api_get",
                new=AsyncMock(return_value=hydro_pkg),
            ):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(mock_parsed_rows, False)),
                ):
                    rows, source_url, was_cached = await q_client.fetch_electricity_data()
        assert len(rows) == 2, (
            f"Expected 2 real rows (legend stripped), got {len(rows)}: {rows}"
        )
        assert rows[0]["rang"] == 1, (
            f"First row should be real data (rang=1), got: {rows[0]}"
        )
        assert rows[1]["rang"] == 2
        # No formula strings in any returned cell
        for row in rows:
            for v in row.values():
                assert not (
                    isinstance(v, str) and "=" in v and any(ch.isdigit() for ch in v)
                ), f"Formula string leaked through filter: {row}"

    async def test_skips_row_with_null_indexing_cell(self) -> None:
        """Defensive: rows with any null indexing cell are filtered, not just legend.

        This protects against other sparse/fill-blank rows that may appear in
        future Hydro-Québec XLSX revisions.
        """
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        hydro_pkg = {
            "success": True,
            "result": {
                "id": "hydro-uuid",
                "name": "historique-production-consommation",
                "title": "Historique",
                "notes": "",
                "organization": {"name": "hydro-quebec", "title": "Hydro-Québec"},
                "resources": [
                    {
                        "id": "xlsx-2021",
                        "name": "2021",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2021.xlsx",
                        "datastore_active": False,
                    },
                ],
            },
        }
        mock_parsed_rows = [
            {"rang": None, "mois": 1, "jour": 1, "heure": 1, "prod_1": 100.0},
            {"rang": 1, "mois": 1, "jour": 1, "heure": 1, "prod_1": 200.0},
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.api_get",
                new=AsyncMock(return_value=hydro_pkg),
            ):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(mock_parsed_rows, False)),
                ):
                    rows, _source, _cached = await q_client.fetch_electricity_data()
        assert len(rows) == 1
        assert rows[0]["rang"] == 1
        assert rows[0]["prod_1"] == 200.0

    async def test_keeps_real_row_with_populated_indexing_cells(self) -> None:
        """Rows with all four indexing cells populated AND no formula strings are kept."""
        import mcp_canada.modules.quebec.client as _mod

        async def passthrough(key, ttl, fetcher):
            return (await fetcher(), False)

        hydro_pkg = {
            "success": True,
            "result": {
                "id": "hydro-uuid",
                "name": "historique-production-consommation",
                "title": "Historique",
                "notes": "",
                "organization": {"name": "hydro-quebec", "title": "Hydro-Québec"},
                "resources": [
                    {
                        "id": "xlsx-2021",
                        "name": "2021",
                        "format": "XLSX",
                        "url": "https://www.hydroquebec.com/data/suivi-2021.xlsx",
                        "datastore_active": False,
                    },
                ],
            },
        }
        mock_parsed_rows = [
            {
                "rang": 1, "mois": 1, "jour": 1, "heure": 1,
                "production_brute": 20000.0, "consommation": 19000.0,
            },
        ]
        with patch.object(_mod, "cached_fetch", side_effect=passthrough):
            with patch(
                "mcp_canada.modules.quebec.client.api_get",
                new=AsyncMock(return_value=hydro_pkg),
            ):
                with patch(
                    "mcp_canada.modules.quebec.client.fetch_and_parse",
                    new=AsyncMock(return_value=(mock_parsed_rows, False)),
                ):
                    rows, _source, _cached = await q_client.fetch_electricity_data()
        assert len(rows) == 1
        assert rows[0]["rang"] == 1
        assert rows[0]["production_brute"] == 20000.0


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
