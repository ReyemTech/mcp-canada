"""Nova Scotia module resources — @resource functions for the MCP server.

All resources use standalone @resource from fastmcp.resources (NEVER @mcp.resource).
Resources have ZERO function parameters — any parameter (including lang) promotes
the function to ResourceTemplate and removes it from resources/list.

URI scheme conventions:
  data:// — JSON catalogs (bilingual content inline)
  docs:// — Markdown guides
  template:// — Markdown templates with {placeholder} syntax

Resource definitions are added by Plan 06.
"""

from __future__ import annotations

import json  # noqa: F401 — used by data:// resources

from fastmcp.resources import resource  # noqa: F401 — used by Plan 06

# Resource definitions added by Plan 06.
