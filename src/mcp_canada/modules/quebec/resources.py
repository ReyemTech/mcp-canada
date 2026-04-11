"""Quebec resources — 7 zero-parameter static resources for Quebec data exploration.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even lang) would make
FastMCP treat them as ResourceTemplate instead of FunctionResource, removing them from
resources/list. Bilingual content is embedded inline.

Catalog resources (data://):
  data://quebec/ministries   — provincial ministries with bilingual labels + CKAN org slugs
  data://quebec/regions      — 17 administrative regions with bilingual labels + codes
  data://quebec/mrcs         — regional county municipalities (MRC) list

Documentation guides (docs://):
  docs://quebec/catalog-federation-quirks  — 139-org federated nature + Montreal overlap
  docs://quebec/bilingual-metadata-guide   — French-primary DQ metadata explained

Templates (template://):
  template://quebec/dataset-report        — dataset exploration report template
  template://quebec/road-conditions-report — road conditions analysis report template
"""

import json

from fastmcp.resources import resource


__all__ = [
    "quebec_ministries",
    "quebec_regions",
    "quebec_mrcs",
    "quebec_catalog_federation_quirks",
    "quebec_bilingual_metadata_guide",
    "quebec_dataset_report_template",
    "quebec_road_conditions_report_template",
]


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://quebec/ministries",
    mime_type="application/json",
    name="quebec_ministries",
    title="Quebec Provincial Ministry and Agency Catalog with CKAN Organization Slugs",
)
async def quebec_ministries() -> str:
    """JSON catalog of Quebec provincial ministries and agencies with their Données Québec CKAN slugs.

    Use slug values in quebec_search_datasets organization= parameter to filter datasets
    by a specific Quebec ministry or agency. Includes bilingual name and description.
    """
    return json.dumps(
        [
            {
                "slug": "msss",
                "name_en": "Ministry of Health and Social Services",
                "name_fr": "Ministère de la Santé et des Services sociaux",
                "description_en": "Health installations, ER wait times, hospital network",
                "description_fr": "Installations de santé, temps d'attente aux urgences, réseau hospitalier",
            },
            {
                "slug": "mtq",
                "name_en": "Ministry of Transport of Quebec",
                "name_fr": "Ministère des Transports du Québec",
                "description_en": "Road conditions, construction zones, bridge inventory, transport data",
                "description_fr": "Conditions routières, chantiers, inventaire des ponts, données de transport",
            },
            {
                "slug": "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques",
                "name_en": "Ministry of the Environment and the Fight Against Climate Change (MELCCFP)",
                "name_fr": "Ministère de l'Environnement et de la Lutte contre les changements climatiques, de la Faune et des Parcs",
                "description_en": "Air quality (RSQAQ), water quality monitoring, protected areas registry",
                "description_fr": "Qualité de l'air (RSQAQ), surveillance qualité eau, registre aires protégées",
            },
            {
                "slug": "mrn",
                "name_en": "Ministry of Natural Resources and Forests (MFFP/MRN)",
                "name_fr": "Ministère des Ressources naturelles et des Forêts",
                "description_en": "Forest fire perimeter archive, forestry data, territorial mapping",
                "description_fr": "Archive périmètres feux de forêt, données forestières, cartographie territoriale",
            },
            {
                "slug": "hydro-quebec",
                "name_en": "Hydro-Québec",
                "name_fr": "Hydro-Québec",
                "description_en": "Historical electricity production and consumption statistics",
                "description_fr": "Statistiques historiques de production et consommation électrique",
            },
            {
                "slug": "affaires-municipales-et-occupation-du-territoire",
                "name_en": "Ministry of Municipal Affairs and Housing (MAMH)",
                "name_fr": "Ministère des Affaires municipales et de l'Habitation",
                "description_en": "Municipal registry, population data, land use, territorial planning",
                "description_fr": "Répertoire des municipalités, données de population, occupation du territoire",
            },
            {
                "slug": "isq",
                "name_en": "Institut de la statistique du Québec (ISQ)",
                "name_fr": "Institut de la statistique du Québec",
                "description_en": "Provincial statistics, demographic projections, economic indicators",
                "description_fr": "Statistiques provinciales, projections démographiques, indicateurs économiques",
            },
            {
                "slug": "msp",
                "name_en": "Ministry of Public Security (MSP)",
                "name_fr": "Ministère de la Sécurité publique",
                "description_en": "Public safety data, emergency measures, crime statistics",
                "description_fr": "Données de sécurité publique, mesures d'urgence, statistiques criminelles",
            },
            {
                "slug": "sepaq",
                "name_en": "Société des établissements de plein air du Québec (Sépaq)",
                "name_fr": "Société des établissements de plein air du Québec",
                "description_en": "Provincial park network, wildlife reserves, outdoor recreation data",
                "description_fr": "Réseau de parcs provinciaux, réserves fauniques, données loisirs plein air",
            },
        ]
    )


