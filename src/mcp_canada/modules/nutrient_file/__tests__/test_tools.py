"""Unit tests for Canadian Nutrient File @tool functions.

Tests verify:
- Each tool returns correct make_response envelope
- nutrient_compare_foods with format="by_food" shapes correctly
- nutrient_compare_foods with format="by_nutrient" pivots correctly
- nutrient_compare_foods validates food_ids length (2-5)
- nutrient_compare_foods with nutrients filter
- All 8 tools have Keywords: and Use for: docstring lines
- lang parameter passed through
"""

import inspect
import pytest
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_FOODS = [
    {"food_id": 1, "food_description": "Apples, raw, with skin", "food_group_id": 9, "food_group_name": "Fruits"},
    {"food_id": 2, "food_description": "Bananas, raw", "food_group_id": 9, "food_group_name": "Fruits"},
]

SAMPLE_FOOD_DETAIL = {
    "food_id": 1,
    "food_description": "Apples, raw, with skin",
    "food_group_id": 9,
    "food_group_name": "Fruits and Fruit Juices",
}

SAMPLE_NUTRIENT_AMOUNTS_APPLE = [
    {"nutrient_name_id": 208, "nutrient_name": "Energy", "nutrient_value": 52.0, "nutrient_unit": "kcal", "nutrient_group": "Proximates"},
    {"nutrient_name_id": 203, "nutrient_name": "Protein", "nutrient_value": 0.26, "nutrient_unit": "g", "nutrient_group": "Proximates"},
]

SAMPLE_NUTRIENT_AMOUNTS_BANANA = [
    {"nutrient_name_id": 208, "nutrient_name": "Energy", "nutrient_value": 89.0, "nutrient_unit": "kcal", "nutrient_group": "Proximates"},
    {"nutrient_name_id": 203, "nutrient_name": "Protein", "nutrient_value": 1.09, "nutrient_unit": "g", "nutrient_group": "Proximates"},
]

SAMPLE_SERVING_SIZES = [
    {"measure_id": 1, "measure_name": "1 medium", "conversion_factor_value": 1.82, "measure_description": "Medium apple"},
]

SAMPLE_NUTRIENT_NAMES = [
    {"nutrient_name_id": 208, "nutrient_name": "Energy", "nutrient_unit": "kcal", "nutrient_group": "Proximates"},
    {"nutrient_name_id": 203, "nutrient_name": "Protein", "nutrient_unit": "g", "nutrient_group": "Proximates"},
]

SAMPLE_FOOD_GROUPS = [
    {"food_group_id": 9, "food_group_name": "Fruits and Fruit Juices"},
    {"food_group_id": 11, "food_group_name": "Vegetables and Vegetable Products"},
]


def import_tools():
    import mcp_canada.modules.nutrient_file.tools as tools_mod
    return tools_mod


# ===========================================================================
# 1. nutrient_search_foods
# ===========================================================================

class TestNutrientSearchFoods:

    @pytest.mark.asyncio
    async def test_search_returns_food_list_in_envelope(self):
        """Happy path: query returns matching foods in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.search_foods",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_FOODS, False)
            result = await tools.nutrient_search_foods(query="apple")

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_search_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.search_foods",
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = (SAMPLE_FOODS, False)
            result = await tools.nutrient_search_foods(query="apple", lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 2. nutrient_get_food_details
# ===========================================================================

class TestNutrientGetFoodDetails:

    @pytest.mark.asyncio
    async def test_get_food_details_returns_food_in_envelope(self):
        """Happy path: food_id returns food detail in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = (SAMPLE_FOOD_DETAIL, False)
            result = await tools.nutrient_get_food_details(food_id=1)

        assert "_meta" in result
        assert result["data"]["food_id"] == 1

    @pytest.mark.asyncio
    async def test_get_food_details_cached_flag_in_meta(self):
        """cached=True is reflected in _meta."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = (SAMPLE_FOOD_DETAIL, True)
            result = await tools.nutrient_get_food_details(food_id=1)

        assert result["_meta"]["cached"] is True


# ===========================================================================
# 3. nutrient_get_nutrient_amounts
# ===========================================================================

class TestNutrientGetNutrientAmounts:

    @pytest.mark.asyncio
    async def test_get_nutrient_amounts_returns_list_in_envelope(self):
        """Happy path: returns nutrient list in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_nutrient_amounts",
                   new_callable=AsyncMock) as mock_nut:
            mock_nut.return_value = (SAMPLE_NUTRIENT_AMOUNTS_APPLE, False)
            result = await tools.nutrient_get_nutrient_amounts(food_id=1)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["nutrient_name"] == "Energy"


