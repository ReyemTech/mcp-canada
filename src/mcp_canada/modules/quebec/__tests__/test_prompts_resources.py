"""Unit tests for quebec prompts and resources.

Wave 0 scaffolds — all test bodies are pytest.skip("Plan 04 implements").
Plan 04 populates all 6 prompts and 7 resources, then fills these test bodies.

Prompts (Plan 04):
  Guided workflows: quebec_explore_health, quebec_explore_transport_conditions,
                    quebec_explore_environment
  Quick lookups:    quebec_quick_dataset_search, quebec_check_road_conditions,
                    quebec_active_fires_now

Resources (Plan 04):
  data://quebec/ministries              — provincial ministries catalog (bilingual)
  data://quebec/regions                 — 17 administrative regions
  data://quebec/mrcs                    — regional county municipalities
  docs://quebec/catalog-federation-quirks  — 139-org federated nature + Montreal overlap
  docs://quebec/bilingual-metadata-guide   — French-primary DQ metadata explained
  template://quebec/dataset-report
  template://quebec/road-conditions-report
"""

import pytest

pytestmark = pytest.mark.asyncio


class TestQuebecPrompts:
    async def test_explore_health_workflow(self):
        pytest.skip("Plan 04")

    async def test_explore_transport_conditions(self):
        pytest.skip("Plan 04")

    async def test_explore_environment(self):
        pytest.skip("Plan 04")

    async def test_quick_dataset_search(self):
        pytest.skip("Plan 04")

    async def test_check_road_conditions(self):
        pytest.skip("Plan 04")

    async def test_active_fires_now(self):
        pytest.skip("Plan 04")


class TestQuebecResources:
    def test_ministries_json_valid(self):
        pytest.skip("Plan 04")

    def test_regions_catalog(self):
        pytest.skip("Plan 04")

    def test_mrcs_catalog(self):
        pytest.skip("Plan 04")

    def test_catalog_federation_quirks_docs(self):
        pytest.skip("Plan 04")

    def test_bilingual_metadata_guide_docs(self):
        pytest.skip("Plan 04")

    def test_dataset_report_template(self):
        pytest.skip("Plan 04")

    def test_road_conditions_report_template(self):
        pytest.skip("Plan 04")
