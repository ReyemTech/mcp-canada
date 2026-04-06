"""Pydantic v2 schemas for Health Canada Recalls API responses."""

from typing import Any
from pydantic import BaseModel


class RecallSummary(BaseModel):
    """Summary of a recall item (returned in list endpoints)."""

    recall_id: str | None = None
    title: str | None = None
    date_published: str | None = None
    category: str | None = None
    url: str | None = None


class RecallDetail(RecallSummary):
    """Full detail for a single recall, extending RecallSummary with detail fields."""

    affected_products: list[dict[str, Any]] | None = None
    corrective_actions: str | None = None
    audience: str | None = None
    description: str | None = None
    images: list[dict[str, Any]] | None = None
