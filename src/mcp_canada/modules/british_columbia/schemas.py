"""Flat Pydantic v2 models for british_columbia module — CKAN dataset metadata and WFS feature records."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class BcResource(BaseModel):
    """A single resource (download/WFS link) within a BC Data Catalogue dataset."""

    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    name: str | None = None
    format: str | None = None
    url: str | None = None
    bcdc_type: str | None = None
    object_name: str | None = None
    resource_storage_location: str | None = None
    resource_type: str | None = None


class BcDatasetSummary(BaseModel):
    """Flat summary of a BC Data Catalogue dataset from package_search results."""

    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    name: str | None = None
    title: str | None = None
    notes: str | None = None
    organization: str | None = None
    bcdc_type: str | None = None
    metadata_modified: str | None = None
    tags: list[str] = []


class BcDatasetDetails(BcDatasetSummary):
    """Full BC Data Catalogue dataset record from package_show, including resource metadata."""

    model_config = ConfigDict(extra="ignore")

    resources: list[BcResource] = []
    object_name: str | None = None
    queryable_via_wfs: bool = False
    projection: str | None = None


class BcFeature(BaseModel):
    """A single WFS feature record — properties dict plus optional geometry."""

    model_config = ConfigDict(extra="ignore")

    properties: dict[str, Any] = {}
    geometry: dict[str, Any] | None = None
