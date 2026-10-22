# PR automation

The repository separates untrusted test execution from trusted feedback publishing.
The public comment names are **PR Checks** and **PR Review**, posted by
`github-actions[bot]`. Comments contain findings and evidence without promotional
footers, model names, or connector attribution. Workflow source and action logs
still identify the dependencies used; this is not a mechanism for hiding provenance.

## Maintainer setup

1. Merge the contributor docs and workflows into the default branch. `workflow_run`
   feedback is loaded from that branch, not from contributor code.
2. In Settings → Actions → General, set fork workflow approval to **first-time
   contributors who are new to GitHub**. Established accounts can run CI without a
   per-PR approval. New accounts may still require approval. CI uses read-only
   permissions and never receives repository secrets.
3. Add an API key as the repository Actions secret `OPENAI_API_KEY`. Use a dedicated
   project with an appropriate spend limit. Never put the key in an issue or PR.
   The provider action and setup are documented at
   [the official action guide](https://learn.chatgpt.com/docs/github-action).
4. Optionally set the Actions variable `PR_REVIEW_MODEL` to a supported model
   available to that project. An empty value uses the action's default. Reasoning
   effort is `medium`; each review job has a 15-minute timeout and a 400 KB diff cap.
5. Disable built-in automatic reviews for this repository in
[review settings](https://chatgpt.com/settings/code-review), and do not use
   its comment triggers. That integration adds its own app name and badge, which
   cannot be removed by changing a comment's text. If posting manually, use the
   maintainer's personal GitHub CLI authentication rather than the connector.
6. Push an update to an open test PR. Verify both comments appear, make a revision
   that fixes a finding, and verify the comments update instead of multiplying.

Optional hard enforcement: use a GitHub ruleset to require the three CI matrix jobs
and maintainer approval. Automated findings remain advisory; the workflow never
merges, changes contributor branches, or submits approval/request-changes reviews.

## Execution and permissions

| Stage | Inputs | Permissions |
| --- | --- | --- |
| `CI` | PR checkout; lint/type/unit/catalog checks | `contents: read`, no secrets |
| `PR Feedback / Publish CI feedback` | Current GitHub run/job metadata | Read actions/content; write PR comments |
| `PR Feedback / Assess PR changes` | Trusted default-branch prompt plus PR diff and git objects | Read content/PR; provider API through a protected proxy |
| `PR Feedback / Publish review` | Validated JSON report or failure status | Read content; write PR comments; no provider secret |

CI runs once per pull-request event, not on branch pushes separately. A push to an
open PR triggers its `synchronize` event and runs the three Python versions once.
Manual CI dispatch remains available for branches without an open PR.

Feedback is triggered by a completed **CI** run for a pull request. The workflow
re-fetches the run and PR metadata, validates the repository and head revision,
and skips closed, draft, or outdated revisions. Fork PR associations are resolved
via GitHub's commit-to-PR API when the event does not include them.

The reviewer fetches PR git objects but never checks out or executes proposed code,
installs its dependencies, or loads its configuration. Its prompt and JSON schema
are trusted default-branch files. It runs with read-only permissions and dropped
sudo privileges. PR text, including proposed agent instructions, is untrusted data.
The API key is not provided to the agent environment as an executable shell secret.
No untrusted workflow artifacts are downloaded into a privileged publisher.

The publisher validates report structure, priorities, changed file paths, and positive
line numbers, escapes displayed text, and prevents user mentions. It rechecks the head
SHA before publishing. It updates only its own marked bot comments, never comments
with a matching marker written by a contributor. A timeout, bad output, missing
key, or oversized diff produces **Manual review required**, not a clean review.

## Reproduction and maintenance

```bash
node --test .github/scripts/*.test.cjs
uv run python scripts/generate_catalog.py --check
```

The feedback tests cover stale revisions, missing/failed checks, CI recovery,
actionable medium-priority findings, invalid reports, mention/HTML handling,
and updating bot comments without overwriting contributor text.

Use Actions → PR Feedback → Run workflow with a PR number to rerun only the review
without executing PR tests. Automatic reviews follow CI completion; the next push
restarts the checks and review. Review jobs for a newer run cancel older feedback
jobs on the same source branch. Any legacy push-triggered CI completions use a
separate group and cannot cancel PR feedback. Automatic and manual publishers serialize per PR,
and an older feedback run cannot overwrite a comment from a newer run. The size
limit requires manual review of large PRs.

GitHub approval can expire after 30 days without running any test jobs. See
[approving fork runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks).
Approve/restart the workflow or ask the contributor to push a new revision; an
expired approval is not evidence that the code failed tests.

Actions used in privileged feedback jobs are pinned to commit SHAs. Update them
deliberately, inspect changed inputs, run helper tests, and validate workflow YAML.
Do not switch these jobs to a fork checkout or execute contributor-provided scripts.
