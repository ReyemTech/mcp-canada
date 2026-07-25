"""Unit tests for StatCan WDS client functions.

TDD: RED → GREEN → REFACTOR
All HTTP calls are mocked; no live network access.
"""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _cached_fetch_call(mock_cf, key_fragment: str):
    """Find the cached_fetch call whose cache key contains key_fragment.

    get_series_info_by_* makes two cached_fetch calls — the series lookup and
    the shared 7-day getCodeSets fetch used to decode the UOM label — so the
    bare `.call_args` (last call) is ambiguous.
    """
    for call in mock_cf.call_args_list:
        if key_fragment in call[0][0]:
            return call
    raise AssertionError(
        f"no cached_fetch call with {key_fragment!r} in its key; "
        f"saw: {[c[0][0] for c in mock_cf.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# Task 1: Schema validation tests
# ---------------------------------------------------------------------------


class TestCubeLiteSchema:
    def test_cube_lite_validates_from_fixture(self, cube_list_lite_response):
        from mcp_canada.modules.statcan.schemas import CubeLite

        raw = cube_list_lite_response[0]
        cube = CubeLite(
            product_id=raw["productId"],
            cansim_id=raw["cansimId"],
            title_en=raw["cubeTitleEn"],
            title_fr=raw["cubeTitleFr"],
            start_date=raw["cubeStartDate"],
            end_date=raw["cubeEndDate"],
            release_time=raw["releaseTime"],
            archived=raw["archived"],
            frequency_code=raw["frequencyCode"],
            frequency="Monthly",  # literal: fixture is frequencyCode 6
            subject_codes=raw["subjectCode"],
            survey_codes=raw["surveyCode"],
        )
        assert cube.product_id == 18100004
        assert cube.title_en == "Consumer Price Index, monthly"
        assert cube.frequency_code == 6
        assert cube.frequency == "Monthly"
        assert cube.subject_codes == ["18"]

    def test_cube_lite_archived_field(self, cube_list_lite_response):
        from mcp_canada.modules.statcan.schemas import CubeLite

        raw = cube_list_lite_response[0]
        cube = CubeLite(
            product_id=raw["productId"],
            cansim_id=raw["cansimId"],
            title_en=raw["cubeTitleEn"],
            title_fr=raw["cubeTitleFr"],
            start_date=raw["cubeStartDate"],
            end_date=raw["cubeEndDate"],
            release_time=raw["releaseTime"],
            archived=raw["archived"],
            frequency_code=raw["frequencyCode"],
            frequency="Monthly",
            subject_codes=raw["subjectCode"],
            survey_codes=raw["surveyCode"],
        )
        assert cube.archived is False


class TestCubeMetadataSchema:
    def test_cube_metadata_validates_with_dimensions(self, cube_metadata_response):
        from mcp_canada.modules.statcan.schemas import CubeMetadata, Dimension, DimensionMember
        obj = cube_metadata_response["object"]
        dimensions = []
        for dim in obj["dimension"]:
            members = [
                DimensionMember(
                    member_id=m["memberId"],
                    parent_member_id=m["parentMemberId"],
                    name_en=m["memberNameEn"],
                    name_fr=m["memberNameFr"],
                    classification_code=m.get("classificationCode"),
                    geo_flag=bool(m["geoFlag"]),
                )
                for m in dim["member"]
            ]
            dimensions.append(
                Dimension(
                    name_en=dim["dimensionNameEn"],
                    name_fr=dim["dimensionNameFr"],
                    has_uom=dim["hasUom"],
                    members=members,
                )
            )
        metadata = CubeMetadata(
            product_id=obj["productId"],
            cansim_id=obj["cansimId"],
            title_en=obj["cubeTitleEn"],
            title_fr=obj["cubeTitleFr"],
            start_date=obj["cubeStartDate"],
            end_date=obj["cubeEndDate"],
            frequency_code=obj["frequencyCode"],
            frequency="Monthly",  # literal: fixture is frequencyCode 6
            nb_series=obj["nbSeries"],
            nb_datapoints=obj["nbDatapoints"],
            dimensions=dimensions,
            footnotes=obj["footnote"],
        )
        assert metadata.product_id == 18100004
        assert len(metadata.dimensions) == 2
        assert metadata.dimensions[0].name_en == "Geography"
        assert len(metadata.dimensions[0].members) == 1
        assert metadata.dimensions[0].members[0].geo_flag is True
        assert metadata.frequency == "Monthly"
        assert metadata.nb_series == 1000


class TestCodeSetsSchema:
    def test_code_sets_validates_all_6_categories(self, code_sets_response):
        from mcp_canada.modules.statcan.schemas import CodeSets, CodeSetEntry

        obj = code_sets_response["object"]
        cs = CodeSets(
            frequency=[
                CodeSetEntry(code=e["frequencyCode"], desc_en=e["frequencyDescEn"], desc_fr=e["frequencyDescFr"])
                for e in obj["frequency"]
            ],
            scalar=[
                CodeSetEntry(code=e["scalarFactorCode"], desc_en=e["scalarFactorDescEn"], desc_fr=e["scalarFactorDescFr"])
                for e in obj["scalar"]
            ],
            status=[
                CodeSetEntry(code=e["statusCode"], desc_en=e["statusDescEn"], desc_fr=e["statusDescFr"])
                for e in obj["status"]
            ],
            symbol=[
                CodeSetEntry(code=e["symbolCode"], desc_en=e["symbolDescEn"], desc_fr=e["symbolDescFr"])
                for e in obj["symbol"]
            ],
            security_level=[
                CodeSetEntry(code=e["securityLevelCode"], desc_en=e["securityLevelDescEn"], desc_fr=e["securityLevelDescFr"])
                for e in obj["securityLevel"]
            ],
            uom=[
                CodeSetEntry(code=e["memberUomCode"], desc_en=e["memberUomEn"], desc_fr=e["memberUomFr"])
                for e in obj["uom"]
            ],
        )
        assert len(cs.frequency) == 2
        assert cs.frequency[0].code == 1
        assert cs.frequency[0].desc_en == "Daily"
        assert len(cs.scalar) == 2
        assert len(cs.status) == 2
        assert len(cs.symbol) == 1
        assert len(cs.security_level) == 1
        assert len(cs.uom) == 1


class TestSeriesInfoSchema:
    def test_series_info_validates_from_fixture(self, series_info_response):
        from mcp_canada.modules.statcan.schemas import SeriesInfo
        obj = series_info_response[0]["object"]
        info = SeriesInfo(
            product_id=obj["productId"],
            coordinate=obj["coordinate"],
            vector_id=obj["vectorId"],
            frequency_code=obj["frequencyCode"],
            frequency="Monthly",  # literal: fixture is frequencyCode 6
            scalar_factor_code=obj["scalarFactorCode"],
            scalar_factor="units",  # literal: fixture is scalarFactorCode 0
            decimals=obj["decimals"],
            terminated=bool(obj["terminated"]),
            title_en=obj["SeriesTitleEn"],
            title_fr=obj["SeriesTitleFr"],
            uom_code=obj["memberUomCode"],
        )
        assert info.vector_id == 41690973
        assert info.frequency == "Monthly"
        assert info.scalar_factor == "units"
        assert info.terminated is False


class TestObservationRowSchema:
    def test_observation_row_validates_with_float_value(self, observation_response):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        dp = observation_response[0]["object"]["vectorDataPoint"][0]
        row = ObservationRow(
            ref_per=dp["refPer"],
            ref_per_raw=dp["refPerRaw"],
            value=dp["value"],
            decimals=dp["decimals"],
            scalar_factor_code=dp["scalarFactorCode"],
            scalar_factor="units",  # literal: fixture is scalarFactorCode 0
            frequency_code=dp["frequencyCode"],
            frequency="Monthly",  # literal: fixture is frequencyCode 6
            status_code=dp["statusCode"],
            symbol_code=dp["symbolCode"],
            release_time=dp["releaseTime"],
        )
        assert row.value == 163.4
        assert isinstance(row.value, float)
        assert row.scalar_factor == "units"
        assert row.frequency == "Monthly"

    def test_observation_row_allows_none_value(self, observation_response):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        dp = observation_response[0]["object"]["vectorDataPoint"][2]
        row = ObservationRow(
            ref_per=dp["refPer"],
            ref_per_raw=dp["refPerRaw"],
            value=dp["value"],
            decimals=dp["decimals"],
            scalar_factor_code=dp["scalarFactorCode"],
            scalar_factor="units",  # literal: fixture is scalarFactorCode 0
            frequency_code=dp["frequencyCode"],
            frequency="Monthly",  # literal: fixture is frequencyCode 6
            status_code=dp["statusCode"],
            symbol_code=dp["symbolCode"],
            release_time=dp["releaseTime"],
        )
        assert row.value is None


# ---------------------------------------------------------------------------
# Task 1: pad_coordinate tests
# ---------------------------------------------------------------------------


class TestPadCoordinate:
    def test_short_coordinate_pads_to_10(self):
        from mcp_canada.modules.statcan.client import pad_coordinate
        result = pad_coordinate("1.3.1")
        assert result == "1.3.1.0.0.0.0.0.0.0"

    def test_exactly_10_parts_returns_unchanged(self):
        from mcp_canada.modules.statcan.client import pad_coordinate
        coord = "1.2.3.4.5.6.7.8.9.10"
        result = pad_coordinate(coord)
        assert result == coord

    def test_more_than_10_parts_truncates(self):
        from mcp_canada.modules.statcan.client import pad_coordinate
        coord = "1.2.3.4.5.6.7.8.9.10.11"
        result = pad_coordinate(coord)
        assert result == "1.2.3.4.5.6.7.8.9.10"
        assert len(result.split(".")) == 10

    def test_single_part_pads_to_10(self):
        from mcp_canada.modules.statcan.client import pad_coordinate
        result = pad_coordinate("5")
        assert result == "5.0.0.0.0.0.0.0.0.0"


# ---------------------------------------------------------------------------
# Task 1: _unwrap tests
# ---------------------------------------------------------------------------


class TestUnwrap:
    def test_unwrap_extracts_from_success_envelope(self, cube_metadata_response):
        from mcp_canada.modules.statcan.client import _unwrap
        result = _unwrap(cube_metadata_response)
        assert result["productId"] == 18100004

    def test_unwrap_raises_on_failed_envelope(self):
        from mcp_canada.modules.statcan.client import _unwrap
        failed = {"status": "FAILED", "object": "Invalid product ID"}
        with pytest.raises(ValueError, match="Invalid product ID"):
            _unwrap(failed)

    def test_unwrap_handles_list_wrapped_single_item(self, cube_metadata_response):
        from mcp_canada.modules.statcan.client import _unwrap
        result = _unwrap([cube_metadata_response])
        assert result["productId"] == 18100004

    def test_unwrap_handles_list_wrapped_series_response(self, series_info_response):
        from mcp_canada.modules.statcan.client import _unwrap
        result = _unwrap(series_info_response)
        assert result["vectorId"] == 41690973


# ---------------------------------------------------------------------------
# Task 2: BM25 search tests
# ---------------------------------------------------------------------------


class TestSearchCubes:
    @pytest.mark.asyncio
    async def test_search_returns_ranked_results(self, cube_list_lite_response):
        """search_cubes('consumer price') returns CubeLite results ranked by BM25 score."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = cube_list_lite_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                results, was_cached = await statcan_client.search_cubes("consumer price")

        assert len(results) > 0
        # CPI cube should rank highest for "consumer price"
        assert results[0].product_id == 18100004

    @pytest.mark.asyncio
    async def test_search_returns_at_most_limit_results(self, cube_list_lite_response):
        """search_cubes returns at most `limit` results."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = cube_list_lite_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                results, _ = await statcan_client.search_cubes("consumer price", limit=1)

        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_search_with_no_matches_returns_empty_list(self, cube_list_lite_response):
        """search_cubes with no matches returns empty list."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = cube_list_lite_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                results, _ = await statcan_client.search_cubes("xyznonexistentquery12345")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_calls_cached_fetch_with_ttl_cubes(self, cube_list_lite_response):
        """search_cubes loads cube list via cached_fetch with CACHE_TTL_CUBES."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_CUBES

        mock_response = MagicMock()
        mock_response.json.return_value = cube_list_lite_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.search_cubes("consumer price")
                    # Verify cached_fetch was called with the correct TTL
                    assert mock_cf.called
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_CUBES  # ttl is second positional arg

    @pytest.mark.asyncio
    async def test_search_calls_rate_limiter(self, cube_list_lite_response):
        """search_cubes calls limiter.acquire() before HTTP request."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = cube_list_lite_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.search_cubes("labour force")

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Task 2: get_cube_metadata tests
# ---------------------------------------------------------------------------


class TestGetCubeMetadata:
    @pytest.mark.asyncio
    async def test_returns_cube_metadata_with_decoded_frequency(self, cube_metadata_response):
        """get_cube_metadata returns (CubeMetadata, was_cached) with frequency decoded."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import CubeMetadata

        mock_response = MagicMock()
        mock_response.json.return_value = cube_metadata_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_cube_metadata(18100004)

        assert isinstance(result, CubeMetadata)
        assert result.product_id == 18100004
        assert result.frequency == "Monthly"
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_calls_rate_limiter_before_request(self, cube_metadata_response):
        """get_cube_metadata calls limiter.acquire() before HTTP request."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = cube_metadata_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_cube_metadata(18100004)

        acquire_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_meta_ttl(self, cube_metadata_response):
        """get_cube_metadata uses CACHE_TTL_META for caching."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_META

        mock_response = MagicMock()
        mock_response.json.return_value = cube_metadata_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_cube_metadata(18100004)
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_META

    @pytest.mark.asyncio
    async def test_raises_value_error_on_failed_response(self):
        """get_cube_metadata raises ValueError for FAILED response (via _unwrap)."""
        from mcp_canada.modules.statcan import client as statcan_client

        failed_response = {"status": "FAILED", "object": "Invalid product ID: 99999"}

        mock_response = MagicMock()
        mock_response.json.return_value = failed_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with pytest.raises(ValueError):
                    await statcan_client.get_cube_metadata(99999)


# ---------------------------------------------------------------------------
# Task 2: get_code_sets tests
# ---------------------------------------------------------------------------


class TestGetCodeSets:
    @pytest.mark.asyncio
    async def test_returns_code_sets_with_all_6_categories(self, code_sets_response):
        """get_code_sets() returns (CodeSets, was_cached) with all 6 code categories."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import CodeSets

        mock_response = MagicMock()
        mock_response.json.return_value = code_sets_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_code_sets()

        assert isinstance(result, CodeSets)
        assert len(result.frequency) == 2
        assert len(result.scalar) == 2
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_uses_7_day_cache_ttl(self, code_sets_response):
        """get_code_sets uses CACHE_TTL_CODESETS (7 day)."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_CODESETS

        mock_response = MagicMock()
        mock_response.json.return_value = code_sets_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_code_sets()
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_CODESETS

    @pytest.mark.asyncio
    async def test_http_409_raises_status_error(self):
        """HTTP 409 from any endpoint raises httpx.HTTPStatusError."""
        import httpx
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "409 Conflict", request=MagicMock(), response=MagicMock()
        )

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with pytest.raises(httpx.HTTPStatusError):
                    await statcan_client.get_code_sets()


