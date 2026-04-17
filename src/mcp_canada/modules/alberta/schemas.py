"""Flat Pydantic v2 models for the alberta module.

All models are flat — no nested dicts mirroring the raw API shape.
Aggressive flattening preserves agent context tokens by shedding API scaffolding
(Alberta CKAN's 50+ publication-repository `extras` — identifier-AGDEX-number,
identifier-ISBN-pdf, audience, creator, etc. — are hidden in AlbertaDatasetDetails;
see Pitfall 11 in 17-RESEARCH.md).

Domain coverage:
  - Discovery (Plan 02): AlbertaDatasetSummary/Details, AlbertaResource,
    AlbertaOrganization, AlbertaCategory
  - AER / energy (Plan 03): AlbertaWellLicence, AlbertaProductionRow,
    AlbertaPipelineRow
  - Wildfire (Plan 04): AlbertaActiveFire, AlbertaFirePerimeter,
    AlbertaFireBan, AlbertaFireControlOrder, AlbertaForestArea
  - Health (Plan 05): AlbertaHospital, AlbertaEmsStation, AlbertaPcnClinic,
    AlbertaAhsZone
  - Transport (Plan 06): Alberta511Event, Alberta511WinterRoad,
    Alberta511Camera
  - Environment / agriculture / demographics / parks (Plan 07):
    AlbertaAqhiStation, AlbertaWaterAdvisory, AlbertaCropProductionRow,
    AlbertaPopulationEstimate, AlbertaProvincialPark
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Discovery (Plan 02)
# ---------------------------------------------------------------------------


class AlbertaResource(BaseModel):
    """A single downloadable / queryable resource within an Alberta dataset."""

    id: str
    name: str | None = None
    format: str | None = None  # "PDF", "CSV", "XLSX", "ESRI REST", "JSON", etc.
    url: str
    datastore_active: bool = False
    size: int | None = None


class AlbertaDatasetSummary(BaseModel):
    """Summary row returned by alberta_search_datasets.

    Alberta CKAN is publication-heavy: 86% of 33,269 datasets are PDF reports.
    `formats` is a deduped list of resource formats on the dataset — use it to
    filter out pure-PDF publications before fetching full details.
    """

    id: str
    name: str  # slug
    title: str
    notes: str | None = None
    organization_slug: str | None = None
    license_id: str | None = None
    num_resources: int = 0
    metadata_modified: str | None = None
    formats: list[str] = Field(default_factory=list)


class AlbertaDatasetDetails(BaseModel):
    """Full dataset record returned by alberta_get_dataset_details.

    Deliberately hides the 50+ Alberta-specific `extras` (identifier-AGDEX-number,
    identifier-ISBN-pdf, audience, etc.) — only the agent-useful subset is surfaced.
    Re-raw access is available via CKAN package_show directly.
    """

    id: str
    name: str
    title: str
    notes: str | None = None
    organization_slug: str | None = None
    license_id: str | None = None
    isopen: bool | None = None
    language: str | None = None
    frequencyofupdate: str | None = None
    creator: str | None = None
    metadata_modified: str | None = None
    resources: list[AlbertaResource] = Field(default_factory=list)


class AlbertaOrganization(BaseModel):
    """Organization returned by alberta_list_organizations.

    Alberta's CKAN is federated across 370 orgs — current ministries, historical
    predecessor ministries, Crown corps, and advisory committees.
    """

    id: str
    name: str  # slug
    title: str
    package_count: int = 0


class AlbertaCategory(BaseModel):
    """Format / category entry returned by alberta_list_categories.

    Alberta CKAN does NOT use groups (group_list returns empty); we surface the
    res_format facet from package_search instead (PDF / CSV / XLSX / ESRI REST / etc.).
    """

    format: str
    count: int = 0


# ---------------------------------------------------------------------------
# AER / energy (Plan 03)
# ---------------------------------------------------------------------------


class AlbertaWellLicence(BaseModel):
    """Single well licence row from AER ST1 (daily TXT or archive XLSX)."""

    licence_number: str
    well_name: str | None = None
    operator: str | None = None
    location: str | None = None
    spud_date: str | None = None
    status: str | None = None
    surface_uwi: str | None = None


class AlbertaProductionRow(BaseModel):
    """Monthly production row flattened from AER ST3 per-product XLSX.

    ST3 XLSX files are multi-sheet by region; flattening emits one row per
    (product, period, region).
    """

    product: str
    period: str  # YYYY-MM
    volume: float | None = None
    units: str | None = None
    region: str | None = None


class AlbertaPipelineRow(BaseModel):
    """Single pipeline statistics row from AER ST39 annual XLSX."""

    substance: str | None = None
    length_km: float | None = None
    operator: str | None = None
    year: int | None = None


# ---------------------------------------------------------------------------
# Wildfire (Plan 04)
# ---------------------------------------------------------------------------


class AlbertaActiveFire(BaseModel):
    """Active wildfire from WMBappServices Active_Wildfires_Dashboard_view."""

    fire_number: str
    fire_year: int | None = None
    fire_type: str | None = None
    fire_status: str | None = None
    area_estimate: float | None = None
    general_cause: str | None = None
    incident_type: str | None = None
    resp_area: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    label: str | None = None
    assessment_date: str | None = None


class AlbertaFirePerimeter(BaseModel):
    """Fire perimeter row from WMB Active_/Extinguished_Wildfire_Perimeters_Simplified_view."""

    fire_number: str
    fire_status: str | None = None
    fire_year: int | None = None
    area_hectares: float | None = None
    geometry: dict | None = None  # GeoJSON geometry; opt-in via include_geometry=True


class AlbertaFireBan(BaseModel):
    """Fire ban / advisory from WMB alberta_fire_ban_system FeatureServer."""

    fire_centre: str | None = None
    ban_type: str | None = None
    area_name: str | None = None
    restriction_level: str | None = None
    effective_date: str | None = None
    link: str | None = None


class AlbertaFireControlOrder(BaseModel):
    """Fire Control Order row from WMB Fire_Control_Orders_Prod_View2."""

    order_id: str | None = None
    order_type: str | None = None
    area_name: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    status: str | None = None


class AlbertaForestArea(BaseModel):
    """Forest Area boundary row from WMB Forest_Area_Prod_View2 (10 forest areas)."""

    fa_name: str
    area_hectares: float | None = None


# ---------------------------------------------------------------------------
# Health (Plan 05)
# ---------------------------------------------------------------------------


class AlbertaHospital(BaseModel):
    """Hospital from AHSGIS AHS_Hospitals FeatureServer (101 hospitals).

    `ip` = inpatient beds, `ed` = emergency department.
    """

    location: str | None = None
    hospital_name: str
    st_address: str | None = None
    postal_code: str | None = None
    phone: str | None = None
    h_code: str | None = None
    ip: bool = False
    ed: bool = False
    label: str | None = None
    zone: str | None = None


class AlbertaEmsStation(BaseModel):
    """EMS station from AHSGIS EMS_Stations FeatureServer."""

    name: str
    address: str | None = None
    zone: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class AlbertaPcnClinic(BaseModel):
    """PCN (Primary Care Network) or walk-in clinic from AHSGIS PCN_Clinics FeatureServer."""

    name: str
    address: str | None = None
    zone: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class AlbertaAhsZone(BaseModel):
    """AHS zone from AHSGIS AHS_Zone FeatureServer (5 zones — South, Calgary,
    Central, Edmonton, North). Population stats come from 2006/2011/2016 census."""

    zone_name: str
    zone_id: str | None = None
    pop_2006: int | None = None
    pop_2011: int | None = None
    pop_2016: int | None = None


# ---------------------------------------------------------------------------
# Transport / 511 Alberta (Plan 06)
# ---------------------------------------------------------------------------


class Alberta511Event(BaseModel):
    """Road event from 511 Alberta v2 API event endpoint.

    Covers closures, construction, incidents, and accidents.
    """

    id: str
    source_id: str | None = None
    roadway_name: str | None = None
    event_type: str | None = None
    event_subtype: str | None = None
    is_full_closure: bool = False
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    reported: str | None = None
    last_updated: str | None = None


class Alberta511WinterRoad(BaseModel):
    """Winter road condition from 511 Alberta v2 API winterroads endpoint."""

    id: str
    area_name: str | None = None
    roadway_name: str | None = None
    primary_condition: str | None = None
    secondary_conditions: str | None = None
    visibility: str | None = None
    encoded_polyline: str | None = None
    last_updated: str | None = None


class Alberta511Camera(BaseModel):
    """Traffic camera location + snapshot URLs from 511 Alberta v2 API cameras endpoint."""

    id: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    views: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Environment / demographics / agriculture / parks (Plan 07)
# ---------------------------------------------------------------------------


class AlbertaAqhiStation(BaseModel):
    """AQHI air quality monitoring station from GeoDiscover aqhi/air_layers MapServer/1.

    Pollutant readings are all `float | None` — any subset may be null depending on
    station instrumentation (75 stations, not all measure every pollutant).
    """

    station_id: str
    station_name: str
    latitude: float | None = None
    longitude: float | None = None
    # Pollutants (μg/m³ or ppb per station)
    so2: float | None = None
    h2s: float | None = None
    trs: float | None = None  # total reduced sulphur
    o3: float | None = None
    nox: float | None = None
    no: float | None = None
    no2: float | None = None
    nh3: float | None = None
    co: float | None = None
    pm2_5: float | None = None
    thc: float | None = None  # total hydrocarbons
    nmhc: float | None = None  # non-methane hydrocarbons
    ch4: float | None = None
    pah: float | None = None
    c2h4: float | None = None  # ethylene
    btex: float | None = None  # benzene/toluene/ethylbenzene/xylenes
    calib: float | None = None
    last_updated: str | None = None


class AlbertaWaterAdvisory(BaseModel):
    """Water management advisory from GeoDiscover environment/river_forecast_centre."""

    advisory_id: str | None = None
    advisory_type: str | None = None
    sub_basin: str | None = None
    status: str | None = None
    effective_date: str | None = None
    area_name: str | None = None
    geometry: dict | None = None  # opt-in


class AlbertaCropProductionRow(BaseModel):
    """Single row from major-crop-production-alberta CKAN CSV."""

    year: int
    crop: str
    area_seeded: float | None = None
    area_harvested: float | None = None
    production_tonnes: float | None = None
    yield_per_acre: float | None = None


class AlbertaPopulationEstimate(BaseModel):
    """Population estimate row from alberta-population-estimates-data-tables CKAN XLSX."""

    geo_code: str
    geo_name: str
    year: int
    population: int | None = None
    breakdown: str  # "csd" / "cma" / "quarterly" / "age_sex" / "sub_provincial" / "components_of_growth"


class AlbertaProvincialPark(BaseModel):
    """Provincial park / protected area from GeoDiscover boundary/parks_protected_areas_alberta."""

    park_id: str | None = None
    park_name: str
    designation: str | None = None  # e.g. "Provincial Park", "Wildland Park"
    area_hectares: float | None = None
    latitude: float | None = None
    longitude: float | None = None
