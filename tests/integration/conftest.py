"""Shared fixtures for integration tests."""

import json
import pytest
from fastmcp import Client

_server_initialized = False


@pytest.fixture(scope="session")
def mcp_server():
    """Build the full MCP server with all providers and transforms wired up.

    Scope=session so the server is built once for the entire test run.
    Guards against duplicate provider/transform registration.
    """
    global _server_initialized

    from mcp_canada.server import mcp, _build_providers, _META_DIR
    from fastmcp.server.providers import FileSystemProvider
    from fastmcp.server.transforms.search import BM25SearchTransform

    if not _server_initialized:
        providers = _build_providers('')
        for p in providers:
            mcp.add_provider(p)
        if _META_DIR.is_dir():
            mcp.add_provider(FileSystemProvider(root=_META_DIR))
        mcp.add_transform(BM25SearchTransform(
            max_results=5,
            always_visible=['discover_tools', 'list_modules', 'plan_query', 'execute_batch'],
            search_tool_name='discover_tools',
            call_tool_name='call_tool',
        ))
        _server_initialized = True

    return mcp


async def call_tool(mcp_server, tool_name: str, arguments: dict | None = None) -> dict:
    """Call a tool through the MCP Client layer and return parsed JSON."""
    async with Client(mcp_server) as client:
        result = await client.call_tool('call_tool', {
            'name': tool_name,
            'arguments': arguments or {},
        })
        return json.loads(result.content[0].text)


async def discover(mcp_server, query: str) -> list[dict]:
    """Search for tools via BM25 discover_tools and return parsed results."""
    async with Client(mcp_server) as client:
        result = await client.call_tool('discover_tools', {'query': query})
        # discover_tools may return results in different formats
        text = result.content[0].text if result.content else "[]"
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []


async def call_direct_tool(mcp_server, tool_name: str, arguments: dict | None = None) -> dict:
    """Call an always-visible tool directly (not through call_tool proxy)."""
    async with Client(mcp_server) as client:
        result = await client.call_tool(tool_name, arguments or {})
        return json.loads(result.content[0].text)
