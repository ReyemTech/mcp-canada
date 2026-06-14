"""Manitoba Government Open Data module.

Primary portal: geoportal.gov.mb.ca (ArcGIS Hub / ArcGIS Online org mMUesHYPkXjaFGfS).
5 Hub discovery tools plus curated FeatureServer tools across:
  - Flood/hydrology (overland flood alerts, provincial waterways, river station CSV)
  - Agriculture & drought (drought monitor, ag weather stations, livestock prices, crop regions)
  - Environment/parks (provincial parks, fisheries waterbody data, provincial forests)
  - Regional health (surgical wait times, rural health care facilities)
  - Transport/511 (road events, winter road conditions, cameras — key-gated)

NOTE: data.manitoba.ca is unreachable; mli.gov.mb.ca is retired (2022-02-09).
All data comes from geoportal.gov.mb.ca (ArcGIS Hub) or Manitoba's 511 REST API.
Default language: en. All tools bilingual via `lang: Literal["en", "fr"] = "en"`.
"""

MODULE_NAME = "manitoba"

MODULE_DESCRIPTION = (
    "Manitoba provincial government open data via geoportal.gov.mb.ca (Data MB) — "
    "an ArcGIS Hub powered by ArcGIS Online org mMUesHYPkXjaFGfS. "
    "5 Hub discovery tools plus curated FeatureServer tools across "
    "flood/hydrology, agriculture & drought, environment/parks, "
    "regional health, and (conditional) Manitoba 511 transport."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial du Manitoba via "
    "geoportal.gov.mb.ca (Data MB) — un ArcGIS Hub propulsé par "
    "l'organisation ArcGIS Online mMUesHYPkXjaFGfS. "
    "5 outils de découverte Hub plus des outils FeatureServer pour "
    "les inondations/hydrologie, l'agriculture et la sécheresse, "
    "l'environnement/parcs, la santé régionale et (conditionnel) "
    "le transport Manitoba 511."
)