@resource(
    "data://quebec/regions",
    mime_type="application/json",
    name="quebec_regions",
    title="Quebec 17 Administrative Regions with Bilingual Labels and Codes",
)
async def quebec_regions() -> str:
    """JSON catalog of Quebec's 17 administrative regions with codes and bilingual names.

    Use region codes (e.g. '06' for Montreal) as the `region` parameter in
    quebec_get_population_by_municipality. Codes match the `regadm` field in MAMH data.
    """
    return json.dumps(
        [
            {"code": "01", "name_fr": "Bas-Saint-Laurent", "name_en": "Lower St. Lawrence", "slug": "bas-saint-laurent"},
            {"code": "02", "name_fr": "Saguenay-Lac-Saint-Jean", "name_en": "Saguenay-Lac-Saint-Jean", "slug": "saguenay-lac-saint-jean"},
            {"code": "03", "name_fr": "Capitale-Nationale", "name_en": "National Capital Region", "slug": "capitale-nationale"},
            {"code": "04", "name_fr": "Mauricie", "name_en": "Mauricie", "slug": "mauricie"},
            {"code": "05", "name_fr": "Estrie", "name_en": "Eastern Townships", "slug": "estrie"},
            {"code": "06", "name_fr": "Montréal", "name_en": "Montreal", "slug": "montreal"},
            {"code": "07", "name_fr": "Outaouais", "name_en": "Outaouais", "slug": "outaouais"},
            {"code": "08", "name_fr": "Abitibi-Témiscamingue", "name_en": "Abitibi-Témiscamingue", "slug": "abitibi-temiscamingue"},
            {"code": "09", "name_fr": "Côte-Nord", "name_en": "North Shore", "slug": "cote-nord"},
            {"code": "10", "name_fr": "Nord-du-Québec", "name_en": "Northern Quebec", "slug": "nord-du-quebec"},
            {"code": "11", "name_fr": "Gaspésie-Îles-de-la-Madeleine", "name_en": "Gaspésie-Îles-de-la-Madeleine", "slug": "gaspesie-iles-de-la-madeleine"},
            {"code": "12", "name_fr": "Chaudière-Appalaches", "name_en": "Chaudière-Appalaches", "slug": "chaudiere-appalaches"},
            {"code": "13", "name_fr": "Laval", "name_en": "Laval", "slug": "laval"},
            {"code": "14", "name_fr": "Lanaudière", "name_en": "Lanaudière", "slug": "lanaudiere"},
            {"code": "15", "name_fr": "Laurentides", "name_en": "Laurentians", "slug": "laurentides"},
            {"code": "16", "name_fr": "Montérégie", "name_en": "Montérégie", "slug": "monteregie"},
            {"code": "17", "name_fr": "Centre-du-Québec", "name_en": "Centre-du-Québec", "slug": "centre-du-quebec"},
        ]
    )


