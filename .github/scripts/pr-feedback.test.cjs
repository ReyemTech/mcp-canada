const { test } = require('node:test');
const assert = require('node:assert/strict');
const feedback = require('./pr-feedback.cjs');

const sha = 'a'.repeat(40);
const passingCI = { state: 'passed', url: 'https://github.com/run/1' };
const report = (overrides = {}) => ({ verdict: 'ready', summary: 'The change fits its scope.',
  strengths: ['The new fixture covers the boundary case.'], findings: [], suggestions: [],
  checklist: [{ label: 'Compatibility', status: 'passed', evidence: 'Existing call signatures are preserved.' }],
  limitations: ['Live API not checked.'], ...overrides });
const jobs = () => ['3.12', '3.13', '3.14'].map(version => ({
  name: `Test (Python ${version})`, conclusion: 'success', html_url: 'job', steps: [],
}));
const pr = { number: 9, user: { login: 'contributor' }, requested_reviewers: [], state: 'open', draft: false, head: { sha, ref: 'feature', repo: { full_name: 'ReyemTech/mcp-canada' } },
  base: { ref: 'main', repo: { full_name: 'ReyemTech/mcp-canada' } } };

test('a completed run cannot publish feedback on a newer PR revision', () => {
  assert.equal(feedback.isCurrent(pr, 'b'.repeat(40), 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent(pr, sha, 'ReyemTech/mcp-canada'), true);
  assert.equal(feedback.isCurrent({ ...pr, draft: true }, sha, 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent({ ...pr, draft: true }, sha, 'ReyemTech/mcp-canada', true), true);
  assert.equal(feedback.isCurrent({ ...pr, state: 'closed' }, sha, 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent(pr, sha, 'other/repo'), false);
});

test('CI failures give contributors reproduction commands and job links', () => {
  const body = feedback.renderChecks({ head_sha: sha, status: 'completed', conclusion: 'failure', html_url: 'https://github.com/run/1' }, [
    { name: 'Test (Python 3.12)', conclusion: 'failure', html_url: 'https://github.com/job/2',
      steps: [{ name: 'Check catalog freshness', conclusion: 'failure' }] },
  ]);
  assert.match(body, /Changes needed/);
  assert.match(body, /uv run python scripts\/generate_catalog.py/);
  assert.match(body, /https:\/\/github.com\/job\/2/);
  assert.doesNotMatch(body, /All checks passed/);
});

test('cancelled or empty runs are never reported as passing', () => {
  for (const conclusion of ['cancelled', 'failure', null, 'success']) {
    assert.doesNotMatch(feedback.renderChecks({ head_sha: sha, status: 'completed', conclusion, html_url: 'run' }, []), /All checks passed/);
  }
});

test('CI recovery produces a passing status', () => {
  assert.match(feedback.renderChecks({ head_sha: sha, status: 'completed', conclusion: 'success', html_url: 'run' }, jobs()), /All checks passed/);
});

test('a successful run with only skipped jobs is not reported as passing', () => {
  assert.doesNotMatch(feedback.renderChecks({ head_sha: sha, status: 'completed', conclusion: 'success', html_url: 'run' }, [
    { name: 'Test', conclusion: 'skipped', html_url: 'job', steps: [] },
  ]), /All checks passed/);
});

test('medium priority findings request fixes with immutable source links', () => {
  const body = feedback.renderReview(report({ verdict: 'changes_requested', summary: 'Aggregation is incomplete.',
    findings: [{ priority: 'P2', title: 'Read every catalog page', body: 'The second page is never fetched.',
      path: 'src/client.py', line: 42 }], limitations: ['Live API not checked.'] }),
  'ReyemTech/mcp-canada', sha, ['src/client.py'], passingCI);
  assert.match(body, /Changes requested/);
  assert.match(body, /P2/);
  assert.match(body, new RegExp(`/blob/${sha}/src/client.py#L42`));
  assert.match(body, /Live API not checked/);
});

test('malformed reports and invented source locations fail validation', () => {
  for (const report of [null, {}, { verdict: 'ready', summary: 'Fine', findings: [{}], limitations: [] },
    { verdict: 'ready', summary: 'Fine', findings: [], limitations: 'untested' },
    { verdict: 'ready', summary: 'Fine', findings: [{ priority: 'P2', title: 'Bug', body: 'Fix it', path: 'secret', line: 1 }], limitations: [] }]) {
    assert.throws(() => feedback.renderReview(report, 'ReyemTech/mcp-canada', sha, ['src/client.py']));
  }
});

test('public review text cannot ping contributors or inject HTML', () => {
  const body = feedback.renderReview(report({ verdict: 'needs_human_review', summary: '@someone <img src=x>',
    findings: [], limitations: [] }), 'ReyemTech/mcp-canada', sha, [], passingCI);
  assert.doesNotMatch(body, /@someone|<img/);
  assert.match(body, /Manual review required/);
});

test('missing credentials or reviewer failures explicitly require manual review', () => {
  for (const reason of ['not_configured', 'failed', 'too_large']) {
    const body = feedback.renderUnavailable(reason, sha, 'https://github.com/run/1');
    assert.match(body, /manual review/i);
    assert.doesNotMatch(body, /Ready for maintainer review|No findings/);
  }
});

test('updates its own comment instead of duplicating it or overwriting user comments', async () => {
  const comments = [
    { id: 1, user: { login: 'contributor' }, body: '<!-- pr-checks --> user text' },
    { id: 2, user: { login: 'github-actions[bot]' }, body: '<!-- pr-checks --> old failure' },
  ];
  const github = {
    paginate: async () => comments,
    rest: { issues: { listComments: () => {},
      updateComment: async ({ comment_id, body }) => { comments.find(c => c.id === comment_id).body = body; },
      createComment: async ({ body }) => { comments.push({ id: 3, user: { login: 'github-actions[bot]' }, body }); },
    } },
  };
  await feedback.upsertComment(github, { owner: 'ReyemTech', repo: 'mcp-canada' }, 9, '<!-- pr-checks -->', 'recovered');
  assert.equal(comments.length, 2);
  assert.equal(comments[0].body, '<!-- pr-checks --> user text');
  assert.equal(comments[1].body, '<!-- pr-checks -->\nrecovered');
});

function apiFixture({ pull = pr, run = {}, comments = [] } = {}) {
  const store = { comments, reads: 0 };
  const github = {
    paginate: async (method) => method(),
    rest: {
      actions: { getWorkflowRun: async () => ({ data: run }) },
      repos: { listPullRequestsAssociatedWithCommit: async () => [{ number: 9 }] },
      pulls: { get: async () => { store.reads++; return { data: pull }; }, listFiles: async () => [{ filename: 'src/client.py' }] },
      issues: {
        listComments: async () => store.comments,
        createComment: async ({ body }) => { store.comments.push({ user: { login: 'github-actions[bot]' }, body }); },
      },
    },
  };
  return { github, store, context: { repo: { owner: 'ReyemTech', repo: 'mcp-canada' },
    runId: 123, eventName: 'workflow_run', payload: { workflow_run: { id: 123 } } } };
}

test('fork PR lookup works when workflow_run omits pull_requests', async () => {
  const fixture = apiFixture({ pull: { ...pr, head: { sha, repo: { full_name: 'contributor/fork' } } },
    run: { event: 'pull_request', path: '.github/workflows/ci.yml', status: 'completed', head_sha: sha,
      head_repository: { full_name: 'contributor/fork' }, pull_requests: [] } });
  assert.equal((await feedback.resolvePull(fixture.github, fixture.context)).pr.number, 9);
});

test('unrelated workflows and fork-repository mismatches cannot trigger review', async () => {
  for (const run of [
    { event: 'push', path: '.github/workflows/ci.yml', status: 'completed', head_sha: sha },
    { event: 'pull_request', path: '.github/workflows/other.yml', status: 'completed', head_sha: sha },
    { event: 'pull_request', path: '.github/workflows/ci.yml', status: 'completed', head_sha: sha,
      head_repository: { full_name: 'wrong/fork' } },
  ]) {
    const fixture = apiFixture({ pull: { ...pr, head: { sha, repo: { full_name: 'contributor/fork' } } }, run });
    assert.equal(await feedback.resolvePull(fixture.github, fixture.context), null);
  }
});

test('a stale review cannot create a PR comment', async () => {
  const fixture = apiFixture();
  await feedback.publish({ ...fixture, core: { warning() {} } }, { number: 9, sha: 'b'.repeat(40), raw: '{}'});
  assert.equal(fixture.store.comments.length, 0);
});

test('invalid model output publishes a manual-review notice rather than a clean review', async () => {
  const fixture = apiFixture();
  await feedback.publish({ ...fixture, core: { warning() {} } }, { number: 9, sha, raw: 'not JSON' });
  assert.equal(fixture.store.comments.length, 1);
  assert.match(fixture.store.comments[0].body, /Manual review required/);
  assert.doesNotMatch(fixture.store.comments[0].body, /Ready for maintainer review/);
});

test('an older feedback run cannot overwrite a newer review of the same commit', async () => {
  const comments = [{ id: 1, user: { login: 'github-actions[bot]' },
    body: '<!-- pr-review -->\n<!-- feedback-run: 200 -->\nNewer review' }];
  const fixture = apiFixture({ comments });
  fixture.github.rest.issues.updateComment = async ({ body }) => { comments[0].body = body; };
  await feedback.upsertComment(fixture.github, fixture.context.repo, 9, '<!-- pr-review -->', 'Old review', 123);
  assert.match(comments[0].body, /Newer review/);
  assert.doesNotMatch(comments[0].body, /Old review/);
});


test('only a clean review plus passing current CI recommends merging', () => {
  const body = feedback.renderReview(report(), 'ReyemTech/mcp-canada', sha, [], passingCI);
  assert.match(body, /Merge recommended/);
  assert.match(body, /What's solid/);
  assert.match(body, /Checklist/);
  assert.match(body, /Compatibility/);
  assert.match(body, /Existing call signatures/);
  for (const state of ['pending', 'unavailable']) {
    const blocked = feedback.renderReview(report(), 'ReyemTech/mcp-canada', sha, [], { state });
    assert.doesNotMatch(blocked, /Merge recommended/);
    assert.match(blocked, /Manual review required/);
  }
  const failed = feedback.renderReview(report(), 'ReyemTech/mcp-canada', sha, [], { state: 'failed' });
  assert.doesNotMatch(failed, /Merge recommended/);
  assert.match(failed, /Changes requested/);
});

test('optional suggestions stay separate and do not block merging', () => {
  const body = feedback.renderReview(report({ suggestions: [{ title: 'Share the prefix list',
    body: 'A shared constant could avoid future drift.', path: 'src/client.py', line: 10 }] }),
  'ReyemTech/mcp-canada', sha, ['src/client.py'], passingCI);
  assert.match(body, /Merge recommended/);
  assert.match(body, /Suggestions.*non-blocking/);
  assert.match(body, /<details>/);
  assert.match(body, new RegExp(`/blob/${sha}/src/client.py#L10`));
  assert.doesNotMatch(body, /Please address these findings/);
});

test('incomplete or failed review checklists cannot claim a clean review', () => {
  const body = feedback.renderReview(report({ verdict: 'needs_human_review', checklist: [
    { label: 'Endpoint contract', status: 'not_verified', evidence: 'No live response was supplied.' },
  ] }), 'ReyemTech/mcp-canada', sha, [], passingCI);
  assert.match(body, /Manual review required/);
  assert.match(body, /Not verified/);
  assert.doesNotMatch(body, /Merge recommended/);
  assert.throws(() => feedback.renderReview(report({ checklist: [] }), 'ReyemTech/mcp-canada', sha, [], passingCI));
  assert.throws(() => feedback.renderReview(report({ checklist: [
    { label: 'Compatibility', status: 'failed', evidence: 'Caller output breaks.' },
  ] }), 'ReyemTech/mcp-canada', sha, [], passingCI));
});

test('suggestions and checklist content cannot inject HTML or user mentions', () => {
  const body = feedback.renderReview(report({ strengths: ['@someone <script>'], suggestions: [
    { title: '</summary>@someone', body: '<img src=x>', path: 'src/client.py', line: 1 },
  ], checklist: [{ label: '@someone', status: 'passed', evidence: '<img src=x>' }] }),
  'ReyemTech/mcp-canada', sha, ['src/client.py'], passingCI);
  assert.doesNotMatch(body, /@someone|<img|<script>/);
  assert.throws(() => feedback.renderReview(report({ suggestions: [
    { title: 'Fix', body: 'Fix', path: 'unrelated.py', line: 1 },
  ] }), 'ReyemTech/mcp-canada', sha, ['src/client.py'], passingCI));
});

test('CI must contain all three successful matrix jobs for the current head', () => {
  const run = { head_sha: sha, status: 'completed', conclusion: 'success', html_url: 'run' };
  assert.equal(feedback.ciStatus(run, jobs(), sha).state, 'passed');
  assert.notEqual(feedback.ciStatus(run, jobs().slice(0, 2), sha).state, 'passed');
  assert.notEqual(feedback.ciStatus(run, jobs().map(job => ({ ...job, conclusion: 'skipped' })), sha).state, 'passed');
  assert.notEqual(feedback.ciStatus(run, jobs(), 'b'.repeat(40)).state, 'passed');
  assert.equal(feedback.ciStatus({ ...run, status: 'in_progress', conclusion: null }, jobs(), sha).state, 'pending');
});

test('latest CI lookup never falls back to an older passing run', async () => {
  const fixture = apiFixture();
  fixture.github.paginate = async method => method();
  fixture.github.rest.actions.listWorkflowRuns = async () => [
    { id: 20, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }], status: 'completed', conclusion: 'success', html_url: 'older' },
    { id: 21, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }], status: 'in_progress', conclusion: null, html_url: 'newer' },
  ];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  const status = await feedback.latestCI(fixture.github, fixture.context.repo, pr);
  assert.equal(status.state, 'pending');
  assert.equal(status.url, 'newer');
});

