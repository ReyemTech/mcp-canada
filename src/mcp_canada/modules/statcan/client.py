"""StatCan WDS REST API client.

Provides async functions for fetching, caching, and rate-limiting all WDS endpoints.
All public functions return (data, was_cached) tuples.

BM25 search uses Okapi BM25 (k1=1.2, b=0.75) over cubeTitleEn + cubeTitleFr +
subjectCode + surveyCode fields from getAllCubesListLite.
"""

import collections
import math
from typing import Any

import httpx

from mcp_canada import __version__
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from mcp_canada.modules.statcan.constants import (
    BASE_URL,
    CACHE_TTL_CODESETS,
    CACHE_TTL_CUBES,
    CACHE_TTL_META,
    CACHE_TTL_OBS,
    FREQUENCY_CODES,
    RATE_GROUP,
    RATE_LIMIT,
    SCALAR_FACTOR_CODES,
    STATCAN_VERIFY,
    TIMEOUT_LARGE,
)
from mcp_canada.modules.statcan.schemas import (
    CodeSetEntry,
    CodeSets,
    CubeLite,
    CubeMetadata,
    Dimension,
    DimensionMember,
    ObservationRow,
    SeriesInfo,
)
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter


def _make_statcan_client(timeout: float = 30.0) -> httpx.AsyncClient:
    """Create an httpx client scoped to StatCan with correct SSL setting.

    verify=True uses certifi (httpx default).
    verify=False is scoped to this client only — never affects shared clients.
    """
    return httpx.AsyncClient(
        verify=STATCAN_VERIFY,
        timeout=httpx.Timeout(timeout),
        headers={"User-Agent": f"mcp-canada/{__version__}"},
    )


async def _limiter_acquire() -> None:
    """Acquire one token from the StatCan rate limiter."""
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)
    await limiter.acquire()


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def pad_coordinate(coord: str) -> str:
    """Pad a WDS coordinate string to exactly 10 dot-separated parts.

    WDS coordinates identify a series within a cube. They have up to 10
    dimensions separated by periods (e.g. "1.3.1"). Shorter coordinates
    are padded with "0" to reach 10 parts. Longer coordinates are truncated.

    Args:
        coord: Dot-separated coordinate string (e.g. "1.3.1").

    Returns:
        10-part dot-separated coordinate string (e.g. "1.3.1.0.0.0.0.0.0.0").
    """
    parts = coord.split(".")
    if len(parts) >= 10:
        return ".".join(parts[:10])
    parts += ["0"] * (10 - len(parts))
    return ".".join(parts)


def _unwrap(raw: Any) -> Any:
    """Extract the object from a WDS SUCCESS envelope.

    WDS endpoints return envelopes like:
      {"status": "SUCCESS", "object": {...}}
    or list-wrapped:
      [{"status": "SUCCESS", "object": {...}}]

    Args:
        raw: Raw WDS response (dict or list).

    Returns:
        The "object" value from the SUCCESS envelope.

    Raises:
        ValueError: If the envelope status is not "SUCCESS", with the
                    WDS error message as the exception text.
    """
    envelope = raw[0] if isinstance(raw, list) else raw
    status = envelope.get("status", "")
    if status != "SUCCESS":
        raise ValueError(str(envelope.get("object", "WDS request failed")))
    return envelope["object"]


# ---------------------------------------------------------------------------
# BM25 search infrastructure
# ---------------------------------------------------------------------------


def _build_doc_tokens(cube: dict) -> list[str]:
    """Tokenize a cube's searchable fields into a list of lowercase tokens.

    Fields used: cubeTitleEn, cubeTitleFr, subjectCode list, surveyCode list.
    """
    parts: list[str] = []
    parts.extend((cube.get("cubeTitleEn") or "").lower().split())
    parts.extend((cube.get("cubeTitleFr") or "").lower().split())
    for code in cube.get("subjectCode") or []:
        parts.extend(str(code).lower().split())
    for code in cube.get("surveyCode") or []:
        parts.extend(str(code).lower().split())
    return parts


