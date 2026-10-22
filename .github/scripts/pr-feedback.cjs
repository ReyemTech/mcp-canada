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

function isCurrent(pr, sha, repository, allowDraft = false, base) {
  return pr.state === 'open' && (allowDraft || !pr.draft) && /^[a-f0-9]{40}$/.test(sha)
    && pr.head.sha === sha && pr.base.repo.full_name === repository
    && (!base || (pr.base.sha === base.sha && pr.base.ref === base.ref));
}

const REQUIRED_JOBS = ['3.12', '3.13', '3.14'].map(version => `Test (Python ${version})`);

function ciStatus(run, jobs, sha) {
  if (!run || run.head_sha !== sha) return { state: 'unavailable' };
  const url = run.html_url;
  if (run.status !== 'completed') return { state: 'pending', url };
  const passed = run.conclusion === 'success'
    && REQUIRED_JOBS.every(name => jobs.some(job => job.name === name && job.conclusion === 'success'))
    && jobs.every(job => job.conclusion === 'success' || job.conclusion === 'skipped');
  const failed = run.conclusion === 'failure' || jobs.some(job => job.conclusion === 'failure');
  return { state: passed ? 'passed' : failed ? 'failed' : 'unavailable', url };
}

function ciSnapshot(run) {
  const match = run.display_title?.match(/^CI PR#(\d+) BASE:([a-f0-9]{40}) REF:(.+)$/);
  return match ? { number: Number(match[1]), sha: match[2], ref: match[3] } : null;
}

function runMatchesBase(run, pr) {
  const base = ciSnapshot(run);
  return Boolean(base && base.number === pr.number && base.sha === pr.base.sha && base.ref === pr.base.ref);
}

async function latestCI(github, repo, pr) {
  const sha = pr.head.sha;
  const runs = await github.paginate(github.rest.actions.listWorkflowRuns,
    { ...repo, workflow_id: 'ci.yml', event: 'pull_request', head_sha: sha, per_page: 100 });
  const candidates = runs.filter(item => item.head_sha === sha && item.head_branch === pr.head.ref
    && item.head_repository?.full_name === pr.head.repo?.full_name).sort((a, b) => b.id - a.id);
  let run;
  for (const candidate of candidates) {
    const snapshot = ciSnapshot(candidate);
    // The workflow run name snapshots the triggering PR/base. The pull_requests
    // association is mutable and can describe a different base after retargeting.
    if (!snapshot) return { state: 'unavailable', url: candidate.html_url };
    if (snapshot.number !== pr.number) continue;
    if (!runMatchesBase(candidate, pr)) return { state: 'unavailable', url: candidate.html_url };
    run = candidate;
    break;
  }
  if (!run) return { state: 'unavailable' };
  if (run.status !== 'completed') return { state: 'pending', url: run.html_url };
  const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRun,
    { ...repo, run_id: run.id, filter: 'latest', per_page: 100 });
  return ciStatus(run, jobs, sha);
}

function renderChecks(run, jobs, verifiedBase = true) {
  const passed = verifiedBase && ciStatus(run, jobs, run.head_sha).state === 'passed';
  const lines = ['## PR Checks', '', `**${passed ? 'All checks passed' : 'Changes needed or checks incomplete'}**`,
    '', `Revision: \`${run.head_sha.slice(0, 7)}\` · [CI run](${run.html_url})`, ''];
  if (!verifiedBase) lines.push('CI ran against an older or unverified base. Push an update to the PR branch for fresh checks; these results do not establish CI for the current target.', '');
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
  const missing = REQUIRED_JOBS.filter(name => !jobs.some(job => job.name === name && job.conclusion === 'success'));
  if (missing.length) lines.push('', `Required jobs not passing: ${missing.map(text).join(', ')}.`);
  if (!passed && jobs.length) lines.push('', 'Please fix the failed checks and push an update. A new run will update this comment.');
  lines.push('', 'Merge decisions remain with the maintainer.');
  return lines.join('\n');
}

function baseMarker(base) {
  return `<!-- reviewed-base: ${base.sha}:${encodeURIComponent(base.ref)} -->`;
}

function requestMarker(base) {
  return `<!-- review-request-base: ${base.sha}:${encodeURIComponent(base.ref)} -->`;
}

function validLogin(login) {
  return typeof login === 'string' && /^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$/i.test(login);
}

