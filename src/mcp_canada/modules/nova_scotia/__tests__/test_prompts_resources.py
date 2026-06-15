"""Unit tests for Nova Scotia module prompts.py and resources.py.

Plan 06 fills TestNsPrompts and TestNsResources with actual test methods.
"""

from __future__ import annotations


class TestNsPrompts:
    """Tests for Nova Scotia @prompt functions. Plan 06 fills.

    Guided workflow prompts (list[Message]) must verify:
    - Returns list with at least 2 messages (user + assistant roles)
    - First message has role="user"
    - Second message has role="assistant"
    - Content references correct ns_ tool names

    Quick lookup prompts (str) must verify:
    - Returns a string
    - String mentions the correct ns_ tool name and key parameters
    """

    pass


class TestNsResources:
    """Tests for Nova Scotia @resource functions. Plan 06 fills.

    data:// resources must verify:
    - Returns valid JSON string
    - JSON is parseable
    - Contains expected top-level keys

    docs:// resources must verify:
    - Returns a string
    - Contains expected sections/headings

    template:// resources must verify:
    - Returns a string with {placeholder} syntax
    """

    pass
