"""Tests for shared/envelope.py — response envelope and error builders."""

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
