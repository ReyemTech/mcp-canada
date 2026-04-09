"""MCP resources for the IRCC Immigration module.

Provides reference catalogs, documentation guides, and response templates for
Immigration, Refugees and Citizenship Canada (IRCC) open data. All resources use
type-prefixed URIs:
- data://ircc/...    — JSON reference catalogs (machine-parseable)
- docs://ircc/...    — Markdown documentation guides (human-readable)
- template://ircc/...— Markdown response templates with {placeholder} syntax

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
    "data://ircc/immigration-categories",
    mime_type="application/json",
    name="ircc_immigration_categories",
    title="IRCC Immigration Categories",
)
def ircc_immigration_categories() -> str:
    """Valid immigration categories for permanent resident data.

    Maps category keys to bilingual descriptions used in IRCC PR data.
    Use this to understand the breakdown parameter values for ircc_get_permanent_residents.
    Format: {"category_key": {"en": "English label", "fr": "Étiquette en français"}}
    """
    return json.dumps(
        {
            "economic": {
                "en": "Economic immigrants (skilled workers, business immigrants)",
                "fr": "Immigrants économiques (travailleurs qualifiés, gens d'affaires)",
            },
            "family": {
                "en": "Family class (spouses, children, parents, grandparents)",
                "fr": "Regroupement familial (conjoints, enfants, parents, grands-parents)",
            },
            "refugee": {
                "en": "Refugees and protected persons (government-assisted, privately sponsored)",
                "fr": "Réfugiés et personnes protégées (pris en charge par le gouvernement, parrainés par le secteur privé)",
            },
            "humanitarian": {
                "en": "Humanitarian and other (H&C grounds, public policy)",
                "fr": "Raisons d'ordre humanitaire et autres (motifs d'ordre humanitaire, politique publique)",
            },
            "express_entry": {
                "en": "Express Entry (Federal Skilled Worker, Canadian Experience Class, Federal Skilled Trades)",
                "fr": "Entrée express (Travailleurs qualifiés fédéraux, Expérience canadienne, Métiers spécialisés fédéraux)",
            },
            "provincial_nominee": {
                "en": "Provincial Nominee Program (PNP) — each province selects based on local needs",
                "fr": "Programme des candidats des provinces (PCP) — chaque province sélectionne selon ses besoins",
            },
            "caregiver": {
                "en": "Caregivers (home child care, home support worker pilots)",
                "fr": "Aidants (gardiens d'enfants à domicile, pilotes de travailleurs en soins à domicile)",
            },
            "atlantic": {
                "en": "Atlantic Immigration Program (AIP) for Atlantic provinces",
                "fr": "Programme d'immigration atlantique (PIA) pour les provinces de l'Atlantique",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ircc/dataset-list",
    mime_type="application/json",
    name="ircc_dataset_list",
    title="Available IRCC Datasets",
)
def ircc_dataset_list() -> str:
    """Available IRCC open data datasets with tool name mappings.

    Maps each dataset key to its tool name, description, and available breakdowns.
    Use this to discover which tool to call for specific immigration data.
    """
    return json.dumps(
        {
            "pr": {
                "tool": "ircc_get_permanent_residents",
                "en": "Permanent Residents — admissions by country, province, gender, age, CMA",
                "fr": "Résidents permanents — admissions par pays, province, sexe, âge, RMR",
                "breakdowns": ["country", "province", "gender", "age", "cma", "noc"],
            },
            "study": {
                "tool": "ircc_get_study_permits",
                "en": "Study Permits — permits issued to international students",
                "fr": "Permis d'études — permis délivrés aux étudiants étrangers",
                "breakdowns": ["country", "province_level", "gender"],
            },
            "work_imp": {
                "tool": "ircc_get_work_permits",
                "en": "Work Permits — International Mobility Program (IMP)",
                "fr": "Permis de travail — Programme de mobilité internationale (PMI)",
                "breakdowns": ["province_program", "gender_skill", "country"],
            },
            "work_tfwp": {
                "tool": "ircc_get_work_permits",
                "en": "Work Permits — Temporary Foreign Worker Program (TFWP)",
                "fr": "Permis de travail — Programme des travailleurs étrangers temporaires (PTET)",
                "breakdowns": ["province_program", "gender_skill", "country"],
            },
            "ee_admissions": {
                "tool": "ircc_get_express_entry",
                "en": "Express Entry Admissions — PR grants from Express Entry draws",
                "fr": "Admissions par Entrée express — octrois de RP suite aux tirages",
                "breakdowns": ["gender", "category", "country", "age"],
            },
            "ee_invited": {
                "tool": "ircc_get_express_entry",
                "en": "Express Entry Invitations to Apply (ITAs) — candidates invited to apply",
                "fr": "Invitations à présenter une demande (IPD) par Entrée express",
                "breakdowns": ["destination", "score", "country", "age"],
            },
            "tr_to_pr": {
                "tool": "ircc_get_tr_to_pr",
                "en": "Temporary Resident to Permanent Resident Transitions",
                "fr": "Transitions de résident temporaire à résident permanent",
                "breakdowns": ["study_permit", "imp", "tfwp", "pgwp"],
            },
            "asylum": {
                "tool": "ircc_get_asylum",
                "en": "Asylum Claimants — refugee protection claimants",
                "fr": "Demandeurs d'asile — demandeurs de protection des réfugiés",
                "breakdowns": ["province_office", "province_age", "province_gender"],
            },
            "citizenship": {
                "tool": "ircc_get_citizenship",
                "en": "New Citizens — grants of citizenship by country of birth",
                "fr": "Nouveaux citoyens — octrois de citoyenneté par pays de naissance",
                "breakdowns": ["country"],
            },
            "afghan": {
                "tool": "ircc_get_afghan",
                "en": "Afghan Refugees — special measures for Afghan nationals",
                "fr": "Réfugiés afghans — mesures spéciales pour les ressortissants afghans",
                "breakdowns": ["gender", "age", "education", "language"],
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ircc/express-entry-streams",
    mime_type="application/json",
    name="ircc_express_entry_streams",
    title="Express Entry Immigration Streams",
)
def ircc_express_entry_streams() -> str:
    """Valid Express Entry streams for ircc_get_express_entry.

    Maps stream codes to bilingual descriptions of each Express Entry category.
    """
    return json.dumps(
        {
            "FSW": {
                "en": "Federal Skilled Worker (FSW) — for skilled workers with foreign work experience",
                "fr": "Travailleurs qualifiés fédéraux (TQF) — pour les travailleurs qualifiés ayant une expérience à l'étranger",
                "requirements_en": "Skilled work experience, language ability, education",
                "requirements_fr": "Expérience de travail qualifié, compétences linguistiques, formation",
            },
            "CEC": {
                "en": "Canadian Experience Class (CEC) — for skilled workers with Canadian work experience",
                "fr": "Expérience canadienne (EC) — pour les travailleurs qualifiés ayant une expérience au Canada",
                "requirements_en": "At least 1 year Canadian work experience in last 3 years",
                "requirements_fr": "Au moins 1 an d'expérience de travail canadienne au cours des 3 dernières années",
            },
            "FST": {
                "en": "Federal Skilled Trades (FST) — for workers qualified in a skilled trade",
                "fr": "Métiers spécialisés fédéraux (MSF) — pour les travailleurs qualifiés dans un métier spécialisé",
                "requirements_en": "Skilled trade qualifications, job offer or certificate of qualification",
                "requirements_fr": "Qualifications en métier spécialisé, offre d'emploi ou certificat de qualification",
            },
            "PNP": {
                "en": "Provincial Nominee Program (PNP) — nominated by a province through Express Entry",
                "fr": "Programme des candidats des provinces (PCP) — désigné par une province via Entrée express",
                "requirements_en": "Provincial nomination adds 600 CRS points; effectively guarantees an ITA",
                "requirements_fr": "La désignation provinciale ajoute 600 points SCC; garantit pratiquement une IPD",
            },
            "TR": {
                "en": "To Transition (TR to PR) — temporary residents transitioning to permanent residency",
                "fr": "Transition (RP vers PR) — résidents temporaires passant à la résidence permanente",
                "requirements_en": "Specific to temporary measures and pilot programs",
                "requirements_fr": "Spécifique aux mesures temporaires et projets pilotes",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://ircc/work-permit-types",
    mime_type="application/json",
    name="ircc_work_permit_types",
    title="IRCC Work Permit Types (IMP vs TFWP)",
)
def ircc_work_permit_types() -> str:
    """Work permit type descriptions for ircc_get_work_permits.

    Explains the difference between IMP (International Mobility Program)
    and TFWP (Temporary Foreign Worker Program).
    """
    return json.dumps(
        {
            "IMP": {
                "full_name_en": "International Mobility Program",
                "full_name_fr": "Programme de mobilité internationale",
                "en": "IMP allows employers to hire temporary workers without an LMIA. Includes intra-company transfers, CUSMA/USMCA workers, and youth exchange programs.",
                "fr": "Le PMI permet aux employeurs d'embaucher des travailleurs temporaires sans EIMT. Comprend les transferts intraentreprises, les travailleurs ACEUM/CUSMA et les programmes d'échanges jeunesse.",
                "lmia_required": False,
                "tool_param": "permit_type='IMP'",
            },
            "TFWP": {
                "full_name_en": "Temporary Foreign Worker Program",
                "full_name_fr": "Programme des travailleurs étrangers temporaires",
                "en": "TFWP requires employers to obtain a Labour Market Impact Assessment (LMIA) proving no Canadian worker is available. Used for specific job offers.",
                "fr": "Le PTET exige que les employeurs obtiennent une étude d'impact sur le marché du travail (EIMT) prouvant l'absence de travailleur canadien disponible. Utilisé pour des offres d'emploi spécifiques.",
                "lmia_required": True,
                "tool_param": "permit_type='TFWP'",
            },
            "note_en": "Use ircc_get_work_permits(permit_type='IMP') or ircc_get_work_permits(permit_type='TFWP'). Omit permit_type to get both combined.",
            "note_fr": "Utilisez ircc_get_work_permits(permit_type='IMP') ou ircc_get_work_permits(permit_type='TFWP'). Omettez permit_type pour obtenir les deux combinés.",
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://ircc/data-guide",
    mime_type="text/markdown",
    name="ircc_data_guide",
    title="IRCC Open Data Guide",
)
def ircc_data_guide() -> str:
    """Guide to IRCC open data structure, privacy masking, and bilingual files.

    Explains how IRCC data is organized, the -- privacy masking convention,
    and how to work with both English and French XLSX files.
    """
    return """# IRCC Open Data Guide