test('publisher checks live CI independently of the model report', async () => {
  const fixture = apiFixture();
  fixture.github.rest.actions.listWorkflowRuns = async () => [
    { id: 21, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }], status: 'completed', conclusion: 'failure', html_url: 'run' },
  ];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  await feedback.publish({ ...fixture, core: { warning() {} } }, { number: 9, sha, raw: JSON.stringify(report()) });
  assert.match(fixture.store.comments[0].body, /Changes requested/);
  assert.doesNotMatch(fixture.store.comments[0].body, /Merge recommended/);
});

test('a passing run from another PR with the same head cannot approve this PR', async () => {
  const fixture = apiFixture();
  fixture.github.rest.actions.listWorkflowRuns = async () => [
    { id: 20, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo,
      pull_requests: [{ number: 9, base: { ref: 'main' } }], status: 'completed', conclusion: 'failure', html_url: 'ours' },
    { id: 21, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo,
      pull_requests: [{ number: 10, base: { ref: 'release' } }], status: 'completed', conclusion: 'success', html_url: 'other' },
  ];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  const status = await feedback.latestCI(fixture.github, fixture.context.repo, pr);
  assert.equal(status.state, 'failed');
  assert.equal(status.url, 'ours');
});

test('missing run associations withhold a merge signal even for a unique current PR', async () => {
  const fixture = apiFixture();
  fixture.github.rest.actions.listWorkflowRuns = async () => [
    { id: 21, head_sha: sha, head_branch: pr.head.ref, head_repository: pr.head.repo,
      pull_requests: [], status: 'completed', conclusion: 'success', html_url: 'run' },
  ];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  fixture.github.rest.repos.listPullRequestsAssociatedWithCommit = async () => [pr];
  assert.equal((await feedback.latestCI(fixture.github, fixture.context.repo, pr)).state, 'unavailable');
  fixture.github.rest.repos.listPullRequestsAssociatedWithCommit = async () => [pr, { ...pr, number: 10 }];
  assert.equal((await feedback.latestCI(fixture.github, fixture.context.repo, pr)).state, 'unavailable');
});

