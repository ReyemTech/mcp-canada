"""Structural guard against masking idioms in the live integration suite.

## Why this exists

Integration tests that cannot fail are worse than no tests: they report green
while the tool is broken. This project shipped that exact failure twice —
the Nova Scotia health-facilities 400 bug (Phase 20-08) reached main behind a
green suite, and quick task 1 then found the same masking pattern in 25 more
scenarios across five provinces.

Fixing the instances is not enough. Without an automatic check the next module
author copies the nearest example and the pattern returns. This test is that
check, and it runs in the DEFAULT unit suite — not the live run — so it is
enforced on every commit even though the tests it inspects need network.

## The rule

Every path through an integration test must reach an assertion.

Three structural violations are detected:

1. **One-armed guarded assertion** — `if "_meta" in data:` wrapping the real
   assertions with no `else`. When the response is an error the body is skipped
   and the test passes silently. This is "idiom B" from quick task 1.
2. **Early return** — a bare `return` inside a test, which abandons the
   remaining assertions. This is "idiom A" (`assert code == "UPSTREAM_ERROR";
   return`).
3. **Skip** — `pytest.skip(...)`, which reports neither pass nor fail. A skip
   conditional on live data means the path under test was never exercised.

The hardened pattern needs no exemption and is the intended way to tolerate a
flaky upstream — both arms assert, so it satisfies the rule by construction:

    if "_meta" in data:
        assert data["_meta"]["source"]["api"] == "..."
    else:
        assert data["error"]["code"] in {"UPSTREAM_ERROR", "RATE_LIMITED"}

## Deliberate exceptions

A test that genuinely cannot follow the rule declares itself:

    @pytest.mark.tolerates_upstream_error(reason="off-season empty is valid")

The reason is mandatory and must be non-trivial — an exemption without a stated
cause is how a PRESERVE list rots into a mask list.
"""

import ast
from pathlib import Path

import pytest

INTEGRATION_DIR = Path(__file__).parent / "integration"
MARKER = "tolerates_upstream_error"

# Response-shaped names. A conditional on one of these branches on what the
# server returned, which is exactly where masking hides. Conditionals on local
# bookkeeping (loop counters, list lengths) are not the target.
RESPONSE_NAMES = {"data", "result", "payload", "response", "info", "row", "rows"}


def _iter_test_functions():
    """Yield (path, ast.FunctionDef) for every test in tests/integration/."""
    for path in sorted(INTEGRATION_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                yield path, node


def _exemption(func) -> str | None:
    """Return the declared reason if the test is marked, else None."""
    for dec in func.decorator_list:
        call = dec if isinstance(dec, ast.Call) else None
        target = call.func if call else dec
        if isinstance(target, ast.Attribute) and target.attr == MARKER:
            if not call:
                return ""
            for kw in call.keywords:
                if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                    return str(kw.value.value)
            return ""
    return None


def _mentions_response(node) -> bool:
    """True if the expression reads one of the response-shaped names."""
    return any(
        isinstance(n, ast.Name) and n.id in RESPONSE_NAMES for n in ast.walk(node)
    )


def _has_terminal(body) -> bool:
    """True if this branch asserts, raises, or explicitly fails."""
    for node in body:
        if isinstance(node, (ast.Assert, ast.Raise)):
            return True
        # pytest.fail(...) / self.fail(...) are assertions by another name
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Attribute) and fn.attr == "fail":
                return True
        # Nested control flow: a branch that asserts inside a loop or an inner
        # conditional still reaches an assertion on some path.
        for inner in ("body", "orelse", "finalbody"):
            if _has_terminal(getattr(node, inner, []) or []):
                return True
    return False


def _violations(func):
    """Structural masking violations in one test function."""
    found = []
    for node in ast.walk(func):
        if isinstance(node, ast.If):
            if node.orelse or not _mentions_response(node.test):
                continue
            if _has_terminal(node.body):
                found.append(
                    f"line {node.lineno}: one-armed `if` on the response wraps the "
                    f"assertions with no `else` — an error response skips the body "
                    f"and the test passes silently"
                )
        elif isinstance(node, ast.Return) and node.value is None:
            found.append(
                f"line {node.lineno}: bare `return` abandons the remaining "
                f"assertions"
            )
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "skip":
                owner = getattr(fn.value, "id", "")
                if owner == "pytest":
                    found.append(
                        f"line {node.lineno}: `pytest.skip` reports neither pass "
                        f"nor fail — the path under test was never exercised"
                    )
    return found


