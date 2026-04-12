# :pill: Drug Product Database

Drug information from [Health Canada's DPD](https://health-products.canada.ca/api/drug/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (8)

<!-- CATALOG:drug-database:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `drug_search` | Search Health Canada's Drug Product Database for drug products. | `brand_name`, `din`, `company` |
| `drug_get_details` | Get comprehensive details for a drug product in one call. | `drug_code` |
| `drug_get_ingredients` | Get active ingredients for a Health Canada drug product. | `drug_code` |
| `drug_get_routes` | Get routes of administration for a Health Canada drug product. | `drug_code` |
| `drug_search_companies` | Search for pharmaceutical companies in Health Canada's Drug Product Database. | `company_name` |
| `drug_get_schedule` | Get schedule classification for a Health Canada drug product. | `drug_code` |
| `drug_get_therapeutic_class` | Get ATC therapeutic classification for a Health Canada drug product. | `drug_code` |
| `drug_get_status` | Get market status for a Health Canada drug product. | `drug_code` |
<!-- CATALOG:drug-database:end -->

> **Note:** `drug_code` is the internal database ID (from `drug_search` results), NOT the DIN.

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `drug_research_medication` | Guided | Research a drug -- search -> ingredients -> schedule -> status |
| `drug_quick_search` | Quick | Search drugs by brand name or DIN |
| `drug_check_company` | Quick | Look up a pharmaceutical company's products |
| `drug_compare_generics` | Guided | Compare a brand drug to its generic equivalents |
| `drug_check_status` | Quick | Get market status for a drug product |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://drug/schedule-codes` | Catalog | Health Canada schedule classification (Prescription/OTC/Schedule I-III) |
| `data://drug/route-codes` | Catalog | Routes of administration with bilingual labels |
| `data://drug/status-codes` | Catalog | Market status codes (marketed, discontinued, etc.) |
| `data://drug/therapeutic-classes` | Catalog | ATC therapeutic class codes and descriptions |
| `docs://drug/din-guide` | Guide | DIN vs drug_code distinction, how to find a drug_code |
| `docs://drug/search-tips` | Guide | Brand vs generic search, company name matching |
| `template://drug/medication-report` | Template | Drug profile with `{drug_code}`, `{brand_name}`, `{schedule}`, `{ingredients}` |