function reviewDecision(report, ci) {
  if (report.findings.length || ci.state === 'failed') return 'changes_requested';
  return report.verdict === 'ready' && ci.state === 'passed' ? 'ready' : 'needs_human_review';
}

function renderReview(report, repository, sha, files, ci = { state: 'unavailable' }, routing = {}) {
  const validText = (value, limit) => typeof value === 'string' && value.trim() && value.length <= limit;
  const textList = (value, count, length) => Array.isArray(value) && value.length <= count
    && value.every(item => validText(item, length));
  const location = item => item && ['title', 'body', 'path'].every(key => validText(item[key], key === 'title' ? 200 : 3000))
    && files.includes(item.path) && !/[\x00-\x1f]/.test(item.path)
    && Number.isSafeInteger(item.line) && item.line > 0;
  if (!report || !['ready', 'changes_requested', 'needs_human_review'].includes(report.verdict)
    || !validText(report.summary, 3000) || !textList(report.strengths, 6, 2000)
    || !textList(report.limitations, 10, 2000)
    || !Array.isArray(report.findings) || report.findings.length > 10
    || !report.findings.every(item => location(item) && ['P0', 'P1', 'P2'].includes(item.priority))
    || !Array.isArray(report.suggestions) || report.suggestions.length > 5 || !report.suggestions.every(location)
    || !Array.isArray(report.checklist) || !report.checklist.length || report.checklist.length > 10
    || !report.checklist.every(item => item && validText(item.label, 200) && validText(item.evidence, 2000)
      && ['passed', 'failed', 'not_verified', 'not_applicable'].includes(item.status))
    || (report.verdict === 'changes_requested' && !report.findings.length)
    || (report.verdict === 'ready' && report.checklist.some(item => item.status === 'failed'))) {
    throw new Error('Invalid review report');
  }
  const decision = reviewDecision(report, ci);
  const blocked = decision === 'changes_requested';
  const ready = decision === 'ready';
  const verdict = blocked ? '🔴 Changes requested' : ready ? '🟢 Merge recommended' : '🟠 Manual review required';
  const lines = ['## PR Review', '', `**${verdict}** · Revision \`${sha.slice(0, 7)}\``];
  if (blocked && validLogin(routing.author)) lines.push('', `@${routing.author} please address the blocking issues or failed checks and push an update.`);
  if (ready && validLogin(routing.maintainer)) lines.push('', `@${routing.maintainer} merge recommended — please review and decide whether to merge.`);
  if (routing.base) lines.push('', baseMarker(routing.base), `Reviewed against: \`${text(routing.base.ref)}@${routing.base.sha.slice(0, 7)}\`. Recommendation applies to this head/base pair.`);
  lines.push('', text(report.summary));
  const ciLabels = { passed: 'All three CI jobs passed for this revision.', failed: 'CI failed or required jobs did not pass.',
    pending: 'CI is still running for this revision.', unavailable: 'Passing CI could not be verified for this revision.' };
  lines.push('', `**CI:** ${ciLabels[ci.state] || ciLabels.unavailable}${ci.url ? ` [View CI](${ci.url})` : ''}`);
  if (ready) lines.push('', 'No blocking findings. Merge recommended; optional suggestions can follow separately.');
  else if (blocked) lines.push('', 'Resolve the blocking findings or CI failures and push an update before merging.');
  else lines.push('', 'A merge recommendation is withheld until CI and the outstanding review questions are resolved.');
  if (report.strengths.length) lines.push('', "### What's solid", '', ...report.strengths.map(item => `- ${text(item)}`));
  lines.push('', '### Blocking issues', '');
  const link = item => `[${text(item.path)}:${item.line}](https://github.com/${repository}/blob/${sha}/${item.path.split('/').map(encodeURIComponent).join('/')}#L${item.line})`;
  if (!report.findings.length) lines.push(ci.state === 'failed' ? 'No blocking code findings; fix the CI failures above.' : 'No blocking code findings.');
  for (const finding of [...report.findings].sort((a, b) => a.priority.localeCompare(b.priority))) {
    lines.push(`#### ${finding.priority}: ${text(finding.title)}`, '', link(finding), '', text(finding.body), '');
  }
  if (report.suggestions.length) {
    lines.push('', '### 🟢 Suggestions (non-blocking)', '');
    report.suggestions.forEach((item, index) => lines.push('<details>', `<summary>Suggestion ${index + 1}</summary>`, '',
      `**${text(item.title)}**`, '', link(item), '', text(item.body), '', '</details>', ''));
  }
  lines.push('', '### Checklist', '', `- [${ci.state === 'passed' ? 'x' : ' '}] CI for this revision — ${ciLabels[ci.state] || ciLabels.unavailable}`);
  const labels = { passed: 'Verified', failed: 'Failed', not_verified: 'Not verified', not_applicable: 'Not applicable' };
  for (const item of report.checklist) {
    lines.push(`- [${item.status === 'passed' || item.status === 'not_applicable' ? 'x' : ' '}] ${text(item.label)} — **${labels[item.status]}:** ${text(item.evidence)}`);
  }
  if (report.limitations.length) lines.push('', '### Verification limits', '', ...report.limitations.map(item => `- ${text(item)}`));
  lines.push('', 'The maintainer makes the final merge decision.');
  const body = lines.join('\n');
  // Leave room for the marker/run stamp below GitHub's 65,536-character limit.
  if (body.length > 60000) throw new Error('Rendered review exceeds the comment limit');
  return body;
}

