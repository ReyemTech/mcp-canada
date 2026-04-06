# Tool Description Quality Checklist

Every tool description in mcp-canada MUST follow these guidelines for BM25 discovery accuracy.

## Required Structure

1. **First sentence:** What the tool does in plain language (verb-first)
   - Good: "Get daily CAD exchange rates against major currencies from the Bank of Canada."
   - Bad: "This tool retrieves exchange rate data."

2. **Use-case line:** "Use for: {comma-separated use cases}"
   - Good: "Use for: currency conversion, forex data, USD/CAD rates, exchange rate history."

3. **Keywords line:** "Keywords: {comma-separated keywords covering synonyms and related terms}"
   - Good: "Keywords: exchange rate, currency, forex, CAD, USD, EUR, Bank of Canada, Valet API."

## Rules

- Minimum 50 characters total
- Include the API source name (e.g., "Bank of Canada", "Environment Canada")
- Include common synonyms agents might search for
- Include data type terms (e.g., "time series", "geospatial", "forecast")
- Do NOT use generic filler ("This tool allows you to...")
- Do NOT repeat the tool name in the description

## Enforcement

The `tests/test_quality.py` suite enforces these rules automatically.
Running `uv run pytest tests/test_quality.py` validates all registered tools.

Any new tool added in Phases 2-4 must pass the quality suite before merge.
