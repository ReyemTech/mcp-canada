"""Saskatchewan module resources.

All @resource functions are defined by Plan 06.
This Wave 0 file imports the required standalone decorators.

IMPORTANT: Use standalone @resource from fastmcp.resources — NEVER @mcp.resource.
Resource functions must have ZERO function parameters — any parameter (including lang)
promotes the function to ResourceTemplate and removes it from resources/list.

URI scheme conventions:
  data://   — JSON catalogs (return json.dumps(...))
  docs://   — Markdown guides (return raw markdown string)
  template:// — Markdown templates with {placeholder} syntax

All URIs use saskatchewan/ path prefix (e.g. data://saskatchewan/crop-regions).
"""

import json

from fastmcp.resources import resource

# Resource definitions added by Plan 06.
