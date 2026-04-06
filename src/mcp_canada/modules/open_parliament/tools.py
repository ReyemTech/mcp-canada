"""Open Parliament @tool functions for the Open Parliament API.

Provides 9 intent-based MCP tools for querying Canadian federal parliamentary data:
bills, MPs, votes, Hansard debates, and full-text search.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.open_parliament.client import (
    fetch_ballots,
    fetch_bill_details,
    fetch_bills,
    fetch_debates,
    fetch_hansard_search,
    fetch_politicians,
    fetch_votes,
)
from mcp_canada.modules.open_parliament.constants import BASE_URL
from mcp_canada.shared.envelope import make_error, make_response

# API name and base URL for _meta envelope
_API_NAME = "Open Parliament"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Search bills — PARL-01
# ---------------------------------------------------------------------------

@tool
async def parl_search_bills(
    keyword: str | None = None,
    session: str | None = None,
    status: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Canadian federal bills filtered by session or status.

    Use for: browsing bills from a specific parliament session (e.g. '42-1') or
    filtering by status (e.g. 'Royal Assent'). Note: the keyword param does NOT
    search bill titles or content — it is unreliable. To find a specific bill,
    use parl_get_bill_details with the bill ID (e.g. '42-1/C-45'), or use
    parl_search_hansard to search debate transcripts by topic.
    Keywords: bill, legislation, federal, parliament, session, status, law, act,
    royal assent, introduced, sponsor, C-11, S-1, private member, government bill.
    """
    try:
        bills, cached = await fetch_bills(
            search=keyword,
            session=session,
            status=status,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                "No bills found matching the specified criteria.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch bills: {exc}",
            lang=lang,
        )

    return make_response(
        bills,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Get bill details — PARL-02
# ---------------------------------------------------------------------------

@tool
async def parl_get_bill_details(
    bill_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get full details for a specific Canadian federal bill including sponsor and status history.

    Use for: retrieving complete information about a specific bill when you know
    its identifier, including vote links, text, summary, and sponsor information.
    Keywords: bill, detail, sponsor, status, history, vote, text, summary, parliament,
    legislation, session, C-11, royal assent, reading, committee, amendment.
    """
    try:
        bill, cached = await fetch_bill_details(bill_id=bill_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"Bill '{bill_id}' not found. Use parl_search_bills to find the correct bill ID.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch bill details: {exc}",
            lang=lang,
        )

    return make_response(
        bill,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Get politicians / MPs — PARL-03
# ---------------------------------------------------------------------------

@tool
async def parl_get_politicians(
    name: str | None = None,
    party: str | None = None,
    province: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search or list Canadian Members of Parliament by name, party, or province.

    Use for: finding MPs by their name, political party affiliation, or the province
    they represent. Returns current and historical MPs from Parliament of Canada.
    Keywords: mp, member of parliament, politician, party, province, liberal, conservative,
    ndp, bloc, green, riding, elected, house of commons, senator, federal.
    """
    try:
        politicians, cached = await fetch_politicians(
            name=name,
            party=party,
            province=province,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                "No politicians found matching the specified criteria.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch politicians: {exc}",
            lang=lang,
        )

    return make_response(
        politicians,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Search by riding — PARL-04
# ---------------------------------------------------------------------------

@tool
async def parl_search_by_riding(
    riding: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Find the MP or politician for a specific electoral riding in Canada.

    Use for: looking up who represents a specific electoral district or riding
    in the House of Commons, past or present.
    Keywords: riding, electoral district, constituency, mp, representative,
    papineau, carleton, toronto, vancouver, quebec, riding name, local mp.
    """
    try:
        politicians, cached = await fetch_politicians(riding=riding)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"No politicians found for riding '{riding}'.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch politicians by riding: {exc}",
            lang=lang,
        )

    return make_response(
        politicians,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Get party members — PARL-05
# ---------------------------------------------------------------------------

@tool
async def parl_get_party_members(
    party: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get the current Members of Parliament for a specific political party.

    Use for: listing all current MPs belonging to a political party such as
    Liberal, Conservative, NDP, Bloc Québécois, or Green Party.
    Keywords: party, caucus, members, liberal, conservative, ndp, bloc, green,
    mp list, current mps, party caucus, political party, house of commons members.
    """
    try:
        politicians, cached = await fetch_politicians(party=party, current=True)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"No current MPs found for party '{party}'.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch party members: {exc}",
            lang=lang,
        )

    return make_response(
        politicians,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Get House of Commons votes — PARL-06
# ---------------------------------------------------------------------------

@tool
async def parl_get_votes(
    session: str | None = None,
    bill: str | None = None,
    result: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get House of Commons vote records, optionally filtered by session, bill, or result.

    Use for: finding how the House voted on bills or motions, with tally counts
    for yeas, nays, and paired votes. Supports filtering by session or bill.
    Keywords: vote, division, yea, nay, passed, failed, motion, bill, house of commons,
    parliament, result, tally, voting record, recorded division, session.
    """
    try:
        votes, cached = await fetch_votes(
            session=session,
            bill=bill,
            result=result,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                "No votes found matching the specified criteria.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch votes: {exc}",
            lang=lang,
        )

    return make_response(
        votes,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Get MP voting record — PARL-07
# ---------------------------------------------------------------------------

@tool
async def parl_get_voting_record(
    politician: str,
    session: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get votes an MP participated in, with house-wide totals per division.

    Use for: seeing which recorded divisions an MP participated in and the
    overall result (agreed/negatived) with yea/nay totals. Note: the API returns
    house-wide vote totals, NOT the individual MP's yea/nay on each division.
    Politician is a slug (e.g. 'justin-trudeau').
    Keywords: voting record, mp vote, division, politician, recorded vote,
    participation, session, member of parliament, votes participated.
    """
    try:
        votes, cached = await fetch_votes(
            politician=politician,
            session=session,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"No voting record found for politician '{politician}'.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch voting record: {exc}",
            lang=lang,
        )

    return make_response(
        votes,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Get Hansard debates — PARL-08
# ---------------------------------------------------------------------------

@tool
async def parl_get_debates(
    date: str | None = None,
    politician: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Hansard debate transcripts from the House of Commons.

    Use for: retrieving transcripts of speeches and debate from the House of Commons
    Hansard, filtered by date or specific politician. Returns bilingual content.
    Keywords: hansard, debate, transcript, speech, house of commons, mp speech,
    parliament, proceedings, statement, question period, reading, committee debate.
    """
    try:
        debates, cached = await fetch_debates(
            date=date,
            politician=politician,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                "No debates found matching the specified criteria.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch debates: {exc}",
            lang=lang,
        )

    return make_response(
        debates,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 9: Search Hansard full-text — PARL-09
# ---------------------------------------------------------------------------

@tool
async def parl_search_hansard(
    query: str,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Full-text search of Canadian Hansard debate transcripts.

    Use for: searching across all Hansard speeches for specific topics, keywords,
    or phrases spoken in the House of Commons. Returns matching speech excerpts
    with politician attribution and date.
    Keywords: hansard, search, full-text, speech, debate, transcript, keyword,
    topic, parliament, mp speech, house of commons, what was said, spoken words.
    """
    try:
        results, cached = await fetch_hansard_search(query=query, page=page)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"No Hansard results found for query '{query}'.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to search Hansard: {exc}",
            lang=lang,
        )

    return make_response(
        results,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 10: Get individual MP ballots — PARL-10
# ---------------------------------------------------------------------------

@tool
async def parl_get_ballots(
    vote_id: str,
    politician: str | None = None,
    page: int = 1,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get individual MP yea/nay ballots for a specific House of Commons vote.

    Use for: finding exactly how an MP voted (yea/nay/paired) on a specific
    recorded division. Pass vote_id as 'session/number' (e.g. '44-1/333') and
    optionally a politician slug to get one MP's ballot. Without politician,
    returns all ballots for that vote (paginated).
    Keywords: ballot, individual vote, yea, nay, how voted, mp vote, division,
    recorded vote, specific vote, paired, abstain.
    """
    vote_url = f"/votes/{vote_id}/"

    politician_url = None
    if politician is not None:
        politician_url = f"/politicians/{politician}/"

    try:
        ballots, cached = await fetch_ballots(
            vote_url=vote_url,
            politician=politician_url,
            page=page,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return make_error(
                "NOT_FOUND",
                f"No ballots found for vote '{vote_id}'.",
                lang=lang,
            )
        return make_error(
            "UPSTREAM_ERROR",
            f"Open Parliament API error: {exc.response.status_code}",
            lang=lang,
        )
    except Exception as exc:
        return make_error(
            "UPSTREAM_ERROR",
            f"Failed to fetch ballots: {exc}",
            lang=lang,
        )

    return make_response(
        ballots,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
