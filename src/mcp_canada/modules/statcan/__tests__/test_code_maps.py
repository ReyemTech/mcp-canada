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


class TestNoSeriesForCoordinate:
    """A coordinate with no series must not crash on Pydantic validation.

    Regression cover for the Phase 20.1 defect. StatCan answers
    getSeriesInfoFromCubePidCoord for an unpopulated coordinate with
    status=SUCCESS and responseStatusCode=2 ("Invalid cube and series
    combination"), where every field is null:

        {"responseStatusCode": 2, "productId": 18100004,
         "coordinate": "1.1.0.0.0.0.0.0.0.0", "vectorId": 0,
         "frequencyCode": null, "scalarFactorCode": null, ...}

    _unwrap only special-cased responseStatusCode 2 when the OUTER status was
    not SUCCESS, so this fell through, SeriesInfo was constructed from nulls,
    and the tool surfaced "UPSTREAM_ERROR: 6 validation errors for SeriesInfo".
    A coordinate that carries no series is a NOT_FOUND, not an upstream fault.
    """

    NO_SERIES = [{
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 2,
            "productId": 18100004,
            "coordinate": "1.1.0.0.0.0.0.0.0.0",
            "vectorId": 0,
            "frequencyCode": None,
            "scalarFactorCode": None,
            "decimals": None,
            "terminated": None,
            "SeriesTitleEn": None,
            "SeriesTitleFr": None,
            "memberUomCode": None,
        },
    }]

    @pytest.mark.asyncio
    async def test_raises_valueerror_not_pydantic_error(self):
        from unittest.mock import AsyncMock, patch
        from mcp_canada.modules.statcan import client as sc

        with patch.object(sc, "cached_fetch", AsyncMock(return_value=(self.NO_SERIES, False))):
            with pytest.raises(ValueError) as exc:
                await sc.get_series_info_by_coord(18100004, "1.1.0.0.0.0.0.0.0.0")

        msg = str(exc.value)
        assert "validation error" not in msg.lower(), (
            f"a coordinate with no series must fail cleanly, not leak a Pydantic "
            f"validation error: {msg}"
        )
        assert "coordinate" in msg.lower(), f"the message should name the problem: {msg}"

    @pytest.mark.asyncio
    async def test_tool_returns_not_found(self):
        from unittest.mock import AsyncMock, patch
        from mcp_canada.modules.statcan import client as sc
        from mcp_canada.modules.statcan.tools import sc_get_series_info_by_coord

        with patch.object(sc, "cached_fetch", AsyncMock(return_value=(self.NO_SERIES, False))):
            fn = getattr(sc_get_series_info_by_coord, "fn", sc_get_series_info_by_coord)
            result = await fn(product_id=18100004, coordinate="1.1.0.0.0.0.0.0.0.0")

        assert "error" in result, f"expected a structured error, got: {result}"
        assert result["error"]["code"] == "NOT_FOUND", (
            f"an empty coordinate is NOT_FOUND, not an upstream fault: {result['error']}"
        )

    @pytest.mark.asyncio
    async def test_populated_coordinate_still_works(self):
        """Coordinate 2.2.0.0... is CPI all-items Canada and must be unaffected."""
        from unittest.mock import AsyncMock, patch
        from mcp_canada.modules.statcan import client as sc

        ok = [{
            "status": "SUCCESS",
            "object": {
                "responseStatusCode": 0, "productId": 18100004,
                "coordinate": "2.2.0.0.0.0.0.0.0.0", "vectorId": 41690973,
                "frequencyCode": 6, "scalarFactorCode": 0, "decimals": 1,
                "terminated": 0, "SeriesTitleEn": "Canada;All-items",
                "SeriesTitleFr": "Canada;Ensemble", "memberUomCode": 17,
            },
        }]
        with patch.object(sc, "cached_fetch", AsyncMock(return_value=(ok, False))), \
             patch.object(sc, "_raw_code_sets", AsyncMock(return_value={"uom": []})):
            info, _ = await sc.get_series_info_by_coord(18100004, "2.2.0.0.0.0.0.0.0.0")

        assert info.vector_id == 41690973
        assert info.frequency == "Monthly"


