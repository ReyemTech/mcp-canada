"""MCP resources for the _example module — demonstrates the 7-file resource pattern.

HOW TO USE THIS FILE:
1. Copy this file to your new module: src/mcp_canada/modules/{name}/resources.py
2. Replace "example" in URIs and function names with your module prefix
3. Implement real catalogs/docs/templates for your module's domain
4. FileSystemProvider auto-discovers @resource decorated functions — no server.py changes needed

URI SCHEME CONVENTIONS:
- data://{module}/{resource-name}     — JSON reference catalogs (machine-parseable)
- docs://{module}/{topic}             — Markdown documentation guides (human-readable)
- template://{module}/{report-type}   — Markdown templates with {placeholder} syntax

CRITICAL RULE — ZERO PARAMETERS:
Resource functions MUST have zero parameters. If you add any parameter (even lang),
FastMCP will classify the function as a ResourceTemplate instead of a FunctionResource.
ResourceTemplates appear in resources/templates/list, NOT resources/list.
For bilingual content, embed both languages inline within the single resource.

MIME TYPES:
- "application/json"  — for data:// catalog resources
- "text/markdown"     — for docs:// and template:// resources

REAL-WORLD REFERENCE: src/mcp_canada/modules/bank_of_canada/resources.py
"""

import json

from fastmcp.resources import resource


# ---------------------------------------------------------------------------
# Pattern 1: Catalog resource (data://) — returns JSON string
# ---------------------------------------------------------------------------

@resource(
    "data://example/sample-codes",   # URI: data://{module}/{resource-name}
    mime_type="application/json",
    name="example_sample_codes",     # snake_case name for programmatic access
    title="Example Sample Codes",    # Human-readable title shown in resource list
)
def example_sample_codes() -> str:
    """Valid codes for the example module's API.

    Bilingual catalog embedding both languages in one JSON structure.
    Format: {"CODE": {"en": "English label", "fr": "Étiquette française"}}
    """
    # Always use json.dumps() — never return a raw dict.
    # Use ensure_ascii=False to preserve French accents.
    return json.dumps(
        {
            "CODE_A": {"en": "Code A description", "fr": "Description du code A"},
            "CODE_B": {"en": "Code B description", "fr": "Description du code B"},
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Pattern 2: Documentation resource (docs://) — returns Markdown string
# ---------------------------------------------------------------------------

@resource(
    "docs://example/getting-started",
    mime_type="text/markdown",
    name="example_getting_started",
    title="Example Module Getting Started Guide",
)
def example_getting_started() -> str:
    """Getting started guide for the example module.

    Explains key concepts, naming conventions, and common usage patterns.
    """
    # Start with a # heading — tests verify docs resources start with #.
    # Embed both English and French content under separate ## sections,
    # or write in one language if the API is English-only.
    return """# Example Module: Getting Started

## Overview

This module provides access to the example API.

## Available Tools

- `example_echo` — Echo a message back in the requested language

## Common Usage

1. Call `example_echo` with your message and lang parameter
2. The response includes a `_meta` envelope with source and cache info

## Series Naming

Example codes follow the pattern `CODE_{LETTER}` (e.g., `CODE_A`, `CODE_B`).
"""


# ---------------------------------------------------------------------------
# Pattern 3: Template resource (template://) — returns Markdown with placeholders
# ---------------------------------------------------------------------------

@resource(
    "template://example/report",
    mime_type="text/markdown",
    name="example_report_template",
    title="Example Report Template",
)
def example_report_template() -> str:
    """Template for formatting an example data report.

    Replace {placeholder} values with actual data before presenting to the user.
    """
    # Use {placeholder} syntax throughout.
    # Tests verify that template resources contain { and } characters.
    return """# {title} Report

**Date:** {report_date}
**Source:** Example API

## Summary

{summary_text}

## Data

| Code | Value |
|------|-------|
{data_rows}

## Notes

{notes}
"""
