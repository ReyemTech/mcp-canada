"""Saskatchewan resources — 7 zero-parameter static resources for Saskatchewan data exploration.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same JSON or markdown body).

Catalog resources (data://):
  data://saskatchewan/crop-regions      — 5 crop reporting regions (SE/SW/Central/NE/NW)
  data://saskatchewan/major-basins      — 6 major river basins with WSA monitoring flags
  data://saskatchewan/health-regions    — Single SHA (province-wide since 2017 merger),
                                          health domain deferred (no public FeatureServer)

Documentation guides (docs://):
  docs://saskatchewan/portal-guide         — Multi-org architecture: GeoHub (zcv98lgAl8xQ04cW)
                                             + WSA (7MBdlVpjqbfBhQer) + SPSA (egis); deferred
                                             transport + health; Petroleum-400 routing;
                                             GOS Standard Unrestricted Use Data Licence v2.0
  docs://saskatchewan/agriculture-data-guide — Crop yields vs PDF crop reports; Crop_Production_2025
                                               boundary-only caveat; grain elevator PR='SK' filter;
                                               mineral mine dispatch

Templates (template://):
  template://saskatchewan/dataset-report  — Dataset exploration report with {placeholder} fields
  template://saskatchewan/wildfire-report — Wildfire situational report template
"""

import json

from fastmcp.resources import resource


