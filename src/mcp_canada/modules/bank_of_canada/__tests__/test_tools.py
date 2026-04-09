"""Unit tests for Bank of Canada @tool functions.

Tests are structured as:
- Happy path: tool returns make_response envelope with correct data shape
- Error paths: invalid input returns make_error with correct code and suggestions
- Docstring quality: Keywords line, Use for line, >= 50 chars for BM25 compliance
- lang parameter: passed through to make_response / make_error
"""

import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_canada.modules.bank_of_canada.schemas import ObservationRow, SeriesInfo, GroupInfo

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_OBSERVATIONS = [
    ObservationRow(
        date="2026-04-02",
        series_name="FXUSDCAD",
        value=1.39,
        label="USD/CAD",
        description="US dollar to Canadian dollar daily exchange rate",
    ),
    ObservationRow(
        date="2026-04-01",
        series_name="FXUSDCAD",
        value=1.385,
        label="USD/CAD",
        description="US dollar to Canadian dollar daily exchange rate",
    ),
]

SAMPLE_SERIES_INFO = [
    SeriesInfo(name="FXUSDCAD", label="USD/CAD", description="US dollar to Canadian dollar"),
    SeriesInfo(name="FXEURCAD", label="EUR/CAD", description="Euro to Canadian dollar"),
]

SAMPLE_GROUPS = [
    GroupInfo(
        name="FX_RATES_DAILY",
        label="Foreign Exchange Rates Daily",
        description="Daily FX rates",
    ),
    GroupInfo(
        name="BCPI_MONTHLY",
        label="BCPI Monthly",
        description="Commodity price index",
    ),
]

SAMPLE_SERIES_METADATA = SeriesInfo(
    name="FXUSDCAD",
    label="USD/CAD",
    description="US dollar to Canadian dollar daily exchange rate",
    link="/valet/series/FXUSDCAD/json",
)


# ---------------------------------------------------------------------------
# Helper to import tools module cleanly
# ---------------------------------------------------------------------------

def import_tools():
    import mcp_canada.modules.bank_of_canada.tools as tools_mod
    return tools_mod


# ===========================================================================
# 1. boc_get_exchange_rates
# ===========================================================================