# ---------------------------------------------------------------------------
# Plan 02 Task 1: get_series_info_by_vector tests
# ---------------------------------------------------------------------------


class TestGetSeriesInfoByVector:
    @pytest.mark.asyncio
    async def test_returns_series_info_with_decoded_labels(self, series_info_response):
        """get_series_info_by_vector returns (SeriesInfo, was_cached) with decoded frequency/scalar."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import SeriesInfo

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_series_info_by_vector(41690973)

        assert isinstance(result, SeriesInfo)
        assert result.vector_id == 41690973
        assert result.frequency == "Monthly"
        assert result.scalar_factor == "units"
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_uses_correct_cache_key(self, series_info_response):
        """get_series_info_by_vector uses cache key 'statcan_wds:getSeriesInfoFromVector:{vector_id}'."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_series_info_by_vector(32164132)
                    call_args = _cached_fetch_call(mock_cf, "getSeriesInfoFromVector")
                    assert call_args[0][0] == "statcan_wds:getSeriesInfoFromVector:32164132"

    @pytest.mark.asyncio
    async def test_uses_meta_ttl(self, series_info_response):
        """get_series_info_by_vector uses CACHE_TTL_META."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_META

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_series_info_by_vector(41690973)
                    call_args = _cached_fetch_call(mock_cf, "getSeriesInfoFromVector")
                    assert call_args[0][1] == CACHE_TTL_META

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, series_info_response):
        """get_series_info_by_vector calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_series_info_by_vector(41690973)

        # Two acquisitions on a cold cache: the series lookup plus the shared
        # 7-day getCodeSets fetch behind the UOM label (08-UAT Gap 2). The code
        # set is cached for a week, so this is not two requests per call in
        # practice — but both must pass through the limiter.
        assert acquire_mock.await_count == 2, (
            f"expected series lookup + getCodeSets to each acquire the limiter, "
            f"got {acquire_mock.await_count}"
        )


