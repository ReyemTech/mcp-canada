"""New Brunswick module resources — 7 zero-parameter @resource functions for the MCP server.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same JSON or markdown body).

URI scheme conventions:
  data:// — JSON catalogs: return json.dumps(...). Bilingual content inline.
  docs:// — Markdown guides: return raw markdown string. Both languages in same document.
  template:// — Markdown templates: return markdown with {placeholder} syntax.

Catalog resources (data://):
  data://nb/geonb-services    — all 62 GeoNB services: department, curated tool/layer id, reason
  data://nb/counties          — New Brunswick's 15 counties, English + French names
  data://nb/health-regions    — Horizon/Vitalité RHAs + HEALTH_FACILITY_LAYERS dispatch
  data://nb/school-districts  — Anglophone/Francophone sectors + SCHOOL_SECTOR_LAYERS dispatch

Documentation guides (docs://):
  docs://nb/portal-guide       — canonical NB portal-architecture document: every verified
                                 dead end (data.gnb.ca/opendata.gnb.ca/nbopendata.ca, GeoNB
                                 Hub 401) and every live surface (federal CKAN, GeoNB
                                 ArcGIS Server, gnb.socrata.com, key-gated 511)
  docs://nb/geonb-query-guide  — the three-step GeoNB discovery path + WHERE syntax + traps

Templates (template://):
  template://nb/flood-risk-report — {placeholder} fields for a flood risk assessment report
"""

from __future__ import annotations

import json

from fastmcp.resources import resource


