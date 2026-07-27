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

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from mcp_canada.shared.errors import InvalidInput

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
        new=AsyncMock(side_effect=InvalidInput("unknown breakdown 'bogus'")),
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


# ---------------------------------------------------------------------------
# Phase 20.3 — the decode guard must cover every portal client, not just CKAN
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "tool_name", "client_fn", "kwargs"),
    [
        ("saskatchewan", "saskatchewan_get_fire_bans", "fetch_fire_bans", {"ban_scope": "urban"}),
        ("saskatchewan", "saskatchewan_get_crop_yields", "fetch_crop_yields", {}),
        ("saskatchewan", "saskatchewan_get_mineral_mines", "fetch_mineral_mines", {"mineral": "potash"}),
        ("manitoba", "manitoba_get_livestock_prices", "fetch_livestock_prices", {}),
        ("manitoba", "manitoba_get_provincial_waterways", "fetch_provincial_waterways", {}),
    ],
)
async def test_arcgis_family_tools_report_decode_failure_as_upstream(
    module, tool_name, client_fn, kwargs
):
    """These five have an `except ValueError -> INVALID_INPUT` arm before their catch-all.

    They must classify a decode failure as upstream. This is the downstream half
    of the Phase 20.3 fix: shared/arcgis_hub.py now raises httpx.DecodingError
    (not a ValueError), so it flows past that arm into the catch-all.
    """
    import importlib

    tools = importlib.import_module(f"mcp_canada.modules.{module}.tools")
    tool = getattr(tools, tool_name)

    with patch(
        f"mcp_canada.modules.{module}.client.{client_fn}",
        new=AsyncMock(side_effect=httpx.DecodingError("non-JSON body")),
    ):
        result = await tool(lang="en", **kwargs)

    code = _envelope_code(result)
    assert code != "INVALID_INPUT", (
        f"{tool_name} blamed the caller for a malformed upstream body"
    )
    assert code in TRANSIENT


@pytest.mark.asyncio
@pytest.mark.parametrize("client_module", ["arcgis_hub", "socrata"])
async def test_portal_clients_convert_bad_json_to_decoding_error(client_module):
    """The upstream half: a 200 carrying HTML must not surface as a ValueError.

    Phase 20.2 guarded shared/http.py only. ArcGIS Hub, OGC WFS and Socrata
    still called response.json() raw, so json.JSONDecodeError -- a ValueError --
    reached the tools' INVALID_INPUT arms.
    """
    import importlib

    mod = importlib.import_module(f"mcp_canada.shared.{client_module}")
    response = MagicMock(spec=httpx.Response)
    response.raise_for_status = MagicMock()
    response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>", 0)

    with pytest.raises(httpx.DecodingError):
        mod.decode_json(response, "https://example.test")

    try:
        mod.decode_json(response, "https://example.test")
    except Exception as exc:  # noqa: BLE001 — asserting the type
        assert not isinstance(exc, ValueError), (
            "a ValueError subclass is swallowed by `except ValueError` arms"
        )


def test_ogc_converts_bad_json_bytes_to_decoding_error():
    """OGC WFS reads response.content, so it needs the bytes variant."""
    from mcp_canada.shared.ogc import decode_json_bytes

    with pytest.raises(httpx.DecodingError):
        decode_json_bytes(b"<html>503 Service Unavailable</html>")

    try:
        decode_json_bytes(b"<html>")
    except Exception as exc:  # noqa: BLE001 — asserting the type
        assert not isinstance(exc, ValueError)


def test_no_shared_portal_client_decodes_json_unguarded():
    """Structural guard: every shared client must decode through the helper.

    Phase 20.3 exists because shared/http.py was fixed and the other three
    portal clients were not. This fails if a raw decode is reintroduced.
    """
    import pathlib
    import re

    shared = pathlib.Path(__file__).resolve().parents[1] / "src" / "mcp_canada" / "shared"
    offenders = []
    for path in sorted(shared.glob("*.py")):
        if path.name == "http.py":  # defines the helpers
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            code = line.split("#")[0]
            if re.search(r"\bresponse\.json\(\)", code) or re.search(r"\bjson\.loads\(", code):
                offenders.append(f"{path.name}:{i}")
    assert offenders == [], (
        "raw JSON decode outside decode_json/decode_json_bytes — a malformed "
        f"upstream body will be reported as INVALID_INPUT: {offenders}"
    )


@pytest.mark.parametrize(
    ("label", "content"),
    [
        ("lone-0xff", b"\xff"),
        ("invalid-utf8-inside-json", b'{"a": "\xff\xfe\xfd"}'),
        ("lone-continuation-byte", b"\x80\x81"),
    ],
)
def test_invalid_byte_encoding_is_also_an_upstream_error(label, content):
    """Undecodable bytes must not be blamed on the caller either.

    json.loads / response.json() raise UnicodeDecodeError -- NOT
    json.JSONDecodeError -- when the body is not valid UTF-8/16/32. Since
    UnicodeDecodeError is *also* a ValueError, guarding only JSONDecodeError
    left the same masking in place for a mangled or truncated body: the
    saskatchewan/manitoba `except ValueError` arms would still report
    INVALID_INPUT. Caught by Codex review on PR #4.
    """
    from mcp_canada.shared.http import decode_json, decode_json_bytes

    with pytest.raises(httpx.DecodingError):
        decode_json_bytes(content, "https://example.test")

    response = MagicMock(spec=httpx.Response)
    response.json.side_effect = UnicodeDecodeError("utf-8", content, 0, 1, "invalid start byte")
    with pytest.raises(httpx.DecodingError):
        decode_json(response, "https://example.test")


def test_decode_helpers_never_raise_a_valueerror_subclass():
    """The whole point: nothing escaping these helpers may be a ValueError."""
    from mcp_canada.shared.http import decode_json_bytes

    for content in (b"\xff", b"<html>503</html>", b"", b"{unclosed"):
        try:
            decode_json_bytes(content)
        except Exception as exc:  # noqa: BLE001 — asserting the type
            assert not isinstance(exc, ValueError), (
                f"{content!r} raised {type(exc).__name__}, a ValueError subclass — "
                "it would be swallowed by an `except ValueError` arm"
            )
