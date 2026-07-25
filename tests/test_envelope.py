"""Tests for shared/envelope.py — response envelope and error builders."""

import pytest


from datetime import datetime


def test_response_has_meta_fields():
    """make_response should include _meta with source, cached, lang, timestamp, and data."""
    from mcp_canada.shared.envelope import make_response

    payload = {"rate": 1.25}
    result = make_response(
        payload,
        api_name="Bank of Canada",
        api_url="https://www.bankofcanada.ca/valet",
        cached=True,
        lang="en",
    )

    assert "_meta" in result
    assert "data" in result
    assert result["data"] == payload

    meta = result["_meta"]
    assert meta["source"]["api"] == "Bank of Canada"
    assert meta["source"]["url"] == "https://www.bankofcanada.ca/valet"
    assert meta["cached"] is True
    assert meta["lang"] == "en"
    # timestamp should be ISO 8601
    assert "timestamp" in meta
    datetime.fromisoformat(meta["timestamp"])  # raises if not valid ISO 8601


def test_error_format():
    """make_error should return structured error dict."""
    from mcp_canada.shared.envelope import make_error

    result = make_error("RATE_LIMITED", "Too many requests", lang="fr")

    assert "error" in result
    error = result["error"]
    assert error["code"] == "RATE_LIMITED"
    assert error["message"] == "Too many requests"
    assert error["lang"] == "fr"


def test_error_extra_kwargs():
    """make_error should include extra kwargs in the error dict."""
    from mcp_canada.shared.envelope import make_error

    result = make_error("RATE_LIMITED", "Slow down", retry_after=5)

    assert result["error"]["retry_after"] == 5


def test_response_default_lang():
    """make_response should default to 'en' lang."""
    from mcp_canada.shared.envelope import make_response

    result = make_response({}, api_name="Test", api_url="https://example.com", cached=False)
    assert result["_meta"]["lang"] == "en"


def test_error_constants_available():
    """Error code constants should be importable from envelope."""
    from mcp_canada.shared.envelope import (
        RATE_LIMITED,
        API_UNAVAILABLE,
        INVALID_INPUT,
        UPSTREAM_ERROR,
        NOT_FOUND,
    )

    assert RATE_LIMITED == "RATE_LIMITED"
    assert API_UNAVAILABLE == "API_UNAVAILABLE"
    assert INVALID_INPUT == "INVALID_INPUT"
    assert UPSTREAM_ERROR == "UPSTREAM_ERROR"
    assert NOT_FOUND == "NOT_FOUND"


class TestUpstreamGuard:
    """Tools must return a structured error, never raise (project rule).

    Regression cover for the Phase 20.1 finding: drug_database and nutrient_file
    shipped 16 tools between them with ZERO exception handling, so an upstream
    timeout escaped as a raw fastmcp ToolError ("Upstream request timed out,
    please retry") instead of an error envelope. Under a full live-suite run the
    Health Canada Drug API is slow enough to trigger this, and 9 scenarios failed
    with an unhandled exception rather than a tolerable UPSTREAM_ERROR.
    """

    @pytest.mark.asyncio
    async def test_timeout_becomes_structured_error(self):
        import httpx
        from mcp_canada.shared.envelope import upstream_guard

        @upstream_guard("test-api")
        async def boom(lang: str = "en") -> dict:
            raise httpx.ReadTimeout("upstream slow")

        result = await boom()
        assert "error" in result, f"expected an envelope, got: {result}"
        assert result["error"]["code"] == "UPSTREAM_ERROR"
        assert "test-api" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_http_status_error_becomes_structured_error(self):
        import httpx
        from mcp_canada.shared.envelope import upstream_guard

        @upstream_guard("test-api")
        async def boom(lang: str = "en") -> dict:
            request = httpx.Request("GET", "https://example.test")
            response = httpx.Response(503, request=request)
            raise httpx.HTTPStatusError("503", request=request, response=response)

        result = await boom()
        assert result["error"]["code"] == "UPSTREAM_ERROR"
        assert "503" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_lang_is_propagated(self):
        import httpx
        from mcp_canada.shared.envelope import upstream_guard

        @upstream_guard("test-api")
        async def boom(lang: str = "en") -> dict:
            raise httpx.ReadTimeout("slow")

        result = await boom(lang="fr")
        assert result["error"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_success_passes_through_untouched(self):
        from mcp_canada.shared.envelope import upstream_guard

        @upstream_guard("test-api")
        async def fine(lang: str = "en") -> dict:
            return {"_meta": {}, "data": [1, 2, 3]}

        assert await fine() == {"_meta": {}, "data": [1, 2, 3]}

    @pytest.mark.asyncio
    async def test_signature_is_preserved_for_tool_registration(self):
        """@tool introspects the signature — the guard must not hide it."""
        import inspect
        from mcp_canada.shared.envelope import upstream_guard

        @upstream_guard("test-api")
        async def typed(drug_code: int, lang: str = "en") -> dict:
            return {}

        params = inspect.signature(typed).parameters
        assert "drug_code" in params, "wrapped signature lost — @tool would break"
        assert params["drug_code"].annotation is int
