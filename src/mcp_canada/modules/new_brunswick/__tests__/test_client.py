"""Unit tests for new_brunswick/client.py.

Task 1 tracer (fetch_crown_land) is fully tested here plus the fully-
implemented Wave 0 private helpers (_build_fq, _geonb_query, _511_get,
Five11NotConfigured). Plan 02 (Task 1) fills TestSharedApiGetContract and
TestShapeDatasetBilingual, plus one class per federal-CKAN discovery
function. Plan 02 (Task 3, checkpoint option-a) fills TestFetchGnbSocrataSearch
and TestFetchGnbSocrataQuery. Plan 04 fills TestFetchGeonbServices,
TestFetchGeonbServiceLayers, TestFetchGeonbLayerFeatures,
TestFetchFloodHazardAreas, TestFetchHistoricalFloods, TestFetchWetlands and
TestFetchContaminatedSites. Plan 05 fills TestFetchParcels and
TestFetchCivicAddresses (the two FILTER_REQUIRED_TOOLS large layers). Plan 06
fills TestFetchHealthFacilities, TestFetchPublicSchools (the two dispatch
tools) and TestFetchRoadEvents / TestFetchWinterRoadConditions /
TestFetchTrafficCameras (the three key-gated 511 tools) — the last
`fetch_*` stubs, closing the 22-tool manifest.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from mcp_canada.modules.new_brunswick import client as nb_client
from mcp_canada.modules.new_brunswick.constants import (
    CROWN_LAND_LAYER,
    FIVE11_KEY_ENV,
    HEALTH_FACILITY_LAYERS,
    NB_ORG_FQ,
    SCHOOL_SECTOR_LAYERS,
)
from mcp_canada.shared.errors import InvalidInput, NotFound


# ---------------------------------------------------------------------------
# Fully-implemented Wave 0 private helpers
# ---------------------------------------------------------------------------


class TestBuildFq:
    def test_no_extra_fq_returns_nb_org_clause_alone(self):
        assert nb_client._build_fq(None) == NB_ORG_FQ

    def test_extra_fq_is_and_ed_after_nb_org_clause(self):
        result = nb_client._build_fq("res_format:CSV")
        # WR-01: both clauses are explicitly parenthesized so Solr's Lucene
        # query parser can't reinterpret operator precedence regardless of
        # what the caller's fragment contains.
        assert result == f"({NB_ORG_FQ}) AND (res_format:CSV)"
        assert result.startswith(f"({NB_ORG_FQ})")  # NB clause always first (T-21-04)

    def test_hostile_extra_fq_cannot_widen_result_past_nb_scope(self):
        # WR-01: assert actual boolean SEMANTICS, not just string shape.
        # Substitute the NB clause and the hostile fragment's leaf terms
        # with Python booleans and evaluate the composed expression under
        # standard `and`/`or` precedence (mirrors Lucene's) — a caller
        # cannot construct a fragment that makes the whole fq true while
        # the NB clause is false, which is exactly what an unparenthesized
        # `A AND B OR C` would have allowed.
        hostile = "*:* OR organization:xyz"
        fq = nb_client._build_fq(hostile)
        assert fq == f"({NB_ORG_FQ}) AND ({hostile})"

        def evaluate(nb_is_true: bool, hostile_is_true: bool) -> bool:
            expr = (
                fq.replace(NB_ORG_FQ, str(nb_is_true))
                .replace("*:*", str(hostile_is_true))
                .replace("organization:xyz", str(hostile_is_true))
                .replace("AND", "and")
                .replace("OR", "or")
            )
            return eval(expr)  # noqa: S307 -- fixed test-only boolean expression

        assert evaluate(nb_is_true=False, hostile_is_true=True) is False
        assert evaluate(nb_is_true=True, hostile_is_true=True) is True
        assert evaluate(nb_is_true=True, hostile_is_true=False) is False


class TestShapeDatasetBilingual:
    def test_lang_fr_distinct_title_translated_returns_fr(self, ckan_package_search_sample):
        raw = ckan_package_search_sample["result"]["results"][0]
        shaped = nb_client._shape_dataset(raw, lang="fr")
        assert shaped["title"] == raw["title_translated"]["fr"]
        assert shaped["description"] == raw["notes_translated"]["fr"]

    def test_lang_fr_duplicate_record_pair_still_returns_french_text(
        self, ckan_childcare_fr_package
    ):
        shaped = nb_client._shape_dataset(ckan_childcare_fr_package, lang="fr")
        assert shaped["title"] == ckan_childcare_fr_package["title_translated"]["fr"]

    def test_no_title_translated_falls_back_to_plain_title(self):
        raw = {"id": "x", "title": "Plain Title", "notes": "Plain notes"}
        shaped = nb_client._shape_dataset(raw, lang="fr")
        assert shaped["title"] == "Plain Title"
        assert shaped["description"] == "Plain notes"

    def test_keywords_flattened_to_requested_language(self):
        raw = {
            "id": "x",
            "title": "T",
            "keywords": {"en": ["flood", "water"], "fr": ["inondation", "eau"]},
        }
        shaped = nb_client._shape_dataset(raw, lang="fr")
        assert shaped["keywords"] == ["inondation", "eau"]

    def test_keywords_fall_back_to_english_list(self):
        raw = {"id": "x", "title": "T", "keywords": {"en": ["flood"]}}
        shaped = nb_client._shape_dataset(raw, lang="fr")
        assert shaped["keywords"] == ["flood"]

    def test_no_keywords_key_returns_empty_list(self):
        raw = {"id": "x", "title": "T"}
        shaped = nb_client._shape_dataset(raw, lang="en")
        assert shaped["keywords"] == []


class TestSharedApiGetContract:
    """Patches the module-local api_get and asserts the outgoing params dict
    for every federal-CKAN discovery function, including the non-overridable
    NB organization clause (T-21-04)."""

    @pytest.mark.asyncio
    async def test_search_outgoing_params_plain(self, monkeypatch, ckan_package_search_sample):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_search_datasets(query="flood", limit=5, offset=0)

        params = mock_api_get.call_args.args[1]
        assert params["q"] == "flood"
        assert params["rows"] == 5
        assert params["start"] == 0
        assert params["fq"] == NB_ORG_FQ

    @pytest.mark.asyncio
    async def test_search_extra_fq_anded_after_nb_clause(
        self, monkeypatch, ckan_package_search_sample
    ):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_search_datasets(extra_fq="res_format:CSV")

        params = mock_api_get.call_args.args[1]
        assert params["fq"] == f"({NB_ORG_FQ}) AND (res_format:CSV)"

    @pytest.mark.asyncio
    async def test_search_hostile_fq_cannot_displace_nb_clause(
        self, monkeypatch, ckan_package_search_sample
    ):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_search_datasets(extra_fq="*:* OR organization:on")

        params = mock_api_get.call_args.args[1]
        fq = params["fq"]
        assert fq == f"({NB_ORG_FQ}) AND (*:* OR organization:on)"

        # WR-01: verify actual boolean semantics, not just string shape —
        # the composed fq can never be true unless the NB clause is true,
        # regardless of how the caller's fragment evaluates.
        def evaluate(nb_is_true: bool, hostile_is_true: bool) -> bool:
            expr = (
                fq.replace(NB_ORG_FQ, str(nb_is_true))
                .replace("*:*", str(hostile_is_true))
                .replace("organization:on", str(hostile_is_true))
                .replace("AND", "and")
                .replace("OR", "or")
            )
            return eval(expr)  # noqa: S307 -- fixed test-only boolean expression

        assert evaluate(nb_is_true=False, hostile_is_true=True) is False
        assert evaluate(nb_is_true=True, hostile_is_true=True) is True

    @pytest.mark.asyncio
    async def test_search_limit_clamped_to_ckan_max(self, monkeypatch, ckan_package_search_sample):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_search_datasets(limit=500)

        params = mock_api_get.call_args.args[1]
        assert params["rows"] == 100

    @pytest.mark.asyncio
    async def test_search_offset_floored_at_zero(self, monkeypatch, ckan_package_search_sample):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_search_datasets(offset=-5)

        params = mock_api_get.call_args.args[1]
        assert params["start"] == 0

    @pytest.mark.asyncio
    async def test_dataset_details_outgoing_params(self, monkeypatch, ckan_package_search_sample):
        raw = ckan_package_search_sample["result"]["results"][0]
        mock_api_get = AsyncMock(return_value={"success": True, "result": raw})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_dataset_details("aa11bb22-nb-submerged-lands")

        params = mock_api_get.call_args.args[1]
        assert params["id"] == "aa11bb22-nb-submerged-lands"

    @pytest.mark.asyncio
    async def test_organizations_outgoing_fq_and_rows(
        self, monkeypatch, ckan_package_search_sample
    ):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_organizations()

        params = mock_api_get.call_args.args[1]
        assert params["fq"] == NB_ORG_FQ
        assert params["rows"] == 1000

    @pytest.mark.asyncio
    async def test_categories_outgoing_fq_rows_and_facets(
        self, monkeypatch, ckan_package_search_sample
    ):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        await nb_client.fetch_categories()

        params = mock_api_get.call_args.args[1]
        assert params["fq"] == NB_ORG_FQ
        assert params["rows"] == 0
        assert "subject" in params["facet.field"]
        assert "topic_category" in params["facet.field"]
        assert "res_format" in params["facet.field"]


class TestGeonbQueryHelper:
    @pytest.mark.asyncio
    async def test_returns_features_count_truncated_shape(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client._geonb_query(
            "https://geonb.snb.ca/arcgis/rest/services/GeoNB_DNR_Crown_Land/MapServer",
            layer_id=CROWN_LAND_LAYER,
        )

        assert payload["count"] == len(features)
        assert payload["truncated"] is False
        assert cached is False
        assert mock_query.call_args.kwargs["layer_id"] == CROWN_LAND_LAYER


class TestFive11Get:
    @pytest.mark.asyncio
    async def test_raises_five11_not_configured_when_key_absent(self, monkeypatch):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)

        with pytest.raises(nb_client.Five11NotConfigured):
            await nb_client._511_get("event")

    @pytest.mark.asyncio
    async def test_not_configured_message_never_leaks_key_value(self, monkeypatch):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)

        with pytest.raises(nb_client.Five11NotConfigured) as exc_info:
            await nb_client._511_get("event")

        assert "SENTINEL" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_returns_list_when_key_set(self, monkeypatch, five11_event_sample):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        mock_api_get = AsyncMock(return_value=five11_event_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        rows = await nb_client._511_get("event")

        assert rows == five11_event_sample

    @pytest.mark.asyncio
    async def test_non_list_response_coerced_to_empty_list(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        mock_api_get = AsyncMock(return_value={"Error": {"Message": "Invalid Key"}})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        rows = await nb_client._511_get("event")

        assert rows == []


# ---------------------------------------------------------------------------
# GeoNB discovery private helpers — exercised directly (Task 1, Plan 04)
# ---------------------------------------------------------------------------


class TestGeonbHelpers:
    def test_decode_department_from_geonb_prefix(self):
        assert nb_client._decode_geonb_department("GeoNB_DNR_Crown_Land") == "DNR"

    def test_decode_department_returns_none_for_non_geonb_name(self):
        assert nb_client._decode_geonb_department("SomeOtherService") is None

    def test_exclusion_reason_named_service(self):
        reason = nb_client._geonb_exclusion_reason("GeoNB_DNR_WildlifeRefuges")
        assert "retired" in reason.lower()

    def test_exclusion_reason_basemap_prefix(self):
        reason = nb_client._geonb_exclusion_reason("GeoNB_Basemap_Grey")
        assert "basemap" in reason.lower()

    def test_exclusion_reason_fallback_for_unnamed_exclusion(self):
        reason = nb_client._geonb_exclusion_reason("GeoNB_Some_Other_Excluded_Service")
        assert reason == "excluded from the default listing"

    def test_escape_sql_value_doubles_apostrophe(self):
        assert nb_client._escape_sql_value("21G'15") == "21G''15"

    def test_require_any_filter_noop_for_tool_not_in_filter_required(self):
        # A tool name that is not in FILTER_REQUIRED_TOOLS is a no-op even
        # with zero filters — the guard set is driven by the constant, not
        # hardcoded per call site.
        nb_client._require_any_filter("nb_get_crown_land", None, None, layer_record_count=1)

    def test_require_any_filter_raises_when_registered_and_unfiltered(self):
        with pytest.raises(InvalidInput):
            nb_client._require_any_filter("nb_get_wetlands", None, None, layer_record_count=163_206)

    def test_require_any_filter_passes_when_registered_and_filtered(self):
        nb_client._require_any_filter("nb_get_wetlands", "Bog", None, layer_record_count=163_206)

    # -- CR-01: FILTER_REQUIRED guard must reject whitespace-only filters ----

    def test_require_any_filter_raises_for_whitespace_only_string(self):
        # " " is truthy in Python — the guard must strip() before testing,
        # or a whitespace-only filter silently satisfies "a filter was given".
        with pytest.raises(InvalidInput):
            nb_client._require_any_filter("nb_get_wetlands", " ", None, layer_record_count=163_206)

    def test_require_any_filter_passes_for_zero_int_filter(self):
        # civic_number=0 is a real, meaningful filter value — falsy under
        # bare `any()` but must NOT be treated as "no filter given".
        nb_client._require_any_filter(
            "nb_get_civic_addresses", None, None, 0, layer_record_count=373_172
        )

    # -- CR-01: LIKE metacharacters must be escaped, not just apostrophes ----

    def test_upper_contains_clause_escapes_percent_wildcard(self):
        # A bare '%' must become a literal-match clause, never a live SQL
        # LIKE wildcard that matches every row.
        clause = nb_client._upper_contains_clause("COUNTY", "%")
        assert clause == r"UPPER(COUNTY) LIKE '%\%%' ESCAPE '\'"

    def test_upper_contains_clause_escapes_underscore_wildcard(self):
        clause = nb_client._upper_contains_clause("COUNTY", "_")
        assert clause == r"UPPER(COUNTY) LIKE '%\_%' ESCAPE '\'"

    def test_upper_contains_clause_escapes_literal_backslash(self):
        clause = nb_client._upper_contains_clause("COUNTY", "\\")
        assert clause == r"UPPER(COUNTY) LIKE '%\\%' ESCAPE '\'"

    def test_upper_contains_clause_still_escapes_apostrophe(self):
        clause = nb_client._upper_contains_clause("COUNTY", "Queen's")
        assert clause == r"UPPER(COUNTY) LIKE '%QUEEN''S%' ESCAPE '\'"


# ---------------------------------------------------------------------------
# Task 1 tracer — fetch_crown_land, exercised directly at the client layer
# ---------------------------------------------------------------------------


class TestFetchCrownLand:
    @pytest.mark.asyncio
    async def test_no_holder_sends_match_all_where(self, monkeypatch, crown_land_geojson):
        features = [f["properties"] for f in crown_land_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_crown_land()

        assert mock_query.call_args.kwargs["where"] == "1=1"
        assert payload["count"] == len(features)

    @pytest.mark.asyncio
    async def test_holder_builds_equality_where(self, monkeypatch, crown_land_geojson):
        matching = [crown_land_geojson["features"][0]["properties"]]
        mock_query = AsyncMock(return_value=(matching, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_crown_land(holder=2)

        assert mock_query.call_args.kwargs["where"] == "HOLDER=2"


# ---------------------------------------------------------------------------
# Placeholder classes — one per locked-signature client stub (owning plan fills)
# ---------------------------------------------------------------------------


class TestFetchSearchDatasets:
    @pytest.mark.asyncio
    async def test_returns_results_and_total(self, monkeypatch, ckan_package_search_sample):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, cached = await nb_client.fetch_search_datasets(query="flood", limit=5)

        assert cached is False
        assert payload["total"] == 221
        assert len(payload["results"]) == 2
        assert payload["results"][0]["id"] == "aa11bb22-nb-submerged-lands"

    @pytest.mark.asyncio
    async def test_results_shaped_through_shape_dataset(
        self, monkeypatch, ckan_package_search_sample
    ):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, _cached = await nb_client.fetch_search_datasets(lang="fr")

        first = payload["results"][0]
        assert first["title"] == "Zones de gestion des terres submergées"

    @pytest.mark.asyncio
    async def test_payload_echoes_clamped_limit_and_offset_not_raw_caller_values(
        self, monkeypatch, ckan_package_search_sample
    ):
        # WR-02: limit=500/offset=-5 sends rows=100/start=0 to CKAN (clamped
        # in the params dict below); the returned payload must report what
        # was actually sent upstream, not the caller's raw values — an agent
        # computing the next page's offset from the raw values would be
        # wrong.
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, _cached = await nb_client.fetch_search_datasets(limit=500, offset=-5)

        assert mock_api_get.call_args.args[1]["rows"] == 100
        assert mock_api_get.call_args.args[1]["start"] == 0
        assert payload["limit"] == 100
        assert payload["offset"] == 0


class TestFetchDatasetDetails:
    @pytest.mark.asyncio
    async def test_returns_shaped_details_with_resources_and_license(
        self, monkeypatch, ckan_package_search_sample
    ):
        raw = ckan_package_search_sample["result"]["results"][0]
        raw_with_license = {
            **raw,
            "license_title": "Open Government Licence",
            "license_url": "https://open.canada.ca/en/open-government-licence-canada",
            "date_published": "2026-01-01",
            "maintainer": "Service New Brunswick",
            "frequency": "annually",
            "spatial": "New Brunswick",
        }
        mock_api_get = AsyncMock(return_value={"success": True, "result": raw_with_license})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, cached = await nb_client.fetch_dataset_details("aa11bb22-nb-submerged-lands")

        assert cached is False
        assert payload["resources"][0]["format"] == "CSV"
        assert payload["license_title"] == "Open Government Licence"
        assert payload["maintainer"] == "Service New Brunswick"

    @pytest.mark.asyncio
    async def test_404_raises_not_found(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "not found",
            request=httpx.Request("GET", "https://open.canada.ca/data/api/3/action/package_show"),
            response=httpx.Response(404),
        )
        mock_api_get = AsyncMock(side_effect=error)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        with pytest.raises(NotFound):
            await nb_client.fetch_dataset_details("does-not-exist")

    @pytest.mark.asyncio
    async def test_non_404_http_error_propagates_unchanged(self, monkeypatch):
        error = httpx.HTTPStatusError(
            "server error",
            request=httpx.Request("GET", "https://open.canada.ca/data/api/3/action/package_show"),
            response=httpx.Response(500),
        )
        mock_api_get = AsyncMock(side_effect=error)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        with pytest.raises(httpx.HTTPStatusError):
            await nb_client.fetch_dataset_details("some-id")


class TestFetchQueryDataset:
    @pytest.mark.asyncio
    async def test_out_of_range_resource_index_raises_invalid_input(
        self, monkeypatch, ckan_package_search_sample
    ):
        raw = ckan_package_search_sample["result"]["results"][0]
        mock_api_get = AsyncMock(return_value={"success": True, "result": raw})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_query_dataset("aa11bb22-nb-submerged-lands", resource_index=9)

    @pytest.mark.asyncio
    async def test_negative_limit_raises_invalid_input_before_any_parsing(
        self, monkeypatch, ckan_package_search_sample
    ):
        # WR-03: rows[:limit] with a negative limit silently drops the
        # trailing abs(limit) rows instead of failing loudly, and
        # `truncated: len(rows) > limit` is nonsensically always True.
        # Must reject before fetch_dataset_details / fetch_and_parse run.
        mock_api_get = AsyncMock()
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)
        mock_parse = AsyncMock()
        monkeypatch.setattr(nb_client, "fetch_and_parse", mock_parse)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_query_dataset(
                "aa11bb22-nb-submerged-lands", resource_index=0, limit=-1
            )

        mock_api_get.assert_not_awaited()
        mock_parse.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_zero_limit_raises_invalid_input(self, monkeypatch):
        mock_api_get = AsyncMock()
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_query_dataset(
                "aa11bb22-nb-submerged-lands", resource_index=0, limit=0
            )

    @pytest.mark.asyncio
    async def test_csv_resource_routes_to_fetch_and_parse(
        self, monkeypatch, ckan_package_search_sample
    ):
        raw = ckan_package_search_sample["result"]["results"][0]
        mock_api_get = AsyncMock(return_value={"success": True, "result": raw})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)
        mock_parse = AsyncMock(return_value=([{"a": 1}, {"a": 2}], False))
        monkeypatch.setattr(nb_client, "fetch_and_parse", mock_parse)

        payload, _cached = await nb_client.fetch_query_dataset(
            "aa11bb22-nb-submerged-lands", resource_index=0, limit=1
        )

        mock_parse.assert_awaited_once()
        assert payload["rows"] == [{"a": 1}]
        assert payload["truncated"] is True

    @pytest.mark.asyncio
    async def test_unparseable_format_returns_metadata_only_never_raises(
        self, monkeypatch, ckan_package_search_sample
    ):
        raw = {
            **ckan_package_search_sample["result"]["results"][0],
            "resources": [
                {"id": "r1", "name": "Archive", "format": "ZIP", "url": "https://example.com/a.zip"}
            ],
        }
        mock_api_get = AsyncMock(return_value={"success": True, "result": raw})
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)
        mock_parse = AsyncMock()
        monkeypatch.setattr(nb_client, "fetch_and_parse", mock_parse)

        payload, _cached = await nb_client.fetch_query_dataset(
            "aa11bb22-nb-submerged-lands", resource_index=0
        )

        mock_parse.assert_not_awaited()
        assert payload["rows"] == []
        assert "note" in payload
        assert "https://example.com/a.zip" in payload["note"]


class TestFetchOrganizations:
    @pytest.mark.asyncio
    async def test_returns_parent_org_and_sections(self, monkeypatch, ckan_package_search_sample):
        mock_api_get = AsyncMock(return_value=ckan_package_search_sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, cached = await nb_client.fetch_organizations()

        assert cached is False
        assert payload[0]["name"] == "Government of New Brunswick"
        assert payload[0]["dataset_count"] == 2

    @pytest.mark.asyncio
    async def test_distinct_org_sections_aggregated(self, monkeypatch):
        sample = {
            "success": True,
            "result": {
                "count": 2,
                "results": [
                    {
                        "id": "p1",
                        "title": "P1",
                        "org_title_at_publication": {"en": "Government of New Brunswick"},
                        "org_section": {"en": "Energy", "fr": "Énergie"},
                    },
                    {
                        "id": "p2",
                        "title": "P2",
                        "org_title_at_publication": {"en": "Government of New Brunswick"},
                        "org_section": {},
                    },
                ],
            },
        }
        mock_api_get = AsyncMock(return_value=sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, _cached = await nb_client.fetch_organizations()

        section_names = [o["name"] for o in payload[1:]]
        assert "Energy" in section_names


class TestFetchCategories:
    @pytest.mark.asyncio
    async def test_returns_subjects_topics_formats_sorted_desc(self, monkeypatch):
        sample = {
            "success": True,
            "result": {
                "count": 221,
                "results": [],
                "facets": {
                    "subject": {"nature_and_environment": 120, "transport": 2},
                    "topic_category": {"geoscientific_information": 80, "elevation": 1},
                    "res_format": {"HTML": 221, "PDF": 30},
                },
            },
        }
        mock_api_get = AsyncMock(return_value=sample)
        monkeypatch.setattr(nb_client, "api_get", mock_api_get)

        payload, cached = await nb_client.fetch_categories()

        assert cached is False
        assert payload["subjects"][0] == {"name": "nature_and_environment", "count": 120}
        assert payload["topics"][0] == {"name": "geoscientific_information", "count": 80}
        assert payload["formats"][0] == {"name": "HTML", "count": 221}


class TestFetchGnbSocrataSearch:
    @pytest.mark.asyncio
    async def test_returns_results_and_total(self, monkeypatch, gnb_socrata_catalog_sample):
        mock_search = AsyncMock(return_value=gnb_socrata_catalog_sample)
        monkeypatch.setattr(nb_client.socrata, "search_catalog", mock_search)

        payload, cached = await nb_client.fetch_gnb_socrata_search(query="childcare")

        assert cached is False
        assert payload["total"] == 312
        assert payload["results"][0]["id"] == "4zbh-z2ij"
        assert mock_search.call_args.args[0] == "gnb.socrata.com"

    @pytest.mark.asyncio
    async def test_limit_clamped_to_100(self, monkeypatch, gnb_socrata_catalog_sample):
        mock_search = AsyncMock(return_value=gnb_socrata_catalog_sample)
        monkeypatch.setattr(nb_client.socrata, "search_catalog", mock_search)

        await nb_client.fetch_gnb_socrata_search(limit=500)

        assert mock_search.call_args.kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_no_x_app_token_header_sent(self, monkeypatch, gnb_socrata_catalog_sample):
        mock_search = AsyncMock(return_value=gnb_socrata_catalog_sample)
        monkeypatch.setattr(nb_client.socrata, "search_catalog", mock_search)

        await nb_client.fetch_gnb_socrata_search()

        assert mock_search.call_args.kwargs.get("app_token") is None


class TestFetchGnbSocrataQuery:
    @pytest.mark.asyncio
    async def test_returns_rows(self, monkeypatch, gnb_socrata_rows_sample):
        mock_query = AsyncMock(return_value=gnb_socrata_rows_sample)
        monkeypatch.setattr(nb_client.socrata, "query_dataset", mock_query)

        payload, cached = await nb_client.fetch_gnb_socrata_query("4zbh-z2ij")

        assert cached is False
        assert payload["rows"] == gnb_socrata_rows_sample
        assert payload["count"] == 2

    @pytest.mark.asyncio
    async def test_limit_above_module_cap_raises_before_any_network_call(self, monkeypatch):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.socrata, "query_dataset", mock_query)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_gnb_socrata_query("4zbh-z2ij", limit=nb_client.MAX_RECORDS + 1)

        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_x_app_token_header_sent(self, monkeypatch, gnb_socrata_rows_sample):
        mock_query = AsyncMock(return_value=gnb_socrata_rows_sample)
        monkeypatch.setattr(nb_client.socrata, "query_dataset", mock_query)

        await nb_client.fetch_gnb_socrata_query("4zbh-z2ij")

        assert mock_query.call_args.kwargs.get("app_token") is None


# ---------------------------------------------------------------------------
# GeoNB discovery — Task 1, D-06 (Plan 04)
# ---------------------------------------------------------------------------

_GEONB_FULL_DIRECTORY: list[dict[str, str]] = [
    {"name": "GeoNB_DNR_Crown_Land", "type": "MapServer"},
    {"name": "GeoNB_ENV_FloodHazardIndex", "type": "MapServer"},
    {"name": "GeoNB_ENV_Historical_Floods", "type": "MapServer"},
    {"name": "GeoNB_ENV_Wetlands", "type": "MapServer"},
    {"name": "GeoNB_ELG_Contaminated_Sites", "type": "MapServer"},
    {"name": "GeoNB_Basemap_Grey", "type": "MapServer"},
    {"name": "GeoNB_Basemap_Imagery", "type": "MapServer"},
    {"name": "GeoNB_Basemap_NBRN", "type": "MapServer"},
    {"name": "GeoNB_Basemap_Provinces_bare", "type": "MapServer"},
    {"name": "GeoNB_Basemap_Topo", "type": "MapServer"},
    {"name": "GeoNB_DNR_WildlifeRefuges", "type": "MapServer"},
]


class TestFetchGeonbServices:
    @pytest.mark.asyncio
    async def test_default_listing_hides_basemaps_and_retired_service(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        services, cached = await nb_client.fetch_geonb_services()

        assert cached is False
        names = [s["name"] for s in services]
        assert not any(n.startswith("GeoNB_Basemap_") for n in names)
        assert "GeoNB_DNR_WildlifeRefuges" not in names
        assert "GeoNB_DNR_Crown_Land" in names

    @pytest.mark.asyncio
    async def test_include_excluded_returns_basemaps_with_reason(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        services, _cached = await nb_client.fetch_geonb_services(include_excluded=True)

        basemap = next(s for s in services if s["name"] == "GeoNB_Basemap_Grey")
        assert basemap["excluded"] is True
        assert basemap["exclusion_reason"]

        retired = next(s for s in services if s["name"] == "GeoNB_DNR_WildlifeRefuges")
        assert retired["excluded"] is True
        assert "retired" in retired["exclusion_reason"].lower()

    @pytest.mark.asyncio
    async def test_query_filters_case_insensitively(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        services, _cached = await nb_client.fetch_geonb_services(query="FLOOD")

        names = [s["name"] for s in services]
        assert names == ["GeoNB_ENV_FloodHazardIndex", "GeoNB_ENV_Historical_Floods"]

    @pytest.mark.asyncio
    async def test_department_decoded_from_prefix(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        services, _cached = await nb_client.fetch_geonb_services()

        crown_land = next(s for s in services if s["name"] == "GeoNB_DNR_Crown_Land")
        assert crown_land["department"] == "DNR"

    @pytest.mark.asyncio
    async def test_curated_tool_name_surfaced_for_curated_service(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        services, _cached = await nb_client.fetch_geonb_services()

        crown_land = next(s for s in services if s["name"] == "GeoNB_DNR_Crown_Land")
        assert crown_land["curated_tool"] == "nb_get_crown_land"


class TestFetchGeonbServiceLayers:
    @pytest.mark.asyncio
    async def test_returns_layers_containing_id_three(
        self, monkeypatch, geonb_mapserver_layers_sample
    ):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)
        mock_layers = AsyncMock(return_value=geonb_mapserver_layers_sample)
        monkeypatch.setattr(nb_client.arcgis_hub, "get_arcgis_server_layers", mock_layers)
        mock_count = AsyncMock(return_value=10001)
        monkeypatch.setattr(nb_client.arcgis_hub, "get_count", mock_count)
        mock_meta = AsyncMock(return_value={"fields": [{"name": "HOLDER", "type": "esriFieldTypeInteger"}]})
        monkeypatch.setattr(nb_client.arcgis_hub, "get_layer_metadata", mock_meta)

        payload, cached = await nb_client.fetch_geonb_service_layers("GeoNB_DNR_Crown_Land")

        assert cached is False
        assert any(layer["id"] == 3 for layer in payload["layers"])
        assert payload["layers"][0]["record_count"] == 10001
        assert "HOLDER" in payload["layers"][0]["fields"]
        assert payload["tables"] == []

    @pytest.mark.asyncio
    async def test_unknown_service_raises_not_found_naming_listing_tool(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)

        with pytest.raises(NotFound) as exc_info:
            await nb_client.fetch_geonb_service_layers("GeoNB_Does_Not_Exist")

        assert "nb_list_geonb_services" in str(exc_info.value)


class TestFetchGeonbLayerFeatures:
    @pytest.mark.asyncio
    async def test_where_none_passed_through_for_downstream_coalescing(self, monkeypatch):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_geonb_layer_features(
            "GeoNB_ENV_FloodHazardIndex", 0, where=None
        )

        # where=None flows through unchanged; query_feature_service (and the
        # httpx params dict beneath it) coalesce a falsy where to "1=1" —
        # proven directly in shared/__tests__/test_arcgis_hub.py.
        assert mock_query.call_args.kwargs["where"] is None
        assert mock_query.call_args.args[0].endswith("GeoNB_ENV_FloodHazardIndex/MapServer")

    @pytest.mark.asyncio
    async def test_unknown_service_raises_not_found_before_any_feature_request(
        self, monkeypatch
    ):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(NotFound):
            await nb_client.fetch_geonb_layer_features("GeoNB_Does_Not_Exist", 0)

        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_limit_above_cap_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_geonb_layer_features(
                "GeoNB_DNR_Crown_Land", 3, limit=nb_client.MAX_RECORDS + 1
            )

        mock_list.assert_not_awaited()
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_empty_feature_collection_is_a_success_not_an_error(
        self, monkeypatch, empty_feature_collection
    ):
        mock_list = AsyncMock(return_value=_GEONB_FULL_DIRECTORY)
        monkeypatch.setattr(nb_client.arcgis_hub, "list_arcgis_server_services", mock_list)
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_geonb_layer_features(
            "GeoNB_DNR_Crown_Land", 3
        )

        assert payload["count"] == 0
        assert payload["features"] == []


class TestFetchFloodHazardAreas:
    @pytest.mark.asyncio
    async def test_no_sheet_sends_falsy_where(self, monkeypatch, flood_hazard_geojson):
        features = [f["properties"] for f in flood_hazard_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_flood_hazard_areas()

        assert cached is False
        assert not mock_query.call_args.kwargs["where"]
        assert payload["count"] == len(features)

    @pytest.mark.asyncio
    async def test_sheet_builds_escaped_equality_where(self, monkeypatch, flood_hazard_geojson):
        matching = [flood_hazard_geojson["features"][0]["properties"]]
        mock_query = AsyncMock(return_value=(matching, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_flood_hazard_areas(sheet="21G01")

        assert mock_query.call_args.kwargs["where"] == "Sheet_Numb='21G01'"

    @pytest.mark.asyncio
    async def test_apostrophe_in_sheet_value_is_escaped(self, monkeypatch, flood_hazard_geojson):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_flood_hazard_areas(sheet="21G'15")

        assert mock_query.call_args.kwargs["where"] == "Sheet_Numb='21G''15'"


class TestFetchHistoricalFloods:
    @pytest.mark.asyncio
    async def test_no_event_uses_main_layer(self, monkeypatch):
        mock_query = AsyncMock(return_value=([{"ID": "x"}], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_historical_floods()

        assert mock_query.call_args.kwargs["layer_id"] == nb_client.HISTORICAL_FLOODS_LAYER

    @pytest.mark.asyncio
    async def test_1973_event_uses_1973_layer(self, monkeypatch):
        mock_query = AsyncMock(return_value=([{"Id": 1}], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_historical_floods(event="1973")

        assert (
            mock_query.call_args.kwargs["layer_id"]
            == nb_client.HISTORICAL_FLOODS_1973_LAYER
        )

    @pytest.mark.asyncio
    async def test_unknown_event_raises_invalid_input_naming_valid_values(self, monkeypatch):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_historical_floods(event="1950")

        assert "1973" in str(exc_info.value)
        mock_query.assert_not_awaited()


class TestFetchWetlands:
    @pytest.mark.asyncio
    async def test_no_filter_raises_invalid_input_before_any_network_call(self, monkeypatch):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_wetlands()

        assert "163,206" in str(exc_info.value)
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_whitespace_only_filter_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        # CR-01: " " is truthy, so a naive `any(filters)` guard would let this
        # through and then build `UPPER(...) LIKE '% %'`, matching every
        # multi-word value in the layer.
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_wetlands(wetland_class=" ")

        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_wetland_class_filter_returns_features(self, monkeypatch, wetlands_geojson):
        features = [f["properties"] for f in wetlands_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_wetlands(wetland_class="Bog")

        assert cached is False
        assert payload["count"] == len(features)
        assert mock_query.call_args.kwargs["where"] == "WETLAND_CLASS='Bog'"

    @pytest.mark.asyncio
    async def test_both_filters_anded(self, monkeypatch, wetlands_geojson):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_wetlands(wetland_class="Bog", status="Provincially Significant")

        where = mock_query.call_args.kwargs["where"]
        assert "WETLAND_CLASS='Bog'" in where
        assert "STATUS='Provincially Significant'" in where
        assert " AND " in where


class TestFetchContaminatedSites:
    @pytest.mark.asyncio
    async def test_status_builds_escaped_english_status_clause(self, monkeypatch):
        mock_query = AsyncMock(return_value=([{"Status_E": "Active"}], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_contaminated_sites(status="Active")

        assert mock_query.call_args.kwargs["where"] == "Status_E='Active'"

    @pytest.mark.asyncio
    async def test_no_status_sends_falsy_where(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_contaminated_sites()

        assert cached is False
        assert not mock_query.call_args.kwargs["where"]
        assert payload["count"] == 0

    @pytest.mark.asyncio
    async def test_features_carry_bilingual_status_and_pidtype_fields(self, monkeypatch):
        row = {
            "Status_E": "Active",
            "Status_F": "Actif",
            "FileOpenDate": "2020-01-01",
            "PidType_E": "PID",
            "PidType_F": "NID",
        }
        mock_query = AsyncMock(return_value=([row], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_contaminated_sites(status="Active")

        feature = payload["features"][0]
        assert feature["Status_E"] == "Active"
        assert feature["Status_F"] == "Actif"


class TestFetchParcels:
    @pytest.mark.asyncio
    async def test_no_filter_raises_invalid_input_before_any_network_call(self, monkeypatch):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_parcels()

        assert "604,520" in str(exc_info.value)
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_whitespace_only_county_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_parcels(county=" ")

        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_percent_county_does_not_match_every_row(self, monkeypatch):
        # CR-01 (the severe half): "%" is a completely ordinary truthy string
        # that must NOT become a live SQL LIKE wildcard matching all 604,520
        # rows once it clears the filter-required guard.
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_parcels(county="%")

        where = mock_query.call_args.kwargs["where"]
        assert where == r"UPPER(COUNTY) LIKE '%\%%' ESCAPE '\'"

    @pytest.mark.asyncio
    async def test_pid_builds_escaped_equality_where(self, monkeypatch):
        mock_query = AsyncMock(
            return_value=([{"PID": "12345678", "COUNTY": "York"}], False)
        )
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_parcels(pid="12345678")

        assert cached is False
        assert mock_query.call_args.kwargs["where"] == "PID='12345678'"
        assert mock_query.call_args.kwargs["layer_id"] == nb_client.PARCELS_LAYER
        assert payload["count"] == 1

    @pytest.mark.asyncio
    async def test_county_builds_upper_containment_where(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_parcels(county="York")

        assert (
            mock_query.call_args.kwargs["where"]
            == r"UPPER(COUNTY) LIKE '%YORK%' ESCAPE '\'"
        )

    @pytest.mark.asyncio
    async def test_apostrophe_in_county_is_escaped(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_parcels(county="Queen's")

        assert (
            mock_query.call_args.kwargs["where"]
            == r"UPPER(COUNTY) LIKE '%QUEEN''S%' ESCAPE '\'"
        )

    @pytest.mark.asyncio
    async def test_features_carry_pid_county_titles_and_gazette_status(self, monkeypatch):
        row = {
            "PID": "12345678",
            "COUNTY": "York",
            "Titles_Status": "Registered",
            "Gazette_Status": "Published",
        }
        mock_query = AsyncMock(return_value=([row], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_parcels(pid="12345678")

        feature = payload["features"][0]
        assert feature["PID"] == "12345678"
        assert feature["Titles_Status"] == "Registered"
        assert feature["Gazette_Status"] == "Published"

    @pytest.mark.asyncio
    async def test_truncated_flag_passed_through(self, monkeypatch):
        mock_query = AsyncMock(return_value=([{"PID": "1"}], True))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_parcels(pid="1")

        assert payload["truncated"] is True


class TestFetchCivicAddresses:
    @pytest.mark.asyncio
    async def test_no_filter_raises_invalid_input_before_any_network_call(self, monkeypatch):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_civic_addresses()

        assert "373,172" in str(exc_info.value)
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_whitespace_only_community_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput):
            await nb_client.fetch_civic_addresses(community=" ")

        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_percent_community_does_not_match_every_row(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_civic_addresses(community="%")

        where = mock_query.call_args.kwargs["where"]
        assert where == r"UPPER(COMMUNITY) LIKE '%\%%' ESCAPE '\'"

    @pytest.mark.asyncio
    async def test_community_builds_upper_containment_where(
        self, monkeypatch, civic_address_geojson
    ):
        features = [f["properties"] for f in civic_address_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_civic_addresses(community="Fredericton")

        assert cached is False
        assert (
            mock_query.call_args.kwargs["where"]
            == r"UPPER(COMMUNITY) LIKE '%FREDERICTON%' ESCAPE '\'"
        )
        assert mock_query.call_args.kwargs["layer_id"] == nb_client.CIVIC_ADDRESS_LAYER
        assert payload["count"] == len(features)

    @pytest.mark.asyncio
    async def test_community_and_street_are_anded(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_civic_addresses(community="Fredericton", street="King")

        where = mock_query.call_args.kwargs["where"]
        assert r"UPPER(COMMUNITY) LIKE '%FREDERICTON%' ESCAPE '\'" in where
        assert r"UPPER(STREET) LIKE '%KING%' ESCAPE '\'" in where
        assert " AND " in where

    @pytest.mark.asyncio
    async def test_civic_number_sends_unquoted_numeric_comparison(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_civic_addresses(civic_number=160)

        where = mock_query.call_args.kwargs["where"]
        assert where == "CIVIC_NUM=160"
        assert "'160'" not in where

    @pytest.mark.asyncio
    async def test_apostrophe_in_community_is_escaped(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_civic_addresses(community="St. Martin's")

        where = mock_query.call_args.kwargs["where"]
        assert "ST. MARTIN''S" in where

    @pytest.mark.asyncio
    async def test_features_carry_civic_number_street_bilingual_type_and_community(
        self, monkeypatch, civic_address_geojson
    ):
        features = [f["properties"] for f in civic_address_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_civic_addresses(community="Fredericton")

        feature = payload["features"][0]
        assert feature["CIVIC_NUM"] == "440"
        assert feature["STREET"] == "King"
        assert feature["ST_TYPE_E"] == "St"
        assert feature["ST_TYPE_F"] == "Rue"
        assert feature["COMMUNITY"] == "Fredericton"

    @pytest.mark.asyncio
    async def test_truncated_flag_passed_through(self, monkeypatch):
        mock_query = AsyncMock(return_value=([{"CIVIC_NUM": 1}], True))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_civic_addresses(civic_number=1)

        assert payload["truncated"] is True


class TestFetchHealthFacilities:
    @pytest.mark.asyncio
    async def test_invalid_facility_type_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_health_facilities("not-a-real-type")

        assert "hospital_horizon" in str(exc_info.value)
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("facility_type, layer_id", sorted(HEALTH_FACILITY_LAYERS.items()))
    async def test_dispatches_correct_layer_id_for_every_key(
        self, monkeypatch, facility_type, layer_id
    ):
        # This is the assertion that would have caught the Saskatchewan
        # wrong-layer bug: read the dispatched layer id from call_args, not
        # from the mocked return value.
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_health_facilities(facility_type)

        assert mock_query.call_args.kwargs["layer_id"] == layer_id

    @pytest.mark.asyncio
    async def test_no_name_sends_falsy_where(self, monkeypatch, health_facility_geojson):
        features = [f["properties"] for f in health_facility_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, cached = await nb_client.fetch_health_facilities("hospital_horizon")

        assert mock_query.call_args.kwargs["where"] is None
        assert cached is False
        assert payload["count"] == len(features)
        assert payload["facility_type"] == "hospital_horizon"

    @pytest.mark.asyncio
    async def test_name_filter_uses_name_e_for_hospital_layers(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_health_facilities("hospital_horizon", name="Chalmers")

        assert mock_query.call_args.kwargs["where"] == r"UPPER(Name_E) LIKE '%CHALMERS%' ESCAPE '\'"

    @pytest.mark.asyncio
    async def test_name_filter_dispatches_to_layer_specific_field(self, monkeypatch):
        # Layer 3 (adult_residential_centre) does NOT carry Name_E — live-
        # verified 2026-07-30, a WHERE clause referencing it 400s upstream.
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_health_facilities("pharmacy", name="Shoppers")

        assert mock_query.call_args.kwargs["where"] == r"UPPER(Pharmacy_Name) LIKE '%SHOPPERS%' ESCAPE '\'"

    @pytest.mark.asyncio
    async def test_out_fields_is_wildcard_because_layers_do_not_share_a_schema(
        self, monkeypatch
    ):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_health_facilities("adult_residential_centre")

        assert mock_query.call_args.kwargs["out_fields"] == "*"

    @pytest.mark.asyncio
    async def test_empty_result_is_success_not_error(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_health_facilities("hospital_vitalite")

        assert payload["count"] == 0
        assert payload["features"] == []


class TestFetchPublicSchools:
    @pytest.mark.asyncio
    async def test_invalid_sector_raises_invalid_input_before_any_network_call(
        self, monkeypatch
    ):
        mock_query = AsyncMock()
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        with pytest.raises(InvalidInput) as exc_info:
            await nb_client.fetch_public_schools(sector="not-a-real-sector")

        assert "anglophone" in str(exc_info.value)
        mock_query.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("sector, layer_id", sorted(SCHOOL_SECTOR_LAYERS.items()))
    async def test_dispatches_correct_layer_id_for_every_key(
        self, monkeypatch, sector, layer_id
    ):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_public_schools(sector=sector)

        assert mock_query.call_args.kwargs["layer_id"] == layer_id

    @pytest.mark.asyncio
    async def test_default_sector_is_anglophone(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_public_schools()

        assert mock_query.call_args.kwargs["layer_id"] == SCHOOL_SECTOR_LAYERS["anglophone"]

    @pytest.mark.asyncio
    async def test_district_builds_upper_containment_where(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        await nb_client.fetch_public_schools(district="ASD-N")

        assert mock_query.call_args.kwargs["where"] == r"UPPER(strDST) LIKE '%ASD-N%' ESCAPE '\'"

    @pytest.mark.asyncio
    async def test_no_district_sends_falsy_where(self, monkeypatch, public_school_geojson):
        features = [f["properties"] for f in public_school_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_public_schools()

        assert mock_query.call_args.kwargs["where"] is None
        assert payload["count"] == len(features)

    @pytest.mark.asyncio
    async def test_features_carry_id_name_address_grade_url(
        self, monkeypatch, public_school_geojson
    ):
        features = [f["properties"] for f in public_school_geojson["features"]]
        mock_query = AsyncMock(return_value=(features, False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_public_schools()

        feature = payload["features"][0]
        assert feature["strID"] == "4010"
        assert feature["strNM"] == "Harcourt School"
        assert feature["strAD1"]
        assert feature["strGR"]
        assert feature["strURL"]

    @pytest.mark.asyncio
    async def test_empty_result_is_success_not_error(self, monkeypatch):
        mock_query = AsyncMock(return_value=([], False))
        monkeypatch.setattr(nb_client.arcgis_hub, "query_feature_service", mock_query)

        payload, _cached = await nb_client.fetch_public_schools(sector="francophone")

        assert payload["count"] == 0
        assert payload["features"] == []


class TestFetchRoadEvents:
    @pytest.mark.asyncio
    async def test_key_absent_raises_five11_not_configured_before_any_network_call(
        self, monkeypatch
    ):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)
        mock_get = AsyncMock()
        monkeypatch.setattr(nb_client, "api_get", mock_get)

        with pytest.raises(nb_client.Five11NotConfigured):
            await nb_client.fetch_road_events()

        mock_get.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_key_set_returns_rows_from_event_endpoint(
        self, monkeypatch, five11_event_sample
    ):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        mock_511_get = AsyncMock(return_value=five11_event_sample)
        monkeypatch.setattr(nb_client, "_511_get", mock_511_get)

        rows, cached = await nb_client.fetch_road_events()

        assert rows == five11_event_sample
        assert cached is False
        mock_511_get.assert_awaited_once_with("event")

    @pytest.mark.asyncio
    async def test_caches_at_live_ttl(self, monkeypatch, five11_event_sample):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        monkeypatch.setattr(
            nb_client, "_511_get", AsyncMock(return_value=five11_event_sample)
        )
        captured: dict[str, Any] = {}

        async def _spy_cached_fetch(key, ttl, fetcher):
            captured["ttl"] = ttl
            return await fetcher(), False

        monkeypatch.setattr(nb_client, "cached_fetch", _spy_cached_fetch)

        await nb_client.fetch_road_events()

        assert captured["ttl"] == nb_client.CACHE_TTL_LIVE

    @pytest.mark.asyncio
    async def test_timeout_propagates_for_tool_layer_to_classify(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        monkeypatch.setattr(
            nb_client, "_511_get", AsyncMock(side_effect=httpx.TimeoutException("boom"))
        )

        with pytest.raises(httpx.TimeoutException):
            await nb_client.fetch_road_events()


class TestFetchWinterRoadConditions:
    @pytest.mark.asyncio
    async def test_key_absent_raises_five11_not_configured_before_any_network_call(
        self, monkeypatch
    ):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)
        mock_get = AsyncMock()
        monkeypatch.setattr(nb_client, "api_get", mock_get)

        with pytest.raises(nb_client.Five11NotConfigured):
            await nb_client.fetch_winter_road_conditions()

        mock_get.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_key_set_returns_rows_from_winterroads_endpoint(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        rows_sample = [{"AreaName": "Northern", "Condition": "Good"}]
        mock_511_get = AsyncMock(return_value=rows_sample)
        monkeypatch.setattr(nb_client, "_511_get", mock_511_get)

        rows, cached = await nb_client.fetch_winter_road_conditions()

        assert rows == rows_sample
        assert cached is False
        mock_511_get.assert_awaited_once_with("winterroads")

    @pytest.mark.asyncio
    async def test_caches_at_live_ttl(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        monkeypatch.setattr(nb_client, "_511_get", AsyncMock(return_value=[]))
        captured: dict[str, Any] = {}

        async def _spy_cached_fetch(key, ttl, fetcher):
            captured["ttl"] = ttl
            return await fetcher(), False

        monkeypatch.setattr(nb_client, "cached_fetch", _spy_cached_fetch)

        await nb_client.fetch_winter_road_conditions()

        assert captured["ttl"] == nb_client.CACHE_TTL_LIVE

    @pytest.mark.asyncio
    async def test_empty_list_outside_season_is_success_not_error(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        monkeypatch.setattr(nb_client, "_511_get", AsyncMock(return_value=[]))

        rows, _cached = await nb_client.fetch_winter_road_conditions()

        assert rows == []


class TestFetchTrafficCameras:
    @pytest.mark.asyncio
    async def test_key_absent_raises_five11_not_configured_before_any_network_call(
        self, monkeypatch
    ):
        monkeypatch.delenv(FIVE11_KEY_ENV, raising=False)
        mock_get = AsyncMock()
        monkeypatch.setattr(nb_client, "api_get", mock_get)

        with pytest.raises(nb_client.Five11NotConfigured):
            await nb_client.fetch_traffic_cameras()

        mock_get.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_key_set_returns_rows_from_cameras_endpoint(self, monkeypatch):
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        rows_sample = [{"Id": "cam-1", "Name": "Route 1 at Fredericton"}]
        mock_511_get = AsyncMock(return_value=rows_sample)
        monkeypatch.setattr(nb_client, "_511_get", mock_511_get)

        rows, cached = await nb_client.fetch_traffic_cameras()

        assert rows == rows_sample
        assert cached is False
        mock_511_get.assert_awaited_once_with("cameras")

    @pytest.mark.asyncio
    async def test_caches_at_meta_ttl_not_live_ttl(self, monkeypatch):
        # Cameras are stable infrastructure — distinct from events/winter
        # roads, both of which cache at CACHE_TTL_LIVE.
        monkeypatch.setenv(FIVE11_KEY_ENV, "test-key-value")
        monkeypatch.setattr(nb_client, "_511_get", AsyncMock(return_value=[]))
        captured: dict[str, Any] = {}

        async def _spy_cached_fetch(key, ttl, fetcher):
            captured["ttl"] = ttl
            return await fetcher(), False

        monkeypatch.setattr(nb_client, "cached_fetch", _spy_cached_fetch)

        await nb_client.fetch_traffic_cameras()

        assert captured["ttl"] == nb_client.CACHE_TTL_META
        assert captured["ttl"] != nb_client.CACHE_TTL_LIVE
