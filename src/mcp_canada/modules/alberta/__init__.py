"""Alberta Government Open Data module.

Four portals federated into a single Alberta surface:
  - open.alberta.ca CKAN (33,269 datasets — 86% PDF publications, ~1,200 machine-readable)
  - GeoDiscover Alberta ArcGIS REST 11.3 (air quality, river forecast, parks, boundaries)
  - WMBappServices ArcGIS Online (wildfire: active fires, perimeters, bans, forest areas)
  - AHSGIS ArcGIS Online (health: hospitals, EMS, AHS zones, PCN clinics)
  - AER static XLSX/TXT (well licences ST1, production ST3, pipelines ST39, outlook ST98)
  - 511 Alberta JSON API (road events, winter roads, traffic cameras)

Default language: en. All tools bilingual via `lang: Literal["en", "fr"] = "en"`.
"""

MODULE_NAME = "alberta"

MODULE_DESCRIPTION = (
    "Alberta provincial government open data: CKAN catalogue (open.alberta.ca, "
    "33,269 datasets), GeoDiscover Alberta ArcGIS REST 11.3, WMBappServices "
    "wildfire FeatureServers, AHSGIS health FeatureServers, Alberta Energy "
    "Regulator (AER) static reports (ST1/ST3/ST39), and 511 Alberta "
    "road/winter/camera APIs."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial de l'Alberta : catalogue CKAN "
    "(open.alberta.ca, 33 269 jeux de données), GeoDiscover Alberta ArcGIS "
    "REST 11.3, services FeatureServer WMBappServices (feux de forêt), "
    "services FeatureServer AHSGIS (santé), rapports statiques de l'Alberta "
    "Energy Regulator (AER — ST1/ST3/ST39), et API 511 Alberta "
    "(incidents routiers, routes d'hiver, caméras)."
)
