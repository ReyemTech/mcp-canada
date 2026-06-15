"""Nova Scotia module tools — @tool functions for the MCP server.

All tools use standalone @tool from fastmcp.tools (NEVER @mcp.tool).
All tools include lang: Literal["en", "fr"] = "en" parameter.
All tools return make_response() on success, make_error() on failure.
All tools use the "ns_" prefix.

Tool definitions are added by Plans 02-05.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import tool  # noqa: F401 — used by Plans 02-05

from mcp_canada.shared.envelope import make_error, make_response  # noqa: F401
from mcp_canada.shared import socrata  # noqa: F401 — used by discovery tools in Plan 02

from . import client as _client  # noqa: F401 — used by all tool implementations

# Tool definitions added by Plans 02-05.
