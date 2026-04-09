"""Pydantic v2 models for Ontario Open Data API responses."""

from typing import Any
from pydantic import BaseModel


class Resource(BaseModel):
    """A single dataset resource (file/link)."""

    id: str | None = None
    name: str | None = None
    format: str | None = None
    size: int | None = None
    url: str | None = None
    description: str | None = None


class DatasetSummary(BaseModel):
    """Summary view of an Ontario CKAN dataset (search result)."""

    id: str | None = None
    name: str | None = None
    title: str | None = None
    description: str | None = None
    organization: dict[str, Any] | None = None
    num_resources: int | None = None
    tags: list[dict[str, Any]] | None = None


class DatasetDetail(DatasetSummary):
    """Full dataset view with resources and timestamps."""

    resources: list[dict[str, Any]] | None = None
    metadata_created: str | None = None
    metadata_modified: str | None = None


class Organization(BaseModel):
    """An Ontario CKAN organization (government ministry or agency)."""

    id: str | None = None
    name: str | None = None
    title: str | None = None
    description: str | None = None
    package_count: int | None = None
