# PR automation

The repository separates untrusted test execution from trusted feedback publishing.
The public comment names are **PR Checks** and **PR Review**, posted by
`github-actions[bot]`. Comments contain findings and evidence without promotional
footers, model names, or connector attribution. Workflow source and action logs
still identify the dependencies used; this is not a mechanism for hiding provenance.

The review comment opens with one of three recommendations:

- **Merge recommended:** no blocking findings, sufficient review evidence, and all
  three required CI jobs passed for the exact reviewed revision.
- **Changes requested:** blocking code findings or CI failures need a new revision.
- **Manual review required:** the assessment or current CI could not be verified,
  CI is still running, or significant correctness questions remain unresolved.

Each completed review explains what is solid with specific evidence, separates
blocking issues from expandable non-blocking suggestions, and includes a checklist
with evidence and explicit verification limits. Optional suggestions do not prevent
a merge recommendation. Blocking comments tag the PR author; merge recommendations
tag the configured maintainer and request their review. Existing requests and
completed reviews for the same revision are not requested again. GitHub forbids
self-review requests, and requests for drafts are deferred until ready for review.
If the request API fails, the comment explains that a manual request is needed.
Unverified checklist items stay unchecked; source inspection is distinguished from
executing tests.

Each recommendation names its reviewed base branch and SHA, and is valid only for
that head/base pair. A changed base invalidates in-progress assessments and stale
CI results. Retargeting triggers fresh CI through the PR edited event; title/body
edits also rerun CI. After the base branch advances, update/rebase the PR branch
to obtain fresh checks and a fresh review before merging. A green comment for an
older base does not authorize merging against a newer base.

The publisher independently reads the newest CI run for the same PR and head/base
commit pair rather than relying on the review's test
claims. The CI run name records the triggering PR number and base ref/SHA at run
creation; mutable PR associations are not proof of which base was tested. This
also identifies fork runs with empty PR associations. Legacy runs without this
snapshot require fresh checks before a merge recommendation can be given.

## Maintainer setup

1. Merge the contributor docs and workflows into the default branch. `workflow_run`
   feedback is loaded from that branch, not from contributor code.
2. In Settings → Actions → General, set fork workflow approval to **first-time
   contributors who are new to GitHub**. Established accounts can run CI without a
   per-PR approval. New accounts may still require approval. CI uses read-only
   permissions and never receives repository secrets.
3. Use the dedicated **mcp-canada** Mantle project in **us-east-1**. Authentication
   uses GitHub OIDC and temporary AWS credentials; no OpenAI or Bedrock API key is
   stored in GitHub. The CloudFormation template at `.github/aws/pr-review.yml`
   creates a role restricted to this repository's `main` branch, the project, and
   the selected model. See the deployment command below.
4. Set these repository Actions **variables**, not secrets:

   | Variable | Value |
   | --- | --- |
   | `PR_REVIEW_ROLE_ARN` | Role ARN from the CloudFormation stack output |
   | `PR_REVIEW_AWS_REGION` | `us-east-1` |
   | `PR_REVIEW_PROJECT_ID` | Dedicated Mantle project ID |
   | `PR_REVIEW_MODEL` | `openai.gpt-6-sol` |
   | `PR_REVIEW_MAINTAINER` | `mariomeyer` |

   Changing the model or region also requires updating the role's policy. Reasoning
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

## AWS deployment

