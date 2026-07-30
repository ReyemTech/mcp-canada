"""New Brunswick module resources — @resource functions (catalogs, docs, templates).

Plan 03 owns this file's ~7 resources (data://nb/geonb-services,
data://nb/counties, data://nb/health-regions, data://nb/school-districts,
docs://nb/portal-guide, docs://nb/geonb-query-guide,
template://nb/flood-risk-report — see 21-01-PLAN.md "Artifacts this phase
produces"). Wave 0 declares the imports only.
"""

import json  # noqa: F401 — used by Plan 03

from fastmcp.resources import resource  # noqa: F401 — used by Plan 03
