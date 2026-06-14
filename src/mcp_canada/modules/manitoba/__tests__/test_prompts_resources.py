"""Manitoba prompts and resources unit tests.

Plan 07 implements all 6 prompts and 7 resources.

Prompts:
  Guided workflows: manitoba_explore_flood_or_water,
                    manitoba_explore_transport,
                    manitoba_explore_agriculture_or_health
  Quick lookups:    manitoba_quick_dataset_search,
                    manitoba_check_road_conditions,
                    manitoba_flood_outlook_now

Resources:
  data://manitoba/departments       — provincial ministries with bilingual labels
  data://manitoba/health-regions    — 5 RHAs (WRHA, PMH, IERHA, SHSS, NHR)
  data://manitoba/major-rivers      — Red, Assiniboine, Winnipeg, Souris + floodway
  docs://manitoba/flood-data-guide  — flood-outlook vs river-level vs forecast distinctions
  docs://manitoba/portal-guide      — geoportal.gov.mb.ca ArcGIS Hub + OpenMB licence
  template://manitoba/dataset-report
  template://manitoba/flood-report
"""

from __future__ import annotations

import json

import pytest

from mcp_canada.modules.manitoba import prompts as m_prompts
from mcp_canada.modules.manitoba import resources as m_resources

pytestmark = pytest.mark.asyncio


