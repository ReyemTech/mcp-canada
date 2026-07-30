"""Unit tests for new_brunswick/tools.py.

TestNbGetCrownLandTools is the Task 1 tracer, fully tested. Plan 02 Task 2
implements + tests the five federal-CKAN discovery tools; Task 3 implements +
tests the two gnb.socrata.com tools (checkpoint option-a). Every remaining
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
from mcp_canada.modules.new_brunswick.tools import (
    nb_get_contaminated_sites,
    nb_get_crown_land,
    nb_get_dataset_details,
    nb_get_flood_hazard_areas,
    nb_get_geonb_service_layers,
    nb_get_historical_floods,
    nb_get_wetlands,
    nb_list_categories,
    nb_list_geonb_services,
    nb_list_organizations,
    nb_query_dataset,
    nb_query_geonb_layer,
    nb_query_gnb_socrata_dataset,
    nb_search_datasets,
    nb_search_gnb_socrata_datasets,
)
from mcp_canada.shared.errors import InvalidInput, NotFound


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
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"results": [{"id": "x"}], "total": 221}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_search_datasets", mock_fetch
        )

        result = await nb_search_datasets(query="flood", limit=5)

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-federal-ckan"
        assert result["data"]["total"] == 221
        assert result["data"]["limit"] == 5
        assert result["data"]["offset"] == 0

    def test_no_organization_parameter_in_signature(self):
        import inspect

        sig = inspect.signature(nb_search_datasets)
        assert "organization" not in sig.parameters
        assert set(sig.parameters) == {"query", "extra_fq", "limit", "offset", "lang"}

    @pytest.mark.asyncio
    async def test_lang_fr_sets_meta_lang(self, monkeypatch):
        payload = {"results": [], "total": 0}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_search_datasets", mock_fetch
        )

        result = await nb_search_datasets(lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope_not_exception(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_search_datasets", mock_fetch
        )

        result = await nb_search_datasets(query="flood")

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbGetDatasetDetails:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"id": "x", "title": "T"}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_dataset_details", mock_fetch
        )

        result = await nb_get_dataset_details("x")

        assert "error" not in result
        assert result["data"]["id"] == "x"

    @pytest.mark.asyncio
    async def test_not_found_returns_not_found_with_suggestions(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=NotFound("NB dataset not found: bad-id"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_dataset_details", mock_fetch
        )
        mock_search = AsyncMock(
            return_value=({"results": [{"name": "good-id"}], "total": 1}, False)
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_search_datasets", mock_search
        )

        result = await nb_get_dataset_details("bad-id")

        assert result["error"]["code"] == "NOT_FOUND"
        assert "suggestions" in result["error"]

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_dataset_details", mock_fetch
        )

        result = await nb_get_dataset_details("x")

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbQueryDataset:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"rows": [{"a": 1}], "resource": {"format": "CSV"}, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_query_dataset", mock_fetch
        )

        result = await nb_query_dataset("x", resource_index=0)

        assert "error" not in result
        assert result["data"]["rows"] == [{"a": 1}]

    @pytest.mark.asyncio
    async def test_pdf_resource_returns_success_with_note_not_error(self, monkeypatch):
        payload = {
            "rows": [],
            "resource": {"format": "PDF", "url": "https://example.com/x.pdf"},
            "note": "Format 'PDF' is not machine-parseable by this server — download directly from https://example.com/x.pdf",
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_query_dataset", mock_fetch
        )

        result = await nb_query_dataset("x", resource_index=0)

        assert "error" not in result
        assert result["data"]["rows"] == []
        assert "note" in result["data"]

    @pytest.mark.asyncio
    async def test_out_of_range_resource_index_returns_invalid_input_with_range(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(side_effect=InvalidInput("resource_index 9 out of range"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_query_dataset", mock_fetch
        )
        mock_details = AsyncMock(
            return_value=({"resources": [{"format": "CSV"}]}, False)
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_dataset_details", mock_details
        )

        result = await nb_query_dataset("x", resource_index=9)

        assert result["error"]["code"] == "INVALID_INPUT"
        assert "valid_range" in result["error"]


class TestNbListOrganizations:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        orgs = [{"name": "Government of New Brunswick", "dataset_count": 221}]
        mock_fetch = AsyncMock(return_value=(orgs, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_organizations", mock_fetch
        )

        result = await nb_list_organizations()

        assert "error" not in result
        assert result["data"]["organizations"] == orgs

    @pytest.mark.asyncio
    async def test_http_status_error_returns_upstream_error_envelope(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://open.canada.ca"),
            response=httpx.Response(500),
        )
        mock_fetch = AsyncMock(side_effect=error)
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_organizations", mock_fetch
        )

        result = await nb_list_organizations()

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbListCategories:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"subjects": [{"name": "environment", "count": 120}], "topics": [], "formats": []}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_categories", mock_fetch
        )

        result = await nb_list_categories(lang="fr")

        assert "error" not in result
        assert result["_meta"]["lang"] == "fr"
        assert result["data"]["subjects"][0]["name"] == "environment"

    @pytest.mark.asyncio
    async def test_key_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=KeyError("facets"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_categories", mock_fetch
        )

        result = await nb_list_categories()

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbSearchGnbSocrataDatasets:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"results": [{"id": "4zbh-z2ij"}], "total": 312}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_gnb_socrata_search", mock_fetch
        )

        result = await nb_search_gnb_socrata_datasets(query="childcare")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-gnb-socrata"
        assert result["data"]["total"] == 312

    @pytest.mark.asyncio
    async def test_upstream_error_returns_envelope_not_exception(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.HTTPError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_gnb_socrata_search", mock_fetch
        )

        result = await nb_search_gnb_socrata_datasets()

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbQueryGnbSocrataDataset:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"rows": [{"facility_name": "Sunshine Daycare"}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_gnb_socrata_query", mock_fetch
        )

        result = await nb_query_gnb_socrata_dataset("4zbh-z2ij")

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_limit_above_cap_returns_invalid_input(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=InvalidInput("limit must be at most 5000"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_gnb_socrata_query", mock_fetch
        )

        result = await nb_query_gnb_socrata_dataset("4zbh-z2ij", limit=999999)

        assert result["error"]["code"] == "INVALID_INPUT"


class TestNbListGeonbServices:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        services = [
            {"name": "GeoNB_DNR_Crown_Land", "type": "MapServer", "department": "DNR", "curated_tool": "nb_get_crown_land"},
        ]
        mock_fetch = AsyncMock(return_value=(services, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_services", mock_fetch
        )

        result = await nb_list_geonb_services()

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"
        assert result["data"]["count"] == 1
        assert result["data"]["services"] == services

    @pytest.mark.asyncio
    async def test_no_hub_search_api_documented_in_docstring(self):
        assert "Hub" in (nb_list_geonb_services.__doc__ or "")
        assert "401" in (nb_list_geonb_services.__doc__ or "")

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_services", mock_fetch
        )

        result = await nb_list_geonb_services()

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbGetGeonbServiceLayers:
    @pytest.mark.asyncio
    async def test_happy_path_layer_id_three(self, monkeypatch):
        payload = {
            "layers": [{"id": 3, "name": "Crown Land", "record_count": 10001, "fields": ["HOLDER"]}],
            "tables": [],
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_service_layers",
            mock_fetch,
        )

        result = await nb_get_geonb_service_layers(service_name="GeoNB_DNR_Crown_Land")

        assert "error" not in result
        assert any(layer["id"] == 3 for layer in result["data"]["layers"])

    @pytest.mark.asyncio
    async def test_layer_ids_not_guessable_documented_with_worked_example(self):
        doc = nb_get_geonb_service_layers.__doc__ or ""
        assert "not" in doc.lower() and "guessable" in doc.lower()
        assert "Crown_Land" in doc

    @pytest.mark.asyncio
    async def test_unknown_service_returns_not_found(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=NotFound("GeoNB service not found: 'Bogus'"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_service_layers",
            mock_fetch,
        )

        result = await nb_get_geonb_service_layers(service_name="Bogus")

        assert result["error"]["code"] == "NOT_FOUND"


class TestNbQueryGeonbLayer:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"features": [{"NAME": "Mount Carleton"}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_layer_features",
            mock_fetch,
        )

        result = await nb_query_geonb_layer(
            service_name="GeoNB_DNR_ProvincialParks", layer_id=0
        )

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_where_passed_through_unchanged(self, monkeypatch):
        payload = {"features": [], "count": 0, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_layer_features",
            mock_fetch,
        )

        await nb_query_geonb_layer(
            service_name="GeoNB_DNR_ProvincialParks", layer_id=0, where="NAME='Mount Carleton'"
        )

        assert mock_fetch.call_args.kwargs["where"] == "NAME='Mount Carleton'"

    @pytest.mark.asyncio
    async def test_sql92_trust_boundary_documented_in_docstring(self):
        doc = nb_query_geonb_layer.__doc__ or ""
        assert "SQL-92" in doc

    @pytest.mark.asyncio
    async def test_unknown_service_returns_not_found(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=NotFound("GeoNB service not found: 'Bogus'"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_layer_features",
            mock_fetch,
        )

        result = await nb_query_geonb_layer(service_name="Bogus", layer_id=0)

        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_limit_above_cap_returns_invalid_input(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=InvalidInput("limit must be at most 5000"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_geonb_layer_features",
            mock_fetch,
        )

        result = await nb_query_geonb_layer(
            service_name="GeoNB_DNR_Crown_Land", layer_id=3, limit=999999
        )

        assert result["error"]["code"] == "INVALID_INPUT"


class TestNbGetFloodHazardAreas:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {
            "features": [{"Sheet_Numb": "21G01", "Flood_Haza": "High"}],
            "count": 1,
            "truncated": False,
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_flood_hazard_areas",
            mock_fetch,
        )

        result = await nb_get_flood_hazard_areas(limit=50, lang="en")

        assert "error" not in result
        assert result["data"]["count"] == 1
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"

    @pytest.mark.asyncio
    async def test_sheet_parameter_passed_through(self, monkeypatch):
        mock_fetch = AsyncMock(return_value=({"features": [], "count": 0, "truncated": False}, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_flood_hazard_areas",
            mock_fetch,
        )

        await nb_get_flood_hazard_areas(sheet="21G01")

        mock_fetch.assert_awaited_once_with(sheet="21G01", limit=MAX_RECORDS)

    @pytest.mark.asyncio
    async def test_empty_result_is_success_not_error(self, monkeypatch):
        mock_fetch = AsyncMock(return_value=({"features": [], "count": 0, "truncated": False}, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_flood_hazard_areas",
            mock_fetch,
        )

        result = await nb_get_flood_hazard_areas(sheet="99Z99")

        assert "error" not in result
        assert result["data"]["count"] == 0


class TestNbGetHistoricalFloods:
    @pytest.mark.asyncio
    async def test_happy_path_envelope_fr_lang(self, monkeypatch):
        payload = {"features": [{"ID": "x"}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_historical_floods",
            mock_fetch,
        )

        result = await nb_get_historical_floods(limit=50, lang="fr")

        assert "error" not in result
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_1973_event_dispatches_through(self, monkeypatch):
        mock_fetch = AsyncMock(return_value=({"features": [], "count": 0, "truncated": False}, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_historical_floods",
            mock_fetch,
        )

        await nb_get_historical_floods(event="1973")

        mock_fetch.assert_awaited_once_with(event="1973", limit=MAX_RECORDS)

    @pytest.mark.asyncio
    async def test_invalid_event_returns_invalid_input_pre_check(self, monkeypatch):
        mock_fetch = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_historical_floods",
            mock_fetch,
        )

        result = await nb_get_historical_floods(event="1950")

        assert result["error"]["code"] == "INVALID_INPUT"
        assert "1973" in str(result["error"]["valid"])
        mock_fetch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        # event="1973" passes the tool's own pre-check; the client still
        # raises — proves the second line of defence (double-guard) fires.
        mock_fetch = AsyncMock(side_effect=InvalidInput("event must be one of ['1973', '2008', '2018']"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_historical_floods",
            mock_fetch,
        )

        result = await nb_get_historical_floods(event="1973")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()


class TestNbGetWetlands:
    @pytest.mark.asyncio
    async def test_unfiltered_call_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_wetlands(lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalid_input_message_names_record_count_and_filters(self):
        result = await nb_get_wetlands(lang="en")

        assert "163,206" in result["error"]["message"]
        assert result["error"]["valid"] == ["wetland_class", "status"]

    @pytest.mark.asyncio
    async def test_wetland_class_filter_returns_features(self, monkeypatch):
        payload = {"features": [{"WETLAND_CLASS": "Bog"}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_wetlands", mock_fetch
        )

        result = await nb_get_wetlands(wetland_class="Bog")

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        # wetland_class="Bog" passes the tool's own pre-check; the client
        # still raises — proves the second line of defence (double-guard) fires.
        mock_fetch = AsyncMock(side_effect=InvalidInput("nb_get_wetlands requires at least one filter"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_wetlands", mock_fetch
        )

        result = await nb_get_wetlands(wetland_class="Bog")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()


class TestNbGetContaminatedSites:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {
            "features": [{"Status_E": "Active", "Status_F": "Actif"}],
            "count": 1,
            "truncated": False,
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_contaminated_sites",
            mock_fetch,
        )

        result = await nb_get_contaminated_sites(limit=50, lang="en")

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_bilingual_status_documented_in_docstring(self):
        doc = nb_get_contaminated_sites.__doc__ or ""
        assert "Status_E" in doc and "Status_F" in doc

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_contaminated_sites",
            mock_fetch,
        )

        result = await nb_get_contaminated_sites()

        assert result["error"]["code"] == "UPSTREAM_ERROR"


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
