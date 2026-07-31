"""New Brunswick module constants.

GeoNB is ArcGIS **Server** (62 MapServer services, zero FeatureServer) — the Hub
at geonb-snb.opendata.arcgis.com returns HTTP 401. Layer ids on GeoNB services
are non-guessable and were resolved LIVE in 21-SPIKE.md: all 11 curated layer
ids in this file are CONFIRMED against 21-RESEARCH.md's Code Examples table
(Plan 01 Task 3, 2026-07-30) — Crown Land is the worked case: layer 3, NOT
layer 0 (layer 0 does not exist on that service).

Discovery is a THREE-surface architecture:
  1. Federal CKAN filtered to `organization:nb` (open.canada.ca) — 221 first-
     party NB datasets, the only NB tabular catalogue. NB has no provincial
     CKAN: `data.gnb.ca`, `opendata.gnb.ca` and `nbopendata.ca` do not resolve
     (verified dead ends, do not re-investigate). D-01.
  2. `gnb.socrata.com` — NB's real provincial Socrata portal (312 datasets,
     keyless). **CHECKPOINT DECISION (Plan 01 Task 2, resolved 2026-07-30):
     option-a.** A live plan-time probe found this portal exists, contradicting
     21-CONTEXT.md's "NB has no provincial catalogue" framing. The user chose
     to add two `nb_` discovery tools against it (reusing `shared/socrata.py`
     verbatim — zero new client technology) alongside the locked federal CKAN
     discovery; D-01 stays intact, the federal CKAN 5 are untouched. To hold
     the tool budget at 22 (D-08's 18-22 band), `nb_get_provincial_parks` and
     `nb_get_mineral_occurrences` were dropped from the curated manifest to
     the long tail — both remain reachable through `nb_query_geonb_layer`.
     GeoNB_DNR_ProvincialParks (layer 0) and GeoNB_DNR_MineralOccurrences
     (layer 0) are documented in 21-SPIKE.md only; no dedicated *_SERVICE /
     *_LAYER constant or `fetch_*`/`nb_get_*` symbol exists for either.
  3. GeoNB (this file's `*_SERVICE` / `*_LAYER` constants) — curated
     geospatial tools via `shared/arcgis_hub.py:query_feature_service`,
     unchanged (D-05).
"""

from typing import Final

# ---------------------------------------------------------------------------
# Federal CKAN (open.canada.ca) — organization:nb filter, D-01
# ---------------------------------------------------------------------------

CKAN_BASE_URL: Final[str] = "https://open.canada.ca/data/api/3"
# Non-overridable — never expose an `organization` parameter to callers (T-21-04).
# The single source of truth for "nb" — `_build_fq` composes NB_ORG_FQ from it,
# and `fetch_dataset_details` compares a package_show result's own
# `organization.name` against it directly (G1) rather than hardcoding a
# second "nb" literal.
NB_ORG_NAME: Final[str] = "nb"
NB_ORG_FQ: Final[str] = f"organization:{NB_ORG_NAME}"

RATE_GROUP_CKAN: Final[str] = "new_brunswick_ckan"
RATE_LIMIT_CKAN: Final[float] = 5.0

# ---------------------------------------------------------------------------
# gnb.socrata.com — NB provincial Socrata portal (checkpoint option-a)
# ---------------------------------------------------------------------------

GNB_SOCRATA_DOMAIN: Final[str] = "gnb.socrata.com"

RATE_GROUP_SOCRATA: Final[str] = "new_brunswick_socrata"
RATE_LIMIT_SOCRATA: Final[float] = 5.0

# ---------------------------------------------------------------------------
# GeoNB — ArcGIS Server (bare MapServer REST, no Hub in front)
# ---------------------------------------------------------------------------

GEONB_BASE_URL: Final[str] = "https://geonb.snb.ca/arcgis/rest/services"

CROWN_LAND_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_DNR_Crown_Land/MapServer"
CROWN_LAND_LAYER: Final[int] = 3
CROWN_LAND_FIELDS: Final[str] = "OBJECTID,HOLDER,Shape_Length,Shape_Area"

FLOOD_HAZARD_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_ENV_FloodHazardIndex/MapServer"
FLOOD_HAZARD_LAYER: Final[int] = 0

HISTORICAL_FLOODS_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_ENV_Historical_Floods/MapServer"
HISTORICAL_FLOODS_LAYER: Final[int] = 0            # 2008 and 2018 Flood Limits
HISTORICAL_FLOODS_1973_LAYER: Final[int] = 8        # 1973 Flood Limits event

WETLANDS_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_ENV_Wetlands/MapServer"
WETLANDS_LAYER: Final[int] = 2                       # "Wetland" (1=PSW, 0=30m buffer)

