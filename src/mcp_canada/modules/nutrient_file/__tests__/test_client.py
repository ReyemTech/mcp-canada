"""Unit tests for Canadian Nutrient File client functions.

Tests verify:
- search_foods filters correctly from cached full list
- search_by_food_group filters by food_group_id from cached full list
- Both search functions use the same cache key (shared fetch_all_foods)
- compare_foods uses asyncio.gather for parallel fetches
- Cache keys include lang param for bilingual isolation
"""

import pytest
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# Inline test data (mirrors conftest.py fixtures)
# ---------------------------------------------------------------------------

SAMPLE_FOOD_LIST = [
    {"food_id": 1, "food_description": "Apples, raw, with skin", "food_group_id": 9, "food_group_name": "Fruits and Fruit Juices"},
    {"food_id": 2, "food_description": "Bananas, raw", "food_group_id": 9, "food_group_name": "Fruits and Fruit Juices"},
    {"food_id": 3, "food_description": "Broccoli, raw", "food_group_id": 11, "food_group_name": "Vegetables and Vegetable Products"},
    {"food_id": 4, "food_description": "Chicken breast, cooked", "food_group_id": 5, "food_group_name": "Poultry Products"},
    {"food_id": 5, "food_description": "Milk, whole", "food_group_id": 1, "food_group_name": "Dairy and Egg Products"},
]

SAMPLE_NUTRIENT_AMOUNTS = [
    {"nutrient_name_id": 208, "nutrient_name": "Energy", "nutrient_value": 52.0, "nutrient_unit": "kcal", "nutrient_group": "Proximates"},
    {"nutrient_name_id": 203, "nutrient_name": "Protein", "nutrient_value": 0.26, "nutrient_unit": "g", "nutrient_group": "Proximates"},
]


# ---------------------------------------------------------------------------
# Helper: import client lazily so we can patch before use
# ---------------------------------------------------------------------------

def import_client():
    import mcp_canada.modules.nutrient_file.client as client_mod
    return client_mod


# ===========================================================================
# Cache key tests
# ===========================================================================

class TestCacheKeys:

    def test_cache_key_has_nut_prefix(self):
        """Cache keys must start with 'nut:' prefix."""
        client = import_client()
        key = client._build_cache_key("food", {"lang": "en", "type": "json"})
        assert key.startswith("nut:")

    def test_cache_key_includes_lang(self):
        """Cache keys must include the lang param for bilingual isolation."""
        client = import_client()
        key_en = client._build_cache_key("food", {"lang": "en"})
        key_fr = client._build_cache_key("food", {"lang": "fr"})
        assert "lang=en" in key_en
        assert "lang=fr" in key_fr
        assert key_en != key_fr

    def test_cache_key_deterministic_sorted_params(self):
        """Cache keys are deterministic regardless of param insertion order."""
        client = import_client()
        key1 = client._build_cache_key("food", {"type": "json", "lang": "en"})
        key2 = client._build_cache_key("food", {"lang": "en", "type": "json"})
        assert key1 == key2

    def test_fetch_all_foods_cache_key_consistent(self):
        """fetch_all_foods cache key matches expected pattern for bilingual isolation."""
        client = import_client()
        # The key for full food list fetch
        key_en = client._build_cache_key("food", {"lang": "en", "type": "json"})
        key_fr = client._build_cache_key("food", {"lang": "fr", "type": "json"})
        assert "nut:food" in key_en
        assert "lang=en" in key_en
        assert "lang=fr" in key_fr


# ===========================================================================
# fetch_all_foods tests
# ===========================================================================

