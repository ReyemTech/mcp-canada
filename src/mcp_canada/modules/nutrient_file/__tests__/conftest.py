"""Test fixtures for Canadian Nutrient File client tests."""

import pytest
from unittest.mock import MagicMock


# Sample food list (5 items from different food groups)
SAMPLE_FOOD_LIST = [
    {
        "food_id": 1,
        "food_description": "Apples, raw, with skin",
        "food_group_id": 9,
        "food_group_name": "Fruits and Fruit Juices",
    },
    {
        "food_id": 2,
        "food_description": "Bananas, raw",
        "food_group_id": 9,
        "food_group_name": "Fruits and Fruit Juices",
    },
    {
        "food_id": 3,
        "food_description": "Broccoli, raw",
        "food_group_id": 11,
        "food_group_name": "Vegetables and Vegetable Products",
    },
    {
        "food_id": 4,
        "food_description": "Chicken breast, cooked",
        "food_group_id": 5,
        "food_group_name": "Poultry Products",
    },
    {
        "food_id": 5,
        "food_description": "Milk, whole",
        "food_group_id": 1,
        "food_group_name": "Dairy and Egg Products",
    },
]

# Sample nutrient amounts for a single food
SAMPLE_NUTRIENT_AMOUNTS = [
    {
        "nutrient_name_id": 208,
        "nutrient_name": "Energy",
        "nutrient_value": 52.0,
        "nutrient_unit": "kcal",
        "nutrient_group": "Proximates",
    },
    {
        "nutrient_name_id": 203,
        "nutrient_name": "Protein",
        "nutrient_value": 0.26,
        "nutrient_unit": "g",
        "nutrient_group": "Proximates",
    },
    {
        "nutrient_name_id": 204,
        "nutrient_name": "Total Fat",
        "nutrient_value": 0.17,
        "nutrient_unit": "g",
        "nutrient_group": "Proximates",
    },
]

# Sample serving sizes
SAMPLE_SERVING_SIZES = [
    {
        "measure_id": 1,
        "measure_name": "1 medium (approx 3\" dia)",
        "conversion_factor_value": 1.82,
        "measure_description": "Medium apple",
    },
    {
        "measure_id": 2,
        "measure_name": "1 cup, sliced",
        "conversion_factor_value": 1.09,
        "measure_description": "Sliced apple",
    },
]

# Sample nutrient names list
SAMPLE_NUTRIENT_NAMES = [
    {
        "nutrient_name_id": 203,
        "nutrient_name": "Protein",
        "nutrient_unit": "g",
        "nutrient_group": "Proximates",
    },
    {
        "nutrient_name_id": 204,
        "nutrient_name": "Total Fat",
        "nutrient_unit": "g",
        "nutrient_group": "Proximates",
    },
    {
        "nutrient_name_id": 208,
        "nutrient_name": "Energy",
        "nutrient_unit": "kcal",
        "nutrient_group": "Proximates",
    },
]

# Sample food groups
SAMPLE_FOOD_GROUPS = [
    {
        "food_group_id": 1,
        "food_group_name": "Dairy and Egg Products",
    },
    {
        "food_group_id": 9,
        "food_group_name": "Fruits and Fruit Juices",
    },
    {
        "food_group_id": 11,
        "food_group_name": "Vegetables and Vegetable Products",
    },
]


def make_mock_response(data) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_food_list():
    """Sample food list for testing."""
    return SAMPLE_FOOD_LIST


@pytest.fixture
def sample_nutrient_amounts():
    """Sample nutrient amounts for a food."""
    return SAMPLE_NUTRIENT_AMOUNTS


@pytest.fixture
def sample_serving_sizes():
    """Sample serving sizes for a food."""
    return SAMPLE_SERVING_SIZES


@pytest.fixture
def sample_nutrient_names():
    """Sample nutrient names."""
    return SAMPLE_NUTRIENT_NAMES


@pytest.fixture
def sample_food_groups():
    """Sample food groups."""
    return SAMPLE_FOOD_GROUPS


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
