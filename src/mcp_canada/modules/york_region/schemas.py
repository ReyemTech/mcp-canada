"""Flat Pydantic v2 models for york_region module — Hub datasets and Feature query results."""

from pydantic import BaseModel, ConfigDict


class HubDataset(BaseModel):
    """Flat representation of a single ArcGIS Hub dataset from the Search API."""

    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    title: str
    type: str | None = None
    description: str | None = None
    url: str | None = None
    owner: str | None = None
    tags: list[str] = []
    categories: list[str] = []
    created: str | None = None
    modified: str | None = None


class FeatureQueryResult(BaseModel):
    """Result of a FeatureServer query — list of feature property dicts plus pagination info."""

    model_config = ConfigDict(extra="ignore")

    features: list[dict]
    count: int
    truncated: bool
