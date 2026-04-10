"""BC open data resources — 7 static resources populated in Plan 04.

Resources provide agents with reference data and documentation:
- data://bc/ministries — BC ministry/agency catalog (JSON)
- data://bc/wildfire-status-codes — fire status code reference (JSON)
- data://bc/object-name-prefixes — BCGW schema prefix reference (JSON)
- docs://bc/wfs-query-guide — CKAN→WFS two-step workflow guide (Markdown)
- docs://bc/bcdc-api-quirks — BC Data Catalogue API notes (Markdown)
- template://bc/wildfire-report — wildfire analysis report template (Markdown)
- template://bc/dataset-report — dataset exploration report template (Markdown)
"""

import json  # noqa: F401 — used by Plan 04 implementations

from fastmcp.resources import resource  # noqa: F401 — used by Plan 04 implementations