@resource(
    "data://quebec/mrcs",
    mime_type="application/json",
    name="quebec_mrcs",
    title="Quebec Regional County Municipalities (MRCs) Catalog",
)
async def quebec_mrcs() -> str:
    """JSON catalog of Quebec's major Regional County Municipalities (MRCs) with region codes.

    MRC (Municipalité régionale de comté) is the sub-regional administrative unit between
    the province and individual municipalities. Use as reference for filtering MAMH data.
    This catalog includes the major MRCs — the full list has 104 MRCs plus 14 agglomerations.
    """
    return json.dumps(
        [
            {"name": "Montréal (agglomération)", "region_code": "06", "region_fr": "Montréal"},
            {"name": "Québec (agglomération)", "region_code": "03", "region_fr": "Capitale-Nationale"},
            {"name": "Laval", "region_code": "13", "region_fr": "Laval"},
            {"name": "Longueuil (agglomération)", "region_code": "16", "region_fr": "Montérégie"},
            {"name": "Gatineau", "region_code": "07", "region_fr": "Outaouais"},
            {"name": "La Vallée-du-Richelieu", "region_code": "16", "region_fr": "Montérégie"},
            {"name": "Roussillon", "region_code": "16", "region_fr": "Montérégie"},
            {"name": "Les Maskoutains", "region_code": "16", "region_fr": "Montérégie"},
            {"name": "Sherbrooke (agglomération)", "region_code": "05", "region_fr": "Estrie"},
            {"name": "Memphrémagog", "region_code": "05", "region_fr": "Estrie"},
            {"name": "Le Fjord-du-Saguenay", "region_code": "02", "region_fr": "Saguenay-Lac-Saint-Jean"},
            {"name": "Lac-Saint-Jean-Est", "region_code": "02", "region_fr": "Saguenay-Lac-Saint-Jean"},
            {"name": "La Côte-de-Beaupré", "region_code": "03", "region_fr": "Capitale-Nationale"},
            {"name": "L'Île-d'Orléans", "region_code": "03", "region_fr": "Capitale-Nationale"},
            {"name": "Shawinigan", "region_code": "04", "region_fr": "Mauricie"},
            {"name": "Trois-Rivières", "region_code": "04", "region_fr": "Mauricie"},
            {"name": "La Matanie", "region_code": "01", "region_fr": "Bas-Saint-Laurent"},
            {"name": "Rimouski-Neigette", "region_code": "01", "region_fr": "Bas-Saint-Laurent"},
            {"name": "Abitibi", "region_code": "08", "region_fr": "Abitibi-Témiscamingue"},
            {"name": "Rouyn-Noranda", "region_code": "08", "region_fr": "Abitibi-Témiscamingue"},
            {"name": "Sept-Rivières", "region_code": "09", "region_fr": "Côte-Nord"},
            {"name": "Manicouagan", "region_code": "09", "region_fr": "Côte-Nord"},
            {"name": "La Haute-Gaspésie", "region_code": "11", "region_fr": "Gaspésie-Îles-de-la-Madeleine"},
            {"name": "Les Îles-de-la-Madeleine", "region_code": "11", "region_fr": "Gaspésie-Îles-de-la-Madeleine"},
            {"name": "Les Chutes-de-la-Chaudière", "region_code": "12", "region_fr": "Chaudière-Appalaches"},
            {"name": "Lévis", "region_code": "12", "region_fr": "Chaudière-Appalaches"},
            {"name": "Les Laurentides", "region_code": "15", "region_fr": "Laurentides"},
            {"name": "Thérèse-De Blainville", "region_code": "15", "region_fr": "Laurentides"},
            {"name": "L'Assomption", "region_code": "14", "region_fr": "Lanaudière"},
            {"name": "Joliette", "region_code": "14", "region_fr": "Lanaudière"},
            {"name": "Arthabaska", "region_code": "17", "region_fr": "Centre-du-Québec"},
            {"name": "Drummond", "region_code": "17", "region_fr": "Centre-du-Québec"},
        ]
    )


