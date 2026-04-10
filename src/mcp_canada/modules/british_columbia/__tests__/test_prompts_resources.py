"""Wave 0 test class scaffolds for british_columbia prompts and resources.

Plan 04 fills in the actual test implementations.
Each class has one xfail placeholder so pytest --collect-only counts them.
"""

from __future__ import annotations

import pytest


class TestBcPrompts:
    """Tests for 6 BC bilingual prompts. Plan 04 implements.

    Covers:
    - bc_explore_wildfires (guided workflow)
    - bc_explore_forestry (guided workflow)
    - bc_explore_environment (guided workflow)
    - bc_quick_dataset_search (quick lookup)
    - bc_check_water_quality (quick lookup)
    - bc_wildfire_status_now (quick lookup)
    """

    @pytest.mark.xfail(reason="Plan 04 will implement", strict=False)
    def test_placeholder(self):
        assert False


class TestBcResources:
    """Tests for 7 BC static resources. Plan 04 implements.

    Covers:
    - data://bc/ministries
    - data://bc/wildfire-status-codes
    - data://bc/object-name-prefixes
    - docs://bc/wfs-query-guide
    - docs://bc/bcdc-api-quirks
    - template://bc/wildfire-report
    - template://bc/dataset-report
    """

    @pytest.mark.xfail(reason="Plan 04 will implement", strict=False)
    def test_placeholder(self):
        assert False
