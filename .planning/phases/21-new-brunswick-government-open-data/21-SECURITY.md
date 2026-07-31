---
phase: 21
slug: new-brunswick-government-open-data
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-30
---

# Phase 21 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register built retroactively from the `<threat_model>` blocks of all 7 PLAN.md files
(`register_authored_at_plan_time: true`), deduplicated across plans, then verified against the
implemented code by `gsd-security-auditor`.

**The L1 short-circuit was deliberately overridden for this phase.** The workflow permits skipping
the auditor when `threats_open: 0` at grep depth, on the premise that L1 grep evidence is
sufficient. That premise is empirically false here: the post-execution code review found **CR-01**,
a hole in T-21-03's mitigation where the guard function existed and was greppable but tested Python
truthiness only, so `county="%"` matched all 604,520 parcel rows. A grep pass would have marked
T-21-03 CLOSED both before and after the fix. T-21-01, T-21-02, T-21-03, T-21-04 and T-21-16 were
therefore traced at L2/L3 depth by reasoning about code paths and test assertions, not symbol
presence.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| agent → MCP tool | Untrusted tool arguments enter the process | `where`, `select`, `q`, `extra_fq`, `county`, `community`, `street`, `civic_number`, `pid`, `service_name`, `layer_id`, `facility_type`, `sector`, `dataset_id`, `limit` |
| MCP tool → GeoNB ArcGIS Server | A SQL-92 WHERE clause and a service path cross to `geonb.snb.ca` | Server-built filter clauses; public geospatial open data returns |
| MCP tool → federal CKAN Solr | `q` and `fq` fragments cross to `open.canada.ca` | Search terms and the NB organization scope filter |
| MCP tool → gnb.socrata.com | SoQL `$where`/`$select` cross to NB's provincial Socrata portal | Caller-supplied SoQL; public provincial open data returns |
| MCP tool → NB 511 | An API credential crosses outbound to `511.gnb.ca` | `NEW_BRUNSWICK_511_KEY` as a query parameter (key-gated, unconfigured by default) |
| process environment → module | `NEW_BRUNSWICK_511_KEY` is read at call time, inside `client.py` only | Credential value — never reaches `tools.py`, never enters an envelope |
| repository documentation → future implementers | CLAUDE.md claims become binding constraints on later phases | Verified-vs-asserted portal facts |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-21-01 | Tampering | WHERE clauses sent to GeoNB `/query` by all curated tools | high | mitigate | No curated tool accepts a raw clause. `client.py:921-960` builds every clause server-side from typed params via `_escape_sql_value` / `_escape_like_value` / `_upper_contains_clause`. **Post-CR-01** the helper escapes `%`, `_` and `\` and emits `ESCAPE '\'`. Applied at all 9 clause-building sites. `civic_number`/`holder` are typed `int`, interpolated unquoted. | closed |
| T-21-02 | Information Disclosure | `Five11NotConfigured` message and the three 511 error envelopes | medium | mitigate | `tools.py` reads no environment at all (zero `os.environ`/`os.getenv` matches); the env is read only in `client.py:348`. `upstream_guard` traced: the `HTTPStatusError` arm echoes only `status_code`, and httpx's `HTTPError.__str__` returns the constructor message without request URL/params, so a key passed as a query param cannot leak. Sentinel-key non-leakage tests in `test_tools.py` and `test_client.py`. | closed |
| T-21-03 | Denial of Service | Unbounded GeoNB queries over Parcels (604,520), Civic_Address (373,172), Wetlands (163,206) | high | mitigate | `FILTER_REQUIRED_TOOLS` drives `_require_any_filter` plus a `_is_blank` tool-layer pre-check. **Post-CR-01** strings are `.strip()`ped and non-strings tested `is not None`, closing the whitespace and wildcard bypass. **Post-F2** (see Audit Notes — this was reopened) `_geonb_query` enforces `1 <= limit <= MAX_RECORDS` centrally, so every curated GeoNB tool inherits a real bound. `assert_not_awaited` tests prove no network I/O precedes rejection. | closed |
| T-21-04 | Tampering | `fq` composition on the five federal CKAN discovery tools | high | mitigate | `_build_fq` emits `f"({NB_ORG_FQ}) AND ({extra_fq})"` with explicit parens (WR-01, operator precedence). **Post-F1** (see Audit Notes — this was reopened) `_validate_extra_fq` rejects a fragment whose own unbalanced parentheses or quotes would break *out* of that wrapping, tracking nesting depth left-to-right rather than comparing counts. Whitespace-only fragments are treated as absent. No `organization` parameter is exposed to callers. | closed |
| T-21-05 | Information Disclosure | Cache keys shared across modules in the process-wide aiocache | low | accept | All NB data is public open data; every key is prefixed `new_brunswick:` (`constants.py:139`, applied at all 24 cache-key sites). A collision would be a correctness bug, not a disclosure. | closed |
| T-21-06 | Tampering | `q` passed through to Solr | low | accept | Solr escapes query terms server-side — the posture every prior CKAN-backed module ships. `q` and `fq` are separate params; `q` is never spliced into `fq`. | closed |
| T-21-07 | Denial of Service | `fetch_and_parse` on an arbitrary CKAN resource URL | medium | mitigate | `_PARSEABLE_RESOURCE_FORMATS` frozenset routes only CSV/XLSX/XLS/JSON/GEOJSON to the parser; archives and binaries return metadata-only. **Post-WR-03** a `limit <= 0` guard precedes any network call. Rows truncated to caller `limit` with a `truncated` flag. | closed |
| T-21-08 | Information Disclosure | Cache-key collision with the federal `ckan` module (same upstream host) | low | mitigate | `CACHE_KEY_PREFIX` applied consistently at all 24 client cache-key sites. See the caveat under **Audit Notes** — the disposition's "asserted in unit tests" claim is not literally satisfied, though the code mitigation is genuinely present. | closed |
| T-21-09 | Tampering | Prompt arguments echoed into workflow instructions an agent will act on | medium | mitigate | Prompt values are interpolated only into natural-language `Message` text, with explicit instructions to pass them as tool arguments and never as raw WHERE/fq fragments. Prompts never call tools or build clauses; the real backstop is T-21-01/T-21-04 at the named tools. | closed |
| T-21-10 | Information Disclosure | `docs://nb/portal-guide` describes the 511 credential mechanism | low | mitigate | The guide names `NEW_BRUNSWICK_511_KEY` and links `511.gnb.ca`; no key value appears anywhere in `resources.py`, and nothing instructs an agent to echo one back. | closed |
| T-21-11 | Spoofing | Static resource content could drift from the live portal | low | accept | Static reference data (counties, health authorities, school sectors) is stable; volatile parts (service list, layer ids) are regenerated from `21-SPIKE.md` and re-verified by 34 live integration scenarios. Drift is a documentation-accuracy risk, not a security one. | closed |
| T-21-12 | Tampering | Raw `where` passed through by `nb_query_geonb_layer` | medium | accept | Deliberate escape hatch making D-07's curation bar honest. Upstream is a read-only public open-data server with no write surface; ArcGIS's own SQL-92 parser is the trust boundary, named explicitly in the tool docstring, matching york_region / alberta / manitoba / saskatchewan. | closed |
| T-21-13 | Tampering | `service_name` interpolated into a GeoNB REST path | medium | mitigate | Validated against the live service directory and rejected with `NotFound` **before** any URL is constructed, in both `fetch_geonb_service_layers` and `fetch_geonb_layer_features`. `assert_not_awaited` tests prove no network call precedes rejection. | closed |
| T-21-14 | Denial of Service | `nb_get_geonb_service_layers` fans out per layer | low | mitigate | Cached at the 24h `CACHE_TTL_META`; `_geonb_limiter.acquire()` precedes every `get_count`/`get_layer_metadata` call, serialising the fan-out. Largest service has fewer than 10 layers. | closed |
| T-21-15 | Information Disclosure | Parcel and civic-address data identifies real property and locations | low | accept | Public open data published by Service New Brunswick and the Dept. of Public Safety, re-exposed exactly as served, with no linkage added. `fetch_parcels` out_fields are `PID,COUNTY,Titles_Status,Gazette_Status` — no owner field exists on the layer. | closed |
| T-21-16 | Tampering | `facility_type` / `sector` interpolated into a layer path | high | mitigate | Neither value is interpolated — both are looked up as keys of the constant `HEALTH_FACILITY_LAYERS` / `SCHOOL_SECTOR_LAYERS` dicts; a non-key raises `InvalidInput` before any URL is built, at both tool and client layers. Parametrized `call_args`-reading tests pin the dispatched `layer_id` for **every** key of both maps — the assertion class the Saskatchewan wrong-layer bug required. | closed |
| T-21-17 | Spoofing | A 511 response is trusted and flattened into an envelope | low | accept | HTTPS to a Government of New Brunswick host with httpx default certificate validation (`verify=False` appears nowhere in the module or `shared/`). A non-list body yields an empty list rather than a type error, so a malformed response degrades rather than crashes. | closed |
| T-21-18 | Repudiation | A tolerated upstream error masking a permanently dead tool | high | mitigate | `tests/test_integration_test_quality.py` runs in the default unit suite and rejects the masking idioms (9 tests, green). 34 NB live scenarios including a manifest-coverage meta-test binding `ALL_NB_TOOL_NAMES` to scenario coverage, so an untested tool cannot ship. The three 511 scenarios assert `NOT_CONFIGURED` by exact shape and are never wrapped in `tolerates_upstream_error`. | closed |
| T-21-19 | Spoofing | Documentation asserting an unverified claim that later phases inherit as fact | medium | mitigate | The concrete failure this phase inherited. CLAUDE.md now records the verified `gnb.socrata.com` facts; the false "no NB Socrata instance / no provincial catalogue" claim appears nowhere. The remaining unprobed province (PEI) is explicitly marked as requiring independent verification. | closed |
| T-21-20 | Tampering | Raw SoQL `where` / `select` passed through by `nb_query_gnb_socrata_dataset` | medium | accept | **Added during this audit** — see Audit Notes. Deliberate escape hatch making the whole 312-dataset portal reachable through two tools. Upstream is a read-only, keyless public open-data server with no write surface; Socrata's own SoQL parser is the trust boundary, now named explicitly in the tool docstring, matching the T-21-12 precedent. | closed |
| T-21-SC | Tampering | npm/pip/cargo installs | high | accept | Zero new external packages across the entire phase — `git diff 6aee36c..HEAD -- pyproject.toml uv.lock` is empty. `.claude/rules/engineering-standards.md` forbids new dependencies. Acceptance is void the moment a plan adds one. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (high) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-21-01 | T-21-05 | Cache-key namespace collision would be a correctness bug, not a disclosure — all NB data is public open data and keys are prefixed. | Phase 21 plan authors | 2026-07-30 |
| AR-21-02 | T-21-06 | Solr escapes query terms server-side; `q` is never spliced into `fq`. Matches the posture of every prior CKAN-backed module. | Phase 21 plan authors | 2026-07-30 |
| AR-21-03 | T-21-11 | Static reference data is stable; volatile parts are regenerated from the live spike and re-verified by live tests. Drift is a docs-accuracy risk. | Phase 21 plan authors | 2026-07-30 |
| AR-21-04 | T-21-12 | Raw-WHERE escape hatch against a read-only public server; ArcGIS SQL-92 parser is the documented trust boundary. Established precedent across four prior provinces. | Phase 21 plan authors | 2026-07-30 |
| AR-21-05 | T-21-15 | Public open data re-exposed exactly as published, no linkage added, no owner field on the layer. | Phase 21 plan authors | 2026-07-30 |
| AR-21-06 | T-21-17 | HTTPS with default cert validation; malformed bodies degrade to an empty list rather than crashing. | Phase 21 plan authors | 2026-07-30 |
| AR-21-07 | T-21-20 | Raw-SoQL escape hatch against a read-only, keyless public server; Socrata's SoQL parser is the trust boundary, same risk class as the already-accepted AR-21-04. | Orchestrator, during this audit | 2026-07-30 |
| AR-21-08 | T-21-SC | Zero new dependencies across the phase; verified by an empty `pyproject.toml`/`uv.lock` diff. Void if any future plan adds one. | Phase 21 plan authors | 2026-07-30 |