## Data Source

IRCC open data is published at:
- Federal open data portal: open.canada.ca
- Direct download URLs via ircc.canada.ca/opendata-donneesouvertes/

All data is available in both English (`EN_ODP-*.xlsx`) and French (`FR_ODP-*.xlsx`).

## Privacy Masking

IRCC masks small counts to protect individual privacy:
- Values of `--` (two dashes) indicate suppressed data (count below privacy threshold)
- The threshold is typically counts of 0-4 (exact threshold not published)
- Suppressed values appear in the data as the string `"--"` or null

**Implication:** When you see `--` in results, that country/category had very few
admissions in that period. The sum of a column with `--` values will be understated.

## File Structure

IRCC XLSX files use complex multi-row headers:
- Rows 1-2: Dataset title and metadata (skipped)
- Row 3: Year labels (spanning merged cells)
- Row 4: Quarter labels (Q1, Q2, Q3, Q4) or Month labels
- Row 5: Month labels (Jan, Feb, Mar... or just month number)
- Last column: "Year Total" — annual sum for each row

## Bilingual Files

Both English and French files contain the same data with:
- Column headers translated (Year/Année, Quarter/Trimestre)
- Category labels translated (e.g., "India" / "Inde")
- Use `lang='fr'` to get French labels in results

## Update Frequency