class TestSdmxEmptyResultIsMalformedUpstream:
    """StatCan emits INVALID JSON for an empty SDMX result.

    Regression cover for the Phase 20.1 defect. Asking for a key with no data
    (DF_18100004 key 1.1) returns HTTP 200 with a body carrying two surplus
    closing braces:

        ..."dataSets": [{ "action": "Information","series":{ }}}}],"structure":...
                                                            ^^^^ should be }}

    resp.json() therefore raises JSONDecodeError, which subclasses ValueError
    and was caught by the handler meant for the last_n/date-range conflict — so
    a malformed upstream body surfaced as
    "INVALID_INPUT: Expecting ',' delimiter: line 1 column 200", blaming the
    caller for StatCan's broken output.

    Two things must hold: an empty result is an empty list, and a genuinely
    unparseable body is an UPSTREAM_ERROR rather than INVALID_INPUT.
    """

    EMPTY_BODY = (
        '{ "header": {"id":"x","prepared":"2026-07-25T01:09:14","test":false,'
        '"sender":{"id":"unknown","name":"unknown"}},"dataSets": [{ "action": '
        '"Information","series":{ }}}}],"structure":{"name":"CPI",'
        '"description":null,"dimensions":{"dataset":null,"series":null,'
        '"observation":null},"attributes":{"dataset":null,"series":null,'
        '"observation":null}}}'
    )

    @staticmethod
    def _mock_http(body: str):
        from unittest.mock import AsyncMock, MagicMock
        import json as _json

        resp = MagicMock()
        resp.text = body
        resp.raise_for_status = MagicMock()

        def _json_raises():
            return _json.loads(body)

        resp.json = _json_raises
        http = AsyncMock()
        http.__aenter__ = AsyncMock(return_value=http)
        http.__aexit__ = AsyncMock(return_value=False)
        http.get = AsyncMock(return_value=resp)
        return http

    @pytest.mark.asyncio
    async def test_empty_sdmx_result_returns_empty_list(self):
        from unittest.mock import AsyncMock, patch
        from mcp_canada.modules.statcan import client as sc

        with patch.object(sc, "_make_statcan_client", return_value=self._mock_http(self.EMPTY_BODY)), \
             patch.object(sc, "_limiter_acquire", AsyncMock()):
            rows, cached = await sc.get_sdmx_data(18100004, "1.1", last_n=3)

        assert rows == [], (
            f"a key with no observations must yield an empty list, not a parse "
            f"failure. Got: {rows}"
        )

    @pytest.mark.asyncio
    async def test_genuinely_broken_body_is_upstream_not_invalid_input(self):
        from unittest.mock import AsyncMock, patch
        from mcp_canada.modules.statcan import client as sc
        from mcp_canada.modules.statcan.tools import sc_get_sdmx_data

        garbage = "<html>502 Bad Gateway</html>"
        fn = getattr(sc_get_sdmx_data, "fn", sc_get_sdmx_data)
        with patch.object(sc, "_make_statcan_client", return_value=self._mock_http(garbage)), \
             patch.object(sc, "_limiter_acquire", AsyncMock()):
            result = await fn(product_id=18100004, key="1.1", last_n=3)

        assert "error" in result, f"expected a structured error, got: {result}"
        assert result["error"]["code"] == "UPSTREAM_ERROR", (
            f"an unparseable upstream body is the service's fault, not the "
            f"caller's: {result['error']}"
        )

    @pytest.mark.asyncio
    async def test_conflicting_params_still_invalid_input(self):
        """The real INVALID_INPUT case must keep its code."""
        from mcp_canada.modules.statcan.tools import sc_get_sdmx_data

        fn = getattr(sc_get_sdmx_data, "fn", sc_get_sdmx_data)
        result = await fn(
            product_id=18100004, key="1.1", last_n=3, start_period="2024-01"
        )
        assert result["error"]["code"] == "INVALID_INPUT", (
            f"lastN + date range is genuinely a caller error: {result}"
        )