function renderUnavailable(reason, sha, url) {
  const reasons = {
    not_configured: 'Maintainer setup is required before automated review can run.',
    too_large: 'The change exceeds the automated review size limit.',
    failed: 'The automated review did not complete or returned an invalid report.',
  };
  return `## PR Review\n\n**Manual review required** · Revision \`${sha.slice(0, 7)}\`\n\n${reasons[reason] || reasons.failed}\n\nThis is not a passing review. [Workflow details](${url})`;
}

async function findBotComment(github, repo, number, marker) {
  const comments = await github.paginate(github.rest.issues.listComments, { ...repo, issue_number: number, per_page: 100 });
  return comments.find(comment => comment.user?.login === 'github-actions[bot]' && comment.body?.startsWith(marker));
}

function superseded(existing, runId) {
  const previousRun = Number(existing?.body?.match(/<!-- feedback-run: (\d+) -->/)?.[1] || 0);
  return Boolean(runId && previousRun > runId);
}

async function upsertComment(github, repo, number, marker, body, runId) {
  const existing = await findBotComment(github, repo, number, marker);
  if (superseded(existing, runId)) return;
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
    const snapshot = ciSnapshot(run);
    candidates = snapshot ? [{ number: snapshot.number }] : run.pull_requests || [];
    // GitHub sometimes omits fork PR associations on workflow_run events.
    if (!candidates.length) {
      candidates = await github.paginate(github.rest.repos.listPullRequestsAssociatedWithCommit,
        { ...repo, commit_sha: run.head_sha, per_page: 100 });
      // Commit associations do not identify a run when several PRs share it.
      if (candidates.length !== 1) return null;
    }
  }
  for (const candidate of candidates) {
    const pr = (await github.rest.pulls.get({ ...repo, pull_number: candidate.number })).data;
    if (isCurrent(pr, run?.head_sha || pr.head.sha, `${repo.owner}/${repo.repo}`, context.eventName === 'workflow_dispatch')) {
      if (run && (pr.head.repo?.full_name !== run.head_repository?.full_name
        || (run.head_branch && run.head_branch !== pr.head.ref))) continue;
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
  core.setOutput('base_ref', pr.base.ref);
  if (run) {
    const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRun,
      { ...context.repo, run_id: run.id, filter: 'latest', per_page: 100 });
    // Recheck after API reads so an obsolete run cannot overwrite current feedback.
    const current = (await github.rest.pulls.get({ ...context.repo, pull_number: pr.number })).data;
    if (!isCurrent(current, pr.head.sha, `${context.repo.owner}/${context.repo.repo}`, context.eventName === 'workflow_dispatch', pr.base)) return;
    await upsertComment(github, context.repo, pr.number, '<!-- pr-checks -->', renderChecks(run, jobs, runMatchesBase(run, pr)), context.runId);
  }
}