IRCC data is updated quarterly (approximately). New quarters appear within
3-4 months after the reference quarter ends. Annual totals are final.

## Available Breakdowns

Each dataset has multiple breakdown files (e.g., PR data by country, by province,
by gender, by age). Use the `breakdown` parameter to select the file you need.
See `data://ircc/dataset-list` for all available breakdowns per dataset.
"""


@resource(
    "docs://ircc/xlsx-quirks",
    mime_type="text/markdown",
    name="ircc_xlsx_quirks_guide",
    title="IRCC XLSX File Quirks Guide",
)
def ircc_xlsx_quirks_guide() -> str:
    """Guide to known IRCC XLSX file quirks for debugging data parsing issues.

    IRCC files use non-standard multi-row merged headers that require special
    parsing. This guide explains the known quirks and how mcp-canada handles them.
    """
    return """# IRCC XLSX File Quirks

## Multi-Row Merged Headers

IRCC Excel files use complex merged cell headers that pandas cannot parse automatically.
mcp-canada uses a custom parser that:
1. Skips the first 2 rows (title/metadata)
2. Reads 2-3 header rows and forward-fills merged cell values
3. Constructs column names like `2023_Q1_Jan`, `2023_Q4_Year Total`

## Header Layouts

| Dataset | Skip Rows | Header Rows | Label Columns | Notes |
|---------|-----------|-------------|---------------|-------|
| pr, study, work_imp, work_tfwp, afghan | 2 | 3 | 1 | Standard quarterly |
| ee_admissions, ee_invited, tr_to_pr | 2 | 3 | 2 | Two category label cols |
| asylum | 2 | 2 | 2 | Monthly (no quarter row) |
| ops | 6 | 2 | 1 | 6 skip rows + yearly/monthly |
| adhoc_pr, citizenship | 2 | 1 | 1 | Simple annual layout |

