"""Manitoba module prompts.

All @prompt definitions are added by Plan 07.
This file exists to satisfy FileSystemProvider discovery.

Prompt naming convention: manitoba_ prefix.
Every @prompt must include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en".
Guided workflow prompts return list[Message]; quick lookup prompts return str.
"""

from typing import Annotated, Literal  # noqa: F401 — used by Plan 07

from fastmcp.prompts import prompt  # noqa: F401 — used by Plan 07
from fastmcp.prompts.prompt import Message  # noqa: F401 — used by Plan 07

# Prompt definitions added by Plan 07.
