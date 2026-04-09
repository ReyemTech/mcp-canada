"""MCP resources for the Open Parliament module.

Provides reference catalogs, documentation guides, and response templates for
the Open Parliament API. All resources use type-prefixed URIs:
- data://parliament/...    — JSON reference catalogs (machine-parseable)
- docs://parliament/...    — Markdown documentation guides (human-readable)
- template://parliament/...— Markdown response templates with {placeholder} syntax

IMPORTANT: All resource functions are zero-parameter. Adding any parameter
(even lang) would make FastMCP treat them as ResourceTemplate instead of
FunctionResource, removing them from resources/list.
Bilingual content is embedded inline in a single resource.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://parliament/party-codes",
    mime_type="application/json",
    name="parl_party_codes",
    title="Canadian Political Party Codes",
)
def parl_party_codes() -> str:
    """Valid party codes used in the Open Parliament API.

    Use this catalog to find the party parameter for parl_get_party_members.
    Format: {"CODE": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "CPC": {
                "en": "Conservative Party of Canada",
                "fr": "Parti conservateur du Canada",
            },
            "LPC": {
                "en": "Liberal Party of Canada",
                "fr": "Parti libéral du Canada",
            },
            "NDP": {
                "en": "New Democratic Party",
                "fr": "Nouveau Parti démocratique",
            },
            "BQ": {
                "en": "Bloc Québécois",
                "fr": "Bloc Québécois",
            },
            "GPC": {
                "en": "Green Party of Canada",
                "fr": "Parti vert du Canada",
            },
            "IND": {
                "en": "Independent",
                "fr": "Indépendant",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://parliament/session-format",
    mime_type="application/json",
    name="parl_session_format",
    title="Parliamentary Session Format Explained",
)
def parl_session_format() -> str:
    """Explains the parliamentary session identifier format used by the API.

    The format '44-1' means the 44th Parliament, 1st Session.
    Use this to understand session parameters in parl_get_votes, parl_get_debates, etc.
    """
    return json.dumps(
        {
            "format": "{parliament_number}-{session_number}",
            "example": "44-1",
            "explanation": {
                "en": "44 = 44th Parliament, 1 = 1st Session of that Parliament",
                "fr": "44 = 44e Parlement, 1 = 1re session de ce Parlement",
            },
            "current_session": {
                "value": "44-1",
                "parliament": 44,
                "session": 1,
                "started": "2021-11-22",
                "en": "44th Parliament, 1st Session (elected Sept 2021)",
                "fr": "44e Parlement, 1re session (élu en septembre 2021)",
            },
            "recent_sessions": [
                {
                    "value": "43-2",
                    "en": "43rd Parliament, 2nd Session (2020-2021)",
                    "fr": "43e Parlement, 2e session (2020-2021)",
                },
                {
                    "value": "43-1",
                    "en": "43rd Parliament, 1st Session (2019-2020)",
                    "fr": "43e Parlement, 1re session (2019-2020)",
                },
                {
                    "value": "42-1",
                    "en": "42nd Parliament, 1st Session (2015-2019)",
                    "fr": "42e Parlement, 1re session (2015-2019)",
                },
            ],
            "note": {
                "en": "Omit session to search across all sessions",
                "fr": "Omettez la session pour chercher dans toutes les sessions",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://parliament/bill-types",
    mime_type="application/json",
    name="parl_bill_types",
    title="Canadian Parliamentary Bill Type Prefixes",
)
def parl_bill_types() -> str:
    """Bill type prefixes used in the Canadian Parliament.

    Use this to interpret bill numbers when searching with parl_search_bills.
    Format: {"PREFIX": {"origin": "...", "en": "description", "fr": "description"}}
    """
    return json.dumps(
        {
            "C-": {
                "origin": "House of Commons",
                "en": "Government bill introduced in the House of Commons",
                "fr": "Projet de loi gouvernemental présenté à la Chambre des communes",
                "example": "C-21 (firearm policy bill)",
            },
            "S-": {
                "origin": "Senate",
                "en": "Government bill introduced in the Senate",
                "fr": "Projet de loi gouvernemental présenté au Sénat",
                "example": "S-7 (fighting foreign influence bill)",
            },
            "C-2xx": {
                "origin": "House of Commons — Private Member",
                "en": "Private member's bill introduced by an MP (numbers 200-299)",
                "fr": "Projet de loi d'initiative parlementaire présenté par un député (numéros 200-299)",
                "example": "C-234 (carbon tax exemption bill)",
            },
            "S-2xx": {
                "origin": "Senate — Private Member",
                "en": "Private senator's bill (numbers 200-299)",
                "fr": "Projet de loi d'initiative sénatoriale (numéros 200-299)",
                "example": "S-205 (intimate partner violence bill)",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://parliament/voting-guide",
    mime_type="text/markdown",
    name="parl_voting_guide",
    title="Guide to Parliamentary Votes and Ballots",
)
def parl_voting_guide() -> str:
    """Guide to how parliamentary votes work and how to interpret vote results.

    Covers divisions, ballot types (yea/nay/paired/absent), and vote outcomes.
    """
    return """# Guide to Canadian Parliamentary Votes

## How Votes Work

When the House of Commons holds a vote (called a "division"), each MP records
their ballot as either:
- **Yea** — in favour of the motion
- **Nay** — against the motion
- **Paired** — absent by agreement (paired MPs cancel each other out)

The motion passes if Yeas > Nays (including the Speaker's casting vote on ties).

## Finding Votes with the API

Use `parl_get_votes` to search for divisions by keyword or session.
Each vote result includes:
- `number` — unique vote number within the session (e.g., 333)
- `session` — parliament-session identifier (e.g., "44-1")
- `date` — date of the division
- `description` — what was being voted on
- `result` — "passed" or "failed"
- `yea_total` / `nay_total` — aggregate counts

## Individual MP Ballots

Use `parl_get_ballots` with the vote session + number to see how each MP voted.
Note: The API returns **house-wide totals**, not individual MP votes for all endpoints.
Use `parl_get_voting_record` for an MP's complete voting history.

## Interpreting Results

| Result | Meaning |
|--------|---------|
| passed | Yeas outnumbered Nays — motion carried |
| failed | Nays outnumbered Yeas — motion defeated |

## Tools Reference

- `parl_get_votes` — Search for divisions by keyword or date
- `parl_get_ballots` — Individual MP votes for a specific division
- `parl_get_voting_record` — All votes cast by a specific MP
"""


@resource(
    "docs://parliament/hansard-guide",
    mime_type="text/markdown",
    name="parl_hansard_guide",
    title="Guide to Searching Hansard Debate Transcripts",
)
def parl_hansard_guide() -> str:
    """Guide to what Hansard is and how to search parliamentary debate transcripts.

    Covers what Hansard is, search strategies, and debate structure.
    """
    return """# Guide to Hansard: Canadian Parliamentary Debate Transcripts

## What is Hansard?

Hansard is the official verbatim record of Canadian parliamentary debates.
It records everything said in the House of Commons during sittings,
including member statements, question period, and committee debates.

The name comes from Thomas Curson Hansard, the first publisher of British
parliamentary debates. Canada has maintained Hansard records since 1870.

## Searching Hansard

Use `parl_search_hansard` to search the full text of debate transcripts:

```
parl_search_hansard(query="carbon tax", session="44-1")
parl_search_hansard(query="housing affordability", politician="trudeau-j")
```

### Effective Search Tips

- Use specific phrases rather than single words (e.g., "pharmacare program" not "health")
- Filter by politician slug to find what a specific MP said
- Filter by date range (start_date, end_date) for time-limited searches
- Use French keywords when searching French-language statements

## Debate Structure

Each Hansard entry includes:
- `date` — sitting date
- `time` — approximate time in the sitting
- `politician` — who made the statement
- `content` — the actual text spoken
- `topic` — heading under which the statement appears (if any)

## Full Sitting Transcripts

Use `parl_get_debates` with a specific date to retrieve the complete
transcript of an entire sitting, organized by topic and MP.

## Tools Reference

- `parl_search_hansard` — Full-text search of debate transcripts
- `parl_get_debates` — Complete transcript for a specific sitting date
"""


@resource(
    "docs://parliament/api-quirks",
    mime_type="text/markdown",
    name="parl_api_quirks_guide",
    title="Open Parliament API Known Quirks and Limitations",
)
def parl_api_quirks_guide() -> str:
    """Guide to known Open Parliament API quirks, pagination, and limitations.

    Read this before querying to understand rate limits, pagination,
    and known API limitations like house-wide vote totals vs individual ballots.
    """
    return """# Open Parliament API: Known Quirks and Limitations

## Rate Limiting

The API guidelines recommend conservative usage: ≤5 req/s.
The mcp-canada module enforces 5 req/s automatically via TokenBucket.

## Pagination

Most list endpoints paginate at 20 results by default.
Use the `limit` and `offset` parameters to page through results.
Maximum `limit` is typically 500.

## Vote Totals vs Individual Ballots

**Important:** `parl_get_votes` returns **house-wide totals** (yea_total, nay_total),
NOT individual MP votes. To see how a specific MP voted, use:
- `parl_get_ballots` — all ballots for a specific division
- `parl_get_voting_record` — all votes for a specific MP

## Politician Slugs

Politicians are identified by URL slug (e.g., "trudeau-j", "singh-j", "poilievre-p"),
not by name. Use `parl_get_politicians` to search for the slug.

## Session Identifiers

Sessions use the "{parliament}-{session}" format (e.g., "44-1").
Omitting the session parameter searches all sessions.
See `data://parliament/session-format` for the current session.

## Bill Numbers

Bill numbers reset each Parliament. C-21 in the 44th Parliament is different
from C-21 in the 43rd Parliament. Always specify the session when referencing
a specific bill.

## Cache TTLs

Parliamentary data is cached for 6 hours (TTL 21600s).
`_meta.cached: true` in responses indicates data from cache.

## Common 404 Causes

1. Wrong politician slug (use parl_get_politicians to find correct slug)
2. Invalid session format (must be "{parliament}-{session}" e.g., "44-1")
3. Bill number from the wrong Parliament
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://parliament/mp-profile",
    mime_type="text/markdown",
    name="parl_mp_profile_template",
    title="Member of Parliament Profile Report Template",
)
def parl_mp_profile_template() -> str:
    """Template for formatting a Member of Parliament profile report.

    Replace {placeholder} values with actual data from parl_get_politicians
    and parl_get_voting_record before presenting to the user.
    """
    return """# MP Profile: {mp_name}

**Party:** {party_name}
**Riding:** {riding_name}, {province}
**Session:** {session}

## Contact and Basic Info

- **Slug:** {mp_slug}
- **Email:** {email}
- **Website:** {website}

## Parliamentary Activity

### Voting Record

- **Total votes:** {total_votes}
- **Yea:** {yea_count} ({yea_percent}%)
- **Nay:** {nay_count} ({nay_percent}%)
- **Absent/Paired:** {absent_count}

### Recent Votes

| Date | Bill/Motion | Vote |
|------|-------------|------|
{recent_vote_rows}

## Debate Contributions

Recent statements in Hansard:

{recent_statements}

## Notes

Data retrieved from the Open Parliament API (openparliament.ca).
"""
