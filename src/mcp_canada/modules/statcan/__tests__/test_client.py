"""Unit tests for StatCan WDS client functions.

TDD: RED → GREEN → REFACTOR
All HTTP calls are mocked; no live network access.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Task 1: Schema validation tests
# ---------------------------------------------------------------------------


class TestCubeLiteSchema:
    def test_cube_lite_validates_from_fixture(self, cube_list_lite_response):
        from mcp_canada.modules.statcan.schemas import CubeLite
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

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
            frequency=FREQUENCY_CODES.get(raw["frequencyCode"], "Unknown"),
            subject_codes=raw["subjectCode"],
            survey_codes=raw["surveyCode"],
        )
        assert cube.product_id == 18100004
        assert cube.title_en == "Consumer Price Index, monthly"
        assert cube.frequency_code == 5
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
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

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
            frequency=FREQUENCY_CODES.get(obj["frequencyCode"], "Unknown"),
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
                CodeSetEntry(code=e["uomCode"], desc_en=e["uomDescEn"], desc_fr=e["uomDescFr"])
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
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES, SCALAR_FACTOR_CODES

        obj = series_info_response[0]["object"]
        info = SeriesInfo(
            product_id=obj["productId"],
            coordinate=obj["coordinate"],
            vector_id=obj["vectorId"],
            frequency_code=obj["frequencyCode"],
            frequency=FREQUENCY_CODES.get(obj["frequencyCode"], "Unknown"),
            scalar_factor_code=obj["scalarFactorCode"],
            scalar_factor=SCALAR_FACTOR_CODES.get(obj["scalarFactorCode"], "Unknown"),
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
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES, SCALAR_FACTOR_CODES

        dp = observation_response[0]["object"]["vectorDataPoint"][0]
        row = ObservationRow(
            ref_per=dp["refPer"],
            ref_per_raw=dp["refPerRaw"],
            value=dp["value"],
            decimals=dp["decimals"],
            scalar_factor_code=dp["scalarFactorCode"],
            scalar_factor=SCALAR_FACTOR_CODES.get(dp["scalarFactorCode"], "Unknown"),
            frequency_code=dp["frequencyCode"],
            frequency=FREQUENCY_CODES.get(dp["frequencyCode"], "Unknown"),
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
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES, SCALAR_FACTOR_CODES

        dp = observation_response[0]["object"]["vectorDataPoint"][2]
        row = ObservationRow(
            ref_per=dp["refPer"],
            ref_per_raw=dp["refPerRaw"],
            value=dp["value"],
            decimals=dp["decimals"],
            scalar_factor_code=dp["scalarFactorCode"],
            scalar_factor=SCALAR_FACTOR_CODES.get(dp["scalarFactorCode"], "Unknown"),
            frequency_code=dp["frequencyCode"],
            frequency=FREQUENCY_CODES.get(dp["frequencyCode"], "Unknown"),
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
