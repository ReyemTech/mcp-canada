# :maple_leaf: IRCC Immigration

Permanent residents, temporary workers, study permits, Express Entry, asylum, and refugee data from [IRCC Open Data](https://www.ircc.canada.ca/opendata-donneesouvertes/data/).

> **Note:** IRCC suppresses values between 0-5 (shown as null) and rounds all other values to the nearest multiple of 5 for privacy protection. Ad-hoc PR files (`ircc_get_adhoc_pr`) are English-only.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (10)

<!-- CATALOG:ircc:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ircc_get_permanent_residents` | Get IRCC permanent resident admissions data by breakdown dimension. | `breakdown`, `year` |
| `ircc_get_study_permits` | Get IRCC study permit issuance data by breakdown dimension. | `breakdown`, `year` |
| `ircc_get_work_permits` | Get IRCC work permit data for IMP or TFWP programs. | `permit_type`, `breakdown`, `year` |
| `ircc_get_express_entry` | Get IRCC Express Entry data for admissions or invited candidates. | `stream`, `breakdown`, `year` |
| `ircc_get_tr_to_pr` | Get IRCC data on temporary residents who transitioned to permanent residence. | `breakdown`, `year` |
| `ircc_get_asylum` | Get IRCC asylum claimant data by province and demographic breakdown. | `breakdown`, `year` |
| `ircc_get_ops` | Get IRCC operational processing statistics (monthly snapshots). | `breakdown` |
| `ircc_get_afghan` | Get IRCC data on Afghan refugees admitted to Canada. | `breakdown`, `year` |
| `ircc_get_adhoc_pr` | Get IRCC ad-hoc historical permanent resident data (1980-2023, English-only). | `breakdown` |
| `ircc_list_datasets` | List all available IRCC open data datasets with their breakdown dimensions. | -- |
<!-- CATALOG:ircc:end -->

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `ircc_explore_immigration` | Guided | Explore IRCC immigration data -- choose dataset -> breakdown -> year |
| `ircc_quick_pr` | Quick | Get permanent resident admissions data |
| `ircc_track_express_entry` | Guided | Track Express Entry admissions and invite rounds |
| `ircc_compare_pathways` | Guided | Compare immigration pathways (PR vs study vs work) |
| `ircc_analyze_trends` | Guided | Analyze multi-year immigration trends |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://ircc/immigration-categories` | Catalog | Immigration category codes and bilingual names |
| `data://ircc/dataset-list` | Catalog | All 10 IRCC datasets mapped to tool names and breakdowns |
| `data://ircc/express-entry-streams` | Catalog | Express Entry stream codes and descriptions |
| `data://ircc/work-permit-types` | Catalog | IMP vs TFWP work permit program codes |
| `docs://ircc/data-guide` | Guide | IRCC open data structure, XLSX format, suppression rules |
| `docs://ircc/xlsx-quirks` | Guide | Multi-sheet XLSX parsing, suppressed values, year totals |
| `template://ircc/immigration-report` | Template | Immigration data report with `{dataset}`, `{breakdown}`, `{year}`, `{data}` |
