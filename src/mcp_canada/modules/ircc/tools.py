"""IRCC Immigration open data tool functions.

Provides 10 ircc_ MCP tools for querying Immigration, Refugees and Citizenship
Canada (IRCC) open data. Each tool fetches parsed XLSX data via the client
layer and returns a standard _meta envelope.

Privacy note: IRCC suppresses values between 0-5 (shown as null) and rounds all
other values to the nearest multiple of 5.
"""

from typing import Literal

import httpx
from fastmcp.tools import tool

from mcp_canada.modules.ircc.client import (
    fetch_afghan,
    fetch_adhoc_pr,
    fetch_asylum,
    fetch_citizenship,
    fetch_ee_admissions,
    fetch_ee_invited,
    fetch_ops,
    fetch_permanent_residents,
    fetch_study_permits,
    fetch_tr_to_pr,
    fetch_work_permits_imp,
    fetch_work_permits_tfwp,
)
from mcp_canada.modules.ircc.constants import DATASET_REGISTRY
from mcp_canada.shared.envelope import make_error, make_response
from mcp_canada.shared.reshape import reshape_temporal_columns

_API_NAME = "IRCC Open Data"
_API_BASE = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/"


def _registry_url(dataset_key: str, breakdown: str, lang: str) -> str:
    """Look up the download URL from DATASET_REGISTRY. Returns empty string if missing."""
    try:
        return DATASET_REGISTRY[dataset_key][breakdown].get(lang, "")
    except KeyError:
        return _API_BASE


# ---------------------------------------------------------------------------
# Tool 1: Permanent residents
# ---------------------------------------------------------------------------

