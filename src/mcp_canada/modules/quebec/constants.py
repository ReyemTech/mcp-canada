"""Constants for the quebec module — Données Québec CKAN base URL, MTQ WFS CSV endpoints,
rate/cache config, org slugs, and curated resource IDs.

All endpoint URLs and resource IDs live-verified against Données Québec 2026-04-11.
MTQ WFS CSV URLs confirmed working for ms:chantiers_mtmdet, ms:evenements,
ms:gsq_v_desc_strct_tri. Use outputformat=csv only — GeoJSON returns HTTP 400
(MapServer tmpl missing on server, see 16-RESEARCH.md Pitfall 7).
"""

from typing import Final

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

BASE_URL: Final[str] = "https://www.donneesquebec.ca/recherche/api/3/action/"
MTQ_WFS_BASE: Final[str] = "https://ws.mapserver.transports.gouv.qc.ca/swtq"
AQ_INDEX_URL: Final[str] = (
    "https://services3.arcgis.com/0lL78GhXbg1Po7WO/arcgis/rest/services"
    "/IQA_resultat_REST/FeatureServer/0/query"
)

# ---------------------------------------------------------------------------
# HTTP identification (DQ CKAN WAF — set for proper identification)
# ---------------------------------------------------------------------------

USER_AGENT: Final[str] = "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"
DEFAULT_HEADERS: Final[dict[str, str]] = {"User-Agent": USER_AGENT}

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

RATE_GROUP: Final[str] = "quebec_ckan"
RATE_LIMIT: Final[float] = 10.0  # req/s — conservative, matches Ontario/BC CKAN

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------

CACHE_TTL_SEARCH: Final[int] = 3600    # 1hr — CKAN search results, daily municipality data
CACHE_TTL_META: Final[int] = 86400     # 24hr — CKAN metadata, annual datasets, static layers
CACHE_TTL_ACTIVE: Final[int] = 300     # 5min — ER wait times (hourly), road works/events (continuous)
CACHE_TTL_DAILY: Final[int] = 3600     # 1hr — same as SEARCH for datasets with daily updates

# ---------------------------------------------------------------------------
# Organization slugs (verified live 2026-04-11)
# ---------------------------------------------------------------------------

ORG_MSSS: Final[str] = "msss"
ORG_MTQ: Final[str] = "mtq"
ORG_MRN: Final[str] = "mrn"
ORG_MELCCFP: Final[str] = (
    "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques"
)
ORG_MSP: Final[str] = "msp"
ORG_HYDRO: Final[str] = "hydro-quebec"
ORG_SEPAQ: Final[str] = "sepaq"
ORG_ISQ: Final[str] = "isq"
ORG_MAMH: Final[str] = "affaires-municipales-et-occupation-du-territoire"

# ---------------------------------------------------------------------------
# Datastore resource IDs (verified live 2026-04-11)
# ---------------------------------------------------------------------------

MSSS_INSTALLATIONS_RESOURCE_ID: Final[str] = "2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d"
MSSS_ER_RESOURCE_ID: Final[str] = "a9272cc9-8234-40d1-9806-9f6b4c75c20d"
RSQAQ_STATIONS_RESOURCE_ID: Final[str] = "cebea532-a9e0-4a39-8c2d-54f33d937c73"

# ---------------------------------------------------------------------------
# Direct file URLs
# ---------------------------------------------------------------------------

MAMH_MUN_CSV_URL: Final[str] = "https://donneesouvertes.affmunqc.net/repertoire/MUN.csv"

# ---------------------------------------------------------------------------
# MTQ WFS CSV URLs (confirmed working 2026-04-11)
# NOTE: Use outputformat=csv ONLY — GeoJSON returns HTTP 400 (MapServer tmpl missing)
# ---------------------------------------------------------------------------

MTQ_ROAD_WORKS_URL: Final[str] = (
    f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature"
    "&typename=ms:chantiers_mtmdet&outputformat=csv"
)
MTQ_ROAD_EVENTS_URL: Final[str] = (
    f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature"
    "&typename=ms:evenements&outputformat=csv"
)
MTQ_BRIDGES_URL: Final[str] = (
    f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature"
    "&typename=ms:gsq_v_desc_strct_tri&outputformat=csv"
)
MTQ_ROAD_CONDITIONS_URL: Final[str] = (
    f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=GetFeature"
    "&typeName=ms:conditions_routieres&outputFormat=csv"
)

# ---------------------------------------------------------------------------
# Curated dataset package IDs (for package_show in metadata-only tools)
# ---------------------------------------------------------------------------

PKG_FOREST_FIRES: Final[str] = "feux-de-foret"
PKG_PROTECTED_AREAS: Final[str] = "aires-protegees-au-quebec"
PKG_WATER_QUALITY: Final[str] = "suivi-physicochimique-des-rivieres-et-du-fleuve"
PKG_ELECTRICITY: Final[str] = "historique-production-consommation"