class TestFetchAllFoods:

    @pytest.mark.asyncio
    async def test_fetch_all_foods_returns_list_and_cached_flag(self):
        """fetch_all_foods returns (list[dict], bool) tuple."""
        client = import_client()
        with patch.object(client, "cached_fetch", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (SAMPLE_FOOD_LIST, False)
            result, was_cached = await client.fetch_all_foods("en")

        assert isinstance(result, list)
        assert isinstance(was_cached, bool)
        assert was_cached is False

    @pytest.mark.asyncio
    async def test_fetch_all_foods_uses_7_day_cache(self):
        """fetch_all_foods uses CACHE_TTL (7 days = 604800 seconds)."""
        client = import_client()
        with patch.object(client, "cached_fetch", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (SAMPLE_FOOD_LIST, False)
            await client.fetch_all_foods("en")

        # Check TTL passed to cached_fetch is CACHE_TTL (7 days)
        call_args = mock_cache.call_args
        ttl_arg = call_args[0][1]  # second positional arg is ttl
        assert ttl_arg == 604800, f"Expected 7-day TTL (604800), got {ttl_arg}"

    @pytest.mark.asyncio
    async def test_fetch_all_foods_lang_in_cache_key(self):
        """fetch_all_foods includes lang in cache key."""
        client = import_client()
        with patch.object(client, "cached_fetch", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = (SAMPLE_FOOD_LIST, False)
            await client.fetch_all_foods("fr")

        cache_key = mock_cache.call_args[0][0]
        assert "lang=fr" in cache_key


# ===========================================================================
# search_foods tests
# ===========================================================================

class TestSearchFoods:

    @pytest.mark.asyncio
    async def test_search_foods_filters_by_name_substring(self):
        """search_foods returns only foods matching the query in food_description."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            results, cached = await client.search_foods("apple", "en")

        # Only "Apples, raw, with skin" should match
        assert len(results) == 1
        assert results[0]["food_description"] == "Apples, raw, with skin"

    @pytest.mark.asyncio
    async def test_search_foods_case_insensitive(self):
        """search_foods is case-insensitive."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            results_upper, _ = await client.search_foods("BANANA", "en")
            results_lower, _ = await client.search_foods("banana", "en")

        assert len(results_upper) == len(results_lower) == 1
        assert results_upper[0]["food_id"] == 2

    @pytest.mark.asyncio
    async def test_search_foods_no_match_returns_empty(self):
        """search_foods returns empty list when no foods match."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            results, _ = await client.search_foods("sushi", "en")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_foods_inherits_cached_flag(self):
        """search_foods returns the cached flag from underlying fetch_all_foods."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, True)  # cache hit
            _, cached = await client.search_foods("apple", "en")

        assert cached is True

    @pytest.mark.asyncio
    async def test_search_foods_calls_fetch_all_foods_once(self):
        """search_foods calls fetch_all_foods (not a separate API call)."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            await client.search_foods("apple", "en")

        mock_all.assert_called_once()


# ===========================================================================
# search_by_food_group tests
# ===========================================================================

class TestSearchByFoodGroup:

    @pytest.mark.asyncio
    async def test_search_by_food_group_filters_by_id(self):
        """search_by_food_group returns only foods in the specified food_group_id."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            results, _ = await client.search_by_food_group(9, "en")  # Fruits

        # food_group_id 9 = Apples + Bananas
        assert len(results) == 2
        food_ids = {r["food_id"] for r in results}
        assert food_ids == {1, 2}

    @pytest.mark.asyncio
    async def test_search_by_food_group_no_match_returns_empty(self):
        """search_by_food_group returns empty list for unknown food_group_id."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            results, _ = await client.search_by_food_group(999, "en")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_by_food_group_calls_fetch_all_foods(self):
        """search_by_food_group calls fetch_all_foods (shares the cached full list)."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            await client.search_by_food_group(9, "en")

        mock_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_both_search_functions_call_fetch_all_foods(self):
        """Both search_foods and search_by_food_group call fetch_all_foods — same cached fetch."""
        client = import_client()
        with patch.object(client, "fetch_all_foods", new_callable=AsyncMock) as mock_all:
            mock_all.return_value = (SAMPLE_FOOD_LIST, False)
            await client.search_foods("apple", "en")
            await client.search_by_food_group(9, "en")

        # Each called fetch_all_foods once (both route through it)
        assert mock_all.call_count == 2


# ===========================================================================
# compare_foods tests
# ===========================================================================

class TestCompareFoods:

    @pytest.mark.asyncio
    async def test_compare_foods_returns_list_of_results(self):
        """compare_foods returns a list of (nutrient_amounts, cached) tuples."""
        client = import_client()
        with patch.object(client, "fetch_nutrient_amounts", new_callable=AsyncMock) as mock_nut:
            mock_nut.return_value = (SAMPLE_NUTRIENT_AMOUNTS, False)
            results = await client.compare_foods([1, 2], "en")

        assert isinstance(results, list)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_compare_foods_uses_asyncio_gather(self):
        """compare_foods uses asyncio.gather for parallel fetches."""
        client = import_client()
        # Patch asyncio.gather in the client module's namespace
        with patch("mcp_canada.modules.nutrient_file.client.asyncio.gather", new_callable=AsyncMock) as mock_gather:
            mock_gather.return_value = [
                (SAMPLE_NUTRIENT_AMOUNTS, False),
                (SAMPLE_NUTRIENT_AMOUNTS, False),
            ]
            await client.compare_foods([1, 2], "en")

        mock_gather.assert_called_once()

    @pytest.mark.asyncio
    async def test_compare_foods_fetches_each_food_id(self):
        """compare_foods calls fetch_nutrient_amounts for each food_id."""
        client = import_client()
        with patch.object(client, "fetch_nutrient_amounts", new_callable=AsyncMock) as mock_nut:
            mock_nut.return_value = (SAMPLE_NUTRIENT_AMOUNTS, False)
            await client.compare_foods([1, 2, 3], "en")

        assert mock_nut.call_count == 3
        call_food_ids = [c[0][0] for c in mock_nut.call_args_list]
        assert set(call_food_ids) == {1, 2, 3}
