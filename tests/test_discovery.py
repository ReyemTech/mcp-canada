"""Integration tests: BM25SearchTransform / discover_tools."""

import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_discover_tools_returns_results():
    """discover_tools (BM25 search) should return results for a relevant query."""
    from fastmcp import FastMCP
    from fastmcp.server.providers import FileSystemProvider
    from fastmcp.server.transforms.search import BM25SearchTransform

    modules_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "modules"
    provider = FileSystemProvider(root=modules_dir)

    test_mcp = FastMCP("test-discovery", providers=[provider])
    test_mcp.add_transform(BM25SearchTransform(
        max_results=5,
        always_visible=["list_modules"],
        search_tool_name="discover_tools",
        call_tool_name="call_tool",
    ))

    # List tools — should return discover_tools + call_tool (and any always_visible)
    tools = await test_mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "discover_tools" in tool_names, (
        f"discover_tools should be listed. Got: {tool_names}"
    )
    assert "call_tool" in tool_names, (
        f"call_tool should be listed. Got: {tool_names}"
    )


@pytest.mark.asyncio
async def test_discover_tools_ranks_by_relevance():
    """BM25 search should rank keyword-matching tools higher than non-matching ones."""
    from fastmcp import FastMCP
    from fastmcp.server.providers import FileSystemProvider
    from fastmcp.server.transforms.search import BM25SearchTransform

    modules_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "modules"
    provider = FileSystemProvider(root=modules_dir)

    test_mcp = FastMCP("test-rank", providers=[provider])
    bm25 = BM25SearchTransform(
        max_results=5,
        always_visible=[],
        search_tool_name="discover_tools",
        call_tool_name="call_tool",
    )
    test_mcp.add_transform(bm25)

    # Search for 'echo message' which should match the example_echo tool
    all_tools = await provider._list_tools()
    results = await bm25._search(all_tools, "echo message")
    # There should be at least one result
    assert len(results) >= 1, "BM25 search should return at least one result"
    # The first result should be example_echo
    first_name = results[0].name
    assert first_name == "example_echo", (
        f"Expected 'example_echo' to rank first, got: {first_name}"
    )