# ===========================================================================
# 4. nutrient_get_serving_sizes
# ===========================================================================

class TestNutrientGetServingSizes:

    @pytest.mark.asyncio
    async def test_get_serving_sizes_returns_list_in_envelope(self):
        """Happy path: returns serving sizes in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_serving_sizes",
                   new_callable=AsyncMock) as mock_srv:
            mock_srv.return_value = (SAMPLE_SERVING_SIZES, False)
            result = await tools.nutrient_get_serving_sizes(food_id=1)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["measure_name"] == "1 medium"


# ===========================================================================
# 5. nutrient_search_by_food_group
# ===========================================================================

class TestNutrientSearchByFoodGroup:

    @pytest.mark.asyncio
    async def test_search_by_food_group_returns_food_list(self):
        """Happy path: returns filtered food list in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.search_by_food_group",
                   new_callable=AsyncMock) as mock_grp:
            mock_grp.return_value = (SAMPLE_FOODS, False)
            result = await tools.nutrient_search_by_food_group(food_group_id=9)

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2


# ===========================================================================
# 6. nutrient_list_nutrients
# ===========================================================================

class TestNutrientListNutrients:

    @pytest.mark.asyncio
    async def test_list_nutrients_returns_all_in_envelope(self):
        """Happy path: returns all nutrients in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_nutrients",
                   new_callable=AsyncMock) as mock_nut:
            mock_nut.return_value = (SAMPLE_NUTRIENT_NAMES, True)
            result = await tools.nutrient_list_nutrients()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["_meta"]["cached"] is True


# ===========================================================================
# 7. nutrient_list_food_groups
# ===========================================================================

class TestNutrientListFoodGroups:

    @pytest.mark.asyncio
    async def test_list_food_groups_returns_all_in_envelope(self):
        """Happy path: returns all food groups in make_response envelope."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_food_groups",
                   new_callable=AsyncMock) as mock_grp:
            mock_grp.return_value = (SAMPLE_FOOD_GROUPS, True)
            result = await tools.nutrient_list_food_groups()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2


# ===========================================================================
# 8. nutrient_compare_foods
# ===========================================================================