def test_no_masking_idioms_in_integration_tests():
    """Every path through an integration test must reach an assertion."""
    offenders = []
    for path, func in _iter_test_functions():
        if _exemption(func) is not None:
            continue
        for v in _violations(func):
            offenders.append(f"{path.name}::{func.name} — {v}")

    assert not offenders, (
        f"{len(offenders)} masking idiom(s) found in the integration suite.\n\n"
        + "\n".join(f"  - {o}" for o in offenders)
        + "\n\nA test that cannot fail is worse than no test. Either assert in "
        "every branch (see the hardened pattern in this file's docstring), or "
        "declare the exception:\n"
        f"    @pytest.mark.{MARKER}(reason=\"why this genuinely cannot assert\")"
    )


def test_every_exemption_states_a_reason():
    """An exemption without a cause is how a PRESERVE list rots into a mask list."""
    bad = []
    for path, func in _iter_test_functions():
        reason = _exemption(func)
        if reason is None:
            continue
        if len(reason.strip()) < 15:
            bad.append(
                f"{path.name}::{func.name} — reason is missing or too short to "
                f"be meaningful: {reason!r}"
            )
    assert not bad, (
        f"{len(bad)} exemption(s) without a usable reason:\n\n"
        + "\n".join(f"  - {b}" for b in bad)
        + "\n\nState why the test cannot assert in every branch, e.g. "
        'reason="empty result is the documented off-season state".'
    )


def test_exemptions_are_not_the_norm():
    """A large exemption list means the rule is being routed around."""
    total = exempt = 0
    for _, func in _iter_test_functions():
        total += 1
        if _exemption(func) is not None:
            exempt += 1
    assert total > 0, "no integration tests discovered — is the glob still right?"
    # 10% ceiling: quick task 1's PRESERVE list was ~10 of ~340 tests (3%).
    # Well clear of the ceiling, so this trips only on real drift.
    assert exempt <= total * 0.10, (
        f"{exempt}/{total} integration tests are exempt from the masking rule "
        f"(ceiling is 10%). The exemption is for documented upstream behaviour, "
        f"not a way to keep tolerant tests passing."
    )


@pytest.mark.parametrize(
    "source,should_flag",
    [
        # idiom B — one-armed guard
        ('async def test_x(self):\n    data = await c()\n    if "_meta" in data:\n        assert data["_meta"]\n', True),
        # hardened pattern — both arms assert, must NOT flag
        ('async def test_x(self):\n    data = await c()\n    if "_meta" in data:\n        assert data["_meta"]\n    else:\n        assert data["error"]["code"] in {"UPSTREAM_ERROR"}\n', False),
        # idiom A — early return
        ('async def test_x(self):\n    data = await c()\n    if "error" in data:\n        assert data["error"]["code"] == "UPSTREAM_ERROR"\n        return\n    assert data["_meta"]\n', True),
        # skip
        ('async def test_x(self):\n    data = await c()\n    if not data:\n        pytest.skip("nothing found")\n    assert data["_meta"]\n', True),
        # plain assertion — must NOT flag
        ('async def test_x(self):\n    data = await c()\n    assert "_meta" in data\n', False),
        # conditional on local bookkeeping, not the response — must NOT flag
        ('async def test_x(self):\n    data = await c()\n    assert "_meta" in data\n    for r in data["data"]:\n        if r.get("x"):\n            assert r["x"] > 0\n', False),
    ],
)
def test_detector_behaviour(source, should_flag):
    """The detector itself is tested — a guard nobody trusts gets deleted."""
    func = ast.parse(source).body[0]
    assert bool(_violations(func)) is should_flag, (
        f"detector returned {_violations(func)} for:\n{source}"
    )
