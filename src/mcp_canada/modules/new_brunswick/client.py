"""New Brunswick module client — async functions returning (data, was_cached) tuples.

Wave 0 (this file) implements: three module-level limiters (federal CKAN, GeoNB,
511) plus a fourth for gnb.socrata.com (checkpoint option-a — a fourth upstream
surface joined the discovery side, Rule 2: rate limiting is a correctness
requirement per CLAUDE.md, not optional), five fully-implemented private
helpers (`_api_get`, `_build_fq`, `_shape_dataset`, `_geonb_query`, `_511_get`),
`fetch_crown_land` (the Task 1 tracer, fully implemented), and every remaining
downstream function as a `raise NotImplementedError` stub with a LOCKED
signature. Plans 02-06 fill bodies only — they never edit a signature here.

  - Plan 02 (federal CKAN + gnb.socrata.com): fetch_search_datasets,
    fetch_dataset_details, fetch_query_dataset, fetch_organizations,
    fetch_categories, fetch_gnb_socrata_search, fetch_gnb_socrata_query
  - Plan 04 (GeoNB discovery + flood/water): fetch_geonb_services,
    fetch_geonb_service_layers, fetch_geonb_layer_features,
    fetch_flood_hazard_areas, fetch_historical_floods, fetch_wetlands,
    fetch_contaminated_sites
  - Plan 05 (parcels/civic address): fetch_parcels, fetch_civic_addresses
  - Plan 06 (health/education + 511): fetch_health_facilities,
    fetch_public_schools, fetch_road_events, fetch_winter_road_conditions,
    fetch_traffic_cameras

CHECKPOINT (option-a): fetch_mineral_occurrences and fetch_provincial_parks
are NOT stubbed here — both dropped to the long tail, reachable through
fetch_geonb_layer_features / nb_query_geonb_layer.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from mcp_canada.shared import arcgis_hub, socrata
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.errors import InvalidInput, NotFound, UpstreamData
from mcp_canada.shared.http import api_get
from mcp_canada.shared.parsers import fetch_and_parse
from mcp_canada.shared.rate_limiter import get_limiter

from .constants import (
    CACHE_KEY_PREFIX,
    CACHE_TTL_LIVE,
    CACHE_TTL_META,
    CACHE_TTL_SEARCH,
    CIVIC_ADDRESS_LAYER,
    CIVIC_ADDRESS_SERVICE,
    CKAN_BASE_URL,
    CONTAMINATED_SITES_LAYER,
    CONTAMINATED_SITES_SERVICE,
    CROWN_LAND_FIELDS,
    CROWN_LAND_LAYER,
    CROWN_LAND_SERVICE,
    FILTER_REQUIRED_TOOLS,
    FIVE11_BASE_URL,
    FIVE11_KEY_ENV,
    FLOOD_HAZARD_LAYER,
    FLOOD_HAZARD_SERVICE,
    GEONB_BASE_URL,
    GEONB_EXCLUDED_SERVICES,
    GNB_SOCRATA_DOMAIN,
    HEALTH_FACILITIES_SERVICE,
    HEALTH_FACILITY_LAYERS,
    HISTORICAL_FLOODS_1973_LAYER,
    HISTORICAL_FLOODS_LAYER,
    HISTORICAL_FLOODS_SERVICE,
    MAX_RECORDS,
    NB_ORG_FQ,
    NB_ORG_NAME,
    PARCELS_LAYER,
    PARCELS_SERVICE,
    PUBLIC_SCHOOLS_SERVICE,
    RATE_GROUP_511,
    RATE_GROUP_CKAN,
    RATE_GROUP_GEONB,
    RATE_GROUP_SOCRATA,
    RATE_LIMIT_511,
    RATE_LIMIT_CKAN,
    RATE_LIMIT_GEONB,
    RATE_LIMIT_SOCRATA,
    SCHOOL_SECTOR_LAYERS,
    USER_AGENT,
    WETLANDS_LAYER,
    WETLANDS_SERVICE,
)
from .schemas import (  # noqa: F401 — re-exported for downstream plans, matching the
    # saskatchewan/alberta/manitoba convention (IN-01): client.py builds and
    # returns plain dicts throughout — these models document the live GeoNB
    # field shapes (21-SPIKE.md §4) and federal-CKAN/gnb.socrata.com/511
    # response shapes without enforcing them on the hot path.
    NB511Camera,
    NB511Event,
    NB511WinterRoad,
    NBCategory,
    NBCivicAddress,
    NBContaminatedSite,
    NBCrownLandParcel,
    NBDatasetDetails,
    NBDatasetSummary,
    NBFloodHazardArea,
    NBGeoNBLayer,
    NBGeoNBService,
    NBHealthFacility,
    NBHistoricalFlood,
    NBMineralOccurrence,
    NBOrganization,
    NBParcel,
    NBProvincialPark,
    NBPublicSchool,
    NBSocrataDatasetSummary,
    NBWetland,
)

__all__ = [
    # Private helpers (fully implemented in Wave 0)
    "_api_get",
    "_build_fq",
    "_shape_dataset",
    "_geonb_query",
    "_511_get",
    "Five11NotConfigured",
    # Federal CKAN discovery (Plan 02)
    "fetch_search_datasets",
    "fetch_dataset_details",
    "fetch_query_dataset",
    "fetch_organizations",
    "fetch_categories",
    # gnb.socrata.com discovery (Plan 02, checkpoint option-a)
    "fetch_gnb_socrata_search",
    "fetch_gnb_socrata_query",
    # GeoNB discovery + flood/water (Plan 04)
    "fetch_geonb_services",
    "fetch_geonb_service_layers",
    "fetch_geonb_layer_features",
    "fetch_flood_hazard_areas",
    "fetch_historical_floods",
    "fetch_wetlands",
    "fetch_contaminated_sites",
    # Crown land — Task 1 tracer (fully implemented)
    "fetch_crown_land",
    # Parcels / civic address (Plan 05)
    "fetch_parcels",
    "fetch_civic_addresses",
    # Health / education + 511 (Plan 06)
    "fetch_health_facilities",
    "fetch_public_schools",
    "fetch_road_events",
    "fetch_winter_road_conditions",
    "fetch_traffic_cameras",
]


# ---------------------------------------------------------------------------
# Exception for missing 511 key
# ---------------------------------------------------------------------------


class Five11NotConfigured(Exception):
    """Raised when NEW_BRUNSWICK_511_KEY env var is not set.

    The message states only that the env var is unset and links 511.gnb.ca —
    it MUST NOT interpolate the value read from the environment (T-21-02).
    """


# ---------------------------------------------------------------------------
# Module-level limiters
# ---------------------------------------------------------------------------

_ckan_limiter = get_limiter(RATE_GROUP_CKAN, RATE_LIMIT_CKAN)
_geonb_limiter = get_limiter(RATE_GROUP_GEONB, RATE_LIMIT_GEONB)
_socrata_limiter = get_limiter(RATE_GROUP_SOCRATA, RATE_LIMIT_SOCRATA)
_511_limiter = get_limiter(RATE_GROUP_511, RATE_LIMIT_511)


# ---------------------------------------------------------------------------
# Private helpers — fully implemented (Wave 0)
# ---------------------------------------------------------------------------


async def _api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Federal CKAN Action API call against open.canada.ca (organization:nb).

    Modeled on alberta/client.py:_api_get. `api_get` returns already-parsed
    JSON — do NOT call `.raise_for_status()` or `.json()` on its return.
    Unwraps the CKAN `{"success": ..., "result": ...}` envelope and raises
    `UpstreamData` (-> UPSTREAM_ERROR, never the caller's fault) when the
    envelope reports failure or is not a dict.

    Args:
        path: Action API path (e.g. "package_search") relative to
            `{CKAN_BASE_URL}/action/`.
        params: Optional query parameters.

    Returns:
        The unwrapped CKAN `result` field (dict OR list depending on action).

    Raises:
        UpstreamData: When the CKAN envelope is missing, malformed, or reports
            `success: false`.
    """
    url = f"{CKAN_BASE_URL}/action/{path}"
    await _ckan_limiter.acquire()
    envelope = await api_get(url, params or {}, headers={"User-Agent": USER_AGENT})
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise UpstreamData(f"federal CKAN returned an unusable envelope for {path}")
    return envelope.get("result", {})


