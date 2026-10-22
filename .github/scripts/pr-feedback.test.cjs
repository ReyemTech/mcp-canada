const { test } = require('node:test');
const assert = require('node:assert/strict');
const feedback = require('./pr-feedback.cjs');

const sha = 'a'.repeat(40);
const pr = { number: 9, state: 'open', draft: false, head: { sha },
  base: { repo: { full_name: 'ReyemTech/mcp-canada' } } };

test('a completed run cannot publish feedback on a newer PR revision', () => {
  assert.equal(feedback.isCurrent(pr, 'b'.repeat(40), 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent(pr, sha, 'ReyemTech/mcp-canada'), true);
  assert.equal(feedback.isCurrent({ ...pr, draft: true }, sha, 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent({ ...pr, draft: true }, sha, 'ReyemTech/mcp-canada', true), true);
  assert.equal(feedback.isCurrent({ ...pr, state: 'closed' }, sha, 'ReyemTech/mcp-canada'), false);
  assert.equal(feedback.isCurrent(pr, sha, 'other/repo'), false);
});

test('CI failures give contributors reproduction commands and job links', () => {
  const body = feedback.renderChecks({ head_sha: sha, conclusion: 'failure', html_url: 'https://github.com/run/1' }, [
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
    assert.doesNotMatch(feedback.renderChecks({ head_sha: sha, conclusion, html_url: 'run' }, []), /All checks passed/);
  }
});

test('CI recovery produces a passing status', () => {
  assert.match(feedback.renderChecks({ head_sha: sha, conclusion: 'success', html_url: 'run' }, [
    { name: 'Test', conclusion: 'success', html_url: 'job', steps: [] },
  ]), /All checks passed/);
});

test('a successful run with only skipped jobs is not reported as passing', () => {
  assert.doesNotMatch(feedback.renderChecks({ head_sha: sha, conclusion: 'success', html_url: 'run' }, [
    { name: 'Test', conclusion: 'skipped', html_url: 'job', steps: [] },
  ]), /All checks passed/);
});

test('medium priority findings request fixes with immutable source links', () => {
  const body = feedback.renderReview({ verdict: 'changes_requested', summary: 'Aggregation is incomplete.',
    findings: [{ priority: 'P2', title: 'Read every catalog page', body: 'The second page is never fetched.',
      path: 'src/client.py', line: 42 }], limitations: ['Live API not checked.'] },
  'ReyemTech/mcp-canada', sha, ['src/client.py']);
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
  const body = feedback.renderReview({ verdict: 'needs_human_review', summary: '@someone <img src=x>',
    findings: [], limitations: [] }, 'ReyemTech/mcp-canada', sha, []);
  assert.doesNotMatch(body, /@someone|<img/);
  assert.match(body, /Human review needed/);
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
