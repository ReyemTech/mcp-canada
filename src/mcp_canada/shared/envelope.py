"""Response envelope and error builders for standardized tool responses."""

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
