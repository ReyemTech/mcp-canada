"""An upstream failure must be reported as an upstream failure.

Phase 20.2. Two defects, one symptom — an outage that reads as caller error, or
as no envelope at all:

1. 108 tools caught only ``httpx.HTTPStatusError`` (or nothing), so a timeout,
   a connect error or a malformed body escaped as a raw fastmcp ToolError.
2. ``json.JSONDecodeError`` subclasses ``ValueError``, so an upstream HTML error
   page reaching ``.json()`` was caught by the ``except ValueError ->
   INVALID_INPUT`` arms in seven modules and blamed on the caller.

These tests pin the user-visible behaviour rather than the implementation:
whatever an upstream does wrong, the agent gets an error envelope whose code
points at the upstream.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

TRANSIENT = {"UPSTREAM_ERROR", "RATE_LIMITED", "UPSTREAM_UNAVAILABLE"}


def _envelope_code(result: dict) -> str:
    assert "error" in result, f"expected an error envelope, got: {str(result)[:200]}"
    return result["error"]["code"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raised",
    [
        httpx.ReadTimeout("upstream slow"),
        httpx.ConnectError("connection refused"),
        httpx.DecodingError("upstream returned a non-JSON body"),
    ],
    ids=["timeout", "connect-error", "malformed-json"],
)
async def test_ircc_tool_returns_upstream_envelope_not_an_exception(raised):
    """Before 20.2 only HTTPStatusError was caught — these three escaped raw."""
    from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents

    with patch(
        "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
        new=AsyncMock(side_effect=raised),
    ):
        result = await ircc_get_permanent_residents(lang="en")

    assert _envelope_code(result) in TRANSIENT


@pytest.mark.asyncio
async def test_malformed_json_is_not_blamed_on_the_caller():
    """The seven ValueError-arm modules must not report INVALID_INPUT here.

    httpx.DecodingError is deliberately not a ValueError subclass, so it flows
    past `except ValueError` into the catch-all instead of being reported as a
    bad argument.
    """
    from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents

    with patch(
        "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
        new=AsyncMock(side_effect=httpx.DecodingError("non-JSON body")),
    ):
        result = await ircc_get_permanent_residents(lang="en")

    code = _envelope_code(result)
    assert code != "INVALID_INPUT", (
        "an upstream HTML error page was reported as caller error — this is the "
        "masking Phase 20.2 removes"
    )
    assert code in TRANSIENT


@pytest.mark.asyncio
async def test_genuine_bad_input_is_still_invalid_input():
    """The fix must not swallow real argument validation."""
    from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents

    with patch(
        "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
        new=AsyncMock(side_effect=ValueError("unknown breakdown 'bogus'")),
    ):
        result = await ircc_get_permanent_residents(lang="en")

    assert _envelope_code(result) == "INVALID_INPUT"


@pytest.mark.asyncio
async def test_upstream_guard_preserves_lang_on_the_envelope():
    """A French caller must still get a French-tagged envelope from the guard."""
    from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents

    with patch(
        "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
        new=AsyncMock(side_effect=httpx.ReadTimeout("slow")),
    ):
        result = await ircc_get_permanent_residents(lang="fr")

    assert result["error"]["lang"] == "fr"
