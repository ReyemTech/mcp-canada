"""Nova Scotia module Pydantic v2 schemas.

All models are flat — no nested objects mirroring API nesting.
Snake_case field names throughout; Optional fields use Field(default=None).

Spike note (20-SPIKE.md): Chronic disease datasets have schema variations across
the 5 disease datasets. NovaScotiaChronicDiseaseRow uses nullable fields to handle:
  - AMI: no sex field; plain string year; uses "health_zone" → normalized to zone
  - Hypertension: different field names (hypertension_count, prevalence_rate)
  - Diabetes/COPD: "agegroup" (no underscore) → normalized to age_group
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Discovery / catalog schemas
# ---------------------------------------------------------------------------


class NovaScotiaDatasetSummary(BaseModel):
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


class NovaScotiaDatasetDetails(BaseModel):
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


class NovaScotiaOrganization(BaseModel):
    """Organization (attribution) publishing on data.novascotia.ca."""

    name: str
    dataset_count: int | None = None


class NovaScotiaCategory(BaseModel):
    """Domain category from the NS Socrata catalog."""

    name: str
    count: int | None = None


# ---------------------------------------------------------------------------
# Fishing / Aquaculture schemas
# ---------------------------------------------------------------------------


class NovaScotiaMarineLease(BaseModel):
    """Marine aquaculture lease (h57h-p9mm). Geometry excluded via $select."""

    license_le: str | None = None
    ownership: str | None = None
    species: str | None = None
    waterbody: str | None = None
    county: str | None = None
    sitestatus: str | None = None
    speciestyp: str | None = None
    hectares: float | None = None
    lat_dms: str | None = None
    long_dms: str | None = None


class NovaScotiaLandbasedLicense(BaseModel):
    """Landbased aquaculture license (yqwg-f62a)."""

    license_le: str | None = None
    species: str | None = None
    speciestyp: str | None = None
    county: str | None = None
    ownership: str | None = None
    sitestatus: str | None = None
    lat_dms: str | None = None
    long_dms: str | None = None


class NovaScotiaHatcheryRecord(BaseModel):
    """Fish hatchery stocking record (8e4a-m6fw)."""

    county: str | None = None
    name: str | None = None
    type: str | None = None
    stock: str | None = None
    stock_strain: str | None = None
    hatchery: str | None = None
    fish_length_cm: float | None = None
    fish_weight_g: float | None = None
    number_released: int | None = None
    stocking_date: str | None = None
    mark: str | None = None
    growth_stage: str | None = None


class NovaScotiaAquacultureProduction(BaseModel):
    """Aquaculture production, value, and employment by county and year (v2ex-ev63)."""

    year: str | None = None
    county: str | None = None
    kgs: float | None = None
    total_value: float | None = None
    full_time: float | None = None
    total_employ: float | None = None


# ---------------------------------------------------------------------------
# Environment / Water schemas
# ---------------------------------------------------------------------------


class NovaScotiaWaterQualityReading(BaseModel):
    """Surface water quality continuous reading (bkfi-mjgw)."""

    station_number: str | None = None
    date: str | None = None
    time: str | None = None
    temperature_c: float | None = None
    ph: float | None = None
    specific_conductance_s_cm: float | None = None
    dissolved_oxygen_mg_l: float | None = None


class NovaScotiaBoilWaterAdvisory(BaseModel):
    """Boil water advisory (7t68-9xmm). date_advisory_removed=None → active advisory."""

    site_name: str | None = None
    county: str | None = None
    date_advisory_issued: str | None = None
    date_advisory_removed: str | None = None
    facility_type: str | None = None
    length_of_advisory: str | None = None


class NovaScotiaProtectedArea(BaseModel):
    """Protected area (ticv-5du5). Geometry excluded via $select."""

    objectid: int | None = None
    pro_name: str | None = None
    protect1: str | None = None
    symbol: str | None = None
    owner: str | None = None
    authority: str | None = None
    status: str | None = None
    web_url: str | None = None
    ha_gis: float | None = None


class NovaScotiaAirQualityStation(BaseModel):
    """Air quality monitoring station (3bbm-drnh)."""

    national_air_pollution_surveillance_network_id: str | None = None
    station_name: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    measurements: str | None = None
    monitoring_period: str | None = None


# ---------------------------------------------------------------------------
# Health + Demographics schemas
# ---------------------------------------------------------------------------


class NovaScotiaHealthFacility(BaseModel):
    """Hospital or LTC facility (tmfr-3h8a / x76a-axw2)."""

    facility_name: str | None = None
    address: str | None = None
    town: str | None = None
    county: str | None = None
    type: str | None = None
    zone: str | None = None
    beds: int | None = None
    x_coordinate: float | None = None
    y_coordinate: float | None = None
    facility_category: str | None = None


class NovaScotiaVitalStatistic(BaseModel):
    """Annual vital statistic by county (r794-fttm)."""

    counties: str | None = None
    year: str | None = None
    population: float | None = None
    live_births: float | None = None
    birth_rate: float | None = None
    deaths: float | None = None
    death_rate: float | None = None
    natural_increase_rate: float | None = None


class NovaScotiaChronicDiseaseRow(BaseModel):
    """Chronic disease prevalence row — normalized across 5 datasets.

    Spike findings (20-SPIKE.md):
      - zone: normalized from "health_zone" (AMI) or "zone" (others) → always "zone" in output
      - sex: None for AMI (no sex field in that dataset)
      - age_group: normalized from "age_group" or "agegroup" → always "age_group" in output
      - prevalence: None for hypertension (uses hypertension_count instead)
      - crude_prevalence_rate: None for hypertension (uses prevalence_rate instead)
      - hypertension_count / prevalence_rate: set only for hypertension disease
    """

    disease: str
    year: str | None = None
    zone: str | None = None            # normalized from health_zone (AMI) or zone (others)
    sex: str | None = None             # None for AMI (no sex field)
    age_group: str | None = None       # normalized from agegroup (diabetes/COPD) or age_group
    population: float | None = None
    prevalence: float | None = None    # None for hypertension (uses hypertension_count)
    crude_prevalence_rate: float | None = None  # None for hypertension (uses prevalence_rate)
    hypertension_count: float | None = None     # Hypertension only
    prevalence_rate: float | None = None        # Hypertension only
