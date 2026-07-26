"""Every @tool must be covered by a catch-all error handler.

Project rule: a tool returns a structured error envelope, never raises. Phase 20.1
found drug_database and nutrient_file shipping 16 tools with ZERO exception
handling, so a slow Health Canada response escaped as a raw fastmcp ToolError
instead of an envelope an agent could reason about.

Phase 20.2 generalises that finding. A tool that catches only
``httpx.HTTPStatusError`` is covered for a 500 but NOT for a timeout, a connect
error, or a malformed body — every one of which escapes the same way. This test
makes the gap impossible to reintroduce.

A tool counts as covered when any of these holds:
  * it is decorated with ``@upstream_guard(...)``
  * it catches ``Exception``, a bare ``except``, or ``httpx.HTTPError``
  * it delegates to a module-level helper that does one of the above
    (york_region's ``_call_client`` is the canonical example)
"""

from __future__ import annotations

import ast
import pathlib

import pytest

MODULES_DIR = pathlib.Path(__file__).resolve().parents[1] / "src" / "mcp_canada" / "modules"


def _has_catch_all(node: ast.AST) -> bool:
    """True if the node contains an except arm that catches broad failures."""
    for handler in ast.walk(node):
        if not isinstance(handler, ast.ExceptHandler):
            continue
        if handler.type is None:  # bare except
            return True
        rendered = ast.unparse(handler.type)
        if rendered == "Exception" or "HTTPError" in rendered:
            return True
    return False


def _uncovered_tools() -> list[tuple[str, str]]:
    """Return (module, tool_name) for every @tool lacking catch-all coverage."""
    offenders: list[tuple[str, str]] = []

    for path in sorted(MODULES_DIR.rglob("tools.py")):
        tree = ast.parse(path.read_text())
        module = str(path.parent.relative_to(MODULES_DIR))

        # Module-level helpers that themselves handle broad failures. A tool that
        # delegates to one of these is covered by it.
        safe_helpers = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
            and _has_catch_all(node)
        }

        for node in tree.body:
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            decorators = [ast.unparse(d) for d in node.decorator_list]
            if "tool" not in decorators:
                continue
            if any("upstream_guard" in d for d in decorators):
                continue
            if _has_catch_all(node):
                continue
            called = {
                call.func.id
                for call in ast.walk(node)
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            }
            if called & safe_helpers:
                continue
            offenders.append((module, node.name))

    return offenders


def test_every_tool_has_catch_all_error_handling():
    """A tool that catches only HTTPStatusError still leaks timeouts as ToolError."""
    offenders = _uncovered_tools()
    assert offenders == [], (
        f"{len(offenders)} tool(s) can leak an unhandled exception to the agent "
        f"instead of returning an error envelope. Add @upstream_guard(<api_name>) "
        f"beneath @tool, or catch httpx.HTTPError. Offenders: {offenders}"
    )


def test_guard_detects_a_known_uncovered_shape():
    """The detector must not vacuously pass — prove it flags a leaky tool."""
    leaky = ast.parse(
        "@tool\n"
        "async def x(lang='en'):\n"
        "    try:\n"
        "        await go()\n"
        "    except httpx.HTTPStatusError:\n"
        "        return make_error('UPSTREAM_ERROR', 'x')\n"
    ).body[0]
    assert not _has_catch_all(leaky), "HTTPStatusError-only must NOT count as covered"

    covered = ast.parse(
        "@tool\n"
        "async def x(lang='en'):\n"
        "    try:\n"
        "        await go()\n"
        "    except httpx.HTTPError:\n"
        "        return make_error('UPSTREAM_ERROR', 'x')\n"
    ).body[0]
    assert _has_catch_all(covered), "httpx.HTTPError must count as covered"


@pytest.mark.asyncio
async def test_upstream_guard_really_is_a_catch_all():
    """This detector counts @upstream_guard as coverage — prove that is earned.

    The assumption was false when first written: the guard caught only httpx
    errors, JSONDecodeError and ValueError, so a KeyError from flattening code
    escaped as a raw ToolError while this file still reported zero offenders.
    If someone narrows the guard again, this fails here rather than silently
    hollowing out every assertion above.
    """
    from mcp_canada.shared.envelope import upstream_guard

    class Exotic(Exception):
        pass

    @upstream_guard("test-api")
    async def boom(lang: str = "en") -> dict:
        raise Exotic("something no one predicted")

    result = await boom()
    assert "error" in result, (
        "upstream_guard let an arbitrary exception escape — every @upstream_guard "
        "counted as coverage by this module is therefore unproven"
    )
    assert result["error"]["code"] == "UPSTREAM_ERROR"


@pytest.mark.parametrize("rendered", ["Exception", "httpx.HTTPError"])
def test_broad_shapes_count_as_covered(rendered):
    node = ast.parse(
        f"def f():\n    try:\n        g()\n    except {rendered}:\n        pass\n"
    ).body[0]
    assert _has_catch_all(node)
