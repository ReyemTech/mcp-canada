"""IRCC client functions: one per dataset category.

Each function looks up the correct URL from DATASET_REGISTRY and delegates to
fetch_and_parse(). Raises ValueError for unknown breakdown keys with a list of
valid options. Network and parsing errors propagate to the tool layer.
"""

from mcp_canada.modules.ircc.constants import DATASET_REGISTRY
from mcp_canada.shared.parsers import fetch_and_parse


async def _fetch_dataset(
    dataset_key: str,
    breakdown: str,
    lang: str,
) -> tuple[list[dict], bool]:
    """Private helper: look up URL from registry and call fetch_and_parse.

    Args:
        dataset_key: Top-level registry key (e.g. "pr", "study").
        breakdown: Breakdown variant key (e.g. "country", "province").
        lang: Language code ("en" or "fr").

    Returns:
        (rows, was_cached) tuple.

    Raises:
        ValueError: If breakdown or lang is not found in the registry for this dataset.
    """
    registry = DATASET_REGISTRY[dataset_key]
    if breakdown not in registry:
        valid = sorted(registry.keys())
        raise ValueError(
            f"Unknown breakdown {breakdown!r} for {dataset_key}. Valid: {valid}"
        )
    urls = registry[breakdown]
    if lang not in urls:
        valid_langs = sorted(urls.keys())
        raise ValueError(
            f"Language {lang!r} not available for {dataset_key}/{breakdown}. "
            f"Valid: {valid_langs}"
        )
    return await fetch_and_parse(urls[lang])


async def fetch_permanent_residents(
    breakdown: str = "country",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC permanent residents data for the given breakdown."""
    return await _fetch_dataset("pr", breakdown, lang)


async def fetch_study_permits(
    breakdown: str = "country",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC study permits data for the given breakdown."""
    return await _fetch_dataset("study", breakdown, lang)


async def fetch_work_permits_imp(
    breakdown: str = "province_program",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC work permits (IMP) data for the given breakdown."""
    return await _fetch_dataset("work_imp", breakdown, lang)


async def fetch_work_permits_tfwp(
    breakdown: str = "province_program",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC work permits (TFWP) data for the given breakdown."""
    return await _fetch_dataset("work_tfwp", breakdown, lang)


async def fetch_ee_admissions(
    breakdown: str = "gender",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC Express Entry admissions data for the given breakdown."""
    return await _fetch_dataset("ee_admissions", breakdown, lang)


async def fetch_ee_invited(
    breakdown: str = "destination",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC Express Entry invited candidates data for the given breakdown."""
    return await _fetch_dataset("ee_invited", breakdown, lang)


async def fetch_tr_to_pr(
    breakdown: str = "study_permit",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC TR-to-PR transitions data for the given breakdown."""
    return await _fetch_dataset("tr_to_pr", breakdown, lang)


async def fetch_asylum(
    breakdown: str = "province_office",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC asylum claimants data for the given breakdown."""
    return await _fetch_dataset("asylum", breakdown, lang)


async def fetch_ops(
    breakdown: str = "pr_intake",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC operational processing data for the given breakdown."""
    return await _fetch_dataset("ops", breakdown, lang)


async def fetch_afghan(
    breakdown: str = "gender",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC Afghan refugees data for the given breakdown."""
    return await _fetch_dataset("afghan", breakdown, lang)


async def fetch_adhoc_pr(
    breakdown: str = "category_1980",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch IRCC ad-hoc historical PR data (1980–2023) for the given breakdown.

    Note: Ad-hoc PR files are English-only. Requesting lang='fr' raises ValueError.
    Requires xlrd (optional): pip install mcp-canada[ircc]
    """
    return await _fetch_dataset("adhoc_pr", breakdown, lang)
