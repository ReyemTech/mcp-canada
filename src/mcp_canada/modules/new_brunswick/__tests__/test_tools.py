"""Unit tests for new_brunswick/tools.py.

TestNbGetCrownLandTools is the Task 1 tracer, fully tested. Plan 02 Task 2
implements + tests the five federal-CKAN discovery tools; Task 3 implements +
tests the two gnb.socrata.com tools (checkpoint option-a). Plan 05 implements
+ tests nb_get_parcels / nb_get_civic_addresses — the two FILTER_REQUIRED_TOOLS
large layers, each proven via a not-awaited guard test. Plan 06 implements +
tests nb_get_health_facilities / nb_get_public_schools (the two dispatch
tools) and nb_get_road_events / nb_get_winter_road_conditions /
nb_get_traffic_cameras (the three key-gated 511 tools), plus
TestManifestMatchesShippedSurface — a genuine, falsifiable bidirectional
set-equality check between constants.ALL_NB_TOOL_NAMES and the @tool objects
actually registered in this module (an orchestrator-directed addition; see
21-06-SUMMARY.md). TestNbEnvelopes / TestNbLangParam are parametrized by
Plan 07 once every tool exists.
"""

from __future__ import annotations

import json
import re
from unittest.mock import AsyncMock

import httpx
import pytest