def _build_search_index(
    cubes: list[dict],
) -> tuple[list[dict], float, dict[str, int]]:
    """Compute BM25 index statistics over all cubes.

    Args:
        cubes: Raw cube dicts from getAllCubesListLite.

    Returns:
        (cubes, avg_dl, df) where:
          - cubes: the original list (unchanged)
          - avg_dl: average document length across all cubes
          - df: per-term document frequency (count of docs containing the term)
    """
    doc_lengths: list[int] = []
    df: dict[str, int] = collections.Counter()

    for cube in cubes:
        tokens = _build_doc_tokens(cube)
        doc_lengths.append(len(tokens))
        for term in set(tokens):  # unique terms per doc for IDF
            df[term] += 1

    avg_dl = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0.0
    return cubes, avg_dl, dict(df)


def _bm25_score(
    query_terms: list[str],
    doc_tokens: list[str],
    avg_dl: float,
    N: int,
    df: dict[str, int],
    k1: float = 1.2,
    b: float = 0.75,
) -> float:
    """Compute Okapi BM25 score for a document given query terms.

    Args:
        query_terms: Tokenized query (lowercase).
        doc_tokens: Tokenized document (lowercase).
        avg_dl: Average document length across the corpus.
        N: Total number of documents in the corpus.
        df: Per-term document frequency dict.
        k1: BM25 k1 parameter (default 1.2).
        b: BM25 b parameter (default 0.75).

    Returns:
        BM25 score (float); 0.0 if no query terms match.
    """
    tf_counter = collections.Counter(doc_tokens)
    dl = len(doc_tokens)
    score = 0.0

    for term in query_terms:
        if term not in tf_counter:
            continue
        tf = tf_counter[term]
        n_q = df.get(term, 0)
        if n_q == 0:
            continue

        idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
        score += idf * tf_norm

    return score


# ---------------------------------------------------------------------------
# Public client functions
# ---------------------------------------------------------------------------


async def search_cubes(
    query: str, limit: int = 10
) -> tuple[list[CubeLite], bool]:
    """Search the StatCan cube catalog using BM25 ranking.

    Lazily loads and caches the full cube list (getAllCubesListLite). On each
    call, scores all cubes against the query and returns the top ``limit``
    results ordered by relevance.

    Args:
        query: Free-text search query (e.g. "consumer price index").
        limit: Maximum number of results to return (default 10).

    Returns:
        (list[CubeLite], was_cached) — results ranked by BM25 score descending.
    """

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_and_index() -> tuple[list[dict], float, dict[str, int]]:
        await _limiter_acquire()
        async with _make_statcan_client(timeout=TIMEOUT_LARGE) as http:
            resp = await http.get(BASE_URL + "getAllCubesListLite")
            resp.raise_for_status()
            cubes: list[dict] = resp.json()
        return _build_search_index(cubes)

    index, was_cached = await cached_fetch(
        "statcan_wds:getAllCubesListLite", CACHE_TTL_CUBES, _fetch_and_index
    )
    cubes, avg_dl, df = index
    N = len(cubes)

    if N == 0 or not query.strip():
        return [], was_cached

    query_terms = query.lower().split()
    scored: list[tuple[float, dict]] = []
    for cube in cubes:
        tokens = _build_doc_tokens(cube)
        score = _bm25_score(query_terms, tokens, avg_dl, N, df)
        if score > 0:
            scored.append((score, cube))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]

    results = [
        CubeLite(
            product_id=c["productId"],
            cansim_id=c.get("cansimId", ""),
            title_en=c.get("cubeTitleEn", ""),
            title_fr=c.get("cubeTitleFr", ""),
            start_date=c.get("cubeStartDate", ""),
            end_date=c.get("cubeEndDate", ""),
            release_time=c.get("releaseTime", ""),
            archived=bool(c.get("archived", False)),
            frequency_code=c.get("frequencyCode", 0),
            frequency=FREQUENCY_CODES.get(c.get("frequencyCode", 0), "Unknown"),
            subject_codes=list(c.get("subjectCode") or []),
            survey_codes=list(c.get("surveyCode") or []),
        )
        for _, c in top
    ]
    return results, was_cached


