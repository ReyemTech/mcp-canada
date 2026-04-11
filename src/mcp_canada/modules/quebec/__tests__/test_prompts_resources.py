"""Unit tests for quebec prompts and resources.

Plan 04 implements all 6 prompts and 7 resources.

Prompts:
  Guided workflows: quebec_explore_health, quebec_explore_transport_conditions,
                    quebec_explore_environment
  Quick lookups:    quebec_quick_dataset_search, quebec_check_road_conditions,
                    quebec_active_fires_now

Resources:
  data://quebec/ministries              — provincial ministries catalog (bilingual)
  data://quebec/regions                 — 17 administrative regions
  data://quebec/mrcs                    — regional county municipalities
  docs://quebec/catalog-federation-quirks  — 139-org federated nature + Montreal overlap
  docs://quebec/bilingual-metadata-guide   — French-primary DQ metadata explained
  template://quebec/dataset-report
  template://quebec/road-conditions-report
"""

import json

import pytest

from mcp_canada.modules.quebec import prompts as q_prompts
from mcp_canada.modules.quebec import resources as q_resources

pytestmark = pytest.mark.asyncio


class TestQuebecPrompts:
    async def test_explore_health_workflow(self):
        """quebec_explore_health returns list[Message] with 2 messages."""
        result = await q_prompts.quebec_explore_health()
        assert isinstance(result, list)
        assert len(result) >= 2
        roles = [m.role for m in result]
        assert "user" in roles
        assert "assistant" in roles

    async def test_explore_health_bilingual(self):
        """quebec_explore_health lang=fr returns French messages."""
        result = await q_prompts.quebec_explore_health(lang="fr")
        assert isinstance(result, list)
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert any(word in all_text for word in ["santé", "MSSS", "installation", "urgence"])

    async def test_explore_transport_conditions(self):
        """quebec_explore_transport_conditions returns list[Message] with 2 messages."""
        result = await q_prompts.quebec_explore_transport_conditions()
        assert isinstance(result, list)
        assert len(result) >= 2
        # Should mention road works or road conditions
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert any(word in all_text for word in ["road", "MTQ", "highway", "bridge", "Route"])

    async def test_explore_environment(self):
        """quebec_explore_environment returns list[Message] with 2 messages."""
        result = await q_prompts.quebec_explore_environment()
        assert isinstance(result, list)
        assert len(result) >= 2
        all_text = " ".join(m.content.text for m in result if hasattr(m.content, "text"))
        assert any(word in all_text for word in [
            "air quality", "environment", "water", "protected", "MELCCFP", "qualité"
        ])

    async def test_quick_dataset_search(self):
        """quebec_quick_dataset_search returns a str instruction."""
        result = await q_prompts.quebec_quick_dataset_search()
        assert isinstance(result, str)
        assert len(result) > 50
        assert "quebec_search_datasets" in result

    async def test_quick_dataset_search_fr(self):
        """quebec_quick_dataset_search lang=fr returns French instruction."""
        result = await q_prompts.quebec_quick_dataset_search(lang="fr")
        assert isinstance(result, str)
        assert any(word in result for word in ["rechercher", "Données Québec", "données"])

    async def test_check_road_conditions(self):
        """quebec_check_road_conditions returns a str instruction."""
        result = await q_prompts.quebec_check_road_conditions()
        assert isinstance(result, str)
        assert len(result) > 50
        assert "road" in result.lower() or "MTQ" in result or "route" in result.lower()

    async def test_active_fires_now(self):
        """quebec_active_fires_now returns a str directing agents to SOPFEU."""
        result = await q_prompts.quebec_active_fires_now()
        assert isinstance(result, str)
        assert len(result) > 30
        # Must mention SOPFEU or the external site since SOPFEU is not on DQ CKAN
        assert any(word in result for word in ["sopfeu", "SOPFEU", "sopfeu.qc.ca"])


class TestQuebecResources:
    async def test_ministries_json_valid(self):
        """data://quebec/ministries returns valid JSON list of ministry entries."""
        result = await q_resources.quebec_ministries()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0
        # Check structure of entries
        entry = parsed[0]
        assert "slug" in entry
        assert "name_en" in entry or "name_fr" in entry

    async def test_regions_catalog(self):
        """data://quebec/regions returns valid JSON with 17 Quebec admin regions."""
        result = await q_resources.quebec_regions()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        # Quebec has 17 administrative regions
        assert len(parsed) == 17
        entry = parsed[0]
        assert "code" in entry or "region_code" in entry or "slug" in entry

    async def test_mrcs_catalog(self):
        """data://quebec/mrcs returns valid JSON list of MRC entries."""
        result = await q_resources.quebec_mrcs()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    async def test_catalog_federation_quirks_docs(self):
        """docs://quebec/catalog-federation-quirks returns markdown string."""
        result = await q_resources.quebec_catalog_federation_quirks()
        assert isinstance(result, str)
        assert len(result) > 100
        # Should mention the federated nature and Montreal
        assert any(word in result for word in ["federated", "139", "Montreal", "Montréal", "fédéré"])

    async def test_bilingual_metadata_guide_docs(self):
        """docs://quebec/bilingual-metadata-guide returns markdown string."""
        result = await q_resources.quebec_bilingual_metadata_guide()
        assert isinstance(result, str)
        assert len(result) > 100
        # Should explain French-primary nature
        assert any(word in result for word in ["French", "français", "title", "metadata"])

    async def test_dataset_report_template(self):
        """template://quebec/dataset-report returns markdown template string."""
        result = await q_resources.quebec_dataset_report_template()
        assert isinstance(result, str)
        assert len(result) > 50
        # Template should have placeholder syntax
        assert "{" in result or "##" in result

    async def test_road_conditions_report_template(self):
        """template://quebec/road-conditions-report returns markdown template string."""
        result = await q_resources.quebec_road_conditions_report_template()
        assert isinstance(result, str)
        assert len(result) > 50
        assert "{" in result or "##" in result
