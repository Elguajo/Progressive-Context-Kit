# Token-efficiency implementation and diagnostic pilot — 2026-10-03

Status: measurement infrastructure implemented; historical Codex pilot completed. Full
plan remains IN PROGRESS. Framework Source-only evidence; no current-version saving or accepted
performance optimization is claimed. Claude runs are deferred at the user's request.

## Implemented measurement infrastructure

Developed against PCK 3.1.0, the new measurement infrastructure reports separate persistent
instructions, Skill frontmatter, and conditional context sizes. `chars / 4` remains an approximate static measure. The generated
[baseline comparison](../../../BASELINE_COMPARISON.md) describes scope and exclusions.
The benchmark preparer accepts `--experiment PATH`, pins distinct immutable SHAs, preserves
configuration provenance, and retains the historical default. The existing run schema remains
unchanged. The analyzer separates agents/models/accounting methods and includes failed-run
tokens in tokens per successful task, returning null when there are no successful tasks.

Focused measurement tests: 38 passed. Canonical release-builder gate: 238 tests and 11/11
checks passed. Source audit: 0 errors/warnings. Packaged Runtime audit: 0 errors, 12 existing
project/global Skill collision warnings (project-local wins). The local unpublished Standalone
Runtime for both agents built successfully. Persistent instructions, compilers, Skills,
adapter policies, version, and project-owned seeds were not changed.

## Controls and accounting

Historical baseline: `b5d68e6ae258f02f7c5829e8f8bac54dd4d39a4a`.
Historical candidate: `8a8e21f16cb30d5cffe7c493a6c31dc17bfaa503`.
These results concern that historical change, not the current working tree.

Codex CLI 0.147.0, model `gpt-5.6-sol`, reasoning `high`, fresh ephemeral sessions,
`--ignore-user-config`, workspace-write sandbox, identical prompt plus acceptance, native
shell tools only. The configured desktop model `gpt-6.1-sol` was rejected by this CLI account;
the successful model was explicitly fixed before the recorded pairs. Existing host Skill
catalogs remained available in both arms; traces warn that their descriptions were shortened.
The native `turn.completed.usage` is preserved. Input includes cached input; output includes
reasoning output. Total uses reported input + output, without adding cache/reasoning again.
Costs, model-request count, and initial/peak context are unavailable; no estimates replace them.

Raw local task executions live in `dist/agent-benchmark/token-efficiency-pilot-2026-10-03/`.
[RUN_PLAN.json](RUN_PLAN.json) preserves fixture/task hashes and immutable workflow refs.
Anonymous A/B artifacts and normalized traces are retained under `pairs/`. Absolute workspace
paths are normalized to `<repo>`, `<pack>` and `<source-root>`; substantive content is preserved.
The control-only arm map is kept separate and is never supplied to a judge. Judging uses fresh
Codex sessions, the existing model-evaluation rubric and actual artifacts/commands/verification.
Judge runs and preflights are separate from task-consumption records.

A task invocation stopped on an account usage limit after one read command and before any
edit. Its provider usage was not reported. It is preserved separately as an incomplete attempt;
zero tokens would be fabricated. Complete-pair statistics cannot establish consumption across
all attempts when this attempt is included. A later fresh preflight succeeded and the unresolved
scenarios resumed with the same pinned settings and preserved original evidence.

## Codex pilot result

Six pairs / 12 completed client invocations, one pair per scenario. Each arm has five accepted
tasks and one failed task. A completed CLI invocation is not necessarily a successful task.
All six pairs received fresh blinded A/B judging; the judges invoked no tools and never saw
the arm map. The existing strict analyzer accepted the records/evidence and returned:

- Median paired total-token delta: **+1.77%** (candidate uses more).
- Quality gate: **FAIL**; median paired quality delta **-0.10 / 3.00** exceeds zero tolerance.
- No baseline-pass/candidate-fail hard regression; both environment-probe arms fail their
  exact mandatory discovery command. Quality scores also penalize unsupported exit-0 claims
  and avoidable work visible in the command traces.
- Recorded tokens per successful task: **307,494.8 baseline**, **290,069.6 candidate**. These
  include the failed environment tasks in the six complete pairs. They exclude the separately
  preserved usage-limit attempt with unknown consumption, so full all-attempt cost is unknown.