async def get_cube_metadata(product_id: int) -> tuple[CubeMetadata, bool]:
    """Fetch and flatten metadata for a single StatCan cube.

    Uses getCubeMetadata WDS endpoint. Result cached for 24 hours.

    Args:
        product_id: The WDS productId (e.g. 18100004).

    Returns:
        (CubeMetadata, was_cached)

    Raises:
        ValueError: If WDS returns a FAILED envelope (e.g. invalid productId).
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = f"statcan_wds:getCubeMetadata:{product_id}"

    async def _fetcher() -> dict:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getCubeMetadata",
                json=[{"productId": product_id}],
            )
            resp.raise_for_status()
            return resp.json()

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_META, _fetcher)
    obj = _unwrap(raw)
    return _flatten_cube_metadata(obj), was_cached


def _flatten_cube_metadata(obj: dict) -> CubeMetadata:
    """Flatten a raw getCubeMetadata object to a CubeMetadata schema instance."""
    dimensions: list[Dimension] = []
    for dim in obj.get("dimension") or []:
        members: list[DimensionMember] = [
            DimensionMember(
                member_id=m["memberId"],
                parent_member_id=m.get("parentMemberId", 0),
                name_en=m.get("memberNameEn", ""),
                name_fr=m.get("memberNameFr", ""),
                classification_code=m.get("classificationCode"),
                geo_flag=bool(m.get("geoFlag", False)),
            )
            for m in dim.get("member") or []
        ]
        dimensions.append(
            Dimension(
                name_en=dim.get("dimensionNameEn", ""),
                name_fr=dim.get("dimensionNameFr", ""),
                has_uom=bool(dim.get("hasUom", False)),
                members=members,
            )
        )

    freq_code: int = obj.get("frequencyCode", 0)
    return CubeMetadata(
        product_id=obj["productId"],
        cansim_id=obj.get("cansimId", ""),
        title_en=obj.get("cubeTitleEn", ""),
        title_fr=obj.get("cubeTitleFr", ""),
        start_date=obj.get("cubeStartDate", ""),
        end_date=obj.get("cubeEndDate", ""),
        frequency_code=freq_code,
        frequency=FREQUENCY_CODES.get(freq_code, "Unknown"),
        nb_series=obj.get("nbSeries", 0),
        nb_datapoints=obj.get("nbDatapoints", 0),
        dimensions=dimensions,
        footnotes=list(obj.get("footnote") or []),
    )


async def get_code_sets() -> tuple[CodeSets, bool]:
    """Fetch all WDS code sets (frequency, scalar, status, symbol, uom, etc.).

    Code sets decode numeric codes into human-readable labels. Result cached
    for 7 days as these values rarely change.

    Returns:
        (CodeSets, was_cached)

    Raises:
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = "statcan_wds:getCodeSets"

    async def _fetcher() -> dict:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.get(BASE_URL + "getCodeSets")
            resp.raise_for_status()
            return resp.json()

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_CODESETS, _fetcher)
    obj = _unwrap(raw)
    return _flatten_code_sets(obj), was_cached


def _flatten_series_info(obj: dict) -> SeriesInfo:
    """Flatten a raw series info object to a SeriesInfo schema instance."""
    freq_code: int = obj.get("frequencyCode", 0)
    scalar_code: int = obj.get("scalarFactorCode", 0)
    return SeriesInfo(
        product_id=obj["productId"],
        coordinate=obj.get("coordinate", ""),
        vector_id=obj["vectorId"],
        frequency_code=freq_code,
        frequency=FREQUENCY_CODES.get(freq_code, "Unknown"),
        scalar_factor_code=scalar_code,
        scalar_factor=SCALAR_FACTOR_CODES.get(scalar_code, "Unknown"),
        decimals=obj.get("decimals", 0),
        terminated=bool(obj.get("terminated", 0)),
        title_en=obj.get("SeriesTitleEn", ""),
        title_fr=obj.get("SeriesTitleFr", ""),
        uom_code=obj.get("memberUomCode", 0),
    )


