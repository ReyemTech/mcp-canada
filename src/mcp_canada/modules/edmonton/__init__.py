"""Edmonton Open Data module.

Portal: data.edmonton.ca (Socrata SODA API — NOT CKAN).
5 catalog discovery tools: search, dataset details, SoQL query, organizations, categories.

Live-verified 2026-09-04: 1421 datasets, keyless catalog + resource reads.
Sample dataset: "General Building Permits" (24uj-dj8v), category "Urban Planning & Economy".
"""

MODULE_NAME = "edmonton"

MODULE_DESCRIPTION = (
    "City of Edmonton open data via data.edmonton.ca — a Socrata (SODA API) portal, "
    "NOT CKAN. 5 catalog discovery tools: search datasets by keyword, fetch dataset "
    "schema/metadata, run SoQL queries against any dataset, list publishing "
    "organizations, and list domain categories. Keyless SODA reads; 1421 datasets "
    "live-verified 2026-09-04."
)

MODULE_DESCRIPTION_FR = (
    "Données ouvertes de la ville d'Edmonton via data.edmonton.ca — un portail "
    "Socrata (API SODA), PAS CKAN. 5 outils de découverte de catalogue : recherche "
    "de jeux de données par mot-clé, schéma/métadonnées d'un jeu de données, "
    "requêtes SoQL sur tout jeu de données, liste des organisations éditrices, "
    "et liste des catégories de domaine. Lectures SODA sans clé; 1421 jeux de "
    "données vérifiés en direct le 2026-09-04."
)
