"""Caller error must be opt-in; upstream failure is the safe default.

Phase 20.4. Four Codex findings across three PRs were all the same defect:

    PR#2  json.JSONDecodeError      subclasses ValueError -> reported INVALID_INPUT
    PR#3  pydantic.ValidationError  subclasses ValueError -> reported INVALID_INPUT
    PR#4  UnicodeDecodeError        subclasses ValueError -> reported INVALID_INPUT
    PR#3  arbitrary exceptions      not enumerated        -> escaped entirely

Each was patched by intercepting one more subclass *above* the
``except ValueError -> INVALID_INPUT`` arm. That is a deny-list, and it can never
be complete: ``ValueError`` is Python's generic bad-value base and any library
may add to it tomorrow.

This module enforces the inversion. ``INVALID_INPUT`` is returned only for
``mcp_canada.shared.errors.InvalidInput`` — a marker the code raises
deliberately. A bare ``ValueError`` from anywhere else defaults to
``UPSTREAM_ERROR``, so a subclass nobody predicted is classified correctly with
no code change.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "mcp_canada"


def _source_files() -> list[pathlib.Path]:
    return [p for p in sorted(SRC.rglob("*.py")) if "__tests__" not in str(p)]


def _raises_bare_valueerror() -> list[str]:
    """Sites raising ValueError directly instead of a classified marker."""
    offenders: list[str] = []
    for path in _source_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - source must always parse
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and isinstance(node.exc.func, ast.Name)
                and node.exc.func.id == "ValueError"
            ):
                offenders.append(f"{path.relative_to(SRC)}:{node.lineno}")
    return offenders


def _valueerror_arms_returning_invalid_input() -> list[str]:
    """`except ValueError` arms that blame the caller."""
    offenders: list[str] = []
    for path in _source_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler) or node.type is None:
                continue
            caught = ast.unparse(node.type)
            # An arm naming InvalidInput explicitly is the opt-in and is fine.
            if "InvalidInput" in caught:
                continue
            if "ValueError" not in caught:
                continue
            if "INVALID_INPUT" in ast.unparse(node):
                offenders.append(f"{path.relative_to(SRC)}:{node.lineno}")
    return offenders


def test_no_bare_valueerror_is_raised_in_source():
    """Raise InvalidInput (caller's fault) or an upstream-shaped error instead.

    A bare `raise ValueError` is ambiguous: the handler cannot tell whether the
    caller passed something wrong or an upstream returned something wrong. The
    sweep that motivated this phase found 31 such raises, of which 9 were
    already misclassified — "Dataset not found", "StatCan returned empty
    response body", "portal has no public ArcGIS Hub open data portal" all
    surfaced to agents as INVALID_INPUT.
    """
    offenders = _raises_bare_valueerror()
    assert offenders == [], (
        f"{len(offenders)} bare `raise ValueError` in source. Raise "
        f"InvalidInput for a caller mistake, or an upstream-shaped exception "
        f"otherwise: {offenders}"
    )


def test_no_handler_maps_plain_valueerror_to_invalid_input():
    """`except ValueError -> INVALID_INPUT` is the deny-list this phase removes.

    It silently captures every ValueError subclass any library defines. Catch
    InvalidInput for the caller-error path and let plain ValueError fall through
    to the upstream default.
    """
    offenders = _valueerror_arms_returning_invalid_input()
    assert offenders == [], (
        f"{len(offenders)} handler(s) still blame the caller for any ValueError. "
        f"Catch InvalidInput instead: {offenders}"
    )


def test_detector_is_not_vacuous():
    """Both detectors must reject the shapes they exist to catch."""
    bad_raise = ast.parse('raise ValueError("nope")').body[0]
    assert isinstance(bad_raise, ast.Raise)
    assert isinstance(bad_raise.exc, ast.Call)
    assert bad_raise.exc.func.id == "ValueError"  # type: ignore[attr-defined]

    arm = ast.parse(
        "try:\n    go()\n"
        "except ValueError:\n    return make_error('INVALID_INPUT', 'x')\n"
    ).body[0]
    handler = arm.handlers[0]  # type: ignore[attr-defined]
    assert "ValueError" in ast.unparse(handler.type)
    assert "INVALID_INPUT" in ast.unparse(handler)


@pytest.mark.asyncio
async def test_unknown_valueerror_subclass_defaults_to_upstream():
    """The whole point: a subclass nobody predicted is classified safely.

    This is the test that would have caught all three of the ValueError-subclass
    findings at once, instead of one per review round.
    """
    from mcp_canada.shared.envelope import upstream_guard

    class SomeLibraryError(ValueError):
        """Stands in for the next json/pydantic/codecs subclass."""

    @upstream_guard("test-api")
    async def boom(lang: str = "en") -> dict:
        raise SomeLibraryError("upstream sent something odd")

    result = await boom()
    assert result["error"]["code"] == "UPSTREAM_ERROR", (
        "an unrecognised ValueError subclass was blamed on the caller — this is "
        "the deny-list failure mode Phase 20.4 removes"
    )


@pytest.mark.asyncio
async def test_invalid_input_marker_still_reaches_the_caller():
    """The opt-in path must keep working, or the inversion has over-reached."""
    from mcp_canada.shared.envelope import upstream_guard
    from mcp_canada.shared.errors import InvalidInput

    @upstream_guard("test-api")
    async def boom(lang: str = "en") -> dict:
        raise InvalidInput("year must be between 1990 and 2026")

    result = await boom()
    assert result["error"]["code"] == "INVALID_INPUT"
    assert "1990" in result["error"]["message"]


def test_invalid_input_is_a_valueerror_for_backwards_compatibility():
    """Existing `except ValueError` arms must still catch the marker.

    InvalidInput subclasses ValueError so that any handler not yet migrated
    keeps working. The inversion changes classification, not control flow.
    """
    from mcp_canada.shared.errors import InvalidInput

    assert issubclass(InvalidInput, ValueError)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "client_attr", "tool_name", "kwargs", "marker", "expected"),
    [
        ("york_region", "fetch_get_dataset_details", "york_region_get_dataset_details",
         {"dataset_id": "bogus"}, "NotFound", "NOT_FOUND"),
        ("manitoba", "fetch_livestock_prices", "manitoba_get_livestock_prices",
         {}, "InvalidInput", "INVALID_INPUT"),
        ("saskatchewan", "fetch_fire_bans", "saskatchewan_get_fire_bans",
         {"ban_scope": "urban"}, "InvalidInput", "INVALID_INPUT"),
        ("ircc", "fetch_permanent_residents", "ircc_get_permanent_residents",
         {}, "InvalidInput", "INVALID_INPUT"),
    ],
)
async def test_markers_survive_the_module_handler(
    module, client_attr, tool_name, kwargs, marker, expected
):
    """Classifying at the raise site is useless if the handler drops it.

    york_region carries no @upstream_guard — its `_call_client` helper is the
    catch-all — so a NotFound raised for an unknown dataset id fell into the
    generic arm and a routine missing record was reported as an upstream
    outage. Caught by Codex on PR #5. This covers each module whose own client
    raises a marker.
    """
    import importlib
    from unittest.mock import AsyncMock, patch

    import mcp_canada.shared.errors as errors

    tools = importlib.import_module(f"mcp_canada.modules.{module}.tools")
    client = importlib.import_module(f"mcp_canada.modules.{module}.client")
    target = tools if hasattr(tools, client_attr) else client
    exc = getattr(errors, marker)("probe")

    with patch.object(target, client_attr, new=AsyncMock(side_effect=exc)):
        result = await getattr(tools, tool_name)(**kwargs)

    assert result["error"]["code"] == expected, (
        f"{module}.{tool_name} dropped a {marker} raised by its client"
    )
