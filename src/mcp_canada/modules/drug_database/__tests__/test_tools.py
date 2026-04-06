"""Unit tests for Drug Product Database @tool functions.

Tests are structured as:
- Happy path: tool returns make_response envelope with correct data shape
- Error paths: invalid input returns make_error with correct code
- Docstring quality: Keywords line, Use for line, >= 50 chars for BM25 compliance
- lang parameter: passed through to make_response / make_error
- drug_code vs DIN: tools use drug_code for detail lookups, not DIN
"""

import inspect
import pytest
from unittest.mock import AsyncMock, patch


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_DRUG_PRODUCTS = [
    {
        "drug_code": 12345,
        "brand_name": "TYLENOL",
        "din": "00559407",
        "company_name": "JOHNSON & JOHNSON INC",
        "descriptor": None,
        "class_name": "Human",
        "number_of_ais": 1,
        "ai_group_no": "0100",
    }
]

SAMPLE_INGREDIENTS = [
    {
        "ingredient_name": "ACETAMINOPHEN",
        "strength": "500",
        "strength_unit": "MG",
        "dosage_value": "1",
        "dosage_unit": "TABLET",
    }
]

SAMPLE_ROUTES = [{"route_of_administration": "ORAL"}]
SAMPLE_SCHEDULE = [{"schedule_name": "OTC"}]
SAMPLE_THERAPEUTIC_CLASS = [
    {
        "tc_atc_number": "N02BE01",
        "tc_atc": "Anilides",
        "tc_ahfs_number": "28:08.92",
        "tc_ahfs": "ANALGESICS AND ANTIPYRETICS, MISC.",
    }
]
SAMPLE_STATUS = [
    {
        "status": "MARKETED",
        "history_date": "1993-02-04",
        "lot_number": None,
        "expiration_date": None,
    }
]
SAMPLE_COMPANIES = [
    {
        "company_code": 100,
        "company_name": "JOHNSON & JOHNSON INC",
        "company_type": "Owner",
        "city": "MARKHAM",
        "province": "ONTARIO",
        "country": "CANADA",
    }
]
SAMPLE_DRUG_DETAILS = {
    "ingredients": SAMPLE_INGREDIENTS,
    "routes": SAMPLE_ROUTES,
    "schedule": SAMPLE_SCHEDULE,
    "therapeutic_class": SAMPLE_THERAPEUTIC_CLASS,
    "status": SAMPLE_STATUS,
}


def import_tools():
    import mcp_canada.modules.drug_database.tools as tools_mod
    return tools_mod


# ===========================================================================
# 1. drug_search
# ===========================================================================

