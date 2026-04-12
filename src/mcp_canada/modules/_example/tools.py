"""Tools for the example module — demonstrates the 7-file pattern.

Private fixture — see ``__init__.py`` for why this module is underscore-prefixed
and excluded from production registration.

This file shows how production modules structure their @tool functions:
- Standalone @tool decorator from ``fastmcp.tools`` (NEVER @mcp.tool)
- Bilingual lang: Literal["en", "fr"] = "en" parameter
- make_response envelope (standard _meta wrapper)
- ``Use for:`` + ``Keywords:`` lines in docstring for BM25 indexing (minimum 8 keywords)
- Module prefix on the tool name (example_, boc_, quebec_, etc.)
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_response
from mcp_canada.modules._example.client import fetch_echo


@tool
async def example_echo(
    message: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Echo a message back in the requested language using the example API.

    Use for: testing auto-registry, verifying bilingual support, checking tool discovery.
    Keywords: echo, test, example, bilingual, lang, message, en, fr.
    """
    data = await fetch_echo(message, lang=lang)
    return make_response(
        data,
        api_name="example",
        api_url="internal://example",
        cached=False,
        lang=lang,
    )
