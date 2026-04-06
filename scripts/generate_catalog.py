"""Auto-generate TOOLS.md and update README.md catalog tables from source.

Uses Python's ast module for static analysis — no runtime imports required.

Usage:
    uv run python scripts/generate_catalog.py          # generate files
    uv run python scripts/generate_catalog.py --check  # verify files are up to date (CI mode)
"""

from __future__ import annotations

import argparse
import ast
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
MODULES_DIR = REPO_ROOT / "src" / "mcp_canada" / "modules"
META_DIR = REPO_ROOT / "src" / "mcp_canada" / "meta"
TOOLS_MD = REPO_ROOT / "TOOLS.md"
README_MD = REPO_ROOT / "README.md"

# Module ordering: meta first, then alphabetical data modules
MODULE_ORDER = [
    "meta",
    "bank_of_canada",
    "open_parliament",
    "recalls",
    "drug_database",
    "ckan",
    "nutrient_file",
    "weather",
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ParamInfo:
    name: str
    annotation: str
    default: str | None
    description: str = ""


@dataclass
class ToolInfo:
    name: str
    description: str
    use_for: str
    keywords: str
    params: list[ParamInfo] = field(default_factory=list)


@dataclass
class ModuleInfo:
    module_name: str      # directory name (e.g. "bank_of_canada")
    display_name: str     # MODULE_NAME value
    description: str      # MODULE_DESCRIPTION value
    tools: list[ToolInfo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _unparse(node: ast.expr | None) -> str:
    """Return a string representation of an AST expression node."""
    if node is None:
        return ""
    return ast.unparse(node)


def _extract_module_constants(init_path: Path) -> tuple[str, str]:
    """Read MODULE_NAME and MODULE_DESCRIPTION from __init__.py via AST."""
    if not init_path.exists():
        return init_path.parent.name, ""
    try:
        source = init_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(init_path))
    except SyntaxError:
        return init_path.parent.name, ""

    module_name = init_path.parent.name
    module_description = ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "MODULE_NAME":
                        val = node.value
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            module_name = val.value
                    elif target.id == "MODULE_DESCRIPTION":
                        # Could be a string constant or a parenthesized Constant
                        val = node.value
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            module_description = val.value
                        elif isinstance(val, ast.JoinedStr):
                            module_description = ast.unparse(val).strip('"').strip("'")
    return module_name, module_description


def _parse_docstring_sections(docstring: str | None) -> tuple[str, str, str]:
    """Parse tool docstring into (description, use_for, keywords)."""
    if not docstring:
        return "", "", ""

    lines = docstring.strip().splitlines()
    description = lines[0].strip() if lines else ""
    use_for = ""
    keywords = ""

    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith("Use for:"):
            use_for = stripped[len("Use for:"):].strip()
        elif stripped.startswith("Keywords:"):
            keywords = stripped[len("Keywords:"):].strip().rstrip(".")

    return description, use_for, keywords


def _parse_args_section(docstring: str | None) -> dict[str, str]:
    """Extract parameter descriptions from Args: section of docstring."""
    if not docstring:
        return {}
    result: dict[str, str] = {}
    in_args = False
    for line in docstring.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("args:"):
            in_args = True
            continue
        if in_args:
            # End of Args section: a new section header (no leading spaces, ends with colon)
            if stripped and not line.startswith(" ") and not line.startswith("\t") and stripped.endswith(":"):
                break
            # Param line: "param_name: description"
            match = re.match(r"^(\w+)\s*[:(]\s*(.*)", stripped)
            if match:
                param_name = match.group(1)
                param_desc = match.group(2).rstrip(")")
                result[param_name] = param_desc
    return result


def _parse_tools_from_file(tools_path: Path) -> list[ToolInfo]:
    """Parse @tool decorated async functions from a tools.py file using AST."""
    source = tools_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(tools_path))
    except SyntaxError as e:
        print(f"WARNING: SyntaxError parsing {tools_path}: {e}", file=sys.stderr)
        return []

    tools: list[ToolInfo] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue

        # Check for @tool decorator
        has_tool_decorator = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "tool":
                has_tool_decorator = True
                break
            # Handle @tool(name=..., ...) call form
            if isinstance(decorator, ast.Call):
                func = decorator.func
                if isinstance(func, ast.Name) and func.id == "tool":
                    has_tool_decorator = True
                    break

        if not has_tool_decorator:
            continue

        func_name = node.name
        docstring = ast.get_docstring(node)
        description, use_for, keywords = _parse_docstring_sections(docstring)
        args_descriptions = _parse_args_section(docstring)

        # Extract parameters
        args = node.args
        all_args = args.args  # positional/keyword args

        # Align defaults: defaults are right-aligned against all_args
        num_defaults = len(args.defaults)
        num_args = len(all_args)
        # padding so index i in all_args maps to defaults[i - (num_args - num_defaults)]
        default_offset = num_args - num_defaults

        params: list[ParamInfo] = []
        for i, arg in enumerate(all_args):
            param_name = arg.arg
            # Skip internal params
            if param_name in ("self", "ctx"):
                continue

            annotation_str = _unparse(arg.annotation) if arg.annotation else ""

            # Default value
            default_str: str | None = None
            default_idx = i - default_offset
            if 0 <= default_idx < num_defaults:
                default_str = _unparse(args.defaults[default_idx])

            # Also check kwonlyargs defaults
            param_desc = args_descriptions.get(param_name, "")

            params.append(ParamInfo(
                name=param_name,
                annotation=annotation_str,
                default=default_str,
                description=param_desc,
            ))

        # Also process kwonlyargs (after *)
        kw_defaults = args.kw_defaults  # same length as kwonlyargs, None if no default
        for i, kwarg in enumerate(args.kwonlyargs):
            param_name = kwarg.arg
            if param_name in ("self", "ctx"):
                continue
            annotation_str = _unparse(kwarg.annotation) if kwarg.annotation else ""
            default_node = kw_defaults[i] if i < len(kw_defaults) else None
            default_str = _unparse(default_node) if default_node else None
            param_desc = args_descriptions.get(param_name, "")
            params.append(ParamInfo(
                name=param_name,
                annotation=annotation_str,
                default=default_str,
                description=param_desc,
            ))

        tools.append(ToolInfo(
            name=func_name,
            description=description,
            use_for=use_for,
            keywords=keywords,
            params=params,
        ))

    return tools


