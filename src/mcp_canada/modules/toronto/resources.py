"""MCP resources for the Toronto Municipal Open Data module.

Provides reference catalogs, documentation guides, and response templates for
the City of Toronto open data portal (open.toronto.ca). All resources use
type-prefixed URIs:
- data://toronto/...    — JSON reference catalogs (machine-parseable)
- docs://toronto/...    — Markdown documentation guides (human-readable)
- template://toronto/...— Markdown response templates with {placeholder} syntax

IMPORTANT: All resource functions are zero-parameter. Adding any parameter
(even lang) would make FastMCP treat them as ResourceTemplate instead of
FunctionResource, removing them from resources/list.
Bilingual content is embedded inline in a single resource.
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Catalog resources (data://)
# ---------------------------------------------------------------------------


@resource(
    "data://toronto/city-divisions",
    mime_type="application/json",
    name="toronto_city_divisions",
    title="City of Toronto Divisions and Agencies",
)
def toronto_city_divisions() -> str:
    """City of Toronto divisions (departments) that publish open data.

    Use these division names with toronto_search_datasets(organization=...)
    to filter datasets by city division.
    Format: {"slug": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps(
        {
            "toronto-transit-commission-ttc": {
                "en": "Toronto Transit Commission (TTC)",
                "fr": "Commission de transport en commun de Toronto (TTC)",
            },
            "city-planning": {
                "en": "City Planning",
                "fr": "Planification urbaine",
            },
            "toronto-police-service": {
                "en": "Toronto Police Service",
                "fr": "Service de police de Toronto",
            },
            "toronto-fire-services": {
                "en": "Toronto Fire Services",
                "fr": "Services d'incendie de Toronto",
            },
            "311-toronto": {
                "en": "311 Toronto — Customer Service",
                "fr": "311 Toronto — Service à la clientèle",
            },
            "municipal-licensing-and-standards": {
                "en": "Municipal Licensing and Standards",
                "fr": "Licences et normes municipales",
            },
            "transportation-services": {
                "en": "Transportation Services",
                "fr": "Services de transport",
            },
            "toronto-water": {
                "en": "Toronto Water",
                "fr": "Eau de Toronto",
            },
            "parks-forestry-and-recreation": {
                "en": "Parks, Forestry and Recreation",
                "fr": "Parcs, foresterie et loisirs",
            },
            "toronto-public-health": {
                "en": "Toronto Public Health",
                "fr": "Santé publique Toronto",
            },
            "shelter-support-and-housing-administration": {
                "en": "Shelter, Support and Housing Administration",
                "fr": "Administration du soutien à l'hébergement et au logement",
            },
            "economic-development-and-culture": {
                "en": "Economic Development and Culture",
                "fr": "Développement économique et culture",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://toronto/ward-list",
    mime_type="application/json",
    name="toronto_ward_list",
    title="Toronto City Council Wards (25 Wards)",
)
def toronto_ward_list() -> str:
    """All 25 Toronto city council wards with numbers and names.

    Use ward numbers with toronto_get_311_requests(ward=...) to filter
    service requests by ward. The current ward structure has 25 wards
    (updated 2018 municipal election).
    """
    return json.dumps(
        [
            {"ward": 1, "name": "Etobicoke North"},
            {"ward": 2, "name": "Etobicoke Centre"},
            {"ward": 3, "name": "Etobicoke-Lakeshore"},
            {"ward": 4, "name": "Parkdale-High Park"},
            {"ward": 5, "name": "York South-Weston"},
            {"ward": 6, "name": "York Centre"},
            {"ward": 7, "name": "Humber River-Black Creek"},
            {"ward": 8, "name": "Eglinton-Lawrence"},
            {"ward": 9, "name": "Davenport"},
            {"ward": 10, "name": "Spadina-Fort York"},
            {"ward": 11, "name": "University-Rosedale"},
            {"ward": 12, "name": "Toronto-St. Paul's"},
            {"ward": 13, "name": "Toronto Centre"},
            {"ward": 14, "name": "Toronto-Danforth"},
            {"ward": 15, "name": "Don Valley West"},
            {"ward": 16, "name": "Don Valley East"},
            {"ward": 17, "name": "Don Valley North"},
            {"ward": 18, "name": "Willowdale"},
            {"ward": 19, "name": "Beaches-East York"},
            {"ward": 20, "name": "Scarborough Southwest"},
            {"ward": 21, "name": "Scarborough Centre"},
            {"ward": 22, "name": "Scarborough-Agincourt"},
            {"ward": 23, "name": "Scarborough North"},
            {"ward": 24, "name": "Scarborough-Guildwood"},
            {"ward": 25, "name": "Scarborough-Rouge Park"},
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://toronto/neighbourhood-list",
    mime_type="application/json",
    name="toronto_neighbourhood_list",
    title="Toronto Neighbourhoods (140 Official Neighbourhoods)",
)
def toronto_neighbourhood_list() -> str:
    """All 140 official Toronto neighbourhoods with IDs (2016 model).

    Use neighbourhood names with toronto_get_neighbourhood_profile to retrieve
    detailed census indicators. The 2016 model has exactly 140 neighbourhoods.
    """
    return json.dumps(
        [
            {"id": 1, "name": "West Humber-Clairville"},
            {"id": 2, "name": "Mount Olive-Silverstone-Jamestown"},
            {"id": 3, "name": "Thistletown-Beaumond Heights"},
            {"id": 4, "name": "Rexdale-Kipling"},
            {"id": 5, "name": "Elms-Old Rexdale"},
            {"id": 6, "name": "Kingsview Village-The Westway"},
            {"id": 7, "name": "Willowridge-Martingrove-Richview"},
            {"id": 8, "name": "Humber Heights-Westmount"},
            {"id": 9, "name": "Edenbridge-Humber Valley"},
            {"id": 10, "name": "Princess-Rosethorn"},
            {"id": 11, "name": "Eringate-Centennial-West Deane"},
            {"id": 12, "name": "Markland Wood"},
            {"id": 13, "name": "Etobicoke West Mall"},
            {"id": 14, "name": "Islington-City Centre West"},
            {"id": 15, "name": "Kingsway South"},
            {"id": 16, "name": "Stonegate-Queensway"},
            {"id": 17, "name": "Mimico (includes Humber Bay Shores)"},
            {"id": 18, "name": "New Toronto"},
            {"id": 19, "name": "Long Branch"},
            {"id": 20, "name": "Alderwood"},
            {"id": 21, "name": "Humber Summit"},
            {"id": 22, "name": "Humbermede"},
            {"id": 23, "name": "Pelmo Park-Humberlea"},
            {"id": 24, "name": "Black Creek"},
            {"id": 25, "name": "Glenfield-Jane Heights"},
            {"id": 26, "name": "Downsview-Roding-CFB"},
            {"id": 27, "name": "York University Heights"},
            {"id": 28, "name": "Rustic"},
            {"id": 29, "name": "Maple Leaf"},
            {"id": 30, "name": "Brookhaven-Amesbury"},
            {"id": 31, "name": "Yorkdale-Glen Park"},
            {"id": 32, "name": "Englemount-Lawrence"},
            {"id": 33, "name": "Clanton Park"},
            {"id": 34, "name": "Bathurst Manor"},
            {"id": 35, "name": "Westminster-Branson"},
            {"id": 36, "name": "Newtonbrook West"},
            {"id": 37, "name": "Willowdale West"},
            {"id": 38, "name": "Lansing-Westgate"},
            {"id": 39, "name": "Bedford Park-Nortown"},
            {"id": 40, "name": "St.Andrew-Windfields"},
            {"id": 41, "name": "Bridle Path-Sunnybrook-York Mills"},
            {"id": 42, "name": "Lawrence Park North"},
            {"id": 43, "name": "Lytton Park"},
            {"id": 44, "name": "Lawrence Park South"},
            {"id": 45, "name": "Forest Hill North"},
            {"id": 46, "name": "Forest Hill South"},
            {"id": 47, "name": "Casa Loma"},
            {"id": 48, "name": "Annex"},
            {"id": 49, "name": "Yonge-St.Clair"},
            {"id": 50, "name": "Rosedale-Moore Park"},
            {"id": 51, "name": "Mount Pleasant East"},
            {"id": 52, "name": "Yonge-Eglinton"},
            {"id": 53, "name": "Mount Pleasant West"},
            {"id": 54, "name": "Davisville Village"},
            {"id": 55, "name": "Mount Pleasant West"},
            {"id": 56, "name": "Lawrence Heights"},
            {"id": 57, "name": "Glen Park"},
            {"id": 58, "name": "Oakwood Village"},
            {"id": 59, "name": "Humewood-Cedarvale"},
            {"id": 60, "name": "Wychwood"},
            {"id": 61, "name": "Corso Italia-Davenport"},
            {"id": 62, "name": "Dovercourt-Wallace Emerson-Junction"},
            {"id": 63, "name": "Weston"},
            {"id": 64, "name": "Weston-Pelham Park"},
            {"id": 65, "name": "Mount Dennis"},
            {"id": 66, "name": "Keelesdale-Eglinton West"},
            {"id": 67, "name": "Rockcliffe-Smythe"},
            {"id": 68, "name": "Beechborough-Greenbrook"},
            {"id": 69, "name": "Lambton Baby Point"},
            {"id": 70, "name": "Runnymede-Bloor West Village"},
            {"id": 71, "name": "High Park-Swansea"},
            {"id": 72, "name": "High Park North"},
            {"id": 73, "name": "Parkdale"},
            {"id": 74, "name": "Roncesvalles"},
            {"id": 75, "name": "South Parkdale"},
            {"id": 76, "name": "Dufferin Grove"},
            {"id": 77, "name": "Little Portugal"},
            {"id": 78, "name": "Trinity-Bellwoods"},
            {"id": 79, "name": "Niagara"},
            {"id": 80, "name": "Palmerston-Little Italy"},
            {"id": 81, "name": "University"},
            {"id": 82, "name": "Kensington-Chinatown"},
            {"id": 83, "name": "Trinity-Bellwoods"},
            {"id": 84, "name": "South Riverdale"},
            {"id": 85, "name": "Greenwood-Coxwell"},
            {"id": 86, "name": "Woodbine Corridor"},
            {"id": 87, "name": "East End-Danforth"},
            {"id": 88, "name": "The Beaches"},
            {"id": 89, "name": "Woodbine-Lumsden"},
            {"id": 90, "name": "O'Connor-Parkview"},
            {"id": 91, "name": "Broadview North"},
            {"id": 92, "name": "Old East York"},
            {"id": 93, "name": "Leaside-Bennington"},
            {"id": 94, "name": "Thorncliffe Park"},
            {"id": 95, "name": "Flemingdon Park"},
            {"id": 96, "name": "Victoria Village"},
            {"id": 97, "name": "Wexford/Maryvale"},
            {"id": 98, "name": "Clairlea-Birchmount"},
            {"id": 99, "name": "Kennedy Park"},
            {"id": 100, "name": "Ionview"},
            {"id": 101, "name": "Dorset Park"},
            {"id": 102, "name": "Bendale"},
            {"id": 103, "name": "Agincourt South-Malvern West"},
            {"id": 104, "name": "Agincourt North"},
            {"id": 105, "name": "Milliken"},
            {"id": 106, "name": "Rouge"},
            {"id": 107, "name": "Malvern"},
            {"id": 108, "name": "Morningside"},
            {"id": 109, "name": "Woburn"},
            {"id": 110, "name": "Centennial Scarborough"},
            {"id": 111, "name": "Highland Creek"},
            {"id": 112, "name": "West Hill"},
            {"id": 113, "name": "Scarborough Village"},
            {"id": 114, "name": "Guildwood"},
            {"id": 115, "name": "Eglinton East"},
            {"id": 116, "name": "Birchcliffe-Cliffside"},
            {"id": 117, "name": "Cliffcrest"},
            {"id": 118, "name": "Oakridge"},
            {"id": 119, "name": "Dorset Park"},
            {"id": 120, "name": "Tam O'Shanter-Sullivan"},
            {"id": 121, "name": "Newtonbrook East"},
            {"id": 122, "name": "Willowdale East"},
            {"id": 123, "name": "Bayview Woods-Steeles"},
            {"id": 124, "name": "Don Valley Village"},
            {"id": 125, "name": "Hillcrest Village"},
            {"id": 126, "name": "Bayview Village"},
            {"id": 127, "name": "Henry Farm"},
            {"id": 128, "name": "Pleasant View"},
            {"id": 129, "name": "L'Amoreaux"},
            {"id": 130, "name": "Steeles"},
            {"id": 131, "name": "Cabbagetown-South St.James Town"},
            {"id": 132, "name": "Regent Park"},
            {"id": 133, "name": "Moss Park"},
            {"id": 134, "name": "North St.James Town"},
            {"id": 135, "name": "Church-Yonge Corridor"},
            {"id": 136, "name": "Bay Street Corridor"},
            {"id": 137, "name": "Waterfront Communities-The Island"},
            {"id": 138, "name": "Downtown Yonge East"},
            {"id": 139, "name": "St.Lawrence-East Bayfront-The Islands"},
            {"id": 140, "name": "Milliken"},
        ],
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://toronto/311-service-types",
    mime_type="application/json",
    name="toronto_311_service_types",
    title="Toronto 311 Common Service Request Types",
)
def toronto_311_service_types() -> str:
    """Common 311 service request types for toronto_get_311_requests.

    Use these service_request_type values to filter 311 request data.
    Types are English-only in the Toronto open data portal.
    """
    return json.dumps(
        {
            "categories": [
                {
                    "type": "Graffiti",
                    "en": "Graffiti removal from public and private property",
                    "fr": "Enlèvement de graffitis sur les propriétés publiques et privées",
                },
                {
                    "type": "Dead Animal on Road or Boulevard",
                    "en": "Removal of dead animals from public roads and boulevards",
                    "fr": "Enlèvement d'animaux morts des voies publiques et des boulevards",
                },
                {
                    "type": "Noise - Residential",
                    "en": "Noise complaints from residential properties",
                    "fr": "Plaintes de bruit provenant de propriétés résidentielles",
                },
                {
                    "type": "Street Light - Out",
                    "en": "Report of a street light that is not working",
                    "fr": "Signalement d'un lampadaire défectueux",
                },
                {
                    "type": "Sidewalk - Repair Needed",
                    "en": "Request to repair damaged or hazardous sidewalk",
                    "fr": "Demande de réparation d'un trottoir endommagé ou dangereux",
                },
                {
                    "type": "Pothole",
                    "en": "Report of a pothole requiring repair",
                    "fr": "Signalement d'un nid-de-poule à réparer",
                },
                {
                    "type": "Illegal Dumping",
                    "en": "Report of garbage or waste dumped illegally",
                    "fr": "Signalement de dépôt illégal de déchets",
                },
                {
                    "type": "Missed Garbage Pickup",
                    "en": "Report of a missed residential garbage collection",
                    "fr": "Signalement d'une collecte de déchets manquée",
                },
                {
                    "type": "Parking Enforcement",
                    "en": "Request for parking enforcement at a location",
                    "fr": "Demande d'application des règles de stationnement",
                },
                {
                    "type": "Tree Not on City Property",
                    "en": "Request for assistance with a tree on private property",
                    "fr": "Demande d'aide pour un arbre sur une propriété privée",
                },
            ],
            "note_en": "Use toronto_get_311_requests(service_request_type='Graffiti') to filter by type. Data available from 2009.",
            "note_fr": "Utilisez toronto_get_311_requests(service_request_type='Graffiti') pour filtrer par type. Données disponibles depuis 2009.",
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://toronto/ckan-guide",
    mime_type="text/markdown",
    name="toronto_ckan_guide",
    title="City of Toronto Open Data Portal Guide",
)
def toronto_ckan_guide() -> str:
    """Overview of Toronto open data portal (open.toronto.ca), CKAN usage, and search tips.

    Explains the Toronto CKAN portal structure, the datastore_active flag,
    and how to find and retrieve Toronto municipal datasets.
    """
    return """# City of Toronto Open Data Portal Guide

## Overview

The City of Toronto open data portal (open.toronto.ca) is powered by CKAN and
contains thousands of datasets from city divisions and agencies.

**API Base URL:** `https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/`
**Portal URL:** `https://open.toronto.ca`

## The `datastore_active` Flag

Toronto's CKAN has a special `datastore_active` property on resources:
- `datastore_active: true` — Data is loaded into CKAN Datastore (queryable via SQL API)
- `datastore_active: false` — Raw file only (CSV, XLSX, etc. must be downloaded)

mcp-canada uses `datastore_active` resources when available for faster access.

## Searching Datasets

Use `toronto_search_datasets` to search by keyword:
```
toronto_search_datasets(query="ttc routes", limit=10)
```

Filter by organization (city division):
```
toronto_search_datasets(query="transit", organization="toronto-transit-commission-ttc")
```

Use `toronto_list_organizations` to see all available division names.

## Dataset Details

Use `toronto_get_dataset_details` with the dataset ID or slug:
```
toronto_get_dataset_details("7795b45e-e65a-4465-81fc-c5b0dc4b531e")
```

## Downloading Resources

Use `toronto_get_resource` with the resource ID:
```
toronto_get_resource("f17e0649-8a28-4ed6-b6b4-d89e5b8bee5d")
```

For GeoJSON resources, the tool automatically handles `.geojson` files.

## Search Tips

- Toronto dataset titles are English-only
- Check for annual datasets (one resource per year) vs cumulative datasets
- 311 data is split into annual ZIP+CSV files — use the `year` parameter
- GTFS data requires downloading a ZIP file; toronto_get_ttc_stops handles this

## Data License

City of Toronto open data is licensed under the Open Government Licence – Toronto.
"""


@resource(
    "docs://toronto/neighbourhood-profiles-guide",
    mime_type="text/markdown",
    name="toronto_neighbourhood_profiles_guide",
    title="Toronto Neighbourhood Profiles Data Guide",
)
def toronto_neighbourhood_profiles_guide() -> str:
    """Guide to Toronto's 140-neighbourhood model and census indicator data.

    Explains the neighbourhood profile dataset structure, available census
    indicators, and how to use toronto_get_neighbourhood_profile effectively.
    """
    return """# Toronto Neighbourhood Profiles Guide

## Overview

Toronto's Neighbourhood Profiles dataset contains 2,383 census characteristics
for each of the city's 140 official neighbourhoods. Data comes from the 2016 Census
of Population conducted by Statistics Canada.

**Tool:** `toronto_get_neighbourhood_profile`
**Compare Tool:** `toronto_compare_neighbourhoods`
**Resource ID:** `7f8eee5e-85fb-415c-aef3-c3bd4998445f`

## The 140-Neighbourhood Model

Toronto has 140 official neighbourhoods (as of the 2016 model):
- Based on 2016 Census geography
- Boundaries align with Statistics Canada census tracts
- Numbered 1 to 158 (with some numbers skipped — only 140 neighbourhoods exist)
- See `data://toronto/neighbourhood-list` for the complete list with IDs

## Available Indicator Categories

| Category | Examples |
|----------|---------|
| Population | Total population, growth rate, density |
| Age | Age groups (0-4, 5-9, ... 85+), median age |
| Household | Household size, family type, lone-parent families |
| Income | Median household income, low income prevalence, LICO |
| Housing | Owned vs. rented, housing costs, housing suitability |
| Education | Highest education level, school attendance |
| Employment | Labour force, occupation, industry |
| Immigration | Immigrant status, country of origin, NOL |
| Language | Mother tongue, language spoken at home |
| Ethnicity | Visible minority status |

## Indicator Format

Each indicator has:
- `Characteristic`: The indicator name (e.g., "Total population")
- `City of Toronto`: City-wide value for comparison
- `{neighbourhood_name}`: Value for the requested neighbourhood

## Usage Example

```
toronto_get_neighbourhood_profile(neighbourhood="Annex")
toronto_compare_neighbourhoods(neighbourhood1="Annex", neighbourhood2="Regent Park")
```

## Notes

- Data is from the 2016 Census — a newer version may be released
- Neighbourhood boundaries and census tracts do not always align perfectly
- Some indicators show ranges or percentages, not raw counts
"""


@resource(
    "docs://toronto/gtfs-guide",
    mime_type="text/markdown",
    name="toronto_gtfs_guide",
    title="Toronto TTC GTFS Data Guide",
)
def toronto_gtfs_guide() -> str:
    """Guide to GTFS data format, TTC stop/route IDs, and refresh frequency.

    Explains the General Transit Feed Specification (GTFS) as used by the
    Toronto Transit Commission (TTC) and how to work with TTC schedule data.
    """
    return """# Toronto TTC GTFS Data Guide

## What is GTFS?

GTFS (General Transit Feed Specification) is the standard format for public
transit schedules and geographic information. The TTC publishes its GTFS feed
on the Toronto open data portal as a ZIP archive.

**Dataset ID:** `7795b45e-e65a-4465-81fc-c5b0dc4b531e`
**Tools:** `toronto_get_ttc_stops`, `toronto_get_ttc_routes`

## GTFS File Structure

The TTC GTFS ZIP contains:

| File | Contents |
|------|---------|
| `stops.txt` | All TTC stops with stop_id, name, lat/lon |
| `routes.txt` | All TTC routes with route_id, short_name, long_name, type |
| `trips.txt` | Service trips linking routes to stop sequences |
| `stop_times.txt` | Scheduled arrival/departure times at each stop |
| `shapes.txt` | Geographic path of each route |
| `calendar.txt` | Service days (weekday, Saturday, Sunday) |
| `agency.txt` | TTC agency information |

## Stop IDs

TTC stop IDs are numeric strings (e.g., `"14002"` for a subway station).
Use `wx_get_ttc_stops(bbox=[lon_min, lat_min, lon_max, lat_max])` to find
stops in a geographic area.

## Route Types

| Type | Description |
|------|-------------|
| 0 | Streetcar (light rail) |
| 1 | Subway |
| 3 | Bus |

## Route Names

- Short name: Route number (e.g., `"501"` for the Queen streetcar)
- Long name: Route description (e.g., `"Queen"`)

## Refresh Frequency

The TTC GTFS feed is updated periodically (typically every 1-3 months).
mcp-canada caches the GTFS data for 6 hours (TTL 21600s).
For real-time positions, the TTC publishes a separate GTFS-Realtime feed
(not currently supported by mcp-canada).

## Common Use Cases

- Find all stops within 500m of an address (use bbox approximation)
- Get all routes serving a specific stop
- Find which subway line stops at a station by route type
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://toronto/neighbourhood-report",
    mime_type="text/markdown",
    name="toronto_neighbourhood_report_template",
    title="Toronto Neighbourhood Comparison Report Template",
)
def toronto_neighbourhood_report_template() -> str:
    """Template for formatting a Toronto neighbourhood comparison report.

    Replace {placeholder} values with actual data from toronto_get_neighbourhood_profile
    or toronto_compare_neighbourhoods before presenting to the user.
    """
    return """# Toronto Neighbourhood Profile: {neighbourhood_name}

**Neighbourhood ID:** {neighbourhood_id}
**Ward:** {ward_number} — {ward_name}
**Source:** City of Toronto Neighbourhood Profiles (2016 Census)

## Population

| Indicator | {neighbourhood_name} | City of Toronto |
|-----------|---------------------|-----------------|
| Total Population | {population} | 2,731,571 |
| Population Density (per km²) | {pop_density} | 4,334.4 |
| Population Change (2011-2016) | {pop_change}% | 4.5% |

## Age

| Age Group | % of Neighbourhood | % of City |
|-----------|-------------------|-----------|
| 0-14 years | {pct_0_14}% | 15.6% |
| 15-64 years | {pct_15_64}% | 67.2% |
| 65+ years | {pct_65_plus}% | 17.2% |
| Median Age | {median_age} | 39.3 |

## Income and Housing

| Indicator | {neighbourhood_name} | City of Toronto |
|-----------|---------------------|-----------------|
| Median Household Income | ${median_income} | $65,829 |
| Low Income Prevalence | {low_income_pct}% | 21.0% |
| Owner-Occupied Dwellings | {pct_owner}% | 53.0% |

## Key Observations

- {observation_1}
- {observation_2}
- {observation_3}

## Notes

Data from the 2016 Census of Population (Statistics Canada).
Neighbourhood boundaries may not align perfectly with census tracts.
"""
