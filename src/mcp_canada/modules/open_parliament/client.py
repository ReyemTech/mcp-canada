"""Open Parliament API client.

Provides async functions for fetching, caching, and rate-limiting all
Open Parliament API endpoints. All public functions return (data, was_cached) tuples.

Uses the shared api_get() helper from shared/http.py with API_HEADERS to set
the Accept: application/json header on every request.
"""

from typing import Any

from mcp_canada.modules.open_parliament.constants import (
    API_HEADERS,
    BASE_URL,
    CACHE_TTL_DATA,
    RATE_GROUP,
    RATE_LIMIT,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.http import api_get
from mcp_canada.shared.rate_limiter import get_limiter


def _safe_get(obj: Any, *keys: str, default: Any = None) -> Any:
    """Safely access nested dict keys without raising on missing keys.

    Args:
        obj: The dict to traverse.
        *keys: Sequence of keys to traverse in order.
        default: Value to return if any key is missing (default: None).

    Returns:
        The nested value if found, otherwise default.
    """
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current


def _build_cache_key(path: str, params: dict[str, Any]) -> str:
    """Build a deterministic cache key from path and sorted params."""
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"parl:{path}?{sorted_params}"


async def _parl_get(
    path: str,
    params: dict[str, Any],
    cache_ttl: int,
) -> tuple[Any, bool]:
    """Internal helper: fetch from Open Parliament API with caching and rate limiting.

    Args:
        path: API path relative to BASE_URL (e.g. "bills/").
        params: Query parameters dict.
        cache_ttl: Cache TTL in seconds.

    Returns:
        (response_json, was_cached)
    """
    url = BASE_URL + path
    cache_key = _build_cache_key(path, params)
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        return await api_get(url, params=params, headers=API_HEADERS)

    return await cached_fetch(cache_key, cache_ttl, fetcher)


async def fetch_bills(
    search: str | None = None,
    session: str | None = None,
    status: str | None = None,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a paginated list of federal bills.

    Args:
        search: Optional keyword search.
        session: Optional parliament session (e.g. "44-1").
        status: Optional bill status filter.
        page: Page number (default 1).

    Returns:
        (list of bill dicts, was_cached)
    """
    params: dict[str, Any] = {"page": page}
    if search is not None:
        params["q"] = search
    if session is not None:
        params["session"] = session
    if status is not None:
        params["status"] = status

    raw, was_cached = await _parl_get("bills/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached


async def fetch_bill_details(
    bill_id: str,
) -> tuple[dict[str, Any], bool]:
    """Fetch details for a single bill.

    Args:
        bill_id: Bill identifier in format "session/number" (e.g. "44-1/C-11").

    Returns:
        (bill detail dict, was_cached)
    """
    raw, was_cached = await _parl_get(f"bills/{bill_id}/", {}, CACHE_TTL_DATA)
    return raw, was_cached


async def fetch_politicians(
    name: str | None = None,
    party: str | None = None,
    province: str | None = None,
    riding: str | None = None,
    current: bool | None = None,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a paginated list of politicians/MPs.

    Args:
        name: Optional name search.
        party: Optional party filter.
        province: Optional province filter.
        riding: Optional riding filter.
        current: Optional current MP filter (True = current MPs only).
        page: Page number (default 1).

    Returns:
        (list of politician dicts, was_cached)
    """
    params: dict[str, Any] = {"page": page}
    if name is not None:
        params["name"] = name
    if party is not None:
        params["party"] = party
    if province is not None:
        params["province"] = province
    if riding is not None:
        params["riding"] = riding
    if current is not None:
        params["current"] = str(current).lower()

    raw, was_cached = await _parl_get("politicians/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached


async def fetch_votes(
    session: str | None = None,
    bill: str | None = None,
    result: str | None = None,
    politician: str | None = None,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a paginated list of House of Commons votes.

    Args:
        session: Optional parliament session filter.
        bill: Optional bill filter.
        result: Optional result filter (e.g. "Passed", "Failed").
        politician: Optional politician URL for voting record.
        page: Page number (default 1).

    Returns:
        (list of vote dicts, was_cached)
    """
    params: dict[str, Any] = {"page": page}
    if session is not None:
        params["session"] = session
    if bill is not None:
        params["bill"] = bill
    if result is not None:
        params["result"] = result
    if politician is not None:
        params["politician"] = politician

    raw, was_cached = await _parl_get("votes/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached


async def fetch_debates(
    date: str | None = None,
    politician: str | None = None,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a paginated list of Hansard debate entries.

    Args:
        date: Optional date filter (ISO 8601 date string).
        politician: Optional politician URL filter.
        page: Page number (default 1).

    Returns:
        (list of debate entry dicts, was_cached)
    """
    params: dict[str, Any] = {"page": page}
    if date is not None:
        params["date"] = date
    if politician is not None:
        params["politician"] = politician

    raw, was_cached = await _parl_get("debates/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached


async def fetch_ballots(
    vote_url: str,
    politician: str | None = None,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch individual MP ballots for a specific recorded division.

    Args:
        vote_url: Vote URL path (e.g. "/votes/44-1/333/").
        politician: Optional politician URL path to filter to one MP's ballot.
        page: Page number (default 1).

    Returns:
        (list of ballot dicts with ballot/politician_url/vote_url, was_cached)
    """
    params: dict[str, Any] = {"vote": vote_url, "limit": 20, "offset": (page - 1) * 20}
    if politician is not None:
        params["politician"] = politician

    raw, was_cached = await _parl_get("votes/ballots/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached


async def fetch_hansard_search(
    query: str,
    page: int = 1,
) -> tuple[list[dict[str, Any]], bool]:
    """Full-text search of Hansard debate content.

    Args:
        query: Search query string.
        page: Page number (default 1).

    Returns:
        (list of search result dicts, was_cached)
    """
    params: dict[str, Any] = {"q": query, "page": page}
    raw, was_cached = await _parl_get("search/", params, CACHE_TTL_DATA)
    objects: list[dict[str, Any]] = raw.get("objects", [])
    return objects, was_cached