__all__ = [
    "saskatchewan_crop_regions",
    "saskatchewan_major_basins",
    "saskatchewan_health_regions",
    "saskatchewan_portal_guide",
    "saskatchewan_agriculture_data_guide",
    "saskatchewan_dataset_report_template",
    "saskatchewan_wildfire_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://) — JSON via json.dumps, bilingual inline
# ---------------------------------------------------------------------------


@resource(
    "data://saskatchewan/crop-regions",
    mime_type="application/json",
    name="saskatchewan_crop_regions",
    title="Saskatchewan's 5 Crop Reporting Regions with Bilingual Labels and Signature Crops",
)
async def saskatchewan_crop_regions() -> str:
    """JSON catalog of Saskatchewan's 5 crop reporting regions with bilingual labels.

    Use to understand which region= value to pass to saskatchewan_get_crop_yields.
    Each region includes location context and its signature crops. 'provincial' (default)
    returns the combined Saskatchewan summary; the 5 regional values return breakdowns.
    See docs://saskatchewan/agriculture-data-guide for the full crop data source guide.
    """
    regions = [
        {
            "id": "southeast",
            "name_en": "Southeast",
            "name_fr": "Sud-Est",
            "location_en": "Weyburn, Estevan, Moosomin — dryland farming, oilfield country",
            "location_fr": "Weyburn, Estevan, Moosomin — agriculture en terres sèches, région pétrolière",
            "signature_crops": ["Durum", "HRSW", "Lentil", "Canola"],
        },
        {
            "id": "southwest",
            "name_en": "Southwest",
            "name_fr": "Sud-Ouest",
            "location_en": "Swift Current, Shaunavon, Maple Creek — semi-arid short-grass prairie",
            "location_fr": "Swift Current, Shaunavon, Maple Creek — prairie courte semi-aride",
            "signature_crops": ["HRSW", "Durum", "Canola", "Chickpea"],
        },
        {
            "id": "central",
            "name_en": "Central",
            "name_fr": "Centre",
            "location_en": "Saskatoon, Humboldt, Outlook — heart of Saskatchewan cropland",
            "location_fr": "Saskatoon, Humboldt, Outlook — cœur des terres cultivées de la Saskatchewan",
            "signature_crops": ["Canola", "HRSW", "Pea", "Lentil"],
        },
        {
            "id": "northeast",
            "name_en": "Northeast",
            "name_fr": "Nord-Est",
            "location_en": "Melfort, Prince Albert, Tisdale — grain belt and boreal fringe",
            "location_fr": "Melfort, Prince Albert, Tisdale — ceinture céréalière et lisière boréale",
            "signature_crops": ["Canola", "HRSW", "Oat", "Barley"],
        },
        {
            "id": "northwest",
            "name_en": "Northwest",
            "name_fr": "Nord-Ouest",
            "location_en": "North Battleford, Lloydminster, Meadow Lake — mixed farming and forestry",
            "location_fr": "North Battleford, Lloydminster, Meadow Lake — agriculture mixte et foresterie",
            "signature_crops": ["Canola", "HRSW", "Barley", "Oat"],
        },
    ]
    return json.dumps(
        {
            "regions": regions,
            "_meta": {
                "count": len(regions),
                "provincial_note_en": (
                    "Use region='provincial' (default) for the combined Saskatchewan summary "
                    "across all 5 regions. Use a region id as region= to get the breakdown "
                    "for that specific crop reporting region."
                ),
                "provincial_note_fr": (
                    "Utilisez region='provincial' (défaut) pour le résumé combiné de la Saskatchewan "
                    "pour les 5 régions. Utilisez un id de région comme region= pour obtenir la "
                    "ventilation de cette région de déclaration de culture."
                ),
                "tool": "saskatchewan_get_crop_yields",
                "crop_types_en": [
                    "HRSW", "Durum", "Oat", "Barley", "Canola", "Mustard",
                    "Soybean", "Pea", "Lentil", "Chickpea", "Canary_seed",
                    "Flax", "Winter_wheat", "Fall_rye", "Other_wheat_",
                ],
                "crop_types_note_en": "Yields returned in bu/acre (bushels per acre)",
                "crop_types_note_fr": "Rendements en bu/acre (boisseaux par acre)",
                "licence_en": "GOS Standard Unrestricted Use Data Licence v2.0",
                "licence_fr": "Licence d'utilisation des données sans restriction standard GOS v2.0",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://saskatchewan/major-basins",
    mime_type="application/json",
    name="saskatchewan_major_basins",
    title="Saskatchewan Major River Basins with WSA Monitoring Flags",
)
async def saskatchewan_major_basins() -> str:
    """JSON catalog of Saskatchewan's major river basins with WSA hydrometric monitoring flags.

    Use to understand which basin= value to pass to saskatchewan_get_wsa_stations.
    Each basin includes the major river, key cities, and whether the WSA operates
    hydrometric gauging stations in that basin. See data://saskatchewan/health-regions
    for health authority context and docs://saskatchewan/portal-guide for the WSA
    ArcGIS org architecture (7MBdlVpjqbfBhQer).
    """
    basins = [
        {
            "name_en": "Qu'Appelle",
            "name_fr": "Qu'Appelle",
            "basin_filter": "Qu Appelle",
            "major_river_en": "Qu'Appelle River (flows east into Assiniboine River)",
            "major_river_fr": "Rivière Qu'Appelle (coule vers l'est dans la rivière Assiniboine)",
            "key_cities": ["Regina", "Fort Qu'Appelle", "Esterhazy"],
            "wsa_monitored": True,
            "notes_en": "Regulated by Qu'Appelle Lakes chain; receives Buffalo Pound reservoir outflow",
            "notes_fr": "Régulée par la chaîne des lacs Qu'Appelle; reçoit l'écoulement du réservoir Buffalo Pound",
        },
        {
            "name_en": "North Saskatchewan",
            "name_fr": "Saskatchewan Nord",
            "basin_filter": "North Saskatchewan",
            "major_river_en": "North Saskatchewan River (rises in Rocky Mountains, flows NE)",
            "major_river_fr": "Rivière Saskatchewan Nord (prend sa source dans les Rocheuses, coule vers NE)",
            "key_cities": ["North Battleford", "Lloydminster"],
            "wsa_monitored": True,
            "notes_en": "Trans-boundary river; flows from Alberta. Feeds Lake Diefenbaker via South Sask",
            "notes_fr": "Rivière transfrontalière; coule depuis l'Alberta. Alimente le lac Diefenbaker via la Sask. Sud",
        },
        {
            "name_en": "South Saskatchewan",
            "name_fr": "Saskatchewan Sud",
            "basin_filter": "South Saskatchewan",
            "major_river_en": "South Saskatchewan River (Red Deer + Oldman join in Alberta)",
            "major_river_fr": "Rivière Saskatchewan Sud (Deer Rouge + Oldman se rejoignent en Alberta)",
            "key_cities": ["Saskatoon", "Outlook", "Elbow"],
            "wsa_monitored": True,
            "notes_en": "Lake Diefenbaker is the major reservoir on this system (WSA operated)",
            "notes_fr": "Le lac Diefenbaker est le principal réservoir de ce système (exploité par la WSA)",
        },
        {
            "name_en": "Assiniboine",
            "name_fr": "Assiniboine",
            "basin_filter": "Assiniboine",
            "major_river_en": "Assiniboine River (flows SE to Manitoba, joins Red River at Winnipeg)",
            "major_river_fr": "Rivière Assiniboine (coule vers SE jusqu'au Manitoba, rejoint la rivière Rouge à Winnipeg)",
            "key_cities": ["Kamsack", "Moosomin"],
            "wsa_monitored": True,
            "notes_en": "Trans-boundary; flows into Manitoba. 2011 near-record flooding",
            "notes_fr": "Transfrontalière; coule vers le Manitoba. Inondations quasi-record en 2011",
        },
        {
            "name_en": "Churchill",
            "name_fr": "Churchill",
            "basin_filter": "Churchill",
            "major_river_en": "Churchill River (flows east through northern Saskatchewan lakes)",
            "major_river_fr": "Rivière Churchill (coule vers l'est à travers les lacs du nord de la Saskatchewan)",
            "key_cities": ["La Ronge", "Flin Flon"],
            "wsa_monitored": True,
            "notes_en": "Northern boreal watershed; connects numerous lakes across northern SK",
            "notes_fr": "Bassin versant boréal nordique; relie de nombreux lacs dans le nord de la SK",
        },
        {
            "name_en": "Athabasca",
            "name_fr": "Athabasca",
            "basin_filter": "Athabasca",
            "major_river_en": "Athabasca River headwaters (far northwest Saskatchewan)",
            "major_river_fr": "Sources de la rivière Athabasca (extrême nord-ouest de la Saskatchewan)",
            "key_cities": ["Buffalo Narrows", "Uranium City"],
            "wsa_monitored": True,
            "notes_en": "Small portion in SK; mostly flows through Alberta to Lake Athabasca",
            "notes_fr": "Petite portion en SK; coule surtout à travers l'Alberta vers le lac Athabasca",
        },
    ]
    return json.dumps(
        {
            "basins": basins,
            "_meta": {
                "count": len(basins),
                "description_en": (
                    "Saskatchewan's major river basins. Use basin_filter value as the basin= "
                    "parameter in saskatchewan_get_wsa_stations to filter hydrometric stations. "
                    "WSA (Water Security Agency) operates monitoring stations across all 6 basins."
                ),
                "description_fr": (
                    "Les principaux bassins fluviaux de la Saskatchewan. Utilisez la valeur basin_filter "
                    "comme paramètre basin= dans saskatchewan_get_wsa_stations pour filtrer les stations "
                    "hydrométriques. La WSA opère des stations de surveillance dans les 6 bassins."
                ),
                "wsa_tool": "saskatchewan_get_wsa_stations",
                "reservoir_tool": "saskatchewan_get_wsa_reservoirs",
                "wsa_org_en": "WSA uses separate ArcGIS org: services1.arcgis.com/7MBdlVpjqbfBhQer",
                "wsa_org_fr": "La WSA utilise un org ArcGIS séparé : services1.arcgis.com/7MBdlVpjqbfBhQer",
            },
        },
        indent=2,
        ensure_ascii=False,
    )


@resource(
    "data://saskatchewan/health-regions",
    mime_type="application/json",
    name="saskatchewan_health_regions",
    title="Saskatchewan Health Authority (SHA) — Single Province-Wide Authority Since 2017",
)
async def saskatchewan_health_regions() -> str:
    """JSON entry for Saskatchewan's single health authority (SHA), formed 2017.

    Saskatchewan merged all 12 Regional Health Authorities into one province-wide
    Saskatchewan Health Authority (SHA) in 2017. NOTE: The health domain is deferred
    in this module — no public SHA facility FeatureServer was found in any Saskatchewan
    ArcGIS Hub org. The eHealth coverage stats FeatureServers found (enrollment counts
    by sex/region) do not provide facility location data useful to agents.
    See docs://saskatchewan/portal-guide for the deferral rationale.
    """
    health_authorities = [
        {
            "short_name": "SHA",
            "name_en": "Saskatchewan Health Authority",
            "name_fr": "Autorité sanitaire de la Saskatchewan",
            "coverage_en": "Province-wide (all of Saskatchewan) — formed 2017 from merger of 12 former RHAs",
            "coverage_fr": "À l'échelle provinciale (toute la Saskatchewan) — formée en 2017 de la fusion de 12 anciennes RSS",
            "formed": 2017,
            "predecessor_rhas_en": [
                "Sunrise Health Region", "Saskatoon Health Region", "Regina Qu'Appelle Health Region",
                "Cypress Health Region", "Five Hills Health Region", "Prairie North Health Region",
                "Heartland Health Region", "Keewatin Yatthé Regional Health Authority",
                "Mamawetan Churchill River Regional Health Authority",
                "Kelsey Trail Health Region", "Prince Albert Parkland Health Region",
                "Sun Country Health Region",
            ],
            "major_facilities_en": [
                "Royal University Hospital (Saskatoon)",
                "St. Paul's Hospital (Saskatoon)",
                "Pasqua Hospital (Regina)",
                "Regina General Hospital (Regina)",
                "Prince Albert Victoria Hospital",
            ],
            "major_facilities_fr": [
                "Hôpital universitaire Royal (Saskatoon)",
                "Hôpital St. Paul (Saskatoon)",
                "Hôpital Pasqua (Regina)",
                "Hôpital général de Regina (Regina)",
                "Hôpital Victoria de Prince Albert",
            ],
        },
    ]
    return json.dumps(
        {
            "health_authorities": health_authorities,
            "_meta": {
                "count": 1,
                "description_en": (
                    "Saskatchewan has ONE health authority (SHA) since 2017. "
                    "There are no former RHA subdivisions to filter by."
                ),
                "description_fr": (
                    "La Saskatchewan n'a QU'UNE autorité sanitaire (SHA) depuis 2017. "
                    "Il n'y a pas d'anciennes subdivisions RSS par lesquelles filtrer."
                ),
                "health_tools_note_en": (
                    "Health domain DEFERRED: No public SHA facility FeatureServer was found "
                    "in any Saskatchewan ArcGIS Hub org (zcv98lgAl8xQ04cW or 7MBdlVpjqbfBhQer). "
                    "eHealth coverage stats FeatureServers found (eHealth_Coverage_by_Sex, "
                    "eHealth_Coverage_By_Region_and_Community) provide enrollment counts, "
                    "not facility locations. Health tools are not available in this module. "
                    "See docs://saskatchewan/portal-guide for the full deferred-domains section."
                ),
                "health_tools_note_fr": (
                    "Domaine santé DIFFÉRÉ : Aucun FeatureServer public de l'ASS n'a été trouvé "
                    "dans aucun org ArcGIS Hub de la Saskatchewan (zcv98lgAl8xQ04cW ou 7MBdlVpjqbfBhQer). "
                    "Les FeatureServers de couverture eHealth trouvés (eHealth_Coverage_by_Sex, "
                    "eHealth_Coverage_By_Region_and_Community) fournissent des décomptes d'inscription, "
                    "pas des emplacements d'établissements. Les outils de santé ne sont pas "
                    "disponibles dans ce module. Consultez docs://saskatchewan/portal-guide "
                    "pour la section complète des domaines différés."
                ),
            },
        },
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Documentation guides (docs://) — markdown with both languages inline
# ---------------------------------------------------------------------------


@resource(
    "docs://saskatchewan/portal-guide",
    mime_type="text/markdown",
    name="saskatchewan_portal_guide",
    title="Saskatchewan Open Data Portal Guide — Multi-Org ArcGIS Architecture, Deferred Domains, GOS Licence",
)
async def saskatchewan_portal_guide() -> str:
    """Markdown guide on Saskatchewan's open data portals, multi-org ArcGIS architecture.

    Covers: geohub.saskatchewan.ca ArcGIS Hub multi-org architecture (primary org
    zcv98lgAl8xQ04cW + WSA org 7MBdlVpjqbfBhQer + SPSA egis), which tool to use
    for what, data.saskatchewan.ca-does-not-exist note, deferred transport (511
    key-gated) and health (no public SHA FeatureServer) domains, Petroleum
    FeatureServer HTTP 400 discovery-only routing, WSA_Reservoirs layer-26 quirk,
    and the GOS Standard Unrestricted Use Data Licence v2.0.
    """
    return """# Saskatchewan Open Data Portal Guide

## English

### Portal Architecture: Three Distinct Servers

Saskatchewan has the most fragmented portal architecture of any province in this module suite.
Data comes from **three separate ArcGIS servers** — choose the right curated tool:

| Server | URL | Tools | Org ID |
|--------|-----|-------|--------|
| **Saskatchewan GeoHub (primary)** | `geohub.saskatchewan.ca` | `saskatchewan_search_datasets`, `_get_dataset_details`, `_query_dataset`, `_list_organizations`, `_list_categories`, `_get_crop_yields`, `_get_grain_elevators`, `_get_mineral_mines`, `_get_historic_wildfires`, `_get_air_quality` | `zcv98lgAl8xQ04cW` |
| **WSA GeoHub** | `geohub-wsask.hub.arcgis.com` | `saskatchewan_get_wsa_stations`, `_get_wsa_reservoirs` | `7MBdlVpjqbfBhQer` |
| **SPSA GIS** | `gis.saskatchewan.ca/egis/` | `saskatchewan_get_fire_bans` | (non-Hub) |

### Primary Portal: geohub.saskatchewan.ca (ArcGIS Hub)

Saskatchewan's primary machine-readable open data portal is **geohub.saskatchewan.ca** —
an ArcGIS Hub powered by ArcGIS Online org `zcv98lgAl8xQ04cW` (181+ public items,
17+ FeatureServer services). Multiple ministry-branded sub-hubs exist but all resolve
to the same org:

- `moh-geohub-saskatchewan.hub.arcgis.com` — Ministry of Highways (NOT Ministry of Health)
- `environment-saskatchewan.hub.arcgis.com` — Environment (air quality, forest, parks)
- `er-saskatchewan.hub.arcgis.com` — Energy & Resources / Geological Survey (67 items)

**Use `geohub.saskatchewan.ca` as the single discovery entry point.** The ministry-branded
hubs are cosmetic wrappers over the same org.

### WSA GeoHub (Water Security Agency): Separate Org

The Water Security Agency (WSA) operates a **separate ArcGIS Hub** at
`geohub-wsask.hub.arcgis.com` (org `7MBdlVpjqbfBhQer`, 60 items). WSA tools
call `services1.arcgis.com/7MBdlVpjqbfBhQer/` — not the primary org base URL.

**WSA_Reservoirs layer-26 quirk:** The WSA_Reservoirs FeatureServer stores reservoir
data at **layer 26**, not layer 0. Queries to layer 0 return empty results with no error.
`saskatchewan_get_wsa_reservoirs` pins this automatically — do not override.

### SPSA GIS: Non-Hub ArcGIS REST Server

The Saskatchewan Public Safety Agency (SPSA) maintains a separate ArcGIS REST server at
`gis.saskatchewan.ca/egis/rest/services/Wildfire/`. Fire ban data is NOT discoverable
via `saskatchewan_search_datasets` Hub search — call `saskatchewan_get_fire_bans` directly.

**Layer routing:** `ban_scope` dispatches to specific layers:
- `'urban'` → layer 0 (urban municipalities)
- `'rural'` → layer 2 (rural improvement districts)
- `'provincial'` → layer 3 (province-wide restrictions)
- `'parks'` → layer 8 (provincial parks)

Empty result `{features:[]}` means **no active bans** — this is normal off-season. Not an error.

### data.saskatchewan.ca Does Not Exist

`data.saskatchewan.ca` is **unreachable** — Saskatchewan has no provincial CKAN portal.
Do NOT call `data.saskatchewan.ca/api/3/action/`. The provincial ArcGIS Hub
(`geohub.saskatchewan.ca`) is the canonical open data portal.

### Petroleum FeatureServer: Discovery Only (HTTP 400)

`gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0` (oil & gas wells)
returns **HTTP 400** on open queries (`where=1=1`). The schema is accessible but data
queries fail. This service is NOT curated with a dedicated tool.

**Routing for petroleum data:** Use `saskatchewan_search_datasets(query='petroleum')` for
discovery. The federal CKAN (`open.canada.ca`) also has Saskatchewan petroleum data
(413 datasets from org `sk`) pointing to the same ESRI REST endpoints.

### Deferred Domains

#### Transport (511) — Key-Gated, Fully Deferred

The Saskatchewan Highway Hotline API (`hotline.gov.sk.ca/api/v2/get/`) returns
`<Error><Message>Invalid Key</Message></Error>` for all keyless requests. A developer
key is required. **No transport tools are provided in this module — no NOT_CONFIGURED stubs.**

Available endpoints when a key is obtained: `roadconditions`, `cameras`, `events`,
`winterroads`, `ferryterminals`, `iceroadsegments`, `advisories`, `trackmyplow`.
Rate limit: 10 calls per 60 seconds. See `hotline.gov.sk.ca/developers/doc`.

#### Health — No Public SHA FeatureServer Found

The Saskatchewan Health Authority (SHA, province-wide since 2017 merger of 12 RHAs)
does not appear to have a public-facing facility FeatureServer in the `zcv98lgAl8xQ04cW` org.

FeatureServers found but NOT curated (no agent value for facility lookup):
- `eHealth_Coverage_by_Sex/FeatureServer` — enrollment counts by year/sex (not facility locations)
- `eHealth_Coverage_By_Region_and_Community/FeatureServer` — coverage by community (not facilities)

**No health tools are provided.** See `data://saskatchewan/health-regions` for SHA context.

### GOS Standard Unrestricted Use Data Licence v2.0

Saskatchewan government data is released under the **GOS Standard Unrestricted Use
Data Licence v2.0**:

- **Permitted:** Reproduction, distribution, adaptation, commercial use, non-commercial use
- **Required:** Attribution statement + accurate representation of data
- **Contact:** `egis@gov.sk.ca` for licence queries
- **Agent use:** CONFIRMED permitted under "unrestricted use" — building AI applications
  is an explicitly allowed use case

---

## Français

### Architecture du portail : Trois serveurs distincts

La Saskatchewan possède l'architecture de portail la plus fragmentée de toutes les
provinces dans cette suite de modules. Les données proviennent de **trois serveurs
ArcGIS distincts** — choisissez le bon outil curé :

| Serveur | URL | Outils | ID Org |
|---------|-----|--------|--------|
| **GeoHub Saskatchewan (principal)** | `geohub.saskatchewan.ca` | `saskatchewan_search_datasets` et autres outils de découverte, `_get_crop_yields`, `_get_grain_elevators`, `_get_mineral_mines`, `_get_historic_wildfires`, `_get_air_quality` | `zcv98lgAl8xQ04cW` |
| **GeoHub WSA** | `geohub-wsask.hub.arcgis.com` | `saskatchewan_get_wsa_stations`, `_get_wsa_reservoirs` | `7MBdlVpjqbfBhQer` |
| **GIS SPSA** | `gis.saskatchewan.ca/egis/` | `saskatchewan_get_fire_bans` | (non-Hub) |

### data.saskatchewan.ca n'existe pas

`data.saskatchewan.ca` est **inaccessible** — la Saskatchewan n'a pas de portail CKAN provincial.
N'appelez PAS `data.saskatchewan.ca/api/3/action/`. Le GeoHub ArcGIS provincial
(`geohub.saskatchewan.ca`) est le portail de données ouvertes canonique.

### Domaines différés

#### Transport (511) — Clé requise, entièrement différé

L'API Saskatchewan Highway Hotline (`hotline.gov.sk.ca/api/v2/get/`) retourne
`<Error><Message>Invalid Key</Message></Error>` pour toutes les requêtes sans clé.
**Aucun outil de transport n'est fourni dans ce module — pas de stubs NOT_CONFIGURED.**

#### Santé — Aucun FeatureServer SHA public trouvé

L'Autorité sanitaire de la Saskatchewan (SHA, provinciale depuis la fusion de 2017)
n'a pas de FeatureServer d'établissements public dans l'org `zcv98lgAl8xQ04cW`.
**Aucun outil de santé n'est fourni.** Consultez `data://saskatchewan/health-regions`.

### Licence d'utilisation des données sans restriction standard GOS v2.0

Les données du gouvernement de la Saskatchewan sont publiées sous la **Licence
d'utilisation des données sans restriction standard GOS v2.0** :

- **Permis :** Reproduction, distribution, adaptation, usage commercial et non commercial
- **Obligatoire :** Déclaration d'attribution + représentation exacte des données
- **Contact :** `egis@gov.sk.ca` pour les questions de licence
"""


@resource(
    "docs://saskatchewan/agriculture-data-guide",
    mime_type="text/markdown",
    name="saskatchewan_agriculture_data_guide",
    title="Saskatchewan Agriculture Data Guide — Crop Yields, Grain Elevators, Mineral Mines",
)
async def saskatchewan_agriculture_data_guide() -> str:
    """Markdown guide on Saskatchewan agriculture and mining data sources and tool mapping.

    Covers: crop yield estimates (bu/acre) from FeatureServers vs PDF-only weekly crop
    reports; Crop_Production_2025 boundary-only caveat; grain elevator PR='SK' filtering
    (Western Canada dataset, CN/CP/SHORTLINE dispatch); mineral mine dispatch by type
    (potash/uranium/helium/coal to dated FeatureServers); Petroleum FeatureServer HTTP 400.
    """
    return """# Saskatchewan Agriculture & Resource Data Guide

## English

### Crop Yield Data

#### Machine-Readable Source: FeatureServers (Annual Estimates)

Saskatchewan crop yield estimates come from **two FeatureServers** on the primary GeoHub org
(`zcv98lgAl8xQ04cW`):

| Tool parameter | FeatureServer | Records |
|----------------|---------------|---------|
| `region='provincial'` | `Provincial_Estimated_Crop_Yields_Province_Summary/FeatureServer/0` | Combined provincial summary |
| Any of the 5 regions | `Provincial_Estimated_Crop_Yields_Regions_Only/FeatureServer/0` | 5 regional breakdowns |

**Tool:** `saskatchewan_get_crop_yields(region='...')`

**16 crop types:** HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean, Pea, Lentil,
Chickpea, Canary_seed, Flax, Winter_wheat, Fall_rye, Other_wheat_. All in **bu/acre**.

#### PDF-Only: Weekly Crop Reports (NOT Machine-Readable)

Weekly crop reports published by Saskatchewan Agriculture (`saskatchewan.ca/business/agriculture/`)
are **PDF and HTML only**. There is no JSON/CSV download endpoint. Do NOT attempt to fetch
these programmatically — the FeatureServer above is the machine-readable substitute.

#### Crop_Production_2025: Boundary-Only (No Crop Data)

The `Crop_Production_2025/FeatureServer/0` layer exists but contains **spatial boundaries only**:
- `CDNAME` (Census Division Name)
- `LANDAREAIN` (land area in km²)
- `Census_Div` (division number)

There are **no crop yield, production, or statistics attributes** in this layer. It is a
base map for crop production maps, not a data table. Use `Provincial_Estimated_Crop_Yields_*`
FeatureServers for actual yield data.

### Grain Elevator Data

**Tool:** `saskatchewan_get_grain_elevators(railway='...')`

The `Western_Canada_Grain_Elevator_2024/FeatureServer/0` covers all of Western Canada.
Saskatchewan elevators are selected with `where=PR='SK'` (applied by default).

| Field | Values |
|-------|--------|
| `Railway` | `CN`, `CP`, `SHORTLINE` |
| `Elevator_type` | `Primary`, `Process` |
| `Capacity_tonne` | tonnes of storage capacity |

Optional `railway=` filter: `'CN'`, `'CP'`, or `'SHORTLINE'`.

**Note:** Dataset is dated 2024 — elevator inventories may have changed since publication.

### Mineral Mines Data

**Tool:** `saskatchewan_get_mineral_mines(mineral='...')`

Dispatches to dated FeatureServers (all on org `zcv98lgAl8xQ04cW`):

| mineral= value | FeatureServer | Notes |
|----------------|---------------|-------|
| `'potash'` | `Potash_2024_06_13/FeatureServer/0` | 13 active mines, world's largest reserve |
| `'uranium'` | `Uranium_2024_06_13/FeatureServer/0` | Athabasca Basin, Cameco operations |
| `'helium'` | `Helium_2024_12_31/FeatureServer/0` | Emerging sector in SK |
| `'coal'` | `Coal_2024_06_13/FeatureServer/0` | Historical and active surface mines |

**Fields returned:** Commodity, Name, Status, Mine_Type, Company, Mine_Site,
Regulation, DateOpened, Website.

**Status values:** Operating, Care & Maintenance, Closed, Permitted.

### Oil & Gas Wells (Petroleum): Discovery Only

`gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0` (oil & gas wells)
returns **HTTP 400** on open queries. Schema is visible but data is not queryable.

**Workaround:** Use `saskatchewan_search_datasets(query='petroleum wells')` for discovery.
Saskatchewan is Canada's 3rd largest oil producer; federal CKAN also has 413 Saskatchewan
geospatial datasets at `open.canada.ca` (org=`sk`).

---

## Français

### Données de rendement des cultures

Les estimations de rendement des cultures de la Saskatchewan proviennent de **deux FeatureServers**
sur l'org GeoHub principal (`zcv98lgAl8xQ04cW`). Utilisez `region='provincial'` (défaut) pour
le résumé provincial, ou l'un des 5 identifiants de région pour les données régionales.

**Outil :** `saskatchewan_get_crop_yields(region='...')`

**Rapports hebdomadaires de culture** (Saskatchewan Agriculture) : Format PDF et HTML uniquement.
Pas de téléchargement JSON/CSV. N'essayez pas de les récupérer par programmation.

**Crop_Production_2025 :** Limites spatiales uniquement (CDNAME, LANDAREAIN, Census_Div).
Aucune donnée de rendement. Utilisez les FS `Provincial_Estimated_Crop_Yields_*` à la place.

### Données sur les élévateurs à grain

**Outil :** `saskatchewan_get_grain_elevators(railway='...')`

Filtre `where=PR='SK'` appliqué par défaut (dataset Western Canada). Filtre optionnel
railway= : `'CN'`, `'CP'`, ou `'SHORTLINE'`.

### Données sur les mines de minéraux

**Outil :** `saskatchewan_get_mineral_mines(mineral='...')`

Dispatch vers les FeatureServers datés (org `zcv98lgAl8xQ04cW`) :
- `'potash'` — 13 mines actives, plus grandes réserves mondiales
- `'uranium'` — Bassin d'Athabasca, opérations Cameco
- `'helium'` — Secteur émergent en Saskatchewan
- `'coal'` — Mines historiques et actives à ciel ouvert
"""


# ---------------------------------------------------------------------------
# Templates (template://) — markdown with {placeholder} syntax
# ---------------------------------------------------------------------------


@resource(
    "template://saskatchewan/dataset-report",
    mime_type="text/markdown",
    name="saskatchewan_dataset_report_template",
    title="Saskatchewan Dataset Exploration Report Template",
)
async def saskatchewan_dataset_report_template() -> str:
    """Markdown template for reporting Saskatchewan GeoHub dataset exploration findings.

    Fill in placeholders with actual values from saskatchewan_search_datasets,
    saskatchewan_get_dataset_details, and saskatchewan_query_dataset calls.
    """
    return """# Saskatchewan Dataset Exploration Report

**Date:** {report_date}
**Dataset searched:** {search_query}
**Category filter:** {category_filter}
**Portal:** geohub.saskatchewan.ca (ArcGIS Hub, org zcv98lgAl8xQ04cW)

## Search Results Summary

- **Total datasets found:** {total_count}
- **Results returned:** {results_count}
- **Data types found:** {data_types}

## Dataset Spotlight

**Dataset ID (GUID):** {dataset_id}
**Title:** {dataset_title}
**Publisher:** {publisher_name}
**License:** GOS Standard Unrestricted Use Data Licence v2.0
**Last modified:** {last_modified}
**Number of resources:** {num_resources}

### Best Resource

- **Type:** {resource_type}
- **URL:** {resource_url}
- **Routing path:** {routing_path}

## Sample Data (first {sample_count} records)

{sample_data_table}

## Notes

- **Portal:** geohub.saskatchewan.ca uses ArcGIS Hub Search API (NOT CKAN)
- **data.saskatchewan.ca does NOT exist** — the Hub is the only provincial portal
- **Authentication:** None required — public access
- **Licence:** GOS Standard Unrestricted Use Data Licence v2.0 (contact: egis@gov.sk.ca)
- **WSA note:** Water data (stations, reservoirs) lives on separate org 7MBdlVpjqbfBhQer
- **SPSA note:** Fire ban data is NOT discoverable via Hub search — use curated tools
- **Auto-router:** `saskatchewan_query_dataset` prefers FeatureServer over file resources

## Next Steps

- [ ] Refine with `saskatchewan_search_datasets(query='{related_keyword}')`
- [ ] Check dataset details via `saskatchewan_get_dataset_details(dataset_id='{dataset_id}')`
- [ ] Filter by category: `category='{category_filter}'`
- [ ] See `data://saskatchewan/crop-regions` for crop reporting region names
- [ ] See `docs://saskatchewan/portal-guide` for multi-org architecture
"""


@resource(
    "template://saskatchewan/wildfire-report",
    mime_type="text/markdown",
    name="saskatchewan_wildfire_report_template",
    title="Saskatchewan Wildfire and Air Quality Situational Report Template",
)
async def saskatchewan_wildfire_report_template() -> str:
    """Markdown template for reporting Saskatchewan wildfire and air quality situational data.

    Fill in placeholders with actual values from saskatchewan_get_fire_bans,
    saskatchewan_get_historic_wildfires, and saskatchewan_get_air_quality calls.
    """
    return """# Saskatchewan Wildfire & Air Quality Situational Report — {report_date}

**Sources:**
- Fire bans: SPSA Public_Fire_Ban FeatureServer (gis.saskatchewan.ca/egis) — TTL 5 min
- Historic wildfires: GeoHub Historic_Wildfire_Boundaries FeatureServer — TTL 24 h
- Air quality: GeoHub Hourly_Ambient_Air_Quality FeatureServer — TTL 15 min

## Fire Ban Status

| Scope | Active Bans | Affected Areas |
|-------|-------------|----------------|
| Urban (layer 0) | {urban_ban_count} | {urban_ban_areas} |
| Rural (layer 2) | {rural_ban_count} | {rural_ban_areas} |
| Provincial (layer 3) | {provincial_ban_count} | {provincial_ban_desc} |
| Parks (layer 8) | {parks_ban_count} | {parks_ban_areas} |

**Note:** Empty result (0 bans) is normal off-season — no active restrictions.

## Historic Wildfires Summary ({wildfire_year})

- **Year queried:** {wildfire_year}
- **Total fires in dataset:** {total_fires}
- **Cause breakdown:** Lightning: {lightning_count} / Human: {human_count} / Unknown: {unknown_count}
- **Total area burned:** {total_hectares} hectares
- **Largest fire:** {largest_fire_name} ({largest_fire_ha} ha)

## Air Quality Readings (current hourly)

| Community | PM2.5 | NO2 | O3 | AQHI link |
|-----------|-------|-----|----|-----------|
| {community_1} | {pm25_1} | {no2_1} | {o3_1} | {aqhi_url_1} |
| {community_2} | {pm25_2} | {no2_2} | {o3_2} | {aqhi_url_2} |
| {community_3} | {pm25_3} | {no2_3} | {o3_3} | {aqhi_url_3} |

**Monitored communities:** Regina, Saskatoon, Prince Albert, Estevan, Swift Current, Buffalo Narrows

## Wildfire Risk Context

- **Fire season:** Typically May–September in Saskatchewan
- **Primary cause:** Lightning accounts for majority of large fires in northern SK
- **SPSA mandate:** Saskatchewan Public Safety Agency manages provincial fire bans
- **AQHI note:** Air Quality Health Index values link to weather.gc.ca — not a direct numeric

## Data Freshness

- **Fire bans queried:** {bans_query_ts}
- **Historic wildfires queried:** {wildfires_query_ts}
- **Air quality queried:** {air_quality_query_ts}
"""
