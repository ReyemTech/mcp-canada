"""Pydantic v2 schemas for Statistics Canada WDS API responses.

All models are intentionally flat — no mirroring of WDS nesting.
"""

from pydantic import BaseModel


class CubeLite(BaseModel):
    """Lightweight cube descriptor from getAllCubesListLite."""

    product_id: int
    cansim_id: str | None = None
    title_en: str = ""
    title_fr: str = ""
    start_date: str = ""
    end_date: str = ""
    release_time: str = ""
    archived: bool = False
    frequency_code: int = 0
    frequency: str = "Unknown"
    subject_codes: list[str] = []
    survey_codes: list[str] = []


class DimensionMember(BaseModel):
    """A single member within a cube dimension."""

    member_id: int
    parent_member_id: int | None = None
    name_en: str
    name_fr: str
    classification_code: str | None = None
    geo_flag: bool


class Dimension(BaseModel):
    """A dimension within a cube (e.g. Geography, Industry)."""

    name_en: str
    name_fr: str
    has_uom: bool
    members: list[DimensionMember]


class CubeMetadata(BaseModel):
    """Full metadata for a single cube (table) from getCubeMetadata."""

    product_id: int
    cansim_id: str
    title_en: str
    title_fr: str
    start_date: str
    end_date: str
    frequency_code: int
    frequency: str
    nb_series: int
    nb_datapoints: int
    dimensions: list[Dimension]
    footnotes: list[dict]


class SeriesInfo(BaseModel):
    """Metadata for a single time series vector."""

    product_id: int
    coordinate: str
    vector_id: int
    frequency_code: int
    frequency: str
    scalar_factor_code: int
    scalar_factor: str
    decimals: int
    terminated: bool
    title_en: str
    title_fr: str
    uom_code: int
    # Decoded from the live getCodeSets uom set (464 entries, hand-maintenance
    # is not viable — see 08-UAT.md Gap 2). None when the code set is
    # unavailable or the code carries a null label upstream.
    uom: str | None = None


class ObservationRow(BaseModel):
    """A single observation data point."""

    ref_per: str
    ref_per_raw: str
    value: float | None
    decimals: int
    scalar_factor_code: int
    scalar_factor: str
    frequency_code: int
    frequency: str
    status_code: int
    symbol_code: int
    release_time: str


class CodeSetEntry(BaseModel):
    """A single entry in a WDS code set."""

    code: int
    desc_en: str | None = None
    desc_fr: str | None = None


class CodeSets(BaseModel):
    """All WDS code sets returned by getCodeSets."""

    frequency: list[CodeSetEntry]
    scalar: list[CodeSetEntry]
    status: list[CodeSetEntry]
    symbol: list[CodeSetEntry]
    security_level: list[CodeSetEntry]
    uom: list[CodeSetEntry]


# ---------------------------------------------------------------------------
# SDMX schemas (Phase 9)
# ---------------------------------------------------------------------------


class SDMXCodeValue(BaseModel):
    """A single code within an SDMX codelist (e.g. a geography value)."""

    id: str
    name_en: str
    name_fr: str


class SDMXDimension(BaseModel):
    """An SDMX dimension with its associated codelist."""

    position: int
    id: str
    codelist_id: str
    codes: list[SDMXCodeValue]


class SDMXStructure(BaseModel):
    """Parsed SDMX structure for a StatCan table (productId)."""

    product_id: int
    dimensions: list[SDMXDimension]
    suggested_key: str = ""


class SDMXObservationRow(BaseModel):
    """A single flattened observation row from SDMX-JSON data response."""

    period: str
    value: float | None
    dimensions: dict[str, str]
