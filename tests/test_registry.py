"""Integration tests: FileSystemProvider auto-discovery and module registry."""

import asyncio
from pathlib import Path


def test_filesystem_provider_discovers_tools():
    """FileSystemProvider should discover example_echo tool from _example fixture.

    _example is a private test fixture (underscore-prefixed) that is excluded
    from production registration in server._build_providers. This test points
    a provider directly at the fixture to verify auto-discovery mechanics.
    """
    from fastmcp.server.providers import FileSystemProvider

    example_dir = (
        Path(__file__).parent.parent
        / "src" / "mcp_canada" / "modules" / "_example"
    )
    provider = FileSystemProvider(root=example_dir)

    # Use the proper async API to list tools
    tools = asyncio.run(provider._list_tools())
    tool_names = [t.name for t in tools]
    assert "example_echo" in tool_names, (
        f"expected 'example_echo' in discovered tools, got: {tool_names}"
    )


def test_module_without_tools_skipped():
    """A directory with no @tool functions should not raise errors."""
    import tempfile
    import os
    from fastmcp.server.providers import FileSystemProvider

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an empty module (no @tool functions)
        module_dir = os.path.join(tmpdir, "empty_module")
        os.makedirs(module_dir)
        with open(os.path.join(module_dir, "__init__.py"), "w") as f:
            f.write("# empty module\n")
        with open(os.path.join(module_dir, "tools.py"), "w") as f:
            f.write("# no tools here\ndef helper(): pass\n")

        # Should not raise
        provider = FileSystemProvider(root=tmpdir)
        tools = asyncio.run(provider._list_tools())
        tool_names = [t.name for t in tools]
        assert len(tool_names) == 0, f"Expected no tools, got: {tool_names}"
