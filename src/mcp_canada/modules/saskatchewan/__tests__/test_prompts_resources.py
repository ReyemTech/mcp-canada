"""Saskatchewan prompts and resources tests.

Plan 06 fills the test bodies for 6 prompts and 7 resources.
Wave 0 defines placeholder classes so downstream plans reference specific node IDs.
"""

from __future__ import annotations

import pytest


class TestSaskPrompts:
    """All 6 Saskatchewan @prompt functions.

    Plan 06 fills:
    - 3 guided workflow prompts (return list[Message], user+assistant roles)
    - 3 quick lookup prompts (return str with tool name + parameter instructions)
    Each prompt has lang='en' and lang='fr' test case.
    """

    pass


class TestSaskResources:
    """All 7 Saskatchewan @resource functions.

    Plan 06 fills:
    - data:// resources return valid JSON
    - docs:// resources return non-empty markdown strings
    - template:// resources contain {placeholder} syntax
    - All resources have ZERO parameters (no lang param)
    """

    pass
