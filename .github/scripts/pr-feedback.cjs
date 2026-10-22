'use strict';

const COMMANDS = {
  'Install dependencies': 'uv sync --locked --dev',
  'Test PR feedback helpers': 'node --test .github/scripts/*.test.cjs',
  'Lint (ruff)': 'uv run ruff check src/ tests/',
  'Type check (pyright)': 'uv run pyright',
  'Run unit tests with coverage': 'uv run pytest --cov=src/mcp_canada',
  'Check catalog freshness': 'uv run python scripts/generate_catalog.py && uv run python scripts/generate_catalog.py --check',
};

function text(value) {
  return String(value).replace(/@/g, '@\u200b').replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' })[c])
    .replace(/[\\`*_{}\[\]()#!|]/g, '\\$&');
}

function isCurrent(pr, sha, repository, allowDraft = false) {
  return pr.state === 'open' && (allowDraft || !pr.draft) && /^[a-f0-9]{40}$/.test(sha)
    && pr.head.sha === sha && pr.base.repo.full_name === repository;
}

function renderChecks(run, jobs) {
  const passed = run.conclusion === 'success' && jobs.some(job => job.conclusion === 'success')
    && jobs.every(job => job.conclusion === 'success' || job.conclusion === 'skipped');
  const lines = ['## PR Checks', '', `**${passed ? 'All checks passed' : 'Changes needed or checks incomplete'}**`,
    '', `Revision: \`${run.head_sha.slice(0, 7)}\` · [CI run](${run.html_url})`, ''];
  if (!jobs.length) {
    lines.push('No test jobs ran. A maintainer should check workflow approval and runner availability, then restart CI. This is not a passing result.');
  }
  for (const job of jobs) {
    lines.push(`- [${text(job.name)}](${job.html_url}): **${text(job.conclusion || 'incomplete')}**`);
    for (const step of job.steps || []) {
      if (step.conclusion !== 'failure') continue;
      lines.push(`  - ${text(step.name)} failed.`);
      if (COMMANDS[step.name]) lines.push(`    Reproduce/fix: \`${COMMANDS[step.name]}\``);
    }
  }
  if (!passed && jobs.length) lines.push('', 'Please fix the failed checks and push an update. A new run will update this comment.');
  lines.push('', 'Merge decisions remain with the maintainer.');
  return lines.join('\n');
}

function renderReview(report, repository, sha, files) {
  const verdicts = { ready: 'Ready for maintainer review', changes_requested: 'Changes requested',
    needs_human_review: 'Human review needed' };
  if (!report || !Object.hasOwn(verdicts, report.verdict)
    || typeof report.summary !== 'string' || !report.summary.trim() || report.summary.length > 3000
    || !Array.isArray(report.findings) || report.findings.length > 10
    || !Array.isArray(report.limitations) || report.limitations.length > 10
    || report.limitations.some(item => typeof item !== 'string' || item.length > 2000)) {
    throw new Error('Invalid review report');
  }
  for (const finding of report.findings) {
    if (!['P0', 'P1', 'P2'].includes(finding.priority)
      || !['title', 'body', 'path'].every(key => typeof finding[key] === 'string' && finding[key].trim())
      || finding.title.length > 200 || finding.body.length > 3000
      || !files.includes(finding.path) || /[\x00-\x1f]/.test(finding.path)
      || !Number.isSafeInteger(finding.line) || finding.line < 1) {
      throw new Error('Invalid review finding');
    }
  }
  const verdict = report.findings.length ? 'Changes requested' : verdicts[report.verdict];
  const lines = ['## PR Review', '', `**${verdict}** · Revision \`${sha.slice(0, 7)}\``, '', text(report.summary)];
  for (const finding of [...report.findings].sort((a, b) => a.priority.localeCompare(b.priority))) {
    const path = finding.path.split('/').map(encodeURIComponent).join('/');
    const url = `https://github.com/${repository}/blob/${sha}/${path}#L${finding.line}`;
    lines.push('', `### ${finding.priority}: ${text(finding.title)}`, '',
      `[${text(finding.path)}:${finding.line}](${url})`, '', text(finding.body));
  }
  if (report.limitations.length) {
    lines.push('', '**Verification limits**', ...report.limitations.map(item => `- ${text(item)}`));
  }
  lines.push('', report.findings.length ? 'Please address these findings and push an update.' : 'Check the PR Checks comment before merging.',
    'This review is advisory; the maintainer makes the merge decision.');
  return lines.join('\n');
}

function renderUnavailable(reason, sha, url) {
  const reasons = {
    not_configured: 'Maintainer setup is required before automated review can run.',
    too_large: 'The change exceeds the automated review size limit.',
    failed: 'The automated review did not complete or returned an invalid report.',
  };
  return `## PR Review\n\n**Manual review required** · Revision \`${sha.slice(0, 7)}\`\n\n${reasons[reason] || reasons.failed}\n\nThis is not a passing review. [Workflow details](${url})`;
}

async function upsertComment(github, repo, number, marker, body, runId) {
  const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: number, per_page: 100 });
  const existing = comments.find(comment => comment.user?.login === 'github-actions[bot]' && comment.body?.startsWith(marker));
  const previousRun = Number(existing?.body?.match(/<!-- feedback-run: (\d+) -->/)?.[1] || 0);
  if (runId && previousRun > runId) return;
  const stamp = runId ? `<!-- feedback-run: ${runId} -->\n` : '';
  const content = `${marker}\n${stamp}${body}`;
  if (existing) {
    await github.rest.issues.updateComment({ ...repo, comment_id: existing.id, body: content });
  } else {
    await github.rest.issues.createComment({ ...repo, issue_number: number, body: content });
  }
}

