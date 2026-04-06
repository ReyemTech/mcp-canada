"""Quality tests for tool descriptions — validates BM25 optimization standards.

These tests validate the _example module and meta-tools now, and will
automatically cover all future modules added in Phases 2-4.
"""

import asyncio
import pytest
from pathlib import Path


def _get_all_tools():
    """Discover all tools from modules/ and meta/ directories."""
    from fastmcp.server.providers import FileSystemProvider

    modules_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "modules"
    meta_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "meta"

    providers = [FileSystemProvider(root=modules_dir)]
    if meta_dir.exists():
        providers.append(FileSystemProvider(root=meta_dir))

    all_tools = []
    for provider in providers:
        tools = asyncio.run(provider._list_tools())
        all_tools.extend(tools)
    return all_tools


# Meta-tool names that are exempt from the module_prefix_action naming convention
_META_TOOL_NAMES = {"discover_tools", "list_modules", "call_tool", "search_tools"}


def test_all_tool_descriptions_meet_quality():
    """All registered tools should have descriptions >= 50 chars."""
    tools = _get_all_tools()
    assert len(tools) > 0, "Should have at least one tool to validate"

    failures = []
    for tool in tools:
        desc = tool.description or ""
        if len(desc) < 50:
            failures.append(f"  {tool.name!r}: {len(desc)} chars — {desc!r}")

    assert not failures, (
        "Tool descriptions must be >= 50 chars.\nFailing tools:\n" + "\n".join(failures)
    )


def test_tool_descriptions_have_keywords():
    """All registered tools should have 'Keywords:' or 'Use for:' in their description."""
    tools = _get_all_tools()
    assert len(tools) > 0, "Should have at least one tool to validate"

    failures = []
    for tool in tools:
        desc = tool.description or ""
        if "Keywords:" not in desc and "Use for:" not in desc:
            failures.append(f"  {tool.name!r}: missing Keywords/Use-for line")

    assert not failures, (
        "Tool descriptions must contain 'Keywords:' or 'Use for:' line.\n"
        "Failing tools:\n" + "\n".join(failures)
    )


def test_tool_names_follow_convention():
    """Tool names should follow {prefix}_{action} pattern or be known meta-tools."""
    tools = _get_all_tools()
    assert len(tools) > 0, "Should have at least one tool to validate"

    failures = []
    for tool in tools:
        name = tool.name
        if name in _META_TOOL_NAMES:
            continue  # Meta-tools are exempt

        # Must have at least one underscore separating prefix from action
        if "_" not in name:
            failures.append(
                f"  {name!r}: must follow {{prefix}}_{{action}} naming convention"
            )

    assert not failures, (
        "Tool names must follow {{prefix}}_{{action}} pattern.\n"
        "Failing tools:\n" + "\n".join(failures)
    )


@pytest.mark.asyncio
async def test_list_modules_tool_exists():
    """list_modules tool should be discoverable in the meta/ directory."""
    from fastmcp.server.providers import FileSystemProvider

    meta_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "meta"
    assert meta_dir.exists(), "meta/ directory should exist"

    provider = FileSystemProvider(root=meta_dir)
    tools = await provider._list_tools()
    tool_names = [t.name for t in tools]
    assert "list_modules" in tool_names, (
        f"list_modules tool should be discoverable. Got: {tool_names}"
    )


@pytest.mark.asyncio
async def test_list_modules_returns_module_info():
    """list_modules() should return dict with _meta and data keys."""
    from mcp_canada.meta.list_modules import list_modules

    result = await list_modules()
    assert isinstance(result, dict), "list_modules should return a dict"
    assert "_meta" in result, "list_modules response should have '_meta' key"
    assert "data" in result, "list_modules response should have 'data' key"
    assert isinstance(result["data"], list), "list_modules data should be a list"
