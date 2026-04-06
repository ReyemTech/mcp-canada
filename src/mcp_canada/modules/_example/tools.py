"""Tools for the example module — demonstrates the 5-file pattern.

This module shows how Phase 2-4 API modules are structured:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response envelope (standard _meta wrapper)
- Keywords line in docstring for BM25 indexing (DISC-04)
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
