"""MCP resources for the Drug Database module.

Provides reference catalogs, documentation guides, and response templates for
the Health Canada Drug Product Database. All resources use type-prefixed URIs:
- data://drug/...    — JSON reference catalogs (machine-parseable)
- docs://drug/...    — Markdown documentation guides (human-readable)
- template://drug/...— Markdown response templates with {placeholder} syntax

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
    "data://drug/schedule-codes",
    mime_type="application/json",
    name="drug_schedule_codes",
    title="Health Canada Drug Schedule Types",
)
def drug_schedule_codes() -> str:
    """Drug schedule classifications used by Health Canada.

    Use this to interpret the schedule field returned by drug_get_details
    and drug_get_schedule.
    """
    return json.dumps(
        {
            "Prescription": {
                "en": "Prescription (Rx) — requires a prescription from a licensed healthcare provider",
                "fr": "Ordonnance (Rx) — nécessite une ordonnance d'un professionnel de la santé",
                "code": "Rx",
            },
            "OTC": {
                "en": "Over-the-counter — available without a prescription",
                "fr": "Sans ordonnance — disponible sans ordonnance",
                "code": "OTC",
            },
            "Schedule I": {
                "en": "Schedule I — requires a prescription; cannot be refilled without a new prescription",
                "fr": "Annexe I — nécessite une ordonnance; ne peut être renouvelé sans nouvelle ordonnance",
                "code": "S-I",
            },
            "Schedule II": {
                "en": "Schedule II — pharmacist oversight required; no prescription needed but kept behind counter",
                "fr": "Annexe II — supervision du pharmacien requise; pas d'ordonnance requise mais conservé derrière le comptoir",
                "code": "S-II",
            },
            "Schedule III": {
                "en": "Schedule III — self-selectable from pharmacy shelves; professional advice recommended",
                "fr": "Annexe III — accessible en libre-service dans la pharmacie; conseil professionnel recommandé",
                "code": "S-III",
            },
            "Unscheduled": {
                "en": "Unscheduled — no scheduling criteria met; may be sold in any retail outlet",
                "fr": "Non planifié — aucun critère d'inscription n'est rempli; peut être vendu dans tout commerce de détail",
                "code": "U",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://drug/route-codes",
    mime_type="application/json",
    name="drug_route_codes",
    title="Health Canada Drug Administration Routes",
)
def drug_route_codes() -> str:
    """Common drug administration routes in the Health Canada database.

    Use this to interpret the route field returned by drug_get_routes.
    Format: {"route": {"en": "English label", "fr": "French label"}}
    """
    return json.dumps(
        {
            "oral": {
                "en": "Oral — taken by mouth (tablets, capsules, liquids)",
                "fr": "Orale — pris par la bouche (comprimés, capsules, liquides)",
            },
            "topical": {
                "en": "Topical — applied to the skin surface",
                "fr": "Topique — appliqué sur la surface de la peau",
            },
            "intravenous": {
                "en": "Intravenous (IV) — injected directly into a vein",
                "fr": "Intraveineuse (IV) — injecté directement dans une veine",
            },
            "intramuscular": {
                "en": "Intramuscular (IM) — injected into muscle tissue",
                "fr": "Intramusculaire (IM) — injecté dans le tissu musculaire",
            },
            "subcutaneous": {
                "en": "Subcutaneous (SC) — injected under the skin",
                "fr": "Sous-cutanée (SC) — injecté sous la peau",
            },
            "inhalation": {
                "en": "Inhalation — breathed in through mouth or nose",
                "fr": "Inhalation — respiré par la bouche ou le nez",
            },
            "ophthalmic": {
                "en": "Ophthalmic — applied to the eye",
                "fr": "Ophtalmique — appliqué à l'oeil",
            },
            "otic": {
                "en": "Otic — applied to the ear",
                "fr": "Otique — appliqué à l'oreille",
            },
            "nasal": {
                "en": "Nasal — applied to or inhaled through the nose",
                "fr": "Nasale — appliqué ou inhalé par le nez",
            },
            "rectal": {
                "en": "Rectal — inserted into the rectum (suppositories, enemas)",
                "fr": "Rectale — inséré dans le rectum (suppositoires, lavements)",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://drug/status-codes",
    mime_type="application/json",
    name="drug_status_codes",
    title="Health Canada Drug Market Status Codes",
)
def drug_status_codes() -> str:
    """Drug market status codes used in the Health Canada Drug Product Database.

    Use this to interpret the status field returned by drug_get_details and drug_get_status.
    """
    return json.dumps(
        {
            "APPROVED": {
                "en": "Approved — drug has been authorized for sale in Canada",
                "fr": "Approuvé — le médicament a été autorisé à la vente au Canada",
                "active": True,
            },
            "MARKETED": {
                "en": "Marketed — drug is currently being sold in Canada",
                "fr": "Commercialisé — le médicament est actuellement vendu au Canada",
                "active": True,
            },
            "CANCELLED PRE-MARKET": {
                "en": "Cancelled (Pre-Market) — authorization cancelled before reaching market",
                "fr": "Annulé (Pré-mise en marché) — autorisation annulée avant commercialisation",
                "active": False,
            },
            "CANCELLED POST-MARKET": {
                "en": "Cancelled (Post-Market) — authorization cancelled after being marketed",
                "fr": "Annulé (Post-mise en marché) — autorisation annulée après commercialisation",
                "active": False,
            },
            "DORMANT": {
                "en": "Dormant — authorization exists but drug is not currently marketed",
                "fr": "Dormant — l'autorisation existe mais le médicament n'est pas commercialisé",
                "active": False,
            },
            "UNDER REVIEW": {
                "en": "Under Review — New Drug Submission under Health Canada review",
                "fr": "À l'examen — présentation de nouveau médicament à l'examen de Santé Canada",
                "active": False,
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@resource(
    "data://drug/therapeutic-classes",
    mime_type="application/json",
    name="drug_therapeutic_classes",
    title="ATC Therapeutic Class Codes for Drug Research",
)
def drug_therapeutic_classes() -> str:
    """Common ATC (Anatomical Therapeutic Chemical) therapeutic class codes.

    Use this to interpret the therapeutic_class field from drug_get_therapeutic_class.
    Format: {"ATC_CODE": {"en": "Class name", "fr": "Nom de la classe"}}
    """
    return json.dumps(
        {
            "A": {
                "en": "Alimentary tract and metabolism (antacids, diabetes, vitamins)",
                "fr": "Voies digestives et métabolisme (antiacides, diabète, vitamines)",
            },
            "B": {
                "en": "Blood and blood forming organs (anticoagulants, antianaemics)",
                "fr": "Sang et organes hématopoïétiques (anticoagulants, antianémiques)",
            },
            "C": {
                "en": "Cardiovascular system (cardiac therapy, antihypertensives, lipid-lowering)",
                "fr": "Système cardiovasculaire (cardiothérapie, antihypertenseurs, hypolipémiants)",
            },
            "D": {
                "en": "Dermatologicals (topical antibiotics, antifungals, corticosteroids)",
                "fr": "Dermatologie (antibiotiques topiques, antifongiques, corticostéroïdes)",
            },
            "G": {
                "en": "Genito-urinary system and sex hormones",
                "fr": "Système génito-urinaire et hormones sexuelles",
            },
            "H": {
                "en": "Systemic hormonal preparations (thyroid, adrenal, pituitary hormones)",
                "fr": "Préparations hormonales systémiques (hormones thyroïdiennes, surrénaliennes, hypophysaires)",
            },
            "J": {
                "en": "Antiinfectives for systemic use (antibiotics, antivirals, vaccines)",
                "fr": "Anti-infectieux à usage systémique (antibiotiques, antiviraux, vaccins)",
            },
            "L": {
                "en": "Antineoplastic and immunomodulating agents (chemotherapy, immunosuppressants)",
                "fr": "Antinéoplasiques et immunomodulateurs (chimiothérapie, immunosuppresseurs)",
            },
            "M": {
                "en": "Musculo-skeletal system (anti-inflammatory, muscle relaxants)",
                "fr": "Système musculo-squelettique (anti-inflammatoires, myorelaxants)",
            },
            "N": {
                "en": "Nervous system (analgesics, antidepressants, anxiolytics, anesthetics)",
                "fr": "Système nerveux (analgésiques, antidépresseurs, anxiolytiques, anesthésiques)",
            },
            "P": {
                "en": "Antiparasitic products, insecticides and repellents",
                "fr": "Antiparasitaires, insecticides et répulsifs",
            },
            "R": {
                "en": "Respiratory system (antiasthmatics, cough/cold preparations)",
                "fr": "Système respiratoire (antiasthmatiques, préparations contre la toux)",
            },
            "S": {
                "en": "Sensory organs (ophthalmic, otic, nasal preparations)",
                "fr": "Organes sensoriels (préparations ophtalmiques, otiques, nasales)",
            },
            "V": {
                "en": "Various (contrast media, radiopharmaceuticals, diagnostics)",
                "fr": "Divers (produits de contraste, radiopharmaceutiques, diagnostics)",
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Documentation resources (docs://)
# ---------------------------------------------------------------------------


@resource(
    "docs://drug/din-guide",
    mime_type="text/markdown",
    name="drug_din_guide",
    title="Guide to Drug Identification Numbers (DIN) in Canada",
)
def drug_din_guide() -> str:
    """Guide to what a DIN (Drug Identification Number) is and how to use it.

    Covers how DINs work, how to find them, and how to use them in drug_get_details.
    """
    return """# Drug Identification Number (DIN) Guide

