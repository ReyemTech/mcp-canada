"""Pydantic v2 models for Open Parliament API responses.

All fields are Optional to ensure graceful degradation when the API
returns partial or inconsistent data (known schema drift in this API).
"""


from pydantic import BaseModel


class BillSummary(BaseModel):
    """Summary of a federal bill."""

    number: str | None = None
    name: str | None = None
    session: str | None = None
    introduced: str | None = None
    sponsor_url: str | None = None
    status: str | None = None
    law: bool | None = None


class BillDetail(BillSummary):
    """Detailed bill information including vote and text links."""

    vote_urls: list[str] | None = None
    text_url: str | None = None
    summary: str | None = None


class Politician(BaseModel):
    """Summary of a Member of Parliament."""

    name: str | None = None
    party: str | None = None
    riding: str | None = None
    province: str | None = None
    current: bool | None = None
    url: str | None = None


class VoteSummary(BaseModel):
    """Summary of a House of Commons vote."""

    number: int | None = None
    date: str | None = None
    result: str | None = None
    bill_url: str | None = None
    yea_total: int | None = None
    nay_total: int | None = None
    paired_total: int | None = None


class DebateEntry(BaseModel):
    """A single Hansard debate entry."""

    date: str | None = None
    politician_url: str | None = None
    content_en: str | None = None
    content_fr: str | None = None
    url: str | None = None


class SearchResult(BaseModel):
    """A Hansard full-text search result."""

    politician_url: str | None = None
    content: str | None = None
    date: str | None = None
    url: str | None = None
