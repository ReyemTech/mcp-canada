"""Flat Pydantic v2 models for the Quebec module.

All models are flat — no nested dicts mirroring the raw API shape.
Bilingual metadata: DQ CKAN uses French-only title/notes fields (no title_translated).
The `lang` parameter on tools affects error messages only, not catalog metadata.
"""

from pydantic import BaseModel, Field


class QuebecDatasetSummary(BaseModel):
    """Summary row returned by quebec_search_datasets."""

    id: str
    name: str  # slug (kebab-case)
    title: str  # French — DQ has no English title field
    notes: str | None = None
    organization_slug: str | None = None
    organization_title: str | None = None
    groups: list[str] = Field(default_factory=list)  # thematic group slugs
    license_id: str | None = None
    update_frequency: str | None = None  # "horaire", "mensuel", "annuel", etc.
    num_resources: int = 0
    num_tags: int = 0


class QuebecResource(BaseModel):
    """A single downloadable/queryable resource within a dataset."""

    id: str
    name: str | None = None
    format: str | None = None  # "CSV", "GeoJSON", "SHP", "GPKG", etc.
    url: str
    datastore_active: bool = False
    size: int | None = None


class QuebecDatasetDetails(BaseModel):
    """Full dataset record returned by quebec_get_dataset_details."""

    id: str
    name: str
    title: str
    notes: str | None = None
    organization_slug: str | None = None
    organization_title: str | None = None
    update_frequency: str | None = None
    license_id: str | None = None
    resources: list[QuebecResource] = Field(default_factory=list)


class QuebecHealthInstallation(BaseModel):
    """MSSS health installation — hospitals, CLSCs, CHSLDs, CHPSYs.

    Source: fichiers-cartographiques-m02-des-installations-et-etablissements
    (datastore_search, resource_id 2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d)
    Total: 1,592 installations.
    """

    instal_code: str | None = None   # INSTAL_COD
    instal_name: str | None = None   # INSTAL_NOM
    etab_name: str | None = None     # ETAB_NOM — parent establishment
    rss_name: str | None = None      # RSS_NOM — health region (région socio-sanitaire)
    mrc_name: str | None = None      # MRC_NOM
    municipality: str | None = None  # MUN_NOM
    address: str | None = None       # ADRESSE
    postal_code: str | None = None   # CODE_POSTA
    latitude: float | None = None    # LATITUDE
    longitude: float | None = None   # LONGITUDE
    is_clsc: bool = False            # CLSC == "Oui"
    is_chsgs: bool = False           # CHSGS == "Oui" — hospital
    is_chsld: bool = False           # CHSLD == "Oui" — long-term care
    is_chpsy: bool = False           # CHPSY == "Oui" — psychiatric
    date_updated: str | None = None  # DATE_MAJ


class QuebecErWaitRow(BaseModel):
    """Single ER department row from the MSSS hourly urgency dataset.

    Source: fichier-horaire-des-donnees-de-la-situation-a-l-urgence
    (datastore_search, resource_id a9272cc9-8234-40d1-9806-9f6b4c75c20d)
    Total: 116 rows (one per hospital ER), updated hourly.
    """

    establishment: str | None = None       # Nom_etablissement
    installation: str | None = None        # Nom_installation
    functional_stretchers: int | None = None   # Nombre_de_civieres_fonctionnelles
    occupied_stretchers: int | None = None     # Nombre_de_civieres_occupees
    patients_over_24h: int | None = None       # Nombre_de_patients_sur_civiere_plus_de_24_heures
    patients_over_48h: int | None = None       # Nombre_de_patients_sur_civiere_plus_de_48_heures
    extraction_time: str | None = None         # Heure_de_l'extraction_(image)
    last_updated: str | None = None            # Mise_a_jour


class QuebecPopulationRow(BaseModel):
    """Municipality row from the MAMH Répertoire des municipalités.

    Source: repertoire-des-municipalites-du-quebec (MUN.csv, 1,282 rows)
    Updated daily.
    """

    mcode: str | None = None         # mcode — municipal code
    municipality: str | None = None  # munnom
    admin_region: str | None = None  # regadm — 17 administrative regions
    mrc: str | None = None           # mrc — regional county municipality
    population: int | None = None    # mpopul
    area_km2: float | None = None    # msuperf
    municipal_type: str | None = None  # mcodedesi — Ville/Village/Municipality
    mayor: str | None = None         # mayor


