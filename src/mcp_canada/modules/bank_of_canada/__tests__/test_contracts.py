"""Tests for Bank of Canada module contracts: __init__, constants, and schemas."""



def test_module_name():
    from mcp_canada.modules.bank_of_canada import MODULE_NAME
    assert MODULE_NAME == "bank_of_canada"


def test_module_description_non_empty():
    from mcp_canada.modules.bank_of_canada import MODULE_DESCRIPTION
    assert isinstance(MODULE_DESCRIPTION, str)
    assert len(MODULE_DESCRIPTION) > 0


def test_base_url():
    from mcp_canada.modules.bank_of_canada.constants import BASE_URL
    assert BASE_URL == "https://www.bankofcanada.ca/valet/"


def test_cache_ttl_obs():
    from mcp_canada.modules.bank_of_canada.constants import CACHE_TTL_OBS
    assert CACHE_TTL_OBS == 3600


def test_cache_ttl_meta():
    from mcp_canada.modules.bank_of_canada.constants import CACHE_TTL_META
    assert CACHE_TTL_META == 86400


def test_rate_group():
    from mcp_canada.modules.bank_of_canada.constants import RATE_GROUP
    assert RATE_GROUP == "bank-of-canada"


def test_rate_limit():
    from mcp_canada.modules.bank_of_canada.constants import RATE_LIMIT
    assert RATE_LIMIT == 10.0


def test_interest_rate_series_keys():
    from mcp_canada.modules.bank_of_canada.constants import INTEREST_RATE_SERIES
    assert "policy" in INTEREST_RATE_SERIES
    assert "corra" in INTEREST_RATE_SERIES
    assert "bond_2yr" in INTEREST_RATE_SERIES
    assert "bond_5yr" in INTEREST_RATE_SERIES
    assert "bond_10yr" in INTEREST_RATE_SERIES


def test_fx_group():
    from mcp_canada.modules.bank_of_canada.constants import FX_GROUP
    assert FX_GROUP == "FX_RATES_DAILY"


def test_bcpi_series_keys():
    from mcp_canada.modules.bank_of_canada.constants import BCPI_SERIES
    assert "total" in BCPI_SERIES
    assert "energy" in BCPI_SERIES
    assert "metals" in BCPI_SERIES
    assert "agriculture" in BCPI_SERIES
    assert "forestry" in BCPI_SERIES
    assert "fish" in BCPI_SERIES


def test_cpi_series_keys():
    from mcp_canada.modules.bank_of_canada.constants import CPI_SERIES
    assert "total" in CPI_SERIES
    assert "trim" in CPI_SERIES
    assert "median" in CPI_SERIES
    assert "common" in CPI_SERIES


def test_observation_row_valid():
    from mcp_canada.modules.bank_of_canada.schemas import ObservationRow
    row = ObservationRow(
        date="2026-04-02",
        series_name="FXUSDCAD",
        value=1.39,
        label="USD/CAD",
        description="US dollar to Canadian dollar daily exchange rate",
    )
    assert row.date == "2026-04-02"
    assert row.series_name == "FXUSDCAD"
    assert row.value == 1.39
    assert row.label == "USD/CAD"


def test_observation_row_allows_none_value():
    from mcp_canada.modules.bank_of_canada.schemas import ObservationRow
    row = ObservationRow(
        date="2026-04-02",
        series_name="FXUSDCAD",
        value=None,
        label="USD/CAD",
        description="US dollar to Canadian dollar daily exchange rate",
    )
    assert row.value is None


def test_series_info_valid():
    from mcp_canada.modules.bank_of_canada.schemas import SeriesInfo
    info = SeriesInfo(
        name="FXUSDCAD",
        label="USD/CAD",
        description="US dollar to Canadian dollar daily exchange rate",
    )
    assert info.name == "FXUSDCAD"
    assert info.label == "USD/CAD"


def test_group_info_valid():
    from mcp_canada.modules.bank_of_canada.schemas import GroupInfo
    info = GroupInfo(
        name="FX_RATES_DAILY",
        label="Foreign Exchange Rates Daily",
        description="Daily foreign exchange rates from the Bank of Canada",
    )
    assert info.name == "FX_RATES_DAILY"
    assert info.label == "Foreign Exchange Rates Daily"