test('large escaped reports fall back to manual review instead of exceeding GitHub limits', async () => {
  const fixture = apiFixture();
  const oversized = report({ summary: '*'.repeat(3000), strengths: Array(6).fill('*'.repeat(2000)),
    checklist: Array(10).fill({ label: 'Check', status: 'passed', evidence: '*'.repeat(2000) }),
    limitations: Array(5).fill('*'.repeat(2000)) });
  assert.ok(Buffer.byteLength(JSON.stringify(oversized)) < 50000);
  await feedback.publish({ ...fixture, core: { warning() {} } }, { number: 9, sha, raw: JSON.stringify(oversized) });
  assert.match(fixture.store.comments[0].body, /Manual review required/);
  assert.ok(fixture.store.comments[0].body.length < 65000);
});

test('ready reviews tag the maintainer and request their review', async () => {
  const fixture = apiFixture();
  fixture.github.rest.actions.listWorkflowRuns = async () => [{ id: 21, head_sha: sha,
    head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }],
    status: 'completed', conclusion: 'success', html_url: 'run' }];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  fixture.github.rest.pulls.listReviews = async () => [];
  const requested = [];
  fixture.github.rest.pulls.requestReviewers = async args => requested.push(args);
  await feedback.publish({ ...fixture, core: { warning() {} } },
    { number: 9, sha, raw: JSON.stringify(report()), maintainer: 'mariomeyer' });
  assert.match(fixture.store.comments[0].body, /@mariomeyer.*merge/i);
  assert.equal(requested.length, 1);
  assert.deepEqual(requested[0].reviewers, ['mariomeyer']);
});