import mcp_canada.modules.new_brunswick.tools as nb_tools
from mcp_canada.modules.new_brunswick.client import Five11NotConfigured
from mcp_canada.modules.new_brunswick.constants import (
    ALL_NB_TOOL_NAMES,
    CROWN_LAND_SERVICE,
    HEALTH_FACILITY_LAYERS,
    MAX_RECORDS,
    SCHOOL_SECTOR_LAYERS,
)
from mcp_canada.modules.new_brunswick.tools import (
    nb_get_civic_addresses,
    nb_get_contaminated_sites,
    nb_get_crown_land,
    nb_get_dataset_details,
    nb_get_flood_hazard_areas,
    nb_get_geonb_service_layers,
    nb_get_health_facilities,
    nb_get_historical_floods,
    nb_get_parcels,
    nb_get_public_schools,
    nb_get_road_events,
    nb_get_traffic_cameras,
    nb_get_wetlands,
    nb_get_winter_road_conditions,
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

# WR-04: `nb_` followed by one or more lowercase-alphanumeric snake_case
# segments — rejects double underscores, missing separators, uppercase, and
# a trailing/dangling underscore, none of which a bare `.startswith("nb_")`
# would catch.
_NB_TOOL_NAME_RE = re.compile(r"nb_[a-z0-9]+(?:_[a-z0-9]+)*")


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
        # WR-04: a bare `.startswith("nb_")` would also accept "nb__get_x"
        # (double underscore) or other typo-adjacent malformed names — the
        # full pattern enforces `nb_` followed by lowercase snake_case
        # segments, matching the module-prefix convention documented in
        # .claude/rules/modules.md.
        for name in ALL_NB_TOOL_NAMES:
            assert _NB_TOOL_NAME_RE.fullmatch(name), name

    @pytest.mark.parametrize(
        "bad_name",
        [
            "nb__get_x",  # double underscore
            "nbget_x",  # missing separator after prefix
            "nb_Get_X",  # uppercase
            "nb_get_x_",  # trailing underscore
            "nb_",  # prefix alone, no segment
            "on_get_x",  # wrong prefix entirely
        ],
    )
    def test_prefix_pattern_rejects_malformed_names(self, bad_name):
        # Proves the strengthened check in the test above is actually
        # falsifiable — a bare `.startswith("nb_")` would have let every one
        # of these through.
        assert not _NB_TOOL_NAME_RE.fullmatch(bad_name), bad_name


class TestManifestMatchesShippedSurface:
    """Orchestrator-directed addition (not in the original plan text): the
    manifest count/membership/prefix checks above are all necessary but not
    sufficient — none of them proves a manifest name resolves to a real,
    registered tool. `ALL_NB_TOOLS = ALL_NB_TOOL_NAMES` in tools.py is an
    alias, not an independent value, so an equality assertion against it is
    unfalsifiable (an alias can never differ from what it aliases). These
    tests instead inspect the module's live attributes directly, in both
    directions:

      1. every name in the locked manifest resolves to a callable @tool
         object in this module (not merely `hasattr` — but `__fastmcp__`
         proof it went through the @tool decorator);
      2. no nb_-prefixed @tool exists in this module OUTSIDE the manifest
         (the direction membership tests above cannot catch — a stray
         nb_get_* tool added without a matching manifest entry would pass
         every existing check while still drifting from D-08/D-25's single
         authoritative manifest).
    """

    def test_every_manifest_name_resolves_to_a_registered_tool(self):
        for name in ALL_NB_TOOL_NAMES:
            obj = getattr(nb_tools, name, None)
            assert obj is not None, (
                f"{name!r} is in constants.ALL_NB_TOOL_NAMES but tools.py has "
                "no attribute of that name"
            )
            assert callable(obj), f"{name!r} exists in tools.py but is not callable"
            assert getattr(obj, "__fastmcp__", None) is not None, (
                f"{name!r} exists in tools.py but was never decorated with @tool "
                "(no __fastmcp__ metadata)"
            )

    def test_no_nb_prefixed_tool_exists_outside_the_manifest(self):
        shipped = {
            name
            for name, obj in vars(nb_tools).items()
            if name.startswith("nb_") and getattr(obj, "__fastmcp__", None) is not None
        }
        assert shipped == set(ALL_NB_TOOL_NAMES), (
            f"tools.py and constants.ALL_NB_TOOL_NAMES disagree — "
            f"shipped-only: {shipped - set(ALL_NB_TOOL_NAMES)}, "
            f"manifest-only: {set(ALL_NB_TOOL_NAMES) - shipped}"
        )


# ---------------------------------------------------------------------------
# Placeholder classes — one per remaining tool (owning plan implements + tests)
# ---------------------------------------------------------------------------


class TestNbSearchDatasets:
    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {"results": [{"id": "x"}], "total": 221, "limit": 5, "offset": 0}
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

    @pytest.mark.asyncio
    async def test_echoes_clamped_limit_and_offset_not_raw_caller_values(self, monkeypatch):
        # WR-02: the client already clamps limit/offset before sending them
        # upstream — the tool must echo what the client actually clamped to
        # (carried in the payload), not its own raw, unclamped parameters.
        payload = {"results": [], "total": 0, "limit": 100, "offset": 0}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_search_datasets", mock_fetch
        )

        result = await nb_search_datasets(query="flood", limit=500, offset=-5)

        assert result["data"]["limit"] == 100
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

    @pytest.mark.asyncio
    async def test_negative_limit_returns_invalid_input_not_out_of_range_message(
        self, monkeypatch
    ):
        # WR-03: a negative-limit InvalidInput is a distinct failure from an
        # out-of-range resource_index — the tool must not mislabel it as
        # "Invalid resource index" (which would also trigger an unnecessary
        # fetch_dataset_details call to compute a meaningless valid_range).
        mock_fetch = AsyncMock(
            side_effect=InvalidInput("nb_query_dataset limit must be greater than 0, got -1")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_query_dataset", mock_fetch
        )
        mock_details = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_dataset_details", mock_details
        )

        result = await nb_query_dataset("x", resource_index=0, limit=-1)

        assert result["error"]["code"] == "INVALID_INPUT"
        assert "resource index" not in result["error"]["message"].lower()
        mock_details.assert_not_awaited()


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
    async def test_whitespace_only_filter_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        # CR-01: the tool-layer pre-check must agree with the client-layer
        # `_require_any_filter` — a whitespace-only value is not a real filter.
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_wetlands(wetland_class=" ", lang="en")

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
    @pytest.mark.asyncio
    async def test_unfiltered_call_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_parcels(lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_whitespace_only_county_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_parcels(county=" ", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalid_input_message_names_record_count_and_filters(self):
        result = await nb_get_parcels(lang="en")

        assert "604,520" in result["error"]["message"]
        assert result["error"]["valid"] == ["pid", "county"]

    @pytest.mark.asyncio
    async def test_pid_filter_returns_features(self, monkeypatch):
        payload = {
            "features": [
                {
                    "PID": "12345678",
                    "COUNTY": "York",
                    "Titles_Status": "Registered",
                    "Gazette_Status": "Published",
                }
            ],
            "count": 1,
            "truncated": False,
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_parcels", mock_fetch
        )

        result = await nb_get_parcels(pid="12345678", lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"
        assert result["data"]["count"] == 1
        mock_fetch.assert_awaited_once_with(pid="12345678", county=None, limit=MAX_RECORDS)

    @pytest.mark.asyncio
    async def test_county_filter_returns_features(self, monkeypatch):
        payload = {"features": [{"COUNTY": "York"}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_parcels", mock_fetch
        )

        result = await nb_get_parcels(county="York", lang="en")

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=InvalidInput("nb_get_parcels requires at least one filter")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_parcels", mock_fetch
        )

        result = await nb_get_parcels(pid="12345678", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_parcels", mock_fetch
        )

        result = await nb_get_parcels(pid="12345678", lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbGetCivicAddresses:
    @pytest.mark.asyncio
    async def test_unfiltered_call_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_civic_addresses(lang="fr")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_whitespace_only_community_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.client.arcgis_hub.query_feature_service",
            mock_query,
        )

        result = await nb_get_civic_addresses(community=" ", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalid_input_message_names_record_count_and_filters(self):
        result = await nb_get_civic_addresses(lang="en")

        assert "373,172" in result["error"]["message"]
        assert result["error"]["valid"] == ["community", "street", "civic_number"]

    @pytest.mark.asyncio
    async def test_community_filter_returns_address_points(
        self, monkeypatch, civic_address_geojson
    ):
        features = [f["properties"] for f in civic_address_geojson["features"]]
        payload = {"features": features, "count": len(features), "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_civic_addresses", mock_fetch
        )

        result = await nb_get_civic_addresses(community="Fredericton", lang="en")

        assert "error" not in result
        assert result["data"]["count"] == len(features)
        mock_fetch.assert_awaited_once_with(
            community="Fredericton", street=None, civic_number=None, limit=MAX_RECORDS
        )

    @pytest.mark.asyncio
    async def test_civic_number_filter_returns_envelope(self, monkeypatch):
        payload = {"features": [{"CIVIC_NUM": 160}], "count": 1, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_civic_addresses", mock_fetch
        )

        result = await nb_get_civic_addresses(civic_number=160, lang="en")

        assert "error" not in result
        assert result["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_features_carry_bilingual_street_type_fields(
        self, monkeypatch, civic_address_geojson
    ):
        features = [f["properties"] for f in civic_address_geojson["features"]]
        payload = {"features": features, "count": len(features), "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_civic_addresses", mock_fetch
        )

        result = await nb_get_civic_addresses(community="Fredericton", lang="en")

        feature = result["data"]["features"][0]
        assert feature["ST_TYPE_E"] == "St"
        assert feature["ST_TYPE_F"] == "Rue"

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=InvalidInput("nb_get_civic_addresses requires at least one filter")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_civic_addresses", mock_fetch
        )

        result = await nb_get_civic_addresses(community="Fredericton", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_civic_addresses", mock_fetch
        )

        result = await nb_get_civic_addresses(community="Fredericton", lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestNbGetHealthFacilities:
    @pytest.mark.asyncio
    async def test_invalid_facility_type_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_health_facilities",
            mock_fetch,
        )

        result = await nb_get_health_facilities(facility_type="not-a-real-type", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        assert result["error"]["valid"] == sorted(HEALTH_FACILITY_LAYERS)
        mock_fetch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        payload = {
            "features": [{"Name_E": "Dr. Everett Chalmers Regional Hospital"}],
            "count": 1,
            "truncated": False,
            "facility_type": "hospital_horizon",
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_health_facilities",
            mock_fetch,
        )

        result = await nb_get_health_facilities(facility_type="hospital_horizon", lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"
        assert result["data"]["count"] == 1
        mock_fetch.assert_awaited_once_with(
            facility_type="hospital_horizon", name=None, limit=MAX_RECORDS
        )

    @pytest.mark.asyncio
    async def test_name_filter_passed_through(self, monkeypatch):
        payload = {"features": [], "count": 0, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_health_facilities",
            mock_fetch,
        )

        await nb_get_health_facilities(facility_type="pharmacy", name="Shoppers", lang="en")

        mock_fetch.assert_awaited_once_with(
            facility_type="pharmacy", name="Shoppers", limit=MAX_RECORDS
        )

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=InvalidInput("facility_type must be one of [...]")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_health_facilities",
            mock_fetch,
        )

        result = await nb_get_health_facilities(facility_type="hospital_horizon", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_health_facilities",
            mock_fetch,
        )

        result = await nb_get_health_facilities(facility_type="hospital_horizon", lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_sets_meta_lang_and_distinct_invalid_message(self, monkeypatch):
        en = await nb_get_health_facilities(facility_type="not-a-real-type", lang="en")
        fr = await nb_get_health_facilities(facility_type="not-a-real-type", lang="fr")

        assert en["error"]["message"] != fr["error"]["message"]
        assert fr["error"]["lang"] == "fr"


class TestNbGetPublicSchools:
    @pytest.mark.asyncio
    async def test_invalid_sector_returns_invalid_input_without_network_call(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock()
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        result = await nb_get_public_schools(sector="not-a-real-sector", lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        assert result["error"]["valid"] == sorted(SCHOOL_SECTOR_LAYERS)
        mock_fetch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_happy_path_default_sector_envelope(self, monkeypatch):
        payload = {
            "features": [{"strID": "4010", "strNM": "Harcourt School"}],
            "count": 1,
            "truncated": False,
        }
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        result = await nb_get_public_schools(lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-geonb"
        assert result["data"]["count"] == 1
        mock_fetch.assert_awaited_once_with(
            sector="anglophone", district=None, limit=MAX_RECORDS
        )

    @pytest.mark.asyncio
    async def test_district_filter_passed_through(self, monkeypatch):
        payload = {"features": [], "count": 0, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        await nb_get_public_schools(sector="francophone", district="DSF-S", lang="en")

        mock_fetch.assert_awaited_once_with(
            sector="francophone", district="DSF-S", limit=MAX_RECORDS
        )

    @pytest.mark.asyncio
    async def test_client_invalid_input_second_line_of_defence_also_returns_invalid_input(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(side_effect=InvalidInput("sector must be one of [...]"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        result = await nb_get_public_schools(lang="en")

        assert result["error"]["code"] == "INVALID_INPUT"
        mock_fetch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        result = await nb_get_public_schools(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr_sets_meta_lang(self, monkeypatch):
        payload = {"features": [], "count": 0, "truncated": False}
        mock_fetch = AsyncMock(return_value=(payload, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_public_schools",
            mock_fetch,
        )

        result = await nb_get_public_schools(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# NB 511 — three key-gated transport tools (Task 2, D-09/D-10)
# ---------------------------------------------------------------------------


class TestNbGetRoadEvents:
    @pytest.mark.asyncio
    async def test_key_absent_returns_not_configured_envelope_not_exception(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert result["error"]["code"] == "NOT_CONFIGURED"
        assert "NEW_BRUNSWICK_511_KEY" in result["error"]["message"]
        assert "511.gnb.ca" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_not_configured_message_differs_by_language(self, monkeypatch):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        en = await nb_get_road_events(lang="en")
        fr = await nb_get_road_events(lang="fr")

        assert en["error"]["code"] == fr["error"]["code"] == "NOT_CONFIGURED"
        assert en["error"]["message"] != fr["error"]["message"]

    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch, five11_event_sample):
        mock_fetch = AsyncMock(return_value=(five11_event_sample, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-511"
        assert result["data"] == five11_event_sample

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_http_500_returns_upstream_error_envelope(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://511.gnb.ca/api/v2/get/event"),
            response=httpx.Response(500),
        )
        mock_fetch = AsyncMock(side_effect=error)
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_not_configured_never_leaks_sentinel_key_in_serialised_response(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_road_events", mock_fetch
        )

        result = await nb_get_road_events(lang="en")

        assert "SENTINEL" not in json.dumps(result)


class TestNbGetWinterRoadConditions:
    @pytest.mark.asyncio
    async def test_key_absent_returns_not_configured_envelope_not_exception(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert result["error"]["code"] == "NOT_CONFIGURED"
        assert "NEW_BRUNSWICK_511_KEY" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_not_configured_message_differs_by_language(self, monkeypatch):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        en = await nb_get_winter_road_conditions(lang="en")
        fr = await nb_get_winter_road_conditions(lang="fr")

        assert en["error"]["message"] != fr["error"]["message"]

    @pytest.mark.asyncio
    async def test_happy_path_empty_list_outside_season_is_success(self, monkeypatch):
        mock_fetch = AsyncMock(return_value=([], False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert "error" not in result
        assert result["data"] == []

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_http_500_returns_upstream_error_envelope(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://511.gnb.ca/api/v2/get/winterroads"),
            response=httpx.Response(500),
        )
        mock_fetch = AsyncMock(side_effect=error)
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_not_configured_never_leaks_sentinel_key_in_serialised_response(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_winter_road_conditions",
            mock_fetch,
        )

        result = await nb_get_winter_road_conditions(lang="en")

        assert "SENTINEL" not in json.dumps(result)


class TestNbGetTrafficCameras:
    @pytest.mark.asyncio
    async def test_key_absent_returns_not_configured_envelope_not_exception(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert result["error"]["code"] == "NOT_CONFIGURED"
        assert "NEW_BRUNSWICK_511_KEY" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_not_configured_message_differs_by_language(self, monkeypatch):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        en = await nb_get_traffic_cameras(lang="en")
        fr = await nb_get_traffic_cameras(lang="fr")

        assert en["error"]["message"] != fr["error"]["message"]

    @pytest.mark.asyncio
    async def test_happy_path_envelope(self, monkeypatch):
        rows_sample = [{"Id": "cam-1", "Name": "Route 1 at Fredericton"}]
        mock_fetch = AsyncMock(return_value=(rows_sample, False))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert "error" not in result
        assert result["_meta"]["source"]["api"] == "new-brunswick-511"
        assert result["data"] == rows_sample

    @pytest.mark.asyncio
    async def test_timeout_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.TimeoutException("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_connect_error_returns_upstream_error_envelope(self, monkeypatch):
        mock_fetch = AsyncMock(side_effect=httpx.ConnectError("boom"))
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_http_500_returns_upstream_error_envelope(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://511.gnb.ca/api/v2/get/cameras"),
            response=httpx.Response(500),
        )
        mock_fetch = AsyncMock(side_effect=error)
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_not_configured_never_leaks_sentinel_key_in_serialised_response(
        self, monkeypatch
    ):
        mock_fetch = AsyncMock(
            side_effect=Five11NotConfigured("NEW_BRUNSWICK_511_KEY not set")
        )
        monkeypatch.setattr(
            "mcp_canada.modules.new_brunswick.tools._client.fetch_traffic_cameras",
            mock_fetch,
        )

        result = await nb_get_traffic_cameras(lang="en")

        assert "SENTINEL" not in json.dumps(result)


# ---------------------------------------------------------------------------
# Cross-tool envelope / lang contract — Plan 07 parametrizes across every tool
# ---------------------------------------------------------------------------

# (tool_name, client_fn_attribute_on_client, sample_kwargs, sample_client_return, api_name)
#
# One entry per name in constants.ALL_NB_TOOL_NAMES (22) — mirrors the Nova
# Scotia / Saskatchewan Plan 07 pattern. kwargs supply the minimum arguments a
# tool needs to reach its success path (e.g. a filter for the three
# FILTER_REQUIRED_TOOLS entries, a facility_type/dataset_id where required).
ALL_NB_TOOLS: list[tuple[str, str, dict, tuple, str]] = [
    # Crown land — Task 1 tracer
    (
        "nb_get_crown_land",
        "fetch_crown_land",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    # Federal CKAN discovery (organization:nb) — D-01
    (
        "nb_search_datasets",
        "fetch_search_datasets",
        {},
        ({"results": [], "total": 0}, False),
        "new-brunswick-federal-ckan",
    ),
    (
        "nb_get_dataset_details",
        "fetch_dataset_details",
        {"dataset_id": "flood-risk-areas"},
        ({"id": "flood-risk-areas", "title": "Flood Risk Areas", "resources": []}, False),
        "new-brunswick-federal-ckan",
    ),
    (
        "nb_query_dataset",
        "fetch_query_dataset",
        {"dataset_id": "flood-risk-areas"},
        ({"rows": [], "resource": {"format": "CSV"}, "truncated": False}, False),
        "new-brunswick-federal-ckan",
    ),
    (
        "nb_list_organizations",
        "fetch_organizations",
        {},
        ([], False),
        "new-brunswick-federal-ckan",
    ),
    (
        "nb_list_categories",
        "fetch_categories",
        {},
        ({"subjects": [], "topics": [], "formats": []}, False),
        "new-brunswick-federal-ckan",
    ),
    # gnb.socrata.com discovery — checkpoint option-a
    (
        "nb_search_gnb_socrata_datasets",
        "fetch_gnb_socrata_search",
        {},
        ({"results": [], "total": 0}, False),
        "new-brunswick-gnb-socrata",
    ),
    (
        "nb_query_gnb_socrata_dataset",
        "fetch_gnb_socrata_query",
        {"dataset_id": "abcd-1234"},
        ({"rows": [], "count": 0, "truncated": False}, False),
        "new-brunswick-gnb-socrata",
    ),
    # GeoNB discovery — D-06, stands in for the 401-ing Hub Search API
    (
        "nb_list_geonb_services",
        "fetch_geonb_services",
        {},
        ([], False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_geonb_service_layers",
        "fetch_geonb_service_layers",
        {"service_name": "GeoNB_DNR_Crown_Land"},
        ({"layers": [], "tables": []}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_query_geonb_layer",
        "fetch_geonb_layer_features",
        {"service_name": "GeoNB_DNR_Crown_Land", "layer_id": 3},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    # Curated flood / water
    (
        "nb_get_flood_hazard_areas",
        "fetch_flood_hazard_areas",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_historical_floods",
        "fetch_historical_floods",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_wetlands",
        "fetch_wetlands",
        {"wetland_class": "Bog"},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_contaminated_sites",
        "fetch_contaminated_sites",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    # Parcels / civic address — both FILTER_REQUIRED_TOOLS
    (
        "nb_get_parcels",
        "fetch_parcels",
        {"county": "YORK"},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_civic_addresses",
        "fetch_civic_addresses",
        {"community": "FREDERICTON"},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    # Health / education dispatch tools
    (
        "nb_get_health_facilities",
        "fetch_health_facilities",
        {"facility_type": "hospital_horizon"},
        ({"features": [], "count": 0, "truncated": False, "facility_type": "hospital_horizon"}, False),
        "new-brunswick-geonb",
    ),
    (
        "nb_get_public_schools",
        "fetch_public_schools",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
        "new-brunswick-geonb",
    ),
    # NB 511 — key-gated (envelope/lang tests exercise the CONFIGURED success
    # path via a mocked fetch; the NOT_CONFIGURED path is covered per-tool above)
    (
        "nb_get_road_events",
        "fetch_road_events",
        {},
        ([], False),
        "new-brunswick-511",
    ),
    (
        "nb_get_winter_road_conditions",
        "fetch_winter_road_conditions",
        {},
        ([], False),
        "new-brunswick-511",
    ),
    (
        "nb_get_traffic_cameras",
        "fetch_traffic_cameras",
        {},
        ([], False),
        "new-brunswick-511",
    ),
]

assert len(ALL_NB_TOOLS) == 22, (
    f"ALL_NB_TOOLS must have 22 entries (matching ALL_NB_TOOL_NAMES), got {len(ALL_NB_TOOLS)}"
)
assert {t[0] for t in ALL_NB_TOOLS} == set(ALL_NB_TOOL_NAMES), (
    f"ALL_NB_TOOLS tool names must exactly match constants.ALL_NB_TOOL_NAMES — "
    f"only in ALL_NB_TOOLS: {set(t[0] for t in ALL_NB_TOOLS) - set(ALL_NB_TOOL_NAMES)}, "
    f"only in ALL_NB_TOOL_NAMES: {set(ALL_NB_TOOL_NAMES) - set(t[0] for t in ALL_NB_TOOLS)}"
)


class TestNbEnvelopes:
    """Parametrized: all 22 nb_ tools return _meta envelope on success (Plan 07).

    Mirrors the Nova Scotia / Saskatchewan Plan 07 pattern. Each tool is called
    with a mocked client function returning an empty-but-valid payload. Asserts
    the full _meta envelope shape: source.api, source.url, cached, lang,
    timestamp keys all present.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return", "api_name"),
        ALL_NB_TOOLS,
        ids=[t[0] for t in ALL_NB_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_envelope_structure(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple, api_name: str
    ) -> None:
        """Every nb_ tool returns _meta with {source.api, source.url, cached, lang, timestamp}."""
        tool_fn = getattr(nb_tools, tool_name)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                f"mcp_canada.modules.new_brunswick.tools._client.{client_fn}",
                AsyncMock(return_value=client_return),
            )
            result = await tool_fn(**kwargs, lang="en")

        assert "_meta" in result, f"{tool_name} missing _meta envelope: {result}"
        meta = result["_meta"]
        for key in ("source", "cached", "lang", "timestamp"):
            assert key in meta, f"{tool_name} _meta missing {key!r}"
        assert "api" in meta["source"], f"{tool_name} _meta.source missing 'api'"
        assert "url" in meta["source"], f"{tool_name} _meta.source missing 'url'"
        assert meta["source"]["api"] == api_name, (
            f"{tool_name} _meta.source.api must be {api_name!r}, got {meta['source']['api']!r}"
        )
        assert meta["lang"] == "en", (
            f"{tool_name} should default _meta.lang to 'en', got {meta['lang']!r}"
        )


class TestNbLangParam:
    """Parametrized: all 22 nb_ tools accept lang='fr' and propagate to _meta.lang (Plan 07)."""

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return", "api_name"),
        ALL_NB_TOOLS,
        ids=[t[0] for t in ALL_NB_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_lang_propagation(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple, api_name: str
    ) -> None:
        """Every tool propagates lang='fr' to the _meta.lang field on success."""
        tool_fn = getattr(nb_tools, tool_name)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                f"mcp_canada.modules.new_brunswick.tools._client.{client_fn}",
                AsyncMock(return_value=client_return),
            )
            result = await tool_fn(**kwargs, lang="fr")

        assert result.get("_meta", {}).get("lang") == "fr", (
            f"{tool_name} did not propagate lang='fr' to _meta.lang — got {result.get('_meta')}"
        )


class TestNbErrorPathLang:
    """Parametrized: all 22 nb_ tools return a structured error envelope — never
    raise — when the client raises an unclassified exception, and the error's
    `lang` field carries the caller's requested language (Plan 07).

    upstream_guard's generic-exception message text is English-only by design
    (shared/envelope.py) — the localized text lives in each tool's own
    InvalidInput/NotFound/Five11NotConfigured handling, already covered by the
    per-tool test classes above (e.g. TestNbGetWetlands, TestNbGetParcels,
    TestNbGetHealthFacilities, TestNbGetRoadEvents/WinterRoadConditions/
    TrafficCameras). This class proves the one guarantee that holds for every
    tool uniformly: the error envelope's `lang` field is never silently
    dropped, regardless of which exception path fired.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return", "api_name"),
        ALL_NB_TOOLS,
        ids=[t[0] for t in ALL_NB_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_error_path_lang_field(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple, api_name: str
    ) -> None:
        """Every tool returns error.lang == 'fr' on an unclassified upstream failure."""
        tool_fn = getattr(nb_tools, tool_name)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                f"mcp_canada.modules.new_brunswick.tools._client.{client_fn}",
                AsyncMock(side_effect=RuntimeError("unclassified upstream failure")),
            )
            result = await tool_fn(**kwargs, lang="fr")

        assert "error" in result, f"{tool_name} must return an error envelope, not raise: {result}"
        assert result["error"].get("lang") == "fr", (
            f"{tool_name} error envelope must carry lang='fr' — got {result['error']}"
        )
        assert result["error"].get("code"), f"{tool_name} error envelope missing 'code': {result['error']}"
