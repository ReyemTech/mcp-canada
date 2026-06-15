"""Saskatchewan module tools.

All @tool functions are defined by Plans 02-05.
This Wave 0 file imports the required standalone decorators and shared utilities.

IMPORTANT: Use standalone @tool from fastmcp.tools — NEVER @mcp.tool.
FileSystemProvider requires standalone decorators for auto-registration.
"""

from typing import Annotated, Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client

# Tool definitions added by Plans 02-05.
# Each @tool must:
#   1. Use standalone @tool (not @mcp.tool)
#   2. Include lang: Literal["en", "fr"] = "en" parameter
#   3. Return make_response() on success, make_error() on failure
#   4. Have Use for: + Keywords: in docstring (BM25 discovery)
#   5. Use saskatchewan_ prefix
