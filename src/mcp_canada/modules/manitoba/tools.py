"""Manitoba module tools.

All @tool definitions are added by Plans 02-06.
This file exists to satisfy FileSystemProvider discovery.

Tool naming convention: manitoba_ prefix.
Every @tool must include lang: Literal["en", "fr"] = "en".
Every @tool must return make_response() or make_error().
Every @tool docstring must have Use for: and Keywords: lines.
"""

from typing import Literal  # noqa: F401 — used by Plans 02-06

from fastmcp.tools import tool  # noqa: F401 — used by Plans 02-06

from mcp_canada.shared.envelope import make_error, make_response  # noqa: F401 — used by Plans 02-06

from . import client as _client  # noqa: F401 — used by Plans 02-06

# Tool definitions added by Plans 02-06.
