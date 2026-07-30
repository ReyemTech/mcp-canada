<p align="center">
  <h1 align="center">🍁 mcp-canada</h1>
  <p align="center">
    <strong>MCP server giving AI agents structured access to Canadian federal, provincial, and municipal government data</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/mcp-canada/"><img src="https://img.shields.io/pypi/v/mcp-canada?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/mcp-canada/"><img src="https://img.shields.io/pypi/dm/mcp-canada?color=blue&label=downloads" alt="PyPI downloads"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml"><img src="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/coverage-96%25-brightgreen" alt="Coverage 96%"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/stargazers"><img src="https://img.shields.io/github/stars/ReyemTech/mcp-canada?style=flat&logo=github" alt="GitHub stars"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python 3.12+"></a>
    <a href="https://github.com/ReyemTech/mcp-canada/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP Compatible"></a>
    <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/built%20with-FastMCP-orange" alt="Built with FastMCP"></a>
  </p>
</p>

---

**295 tools, ~107 prompts, and ~141 resources** across **9 federal APIs + 9 provincial APIs + 2 municipal APIs + 1 local SQLite datastore** — exchange rates, parliamentary data, product recalls, drug information, 80K+ open datasets, food nutrition data, real-time weather, immigration statistics, Ontario provincial data, Toronto municipal data, York Region ArcGIS Hub data, British Columbia CKAN + WFS geospatial data, Quebec Données Québec CKAN + ArcGIS IQA data, Alberta open data + AER energy + WMBappServices wildfire + AHSGIS health + 511 Alberta transport, Manitoba geoportal (ArcGIS Hub) + 511 Manitoba transport, Saskatchewan geoportal (ArcGIS Hub) + WSA water infrastructure + SPSA fire bans, Nova Scotia Socrata SODA portal (data.novascotia.ca), New Brunswick federal-CKAN discovery + GeoNB bare ArcGIS Server geospatial data + gnb.socrata.com Socrata portal + key-gated 511 NB transport, and persistent local storage. All bilingual (English/French).

> **First ArcGIS Hub module** — shared infrastructure in `shared/arcgis_hub.py` is reusable for future Canadian municipal modules (BC, Calgary, Edmonton, and other cities publishing via ArcGIS Hub).
> **First OGC WFS module** — BC introduces WFS 2.0 (OGC) support via `shared/ogc.py`, making WFS the third portal technology alongside CKAN and ArcGIS Hub. See `docs://bc/wfs-query-guide` for the CKAN→WFS two-step workflow.


## Quick Start

```bash
# Auto-configure your platform (interactive)
uvx mcp-canada install

# Or name platforms directly
uvx mcp-canada install claude-desktop cursor vscode
```

Supports 14 platforms: Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, Zed, Codex CLI, Gemini CLI, Amazon Q, OpenCode, Cline, Roo Code, Goose CLI, Junie CLI.

### Manual Setup

<details>
<summary>Claude Desktop</summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-canada": {
      "command": "uvx",
      "args": ["mcp-canada"]
    }
  }
}
```
</details>

<details>
<summary>Claude Code</summary>

```bash
claude mcp add mcp-canada -- uvx mcp-canada
```
</details>

<details>
<summary>From Source</summary>

```bash
git clone https://github.com/reyemtech/mcp-canada.git
cd mcp-canada
uv run mcp-canada
```
</details>

### Options

| Flag | Description | Example |
|------|-------------|---------|
| `--transport` | Transport protocol | `--transport sse` |
| `--port` | Port for SSE/HTTP | `--port 8000` |
| `--modules` | Load only specific modules | `--modules bank_of_canada,recalls` |
| `--verbose` | INFO-level logging | `--verbose` |
| `--debug` | DEBUG-level logging | `--debug` |

Environment variable: `MCP_CANADA_MODULES=bank_of_canada,recalls`

## Examples

See **[EXAMPLES.md](EXAMPLES.md)** for 25 cross-API intelligence scenarios — from tracing prairie drought to the Canadian dollar, to building pharmaceutical safety audits, to assembling MP accountability briefs, to joining data from multiple APIs in a single SQL query. Each example includes the exact prompt and tool chain you can run today.

## How Discovery Works

With 250 tools, listing all of them would consume half an agent's context window. Instead, **BM25 search** lets agents find exactly what they need:

```
Agent: "What tools do you have for exchange rates?"

