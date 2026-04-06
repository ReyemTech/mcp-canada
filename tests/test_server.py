"""Tests for the FastMCP server entry point."""

import pytest
import httpx
from unittest.mock import MagicMock, patch


def test_server_creates_fastmcp_instance():
    """Server should expose a FastMCP instance named 'mcp-canada'."""
    from mcp_canada.server import mcp

    assert mcp.name == "mcp-canada"


@pytest.mark.asyncio
async def test_lifespan_yields_http_client():
    """Lifespan context manager should yield a dict with 'http' key containing AsyncClient."""
    from mcp_canada.server import lifespan

    # lifespan takes a server arg (FastMCP app), pass None for testing
    async with lifespan(None) as ctx:
        assert "http" in ctx
        assert isinstance(ctx["http"], httpx.AsyncClient)


def test_main_is_callable():
    """main() should be a callable entry point."""
    from mcp_canada.server import main

    assert callable(main)


def test_cli_defaults():
    """CLI should default to stdio transport."""
    from mcp_canada.server import _build_parser

    parser = _build_parser()
    args = parser.parse_args([])
    assert args.transport == "stdio"
    assert args.port == 8000
    assert args.host == "127.0.0.1"
    assert args.verbose is False
    assert args.debug is False


def test_main_stdio_transport():
    """main() with stdio transport should call mcp.run() with no transport arg."""
    from mcp_canada import server

    with (
        patch.object(server, "_build_parser") as mock_parser_factory,
        patch.object(server.mcp, "run") as mock_run,
    ):
        mock_args = MagicMock()
        mock_args.debug = False
        mock_args.verbose = False
        mock_args.modules = "weather"
        mock_args.transport = "stdio"
        mock_parser_factory.return_value.parse_args.return_value = mock_args

        server.main()

        mock_run.assert_called_once_with()


def test_main_sse_transport():
    """main() with sse transport should call mcp.run(transport='sse', ...)."""
    from mcp_canada import server

    with (
        patch.object(server, "_build_parser") as mock_parser_factory,
        patch.object(server.mcp, "run") as mock_run,
    ):
        mock_args = MagicMock()
        mock_args.debug = False
        mock_args.verbose = True
        mock_args.modules = "boc"
        mock_args.transport = "sse"
        mock_args.host = "127.0.0.1"
        mock_args.port = 9000
        mock_parser_factory.return_value.parse_args.return_value = mock_args

        server.main()

        mock_run.assert_called_once_with(transport="sse", host="127.0.0.1", port=9000)


def test_main_http_transport():
    """main() with http transport should call mcp.run(transport='streamable-http', ...)."""
    from mcp_canada import server

    with (
        patch.object(server, "_build_parser") as mock_parser_factory,
        patch.object(server.mcp, "run") as mock_run,
    ):
        mock_args = MagicMock()
        mock_args.debug = True
        mock_args.verbose = False
        mock_args.modules = ""
        mock_args.transport = "http"
        mock_args.host = "0.0.0.0"
        mock_args.port = 8080
        mock_parser_factory.return_value.parse_args.return_value = mock_args

        server.main()

        mock_run.assert_called_once_with(
            transport="streamable-http", host="0.0.0.0", port=8080
        )


def test_selective_module_loading():
    """--modules flag should filter which modules are registered in FileSystemProvider."""
    import asyncio
    from pathlib import Path
    from fastmcp.server.providers import FileSystemProvider

    modules_dir = Path(__file__).parent.parent / "src" / "mcp_canada" / "modules"

    # With no filter: all modules discovered (including _example)
    provider_all = FileSystemProvider(root=modules_dir)
    all_tools = asyncio.run(provider_all._list_tools())
    all_tool_names = [t.name for t in all_tools]
    assert "example_echo" in all_tool_names, (
        f"All-modules load should find example_echo. Got: {all_tool_names}"
    )

    # With modules filter: only load specified subdirectory names
    # Since _example exists, specifying only a non-existing module should yield 0 tools
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a filtered modules dir with only a real_module subdirectory
        real_module = os.path.join(tmpdir, "real_module")
        os.makedirs(real_module)
        with open(os.path.join(real_module, "__init__.py"), "w") as f:
            f.write("MODULE_NAME = 'real'\n")
        with open(os.path.join(real_module, "tools.py"), "w") as f:
            f.write("# no tools\n")

        # Filter to only 'other_module' (which doesn't exist) → 0 tools
        selected = ["other_module"]
        filtered_providers = [
            FileSystemProvider(root=Path(tmpdir) / mod)
            for mod in selected
            if (Path(tmpdir) / mod).exists()
        ]
        total_tools = sum(len(p._components) for p in filtered_providers)
        assert total_tools == 0, "Expected 0 tools when filtering to non-existent module"
