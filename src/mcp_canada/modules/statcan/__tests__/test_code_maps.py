"""Regression tests for the StatCan WDS decode maps.

These assert LITERAL expected labels taken from StatCan's published code set
(https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets), NOT values re-derived
from the maps under test.

Why this file exists: the original assertions in test_client.py built their
expected value with `FREQUENCY_CODES.get(raw["frequencyCode"])` — asserting the
map against itself. Those assertions pass for any map, correct or not, and so
shipped a map that reported monthly CPI as "Bi-monthly" for three phases. Every
assertion here must be independently checkable against the upstream code set.

The live-drift counterpart lives in tests/integration/test_tool_scenarios.py
(TestStatCanCodeSetDrift) and fails if StatCan ever changes the published set.
"""

import pytest


# StatCan's published frequency code set, transcribed from getCodeSets.
# 17 entries; note there is no code 3, 5, 8, or 10.
EXPECTED_FREQUENCY = {
    1: "Daily",
    2: "Weekly",
    4: "Biweekly",
    6: "Monthly",
    7: "Bimonthly",
    9: "Quarterly",
    11: "Semi-annual",
    12: "Annual",
    13: "Every 2 years",
    14: "Every 3 years",
    15: "Every 4 years",
    16: "Every 5 years",
    17: "Every 10 years",
    18: "Occasional",
    19: "Occasional Quarterly",
    20: "Occasional Monthly",
    21: "Occasional Daily",
}

# StatCan's published scalar factor code set, transcribed from getCodeSets.
# 10 entries, 0-9, strictly ascending powers of ten.
EXPECTED_SCALAR = {
    0: "units",
    1: "tens",
    2: "hundreds",
    3: "thousands",
    4: "tens of thousands",
    5: "hundreds of thousands",
    6: "millions",
    7: "tens of millions",
    8: "hundreds of millions",
    9: "billions",
}


class TestFrequencyCodes:
    """FREQUENCY_CODES must match StatCan's published frequency code set."""

    def test_map_matches_published_code_set_exactly(self):
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        assert FREQUENCY_CODES == EXPECTED_FREQUENCY

    @pytest.mark.parametrize("code,label", sorted(EXPECTED_FREQUENCY.items()))
    def test_each_code_decodes_to_published_label(self, code, label):
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        assert FREQUENCY_CODES[code] == label

    def test_code_6_is_monthly_not_bimonthly(self):
        """The specific defect: CPI 18100004 is frequencyCode 6 and is monthly.

        Reproduces .planning/phases/08-statcan-wds/08-UAT.md Gap 1 — live
        sc_get_data_by_vector returned one-month-apart reference periods all
        labelled "Bi-monthly".
        """
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        assert FREQUENCY_CODES[6] == "Monthly"
        assert FREQUENCY_CODES[7] == "Bimonthly"

    @pytest.mark.parametrize("absent", [3, 5, 8, 10])
    def test_codes_absent_upstream_are_not_invented(self, absent):
        """StatCan publishes no 3/5/8/10 — the map must not fabricate them."""
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        assert absent not in FREQUENCY_CODES

    def test_long_period_codes_are_present(self):
        """Codes 14-21 were missing entirely, so those series decoded "Unknown"."""
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES

        for code in range(14, 22):
            assert code in FREQUENCY_CODES


class TestScalarFactorCodes:
    """SCALAR_FACTOR_CODES must match StatCan's published scalar code set."""

    def test_map_matches_published_code_set_exactly(self):
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES

        assert SCALAR_FACTOR_CODES == EXPECTED_SCALAR

    @pytest.mark.parametrize("code,label", sorted(EXPECTED_SCALAR.items()))
    def test_each_code_decodes_to_published_label(self, code, label):
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES

        assert SCALAR_FACTOR_CODES[code] == label

    def test_codes_are_ascending_powers_of_ten(self):
        """Scalar factor is a magnitude multiplier: code N means 10^N.

        The shipped map had 1="thousands" (10^3) where upstream means "tens"
        (10^1) — a 100x misread of every scaled observation.
        """
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES

        powers = {
            0: "units", 1: "tens", 2: "hundreds", 3: "thousands",
            4: "tens of thousands", 5: "hundreds of thousands",
            6: "millions", 7: "tens of millions",
            8: "hundreds of millions", 9: "billions",
        }
        for code, label in powers.items():
            assert SCALAR_FACTOR_CODES[code] == label, (
                f"scalar code {code} means 10^{code} ({label})"
            )

    def test_code_888_is_not_invented(self):
        """The shipped map carried a fabricated 888:'null' entry."""
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES

        assert 888 not in SCALAR_FACTOR_CODES


class TestResourceCatalogsMatchMaps:
    """The data:// catalogs must not drift from the constants they document."""

    def test_frequency_resource_matches_constant(self):
        import json
        from mcp_canada.modules.statcan.constants import FREQUENCY_CODES
        from mcp_canada.modules.statcan.resources import statcan_frequency_codes

        catalog = json.loads(statcan_frequency_codes())
        assert {int(k) for k in catalog} == set(FREQUENCY_CODES)
        for code, entry in catalog.items():
            assert entry["en"] == FREQUENCY_CODES[int(code)]
            assert entry["fr"], f"frequency code {code} missing French label"

    def test_scalar_resource_matches_constant(self):
        import json
        from mcp_canada.modules.statcan.constants import SCALAR_FACTOR_CODES
        from mcp_canada.modules.statcan.resources import statcan_scalar_factor_codes

        catalog = json.loads(statcan_scalar_factor_codes())
        assert {int(k) for k in catalog} == set(SCALAR_FACTOR_CODES)
        for code, entry in catalog.items():
            assert entry["en"] == SCALAR_FACTOR_CODES[int(code)]
            assert entry["fr"], f"scalar code {code} missing French label"
