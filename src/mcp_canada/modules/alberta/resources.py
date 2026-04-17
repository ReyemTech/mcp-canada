"""Alberta resources — 7 zero-parameter resources — Plan 08 fills bodies.

Resource catalog (type-prefixed URIs per CLAUDE.md convention):

  data://alberta/ministries         — 14 provincial ministry org slugs + bilingual labels
  data://alberta/forest-areas       — 10 Alberta Wildfire Forest Areas (FA_NAME + area)
  data://alberta/ahs-zones          — 5 AHS zones (South, Calgary, Central, Edmonton, North)
  docs://alberta/aer-data-guide     — markdown explaining AER surfaces (ST1/ST3/ST39/OneStop)
  docs://alberta/wildfire-data-guide — markdown on incident/perimeter/ban distinctions
  template://alberta/dataset-report — response formatting template
  template://alberta/wildfire-report — wildfire-specific response template

IMPORTANT: Every resource MUST be zero-parameter (no `lang` param — that would
promote it to a ResourceTemplate and remove it from resources/list). Bilingual
content is embedded inline (both en and fr in the same JSON / markdown body).
"""

import json  # noqa: F401 — used by Plan 08 for data:// resources

from fastmcp.resources import resource  # noqa: F401 — used by Plan 08


__all__ = [
    "alberta_ministries",
    "alberta_forest_areas",
    "alberta_ahs_zones",
    "alberta_aer_data_guide",
    "alberta_wildfire_data_guide",
    "alberta_dataset_report_template",
    "alberta_wildfire_report_template",
]


# ---------------------------------------------------------------------------
# data:// resources — JSON catalogs (Plan 08)
# ---------------------------------------------------------------------------

# Plan 08 defines:
#   @resource(uri="data://alberta/ministries")
#   def alberta_ministries() -> str: return json.dumps({...})
#
#   @resource(uri="data://alberta/forest-areas")
#   def alberta_forest_areas() -> str: return json.dumps({...})
#
#   @resource(uri="data://alberta/ahs-zones")
#   def alberta_ahs_zones() -> str: return json.dumps({...})


# ---------------------------------------------------------------------------
# docs:// resources — markdown guides (Plan 08)
# ---------------------------------------------------------------------------

# Plan 08 defines:
#   @resource(uri="docs://alberta/aer-data-guide")
#   def alberta_aer_data_guide() -> str: return "..."
#
#   @resource(uri="docs://alberta/wildfire-data-guide")
#   def alberta_wildfire_data_guide() -> str: return "..."


# ---------------------------------------------------------------------------
# template:// resources — markdown response templates (Plan 08)
# ---------------------------------------------------------------------------

# Plan 08 defines:
#   @resource(uri="template://alberta/dataset-report")
#   def alberta_dataset_report_template() -> str: return "..."
#
#   @resource(uri="template://alberta/wildfire-report")
#   def alberta_wildfire_report_template() -> str: return "..."
