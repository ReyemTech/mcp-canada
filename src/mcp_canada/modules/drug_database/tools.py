"""Drug Product Database @tool functions for Health Canada's drug product API.

Provides 8 intent-based MCP tools for querying Health Canada Drug Product Database:
drug search, comprehensive details, active ingredients, routes of administration,
schedule classification, ATC therapeutic class, market status, and company search.

Each tool follows the 5-file module pattern:
- Standalone @tool decorator (NOT @mcp.tool)
- Bilingual lang: en|fr parameter (I18N-01)
- make_response / make_error envelope for all return paths
- BM25-optimized docstrings with Keywords: and Use for: lines

IMPORTANT: drug_code vs DIN
- DIN (Drug Identification Number): the public identifier on a drug package (e.g. "00559407")
- drug_code: the internal numeric database ID used for all detail API lookups
- Use drug_search to get drug_code, then use drug_code for all detail tools
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.modules.drug_database.client import (
    fetch_companies,
    fetch_drug_details,
    fetch_drug_search,
    fetch_ingredients,
    fetch_routes,
    fetch_schedule,
    fetch_status,
    fetch_therapeutic_class,
)
from mcp_canada.modules.drug_database.constants import BASE_URL
from mcp_canada.shared.envelope import INVALID_INPUT, make_error, make_response, upstream_guard

# API name and base URL for _meta envelope
_API_NAME = "Drug Product Database"
_API_URL = BASE_URL


# ---------------------------------------------------------------------------
# Tool 1: Drug search
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_search(
    brand_name: str | None = None,
    din: str | None = None,
    company: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Health Canada's Drug Product Database for drug products.

    At least one of brand_name, din, or company is required. Returns a list
    of matching drug products including their drug_code (internal database ID)
    which is needed for all detail lookups (not the DIN).

    Use for: finding Canadian drug products by brand name, DIN number, or
    manufacturer company name. Returns drug_code required for detail tools.
    Keywords: drug, search, brand, name, din, company, medication, pharmaceutical,
    health canada, product, canadian, find, lookup, drug identification number.
    """
    if brand_name is None and din is None and company is None:
        return make_error(
            INVALID_INPUT,
            "At least one of brand_name, din, or company is required.",
            lang=lang,
            suggestions=[
                "Provide brand_name to search by drug brand name (e.g. 'TYLENOL')",
                "Provide din to search by Drug Identification Number (e.g. '00559407')",
                "Provide company to search by manufacturer name (e.g. 'PFIZER')",
            ],
        )

    data, cached = await fetch_drug_search(
        brandname=brand_name,
        din=din,
        company=company,
    )

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Drug comprehensive details (parallel fetch)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_details(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get comprehensive details for a drug product in one call.

    Fetches active ingredients, routes of administration, schedule classification,
    ATC therapeutic class, and market status in parallel using a single drug_code.
    Returns a flat sections dict. Use drug_search first to obtain the drug_code.

    Use for: getting full drug product details including ingredients, routes, schedule,
    ATC classification, and market status in a single efficient call.
    Keywords: drug, details, comprehensive, ingredients, routes, schedule, atc,
    therapeutic, status, drug_code, health canada, full, complete, all.
    """
    sections, cached = await fetch_drug_details(drug_code)

    return make_response(
        sections,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Active ingredients
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_ingredients(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get active ingredients for a Health Canada drug product.

    Returns ingredient names, strength, strength unit, dosage value, and dosage unit.
    Requires drug_code (internal database ID from drug_search), not the DIN.

    Use for: looking up the active ingredients and their dosages in a specific
    Canadian drug product identified by its drug_code.
    Keywords: ingredients, active, substance, strength, dosage, formulation,
    drug_code, health canada, composition, drug product, pharmaceutical.
    """
    data, cached = await fetch_ingredients(drug_code)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Routes of administration
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_routes(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get routes of administration for a Health Canada drug product.

    Returns how the drug is administered (e.g. ORAL, TOPICAL, INTRAVENOUS).
    Requires drug_code (internal database ID from drug_search), not the DIN.

    Use for: finding out how a specific Canadian drug product is administered,
    such as oral, topical, intravenous, or subcutaneous routes.
    Keywords: route, administration, oral, topical, intravenous, subcutaneous,
    drug_code, health canada, how to take, delivery method, dosage form.
    """
    data, cached = await fetch_routes(drug_code)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: Company search
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_search_companies(
    company_name: str,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search for pharmaceutical companies in Health Canada's Drug Product Database.

    Returns company details including name, type, city, province, and country.

    Use for: finding pharmaceutical companies registered in Health Canada's Drug
    Product Database by company name, including manufacturers and distributors.
    Keywords: company, manufacturer, pharmaceutical, distributor, owner, health canada,
    drug company, search, find, canadian, registration.
    """
    data, cached = await fetch_companies(company_name)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Schedule classification
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_schedule(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get schedule classification for a Health Canada drug product.

    Returns the regulatory schedule (e.g. OTC, prescription, controlled drug).
    Requires drug_code (internal database ID from drug_search), not the DIN.

    Use for: finding out the regulatory schedule classification of a Canadian
    drug product — whether it is OTC, prescription-only, or a controlled substance.
    Keywords: schedule, otc, prescription, controlled, regulatory, classification,
    drug_code, health canada, over the counter, rx, drug scheduling.
    """
    data, cached = await fetch_schedule(drug_code)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Therapeutic class (ATC)
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_therapeutic_class(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get ATC therapeutic classification for a Health Canada drug product.

    Returns the WHO Anatomical Therapeutic Chemical (ATC) classification code
    and AHFS classification. Requires drug_code (internal database ID from
    drug_search), not the DIN.

    Use for: finding the therapeutic category and ATC classification code for
    a Canadian drug product to understand its pharmacological class.
    Keywords: atc, therapeutic, class, classification, anatomical, chemical,
    drug_code, health canada, pharmacological, ahfs, category, drug class.
    """
    data, cached = await fetch_therapeutic_class(drug_code)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Market status
# ---------------------------------------------------------------------------

@tool
@upstream_guard(_API_NAME)
async def drug_get_status(
    drug_code: int,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get market status for a Health Canada drug product.

    Returns current market status (e.g. MARKETED, CANCELLED, DORMANT) and
    history date. Requires drug_code (internal database ID from drug_search),
    not the DIN.

    Use for: checking whether a specific Canadian drug product is currently
    marketed, cancelled, or dormant in the Canadian market.
    Keywords: status, market, marketed, cancelled, dormant, history,
    drug_code, health canada, availability, approval, current status.
    """
    data, cached = await fetch_status(drug_code)

    return make_response(
        data,
        api_name=_API_NAME,
        api_url=_API_URL,
        cached=cached,
        lang=lang,
    )