*Accepted risks do not resurface in future audit runs.*

---

## Audit Notes

**T-21-20 was not in the plan-time register — it was created by the Wave 0 checkpoint.** The blocking
`checkpoint:decision` in plan 21-01 resolved to option-a, adding `nb_search_gnb_socrata_datasets` and
`nb_query_gnb_socrata_dataset` to the tool manifest. All seven `<threat_model>` blocks were authored
*before* that decision, so no registered threat covered the new Socrata surface. The auditor found
that `nb_query_gnb_socrata_dataset` forwards caller-supplied `where`/`select` verbatim into SoQL
`$where`/`$select` with no escaping — structurally identical to the accepted T-21-12 GeoNB escape
hatch, but with no equivalent trust-boundary statement in its docstring.

Resolution: registered as T-21-20 (Tampering / medium / accept, AR-21-07), and a trust-boundary
paragraph was added to the tool's docstring so the boundary is stated where agents actually read it,
per CLAUDE.md's "API Limitations Go in Docstrings" rule. This is the only implementation change made
during the audit; 371 module + quality tests and `ruff` remain green.

**Generalisable lesson:** a threat register authored at plan time does not automatically cover
surface added by a mid-phase checkpoint decision. Any future phase whose checkpoint changes the tool
manifest should re-check its register against the shipped surface, not the planned one.