@tool
async def ircc_get_permanent_residents(
    breakdown: Literal[
        "country", "province", "gender", "age", "cma", "noc",
        "country_category", "csd", "adoptions"
    ] = "country",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC permanent resident admissions data by breakdown dimension.

    Note: Values between 0-5 are suppressed (shown as null) and all other
    values are rounded to the nearest multiple of 5 for privacy protection.
    Use for: permanent residents, immigration admissions, PR by country, province, gender, age, occupation NOC, CMA, CSD, adoptions, IRCC statistics.
    Keywords: permanent residents, PR, immigration, admissions, country, province, territory, gender, age, category, CMA, NOC, CSD, adoptions, IRCC, Canada, citizenship, immigration category.
    """
    try:
        rows, cached = await fetch_permanent_residents(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("pr", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 2: Study permits
# ---------------------------------------------------------------------------

@tool
async def ircc_get_study_permits(
    breakdown: Literal[
        "country", "province_level", "gender", "annual_country", "annual_province"
    ] = "country",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC study permit issuance data by breakdown dimension.

    Covers international students who received study permits in Canada.
    Use for: study permits, international students, student visas, education, student immigration by country province gender, IRCC study data.
    Keywords: study permit, international student, student visa, education, study, school, university, college, country, province, gender, IRCC, immigration, academic, enrollment.
    """
    try:
        rows, cached = await fetch_study_permits(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("study", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 3: Work permits (IMP + TFWP combined)
# ---------------------------------------------------------------------------

@tool
async def ircc_get_work_permits(
    permit_type: Literal["imp", "tfwp"] = "imp",
    breakdown: str = "province_program",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC work permit data for IMP (International Mobility Program) or TFWP (Temporary Foreign Worker Program).

    IMP breakdowns: province_program, gender_skill, country, noc.
    TFWP breakdowns: province_program, country, gender_skill, noc.
    Use for: work permits, temporary workers, IMP, TFWP, foreign workers, labour mobility, work authorization, LMIA, international mobility.
    Keywords: work permit, temporary worker, IMP, TFWP, international mobility, foreign worker, LMIA, labour, province, NOC, occupation, skill, country, employment, Canada.
    """
    if permit_type not in ("imp", "tfwp"):
        return make_error(
            "INVALID_INPUT",
            f"Invalid permit_type {permit_type!r}. Valid: ['imp', 'tfwp']",
            lang=lang,
        )

    dataset_key = "work_imp" if permit_type == "imp" else "work_tfwp"
    fetch_fn = fetch_work_permits_imp if permit_type == "imp" else fetch_work_permits_tfwp

    try:
        rows, cached = await fetch_fn(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url(dataset_key, breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 4: Express Entry (admissions + invited candidates combined)
# ---------------------------------------------------------------------------

@tool
async def ircc_get_express_entry(
    stream: Literal["admissions", "invited"] = "admissions",
    breakdown: str = "gender",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC Express Entry data for admissions or invited candidates.

    Admissions breakdowns: gender, category, country, age, occupation.
    Invited breakdowns: destination, score, country, age, education.
    Use for: Express Entry, EE, immigration draw, CRS score, FSW, CEC, FSWP, PNP, invited candidates, ITAs, admissions by stream.
    Keywords: Express Entry, EE, CRS, draw, FSW, CEC, federal skilled worker, Canadian experience class, PNP, ITA, invitation, admissions, category, score, country, gender, age, IRCC.
    """
    if stream not in ("admissions", "invited"):
        return make_error(
            "INVALID_INPUT",
            f"Invalid stream {stream!r}. Valid: ['admissions', 'invited']",
            lang=lang,
        )

    dataset_key = "ee_admissions" if stream == "admissions" else "ee_invited"
    fetch_fn = fetch_ee_admissions if stream == "admissions" else fetch_ee_invited

    try:
        rows, cached = await fetch_fn(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url(dataset_key, breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 5: TR-to-PR transitions
# ---------------------------------------------------------------------------

@tool
async def ircc_get_tr_to_pr(
    breakdown: Literal["study_permit", "imp", "tfwp", "pgwp"] = "study_permit",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC data on temporary residents who transitioned to permanent residence.

    Covers transitions from study permit holders, IMP, TFWP, and PGWP streams.
    Use for: TR to PR, temporary to permanent, pathway to PR, study to permanent, PGWP to PR, immigration transition, IRCC transition data.
    Keywords: TR to PR, temporary resident, permanent resident, transition, pathway, study permit, PGWP, post-graduation, IMP, TFWP, immigration, Canada, residence, status change.
    """
    try:
        rows, cached = await fetch_tr_to_pr(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("tr_to_pr", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 6: Asylum claimants
# ---------------------------------------------------------------------------

@tool
async def ircc_get_asylum(
    breakdown: Literal["province_office", "province_age", "province_gender"] = "province_office",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC asylum claimant data by province and demographic breakdown.

    Covers refugee protection claims received at offices across Canada.
    Use for: asylum seekers, refugee claimants, asylum claims, refugee protection, IRB, IRCC asylum data, refugee by province, claimant demographics.
    Keywords: asylum, refugee, claimant, IRB, refugee protection, province, office, age, gender, IRCC, Canada, humanitarian, immigration, refugee claim, protection.
    """
    try:
        rows, cached = await fetch_asylum(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("asylum", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 7: Operational processing data
# ---------------------------------------------------------------------------

@tool
async def ircc_get_ops(
    breakdown: Literal[
        "pr_intake", "copr_issued", "study_processed",
        "tr_processed", "trv_intake", "tr_approved",
        "trv_v1_approved"
    ] = "pr_intake",
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC operational processing statistics (monthly snapshots).

    Covers PR intake, COPR issued, study permit processing, TR processing,
    visitor visa intake, TR approvals, and visitor visa V-1 approvals.
    No year filter — data is monthly.
    Use for: IRCC processing times, application intake, operational stats, PR applications, study permit processing, visitor visa, TR approvals, COPR, V-1 visa.
    Keywords: IRCC operations, processing, intake, application, PR intake, COPR, study permit, TR processing, visitor visa, TRV, V-1, approval, monthly, statistics, backlog.
    """
    try:
        rows, cached = await fetch_ops(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("ops", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 8: Afghan refugees
# ---------------------------------------------------------------------------

@tool
async def ircc_get_afghan(
    breakdown: Literal["gender", "age", "education", "language"] = "gender",
    year: int | None = None,
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC data on Afghan refugees admitted to Canada.

    Covers gender, age group, education level, and official language ability.
    Use for: Afghan refugees, Operation Afghan Allies, Afghan evacuation, refugee resettlement, Afghanistan immigration, IRCC Afghan data, resettlement demographics.
    Keywords: Afghan, Afghanistan, refugee, resettlement, evacuation, gender, age, education, language, Operation Afghan Allies, IRCC, immigration, humanitarian, settlement.
    """
    try:
        rows, cached = await fetch_afghan(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, year=year, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("afghan", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 9: Ad-hoc historical PR data (1980-2023, English-only)
# ---------------------------------------------------------------------------

@tool
async def ircc_get_adhoc_pr(
    breakdown: Literal[
        "category_1980", "country_1980", "province_cat_2000", "province_citz_2000"
    ] = "category_1980",
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC ad-hoc historical permanent resident data (1980-2023).

    Note: These files are English-only. Requesting lang='fr' will return an error.
    Note: Legacy XLS format — requires xlrd (pip install mcp-canada[ircc]).
    Use for: historical immigration trends, long-term PR data, 1980s 1990s 2000s immigration, historical permanent residents by category country province.
    Keywords: historical immigration, permanent residents 1980, PR trends, long-term, category, country of birth, province, 1980 1990 2000 2010, IRCC history, immigration statistics, adhoc, legacy.
    """
    try:
        rows, cached = await fetch_adhoc_pr(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("adhoc_pr", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 10: New Canadian citizens
# ---------------------------------------------------------------------------

@tool
async def ircc_get_citizenship(
    breakdown: Literal["country"] = "country",
    recent: int | None = None,
    filter: str | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC new Canadian citizens data by country of birth (monthly).

    Covers persons granted Canadian citizenship, broken down by source country.
    Use for: citizenship, naturalization, new citizens, country of birth, Canadian citizenship grants, IRCC citizenship data.
    Keywords: citizenship, naturalization, new citizens, country of birth, Canadian, granted, persons, IRCC, immigration, monthly, source country.
    """
    try:
        rows, cached = await fetch_citizenship(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    return make_response(
        reshape_temporal_columns(rows, recent=recent, filter_value=filter),
        api_name=_API_NAME,
        api_url=_registry_url("citizenship", breakdown, lang),
        cached=cached,
        lang=lang,
    )


# ---------------------------------------------------------------------------
# Tool 11: List all available datasets
# ---------------------------------------------------------------------------

@tool
async def ircc_list_datasets(
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """List all available IRCC open data datasets with their breakdown dimensions.

    Returns a structured catalogue of all dataset categories (PR, study permits,
    work permits, Express Entry, asylum, etc.) and the valid breakdown keys for
    each. No network call — reads from the local registry.
    Use for: discover IRCC datasets, list available breakdowns, what IRCC data is available, immigration data catalogue, IRCC API options.
    Keywords: IRCC datasets, available data, breakdown, catalogue, list, permanent residents, study permits, work permits, Express Entry, asylum, operations, Afghan, adhoc, immigration options.
    """
    dataset_descriptions = {
        "pr": "Permanent resident admissions",
        "study": "Study permit issuances",
        "work_imp": "Work permits — International Mobility Program (IMP)",
        "work_tfwp": "Work permits — Temporary Foreign Worker Program (TFWP)",
        "ee_admissions": "Express Entry admissions",
        "ee_invited": "Express Entry invited candidates (ITAs issued)",
        "tr_to_pr": "Temporary resident to permanent resident transitions",
        "asylum": "Asylum claimants",
        "ops": "Operational processing statistics (monthly snapshots)",
        "citizenship": "New Canadian citizens by country of birth (monthly)",
        "afghan": "Afghan refugees admitted to Canada",
        "adhoc_pr": "Ad-hoc historical PR data 1980-2023 (English-only)",
    }

    entries = []
    for dataset_key, breakdowns in DATASET_REGISTRY.items():
        langs_available = sorted({
            lang_code
            for bd_langs in breakdowns.values()
            for lang_code in bd_langs
        })
        entries.append({
            "dataset": dataset_key,
            "description": dataset_descriptions.get(dataset_key, dataset_key),
            "breakdowns": sorted(breakdowns.keys()),
            "languages": langs_available,
        })

    return make_response(
        entries,
        api_name=_API_NAME,
        api_url=_API_BASE,
        cached=False,
        lang=lang,
    )
