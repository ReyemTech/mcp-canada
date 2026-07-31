"""New Brunswick module Pydantic v2 schemas.

All models are flat — no nested objects mirroring API nesting. Snake_case
field names throughout; optional fields use `Field(default=None)`.

Geospatial models use the exact truncated GeoNB field names captured live in
21-SPIKE.md §4 (shapefile-derived, non-self-describing — RESEARCH Pitfall 2),
not the ArcGIS layer display name.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Federal CKAN discovery / catalog schemas
# ---------------------------------------------------------------------------


class NBDatasetSummary(BaseModel):
    """Flat summary of a federal CKAN package_search result, organization:nb."""

    id: str | None = None
    name: str = ""
    title: str | None = None
    description: str | None = None
    organization: str | None = None
    subject: list[str] = Field(default_factory=list)
    topic_category: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    num_resources: int | None = None
    formats: list[str] = Field(default_factory=list)
    metadata_modified: str | None = None
    url: str | None = None


class NBDatasetDetails(NBDatasetSummary):
    """Full metadata for a single federal CKAN dataset (package_show)."""

    resources: list[dict] = Field(default_factory=list)
    license_title: str | None = None
    license_url: str | None = None
    date_published: str | None = None
    maintainer: str | None = None
    frequency: str | None = None
    spatial: str | None = None


class NBOrganization(BaseModel):
    """A federal CKAN organization (used to identify the nb org)."""

    name: str
    name_fr: str | None = None
    dataset_count: int | None = None


class NBCategory(BaseModel):
    """A federal CKAN group/category among NB datasets."""

    name: str
    name_fr: str | None = None
    count: int | None = None


# ---------------------------------------------------------------------------
# gnb.socrata.com discovery schemas (checkpoint option-a)
# ---------------------------------------------------------------------------


class NBSocrataDatasetSummary(BaseModel):
    """Flat summary of a gnb.socrata.com /api/catalog/v1 result."""

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


# ---------------------------------------------------------------------------
# GeoNB discovery schemas
# ---------------------------------------------------------------------------


class NBGeoNBService(BaseModel):
    """A single entry from the live GeoNB service directory."""

    name: str
    type: str = "MapServer"
    department: str | None = None
    curated_tool: str | None = None
    excluded_reason: str | None = None


class NBGeoNBLayer(BaseModel):
    """A single layer/table resolved from a GeoNB MapServer's ?f=json."""

    id: int
    name: str
    geometry_type: str | None = None
    record_count: int | None = None
    fields: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Curated GeoNB geospatial schemas — field names from 21-SPIKE.md §4
# ---------------------------------------------------------------------------


class NBFloodHazardArea(BaseModel):
    """Flood Hazard polygon (GeoNB_ENV_FloodHazardIndex layer 0)."""

    OBJECTID: int | None = None
    Sheet_Numb: str | None = None
    Technical_: str | None = None
    Flood_Haza: str | None = None
    Shape_Area: float | None = None


class NBHistoricalFlood(BaseModel):
    """Historical flood limit/extent (GeoNB_ENV_Historical_Floods, layers 0-8)."""

    OBJECTID: int | None = None
    ID: str | None = None
    KEY: str | None = None
    FEATURE: str | None = None
    SOURCE: str | None = None
    LIMIT: str | None = None
    Shape_Length: float | None = None


class NBWetland(BaseModel):
    """Wetland polygon (GeoNB_ENV_Wetlands layer 2)."""

    OBJECTID: int | None = None
    ID: str | None = None
    Hectares: float | None = None
    WC: str | None = None
    WETLAND_CLASS: str | None = None
    STATUS: str | None = None
    Shape_Area: float | None = None


class NBContaminatedSite(BaseModel):
    """Contaminated site point (GeoNB_ELG_Contaminated_Sites layer 0)."""

    OBJECTID: int | None = None
    Status_E: str | None = None
    Status_F: str | None = None
    PidType_E: str | None = None
    PidType_F: str | None = None
    FileOpenDate: str | None = None
    FileNumber: str | None = None
    Latitude: float | None = None
    Longitude: float | None = None


class NBCrownLandParcel(BaseModel):
    """Crown Land parcel polygon (GeoNB_DNR_Crown_Land layer 3)."""

    OBJECTID: int | None = None
    HOLDER: int | None = None  # raw integer code, no server-exposed domain (Pitfall 4)
    Shape_Length: float | None = None
    Shape_Area: float | None = None


class NBMineralOccurrence(BaseModel):
    """Mineral occurrence point (GeoNB_DNR_MineralOccurrences layer 0).

    Long-tail model — no curated tool ships this in Phase 21 (checkpoint
    option-a); reachable via nb_query_geonb_layer. Kept for a future plan.
    """

    OBJECTID: int | None = None
    NAME: str | None = None
    COMMODITIE: str | None = None
    LAT: float | None = None
    LON: float | None = None


class NBProvincialPark(BaseModel):
    """Provincial park polygon (GeoNB_DNR_ProvincialParks layer 0).

    Long-tail model — no curated tool ships this in Phase 21 (checkpoint
    option-a); reachable via nb_query_geonb_layer. Kept for a future plan.
    """

    OBJECTID: int | None = None
    NAME: str | None = None
    Nom: str | None = None
    AREA: float | None = None
    Hectares: float | None = None


class NBParcel(BaseModel):
    """Land parcel polygon (GeoNB_SNB_Parcels layer 0). FILTER_REQUIRED."""

    OBJECTID: int | None = None
    PID: str | None = None
    COUNTY: str | None = None
    Titles_Status: str | None = None
    Gazette_Status: str | None = None


class NBCivicAddress(BaseModel):
    """Civic address point (GeoNB_DPS_Civic_Address layer 0). FILTER_REQUIRED.

    LATITUDE/LONGITUDE/PID added alongside the pre-existing COUNTY (F5) so the
    documented address -> point / address -> parcel geocoding workflow is
    actually completable from a single result.
    """

    OBJECTID: int | None = None
    CIVIC_NUM: str | None = None
    STREET: str | None = None
    ST_TYPE_E: str | None = None
    ST_TYPE_F: str | None = None
    COMMUNITY: str | None = None
    COUNTY: str | None = None
    PID: str | None = None
    LATITUDE: float | None = None
    LONGITUDE: float | None = None


class NBHealthFacility(BaseModel):
    """Health facility point — normalized across the 6 GeoNB_Health_Facilities
    layers (0-5), which publish two distinct raw schemas (21-SPIKE.md §4)."""

    facility_type: str | None = None
    OBJECTID: int | None = None
    Hospital_N: str | None = None
    Name_E: str | None = None
    Name_F: str | None = None
    Telephone_: str | None = None


class NBPublicSchool(BaseModel):
    """Public school point (GeoNB_EECD_PublicSchools layers 0-1)."""

    strID: str | None = None
    strNM: str | None = None
    strAD1: str | None = None
    strGR: str | None = None
    strURL: str | None = None
    sector: str | None = None


# ---------------------------------------------------------------------------
# NB 511 schemas (key-gated stubs)
# ---------------------------------------------------------------------------


class NB511Event(BaseModel):
    """A road event from 511.gnb.ca (key-gated)."""

    id: str | None = None
    event_type: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class NB511WinterRoad(BaseModel):
    """A winter road condition segment from 511.gnb.ca (key-gated)."""

    area_name: str | None = None
    condition: str | None = None
    updated: str | None = None


class NB511Camera(BaseModel):
    """A traffic camera from 511.gnb.ca (key-gated)."""

    id: str | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    url: str | None = None
