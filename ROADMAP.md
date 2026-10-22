# Roadmap

Public roadmap for mcp-canada — the MCP server for Canadian government data.

## Shipped

### Federal Government Data

| Module | Tools | Data Source |
|--------|-------|------------|
| Bank of Canada | 8 | Exchange rates, interest rates, CPI, commodity prices |
| Open Parliament | 6 | Bills, votes, MPs, debates |
| Recalls | 3 | Product, vehicle, food recalls |
| Drug Database | 5 | Drug products, ingredients, companies |
| CKAN | 4 | Federal open data catalogue (250K+ datasets) |
| Nutrient File | 4 | Canadian food nutrient database |
| Weather/Climate | 6 | Forecasts, radar, daily/hourly climate, normals |
| Statistics Canada | 10 | 80K+ tables via WDS + SDMX endpoints |
| IRCC Immigration | 11 | Permanent residents, study/work permits, Express Entry, asylum, citizenship |
| Datastore | 6 | Local SQLite for cross-module SQL queries |

### Provincial Government Data

| Module | Tools | Data Source |
|--------|-------|------------|
| Ontario | 6 | 3,000+ provincial datasets via data.ontario.ca |

### Municipal Government Data

| Module | Tools | Data Source |
|--------|-------|------------|
| Calgary | 5 | Open Calgary catalogue via data.calgary.ca (Socrata SODA API — not CKAN) |
| Edmonton | 5 | Edmonton Open Data Portal via data.edmonton.ca (Socrata SODA API — not CKAN) |

---

## In Progress

### Provincial Government Open Data

Expanding from federal to provincial data. Each province/territory gets a module with CKAN/API discovery tools and curated high-value dataset tools.

| Jurisdiction | Portal | Status |
|-------------|--------|--------|
| Ontario | data.ontario.ca | Shipped |
| British Columbia | catalogue.data.gov.bc.ca | Planned |
| Quebec | donneesquebec.ca | Planned |
| Alberta | open.alberta.ca | Planned |
| Manitoba | geoportal.gov.mb.ca | Planned |
| Saskatchewan | data.open.saskatchewan.ca | Planned |
| Nova Scotia | data.novascotia.ca | Planned |
| New Brunswick | open.canada.ca (NB subset) | Planned |
| Newfoundland and Labrador | opendata.gov.nl.ca | Planned |
| Prince Edward Island | data.princeedwardisland.ca | Planned |
| Northwest Territories | opendata.gov.nt.ca | Planned |
| Yukon | open.yukon.ca | Planned |
| Nunavut | TBD | Planned |

### Municipal Government Open Data

Major Canadian cities with established open data portals.

| City | Portal | Status |
|------|--------|--------|
| Toronto | open.toronto.ca | Planned |
| Montreal | donnees.montreal.ca | Planned |
| Vancouver | opendata.vancouver.ca | Planned — Socrata, not CKAN (confirmed live) |
| Calgary | data.calgary.ca | Shipped — Socrata, not CKAN (confirmed live) |
| Edmonton | data.edmonton.ca | Shipped — Socrata, not CKAN (confirmed live) |
| Ottawa | open.ottawa.ca | Planned |
| Winnipeg | data.winnipeg.ca | Planned |
| Halifax | catalogue.open.halifax.ca | Planned |
| Mississauga | data.mississauga.ca | Planned |

### Regional Government Open Data

Regional municipalities with significant open data programs.

| Region | Portal | Status |
|--------|--------|--------|
| York Region | york.ca/open-data | Planned |
| Peel Region | data.peelregion.ca | Planned |
| Durham Region | opendata.durham.ca | Planned |
| Halton Region | opendata.halton.ca | Planned |
| Waterloo Region | opendata.regionofwaterloo.ca | Planned |
| Metro Vancouver | open.metrovancouver.org | Planned |

---

## Architecture

All government data modules follow the same 5-file pattern:

```
src/mcp_canada/modules/{name}/
  __init__.py      # MODULE_NAME + MODULE_DESCRIPTION
  constants.py     # BASE_URL, rate limits, cache TTLs
  schemas.py       # Pydantic v2 flat models
  client.py        # Async functions → (data, was_cached)
  tools.py         # @tool functions with BM25 keywords
```

Shared infrastructure reused across all modules:
- **BM25 search** — agents discover tools via natural language
- **Bilingual** — all tools accept `lang: en|fr`
- **Caching** — `cached_fetch()` with per-source TTLs
- **Rate limiting** — `get_limiter()` per-source TokenBucket
- **Parsers** — `fetch_and_parse()` for XLSX/CSV/XLS
- **Reshape** — `reshape_observations()` and `reshape_temporal_columns()` for nested output
- **Envelope** — `make_response()`/`make_error()` for consistent `_meta` responses

---

## Contributing

Want to add a data source? Follow the [module pattern](CLAUDE.md) and submit a PR. Each module is self-contained — drop a folder into `src/mcp_canada/modules/` and it registers automatically via FileSystemProvider.