**T-21-03 and T-21-04 were reopened after this audit signed them off. Both are now genuinely closed.**

Codex's automated review of PR #6 found two P1 defects that this audit had passed. Both were
independently verified against the code and the live upstream before being accepted, and both are
real:

- **T-21-04 (F1).** This audit closed the threat citing
  `TestBuildFq.test_hostile_extra_fq_cannot_widen_result_past_nb_scope` as proof of "boolean
  semantics, not string shape". That test only ever fed a *balanced* fragment, and its truth-table
  evaluator assumes `extra_fq` is a well-formed Lucene atom — precisely the assumption the attack
  breaks. `extra_fq = "*:* ) OR (*:*"` (a live `@tool` parameter) composes to
  `(organization:nb) AND (*:* ) OR (*:*)`, whose trailing `OR` branch matches every non-NB dataset.
  The caller's own parenthesis broke *out* of the wrapper rather than being reinterpreted inside it.
  Fixed in `264449c`. Note the subtlety the fix had to handle: the attack string has *equal* counts
  of `(` and `)`, so a count comparison would have passed it — the validator tracks nesting depth
  left-to-right instead.

- **T-21-03 (F2).** This audit closed the threat partly on "`MAX_RECORDS=5000` + `truncated` flag
  bound all other paths". That was false. `MAX_RECORDS` appeared only as the *default value* of each
  tool's `limit` parameter, and `_geonb_query` forwarded `max_records=limit` directly, replacing
  `query_feature_service`'s own default rather than being bounded by it. Verified empirically:
  `fetch_crown_land(limit=10_000_000)` forwarded `max_records=10000000`, and `limit=0` forwarded `0`.
  A caller could paginate an entire layer — the exact DoS T-21-03 exists to prevent. Fixed in
  `3ecf46f`, centrally in `_geonb_query` so every curated tool inherits the bound. (The raw escape
  hatch `fetch_geonb_layer_features` had been clamping correctly all along; only the *curated* tools
  were unbounded.)

