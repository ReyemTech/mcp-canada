"""Unit tests for Toronto Open Data module prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.toronto.prompts import (
    toronto_check_311,
    toronto_explore_city_data,
    toronto_explore_neighbourhood,
    toronto_quick_search,
    toronto_rental_analysis,
    toronto_ttc_transit,
)
from mcp_canada.modules.toronto.resources import (
    toronto_311_service_types,
    toronto_city_divisions,
    toronto_ckan_guide,
    toronto_gtfs_guide,
    toronto_neighbourhood_list,
    toronto_neighbourhood_profiles_guide,
    toronto_neighbourhood_report_template,
    toronto_ward_list,
)


class TestTorontoPrompts:
    """Tests for the 6 Toronto @prompt functions."""

    # ------------------------------------------------------------------
    # toronto_explore_city_data — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_city_data_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(toronto_explore_city_data)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_city_data_en_roles(self):
        p = FunctionPrompt.from_function(toronto_explore_city_data)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_city_data_en_references_tool(self):
        p = FunctionPrompt.from_function(toronto_explore_city_data)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "toronto_search_datasets" in full_text

    @pytest.mark.asyncio
    async def test_explore_city_data_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(toronto_explore_city_data)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_explore_city_data_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_explore_city_data)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("données", "Toronto", "explorer", "recherche", "jeux de données")
        )

    # ------------------------------------------------------------------
    # toronto_quick_search — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_search_en_returns_single_message(self):
        p = FunctionPrompt.from_function(toronto_quick_search)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_en_references_tool(self):
        p = FunctionPrompt.from_function(toronto_quick_search)
        result = await p.render({"lang": "en"})
        assert "toronto_search_datasets" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_search_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(toronto_quick_search)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_search_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_quick_search)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "toronto_search_datasets" in text

    # ------------------------------------------------------------------
    # toronto_explore_neighbourhood — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_neighbourhood_en_returns_messages(self):
        p = FunctionPrompt.from_function(toronto_explore_neighbourhood)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_explore_neighbourhood_en_references_tool(self):
        p = FunctionPrompt.from_function(toronto_explore_neighbourhood)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "toronto_get_neighbourhood_profile" in full_text or "toronto_compare_neighbourhoods" in full_text

    @pytest.mark.asyncio
    async def test_explore_neighbourhood_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_explore_neighbourhood)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("quartier", "voisinage", "profil", "comparer", "Toronto")
        )

    # ------------------------------------------------------------------
    # toronto_ttc_transit — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ttc_transit_en_returns_messages(self):
        p = FunctionPrompt.from_function(toronto_ttc_transit)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_ttc_transit_en_references_tools(self):
        p = FunctionPrompt.from_function(toronto_ttc_transit)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "toronto_get_ttc_stops" in full_text or "toronto_get_ttc_routes" in full_text

    @pytest.mark.asyncio
    async def test_ttc_transit_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_ttc_transit)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("TTC", "transit", "arrêts", "lignes", "transport")
        )

    # ------------------------------------------------------------------
    # toronto_check_311 — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_311_en_returns_single_message(self):
        p = FunctionPrompt.from_function(toronto_check_311)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_311_en_references_tool(self):
        p = FunctionPrompt.from_function(toronto_check_311)
        result = await p.render({"lang": "en"})
        assert "toronto_get_311_requests" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_311_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_check_311)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "toronto_get_311_requests" in text

    # ------------------------------------------------------------------
    # toronto_rental_analysis — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_rental_analysis_en_returns_messages(self):
        p = FunctionPrompt.from_function(toronto_rental_analysis)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_rental_analysis_en_references_tools(self):
        p = FunctionPrompt.from_function(toronto_rental_analysis)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "toronto_get_rentsafe_evaluations" in full_text or "toronto_get_short_term_rentals" in full_text

    @pytest.mark.asyncio
    async def test_rental_analysis_fr_is_french(self):
        p = FunctionPrompt.from_function(toronto_rental_analysis)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("logement", "locatif", "location", "court terme", "appartements")
        )


class TestTorontoResources:
    """Tests for the 8 Toronto @resource functions."""

    # ------------------------------------------------------------------
    # data://toronto/city-divisions
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_city_divisions_is_valid_json(self):
        r = FunctionResource.from_function(
            toronto_city_divisions, uri="data://toronto/city-divisions"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_city_divisions_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            toronto_city_divisions, uri="data://toronto/city-divisions"
        )
        content = await r.read()
        data = json.loads(content)
        if isinstance(data, dict):
            first = next(iter(data.values()))
        else:
            first = data[0]
        assert "en" in first
        assert "fr" in first

    # ------------------------------------------------------------------
    # data://toronto/ward-list
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ward_list_is_valid_json(self):
        r = FunctionResource.from_function(
            toronto_ward_list, uri="data://toronto/ward-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_ward_list_has_25_wards(self):
        r = FunctionResource.from_function(
            toronto_ward_list, uri="data://toronto/ward-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) == 25

    # ------------------------------------------------------------------
    # data://toronto/neighbourhood-list
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_neighbourhood_list_is_valid_json(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_list, uri="data://toronto/neighbourhood-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_neighbourhood_list_has_140_neighbourhoods(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_list, uri="data://toronto/neighbourhood-list"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) == 140

    # ------------------------------------------------------------------
    # data://toronto/311-service-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_service_types_is_valid_json(self):
        r = FunctionResource.from_function(
            toronto_311_service_types, uri="data://toronto/311-service-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_service_types_has_entries(self):
        r = FunctionResource.from_function(
            toronto_311_service_types, uri="data://toronto/311-service-types"
        )
        content = await r.read()
        data = json.loads(content)
        if isinstance(data, list):
            assert len(data) > 0
        else:
            assert len(data) > 0

    # ------------------------------------------------------------------
    # docs://toronto/ckan-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ckan_guide_is_markdown(self):
        r = FunctionResource.from_function(
            toronto_ckan_guide, uri="docs://toronto/ckan-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "CKAN guide must start with # heading"

    @pytest.mark.asyncio
    async def test_ckan_guide_mentions_toronto(self):
        r = FunctionResource.from_function(
            toronto_ckan_guide, uri="docs://toronto/ckan-guide"
        )
        content = await r.read()
        assert "Toronto" in content

    # ------------------------------------------------------------------
    # docs://toronto/neighbourhood-profiles-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_neighbourhood_profiles_guide_is_markdown(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_profiles_guide, uri="docs://toronto/neighbourhood-profiles-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Neighbourhood profiles guide must start with # heading"

    @pytest.mark.asyncio
    async def test_neighbourhood_profiles_guide_mentions_140(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_profiles_guide, uri="docs://toronto/neighbourhood-profiles-guide"
        )
        content = await r.read()
        assert "140" in content

    # ------------------------------------------------------------------
    # docs://toronto/gtfs-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_gtfs_guide_is_markdown(self):
        r = FunctionResource.from_function(
            toronto_gtfs_guide, uri="docs://toronto/gtfs-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "GTFS guide must start with # heading"

    @pytest.mark.asyncio
    async def test_gtfs_guide_mentions_gtfs(self):
        r = FunctionResource.from_function(
            toronto_gtfs_guide, uri="docs://toronto/gtfs-guide"
        )
        content = await r.read()
        assert "GTFS" in content

    # ------------------------------------------------------------------
    # template://toronto/neighbourhood-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_neighbourhood_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_report_template, uri="template://toronto/neighbourhood-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Neighbourhood report template must start with # heading"

    @pytest.mark.asyncio
    async def test_neighbourhood_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            toronto_neighbourhood_report_template, uri="template://toronto/neighbourhood-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    # ------------------------------------------------------------------
    # Zero-param sanity
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            toronto_city_divisions,
            toronto_ward_list,
            toronto_neighbourhood_list,
            toronto_311_service_types,
            toronto_ckan_guide,
            toronto_neighbourhood_profiles_guide,
            toronto_gtfs_guide,
            toronto_neighbourhood_report_template,
        ]
        for fn in resources:
            sig = inspect.signature(fn)
            params = [
                name
                for name, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty
            ]
            assert params == [], (
                f"{fn.__name__} has required parameters {params}; "
                "resources must be zero-param functions"
            )
