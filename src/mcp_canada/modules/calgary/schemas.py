"""Calgary module Pydantic v2 schemas.

All models are flat — no nested objects mirroring API nesting.
Snake_case field names throughout; Optional fields use Field(default=None).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CalgaryDatasetSummary(BaseModel):
    """Flat summary of a dataset from /api/catalog/v1 results."""

    id: str | None = None
    name: str = ""
    description: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    department: str | None = None
    permalink: str | None = None
    updated_at: str | None = None
    download_count: int | None = None
    type: str | None = None
    column_names: list[str] = Field(default_factory=list)


class CalgaryDatasetDetails(BaseModel):
    """Full metadata from /api/views/{id}.json."""

    id: str | None = None
    name: str = ""
    category: str | None = None
    description: str | None = None
    columns: list[dict] = Field(default_factory=list)
    attribution: str | None = None
    license_name: str | None = None
    publication_date: str | None = None
    tags: list[str] = Field(default_factory=list)


class CalgaryOrganization(BaseModel):
    """Organization (attribution) publishing on data.calgary.ca."""

    name: str
    dataset_count: int | None = None


class CalgaryCategory(BaseModel):
    """Domain category from the Calgary Socrata catalog."""

    name: str
    count: int | None = None
