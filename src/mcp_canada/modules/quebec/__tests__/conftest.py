"""Shared fixtures for quebec module unit tests.

Covers CKAN (package_search, package_show, org/group lists), datastore
(ER wait times, health installations, AQ stations), and MTQ WFS CSV
(road works, road events, bridges) sample responses.

All fixtures mirror real Données Québec response shapes (verified 2026-04-11).
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# CKAN fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_ckan_package_search_response():
    """package_search — mirrors Données Québec response shape (verified 2026-04-11)."""
    return {
        "success": True,
        "result": {
            "count": 1593,
            "results": [
                {
                    "id": "d1a7c5e0-1111-4222-8333-444444444444",
                    "name": "repertoire-des-municipalites-du-quebec",
                    "title": "Répertoire des municipalités du Québec",
                    "notes": "Liste officielle des municipalités...",
                    "organization": {
                        "name": "affaires-municipales-et-occupation-du-territoire",
                        "title": "Ministère des Affaires municipales et de l'Habitation",
                    },
                    "license_id": "cc-by",
                    "update_frequency": "continu",
                    "groups": [
                        {
                            "name": "gouvernement-finances",
                            "display_name": "Gouvernement et finances",
                        }
                    ],
                    "num_resources": 3,
                    "num_tags": 5,
                }
            ],
        },
    }


@pytest.fixture
def sample_ckan_package_show_response():
    """package_show with resources list including datastore_active flag."""
    return {
        "success": True,
        "result": {
            "id": "abc123",
            "name": "fichier-horaire-des-donnees-de-la-situation-a-l-urgence",
            "title": "Données horaires de la situation à l'urgence",
            "notes": "Données mises à jour toutes les heures...",
            "organization": {
                "name": "msss",
                "title": "Ministère de la Santé et des Services sociaux",
            },
            "license_id": "cc-by",
            "update_frequency": "horaire",
            "resources": [
                {
                    "id": "a9272cc9-8234-40d1-9806-9f6b4c75c20d",
                    "name": "Données horaires ER",
                    "format": "CSV",
                    "url": "https://example.com/er.csv",
                    "datastore_active": True,
                }
            ],
        },
    }


@pytest.fixture
def sample_ckan_package_show_csv_only_response():
    """package_show for a dataset with CSV resource but datastore_active=False."""
    return {
        "success": True,
        "result": {
            "id": "def456",
            "name": "feux-de-foret",
            "title": "Feux de forêt",
            "notes": "Données sur les feux de forêt...",
            "organization": {
                "name": "mrn",
                "title": "Ministère des Ressources naturelles",
            },
            "license_id": "cc-by",
            "update_frequency": "annuel",
            "resources": [
                {
                    "id": "res-shp-001",
                    "name": "Feux de forêt SHP",
                    "format": "SHP",
                    "url": "https://diffusion.mffp.gouv.qc.ca/feux.shp",
                    "datastore_active": False,
                }
            ],
        },
    }


@pytest.fixture
def sample_ckan_organization_list_response():
    """organization_list — 3-org sample from the 139-org federated DQ catalogue."""
    return {
        "success": True,
        "result": [
            {
                "name": "msss",
                "title": "Ministère de la Santé et des Services sociaux",
                "package_count": 42,
            },
            {
                "name": "mtq",
                "title": "Ministère des Transports du Québec",
                "package_count": 35,
            },
            {
                "name": "mrn",
                "title": "Ministère des Ressources naturelles et des Forêts",
                "package_count": 28,
            },
        ],
    }


@pytest.fixture
def sample_ckan_group_list_response():
    """group_list?all_fields=true — DQ has 10 thematic groups (unlike BC which returns HTTP 403)."""
    return {
        "success": True,
        "result": [
            {"name": "sante", "display_name": "Santé", "package_count": 120},
            {
                "name": "gouvernement-finances",
                "display_name": "Gouvernement et finances",
                "package_count": 85,
            },
            {
                "name": "environnement",
                "display_name": "Environnement, ressources naturelles et énergie",
                "package_count": 65,
            },
            {
                "name": "infrastructures",
                "display_name": "Infrastructures",
                "package_count": 55,
            },
            {
                "name": "economie",
                "display_name": "Économie et emploi",
                "package_count": 45,
            },
        ],
    }


# ---------------------------------------------------------------------------
# CKAN datastore fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_datastore_er_response():
    """datastore_search for MSSS ER wait times — 2-row sample (116 total in production)."""
    return {
        "success": True,
        "result": {
            "total": 116,
            "records": [
                {
                    "_id": 1,
                    "Nom_etablissement": "CISSS du Bas-Saint-Laurent",
                    "Nom_installation": "Hôpital de Rimouski",
                    "Nombre_de_civieres_fonctionnelles": 20,
                    "Nombre_de_civieres_occupees": 25,
                    "Nombre_de_patients_sur_civiere_plus_de_24_heures": 3,
                    "Nombre_de_patients_sur_civiere_plus_de_48_heures": 1,
                    "Mise_a_jour": "2026-04-11 08:00",
                },
                {
                    "_id": 2,
                    "Nom_etablissement": "CIUSSS de la Capitale-Nationale",
                    "Nom_installation": "Hôpital de l'Enfant-Jésus",
                    "Nombre_de_civieres_fonctionnelles": 35,
                    "Nombre_de_civieres_occupees": 40,
                    "Nombre_de_patients_sur_civiere_plus_de_24_heures": 5,
                    "Nombre_de_patients_sur_civiere_plus_de_48_heures": 2,
                    "Mise_a_jour": "2026-04-11 08:00",
                },
            ],
            "fields": [],
        },
    }


@pytest.fixture
def sample_datastore_installations_response():
    """datastore_search for MSSS health installations — 1-row sample with type flags."""
    return {
        "success": True,
        "result": {
            "total": 1592,
            "records": [
                {
                    "_id": 1,
                    "INSTAL_COD": "12345",
                    "INSTAL_NOM": "Hôpital de Chicoutimi",
                    "ETAB_NOM": "CIUSSS du Saguenay-Lac-Saint-Jean",
                    "RSS_NOM": "Saguenay-Lac-Saint-Jean",
                    "MRC_NOM": "Le Fjord-du-Saguenay",
                    "MUN_NOM": "Saguenay",
                    "ADRESSE": "305 Rue Saint-Vallier",
                    "CODE_POSTA": "G7H 5H6",
                    "LONGITUDE": -71.0666,
                    "LATITUDE": 48.4277,
                    "CLSC": "Non",
                    "CHSGS": "Oui",
                    "CHSLD": "Non",
                    "CHPSY": "Non",
                    "DATE_MAJ": "2026-01-15",
                },
            ],
            "fields": [],
        },
    }


@pytest.fixture
def sample_datastore_aq_stations_response():
    """datastore_search for RSQAQ air quality stations — 2-row sample (245 total)."""
    return {
        "success": True,
        "result": {
            "total": 245,
            "records": [
                {
                    "_id": 1,
                    "ID_STATION": "06033",
                    "NOM_STATION": "Montréal - Anjou",
                    "RA": "06",
                    "ADRESSE": "7575 rue Châteauneuf",
                    "MUNICIPALITE": "Montréal",
                    "TYPE_MILIEU": "Urbain",
                    "DATE_OUVERTURE": "2001-01-01",
                    "DATE_FERMETURE": None,
                    "LATITUDE": 45.6041,
                    "LONGITUDE": -73.5626,
                },
                {
                    "_id": 2,
                    "ID_STATION": "03002",
                    "NOM_STATION": "Québec - Vieux-Québec",
                    "RA": "03",
                    "ADRESSE": "100 Grande Allée Est",
                    "MUNICIPALITE": "Québec",
                    "TYPE_MILIEU": "Urbain",
                    "DATE_OUVERTURE": "1995-06-01",
                    "DATE_FERMETURE": None,
                    "LATITUDE": 46.8139,
                    "LONGITUDE": -71.2082,
                },
            ],
            "fields": [],
        },
    }


# ---------------------------------------------------------------------------
# MTQ WFS CSV fixtures (parsed rows — result of fetch_and_parse)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_mamh_municipalities_csv():
    """MAMH MUN.csv — 2-row sample (1,282 rows in production)."""
    return [
        {
            "mcode": "66023",
            "munnom": "Montréal",
            "regadm": "06",
            "mrc": "Montréal",
            "mpopul": "1762949",
            "msuperf": "365.13",
            "mcodedesi": "Ville",
            "mayor": "Mayor Name",
        },
        {
            "mcode": "23027",
            "munnom": "Québec",
            "regadm": "03",
            "mrc": "Québec",
            "mpopul": "549459",
            "msuperf": "454.09",
            "mcodedesi": "Ville",
            "mayor": "Mayor Name",
        },
    ]


@pytest.fixture
def sample_mtq_road_works_csv():
    """MTQ chantiers_mtmdet WFS CSV — 1-row sample. Bilingual description columns."""
    return [
        {
            "identifiant": "154000",
            "identifiantChantier": "CH-A25-2026-01",
            "routeAutoroute": "A-25",
            "entraveType": "Fermeture partielle",
            "debut": "2026-04-10",
            "fin": "2026-04-15",
            "miseAJour": "2026-04-11 06:00",
            "identificationDesTravaux": "Réfection asphalte",
            "localisation": "km 8",
            "direction": "Nord",
            "descriptionFrancais": "Fermeture d'une voie sens nord entre km 7 et km 9.",
            "descriptionAnglais": "One lane closed northbound between km 7 and km 9.",
            "couleurLigne": "orange",
            "source": "MTQ",
        }
    ]


@pytest.fixture
def sample_mtq_road_events_csv():
    """MTQ evenements WFS CSV — 1-row sample. French-only columns (no EN equivalent)."""
    return [
        {
            "identifiant": "E-2026-001",
            "entrave": "Accident",
            "numeroRoute": "A-40",
            "localisation": "km 20",
            "direction": "Est",
            "municipalite": "Montréal",
            "duree": "2h",
            "cause": "Collision",
            "consequence": "Ralentissement important",
            "detour": "Aucun",
            "regions": "Montréal",
            "enVigueurDepuis": "2026-04-11 08:00",
            "couleurLigne": "red",
        }
    ]


@pytest.fixture
def sample_mtq_bridges_csv():
    """MTQ gsq_v_desc_strct_tri WFS CSV — 1-row sample (50K+ structures in production)."""
    return [
        {
            "ide_strct": "S-12345",
            "num_dossr": "12345",
            "val_annee_": "1985",
            "code_des_s": "Bon",
            "nom_route": "A-10",
            "nom_obstc": "Rivière Yamaska",
            "nom_muncp": "Granby",
            "cod_muncp": "47017",
            "nom_strct": "Pont A-10 sur la rivière Yamaska",
            "num_route": "10",
            "geo_lattd": "45.40",
            "geo_longt": "-72.73",
            "val_longr": "42.5",
            "val_largr_": "12.0",
            "cod_type_s": "Pont",
        }
    ]


@pytest.fixture
def sample_ckan_error_response():
    """CKAN error envelope — for testing error handling in _api_get."""
    return {
        "success": False,
        "error": {
            "message": "Not found",
            "__type": "Not Found Error",
        },
    }