class TestManitobaPrompts:
    """Unit tests for all Manitoba @prompt functions."""

    async def test_six_prompts_registered(self):
        """All 6 @prompt functions are importable from prompts module."""
        expected = [
            "manitoba_explore_flood_or_water",
            "manitoba_explore_transport",
            "manitoba_explore_agriculture_or_health",
            "manitoba_quick_dataset_search",
            "manitoba_check_road_conditions",
            "manitoba_flood_outlook_now",
        ]
        for name in expected:
            assert hasattr(m_prompts, name), f"prompts module missing {name}"

    # -------------------------------------------------------------------------
    # Guided workflow: explore_flood_or_water
    # -------------------------------------------------------------------------

    async def test_explore_flood_or_water_is_guided_workflow(self):
        """manitoba_explore_flood_or_water returns list[Message] with user + assistant roles."""
        result = await m_prompts.manitoba_explore_flood_or_water()
        assert isinstance(result, list)
        assert len(result) >= 2
        roles = [m.role for m in result]
        assert "user" in roles
        assert "assistant" in roles

    async def test_explore_flood_or_water_references_flood_tools(self):
        """manitoba_explore_flood_or_water assistant message references flood tool names."""
        result = await m_prompts.manitoba_explore_flood_or_water()
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "manitoba_get_flood_alerts" in all_text
        assert "manitoba_get_river_stations" in all_text
        assert "manitoba_get_provincial_waterways" in all_text

    async def test_explore_flood_or_water_bilingual(self):
        """manitoba_explore_flood_or_water lang=fr returns French content distinct from English."""
        en = await m_prompts.manitoba_explore_flood_or_water(lang="en")
        fr = await m_prompts.manitoba_explore_flood_or_water(lang="fr")
        en_text = " ".join(m.content.text for m in en if hasattr(m.content, "text"))
        fr_text = " ".join(m.content.text for m in fr if hasattr(m.content, "text"))
        assert en_text != fr_text
        assert any(word in fr_text for word in ["inondation", "rivière", "alerte", "eau"])

    # -------------------------------------------------------------------------
    # Guided workflow: explore_transport
    # -------------------------------------------------------------------------

    async def test_explore_transport_is_guided_workflow(self):
        """manitoba_explore_transport returns list[Message] with 2+ messages."""
        result = await m_prompts.manitoba_explore_transport()
        assert isinstance(result, list)
        assert len(result) >= 2
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "manitoba_get_road_events" in all_text
        assert "manitoba_get_winter_road_conditions" in all_text
        assert "manitoba_get_traffic_cameras" in all_text

    async def test_explore_transport_mentions_key_requirement(self):
        """manitoba_explore_transport notes the 511 key requirement."""
        result = await m_prompts.manitoba_explore_transport()
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert any(word in all_text for word in ["NOT_CONFIGURED", "key", "clé", "API key"])

    async def test_explore_transport_bilingual(self):
        """manitoba_explore_transport lang=fr returns French content distinct from English."""
        en = await m_prompts.manitoba_explore_transport(lang="en")
        fr = await m_prompts.manitoba_explore_transport(lang="fr")
        en_text = " ".join(m.content.text for m in en if hasattr(m.content, "text"))
        fr_text = " ".join(m.content.text for m in fr if hasattr(m.content, "text"))
        assert en_text != fr_text
        assert any(word in fr_text for word in ["routier", "conditions", "transport", "caméras"])

    # -------------------------------------------------------------------------
    # Guided workflow: explore_agriculture_or_health
    # -------------------------------------------------------------------------

    async def test_explore_agriculture_or_health_is_guided_workflow(self):
        """manitoba_explore_agriculture_or_health returns list[Message] with 2+ messages."""
        result = await m_prompts.manitoba_explore_agriculture_or_health()
        assert isinstance(result, list)
        assert len(result) >= 2
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "manitoba_get_drought_status" in all_text
        assert "manitoba_get_livestock_prices" in all_text
        assert "manitoba_get_surgical_wait_times" in all_text
        assert "manitoba_get_health_facilities" in all_text

    async def test_explore_agriculture_or_health_bilingual(self):
        """manitoba_explore_agriculture_or_health lang=fr returns French content."""
        en = await m_prompts.manitoba_explore_agriculture_or_health(lang="en")
        fr = await m_prompts.manitoba_explore_agriculture_or_health(lang="fr")
        en_text = " ".join(m.content.text for m in en if hasattr(m.content, "text"))
        fr_text = " ".join(m.content.text for m in fr if hasattr(m.content, "text"))
        assert en_text != fr_text
        assert any(word in fr_text for word in ["agriculture", "santé", "bétail", "sécheresse"])

    # -------------------------------------------------------------------------
    # Quick lookup: quick_dataset_search
    # -------------------------------------------------------------------------

    async def test_quick_dataset_search_returns_str(self):
        """manitoba_quick_dataset_search returns a str instruction referencing the search tool."""
        result = await m_prompts.manitoba_quick_dataset_search()
        assert isinstance(result, str)
        assert len(result) > 100
        assert "manitoba_search_datasets" in result

    async def test_quick_dataset_search_fr(self):
        """manitoba_quick_dataset_search lang=fr returns French instruction."""
        result = await m_prompts.manitoba_quick_dataset_search(lang="fr")
        assert isinstance(result, str)
        assert any(word in result for word in ["rechercher", "catalogue", "géoportail", "jeux de données"])

    # -------------------------------------------------------------------------
    # Quick lookup: check_road_conditions
    # -------------------------------------------------------------------------

    async def test_check_road_conditions_returns_str(self):
        """manitoba_check_road_conditions returns a str referencing 511 tools."""
        result = await m_prompts.manitoba_check_road_conditions()
        assert isinstance(result, str)
        assert len(result) > 100
        assert "manitoba_get_winter_road_conditions" in result

    async def test_check_road_conditions_mentions_not_configured(self):
        """manitoba_check_road_conditions mentions NOT_CONFIGURED for missing 511 key."""
        result = await m_prompts.manitoba_check_road_conditions()
        assert "NOT_CONFIGURED" in result or "key" in result.lower()

    async def test_check_road_conditions_fr(self):
        """manitoba_check_road_conditions lang=fr returns French instruction."""
        result = await m_prompts.manitoba_check_road_conditions(lang="fr")
        assert isinstance(result, str)
        assert any(word in result for word in ["routières", "conditions", "hivernales", "clé"])

    # -------------------------------------------------------------------------
    # Quick lookup: flood_outlook_now
    # -------------------------------------------------------------------------

    async def test_flood_outlook_now_returns_str(self):
        """manitoba_flood_outlook_now returns a str directing to flood alert tool."""
        result = await m_prompts.manitoba_flood_outlook_now()
        assert isinstance(result, str)
        assert len(result) > 50
        assert "manitoba_get_flood_alerts" in result

    async def test_flood_outlook_now_fr(self):
        """manitoba_flood_outlook_now lang=fr returns French instruction."""
        result = await m_prompts.manitoba_flood_outlook_now(lang="fr")
        assert isinstance(result, str)
        assert any(word in result for word in ["inondation", "alerte", "rivière", "surveillance"])