# ---------------------------------------------------------------------------
# Documentation guides (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://quebec/catalog-federation-quirks",
    mime_type="text/markdown",
    name="quebec_catalog_federation_quirks",
    title="Données Québec Catalog Federation Quirks — 139 Organizations, Montreal Overlap",
)
async def quebec_catalog_federation_quirks() -> str:
    """Markdown guide explaining the federated nature of Données Québec and common agent pitfalls.

    Covers: 139-org federated catalog, Montreal data overlap, parastatal entities,
    French-primary metadata, thematic groups vs tag_list, and tool scoping advice.
    """
    return """# Données Québec Catalog Federation Quirks

## The Federated Nature

Données Québec (`donneesquebec.ca`) is a **federated CKAN instance** with ~1,593 datasets
published by **139 organizations**. This is NOT just the provincial government — the catalog
includes:

- **Provincial ministries** (MSSS, MTQ, MELCCFP, MRN, MAMH, etc.)
- **Parastatal entities** (Hydro-Québec, BIXI Montréal, ARTM transit authority)
- **Municipal governments** (Ville de Montréal, Laval, Longueuil, Gatineau)
- **Academic and NGO publishers** (INSPQ, university research groups)

### Implication for Agents

When you call `quebec_search_datasets` without an `organization` filter, results will include
**all 139 organizations** — including Montreal BIXI transit routes, ARTM public transit data,
and parastatal entities. This is by design.

## Montreal Data Overlap

Montreal data appears in **two separate modules**:
- **Phase 16 (this module):** Montreal data published to Données Québec via Ville de Montréal
  organization (e.g. BIXI, some infrastructure datasets)
- **Phase 27 (future):** Montreal's own open data portal (`donnees.montreal.ca`) will be covered
  comprehensively in the future Montreal module

Use `organization='ville-de-montreal'` to filter DQ results to Montreal-published data.
For comprehensive Montreal data, a future Phase 27 module is planned.

## French-Primary Metadata

All dataset `title` and `notes` fields in Données Québec are **French only**. There is no
`title_translated`, `title_en`, or `title_fr` field (unlike BC CKAN which has some).

The `lang` parameter on `quebec_` tools affects **error messages only** — catalog metadata
is always returned as-is in French.

## Thematic Groups (Use Groups, Not Tags)

Données Québec has **10 thematic groups** accessible via `quebec_list_categories`:
- `sante` — Santé
- `environnement` — Environnement, ressources naturelles et énergie
- `infrastructures` — Infrastructures
- `gouvernement-finances` — Gouvernement et finances
- `economie` — Économie et emploi
- `education` — Éducation et science
- `loi-justice-securite` — Loi, justice et sécurité
- `politiques-sociales` — Politiques sociales et immigration
- `societe-culture` — Société et culture
- `agriculture` — Agriculture et alimentation

**Do NOT use `tag_list`** — it returns 4,200+ noisy tags with no hierarchy.
Always use `group_list` (exposed as `quebec_list_categories`).

## SOPFEU Wildfire Data Not Available

SOPFEU (wildfire prevention society) is **NOT registered** on Données Québec. Active fire data
requires visiting `sopfeu.qc.ca` directly. Historical fire perimeter archives (SHP/GPKG) are
available via `quebec_get_forest_fires_history` (MFFP/MRN published data).

## Hydro-Québec Outages Not Available

Hydro-Québec outage data is **NOT on Données Québec**. DQ has Hydro-Québec's historical
production/consumption statistics only. For current outages, visit `hydroquebec.com/pannes/`.
"""


@resource(
    "docs://quebec/bilingual-metadata-guide",
    mime_type="text/markdown",
    name="quebec_bilingual_metadata_guide",
    title="Données Québec Bilingual Metadata Guide — French-Primary Metadata Explained",
)
async def quebec_bilingual_metadata_guide() -> str:
    """Markdown guide explaining the French-primary metadata structure of Données Québec.

    Covers: French-only title/notes fields, update_frequency French values,
    how lang parameter affects tools, and bilingual strategies for agents.
    """
    return """# Données Québec Bilingual Metadata Guide

## French-Primary Metadata

Unlike the federal CKAN portal (`open.canada.ca`) or BC Data Catalogue which provide both
French and English metadata, **Données Québec is French-primary**: all dataset titles,
descriptions, and organization names are in French only.

### Field Reference

| Field | Shape | English Available? |
|-------|-------|--------------------|
| `title` | Plain French string | ❌ No |
| `notes` | French markdown/text | ❌ No |
| `organization.title` | French org name | ❌ No |
| `update_frequency` | French value (see below) | ❌ No |
| `groups[].display_name` | French group name | ❌ No |

### update_frequency Values (French)

| French value | Meaning |
|-------------|---------|
| `horaire` | Hourly |
| `continu` | Continuous |
| `quotidien` | Daily |
| `hebdomadaire` | Weekly |
| `mensuel` | Monthly |
| `semiannuel` | Semi-annual |
| `annuel` | Annual |
| `asNeeded` | As needed |

## How the `lang` Parameter Works

The `lang: Literal["en", "fr"]` parameter on Quebec tools affects:

1. **Error messages** — INVALID_INPUT, UPSTREAM_ERROR, NOT_FOUND messages are bilingual
2. **Bilingual data columns** — MTQ WFS CSV files have separate EN/FR columns that are
   selected by `lang` (e.g. `descriptionFrancais`/`descriptionAnglais` in road works)

The `lang` parameter does **NOT** affect:
- Dataset `title` or `notes` (always French)
- Organization names (always French)
- RSQAQ station names, MSSS installation names (always French)

## Bilingual Strategies for Agents

When presenting Quebec data to English-speaking users:

1. **For dataset titles:** Return as-is (French) and note "Données Québec titles are in French"
2. **For road works/conditions:** Use `lang='en'` to get English description columns in MTQ data
3. **For MSSS data:** Installation and establishment names are French proper nouns — keep as-is
4. **For population data:** Municipality names are French — keep as-is (e.g. "Montréal", "Québec")

## MTQ WFS CSV Bilingual Columns

Road construction zones (`quebec_get_road_works`) and road conditions
(`quebec_get_road_conditions`) have bilingual columns:

- `descriptionFrancais` / `descriptionAnglais` — road works description (selected by lang)
- `DescriptionEtatChausseeFR` / `DescriptionEtatChausseeEN` — pavement status
- `DescriptionVisibiliteFR` / `DescriptionVisibiliteEN` — visibility status

Road events (`quebec_get_road_events`) have **French-only columns** — no English equivalent.
"""