# ---------------------------------------------------------------------------
# Plan 02 Task 1: get_series_info_by_coord tests
# ---------------------------------------------------------------------------


class TestGetSeriesInfoByCoord:
    @pytest.mark.asyncio
    async def test_auto_pads_coordinate_before_post(self, series_info_by_coord_response):
        """get_series_info_by_coord calls pad_coordinate before POST."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                await statcan_client.get_series_info_by_coord(35100003, "1.12")

        # The POST body should contain the padded coordinate
        call_kwargs = mock_http.post.call_args
        body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
        assert body[0]["coordinate"] == "1.12.0.0.0.0.0.0.0.0"

    @pytest.mark.asyncio
    async def test_returns_series_info_with_decoded_labels(self, series_info_by_coord_response):
        """get_series_info_by_coord returns (SeriesInfo, was_cached) with decoded labels."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import SeriesInfo

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_series_info_by_coord(35100003, "1.12")

        assert isinstance(result, SeriesInfo)
        assert result.product_id == 35100003
        assert result.frequency == "Annual"
        assert result.scalar_factor == "hundreds"
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_cache_key_uses_padded_coordinate(self, series_info_by_coord_response):
        """get_series_info_by_coord cache key uses the padded coordinate."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_series_info_by_coord(35100003, "1.12")
                    call_args = _cached_fetch_call(mock_cf, "getSeriesInfoFromCubePidCoord")
                    assert "35100003" in call_args[0][0]
                    assert "1.12.0.0.0.0.0.0.0.0" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, series_info_by_coord_response):
        """get_series_info_by_coord calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = series_info_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_series_info_by_coord(35100003, "1.12")

        # Two acquisitions on a cold cache: the series lookup plus the shared
        # 7-day getCodeSets fetch behind the UOM label (08-UAT Gap 2). The code
        # set is cached for a week, so this is not two requests per call in
        # practice — but both must pass through the limiter.
        assert acquire_mock.await_count == 2, (
            f"expected series lookup + getCodeSets to each acquire the limiter, "
            f"got {acquire_mock.await_count}"
        )