## What is a DIN?

A Drug Identification Number (DIN) is an 8-digit number assigned by Health Canada
to each drug product authorized for sale in Canada. Every unique combination of:
- Drug product name
- Manufacturer
- Active ingredients and strengths
- Pharmaceutical dosage form
- Route of administration

...receives its own unique DIN.

## Format

DINs are always **8 digits** (zero-padded if needed):
- Example: `00012262` (acetaminophen 325 mg tablets)
- Example: `02241007` (atorvastatin 10 mg tablets)

## Finding a DIN

1. **From a medication bottle** — printed on the label as "DIN: XXXXXXXX"
2. **Using drug_search** — search by brand or generic name, then check the `din` field
3. **Health Canada Drug Product Database** — searchable at health-products.canada.ca

## Using DINs in the API

```
drug_get_details(din="02241007")
drug_get_ingredients(din="02241007")
drug_get_routes(din="02241007")
drug_get_status(din="02241007")
drug_get_schedule(din="02241007")
drug_get_therapeutic_class(din="02241007")
```

## Common Gotchas

- **Multiple DINs per drug** — a drug with 3 strengths (10mg, 20mg, 40mg) has 3 DINs
- **Generic equivalents have different DINs** — Lipitor and atorvastatin have different DINs
- **Cancelled drugs retain their DIN** — the DIN may still exist but status = "CANCELLED"
- **DINs are Canada-specific** — US NDC codes and UK PLs are different numbering systems

