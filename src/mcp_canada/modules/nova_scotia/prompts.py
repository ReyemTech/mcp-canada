"""Nova Scotia module prompts — @prompt functions for the MCP server.

All prompts use standalone @prompt from fastmcp.prompts (NEVER @mcp.prompt).
All prompts include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en".
All prompts use the "ns_" prefix.

Guided workflow prompts (list[Message]) for multi-step tool chaining.
Quick lookup prompts (str) for single-tool instructions.

Prompt definitions are added by Plan 06.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.prompts import prompt  # noqa: F401 — used by Plan 06
from fastmcp.prompts.prompt import Message  # noqa: F401 — used by guided workflow prompts

# Prompt definitions added by Plan 06.
