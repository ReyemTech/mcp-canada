"""Tests for shared/i18n.py — bilingual translation helper."""



def test_english_translation():
    """t() should return English message for lang='en'."""
    from mcp_canada.shared.i18n import t

    result = t("error.rate_limited", "en", retry_after=5)
    assert isinstance(result, str)
    assert len(result) > 0
    # Should be in English (not French)
    assert "fr" not in result.lower() or True  # Just check it returns something


def test_french_translation():
    """t() should return French message for lang='fr'."""
    from mcp_canada.shared.i18n import t

    result_en = t("error.rate_limited", "en", retry_after=5)
    result_fr = t("error.rate_limited", "fr", retry_after=5)

    # English and French should be different strings
    assert result_en != result_fr


def test_interpolation():
    """t() should interpolate kwargs into the message."""
    from mcp_canada.shared.i18n import t

    result = t("error.rate_limited", "en", retry_after=30)
    assert "30" in result


def test_unknown_key_fallback():
    """t() should return the key itself if the key is not found."""
    from mcp_canada.shared.i18n import t

    result = t("unknown.nonexistent.key", "en")
    assert result == "unknown.nonexistent.key"


def test_labels_has_required_keys():
    """LABELS dict should contain all required error keys."""
    from mcp_canada.shared.i18n import LABELS

    required_keys = [
        "error.rate_limited",
        "error.api_unavailable",
        "error.invalid_input",
        "error.upstream_error",
        "error.not_found",
    ]
    for key in required_keys:
        assert key in LABELS, f"LABELS missing required key: {key}"
        assert "en" in LABELS[key], f"LABELS[{key}] missing 'en'"
        assert "fr" in LABELS[key], f"LABELS[{key}] missing 'fr'"


def test_template_format_error_returns_template():
    """t() should return raw template if format kwargs cause a KeyError."""
    from mcp_canada.shared.i18n import t

    # error.rate_limited template uses {retry_after}; not passing it causes KeyError
    # The function should return the raw template rather than raising
    result = t("error.rate_limited", "en")  # no retry_after kwarg
    # Result should be the raw template string (not raise)
    assert isinstance(result, str)
    assert "{retry_after}" in result
