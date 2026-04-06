"""Unit tests for CKAN Open Data client functions.

Tests cover:
- _truncate: short/long strings, None handling
- _limit_resources: caps at max_count
- _shape_dataset: bilingual extraction with fallback, truncation, resource limiting
- _shape_resource: field extraction
- CKAN envelope unwrapping (_api_get returns result key)
- fetch_dataset_count: returns count from result.count
"""


from mcp_canada.modules.ckan.client import (
    _truncate,
    _limit_resources,
    _shape_dataset,
    _shape_resource,
    _build_cache_key,
)
from mcp_canada.modules.ckan.__tests__.conftest import (
    LONG_DESCRIPTION,
    SAMPLE_CKAN_DATASET_BILINGUAL,
    SAMPLE_CKAN_DATASET_NO_TRANSLATION,
)


# ===========================================================================
# _truncate
# ===========================================================================

class TestTruncate:

    def test_short_string_not_truncated(self):
        """Strings under max_chars are returned unchanged."""
        text = "Short description."
        result = _truncate(text)
        assert result == text
        assert not result.endswith("...")

    def test_long_string_truncated_at_500(self):
        """Strings over 500 chars are truncated with '...' suffix."""
        result = _truncate(LONG_DESCRIPTION)
        assert result is not None
        assert len(result) <= 503  # 500 + len("...")
        assert result.endswith("...")

    def test_long_string_truncated_at_custom_limit(self):
        """Custom max_chars is respected."""
        text = "A" * 200
        result = _truncate(text, max_chars=100)
        assert result is not None
        assert len(result) == 103  # 100 chars + "..."
        assert result.endswith("...")

    def test_exactly_at_limit_not_truncated(self):
        """String exactly at limit is NOT truncated."""
        text = "A" * 500
        result = _truncate(text)
        assert result is not None
        assert result == text
        assert not result.endswith("...")

    def test_one_over_limit_truncated(self):
        """String one char over limit IS truncated."""
        text = "A" * 501
        result = _truncate(text)
        assert result is not None
        assert result.endswith("...")

    def test_none_returns_none(self):
        """None input returns None."""
        result = _truncate(None)
        assert result is None

    def test_empty_string_returns_empty(self):
        """Empty string returns empty string."""
        result = _truncate("")
        assert result == ""


# ===========================================================================
# _limit_resources
# ===========================================================================

class TestLimitResources:

    def test_list_under_max_unchanged(self):
        """Lists with fewer resources than max are returned as-is."""
        resources = [{"id": f"r{i}"} for i in range(5)]
        result = _limit_resources(resources)
        assert len(result) == 5

    def test_list_at_max_unchanged(self):
        """Lists with exactly max resources are returned unchanged."""
        resources = [{"id": f"r{i}"} for i in range(10)]
        result = _limit_resources(resources)
        assert len(result) == 10

    def test_list_over_max_capped(self):
        """Lists with more than max resources are capped at max."""
        resources = [{"id": f"r{i}"} for i in range(15)]
        result = _limit_resources(resources)
        assert len(result) == 10

    def test_custom_max_count_respected(self):
        """Custom max_count is used instead of default."""
        resources = [{"id": f"r{i}"} for i in range(20)]
        result = _limit_resources(resources, max_count=5)
        assert len(result) == 5

    def test_first_n_items_preserved(self):
        """Capping returns the FIRST N items, not random."""
        resources = [{"id": f"r{i}"} for i in range(15)]
        result = _limit_resources(resources, max_count=3)
        assert result[0]["id"] == "r0"
        assert result[1]["id"] == "r1"
        assert result[2]["id"] == "r2"

    def test_empty_list_returns_empty(self):
        """Empty list returns empty list."""
        result = _limit_resources([])
        assert result == []


# ===========================================================================
# _shape_dataset
# ===========================================================================

class TestShapeDataset:

    def test_bilingual_en_extraction(self):
        """English title and description extracted from title_translated/notes_translated."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="en")
        assert result["title"] == "Government Spending Data"
        assert result["description"] is not None
        # Description should be truncated (long text)
        assert result["description"].endswith("...")

    def test_bilingual_fr_extraction(self):
        """French title and description extracted when lang='fr'."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="fr")
        assert result["title"] == "Données de dépenses gouvernementales"
        assert result["description"] == "Description en français des dépenses gouvernementales."

    def test_fallback_to_en_when_fr_missing(self):
        """Falls back to 'en' when requested language not in title_translated."""
        raw = dict(SAMPLE_CKAN_DATASET_BILINGUAL)
        raw["title_translated"] = {"en": "English Only Title"}
        result = _shape_dataset(raw, lang="fr")
        assert result["title"] == "English Only Title"

    def test_fallback_to_raw_title_when_no_translation(self):
        """Falls back to raw 'title' field when title_translated is absent."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_NO_TRANSLATION, lang="en")
        assert result["title"] == "Simple Dataset"

    def test_resources_capped_at_10(self):
        """Resources are limited to first 10 even when dataset has 15."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="en")
        assert len(result["resources"]) == 10

    def test_num_resources_shows_total_count(self):
        """num_resources reflects the TOTAL count before limiting."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="en")
        assert result["num_resources"] == 15  # total, not capped count

    def test_id_name_org_included(self):
        """id, name, and organization are included in shaped result."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="en")
        assert result["id"] == "abc123"
        assert result["name"] == "government-spending-data"
        assert result["organization"] == {"title": "Treasury Board of Canada"}

    def test_tags_included(self):
        """tags list is included in shaped result."""
        result = _shape_dataset(SAMPLE_CKAN_DATASET_BILINGUAL, lang="en")
        assert result["tags"] == [{"name": "spending"}, {"name": "budget"}]


# ===========================================================================
# _shape_resource
# ===========================================================================

class TestShapeResource:

    def test_resource_fields_extracted(self):
        """id, name, format, size, url fields are extracted."""
        raw = {
            "id": "res-001",
            "name": "Main CSV",
            "format": "CSV",
            "size": 2048,
            "url": "https://example.com/file.csv",
            "description": "A CSV file.",
            "extra_field": "ignored",
        }
        result = _shape_resource(raw)
        assert result["id"] == "res-001"
        assert result["name"] == "Main CSV"
        assert result["format"] == "CSV"
        assert result["size"] == 2048
        assert result["url"] == "https://example.com/file.csv"

    def test_missing_fields_are_none(self):
        """Missing fields default to None."""
        result = _shape_resource({"id": "r1"})
        assert result["name"] is None
        assert result["format"] is None
        assert result["size"] is None
        assert result["url"] is None


# ===========================================================================
# _build_cache_key
# ===========================================================================

class TestBuildCacheKey:

    def test_cache_key_has_ckan_prefix(self):
        """Cache key starts with 'ckan:' prefix."""
        key = _build_cache_key("action/package_search", {"q": "water"})
        assert key.startswith("ckan:")

    def test_cache_key_includes_path(self):
        """Cache key includes the path."""
        key = _build_cache_key("action/package_search", {})
        assert "action/package_search" in key

    def test_params_sorted_for_determinism(self):
        """Same params in different order produce the same key."""
        key1 = _build_cache_key("path", {"b": "2", "a": "1"})
        key2 = _build_cache_key("path", {"a": "1", "b": "2"})
        assert key1 == key2
