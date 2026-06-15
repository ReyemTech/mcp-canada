"""Saskatchewan module prompts.

All @prompt functions are defined by Plan 06.
This Wave 0 file imports the required standalone decorators.

IMPORTANT: Use standalone @prompt from fastmcp.prompts — NEVER @mcp.prompt.
Include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en"
on every @prompt function.

Guided workflow prompts return list[Message] (user + assistant roles).
Quick lookup prompts return str.
"""

from fastmcp.prompts import prompt
from fastmcp.prompts.prompt import Message

# Prompt definitions added by Plan 06.