## DIN vs NPN vs DIN-HM

Health Canada uses different identification numbers for different product types:
- **DIN** — prescription and OTC drugs (Drug Identification Number)
- **NPN** — natural health products (Natural Product Number)
- **DIN-HM** — homeopathic medicines (Drug Identification Number - Homeopathic Medicine)

The Drug Product Database only covers **DIN** products.
"""


@resource(
    "docs://drug/search-tips",
    mime_type="text/markdown",
    name="drug_search_tips",
    title="Tips for Searching the Health Canada Drug Product Database",
)
def drug_search_tips() -> str:
    """Tips for searching the Health Canada Drug Product Database effectively.

    Covers brand name vs generic name searches, company searches, and DIN lookups.
    """
    return """# Health Canada Drug Database: Search Tips

## Brand Name vs Generic Name

The database contains both brand-name and generic products:
- **Brand name:** `drug_search(query="Tylenol")` — finds the Janssen/J&J product
- **Generic name:** `drug_search(query="acetaminophen")` — finds ALL products with this ingredient

When searching generics, expect many results (e.g., acetaminophen has 100+ DINs).
Use `drug_get_therapeutic_class` to narrow by class if needed.

## Searching by Company

```
drug_search_companies(query="Pfizer")
```

This finds the company record. Then search:
```
drug_search(query="Pfizer", company=True)
```

## Exact DIN Lookup

If you have a DIN, skip search entirely:
```
drug_get_details(din="02241007")
```

This is faster and more precise than searching.

## Handling Slow Responses

The Drug API can be slow (up to 45 seconds for broad searches).
The mcp-canada module enforces a 60-second timeout automatically.
Broad searches like `drug_search(query="a")` will timeout — be specific.

## Common Search Patterns

| Goal | Tool | Parameter |
|------|------|-----------|
| Find by brand name | `drug_search` | `query="Lipitor"` |
| Find all generics | `drug_search` | `query="atorvastatin"` |
| Find by DIN | `drug_get_details` | `din="02241007"` |
| Find by company | `drug_search_companies` | `query="Pfizer"` |
| Check market status | `drug_get_status` | `din="02241007"` |
| Check schedule | `drug_get_schedule` | `din="02241007"` |

## Interpreting Results

- `status: "MARKETED"` — currently sold in Canada
- `status: "APPROVED"` — approved but not confirmed as marketed
- `status: "CANCELLED"` — no longer authorized; do not use for active prescriptions
- `status: "DORMANT"` — authorization maintained but not marketed

For clinical decisions, always verify status with drug_get_status.
"""


# ---------------------------------------------------------------------------
# Template resources (template://)
# ---------------------------------------------------------------------------


@resource(
    "template://drug/medication-report",
    mime_type="text/markdown",
    name="drug_medication_report_template",
    title="Medication Profile Report Template",
)
def drug_medication_report_template() -> str:
    """Template for formatting a Health Canada drug product medication profile.

    Replace {placeholder} values with actual data from drug_get_details,
    drug_get_ingredients, and drug_get_routes before presenting to the user.
    """
    return """# Medication Profile: {drug_name}

**DIN:** {din}
**Status:** {market_status}
**Manufacturer:** {company_name}
**Schedule:** {schedule}

## Drug Information

- **Brand Name:** {brand_name}
- **Generic Name:** {generic_name}
- **Dosage Form:** {dosage_form}
- **Strength:** {strength}
- **Route(s) of Administration:** {routes}

## Active Ingredients

| Ingredient | Strength | Unit |
|-----------|---------|------|
{active_ingredient_rows}

## Non-Medicinal Ingredients

{non_medicinal_ingredients}

## Therapeutic Classification

- **ATC Code:** {atc_code}
- **Class:** {therapeutic_class}

## Market Status

- **Current Status:** {market_status}
- **Approval Date:** {approval_date}
- **Last Status Change:** {status_date}

## Source

Health Canada Drug Product Database (DPD)
Retrieved: {retrieval_timestamp}
"""
