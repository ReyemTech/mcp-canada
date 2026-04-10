"""BC open data tools — Plan 02 adds 5 discovery tools, Plan 03 adds 15 curated WFS tools.

tools.py is edited by both Plan 02 and Plan 03, so they must be serialized:
Plan 02 first, Plan 03 depends_on Plan 02. FastMCP FileSystemProvider scans for
tools.py (not a tools/ package), so splitting is not an option.
"""

from fastmcp.tools import tool  # noqa: F401 — used by Plan 02/03 implementations
