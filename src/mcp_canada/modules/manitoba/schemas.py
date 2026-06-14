"""Manitoba module schemas — flat Pydantic v2 models.

All fields use snake_case. Optional fields use Field(default=None).
Aggressive flattening — no nested models mirroring API nesting.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Hub Discovery models (Plans 02)
# ---------------------------------------------------------------------------


class ManitobaDatasetSummary(BaseModel):
    """Summarized view of a Manitoba geoportal dataset item."""

    id: str
    title: str
    snippet: str | None = Field(default=None)
    type: str | None = Field(default=None)
    owner: str | None = Field(default=None)
    url: str | None = Field(default=None)
    num_views: int | None = Field(default=None)
    modified: int | None = Field(default=None)  # Unix ms timestamp
    source: str | None = Field(default=None)


class ManitobaDatasetDetails(ManitobaDatasetSummary):
    """Full details for a Manitoba geoportal dataset including resource links."""

    description: str | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    resources: list[dict] = Field(default_factory=list)
    feature_server_url: str | None = Field(default=None)
    download_urls: list[str] = Field(default_factory=list)
    licence_info: str | None = Field(default=None)
    access: str | None = Field(default=None)


class ManitobaOrganization(BaseModel):
    """A publishing organization on the Manitoba geoportal."""

    id: str
    name: str
    title: str | None = Field(default=None)
    item_count: int | None = Field(default=None)


class ManitobaCategory(BaseModel):
    """A content category/tag on the Manitoba geoportal."""

    name: str
    count: int | None = Field(default=None)


# ---------------------------------------------------------------------------
# Flood / Hydrology models (Plan 03)
# ---------------------------------------------------------------------------


class ManitobaFloodAlert(BaseModel):
    """An overland flood alert polygon from Overland_Flood_Alerts FeatureServer."""

    type_en: str | None = Field(default=None)   # "Watch" | "Warning"
    type_fr: str | None = Field(default=None)   # Bilingual
    start_date: int | None = Field(default=None)  # Unix ms timestamp
    end_date: int | None = Field(default=None)
    area_sqkm: float | None = Field(default=None)  # Shape__Area
    geometry: dict | None = Field(default=None)    # Polygon geometry if requested


class ManitobaRiverStation(BaseModel):
    """A hydrometric station from the Manitoba River Conditions CSV.

    Note: This is a CSV feed (not FeatureServer) at:
    www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv
    """

    station_id: str | None = Field(default=None)
    station_name: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    alert: str | None = Field(default=None)   # "No Flooding" | "High Water Advisory" | "Flood Watch" | "Flood Warning" | "No Current Data"
    measured_level: float | None = Field(default=None)
    measured_flow: float | None = Field(default=None)
    flood_stage: float | None = Field(default=None)
    warning_trigger_level: float | None = Field(default=None)
    province: str | None = Field(default=None)
    measurement_date: str | None = Field(default=None)
    water_level: float | None = Field(default=None)
    discharge: float | None = Field(default=None)
    wsc_real_time_url: str | None = Field(default=None)


class ManitobaWaterway(BaseModel):
    """A provincial waterway from Provincial_Waterways FeatureServer."""

    f_type: str | None = Field(default=None)  # "Dike" | "Floodway" | "Dam" | "Diversion" | "Reservoir" | "Waterway"
    name: str | None = Field(default=None)
    watershed: str | None = Field(default=None)
    wcw: str | None = Field(default=None)      # Water Control Works identifier
    length_km: float | None = Field(default=None)
    geometry: dict | None = Field(default=None)


# ---------------------------------------------------------------------------
# Agriculture / Drought models (Plan 04)
# ---------------------------------------------------------------------------


class ManitobaDroughtPolygon(BaseModel):
    """A drought intensity polygon from Canada_USA_Drought_Monitor FeatureServer."""

    dm: str | None = Field(default=None)        # "D0" | "D1" | "D2" | "D3" | "D4"
    obs_date: int | None = Field(default=None)  # Unix ms timestamp of observation
    source: str | None = Field(default=None)
    geometry: dict | None = Field(default=None)


class ManitobaAgWeatherStation(BaseModel):
    """An agricultural weather station from WeatherStations FeatureServer."""

    stn_name: str | None = Field(default=None)
    lat_dd: float | None = Field(default=None)
    long_dd: float | None = Field(default=None)
    elevation: float | None = Field(default=None)
    ag_region: str | None = Field(default=None)
    url: str | None = Field(default=None)  # Link to live hourly data page


class ManitobaLivestockPrice(BaseModel):
    """A weekly livestock price record from Manitoba Agriculture FeatureServer."""

    week: str | None = Field(default=None)
    auction: str | None = Field(default=None)
    parameter: str | None = Field(default=None)  # Description of livestock/price type
    measure: str | None = Field(default=None)    # Unit of measure
    value: float | None = Field(default=None)
    livestock: str = Field(default="cattle")     # "cattle" | "hog"


class ManitobaCropRegion(BaseModel):
    """A crop reporting region from MbAg_Crop_Reporting_Regions FeatureServer."""

    region_en: str | None = Field(default=None)  # REGION field
    region_fr: str | None = Field(default=None)  # RÉGION field
    geometry: dict | None = Field(default=None)


# ---------------------------------------------------------------------------
# Environment / Parks models (Plan 05)
# ---------------------------------------------------------------------------


class ManitobaPark(BaseModel):
    """A provincial park from Manitoba_Parks FeatureServer."""

    name_en: str | None = Field(default=None)    # NAME_E
    nom_fr: str | None = Field(default=None)     # NOM_F
    biome: str | None = Field(default=None)
    area_ha: float | None = Field(default=None)  # O_AREA
    type_en: str | None = Field(default=None)    # TYPE_E
    type_fr: str | None = Field(default=None)    # TYPE_F
    status_en: str | None = Field(default=None)  # STATUS_E
    prot_date: int | None = Field(default=None)  # PROTDATE (Unix ms)
    park_class: str | None = Field(default=None) # PRK_CLSS
    url: str | None = Field(default=None)


class ManitobaWaterbody(BaseModel):
    """A fisheries waterbody from Manitoba_Waterbody_Data FeatureServer."""

    id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    surface_area: float | None = Field(default=None)
    avg_depth: float | None = Field(default=None)
    secchi_depth: float | None = Field(default=None)
    fishing_division: str | None = Field(default=None)
    species: str | None = Field(default=None)
    regulations: str | None = Field(default=None)
    boat_launch: str | None = Field(default=None)


class ManitobaForest(BaseModel):
    """A provincial forest from Manitoba_Provincial_Forests___Version_6 FeatureServer."""

    name: str | None = Field(default=None)
    area_ha: float | None = Field(default=None)
    geometry: dict | None = Field(default=None)


# ---------------------------------------------------------------------------
# Health models (Plan 05)
# ---------------------------------------------------------------------------


class ManitobaWaitTime(BaseModel):
    """A diagnostic/surgical wait time record from Manitoba_Diagnostic_and_Surgical_Wait_Time_Averages."""

    year: int | None = Field(default=None)
    indicator_data_area: str | None = Field(default=None)  # IndicatorDataArea
    average_wait: float | None = Field(default=None)       # Average_Wait (days)


class ManitobaHealthFacility(BaseModel):
    """A rural health care facility from Rural_Health_Care_Facilities_in_Manitoba FeatureServer."""

    community: str | None = Field(default=None)   # Community_Name
    facility: str | None = Field(default=None)    # Facility_Name
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    emergency_dept: str | None = Field(default=None)      # Emergency_Department_Availabili
    time_open_pct: str | None = Field(default=None)       # Percentage_of_Time_Open__2015_
    nearest_alt_ed: str | None = Field(default=None)      # Nearest_Alternate_Emergency_Dep
    acute_care: str | None = Field(default=None)          # Acute_Care_Availability
    acute_care_beds: int | None = Field(default=None)     # Acute_Care_Number_of_Beds
    transitional_care: str | None = Field(default=None)
    diagnostic_services: str | None = Field(default=None)
    pch: str | None = Field(default=None)                 # Personal Care Home
    rha: str | None = Field(default=None)                 # Regional Health Authority (derived)


# ---------------------------------------------------------------------------
# Transport / 511 models (Plan 06)
# ---------------------------------------------------------------------------


class Manitoba511Event(BaseModel):
    """A road event from Manitoba 511 API v3 /events endpoint."""

    id: str | None = Field(default=None)
    roadway_name: str | None = Field(default=None)
    event_type: str | None = Field(default=None)
    is_full_closure: bool = Field(default=False)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    description: str | None = Field(default=None)
    last_updated: str | None = Field(default=None)


class Manitoba511WinterRoad(BaseModel):
    """A winter road condition from Manitoba 511 API v3 /winterroads endpoint."""

    id: str | None = Field(default=None)
    area_name: str | None = Field(default=None)
    roadway_name: str | None = Field(default=None)
    primary_condition: str | None = Field(default=None)
    secondary_conditions: str | None = Field(default=None)
    visibility: str | None = Field(default=None)
    encoded_polyline: str | None = Field(default=None)
    last_updated: str | None = Field(default=None)


class Manitoba511Camera(BaseModel):
    """A traffic camera from Manitoba 511 API v3 /cameras endpoint."""

    id: str | None = Field(default=None)
    location: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    views: list[dict] = Field(default_factory=list)  # Camera view URLs/names
