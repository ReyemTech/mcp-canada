"""Nova Scotia Government Open Data module.

Portal: data.novascotia.ca (Socrata SODA API — NOT CKAN, NOT ArcGIS Hub).
5 catalog discovery tools plus curated tools across:
  - Fishing/Aquaculture (marine leases, landbased licenses, hatchery stocking, production)
  - Environment/Water (surface water quality, boil-water advisories, protected areas, air quality)
  - Health + Demographics (hospitals/LTC, vital statistics, chronic disease prevalence)

NOTE: Transport/511 is HTML-only — deferred. NS ArcGIS Hub (novagis) is deferred.
All data comes from data.novascotia.ca via Socrata SODA (/api/catalog/v1 discovery;
/resource/{id}.json SoQL reads). Keyless reads; X-App-Token optional (future).
"""

MODULE_NAME = "nova_scotia"

MODULE_DESCRIPTION = (
    "Nova Scotia provincial government open data via data.novascotia.ca — "
    "a Socrata (SODA API) portal. "
    "5 catalog discovery tools plus curated tools across "
    "fishing/aquaculture (marine + landbased leases, hatchery stocking, production/employment), "
    "environment/water (surface water quality, boil-water advisories, protected areas, air-quality stations), "
    "and health + demographics (hospitals/LTC facilities, vital statistics, chronic disease prevalence). "
    "Keyless SODA reads; geometry excluded via $select. "
    "Transport/511 and the NS ArcGIS Hub (novagis) are deferred."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes du gouvernement provincial de la Nouvelle-Écosse via "
    "data.novascotia.ca — un portail Socrata (API SODA). "
    "5 outils de découverte de catalogue plus des outils ciblés pour "
    "la pêche et l'aquaculture (baux marins + terrestres, ensemencement en écloseries, production/emploi), "
    "l'environnement et l'eau (qualité de l'eau de surface, avis d'ébullition de l'eau, "
    "aires protégées, stations de qualité de l'air), "
    "et la santé + démographie (hôpitaux/soins de longue durée, statistiques de l'état civil, "
    "prévalence des maladies chroniques). "
    "Lectures SODA sans clé; géométrie exclue via $select. "
    "Transport/511 et le Hub ArcGIS NS (novagis) sont différés."
)