Create the Mantle project through the
[Projects API](https://docs.aws.amazon.com/bedrock/latest/userguide/projects.html)
and tag it with `Application=mcp-canada` and `Purpose=pull-request-review`.
The stack does not create or delete the project, so replacing the role cannot
delete inference history. Deploy the scoped role with:

```bash
aws cloudformation deploy --region us-east-1 \
  --stack-name mcp-canada-pr-review \
  --template-file .github/aws/pr-review.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides MantleProjectId=YOUR_PROJECT_ID VerificationBranch=
```

For a new stack in an account with an existing GitHub OIDC provider, also pass its
ARN as `ExistingOidcProviderArn`. Leave that parameter unchanged on stack updates.
The optional `VerificationBranch` allows a specific maintainer-owned branch during
setup; reset it to empty immediately after verification. Normal role trust permits
only `repo:ReyemTech/mcp-canada:ref:refs/heads/main`, never fork PR refs.

The role permits `bedrock-mantle:CreateInference` only on the dedicated project,
conditioned on the configured model and region, plus `GetProject` on that project.
Requests include an explicit `OpenAI-Project` header. Inference in the default
project, another project, or another model is not authorized by this role.
Sessions last 15 minutes. Tag-based cost reporting may require activation in AWS
Billing and can take time to appear; project separation is not a spending cap.

## Execution and permissions

| Stage | Inputs | Permissions |
| --- | --- | --- |
| `CI` | PR checkout; lint/type/unit/catalog checks | `contents: read`, no secrets |
| `PR Feedback / Publish CI feedback` | Current GitHub run/job metadata | Read actions/content; write PR comments |
| `PR Feedback / Assess PR changes` | Trusted default-branch prompt plus PR diff and git objects | Read content/PR; OIDC; inference in one Mantle project |
| `PR Feedback / Publish review` | Validated JSON report plus current CI status | Read content/actions; write PR comments; no provider secret |

CI runs once per pull-request event, not on branch pushes separately. A push to an
open PR triggers its `synchronize` event and runs the three Python versions once.
Manual CI dispatch remains available for branches without an open PR.

Feedback is triggered by a completed **CI** run for a pull request. The workflow
re-fetches the run and PR metadata, validates the repository and head revision,
and skips closed, draft, or outdated revisions. Fork PR associations are resolved
via GitHub's commit-to-PR API when the event does not include them.

The reviewer fetches PR git objects but never checks out or executes proposed code,
installs its dependencies, or loads its configuration. Its prompt and JSON schema
are trusted default-branch files. A pinned CLI runs under the separate `pr-reviewer`
OS account with a read-only sandbox and no sudo rights. PR text, including proposed
agent instructions, is untrusted data. The provider process receives temporary,
project-scoped AWS credentials; its shell tools inherit no AWS or GitHub tokens.
The provider environment excludes bearer keys, OpenAI keys, AWS profiles, and runner
tokens. No untrusted workflow artifacts are downloaded into a privileged publisher.

The publisher validates report structure, priorities, changed file paths, and positive
line numbers, escapes displayed text and model-supplied mentions. Only trusted publisher logic
adds the PR author or configured maintainer mention. It rechecks the head
SHA before publishing. It updates only its own marked bot comments, never comments
with a matching marker written by a contributor. A timeout, bad output, missing
configuration, failed AWS authentication, or oversized diff produces **Manual review required**, not a clean review.

## Reproduction and maintenance

```bash
node --test .github/scripts/*.test.cjs
uv run python scripts/generate_catalog.py --check
```

The feedback tests cover stale revisions, missing/failed checks, CI recovery,
actionable medium-priority findings, invalid reports, mention/HTML handling,
and updating bot comments without overwriting contributor text.

Use Actions → PR Feedback → Run workflow with a PR number to rerun only the review
without executing PR tests. A manual dispatch can review a draft; automatic runs
skip drafts. Automatic reviews follow CI completion; the next push
restarts the checks and review. Automatic feedback runs are isolated by CI run ID, so PRs sharing a source branch
cannot cancel each other. Manual reruns for the same PR cancel older manual reruns.
Stale revision checks prevent outdated automatic assessments from publishing. Automatic and manual publishers serialize per PR,
and an older feedback run cannot overwrite a comment from a newer run. The size
limit requires manual review of large PRs.

GitHub approval can expire after 30 days without running any test jobs. See
[approving fork runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks).
Approve/restart the workflow or ask the contributor to push a new revision; an
expired approval is not evidence that the code failed tests.

Actions used in privileged feedback jobs are pinned to commit SHAs. Update them
deliberately, inspect changed inputs, run helper tests, and validate workflow YAML.
Do not switch these jobs to a fork checkout or execute contributor-provided scripts.
