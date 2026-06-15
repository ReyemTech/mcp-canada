"""Saskatchewan module schemas — flat Pydantic v2 models for all response types.

All models are flat (no nested objects). Optional fields use Field(default=None).
Snake_case field names throughout. Aggressive flattening — API nesting is unwrapped here.

Plans 02-05 use these models to validate and document response shapes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SaskatchewanDatasetSummary(BaseModel):
    """Flat summary of a Saskatchewan GeoHub dataset from Hub Search API."""

    id: str = Field(default="")
    title: str = Field(default="")
    snippet: str | None = Field(default=None)
    type: str | None = Field(default=None)
    owner: str | None = Field(default=None)
    url: str | None = Field(default=None)
    modified: Any = Field(default=None)
    source: str | None = Field(default=None)


class SaskatchewanDatasetDetails(BaseModel):
    """Full metadata for a Saskatchewan GeoHub dataset item."""

    id: str = Field(default="")
    title: str = Field(default="")
    snippet: str | None = Field(default=None)
    description: str | None = Field(default=None)
    type: str | None = Field(default=None)
    owner: str | None = Field(default=None)
    url: str | None = Field(default=None)
    feature_server_url: str | None = Field(default=None)
    download_urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    modified: Any = Field(default=None)
    num_views: int | None = Field(default=None)
    access: str | None = Field(default=None)
    licence_info: str | None = Field(default=None)


class SaskatchewanOrganization(BaseModel):
    """A publishing organization on the Saskatchewan GeoHub."""

    id: str | None = Field(default=None)
    name: str = Field(default="")
    item_count: int | None = Field(default=None)


class SaskatchewanCategory(BaseModel):
    """A dataset category/theme on the Saskatchewan GeoHub."""

    name: str = Field(default="")
    count: int | None = Field(default=None)


class SaskatchewanCropYield(BaseModel):
    """Estimated crop yield record by region (bu/acre).

    16 crop types from Provincial_Estimated_Crop_Yields FeatureServers.
    All crop fields are float|None (yields in bu/acre).
    """

    region: str = Field(default="")
    hrsw: float | None = Field(default=None, description="Hard Red Spring Wheat (bu/acre)")
    durum: float | None = Field(default=None, description="Durum wheat (bu/acre)")
    oat: float | None = Field(default=None, description="Oat (bu/acre)")
    barley: float | None = Field(default=None, description="Barley (bu/acre)")
    canola: float | None = Field(default=None, description="Canola (bu/acre)")
    mustard: float | None = Field(default=None, description="Mustard (bu/acre)")
    soybean: float | None = Field(default=None, description="Soybean (bu/acre)")
    pea: float | None = Field(default=None, description="Pea (bu/acre)")
    lentil: float | None = Field(default=None, description="Lentil (bu/acre)")
    chickpea: float | None = Field(default=None, description="Chickpea (bu/acre)")
    canary_seed: float | None = Field(default=None, description="Canary seed (bu/acre)")
    flax: float | None = Field(default=None, description="Flax (bu/acre)")
    winter_wheat: float | None = Field(default=None, description="Winter wheat (bu/acre)")
    fall_rye: float | None = Field(default=None, description="Fall rye (bu/acre)")
    other_wheat: float | None = Field(default=None, description="Other wheat (bu/acre)")


class SaskatchewanGrainElevator(BaseModel):
    """A grain elevator location from Western Canada Grain Elevator 2024 dataset."""

    station: str | None = Field(default=None)
    pr: str | None = Field(default=None, description="Province code (SK for Saskatchewan)")
    railway: str | None = Field(default=None, description="Railway line (CN, CP, SHORTLINE)")
    licensee: str | None = Field(default=None)
    elevator_type: str | None = Field(default=None, description="Primary or process elevator")
    capacity_tonne: float | None = Field(default=None, description="Capacity in tonnes")


class SaskatchewanMineralMine(BaseModel):
    """A mineral mine record from Saskatchewan's mineral deposit index."""

    commodity: str | None = Field(default=None, description="Mineral commodity (Potash, Uranium, etc.)")
    name: str | None = Field(default=None, description="Mine name")
    status: str | None = Field(default=None, description="Operating, Care & Maintenance, Closed, etc.")
    mine_type: str | None = Field(default=None, description="Solution, Underground, Open Pit, etc.")
    company: str | None = Field(default=None)
    mine_site: str | None = Field(default=None)
    regulation: str | None = Field(default=None)
    date_opened: str | None = Field(default=None)
    website: str | None = Field(default=None)


