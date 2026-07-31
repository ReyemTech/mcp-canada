"""New Brunswick Government Open Data module.

Four upstream surfaces:
  - Federal CKAN (open.canada.ca) filtered to organization:nb — dataset discovery
    (221 NB-published federal-mirror datasets). NOT a provincial CKAN — data.gnb.ca,
    opendata.gnb.ca and nbopendata.ca do NOT resolve.
  - gnb.socrata.com — New Brunswick's real provincial Socrata portal (312 datasets,
    keyless; checkpoint option-a, added alongside the locked federal CKAN discovery).
  - GeoNB (geonb.snb.ca) ArcGIS **Server** — 62 MapServer services, ZERO FeatureServer.
    This is bare ArcGIS Server REST, NOT ArcGIS Hub (the Hub at
    geonb-snb.opendata.arcgis.com returns HTTP 401). Layer ids are non-guessable
    and are resolved live from {service}/MapServer?f=json. Minerals and provincial
    parks are reachable only through the long-tail nb_query_geonb_layer tool — both
    were dropped from the curated manifest at the checkpoint, so neither has a
    dedicated nb_get_* tool.
  - NB 511 (511.gnb.ca) — key-gated live transportation data (road events, winter
    road conditions, traffic cameras).

MODULE_NAME must match this directory name for FileSystemProvider auto-discovery.
"""

MODULE_NAME = "new_brunswick"

MODULE_DESCRIPTION = (
    "New Brunswick provincial government open data across four upstream surfaces: "
    "the federal open.canada.ca CKAN catalogue filtered to organization:nb "
    "(dataset discovery — NOT a provincial CKAN; data.gnb.ca/opendata.gnb.ca/nbopendata.ca "
    "do not resolve), gnb.socrata.com (New Brunswick's real provincial Socrata portal, "
    "312 datasets, keyless), GeoNB (geonb.snb.ca) ArcGIS Server MapServer services (bare "
    "ArcGIS Server REST, NOT ArcGIS Hub — the Hub returns HTTP 401) covering flood hazard, "
    "wetlands, contaminated sites, Crown land, parcels, civic addresses, health facilities "
    "and public schools — minerals and provincial parks are reachable only through the "
    "long-tail nb_query_geonb_layer tool, not a dedicated curated tool — and NB 511 "
    "(511.gnb.ca) key-gated live road events, winter road conditions and traffic cameras."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial du Nouveau-Brunswick sur quatre "
    "sources en amont : le catalogue CKAN fédéral open.canada.ca filtré sur "
    "organization:nb (découverte de jeux de données — PAS un CKAN provincial; "
    "data.gnb.ca/opendata.gnb.ca/nbopendata.ca ne résolvent pas), gnb.socrata.com "
    "(le véritable portail Socrata provincial du Nouveau-Brunswick, 312 jeux de "
    "données, sans clé), GeoNB (geonb.snb.ca) services ArcGIS Server MapServer "
    "(ArcGIS Server brut, PAS ArcGIS Hub — le Hub retourne HTTP 401) couvrant les "
    "risques d'inondation, les milieux humides, les sites contaminés, les terres de "
    "la Couronne, les parcelles, les adresses civiques, les établissements de santé "
    "et les écoles publiques — les minéraux et les parcs provinciaux ne sont "
    "accessibles que via l'outil à longue traîne nb_query_geonb_layer, pas un outil "
    "dédié — et le NB 511 (511.gnb.ca) avec clé requise pour les événements routiers "
    "en direct, l'état des routes hivernales et les caméras de circulation."
)
