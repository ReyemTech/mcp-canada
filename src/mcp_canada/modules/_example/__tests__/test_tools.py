"""Colocated module-internal unit tests for the _example module tools."""



def test_example_echo_returns_envelope():
    """example_echo should return a dict with _meta and data keys."""
    import asyncio
    from mcp_canada.modules._example.tools import example_echo

    result = asyncio.run(example_echo("hello", lang="en"))
    assert isinstance(result, dict), "Response should be a dict"
    assert "_meta" in result, "Response should have '_meta' key"
    assert "data" in result, "Response should have 'data' key"


def test_example_echo_french():
    """example_echo with lang='fr' should set _meta.lang to 'fr'."""
    import asyncio
    from mcp_canada.modules._example.tools import example_echo

    result = asyncio.run(example_echo("bonjour", lang="fr"))
    assert result["_meta"]["lang"] == "fr", "_meta.lang should be 'fr'"


def test_example_echo_description_quality():
    """example_echo tool description should be >= 50 chars and contain 'Keywords:'."""
    from mcp_canada.modules._example.tools import example_echo

    # Get the function's docstring (the tool description)
    description = example_echo.__doc__ or ""
    assert len(description) >= 50, (
        f"Description must be >= 50 chars, got {len(description)}: {description!r}"
    )
    assert "Keywords:" in description, (
        f"Description must contain 'Keywords:' for BM25 indexing. Got: {description!r}"
    )