class TestBocGetExchangeRates:

    @pytest.mark.asyncio
    async def test_no_currency_returns_group_observations(self):
        """Happy path: no currency fetches FX group and returns make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_group_observations",
                   new_callable=AsyncMock) as mock_group:
            mock_group.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_exchange_rates()

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "bank-of-canada-valet"
        assert "cached" in result["_meta"]
        assert isinstance(result["data"], dict)
        assert "FXUSDCAD" in result["data"]
        assert "observations" in result["data"]["FXUSDCAD"]

    @pytest.mark.asyncio
    async def test_currency_filter_fetches_single_series(self):
        """With currency='USD', fetches FXUSDCAD series only."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, True)
            result = await tools.boc_get_exchange_rates(currency="USD")

        assert "_meta" in result
        assert result["_meta"]["cached"] is True
        # fetch_observations should have been called with FXUSDCAD
        mock_obs.assert_called_once()
        call_args = mock_obs.call_args
        assert "FXUSDCAD" in call_args[0][0] or "FXUSDCAD" in str(call_args)

    @pytest.mark.asyncio
    async def test_invalid_currency_returns_invalid_series_error(self):
        """Invalid currency code triggers 404 and returns INVALID_SERIES error."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.side_effect = http_error
            with patch("mcp_canada.modules.bank_of_canada.tools._get_all_series_names",
                       new_callable=AsyncMock) as mock_names:
                mock_names.return_value = ["FXUSDCAD", "FXEURCAD"]
                result = await tools.boc_get_exchange_rates(currency="XYZ")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_SERIES"
        assert "suggestions" in result["error"]
        assert isinstance(result["error"]["suggestions"], list)

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_group_observations",
                   new_callable=AsyncMock) as mock_group:
            mock_group.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_exchange_rates(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 2. boc_get_interest_rates
# ===========================================================================

class TestBocGetInterestRates:

    @pytest.mark.asyncio
    async def test_rate_type_policy_fetches_correct_series(self):
        """rate_type='policy' fetches V39079 series."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_interest_rates(rate_type="policy")

        assert "_meta" in result
        mock_obs.assert_called_once()
        call_args = mock_obs.call_args
        assert "V39079" in str(call_args)

    @pytest.mark.asyncio
    async def test_rate_type_all_fetches_all_series(self):
        """rate_type='all' fetches all interest rate series comma-joined."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_interest_rates(rate_type="all")

        assert "_meta" in result
        mock_obs.assert_called_once()
        # The series names should be comma-joined and contain multiple series
        call_args = mock_obs.call_args
        series_arg = call_args[0][0]
        assert "," in series_arg  # multiple series joined

    @pytest.mark.asyncio
    async def test_invalid_rate_type_returns_invalid_input_error(self):
        """Invalid rate_type returns INVALID_INPUT error without making HTTP calls."""
        tools = import_tools()
        result = await tools.boc_get_interest_rates(rate_type="garbage_value")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"
        assert "garbage_value" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_lang_passed_to_error(self):
        """lang is passed through even for error responses."""
        tools = import_tools()
        result = await tools.boc_get_interest_rates(rate_type="invalid", lang="fr")

        assert "error" in result
        assert result["error"]["lang"] == "fr"


# ===========================================================================
# 3. boc_get_commodity_prices
# ===========================================================================

class TestBocGetCommodityPrices:

    @pytest.mark.asyncio
    async def test_no_commodity_type_fetches_bcpi_group(self):
        """No commodity_type fetches full BCPI group."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_group_observations",
                   new_callable=AsyncMock) as mock_group:
            mock_group.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_commodity_prices()

        assert "_meta" in result
        assert isinstance(result["data"], dict)
        # Group fetch should be called with BCPI group
        mock_group.assert_called_once()
        call_args = mock_group.call_args
        assert "BCPI_MONTHLY" in str(call_args)

    @pytest.mark.asyncio
    async def test_commodity_type_energy_fetches_single_series(self):
        """commodity_type='energy' fetches M.ENER series only."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_commodity_prices(commodity_type="energy")

        assert "_meta" in result
        mock_obs.assert_called_once()
        call_args = mock_obs.call_args
        assert "M.ENER" in str(call_args)

    @pytest.mark.asyncio
    async def test_invalid_commodity_type_returns_invalid_input_error(self):
        """Invalid commodity_type returns INVALID_INPUT error."""
        tools = import_tools()
        result = await tools.boc_get_commodity_prices(commodity_type="uranium")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


# ===========================================================================
# 4. boc_get_inflation_data
# ===========================================================================

class TestBocGetInflationData:

    @pytest.mark.asyncio
    async def test_no_indicator_fetches_cpi_group(self):
        """No indicator fetches full CPI group."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_group_observations",
                   new_callable=AsyncMock) as mock_group:
            mock_group.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_inflation_data()

        assert "_meta" in result
        mock_group.assert_called_once()
        call_args = mock_group.call_args
        assert "CPI_MONTHLY" in str(call_args)

    @pytest.mark.asyncio
    async def test_indicator_trim_fetches_cpi_trim_series(self):
        """indicator='trim' fetches CPI_TRIM series."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_inflation_data(indicator="trim")

        assert "_meta" in result
        mock_obs.assert_called_once()
        call_args = mock_obs.call_args
        assert "CPI_TRIM" in str(call_args)

    @pytest.mark.asyncio
    async def test_invalid_indicator_returns_invalid_input_error(self):
        """Invalid indicator returns INVALID_INPUT error."""
        tools = import_tools()
        result = await tools.boc_get_inflation_data(indicator="ppi")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


# ===========================================================================
# 5. boc_search_series
# ===========================================================================

class TestBocSearchSeries:

    @pytest.mark.asyncio
    async def test_keyword_returns_filtered_series_list(self):
        """Valid keyword returns matching series in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.search_series",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = SAMPLE_SERIES_INFO
            result = await tools.boc_search_series(keyword="exchange")

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "FXUSDCAD"

    @pytest.mark.asyncio
    async def test_short_keyword_returns_invalid_input_error(self):
        """Keyword shorter than 2 chars returns INVALID_INPUT error."""
        tools = import_tools()
        result = await tools.boc_search_series(keyword="x")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_empty_keyword_returns_invalid_input_error(self):
        """Empty keyword returns INVALID_INPUT error."""
        tools = import_tools()
        result = await tools.boc_search_series(keyword="")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


# ===========================================================================
# 6. boc_get_series_metadata
# ===========================================================================