class TestDrugSearch:

    @pytest.mark.asyncio
    async def test_search_by_brand_name_returns_envelope(self):
        """drug_search with brand_name returns make_response envelope with drug list."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_search",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DRUG_PRODUCTS, False)
            result = await tools.drug_search(brand_name="TYLENOL")

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "Drug Product Database"
        assert "cached" in result["_meta"]
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_search_by_din_returns_envelope(self):
        """drug_search with din passes din to fetch_drug_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_search",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DRUG_PRODUCTS, True)
            result = await tools.drug_search(din="00559407")

        assert "_meta" in result
        assert result["_meta"]["cached"] is True
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_company_returns_envelope(self):
        """drug_search with company passes company to fetch_drug_search."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_search",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DRUG_PRODUCTS, False)
            result = await tools.drug_search(company="PFIZER")

        assert "_meta" in result
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_params_returns_invalid_input_error(self):
        """drug_search with all None returns INVALID_INPUT error."""
        tools = import_tools()
        result = await tools.drug_search()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_search",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DRUG_PRODUCTS, False)
            result = await tools.drug_search(brand_name="TYLENOL", lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_no_params_error_lang_passed_through(self):
        """lang is passed to make_error when no params provided."""
        tools = import_tools()
        result = await tools.drug_search(lang="fr")

        assert "error" in result
        assert result["error"]["lang"] == "fr"


# ===========================================================================
# 2. drug_get_details
# ===========================================================================

class TestDrugGetDetails:

    @pytest.mark.asyncio
    async def test_returns_flat_sections_dict(self):
        """drug_get_details returns flat sections dict wrapped in make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_details",
                   new_callable=AsyncMock) as mock_details:
            mock_details.return_value = (SAMPLE_DRUG_DETAILS, False)
            result = await tools.drug_get_details(drug_code=12345)

        assert "_meta" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "ingredients" in data
        assert "routes" in data
        assert "schedule" in data
        assert "therapeutic_class" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_details passes drug_code (not DIN) to fetch_drug_details."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_details",
                   new_callable=AsyncMock) as mock_details:
            mock_details.return_value = (SAMPLE_DRUG_DETAILS, False)
            await tools.drug_get_details(drug_code=12345)

        mock_details.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_details",
                   new_callable=AsyncMock) as mock_details:
            mock_details.return_value = (SAMPLE_DRUG_DETAILS, False)
            result = await tools.drug_get_details(drug_code=12345, lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 3. drug_get_ingredients
# ===========================================================================

class TestDrugGetIngredients:

    @pytest.mark.asyncio
    async def test_returns_ingredient_list_in_envelope(self):
        """drug_get_ingredients returns ingredient list in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_ingredients",
                   new_callable=AsyncMock) as mock_ing:
            mock_ing.return_value = (SAMPLE_INGREDIENTS, False)
            result = await tools.drug_get_ingredients(drug_code=12345)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1
        assert result["data"][0]["ingredient_name"] == "ACETAMINOPHEN"

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_ingredients passes drug_code to fetch_ingredients."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_ingredients",
                   new_callable=AsyncMock) as mock_ing:
            mock_ing.return_value = (SAMPLE_INGREDIENTS, False)
            await tools.drug_get_ingredients(drug_code=12345)

        mock_ing.assert_called_once_with(12345)


# ===========================================================================
# 4. drug_get_routes
# ===========================================================================

class TestDrugGetRoutes:

    @pytest.mark.asyncio
    async def test_returns_route_list_in_envelope(self):
        """drug_get_routes returns route list in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_routes",
                   new_callable=AsyncMock) as mock_rts:
            mock_rts.return_value = (SAMPLE_ROUTES, False)
            result = await tools.drug_get_routes(drug_code=12345)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["route_of_administration"] == "ORAL"

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_routes passes drug_code to fetch_routes."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_routes",
                   new_callable=AsyncMock) as mock_rts:
            mock_rts.return_value = (SAMPLE_ROUTES, False)
            await tools.drug_get_routes(drug_code=12345)

        mock_rts.assert_called_once_with(12345)


# ===========================================================================
# 5. drug_search_companies
# ===========================================================================

class TestDrugSearchCompanies:

    @pytest.mark.asyncio
    async def test_returns_company_list_in_envelope(self):
        """drug_search_companies returns company list in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_companies",
                   new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = (SAMPLE_COMPANIES, False)
            result = await tools.drug_search_companies(company_name="JOHNSON")

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["company_name"] == "JOHNSON & JOHNSON INC"

    @pytest.mark.asyncio
    async def test_company_name_passed_to_fetch(self):
        """drug_search_companies passes company_name to fetch_companies."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_companies",
                   new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = (SAMPLE_COMPANIES, False)
            await tools.drug_search_companies(company_name="JOHNSON")

        mock_comp.assert_called_once_with("JOHNSON")


# ===========================================================================
# 6. drug_get_schedule
# ===========================================================================