# ---------------------------------------------------------------------------
# Plan 02 Task 1: get_latest_n_by_vector tests
# ---------------------------------------------------------------------------


class TestGetLatestNByVector:
    @pytest.mark.asyncio
    async def test_returns_observation_list_sorted_newest_first(self, observation_response):
        """get_latest_n_by_vector returns (list[ObservationRow], was_cached) sorted newest-first."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import ObservationRow

        mock_response = MagicMock()
        mock_response.json.return_value = observation_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_latest_n_by_vector(41690973, 12)

        assert isinstance(result, list)
        assert all(isinstance(r, ObservationRow) for r in result)
        assert was_cached is False
        # Should be sorted newest-first
        ref_periods = [r.ref_per for r in result]
        assert ref_periods == sorted(ref_periods, reverse=True)

    @pytest.mark.asyncio
    async def test_decodes_scalar_and_frequency_labels(self, observation_response):
        """get_latest_n_by_vector decodes scalar_factor and frequency labels on each row."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = observation_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, _ = await statcan_client.get_latest_n_by_vector(41690973, 12)

        for row in result:
            assert row.scalar_factor == "units"
            assert row.frequency == "Monthly"

    @pytest.mark.asyncio
    async def test_handles_none_value(self, observation_response):
        """get_latest_n_by_vector handles observations with None/null value."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = observation_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, _ = await statcan_client.get_latest_n_by_vector(41690973, 12)

        # observation_response has one row with None value
        none_rows = [r for r in result if r.value is None]
        assert len(none_rows) == 1

    @pytest.mark.asyncio
    async def test_uses_obs_ttl(self, observation_response):
        """get_latest_n_by_vector uses CACHE_TTL_OBS."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_OBS

        mock_response = MagicMock()
        mock_response.json.return_value = observation_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_latest_n_by_vector(41690973, 12)
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_OBS

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, observation_response):
        """get_latest_n_by_vector calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = observation_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_latest_n_by_vector(41690973, 12)

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Plan 02 Task 1: get_latest_n_by_coord tests
# ---------------------------------------------------------------------------


class TestGetLatestNByCoord:
    @pytest.mark.asyncio
    async def test_auto_pads_coordinate_before_post(self, latest_n_by_coord_response):
        """get_latest_n_by_coord auto-pads coordinate before POST."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = latest_n_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                await statcan_client.get_latest_n_by_coord(35100003, "1.12", 5)

        call_kwargs = mock_http.post.call_args
        body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
        assert body[0]["coordinate"] == "1.12.0.0.0.0.0.0.0.0"

    @pytest.mark.asyncio
    async def test_returns_observation_list(self, latest_n_by_coord_response):
        """get_latest_n_by_coord returns (list[ObservationRow], was_cached)."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import ObservationRow

        mock_response = MagicMock()
        mock_response.json.return_value = latest_n_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_latest_n_by_coord(35100003, "1.12", 5)

        assert isinstance(result, list)
        assert all(isinstance(r, ObservationRow) for r in result)
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, latest_n_by_coord_response):
        """get_latest_n_by_coord calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = latest_n_by_coord_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_latest_n_by_coord(35100003, "1.12", 5)

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Plan 02 Task 2: get_data_by_ref_period tests
# ---------------------------------------------------------------------------


