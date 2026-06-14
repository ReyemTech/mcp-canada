"""Manitoba prompts and resources unit tests.

Wave 0 placeholder classes — Plan 07 fills test bodies.
"""

from __future__ import annotations


class TestManitobaPrompts:
    """Unit tests for all Manitoba @prompt functions.

    Plan 07 fills — verifies:
    - All 6 prompts are discoverable via FastMCP Client
    - Guided workflow prompts return list[Message] (at least 2 messages)
    - Quick lookup prompts return str
    - lang parameter passes through correctly
    """

    pass


class TestManitobaResources:
    """Unit tests for all Manitoba @resource functions.

    Plan 07 fills — verifies:
    - All ~7 resources are discoverable via FastMCP Client (resources/list)
    - data:// resources return valid JSON strings
    - docs:// resources return non-empty markdown strings
    - Zero-parameter resources do NOT appear as ResourceTemplates
    """

    pass