def _validate_extra_fq(extra_fq: str) -> None:
    """Reject a caller-supplied fq fragment that could break out of the
    parentheses `_build_fq` wraps around it (F1/T-21-04).

    WR-01's explicit parenthesization assumes `extra_fq` is a well-formed
    Lucene atom. That assumption does not hold for a fragment carrying its
    own unbalanced parenthesis: `"*:* ) OR (*:*"` composes into
    `"(organization:nb) AND (*:* ) OR (*:*)"`, whose trailing `OR (*:*)`
    matches every non-NB dataset regardless of the NB clause — the wrapping
    parens themselves are broken out of, not merely reinterpreted. An
    unbalanced double quote is rejected for the same reason: it changes how
    Solr's Lucene parser tokenizes everything composed after it.

    Args:
        extra_fq: The caller-supplied fq fragment, already known truthy.

    Raises:
        InvalidInput: When parentheses or double quotes are unbalanced.
    """
    # A plain count comparison is not enough: "*:* ) OR (*:*" has one "("
    # and one ")" — equal counts — but the ")" comes BEFORE the "(", so it
    # still closes `_build_fq`'s own wrapping paren early. Track nesting
    # depth left-to-right instead; depth must never go negative and must
    # return to exactly 0.
    depth = 0
    for char in extra_fq:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise InvalidInput(
                    f"extra_fq closes a parenthesis that was never opened "
                    f"and cannot be safely composed into the NB-scoped "
                    f"filter query: {extra_fq!r}"
                )
    if depth != 0:
        raise InvalidInput(
            f"extra_fq has unbalanced parentheses and cannot be safely "
            f"composed into the NB-scoped filter query: {extra_fq!r}"
        )
    if extra_fq.count('"') % 2 != 0:
        raise InvalidInput(
            f"extra_fq has an unbalanced double quote and cannot be safely "
            f"composed into the NB-scoped filter query: {extra_fq!r}"
        )


def _build_fq(extra_fq: str | None) -> str:
    """Compose the fq (filter query) clause for federal CKAN discovery calls.

    The NB organization clause is always first and is NEVER caller-overridable
    (T-21-04) — no `organization` parameter is exposed to any discovery tool.

    WR-01: both clauses are wrapped in explicit parentheses. CKAN forwards
    `fq` straight to Solr's classic Lucene query parser, where mixing
    `AND`/`OR` without explicit grouping is a well-documented source of
    unintended operator precedence (`A AND B OR C` does not reliably parse
    as `A AND (B OR C)`). A caller-supplied fragment containing its own
    `OR` (e.g. `"*:* OR organization:xyz"`) could otherwise widen the
    result past the NB scope. Explicit grouping makes the composed clause
    require the NB clause regardless of what operators the fragment uses.

    F1: `_validate_extra_fq` rejects a fragment whose own unbalanced
    parentheses or quotes would break OUT of that wrapping — the case the
    WR-01 grouping alone does not cover, since it assumes `extra_fq` is a
    well-formed atom in the first place.

    Args:
        extra_fq: An optional caller-supplied fq fragment (e.g. a format or
            tag filter) to AND onto the NB clause.

    A whitespace-only fragment is treated as absent rather than composed:
    `"... AND (   )"` is not a valid Lucene clause and Solr answers it with
    HTTP 409, which would surface a caller mistake to the agent as
    `UPSTREAM_ERROR` — the misclassification ERR-01..ERR-07 exist to prevent.
    `extra_fq` is optional, so "nothing meaningful" means "no extra filter".

    Returns:
        `"organization:nb"` alone, or `"(organization:nb) AND ({extra_fq})"`.

    Raises:
        InvalidInput: When `extra_fq` has unbalanced parentheses or quotes.
    """
    if extra_fq and extra_fq.strip():
        _validate_extra_fq(extra_fq)
        return f"({NB_ORG_FQ}) AND ({extra_fq})"
    return NB_ORG_FQ


def _shape_dataset(raw: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    """Shape a raw federal CKAN dataset dict for token-efficient consumption.

    Copies the bilingual fallback chain from ckan/client.py:_shape_dataset
    verbatim (D-12, Pattern 2): prefer the requested language from
    `title_translated`/`notes_translated`, then their English key, then the
    plain `title`/`notes`. NB's separately-published FR/EN record pairs are
    handled correctly by this same chain — no deduplication (RESEARCH
    Pitfall 5): each CKAN record already carries only its own language.

    Args:
        raw: Raw dataset dict from federal CKAN package_show/package_search.
        lang: Language code ('en' or 'fr').

    Returns:
        Flat dict: id, name, title, description, organization, num_resources,
        tags, resources (capped to 10), metadata_modified.
    """
    title_translated: dict[str, str] | None = raw.get("title_translated")
    if title_translated:
        title = title_translated.get(lang) or title_translated.get("en") or raw.get("title")
    else:
        title = raw.get("title")

    notes_translated: dict[str, str] | None = raw.get("notes_translated")
    if notes_translated:
        description = notes_translated.get(lang) or notes_translated.get("en") or raw.get("notes")
    else:
        description = raw.get("notes")

    keywords_translated: dict[str, list[str]] | None = raw.get("keywords")
    if keywords_translated:
        keywords = keywords_translated.get(lang) or keywords_translated.get("en") or []
    else:
        keywords = []

    raw_resources: list[dict[str, Any]] = raw.get("resources") or []

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "title": title,
        "description": description,
        "organization": raw.get("organization"),
        "num_resources": len(raw_resources),
        "tags": [t.get("name") for t in (raw.get("tags") or []) if isinstance(t, dict)],
        "keywords": keywords,
        "resources": raw_resources[:10],
        "metadata_modified": raw.get("metadata_modified"),
    }


