"""Quebec resources — populated in Plan 04.

Static catalogs (Plan 04):
  data://quebec/ministries   — provincial ministries with bilingual labels
  data://quebec/regions      — 17 administrative regions
  data://quebec/mrcs         — regional county municipalities (MRCs)

Documentation guides (Plan 04):
  docs://quebec/catalog-federation-quirks  — 139-org federated nature + Montreal overlap
  docs://quebec/bilingual-metadata-guide   — French-primary DQ metadata explained

Templates (Plan 04):
  template://quebec/dataset-report
  template://quebec/road-conditions-report
"""

import json

from fastmcp.resources import resource

__all__: list[str] = []