def _flatten_observation(raw_point: dict) -> ObservationRow:
    """Flatten a raw vectorDataPoint dict to an ObservationRow.

    Decodes scalarFactorCode and frequencyCode using constants dicts.
    Converts value to float | None (handles empty string or null).
    """
    freq_code: int = raw_point.get("frequencyCode", 0)
    scalar_code: int = raw_point.get("scalarFactorCode", 0)
    raw_value = raw_point.get("value")
    value: float | None
    if raw_value is None or raw_value == "":
        value = None
    else:
        value = float(raw_value)
    return ObservationRow(
        ref_per=raw_point.get("refPer", ""),
        ref_per_raw=raw_point.get("refPerRaw", ""),
        value=value,
        decimals=raw_point.get("decimals", 0),
        scalar_factor_code=scalar_code,
        scalar_factor=SCALAR_FACTOR_CODES.get(scalar_code, "Unknown"),
        frequency_code=freq_code,
        frequency=FREQUENCY_CODES.get(freq_code, "Unknown"),
        status_code=raw_point.get("statusCode", 0),
        symbol_code=raw_point.get("symbolCode", 0),
        release_time=raw_point.get("releaseTime", ""),
    )


def _flatten_code_sets(obj: dict) -> CodeSets:
    """Flatten raw getCodeSets object to a CodeSets schema instance."""

    def _entries(items: list[dict], code_key: str, en_key: str, fr_key: str) -> list[CodeSetEntry]:
        return [
            CodeSetEntry(code=e[code_key], desc_en=e[en_key], desc_fr=e[fr_key])
            for e in (items or [])
        ]

    return CodeSets(
        frequency=_entries(
            obj.get("frequency") or [], "frequencyCode", "frequencyDescEn", "frequencyDescFr"
        ),
        scalar=_entries(
            obj.get("scalar") or [], "scalarFactorCode", "scalarFactorDescEn", "scalarFactorDescFr"
        ),
        status=_entries(
            obj.get("status") or [], "statusCode", "statusDescEn", "statusDescFr"
        ),
        symbol=_entries(
            obj.get("symbol") or [], "symbolCode", "symbolDescEn", "symbolDescFr"
        ),
        security_level=_entries(
            obj.get("securityLevel") or [], "securityLevelCode", "securityLevelDescEn", "securityLevelDescFr"
        ),
        uom=_entries(
            obj.get("uom") or [], "memberUomCode", "memberUomEn", "memberUomFr"
        ),
    )


async def get_series_info_by_vector(vector_id: int) -> tuple[SeriesInfo, bool]:
    """Fetch series metadata by vectorId.

    Uses getSeriesInfoFromVector WDS endpoint. Result cached for 24 hours.

    Args:
        vector_id: The WDS vectorId (e.g. 32164132).

    Returns:
        (SeriesInfo, was_cached) with decoded frequency and scalar_factor labels.

    Raises:
        ValueError: If WDS returns a FAILED envelope.
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = f"statcan_wds:getSeriesInfoFromVector:{vector_id}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getSeriesInfoFromVector",
                json=[{"vectorId": vector_id}],
            )
            resp.raise_for_status()
            return resp.json()

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_META, _fetcher)
    obj = _unwrap(raw)
    return _flatten_series_info(obj), was_cached


async def get_series_info_by_coord(
    product_id: int, coordinate: str
) -> tuple[SeriesInfo, bool]:
    """Fetch series metadata by productId + coordinate with auto-padding.

    Uses getSeriesInfoFromCubePidCoord WDS endpoint. Coordinate is
    auto-padded to 10 parts before the request. Result cached for 24 hours.

    Args:
        product_id: The WDS productId (e.g. 35100003).
        coordinate: Dot-separated coordinate string (e.g. "1.12").

    Returns:
        (SeriesInfo, was_cached) with decoded frequency and scalar_factor labels.

    Raises:
        ValueError: If WDS returns a FAILED envelope.
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    padded = pad_coordinate(coordinate)
    cache_key = f"statcan_wds:getSeriesInfoFromCubePidCoord:{product_id}:{padded}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getSeriesInfoFromCubePidCoord",
                json=[{"productId": product_id, "coordinate": padded}],
            )
            resp.raise_for_status()
            return resp.json()

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_META, _fetcher)
    obj = _unwrap(raw)
    return _flatten_series_info(obj), was_cached


