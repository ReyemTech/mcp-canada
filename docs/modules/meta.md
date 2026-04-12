# :mag: Meta / Discovery

Orchestration tools always available to agents -- no discovery required.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (5)

<!-- CATALOG:meta:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `execute_batch` | Execute multiple tool calls in parallel and return aggregated results. | `calls` |
| `list_modules` | List all registered API modules with tool counts and descriptions. | -- |
| `plan_query` | Plan a multi-step query across Canadian government data APIs. | `query`, `top_k` |
<!-- CATALOG:meta:end -->

> `discover_tools` and `call_tool` are injected by the BM25SearchTransform and don't appear in `tools/list` directly.

## Prompts (0)

_No prompts for this module._

## Resources (0)

_No resources for this module._