class TestManitobaResources:
    """Unit tests for all Manitoba @resource functions."""

    async def test_seven_resources_registered(self):
        """All 7 @resource functions are importable from resources module."""
        expected = [
            "manitoba_departments",
            "manitoba_health_regions",
            "manitoba_major_rivers",
            "manitoba_flood_data_guide",
            "manitoba_portal_guide",
            "manitoba_dataset_report_template",
            "manitoba_flood_report_template",
        ]
        for name in expected:
            assert hasattr(m_resources, name), f"resources module missing {name}"

    # -------------------------------------------------------------------------
    # data://manitoba/departments
    # -------------------------------------------------------------------------

    async def test_departments_returns_valid_json(self):
        """data://manitoba/departments returns valid JSON with departments list."""
        result = await m_resources.manitoba_departments()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "departments" in parsed
        assert len(parsed["departments"]) >= 5
        first = parsed["departments"][0]
        assert "name_en" in first
        assert "name_fr" in first

    async def test_departments_has_bilingual_labels(self):
        """data://manitoba/departments includes both English and French names."""
        result = await m_resources.manitoba_departments()
        parsed = json.loads(result)
        for dept in parsed["departments"]:
            assert dept.get("name_en"), f"Missing name_en in {dept}"
            assert dept.get("name_fr"), f"Missing name_fr in {dept}"

    async def test_departments_has_data_domains(self):
        """data://manitoba/departments includes data_domains field per entry."""
        result = await m_resources.manitoba_departments()
        parsed = json.loads(result)
        for dept in parsed["departments"]:
            assert "data_domains" in dept, f"Missing data_domains in {dept}"

    # -------------------------------------------------------------------------
    # data://manitoba/health-regions
    # -------------------------------------------------------------------------

    async def test_health_regions_returns_valid_json(self):
        """data://manitoba/health-regions returns JSON with exactly 5 RHAs."""
        result = await m_resources.manitoba_health_regions()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "health_regions" in parsed
        assert len(parsed["health_regions"]) == 5

    async def test_health_regions_contains_known_rhas(self):
        """data://manitoba/health-regions includes WRHA and other known RHAs."""
        result = await m_resources.manitoba_health_regions()
        parsed = json.loads(result)
        short_names = {r["short_name"] for r in parsed["health_regions"]}
        assert "WRHA" in short_names
        assert "PMH" in short_names
        assert "IERHA" in short_names
        assert "SHSS" in short_names
        assert "NHR" in short_names

    async def test_health_regions_has_major_hospitals(self):
        """data://manitoba/health-regions includes major_hospitals field for each RHA."""
        result = await m_resources.manitoba_health_regions()
        parsed = json.loads(result)
        for rha in parsed["health_regions"]:
            assert "major_hospitals" in rha, f"Missing major_hospitals in {rha['short_name']}"

    async def test_health_regions_wrha_has_hsc(self):
        """WRHA entry lists Health Sciences Centre as a major hospital."""
        result = await m_resources.manitoba_health_regions()
        parsed = json.loads(result)
        wrha = next(r for r in parsed["health_regions"] if r["short_name"] == "WRHA")
        hospitals = " ".join(wrha["major_hospitals"])
        assert "Health Sciences Centre" in hospitals or "HSC" in hospitals

    # -------------------------------------------------------------------------
    # data://manitoba/major-rivers
    # -------------------------------------------------------------------------

    async def test_major_rivers_returns_valid_json(self):
        """data://manitoba/major-rivers returns valid JSON with rivers list."""
        result = await m_resources.manitoba_major_rivers()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "rivers" in parsed
        assert len(parsed["rivers"]) >= 4

    async def test_major_rivers_includes_red_river(self):
        """data://manitoba/major-rivers includes the Red River with flood risk info."""
        result = await m_resources.manitoba_major_rivers()
        parsed = json.loads(result)
        river_names = {r["name"] for r in parsed["rivers"]}
        assert "Red River" in river_names
        red = next(r for r in parsed["rivers"] if r["name"] == "Red River")
        assert "flood_risk" in red

    async def test_major_rivers_includes_floodway(self):
        """data://manitoba/major-rivers includes the Red River Floodway."""
        result = await m_resources.manitoba_major_rivers()
        parsed = json.loads(result)
        names = {r["name"] for r in parsed["rivers"]}
        assert any("Floodway" in n or "floodway" in n.lower() for n in names)

    async def test_major_rivers_includes_assiniboine(self):
        """data://manitoba/major-rivers includes the Assiniboine River."""
        result = await m_resources.manitoba_major_rivers()
        parsed = json.loads(result)
        river_names = {r["name"] for r in parsed["rivers"]}
        assert "Assiniboine River" in river_names

    # -------------------------------------------------------------------------
    # docs://manitoba/flood-data-guide
    # -------------------------------------------------------------------------

    async def test_flood_data_guide_returns_markdown(self):
        """docs://manitoba/flood-data-guide returns non-empty markdown with tool references."""
        result = await m_resources.manitoba_flood_data_guide()
        assert isinstance(result, str)
        assert result.startswith("#")
        assert len(result) > 300
        assert "manitoba_get_flood_alerts" in result

    async def test_flood_data_guide_bilingual_content(self):
        """docs://manitoba/flood-data-guide includes both English and French sections."""
        result = await m_resources.manitoba_flood_data_guide()
        assert "English" in result or "## English" in result
        assert "Français" in result or "## Français" in result

    async def test_flood_data_guide_distinguishes_data_sources(self):
        """docs://manitoba/flood-data-guide explains ArcGIS Hub vs HFC PDF distinction."""
        result = await m_resources.manitoba_flood_data_guide()
        # Must help agents understand what's machine-readable
        assert any(word in result for word in ["ArcGIS", "FeatureServer", "PDF", "HFC"])

    # -------------------------------------------------------------------------
    # docs://manitoba/portal-guide
    # -------------------------------------------------------------------------

    async def test_portal_guide_returns_markdown(self):
        """docs://manitoba/portal-guide returns markdown referencing geoportal.gov.mb.ca."""
        result = await m_resources.manitoba_portal_guide()
        assert isinstance(result, str)
        assert result.startswith("#")
        assert len(result) > 300
        assert "geoportal.gov.mb.ca" in result

    async def test_portal_guide_mentions_openmb_licence(self):
        """docs://manitoba/portal-guide mentions OpenMB licence."""
        result = await m_resources.manitoba_portal_guide()
        assert "OpenMB" in result or "openmb" in result.lower()

    async def test_portal_guide_mentions_mli_deprecation(self):
        """docs://manitoba/portal-guide notes MLI retirement."""
        result = await m_resources.manitoba_portal_guide()
        assert "MLI" in result or "mli.gov.mb.ca" in result or "retired" in result.lower()

    # -------------------------------------------------------------------------
    # template://manitoba/dataset-report
    # -------------------------------------------------------------------------

    async def test_dataset_report_template_has_placeholders(self):
        """template://manitoba/dataset-report returns markdown with {placeholder} syntax."""
        result = await m_resources.manitoba_dataset_report_template()
        assert isinstance(result, str)
        assert result.startswith("#")
        assert "{" in result and "}" in result
        assert "{dataset_title}" in result or "{search_query}" in result

    # -------------------------------------------------------------------------
    # template://manitoba/flood-report
    # -------------------------------------------------------------------------

    async def test_flood_report_template_has_placeholders(self):
        """template://manitoba/flood-report returns markdown with {placeholder} syntax."""
        result = await m_resources.manitoba_flood_report_template()
        assert isinstance(result, str)
        assert result.startswith("#")
        assert "{" in result and "}" in result
        assert "{report_date}" in result or "{alert_count}" in result