# ---------------------------------------------------------------------------
# Module discovery
# ---------------------------------------------------------------------------

def _discover_tools_files() -> list[tuple[str, Path]]:
    """Return list of (module_key, tools_path) for all module tools.py files.

    module_key is the directory name used to group tools:
    - "meta" for meta/ top-level tools
    - module directory name for modules/ tools
    - "weather/subdir" for weather sub-modules
    """
    result: list[tuple[str, Path]] = []

    # Meta tools (plan_query, execute_batch, list_modules)
    for py_file in sorted(META_DIR.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        result.append(("meta", py_file))

    # Standard modules
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir():
            continue
        if module_dir.name.startswith("_"):
            continue
        if module_dir.name == "weather":
            # Weather has sub-modules
            for sub_dir in sorted(module_dir.iterdir()):
                if not sub_dir.is_dir() or sub_dir.name.startswith("_"):
                    continue
                tools_file = sub_dir / "tools.py"
                if tools_file.exists():
                    result.append(("weather", tools_file))
        else:
            tools_file = module_dir / "tools.py"
            if tools_file.exists():
                result.append((module_dir.name, tools_file))

    return result


def _build_module_infos() -> list[ModuleInfo]:
    """Build the complete list of ModuleInfo objects, ordered by MODULE_ORDER."""
    # Collect all (module_key, tools) pairs
    all_tools_files = _discover_tools_files()

    # Group by module_key
    grouped: dict[str, list[ToolInfo]] = {}
    for module_key, tools_path in all_tools_files:
        tools = _parse_tools_from_file(tools_path)
        if module_key not in grouped:
            grouped[module_key] = []
        grouped[module_key].extend(tools)

    # Build ModuleInfo for each module key
    module_infos: dict[str, ModuleInfo] = {}

    # Meta module
    if "meta" in grouped:
        module_infos["meta"] = ModuleInfo(
            module_name="meta",
            display_name="Meta / Discovery",
            description="Orchestration tools always available to agents — no discovery required.",
            tools=grouped["meta"],
        )

    # Data modules
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        key = module_dir.name
        if key not in grouped:
            continue
        init_path = module_dir / "__init__.py"
        display_name, description = _extract_module_constants(init_path)
        module_infos[key] = ModuleInfo(
            module_name=key,
            display_name=display_name,
            description=description,
            tools=grouped.get(key, []),
        )

    # Return in defined order, then any extras alphabetically
    ordered: list[ModuleInfo] = []
    for key in MODULE_ORDER:
        if key in module_infos:
            ordered.append(module_infos[key])
    for key in sorted(module_infos):
        if key not in MODULE_ORDER:
            ordered.append(module_infos[key])

    return ordered


# ---------------------------------------------------------------------------
# TOOLS.md generation
# ---------------------------------------------------------------------------

def _format_param_table(params: list[ParamInfo]) -> str:
    """Format parameters as a markdown table."""
    if not params:
        return "_No parameters._\n"

    rows = []
    for p in params:
        default_cell = f"`{p.default}`" if p.default is not None else "—"
        annotation_cell = f"`{p.annotation}`" if p.annotation else "—"
        desc_cell = p.description if p.description else "—"
        rows.append(f"| `{p.name}` | {annotation_cell} | {default_cell} | {desc_cell} |")

    header = "| Parameter | Type | Default | Description |\n|-----------|------|---------|-------------|"
    return header + "\n" + "\n".join(rows) + "\n"


def generate_tools_md(module_infos: list[ModuleInfo]) -> str:
    """Generate the full TOOLS.md content."""
    lines = [
        "# Tool Reference",
        "",
        "Auto-generated from source. Do not edit manually.",
        "Run `uv run python scripts/generate_catalog.py` to regenerate.",
        "",
    ]

    total_tools = sum(len(m.tools) for m in module_infos)
    lines.append(f"**{total_tools} tools** across {len(module_infos)} modules.")
    lines.append("")

    for module in module_infos:
        n = len(module.tools)
        lines.append(f"## Module: {module.display_name} ({n} tool{'s' if n != 1 else ''})")
        lines.append("")
        if module.description:
            lines.append(module.description)
            lines.append("")

        for tool_info in module.tools:
            lines.append(f"### `{tool_info.name}`")
            lines.append("")
            if tool_info.description:
                lines.append(tool_info.description)
                lines.append("")
            lines.append(_format_param_table(tool_info.params))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# README catalog table generation
# ---------------------------------------------------------------------------

# Map from module key to CATALOG marker name
_MODULE_CATALOG_KEYS: dict[str, str] = {
    "meta": "meta",
    "bank_of_canada": "bank_of_canada",
    "open_parliament": "open_parliament",
    "recalls": "recalls",
    "drug_database": "drug_database",
    "ckan": "ckan",
    "nutrient_file": "nutrient_file",
    "weather": "weather",
}


def _format_summary_table(tools: list[ToolInfo]) -> str:
    """Format a compact summary table for README (excludes lang param)."""
    if not tools:
        return "_No tools._\n"

    rows = []
    for t in tools:
        # Key params: exclude lang (universal) and ctx (internal)
        key_params = [
            p.name for p in t.params
            if p.name not in ("lang", "ctx")
        ]
        key_params_str = ", ".join(f"`{p}`" for p in key_params) if key_params else "—"
        desc = t.description.replace("|", "\\|") if t.description else "—"
        rows.append(f"| `{t.name}` | {desc} | {key_params_str} |")

    header = "| Tool | Description | Key Parameters |\n|------|-------------|----------------|"
    return header + "\n" + "\n".join(rows)


def update_readme_catalog(readme_content: str, module_infos: list[ModuleInfo]) -> str:
    """Replace content between CATALOG markers in README with fresh summary tables."""
    result = readme_content

    # Build a lookup: catalog_key -> ModuleInfo
    module_by_key: dict[str, ModuleInfo] = {}
    for module in module_infos:
        catalog_key = _MODULE_CATALOG_KEYS.get(module.module_name)
        if catalog_key:
            module_by_key[catalog_key] = module

    # Find and replace each CATALOG section
    catalog_keys = list(_MODULE_CATALOG_KEYS.values())
    for catalog_key in catalog_keys:
        start_marker = f"<!-- CATALOG:{catalog_key}:start -->"
        end_marker = f"<!-- CATALOG:{catalog_key}:end -->"

        start_idx = result.find(start_marker)
        end_idx = result.find(end_marker)

        if start_idx == -1 or end_idx == -1:
            # Markers not present — skip
            continue

        module = module_by_key.get(catalog_key)
        if module is None:
            continue

        table = _format_summary_table(module.tools)
        # Replace everything between start marker and end marker
        new_section = f"{start_marker}\n{table}\n{end_marker}"
        result = result[:start_idx] + new_section + result[end_idx + len(end_marker):]

    return result


# ---------------------------------------------------------------------------
# Check mode
# ---------------------------------------------------------------------------

def check_mode(module_infos: list[ModuleInfo]) -> int:
    """Compare generated content against disk files. Returns 0 if fresh, 1 if stale."""
    expected_tools_md = generate_tools_md(module_infos)

    readme_content = README_MD.read_text(encoding="utf-8") if README_MD.exists() else ""
    expected_readme = update_readme_catalog(readme_content, module_infos)

    issues: list[str] = []

    # Check TOOLS.md
    if TOOLS_MD.exists():
        actual_tools = TOOLS_MD.read_text(encoding="utf-8")
        if actual_tools != expected_tools_md:
            diff = difflib.unified_diff(
                actual_tools.splitlines(keepends=True),
                expected_tools_md.splitlines(keepends=True),
                fromfile="TOOLS.md (current)",
                tofile="TOOLS.md (expected)",
                n=3,
            )
            issues.append("TOOLS.md is stale:\n" + "".join(list(diff)[:50]))
    else:
        issues.append("TOOLS.md does not exist.")

    # Check README.md
    if README_MD.exists():
        actual_readme = README_MD.read_text(encoding="utf-8")
        if actual_readme != expected_readme:
            diff = difflib.unified_diff(
                actual_readme.splitlines(keepends=True),
                expected_readme.splitlines(keepends=True),
                fromfile="README.md (current)",
                tofile="README.md (expected)",
                n=3,
            )
            issues.append("README.md catalog tables are stale:\n" + "".join(list(diff)[:50]))
    else:
        issues.append("README.md does not exist.")

    if issues:
        print("Catalog is STALE. Run `uv run python scripts/generate_catalog.py` to update.\n")
        for issue in issues:
            print(issue)
        return 1

    print("Catalog is up to date.")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate or verify the tool catalog (TOOLS.md and README tables).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify files are up to date and exit 1 if stale (CI mode).",
    )
    args = parser.parse_args()

    module_infos = _build_module_infos()

    if args.check:
        sys.exit(check_mode(module_infos))
    else:
        # Write TOOLS.md
        tools_content = generate_tools_md(module_infos)
        TOOLS_MD.write_text(tools_content, encoding="utf-8")
        print(f"Written: {TOOLS_MD}")

        # Update README.md
        if README_MD.exists():
            readme_content = README_MD.read_text(encoding="utf-8")
            updated_readme = update_readme_catalog(readme_content, module_infos)
            README_MD.write_text(updated_readme, encoding="utf-8")
            print(f"Updated: {README_MD}")
        else:
            print(f"WARNING: {README_MD} does not exist — README not updated.", file=sys.stderr)

        total = sum(len(m.tools) for m in module_infos)
        print(f"Catalog generated: {total} tools across {len(module_infos)} modules.")


if __name__ == "__main__":
    main()