| Scenario | Baseline reported tokens | Candidate reported tokens | Paired delta | Acceptance baseline / candidate |
|---|---:|---:|---:|---|
| recon-batch | 241,467 | 248,518 | +2.92% | PASS / PASS |
| keyhole-read | 231,033 | 207,196 | -10.32% | PASS / PASS |
| environment-probe | 135,857 | 209,374 | +54.11% | FAIL / FAIL |
| validation-convergence | 177,807 | 287,475 | +61.68% | PASS / PASS |
| failure-pivot | 553,715 | 298,964 | -46.01% | PASS / PASS |
| polling-discipline | 197,595 | 198,821 | +0.62% | PASS / PASS |

The candidate's lower sum of recorded tokens is dominated by the failure-pivot outlier;
it does not meet the median paired acceptance criterion. No optimization receives KEEP.
Do not roll back or extrapolate current PCK behavior from this small historical comparison.
See [run records](codex-runs.jsonl), [blinded judge records](judge-records.jsonl),
[analyzer summary](codex-summary.json), [trace counters](MEASUREMENTS.json), and
[incomplete invocations](INCOMPLETE_ATTEMPTS.json).

`turns` counts completed outer client turns, not hidden model requests. `tool_calls` counts
observable completed command/file-change items. The required `file_reads` field records a
consistent observable proxy: shell inspection requests containing sed/cat/head/tail; item IDs
are retained. It is not a count of physical file opens and includes streamed inspection.
The JSON stream does not expose every internal wait/request; do not infer polling savings
from these counters. Costs and model-request counts remain unavailable.

The existing preparer exposes benchmark and arm labels in paths/seeds. Candidate runs were
not fully blinded; only A/B judging was blinded. This further limits behavioral attribution.
The canonical judge schema was rejected by the CLI structured-output subset (missing explicit
const type, then unsupported array const). Two rejected judge preflights are retained; the
successful judges emitted plain JSON that passed the canonical local validator. Their usage
is separate from task consumption. The exact successful review prompt is retained as
[JUDGE_PROMPT.template.txt](JUDGE_PROMPT.template.txt); substitute the existing schema/rubric
and each pair's review-input.json without adding the private map.

## Observations and limitations

Several historical fixtures omit `tests/__init__.py` (reconnaissance, keyhole reads,
environment probe, and failure pivot). In this Python 3.12.10 environment the exact
required `python3 -m unittest discover -v` can find zero tests and exit 5. Some runs repair the
fixture, others only run an alternative test command. The exact required command remains an
acceptance gate. This is a fixture/toolchain confound, not evidence for another framework rule.
Do not silently modify fixtures midway through this comparison. Any repaired-fixture rerun
must be a new dataset with its own fixture hash and fixed environment.

One pair per scenario is exploratory and cannot establish the 10% threshold. No RTK/Serena
routing change has been adopted. Missing Claude measurements prevent a two-agent KEEP decision.
No compaction occurred in these short tasks, so compaction continuity is not empirically tested.

## Tool installation and diagnostic check

The user approved both official user-local installations. Claude Code 2.1.285 is installed
but unauthenticated; the user deferred its runs. RTK 0.51.0 is installed, SHA-256 verified.
Hooks/proxy integration and telemetry are not enabled; shell profiles were not modified.
Use absolute installed paths when `~/.local/bin` is absent from PATH.
See [setup evidence](tooling/SETUP.json) and installer script hashes.

On a synthetic noisy failure, native output was 4,207 characters, RTK output 211 characters.
Both returned exit 7 and retained the assertion failure; `rtk recall --full` returned all 4,207
characters with no original lines missing. A missing command returned 127 with its diagnostic.
These are local output-mechanism checks, not provider-token or complete-task savings, and do
not establish coverage of other commands. Full originals and results are preserved in `tooling/`.

## Continuation checkpoint

The user approved harness repair directly on main. It is complete in opt-in controlled-v2,
with historical default fixtures/layout/metadata preserved. A separate six-pair Codex rerun
also completed; all twelve implementations passed required validation. Median paired tokens
-1.36%, quality gate FAIL. See [the new dataset and nearest remaining boundary](controlled-v2/README.md).
Do not pool these datasets or attribute their difference to current PCK. Claude remains deferred;
no instruction/adapter optimization is accepted. The measurement code remains RUNNABLE / GREEN.