→ discover_tools("exchange rate CAD")
→ Returns: boc_get_exchange_rates, boc_get_observations

→ call_tool("boc_get_exchange_rates", {"currency": "USD", "recent": 3})
→ Returns: {"_meta": {...}, "data": [{"date": "2026-04-02", "value": 1.3918, ...}]}
```

Agents see **5 always-visible tools**:

| Tool | Purpose |
|------|---------|
| `discover_tools` | BM25 natural language search across all tools |
| `call_tool` | Execute any discovered tool by name |
| `list_modules` | List available API modules with tool counts |
| `plan_query` | Plan a multi-step query across Canadian government data APIs |
| `execute_batch` | Run multiple tool calls in parallel with per-step error isolation |

---

## Modules

All tools accept `lang: "en" | "fr"` for bilingual support. Responses include a `_meta` envelope with source attribution and cache status. Click a module for its full tool, prompt, and resource catalog.

| Module | Level | Tools | Prompts | Resources | Description |
|--------|-------|------:|--------:|----------:|-------------|
| [Meta / Discovery](docs/modules/meta.md) | — | 5 | — | — | Always-visible orchestration tools (`discover_tools`, `call_tool`, `list_modules`, `plan_query`, `execute_batch`) |
| [Bank of Canada](docs/modules/bank-of-canada.md) | Federal | 8 | 5 | 7 | Exchange rates, interest rates, commodity prices, inflation — [Valet API](https://www.bankofcanada.ca/valet/) |
| [CKAN Open Data](docs/modules/ckan.md) | Federal | 7 | 5 | 7 | 80,000+ federal datasets — [open.canada.ca](https://open.canada.ca/data/en/api/3/) |
| [Drug Database](docs/modules/drug-database.md) | Federal | 8 | 5 | 7 | Drug products, ingredients, schedules — [Health Canada DPD](https://health-products.canada.ca/api/drug/) |
| [IRCC Immigration](docs/modules/ircc.md) | Federal | 10 | 5 | 7 | PR, study/work permits, Express Entry, asylum — [IRCC Open Data](https://www.ircc.canada.ca/opendata-donneesouvertes/data/) |
| [Nutrient File](docs/modules/nutrient-file.md) | Federal | 8 | 5 | 7 | Food nutrition data — [Canadian Nutrient File](https://food-nutrition.canada.ca/api/canadian-nutrient-file/) |
| [Open Parliament](docs/modules/open-parliament.md) | Federal | 10 | 5 | 7 | Bills, MPs, votes, ballots, Hansard debates — [Open Parliament API](https://api.openparliament.ca/) |
| [Recalls & Safety](docs/modules/recalls.md) | Federal | 6 | 4 | 6 | Food, vehicle, and health product recalls — [Healthy Canadians](https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/) |
| [Statistics Canada](docs/modules/statcan.md) | Federal | 15 | 6 | 8 | Time series, cube metadata, SDMX filtering — [StatCan WDS](https://www.statcan.gc.ca/en/developers/wds) |
| [Weather](docs/modules/weather.md) | Federal | 34 | 6 | 8 | Conditions, climate, air quality, hydrology, marine, radar — [MSC GeoMet](https://api.weather.gc.ca/) |
| [Alberta](docs/modules/alberta.md) | Provincial | 24 | 6 | 7 | CKAN + AER energy + WMBappServices wildfire + AHSGIS health + 511 Alberta — [open.alberta.ca](https://open.alberta.ca) |
| [British Columbia](docs/modules/british-columbia.md) | Provincial | 20 | 6 | 7 | CKAN + WFS geospatial — [BC Data Catalogue](https://catalogue.data.gov.bc.ca) |
| [Manitoba](docs/modules/manitoba.md) | Provincial | 20 | 6 | 7 | ArcGIS Hub + 511 Manitoba — [geoportal.gov.mb.ca](https://geoportal.gov.mb.ca) |
| [Saskatchewan](docs/modules/saskatchewan.md) | Provincial | 13 | 6 | 7 | ArcGIS Hub + WSA water + SPSA fire bans — [geohub.saskatchewan.ca](https://geohub.saskatchewan.ca) |
| New Brunswick (`new_brunswick/`) | Provincial | 22 | 6 | 7 | Federal CKAN + GeoNB bare ArcGIS Server + gnb.socrata.com Socrata + key-gated 511 NB transport — [geonb.snb.ca](https://geonb.snb.ca) |
| [Nova Scotia](docs/modules/nova-scotia.md) | Provincial | 16 | 6 | 7 | Socrata SODA portal (aquaculture, environment, health) — [data.novascotia.ca](https://data.novascotia.ca) |
| [Ontario](docs/modules/ontario.md) | Provincial | 6 | 4 | 6 | 3,000+ provincial datasets — [Ontario Open Data](https://data.ontario.ca) |
| [Quebec](docs/modules/quebec.md) | Provincial | 18 | 6 | 7 | Federated CKAN (139 orgs) — [Données Québec](https://www.donneesquebec.ca) |
| [Toronto](docs/modules/toronto.md) | Municipal | 12 | 6 | 8 | TTC, neighbourhoods, 311, RentSafe — [Toronto Open Data](https://open.toronto.ca) |
| [York Region](docs/modules/york-region.md) | Municipal | 27 | 5 | 8 | 4 ArcGIS Hub portals (York Region, Markham, Newmarket, Aurora) |
| [Local Datastore](docs/modules/datastore.md) | Local | 6 | 4 | 6 | SQLite persistence for cross-API SQL JOINs — `~/.mcp-canada/datastore.db` |
| **Total** | | **295** | **~107** | **~141** | |

---

## Response Format

All tools return a consistent envelope:

```json
{
  "_meta": {
    "source": {"api": "bank-of-canada-valet", "url": "https://..."},
    "cached": true,
    "lang": "en",
    "timestamp": "2026-04-04T12:00:00Z"
  },
  "data": [ ... ]
}
```

Errors return:

```json
{
  "error": {
    "code": "INVALID_SERIES",
    "message": "Series 'FXXYZCAD' not found.",
    "suggestions": ["FXUSDCAD", "FXEURCAD"]
  }
}
```

## Architecture

```
src/mcp_canada/
├── server.py              # FastMCP entry point, transport, module loading
├── shared/                # Cross-module utilities
│   ├── cache.py           # TTL-based in-memory cache (aiocache)
│   ├── envelope.py        # Response/error envelope (make_response/make_error)
│   ├── http.py            # Shared HTTP client with retry (tenacity)
│   ├── rate_limiter.py    # Per-source token bucket
│   └── i18n.py            # Bilingual error messages
├── meta/
│   └── list_modules.py    # list_modules meta-tool
└── modules/
    ├── bank_of_canada/    # 8 tools — Valet API
    ├── open_parliament/   # 10 tools — Parliament API
    ├── recalls/           # 6 tools — Healthy Canadians API
    ├── drug_database/     # 8 tools — Health Canada DPD
    ├── ckan/              # 7 tools — Open Data Portal
    ├── nutrient_file/     # 8 tools — Canadian Nutrient File
    ├── datastore/         # 6 tools — local SQLite persistence
    ├── ircc/              # 10 tools — IRCC Immigration Open Data
    ├── ontario/           # 6 tools — Ontario Open Data Catalogue
    ├── toronto/           # 12 tools — City of Toronto Open Data Portal
    ├── york_region/       # 27 tools — York Region ArcGIS Hub (4 portals)
    ├── british_columbia/  # 20 tools — BC Data Catalogue + WFS
    ├── manitoba/          # 20 tools — geoportal.gov.mb.ca ArcGIS Hub + 511 Manitoba
    ├── saskatchewan/      # 13 tools — geohub.saskatchewan.ca ArcGIS Hub + WSA water + SPSA fire bans
    ├── quebec/            # 18 tools — Données Québec CKAN
    ├── alberta/           # 24 tools — open.alberta.ca CKAN + AER + WMB + AHSGIS + 511
    ├── nova_scotia/       # 16 tools — data.novascotia.ca Socrata SODA
    ├── statcan/           # 15 tools — Statistics Canada WDS + SDMX
    └── weather/           # 34 tools — MSC GeoMet OGC API
        ├── current/       # 5 tools — realtime conditions, forecast, alerts
        ├── climate/       # 7 tools — daily/monthly/normals/trends
        ├── aqhi/          # 3 tools — air quality health index
        ├── hydro/         # 5 tools — water levels, flow, flood risk
        ├── marine/        # 3 tools — marine forecasts, hurricane tracks
        ├── severe/        # 3 tools — radar, lightning, UV index
        ├── snow/          # 2 tools — snow depth, snow water equivalent
        ├── collections/   # 2 tools — collection browser and direct query
        └── summary/       # 4 tools — composite summary, extremes, growing season, degree days