## Filenames with Spaces

Some IRCC filenames contain literal spaces:
- `EN_ODP-TR-Work-IMP CITZ.xlsx` (note the space before CITZ)
- `Open Data - OPS PR Intake en.xlsx` (spaces in Operational Processing files)

These URLs are stored as-is; httpx handles encoding correctly.
Do NOT manually percent-encode spaces in these filenames.

## Multi-Sheet Workbooks

Some IRCC files contain multiple worksheets. mcp-canada always reads the first
sheet (`sheet_name=0`). If data appears missing, the file may have been updated
with a different sheet structure.

## Year Total Columns

Each file has a "Year Total" column at the end of each year's data.
These are NOT individual month/quarter observations — they are annual sums.
mcp-canada's parser identifies and handles Year Total columns separately.

## Ad-Hoc PR Files (XLS Format)

The `adhoc_pr` dataset uses legacy `.xls` format (not `.xlsx`).
Requires the `xlrd` package: `pip install mcp-canada[ircc]`
These files are English-only — requesting `lang='fr'` will raise an error.

## Operational Processing Files

The `ops` dataset has 6 extra header rows with notes and disclaimers.
The parser skips these 6 rows before reading the 2-row year/month header.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://ircc/immigration-report",
    mime_type="text/markdown",
    name="ircc_immigration_report_template",
    title="IRCC Immigration Data Analysis Report Template",
)
def ircc_immigration_report_template() -> str:
    """Template for formatting an IRCC immigration data analysis report.

    Replace {placeholder} values with actual data from IRCC tools before
    presenting to the user.
    """
    return """# Immigration Data Report: {dataset_name}

**Period:** {start_year} to {end_year}
**Breakdown:** {breakdown_type}
**Source:** Immigration, Refugees and Citizenship Canada (IRCC)

## Summary

{summary_paragraph}

## Top {n} {category_type}

| Rank | {category_label} | {year1} | {year2} | Change |
|------|{category_dashes}|---------|---------|--------|
{top_rows}

## Annual Totals

| Year | Total | Change vs Prior Year |
|------|-------|---------------------|
{annual_rows}

## Key Observations

- {observation_1}
- {observation_2}
- {observation_3}

## Notes

Data retrieved from IRCC open data portal.
Values of `--` indicate suppressed counts (privacy threshold).
Annual totals may differ from sum of quarterly values due to rounding.
"""
