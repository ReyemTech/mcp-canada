"""list_modules meta-tool — lists all registered API modules with tool counts."""

from pathlib import Path

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_response

# Path to the modules directory — relative to this file's parent's parent
_MODULES_DIR = Path(__file__).parent.parent / "modules"


@tool(name="list_modules", tags={"meta", "discovery", "modules"})
async def list_modules() -> dict:
    """List all registered API modules with tool counts and descriptions.

    Use this to understand what data sources are available before calling
    discover_tools for specific queries.
    Keywords: modules, APIs, data sources, available tools, capabilities.
    """
    module_infos = []

    if _MODULES_DIR.exists():
        for module_dir in sorted(_MODULES_DIR.iterdir()):
            if not module_dir.is_dir():
                continue
            # Skip __pycache__
            if module_dir.name == "__pycache__":
                continue

            # Load module metadata from __init__.py if available
            module_name = module_dir.name
            module_description = ""
            try:
                import importlib
                pkg_name = f"mcp_canada.modules.{module_name}"
                mod = importlib.import_module(pkg_name)
                module_description = getattr(mod, "MODULE_DESCRIPTION", "")
                display_name = getattr(mod, "MODULE_NAME", module_name)
            except ImportError:
                display_name = module_name

            # Count @tool-decorated functions by scanning tools.py
            tool_count = _count_tools_in_module(module_dir)

            module_infos.append({
                "name": display_name,
                "directory": module_name,
                "description": module_description,
                "tool_count": tool_count,
            })

    from mcp_canada import __version__

    return make_response(
        {"version": __version__, "modules": module_infos},
        api_name="mcp-canada",
        api_url="internal://list_modules",
        cached=False,
        lang="en",
    )


def _count_tools_in_module(module_dir: Path) -> int:
    """Count @tool-decorated functions in a module directory.

    Uses FileSystemProvider's internal component store (populated synchronously
    at init time) to avoid nesting event loops.
    """
    try:
        from fastmcp.server.providers import FileSystemProvider

        provider = FileSystemProvider(root=module_dir)
        # _components is populated synchronously during __init__ via _load_components()
        # Count only Tool-type components (not resources/prompts)
        from fastmcp.tools.base import Tool
        return sum(
            1 for c in provider._components.values() if isinstance(c, Tool)
        )
    except Exception:
        return 0