async function prepareReview({ github, context, core }, number, sha, directory, base) {
  const fs = require('node:fs');
  const pr = (await github.rest.pulls.get({ ...context.repo, pull_number: Number(number) })).data;
  if (!isCurrent(pr, sha, `${context.repo.owner}/${context.repo.repo}`, context.eventName === 'workflow_dispatch', base)) return;
  const files = await github.paginate(github.rest.pulls.listFiles, { ...context.repo, pull_number: pr.number, per_page: 100 });
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(`${directory}/pr.json`, JSON.stringify({ number: pr.number, title: pr.title, body: pr.body,
    head_sha: sha, base_sha: pr.base.sha, base_ref: pr.base.ref, files: files.map(file => ({ path: file.filename, status: file.status })) }, null, 2));
  core.setOutput('base_sha', pr.base.sha);
  core.setOutput('base_ref', pr.base.ref);
  core.setOutput('current', 'true');
}

async function requestMaintainerReview({ github, context, core }, pr, maintainer, sha, freshBase = false) {
  if (pr.user?.login.toLowerCase() === maintainer.toLowerCase()) {
    return 'GitHub does not allow an author to review their own PR; the maintainer was tagged instead.';
  }
  if (pr.draft) return 'Review requests are deferred until this draft is marked ready for review.';
  if (pr.requested_reviewers?.some(user => user.login.toLowerCase() === maintainer.toLowerCase())) return '';
  try {
    const reviews = await github.paginate(github.rest.pulls.listReviews,
      { ...context.repo, pull_number: pr.number, per_page: 100 });
    if (!freshBase && reviews.some(review => review.user?.login.toLowerCase() === maintainer.toLowerCase()
      && review.commit_id === sha && ['APPROVED', 'CHANGES_REQUESTED'].includes(review.state))) return '';
    await github.rest.pulls.requestReviewers({ ...context.repo, pull_number: pr.number, reviewers: [maintainer] });
    return '';
  } catch (error) {
    core.warning('Could not automatically request the maintainer review');
    return 'Could not automatically request the maintainer review. Please request it manually; the maintainer has been tagged above.';
  }
}

async function publish({ github, context, core }, { number, sha, raw, reason, maintainer, base }) {
  const repository = `${context.repo.owner}/${context.repo.repo}`;
  const pr = (await github.rest.pulls.get({ ...context.repo, pull_number: Number(number) })).data;
  if (!isCurrent(pr, sha, repository, context.eventName === 'workflow_dispatch', base)) return;
  const url = `https://github.com/${repository}/actions/runs/${context.runId}`;
  let body = renderUnavailable(reason || 'failed', sha, url);
  let decision;
  if (raw && !reason) {
    try {
      const files = await github.paginate(github.rest.pulls.listFiles, { ...context.repo, pull_number: pr.number, per_page: 100 });
      let ci;
      try {
        ci = await latestCI(github, context.repo, pr);
      } catch (error) {
        core.warning('Current CI status could not be verified');
        ci = { state: 'unavailable' };
      }
      const report = JSON.parse(raw);
      body = renderReview(report, repository, sha, files.map(file => file.filename), ci, { author: pr.user?.login, maintainer, base });
      decision = reviewDecision(report, ci);
      if (decision === 'ready' && !validLogin(maintainer)) {
        body = renderUnavailable('not_configured', sha, url);
        decision = undefined;
      }
    } catch (error) {
      core.warning(`Review report rejected: ${error.message}`);
    }
  }
  // Discard results if a new commit arrived while rendering.
  const current = (await github.rest.pulls.get({ ...context.repo, pull_number: pr.number })).data;
  if (!isCurrent(current, sha, repository, context.eventName === 'workflow_dispatch', base)) return;
  if (decision === 'ready') {
    const existing = await findBotComment(github, context.repo, pr.number, '<!-- pr-review -->');
    if (superseded(existing, context.runId)) return;
    const note = await requestMaintainerReview({ github, context, core }, current, maintainer, sha,
      Boolean(base && !existing?.body?.includes(requestMarker(base))));
    if (note) body += `\n\n${note}`;
    else if (base) body += `\n${requestMarker(base)}`;
    // A reviewer API call may race with a new contributor revision.
    const latest = (await github.rest.pulls.get({ ...context.repo, pull_number: pr.number })).data;
    if (!isCurrent(latest, sha, repository, context.eventName === 'workflow_dispatch', base)) return;
  }
  await upsertComment(github, context.repo, pr.number, '<!-- pr-review -->', body, context.runId);
}

module.exports = { ciStatus, latestCI, isCurrent, renderChecks, renderReview, renderUnavailable, upsertComment,
  resolvePull, prepare, prepareReview, publish };
