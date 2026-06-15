"""Nova Scotia module tools — @tool functions for the MCP server.

All tools use standalone @tool from fastmcp.tools (NEVER @mcp.tool).
All tools include lang: Literal["en", "fr"] = "en" parameter.
All tools return make_response() on success, make_error() on failure.
All tools use the "ns_" prefix.

Discovery tools (Plan 02):
  ns_search_datasets, ns_get_dataset_details, ns_query_dataset,
  ns_list_organizations, ns_list_categories

Curated tools added by Plans 03-05.
"""

from __future__ import annotations

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared import socrata  # noqa: F401 — used by discovery tools

from . import client as _client
from .constants import (
    BASE_URL,
    CATALOG_URL,
    CHRONIC_DISEASE_DATASETS,
    DS_MARINE_AQUACULTURE_LEASES,
    DS_LANDBASED_AQUACULTURE_LICENSES,
    DS_FISH_HATCHERY_STOCKING,
    DS_AQUACULTURE_PRODUCTION,
    DS_SURFACE_WATER_QUALITY_CONTINUOUS,
    DS_BOIL_WATER_ADVISORIES,
    DS_PROTECTED_AREAS,
    DS_AIR_QUALITY_STATIONS,
    DS_HOSPITALS,
    DS_LTC_RCF_FACILITIES,
    DS_BIRTHS_DEATHS,
)


# ---------------------------------------------------------------------------
# Discovery tools (Plan 02)
# ---------------------------------------------------------------------------