async def get_latest_n_by_vector(
    vector_id: int, n: int = 10
) -> tuple[list[ObservationRow], bool]:
    """Fetch latest N observations for a vector.

    Uses getDataFromVectorsAndLatestNPeriods WDS endpoint.
    Observations are sorted newest-first. Result cached for 1 hour.

    Args:
        vector_id: The WDS vectorId (e.g. 32164132).
        n: Number of most recent periods to return (default 10).

    Returns:
        (list[ObservationRow], was_cached) sorted newest-first by ref_per.

    Raises:
        ValueError: If WDS returns a FAILED envelope.
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = f"statcan_wds:getDataFromVectorsAndLatestNPeriods:{vector_id}:{n}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getDataFromVectorsAndLatestNPeriods",
                json=[{"vectorId": vector_id, "latestN": n}],
            )
            resp.raise_for_status()
            return resp.json()

    raw, was_cached = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    obj = _unwrap(raw)
    data_points: list[dict] = obj.get("vectorDataPoint") or []
    rows = [_flatten_observation(dp) for dp in data_points]
    rows.sort(key=lambda r: r.ref_per, reverse=True)
    return rows, was_cached


async def get_latest_n_by_coord(
    product_id: int, coordinate: str, n: int = 10
) -> tuple[list[ObservationRow], bool]:
    """Fetch latest N observations by productId + coordinate with auto-padding.

    Uses getDataFromCubePidCoordAndLatestNPeriods WDS endpoint. Coordinate
    is auto-padded to 10 parts before the request. Result cached for 1 hour.

    Args:
        product_id: The WDS productId (e.g. 35100003).
        coordinate: Dot-separated coordinate string (e.g. "1.12").
        n: Number of most recent periods to return (default 10).

    Returns:
        (list[ObservationRow], was_cached) sorted newest-first by ref_per.

    Raises:
        ValueError: If WDS returns a FAILED envelope.
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    padded = pad_coordinate(coordinate)
    cache_key = f"statcan_wds:getDataFromCubePidCoordAndLatestNPeriods:{product_id}:{padded}:{n}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getDataFromCubePidCoordAndLatestNPeriods",
                json=[{"productId": product_id, "coordinate": padded, "latestN": n}],
            )
            resp.raise_for_status()
            return resp.json()

    raw_coord, was_cached_coord = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    obj_coord = _unwrap(raw_coord)
    dp_coord: list[dict] = obj_coord.get("vectorDataPoint") or []
    rows_coord = [_flatten_observation(dp) for dp in dp_coord]
    rows_coord.sort(key=lambda r: r.ref_per, reverse=True)
    return rows_coord, was_cached_coord


