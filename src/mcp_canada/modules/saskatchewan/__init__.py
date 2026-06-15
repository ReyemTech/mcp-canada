"""Saskatchewan Government Open Data module.

Primary portal: geohub.saskatchewan.ca (ArcGIS Hub / ArcGIS Online org zcv98lgAl8xQ04cW).
5 Hub discovery tools plus curated FeatureServer tools across:
  - Agriculture (crop yields by region, grain elevator locations)
  - Energy / mining (potash, uranium, helium, coal mineral mines dispatch)
  - Environment / wildfire (fire bans by scope, historic wildfire boundaries, air quality)
  - Water / WSA (hydrometric gauging stations, reservoirs)

NOTE: data.saskatchewan.ca does NOT exist — Saskatchewan has no provincial CKAN portal.
Water data is on the separate WSA ArcGIS org 7MBdlVpjqbfBhQer;
fire bans are on the SPSA REST server gis.saskatchewan.ca/egis (separate ArcGIS REST server).
All data comes from geohub.saskatchewan.ca (ArcGIS Hub), WSA Hub, or SPSA GIS.
Default language: en. All tools bilingual via `lang: Literal["en", "fr"] = "en"`.
"""

MODULE_NAME = "saskatchewan"

MODULE_DESCRIPTION = (
    "Saskatchewan provincial government open data via geohub.saskatchewan.ca — "
    "an ArcGIS Hub powered by ArcGIS Online org zcv98lgAl8xQ04cW. "
    "5 Hub discovery tools plus curated FeatureServer tools across "
    "agriculture (crop yields, grain elevators), energy/mining (potash/uranium/helium/coal), "
    "environment (fire bans, historic wildfires, air quality), and "
    "water (WSA hydrometric stations, reservoirs). "
    "Water data is on the separate WSA ArcGIS org 7MBdlVpjqbfBhQer; "
    "fire bans are on the SPSA REST server gis.saskatchewan.ca/egis."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial de la Saskatchewan via "
    "geohub.saskatchewan.ca — un ArcGIS Hub propulsé par "
    "l'organisation ArcGIS Online zcv98lgAl8xQ04cW. "
    "5 outils de découverte Hub plus des outils FeatureServer pour "
    "l'agriculture (rendements des cultures, silos-élévateurs), "
    "l'énergie et les mines (potasse/uranium/hélium/charbon), "
    "l'environnement (interdictions de feu, incendies historiques, qualité de l'air) et "
    "l'eau (stations hydrométriques WSA, réservoirs). "
    "Les données sur l'eau proviennent de l'organisation WSA ArcGIS 7MBdlVpjqbfBhQer; "
    "les interdictions de feu viennent du serveur REST SPSA gis.saskatchewan.ca/egis."
)