test('blocking findings tag only the actual PR author, not names from the report', async () => {
  const fixture = apiFixture();
  const blocking = report({ verdict: 'changes_requested', findings: [{ priority: 'P2', title: 'Fix paging',
    body: '@untrusted please fix this', path: 'src/client.py', line: 1 }] });
  await feedback.publish({ ...fixture, core: { warning() {} } },
    { number: 9, sha, raw: JSON.stringify(blocking), maintainer: 'mariomeyer' });
  assert.match(fixture.store.comments[0].body, /@contributor.*address/i);
  assert.doesNotMatch(fixture.store.comments[0].body, /@mariomeyer|@untrusted/);
});

test('a maintainer who authored the PR is mentioned without an invalid self-review request', async () => {
  const fixture = apiFixture({ pull: { ...pr, user: { login: 'mariomeyer' } } });
  fixture.github.rest.actions.listWorkflowRuns = async () => [{ id: 21, head_sha: sha,
    head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }],
    status: 'completed', conclusion: 'success', html_url: 'run' }];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  fixture.github.rest.pulls.requestReviewers = async () => { throw new Error('Self request attempted'); };
  await feedback.publish({ ...fixture, core: { warning() {} } },
    { number: 9, sha, raw: JSON.stringify(report()), maintainer: 'mariomeyer' });
  assert.match(fixture.store.comments[0].body, /@mariomeyer/);
  assert.match(fixture.store.comments[0].body, /author.*own PR|own PR.*review/i);
});