class TestNutrientCompareFoods:

    def _make_compare_mock(self):
        """Return mock for compare_foods client function."""
        return [
            (SAMPLE_NUTRIENT_AMOUNTS_APPLE, False),
            (SAMPLE_NUTRIENT_AMOUNTS_BANANA, False),
        ]

    def _make_food_detail_mock(self, food_id: int):
        """Return mock food detail for given food_id."""
        descriptions = {1: "Apples, raw, with skin", 2: "Bananas, raw"}
        return ({"food_id": food_id, "food_description": descriptions.get(food_id, f"Food {food_id}")}, False)

    @pytest.mark.asyncio
    async def test_compare_by_food_format_returns_food_keyed_list(self):
        """format='by_food' returns list of {food_id, food_description, nutrients}."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = self._make_compare_mock()
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            result = await tools.nutrient_compare_foods(food_ids=[1, 2], format="by_food")

        assert "_meta" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) == 2
        # Each item should have food_id and nutrients
        assert "food_id" in data[0]
        assert "nutrients" in data[0]

    @pytest.mark.asyncio
    async def test_compare_by_nutrient_format_returns_pivot(self):
        """format='by_nutrient' returns list of {nutrient_name, unit, values dict}."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = self._make_compare_mock()
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            result = await tools.nutrient_compare_foods(food_ids=[1, 2], format="by_nutrient")

        assert "_meta" in result
        data = result["data"]
        assert isinstance(data, list)
        # Each item should have nutrient_name and values dict
        for item in data:
            assert "nutrient_name" in item
            assert "values" in item
            assert isinstance(item["values"], dict)

    @pytest.mark.asyncio
    async def test_compare_validates_minimum_two_foods(self):
        """food_ids with only 1 item returns make_error INVALID_INPUT."""
        tools = import_tools()
        result = await tools.nutrient_compare_foods(food_ids=[1])

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_compare_validates_maximum_five_foods(self):
        """food_ids with 6 items returns make_error INVALID_INPUT."""
        tools = import_tools()
        result = await tools.nutrient_compare_foods(food_ids=[1, 2, 3, 4, 5, 6])

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_compare_accepts_exactly_two_foods(self):
        """food_ids with 2 items is valid (minimum)."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = self._make_compare_mock()
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            result = await tools.nutrient_compare_foods(food_ids=[1, 2])

        assert "_meta" in result, f"Expected success, got: {result}"

    @pytest.mark.asyncio
    async def test_compare_accepts_exactly_five_foods(self):
        """food_ids with 5 items is valid (maximum)."""
        tools = import_tools()
        five_nutrients = [(SAMPLE_NUTRIENT_AMOUNTS_APPLE, False)] * 5
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = five_nutrients
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            result = await tools.nutrient_compare_foods(food_ids=[1, 2, 3, 4, 5])

        assert "_meta" in result, f"Expected success, got: {result}"

    @pytest.mark.asyncio
    async def test_compare_nutrients_filter(self):
        """nutrients filter keeps only matching nutrient_name_ids."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = self._make_compare_mock()
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            # Filter to only Energy (nutrient_name_id=208)
            result = await tools.nutrient_compare_foods(
                food_ids=[1, 2], format="by_food", nutrients=[208]
            )

        assert "_meta" in result
        data = result["data"]
        # Each food's nutrients list should only contain Energy
        for food_data in data:
            for nutrient in food_data["nutrients"]:
                assert nutrient["nutrient_name_id"] == 208

    @pytest.mark.asyncio
    async def test_compare_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.compare_foods",
                   new_callable=AsyncMock) as mock_cmp, \
             patch("mcp_canada.modules.nutrient_file.tools.fetch_food_details",
                   new_callable=AsyncMock) as mock_detail:
            mock_cmp.return_value = self._make_compare_mock()
            mock_detail.side_effect = lambda fid, lang="en": (
                {"food_id": fid, "food_description": f"Food {fid}"}, False
            )
            result = await tools.nutrient_compare_foods(food_ids=[1, 2], lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 8 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "nutrient_search_foods",
        "nutrient_get_food_details",
        "nutrient_get_nutrient_amounts",
        "nutrient_get_serving_sizes",
        "nutrient_search_by_food_group",
        "nutrient_list_nutrients",
        "nutrient_list_food_groups",
        "nutrient_compare_foods",
    ]

    def _get_tool_func(self, name: str):
        tools = import_tools()
        return getattr(tools, name)

    def test_all_tools_have_keywords_line(self):
        """All 8 tools must have 'Keywords:' in their docstring."""
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

    def test_all_tools_are_callable_async(self):
        """All 8 tool functions exist and are callable."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"


# ===========================================================================
# Envelope structure
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_success_response_has_meta_source_and_cached(self):
        """All success responses must have _meta.source and _meta.cached."""
        tools = import_tools()
        with patch("mcp_canada.modules.nutrient_file.tools.fetch_food_groups",
                   new_callable=AsyncMock) as mock_grp:
            mock_grp.return_value = (SAMPLE_FOOD_GROUPS, False)
            result = await tools.nutrient_list_food_groups()

        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]
        assert isinstance(result["_meta"]["cached"], bool)

    @pytest.mark.asyncio
    async def test_error_response_has_code_and_message(self):
        """Error responses must have error.code and error.message."""
        tools = import_tools()
        result = await tools.nutrient_compare_foods(food_ids=[1])  # too few

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