**The pattern to take away.** Both of these — and CR-01 before them — are the same failure: *a test
that appears to prove a guarantee while testing the wrong thing.* CR-01's guard was greppable but
tested truthiness; WR-01's test evaluated boolean semantics but assumed a well-formed atom; T-21-03's
bound was a default value mistaken for a clamp. This audit explicitly overrode the L1 grep
short-circuit because of CR-01, and then reproduced the same class of error one level up. The
durable lesson is not "grep is insufficient" but "state the adversary's move, then check the test
actually makes that move." An external reviewer with no stake in the prior conclusions caught what
three internal passes (code review, verification, this audit) did not.

Three further P2 usability/correctness defects from the same review were fixed alongside
(`193c091`, `6e81ebe`, `4964e77`) and are not threat-register items.

**T-21-08 evidence caveat (non-blocking).** The disposition text claims the cache-key prefix is
"asserted in unit tests". No test directly asserts the prefix on `cached_fetch`'s `key` argument —
the autouse test fixture bypasses caching and ignores `key`. The code mitigation is genuinely and
consistently present at all 24 sites, so the threat is closed on code evidence; only the claim about
test coverage is overstated. Worth a small test if the module is revisited.

**CR-01 history.** T-21-03 and T-21-01 were both genuinely OPEN between plan execution and the
post-execution code review — the mitigations were declared in the plans and partially present in code,
but ineffective. They were closed by commit `84192e3`, re-verified live by the orchestrator, and
independently re-verified by both `gsd-verifier` and `gsd-security-auditor`. This is recorded because
"mitigation declared in plan" and "mitigation effective in code" were demonstrably different states
for this phase.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-30 | 21 | 21 | 0 | gsd-security-auditor (ASVS L1, with L2/L3 tracing on T-21-01/02/03/04/16) |
| 2026-07-31 | 21 | 21 | 0 | Codex review of PR #6 reopened T-21-03 + T-21-04; both re-closed after fix and live re-verification |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-30