# ---------------------------------------------------------------------------
# Templates (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://quebec/dataset-report",
    mime_type="text/markdown",
    name="quebec_dataset_report",
    title="Quebec Dataset Exploration Report Template",
)
async def quebec_dataset_report_template() -> str:
    """Markdown template for reporting Quebec dataset exploration findings.

    Fill in placeholders with actual values from quebec_search_datasets,
    quebec_get_dataset_details, and quebec_query_dataset calls.
    """
    return """# Quebec Dataset Exploration Report

**Date:** {date}
**Dataset searched:** {search_query}
**Organization filter:** {organization_filter}

## Search Results Summary

- **Total datasets found:** {total_count}
- **Results returned:** {results_count}
- **Group/theme:** {group_filter}

## Dataset Spotlight

**Dataset name (slug):** {dataset_slug}
**Title (French):** {dataset_title_fr}
**Organization:** {organization_name}
**Update frequency:** {update_frequency}
**License:** {license_id}

### Available Resources

| Resource Name | Format | Datastore Active? | URL |
|--------------|--------|-------------------|-----|
| {resource_name_1} | {format_1} | {datastore_1} | {url_1} |
| {resource_name_2} | {format_2} | {datastore_2} | {url_2} |

## Sample Data (first {sample_count} records)

{sample_data_table}

## Notes

- **Language note:** All Données Québec metadata is French-primary. Titles returned as-is.
- **Federated catalog:** Results may include municipal (Montréal, Laval) and parastatal data.
- **Data source:** Données Québec CKAN API (`donneesquebec.ca/recherche/api/3/action/`)

## Next Steps

- [ ] Explore related datasets with `quebec_search_datasets q='{related_keyword}'`
- [ ] Check datastore-active resources with `quebec_query_dataset`
- [ ] Filter by organization: `organization='{organization_slug}'`
"""


@resource(
    "template://quebec/road-conditions-report",
    mime_type="text/markdown",
    name="quebec_road_conditions_report",
    title="Quebec Road Conditions Analysis Report Template",
)
async def quebec_road_conditions_report_template() -> str:
    """Markdown template for reporting Quebec road conditions and transport data analysis.

    Fill in placeholders with actual values from quebec_get_road_conditions,
    quebec_get_road_works, and quebec_get_road_events calls.
    """
    return """# Quebec Road Conditions Report

**Date/Time:** {datetime}
**Data source:** MTQ live WFS CSV feeds (continuous updates)
**Season:** {season}

## Winter Road Conditions Summary

- **Total segments reported:** {segments_count}
- **Segments with poor pavement:** {poor_pavement_count}
- **Segments with reduced visibility:** {low_visibility_count}
- **Segments with snow presence:** {snow_presence_count}

### Most Affected Routes

| Route | Region | Pavement Status | Visibility | Snow |
|-------|--------|-----------------|------------|------|
| {route_1} | {region_1} | {pavement_1} | {visibility_1} | {snow_1} |
| {route_2} | {region_2} | {pavement_2} | {visibility_2} | {snow_2} |

## Active Construction Zones

- **Total active chantiers:** {works_count}
- **Critical closures (fermeture totale):** {total_closures}
- **Partial lane restrictions:** {partial_restrictions}

### Highlighted Construction Zones

| Route | Location | Type | Start | End | Description |
|-------|----------|------|-------|-----|-------------|
| {work_route_1} | {work_loc_1} | {work_type_1} | {work_start_1} | {work_end_1} | {work_desc_1} |

## Active Road Events (Accidents & Incidents)

- **Total active events:** {events_count}

### Significant Events

| Route | Municipality | Obstruction Type | Cause | Duration |
|-------|-------------|-----------------|-------|---------|
| {event_route_1} | {event_mun_1} | {event_obs_1} | {event_cause_1} | {event_dur_1} |

## Travel Advisory

{travel_advisory_text}

## Data Notes

- **MTQ winter conditions:** Variable reliability outside November-April season (may be empty in summer)
- **Road works:** Continuous WFS feed, ~5 min cache
- **Road events:** Continuous WFS feed, French-only columns
- **Timestamps:** All times are local Quebec time (EST/EDT)
"""