__all__ = [
    "nb_geonb_services",
    "nb_counties",
    "nb_health_regions",
    "nb_school_districts",
    "nb_portal_guide",
    "nb_geonb_query_guide",
    "nb_flood_risk_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://) — JSON via json.dumps, bilingual inline
# ---------------------------------------------------------------------------


def _svc(
    name: str,
    department: str,
    department_name: str,
    status: str,
    curated_tool: str | None = None,
    curated_layer_id: object = None,
    reason: str | None = None,
) -> dict[str, object]:
    """Build one data://nb/geonb-services entry. Internal helper, not exported."""
    return {
        "name": name,
        "type": "MapServer",
        "department": department,
        "department_name": department_name,
        "status": status,  # "curated" | "excluded" | "long_tail"
        "curated_tool": curated_tool,
        "curated_layer_id": curated_layer_id,
        "reason": reason,
    }


@resource(
    "data://nb/geonb-services",
    mime_type="application/json",
    name="nb_geonb_services",
    title="GeoNB 62-Service Catalogue — Departments, Curated Tools, Layer Ids, Exclusion Reasons",
)
async def nb_geonb_services() -> str:
    """JSON catalogue of all 62 live-enumerated GeoNB (geonb.snb.ca) MapServer services.

    Use to discover which of GeoNB's 62 services has a curated nb_ tool, which layer
    id that tool uses, and why the other 53 are either excluded (tile basemaps,
    retired services, telemetry) or reachable only through the long-tail path
    (nb_list_geonb_services -> nb_get_geonb_service_layers -> nb_query_geonb_layer).
    Layer ids were resolved LIVE in 21-SPIKE.md (2026-07-30) — GeoNB layer 0 is
    frequently NOT the primary layer (Crown Land's only layer is 3, not 0).
    """
    services = [
        _svc("GeoNB_Basemap_Grey", "Basemap", "GeoNB Basemap (cartographic tiles)", "excluded",
             reason="tile basemap, not attribute data — no agent value"),
        _svc("GeoNB_Basemap_Imagery", "Basemap", "GeoNB Basemap (cartographic tiles)", "excluded",
             reason="tile basemap, not attribute data — no agent value"),
        _svc("GeoNB_Basemap_NBRN", "Basemap", "GeoNB Basemap (cartographic tiles)", "excluded",
             reason="tile basemap, not attribute data — no agent value"),
        _svc("GeoNB_Basemap_Provinces_bare", "Basemap", "GeoNB Basemap (cartographic tiles)", "excluded",
             reason="tile basemap, not attribute data — no agent value"),
        _svc("GeoNB_Basemap_Topo", "Basemap", "GeoNB Basemap (cartographic tiles)", "excluded",
             reason="tile basemap, not attribute data — no agent value"),
        _svc("GeoNB_DEM_Coastal_Erosion", "DEM", "GeoNB internal (elevation data)", "long_tail",
             reason="reachable via nb_query_geonb_layer; coastal erosion is covered thematically by GeoNB_ELG_CoastalZones, also un-curated"),
        _svc("GeoNB_DNR_Crown_Land", "DNR", "Natural Resources and Energy Development", "curated",
             curated_tool="nb_get_crown_land", curated_layer_id=3),
        _svc("GeoNB_DNR_Forest", "DNR", "Natural Resources and Energy Development", "long_tail",
             reason="reachable via nb_query_geonb_layer; 6 treatment/location tier layers need per-tier curation beyond the budget"),
        _svc("GeoNB_DNR_ForestSoils", "DNR", "Natural Resources and Energy Development", "long_tail",
             reason="reachable via nb_query_geonb_layer; soils are a specialist sub-domain below the D-07 bar"),
        _svc("GeoNB_DNR_MineralOccurrences", "DNR", "Natural Resources and Energy Development", "long_tail",
             curated_layer_id=0,
             reason="reachable via nb_query_geonb_layer (layer 0); dropped from the curated manifest under the 21-01 Task 2 checkpoint (option-a) to hold the 22-tool budget"),
        _svc("GeoNB_DNR_NBHN", "DNR", "Natural Resources and Energy Development", "long_tail",
             reason="reachable via nb_query_geonb_layer; hydrographic network is a basemap-grade reference layer"),
        _svc("GeoNB_DNR_NonForest", "DNR", "Natural Resources and Energy Development", "long_tail",
             reason="reachable via nb_query_geonb_layer; 7 category tier layers need per-tier curation beyond the budget"),
        _svc("GeoNB_DNR_ProvincialParks", "DNR", "Natural Resources and Energy Development", "long_tail",
             curated_layer_id=0,
             reason="reachable via nb_query_geonb_layer (layer 0); dropped from the curated manifest under the 21-01 Task 2 checkpoint (option-a) to hold the 22-tool budget"),
        _svc("GeoNB_DNR_WildlifeRefuges", "DNR", "Natural Resources and Energy Development", "excluded",
             reason="retired: layer 0 is named 'Retired Map Service' and holds 1 placeholder polygon (live-verified 2026-07-30)"),
        _svc("GeoNB_DPS_Civic_Address", "DPS", "Public Safety", "curated",
             curated_tool="nb_get_civic_addresses", curated_layer_id=0),
        _svc("GeoNB_DPS_NB911_Communities", "DPS", "Public Safety", "long_tail",
             reason="reachable via nb_query_geonb_layer; nb_get_civic_addresses is the higher-value SNB/DPS pick per D-07"),
        _svc("GeoNB_EECD_PublicSchools", "EECD", "Education and Early Childhood Development", "curated",
             curated_tool="nb_get_public_schools", curated_layer_id={"anglophone": 0, "francophone": 1}),
        _svc("GeoNB_ELG_Climate_Change_Adaptation_Plans", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; plan-document pointers rather than measurements"),
        _svc("GeoNB_ELG_CoastalZones", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; flood hazard + historical floods are the higher-value flood picks"),
        _svc("GeoNB_ELG_Contaminated_Sites", "ELG", "Environment and Local Government", "curated",
             curated_tool="nb_get_contaminated_sites", curated_layer_id=0),
        _svc("GeoNB_ELG_Local_Governance", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; administrative boundary layer below the D-07 bar"),
        _svc("GeoNB_ELG_LocalServiceDistricts", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; superseded by NB's 2023 local governance reform, historical value only"),
        _svc("GeoNB_ELG_WaterQuality_Lakes_Rivers", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; station catalogue only, no readings; contaminated sites is the higher-value ELG pick"),
        _svc("GeoNB_ELG_WAWA", "ELG", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; Watercourse and Wetland Alteration Act permit areas overlap nb_get_wetlands"),
        _svc("GeoNB_ENB_Local_Government_Elections", "ENB", "Elections New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; electoral boundaries below the D-07 bar for this budget"),
        _svc("GeoNB_ENB_Provincial_Elections", "ENB", "Elections New Brunswick", "long_tail",
             curated_layer_id=2,
             reason="reachable via nb_query_geonb_layer (layer 2 = 2024 districts); electoral boundaries below the D-07 bar"),
        _svc("GeoNB_ENB_RegionalHealthAuthorities", "ENB", "Elections New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; RHA names are shipped statically in data://nb/health-regions"),
        _svc("GeoNB_ENB_SchoolDistricts", "ENB", "Elections New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; district names are shipped statically in data://nb/school-districts"),
        _svc("GeoNB_ENV_Flood_Link", "ENV", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; link-out layer to external PDF flood maps, no queryable attributes of value"),
        _svc("GeoNB_ENV_FloodHazardIndex", "ENV", "Environment and Local Government", "curated",
             curated_tool="nb_get_flood_hazard_areas", curated_layer_id=0),
        _svc("GeoNB_ENV_Flood", "ENV", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; overlaps GeoNB_ENV_FloodHazardIndex, the curated pick"),
        _svc("GeoNB_ENV_Historical_Floods", "ENV", "Environment and Local Government", "curated",
             curated_tool="nb_get_historical_floods", curated_layer_id={"2008_2018": 0, "1973": 8}),
        _svc("GeoNB_ENV_ProtectedWatersheds", "ENV", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; zone-tiered across layers 0-4, needs per-tier curation"),
        _svc("GeoNB_ENV_ProtectedWellfields", "ENV", "Environment and Local Government", "long_tail",
             reason="reachable via nb_query_geonb_layer; narrow regulatory layer below the D-07 bar"),
        _svc("GeoNB_ENV_Wetlands", "ENV", "Environment and Local Government", "curated",
             curated_tool="nb_get_wetlands", curated_layer_id=2),
        _svc("GeoNB_Health_Boundaries", "Health", "Health", "long_tail",
             reason="reachable via nb_query_geonb_layer; nb_get_health_facilities is the higher-value Health pick"),
        _svc("GeoNB_Health_Facilities", "Health", "Health", "curated",
             curated_tool="nb_get_health_facilities",
             curated_layer_id={"hospital_horizon": 0, "hospital_vitalite": 1, "after_hours_clinic": 2,
                                "adult_residential_centre": 3, "nursing_home": 4, "pharmacy": 5}),
        _svc("GeoNB_NRCan_FirstNations", "NRCan", "Natural Resources Canada (federal, republished)", "long_tail",
             reason="reachable via nb_query_geonb_layer; federal NRCan layer republished, not first-party NB data"),
        _svc("GeoNB_NRCan_PlaceNames", "NRCan", "Natural Resources Canada (federal, republished)", "long_tail",
             reason="reachable via nb_query_geonb_layer; federal NRCan gazetteer republished, not first-party NB data"),
        _svc("GeoNB_PETL_WorkingNB_Boundaries", "PETL", "Post-Secondary Education, Training and Labour", "long_tail",
             reason="reachable via nb_query_geonb_layer; single administrative boundary layer below the D-07 bar"),
        _svc("GeoNB_ScriptedUpdateTrackingData", "internal", "GeoNB internal (ETL tracking)", "excluded",
             reason="GeoNB internal ETL update tracking — operator diagnostics, not open data"),
        _svc("GeoNB_SNB_atlas_index", "SNB", "Service New Brunswick", "excluded",
             reason="atlas sheet index, not attribute data"),
        _svc("GeoNB_SNB_Atlas", "SNB", "Service New Brunswick", "excluded",
             reason="cartographic atlas rendering service, not attribute data"),
        _svc("GeoNB_SNB_Buildings", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; building footprints carry no attributes beyond geometry"),
        _svc("GeoNB_SNB_Contours", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; elevation contours are cartographic geometry, not agent-queryable attributes"),
        _svc("GeoNB_SNB_Counties", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; NB's 15 counties are shipped statically in data://nb/counties"),
        _svc("GeoNB_SNB_dtdb_index", "SNB", "Service New Brunswick", "excluded",
             reason="digital-topographic sheet index, not attribute data"),
        _svc("GeoNB_SNB_FSAs", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; forward sortation areas are Canada Post reference geography, not NB data"),
        _svc("GeoNB_SNB_Historical_Municipal_Areas", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; pre-2023-reform boundaries, historical value only"),
        _svc("GeoNB_SNB_ImageIndex", "SNB", "Service New Brunswick", "excluded",
             reason="imagery tile index, not attribute data"),
        _svc("GeoNB_SNB_ImageryYear", "SNB", "Service New Brunswick", "excluded",
             reason="imagery capture-year index, not attribute data"),
        _svc("GeoNB_SNB_LidarIndex", "SNB", "Service New Brunswick", "excluded",
             reason="lidar tile index, not attribute data"),
        _svc("GeoNB_SNB_Municipal_Information", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; municipal attributes overlap the parcel/civic-address curated pair"),
        _svc("GeoNB_SNB_Municipal_Planning", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; zoning/planning overlays are municipality-scoped (municipal NB portals are a separate phase per CONTEXT.md)"),
        _svc("GeoNB_SNB_NBDEMgrid", "SNB", "Service New Brunswick", "excluded",
             reason="elevation grid tile index, not attribute data"),
        _svc("GeoNB_SNB_NBDEMyear", "SNB", "Service New Brunswick", "excluded",
             reason="elevation capture-year index, not attribute data"),
        _svc("GeoNB_SNB_NRWN", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; national road network reference geometry, not NB attribute data"),
        _svc("GeoNB_SNB_Pan", "SNB", "Service New Brunswick", "excluded",
             reason="panchromatic imagery rendering service, not attribute data"),
        _svc("GeoNB_SNB_Parcels", "SNB", "Service New Brunswick", "curated",
             curated_tool="nb_get_parcels", curated_layer_id=0),
        _svc("GeoNB_SNB_Scanned_Topo_Map_Index", "SNB", "Service New Brunswick", "excluded",
             reason="scanned-map tile index, not attribute data"),
        _svc("GeoNB_SNB_Server_Log_Metrics", "SNB", "Service New Brunswick", "excluded",
             reason="GeoNB server telemetry — operator diagnostics, not open data"),
        _svc("GeoNB_SNB_SurveyControlNetwork", "SNB", "Service New Brunswick", "long_tail",
             reason="reachable via nb_query_geonb_layer; geodetic survey monuments are a surveyor tool, no general agent value"),
    ]
    curated_count = sum(1 for s in services if s["status"] == "curated")
    excluded_count = sum(1 for s in services if s["status"] == "excluded")
    long_tail_count = sum(1 for s in services if s["status"] == "long_tail")
    return json.dumps(
        {
            "services": services,
            "_meta": {
                "count": len(services),
                "curated_count": curated_count,
                "excluded_count": excluded_count,
                "long_tail_count": long_tail_count,
                "portal": "geonb.snb.ca",
                "technology": "bare ArcGIS Server (MapServer only, zero FeatureServer)",
                "enumerated_date": "2026-07-30",
                "layer_id_warning_en": (
                    "Layer ids here were resolved LIVE against geonb.snb.ca (21-SPIKE.md) — "
                    "GeoNB layer 0 is frequently NOT the primary layer. Crown Land's only "
                    "layer is 3; layer 0 does not exist on that service."
                ),
                "layer_id_warning_fr": (
                    "Les identifiants de couche ici ont été résolus EN DIRECT sur "
                    "geonb.snb.ca (21-SPIKE.md) — la couche 0 de GeoNB N'EST PAS souvent la "
                    "couche principale. La seule couche des terres de la Couronne est 3 ; "
                    "la couche 0 n'existe pas sur ce service."
                ),
                "long_tail_path": "nb_list_geonb_services -> nb_get_geonb_service_layers -> nb_query_geonb_layer",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://nb/counties",
    mime_type="application/json",
    name="nb_counties",
    title="New Brunswick's 15 Counties — English and French Names",
)
async def nb_counties() -> str:
    """JSON list of New Brunswick's 15 counties with English and French names.

    Use as the valid county= filter values for nb_get_parcels and any long-tail
    query against GeoNB_SNB_Counties (un-curated; this static list replaces it,
    per D-07). Embedded statically — not fetched from GeoNB.
    """
    counties = [
        {"name_en": "Albert", "name_fr": "Albert"},
        {"name_en": "Carleton", "name_fr": "Carleton"},
        {"name_en": "Charlotte", "name_fr": "Charlotte"},
        {"name_en": "Gloucester", "name_fr": "Gloucester"},
        {"name_en": "Kent", "name_fr": "Kent"},
        {"name_en": "Kings", "name_fr": "Kings"},
        {"name_en": "Madawaska", "name_fr": "Madawaska"},
        {"name_en": "Northumberland", "name_fr": "Northumberland"},
        {"name_en": "Queens", "name_fr": "Queens"},
        {"name_en": "Restigouche", "name_fr": "Restigouche"},
        {"name_en": "Saint John", "name_fr": "Saint-Jean"},
        {"name_en": "Sunbury", "name_fr": "Sunbury"},
        {"name_en": "Victoria", "name_fr": "Victoria"},
        {"name_en": "Westmorland", "name_fr": "Westmorland"},
        {"name_en": "York", "name_fr": "York"},
    ]
    return json.dumps(
        {
            "counties": counties,
            "_meta": {
                "count": len(counties),
                "description_en": (
                    "New Brunswick's 15 counties. Use as county= for nb_get_parcels. "
                    "GeoNB_SNB_Counties (long tail) is superseded by this static list per D-07."
                ),
                "description_fr": (
                    "Les 15 comtés du Nouveau-Brunswick. À utiliser comme county= pour "
                    "nb_get_parcels. GeoNB_SNB_Counties (longue traîne) est remplacé par "
                    "cette liste statique selon D-07."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://nb/health-regions",
    mime_type="application/json",
    name="nb_health_regions",
    title="New Brunswick's 2 Regional Health Authorities + Facility-Type Dispatch",
)
async def nb_health_regions() -> str:
    """JSON catalogue of New Brunswick's 2 regional health authorities and the
    nb_get_health_facilities facility_type dispatch (constants.HEALTH_FACILITY_LAYERS).

    Use to know the valid facility_type argument values without a probe, and which
    of the two RHAs (Horizon / Vitalité) each hospital layer covers.
    """
    authorities = [
        {
            "id": "horizon",
            "name_en": "Horizon Health Network",
            "name_fr": "Réseau de santé Horizon",
            "hospital_facility_type": "hospital_horizon",
            "hospital_layer": 0,
        },
        {
            "id": "vitalite",
            "name_en": "Vitalité Health Network",
            "name_fr": "Réseau de santé Vitalité",
            "hospital_facility_type": "hospital_vitalite",
            "hospital_layer": 1,
        },
    ]
    facility_types = [
        {"value": "hospital_horizon", "layer": 0, "description_en": "Horizon Health Network hospitals", "description_fr": "Hôpitaux du Réseau de santé Horizon"},
        {"value": "hospital_vitalite", "layer": 1, "description_en": "Vitalité Health Network hospitals", "description_fr": "Hôpitaux du Réseau de santé Vitalité"},
        {"value": "after_hours_clinic", "layer": 2, "description_en": "After-hours clinics", "description_fr": "Cliniques sans rendez-vous"},
        {"value": "adult_residential_centre", "layer": 3, "description_en": "Adult residential centres", "description_fr": "Centres résidentiels pour adultes"},
        {"value": "nursing_home", "layer": 4, "description_en": "Licensed nursing homes", "description_fr": "Foyers de soins agréés"},
        {"value": "pharmacy", "layer": 5, "description_en": "Pharmacies", "description_fr": "Pharmacies"},
    ]
    return json.dumps(
        {
            "authorities": authorities,
            "facility_types": facility_types,
            "_meta": {
                "count_authorities": len(authorities),
                "count_facility_types": len(facility_types),
                "source_service": "GeoNB_Health_Facilities",
                "tool": "nb_get_health_facilities",
                "schema_note_en": (
                    "Layers 0-1 use a compact schema (Hospital_N, Name_E/Name_F, "
                    "Telephone_). Layers 2-5 use a much wider Esri-geocoder-derived "
                    "schema (Match_addr, AddNum/StName/StType, bed/client counts)."
                ),
                "schema_note_fr": (
                    "Les couches 0-1 utilisent un schéma compact (Hospital_N, "
                    "Name_E/Name_F, Telephone_). Les couches 2-5 utilisent un schéma "
                    "dérivé du géocodeur Esri, beaucoup plus large."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://nb/school-districts",
    mime_type="application/json",
    name="nb_school_districts",
    title="New Brunswick Anglophone/Francophone School Sectors and Districts",
)
async def nb_school_districts() -> str:
    """JSON catalogue of New Brunswick's anglophone/francophone school sectors,
    their districts, and the nb_get_public_schools sector dispatch
    (constants.SCHOOL_SECTOR_LAYERS).

    Notes that GeoNB_EECD_PublicSchools field names (strID, strNM, strAD1, strGR,
    strURL) are truncated shapefile artefacts — not display names.
    """
    sectors = [
        {
            "id": "anglophone",
            "name_en": "Anglophone Sector",
            "name_fr": "Secteur anglophone",
            "sector_layer": 0,
            "districts_en": ["Anglophone East", "Anglophone West", "Anglophone North", "Anglophone South"],
            "districts_fr": ["Anglophone East", "Anglophone West", "Anglophone North", "Anglophone South"],
        },
        {
            "id": "francophone",
            "name_en": "Francophone Sector",
            "name_fr": "Secteur francophone",
            "sector_layer": 1,
            "districts_en": [
                "Francophone Northeast School District",
                "Francophone Northwest School District",
                "Francophone South School District",
            ],
            "districts_fr": [
                "District scolaire francophone Nord-Est",
                "District scolaire francophone Nord-Ouest",
                "District scolaire francophone Sud",
            ],
        },
    ]
    return json.dumps(
        {
            "sectors": sectors,
            "_meta": {
                "count": len(sectors),
                "source_service": "GeoNB_EECD_PublicSchools",
                "tool": "nb_get_public_schools",
                "field_name_warning_en": (
                    "Field names on GeoNB_EECD_PublicSchools (strID, strDST, strSEC, "
                    "strNM, strAD1, strAD2, strGR, strURL, intBuilt) are TRUNCATED "
                    "shapefile-derived artefacts, not display names — read from layer "
                    "metadata via nb_get_geonb_service_layers rather than inferring."
                ),
                "field_name_warning_fr": (
                    "Les noms de champs sur GeoNB_EECD_PublicSchools (strID, strDST, "
                    "strSEC, strNM, strAD1, strAD2, strGR, strURL, intBuilt) sont des "
                    "artefacts TRONQUÉS dérivés de shapefiles, pas des noms d'affichage — "
                    "consultez les métadonnées de couche via nb_get_geonb_service_layers "
                    "plutôt que de les deviner."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Documentation guides (docs://) — markdown with both languages inline
# ---------------------------------------------------------------------------


@resource(
    "docs://nb/portal-guide",
    mime_type="text/markdown",
    name="nb_portal_guide",
    title="New Brunswick Open Data Portal Architecture Guide — Dead Ends, Live Surfaces, 511",
)
async def nb_portal_guide() -> str:
    """Markdown guide on New Brunswick's open data portal architecture.

    States: discovery for tabular data runs against the federal catalogue
    (open.canada.ca, organization:nb, 221 datasets) because NB has no provincial
    CKAN; data.gnb.ca/opendata.gnb.ca/nbopendata.ca do not resolve; the GeoNB
    ArcGIS Hub returns HTTP 401; GeoNB is a bare ArcGIS Server (62 MapServer
    services, zero FeatureServer); gnb.socrata.com is a live keyless Socrata
    portal with 312 datasets (21-01 checkpoint option-a); NB 511 exists but
    rejects every unkeyed request (NEW_BRUNSWICK_511_KEY). Includes the D-12
    bilingual duplicate-record note.
    """
    return """# New Brunswick Open Data Portal Guide

## English

### Discovery Architecture: Three Surfaces

New Brunswick has **no provincial CKAN portal**. Discovery for tabular datasets runs
against **`open.canada.ca`** (the federal CKAN catalogue) filtered server-side to
`organization:nb` — 221 first-party New Brunswick datasets. This is the only NB
tabular catalogue; there is no `organization` parameter to widen or bypass it (T-21-04).

| Surface | Base URL | Technology | Tools |
|---------|----------|------------|-------|
| Federal CKAN (NB-scoped) | `open.canada.ca` | CKAN Action API | `nb_search_datasets`, `nb_get_dataset_details`, `nb_query_dataset`, `nb_list_organizations`, `nb_list_categories` |
| gnb.socrata.com | `gnb.socrata.com` | Socrata SODA | `nb_search_gnb_socrata_datasets`, `nb_query_gnb_socrata_dataset` |
| GeoNB | `geonb.snb.ca/arcgis/rest/services` | bare ArcGIS Server | `nb_list_geonb_services`, `nb_get_geonb_service_layers`, `nb_query_geonb_layer` + 9 curated tools |
| NB 511 | `511.gnb.ca/api/v2` | key-gated REST | `nb_get_road_events`, `nb_get_winter_road_conditions`, `nb_get_traffic_cameras` |

### Verified Dead Ends — Do Not Re-Investigate

The following hostnames were probed at plan time and confirmed unreachable. They are
**not** placeholders for future work — they are permanently dead:

- `data.gnb.ca` — DNS failure, does not resolve
- `opendata.gnb.ca` — DNS failure, does not resolve
- `nbopendata.ca` — DNS failure, does not resolve
- GeoNB ArcGIS **Hub** Search API (`geonb-snb.opendata.arcgis.com`) — returns
  **HTTP 401** `"private org id ... is not accessible"`. This is why GeoNB discovery
  uses a bare ArcGIS Server directory enumerator (`nb_list_geonb_services`) instead
  of the Hub Search API pattern used by York Region, Manitoba, Saskatchewan and Alberta.

### GeoNB: Bare ArcGIS Server, Not Hub

`geonb.snb.ca/arcgis/rest/services` is a **bare ArcGIS Server** — 62 `MapServer`
services, **zero `FeatureServer`** endpoints, and no Hub Search API in front of it
(live-enumerated 2026-07-30, `21-SPIKE.md`). Layer ids are **non-guessable**: Crown
Land's only layer is 3 (layer 0 does not exist on that service); Wetlands' usable
layer is 2. See `data://nb/geonb-services` for the full 62-service catalogue and
`docs://nb/geonb-query-guide` for the three-step discovery path.

### gnb.socrata.com — Live Provincial Portal (21-01 Checkpoint: option-a)

**This surface contradicts an earlier planning assumption that New Brunswick has no
provincial catalogue.** A live plan-time probe (2026-07-30) found `gnb.socrata.com`
answering `/api/catalog/v1` with **312 datasets** (674 assets), keyless, HTTP 200.
The federal-CKAN NB resource URLs point directly at it
(`gnb.socrata.com/api/views/{id}/rows.csv`). The user selected **option-a** at the
Task 2 blocking checkpoint in `21-01-PLAN.md`: two dedicated tools
(`nb_search_gnb_socrata_datasets`, `nb_query_gnb_socrata_dataset`) join the discovery
surface, reusing `shared/socrata.py` verbatim — zero new client technology. The
locked federal-CKAN discovery (`nb_search_datasets` etc.) is untouched and stays the
primary discovery path; gnb.socrata.com is an additional, separate catalogue.

### NB 511 — Key-Gated

`511.gnb.ca/api/v2` exists and responds, but **every unkeyed request** returns
`<Error><Message>Invalid Key</Message></Error>`. `nb_get_road_events`,
`nb_get_winter_road_conditions`, and `nb_get_traffic_cameras` return a
`NOT_CONFIGURED` envelope (not an exception) until the `NEW_BRUNSWICK_511_KEY`
environment variable is set. This is the expected default state — no key is required
to use the rest of this module.

### Bilingual Records (D-12): Watch for Duplicate FR/EN Pairs

New Brunswick's federal-CKAN publisher sometimes publishes a dataset as **two
separate CKAN records** — one French, one English — rather than one record with
`title_translated`/`notes_translated` fields covering both languages. When
`nb_search_datasets` returns two near-identical results (same subject, different
language titles), this is the EXPECTED, CORRECT behaviour for those datasets, not a
duplicate to report as a bug. `nb_get_dataset_details(lang='fr')` and
`nb_search_datasets(..., lang='fr')` follow a fallback chain: requested language
first, then English, then the plain field — this works correctly for both the
genuinely-bilingual case and the separately-published-pair case.

---

## Français

### Architecture de découverte : trois surfaces

Le Nouveau-Brunswick n'a **aucun portail CKAN provincial**. La découverte de jeux de
données tabulaires se fait sur **`open.canada.ca`** (catalogue CKAN fédéral) filtré
côté serveur à `organization:nb` — 221 jeux de données de première partie du
Nouveau-Brunswick. C'est le seul catalogue tabulaire du N.-B. ; il n'existe aucun
paramètre `organization` pour élargir ou contourner ce filtre (T-21-04).

### Impasses vérifiées — ne pas réenquêter

`data.gnb.ca`, `opendata.gnb.ca` et `nbopendata.ca` échouent en résolution DNS
(impasses permanentes, non des espaces réservés). Le Hub ArcGIS de GeoNB
(`geonb-snb.opendata.arcgis.com`) retourne **HTTP 401**
`"private org id ... is not accessible"`.

### GeoNB : ArcGIS Server nu, pas de Hub

`geonb.snb.ca/arcgis/rest/services` est un **ArcGIS Server nu** — 62 services
`MapServer`, **zéro point de terminaison `FeatureServer`**, et aucune API Hub Search
en façade. Les identifiants de couche ne sont PAS devinables : la seule couche des
terres de la Couronne est 3, pas 0.

### gnb.socrata.com — Portail provincial en direct (Décision 21-01 : option-a)

**Cette surface contredit une hypothèse de planification antérieure selon laquelle le
Nouveau-Brunswick n'a pas de catalogue provincial.** Une sonde en direct
(2026-07-30) a trouvé `gnb.socrata.com` répondant avec **312 jeux de données**, sans
clé, HTTP 200. L'utilisateur a choisi **l'option-a** : deux outils dédiés
(`nb_search_gnb_socrata_datasets`, `nb_query_gnb_socrata_dataset`) rejoignent la
surface de découverte, en réutilisant `shared/socrata.py` tel quel.

### NB 511 — Verrouillé par clé

`511.gnb.ca/api/v2` existe mais **toute requête non authentifiée** retourne
`<Error><Message>Invalid Key</Message></Error>`. Les outils 511 retournent une
enveloppe `NOT_CONFIGURED` jusqu'à ce que la variable d'environnement
`NEW_BRUNSWICK_511_KEY` soit définie.

### Enregistrements bilingues (D-12) : paires FR/EN dupliquées

Le Nouveau-Brunswick publie parfois un jeu de données comme **deux enregistrements
CKAN distincts** — un français, un anglais — plutôt qu'un seul enregistrement
bilingue. Des résultats quasi-identiques dans `nb_search_datasets` sont donc
ATTENDUS et CORRECTS, pas un doublon à signaler.
"""


@resource(
    "docs://nb/geonb-query-guide",
    mime_type="text/markdown",
    name="nb_geonb_query_guide",
    title="GeoNB Query How-To — Three-Step Discovery, WHERE Syntax, and Four Traps",
)
async def nb_geonb_query_guide() -> str:
    """Markdown how-to for querying GeoNB (geonb.snb.ca), the bare ArcGIS Server surface.

    Walks the three-step path (list services -> list a service's layers -> query
    that layer) with a worked GeoNB_DNR_Crown_Land example, WHERE-clause syntax
    (ArcGIS SQL-92), the record cap/truncation flag, the three filter-required
    layers, truncated shapefile field names, and the Crown Land integer holder code.
    """
    return """# GeoNB Query Guide

## English

### The Three-Step Discovery Path

GeoNB (`geonb.snb.ca/arcgis/rest/services`) is a bare ArcGIS Server — there is no Hub
Search API, so discovery is a three-call path:

1. **List services:** `nb_list_geonb_services()` — returns all 62 service names and
   types (all `MapServer`).
2. **List a service's layers:** `nb_get_geonb_service_layers(service_name=...)` —
   returns the layer ids, names, and field metadata for one service. **Never guess a
   layer id** — GeoNB layer ids are non-sequential and layer 0 is frequently not the
   primary layer.
3. **Query that layer:** `nb_query_geonb_layer(service_name=..., layer_id=..., where=...)`
   — returns features filtered by a WHERE clause.

### Worked Example: `GeoNB_DNR_Crown_Land`

```
Step 1: nb_list_geonb_services() -> confirms "GeoNB_DNR_Crown_Land" exists
Step 2: nb_get_geonb_service_layers(service_name="GeoNB_DNR_Crown_Land")
        -> only layer id is 3 (NOT 0 — layer 0 does not exist on this service)
        -> fields: OBJECTID, Shape, HOLDER, Shape_Length, Shape_Area
Step 3: nb_query_geonb_layer(service_name="GeoNB_DNR_Crown_Land", layer_id=3,
                              where="HOLDER=12345")
        -> or use the curated nb_get_crown_land(holder=12345) shortcut instead
```

### WHERE-Clause Syntax (ArcGIS SQL-92)

GeoNB layers accept a standard ArcGIS SQL-92 WHERE clause:

| Operator | Example |
|----------|---------|
| Equality | `HOLDER=12345` |
| String equality (quoted) | `COUNTY='York'` |
| Comparison | `Hectares>100` |
| AND / OR | `STATUS='Active' AND WETLAND_CLASS='Bog'` |
| LIKE (wildcard `%`) | `STREET LIKE 'Main%'` |
| IN | `COUNTY IN ('York','Kings')` |
| Match everything | `1=1` (the default when no filter is given) |

### Record Cap and Truncation

Every query is capped at `MAX_RECORDS` (5000). The response includes a `truncated`
boolean — when `true`, narrow the WHERE clause rather than assuming the result set
is complete.

### Filter-Required Layers (T-21-03)

Three layers are large enough that the tool layer **rejects an unfiltered call
before any network call**:

- `nb_get_parcels` — 604,520 rows (`GeoNB_SNB_Parcels`)
- `nb_get_civic_addresses` — 373,172 rows (`GeoNB_DPS_Civic_Address`)
- `nb_get_wetlands` — 163,206 rows (`GeoNB_ENV_Wetlands`)

### Truncated Shapefile Field Names

GeoNB field names are truncated shapefile-derived artefacts, not display names —
e.g. `Sheet_Numb`, `Technical_`, `Flood_Haza`, `Hospital_N`, `strID`. Always read
the real field list from `nb_get_geonb_service_layers` rather than inferring from
the truncated name.

### Crown Land: HOLDER Is a Coded Integer, Not a Name

`GeoNB_DNR_Crown_Land`'s `HOLDER` field is a raw integer code with **no
server-exposed name lookup**. Never report a `HOLDER` value as a person or
organization name — it is only usable as an opaque filter value if you already
have it from a prior result.

---

## Français

### Le chemin de découverte en trois étapes

GeoNB est un ArcGIS Server nu — il n'y a pas d'API Hub Search, donc la découverte se
fait en trois appels : lister les services (`nb_list_geonb_services`), lister les
couches d'un service (`nb_get_geonb_service_layers`), puis interroger cette couche
(`nb_query_geonb_layer`).

### Exemple travaillé : `GeoNB_DNR_Crown_Land`

La seule couche est 3 (PAS 0 — la couche 0 n'existe pas sur ce service). Champs :
`OBJECTID`, `Shape`, `HOLDER`, `Shape_Length`, `Shape_Area`.

### Syntaxe de la clause WHERE (ArcGIS SQL-92)

Les couches GeoNB acceptent une clause WHERE SQL-92 standard : `HOLDER=12345`,
`COUNTY='York'`, `Hectares>100`, `STATUS='Active' AND WETLAND_CLASS='Bog'`,
`STREET LIKE 'Main%'`, `COUNTY IN ('York','Kings')`. `1=1` correspond à tout
(valeur par défaut sans filtre).

### Couches à filtre obligatoire (T-21-03)

`nb_get_parcels` (604 520 lignes), `nb_get_civic_addresses` (373 172 lignes) et
`nb_get_wetlands` (163 206 lignes) REJETTENT un appel non filtré avant tout appel
réseau.

### Noms de champs tronqués

Les noms de champs GeoNB sont des artefacts tronqués dérivés de shapefiles
(`Sheet_Numb`, `Technical_`, `Flood_Haza`, `Hospital_N`, `strID`), pas des noms
d'affichage — consultez toujours `nb_get_geonb_service_layers`.

### Terres de la Couronne : HOLDER est un code entier, pas un nom

Le champ `HOLDER` de `GeoNB_DNR_Crown_Land` est un code entier brut SANS
correspondance de nom exposée par le serveur — ne le signalez jamais comme un nom
de personne ou d'organisation.
"""


# ---------------------------------------------------------------------------
# Templates (template://) — markdown with {placeholder} syntax
# ---------------------------------------------------------------------------


@resource(
    "template://nb/flood-risk-report",
    mime_type="text/markdown",
    name="nb_flood_risk_report_template",
    title="New Brunswick Flood Risk Assessment Report Template",
)
async def nb_flood_risk_report_template() -> str:
    """Markdown report skeleton for a New Brunswick flood risk assessment.

    Fill in {placeholder} fields with values from nb_get_flood_hazard_areas,
    nb_get_historical_floods, nb_get_wetlands, and nb_get_civic_addresses calls.
    """
    return """# New Brunswick Flood Risk Assessment — {location}

**Data retrieval date:** {data_retrieval_date}
**Source:** GeoNB (geonb.snb.ca), Environment and Local Government

## Flood Hazard Classification

**Hazard classification:** {hazard_classification}
**Source map sheet (Sheet_Numb / Technical_):** {source_map_sheet}

## Historical Flood Events

| Event | Extent (Shape_Length) | Source | Notes |
|-------|-----------------------|--------|-------|
| 2008/2018 | {flood_event_2008_2018_extent} | {flood_event_2008_2018_source} | {flood_event_2008_2018_notes} |
| 1973 | {flood_event_1973_extent} | — | {flood_event_1973_notes} |

## Wetland Proximity

**Wetlands within scope:** {wetland_proximity}
**Wetland class / status filter used:** {wetland_class_filter}

## Affected Civic Addresses

{affected_civic_addresses}

## Key Findings

1. {finding_1}
2. {finding_2}
3. {finding_3}

## Data Notes

- Flood hazard index, historical floods, and wetlands are all sourced from GeoNB
  (bare ArcGIS Server, no Hub) — layer ids were live-verified, not guessed.
- Wetland and civic-address queries require a filter — an unfiltered call is
  rejected before any network call (T-21-03).
- See `docs://nb/geonb-query-guide` for WHERE-clause syntax and
  `data://nb/geonb-services` for the full service catalogue.
"""
