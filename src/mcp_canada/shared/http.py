"""Shared httpx client factory with tenacity retry logic."""

import json
from collections.abc import Callable
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)


def is_retryable(exc: BaseException) -> bool:
    """Return True if the exception warrants a retry."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False


def with_retry(func: Callable) -> Callable:
    """Decorator that applies tenacity retry with exponential backoff."""
    return retry(
        retry=retry_if_exception(is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )(func)


async def api_get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> Any:
    """Shared GET helper with retry, optional headers.

    Args:
        url: Full URL to fetch.
        params: Query parameters.
        headers: Optional HTTP headers (e.g. {"Accept": "application/json"}).
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response.
    """
    @with_retry
    async def _fetch() -> Any:
        async with httpx.AsyncClient(timeout=timeout) as http:
            response = await http.get(url, params=params, headers=headers)
            response.raise_for_status()
            try:
                return response.json()
            except json.JSONDecodeError as exc:
                # An upstream that answers 200 with an HTML error page is an
                # upstream failure, but json.JSONDecodeError subclasses
                # ValueError and would be caught by the
                # `except ValueError -> INVALID_INPUT` arms in statcan, ircc,
                # manitoba, saskatchewan, nova_scotia, british_columbia and
                # datastore — blaming the caller for someone else's outage.
                # httpx.DecodingError is an httpx.HTTPError but NOT a
                # ValueError, so it bypasses those arms and lands in the
                # catch-all every module now has.
                raise httpx.DecodingError(
                    f"upstream returned a non-JSON body from {url}: {exc}"
                ) from exc

    return await _fetch()