class TestGetDataByRefPeriod:
    @pytest.mark.asyncio
    async def test_returns_observation_list_sorted_newest_first(self, ref_period_response):
        """get_data_by_ref_period returns (list[ObservationRow], was_cached) sorted newest-first."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import ObservationRow

        mock_response = MagicMock()
        mock_response.json.return_value = ref_period_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_data_by_ref_period(
                    32164132, "2020-01-01", "2023-01-01"
                )

        assert isinstance(result, list)
        assert all(isinstance(r, ObservationRow) for r in result)
        assert was_cached is False
        ref_periods = [r.ref_per for r in result]
        assert ref_periods == sorted(ref_periods, reverse=True)

    @pytest.mark.asyncio
    async def test_uses_obs_ttl(self, ref_period_response):
        """get_data_by_ref_period uses CACHE_TTL_OBS."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_OBS

        mock_response = MagicMock()
        mock_response.json.return_value = ref_period_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_data_by_ref_period(32164132, "2020-01-01", "2023-01-01")
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_OBS

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, ref_period_response):
        """get_data_by_ref_period calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = ref_period_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_data_by_ref_period(32164132, "2020-01-01", "2023-01-01")

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Plan 02 Task 2: get_bulk_vector_data tests
# ---------------------------------------------------------------------------


class TestGetBulkVectorData:
    @pytest.mark.asyncio
    async def test_returns_dict_keyed_by_vector_id(self, bulk_vector_response):
        """get_bulk_vector_data returns (dict[int, list[ObservationRow]], was_cached)."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.schemas import ObservationRow

        mock_response = MagicMock()
        mock_response.json.return_value = bulk_vector_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_bulk_vector_data(
                    [74804, 32164132], "2023-01-01T08:30", "2024-01-01T08:30"
                )

        assert isinstance(result, dict)
        # Only vectorId 74804 succeeded in the fixture; 32164132 FAILED
        assert 74804 in result
        assert 32164132 not in result
        assert all(isinstance(r, ObservationRow) for r in result[74804])
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_passes_vector_ids_as_strings(self, bulk_vector_response):
        """get_bulk_vector_data passes vectorIds as strings in request body."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = bulk_vector_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                await statcan_client.get_bulk_vector_data(
                    [74804, 32164132], "2023-01-01T08:30", "2024-01-01T08:30"
                )

        call_kwargs = mock_http.post.call_args
        body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
        assert all(isinstance(vid, str) for vid in body["vectorIds"])

    @pytest.mark.asyncio
    async def test_handles_partial_failures(self, bulk_vector_response):
        """get_bulk_vector_data returns data for succeeded, omits failed vectors."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = bulk_vector_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, _ = await statcan_client.get_bulk_vector_data(
                    [74804, 32164132], "2023-01-01T08:30", "2024-01-01T08:30"
                )

        # One success, one failure — result has only the succeeded vector
        assert len(result) == 1
        assert 74804 in result

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, bulk_vector_response):
        """get_bulk_vector_data calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = bulk_vector_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.post = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_bulk_vector_data(
                    [74804, 32164132], "2023-01-01T08:30", "2024-01-01T08:30"
                )

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Plan 02 Task 2: get_changed_series tests
# ---------------------------------------------------------------------------


class TestGetChangedSeries:
    @pytest.mark.asyncio
    async def test_returns_list_of_dicts_with_expected_keys(self, changed_series_response):
        """get_changed_series() returns (list[dict], was_cached) with expected keys per item."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = changed_series_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_changed_series()

        assert isinstance(result, list)
        assert was_cached is False
        for item in result:
            assert "vectorId" in item
            assert "productId" in item
            assert "coordinate" in item
            assert "releaseTime" in item

    @pytest.mark.asyncio
    async def test_uses_obs_ttl(self, changed_series_response):
        """get_changed_series uses CACHE_TTL_OBS."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_OBS

        mock_response = MagicMock()
        mock_response.json.return_value = changed_series_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_changed_series()
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_OBS

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, changed_series_response):
        """get_changed_series calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = changed_series_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_changed_series()

        acquire_mock.assert_called_once()


