# Repository guidance

Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution checks and
[CLAUDE.md](CLAUDE.md) for module conventions and upstream portal facts.

Commits, PR titles/descriptions, and review comments must not contain model/tool
attribution, generated-by footers, session links, or AI co-author trailers.

## Code Review Rules

- Verify pagination and complete aggregation against actual catalog sizes. A large
  page size is not proof of completeness. Require multi-page coverage or explicit
  disclosure of partial results; otherwise categories and counts can be misleading.
- Trace public parameters through shared helpers to the response. Flag options that
  are ignored, change only cache keys, or fail their documented contract. Check both
  sides of boolean options and limit/offset boundaries.
- Preserve error blame: caller mistakes use `InvalidInput`; upstream decoding,
  schema, network, and response-shape failures stay upstream errors. Report concrete
  misclassification or silently accepted failures with the triggering condition.

Focus on actionable correctness issues introduced by a PR, including P2 defects.
Leave mechanical lint, typing, test execution, and catalog freshness checks to CI.
State what was not verified; the maintainer retains the merge decision.