@tool
async def ns_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search the Government of Nova Scotia open data catalogue on data.novascotia.ca (Socrata).

    Use for: searching Nova Scotia's open data portal; discovering datasets by keyword; browsing the NS Socrata catalogue; finding provincial government data; paginating through dataset results.
    Keywords: nova scotia open data catalogue search datasets socrata soda portal browse discover inventory find provincial government data novascotia
    """
    try:
        data, cached = await _client.fetch_search_datasets(query=query, limit=limit, offset=offset)
        return make_response(
            {
                "results": data.get("results", []),
                "total": data.get("total", 0),
                "offset": offset,
                "limit": limit,
            },
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_dataset_details(
    dataset_id: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get schema and metadata for a specific Nova Scotia dataset by its 4x4 dataset ID.

    Use for: inspecting a Nova Scotia dataset schema; finding column names and types; getting attribution, license, and publication date for a specific dataset.
    Keywords: nova scotia dataset details schema columns metadata views attribution license socrata dataset info fields inspect
    """
    try:
        data, cached = await _client.fetch_dataset_details(dataset_id=dataset_id)
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/api/views/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_query_dataset(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 1000,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    include_geometry: bool = False,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Run a SoQL query against any Nova Scotia Socrata dataset via /resource/{id}.json.

    Use for: querying any NS dataset with filters; running SoQL against Nova Scotia open data; getting specific rows from a provincial dataset; aggregating NS data by field.
    Keywords: nova scotia query dataset soql where select order limit offset filter socrata resource sql data rows fetch

    Note: geometry (the_geom) is returned in rows when include_geometry=True or when
    $select is not specified. Use $select to exclude the_geom when not needed.
    Example: dataset_id='h57h-p9mm', where="county='Halifax'", select="county,species,ownership", limit=100
    """
    try:
        data, cached = await _client.fetch_query_dataset(
            dataset_id=dataset_id,
            where=where,
            select=select,
            order=order,
            limit=limit,
            offset=offset,
            q=q,
            group=group,
            include_geometry=include_geometry,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_list_organizations(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Nova Scotia government organizations and publishers on data.novascotia.ca.

    Use for: discovering which NS departments publish open data; finding organization names for Nova Scotia's Socrata portal; browsing data publishers by dataset count.
    Keywords: nova scotia organizations publishers departments attributions government agencies data owners socrata portal list browse
    """
    try:
        data, cached = await _client.fetch_organizations()
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_list_categories(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List Nova Scotia data categories from the data.novascotia.ca Socrata catalogue.

    Use for: discovering all topic categories in Nova Scotia's open data portal; finding categories like Fishing and Aquaculture, Health and Wellness, Environment and Energy; browsing NS dataset subjects.
    Keywords: nova scotia categories topics domains classification fisheries health environment energy agriculture government socrata catalogue browse subjects

    Note: The catalog categories= API parameter is broken (returns 0 results always).
    This tool uses q= full-text search + client-side aggregation of
    classification.domain_category — never the broken categories= parameter.
    """
    try:
        data, cached = await _client.fetch_categories()
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=CATALOG_URL,
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Fishing / Aquaculture curated tools (Plan 03)
# ---------------------------------------------------------------------------


@tool
async def ns_get_marine_aquaculture_leases(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia marine aquaculture lease locations with species, owner, waterbody, county, status, and area.

    Use for: finding NS marine aquaculture leases by county or species type; discovering shellfish or finfish lease locations; marine aquaculture licensing queries in Nova Scotia.
    Keywords: nova scotia marine aquaculture lease shellfish finfish oyster salmon waterbody county status ownership hectares coordinates fishing aquaculture NS

    Note: geometry (the_geom MultiPolygon boundaries) is excluded from this tool's response.
    To retrieve polygon boundaries, use ns_query_dataset with dataset_id='h57h-p9mm' and
    include $select=...,the_geom explicitly. County names use title case (e.g., 'Inverness').
    Species type values: 'Shellfish', 'Finfish', 'Marine Plant'.
    """
    try:
        data, cached = await _client.fetch_marine_aquaculture_leases(
            county=county,
            species_type=species_type,
            limit=limit,
        )
        # Belt-and-suspenders: strip the_geom from any row that still has it
        leases = [{k: v for k, v in row.items() if k != "the_geom"} for row in data.get("leases", [])]
        return make_response(
            {**data, "leases": leases},
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_MARINE_AQUACULTURE_LEASES}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_landbased_aquaculture_licenses(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia landbased aquaculture licenses with species type, owner, county, and operational status.

    Use for: finding NS landbased aquaculture operations by county or species type; Atlantic Salmon or Rainbow Trout license queries; finfish farm locations; aquaculture licensing in Nova Scotia.
    Keywords: nova scotia landbased aquaculture license finfish salmon rainbow trout county ownership status lat long coordinates farm facility NS aquaculture

    Note: County names use title case (e.g., 'Hants', 'Colchester').
    Species type values: 'Finfish', 'Shellfish'. Finfish (Atlantic Salmon) dominates this dataset.
    """
    try:
        data, cached = await _client.fetch_landbased_aquaculture_licenses(
            county=county,
            species_type=species_type,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_LANDBASED_AQUACULTURE_LICENSES}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_fish_hatchery_stocking(
    stock: str | None = None,
    county: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia fish hatchery stocking records with species, hatchery, county, fish size, count released, and stocking date.

    Use for: querying NS hatchery stocking records by species or county; finding Brook Trout or Atlantic Salmon releases; hatchery production data; stocking history by waterbody in Nova Scotia.
    Keywords: nova scotia fish hatchery stocking brook trout atlantic salmon releases county hatchery fingerling smolt number released stocking date NS fisheries aquaculture

    Note: Records are ordered newest-first (stocking_date DESC). Data current to 2025-11.
    Brook Trout is the dominant stocked species. County names use title case (e.g., 'Antigonish').
    Common stock values: 'Brook Trout', 'Atlantic Salmon', 'Brown Trout', 'Rainbow Trout'.
    """
    try:
        data, cached = await _client.fetch_fish_hatchery_stocking(
            stock=stock,
            county=county,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_FISH_HATCHERY_STOCKING}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_aquaculture_production(
    year: str | None = None,
    county: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia aquaculture production, value, and employment data by county and year.

    Use for: querying NS aquaculture economic data by county and year; production volume (kg) and total value by region; employment statistics for NS aquaculture sector; annual industry analysis.
    Keywords: nova scotia aquaculture production value employment county year kg kgs full time jobs economic annual industry data NS fisheries shellfish finfish

    Note: year is stored as a text field — use the year as a string (e.g., year='2022').
    Annual data by county. Fields: year, county, kgs, total_value, full_time, pt_employ_6_mth,
    pt_employ_6_mth_1, total_employ. Results ordered most recent year first.
    """
    try:
        data, cached = await _client.fetch_aquaculture_production(
            year=year,
            county=county,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_AQUACULTURE_PRODUCTION}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Environment / Water / Air Quality curated tools (Plan 04)
# ---------------------------------------------------------------------------


@tool
async def ns_get_water_quality_monitoring(
    station_number: str | None = None,
    since: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia surface water quality continuous sensor readings (temperature, pH, conductance, dissolved oxygen).

    Use for: querying NS water quality sensor data by station or date range; temperature, pH, dissolved oxygen, specific conductance readings; continuous water quality monitoring in Nova Scotia.
    Keywords: nova scotia water quality monitoring sensor station temperature pH dissolved oxygen conductance readings continuous surface water NS environment

    Note: Data is from the continuous monitoring network (dataset bkfi-mjgw), current through 2024-12.
    Use since='YYYY-MM-DD' to filter by date (e.g., since='2024-01-01'). Results ordered newest-first.
    Station locations are in a separate catalog dataset (i9ee-9hct) — use ns_query_dataset if needed.
    """
    try:
        data, cached = await _client.fetch_water_quality_monitoring(
            station_number=station_number,
            since=since,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_SURFACE_WATER_QUALITY_CONTINUOUS}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_boil_water_advisories(
    county: str | None = None,
    active_only: bool = False,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia boil water advisories with site name, county, date issued, date removed, facility type, and duration.

    Use for: checking NS boil water advisories; finding active drinking water advisories in Nova Scotia; water safety notices by county; historical advisory records.
    Keywords: nova scotia boil water advisory drinking water safety county facility active removed issued duration community water supply municipal NS health

    Note: Use active_only=True to get only current advisories (date_advisory_removed IS NULL).
    An empty advisory list is a VALID success — no active advisories is the normal off-season state.
    County names are uppercase (e.g., 'ANNAPOLIS COUNTY', 'INVERNESS COUNTY').
    Data current to 2025.
    """
    try:
        data, cached = await _client.fetch_boil_water_advisories(
            county=county,
            active_only=active_only,
            limit=limit,
        )
        # Empty advisories list is a valid success — no active advisories is normal
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_BOIL_WATER_ADVISORIES}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_protected_areas(
    status: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia protected areas with name, protection type, owner, authority, designation status, and area.

    Use for: finding NS protected areas by designation status; national parks, wilderness areas, nature reserves in Nova Scotia; conservation lands by owner or authority; protected area inventory.
    Keywords: nova scotia protected areas national park wilderness reserve conservation land owner authority status designation area hectares NS environment lands forestry wildlife

    Note: Geometry (MultiPolygon boundaries) is excluded from this tool's response to reduce context size.
    To retrieve polygon boundaries, use ns_query_dataset with dataset_id='ticv-5du5' and include
    the_geom in $select explicitly. Status values: 'Designated', 'Candidate', 'Proposed'.
    """
    try:
        data, cached = await _client.fetch_protected_areas(
            status=status,
            limit=limit,
        )
        # Belt-and-suspenders: strip the_geom in case client data has it
        areas = [{k: v for k, v in row.items() if k != "the_geom"} for row in data.get("protected_areas", [])]
        return make_response(
            {**data, "protected_areas": areas},
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_PROTECTED_AREAS}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_air_quality_stations(
    city: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia ambient air quality monitoring station locations with measurements and monitoring period.

    Use for: finding NS air quality monitoring stations by city; locating PM2.5, O3, NO2, SO2 monitoring sites; ambient air quality station inventory in Nova Scotia.
    Keywords: nova scotia air quality stations monitoring PM2.5 O3 NO2 SO2 pollutant city latitude longitude ambient environment NS NAPS network

    Note: This tool returns the STATION CATALOG only (locations, measurement types, monitoring period).
    Individual pollutant time series (O3, PM2.5, SO2, CO by station and year) are in 20+ separate
    per-station datasets. Use ns_query_dataset with the specific dataset ID from the station record
    to read individual pollutant readings. See docs://ns/air-quality-guide for the full pattern.
    """
    try:
        data, cached = await _client.fetch_air_quality_stations(
            city=city,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_AIR_QUALITY_STATIONS}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


# ---------------------------------------------------------------------------
# Health + Demographics curated tools (Plan 05)
# ---------------------------------------------------------------------------


@tool
async def ns_get_health_facilities(
    facility_type: str,
    county: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia hospital or long-term care facility locations by type, county, health zone, and beds.

    Use for: finding NS hospitals by county; locating long-term care or residential care facilities in Nova Scotia; health facility inventory by zone; beds count at LTC facilities.
    Keywords: nova scotia hospital long-term care LTC residential care facility county health zone beds location address coordinates type regional community NS health

    Dispatches by facility_type:
      - "hospital"       → Hospitals dataset (tmfr-3h8a): facility_name, address, town, county, type
                           (Regional/District/Community), x_coordinate, y_coordinate
      - "long_term_care" → LTC/RCF Facilities dataset (x76a-axw2): facility_name, address, town,
                           county, zone (Central/Eastern/Northern/Western), beds, x_coordinate, y_coordinate

    Both types return a common facility shape with facility_category set to the requested type.
    Invalid facility_type returns INVALID_INPUT with the valid options list.
    """
    _VALID = sorted(["hospital", "long_term_care"])
    if facility_type not in _VALID:
        msg = (
            f"Type d'établissement invalide '{facility_type}'"
            if lang == "fr"
            else f"Invalid facility_type '{facility_type}'"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=_VALID)
    # Dispatch dataset URL based on facility type
    dataset_id = DS_HOSPITALS if facility_type == "hospital" else DS_LTC_RCF_FACILITIES
    try:
        data, cached = await _client.fetch_health_facilities(
            facility_type=facility_type,
            county=county,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except ValueError as exc:
        # Secondary guard: client also raises ValueError on invalid facility_type
        return make_error("INVALID_INPUT", str(exc), lang=lang, valid=_VALID)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_vital_statistics(
    county: str | None = None,
    year: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia vital statistics (births, deaths, rates, natural increase) by county and year.

    Use for: analyzing NS birth and death rates by county; population growth and natural increase in Nova Scotia; demographic trends; vital statistics comparison across counties and years.
    Keywords: nova scotia vital statistics births deaths birth rate death rate population natural increase county year demographics NS census demography

    IMPORTANT: county names are UPPERCASE in this dataset (e.g., 'ANNAPOLIS', 'HALIFAX', 'LUNENBURG').
    IMPORTANT: year is a TEXT column — use string year values (e.g., year='2020'), not integers.
    Returns fields: counties, year, population, live_births, birth_rate, deaths, death_rate,
    excess_of_births_over_deaths, natural_increase_rate.
    """
    try:
        data, cached = await _client.fetch_vital_statistics(
            county=county,
            year=year,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{DS_BIRTHS_DEATHS}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)


@tool
async def ns_get_chronic_disease_prevalence(
    disease: str,
    health_zone: str | None = None,
    sex: str | None = None,
    year: str | None = None,
    limit: int = 5000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia chronic disease crude prevalence by health zone, sex, age group, and year.

    Use for: querying NS chronic disease rates by health zone; comparing disease burden across zones; diabetes prevalence in Nova Scotia; AMI heart disease statistics; COPD asthma hypertension trends by age sex zone year.
    Keywords: nova scotia chronic disease prevalence diabetes heart disease AMI COPD hypertension asthma health zone sex age year crude prevalence rate NS Health statistics

    Dispatches by disease:
      - "ami"          → Acute Myocardial Infarction (24qf-ntke) — no sex field in this dataset
      - "diabetes"     → Diabetes (cumi-sw99)
      - "copd"         → Chronic Obstructive Pulmonary Disease (ua9e-4pss)
      - "hypertension" → Hypertension (sztc-sewr) — fields: hypertension_count, prevalence_rate
      - "asthma"       → Asthma (2bih-5dgk)

    Zone is normalized: AMI uses 'health_zone' in the source dataset, renamed to 'zone' in output.
    All 5 disease datasets surface a consistent 'zone' key in returned rows.
    Invalid disease returns INVALID_INPUT with the valid disease list.
    """
    _VALID = sorted(CHRONIC_DISEASE_DATASETS.keys())
    if disease not in CHRONIC_DISEASE_DATASETS:
        msg = (
            f"Maladie inconnue '{disease}'"
            if lang == "fr"
            else f"Unknown disease '{disease}'"
        )
        return make_error("INVALID_INPUT", msg, lang=lang, valid=_VALID)
    dataset_id = CHRONIC_DISEASE_DATASETS[disease]
    try:
        data, cached = await _client.fetch_chronic_disease(
            disease=disease,
            health_zone=health_zone,
            sex=sex,
            year=year,
            limit=limit,
        )
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/resource/{dataset_id}.json",
            cached=cached,
            lang=lang,
        )
    except ValueError as exc:
        # Secondary guard: client also validates disease
        return make_error("INVALID_INPUT", str(exc), lang=lang, valid=_VALID)
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