test('a pending review request or completed review is not requested again', async () => {
  for (const alreadyRequested of [true, false]) {
    const fixture = apiFixture({ pull: { ...pr, requested_reviewers: alreadyRequested ? [{ login: 'mariomeyer' }] : [] } });
    fixture.github.rest.actions.listWorkflowRuns = async () => [{ id: 21, head_sha: sha,
      head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }],
      status: 'completed', conclusion: 'success', html_url: 'run' }];
    fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
    fixture.github.rest.pulls.listReviews = async () => [{ user: { login: 'mariomeyer' }, commit_id: sha, state: 'APPROVED' }];
    const requested = [];
    fixture.github.rest.pulls.requestReviewers = async args => { requested.push(args); };
    await feedback.publish({ ...fixture, core: { warning() {} } },
      { number: 9, sha, raw: JSON.stringify(report()), maintainer: 'mariomeyer' });
    assert.match(fixture.store.comments[0].body, /Merge recommended/);
    assert.equal(requested.length, 0);
  }
});

test('failed reviewer assignment is visible in the comment', async () => {
  const fixture = apiFixture();
  fixture.github.rest.actions.listWorkflowRuns = async () => [{ id: 21, head_sha: sha,
    head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }],
    status: 'completed', conclusion: 'success', html_url: 'run' }];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  fixture.github.rest.pulls.listReviews = async () => [];
  fixture.github.rest.pulls.requestReviewers = async () => { throw new Error('API unavailable'); };
  await feedback.publish({ ...fixture, core: { warning() {} } },
    { number: 9, sha, raw: JSON.stringify(report()), maintainer: 'mariomeyer' });
  assert.match(fixture.store.comments[0].body, /could not.*request.*review/i);
});

test('ambiguous commit associations cannot send feedback to the wrong PR', async () => {
  const fixture = apiFixture({ pull: { ...pr, head: { ...pr.head, repo: { full_name: 'contributor/fork' } } },
    run: { event: 'pull_request', path: '.github/workflows/ci.yml', status: 'completed', head_sha: sha,
      head_repository: { full_name: 'contributor/fork' }, pull_requests: [] } });
  fixture.github.rest.repos.listPullRequestsAssociatedWithCommit = async () => [{ number: 9 }, { number: 10 }];
  assert.equal(await feedback.resolvePull(fixture.github, fixture.context), null);
});

test('an older ready result cannot request review after a newer blocking comment', async () => {
  const fixture = apiFixture({ comments: [{ id: 1, user: { login: 'github-actions[bot]' },
    body: '<!-- pr-review -->\n<!-- feedback-run: 200 -->\nChanges requested' }] });
  fixture.github.rest.actions.listWorkflowRuns = async () => [{ id: 21, head_sha: sha,
    head_branch: pr.head.ref, head_repository: pr.head.repo, pull_requests: [{ number: 9, base: { ref: 'main' } }],
    status: 'completed', conclusion: 'success', html_url: 'run' }];
  fixture.github.rest.actions.listJobsForWorkflowRun = async () => jobs();
  fixture.github.rest.pulls.listReviews = async () => [];
  const requested = [];
  fixture.github.rest.pulls.requestReviewers = async args => { requested.push(args); };
  await feedback.publish({ ...fixture, core: { warning() {} } },
    { number: 9, sha, raw: JSON.stringify(report()), maintainer: 'mariomeyer' });
  assert.equal(requested.length, 0);
  assert.match(fixture.store.comments[0].body, /Changes requested/);
});
