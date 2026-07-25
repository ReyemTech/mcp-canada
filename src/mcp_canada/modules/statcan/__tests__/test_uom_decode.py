"""Tests for UOM label decoding on series info.

Closes 08-UAT.md Gap 2: `sc_get_series_info_by_vector` returned `uom_code` with
no decoded label, even though `frequency` and `scalar_factor` are both decoded
in the same response.

UOM is decoded from the live getCodeSets payload rather than a hardcoded map:
there are 464 codes upstream and the previously hand-written catalog in
resources.py had all 15 of its entries wrong. Codes like 17 ("2002=100") are
index bases, not units, so guessing from the name is not viable.
"""

import pytest
from unittest.mock import AsyncMock, patch


# Real upstream shape, trimmed. memberUomCode 17 is the CPI index base.
FAKE_CODE_SETS = {
    "status": "SUCCESS",
    "object": {
        "frequency": [
            {"frequencyCode": 6, "frequencyDescEn": "Monthly", "frequencyDescFr": "Mensuelle"},
        ],
        "scalar": [
            {"scalarFactorCode": 0, "scalarFactorDescEn": "units", "scalarFactorDescFr": "unités"},
        ],
        "status": [{"statusCode": 0, "statusDescEn": "Normal", "statusDescFr": "Normal"}],
        "symbol": [{"symbolCode": 0, "symbolDescEn": "Not applicable", "symbolDescFr": "Sans objet"}],
        "securityLevel": [
            {"securityLevelCode": 0, "securityLevelDescEn": "Public", "securityLevelDescFr": "Public"}
        ],
        "uom": [
            {"memberUomCode": 17, "memberUomEn": "2002=100", "memberUomFr": "2002=100"},
            {"memberUomCode": 239, "memberUomEn": "Percent", "memberUomFr": "Pourcent"},
            {"memberUomCode": 0, "memberUomEn": None, "memberUomFr": None},
        ],
    },
}


class TestSeriesInfoUomField:
    def test_schema_has_uom_label_field(self):
        """SeriesInfo must expose a decoded label, not just the raw code."""
        from mcp_canada.modules.statcan.schemas import SeriesInfo

        assert "uom" in SeriesInfo.model_fields, (
            "SeriesInfo exposes uom_code but no decoded uom label — 08-UAT Gap 2"
        )

    def test_uom_defaults_to_none_when_not_supplied(self):
        from mcp_canada.modules.statcan.schemas import SeriesInfo

        info = SeriesInfo(
            product_id=18100004, coordinate="2.2", vector_id=41690973,
            frequency_code=6, frequency="Monthly",
            scalar_factor_code=0, scalar_factor="units",
            decimals=1, terminated=False,
            title_en="CPI", title_fr="IPC", uom_code=17,
        )
        assert info.uom is None


class TestUomLookup:
    @pytest.mark.asyncio
    async def test_builds_code_to_label_map_from_code_sets(self):
        from mcp_canada.modules.statcan import client as sc

        with patch.object(sc, "_raw_code_sets", AsyncMock(return_value=FAKE_CODE_SETS["object"])):
            assert await sc._uom_label(17) == "2002=100"
            assert await sc._uom_label(239) == "Percent"

    @pytest.mark.asyncio
    async def test_unknown_code_returns_none(self):
        from mcp_canada.modules.statcan import client as sc

        with patch.object(sc, "_raw_code_sets", AsyncMock(return_value=FAKE_CODE_SETS["object"])):
            assert await sc._uom_label(999999) is None

    @pytest.mark.asyncio
    async def test_null_label_upstream_returns_none(self):
        """memberUomCode 0 has a null label upstream — must not become "None"."""
        from mcp_canada.modules.statcan import client as sc

        with patch.object(sc, "_raw_code_sets", AsyncMock(return_value=FAKE_CODE_SETS["object"])):
            assert await sc._uom_label(0) is None

    @pytest.mark.asyncio
    async def test_code_set_failure_degrades_to_none_not_raise(self):
        """A getCodeSets outage must not take down series-info lookups."""
        import httpx
        from mcp_canada.modules.statcan import client as sc

        boom = AsyncMock(side_effect=httpx.ConnectError("upstream down"))
        with patch.object(sc, "_raw_code_sets", boom):
            assert await sc._uom_label(17) is None


class TestSeriesInfoDecodesUom:
    @pytest.mark.asyncio
    async def test_by_vector_decodes_uom_label(self, series_info_response):
        from mcp_canada.modules.statcan import client as sc

        # fixture carries memberUomCode 239
        series_info_response[0]["object"]["memberUomCode"] = 239

        with patch.object(sc, "_raw_code_sets", AsyncMock(return_value=FAKE_CODE_SETS["object"])), \
             patch.object(sc, "cached_fetch", AsyncMock(return_value=(series_info_response, False))):
            info, _ = await sc.get_series_info_by_vector(41690973)

        assert info.uom_code == 239
        assert info.uom == "Percent", "uom_code must be decoded alongside frequency/scalar"

    @pytest.mark.asyncio
    async def test_by_coord_decodes_uom_label(self, series_info_by_coord_response):
        from mcp_canada.modules.statcan import client as sc

        series_info_by_coord_response[0]["object"]["memberUomCode"] = 17

        with patch.object(sc, "_raw_code_sets", AsyncMock(return_value=FAKE_CODE_SETS["object"])), \
             patch.object(sc, "cached_fetch", AsyncMock(return_value=(series_info_by_coord_response, False))):
            info, _ = await sc.get_series_info_by_coord(35100003, "1.12")

        assert info.uom == "2002=100"


class TestUomResourceCatalogIsHonest:
    """The hand-written catalog had all 15 entries wrong; it must not be fiction."""

    def test_catalog_entries_are_real_upstream_values(self):
        import json
        from mcp_canada.modules.statcan.resources import statcan_uom_codes

        catalog = json.loads(statcan_uom_codes())
        # Spot-check codes whose upstream values are known and were previously wrong.
        assert catalog.get("17", {}).get("en") == "2002=100", (
            "code 17 is the CPI index base, not 'Canadian dollars'"
        )
        assert catalog.get("239", {}).get("en") == "Percent"
        assert "301" not in catalog or catalog["301"]["en"] == "Vehicle-kilometres"

    def test_catalog_points_at_the_full_code_set(self):
        import json
        from mcp_canada.modules.statcan.resources import statcan_uom_codes

        catalog = json.loads(statcan_uom_codes())
        assert "_note" in catalog, (
            "a 464-entry upstream set cannot be fully embedded — the catalog must "
            "tell agents where to get the rest"
        )
        assert "sc_get_code_sets" in catalog["_note"]
