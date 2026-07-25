# :bank: Bank of Canada

Exchange rates, interest rates, commodity prices, and inflation data from the [Valet API](https://www.bankofcanada.ca/valet/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (8)

<!-- CATALOG:bank-of-canada:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `boc_get_exchange_rates` | Get daily CAD exchange rates for one or all foreign currencies. | `currency`, `start_date`, `end_date`, `recent` |
| `boc_get_interest_rates` | Get Bank of Canada interest rates including policy rate, CORRA, and bond yields. | `rate_type`, `start_date`, `end_date`, `recent` |
| `boc_get_commodity_prices` | Get Bank of Canada Commodity Price Index (BCPI) data by commodity category. | `commodity_type`, `start_date`, `end_date`, `recent` |
| `boc_get_inflation_data` | Get Consumer Price Index (CPI) inflation data from the Bank of Canada. | `indicator`, `start_date`, `end_date`, `recent` |
| `boc_search_series` | Search available Bank of Canada Valet API data series by keyword. | `keyword` |
| `boc_get_series_metadata` | Get metadata (label, description, link) for a specific Valet API series. | `series_name` |
| `boc_get_observations` | Get raw time-series observations for any Bank of Canada Valet API series. | `series_names`, `start_date`, `end_date`, `recent` |
| `boc_list_groups` | List all available data group collections in the Bank of Canada Valet API. | -- |
<!-- CATALOG:bank-of-canada:end -->

### Example

```
call_tool("boc_get_exchange_rates", {"currency": "USD", "recent": 3})
```

Response:

```json
{
  "_meta": {
    "source": {"api": "bank-of-canada-valet", "url": "https://www.bankofcanada.ca/valet/"},
    "cached": false,
    "lang": "en",
    "timestamp": "2026-04-04T22:16:54.133649+00:00"
  },
  "data": {
    "FXUSDCAD": {
      "label": "USD/CAD",
      "description": "US dollar to Canadian dollar daily exchange rate",
      "observations": {
        "2026-04-02": 1.3918,
        "2026-04-01": 1.3888,
        "2026-03-31": 1.3939
      }
    }
  }
}
```

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `boc_analyze_rates` | Guided | Exchange rate analysis workflow -- chains `boc_search_series` -> `boc_get_exchange_rates` |
| `boc_get_policy_rate` | Quick | Get current BoC overnight policy rate |
| `boc_compare_currencies` | Guided | Compare two currencies over a date range |
| `boc_explore_commodities` | Guided | Explore BCPI commodity prices -- chains `boc_list_groups` -> `boc_get_commodity_prices` |
| `boc_check_inflation` | Quick | Get CPI inflation data |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://boc/currency-codes` | Catalog | 17 FX currency codes with bilingual labels |
| `data://boc/interest-rate-types` | Catalog | Rate types mapped to Valet series codes |
| `data://boc/commodity-types` | Catalog | BCPI commodity categories with bilingual descriptions |
| `data://boc/inflation-indicators` | Catalog | CPI measures with series codes and bilingual descriptions |
| `docs://boc/series-naming` | Guide | FX/rate/CPI/BCPI series naming conventions |
| `docs://boc/api-quirks` | Guide | Date formats, null values, cache TTLs, common 404 causes |
| `template://boc/rate-report` | Template | Exchange rate report with `{currency}`, `{start_date}`, `{latest_value}` |