async function resolvePull(github, context) {
  const repo = context.repo;
  let candidates;
  let run;
  if (context.eventName === 'workflow_dispatch') {
    const number = Number(context.payload.inputs?.pr_number);
    if (!Number.isSafeInteger(number) || number < 1) throw new Error('A positive PR number is required');
    candidates = [{ number }];
  } else {
    run = (await github.rest.actions.getWorkflowRun({ ...repo, run_id: context.payload.workflow_run.id })).data;
    if (run.event !== 'pull_request' || run.path !== '.github/workflows/ci.yml' || run.status !== 'completed') return null;
    candidates = run.pull_requests || [];
    // GitHub sometimes omits fork PR associations on workflow_run events.
    if (!candidates.length) {
      candidates = await github.paginate(github.rest.repos.listPullRequestsAssociatedWithCommit,
        { ...repo, commit_sha: run.head_sha, per_page: 100 });
    }
  }
  for (const candidate of candidates) {
    const pr = (await github.rest.pulls.get({ ...repo, pull_number: candidate.number })).data;
    if (isCurrent(pr, run?.head_sha || pr.head.sha, `${repo.owner}/${repo.repo}`, context.eventName === 'workflow_dispatch')) {
      if (run && pr.head.repo?.full_name !== run.head_repository?.full_name) continue;
      return { pr, run };
    }
  }
  return null;
}

async function prepare({ github, context, core }) {
  const target = await resolvePull(github, context);
  if (!target) return;
  const { pr, run } = target;
  core.setOutput('pr_number', pr.number);
  core.setOutput('head_sha', pr.head.sha);
  core.setOutput('base_sha', pr.base.sha);
  if (run) {
    const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRun,
      { ...context.repo, run_id: run.id, filter: 'latest', per_page: 100 });
    // Recheck after API reads so an obsolete run cannot overwrite current feedback.
    const current = (await github.rest.pulls.get({ ...context.repo, pull_number: pr.number })).data;
    if (!isCurrent(current, pr.head.sha, `${context.repo.owner}/${context.repo.repo}`, context.eventName === 'workflow_dispatch')) return;
    await upsertComment(github, context.repo, pr.number, '<!-- pr-checks -->', renderChecks(run, jobs), context.runId);
  }
}

async function prepareReview({ github, context, core }, number, sha, directory) {
  const fs = require('node:fs');
  const pr = (await github.rest.pulls.get({ ...context.repo, pull_number: Number(number) })).data;
  if (!isCurrent(pr, sha, `${context.repo.owner}/${context.repo.repo}`, context.eventName === 'workflow_dispatch')) return;
  const files = await github.paginate(github.rest.pulls.listFiles, { ...context.repo, pull_number: pr.number, per_page: 100 });
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(`${directory}/pr.json`, JSON.stringify({ number: pr.number, title: pr.title, body: pr.body,
    head_sha: sha, base_sha: pr.base.sha, files: files.map(file => ({ path: file.filename, status: file.status })) }, null, 2));
  core.setOutput('current', 'true');
}

async function publish({ github, context, core }, { number, sha, raw, reason }) {
  const repository = `${context.repo.owner}/${context.repo.repo}`;
  const pr = (await github.rest.pulls.get({ ...context.repo, pull_number: Number(number) })).data;
  if (!isCurrent(pr, sha, repository, context.eventName === 'workflow_dispatch')) return;
  const url = `https://github.com/${repository}/actions/runs/${context.runId}`;
  let body = renderUnavailable(reason || 'failed', sha, url);
  if (raw && !reason) {
    try {
      const files = await github.paginate(github.rest.pulls.listFiles, { ...context.repo, pull_number: pr.number, per_page: 100 });
      body = renderReview(JSON.parse(raw), repository, sha, files.map(file => file.filename));
    } catch (error) {
      core.warning(`Review report rejected: ${error.message}`);
    }
  }
  // Discard results if a new commit arrived while rendering.
  const current = (await github.rest.pulls.get({ ...context.repo, pull_number: pr.number })).data;
  if (!isCurrent(current, sha, repository, context.eventName === 'workflow_dispatch')) return;
  await upsertComment(github, context.repo, pr.number, '<!-- pr-review -->', body, context.runId);
}

module.exports = { isCurrent, renderChecks, renderReview, renderUnavailable, upsertComment,
  resolvePull, prepare, prepareReview, publish };
