"""New Brunswick module tools — @tool functions for the MCP server.

Every tool:
  - Uses standalone `@tool` from fastmcp.tools (NEVER @mcp.tool)
  - Accepts lang: Literal["en", "fr"] = "en"
  - Returns make_response() on success / make_error() on failure via @upstream_guard
  - Has a docstring with a first line, `Use for:` and a single-line `Keywords:`
  - Uses the `nb_` prefix

TRACER SUBSET (Task 1) — nb_get_crown_land only. Task 4 adds the remaining
21 tools once the Task 2 checkpoint and Task 4 scaffold are in place.
"""

from __future__ import annotations

from typing import Any, Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_response, upstream_guard

from . import client as _client
from .constants import CROWN_LAND_SERVICE, MAX_RECORDS

_API_NAME_GEONB = "new-brunswick-geonb"

__all__ = ["nb_get_crown_land"]


# ---------------------------------------------------------------------------
# Crown Land — Task 1 tracer
# ---------------------------------------------------------------------------


@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_crown_land(
    holder: int | None = None,
    limit: int = MAX_RECORDS,
    lang: Literal["en", "fr"] = "en",
) -> dict[str, Any]:
    """Get New Brunswick Crown Land parcels from GeoNB (geonb.snb.ca), layer 3.

    Use for: retrieving Crown Land parcel records administered by NB Natural
    Resources — holder codes, parcel geometry area/length — from the live
    GeoNB_DNR_Crown_Land ArcGIS Server MapServer. NOTE: `holder` is a raw
    integer holder code with no server-exposed name domain — it is NOT a
    person or organization name; use it only if you already have the code
    from a prior result.

    Keywords: new brunswick crown land parcel holder geonb dnr natural resources provincial forestry tenure arcgis mapserver crown
    """
    payload, cached = await _client.fetch_crown_land(holder=holder, limit=limit)
    return make_response(
        payload,
        api_name=_API_NAME_GEONB,
        api_url=CROWN_LAND_SERVICE,
        cached=cached,
        lang=lang,
    )
