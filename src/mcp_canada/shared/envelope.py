"""Response envelope and error builders for standardized tool responses."""

import functools
import json
import httpx
import pydantic
from collections.abc import Callable

from datetime import datetime, timezone
from typing import Any

# Error code constants
RATE_LIMITED = "RATE_LIMITED"
API_UNAVAILABLE = "API_UNAVAILABLE"
INVALID_INPUT = "INVALID_INPUT"
UPSTREAM_ERROR = "UPSTREAM_ERROR"
NOT_FOUND = "NOT_FOUND"


def make_response(
    data: Any,
    *,
    api_name: str,
    api_url: str,
    cached: bool,
    lang: str = "en",
) -> dict[str, Any]:
    """Wrap data in a standard response envelope with _meta.

    Args:
        data: The response payload.
        api_name: Human-readable name of the upstream API.
        api_url: URL of the upstream API.
        cached: Whether this response was served from cache.
        lang: Language code ('en' or 'fr').

    Returns:
        Dict with '_meta' and 'data' keys.
    """
    return {
        "_meta": {
            "source": {
                "api": api_name,
                "url": api_url,
            },
            "cached": cached,
            "lang": lang,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "data": data,
    }


def make_error(code: str, message: str, lang: str = "en", **extra: Any) -> dict[str, Any]:
    """Build a structured error response.

    Args:
        code: Machine-readable error code (e.g. RATE_LIMITED).
        message: Human-readable error description.
        lang: Language of the message ('en' or 'fr').
        **extra: Additional fields to include in the error dict (e.g. retry_after=5).

    Returns:
        Dict with 'error' key containing code, message, lang, and any extras.
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "lang": lang,
            **extra,
        }
    }


def upstream_guard(api_name: str) -> Callable:
    """Turn an unhandled upstream exception into a structured error envelope.

    Project rule: a tool returns ``make_error(...)`` on failure and never raises
    (``.claude/rules/modules.md``). drug_database and nutrient_file shipped 16
    tools between them with no exception handling at all, so a slow Health
    Canada response escaped as a raw fastmcp ToolError — "Upstream request timed
    out, please retry" — instead of an envelope an agent (or a hardened test)
    can reason about. Nine live scenarios failed that way under full-suite load
    while passing in isolation (Phase 20.1).

    Applied UNDER ``@tool`` so the tool decorator still sees the real signature:

        @tool
        @upstream_guard(_API_NAME)
        async def drug_search(...) -> dict:

    ``functools.wraps`` sets ``__wrapped__``, which ``inspect.signature`` follows,
    so parameter names, annotations and defaults survive for registration.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            lang = kwargs.get("lang", "en")
            try:
                return await fn(*args, **kwargs)
            except httpx.HTTPStatusError as exc:
                return make_error(
                    "UPSTREAM_ERROR",
                    f"{api_name} returned HTTP {exc.response.status_code}",
                    lang=lang,
                )
            except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError) as exc:
                return make_error(
                    "UPSTREAM_ERROR",
                    f"{api_name} request failed: {type(exc).__name__}: {exc}",
                    lang=lang,
                )
            except json.JSONDecodeError as exc:
                # Must precede the ValueError arm — JSONDecodeError subclasses it.
                # An upstream HTML error page reaching httpx's .json() is an
                # upstream failure, not a bad argument from the caller.
                return make_error(
                    "UPSTREAM_ERROR",
                    f"{api_name} returned a malformed JSON body: {exc}",
                    lang=lang,
                )
            except pydantic.ValidationError as exc:
                # Also precedes ValueError — pydantic.ValidationError subclasses
                # it. These models validate UPSTREAM payloads, so a failure here
                # is upstream schema drift, not a bad argument from the caller.
                return make_error(
                    "UPSTREAM_ERROR",
                    f"{api_name} returned a payload that failed validation: {exc}",
                    lang=lang,
                )
            except ValueError as exc:
                # Reached only by an explicit `raise ValueError` for a genuinely
                # bad argument — the two upstream-shaped ValueError subclasses
                # are intercepted above.
                return make_error("INVALID_INPUT", str(exc), lang=lang)
            except Exception as exc:  # noqa: BLE001 — tools must never raise
                # Real catch-all. Flattening code raises KeyError/TypeError/
                # IndexError/AttributeError when an upstream returns valid JSON
                # in an unexpected shape (a BoC observation with no "d", a
                # weather feature with no "properties"). Without this arm those
                # escaped as raw ToolErrors while tests/test_tool_error_handling.py
                # — which treats this decorator as proof of coverage — still passed.
                return make_error(
                    "UPSTREAM_ERROR",
                    f"{api_name} returned an unexpected response shape: "
                    f"{type(exc).__name__}: {exc}",
                    lang=lang,
                )
        return wrapper
    return decorator
