"""Unit tests for new_brunswick/prompts.py and new_brunswick/resources.py.

Plan 03 fills both classes once the ~6 prompts and ~7 resources exist. Wave 0
only proves the two files import cleanly (exercised by the module-level
`test_module_scaffold_imports` below).
"""

from __future__ import annotations


def test_prompts_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import prompts  # noqa: F401


def test_resources_module_imports_cleanly():
    from mcp_canada.modules.new_brunswick import resources  # noqa: F401


class TestNbPrompts:
    """Plan 03 fills this — nb_flood_risk_assessment, nb_crown_land_report,
    nb_property_lookup, nb_quick_dataset_search, nb_health_facility_finder,
    nb_bilingual_dataset_lookup."""


class TestNbResources:
    """Plan 03 fills this — data://nb/geonb-services, data://nb/counties,
    data://nb/health-regions, data://nb/school-districts,
    docs://nb/portal-guide, docs://nb/geonb-query-guide,
    template://nb/flood-risk-report."""
