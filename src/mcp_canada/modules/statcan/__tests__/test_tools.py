"""Unit tests for StatCan WDS @tool functions.

TDD: RED → GREEN → REFACTOR

Tests follow pattern:
- Happy path: mock client returns (data, was_cached), verify make_response envelope
- Error 409: mock raises HTTPStatusError with 409, verify UPSTREAM_UNAVAILABLE
- Generic error: mock raises Exception, verify UPSTREAM_ERROR
- Lang passthrough: call with lang="fr", verify _meta.lang == "fr"
- Quality: verify all tools have Use for: and Keywords: in docstring
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

# ─── Quality tests ────────────────────────────────────────────────────────────


class TestToolDocstringQuality:
    """Verify all tools have required BM25 discovery metadata in docstrings."""

    def _get_all_tools(self):
        from mcp_canada.modules.statcan import tools
        tool_names = [
            "sc_search_cubes",
            "sc_get_cube_metadata",
            "sc_get_code_sets",
            "sc_get_series_info_by_vector",
            "sc_get_series_info_by_coord",
            "sc_get_data_by_vector",
            "sc_get_data_by_coord",
            "sc_get_data_by_date_range",
            "sc_get_bulk_vector_data",
            "sc_get_changed_series",
            "sc_get_changed_cubes",
        ]
        return [(name, getattr(tools, name)) for name in tool_names]

    def test_all_tools_have_use_for_line(self):
        for name, fn in self._get_all_tools():
            doc = inspect.getdoc(fn) or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' in docstring"

    def test_all_tools_have_keywords_line(self):
        for name, fn in self._get_all_tools():
            doc = inspect.getdoc(fn) or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' in docstring"

    def test_all_tools_have_eight_or_more_keywords(self):
        for name, fn in self._get_all_tools():
            doc = inspect.getdoc(fn) or ""
            kw_line = ""
            for line in doc.split("\n"):
                if "Keywords:" in line:
                    kw_line = line
                    break
            keywords = [k.strip() for k in kw_line.replace("Keywords:", "").split(",") if k.strip()]
            assert len(keywords) >= 8, (
                f"{name} has only {len(keywords)} keywords (need >= 8): {keywords}"
            )


# ─── Helper to make mock 409 HTTPStatusError ─────────────────────────────────


def _make_409_error() -> httpx.HTTPStatusError:
    mock_resp = MagicMock()
    mock_resp.status_code = 409
    return httpx.HTTPStatusError("maintenance", request=MagicMock(), response=mock_resp)


def _make_500_error() -> httpx.HTTPStatusError:
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    return httpx.HTTPStatusError("server error", request=MagicMock(), response=mock_resp)


# ─── sc_search_cubes ─────────────────────────────────────────────────────────


class TestScSearchCubes:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_data(self):
        from mcp_canada.modules.statcan.schemas import CubeLite
        mock_cube = CubeLite(
            product_id=18100004,
            cansim_id="326-0021",
            title_en="Consumer Price Index, monthly",
            title_fr="Indice des prix",
            start_date="1914-01",
            end_date="2026-03",
            release_time="2026-03-19",
            archived=False,
            frequency_code=5,
            frequency="Monthly",
            subject_codes=["18"],
            survey_codes=["2301"],
        )
        with patch(
            "mcp_canada.modules.statcan.tools.search_cubes",
            new=AsyncMock(return_value=([mock_cube], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_search_cubes
            result = await sc_search_cubes("consumer price")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "statcan-wds"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1
        assert result["data"][0]["product_id"] == 18100004

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.search_cubes",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_search_cubes
            result = await sc_search_cubes("consumer price")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"
        assert "maintenance" in result["error"]["message"].lower() or "08:30" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_generic_exception_returns_upstream_error(self):
        with patch(
            "mcp_canada.modules.statcan.tools.search_cubes",
            new=AsyncMock(side_effect=Exception("network failure")),
        ):
            from mcp_canada.modules.statcan.tools import sc_search_cubes
            result = await sc_search_cubes("consumer price")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passthrough(self):
        with patch(
            "mcp_canada.modules.statcan.tools.search_cubes",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_search_cubes
            result = await sc_search_cubes("consumer", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_cube_metadata ─────────────────────────────────────────────────────


class TestScGetCubeMetadata:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_metadata(self):
        from mcp_canada.modules.statcan.schemas import CubeMetadata
        mock_meta = CubeMetadata(
            product_id=18100004,
            cansim_id="326-0021",
            title_en="Consumer Price Index, monthly",
            title_fr="Indice des prix",
            start_date="1914-01",
            end_date="2026-03",
            frequency_code=5,
            frequency="Monthly",
            nb_series=1000,
            nb_datapoints=500000,
            dimensions=[],
            footnotes=[],
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_cube_metadata",
            new=AsyncMock(return_value=(mock_meta, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_cube_metadata
            result = await sc_get_cube_metadata(18100004)
        assert "_meta" in result
        assert result["data"]["product_id"] == 18100004

    @pytest.mark.asyncio
    async def test_value_error_returns_upstream_error(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_cube_metadata",
            new=AsyncMock(side_effect=ValueError("FAILED WDS response")),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_cube_metadata
            result = await sc_get_cube_metadata(999999999)
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_cube_metadata",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_cube_metadata
            result = await sc_get_cube_metadata(18100004)
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr_passthrough(self):
        from mcp_canada.modules.statcan.schemas import CubeMetadata
        mock_meta = CubeMetadata(
            product_id=18100004, cansim_id="", title_en="", title_fr="",
            start_date="", end_date="", frequency_code=5, frequency="Monthly",
            nb_series=0, nb_datapoints=0, dimensions=[], footnotes=[],
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_cube_metadata",
            new=AsyncMock(return_value=(mock_meta, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_cube_metadata
            result = await sc_get_cube_metadata(18100004, lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_code_sets ─────────────────────────────────────────────────────────


class TestScGetCodeSets:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_code_sets(self):
        from mcp_canada.modules.statcan.schemas import CodeSetEntry, CodeSets
        mock_sets = CodeSets(
            frequency=[CodeSetEntry(code=5, desc_en="Monthly", desc_fr="Mensuel")],
            scalar=[CodeSetEntry(code=0, desc_en="units", desc_fr="unités")],
            status=[CodeSetEntry(code=0, desc_en="Normal", desc_fr="Normal")],
            symbol=[],
            security_level=[],
            uom=[],
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_code_sets",
            new=AsyncMock(return_value=(mock_sets, True)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_code_sets
            result = await sc_get_code_sets()
        assert "_meta" in result
        assert result["_meta"]["cached"] is True
        assert "frequency" in result["data"]
        assert "scalar" in result["data"]

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_code_sets",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_code_sets
            result = await sc_get_code_sets()
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_code_sets",
            new=AsyncMock(side_effect=Exception("timeout")),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_code_sets
            result = await sc_get_code_sets()
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ─── sc_get_series_info_by_vector ─────────────────────────────────────────────


class TestScGetSeriesInfoByVector:

    @pytest.mark.asyncio
    async def test_returns_make_response(self):
        from mcp_canada.modules.statcan.schemas import SeriesInfo
        mock_info = SeriesInfo(
            product_id=18100004, coordinate="1.1", vector_id=32164132,
            frequency_code=5, frequency="Monthly", scalar_factor_code=0,
            scalar_factor="units", decimals=1, terminated=False,
            title_en="CPI", title_fr="IPC", uom_code=239,
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_vector",
            new=AsyncMock(return_value=(mock_info, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_vector
            result = await sc_get_series_info_by_vector(32164132)
        assert "_meta" in result
        assert result["data"]["vector_id"] == 32164132

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_vector",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_vector
            result = await sc_get_series_info_by_vector(32164132)
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        from mcp_canada.modules.statcan.schemas import SeriesInfo
        mock_info = SeriesInfo(
            product_id=18100004, coordinate="1.1", vector_id=32164132,
            frequency_code=5, frequency="Monthly", scalar_factor_code=0,
            scalar_factor="units", decimals=1, terminated=False,
            title_en="CPI", title_fr="IPC", uom_code=239,
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_vector",
            new=AsyncMock(return_value=(mock_info, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_vector
            result = await sc_get_series_info_by_vector(32164132, lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_series_info_by_coord ─────────────────────────────────────────────


class TestScGetSeriesInfoByCoord:

    @pytest.mark.asyncio
    async def test_returns_make_response(self):
        from mcp_canada.modules.statcan.schemas import SeriesInfo
        mock_info = SeriesInfo(
            product_id=35100003, coordinate="1.12.0.0.0.0.0.0.0.0", vector_id=32164132,
            frequency_code=9, frequency="Annual", scalar_factor_code=6,
            scalar_factor="hundreds", decimals=2, terminated=False,
            title_en="GDP", title_fr="PIB", uom_code=301,
        )
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_coord",
            new=AsyncMock(return_value=(mock_info, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_coord
            result = await sc_get_series_info_by_coord(35100003, "1.12")
        assert "_meta" in result
        assert result["data"]["product_id"] == 35100003

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_coord",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_coord
            result = await sc_get_series_info_by_coord(35100003, "1.12")
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_value_error_returns_upstream_error(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_series_info_by_coord",
            new=AsyncMock(side_effect=ValueError("bad coord")),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_series_info_by_coord
            result = await sc_get_series_info_by_coord(35100003, "bad")
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ─── sc_get_data_by_vector ────────────────────────────────────────────────────


class TestScGetDataByVector:

    @pytest.mark.asyncio
    async def test_returns_observations_list(self):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        mock_rows = [
            ObservationRow(
                ref_per="2026-03", ref_per_raw="2026-03", value=163.4,
                decimals=1, scalar_factor_code=0, scalar_factor="units",
                frequency_code=5, frequency="Monthly", status_code=0,
                symbol_code=0, release_time="2026-03-19 08:30",
            ),
        ]
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_vector",
            new=AsyncMock(return_value=(mock_rows, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_vector
            result = await sc_get_data_by_vector(32164132, 12)
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1
        assert result["data"][0]["value"] == 163.4

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_vector",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_vector
            result = await sc_get_data_by_vector(32164132)
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_vector",
            new=AsyncMock(side_effect=Exception("timeout")),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_vector
            result = await sc_get_data_by_vector(32164132)
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_vector",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_vector
            result = await sc_get_data_by_vector(32164132, lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_data_by_coord ─────────────────────────────────────────────────────


class TestScGetDataByCoord:

    @pytest.mark.asyncio
    async def test_returns_observations_list(self):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        mock_rows = [
            ObservationRow(
                ref_per="2023-01", ref_per_raw="2023-01", value=99.5,
                decimals=1, scalar_factor_code=0, scalar_factor="units",
                frequency_code=9, frequency="Annual", status_code=0,
                symbol_code=0, release_time="2023-03-01 08:30",
            ),
        ]
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_coord",
            new=AsyncMock(return_value=(mock_rows, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_coord
            result = await sc_get_data_by_coord(35100003, "1.12", 5)
        assert "_meta" in result
        assert result["data"][0]["ref_per"] == "2023-01"

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_coord",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_coord
            result = await sc_get_data_by_coord(35100003, "1.12")
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_latest_n_by_coord",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_coord
            result = await sc_get_data_by_coord(35100003, "1.12", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_data_by_date_range ────────────────────────────────────────────────


class TestScGetDataByDateRange:

    @pytest.mark.asyncio
    async def test_returns_observations_list(self):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        mock_rows = [
            ObservationRow(
                ref_per="2023-01", ref_per_raw="2023-01", value=99.5,
                decimals=1, scalar_factor_code=0, scalar_factor="units",
                frequency_code=9, frequency="Annual", status_code=0,
                symbol_code=0, release_time="2023-03-01 08:30",
            ),
        ]
        with patch(
            "mcp_canada.modules.statcan.tools.get_data_by_ref_period",
            new=AsyncMock(return_value=(mock_rows, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_date_range
            result = await sc_get_data_by_date_range(32164132, "2020-01-01", "2023-01-01")
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_data_by_ref_period",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_date_range
            result = await sc_get_data_by_date_range(32164132, "2020-01-01", "2023-01-01")
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_data_by_ref_period",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_data_by_date_range
            result = await sc_get_data_by_date_range(32164132, "2020-01-01", "2023-01-01", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_bulk_vector_data ──────────────────────────────────────────────────


class TestScGetBulkVectorData:

    @pytest.mark.asyncio
    async def test_returns_make_response_with_dict(self):
        from mcp_canada.modules.statcan.schemas import ObservationRow
        mock_row = ObservationRow(
            ref_per="2024-01", ref_per_raw="2024-01", value=150.2,
            decimals=1, scalar_factor_code=0, scalar_factor="units",
            frequency_code=5, frequency="Monthly", status_code=0,
            symbol_code=0, release_time="2024-02-15 08:30",
        )
        mock_data: dict[int, list] = {74804: [mock_row]}
        with patch(
            "mcp_canada.modules.statcan.tools.get_bulk_vector_data",
            new=AsyncMock(return_value=(mock_data, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_bulk_vector_data
            result = await sc_get_bulk_vector_data([74804, 32164132], "2023-01-01T08:30", "2024-01-01T08:30")
        assert "_meta" in result
        assert "74804" in result["data"] or 74804 in result["data"]

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_bulk_vector_data",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_bulk_vector_data
            result = await sc_get_bulk_vector_data([74804], "2023-01-01T08:30", "2024-01-01T08:30")
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_bulk_vector_data",
            new=AsyncMock(return_value=({}, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_bulk_vector_data
            result = await sc_get_bulk_vector_data([74804], "2023-01-01T08:30", "2024-01-01T08:30", lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_changed_series ────────────────────────────────────────────────────


class TestScGetChangedSeries:

    @pytest.mark.asyncio
    async def test_returns_list_of_changed_series(self):
        mock_data = [
            {"vectorId": 41690973, "productId": 18100004, "coordinate": "1.1", "releaseTime": "2026-04-07 08:30"},
            {"vectorId": 32164132, "productId": 35100003, "coordinate": "1.12", "releaseTime": "2026-04-07 08:30"},
        ]
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_series",
            new=AsyncMock(return_value=(mock_data, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_series
            result = await sc_get_changed_series()
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_series",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_series
            result = await sc_get_changed_series()
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_series",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_series
            result = await sc_get_changed_series(lang="fr")
        assert result["_meta"]["lang"] == "fr"


# ─── sc_get_changed_cubes ─────────────────────────────────────────────────────


class TestScGetChangedCubes:

    @pytest.mark.asyncio
    async def test_returns_list_of_changed_cubes(self):
        mock_data = [
            {"productId": 18100004, "releaseTime": "2026-04-07 08:30"},
        ]
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_cubes",
            new=AsyncMock(return_value=(mock_data, False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_cubes
            result = await sc_get_changed_cubes("2024-01-15")
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["productId"] == 18100004

    @pytest.mark.asyncio
    async def test_409_returns_upstream_unavailable(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_cubes",
            new=AsyncMock(side_effect=_make_409_error()),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_cubes
            result = await sc_get_changed_cubes("2024-01-15")
        assert result["error"]["code"] == "UPSTREAM_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_cubes",
            new=AsyncMock(side_effect=Exception("timeout")),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_cubes
            result = await sc_get_changed_cubes("2024-01-15")
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_fr(self):
        with patch(
            "mcp_canada.modules.statcan.tools.get_changed_cubes",
            new=AsyncMock(return_value=([], False)),
        ):
            from mcp_canada.modules.statcan.tools import sc_get_changed_cubes
            result = await sc_get_changed_cubes("2024-01-15", lang="fr")
        assert result["_meta"]["lang"] == "fr"