async def _geonb_query(
    service_url: str,
    layer_id: int,
    where: str | None = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
    limit: int = MAX_RECORDS,
    ttl: int = CACHE_TTL_META,
    cache_key: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Shared curated-tool helper: query a GeoNB MapServer layer via
    `shared/arcgis_hub.py:query_feature_service` (unchanged, D-05), rate
    limited and cached.

    Every curated GeoNB tool's client function delegates here rather than
    calling `arcgis_hub.query_feature_service` directly, so the limiter
    acquisition and cache-key convention live in one place.

    F2: `limit` is `query_feature_service`'s `max_records` argument, which
    REPLACES that function's own MAX_RECORDS default rather than being
    bounded by it — `MAX_RECORDS` otherwise only ever appears as a curated
    tool's `limit` *default*, never as an enforced cap. `1 <= limit <=
    MAX_RECORDS` is validated here, centrally, before any network call, so
    every curated GeoNB tool inherits the bound without repeating it —
    including `fetch_geonb_layer_features`'s own upper-bound pre-check,
    which is now a redundant (harmless) first line of defence rather than
    the only one.

    Raises:
        InvalidInput: When `limit` is not in `[1, MAX_RECORDS]`.

    Returns ({"features": [...], "count": N, "truncated": bool}, was_cached).
    """
    if not (1 <= limit <= MAX_RECORDS):
        raise InvalidInput(
            f"limit must be between 1 and {MAX_RECORDS}, got {limit}"
        )
    key = cache_key or f"{CACHE_KEY_PREFIX}geonb:{service_url}:{layer_id}:{where}:{out_fields}:{limit}"

    async def _fetch() -> dict[str, Any]:
        await _geonb_limiter.acquire()
        features, truncated = await arcgis_hub.query_feature_service(
            service_url,
            layer_id=layer_id,
            where=where,
            out_fields=out_fields,
            include_geometry=include_geometry,
            max_records=limit,
        )
        return {"features": features, "count": len(features), "truncated": truncated}

    return await cached_fetch(key, ttl, _fetch)


async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """NB 511 REST API v2 call. Returns raw JSON list.

    GATED: requires NEW_BRUNSWICK_511_KEY environment variable — verified live
    against `511.gnb.ca/api/v2/get/event`, which exists and returns
    `<Error><Message>Invalid Key</Message></Error>` when unkeyed (D-09).
    If the key is absent, raises `Five11NotConfigured` — the tool layer
    catches it and returns `make_error("NOT_CONFIGURED", ...)` (D-10, a
    normal envelope, not an exception path).

    Args:
        endpoint: 511 endpoint name (e.g. "event", "winterroadcondition",
            "camera").
        params: Optional extra query parameters.

    Returns:
        Raw JSON list from the 511 API.

    Raises:
        Five11NotConfigured: When NEW_BRUNSWICK_511_KEY is unset.
    """
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured(
            f"{FIVE11_KEY_ENV} not set. NB 511 requires an API key — see https://511.gnb.ca"
        )
    rows = await api_get(
        f"{FIVE11_BASE_URL}/{endpoint}",
        {**(params or {}), "key": key, "format": "json"},
        headers={"User-Agent": USER_AGENT},
    )
    return rows if isinstance(rows, list) else []


# ---------------------------------------------------------------------------
# Crown Land — Task 1 tracer (fully implemented)
# ---------------------------------------------------------------------------


async def fetch_crown_land(
    holder: int | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch New Brunswick Crown Land parcels from GeoNB_DNR_Crown_Land layer 3.

    Builds the WHERE clause server-side from the typed `holder` argument — never
    from a caller-supplied clause string. `holder` is a raw integer holder code
    with no server-exposed name domain (RESEARCH Pitfall 4).

    Returns ({"features": [...], "count": N, "truncated": bool}, was_cached).
    """
    where = f"HOLDER={holder}" if holder is not None else "1=1"
    cache_key = f"{CACHE_KEY_PREFIX}crown_land:{holder}:{limit}"
    return await _geonb_query(
        CROWN_LAND_SERVICE,
        layer_id=CROWN_LAND_LAYER,
        where=where,
        out_fields=CROWN_LAND_FIELDS,
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


# ---------------------------------------------------------------------------
# Federal CKAN discovery — Plan 02 fills bodies
# ---------------------------------------------------------------------------


async def fetch_search_datasets(
    query: str = "",
    extra_fq: str | None = None,
    limit: int = 10,
    offset: int = 0,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Search federal CKAN datasets filtered to organization:nb.

    `limit` is clamped to CKAN's 100-row maximum (floored at 1); `offset` is
    floored at 0. `fq` is always `_build_fq(extra_fq)` — the NB organization
    clause is first and is never caller-overridable (T-21-04).

    Returns ({"results": [...], "total": N, "limit": clamped_limit,
    "offset": clamped_offset}, was_cached) with each result shaped through
    `_shape_dataset(raw, lang)`. WR-02: the payload echoes the CLAMPED
    values actually sent upstream, not the caller's raw `limit`/`offset` —
    an agent computing the next page's offset from the raw values would
    otherwise be misled.
    """
    clamped_limit = max(1, min(limit, 100))
    clamped_offset = max(offset, 0)
    fq = _build_fq(extra_fq)
    cache_key = (
        f"{CACHE_KEY_PREFIX}search:{query}:{fq}:{clamped_limit}:{clamped_offset}:{lang}"
    )

    async def _fetch() -> dict[str, Any]:
        params = {
            "q": query,
            "rows": clamped_limit,
            "start": clamped_offset,
            "fq": fq,
        }
        result = await _api_get("package_search", params)
        raw_results = result.get("results") or []
        return {
            "results": [_shape_dataset(r, lang=lang) for r in raw_results],
            "total": int(result.get("count") or 0),
            "limit": clamped_limit,
            "offset": clamped_offset,
        }

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_dataset_details(
    dataset_id: str,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Fetch full details for a single federal CKAN dataset.

    Raises `NotFound` on an upstream 404 (package_show for an unknown id), OR
    when `package_show` resolves to a package outside the NB organization
    (G1). Unlike `package_search`, `package_show` takes a bare id/slug with
    no `fq` scoping at all — the earlier `extra_fq` hardening
    (`_build_fq`/`_validate_extra_fq`) protects only `package_search`, so a
    non-NB id was otherwise returned in full: orchestrator-verified LIVE that
    `dataset_id="6059da1d-e1da-4f2b-a420-b5c2a130eeaa"` returned an
    Environment Canada ("ec") dataset through a tool whose docstring states
    the NB filter "CANNOT be widened" (T-21-04). A missing or `None`
    `organization` key fails closed — treated as non-NB, not as NB by
    omission. `fetch_query_dataset` inherits this guard because it calls
    this function.

    Shaped through `_shape_dataset` plus resources (flattened to format,
    name, url, description), license_title, license_url, date_published,
    maintainer, frequency and spatial.
    """
    cache_key = f"{CACHE_KEY_PREFIX}details:{dataset_id}:{lang}"

    async def _fetch() -> dict[str, Any]:
        try:
            raw = await _api_get("package_show", {"id": dataset_id})
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise NotFound(f"NB dataset not found: {dataset_id}") from exc
            raise
        organization = raw.get("organization")
        org_name = organization.get("name") if isinstance(organization, dict) else None
        if org_name != NB_ORG_NAME:
            raise NotFound(f"NB dataset not found: {dataset_id}")
        shaped = _shape_dataset(raw, lang=lang)
        shaped["resources"] = [
            {
                "format": r.get("format"),
                "name": r.get("name"),
                "url": r.get("url"),
                "description": r.get("description"),
            }
            for r in (raw.get("resources") or [])
        ]
        shaped["license_title"] = raw.get("license_title")
        shaped["license_url"] = raw.get("license_url")
        shaped["date_published"] = raw.get("date_published")
        shaped["maintainer"] = raw.get("maintainer")
        shaped["frequency"] = raw.get("frequency")
        shaped["spatial"] = raw.get("spatial")
        return shaped

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


_PARSEABLE_RESOURCE_FORMATS: frozenset[str] = frozenset({"CSV", "XLSX", "XLS", "JSON", "GEOJSON"})


async def fetch_query_dataset(
    dataset_id: str,
    resource_index: int = 0,
    limit: int = 1000,
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """Query/parse a resource from a federal CKAN NB dataset.

    Selects `resources[resource_index]` from `fetch_dataset_details` and
    raises `InvalidInput` when the index is out of range. `limit` is
    rejected with `InvalidInput` when `<= 0` (WR-03), before any network
    call — `rows[:limit]` with a negative limit would otherwise silently
    drop the trailing `abs(limit)` rows instead of failing loudly, and
    `truncated: len(rows) > limit` would be nonsensically always True.
    CSV / XLSX / XLS / JSON / GEOJSON resources are routed through
    `fetch_and_parse` and truncated to `limit` rows. Every other format
    returns a metadata-only payload naming the download url — this NEVER
    raises for an unparseable format, it is a normal, describable outcome.
    """
    if limit <= 0:
        raise InvalidInput(
            f"nb_query_dataset limit must be greater than 0, got {limit}"
        )
    details, _ = await fetch_dataset_details(dataset_id, lang=lang)
    resources: list[dict[str, Any]] = details.get("resources") or []
    if not (0 <= resource_index < len(resources)):
        if resources:
            valid_range = f"0-{len(resources) - 1}"
        else:
            valid_range = "no resources available"
        raise InvalidInput(
            f"resource_index {resource_index} out of range for dataset {dataset_id} "
            f"(valid range: {valid_range})"
        )
    resource = resources[resource_index]
    fmt = (resource.get("format") or "").upper()
    url = resource.get("url") or ""
    cache_key = f"{CACHE_KEY_PREFIX}query:{dataset_id}:{resource_index}:{limit}"

    async def _fetch() -> dict[str, Any]:
        if fmt in _PARSEABLE_RESOURCE_FORMATS and url:
            rows, _cached = await fetch_and_parse(url, ttl=CACHE_TTL_SEARCH)
            return {
                "rows": rows[:limit],
                "resource": resource,
                "truncated": len(rows) > limit,
            }
        return {
            "rows": [],
            "resource": resource,
            "note": (
                f"Format '{fmt or 'unknown'}' is not machine-parseable by this server — "
                f"download directly from {url or '(no url provided)'}"
            ),
        }

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_organizations(
    lang: str = "en",
) -> tuple[list[dict[str, Any]], bool]:
    """List organizations among NB federal CKAN datasets.

    NB publishes under a single federal CKAN organization (organization:nb),
    so the useful decomposition is the publishing section (`org_section`),
    which is empty on most packages. One package_search call (rows=1000)
    aggregates the parent `org_title_at_publication` and every distinct
    non-empty `org_section` into `{name, name_fr, dataset_count}` entries.
    """
    cache_key = f"{CACHE_KEY_PREFIX}organizations:{lang}"

    async def _fetch() -> list[dict[str, Any]]:
        params = {"q": "", "rows": 1000, "start": 0, "fq": _build_fq(None)}
        result = await _api_get("package_search", params)
        raw_results = result.get("results") or []

        parent_title_en: str | None = None
        parent_title_fr: str | None = None
        section_counts: dict[str, dict[str, Any]] = {}

        for raw in raw_results:
            org_pub = raw.get("org_title_at_publication") or {}
            if isinstance(org_pub, dict):
                parent_title_en = parent_title_en or org_pub.get("en")
                parent_title_fr = parent_title_fr or org_pub.get("fr")

            section = raw.get("org_section") or {}
            if isinstance(section, dict):
                section_en = section.get("en")
                if section_en:
                    entry = section_counts.setdefault(
                        section_en,
                        {"name": section_en, "name_fr": section.get("fr"), "dataset_count": 0},
                    )
                    entry["dataset_count"] += 1

        organizations: list[dict[str, Any]] = [
            {
                "name": parent_title_en or "Government of New Brunswick",
                "name_fr": parent_title_fr or "Gouvernement du Nouveau-Brunswick",
                "dataset_count": len(raw_results),
            }
        ]
        organizations.extend(
            sorted(
                section_counts.values(),
                key=lambda e: (-int(e["dataset_count"]), str(e["name"])),
            )
        )
        return organizations

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_categories(
    lang: str = "en",
) -> tuple[dict[str, Any], bool]:
    """List categories/groups among NB federal CKAN datasets.

    NB packages carry an empty CKAN `groups` array (do not build this on
    group_list) — subject, topic_category and res_format facets stand in
    instead. One package_search call with rows=0 and facet.field requesting
    all three facets (facet.limit=50).

    Returns {"subjects": [...], "topics": [...], "formats": [...]}, each a
    list of {name, count} sorted by count descending.
    """
    cache_key = f"{CACHE_KEY_PREFIX}categories"

    async def _fetch() -> dict[str, Any]:
        params = {
            "q": "",
            "rows": 0,
            "fq": _build_fq(None),
            "facet.field": '["subject", "topic_category", "res_format"]',
            "facet.limit": 50,
        }
        result = await _api_get("package_search", params)
        facets = result.get("facets") or {}

        def _sorted_buckets(name: str) -> list[dict[str, Any]]:
            buckets = facets.get(name)
            if not isinstance(buckets, dict):
                return []
            pairs = sorted(buckets.items(), key=lambda kv: kv[1], reverse=True)
            return [{"name": str(k), "count": int(v)} for k, v in pairs if k]

        return {
            "subjects": _sorted_buckets("subject"),
            "topics": _sorted_buckets("topic_category"),
            "formats": _sorted_buckets("res_format"),
        }

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


# ---------------------------------------------------------------------------
# gnb.socrata.com discovery — Plan 02 fills bodies (checkpoint option-a)
# ---------------------------------------------------------------------------


async def fetch_gnb_socrata_search(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], bool]:
    """Search gnb.socrata.com's catalog (keyless, 312 datasets — checkpoint option-a).

    Keyless reads are verified working — no X-App-Token header is sent.
    `limit` is clamped to [1, 100]; `offset` is floored at 0.
    """
    clamped_limit = max(1, min(limit, 100))
    clamped_offset = max(offset, 0)
    cache_key = (
        f"{CACHE_KEY_PREFIX}socrata:search:{query}:{clamped_limit}:{clamped_offset}"
    )

    async def _fetch() -> dict[str, Any]:
        await _socrata_limiter.acquire()
        raw = await socrata.search_catalog(
            GNB_SOCRATA_DOMAIN,
            q=query,
            limit=clamped_limit,
            offset=clamped_offset,
            only="datasets",
        )
        results = [socrata.shape_catalog_result(r) for r in raw.get("results", [])]
        return {"results": results, "total": raw.get("resultSetSize", 0)}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


async def fetch_gnb_socrata_query(
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    limit: int = 1000,
) -> tuple[dict[str, Any], bool]:
    """Query a gnb.socrata.com dataset via SoQL (checkpoint option-a).

    Rejects a `limit` above `MAX_RECORDS`, or `<= 0` (F3 — matching
    `fetch_query_dataset`'s lower-bound check), with `InvalidInput` before
    any network call. A non-positive limit sent upstream as `$limit` either
    errors at Socrata or returns a misleading payload whose `truncated`
    calculation is true with no rows. When the caller has not supplied an
    explicit `select`, geometry-shaped columns (`the_geom*`) are stripped
    from the returned rows after the fetch — the Nova Scotia precedent for
    excluding geometry by default. No X-App-Token header is sent (keyless
    reads verified working).
    """
    if limit <= 0:
        raise InvalidInput(
            f"limit must be greater than 0 for gnb.socrata.com queries, got {limit}"
        )
    if limit > MAX_RECORDS:
        raise InvalidInput(
            f"limit must be at most {MAX_RECORDS} for gnb.socrata.com queries, got {limit}"
        )
    cache_key = f"{CACHE_KEY_PREFIX}socrata:query:{dataset_id}:{where}:{select}:{limit}"

    async def _fetch() -> dict[str, Any]:
        await _socrata_limiter.acquire()
        rows = await socrata.query_dataset(
            GNB_SOCRATA_DOMAIN,
            dataset_id,
            where=where,
            select=select,
            limit=limit,
        )
        if select is None:
            rows = [
                {k: v for k, v in row.items() if not k.lower().startswith("the_geom")}
                for row in rows
            ]
        return {"rows": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, _fetch)


# ---------------------------------------------------------------------------
# GeoNB discovery + flood/water — Plan 04 fills bodies
# ---------------------------------------------------------------------------

# Services with a curated nb_get_* tool built on a locked *_SERVICE/*_LAYER
# constant (D-07). GeoNB_DNR_ProvincialParks and GeoNB_DNR_MineralOccurrences
# are deliberately absent — the checkpoint (21-01) dropped both to the long
# tail, reachable only through nb_query_geonb_layer.
_GEONB_CURATED_TOOL_BY_SERVICE: dict[str, str] = {
    "GeoNB_DNR_Crown_Land": "nb_get_crown_land",
    "GeoNB_ENV_FloodHazardIndex": "nb_get_flood_hazard_areas",
    "GeoNB_ENV_Historical_Floods": "nb_get_historical_floods",
    "GeoNB_ENV_Wetlands": "nb_get_wetlands",
    "GeoNB_ELG_Contaminated_Sites": "nb_get_contaminated_sites",
    "GeoNB_SNB_Parcels": "nb_get_parcels",
    "GeoNB_DPS_Civic_Address": "nb_get_civic_addresses",
    "GeoNB_Health_Facilities": "nb_get_health_facilities",
    "GeoNB_EECD_PublicSchools": "nb_get_public_schools",
}

# Named exclusion reasons for GEONB_EXCLUDED_SERVICES entries that are not
# self-evidently a basemap (21-SPIKE.md §3: WildlifeRefuges is a retired
# 1-record placeholder, not live data).
_GEONB_NAMED_EXCLUSION_REASONS: dict[str, str] = {
    "GeoNB_DNR_WildlifeRefuges": (
        "retired placeholder service — layer 0 is named 'Retired Map Service' "
        "and holds 1 record (21-SPIKE.md section 3), not live wildlife refuge data"
    ),
}


def _decode_geonb_department(service_name: str) -> str | None:
    """Decode the department code from a `GeoNB_{DEPT}_...` service name."""
    parts = service_name.split("_")
    if len(parts) >= 2 and parts[0] == "GeoNB":
        return parts[1]
    return None


def _geonb_exclusion_reason(service_name: str) -> str:
    """Return why a service is hidden from the default nb_list_geonb_services listing."""
    if service_name in _GEONB_NAMED_EXCLUSION_REASONS:
        return _GEONB_NAMED_EXCLUSION_REASONS[service_name]
    if service_name.startswith("GeoNB_Basemap_"):
        return "basemap tile layer — imagery/reference tiles, not queryable feature data"
    return "excluded from the default listing"


async def fetch_geonb_services(
    query: str = "",
    include_excluded: bool = False,
) -> tuple[list[dict[str, Any]], bool]:
    """List GeoNB services via the live service-directory enumerator (D-06).

    Stands in for the Hub Search API, which returns HTTP 401 on GeoNB's Hub.
    Every entry carries `name`, `type`, the department decoded from the
    `GeoNB_{DEPT}_` prefix, and `curated_tool` (the nb_get_* tool name when
    one exists, else None). By default the 5 basemap tile services and the
    retired `GeoNB_DNR_WildlifeRefuges` placeholder are omitted; pass
    `include_excluded=True` to see them, each carrying a non-empty
    `exclusion_reason`. `query` filters by case-insensitive substring match
    against the service name.
    """
    cache_key = f"{CACHE_KEY_PREFIX}geonb:services:{include_excluded}"

    async def _fetch() -> list[dict[str, Any]]:
        await _geonb_limiter.acquire()
        raw_services = await arcgis_hub.list_arcgis_server_services(GEONB_BASE_URL)
        entries: list[dict[str, Any]] = []
        for svc in raw_services:
            name = svc.get("name", "")
            excluded = name in GEONB_EXCLUDED_SERVICES
            if excluded and not include_excluded:
                continue
            entry: dict[str, Any] = {
                "name": name,
                "type": svc.get("type"),
                "department": _decode_geonb_department(name),
                "curated_tool": _GEONB_CURATED_TOOL_BY_SERVICE.get(name),
            }
            if excluded:
                entry["excluded"] = True
                entry["exclusion_reason"] = _geonb_exclusion_reason(name)
            entries.append(entry)
        return entries

    services, cached = await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
    if query:
        q = query.lower()
        services = [s for s in services if q in s["name"].lower()]
    return services, cached


async def fetch_geonb_service_layers(
    service_name: str,
) -> tuple[dict[str, Any], bool]:
    """List the layers/tables of a single GeoNB service, enriched with each
    layer's live record count and real field names (D-06).

    Raises `NotFound` naming `nb_list_geonb_services` when `service_name`
    is not in the live directory. Fanning out to `get_count` and
    `get_layer_metadata` per layer is what gives an agent the layer id, real
    field names and scale in one call — the absence of exactly this
    information caused the Saskatchewan wrong-layer bug (T-21-14 bounds the
    fan-out: cached at CACHE_TTL_META, the GeoNB limiter serialises it, and
    every GeoNB service has fewer than 10 layers).
    """
    cache_key = f"{CACHE_KEY_PREFIX}geonb:service_layers:{service_name}"

    async def _fetch() -> dict[str, Any]:
        services, _ = await fetch_geonb_services(include_excluded=True)
        valid_names = {s["name"] for s in services}
        if service_name not in valid_names:
            raise NotFound(
                f"GeoNB service not found: {service_name!r} — "
                "use nb_list_geonb_services to see valid service names"
            )
        service_root = f"{GEONB_BASE_URL}/{service_name}"
        mapserver_url = f"{service_root}/MapServer"

        await _geonb_limiter.acquire()
        layer_data = await arcgis_hub.get_arcgis_server_layers(service_root)

        enriched_layers: list[dict[str, Any]] = []
        for layer in layer_data.get("layers", []):
            layer_id = layer.get("id")
            await _geonb_limiter.acquire()
            count = await arcgis_hub.get_count(mapserver_url, layer_id)
            await _geonb_limiter.acquire()
            meta = await arcgis_hub.get_layer_metadata(mapserver_url, layer_id)
            enriched_layers.append(
                {
                    "id": layer_id,
                    "name": layer.get("name"),
                    "record_count": count,
                    "fields": [f.get("name") for f in meta.get("fields", [])],
                }
            )
        return {"layers": enriched_layers, "tables": layer_data.get("tables", [])}

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)


async def fetch_geonb_layer_features(
    service_name: str,
    layer_id: int,
    where: str | None = None,
    out_fields: str = "*",
    limit: int = MAX_RECORDS,
    include_geometry: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Query any GeoNB layer by service name + layer id — the long-tail escape
    hatch that keeps `nb_get_provincial_parks`/`nb_get_mineral_occurrences`
    reachable after the checkpoint option-a manifest change.

    Rejects `limit` above `MAX_RECORDS` with `InvalidInput`, and rejects a
    `service_name` absent from the live directory with `NotFound`, both
    before any feature request. `where` is passed straight through — a falsy
    value is coalesced to the ArcGIS match-all form by `_geonb_query`/
    `arcgis_hub.query_feature_service`.
    """
    if limit > MAX_RECORDS:
        raise InvalidInput(
            f"limit must be at most {MAX_RECORDS} for nb_query_geonb_layer, got {limit}"
        )
    services, _ = await fetch_geonb_services(include_excluded=True)
    valid_names = {s["name"] for s in services}
    if service_name not in valid_names:
        raise NotFound(
            f"GeoNB service not found: {service_name!r} — "
            "use nb_list_geonb_services to see valid service names"
        )
    service_url = f"{GEONB_BASE_URL}/{service_name}/MapServer"
    cache_key = (
        f"{CACHE_KEY_PREFIX}geonb:query:{service_name}:{layer_id}:{where}:"
        f"{out_fields}:{limit}:{include_geometry}"
    )
    return await _geonb_query(
        service_url,
        layer_id=layer_id,
        where=where,
        out_fields=out_fields,
        include_geometry=include_geometry,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


_HISTORICAL_FLOOD_LAYERS_BY_EVENT: dict[str | None, int] = {
    None: HISTORICAL_FLOODS_LAYER,
    "2008": HISTORICAL_FLOODS_LAYER,
    "2018": HISTORICAL_FLOODS_LAYER,
    "1973": HISTORICAL_FLOODS_1973_LAYER,
}

_HISTORICAL_FLOOD_FIELDS_BY_LAYER: dict[int, str] = {
    HISTORICAL_FLOODS_LAYER: "ID,KEY,FEATURE,SOURCE,LIMIT",
    HISTORICAL_FLOODS_1973_LAYER: "Id",
}


def _escape_sql_value(value: str) -> str:
    """Single-quote-escape a string value before interpolating it into a
    server-built WHERE clause (T-21-01). ArcGIS's SQL-92 dialect doubles a
    literal apostrophe the same way standard SQL does.
    """
    return value.replace("'", "''")


def _escape_like_value(value: str) -> str:
    r"""Escape SQL `LIKE` metacharacters (CR-01) before quote-doubling.

    `_upper_contains_clause` wraps `value` in `%...%` wildcards — without
    this, a caller-supplied `%` or `_` is interpreted by ArcGIS as a live
    wildcard rather than a literal character. `county="%"` would otherwise
    build `UPPER(COUNTY) LIKE '%%%'`, which matches every row in a
    604,520-row layer. The literal backslash (the escape character itself)
    is doubled first so a caller-supplied backslash can't be misread as
    escaping the character that follows it; `_escape_sql_value` still
    handles the trailing apostrophe-doubling pass. The companion
    `_upper_contains_clause` declares `ESCAPE '\'` on the generated clause
    so ArcGIS honours this escaping (live-verified against
    GeoNB_SNB_Parcels 2026-07-30: an unescaped `LIKE '%%%'` matches all
    604,520 rows; the escaped form with `ESCAPE '\'` matches 0 for a
    literal `%` and the expected count for a real value).
    """
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return _escape_sql_value(escaped)


def _upper_contains_clause(field: str, value: str) -> str:
    """Case-insensitive containment clause: `UPPER(field) LIKE '%VALUE%'`,
    upper-casing both sides (T-21-01), escaping `LIKE` metacharacters
    (CR-01, via `_escape_like_value`) and single-quote-escaping the value.

    Used where the upstream field holds free text a caller would reasonably
    substring-match (county, community, street) rather than an identifier a
    caller would equality-match (PID) — an equality clause on a free-text
    field would silently return nothing for a real, differently-cased value.
    """
    return f"UPPER({field}) LIKE '%{_escape_like_value(value.upper())}%' ESCAPE '\\'"


async def fetch_flood_hazard_areas(
    sheet: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch flood hazard index polygons (GeoNB_ENV_FloodHazardIndex layer 0).

    `sheet` restricts to a single source map sheet via a server-built,
    single-quote-escaped equality clause on `Sheet_Numb`; when omitted the
    WHERE clause is the falsy form, coalesced to match-all downstream.
    """
    where = f"Sheet_Numb='{_escape_sql_value(sheet)}'" if sheet else None
    cache_key = f"{CACHE_KEY_PREFIX}flood_hazard:{sheet}:{limit}"
    return await _geonb_query(
        FLOOD_HAZARD_SERVICE,
        layer_id=FLOOD_HAZARD_LAYER,
        where=where,
        out_fields="Sheet_Numb,Technical_,Flood_Haza,Technical1",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


async def fetch_historical_floods(
    event: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch historical flood limits/extents (GeoNB_ENV_Historical_Floods,
    layer 0 for the 2008/2018 events, layer 8 for the separately-mapped 1973
    event).

    `event` dispatches through `_HISTORICAL_FLOOD_LAYERS_BY_EVENT`; None (the
    default), "2008" and "2018" all resolve to the shared main layer, "1973"
    resolves to the dedicated 1973 layer. Any other value raises
    `InvalidInput` naming the accepted values before any network call — the
    second line of defence behind the tool layer's own pre-check.
    """
    if event not in _HISTORICAL_FLOOD_LAYERS_BY_EVENT:
        valid = sorted(k for k in _HISTORICAL_FLOOD_LAYERS_BY_EVENT if k)
        raise InvalidInput(f"event must be one of {valid}, got {event!r}")
    layer_id = _HISTORICAL_FLOOD_LAYERS_BY_EVENT[event]
    cache_key = f"{CACHE_KEY_PREFIX}historical_floods:{event}:{limit}"
    return await _geonb_query(
        HISTORICAL_FLOODS_SERVICE,
        layer_id=layer_id,
        where=None,
        out_fields=_HISTORICAL_FLOOD_FIELDS_BY_LAYER[layer_id],
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


def _require_any_filter(
    tool_name: str,
    *filters: Any,
    layer_record_count: int,
) -> None:
    """Raise InvalidInput before any network call when a FILTER_REQUIRED_TOOLS
    entry receives no filter argument (T-21-03). Reused by every large-layer
    curated fetcher so the guard set stays driven by
    `constants.FILTER_REQUIRED_TOOLS` rather than scattered per-function
    literals.

    Tests on Python *truthiness* alone (CR-01: `any(filters)`) let a
    whitespace-only string (`" "`) through — it's truthy but not a real
    filter, and downstream builds a WHERE clause matching every row whose
    value contains a space. String filters are `.strip()`ped before the
    truthiness check; non-string filters (e.g. `civic_number: int | None`)
    are tested with `is not None` so a real, meaningful `0` isn't mistaken
    for "not provided".
    """
    if tool_name not in FILTER_REQUIRED_TOOLS:
        return
    if any(f.strip() if isinstance(f, str) else f is not None for f in filters):
        return
    raise InvalidInput(
        f"{tool_name} requires at least one filter parameter "
        f"(the layer has {layer_record_count:,} rows)"
    )


async def fetch_wetlands(
    wetland_class: str | None = None,
    status: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch wetland polygons (GeoNB_ENV_Wetlands layer 2). FILTER_REQUIRED —
    163,206 rows; rejects an unfiltered call with `InvalidInput` before any
    network call (T-21-03), enforced via `_require_any_filter` and
    `constants.FILTER_REQUIRED_TOOLS`.

    `wetland_class` and `status` each build a server-side, single-quote-
    escaped equality clause; both together are AND-ed.
    """
    _require_any_filter(
        "nb_get_wetlands", wetland_class, status, layer_record_count=163_206
    )
    clauses: list[str] = []
    if wetland_class:
        clauses.append(f"WETLAND_CLASS='{_escape_sql_value(wetland_class)}'")
    if status:
        clauses.append(f"STATUS='{_escape_sql_value(status)}'")
    where = " AND ".join(clauses)
    cache_key = f"{CACHE_KEY_PREFIX}wetlands:{wetland_class}:{status}:{limit}"
    return await _geonb_query(
        WETLANDS_SERVICE,
        layer_id=WETLANDS_LAYER,
        where=where,
        out_fields="ID,Hectares,WC,WETLAND_CLASS,STATUS",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


async def fetch_contaminated_sites(
    status: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch contaminated site points (GeoNB_ELG_Contaminated_Sites layer 0).

    `status` restricts on the English status field (`Status_E`) via a
    server-built, single-quote-escaped equality clause; both `Status_E` and
    `Status_F` (bilingual status text) are always returned regardless of
    which field the filter matched on. F4: `Latitude`/`Longitude` are
    included so a caller can actually locate a returned site — live-verified
    2026-07-30 against GeoNB_ELG_Contaminated_Sites/0, which carries both.
    """
    where = f"Status_E='{_escape_sql_value(status)}'" if status else None
    cache_key = f"{CACHE_KEY_PREFIX}contaminated_sites:{status}:{limit}"
    return await _geonb_query(
        CONTAMINATED_SITES_SERVICE,
        layer_id=CONTAMINATED_SITES_LAYER,
        where=where,
        out_fields="Status_E,Status_F,FileOpenDate,PidType_E,PidType_F,Latitude,Longitude",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


# ---------------------------------------------------------------------------
# Parcels / civic address — Plan 05 fills bodies
# ---------------------------------------------------------------------------


async def fetch_parcels(
    pid: str | None = None,
    county: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch land parcels (GeoNB_SNB_Parcels layer 0). FILTER_REQUIRED —
    604,520 rows; rejects an unfiltered call with `InvalidInput` before any
    network call (T-21-03), enforced via `_require_any_filter` and
    `constants.FILTER_REQUIRED_TOOLS` — the second line of defence behind the
    tool layer's own pre-check.

    `pid` builds a server-side, single-quote-escaped equality clause on `PID`
    (an identifier — equality is correct here, unlike the free-text fields
    below). `county` builds a case-insensitive containment clause via
    `_upper_contains_clause`. Both together are AND-ed.
    """
    _require_any_filter("nb_get_parcels", pid, county, layer_record_count=604_520)
    clauses: list[str] = []
    if pid:
        clauses.append(f"PID='{_escape_sql_value(pid)}'")
    if county:
        clauses.append(_upper_contains_clause("COUNTY", county))
    where = " AND ".join(clauses)
    cache_key = f"{CACHE_KEY_PREFIX}parcels:{pid}:{county}:{limit}"
    return await _geonb_query(
        PARCELS_SERVICE,
        layer_id=PARCELS_LAYER,
        where=where,
        out_fields="PID,COUNTY,Titles_Status,Gazette_Status",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


async def fetch_civic_addresses(
    community: str | None = None,
    street: str | None = None,
    civic_number: int | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch civic addresses (GeoNB_DPS_Civic_Address layer 0). FILTER_REQUIRED
    — 373,172 rows; rejects an unfiltered call with `InvalidInput` before any
    network call (T-21-03), enforced via `_require_any_filter` and
    `constants.FILTER_REQUIRED_TOOLS` — the second line of defence behind the
    tool layer's own pre-check.

    `community` and `street` each build a case-insensitive containment clause
    via `_upper_contains_clause`. `civic_number` builds a numeric equality
    clause on `CIVIC_NUM` with the integer interpolated UNQUOTED — quoting it
    would make ArcGIS compare a number to a string and silently return
    nothing. All supplied filters are AND-ed.

    F5: `LATITUDE`/`LONGITUDE` (the address -> point half of the documented
    geocoding workflow) and `COUNTY`/`PID` (what makes chaining into
    `nb_get_parcels`'s county/pid filters actually work) are included —
    live-verified 2026-07-30 against GeoNB_DPS_Civic_Address/0, which
    carries all four alongside the previously-projected fields.
    """
    _require_any_filter(
        "nb_get_civic_addresses",
        community,
        street,
        civic_number,
        layer_record_count=373_172,
    )
    clauses: list[str] = []
    if community:
        clauses.append(_upper_contains_clause("COMMUNITY", community))
    if street:
        clauses.append(_upper_contains_clause("STREET", street))
    if civic_number is not None:
        clauses.append(f"CIVIC_NUM={int(civic_number)}")
    where = " AND ".join(clauses)
    cache_key = (
        f"{CACHE_KEY_PREFIX}civic_addresses:{community}:{street}:{civic_number}:{limit}"
    )
    return await _geonb_query(
        CIVIC_ADDRESS_SERVICE,
        layer_id=CIVIC_ADDRESS_LAYER,
        where=where,
        out_fields="CIVIC_NUM,STREET,ST_TYPE_E,ST_TYPE_F,COMMUNITY,COUNTY,PID,LATITUDE,LONGITUDE",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


# ---------------------------------------------------------------------------
# Health / education + 511 — Plan 06 fills bodies
# ---------------------------------------------------------------------------

# GeoNB_Health_Facilities publishes two distinct raw schemas across its 6
# layers (21-SPIKE.md §4): layers 0-1 (hospitals) are the compact
# Name_E/Telephone_ shape, layers 2-5 are a wide Esri-geocoder-derived shape
# that SPIKE names only representative fields for, not an exhaustive list.
# Live-verified 2026-07-30 (this plan) against
# https://geonb.snb.ca/arcgis/rest/services/GeoNB_Health_Facilities/MapServer/{0..5}?f=json
# to find the real per-layer field that holds the facility name, so a `name`
# containment filter never sends a WHERE clause referencing a field that
# layer does not have (a bare Name_E filter against layer 3, for example,
# returns an upstream HTTP 400 "Failed to execute query").
_HEALTH_FACILITY_NAME_FIELD: dict[str, str] = {
    "hospital_horizon": "Name_E",
    "hospital_vitalite": "Name_E",
    "after_hours_clinic": "USER_Clini",
    "adult_residential_centre": "Name",
    "nursing_home": "Name___Nom",
    "pharmacy": "Pharmacy_Name",
}


async def fetch_health_facilities(
    facility_type: str,
    name: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch health facilities (GeoNB_Health_Facilities, HEALTH_FACILITY_LAYERS
    dispatch by facility_type).

    `facility_type` must be a key of HEALTH_FACILITY_LAYERS — an unknown value
    raises `InvalidInput` listing the sorted valid keys before any network
    call. `out_fields` is always `"*"` because the 6 layers do not share one
    field schema (see `_HEALTH_FACILITY_NAME_FIELD` above); `name` AND-s a
    case-insensitive containment clause on the live-verified name field for
    the dispatched layer rather than assuming `Name_E` exists everywhere.
    """
    if facility_type not in HEALTH_FACILITY_LAYERS:
        valid = sorted(HEALTH_FACILITY_LAYERS)
        raise InvalidInput(
            f"facility_type must be one of {valid}, got {facility_type!r}"
        )
    layer_id = HEALTH_FACILITY_LAYERS[facility_type]
    where: str | None = None
    if name:
        name_field = _HEALTH_FACILITY_NAME_FIELD[facility_type]
        where = _upper_contains_clause(name_field, name)
    cache_key = f"{CACHE_KEY_PREFIX}health_facilities:{facility_type}:{name}:{limit}"
    payload, cached = await _geonb_query(
        HEALTH_FACILITIES_SERVICE,
        layer_id=layer_id,
        where=where,
        out_fields="*",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )
    payload["facility_type"] = facility_type
    return payload, cached


async def fetch_public_schools(
    sector: str = "anglophone",
    district: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict[str, Any], bool]:
    """Fetch public schools (GeoNB_EECD_PublicSchools, SCHOOL_SECTOR_LAYERS
    dispatch by sector).

    `sector` must be a key of SCHOOL_SECTOR_LAYERS ("anglophone" or
    "francophone") — an unknown value raises `InvalidInput` listing the
    sorted valid keys before any network call. `district` builds a
    case-insensitive containment clause on `strDST` — live-verified 2026-07-30
    short codes: ASD-E/ASD-N/ASD-S/ASD-W (anglophone), DSF-NE/DSF-NO/DSF-S
    (francophone). Both layers share the same field schema (21-SPIKE.md §4).
    """
    if sector not in SCHOOL_SECTOR_LAYERS:
        valid = sorted(SCHOOL_SECTOR_LAYERS)
        raise InvalidInput(f"sector must be one of {valid}, got {sector!r}")
    layer_id = SCHOOL_SECTOR_LAYERS[sector]
    where = _upper_contains_clause("strDST", district) if district else None
    cache_key = f"{CACHE_KEY_PREFIX}public_schools:{sector}:{district}:{limit}"
    return await _geonb_query(
        PUBLIC_SCHOOLS_SERVICE,
        layer_id=layer_id,
        where=where,
        out_fields="strID,strDST,strNM,strAD1,strGR,strURL",
        include_geometry=False,
        limit=limit,
        ttl=CACHE_TTL_META,
        cache_key=cache_key,
    )


async def fetch_road_events() -> tuple[list[dict[str, Any]], bool]:
    """Fetch current road events from NB 511 (key-gated).

    KEY REQUIRED: `_511_get` reads `NEW_BRUNSWICK_511_KEY` and raises
    `Five11NotConfigured` before any network call when it is absent — the
    tool layer maps that to a `NOT_CONFIGURED` envelope (D-10). Live-probed
    endpoint: `511.gnb.ca/api/v2/get/event`. Cached at `CACHE_TTL_LIVE`
    because road events change frequently.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:event"

    async def _fetch() -> list[dict[str, Any]]:
        await _511_limiter.acquire()
        return await _511_get("event")

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_winter_road_conditions() -> tuple[list[dict[str, Any]], bool]:
    """Fetch winter road conditions from NB 511 (key-gated).

    KEY REQUIRED: `_511_get` reads `NEW_BRUNSWICK_511_KEY` and raises
    `Five11NotConfigured` before any network call when it is absent. Endpoint:
    `511.gnb.ca/api/v2/get/winterroads`. Cached at `CACHE_TTL_LIVE` because
    conditions change frequently through the winter season.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:winterroads"

    async def _fetch() -> list[dict[str, Any]]:
        await _511_limiter.acquire()
        return await _511_get("winterroads")

    return await cached_fetch(cache_key, CACHE_TTL_LIVE, _fetch)


async def fetch_traffic_cameras() -> tuple[list[dict[str, Any]], bool]:
    """Fetch traffic camera locations from NB 511 (key-gated).

    KEY REQUIRED: `_511_get` reads `NEW_BRUNSWICK_511_KEY` and raises
    `Five11NotConfigured` before any network call when it is absent. Endpoint:
    `511.gnb.ca/api/v2/get/cameras`. Cached at `CACHE_TTL_META` (24h) — unlike
    events and winter roads, camera locations are stable infrastructure.
    """
    cache_key = f"{CACHE_KEY_PREFIX}511:cameras"

    async def _fetch() -> list[dict[str, Any]]:
        await _511_limiter.acquire()
        return await _511_get("cameras")

    return await cached_fetch(cache_key, CACHE_TTL_META, _fetch)