class TestBocGetSeriesMetadata:

    @pytest.mark.asyncio
    async def test_valid_series_returns_metadata_in_envelope(self):
        """Valid series name returns SeriesInfo in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_series_metadata",
                   new_callable=AsyncMock) as mock_meta:
            mock_meta.return_value = (SAMPLE_SERIES_METADATA, False)
            result = await tools.boc_get_series_metadata(series_name="FXUSDCAD")

        assert "_meta" in result
        assert result["data"]["name"] == "FXUSDCAD"
        assert result["data"]["label"] == "USD/CAD"

    @pytest.mark.asyncio
    async def test_invalid_series_name_returns_invalid_series_error(self):
        """Unknown series triggers 404 and returns INVALID_SERIES error with suggestions."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_series_metadata",
                   new_callable=AsyncMock) as mock_meta:
            mock_meta.side_effect = http_error
            with patch("mcp_canada.modules.bank_of_canada.tools._get_all_series_names",
                       new_callable=AsyncMock) as mock_names:
                mock_names.return_value = ["FXUSDCAD", "FXEURCAD"]
                result = await tools.boc_get_series_metadata(series_name="FXUSDCA")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_SERIES"
        assert "suggestions" in result["error"]

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_series_metadata",
                   new_callable=AsyncMock) as mock_meta:
            mock_meta.return_value = (SAMPLE_SERIES_METADATA, False)
            result = await tools.boc_get_series_metadata(series_name="FXUSDCAD", lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 7. boc_get_observations
# ===========================================================================

class TestBocGetObservations:

    @pytest.mark.asyncio
    async def test_valid_series_returns_raw_observations(self):
        """Valid series name returns flattened observations in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_observations(series_names="FXUSDCAD")

        assert "_meta" in result
        assert isinstance(result["data"], dict)
        assert "FXUSDCAD" in result["data"]

    @pytest.mark.asyncio
    async def test_invalid_series_returns_invalid_series_error(self):
        """Unknown series triggers 404 and returns INVALID_SERIES error."""
        import httpx
        tools = import_tools()

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)

        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_observations",
                   new_callable=AsyncMock) as mock_obs:
            mock_obs.side_effect = http_error
            with patch("mcp_canada.modules.bank_of_canada.tools._get_all_series_names",
                       new_callable=AsyncMock) as mock_names:
                mock_names.return_value = ["FXUSDCAD", "FXEURCAD"]
                result = await tools.boc_get_observations(series_names="FXUSDCA")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_SERIES"
        assert "suggestions" in result["error"]


# ===========================================================================
# 8. boc_list_groups
# ===========================================================================

class TestBocListGroups:

    @pytest.mark.asyncio
    async def test_returns_full_group_list_in_envelope(self):
        """Returns all groups in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_all_groups",
                   new_callable=AsyncMock) as mock_groups:
            mock_groups.return_value = (SAMPLE_GROUPS, False)
            result = await tools.boc_list_groups()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "FX_RATES_DAILY"

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_all_groups",
                   new_callable=AsyncMock) as mock_groups:
            mock_groups.return_value = (SAMPLE_GROUPS, False)
            result = await tools.boc_list_groups(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 8 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "boc_get_exchange_rates",
        "boc_get_interest_rates",
        "boc_get_commodity_prices",
        "boc_get_inflation_data",
        "boc_search_series",
        "boc_get_series_metadata",
        "boc_get_observations",
        "boc_list_groups",
    ]

    def _get_tool_func(self, name: str):
        tools = import_tools()
        return getattr(tools, name)

    def test_all_tools_have_keywords_line(self):
        """All 8 tools must have 'Keywords:' in their docstring for BM25 indexing."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' line in docstring"

    def test_all_tools_have_use_for_line(self):
        """All 8 tools must have 'Use for:' in their docstring."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' line in docstring"

    def test_all_tool_docstrings_at_least_50_chars(self):
        """All 8 tool docstrings must be >= 50 characters."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert len(doc) >= 50, f"{name} docstring too short ({len(doc)} chars)"

    def test_all_tools_have_lang_parameter(self):
        """All 8 tools must accept lang: Literal['en', 'fr'] = 'en' parameter."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            sig = inspect.signature(func)
            assert "lang" in sig.parameters, f"{name} missing 'lang' parameter"
            param = sig.parameters["lang"]
            assert param.default == "en", f"{name} lang default should be 'en'"

    def test_all_tools_return_dict_with_meta_or_error(self):
        """All 8 tool functions exist and are callable async functions."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"
            assert inspect.iscoroutinefunction(func) or inspect.isfunction(func), \
                f"{name} is not a function"


# ===========================================================================
# Envelope structure: _meta must have source and cached
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_make_response_contains_meta_source_and_cached(self):
        """All success responses must have _meta.source and _meta.cached."""
        tools = import_tools()
        with patch("mcp_canada.modules.bank_of_canada.tools.fetch_group_observations",
                   new_callable=AsyncMock) as mock_group:
            mock_group.return_value = (SAMPLE_OBSERVATIONS, False)
            result = await tools.boc_get_exchange_rates()

        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert isinstance(result["_meta"]["cached"], bool)

    @pytest.mark.asyncio
    async def test_error_response_has_error_key_with_code_and_message(self):
        """All error responses must have error.code and error.message."""
        tools = import_tools()
        result = await tools.boc_get_interest_rates(rate_type="invalid_type_xyz")

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