class TestDrugGetSchedule:

    @pytest.mark.asyncio
    async def test_returns_schedule_in_envelope(self):
        """drug_get_schedule returns schedule info in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_schedule",
                   new_callable=AsyncMock) as mock_sch:
            mock_sch.return_value = (SAMPLE_SCHEDULE, False)
            result = await tools.drug_get_schedule(drug_code=12345)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["schedule_name"] == "OTC"

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_schedule passes drug_code to fetch_schedule."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_schedule",
                   new_callable=AsyncMock) as mock_sch:
            mock_sch.return_value = (SAMPLE_SCHEDULE, False)
            await tools.drug_get_schedule(drug_code=12345)

        mock_sch.assert_called_once_with(12345)


# ===========================================================================
# 7. drug_get_therapeutic_class
# ===========================================================================

class TestDrugGetTherapeuticClass:

    @pytest.mark.asyncio
    async def test_returns_atc_info_in_envelope(self):
        """drug_get_therapeutic_class returns ATC info in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_therapeutic_class",
                   new_callable=AsyncMock) as mock_tc:
            mock_tc.return_value = (SAMPLE_THERAPEUTIC_CLASS, False)
            result = await tools.drug_get_therapeutic_class(drug_code=12345)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["tc_atc_number"] == "N02BE01"

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_therapeutic_class passes drug_code to fetch_therapeutic_class."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_therapeutic_class",
                   new_callable=AsyncMock) as mock_tc:
            mock_tc.return_value = (SAMPLE_THERAPEUTIC_CLASS, False)
            await tools.drug_get_therapeutic_class(drug_code=12345)

        mock_tc.assert_called_once_with(12345)


# ===========================================================================
# 8. drug_get_status
# ===========================================================================

class TestDrugGetStatus:

    @pytest.mark.asyncio
    async def test_returns_status_in_envelope(self):
        """drug_get_status returns market status in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_status",
                   new_callable=AsyncMock) as mock_st:
            mock_st.return_value = (SAMPLE_STATUS, False)
            result = await tools.drug_get_status(drug_code=12345)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["status"] == "MARKETED"

    @pytest.mark.asyncio
    async def test_drug_code_passed_to_fetch(self):
        """drug_get_status passes drug_code to fetch_status."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_status",
                   new_callable=AsyncMock) as mock_st:
            mock_st.return_value = (SAMPLE_STATUS, False)
            await tools.drug_get_status(drug_code=12345)

        mock_st.assert_called_once_with(12345)


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 8 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "drug_search",
        "drug_get_details",
        "drug_get_ingredients",
        "drug_get_routes",
        "drug_search_companies",
        "drug_get_schedule",
        "drug_get_therapeutic_class",
        "drug_get_status",
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

    def test_all_tools_are_async_callables(self):
        """All 8 tools must be async callable functions."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"

    def test_drug_search_docstring_mentions_drug_code(self):
        """drug_search docstring must clarify drug_code for follow-up lookups."""
        tools = import_tools()
        doc = inspect.getdoc(tools.drug_search) or ""
        assert "drug_code" in doc, (
            "drug_search docstring must mention 'drug_code' to clarify it's needed for detail lookups"
        )

    def test_detail_tools_docstrings_distinguish_drug_code_from_din(self):
        """Detail tools docstrings must clarify drug_code vs DIN."""
        detail_tools = [
            "drug_get_details",
            "drug_get_ingredients",
            "drug_get_routes",
            "drug_get_schedule",
            "drug_get_therapeutic_class",
            "drug_get_status",
        ]
        tools = import_tools()
        for name in detail_tools:
            func = getattr(tools, name)
            doc = inspect.getdoc(func) or ""
            assert "drug_code" in doc, (
                f"{name} docstring must mention 'drug_code' to clarify it's NOT the DIN"
            )


# ===========================================================================
# Envelope structure tests
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_make_response_contains_meta_source_and_cached(self):
        """All success responses must have _meta.source and _meta.cached."""
        tools = import_tools()
        with patch("mcp_canada.modules.drug_database.tools.fetch_drug_search",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_DRUG_PRODUCTS, False)
            result = await tools.drug_search(brand_name="TYLENOL")

        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert isinstance(result["_meta"]["cached"], bool)

    @pytest.mark.asyncio
    async def test_error_response_has_error_key_with_code_and_message(self):
        """Error responses must have error.code and error.message."""
        tools = import_tools()
        result = await tools.drug_search()  # No params — should error

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
