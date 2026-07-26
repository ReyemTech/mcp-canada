"""Tests for shared/http.py — retry logic."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch


def test_retryable_status_codes():
    """is_retryable should return True for 429, 500, 502, 503, 504."""
    from mcp_canada.shared.http import is_retryable

    for code in [429, 500, 502, 503, 504]:
        exc = httpx.HTTPStatusError(
            f"HTTP {code}",
            request=httpx.Request("GET", "https://example.com"),
            response=httpx.Response(code),
        )
        assert is_retryable(exc) is True, f"Expected True for status {code}"


def test_non_retryable_status_codes():
    """is_retryable should return False for 400, 401, 404."""
    from mcp_canada.shared.http import is_retryable

    for code in [400, 401, 404]:
        exc = httpx.HTTPStatusError(
            f"HTTP {code}",
            request=httpx.Request("GET", "https://example.com"),
            response=httpx.Response(code),
        )
        assert is_retryable(exc) is False, f"Expected False for status {code}"


def test_retryable_connect_error():
    """is_retryable should return True for ConnectError."""
    from mcp_canada.shared.http import is_retryable

    exc = httpx.ConnectError("Connection refused")
    assert is_retryable(exc) is True


def test_retryable_timeout_exception():
    """is_retryable should return True for TimeoutException."""
    from mcp_canada.shared.http import is_retryable

    exc = httpx.TimeoutException("Timeout")
    assert is_retryable(exc) is True


def test_non_retryable_other_exception():
    """is_retryable should return False for unrelated exceptions."""
    from mcp_canada.shared.http import is_retryable

    assert is_retryable(ValueError("not an HTTP error")) is False


@pytest.mark.asyncio
async def test_retry_on_429():
    """with_retry should retry up to 3 times on 429 status."""
    from mcp_canada.shared.http import with_retry

    call_count = 0

    @with_retry
    async def flaky_call():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.HTTPStatusError(
                "429",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(429),
            )
        return "ok"

    # Patch tenacity sleep to avoid actual waiting
    with patch("tenacity.nap.sleep"):
        result = await flaky_call()

    assert result == "ok"
    assert call_count == 3


@pytest.mark.asyncio
async def test_no_retry_on_400():
    """with_retry should NOT retry on 400 status."""
    from mcp_canada.shared.http import with_retry

    call_count = 0

    @with_retry
    async def bad_request():
        nonlocal call_count
        call_count += 1
        raise httpx.HTTPStatusError(
            "400",
            request=httpx.Request("GET", "https://example.com"),
            response=httpx.Response(400),
        )

    with pytest.raises(httpx.HTTPStatusError):
        await bad_request()

    assert call_count == 1  # Only called once, no retry


# ===========================================================================
# api_get tests
# ===========================================================================

@pytest.mark.asyncio
async def test_api_get_returns_json_on_success():
    """api_get should return parsed JSON response on 200."""
    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_get("https://example.com/api")

    assert result == {"key": "value"}
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_api_get_passes_headers_when_provided():
    """api_get should pass custom headers to the HTTP request."""
    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "ok"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    custom_headers = {"Accept": "application/json"}
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_get("https://example.com/api", headers=custom_headers)

    mock_client.get.assert_called_once_with(
        "https://example.com/api",
        params=None,
        headers=custom_headers,
    )
    assert result == {"data": "ok"}


@pytest.mark.asyncio
async def test_api_get_works_without_headers():
    """api_get should work when headers=None (default)."""
    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_get("https://example.com/api")

    mock_client.get.assert_called_once_with(
        "https://example.com/api",
        params=None,
        headers=None,
    )
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_get_raises_on_404():
    """api_get should raise HTTPStatusError on 404 response."""
    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=httpx.Request("GET", "https://example.com/api"),
        response=httpx.Response(404),
    )

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await api_get("https://example.com/api")


@pytest.mark.asyncio
async def test_api_get_retries_on_429():
    """api_get should retry on 429 via with_retry."""
    from mcp_canada.shared.http import api_get

    call_count = 0

    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    async def mock_get(url, params=None, headers=None):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            response = MagicMock()
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "429",
                request=httpx.Request("GET", url),
                response=httpx.Response(429),
            )
            return response
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"data": "ok"}
        return response

    mock_client_instance.get = mock_get

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        with patch("tenacity.nap.sleep"):
            result = await api_get("https://example.com/api")

    assert result == {"data": "ok"}
    assert call_count == 3


@pytest.mark.asyncio
async def test_api_get_raises_decoding_error_not_valueerror_on_malformed_body():
    """HTTP 200 carrying HTML must not surface as a ValueError.

    json.JSONDecodeError subclasses ValueError, so a Health Canada / CKAN error
    page reaching .json() lands in the `except ValueError -> INVALID_INPUT` arms
    of statcan, ircc, manitoba, saskatchewan, nova_scotia, british_columbia and
    datastore — blaming the caller for an upstream outage. Raising
    httpx.DecodingError keeps it out of those arms while remaining an
    httpx.HTTPError, which every module's catch-all already maps to
    UPSTREAM_ERROR.
    """
    import json

    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>", 0)

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.DecodingError):
            await api_get("https://example.com/api")


@pytest.mark.asyncio
async def test_api_get_decoding_error_is_not_a_valueerror():
    """Pin the property the seven ValueError-arm modules depend on."""
    import json

    from mcp_canada.shared.http import api_get

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>", 0)

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        try:
            await api_get("https://example.com/api")
        except Exception as exc:  # noqa: BLE001 — asserting the type below
            assert not isinstance(exc, ValueError), (
                "a ValueError subclass would be swallowed by `except ValueError` "
                "arms and reported as INVALID_INPUT"
            )
            assert isinstance(exc, httpx.HTTPError), (
                "must stay an HTTPError so existing catch-alls map it to UPSTREAM_ERROR"
            )
        else:
            pytest.fail("api_get should have raised on a malformed body")
