"""Shared fixtures for integration tests."""

import json
from typing import Any

import pytest
from fastmcp import Client

_server_initialized = False


def _extract_text(result: Any) -> str:
    """Extract text from MCP CallToolResult, handling content type union."""
    if result.content:
        item = result.content[0]
        if hasattr(item, "text"):
            return item.text  # type: ignore[no-any-return]
    return "[]"


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


async def call_tool(mcp_server: Any, tool_name: str, arguments: dict | None = None) -> dict:
    """Call a tool through the MCP Client layer and return parsed JSON."""
    async with Client(mcp_server) as client:
        result = await client.call_tool('call_tool', {
            'name': tool_name,
            'arguments': arguments or {},
        })
        return json.loads(_extract_text(result))  # type: ignore[no-any-return]


async def discover(mcp_server: Any, query: str) -> list[dict]:
    """Search for tools via BM25 discover_tools and return parsed results."""
    async with Client(mcp_server) as client:
        result = await client.call_tool('discover_tools', {'query': query})
        text = _extract_text(result)
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []


async def call_direct_tool(mcp_server: Any, tool_name: str, arguments: dict | None = None) -> dict:
    """Call an always-visible tool directly (not through call_tool proxy)."""
    async with Client(mcp_server) as client:
        result = await client.call_tool(tool_name, arguments or {})
        return json.loads(_extract_text(result))  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Live-assertion helpers (Phase 20.1)
#
# Government APIs genuinely go down, so integration tests need a way to tolerate
# an outage without tolerating a bug. The rule: a test may accept an error
# response, but it must assert WHICH error — an unreachable upstream is
# UPSTREAM_ERROR or RATE_LIMITED, while NOT_FOUND or INVALID_INPUT on a call that
# should succeed is a real defect and must fail loudly.
#
# The pattern these replace silently passed on any error:
#
#     assert "_meta" in data or "error" in data   # ← true for both outcomes
#     if "_meta" in data:                          # ← skipped entirely on error
#         assert ...
#
# See tests/test_integration_test_quality.py for the guard that enforces this.
# ---------------------------------------------------------------------------

#: Error codes that a live upstream outage may legitimately produce.
#:
#: UPSTREAM_UNAVAILABLE covers scheduled downtime the tool detects and reports
#: deliberately — StatCan WDS has a documented nightly maintenance window
#: (00:00-08:30 EST) and returns this rather than failing opaquely. Treating it
#: as transient is what lets the suite run overnight; it is still distinct from
#: NOT_FOUND or INVALID_INPUT, which remain hard failures.
TRANSIENT_CODES = frozenset({"UPSTREAM_ERROR", "RATE_LIMITED", "UPSTREAM_UNAVAILABLE"})


def assert_live_or_transient(data: dict, tool: str, api: str | None = None) -> bool:
    """Assert the response is either live data or a *tolerated transient* error.

    Returns True when live data is present, so the caller can go on to assert on
    the payload. Returns False when a transient upstream error was tolerated —
    but only after asserting the error code is genuinely transient.

    Assign the result to a plain local (``live = assert_live_or_transient(...)``)
    rather than branching on the call directly; the masking guard keys off
    conditionals over response-shaped names.

    Args:
        data: parsed tool response.
        tool: tool name, for the failure message.
        api: when given, assert ``_meta.source.api`` equals it.
    """
    if "error" in data:
        code = data.get("error", {}).get("code")
        assert code in TRANSIENT_CODES, (
            f"{tool} returned a NON-transient error. Only {sorted(TRANSIENT_CODES)} "
            f"are tolerated here — anything else is a real defect, not an outage. "
            f"Got: {data['error']}"
        )
        return False

    assert "_meta" in data, (
        f"{tool} returned neither a _meta envelope nor an error. Every tool must "
        f"return one or the other. Got: {data}"
    )
    if api is not None:
        assert data["_meta"]["source"]["api"] == api, (
            f"{tool} _meta.source.api should be {api!r}, got "
            f"{data['_meta']['source'].get('api')!r}"
        )
    return True


def assert_rows(data: dict, tool: str, *, allow_empty_reason: str | None = None) -> list:
    """Return ``data["data"]`` as a list, asserting its type.

    ``allow_empty_reason`` documents why an empty result is a legitimate live
    state (off-season, no active alerts). Without it, empty fails — an empty
    payload is the most common way a broken tool looks healthy.
    """
    rows = data.get("data")
    assert isinstance(rows, list), (
        f"{tool} data should be a list of rows, got {type(rows).__name__}: {rows!r}"
    )
    if not rows:
        assert allow_empty_reason, (
            f"{tool} returned zero rows and empty is not documented as valid here. "
            f"An empty payload is how a broken tool looks healthy — if empty IS "
            f"valid, pass allow_empty_reason= saying why."
        )
    return rows


def assert_feature_payload(data: dict, tool: str) -> dict:
    """Assert the geospatial feature-collection payload shape and return it.

    Feature-query tools (BC WFS, York Region / Alberta / Manitoba / Saskatchewan
    ArcGIS) deliberately return a dict — ``{"features": [...], "count": N,
    "truncated": bool}`` — rather than a bare list, because the truncation flag
    and match count are meaningful to an agent. Tests that assert
    ``isinstance(data["data"], list)`` against these tools are asserting the
    wrong contract.
    """
    payload = data.get("data")
    assert isinstance(payload, dict), (
        f"{tool} returns a feature-collection dict, not a bare "
        f"{type(payload).__name__}. Expected keys: features, count, truncated."
    )
    assert "features" in payload, f"{tool} payload missing features: {list(payload)}"
    assert isinstance(payload["features"], list), (
        f"{tool} features must be a list, got {type(payload['features']).__name__}"
    )
    return payload


def assert_series_payload(data: dict, tool: str, *series_names: str) -> dict:
    """Assert the series-keyed observation payload shape and return it.

    BOC observation tools return a dict keyed by series name — deliberately, as
    of the 2026-04-09 shared/reshape.py refactor — rather than a flat list that
    repeats the label and description on every row::

        {"FXUSDCAD": {"label": "USD/CAD",
                      "description": "...",
                      "observations": {"2026-07-23": 1.39}}}

    Each named series must be present and carry a non-empty observations map.
    """
    payload = data.get("data")
    assert isinstance(payload, dict), (
        f"{tool} returns a series-keyed dict, not a bare "
        f"{type(payload).__name__}. See shared/reshape.py:reshape_observations."
    )
    for name in series_names:
        assert name in payload, (
            f"{tool} payload missing series {name!r}; got {list(payload)}"
        )
        series = payload[name]
        assert "observations" in series, (
            f"{tool} series {name!r} missing observations: {list(series)}"
        )
        assert series["observations"], (
            f"{tool} series {name!r} has an empty observations map — a published "
            f"BOC series should always have values: {series}"
        )
    return payload