```

Each module follows a **7-file pattern**:

| File | Purpose |
|------|---------|
| `__init__.py` | Module name and description |
| `constants.py` | Base URL, rate limits, cache TTLs, API mappings |
| `schemas.py` | Pydantic v2 response models (always flat) |
| `client.py` | Async HTTP functions with caching and rate limiting |
| `tools.py` | `@tool` decorated MCP tool functions |
| `prompts.py` | `@prompt` functions — guided workflows + quick lookups |
| `resources.py` | `@resource` functions — catalogs, docs, templates |

New modules are auto-discovered — drop a folder in `modules/` and it registers via FileSystemProvider.

## Development

```bash
# Install dependencies
uv sync

# Run tests (~2000 unit tests, ~15s)
uv run pytest

# Run integration tests against live APIs (~2min)
uv run pytest tests/integration/ -v -m integration --timeout=120

# Type check and lint
uv run pyright
uv run ruff check src/ tests/

# Coverage (must be ≥95%)
uv run pytest --cov=src/mcp_canada --cov-fail-under=95
```

## Contributing

Each module is self-contained. To add a new API:

1. Create `src/mcp_canada/modules/your_api/` with the 7-file pattern
2. Add colocated `__tests__/` with unit tests
3. Add integration tests in `tests/integration/test_tool_scenarios.py`
4. Add a module doc in `docs/modules/` and update the Modules table in this README

See [CLAUDE.md](CLAUDE.md) for coding conventions.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version-by-version changes, or browse [GitHub Releases](https://github.com/ReyemTech/mcp-canada/releases).

## Security

Found a vulnerability? Please **do not** open a public issue. Email [contact@reyem.tech](mailto:contact@reyem.tech) with details and reproduction steps. We support the latest minor version on PyPI.

## Community

- **Questions & ideas:** [GitHub Discussions](https://github.com/ReyemTech/mcp-canada/discussions)
- **Bugs & feature requests:** [GitHub Issues](https://github.com/ReyemTech/mcp-canada/issues)
- **Contact:** [contact@reyem.tech](mailto:contact@reyem.tech)

## License

[MIT](LICENSE) — [Reyem Tech](https://reyem.tech)

### Data Attributions

Data from the following government sources is accessed by this library subject to their respective licences:

- **Nova Scotia Open Data** — Licensed under the [Open Government Licence – Nova Scotia v1.1](https://novascotia.ca/opendata/licence.asp). Contains public sector information provided by the Province of Nova Scotia.

## Star History

<a href="https://star-history.com/#ReyemTech/mcp-canada&Date">
  <img src="https://api.star-history.com/svg?repos=ReyemTech/mcp-canada&type=Date" alt="Star History Chart">
</a>