class QuebecRoadWork(BaseModel):
    """Active road construction zone from MTQ chantiers_mtmdet WFS CSV.

    Source: MTQ_ROAD_WORKS_URL (live, continuous updates)
    Bilingual: descriptionFrancais / descriptionAnglais — selected by lang param.
    """

    identifier: str | None = None      # identifiant
    chantier_id: str | None = None     # identifiantChantier
    route: str | None = None           # routeAutoroute
    obstruction_type: str | None = None  # entraveType
    start: str | None = None           # debut
    end: str | None = None             # fin
    updated: str | None = None         # miseAJour
    work_description: str | None = None  # identificationDesTravaux
    location: str | None = None        # localisation
    direction: str | None = None       # direction
    description: str | None = None     # selected by lang: descriptionFrancais or descriptionAnglais


class QuebecRoadEvent(BaseModel):
    """Active road event/warning from MTQ evenements WFS CSV.

    Source: MTQ_ROAD_EVENTS_URL (live, continuous updates)
    Note: French-only columns — no English equivalent in this CSV.
    """

    identifier: str | None = None    # identifiant
    obstruction: str | None = None   # entrave
    route: str | None = None         # numeroRoute
    location: str | None = None      # localisation
    direction: str | None = None     # direction
    municipality: str | None = None  # municipalite
    duration: str | None = None      # duree
    cause: str | None = None         # cause
    consequence: str | None = None   # consequence
    detour: str | None = None        # detour
    regions: str | None = None       # regions
    active_since: str | None = None  # enVigueurDepuis


class QuebecBridgeStructure(BaseModel):
    """Bridge, culvert (>4.5m), tunnel, or retaining wall from MTQ structure WFS CSV.

    Source: MTQ_BRIDGES_URL (~50K+ structures, requires at least one filter)
    """

    structure_id: str | None = None    # ide_strct
    dossier_num: str | None = None     # num_dossr
    year: int | None = None            # val_annee_ — construction year
    status_code: str | None = None     # code_des_s
    route_name: str | None = None      # nom_route
    obstacle: str | None = None        # nom_obstc — obstacle crossed (river, road, etc.)
    municipality: str | None = None    # nom_muncp
    municipality_code: str | None = None  # cod_muncp
    structure_name: str | None = None  # nom_strct
    route_num: str | None = None       # num_route
    latitude: float | None = None      # geo_lattd
    longitude: float | None = None     # geo_longt
    length: float | None = None        # val_longr (metres)
    width: float | None = None         # val_largr_ (metres)
    structure_type: str | None = None  # cod_type_s — Pont/Ponceau/Tunnel/etc.


class QuebecAirQualityStation(BaseModel):
    """Air quality monitoring station from RSQAQ (Réseau de surveillance de la qualité de l'air).

    Source: rsqaq-stations (datastore_search, resource_id cebea532-a9e0-4a39-8c2d-54f33d937c73)
    Total: 245 rows (active + historical closed stations).
    """

    station_id: str | None = None     # ID_STATION
    station_name: str | None = None   # NOM_STATION
    admin_region: str | None = None   # RA — région administrative code
    address: str | None = None        # ADRESSE
    municipality: str | None = None   # MUNICIPALITE
    milieu_type: str | None = None    # TYPE_MILIEU — Urbain/Rural/Industriel
    date_opened: str | None = None    # DATE_OUVERTURE
    date_closed: str | None = None    # DATE_FERMETURE — None for active stations
    latitude: float | None = None     # LATITUDE
    longitude: float | None = None    # LONGITUDE


class QuebecOrganization(BaseModel):
    """Organization entry from organization_list."""

    name: str          # slug
    title: str
    package_count: int = 0


class QuebecCategory(BaseModel):
    """Thematic group entry from group_list (10 groups on Données Québec).

    NOTE: DQ has 10 meaningful thematic groups (unlike BC which returns HTTP 403
    on group_list). Use group_list for quebec_list_categories, NOT tag_list
    (tag_list returns ~4,200 noisy tags with no hierarchy).
    """

    name: str               # slug
    title: str | None = None
    display_name: str | None = None
    package_count: int = 0