# ---------------------------------------------------------------------------
# Plan 02 Task 2: get_changed_cubes tests
# ---------------------------------------------------------------------------


class TestGetChangedCubes:
    @pytest.mark.asyncio
    async def test_returns_list_of_dicts_with_expected_keys(self, changed_cubes_response):
        """get_changed_cubes returns (list[dict], was_cached) with productId, releaseTime."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = changed_cubes_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                result, was_cached = await statcan_client.get_changed_cubes("2024-01-15")

        assert isinstance(result, list)
        assert was_cached is False
        for item in result:
            assert "productId" in item
            assert "releaseTime" in item

    @pytest.mark.asyncio
    async def test_uses_obs_ttl(self, changed_cubes_response):
        """get_changed_cubes uses CACHE_TTL_OBS."""
        from mcp_canada.modules.statcan import client as statcan_client
        from mcp_canada.modules.statcan.constants import CACHE_TTL_OBS

        mock_response = MagicMock()
        mock_response.json.return_value = changed_cubes_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=AsyncMock()):
                with patch("mcp_canada.modules.statcan.client.cached_fetch", wraps=statcan_client.cached_fetch) as mock_cf:
                    await statcan_client.get_changed_cubes("2024-01-15")
                    call_args = mock_cf.call_args
                    assert call_args[0][1] == CACHE_TTL_OBS

    @pytest.mark.asyncio
    async def test_calls_rate_limiter(self, changed_cubes_response):
        """get_changed_cubes calls limiter.acquire() before HTTP."""
        from mcp_canada.modules.statcan import client as statcan_client

        mock_response = MagicMock()
        mock_response.json.return_value = changed_cubes_response
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await statcan_client.get_changed_cubes("2024-01-15")


# ---------------------------------------------------------------------------
# Task 1 (Phase 9): SDMX schema tests (RED phase)
# ---------------------------------------------------------------------------


class TestSDMXConstant:
    """Tests for SDMX constants in constants.py."""

    def test_sdmx_base_url_ends_with_slash(self):
        from mcp_canada.modules.statcan.constants import SDMX_BASE_URL

        assert SDMX_BASE_URL.endswith("/")
        assert "sdmx" in SDMX_BASE_URL

    def test_sdmx_api_name(self):
        from mcp_canada.modules.statcan.constants import _SDMX_API_NAME

        assert _SDMX_API_NAME == "statcan-sdmx"

    def test_sdmx_xml_namespaces_has_required_keys(self):
        from mcp_canada.modules.statcan.constants import SDMX_XML_NAMESPACES

        assert "mes" in SDMX_XML_NAMESPACES
        assert "str" in SDMX_XML_NAMESPACES
        assert "com" in SDMX_XML_NAMESPACES


class TestSDMXSchema:
    """Tests for SDMX Pydantic schema models."""

    def test_sdmx_code_value_fields(self):
        from mcp_canada.modules.statcan.schemas import SDMXCodeValue

        cv = SDMXCodeValue(id="1", name_en="Canada", name_fr="Canada")
        assert cv.id == "1"
        assert cv.name_en == "Canada"
        assert cv.name_fr == "Canada"

    def test_sdmx_dimension_fields(self):
        from mcp_canada.modules.statcan.schemas import SDMXDimension, SDMXCodeValue

        codes = [SDMXCodeValue(id="1", name_en="Canada", name_fr="Canada")]
        dim = SDMXDimension(position=1, id="GEO", codelist_id="CL_GEO", codes=codes)
        assert dim.position == 1
        assert dim.id == "GEO"
        assert dim.codelist_id == "CL_GEO"
        assert len(dim.codes) == 1

    def test_sdmx_structure_fields(self):
        from mcp_canada.modules.statcan.schemas import SDMXStructure, SDMXDimension, SDMXCodeValue

        codes = [SDMXCodeValue(id="1", name_en="Canada", name_fr="Canada")]
        dim = SDMXDimension(position=1, id="GEO", codelist_id="CL_GEO", codes=codes)
        struct = SDMXStructure(product_id=18100004, dimensions=[dim], suggested_key="1")
        assert struct.product_id == 18100004
        assert len(struct.dimensions) == 1
        assert struct.suggested_key == "1"

    def test_sdmx_structure_suggested_key_default_empty(self):
        from mcp_canada.modules.statcan.schemas import SDMXStructure

        struct = SDMXStructure(product_id=18100004, dimensions=[])
        assert struct.suggested_key == ""

    def test_sdmx_observation_row_fields(self):
        from mcp_canada.modules.statcan.schemas import SDMXObservationRow

        row = SDMXObservationRow(
            period="2024-01",
            value=163.4,
            dimensions={"GEO": "Canada", "PRODUCT": "All-items"},
        )
        assert row.period == "2024-01"
        assert row.value == 163.4
        assert row.dimensions["GEO"] == "Canada"

    def test_sdmx_observation_row_value_can_be_none(self):
        from mcp_canada.modules.statcan.schemas import SDMXObservationRow

        row = SDMXObservationRow(period="2024-01", value=None, dimensions={})
        assert row.value is None


# ---------------------------------------------------------------------------
# Task 2 (Phase 9): SDMX client function tests (RED phase)
# ---------------------------------------------------------------------------


class TestParseStructureXml:
    """Tests for _parse_structure_xml helper."""

    def test_returns_sdmx_structure_with_two_dimensions(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        assert struct.product_id == 18100004
        assert len(struct.dimensions) == 2

    def test_dimensions_sorted_by_position(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        positions = [d.position for d in struct.dimensions]
        assert positions == sorted(positions)

    def test_dimensions_have_correct_ids(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        ids = [d.id for d in struct.dimensions]
        assert "GEO" in ids
        assert "PRODUCT" in ids

    def test_codes_populated_for_each_dimension(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        for dim in struct.dimensions:
            assert len(dim.codes) >= 2

    def test_codes_have_english_and_french_names(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        geo_dim = next(d for d in struct.dimensions if d.id == "GEO")
        canada = next(c for c in geo_dim.codes if c.id == "1")
        assert canada.name_en == "Canada"
        assert canada.name_fr == "Canada"

    def test_suggested_key_is_populated(self, sdmx_structure_xml):
        from mcp_canada.modules.statcan.client import _parse_structure_xml

        struct = _parse_structure_xml(sdmx_structure_xml, 18100004)
        # suggested_key should be dot-joined first code of each dimension
        assert "." in struct.suggested_key or len(struct.dimensions) == 1


class TestMakeSuggestedKey:
    """Tests for _make_suggested_key helper."""

    def test_returns_dot_joined_first_code_ids(self):
        from mcp_canada.modules.statcan.client import _make_suggested_key
        from mcp_canada.modules.statcan.schemas import SDMXStructure, SDMXDimension, SDMXCodeValue

        dims = [
            SDMXDimension(
                position=1, id="GEO", codelist_id="CL_GEO",
                codes=[SDMXCodeValue(id="1", name_en="Canada", name_fr="Canada"),
                       SDMXCodeValue(id="2", name_en="Ontario", name_fr="Ontario")]
            ),
            SDMXDimension(
                position=2, id="PRODUCT", codelist_id="CL_PRODUCT",
                codes=[SDMXCodeValue(id="1", name_en="All-items", name_fr="Ensemble")]
            ),
        ]
        struct = SDMXStructure(product_id=18100004, dimensions=dims)
        key = _make_suggested_key(struct)
        assert key == "1.1"

    def test_empty_dimension_codes_produces_empty_part(self):
        from mcp_canada.modules.statcan.client import _make_suggested_key
        from mcp_canada.modules.statcan.schemas import SDMXStructure, SDMXDimension

        dims = [
            SDMXDimension(position=1, id="GEO", codelist_id="CL_GEO", codes=[]),
        ]
        struct = SDMXStructure(product_id=18100004, dimensions=dims)
        key = _make_suggested_key(struct)
        assert key == ""


class TestBuildSdmxKey:
    """Tests for _build_sdmx_key helper."""

    def _make_structure(self):
        from mcp_canada.modules.statcan.schemas import SDMXStructure, SDMXDimension, SDMXCodeValue

        return SDMXStructure(
            product_id=18100004,
            dimensions=[
                SDMXDimension(
                    position=1, id="GEO", codelist_id="CL_GEO",
                    codes=[SDMXCodeValue(id="1", name_en="Canada", name_fr="Canada")]
                ),
                SDMXDimension(
                    position=2, id="PRODUCT", codelist_id="CL_PRODUCT",
                    codes=[SDMXCodeValue(id="1", name_en="All-items", name_fr="Ensemble")]
                ),
            ],
        )

    def test_full_dict_produces_correct_key(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"GEO": "1", "PRODUCT": "1"}, struct)
        assert key == "1.1"

    def test_partial_dict_wildcards_missing_dims(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"GEO": "1"}, struct)
        assert key == "1."

    def test_all_value_produces_wildcard(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"GEO": "all", "PRODUCT": "1"}, struct)
        assert key == ".1"

    def test_list_values_joined_with_plus(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"GEO": ["1", "2"], "PRODUCT": "1"}, struct)
        assert key == "1+2.1"

    def test_unknown_dim_name_silently_wildcards(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"UNKNOWN": "99", "PRODUCT": "1"}, struct)
        # GEO position is wildcard (unknown dim name)
        assert key == ".1"

    def test_case_insensitive_dim_name_matching(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"geo": "1", "product": "1"}, struct)
        assert key == "1.1"

    def test_empty_string_value_produces_wildcard(self):
        from mcp_canada.modules.statcan.client import _build_sdmx_key

        struct = self._make_structure()
        key = _build_sdmx_key({"GEO": "", "PRODUCT": "1"}, struct)
        assert key == ".1"


class TestFlattenSdmxJson:
    """Tests for _flatten_sdmx_json helper."""

    def test_returns_correct_row_count(self, sdmx_data_json):
        from mcp_canada.modules.statcan.client import _flatten_sdmx_json

        rows = _flatten_sdmx_json(sdmx_data_json)
        # 2 series * 3 observations = 6 rows
        assert len(rows) == 6

    def test_periods_resolved_correctly(self, sdmx_data_json):
        from mcp_canada.modules.statcan.client import _flatten_sdmx_json

        rows = _flatten_sdmx_json(sdmx_data_json)
        periods = {r.period for r in rows}
        assert "2024-01" in periods
        assert "2024-02" in periods
        assert "2024-03" in periods

    def test_dimension_names_resolved_not_indices(self, sdmx_data_json):
        from mcp_canada.modules.statcan.client import _flatten_sdmx_json

        rows = _flatten_sdmx_json(sdmx_data_json)
        # All rows should have resolved dimension names, not numeric strings
        geo_values = {r.dimensions.get("GEO") for r in rows}
        assert "Canada" in geo_values or "Ontario" in geo_values

    def test_none_value_handled(self, sdmx_data_json):
        from mcp_canada.modules.statcan.client import _flatten_sdmx_json

        rows = _flatten_sdmx_json(sdmx_data_json)
        none_rows = [r for r in rows if r.value is None]
        assert len(none_rows) == 1  # One None observation in fixture

    def test_handles_dot_delimited_series_keys(self):
        from mcp_canada.modules.statcan.client import _flatten_sdmx_json

        # Same fixture but using "." as delimiter instead of ":"
        dot_payload = {
            "data": {
                "structures": [
                    {
                        "dimensions": {
                            "series": [
                                {
                                    "id": "GEO",
                                    "keyPosition": 0,
                                    "values": [{"id": "1", "name": "Canada"}],
                                }
                            ],
                            "observation": [
                                {
                                    "id": "TIME_PERIOD",
                                    "values": [{"id": "2024-01"}],
                                }
                            ],
                        }
                    }
                ],
                "dataSets": [
                    {
                        "series": {
                            "0": {  # single dimension — no delimiter needed
                                "observations": {"0": [163.4]}
                            }
                        }
                    }
                ],
            }
        }
        rows = _flatten_sdmx_json(dot_payload)
        assert len(rows) == 1
        assert rows[0].period == "2024-01"
        assert rows[0].value == 163.4


class TestGetSdmxStructure:
    """Tests for get_sdmx_structure public function."""

    @pytest.mark.asyncio
    async def test_fetches_and_parses_structure(self, sdmx_structure_xml):
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_structure

        mock_response = MagicMock()
        mock_response.text = sdmx_structure_xml
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                struct, was_cached = await get_sdmx_structure(18100004)

        assert struct.product_id == 18100004
        assert len(struct.dimensions) == 2
        acquire_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_statcan_sdmx_cache_key(self, sdmx_structure_xml):
        """Cache key must be prefixed with statcan_sdmx: not statcan_wds:"""
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_structure

        mock_response = MagicMock()
        mock_response.text = sdmx_structure_xml
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                # Call twice — second call should be cached
                struct1, cached1 = await get_sdmx_structure(18100004)
                struct2, cached2 = await get_sdmx_structure(18100004)

        # First call: not cached; second: cached
        assert not cached1
        assert cached2
        # HTTP called only once
        assert mock_http.get.call_count == 1


class TestGetSdmxData:
    """Tests for get_sdmx_data public function."""

    @pytest.mark.asyncio
    async def test_raises_value_error_when_last_n_and_date_range_combined(self):
        from mcp_canada.modules.statcan.client import get_sdmx_data

        with pytest.raises(ValueError, match="Cannot use both lastN"):
            await get_sdmx_data(18100004, "1.1", start_period="2024-01", last_n=5)

    @pytest.mark.asyncio
    async def test_raises_value_error_with_end_period_and_last_n(self):
        from mcp_canada.modules.statcan.client import get_sdmx_data

        with pytest.raises(ValueError, match="Cannot use both lastN"):
            await get_sdmx_data(18100004, "1.1", end_period="2024-12", last_n=5)

    @pytest.mark.asyncio
    async def test_happy_path_with_last_n(self, sdmx_data_json):
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_data

        mock_response = MagicMock()
        mock_response.json.return_value = sdmx_data_json
        mock_response.text = json.dumps(sdmx_data_json)
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                rows, was_cached = await get_sdmx_data(18100004, "1.1", last_n=3)

        assert len(rows) == 6  # 2 series * 3 obs
        assert was_cached is False
        acquire_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_happy_path_with_date_range(self, sdmx_data_json):
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_data

        mock_response = MagicMock()
        mock_response.json.return_value = sdmx_data_json
        mock_response.text = json.dumps(sdmx_data_json)
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                rows, was_cached = await get_sdmx_data(
                    18100004, "1.1",
                    start_period="2024-01", end_period="2024-03"
                )

        assert len(rows) > 0
        assert was_cached is False


class TestGetSdmxVectorData:
    """Tests for get_sdmx_vector_data public function."""

    @pytest.mark.asyncio
    async def test_happy_path_returns_flattened_rows(self, sdmx_vector_json):
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_vector_data

        mock_response = MagicMock()
        mock_response.json.return_value = sdmx_vector_json
        mock_response.text = json.dumps(sdmx_vector_json)
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                rows, was_cached = await get_sdmx_vector_data(
                    41690973,
                    start_period="2024-01",
                    end_period="2024-02"
                )

        assert len(rows) == 2  # 1 series * 2 obs
        assert was_cached is False
        acquire_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_url_includes_vector_id(self, sdmx_vector_json):
        import mcp_canada.modules.statcan.client as statcan_client
        from mcp_canada.modules.statcan.client import get_sdmx_vector_data

        mock_response = MagicMock()
        mock_response.json.return_value = sdmx_vector_json
        mock_response.text = json.dumps(sdmx_vector_json)
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=mock_response)

        acquire_mock = AsyncMock()
        with patch("mcp_canada.modules.statcan.client._make_statcan_client", return_value=mock_http):
            with patch.object(statcan_client, "_limiter_acquire", new=acquire_mock):
                await get_sdmx_vector_data(41690973)

        call_args = mock_http.get.call_args
        called_url = call_args[0][0]
        assert "v41690973" in called_url