async def get_data_by_ref_period(
    vector_id: int, start_date: str, end_date: str
) -> tuple[list[ObservationRow], bool]:
    """Fetch observations for a vector within a reference period date range.

    Uses getDataFromVectorByReferencePeriodRange WDS GET endpoint.
    Observations are sorted newest-first. Result cached for 1 hour.

    Args:
        vector_id: The WDS vectorId (e.g. 32164132).
        start_date: Start reference period (e.g. "2020-01-01").
        end_date: End reference period (e.g. "2023-01-01").

    Returns:
        (list[ObservationRow], was_cached) sorted newest-first by ref_per.

    Raises:
        ValueError: If WDS returns a FAILED envelope.
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = f"statcan_wds:getDataFromVectorByReferencePeriodRange:{vector_id}:{start_date}:{end_date}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            url = (
                BASE_URL
                + "getDataFromVectorByReferencePeriodRange"
                f"?vectorIds={vector_id}&startRefPeriod={start_date}&endReferencePeriod={end_date}"
            )
            resp = await http.get(url)
            resp.raise_for_status()
            return resp.json()

    raw2, was_cached2 = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    obj2 = _unwrap(raw2)
    data_points2: list[dict] = obj2.get("vectorDataPoint") or []
    rows2 = [_flatten_observation(dp) for dp in data_points2]
    rows2.sort(key=lambda r: r.ref_per, reverse=True)
    return rows2, was_cached2


async def get_bulk_vector_data(
    vector_ids: list[int], start_release: str, end_release: str
) -> tuple[dict[int, list[ObservationRow]], bool]:
    """Fetch observations for multiple vectors within a release date range.

    Uses getBulkVectorDataByRange WDS POST endpoint. vectorIds are passed
    as strings per the WDS specification. Partial failures are handled
    gracefully — failed vectors are omitted from the result dict.
    Result cached for 1 hour.

    Args:
        vector_ids: List of WDS vectorIds (e.g. [74804, 32164132]).
        start_release: Start release datetime (e.g. "2023-01-01T08:30").
        end_release: End release datetime (e.g. "2024-01-01T08:30").

    Returns:
        (dict[int, list[ObservationRow]], was_cached) — keyed by vectorId for
        successful vectors only. Check if any expected vectorIds are missing.

    Raises:
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    sorted_ids = sorted(vector_ids)
    cache_key = f"statcan_wds:getBulkVectorDataByRange:{sorted_ids}:{start_release}:{end_release}"

    async def _fetcher() -> list:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getBulkVectorDataByRange",
                json={
                    "vectorIds": [str(v) for v in vector_ids],
                    "startDataPointReleaseDate": start_release,
                    "endDataPointReleaseDate": end_release,
                },
            )
            resp.raise_for_status()
            return resp.json()

    raw3, was_cached3 = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    # raw3 is a list of per-vector envelopes — each has status + object
    result: dict[int, list[ObservationRow]] = {}
    for item in (raw3 if isinstance(raw3, list) else [raw3]):
        if item.get("status") != "SUCCESS":
            # FAILED item — skip (caller sees missing key in result)
            continue
        obj3 = item["object"]
        vid: int = obj3.get("vectorId", 0)
        data_points3: list[dict] = obj3.get("vectorDataPoint") or []
        rows3 = [_flatten_observation(dp) for dp in data_points3]
        rows3.sort(key=lambda r: r.ref_per, reverse=True)
        result[vid] = rows3
    return result, was_cached3


async def get_changed_series() -> tuple[list[dict], bool]:
    """Fetch the list of series (vectors) that changed today.

    Uses getChangedSeriesList WDS GET endpoint. Returns lightweight dicts
    with vectorId, productId, coordinate, releaseTime for each changed series.
    Result cached for 1 hour.

    Returns:
        (list[dict], was_cached) — each dict has keys: vectorId, productId,
        coordinate, releaseTime.

    Raises:
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = "statcan_wds:getChangedSeriesList"

    async def _fetcher() -> dict:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.get(BASE_URL + "getChangedSeriesList")
            resp.raise_for_status()
            return resp.json()

    raw4, was_cached4 = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    items4: list[dict] = _unwrap(raw4)
    result4 = [
        {
            "vectorId": item.get("vectorId"),
            "productId": item.get("productId"),
            "coordinate": item.get("coordinate"),
            "releaseTime": item.get("releaseTime"),
        }
        for item in (items4 if isinstance(items4, list) else [])
    ]
    return result4, was_cached4


async def get_changed_cubes(date: str) -> tuple[list[dict], bool]:
    """Fetch the list of cubes that changed on a specific date.

    Uses getChangedCubeList/{date} WDS GET endpoint. Returns lightweight
    dicts with productId, releaseTime for each changed cube.
    Result cached for 1 hour.

    Args:
        date: Date in YYYY-MM-DD format (e.g. "2024-01-15").

    Returns:
        (list[dict], was_cached) — each dict has keys: productId, releaseTime.

    Raises:
        httpx.HTTPStatusError: On HTTP 4xx/5xx responses.
    """
    cache_key = f"statcan_wds:getChangedCubeList:{date}"

    async def _fetcher() -> dict:
        await _limiter_acquire()
        async with _make_statcan_client() as http:
            resp = await http.get(BASE_URL + f"getChangedCubeList/{date}")
            resp.raise_for_status()
            return resp.json()

    raw5, was_cached5 = await cached_fetch(cache_key, CACHE_TTL_OBS, _fetcher)
    items5: list[dict] = _unwrap(raw5)
    result5 = [
        {
            "productId": item.get("productId"),
            "releaseTime": item.get("releaseTime"),
        }
        for item in (items5 if isinstance(items5, list) else [])
    ]
    return result5, was_cached5
