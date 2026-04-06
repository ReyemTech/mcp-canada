"""plan_query meta-tool — maps a natural language query to a multi-API execution plan."""

from pathlib import Path
from typing import Literal

from fastmcp.server.providers import FileSystemProvider
from fastmcp.server.transforms.search.bm25 import _BM25Index
from fastmcp.server.transforms.search.base import _extract_searchable_text
from fastmcp.tools import tool
from fastmcp.tools.base import Tool

from mcp_canada.shared.envelope import make_response

# Path to the modules directory — relative to this file's parent's parent
_MODULES_DIR = Path(__file__).parent.parent / "modules"


@tool(name="plan_query", tags={"meta", "planning", "discovery"})
async def plan_query(
    query: str,
    top_k: int = 5,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Plan a multi-step query across Canadian government data APIs.

    Returns a structured execution plan with the most relevant tool names for
    the given natural language question. Use execute_batch to run the plan.

    Use for: orchestrating queries that span multiple data sources, finding
    which tools to use for a complex question, multi-API planning, cross-module
    queries, batch query preparation.

    Keywords: plan, query, multi-step, orchestrate, batch, cross-module,
    execution plan, tool selection, NL query, natural language, discover,
    which tools, what tools, how to query, planning, workflow
    """
    # Build BM25 index from raw module providers, bypassing BM25SearchTransform.
    # This avoids Pitfall 4: ctx.fastmcp.list_tools() goes through the transform
    # and returns only the always-visible tools (not the full catalog).
    provider = FileSystemProvider(root=_MODULES_DIR)
    tools: list[Tool] = [
        c for c in provider._components.values() if isinstance(c, Tool)
    ]

    if not tools:
        return make_response(
            {"steps": [], "explanation": f"No tools available to match: {query}"},
            api_name="mcp-canada",
            api_url="internal://plan_query",
            cached=False,
            lang=lang,
        )

    # Build searchable text for each tool (name + description + params)
    texts = [_extract_searchable_text(t) for t in tools]

    # Build BM25 index and query
    index = _BM25Index()
    index.build(texts)
    indices = index.query(query, top_k=top_k)

    # Map indices back to Tool objects
    matched = [tools[i] for i in indices]

    steps = [{"tool": t.name, "params": {}} for t in matched]
    explanation = (
        f"Found {len(matched)} tools matching: {query}"
        if matched
        else f"No tools matched the query: {query}"
    )

    return make_response(
        {"steps": steps, "explanation": explanation},
        api_name="mcp-canada",
        api_url="internal://plan_query",
        cached=False,
        lang=lang,
    )
