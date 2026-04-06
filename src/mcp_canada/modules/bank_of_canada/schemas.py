"""Pydantic v2 schemas for flattened Bank of Canada Valet API responses.

All models use flat structures — no nested Valet JSON shapes.
Sort order convention: newest first (index 0 = most recent) — enforced in client.
"""

from pydantic import BaseModel


class ObservationRow(BaseModel):
    """A single flattened observation data point from the Valet API."""

    date: str
    series_name: str
    value: float | None
    label: str
    description: str


class SeriesInfo(BaseModel):
    """Metadata for a single Valet API series."""

    name: str
    label: str
    description: str
    link: str | None = None


class GroupInfo(BaseModel):
    """Metadata for a Valet API series group."""

    name: str
    label: str
    description: str
    link: str | None = None
