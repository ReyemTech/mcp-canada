"""New Brunswick Government Open Data module.

Three upstream surfaces:
  - Federal CKAN (open.canada.ca) filtered to organization:nb — dataset discovery
    (221 NB-published federal-mirror datasets). NOT a provincial CKAN — data.gnb.ca,
    opendata.gnb.ca and nbopendata.ca do NOT resolve.
  - GeoNB (geonb.snb.ca) ArcGIS **Server** — 62 MapServer services, ZERO FeatureServer.
    This is bare ArcGIS Server REST, NOT ArcGIS Hub (the Hub at
    geonb-snb.opendata.arcgis.com returns HTTP 401). Layer ids are non-guessable
    and are resolved live from {service}/MapServer?f=json.
  - NB 511 (511.gnb.ca) — key-gated live transportation data (road events, winter
    road conditions, traffic cameras).

MODULE_NAME must match this directory name for FileSystemProvider auto-discovery.
"""

MODULE_NAME = "new_brunswick"

MODULE_DESCRIPTION = (
    "New Brunswick provincial government open data across three upstream surfaces: "
    "the federal open.canada.ca CKAN catalogue filtered to organization:nb "
    "(dataset discovery — NOT a provincial CKAN; data.gnb.ca/opendata.gnb.ca/nbopendata.ca "
    "do not resolve), GeoNB (geonb.snb.ca) ArcGIS Server MapServer services (bare ArcGIS "
    "Server REST, NOT ArcGIS Hub — the Hub returns HTTP 401) covering flood hazard, "
    "wetlands, contaminated sites, Crown land, minerals, parks, parcels, civic addresses, "
    "health facilities and public schools, and NB 511 (511.gnb.ca) key-gated live road "
    "events, winter road conditions and traffic cameras."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial du Nouveau-Brunswick sur trois "
    "sources en amont : le catalogue CKAN fédéral open.canada.ca filtré sur "
    "organization:nb (découverte de jeux de données — PAS un CKAN provincial; "
    "data.gnb.ca/opendata.gnb.ca/nbopendata.ca ne résolvent pas), GeoNB (geonb.snb.ca) "
    "services ArcGIS Server MapServer (ArcGIS Server brut, PAS ArcGIS Hub — le Hub "
    "retourne HTTP 401) couvrant les risques d'inondation, les milieux humides, les "
    "sites contaminés, les terres de la Couronne, les minéraux, les parcs, les parcelles, "
    "les adresses civiques, les établissements de santé et les écoles publiques, et le "
    "NB 511 (511.gnb.ca) avec clé requise pour les événements routiers en direct, l'état "
    "des routes hivernales et les caméras de circulation."
)
