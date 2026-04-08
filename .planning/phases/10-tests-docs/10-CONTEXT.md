# Phase 10: Tests + Docs - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Integration test sweep for all new tools through MCP Client layer, README update with StatCan + datastore sections, and EXAMPLES.md update with cross-module SQL query examples. No new tools, no new features.

</domain>

<decisions>
## Implementation Decisions

### README structure
- Update tool count: "100+ tools across 8 federal APIs + shared datastore"
- Add StatCan section to tool catalog (11 WDS + 3 SDMX + 1 composite = 15 sc_ tools)
- Add Datastore section to tool catalog (6 ds_ tools)
- Replace "complementary to mcp-statcan" note with "Inspired by mcp-statcan by Aryan Jhaveri" credit in StatCan section
- Keep existing module sections unchanged

### Cross-module SQL examples
- Add 4 new cross-module examples to EXAMPLES.md showing full workflow (fetch → store → SQL JOIN):
  1. **CPI + BoC rates**: StatCan CPI data + BoC interest rates, JOIN on date. "Did rate hikes slow inflation?"
  2. **GDP + exchange rate**: StatCan GDP by province + BoC CAD/USD. "GDP growth vs currency correlation"
  3. **Labour + weather**: StatCan employment + weather growing season. "Seasonal employment in agricultural regions"
  4. **Population + Parliament**: StatCan population by riding + parliamentary voting. "How do MPs from growing ridings vote?"
- Each example shows the complete chain: fetch data, store to datastore, SQL query
- Follow existing EXAMPLES.md format (prompt → tool chain → insight)

### Claude's Discretion
- Exact integration test scenarios (which tools, which parameters)
- README section ordering
- Whether to add a "Datastore" section to EXAMPLES.md or integrate into existing categories
- How much of the StatCan tool catalog to show in README (all 15 or grouped)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/integration/test_tool_scenarios.py`: Existing integration test pattern with `TestStatcanWdsScenarios` (10 tests) and `TestSdmxScenarios` (6 tests) and `TestDatastoreScenarios` (6 tests)
- `EXAMPLES.md`: 19 existing examples across 5 categories with consistent format
- `README.md`: Tool catalog sections with consistent table format

### Established Patterns
- Integration tests call tools through `Client(mcp)` → `call_tool('call_tool', {...})`
- README tool tables: `| Tool | Description | Key Parameters |`
- EXAMPLES.md format: heading, prompt, tool chain steps, insight paragraph

### Integration Points
- `README.md` — update tool count, add StatCan + Datastore catalog sections, update mcp-statcan reference
- `EXAMPLES.md` — add new "Cross-Module SQL" section with 4 examples
- `tests/integration/test_tool_scenarios.py` — may need additional scenarios for coverage gaps

</code_context>

<specifics>
## Specific Ideas

No specific requirements — follow existing documentation patterns.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 10-tests-docs*
*Context gathered: 2026-04-08*