CONTAMINATED_SITES_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_ELG_Contaminated_Sites/MapServer"
CONTAMINATED_SITES_LAYER: Final[int] = 0

PARCELS_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_SNB_Parcels/MapServer"
PARCELS_LAYER: Final[int] = 0                        # 604,520 rows — FILTER_REQUIRED

CIVIC_ADDRESS_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_DPS_Civic_Address/MapServer"
CIVIC_ADDRESS_LAYER: Final[int] = 0                  # 373,172 rows — FILTER_REQUIRED

HEALTH_FACILITIES_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_Health_Facilities/MapServer"
HEALTH_FACILITY_LAYERS: Final[dict[str, int]] = {
    "hospital_horizon": 0,
    "hospital_vitalite": 1,
    "after_hours_clinic": 2,
    "adult_residential_centre": 3,
    "nursing_home": 4,
    "pharmacy": 5,
}

PUBLIC_SCHOOLS_SERVICE: Final[str] = f"{GEONB_BASE_URL}/GeoNB_EECD_PublicSchools/MapServer"
SCHOOL_SECTOR_LAYERS: Final[dict[str, int]] = {
    "anglophone": 0,
    "francophone": 1,
}

# 5 basemaps (tiles, not data) plus the retired placeholder (21-SPIKE.md §3:
# layer 0 = "Retired Map Service", 1 record).
GEONB_EXCLUDED_SERVICES: Final[tuple[str, ...]] = (
    "GeoNB_Basemap_Grey",
    "GeoNB_Basemap_Imagery",
    "GeoNB_Basemap_NBRN",
    "GeoNB_Basemap_Provinces_bare",
    "GeoNB_Basemap_Topo",
    "GeoNB_DNR_WildlifeRefuges",
)

# The three large-layer tools that must reject an unfiltered call before any
# network call — T-21-03 (Parcels 604,520 / Civic_Address 373,172 / Wetlands
# 163,206 rows).
FILTER_REQUIRED_TOOLS: Final[tuple[str, ...]] = (
    "nb_get_parcels",
    "nb_get_civic_addresses",
    "nb_get_wetlands",
)

RATE_GROUP_GEONB: Final[str] = "new_brunswick_geonb"
RATE_LIMIT_GEONB: Final[float] = 5.0

# ---------------------------------------------------------------------------
# NB 511 (511.gnb.ca) — key-gated, D-09/D-10
# ---------------------------------------------------------------------------

FIVE11_BASE_URL: Final[str] = "https://511.gnb.ca/api/v2/get"
FIVE11_KEY_ENV: Final[str] = "NEW_BRUNSWICK_511_KEY"

RATE_GROUP_511: Final[str] = "new_brunswick_511"
RATE_LIMIT_511: Final[float] = 2.0

USER_AGENT: Final[str] = "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------

CACHE_KEY_PREFIX: Final[str] = "new_brunswick:"
CACHE_TTL_LIVE: Final[int] = 300         # 511 events/cameras/winter roads
CACHE_TTL_SEARCH: Final[int] = 3600      # federal CKAN + gnb.socrata.com search
CACHE_TTL_META: Final[int] = 86400       # curated GeoNB layers, service directory
CACHE_TTL_ANNUAL: Final[int] = 604800    # 7d — annually-updated reference data

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

MAX_RECORDS: Final[int] = 5000
DEFAULT_PAGE_SIZE: Final[int] = 1000

# ---------------------------------------------------------------------------
# Locked tool manifest (22 tools) — checkpoint option-a applied
# ---------------------------------------------------------------------------

ALL_NB_TOOL_NAMES: Final[tuple[str, ...]] = (
    # Federal CKAN discovery (organization:nb) — D-01, untouched by the checkpoint
    "nb_search_datasets",
    "nb_get_dataset_details",
    "nb_query_dataset",
    "nb_list_organizations",
    "nb_list_categories",
    # gnb.socrata.com discovery — checkpoint option-a
    "nb_search_gnb_socrata_datasets",
    "nb_query_gnb_socrata_dataset",
    # GeoNB discovery (service-directory enumeration, D-06)
    "nb_list_geonb_services",
    "nb_get_geonb_service_layers",
    "nb_query_geonb_layer",
    # Curated flood / water
    "nb_get_flood_hazard_areas",
    "nb_get_historical_floods",
    "nb_get_wetlands",
    "nb_get_contaminated_sites",
    # Curated Crown land / forestry
    "nb_get_crown_land",
    # Curated parcels / civic address
    "nb_get_parcels",
    "nb_get_civic_addresses",
    # Curated health / education
    "nb_get_health_facilities",
    "nb_get_public_schools",
    # Transport (511, NOT_CONFIGURED stubs)
    "nb_get_road_events",
    "nb_get_winter_road_conditions",
    "nb_get_traffic_cameras",
)
