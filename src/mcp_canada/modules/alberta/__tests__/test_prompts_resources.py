"""Unit tests for alberta prompts and resources.

Plan 08 implements all 6 prompts and 7 resources.

Prompts:
  Guided workflows: alberta_explore_energy, alberta_explore_wildfires,
                    alberta_explore_health_or_transport
  Quick lookups:    alberta_quick_dataset_search, alberta_check_road_conditions,
                    alberta_active_fires_now

Resources:
  data://alberta/ministries         — 14 provincial ministry slugs + bilingual labels
  data://alberta/forest-areas       — 10 Wildfire Forest Areas (hectares)
  data://alberta/ahs-zones          — 5 AHS zones + POP2006/2011/2016
  docs://alberta/aer-data-guide     — AER static reports (ST1/ST3/ST39) → tool mapping
  docs://alberta/wildfire-data-guide — WMBappServices vs CKAN + AB-23 water-licence guidance
  template://alberta/dataset-report
  template://alberta/wildfire-report
"""

from __future__ import annotations

import json

import pytest

from mcp_canada.modules.alberta import prompts as a_prompts
from mcp_canada.modules.alberta import resources as a_resources

pytestmark = pytest.mark.asyncio


class TestAlbertaPrompts:
    async def test_six_prompts_registered(self):
        """All 6 @prompt functions are importable from prompts module."""
        expected = [
            "alberta_explore_energy",
            "alberta_explore_wildfires",
            "alberta_explore_health_or_transport",
            "alberta_quick_dataset_search",
            "alberta_check_road_conditions",
            "alberta_active_fires_now",
        ]
        for name in expected:
            assert hasattr(a_prompts, name), f"prompts module missing {name}"

    async def test_explore_energy_workflow(self):
        """alberta_explore_energy returns list[Message] with user + assistant roles."""
        result = await a_prompts.alberta_explore_energy()
        assert isinstance(result, list)
        assert len(result) >= 2
        roles = [m.role for m in result]
        assert "user" in roles
        assert "assistant" in roles

    async def test_explore_energy_references_aer_tools(self):
        """alberta_explore_energy assistant message references AER tool names."""
        result = await a_prompts.alberta_explore_energy()
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        # Must reference multiple AER tools
        assert "alberta_get_well_licences_today" in all_text
        assert "alberta_get_production_volumes" in all_text
        assert "alberta_get_pipeline_statistics" in all_text

    async def test_explore_energy_bilingual(self):
        """alberta_explore_energy lang=fr returns French content distinct from English."""
        en = await a_prompts.alberta_explore_energy(lang="en")
        fr = await a_prompts.alberta_explore_energy(lang="fr")
        en_text = " ".join(m.content.text for m in en if hasattr(m.content, "text"))
        fr_text = " ".join(m.content.text for m in fr if hasattr(m.content, "text"))
        assert en_text != fr_text
        # French content should contain French vocabulary
        assert any(word in fr_text for word in ["énergétiques", "pétrole", "pipelines", "étape"])

    async def test_explore_wildfires_workflow(self):
        """alberta_explore_wildfires returns list[Message] with 2+ messages referencing WMB tools."""
        result = await a_prompts.alberta_explore_wildfires()
        assert isinstance(result, list)
        assert len(result) >= 2
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert "alberta_get_active_fires" in all_text
        assert "alberta_get_fire_perimeters" in all_text
        assert "alberta_get_fire_bans" in all_text

    async def test_explore_health_or_transport_branched(self):
        """alberta_explore_health_or_transport surfaces both health and transport branches."""
        result = await a_prompts.alberta_explore_health_or_transport()
        assert isinstance(result, list)
        assert len(result) >= 2
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        # Health tools
        assert "alberta_get_hospitals" in all_text
        assert "alberta_get_ahs_zones" in all_text
        # Transport tools
        assert "alberta_get_road_events" in all_text
        assert "alberta_get_winter_road_conditions" in all_text

    async def test_quick_dataset_search(self):
        """alberta_quick_dataset_search returns a str instruction referencing the search tool."""
        result = await a_prompts.alberta_quick_dataset_search()
        assert isinstance(result, str)
        assert len(result) > 100
        assert "alberta_search_datasets" in result

    async def test_quick_dataset_search_fr(self):
        """alberta_quick_dataset_search lang=fr returns French instruction."""
        result = await a_prompts.alberta_quick_dataset_search(lang="fr")
        assert isinstance(result, str)
        assert any(word in result for word in ["rechercher", "catalogue", "ministère"])

    async def test_check_road_conditions(self):
        """alberta_check_road_conditions returns a str referencing 511 tools."""
        result = await a_prompts.alberta_check_road_conditions()
        assert isinstance(result, str)
        assert len(result) > 100
        assert "alberta_get_road_events" in result
        assert "alberta_get_winter_road_conditions" in result

    async def test_active_fires_now(self):
        """alberta_active_fires_now returns a str directing to alberta_get_active_fires."""
        result = await a_prompts.alberta_active_fires_now()
        assert isinstance(result, str)
        assert len(result) > 50
        assert "alberta_get_active_fires" in result


class TestAlbertaResources:  # Plan 08 Task 2 — filled below after resources.py
    pass
