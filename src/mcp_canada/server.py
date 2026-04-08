"""FastMCP server entry point for mcp-canada."""

import argparse
import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider
from fastmcp.server.transforms.search import BM25SearchTransform

from mcp_canada import __version__

logger = logging.getLogger(__name__)

# Module-level config dict so Plan 02+ can read module selection
_config: dict[str, Any] = {}

# Path to the modules and meta directories (relative to this file)
_MODULES_DIR = Path(__file__).parent / "modules"
_META_DIR = Path(__file__).parent / "meta"


@asynccontextmanager
async def lifespan(app: Any) -> AsyncGenerator[dict[str, Any], None]:
    """Manage server lifespan: create and close shared httpx.AsyncClient."""
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        headers={"User-Agent": f"mcp-canada/{__version__}"},
    )
    try:
        yield {"http": client}
    finally:
        await client.aclose()


def _build_providers(modules_filter: str) -> list[FileSystemProvider]:
    """Build FileSystemProvider(s) based on optional --modules filter.

    Args:
        modules_filter: Comma-separated module names to load.
            If empty, all subdirectories under modules/ are loaded.

    Returns:
        List of FileSystemProvider instances.
    """
    if not modules_filter:
        # Load all modules — single provider pointing at modules/
        logger.info(
            "Loading all modules. Consider using --modules to load only what you need "
            "(e.g. --modules weather,recalls)"
        )
        return [FileSystemProvider(root=_MODULES_DIR)]

    # Selective loading: one provider per named module subdirectory
    selected = [m.strip() for m in modules_filter.split(",") if m.strip()]
    providers = []
    for mod_name in selected:
        mod_path = _MODULES_DIR / mod_name
        if mod_path.is_dir():
            providers.append(FileSystemProvider(root=mod_path))
            logger.info(f"Loaded module: {mod_name}")
        else:
            logger.warning(f"Module directory not found, skipping: {mod_path}")
    return providers


mcp = FastMCP(
    "mcp-canada",
    instructions=(
        "Canadian federal government data. Use discover_tools to find relevant tools."
    ),
    lifespan=lifespan,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="mcp-canada",
        description="MCP server for Canadian federal government data",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE/HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for SSE/HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--modules",
        default=os.environ.get("MCP_CANADA_MODULES", ""),
        help="Comma-separated list of modules to load (env: MCP_CANADA_MODULES)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable INFO-level logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        default=False,
        help="Use in-memory SQLite datastore (no persistence)",
    )
    subparsers = parser.add_subparsers(dest="command")
    install_parser = subparsers.add_parser(
        "install",
        help="Configure mcp-canada on MCP client platforms",
    )
    install_parser.add_argument(
        "platforms",
        nargs="*",
        default=[],
        help="Platform names to configure (omit for interactive selection)",
    )
    install_parser.add_argument(
        "--modules",
        default="",
        help="Modules to include in generated config (e.g. bank_of_canada,weather)",
    )
    return parser


def main() -> None:
    """CLI entry point for mcp-canada."""
    parser = _build_parser()
    args = parser.parse_args()

    # Handle install subcommand
    if args.command == "install":
        from mcp_canada.installer import run_install
        run_install(args)
        return

    # Configure logging
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.ERROR

    logging.basicConfig(level=log_level)

    import sys
    print(f"mcp-canada v{__version__}", file=sys.stderr)

    # Store parsed config for other modules to read
    _config.update(vars(args))

    # Add module providers based on --modules filter
    providers = _build_providers(args.modules)
    for provider in providers:
        mcp.add_provider(provider)

    # Add meta provider (list_modules, etc.) — always loaded regardless of --modules
    if _META_DIR.is_dir():
        mcp.add_provider(FileSystemProvider(root=_META_DIR))

    # Add BM25 search transform: exposes discover_tools + call_tool meta-tools
    mcp.add_transform(BM25SearchTransform(
        max_results=5,
        always_visible=["discover_tools", "list_modules", "plan_query", "execute_batch"],
        search_tool_name="discover_tools",
        call_tool_name="call_tool",
    ))

    # Run the server
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:  # http
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