class SaskatchewanAirQuality(BaseModel):
    """Hourly ambient air quality reading for a Saskatchewan monitoring station.

    Fields follow the Hourly_Ambient_Air_Quality FeatureServer schema.
    All pollutant readings are float|None (units vary by pollutant).
    aqhi: str|None because AQHI field contains a URL (link to weather.gc.ca AQHI page).
    """

    community: str | None = Field(default=None)
    station_id: str | None = Field(default=None)
    pm2_5: float | None = Field(default=None, description="PM2.5 (µg/m³)")
    no2: float | None = Field(default=None, description="NO2 (ppb)")
    o3: float | None = Field(default=None, description="Ozone (ppb)")
    pm10: float | None = Field(default=None, description="PM10 (µg/m³)")
    so2: float | None = Field(default=None, description="SO2 (ppb)")
    co: float | None = Field(default=None, description="CO (ppm)")
    h2s: float | None = Field(default=None, description="H2S (ppb)")
    aqhi: str | None = Field(default=None, description="AQHI link to weather.gc.ca")
    datetime: str | None = Field(default=None, description="Reading datetime (ISO8601)")


class SaskatchewanFireBan(BaseModel):
    """A current fire ban record from SPSA Public_Fire_Ban FeatureServer.

    scope field indicates which ban layer was queried (urban/rural/provincial/parks).
    CRITICAL: empty list of fire bans is CORRECT when no bans are active (off-season).
    """

    um_type: str | None = Field(default=None, description="UMTYPE field from FeatureServer")
    municipality: str | None = Field(default=None, description="Municipali field (truncated name)")
    fire_department: str | None = Field(default=None, description="Fire_Depar field")
    start_date: str | None = Field(default=None, description="Start_Date field")
    contact: str | None = Field(default=None, description="Contact_Nu field")
    type: str | None = Field(default=None, description="Type field (Ban/Restriction/etc.)")
    comment: str | None = Field(default=None)
    scope: str = Field(default="", description="Ban scope: urban/rural/provincial/parks")


class SaskatchewanWildfire(BaseModel):
    """A historic wildfire record from SPSA Historic_Wildfire_Boundaries or Origins FeatureServer."""

    year: int | None = Field(default=None)
    fire_name: str | None = Field(default=None)
    cause1: str | None = Field(default=None, description="Primary cause (Lightning/Human/Unknown)")
    hectares: float | None = Field(default=None, description="Area burned in hectares")
    status: str | None = Field(default=None, description="Out/Under Control/Being Held/etc.")
    start_date: str | None = Field(default=None)
    out_date: str | None = Field(default=None)
    type: str | None = Field(default=None)


class SaskatchewanWSAStation(BaseModel):
    """A WSA hydrometric gauging station from Hydrometric_Gauging_Stations_V2 FeatureServer."""

    station_number: str | None = Field(default=None, description="WSC station number (e.g. 05MB006)")
    station_name: str | None = Field(default=None)
    province: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    major_basin: str | None = Field(default=None, description="Major river basin name")
    station_type: str | None = Field(default=None)
    station_class: str | None = Field(default=None)
    operated_by: str | None = Field(default=None)
    hyperlink_graph: str | None = Field(
        default=None,
        description="URL to live hourly hydrograph at wsask.ca",
    )


class SaskatchewanWSAReservoir(BaseModel):
    """A WSA reservoir from WSA_Reservoirs FeatureServer layer 26 (NOT layer 0)."""

    reservoir_name: str | None = Field(default=None)
    dam_name: str | None = Field(default=None)
    imagery_date: str | None = Field(default=None)
    water_level_masl: float | None = Field(
        default=None, description="Water level in metres above sea level"
    )
